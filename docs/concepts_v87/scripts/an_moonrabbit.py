from faunalib import *

ID, NAME, RARITY, BIOME = 'moonrabbit', 'Moon Rabbit', 5, 1
KIND = 'ground'
METHOD, GESTURE = 'flash_appear', 'bow'      # появляется вспышкой, зависает в воздухе / поклон
BUSH_D = 2.4
OPEN = 'Open_Burst'
S = 1.2                                       # built in rabbit units, scaled up
HOVER = 2.3                                   # hover height of the show pose (studs)


def V(t):
    return tuple(x * S for x in t)


def B(n, size, mat, loc, **kw):
    return blk(n, V(size), mat, V(loc), **kw)


def P(n, size, mat, loc, **kw):
    return pix(n, V(size), mat, V(loc), **kw)


def SG(n, parent, joint):
    seg(n, parent, V(joint))


def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    fur = studs('mr_fur', '#e2e5ff')
    lav = studs('mr_lav', '#a9a3f7')
    navy = studs('mr_navy', '#4646b4')
    night = studs('mr_night', '#2e2a7a')
    gold = neon('mr_gold', '#ffe14a', 3.0)       # element glow of the biome: moonlit meadow gold
    cyan = neon('mr_cyan', '#7fe0ff', 2.6)
    aura = neon('mr_aura', '#ffe600', 3.4)       # rarity-5 yellow aura
    pink = smooth('mr_pink', '#ff9fc8', 0.35)
    tooth = smooth('mr_tooth', '#ffffff', 0.15)
    dark = smooth('mr_line', '#2a2450', 0.3)
    # ---- body
    SG('body', 'root', (0, 0.1, 0.5))
    B('body', (0.86, 0.95, 0.7), fur, (0, 0.12, 0.55))
    B('rump', (0.94, 0.5, 0.6), fur, (0, 0.5, 0.5))
    B('rump_top', (0.7, 0.4, 0.12), fur, (0, 0.42, 0.9), bev=0.03)
    B('belly', (0.62, 0.1, 0.5), lav, (0, -0.37, 0.48))
    for i, (w, z) in enumerate(((0.5, 0.74), (0.36, 0.66), (0.2, 0.58))):
        P('chest_fluff_%d' % i, (w, 0.05, 0.1), lav, (0, -0.42 - i * 0.012, z))
    for sg, n in LR:
        P('side_tuft_a' + n, (0.04, 0.2, 0.14), lav, (sg * 0.445, 0.0, 0.42))
        P('side_tuft_b' + n, (0.04, 0.12, 0.1), lav, (sg * 0.445, 0.14, 0.34))
        P('hip_spot_' + n, (0.04, 0.2, 0.2), lav, (sg * 0.485, 0.55, 0.62))
    # night-sky cape with a glowing hem, star collar
    B('cape_top', (0.8, 0.86, 0.05), navy, (0, 0.2, 0.935), bev=0.02)
    B('cape_back', (0.9, 0.06, 0.62), navy, (0, 0.79, 0.6), bev=0.02)
    for sg, n in LR:
        B('cape_side_' + n, (0.05, 0.6, 0.4), navy, (sg * 0.5, 0.4, 0.74), bev=0.02)
        P('cape_trim_' + n, (0.06, 0.62, 0.05), night, (sg * 0.505, 0.4, 0.53))
    P('cape_trim_b', (0.92, 0.07, 0.05), night, (0, 0.795, 0.3))
    B('collar', (0.8, 0.5, 0.1), night, (0, -0.1, 0.93), bev=0.02)
    # ---- glowing body pattern (rarity 5): own segment so it flickers
    SG('glow', 'body', (0, 0.3, 0.6))
    for i, (x, y) in enumerate(((-0.24, 0.0), (0.2, 0.18), (-0.08, 0.4), (0.27, 0.52), (-0.28, 0.5))):
        P('cape_star_%d' % i, (0.1, 0.1, 0.03), gold, (x, y, 0.972), rot=(0, 0, 45))
        P('cape_star_dot_%d' % i, (0.04, 0.04, 0.03), cyan, (x + 0.12, y + 0.1, 0.972))
    for i, (x, z) in enumerate(((-0.28, 0.72), (0.0, 0.58), (0.26, 0.76), (-0.14, 0.42), (0.2, 0.44))):
        P('back_star_%d' % i, (0.1, 0.03, 0.1), gold, (x, 0.83, z), rot=(0, 45, 0))
    for sg, n in LR:
        for j, (y, z) in enumerate(((0.22, 0.82), (0.42, 0.66), (0.6, 0.8))):
            P('side_star_%s%d' % (n, j), (0.03, 0.09, 0.09), gold if j != 1 else cyan, (sg * 0.535, y, z), rot=(45, 0, 0))
    P('hem_back', (0.9, 0.04, 0.06), cyan, (0, 0.83, 0.33))
    for sg, n in LR:
        P('hem_' + n, (0.04, 0.6, 0.05), cyan, (sg * 0.535, 0.4, 0.57))
    for i, x in enumerate((-0.3, 0.0, 0.3)):
        P('collar_gem_%d' % i, (0.09, 0.04, 0.09), gold if i == 1 else cyan, (x * 0.8, -0.365, 0.93), rot=(0, 45, 0))
    P('pendant', (0.14, 0.05, 0.14), gold, (0, -0.47, 0.8), rot=(0, 45, 0))
    # ---- head
    SG('head', 'body', (0, -0.2, 0.9))
    B('head', (1.08, 0.9, 0.9), fur, (0, -0.25, 1.32))
    B('head_top', (0.8, 0.66, 0.1), fur, (0, -0.25, 1.8), bev=0.03)
    B('muzzle', (0.5, 0.16, 0.3), lav, (0, -0.74, 1.07))
    B('muzzle_top', (0.26, 0.12, 0.1), lav, (0, -0.74, 1.25), bev=0.02)
    B('chin', (0.3, 0.12, 0.08), lav, (0, -0.7, 0.9), bev=0.02)
    B('nose', (0.16, 0.07, 0.1), pink, (0, -0.85, 1.2), bev=0.02, ol=0.01)
    P('mouth_line', (0.03, 0.03, 0.1), dark, (0, -0.83, 1.1))
    for i, (x, z, w) in enumerate(((-0.2, 1.5, 0.22), (0.18, 1.2, 0.18), (0.0, 1.0, 0.3))):
        P('nape_spot_%d' % i, (w, 0.03, 0.16), lav, (x, 0.205, z))
    for sg, n in LR:
        B('cheek_' + n, (0.22, 0.2, 0.3), lav, (sg * 0.5, -0.6, 1.08), bev=0.04)
        P('cheek_tuft_a' + n, (0.1, 0.1, 0.1), lav, (sg * 0.62, -0.58, 1.02))
        P('cheek_tuft_b' + n, (0.08, 0.08, 0.08), lav, (sg * 0.63, -0.56, 1.16))
        P('blush_' + n, (0.16, 0.03, 0.08), pink, (sg * 0.37, -0.71, 1.1))
        P('tooth_' + n, (0.08, 0.04, 0.1), tooth, (sg * 0.045, -0.82, 0.97))
        P('mouth_' + n, (0.1, 0.03, 0.03), dark, (sg * 0.06, -0.83, 1.04))
        for j, (dz, ry) in enumerate(((0.06, 12), (0.0, 0), (-0.06, -12))):
            P('whisker_%s%d' % (n, j), (0.22, 0.02, 0.02), tooth, (sg * 0.7, -0.66, 1.08 + dz), rot=(0, -sg * ry, sg * 12))
        P('temple_' + n, (0.03, 0.2, 0.16), lav, (sg * 0.545, -0.1, 1.5))
        P('temple_b' + n, (0.03, 0.12, 0.1), lav, (sg * 0.545, 0.08, 1.36))
    anime_eyes(0.33 * S, 0.27 * S, -0.705 * S, 1.4 * S, '#5a4ae0', glow='#7fe0ff', lash=True, brow='#8f8ae0',
               brow_tilt=6, brow_dz=0.17)
    P('tiara_band', (0.8, 0.06, 0.05), night, (0, -0.68, 1.845))
    for i, x in enumerate((-0.3, -0.15, 0.0, 0.15, 0.3)):
        P('tiara_%d' % i, (0.08, 0.05, 0.16 if i == 2 else 0.1), gold, (x, -0.68, 1.92 if i == 2 else 1.9))
    for sg, n in LR:
        P('tiara_gem_' + n, (0.06, 0.05, 0.06), cyan, (sg * 0.38, -0.68, 1.845))
    # glowing crescent on the forehead + cheek stars
    SG('glow_h', 'head', (0, -0.71, 1.7))
    for i, (x, z, w, h) in enumerate(((-0.02, 1.78, 0.14, 0.05), (-0.09, 1.72, 0.06, 0.1), (-0.09, 1.66, 0.06, 0.06), (-0.02, 1.61, 0.14, 0.05),
                                      (0.07, 1.8, 0.05, 0.04), (0.07, 1.59, 0.05, 0.04))):
        P('crescent_%d' % i, (w, 0.03, h), gold, (x, -0.715, z))
    for sg, n in LR:
        P('cheek_star_' + n, (0.07, 0.03, 0.07), gold, (sg * 0.46, -0.715, 1.26), rot=(0, 45, 0))
        P('cheek_dot_' + n, (0.035, 0.03, 0.035), cyan, (sg * 0.4, -0.715, 1.2))
    # ---- ears: tall, glowing inside, star rings
    for sg, n in LR:
        SG('ear_' + n, 'head', (sg * 0.3, -0.2, 1.75))
        r = (0, sg * 8, 0)
        B('ear_base_' + n, (0.3, 0.16, 0.3), fur, (sg * 0.31, -0.2, 1.9), rot=r)
        B('ear_' + n, (0.26, 0.14, 0.62), fur, (sg * 0.36, -0.2, 2.3), rot=r)
        B('ear_tip_' + n, (0.2, 0.13, 0.2), navy, (sg * 0.42, -0.2, 2.68), rot=r, bev=0.04)
        P('ear_in_' + n, (0.14, 0.03, 0.56), cyan, (sg * 0.36, -0.275, 2.26), rot=r)
        P('ear_in_tip_' + n, (0.08, 0.03, 0.12), cyan, (sg * 0.41, -0.275, 2.58), rot=r)
        P('ear_ring_' + n, (0.3, 0.18, 0.05), gold, (sg * 0.345, -0.2, 2.12), rot=r)
        P('ear_star_' + n, (0.08, 0.03, 0.08), gold, (sg * 0.425, -0.27, 2.7), rot=(0, 45 + sg * 8, 0))
        for j in range(2):
            P('ear_back_%s%d' % (n, j), (0.1, 0.03, 0.1), lav, (sg * (0.35 + j * 0.03), -0.125, 2.2 + j * 0.24), rot=r)
    # ---- legs with glowing bracelets
    for sg, n in LR:
        SG('leg_f' + n, 'body', (sg * 0.24, -0.28, 0.32))
        B('arm_' + n, (0.22, 0.22, 0.28), fur, (sg * 0.24, -0.3, 0.22))
        B('paw_f' + n, (0.26, 0.3, 0.12), lav, (sg * 0.24, -0.36, 0.06), bev=0.03)
        P('band_f' + n, (0.25, 0.25, 0.05), gold, (sg * 0.24, -0.3, 0.16))
        for j in (-1, 0, 1):
            P('toe_f%s%d' % (n, j + 1), (0.06, 0.05, 0.07), navy, (sg * 0.24 + j * 0.085, -0.515, 0.05))
        SG('leg_b' + n, 'body', (sg * 0.4, 0.42, 0.38))
        B('thigh_' + n, (0.24, 0.5, 0.42), fur, (sg * 0.5, 0.42, 0.3))
        B('foot_' + n, (0.26, 0.66, 0.13), lav, (sg * 0.5, 0.16, 0.065), bev=0.03)
        P('pad_' + n, (0.14, 0.03, 0.07), pink, (sg * 0.5, -0.175, 0.07))
        P('band_b' + n, (0.28, 0.06, 0.15), gold, (sg * 0.5, 0.3, 0.07))
        P('thigh_star_' + n, (0.03, 0.1, 0.1), cyan, (sg * 0.625, 0.42, 0.34), rot=(45, 0, 0))
        for j in (-1, 0, 1):
            P('toe_b%s%d' % (n, j + 1), (0.06, 0.05, 0.07), navy, (sg * 0.5 + j * 0.085, -0.19, 0.11))
    # ---- tail: fluffy pom with a glowing core
    SG('tail', 'body', (0, 0.8, 0.55))
    B('tail', (0.36, 0.3, 0.36), fur, (0, 0.96, 0.62))
    B('tail_b', (0.24, 0.16, 0.24), fur, (0, 1.14, 0.66), bev=0.03)
    P('tail_glow', (0.14, 0.06, 0.14), gold, (0, 1.24, 0.66), rot=(0, 45, 0))
    P('tail_tuft_a', (0.12, 0.1, 0.12), lav, (0.1, 1.1, 0.82))
    P('tail_tuft_b', (0.1, 0.1, 0.1), lav, (-0.14, 1.08, 0.5))
    # ---- floating parts (rarity 5): a little crescent moon and stars orbiting the body
    SG('orbit', 'root', (0, 0.1, 1.5))
    for i, (dx, dz, w, h) in enumerate(((0.0, 0.16, 0.2, 0.08), (-0.1, 0.08, 0.1, 0.1), (-0.14, 0.0, 0.1, 0.1), (-0.1, -0.08, 0.1, 0.1),
                                        (0.0, -0.16, 0.2, 0.08), (0.12, 0.2, 0.08, 0.06), (0.12, -0.2, 0.08, 0.06))):
        P('moon_%d' % i, (w * 1.6, 0.14, h * 1.6), gold, (1.2 + dx * 1.6, 0.1, 1.9 + dz * 1.6))
    for i in range(6):
        a = math.radians(i * 60 + 100)
        P('orbit_star_%d' % i, (0.11, 0.11, 0.11), cyan if i % 2 else gold,
          (math.cos(a) * 1.2, 0.1 + math.sin(a) * 1.2, 1.1 + (i % 3) * 0.42), rot=(45, 45, 0))
    # ---- FX segments (not exported with the model): yellow aura ring at the feet + drifting motes
    SG('fxs_aura', 'root', (0, 0.1, 0.03))
    for i in range(14):
        a = math.radians(i * 360 / 14)
        P('aura_%d' % i, (0.2, 0.12, 0.05 if i % 2 else 0.1), aura, (math.cos(a) * 1.25, 0.1 + math.sin(a) * 1.25, 0.04),
          rot=(0, 0, math.degrees(a) + 90))
    for i in range(8):
        a = math.radians(i * 45 + 20)
        P('aura_in_%d' % i, (0.08, 0.08, 0.04), aura, (math.cos(a) * 0.95, 0.1 + math.sin(a) * 0.95, 0.03), rot=(0, 0, 45))
    SG('fxs_motes', 'root', (0, 0.1, 1.2))
    for i in range(10):
        a = math.radians(i * 36 + 10)
        rr = 1.5 + (i % 3) * 0.25
        P('mote_%d' % i, (0.07, 0.07, 0.07), gold if i % 2 else cyan,
          (math.cos(a) * rr, 0.1 + math.sin(a) * rr, 0.4 + (i * 7 % 10) * 0.22), rot=(45, 45, 0))
    assemble()
    marker('Head', 'head', V((0, -0.25, 1.32)))
    marker('Chest', 'body', V((0, -0.37, 0.6)))
    marker('Hit', 'body', V((0, 0.15, 0.8)))
    anims()
    build_fx()
    return bake_actions()


def anims():
    # Reveal (45 f = 1.5 s): flash in the bush -> shoots up spinning -> hangs in the air in a star pose
    # (shockwave + light rings) -> drops, lands -> deep bow
    R = 'Reveal'
    clip(R, 45)
    k(R, 'root', 1, loc=(0, BUSH_D, 0.8), scale=0.0, rot=(0, 0, -360), ease='CONSTANT')
    k(R, 'root', 5, loc=(0, BUSH_D, 0.8), scale=0.0, rot=(0, 0, -360))
    k(R, 'root', 9, loc=(0, BUSH_D * 0.5, HOVER + 0.5), scale=1.2, rot=(0, 0, -180))
    k(R, 'root', 13, loc=(0, 0.2, HOVER), scale=1.0, rot=(0, 0, 0))
    k(R, 'root', 20, loc=(0, 0.1, HOVER + 0.25), scale=1.0, rot=(0, 0, 0))
    k(R, 'root', 27, loc=(0, 0, HOVER), scale=1.0)
    k(R, 'root', 32, loc=(0, 0, 0), ease='LINEAR')
    k(R, 'root', 45, loc=(0, 0, 0), scale=1.0, rot=(0, 0, 0))
    # star pose in the air
    k(R, 'body', 9, rot=(0, 0, 0), scale=1.0)
    k(R, 'body', 14, rot=(-18, 0, 0))
    k(R, 'body', 27, rot=(-18, 0, 0), scale=1.0)
    k(R, 'body', 32, rot=(6, 0, 0), scale=(1.15, 1.15, 0.8))
    k(R, 'body', 35, rot=(0, 0, 0), scale=1.0)
    k(R, 'body', 39, rot=(24, 0, 0))
    k(R, 'body', 42, rot=(24, 0, 0))
    k(R, 'body', 45, rot=(0, 0, 0))
    k(R, 'head', 9, rot=(0, 0, 0))
    k(R, 'head', 14, rot=(-14, 0, 0))
    k(R, 'head', 27, rot=(-14, 0, 0))
    k(R, 'head', 35, rot=(0, 0, 0))
    k(R, 'head', 39, rot=(26, 0, 0))
    k(R, 'head', 42, rot=(26, 0, 0))
    k(R, 'head', 45, rot=(0, 0, 0))
    for n, s in (('L', -1), ('R', 1)):
        k(R, 'leg_f' + n, 9, rot=(0, 0, 0))
        k(R, 'leg_f' + n, 14, rot=(-120, s * 40, 0))
        k(R, 'leg_f' + n, 27, rot=(-120, s * 40, 0))
        k(R, 'leg_f' + n, 33, rot=(0, 0, 0))
        k(R, 'leg_b' + n, 9, rot=(0, 0, 0))
        k(R, 'leg_b' + n, 14, rot=(35, s * 15, 0))
        k(R, 'leg_b' + n, 27, rot=(35, s * 15, 0))
        k(R, 'leg_b' + n, 32, rot=(0, 0, 0))
        k(R, 'ear_' + n, 9, rot=(30, 0, 0))
        k(R, 'ear_' + n, 14, rot=(-15, s * 28, 0))
        k(R, 'ear_' + n, 27, rot=(-15, s * 28, 0))
        k(R, 'ear_' + n, 32, rot=(25, 0, 0))
        k(R, 'ear_' + n, 35, rot=(0, 0, 0))
        k(R, 'ear_' + n, 39, rot=(42, s * 10, 0))
        k(R, 'ear_' + n, 42, rot=(42, s * 10, 0))
        k(R, 'ear_' + n, 45, rot=(0, 0, 0))
    k(R, 'leg_fR', 35, rot=(0, 0, 0))
    k(R, 'leg_fR', 39, rot=(-80, 0, -20))
    k(R, 'leg_fR', 42, rot=(-80, 0, -20))
    k(R, 'leg_fR', 45, rot=(0, 0, 0))
    k(R, 'tail', 13, rot=(0, 0, 0))
    k(R, 'tail', 20, rot=(0, 0, 30))
    k(R, 'tail', 27, rot=(0, 0, -30))
    k(R, 'tail', 34, rot=(0, 0, 0))
    k(R, 'orbit', 5, rot=(0, 0, 0), scale=0.4)
    k(R, 'orbit', 13, rot=(0, 0, 240), scale=1.3)
    k(R, 'orbit', 27, rot=(0, 0, 600), scale=1.3, ease='LINEAR')
    k(R, 'orbit', 45, rot=(0, 0, 720), scale=1.0)
    k(R, 'glow', 13, scale=1.0)
    k(R, 'glow', 20, scale=1.06)
    k(R, 'glow', 27, scale=1.0)
    k(R, 'fxs_aura', 1, scale=0.0)
    k(R, 'fxs_aura', 31, scale=0.0)
    k(R, 'fxs_aura', 36, scale=1.3, rot=(0, 0, -60))
    k(R, 'fxs_aura', 45, scale=1.0, rot=(0, 0, 0))
    k(R, 'fxs_motes', 1, scale=0.0)
    k(R, 'fxs_motes', 12, scale=0.0)
    k(R, 'fxs_motes', 20, scale=1.0, rot=(0, 0, -90))
    k(R, 'fxs_motes', 45, scale=1.0, rot=(0, 0, 0))
    blink(R, (37,))
    # Idle (60 f loop): breathing, blink, ear twitch, orbiting moon and stars, flickering pattern, turning aura
    I = 'Idle'
    clip(I, 60)
    k(I, 'orbit', 1, loc=(0, 0, 0), rot=(0, 0, 0))
    k(I, 'orbit', 30, loc=(0, 0, 0.15), rot=(0, 0, 180), ease='LINEAR')
    k(I, 'orbit', 60, loc=(0, 0, 0), rot=(0, 0, 360), ease='LINEAR')
    k(I, 'body', 1, scale=1.0)
    k(I, 'body', 30, scale=(1.03, 1.03, 1.04))
    k(I, 'body', 60, scale=1.0)
    for f, a in ((1, 0), (40, 0), (43, 15), (46, 0), (60, 0)):
        k(I, 'ear_R', f, rot=(a, 0, 0))
    for f, a in ((1, 0), (20, 6), (40, 0), (60, 0)):
        k(I, 'head', f, rot=(0, a, 0))
    for f, a in ((1, 0), (10, 20), (14, -15), (18, 0), (60, 0)):
        k(I, 'tail', f, rot=(0, 0, a))
    blink(I, (24, 52))
    pulse(I, 'glow', 20, 0.03)
    pulse(I, 'glow_h', 20, 0.18)
    k(I, 'fxs_aura', 1, rot=(0, 0, 0))
    k(I, 'fxs_aura', 1, rot=(0, 0, 0), ease='LINEAR')
    k(I, 'fxs_aura', 60, rot=(0, 0, -180), ease='LINEAR')   # ring has 2-fold symmetry: 180 deg loops
    k(I, 'fxs_motes', 1, rot=(0, 0, 0), loc=(0, 0, 0))
    k(I, 'fxs_motes', 30, rot=(0, 0, 0), loc=(0, 0, 0.3))
    k(I, 'fxs_motes', 60, rot=(0, 0, 0), loc=(0, 0, 0))


def build_fx():
    fx(True)
    flash = neon('mr_flash', '#fff6b0', 4.0)
    spark = neon('mr_spark', '#ffe55a', 3.5)
    ringm = neon('mr_ring', '#7fe0ff', 3.0)
    base = G.root.location
    c = base + Vector((0, BUSH_D, 1.2))
    h = base + Vector((0, 0.2, HOVER + 1.3))
    # flash inside the bush
    core = blk('flash_core', (0.6, 0.6, 0.6), flash, (0, 0, 0), bev=0.1)
    fxkey(core, 1, loc=c, scale=0, alpha=1, rot=(0, 0, 0))
    fxkey(core, 3, scale=0.6, alpha=1)
    fxkey(core, 6, scale=2.6, alpha=0.9, rot=(45, 45, 0))
    fxkey(core, 11, scale=3.2, alpha=0)
    # shockwave on the ground when it reaches the hover point
    wave = torus('shockwave', 0.6, 0.07, flash, 16, 4)
    g0 = base + Vector((0, 0.2, 0.1))
    fxkey(wave, 1, loc=g0, scale=0, alpha=1)
    fxkey(wave, 12, scale=0.3, alpha=1)
    fxkey(wave, 24, scale=5.0, alpha=0)
    # two light rings around the hovering rabbit
    for i, (rx, f0) in enumerate(((70, 13), (110, 16))):
        rg = torus('light_ring_%d' % i, 1.4, 0.05, ringm if i else flash, 20, 4)
        fxkey(rg, 1, loc=h, scale=0, alpha=1, rot=(rx, 0, 0))
        fxkey(rg, f0, scale=0.2, alpha=1, rot=(rx, 0, 0))
        fxkey(rg, f0 + 8, scale=1.0, alpha=1, rot=(rx, 0, 120))
        fxkey(rg, 28, scale=1.25, alpha=0.8, rot=(rx, 0, 300))
        fxkey(rg, 33, scale=1.6, alpha=0)
    # star burst from the hover point
    for i in range(12):
        a = math.radians(i * 30)
        s_ = star('spark_%d' % i, 0.16, 0.06, 4, 0.05, spark)
        p1 = h + Vector((math.cos(a) * 2.4, math.sin(a) * 1.0, math.sin(a * 2) * 0.9 + math.cos(a) * 0.3))
        fxkey(s_, 1, loc=h, scale=0, alpha=1)
        fxkey(s_, 12, loc=h, scale=0.4, alpha=1)
        fxkey(s_, 22, loc=p1, scale=1.0, alpha=1, rot=(0, 0, 180))
        fxkey(s_, 34, loc=p1 - Vector((0, 0, 0.8)), scale=0.0, alpha=0, rot=(0, 0, 360))
    # landing ring (rarity yellow)
    land = torus('land_ring', 0.7, 0.06, spark, 16, 4)
    fxkey(land, 1, loc=base + Vector((0, 0, 0.08)), scale=0, alpha=1)
    fxkey(land, 31, scale=0.3, alpha=1)
    fxkey(land, 42, scale=3.2, alpha=0)
    fx(False)
