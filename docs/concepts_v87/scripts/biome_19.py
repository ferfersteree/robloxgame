# Biome 19 - Starbound Frontier: meteor craters, star dust, constellation light
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 19
GROUND = '#2e3a6a'
SKY = '#1e2450'
THEME = dict(bits=['#ffe68a', '#8ad8ff'], dust='#6a7ab8', glow='#ffe68a', splash='#c8e0ff', bit_name='звёздная пыль')
FOOT = dict(orbital_jellyfish=1.2, astral_dragon=1.35, stellar_stag=1.1)
BUSH_NAME = 'метеоритный куст: оплавленный камень-кратер, из которого растут кристаллические ветви со звёздами-плодами'


def bush():
    B = begin_bush(NN)
    rock = mat('rock', '#3a3450')
    rock2 = mat('rock2', '#5a5274')
    lava = mat('core', '#ff9a4a', 'neon', 2.0)
    branch = mat('branch', '#a8c8ff')
    leaf = mat('leaf', '#4a5ab8')
    star = mat('star', '#ffe68a', 'neon', 2.6)
    star2 = mat('star2', '#8ad8ff', 'neon', 2.4)
    # crater ring of rubble around a glowing meteorite core
    part('big', (0, 0.3, 0.3), 'crater')
    for i in range(10):
        ang = math.radians(i * 36)
        b('crater_rock', (1.2, 0.9, 0.6 + 0.2 * (i % 3)), rock if i % 2 else rock2, (math.cos(ang) * 2.6, 0.3 + math.sin(ang) * 1.1, 0.35),
          rot=(0, 0, i * 36), bev=0.1)
    b('meteor', (1.6, 1.4, 1.2), rock, (0, 0.4, 0.7), rot=(10, 15, 20), bev=0.15)
    for i, (x, y, z) in enumerate(((-0.5, -0.3, 0.9), (0.4, -0.25, 0.6), (0.1, -0.32, 1.2))):
        p('meteor_crack', (0.3, 0.06, 0.1), lava, (x, y, z), rot=(0, 30 * (i - 1), 0))
    # crystal branches growing out of the meteor, star fruit on the tips
    spec = ((-1.4, 0.4, 3.6, -30), (1.4, 0.4, 3.8, 28), (0, 0.6, 3.9, 0), (-0.7, 0.2, 3.0, -15), (0.8, 0.3, 3.1, 14), (-2.4, 0.2, 2.2, -40), (2.4, 0.3, 2.3, 40))
    for i, (x, y, h, tilt) in enumerate(spec):
        part('big' if h > 3.5 else 'small', (x, y, h * 0.6), 'branch_%d' % i)
        b('branch', (0.24, 0.24, h - 1.0), branch, (x * 0.55, y, 1.0 + (h - 1.0) / 2), rot=(0, tilt, 0), bev=0.04)
        for j in range(2):
            p('leaf', (0.4, 0.1, 0.18), leaf, (x * (0.55 + 0.15 * j) + 0.2, y, 1.6 + j * 0.8), rot=(0, tilt + 20, 0))
        s = 0.6 if h > 3.5 else 0.45
        b('star_fruit', (s, s * 0.4, s), star if i % 2 == 0 else star2, (x, y, h), rot=(0, 45, 0), bev=0.04)
        for k_ in range(4):
            ang = math.radians(k_ * 90)
            p('star_point', (s * 0.24, s * 0.3, s * 0.24), star if i % 2 == 0 else star2, (x + math.cos(ang) * s * 0.62, y, h + math.sin(ang) * s * 0.62),
              rot=(0, 45, 0))
    for i, (x, y, z) in enumerate(((-1.0, 0.0, 4.6), (0.9, 0.1, 4.5), (1.9, 0.0, 3.4), (-2.0, 0.1, 3.2))):
        part('small', (x, y, z), 'dust_%d' % i)
        b('dust', (0.18, 0.18, 0.18), star2, (x, y, z), rot=(45, 45, 0), bev=0.04)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def nebula_tardigrade(row):
    """water-bear: a chubby barrel of four puffy rings, eight stubby legs with tiny claws, a round tube snout, freckled with nebula dots"""
    a = start(row, dict(main='#c8b0ff', belly='#ece0ff', dark='#5a4a9a', accent='#ff9ad0', claw='#3a2e6a', freckle='#8ad8ff'), 1.24)
    sg('body', 'root', (0, 0.2, 0.75))
    B = None
    for i in range(4):
        w = (0.95, 1.05, 1.0, 0.85)[i]
        bx = b('ring', (w, 0.42, w * 0.85), mm('main' if i % 2 == 0 else 'belly'), (0, -0.35 + i * 0.4, 0.78), bev=0.14)
        if i == 1:
            B = bx
        p('ring_line', (w * 0.9, 0.05, 0.06), mm('dark'), (0, -0.14 + i * 0.4, 0.78 + w * 0.42))
    # legs: 4 pairs of stubby legs
    for i in range(4):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.4, -0.35 + i * 0.4, 0.4))
            a.legs.append(nm)
            b('leg', (0.26, 0.26, 0.32), mm('main'), (sgn * 0.44, -0.35 + i * 0.4, 0.2), bev=0.07)
            for t in range(2):
                p('claw', (0.05, 0.1, 0.05), mm('claw'), (sgn * 0.44 + (t - 0.5) * 0.1, -0.35 + i * 0.4 - 0.15, 0.04))
    sg('head', 'body', (0, -0.55, 0.8))
    Hd = b('head', (0.84, 0.4, 0.7), mm('main'), (0, -0.7, 0.8), bev=0.14)
    # tube snout (the silhouette)
    b('snout', (0.32, 0.3, 0.32), mm('belly'), (0, Hd.front - 0.12, 0.66), bev=0.06)
    p('snout_hole', (0.16, 0.04, 0.16), mm('dark'), (0, Hd.front - 0.28, 0.66))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('accent'), (sgn * 0.3, Hd.front - 0.012, 0.66))
    eyes(Hd, 0.22, 0.24, 0.16, iris='#3a2e6a', brow=None)
    use('body')
    grid(Box((0, 0.2, 0.78), (1.0, 1.6, 0.86)), 't', 3, 4, mm('freckle'), (0.1, 0.1), name='nebula_dot', span=(0.6, 0.8))
    grid(Box((0, 0.2, 0.78), (1.0, 1.6, 0.86)), 'l', 4, 2, mm('accent'), (0.08, 0.08), name='side_dot', span=(0.8, 0.5))
    grid(Box((0, 0.2, 0.78), (1.0, 1.6, 0.86)), 'r', 4, 2, mm('accent'), (0.08, 0.08), name='side_dot', span=(0.8, 0.5))
    tail_kit('stub', 'body', (0, 1.0, 0.7), 'main', 'belly', size=0.22)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, Hd.front - 0.1, 0.7), Hit=(0, 0.2, 1.2))
    return finish(a)


def comet_fox(row):
    """comet fox curled up like a sleeping donut: round body, head resting on its paws, a huge comet tail
    wrapped round the front that fades from orange to a glowing white tip"""
    a = start(row, dict(main='#3a4a9a', belly='#e8ecff', dark='#1e2450', accent='#ffb04a', t1='#ff8a3a', t2='#ffd04a', t3='#fff4c8', ear='#ff9ad0',
                        **{'*tip': '#ffffff'}), 1.23)
    sg('body', 'root', (0, 0.3, 0.5))
    B = b('body', (1.3, 1.1, 0.8), mm('main'), (0, 0.4, 0.45), bev=0.18)
    b('body_hump', (0.9, 0.8, 0.3), mm('main'), (0.1, 0.5, 0.94), bev=0.1)
    grid(B, 't', 3, 3, mm('belly'), (0.08, 0.08), name='star_freckle', span=(0.7, 0.7), rot=(0, 0, 45))
    grid(B, 'l', 3, 2, mm('dark'), (0.1, 0.1), name='side_spot', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('dark'), (0.1, 0.1), name='side_spot', span=(0.7, 0.5))
    grid(B, 'k', 3, 2, mm('dark'), (0.1, 0.1), name='back_spot', span=(0.7, 0.5))
    # front paws tucked in front
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.3, -0.1, 0.2))
        a.legs.append(nm)
        b('paw', (0.3, 0.5, 0.2), mm('belly'), (sgn * 0.3, -0.3, 0.1), bev=0.06)
        for t in range(3):
            p('toe', (0.07, 0.05, 0.06), mm('dark'), (sgn * 0.3 + (t - 1) * 0.09, -0.56, 0.08))
    # head resting low on the paws, turned toward the camera
    sg('head', 'body', (-0.1, -0.2, 0.5))
    Hd = b('head', (0.84, 0.66, 0.66), mm('main'), (-0.1, -0.4, 0.5), rot=(0, 0, 8), bev=0.12)
    mz = muzzle(Hd, (0.4, 0.28, 0.24), -0.32, 'belly', nose=(0.12, 0.08, 0.08), nose_mat='dark')
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (-0.1 + sgn * 0.26, -0.4, Hd.top))
        a.ears.append(nm)
        b('ear', (0.24, 0.14, 0.36), mm('main'), (-0.1 + sgn * 0.26, -0.4, Hd.top + 0.16), rot=(0, sgn * 12, 0), bev=0.04)
        p('ear_in', (0.12, 0.04, 0.22), mm('ear'), (-0.1 + sgn * 0.26, -0.48, Hd.top + 0.14), rot=(0, sgn * 12, 0))
        p('ear_tip', (0.16, 0.16, 0.08), mm('accent'), (-0.1 + sgn * 0.27, -0.4, Hd.top + 0.36))
        p('blush', (0.12, 0.03, 0.06), mm('ear'), (-0.1 + sgn * 0.26, Hd.front - 0.012, Hd.c.z - 0.1))
    eyes(Hd, 0.24, 0.24, 0.08, iris='#ffb04a', brow=None, sleepy=0.5)
    # the comet tail: from the back, round the right side, across the front (the silhouette)
    use('body')
    sg('tail', 'body', (0.4, 0.9, 0.5))
    a.tail = ['tail']
    cols = ('t1', 't1', 't2', 't2', 't3', 't3', 't3', 't3')
    for i in range(8):
        ang = math.radians(95 - i * 20)
        r = 0.95
        s = 0.5 + 0.03 * i
        b('tail', (s, s, s * 0.9), mm(cols[i]), (math.cos(ang) * r + 0.1, 0.35 + math.sin(ang) * r * 0.9, 0.3 + 0.04 * i), rot=(0, 0, -i * 20), bev=0.08)
    p('tail_star', (0.3, 0.12, 0.3), mm('tip'), (math.cos(math.radians(-45)) * 0.95 + 0.1, 0.35 + math.sin(math.radians(-45)) * 0.86, 0.9), rot=(0, 45, 0))
    for i in range(6):
        ang = math.radians(70 - i * 22)
        p('tail_spark', (0.1, 0.1, 0.1), mm('tip'), (math.cos(ang) * 1.25 + 0.1, 0.35 + math.sin(ang) * 1.15, 0.4 + 0.1 * (i % 2)), rot=(45, 45, 0))
    use('head')
    grid(Hd, 't', 2, 2, mm('belly'), (0.08, 0.08), name='head_star', span=(0.5, 0.5), rot=(0, 0, 45))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 0.5), Hit=(0, 0.4, 0.9))
    return finish(a)


def astral_starfish(row):
    """a five-armed star that walks upright on its two lower arms like a little person, face in the middle,
    tube-feet dots along every arm, a tiny constellation crown on the top arm"""
    a = start(row, dict(main='#ff8a5a', belly='#ffd8a8', dark='#a8402a', accent='#ffe68a', dot='#fff0d8', iris='#3a2e6a'), 3.46)
    zc = 1.3
    sg('body', 'root', (0, 0, zc))
    B = b('core', (1.0, 0.5, 1.0), mm('main'), (0, 0, zc), rot=(0, 45, 0), bev=0.14)
    b('core_belly', (0.66, 0.1, 0.66), mm('belly'), (0, -0.26, zc), rot=(0, 45, 0), bev=0.06)
    arms = ((0, 'head'), (72, 'arm_R'), (-72, 'arm_L'), (148, 'leg_R'), (-148, 'leg_L'))
    for ang, nm in arms:
        r = math.radians(ang)
        d = Vector((math.sin(r), 0, math.cos(r)))
        j = Vector((0, 0, zc)) + d * 0.4
        sg(nm, 'body', tuple(j))
        if nm.startswith('arm'):
            a.arms.append(nm)
        elif nm.startswith('leg'):
            a.legs.append(nm)
        for k_ in range(3):
            ln = 0.42
            w = 0.5 - 0.12 * k_
            c = j + d * (0.22 + k_ * ln)
            b('arm_seg', (w, 0.38 - 0.06 * k_, ln + 0.06), mm('main'), tuple(c), rot=(0, ang, 0), bev=0.07)
            p('tube_foot', (0.1, 0.06, 0.1), mm('dot'), tuple(c + Vector((0, -0.2 + 0.03 * k_, 0))), rot=(0, ang, 0))
            p('arm_band', (w + 0.02, 0.2, 0.05), mm('belly'), tuple(c + d * (ln / 2)), rot=(0, ang, 0))
            for sgn in (-1, 1):
                side = Vector((d.z, 0, -d.x)) * sgn * (w / 2 + 0.01)
                p('arm_bump', (0.06, 0.08, 0.06), mm('dark'), tuple(c + side), rot=(0, ang, 0))
        tip = j + d * (0.22 + 2 * 0.42 + 0.3)
        p('arm_tip', (0.16, 0.16, 0.16), mm('accent'), tuple(tip), rot=(0, ang + 45, 0))
    # face on the core
    use('body')
    Hd = Box((0, -0.08, zc + 0.05), (0.9, 0.5, 0.8), 'body')
    eyes(Hd, 0.24, 0.22, 0.12, iris='#3a2e6a', brow=None, lash=True, head='body')
    p('smile', (0.24, 0.03, 0.04), mm('dark'), (0, -0.335, zc - 0.16))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('dark'), (sgn * 0.26, -0.335, zc - 0.08))
    # little constellation crown on the top arm
    use('head')
    for i in range(3):
        p('crown_star', (0.12, 0.08, 0.12), mm('accent'), ((i - 1) * 0.16, 0, zc + 1.62 + (0.08 if i == 1 else 0)), rot=(0, 45, 0))
    p('crown_bar', (0.36, 0.05, 0.04), mm('accent'), (0, 0, zc + 1.58))
    use('body')
    for i in range(10):
        ang = math.radians(i * 36 + 18)
        p('core_dot', (0.08, 0.06, 0.08), mm('accent' if i % 2 else 'dot'), (math.sin(ang) * 0.42, 0.22, zc + math.cos(ang) * 0.42), rot=(0, 45, 0))
    for i in range(4):
        p('back_ridge', (0.14, 0.1, 0.14), mm('dark'), ((i - 1.5) * 0.18, 0.27, zc + 0.1), rot=(0, 45, 0))
    a.bx.update(body=B, head=Box((0, 0, zc + 1.1), (0.5, 0.38, 1.2), 'head'))
    a.marks = dict(Head=(0, 0, zc + 1.0), Chest=(0, -0.3, zc), Hit=(0, 0, zc + 0.2))
    a.tail = []
    return finish(a)


def stellar_stag(row):
    """a constellation stag: its body is a see-through frame of dark star-lines with glowing star nodes on every corner,
    a solid little face, huge branching constellation antlers"""
    a = start(row, dict(main='#1e2a6a', belly='#3a4a9a', dark='#0e1430', accent='#c8d8ff', face='#2e3e8a', hoof='#8ad8ff',
                        **{'*glow': '#ffffff', '*glow2': '#8ad8ff', '*glow3': '#ffe68a'}), 5.56)
    LEG = 1.6
    zb = LEG + 0.4
    by, bl, bw, bh = 0.4, 1.6, 0.7, 0.8
    sg('body', 'root', (0, by, zb))
    th = 0.12
    B = Box((0, by, zb), (bw, bl, bh), 'body')
    xs, ys, zs = (-bw / 2, bw / 2), (by - bl / 2, by + bl / 2), (zb - bh / 2, zb + bh / 2)
    for x in xs:
        for z in zs:
            b('line_y', (th, bl, th), mm('main'), (x, by, z), bev=0.03)
    for y in ys:
        for z in zs:
            b('line_x', (bw, th, th), mm('main'), (0, y, z), bev=0.03)
        for x in xs:
            b('line_z', (th, th, bh), mm('main'), (x, y, zb), bev=0.03)
    for sgn in (-1, 1):
        p('line_diag', (th * 0.7, th * 0.7, bl * 0.95), mm('belly'), (sgn * bw / 2, by, zb), rot=(62, 0, 0))
        p('line_diag_t', (th * 0.7, bl * 0.95, th * 0.7), mm('belly'), (0, by, zs[1]), rot=(0, 0, sgn * 22))
    # nebula heart floating inside the frame
    b('heart', (0.3, 0.3, 0.3), mm('belly'), (0, by, zb), rot=(45, 45, 0), bev=0.05)
    # legs: two-bar lines with star knees
    a.bx['feet'] = []
    for fy in (by - bl / 2 + 0.1, by + bl / 2 - 0.1):
        for sgn, n in LR:
            nm = 'leg_%s%s' % ('f' if fy < by else 'b', n)
            sg(nm, 'body', (sgn * bw / 2, fy, zs[0]))
            a.legs.append(nm)
            b('leg_up', (th, th, LEG * 0.5), mm('main'), (sgn * bw / 2, fy, zs[0] - LEG * 0.25), bev=0.03)
            b('leg_low', (th, th, LEG * 0.5), mm('main'), (sgn * bw / 2, fy + 0.06, LEG * 0.25 + 0.1), bev=0.03)
            b('hoof', (0.24, 0.3, 0.16), mm('hoof'), (sgn * bw / 2, fy + 0.02, 0.08), bev=0.04)
            p('hoof_band', (0.2, 0.2, 0.05), mm('accent'), (sgn * bw / 2, fy + 0.04, 0.2))
    # neck and the solid little head
    sg('head', 'body', (0, ys[0], zs[1]))
    b('neck', (th, th, 0.9), mm('main'), (0, ys[0] - 0.1, zs[1] + 0.36), rot=(-20, 0, 0), bev=0.03)
    hz = zs[1] + 0.95
    Hd = b('head', (0.66, 0.6, 0.56), mm('face'), (0, ys[0] - 0.36, hz), bev=0.12)
    mz = muzzle(Hd, (0.36, 0.26, 0.24), -0.18, 'belly', nose=(0.12, 0.08, 0.08), nose_mat='accent')
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.3, Hd.c.y, Hd.top - 0.1))
        a.ears.append(nm)
        b('ear', (0.3, 0.1, 0.14), mm('face'), (sgn * 0.44, Hd.c.y, Hd.top - 0.08), rot=(0, sgn * -20, 0), bev=0.03)
        p('blush', (0.1, 0.03, 0.05), mm('accent'), (sgn * 0.22, Hd.front - 0.012, hz - 0.12))
    eyes(Hd, 0.26, 0.22, 0.1, iris='#8ad8ff', glow='#8ad8ff', lash=True, brow=None)
    grid(Hd, 't', 2, 2, mm('accent'), (0.06, 0.06), name='face_star', span=(0.5, 0.5), rot=(0, 0, 45))
    grid(Hd, 'l', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_dot', span=(0.6, 0.5))
    grid(Hd, 'r', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_dot', span=(0.6, 0.5))
    # constellation antlers: branching lines with nodes
    use('head')
    ant = {}
    for sgn, n in LR:
        base = Vector((sgn * 0.2, Hd.c.y, Hd.top))
        segs = ((base, base + Vector((sgn * 0.3, 0, 0.6))), (base + Vector((sgn * 0.3, 0, 0.6)), base + Vector((sgn * 0.8, 0.1, 1.1))),
                (base + Vector((sgn * 0.3, 0, 0.6)), base + Vector((sgn * 0.2, -0.1, 1.3))), (base + Vector((sgn * 0.8, 0.1, 1.1)), base + Vector((sgn * 1.3, 0.1, 1.3))),
                (base + Vector((sgn * 0.8, 0.1, 1.1)), base + Vector((sgn * 0.9, 0.15, 1.7))), (base + Vector((sgn * 0.2, -0.1, 1.3)), base + Vector((sgn * 0.5, -0.1, 1.8))))
        ant[n] = segs
        for s0, s1 in segs:
            d = s1 - s0
            c = (s0 + s1) / 2
            ln = d.length
            ry = math.degrees(math.atan2(d.x, d.z))
            rx = -math.degrees(math.asin(max(-1, min(1, d.y / ln))))
            b('antler_line', (0.09, 0.09, ln), mm('accent'), tuple(c), rot=(rx, ry, 0), bev=0.02)
    # star nodes: frame corners, knees, antler joints (glowing, own segments)
    sg('glow', 'body', (0, by, zb))
    a.glow.append('glow')
    for x in xs:
        for y in ys:
            for z in zs:
                p('node', (0.2, 0.2, 0.2), mm('glow' if z > zb else 'glow2'), (x, y, z), rot=(45, 45, 0))
    p('heart_glow', (0.16, 0.16, 0.16), mm('glow3'), (0, by, zb), rot=(45, 0, 45))
    for i in range(10):
        p('dust', (0.07, 0.07, 0.07), mm('glow2'), (0.22 * math.sin(i * 2.1), by - 0.65 + i * 0.145, zb + 0.22 * math.cos(i * 1.7)), rot=(45, 45, 0))
    for nm in a.legs:
        use(nm)
        sgn = -1 if nm.endswith('L') else 1
        fy = by - bl / 2 + 0.1 if '_f' in nm else by + bl / 2 - 0.1
        p('knee_node', (0.16, 0.16, 0.16), mm('glow2'), (sgn * bw / 2, fy + 0.03, LEG * 0.5 + 0.1), rot=(45, 45, 0))
    use('head')
    for n, segs in ant.items():
        for s0, s1 in segs:
            p('antler_node', (0.15, 0.15, 0.15), mm('glow3' if s1.z > Hd.top + 1.5 else 'glow'), tuple(s1), rot=(45, 45, 0))
    use('body')
    sg('tail', 'body', (0, ys[1], zs[1]))
    a.tail = ['tail']
    b('tail_line', (th, 0.5, th), mm('main'), (0, ys[1] + 0.2, zs[1] + 0.1), rot=(30, 0, 0), bev=0.03)
    p('tail_node', (0.18, 0.18, 0.18), mm('glow3'), (0, ys[1] + 0.42, zs[1] + 0.24), rot=(45, 45, 0))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, ys[0], zb), Hit=(0, by, zb + 0.2))
    aura_kit(1.4, 4, motes=8, mote_col='glow2', height=3.4)
    return finish(a)


def orbital_jellyfish(row):
    """sky jellyfish: a tall stepped bell with a smiling face, a tilted planet ring around the bell,
    four frilly oral arms in the middle and six long ribbon tentacles"""
    zc = 2.0
    a = start(row, dict(main='#9ad0ff', belly='#e0f2ff', dark='#3a6aa8', accent='#ff9ad0', ring='#ffd88a', ring2='#c8a8ff', frill='#c8e8ff',
                        **{'*glow': '#8ae8ff', '*glow2': '#ffe68a'}), 3.87, hover=3.4, z0=zc)
    sg('body', 'root', (0, 0, zc))
    B = None
    for i, (w, h) in enumerate(((2.0, 0.6), (1.7, 0.5), (1.3, 0.4), (0.8, 0.25))):
        bx = b('bell', (w, w, h), mm('main' if i % 2 == 0 else 'belly'), (0, 0, zc + 0.3 + sum((0.6, 0.5, 0.4, 0.25)[:i]) + h / 2 - 0.3), bev=0.12)
        if i == 0:
            B = bx
    for i in range(12):
        ang = math.radians(i * 30)
        p('skirt', (0.3, 0.3, 0.24), mm('frill' if i % 2 else 'accent'), (math.cos(ang) * 0.95, math.sin(ang) * 0.95, zc - 0.08), rot=(0, 0, i * 30))
        p('skirt_dot', (0.1, 0.1, 0.1), mm('belly'), (math.cos(ang) * 1.01, math.sin(ang) * 1.01, zc + 0.1), rot=(0, 0, i * 30))
    Hd = Box((0, 0, zc + 0.4), (2.0, 2.0, 0.8), 'body')
    eyes(Hd, 0.34, 0.36, 0.0, iris='#3a4a8a', brow=None, lash=True, head='body')
    p('smile', (0.34, 0.03, 0.05), mm('dark'), (0, -1.012, zc + 0.12))
    for sgn, n in LR:
        p('blush', (0.18, 0.03, 0.08), mm('accent'), (sgn * 0.56, -1.012, zc + 0.2))
    sg('head', 'body', (0, 0, zc + 1.1))
    grid(Box((0, 0, zc + 0.85), (1.7, 1.7, 0.5)), 't', 3, 3, mm('belly'), (0.12, 0.12), name='bell_spot', span=(0.7, 0.7))
    use('body')
    # tilted planet ring (own segment so it can rock)
    sg('ring', 'body', (0, 0, zc + 0.6))
    a.ears.append('ring')
    for i in range(16):
        ang = math.radians(i * 22.5)
        x, y = math.cos(ang) * 1.65, math.sin(ang) * 1.65
        z = zc + 0.6 + math.sin(ang) * 0.35
        p('ring_seg', (0.42, 0.3, 0.1), mm('ring' if i % 2 else 'ring2'), (x, y, z), rot=(0, 0, i * 22.5 + 90))
    # oral arms
    for i in range(4):
        ang = math.radians(45 + i * 90)
        nm = 'arm_%d' % i
        sg(nm, 'body', (math.cos(ang) * 0.25, math.sin(ang) * 0.25, zc - 0.2))
        a.arms.append(nm)
        for j in range(3):
            b('oral_arm', (0.24, 0.24, 0.4), mm('frill'), (math.cos(ang) * 0.25, math.sin(ang) * 0.25, zc - 0.4 - j * 0.38), rot=(0, 0, 45 * j), bev=0.05)
            p('oral_frill', (0.36, 0.08, 0.12), mm('accent'), (math.cos(ang) * 0.25, math.sin(ang) * 0.25, zc - 0.3 - j * 0.38), rot=(0, 0, 45 * j + i * 90))
            p('oral_dot', (0.08, 0.08, 0.08), mm('belly'), (math.cos(ang) * 0.38, math.sin(ang) * 0.38, zc - 0.45 - j * 0.38))
    # six long ribbon tentacles in chains
    a.tail = []
    for i in range(6):
        ang = math.radians(i * 60 + 30)
        x, y = math.cos(ang) * 0.75, math.sin(ang) * 0.75
        par = 'body'
        for j in range(2):
            nm = 'tent_%d_%d' % (i, j)
            sg(nm, par, (x, y, zc - 0.2 - j * 0.9))
            if j == 0:
                a.tail.append(nm)
            for t in range(4):
                p('tentacle', (0.12, 0.06, 0.24), mm('main' if (t + j) % 2 else 'belly'), (x, y, zc - 0.32 - j * 0.9 - t * 0.225), rot=(0, 0, i * 60))
            par = nm
    # rarity 5: glowing bell dots + tentacle tips, ring orbit, yellow aura
    sg('glow', 'body', (0, 0, zc + 0.4))
    a.glow.append('glow')
    for i in range(12):
        ang = math.radians(i * 30 + 15)
        p('bell_glow', (0.12, 0.12, 0.12), mm('glow' if i % 2 else 'glow2'), (math.cos(ang) * 0.86, math.sin(ang) * 0.86, zc + 0.34), rot=(45, 45, 0))
    for i in range(6):
        use('tent_%d_1' % i)
        ang = math.radians(i * 60 + 30)
        p('tent_glow', (0.14, 0.14, 0.14), mm('glow'), (math.cos(ang) * 0.75, math.sin(ang) * 0.75, zc - 2.0), rot=(45, 45, 0))
    use('body')
    a.bx.update(body=B, head=B)
    a.marks = dict(Head=(0, 0, zc + 0.6), Chest=(0, -1.0, zc), Hit=(0, 0, zc + 0.8))
    orbit_kit((0, 0, zc + 0.6), 2.4, 6, 'glow', 'glow2', size=0.14, dz=0.3, shape='ring')
    aura_kit(1.8, 5, motes=10, mote_col='glow', height=2.0, style='rays')
    return finish(a)


def astral_dragon(row):
    """a chubby baby dragon sitting inside a big crescent moon like a cradle, round belly, short snout,
    wide star-map wings spread up and out, tail curled along the moon rim"""
    zc = 1.6
    a = start(row, dict(main='#4a3ab8', belly='#ffe8a8', dark='#1e1650', accent='#ff9ad0', horn='#fff4d8', moon='#fff0b8', moon2='#e8d088',
                        wing='#2e2a7a', **{'*glow': '#ffe68a', '*glow2': '#8ad8ff', '*star': '#ffffff'}), 3.82, hover=3.0, z0=zc)
    sg('body', 'root', (0, 0, zc))
    # the crescent moon cradle (U shape in the x-z plane)
    R = 1.6
    for i in range(13):
        th = math.radians(150 + i * 20)
        x, z = math.cos(th) * R, zc + 0.2 + math.sin(th) * R
        t = 1.0 - abs(i - 6) / 7.0
        s = 0.3 + 0.45 * t
        b('moon', (s, 0.9, s), mm('moon' if i % 2 else 'moon2'), (x, 0.35, z), rot=(0, -math.degrees(th), 0), bev=0.08)
        if i % 3 == 1:
            p('crater', (s * 0.4, 0.06, s * 0.4), mm('moon2'), (x, -0.12, z))
    # chubby sitting dragon
    B = b('body', (1.0, 0.9, 1.0), mm('main'), (0, 0.2, zc - 0.5), bev=0.18)
    b('belly', (0.7, 0.1, 0.8), mm('belly'), (0, -0.26, zc - 0.5), bev=0.05)
    for j in range(4):
        p('belly_line', (0.6, 0.11, 0.04), mm('moon2'), (0, -0.27, zc - 0.8 + j * 0.2))
    grid(B, 'k', 2, 3, mm('dark'), (0.12, 0.12), name='back_scale')
    grid(B, 'l', 2, 2, mm('dark'), (0.1, 0.1), name='side_scale')
    grid(B, 'r', 2, 2, mm('dark'), (0.1, 0.1), name='side_scale')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.4, 0.0, zc - 0.9))
        a.legs.append(nm)
        b('thigh', (0.4, 0.6, 0.36), mm('main'), (sgn * 0.42, -0.1, zc - 0.88), bev=0.08)
        b('foot', (0.34, 0.3, 0.18), mm('main'), (sgn * 0.42, -0.42, zc - 1.0), bev=0.05)
        for t in range(3):
            p('toe', (0.07, 0.06, 0.07), mm('horn'), (sgn * 0.42 + (t - 1) * 0.1, -0.58, zc - 1.0))
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.5, -0.1, zc - 0.2))
        a.arms.append(nm)
        b('arm', (0.22, 0.4, 0.22), mm('main'), (sgn * 0.5, -0.3, zc - 0.36), rot=(30, 0, 0), bev=0.05)
        p('hand', (0.2, 0.16, 0.18), mm('belly'), (sgn * 0.44, -0.48, zc - 0.5))
    sg('head', 'body', (0, 0.1, zc))
    Hd = b('head', (1.1, 0.9, 0.86), mm('main'), (0, 0.0, zc + 0.46), bev=0.16)
    b('snout', (0.6, 0.36, 0.34), mm('belly'), (0, Hd.front - 0.12, zc + 0.3), bev=0.08)
    for sgn, n in LR:
        p('nostril', (0.06, 0.03, 0.04), mm('dark'), (sgn * 0.12, Hd.front - 0.31, zc + 0.36))
        p('blush', (0.14, 0.03, 0.07), mm('accent'), (sgn * 0.4, Hd.front - 0.012, zc + 0.38))
        nm = 'horn_' + n
        sg(nm, 'head', (sgn * 0.3, 0.1, Hd.top))
        a.ears.append(nm)
        b('horn', (0.16, 0.16, 0.34), mm('horn'), (sgn * 0.3, 0.12, Hd.top + 0.14), rot=(-20, sgn * 15, 0), bev=0.04)
        p('horn_tip', (0.1, 0.1, 0.14), mm('horn'), (sgn * 0.34, 0.18, Hd.top + 0.34), rot=(-30, sgn * 20, 0))
        b('cheek_fin', (0.1, 0.3, 0.3), mm('wing'), (sgn * 0.6, 0.1, zc + 0.5), rot=(0, sgn * 20, 0), bev=0.03)
    p('smile', (0.24, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.3, zc + 0.2))
    eyes(Hd, 0.32, 0.26, 0.14, iris='#ffe68a', glow='#ffe68a', lash=True, brow=None)
    grid(Hd, 't', 3, 2, mm('dark'), (0.1, 0.1), name='head_scale', span=(0.6, 0.6))
    # wide star-map wings: three membrane panels fanning up and out
    for sgn, n in LR:
        nm = 'wing_' + n
        sg(nm, 'body', (sgn * 0.4, 0.5, zc - 0.2))
        a.wings.append(nm)
        for j, ang in enumerate((20, 45, 70)):
            r = math.radians(ang)
            ln = 1.6 - 0.25 * j
            cx, cz = sgn * (0.4 + math.cos(r) * ln * 0.5), zc - 0.2 + math.sin(r) * ln * 0.5
            b('wing_bone', (ln, 0.1, 0.1), mm('main'), (cx, 0.5, cz + 0.2), rot=(0, -sgn * ang, 0), bev=0.02)
            b('wing_panel', (ln * 0.9, 0.06, 0.5), mm('wing'), (cx, 0.52, cz - 0.08), rot=(0, -sgn * ang, 0), bev=0.02)
            p('wing_edge', (ln * 0.8, 0.07, 0.06), mm('accent'), (cx, 0.52, cz - 0.33), rot=(0, -sgn * ang, 0))
            p('wing_claw', (0.1, 0.1, 0.14), mm('horn'), (sgn * (0.4 + math.cos(r) * ln), 0.5, zc - 0.2 + math.sin(r) * ln + 0.2))
    use('body')
    # tail curled along the moon rim
    sg('tail', 'body', (0.3, 0.5, zc - 0.9))
    a.tail = ['tail']
    for i in range(5):
        th = math.radians(280 + i * 14)
        s = 0.36 - 0.05 * i
        b('tail', (s, s, s), mm('main'), (math.cos(th) * (R - 0.3), 0.1, zc + 0.2 + math.sin(th) * (R - 0.3)), bev=0.05)
    p('tail_tip', (0.24, 0.1, 0.24), mm('accent'), (math.cos(math.radians(350)) * (R - 0.3), 0.1, zc + 0.2 + math.sin(math.radians(350)) * (R - 0.3)), rot=(0, 45, 0))
    # rarity 6: constellation dots on the wings, moon-tip stars, crown, two orbits, red aura
    for sgn, n in LR:
        use('wing_' + n)
        for j, ang in enumerate((20, 45, 70)):
            r = math.radians(ang)
            ln = 1.6 - 0.25 * j
            for t in range(3):
                q = 0.35 + t * 0.25
                p('wing_star', (0.1, 0.1, 0.1), mm('star' if (t + j) % 2 else 'glow2'), (sgn * (0.4 + math.cos(r) * ln * q), 0.48, zc - 0.28 + math.sin(r) * ln * q), rot=(0, 45, 0))
    sg('glow', 'body', (0, 0.35, zc + 0.2))
    a.glow.append('glow')
    for th_ in (150, 390):
        th = math.radians(th_)
        p('moon_tip_star', (0.24, 0.24, 0.24), mm('glow'), (math.cos(th) * R, 0.35, zc + 0.2 + math.sin(th) * R + 0.3), rot=(45, 45, 0))
    for i in range(5):
        th = math.radians(200 + i * 35)
        p('moon_glow', (0.12, 0.06, 0.12), mm('glow'), (math.cos(th) * R, -0.12, zc + 0.2 + math.sin(th) * R), rot=(0, 45, 0))
    halo_kit(Hd, 'glow', r=0.4, n=6, dz=0.75, kind='crown')
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc - 0.4), Hit=(0, 0.2, zc))
    orbit_kit((0, 0.3, zc + 0.2), 2.6, 5, 'star', 'glow', size=0.16, dz=0.5, shape='cross')
    orbit_kit((0, 0.3, zc - 0.6), 2.2, 8, 'glow2', 'glow', size=0.1, name='orbit2', dz=0.2, shape='gem')
    aura_kit(2.2, 6, motes=12, mote_col='glow', height=3.6, style='double')
    return finish(a)


ANIMALS = dict(nebula_tardigrade=nebula_tardigrade, comet_fox=comet_fox, astral_starfish=astral_starfish, stellar_stag=stellar_stag,
               orbital_jellyfish=orbital_jellyfish, astral_dragon=astral_dragon)
