# Biome 7 - Mirage Dunes: dunes, oases, ruins in the sand
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 7
GROUND = '#d6b266'
SKY = '#fff2d0'
THEME = dict(bits=['#f2dc9c', '#7ab85a'], dust='#f6e4b4', glow='#5ae8e0', splash='#bff4f0', bit_name='песок и травинки')
FOOT = dict(sand_wyrm=1.2)
BUSH_NAME = 'песчаный холм с пучками травы, пальмой-ростком, обломком колонны и цветами оазиса'


def bush():
    B = begin_bush(NN)
    s1 = mat('sand', '#f0d490')
    s2 = mat('sand2', '#e0ba6c')
    s3 = mat('sand3', '#fae8b8')
    gr = mat('grass', '#8fc85a')
    gr2 = mat('grass2', '#6aa844')
    palm = mat('palm', '#5ab860')
    palm2 = mat('palm2', '#3f9a4c')
    trunk = mat('trunk', '#a8784a')
    stone = mat('stone', '#d8c8a8')
    stone2 = mat('stone2', '#b8a888')
    fl = mat('flower', '#ff7ab0')
    gem = mat('gem', '#5ae8e0', 'neon', 2.0)
    coco = mat('coco', '#7a5230')
    # dune: stepped mounds with wind ripples
    for i, (x, y, w, d, h) in enumerate(((0, 0.3, 5.6, 3.0, 1.2), (-0.6, 0.5, 3.8, 2.3, 2.0), (-1.0, 0.6, 2.2, 1.6, 2.7), (2.4, 0.2, 2.2, 2.0, 1.7))):
        part('big', (x, y, 0.2), 'dune_%d' % i)
        b('dune', (w, d, h), (s1, s2, s1, s2)[i], (x, y, h / 2), bev=0.16)
        b('dune_top', (w * 0.7, d * 0.7, 0.3), s3, (x + 0.1, y, h + 0.1), bev=0.1)
        for j in range(3):
            p('ripple', (w * (0.8 - 0.15 * j), 0.06, 0.07), s3, (x, y - d / 2 - 0.01, h * (0.3 + 0.22 * j)))
    # half-buried ruin column + broken block
    part('big', (2.9, -0.6, 0.2), 'column')
    b('column', (0.8, 0.8, 2.6), stone, (2.9, -0.6, 1.2), rot=(0, 10, 0), bev=0.08)
    for j in range(4):
        p('column_groove', (0.1, 0.05, 2.2), stone2, (2.9 + (j - 1.5) * 0.2, -1.01, 1.2), rot=(0, 10, 0))
    b('column_cap', (1.1, 1.1, 0.3), stone, (3.14, -0.6, 2.6), rot=(0, 10, 0), bev=0.06)
    p('column_gem', (0.24, 0.06, 0.24), gem, (2.95, -1.02, 2.0), rot=(0, 45, 0))
    part('big', (-3.0, -0.7, 0.2), 'block')
    b('block', (1.2, 1.0, 0.8), stone, (-3.0, -0.7, 0.4), rot=(0, 0, 14), bev=0.08)
    p('block_rune', (0.5, 0.05, 0.1), stone2, (-3.05, -1.2, 0.5), rot=(0, 0, 14))
    p('block_rune', (0.1, 0.05, 0.4), stone2, (-3.05, -1.2, 0.4), rot=(0, 0, 14))
    p('block_gem', (0.16, 0.06, 0.16), gem, (-2.7, -1.14, 0.56), rot=(0, 45, 14))
    # palm sprout with fronds and coconuts
    part('big', (0.9, 0.9, 1.6), 'palm_trunk')
    for j in range(5):
        b('palm_trunk', (0.4 - 0.03 * j, 0.4 - 0.03 * j, 0.5), trunk, (0.9 + 0.06 * j, 0.9, 1.5 + j * 0.46), bev=0.06)
        p('palm_ring', (0.44 - 0.03 * j, 0.44 - 0.03 * j, 0.06), coco, (0.9 + 0.06 * j, 0.9, 1.74 + j * 0.46))
    for i in range(6):
        ang = math.radians(i * 60)
        part('small', (1.15, 0.9, 3.8), 'frond_%d' % i)
        for k_ in range(3):
            t = (k_ + 1) / 3.0
            b('frond', (0.7 - 0.12 * k_, 0.36 - 0.06 * k_, 0.12), palm if k_ % 2 == 0 else palm2,
              (1.15 + math.cos(ang) * 0.6 * t * 1.6, 0.9 + math.sin(ang) * 0.6 * t * 1.6, 3.9 + 0.3 * math.sin(math.pi * t) - 0.3 * t), rot=(0, 0, math.degrees(ang)), bev=0.03)
    part('small', (1.15, 0.9, 3.6), 'coconuts')
    for i in range(3):
        b('coconut', (0.26, 0.26, 0.26), coco, (1.15 + math.cos(i * 2.1) * 0.24, 0.9 + math.sin(i * 2.1) * 0.24, 3.56), bev=0.07)
    # grass tufts
    k_ = 0
    for (cx, cy, z, n) in ((-2.2, -0.9, 0.3, 4), (-0.4, -1.2, 0.3, 5), (1.4, -1.1, 0.3, 4), (-1.9, 0.8, 1.9, 4), (0.4, 0.2, 2.0, 4), (3.3, 0.9, 0.3, 3)):
        part('small', (cx, cy, z), 'grass_%d' % k_)
        for i in range(n):
            lean = (i - (n - 1) / 2) * 14
            h = 1.0 - 0.15 * abs(i - (n - 1) / 2)
            b('blade', (0.14, 0.12, h), gr if i % 2 else gr2, (cx + (i - (n - 1) / 2) * 0.16 + math.sin(math.radians(lean)) * h / 2, cy, z + h / 2), rot=(0, lean, 0), bev=0.03)
        k_ += 1
    # oasis flowers
    for i, (x, y, z) in enumerate(((-1.2, -1.4, 0.2), (0.6, -1.5, 0.2), (2.0, -1.2, 0.2), (-2.9, 0.4, 0.2))):
        part('small', (x, y, z), 'flower_%d' % i)
        b('stalk', (0.07, 0.07, 0.5), gr2, (x, y, z + 0.25), bev=0.01)
        for j in range(4):
            ang = math.radians(j * 90)
            p('petal', (0.16, 0.16, 0.08), fl, (x + math.cos(ang) * 0.13, y + math.sin(ang) * 0.13, z + 0.54))
        p('core', (0.12, 0.12, 0.12), mat('core', '#ffd84a'), (x, y, z + 0.58))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def oasis_scarab(row):
    a = start(row, dict(main='#2fa8a0', belly='#3a3a52', dark='#24243a', accent='#ffd84a', shine='#8ff0e4'), 1.3)
    B, Hd = bug(bw=1.1, bl=1.25, bh=0.72, legh=0.3, hw=0.8, hd=0.46, hh=0.56, nleg=3, leg_w=0.11, leg_span=0.42, antenna=0.3, head_z=-0.08)
    use('head')
    b('horn', (0.16, 0.2, 0.3), mm('dark'), (0, Hd.front + 0.06, Hd.top + 0.1), rot=(-20, 0, 0), bev=0.04)
    p('horn_tip', (0.24, 0.12, 0.1), mm('accent'), (0, Hd.front - 0.02, Hd.top + 0.26))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.28, Hd.front - 0.012, Hd.c.z - 0.16))
        p('mandible', (0.1, 0.14, 0.08), mm('dark'), (sgn * 0.14, Hd.front - 0.06, Hd.bot + 0.06))
    eyes(Hd, 0.44, 0.24, 0.1, iris='#e8a020', brow='#24243a', tilt=10)
    use('body')
    # glossy wing cases: split line, golden rim, highlights and dots
    p('split', (0.05, B.s.y * 0.92, 0.04), mm('dark'), (0, B.c.y + 0.03, B.top + 0.13))
    p('rim_f', (B.s.x + 0.04, 0.1, 0.12), mm('accent'), (0, B.front + 0.04, B.top - 0.04))
    for sgn, n in LR:
        p('rim_side', (0.06, B.s.y * 0.9, 0.08), mm('accent'), (sgn * (B.s.x / 2 + 0.01), B.c.y + 0.02, B.bot + 0.1))
        p('shine', (0.24, 0.4, 0.03), mm('shine'), (sgn * 0.26, B.c.y - 0.2, B.top + 0.135))
        p('shine', (0.12, 0.14, 0.03), mm('shine'), (sgn * 0.3, B.c.y + 0.2, B.top + 0.135))
        for j in range(3):
            p('dot', (0.1, 0.1, 0.03), mm('accent'), (sgn * 0.16, B.c.y - 0.3 + j * 0.3, B.top + 0.135))
            p('groove', (0.03, 0.26, 0.2), mm('dark'), (sgn * (B.s.x / 2 + 0.005), B.c.y - 0.34 + j * 0.34, B.c.z + 0.1))
    p('shield', (0.7, 0.3, 0.1), mm('dark'), (0, B.front + 0.12, B.top + 0.1))
    p('shield_gem', (0.16, 0.16, 0.06), mm('accent'), (0, B.front + 0.12, B.top + 0.17), rot=(0, 0, 45))
    p('tail_plate', (0.5, 0.1, 0.3), mm('dark'), (0, B.back + 0.03, B.c.z - 0.1))
    for sgn, n in LR:
        for j in range(2):
            p('vein', (0.03, 0.36, 0.03), mm('shine'), (sgn * (0.1 + 0.26 * j), B.c.y + 0.1, B.top + 0.135))
            p('belly_stud', (0.12, 0.12, 0.05), mm('accent'), (sgn * 0.2, B.c.y - 0.3 + j * 0.6, B.bot - 0.16))
    return finish(a)


def fennec(row):
    """fennec sitting up like a little dog; two GIANT ears spread out sideways wider than its whole body, fluffy tail wrapped round its feet"""
    a = start(row, dict(main='#f2d8a8', belly='#fffaf0', dark='#8a6240', accent='#e0b47a', ear_in='#ffb8b0'), 2.4)
    sg('body', 'root', (0, 0.2, 0.6))
    B = b('body', (0.7, 0.7, 0.9), mm('main'), (0, 0.25, 0.55), rot=(-10, 0, 0), bev=0.16)
    b('chest', (0.5, 0.1, 0.6), mm('belly'), (0, -0.1, 0.6), bev=0.04)
    for j in range(3):
        p('chest_fluff', (0.14, 0.06, 0.14), mm('belly'), ((j - 1) * 0.14, -0.16, 0.86))
    grid(B, 'k', 2, 2, mm('accent'), (0.1, 0.1), name='back_fleck', span=(0.5, 0.5))
    grid(B, 'l', 2, 2, mm('accent'), (0.1, 0.1), name='side_fleck', span=(0.5, 0.5))
    grid(B, 'r', 2, 2, mm('accent'), (0.1, 0.1), name='side_fleck', span=(0.5, 0.5))
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.22, -0.05, 0.4))
        a.legs.append(nm)
        b('front_leg', (0.16, 0.16, 0.45), mm('main'), (sgn * 0.18, -0.12, 0.22), bev=0.03)
        p('front_paw', (0.18, 0.22, 0.08), mm('belly'), (sgn * 0.18, -0.18, 0.04))
        b('haunch', (0.26, 0.5, 0.36), mm('main'), (sgn * 0.33, 0.4, 0.2), bev=0.06)
        p('hind_paw', (0.2, 0.3, 0.08), mm('belly'), (sgn * 0.33, 0.2, 0.04))
    sg('head', 'body', (0, 0.0, 1.0))
    Hd = b('head', (0.74, 0.6, 0.6), mm('main'), (0, -0.05, 1.3), bev=0.14)
    mz = muzzle(Hd, (0.3, 0.26, 0.2), -0.22, 'belly', nose=(0.1, 0.06, 0.08))
    eyes(Hd, 0.36, 0.25, 0.1, iris='#5a3418', lash=True, brow='#8a6240', tilt=10)
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.26, Hd.front - 0.012, 1.2))
        p('cheek_fluff', (0.1, 0.16, 0.14), mm('belly'), (sgn * 0.4, -0.1, 1.2))
        # giant sideways ears (the silhouette)
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.3, -0.05, Hd.top - 0.1))
        a.ears.append(nm)
        b('ear', (0.9, 0.12, 0.62), mm('main'), (sgn * 0.75, -0.02, Hd.top + 0.16), rot=(0, -sgn * 32, 0), bev=0.05)
        p('ear_in', (0.7, 0.04, 0.44), mm('ear_in'), (sgn * 0.72, -0.09, Hd.top + 0.15), rot=(0, -sgn * 32, 0))
        p('ear_tip', (0.2, 0.13, 0.16), mm('dark'), (sgn * 1.15, -0.02, Hd.top + 0.42), rot=(0, -sgn * 32, 0))
        for j in range(3):
            p('ear_fluff', (0.1, 0.05, 0.1), mm('belly'), (sgn * (0.5 + 0.12 * j), -0.11, Hd.top + 0.02 + 0.07 * j))
    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='fore_mark', span=(0.4, 0.4))
    for sgn in (-1, 1):
        for j in range(2):
            p('whisker', (0.24, 0.02, 0.02), mm('dark'), (sgn * 0.3, Hd.front - 0.12, 1.22 + j * 0.05))
    use('body')
    sg('tail', 'body', (0.2, 0.6, 0.25))
    a.tail = ['tail']
    for j in range(5):
        ang = math.radians(90 - j * 45)
        b('tail', (0.3, 0.3, 0.26), mm('main' if j < 4 else 'dark'), (math.cos(ang) * 0.5, 0.3 + math.sin(ang) * 0.45 - 0.2, 0.14), bev=0.08)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 0.7), Hit=(0, 0.25, 0.9))
    return finish(a)


def dune_jerboa(row):
    """jerboa: a tiny round ball of a body perched high on two very long thin hind legs, big ROUND mouse ears,
    a super long thin tail arching up over its back with a black-and-white tuft above its head"""
    a = start(row, dict(main='#e8c48a', belly='#fff8e6', dark='#7a5636', accent='#c89a5c', ear_in='#ffb8b0'), 3.04)
    LEG = 0.9
    zb = LEG + 0.4
    sg('body', 'root', (0, 0.1, zb))
    B = b('body', (0.8, 0.8, 0.8), mm('main'), (0, 0.1, zb), bev=0.3)
    b('belly', (0.56, 0.1, 0.56), mm('belly'), (0, -0.3, zb - 0.06), bev=0.06)
    grid(B, 'k', 3, 2, mm('accent'), (0.1, 0.1), name='back_band', span=(0.6, 0.5))
    grid(B, 'l', 2, 2, mm('accent'), (0.08, 0.08), name='side_dot', span=(0.5, 0.5))
    grid(B, 'r', 2, 2, mm('accent'), (0.08, 0.08), name='side_dot', span=(0.5, 0.5))
    grid(B, 't', 2, 2, mm('dark'), (0.08, 0.08), name='top_dot', span=(0.5, 0.5))
    grid(B, 'u', 3, 3, mm('belly'), (0.08, 0.08), name='under_fur', span=(0.6, 0.6))
    for k_ in range(8):
        ang = math.radians(k_ * 45)
        p('fur_tuft', (0.1, 0.1, 0.1), mm('belly'), (math.cos(ang) * 0.42, 0.1 + math.sin(ang) * 0.42, zb - 0.2))
    accessory('necklace', Box((0, -0.1, zb + 0.3), (0.6, 0.6, 0.2)), '#e8782a', '#5ae8e0', z=zb + 0.26)
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.25, 0.2, zb - 0.3))
        a.legs.append(nm)
        b('thigh', (0.22, 0.36, 0.36), mm('main'), (sgn * 0.3, 0.25, zb - 0.32), bev=0.06)
        b('stilt', (0.08, 0.08, LEG - 0.1), mm('main'), (sgn * 0.3, 0.2, (LEG - 0.1) / 2 + 0.1), bev=0.02)
        p('ankle', (0.1, 0.1, 0.1), mm('accent'), (sgn * 0.3, 0.2, 0.5))
        for j in range(4):
            p('leg_band', (0.1, 0.1, 0.04), mm('accent' if j % 2 else 'dark'), (sgn * 0.3, 0.2, 0.2 + j * 0.16))
        b('long_foot', (0.14, 0.5, 0.08), mm('belly'), (sgn * 0.3, 0.04, 0.04), bev=0.02)
        for j in range(3):
            p('toe', (0.04, 0.06, 0.04), mm('dark'), (sgn * 0.3 + (j - 1) * 0.04, -0.22, 0.03))
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.16, -0.3, zb - 0.1))
        a.arms.append(nm)
        p('tiny_arm', (0.06, 0.06, 0.2), mm('main'), (sgn * 0.14, -0.36, zb - 0.22))
        p('tiny_paw', (0.07, 0.07, 0.06), mm('belly'), (sgn * 0.14, -0.38, zb - 0.34))
    sg('head', 'body', (0, -0.1, zb + 0.35))
    Hd = b('head', (0.66, 0.56, 0.54), mm('main'), (0, -0.2, zb + 0.6), bev=0.16)
    mz = muzzle(Hd, (0.26, 0.18, 0.18), -0.2, 'belly', nose=(0.1, 0.05, 0.07), nose_mat='pink')
    eyes(Hd, 0.42, 0.25, 0.1, iris='#3a2414', lash=True, brow=None)
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.24, Hd.front - 0.012, zb + 0.5))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.24, -0.2, Hd.top - 0.05))
        a.ears.append(nm)
        b('round_ear', (0.56, 0.1, 0.56), mm('main'), (sgn * 0.42, -0.15, Hd.top + 0.24), rot=(0, -sgn * 20, 0), bev=0.2)
        p('ear_in', (0.38, 0.04, 0.38), mm('ear_in'), (sgn * 0.42, -0.21, Hd.top + 0.24), rot=(0, -sgn * 20, 0))
        for j in range(3):
            p('whisker', (0.26, 0.02, 0.02), mm('dark'), (sgn * 0.3, Hd.front - 0.12, zb + 0.48 + (j - 1) * 0.04), rot=(0, sgn * (j - 1) * 10, 0))
    use('body')
    # super long tail arching up over the back (the silhouette)
    sg('tail', 'body', (0, 0.5, zb - 0.1))
    a.tail = ['tail']
    for j in range(12):
        th = math.radians(200 - j * 15)
        y = 0.9 + math.cos(th) * 0.8
        z = zb + 0.5 + math.sin(th) * 1.0
        p('tail', (0.07, 0.16, 0.16), mm('main'), (0, y, z), rot=(-math.degrees(th), 0, 0))
    p('tail_tuft_dark', (0.24, 0.28, 0.24), mm('dark'), (0, 0.9 + math.cos(math.radians(20)) * 0.8 - 0.3, zb + 0.5 + math.sin(math.radians(20)) * 1.0 + 0.6))
    p('tail_tuft', (0.3, 0.14, 0.3), mm('belly'), (0, 0.9 + math.cos(math.radians(20)) * 0.8 - 0.5, zb + 0.5 + math.sin(math.radians(20)) * 1.0 + 0.75))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.35, zb), Hit=(0, 0.1, zb + 0.3))
    return finish(a)


def dune_scorpion(row):
    a = start(row, dict(main='#e8a04a', belly='#f6d8a0', dark='#8a4a20', accent='#ffd84a', shell='#d8823a', **{'*glow': '#5ae8e0'}), 2.3)
    B, Hd = bug(bw=1.1, bl=1.4, bh=0.6, legh=0.34, hw=0.9, hd=0.5, hh=0.56, nleg=4, leg_w=0.11, leg_span=0.46, claws=0.5, antenna=0,
                head_z=0.0, leg_mat='dark', shell='main')
    use('head')
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.16))
        p('fang', (0.08, 0.1, 0.1), mm('dark'), (sgn * 0.12, Hd.front - 0.04, Hd.bot + 0.06))
    eyes(Hd, 0.44, 0.24, 0.1, iris='#2a8a84', glow='#5ae8e0', brow='#8a4a20', tilt=-12)
    use('body')
    # armour plates across the back (pattern)
    for j in range(5):
        b('plate', (B.s.x * (0.96 - 0.05 * j), 0.22, 0.12), mm('shell' if j % 2 else 'dark'), (0, B.front + 0.16 + j * 0.27, B.top + 0.14), bev=0.03)
        for sgn, n in LR:
            p('plate_stud', (0.1, 0.1, 0.05), mm('accent'), (sgn * 0.3, B.front + 0.16 + j * 0.27, B.top + 0.22))
    for sgn, n in LR:
        for j in range(3):
            p('side_plate', (0.05, 0.3, 0.24), mm('shell'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.36 + j * 0.36, B.c.z))
    # arched tail of shrinking segments with a glowing stinger (the silhouette)
    cur = Vector((0, B.back - 0.1, B.c.z + 0.1))
    par = 'body'
    a.tail = []
    pts = ((0.0, 0.32, 0.34), (0.0, 0.2, 0.46), (0.0, -0.06, 0.46), (0.0, -0.3, 0.3))
    for i, d in enumerate(pts):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        w = 0.34 - 0.04 * i
        c = cur + Vector(d) * 0.5
        b('tail_seg', (w, w, w), mm('main' if i % 2 == 0 else 'shell'), tuple(c), rot=(-30 * i, 0, 0), bev=0.07)
        p('tail_ring', (w + 0.03, w * 0.4, w + 0.03), mm('dark'), tuple(c), rot=(-30 * i, 0, 0))
        cur = cur + Vector(d)
        par = nm
    sg('glow', par, tuple(cur))
    a.glow.append('glow')
    b('sting_bulb', (0.34, 0.34, 0.34), mm('glow'), tuple(cur + Vector((0, -0.1, -0.06))), bev=0.09)
    cn('sting', 0.1, 0.34, mm('glow'), tuple(cur + Vector((0, -0.26, -0.12))), (0, -1, -0.5))
    p('sting_shine', (0.1, 0.1, 0.04), mm('white'), tuple(cur + Vector((0.06, -0.1, 0.12))))
    # rarity 4: glowing runes on the plates and claw gems, sparks
    use('body')
    sg('glow_b', 'body', tuple(B.c))
    a.glow.append('glow_b')
    for j in range(3):
        p('rune', (0.16, 0.16, 0.04), mm('glow'), (0, B.front + 0.16 + j * 0.54, B.top + 0.215), rot=(0, 0, 45))
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        p('claw_gem', (0.14, 0.14, 0.06), mm('glow'), (sgn * (B.s.x * 0.4 + 0.475), B.front - 0.275, B.c.z + 0.25), rot=(0, 0, 45))
        p('claw_tip', (0.1, 0.12, 0.08), mm('accent'), (sgn * (B.s.x * 0.4 + 0.575), B.front - 0.92, B.c.z + 0.07))
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        for j in range(3):
            p('claw_stud', (0.08, 0.08, 0.05), mm('accent'), (sgn * (B.s.x * 0.4 + 0.3 + 0.1 * j), B.front - 0.2 - 0.14 * j, B.c.z + 0.2))
    use('head')
    for sgn, n in LR:
        on(Hd, 't', sgn * 0.26, 0, (0.16, 0.2), mm('shell'), name='head_plate', th=0.05)
        p('cheek_stud', (0.08, 0.04, 0.08), mm('accent'), (sgn * 0.36, Hd.front - 0.02, Hd.c.z + 0.16), rot=(0, 45, 0))
    use('body')
    for sgn, n in LR:
        for j in range(4):
            p('rim_stud', (0.06, 0.08, 0.08), mm('accent'), (sgn * (B.s.x / 2 + 0.03), B.c.y - 0.5 + j * 0.34, B.c.z + 0.2))
    aura_kit(1.5, 4, motes=8, mote_col='glow', height=1.4)
    return finish(a)


def sand_wyrm(row):
    a = start(row, dict(main='#e8c070', belly='#fff0c0', dark='#a8742a', accent='#d89a3a', fin='#5ac8c0', horn='#fff6e0',
                        **{'*glow': '#5ae8e0', '*glow2': '#ffd21a'}), 4.3)
    B, Hd, necks = serp(w=0.86, n=4, seg_l=0.9, hw=1.24, hd=1.06, hh=1.0, rise=0.55, coil=True, ntail=3)
    mz = muzzle(Hd, (0.64, 0.3, 0.34), -0.24, 'belly', nose=None, mouth=True, fangs=1, tongue=True)
    for sgn, n in LR:
        p('nostril', (0.07, 0.03, 0.05), mm('line'), (sgn * 0.14, mz.front - 0.008, mz.c.z + 0.1))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.46, Hd.front - 0.012, Hd.c.z - 0.2))
        # side frill fins
        b('frill', (0.14, 0.5, 0.6), mm('fin'), (sgn * (Hd.s.x / 2 + 0.05), Hd.back - 0.1, Hd.c.z), rot=(0, 0, sgn * 20), bev=0.05)
        for j in range(3):
            p('frill_ray', (0.16, 0.5, 0.05), mm('dark'), (sgn * (Hd.s.x / 2 + 0.06), Hd.back - 0.1, Hd.c.z - 0.2 + j * 0.2), rot=(0, 0, sgn * 20))
        cn('horn', 0.1, 0.4, mm('horn'), (sgn * 0.36, Hd.c.y + 0.1, Hd.top - 0.02), (sgn * 0.3, 0.3, 1))
    eyes(Hd, 0.33, 0.26, 0.12, iris='#2a8a84', glow='#5ae8e0', brow='#a8742a', tilt=-8)
    use('head')
    for i in range(3):
        b('crest', (0.16, 0.24, 0.3 - 0.05 * i), mm('fin'), (0, Hd.c.y - 0.2 + i * 0.28, Hd.top + 0.12), bev=0.04)
    # armour bands and dorsal fins on every neck / tail segment (pattern)
    for i, (nm, nb) in enumerate(zip(a.neck, necks)):
        use(nm)
        p('band', (nb.s.x + 0.04, nb.s.y + 0.04, 0.12), mm('dark'), (0, nb.c.y, nb.c.z + 0.2), rot=(12, 0, 0))
        p('band', (nb.s.x + 0.04, nb.s.y + 0.04, 0.08), mm('accent'), (0, nb.c.y + 0.03, nb.c.z - 0.16), rot=(12, 0, 0))
        b('dorsal', (0.14, 0.3, 0.36), mm('fin'), (0, nb.back + 0.12, nb.c.z + 0.06), rot=(12, 0, 0), bev=0.04)
        for sgn, n in LR:
            p('scale', (0.04, 0.24, 0.24), mm('accent'), (sgn * (nb.s.x / 2 + 0.01), nb.c.y, nb.c.z), rot=(12, 0, 0))
            p('scale', (0.04, 0.16, 0.16), mm('dark'), (sgn * (nb.s.x / 2 + 0.012), nb.c.y + 0.1, nb.c.z - 0.26), rot=(12, 0, 0))
            p('scale', (0.04, 0.16, 0.16), mm('belly'), (sgn * (nb.s.x / 2 + 0.012), nb.c.y - 0.1, nb.c.z + 0.28), rot=(12, 0, 0))
            cn('side_spike', 0.07, 0.24, mm('horn'), (sgn * (nb.s.x / 2 - 0.02), nb.back - 0.06, nb.c.z + 0.2), (sgn * 1, 0.6, 0.3))
    use('body')
    for i in range(4):
        p('body_band', (B.s.x + 0.04, 0.12, B.s.z + 0.04), mm('dark' if i % 2 else 'accent'), (0, B.front + 0.2 + i * 0.36, B.c.z))
    for sgn, n in LR:
        for i in range(3):
            p('body_scale', (0.04, 0.26, 0.3), mm('accent'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.4 + i * 0.4, B.c.z + 0.05))
            cn('body_spike', 0.09, 0.3, mm('horn'), (sgn * 0.4, B.c.y - 0.4 + i * 0.4, B.top - 0.02), (sgn * 0.5, 0.2, 1))
    for i in range(4):
        b('body_fin', (0.14, 0.26, 0.3), mm('fin'), (0, B.front + 0.24 + i * 0.36, B.top + 0.12), bev=0.04)
    use('head')
    for sgn, n in LR:
        for j in range(3):
            p('tooth', (0.07, 0.04, 0.08), mm('white'), (sgn * (0.08 + 0.1 * j), mz.front - 0.006, mz.bot + 0.03))
        b('barbel', (0.06, 0.06, 0.34), mm('fin'), (sgn * 0.36, mz.front + 0.04, mz.bot - 0.14), rot=(0, sgn * 16, 0), bev=0.02)
        p('barbel_tip', (0.1, 0.1, 0.1), mm('glow'), (sgn * 0.41, mz.front + 0.04, mz.bot - 0.34))
    use('body')
    for i, t in enumerate(a.tail):
        use(t)
        j = a.joint[t]
        b('tail_fin', (0.12, 0.3, 0.3 - 0.06 * i), mm('fin'), (j.x, j.y + 0.4, j.z + 0.5 - 0.08 * i), bev=0.04)
        p('tail_band', (0.86 * (0.8 - 0.2 * i) + 0.04, 0.12, 0.86 * (0.8 - 0.2 * i) * 0.9 + 0.04), mm('dark'), (j.x, j.y + 0.45, 0.86 * (0.8 - 0.2 * i) * 0.45))
        p('tail_band', (0.86 * (0.8 - 0.2 * i) + 0.04, 0.08, 0.86 * (0.8 - 0.2 * i) * 0.9 + 0.04), mm('accent'), (j.x, j.y + 0.2, 0.86 * (0.8 - 0.2 * i) * 0.45))
        for sgn, n in LR:
            p('tail_scale', (0.04, 0.2, 0.2), mm('accent'), (j.x + sgn * (0.43 * (0.8 - 0.2 * i) + 0.01), j.y + 0.62, 0.86 * (0.8 - 0.2 * i) * 0.45))
    use(a.tail[-1])
    te = a.tail_end
    b('tail_club', (0.4, 0.4, 0.4), mm('fin'), (te[0], te[1] + 0.1, 0.24), rot=(0, 0, 45), bev=0.08)
    # rarity 5: glowing belly plates up the neck, glowing frill tips, orbiting mirage gems, yellow aura
    for i, (nm, nb) in enumerate(zip(a.neck, necks)):
        gname = 'glow' if i == 0 else 'glow%d' % (i + 1)
        sg(gname, nm, tuple(nb.c))
        a.glow.append(gname)
        p('belly_glow', (nb.s.x * 0.5, 0.05, 0.2), mm('glow'), (0, nb.front - 0.03, nb.c.z + 0.16), rot=(12, 0, 0))
        p('belly_glow', (nb.s.x * 0.36, 0.05, 0.12), mm('glow2'), (0, nb.front - 0.03, nb.c.z - 0.14), rot=(12, 0, 0))
        for sgn, n in LR:
            p('side_gem', (0.05, 0.14, 0.14), mm('glow'), (sgn * (nb.s.x / 2 + 0.03), nb.c.y, nb.c.z + 0.14), rot=(45, 0, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(3):
        p('crest_glow', (0.1, 0.12, 0.1), mm('glow'), (0, Hd.c.y - 0.2 + i * 0.28, Hd.top + 0.3 - 0.03 * i))
    on(Hd, 'f', 0, 0.36, (0.16, 0.16), mm('glow2'), th=0.035, name='fore_gem', rot=(0, 45, 0))
    for sgn, n in LR:
        p('frill_glow', (0.16, 0.12, 0.62), mm('glow'), (sgn * (Hd.s.x / 2 + 0.07), Hd.back + 0.16, Hd.c.z), rot=(0, 0, sgn * 20))
    use('body')
    orbit_kit((0, 0.2, 2.0), 1.6, 6, 'glow', 'glow2', size=0.14, dz=0.6, shape='cross')
    aura_kit(1.9, 5, motes=10, mote_col='glow', height=2.6, style='petals')
    return finish(a)


def mirage_camel(row):
    a = start(row, dict(main='#f0cc8a', belly='#fff2d0', dark='#a87a42', accent='#d8a45c', cloth='#3fb8c8', cloth2='#ff7ab0',
                        **{'*glow': '#5ae8e0', '*glow2': '#ff8ad0', '*gold': '#ffd84a'}), 4.6)
    B, Hd = quad(bw=0.98, bl=1.5, bh=0.84, legh=1.06, lw=0.22, hw=1.0, hd=0.9, hh=0.9, neck=0.9, toe='dark', head_fwd=0.4, leg_fl=0.34, ntoe=2)
    mz = muzzle(Hd, (0.5, 0.4, 0.36), -0.24, 'belly', nose=None, mouth=True)
    b('lip', (0.42, 0.12, 0.14), mm('accent'), (0, mz.front - 0.03, mz.bot + 0.06), bev=0.04)
    for sgn, n in LR:
        p('nostril', (0.07, 0.03, 0.05), mm('line'), (sgn * 0.1, mz.front - 0.008, mz.c.z + 0.1))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.2))
    eyes(Hd, 0.36, 0.25, 0.14, iris='#2a8a84', glow='#5ae8e0', lash=True, brow='#a87a42', tilt=8, sleepy=0.14)
    ears(Hd, 'round', 'main', 'pink', x=0.46, h=0.2, w=0.2, lean=40)
    use('head')
    for i in range(3):
        b('head_tuft', (0.22, 0.2, 0.18), mm('dark'), ((i - 1) * 0.2, Hd.c.y + 0.06, Hd.top + 0.08), bev=0.05)
    use('body')
    # two humps (the silhouette), shaggy neck, knee pads
    for j, y in enumerate((B.c.y - 0.34, B.c.y + 0.38)):
        b('hump', (0.76, 0.56, 0.5), mm('main'), (0, y, B.top + 0.22), bev=0.12)
        b('hump_top', (0.5, 0.36, 0.26), mm('accent'), (0, y, B.top + 0.56), bev=0.1)
        p('hump_tuft', (0.2, 0.2, 0.12), mm('dark'), (0, y, B.top + 0.72))
    nk = Box((0, B.front + 0.2, 1.06 + 0.84 * 0.85 + 0.45), (0.98 * 0.6, 0.98 * 0.6, 0.9 + 0.84 * 0.3))
    for j in range(4):
        p('neck_fur', (0.3, 0.14, 0.2), mm('dark'), (0, nk.front - 0.04, nk.c.z + 0.4 - j * 0.26))
        for sgn, n in LR:
            p('neck_patch', (0.04, 0.2, 0.16), mm('accent'), (sgn * (nk.s.x / 2 + 0.01), nk.c.y, nk.c.z + 0.36 - j * 0.24))
    fluff(a.bx['chest'], 'f', mm('dark'), 3, 0.9, 0.3, th=0.07)
    # saddle cloth with tassels and gems between the humps
    b('saddle', (B.s.x + 0.1, 0.44, 0.1), mm('cloth'), (0, B.c.y + 0.02, B.top + 0.06), bev=0.03)
    for sgn, n in LR:
        b('saddle_side', (0.08, 0.5, 0.5), mm('cloth'), (sgn * (B.s.x / 2 + 0.05), B.c.y + 0.02, B.top - 0.22), bev=0.03)
        p('saddle_trim', (0.1, 0.54, 0.08), mm('gold'), (sgn * (B.s.x / 2 + 0.055), B.c.y + 0.02, B.top - 0.48))
        for j in range(3):
            p('tassel', (0.06, 0.08, 0.16), mm('cloth2'), (sgn * (B.s.x / 2 + 0.055), B.c.y - 0.18 + j * 0.2, B.top - 0.6))
        for j in range(2):
            p('saddle_star', (0.1, 0.14, 0.14), mm('cloth2'), (sgn * (B.s.x / 2 + 0.06), B.c.y - 0.1 + j * 0.24, B.top - 0.2), rot=(45, 0, 0))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('knee_pad', (ft.s.x + 0.04, ft.s.y * 0.7, 0.12), mm('dark'), (ft.c.x, ft.c.y + 0.05, 0.6))
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.06), mm('accent'), (ft.c.x, ft.c.y + 0.05, 0.86))
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.05), mm('accent'), (ft.c.x, ft.c.y + 0.05, 0.36))
        p('ankle', (ft.s.x + 0.03, ft.s.y * 0.8, 0.06), mm('gold'), (ft.c.x, ft.c.y + 0.03, ft.top + 0.06))
        p('foot_glow', (ft.s.x + 0.04, ft.s.y + 0.04, 0.035), mm('glow'), (ft.c.x, ft.c.y, ft.top + 0.01))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)
    # rarity 6: mirage shimmer gems, glowing hump crystals, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for j, y in enumerate((B.c.y - 0.34, B.c.y + 0.38)):
        cn('hump_crystal', 0.12, 0.44, mm('glow' if j == 0 else 'glow2'), (0, y, B.top + 0.74), (0, 0.1, 1))
        for sgn, n in LR:
            cn('hump_crystal', 0.08, 0.28, mm('glow2' if j == 0 else 'glow'), (sgn * 0.2, y, B.top + 0.62), (sgn * 0.5, 0, 1))
    for sgn, n in LR:
        f = 'l' if sgn < 0 else 'r'
        for i in range(3):
            on(B, f, -0.34 + i * 0.34, -0.3, (0.14, 0.14), mm('glow' if i % 2 else 'glow2'), th=0.035, name='flank_gem', rot=(45, 0, 0))
        on(a.bx['rump'], f, 0, 0.14, (0.2, 0.2), mm('glow'), th=0.035, name='flank_gem', rot=(45, 0, 0))
        p('saddle_gem', (0.12, 0.16, 0.16), mm('glow'), (sgn * (B.s.x / 2 + 0.07), B.c.y + 0.02, B.top - 0.34), rot=(45, 0, 0))
    for j in range(3):
        p('neck_gem', (0.14, 0.06, 0.14), mm('glow'), (0, nk.front - 0.13, nk.c.z + 0.27 - j * 0.26), rot=(0, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    on(Hd, 'f', 0, 0.38, (0.16, 0.16), mm('glow2'), th=0.035, name='fore_gem', rot=(0, 45, 0))
    for sgn, n in LR:
        on(Hd, 'f', sgn * 0.4, -0.3, (0.08, 0.08), mm('glow'), th=0.035, name='cheek_gem', rot=(0, 45, 0))
        p('ear_gem', (0.08, 0.08, 0.08), mm('glow2'), (sgn * (0.46 * Hd.s.x + 0.14), Hd.c.y, Hd.top + 0.02), rot=(45, 45, 0))
    halo_kit(Hd, 'gold', r=0.5, n=10, dz=0.8, kind='stars')
    use('body')
    orbit_kit((0, 0.2, 2.3), 1.4, 6, 'glow', 'glow2', size=0.13, dz=0.5, shape='star')
    orbit_kit((0, 0.2, 1.4), 1.6, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.2, shape='ring')
    aura_kit(1.5, 6, motes=12, mote_col='glow', mote_r=1.6, height=3.0, style='double')
    return finish(a)


ANIMALS = dict(oasis_scarab=oasis_scarab, fennec=fennec, dune_jerboa=dune_jerboa, dune_scorpion=dune_scorpion, sand_wyrm=sand_wyrm,
               mirage_camel=mirage_camel)
