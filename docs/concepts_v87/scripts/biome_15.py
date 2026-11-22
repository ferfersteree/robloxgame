# Biome 15 - Crystal Caverns: amethyst geodes, crystal bridges, underground lakes
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 15
GROUND = '#6a5a8a'
SKY = '#c8b8e8'
THEME = dict(bits=['#b87aff', '#7ae8ff'], dust='#d8c8f0', glow='#c88aff', splash='#d0f0ff', bit_name='осколки кристаллов')
FOOT = dict(prism_moth=1.2, crystal_bat=1.2, crystal_anemone=1.25, quartz_dragon=1.35)
BUSH_NAME = 'аметистовая друза в каменной чаше с голубыми кристаллами и светящимся мхом'


def bush():
    B = begin_bush(NN)
    rk = mat('rock', '#5a5068')
    rk2 = mat('rock2', '#7a6e8a')
    am = mat('amethyst', '#a86af0', 'smooth')
    am2 = mat('amethyst2', '#d8a8ff', 'smooth')
    bl = mat('blue', '#6ad8ff', 'smooth')
    core = mat('core', '#e8c8ff', 'neon', 2.2)
    moss = mat('moss', '#7affc8', 'neon', 1.4)
    # geode bowl (split rock with a crystal heart)
    part('big', (0, 0.3, 0.2), 'bowl')
    b('bowl', (5.4, 2.8, 1.2), rk, (0, 0.3, 0.6), bev=0.16)
    b('bowl_rim', (5.0, 2.4, 0.3), rk2, (0, 0.3, 1.3), bev=0.1)
    b('bowl_in', (4.2, 1.8, 0.12), mat('in', '#3a2e4a'), (0, 0.3, 1.47), bev=0.04)
    for i, x in enumerate((-2.0, -0.6, 0.8, 2.1)):
        p('bowl_crack', (0.08, 0.05, 0.7), rk2, (x, -1.11, 0.6))
    # crystal clusters (the silhouette): tall square crystals with glowing cores
    spec = ((0, 0.4, 1.4, 1.5, am), (-1.3, 0.6, 1.4, 1.1, am2), (1.4, 0.5, 1.4, 1.2, bl), (-2.4, 0.2, 1.0, 0.8, bl), (2.5, 0.1, 1.0, 0.8, am),
            (-0.6, -0.5, 1.3, 0.7, bl), (0.8, -0.5, 1.3, 0.7, am2))
    for i, (x, y, z, s, m_) in enumerate(spec):
        part('big' if s > 1.0 else 'small', (x, y, z), 'cluster_%d' % i)
        cn('crystal', 0.3 * s, 2.0 * s, m_, (x, y, z), (0.05, 0.05, 1))
        cn('crystal', 0.2 * s, 1.3 * s, m_, (x + 0.32 * s, y + 0.1, z), (0.45, 0.1, 1))
        cn('crystal', 0.18 * s, 1.1 * s, am2 if m_ != am2 else bl, (x - 0.3 * s, y - 0.1, z), (-0.5, -0.1, 1))
        cn('crystal', 0.12 * s, 0.7 * s, m_, (x + 0.05, y - 0.3 * s, z), (0.1, -0.6, 1))
        p('crystal_core', (0.12 * s, 0.12 * s, 0.9 * s), core, (x, y, z + 0.7 * s))
    # glowing moss patches and small loose crystals
    for i, (x, y) in enumerate(((-2.0, -1.0), (0.0, -1.2), (1.9, -1.0), (-2.8, 0.9), (2.9, 0.9))):
        part('small', (x, y, 0.1), 'moss_%d' % i)
        b('moss', (0.7, 0.5, 0.14), moss, (x, y, 0.12), bev=0.04)
        cn('shard', 0.08, 0.4, am2 if i % 2 else bl, (x + 0.2, y, 0.18), (0.3, 0, 1))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def _moth_wings(a, B, span=1.6, depth=1.0, colA='main', colB='accent', z=0.0):
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * B.s.x / 2, B.c.y - 0.1, z))
        a.wings.append('wing_' + n)
        b('wing_up', (span * 0.6, depth, 0.08), mm(colA), (sgn * (B.s.x / 2 + span * 0.3), B.c.y - 0.2, z + 0.2), rot=(0, -sgn * 20, 0), bev=0.03)
        b('wing_low', (span * 0.45, depth * 0.7, 0.08), mm(colB), (sgn * (B.s.x / 2 + span * 0.22), B.c.y + 0.4, z - 0.24), rot=(0, sgn * 10, 0), bev=0.03)
        p('wing_eye', (0.26, 0.26, 0.09), mm('belly'), (sgn * (B.s.x / 2 + span * 0.4), B.c.y - 0.2, z + 0.28), rot=(0, -sgn * 20, 0))
        p('wing_eye_in', (0.12, 0.12, 0.1), mm('dark'), (sgn * (B.s.x / 2 + span * 0.4), B.c.y - 0.2, z + 0.28), rot=(0, -sgn * 20, 0))
        p('wing_rim', (span * 0.6, 0.08, 0.09), mm('dark'), (sgn * (B.s.x / 2 + span * 0.3), B.c.y - 0.2 - depth / 2, z + 0.2), rot=(0, -sgn * 20, 0))


def prism_moth(row):
    zc = 0.6
    a = start(row, dict(main='#c8b0ff', belly='#ffffff', dark='#5a4a8a', accent='#7ae8ff', fur='#f0e8ff'), 1.6, hover=2.6, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (0.5, 0.9, 0.5), mm('fur'), (0, 0.2, zc))
    b('abdomen', (0.4, 0.6, 0.4), mm('main'), (0, 0.8, zc - 0.05), bev=0.08)
    for j in range(3):
        p('abdomen_band', (0.42, 0.08, 0.42), mm('dark'), (0, 0.66 + j * 0.16, zc - 0.05))
    fluff(Box((0, B.front - 0.02, zc), (0.5, 0.1, 0.5)), 'f', mm('belly'), 3, 0.9, 0.3)
    sg('head', 'body', (0, -0.2, zc + 0.1))
    Hd = b('head', (0.66, 0.5, 0.56), mm('fur'), (0, -0.4, zc + 0.14))
    p('mouth', (0.14, 0.03, 0.04), mm('line'), (0, Hd.front - 0.012, zc - 0.04))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.22, Hd.front - 0.012, zc + 0.02))
        sg('antenna_' + n, 'head', (sgn * 0.16, -0.4, Hd.top))
        a.ears.append('antenna_' + n)
        b('antenna', (0.05, 0.05, 0.4), mm('dark'), (sgn * 0.2, -0.46, Hd.top + 0.2), rot=(-15, sgn * 20, 0), bev=0.01)
        b('antenna_plume', (0.2, 0.06, 0.2), mm('fur'), (sgn * 0.3, -0.52, Hd.top + 0.42), rot=(0, sgn * 20, 0), bev=0.02)
    use('head')
    eyes(Hd, 0.5, 0.25, 0.12, iris='#7a5ad8', lash=True, brow=None)
    use('body')
    _moth_wings(a, B, span=1.6, depth=1.0, colA='main', colB='accent', z=zc + 0.1)
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(3):
            p('prism_spot', (0.14, 0.14, 0.09), mm('accent' if j % 2 else 'belly'), (sgn * (B.s.x / 2 + 0.3 + j * 0.3), B.c.y - 0.1 + 0.1 * j, zc + 0.3 + 0.02 * j), rot=(0, -sgn * 20, 45))
        p('tail_tip', (0.2, 0.3, 0.09), mm('accent'), (sgn * (B.s.x / 2 + 0.4), B.c.y + 0.7, zc - 0.2))
    use('body')
    for sgn, n in LR:
        for j in range(3):
            p('leg', (0.05, 0.05, 0.3), mm('dark'), (sgn * 0.2, -0.1 + j * 0.2, zc - 0.38))
    tail_kit('stub', 'body', (0, 1.1, zc - 0.05), 'main', 'accent', size=0.12)
    use('body')
    grid(B, 'l', 3, 2, mm('belly'), (0.1, 0.1), name='fur_tuft')
    grid(B, 'r', 3, 2, mm('belly'), (0.1, 0.1), name='fur_tuft')
    grid(B, 't', 2, 3, mm('accent'), (0.1, 0.1), name='back_dot')
    use('head')
    grid(Hd, 't', 2, 2, mm('belly'), (0.12, 0.12), name='head_fluff')
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(4):
            p('wing_vein', (0.04, 0.5, 0.09), mm('dark'), (sgn * (B.s.x / 2 + 0.2 + j * 0.22), B.c.y - 0.2, zc + 0.3), rot=(0, -sgn * 20, sgn * 20))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, B.front - 0.05, zc), Hit=(0, 0.3, zc + 0.3))
    return finish(a)


def crystal_bat(row):
    zc = 0.6
    a = start(row, dict(main='#6a5a9a', belly='#c8b8f0', dark='#3a2e5a', accent='#a86af0', crystal='#d8a8ff', web='#8a7ac8'), 1.7, hover=3.0, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (0.7, 0.6, 0.7), mm('main'), (0, 0.1, zc))
    b('belly', (0.5, 0.1, 0.5), mm('belly'), (0, -0.22, zc - 0.04), bev=0.04)
    fluff(Box((0, -0.25, zc), (0.5, 0.1, 0.5)), 'f', mm('belly'), 3, 0.9, 0.3)
    sg('head', 'body', (0, -0.1, zc + 0.3))
    Hd = b('head', (0.8, 0.66, 0.66), mm('main'), (0, -0.14, zc + 0.6))
    mz = muzzle(Hd, (0.34, 0.16, 0.2), -0.26, 'belly', nose=(0.12, 0.06, 0.07), nose_mat='pink', fangs=1)
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.26, Hd.front - 0.012, Hd.c.z - 0.1))
    eyes(Hd, 0.38, 0.25, 0.12, iris='#a86af0', lash=True, brow='#3a2e5a', tilt=8)
    # big crystal ears (the silhouette)
    for sgn, n in LR:
        sg('ear_' + n, 'head', (sgn * 0.26, Hd.c.y, Hd.top))
        a.ears.append('ear_' + n)
        cn('ear', 0.2, 0.7, mm('crystal'), (sgn * 0.28, Hd.c.y, Hd.top - 0.04), (sgn * 0.3, 0, 1))
        cn('ear_in', 0.12, 0.5, mm('accent'), (sgn * 0.28, Hd.c.y - 0.12, Hd.top - 0.02), (sgn * 0.3, 0, 1))
    use('body')
    wings_big('body', (0.35, 0.1, zc + 0.15), span=1.6, depth=0.9, th=0.1, mat='web', bone='dark', web='accent', n=3, up=10)
    for sgn, n in LR:
        use('wing_' + n)
        for i in range(3):
            cn('wing_crystal', 0.06, 0.24, mm('crystal'), (sgn * (0.35 + 0.53 * (i + 1)), 0.1 + 0.8, zc + 0.15 + 0.05 * i), (sgn * 0.3, 0.5, 1))
    use('body')
    for sgn, n in LR:
        p('foot', (0.12, 0.14, 0.14), mm('dark'), (sgn * 0.16, 0.2, zc - 0.42))
    spots(B, 'lr', 4, mm('accent'), 0.1, seed=2, name='spot')
    cn('back_crystal', 0.1, 0.4, mm('crystal'), (0, 0.3, B.top - 0.02), (0, 0.3, 1))
    grid(B, 'k', 3, 2, mm('dark'), (0.12, 0.12), name='back_fur')
    use('head')
    grid(Hd, 't', 3, 2, mm('dark'), (0.1, 0.1), name='head_fur')
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc), Hit=(0, 0.1, zc + 0.3))
    return finish(a)


def geode_mole(row):
    """geode mole: lives inside a split-open geode egg - the round shell is its body/house, crystals inside, the mole leans out
    the front with huge pink digging hands and a star nose; miner lamp on the shell"""
    a = start(row, dict(main='#6a5a6a', belly='#d8c8d0', dark='#3a2e3a', accent='#ff9ac8', nose='#ff7aa8', shell='#8a8292', shell2='#b0a8b8',
                        crystal='#a86af0', crystal2='#6ad8ff'), 1.9)
    # the geode shell (body segment): a hollow box opened to the front, crystal lining inside
    sg('body', 'root', (0, 0.2, 0.6))
    B = b('shell_back', (1.5, 0.3, 1.3), mm('shell'), (0, 0.6, 0.7), bev=0.16)
    b('shell_floor', (1.5, 1.1, 0.24), mm('shell'), (0, 0.2, 0.12), bev=0.08)
    for sgn, n in LR:
        b('shell_side', (0.24, 1.0, 1.2), mm('shell'), (sgn * 0.66, 0.24, 0.66), bev=0.1)
        p('shell_crack', (0.26, 0.06, 0.6), mm('dark'), (sgn * 0.66, -0.25, 0.7), rot=(0, sgn * 20, 0))
        grid(Box((sgn * 0.66, 0.24, 0.66), (0.24, 1.0, 1.2)), 'l' if sgn < 0 else 'r', 3, 3, mm('shell2'), (0.14, 0.14), name='shell_spot')
    b('shell_top', (1.5, 1.0, 0.24), mm('shell2'), (0, 0.26, 1.34), bev=0.1)
    # crystal lining (inside)
    for i, (x, z, d, m_) in enumerate(((-0.4, 1.1, (0.3, 0.3, -1), 'crystal'), (0.4, 1.1, (-0.3, 0.3, -1), 'crystal2'), (-0.5, 0.4, (0.6, 0, 0.6), 'crystal2'),
                                       (0.5, 0.4, (-0.6, 0, 0.6), 'crystal'), (0, 1.1, (0, 0.2, -1), 'crystal'), (-0.2, 0.6, (0, -0.8, 0.2), 'crystal'),
                                       (0.24, 0.7, (0, -0.8, 0.3), 'crystal2'))):
        cn('lining', 0.1, 0.36, mm(m_), (x, 0.42, z), d)
    # the mole: head and arms leaning out of the front
    sg('head', 'body', (0, -0.1, 0.6))
    Hd = b('head', (0.84, 0.76, 0.7), mm('main'), (0, -0.36, 0.66))
    b('cheek_fur', (0.9, 0.4, 0.3), mm('belly'), (0, -0.44, 0.42), bev=0.06)
    for i in range(6):
        ang = math.radians(i * 60)
        p('nose_ray', (0.08, 0.1, 0.08), mm('nose'), (math.cos(ang) * 0.13, Hd.front - 0.04, 0.5 + math.sin(ang) * 0.13))
    p('nose_core', (0.14, 0.1, 0.14), mm('nose'), (0, Hd.front - 0.03, 0.5))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.3, Hd.front - 0.012, 0.58))
    eyes(Hd, 0.26, 0.24, 0.24, iris='#3a2e3a', brow='#3a2e3a', tilt=8, sleepy=0.24)
    for sgn, n in LR:
        sg('arm_' + n, 'body', (sgn * 0.42, -0.2, 0.5))
        a.arms.append('arm_' + n)
        b('arm', (0.2, 0.4, 0.2), mm('main'), (sgn * 0.48, -0.42, 0.4), rot=(-20, 0, 0), bev=0.04)
        b('hand', (0.4, 0.2, 0.36), mm('accent'), (sgn * 0.56, -0.66, 0.3), bev=0.06)
        for j in range(4):
            p('claw', (0.07, 0.14, 0.07), mm('belly'), (sgn * 0.56 + (j - 1.5) * 0.09, -0.8, 0.16))
    # miner lamp on top of the shell (accessory)
    use('body')
    setm('lamp', '#fff6c0')
    setm('hat', '#ffd84a')
    b('lamp_box', (0.3, 0.3, 0.2), mm('hat'), (0, -0.16, 1.54), bev=0.05)
    b('lamp', (0.2, 0.12, 0.16), mm('lamp'), (0, -0.34, 1.54), bev=0.03)
    p('lamp_rim', (0.24, 0.06, 0.2), mm('dark'), (0, -0.3, 1.54))
    for j in range(3):
        cn('top_crystal', 0.1, 0.36 - 0.06 * j, mm('crystal' if j % 2 else 'crystal2'), ((j - 1) * 0.36, 0.5, 1.44), ((j - 1) * 0.4, 0.2, 1))
    grid(Box((0, 0.26, 1.34), (1.5, 1.0, 0.24)), 't', 4, 3, mm('shell'), (0.14, 0.14), name='top_spot', th=0.04)
    grid(Box((0, 0.6, 0.7), (1.5, 0.3, 1.3)), 'k', 4, 3, mm('shell2'), (0.14, 0.14), name='back_spot')
    for i in range(6):
        p('rim_crystal', (0.08, 0.08, 0.16), mm('crystal2' if i % 2 else 'crystal'), ((i - 2.5) * 0.24, -0.24, 1.22), rot=(0, 0, 45))
    use('head')
    grid(Hd, 't', 3, 2, mm('belly'), (0.1, 0.1), name='head_fur')
    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='temple_fur')
    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='temple_fur')
    for sgn, n in LR:
        p('whisker', (0.26, 0.02, 0.02), mm('dark'), (sgn * 0.48, Hd.front + 0.04, 0.52), rot=(0, 0, sgn * 10))
        p('whisker', (0.26, 0.02, 0.02), mm('dark'), (sgn * 0.48, Hd.front + 0.04, 0.46), rot=(0, 0, sgn * 10))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.5, 0.4), Hit=(0, 0.3, 1.4))
    return finish(a)


def amethyst_fox(row):
    """amethyst fox with FIVE crystal tails spread behind it in a tall fan like a peacock, small slim body, crystal ear tips"""
    a = start(row, dict(main='#9a6ad8', belly='#f0e4ff', dark='#4a2a7a', accent='#c8a8ff', crystal='#e0c8ff',
                        **{'*glow': '#d8a8ff', '*glow2': '#ff9ae8'}), 3.16)
    B, Hd = quad(bw=0.7, bl=1.1, bh=0.6, legh=0.5, lw=0.18, hw=0.9, hd=0.76, hh=0.72, toe='dark', head_fwd=0.2)
    use('head')
    mz = muzzle(Hd, (0.32, 0.3, 0.22), -0.26, 'belly', nose=(0.1, 0.06, 0.08), nose_mat='dark')
    eyes(Hd, 0.34, 0.25, 0.1, iris='#4a2a7a', lash=True, brow='#4a2a7a', tilt=10)
    ears(Hd, 'point', 'main', 'pink', tip='crystal', x=0.32, h=0.5, w=0.28, lean=10)
    use('body')
    grid(B, 't', 2, 3, mm('accent'), (0.08, 0.08), name='back_gem', span=(0.5, 0.7), rot=(0, 0, 45))
    grid(B, 'l', 3, 2, mm('belly'), (0.08, 0.08), name='side_fleck', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('belly'), (0.08, 0.08), name='side_fleck', span=(0.7, 0.5))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('crystal_sock', (ft.s.x + 0.03, ft.s.y + 0.03, 0.08), mm('crystal'), (ft.c.x, ft.c.y, ft.top + 0.04))
    use('head')
    grid(Hd, 't', 2, 2, mm('accent'), (0.06, 0.06), name='head_gem', span=(0.4, 0.4))
    for sgn in (-1, 1):
        for j in range(2):
            p('whisker', (0.22, 0.02, 0.02), mm('dark'), (sgn * 0.3, Hd.front - 0.12, Hd.c.z - 0.12 + j * 0.05))
    use('body')
    # the five-tail crystal fan (the silhouette)
    sg('tail', 'body', a.tail_j)
    a.tail = ['tail']
    for k_ in range(5):
        ang = math.radians(-50 + k_ * 25)
        for j in range(4):
            r = 0.35 + j * 0.38
            s = 0.3 - 0.03 * j
            b('crystal_tail', (s, 0.16, s * 1.4), mm('main' if j < 2 else 'crystal'), (math.sin(ang) * r, a.tail_j[1] + 0.2, a.tail_j[2] + math.cos(ang) * r),
              rot=(0, math.degrees(ang), 0), bev=0.04)
        p('tail_gem', (0.16, 0.18, 0.24), mm('accent'), (math.sin(ang) * 1.95, a.tail_j[1] + 0.2, a.tail_j[2] + math.cos(ang) * 1.95), rot=(0, math.degrees(ang) + 45, 0))
    # rarity 4: glowing tail tips and back gems (glow segment)
    sg('glow', 'tail', (0, a.tail_j[1] + 0.2, a.tail_j[2] + 1.5))
    a.glow.append('glow')
    for k_ in range(5):
        ang = math.radians(-50 + k_ * 25)
        p('tip_glow', (0.1, 0.12, 0.1), mm('glow' if k_ % 2 else 'glow2'), (math.sin(ang) * 2.15, a.tail_j[1] + 0.2, a.tail_j[2] + math.cos(ang) * 2.15), rot=(45, 45, 0))
    use('body')
    aura_kit(1.4, 4, motes=8, mote_col='glow', height=2.6)
    return finish(a)


def crystal_anemone(row):
    a = start(row, dict(main='#7a5ab8', belly='#f0e0ff', dark='#3a2a6a', accent='#d8a8ff', crystal='#e8c8ff', blue='#6ad8ff',
                        **{'*glow': '#c88aff', '*glow2': '#7ae8ff'}), 3.3)
    B, Hd = blob(w=1.6, d=1.4, h=1.1, base=True)
    use('head')
    p('mouth', (0.4, 0.03, 0.05), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.2))
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.44, Hd.front - 0.012, Hd.c.z - 0.12))
    eyes(Hd, 0.44, 0.25, 0.08, iris='#a86af0', glow='#c88aff', lash=True, brow=None)
    use('body')
    # crystal tentacles: each its own segment so they sway (the silhouette)
    a.arms = []
    for i in range(12):
        ang = math.radians(i * 30 + 15)
        x, y = math.cos(ang) * 0.6, 0.1 + math.sin(ang) * 0.5
        nm = 'arm_%d' % (i + 1)
        sg(nm, 'body', (x, y, 1.1 + 0.1))
        a.arms.append(nm)
        h = 1.0 + 0.3 * (i % 3)
        b('tentacle', (0.2, 0.2, h), mm('main' if i % 2 else 'dark'), (x * 1.1, y + (y - 0.1) * 0.1, 1.2 + h / 2), rot=(-math.sin(ang) * 18, math.cos(ang) * 18, 0), bev=0.05)
        cn('tentacle_crystal', 0.14, 0.5, mm('crystal' if i % 2 else 'blue'), (x * 1.3, y + (y - 0.1) * 0.3, 1.2 + h), (math.cos(ang) * 0.4, math.sin(ang) * 0.4, 1))
        p('tentacle_ring', (0.24, 0.24, 0.06), mm('accent'), (x * 1.05, y + (y - 0.1) * 0.05, 1.3))
        p('tentacle_ring', (0.24, 0.24, 0.06), mm('accent'), (x * 1.08, y + (y - 0.1) * 0.08, 1.2 + h * 0.6))
        p('sucker', (0.08, 0.08, 0.08), mm('belly'), (x * 1.08 + 0.1, y + (y - 0.1) * 0.08, 1.2 + h * 0.35))
        p('sucker', (0.08, 0.08, 0.08), mm('belly'), (x * 1.1 + 0.1, y + (y - 0.1) * 0.1, 1.2 + h * 0.8))
    use('body')
    grid(B, 'l', 4, 3, mm('accent'), (0.12, 0.12), name='side_gem', rot=(45, 0, 0))
    grid(B, 'r', 4, 3, mm('accent'), (0.12, 0.12), name='side_gem', rot=(45, 0, 0))
    grid(B, 'k', 4, 3, mm('accent'), (0.12, 0.12), name='back_gem', rot=(0, 45, 0))
    grid(B, 't', 4, 3, mm('crystal'), (0.1, 0.1), name='top_gem', th=0.2, rot=(0, 0, 45))
    for i in range(16):
        ang = math.radians(i * 22.5)
        p('base_crystal', (0.14, 0.14, 0.3), mm('blue' if i % 2 else 'crystal'), (math.cos(ang) * 0.9, 0.1 + math.sin(ang) * 0.8, 0.2), rot=(0, 0, 45))

    def tent_idle(c, n):
        for i, nm in enumerate(a.arms):
            ph = i * 3
            for x, r in ((1, 0), (n // 4, 8), (n // 2, 0), (3 * n // 4, -8), (n, 0)):
                k(c, nm, min(n, max(1, x)), rot=(r if i % 2 else -r, r * 0.5, 0))
    a.extra_idle.append(tent_idle)
    # rarity 5: glowing tentacle tips (own segment), glowing core, orbiting shards, yellow aura
    sg('glow', 'body', (0, 0.1, 1.2))
    a.glow.append('glow')
    b('core', (0.5, 0.5, 0.3), mm('glow'), (0, 0.1, 1.26), rot=(0, 0, 45), bev=0.06)
    for i in range(4):
        p('core_ray', (0.08, 0.3, 0.06), mm('glow2'), (math.cos(i * 1.57) * 0.3, 0.1 + math.sin(i * 1.57) * 0.3, 1.3), rot=(0, 0, i * 90))
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', 0, 0.3, (0.2, 0.2), mm('glow2'), th=0.035, name='side_glow', rot=(45, 0, 0))
    orbit_kit((0, 0.1, 1.6), 1.6, 6, 'glow', 'glow2', size=0.15, dz=0.5)
    aura_kit(1.6, 5, motes=10, mote_col='glow', height=2.4)
    return finish(a)


def quartz_dragon(row):
    """crystal golem-dragon: wide low armoured body on short pillar legs, a folded fan of crystal slabs instead of membrane wings,
    blunt head with a forest of crystal horns, club tail with a crystal cluster"""
    a = start(row, dict(main='#b8b0d8', belly='#e8e4f8', dark='#5a4e7a', accent='#8a7ab8', crystal='#e8d8ff', blue='#8ae0ff', rock='#6a6088',
                        **{'*glow': '#c88aff', '*glow2': '#7ae8ff', '*gem': '#ff8ad8'}), 2.7)
    B, Hd = quad(bw=1.8, bl=1.9, bh=0.9, legh=0.36, lw=0.46, hw=1.5, hd=1.0, hh=0.98, head_up=0.3, toe='crystal', head_fwd=0.36,
                 leg_fl=0.6, ntoe=3, leg_mat='rock', foot='rock', rump=True, chest=False)
    use('head')
    # blunt boxy jaw
    b('jaw', (1.2, 0.5, 0.36), mm('rock'), (0, Hd.front - 0.12, Hd.bot + 0.1), bev=0.06)
    for i in range(6):
        p('tooth', (0.08, 0.06, 0.12), mm('crystal'), ((i - 2.5) * 0.18, Hd.front - 0.37, Hd.bot + 0.24))
    for sgn, n in LR:
        for j in range(2):
            p('cheek_crystal', (0.06, 0.12, 0.12), mm('blue'), (sgn * (Hd.s.x / 2 + 0.02), Hd.c.y - 0.1 + j * 0.24, Hd.c.z), rot=(45, 0, 0))
    for sgn, n in LR:
        p('nostril', (0.1, 0.04, 0.06), mm('line'), (sgn * 0.2, Hd.front - 0.012, Hd.c.z - 0.06))
        p('blush', (0.18, 0.03, 0.09), mm('pink'), (sgn * 0.48, Hd.front - 0.012, Hd.c.z - 0.2))
    eyes(Hd, 0.3, 0.27, 0.16, iris='#5a3aa8', glow='#c88aff', brow='#5a4e7a', tilt=-14)
    # forest of crystal horns on the head (the silhouette)
    for i, (x, y, h, d) in enumerate(((0, 0.0, 0.9, (0, 0.2, 1)), (-0.36, 0.1, 0.7, (-0.5, 0.3, 1)), (0.36, 0.1, 0.7, (0.5, 0.3, 1)),
                                      (-0.5, 0.3, 0.5, (-0.8, 0.5, 0.6)), (0.5, 0.3, 0.5, (0.8, 0.5, 0.6)), (0, 0.3, 0.5, (0, 0.8, 0.8)))):
        cn('horn_crystal', 0.12 + 0.03 * (i == 0), h, mm('crystal' if i % 2 == 0 else 'blue'), (x, Hd.c.y + y, Hd.top - 0.04), d)
    use('body')
    # armour: rows of square rock plates with crystal studs (no membrane, no scales)
    for i in range(4):
        for j in range(4):
            b('plate', (0.4, 0.4, 0.14), mm('rock' if (i + j) % 2 else 'main'), ((i - 1.5) * 0.44, B.front + 0.26 + j * 0.46, B.top + 0.06), bev=0.04)
    for sgn, n in LR:
        for j in range(4):
            b('side_plate', (0.12, 0.4, 0.5), mm('rock'), (sgn * (B.s.x / 2 + 0.05), B.front + 0.26 + j * 0.46, B.c.z), bev=0.04)
            cn('side_crystal', 0.08, 0.3, mm('blue'), (sgn * (B.s.x / 2 + 0.12), B.front + 0.26 + j * 0.46, B.c.z + 0.1), (sgn * 1, 0, 0.4))
    b('belly', (1.4, 1.6, 0.1), mm('belly'), (0, B.c.y, B.bot - 0.02), bev=0.03)
    # folded crystal-slab "wings": two fans of tall flat crystals rising from the shoulders, leaning outwards
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.6, B.front + 0.5, B.top))
        a.wings.append('wing_' + n)
        for i in range(5):
            h = 1.6 - 0.22 * i
            x = sgn * (0.6 + 0.16 * i)
            y = B.front + 0.5 + i * 0.32
            b('slab', (0.14, 0.42, h), mm('crystal' if i % 2 == 0 else 'blue'), (x + sgn * h * 0.18, y, B.top + h / 2), rot=(0, sgn * 20, 0), bev=0.03)
            p('slab_edge', (0.16, 0.08, h * 0.9), mm('dark'), (x + sgn * h * 0.18, y + 0.2, B.top + h / 2), rot=(0, sgn * 20, 0))
            cn('slab_tip', 0.12, 0.3, mm('crystal'), (x + sgn * h * 0.36, y, B.top + h - 0.02), (sgn * 0.35, 0, 1))
    # short pillar legs get crystal knee caps
    for ft in a.bx['feet']:
        use(ft.seg)
        b('knee_cap', (ft.s.x + 0.06, ft.s.y * 0.8, 0.16), mm('main'), (ft.c.x, ft.c.y + 0.06, 0.34), bev=0.04)
        cn('knee_crystal', 0.07, 0.24, mm('blue'), (ft.c.x, ft.front + 0.1, 0.4), (0, -0.6, 0.8))
    use('body')
    # club tail ending in a crystal cluster
    tail_kit('thick', 'body', a.tail_j, 'rock', 'main', size=0.26)
    use('tail')
    for i, (dx, dz, d) in enumerate(((0, 0.2, (0, 0.6, 1)), (-0.2, 0.0, (-0.8, 0.4, 0.6)), (0.2, 0.0, (0.8, 0.4, 0.6)), (0, -0.1, (0, 1, 0.2)))):
        cn('club_crystal', 0.1, 0.45, mm('crystal' if i % 2 else 'blue'), (dx, a.tail_j[1] + 0.26 * 4.2, a.tail_j[2] - 0.08 + dz), d)
    # rarity 6: glowing gem cores in the slabs and plates, a floating ring of shards (not a gold crown), shard orbit, red aura (rays)
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i in range(4):
        p('plate_gem', (0.16, 0.16, 0.06), mm('glow' if i % 2 else 'glow2'), ((i - 1.5) * 0.44, B.front + 0.95, B.top + 0.16), rot=(0, 0, 45))
    p('chest_gem', (0.3, 0.08, 0.3), mm('gem'), (0, B.front - 0.06, B.c.z), rot=(0, 45, 0))
    for sgn, n in LR:
        use('wing_' + n)
        for i in range(5):
            h = 1.6 - 0.22 * i
            p('slab_core', (0.15, 0.2, h * 0.5), mm('glow' if i % 2 == 0 else 'glow2'), (sgn * (0.6 + 0.16 * i) + sgn * h * 0.18, B.front + 0.5 + i * 0.32, B.top + h / 2), rot=(0, sgn * 20, 0))
    use('head')
    halo_kit(Hd, 'glow2', r=0.7, n=10, dz=1.2, kind='shards')
    use('body')
    orbit_kit((0, 0.3, 1.6), 2.0, 8, 'glow', 'glow2', size=0.14, dz=0.4, shape='shard')
    aura_kit(2.1, 6, motes=12, mote_col='glow', mote_r=2.2, height=2.4, style='rays')
    return finish(a)


ANIMALS = dict(prism_moth=prism_moth, crystal_bat=crystal_bat, geode_mole=geode_mole, amethyst_fox=amethyst_fox,
               crystal_anemone=crystal_anemone, quartz_dragon=quartz_dragon)
