# Biome 5 - Amber Savanna: golden grass, acacias, warm stones
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 5
GROUND = '#d9b85c'
SKY = '#ffe9c4'
THEME = dict(bits=['#ecc85a', '#c89a40'], dust='#ecd49c', glow='#ffb020', splash='#ffe9b0', bit_name='сухая трава')
BUSH_NAME = 'куртина сухой золотой травы с молодой акацией, термитником и тёплыми камнями'


def bush():
    B = begin_bush(NN)
    g1 = mat('grass', '#ecc85a')
    g2 = mat('grass2', '#d8a83e')
    g3 = mat('grass3', '#f6de8a')
    earth = mat('earth', '#c08a52')
    earth2 = mat('earth2', '#a06e3c')
    rock = mat('rock', '#d89a6a')
    rock2 = mat('rock2', '#b87a50')
    leaf = mat('leaf', '#8fb840')
    leaf2 = mat('leaf2', '#6e9a30')
    wood = mat('wood', '#8a623e')
    seed = mat('seed', '#fff4c8')
    amber = mat('amber', '#ffb020', 'neon', 1.8)
    # grass mounds
    for i, (x, y, w, d, h) in enumerate(((0, 0.2, 3.6, 2.4, 1.3), (-2.2, 0.0, 2.2, 1.9, 1.0), (2.2, 0.3, 2.3, 1.9, 1.1))):
        part('big', (x, y, 0.2), 'mound_%d' % i)
        b('mound', (w, d, h), g2, (x, y, h / 2 + 0.05), bev=0.12)
        b('mound_top', (w * 0.72, d * 0.72, 0.4), g1, (x, y + 0.05, h + 0.2), bev=0.1)
    # tall grass blades in tufts: stepped, leaning
    k_ = 0
    for (cx, cy, n, h0) in ((-3.0, 0.2, 5, 2.3), (-1.7, 0.9, 5, 3.1), (-0.4, 0.5, 6, 3.6), (1.0, 0.9, 5, 3.3), (2.4, 0.6, 5, 2.8), (3.2, -0.1, 4, 2.0),
                            (-1.0, -0.8, 5, 2.2), (0.9, -0.9, 5, 2.4)):
        part('small', (cx, cy, 0.9), 'tuft_%d' % k_)
        for i in range(n):
            x = cx + (i - (n - 1) / 2) * 0.26
            h = h0 - 0.4 * abs(i - (n - 1) / 2)
            lean = (i - (n - 1) / 2) * 7
            b('blade', (0.16, 0.14, h), (g1, g3, g2)[i % 3], (x + math.sin(math.radians(lean)) * h / 2, cy + 0.1 * (i % 2), 0.9 + h / 2), rot=(0, lean, 0), bev=0.03)
            p('blade_tip', (0.1, 0.1, 0.3), seed, (x + math.sin(math.radians(lean)) * (h + 0.1), cy + 0.1 * (i % 2), 0.9 + h + 0.1), rot=(0, lean, 0))
        k_ += 1
    # young acacia: thin trunk, flat stepped canopy
    part('big', (-0.9, 1.0, 1.0), 'acacia')
    b('acacia_trunk', (0.3, 0.3, 2.6), wood, (-0.9, 1.0, 2.2), rot=(0, 6, 0), bev=0.05)
    b('acacia_branch', (0.9, 0.2, 0.2), wood, (-0.4, 1.0, 3.4), rot=(0, -30, 0), bev=0.04)
    part('big', (-0.7, 1.0, 3.6), 'canopy')
    b('canopy', (2.8, 1.8, 0.4), leaf, (-0.6, 1.0, 3.9), bev=0.1)
    b('canopy_top', (1.9, 1.2, 0.34), leaf2, (-0.5, 1.0, 4.26), bev=0.1)
    for i in range(6):
        p('canopy_tuft', (0.4, 0.3, 0.16), leaf2 if i % 2 else leaf, (-1.7 + i * 0.46, 0.1 + 0.3 * (i % 2), 3.72))
    # termite mound
    part('big', (2.4, -0.6, 0.1), 'termite')
    b('termite', (1.0, 0.9, 1.5), earth, (2.4, -0.6, 0.75), bev=0.14)
    b('termite_mid', (0.7, 0.64, 0.9), earth, (2.45, -0.6, 1.9), bev=0.12)
    b('termite_top', (0.4, 0.4, 0.6), earth2, (2.5, -0.6, 2.6), bev=0.1)
    for i, (dx, dz) in enumerate(((-0.2, 0.5), (0.2, 1.0), (0.0, 1.7), (-0.1, 2.3))):
        p('termite_hole', (0.14, 0.05, 0.14), mat('hole', '#5a3a22'), (2.4 + dx, -1.07 + (0.14 if dz > 1.4 else 0) + (0.12 if dz > 2 else 0), dz))
    # warm stones with amber veins
    for i, (x, y, s) in enumerate(((-2.6, -1.0, 1.0), (-1.6, -1.3, 0.6), (0.4, -1.5, 0.7))):
        part('big', (x, y, 0.1), 'stone_%d' % i)
        b('stone', (1.2 * s, 1.0 * s, 0.9 * s), rock if i % 2 == 0 else rock2, (x, y, 0.45 * s), rot=(0, 0, 12 * (1 - i)), bev=0.14)
        b('stone_top', (0.8 * s, 0.66 * s, 0.24 * s), rock, (x, y, 0.98 * s), rot=(0, 0, 12 * (1 - i)), bev=0.08)
        p('amber_vein', (0.4 * s, 0.05, 0.1 * s), amber, (x, y - 0.5 * s, 0.5 * s), rot=(0, 20, 0))
        p('amber_vein', (0.1 * s, 0.05, 0.3 * s), amber, (x + 0.2 * s, y - 0.5 * s, 0.36 * s))
    # small flowers / seed heads
    for i, (x, y, z) in enumerate(((-2.0, -0.3, 1.1), (0.2, -0.6, 1.5), (1.6, -0.3, 1.2), (3.0, 0.9, 1.0), (-3.2, 0.9, 0.9))):
        part('small', (x, y, z), 'seedhead_%d' % i)
        b('stalk', (0.07, 0.07, 0.7), g2, (x, y, z + 0.35), bev=0.01)
        b('seedhead', (0.26, 0.26, 0.26), seed, (x, y, z + 0.8), rot=(45, 45, 0), bev=0.05)
        p('seedhead_core', (0.12, 0.12, 0.12), mat('orange', '#ff9a3c'), (x, y, z + 0.8), rot=(45, 45, 0))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def watchful_meerkat(row):
    a = start(row, dict(main='#d8b078', belly='#f6e6c0', dark='#6a4a30', accent='#b88a54'), 2.0)
    B, Hd = sit(bw=0.62, bd=0.6, bh=1.06, hw=0.86, hd=0.74, hh=0.72, arm=0.34, lw=0.16, foot_l=0.5, thigh=False)
    mz = muzzle(Hd, (0.34, 0.24, 0.22), -0.26, 'belly', nose=(0.14, 0.07, 0.09))
    cheeks(Hd, 'belly', (0.14, 0.14, 0.2), -0.26, whisk=2, tuft=False)
    # dark eye patches (the meerkat mask)
    for sgn, n in LR:
        on(Hd, 'f', sgn * 0.25, 0.1, (0.3, 0.3), mm('dark'), name='eye_patch')
    eyes(Hd, 0.34, 0.25, 0.1, iris='#3a2414', brow='#6a4a30', tilt=12, bdz=0.56)
    ears(Hd, 'round', 'dark', 'pink', x=0.46, h=0.16, w=0.18, lean=30, y=Hd.c.y + 0.1)
    use('body')
    # back bands, belly, standing tall
    for j in range(5):
        on(B, 'k', 0, 0.36 - j * 0.17, (0.5 - 0.02 * j, 0.06), mm('accent'), name='back_band')
        for sgn, n in LR:
            on(B, 'l' if sgn < 0 else 'r', 0.2, 0.36 - j * 0.17, (0.2, 0.06), mm('accent'), name='back_band')
    fluff(Box((0, B.front - 0.07, B.c.z + 0.1), (B.s.x * 0.72, 0.1, 0.8)), 'f', mm('belly'), 3, 1.0, 0.4)
    on(Hd, 't', 0, 0.1, (0.3, 0.3), mm('accent'), name='head_patch', th=0.12)
    for sgn, n in LR:
        p('shoulder', (0.12, 0.2, 0.16), mm('accent'), (sgn * (B.s.x / 2 + 0.02), B.front + 0.16, B.top - 0.26))
        p('hip', (0.14, 0.3, 0.3), mm('main'), (sgn * (B.s.x / 2 + 0.04), 0.36, 0.42))
        p('freckle', (0.03, 0.03, 0.03), mm('dark'), (sgn * 0.1, mz.front - 0.008, mz.c.z + 0.0))
    tail_kit('long', 'body', (0, a.tail_j[1] - 0.12, 0.3), 'main', 'dark', n=2, size=0.1, dark='accent')
    return finish(a)


def gazelle(row):
    a = start(row, dict(main='#e0a45a', belly='#fff6e4', dark='#5a3a24', accent='#8a5a32', horn='#4a3a30'), 3.3)
    B, Hd = quad(bw=0.72, bl=1.15, bh=0.6, legh=0.84, lw=0.16, hw=0.96, hd=0.82, hh=0.84, neck=0.3, hoof='dark', head_fwd=0.3)
    mz = muzzle(Hd, (0.38, 0.28, 0.26), -0.26, 'belly', nose=(0.14, 0.07, 0.09))
    cheeks(Hd, 'belly', (0.16, 0.14, 0.22), -0.26, whisk=0)
    for sgn, n in LR:
        on(Hd, 'f', sgn * 0.42, -0.02, (0.08, 0.4), mm('accent'), name='face_stripe')
    eyes(Hd, 0.36, 0.24, 0.12, iris='#3a2414', lash=True, brow='#5a3a24', tilt=8)
    ears(Hd, 'long', 'main', 'pink', tip='dark', x=0.48, h=0.4, w=0.2, lean=50)
    # lyre-shaped ringed horns
    use('head')
    for sgn, n in LR:
        x0 = sgn * 0.2
        for j in range(5):
            t = j / 4.0
            b('horn', (0.13 - 0.015 * j, 0.13 - 0.015 * j, 0.24), mm('horn'), (x0 + sgn * 0.16 * math.sin(t * 3.0), Hd.c.y + 0.06 * j, Hd.top + 0.1 + j * 0.2), rot=(-8, sgn * 30 * math.cos(t * 3.0), 0), bev=0.03)
            p('horn_ring', (0.15 - 0.015 * j, 0.15 - 0.015 * j, 0.04), mm('accent'), (x0 + sgn * 0.16 * math.sin(t * 3.0), Hd.c.y + 0.06 * j, Hd.top + 0.2 + j * 0.2))
    use('body')
    # the dark side stripe and white belly
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', 0, -0.16, (B.s.y * 0.9, 0.12), mm('dark'), name='side_stripe', th=0.04)
        on(B, 'l' if sgn < 0 else 'r', 0, -0.36, (B.s.y * 0.9, 0.16), mm('belly'), name='side_white', th=0.04)
        on(a.bx['rump'], 'l' if sgn < 0 else 'r', 0, -0.2, (0.3, 0.12), mm('dark'), name='side_stripe', th=0.035)
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.8, 0.3)
    on(a.bx['rump'], 'k', 0, 0.1, (0.5, 0.4), mm('belly'), name='rump_patch')
    on(B, 't', 0, 0, (0.14, B.s.y * 0.9), mm('accent'), name='back_stripe')
    for ft in a.bx['feet']:
        p('sock', (ft.s.x - 0.02, ft.s.y - 0.04, 0.2), mm('belly'), (ft.c.x, ft.c.y + 0.02, ft.top + 0.12))
        p('knee', (0.06, 0.04, 0.08), mm('accent'), (ft.c.x, ft.front + 0.02, 0.6))
    tail_kit('stub', 'body', a.tail_j, 'belly', 'dark', size=0.2)
    return finish(a)


def savanna_ostrich(row):
    a = start(row, dict(main='#3a3440', belly='#ffffff', dark='#24202a', accent='#f4a8b8', leg='#f0b0b8', beak='#ffc93c', beak_tip='#f08a24'), 4.3)
    B, Hd = bird(bw=1.2, bl=1.3, bh=1.0, legh=1.4, lw=0.16, hw=0.86, hd=0.78, hh=0.78, neck=1.2, beak=(0.42, 0.4, 0.16),
                 wing=(0.18, 0.9, 0.62), ntail=5, tail_l=0.5, tail_mat='belly', head_mat='accent')
    use('head')
    # pink neck, fluffy white collar, tuft on the head
    b('neck_skin', (0.4, 0.4, 1.2), mm('accent'), (0, Hd.c.y + 0.06, Hd.bot - 0.56), bev=0.05)
    for j in range(3):
        p('neck_ring', (0.44, 0.44, 0.05), mm('leg'), (0, Hd.c.y + 0.06, Hd.bot - 0.2 - j * 0.34))
    b('collar', (0.8, 0.8, 0.22), mm('belly'), (0, Hd.c.y + 0.1, Hd.bot - 1.16), bev=0.07)
    for i in range(3):
        p('head_tuft', (0.08, 0.08, 0.2 + 0.06 * (i % 2)), mm('main'), ((i - 1) * 0.12, Hd.c.y, Hd.top + 0.1))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.2))
    eyes(Hd, 0.4, 0.25, 0.14, iris='#6a3a1c', lash=True, brow='#24202a', tilt=10)
    use('body')
    # white wing and tail plumes, feather rows (pattern, rarity 3)
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(4):
            b('plume', (0.16, 0.3, 0.22), mm('belly'), (sgn * (B.s.x / 2 + 0.08), B.c.y + 0.5, B.c.z + 0.26 - j * 0.2), rot=(-20, 0, 0), bev=0.04)
    use('body')
    for i in range(3):
        for j in range(3):
            p('back_feather', (0.3, 0.3, 0.05), mm('dark'), ((i - 1) * 0.34, B.c.y - 0.34 + j * 0.34, B.top + 0.03))
    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('belly'), 3, 0.9, 0.3)
    accessory('bow', Box((0, Hd.c.y + 0.06, Hd.bot - 1.0), (0.5, 0.5, 0.2)), '#ffb020', '#e8782a', z=Hd.bot - 0.98)
    use('body')
    for sgn, n in LR:
        for j in range(4):
            p('side_feather', (0.05, 0.26, 0.22), mm('dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.42 + j * 0.2, B.c.z - 0.3))
            p('rump_plume', (0.2, 0.2, 0.2), mm('belly'), (sgn * (0.16 + 0.14 * (j % 2)), B.back + 0.3 + 0.05 * j, B.c.z + 0.3 - 0.14 * j))
    return finish(a)


def hyena(row):
    a = start(row, dict(main='#c8a878', belly='#ecd8b0', dark='#4a3830', accent='#8a6a4a', **{'*glow': '#ffb020'}), 2.3)
    B, Hd = quad(bw=0.96, bl=1.3, bh=0.78, legh=0.56, lw=0.26, hw=1.16, hd=0.94, hh=0.94, toe='dark', hump=0.22, sock='dark', head_fwd=0.28)
    mz = muzzle(Hd, (0.5, 0.3, 0.3), -0.26, 'dark', nose=(0.2, 0.09, 0.12), fangs=0, teeth=1, tongue=True)
    cheeks(Hd, 'belly', (0.26, 0.22, 0.28), -0.25, whisk=2, wmat='dark')
    eyes(Hd, 0.34, 0.25, 0.1, iris='#b06a10', glow='#ffb020', brow='#4a3830', tilt=14, bdz=0.54)
    ears(Hd, 'round', 'dark', 'pink', x=0.42, h=0.36, w=0.36, lean=14)
    use('head')
    for i in range(4):
        b('mane', (0.2, 0.2, 0.24 + 0.05 * (i % 2)), mm('dark'), (0, Hd.c.y - 0.1 + i * 0.2, Hd.top + 0.1), bev=0.05)
    use('body')
    hp = a.bx['hump']
    for i in range(5):
        b('mane', (0.2, 0.2, 0.26 - 0.03 * i), mm('dark'), (0, B.front + 0.1 + i * 0.22, (hp.top if i < 3 else B.top) + 0.1), bev=0.05)
    spots(B, 'lr', 8, mm('accent'), 0.15, seed=4, name='spot')
    spots(a.bx['rump'], 'tlr', 6, mm('accent'), 0.13, seed=6, name='spot')
    spots(hp, 'lr', 2, mm('dark'), 0.12, seed=2, name='spot')
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)
    for ft in a.bx['feet']:
        p('leg_spot', (0.1, 0.03, 0.1), mm('accent'), (ft.c.x, ft.c.y - 0.15, 0.44))
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.16)
    # rarity 4: glowing amber spots, glowing mane tips, ember sparks
    glow_marks(B, ('l', 'r'), 3, 'glow', style='star', size=0.15)
    use('glow')
    for i in range(4):
        p('mane_glow', (0.12, 0.12, 0.1), mm('glow'), (0, B.front + 0.1 + i * 0.22, (hp.top if i < 3 else B.top) + 0.3 - 0.03 * i))
    use('tail')
    p('tail_glow', (0.14, 0.14, 0.14), mm('glow'), (0, a.tail_j[1] + 0.42, a.tail_j[2] - 0.2), rot=(45, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        on(Hd, 'f', sgn * 0.4, -0.3, (0.08, 0.08), mm('glow'), th=0.035, name='cheek_star', rot=(0, 45, 0))
        p('ear_glow', (0.2, 0.05, 0.06), mm('glow'), (sgn * 0.42 * Hd.s.x, Hd.c.y - 0.08, Hd.top + 0.3))
    on(Hd, 'f', 0, 0.38, (0.12, 0.12), mm('glow'), th=0.035, name='fore_star', rot=(0, 45, 0))
    aura_kit(1.4, 4, motes=8, mote_col='glow', height=1.7)
    return finish(a)


def sunlion(row):
    a = start(row, dict(main='#f2b84a', belly='#fff2cc', dark='#b8742a', accent='#ff8a2a', mane='#ff9a2a', mane2='#ffc83c',
                        **{'*glow': '#ffd21a', '*glow2': '#ff7a1a'}), 2.75)
    B, Hd = quad(bw=1.04, bl=1.42, bh=0.84, legh=0.56, lw=0.32, hw=1.2, hd=0.98, hh=0.98, toe='dark', leg_fl=0.5, hump=0.1)
    mz = muzzle(Hd, (0.52, 0.28, 0.32), -0.26, 'belly', nose=(0.22, 0.1, 0.13), nose_mat='pink', top='main', fangs=1)
    cheeks(Hd, 'belly', (0.28, 0.24, 0.3), -0.25, whisk=3)
    eyes(Hd, 0.33, 0.25, 0.1, iris='#c86a10', glow='#ffd21a', brow='#b8742a', tilt=-10)
    ears(Hd, 'round', 'main', 'pink', x=0.4, h=0.24, w=0.3, lean=8)
    # sun mane: a ring of stepped blocks round the head with glowing ray tips (the silhouette)
    sg('mane', 'head', (0, Hd.c.y + 0.1, Hd.c.z))
    a.glow.append('mane')
    nm = 14
    for i in range(nm):
        ang = math.radians(i * 360.0 / nm + 90)
        rr = Hd.s.x * 0.62
        cx, cz = math.cos(ang) * rr, Hd.c.z + math.sin(ang) * rr * 0.92
        b('mane', (0.36, 0.5, 0.36), mm('mane' if i % 2 else 'mane2'), (cx, Hd.c.y + 0.14, cz), rot=(0, -math.degrees(ang) + 90, 0), bev=0.07)
        b('mane_ray', (0.2, 0.3, 0.3), mm('accent'), (cx * 1.36, Hd.c.y + 0.16, Hd.c.z + (cz - Hd.c.z) * 1.36), rot=(0, -math.degrees(ang) + 90, 0), bev=0.05)
        p('mane_tip', (0.12, 0.2, 0.2), mm('glow' if i % 2 else 'glow2'), (cx * 1.62, Hd.c.y + 0.16, Hd.c.z + (cz - Hd.c.z) * 1.62), rot=(0, -math.degrees(ang) + 90, 0))
    use('body')
    for j in range(4):
        b('chest_mane', (0.8 - 0.14 * j, 0.16, 0.22), mm('mane' if j % 2 else 'mane2'), (0, B.front - 0.1 - 0.01 * j, B.top - 0.06 - j * 0.2), bev=0.05)
    stripes(B, 't', 4, mm('dark'), 0.1, name='stripe', span=0.8)
    spots(B, 'lr', 6, mm('dark'), 0.14, seed=3, name='spot')
    spots(a.bx['rump'], 'lr', 4, mm('dark'), 0.12, seed=7, name='spot')
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_band', (ft.s.x - 0.02, ft.s.y * 0.6, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.08, 0.38))
        p('paw_glow', (ft.s.x + 0.03, ft.s.y * 0.5, 0.05), mm('glow'), (ft.c.x, ft.c.y + 0.1, ft.top + 0.06))
        p('pad', (ft.s.x * 0.6, 0.03, 0.06), mm('pink'), (ft.c.x, ft.back + 0.012, 0.06))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'mane', size=0.2)
    use('tail')
    p('tail_sun', (0.2, 0.2, 0.2), mm('glow'), (0, a.tail_j[1] + 0.5, a.tail_j[2] - 0.2), rot=(45, 45, 0))
    for i in range(4):
        ang = math.radians(i * 90)
        p('tail_ray', (0.08, 0.08, 0.14), mm('glow2'), (math.cos(ang) * 0.2, a.tail_j[1] + 0.5, a.tail_j[2] - 0.2 + math.sin(ang) * 0.2), rot=(0, -math.degrees(ang) + 90, 0))
    # rarity 5: sun emblem on the flanks and forehead, orbiting little suns, yellow aura
    glow_marks(B, ('l', 'r'), 3, 'glow', style='star', size=0.18, col2='glow2')
    use('glow')
    for i in range(4):
        on(B, 't', 0, -0.36 + i * 0.24, (0.16, 0.16), mm('glow2' if i % 2 else 'glow'), th=0.045, name='glow_star', rot=(0, 0, 45))
    for sgn, n in LR:
        on(a.bx['rump'], 'l' if sgn < 0 else 'r', 0, 0.1, (0.22, 0.22), mm('glow'), th=0.035, name='sun_mark', rot=(45, 0, 0))
        for i in range(4):
            ang = math.radians(i * 90 + 45)
            on(a.bx['rump'], 'l' if sgn < 0 else 'r', math.cos(ang) * 0.3, 0.1 + math.sin(ang) * 0.26, (0.07, 0.07), mm('glow2'), th=0.035, name='sun_ray')
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.c.z + 0.36))
    a.glow.append('glow_h')
    p('fore_sun', (0.14, 0.03, 0.14), mm('glow'), (0, Hd.front - 0.012, Hd.c.z + 0.37), rot=(0, 45, 0))
    for i in range(4):
        ang = math.radians(i * 90)
        p('fore_ray', (0.05, 0.03, 0.05), mm('glow2'), (math.cos(ang) * 0.14, Hd.front - 0.012, Hd.c.z + 0.37 + math.sin(ang) * 0.14))
    use('body')
    orbit_kit((0, 0.2, 1.3), 1.5, 6, 'glow', 'glow2', size=0.14, dz=0.4, shape='flame')
    aura_kit(1.6, 5, motes=10, mote_col='glow', height=1.9, style='rays')
    return finish(a)


def amber_giraffe(row):
    a = start(row, dict(main='#f6d27a', belly='#fff4d0', dark='#c8782a', accent='#e89a3a', horn='#8a5a32',
                        **{'*glow': '#ffb020', '*glow2': '#fff0a0', '*gold': '#ffd84a'}), 5.9)
    B, Hd = quad(bw=0.92, bl=1.3, bh=0.82, legh=1.3, lw=0.22, hw=1.0, hd=0.9, hh=0.9, neck=1.9, hoof='dark', head_fwd=0.34, hump=0.2)
    mz = muzzle(Hd, (0.46, 0.4, 0.34), -0.24, 'belly', nose=None, mouth=True)
    for sgn, n in LR:
        p('nostril', (0.07, 0.03, 0.05), mm('line'), (sgn * 0.1, mz.front - 0.008, mz.c.z + 0.08))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.2))
    eyes(Hd, 0.36, 0.25, 0.12, iris='#8a4a14', glow='#ffb020', lash=True, brow='#c8782a', tilt=8)
    ears(Hd, 'long', 'main', 'pink', tip='dark', x=0.52, h=0.34, w=0.2, lean=62)
    use('head')
    for sgn, n in LR:   # ossicones with amber tips
        b('ossicone', (0.14, 0.14, 0.3), mm('horn'), (sgn * 0.2, Hd.c.y + 0.05, Hd.top + 0.14), bev=0.04)
    # neck: amber patches all the way up + short mane
    nk = Box((0, 0.2 - 1.3 / 2 + 0.2, 1.3 + 0.82 * 0.85 + 1.9 / 2), (0.92 * 0.6, 0.92 * 0.6, 1.9 + 0.82 * 0.3))
    for j in range(6):
        v = -0.4 + j * 0.16
        for f in ('l', 'r', 'f'):
            on(nk, f, 0.14 * (1 if j % 2 else -1), v, (0.22, 0.2), mm('accent' if j % 2 else 'dark'), name='neck_patch')
        b('neck_mane', (0.14, 0.14, 0.24), mm('dark'), (0, nk.back + 0.05, nk.c.z + v * nk.s.z), bev=0.03)
    use('body')
    # amber "crystal" patches: irregular blocks standing proud of the coat
    rnd = __import__('random').Random(5)
    for f in ('l', 'r', 't'):
        for i in range(7):
            u, v = rnd.uniform(-0.4, 0.4), rnd.uniform(-0.36, 0.36)
            on(B, f, u, v, (rnd.uniform(0.16, 0.28), rnd.uniform(0.14, 0.24)), mm('accent' if i % 3 else 'dark'), th=0.05, name='patch')
    for f in ('l', 'r', 'k'):
        for i in range(3):
            on(a.bx['rump'], f, rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), (0.2, 0.2), mm('accent' if i % 2 else 'dark'), th=0.05, name='patch')
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.8, 0.3)
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(4):
            p('leg_patch', (0.14, 0.03, 0.14), mm('accent' if j % 2 else 'dark'), (ft.c.x + 0.03 * (1 if j % 2 else -1), ft.front + 0.06, 0.4 + j * 0.22))
        p('sock', (ft.s.x - 0.02, ft.s.y - 0.04, 0.2), mm('belly'), (ft.c.x, ft.c.y + 0.02, ft.top + 0.12))
        p('hoof_gold', (ft.s.x + 0.02, ft.s.y + 0.02, 0.04), mm('gold'), (ft.c.x, ft.c.y, ft.top + 0.01))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.16)
    # rarity 6: glowing amber gems down the neck and on the flanks, crown, two orbits, red aura
    sg('glow', 'body', tuple(nk.c))
    a.glow.append('glow')
    for j in range(5):
        p('neck_gem', (0.16, 0.06, 0.16), mm('glow' if j % 2 else 'glow2'), (0, nk.front - 0.03, nk.c.z - 0.7 + j * 0.34), rot=(0, 45, 0))
    for sgn, n in LR:
        f = 'l' if sgn < 0 else 'r'
        for i in range(3):
            on(B, f, -0.3 + i * 0.3, 0.0, (0.16, 0.16), mm('glow'), th=0.07, name='flank_gem', rot=(45, 0, 0))
        on(a.bx['rump'], f, 0, 0.0, (0.2, 0.2), mm('glow2'), th=0.07, name='flank_gem', rot=(45, 0, 0))
    use('tail')
    p('tail_gem', (0.16, 0.16, 0.16), mm('glow'), (0, a.tail_j[1] + 0.42, a.tail_j[2] - 0.2), rot=(45, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        b('ossicone_gem', (0.2, 0.2, 0.2), mm('glow'), (sgn * 0.2, Hd.c.y + 0.05, Hd.top + 0.36), rot=(0, 0, 45), bev=0.05)
        on(Hd, 'f', sgn * 0.4, -0.3, (0.08, 0.08), mm('glow'), th=0.035, name='cheek_gem', rot=(0, 45, 0))
    p('fore_gem', (0.16, 0.05, 0.2), mm('glow2'), (0, Hd.front - 0.02, Hd.c.z + 0.36), rot=(0, 45, 0))
    halo_kit(Hd, 'gold', r=0.5, n=10, dz=0.9, kind='crown')
    use('body')
    orbit_kit((0, 0.2, 2.6), 1.3, 6, 'glow', 'glow2', size=0.13, dz=0.6, shape='gem')
    orbit_kit((0, 0.2, 1.5), 1.5, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.2, shape='ring')
    aura_kit(1.4, 6, motes=12, mote_col='glow', mote_r=1.5, height=3.6, style='ring')
    return finish(a)


ANIMALS = dict(watchful_meerkat=watchful_meerkat, gazelle=gazelle, savanna_ostrich=savanna_ostrich, hyena=hyena, sunlion=sunlion,
               amber_giraffe=amber_giraffe)
