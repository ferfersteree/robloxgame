#!/usr/bin/env python3
"""V61: 25 кустов-укрытий, по одному на биом, каждый со своим силуэтом и своей манерой раскрытия.

    python tools/biome_covers.py preview [out.png]       # лист-превью 5x5 (картинка, без Studio)
    python tools/biome_covers.py json  <папка>           # spawn_cover_XX.luamod: исходники ModuleScript для V15Covers/ModelsData
    python tools/biome_covers.py stats                   # размеры, число кубиков, цвета частиц

Формат тот же, что читает V15Covers/Factory (кубики 0,5 студа, группы 0 Core / 1 LeftLobe / 2 RightLobe), плюс два новых поля:
  appearance.openStyle  curtain | swing | burst | sink | rise   (как створки раскрываются, см. V15Covers/Motion)
  particleColors        два цвета для брызг при раскрытии (раньше брались по индексу кубика)
Перед (сторона к игроку) это -Z. Центр и пол (y = 0) лежат в группе Core и остаются на месте, створки (левая x<0, правая x>0) раскрываются.
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter

UNIT = 0.5
HALF = 0.25
ORIGIN = [0.0, 0.25, 0.0]


def rgb(h: str) -> int:
    return int(h.lstrip("#"), 16)


class Vox:
    def __init__(self, seed: int):
        self.c: dict[tuple[int, int, int], tuple[int, bool]] = {}
        self.r = random.Random(seed)

    def col(self, c):
        if isinstance(c, (list, tuple)):
            return rgb(self.r.choice(c))
        return rgb(c)

    def put(self, x, y, z, c, ground=False):
        x, y, z = int(round(x)), int(round(y)), int(round(z))
        if y < 0:
            return
        self.c[(x, y, z)] = (self.col(c), ground)

    def erase(self, x, y, z):
        self.c.pop((int(round(x)), int(round(y)), int(round(z))), None)

    def box(self, x0, x1, y0, y1, z0, z1, c, ground=False):
        for x in range(int(x0), int(x1) + 1):
            for y in range(int(y0), int(y1) + 1):
                for z in range(int(z0), int(z1) + 1):
                    self.put(x, y, z, c, ground)

    def ell(self, cx, cy, cz, rx, ry, rz, c, keep_below=True):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            for y in range(int(cy - ry - 1), int(cy + ry + 2)):
                for z in range(int(cz - rz - 1), int(cz + rz + 2)):
                    if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1.0:
                        self.put(x, y, z, c)

    def cyl(self, cx, cz, y0, y1, r, c):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            for z in range(int(cz - r - 1), int(cz + r + 2)):
                if (x - cx) ** 2 + (z - cz) ** 2 <= r * r + 0.3:
                    for y in range(int(y0), int(y1) + 1):
                        self.put(x, y, z, c)

    def cone(self, cx, cz, y0, h, r0, c):
        for y in range(int(y0), int(y0 + h)):
            r = r0 * (1 - (y - y0) / h)
            self.cyl(cx, cz, y, y, max(r, 0.4), c)

    def line(self, a, b, r, c):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]), abs(b[2] - a[2]))) * 2 + 1
        for i in range(n + 1):
            t = i / n
            x, y, z = (a[k] + (b[k] - a[k]) * t for k in range(3))
            if r <= 0.6:
                self.put(x, y, z, c)
            else:
                self.ell(x, y, z, r, r, r, c)

    def scatter(self, n, xr, yr, zr, c, on=None):
        for _ in range(n):
            x, y, z = self.r.randint(*xr), self.r.randint(*yr), self.r.randint(*zr)
            if on is None or (x, y - 1, z) in self.c or y == 0:
                self.put(x, y, z, c)

    def trim(self, xmax=10, zmax=6, ymax=12):
        for k in list(self.c):
            if abs(k[0]) > xmax or abs(k[2]) > zmax or k[1] > ymax:
                del self.c[k]

    def prune_floaters(self):
        """убрать кубики, не связанные с землёй (кроме тех, что нарочно парят: float_ok)"""
        seen = set()
        stack = [k for k in self.c if k[1] == 0]
        seen.update(stack)
        while stack:
            x, y, z = stack.pop()
            for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                n = (x + d[0], y + d[1], z + d[2])
                if n in self.c and n not in seen:
                    seen.add(n)
                    stack.append(n)
        for k in list(self.c):
            if k not in seen:
                del self.c[k]


# ---------------------------------------------------------------- рисунки
def noisy(v: Vox, base, accents, n):
    """добавить цветные пятна к уже стоящим кубикам"""
    keys = list(v.c)
    for _ in range(n):
        k = v.r.choice(keys)
        v.c[k] = (v.col(accents), v.c[k][1])


def d01(v):  # Ягодная чаща: плотный куст с ягодами и ромашками
    G = ["#76a54d", "#477d32", "#294e2e", "#5f9a41"]
    for cx, cy, rx, ry in ((-5, 3, 5.0, 3.0), (5, 3, 5.0, 3.0), (0, 4, 4.5, 3.6), (-8, 2, 3, 2.3), (8, 2, 3, 2.3), (0, 2, 5, 2.6)):
        v.ell(cx, cy, 0, rx, ry, 3.4, G)
    v.scatter(34, (-9, 9), (1, 7), (-4, 0), ["#d63a45", "#c22f5a"], on=True)
    v.scatter(10, (-9, 9), (0, 2), (-5, -3), ["#ffffff", "#ffe27a"], on=True)
    v.box(-9, 9, 0, 0, -5, -4, ["#5f9a41", "#76a54d"], ground=True)


def d02(v):  # Хвойный заслон: ёлки, папоротник, паутина
    DK = ["#1c5944", "#154634", "#2a6a50"]
    for cx in (-6, 6):
        v.cyl(cx, 0, 0, 3, 0.8, "#4a3326")
        for i, r in enumerate((5.2, 4.3, 3.4, 2.4, 1.4)):
            v.cyl(cx, 0, 2 + i * 2, 3 + i * 2, r, DK + ["#387b52"])
        v.put(cx, 12, 0, "#9ac28a")
    v.ell(0, 2, 0, 3, 2.4, 3, DK)
    for x in range(-9, 10, 3):
        v.line((x, 0, -4), (x + v.r.choice((-2, 2)), 4, -3), 0.5, "#769f62")
    for x in range(-7, 8, 2):
        v.put(x, 4 + (x % 3), -3, "#e8eef0")  # паутина
    v.scatter(7, (-9, 9), (0, 1), (-5, -3), ["#d9463a", "#e6e0c8"], on=True)
    v.box(-8, 8, 0, 0, -5, -4, ["#2a6a50", "#154634"], ground=True)


def d03(v):  # Мшистый бурелом: поваленные брёвна, светящиеся грибы
    B = ["#503c2e", "#42301f", "#5d4637"]
    M = ["#77904b", "#5d7a37", "#465b32"]
    v.line((-10, 2, -2), (9, 4, 1), 1.9, B)
    v.line((-9, 5, 2), (8, 1, -2), 1.7, B)
    v.line((-4, 0, -3), (-2, 7, 1), 1.2, B)
    v.line((5, 0, 1), (7, 7, -1), 1.2, B)
    for k in list(v.c):
        if v.r.random() < 0.45 and (k[0], k[1] + 1, k[2]) not in v.c:
            v.c[k] = (rgb(v.r.choice(M)), False)
    for x, y, z in ((-6, 3, -3), (-1, 5, -2), (4, 4, -3), (7, 3, -2), (1, 2, -4)):
        v.cyl(x, z, y, y + 1, 0.6, "#e6dcb8")
        v.ell(x, y + 2, z, 1.8, 1.0, 1.8, ["#b456ff", "#d28aff"])
    for x in range(-9, 10, 3):
        v.line((x, 0, 3), (x + 1, 6 + (x % 4), 3), 0.5, "#6f8a44")  # камыш
        v.put(x + 1, 7 + (x % 4), 3, "#4a3326")
    v.box(-9, 9, 0, 0, -5, -4, ["#465b32", "#503c2e"], ground=True)


def d04(v):  # Снежные ветви: сугроб с заиндевелыми ветками и сосульками
    S = ["#f2f8fa", "#dfeff3", "#c7e0e8"]
    v.ell(-5, 2, 0, 6, 3.4, 3.8, S)
    v.ell(5, 2, 0, 6, 3.4, 3.8, S)
    v.ell(0, 3, 1, 5, 4, 3, S)
    for cx in (-6, 0, 6):
        v.cyl(cx, 1, 0, 8, 0.7, "#4c7160")
        for i in range(3):
            y = 3 + i * 2
            v.line((cx, y, 1), (cx - 3, y - 1, 1), 0.5, "#326544")
            v.line((cx, y, 1), (cx + 3, y - 1, 1), 0.5, "#326544")
            v.put(cx - 3, y, 1, "#ffffff")
            v.put(cx + 3, y, 1, "#ffffff")
    for x in range(-9, 10, 2):
        h = v.r.choice((1, 2, 3))
        for y in range(h):
            v.put(x, 6 - y, -3, "#adc9d0" if y else "#e8f6fa")
    v.box(-9, 9, 0, 0, -5, -4, ["#f2f8fa", "#c7e0e8"], ground=True)


def d05(v):  # Высокие травы: золотая трава и тёплые камни
    G = ["#bc923e", "#dec373", "#8d8148", "#d6b24f"]
    for _ in range(170):
        x = v.r.randint(-10, 10)
        z = v.r.randint(-4, 3)
        h = v.r.randint(4, 11)
        lean = v.r.choice((-1, 0, 0, 1))
        for y in range(h):
            v.put(x + (lean if y > h // 2 else 0), y, z, v.r.choice(G))
        if v.r.random() < 0.25:
            v.put(x + lean, h, z, "#f2dc8a")
    for cx, r in ((-7, 1.6), (6, 2.0), (1, 1.2)):
        v.ell(cx, 1, -3, r + 0.5, r, r, ["#a08a66", "#8d7a5c"])
    v.box(-10, 10, 0, 0, -5, -4, ["#8d8148", "#bc923e"], ground=True)


def d06(v):  # Каньонные кактусы: сагуаро и красные валуны
    C = ["#4e8a43", "#3f7a3a", "#5a9a4c"]
    for cx, h, arm in ((-6, 9, 1), (0, 7, -1), (6, 10, 1)):
        v.cyl(cx, 0, 0, h, 1.3, C)
        for sgn in (-1, 1):
            if (arm if sgn == 1 else -arm) > 0 or v.r.random() < 0.5:
                ah = h // 2 + 1
                v.cyl(cx + sgn * 3, 0, ah, ah + 3, 0.9, C)
                v.line((cx + sgn * 1, ah, 0), (cx + sgn * 3, ah, 0), 0.9, C)
        v.put(cx, h + 1, 0, "#e86aa0")
    for cx, cz, r in ((-9, -2, 2.4), (9, -2, 2.6), (-2, -3, 1.8), (3, -3, 2.1)):
        v.ell(cx, r * 0.6, cz, r, r * 0.7, r, ["#ba7749", "#a5643a", "#e3ab6d"])
    v.box(-10, 10, 0, 0, -5, -4, ["#ba7749", "#9b784a"], ground=True)


def d07(v):  # Корни дюн: песчаный бархан, сухие корни, полузасыпанная колонна
    S = ["#e3c27a", "#d6b266", "#c4a057"]
    v.ell(-5, 2, 0, 6.5, 3.2, 4, S)
    v.ell(5, 2, 0, 6.5, 3.2, 4, S)
    v.ell(0, 1, 2, 5, 2.4, 3, S)
    v.cyl(-3, -1, 0, 6, 1.5, ["#9b784a", "#7b6245"])  # колонна
    v.box(-5, -1, 7, 7, -3, 1, ["#8a6c45"])
    for sx in (-1, 1):
        a = (sx * 8, 3, -1)
        v.line(a, (sx * 6, 6, 0), 0.9, "#7b6245")
        v.line((sx * 6, 6, 0), (sx * 3, 9, -1), 0.7, "#6b523a")
        v.line((sx * 6, 6, 0), (sx * 8, 9, 1), 0.6, "#6b523a")
        v.line((sx * 2, 3, -2), (sx * 5, 6, -2), 0.6, "#96704b")
    v.scatter(12, (-9, 9), (1, 4), (-4, -2), ["#f2d98f"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, S, ground=True)


def d08(v):  # Лиановая завеса: широкие листья и лианы
    L = ["#3f8242", "#65a451", "#2a7848", "#4a9a4d"]
    for sx in (-1, 1):
        for i, (cx, cy, rx, ry) in enumerate(((3, 3, 4.5, 0.8), (6, 5, 4.0, 0.7), (8, 2, 3.4, 0.7), (4, 7, 3.6, 0.6))):
            v.ell(sx * cx, cy, 0, rx, ry, 3.2, L)
            v.line((sx * cx, cy, 0), (sx * (cx - 2), 0, 0), 0.5, "#2a5a32")
        v.cyl(sx * 1, 1, 0, 8, 0.8, "#4a3f2a")
    for x in range(-9, 10, 2):
        h = v.r.randint(3, 8)
        for y in range(h):
            v.put(x, 9 - y, -3, v.r.choice(("#4e8f3a", "#2f6e32")))
    for x, y, z in ((-7, 3, -3), (-2, 6, -3), (4, 4, -3), (8, 7, -3), (0, 2, -4)):
        v.ell(x, y, z, 1.2, 1.2, 0.8, ["#ff5d8f", "#ffb347"])
    v.box(-9, 9, 0, 0, -5, -4, ["#2a7848", "#3f8242"], ground=True)


def d09(v):  # Мангровый сплетень: ходульные корни и вода между ними
    R = ["#99704a", "#77613d", "#6b5236"]
    for cx in (-7, -2, 3, 8):
        top = v.r.randint(6, 9)
        for dx in (-2, 0, 2):
            v.line((cx + dx, 0, v.r.randint(-1, 1)), (cx, top, 0), 0.7, R)
        v.ell(cx, top + 1, 0, 3.3, 1.8, 2.6, ["#88a574", "#6e9462", "#5d8a52"])
    v.box(-10, 10, 0, 0, -5, -4, ["#3d8c8a", "#2f7a7e"], ground=True)
    v.box(-9, 9, 1, 1, -4, -3, ["#3d8c8a", "#4aa5a0"])
    for x, z in ((-5, -4), (1, -5), (6, -4)):
        v.ell(x, 1, z, 1.6, 0.5, 1.4, "#5fae52")
        v.put(x, 2, z, "#ff9ec4")
    v.scatter(9, (-9, 9), (1, 3), (-3, 2), ["#ffffff"], on=True)


def d10(v):  # Грозовые валуны: острые скалы, обожжённый пень, голубой камень
    G = ["#626e65", "#51715a", "#3c564c", "#74827a"]
    for cx, h, r in ((-7, 8, 2.8), (-2, 10, 2.4), (4, 7, 3.0), (8, 9, 2.2)):
        for y in range(h):
            v.cyl(cx + (y // 4) * (1 if cx < 0 else -1) * 0, 0, y, y, max(r * (1 - y / (h + 2)), 0.6), G)
    v.cyl(0, -2, 0, 5, 1.4, ["#2a2a2e", "#3a3a40"])  # пень
    v.line((0, 5, -2), (-2, 8, -2), 0.7, "#2a2a2e")
    v.line((0, 5, -2), (2, 7, -2), 0.6, "#2a2a2e")
    for x, y, z in ((-4, 2, -4), (3, 1, -4), (6, 3, -3)):
        v.ell(x, y, z, 1.4, 1.8, 1.2, ["#7ad0ff", "#a8e4ff", "#5ab4f0"])
    v.scatter(8, (-9, 9), (1, 6), (-4, -2), ["#fff6a0"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, ["#51715a", "#626e65"], ground=True)


def d11(v):  # Береговой риф: ракушки, кораллики, плавник
    S = ["#f0dcb4", "#e6cfa0"]
    v.ell(-5, 1.4, 0, 6, 2.2, 3.6, S)
    v.ell(5, 1.4, 0, 6, 2.2, 3.6, S)
    for cx, h, c in ((-7, 5, "#a76a8e"), (-3, 4, "#d79a80"), (3, 6, "#a76a8e"), (7, 4, "#65ac9b")):
        v.cyl(cx, -1, 1, h, 0.9, c)
        v.ell(cx, h + 1, -1, 1.6, 1.4, 1.6, c)
        v.line((cx, h - 1, -1), (cx + 2, h + 1, -1), 0.6, c)
    v.line((-9, 1, 2), (-1, 4, 2), 1.0, ["#a99a82", "#8c7e69"])  # плавник
    for x, z in ((-4, -4), (1, -4), (6, -3), (-8, -3)):
        v.ell(x, 1, z, 1.3, 0.9, 1.0, ["#fff1d6", "#ffc3b0"])
    v.scatter(14, (-9, 9), (1, 3), (-4, 3), ["#ffffff", "#f4b6c2"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, ["#e6cfa0", "#f0dcb4"], ground=True)


def d12(v):  # Густой коралловый риф: ветвистые и мозговые кораллы
    P = ["#a76a8e", "#6abbb7", "#f2d7b3", "#ff7aa8", "#ffb259"]
    for cx, h, c in ((-8, 8, "#ff7aa8"), (-4, 10, "#6abbb7"), (0, 7, "#ffb259"), (4, 9, "#a76a8e"), (8, 8, "#6abbb7")):
        v.cyl(cx, 0, 0, 3, 1.1, c)
        for sx in (-1, 0, 1):
            v.line((cx, 3, 0), (cx + sx * 2, h, v.r.randint(-1, 1)), 0.6, c)
            v.line((cx + sx * 2, h - 3, 0), (cx + sx * 3, h, 0), 0.5, c)
    v.ell(-6, 2, -3, 2.6, 2.2, 1.8, ["#e8a0c4", "#c47aa0"])
    v.ell(6, 2, -3, 2.4, 2.0, 1.8, ["#8ad2c6", "#6abbb7"])
    for x in (-2, 2):
        v.ell(x, 1, -3, 1.3, 1.0, 1.0, "#f2d7b3")
        for t in range(-1, 2):
            v.line((x + t, 2, -3), (x + t * 2, 4, -3), 0.4, ["#ffe0f0", "#ffffff"])
    v.box(-10, 10, 0, 0, -5, -4, ["#c9b78e", "#e6d9b8"], ground=True)


def d13(v):  # Пепельные корни: обугленные корни, горки пепла, угольки
    K = ["#423c46", "#2e2a33", "#554c5a"]
    A = ["#b49a7d", "#9b8870", "#7d6e5c"]
    v.ell(-6, 1.5, 0, 5, 2.0, 3.4, A)
    v.ell(6, 1.5, 0, 5, 2.0, 3.4, A)
    for sx in (-1, 1):
        v.line((sx * 9, 0, 0), (sx * 7, 5, 0), 1.0, K)
        v.line((sx * 7, 5, 0), (sx * 3, 8, 0), 0.9, K)
        v.line((sx * 3, 8, 0), (sx * 0.5, 6, 0), 0.7, K)
        v.line((sx * 7, 5, 0), (sx * 9, 8, -1), 0.7, K)
        v.line((sx * 5, 2, -2), (sx * 2, 5, -2), 0.8, K)
    for k in list(v.c):
        if v.c[k][0] in (rgb("#423c46"), rgb("#2e2a33")) and v.r.random() < 0.10:
            v.c[k] = (rgb(v.r.choice(["#ff7a2a", "#ffb347"])), False)
    v.scatter(20, (-9, 9), (1, 4), (-5, -2), ["#ff6a1f", "#ffa13a"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, ["#423c46", "#675349"], ground=True)


def d14(v):  # Базальтовая заслонка: шестигранные колонны и лавовая щель
    D = ["#423c46", "#4b3e48", "#625b61"]
    xs = [-9, -7, -5, -3, 3, 5, 7, 9, -1, 1]
    for i, cx in enumerate(xs):
        h = 4 + (i * 5 + 3) % 6
        v.cyl(cx, (i % 3) - 1, 0, h, 1.0, D)
        v.put(cx, h + 1, (i % 3) - 1, "#7a7078")
    v.box(-1, 1, 0, 1, -3, 3, ["#ff6f35", "#ffb347"])  # лавовая щель в центре
    for x in (-8, -4, 4, 8):
        v.put(x, 1, -4, "#ff8a3a")
        v.put(x, 2, -4, "#ffc36a")
    v.box(-10, 10, 0, 0, -5, -4, ["#423c46", "#2e2a33"], ground=True)


def d15(v):  # Аметистовая друза: кристаллы на сером камне
    P = ["#9d74be", "#6c528d", "#b48ada", "#c9a6ee"]
    v.ell(-5, 1.5, 0, 6, 2.0, 3.4, ["#5a5560", "#6a6470"])
    v.ell(5, 1.5, 0, 6, 2.0, 3.4, ["#5a5560", "#6a6470"])
    for cx, cz, h, r in ((-7, 0, 9, 1.5), (-4, -2, 6, 1.3), (-2, 1, 11, 1.6), (2, 0, 10, 1.5), (5, -2, 7, 1.4), (8, 1, 8, 1.5), (0, -3, 4, 1.1)):
        v.cone(cx, cz, 2, h - 2, r + 0.6, P)
        v.cyl(cx, cz, 1, 3, r + 0.6, P)
    v.scatter(12, (-9, 9), (2, 8), (-3, 3), ["#e4d0ff"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, ["#5a5560", "#8d6fb0"], ground=True)


def d16(v):  # Сросшийся ледник: ледяные глыбы и сосульки
    I = ["#c1e0e7", "#8dbccf", "#77a9c6", "#e4f6fa"]
    for cx, cy, rx, ry in ((-6, 3, 4.2, 3.4), (6, 3, 4.2, 3.4), (0, 4, 3.4, 4.2), (-9, 2, 2, 2), (9, 2, 2, 2)):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            for y in range(0, int(cy + ry) + 1):
                for z in range(-4, 5):
                    if abs(x - cx) / rx + abs(y - cy) / ry * 0.9 + abs(z) / 4.6 <= 1.05:
                        v.put(x, y, z, I)
    for x in range(-9, 10, 2):
        for y in range(v.r.choice((1, 2, 3, 4))):
            v.put(x, 5 - y, -4, "#e4f6fa" if y == 0 else "#aad6e6")
    v.scatter(10, (-9, 9), (1, 7), (-4, 4), ["#ffffff"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, ["#c1e0e7", "#e4f6fa"], ground=True)


def d17(v):  # Облачная крона: пухлые облака
    C = ["#e5e4d3", "#f1eddf", "#b5cfbd", "#ffffff"]
    for cx, cy, rx, ry, rz in ((-6, 2, 4, 2.2, 3), (-3, 4, 3.4, 2.4, 3), (0, 3, 3.6, 2.6, 3.2), (3, 4, 3.4, 2.4, 3), (6, 2, 4, 2.2, 3), (-8, 1, 2.4, 1.6, 2.4), (8, 1, 2.4, 1.6, 2.4)):
        v.ell(cx, cy, 0, rx, ry, rz, C)
    v.ell(0, 7, 0, 2.6, 1.6, 2.4, C)
    v.scatter(8, (-9, 9), (2, 8), (-4, -2), ["#ffd8ec", "#d8ecff"], on=True)
    v.box(-9, 9, 0, 0, -5, -4, ["#e5e4d3", "#f1eddf"], ground=True)


def d18(v):  # Теневые колючки: ежевичные заросли шипов и светящиеся споры
    T = ["#443b5c", "#2c2640", "#755a83", "#384956"]
    for cx in (-8, -5, -2, 2, 5, 8):
        h = v.r.randint(6, 10)
        v.line((cx, 0, 0), (cx + v.r.choice((-2, -1, 1, 2)), h, v.r.randint(-1, 1)), 1.0, T)
        v.line((cx, 3, 0), (cx + v.r.choice((-3, 3)), 6, v.r.randint(-2, 2)), 0.6, T)
    v.ell(-6, 2, 0, 4, 2.4, 3.0, T)
    v.ell(6, 2, 0, 4, 2.4, 3.0, T)
    keys = [k for k in v.c if k[1] >= 3]
    for k in v.r.sample(keys, min(55, len(keys))):
        v.put(k[0], k[1] + 1, k[2] - 1, "#c8b0ff")  # шипы
    v.scatter(18, (-9, 9), (2, 9), (-4, 3), ["#5effd0", "#a2ffea"], on=None)
    v.box(-10, 10, 0, 0, -5, -4, ["#2c2640", "#443b5c"], ground=True)


def d19(v):  # Звёздный заслон: осколки портала и звёздная пыль
    P = ["#9ca4d5", "#69699e", "#d4c5a1", "#b6bff2"]
    for sx in (-1, 1):
        v.cyl(sx * 8, 0, 0, 5, 1.7, ["#69699e", "#53537f"])
        for y in range(5, 11):
            ang = (y - 5) / 5.0
            v.ell(sx * (8 - ang * 5.5), y + 1, 0, 1.4, 1.3, 1.4, P)
    for cx, cy in ((-3, 3), (3, 3), (0, 5)):
        v.ell(cx, cy, -1, 2.2, 2.4, 1.6, ["#6e5ac8", "#8a76ff", "#a89cff"])
    v.scatter(30, (-9, 9), (1, 11), (-4, 3), ["#fff8d6", "#d4c5ff"], on=None)
    v.box(-10, 10, 0, 0, -5, -4, ["#69699e", "#4a4a7a"], ground=True)


def d20(v):  # Латунный живоплот: шестерёнки, трубы, пар
    B = ["#c2a65a", "#90703c", "#5c6b58", "#b08d45"]
    for cx, cy, r in ((-6, 4, 3.6), (-1, 6, 2.6), (5, 4, 3.8), (9, 7, 2.2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            for y in range(int(cy - r - 1), int(cy + r + 2)):
                d = math.hypot(x - cx, y - cy)
                a = math.atan2(y - cy, x - cx)
                tooth = r + (0.9 if int(a / (math.pi / 6) + 100) % 2 == 0 else 0)
                if d <= tooth and d >= r * 0.35 and y >= 0:
                    for z in (-1, 0):
                        v.put(x, y, z, B)
        v.put(cx, cy, -1, "#3a3a36")
    for x in (-9, -3, 2, 8):
        v.cyl(x, 1, 0, 6, 0.8, ["#90703c", "#7a5c30"])
    v.scatter(14, (-9, 9), (6, 11), (-3, 2), ["#e8e8e8", "#cfcfcf"], on=None)
    v.box(-10, 10, 0, 0, -5, -4, ["#5c6b58", "#90703c"], ground=True)


def d21(v):  # Споровая завеса: гигантские грибные шляпки
    for cx, h, r, c in ((-7, 6, 3.6, ["#7f5e9c", "#9a76bb"]), (-1, 8, 4.0, ["#c484b5", "#d9a0cc"]), (6, 7, 3.8, ["#91bfa2", "#a8d3b8"]), (9, 4, 2.2, ["#c484b5"])):
        v.cyl(cx, 0, 0, h, 1.0, "#efe6d0")
        v.ell(cx, h + 1, 0, r, 1.9, r * 0.85, c)
        for k in range(8):
            v.put(cx + v.r.randint(-int(r) + 1, int(r) - 1), h + 2, v.r.randint(-2, 2), "#ffffff")
    v.scatter(26, (-9, 9), (1, 10), (-4, 3), ["#b8ffe0", "#e6ffd8"], on=None)
    v.scatter(8, (-9, 9), (0, 1), (-5, -3), ["#c484b5", "#91bfa2"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, ["#5a6b4a", "#7f5e9c"], ground=True)


def d22(v):  # Костяной завал: груда костей, рёбра-арки, череп
    Bn = ["#d3c5a4", "#a69b7d", "#e8dcc0", "#7d6d58"]
    v.ell(-5, 2, 0, 5.5, 2.6, 3.4, Bn)
    v.ell(5, 2, 0, 5.5, 2.6, 3.4, Bn)
    v.ell(0, 2, 1, 4, 3.0, 2.6, Bn)
    for cx, h in ((-7, 9), (-3, 11), (2, 11), (6, 9)):
        for t in range(0, 21):
            a = t / 20 * math.pi
            x = cx + (1 if cx < 0 else -1) * (1 - math.cos(a)) * 2.2
            y = math.sin(a) * h * 0.55 + 2
            for z in (-1, 0, 1):
                v.put(x, y, z, Bn)
    for x in range(-9, 10, 3):
        v.line((x, 5 + (x % 3), -2), (x + 3, 7 + (x % 2), -2), 0.5, "#e8dcc0")
    v.ell(-1, 2, -3, 2.6, 2.0, 1.8, "#e8dcc0")  # череп
    v.put(-2, 3, -5, "#2a2622")
    v.put(0, 3, -5, "#2a2622")
    v.box(-2, 0, 1, 1, -5, -4, "#7d6d58")
    v.line((-9, 4, 3), (8, 6, 3), 0.9, Bn)
    v.box(-10, 10, 0, 0, -5, -4, ["#a69b7d", "#7d6d58"], ground=True)


def d23(v):  # Кораллы затонувшей стены: перламутровая кладка с кораллами и воротами
    W = ["#b69bb8", "#c9b4cb", "#a085a8", "#d8c8dc"]
    for sx in (-1, 1):
        for row in range(0, 10, 2):
            off = (row // 2) % 2
            for bx in range(2, 10, 3):
                x0 = sx * (bx + off)
                v.box(min(x0, x0 + sx * 2), max(x0, x0 + sx * 2), row, row + 1, -1, 1, W)
        for x, y, c in ((sx * 6, 9, "#5a8b94"), (sx * 8, 7, "#86b8ac"), (sx * 4, 8, "#ff8aa8")):
            v.line((x, y, -1), (x + sx, y + 3, -1), 0.6, c)
            v.ell(x + sx, y + 3, -1, 1.1, 0.9, 0.9, c)
    v.box(-1, 1, 7, 9, -1, 1, W)  # замковый камень
    for x in range(-9, 10, 3):
        v.put(x, 1, -3, "#e9fbff")  # пузыри
        v.put(x, 3 + (x % 3), -3, "#cfeff6")
    v.box(-10, 10, 0, 0, -5, -4, ["#5a8b94", "#86b8ac"], ground=True)


def d24(v):  # Штормовые осколки: парящие осколки, фульгурит и молнии
    S = ["#6d6b9c", "#8c9fc3", "#c8d7e7", "#4f4d78"]
    for cx, h, r in ((-8, 7, 2.2), (-3, 10, 2.6), (3, 9, 2.4), (8, 7, 2.0)):
        v.cone(cx, 0, 0, h, r + 0.8, S)
    for x, y, z in ((-6, 6, -3), (0, 9, -3), (6, 7, -3)):
        v.line((x, y, z), (x + 1, y - 2, z), 0.5, "#fff6a8")
        v.line((x + 1, y - 2, z), (x - 1, y - 4, z), 0.5, "#fff6a8")
        v.line((x - 1, y - 4, z), (x, y - 6, z), 0.5, "#ffe45a")
    v.cyl(0, -2, 0, 4, 1.2, ["#c8d7e7", "#e8eef5"])
    v.scatter(14, (-9, 9), (1, 9), (-4, 3), ["#bfe2ff", "#fff6a8"], on=None)
    v.box(-10, 10, 0, 0, -5, -4, ["#4f4d78", "#6d6b9c"], ground=True)


def d25(v):  # Обсидиановые наросты: чёрные шипы с лавовыми жилами
    O = ["#483e46", "#2e2830", "#5a4f58"]
    for cx, h, r in ((-9, 6, 1.8), (-6, 10, 2.4), (-2, 7, 2.2), (2, 9, 2.4), (6, 11, 2.6), (9, 6, 1.8)):
        v.cone(cx, 0, 0, h, r + 0.8, O)
    v.ell(0, 1, -2, 4, 1.6, 1.6, O)
    for k in list(v.c):
        if v.r.random() < 0.10 and k[1] > 0:
            v.c[k] = (rgb(v.r.choice(["#c48443", "#ff7a3d", "#84554e"])), False)
    v.scatter(14, (-9, 9), (1, 5), (-5, -2), ["#ff7a3d", "#ffb347"], on=True)
    v.box(-10, 10, 0, 0, -5, -4, ["#84554e", "#483e46"], ground=True)


# id: (name, description, drawing, openStyle, hinge x in studs)
COVERS = {
    1: ("Ягодная чаща", "Густой куст с ягодами и ромашками: ветви расходятся в стороны.", d01, "curtain", 2.5),
    2: ("Хвойный заслон", "Две молодые ели, папоротник и паутина: хвоя раздвигается.", d02, "curtain", 2.5),
    3: ("Мшистый бурелом", "Поваленные мшистые брёвна и светящиеся грибы: брёвна распахиваются, как створки.", d03, "swing", 4.5),
    4: ("Снежные ветви", "Сугроб с заиндевелыми ветками: снег оседает и проваливается.", d04, "sink", 2.5),
    5: ("Высокие травы", "Стена золотой травы и тёплые камни: трава ложится в стороны.", d05, "curtain", 2.5),
    6: ("Каньонные кактусы", "Три кактуса сагуаро и красные валуны: заросль раздвигается.", d06, "curtain", 2.5),
    7: ("Корни дюн", "Бархан с сухими корнями и полузасыпанной колонной: песок осыпается.", d07, "sink", 2.5),
    8: ("Лиановая завеса", "Широкие листья и лианы: листья распахиваются, как двери.", d08, "swing", 4.5),
    9: ("Мангровый сплетень", "Ходульные корни над водой с кувшинками: заросль раздвигается.", d09, "curtain", 2.5),
    10: ("Грозовые валуны", "Острые скалы, обожжённый пень и голубой камень: скалы разлетаются.", d10, "burst", 2.5),
    11: ("Береговой риф", "Ракушки, кораллики и плавник на песке: заросль раздвигается.", d11, "curtain", 2.5),
    12: ("Густой коралловый риф", "Ветвистые и мозговые кораллы: кораллы колышутся и расходятся.", d12, "curtain", 2.5),
    13: ("Пепельные корни", "Обугленные корни и тлеющий пепел: корни разлетаются искрами.", d13, "burst", 2.5),
    14: ("Базальтовая заслонка", "Шестигранные колонны над лавовой щелью: колонны уходят в землю.", d14, "sink", 2.5),
    15: ("Аметистовая друза", "Кристаллы на сером камне: друза раскалывается.", d15, "burst", 2.5),
    16: ("Сросшийся ледник", "Ледяные глыбы с сосульками: лёд раскалывается.", d16, "burst", 2.5),
    17: ("Облачная крона", "Пухлые облака: облака всплывают и расходятся.", d17, "rise", 2.5),
    18: ("Теневые колючки", "Шипастые заросли со светящимися спорами: колючки раздвигаются.", d18, "curtain", 2.5),
    19: ("Звёздный заслон", "Осколки портала и звёздная пыль: осколки всплывают.", d19, "rise", 2.5),
    20: ("Латунный живоплот", "Шестерёнки и трубы с паром: шестерни распахиваются, как ворота.", d20, "swing", 4.5),
    21: ("Споровая завеса", "Гигантские грибные шляпки: шляпки откидываются, выпуская споры.", d21, "swing", 4.5),
    22: ("Костяной завал", "Рёбра-арки, череп и позвонки: кости разваливаются.", d22, "burst", 2.5),
    23: ("Кораллы затонувшей стены", "Перламутровая кладка с кораллами: ворота цитадели открываются.", d23, "swing", 4.5),
    24: ("Штормовые осколки", "Парящие осколки с молниями: осколки разлетаются.", d24, "burst", 2.5),
    25: ("Обсидиановые наросты", "Чёрные шипы с лавовыми жилами: наросты раскалываются.", d25, "burst", 2.5),
}


def build(zone: int) -> dict:
    name, desc, draw, style, hinge = COVERS[zone]
    v = Vox(zone * 7919)
    draw(v)
    v.trim()
    v.prune_floaters() if zone not in (17, 19, 21, 24) else None
    cells = []
    for (x, y, z), (c, ground) in sorted(v.c.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])):
        if ground:
            g = 0
        elif x < 0:
            g = 1
        elif x > 0:
            g = 2
        else:
            g = 1 if (y + z) % 2 else 2
        cells.append([x, y, z, c, g])
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    zs = [c[2] for c in cells]
    mn = [min(xs) * UNIT + ORIGIN[0] - HALF, min(ys) * UNIT + ORIGIN[1] - HALF, min(zs) * UNIT + ORIGIN[2] - HALF]
    mx = [max(xs) * UNIT + ORIGIN[0] + HALF, max(ys) * UNIT + ORIGIN[1] + HALF, max(zs) * UNIT + ORIGIN[2] + HALF]
    size = [mx[i] - mn[i] for i in range(3)]
    # цвета частиц: два самых частых не-«земляных» цвета на высоте
    cnt = Counter(c[3] for c in cells if c[1] >= 2 and c[4] != 0)
    top = [c for c, _ in cnt.most_common(2)] or [cells[0][3]]
    if len(top) == 1:
        top.append(top[0])
    surface = 0
    occ = {(c[0], c[1], c[2]): c[4] for c in cells}
    for (x, y, z), g in occ.items():
        if any(occ.get((x + dx, y + dy, z + dz)) != g for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
            surface += 1
    return {
        "id": "spawn_cover_%02d" % zone,
        "name": name,
        "category": "spawn_cover",
        "biomes": [zone],
        "description": desc,
        "voxelSize": UNIT,
        "origin": ORIGIN,
        "bounds": {"min": mn, "max": mx, "size": size},
        "groups": [
            {"id": 0, "name": "Core", "pivot": [0, 0, 0]},
            {"id": 1, "name": "LeftLobe", "pivot": [-hinge, 0.25, 0]},
            {"id": 2, "name": "RightLobe", "pivot": [hinge, 0.25, 0]},
        ],
        "voxelCount": len(cells),
        "surfaceVoxelCount": surface,
        "colors": sorted({c[3] for c in cells}),
        "source": "authored_v61_biome_cover",
        "material": "Plastic",
        "studFaces": "all6",
        "allowScale": False,
        "biomeId": zone,
        "attachments": {
            "HatchOrigin": [0, 0, size[2] / 2],
            "ExitOrigin": [0, 0, -size[2] / 2 - 4],
            "EffectOrigin": [0.0, min(size[1] * 0.5, 3.0), 0.0],
            "LeftHinge": [-hinge, 0.25, 0],
            "RightHinge": [hinge, 0.25, 0],
        },
        "appearance": {"openStyle": style, "motion": "rigid lobes; no voxel scaling"},
        "particleColors": top,
        "legacyTypes": [],
        "cubeSize": [UNIT, UNIT, UNIT],
        "transparency": 0,
        "version": 61,
        "centreFilled": True,
        "voxels": cells,
    }


def luamod(spec: dict) -> str:
    return "return [====[" + json.dumps(spec, ensure_ascii=False, separators=(",", ":")) + "]====]"


# ---------------------------------------------------------------- превью
def preview(path: str):
    from PIL import Image, ImageDraw

    S = 9
    cw, ch = 360, 250
    sheet = Image.new("RGB", (cw * 5, ch * 5), (46, 50, 58))
    dr = ImageDraw.Draw(sheet)

    def shade(c, k):
        r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
        return (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)))

    for zone in range(1, 26):
        spec = build(zone)
        ox = ((zone - 1) % 5) * cw + cw // 2
        oy = ((zone - 1) // 5) * ch + ch - 40
        order = sorted(spec["voxels"], key=lambda c: (-c[2], c[1], abs(c[0]) * -1))
        # красим: левая створка чуть светлее, правая темнее; ядро нейтрально
        for x, y, z, col, g in order:
            sx = ox + x * S + z * S * 0.45
            sy = oy - y * S - z * S * 0.45
            k = 1.0
            front = [(sx, sy), (sx + S, sy), (sx + S, sy - S), (sx, sy - S)]
            top = [(sx, sy - S), (sx + S, sy - S), (sx + S + S * 0.45, sy - S - S * 0.45), (sx + S * 0.45, sy - S - S * 0.45)]
            side = [(sx + S, sy), (sx + S + S * 0.45, sy - S * 0.45), (sx + S + S * 0.45, sy - S - S * 0.45), (sx + S, sy - S)]
            dr.polygon(front, fill=shade(col, 0.9 * k))
            dr.polygon(top, fill=shade(col, 1.12))
            dr.polygon(side, fill=shade(col, 0.68))
        dr.text((zone and ((zone - 1) % 5) * cw + 8, ((zone - 1) // 5) * ch + 6), "%02d %s [%s] %d vox %s" % (zone, "", spec["appearance"]["openStyle"], spec["voxelCount"], [round(s, 1) for s in spec["bounds"]["size"]]), fill=(255, 255, 255))
    sheet.save(path)
    print("saved", path)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "preview":
        preview(sys.argv[2] if len(sys.argv) > 2 else "covers.png")
    elif cmd == "check":
        bad = []
        names = set()
        for z in range(1, 26):
            sp = build(z)
            gs = Counter(c[4] for c in sp["voxels"])
            if sp["voxelCount"] > 1300 or sp["surfaceVoxelCount"] > 900:
                bad.append("%d: слишком много кубиков (%d/%d)" % (z, sp["voxelCount"], sp["surfaceVoxelCount"]))
            if not gs[1] or not gs[2] or not gs[0]:
                bad.append("%d: пустая группа %s" % (z, dict(gs)))
            if any(c[3] < 0x1000 or c[3] > 0xFFFFFF for c in sp["voxels"]):
                bad.append("%d: цвет вне диапазона (3-значный hex?)" % z)
            if not 8.5 <= sp["bounds"]["size"][0] <= 11 or sp["bounds"]["size"][1] < 2.5:
                bad.append("%d: размер %s" % (z, sp["bounds"]["size"]))
            if sp["name"] in names:
                bad.append("%d: имя повторяется" % z)
            names.add(sp["name"])
            if sp["appearance"]["openStyle"] not in ("curtain", "swing", "burst", "sink", "rise"):
                bad.append("%d: openStyle" % z)
        print("covers: 25 checked, %d problems" % len(bad))
        for b in bad:
            print("  " + b)
        sys.exit(1 if bad else 0)
    elif cmd == "json":
        import os

        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        for z in range(1, 26):
            open(os.path.join(out, "spawn_cover_%02d.luamod" % z), "w", encoding="utf-8", newline="\n").write(luamod(build(z)))
        print("written 25 modules to", out)
    else:
        for z in range(1, 26):
            s = build(z)
            print(z, s["name"], s["appearance"]["openStyle"], s["voxelCount"], "surf", s["surfaceVoxelCount"], [round(i, 2) for i in s["bounds"]["size"]], ["%06x" % c for c in s["particleColors"]])


if __name__ == "__main__":
    main()
