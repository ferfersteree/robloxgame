# Biome 6 - Red Canyons: red sandstone, trails, arches
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 6
GROUND = '#d98a5c'
SKY = '#ffdcbc'
THEME = dict(bits=['#c8683a', '#8aa84a'], dust='#ecc09a', glow='#ff6a3a', splash='#ffd0b0', bit_name='песок и колючки')
FOOT = dict(canyon_condor=1.7, redthorn_lizard=1.35)
BUSH_NAME = 'колючий куст у валунов красного песчаника с кактусами и каменной аркой'


def bush():
    B = begin_bush(NN)
    r1 = mat('rock', '#c8683a')
    r2 = mat('rock2', '#e08a52')
    r3 = mat('rock3', '#a8502c')
    sand = mat('sand', '#f0c090')
    th1 = mat('thorn', '#8aa84a')
    th2 = mat('thorn2', '#6a8a36')
    twig = mat('twig', '#8a6a4a')
    spike = mat('spike', '#f6ead2', 'smooth')
    cac = mat('cactus', '#5aa860')
    cac2 = mat('cactus2', '#458a4c')
    fl = mat('flower', '#ff5a8a')
    gem = mat('gem', '#ff6a3a', 'neon', 1.8)
    # layered sandstone boulders (strata bands)
    for i, (x, y, w, d, h) in enumerate(((-2.2, 0.4, 2.4, 2.0, 2.6), (2.3, 0.5, 2.2, 1.9, 2.0), (0.2, 1.1, 2.6, 1.4, 3.4))):
        part('big', (x, y, 0.2), 'boulder_%d' % i)
        b('boulder', (w, d, h), r1, (x, y, h / 2), bev=0.14)
        for j in range(3):
            p('strata', (w + 0.04, d + 0.04, 0.16), (r2, r3, sand)[j], (x, y, h * (0.25 + 0.25 * j)))
        b('boulder_top', (w * 0.7, d * 0.7, 0.4), r2, (x + 0.1, y, h + 0.18), bev=0.1)
        p('crack', (0.06, 0.05, h * 0.4), r3, (x + w * 0.2, y - d / 2 - 0.01, h * 0.5))
    # little arch between the back boulders
    part('big', (1.2, 1.0, 3.0), 'arch')
    b('arch', (2.4, 0.8, 0.6), r2, (1.3, 0.9, 3.5), rot=(0, 10, 0), bev=0.12)
    p('arch_strata', (2.44, 0.84, 0.12), r3, (1.3, 0.9, 3.5), rot=(0, 10, 0))
    b('arch_cap', (1.2, 0.6, 0.3), r1, (1.0, 0.9, 3.9), rot=(0, 10, 0), bev=0.08)
    # thorn bush: twiggy stepped branches with white spikes and small leaves
    k_ = 0
    for (cx, cy, n, h0) in ((-0.9, -0.7, 5, 2.2), (0.4, -0.9, 6, 2.8), (1.6, -0.6, 5, 2.0), (-2.9, -0.8, 4, 1.5), (3.0, -0.6, 4, 1.4)):
        part('small', (cx, cy, 0.2), 'thorn_%d' % k_)
        for i in range(n):
            lean = (i - (n - 1) / 2) * 16
            h = h0 - 0.3 * abs(i - (n - 1) / 2)
            x = cx + math.sin(math.radians(lean)) * h / 2
            b('branch', (0.14, 0.14, h), twig, (x, cy + 0.12 * (i % 2), h / 2 + 0.1), rot=(0, lean, 0), bev=0.03)
            for j in range(3):
                z = 0.5 + j * h * 0.28
                xx = cx + math.sin(math.radians(lean)) * z
                p('leaf', (0.3, 0.2, 0.14), th1 if (i + j) % 2 else th2, (xx + 0.12, cy + 0.12 * (i % 2), z))
                p('spike', (0.22, 0.04, 0.04), spike, (xx - 0.14, cy + 0.12 * (i % 2), z + 0.1), rot=(0, 25, 0))
        k_ += 1
    # cacti
    for i, (x, y, s) in enumerate(((-3.2, 0.9, 1.0), (3.3, 0.9, 0.8), (-1.6, -1.5, 0.55))):
        part('small', (x, y, 0.1), 'cactus_%d' % i)
        b('cactus', (0.6 * s, 0.6 * s, 2.2 * s), cac, (x, y, 1.1 * s), bev=0.1)
        b('cactus_arm', (0.6 * s, 0.34 * s, 0.34 * s), cac, (x + 0.5 * s, y, 1.1 * s), bev=0.06)
        b('cactus_arm_up', (0.34 * s, 0.34 * s, 0.8 * s), cac, (x + 0.72 * s, y, 1.5 * s), bev=0.06)
        for j in range(3):
            p('cactus_rib', (0.08 * s, 0.62 * s, 2.0 * s), cac2, (x + (j - 1) * 0.2 * s, y, 1.1 * s))
        b('cactus_flower', (0.26 * s, 0.26 * s, 0.16 * s), fl, (x, y, 2.28 * s), bev=0.04)
        p('flower_core', (0.1 * s, 0.1 * s, 0.1 * s), mat('core', '#ffd84a'), (x, y, 2.38 * s))
    # pebbles with glowing veins + sand drift
    part('big', (0.3, -1.7, 0.05), 'drift')
    b('drift', (3.4, 0.9, 0.24), sand, (0.3, -1.7, 0.12), bev=0.08)
    for i, (x, y, s) in enumerate(((-0.6, -1.8, 0.5), (1.1, -1.9, 0.4), (2.2, -1.6, 0.6))):
        part('small', (x, y, 0.2), 'pebble_%d' % i)
        b('pebble', (0.9 * s, 0.8 * s, 0.7 * s), r3 if i % 2 else r1, (x, y, 0.24 + 0.3 * s), bev=0.1)
        p('vein', (0.4 * s, 0.05, 0.08), gem, (x, y - 0.4 * s, 0.3 + 0.3 * s), rot=(0, 25, 0))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def rock_hyrax(row):
    a = start(row, dict(main='#a8846a', belly='#e6cfae', dark='#5e4636', accent='#c8a482'), 1.38)
    B, Hd = quad(bw=0.92, bl=1.1, bh=0.72, legh=0.2, lw=0.22, hw=1.02, hd=0.86, hh=0.84, head_up=0.3, toe='dark', head_fwd=0.3)
    mz = muzzle(Hd, (0.4, 0.2, 0.26), -0.26, 'belly', nose=(0.15, 0.07, 0.1), teeth=1)
    cheeks(Hd, 'belly', (0.24, 0.2, 0.28), -0.24, whisk=3)
    eyes(Hd, 0.34, 0.25, 0.1, iris='#3a2414', brow='#5e4636', tilt=10, lash=True)
    ears(Hd, 'round', 'main', 'pink', x=0.4, h=0.18, w=0.24, lean=14)
    on(Hd, 'f', 0, 0.38, (0.2, 0.14), mm('accent'), name='fore_patch')
    use('body')
    on(B, 't', 0, 0.0, (0.3, 0.3), mm('accent'), name='back_gland', th=0.05)
    on(B, 't', 0, 0.0, (0.14, 0.14), mm('belly'), name='back_gland', th=0.07)
    spots(B, 'lr', 6, mm('dark'), 0.12, seed=3, name='fleck')
    spots(a.bx['rump'], 'tlr', 5, mm('accent'), 0.12, seed=4, name='fleck')
    fluff(a.bx['chest'], 'f', mm('accent'), 3, 0.9, 0.3)
    for sgn, n in LR:
        p('side_fluff', (0.06, 0.3, 0.2), mm('belly'), (sgn * (B.s.x / 2 + 0.02), B.c.y - 0.1, B.bot + 0.14))
        p('side_fluff', (0.06, 0.2, 0.14), mm('belly'), (sgn * (B.s.x / 2 + 0.02), B.c.y + 0.2, B.bot + 0.1))
    for ft in a.bx['feet']:
        p('pad', (ft.s.x * 0.6, 0.03, 0.05), mm('pink'), (ft.c.x, ft.back + 0.012, 0.05))
    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.14)
    return finish(a)


def mountain_goat(row):
    a = start(row, dict(main='#f4f0e6', belly='#ffffff', dark='#4a4038', accent='#d8d0c0', horn='#5a4a40'), 2.42)
    B, Hd = quad(bw=0.9, bl=1.2, bh=0.76, legh=0.6, lw=0.22, hw=1.02, hd=0.86, hh=0.9, neck=0.1, hoof='dark', hump=0.12, head_fwd=0.3)
    mz = muzzle(Hd, (0.4, 0.28, 0.28), -0.26, 'accent', nose=(0.16, 0.07, 0.1))
    b('beard', (0.24, 0.2, 0.34), mm('belly'), (0, Hd.front + 0.12, Hd.bot - 0.14), bev=0.05)
    p('beard_tip', (0.14, 0.14, 0.16), mm('accent'), (0, Hd.front + 0.12, Hd.bot - 0.36))
    cheeks(Hd, 'belly', (0.2, 0.18, 0.26), -0.26, whisk=0)
    eyes(Hd, 0.32, 0.25, 0.1, iris='#b08a2a', brow='#4a4038', tilt=-10)
    ears(Hd, 'long', 'main', 'pink', tip='accent', x=0.5, h=0.3, w=0.2, lean=70)
    # back-swept ringed horns
    use('head')
    for sgn, n in LR:
        for j in range(4):
            b('horn', (0.15 - 0.02 * j, 0.2, 0.2), mm('horn'), (sgn * (0.22 + 0.03 * j), Hd.c.y + 0.1 + j * 0.16, Hd.top + 0.1 + j * 0.12 - 0.03 * j * j), rot=(-25 - 12 * j, 0, 0), bev=0.04)
            p('horn_ring', (0.17 - 0.02 * j, 0.05, 0.22), mm('accent'), (sgn * (0.22 + 0.03 * j), Hd.c.y + 0.18 + j * 0.16, Hd.top + 0.14 + j * 0.12 - 0.03 * j * j), rot=(-25 - 12 * j, 0, 0))
    use('body')
    # shaggy coat: skirts on the flanks and "pantaloons" on the legs
    for sgn, n in LR:
        for j in range(4):
            p('skirt', (0.07, 0.26, 0.3 - 0.04 * (j % 2)), mm('accent'), (sgn * (B.s.x / 2 + 0.02), B.front + 0.16 + j * 0.28, B.bot + 0.12))
    fluff(a.bx['chest'], 'f', mm('accent'), 4, 0.95, 0.38, th=0.07)
    for i in range(3):
        b('wither_tuft', (0.3, 0.2, 0.16), mm('belly'), ((i - 1) * 0.26, B.front + 0.24, B.top + 0.18), bev=0.05)
    for ft in a.bx['feet']:
        p('pants', (ft.s.x + 0.08, ft.s.y + 0.04, 0.22), mm('accent'), (ft.c.x, ft.c.y + 0.02, 0.5))
        p('pants_tuft', (0.1, 0.06, 0.12), mm('belly'), (ft.c.x, ft.front + 0.0, 0.36))
    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.2)
    return finish(a)


def canyon_roadrunner(row):
    a = start(row, dict(main='#8a6a4a', belly='#f4e6c8', dark='#4a3626', accent='#3a6a9a', leg='#c8b060', beak='#5a4a40', beak_tip='#3a2e28'), 2.75)
    B, Hd = bird(bw=0.8, bl=1.2, bh=0.72, legh=0.86, lw=0.12, hw=0.84, hd=0.78, hh=0.74, neck=0.36, beak=(0.2, 0.62, 0.16),
                 wing=(0.14, 0.8, 0.46), ntail=0, head_mat='main', beak_low=True)
    use('head')
    # shaggy crest + bare blue-orange patch behind the eye
    for i in range(4):
        b('crest', (0.16, 0.16, 0.3 - 0.04 * i), mm('dark'), (0, Hd.c.y - 0.2 + i * 0.16, Hd.top + 0.12), rot=(-20 - 8 * i, 0, 0), bev=0.04)
    for sgn, n in LR:
        on(Hd, 'l' if sgn < 0 else 'r', -0.1, 0.1, (0.2, 0.12), mm('accent'), name='eye_patch')
        on(Hd, 'l' if sgn < 0 else 'r', 0.12, 0.1, (0.14, 0.1), setm('orange', '#ff8a3a'), name='eye_patch')
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.22))
    eyes(Hd, 0.4, 0.25, 0.14, iris='#c8782a', brow='#4a3626', tilt=-12)
    use('body')
    # streaked plumage (pattern) and a long cocked tail (the silhouette)
    stripes(B, 't', 5, mm('dark'), 0.08, name='streak', span=0.86)
    for sgn, n in LR:
        for j in range(4):
            p('streak', (0.04, 0.2, 0.3), mm('belly' if j % 2 else 'dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.3 + j * 0.2, B.c.z - 0.1))
    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('dark'), 4, 0.9, 0.34)
    sg('tail', 'body', (0, B.back + 0.1, B.c.z + 0.2))
    a.tail = ['tail']
    for i in range(3):
        b('tail_feather', (0.2 - 0.03 * i, 1.3 + 0.2 * (i == 1), 0.1), mm('dark' if i != 1 else 'main'), ((i - 1) * 0.16, B.back + 0.7, B.c.z + 0.56 + 0.03 * (i == 1)), rot=(28, 0, (i - 1) * 6), bev=0.03)
        p('tail_tip', (0.2, 0.2, 0.1), mm('belly'), ((i - 1) * 0.2, B.back + 1.3, B.c.z + 0.9), rot=(28, 0, 0))
        p('tail_band', (0.2, 0.12, 0.1), mm('belly'), ((i - 1) * 0.17, B.back + 0.9, B.c.z + 0.68), rot=(28, 0, 0))
    use('body')
    accessory('scarf', Box((0, B.front + 0.2, B.top + 0.2), (0.5, 0.5, 0.3)), '#e8443a', '#a82a2a', z=B.top + 0.2)
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(4):
            p('wing_spot', (0.04, 0.12, 0.1), mm('belly'), (sgn * (B.s.x / 2 + 0.13), B.c.y - 0.1 + j * 0.16, B.c.z + 0.1 - 0.06 * j))
        use('leg_' + n)
        for j in range(4):
            p('leg_scale', (0.14, 0.14, 0.04), mm('dark'), (sgn * B.s.x * 0.24, 0.15, 0.2 + j * 0.14))
    use('body')
    return finish(a)


def armadillo(row):
    a = start(row, dict(main='#c89a7a', belly='#f0d8c0', dark='#8a5a44', accent='#e0b898', shell='#b07a5c', **{'*glow': '#ff6a3a'}), 1.75)
    B, Hd = quad(bw=1.0, bl=1.3, bh=0.8, legh=0.22, lw=0.22, hw=0.9, hd=0.9, hh=0.8, head_up=0.16, toe='dark', head_fwd=0.5, rump=False, chest=False)
    mz = muzzle(Hd, (0.34, 0.4, 0.26), -0.24, 'accent', nose=(0.14, 0.07, 0.09), nose_mat='pink')
    cheeks(Hd, 'belly', (0.16, 0.14, 0.2), -0.28, whisk=0, tuft=False)
    eyes(Hd, 0.32, 0.25, 0.14, iris='#7a3a1a', glow='#ff6a3a', brow='#8a5a44', tilt=6)
    ears(Hd, 'long', 'accent', 'pink', tip='dark', x=0.34, h=0.42, w=0.2, lean=14)
    use('head')
    b('head_plate', (0.6, 0.6, 0.1), mm('shell'), (0, Hd.c.y + 0.04, Hd.top + 0.05), bev=0.03)
    for i in range(3):
        p('head_scale', (0.16, 0.16, 0.04), mm('dark'), ((i - 1) * 0.2, Hd.c.y - 0.1, Hd.top + 0.11))
    use('body')
    # banded shell: front shield, movable bands, rear shield (the silhouette)
    b('shield_f', (1.12, 0.44, 0.76), mm('shell'), (0, B.front + 0.2, B.c.z + 0.1), bev=0.1)
    b('shield_b', (1.12, 0.46, 0.74), mm('shell'), (0, B.back - 0.2, B.c.z + 0.08), bev=0.1)
    for j in range(4):
        y = B.front + 0.5 + j * 0.13
        b('band', (1.16, 0.12, 0.8 + 0.03 * (j % 2)), mm('dark' if j % 2 else 'shell'), (0, y, B.c.z + 0.12), bev=0.04)
    for f_, yy in (('f', B.front + 0.2), ('b', B.back - 0.2)):
        for i in range(3):
            for j in range(2):
                p('scale', (0.2, 0.16, 0.04), mm('accent'), ((i - 1) * 0.3, yy - 0.1 + j * 0.2, B.c.z + 0.5))
        for sgn, n in LR:
            for j in range(2):
                p('scale_side', (0.04, 0.16, 0.2), mm('accent'), (sgn * 0.57, yy - 0.1 + j * 0.2, B.c.z + 0.2))
    for i in range(5):
        for j in range(2):
            p('band_stud', (0.1, 0.06, 0.04), mm('accent'), ((i - 2) * 0.2, B.front + 0.5 + j * 0.26, B.c.z + 0.55))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_scale', (ft.s.x + 0.02, ft.s.y * 0.7, 0.05), mm('shell'), (ft.c.x, ft.c.y + 0.06, 0.2))
        p('leg_scale', (ft.s.x + 0.02, ft.s.y * 0.6, 0.04), mm('dark'), (ft.c.x, ft.c.y + 0.06, 0.27))
        p('claw_big', (0.08, 0.1, 0.06), mm('belly'), (ft.c.x, ft.front - 0.02, 0.04))
    use('body')
    tail_kit('long', 'body', (0, B.back - 0.02, B.c.z - 0.2), 'shell', 'dark', n=2, size=0.12, dark='dark')
    # rarity 4: glowing seams between the bands, glowing ear tips, sparks
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for j in range(3):
        y = B.front + 0.565 + j * 0.13
        p('seam', (1.18, 0.03, 0.82), mm('glow'), (0, y, B.c.z + 0.12))
    for sgn, n in LR:
        p('shield_gem', (0.05, 0.14, 0.14), mm('glow'), (sgn * 0.58, B.front + 0.2, B.c.z + 0.3), rot=(45, 0, 0))
        p('shield_gem', (0.05, 0.14, 0.14), mm('glow'), (sgn * 0.58, B.back - 0.2, B.c.z + 0.3), rot=(45, 0, 0))
        use('ear_' + n)
        p('ear_glow', (0.1, 0.1, 0.08), mm('glow'), (sgn * (0.34 * Hd.s.x + 0.07), Hd.c.y, Hd.top + 0.44))
        use('glow')
    use('body')
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=1.3)
    return finish(a)


def canyon_condor(row):
    """canyon condor perched hunched on a red rock: wings folded and draped over its back like a big cloak, a long bald pink neck
    hanging forward out of a fluffy white ruff, a heavy hooked beak"""
    zc = 1.0
    a = start(row, dict(main='#2a2a30', belly='#4a4a52', dark='#141418', accent='#ff8aa0', ruff='#ffffff', beak='#e8d8b8', rock='#c8643a',
                        rock2='#a84a2a', **{'*glow': '#ffd84a', '*glow2': '#ff8a3a'}), 2.3, hover=2.0, z0=zc)
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
    grid(B, 'f', 3, 3, mm('belly'), (0.1, 0.1), name='chest_feather', span=(0.6, 0.6))
    grid(B, 't', 3, 3, mm('belly'), (0.1, 0.1), name='shoulder_feather', span=(0.6, 0.6))
    for sgn in (-1, 1):
        for j in range(6):
            p('cloak_edge', (0.27, 0.12, 0.12), mm('dark'), (sgn * 0.72, -0.15 + j * 0.25, zc - 0.55 + j * 0.02))
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
    grid(Box((0, 0.4, zc - 1.0), (1.6, 1.4, 0.6)), 'l', 3, 2, mm('rock2'), (0.14, 0.14), name='rock_crack', span=(0.8, 0.6))
    grid(Box((0, 0.4, zc - 1.0), (1.6, 1.4, 0.6)), 'r', 3, 2, mm('rock2'), (0.14, 0.14), name='rock_crack', span=(0.8, 0.6))
    for j in range(9):
        p('pebble', (0.14, 0.14, 0.1), mm('rock2'), (-0.7 + j * 0.17, -0.35, zc - 1.25))
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
            p('feather_glow2', (0.06, 0.1, 0.06), mm('glow2'), (sgn * 0.83, 0.3 + j * 0.12, zc + 0.3 - j * 0.1))
            p('feather_glow', (0.06, 0.12, 0.08), mm('glow' if j % 2 else 'glow2'), (sgn * 0.83, 0.85 + j * 0.12, zc - 0.5 + j * 0.05))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, zc + 0.3), Hit=(0, 0.4, zc + 0.5))
    orbit_kit((0, 0.4, zc + 0.4), 2.0, 6, 'glow', 'glow2', size=0.14, dz=0.4, shape='star')
    aura_kit(1.8, 5, motes=10, mote_col='glow', height=2.4, style='double')
    return finish(a)


def redthorn_lizard(row):
    a = start(row, dict(main='#d86a3a', belly='#ffe0b0', dark='#8a3220', accent='#f09a4a', thorn='#b02a2a', horn='#fff0d8',
                        **{'*glow': '#ff5a2a', '*glow2': '#ffd21a', '*gold': '#ffd84a'}), 2.55)
    B, Hd = quad(bw=1.2, bl=1.6, bh=0.72, legh=0.34, lw=0.3, hw=1.24, hd=1.1, hh=0.9, head_up=0.3, toe='horn', head_fwd=0.4,
                 leg_fl=0.56, ntoe=4, leg_back_x=0.66)
    mz = muzzle(Hd, (0.7, 0.3, 0.32), -0.2, 'belly', nose=None, mouth=True, fangs=1, tongue=True)
    for sgn, n in LR:
        p('nostril', (0.07, 0.03, 0.05), mm('line'), (sgn * 0.16, mz.front - 0.008, mz.c.z + 0.1))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.46, Hd.front - 0.012, Hd.c.z - 0.2))
        # frill of thorns behind the cheeks
        for j in range(4):
            cn('frill', 0.1, 0.4 - 0.05 * j, mm('thorn'), (sgn * (Hd.s.x / 2 - 0.02), Hd.back - 0.1, Hd.c.z + 0.3 - j * 0.22), (sgn * 1, 0.5, 0.4 - 0.3 * j))
        p('frill_web', (0.08, 0.3, 0.7), mm('accent'), (sgn * (Hd.s.x / 2 + 0.03), Hd.back - 0.06, Hd.c.z))
    eyes(Hd, 0.33, 0.26, 0.14, iris='#b03a1a', glow='#ff5a2a', brow='#8a3220', tilt=-10)
    use('head')
    for i in range(3):
        cn('brow_thorn', 0.09, 0.3, mm('thorn'), ((i - 1) * 0.3, Hd.c.y - 0.1, Hd.top - 0.02), ((i - 1) * 0.4, -0.2, 1))
    use('body')
    # red thorns in three rows down the back and tail (the silhouette) + scale pattern
    for j in range(8):
        y = B.front + 0.14 + j * 0.2
        cn('thorn', 0.12, 0.5 - 0.02 * j, mm('thorn'), (0, y, B.top - 0.02), (0, 0.3, 1))
        for sgn, n in LR:
            cn('thorn_side', 0.08, 0.3, mm('thorn'), (sgn * 0.36, y + 0.1, B.top - 0.02), (sgn * 0.7, 0.3, 1))
    stripes(B, 'lr', 6, mm('dark'), 0.1, name='band', span=0.9)
    spots(B, 't', 6, mm('accent'), 0.16, seed=3, name='scale')
    spots(a.bx['rump'], 'lr', 4, mm('accent'), 0.14, seed=5, name='scale')
    fluff(a.bx['chest'], 'f', mm('accent'), 3, 0.9, 0.3)
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.1, 0.3))
        cn('elbow_thorn', 0.07, 0.24, mm('thorn'), (ft.c.x + (0.16 if ft.c.x > 0 else -0.16), ft.c.y + 0.14, 0.34), ((1 if ft.c.x > 0 else -1), 0.4, 0.5))
        p('claw_gold', (ft.s.x * 0.8, 0.06, 0.04), mm('gold'), (ft.c.x, ft.front, 0.03))
    use('body')
    tail_kit('long', 'body', (0, B.back + 0.1, B.c.z), 'main', 'thorn', n=3, size=0.22, dark='dark')
    for i, t in enumerate(a.tail):
        use(t)
        cn('tail_thorn', 0.1, 0.36 - 0.06 * i, mm('thorn'), (0, B.back + 0.3 + i * 0.43, B.c.z + 0.11 + i * 0.055), (0, 0.3, 1))
        cn('tail_thorn', 0.08, 0.26 - 0.04 * i, mm('thorn'), (0, B.back + 0.5 + i * 0.43, B.c.z + 0.14 + i * 0.075), (0, 0.3, 1))
    # rarity 6: molten glow under the thorns, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for j in range(8):
        y = B.front + 0.14 + j * 0.2
        p('thorn_base', (0.3, 0.16, 0.05), mm('glow' if j % 2 else 'glow2'), (0, y, B.top + 0.02))
    for sgn, n in LR:
        f = 'l' if sgn < 0 else 'r'
        for i in range(4):
            on(B, f, -0.36 + i * 0.24, -0.26, (0.14, 0.14), mm('glow'), th=0.035, name='flank_gem', rot=(45, 0, 0))
        on(a.bx['rump'], f, 0, 0.14, (0.2, 0.2), mm('glow2'), th=0.035, name='flank_gem', rot=(45, 0, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(3):
        p('brow_glow', (0.2, 0.2, 0.05), mm('glow'), ((i - 1) * 0.3, Hd.c.y - 0.1, Hd.top + 0.02))
    on(Hd, 'f', 0, 0.36, (0.16, 0.16), mm('glow2'), th=0.035, name='fore_gem', rot=(0, 45, 0))
    halo_kit(Hd, 'gold', r=0.56, n=10, dz=0.75, kind='flames')
    use('body')
    orbit_kit((0, 0.3, 1.3), 1.5, 6, 'glow', 'glow2', size=0.13, dz=0.3, shape='flame')
    orbit_kit((0, 0.3, 0.8), 1.8, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.15, shape='gem')
    aura_kit(1.6, 6, motes=12, mote_col='glow', mote_r=1.7, height=1.6, style='diamond')
    return finish(a)


ANIMALS = dict(rock_hyrax=rock_hyrax, mountain_goat=mountain_goat, canyon_roadrunner=canyon_roadrunner, armadillo=armadillo,
               canyon_condor=canyon_condor, redthorn_lizard=redthorn_lizard)
