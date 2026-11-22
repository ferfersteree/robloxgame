# Biome 24 - Storm Rift: torn sky, lightning, glass fulgurite spikes, floating rocks
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 24
GROUND = '#4a4a6a'
SKY = '#8a8ab8'
THEME = dict(bits=['#8ae8ff', '#ffe84a'], dust='#6a6a8a', glow='#8ae8ff', splash='#d8e8ff', bit_name='искры и стеклянная крошка')
FOOT = dict(rift_serpent=1.25, storm_harrier=1.2, thunder_centaur=1.1)
BUSH_NAME = 'грозовой куст: расколотый камень, из трещины растут стеклянные молнии-фульгуриты и колючий синий кустарник'


def bush():
    B = begin_bush(NN)
    rock = mat('rock', '#4a4a5e')
    rock2 = mat('rock2', '#6a6a82')
    shrub = mat('shrub', '#3a5a9a')
    shrub2 = mat('shrub2', '#5a7ac8')
    glass = mat('glass', '#c8f0ff')
    bolt = mat('bolt', '#ffe84a', 'neon', 2.6)
    spark = mat('spark', '#8ae8ff', 'neon', 2.4)
    part('big', (0, 0.3, 0.4), 'rock')
    for sgn in (-1, 1):
        b('split_rock', (2.8, 2.2, 0.9), rock if sgn < 0 else rock2, (sgn * 1.7, 0.3, 0.45), rot=(0, sgn * -8, 0), bev=0.15)
    p('crack_glow', (0.3, 1.8, 0.1), spark, (0, 0.3, 0.3))
    for i, (x, h, tilt) in enumerate(((-0.3, 4.2, -10), (0.4, 3.6, 18), (-1.2, 2.8, -30), (1.3, 3.0, 32))):
        part('big' if h > 3.5 else 'small', (x, 0.3, h * 0.6), 'fulgurite_%d' % i)
        segs = 4
        for j in range(segs):
            z = 0.6 + j * (h - 0.6) / segs
            p('fulgurite', (0.24, 0.24, (h - 0.6) / segs + 0.05), glass, (x + math.sin(math.radians(tilt)) * (z - 0.6) * 0.6 + 0.12 * ((j % 2) * 2 - 1), 0.3, z + 0.3),
              rot=(0, tilt + (20 if j % 2 else -20), 0))
        p('bolt_tip', (0.2, 0.2, 0.3), bolt, (x + math.sin(math.radians(tilt)) * (h - 0.6) * 0.6, 0.3, h + 0.2), rot=(45, 0, 45))
    for i, (x, y, s) in enumerate(((-2.4, -0.2, 1.1), (2.4, -0.1, 1.2), (-1.4, 0.8, 1.3), (1.6, 0.9, 1.2))):
        part('small', (x, y, 1.4), 'shrub_%d' % i)
        b('shrub', (s, s, s * 0.9), shrub if i % 2 else shrub2, (x, y, 1.3), bev=0.15)
        for j in range(3):
            p('thorn', (0.08, 0.08, 0.3), glass, (x + (j - 1) * 0.3, y - s * 0.4, 1.4 + s * 0.3), rot=(-30, (j - 1) * 25, 0))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def fulgurite_cricket(row):
    """storm cricket: small body, HUGE folded jumping legs rising high above its back in a Z shape, very long whip antennae,
    glassy fulgurite crystal sprigs on its back"""
    a = start(row, dict(main='#3a6ab8', belly='#c8e0ff', dark='#1a2a4a', accent='#ffe84a', glass='#d8f4ff', leg='#2a4a8a', blush='#ff9ab4'), 2.22)
    sg('body', 'root', (0, 0.3, 0.45))
    B = b('body', (0.7, 1.4, 0.6), mm('main'), (0, 0.4, 0.45), bev=0.14)
    b('wing_case', (0.74, 1.1, 0.16), mm('leg'), (0, 0.55, 0.8), bev=0.05)
    for j in range(4):
        p('wing_vein', (0.76, 0.05, 0.17), mm('accent'), (0, 0.15 + j * 0.25, 0.8))
    grid(B, 'l', 3, 2, mm('belly'), (0.08, 0.08), name='side_dot', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('belly'), (0.08, 0.08), name='side_dot', span=(0.7, 0.5))
    # fulgurite sprigs on the back
    for i, (x, y, h) in enumerate(((0.0, 0.3, 0.4), (-0.12, 0.6, 0.3), (0.12, 0.8, 0.34))):
        for j in range(2):
            p('fulgurite', (0.08, 0.08, h / 2 + 0.04), mm('glass'), (x + (0.04 if j else -0.04), y, 0.9 + h / 4 + j * h / 2), rot=(0, 20 if j else -20, 0))
    sg('head', 'body', (0, -0.3, 0.5))
    Hd = b('head', (0.66, 0.5, 0.6), mm('main'), (0, -0.5, 0.56), bev=0.14)
    eyes(Hd, 0.34, 0.26, 0.12, iris='#ffe84a', brow=None)
    p('smile', (0.14, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 0.4))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('blush'), (sgn * 0.22, Hd.front - 0.012, 0.44))
        nm = 'antenna_' + n
        sg(nm, 'head', (sgn * 0.15, -0.6, Hd.top))
        a.ears.append(nm)
        for j in range(4):
            p('antenna', (0.04, 0.04, 0.36), mm('dark'), (sgn * (0.18 + 0.12 * j), -0.65 + 0.2 * j, Hd.top + 0.18 + 0.3 * j), rot=(-30, sgn * 25, 0))
        p('antenna_tip', (0.08, 0.08, 0.08), mm('accent'), (sgn * 0.66, 0.15, Hd.top + 1.32))
    use('body')
    # small front/middle legs
    for i, y in enumerate((-0.1, 0.25)):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.3, y, 0.3))
            a.legs.append(nm)
            b('leg', (0.1, 0.1, 0.36), mm('leg'), (sgn * 0.42, y, 0.18), rot=(0, sgn * 15, 0), bev=0.02)
            p('foot', (0.12, 0.16, 0.04), mm('dark'), (sgn * 0.46, y - 0.03, 0.02))
    # huge jumping hind legs (the silhouette): thigh up and back, shin back down
    for sgn, n in LR:
        nm = 'leg_3' + n
        sg(nm, 'body', (sgn * 0.36, 0.7, 0.5))
        a.legs.append(nm)
        b('thigh', (0.22, 0.24, 1.0), mm('main'), (sgn * 0.44, 0.9, 0.95), rot=(-35, 0, 0), bev=0.04)
        for j in range(3):
            p('thigh_stripe', (0.24, 0.06, 0.2), mm('accent'), (sgn * 0.44, 0.78 + j * 0.14, 0.75 + j * 0.2), rot=(-35, 0, 0))
        b('shin', (0.1, 0.1, 1.1), mm('leg'), (sgn * 0.48, 1.35, 0.7), rot=(25, 0, 0), bev=0.02)
        for j in range(4):
            p('shin_spike', (0.05, 0.08, 0.05), mm('glass'), (sgn * 0.48, 1.25 + j * 0.06, 0.4 + j * 0.2))
        p('hind_foot', (0.14, 0.26, 0.05), mm('dark'), (sgn * 0.48, 1.55, 0.03))
    sg('tail', 'body', (0, 1.1, 0.45))
    a.tail = ['tail']
    for sgn in (-1, 1):
        p('cercus', (0.04, 0.4, 0.04), mm('dark'), (sgn * 0.12, 1.3, 0.5), rot=(10, 0, sgn * 12))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.7, 0.45), Hit=(0, 0.4, 0.8))
    return finish(a)


def rift_kangaroo(row):
    """rift kangaroo standing tall on huge feet and a thick tail (a tripod), short arms held up, long ears,
    and a little joey peeking out of the pouch holding a glowing rift shard"""
    a = start(row, dict(main='#b87a5a', belly='#f0d8b8', dark='#4a2a1e', accent='#8ae8ff', ear='#ff9ab4', joey='#d89a7a', blush='#ff8ab4',
                        **{'*shard': '#8ae8ff'}), 3.54)
    sg('body', 'root', (0, 0.2, 1.4))
    B = b('body', (1.1, 1.0, 1.5), mm('main'), (0, 0.25, 1.5), rot=(-8, 0, 0), bev=0.2)
    b('belly', (0.8, 0.1, 1.1), mm('belly'), (0, -0.28, 1.4), rot=(-8, 0, 0), bev=0.05)
    b('pouch', (0.7, 0.3, 0.5), mm('belly'), (0, -0.4, 1.05), bev=0.08)
    p('pouch_rim', (0.74, 0.32, 0.06), mm('main'), (0, -0.4, 1.31))
    grid(B, 'k', 2, 3, mm('dark'), (0.12, 0.12), name='back_spot', span=(0.5, 0.6))
    # joey in the pouch with the shard
    sg('joey', 'body', (0, -0.42, 1.3))
    a.ears.append('joey')
    b('joey_head', (0.36, 0.3, 0.32), mm('joey'), (0, -0.46, 1.46), bev=0.08)
    for sgn in (-1, 1):
        p('joey_ear', (0.08, 0.06, 0.2), mm('joey'), (sgn * 0.12, -0.46, 1.68))
        p('joey_eye', (0.06, 0.03, 0.08), mm('dark'), (sgn * 0.08, -0.62, 1.5))
        p('joey_paw', (0.08, 0.08, 0.08), mm('joey'), (sgn * 0.16, -0.6, 1.34))
    b('shard', (0.14, 0.14, 0.3), mm('shard'), (0.16, -0.66, 1.46), rot=(0, 20, 45), bev=0.02)
    # big feet and legs
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.45, 0.4, 0.9))
        a.legs.append(nm)
        b('thigh', (0.46, 0.8, 0.8), mm('main'), (sgn * 0.5, 0.4, 0.7), bev=0.14)
        b('foot', (0.32, 1.2, 0.2), mm('main'), (sgn * 0.45, -0.1, 0.1), bev=0.06)
        for t in range(3):
            p('toe', (0.08, 0.08, 0.08), mm('dark'), (sgn * 0.45 + (t - 1) * 0.1, -0.72, 0.06))
    # short arms held up
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.5, -0.1, 1.9))
        a.arms.append(nm)
        b('arm', (0.18, 0.18, 0.5), mm('main'), (sgn * 0.48, -0.3, 1.75), rot=(40, 0, 0), bev=0.04)
        p('paw', (0.2, 0.16, 0.16), mm('belly'), (sgn * 0.46, -0.5, 1.6))
    # head with long ears
    sg('head', 'body', (0, 0.1, 2.2))
    Hd = b('head', (0.8, 0.8, 0.7), mm('main'), (0, -0.05, 2.6), bev=0.14)
    mz = muzzle(Hd, (0.4, 0.3, 0.3), -0.2, 'belly', nose=(0.14, 0.08, 0.1), nose_mat='dark')
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.28, Hd.front - 0.012, 2.5))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.25, 0.0, Hd.top))
        a.ears.append(nm)
        b('ear', (0.22, 0.12, 0.6), mm('main'), (sgn * 0.3, 0.05, Hd.top + 0.28), rot=(0, sgn * 15, 0), bev=0.04)
        p('ear_in', (0.12, 0.04, 0.44), mm('ear'), (sgn * 0.3, -0.02, Hd.top + 0.28), rot=(0, sgn * 15, 0))
    eyes(Hd, 0.3, 0.24, 0.14, iris='#4a2a1e', brow='#4a2a1e', lash=True)
    grid(Hd, 't', 2, 2, mm('dark'), (0.08, 0.08), name='head_spot', span=(0.5, 0.5))
    use('body')
    grid(B, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.5, 0.5))
    grid(B, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.5, 0.5))
    # thick tail (third leg of the tripod)
    use('body')
    sg('tail', 'body', (0, 0.7, 0.9))
    a.tail = ['tail']
    for j in range(4):
        s = 0.5 - 0.08 * j
        b('tail', (s, 0.5, s), mm('main'), (0, 0.9 + j * 0.4, 0.7 - j * 0.16), bev=0.08)
    p('tail_tip', (0.2, 0.3, 0.2), mm('dark'), (0, 2.35, 0.14))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, 1.6), Hit=(0, 0.25, 2.0))
    return finish(a)


def thunder_centaur(row):
    """a little thunder centaur: a chunky pony body with a kid-like upper body on top, storm-cloud hair,
    a lightning javelin in one hand, cloud tail"""
    a = start(row, dict(main='#6a7ab8', belly='#c8d0f0', dark='#2a2e4a', accent='#ffe84a', skin='#ffd8b8', cloud='#e8ecff', cloud2='#a8b0d8',
                        hoof='#3a3a5a', blush='#ff9ab4', shirt='#3a5ab8'), 4.0)
    LEG = 0.9
    zb = LEG + 0.45
    by = 0.3
    sg('body', 'root', (0, by, zb))
    B = b('body', (1.1, 1.7, 0.9), mm('main'), (0, by, zb), bev=0.16)
    for fy in (by - 0.6, by + 0.6):
        for sgn, n in LR:
            nm = 'leg_%s%s' % ('f' if fy < by else 'b', n)
            sg(nm, 'body', (sgn * 0.35, fy, zb - 0.4))
            a.legs.append(nm)
            b('leg', (0.3, 0.3, LEG), mm('main'), (sgn * 0.35, fy, LEG / 2), bev=0.05)
            p('sock', (0.32, 0.32, 0.12), mm('belly'), (sgn * 0.35, fy, 0.24))
            p('hoof', (0.34, 0.38, 0.16), mm('hoof'), (sgn * 0.35, fy - 0.02, 0.08))
            p('knee_band', (0.34, 0.34, 0.08), mm('accent'), (sgn * 0.35, fy, LEG * 0.6))
            for t in (-1, 1):
                p('fetlock', (0.1, 0.1, 0.14), mm('cloud'), (sgn * 0.35 + t * 0.1, fy - 0.16, 0.3))
    a.tail_j = (0, by + 0.85, zb + 0.2)
    use('body')
    grid(B, 'l', 3, 2, mm('belly'), (0.12, 0.12), name='dapple', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('belly'), (0.12, 0.12), name='dapple', span=(0.7, 0.5))
    grid(B, 't', 2, 3, mm('belly'), (0.12, 0.12), name='dapple', span=(0.6, 0.6), offset=0.2)
    grid(B, 'k', 2, 2, mm('belly'), (0.12, 0.12), name='dapple', span=(0.6, 0.5))
    grid(B, 'u', 2, 3, mm('dark'), (0.12, 0.12), name='under_spot', span=(0.6, 0.6))
    p('saddle_cloth', (1.14, 0.6, 0.06), mm('accent'), (0, B.c.y + 0.3, B.top + 0.01))
    sg('torso', 'body', (0, B.front + 0.3, B.top))
    TB = b('torso', (0.8, 0.6, 0.9), mm('shirt'), (0, B.front + 0.3, B.top + 0.45), bev=0.12)
    p('belt', (0.84, 0.64, 0.1), mm('accent'), (0, B.front + 0.3, B.top + 0.1))
    p('bolt_emblem', (0.2, 0.05, 0.3), mm('accent'), (0, TB.front - 0.01, B.top + 0.5), rot=(0, 20, 0))
    grid(TB, 'k', 2, 2, mm('belly'), (0.1, 0.1), name='shirt_dot', span=(0.5, 0.5))
    grid(TB, 'l', 2, 2, mm('belly'), (0.08, 0.08), name='shirt_dot', span=(0.5, 0.5))
    grid(TB, 'r', 2, 2, mm('belly'), (0.08, 0.08), name='shirt_dot', span=(0.5, 0.5))
    p('scarf', (0.7, 0.5, 0.12), mm('accent'), (0, B.front + 0.3, B.top + 0.92))
    for t in range(2):
        p('scarf_tail', (0.12, 0.08, 0.3), mm('accent'), (0.2 + t * 0.12, TB.front - 0.02, B.top + 0.72 - t * 0.06))
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'torso', (sgn * 0.45, B.front + 0.3, B.top + 0.8))
        a.arms.append(nm)
        b('arm', (0.22, 0.22, 0.6), mm('skin'), (sgn * 0.52, B.front + 0.25, B.top + 0.5), rot=(20, 0, 0), bev=0.04)
        p('sleeve', (0.26, 0.26, 0.2), mm('shirt'), (sgn * 0.52, B.front + 0.3, B.top + 0.75))
        p('bracelet', (0.26, 0.26, 0.06), mm('accent'), (sgn * 0.52, B.front + 0.18, B.top + 0.3))
    use('arm_R')
    b('javelin', (0.08, 0.08, 1.8), mm('dark'), (0.56, B.front, B.top + 0.6), bev=0.02)
    b('javelin_tip', (0.2, 0.1, 0.4), mm('accent'), (0.56, B.front, B.top + 1.6), rot=(0, 20, 0), bev=0.02)
    p('javelin_tip2', (0.16, 0.1, 0.3), mm('accent'), (0.6, B.front, B.top + 1.86), rot=(0, -20, 0))
    for t in range(3):
        p('javelin_wrap', (0.12, 0.12, 0.06), mm('cloud'), (0.56, B.front, B.top + 0.3 + t * 0.12))
    sg('head', 'torso', (0, B.front + 0.3, B.top + 0.9))
    Hd = b('head', (0.84, 0.74, 0.74), mm('skin'), (0, B.front + 0.28, B.top + 1.3), bev=0.14)
    eyes(Hd, 0.3, 0.24, 0.0, iris='#3a5ab8', brow='#2a2e4a', lash=True)
    p('smile', (0.16, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.2))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.26, Hd.front - 0.012, Hd.c.z - 0.12))
        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.2, Hd.front - 0.013, Hd.c.z - 0.06))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.4, Hd.c.y, Hd.top - 0.1))
        a.ears.append(nm)
        b('pony_ear', (0.14, 0.1, 0.26), mm('main'), (sgn * 0.36, Hd.c.y, Hd.top + 0.24), rot=(0, sgn * 15, 0), bev=0.03)
    # storm-cloud hair (the silhouette)
    use('head')
    for i, (x, y, z, s) in enumerate(((0, 0.05, 0.42, 0.6), (-0.32, 0.1, 0.3, 0.44), (0.32, 0.1, 0.32, 0.46), (0, 0.32, 0.2, 0.5),
                                     (-0.18, -0.2, 0.44, 0.36), (0.2, -0.2, 0.46, 0.34))):
        b('cloud_hair', (s, s, s * 0.8), mm('cloud' if i % 2 == 0 else 'cloud2'), (x, Hd.c.y + y, Hd.top + z - 0.1), bev=0.1)
    p('hair_bolt', (0.08, 0.05, 0.3), mm('accent'), (0.3, Hd.front - 0.05, Hd.top + 0.05), rot=(0, 25, 0))
    # cloud tail
    use('body')
    sg('tail', 'body', a.tail_j)
    a.tail = ['tail']
    for j in range(4):
        b('cloud_tail', (0.4 - 0.05 * j, 0.36, 0.36 - 0.04 * j), mm('cloud' if j % 2 else 'cloud2'), (0, a.tail_j[1] + 0.2 + j * 0.24, a.tail_j[2] - 0.1 - j * 0.12), bev=0.08)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, TB.front, TB.c.z), Hit=(0, B.c.y, B.top + 0.4))
    return finish(a)


def prism_revenant(row):
    """prism revenant: a floating ghost in a hooded cloak made of triangular crystal prisms, a dark hood with two glowing
    eyes, two floating crystal hands, the cloak hem breaks into falling shards, a rainbow beam through its chest"""
    zc = 1.0
    a = start(row, dict(main='#c8d8ff', belly='#f0f4ff', dark='#1e1a3a', accent='#ffe84a', prism1='#ff9ad0', prism2='#9ad8ff', prism3='#c8ff9a',
                        **{'*glow': '#ffffff', '*glow2': '#ff8ae0', '*glow3': '#8ae8ff'}), 3.71, hover=2.4, z0=zc)
    sg('body', 'root', (0, 0, zc))
    B = b('cloak', (1.2, 1.0, 1.4), mm('main'), (0, 0.05, zc), bev=0.14)
    grid(B, 'f', 2, 3, mm('belly'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))
    grid(B, 'k', 2, 3, mm('belly'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))
    grid(B, 'l', 2, 3, mm('prism2'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))
    grid(B, 'r', 2, 3, mm('prism1'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))
    for i in range(16):
        ang = math.radians(i * 22.5 + 11)
        p('cloak_prism', (0.22, 0.22, 0.6), mm(('prism1', 'prism2', 'prism3', 'belly')[i % 4]), (math.cos(ang) * 0.62, 0.05 + math.sin(ang) * 0.52, zc - 0.2),
          rot=(0, 0, i * 22.5 + 45))
    # hem breaking into shards (tail)
    sg('tail', 'body', (0, 0.05, zc - 0.7))
    a.tail = ['tail']
    for i in range(12):
        ang = math.radians(i * 30)
        p('hem_shard', (0.18, 0.18, 0.4 - 0.03 * i), mm(('prism1', 'prism2', 'prism3')[i % 3]), (math.cos(ang) * 0.4, 0.05 + math.sin(ang) * 0.35, zc - 0.9 - 0.12 * (i % 3)),
          rot=(0, 0, 45 + i * 20))
    p('hem_tip', (0.2, 0.2, 0.36), mm('main'), (0, 0.05, zc - 1.3), rot=(0, 0, 45))
    # hood (the silhouette): a tall pointed prism hood with a dark face
    sg('head', 'body', (0, 0, zc + 0.7))
    Hd = b('hood', (1.0, 0.9, 0.9), mm('main'), (0, 0.0, zc + 1.1), bev=0.14)
    b('hood_peak', (0.5, 0.5, 0.5), mm('main'), (0, 0.15, zc + 1.7), rot=(0, 45, 0), bev=0.06)
    p('hood_tip', (0.2, 0.2, 0.3), mm('prism2'), (0, 0.2, zc + 2.05), rot=(0, 45, 0))
    p('face_dark', (0.7, 0.06, 0.56), mm('dark'), (0, Hd.front - 0.01, zc + 1.06))
    eyes(Box((0, -0.07, zc + 1.08), (0.7, 0.9, 0.56), 'head'), 0.4, 0.26, 0.06, iris='#8ae8ff', glow='#8ae8ff', brow=None)
    p('smile', (0.14, 0.03, 0.04), mm('glow'), (0, Hd.front - 0.06, zc + 0.86))
    for sgn in (-1, 1):
        p('hood_rim', (0.1, 0.1, 0.8), mm('accent'), (sgn * 0.42, Hd.front - 0.02, zc + 1.06))
    p('hood_rim_top', (0.84, 0.1, 0.1), mm('accent'), (0, Hd.front - 0.02, zc + 1.4))
    grid(Hd, 't', 2, 2, mm('prism1'), (0.1, 0.1), name='hood_gem', span=(0.5, 0.5))
    grid(Hd, 'l', 2, 2, mm('prism3'), (0.1, 0.1), name='hood_gem', span=(0.5, 0.5))
    grid(Hd, 'r', 2, 2, mm('prism2'), (0.1, 0.1), name='hood_gem', span=(0.5, 0.5))
    # floating crystal hands
    use('body')
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.6, -0.1, zc + 0.3))
        a.arms.append(nm)
        b('sleeve', (0.36, 0.4, 0.36), mm('main'), (sgn * 0.7, -0.1, zc + 0.2), bev=0.06)
        b('hand', (0.3, 0.3, 0.3), mm('prism2' if sgn < 0 else 'prism1'), (sgn * 1.0, -0.3, zc + 0.1), rot=(45, 45, 0), bev=0.04)
        for t in range(5):
            p('finger_shard', (0.05, 0.05, 0.2), mm('belly'), (sgn * 1.0 + (t - 2) * 0.06, -0.42, zc + 0.3))
        for t in range(2):
            p('cuff', (0.4, 0.44, 0.06), mm('accent'), (sgn * 0.7, -0.1, zc + 0.05 + t * 0.3))
    # rarity 4: rainbow beam through the chest + glowing prism edges (glow segment)
    sg('glow', 'body', (0, -0.5, zc + 0.1))
    a.glow.append('glow')
    for j, m_ in enumerate(('glow2', 'glow', 'glow3')):
        p('rainbow', (0.1, 0.5, 0.1), mm(m_), (-0.1 + j * 0.1, -0.7, zc + 0.1))
    b('chest_gem', (0.3, 0.1, 0.3), mm('glow'), (0, B.front - 0.02, zc + 0.1), rot=(0, 45, 0), bev=0.02)
    for i in range(4):
        ang = math.radians(i * 90)
        p('gem_frame', (0.08, 0.08, 0.08), mm('glow2'), (math.cos(ang) * 0.24, B.front - 0.03, zc + 0.1 + math.sin(ang) * 0.24))
    for i in range(6):
        ang = math.radians(i * 60)
        p('float_shard', (0.1, 0.1, 0.18), mm('glow3' if i % 2 else 'glow2'), (math.cos(ang) * 1.0, 0.05 + math.sin(ang) * 0.8, zc + 1.3 + 0.1 * (i % 2)), rot=(0, 0, 45))
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        p('prism_glow', (0.08, 0.08, 0.4), mm('glow3' if i % 2 else 'glow2'), (math.cos(ang) * 0.78, 0.05 + math.sin(ang) * 0.66, zc - 0.2))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.6, zc + 0.1), Hit=(0, 0.0, zc + 0.6))
    aura_kit(1.6, 4, motes=8, mote_col='glow3', height=3.0)
    return finish(a)


def storm_harrier(row):
    """storm harrier in a dive: the whole bird is a dart pointing forward and down, wings swept straight back tight
    against the body, a long forked tail like twin lightning tips, a crest of spikes, sharp hooked beak"""
    zc = 1.2
    a = start(row, dict(main='#3a4a8a', belly='#e8ecff', dark='#1a1e3a', accent='#ffe84a', wing='#2a3a6a', wing2='#5a7ac8', beak='#ffb84a',
                        blush='#ff9ab4', **{'*glow': '#ffe84a', '*glow2': '#8ae8ff'}), 1.79, hover=3.4, z0=zc)
    sg('body', 'root', (0, 0.3, zc))
    B = b('body', (0.8, 1.6, 0.8), mm('main'), (0, 0.4, zc), rot=(-20, 0, 0), bev=0.18)
    b('belly', (0.6, 1.3, 0.1), mm('belly'), (0, 0.35, zc - 0.36), rot=(-20, 0, 0), bev=0.04)
    for j in range(4):
        p('belly_bar', (0.62, 0.08, 0.11), mm('dark'), (0, -0.05 + j * 0.3, zc - 0.4 + j * 0.1), rot=(-20, 0, 0))
    grid(B, 't', 3, 6, mm('wing2'), (0.08, 0.08), name='back_feather', span=(0.6, 0.8))
    grid(B, 'u', 2, 4, mm('belly'), (0.1, 0.1), name='belly_feather', span=(0.6, 0.8))
    grid(B, 'l', 3, 2, mm('wing2'), (0.1, 0.1), name='side_feather', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('wing2'), (0.1, 0.1), name='side_feather', span=(0.7, 0.5))
    sg('head', 'body', (0, -0.4, zc - 0.2))
    Hd = b('head', (0.7, 0.66, 0.6), mm('main'), (0, -0.7, zc - 0.36), bev=0.14)
    p('face_mask', (0.72, 0.06, 0.24), mm('belly'), (0, Hd.front - 0.01, zc - 0.5))
    b('beak', (0.24, 0.36, 0.22), mm('beak'), (0, Hd.front - 0.16, zc - 0.48), rot=(25, 0, 0), bev=0.04)
    p('beak_hook', (0.14, 0.1, 0.14), mm('dark'), (0, Hd.front - 0.32, zc - 0.62))
    eyes(Hd, 0.32, 0.25, 0.16, iris='#ffe84a', brow='#1a1e3a', tilt=-12)
    grid(Hd, 'l', 2, 2, mm('wing2'), (0.08, 0.08), name='cheek_feather', span=(0.5, 0.5))
    grid(Hd, 'r', 2, 2, mm('wing2'), (0.08, 0.08), name='cheek_feather', span=(0.5, 0.5))
    grid(Hd, 't', 2, 2, mm('wing2'), (0.08, 0.08), name='head_feather', span=(0.5, 0.5))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('blush'), (sgn * 0.26, Hd.front - 0.012, zc - 0.44))
    # crest of spikes
    for j in range(6):
        p('crest', (0.08, 0.16, 0.3 - 0.03 * j), mm('accent'), (0, -0.66 + j * 0.11, Hd.top + 0.08 + 0.02 * j), rot=(40, 0, 0))
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.25, -0.7, Hd.top))
        a.ears.append(nm)
        p('ear_tuft', (0.1, 0.16, 0.2), mm('wing2'), (sgn * 0.3, -0.6, Hd.top + 0.04), rot=(40, sgn * 20, 0))
    # wings swept straight back (the silhouette)
    use('body')
    for sgn, n in LR:
        nm = 'wing_' + n
        sg(nm, 'body', (sgn * 0.4, 0.0, zc + 0.1))
        a.wings.append(nm)
        b('wing_root', (0.5, 1.0, 0.16), mm('wing'), (sgn * 0.6, 0.4, zc + 0.15), rot=(-15, 0, sgn * 12), bev=0.04)
        for j in range(8):
            b('primary', (0.16, 1.4 - 0.08 * j, 0.08), mm('wing2' if j % 2 else 'wing'), (sgn * (0.72 + 0.08 * j), 1.1 + 0.07 * j, zc + 0.35 + 0.015 * j),
              rot=(-15, 0, sgn * (8 + 3 * j)), bev=0.02)
        for j in range(6):
            p('covert', (0.2, 0.2, 0.1), mm('main' if j % 2 else 'wing2'), (sgn * (0.5 + 0.08 * j), 0.1 + 0.15 * j, zc + 0.26))
        for j in range(3):
            p('wing_bolt', (0.08, 0.4, 0.09), mm('accent'), (sgn * (0.7 + 0.1 * j), 0.8 + 0.3 * j, zc + 0.42), rot=(-15, 0, sgn * (10 + 20 * (j % 2))))
    # forked tail
    sg('tail', 'body', (0, 1.1, zc + 0.2))
    a.tail = ['tail']
    for sgn in (-1, 1):
        b('tail_fork', (0.18, 1.2, 0.08), mm('wing'), (sgn * 0.16, 1.7, zc + 0.36), rot=(-12, 0, sgn * 12), bev=0.02)
        p('fork_tip', (0.2, 0.24, 0.09), mm('accent'), (sgn * 0.3, 2.3, zc + 0.48), rot=(-12, 0, sgn * 40))
        for t in range(3):
            p('tail_bar', (0.2, 0.06, 0.09), mm('dark'), (sgn * (0.16 + 0.04 * t), 1.35 + 0.25 * t, zc + 0.3 + 0.05 * t))
    # talons tucked
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.2, 0.6, zc - 0.3))
        a.legs.append(nm)
        b('leg', (0.12, 0.3, 0.12), mm('beak'), (sgn * 0.2, 0.75, zc - 0.36), bev=0.02)
        for t in range(2):
            p('leg_feather', (0.16, 0.12, 0.12), mm('belly'), (sgn * 0.2, 0.62 + t * 0.1, zc - 0.28))
        for t in range(3):
            p('talon', (0.05, 0.12, 0.05), mm('dark'), (sgn * 0.2 + (t - 1) * 0.06, 0.94, zc - 0.4))
    # rarity 5: glowing bolt edges on the wings + spark trail (glow seg), orbit, yellow aura
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(8):
            p('wing_tip_glow', (0.08, 0.14, 0.08), mm('glow' if j % 2 else 'glow2'), (sgn * (0.72 + 0.08 * j + 0.05 * j), 1.1 + 0.07 * j + (1.4 - 0.08 * j) / 2, zc + 0.4))
    sg('glow', 'body', (0, 2.0, zc + 0.4))
    a.glow.append('glow')
    for i in range(10):
        p('spark_trail', (0.12, 0.12, 0.12), mm('glow' if i % 2 else 'glow2'), (0.2 * math.sin(i * 1.7), 2.4 + i * 0.16, zc + 0.5 + 0.06 * i), rot=(45, 45, 0))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, zc - 0.3), Hit=(0, 0.4, zc + 0.3))
    orbit_kit((0, 0.4, zc + 0.3), 2.2, 6, 'glow', 'glow2', size=0.14, dz=0.4, shape='flame')
    aura_kit(2.0, 5, motes=10, mote_col='glow', height=2.2, style='rays')
    return finish(a)


def rift_serpent(row):
    """rift serpent: a serpent curled into a perfect upright RING, biting its own tail (ouroboros) like a big wheel standing
    on the ground; inside the ring a torn rift of lightning crackles; a horned head with a mane of sparks"""
    a = start(row, dict(main='#4a3ab8', belly='#c8c0ff', dark='#1a1440', accent='#ffe84a', scale2='#7a5ae0', horn='#f0e8ff', blush='#ff9ab4',
                        **{'*glow': '#8ae8ff', '*glow2': '#ffe84a', '*glow3': '#ff6ad0'}), 3.4)
    R = 1.3
    zc = R + 0.35
    sg('body', 'root', (0, 0.0, 0.4))
    # bottom of the ring is the body; the ring is split into 4 chained segments that the tail anim can sway
    B = None
    a.tail = []
    a.neck = []
    segs = (('body', range(9, 15)), ('tail', range(15, 20)), ('tail2', range(20, 24)), ('neck1', range(3, 9)))
    for sname, rng in segs:
        if sname != 'body':
            th0 = math.radians(min(rng) * 15 - 90)
            sg(sname, 'body' if sname in ('tail', 'neck1') else 'tail', (math.cos(th0) * R, 0, zc + math.sin(th0) * R))
            (a.tail if sname.startswith('tail') else a.neck).append(sname)
        else:
            use('body')
        for i in rng:
            th = math.radians(i * 15 - 90)
            x, z = math.cos(th) * R, zc + math.sin(th) * R
            s = 0.62 - 0.012 * abs(i - 12)
            bx = b('coil', (s, 0.6, s), mm('main' if i % 2 else 'scale2'), (x, 0.0, z), rot=(0, -math.degrees(th), 0), bev=0.1)
            if i == 12:
                B = bx
            p('belly_scale', (s * 0.6, 0.62, 0.06), mm('belly'), (x - math.cos(th) * s * 0.5, 0.0, z - math.sin(th) * s * 0.5), rot=(0, -math.degrees(th), 0))
            p('ridge', (0.14, 0.2, 0.14), mm('accent'), (x + math.cos(th) * (s / 2 + 0.05), 0.0, z + math.sin(th) * (s / 2 + 0.05)), rot=(0, 45 - math.degrees(th), 0))
            for sgn in (-1, 1):
                p('side_scale', (0.16, 0.04, 0.16), mm('dark'), (x, sgn * 0.31, z), rot=(0, 45, 0))
    # head at the top-left biting the tail tip
    th = math.radians(2 * 15 - 90)
    hx, hz = math.cos(th) * R, zc + math.sin(th) * R
    sg('head', 'neck1', (hx, 0, hz))
    Hd = b('head', (0.9, 0.8, 0.8), mm('main'), (hx + 0.1, -0.05, hz + 0.1), bev=0.14)
    b('snout', (0.5, 0.4, 0.36), mm('belly'), (hx + 0.1, Hd.front - 0.14, hz - 0.06), bev=0.06)
    eyes(Hd, 0.3, 0.24, 0.18, iris='#ffe84a', glow='#ffe84a', brow='#1a1440', tilt=6)
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (hx + 0.1 + sgn * 0.3, Hd.front - 0.012, hz - 0.02))
        nm = 'horn_' + n
        sg(nm, 'head', (hx + 0.1 + sgn * 0.3, -0.05, Hd.top))
        a.ears.append(nm)
        b('horn', (0.14, 0.14, 0.5), mm('horn'), (hx + 0.1 + sgn * 0.32, 0.05, Hd.top + 0.2), rot=(-25, sgn * 15, 0), bev=0.03)
    for j in range(9):
        p('mane', (0.1, 0.3, 0.3), mm('accent'), (hx + 0.1 + (j - 4) * 0.09, 0.3, Hd.top - 0.05 + 0.03 * (4 - abs(j - 4))), rot=(30, 0, 0))
    # tail tip in the mouth
    p('tail_tip', (0.3, 0.3, 0.3), mm('accent'), (math.cos(math.radians(-90 + 24 * 15 - 15)) * R, -0.1, zc + math.sin(math.radians(-90 + 24 * 15 - 15)) * R), rot=(0, 45, 0))
    # rarity 6: the rift of lightning inside the ring (glow segment), crown, two orbits, red aura
    sg('glow', 'body', (0, 0, zc))
    a.glow.append('glow')
    pts = ((-0.2, 0.9), (0.15, 0.45), (-0.15, 0.1), (0.2, -0.3), (-0.1, -0.7))
    for j in range(len(pts) - 1):
        (x0, z0), (x1, z1) = pts[j], pts[j + 1]
        ln = math.hypot(x1 - x0, z1 - z0)
        p('rift_bolt', (0.12, 0.08, ln + 0.08), mm('glow2' if j % 2 else 'glow'), ((x0 + x1) / 2, 0, zc + (z0 + z1) / 2), rot=(0, math.degrees(math.atan2(x1 - x0, z1 - z0)), 0))
    b('rift_core', (0.4, 0.06, 0.9), mm('glow3'), (0, 0.04, zc), rot=(0, 15, 0), bev=0.02)
    for i in range(6):
        ang = math.radians(i * 60)
        p('rift_spark', (0.1, 0.1, 0.1), mm('glow'), (math.cos(ang) * 0.6, 0, zc + math.sin(ang) * 0.6), rot=(45, 45, 0))
    halo_kit(Hd, 'glow2', r=0.42, n=6, dz=0.7, kind='shards')
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, zc - R), Hit=(0, -0.3, zc))
    orbit_kit((0, 0, zc), 2.4, 6, 'glow', 'glow2', size=0.16, dz=0.5, shape='cross')
    orbit_kit((0, 0, zc - 0.8), 2.8, 8, 'glow3', 'glow', size=0.1, name='orbit2', dz=0.2, shape='shard')
    aura_kit(2.2, 6, motes=12, mote_col='glow', height=4.0, style='rays')
    return finish(a)


ANIMALS = dict(fulgurite_cricket=fulgurite_cricket, rift_kangaroo=rift_kangaroo, thunder_centaur=thunder_centaur,
               prism_revenant=prism_revenant, storm_harrier=storm_harrier, rift_serpent=rift_serpent)
