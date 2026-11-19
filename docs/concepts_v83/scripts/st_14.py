from gymlib import *
import db_14

NAME = 'ST_14_Celestial'
T = 1.3


def stretch(pts, k):
    return [(p[0] * k, p[1], p[2]) for p in pts]


def build():
    begin(NAME, ol=0.04)
    M = db_14.mats()
    indigo, navy, gold, silver, core, blue = (M[k] for k in ('indigo', 'navy', 'gold', 'silver', 'core', 'blue'))
    s = stats(db_14.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    W = min(11.4, max(10.0, 2 * (cx + half) + 1.2))
    rnd = random.Random(1414)

    # ---- base, deck, sign
    box('base', (W - 0.6, 2.6, T - 0.3), navy, bev=0.08, loc=(0, 0, (T - 0.3) / 2))
    box('foot', (W - 0.3, 2.8, 0.2), silver, bev=0.05, loc=(0, 0, 0.1))
    box('deck', (W, 3.0, 0.3), indigo, bev=0.07, loc=(0, 0, T - 0.15))
    box('deck_trim', (W + 0.06, 0.08, 0.12), gold, bev=0.03, bsegs=1, loc=(0, -1.5, T - 0.1), ol=0.02)
    box('sign_frame', (5.5, 0.1, 1.0), silver, bev=0.06, loc=(0, -1.33, 0.7))
    box('sign_plaque', (5.3, 0.12, 0.84), navy, bev=0.05, loc=(0, -1.38, 0.7), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, gold, loc=(0, -1.47, 0.7), rot=(90, 0, 0))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        x0 = sx * (W / 2 - 1.2)
        star('base_star_' + n, 0.34, 0.14, 8, 0.06, gold, loc=(x0, -1.34, 0.7), rot=(90, 0, 0), ol=0.02)
        star('base_star_s_' + n, 0.15, 0.06, 4, 0.05, silver, loc=(x0 + sx * 0.5, -1.33, 0.95), rot=(90, 0, 0), ol=0.015)
        star('base_star_t_' + n, 0.12, 0.05, 4, 0.05, silver, loc=(x0 - sx * 0.5, -1.33, 0.45), rot=(90, 0, 0), ol=0.015)
    for i in range(5):
        star('deck_star_%d' % i, 0.14, 0.055, 5, 0.03, gold, loc=(-3.6 + 1.8 * i, -1.2, T + 0.02), rot=(0, 0, rnd.uniform(0, 70)), ol=0.015)

    # ---- armillary arch behind the pair
    Rz = 3.5
    a1 = stretch(arc_pts((0, 1.3, T), Rz, 0, 180, 24, 'XZ'), 1.45)
    tube('arch_gold', a1, 0.12, gold, 6)
    a2 = stretch(arc_pts((0, 1.3, T), Rz - 0.5, 0, 180, 20, 'XZ'), 1.4)
    tube('arch_silver', a2, 0.07, silver, 6, ol=0.025)
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        box('arch_foot_' + n, (0.7, 0.7, 0.3), silver, bev=0.06, loc=(sx * Rz * 1.45, 1.3, T + 0.15))
    for i in range(1, 8):
        p = a1[i * 3]
        sphere('arch_stud_%d' % i, 0.1, core if i == 4 else gold, 6, 4, loc=(p[0], p[1] - 0.05, p[2]), ol=0.015)
    for i in range(1, 6):
        p = a2[i * 3 + 1]
        sphere('arch_stud_s_%d' % i, 0.07, silver, 6, 4, loc=(p[0], p[1] - 0.04, p[2]), ol=0.012)
    torus('armillary_ring', 1.6, 0.05, gold, 24, 5, 'Y', loc=(0, 1.1, hz + 1.0), rot=(18, 0, 0), ol=0.02)
    cz = T + Rz + 0.12 + 0.25
    cpts = arc_pts((0, 1.3, cz), 0.3, 160, 380, 8, 'XZ')
    tube('arch_crescent', cpts, [0, 0.06, 0.09, 0.11, 0.11, 0.11, 0.09, 0.06, 0], silver, segs=6, ol=0.02)
    star('arch_finial_star', 0.2, 0.08, 8, 0.08, core, loc=(0, 1.3, cz + 0.06), rot=(90, 0, 0), ol=0.02)

    # ---- crescent obelisks at the front corners
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        x, y = sx * (W / 2 - 0.4), -1.0
        box('obe_plinth_' + n, (0.75, 0.75, 0.3), silver, bev=0.06, loc=(x, y, T + 0.15))
        lathe('obelisk_' + n, [(T + 0.3, 0), (T + 0.3, 0.32), (T + 0.45, 0.26), (T + 2.0, 0.14), (T + 2.1, 0.18), (T + 2.25, 0)], indigo, 8, 'Z', loc=(x, y, 0))
        torus('obe_band_' + n, 0.3, 0.05, gold, 10, 5, 'Z', loc=(x, y, T + 0.65), ol=0.02)
        pts = arc_pts((x, y, T + 2.6), 0.3, 160, 380, 8, 'XZ')
        tube('obe_crescent_' + n, pts, [0, 0.06, 0.09, 0.11, 0.11, 0.11, 0.09, 0.06, 0], silver, segs=6, ol=0.02)
        star('obe_star_' + n, 0.16, 0.06, 4, 0.06, core, loc=(x, y, T + 2.7), rot=(90, 0, 0), ol=0.015)

    # ---- floating star stones above the pair
    for i, x in enumerate((-4.3, -2.9, -1.0, 1.0, 2.9, 4.3)):
        z = min(5.1, top + 0.65 + 0.3 * (i % 2))
        crystal('star_stone_%d' % i, 0.17, 0.62, indigo if i % 2 else navy, sides=5, tip=0.35, both=True,
                loc=(x, 0.1 + 0.15 * (i % 3), z), rot=(rnd.uniform(-15, 15), rnd.uniform(-15, 15), 0), ol=0.02)
        torus('star_stone_ring_%d' % i, 0.3, 0.025, gold, 12, 4, 'Z', loc=(x, 0.1 + 0.15 * (i % 3), z), ol=0.012)

    # ---- crescent cradles
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        X = sx * cx
        for e in (-1, 1):
            m = 'a' if e < 0 else 'b'
            px = X + e * 0.42
            ztop = hz - 0.28
            box('cr_plate_%s%s' % (n, m), (0.6, 0.7, 0.1), silver, bev=0.03, loc=(px, 0, T + 0.05))
            box('cr_post_%s%s' % (n, m), (0.28, 0.34, ztop - T - 0.1), navy, bev=0.05, loc=(px, 0, (ztop + T + 0.1) / 2))
            pts = arc_pts((px, 0, hz + 0.1), 0.3, 190, 350, 8, 'YZ')
            tube('cr_crescent_%s%s' % (n, m), pts, [0.04, 0.07, 0.09, 0.1, 0.1, 0.1, 0.09, 0.07, 0.04], gold, segs=6, ol=0.02)
            sphere('cr_star_%s%s' % (n, m), 0.07, core, 6, 4, loc=(px, 0, ztop + 0.05), ol=0.01)

    fx(True)
    star_m = glow('cel_star', '#fff0b8', 2.8)
    pl_m = glow('cel_planet', '#b0c4ff', 2.2)
    com_m = glow('cel_comet', '#d8e4ff', 3.0)
    sphere('fx_aura', 3.4, ghost('cel_aura', '#a9a8ff', 1.1, 0.11), 18, 10, loc=(0, 0.6, hz + 0.4), scale=(1.55, 0.6, 0.75))
    torus('fx_orbit', 4.6, 0.015, glow('cel_orbit', '#a8b8ff', 1.8), 40, 3, 'Z', loc=(0, 0.2, 4.7), scale=(1, 0.3, 1))
    for i in range(10):
        a = 2 * math.pi * i / 10
        p = (4.6 * math.cos(a), 0.2 + 1.38 * math.sin(a), 4.7)
        if i % 3 == 0:
            sphere('fx_planet_%d' % i, 0.1, pl_m, 8, 5, loc=p)
        else:
            star('fx_ostar_%d' % i, 0.16, 0.06, 4, 0.03, star_m, loc=p, rot=(90, 0, rnd.uniform(0, 45)))
    for k, sx in enumerate((-1, 1)):
        head = Vector((sx * 3.4, -1.1, 4.9))
        tail = head + Vector((-sx * 2.0, -0.1, 0.6))
        tube('fx_comet_%d' % k, [head, head.lerp(tail, 0.3), head.lerp(tail, 0.6), tail], [0.09, 0.07, 0.035, 0.0], com_m, segs=5)
        sphere('fx_comet_head_%d' % k, 0.12, com_m, 8, 5, loc=head)
    for i in range(12):
        star('fx_sparkle_%d' % i, rnd.uniform(0.08, 0.16), 0.03, 4, 0.02, star_m,
             loc=(rnd.uniform(-W / 2 + 0.5, W / 2 - 0.5), -rnd.uniform(1.0, 1.5), rnd.uniform(T + 0.5, 5.2)), rot=(90, 0, rnd.uniform(0, 45)))
    torus('fx_halo', 2.9, 0.02, glow('cel_halo', '#c8d0ff', 1.8), 48, 3, 'Y', loc=(0, 1.45, T + 2.9))
    fx(False)
    display(NAME, db_14.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
