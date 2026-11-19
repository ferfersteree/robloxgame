from gymlib import *


def mats():
    return dict(
        silver=toon('silver', '#dfe6f7', shade='#7f86c4', light='#ffffff', spec=1.0),
        gold=toon('gold', '#ffcf4d', shade='#c2742a', light='#fff2a6', spec=1.0),
        rockm=toon('geode_rock', '#4b3a86', shade='#281c55', light='#6d58b5', spec=0.2),
        vio=toon('cry_violet', '#a55cf2', shade='#5b2bb5', light='#e3b8ff', spec=1.0, rim=0.9, emit=0.12),
        pink=toon('cry_pink', '#ff74d4', shade='#b5349d', light='#ffd0f2', spec=1.0, rim=0.9, emit=0.12),
        cyan=toon('cry_cyan', '#58e2ff', shade='#2a86d6', light='#d8fbff', spec=1.0, rim=0.9, emit=0.12),
    )


def build():
    begin('DB_08_Crystal', ol=0.03)
    M = mats()
    silver, gold, rockm = M['silver'], M['gold'], M['rockm']
    cols = [M['vio'], M['pink'], M['cyan']]

    cyl('handle', 0.15, 1.5, silver, segs=6, bev=0.02, sharp=20)
    for i, x in enumerate((-0.4, 0.0, 0.4)):
        torus('grip_ring_%d' % i, 0.15, 0.03, gold, 12, 5, loc=(x, 0, 0), ol=0.015)
    for i, x in enumerate((-0.2, 0.2)):
        lathe('grip_band_%d' % i, [(-0.07, 0.15), (-0.05, 0.17), (0.05, 0.17), (0.07, 0.15)], M['vio'], 6, loc=(x, 0, 0), caps=False, ol=0.012, sharp=20)

    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        lathe('collar_' + n, [(0.6, 0), (0.6, 0.24), (0.68, 0.28), (0.82, 0.5), (0.92, 0.56), (0.98, 0.5), (0.98, 0)], silver, 8, scale=(s, 1, 1), sharp=20)
        for k in range(6):
            d = radial(s, 90, k * 60 + 30)
            crystal('collar_gem_%s%d' % (n, k), 0.075, 0.2, cols[(k + 1) % 3], sides=4, tip=0.5, both=True,
                    loc=Vector((s * 0.9, 0, 0)) + d * 0.57, rot=aim(d), ol=0.015)
        rock('geode_' + n, 0.6, rockm, seed=3 if s > 0 else 8, sub=1, rough=0.12, flat=True, loc=(s * 1.3, 0, 0), scale=(0.85, 1, 1))
        torus('geode_ring_' + n, 0.64, 0.055, gold, 12, 6, loc=(s * 1.08, 0, 0), ol=0.02)
        # main crystal, pointing outward along X
        crystal('main_' + n, 0.36, 0.95, cols[0], sides=6, tip=0.42, base=0.85, loc=(s * 1.0, 0, 0), rot=aim((s, 0, 0)))
        rnd = random.Random(11 if s > 0 else 23)
        for k in range(6):
            ang = k * 60 + (0 if s > 0 else 30)
            d = radial(s, 62 + rnd.uniform(-8, 8), ang)
            crystal('spike_%s%d' % (n, k), rnd.uniform(0.15, 0.2), rnd.uniform(0.62, 0.95), cols[k % 3], sides=6, tip=0.38,
                    loc=Vector((s * 1.22, 0, 0)) + d * 0.3, rot=aim(d, k * 17))
        for k in range(6):
            ang = k * 60 + 30 + (0 if s > 0 else 30)
            d = radial(s, 82 + rnd.uniform(-10, 10), ang)
            crystal('shard_%s%d' % (n, k), 0.1, rnd.uniform(0.3, 0.42), cols[(k + 2) % 3], sides=5, tip=0.5,
                    loc=Vector((s * 1.3, 0, 0)) + d * 0.5, rot=aim(d, k * 31), ol=0.02)
        for k in range(3):
            d = radial(s, 24, k * 120 + 40)
            crystal('tip_%s%d' % (n, k), 0.12, 0.44, cols[(k + 1) % 3], sides=6, tip=0.4,
                    loc=Vector((s * 1.22, 0, 0)) + d * 0.2, rot=aim(d, k * 20), ol=0.025)

    fx(True)
    rnd = random.Random(5)
    sh = [toon('fx_shard_v', '#c79bff', emit=1.0, rim=1.0), toon('fx_shard_c', '#9ff2ff', emit=1.0, rim=1.0), toon('fx_shard_p', '#ffb0ea', emit=1.0, rim=1.0)]
    for i in range(10):
        s = -1 if i % 2 else 1
        d = radial(s, rnd.uniform(40, 130), rnd.uniform(0, 360))
        p = Vector((s * 1.35, 0, 0)) + d * rnd.uniform(1.15, 1.5)
        crystal('fx_float_%d' % i, rnd.uniform(0.05, 0.09), rnd.uniform(0.2, 0.34), sh[i % 3], sides=4, tip=0.5, both=True,
                loc=p, rot=(rnd.uniform(-40, 40), rnd.uniform(-40, 40), rnd.uniform(0, 90)))
    rain = ['#ff5a7a', '#ffb347', '#fff36b', '#6bff9e', '#5ad2ff', '#b77bff']
    for s in (-1, 1):
        for k in range(6):
            pts = arc_pts((s * 1.35, 0, 0), 1.18, k * 60 + 6, k * 60 + 54, 6, 'YZ')
            tube('fx_rainbow_%s%d' % ('L' if s < 0 else 'R', k), pts, 0.022, glow('rain%d' % k, rain[k], 2.2), segs=4)
        sphere('fx_aura_' + ('L' if s < 0 else 'R'), 1.25, ghost('aura_violet', '#b98cff', 1.0, 0.1), 16, 10, loc=(s * 1.35, 0, 0))
    spk = glow('spark_white', '#ffffff', 2.5)
    for i in range(7):
        s = -1 if i % 2 else 1
        p = (s * rnd.uniform(0.9, 2.1), -rnd.uniform(0.6, 1.0), rnd.uniform(-0.4, 1.1))
        star('fx_sparkle_%d' % i, rnd.uniform(0.07, 0.14), 0.025, 4, 0.02, spk, loc=p, rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    return stats('DB_08_Crystal')
