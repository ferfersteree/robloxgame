from gymlib import *

DROP = 1.5
SHELF = (1.3,)   # single deck (top surface) - the stand holds only the current pair


def build():
    begin('ST_01_Wooden', ol=0.04)
    wood = toon('wood', '#c07a3c', light='#e3a35c')
    wood2 = toon('wood_b', '#d18f4a', light='#f0b872')
    dark = toon('wood_dark', '#8b5229', light='#b3743f')
    bark = toon('bark', '#74482a', shade='#3d2320', light='#96633a', spec=0.2)
    cut = toon('wood_cut', '#f0cf93', light='#fff0c4', spec=0.3)
    rope = toon('rope', '#e2c07d', shade='#9a7340', light='#f7e2a8', spec=0.2)
    leafm = toon('leaf', '#62c53c', shade='#2c7a35', light='#a8e85a')
    stone = toon('stone_grey', '#a3a9b4', shade='#5c5f7c', light='#d5d9e0', spec=0.2)
    shroom = toon('shroom_cap', '#e8553a', light='#ff9a6a', spec=1.0)
    white = toon('cream', '#fff3d8', spec=0.2)
    rnd = random.Random(1)

    # shelves: side rails + planks
    for i, z in ((2, 2.8),):
        for sx in (-1, 1):
            tube('rail_%d%s' % (i, 'L' if sx < 0 else 'R'), [(sx * 4.5, -1.42, z - 0.25), (sx * 4.5, 1.42, z - 0.25)], 0.13, dark, segs=7)
        for j, y in enumerate((-0.88, 0.0, 0.88)):
            box('plank_%d%d' % (i, j), (rnd.uniform(9.4, 9.9), 0.8, 0.15), wood if (i + j) % 2 else wood2, bev=0.05,
                loc=(rnd.uniform(-0.08, 0.08), y, z - 0.075), rot=(0, 0, rnd.uniform(-0.5, 0.5)))
    # back X brace + top beam
    tube('beam', [(-5.0, 1.1, 5.3), (0, 1.1, 5.38), (5.0, 1.1, 5.25)], 0.17, bark, segs=8)
    for sx in (-1, 1):
        torus('beam_rope_' + ('L' if sx < 0 else 'R'), 0.2, 0.05, rope, 12, 5, loc=(sx * 4.42, 1.1, 5.3), ol=0.02)
        sphere('beam_cut_' + ('L' if sx < 0 else 'R'), 0.14, cut, 8, 4, loc=(sx * 5.0, 1.1, 5.3 if sx < 0 else 5.25), scale=(0.3, 1, 1), ol=0)
    # sign
    box('sign_plank_a', (5.5, 0.14, 0.52), dark, bev=0.05, loc=(0, 0.95, 4.76), rot=(0, 1.2, 0))
    box('sign_plank_b', (5.3, 0.14, 0.5), dark, bev=0.05, loc=(0.05, 0.95, 4.25), rot=(0, -0.8, 0))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        box('sign_cap_' + n, (0.2, 0.2, 1.2), bark, bev=0.05, loc=(sx * 2.62, 0.93, 4.5))
        tube('sign_rope_' + n, [(sx * 2.3, 1.08, 5.3), (sx * 2.3, 0.98, 5.0)], 0.045, rope, segs=5, ol=0.02)
        sphere('sign_nail_' + n, 0.07, stone, 6, 4, loc=(sx * 2.62, 0.82, 4.9), ol=0.015)
    text('sign_text', 'CAMP GYM', 0.62, 0.05, white, loc=(0, 0.86, 4.5), rot=(90, 0, 0))
    # cradles for the top pair (Y forks)
    for ci, cx in enumerate((-2.1, 2.1)):
        for fi, dx in enumerate((-0.4, 0.4)):
            x = cx + dx
            n = '%d%d' % (ci, fi)
            tube('fork_post_' + n, [(x, 0, 2.8), (x, 0, 3.32)], [0.1, 0.085], bark, segs=6, ol=0.025)
            for sy in (-1, 1):
                tube('fork_prong_%s%s' % (n, 'a' if sy < 0 else 'b'), [(x, 0, 3.28), (x, sy * 0.2, 3.5), (x, sy * 0.27, 3.72)], [0.075, 0.065, 0.05], bark, segs=6, ol=0.025)
            torus('fork_rope_' + n, 0.1, 0.035, rope, 8, 4, 'Z', loc=(x, 0, 3.26), ol=0.015)
    coil('vine', 0.25, 0.035, 3.1, 5.0, 4, leafm, segs=4, steps=10, axis='Z', loc=(-4.45, 1.1, 0), ol=0.015)
    for i, (z, a) in enumerate(((3.4, 200), (3.9, 300), (4.4, 220), (4.9, 330))):
        leaf('vine_leaf_%d' % i, 0.42, 0.22, leafm, loc=(-4.45 + 0.25 * math.cos(math.radians(a)), 1.1 + 0.25 * math.sin(math.radians(a)), z), rot=(60, -20, a), ol=0.025)
    for i, (x, a) in enumerate(((-1.2, 20), (0.6, -15), (3.3, 30))):
        leaf('beam_leaf_%d' % i, 0.4, 0.2, leafm, loc=(x, 0.95, 5.5), rot=(75, -30 + a, a * 3), ol=0.025)
    fx(True)
    sp = glow('spark_warm', '#fff2a8', 3.0)
    ff = glow('firefly', '#d6ff7a', 3.0)
    for i, p in enumerate(((-2.9, 0.7, 5.2), (3.05, 0.7, 4.1), (0.2, -1.2, 3.0))):
        star('fx_sparkle_%d' % i, 0.14, 0.035, 4, 0.02, sp, loc=p, rot=(90, 0, 15 * i))
    for i, p in enumerate(((-4.0, -1.0, 4.2), (4.2, -0.6, 3.8), (-1.5, 0.3, 5.9))):
        sphere('fx_firefly_%d' % i, 0.05, ff, 6, 4, loc=p)
    leaf('fx_leaf_a', 0.26, 0.14, leafm, loc=(-3.4, -0.8, 3.9), rot=(40, 20, 60))
    leaf('fx_leaf_b', 0.22, 0.12, leafm, loc=(2.2, -1.0, 5.3), rot=(-30, 40, 200))
    fx(False)

    drop(DROP)
    # posts
    posts = {'FL': (-4.55, -1.1, 1.6), 'FR': (4.55, -1.1, 1.55), 'BL': (-4.55, 1.1, 4.1), 'BR': (4.55, 1.1, 4.0)}
    for k, (x, y, h) in posts.items():
        lean = -0.12 if x > 0 else 0.12
        tube('post_' + k, [(x, y, 0), (x + lean * 0.4, y, h * 0.5), (x + lean, y, h)], [0.24, 0.22, 0.19], bark, segs=8)
        sphere('post_cut_' + k, 0.17, cut, 8, 4, loc=(x + lean, y, h), scale=(1, 1, 0.3), ol=0)
        rock('post_stone_' + k, 0.42, stone, seed=len(k) + x, sub=1, rough=0.15, loc=(x * 1.03, y * 1.15, 0.3), scale=(1, 1, 0.55))
        for i, z in enumerate((1.3,)):
            coil('lash_%s%d' % (k, i), 0.25, 0.05, z - 0.36, z - 0.14, 2.5, rope, segs=5, steps=10, axis='Z', loc=(x + lean * z / h, y, 0), ol=0.02)
    tube('brace_a', [(-4.5, 1.25, 0.25), (4.5, 1.25, 1.0)], 0.09, dark, segs=6)
    tube('brace_b', [(4.5, 1.25, 0.25), (-4.5, 1.25, 1.0)], 0.09, dark, segs=6)
    tube('front_rail', [(-4.6, -1.15, 0.45), (4.6, -1.15, 0.5)], 0.11, bark, segs=7)
    for i, (x, r_, h_) in enumerate(((-2.6, 0.38, 0.75), (-1.7, 0.3, 0.6), (2.3, 0.42, 0.8))):
        lathe('stump_%d' % i, [(0, 0), (0, r_ * 1.1), (h_ * 0.5, r_), (h_, r_ * 0.92), (h_, 0)], bark, 10, 'Z', loc=(x, 0.3, 0))
        sphere('stump_cut_%d' % i, r_ * 0.8, cut, 10, 4, loc=(x, 0.3, h_), scale=(1, 1, 0.12), ol=0)
    tube('spear_shaft', [(5.25, 0.75, 0.0), (5.05, 1.35, 3.6)], 0.06, wood2, segs=6, ol=0.025)
    crystal('spear_tip', 0.16, 0.55, stone, sides=4, tip=0.7, loc=(5.05, 1.35, 3.55), rot=aim((-0.2, 0.6, 3.6)), scale=(1, 0.45, 1), ol=0.025)
    coil('spear_bind', 0.075, 0.03, 3.4, 3.6, 2.5, rope, segs=4, steps=8, axis='Z', loc=(5.06, 1.33, 0), ol=0.012)
    for i, (x, y) in enumerate(((-5.1, 0.3), (5.15, -0.2), (-3.0, 1.55), (2.4, 1.6))):
        for j in range(3):
            leaf('grass_%d%d' % (i, j), rnd.uniform(0.45, 0.7), 0.16, leafm, loc=(x + j * 0.08, y, 0.0), rot=(90, -70 - j * 20, rnd.uniform(0, 360)), ol=0.02)
    for i, (x, y, k) in enumerate(((-5.15, -0.5, 1.0), (-5.3, -0.15, 0.7))):
        tube('shroom_stem_%d' % i, [(x, y, 0), (x, y, 0.3 * k)], [0.08 * k, 0.065 * k], white, segs=6, ol=0.02)
        lathe('shroom_cap_%d' % i, [(0.24 * k, 0.24 * k), (0.34 * k, 0.2 * k), (0.42 * k, 0.1 * k), (0.45 * k, 0)], shroom, 10, 'Z', loc=(x, y, 0), ol=0.025)


    display('ST_01_Wooden', 'DB_01_Wooden', [((-2.1, 0, 3.56 - DROP), (0, 0, 180)), ((2.1, 0, 3.56 - DROP), (0, 0, 0))], [], SHELF)
    return stats('ST_01_Wooden')
