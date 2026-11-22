# Biome 22 - Bone Dunes: pale dunes, half-buried giant bones, fossils, dry wind
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 22
GROUND = '#d8b878'
SKY = '#f0d8a8'
THEME = dict(bits=['#f0e8d0', '#c8a868'], dust='#e0c890', glow='#ffe08a', splash='#f0d8a0', bit_name='песок и костяная крошка')
FOOT = dict(bone_vulture=1.9, sand_reaper=1.9, skeletal_colossus=1.0)
BUSH_NAME = 'костяной куст: полузасыпанная грудная клетка, сквозь рёбра растёт пустынный кустарник с сухими цветами'


def bush():
    B = begin_bush(NN)
    sand = mat('sand', '#e0c080')
    sand2 = mat('sand2', '#c8a868')
    bone = mat('bone', '#f4ecd8')
    bone2 = mat('bone2', '#d8ccb0')
    shrub = mat('shrub', '#8a9a4a')
    shrub2 = mat('shrub2', '#a8a85a')
    flower = mat('flower', '#e86a5a')
    glow = mat('glow', '#ffe08a', 'neon', 2.2)
    part('big', (0, 0.3, 0.3), 'dune')
    b('dune', (6.4, 2.6, 0.6), sand, (0, 0.3, 0.3), bev=0.25)
    b('dune_top', (4.0, 1.8, 0.3), sand2, (-0.6, 0.4, 0.7), bev=0.12)
    # half buried ribcage: spine + arching ribs
    b('spine', (5.2, 0.4, 0.4), bone2, (0, 0.6, 0.8), bev=0.08)
    for i in range(6):
        x = -2.2 + i * 0.88
        h = 2.8 - abs(i - 2.5) * 0.4
        part('big' if 1 <= i <= 4 else 'small', (x, 0.0, h * 0.6), 'rib_%d' % i)
        for sgn in (-1, 1):
            b('rib', (0.26, 0.26, h), bone, (x, 0.6 + sgn * 0.7, 0.6 + h / 2), rot=(sgn * -18, 0, 0), bev=0.06)
        p('rib_knob', (0.34, 0.34, 0.2), bone2, (x, 0.6, 0.6 + h + 0.05))
    # desert shrub growing through the ribs
    for i, (x, z, s) in enumerate(((-0.8, 2.6, 1.3), (0.6, 3.0, 1.5), (1.8, 2.3, 1.1), (-2.0, 1.9, 1.0), (0.0, 3.9, 1.0))):
        part('big' if s > 1.2 else 'small', (x, 0.6, z), 'shrub_%d' % i)
        b('shrub', (s, s * 0.9, s * 0.8), shrub if i % 2 else shrub2, (x, 0.6, z), bev=0.14)
        for j in range(3):
            ang = math.radians(j * 120 + 30)
            p('dry_flower', (0.2, 0.2, 0.16), flower, (x + math.cos(ang) * s * 0.4, 0.6 - s * 0.45, z + math.sin(ang) * s * 0.3))
    for i, (x, y) in enumerate(((2.8, -0.6), (-2.9, -0.5))):
        part('small', (x, y, 0.8), 'skull_%d' % i)
        b('small_skull', (0.6, 0.5, 0.5), bone, (x, y, 0.8), bev=0.1)
        for sgn in (-1, 1):
            p('socket', (0.14, 0.06, 0.14), glow, (x + sgn * 0.14, y - 0.26, 0.86))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def fossil_trilobite(row):
    """trilobite: a flat oval three-lobed shield split into ribbed segments, big crescent eyes on top of the head shield,
    a fringe of tiny legs peeking out, two short tail spines"""
    a = start(row, dict(main='#a8885a', belly='#e8d8b0', dark='#5a4028', accent='#4ab8a8', leg='#6a5038', blush='#ff9ab4'), 0.75)
    sg('body', 'root', (0, 0.2, 0.3))
    B = None
    for i in range(6):
        w = 1.5 - 0.12 * i
        y = 0.1 + i * 0.28
        bx = b('thorax_seg', (w, 0.26, 0.28), mm('main' if i % 2 else 'belly'), (0, y, 0.3), bev=0.06)
        if i == 1:
            B = bx
        b('axial_lobe', (0.4, 0.28, 0.14), mm('dark'), (0, y, 0.48), bev=0.04)
        for sgn in (-1, 1):
            p('pleura_tip', (0.12, 0.2, 0.08), mm('dark'), (sgn * (w / 2 + 0.04), y + 0.04, 0.24))
            p('leg', (0.24, 0.05, 0.05), mm('leg'), (sgn * (w / 2 - 0.02), y, 0.1), rot=(0, sgn * -25, 0))
    sg('head', 'body', (0, -0.1, 0.3))
    Hd = b('cephalon', (1.6, 0.6, 0.4), mm('main'), (0, -0.36, 0.32), bev=0.12)
    b('glabella', (0.56, 0.5, 0.22), mm('belly'), (0, -0.36, 0.56), bev=0.08)
    for sgn in (-1, 1):
        p('genal_spine', (0.12, 0.6, 0.1), mm('dark'), (sgn * 0.78, 0.0, 0.26), rot=(0, 0, sgn * -10))
        p('blush', (0.12, 0.03, 0.05), mm('blush'), (sgn * 0.26, Hd.front - 0.012, 0.24))
    eyes(Box((0, -0.4, 0.62), (0.9, 0.36, 0.34), 'head'), 0.8, 0.32, 0.0, iris='#4ab8a8', brow=None)
    p('smile', (0.18, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 0.22))
    for sgn, n in LR:
        nm = 'antenna_' + n
        sg(nm, 'head', (sgn * 0.2, Hd.front, 0.2))
        a.ears.append(nm)
        p('antenna', (0.05, 0.4, 0.05), mm('leg'), (sgn * 0.3, Hd.front - 0.2, 0.18), rot=(0, 0, sgn * 25))
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.6, 0.6, 0.15))
        a.legs.append(nm)
        p('leg_front', (0.22, 0.05, 0.05), mm('leg'), (sgn * 0.7, -0.1, 0.1), rot=(0, sgn * -25, 0))
    sg('tail', 'body', (0, 1.6, 0.3))
    a.tail = ['tail']
    b('pygidium', (0.7, 0.4, 0.22), mm('main'), (0, 1.86, 0.28), bev=0.06)
    for sgn in (-1, 1):
        p('tail_spine', (0.08, 0.4, 0.08), mm('dark'), (sgn * 0.2, 2.2, 0.26), rot=(0, 0, sgn * 12))
    grid(Box((0, 0.8, 0.3), (1.2, 1.6, 0.28)), 't', 2, 4, mm('accent'), (0.08, 0.08), name='fossil_dot', span=(0.7, 0.8), offset=0.12)
    use('head')
    grid(Hd, 't', 4, 1, mm('dark'), (0.08, 0.08), name='head_dot', span=(0.8, 0.1), offset=0.0)
    for sgn in (-1, 1):
        p('cheek_ridge', (0.3, 0.06, 0.06), mm('dark'), (sgn * 0.5, Hd.front - 0.01, 0.4))
        p('mouth_hook', (0.04, 0.03, 0.06), mm('dark'), (sgn * 0.09, Hd.front - 0.012, 0.2))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.7, 0.3), Hit=(0, 0.8, 0.5))
    return finish(a)


def dune_ankylosaur(row):
    """dune ankylosaur flat as a rug: wide low armoured body with a skirt of side spikes, a stubby face,
    and its club tail curled UP AND FORWARD over its back like a scorpion"""
    a = start(row, dict(main='#c8985a', belly='#f0dcb0', dark='#6a4a28', accent='#e86a3a', plate='#a8783a', spike='#f4ecd8', blush='#ff9ab4'), 2.6)
    sg('body', 'root', (0, 0.3, 0.5))
    B = b('body', (1.8, 2.0, 0.6), mm('main'), (0, 0.3, 0.45), bev=0.16)
    b('armor', (1.6, 1.8, 0.3), mm('plate'), (0, 0.3, 0.86), bev=0.1)
    grid(Box((0, 0.3, 0.86), (1.6, 1.8, 0.3)), 't', 3, 4, mm('spike'), (0.16, 0.16), name='osteoderm', span=(0.8, 0.85), th=0.1)
    for j in range(5):
        for sgn in (-1, 1):
            b('side_spike', (0.36, 0.24, 0.2), mm('spike'), (sgn * 1.04, -0.5 + j * 0.4, 0.5), rot=(0, 0, sgn * (-10 + j * 5)), bev=0.04)
    a.bx['feet'] = []
    for fy in (-0.4, 1.0):
        for sgn, n in LR:
            nm = 'leg_%s%s' % ('f' if fy < 0 else 'b', n)
            sg(nm, 'body', (sgn * 0.6, fy, 0.3))
            a.legs.append(nm)
            b('leg', (0.36, 0.4, 0.3), mm('main'), (sgn * 0.6, fy, 0.15), bev=0.06)
            for t in range(3):
                p('toe', (0.08, 0.06, 0.06), mm('spike'), (sgn * 0.6 + (t - 1) * 0.1, fy - 0.22, 0.04))
    sg('head', 'body', (0, -0.7, 0.5))
    Hd = b('head', (0.9, 0.6, 0.56), mm('main'), (0, -0.95, 0.45), bev=0.12)
    b('beak', (0.5, 0.2, 0.26), mm('belly'), (0, Hd.front - 0.06, 0.34), bev=0.05)
    b('head_plate', (0.8, 0.5, 0.14), mm('plate'), (0, -0.95, Hd.top + 0.04), bev=0.04)
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.3, Hd.front - 0.012, 0.4))
        p('cheek_horn', (0.14, 0.14, 0.18), mm('spike'), (sgn * 0.48, -0.9, 0.56), rot=(0, sgn * 30, 0))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.3, -0.95, Hd.top))
        a.ears.append(nm)
        p('head_spike', (0.12, 0.12, 0.14), mm('spike'), (sgn * 0.3, -0.85, Hd.top + 0.16))
    eyes(Hd, 0.3, 0.24, 0.14, iris='#6a4a28', brow='#6a4a28')
    # the tail curls up and forward over the back (the silhouette)
    use('body')
    path = ((0, 1.4, 0.6), (0, 1.75, 1.0), (0, 1.75, 1.55), (0, 1.4, 2.0), (0, 0.9, 2.2))
    par = 'body'
    a.tail = []
    for i, (x, y, z) in enumerate(path):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, (x, y, z - 0.1))
        a.tail.append(nm)
        s = 0.46 - 0.04 * i
        b('tail_seg', (s, s, s), mm('main' if i % 2 else 'plate'), (x, y, z), bev=0.06)
        for sgn in (-1, 1):
            p('tail_spike', (0.12, 0.1, 0.1), mm('spike'), (sgn * (s / 2 + 0.05), y, z))
        par = nm
    b('club', (0.8, 0.6, 0.6), mm('plate'), (0, 0.4, 2.25), bev=0.14)
    for sgn in (-1, 1):
        b('club_lobe', (0.3, 0.5, 0.5), mm('spike'), (sgn * 0.44, 0.4, 2.25), bev=0.08)
    p('club_band', (0.84, 0.1, 0.64), mm('accent'), (0, 0.6, 2.25))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -1.0, 0.4), Hit=(0, 0.3, 1.0))
    return finish(a)


def fossil_ceratopsian(row):
    """a stubby ceratopsian whose huge round frill is a fossil sun-disc: a giant fan of bone studs around its head,
    three horns, short chunky legs, beaky smile"""
    a = start(row, dict(main='#8a9a5a', belly='#e8e0b0', dark='#3a4228', accent='#e8a84a', frill='#d8b878', frill2='#f4ecd8', horn='#fff8e8',
                        blush='#ff9ab4'), 2.91)
    B, Hd = quad(bw=1.4, bl=1.8, bh=1.0, legh=0.5, lw=0.42, hw=1.1, hd=1.0, hh=0.9, head_up=0.3, toe='horn', head_fwd=0.24,
                 rump=True, chest=True, ntoe=3)
    use('head')
    b('beak', (0.5, 0.36, 0.4), mm('belly'), (0, Hd.front - 0.12, Hd.c.z - 0.2), bev=0.08)
    p('beak_tip', (0.2, 0.14, 0.16), mm('dark'), (0, Hd.front - 0.3, Hd.c.z - 0.3))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('blush'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.1))
        b('brow_horn', (0.16, 0.16, 0.6), mm('horn'), (sgn * 0.28, Hd.front + 0.1, Hd.top + 0.24), rot=(-30, 0, 0), bev=0.04)
    b('nose_horn', (0.16, 0.16, 0.36), mm('horn'), (0, Hd.front - 0.2, Hd.c.z + 0.12), rot=(-20, 0, 0), bev=0.04)
    p('nose_horn_tip', (0.1, 0.1, 0.1), mm('accent'), (0, Hd.front - 0.27, Hd.c.z + 0.3))
    p('chin', (0.3, 0.1, 0.1), mm('dark'), (0, Hd.front - 0.2, Hd.c.z - 0.42))
    eyes(Hd, 0.3, 0.24, 0.06, iris='#3a4228', brow='#3a4228', lash=True)
    # the giant round frill (the silhouette): a stepped disc behind the head
    FY = Hd.back + 0.1
    FZ = Hd.c.z + 0.5
    b('frill', (2.4, 0.2, 2.0), mm('frill'), (0, FY, FZ), bev=0.16)
    b('frill_in', (1.8, 0.22, 1.5), mm('frill2'), (0, FY - 0.02, FZ), bev=0.12)
    for k_ in range(14):
        ang = math.radians(k_ * (180 / 13))
        p('frill_stud', (0.24, 0.24, 0.24), mm('horn'), (math.cos(ang) * 1.2, FY, FZ + math.sin(ang) * 1.0 + 0.0), rot=(0, 45, 0))
    for k_ in range(5):
        ang = math.radians(30 + k_ * 30)
        p('frill_ray', (0.08, 0.06, 0.6), mm('accent'), (math.cos(ang) * 0.55, FY - 0.13, FZ + math.sin(ang) * 0.45), rot=(0, 90 - math.degrees(ang), 0))
    for sgn in (-1, 1):
        b('frill_hole', (0.36, 0.24, 0.3), mm('dark'), (sgn * 0.6, FY - 0.03, FZ + 0.35), bev=0.06)
    use('body')
    grid(B, 't', 3, 3, mm('dark'), (0.14, 0.14), name='back_scale', span=(0.7, 0.7))
    grid(B, 'l', 3, 2, mm('belly'), (0.12, 0.12), name='side_scale', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('belly'), (0.12, 0.12), name='side_scale', span=(0.7, 0.5))
    grid(B, 'k', 3, 2, mm('dark'), (0.12, 0.12), name='rump_scale', span=(0.7, 0.5))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_band', (ft.s.x + 0.04, ft.s.y + 0.04, 0.08), mm('dark'), (ft.c.x, ft.c.y, 0.36))
    use('head')
    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_scale', span=(0.5, 0.5))
    for k_ in range(6):
        ang = math.radians(15 + k_ * 30)
        p('frill_spot', (0.12, 0.06, 0.12), mm('accent'), (math.cos(ang) * 0.85, FY - 0.13, FZ + math.sin(ang) * 0.68))
    use('body')
    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.34)
    a.bx.update(body=B, head=Hd)
    return finish(a)


def skeletal_colossus(row):
    """a walking dinosaur fossil skeleton: horizontal theropod pose, a big friendly skull, see-through ribcage of separate ribs
    with a glowing heart, two strong legs, tiny arms, a long vertebrae tail held straight back"""
    a = start(row, dict(main='#f4ecd8', belly='#fff8ec', dark='#5a4a3a', accent='#c8a868', joint='#d8ccb0', blush='#ff9ab4',
                        **{'*glow': '#ff6a8a', '*glow2': '#ffe08a'}), 3.73)
    LEG = 1.6
    zb = LEG + 0.5
    sg('body', 'root', (0, 0.2, zb))
    # spine
    for i in range(6):
        b('vertebra', (0.3, 0.34, 0.3), mm('main'), (0, -0.6 + i * 0.36, zb + 0.5), bev=0.06)
        p('spine_fin', (0.1, 0.16, 0.24), mm('joint'), (0, -0.6 + i * 0.36, zb + 0.74))
        for sgn in (-1, 1):
            p('vert_process', (0.2, 0.1, 0.08), mm('joint'), (sgn * 0.24, -0.6 + i * 0.36, zb + 0.52))
    B = Box((0, 0.3, zb), (1.2, 1.8, 1.1), 'body')
    # ribcage: separate ribs hanging from the spine
    for i in range(5):
        y = -0.5 + i * 0.36
        h = 1.0 - abs(i - 2) * 0.12
        for sgn in (-1, 1):
            b('rib', (0.14, 0.14, h), mm('main'), (sgn * 0.48, y, zb + 0.5 - h / 2), rot=(0, sgn * 18, 0), bev=0.03)
        p('sternum', (0.5, 0.12, 0.12), mm('joint'), (0, y, zb + 0.5 - h - 0.02))
    b('heart', (0.36, 0.36, 0.36), mm('glow'), (0, 0.0, zb), rot=(45, 45, 0), bev=0.04)
    # hips and legs
    b('pelvis', (0.8, 0.5, 0.4), mm('main'), (0, 1.3, zb + 0.4), bev=0.08)
    for sgn in (-1, 1):
        p('hip_knob', (0.2, 0.2, 0.2), mm('joint'), (sgn * 0.42, 1.3, zb + 0.66))
    a.bx['feet'] = []
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.4, 1.3, zb + 0.2))
        a.legs.append(nm)
        b('femur', (0.24, 0.24, 1.0), mm('main'), (sgn * 0.42, 1.1, zb - 0.3), rot=(-20, 0, 0), bev=0.04)
        p('knee', (0.3, 0.3, 0.3), mm('joint'), (sgn * 0.42, 0.95, zb - 0.8))
        b('shin', (0.2, 0.2, 1.0), mm('main'), (sgn * 0.42, 1.1, LEG / 2 - 0.1), rot=(15, 0, 0), bev=0.04)
        b('foot', (0.3, 0.7, 0.16), mm('main'), (sgn * 0.42, 0.9, 0.08), bev=0.04)
        for t in range(3):
            p('toe_claw', (0.08, 0.16, 0.08), mm('dark'), (sgn * 0.42 + (t - 1) * 0.12, 0.5, 0.06))
    # tiny arms
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.4, -0.5, zb + 0.2))
        a.arms.append(nm)
        b('arm', (0.12, 0.12, 0.4), mm('main'), (sgn * 0.44, -0.6, zb - 0.05), rot=(30, 0, 0), bev=0.02)
        for t in range(2):
            p('finger', (0.05, 0.1, 0.05), mm('dark'), (sgn * 0.44 + (t - 0.5) * 0.08, -0.74, zb - 0.26))
    # neck and skull
    sg('head', 'body', (0, -0.8, zb + 0.6))
    b('neck_bone', (0.24, 0.5, 0.24), mm('main'), (0, -0.95, zb + 0.75), rot=(-30, 0, 0), bev=0.04)
    for j in range(4):
        p('neck_knob', (0.3, 0.08, 0.1), mm('joint'), (0, -0.78 - j * 0.1, zb + 0.62 + j * 0.06))
    Hd = b('skull', (1.0, 1.1, 0.8), mm('main'), (0, -1.5, zb + 1.1), bev=0.14)
    b('jaw', (0.8, 0.8, 0.24), mm('joint'), (0, -1.62, zb + 0.6), bev=0.06)
    for sgn in (-1, 1):
        p('jaw_hinge', (0.1, 0.2, 0.2), mm('accent'), (sgn * 0.42, -1.3, zb + 0.66))
    for t in range(5):
        p('tooth', (0.08, 0.06, 0.12), mm('belly'), ((t - 2) * 0.14, Hd.front + 0.04, zb + 0.74))
    for sgn, n in LR:
        p('cheek_hole', (0.06, 0.4, 0.24), mm('dark'), (sgn * 0.51, -1.5, zb + 1.0))
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.3, Hd.front - 0.012, zb + 0.9))
        nm = 'brow_' + n
        sg(nm, 'head', (sgn * 0.3, -1.5, Hd.top))
        a.ears.append(nm)
        p('brow_knob', (0.24, 0.3, 0.14), mm('accent'), (sgn * 0.3, -1.5, Hd.top + 0.06))
    p('nostril', (0.2, 0.04, 0.08), mm('dark'), (0, Hd.front - 0.012, zb + 1.32))
    eyes(Hd, 0.34, 0.25, 0.08, iris='#ff6a8a', glow='#ff6a8a', brow=None)
    grid(Hd, 't', 2, 3, mm('accent'), (0.1, 0.1), name='skull_crack', span=(0.5, 0.6))
    # long vertebrae tail held straight back
    use('body')
    par = 'body'
    a.tail = []
    for i in range(3):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        y0 = 1.6 + i * 0.75
        sg(nm, par, (0, y0 - 0.1, zb + 0.4 - i * 0.12))
        a.tail.append(nm)
        for j in range(3):
            s = 0.28 - 0.03 * i - 0.01 * j
            b('tail_vert', (s, 0.22, s), mm('main'), (0, y0 + j * 0.25, zb + 0.4 - i * 0.12 - j * 0.04), bev=0.03)
            p('tail_fin', (0.06, 0.1, 0.14), mm('joint'), (0, y0 + j * 0.25, zb + 0.4 - i * 0.12 - j * 0.04 + s / 2 + 0.05))
        par = nm
    # rarity 4: glowing heart core + sparks between ribs (glow seg)
    sg('glow', 'body', (0, 0.0, zb))
    a.glow.append('glow')
    for i in range(6):
        p('soul_spark', (0.1, 0.1, 0.1), mm('glow2' if i % 2 else 'glow'), (0.3 * math.sin(i * 1.3), -0.3 + i * 0.18, zb + 0.25 * math.cos(i * 1.7)), rot=(45, 45, 0))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.5, zb), Hit=(0, 0.3, zb + 0.4))
    aura_kit(1.8, 4, motes=8, mote_col='glow2', height=3.6)
    return finish(a)


def sand_reaper(row):
    """sand reaper (antlion): a fat round sandy body low to the ground, a flat head with HUGE sickle jaws spread wide
    in front, six short hairy legs, bristle tufts, sand flowing off its back"""
    a = start(row, dict(main='#c8a060', belly='#f0dcb0', dark='#5a3a20', accent='#e86a3a', jaw='#3a2a1a', hair='#8a6a3a', blush='#ff9ab4',
                        **{'*glow': '#ffd84a', '*glow2': '#ff8a3a'}), 1.91)
    sg('body', 'root', (0, 0.4, 0.8))
    B = b('abdomen', (2.0, 2.2, 1.4), mm('main'), (0, 0.8, 0.8), bev=0.3)
    b('abdomen_top', (1.5, 1.6, 0.4), mm('main'), (0, 0.8, 1.6), bev=0.14)
    for j in range(4):
        p('abd_band', (2.04, 0.1, 1.2), mm('dark'), (0, 0.1 + j * 0.45, 0.8))
    grid(B, 'l', 4, 3, mm('hair'), (0.12, 0.12), name='bristle', span=(0.8, 0.7), th=0.12)
    grid(B, 'r', 4, 3, mm('hair'), (0.12, 0.12), name='bristle', span=(0.8, 0.7), th=0.12)
    grid(B, 'k', 3, 3, mm('hair'), (0.14, 0.14), name='bristle', span=(0.7, 0.7), th=0.12)
    grid(Box((0, 0.8, 1.6), (1.5, 1.6, 0.4)), 't', 3, 3, mm('belly'), (0.16, 0.16), name='back_spot', span=(0.7, 0.7))
    b('thorax', (1.2, 0.7, 0.8), mm('main'), (0, -0.5, 0.6), bev=0.16)
    TB = Box((0, -0.5, 0.6), (1.2, 0.7, 0.8))
    grid(TB, 't', 3, 2, mm('belly'), (0.1, 0.1), name='thorax_spot', span=(0.7, 0.6))
    grid(TB, 'l', 2, 2, mm('hair'), (0.1, 0.1), name='thorax_hair', span=(0.6, 0.5))
    grid(TB, 'r', 2, 2, mm('hair'), (0.1, 0.1), name='thorax_hair', span=(0.6, 0.5))
    for i, y in enumerate((-0.6, -0.2, 0.3)):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.6, y, 0.5))
            a.legs.append(nm)
            b('leg', (0.5, 0.16, 0.16), mm('dark'), (sgn * 0.85, y, 0.38), rot=(0, sgn * -35, 0), bev=0.03)
            b('leg_low', (0.14, 0.14, 0.36), mm('dark'), (sgn * 1.1, y, 0.18), bev=0.03)
            for t in range(4):
                p('leg_hair', (0.06, 0.06, 0.12), mm('hair'), (sgn * (0.7 + 0.12 * t), y, 0.52 - 0.06 * t))
            p('leg_foot', (0.18, 0.2, 0.06), mm('jaw'), (sgn * 1.1, y - 0.03, 0.03))
    sg('head', 'body', (0, -0.8, 0.6))
    Hd = b('head', (1.1, 0.7, 0.5), mm('main'), (0, -1.1, 0.5), bev=0.12)
    eyes(Hd, 0.4, 0.26, 0.2, iris='#e86a3a', brow='#5a3a20')
    grid(Hd, 't', 3, 2, mm('hair'), (0.1, 0.1), name='head_bristle', span=(0.7, 0.6))
    p('smile', (0.2, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 0.36))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.34, Hd.front - 0.012, 0.42))
        # huge sickle jaws (the silhouette)
        nm = 'claw_' + n
        sg(nm, 'head', (sgn * 0.4, Hd.front, 0.4))
        a.arms.append(nm)
        pts = ((0.45, 0.0), (0.85, -0.35), (0.95, -0.8), (0.75, -1.25), (0.35, -1.55))
        for j in range(4):
            (x0, y0), (x1, y1) = pts[j], pts[j + 1]
            cx, cy = sgn * (x0 + x1) / 2, Hd.front + (y0 + y1) / 2
            ln = math.hypot(x1 - x0, y1 - y0) + 0.12
            rz = math.degrees(math.atan2(sgn * (x1 - x0), -(y1 - y0)))
            b('jaw_seg', (0.28, ln, 0.24), mm('jaw'), (cx, cy, 0.42), rot=(0, 0, rz), bev=0.04)
            p('jaw_tooth', (0.08, 0.1, 0.12), mm('belly'), (cx - sgn * 0.16, cy, 0.42))
            p('jaw_tooth2', (0.08, 0.08, 0.1), mm('belly'), (cx - sgn * 0.16, cy + 0.14, 0.42))
        p('jaw_tip', (0.2, 0.26, 0.2), mm('accent'), (sgn * 0.35, Hd.front - 1.6, 0.42), rot=(0, 0, sgn * 60))
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.3, -1.1, Hd.top))
        a.ears.append(nm)
        p('head_tuft', (0.16, 0.16, 0.2), mm('hair'), (sgn * 0.3, -1.1, Hd.top + 0.08))
    # sand pouring off the back (tail)
    use('body')
    sg('tail', 'body', (0, 1.8, 1.0))
    a.tail = ['tail']
    for j in range(9):
        p('sand_stream', (0.3 - 0.02 * j, 0.2, 0.2), mm('belly'), (0.1 * (j % 2), 1.95 + j * 0.04, 1.2 - j * 0.13))
    # rarity 5: glowing jaw tips + abdomen glow bands, orbit, yellow aura
    sg('glow', 'body', (0, 0.8, 1.0))
    a.glow.append('glow')
    for j in range(3):
        p('band_glow', (2.06, 0.06, 0.2), mm('glow2' if j % 2 else 'glow'), (0, 0.32 + j * 0.45, 1.3))
    for sgn, n in LR:
        use('claw_' + n)
        p('jaw_glow', (0.1, 0.16, 0.1), mm('glow'), (sgn * 0.3, Hd.front - 1.74, 0.42))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -1.0, 0.6), Hit=(0, 0.8, 1.5))
    orbit_kit((0, 0.6, 1.2), 2.4, 6, 'glow', 'glow2', size=0.14, dz=0.4, shape='shard')
    aura_kit(2.2, 5, motes=10, mote_col='glow', height=2.0, style='diamond')
    return finish(a)


def bone_vulture(row):
    """bone vulture gliding with the body HORIZONTAL and the wings raised in a high V; every wing is a fan of separate
    bone feather-rays with gaps between them; bald pink head on a long dipping neck, white ruff, bone mask beak"""
    zc = 0.8
    a = start(row, dict(main='#3a2e3a', belly='#6a5a6a', dark='#1e161e', accent='#e8a0a8', bone='#f4ecd8', bone2='#d8ccb0', ruff='#fff8f0',
                        **{'*glow': '#ff5a6a', '*glow2': '#ffe08a', '*glow3': '#c88aff'}), 2.53, hover=4.0, z0=zc)
    sg('body', 'root', (0, 0.3, zc))
    B = b('body', (1.0, 1.8, 0.8), mm('main'), (0, 0.4, zc), bev=0.16)
    b('belly', (0.8, 1.5, 0.1), mm('belly'), (0, 0.4, zc - 0.42), bev=0.04)
    grid(B, 't', 4, 5, mm('belly'), (0.1, 0.1), name='back_feather', span=(0.7, 0.8))
    # ruff collar
    for k_ in range(16):
        ang = math.radians(k_ * 22.5)
        p('ruff', (0.24, 0.3, 0.22), mm('ruff'), (math.cos(ang) * 0.48, -0.5, zc + math.sin(ang) * 0.42), rot=(0, -k_ * 22.5, 0))
    # long dipping neck and bald head
    sg('head', 'body', (0, -0.55, zc))
    for j in range(3):
        b('neck', (0.26, 0.3, 0.26), mm('accent'), (0, -0.7 - j * 0.24, zc - 0.1 - j * 0.12), bev=0.05)
        p('neck_wrinkle', (0.28, 0.06, 0.28), mm('main'), (0, -0.6 - j * 0.24, zc - 0.06 - j * 0.12))
    Hd = b('head', (0.7, 0.6, 0.56), mm('accent'), (0, -1.5, zc - 0.36), bev=0.14)
    b('bone_mask', (0.74, 0.3, 0.3), mm('bone'), (0, -1.6, Hd.top - 0.06), bev=0.06)
    b('beak', (0.3, 0.5, 0.26), mm('bone'), (0, Hd.front - 0.2, zc - 0.48), rot=(20, 0, 0), bev=0.05)
    p('beak_hook', (0.16, 0.12, 0.2), mm('dark'), (0, Hd.front - 0.44, zc - 0.62))
    eyes(Hd, 0.34, 0.25, 0.08, iris='#ff5a6a', glow='#ff5a6a', brow=None)
    grid(Hd, 'l', 2, 2, mm('main'), (0.08, 0.08), name='head_spot', span=(0.5, 0.5))
    grid(Hd, 'r', 2, 2, mm('main'), (0.08, 0.08), name='head_spot', span=(0.5, 0.5))
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.3, -1.5, Hd.top))
        a.ears.append(nm)
        p('mask_horn', (0.1, 0.1, 0.26), mm('bone2'), (sgn * 0.3, -1.55, Hd.top + 0.14), rot=(-20, sgn * 15, 0))
    # V wings: fans of separate bone rays (the silhouette)
    use('body')
    for sgn, n in LR:
        nm = 'wing_' + n
        sg(nm, 'body', (sgn * 0.5, 0.2, zc + 0.2))
        a.wings.append(nm)
        b('wing_arm', (1.2, 0.24, 0.24), mm('bone2'), (sgn * 0.95, 0.2, zc + 0.55), rot=(0, -sgn * 30, 0), bev=0.04)
        p('wing_elbow', (0.3, 0.3, 0.3), mm('bone'), (sgn * 1.5, 0.2, zc + 0.85))
        for j in range(5):
            p('covert', (0.26, 0.3, 0.16), mm('main' if j % 2 else 'belly'), (sgn * (0.6 + j * 0.28), 0.12, zc + 0.36 + j * 0.15))
        for j in range(7):
            ang = 50 - j * 14
            r = math.radians(ang)
            ln = 1.0 - 0.06 * abs(j - 3)
            ox, oz = sgn * (0.8 + 0.1 * j), zc + 0.5 + 0.08 * j
            cx, cz = ox + sgn * math.cos(r) * ln * 0.5, oz + math.sin(r) * ln * 0.5 + 0.3
            b('feather_ray', (ln, 0.12, 0.14), mm('bone' if j % 2 else 'bone2'), (cx, 0.3 + 0.08 * j, cz), rot=(0, -sgn * ang, 0), bev=0.03)
            p('ray_tip', (0.14, 0.14, 0.14), mm('main'), (ox + sgn * math.cos(r) * ln, 0.3 + 0.08 * j, oz + math.sin(r) * ln + 0.3), rot=(0, 45, 0))
    # tail fan of bones
    sg('tail', 'body', (0, 1.3, zc))
    a.tail = ['tail']
    for j in range(7):
        ang = (j - 3) * 13
        b('tail_ray', (0.12, 0.9, 0.1), mm('bone2'), (math.sin(math.radians(ang)) * 0.4, 1.7, zc + 0.1), rot=(0, 0, -ang), bev=0.02)
    # legs tucked under
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.3, 0.8, zc - 0.4))
        a.legs.append(nm)
        b('leg', (0.14, 0.14, 0.4), mm('accent'), (sgn * 0.3, 0.9, zc - 0.56), rot=(-50, 0, 0), bev=0.02)
        for t in range(3):
            p('talon', (0.05, 0.14, 0.05), mm('dark'), (sgn * 0.3 + (t - 1) * 0.07, 1.1, zc - 0.72))
    # rarity 6: glowing ray tips & ribs on the belly, crown, two orbits, red aura
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(0, 7, 2):
            ang = 50 - j * 14
            r = math.radians(ang)
            ln = 1.0 - 0.06 * abs(j - 3)
            ox, oz = sgn * (0.8 + 0.1 * j), zc + 0.5 + 0.08 * j
            p('ray_glow', (0.1, 0.16, 0.1), mm('glow3'), (ox + sgn * math.cos(r) * ln * 0.7, 0.26 + 0.08 * j, oz + math.sin(r) * ln * 0.7 + 0.3), rot=(0, 45, 0))
    sg('glow', 'body', (0, 0.4, zc - 0.4))
    a.glow.append('glow')
    for j in range(5):
        p('belly_rib_glow', (0.7, 0.06, 0.06), mm('glow' if j % 2 else 'glow2'), (0, 0.0 + j * 0.2, zc - 0.48))
    halo_kit(Hd, 'glow2', r=0.4, n=6, dz=0.65, kind='flames')
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.6, zc - 0.2), Hit=(0, 0.4, zc + 0.3))
    orbit_kit((0, 0.3, zc + 0.6), 3.0, 6, 'glow', 'glow3', size=0.16, dz=0.5, shape='shard')
    orbit_kit((0, 0.3, zc - 0.2), 2.4, 8, 'glow2', 'glow', size=0.1, name='orbit2', dz=0.2, shape='flame')
    aura_kit(2.4, 6, motes=12, mote_col='glow', height=3.0, style='double')
    return finish(a)


ANIMALS = dict(fossil_trilobite=fossil_trilobite, dune_ankylosaur=dune_ankylosaur, fossil_ceratopsian=fossil_ceratopsian,
               skeletal_colossus=skeletal_colossus, sand_reaper=sand_reaper, bone_vulture=bone_vulture)
