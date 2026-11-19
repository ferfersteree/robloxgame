from gymlib import *

BG = '#3a3448'
NAME = 'DB_09_Obsidian'

# faceted obsidian mass profile (axial from grip centre, radius)
BODY = [(0.86, 0), (0.86, 0.46), (0.96, 0.64), (1.25, 0.7), (1.5, 0.62), (1.62, 0.4), (1.66, 0)]


def body_r(x):
    for (a, r), (b, q) in zip(BODY, BODY[1:]):
        if b > a and a <= x <= b:
            return r + (q - r) * (x - a) / (b - a)
    return 0.5


def mats():
    return dict(
        glass=toon('obs_glass', '#17141f', shade='#06050a', light='#5a4f80', spec=1.0, rim=1.0, rimcol='#b79cff'),
        glass2=toon('obs_glass2', '#2b2339', shade='#0b0911', light='#7a6aa8', spec=1.0, rim=1.0, rimcol='#b79cff'),
        silver=toon('obs_dsilver', '#8d90a3', shade='#2f3144', light='#d9dcf0', spec=1.0),
        gem=toon('obs_gem', '#a55cff', shade='#4a1a9c', light='#e6c9ff', spec=1.0, rim=1.0, emit=0.4),
        crack=glow('obs_crack', '#a45cff', 2.6),
        core=glow('obs_core', '#c689ff', 3.0),
        wrap=toon('obs_wrap', '#241d33', shade='#0d0a14', light='#4d4268', spec=0.3),
    )


def build():
    begin(NAME, ol=0.03)
    M = mats()
    glass, glass2, silver, gem, crack, core, wrap = (M[k] for k in ('glass', 'glass2', 'silver', 'gem', 'crack', 'core', 'wrap'))

    cyl('handle', 0.15, 1.3, wrap, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.45, 0.45, 4, silver, segs=5, steps=10, ol=0.012)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        rnd = random.Random(90 + (7 if s > 0 else 0))
        torus('grip_end_' + n, 0.17, 0.04, silver, 12, 6, loc=(s * 0.54, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.26), (0.66, 0.3), (0.8, 0.44), (0.86, 0.4), (0.86, 0)], silver, 8, scale=(s, 1, 1))
        lathe('body_' + n, BODY, glass, 8, scale=(s, 1, 1), smooth=False)
        for j, x in enumerate((1.05, 1.45)):
            r = body_r(x) + 0.01
            lathe('band_%s%d' % (n, j), [(-0.06, r), (-0.04, r + 0.1), (0.04, r + 0.1), (0.06, r)], silver, 8,
                  loc=(s * x, 0, 0), caps=False, ol=0.025)
        # jagged blade-like shards fused into the mass (asymmetric)
        for k in range(8):
            ang = k * 45 + rnd.uniform(-12, 12)
            tilt = rnd.uniform(45, 85)
            x = rnd.uniform(1.0, 1.5)
            h = rnd.uniform(0.6, 0.95)
            if k == 2:
                h = 1.15
            if k >= 5:
                h = min(h, 0.7)
            c = math.cos(math.radians(tilt))
            if c > 0.05:
                h = min(h, (2.0 - x) / c)
            d = radial(s, tilt, ang)
            base = Vector((s * x, 0, 0)) + radial(s, 90, ang) * 0.4
            crystal('blade_%s%d' % (n, k), 0.17, h, glass if k % 2 == 0 else glass2, sides=5, tip=0.45, base=0.8,
                    loc=base, rot=aim(d, rnd.uniform(0, 90)), scale=(1, 0.45, 1))
        # small shard cluster near the gem
        for k in range(5):
            ang = k * 72 + 20
            base = Vector((s * 1.45, 0, 0)) + radial(s, 90, ang) * 0.58
            crystal('shard_%s%d' % (n, k), 0.08, 0.35, glass2, sides=4, tip=0.4, loc=base, rot=aim(radial(s, 25, ang)), ol=0.02)
        rock('chunk_a_' + n, 0.3, glass2, seed=3 + k, sub=1, flat=True, loc=(s * 1.1, 0.35, 0.55), scale=(1.2, 0.9, 0.8))
        rock('chunk_b_' + n, 0.28, glass2, seed=5, sub=1, flat=True, loc=(s * 1.55, -0.4, -0.5), scale=(1.1, 0.9, 0.8))
        # violet cracks running over the glass
        for k in range(6):
            a0 = k * 60 + rnd.uniform(-10, 10)
            x0 = rnd.uniform(0.98, 1.2)
            pts = []
            for i in range(5):
                x = x0 + i * 0.13
                a = math.radians(a0 + rnd.uniform(-14, 14) * i)
                rr = body_r(x) * 0.96
                pts.append((s * x, rr * math.cos(a), rr * math.sin(a)))
            tube('crack_%s%d' % (n, k), pts, [0.0, 0.022, 0.028, 0.02, 0.0], crack, segs=4)
        # core gem + silver claws
        crystal('core_gem_' + n, 0.24, 0.6, gem, sides=6, tip=0.35, both=True, loc=(s * 1.75, 0, 0), rot=aim((s, 0, 0)))
        for k in range(4):
            ang = k * 90 + 45
            base = Vector((s * 1.58, 0, 0)) + radial(s, 90, ang) * 0.4
            d = Vector((s * 0.85, 0, 0)) - radial(s, 90, ang) * 0.25
            crystal('claw_%s%d' % (n, k), 0.05, 0.4, silver, sides=4, tip=0.5, loc=base, rot=aim(d), ol=0.015)

    # ---------------- FX
    fx(True)
    rnd = random.Random(9)
    haze = ghost('obs_haze', '#6a2fa8', 1.0, 0.12)
    haze2 = ghost('obs_haze_dark', '#2a1646', 0.8, 0.12)
    spk = glow('obs_spark', '#d9b8ff', 2.5)
    bolt_m = glow('obs_bolt', '#c58bff', 3.0)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_haze_a_' + n, 1.5, haze, 14, 8, loc=(s * 1.3, 0, 0.1), scale=(1.3, 0.9, 0.8))
        sphere('fx_haze_b_' + n, 1.0, haze2, 12, 8, loc=(s * 1.9, 0.2, -0.3), scale=(1.0, 1.0, 0.9))
        bolt('fx_bolt_' + n, (s * 1.0, -0.6, 0.8), (s * 1.9, 0.7, -0.5), bolt_m, r=0.03, n=6, amp=0.16, seed=9 + s)
    for i in range(8):
        s = -1 if i % 2 else 1
        crystal('fx_shard_%d' % i, rnd.uniform(0.06, 0.1), rnd.uniform(0.3, 0.5), glass, sides=4, tip=0.4, both=True,
                loc=(s * rnd.uniform(0.9, 2.2), rnd.uniform(-1.1, 1.1), rnd.uniform(0.9, 1.8) if i % 3 else rnd.uniform(-1.0, -0.6)),
                rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
    for i in range(8):
        s = -1 if i % 2 else 1
        star('fx_sparkle_%d' % i, rnd.uniform(0.1, 0.17), 0.03, 4, 0.02, spk,
             loc=(s * rnd.uniform(0.9, 2.1), -rnd.uniform(1.0, 1.4), rnd.uniform(-0.8, 1.7)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    return stats(NAME)
