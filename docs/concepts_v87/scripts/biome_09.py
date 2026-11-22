# Biome 9 - Mangrove Marshes: warm channels, mangrove roots, backwaters
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 9
GROUND = '#4f8c7c'
SKY = '#d2efe8'
THEME = dict(bits=['#4fa85c', '#8a6a4a'], dust='#b9aa8a', glow='#7af0c0', splash='#a8e4e0', bit_name='листья и брызги')
FOOT = dict(crocodile=1.6, marsh_hydra=1.5)
BUSH_NAME = 'мангровый куст на ходульных корнях над водой, с кроной, стручками и ракушками'


def bush():
    B = begin_bush(NN)
    root = mat('root', '#8a6a4a')
    root2 = mat('root2', '#6e5238')
    l1 = mat('leaf', '#3f9a54')
    l2 = mat('leaf2', '#57b866')
    l3 = mat('leaf3', '#2f7e46')
    water = mat('water', '#5ab8b8')
    water2 = mat('water2', '#8fe0dc')
    mud = mat('mud', '#7a6a52')
    pod = mat('pod', '#b8c85a')
    shell = mat('shell', '#f2e6d8')
    fl = mat('flower', '#ff8ac0')
    gem = mat('gem', '#7af0c0', 'neon', 2.0)
    # water pool + mud bank
    part('big', (0, -0.2, 0.02), 'pool')
    b('pool', (6.6, 3.2, 0.1), water, (0, 0.1, 0.05), bev=0.04)
    for i, (x, y, w) in enumerate(((-1.8, -1.0, 1.0), (1.2, -1.2, 0.7), (2.4, 0.6, 0.8), (-0.4, 0.9, 0.6))):
        p('ripple', (w, 0.14, 0.02), water2, (x, y, 0.11))
    part('big', (0, 0.6, 0.1), 'bank')
    b('bank', (4.0, 1.6, 0.5), mud, (0, 0.7, 0.3), bev=0.12)
    # trunk and stilt roots arching down into the water (the silhouette)
    part('big', (0, 0.6, 1.6), 'trunk')
    b('trunk', (0.7, 0.7, 1.6), root, (0, 0.6, 2.3), bev=0.1)
    p('trunk_ring', (0.74, 0.74, 0.1), root2, (0, 0.6, 2.0))
    k_ = 0
    for ang, ln in ((200, 2.6), (240, 2.2), (300, 2.3), (340, 2.7), (20, 2.2), (160, 2.2), (90, 1.7)):
        part('big', (0, 0.6, 1.8), 'stilt_%d' % k_)
        r = math.radians(ang)
        dx, dy = math.cos(r), math.sin(r)
        b('stilt_up', (0.3, 0.3, 0.9), root, (dx * 0.5, 0.6 + dy * 0.4, 1.7), rot=(dy * 40, -dx * 40, 0), bev=0.06)
        b('stilt_mid', (0.26, 0.26, 1.0), root, (dx * ln * 0.5, 0.6 + dy * ln * 0.36, 1.15), rot=(dy * 55, -dx * 55, 0), bev=0.06)
        b('stilt_low', (0.24, 0.24, 1.0), root2, (dx * ln * 0.86, 0.6 + dy * ln * 0.6, 0.5), rot=(dy * 12, -dx * 12, 0), bev=0.06)
        p('stilt_knee', (0.3, 0.3, 0.2), root2, (dx * ln * 0.74, 0.6 + dy * ln * 0.52, 0.98))
        k_ += 1
    # canopy clumps
    for i, (x, y, z, w, m_) in enumerate(((0, 0.6, 3.5, 3.0, l1), (-1.3, 0.4, 3.1, 2.0, l2), (1.4, 0.7, 3.2, 2.1, l3), (0.2, 0.9, 4.1, 1.8, l2))):
        part('big', (x, y, z - 0.4), 'canopy_%d' % i)
        b('canopy', (w, w * 0.72, 0.8), m_, (x, y, z), bev=0.14)
        b('canopy_top', (w * 0.66, w * 0.5, 0.4), m_, (x + 0.1, y, z + 0.5), bev=0.1)
        for j in range(4):
            p('canopy_leaf', (0.4, 0.14, 0.24), l2 if j % 2 else l3, (x - w * 0.36 + j * w * 0.24, y - w * 0.37, z - 0.2 - 0.08 * (j % 2)))
    # hanging propagules (seed pods), flowers, shells, glowing algae
    for i, (x, y, z) in enumerate(((-1.6, -0.3, 2.6), (-0.4, -0.5, 2.9), (0.9, -0.4, 2.7), (1.9, 0.0, 2.6), (-0.9, 1.2, 2.6))):
        part('small', (x, y, z + 0.4), 'pod_%d' % i)
        b('pod', (0.12, 0.12, 0.8), pod, (x, y, z), bev=0.03)
        p('pod_cap', (0.18, 0.18, 0.12), root2, (x, y, z + 0.42))
        p('pod_tip', (0.08, 0.08, 0.14), mat('pod2', '#8a9a3a'), (x, y, z - 0.46))
    for i, (x, y, z) in enumerate(((-0.9, -0.2, 3.4), (0.8, -0.1, 3.7), (1.9, 0.1, 3.4))):
        part('small', (x, y, z), 'flower_%d' % i)
        for j in range(4):
            ang = math.radians(j * 90 + 45)
            p('petal', (0.2, 0.1, 0.2), fl, (x + math.cos(ang) * 0.16, y - 0.3, z + math.sin(ang) * 0.16), rot=(0, 45, 0))
        p('flower_core', (0.14, 0.14, 0.14), mat('core', '#fff0a0'), (x, y - 0.34, z))
    for i, (x, y, s) in enumerate(((-2.4, -1.0, 1.0), (2.2, -1.1, 0.8), (-0.6, -1.4, 0.7), (3.0, 0.8, 0.8))):
        part('small', (x, y, 0.1), 'shell_%d' % i)
        b('shell', (0.5 * s, 0.4 * s, 0.34 * s), shell, (x, y, 0.2 + 0.1 * s), rot=(0, 0, 30 * i), bev=0.08)
        for j in range(3):
            p('shell_rib', (0.06 * s, 0.42 * s, 0.36 * s), mat('shell2', '#d8c0a8'), (x + (j - 1) * 0.14 * s, y, 0.2 + 0.1 * s), rot=(0, 0, 30 * i))
        p('algae', (0.3 * s, 0.3 * s, 0.05), gem, (x + 0.4 * s, y + 0.1, 0.12))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def mudskipper(row):
    a = start(row, dict(main='#8a8a5a', belly='#e8e0b8', dark='#4a4a30', accent='#5ac8d8', spot='#c8e85a'), 1.6)
    zc = 0.62
    B, Hd = fish(bw=0.9, bl=1.3, bh=0.8, face_h=0.78, fin=(0.44, 0.4, 0.12), tail=(0.12, 0.44, 0.6), dorsal=0.0, zc=zc)
    use('head')
    # eyes sit on top of the head like a frog's; wide mouth
    for sgn, n in LR:
        b('eye_mount', (0.36, 0.34, 0.3), mm('main'), (sgn * 0.26, Hd.c.y + 0.1, Hd.top + 0.08), bev=0.07)
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.1))
        p('gill', (0.04, 0.2, 0.3), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y + 0.16, Hd.c.z))
    p('mouth', (0.7, 0.04, 0.05), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.22))
    p('lip', (0.5, 0.05, 0.06), mm('belly'), (0, Hd.front - 0.015, Hd.c.z - 0.3))
    em = Box((0, Hd.c.y + 0.1, Hd.top + 0.08), (0.9, 0.34, 0.3), 'head')
    eyes(em, 0.8, 0.29, 0.0, iris='#c89a2a', brow=None, w=0.9)
    use('body')
    # tall sail fin on the back with blue spots (the silhouette), speckled sides, stubby arm-fins used as legs
    sg('sail', 'body', (0, B.c.y - 0.1, B.top))
    a.ears.append('sail')
    for i in range(4):
        b('sail', (0.1, 0.26, 0.6 - 0.1 * i), mm('accent'), (0, B.c.y - 0.3 + i * 0.24, B.top + 0.3 - 0.05 * i), bev=0.03)
        p('sail_spot', (0.12, 0.1, 0.1), mm('spot'), (0, B.c.y - 0.3 + i * 0.24, B.top + 0.36 - 0.08 * i))
        p('sail_ray', (0.12, 0.04, 0.5 - 0.1 * i), mm('dark'), (0, B.c.y - 0.18 + i * 0.24, B.top + 0.26 - 0.05 * i))
    use('body')
    spots(B, 'lr', 8, mm('spot'), 0.1, seed=3, name='speck')
    spots(B, 't', 4, mm('dark'), 0.14, seed=5, name='blotch')
    for i in range(4):
        p('belly_band', (B.s.x * 0.7, 0.1, 0.03), mm('belly'), (0, B.front + 0.2 + i * 0.3, B.bot - 0.03))
    for sgn, n in LR:
        for j in range(3):
            p('side_stripe', (0.03, 0.3, 0.06), mm('dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.3 + j * 0.3, B.c.z + 0.2))
            p('side_dot', (0.03, 0.08, 0.08), mm('accent'), (sgn * (B.s.x / 2 + 0.012), B.c.y - 0.2 + j * 0.3, B.c.z - 0.1))
    use('head')
    for sgn, n in LR:
        p('cheek_spot', (0.08, 0.03, 0.08), mm('spot'), (sgn * 0.2, Hd.front - 0.012, Hd.c.z + 0.06))
        p('lid', (0.38, 0.36, 0.06), mm('dark'), (sgn * 0.26, Hd.c.y + 0.1, Hd.top + 0.24))
    use('body')
    for sgn, n in LR:
        use('wing_' + n)
        b('elbow', (0.2, 0.2, 0.3), mm('main'), (sgn * (B.s.x / 2 + 0.06), 0.1, zc - 0.36), bev=0.05)
        for j in range(3):
            p('fin_toe', (0.1, 0.12, 0.06), mm('dark'), (sgn * (B.s.x / 2 + 0.2 + j * 0.12), 0.0, 0.04))
    use('body')
    return finish(a)


def otter(row):
    a = start(row, dict(main='#7a5236', belly='#e8cfa8', dark='#4a2e1c', accent='#a87a52', shell='#f2e6d8', shell2='#ffb0c8'), 2.2)
    B, Hd = sit(bw=0.76, bd=0.74, bh=1.0, hw=1.0, hd=0.86, hh=0.8, arm=0.3, lw=0.2, foot_l=0.6, thigh=True, ntoe=4)
    mz = muzzle(Hd, (0.5, 0.22, 0.3), -0.24, 'belly', nose=(0.2, 0.08, 0.12), teeth=0)
    cheeks(Hd, 'belly', (0.26, 0.22, 0.28), -0.24, whisk=3)
    eyes(Hd, 0.33, 0.25, 0.12, iris='#3a2414', brow='#4a2e1c', tilt=8)
    ears(Hd, 'round', 'main', 'pink', x=0.46, h=0.14, w=0.16, lean=24, y=Hd.c.y + 0.1)
    use('body')
    fluff(Box((0, B.front - 0.07, B.c.z + 0.1), (B.s.x * 0.72, 0.1, 0.8)), 'f', mm('belly'), 4, 1.0, 0.4)
    on(B, 'k', 0, 0, (0.3, B.s.z * 0.9), mm('dark'), name='back_stripe')
    spots(B, 'lr', 6, mm('accent'), 0.12, seed=3, name='fleck')
    for sgn, n in LR:
        p('shoulder', (0.12, 0.22, 0.2), mm('accent'), (sgn * (B.s.x / 2 + 0.02), B.front + 0.2, B.top - 0.26))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('web', (ft.s.x + 0.1, 0.2, 0.04), mm('dark'), (ft.c.x, ft.front + 0.06, 0.03))
    use('body')
    # the clam it holds against its chest (own segment: it taps it in Idle)
    sg('clam', 'body', (0, B.front - 0.16, B.c.z + 0.1))
    b('clam', (0.36, 0.2, 0.3), mm('shell'), (0, B.front - 0.2, B.c.z + 0.1), bev=0.07)
    for j in range(3):
        p('clam_rib', (0.05, 0.22, 0.3), mm('shell2'), ((j - 1) * 0.11, B.front - 0.2, B.c.z + 0.1))
    p('clam_hinge', (0.2, 0.1, 0.06), mm('dark'), (0, B.front - 0.2, B.c.z + 0.27))

    def clam_idle(c, n):
        for x, z in ((1, 0), (n // 6, 0.06), (n // 3, 0), (n // 2, 0.06), (2 * n // 3, 0), (n, 0)):
            k(c, 'clam', x, loc=(0, 0, z * K.S))
    a.extra_idle.append(clam_idle)
    use('body')
    tail_kit('thick', 'body', (0, a.tail_j[1] - 0.06, 0.3), 'main', 'dark', size=0.15)
    return finish(a)


def mangrove_fiddler(row):
    a = start(row, dict(main='#e8603a', belly='#f6c8a0', dark='#8a2e1c', accent='#ffd84a', claw='#ff8a3a', claw2='#fff0d0'), 1.75)
    B, Hd = bug(bw=1.2, bl=0.9, bh=0.6, legh=0.36, hw=0.9, hd=0.3, hh=0.5, nleg=4, leg_w=0.1, leg_span=0.44, claws=0.34, antenna=0,
                head_z=0.02, shell='main', under='belly', leg_mat='dark')
    use('head')
    p('mouth', (0.3, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.14))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.06))
        b('eye_stalk', (0.1, 0.1, 0.4), mm('dark'), (sgn * 0.24, Hd.c.y, Hd.top + 0.16), bev=0.02)
    em = Box((0, Hd.c.y - 0.02, Hd.top + 0.5), (0.9, 0.2, 0.36), 'head')
    for sgn, n in LR:
        b('eye_ball', (0.34, 0.24, 0.36), mm('main'), (sgn * 0.24, Hd.c.y, Hd.top + 0.5), bev=0.07)
    eyes(em, 0.86, 0.27, 0.0, iris='#3a1a10', brow=None, w=0.86)
    use('body')
    # carapace pattern (rarity 3): bands, dots, a little starfish stuck on the shell as accessory
    for j in range(3):
        p('shell_band', (B.s.x * (0.9 - 0.14 * j), 0.1, 0.04), mm('dark'), (0, B.c.y - 0.2 + j * 0.22, B.top + 0.13))
    for sgn, n in LR:
        for j in range(3):
            p('shell_dot', (0.1, 0.1, 0.04), mm('accent'), (sgn * (0.2 + 0.14 * j), B.c.y + 0.06 - 0.1 * j, B.top + 0.135))
        cn('shell_spike', 0.08, 0.2, mm('dark'), (sgn * (B.s.x / 2 - 0.04), B.c.y, B.c.z + 0.1), (sgn * 1, 0, 0.3))
        p('rim', (0.05, B.s.y * 0.8, 0.1), mm('belly'), (sgn * (B.s.x / 2 + 0.01), B.c.y + 0.02, B.bot + 0.1))
    setm('star', '#ffd84a')
    for i in range(5):
        ang = math.radians(i * 72)
        p('starfish_arm', (0.16, 0.08, 0.05), mm('star'), (0.3 + math.cos(ang) * 0.1, B.c.y + 0.16 + math.sin(ang) * 0.1, B.top + 0.16), rot=(0, 0, math.degrees(ang)))
    p('starfish_core', (0.1, 0.1, 0.07), mm('accent'), (0.3, B.c.y + 0.16, B.top + 0.17))
    # the one giant claw (the silhouette) on the right arm
    use('claw_R')
    cx = B.s.x * 0.4 + 0.34 * 0.95
    cy = 0.2 - B.s.y / 2 - 0.34 * 0.55
    b('big_claw', (0.6, 0.9, 0.6), mm('claw'), (cx + 0.2, cy - 0.3, B.c.z + 0.2), bev=0.12)
    b('big_claw_top', (0.3, 0.7, 0.26), mm('claw'), (cx + 0.3, cy - 1.0, B.c.z + 0.4), bev=0.06)
    b('big_claw_low', (0.3, 0.56, 0.2), mm('claw2'), (cx + 0.08, cy - 0.94, B.c.z + 0.02), bev=0.05)
    for j in range(3):
        p('claw_tooth', (0.08, 0.1, 0.08), mm('claw2'), (cx + 0.3, cy - 0.76 - j * 0.16, B.c.z + 0.24))
        p('claw_stud', (0.12, 0.12, 0.05), mm('accent'), (cx + 0.1 + j * 0.14, cy - 0.2, B.c.z + 0.51))
    p('claw_band', (0.64, 0.12, 0.64), mm('dark'), (cx + 0.2, cy + 0.06, B.c.z + 0.2))
    use('body')
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_band', (0.08, 0.13, 0.13), mm('accent'), (j.x + sgn * 0.2, j.y, j.z + 0.04))
        p('leg_hair', (0.04, 0.04, 0.1), mm('belly'), (j.x + sgn * 0.36, j.y, j.z + 0.1))
    use('claw_L')
    for j in range(2):
        p('small_claw_dot', (0.08, 0.08, 0.04), mm('accent'), (-(B.s.x * 0.4 + 0.2 + 0.1 * j), B.front - 0.2, B.c.z + 0.1))
    use('body')
    for i in range(6):
        p('back_bump', (0.12, 0.12, 0.05), mm('belly'), ((i - 2.5) * 0.18, B.c.y + 0.3, B.top + 0.13))
    for sgn, n in LR:
        p('under_band', (0.4, 0.06, 0.03), mm('dark'), (sgn * 0.2, B.c.y, B.bot - 0.08))
    return finish(a)


def crocodile(row):
    a = start(row, dict(main='#5a9a52', belly='#f0e8b0', dark='#2f6a3a', accent='#8fc86a', horn='#fff6e0', **{'*glow': '#7af0c0'}), 1.5)
    B, Hd = quad(bw=1.2, bl=2.0, bh=0.6, legh=0.22, lw=0.28, hw=1.1, hd=0.8, hh=0.72, head_up=0.26, toe='horn', head_fwd=0.5, leg_fl=0.5,
                 ntoe=4, leg_back_x=0.66, rump=False)
    use('head')
    # long flat snout with teeth along the edge (the silhouette) and raised eye ridges
    sn = b('snout', (0.8, 1.0, 0.3), mm('main'), (0, Hd.front - 0.46, Hd.c.z - 0.16), bev=0.07)
    b('jaw', (0.72, 0.9, 0.14), mm('belly'), (0, Hd.front - 0.42, Hd.c.z - 0.36), bev=0.04)
    b('snout_tip', (0.5, 0.2, 0.2), mm('main'), (0, sn.front - 0.02, sn.top + 0.04), bev=0.06)
    for sgn, n in LR:
        p('nostril', (0.08, 0.08, 0.05), mm('dark'), (sgn * 0.12, sn.front + 0.02, sn.top + 0.14))
        for j in range(5):
            p('tooth', (0.07, 0.08, 0.1), mm('horn'), (sgn * 0.39, sn.front + 0.12 + j * 0.18, sn.bot + 0.0))
        b('eye_ridge', (0.4, 0.4, 0.2), mm('main'), (sgn * 0.3, Hd.front + 0.2, Hd.top + 0.06), bev=0.06)
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.44, Hd.front - 0.012, Hd.c.z - 0.06))
    for i in range(3):
        p('snout_bump', (0.14, 0.14, 0.05), mm('dark'), (0, sn.front + 0.3 + i * 0.26, sn.top + 0.02))
    eyes(Hd, 0.42, 0.27, 0.22, iris='#2a8a6a', glow='#7af0c0', brow='#2f6a3a', tilt=-8)
    use('body')
    # two rows of scutes down the back and tail, banded flanks
    for j in range(8):
        y = B.front + 0.14 + j * 0.25
        for sgn, n in LR:
            b('scute', (0.22, 0.2, 0.18), mm('dark'), (sgn * 0.24, y, B.top + 0.07), bev=0.05)
        p('scute_mid', (0.14, 0.14, 0.08), mm('accent'), (0, y + 0.12, B.top + 0.03))
    stripes(B, 'lr', 6, mm('dark'), 0.12, name='band', span=0.9)
    for i in range(5):
        p('belly_plate', (B.s.x * 0.66, 0.26, 0.03), mm('belly'), (0, B.front + 0.24 + i * 0.36, B.bot - 0.05))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.05), mm('dark'), (ft.c.x, ft.c.y + 0.1, 0.2))
    use('body')
    tail_kit('long', 'body', (0, B.back + 0.06, B.c.z), 'main', 'dark', n=3, size=0.22, dark='dark')
    for i, t in enumerate(a.tail):
        use(t)
        for j in range(2):
            b('tail_scute', (0.14, 0.16, 0.2 - 0.04 * i), mm('dark'), (0, B.back + 0.2 + i * 0.42 + j * 0.2, B.c.z + 0.16 + i * 0.055), bev=0.04)
    # rarity 4: glowing algae marks between the scutes, glowing tail tip, water sparks
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for j in range(7):
        p('glow_mark', (0.12, 0.08, 0.05), mm('glow'), (0, B.front + 0.265 + j * 0.25, B.top + 0.05))
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', -0.3, 0.1, (0.14, 0.14), mm('glow'), th=0.035, name='flank_rune', rot=(45, 0, 0))
        on(B, 'l' if sgn < 0 else 'r', 0.2, 0.1, (0.14, 0.14), mm('glow'), th=0.035, name='flank_rune', rot=(45, 0, 0))
    use(a.tail[-1])
    p('tail_glow', (0.2, 0.12, 0.2), mm('glow'), (0, B.back + 1.42, B.c.z + 0.14))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    p('fore_rune', (0.14, 0.14, 0.05), mm('glow'), (0, Hd.c.y - 0.05, Hd.top + 0.02), rot=(0, 0, 45))
    for sgn, n in LR:
        p('ridge_glow', (0.3, 0.06, 0.05), mm('glow'), (sgn * 0.3, Hd.front + 0.4, Hd.top + 0.14))
    use('body')
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=1.2)
    return finish(a)


def _side_head(a, tag, sgn, base, top, pal_iris):
    """extra hydra head on its own neck: segments neck_<tag> -> head_<tag>; simple non-blinking eyes"""
    sg('neck_' + tag, 'body', base)
    mid = ((base[0] + top[0]) / 2, (base[1] + top[1]) / 2, (base[2] + top[2]) / 2)
    b('neck', (0.44, 0.44, 0.7), mm('main'), (base[0] + (top[0] - base[0]) * 0.25, mid[1] + 0.1, base[2] + 0.3), rot=(10, sgn * 24, 0), bev=0.07)
    b('neck', (0.4, 0.4, 0.7), mm('main'), (base[0] + (top[0] - base[0]) * 0.75, mid[1], base[2] + 0.84), rot=(14, sgn * 24, 0), bev=0.07)
    for j in range(3):
        p('neck_belly', (0.26, 0.04, 0.24), mm('belly'), (base[0] + (top[0] - base[0]) * (0.2 + 0.3 * j), mid[1] - 0.2 - 0.02 * j, base[2] + 0.2 + j * 0.4))
        b('neck_fin', (0.1, 0.2, 0.26), mm('fin'), (base[0] + (top[0] - base[0]) * (0.2 + 0.3 * j), mid[1] + 0.3, base[2] + 0.3 + j * 0.4), bev=0.03)
    sg('head_' + tag, 'neck_' + tag, top)
    hc = (top[0], top[1] - 0.2, top[2] + 0.36)
    H2 = b('head', (0.9, 0.8, 0.74), mm('main'), hc)
    b('snout', (0.5, 0.26, 0.26), mm('belly'), (hc[0], H2.front - 0.1, hc[2] - 0.18), bev=0.05)
    p('mouth', (0.3, 0.03, 0.03), mm('line'), (hc[0], H2.front - 0.235, hc[2] - 0.24))
    for s2 in (-1, 1):
        ex = hc[0] + s2 * 0.22
        p('eye_frame', (0.3, 0.03, 0.3), smooth('eye_dark', '#1f1520', 0.2), (ex, H2.front, hc[2] + 0.1))
        p('eye_white', (0.25, 0.03, 0.25), smooth('eye_w_ffffff', '#ffffff', 0.2), (ex, H2.front - 0.012, hc[2] + 0.1))
        p('eye_iris', (0.18, 0.03, 0.2), mm('glow'), (ex, H2.front - 0.024, hc[2] + 0.08))
        p('eye_pupil', (0.1, 0.03, 0.13), smooth('eye_p_1f1520', '#1f1520', 0.1), (ex, H2.front - 0.036, hc[2] + 0.07))
        p('eye_hi', (0.07, 0.03, 0.07), smooth('eye_shine', '#ffffff', 0.05), (ex - 0.05, H2.front - 0.048, hc[2] + 0.15))
        p('nostril', (0.05, 0.03, 0.04), mm('line'), (hc[0] + s2 * 0.1, H2.front - 0.235, hc[2] - 0.12))
        cn('horn', 0.08, 0.3, mm('horn'), (hc[0] + s2 * 0.3, hc[1] + 0.1, H2.top - 0.02), (s2 * 0.4, 0.3, 1))
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (hc[0] + s2 * 0.34, H2.front - 0.012, hc[2] - 0.1))
    for i in range(2):
        b('crest', (0.12, 0.2, 0.24 - 0.06 * i), mm('fin'), (hc[0], hc[1] - 0.1 + i * 0.26, H2.top + 0.1), bev=0.03)
    p('crest_glow', (0.1, 0.1, 0.1), mm('glow'), (hc[0], hc[1] - 0.1, H2.top + 0.26))
    use('body')
    return H2


def marsh_hydra(row):
    a = start(row, dict(main='#4a9a6a', belly='#e8f0b8', dark='#2a6a4a', accent='#7ac88a', fin='#3fb8b0', horn='#fff6e0',
                        **{'*glow': '#7af0c0', '*glow2': '#ffe14a'}), 3.3)
    B, Hd = quad(bw=1.4, bl=1.6, bh=1.0, legh=0.5, lw=0.4, hw=1.06, hd=0.94, hh=0.9, neck=1.0, toe='horn', head_fwd=0.3, leg_fl=0.6, ntoe=3, hump=0.0)
    mz = muzzle(Hd, (0.56, 0.3, 0.3), -0.24, 'belly', nose=None, mouth=True, fangs=1)
    for sgn, n in LR:
        p('nostril', (0.06, 0.03, 0.05), mm('line'), (sgn * 0.12, mz.front - 0.008, mz.c.z + 0.08))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.4, Hd.front - 0.012, Hd.c.z - 0.2))
        cn('horn', 0.1, 0.4, mm('horn'), (sgn * 0.34, Hd.c.y + 0.1, Hd.top - 0.02), (sgn * 0.4, 0.3, 1))
    eyes(Hd, 0.34, 0.25, 0.1, iris='#2a8a6a', glow='#7af0c0', brow='#2a6a4a', tilt=-8)
    use('head')
    for i in range(3):
        b('crest', (0.14, 0.22, 0.3 - 0.06 * i), mm('fin'), (0, Hd.c.y - 0.2 + i * 0.26, Hd.top + 0.12), bev=0.04)
    nk = Box((0, B.front + 0.2, 0.5 + 1.0 * 0.85 + 0.5), (1.4 * 0.6, 1.4 * 0.6, 1.0 + 0.3))
    for j in range(3):
        p('neck_belly', (0.5, 0.04, 0.26), mm('belly'), (0, nk.front - 0.012, nk.c.z + 0.34 - j * 0.34))
        b('neck_fin', (0.12, 0.24, 0.3), mm('fin'), (0, nk.back + 0.1, nk.c.z + 0.34 - j * 0.34), bev=0.04)
    use('body')
    # two more heads on their own necks (the silhouette); they look around too
    HL = _side_head(a, 'L', -1, (-0.5, B.front + 0.3, B.top - 0.1), (-1.25, B.front - 0.3, B.top + 1.1), 0)
    HR = _side_head(a, 'R', 1, (0.5, B.front + 0.3, B.top - 0.1), (1.25, B.front - 0.3, B.top + 1.1), 0)

    def heads_idle(c, n):
        for x, r in ((1, 0), (n // 4, 10), (n // 2, 0), (3 * n // 4, -10), (n, 0)):
            k(c, 'neck_L', x, rot=(0, 0, r))
            k(c, 'neck_R', x, rot=(0, 0, -r))
            k(c, 'head_L', x, rot=(r * 0.6, 0, 0))
            k(c, 'head_R', x, rot=(-r * 0.6, 0, 0))

    def heads_show(c, T, n):
        for x, r in ((0, 0), (0.25, 30), (0.5, -20), (0.75, 30), (1.0, 0)):
            k(c, 'head_L', int(T + n * x), rot=(0, 0, -r))
            k(c, 'head_R', int(T + n * x), rot=(0, 0, r))
            k(c, 'neck_L', int(T + n * x), rot=(0, r * 0.3, 0))
            k(c, 'neck_R', int(T + n * x), rot=(0, -r * 0.3, 0))
    a.extra_idle.append(heads_idle)
    a.extra_reveal.append(heads_show)
    # scales, belly plates, back fins
    stripes(B, 'lr', 5, mm('dark'), 0.12, name='band', span=0.86)
    spots(B, 't', 6, mm('accent'), 0.18, seed=3, name='scale')
    spots(a.bx['rump'], 'lr', 4, mm('accent'), 0.16, seed=5, name='scale')
    fluff(a.bx['chest'], 'f', mm('accent'), 3, 0.9, 0.3)
    for i in range(5):
        b('back_fin', (0.14, 0.24, 0.34 - 0.03 * i), mm('fin'), (0, B.front + 0.3 + i * 0.3, B.top + 0.14), bev=0.04)
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.1, 0.34))
        p('leg_fin', (0.06, 0.2, 0.2), mm('fin'), (ft.c.x + (0.22 if ft.c.x > 0 else -0.22), ft.c.y + 0.14, 0.36))
    use('body')
    tail_kit('long', 'body', a.tail_j, 'main', 'fin', n=3, size=0.24, dark='dark')
    # rarity 5: glowing belly scales, glowing fins, orbiting water gems, yellow aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i in range(5):
        p('fin_glow', (0.1, 0.12, 0.1), mm('glow' if i % 2 else 'glow2'), (0, B.front + 0.3 + i * 0.3, B.top + 0.36 - 0.03 * i))
    for sgn, n in LR:
        f = 'l' if sgn < 0 else 'r'
        for i in range(3):
            on(B, f, -0.3 + i * 0.3, -0.3, (0.16, 0.16), mm('glow'), th=0.035, name='flank_gem', rot=(45, 0, 0))
        on(a.bx['rump'], f, 0, 0.14, (0.2, 0.2), mm('glow2'), th=0.035, name='flank_gem', rot=(45, 0, 0))
    p('chest_gem', (0.24, 0.06, 0.24), mm('glow2'), (0, B.front - 0.13, B.c.z + 0.1), rot=(0, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(3):
        p('crest_glow', (0.1, 0.12, 0.1), mm('glow'), (0, Hd.c.y - 0.2 + i * 0.26, Hd.top + 0.3 - 0.06 * i))
    on(Hd, 'f', 0, 0.36, (0.16, 0.16), mm('glow2'), th=0.035, name='fore_gem', rot=(0, 45, 0))
    use('body')
    orbit_kit((0, 0.2, 1.6), 1.9, 6, 'glow', 'glow2', size=0.14, dz=0.5, shape='bubble')
    aura_kit(1.9, 5, motes=10, mote_col='glow', mote_r=2.0, height=2.6, style='ring')
    return finish(a)


def mangrove_flamingo(row):
    a = start(row, dict(main='#ff8ab8', belly='#ffc8dc', dark='#e85a94', accent='#ffffff', leg='#ff6aa0', beak='#fff0e0', beak_tip='#2a2030',
                        **{'*glow': '#ff9ad0', '*glow2': '#7af0c0', '*gold': '#ffd84a'}), 5.7)
    B, Hd = bird(bw=1.0, bl=1.2, bh=0.9, legh=2.0, lw=0.12, hw=0.82, hd=0.76, hh=0.76, neck=1.6, beak=(0.34, 0.44, 0.3),
                 wing=(0.16, 0.9, 0.6), ntail=5, tail_l=0.5, tail_mat='dark', head_mat='main')
    bk = a.bx['beak']
    use('head')
    # the bent black-tipped bill
    b('beak_bend', (0.3, 0.3, 0.36), mm('beak_tip'), (0, bk.front - 0.06, bk.c.z - 0.2), rot=(-25, 0, 0), bev=0.06)
    p('beak_band', (0.36, 0.06, 0.32), mm('dark'), (0, bk.c.y + 0.06, bk.c.z))
    # S-neck: stepped ruffs up the long neck
    nz0 = 2.0 + 0.9 * 0.9
    for j in range(6):
        b('neck_ruff', (0.5 - 0.02 * j, 0.5 - 0.02 * j, 0.14), mm('belly' if j % 2 else 'dark'), (0, Hd.c.y + 0.08, nz0 + 0.2 + j * 0.24), bev=0.04)
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('accent'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.2))
    for i in range(4):
        b('head_plume', (0.1, 0.1, 0.34 - 0.05 * i), mm('dark'), (0, Hd.c.y - 0.2 + i * 0.16, Hd.top + 0.12), rot=(-10 - 10 * i, 0, 0), bev=0.03)
    eyes(Hd, 0.4, 0.25, 0.14, iris='#c83a7a', glow='#ff9ad0', lash=True, brow='#e85a94', tilt=8)
    use('body')
    # layered plumage: stepped feather rows on the back, chest ruff, black flight feathers
    for i in range(3):
        for j in range(4):
            p('back_feather', (0.3, 0.3, 0.06), mm('dark' if (i + j) % 2 else 'belly'), ((i - 1) * 0.3, B.c.y - 0.4 + j * 0.28, B.top + 0.04 + 0.02 * ((i + j) % 2)))
    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('accent'), 4, 0.9, 0.36)
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(4):
            b('flight', (0.14, 0.3, 0.2), mm('beak_tip'), (sgn * (B.s.x / 2 + 0.1), B.c.y + 0.6, B.c.z + 0.2 - j * 0.16), rot=(-20, 0, 0), bev=0.03)
            p('covert', (0.05, 0.2, 0.16), mm('accent'), (sgn * (B.s.x / 2 + 0.17), B.c.y - 0.1 + j * 0.16, B.c.z + 0.2 - 0.05 * j))
        use('leg_' + n)
        for j in range(3):
            p('leg_ring', (0.17, 0.17, 0.05), mm('gold'), (sgn * B.s.x * 0.24, 0.15, 0.5 + j * 0.5))
        p('knee_glow', (0.2, 0.2, 0.1), mm('glow'), (sgn * B.s.x * 0.24, 0.15, 1.24))
    use('body')
    # rarity 6: glowing wing and tail tips, lotus gems, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i in range(5):
        on(B, 't', 0.0, -0.4 + i * 0.2, (0.5 - 0.06 * i, 0.06), mm('glow' if i % 2 else 'glow2'), th=0.1, name='back_glow')
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', -0.2, 0.2, (0.16, 0.16), mm('glow2'), th=0.3, name='wing_gem', rot=(45, 0, 0))
        on(B, 'l' if sgn < 0 else 'r', 0.2, 0.0, (0.12, 0.12), mm('glow'), th=0.3, name='wing_gem', rot=(45, 0, 0))
    p('chest_lotus', (0.24, 0.06, 0.24), mm('glow2'), (0, B.front - 0.16, B.c.z + 0.1), rot=(0, 45, 0))
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        p('lotus_petal', (0.12, 0.05, 0.12), mm('glow'), (math.cos(ang) * 0.2, B.front - 0.15, B.c.z + 0.1 + math.sin(ang) * 0.2), rot=(0, 45, 0))
    use('tail')
    for i in range(5):
        ang = (i - 2) * 17.5
        p('tail_glow', (0.12, 0.14, 0.1), mm('glow'), (math.sin(math.radians(ang)) * 0.42, 0.15 + 1.2 * 0.62 + 0.52, 2.0 + 0.45 + 0.9 * 0.22 + math.cos(math.radians(ang)) * 0.2 + 0.26))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(4):
        p('plume_glow', (0.08, 0.08, 0.1), mm('glow2'), (0, Hd.c.y - 0.26 + i * 0.12, Hd.top + 0.3 - 0.03 * i))
    on(Hd, 'f', 0, 0.38, (0.12, 0.12), mm('glow2'), th=0.035, name='fore_gem', rot=(0, 45, 0))
    halo_kit(Hd, 'gold', r=0.44, n=8, dz=0.7, kind='stars')
    use('body')
    orbit_kit((0, 0.15, 2.6), 1.2, 6, 'glow', 'glow2', size=0.12, dz=0.6, shape='leaf')
    orbit_kit((0, 0.15, 1.2), 1.4, 8, 'gold', 'glow', size=0.08, name='orbit2', dz=0.2, shape='bubble')
    aura_kit(1.2, 6, motes=12, mote_col='glow', mote_r=1.3, height=3.6, style='rays')
    return finish(a)


ANIMALS = dict(mudskipper=mudskipper, otter=otter, mangrove_fiddler=mangrove_fiddler, crocodile=crocodile, marsh_hydra=marsh_hydra,
               mangrove_flamingo=mangrove_flamingo)
