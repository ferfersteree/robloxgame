from gymlib import *

BG = '#f6e6c6'
NAME = 'DB_03_Bronze'


def mats():
    return dict(
        bronze=toon('bronze_main', '#e09a45', shade='#8e4a1e', light='#ffe0a0', spec=1.0),
        dbronze=toon('bronze_dark', '#9a5f2a', shade='#522c12', light='#d79a58', spec=0.6),
        patina=toon('bronze_patina', '#5f8a6a', shade='#2e5148', light='#a6d4b0', spec=0.4),
        gold=toon('gold', '#ffcf4d', shade='#c2742a', light='#fff2a6', spec=1.0),
        turq=toon('bronze_turq', '#2fd6c4', shade='#168a86', light='#b4fff2', spec=1.0, rim=0.8, emit=0.1),
        red=toon('bronze_red', '#d93a2f', shade='#8e1a1a', light='#ff8b72', spec=1.0, rim=0.7, emit=0.05),
    )


def build():
    begin(NAME, ol=0.03)
    M = mats()
    bronze, dbronze, patina, gold = M['bronze'], M['dbronze'], M['patina'], M['gold']
    turq, red = M['turq'], M['red']

    # ---- handle
    cyl('handle', 0.15, 1.5, dbronze, segs=8, bev=0.02, sharp=20)
    for i, x in enumerate((-0.4, 0.0, 0.4)):
        torus('grip_ring_%d' % i, 0.15, 0.03, bronze, 12, 5, loc=(x, 0, 0), ol=0.015)
    for i, x in enumerate((-0.2, 0.2)):
        lathe('grip_band_%d' % i, [(-0.07, 0.15), (-0.05, 0.17), (0.05, 0.17), (0.07, 0.15)], red, 8,
              loc=(x, 0, 0), caps=False, ol=0.012, sharp=20)

    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        off = 0 if s > 0 else 22.5
        # flared collar
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.24), (0.66, 0.27), (0.74, 0.4), (0.82, 0.47), (0.9, 0.46), (0.92, 0.38), (0.92, 0)],
              bronze, 12, scale=(s, 1, 1), sharp=20)
        # layered plates with chamfers
        lathe('plateA_' + n, [(0.92, 0), (0.92, 0.58), (0.98, 0.66), (1.1, 0.66), (1.16, 0.58), (1.16, 0)],
              bronze, 12, scale=(s, 1, 1), sharp=20)
        lathe('plateB_' + n, [(1.16, 0), (1.16, 0.52), (1.2, 0.58), (1.3, 0.58), (1.34, 0.52), (1.34, 0)],
              dbronze, 12, scale=(s, 1, 1), sharp=20)
        lathe('cap_' + n, [(1.34, 0), (1.34, 0.4), (1.38, 0.44), (1.42, 0.4), (1.44, 0.3), (1.44, 0)],
              bronze, 12, scale=(s, 1, 1), sharp=20)
        # sun-ray fins around plate A (gear / sunburst silhouette)
        for k in range(8):
            a = k * 45 + off
            d = radial(s, 80, a)
            crystal('fin_%s%d' % (n, k), 0.12, 0.42, bronze, sides=4, tip=0.4, base=0.85,
                    loc=Vector((s * 1.04, 0, 0)) + radial(s, 90, a) * 0.58, rot=aim(d, 45))
        # scalloped bumps between the fins
        for k in range(8):
            a = k * 45 + 22.5 + off
            sphere('scallop_%s%d' % (n, k), 0.1, gold, 6, 4, loc=Vector((s * 1.04, 0, 0)) + radial(s, 90, a) * 0.66, ol=0.015)
        # embossed studs ring on plate B face
        for k in range(6):
            a = math.radians(k * 60 + 30)
            sphere('stud_%s%d' % (n, k), 0.055, gold, 6, 4, loc=(s * 1.345, 0.485 * math.cos(a), 0.485 * math.sin(a)), ol=0.012)
        # patina bands and red enamel ring
        torus('patina_a_' + n, 0.67, 0.035, patina, 12, 4, loc=(s * 1.04, 0, 0), ol=0.015)
        torus('patina_b_' + n, 0.585, 0.035, patina, 12, 4, loc=(s * 1.25, 0, 0), ol=0.015)
        torus('red_ring_' + n, 0.57, 0.04, red, 12, 4, loc=(s * 1.17, 0, 0), ol=0.015)
        # sun emblem on the end cap
        star('sun_' + n, 0.34, 0.2, 8, 0.05, gold, loc=(s * 1.45, 0, 0), rot=(0, 90, 0), ol=0.02)
        cyl('enamel_' + n, 0.13, 0.06, turq, segs=10, bev=0.02, loc=(s * 1.46, 0, 0), ol=0.015)

    # ---- effects: a few star glints
    fx(True)
    spk = glow('spark_white', '#ffffff', 2.5)
    for i, (p, r) in enumerate((((1.0, -0.9, 0.6), 0.2), ((-1.05, -0.95, -0.1), 0.16), ((0.2, -0.7, 0.55), 0.13))):
        star('fx_glint_%d' % i, r, 0.035, 4, 0.02, spk, loc=p, rot=(90, 0, 0))
    fx(False)
    return stats(NAME)
