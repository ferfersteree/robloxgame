# Biome 3 - Wild Marsh: bog, snags, glowing mushrooms, mossy ruins
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 3
GROUND = '#6a9a58'
SKY = '#c2d2b8'
THEME = dict(bits=['#7aaa3e', '#8a6a44'], dust='#b9b08a', glow='#5affd0', splash='#9ad8c8', bit_name='камыш и тина')
BUSH_NAME = 'болотная кочка с камышом, рогозом, корягой, мшистыми камнями и светящимися грибами'


def bush():
    B = begin_bush(NN)
    moss = mat('moss', '#5f9a3e')
    moss2 = mat('moss2', '#7ab84a')
    mud = mat('mud', '#7a6244')
    reed = mat('reed', '#8fbf4a')
    reed2 = mat('reed2', '#6a9a36')
    cat = mat('cattail', '#7a4a2a')
    wood = mat('wood', '#8a6a4c')
    wood2 = mat('wood2', '#6a4e36')
    stone = mat('stone', '#9aa29a')
    water = mat('water', '#5ab8b0')
    lily = mat('lily', '#4fae5a')
    petal = mat('petal', '#ffd0e6')
    shroom = mat('shroom', '#5affd0', 'neon', 2.4)
    stemm = mat('stem', '#e8f4e0')
    # the tussock: stacked mounds
    part('big', (0, 0.3, 0.3), 'mound')
    b('mound', (5.2, 3.0, 1.0), mud, (0, 0.3, 0.5), bev=0.12)
    b('mound_moss', (4.8, 2.7, 0.3), moss, (0, 0.3, 1.1), bev=0.08)
    for i, (x, y) in enumerate(((-1.9, -0.9), (1.7, -1.0), (0.2, -1.25), (-0.6, 1.3), (2.0, 1.1))):
        p('drip', (0.5, 0.12, 0.4), moss, (x, 0.3 + y * 1.0 - (0.07 if y < 0 else -0.07), 0.82))
    part('big', (-0.6, 0.5, 1.2), 'hump_a')
    b('hump', (2.6, 2.0, 1.1), moss, (-0.7, 0.5, 1.7), bev=0.12)
    b('hump_top', (1.7, 1.3, 0.5), moss2, (-0.8, 0.5, 2.4), bev=0.1)
    spots_ = ((-1.5, -0.52, 1.7), (-0.2, -0.52, 2.0), (-0.9, -0.52, 1.4))
    for x, y, z in spots_:
        p('moss_patch', (0.4, 0.06, 0.3), moss2, (x, y, z))
    part('big', (1.4, 0.4, 1.2), 'hump_b')
    b('hump', (2.0, 1.8, 0.8), moss2, (1.5, 0.4, 1.55), bev=0.12)
    b('hump_top', (1.2, 1.1, 0.4), moss, (1.6, 0.4, 2.1), bev=0.08)
    # reeds: tall stalks in clumps
    k_ = 0
    for (cx, cy, n, h0) in ((-2.9, 0.4, 4, 2.7), (-1.6, 1.3, 3, 3.3), (0.3, 1.4, 4, 3.7), (2.3, 1.0, 3, 2.9), (3.1, -0.1, 3, 2.2), (-0.2, 0.7, 3, 3.5)):
        part('small', (cx, cy, 0.9), 'reeds_%d' % k_)
        for i in range(n):
            x = cx + (i - (n - 1) / 2) * 0.3
            y = cy + (0.15 if i % 2 else -0.1)
            h = h0 - 0.5 * (i % 3)
            lean = (i - (n - 1) / 2) * 5
            b('reed', (0.14, 0.14, h), reed if i % 2 else reed2, (x + math.sin(math.radians(lean)) * h / 2, y, 0.9 + h / 2), rot=(0, lean, 0), bev=0.03)
            p('reed_leaf', (0.5, 0.06, 0.12), reed2, (x + 0.28 * (1 if i % 2 else -1), y, 0.9 + h * 0.5), rot=(0, 35 * (1 if i % 2 else -1), 0))
            p('reed_leaf', (0.4, 0.06, 0.1), reed, (x - 0.22 * (1 if i % 2 else -1), y, 0.9 + h * 0.7), rot=(0, -40 * (1 if i % 2 else -1), 0))
        k_ += 1
    # cattails
    for i, (x, y, h) in enumerate(((-2.3, -0.6, 2.3), (-1.2, 0.0, 2.9), (1.0, 0.9, 3.1), (2.7, 0.5, 2.4), (0.9, -0.5, 1.9))):
        part('small', (x, y, 0.9), 'cattail_%d' % i)
        b('stalk', (0.1, 0.1, h), reed2, (x, y, 0.9 + h / 2), bev=0.02)
        b('head', (0.26, 0.26, 0.7), cat, (x, y, 0.9 + h + 0.1), bev=0.07)
        p('tip', (0.07, 0.07, 0.3), reed, (x, y, 0.9 + h + 0.6))
        p('leaf', (0.6, 0.06, 0.12), reed, (x + 0.3, y, 0.9 + h * 0.35), rot=(0, 30, 0))
    # snag (driftwood) leaning over the front
    part('big', (2.4, -0.9, 0.5), 'snag')
    b('snag', (0.5, 0.5, 2.4), wood, (2.5, -0.9, 1.5), rot=(0, 18, 0), bev=0.08)
    b('snag_branch', (1.1, 0.3, 0.3), wood, (2.2, -0.9, 2.3), rot=(0, 30, 0), bev=0.06)
    b('snag_branch', (0.3, 0.3, 0.9), wood2, (3.1, -0.9, 2.5), rot=(0, 40, 0), bev=0.06)
    p('snag_knot', (0.2, 0.06, 0.3), wood2, (2.55, -1.17, 1.3), rot=(0, 18, 0))
    p('snag_ring', (0.56, 0.56, 0.12), wood2, (2.3, -0.9, 0.8), rot=(0, 18, 0))
    for i in range(3):
        p('snag_moss', (0.3, 0.3, 0.1), moss2, (2.6 + i * 0.1, -0.9, 2.74 - i * 0.02), rot=(0, 18, 0))
    # mossy ruin stones with runes
    for i, (x, y, w, h) in enumerate(((-2.6, -1.0, 1.1, 1.5), (-1.5, -1.3, 0.8, 0.9))):
        part('big', (x, y, 0.2), 'ruin_%d' % i)
        b('ruin', (w, 0.7, h), stone, (x, y, h / 2 + 0.1), rot=(0, -6 + 10 * i, 8 * i), bev=0.08)
        p('ruin_moss', (w * 0.8, 0.74, 0.14), moss, (x, y, h + 0.1), rot=(0, -6 + 10 * i, 8 * i))
        p('ruin_crack', (0.05, 0.03, h * 0.5), mat('stone2', '#6e766e'), (x + 0.2, y - 0.365, h * 0.5))
        p('ruin_rune', (w * 0.4, 0.03, 0.12), mat('stone2', '#6e766e'), (x - 0.1, y - 0.365, h * 0.75))
        p('ruin_rune', (0.12, 0.03, w * 0.4), mat('stone2', '#6e766e'), (x - 0.1, y - 0.365, h * 0.6))
    # glowing mushrooms
    for i, (x, y, z, s) in enumerate(((-0.3, -1.25, 0.25, 1.0), (0.3, -1.4, 0.2, 0.7), (1.4, -1.2, 0.3, 0.9), (-2.0, 1.3, 1.2, 0.8), (0.8, -0.6, 1.25, 0.8))):
        part('small', (x, y, z), 'shroom_%d' % i)
        b('stem', (0.18 * s, 0.18 * s, 0.5 * s), stemm, (x, y, z + 0.25 * s), bev=0.03)
        b('cap', (0.6 * s, 0.6 * s, 0.24 * s), shroom, (x, y, z + 0.58 * s), bev=0.07)
        p('cap_top', (0.32 * s, 0.32 * s, 0.1 * s), shroom, (x, y, z + 0.74 * s))
        p('cap_dot', (0.1 * s, 0.1 * s, 0.03), stemm, (x + 0.12 * s, y - 0.1 * s, z + 0.705 * s))
    # puddle with a lily
    part('big', (0.6, -1.9, 0.02), 'puddle')
    b('puddle', (2.4, 1.0, 0.08), water, (0.6, -1.85, 0.04), bev=0.03)
    p('puddle_shine', (0.6, 0.2, 0.02), mat('shine', '#c8f4f0'), (0.2, -1.9, 0.09))
    part('small', (1.2, -1.9, 0.1), 'lily')
    b('lily_pad', (0.6, 0.6, 0.06), lily, (1.2, -1.9, 0.12), bev=0.03)
    p('lily_cut', (0.2, 0.3, 0.07), water, (1.2, -2.1, 0.12))
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        p('lily_petal', (0.16, 0.16, 0.12), petal, (1.2 + math.cos(ang) * 0.12, -1.85 + math.sin(ang) * 0.12, 0.22))
    p('lily_core', (0.1, 0.1, 0.12), mat('core', '#ffd84a'), (1.2, -1.85, 0.26))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def deer(row):
    """a resting deer lying down: belly on the ground, all four legs folded under, neck up, head tilted, white spots, two little prong antlers"""
    a = start(row, dict(main='#b8743a', belly='#fff2dc', dark='#5a3418', accent='#e8c48a', antler='#f0e0c0'), 2.19)
    sg('body', 'root', (0, 0.3, 0.4))
    B = b('body', (1.0, 1.7, 0.7), mm('main'), (0, 0.4, 0.38), bev=0.2)
    b('belly', (0.8, 1.4, 0.1), mm('belly'), (0, 0.4, 0.06), bev=0.04)
    grid(B, 't', 3, 5, mm('belly'), (0.1, 0.1), name='spot', span=(0.7, 0.8))
    grid(B, 'l', 4, 1, mm('belly'), (0.08, 0.08), name='spot', span=(0.8, 0.1))
    grid(B, 'r', 4, 1, mm('belly'), (0.08, 0.08), name='spot', span=(0.8, 0.1))
    for fy, tag in ((-0.25, 'f'), (0.95, 'b')):
        for sgn, n in LR:
            nm = 'leg_%s%s' % (tag, n)
            sg(nm, 'body', (sgn * 0.4, fy, 0.25))
            a.legs.append(nm)
            b('folded_leg', (0.24, 0.6, 0.18), mm('main'), (sgn * 0.5, fy - 0.2, 0.1), rot=(0, 0, sgn * (10 if tag == 'f' else -20)), bev=0.04)
            p('hoof', (0.16, 0.14, 0.12), mm('dark'), (sgn * 0.5 - sgn * 0.04, fy - 0.52, 0.07))
    sg('neck', 'body', (0, -0.3, 0.6))
    b('neck', (0.4, 0.4, 0.8), mm('main'), (0, -0.4, 0.95), rot=(-15, 0, 0), bev=0.08)
    p('neck_front', (0.26, 0.06, 0.6), mm('belly'), (0, -0.62, 0.95), rot=(-15, 0, 0))
    sg('head', 'neck', (0, -0.5, 1.3))
    Hd = b('head', (0.72, 0.66, 0.6), mm('main'), (0, -0.6, 1.55), rot=(0, 12, 0), bev=0.14)
    mz = muzzle(Hd, (0.34, 0.26, 0.24), -0.26, 'belly', nose=(0.12, 0.07, 0.08))
    eyes(Hd, 0.32, 0.25, 0.1, iris='#3a2414', lash=True, brow=None, sleepy=0.25)
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.24, Hd.front - 0.012, 1.45))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.34, -0.6, Hd.top - 0.1))
        a.ears.append(nm)
        b('ear', (0.34, 0.1, 0.18), mm('main'), (sgn * 0.5, -0.6, Hd.top - 0.04), rot=(0, sgn * -25, 0), bev=0.03)
        p('ear_in', (0.22, 0.03, 0.1), mm('pink'), (sgn * 0.5, -0.66, Hd.top - 0.04), rot=(0, sgn * -25, 0))
        p('antler', (0.07, 0.07, 0.3), mm('antler'), (sgn * 0.16, -0.55, Hd.top + 0.15))
        p('antler_prong', (0.06, 0.06, 0.16), mm('antler'), (sgn * 0.22, -0.6, Hd.top + 0.26), rot=(0, sgn * 30, 0))
    use('body')
    grid(B, 'k', 2, 2, mm('belly'), (0.1, 0.1), name='rump_spot', span=(0.5, 0.5))
    use('head')
    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='head_spot', span=(0.4, 0.4))
    use('body')
    tail_kit('pom', 'body', (0, 1.25, 0.5), 'main', 'belly', size=0.18)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.6, 0.8), Hit=(0, 0.4, 0.7))
    return finish(a)


def moose(row):
    a = start(row, dict(main='#6e4a34', belly='#8e6a50', dark='#3e2a20', accent='#c8a884', horn='#ecd9b0', snout='#553a2c'), 3.57)
    B, Hd = quad(bw=1.0, bl=1.5, bh=0.9, legh=0.86, lw=0.24, hw=1.06, hd=0.98, hh=0.96, neck=0.1, hump=0.24, hoof='dark',
                 leg_mat='accent', head_fwd=0.34)
    # big droopy snout + bell (dewlap)
    mz = muzzle(Hd, (0.62, 0.42, 0.44), -0.3, 'snout', nose=None, mouth=True)
    b('snout_tip', (0.5, 0.14, 0.26), mm('snout'), (0, mz.front - 0.05, mz.c.z - 0.12), bev=0.05)
    for sgn, n in LR:
        p('nostril', (0.1, 0.03, 0.08), mm('line'), (sgn * 0.13, mz.front - 0.13, mz.c.z - 0.06))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.42, Hd.front - 0.012, Hd.c.z - 0.2))
    b('bell', (0.2, 0.2, 0.36), mm('main'), (0, Hd.front + 0.24, Hd.bot - 0.14), bev=0.05)
    p('bell_tip', (0.12, 0.12, 0.14), mm('dark'), (0, Hd.front + 0.24, Hd.bot - 0.36))
    eyes(Hd, 0.3, 0.27, 0.2, iris='#4a2a16', brow='#3e2a20', tilt=6, sleepy=0.12)
    ears(Hd, 'point', 'main', 'pink', tip='dark', x=0.5, h=0.3, w=0.22, lean=55)
    # palmate antlers: wide flat plates with finger tines (the silhouette)
    use('head')
    for sgn, n in LR:
        x0 = sgn * 0.3
        b('antler_beam', (0.5, 0.14, 0.14), mm('horn'), (x0 + sgn * 0.3, Hd.c.y, Hd.top + 0.14), rot=(0, -sgn * 20, 0), bev=0.03)
        b('antler_palm', (0.7, 0.14, 0.42), mm('horn'), (x0 + sgn * 0.85, Hd.c.y, Hd.top + 0.44), rot=(0, -sgn * 20, 0), bev=0.05)
        for j in range(4):
            b('antler_tine', (0.12, 0.13, 0.3), mm('horn'), (x0 + sgn * (0.55 + j * 0.22), Hd.c.y, Hd.top + 0.74 + j * 0.07), rot=(0, sgn * (6 + j * 8), 0), bev=0.03)
        p('antler_tine_f', (0.12, 0.26, 0.1), mm('horn'), (x0 + sgn * 0.6, Hd.c.y - 0.18, Hd.top + 0.3))
        p('antler_shade', (0.5, 0.03, 0.2), mm('accent'), (x0 + sgn * 0.85, Hd.c.y - 0.075, Hd.top + 0.42), rot=(0, -sgn * 20, 0))
    use('body')
    fluff(a.bx['chest'], 'f', mm('dark'), 3, 0.9, 0.34)
    spots(B, 'lr', 4, mm('dark'), 0.2, seed=2, name='shade')
    spots(a.bx['rump'], 'lr', 4, mm('belly'), 0.16, seed=5, name='patch')
    on(a.bx['hump'], 't', 0, 0, (0.5, 0.4), mm('dark'), name='hump_fur', th=0.08)
    for j in range(3):
        p('hump_tuft', (0.2, 0.16, 0.14), mm('dark'), (0, B.front + 0.2 + j * 0.2, B.top + 0.3 - 0.04 * j))
    for ft in a.bx['feet']:
        p('knee', (ft.s.x - 0.02, ft.s.y - 0.06, 0.1), mm('belly'), (ft.c.x, ft.c.y + 0.03, 0.52))
    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.22)
    return finish(a)


def bear(row):
    a = start(row, dict(main='#9a6238', belly='#e0b88a', dark='#5e3a20', accent='#f6dcb4'), 2.15)
    B, Hd = quad(bw=1.22, bl=1.42, bh=1.0, legh=0.4, lw=0.37, hw=1.28, hd=1.02, hh=1.02, head_up=0.48, hump=0.14, toe='accent',
                 leg_fl=0.56, ntoe=4)
    mz = muzzle(Hd, (0.58, 0.3, 0.38), -0.25, 'belly', nose=(0.22, 0.1, 0.14), top=None, tongue=True)
    cheeks(Hd, 'main', (0.26, 0.24, 0.3), -0.2, whisk=0, tuft=True)
    eyes(Hd, 0.3, 0.24, 0.14, iris='#4a2a16', brow='#5e3a20', tilt=8)
    ears(Hd, 'round', 'main', 'belly', x=0.4, h=0.3, w=0.34, lean=6)
    use('body')
    # chest crescent + accessory (rarity 3): flower wreath round the neck, honey drips, pattern on the back
    ch = a.bx['chest']
    on(ch, 'f', 0, 0.22, (0.6, 0.12), mm('accent'), name='crescent', th=0.05)
    on(ch, 'f', -0.3, 0.32, (0.14, 0.14), mm('accent'), name='crescent', th=0.05)
    on(ch, 'f', 0.3, 0.32, (0.14, 0.14), mm('accent'), name='crescent', th=0.05)
    stripes(B, 'lr', 3, mm('dark'), 0.12, name='fur_streak', span=0.8)
    spots(B, 't', 4, mm('dark'), 0.2, seed=4, name='back_patch')
    spots(a.bx['rump'], 'lr', 4, mm('belly'), 0.16, seed=6, name='patch')
    setm('fl1', '#ff7fb0')
    setm('fl2', '#ffe14a')
    setm('fl3', '#ffffff')
    setm('leaf', '#5bbb36')
    for i in range(9):
        ang = math.radians(i * 40)
        cx, cy = math.cos(ang) * 0.62, B.front + 0.3 + math.sin(ang) * 0.42
        z = B.top + 0.2 + 0.12 - 0.1 * math.sin(ang)
        p('wreath_leaf', (0.26, 0.2, 0.08), mm('leaf'), (cx, cy, z - 0.04), rot=(0, 0, math.degrees(ang)))
        p('wreath_flower', (0.16, 0.16, 0.12), mm(('fl1', 'fl2', 'fl3')[i % 3]), (cx, cy, z + 0.04), rot=(0, 0, 45))
        p('wreath_core', (0.07, 0.07, 0.06), mm('fl2' if i % 3 != 1 else 'fl1'), (cx, cy, z + 0.12))
    for ft in a.bx['feet']:
        p('pad', (ft.s.x * 0.6, 0.03, 0.06), mm('dark'), (ft.c.x, ft.back + 0.012, 0.06))
        p('elbow_tuft', (0.1, 0.12, 0.14), mm('dark'), (ft.c.x, ft.back + 0.1, 0.36))
        p('leg_patch', (ft.s.x - 0.04, 0.03, 0.14), mm('belly'), (ft.c.x, ft.front + 0.07, 0.3))
    use('head')
    for sgn, n in LR:
        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.2, mz.front - 0.008, mz.c.z + 0.06))
        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.14, mz.front - 0.008, mz.c.z - 0.02))
    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.26)
    return finish(a)


def bison(row):
    """swamp bison: front-heavy wedge - a giant golden shaggy mane cloak over the front half with the face peeking out low,
    slim charcoal hindquarters, wide crescent horns sweeping sideways"""
    a = start(row, dict(main='#3a3438', belly='#5a5258', dark='#24202a', accent='#e0a85a', mane='#d8963a', mane2='#f0c070', horn='#f6ecd8',
                        **{'*glow': '#5affd0'}), 2.12)
    B, Hd = quad(bw=1.0, bl=1.5, bh=0.8, legh=0.48, lw=0.26, hw=1.0, hd=0.9, hh=0.86, head_up=0.06, hoof='dark', leg_mat='dark',
                 head_mat='main', head_fwd=0.5, rump=True, chest=False)
    use('body')
    # the mane cloak: a big stepped block hugging the front half of the body, taller than the head (the silhouette)
    b('mane', (1.6, 0.9, 1.5), mm('mane'), (0, B.front + 0.3, B.c.z + 0.3), bev=0.16)
    b('mane_top', (1.2, 0.7, 0.4), mm('mane2'), (0, B.front + 0.34, B.c.z + 1.16), bev=0.12)
    for sgn, n in LR:
        for j in range(4):
            b('mane_lock', (0.16, 0.3, 0.5 - 0.06 * j), mm('mane' if j % 2 else 'mane2'), (sgn * 0.82, B.front + 0.0 + j * 0.2, B.c.z - 0.1 - 0.12 * j), bev=0.04)
    for i in range(5):
        b('mane_fringe', (0.28, 0.14, 0.34 + 0.08 * (i % 2)), mm('mane2'), ((i - 2) * 0.3, B.front - 0.16, B.c.z - 0.36), bev=0.04)
    grid(Box((0, B.front + 0.3, B.c.z + 0.3), (1.6, 0.9, 1.5)), 'l', 3, 3, mm('mane2'), (0.14, 0.14), name='mane_tuft', th=0.06)
    grid(Box((0, B.front + 0.3, B.c.z + 0.3), (1.6, 0.9, 1.5)), 'r', 3, 3, mm('mane2'), (0.14, 0.14), name='mane_tuft', th=0.06)
    # slim dark hindquarters with a light saddle line
    p('saddle_line', (0.2, 0.8, 0.04), mm('belly'), (0, B.back - 0.4, B.top + 0.01))
    grid(a.bx['rump'], 'k', 2, 2, mm('belly'), (0.12, 0.12), name='rump_spot')
    grid(B, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='flank_spot', span=(0.4, 0.5), offset=0.0)
    grid(B, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='flank_spot', span=(0.4, 0.5), offset=0.0)
    grid(Box((0, B.front + 0.3, B.c.z + 0.3), (1.6, 0.9, 1.5)), 't', 3, 2, mm('mane2'), (0.16, 0.16), name='mane_top_tuft', th=0.42)
    use('head')
    mz = muzzle(Hd, (0.56, 0.3, 0.32), -0.28, 'belly', nose=(0.26, 0.1, 0.14), nose_mat='dark')
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.22))
        # wide crescent horns sweeping out sideways
        for j in range(3):
            b('horn', (0.24, 0.18 - 0.02 * j, 0.18 - 0.02 * j), mm('horn'), (sgn * (Hd.s.x / 2 + 0.1 + j * 0.18), Hd.c.y, Hd.top - 0.02 + 0.03 * j * j), rot=(0, -sgn * 10 * j, 0), bev=0.04)
    eyes(Hd, 0.3, 0.25, 0.1, iris='#2a6a5a', glow='#5affd0', brow='#24202a', tilt=-10)
    for i in range(4):
        b('forelock', (0.22, 0.2, 0.22), mm('mane2'), ((i - 1.5) * 0.24, Hd.front + 0.14, Hd.top + 0.04), bev=0.05)
    b('beard', (0.44, 0.24, 0.4), mm('mane'), (0, Hd.front + 0.16, Hd.bot - 0.16), bev=0.06)
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        p('hoof_glow', (ft.s.x + 0.03, ft.s.y + 0.03, 0.035), mm('glow'), (ft.c.x, ft.c.y, ft.top + 0.01))
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.8, 0.06), mm('belly'), (ft.c.x, ft.c.y + 0.02, 0.3))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'mane', size=0.16)
    # rarity 4: glowing runes on the mane cloak, glowing horn tips, sparks
    sg('glow', 'body', (0, B.front + 0.3, B.c.z + 0.3))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(3):
            p('mane_rune', (0.06, 0.16, 0.16), mm('glow'), (sgn * 0.81, B.front + 0.1 + j * 0.3, B.c.z + 0.5), rot=(45, 0, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        p('horn_tip', (0.16, 0.14, 0.14), mm('glow'), (sgn * (Hd.s.x / 2 + 0.1 + 3 * 0.18 + 0.04), Hd.c.y, Hd.top + 0.2))
    use('body')
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=1.8)
    return finish(a)


def _bear_base(a, pal_scale=1.0):
    B, Hd = quad(bw=1.3, bl=1.5, bh=1.06, legh=0.44, lw=0.4, hw=1.34, hd=1.06, hh=1.06, head_up=0.46, hump=0.2, toe='accent',
                 leg_fl=0.6, ntoe=4)
    return B, Hd


def cavebear(row):
    """seated mountain bear: sits like a boulder, round belly, arms hugging a mossy stone, mushroom garden growing on its head and shoulders"""
    a = start(row, dict(main='#8e8a80', belly='#d8d2c0', dark='#5a564e', accent='#f6f0dc', moss='#6aa84a', stone='#6e7068',
                        **{'*glow': '#5affd0', '*glow2': '#ffe14a'}), 3.14)
    B, Hd = sit(bw=1.6, bd=1.3, bh=1.5, hw=1.4, hd=1.1, hh=1.0, arm=0.7, lw=0.4, foot_l=0.8, ntoe=4, foot='belly', toe='dark')
    use('body')
    b('belly_round', (1.2, 0.2, 1.1), mm('belly'), (0, B.front - 0.06, B.c.z - 0.1), bev=0.12)
    for j in range(4):
        p('belly_fur', (0.9 - 0.15 * j, 0.06, 0.1), mm('accent'), (0, B.front - 0.17, B.c.z + 0.3 - j * 0.22))
    for sgn, n in LR:
        b('hip', (0.36, 0.7, 0.6), mm('main'), (sgn * (B.s.x / 2 + 0.1), 0.42, 0.5), bev=0.08)
        for j in range(3):
            p('side_fur', (0.06, 0.24, 0.26), mm('dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.3 + j * 0.3, B.c.z + 0.3))
    use('head')
    mz = muzzle(Hd, (0.6, 0.3, 0.38), -0.25, 'belly', nose=(0.26, 0.12, 0.15), fangs=0)
    for sgn, n in LR:
        p('blush', (0.18, 0.03, 0.09), mm('pink'), (sgn * 0.48, Hd.front - 0.012, Hd.c.z - 0.2))
        b('ear', (0.3, 0.14, 0.3), mm('main'), (sgn * 0.52, Hd.c.y, Hd.top + 0.1), bev=0.07)
        p('ear_in', (0.16, 0.04, 0.16), mm('accent'), (sgn * 0.52, Hd.c.y - 0.08, Hd.top + 0.1))
    eyes(Hd, 0.26, 0.24, 0.14, iris='#2a6a5a', glow='#5affd0', brow='#5a564e', tilt=10, sleepy=0.22)
    # the mossy stone it hugs (own segment, rocks in Idle)
    sg('stone', 'body', (0, B.front - 0.4, B.c.z - 0.3))
    b('hug_stone', (1.0, 0.6, 0.8), mm('stone'), (0, B.front - 0.4, B.c.z - 0.3), bev=0.14)
    b('hug_moss', (0.8, 0.5, 0.2), mm('moss'), (0, B.front - 0.4, B.c.z + 0.16), bev=0.06)
    for j in range(3):
        p('stone_spot', (0.16, 0.05, 0.16), mm('dark'), ((j - 1) * 0.3, B.front - 0.71, B.c.z - 0.3 + 0.1 * (j % 2)))
    a.extra_idle.append(lambda c, n: [k(c, 'stone', x, rot=(0, r, 0)) for x, r in ((1, 0), (n // 2, 4), (n, 0))])
    use('body')
    grid(B, 'l', 4, 4, mm('dark'), (0.12, 0.12), name='fur_tuft', offset=0.06)
    grid(B, 'r', 4, 4, mm('dark'), (0.12, 0.12), name='fur_tuft', offset=0.06)
    grid(B, 'k', 4, 3, mm('accent'), (0.14, 0.14), name='back_tuft')
    grid(B, 't', 2, 2, mm('accent'), (0.14, 0.14), name='top_tuft')
    use('head')
    grid(Hd, 'l', 3, 2, mm('accent'), (0.12, 0.12), name='cheek_tuft')
    grid(Hd, 'r', 3, 2, mm('accent'), (0.12, 0.12), name='cheek_tuft')
    grid(Hd, 'k', 3, 2, mm('dark'), (0.12, 0.12), name='nape_tuft')
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(4):
            p('claw', (0.08, 0.1, 0.08), mm('accent'), (ft.c.x + (j - 1.5) * 0.08, ft.front - 0.04, 0.08))
    use('body')
    tail_kit('stub', 'body', (0, a.tail_j[1], 0.3), 'main', 'dark', size=0.24)
    # rarity 5: glowing mushroom garden on the head and shoulders (own segment), leaf orbit, yellow aura
    sg('glow', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow')
    for i, (x, y, s) in enumerate(((-0.34, 0.0, 1.0), (0.3, 0.1, 0.8), (0.0, 0.3, 1.2), (-0.1, -0.24, 0.6))):
        p('shroom_stem', (0.1 * s, 0.1 * s, 0.3 * s), mm('accent'), (x, Hd.c.y + y, Hd.top + 0.15 * s))
        b('shroom_cap', (0.36 * s, 0.36 * s, 0.14 * s), mm('glow'), (x, Hd.c.y + y, Hd.top + 0.36 * s), bev=0.04)
        p('shroom_dot', (0.07 * s, 0.07 * s, 0.03), mm('glow2'), (x + 0.08 * s, Hd.c.y + y - 0.06 * s, Hd.top + 0.44 * s))
    b('head_moss', (1.0, 0.8, 0.1), mm('moss'), (0, Hd.c.y, Hd.top + 0.04), bev=0.03)
    use('body')
    for sgn, n in LR:
        b('shoulder_moss', (0.5, 0.5, 0.1), mm('moss'), (sgn * 0.5, B.c.y, B.top + 0.04), bev=0.03)
        for j in range(2):
            p('shoulder_shroom', (0.2, 0.2, 0.1), mm('glow2' if j else 'glow'), (sgn * (0.4 + 0.2 * j), B.c.y + 0.1 * j, B.top + 0.18))
    orbit_kit((0, 0.1, 1.6), 1.7, 6, 'glow', 'glow2', size=0.13, dz=0.4, shape='leaf')
    aura_kit(1.7, 5, motes=10, mote_col='glow', height=2.2, style='double')
    return finish(a)


def spiritdeer(row):
    a = start(row, dict(main='#eafff6', belly='#c4f4e4', dark='#3a8a86', accent='#8fe8d6', mane='#7fe0cc',
                        **{'*glow': '#5affd0', '*glow2': '#fff6a0', '*gold': '#ffd84a'}), 4.4)
    B, Hd = quad(bw=0.84, bl=1.3, bh=0.68, legh=0.84, lw=0.2, hw=1.04, hd=0.88, hh=0.9, neck=0.3, hoof='dark', head_fwd=0.3)
    mz = muzzle(Hd, (0.42, 0.3, 0.28), -0.26, 'belly', nose=(0.16, 0.08, 0.1), nose_mat='pink')
    cheeks(Hd, 'belly', (0.18, 0.16, 0.24), -0.26, whisk=0)
    eyes(Hd, 0.36, 0.25, 0.1, iris='#2a8a7a', glow='#5affd0', lash=True, brow='#3a8a86', tilt=8)
    ears(Hd, 'long', 'main', 'accent', tip='accent', x=0.48, h=0.44, w=0.24, lean=52)
    # glowing antlers: own segment so they flicker
    sg('antlers', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('antlers')
    horns(Hd, 'antler', 'glow', x=0.2, h=1.0, r=0.07, n=3, seg_parent='antlers')
    for sgn, n in LR:
        p('antler_gem', (0.12, 0.12, 0.12), mm('glow2'), (sgn * (0.2 * Hd.s.x + 0.22), Hd.c.y, Hd.top + 1.22), rot=(45, 45, 0))
        p('antler_ring', (0.2, 0.2, 0.06), mm('gold'), (sgn * (0.2 * Hd.s.x + 0.03), Hd.c.y, Hd.top + 0.12))
        p('antler_vine', (0.1, 0.05, 0.3), mm('glow2'), (sgn * (0.2 * Hd.s.x + 0.4), Hd.c.y - 0.06, Hd.top + 0.5), rot=(0, sgn * 30, 0))
    use('head')
    for i, (dx, dz, w, h) in enumerate(((0, 0.3, 0.1, 0.2), (-0.12, 0.34, 0.07, 0.07), (0.12, 0.34, 0.07, 0.07), (0, 0.46, 0.06, 0.06))):
        p('fore_rune', (w, 0.03, h), mm('glow'), (dx, Hd.front - 0.012, Hd.c.z + dz - 0.1))
    for j in range(4):
        b('mane', (0.24, 0.22, 0.26 - 0.03 * j), mm('mane'), (0, Hd.back - 0.02 + j * 0.02, Hd.top - 0.1 - j * 0.24), bev=0.05)
    use('body')
    for j in range(4):
        b('mane', (0.22, 0.24, 0.2), mm('mane'), (0, B.front + 0.1 + j * 0.24, B.top + 0.08 + (0.24 if j == 0 else 0)), bev=0.05)
    fluff(a.bx['chest'], 'f', mm('accent'), 4, 0.9, 0.38)
    on(a.bx['rump'], 'k', 0, 0.12, (0.56, 0.4), mm('belly'), name='rump_patch')
    spots(B, 'lr', 6, mm('accent'), 0.12, seed=3, name='spot')
    spots(a.bx['rump'], 'lr', 4, mm('accent'), 0.1, seed=7, name='spot')
    for ft in a.bx['feet']:
        p('sock', (ft.s.x - 0.02, ft.s.y - 0.04, 0.16), mm('accent'), (ft.c.x, ft.c.y + 0.02, ft.top + 0.1))
        p('hoof_gold', (ft.s.x + 0.02, ft.s.y + 0.02, 0.04), mm('gold'), (ft.c.x, ft.c.y, ft.top + 0.01))
        p('leg_vine', (0.05, 0.04, 0.3), mm('glow'), (ft.c.x, ft.front + 0.06, 0.52))
        p('leg_leaf', (0.1, 0.04, 0.08), mm('glow2'), (ft.c.x + 0.05, ft.front + 0.06, 0.66))
    tail_kit('tuft', 'body', a.tail_j, 'main', 'mane', size=0.2)
    # rarity 6: glowing constellation on the body, halo crown, two counter-rotating orbits, red aura
    glow_marks(B, ('l', 'r'), 4, 'glow', style='star', size=0.13, col2='glow2')
    use('glow')
    for i in range(5):
        on(B, 't', 0.2 * (1 if i % 2 else -1), -0.4 + i * 0.2, (0.12, 0.12), mm('glow2' if i % 2 else 'glow'), th=0.035, name='glow_star', rot=(0, 0, 45))
    for sgn, n in LR:
        on(a.bx['rump'], 'l' if sgn < 0 else 'r', 0, 0.12, (0.2, 0.2), mm('glow'), th=0.035, name='glow_star', rot=(45, 0, 0))
        on(a.bx['rump'], 'l' if sgn < 0 else 'r', 0.2, -0.16, (0.1, 0.1), mm('glow2'), th=0.035, name='glow_star', rot=(45, 0, 0))
    use('tail')
    p('tail_glow', (0.16, 0.16, 0.16), mm('glow'), (0, a.tail_j[1] + 0.5, a.tail_j[2] - 0.24), rot=(45, 45, 0))
    halo_kit(Hd, 'gold', r=0.5, n=10, dz=1.55, kind='leaves')
    use('body')
    orbit_kit((0, 0.2, 1.6), 1.5, 6, 'glow', 'glow2', size=0.13, dz=0.5, shape='leaf')
    orbit_kit((0, 0.2, 1.2), 2.0, 8, 'gold', 'glow', size=0.1, name='orbit2', dz=0.2, shape='star')
    aura_kit(1.7, 6, motes=12, mote_col='glow', height=2.4, style='petals')
    return finish(a)


ANIMALS = dict(deer=deer, moose=moose, bear=bear, bison=bison, cavebear=cavebear, spiritdeer=spiritdeer)
