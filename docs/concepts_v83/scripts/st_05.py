from gymlib import *
import db_05

NAME = 'ST_05_Granite'
T = 1.4


def build():
    begin(NAME, ol=0.04)
    M = db_05.mats()
    granite, cap, sd, sl, iron, brass, rune, spark = (M[k] for k in ('granite', 'cap', 'sd', 'sl', 'iron', 'brass', 'rune', 'spark'))
    dark = toon('gran_base', '#6a6e7c', shade='#363949', light='#9a9fb2', spec=0.2)
    s = stats(db_05.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    rnd = random.Random(105)

    # ---- base, altar, deck
    box('base', (10.4, 3.0, 0.3), dark, bev=0.06, loc=(0, 0, 0.15))
    ha = T - 0.52
    box('altar', (9.0, 2.5, ha), granite, bev=0.08, loc=(0, 0, 0.3 + ha / 2))
    box('deck', (8.6, 2.8, 0.22), cap, bev=0.05, loc=(0, 0, T - 0.11))
    for i, z in enumerate((0.5, T - 0.3)):
        box('altar_band_%d' % i, (9.1, 2.6, 0.08), iron, bev=0.02, bsegs=1, loc=(0, 0, z), ol=0.025)
    zr = 0.3 + ha / 2 + 0.02
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        box('altar_rune_a' + n, (0.07, 0.04, 0.42), rune, bev=0, loc=(sx * 3.5, -1.255, zr), ol=0)
        box('altar_rune_b' + n, (0.35, 0.04, 0.07), rune, bev=0, loc=(sx * 3.66, -1.255, zr + 0.13), ol=0)
        box('altar_rune_c' + n, (0.07, 0.04, 0.26), rune, bev=0, loc=(sx * 3.2, -1.255, zr - 0.06), ol=0)
    torus('altar_ring', 0.34, 0.04, rune, 16, 4, 'Y', loc=(0, -1.26, zr), ol=0)
    sphere('altar_gem', 0.12, rune, 8, 5, loc=(0, -1.26, zr), ol=0)
    for i in range(6):
        sx = rnd.choice((-1, 1))
        box('altar_speck_%d' % i, (rnd.uniform(0.07, 0.12), 0.03, rnd.uniform(0.05, 0.08)), sd if i % 2 == 0 else sl, bev=0,
            loc=(rnd.uniform(-2.4, 2.4), -1.255, rnd.uniform(0.45, 0.95)), ol=0)

    # ---- cradles under each handle
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('a' if sy < 0 else 'b')
            x = sx * cx + sy * 0.42
            ptop = hz - 0.15
            ph = ptop - T
            box('cradle_post_' + n, (0.28, 0.6, ph), granite, bev=0.05, bsegs=1, loc=(x, 0, T + ph / 2))
            for e in (-1, 1):
                box('cradle_claw_%s%d' % (n, e), (0.28, 0.14, 0.27), cap, bev=0.04, bsegs=1, loc=(x, e * 0.26, hz - 0.015))
            box('cradle_rune_' + n, (0.06, 0.03, min(0.3, ph - 0.1)), rune, bev=0, loc=(x, -0.305, T + ph / 2), ol=0)

    # ---- sign geometry
    zs = top + 0.6
    zl = zs + 0.94
    ys = 0.95

    # ---- rune-circle pillars
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        px = sx * 4.75
        # tall back pillars carry the lintel
        py = 0.95
        hb = (zl - 0.225) - 0.3
        box('pillar_back_' + n, (0.8, 0.8, hb), granite, bev=0.08, loc=(px, py, 0.3 + hb / 2))
        box('pillar_back_band_' + n, (0.9, 0.9, 0.14), iron, bev=0.03, bsegs=1, loc=(px, py, 0.5), ol=0.025)
        zc = 0.3 + hb * 0.55
        box('pillar_back_rune_a' + n, (0.08, 0.04, 1.2), rune, bev=0, loc=(px, py - 0.405, zc), ol=0)
        box('pillar_back_rune_b' + n, (0.4, 0.04, 0.08), rune, bev=0, loc=(px, py - 0.405, zc + 0.45), ol=0)
        box('pillar_back_rune_c' + n, (0.26, 0.04, 0.08), rune, bev=0, loc=(px, py - 0.405, zc - 0.2), ol=0)
        # short front pillars with obelisk tips
        fy = -0.95
        box('pillar_front_' + n, (0.8, 0.8, 2.6), granite, bev=0.08, loc=(px, fy, 1.6))
        box('pillar_front_band_' + n, (0.9, 0.9, 0.14), iron, bev=0.03, bsegs=1, loc=(px, fy, 0.5), ol=0.025)
        box('pillar_front_cap_' + n, (0.95, 0.95, 0.2), cap, bev=0.04, loc=(px, fy, 2.99))
        cone('pillar_front_tip_' + n, 0.22, 0.45, cap, 4, r2=0.05, loc=(px, fy, 3.09), ol=0.025)
        box('pillar_front_rune_a' + n, (0.08, 0.04, 1.0), rune, bev=0, loc=(px, fy - 0.405, 1.5), ol=0)
        box('pillar_front_rune_b' + n, (0.4, 0.04, 0.08), rune, bev=0, loc=(px, fy - 0.405, 1.95), ol=0)
        box('pillar_front_rune_c' + n, (0.26, 0.04, 0.08), rune, bev=0, loc=(px, fy - 0.405, 1.15), ol=0)
        # standing stones behind the pair
        sxx = sx * 3.4
        box('stone_' + n, (0.7, 0.5, 2.3), granite, bev=0.1, loc=(sxx, 1.1, 1.45), rot=(0, sx * 5, 0))
        box('stone_rune_a' + n, (0.07, 0.04, 0.6), rune, bev=0, loc=(sxx, 0.845, 1.5), rot=(0, sx * 5, 0), ol=0)
        box('stone_rune_b' + n, (0.3, 0.04, 0.07), rune, bev=0, loc=(sxx, 0.845, 1.8), rot=(0, sx * 5, 0), ol=0)

    # ---- lintel
    box('lintel', (10.1, 0.9, 0.45), granite, bev=0.08, loc=(0, ys, zl))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        box('lintel_band_' + n, (0.2, 1.0, 0.52), iron, bev=0.03, bsegs=1, loc=(sx * 4.0, ys, zl), ol=0.025)
    for i, x in enumerate((-2.4, 0.0, 2.4)):
        box('lintel_rune_%d' % i, (0.07, 0.04, 0.28), rune, bev=0, loc=(x, ys - 0.455, zl), ol=0)

    # ---- carved granite sign (hanging under the lintel)
    box('sign_frame', (5.25, 0.14, 1.15), iron, bev=0.04, bsegs=1, loc=(0, ys + 0.05, zs))
    box('sign_plaque', (5.0, 0.2, 0.95), granite, bev=0.06, loc=(0, ys - 0.05, zs))
    text('sign_text', 'CAMP GYM', 0.58, 0.05, rune, loc=(0, ys - 0.25, zs), rot=(90, 0, 0))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        box('sign_rod_' + n, (0.07, 0.07, 0.34), iron, bev=0.02, bsegs=1, loc=(sx * 2.2, ys, zs + 0.64), ol=0.02)
        for e in (-1, 1):
            sphere('sign_rivet_%s%d' % (n, e), 0.07, brass, 8, 5, loc=(sx * 2.35, ys - 0.15, zs + e * 0.38), ol=0.015)

    # ---------------- FX
    fx(True)
    chip = glow('gran_rune', '#3cffc4', 2.6)
    sphere('fx_aura', 2.4, ghost('gran_aura', '#3cffb4', 1.0, 0.1), 16, 10, loc=(0, 0.6, top - 0.5), scale=(1.5, 0.45, 0.6))
    for i in range(5):
        a = math.radians(30 + 30 * i)
        crystal('fx_chip_%d' % i, 0.09, 0.26, chip, sides=4, tip=0.4, both=True,
                loc=(3.1 * math.cos(a), 0.4, 2.2 + 2.6 * math.sin(a)), rot=(rnd.uniform(0, 30), rnd.uniform(0, 30), rnd.uniform(0, 90)))
    for i in range(3):
        star('fx_sparkle_%d' % i, rnd.uniform(0.12, 0.2), 0.035, 4, 0.02, spark,
             loc=(rnd.uniform(-4.2, 4.2), -rnd.uniform(1.2, 1.5), rnd.uniform(1.8, 4.2)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)

    display(NAME, db_05.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
