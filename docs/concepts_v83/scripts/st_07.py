from gymlib import *
import db_07

NAME = 'ST_07_Mammoth'
T = 1.4


def totem(n, px, py, M, wood):
    bone, knuckle, fur, leather, red, teal, dark = (M[k] for k in ('bone', 'knuckle', 'fur', 'leather', 'red', 'teal', 'dark'))
    for j in range(2):
        zc = 0.3 + 0.45 + j * 0.9
        box('totem_%s%d' % (n, j), (0.7, 0.7, 0.9), wood, bev=0.07, loc=(px, py, zc))
        yf = py - 0.355
        for e in (-1, 1):
            sphere('totem_eye_%s%d%d' % (n, j, e), 0.08, teal if j == 0 else red, 8, 5, loc=(px + e * 0.15, yf, zc + 0.08), scale=(1, 0.5, 1), ol=0.015)
        box('totem_brow_%s%d' % (n, j), (0.5, 0.1, 0.09), red if j == 0 else teal, bev=0.02, bsegs=1, loc=(px, yf, zc + 0.28), ol=0.018)
        box('totem_mouth_%s%d' % (n, j), (0.34, 0.1, 0.12), dark, bev=0.02, bsegs=1, loc=(px, yf, zc - 0.22), ol=0.015)
    zt = 0.3 + 1.8
    box('totem_cap_' + n, (0.86, 0.86, 0.18), leather, bev=0.05, bsegs=1, loc=(px, py, zt + 0.09))
    for side in (-1, 1):
        pts = [(px + side * 0.2, py, zt + 0.15), (px + side * 0.5, py, zt + 0.25), (px + side * 0.72, py, zt + 0.55), (px + side * 0.62, py, zt + 0.95)]
        tube('totem_horn_%s%d' % (n, side), pts, [0.12, 0.11, 0.08, 0.0], bone, segs=7)


def build():
    begin(NAME, ol=0.04)
    M = db_07.mats()
    bone, knuckle, fur, leather, red, teal, dark, snow, spark = (
        M[k] for k in ('bone', 'knuckle', 'fur', 'leather', 'red', 'teal', 'dark', 'snow', 'spark'))
    stone = toon('mam_stone', '#6b7a96', shade='#38455e', light='#9db0cc', spec=0.2)
    wood = toon('mam_wood', '#8a5a34', shade='#4a2c18', light='#b8844e', spec=0.15)
    hide = toon('mam_hide', '#c29a68', shade='#7a5230', light='#e8c898', spec=0.15)
    furw = toon('mam_fur_w', '#d8d2c8', shade='#8f8a86', light='#ffffff', spec=0.1)
    s = stats(db_07.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    rnd = random.Random(107)

    # ---- base, altar, deck, fur rug
    box('base', (10.6, 3.0, 0.3), stone, bev=0.06, loc=(0, 0, 0.15))
    ha = T - 0.52
    box('altar', (9.4, 2.5, ha), leather, bev=0.08, loc=(0, 0, 0.3 + ha / 2))
    box('deck', (9.9, 2.8, 0.22), knuckle, bev=0.05, loc=(0, 0, T - 0.11))
    box('fur_rug', (8.4, 1.8, 0.07), furw, bev=0.03, bsegs=1, loc=(0, 0, T + 0.03), ol=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            sphere('altar_knuckle_%d%d' % (sx, sy), 0.19, knuckle, 8, 5, loc=(sx * 4.7, sy * 1.25, 0.42), ol=0.02)

    # ---- hide-stretched sign on the altar front
    zr = 0.3 + ha / 2
    box('sign_hide', (4.9, 0.14, 0.76), hide, bev=0.05, bsegs=1, loc=(0, -1.32, zr))
    text('sign_text', 'CAMP GYM', 0.58, 0.05, dark, loc=(0, -1.44, zr), rot=(90, 0, 0))
    for e in (-1, 1):
        box('sign_rod_%d' % e, (5.1, 0.1, 0.08), bone, bev=0.03, bsegs=1, loc=(0, -1.34, zr + e * 0.4), ol=0.02)
        for sx in (-1, 1):
            cone('sign_peg_%d_%d' % (e, sx), 0.07, 0.15, bone, 6, loc=(sx * 2.5, -1.4, zr + e * 0.4), rot=aim((0, -1, 0)), ol=0.015)
    for i, x in enumerate((-1.6, 0.0, 1.6)):
        for e in (-1, 1):
            if (i + e) % 2 == 0:
                box('sign_lace_%d_%d' % (i, e), (0.05, 0.03, 0.14), leather, bev=0, loc=(x, -1.405, zr + e * 0.4), ol=0)

    # ---- cradles: bone posts with tusk claws
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('a' if sy < 0 else 'b')
            x = sx * cx + sy * 0.42
            ptop = hz - 0.15
            ph = ptop - T
            box('cradle_post_' + n, (0.28, 0.6, ph), knuckle, bev=0.05, bsegs=1, loc=(x, 0, T + ph / 2))
            box('cradle_strap_' + n, (0.32, 0.64, 0.08), red, bev=0.02, bsegs=1, loc=(x, 0, T + ph * 0.5), ol=0.018)
            for e in (-1, 1):
                cone('cradle_claw_%s%d' % (n, e), 0.09, 0.42, bone, 6, loc=(x, e * 0.26, ptop), rot=aim((0, e * 0.25, 1)), ol=0.018)

    # ---- giant tusks framing the pair
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        px = sx * 4.55
        pts = [(px, 0, T - 0.05), (sx * 4.85, 0, 2.2), (sx * 4.95, 0, 3.1), (sx * 4.7, 0, 4.0), (sx * 4.1, 0, 4.75), (sx * 3.35, 0, 5.05)]
        tube('giant_tusk_' + n, pts, [0.4, 0.38, 0.34, 0.27, 0.17, 0.0], bone, segs=10)
        for i, t in enumerate((1, 2, 3)):
            tan = (Vector(pts[t + 1]) - Vector(pts[t - 1])).normalized()
            torus('giant_tusk_band_%s%d' % (n, i), (0.4, 0.37, 0.3)[i], 0.05, (red, teal, red)[i], 12, 5, 'Z', loc=pts[t], rot=aim(tan), ol=0.02)
        lathe('giant_tusk_fur_' + n, [(0, 0.55), (0.1, 0.62), (0.28, 0.5), (0.3, 0.42)], fur, 12, 'Z', loc=(px, 0, T), caps=False, ol=0.03)

    # ---- totem poles
    for sx in (-1, 1):
        totem('L' if sx < 0 else 'R', sx * 4.85, 1.0, M, wood)

    # ---- rib-bone arch behind the pair
    for i, y in enumerate((1.1, 1.28, 1.46)):
        pts = arc_pts((0, y, T), 3.85, 0, 180, 12)
        rad = [0.1] * 13
        rad[0] = rad[-1] = 0.06
        tube('rib_%d' % i, pts, rad, bone, segs=6)

    # ---- fur drapes hanging from the arch
    for i, ang in enumerate((35, 70, 110, 145)):
        a = math.radians(ang)
        px, pz = 3.85 * math.cos(a), T + 3.85 * math.sin(a)
        mat = furw if i % 2 else fur
        box('drape_%d' % i, (0.6, 0.1, 1.0), mat, bev=0.04, bsegs=1, loc=(px, 1.28, pz - 0.5))
        cone('drape_tuft_%d' % i, 0.14, 0.3, mat, 5, loc=(px, 1.28, pz - 1.0), rot=(180, 0, 0), ol=0.02)

    # ---------------- FX
    fx(True)
    breath = ghost('mam_breath', '#cfe8ff', 1.0, 0.1)
    sphere('fx_aura', 2.4, breath, 16, 10, loc=(0, 0.6, top - 0.6), scale=(1.5, 0.45, 0.6))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        sphere('fx_breath_a_' + n, 0.3, breath, 12, 7, loc=(sx * 3.1, -0.2, 3.6))
        sphere('fx_breath_b_' + n, 0.2, breath, 12, 7, loc=(sx * 3.4, -0.3, 3.9))
    for i in range(4):
        star('fx_flake_%d' % i, rnd.uniform(0.14, 0.22), 0.05, 6, 0.02, snow,
             loc=(rnd.uniform(-4.2, 4.2), -rnd.uniform(1.2, 1.5), rnd.uniform(2.0, 4.8)), rot=(90, 0, rnd.uniform(0, 45)))
    for i in range(4):
        sphere('fx_speck_%d' % i, rnd.uniform(0.03, 0.05), snow, 6, 4,
               loc=(rnd.uniform(-4.5, 4.5), rnd.uniform(-1.3, 1.0), rnd.uniform(2.0, 5.0)))
    fx(False)

    display(NAME, db_07.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
