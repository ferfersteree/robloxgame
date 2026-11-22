from faunalib import *

ID, NAME, RARITY, BIOME = 'dodo', 'Dodo', 4, 1
KIND = 'ground'
METHOD, GESTURE = 'trot', 'wing_puff'       # бежит рысцой / раздувает крылья
BUSH_D = 2.6
OPEN = 'Open_Part'


def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    body = studs('dd_body', '#5f8fe8')
    spot = studs('dd_spot', '#a9c6ff')
    belly = studs('dd_belly', '#e6ecff')
    beak = studs('dd_beak', '#ffc93c')
    beak_tip = studs('dd_beak_tip', '#f08a24')
    leg = studs('dd_leg', '#ffa826')
    tailw = studs('dd_tail', '#ffffff')
    leafm = studs('dd_leaf', '#5bcb46')
    pink = smooth('dd_pink', '#ff9db4', 0.35)
    dark = smooth('dd_line', '#2a2030', 0.3)
    claw = smooth('dd_claw', '#fff6e0', 0.2)
    crestm = neon('dd_crest', '#ff5fa0', 2.4)
    glowc = neon('dd_glow', '#6ff7ff', 2.6)
    seg('body', 'root', (0, 0.1, 1.1))
    blk('body', (1.4, 1.5, 1.2), body, (0, 0.15, 1.2))
    blk('rump', (1.1, 0.4, 0.8), body, (0, 0.95, 1.3))
    blk('belly', (1.04, 0.12, 0.9), belly, (0, -0.62, 1.1))
    blk('belly_low', (1.1, 1.1, 0.1), belly, (0, 0.1, 0.58))
    for i, w in enumerate((0.8, 0.6, 0.4, 0.2)):
        pix('chest_feather_%d' % i, (w, 0.04, 0.12), spot, (0, -0.69 - i * 0.008, 1.5 - i * 0.12))
    for i, (x, y, z) in enumerate(((-1, 0.0, 1.5), (-1, 0.5, 1.05), (1, 0.25, 1.45), (1, -0.25, 1.0),
                                   (1, 0.65, 1.2), (-1, -0.3, 1.2), (-1, 0.75, 1.55), (1, -0.35, 1.6))):
        pix('spot_%d' % i, (0.03, 0.24, 0.2), spot, (x * 0.705, y, z))
    for i in range(2):
        for j, x in enumerate((-0.4, 0.0, 0.4)):
            pix('back_feather_%d%d' % (i, j), (0.26, 0.3, 0.04), spot, (x, 0.15 + i * 0.42, 1.815))
    for i, x in enumerate((-0.44, -0.22, 0.0, 0.22, 0.44)):
        pix('collar_leaf_%d' % i, (0.2, 0.05, 0.16 if i % 2 else 0.22), leafm, (x, -0.7, 1.72 - (0.0 if i % 2 else 0.03)))
    # glowing rune spots (rarity 4): their own segment so they can flicker
    seg('glow', 'body', (0, 0.15, 1.2))
    for i, (x, y, z) in enumerate(((-1, 0.25, 1.3), (1, 0.0, 1.25), (-1, 0.0, 0.95), (1, 0.5, 0.9))):
        pix('rune_%d' % i, (0.03, 0.14, 0.12), glowc, (x * 0.72, y, z))
        pix('rune_dot_%d' % i, (0.03, 0.06, 0.05), glowc, (x * 0.72, y + 0.16, z + 0.1))
    # ---- head: big white cube with a blue cap
    seg('head', 'body', (0, -0.4, 1.75))
    blk('neck', (0.7, 0.6, 0.4), body, (0, -0.45, 1.9))
    pix('ruff', (0.84, 0.74, 0.08), belly, (0, -0.45, 1.8))
    blk('head', (1.2, 1.0, 1.0), belly, (0, -0.6, 2.55))
    blk('cap', (1.24, 1.04, 0.3), body, (0, -0.6, 2.95))
    for i, x in enumerate((-0.4, 0.0, 0.4)):
        pix('cap_fringe_%d' % i, (0.2, 0.04, 0.12), body, (x, -1.125, 2.76))
    blk('beak', (0.5, 0.5, 0.34), beak, (0, -1.3, 2.38))
    blk('beak_low', (0.4, 0.36, 0.12), beak_tip, (0, -1.24, 2.18), bev=0.03)
    blk('beak_hook', (0.36, 0.2, 0.36), beak_tip, (0, -1.6, 2.3), bev=0.05)
    pix('beak_band', (0.52, 0.04, 0.36), beak_tip, (0, -1.08, 2.38))
    blk('chest_puff', (1.1, 0.2, 0.6), belly, (0, -0.66, 1.3), bev=0.06)
    for sg, n in LR:
        pix('nostril_' + n, (0.05, 0.08, 0.04), dark, (sg * 0.1, -1.4, 2.555))
        pix('blush_' + n, (0.2, 0.03, 0.1), pink, (sg * 0.43, -1.105, 2.26))
        pix('cheek_feather_a' + n, (0.03, 0.2, 0.16), spot, (sg * 0.615, -0.6, 2.4))
        pix('cheek_feather_b' + n, (0.03, 0.14, 0.12), spot, (sg * 0.615, -0.38, 2.28))
    anime_eyes(0.36, 0.34, -1.105, 2.6, '#2a9df4', glow='#6ff7ff', lash=True, brow='#3f6fc8', brow_tilt=12, brow_dz=0.1)
    seg('crest', 'head', (0, -0.6, 3.1))
    for i, (x, h) in enumerate(((-0.26, 0.26), (-0.13, 0.4), (0.0, 0.52), (0.13, 0.4), (0.26, 0.26))):
        blk('crest_%d' % i, (0.1, 0.12, h), crestm, (x * 1.15, -0.62 + abs(x) * 0.2, 3.12 + h / 2), rot=(0, x * 70, 0), bev=0.02)
    for i, x in enumerate((-0.2, 0.0, 0.2)):
        pix('crest_base_%d' % i, (0.16, 0.16, 0.08), body, (x, -0.6, 3.13))
    for sg, n in LR:
        seg('wing_' + n, 'body', (sg * 0.7, -0.1, 1.6))
        blk('wing_' + n, (0.16, 0.84, 0.6), body, (sg * 0.78, 0.1, 1.3))
        pix('wing_layer_a' + n, (0.04, 0.6, 0.36), spot, (sg * 0.875, 0.12, 1.34))
        pix('wing_layer_b' + n, (0.04, 0.36, 0.2), belly, (sg * 0.9, 0.1, 1.38))
        pix('shoulder_' + n, (0.2, 0.24, 0.14), body, (sg * 0.76, -0.2, 1.62))
        for j in range(3):
            blk('wing_tip_%s%d' % (n, j), (0.14, 0.2, 0.18), spot, (sg * 0.78, 0.58, 1.48 - 0.2 * j), bev=0.03)
        for j in range(2):
            pix('wing_glow_%s%d' % (n, j), (0.1, 0.08, 0.1), glowc, (sg * 0.78, 0.7, 1.48 - 0.4 * j))
        seg('leg_' + n, 'body', (sg * 0.34, 0.15, 0.6))
        pix('pants_' + n, (0.28, 0.28, 0.1), body, (sg * 0.34, 0.15, 0.58))
        blk('leg_' + n, (0.18, 0.18, 0.5), leg, (sg * 0.34, 0.15, 0.34))
        pix('knee_' + n, (0.22, 0.22, 0.08), beak_tip, (sg * 0.34, 0.15, 0.4))
        blk('foot_' + n, (0.3, 0.3, 0.1), leg, (sg * 0.34, 0.05, 0.05), bev=0.03)
        for j, dx in enumerate((-0.13, 0.0, 0.13)):
            blk('toe_%s%d' % (n, j), (0.09, 0.3, 0.08), leg, (sg * 0.34 + dx * 1.2, -0.2, 0.04), rot=(0, 0, dx * 120), bev=0.02)
            pix('claw_%s%d' % (n, j), (0.05, 0.07, 0.05), claw, (sg * 0.34 + dx * 1.6, -0.37, 0.04))
    seg('tail', 'body', (0, 1.1, 1.5))
    for i, a in enumerate((-40, -20, 0, 20, 40)):
        sx, cz = math.sin(math.radians(a)), math.cos(math.radians(a))
        blk('tail_%d' % i, (0.16, 0.4, 0.16), tailw, (sx * 0.34, 1.28, 1.5 + cz * 0.2), rot=(-35, a, 0), bev=0.04)
        pix('tail_glow_%d' % i, (0.1, 0.1, 0.1), glowc, (sx * 0.4, 1.46, 1.64 + cz * 0.24), rot=(-35, a, 0))
    # light sparks drifting around (rarity 4) - FX segment, not exported with the model
    seg('fxs_sparks', 'root', (0, 0.1, 1.7))
    for i in range(6):
        a = math.radians(i * 60 + 20)
        pix('spark_%d' % i, (0.1, 0.1, 0.1), glowc if i % 2 else crestm,
            (math.cos(a) * 1.7, 0.1 + math.sin(a) * 1.7, 1.2 + (i % 3) * 0.7), rot=(45, 45, 0))
    assemble()
    marker('Head', 'head', (0, -0.6, 2.55))
    marker('Chest', 'body', (0, -0.65, 1.2))
    marker('Hit', 'body', (0, 0.15, 1.6))
    anims()
    build_fx()
    return bake_actions()


def anims():
    # Reveal: trots out of the bush with bouncy steps, stops, puffs up and flaps its tiny wings (45 frames)
    R = 'Reveal'
    clip(R, 45)
    k(R, 'root', 1, loc=(0, BUSH_D, 0))
    k(R, 'root', 22, loc=(0, 0, 0), ease='LINEAR')
    for i, f in enumerate(range(1, 23, 4)):
        k(R, 'body', f, loc=(0, 0, 0), rot=(0, 0, 6 if i % 2 else -6))
        k(R, 'body', f + 2, loc=(0, 0, 0.15))
        k(R, 'leg_L', f, rot=(35 if i % 2 else -35, 0, 0))
        k(R, 'leg_R', f, rot=(-35 if i % 2 else 35, 0, 0))
        k(R, 'head', f, rot=(-8 if i % 2 else 8, 0, 0))
    k(R, 'body', 24, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0)
    k(R, 'leg_L', 24, rot=(0, 0, 0))
    k(R, 'leg_R', 24, rot=(0, 0, 0))
    k(R, 'head', 24, rot=(0, 0, 0))
    # puff up + flap
    k(R, 'body', 30, scale=(1.18, 1.1, 1.12))
    k(R, 'body', 40, scale=(1.18, 1.1, 1.12))
    k(R, 'body', 45, scale=1.0)
    for n, s in (('L', -1), ('R', 1)):
        k(R, 'wing_' + n, 24, rot=(0, 0, 0))
        for j, f in enumerate(range(28, 42, 3)):
            k(R, 'wing_' + n, f, rot=(0, -s * (70 if j % 2 == 0 else 25), 0))
        k(R, 'wing_' + n, 45, rot=(0, 0, 0))
    k(R, 'crest', 24, rot=(0, 0, 0), scale=1.0)
    k(R, 'crest', 30, rot=(0, 0, 0), scale=1.4)
    k(R, 'crest', 45, scale=1.0)
    k(R, 'head', 30, rot=(-20, 0, 0))
    k(R, 'head', 40, rot=(-20, 0, 0))
    k(R, 'head', 45, rot=(0, 0, 0))
    k(R, 'tail', 30, rot=(-25, 0, 0))
    k(R, 'tail', 45, rot=(0, 0, 0))
    I = 'Idle'
    clip(I, 50)
    for f, a in ((1, 0), (10, 12), (14, 0), (30, 0), (36, 0), (50, 0)):
        k(I, 'head', f, rot=(a, 0, 0))
    k(I, 'head', 33, rot=(0, 0, 20))
    k(I, 'body', 1, scale=1.0)
    k(I, 'body', 25, scale=(1.03, 1.03, 1.04))
    k(I, 'body', 50, scale=1.0)
    for f, a in ((1, 0), (20, 0), (23, 20), (26, 0), (50, 0)):
        k(I, 'tail', f, rot=(0, 0, a))
    blink(I, (18, 42))
    blink(R, (26,))
    pulse(I, 'crest', 16, 0.12)
    pulse(I, 'glow', 16, 0.03)
    k(I, 'fxs_sparks', 1, rot=(0, 0, 0), loc=(0, 0, 0))
    k(I, 'fxs_sparks', 25, rot=(0, 0, 0), loc=(0, 0, 0.25))
    k(I, 'fxs_sparks', 50, rot=(0, 0, 0), loc=(0, 0, 0))
    k(R, 'fxs_sparks', 1, scale=0.0)
    k(R, 'fxs_sparks', 28, scale=0.0)
    k(R, 'fxs_sparks', 36, scale=1.0, rot=(0, 0, -120))
    k(R, 'fxs_sparks', 45, scale=1.0, rot=(0, 0, 0))


def build_fx():
    fx(True)
    dust = ghost('dd_dust', '#f1e0bc', 1.1, 0.85, 1.2)
    feather = studs('dd_feather', '#a8b6dc')
    rnd = random.Random(51)
    base = G.root.location
    for i in range(6):
        p = blk('step_dust_%d' % i, (0.3, 0.3, 0.3), dust, (0, 0, 0), bev=0.06)
        f = 3 + i * 4
        y = BUSH_D * (1 - (f - 1) / 21)
        p0 = base + Vector(((-0.3 if i % 2 else 0.3), y, 0.1))
        fxkey(p, 1, loc=p0, scale=0, alpha=1)
        fxkey(p, f, loc=p0, scale=0.3, alpha=1)
        fxkey(p, f + 10, loc=p0 + Vector((0, 0.3, 0.4)), scale=1.3, alpha=0)
    for i in range(10):
        fb = blk('feather_%d' % i, (0.08, 0.28, 0.03), feather, (0, 0, 0), bev=0.01)
        p0 = base + Vector((rnd.choice((-0.8, 0.8)), 0.1, 1.4))
        p1 = p0 + Vector((rnd.uniform(-1.4, 1.4), rnd.uniform(-1.2, 0.8), rnd.uniform(0.6, 1.5)))
        fxkey(fb, 1, loc=p0, scale=0)
        fxkey(fb, 30, loc=p0, scale=0)
        fxkey(fb, 32, loc=p0, scale=1)
        fxkey(fb, 40, loc=p1, rot=(rnd.uniform(0, 90), 120, rnd.uniform(0, 360)))
        fxkey(fb, 45, loc=p1 - Vector((0, 0, 0.5)), scale=0, rot=(rnd.uniform(0, 90), 200, rnd.uniform(0, 360)))
    fx(False)
