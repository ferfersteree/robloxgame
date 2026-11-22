from faunalib import *

ID, NAME, RARITY, BIOME = 'rabbit', 'Rabbit', 1, 1
KIND = 'ground'
METHOD, GESTURE = 'leap', 'sniff'          # выпрыгивает / принюхивается
BUSH_D = 2.2                               # bush centre is BUSH_D studs behind the final spot (+Y)
OPEN = 'Open_Part'


def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    fur = studs('rb_fur', '#dba266')
    dk = studs('rb_dark', '#b0733e')
    cream = studs('rb_cream', '#fbeed2')
    pink = smooth('rb_pink', '#ff9db4', 0.35)
    nose = smooth('rb_nose', '#e8507c', 0.2)
    tooth = smooth('rb_tooth', '#ffffff', 0.15)
    dark = smooth('rb_line', '#3a2620', 0.3)
    # ---- body: short chubby block with stepped rump and fluffy chest
    seg('body', 'root', (0, 0.1, 0.5))
    blk('body', (0.86, 0.95, 0.7), fur, (0, 0.12, 0.55))
    blk('rump', (0.94, 0.5, 0.6), fur, (0, 0.5, 0.5))
    blk('rump_top', (0.7, 0.4, 0.12), fur, (0, 0.42, 0.9), bev=0.03)
    blk('belly', (0.62, 0.1, 0.5), cream, (0, -0.37, 0.48))
    for i, (w, z) in enumerate(((0.5, 0.74), (0.36, 0.66), (0.2, 0.58))):
        pix('chest_fluff_%d' % i, (w, 0.05, 0.1), cream, (0, -0.42 - i * 0.012, z))
    for i, (x, y, z) in enumerate(((-0.2, 0.2, 0.915), (0.15, 0.05, 0.915), (0.22, 0.5, 0.975), (-0.12, 0.55, 0.975))):
        pix('back_spot_%d' % i, (0.18, 0.18, 0.03), dk, (x, y, z))
    for sg, n in LR:
        pix('side_tuft_a' + n, (0.04, 0.2, 0.14), cream, (sg * 0.445, 0.0, 0.42))
        pix('side_tuft_b' + n, (0.04, 0.12, 0.1), cream, (sg * 0.445, 0.14, 0.34))
        pix('hip_spot_' + n, (0.04, 0.2, 0.2), dk, (sg * 0.485, 0.55, 0.62))
    # ---- head: big cube ~45 % of the height
    seg('head', 'body', (0, -0.2, 0.9))
    blk('head', (1.08, 0.9, 0.9), fur, (0, -0.25, 1.32))
    blk('head_top', (0.8, 0.66, 0.1), fur, (0, -0.25, 1.8), bev=0.03)
    blk('muzzle', (0.5, 0.16, 0.3), cream, (0, -0.74, 1.07))
    blk('muzzle_top', (0.26, 0.12, 0.1), cream, (0, -0.74, 1.25), bev=0.02)
    blk('chin', (0.3, 0.12, 0.08), cream, (0, -0.7, 0.9), bev=0.02)
    blk('nose', (0.16, 0.07, 0.1), nose, (0, -0.85, 1.2), bev=0.02, ol=0.01)
    pix('mouth_line', (0.03, 0.03, 0.1), dark, (0, -0.83, 1.1))
    for i, w in enumerate((0.34, 0.22, 0.1)):
        pix('fore_tuft_%d' % i, (w, 0.05, 0.07), cream, (0.02 * i, -0.715, 1.72 - i * 0.07))
    for sg, n in LR:
        blk('cheek_' + n, (0.22, 0.2, 0.3), cream, (sg * 0.5, -0.6, 1.08), bev=0.04)
        pix('cheek_tuft_a' + n, (0.1, 0.1, 0.1), cream, (sg * 0.62, -0.58, 1.02))
        pix('cheek_tuft_b' + n, (0.08, 0.08, 0.08), cream, (sg * 0.63, -0.56, 1.16))
        pix('blush_' + n, (0.16, 0.03, 0.08), pink, (sg * 0.37, -0.71, 1.1))
        pix('tooth_' + n, (0.08, 0.04, 0.1), tooth, (sg * 0.045, -0.82, 0.97))
        pix('mouth_' + n, (0.1, 0.03, 0.03), dark, (sg * 0.06, -0.83, 1.04))
        for j, (dz, ry) in enumerate(((0.06, 12), (0.0, 0), (-0.06, -12))):
            pix('whisker_%s%d' % (n, j), (0.22, 0.02, 0.02), tooth, (sg * 0.7, -0.66, 1.08 + dz), rot=(0, -sg * ry, sg * 12))
    anime_eyes(0.32, 0.27, -0.705, 1.4, '#9a5a2c', lash=True, brow='#8a5530', brow_tilt=10, brow_dz=0.15)
    for i, (x, z, w) in enumerate(((-0.2, 1.5, 0.22), (0.18, 1.2, 0.18), (0.0, 1.0, 0.3))):
        pix('nape_spot_%d' % i, (w, 0.03, 0.16), dk if i < 2 else cream, (x, 0.205, z))
    for sg, n in LR:
        pix('temple_' + n, (0.03, 0.2, 0.16), dk, (sg * 0.545, -0.1, 1.5))
        pix('temple_b' + n, (0.03, 0.12, 0.1), dk, (sg * 0.545, 0.08, 1.36))
    # ---- ears: tall stepped slabs (the silhouette)
    for sg, n in LR:
        seg('ear_' + n, 'head', (sg * 0.3, -0.2, 1.75))
        r = (0, sg * 8, 0)
        blk('ear_base_' + n, (0.3, 0.16, 0.3), fur, (sg * 0.31, -0.2, 1.9), rot=r)
        blk('ear_' + n, (0.26, 0.14, 0.62), fur, (sg * 0.36, -0.2, 2.3), rot=r)
        blk('ear_tip_' + n, (0.2, 0.13, 0.2), dk, (sg * 0.42, -0.2, 2.68), rot=r, bev=0.04)
        pix('ear_in_' + n, (0.14, 0.03, 0.56), pink, (sg * 0.36, -0.275, 2.26), rot=r)
        pix('ear_in_tip_' + n, (0.08, 0.03, 0.12), pink, (sg * 0.41, -0.275, 2.58), rot=r)
    # ---- legs: short, with toe cubes
    for sg, n in LR:
        seg('leg_f' + n, 'body', (sg * 0.24, -0.28, 0.32))
        blk('arm_' + n, (0.22, 0.22, 0.28), fur, (sg * 0.24, -0.3, 0.22))
        blk('paw_f' + n, (0.26, 0.3, 0.12), cream, (sg * 0.24, -0.36, 0.06), bev=0.03)
        for j in (-1, 0, 1):
            pix('toe_f%s%d' % (n, j + 1), (0.06, 0.05, 0.07), dk, (sg * 0.24 + j * 0.085, -0.515, 0.05))
        seg('leg_b' + n, 'body', (sg * 0.4, 0.42, 0.38))
        blk('thigh_' + n, (0.24, 0.5, 0.42), fur, (sg * 0.5, 0.42, 0.3))
        blk('foot_' + n, (0.26, 0.66, 0.13), cream, (sg * 0.5, 0.16, 0.065), bev=0.03)
        pix('pad_' + n, (0.14, 0.03, 0.07), pink, (sg * 0.5, -0.175, 0.07))
        for j in (-1, 0, 1):
            pix('toe_b%s%d' % (n, j + 1), (0.06, 0.05, 0.07), dk, (sg * 0.5 + j * 0.085, -0.19, 0.11))
    # ---- tail: fluffy stepped pom
    seg('tail', 'body', (0, 0.74, 0.55))
    blk('tail', (0.36, 0.3, 0.36), cream, (0, 0.86, 0.62))
    blk('tail_b', (0.24, 0.16, 0.24), cream, (0, 1.04, 0.66), bev=0.03)
    pix('tail_tuft_a', (0.12, 0.1, 0.12), cream, (0.1, 1.0, 0.82))
    pix('tail_tuft_b', (0.1, 0.1, 0.1), cream, (-0.14, 0.98, 0.5))
    assemble()
    marker('Head', 'head', (0, -0.25, 1.32))
    marker('Chest', 'body', (0, -0.37, 0.6))
    marker('Hit', 'body', (0, 0.15, 0.8))
    anims()
    build_fx()
    return bake_actions()


def anims():
    # Reveal: leap out of the bush, land squash, then sniff around (36 frames = 1.2 s)
    R = 'Reveal'
    clip(R, 36)
    k(R, 'root', 1, loc=(0, BUSH_D, -0.4), scale=0.85)
    k(R, 'root', 5, loc=(0, BUSH_D - 0.1, 0.0), scale=1.0)
    k(R, 'root', 11, loc=(0, BUSH_D * 0.45, 1.5))
    k(R, 'root', 17, loc=(0, 0, 0), ease='LINEAR')
    k(R, 'root', 36, loc=(0, 0, 0))
    k(R, 'body', 1, rot=(0, 0, 0), scale=(1.05, 1.05, 0.85))
    k(R, 'body', 5, rot=(10, 0, 0), scale=(0.95, 0.95, 1.1))
    k(R, 'body', 11, rot=(-25, 0, 0), scale=(0.9, 0.9, 1.15))
    k(R, 'body', 17, rot=(8, 0, 0), scale=(1.15, 1.15, 0.8))
    k(R, 'body', 21, rot=(0, 0, 0), scale=1.0)
    for s, n in ((-1, 'L'), (1, 'R')):
        k(R, 'leg_b' + n, 1, rot=(0, 0, 0))
        k(R, 'leg_b' + n, 8, rot=(-50, 0, 0))
        k(R, 'leg_b' + n, 14, rot=(25, 0, 0))
        k(R, 'leg_b' + n, 19, rot=(0, 0, 0))
        k(R, 'leg_f' + n, 8, rot=(40, 0, 0))
        k(R, 'leg_f' + n, 15, rot=(-30, 0, 0))
        k(R, 'leg_f' + n, 19, rot=(0, 0, 0))
        k(R, 'ear_' + n, 1, rot=(0, 0, 0))
        k(R, 'ear_' + n, 11, rot=(35, 0, -s * 10))
        k(R, 'ear_' + n, 18, rot=(-20, 0, s * 15))
        k(R, 'ear_' + n, 23, rot=(5, 0, 0))
        k(R, 'ear_' + n, 36, rot=(0, 0, 0))
    k(R, 'head', 17, rot=(0, 0, 0))
    k(R, 'head', 21, rot=(12, 0, 0))
    k(R, 'head', 24, rot=(6, 0, 20))
    k(R, 'head', 26, rot=(10, 0, 18))
    k(R, 'head', 29, rot=(6, 0, -20))
    k(R, 'head', 31, rot=(10, 0, -18))
    k(R, 'head', 36, rot=(0, 0, 0))
    k(R, 'tail', 17, rot=(0, 0, 0))
    k(R, 'tail', 20, rot=(0, 0, 30))
    k(R, 'tail', 23, rot=(0, 0, -30))
    k(R, 'tail', 26, rot=(0, 0, 0))
    # Idle: breathe, ear twitch, tail flick (45 frames, loops)
    I = 'Idle'
    clip(I, 45)
    k(I, 'body', 1, scale=1.0)
    k(I, 'body', 23, scale=(1.03, 1.03, 1.04))
    k(I, 'body', 45, scale=1.0)
    k(I, 'head', 1, rot=(0, 0, 0))
    k(I, 'head', 12, rot=(4, 0, 0))
    k(I, 'head', 16, rot=(0, 0, 0))
    k(I, 'head', 45, rot=(0, 0, 0))
    k(I, 'ear_L', 1, rot=(0, 0, 0))
    k(I, 'ear_L', 28, rot=(0, 0, 0))
    k(I, 'ear_L', 31, rot=(18, 0, -10))
    k(I, 'ear_L', 35, rot=(0, 0, 0))
    k(I, 'ear_L', 45, rot=(0, 0, 0))
    k(I, 'tail', 1, rot=(0, 0, 0))
    k(I, 'tail', 6, rot=(0, 0, 25))
    k(I, 'tail', 10, rot=(0, 0, 0))
    k(I, 'tail', 45, rot=(0, 0, 0))
    blink(I, (20,))
    blink(R, (30,))


def build_fx():
    """reveal FX (clip frames, world positions around the final spot): dust cubes + leaf bits"""
    fx(True)
    dust = ghost('rb_dust', '#f3e2c0', 1.1, 0.8, 1.2)
    leafm = studs('rb_leafbit', '#5fb83c')
    rnd = random.Random(11)
    for i in range(6):
        a = i * 60 + 15
        p = blk('land_dust_%d' % i, (0.3, 0.3, 0.3), dust, (0, 0, 0.1), bev=0.06)
        p0 = Vector((0, 0, 0.15)) + G.root.location
        p1 = p0 + Vector((0.8 * math.cos(math.radians(a)), 0.8 * math.sin(math.radians(a)), 0.25))
        fxkey(p, 1, loc=p0, scale=0, alpha=1)
        fxkey(p, 17, loc=p0, scale=0.2, alpha=1)
        fxkey(p, 26, loc=p1, scale=1.4, alpha=0.7, rot=(20, 30, 0))
        fxkey(p, 36, loc=p1 + Vector((0, 0, 0.3)), scale=1.8, alpha=0)
    for i in range(5):
        l_ = blk('leaf_bit_%d' % i, (0.22, 0.22, 0.05), leafm, (0, 0, 0), bev=0.02)
        p0 = G.root.location + Vector((0, BUSH_D, 0.8))
        p1 = p0 + Vector((rnd.uniform(-1.2, 1.2), rnd.uniform(-1.5, -0.3), rnd.uniform(0.6, 1.4)))
        fxkey(l_, 1, loc=p0, scale=0, rot=(0, 0, 0))
        fxkey(l_, 5, loc=p0, scale=1)
        fxkey(l_, 16, loc=p1, rot=(rnd.uniform(0, 360), 200, 90))
        fxkey(l_, 30, loc=(p1.x, p1.y, 0.05), scale=0.8, rot=(rnd.uniform(0, 360), 360, 180))
        fxkey(l_, 36, scale=0)
    fx(False)
