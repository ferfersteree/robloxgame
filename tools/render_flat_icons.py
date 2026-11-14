"""Flat, clean shop icons (V32): thick dark outline, flat colours with a light edge on the top-left and a dark edge on the
bottom-right, one simple picture per item so it reads at a glance. Rendered offline with numpy + OpenCV at 4x and
downsampled. The shop draws them through EditableImage (Client/EggArt). Nothing is uploaded.
Usage: python tools/render_flat_icons.py <out_dir> [name ...]
"""
import sys, os, math
import numpy as np
import cv2

SIZE = 192
S = 4
N = SIZE * S
U = N / 100.0          # unit (0..100) -> work pixels
OUTLINE = (44, 18, 84)

GOLD = (255, 200, 50)
GOLD_L = (255, 228, 120)
BROWN = (170, 104, 54)
TAN = (226, 176, 104)
RED = (232, 66, 78)
GREEN = (84, 200, 92)
BLUE = (80, 150, 255)
PURPLE = (150, 90, 240)
PINK = (240, 90, 170)
TEAL = (40, 200, 190)
SILVER = (206, 214, 232)
GRAY = (128, 134, 160)
DGRAY = (84, 82, 120)
ORANGE = (255, 150, 50)
CREAM = (248, 244, 255)
WHITE = (255, 255, 255)


def px(v):
    return int(round(v * U))


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((N, N, 3), np.float32)
        self.a = np.zeros((N, N), np.float32)

    def fill(self, m, color):
        mm = m > 127
        self.rgb[mm] = color
        self.a[mm] = 1.0

    def part(self, m, color, outline=2.3, band=2.4, shade=True):
        """draw a mask as a sticker: outline, flat colour, light top-left edge, dark bottom-right edge"""
        m = (m > 127).astype(np.uint8) * 255
        if outline > 0:
            o = max(1, px(outline))
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * o + 1, 2 * o + 1))
            self.fill(cv2.dilate(m, k), OUTLINE)
        self.fill(m, color)
        if shade and band > 0:
            kb = px(band)
            M = np.float32([[1, 0, -kb], [0, 1, -kb]])
            up_left = cv2.warpAffine(m, M, (N, N))
            M2 = np.float32([[1, 0, kb], [0, 1, kb]])
            down_right = cv2.warpAffine(m, M2, (N, N))
            dark = (m > 127) & ~(up_left > 127)
            light = (m > 127) & ~(down_right > 127)
            c = np.array(color, np.float32)
            self.rgb[dark] = c * 0.74
            self.rgb[light] = np.minimum(255, c * 1.0 + (255 - c) * 0.42)

    def result(self):
        prem = np.dstack([self.rgb * self.a[..., None], self.a * 255]).astype(np.float32)
        small = cv2.resize(prem, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
        al = np.maximum(small[..., 3:4] / 255, 1e-4)
        straight = np.clip(small[..., :3] / al, 0, 255)
        return np.clip(np.dstack([straight, small[..., 3]]), 0, 255).astype(np.uint8)


def blank():
    return np.zeros((N, N), np.uint8)


def rot(pt, ang, c=(50, 50)):
    a = math.radians(ang)
    x, y = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def ell(cx, cy, rx, ry, ang=0.0):
    m = blank()
    cv2.ellipse(m, (px(cx), px(cy)), (max(1, px(rx)), max(1, px(ry))), ang, 0, 360, 255, -1, cv2.LINE_AA)
    return m


def circ(cx, cy, r):
    return ell(cx, cy, r, r)


def poly(pts):
    m = blank()
    cv2.fillPoly(m, [np.array([[px(x), px(y)] for x, y in pts], np.int32)], 255, cv2.LINE_AA)
    return m


def rrect(x, y, w, h, r=3.0, ang=0.0, c=None):
    """rounded rectangle, optionally rotated about c (defaults to its centre)"""
    m = blank()
    r = min(r, w / 2, h / 2)
    parts = [(x + r, y, w - 2 * r, h), (x, y + r, w, h - 2 * r)]
    pts = []
    if ang == 0.0:
        for (xx, yy, ww, hh) in parts:
            cv2.rectangle(m, (px(xx), px(yy)), (px(xx + ww), px(yy + hh)), 255, -1, cv2.LINE_AA)
        for (cx, cy) in [(x + r, y + r), (x + w - r, y + r), (x + r, y + h - r), (x + w - r, y + h - r)]:
            cv2.circle(m, (px(cx), px(cy)), max(1, px(r)), 255, -1, cv2.LINE_AA)
        return m
    cc = c or (x + w / 2, y + h / 2)
    for (xx, yy, ww, hh) in parts:
        p = [rot(q, ang, cc) for q in [(xx, yy), (xx + ww, yy), (xx + ww, yy + hh), (xx, yy + hh)]]
        cv2.fillPoly(m, [np.array([[px(a), px(b)] for a, b in p], np.int32)], 255, cv2.LINE_AA)
    for (cx, cy) in [(x + r, y + r), (x + w - r, y + r), (x + r, y + h - r), (x + w - r, y + h - r)]:
        q = rot((cx, cy), ang, cc)
        cv2.circle(m, (px(q[0]), px(q[1])), max(1, px(r)), 255, -1, cv2.LINE_AA)
    return m


def cap(x1, y1, x2, y2, w):
    m = blank()
    cv2.line(m, (px(x1), px(y1)), (px(x2), px(y2)), 255, max(1, px(w)), cv2.LINE_AA)
    cv2.circle(m, (px(x1), px(y1)), max(1, px(w / 2)), 255, -1, cv2.LINE_AA)
    cv2.circle(m, (px(x2), px(y2)), max(1, px(w / 2)), 255, -1, cv2.LINE_AA)
    return m


def star4(cx, cy, r, ang=0.0):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.32
        a = math.radians(ang + i * 45 - 90)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return poly(pts)


def sparkle(cv, cx, cy, r, color=WHITE):
    cv.fill(star4(cx, cy, r), color)


def text(m, s, cx, cy, h):
    """centred bold text drawn into a mask"""
    font = cv2.FONT_HERSHEY_DUPLEX
    scale = h * U / 22.0
    th = max(2, int(scale * 2.2))
    (tw, tht), base = cv2.getTextSize(s, font, scale, th)
    cv2.putText(m, s, (px(cx) - tw // 2, px(cy) + tht // 2), font, scale, 255, th, cv2.LINE_AA)
    return m


# ------------------------------------------------------------------ icons
def coin_side(cv, cx, cy, r=11):
    cv.part(ell(cx, cy + 3.2, r, r * 0.52), (214, 150, 20), outline=1.8, band=0, shade=False)
    cv.part(ell(cx, cy, r, r * 0.52), GOLD, outline=1.8, band=1.6)
    cv.fill(ell(cx, cy, r * 0.62, r * 0.3), GOLD_L)


def coin_front(cv, cx, cy, r=11):
    cv.part(circ(cx, cy, r), GOLD, outline=2.0, band=2.0)
    cv.fill(circ(cx, cy, r * 0.66), (255, 214, 90))
    m = blank()
    cv2.circle(m, (px(cx), px(cy)), px(r * 0.66), 255, max(1, px(1.1)), cv2.LINE_AA)
    cv.fill(m, (214, 150, 20))
    cv.fill(rrect(cx - 1.2, cy - r * 0.42, 2.4, r * 0.84, 1.1), (214, 150, 20))


def stack(cv, x, y, n):
    for i in range(n):
        coin_side(cv, x, y - i * 4.6)


def bag_body(cv, cx, cy, sc):
    cv.part(poly([(cx - 11 * sc, cy - 26 * sc), (cx + 11 * sc, cy - 26 * sc), (cx + 17 * sc, cy - 12 * sc), (cx - 17 * sc, cy - 12 * sc)]), TAN)
    cv.part(ell(cx, cy + 2 * sc, 29 * sc, 25 * sc), TAN)
    cv.part(rrect(cx - 15 * sc, cy - 30 * sc, 30 * sc, 7 * sc, 3), RED, band=1.6)
    cv.part(ell(cx + 17 * sc, cy - 26 * sc, 4.5 * sc, 7 * sc, 40), RED, band=1.2)
    cv.part(ell(cx - 17 * sc, cy - 26 * sc, 4.5 * sc, 7 * sc, -40), RED, band=1.2)


def icon_coins1():
    cv = Canvas()
    stack(cv, 80, 86, 2)
    stack(cv, 22, 88, 1)
    bag_body(cv, 50, 62, 0.88)
    coin_front(cv, 50, 66, 10)
    sparkle(cv, 82, 40, 6, GOLD_L)
    return cv


def icon_coins2():
    cv = Canvas()
    stack(cv, 78, 88, 3)
    stack(cv, 20, 88, 2)
    bag_body(cv, 48, 58, 1.08)
    coin_front(cv, 48, 64, 12)
    sparkle(cv, 84, 28, 7, GOLD_L)
    sparkle(cv, 14, 36, 5, WHITE)
    return cv


def chest(cv, cx, cy, sc=1.0):
    cv.part(rrect(cx - 32 * sc, cy - 8 * sc, 64 * sc, 36 * sc, 5), BROWN)
    cv.part(rrect(cx - 34 * sc, cy - 26 * sc, 68 * sc, 24 * sc, 11), (138, 80, 44), band=2.2)
    cv.part(rrect(cx - 21 * sc, cy - 26 * sc, 8 * sc, 54 * sc, 2), GOLD, band=1.4)
    cv.part(rrect(cx + 13 * sc, cy - 26 * sc, 8 * sc, 54 * sc, 2), GOLD, band=1.4)
    cv.part(rrect(cx - 7 * sc, cy - 8 * sc, 14 * sc, 16 * sc, 3), GOLD_L, band=1.4)
    cv.fill(circ(cx, cy, 2.4 * sc), (160, 100, 20))


def icon_coins3():
    cv = Canvas()
    stack(cv, 50, 40, 3)
    stack(cv, 30, 44, 2)
    stack(cv, 70, 44, 2)
    chest(cv, 50, 60, 0.95)
    sparkle(cv, 86, 24, 6, GOLD_L)
    return cv


def gem(cv, cx, cy, r, color):
    cv.part(poly([(cx - r, cy - r * 0.35), (cx - r * 0.55, cy - r * 0.85), (cx + r * 0.55, cy - r * 0.85), (cx + r, cy - r * 0.35), (cx, cy + r)]), color, outline=1.9, band=1.6)
    cv.fill(poly([(cx - r * 0.5, cy - r * 0.35), (cx - r * 0.2, cy - r * 0.7), (cx + r * 0.1, cy - r * 0.35)]), WHITE)


def icon_coins4():
    cv = Canvas()
    chest(cv, 50, 48, 1.0)
    stack(cv, 22, 88, 3)
    stack(cv, 78, 88, 4)
    stack(cv, 50, 90, 2)
    gem(cv, 34, 78, 8, (80, 210, 255))
    gem(cv, 64, 76, 8, (255, 90, 130))
    sparkle(cv, 12, 30, 6, GOLD_L)
    sparkle(cv, 90, 22, 8, WHITE)
    sparkle(cv, 50, 8, 5, GOLD_L)
    return cv


def icon_charm():
    cv = Canvas()
    cv.part(cap(50, 58, 54, 90, 5.5), (60, 150, 70), band=1.2)
    c = (50, 46)
    for ang in (0, 90, 180, 270):
        def r(p):
            return rot((c[0] + p[0], c[1] + p[1]), ang, c)
        m = blank()
        for q in [(-9, -13), (9, -13)]:
            x, y = r(q)
            cv2.circle(m, (px(x), px(y)), px(11), 255, -1, cv2.LINE_AA)
        tri = [r((-19, -9)), r((19, -9)), r((0, 6))]
        cv2.fillPoly(m, [np.array([[px(a), px(b)] for a, b in tri], np.int32)], 255, cv2.LINE_AA)
        cv.part(m, GREEN, band=2.2)
    cv.part(circ(50, 46, 6), GOLD, outline=1.8, band=1.4)
    sparkle(cv, 82, 20, 8, GOLD_L)
    sparkle(cv, 16, 78, 5, WHITE)
    return cv


def icon_insight():
    cv = Canvas()
    cv.part(rrect(10, 16, 80, 58, 9), CREAM, band=2.4)
    for gy in (32, 46, 60):
        cv.fill(rrect(18, gy, 64, 1.6, 0.8), (200, 196, 225))
    m = blank()
    pts = [(20, 62), (36, 48), (48, 54), (62, 36), (78, 28)]
    cv2.polylines(m, [np.array([[px(a), px(b)] for a, b in pts], np.int32)], False, 255, px(5.2), cv2.LINE_AA)
    for a, b in pts:
        cv2.circle(m, (px(a), px(b)), px(2.6), 255, -1, cv2.LINE_AA)
    cv.part(m, GREEN, outline=1.6, band=0, shade=False)
    cv.part(poly([(70, 20), (86, 24), (77, 38)]), GREEN, outline=1.6, band=0, shade=False)
    cv.part(circ(76, 74, 18), BLUE, band=2.4)
    cv.fill(circ(76, 74, 13), WHITE)
    cv.fill(cap(76, 74, 76, 64, 2.6), OUTLINE)
    cv.fill(cap(76, 74, 84, 78, 2.6), OUTLINE)
    cv.fill(circ(76, 74, 2.2), OUTLINE)
    return cv


def icon_broker():
    cv = Canvas()
    cv.part(rrect(34, 82, 32, 9, 3), DGRAY)
    cv.part(rrect(46, 26, 8, 58, 3), SILVER, band=1.6)
    cv.part(cap(18, 34, 82, 26, 5.5), SILVER, band=1.4)
    cv.part(circ(50, 24, 7), GOLD, outline=2.0, band=1.6)
    for (x, y0, y1, ang) in [(20, 36, 62, 0), (80, 28, 54, 0)]:
        cv.fill(cap(x - 9, y0, x, y1 - 2, 1.7), (176, 176, 214))
        cv.fill(cap(x + 9, y0, x, y1 - 2, 1.7), (176, 176, 214))
    cv.part(ell(20, 64, 17, 6), SILVER, band=1.6)
    cv.part(ell(80, 56, 17, 6), SILVER, band=1.6)
    stack(cv, 80, 52, 2)
    coin_side(cv, 20, 60)
    sparkle(cv, 90, 80, 5, WHITE)
    return cv


def icon_smith():
    cv = Canvas()
    cv.part(rrect(26, 78, 48, 10, 3), DGRAY)
    cv.part(poly([(38, 62), (62, 62), (66, 80), (34, 80)]), GRAY)
    cv.part(poly([(24, 46), (24, 62), (4, 56), (4, 50)]), (150, 156, 180), band=1.6)
    cv.part(rrect(20, 44, 62, 18, 4), (166, 172, 198))
    cv.part(cap(64, 16, 74, 38, 7.5), BROWN, band=1.4)
    cv.part(rrect(52, 6, 34, 16, 4, ang=-20), (200, 206, 224), band=1.8)
    cv.fill(star4(34, 34, 7, 10), (255, 170, 60))
    cv.fill(star4(30, 34, 3.2, 0), WHITE)
    sparkle(cv, 14, 28, 4, GOLD_L)
    return cv


def icon_wrap():
    cv = Canvas()
    cv.part(rrect(20, 48, 60, 38, 5), PINK)
    cv.part(rrect(14, 36, 72, 16, 5), (255, 130, 195), band=2.0)
    cv.part(rrect(44, 36, 12, 50, 2), GOLD, band=1.4)
    cv.part(ell(36, 26, 15, 9, -28), GOLD, band=1.6)
    cv.part(ell(64, 26, 15, 9, 28), GOLD, band=1.6)
    cv.part(circ(50, 30, 6.5), GOLD_L, outline=2.0, band=1.4)
    sparkle(cv, 88, 22, 6, WHITE)
    sparkle(cv, 12, 66, 5, GOLD_L)
    return cv


def crown(cv, body, trim, gems):
    cv.part(poly([(16, 64), (10, 28), (32, 46), (50, 20), (68, 46), (90, 28), (84, 64)]), body)
    cv.part(rrect(14, 62, 72, 18, 5), trim)
    for (x, y) in [(10, 27), (50, 19), (90, 27)]:
        cv.part(circ(x, y, 5.6), GOLD_L, outline=2.0, band=1.4)
    for (x, c) in zip((30, 50, 70), gems):
        cv.part(circ(x, 71, 5.2), c, outline=1.8, band=1.4)


def icon_vip():
    cv = Canvas()
    crown(cv, GOLD, (255, 176, 40), (RED, BLUE, GREEN))
    sparkle(cv, 90, 56, 6, WHITE)
    sparkle(cv, 10, 66, 4, GOLD_L)
    return cv


def icon_founder():
    cv = Canvas()
    crown(cv, PURPLE, GOLD, (PINK, (90, 220, 255), PINK))
    sparkle(cv, 90, 56, 7, WHITE)
    sparkle(cv, 12, 60, 5, GOLD_L)
    sparkle(cv, 50, 6, 4, WHITE)
    return cv


def flask(cv, cx, cy, sc, liquid, emblem=None):
    def X(v):
        return cx + (v - 50) * sc

    def Y(v):
        return cy + (v - 52) * sc

    cv.part(rrect(X(40), Y(22), 20 * sc, 28 * sc, 3), (205, 228, 255), band=1.6)
    cv.part(ell(X(50), Y(66), 29 * sc, 27 * sc), liquid)
    cv.part(rrect(X(36), Y(17), 28 * sc, 8 * sc, 3), (230, 242, 255), band=1.2)
    cv.part(rrect(X(42), Y(4), 16 * sc, 14 * sc, 3), BROWN, band=1.2)
    cv.fill(ell(X(36), Y(58), 5 * sc, 8 * sc, 25), WHITE)
    if emblem == "star":
        cv.fill(star4(X(53), Y(68), 11 * sc), WHITE)
    elif emblem == "gem":
        cv.fill(poly([(X(42), Y(64)), (X(48), Y(58)), (X(58), Y(58)), (X(64), Y(64)), (X(53), Y(78))]), WHITE)
    elif emblem == "equal":
        cv.fill(rrect(X(40), Y(62), 26 * sc, 5 * sc, 2), WHITE)
        cv.fill(rrect(X(40), Y(72), 26 * sc, 5 * sc, 2), WHITE)
    elif emblem == "clover":
        for (dx, dy) in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
            cv.fill(circ(X(53 + dx), Y(68 + dy), 5 * sc), WHITE)


def icon_fortune20():
    cv = Canvas()
    flask(cv, 50, 54, 1.0, (255, 190, 40), "star")
    sparkle(cv, 86, 24, 7, GOLD_L)
    sparkle(cv, 14, 40, 5, WHITE)
    return cv


def icon_jackpot20():
    cv = Canvas()
    flask(cv, 50, 54, 1.0, (244, 80, 150), "gem")
    sparkle(cv, 86, 24, 7, WHITE)
    sparkle(cv, 14, 40, 5, GOLD_L)
    return cv


def icon_fair30():
    cv = Canvas()
    flask(cv, 50, 54, 1.0, (40, 200, 190), "equal")
    sparkle(cv, 86, 28, 6, WHITE)
    return cv


def icon_luck30():
    cv = Canvas()
    flask(cv, 50, 54, 1.0, (84, 200, 92), "clover")
    sparkle(cv, 86, 24, 6, GOLD_L)
    return cv


def icon_hour_bundle():
    cv = Canvas()
    flask(cv, 22, 62, 0.62, (255, 190, 40), "star")
    flask(cv, 78, 62, 0.62, (40, 200, 190), "equal")
    flask(cv, 50, 56, 0.88, (244, 80, 150), "gem")
    sparkle(cv, 90, 14, 6, GOLD_L)
    sparkle(cv, 8, 24, 5, WHITE)
    return cv


def icon_server15():
    cv = Canvas()
    cv.part(rrect(30, 86, 40, 8, 3), DGRAY)
    cv.part(circ(46, 52, 34), (60, 140, 255), band=2.6)
    for pts in ([(26, 38), (38, 30), (48, 40), (40, 52), (28, 50)], [(52, 58), (66, 52), (72, 66), (60, 78), (50, 70)]):
        cv.fill(poly(pts), (84, 204, 100))
    cv.fill(ell(34, 38, 6, 9, 30), WHITE)
    m = blank()
    cv.part(circ(78, 24, 17), GOLD, band=2.0)
    t = blank()
    text(t, "x2", 78, 25, 17)
    cv.fill(t, OUTLINE)
    return cv


def icon_bag():
    cv = Canvas()
    m = blank()
    cv2.ellipse(m, (px(50), px(30)), (px(14), px(13)), 0, 180, 360, 255, px(5.5), cv2.LINE_AA)
    cv.part(m, (150, 84, 40), outline=1.8, band=0, shade=False)
    cv.part(rrect(22, 28, 56, 60, 15), ORANGE)
    cv.part(rrect(30, 56, 40, 26, 8), (255, 176, 86), band=1.8)
    cv.part(rrect(43, 44, 14, 10, 3), GOLD, outline=1.8, band=1.2)
    cv.fill(rrect(35, 60, 30, 2.6, 1.2), (190, 100, 30))
    sparkle(cv, 84, 22, 6, WHITE)
    return cv


ICONS = {
    "coins1": icon_coins1, "coins2": icon_coins2, "coins3": icon_coins3, "coins4": icon_coins4,
    "charm": icon_charm, "insight": icon_insight, "broker": icon_broker, "smith": icon_smith,
    "wrap": icon_wrap, "vip": icon_vip, "founder": icon_founder,
    "fortune20": icon_fortune20, "jackpot20": icon_jackpot20, "fair30": icon_fair30, "luck30": icon_luck30,
    "hour_bundle": icon_hour_bundle, "server15": icon_server15, "bag": icon_bag,
}


def main():
    out_dir = sys.argv[1]
    names = sys.argv[2:] or list(ICONS)
    os.makedirs(out_dir, exist_ok=True)
    for n in names:
        img = ICONS[n]().result()
        cv2.imwrite(os.path.join(out_dir, n + ".png"), cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA))
        bg = np.zeros((SIZE, SIZE, 3), np.float32); bg[:] = (62, 28, 118)
        a = img[..., 3:4].astype(np.float32) / 255
        cv2.imwrite(os.path.join(out_dir, n + "_preview.png"), cv2.cvtColor((img[..., :3] * a + bg * (1 - a)).astype(np.uint8), cv2.COLOR_RGB2BGR))
        print(n, "ok", flush=True)


if __name__ == "__main__":
    main()
