from faunalib import *

ID, NAME, RARITY, BIOME = 'squirrel', 'Squirrel', 1, 1
KIND = 'ground'
METHOD, GESTURE = 'drop_from_above', 'tail_wave'     # падает сверху / машет хвостом
BUSH_D = 1.6
OPEN = 'Open_Burst'


def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    fur = studs('sq_fur', '#f47c2c')
    cream = studs('sq_cream', '#fff0d2')
    dark = studs('sq_dark', '#a8481a')
    nose = smooth('sq_nose', '#3a2026', 0.2)
    line = smooth('sq_line', '#3a2620', 0.3)
    white = smooth('sq_tooth', '#ffffff', 0.15)
    pink = smooth('sq_pink', '#ff9db4', 0.35)
    acorn = studs('sq_acorn', '#d09a48')
    cap = studs('sq_cap', '#70482a')
    # ---- body: sits upright
    seg('body', 'root', (0, 0.05, 0.4))
    blk('body', (0.62, 0.58, 0.68), fur, (0, 0.06, 0.5))
    blk('hips', (0.7, 0.42, 0.36), fur, (0, 0.16, 0.3))
    blk('belly', (0.42, 0.06, 0.5), cream, (0, -0.24, 0.48), bev=0.02)
    for i, (w, z) in enumerate(((0.34, 0.76), (0.24, 0.69), (0.12, 0.62))):
        pix('chest_fluff_%d' % i, (w, 0.04, 0.08), cream, (0, -0.275 - i * 0.01, z))
    pix('stripe_c', (0.12, 0.03, 0.5), dark, (0, 0.365, 0.52))
    for sg, n in LR:
        pix('stripe_' + n, (0.07, 0.03, 0.44), cream, (sg * 0.13, 0.365, 0.52))
        pix('stripe_o' + n, (0.05, 0.03, 0.4), dark, (sg * 0.21, 0.365, 0.52))
        pix('side_' + n, (0.03, 0.2, 0.14), cream, (sg * 0.325, -0.02, 0.5))
        pix('side_b' + n, (0.03, 0.12, 0.1), cream, (sg * 0.325, 0.1, 0.42))
    # ---- head
    seg('head', 'body', (0, -0.02, 0.82))
    blk('head', (0.84, 0.72, 0.7), fur, (0, -0.08, 1.13))
    blk('head_top', (0.6, 0.5, 0.08), fur, (0, -0.08, 1.5), bev=0.03)
    blk('muzzle', (0.36, 0.14, 0.2), cream, (0, -0.47, 0.95), bev=0.03)
    blk('nose', (0.1, 0.06, 0.07), nose, (0, -0.56, 1.02), bev=0.015, ol=0.008)
    pix('mouth', (0.03, 0.03, 0.07), line, (0, -0.545, 0.94))
    pix('fore_c', (0.1, 0.03, 0.2), dark, (0, -0.445, 1.38))
    pix('fore_d', (0.2, 0.03, 0.06), dark, (0, -0.445, 1.45))
    for sg, n in LR:
        blk('cheek_' + n, (0.26, 0.22, 0.28), cream, (sg * 0.36, -0.36, 0.95), bev=0.05)
        pix('cheek_tuft_a' + n, (0.09, 0.09, 0.09), cream, (sg * 0.5, -0.34, 0.9))
        pix('cheek_tuft_b' + n, (0.07, 0.07, 0.07), cream, (sg * 0.5, -0.32, 1.03))
        pix('blush_' + n, (0.12, 0.03, 0.06), pink, (sg * 0.37, -0.475, 1.02))
        pix('tooth_' + n, (0.06, 0.03, 0.07), white, (sg * 0.035, -0.54, 0.87))
        for j, dz in enumerate((0.04, -0.03)):
            pix('whisker_%s%d' % (n, j), (0.18, 0.02, 0.02), white, (sg * 0.56, -0.4, 0.95 + dz), rot=(0, -sg * (10 if j == 0 else -10), sg * 10))
        pix('temple_' + n, (0.03, 0.2, 0.14), dark, (sg * 0.425, 0.0, 1.3))
    anime_eyes(0.27, 0.2, -0.445, 1.2, '#7a3f18', brow='#70401a', brow_tilt=-8, brow_dz=0.09)
    for sg, n in LR:
        seg('ear_' + n, 'head', (sg * 0.26, -0.05, 1.46))
        blk('ear_' + n, (0.2, 0.1, 0.26), fur, (sg * 0.28, -0.05, 1.58), bev=0.03)
        pix('ear_in_' + n, (0.1, 0.03, 0.16), pink, (sg * 0.28, -0.105, 1.57))
        pix('ear_tuft_a' + n, (0.1, 0.08, 0.14), dark, (sg * 0.3, -0.05, 1.76))
        pix('ear_tuft_b' + n, (0.06, 0.06, 0.1), dark, (sg * 0.33, -0.05, 1.86))
    # ---- arms hold the acorn
    for sg, n in LR:
        seg('leg_f' + n, 'body', (sg * 0.2, -0.2, 0.62))
        blk('arm_' + n, (0.13, 0.28, 0.13), fur, (sg * 0.18, -0.32, 0.56), rot=(-30, 0, 0), bev=0.02)
        blk('hand_' + n, (0.13, 0.12, 0.12), cream, (sg * 0.13, -0.44, 0.5), bev=0.02)
        for j in (-1, 1):
            pix('finger_%s%d' % (n, j), (0.04, 0.05, 0.05), dark, (sg * 0.13 + j * 0.035, -0.51, 0.5))
        seg('leg_b' + n, 'body', (sg * 0.28, 0.12, 0.28))
        blk('thigh_' + n, (0.18, 0.4, 0.34), fur, (sg * 0.36, 0.12, 0.24), bev=0.03)
        blk('foot_' + n, (0.19, 0.44, 0.1), cream, (sg * 0.36, -0.06, 0.05), bev=0.02)
        for j in (-1, 0, 1):
            pix('toe_%s%d' % (n, j + 1), (0.045, 0.04, 0.06), dark, (sg * 0.36 + j * 0.06, -0.29, 0.05))
    seg('acorn', 'body', (0, -0.5, 0.46))
    blk('acorn', (0.2, 0.2, 0.22), acorn, (0, -0.52, 0.44), bev=0.04)
    blk('acorn_cap', (0.24, 0.24, 0.09), cap, (0, -0.52, 0.57), bev=0.02)
    pix('acorn_stem', (0.04, 0.04, 0.07), cap, (0, -0.52, 0.65))
    pix('acorn_tip', (0.06, 0.06, 0.04), cap, (0, -0.52, 0.32))
    pix('acorn_shine', (0.05, 0.03, 0.08), cream, (-0.05, -0.625, 0.47))
    for j in (-1, 1):
        pix('acorn_dot_%d' % j, (0.05, 0.03, 0.04), acorn, (j * 0.06, -0.645, 0.57))
    # ---- huge stacked tail curling over the back
    seg('tail', 'body', (0, 0.34, 0.3))
    blk('tail_a', (0.36, 0.4, 0.36), fur, (0, 0.52, 0.34))
    blk('tail_b', (0.42, 0.4, 0.5), fur, (0, 0.72, 0.72))
    pix('tail_stripe_b', (0.14, 0.03, 0.4), dark, (0, 0.925, 0.72))
    pix('tail_tuft_b1', (0.12, 0.12, 0.12), fur, (0.22, 0.8, 0.5))
    pix('tail_tuft_b2', (0.12, 0.12, 0.12), fur, (-0.22, 0.66, 0.92))
    seg('tail_tip', 'tail', (0, 0.72, 0.97))
    blk('tail_c', (0.48, 0.46, 0.46), fur, (0, 0.7, 1.2))
    blk('tail_d', (0.42, 0.38, 0.34), cream, (0, 0.48, 1.48))
    blk('tail_e', (0.32, 0.26, 0.24), fur, (0, 0.28, 1.4), bev=0.04)
    pix('tail_stripe_c', (0.14, 0.03, 0.36), dark, (0, 0.935, 1.2))
    pix('tail_top', (0.14, 0.2, 0.03), dark, (0, 0.8, 1.44))
    pix('tail_tuft_c1', (0.12, 0.12, 0.12), cream, (0.22, 0.5, 1.62))
    pix('tail_tuft_c2', (0.12, 0.12, 0.12), cream, (-0.2, 0.42, 1.66))
    pix('tail_tuft_c3', (0.12, 0.12, 0.12), fur, (0.26, 0.74, 1.4))
    assemble()
    marker('Head', 'head', (0, -0.08, 1.13))
    marker('Chest', 'body', (0, -0.24, 0.55))
    marker('Hit', 'body', (0, 0.06, 0.6))
    anims()
    build_fx()
    return bake_actions()


def anims():
    # Reveal: drops from the top of the bush with a somersault, bounces, waves the big tail (33 frames)
    R = 'Reveal'
    clip(R, 33)
    k(R, 'root', 1, loc=(0, BUSH_D, 4.6), rot=(0, 0, 0), scale=0.9)
    k(R, 'root', 5, loc=(0, BUSH_D * 0.6, 5.0), rot=(-40, 0, 0), scale=1.0)
    k(R, 'root', 13, loc=(0, 0, 0), rot=(-360, 0, 0), ease='LINEAR')
    k(R, 'root', 16, loc=(0, 0, 0.35), rot=(-360, 0, 0))
    k(R, 'root', 19, loc=(0, 0, 0), rot=(-360, 0, 0))
    k(R, 'body', 13, scale=(1.2, 1.2, 0.75))
    k(R, 'body', 16, scale=(0.9, 0.9, 1.1))
    k(R, 'body', 20, scale=1.0)
    k(R, 'tail', 19, rot=(0, 0, 0))
    k(R, 'tail', 22, rot=(0, 30, 0))
    k(R, 'tail', 25, rot=(0, -30, 0))
    k(R, 'tail', 28, rot=(0, 25, 0))
    k(R, 'tail', 33, rot=(0, 0, 0))
    k(R, 'tail_tip', 19, rot=(0, 0, 0))
    k(R, 'tail_tip', 23, rot=(-25, 0, 0))
    k(R, 'tail_tip', 27, rot=(15, 0, 0))
    k(R, 'tail_tip', 33, rot=(0, 0, 0))
    k(R, 'head', 19, rot=(0, 0, 0))
    k(R, 'head', 25, rot=(0, 0, -12))
    k(R, 'head', 33, rot=(0, 0, 0))
    # Idle: nibble the acorn + tail sway (40 frames)
    I = 'Idle'
    clip(I, 40)
    for n in ('L', 'R'):
        for f, a in ((1, 0), (6, -20), (11, 0), (16, -20), (21, 0), (40, 0)):
            k(I, 'leg_f' + n, f, rot=(a, 0, 0))
    for f, z in ((1, 0), (6, 0.1), (11, 0), (16, 0.1), (21, 0), (40, 0)):
        k(I, 'acorn', f, loc=(0, 0, z))
    k(I, 'tail', 1, rot=(0, 0, 0))
    k(I, 'tail', 20, rot=(0, 8, 0))
    k(I, 'tail', 40, rot=(0, 0, 0))
    for f, a in ((1, 0), (6, 8), (11, 0), (40, 0)):
        k(I, 'head', f, rot=(a, 0, 0))
    blink(I, (28,))
    blink(R, (26,))
    for n in ('L', 'R'):
        for f, a in ((1, 0), (30, 0), (32, 18), (34, 0), (40, 0)):
            k(I, 'ear_' + n, f, rot=(a, 0, 0))


def build_fx():
    fx(True)
    leafm = studs('sq_leafbit', '#4fae35')
    rnd = random.Random(21)
    for i in range(7):
        l_ = blk('leaf_bit_%d' % i, (0.22, 0.22, 0.05), leafm, (0, 0, 0), bev=0.02)
        p0 = G.root.location + Vector((rnd.uniform(-0.6, 0.6), BUSH_D, 4.4))
        p1 = p0 + Vector((rnd.uniform(-1.5, 1.5), rnd.uniform(-1.0, 0.5), rnd.uniform(0.3, 1.0)))
        fxkey(l_, 1, loc=p0, scale=0)
        fxkey(l_, 3, loc=p0, scale=1)
        fxkey(l_, 12, loc=p1, rot=(rnd.uniform(0, 360), 180, 90))
        fxkey(l_, 30, loc=(p1.x, p1.y, 0.05), rot=(rnd.uniform(0, 360), 360, 200), scale=0.8)
        fxkey(l_, 33, scale=0)
    ring = torus('land_ring', 0.4, 0.04, ghost('sq_ring', '#fff4d8', 1.6, 0.9, 0.8), 4, 4)
    ring.rotation_euler = (0, 0, math.radians(45))
    p0 = G.root.location + Vector((0, 0, 0.04))
    fxkey(ring, 1, loc=p0, scale=0, alpha=1)
    fxkey(ring, 13, scale=0.3, alpha=1)
    fxkey(ring, 22, scale=2.4, alpha=0)
    fx(False)
