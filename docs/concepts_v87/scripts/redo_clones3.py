# Third look-alike pass (after the 150 contact sheet): new body plans for 10 animals. Spliced into the biome files.
from redo_dragons import splice

FENNEC = r'''
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
    use('body')
    sg('tail', 'body', (0.2, 0.6, 0.25))
    a.tail = ['tail']
    for j in range(5):
        ang = math.radians(90 - j * 45)
        b('tail', (0.3, 0.3, 0.26), mm('main' if j < 4 else 'dark'), (math.cos(ang) * 0.5, 0.3 + math.sin(ang) * 0.45 - 0.2, 0.14), bev=0.08)
    return finish(a)
'''

JERBOA = r'''
def dune_jerboa(row):
    """jerboa: a tiny round ball of a body perched high on two very long thin hind legs, big ROUND mouse ears,
    a super long thin tail arching up over its back with a black-and-white tuft above its head"""
    a = start(row, dict(main='#e8c48a', belly='#fff8e6', dark='#7a5636', accent='#c89a5c', ear_in='#ffb8b0'), 2.6)
    LEG = 0.9
    zb = LEG + 0.4
    sg('body', 'root', (0, 0.1, zb))
    B = b('body', (0.8, 0.8, 0.8), mm('main'), (0, 0.1, zb), bev=0.3)
    b('belly', (0.56, 0.1, 0.56), mm('belly'), (0, -0.3, zb - 0.06), bev=0.06)
    grid(B, 'k', 3, 2, mm('accent'), (0.1, 0.1), name='back_band', span=(0.6, 0.5))
    grid(B, 'l', 2, 2, mm('accent'), (0.08, 0.08), name='side_dot', span=(0.5, 0.5))
    grid(B, 'r', 2, 2, mm('accent'), (0.08, 0.08), name='side_dot', span=(0.5, 0.5))
    grid(B, 't', 2, 2, mm('dark'), (0.08, 0.08), name='top_dot', span=(0.5, 0.5))
    accessory('necklace', Box((0, -0.1, zb + 0.3), (0.6, 0.6, 0.2)), '#e8782a', '#5ae8e0', z=zb + 0.26)
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.25, 0.2, zb - 0.3))
        a.legs.append(nm)
        b('thigh', (0.22, 0.36, 0.36), mm('main'), (sgn * 0.3, 0.25, zb - 0.32), bev=0.06)
        b('stilt', (0.08, 0.08, LEG - 0.1), mm('main'), (sgn * 0.3, 0.2, (LEG - 0.1) / 2 + 0.1), bev=0.02)
        p('ankle', (0.1, 0.1, 0.1), mm('accent'), (sgn * 0.3, 0.2, 0.5))
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
'''

DEER = r'''
def deer(row):
    """a resting deer lying down: belly on the ground, all four legs folded under, neck up, head tilted, white spots, two little prong antlers"""
    a = start(row, dict(main='#b8743a', belly='#fff2dc', dark='#5a3418', accent='#e8c48a', antler='#f0e0c0'), 2.4)
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
    tail_kit('pom', 'body', (0, 1.25, 0.5), 'main', 'belly', size=0.18)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.6, 0.8), Hit=(0, 0.4, 0.7))
    return finish(a)
'''

MEGADEER = r'''
def megadeer(row):
    """giant deer whose antlers are a little TREE: two trunks branching up into a leafy crown with a bird nest, shaggy neck mane"""
    a = start(row, dict(main='#8a6240', belly='#e8d0a8', dark='#3a2414', accent='#c89a5c', bark='#6a4a30', leaf='#5aa83a', leaf2='#8ac84a',
                        nest='#a8784a', egg='#a8e0ff'), 3.0)
    B, Hd = quad(bw=1.0, bl=1.6, bh=0.9, legh=0.9, lw=0.26, hw=0.8, hd=0.8, hh=0.7, head_up=0.7, toe='dark', head_fwd=0.2, hoof='dark')
    use('body')
    grid(B, 'k', 2, 2, mm('belly'), (0.14, 0.14), name='rump_patch', span=(0.6, 0.6))
    for j in range(6):
        p('mane', (0.3, 0.2, 0.3), mm('accent'), (0, B.front + 0.05 + j * 0.06, B.top - 0.2 - j * 0.06))
    use('head')
    mz = muzzle(Hd, (0.36, 0.3, 0.24), -0.24, 'belly', nose=(0.14, 0.08, 0.08))
    eyes(Hd, 0.32, 0.25, 0.1, iris='#3a2414', lash=True, brow='#3a2414')
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.26, Hd.front - 0.012, Hd.c.z - 0.12))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.4, Hd.c.y, Hd.top - 0.1))
        a.ears.append(nm)
        b('ear', (0.3, 0.1, 0.16), mm('main'), (sgn * 0.52, Hd.c.y, Hd.top - 0.06), rot=(0, sgn * -20, 0), bev=0.03)
    # tree antlers (the silhouette)
    use('head')
    for sgn in (-1, 1):
        b('trunk', (0.14, 0.14, 0.9), mm('bark'), (sgn * 0.25, Hd.c.y, Hd.top + 0.42), rot=(0, sgn * 15, 0), bev=0.03)
        b('branch', (0.1, 0.1, 0.6), mm('bark'), (sgn * 0.55, Hd.c.y, Hd.top + 0.95), rot=(0, sgn * 45, 0), bev=0.02)
        b('branch2', (0.1, 0.1, 0.5), mm('bark'), (sgn * 0.2, Hd.c.y, Hd.top + 1.1), rot=(0, -sgn * 20, 0), bev=0.02)
    for i, (x, z, s) in enumerate(((-0.8, 1.3, 0.6), (0.8, 1.3, 0.6), (-0.35, 1.55, 0.7), (0.35, 1.55, 0.7), (0.0, 1.85, 0.6),
                                   (-1.1, 1.0, 0.4), (1.1, 1.0, 0.4))):
        b('leaves', (s, s * 0.8, s * 0.7), mm('leaf' if i % 2 else 'leaf2'), (x, Hd.c.y, Hd.top + z), bev=0.1)
    b('nest', (0.4, 0.4, 0.16), mm('nest'), (0.0, Hd.c.y, Hd.top + 2.18), bev=0.04)
    for j in range(3):
        p('egg', (0.1, 0.1, 0.12), mm('egg'), ((j - 1) * 0.1, Hd.c.y, Hd.top + 2.28))
    for j in range(5):
        p('leaf_bit', (0.12, 0.12, 0.06), mm('leaf2'), (-0.9 + j * 0.45, Hd.c.y - 0.3, Hd.top + 1.1 + 0.15 * (j % 2)))
    use('body')
    tail_kit('pom', 'body', a.tail_j, 'main', 'belly', size=0.2)
    return finish(a)
'''

WOLF = r'''
def wolf(row):
    """wolf frozen mid-leap: body stretched long and level, front legs reaching far forward, hind legs kicked back,
    ears flat back, tail streaming straight behind, mouth open in a happy pant"""
    a = start(row, dict(main='#7a8494', belly='#e8ecf0', dark='#3a3e48', accent='#b8c0cc', tongue='#ff7a8a'), 2.6)
    zb = 1.1
    sg('body', 'root', (0, 0.3, zb))
    B = b('body', (0.8, 1.9, 0.7), mm('main'), (0, 0.4, zb), rot=(4, 0, 0), bev=0.18)
    b('belly', (0.6, 1.5, 0.1), mm('belly'), (0, 0.4, zb - 0.36), bev=0.04)
    b('chest_ruff', (0.84, 0.5, 0.8), mm('accent'), (0, -0.4, zb), bev=0.14)
    grid(B, 't', 3, 6, mm('dark'), (0.08, 0.08), name='saddle', span=(0.6, 0.8))
    grid(B, 'l', 4, 2, mm('accent'), (0.08, 0.08), name='side_fur', span=(0.8, 0.5))
    grid(B, 'r', 4, 2, mm('accent'), (0.08, 0.08), name='side_fur', span=(0.8, 0.5))
    for sgn, n in LR:
        nm = 'leg_f' + n
        sg(nm, 'body', (sgn * 0.26, -0.4, zb - 0.2))
        a.legs.append(nm)
        b('front_leg', (0.2, 0.9, 0.2), mm('main'), (sgn * 0.26, -0.9, zb - 0.45), rot=(-30, 0, 0), bev=0.04)
        p('front_paw', (0.22, 0.26, 0.14), mm('belly'), (sgn * 0.26, -1.35, zb - 0.72))
        nm = 'leg_b' + n
        sg(nm, 'body', (sgn * 0.28, 1.1, zb - 0.1))
        a.legs.append(nm)
        b('thigh', (0.28, 0.5, 0.4), mm('main'), (sgn * 0.3, 1.2, zb - 0.2), bev=0.06)
        b('hind_leg', (0.18, 0.9, 0.18), mm('main'), (sgn * 0.3, 1.7, zb - 0.55), rot=(35, 0, 0), bev=0.04)
        p('hind_paw', (0.2, 0.26, 0.12), mm('belly'), (sgn * 0.3, 2.1, zb - 0.85))
    sg('head', 'body', (0, -0.6, zb + 0.2))
    Hd = b('head', (0.8, 0.7, 0.66), mm('main'), (0, -0.95, zb + 0.35), bev=0.14)
    mz = muzzle(Hd, (0.4, 0.4, 0.26), -0.3, 'belly', nose=(0.14, 0.08, 0.08), nose_mat='dark')
    p('open_mouth', (0.3, 0.06, 0.12), mm('dark'), (0, mz.front - 0.01, mz.bot + 0.02))
    p('tongue', (0.14, 0.2, 0.06), mm('tongue'), (0.04, mz.front - 0.08, mz.bot - 0.04))
    eyes(Hd, 0.3, 0.25, 0.14, iris='#ffd84a', brow='#3a3e48', tilt=-6)
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.28, Hd.front - 0.012, zb + 0.24))
        p('cheek_fur', (0.12, 0.2, 0.2), mm('belly'), (sgn * 0.44, -1.0, zb + 0.24))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.24, -0.9, Hd.top))
        a.ears.append(nm)
        b('ear_flat', (0.2, 0.4, 0.12), mm('dark'), (sgn * 0.26, -0.7, Hd.top + 0.02), rot=(-30, 0, sgn * 15), bev=0.03)
    grid(Hd, 't', 2, 2, mm('dark'), (0.08, 0.08), name='brow_mark', span=(0.5, 0.5))
    use('body')
    sg('tail', 'body', (0, 1.35, zb + 0.15))
    a.tail = ['tail']
    for j in range(4):
        b('tail', (0.3 - 0.02 * j, 0.4, 0.3 - 0.02 * j), mm('main' if j < 3 else 'belly'), (0, 1.55 + j * 0.36, zb + 0.2 + 0.04 * j), bev=0.08)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.7, zb), Hit=(0, 0.4, zb + 0.35))
    return finish(a)
'''

LYNX = r'''
def lynx(row):
    """lynx as a cat-loaf: a low rectangular loaf with paws tucked in, a huge fan-shaped fur ruff framing the face,
    very long black ear tufts, stubby black-tipped bobtail; glowing rune spots"""
    a = start(row, dict(main='#d8a868', belly='#fff2dc', dark='#3a2a1a', accent='#b8823a', ruff='#f4e4c8', **{'*glow': '#7af0d0'}), 2.2)
    sg('body', 'root', (0, 0.3, 0.45))
    B = b('loaf', (1.2, 1.6, 0.85), mm('main'), (0, 0.4, 0.43), bev=0.22)
    b('loaf_top', (0.9, 1.3, 0.2), mm('main'), (0, 0.45, 0.92), bev=0.08)
    grid(B, 'l', 4, 2, mm('dark'), (0.08, 0.08), name='spot', span=(0.8, 0.5))
    grid(B, 'r', 4, 2, mm('dark'), (0.08, 0.08), name='spot', span=(0.8, 0.5))
    grid(B, 'k', 3, 2, mm('dark'), (0.08, 0.08), name='spot', span=(0.6, 0.5))
    grid(Box((0, 0.45, 0.92), (0.9, 1.3, 0.2)), 't', 3, 4, mm('accent'), (0.1, 0.1), name='back_stripe', span=(0.7, 0.8))
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.3, -0.3, 0.15))
        a.legs.append(nm)
        b('tucked_paw', (0.3, 0.3, 0.16), mm('belly'), (sgn * 0.26, -0.42, 0.08), bev=0.06)
        for t in range(3):
            p('toe', (0.06, 0.04, 0.05), mm('accent'), (sgn * 0.26 + (t - 1) * 0.08, -0.58, 0.06))
    sg('head', 'body', (0, -0.3, 0.8))
    Hd = b('head', (0.8, 0.66, 0.66), mm('main'), (0, -0.45, 1.05), bev=0.14)
    # the fan ruff behind the face (the silhouette)
    for k_ in range(11):
        ang = math.radians(-20 + k_ * 22)
        p('ruff', (0.26, 0.12, 0.3), mm('ruff' if k_ % 2 else 'belly'), (math.cos(ang) * 0.6, -0.3, 1.0 - math.sin(ang) * 0.2 + (0 if k_ in (0, 10) else 0.0) - 0.18 + abs(math.sin(ang)) * 0.0),
          rot=(0, -math.degrees(ang) + 90, 0))
    for sgn in (-1, 1):
        for j in range(3):
            p('side_ruff', (0.2, 0.12, 0.3 - 0.06 * j), mm('ruff'), (sgn * (0.5 + 0.1 * j), -0.32, 0.86 - 0.12 * j), rot=(0, sgn * (20 + 20 * j), 0))
    mz = muzzle(Hd, (0.34, 0.24, 0.22), -0.24, 'belly', nose=(0.12, 0.06, 0.08))
    eyes(Hd, 0.32, 0.25, 0.12, iris='#7af0d0', glow='#7af0d0', lash=True, brow='#3a2a1a', tilt=8)
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.28, -0.45, Hd.top))
        a.ears.append(nm)
        b('ear', (0.2, 0.1, 0.3), mm('main'), (sgn * 0.28, -0.45, Hd.top + 0.14), bev=0.03)
        p('ear_tuft', (0.06, 0.06, 0.5), mm('dark'), (sgn * 0.28, -0.45, Hd.top + 0.52))
        p('ear_tuft_tip', (0.08, 0.08, 0.08), mm('dark'), (sgn * 0.3, -0.45, Hd.top + 0.8))
        for j in range(3):
            p('whisker', (0.28, 0.02, 0.02), mm('dark'), (sgn * 0.36, Hd.front - 0.1, 0.96 + (j - 1) * 0.04), rot=(0, sgn * (j - 1) * 10, 0))
    use('body')
    sg('tail', 'body', (0, 1.2, 0.5))
    a.tail = ['tail']
    b('bobtail', (0.24, 0.3, 0.24), mm('main'), (0, 1.3, 0.55), bev=0.06)
    p('bobtail_tip', (0.2, 0.12, 0.2), mm('dark'), (0, 1.48, 0.58))
    # rarity 4: glowing rune spots on the back (glow segment)
    sg('glow', 'body', (0, 0.45, 1.0))
    a.glow.append('glow')
    for j in range(5):
        p('rune_spot', (0.12, 0.12, 0.05), mm('glow'), ((j % 2 - 0.5) * 0.3, 0.0 + j * 0.24, 1.03), rot=(0, 0, 45))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.6, 0.5), Hit=(0, 0.4, 0.9))
    aura_kit(1.4, 4, motes=8, mote_col='glow', height=1.6)
    return finish(a)
'''

AFOX = r'''
def amethyst_fox(row):
    """amethyst fox with FIVE crystal tails spread behind it in a tall fan like a peacock, small slim body, crystal ear tips"""
    a = start(row, dict(main='#9a6ad8', belly='#f0e4ff', dark='#4a2a7a', accent='#c8a8ff', crystal='#e0c8ff',
                        **{'*glow': '#d8a8ff', '*glow2': '#ff9ae8'}), 2.8)
    B, Hd = quad(bw=0.7, bl=1.1, bh=0.6, legh=0.5, lw=0.18, hw=0.9, hd=0.76, hh=0.72, toe='dark', head_fwd=0.2)
    use('head')
    mz = muzzle(Hd, (0.32, 0.3, 0.22), -0.26, 'belly', nose=(0.1, 0.06, 0.08), nose_mat='dark')
    eyes(Hd, 0.34, 0.25, 0.1, iris='#4a2a7a', lash=True, brow='#4a2a7a', tilt=10)
    ears(Hd, 'point', 'main', 'pink', tip='crystal', x=0.32, h=0.5, w=0.28, lean=10)
    use('body')
    grid(B, 't', 2, 3, mm('accent'), (0.08, 0.08), name='back_gem', span=(0.5, 0.7), rot=(0, 0, 45))
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
'''

PELICAN = r'''
def lagoon_pelican(row):
    """pelican floating with its wings folded: a round boat-shaped body, a short neck and a HUGE beak whose pouch hangs down
    full of water with a little fish peeking out; webbed feet dangling"""
    zc = 0.8
    a = start(row, dict(main='#f4f4f0', belly='#ffffff', dark='#3a4a5a', accent='#ffb84a', pouch='#ffa86a', wing='#c8d0d8', fish='#5ab8e8',
                        water='#a8e0ff'), 2.4, hover=2.2, z0=zc)
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
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc), Hit=(0, 0.4, zc + 0.4))
    return finish(a)
'''

OWL = r'''
def moon_owl(row):
    """moon owl: a perfectly round puffball owl with tiny folded wings, a big heart-shaped face disc, long ear tufts,
    perched on a short floating branch it grips with both feet"""
    zc = 0.9
    a = start(row, dict(main='#c8d0e8', belly='#f4f6ff', dark='#3a3e5a', accent='#ffe14a', disc='#ffffff', branch='#6a5a4a', leaf='#7ab8a8'),
              2.2, hover=2.4, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (1.2, 1.1, 1.2), mm('main'), (0, 0.1, zc), bev=0.42)
    b('belly', (0.8, 0.1, 0.8), mm('belly'), (0, -0.46, zc - 0.15), bev=0.2)
    for j in range(3):
        for k_ in range(3):
            p('chevron', (0.12, 0.04, 0.06), mm('dark'), ((k_ - 1) * 0.2 + (0.1 if j % 2 else 0), -0.52, zc - 0.35 + j * 0.18))
    grid(B, 'k', 3, 3, mm('dark'), (0.08, 0.08), name='back_spot', span=(0.6, 0.6))
    for sgn, n in LR:
        nm = 'wing_' + n
        sg(nm, 'body', (sgn * 0.6, 0.1, zc + 0.2))
        a.wings.append(nm)
        b('tiny_wing', (0.14, 0.6, 0.66), mm('dark'), (sgn * 0.62, 0.15, zc - 0.05), bev=0.08)
        for j in range(3):
            p('wing_bar', (0.15, 0.08, 0.5), mm('main'), (sgn * 0.63, -0.05 + j * 0.2, zc - 0.05))
    # heart face disc (the silhouette) and ear tufts
    sg('head', 'body', (0, -0.3, zc + 0.3))
    Hd = Box((0, 0.0, zc + 0.3), (1.0, 1.1, 0.7), 'head')
    b('face_disc', (1.0, 0.08, 0.7), mm('disc'), (0, -0.56, zc + 0.3), bev=0.06)
    for sgn in (-1, 1):
        b('disc_lobe', (0.5, 0.08, 0.5), mm('disc'), (sgn * 0.26, -0.56, zc + 0.62), bev=0.08)
    eyes(Box((0, -0.03, zc + 0.36), (1.0, 1.1, 0.7), 'head'), 0.46, 0.24, 0.0, iris='#ffe14a', brow=None)
    p('beak', (0.12, 0.1, 0.16), mm('accent'), (0, -0.62, zc + 0.14))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.34, -0.62, zc + 0.12))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.4, 0.0, zc + 0.6))
        a.ears.append(nm)
        b('ear_tuft', (0.16, 0.16, 0.5), mm('dark'), (sgn * 0.42, 0.0, zc + 0.9), rot=(0, sgn * 18, 0), bev=0.03)
    p('moon_mark', (0.14, 0.06, 0.2), mm('accent'), (0, -0.62, zc + 0.58), rot=(0, 30, 0))
    # perch branch gripped by the feet
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.22, 0.0, zc - 0.5))
        a.legs.append(nm)
        for t in range(3):
            p('talon', (0.05, 0.12, 0.06), mm('accent'), (sgn * 0.22 + (t - 1) * 0.06, -0.08, zc - 0.66))
    b('branch', (1.6, 0.18, 0.18), mm('branch'), (0, 0.0, zc - 0.72), bev=0.04)
    for sgn in (-1, 1):
        p('branch_leaf', (0.24, 0.14, 0.06), mm('leaf'), (sgn * 0.7, -0.05, zc - 0.62), rot=(0, sgn * 20, 0))
        p('branch_end', (0.2, 0.2, 0.2), mm('branch'), (sgn * 0.85, 0.0, zc - 0.72))
    sg('tail', 'body', (0, 0.6, zc - 0.3))
    a.tail = ['tail']
    for j in range(3):
        p('tail_feather', (0.14, 0.3, 0.06), mm('dark'), ((j - 1) * 0.14, 0.7, zc - 0.45))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, -0.3, zc + 0.3), Chest=(0, -0.6, zc - 0.1), Hit=(0, 0.1, zc + 0.4))
    return finish(a)
'''

CONDOR = r'''
def canyon_condor(row):
    """canyon condor perched hunched on a red rock: wings folded and draped over its back like a big cloak, a long bald pink neck
    hanging forward out of a fluffy white ruff, a heavy hooked beak"""
    zc = 1.0
    a = start(row, dict(main='#2a2a30', belly='#4a4a52', dark='#141418', accent='#ff8aa0', ruff='#ffffff', beak='#e8d8b8', rock='#c8643a',
                        rock2='#a84a2a', **{'*glow': '#ffd84a', '*glow2': '#ff8a3a'}), 2.6, hover=2.0, z0=zc)
    sg('body', 'root', (0, 0.3, zc))
    B = b('body', (1.2, 1.2, 1.3), mm('main'), (0, 0.4, zc + 0.1), rot=(-15, 0, 0), bev=0.24)
    # cloak wings (the silhouette)
    for sgn, n in LR:
        nm = 'wing_' + n
        sg(nm, 'body', (sgn * 0.6, 0.2, zc + 0.6))
        a.wings.append(nm)
        b('cloak_wing', (0.24, 1.5, 1.4), mm('main'), (sgn * 0.68, 0.55, zc + 0.1), rot=(-15, 0, sgn * 8), bev=0.1)
        for j in range(5):
            p('primary', (0.25, 0.3, 0.12), mm('belly'), (sgn * 0.7, 0.9 + j * 0.1, zc - 0.55 + j * 0.05))
            p('covert_stripe', (0.26, 0.5, 0.06), mm('ruff'), (sgn * 0.71, 0.4 + j * 0.15, zc + 0.5 - j * 0.12))
    grid(B, 'k', 3, 4, mm('belly'), (0.1, 0.1), name='back_feather', span=(0.6, 0.7))
    # ruff, bald neck and head
    for k_ in range(12):
        ang = math.radians(k_ * 30)
        p('ruff', (0.3, 0.3, 0.26), mm('ruff'), (math.cos(ang) * 0.45, -0.2 + math.sin(ang) * 0.3, zc + 0.85), rot=(0, 0, k_ * 30))
    sg('head', 'body', (0, -0.3, zc + 0.8))
    for j in range(3):
        b('neck', (0.26, 0.3, 0.3), mm('accent'), (0, -0.4 - j * 0.15, zc + 0.85 - j * 0.12), bev=0.06)
    Hd = b('head', (0.6, 0.6, 0.5), mm('accent'), (0, -0.85, zc + 0.6), bev=0.14)
    b('beak', (0.26, 0.4, 0.3), mm('beak'), (0, Hd.front - 0.16, zc + 0.52), rot=(20, 0, 0), bev=0.05)
    p('beak_hook', (0.14, 0.12, 0.16), mm('dark'), (0, Hd.front - 0.36, zc + 0.38))
    p('wattle', (0.2, 0.1, 0.16), mm('rock'), (0, Hd.front + 0.1, Hd.top + 0.04))
    eyes(Hd, 0.32, 0.26, 0.12, iris='#ff5a3a', brow='#141418', tilt=8)
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.26, -0.85, Hd.top))
        a.ears.append(nm)
        p('wrinkle', (0.06, 0.4, 0.06), mm('rock'), (sgn * 0.31, -0.85, Hd.top - 0.1))
    # the perch rock and gripping feet
    use('body')
    b('rock', (1.6, 1.4, 0.6), mm('rock'), (0, 0.4, zc - 1.0), bev=0.14)
    b('rock_top', (1.1, 1.0, 0.24), mm('rock2'), (0, 0.4, zc - 0.62), bev=0.06)
    grid(Box((0, 0.4, zc - 1.0), (1.6, 1.4, 0.6)), 'f', 3, 2, mm('rock2'), (0.14, 0.14), name='rock_crack', span=(0.8, 0.6))
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.3, 0.2, zc - 0.45))
        a.legs.append(nm)
        p('leg', (0.12, 0.12, 0.2), mm('beak'), (sgn * 0.3, 0.2, zc - 0.48))
        for t in range(3):
            p('talon', (0.06, 0.16, 0.06), mm('dark'), (sgn * 0.3 + (t - 1) * 0.08, 0.05, zc - 0.55))
    sg('tail', 'body', (0, 1.0, zc - 0.3))
    a.tail = ['tail']
    for j in range(5):
        p('tail_feather', (0.14, 0.5, 0.06), mm('main'), ((j - 2) * 0.13, 1.25, zc - 0.4))
    # rarity 5: glowing feather tips on the cloak, star orbit, yellow aura
    sg('glow', 'body', (0, 0.6, zc - 0.2))
    a.glow.append('glow')
    for sgn in (-1, 1):
        for j in range(5):
            p('feather_glow', (0.06, 0.12, 0.08), mm('glow' if j % 2 else 'glow2'), (sgn * 0.83, 0.85 + j * 0.12, zc - 0.5 + j * 0.05))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, zc + 0.3), Hit=(0, 0.4, zc + 0.5))
    orbit_kit((0, 0.4, zc + 0.4), 2.0, 6, 'glow', 'glow2', size=0.14, dz=0.4, shape='star')
    aura_kit(1.8, 5, motes=10, mote_col='glow', height=2.4, style='double')
    return finish(a)
'''

if __name__ == '__main__':
    splice('biome_07.py', 'fennec', FENNEC)
    splice('biome_07.py', 'dune_jerboa', JERBOA)
    splice('biome_03.py', 'deer', DEER)
    splice('biome_04.py', 'megadeer', MEGADEER)
    splice('biome_02.py', 'wolf', WOLF)
    splice('biome_02.py', 'lynx', LYNX)
    splice('biome_15.py', 'amethyst_fox', AFOX)
    splice('biome_11.py', 'lagoon_pelican', PELICAN)
    splice('biome_16.py', 'moon_owl', OWL)
    splice('biome_06.py', 'canyon_condor', CONDOR)
    print('spliced')
