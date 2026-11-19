from gymlib import *
import db_10

NAME = 'ST_10_Frost'
T = 1.3


def build():
    begin(NAME, ol=0.04)
    M = db_10.mats()
    ice, ice2, snow, silver, deep, sapph, gl = (M[k] for k in ('ice', 'ice2', 'snow', 'silver', 'deep', 'sapph', 'glow'))
    slate = toon('frost_slate', '#35466e', shade='#18223f', light='#6d86bd', spec=0.3)
    slate2 = toon('frost_slate2', '#4a5f90', shade='#222f58', light='#8aa2d6', spec=0.4)
    s = stats(db_10.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    rnd = random.Random(10)

    # ---- base
    box('plinth', (10.0, 3.0, 0.3), slate, bev=0.06, loc=(0, 0, 0.15))
    box('altar', (9.4, 2.6, 0.8), slate2, bev=0.08, loc=(0, 0, 0.7))
    box('deck', (9.8, 2.9, 0.2), ice2, bev=0.05, loc=(0, 0, 1.2))
    box('deck_trim', (9.9, 0.08, 0.1), silver, bev=0.02, bsegs=1, loc=(0, -1.46, 1.22), ol=0.025)
    box('deck_glow', (9.0, 0.04, 0.05), gl, bev=0, loc=(0, -1.48, 1.08), ol=0)
    for i, x in enumerate((-4.3, -3.8, -3.3, 3.3, 3.8, 4.3)):
        box('altar_rune_%d' % i, (0.06, 0.04, 0.5 - 0.12 * (i % 2)), gl, bev=0, loc=(x, -1.31, 0.7), ol=0)
    # ---- sign
    box('sign_plaque', (5.2, 0.12, 0.76), silver, bev=0.05, loc=(0, -1.3, 0.7))
    box('sign_panel', (4.9, 0.1, 0.64), deep, bev=0.04, bsegs=1, loc=(0, -1.37, 0.7), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, snow, loc=(0, -1.42, 0.7), rot=(90, 0, 0))
    for sx in (-1, 1):
        sphere('sign_gem_%s' % ('L' if sx < 0 else 'R'), 0.11, sapph, 8, 5, loc=(sx * 2.45, -1.4, 0.7), ol=0.02)
    # ---- front icicles under the deck lip (outside the sign span)
    for i, x in enumerate((-4.6, -4.2, -3.8, -3.4, -3.0, 3.0, 3.4, 3.8, 4.2, 4.6)):
        cone('lip_icicle_%d' % i, 0.09, 0.3 + 0.12 * (i % 3), ice2, 6, loc=(x, -1.4, 1.1), rot=(180, 0, 0), ol=0.02)

    # ---- cradles: ice forks on silver caps
    topc = hz - 0.15
    for sx in (-1, 1):
        for dx in (-0.42, 0.42):
            x = sx * cx + dx
            n = '%s%s' % ('L' if sx < 0 else 'R', 'a' if dx < 0 else 'b')
            ph = topc - 0.3 - T
            box('post_' + n, (0.3, 0.5, ph), ice, bev=0.05, bsegs=1, loc=(x, 0, T + ph / 2))
            box('cap_' + n, (0.34, 0.8, 0.12), silver, bev=0.03, bsegs=1, loc=(x, 0, topc - 0.24), ol=0.025)
            for sy in (-1, 1):
                crystal('prong_%s%d' % (n, sy), 0.07, 0.5, ice2, sides=4, tip=0.4, loc=(x, sy * 0.27, topc - 0.2), ol=0.02)

    # ---- igloo / ice throne arch behind the pair
    R = 3.4
    C = (0, 1.2, 1.3)
    for k in range(10):
        a = 9 + 18 * k
        ar = math.radians(a)
        p = (R * math.cos(ar), C[1], C[2] + R * math.sin(ar))
        box('arch_block_%d' % k, (1.1, 0.6, 0.5), ice if k % 2 else ice2, bev=0.07, bsegs=1, loc=p, rot=(0, -(a + 90), 0))
        if k in (1, 3, 5, 7, 8):
            rock('arch_snow_%d' % k, 0.34, snow, seed=k, sub=1, loc=(p[0] + math.cos(ar) * 0.3, p[1], p[2] + math.sin(ar) * 0.3),
                 scale=(1.3, 1.0, 0.45), rot=(0, -(a + 90), 0))
    for k, a in enumerate((35, 55, 75, 90, 105, 125, 145)):
        ar = math.radians(a)
        r = R - 0.3
        cone('arch_icicle_%d' % k, 0.1, 0.45 + 0.15 * (k % 3), ice2, 6, loc=(r * math.cos(ar), C[1] - 0.1, C[2] + r * math.sin(ar)), rot=(180, 0, 0), ol=0.02)
    crystal('arch_crest', 0.22, 0.8, sapph, sides=6, tip=0.35, both=True, loc=(0, C[1] - 0.1, C[2] + R + 0.3))
    # glowing inlay ring inside the arch
    tube('arch_glow', arc_pts((0, C[1] - 0.33, C[2]), R, 12, 168, 14, 'XZ'), 0.04, gl, segs=4)

    # ---- spires, lanterns, snow drifts
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        crystal('spire_back_' + n, 0.4, 4.0, ice, sides=6, tip=0.35, base=1.0, loc=(sx * 4.8, 0.9, 1.2), rot=(0, sx * -4, 0))
        crystal('spire_mid_' + n, 0.28, 2.8, ice2, sides=6, tip=0.4, base=1.0, loc=(sx * 4.25, 1.15, 1.3), rot=(0, sx * 10, 0))
        crystal('spire_front_' + n, 0.26, 2.0, ice, sides=6, tip=0.4, base=1.0, loc=(sx * 4.85, -0.5, 1.3), rot=(0, sx * -6, 0))
        lathe('lantern_' + n, [(0, 0), (0, 0.16), (0.1, 0.12), (0.26, 0.3), (0.34, 0.34), (0.34, 0.28), (0.26, 0.2), (0.26, 0)],
              silver, 10, 'Z', loc=(sx * 4.6, -1.05, T), ol=0.03)
        for k in range(3):
            crystal('lantern_flame_%s%d' % (n, k), 0.09, 0.55, gl, sides=4, tip=0.4,
                    loc=(sx * 4.6 + (k - 1) * 0.1, -1.05 + (k % 2) * 0.08, T + 0.3), rot=(10 * (k - 1), 12 * (1 - k), 0), ol=0)
        for j, (x, y) in enumerate(((3.6, -0.95), (4.2, -0.9), (4.9, -1.0))):
            rock('drift_%s%d' % (n, j), 0.5, snow, seed=j + 2, sub=1, loc=(sx * x, y, 0.35), scale=(1.4, 0.8, 0.45))
        rock('deck_drift_' + n, 0.45, snow, seed=7, sub=1, loc=(sx * 4.3, 1.1, T + 0.05), scale=(1.5, 0.9, 0.4))

    fx(True)
    mist = ghost('frost_mist', '#d9efff', 1.0, 0.1)
    aura = ghost('frost_aura', '#7fd0ff', 1.2, 0.08)
    flake = glow('frost_flake', '#dff6ff', 2.4)
    spk = glow('frost_spark', '#ffffff', 2.5)
    sphere('fx_aura', 3.2, aura, 16, 9, loc=(0, 1.0, 3.4), scale=(1.5, 0.5, 0.85))
    for i, x in enumerate((-3.2, 0, 3.2)):
        sphere('fx_mist_%d' % i, 1.9, mist, 14, 8, loc=(x, 0.2, 1.5), scale=(1.8, 1.0, 0.3))
    for i in range(8):
        sx = -1 if i % 2 else 1
        crystal('fx_ice_%d' % i, rnd.uniform(0.08, 0.14), rnd.uniform(0.4, 0.7), ice2, sides=4, tip=0.4, both=True,
                loc=(sx * rnd.uniform(1.0, 5.0), rnd.uniform(-0.8, 1.2), rnd.uniform(4.3, 5.1) if i % 2 else rnd.uniform(2.9, 3.6)),
                rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
    for i in range(8):
        star('fx_flake_%d' % i, rnd.uniform(0.14, 0.26), 0.06, 6, 0.02, flake,
             loc=(rnd.uniform(-5.0, 5.0), -rnd.uniform(1.2, 1.55), rnd.uniform(1.8, 5.0)), rot=(90, 0, rnd.uniform(0, 60)))
    for i in range(6):
        star('fx_sparkle_%d' % i, rnd.uniform(0.1, 0.17), 0.03, 4, 0.02, spk,
             loc=(rnd.uniform(-5.0, 5.0), -rnd.uniform(1.2, 1.55), rnd.uniform(1.8, 5.0)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)

    display(NAME, db_10.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
