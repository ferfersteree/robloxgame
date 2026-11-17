"""Модели копий 41-46 (V51): рисунок кубиками 0,1 и выгрузка в SpearFactoryV15.

Кубики 0,1 стад: ячейка (x, y, z) занимает [x, x+1) x [y, y+1) x [z, z+1) в единицах 0,1.
Ось копья проходит между ячейками x = -1 и x = 0 (древко 2x2: x -1..0, z -1..0), низ копья y = 0.
Как у моделей 1-40 из ModelsData: плоский рисунок толщиной 2 кубика, рука на высоте 2,5 стада, след на 5,2.

Запуск:
    python tools/spear_models.py preview out.png      # картинка всех шести (спереди, с подсветкой граней)
    python tools/spear_models.py stats                # число кубиков и коробок
    python tools/spear_models.py patch                # вписать блок в SpearFactoryV15.luau
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

# ----------------------------------------------------------------------------
# Материалы: (тень, основной, свет), 0xRRGGBB
# ----------------------------------------------------------------------------
MAT = {
    # 41 Gearwork Pike
    "copper": (0x7A4220, 0xB87333, 0xE8A860),
    "brass": (0xB8862B, 0xF2C14E, 0xFFF0B0),
    "steel": (0x5B6472, 0x9AA5B5, 0xE6EDF5),
    "iron": (0x2A2832, 0x3F3C4A, 0x5C5868),
    "oak": (0x3A2414, 0x5A3A20, 0x7A5230),
    # 42 Sporebloom Halberd
    "pale": (0xA9BDB3, 0xE4F1EA, 0xFFFFFF),
    "mint": (0x2F8F78, 0x7FE8C2, 0xD6FFF0),
    "moss": (0x2E3B24, 0x4E6234, 0x6F8C46),
    "teal": (0x174A3F, 0x24705E, 0x3F9A80),
    # 43 Boneforged Glaive
    "bone": (0xB5A47A, 0xF1E6C8, 0xFFFAEB),
    "fossil": (0x5E5038, 0x8D7C5A, 0xB3A07A),
    "leather": (0x4A2C18, 0x7A4E2C, 0xA06B3C),
    # 44 Citadel Pearl Lance
    "aqua": (0x2F6F84, 0x6FB4C4, 0xBFF3FF),
    "stone": (0x2B5566, 0x477F90, 0x78B3C2),
    "coral": (0x8C7A58, 0xC9B48A, 0xEBDDBE),
    "pearl": (0xB9C6D6, 0xF4FAFF, 0xFFFFFF),
    "kelp": (0x1F5E46, 0x2F8F6A, 0x58C196),
    # 45 Rift Conductor
    "indigo": (0x12102A, 0x2A2558, 0x4C4592),
    "volt": (0x6F62E0, 0xB4A8FF, 0xEEEAFF),
    "spark": (0xCFC8FF, 0xF4F1FF, 0xFFFFFF),
    # 46 Primordial Fang
    "basalt": (0x14100F, 0x2E2522, 0x4C3F39),
    "ash": (0x4F4743, 0x6F6560, 0x948883),
    "lava": (0xC2410C, 0xFF7A3D, 0xFFD08A),
}

Paint = tuple  # ("m", name) | ("c", 0xRRGGBB)


def M(name: str) -> Paint:
    return ("m", name)


def C(color: int) -> Paint:
    return ("c", color)


class Canvas:
    def __init__(self) -> None:
        self.v: dict[tuple[int, int, int], Paint] = {}

    # --- примитивы -------------------------------------------------------
    def put(self, x: int, y: int, z: int, p: Paint) -> None:
        self.v[(x, y, z)] = p

    def erase(self, x: int, y: int, z: int) -> None:
        self.v.pop((x, y, z), None)

    def box(self, x0: int, y0: int, x1: int, y1: int, p: Paint, z0: int = -1, z1: int = 0) -> None:
        for z in range(z0, z1 + 1):
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    self.v[(x, y, z)] = p

    def mbox(self, x0: int, y0: int, x1: int, y1: int, p: Paint, z0: int = -1, z1: int = 0) -> None:
        """Коробка и её зеркало относительно оси копья (x -> -1 - x)."""
        self.box(x0, y0, x1, y1, p, z0, z1)
        self.box(-1 - x1, y0, -1 - x0, y1, p, z0, z1)

    def poly(self, pts: list[tuple[float, float]], p: Paint, z0: int = -1, z1: int = 0) -> None:
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        for y in range(int(math.floor(min(ys))) - 1, int(math.ceil(max(ys))) + 1):
            for x in range(int(math.floor(min(xs))) - 1, int(math.ceil(max(xs))) + 1):
                if _inside(x + 0.5, y + 0.5, pts):
                    for z in range(z0, z1 + 1):
                        self.v[(x, y, z)] = p

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, p: Paint, z0: int = -1, z1: int = 0,
                ymin: float = -1e9, ymax: float = 1e9, rin: float = 0.0) -> None:
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                fx, fy = x + 0.5, y + 0.5
                if fy < ymin or fy > ymax:
                    continue
                d = ((fx - cx) / rx) ** 2 + ((fy - cy) / ry) ** 2
                if d <= 1.0 and d >= rin * rin:
                    for z in range(z0, z1 + 1):
                        self.v[(x, y, z)] = p

    def line(self, x0: int, y0: int, x1: int, y1: int, p: Paint, z0: int = -1, z1: int = 0, w: int = 1) -> None:
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            self.box(x, y, x + w - 1, y + w - 1, p, z0, z1)

    def thin(self, x0: int, y0: int, x1: int, y1: int) -> None:
        """Внутри прямоугольника убирает задний слой там, где все четыре соседа заняты (кромка остаётся в два слоя)."""
        kill = []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if (x, y, 0) in self.v and all((x + dx, y + dy, 0) in self.v for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    kill.append((x, y, 0))
        for k in kill:
            del self.v[k]

    # --- заготовки -------------------------------------------------------
    def shaft(self, y0: int, y1: int, p: Paint) -> None:
        self.box(-1, y0, 0, y1, p)

    def collar(self, y0: int, y1: int, p: Paint) -> None:
        """Кольцо шириной 4 на древке (как EEEE у старых моделей), в тех же двух слоях."""
        self.box(-2, y0, 1, y1, p, -1, 0)

    def wrap(self, y0: int, y1: int, a: int, b: int) -> None:
        """Обмотка: две краски шахматкой по рядам, виден «виток»."""
        for y in range(y0, y1 + 1):
            first, second = (a, b) if ((y - y0) // 2) % 2 == 0 else (b, a)
            for z in (-1, 0):
                self.v[(-1, y, z)] = C(first)
                self.v[(0, y, z)] = C(second)

    # --- итог ------------------------------------------------------------
    def resolve(self) -> dict[tuple[int, int, int], int]:
        """Подсветка граней: левый/верхний край светлее, правый/нижний темнее."""
        out: dict[tuple[int, int, int], int] = {}
        for (x, y, z), p in self.v.items():
            if p[0] == "c":
                out[(x, y, z)] = p[1]
                continue
            dark, base, light = MAT[p[1]]
            left = (x - 1, y, z) not in self.v
            top = (x, y + 1, z) not in self.v
            right = (x + 1, y, z) not in self.v
            bottom = (x, y - 1, z) not in self.v
            lit = left or top
            shade = right or bottom
            out[(x, y, z)] = light if (lit and not shade) else dark if (shade and not lit) else base
        return out


def _inside(px: float, py: float, pts: list[tuple[float, float]]) -> bool:
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


# ----------------------------------------------------------------------------
# Общая нижняя часть: пятка, обмотка под руку, кольца
# ----------------------------------------------------------------------------
def haft(c: Canvas, top: int, shaft_mat: str, cap_mat: str, ring_mat: str, w_a: int, w_b: int) -> None:
    c.shaft(0, top, M(shaft_mat))
    c.collar(0, 1, M(cap_mat))              # пятка
    c.box(-1, 2, 0, 2, M(cap_mat))
    c.wrap(21, 30, w_a, w_b)                # под руку (рука на 2,5 = ячейка 25)
    c.collar(19, 20, M(ring_mat))
    c.collar(31, 32, M(ring_mat))


def polyline(c: Canvas, pts: list[tuple[int, int]], p: Paint, w: int = 1, z0: int = -1, z1: int = 0) -> None:
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        c.line(x0, y0, x1, y1, p, z0, z1, w)


def lerp_path(pts: list[tuple[float, float]], y: float) -> float:
    """x кривой по y (кривая задана точками с возрастающим y)."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return pts[-1][0] if y > pts[-1][1] else pts[0][0]


# ----------------------------------------------------------------------------
# 41. Шестерённая пика: медь и латунь, две шестерни в зацеплении, длинное остриё
# ----------------------------------------------------------------------------
def gear(c: Canvas, cx: float, cy: float, r_out: float, r_in: float, teeth: int, hub: float,
         rim: str, plate: str, hubm: str, spokes: bool = False, phase: float = 0.0, rim_w: float = 2.0) -> None:
    for y in range(int(cy - r_out) - 1, int(cy + r_out) + 2):
        for x in range(int(cx - r_out) - 1, int(cx + r_out) + 2):
            fx, fy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(fx, fy)
            t = ((math.atan2(fy, fx) + phase) / (2 * math.pi) * teeth) % 1.0
            lim = r_out if t < 0.5 else r_in
            if d > lim:
                continue
            if d <= hub:
                p = M(hubm)
            elif d >= r_in - rim_w:
                p = M(rim)
            elif spokes and (abs(fx) < 1.0 or abs(fy) < 1.0):
                p = M(rim)
            else:
                p = M(plate)
            for z in (-1, 0):
                c.v[(x, y, z)] = p


def spear_gear_pike() -> Canvas:
    c = Canvas()
    haft(c, 56, "oak", "iron", "brass", 0x4A2C18, 0x6A4224)
    c.collar(12, 12, M("copper"))
    c.collar(38, 38, M("copper"))
    c.collar(43, 44, M("brass"))
    c.collar(48, 48, M("copper"))
    for y in (12, 38):
        c.put(-2, y, -1, M("brass"))
        c.put(1, y, 0, M("brass"))
    # две шестерни: зубья одной входят во впадины другой
    big = (0.0, 58.0, 7.6, 5.8, 10)
    small = (7.6, 50.4, 4.4, 3.2, 6)
    theta = math.atan2(small[1] - big[1], small[0] - big[0])           # от большой к малой
    ph_big = ((0.75 / big[4]) * 2 * math.pi) - theta                    # там впадина большой
    ph_small = ((0.25 / small[4]) * 2 * math.pi) - (theta + math.pi)    # там зуб малой
    gear(c, big[0], big[1], big[2], big[3], big[4], 1.9, "copper", "iron", "brass", phase=ph_big)
    gear(c, small[0], small[1], small[2], small[3], small[4], 1.0, "brass", "iron", "copper", phase=ph_small, rim_w=1.6)
    c.put(-1, 58, -1, C(0xFFF6C8))
    c.put(0, 58, 0, C(0xFFF6C8))
    c.collar(66, 67, M("copper"))
    c.box(-1, 65, 0, 65, M("copper"))
    # острие: длинный лист, латунное ребро (толще на 2 слоя)
    leaf = [(-4.0, 68.0), (-4.5, 73.0), (-3.8, 79.0), (-2.4, 85.0), (0.0, 93.0), (2.4, 85.0), (3.8, 79.0), (4.5, 73.0), (4.0, 68.0)]
    c.poly(leaf, M("steel"))
    c.box(-1, 68, 0, 86, M("brass"), -2, 1)
    c.box(-1, 87, 0, 91, M("brass"), -1, 0)
    c.thin(-4, 68, 3, 90)
    c.thin(-5, 52, 5, 64)
    return c


# ----------------------------------------------------------------------------
# 42. Спороцветная алебарда: бледное лезвие-секира, светящаяся шляпка позади
# ----------------------------------------------------------------------------
def spear_spore_halberd() -> Canvas:
    c = Canvas()
    haft(c, 58, "moss", "teal", "teal", 0x2E3B24, 0x4E6234)
    for y, side in ((8, 1), (13, -1), (40, 1), (46, -1)):
        if side > 0:
            c.box(1, y, 2, y, M("mint"))
            c.box(1, y + 1, 3, y + 1, M("mint"))
        else:
            c.box(-3, y, -2, y, M("mint"))
            c.box(-4, y + 1, -2, y + 1, M("mint"))
    c.collar(54, 55, M("teal"))
    c.collar(59, 60, M("pale"))
    # верхний шип: бледный лист
    spike = [(-2.6, 72.0), (-2.2, 78.0), (-1.2, 84.0), (0.0, 91.0), (1.2, 84.0), (2.2, 78.0), (2.6, 72.0)]
    c.poly(spike, M("pale"))
    c.box(-1, 61, 0, 72, M("pale"))
    # лезвие-секира справа: верх прямой, низ закруглён, в обухе вырез-«цветок»
    blade = [(1.0, 76.0), (6.0, 76.0), (10.5, 73.5), (12.5, 68.0), (11.5, 62.0), (8.0, 57.5), (4.0, 56.0), (1.0, 57.5)]
    c.poly(blade, M("pale"))
    for y in range(58, 76):
        for x in range(2, 9):
            fx, fy = x + 0.5 - 4.6, y + 0.5 - 66.0
            if (fx / 1.7) ** 2 + (fy / 1.9) ** 2 <= 1.0:
                for z in (-1, 0):
                    c.erase(x, y, z)
    c.thin(2, 58, 12, 75)
    for y in range(58, 76, 3):                                   # жилки мяты вдоль обуха
        c.put(2, y, -1, M("mint"))
        c.put(2, y, 0, M("mint"))
    # шляпка гриба слева, «цветёт» позади лезвия
    c.ellipse(-7.0, 64.0, 7.4, 6.0, M("mint"), ymin=63.0)
    c.thin(-14, 64, -1, 70)
    c.box(-14, 62, -1, 63, M("pale"))                            # пластинки под шляпкой
    c.box(-9, 52, -7, 61, M("pale"))                             # ножка
    c.line(-7, 52, -2, 49, M("moss"), w=2)                       # корешок к древку
    for sx, sy in ((-11, 67), (-7, 69), (-4, 66), (-10, 64)):
        c.box(sx, sy, sx + 1, sy + 1, C(0xFFF3A8))               # пятна
    for sx, sy, sz in ((-13, 74, -1), (-4, 78, 0), (-11, 71, 0), (5, 83, -1), (8, 80, 0), (-3, 86, 0)):
        c.put(sx, sy, sz, C(0xBFFFE8))                           # споры
    return c


# ----------------------------------------------------------------------------
# 43. Глефа из кости: изогнутое лезвие-ребро, позвонки на древке
# ----------------------------------------------------------------------------
def spear_bone_glaive() -> Canvas:
    c = Canvas()
    c.shaft(0, 62, M("bone"))
    c.collar(0, 1, M("fossil"))
    c.box(-1, 2, 0, 2, M("fossil"))
    for y in range(6, 19, 4):
        c.collar(y, y, M("fossil"))
    c.wrap(21, 30, 0x4A2C18, 0x7A4E2C)
    c.collar(19, 20, M("leather"))
    c.collar(31, 32, M("leather"))
    for y in range(36, 53, 4):
        c.collar(y, y, M("fossil"))
    c.collar(53, 55, M("leather"))
    c.collar(56, 57, M("fossil"))
    # лезвие: спинка слева изгибается вправо, режущая кромка выпуклая
    spine = [(-2.5, 58.0), (-3.5, 66.0), (-3.0, 74.0), (-0.5, 83.0), (4.0, 90.0), (11.0, 95.0)]
    edge = [(11.5, 95.5), (8.5, 90.0), (6.2, 83.0), (5.5, 75.0), (5.5, 67.0), (3.5, 59.0)]
    c.poly(spine + edge, M("bone"))
    # головка ребра: круглый сустав в основании, прожилки вдоль лезвия
    c.ellipse(-0.5, 59.0, 3.4, 2.6, M("fossil"))
    for i in range(0, 5):
        y = 63 + i * 5
        x = int(lerp_path([(p[0], p[1]) for p in [(0.5, 58.0), (0.0, 66.0), (1.0, 74.0), (3.0, 83.0), (7.0, 90.0)]], y))
        c.box(x, y, x + 1, y + 2, M("fossil"))
    for i in range(0, 12):                                       # костный гребень по спинке, толще на 2 слоя
        y = 60 + i * 3
        x = int(lerp_path([(p[0], p[1]) for p in spine[:5]], y)) + 1
        c.put(x, y, -2, M("bone"))
        c.put(x, y, 1, M("bone"))
    return c


# ----------------------------------------------------------------------------
# 44. Жемчужное копьё Цитадели: башенка с зубцами, жемчужина, длинное остриё
# ----------------------------------------------------------------------------
def spear_pearl_lance() -> Canvas:
    c = Canvas()
    haft(c, 54, "stone", "coral", "coral", 0x1F4D60, 0x2B6B80)
    c.collar(10, 10, M("coral"))
    c.collar(44, 45, M("coral"))
    kx = -3
    for y in range(36, 54):                                      # водоросль свисает с башни
        kx = -3 - (1 if (y // 3) % 2 == 0 else 0)
        c.put(kx, y, -1, M("kelp"))
        c.put(kx - 1, y, -1, M("kelp"))
    c.box(-5, 54, 4, 64, M("stone"))                             # башенка-замок
    c.box(-5, 54, 4, 55, M("coral"))
    for wx in (-3, 1):
        c.box(wx, 58, wx + 1, 61, C(0x0F2E3A))                   # бойницы
    for mx in (-5, -1, 3):
        c.box(mx, 65, mx + 1, 67, M("stone"))                    # зубцы
    for sx, sy in ((-5, 57), (4, 59), (-5, 63), (4, 56)):        # наросты
        c.put(sx, sy, -1, M("coral"))
        c.put(sx, sy, 0, M("coral"))
    c.ellipse(0.0, 70.5, 3.8, 3.8, M("pearl"), z0=-2, z1=1)      # жемчужина
    c.put(-2, 72, -2, C(0xFFFFFF))
    c.put(-3, 71, -2, C(0xFFFFFF))
    leaf = [(-2.5, 73.0), (-2.6, 79.0), (-1.8, 84.0), (0.0, 90.5), (1.8, 84.0), (2.6, 79.0), (2.5, 73.0)]
    c.poly(leaf, M("aqua"))
    c.box(-1, 73, 0, 86, M("aqua"), -2, 1)
    return c


# ----------------------------------------------------------------------------
# 45. Проводник разлома: вилка-катушка, молнии между зубцами и иглой
# ----------------------------------------------------------------------------
def spear_rift_conductor() -> Canvas:
    c = Canvas()
    haft(c, 62, "indigo", "volt", "volt", 0x12102A, 0x2A2558)
    for i, y in enumerate(range(40, 62, 2)):                     # катушка: тугие витки
        c.collar(y, y + 1, M("volt" if i % 2 == 0 else "indigo"))
    for y in (36, 62):
        c.box(-3, y, 2, y + 1, M("indigo"))                      # изоляторы
    c.box(-1, 64, 0, 79, M("volt"))                              # игла
    c.box(-1, 80, 0, 88, M("spark"))
    c.box(-1, 89, -1, 91, M("spark"), -1, 0)
    tine = [(3.0, 65.0), (5.0, 70.0), (7.0, 76.0), (8.0, 82.0), (7.0, 88.0)]
    for side in (1, -1):
        for (x0, y0), (x1, y1) in zip(tine, tine[1:]):
            xa, xb = int(round(x0)), int(round(x1))
            ya, yb = int(round(y0)), int(round(y1))
            lo, hi = min(xa, xb), max(xa, xb)
            if side > 0:
                c.box(lo, ya, hi + 1, yb, M("volt"))
            else:
                c.box(-1 - hi - 1, ya, -1 - lo, yb, M("volt"))
        c.box(5, 87, 7, 90, M("spark")) if side > 0 else c.box(-8, 87, -6, 90, M("spark"))
    # молнии: рваные линии от иглы к зубцам
    arcs = {73: [(1, 73), (3, 75), (4, 72), (6, 74)], 83: [(1, 83), (3, 85), (5, 82), (7, 84)]}
    for y0, pts in arcs.items():
        polyline(c, pts, C(0xFFFFFF))
        polyline(c, [(-1 - x, y) for x, y in pts], C(0xDDD6FF))
    return c


# ----------------------------------------------------------------------------
# 46. Первозданный клык: базальт и лава, загнутый клык, светящееся остриё
# ----------------------------------------------------------------------------
def spear_primal_fang() -> Canvas:
    c = Canvas()
    haft(c, 54, "basalt", "ash", "lava", 0x1A1514, 0x2E2522)
    for y in (6, 11, 14, 36, 41, 46):
        c.put(0, y, -1, M("lava"))
        c.put(-1, y + 1, 0, M("lava"))
    rnd = random.Random(46)
    for y in range(49, 57):                                      # венец из обломков
        for x in range(-6, 6):
            if rnd.random() < 0.82 or abs(x + 0.5) < 3:
                for z in (-1, 0):
                    c.put(x, y, z, M("basalt"))
    for sx, sy in ((-7, 51), (6, 53), (-6, 57), (5, 57)):
        for z in (-1, 0):
            c.put(sx, sy, z, M("ash"))
    for sx, sy in ((-4, 52), (0, 54), (3, 50), (-2, 49)):
        c.box(sx, sy, sx + 1, sy, M("lava"))
    # клык: от широкого основания к острию, изогнут влево
    N = 36
    left, right = [], []
    for i in range(N + 1):
        t = i / N
        y = 56.0 + 36.0 * t
        xc = -0.5 - 5.5 * t ** 1.7
        w = 6.0 * (1.0 - t) ** 1.05 + 0.5
        left.append((xc - w, y))
        right.append((xc + w, y))
    c.poly(left + right[::-1], M("basalt"))
    # раскалённые трещины идут по оси клыка
    vein = []
    for i in range(0, N, 3):
        t = i / N
        y = 58.0 + 30.0 * t
        xc = -0.5 - 5.5 * t ** 1.7
        vein.append((int(round(xc + (1.5 if (i // 3) % 2 == 0 else -1.5))), int(round(y))))
    polyline(c, vein, M("lava"))
    polyline(c, [(x + 3, y - 1) for x, y in vein[:4]], M("lava"))
    # светящееся остриё
    for (x, y, z), p in list(c.v.items()):
        if y >= 86 and p[0] == "m" and p[1] == "basalt":
            c.v[(x, y, z)] = M("lava")
    c.box(-1, 57, 0, 60, M("lava"))                              # «первый огонь» у основания
    for sx, sy, sz in ((-10, 70, -1), (7, 72, 0), (-12, 84, 0), (3, 90, -1), (8, 64, -1)):
        c.put(sx, sy, sz, C(0xFFD08A))
    return c


SPEARS = {
    "gear_pike": spear_gear_pike,
    "spore_halberd": spear_spore_halberd,
    "bone_glaive": spear_bone_glaive,
    "pearl_lance": spear_pearl_lance,
    "rift_conductor": spear_rift_conductor,
    "primal_fang": spear_primal_fang,
}


# ----------------------------------------------------------------------------
# Выгрузка: объединяем одинаковые по цвету кубики в коробки
# ----------------------------------------------------------------------------
def boxes(vox: dict[tuple[int, int, int], int]) -> list[tuple[int, int, int, int, int, int, int]]:
    left = dict(vox)
    out = []
    for key in sorted(left, key=lambda k: (k[2], k[1], k[0])):
        if key not in left:
            continue
        x0, y0, z0 = key
        col = left[key]
        x1 = x0
        while left.get((x1 + 1, y0, z0)) == col:
            x1 += 1
        y1 = y0
        while all(left.get((x, y1 + 1, z0)) == col for x in range(x0, x1 + 1)):
            y1 += 1
        z1 = z0
        while all(left.get((x, y, z1 + 1)) == col for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)):
            z1 += 1
        for z in range(z0, z1 + 1):
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    del left[(x, y, z)]
        out.append((x0, y0, z0, x1, y1, z1, col))
    return out


def build_all() -> dict[str, dict]:
    res = {}
    for name, fn in SPEARS.items():
        vox = fn().resolve()
        top = max(y for (_, y, _) in vox)
        res[name] = {"vox": vox, "top": top, "boxes": boxes(vox)}
    return res


def lua_block() -> str:
    lines = ["-- BEGIN V51 EXTRA (сгенерировано tools/spear_models.py, правьте там)", "local EXTRA={"]
    for name, d in build_all().items():
        tip = f"{{0,{(d['top'] + 0.5) / 10:.2f},0}}"
        body = ",".join("{%d,%d,%d,%d,%d,%d,%d}" % b for b in d["boxes"])
        lines.append(f"\t{name}={{tip={tip},boxes={{{body}}}}},")
    lines.append("}")
    lines.append("-- END V51 EXTRA")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Картинка для проверки глазами
# ----------------------------------------------------------------------------
def preview(path: str, scale: int = 7) -> None:
    from PIL import Image, ImageDraw

    data = build_all()
    cols = len(data)
    wv, hv = 26, 104
    img = Image.new("RGB", (cols * wv * scale, hv * scale + 24), (58, 66, 96))
    dr = ImageDraw.Draw(img)
    for i, (name, d) in enumerate(data.items()):
        ox = i * wv * scale
        # рисуем слой за слоем: сначала дальний (z=0), потом ближний (z=-1, -2)
        order = sorted(d["vox"].items(), key=lambda kv: -kv[0][2])
        for (x, y, z), col in order:
            px = ox + (x + wv // 2) * scale
            py = (hv - 1 - y) * scale
            dr.rectangle([px, py, px + scale - 1, py + scale - 1], fill=((col >> 16) & 255, (col >> 8) & 255, col & 255))
        dr.text((ox + 4, hv * scale + 4), f"{name} {len(d['vox'])}c/{len(d['boxes'])}b h={d['top'] + 1}", fill=(255, 255, 255))
    img.save(path)


def stats() -> None:
    for name, d in build_all().items():
        print(f"{name:16s} cubes={len(d['vox']):4d} boxes={len(d['boxes']):4d} height={(d['top'] + 1) / 10:.1f}")


def patch_factory(path: str) -> None:
    p = Path(path)
    t = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in t else "\n"
    t = t.replace("\r\n", "\n")
    block = lua_block()
    a = t.find("-- BEGIN V51 EXTRA")
    b = t.find("-- END V51 EXTRA")
    if a < 0 or b < 0:
        raise SystemExit("нет отметок BEGIN/END V51 EXTRA в файле")
    b = b + len("-- END V51 EXTRA")
    t = t[:a] + block + t[b:]
    p.write_bytes(t.replace("\n", nl).encode("utf-8"))
    print("block updated:", len(block), "chars")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "preview":
        preview(sys.argv[2])
    elif cmd == "stats":
        stats()
    elif cmd == "lua":
        print(lua_block())
    elif cmd == "patch":
        patch_factory(sys.argv[2] if len(sys.argv) > 2 else "source/ReplicatedStorage/V15SpearPresentation/SpearFactoryV15.luau")
    else:
        raise SystemExit(__doc__)
