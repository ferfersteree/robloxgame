from gymlib import *

BG = '#16407a'
NAME = 'DB_10_Frost'

BODY = [(0.86, 0), (0.86, 0.5), (0.96, 0.68), (1.4, 0.74), (1.8, 0.68), (2.02, 0.52), (2.02, 0)]


def body_r(x):
    for (a, r), (b, q) in zip(BODY, BODY[1:]):
        if b > a and a <= x <= b:
            return r + (q - r) * (x - a) / (b - a)
    return 0.5


def mats():
    return dict(
        ice=toon('frost_ice', '#a6e0f7', shade='#5da4dc', light='#effcff', spec=1.0, rim=0.9, emit=0.1),
        ice2=toon('frost_ice2', '#d6f3ff', shade='#8cc4ec', light='#ffffff', spec=1.0, rim=0.9, emit=0.1),
        snow=toon('frost_snow', '#ffffff', shade='#aebfe6', light='#ffffff', spec=0.3),
        silver=toon('frost_silver', '#e4eefc', shade='#7f94cf', light='#ffffff', spec=1.0),
        deep=toon('frost_deep', '#2c68c8', shade='#143a86', light='#6fa8ff', spec=0.8),
        sapph=toon('frost_gem', '#4fd2ff', shade='#1b7fc4', light='#c9f4ff', spec=1.0, rim=1.0, emit=0.4),
        glow=glow('frost_glow', '#9deaff', 2.2),
    )


def build():
    begin(NAME, ol=0.03)
    M = mats()
    ice, ice2, snow, silver, deep, sapph = (M[k] for k in ('ice', 'ice2', 'snow', 'silver', 'deep', 'sapph'))

    cyl('handle', 0.15, 1.3, deep, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.45, 0.45, 4, silver, segs=5, steps=10, ol=0.012)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        rnd = random.Random(100 + (3 if s > 0 else 0))
        torus('grip_end_' + n, 0.17, 0.04, silver, 12, 6, loc=(s * 0.54, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.26), (0.66, 0.3), (0.8, 0.44), (0.86, 0.4), (0.86, 0)], silver, 12, scale=(s, 1, 1))
        for k in range(3):
            ang = k * 120 + 30
            sphere('collar_gem_%s%d' % (n, k), 0.07, sapph, 8, 5, loc=Vector((s * 0.76, 0, 0)) + radial(s, 90, ang) * 0.45, ol=0.015)
        # hexagonal ice block
        lathe('ice_' + n, BODY, ice, 6, scale=(s, 1, 1), smooth=False)
        lathe('ice_plate_' + n, [(-0.15, 0.75), (-0.1, 0.83), (0.1, 0.83), (0.15, 0.75)], ice2, 6, loc=(s * 1.45, 0, 0), caps=False, smooth=False)
        for j, x in enumerate((1.15, 1.75)):
            r = body_r(x) + 0.01
            lathe('band_%s%d' % (n, j), [(-0.07, r), (-0.05, r + 0.1), (0.05, r + 0.1), (0.07, r)], silver, 6,
                  loc=(s * x, 0, 0), caps=False, ol=0.025)
        # snowflake spike plate behind the block
        star('flake_plate_' + n, 0.95, 0.5, 6, 0.1, ice2, loc=(s * 0.92, 0, 0), rot=(0, 90, 0))
        # snow caps
        for j, (x, r) in enumerate(((1.05, 0.36), (1.45, 0.42), (1.85, 0.34))):
            rock('snow_%s%d' % (n, j), r, snow, seed=j + 4 * (s > 0), sub=1, loc=(s * min(x, 1.66), 0, 0.7), scale=(0.95, 1.0, 0.38))
        # hanging icicles
        for j, (x, y, h) in enumerate(((1.0, 0.25, 0.4), (1.25, -0.3, 0.55), (1.5, 0.2, 0.5), (1.7, -0.15, 0.42), (1.9, 0.12, 0.3), (1.4, 0.0, 0.3))):
            z = -0.6 if x < 1.8 else -0.5
            cone('icicle_%s%d' % (n, j), 0.1 if h > 0.35 else 0.08, h, ice2, 6, loc=(s * x, y, z), rot=(180, 0, 0), ol=0.02)
        # crystal spikes
        for j in range(3):
            ang = (60, 120, 270)[j] + rnd.uniform(-10, 10)
            base = Vector((s * (1.2 + 0.3 * j), 0, 0)) + radial(s, 90, ang) * 0.55
            crystal('spike_%s%d' % (n, j), 0.13, 0.5 + 0.1 * (j == 0), ice2, sides=6, tip=0.4, loc=base, rot=aim(radial(s, 55, ang)), ol=0.02)
        # six-armed snowflake emblem on the end
        xe = s * 2.07
        for j, a in enumerate((0, 60, 120)):
            box('emblem_arm_%s%d' % (n, j), (0.07, 1.1, 0.1), silver, bev=0.02, bsegs=1, loc=(xe, 0, 0), rot=(a, 0, 0), ol=0.02)
        torus('emblem_ring_' + n, 0.3, 0.03, deep, 12, 5, loc=(xe, 0, 0), ol=0.015)
        sphere('emblem_gem_' + n, 0.12, sapph, 8, 5, loc=(xe, 0, 0), scale=(0.5, 1, 1), ol=0.015)

    # ---------------- FX
    fx(True)
    rnd = random.Random(10)
    mist = ghost('frost_mist', '#d9efff', 1.0, 0.1)
    aura = ghost('frost_aura', '#7fd0ff', 1.2, 0.08)
    flake = glow('frost_flake', '#dff6ff', 2.4)
    spk = glow('frost_spark', '#ffffff', 2.5)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_mist_a_' + n, 1.3, mist, 14, 8, loc=(s * 1.4, 0, -0.65), scale=(1.5, 1.2, 0.35))
        sphere('fx_mist_b_' + n, 1.0, mist, 12, 8, loc=(s * 0.9, 0.4, -0.85), scale=(1.4, 1.1, 0.3))
        sphere('fx_aura_' + n, 1.7, aura, 16, 10, loc=(s * 1.45, 0, 0.1))
    for i in range(10):
        s = -1 if i % 2 else 1
        star('fx_flake_%d' % i, rnd.uniform(0.14, 0.26), 0.06, 6, 0.02, flake,
             loc=(s * rnd.uniform(0.8, 2.5), rnd.uniform(-1.3, 1.0), rnd.uniform(-0.6, 1.8)), rot=(90, 0, rnd.uniform(0, 60)))
    for i in range(6):
        s = -1 if i % 2 else 1
        star('fx_sparkle_%d' % i, rnd.uniform(0.1, 0.17), 0.03, 4, 0.02, spk,
             loc=(s * rnd.uniform(0.9, 2.5), -rnd.uniform(1.0, 1.4), rnd.uniform(-0.6, 1.8)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    return stats(NAME)
