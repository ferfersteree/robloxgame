# Biome 21 - Fungal Bogs: giant mushrooms, glowing caps, peat pools, mycelium threads
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 21
GROUND = '#4a5a3a'
SKY = '#b8c8a0'
THEME = dict(bits=['#c86a8a', '#e8d0a0'], dust='#7a8a5a', glow='#8affc8', splash='#6a7a4a', bit_name='споры и клочки мха')
FOOT = dict(spore_marauder=1.15, cap_mantis=1.25, mycelium_bloomstalker=1.05)
BUSH_NAME = 'грибной куст: кочка мха с торфяной лужей, грибы-зонтики разной высоты и светящиеся опята'


def bush():
    B = begin_bush(NN)
    moss = mat('moss', '#5a7a3a')
    moss2 = mat('moss2', '#7a9a4a')
    peat = mat('peat', '#3a2a1e')
    water = mat('pool', '#4a6a5a')
    stem = mat('stem', '#f0e8d0')
    cap = mat('cap', '#c84a5a')
    cap2 = mat('cap2', '#d88a4a')
    dot = mat('dot', '#fff8e8')
    glow = mat('glow', '#8affc8', 'neon', 2.4)
    part('big', (0, 0.3, 0.3), 'mound')
    b('mound', (6.0, 2.6, 0.6), moss, (0, 0.3, 0.3), bev=0.2)
    b('mound_top', (4.6, 2.0, 0.3), moss2, (0, 0.3, 0.7), bev=0.1)
    p('pool', (1.4, 0.8, 0.06), water, (2.0, -0.4, 0.62))
    p('peat', (1.6, 1.0, 0.04), peat, (2.0, -0.4, 0.6))
    spec = ((0.0, 0.5, 3.8, 1.9, cap), (-1.7, 0.4, 3.0, 1.6, cap2), (1.6, 0.6, 3.4, 1.5, cap), (-2.6, 0.0, 1.8, 1.0, cap), (-0.8, -0.3, 1.8, 0.9, cap2))
    for i, (x, y, h, s, m_) in enumerate(spec):
        part('big' if s > 1.2 else 'small', (x, y, h), 'shroom_%d' % i)
        b('stem', (0.3 * s, 0.3 * s, h - 0.8), stem, (x, y, 0.8 + (h - 0.8) / 2), bev=0.05)
        b('cap', (s * 1.2, s * 1.2, s * 0.4), m_, (x, y, h + s * 0.1), bev=0.12 * s)
        b('cap_top', (s * 0.8, s * 0.8, s * 0.24), m_, (x, y, h + s * 0.4), bev=0.08)
        p('gills', (s * 1.1, s * 1.1, 0.06), stem, (x, y, h - s * 0.1))
        for j in range(4):
            ang = math.radians(j * 90 + 45)
            p('cap_dot', (0.14 * s, 0.14 * s, 0.06), dot, (x + math.cos(ang) * s * 0.36, y + math.sin(ang) * s * 0.36, h + s * 0.53))
    for i, (x, y) in enumerate(((2.6, 0.6), (-0.4, 1.0), (0.9, -0.5))):
        part('small', (x, y, 1.0), 'glow_%d' % i)
        for j in range(3):
            p('honey_stem', (0.08, 0.08, 0.3 + 0.1 * j), stem, (x + (j - 1) * 0.16, y, 0.95 + 0.05 * j))
            b('honey_cap', (0.24, 0.24, 0.1), glow, (x + (j - 1) * 0.16, y, 1.15 + 0.1 * j), bev=0.03)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def shelf_millipede(row):
    """a low millipede: a chain of round segments, each carrying a bracket-fungus shelf on its back, lots of tiny legs, two curled antennae"""
    a = start(row, dict(main='#6a4a3a', belly='#c8a888', dark='#2e1e16', accent='#e8a84a', shelf='#d8b878', shelf2='#a8c86a', leg='#3a2a20'), 0.94)
    sg('body', 'root', (0, 0.0, 0.3))
    B = b('seg0', (0.6, 0.5, 0.5), mm('main'), (0, 0.0, 0.32), bev=0.1)
    sg('head', 'body', (0, -0.25, 0.32))
    Hd = b('head', (0.66, 0.46, 0.54), mm('main'), (0, -0.46, 0.36), bev=0.12)
    eyes(Hd, 0.34, 0.26, 0.12, iris='#2e1e16', brow=None)
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('accent'), (sgn * 0.22, Hd.front - 0.012, 0.24))
        nm = 'antenna_' + n
        sg(nm, 'head', (sgn * 0.16, -0.5, Hd.top))
        a.ears.append(nm)
        p('antenna', (0.05, 0.05, 0.3), mm('dark'), (sgn * 0.2, -0.52, Hd.top + 0.15), rot=(-20, sgn * 20, 0))
        p('antenna_curl', (0.14, 0.05, 0.05), mm('dark'), (sgn * 0.28, -0.6, Hd.top + 0.3))
    p('mouth', (0.14, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 0.18))
    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='head_dot', span=(0.5, 0.5))
    for sgn in (-1, 1):
        p('mandible', (0.06, 0.08, 0.06), mm('dark'), (sgn * 0.1, Hd.front - 0.04, 0.12))
    use('body')
    par = 'body'
    a.tail = []
    for i in range(6):
        y = 0.45 + i * 0.45
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, (0, y - 0.22, 0.3))
        a.tail.append(nm)
        w = 0.62 - 0.03 * i
        b('seg', (w, 0.44, 0.48), mm('main' if i % 2 else 'belly'), (0, y, 0.3), bev=0.1)
        b('shelf', (w + 0.3, 0.36, 0.1), mm('shelf' if i % 2 == 0 else 'shelf2'), (0.08 * (1 if i % 2 else -1), y, 0.6), bev=0.03)
        p('shelf_rim', (w + 0.34, 0.06, 0.06), mm('accent'), (0.08 * (1 if i % 2 else -1), y - 0.17, 0.6))
        p('shelf_dot', (0.1, 0.1, 0.04), mm('belly'), (0.08 * (1 if i % 2 else -1) + 0.15, y, 0.66))
        for sgn, n in LR:
            for t in range(2):
                p('leg', (0.18, 0.05, 0.05), mm('leg'), (sgn * (w / 2 + 0.08), y - 0.1 + t * 0.2, 0.08), rot=(0, sgn * -30, 0))
        par = nm
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.3, 0, 0.2))
        a.legs.append(nm)
        for t in range(2):
            p('leg', (0.18, 0.05, 0.05), mm('leg'), (sgn * 0.38, -0.1 + t * 0.2, 0.08), rot=(0, sgn * -30, 0))
    use('tail6')
    p('tail_tip', (0.3, 0.2, 0.3), mm('accent'), (0, 2.85, 0.3), rot=(0, 45, 0))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.7, 0.3), Hit=(0, 1.0, 0.6))
    return finish(a)


def peat_leech(row):
    """peat leech arched into a tall loop like an inchworm: both ends on the ground, round sucker foot behind,
    smiling head in front, moss tufts and stripes along the arch"""
    a = start(row, dict(main='#5a3a2a', belly='#c88a6a', dark='#2a1a12', accent='#e8c84a', moss='#7aa04a', blush='#ff9ab4'), 1.4)
    sg('body', 'root', (0, 0.0, 0.3))
    B = None
    n_s = 9
    for i in range(n_s):
        th = math.radians(180 - i * 180 / (n_s - 1))
        y = math.cos(th) * 0.7
        z = 0.25 + math.sin(th) * 0.9
        w = 0.5 - 0.02 * abs(i - 4)
        bx = b('arch', (w, 0.36, 0.36), mm('main' if i % 2 else 'dark'), (0, -y, z), rot=(math.degrees(th) - 90, 0, 0), bev=0.08)
        if i == 4:
            B = bx
        p('arch_belly', (w * 0.7, 0.3, 0.06), mm('belly'), (0, -y + math.cos(th) * 0.0, z - 0.19 * math.sin(th) - 0.01), rot=(math.degrees(th) - 90, 0, 0))
        for sgn in (-1, 1):
            p('stripe', (0.04, 0.3, 0.1), mm('accent'), (sgn * (w / 2 + 0.01), -y, z))
        if i % 2 == 0:
            p('moss', (0.2, 0.2, 0.1), mm('moss'), (0.06 * (i % 3 - 1), -y, z + 0.2))
    # sucker foot at the back end
    sg('tail', 'body', (0, 0.7, 0.25))
    a.tail = ['tail']
    b('sucker', (0.6, 0.6, 0.16), mm('belly'), (0, 0.7, 0.08), bev=0.05)
    p('sucker_ring', (0.4, 0.4, 0.04), mm('dark'), (0, 0.7, 0.17))
    # head at the front end
    sg('head', 'body', (0, -0.7, 0.4))
    Hd = b('head', (0.64, 0.5, 0.56), mm('main'), (0, -0.75, 0.32), bev=0.14)
    eyes(Hd, 0.34, 0.26, 0.14, iris='#e8c84a', brow=None, lash=True)
    p('smile', (0.2, 0.03, 0.04), mm('belly'), (0, Hd.front - 0.012, 0.18))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('blush'), (sgn * 0.22, Hd.front - 0.012, 0.24))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.2, -0.75, Hd.top))
        a.ears.append(nm)
        p('moss_tuft', (0.16, 0.16, 0.16), mm('moss'), (sgn * 0.16, -0.75, Hd.top + 0.06))
    grid(Hd, 't', 2, 2, mm('accent'), (0.06, 0.06), name='head_dot', span=(0.5, 0.5))
    grid(Hd, 'l', 2, 2, mm('accent'), (0.06, 0.06), name='side_dot', span=(0.5, 0.5))
    grid(Hd, 'r', 2, 2, mm('accent'), (0.06, 0.06), name='side_dot', span=(0.5, 0.5))
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.2, 0.0, 0.3))
        a.legs.append(nm)
        for t in range(4):
            p('nub', (0.08, 0.08, 0.08), mm('belly'), (sgn * 0.22, -0.55 + t * 0.36, 0.06))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -1.0, 0.3), Hit=(0, 0, 1.1))
    return finish(a)


def lantern_slug(row):
    """slug carrying a three-tier pagoda of glowing mushroom caps on its back, long eye stalks, frilly mantle skirt"""
    a = start(row, dict(main='#e8a8c8', belly='#fff0f4', dark='#8a4a6a', accent='#ffe08a', cap='#c86a8a', cap2='#e89a6a', blush='#ff8ab4',
                        **{'*lamp': '#ffe08a'}), 2.4)
    sg('body', 'root', (0, 0.2, 0.3))
    B = b('foot', (0.9, 2.2, 0.4), mm('main'), (0, 0.3, 0.2), bev=0.14)
    b('back', (0.8, 1.4, 0.4), mm('main'), (0, 0.2, 0.55), bev=0.14)
    for j in range(10):
        for sgn in (-1, 1):
            p('mantle_frill', (0.08, 0.18, 0.14), mm('belly'), (sgn * 0.47, -0.6 + j * 0.2, 0.16))
    for j in range(6):
        for sgn in (-1, 1):
            p('back_stripe', (0.04, 0.16, 0.24), mm('dark'), (sgn * 0.41, -0.3 + j * 0.2, 0.56))
    for j in range(4):
        p('tail_ridge', (0.12, 0.16, 0.08), mm('dark'), (0, 1.0 + j * 0.16, 0.42 - j * 0.05))
    grid(B, 'k', 2, 1, mm('dark'), (0.12, 0.12), name='tail_spot', span=(0.6, 0.1))
    p('tail_tip', (0.4, 0.3, 0.2), mm('main'), (0, 1.5, 0.12))
    # pagoda of glowing mushroom caps on the back (the silhouette)
    sg('pagoda', 'body', (0, 0.3, 0.75))
    a.ears.append('pagoda')
    for i, (s, z) in enumerate(((1.3, 1.0), (1.0, 1.55), (0.7, 2.05))):
        b('pagoda_stem', (0.2, 0.2, 0.5), mm('belly'), (0, 0.3, z - 0.25), bev=0.03)
        b('pagoda_cap', (s, s, 0.24), mm('cap' if i % 2 == 0 else 'cap2'), (0, 0.3, z), bev=0.08)
        p('cap_gill', (s * 0.9, s * 0.9, 0.04), mm('belly'), (0, 0.3, z - 0.14))
        for k_ in range(8):
            ang = math.radians(k_ * 45 + 22)
            p('cap_lamp', (0.1, 0.1, 0.14), mm('lamp'), (math.cos(ang) * s * 0.44, 0.3 + math.sin(ang) * s * 0.44, z - 0.22))
        grid(Box((0, 0.3, z), (s, s, 0.24)), 't', 2, 2, mm('belly'), (0.1, 0.1), name='cap_spot', span=(0.6, 0.6))
    p('pagoda_tip', (0.14, 0.14, 0.24), mm('lamp'), (0, 0.3, 2.3))
    # head with long eye stalks
    sg('head', 'body', (0, -0.7, 0.4))
    Hd = b('head', (0.76, 0.5, 0.56), mm('main'), (0, -0.86, 0.36), bev=0.14)
    p('smile', (0.2, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 0.24))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.24, Hd.front - 0.012, 0.3))
        nm = 'stalk_' + n
        sg(nm, 'head', (sgn * 0.2, -0.86, Hd.top))
        b('eye_stalk', (0.1, 0.1, 0.6), mm('main'), (sgn * 0.26, -0.86, Hd.top + 0.3), rot=(0, sgn * 14, 0), bev=0.03)
        b('stalk_ball', (0.3, 0.26, 0.3), mm('belly'), (sgn * 0.33, -0.86, Hd.top + 0.66), bev=0.08)
        p('eye_dot', (0.14, 0.04, 0.16), mm('dark'), (sgn * 0.33, -1.0, Hd.top + 0.68))
        p('eye_shine', (0.05, 0.05, 0.05), mm('white'), (sgn * 0.3, -1.02, Hd.top + 0.72))
        p('stalk_ring', (0.14, 0.14, 0.05), mm('dark'), (sgn * 0.28, -0.86, Hd.top + 0.42))
    for sgn, n in LR:
        nm = 'tent_' + n
        sg(nm, 'head', (sgn * 0.2, Hd.front, 0.2))
        a.ears.append(nm)
        p('feeler', (0.08, 0.2, 0.08), mm('main'), (sgn * 0.22, Hd.front - 0.08, 0.14))
    grid(Hd, 't', 2, 2, mm('belly'), (0.08, 0.08), name='head_dot', span=(0.5, 0.5))
    grid(Hd, 'l', 2, 2, mm('dark'), (0.07, 0.07), name='cheek_dot', span=(0.5, 0.5))
    grid(Hd, 'r', 2, 2, mm('dark'), (0.07, 0.07), name='cheek_dot', span=(0.5, 0.5))
    use('body')
    grid(Box((0, 0.2, 0.55), (0.8, 1.4, 0.4)), 'l', 4, 1, mm('dark'), (0.1, 0.1), name='side_spot', span=(0.8, 0.1))
    grid(Box((0, 0.2, 0.55), (0.8, 1.4, 0.4)), 'r', 4, 1, mm('dark'), (0.1, 0.1), name='side_spot', span=(0.8, 0.1))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -1.1, 0.3), Hit=(0, 0.2, 0.9))
    a.tail = []
    return finish(a)


def mycelium_bloomstalker(row):
    """a walking mushroom: a thick stem body with a face, a huge drooping bell cap like a hat, root legs,
    two long mycelium-thread arms ending in little flowers"""
    a = start(row, dict(main='#f0e8d0', belly='#fff8ec', dark='#5a4a3a', accent='#8a5ac8', cap='#6a4ab8', cap2='#9a7ae0', root='#a88a5a',
                        flower='#ff8ac8', blush='#ff9ab4', **{'*glow': '#8affc8', '*glow2': '#d8a8ff'}), 4.05)
    LEG = 0.6
    sg('body', 'root', (0, 0, LEG + 0.8))
    B = b('stem', (1.0, 0.9, 1.6), mm('main'), (0, 0, LEG + 0.8), bev=0.16)
    p('stem_ring', (1.1, 1.0, 0.16), mm('belly'), (0, 0, LEG + 1.2))
    for j in range(3):
        p('stem_band', (1.04, 0.94, 0.06), mm('root'), (0, 0, LEG + 1.2 + j * 0.18))
    grid(B, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='stem_spot', span=(0.6, 0.5))
    grid(B, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='stem_spot', span=(0.6, 0.5))
    grid(B, 'k', 2, 3, mm('belly'), (0.1, 0.1), name='stem_spot', span=(0.6, 0.6))
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.28, 0, LEG))
        a.legs.append(nm)
        b('root_leg', (0.34, 0.4, LEG), mm('root'), (sgn * 0.28, 0, LEG / 2), bev=0.05)
        for t in range(5):
            p('root_toe', (0.08, 0.24, 0.1), mm('root'), (sgn * 0.28 + (t - 2) * 0.08, -0.24, 0.05), rot=(0, 0, (t - 2) * 18))
    # face on the stem
    sg('head', 'body', (0, 0, LEG + 1.4))
    Hd = Box((0, 0, LEG + 0.62), (1.0, 0.9, 0.9), 'head')
    eyes(Hd, 0.32, 0.24, 0.16, iris='#6a4ab8', brow=None, lash=True)
    p('smile', (0.24, 0.03, 0.05), mm('dark'), (0, -0.462, LEG + 0.46))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('blush'), (sgn * 0.3, -0.462, LEG + 0.54))
    # the huge drooping cap (the silhouette)
    zc = LEG + 1.95
    b('cap', (2.4, 2.2, 0.5), mm('cap'), (0, 0.05, zc), bev=0.18)
    b('cap_top', (1.7, 1.6, 0.4), mm('cap'), (0, 0.05, zc + 0.4), bev=0.14)
    b('cap_crown', (0.9, 0.9, 0.24), mm('cap2'), (0, 0.05, zc + 0.68), bev=0.08)
    for k_ in range(12):
        ang = math.radians(k_ * 30)
        p('cap_droop', (0.36, 0.36, 0.3), mm('cap2' if k_ % 2 else 'cap'), (math.cos(ang) * 1.12, 0.05 + math.sin(ang) * 1.02, zc - 0.3), rot=(0, 0, k_ * 30))
    p('gills', (2.2, 2.0, 0.06), mm('belly'), (0, 0.05, zc - 0.27))
    for k_ in range(4):
        ang = math.radians(k_ * 90)
        p('cap_rim', (0.5, 0.5, 0.08), mm('belly'), (math.cos(ang) * 0.75, 0.05 + math.sin(ang) * 0.7, zc + 0.22), rot=(0, 0, k_ * 90))
    for k_ in range(12):
        ang = math.radians(k_ * 30 + 15)
        p('gill_line', (0.7, 0.04, 0.05), mm('dark'), (math.cos(ang) * 0.75, 0.05 + math.sin(ang) * 0.7, zc - 0.31), rot=(0, 0, k_ * 30 + 15))
    grid(Box((0, 0.05, zc + 0.4), (1.7, 1.6, 0.4)), 't', 3, 3, mm('belly'), (0.16, 0.16), name='cap_spot', span=(0.7, 0.7))
    # mycelium arms with flowers
    use('body')
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.5, 0, LEG + 1.0))
        a.arms.append(nm)
        for j in range(6):
            p('thread', (0.1, 0.1, 0.22), mm('belly'), (sgn * (0.6 + 0.085 * j), -0.04 * j, LEG + 0.92 - j * 0.18), rot=(0, sgn * 20, 0))
        b('hand_flower', (0.26, 0.26, 0.26), mm('flower'), (sgn * 1.12, -0.26, LEG - 0.2 + 0.1), rot=(0, 45, 0), bev=0.04)
        for k_ in range(4):
            ang = math.radians(k_ * 90)
            p('petal', (0.12, 0.08, 0.12), mm('flower'), (sgn * 1.12 + math.cos(ang) * 0.2, -0.26, LEG - 0.1 + math.sin(ang) * 0.2))
    # rarity 4: glowing gill dots and spore puffs (glow segment)
    sg('glow', 'head', (0, 0.05, zc))
    a.glow.append('glow')
    for k_ in range(8):
        ang = math.radians(k_ * 45 + 22)
        p('gill_glow', (0.12, 0.12, 0.06), mm('glow' if k_ % 2 else 'glow2'), (math.cos(ang) * 0.9, 0.05 + math.sin(ang) * 0.85, zc - 0.33))
    for i in range(4):
        p('spore_puff', (0.12, 0.12, 0.12), mm('glow2'), (0.3 * math.sin(i * 2), 0.05 + 0.3 * math.cos(i * 2), zc + 1.0 + i * 0.2), rot=(45, 45, 0))
    use('body')
    tail_kit('stub', 'body', (0, 0.45, LEG + 0.4), 'root', 'main', size=0.2)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, 0, LEG + 1.1), Chest=(0, -0.5, LEG + 0.8), Hit=(0, 0, LEG + 1.4))
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=3.4)
    return finish(a)


def spore_marauder(row):
    """spore marauder: a big round toad standing upright like a warrior, wide grin, puffball spore sacs on its back,
    a toadstool shield on one arm and a fungus club in the other"""
    a = start(row, dict(main='#6a8a3a', belly='#e8e0a0', dark='#2e3a1a', accent='#c84a5a', sac='#c8a87a', sac2='#a8885a', wood='#7a5a3a',
                        blush='#ff9ab4', **{'*glow': '#c8ff6a', '*glow2': '#ffe68a'}), 3.82)
    B, Hd = biped(tw=1.6, td=1.2, th=1.3, legh=0.5, lw=0.5, hw=1.5, hd=1.1, hh=0.9, arm_l=0.9, arm_w=0.36, hand=0.42, ntoe=3, foot='main', toe='belly')
    use('head')
    # wide toad grin and bulging eyes on top
    p('grin', (1.1, 0.04, 0.06), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.2))
    for sgn in (-1, 1):
        p('grin_end', (0.06, 0.04, 0.12), mm('dark'), (sgn * 0.55, Hd.front - 0.012, Hd.c.z - 0.16))
        p('blush', (0.16, 0.03, 0.08), mm('blush'), (sgn * 0.5, Hd.front - 0.012, Hd.c.z))
        b('eye_bump', (0.5, 0.5, 0.36), mm('main'), (sgn * 0.42, Hd.c.y, Hd.top + 0.08), bev=0.1)
    eyes(Box((0, Hd.c.y, Hd.top + 0.1), (1.4, Hd.s.y, 0.4), 'head'), 0.7, 0.3, 0.0, iris='#e8c84a', brow='#2e3a1a', tilt=-8)
    grid(Hd, 't', 3, 2, mm('dark'), (0.1, 0.1), name='wart', span=(0.6, 0.4))
    grid(Hd, 'l', 2, 2, mm('dark'), (0.1, 0.1), name='wart', span=(0.6, 0.5))
    grid(Hd, 'r', 2, 2, mm('dark'), (0.1, 0.1), name='wart', span=(0.6, 0.5))
    p('tongue', (0.3, 0.04, 0.08), mm('accent'), (0.2, Hd.front - 0.02, Hd.c.z - 0.26))
    for sgn in (-1, 1):
        p('nostril', (0.06, 0.03, 0.04), mm('dark'), (sgn * 0.12, Hd.front - 0.012, Hd.c.z + 0.06))
        p('cheek_wart', (0.08, 0.04, 0.08), mm('dark'), (sgn * 0.62, Hd.front - 0.02, Hd.c.z + 0.1))
    for k_ in range(8):
        ang = math.radians(k_ * 45)
        p('neck_frill', (0.24, 0.24, 0.12), mm('belly' if k_ % 2 else 'accent'), (math.cos(ang) * 0.7, Hd.c.y + math.sin(ang) * 0.5, Hd.bot - 0.02), rot=(0, 0, k_ * 45))
    use('body')
    grid(B, 'f', 3, 3, mm('belly'), (0.14, 0.14), name='belly_spot', span=(0.6, 0.6))
    grid(B, 'l', 2, 3, mm('dark'), (0.12, 0.12), name='wart', span=(0.6, 0.6))
    grid(B, 'r', 2, 3, mm('dark'), (0.12, 0.12), name='wart', span=(0.6, 0.6))
    grid(B, 'k', 3, 4, mm('belly'), (0.12, 0.12), name='back_spot', span=(0.7, 0.7))
    p('belt', (B.s.x + 0.08, B.s.y + 0.08, 0.16), mm('wood'), (0, B.c.y, B.c.z - B.s.z * 0.3))
    for k_ in range(6):
        p('belt_stud', (0.1, 0.06, 0.1), mm('sac'), ((k_ - 2.5) * 0.24, B.front - 0.04, B.c.z - B.s.z * 0.3))
    for i, (x, z, s) in enumerate(((-0.2, 0.0, 0.3), (0.3, 0.1, 0.34), (-0.8, 0.7, 0.3), (0.8, 0.8, 0.3))):
        b('spore_sac_small', (s, s, s), mm('sac'), (x, B.back + 0.1, B.c.z + z), bev=0.06)
        p('small_pore', (s * 0.3, 0.06, s * 0.3), mm('dark'), (x, B.back + 0.1 + s * 0.5, B.c.z + z))
    # puffball sacs on the back (the silhouette)
    for i, (x, z, s) in enumerate(((-0.5, 0.4, 0.6), (0.5, 0.5, 0.66), (0.0, 0.9, 0.56), (-0.6, 1.1, 0.4), (0.6, 1.2, 0.44))):
        b('spore_sac', (s, s, s), mm('sac' if i % 2 else 'sac2'), (x, B.back + s * 0.3, B.c.z + z - 0.3), bev=0.14 * s)
        p('sac_pore', (s * 0.3, 0.06, s * 0.3), mm('dark'), (x, B.back + s * 0.8, B.c.z + z - 0.3))
    # toadstool shield (left arm) and fungus club (right arm)
    use('arm_L')
    ha = a.bx['hands'][0] if 'hands' in a.bx else None
    hx = ha.c.x if ha else -1.2
    hz = ha.c.z if ha else 1.0
    b('shield', (0.16, 1.2, 1.2), mm('accent'), (hx - 0.24, -0.1, hz + 0.2), bev=0.1)
    for k_ in range(10):
        ang = math.radians(k_ * 36)
        p('shield_dot', (0.06, 0.14, 0.14), mm('belly'), (hx - 0.33, -0.1 + math.cos(ang) * 0.34, hz + 0.2 + math.sin(ang) * 0.34))
    p('shield_boss', (0.08, 0.3, 0.3), mm('belly'), (hx - 0.34, -0.1, hz + 0.2))
    use('arm_R')
    ha = a.bx['hands'][1] if 'hands' in a.bx else None
    hx = ha.c.x if ha else 1.2
    hz = ha.c.z if ha else 1.0
    b('club', (0.24, 0.24, 1.2), mm('wood'), (hx, -0.2, hz + 0.5), bev=0.04)
    b('club_cap', (0.7, 0.7, 0.36), mm('sac'), (hx, -0.2, hz + 1.2), bev=0.1)
    for k_ in range(8):
        ang = math.radians(k_ * 45 + 22)
        p('club_spike', (0.12, 0.12, 0.12), mm('dark'), (hx + math.cos(ang) * 0.34, -0.2 + math.sin(ang) * 0.34, hz + 1.2))
    # rarity 5: glowing spore pores and floating spores (glow segment), orbit, yellow aura
    sg('glow', 'body', (0, B.back + 0.4, B.c.z + 0.4))
    a.glow.append('glow')
    for i, (x, z, s) in enumerate(((-0.5, 0.4, 0.6), (0.5, 0.5, 0.66), (0.0, 0.9, 0.56), (-0.6, 1.1, 0.4), (0.6, 1.2, 0.44))):
        p('pore_glow', (s * 0.2, 0.06, s * 0.2), mm('glow'), (x, B.back + s * 0.82, B.c.z + z - 0.3))
    for i in range(10):
        p('spore', (0.12, 0.12, 0.12), mm('glow' if i % 2 else 'glow2'), (0.7 * math.sin(i * 1.1), B.back + 0.8 + 0.2 * (i % 3), B.c.z + 1.3 + 0.16 * i), rot=(45, 45, 0))
    use('body')
    a.bx.update(body=B, head=Hd)
    orbit_kit((0, 0.2, B.c.z + 0.4), 2.2, 6, 'glow', 'glow2', size=0.16, dz=0.4, shape='leaf')
    aura_kit(1.9, 5, motes=10, mote_col='glow', height=2.6, style='petals')
    return finish(a)


def cap_mantis(row):
    """cap mantis: a LOW, wide flower-mantis crouched flat to the ground; every leg carries a round mushroom-cap lobe,
    a big hooded cap behind its head like a cobra hood, scythe arms held out flat in front"""
    a = start(row, dict(main='#e8d0e8', belly='#fff4f8', dark='#5a3a5a', accent='#c84a8a', cap='#b84a6a', cap2='#e87aa0', dot='#fff8e8',
                        blush='#ff8ab4', **{'*glow': '#ff8ae0', '*glow2': '#8affc8', '*glow3': '#ffe68a'}), 3.42)
    zb = 0.6
    sg('body', 'root', (0, 0.4, zb))
    B = b('abdomen', (1.8, 1.8, 0.5), mm('main'), (0, 0.7, zb), bev=0.16)
    b('abdomen_lobe', (1.4, 1.0, 0.3), mm('cap2'), (0, 1.0, zb + 0.36), bev=0.1)
    grid(B, 't', 3, 3, mm('accent'), (0.14, 0.14), name='back_spot', span=(0.6, 0.6), offset=0.15)
    b('thorax', (0.8, 0.8, 0.5), mm('main'), (0, -0.4, zb + 0.1), bev=0.12)
    grid(B, 'l', 3, 2, mm('cap2'), (0.12, 0.12), name='side_spot', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('cap2'), (0.12, 0.12), name='side_spot', span=(0.7, 0.5))
    grid(Box((0, -0.4, zb + 0.1), (0.8, 0.8, 0.5)), 't', 2, 2, mm('accent'), (0.1, 0.1), name='thorax_dot', span=(0.6, 0.6))
    for j in range(4):
        p('back_stripe', (1.5, 0.06, 0.04), mm('dark'), (0, 0.1 + j * 0.4, zb + 0.26))
    for j in range(4):
        p('lobe_dot', (0.14, 0.14, 0.04), mm('dot'), ((j - 1.5) * 0.3, 1.0, zb + 0.52))
    # head and the cobra-like cap hood (the silhouette)
    sg('head', 'body', (0, -0.6, zb + 0.4))
    Hd = b('head', (0.9, 0.6, 0.7), mm('main'), (0, -0.8, zb + 0.6), bev=0.12)
    eyes(Hd, 0.36, 0.26, 0.12, iris='#c84a8a', lash=True, brow=None)
    p('smile', (0.2, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, zb + 0.4))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.3, Hd.front - 0.012, zb + 0.46))
    b('hood', (2.0, 0.24, 1.3), mm('cap'), (0, -0.4, zb + 1.2), bev=0.12)
    b('hood_top', (1.4, 0.24, 0.4), mm('cap'), (0, -0.4, zb + 1.95), bev=0.1)
    p('hood_inner', (1.6, 0.06, 1.0), mm('cap2'), (0, -0.53, zb + 1.2))
    for k_ in range(13):
        ang = math.radians(k_ * 15)
        p('hood_dot', (0.12, 0.06, 0.12), mm('dot'), (math.cos(ang) * 0.7, -0.27, zb + 1.2 + math.sin(ang) * 0.6))
    for sgn, n in LR:
        nm = 'antenna_' + n
        sg(nm, 'head', (sgn * 0.2, -0.8, Hd.top))
        a.ears.append(nm)
        p('antenna', (0.05, 0.05, 0.5), mm('dark'), (sgn * 0.28, -0.9, Hd.top + 0.2), rot=(-35, sgn * 25, 0))
        p('antenna_tip', (0.1, 0.1, 0.1), mm('accent'), (sgn * 0.38, -1.06, Hd.top + 0.42))
    # scythe arms held out flat
    use('body')
    for sgn, n in LR:
        nm = 'claw_' + n
        sg(nm, 'body', (sgn * 0.4, -0.6, zb + 0.2))
        a.arms.append(nm)
        b('scythe_base', (0.24, 0.9, 0.2), mm('main'), (sgn * 0.5, -1.1, zb + 0.1), bev=0.04)
        b('scythe_blade', (0.18, 0.8, 0.14), mm('accent'), (sgn * 0.4, -1.7, zb + 0.2), rot=(0, 0, sgn * 15), bev=0.03)
        for t in range(5):
            p('scythe_tooth', (0.06, 0.08, 0.1), mm('belly'), (sgn * 0.32, -1.3 - t * 0.14, zb + 0.06))
        b('arm_lobe', (0.6, 0.6, 0.16), mm('cap2'), (sgn * 0.8, -1.0, zb + 0.24), bev=0.08)
    # four legs, each with a mushroom-cap lobe
    for i, y in enumerate((0.2, 1.2)):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.8, y, zb))
            a.legs.append(nm)
            b('leg', (0.8, 0.16, 0.16), mm('main'), (sgn * 1.2, y, zb - 0.1), rot=(0, sgn * 20, 0), bev=0.03)
            b('leg_low', (0.14, 0.14, 0.5), mm('dark'), (sgn * 1.55, y, 0.25), bev=0.03)
            b('leg_cap', (0.8, 0.8, 0.2), mm('cap' if i % 2 else 'cap2'), (sgn * 1.4, y, zb + 0.1), bev=0.1)
            for k_ in range(5):
                ang = math.radians(k_ * 72)
                p('leg_cap_dot', (0.12, 0.12, 0.05), mm('dot'), (sgn * 1.4 + math.cos(ang) * 0.22, y + math.sin(ang) * 0.22, zb + 0.22))
            p('foot', (0.2, 0.24, 0.06), mm('accent'), (sgn * 1.55, y - 0.04, 0.03))
    tail_kit('stub', 'body', (0, 1.6, zb), 'main', 'cap2', size=0.3)
    # rarity 6: glowing hood rim and cap lobes (own glow segment), crown, two orbits, red aura
    sg('glow', 'head', (0, -0.4, zb + 1.2))
    a.glow.append('glow')
    for k_ in range(13):
        ang = math.radians(k_ * 15)
        p('hood_glow', (0.14, 0.08, 0.14), mm('glow' if k_ % 2 else 'glow3'), (math.cos(ang) * 1.0, -0.5, zb + 1.2 + math.sin(ang) * 0.75), rot=(0, 45, 0))
    for i, y in enumerate((0.2, 1.2)):
        for sgn, n in LR:
            use('leg_%d%s' % (i + 1, n))
            p('lobe_glow', (0.16, 0.16, 0.06), mm('glow2'), (sgn * 1.4, y, zb + 0.24))
    halo_kit(Box((0, -0.4, zb + 1.95), (1.4, 0.24, 0.4), 'head'), 'glow3', r=0.5, n=6, dz=0.4, kind='leaves')
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -1.0, zb), Hit=(0, 0.6, zb + 0.4))
    orbit_kit((0, 0.3, zb + 1.0), 2.6, 6, 'glow', 'glow3', size=0.16, dz=0.5, shape='flame')
    orbit_kit((0, 0.3, zb + 0.3), 3.0, 8, 'glow2', 'glow', size=0.1, name='orbit2', dz=0.2, shape='bubble')
    aura_kit(2.6, 6, motes=12, mote_col='glow', height=3.0, style='petals')
    return finish(a)


ANIMALS = dict(shelf_millipede=shelf_millipede, peat_leech=peat_leech, lantern_slug=lantern_slug, mycelium_bloomstalker=mycelium_bloomstalker,
               spore_marauder=spore_marauder, cap_mantis=cap_mantis)
