from gymlib import *

BG = '#3a1410'
NAME = 'DB_11_Magma'


def mats():
    return dict(
        basalt=toon('mag_basalt', '#2a2527', shade='#0f0b0e', light='#5c4f55', spec=0.4),
        basalt2=toon('mag_basalt2', '#4a3a38', shade='#1b1214', light='#85706a', spec=0.4),
        iron=toon('mag_iron', '#3a3438', shade='#15111a', light='#7a6e74', spec=0.8),
        ember=toon('mag_ember', '#ff8a2a', shade='#b03a10', light='#ffd27a', spec=1.0, rim=1.0, emit=0.4),
        lava=glow('mag_lava', '#ff6a12', 2.6),
        hot=glow('mag_hot', '#ffb43a', 2.8),
        wrap=toon('mag_wrap', '#2c1a1c', shade='#120a0c', light='#5c3a3a', spec=0.2),
    )


def build():
    begin(NAME, ol=0.03)
    M = mats()
    basalt, basalt2, iron, ember, lava, hot, wrap = (M[k] for k in ('basalt', 'basalt2', 'iron', 'ember', 'lava', 'hot', 'wrap'))

    cyl('handle', 0.15, 1.3, wrap, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.45, 0.45, 4, iron, segs=5, steps=10, ol=0.012)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        rnd = random.Random(110 + (5 if s > 0 else 0))
        torus('grip_end_' + n, 0.17, 0.04, iron, 12, 6, loc=(s * 0.54, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.26), (0.66, 0.3), (0.8, 0.44), (0.86, 0.4), (0.86, 0)], iron, 10, scale=(s, 1, 1))
        torus('lava_ring_' + n, 0.46, 0.03, lava, 12, 4, loc=(s * 0.8, 0, 0), ol=0)
        # glowing lava core visible between the plates
        sphere('core_' + n, 0.55, lava, 10, 6, loc=(s * 1.45, 0, 0), scale=(1.4, 1, 1))
        # basalt plates in two staggered rings
        for k in range(5):
            for ring, (x, off) in enumerate(((1.05, 10), (1.72, 46))):
                a = 72 * k + off
                r = 0.68 + rnd.uniform(-0.02, 0.04)
                ar = math.radians(a)
                box('plate_%s%d%d' % (n, ring, k), (0.56 + rnd.uniform(-0.04, 0.06), 0.6, 0.16), basalt if (k + ring) % 2 else basalt2,
                    bev=0.05, bsegs=1, loc=(s * x, r * math.cos(ar), r * math.sin(ar)), rot=(a - 90, 0, 0))
        # glowing crack strips in the gaps
        for k in range(4):
            a = 72 * k + 46
            ar = math.radians(a)
            box('crack_%s%d' % (n, k), (0.56, 0.07, 0.05), hot, bev=0, loc=(s * 1.05, 0.66 * math.cos(ar), 0.66 * math.sin(ar)), rot=(a - 90, 0, 0), ol=0)
        # charred band and cap
        lathe('band_' + n, [(-0.06, 0.74), (-0.04, 0.84), (0.04, 0.84), (0.06, 0.74)], iron, 10, loc=(s * 1.39, 0, 0), caps=False, ol=0.025)
        lathe('cap_' + n, [(1.98, 0), (1.98, 0.55), (2.08, 0.62), (2.18, 0.5), (2.225, 0.3), (2.225, 0)], iron, 10, scale=(s, 1, 1))
        # volcano vents on top
        for j, x in enumerate((1.05, 1.75)):
            cone('vent_%s%d' % (n, j), 0.3, 0.35, basalt, 8, r2=0.13, loc=(s * x, 0, 0.7))
            sphere('vent_glow_%s%d' % (n, j), 0.14, lava, 8, 4, loc=(s * x, 0, 1.04), scale=(1, 1, 0.4), ol=0)
        # flame-shaped horns
        for side in (-1, 1):
            flame('horn_%s%d' % (n, side), 0.9, 0.2, basalt, bend=0.15, segs=8, loc=(s * 1.4, side * 0.45, 0.5), rot=(-side * 25, 0, 0))
        # broken chunks
        rock('chunk_a_' + n, 0.3, basalt2, seed=2, sub=1, flat=True, loc=(s * 0.95, -0.5, 0.55), scale=(1.2, 0.9, 0.8))
        rock('chunk_b_' + n, 0.28, basalt2, seed=6, sub=1, flat=True, loc=(s * 1.9, 0.5, -0.55), scale=(1.1, 0.9, 0.8))
        # lava drips
        for j, (x, y) in enumerate(((1.0, 0.15), (1.7, -0.2), (1.35, 0.1))):
            lathe('drip_%s%d' % (n, j), [(0, 0), (0, 0.08), (-0.2, 0.05), (-0.36, 0.1), (-0.46, 0)], lava, 6, 'Z', loc=(s * x, y, -0.6), ol=0)

    # ---------------- FX
    fx(True)
    rnd = random.Random(11)
    fl_o = glow('mag_flame_o', '#ff6a1a', 2.0)
    fl_y = glow('mag_flame_y', '#ffe66b', 2.4)
    fl_r = glow('mag_flame_r', '#ff2a2a', 1.8)
    emb = glow('mag_ember_fx', '#ffb347', 3.0)
    aura = ghost('mag_aura', '#ff6a1a', 1.2, 0.1)
    smoke = ghost('mag_smoke', '#2a2024', 0.6, 0.12)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_aura_' + n, 1.7, aura, 16, 10, loc=(s * 1.45, 0, 0.1))
        for k in range(7):
            x = s * rnd.uniform(0.95, 2.0)
            y = rnd.uniform(-0.35, 0.35)
            h = rnd.uniform(0.55, 1.0)
            z = 0.72 + rnd.uniform(0, 0.15)
            rz = rnd.uniform(0, 360)
            flame('fx_flame_%s%d' % (n, k), h, 0.18, fl_r if k % 3 == 0 else fl_o, bend=0.18, loc=(x, y, z), rot=(0, 0, rz))
            flame('fx_flame_in_%s%d' % (n, k), h * 0.55, 0.1, fl_y, bend=0.15, loc=(x, y, z + 0.03), rot=(0, 0, rz))
    for i, (x, z) in enumerate(((-1.6, 1.6), (1.6, 1.7), (0.0, 1.5))):
        sphere('fx_smoke_%d' % i, 0.7, smoke, 12, 8, loc=(x, 0, z), scale=(1.2, 1.0, 0.9))
    for i in range(12):
        s = -1 if i % 2 else 1
        sphere('fx_ember_%d' % i, rnd.uniform(0.03, 0.06), emb, 6, 4,
               loc=(s * rnd.uniform(0.7, 2.4), rnd.uniform(-1.2, 1.0), rnd.uniform(0.2, 1.9)))
    fx(False)
    return stats(NAME)
