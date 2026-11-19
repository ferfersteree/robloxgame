from gymlib import *
import db_09

NAME = 'ST_09_Obsidian'
T = 1.3


def build():
    begin(NAME, ol=0.04)
    M = db_09.mats()
    glass, glass2, silver, gem, crack, core = (M[k] for k in ('glass', 'glass2', 'silver', 'gem', 'crack', 'core'))
    stone = toon('obs_stone', '#2b2a36', shade='#0f0e16', light='#575470', spec=0.3)
    s = stats(db_09.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    rnd = random.Random(9)

    # ---- base: plinth, altar, deck
    box('plinth', (10.0, 3.0, 0.3), stone, bev=0.06, loc=(0, 0, 0.15))
    box('altar', (9.4, 2.6, 0.8), glass2, bev=0.08, loc=(0, 0, 0.7))
    box('deck', (9.8, 2.9, 0.2), stone, bev=0.05, loc=(0, 0, 1.2))
    box('deck_trim', (9.9, 0.08, 0.1), silver, bev=0.02, bsegs=1, loc=(0, -1.46, 1.22), ol=0.025)
    box('deck_glow', (9.0, 0.04, 0.05), crack, bev=0, loc=(0, -1.48, 1.08), ol=0)
    for i, x in enumerate((-4.3, -3.8, -3.3, 3.3, 3.8, 4.3)):
        box('altar_rune_%d' % i, (0.06, 0.04, 0.5 - 0.12 * (i % 2)), crack, bev=0, loc=(x, -1.31, 0.7), ol=0)
    # ---- sign on altar front
    box('sign_plaque', (5.2, 0.12, 0.76), silver, bev=0.05, loc=(0, -1.3, 0.7))
    box('sign_panel', (4.9, 0.1, 0.64), glass, bev=0.04, bsegs=1, loc=(0, -1.37, 0.7), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, core, loc=(0, -1.42, 0.7), rot=(90, 0, 0))
    for sx in (-1, 1):
        sphere('sign_gem_%s' % ('L' if sx < 0 else 'R'), 0.11, gem, 8, 5, loc=(sx * 2.45, -1.4, 0.7), ol=0.02)

    # ---- cradles (forks of black glass with silver caps)
    topc = hz - 0.15
    for sx in (-1, 1):
        for dx in (-0.42, 0.42):
            x = sx * cx + dx
            n = '%s%s' % ('L' if sx < 0 else 'R', 'a' if dx < 0 else 'b')
            ph = topc - 0.3 - T
            box('post_' + n, (0.3, 0.5, ph), glass2, bev=0.05, bsegs=1, loc=(x, 0, T + ph / 2))
            box('cap_' + n, (0.34, 0.8, 0.12), silver, bev=0.03, bsegs=1, loc=(x, 0, topc - 0.24), ol=0.025)
            for sy in (-1, 1):
                crystal('prong_%s%d' % (n, sy), 0.07, 0.5, glass, sides=4, tip=0.4, loc=(x, sy * 0.27, topc - 0.2), ol=0.02)

    # ---- jagged spires
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        crystal('spire_back_' + n, 0.42, 4.2, glass, sides=5, tip=0.35, base=1.0, loc=(sx * 4.8, 0.9, 1.2), scale=(1, 0.7, 1))
        crystal('spire_mid_' + n, 0.3, 3.4, glass2, sides=5, tip=0.4, base=1.0, loc=(sx * 4.2, 1.2, 1.3), rot=(rnd.uniform(-6, 6), sx * 8, 0), scale=(1, 0.7, 1))
        crystal('spire_front_' + n, 0.32, 2.6, glass, sides=5, tip=0.4, base=1.0, loc=(sx * 4.85, -0.5, 1.3), rot=(0, sx * -6, 0), scale=(1, 0.8, 1))
        pts = [(sx * 4.8 + rnd.uniform(-0.1, 0.1), 0.6, 1.5 + i * 0.5) for i in range(5)]
        tube('spire_crack_' + n, pts, [0.0, 0.03, 0.035, 0.03, 0.0], crack, segs=4)
        # braziers with violet crystal flames
        lathe('brazier_' + n, [(0, 0), (0, 0.16), (0.1, 0.12), (0.26, 0.3), (0.34, 0.34), (0.34, 0.28), (0.26, 0.2), (0.26, 0)],
              silver, 10, 'Z', loc=(sx * 4.6, -1.05, T), ol=0.03)
        for k in range(3):
            crystal('torch_%s%d' % (n, k), 0.09, 0.55, crack, sides=4, tip=0.4,
                    loc=(sx * 4.6 + (k - 1) * 0.1, -1.05 + (k % 2) * 0.08, T + 0.3), rot=(10 * (k - 1), 12 * (1 - k), 0), ol=0)
        crystal('deck_shard_%s' % n, 0.14, 0.8, glass2, sides=5, tip=0.4, loc=(sx * 4.3, 1.15, T), rot=(rnd.uniform(-10, 10), sx * 12, 0))

    # ---- violet rift arch behind the pair
    R = 3.4
    C = (0, 1.25, 1.3)
    ap = arc_pts(C, R, 8, 172, 16, 'XZ')
    rad = [0.05 + 0.21 * math.sin(math.pi * i / 16) ** 0.5 for i in range(17)]
    tube('rift_arch', ap, rad, glass, segs=6)
    tube('rift_glow', arc_pts((0, 0.98, 1.3), R, 15, 165, 14, 'XZ'), 0.05, crack, segs=4)
    tube('rift_glow_in_a', arc_pts((0, 0.98, 1.3), 2.9, 30, 80, 6, 'XZ'), 0.035, crack, segs=4)
    tube('rift_glow_in_b', arc_pts((0, 0.98, 1.3), 2.9, 100, 150, 6, 'XZ'), 0.035, crack, segs=4)
    for k in range(9):
        a = math.radians(20 + 17.5 * k)
        d = Vector((math.cos(a), 0, math.sin(a)))
        h = min(rnd.uniform(0.5, 1.0), 5.35 - 1.3 - R * math.sin(a))
        crystal('rift_shard_%d' % k, 0.14, h, glass if k % 2 else glass2, sides=4, tip=0.45,
                loc=Vector(C) + d * R, rot=aim(d), scale=(1, 0.5, 1))
    crystal('rift_gem', 0.2, 0.7, gem, sides=6, tip=0.35, both=True, loc=(0, 1.0, 1.3 + R))
    for sx in (-1, 1):
        box('rift_foot_%s' % ('L' if sx < 0 else 'R'), (0.75, 0.75, 0.9), glass2, bev=0.06, bsegs=1, loc=(sx * 3.37, 1.25, 1.75))

    fx(True)
    haze = ghost('obs_haze', '#6a2fa8', 1.0, 0.12)
    haze2 = ghost('obs_haze_dark', '#2a1646', 0.8, 0.12)
    spk = glow('obs_spark', '#d9b8ff', 2.5)
    bolt_m = glow('obs_bolt', '#c58bff', 3.0)
    sphere('fx_haze_a', 3.2, haze, 16, 9, loc=(0, 1.1, 3.4), scale=(1.5, 0.5, 0.85))
    sphere('fx_haze_b', 2.2, haze2, 16, 9, loc=(-2.5, 0.3, 1.9), scale=(1.5, 0.8, 0.5))
    sphere('fx_haze_c', 2.2, haze2, 16, 9, loc=(2.5, 0.3, 1.9), scale=(1.5, 0.8, 0.5))
    for sx in (-1, 1):
        bolt('fx_bolt_%s' % ('L' if sx < 0 else 'R'), (sx * 4.8, 0.6, 4.3), (sx * 3.2, 1.0, 4.2), bolt_m, r=0.04, n=6, amp=0.22, seed=20 + sx)
    for i in range(8):
        sx = -1 if i % 2 else 1
        crystal('fx_shard_%d' % i, rnd.uniform(0.08, 0.14), rnd.uniform(0.4, 0.7), glass, sides=4, tip=0.4, both=True,
                loc=(sx * rnd.uniform(1.0, 5.0), rnd.uniform(-0.8, 1.2), rnd.uniform(4.3, 5.1) if i % 2 else rnd.uniform(2.9, 3.6)),
                rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
    for i in range(8):
        star('fx_sparkle_%d' % i, rnd.uniform(0.12, 0.2), 0.03, 4, 0.02, spk,
             loc=(rnd.uniform(-5.0, 5.0), -rnd.uniform(1.2, 1.55), rnd.uniform(1.8, 5.0)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)

    display(NAME, db_09.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
