# Biome 11 - Azure Coast: white beaches, grottos, coral lagoons
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 11
GROUND = '#d8bc84'
SKY = '#c8eeff'
THEME = dict(bits=['#f6ecd0', '#5ac8e8'], dust='#fff4dc', glow='#5ae8ff', splash='#bfefff', bit_name='песок и брызги')
FOOT = dict(lagoon_pelican=1.3, coral_wyvern=1.4, azure_horseshoe_crab=1.25)
BUSH_NAME = 'прибрежная дюна с пляжной травой, кораллом, ракушками, морской звездой и бирюзовой лужицей'


def bush():
    B = begin_bush(NN)
    sd = mat('sand', '#f6e6c0')
    sd2 = mat('sand2', '#e8d0a0')
    gr = mat('grass', '#9ac85a')
    gr2 = mat('grass2', '#7aa848')
    cor = mat('coral', '#ff7a8a')
    cor2 = mat('coral2', '#ffb070')
    sh = mat('shell', '#fff0f4')
    sh2 = mat('shell2', '#ffb8cc')
    wat = mat('water', '#4ac8e0')
    wat2 = mat('water2', '#9aeaf6')
    rock = mat('rock', '#c8c0b0')
    star_m = mat('star', '#ff9a3a')
    pearl = mat('pearl', '#e8fbff', 'neon', 1.6)
    # dune mounds with wind lines
    for i, (x, y, w, d, h) in enumerate(((0, 0.4, 5.4, 2.6, 1.0), (-0.9, 0.6, 3.0, 1.8, 1.8), (1.5, 0.5, 2.2, 1.6, 1.5))):
        part('big', (x, y, 0.2), 'dune_%d' % i)
        b('dune', (w, d, h), sd if i % 2 == 0 else sd2, (x, y, h / 2), bev=0.16)
        b('dune_top', (w * 0.66, d * 0.66, 0.24), sd, (x, y, h + 0.08), bev=0.08)
        p('wind_line', (w * 0.6, 0.05, 0.06), sd2, (x, y - d / 2 - 0.01, h * 0.55))
    # beach grass (tall tufts that sway)
    k_ = 0
    for (cx, cy, z, n, h0) in ((-2.2, 0.0, 0.9, 5, 2.4), (-0.9, 0.7, 1.7, 6, 2.8), (0.6, 0.5, 1.1, 5, 2.6), (1.8, 0.6, 1.5, 5, 2.4), (-0.2, -0.3, 1.0, 4, 1.8)):
        part('small', (cx, cy, z), 'grass_%d' % k_)
        for i in range(n):
            lean = (i - (n - 1) / 2) * 12
            h = h0 - 0.3 * abs(i - (n - 1) / 2)
            b('blade', (0.14, 0.12, h), gr if i % 2 else gr2, (cx + (i - (n - 1) / 2) * 0.16 + math.sin(math.radians(lean)) * h / 2, cy, z + h / 2), rot=(0, lean, 0), bev=0.03)
        k_ += 1
    # branching coral clumps (the colour pop)
    for i, (x, y, s, m_) in enumerate(((-2.6, -0.9, 1.0, cor), (2.6, -0.7, 0.9, cor2), (0.9, -1.2, 0.7, cor))):
        part('small', (x, y, 0.1), 'coral_%d' % i)
        b('coral_base', (0.5 * s, 0.5 * s, 0.5 * s), m_, (x, y, 0.3 * s), bev=0.06)
        for j, (dx, dz, h) in enumerate(((-0.3, 0.5, 0.9), (0.0, 0.6, 1.3), (0.3, 0.5, 1.0), (-0.15, 1.2, 0.5), (0.2, 1.3, 0.5))):
            b('coral_branch', (0.2 * s, 0.2 * s, h * s), m_, (x + dx * s, y, (dz + h / 2) * s), rot=(0, dx * 50, 0), bev=0.04)
            p('coral_tip', (0.24 * s, 0.24 * s, 0.1 * s), sh, (x + dx * s * 1.3, y, (dz + h) * s))
    # shells, a starfish, a pearl
    for i, (x, y, s) in enumerate(((-1.4, -1.4, 1.0), (0.0, -1.6, 0.8), (1.9, -1.5, 0.9), (-3.0, 0.6, 0.8))):
        part('small', (x, y, 0.1), 'shell_%d' % i)
        b('shell', (0.46 * s, 0.4 * s, 0.3 * s), sh, (x, y, 0.2 * s), rot=(0, 0, 25 * i), bev=0.08)
        for j in range(3):
            p('shell_rib', (0.06 * s, 0.42 * s, 0.32 * s), sh2, (x + (j - 1) * 0.13 * s, y, 0.2 * s), rot=(0, 0, 25 * i))
    part('small', (-0.6, -1.3, 0.1), 'starfish')
    for i in range(5):
        ang = math.radians(i * 72 + 90)
        b('star_arm', (0.42, 0.18, 0.12), star_m, (-0.6 + math.cos(ang) * 0.24, -1.3 + math.sin(ang) * 0.24, 0.12), rot=(0, 0, math.degrees(ang)), bev=0.04)
    p('star_core', (0.22, 0.22, 0.14), mat('star2', '#ffc85a'), (-0.6, -1.3, 0.16))
    # rock pool with a glowing pearl
    part('big', (2.4, 1.0, 0.1), 'pool')
    b('pool_rim', (1.8, 1.4, 0.4), rock, (2.4, 1.0, 0.2), bev=0.1)
    b('pool_water', (1.4, 1.0, 0.1), wat, (2.4, 1.0, 0.38), bev=0.03)
    p('pool_shine', (0.5, 0.2, 0.02), wat2, (2.2, 0.9, 0.44))
    part('small', (2.6, 1.1, 0.4), 'pearl_clam')
    b('clam', (0.4, 0.34, 0.16), sh2, (2.6, 1.1, 0.48), bev=0.05)
    b('pearl', (0.16, 0.16, 0.16), pearl, (2.6, 1.08, 0.6), bev=0.06)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def spiral_hermit_crab(row):
    a = start(row, dict(main='#ff7a4a', belly='#ffd0a8', dark='#a83a20', accent='#ffd84a', shell='#f2e6ff', shell2='#a88ae8'), 2.4)
    B, Hd = bug(bw=0.9, bl=0.7, bh=0.5, legh=0.3, hw=0.8, hd=0.36, hh=0.5, nleg=3, leg_w=0.1, leg_span=0.4, claws=0.3, antenna=0.3,
                head_z=0.0, shell='main', under='belly', leg_mat='dark')
    use('head')
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.28, Hd.front - 0.012, Hd.c.z - 0.14))
    p('mouth', (0.2, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.18))
    eyes(Hd, 0.46, 0.25, 0.06, iris='#3a1a10', brow='#a83a20', tilt=12, lash=True)
    use('body')
    # the spiral shell house (the silhouette): stepped cubes winding up
    sg('house', 'body', (0, B.c.y + 0.1, B.top))
    for i in range(6):
        ang = math.radians(i * 70)
        s = 0.86 - 0.11 * i
        b('spiral', (s, s, s * 0.7), mm('shell' if i % 2 == 0 else 'shell2'), (math.cos(ang) * 0.12 * i, B.c.y + 0.16 + math.sin(ang) * 0.1 * i, B.top + 0.28 + i * 0.26), rot=(0, 0, i * 25), bev=0.08)
        p('spiral_band', (s + 0.02, s * 0.3, 0.06), mm('shell2' if i % 2 == 0 else 'shell'), (math.cos(ang) * 0.12 * i, B.c.y + 0.16 + math.sin(ang) * 0.1 * i, B.top + 0.28 + i * 0.26 + s * 0.2), rot=(0, 0, i * 25))
    b('shell_mouth', (0.8, 0.3, 0.5), mm('shell2'), (0, B.c.y - 0.1, B.top + 0.24), bev=0.06)
    p('barnacle', (0.14, 0.14, 0.1), mm('accent'), (0.3, B.c.y + 0.4, B.top + 0.6))
    p('barnacle', (0.1, 0.1, 0.08), mm('accent'), (-0.24, B.c.y + 0.3, B.top + 0.9))
    p('seaweed', (0.08, 0.06, 0.3), studs(a.id + '_weed', '#5ab85a'), (-0.3, B.c.y + 0.2, B.top + 0.4))
    a.extra_idle.append(lambda c, n: [k(c, 'house', x, rot=(0, r, 0)) for x, r in ((1, 0), (n // 2, 5), (n, 0))])
    use('body')
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_band', (0.08, 0.13, 0.13), mm('accent'), (j.x + sgn * 0.18, j.y, j.z + 0.04))
    use('body')
    return finish(a)


def sea_turtle(row):
    a = start(row, dict(main='#5ab88a', belly='#f6e8b8', dark='#2a7a5a', accent='#a8e070', shell='#3a8a6a', shell2='#8ad8a0'), 1.9)
    B, Hd = quad(bw=1.3, bl=1.4, bh=0.6, legh=0.24, lw=0.3, hw=0.9, hd=0.84, hh=0.76, head_up=0.3, toe='dark', head_fwd=0.5, leg_fl=0.6,
                 rump=False, chest=False)
    mz = muzzle(Hd, (0.4, 0.2, 0.24), -0.24, 'belly', nose=None, mouth=True)
    for sgn, n in LR:
        p('nostril', (0.05, 0.03, 0.04), mm('line'), (sgn * 0.08, mz.front - 0.008, mz.c.z + 0.06))
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.16))
    eyes(Hd, 0.34, 0.25, 0.12, iris='#2a5a3a', brow='#2a7a5a', tilt=8, sleepy=0.18)
    spots(Hd, 'tlr', 5, mm('dark'), 0.12, seed=2, name='head_scale')
    use('body')
    # domed shell of hex-like plates (the silhouette)
    b('shell', (1.5, 1.6, 0.5), mm('shell'), (0, B.c.y, B.top + 0.2), bev=0.12)
    b('shell_top', (1.1, 1.2, 0.3), mm('shell'), (0, B.c.y, B.top + 0.52), bev=0.1)
    for i in range(3):
        for j in range(3):
            p('plate', (0.36, 0.38, 0.06), mm('shell2' if (i + j) % 2 else 'accent'), ((i - 1) * 0.38, B.c.y - 0.4 + j * 0.4, B.top + 0.69))
    for sgn, n in LR:
        for j in range(4):
            p('rim_plate', (0.08, 0.32, 0.16), mm('dark'), (sgn * 0.76, B.c.y - 0.54 + j * 0.36, B.top + 0.12))
    for j in range(3):
        p('rim_front', (0.4, 0.08, 0.16), mm('dark'), ((j - 1) * 0.44, B.c.y - 0.81, B.top + 0.12))
    b('plastron', (1.2, 1.3, 0.1), mm('belly'), (0, B.c.y, B.bot - 0.02), bev=0.03)
    # flippers: the front legs are wide flat paddles
    for ft in a.bx['feet']:
        use(ft.seg)
        sgn = 1 if ft.c.x > 0 else -1
        b('flipper', (0.6, 0.4, 0.1), mm('main'), (ft.c.x + sgn * 0.2, ft.c.y - 0.1, 0.08), rot=(0, 0, -sgn * 20), bev=0.04)
        p('flipper_spot', (0.16, 0.16, 0.04), mm('dark'), (ft.c.x + sgn * 0.3, ft.c.y - 0.1, 0.14))
    use('body')
    tail_kit('stub', 'body', (0, B.back, B.c.z - 0.1), 'main', 'dark', size=0.14)
    return finish(a)


def lagoon_pelican(row):
    """pelican floating with its wings folded: a round boat-shaped body, a short neck and a HUGE beak whose pouch hangs down
    full of water with a little fish peeking out; webbed feet dangling"""
    zc = 0.8
    a = start(row, dict(main='#f4f4f0', belly='#ffffff', dark='#3a4a5a', accent='#ffb84a', pouch='#ffa86a', wing='#c8d0d8', fish='#5ab8e8',
                        water='#a8e0ff'), 2.12, hover=2.2, z0=zc)
    sg('body', 'root', (0, 0.3, zc))
    B = b('body', (1.0, 1.5, 0.8), mm('main'), (0, 0.4, zc), bev=0.3)
    b('tail_up', (0.5, 0.4, 0.3), mm('main'), (0, 1.2, zc + 0.3), rot=(-25, 0, 0), bev=0.08)
    grid(B, 'u', 2, 3, mm('wing'), (0.1, 0.1), name='belly_feather', span=(0.6, 0.7))
    for sgn, n in LR:
        nm = 'wing_' + n
        sg(nm, 'body', (sgn * 0.5, 0.2, zc + 0.2))
        a.wings.append(nm)
        b('folded_wing', (0.16, 1.2, 0.6), mm('wing'), (sgn * 0.52, 0.5, zc + 0.08), rot=(-8, 0, 0), bev=0.06)
        for j in range(4):
            p('wing_feather', (0.17, 0.2, 0.14), mm('dark'), (sgn * 0.53, 0.75 + j * 0.15, zc - 0.12 + j * 0.04))
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.25, 0.5, zc - 0.4))
        a.legs.append(nm)
        p('leg', (0.08, 0.08, 0.3), mm('accent'), (sgn * 0.25, 0.5, zc - 0.55))
        p('web_foot', (0.26, 0.3, 0.05), mm('accent'), (sgn * 0.25, 0.42, zc - 0.7))
    sg('head', 'body', (0, -0.3, zc + 0.4))
    b('neck', (0.34, 0.34, 0.5), mm('main'), (0, -0.3, zc + 0.6), bev=0.08)
    Hd = b('head', (0.6, 0.56, 0.5), mm('main'), (0, -0.4, zc + 1.0), bev=0.14)
    p('crest', (0.1, 0.3, 0.16), mm('accent'), (0, -0.3, Hd.top + 0.06))
    eyes(Hd, 0.32, 0.25, 0.14, iris='#3a4a5a', brow=None)
    # the huge beak with a full hanging pouch (the silhouette)
    b('upper_beak', (0.3, 1.2, 0.12), mm('accent'), (0, Hd.front - 0.55, zc + 0.92), bev=0.03)
    p('beak_hook', (0.1, 0.12, 0.12), mm('pouch'), (0, Hd.front - 1.15, zc + 0.86))
    b('pouch', (0.4, 1.0, 0.6), mm('pouch'), (0, Hd.front - 0.55, zc + 0.56), bev=0.16)
    p('pouch_water', (0.3, 0.8, 0.06), mm('water'), (0, Hd.front - 0.55, zc + 0.84))
    p('fish', (0.1, 0.3, 0.14), mm('fish'), (0.06, Hd.front - 0.75, zc + 0.92), rot=(0, 0, 20))
    p('fish_tail', (0.04, 0.1, 0.14), mm('fish'), (0.1, Hd.front - 0.58, zc + 0.94))
    for sgn in (-1, 1):
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.22, Hd.front - 0.012, zc + 0.94))
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.2, -0.4, Hd.top))
        a.ears.append(nm)
        p('head_tuft', (0.08, 0.14, 0.14), mm('belly'), (sgn * 0.12, -0.3, Hd.top + 0.04))
    grid(Hd, 'l', 2, 2, mm('wing'), (0.06, 0.06), name='cheek_feather', span=(0.4, 0.4))
    grid(Hd, 'r', 2, 2, mm('wing'), (0.06, 0.06), name='cheek_feather', span=(0.4, 0.4))
    use('body')
    sg('tail', 'body', (0, 1.1, zc + 0.3))
    a.tail = ['tail']
    for j in range(3):
        p('tail_feather', (0.14, 0.3, 0.06), mm('dark'), ((j - 1) * 0.14, 1.4, zc + 0.45))
    grid(B, 't', 3, 3, mm('wing'), (0.08, 0.08), name='back_feather', span=(0.5, 0.6))
    grid(B, 'l', 4, 2, mm('belly'), (0.08, 0.08), name='side_feather', span=(0.8, 0.5))
    grid(B, 'r', 4, 2, mm('belly'), (0.08, 0.08), name='side_feather', span=(0.8, 0.5))
    grid(B, 'f', 3, 2, mm('belly'), (0.08, 0.08), name='chest_feather', span=(0.6, 0.5))
    use('head')
    for j in range(6):
        p('beak_line', (0.31, 0.12, 0.03), mm('pouch'), (0, Hd.front - 0.1 - j * 0.18, zc + 0.98))
    for j in range(5):
        p('pouch_fold', (0.42, 0.06, 0.4), mm('accent'), (0, Hd.front - 0.2 - j * 0.16, zc + 0.56))
    use('head')
    grid(Hd, 't', 2, 2, mm('wing'), (0.06, 0.06), name='head_feather', span=(0.4, 0.4))
    use('body')
    grid(B, 'k', 2, 2, mm('wing'), (0.1, 0.1), name='rump_feather', span=(0.5, 0.5))
    for j in range(10):
        p('waterline', (0.12, 0.12, 0.05), mm('water'), ((j % 5 - 2) * 0.24, 0.0 + (j // 5) * 0.8, zc - 0.42))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc), Hit=(0, 0.4, zc + 0.4))
    return finish(a)


def sea_lion(row):
    a = start(row, dict(main='#8a6a52', belly='#c8a888', dark='#4a3628', accent='#ffd84a', **{'*glow': '#5ae8ff'}), 3.0)
    B, Hd = sit(bw=0.9, bd=1.0, bh=1.2, hw=0.94, hd=0.86, hh=0.82, arm=0.3, lw=0.2, foot_l=0.8, thigh=False, ntoe=3, foot='dark', toe='belly')
    mz = muzzle(Hd, (0.5, 0.26, 0.3), -0.24, 'belly', nose=(0.2, 0.09, 0.12), teeth=0)
    cheeks(Hd, 'belly', (0.24, 0.2, 0.28), -0.24, whisk=4, wmat='white')
    eyes(Hd, 0.4, 0.25, 0.12, iris='#2a1a10', glow='#5ae8ff', brow='#4a3628', tilt=8, lash=True)
    for sgn, n in LR:
        p('ear', (0.08, 0.1, 0.12), mm('dark'), (sgn * (Hd.s.x / 2 + 0.03), Hd.c.y, Hd.c.z + 0.1))
    use('body')
    fluff(Box((0, B.front - 0.07, B.c.z), (B.s.x * 0.72, 0.1, B.s.z * 0.7)), 'f', mm('belly'), 4, 1.0, 0.4)
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        b('flipper', (0.2, 0.36, 0.5), mm('dark'), (sgn * (B.s.x / 2 + 0.04), 0.12 - 1.0 / 2 + 0.1, 0.4), rot=(0, sgn * 20, 0), bev=0.05)
    use('body')
    spots(B, 'lr', 4, mm('dark'), 0.14, seed=3, name='spot')
    spots(B, 'k', 4, mm('dark'), 0.14, seed=5, name='spot')
    for i in range(5):
        p('neck_fold', (B.s.x * 0.9 - 0.06 * i, 0.06, 0.05), mm('belly'), (0, B.front - 0.06, B.top - 0.1 - i * 0.2))
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        for j in range(3):
            p('flipper_line', (0.22, 0.06, 0.06), mm('belly'), (sgn * (0.9 / 2 + 0.04), 0.12 - 0.5 + 0.0, 0.3 + j * 0.12), rot=(0, sgn * 20, 0))
    for ft in a.bx['feet']:
        use(ft.seg)
        sgn = 1 if ft.c.x > 0 else -1
        b('hind_flipper', (0.36, 0.5, 0.08), mm('dark'), (ft.c.x + sgn * 0.12, ft.c.y + 0.3, 0.05), rot=(0, 0, sgn * 30), bev=0.03)
        for j in range(3):
            p('hind_line', (0.06, 0.4, 0.05), mm('belly'), (ft.c.x + sgn * (0.04 + j * 0.1), ft.c.y + 0.3, 0.1), rot=(0, 0, sgn * 30))
    use('head')
    for sgn, n in LR:
        for j in range(3):
            p('whisker_dot', (0.03, 0.03, 0.03), mm('dark'), (sgn * (0.08 + 0.06 * j), mz.front - 0.008, mz.c.z - 0.02))
    use('body')
    tail_kit('stub', 'body', (0, a.tail_j[1], 0.3), 'dark', 'dark', size=0.18)
    # the ball it juggles on its nose (own segment, bounces in Idle)
    sg('ball', 'head', (0, Hd.front - 0.1, Hd.top + 0.2))
    setm('ball1', '#ff4a5a')
    setm('ball2', '#ffffff')
    setm('ball3', '#3a8ad8')
    b('ball', (0.5, 0.5, 0.5), mm('ball2'), (0, mz.c.y, Hd.top + 0.4), bev=0.12)
    for i, m_ in enumerate(('ball1', 'ball3', 'ball1', 'accent')):
        ang = i * 90
        p('ball_panel', (0.52, 0.14, 0.52), mm(m_), (0, mz.c.y, Hd.top + 0.4), rot=(0, 0, ang))

    def ball_idle(c, n):
        for x, z in ((1, 0), (n // 4, 0.3), (n // 2, 0), (3 * n // 4, 0.3), (n, 0)):
            k(c, 'ball', x, loc=(0, 0, z * K.S), rot=(0, 0, 0))
    a.extra_idle.append(ball_idle)
    # rarity 4: glowing collar of sea gems and glowing whisker tips, sparks
    sg('glow', 'body', (0, B.front, B.top))
    a.glow.append('glow')
    for i in range(7):
        ang = math.radians(i * 30)
        p('collar_gem', (0.12, 0.08, 0.12), mm('glow' if i % 2 else 'accent'), (math.cos(ang) * 0.42, B.front + 0.4 - math.sin(ang) * 0.42 - 0.38, B.top - 0.06), rot=(0, 45, 0))
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', 0, 0.2, (0.16, 0.16), mm('glow'), th=0.035, name='side_gem', rot=(45, 0, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.c.z))
    a.glow.append('glow_h')
    for sgn, n in LR:
        p('whisker_glow', (0.06, 0.06, 0.06), mm('glow'), (sgn * (Hd.s.x / 2 + 0.25), Hd.front + 0.06, Hd.c.z - 0.2))
    on(Hd, 'f', 0, 0.36, (0.12, 0.12), mm('glow'), th=0.035, name='fore_gem', rot=(0, 45, 0))
    use('body')
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=1.8)
    return finish(a)


def coral_wyvern(row):
    """sea wyvern: stands on two webbed legs, long S-neck, seahorse-like head with a fan frill, fin-sail wings, eel tail with a fluke"""
    zc = 1.4
    a = start(row, dict(main='#2ab8b0', belly='#fff0d8', dark='#14706a', accent='#ff7a8a', coral='#ff9a5a', fin='#7ae8ff', horn='#fff4e0',
                        **{'*glow': '#5ae8ff', '*glow2': '#ffd21a'}), 4.6, hover=2.4, z0=zc)
    # upright pear-shaped torso
    sg('body', 'root', (0, 0.2, zc))
    B = b('body', (0.9, 0.8, 1.1), mm('main'), (0, 0.2, zc))
    b('hips', (1.0, 0.9, 0.5), mm('main'), (0, 0.3, zc - 0.55), bev=0.08)
    b('belly', (0.6, 0.12, 0.9), mm('belly'), (0, -0.22, zc - 0.05), bev=0.04)
    for j in range(5):
        p('belly_plate', (0.62, 0.14, 0.06), mm('coral'), (0, -0.26, zc - 0.42 + j * 0.2))
    for sgn, n in LR:
        for j in range(3):
            p('side_scale', (0.05, 0.22, 0.2), mm('dark'), (sgn * 0.46, 0.1 + j * 0.2, zc + 0.2 - j * 0.24))
            b('shoulder_coral', (0.1, 0.1, 0.34 - 0.08 * j), mm('coral'), (sgn * (0.3 + 0.12 * j), 0.3, zc + 0.6 + 0.14 * (2 - j)), rot=(0, sgn * 25, 0), bev=0.02)
    # S-neck: three thin segments curving forward
    cur = Vector((0, 0.0, zc + 0.5))
    par = 'body'
    a.neck = []
    for i, (dy, dz) in enumerate(((-0.1, 0.5), (-0.3, 0.45), (-0.1, 0.4))):
        nm = 'neck%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.neck.append(nm)
        c = cur + Vector((0, dy * 0.5, dz * 0.5))
        b('neck', (0.38 - 0.03 * i, 0.38 - 0.03 * i, 0.5), mm('main'), tuple(c), rot=(-dy * 60, 0, 0), bev=0.06)
        p('neck_belly', (0.24, 0.05, 0.4), mm('belly'), (0, c.y - 0.19, c.z), rot=(-dy * 60, 0, 0))
        b('neck_fin', (0.06, 0.2, 0.3), mm('fin'), (0, c.y + 0.2, c.z), bev=0.02)
        for sgn, n in LR:
            p('neck_scale', (0.04, 0.2, 0.2), mm('dark'), (sgn * (0.19 - 0.015 * i + 0.01), c.y, c.z), rot=(-dy * 60, 0, 0))
        cur = cur + Vector((0, dy, dz))
        par = nm
    # long seahorse head
    sg('head', par, tuple(cur))
    hc = (0, cur.y - 0.2, cur.z + 0.25)
    Hd = b('head', (0.74, 0.7, 0.62), mm('main'), hc)
    sn = b('snout', (0.34, 0.6, 0.3), mm('main'), (0, Hd.front - 0.26, hc[2] - 0.1), bev=0.05)
    p('snout_tip', (0.36, 0.08, 0.26), mm('dark'), (0, sn.front + 0.02, sn.c.z))
    p('mouth', (0.2, 0.03, 0.03), mm('line'), (0, sn.front - 0.006, sn.c.z - 0.06))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.26, Hd.front - 0.012, hc[2] - 0.16))
        b('barbel', (0.05, 0.05, 0.36), mm('fin'), (sgn * 0.16, sn.front + 0.06, sn.bot - 0.16), rot=(0, sgn * 15, 0), bev=0.01)
        p('barbel_tip', (0.1, 0.1, 0.1), mm('glow'), (sgn * 0.2, sn.front + 0.06, sn.bot - 0.34))
    # fan frill behind the head (the silhouette)
    for i in range(7):
        ang = math.radians(-60 + i * 20)
        ln = 0.6 + 0.12 * (3 - abs(i - 3))
        b('frill_spine', (0.06, 0.06, ln), mm('dark'), (math.sin(ang) * ln * 0.5, Hd.back + 0.04, Hd.top - 0.1 + math.cos(ang) * ln * 0.5), rot=(0, math.degrees(ang), 0), bev=0.01)
        p('frill_web', (0.16, 0.04, ln * 0.8), mm('fin' if i % 2 else 'accent'), (math.sin(ang) * ln * 0.45, Hd.back + 0.06, Hd.top - 0.1 + math.cos(ang) * ln * 0.45), rot=(0, math.degrees(ang) + 10, 0))
    eyes(Hd, 0.38, 0.25, 0.14, iris='#2a8ab0', glow='#5ae8ff', lash=True, brow='#14706a', tilt=-6)
    for i in range(4):
        p('head_dot', (0.1, 0.1, 0.05), mm('coral'), ((i - 1.5) * 0.16, Hd.c.y, Hd.top + 0.02))
    for sgn, n in LR:
        p('gill', (0.04, 0.1, 0.3), mm('accent'), (sgn * 0.38, Hd.c.y + 0.16, hc[2] - 0.06))
    # two webbed legs (bird-like stance)
    for sgn, n in LR:
        sg('leg_' + n, 'body', (sgn * 0.34, 0.3, zc - 0.7))
        a.legs.append('leg_' + n)
        b('thigh', (0.32, 0.4, 0.5), mm('main'), (sgn * 0.36, 0.34, zc - 0.9), bev=0.05)
        b('shin', (0.2, 0.2, 0.5), mm('dark'), (sgn * 0.36, 0.46, zc - 1.26), bev=0.03)
        b('foot', (0.44, 0.5, 0.1), mm('fin'), (sgn * 0.36, 0.3, zc - 1.52), bev=0.03)
        for j in range(3):
            p('toe_claw', (0.07, 0.1, 0.07), mm('horn'), (sgn * 0.36 + (j - 1) * 0.14, 0.04, zc - 1.52))
    # tiny front claws
    for sgn, n in LR:
        sg('arm_' + n, 'body', (sgn * 0.4, -0.1, zc + 0.2))
        a.arms.append('arm_' + n)
        b('arm', (0.14, 0.14, 0.34), mm('main'), (sgn * 0.44, -0.16, zc + 0.04), rot=(-30, 0, 0), bev=0.03)
        p('claw', (0.16, 0.12, 0.1), mm('horn'), (sgn * 0.44, -0.26, zc - 0.12))
    # fin-sail wings: spines fanning up and back with webbing
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.42, 0.4, zc + 0.4))
        a.wings.append('wing_' + n)
        for i in range(5):
            ang = math.radians(10 + i * 18)
            ln = 1.2 + 0.25 * (2 - abs(i - 2))
            ex, ez = math.cos(ang) * ln, math.sin(ang) * ln
            b('wing_spine', (ln, 0.08, 0.08), mm('dark'), (sgn * (0.42 + ex / 2), 0.45 + i * 0.08, zc + 0.4 + ez / 2), rot=(0, -sgn * math.degrees(ang), 0), bev=0.02)
            p('wing_web', (ln * 0.9, 0.05, 0.22), mm('fin' if i % 2 else 'accent'), (sgn * (0.42 + ex * 0.48), 0.48 + i * 0.08, zc + 0.4 + ez * 0.48 - 0.12), rot=(0, -sgn * math.degrees(ang), 0))
            p('wing_tip', (0.12, 0.12, 0.12), mm('glow' if i % 2 else 'glow2'), (sgn * (0.42 + ex), 0.45 + i * 0.08, zc + 0.4 + ez), rot=(45, 45, 0))
    # long eel tail curling down with a fluke
    cur = Vector((0, 0.7, zc - 0.5))
    par = 'body'
    a.tail = []
    for i in range(4):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        w = 0.42 - 0.07 * i
        d = Vector((0, 0.45, -0.18 + 0.1 * i))
        b('tail', (w, 0.5, w), mm('main' if i % 2 == 0 else 'dark'), tuple(cur + d * 0.5), bev=0.05)
        p('tail_fin', (0.05, 0.36, w + 0.2), mm('fin'), tuple(cur + d * 0.5 + Vector((0, 0, w / 2 + 0.06))))
        for sgn, n in LR:
            p('tail_scale', (0.04, 0.2, w * 0.6), mm('dark' if i % 2 == 0 else 'main'), tuple(cur + d * 0.5 + Vector((sgn * (w / 2 + 0.01), 0, 0))))
            p('tail_spot', (0.04, 0.1, 0.1), mm('belly'), tuple(cur + d * 0.5 + Vector((sgn * (w / 2 + 0.015), 0.14, 0.06))))
        cur = cur + d
        par = nm
    b('fluke', (0.9, 0.3, 0.12), mm('fin'), tuple(cur + Vector((0, 0.16, 0))), bev=0.04)
    p('fluke_glow', (0.6, 0.12, 0.13), mm('glow'), tuple(cur + Vector((0, 0.26, 0))))
    use('body')
    # rarity 5: glowing coral tips and belly gem, bubble orbit, yellow aura (diamond style)
    sg('glow', 'body', (0, 0.2, zc))
    a.glow.append('glow')
    p('chest_pearl', (0.2, 0.08, 0.2), mm('glow2'), (0, -0.33, zc + 0.3), rot=(0, 45, 0))
    for sgn, n in LR:
        for j in range(3):
            p('coral_glow', (0.08, 0.08, 0.08), mm('glow'), (sgn * (0.3 + 0.12 * j), 0.3, zc + 0.6 + 0.14 * (2 - j) + 0.2 - 0.04 * j))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=hc, Chest=(0, -0.3, zc + 0.1), Hit=(0, 0.2, zc + 0.5))
    orbit_kit((0, 0.2, zc + 0.6), 1.6, 8, 'glow', 'glow2', size=0.12, dz=0.4, shape='bubble')
    aura_kit(1.4, 5, motes=10, mote_col='glow', height=2.2, style='diamond')
    return finish(a)


def azure_horseshoe_crab(row):
    a = start(row, dict(main='#3a7ad8', belly='#c8e0ff', dark='#1a3a8a', accent='#7ac8ff', shell2='#5a9af0', horn='#ffffff',
                        **{'*glow': '#5ae8ff', '*glow2': '#ffd21a', '*gold': '#ffd84a'}), 2.0)
    B, Hd = bug(bw=1.9, bl=1.4, bh=0.5, legh=0.24, hw=1.0, hd=0.34, hh=0.42, nleg=4, leg_w=0.1, leg_span=0.3, antenna=0, head_z=-0.02,
                shell='main', under='belly', leg_mat='dark')
    use('head')
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.06), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.12))
    eyes(Hd, 0.5, 0.25, 0.06, iris='#1a3a8a', glow='#5ae8ff', brow='#1a3a8a', tilt=8)
    use('body')
    # big horseshoe dome front shield + spiky rear shield + long tail spike (the silhouette)
    b('dome', (2.1, 1.3, 0.4), mm('main'), (0, B.c.y - 0.1, B.top + 0.12), bev=0.12)
    b('dome_ridge', (0.5, 1.2, 0.2), mm('shell2'), (0, B.c.y - 0.1, B.top + 0.38), bev=0.06)
    for sgn, n in LR:
        b('dome_wing', (0.5, 1.0, 0.24), mm('main'), (sgn * 1.06, B.c.y - 0.1, B.top - 0.04), rot=(0, sgn * 14, 0), bev=0.07)
        p('ridge_side', (0.12, 0.9, 0.12), mm('shell2'), (sgn * 0.6, B.c.y - 0.1, B.top + 0.33))
        for j in range(4):
            cn('rear_spike', 0.06, 0.24, mm('horn'), (sgn * 0.6, B.back + 0.1 + j * 0.14, B.c.z + 0.1), (sgn * 1, 0.2, 0.3))
        p('dome_eye', (0.14, 0.14, 0.06), mm('dark'), (sgn * 0.5, B.c.y - 0.4, B.top + 0.33))
    b('rear_shield', (1.1, 0.7, 0.36), mm('shell2'), (0, B.back + 0.3, B.c.z + 0.04), bev=0.08)
    for j in range(3):
        cn('ridge_spike', 0.07, 0.24, mm('horn'), (0, B.c.y - 0.5 + j * 0.4, B.top + 0.46), (0, 0.3, 1))
        p('dome_band', (1.6, 0.08, 0.05), mm('dark'), (0, B.c.y - 0.5 + j * 0.3, B.top + 0.33))
    for i in range(4):
        for j in range(3):
            p('dome_dot', (0.12, 0.12, 0.05), mm('accent'), ((i - 1.5) * 0.38, B.c.y - 0.6 + j * 0.45, B.top + 0.33))
    for sgn, n in LR:
        for j in range(4):
            p('rim_plate', (0.1, 0.2, 0.12), mm('dark'), (sgn * 1.32, B.c.y - 0.5 + j * 0.26, B.top - 0.04))
        for j in range(5):
            p('rear_band', (0.3, 0.06, 0.05), mm('dark'), (sgn * 0.26, B.back + 0.1 + j * 0.11, B.c.z + 0.23))
    for i in range(5):
        p('front_rim', (0.36, 0.1, 0.12), mm('dark'), ((i - 2) * 0.4, B.c.y - 0.76, B.top + 0.04))
        p('front_dot', (0.1, 0.06, 0.1), mm('accent'), ((i - 2) * 0.4, B.c.y - 0.83, B.top + 0.04))
    for i in range(8):
        p('under_gill', (0.4, 0.1, 0.04), mm('belly'), ((i % 2 - 0.5) * 0.5, B.c.y + 0.1 + (i // 2) * 0.16, B.bot - 0.06))
    sg('tail', 'body', (0, B.back + 0.6, B.c.z))
    a.tail = ['tail']
    b('telson', (0.14, 1.4, 0.14), mm('dark'), (0, B.back + 1.3, B.c.z - 0.04), rot=(-6, 0, 0), bev=0.03)
    p('telson_band', (0.18, 0.12, 0.18), mm('accent'), (0, B.back + 1.0, B.c.z - 0.02))
    # rarity 6: glowing azure rings on the shell, gem ridge, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i in range(6):
        ang = math.radians(i * 60)
        p('shell_ring', (0.2, 0.1, 0.06), mm('glow' if i % 2 else 'glow2'), (math.cos(ang) * 0.7, B.c.y - 0.1 + math.sin(ang) * 0.42, B.top + 0.34), rot=(0, 0, math.degrees(ang) + 90))
    for j in range(3):
        p('ridge_gem', (0.16, 0.16, 0.08), mm('glow'), (0, B.c.y - 0.5 + j * 0.4, B.top + 0.48), rot=(0, 0, 45))
    use('tail')
    b('telson_glow', (0.2, 0.3, 0.2), mm('glow'), (0, B.back + 2.0, B.c.z - 0.08), bev=0.04)
    use('head')
    halo_kit(Hd, 'gold', r=0.56, n=10, dz=1.0, kind='halo')
    use('body')
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_glow', (0.08, 0.12, 0.12), mm('glow'), (j.x + sgn * 0.2, j.y, j.z + 0.04))
    use('body')
    orbit_kit((0, 0.2, 1.2), 1.8, 6, 'glow', 'glow2', size=0.14, dz=0.3, shape='bubble')
    orbit_kit((0, 0.2, 0.8), 2.1, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.15, shape='gem')
    aura_kit(1.9, 6, motes=12, mote_col='glow', mote_r=2.0, height=1.6, style='diamond')
    return finish(a)


ANIMALS = dict(spiral_hermit_crab=spiral_hermit_crab, sea_turtle=sea_turtle, lagoon_pelican=lagoon_pelican, sea_lion=sea_lion,
               coral_wyvern=coral_wyvern, azure_horseshoe_crab=azure_horseshoe_crab)
