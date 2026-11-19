from gymlib import *
import db_08

DROP = 1.5
SHELF = (1.3,)   # single deck - the stand holds only the current pair


def build():
    begin('ST_08_Crystal', ol=0.04)
    M = db_08.mats()
    silver, gold, rockm = M['silver'], M['gold'], M['rockm']
    vio, pink, cyan = M['vio'], M['pink'], M['cyan']
    cols = [vio, pink, cyan]
    marble = toon('marble', '#eef0fb', shade='#9a9fd8', light='#ffffff', spec=0.6)
    glass = toon('glass', '#bfeeff', shade='#7aaeea', light='#ffffff', spec=1.0, rim=0.9, emit=0.08)
    plaque = toon('plaque_violet', '#3b2a80', shade='#1e1450', light='#5a44b0', spec=0.4)
    cg = glow('cyan_glow', '#6ff0ff', 2.4)
    rnd = random.Random(8)

    box('base', (10.0, 3.0, 0.25), marble, bev=0.07, loc=(0, 0, 0.125 + DROP))
    box('base_glow', (8.8, 0.05, 0.07), cg, bev=0.0, loc=(0, -1.5, 0.12 + DROP), ol=0)
    # columns
    for cx in (-4.5, 4.5):
        for cy in (-1.1, 1.1):
            n = ('L' if cx < 0 else 'R') + ('F' if cy < 0 else 'B')
            lathe('column_' + n, [(0.25, 0), (0.25, 0.32), (0.38, 0.32), (0.46, 0.2), (1.06, 0.2), (1.14, 0.3), (1.3, 0.3), (1.3, 0)],
                  silver, 6, 'Z', loc=(cx, cy, DROP), sharp=20)
            for i, z in enumerate((0.75 + DROP,)):
                torus('column_ring_%s%d' % (n, i), 0.22, 0.05, gold, 10, 5, 'Z', loc=(cx, cy, z), ol=0.02)
            if cy < 0:
                crystal('finial_' + n, 0.2, 0.62, cols[1 if cx < 0 else 2], sides=6, tip=0.45, loc=(cx, cy, 2.8))
                torus('finial_ring_' + n, 0.2, 0.045, gold, 10, 5, 'Z', loc=(cx, cy, 2.86), ol=0.02)
    # shelves
    for i, z in ((2, 2.8),):
        box('slab_%d' % i, (9.5, 2.7, 0.12), glass, bev=0.04, loc=(0, 0, z - 0.06))
        box('trim_%d' % i, (9.6, 0.12, 0.2), silver, bev=0.04, loc=(0, -1.37, z - 0.08))
        box('trim_glow_%d' % i, (9.0, 0.04, 0.05), cg, bev=0.0, loc=(0, -1.33, z - 0.22), ol=0)
        for k in range(6):
            crystal('trim_gem_%d%d' % (i, k), 0.09, 0.2, cols[(k + i) % 3], sides=4, tip=0.5, both=True,
                    loc=(-3.75 + 1.5 * k, -1.45, z - 0.08), rot=aim((0, -1, 0)), ol=0.015)
    # obelisks on the back corners
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        crystal('obelisk_' + n, 0.44, 3.0, vio, sides=6, tip=0.22, base=0.8, loc=(sx * 4.5, 1.15, 2.8), rot=(0, sx * 3, 20))
        crystal('obelisk_side_a_' + n, 0.27, 2.0, pink, sides=6, tip=0.3, loc=(sx * 4.85, 1.05, 2.8), rot=aim((sx * 0.32, 0, 1)))
        crystal('obelisk_side_b_' + n, 0.24, 1.55, cyan, sides=6, tip=0.3, loc=(sx * 4.05, 1.25, 2.8), rot=aim((-sx * 0.22, 0.1, 1)))
        crystal('obelisk_side_c_' + n, 0.17, 0.9, cyan, sides=5, tip=0.4, loc=(sx * 4.6, 0.7, 2.8), rot=aim((sx * 0.1, -0.3, 1)), ol=0.03)
        torus('obelisk_ring_' + n, 0.5, 0.06, gold, 12, 5, 'Z', loc=(sx * 4.5, 1.15, 2.9), ol=0.02)
        # geode clusters on the base at both ends
        rock('geode_' + n, 0.42, rockm, seed=4 + sx, sub=1, rough=0.14, flat=True, loc=(sx * 4.75, 0.0, 0.4 + DROP), scale=(0.6, 1.0, 0.7))
        for k in range(3):
            d = Vector((sx * 0.35, (k - 1) * 0.5, 1))
            crystal('geode_cry_%s%d' % (n, k), 0.13, rnd.uniform(0.5, 0.8), cols[k], sides=6, tip=0.4,
                    loc=(sx * 4.78, (k - 1) * 0.3, 0.5 + DROP), rot=aim(d), ol=0.03)
    # back arch with sign plaque and crystal crown
    pts = [(3.3 * math.cos(math.radians(a)), 1.25, 2.8 + 1.95 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    tube('arch', pts, 0.11, silver, segs=6)
    for i, a in enumerate((30, 60, 120, 150)):
        p = (3.3 * math.cos(math.radians(a)), 1.14, 2.8 + 1.95 * math.sin(math.radians(a)))
        crystal('arch_gem_%d' % i, 0.11, 0.24, cols[i % 3], sides=4, tip=0.5, both=True, loc=p, rot=aim((0, -1, 0)), ol=0.02)
    box('plaque', (4.9, 0.2, 0.86), plaque, bev=0.06, loc=(0, 1.2, 4.9))
    box('plaque_frame_top', (5.1, 0.26, 0.12), silver, bev=0.04, loc=(0, 1.2, 5.36))
    box('plaque_frame_bot', (5.1, 0.26, 0.12), silver, bev=0.04, loc=(0, 1.2, 4.44))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        box('plaque_frame_' + n, (0.12, 0.26, 1.04), silver, bev=0.04, loc=(sx * 2.5, 1.2, 4.9))
        crystal('plaque_gem_' + n, 0.16, 0.34, pink, sides=4, tip=0.5, both=True, loc=(sx * 2.5, 1.05, 4.9), rot=aim((0, -1, 0)), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, cg, loc=(0, 1.08, 4.9), rot=(90, 0, 0))
    for k in range(7):
        a = -66 + 22 * k
        h = 0.9 - abs(k - 3) * 0.13
        d = Vector((math.sin(math.radians(a)), 0, math.cos(math.radians(a))))
        crystal('crown_%d' % k, 0.19 - abs(k - 3) * 0.015, h, cols[k % 3], sides=6, tip=0.4,
                loc=Vector((0, 1.2, 5.3)) + Vector((d.x * 1.2, 0, 0.0)), rot=aim(d, k * 13))
    # cradles (silver posts with crystal prongs)
    for ci, cx in enumerate((-2.2, 2.2)):
        for fi, dx in enumerate((-0.42, 0.42)):
            x = cx + dx
            n = '%d%d' % (ci, fi)
            lathe('cradle_post_' + n, [(2.8, 0), (2.8, 0.2), (2.9, 0.2), (2.96, 0.1), (3.56, 0.09), (3.62, 0.14), (3.66, 0)], silver, 6, 'Z', loc=(x, 0, 0), sharp=20, ol=0.03)
            for sy in (-1, 1):
                crystal('cradle_prong_%s%s' % (n, 'a' if sy < 0 else 'b'), 0.07, 0.36, cols[(ci + fi) % 3], sides=4, tip=0.5,
                        loc=(x, sy * 0.1, 3.6), rot=aim((0, sy * 0.55, 1)), ol=0.02)

    # big geode heart under the glass deck
    rock('heart_geode', 0.62, rockm, seed=21, sub=1, rough=0.14, flat=True, loc=(0, 0.1, 0.6 + DROP), scale=(1.5, 1.0, 0.6))
    for k in range(7):
        d = Vector(((k - 3) * 0.28, -0.25 + 0.1 * (k % 2), 1))
        crystal('heart_cry_%d' % k, 0.15 - abs(k - 3) * 0.015, 0.85 - abs(k - 3) * 0.14, cols[k % 3], sides=6, tip=0.4,
                loc=((k - 3) * 0.32, 0.05, 0.62 + DROP), rot=aim(d, k * 19), ol=0.03)
    for sx in (-1, 1):
        rock('mid_geode_%d' % sx, 0.36, rockm, seed=30 + sx, sub=1, rough=0.14, flat=True, loc=(sx * 2.6, 0.3, 0.42 + DROP), scale=(1.2, 1.0, 0.6))
        for k in range(3):
            crystal('mid_cry_%d%d' % (sx, k), 0.11, 0.45 + 0.12 * (k == 1), cols[(k + (sx > 0)) % 3], sides=6, tip=0.4,
                    loc=(sx * 2.6 + (k - 1) * 0.24, 0.25, 0.45 + DROP), rot=aim(((k - 1) * 0.3, -0.2, 1)), ol=0.025)

    fx(True)
    sh = [toon('fx_shard_v', '#c79bff', emit=1.0, rim=1.0), toon('fx_shard_c', '#9ff2ff', emit=1.0, rim=1.0), toon('fx_shard_p', '#ffb0ea', emit=1.0, rim=1.0)]
    for i in range(16):
        sx = -1 if i % 2 else 1
        if i < 10:
            p = (sx * rnd.uniform(3.6, 5.4), rnd.uniform(0.3, 1.5), rnd.uniform(3.4, 6.3))
        else:
            p = (rnd.uniform(-2.6, 2.6), rnd.uniform(0.9, 1.5), rnd.uniform(5.9, 6.9))
        crystal('fx_float_%d' % i, rnd.uniform(0.07, 0.13), rnd.uniform(0.28, 0.5), sh[i % 3], sides=4, tip=0.5, both=True,
                loc=p, rot=(rnd.uniform(-40, 40), rnd.uniform(-40, 40), rnd.uniform(0, 90)))
    rain = ['#ff5a7a', '#ffb347', '#fff36b', '#6bff9e', '#5ad2ff', '#b77bff']
    for k in range(6):
        pts = arc_pts((0, 1.45, 4.8), 2.75, k * 30 + 3, k * 30 + 27, 6, 'XZ')
        tube('fx_rainbow_%d' % k, pts, 0.035, glow('rain%d' % k, rain[k], 2.2), segs=4)
    sphere('fx_crown_aura', 1.8, ghost('aura_violet', '#b98cff', 1.0, 0.1), 16, 10, loc=(0, 1.3, 5.6), scale=(1.5, 0.6, 0.8))
    for sx in (-1, 1):
        sphere('fx_mist_' + ('L' if sx < 0 else 'R'), 1.2, ghost('mist_cyan', '#9fe9ff', 0.9, 0.1), 14, 8, loc=(sx * 4.6, 0.3, 0.5 + DROP), scale=(1, 1.2, 0.5))
    spk = glow('spark_white', '#ffffff', 2.5)
    for i in range(10):
        p = (rnd.uniform(-5.0, 5.0), -rnd.uniform(1.0, 1.5), rnd.uniform(1.8, 6.2))
        star('fx_sparkle_%d' % i, rnd.uniform(0.1, 0.2), 0.035, 4, 0.02, spk, loc=p, rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)

    drop(DROP)
    display('ST_08_Crystal', 'DB_08_Crystal', [((-2.2, 0, 3.86 - DROP), (0, 0, 0)), ((2.2, 0, 3.86 - DROP), (0, 0, 0))], [], SHELF)
    return stats('ST_08_Crystal')
