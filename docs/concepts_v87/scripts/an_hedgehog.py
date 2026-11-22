from faunalib import *

ID, NAME, RARITY, BIOME = 'hedgehog', 'Hedgehog', 2, 1
KIND = 'ground'
METHOD, GESTURE = 'roll_ball', 'shake_off'       # катится клубком / отряхивается
BUSH_D = 2.0
OPEN = 'Open_Part'


def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    spine = studs('hh_spine', '#8a5a38')
    spine_tip = studs('hh_spine_tip', '#f0d8a8')
    face = studs('hh_face', '#f7d9ac')
    belly = studs('hh_belly', '#fff0d6')
    nose = smooth('hh_nose', '#2b1a20', 0.15)
    line = smooth('hh_line', '#3a2620', 0.3)
    apple = studs('hh_apple', '#f0402e')
    stem = studs('hh_stem', '#5a3a1c')
    leafm = studs('hh_leaf', '#5bbb36')
    leafo = studs('hh_leaf_o', '#f0a020')
    blush = smooth('hh_blush', '#ff9aa8', 0.4)
    shine = smooth('hh_shine', '#ffffff', 0.1)
    seg('body', 'root', (0, 0.05, 0.45))
    blk('body', (1.0, 1.05, 0.62), belly, (0, 0.08, 0.42))
    blk('coat', (1.12, 1.1, 0.6), spine, (0, 0.2, 0.62))
    blk('coat_top', (0.86, 0.86, 0.2), spine, (0, 0.22, 0.98))
    blk('coat_back', (0.9, 0.2, 0.5), spine, (0, 0.8, 0.55))
    for i, x in enumerate((-0.44, -0.22, 0.0, 0.22, 0.44)):
        pix('fringe_%d' % i, (0.16, 0.06, 0.12 if i % 2 else 0.18), spine_tip, (x, -0.36, 0.38 if i % 2 else 0.35))
    for sg, n in LR:
        for j, y in enumerate((-0.1, 0.2, 0.5)):
            pix('fringe_s%s%d' % (n, j), (0.04, 0.18, 0.12), spine_tip, (sg * 0.57, y, 0.36))
    # spikes: square pyramids (the silhouette)
    n = 0
    for i, x in enumerate((-0.36, -0.12, 0.12, 0.36)):
        for j, y in enumerate((-0.14, 0.12, 0.38, 0.62)):
            z = 1.06 if abs(x) < 0.2 else 0.9
            tilt = Vector((x * 0.9, 0.35 + y * 0.6, 1.0))
            cone('spike_t%d' % n, 0.12, 0.36, spine_tip if (i + j) % 2 else spine, 4, loc=(x, y, z), rot=aim(tilt, 45), ol=0.012)
            n += 1
    for s in (-1, 1):
        for y in (-0.1, 0.2, 0.5):
            cone('spike_s%d' % n, 0.11, 0.32, spine, 4, loc=(s * 0.55, y, 0.74), rot=aim((s, 0.4, 0.5), 45), ol=0.012)
            n += 1
        for y in (0.05, 0.38):
            cone('spike_s%d' % n, 0.1, 0.28, spine_tip, 4, loc=(s * 0.56, y, 0.52), rot=aim((s, 0.4, 0.15), 45), ol=0.012)
            n += 1
    for x in (-0.3, 0.0, 0.3):
        cone('spike_b%d' % n, 0.11, 0.32, spine_tip if x else spine, 4, loc=(x, 0.9, 0.62), rot=aim((x, 1, 0.4), 45), ol=0.012)
        n += 1
    blk('apple', (0.3, 0.3, 0.28), apple, (0.2, 0.3, 1.26), bev=0.06)
    pix('apple_stem', (0.05, 0.05, 0.1), stem, (0.2, 0.3, 1.44))
    pix('apple_leaf', (0.16, 0.08, 0.04), leafm, (0.29, 0.3, 1.46), rot=(0, -25, 0))
    pix('apple_shine', (0.06, 0.03, 0.1), shine, (0.12, 0.145, 1.3))
    pix('leaf_a', (0.2, 0.14, 0.04), leafo, (-0.28, 0.5, 1.2), rot=(15, 20, 30))
    pix('leaf_a_stem', (0.03, 0.08, 0.03), stem, (-0.2, 0.42, 1.18), rot=(15, 20, 30))
    # ---- big face
    seg('head', 'body', (0, -0.4, 0.5))
    blk('face', (0.86, 0.4, 0.62), face, (0, -0.58, 0.5))
    blk('hood', (0.92, 0.3, 0.16), spine, (0, -0.5, 0.85))
    for i, x in enumerate((-0.33, -0.11, 0.11, 0.33)):
        pix('hood_tip_%d' % i, (0.14, 0.05, 0.1), spine_tip if i % 2 else spine, (x, -0.66, 0.76))
    blk('snout', (0.32, 0.26, 0.22), face, (0, -0.9, 0.36), bev=0.04)
    blk('nose', (0.14, 0.09, 0.11), nose, (0, -1.05, 0.42), bev=0.02, ol=0.01)
    pix('mouth', (0.1, 0.03, 0.03), line, (0, -1.03, 0.29))
    for sg, nn in LR:
        blk('ear_' + nn, (0.18, 0.08, 0.18), face, (sg * 0.36, -0.62, 0.9), bev=0.03)
        pix('ear_in_' + nn, (0.09, 0.03, 0.09), blush, (sg * 0.36, -0.665, 0.9))
        pix('blush_' + nn, (0.13, 0.03, 0.07), blush, (sg * 0.3, -0.785, 0.34))
        pix('cheek_' + nn, (0.08, 0.08, 0.1), belly, (sg * 0.45, -0.72, 0.3))
        for j, (dx, dz) in enumerate(((0.0, 0.0), (0.06, 0.05))):
            pix('freckle_%s%d' % (nn, j), (0.03, 0.03, 0.03), spine, (sg * (0.2 + dx), -0.785, 0.42 + dz))
    anime_eyes(0.25, 0.21, -0.785, 0.6, '#5a7a2a', lash=True, brow='#8a5a38', brow_tilt=8, brow_dz=0.08, sleepy=0.14)
    for sg, nn in LR:
        for fb, y in (('f', -0.3), ('b', 0.4)):
            seg('leg_%s%s' % (fb, nn), 'body', (sg * 0.32, y, 0.2))
            blk('leg_%s%s' % (fb, nn), (0.18, 0.2, 0.18), face, (sg * 0.32, y, 0.13), bev=0.03)
            blk('paw_%s%s' % (fb, nn), (0.2, 0.26, 0.08), belly, (sg * 0.32, y - 0.04, 0.04), bev=0.015)
            for j in (-1, 0, 1):
                pix('toe_%s%s%d' % (fb, nn, j + 1), (0.045, 0.04, 0.05), spine, (sg * 0.32 + j * 0.065, y - 0.18, 0.035))
    seg('tail', 'body', (0, 0.9, 0.3))
    blk('tail', (0.14, 0.14, 0.12), face, (0, 0.95, 0.3), bev=0.02)
    pix('tail_tip', (0.08, 0.08, 0.08), belly, (0, 1.04, 0.32))
    assemble()
    marker('Head', 'head', (0, -0.6, 0.5))
    marker('Chest', 'body', (0, -0.38, 0.4))
    marker('Hit', 'body', (0, 0.2, 0.95))
    anims()
    build_fx()
    return bake_actions()


def anims():
    # Reveal: rolls out as a spiky ball, uncurls, then shakes like a wet dog (40 frames)
    R = 'Reveal'
    clip(R, 40)
    # roll about the body centre (root pivot is on the ground, so the offset is compensated every frame)
    cz = 0.5
    for f in range(1, 21):
        if f <= 16:
            t = (f - 1) / 15.0
            ang, y, z = -540 * t, BUSH_D + (-0.15 - BUSH_D) * t, 0.15
        else:
            t = (f - 16) / 4.0
            ang, y, z = -540 - 180 * t, -0.15 + 0.15 * t, 0.15 * (1 - t)
        r = math.radians(ang)
        k(R, 'root', f, loc=(0, y + cz * math.sin(r), z + cz - cz * math.cos(r)), rot=(ang, 0, 0), ease='LINEAR')
    k(R, 'body', 1, scale=(0.9, 0.9, 1.0))
    k(R, 'body', 16, scale=(0.9, 0.9, 1.0))
    k(R, 'body', 21, scale=1.0)
    k(R, 'head', 1, loc=(0, 0.3, -0.05), rot=(60, 0, 0))
    k(R, 'head', 16, loc=(0, 0.3, -0.05), rot=(60, 0, 0))
    k(R, 'head', 21, loc=(0, 0, 0), rot=(0, 0, 0))
    for fb in ('f', 'b'):
        for nn in ('L', 'R'):
            k(R, 'leg_%s%s' % (fb, nn), 1, loc=(0, 0, 0.12), scale=0.3)
            k(R, 'leg_%s%s' % (fb, nn), 16, loc=(0, 0, 0.12), scale=0.3)
            k(R, 'leg_%s%s' % (fb, nn), 21, loc=(0, 0, 0), scale=1.0)
    for i, f in enumerate(range(22, 37, 2)):
        a = 18 * (1 if i % 2 == 0 else -1) * (1 - i / 9)
        k(R, 'body', f, rot=(0, a * 0.4, a))
    k(R, 'body', 38, rot=(0, 0, 0))
    k(R, 'head', 26, rot=(0, 0, -14))
    k(R, 'head', 30, rot=(0, 0, 14))
    k(R, 'head', 36, rot=(0, 0, 0))
    k(R, 'tail', 22, rot=(0, 0, 0))
    k(R, 'tail', 30, rot=(0, 0, 30))
    k(R, 'tail', 38, rot=(0, 0, 0))
    I = 'Idle'
    clip(I, 40)
    k(I, 'body', 1, scale=1.0)
    k(I, 'body', 20, scale=(1.03, 1.02, 1.05))
    k(I, 'body', 40, scale=1.0)
    for f, a in ((1, 0), (8, -8), (11, -4), (14, -8), (22, 0), (40, 0)):
        k(I, 'head', f, rot=(a, 0, 0))
    blink(I, (30,))
    blink(R, (25,))
    for f, a in ((1, 0), (26, 0), (29, 25), (32, -20), (35, 0), (40, 0)):
        k(I, 'tail', f, rot=(0, 0, a))


def build_fx():
    fx(True)
    dust = ghost('hh_dust', '#f1e0bc', 1.1, 0.85, 1.2)
    drop = smooth('hh_drop', '#bfeaff', 0.1)
    rnd = random.Random(31)
    base = G.root.location
    for i in range(6):
        p = blk('roll_dust_%d' % i, (0.3, 0.3, 0.3), dust, (0, 0, 0), bev=0.06)
        t = 3 + i * 2
        y = BUSH_D * (1 - (t - 1) / 15)
        p0 = base + Vector((rnd.uniform(-0.3, 0.3), y + 0.3, 0.12))
        fxkey(p, 1, loc=p0, scale=0, alpha=1)
        fxkey(p, t, loc=p0, scale=0.4, alpha=1)
        fxkey(p, t + 12, loc=p0 + Vector((0, 0.3, 0.4)), scale=1.4, alpha=0, rot=(30, 20, 10))
    for i in range(8):
        a = math.radians(i * 45 + 10)
        d = blk('shake_drop_%d' % i, (0.09, 0.09, 0.09), drop, (0, 0, 0), bev=0.02, ol=0)
        p0 = base + Vector((0, 0.1, 0.6))
        p1 = p0 + Vector((math.cos(a) * 1.0, math.sin(a) * 1.0, 0.5))
        fxkey(d, 1, loc=p0, scale=0)
        fxkey(d, 22, loc=p0, scale=0)
        fxkey(d, 24, loc=p0, scale=1)
        fxkey(d, 34, loc=(p1.x, p1.y, 0.05), scale=0.8)
        fxkey(d, 38, scale=0)
    fx(False)
