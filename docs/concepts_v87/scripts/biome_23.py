# Biome 23 - Sunken Citadel: drowned towers, deep blue water, glowing sea life
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 23
GROUND = '#2e5a7a'
SKY = '#5a8ab8'
THEME = dict(bits=['#8ae8ff', '#ff9ad0'], dust='#4a7a9a', glow='#8ae8ff', splash='#c8f0ff', bit_name='пузырьки и светящийся планктон')
FOOT = dict(abyss_octopus=1.3, pressure_colossus=1.15, trench_angler=1.1)
BUSH_NAME = 'подводный куст: обломок колонны цитадели в водорослях-лентах, кораллы-веера и светящиеся пузырьки'


def bush():
    B = begin_bush(NN)
    stone = mat('stone', '#8a9ab0')
    stone2 = mat('stone2', '#b8c8d8')
    kelp = mat('kelp', '#3a8a6a')
    kelp2 = mat('kelp2', '#5ab88a')
    coral = mat('coral', '#ff7a9a')
    coral2 = mat('coral2', '#ffb04a')
    sand = mat('sand', '#c8b88a')
    glow = mat('glow', '#8ae8ff', 'neon', 2.4)
    part('big', (0, 0.3, 0.2), 'base')
    b('sand', (6.2, 2.6, 0.4), sand, (0, 0.3, 0.2), bev=0.15)
    # fallen column + standing broken column
    b('fallen_column', (3.4, 0.9, 0.9), stone, (-0.9, 0.5, 0.85), rot=(0, 0, 8), bev=0.1)
    for x in (-2.4, -1.4, -0.4, 0.6):
        p('flute', (0.1, 0.94, 0.94), stone2, (x, 0.5, 0.85))
    part('big', (1.8, 0.6, 1.6), 'column')
    b('column', (0.9, 0.9, 2.8), stone, (1.8, 0.6, 1.8), bev=0.08)
    b('capital', (1.3, 1.3, 0.3), stone2, (1.8, 0.6, 3.3), bev=0.06)
    p('break', (0.6, 0.6, 0.2), stone2, (1.7, 0.6, 3.55), rot=(15, 10, 0))
    # kelp ribbons
    for i, (x, h) in enumerate(((-2.6, 4.2), (-0.2, 4.5), (0.9, 3.6), (2.8, 3.8))):
        part('big' if h > 4 else 'small', (x, 0.0, h * 0.5), 'kelp_%d' % i)
        for j in range(int(h / 0.6)):
            p('kelp', (0.3, 0.1, 0.6), kelp if j % 2 else kelp2, (x + 0.12 * math.sin(j * 1.2), 0.0, 0.5 + j * 0.6), rot=(0, 15 * math.sin(j * 1.2), 0))
        p('kelp_bulb', (0.2, 0.2, 0.2), glow, (x, 0.0, h + 0.1))
    # fan corals
    for i, (x, m_) in enumerate(((-1.6, coral), (0.4, coral2), (2.6, coral))):
        part('small', (x, -0.6, 1.0), 'coral_%d' % i)
        b('coral_fan', (0.9, 0.12, 0.9), m_, (x, -0.6, 0.9), rot=(0, 45, 0), bev=0.04)
        p('coral_dot', (0.16, 0.14, 0.16), glow, (x, -0.68, 1.0))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def abyss_sea_urchin(row):
    """a round sea urchin with long spines sticking out in every direction, a tiny happy face peeking out of the spines,
    little tube feet underneath"""
    a = start(row, dict(main='#6a3a9a', belly='#c8a8e8', dark='#2e1a4a', accent='#ff9ad0', spine='#3a1e6a', tip='#e8c8ff', blush='#ff9ab4'), 2.16)
    zc = 0.6
    sg('body', 'root', (0, 0, zc))
    B = b('body', (1.0, 1.0, 0.9), mm('main'), (0, 0, zc), bev=0.22)
    # long spines on a fibonacci sphere (the silhouette); leave a gap at the face
    n = 34
    for i in range(n):
        z = 1 - (i + 0.5) / n * 2
        r = math.sqrt(1 - z * z)
        th = i * 2.39996
        d = Vector((math.cos(th) * r, math.sin(th) * r, z))
        if d.y < -0.6 and abs(d.z) < 0.55:
            continue
        if d.z < -0.55:
            continue
        ln = 0.9
        c = Vector((0, 0, zc)) + d * (0.45 + ln / 2)
        ry = math.degrees(math.atan2(d.x, d.z))
        rx = -math.degrees(math.asin(max(-1.0, min(1.0, d.y))))
        p('spine', (0.08, 0.08, ln), mm('spine'), tuple(c), rot=(rx, ry, 0))
        p('spine_tip', (0.1, 0.1, 0.1), mm('tip'), tuple(Vector((0, 0, zc)) + d * (0.45 + ln)), rot=(45, 45, 0))
    sg('head', 'body', (0, -0.4, zc))
    Hd = Box((0, 0, zc), (1.0, 1.0, 0.9), 'head')
    eyes(Hd, 0.3, 0.2, 0.06, iris='#ff9ad0', brow=None, lash=True)
    p('smile', (0.16, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, zc - 0.16))
    for sgn, n_ in LR:
        p('blush', (0.1, 0.03, 0.05), mm('blush'), (sgn * 0.26, Hd.front - 0.012, zc - 0.1))
    use('body')
    for sgn, n_ in LR:
        nm = 'leg_' + n_
        sg(nm, 'body', (sgn * 0.25, 0, 0.15))
        a.legs.append(nm)
        for t in range(5):
            p('tube_foot', (0.08, 0.08, 0.16), mm('belly'), (sgn * 0.25, (t - 2) * 0.16, 0.08))
    grid(B, 'u', 3, 3, mm('belly'), (0.12, 0.12), name='under_dot', span=(0.6, 0.6))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, -0.3, zc), Chest=(0, -0.5, zc), Hit=(0, 0, zc + 0.4))
    a.tail = []
    return finish(a)


def citadel_cuttlefish(row):
    """cuttlefish swimming level: oval mantle with a rippling fin skirt all around the edge, zebra stripes,
    big W-pupil eyes, a short bundle of arms in front"""
    zc = 0.6
    a = start(row, dict(main='#e8b06a', belly='#fff0d8', dark='#6a3a1e', accent='#ff8ac8', fin='#ffd8a8', stripe='#8a4a2a', blush='#ff9ab4'),
              0.98, hover=2.2, z0=zc)
    sg('body', 'root', (0, 0.3, zc))
    B = b('mantle', (1.0, 1.8, 0.7), mm('main'), (0, 0.4, zc), bev=0.2)
    b('mantle_top', (0.7, 1.4, 0.2), mm('main'), (0, 0.45, zc + 0.4), bev=0.08)
    for j in range(6):
        p('zebra', (0.72, 0.1, 0.06), mm('stripe'), (0, -0.15 + j * 0.24, zc + 0.5))
    # rippling fin skirt (the silhouette)
    sg('fin', 'body', (0, 0.4, zc))
    a.wings.append('fin')
    for j in range(9):
        y = -0.4 + j * 0.2
        for sgn in (-1, 1):
            p('fin_wave', (0.5, 0.22, 0.06), mm('fin'), (sgn * 0.72, y, zc - 0.05 + 0.08 * math.sin(j * 1.4)), rot=(0, sgn * 15 * math.sin(j * 1.4), 0))
    p('fin_back', (0.6, 0.24, 0.06), mm('fin'), (0, 1.38, zc - 0.05))
    sg('head', 'body', (0, -0.5, zc))
    Hd = b('head', (0.9, 0.6, 0.6), mm('main'), (0, -0.75, zc), bev=0.14)
    eyes(Hd, 0.4, 0.28, 0.12, iris='#3a2a1a', brow=None, lash=True)
    for sgn, n in LR:
        p('w_pupil', (0.16, 0.04, 0.05), mm('dark'), (sgn * 0.25, Hd.front - 0.04, zc + 0.12))
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.3, Hd.front - 0.012, zc - 0.1))
    # short arm bundle
    use('head')
    for i in range(6):
        x = (i - 2.5) * 0.12
        nm = None
        p('arm', (0.1, 0.5, 0.1), mm('accent' if i % 2 else 'main'), (x, Hd.front - 0.24, zc - 0.15 - 0.03 * abs(i - 2.5)), rot=(15, 0, 0))
    for sgn, n in LR:
        nm = 'tent_' + n
        sg(nm, 'head', (sgn * 0.2, Hd.front, zc - 0.15))
        a.arms.append(nm)
        b('long_tentacle', (0.1, 0.5, 0.1), mm('accent'), (sgn * 0.3, Hd.front - 0.3, zc - 0.22), rot=(15, 0, sgn * 15), bev=0.02)
        p('club', (0.16, 0.18, 0.12), mm('accent'), (sgn * 0.38, Hd.front - 0.56, zc - 0.3))
    grid(Hd, 't', 2, 2, mm('stripe'), (0.08, 0.08), name='head_stripe', span=(0.6, 0.5))
    use('body')
    grid(B, 'l', 4, 2, mm('stripe'), (0.08, 0.08), name='side_spot', span=(0.8, 0.5))
    grid(B, 'r', 4, 2, mm('stripe'), (0.08, 0.08), name='side_spot', span=(0.8, 0.5))
    grid(B, 'u', 2, 4, mm('belly'), (0.12, 0.12), name='belly_dot', span=(0.6, 0.8))
    sg('tail', 'body', (0, 1.2, zc))
    a.tail = ['tail']
    p('tail_tip', (0.4, 0.3, 0.3), mm('main'), (0, 1.35, zc))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -1.0, zc), Hit=(0, 0.4, zc + 0.4))
    return finish(a)


def cathedral_clam(row):
    """a giant clam standing open; the upper shell rim is a pointed cathedral arch with stained-glass ribs,
    a big pearl inside, a sleepy face on the soft mantle"""
    a = start(row, dict(main='#c8d0e0', belly='#f0f4ff', dark='#4a5a7a', accent='#8a6ac8', mantle='#ff9ad0', glass1='#6ac8ff', glass2='#ffd84a',
                        glass3='#ff6a8a', pearl='#fff8f0', blush='#ff9ab4'), 3.0)
    sg('body', 'root', (0, 0.2, 0.4))
    B = b('lower_shell', (2.2, 1.4, 0.6), mm('main'), (0, 0.2, 0.3), bev=0.2)
    for j in range(9):
        p('shell_rib', (0.1, 1.44, 0.5), mm('belly'), ((j - 4) * 0.22, 0.2, 0.32))
    grid(B, 'l', 2, 2, mm('dark'), (0.1, 0.1), name='shell_dot', span=(0.6, 0.5))
    grid(B, 'r', 2, 2, mm('dark'), (0.1, 0.1), name='shell_dot', span=(0.6, 0.5))
    grid(B, 'k', 4, 1, mm('dark'), (0.1, 0.1), name='shell_dot', span=(0.8, 0.1))
    for k_ in range(6):
        p('barnacle', (0.14, 0.14, 0.1), mm('stone') if False else mm('belly'), (-0.9 + k_ * 0.36, 0.7, 0.62))
    b('mantle', (1.9, 1.2, 0.4), mm('mantle'), (0, 0.02, 0.7), bev=0.12)
    for k_ in range(16):
        p('mantle_frill', (0.12, 0.12, 0.14), mm('accent'), (-0.9 + k_ * 0.12, -0.6, 0.86 + 0.05 * (k_ % 2)))
    # pearl
    sg('pearl', 'body', (0, 0.6, 0.9))
    a.ears.append('pearl')
    for k_ in range(6):
        ang = math.radians(k_ * 60)
        p('pearl_cup', (0.14, 0.14, 0.1), mm('accent'), (math.cos(ang) * 0.3, 0.3 + math.sin(ang) * 0.3, 0.86))
    # upper shell: a pointed cathedral arch standing up behind (the silhouette)
    sg('head', 'body', (0, 0.8, 0.6))
    Hd = Box((0, 0.15, 0.68), (1.9, 1.1, 0.36), 'head')
    for i in range(7):
        th = math.radians(180 - i * 30)
        x = math.cos(th) * 1.0
        z = 0.6 + math.sin(th) * 1.4 + (0.5 if i == 3 else 0.25 * (1 - abs(i - 3) / 3.0))
        b('arch', (0.42, 0.3, 0.42), mm('main'), (x, 0.85, z), rot=(0, 45 if i == 3 else 0, 0), bev=0.06)
        p('arch_stud', (0.12, 0.08, 0.12), mm('accent'), (x, 0.68, z))
    b('spire', (0.24, 0.26, 0.6), mm('main'), (0, 0.85, 2.6), bev=0.04)
    p('spire_tip', (0.12, 0.12, 0.2), mm('glass2'), (0, 0.85, 2.96))
    for k_ in range(4):
        p('spire_rib', (0.28, 0.3, 0.05), mm('dark'), (0, 0.85, 2.4 + k_ * 0.14))
    for j, (x, z, m_) in enumerate(((-0.25, 0.75, 'glass2'), (0.25, 0.75, 'glass1'), (-0.75, 0.75, 'glass3'), (0.75, 0.75, 'glass1'),
                                    (-0.25, 1.85, 'glass1'), (0.25, 1.85, 'glass3'))):
        p('glass_small', (0.2, 0.1, 0.22), mm(m_), (x, 0.88, z))
    # stained glass panes inside the arch
    for j, (x, z, m_) in enumerate(((-0.5, 1.0, 'glass1'), (0.0, 1.0, 'glass2'), (0.5, 1.0, 'glass3'), (-0.3, 1.6, 'glass3'), (0.3, 1.6, 'glass1'),
                                    (0.0, 2.1, 'glass2'), (-0.65, 1.5, 'glass2'), (0.65, 1.5, 'glass3'))):
        p('glass', (0.36, 0.1, 0.42), mm(m_), (x, 0.88, z))
    for j in range(3):
        p('lead_v', (0.06, 0.12, 1.4), mm('dark'), ((j - 1) * 0.26, 0.86, 1.5))
    for j in range(2):
        p('lead_h', (1.5, 0.12, 0.06), mm('dark'), (0, 0.86, 1.3 + j * 0.55))
    # the big pearl is the face
    use('head')
    PB = b('pearl', (0.9, 0.8, 0.86), mm('pearl'), (0, 0.05, 1.28), bev=0.26)
    p('pearl_shine', (0.12, 0.06, 0.12), mm('white'), (-0.26, PB.front - 0.01, 1.56))
    eyes(PB, 0.3, 0.22, 0.08, iris='#8a6ac8', brow=None, lash=True)
    p('smile', (0.2, 0.03, 0.04), mm('dark'), (0, PB.front - 0.012, 1.1))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.28, PB.front - 0.012, 1.16))
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.6, 0.2, 0.1))
        a.legs.append(nm)
        p('foot', (0.3, 0.4, 0.1), mm('mantle'), (sgn * 0.6, 0.2, 0.04))
        for t in range(3):
            p('foot_toe', (0.08, 0.08, 0.06), mm('accent'), (sgn * 0.6 + (t - 1) * 0.1, -0.02, 0.03))
    grid(B, 'f', 4, 1, mm('dark'), (0.1, 0.1), name='shell_dot', span=(0.8, 0.1))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, 0.15, 0.8), Chest=(0, -0.6, 0.5), Hit=(0, 0.3, 1.2))
    a.tail = []
    return finish(a)


def trench_angler(row):
    """trench angler: a round pale pink balloon fish floating upright, a huge open grin full of soft teeth,
    a long bent rod from the forehead hanging a glowing lure in front of its face, tiny fins"""
    zc = 1.0
    a = start(row, dict(main='#ffc8d8', belly='#fff0f4', dark='#8a3a5a', accent='#ff8ab4', tooth='#ffffff', fin='#ffd8e8', blush='#ff6a9a',
                        **{'*glow': '#8affe8', '*glow2': '#ffe68a'}), 2.33, hover=2.4, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (1.6, 1.4, 1.6), mm('main'), (0, 0.1, zc), bev=0.36)
    b('belly', (1.2, 0.1, 0.8), mm('belly'), (0, -0.62, zc - 0.4), bev=0.04)
    grid(B, 't', 3, 3, mm('accent'), (0.1, 0.1), name='spot', span=(0.6, 0.6))
    grid(B, 'l', 3, 3, mm('accent'), (0.1, 0.1), name='spot', span=(0.6, 0.6))
    grid(B, 'r', 3, 3, mm('accent'), (0.1, 0.1), name='spot', span=(0.6, 0.6))
    grid(B, 'k', 3, 3, mm('accent'), (0.1, 0.1), name='spot', span=(0.6, 0.6))
    grid(B, 'u', 3, 3, mm('belly'), (0.12, 0.12), name='under_dot', span=(0.6, 0.6))
    for j in range(4):
        p('dorsal_spike', (0.06, 0.1, 0.2), mm('accent'), (0, 0.1 + j * 0.16, zc + 1.0 + 0.04 * j))
    sg('head', 'body', (0, -0.5, zc + 0.2))
    Hd = Box((0, 0.1, zc + 0.35), (1.6, 1.4, 0.9), 'head')
    eyes(Hd, 0.36, 0.24, 0.24, iris='#8a3a5a', brow=None)
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('blush'), (sgn * 0.5, -0.612, zc + 0.2))
    # huge grin (the silhouette): dark mouth with teeth rows
    b('mouth', (1.1, 0.12, 0.5), mm('dark'), (0, -0.6, zc - 0.25), bev=0.06)
    for t in range(8):
        p('tooth_top', (0.08, 0.08, 0.14), mm('tooth'), ((t - 3.5) * 0.13, -0.67, zc - 0.06))
        p('tooth_bot', (0.08, 0.08, 0.12), mm('tooth'), ((t - 3.5) * 0.13 + 0.06, -0.67, zc - 0.44))
    p('tongue', (0.4, 0.06, 0.12), mm('accent'), (0, -0.64, zc - 0.4))
    # the rod and lure
    sg('lure', 'head', (0, -0.2, zc + 0.8))
    a.ears.append('lure')
    for j, (y, z) in enumerate(((-0.25, 1.0), (-0.45, 1.3), (-0.75, 1.45), (-1.05, 1.35))):
        p('rod', (0.08, 0.24, 0.08), mm('dark'), (0, y, zc + z), rot=(60 - j * 40, 0, 0))
    p('line', (0.04, 0.04, 0.4), mm('dark'), (0, -1.15, zc + 1.05))
    # fins
    use('body')
    for sgn, n in LR:
        nm = 'fin_' + n
        sg(nm, 'body', (sgn * 0.8, 0.1, zc))
        a.wings.append(nm)
        b('side_fin', (0.4, 0.3, 0.1), mm('fin'), (sgn * 0.96, 0.2, zc - 0.1), rot=(0, sgn * -20, 0), bev=0.03)
        for t in range(4):
            p('fin_ray', (0.36, 0.04, 0.04), mm('accent'), (sgn * 0.96, 0.08 + t * 0.08, zc - 0.1))
    sg('tail', 'body', (0, 0.8, zc))
    a.tail = ['tail']
    b('tail_stalk', (0.3, 0.4, 0.3), mm('main'), (0, 0.95, zc - 0.1), bev=0.06)
    b('tail_fin', (0.1, 0.4, 0.7), mm('fin'), (0, 1.2, zc - 0.1), bev=0.03)
    for t in range(3):
        p('tail_ray', (0.12, 0.36, 0.04), mm('accent'), (0, 1.2, zc - 0.35 + t * 0.25))
    p('dorsal', (0.1, 0.5, 0.3), mm('fin'), (0, 0.4, zc + 0.9))
    # rarity 4: glowing lure and photophores (glow segment)
    sg('glow', 'lure', (0, -1.15, zc + 0.75))
    a.glow.append('glow')
    b('lure_bulb', (0.34, 0.34, 0.34), mm('glow'), (0, -1.15, zc + 0.75), rot=(45, 45, 0), bev=0.06)
    p('lure_ring', (0.44, 0.06, 0.06), mm('glow2'), (0, -1.15, zc + 0.75))
    use('body')
    for sgn in (-1, 1):
        for j in range(7):
            p('photophore', (0.04, 0.08, 0.08), mm('glow'), (sgn * 0.81, -0.4 + j * 0.15, zc - 0.5))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, -0.3, zc + 0.3), Chest=(0, -0.7, zc - 0.2), Hit=(0, 0.1, zc + 0.6))
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=2.4)
    return finish(a)


def pressure_colossus(row):
    """pressure colossus: a giant in an old brass diving suit: a round helmet with three portholes (the face looks out
    of the front one), bulky canvas body, lead boots, clamp hands, an air hose looping to a tank on its back"""
    a = start(row, dict(main='#c8a86a', belly='#e8d8b0', dark='#3a3a48', accent='#d88a3a', brass='#e0b84a', canvas='#6a8aa8', lead='#4a4a58',
                        glass='#9ad8ff', face='#ffd8c0', blush='#ff9ab4', **{'*glow': '#8ae8ff', '*glow2': '#ffe68a'}), 5.23)
    B, Hd = biped(tw=1.6, td=1.2, th=1.4, legh=0.8, lw=0.56, hw=1.2, hd=1.2, hh=1.1, arm_l=1.1, arm_w=0.42, hand=0.5, ntoe=0,
                  foot='lead', toe='dark', hand_mat='dark')
    use('body')
    grid(B, 'f', 3, 3, mm('belly'), (0.14, 0.14), name='canvas_patch', span=(0.6, 0.6))
    grid(B, 'l', 2, 3, mm('belly'), (0.14, 0.14), name='canvas_patch', span=(0.6, 0.6))
    grid(B, 'r', 2, 3, mm('belly'), (0.14, 0.14), name='canvas_patch', span=(0.6, 0.6))
    p('chest_plate', (1.0, 0.1, 0.5), mm('brass'), (0, B.front - 0.02, B.top - 0.3))
    for k_ in range(10):
        p('plate_bolt', (0.06, 0.06, 0.06), mm('dark'), ((k_ - 4.5) * 0.1, B.front - 0.06, B.top - 0.08))
    p('belt', (B.s.x + 0.08, B.s.y + 0.08, 0.16), mm('lead'), (0, B.c.y, B.c.z - B.s.z * 0.3))
    for k_ in range(6):
        p('belt_weight', (0.2, 0.12, 0.24), mm('lead'), ((k_ - 2.5) * 0.26, B.front - 0.05, B.c.z - B.s.z * 0.3))
    # air tank on the back with the hose
    b('tank', (0.7, 0.5, 1.2), mm('brass'), (0, B.back + 0.25, B.c.z + 0.1), bev=0.16)
    for j in range(2):
        p('tank_band', (0.74, 0.54, 0.08), mm('dark'), (0, B.back + 0.25, B.c.z - 0.3 + j * 0.7))
    p('tank_valve', (0.2, 0.2, 0.2), mm('accent'), (0, B.back + 0.25, B.c.z + 0.8))
    for k_ in range(6):
        p('tank_rivet', (0.06, 0.06, 0.06), mm('dark'), ((k_ % 3 - 1) * 0.2, B.back + 0.51, B.c.z - 0.2 + (k_ // 3) * 0.6))
    for j in range(10):
        ang = math.radians(j * 18)
        p('hose', (0.16, 0.16, 0.24), mm('dark'), (0.5 + math.sin(ang) * 0.3, B.back + 0.1 - math.sin(ang) * 0.3, B.top + 0.1 + math.cos(ang) * 0.3))
    # helmet (the silhouette): round brass dome with 3 portholes
    use('head')
    b('helmet', (Hd.s.x + 0.2, Hd.s.y + 0.2, Hd.s.z + 0.2), mm('brass'), tuple(Hd.c), bev=0.32)
    b('collar', (Hd.s.x + 0.4, Hd.s.y + 0.4, 0.2), mm('accent'), (Hd.c.x, Hd.c.y, Hd.bot - 0.1), bev=0.06)
    for k_ in range(8):
        ang = math.radians(k_ * 45)
        p('collar_bolt', (0.1, 0.1, 0.1), mm('dark'), (math.cos(ang) * (Hd.s.x / 2 + 0.2), Hd.c.y + math.sin(ang) * (Hd.s.y / 2 + 0.2), Hd.bot - 0.02))
    b('porthole', (0.8, 0.14, 0.7), mm('accent'), (0, Hd.front - 0.12, Hd.c.z), bev=0.08)
    p('porthole_glass', (0.66, 0.1, 0.56), mm('face'), (0, Hd.front - 0.17, Hd.c.z))
    for k_ in range(8):
        ang = math.radians(k_ * 45)
        p('port_rivet', (0.06, 0.06, 0.06), mm('dark'), (math.cos(ang) * 0.44, Hd.front - 0.2, Hd.c.z + math.sin(ang) * 0.4))
    for j in range(2):
        p('helmet_band', (Hd.s.x + 0.24, Hd.s.y + 0.24, 0.06), mm('accent'), (Hd.c.x, Hd.c.y, Hd.c.z + 0.42 + j * 0.12))
    eyes(Box((0, Hd.c.y, Hd.c.z), (0.66, Hd.s.y + 0.36, 0.56), 'head'), 0.4, 0.26, 0.05, iris='#3a5a8a', brow=None)
    p('smile', (0.16, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.31, Hd.c.z - 0.16))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('blush'), (sgn * 0.2, Hd.front - 0.31, Hd.c.z - 0.1))
        b('side_port', (0.14, 0.5, 0.5), mm('accent'), (sgn * (Hd.s.x / 2 + 0.1), Hd.c.y, Hd.c.z), bev=0.06)
        p('side_glass', (0.1, 0.36, 0.36), mm('glass'), (sgn * (Hd.s.x / 2 + 0.16), Hd.c.y, Hd.c.z))
        for t in range(3):
            p('side_rivet', (0.06, 0.06, 0.06), mm('dark'), (sgn * (Hd.s.x / 2 + 0.17), Hd.c.y + (t - 1) * 0.2, Hd.c.z - 0.3))
    p('top_valve', (0.24, 0.24, 0.24), mm('accent'), (0, Hd.c.y, Hd.top + 0.14))
    # clamp hands
    for sgn, n in LR:
        use('arm_' + n)
        hb = a.bx['hands'][0 if sgn < 0 else 1] if 'hands' in a.bx else None
        hx, hy, hz = (hb.c.x, hb.c.y, hb.c.z) if hb else (sgn * 1.2, 0.0, 1.2)
        for t in (-1, 1):
            b('clamp', (0.14, 0.2, 0.4), mm('lead'), (hx + t * 0.16, hy - 0.1, hz - 0.3), bev=0.03)
        p('wrist_ring', (0.5, 0.5, 0.1), mm('brass'), (hx, hy, hz + 0.3))
        for t in range(3):
            p('arm_band', (0.48, 0.48, 0.06), mm('belly'), (hx, hy, hz + 0.45 + t * 0.12))
        for t in (-1, 1):
            for q in range(2):
                p('clamp_tooth', (0.06, 0.08, 0.08), mm('brass'), (hx + t * 0.1, hy - 0.2, hz - 0.4 - q * 0.14))
        p('elbow_pad', (0.46, 0.46, 0.2), mm('brass'), (hx, hy, hz + 0.75))
    # lead boots
    for sgn, n in LR:
        use('leg_' + n)
        p('boot_lead', (0.7, 0.8, 0.2), mm('lead'), (sgn * 0.42, 0.0, 0.1))
        p('boot_strap', (0.62, 0.1, 0.1), mm('brass'), (sgn * 0.42, -0.4, 0.3))
        p('knee_pad', (0.5, 0.2, 0.3), mm('brass'), (sgn * 0.42, -0.3, 0.6))
        for t in range(3):
            p('leg_stitch', (0.56, 0.06, 0.04), mm('belly'), (sgn * 0.42, -0.29, 0.25 + t * 0.12))
        p('buckle', (0.12, 0.06, 0.12), mm('dark'), (sgn * 0.42, -0.46, 0.3))
    # rarity 5: glowing portholes rim + bubbles stream (glow segment), orbit, yellow aura
    use('head')
    for sgn in (-1, 1):
        p('port_glow', (0.06, 0.4, 0.06), mm('glow'), (sgn * (Hd.s.x / 2 + 0.17), Hd.c.y, Hd.c.z + 0.22))
    sg('glow', 'head', (0, Hd.c.y, Hd.top + 0.3))
    a.glow.append('glow')
    for i in range(6):
        b('bubble', (0.14 + 0.04 * i, 0.14 + 0.04 * i, 0.14 + 0.04 * i), mm('glow' if i % 2 else 'glow2'),
          (0.1 * math.sin(i * 2.0), Hd.c.y + 0.1 * math.cos(i * 2.0), Hd.top + 0.4 + i * 0.3), bev=0.04)
    use('body')
    a.bx.update(body=B, head=Hd)
    orbit_kit((0, 0.2, B.c.z + 0.6), 2.2, 6, 'glow', 'glow2', size=0.16, dz=0.4, shape='bubble')
    aura_kit(2.0, 5, motes=10, mote_col='glow', height=3.0, style='ring')
    return finish(a)


def abyss_octopus(row):
    """abyss octopus floating with eight arms spread wide like a star, each arm tip curled up;
    a round head that wears a little sunken-citadel tower with a glowing window and a flag"""
    zc = 1.0
    a = start(row, dict(main='#8a3ab8', belly='#e8b8ff', dark='#2e1450', accent='#ff8ac8', sucker='#ffd8f0', stone='#b8c8d8', stone2='#8a9ab0',
                        roof='#3a6ab8', flag='#ffd84a', blush='#ff9ab4', **{'*glow': '#8ae8ff', '*glow2': '#ffe68a', '*glow3': '#ff6ad0'}),
              4.14, hover=2.6, z0=zc)
    sg('body', 'root', (0, 0, zc))
    B = b('mantle', (1.4, 1.3, 1.2), mm('main'), (0, 0.1, zc + 0.3), bev=0.3)
    b('skirt', (1.6, 1.5, 0.3), mm('main'), (0, 0.1, zc - 0.25), bev=0.12)
    sg('head', 'body', (0, -0.3, zc + 0.3))
    Hd = Box((0, 0.1, zc + 0.2), (1.4, 1.3, 1.0), 'head')
    eyes(Hd, 0.34, 0.25, 0.08, iris='#ffe68a', glow='#ffe68a', brow='#2e1450', lash=True)
    p('smile', (0.22, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, zc - 0.05))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('blush'), (sgn * 0.42, Hd.front - 0.012, zc + 0.02))
    grid(B, 'l', 2, 2, mm('belly'), (0.12, 0.12), name='spot', span=(0.6, 0.5))
    grid(B, 'r', 2, 2, mm('belly'), (0.12, 0.12), name='spot', span=(0.6, 0.5))
    grid(B, 'k', 3, 2, mm('belly'), (0.12, 0.12), name='spot', span=(0.6, 0.5))
    # the citadel tower on the head (the silhouette)
    TZ = zc + 0.9
    b('tower', (0.7, 0.7, 1.2), mm('stone'), (0, 0.15, TZ + 0.6), bev=0.06)
    for k_ in range(4):
        for sgn in (-1, 1):
            p('brick', (0.26, 0.06, 0.12), mm('stone2'), (sgn * 0.16, -0.21, TZ + 0.2 + k_ * 0.26 + (0.06 if sgn > 0 else 0)))
    for k_ in range(4):
        ang = math.radians(k_ * 90 + 45)
        p('battlement', (0.2, 0.2, 0.2), mm('stone'), (math.cos(ang) * 0.3, 0.15 + math.sin(ang) * 0.3, TZ + 1.3))
    b('roof', (0.6, 0.6, 0.5), mm('roof'), (0, 0.15, TZ + 1.55), rot=(0, 0, 45), bev=0.06)
    p('roof_tip', (0.24, 0.24, 0.3), mm('roof'), (0, 0.15, TZ + 1.9), rot=(0, 0, 45))
    p('flag_pole', (0.04, 0.04, 0.5), mm('dark'), (0, 0.15, TZ + 2.2))
    p('flag', (0.3, 0.04, 0.2), mm('flag'), (0.17, 0.15, TZ + 2.34))
    p('door', (0.24, 0.06, 0.34), mm('dark'), (0, -0.21, TZ + 0.2))
    # eight spread arms with curled tips
    a.tail = []
    for i in range(8):
        ang = math.radians(i * 45 + 22.5)
        dx, dy = math.cos(ang), math.sin(ang)
        nm = 'arm_%d' % i
        sg(nm, 'body', (dx * 0.6, 0.1 + dy * 0.6, zc - 0.3))
        (a.arms if i in (2, 5) else a.tail).append(nm)
        for j in range(4):
            r = 0.75 + j * 0.42
            z = zc - 0.4 - 0.06 * j + (0.25 * (j - 2) if j >= 3 else 0)
            s = 0.4 - 0.06 * j
            b('arm_seg', (s, s, s * 0.8), mm('main' if j % 2 == 0 else 'belly'), (dx * r, 0.1 + dy * r, z), rot=(0, 0, math.degrees(ang)), bev=0.06)
            p('sucker', (s * 0.4, s * 0.4, 0.06), mm('sucker'), (dx * r, 0.1 + dy * r, z - s * 0.42))
        p('arm_curl', (0.2, 0.2, 0.3), mm('accent'), (dx * 2.25, 0.1 + dy * 2.25, zc - 0.2))
    # rarity 6: glowing window, arm-tip lights, crown, two orbits, red aura
    sg('glow', 'head', (0, 0.15, TZ + 0.8))
    a.glow.append('glow')
    p('window', (0.24, 0.08, 0.3), mm('glow2'), (0, -0.21, TZ + 0.85))
    for sgn in (-1, 1):
        p('side_window', (0.08, 0.2, 0.24), mm('glow2'), (sgn * 0.36, 0.15, TZ + 0.7))
    for i in range(8):
        ang = math.radians(i * 45 + 22.5)
        use('arm_%d' % i)
        p('tip_glow', (0.12, 0.12, 0.12), mm('glow' if i % 2 else 'glow3'), (math.cos(ang) * 2.25, 0.1 + math.sin(ang) * 2.25, zc + 0.0), rot=(45, 45, 0))
    halo_kit(Box((0, 0.15, TZ + 1.4), (0.7, 0.7, 0.3), 'head'), 'glow2', r=0.5, n=6, dz=0.9, kind='stars')
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, -0.2, zc + 0.3), Chest=(0, -0.6, zc), Hit=(0, 0.1, zc + 0.8))
    orbit_kit((0, 0.1, zc + 0.6), 3.0, 6, 'glow', 'glow3', size=0.16, dz=0.5, shape='bubble')
    orbit_kit((0, 0.1, zc - 0.3), 3.4, 8, 'glow2', 'glow', size=0.1, name='orbit2', dz=0.2, shape='star')
    aura_kit(2.8, 6, motes=12, mote_col='glow', height=3.6, style='petals')
    return finish(a)


ANIMALS = dict(abyss_sea_urchin=abyss_sea_urchin, citadel_cuttlefish=citadel_cuttlefish, cathedral_clam=cathedral_clam,
               trench_angler=trench_angler, pressure_colossus=pressure_colossus, abyss_octopus=abyss_octopus)
