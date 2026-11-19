from gymlib import *
import db_06

NAME = 'ST_06_Golden'
T = 1.4


def coin_stack(name, x, y, z, n, r, mat):
    prof = [(0, 0)]
    for i in range(n):
        z0 = i * 0.075
        prof += [(z0, r - 0.015), (z0 + 0.01, r), (z0 + 0.065, r)]
    prof += [(n * 0.075, r - 0.015), (n * 0.075, 0)]
    return lathe(name, prof, mat, 10, 'Z', loc=(x, y, z), ol=0.02)


def column(n, x, y, h, gold, deep):
    z0 = 0.3
    prof = [(0, 0), (0, 0.46), (0.08, 0.5), (0.16, 0.46), (0.22, 0.34), (0.3, 0.3), (h - 0.34, 0.3), (h - 0.26, 0.36),
            (h - 0.16, 0.44), (h - 0.08, 0.5), (h, 0.5), (h, 0)]
    lathe('col_' + n, prof, gold, 12, 'Z', loc=(x, y, z0))
    torus('col_ring_a_' + n, 0.33, 0.045, deep, 12, 5, 'Z', loc=(x, y, z0 + 0.55), ol=0.02)
    torus('col_ring_b_' + n, 0.33, 0.045, deep, 12, 5, 'Z', loc=(x, y, z0 + h - 0.6), ol=0.02)


def build():
    begin(NAME, ol=0.04)
    M = db_06.mats()
    gold, deep, ruby, emerald, sapph, pearl, velvet, glint, spark = (
        M[k] for k in ('gold', 'deep', 'ruby', 'emerald', 'sapph', 'pearl', 'velvet', 'glint', 'spark'))
    marble = toon('tre_marble', '#efe2cc', shade='#b09a86', light='#fffaf0', spec=0.5)
    purple = toon('tre_panel', '#4a2a7a', shade='#241040', light='#7a52b0', spec=0.4)
    s = stats(db_06.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    gems = (ruby, emerald, sapph, emerald, ruby)

    # ---- base, altar, deck, cushion
    box('base', (10.8, 3.0, 0.3), marble, bev=0.06, loc=(0, 0, 0.15))
    box('base_trim', (10.9, 0.1, 0.1), gold, bev=0.03, bsegs=1, loc=(0, -1.5, 0.3))
    ha = T - 0.72
    box('altar', (9.2, 2.5, ha), purple, bev=0.08, loc=(0, 0, 0.3 + ha / 2))
    for i, z in enumerate((0.34, T - 0.44)):
        box('altar_band_%d' % i, (9.3, 2.6, 0.1), gold, bev=0.03, bsegs=1, loc=(0, 0, z), ol=0.025)
    zg = 0.3 + ha / 2
    for i, x in enumerate((-3.4, -1.7, 0.0, 1.7, 3.4)):
        crystal('altar_gem_%d' % i, 0.15, 0.34, gems[i], sides=6, tip=0.3, both=True, loc=(x, -1.26, zg), rot=aim((0, -1, 0)), ol=0.02)
    box('deck', (8.9, 2.8, 0.22), deep, bev=0.05, loc=(0, 0, T - 0.31))
    box('cushion', (7.6, 1.9, 0.2), velvet, bev=0.08, loc=(0, 0, T - 0.1))
    for sy in (-1, 1):
        box('cushion_trim_%d' % sy, (7.7, 0.07, 0.1), gold, bev=0.02, bsegs=1, loc=(0, sy * 0.96, T - 0.1), ol=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('F' if sy < 0 else 'B')
            cone('tassel_' + n, 0.08, 0.3, gold, 6, loc=(sx * 3.8, sy * 0.95, T - 0.1), rot=(180, 0, 0), ol=0.015)
            sphere('tassel_ball_' + n, 0.1, gold, 8, 5, loc=(sx * 3.8, sy * 0.95, T - 0.06), ol=0.015)

    # ---- cradles
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('a' if sy < 0 else 'b')
            x = sx * cx + sy * 0.42
            ptop = hz - 0.15
            ph = ptop - T
            box('cradle_post_' + n, (0.28, 0.6, ph), gold, bev=0.05, bsegs=1, loc=(x, 0, T + ph / 2))
            for e in (-1, 1):
                box('cradle_claw_%s%d' % (n, e), (0.28, 0.14, 0.27), deep, bev=0.04, bsegs=1, loc=(x, e * 0.26, hz - 0.015))
            crystal('cradle_gem_' + n, 0.06, 0.14, ruby if sx < 0 else sapph, sides=4, tip=0.4, both=True,
                    loc=(x, -0.31, T + ph / 2), rot=aim((0, -1, 0)), ol=0.015)

    # ---- sign geometry
    zs = top + 0.55
    ys = 0.95
    hc = (zs + 0.8) - 0.3

    # ---- columns
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        px = sx * 4.9
        column('back_' + n, px, 0.95, hc, gold, deep)
        sphere('col_finial_' + n, 0.2, pearl, 10, 6, loc=(px, 0.95, 0.3 + hc + 0.18), ol=0.02)
        crystal('col_gem_back_' + n, 0.11, 0.24, emerald if sx < 0 else ruby, sides=6, tip=0.35, loc=(px, 0.95 - 0.3, 0.3 + hc * 0.5),
                rot=aim((0, -1, 0)), ol=0.018)
        column('front_' + n, px, -0.95, 2.6, gold, deep)
        sphere('col_finial_front_' + n, 0.17, pearl, 10, 6, loc=(px, -0.95, 0.3 + 2.6 + 0.15), ol=0.02)
        crystal('col_gem_front_' + n, 0.11, 0.24, sapph if sx < 0 else emerald, sides=6, tip=0.35, loc=(px, -0.95 - 0.3, 1.7),
                rot=aim((0, -1, 0)), ol=0.018)
    for i, dz in enumerate((-0.3, 0.3)):
        box('rail_%d' % i, (9.5, 0.25, 0.2), deep, bev=0.04, bsegs=1, loc=(0, 1.2, zs + dz))

    # ---- coin piles on the deck ends
    for sx in (-1, 1):
        for j, (y, cn) in enumerate(((-0.7, 5), (0.0, 4), (0.7, 3))):
            coin_stack('coins_%d_%d' % (sx, j), sx * 4.1, y, T - 0.2, cn, 0.26, gold if (j + (sx > 0)) % 2 else deep)

    # ---- crown-topped sign
    box('sign_frame', (5.25, 0.14, 1.15), gold, bev=0.04, bsegs=1, loc=(0, ys + 0.05, zs))
    box('sign_plaque', (5.0, 0.2, 0.95), purple, bev=0.06, loc=(0, ys - 0.05, zs))
    text('sign_text', 'CAMP GYM', 0.58, 0.05, glint, loc=(0, ys - 0.25, zs), rot=(90, 0, 0))
    for sx in (-1, 1):
        for e in (-1, 1):
            sphere('sign_rivet_%d_%d' % (sx, e), 0.07, pearl, 8, 5, loc=(sx * 2.35, ys - 0.15, zs + e * 0.38), ol=0.015)
    zc = zs + 0.575 + 0.1
    box('crown_band', (2.4, 0.22, 0.2), gold, bev=0.05, bsegs=1, loc=(0, ys - 0.05, zc))
    for i, x in enumerate((-1.0, -0.5, 0.0, 0.5, 1.0)):
        h = 0.5 if i == 2 else 0.36
        cone('crown_pt_%d' % i, 0.13, h, gold, 6, loc=(x, ys - 0.05, zc + 0.1), ol=0.02)
        sphere('crown_pearl_%d' % i, 0.065, pearl, 8, 5, loc=(x, ys - 0.05, zc + 0.1 + h + 0.03), ol=0.015)
    for i, (x, g) in enumerate(((-0.7, emerald), (0.0, ruby), (0.7, sapph))):
        crystal('crown_gem_%d' % i, 0.07, 0.16, g, sides=4, tip=0.4, both=True, loc=(x, ys - 0.19, zc), rot=aim((0, -1, 0)), ol=0.015)

    # ---------------- FX
    fx(True)
    rnd = random.Random(106)
    sphere('fx_aura', 2.4, ghost('gold_aura', '#ffcf5a', 1.0, 0.1), 16, 10, loc=(0, 0.6, top - 0.6), scale=(1.5, 0.45, 0.6))
    for i in range(5):
        a = math.radians(30 + 30 * i)
        crystal('fx_glint_%d' % i, 0.08, 0.24, glint, sides=4, tip=0.4, both=True,
                loc=(3.3 * math.cos(a), 0.3, 2.0 + 2.2 * math.sin(a)), rot=(rnd.uniform(0, 30), rnd.uniform(0, 30), rnd.uniform(0, 90)))
    for i in range(10):
        star('fx_sparkle_%d' % i, rnd.uniform(0.12, 0.22), 0.035, 4, 0.02, spark if i % 2 else glint,
             loc=(rnd.uniform(-4.4, 4.4), -rnd.uniform(1.2, 1.5), rnd.uniform(1.8, 4.8)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)

    display(NAME, db_06.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
