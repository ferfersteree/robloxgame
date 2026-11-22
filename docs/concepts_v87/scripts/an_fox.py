from faunalib import *

ID, NAME, RARITY, BIOME = 'fox', 'Fox', 3, 1
KIND = 'ground'
METHOD, GESTURE = 'pounce', 'spin'          # прыгает в атаку / кружится (ловит хвост)
BUSH_D = 2.6
OPEN = 'Open_Burst'


def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    fur = studs('fx_fur', '#f57f1f')
    dk = studs('fx_dk', '#c8551a')
    white = studs('fx_white', '#fff6e8')
    black = studs('fx_black', '#3a2a2e')
    scarf = studs('fx_scarf', '#3fbe4a')
    scarf_dk = studs('fx_scarf_dk', '#2a8a34')
    scarf_lt = studs('fx_scarf_lt', '#b6f070')
    tooth = smooth('fx_bone', '#fffaf0', 0.3)
    nose = smooth('fx_nose', '#24161c', 0.15)
    pink = smooth('fx_pink', '#ff9db4', 0.35)
    seg('body', 'root', (0, 0.1, 0.85))
    blk('body', (0.9, 1.3, 0.72), fur, (0, 0.25, 0.85))
    blk('chest', (0.66, 0.14, 0.6), white, (0, -0.42, 0.82))
    for i, w in enumerate((0.5, 0.38, 0.26, 0.14)):
        pix('bib_%d' % i, (w, 0.04, 0.09), white, (0, -0.5 - i * 0.008, 0.98 - i * 0.1))
    blk('belly', (0.6, 1.0, 0.08), white, (0, 0.25, 0.47))
    pix('back_stripe', (0.2, 0.9, 0.03), dk, (0, 0.3, 1.225))
    for i, (x, y) in enumerate(((-0.28, 0.0), (0.28, 0.2), (-0.26, 0.5), (0.27, 0.7))):
        pix('back_spot_%d' % i, (0.14, 0.14, 0.03), dk, (x, y, 1.225))
    for sg, n in LR:
        pix('side_tuft_a' + n, (0.03, 0.3, 0.14), white, (sg * 0.465, -0.1, 0.6))
        pix('side_tuft_b' + n, (0.03, 0.18, 0.1), white, (sg * 0.465, 0.1, 0.54))
        pix('hip_' + n, (0.03, 0.26, 0.26), dk, (sg * 0.465, 0.65, 0.95))
    # accessory: leaf-green scarf with a bone charm (rarity 3)
    blk('scarf', (1.02, 0.66, 0.26), scarf, (0, -0.36, 1.1))
    blk('scarf_knot', (0.28, 0.16, 0.22), scarf_dk, (0.3, -0.72, 1.0), bev=0.03)
    blk('scarf_end_a', (0.2, 0.08, 0.4), scarf, (0.42, -0.73, 0.76), rot=(0, 12, 0), bev=0.03)
    blk('scarf_end_b', (0.18, 0.08, 0.3), scarf_dk, (0.22, -0.74, 0.8), rot=(0, -8, 0), bev=0.03)
    for sg, n in LR:
        for j in range(3):
            pix('scarf_dot_%s%d' % (n, j), (0.03, 0.09, 0.09), scarf_lt, (sg * 0.515, -0.56 + 0.2 * j, 1.1))
    pix('charm', (0.2, 0.05, 0.06), tooth, (-0.2, -0.7, 0.94))
    pix('charm_a', (0.07, 0.06, 0.1), tooth, (-0.3, -0.7, 0.94))
    pix('charm_b', (0.07, 0.06, 0.1), tooth, (-0.1, -0.7, 0.94))
    # ---- head: big cube
    seg('head', 'body', (0, -0.35, 1.15))
    blk('head', (1.16, 0.9, 0.92), fur, (0, -0.55, 1.6))
    blk('head_top', (0.8, 0.6, 0.08), fur, (0, -0.55, 2.08), bev=0.03)
    blk('snout', (0.46, 0.34, 0.3), white, (0, -1.12, 1.34))
    blk('snout_top', (0.3, 0.3, 0.08), fur, (0, -1.1, 1.52), bev=0.02)
    blk('nose', (0.16, 0.08, 0.11), nose, (0, -1.31, 1.44), bev=0.02, ol=0.01)
    pix('mouth_line', (0.03, 0.03, 0.08), nose, (0, -1.295, 1.34))
    pix('fore_mark_a', (0.14, 0.03, 0.2), white, (0, -1.005, 1.92))
    pix('fore_mark_b', (0.08, 0.03, 0.1), white, (0, -1.005, 1.78))
    for sg, n in LR:
        blk('cheek_' + n, (0.34, 0.3, 0.34), white, (sg * 0.5, -0.84, 1.34), bev=0.05)
        pix('cheek_tuft_a' + n, (0.12, 0.12, 0.12), white, (sg * 0.7, -0.8, 1.26))
        pix('cheek_tuft_b' + n, (0.1, 0.1, 0.1), white, (sg * 0.71, -0.78, 1.42))
        pix('cheek_tuft_c' + n, (0.08, 0.08, 0.08), white, (sg * 0.69, -0.76, 1.53))
        pix('mouth_' + n, (0.12, 0.03, 0.03), nose, (sg * 0.07, -1.295, 1.29))
        pix('fang_' + n, (0.05, 0.03, 0.07), tooth, (sg * 0.13, -1.295, 1.24))
        pix('blush_' + n, (0.16, 0.03, 0.08), pink, (sg * 0.5, -0.995, 1.4))
        for j, dz in enumerate((0.05, -0.04)):
            pix('whisker_%s%d' % (n, j), (0.2, 0.02, 0.02), black, (sg * 0.36, -1.2, 1.36 + dz), rot=(0, -sg * (12 if j == 0 else -12), sg * 25))
        pix('temple_' + n, (0.03, 0.24, 0.2), dk, (sg * 0.585, -0.3, 1.8))
    anime_eyes(0.32, 0.28, -1.005, 1.72, '#f2a81e', brow='#3a2a2e', brow_tilt=-6, brow_dz=0.15)
    for sg, n in LR:
        seg('ear_' + n, 'head', (sg * 0.36, -0.5, 2.05))
        blk('ear_base_' + n, (0.34, 0.16, 0.26), fur, (sg * 0.37, -0.5, 2.16))
        blk('ear_mid_' + n, (0.26, 0.15, 0.22), fur, (sg * 0.39, -0.5, 2.38))
        blk('ear_tip_' + n, (0.16, 0.14, 0.18), black, (sg * 0.41, -0.5, 2.56), bev=0.03)
        pix('ear_in_' + n, (0.2, 0.03, 0.2), white, (sg * 0.37, -0.585, 2.16))
        pix('ear_in_b' + n, (0.12, 0.03, 0.16), white, (sg * 0.39, -0.58, 2.36))
        pix('ear_tuft_' + n, (0.06, 0.05, 0.1), white, (sg * 0.26, -0.6, 2.1))
    for sg, n in LR:
        for fb, y in (('f', -0.22), ('b', 0.72)):
            seg('leg_%s%s' % (fb, n), 'body', (sg * 0.28, y, 0.6))
            blk('leg_%s%s' % (fb, n), (0.26, 0.28, 0.4), fur, (sg * 0.28, y, 0.44))
            blk('sock_%s%s' % (fb, n), (0.28, 0.3, 0.2), black, (sg * 0.28, y, 0.2))
            blk('paw_%s%s' % (fb, n), (0.3, 0.36, 0.12), black, (sg * 0.28, y - 0.04, 0.06), bev=0.03)
            for j in (-1, 0, 1):
                pix('toe_%s%s%d' % (fb, n, j + 1), (0.05, 0.04, 0.06), white, (sg * 0.28 + j * 0.09, y - 0.225, 0.05))
    # ---- big bushy tail with a white tip
    seg('tail', 'body', (0, 0.88, 1.0))
    blk('tail_a', (0.4, 0.46, 0.4), fur, (0, 1.08, 1.08))
    blk('tail_b', (0.6, 0.6, 0.6), fur, (0, 1.52, 1.3))
    blk('tail_c', (0.5, 0.4, 0.5), white, (0, 1.96, 1.5))
    blk('tail_tip', (0.26, 0.16, 0.26), white, (0, 2.2, 1.58), bev=0.04)
    pix('tail_ring', (0.56, 0.06, 0.56), dk, (0, 1.8, 1.42))
    for i, (x, y, z, m) in enumerate(((0.3, 1.5, 1.62, fur), (-0.32, 1.4, 1.1, fur), (0.1, 1.6, 0.98, fur),
                                       (0.26, 2.0, 1.74, white), (-0.24, 2.05, 1.3, white))):
        pix('tail_tuft_%d' % i, (0.14, 0.14, 0.14), m, (x, y, z))
    assemble()
    marker('Head', 'head', (0, -0.55, 1.6))
    marker('Chest', 'body', (0, -0.48, 0.85))
    marker('Hit', 'body', (0, 0.25, 1.2))
    anims()
    build_fx()
    return bake_actions()


def anims():
    # Reveal: crouches in the bush, pounces out in an arc (attack!), lands and spins round chasing its tail (42 frames)
    R = 'Reveal'
    clip(R, 42)
    k(R, 'root', 1, loc=(0, BUSH_D, -0.2))
    k(R, 'root', 6, loc=(0, BUSH_D + 0.2, -0.35))
    k(R, 'root', 12, loc=(0, BUSH_D * 0.45, 1.6))
    k(R, 'root', 18, loc=(0, 0, 0), ease='LINEAR')
    k(R, 'root', 20, loc=(0, 0, 0), rot=(0, 0, 0))
    k(R, 'root', 36, loc=(0, 0, 0), rot=(0, 0, 360))
    k(R, 'body', 1, rot=(0, 0, 0))
    k(R, 'body', 6, rot=(8, 0, 0), scale=(1.05, 1.05, 0.88))
    k(R, 'body', 12, rot=(-22, 0, 0), scale=(0.95, 1.1, 1.0))
    k(R, 'body', 18, rot=(10, 0, 0), scale=(1.1, 0.95, 0.85))
    k(R, 'body', 22, rot=(0, 0, 0), scale=1.0)
    for n in ('L', 'R'):
        k(R, 'leg_f' + n, 6, rot=(0, 0, 0))
        k(R, 'leg_f' + n, 12, rot=(70, 0, 0))
        k(R, 'leg_f' + n, 18, rot=(-15, 0, 0))
        k(R, 'leg_f' + n, 22, rot=(0, 0, 0))
        k(R, 'leg_b' + n, 6, rot=(0, 0, 0))
        k(R, 'leg_b' + n, 12, rot=(-60, 0, 0))
        k(R, 'leg_b' + n, 20, rot=(0, 0, 0))
        k(R, 'ear_' + n, 6, rot=(0, 0, 0))
        k(R, 'ear_' + n, 12, rot=(30, 0, 0))
        k(R, 'ear_' + n, 20, rot=(0, 0, 0))
    k(R, 'tail', 6, rot=(0, 0, 0))
    k(R, 'tail', 12, rot=(25, 0, 0))
    k(R, 'tail', 20, rot=(0, 0, 0))
    k(R, 'tail', 24, rot=(0, 0, 35))
    k(R, 'tail', 32, rot=(0, 0, 35))
    k(R, 'tail', 38, rot=(0, 0, 0))
    k(R, 'head', 20, rot=(0, 0, 0))
    k(R, 'head', 24, rot=(0, 0, 30))
    k(R, 'head', 32, rot=(0, 0, 30))
    k(R, 'head', 38, rot=(-10, 0, 0))
    k(R, 'head', 42, rot=(0, 0, 0))
    I = 'Idle'
    clip(I, 48)
    k(I, 'body', 1, scale=1.0)
    k(I, 'body', 24, scale=(1.02, 1.02, 1.03))
    k(I, 'body', 48, scale=1.0)
    for f, a in ((1, 0), (12, 14), (24, 0), (36, -14), (48, 0)):
        k(I, 'tail', f, rot=(0, 0, a))
    for f, a in ((1, 0), (30, 0), (33, -20), (36, 0), (48, 0)):
        k(I, 'ear_R', f, rot=(a, 0, 0))
    for f, a in ((1, 0), (16, 8), (32, 0), (48, 0)):
        k(I, 'head', f, rot=(0, a, 0))
    blink(I, (22,))
    blink(R, (40,))


def build_fx():
    fx(True)
    dust = ghost('fx_dust', '#f1e0bc', 1.1, 0.85, 1.2)
    leafm = studs('fx_leafbit', '#4fae35')
    rnd = random.Random(41)
    base = G.root.location
    for i in range(8):
        l_ = blk('leaf_bit_%d' % i, (0.24, 0.24, 0.05), leafm, (0, 0, 0), bev=0.02)
        p0 = base + Vector((rnd.uniform(-0.5, 0.5), BUSH_D, 1.6))
        p1 = p0 + Vector((rnd.uniform(-2, 2), rnd.uniform(-2.2, -0.4), rnd.uniform(0.4, 1.6)))
        fxkey(l_, 1, loc=p0, scale=0)
        fxkey(l_, 7, loc=p0, scale=1)
        fxkey(l_, 18, loc=p1, rot=(rnd.uniform(0, 360), 180, 90))
        fxkey(l_, 38, loc=(p1.x, p1.y, 0.05), rot=(rnd.uniform(0, 360), 360, 200), scale=0.8)
        fxkey(l_, 42, scale=0)
    # spin dust ring of cubes
    for i in range(8):
        a = math.radians(i * 45)
        p = blk('spin_dust_%d' % i, (0.32, 0.32, 0.32), dust, (0, 0, 0), bev=0.06)
        p0 = base + Vector((math.cos(a) * 0.8, math.sin(a) * 0.8, 0.15))
        p1 = base + Vector((math.cos(a + 1.2) * 1.6, math.sin(a + 1.2) * 1.6, 0.5))
        fxkey(p, 1, loc=p0, scale=0, alpha=1)
        fxkey(p, 20, loc=p0, scale=0.3, alpha=1)
        fxkey(p, 32, loc=p1, scale=1.3, alpha=0.6, rot=(30, 40, 0))
        fxkey(p, 42, loc=p1 + Vector((0, 0, 0.4)), scale=1.6, alpha=0)
    fx(False)
