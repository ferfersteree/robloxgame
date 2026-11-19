from gymlib import *
import db_03

NAME = 'ST_03_Bronze'
T = 1.35


def build():
    begin(NAME, ol=0.04)
    M = db_03.mats()
    bronze, dbronze, patina, gold = M['bronze'], M['dbronze'], M['patina'], M['gold']
    turq, red = M['turq'], M['red']
    coal = glow('bronze_coal', '#ff8a2a', 2.2)
    s = stats(db_03.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    zs = top + 0.8                 # sign centre height

    def shield(n, x, y, z):
        lathe('shield_' + n, [(-0.06, 0), (-0.06, 0.6), (-0.02, 0.68), (0.04, 0.68), (0.08, 0.6), (0.08, 0)],
              bronze, 14, 'Y', loc=(x, y, z), sharp=20)
        torus('shield_rim_' + n, 0.68, 0.05, dbronze, 14, 5, 'Y', loc=(x, y, z), ol=0.02)
        sphere('shield_boss_' + n, 0.2, gold, 10, 6, 'Y', loc=(x, y - 0.08, z), scale=(1, 0.5, 1))
        torus('shield_enamel_' + n, 0.4, 0.035, turq, 12, 4, 'Y', loc=(x, y - 0.06, z), ol=0.015)
        for k in range(4):
            a = math.radians(k * 90 + 45)
            sphere('shield_stud_%s%d' % (n, k), 0.06, gold, 6, 4, loc=(x + 0.5 * math.cos(a), y - 0.07, z + 0.5 * math.sin(a)), ol=0.012)
        box('shield_foot_' + n, (0.9, 0.7, 0.1), dbronze, bev=0.03, bsegs=1, loc=(x, y, T + 0.05))

    def brazier(n, x, y):
        zb = T + 0.55
        for k in range(3):
            a = math.radians(90 + k * 120)
            tube('brazier_leg_%s%d' % (n, k),
                 [(x + 0.32 * math.cos(a), y + 0.32 * math.sin(a), T + 0.04), (x + 0.16 * math.cos(a), y + 0.16 * math.sin(a), zb + 0.05)],
                 0.05, dbronze, segs=5, ol=0.02)
        lathe('brazier_bowl_' + n, [(zb, 0), (zb, 0.16), (zb + 0.1, 0.3), (zb + 0.28, 0.44), (zb + 0.36, 0.46), (zb + 0.34, 0.36), (zb + 0.26, 0)],
              bronze, 12, 'Z', loc=(x, y, 0), sharp=20)
        torus('brazier_rim_' + n, 0.45, 0.045, gold, 12, 4, 'Z', loc=(x, y, zb + 0.36), ol=0.02)
        sphere('brazier_coals_' + n, 0.3, coal, 10, 6, loc=(x, y, zb + 0.27), scale=(1, 1, 0.35))

    # ---- base, legs, deck
    box('base', (10.0, 3.0, 0.3), dbronze, bev=0.08, loc=(0, 0, 0.15))
    box('base_step', (9.8, 2.8, 0.1), bronze, bev=0.04, bsegs=1, loc=(0, 0, 0.35))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl('leg_%d%d' % (sx, sy), 0.22, T - 0.3 - 0.4, bronze, segs=10, bev=0.05, axis='Z', loc=(sx * 4.2, sy * 1.0, 0.4 + (T - 0.7) / 2), sharp=20)
    for sy in (-1, 1):
        box('beam_%d' % sy, (8.4, 0.2, 0.2), dbronze, bev=0.04, bsegs=1, loc=(0, sy * 1.0, 0.75))
    box('deck', (9.6, 2.7, 0.3), dbronze, bev=0.06, loc=(0, 0, T - 0.15))
    box('apron', (9.2, 0.14, 0.5), bronze, bev=0.04, bsegs=1, loc=(0, -1.4, T - 0.55))
    for i, x in enumerate((-3.6, -1.8, 0.0, 1.8, 3.6)):
        if i in (0, 2, 4):
            cyl('medallion_%d' % i, 0.2, 0.1, gold, segs=12, bev=0.03, axis='Y', loc=(x, -1.5, T - 0.55), ol=0.02)
            cyl('medallion_gem_%d' % i, 0.08, 0.06, turq if i != 2 else red, segs=8, bev=0.015, axis='Y', loc=(x, -1.55, T - 0.55), ol=0.012)
        else:
            cyl('medallion_%d' % i, 0.2, 0.1, patina, segs=12, bev=0.03, axis='Y', loc=(x, -1.5, T - 0.55), ol=0.02)
            cyl('medallion_gem_%d' % i, 0.08, 0.06, gold, segs=8, bev=0.015, axis='Y', loc=(x, -1.55, T - 0.55), ol=0.012)
    for i in range(8):
        sphere('deck_stud_%d' % i, 0.07, gold, 6, 4, loc=(-3.85 + 1.1 * i, -1.38, T - 0.08), ol=0.015)

    # ---- cradles: bronze posts with a seat and two prongs
    zt = hz - 0.2
    for ci, sx in enumerate((-cx, cx)):
        for fi, dx in enumerate((-0.42, 0.42)):
            x = sx + dx
            nm = '%d%d' % (ci, fi)
            lathe('cradle_post_' + nm, [(T, 0), (T, 0.28), (T + 0.1, 0.28), (T + 0.2, 0.18), (zt - 0.12, 0.15), (zt - 0.04, 0.22), (zt, 0.22), (zt, 0)],
                  bronze, 10, 'Z', loc=(x, 0, 0), sharp=20)
            torus('cradle_ring_' + nm, 0.19, 0.03, patina, 10, 4, 'Z', loc=(x, 0, T + 0.3), ol=0.015)
            box('cradle_seat_' + nm, (0.34, 0.5, 0.1), dbronze, bev=0.03, bsegs=1, loc=(x, 0, zt + 0.05))
            for sy in (-1, 1):
                box('cradle_prong_%s%s' % (nm, 'a' if sy < 0 else 'b'), (0.2, 0.09, 0.3), gold, bev=0.03, bsegs=1,
                    loc=(x, sy * 0.24, zt + 0.2), rot=(sy * 8, 0, 0))

    # ---- shields and braziers
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        shield(n, sx * 4.1, 0.5, T + 0.8)
        brazier(n, sx * 4.3, -0.75)

    # ---- sign: plaque on two pillars with a sun crest
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        zt2 = zs + 0.55
        lathe('pillar_' + n, [(T, 0), (T, 0.3), (T + 0.12, 0.3), (T + 0.22, 0.2), (zt2 - 0.12, 0.17), (zt2 - 0.04, 0.24), (zt2 + 0.06, 0.24), (zt2 + 0.06, 0)],
              bronze, 10, 'Z', loc=(sx * 2.95, 1.3, 0), sharp=20)
        sphere('pillar_finial_' + n, 0.15, gold, 8, 5, loc=(sx * 2.95, 1.3, zt2 + 0.18), ol=0.02)
    box('sign_plaque', (4.9, 0.2, 1.0), dbronze, bev=0.06, loc=(0, 1.25, zs))
    for sz in (-1, 1):
        box('sign_trim_%d' % sz, (5.1, 0.26, 0.1), gold, bev=0.03, bsegs=1, loc=(0, 1.25, zs + sz * 0.55))
    for sx in (-1, 1):
        for sz in (-1, 1):
            sphere('sign_rivet_%d%d' % (sx, sz), 0.07, red, 6, 4, loc=(sx * 2.3, 1.13, zs + sz * 0.36), ol=0.012)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, gold, loc=(0, 1.04, zs), rot=(90, 0, 0))
    cz = zs + 0.68
    lathe('crest_disc', [(-0.06, 0), (-0.06, 0.2), (-0.02, 0.24), (0.04, 0.24), (0.06, 0.2), (0.06, 0)], gold, 12, 'Y',
          loc=(0, 1.25, cz), sharp=20)
    cyl('crest_gem', 0.1, 0.06, turq, segs=8, bev=0.015, axis='Y', loc=(0, 1.19, cz), ol=0.012)
    for k in range(6):
        a = math.radians(k * 60 + 30)
        d = Vector((math.cos(a), 0, math.sin(a)))
        crystal('crest_ray_%d' % k, 0.06, 0.16, bronze, sides=4, tip=0.4, loc=Vector((0, 1.25, cz)) + d * 0.22, rot=aim(d), ol=0.015)

    # ---- effects: a few star glints
    fx(True)
    spk = glow('spark_white', '#ffffff', 2.5)
    for i, (p, r) in enumerate((((-3.5, -1.2, 3.3), 0.24), ((3.0, -1.2, 2.2), 0.2), ((0.3, -1.2, 3.7), 0.17))):
        star('fx_glint_%d' % i, r, 0.04, 4, 0.02, spk, loc=p, rot=(90, 0, 0))
    fx(False)

    display(NAME, db_03.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
