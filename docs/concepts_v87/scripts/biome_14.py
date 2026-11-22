# Biome 14 - Volcano Heart: magma bridges, obsidian, glowing vents
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 14
GROUND = '#8a6a6a'
SKY = '#ffd0b0'
THEME = dict(bits=['#2a2430', '#ff5a1a'], dust='#c89a8a', glow='#ff5a1a', splash='#ffc080', bit_name='обсидиан и искры')
FOOT = dict(phoenix=1.3, obsidian_pangolin=1.2, magma_rhino=1.1)
BUSH_NAME = 'обсидиановые глыбы с магмовыми трещинами, вулканическим жерлом и огненными цветами'


def bush():
    B = begin_bush(NN)
    ob = mat('obsidian', '#2e2838')
    ob2 = mat('obsidian2', '#4a3e58')
    ob3 = mat('obsidian_hi', '#7a6a98')
    bas = mat('basalt', '#5a4a4a')
    lava = mat('lava', '#ff5a1a', 'neon', 2.8)
    lava2 = mat('lava2', '#ffb02a', 'neon', 3.2)
    fl = mat('fireflower', '#ff3a4a')
    st = mat('stem', '#6a5a3a')
    # obsidian shards: tall angular blocks leaning outwards (the silhouette), magma cracks
    spec = ((-1.8, 0.4, 1.1, 3.0, -12), (-0.5, 0.9, 1.3, 3.6, -4), (0.9, 0.8, 1.2, 3.3, 8), (2.2, 0.3, 1.0, 2.6, 16), (-2.8, -0.3, 0.8, 1.8, -24),
            (2.9, -0.4, 0.8, 1.8, 26))
    for i, (x, y, w, h, lean) in enumerate(spec):
        part('big', (x, y, 0.2), 'shard_%d' % i)
        b('shard', (w, w * 0.9, h), ob if i % 2 else ob2, (x, y, h / 2 + 0.1), rot=(0, lean, 0), bev=0.06)
        cn('shard_tip', w * 0.5, w * 0.9, ob, (x + math.sin(math.radians(lean)) * h, y, h + 0.05), (math.sin(math.radians(lean)), 0, 1))
        p('shard_shine', (0.12, 0.05, h * 0.6), ob3, (x - w * 0.25 + math.sin(math.radians(lean)) * h * 0.5, y - w * 0.46, h * 0.55), rot=(0, lean, 0))
        p('crack', (0.08, 0.05, h * 0.5), lava, (x + w * 0.2 + math.sin(math.radians(lean)) * h * 0.4, y - w * 0.46, h * 0.45), rot=(0, lean + 8, 0))
        p('crack_branch', (0.3, 0.05, 0.07), lava, (x + w * 0.1 + math.sin(math.radians(lean)) * h * 0.3, y - w * 0.46, h * 0.35), rot=(0, lean + 40, 0))
    # basalt base with a glowing vent
    part('big', (0, 0.0, 0.1), 'base')
    b('base', (6.0, 2.8, 0.5), bas, (0, 0.2, 0.25), bev=0.12)
    p('base_crack', (2.4, 0.06, 0.08), lava, (0.2, -1.21, 0.3))
    part('small', (0.2, -0.9, 0.5), 'vent')
    b('vent', (1.0, 0.8, 0.5), bas, (0.2, -0.9, 0.75), bev=0.1)
    b('vent_glow', (0.6, 0.5, 0.06), lava2, (0.2, -0.9, 1.01), bev=0.02)
    for i in range(3):
        b('vent_smoke', (0.3 - 0.06 * i, 0.3 - 0.06 * i, 0.26), mat('smoke', '#8a7a8a'), (0.2 + 0.1 * i, -0.9, 1.3 + i * 0.36), bev=0.08)
    # fire flowers between the shards
    for i, (x, y) in enumerate(((-1.2, -0.8), (1.6, -0.9), (-2.4, -1.1), (2.6, -1.2))):
        part('small', (x, y, 0.5), 'flower_%d' % i)
        b('stem', (0.08, 0.08, 0.6), st, (x, y, 0.8), bev=0.02)
        for j in range(4):
            ang = math.radians(j * 90 + 45)
            b('petal', (0.22, 0.22, 0.12), fl, (x + math.cos(ang) * 0.16, y + math.sin(ang) * 0.16, 1.14), rot=(0, 0, 45), bev=0.03)
        p('flower_core', (0.14, 0.14, 0.14), lava2, (x, y, 1.2))
    # magma pebbles
    for i, (x, y, s) in enumerate(((-0.8, -1.5, 0.4), (1.0, -1.5, 0.35), (-3.0, 0.9, 0.5), (3.0, 0.9, 0.45))):
        part('small', (x, y, 0.5), 'pebble_%d' % i)
        b('pebble', (s, s, s * 0.8), ob2, (x, y, 0.5 + s * 0.4), rot=(0, 0, 30 * i), bev=0.06)
        p('pebble_glow', (s * 0.5, 0.05, 0.08), lava, (x, y - s * 0.51, 0.5 + s * 0.4), rot=(0, 30, 0))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def furnace_stag_beetle(row):
    a = start(row, dict(main='#6a3a2a', belly='#c8784a', dark='#2a1a18', accent='#ffb02a', shine='#e8a07a'), 1.5)
    B, Hd = bug(bw=1.0, bl=1.1, bh=0.62, legh=0.32, hw=0.84, hd=0.44, hh=0.54, nleg=3, leg_w=0.1, leg_span=0.42, antenna=0.26, head_z=0.0,
                shell='main', under='belly', leg_mat='dark')
    use('head')
    # big antler mandibles (the silhouette)
    for sgn, n in LR:
        b('mandible', (0.14, 0.6, 0.14), mm('dark'), (sgn * 0.26, Hd.front - 0.28, Hd.c.z + 0.08), rot=(10, 0, -sgn * 18), bev=0.03)
        b('mandible_tip', (0.12, 0.24, 0.12), mm('dark'), (sgn * 0.14, Hd.front - 0.6, Hd.c.z + 0.12), rot=(0, 0, sgn * 40), bev=0.03)
        p('mandible_tooth', (0.08, 0.08, 0.08), mm('accent'), (sgn * 0.22, Hd.front - 0.4, Hd.c.z + 0.04))
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.28, Hd.front - 0.012, Hd.c.z - 0.14))
    eyes(Hd, 0.44, 0.25, 0.04, iris='#c86a1a', brow='#2a1a18', tilt=-10)
    use('body')
    p('split', (0.05, B.s.y * 0.92, 0.04), mm('dark'), (0, B.c.y + 0.03, B.top + 0.13))
    for sgn, n in LR:
        p('shine', (0.2, 0.36, 0.03), mm('shine'), (sgn * 0.24, B.c.y - 0.16, B.top + 0.135))
        p('shine2', (0.1, 0.12, 0.03), mm('shine'), (sgn * 0.3, B.c.y + 0.22, B.top + 0.135))
        for j in range(3):
            p('rivet', (0.08, 0.08, 0.04), mm('accent'), (sgn * 0.14, B.c.y - 0.3 + j * 0.3, B.top + 0.135))
    grid(B, 'l', 3, 1, mm('belly'), (0.14, 0.1), name='side_plate', span=(0.8, 0.2))
    grid(B, 'r', 3, 1, mm('belly'), (0.14, 0.1), name='side_plate', span=(0.8, 0.2))
    p('furnace_vent', (0.36, 0.1, 0.16), mm('accent'), (0, B.back + 0.04, B.c.z))
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_band', (0.08, 0.13, 0.13), mm('accent'), (j.x + sgn * 0.2, j.y, j.z + 0.04))
    use('body')
    return finish(a)


def obsidian_crab(row):
    a = start(row, dict(main='#3a3048', belly='#7a6a98', dark='#1e1828', accent='#ff6a2a', shine='#a898c8'), 1.9)
    B, Hd = bug(bw=1.3, bl=1.0, bh=0.6, legh=0.36, hw=0.9, hd=0.3, hh=0.46, nleg=4, leg_w=0.1, leg_span=0.46, claws=0.44, antenna=0,
                head_z=0.02, shell='main', under='belly', leg_mat='dark')
    use('head')
    p('mouth', (0.3, 0.03, 0.04), mm('accent'), (0, Hd.front - 0.012, Hd.c.z - 0.12))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.06))
        b('eye_stalk', (0.1, 0.1, 0.32), mm('dark'), (sgn * 0.24, Hd.c.y, Hd.top + 0.12), bev=0.02)
        b('eye_ball', (0.32, 0.22, 0.32), mm('main'), (sgn * 0.24, Hd.c.y, Hd.top + 0.42), bev=0.06)
    em = Box((0, Hd.c.y - 0.02, Hd.top + 0.42), (0.9, 0.2, 0.32), 'head')
    eyes(em, 0.86, 0.27, 0.0, iris='#ff6a2a', brow=None, w=0.86)
    use('body')
    # faceted obsidian shell (glassy facets)
    for i in range(3):
        for j in range(2):
            b('facet', (0.36, 0.36, 0.12), mm('dark' if (i + j) % 2 else 'main'), ((i - 1) * 0.38, B.c.y - 0.2 + j * 0.4, B.top + 0.1), rot=(0, 0, 45), bev=0.03)
    for sgn, n in LR:
        p('shine', (0.12, 0.3, 0.03), mm('shine'), (sgn * 0.34, B.c.y - 0.1, B.top + 0.17))
        cn('rim_spike', 0.07, 0.24, mm('dark'), (sgn * (B.s.x / 2 - 0.04), B.c.y, B.c.z + 0.1), (sgn * 1, 0, 0.3))
        p('lava_seam', (0.05, 0.6, 0.05), mm('accent'), (sgn * (B.s.x / 2 + 0.01), B.c.y, B.c.z))
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        cx = sgn * (B.s.x * 0.4 + 0.44 * 0.95)
        p('claw_shine', (0.12, 0.2, 0.05), mm('shine'), (cx, 0.2 - B.s.y / 2 - 0.44 * 0.55, B.c.z + 0.24))
        p('claw_seam', (0.36, 0.05, 0.05), mm('accent'), (cx, 0.2 - B.s.y / 2 - 0.2, B.c.z + 0.2))
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_band', (0.08, 0.12, 0.12), mm('belly'), (j.x + sgn * 0.22, j.y, j.z + 0.04))
    use('body')
    return finish(a)


def caldera_toad(row):
    a = start(row, dict(main='#c8582a', belly='#ffd8a0', dark='#6a2a1a', accent='#ffd84a', wart='#ff9a4a', scarf='#3a3a4a'), 2.3)
    B, Hd = sit(bw=1.3, bd=1.1, bh=0.76, hw=1.4, hd=1.0, hh=0.8, arm=0.3, lw=0.22, foot_l=0.7, ntoe=3, foot='belly', toe='accent')
    use('head')
    p('mouth', (1.0, 0.04, 0.05), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.2))
    for sgn, n in LR:
        p('mouth_corner', (0.05, 0.04, 0.12), mm('dark'), (sgn * 0.5, Hd.front - 0.012, Hd.c.z - 0.15))
        p('nostril', (0.06, 0.04, 0.05), mm('dark'), (sgn * 0.1, Hd.front - 0.012, Hd.c.z + 0.02))
        p('blush', (0.2, 0.03, 0.1), mm('pink'), (sgn * 0.5, Hd.front - 0.012, Hd.c.z - 0.06))
        b('eye_mount', (0.5, 0.46, 0.44), mm('main'), (sgn * 0.4, Hd.front + 0.26, Hd.top + 0.12), bev=0.1)
        p('eyelid', (0.52, 0.48, 0.08), mm('dark'), (sgn * 0.4, Hd.front + 0.26, Hd.top + 0.36))
    b('throat', (0.9, 0.2, 0.3), mm('belly'), (0, Hd.front + 0.04, Hd.bot + 0.06), bev=0.08)
    em = Box((0, Hd.front + 0.26, Hd.top + 0.12), (1.3, 0.46, 0.44), 'head')
    eyes(em, 0.8, 0.3, 0.0, iris='#ffb02a', brow=None, w=0.9, sleepy=0.18)
    use('body')
    # warts (pattern) and a little knitted heat-proof scarf (accessory)
    for i in range(4):
        for j in range(2):
            p('wart', (0.12, 0.12, 0.08), mm('wart' if (i + j) % 2 else 'dark'), ((i - 1.5) * 0.28, B.c.y + 0.1 + j * 0.3, B.top + 0.04))
    grid(B, 'l', 3, 2, mm('wart'), (0.1, 0.1), name='side_wart')
    grid(B, 'r', 3, 2, mm('wart'), (0.1, 0.1), name='side_wart')
    use('head')
    grid(Hd, 't', 3, 1, mm('wart'), (0.12, 0.12), name='head_wart', span=(0.6, 0.2))
    use('body')
    accessory('scarf', Box((0, B.front + 0.2, B.top + 0.1), (B.s.x * 0.9, 0.6, 0.3)), '#3a8ad8', '#ffd84a', z=B.top + 0.06)
    grid(B, 'k', 3, 2, mm('wart'), (0.12, 0.12), name='rump_wart')
    grid(B, 'f', 3, 2, mm('accent'), (0.1, 0.06), name='belly_line', span=(0.6, 0.5))
    use('head')
    grid(Hd, 'l', 2, 2, mm('wart'), (0.1, 0.1), name='head_wart')
    grid(Hd, 'r', 2, 2, mm('wart'), (0.1, 0.1), name='head_wart')
    for sgn, n in LR:
        p('tympanum', (0.05, 0.2, 0.2), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y + 0.1, Hd.c.z))
        p('tympanum_in', (0.06, 0.1, 0.1), mm('accent'), (sgn * (Hd.s.x / 2 + 0.012), Hd.c.y + 0.1, Hd.c.z))
    for i in range(5):
        p('lip_dot', (0.06, 0.04, 0.05), mm('belly'), ((i - 2) * 0.2, Hd.front - 0.012, Hd.c.z - 0.28))
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(3):
            p('leg_band', (ft.s.x + 0.02, 0.08, ft.s.z + 0.02), mm('dark'), (ft.c.x, ft.c.y - 0.1 + j * 0.2, ft.c.z))
    use('body')
    return finish(a)


def magma_rhino(row):
    """volcano rhino: carries a stepped volcano cone on its back that glows at the crater, single fat horn, stumpy elephant legs"""
    a = start(row, dict(main='#4a3a3e', belly='#8a6a6a', dark='#24181c', accent='#ffd0a0', horn='#3a2a30', rock='#5a4a4a', **{'*glow': '#ff5a1a', '*glow2': '#ffd21a'}), 3.0)
    B, Hd = quad(bw=1.5, bl=1.4, bh=0.9, legh=0.3, lw=0.48, hw=1.2, hd=1.0, hh=0.9, head_up=0.2, toe='accent', leg_fl=0.52, head_fwd=0.36,
                 rump=False)
    mz = muzzle(Hd, (0.8, 0.4, 0.46), -0.24, 'belly', nose=None, mouth=True)
    for sgn, n in LR:
        p('nostril', (0.1, 0.03, 0.07), mm('line'), (sgn * 0.2, mz.front - 0.008, mz.c.z + 0.08))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.44, Hd.front - 0.012, Hd.c.z - 0.24))
        b('ear', (0.2, 0.12, 0.26), mm('main'), (sgn * 0.5, Hd.c.y + 0.1, Hd.top + 0.04), rot=(0, sgn * 30, 0), bev=0.04)
    b('horn', (0.36, 0.36, 0.5), mm('horn'), (0, mz.c.y - 0.04, mz.top + 0.24), bev=0.08)
    p('horn_tip', (0.2, 0.2, 0.2), mm('rock'), (0, mz.c.y - 0.04, mz.top + 0.56))
    eyes(Hd, 0.28, 0.27, 0.12, iris='#c84a1a', glow='#ff5a1a', brow='#24181c', tilt=-14)
    use('body')
    # the volcano on its back (the silhouette): stepped cone of rock
    for i, (w, h) in enumerate(((1.4, 0.4), (1.1, 0.4), (0.8, 0.36), (0.6, 0.3))):
        b('cone', (w, w * 0.9, h), mm('rock' if i % 2 else 'main'), (0, B.c.y + 0.06, B.top + 0.2 + i * 0.38), bev=0.06)
    b('crater_rim', (0.66, 0.6, 0.12), mm('dark'), (0, B.c.y + 0.06, B.top + 1.48), bev=0.03)
    for sgn, n in LR:
        for j in range(3):
            p('lava_drip', (0.08, 0.05, 0.3 - 0.06 * j), mm('glow'), (sgn * (0.3 + 0.12 * j), B.c.y + 0.06 - 0.4 + 0.06 * j, B.top + 0.9 - 0.36 * j))
    for ft in a.bx['feet']:
        use(ft.seg)
        b('foot_pad', (ft.s.x + 0.1, ft.s.y + 0.1, 0.12), mm('rock'), (ft.c.x, ft.c.y + 0.04, 0.06), bev=0.03)
        for j in range(3):
            p('toenail', (0.1, 0.06, 0.08), mm('accent'), (ft.c.x + (j - 1) * 0.14, ft.front - 0.04, 0.06))
    use('body')
    grid(B, 'l', 4, 3, mm('rock'), (0.14, 0.14), name='rock_plate', offset=0.06)
    grid(B, 'r', 4, 3, mm('rock'), (0.14, 0.14), name='rock_plate', offset=0.06)
    grid(B, 'k', 3, 2, mm('rock'), (0.16, 0.16), name='rump_plate')
    use('head')
    grid(Hd, 'l', 2, 2, mm('rock'), (0.12, 0.12), name='cheek_plate')
    grid(Hd, 'r', 2, 2, mm('rock'), (0.12, 0.12), name='cheek_plate')
    use('body')
    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.2)
    # rarity 4: glowing crater and lava cracks (own segment), smoke-ember sparks
    sg('glow', 'body', (0, B.c.y + 0.06, B.top + 1.4))
    a.glow.append('glow')
    b('crater_lava', (0.46, 0.42, 0.1), mm('glow2'), (0, B.c.y + 0.06, B.top + 1.5), bev=0.03)
    for i in range(3):
        p('crater_spark', (0.1, 0.1, 0.16), mm('glow'), ((i - 1) * 0.14, B.c.y + 0.06, B.top + 1.66 + 0.06 * (i % 2)))
    for sgn, n in LR:
        p('flank_crack', (0.05, 0.6, 0.06), mm('glow'), (sgn * (B.s.x / 2 + 0.02), B.c.y, B.c.z))
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=2.2)
    return finish(a)


def phoenix(row):
    z0 = 0.26 + 0.5
    a = start(row, dict(main='#ff5a2a', belly='#ffd84a', dark='#c8281a', accent='#ff9a2a', leg='#ffd84a', beak='#ffe08a', beak_tip='#ff9a2a',
                        **{'*glow': '#ffb02a', '*glow2': '#ffe14a', '*flame': '#ff4a1a'}), 2.6, hover=5.0, z0=z0)
    B, Hd = bird(bw=1.0, bl=1.2, bh=0.9, legh=0.26, lw=0.13, hw=0.86, hd=0.8, hh=0.8, neck=0.2, beak=(0.3, 0.42, 0.24),
                 wing=(0.16, 0.9, 0.56), fly=True, wing_span=2.4, ntail=5, tail_l=0.9, tail_mat='accent', head_mat='main')
    use('head')
    for i in range(5):
        b('crest', (0.1, 0.12, 0.44 - 0.06 * abs(i - 2)), mm('glow2' if i % 2 else 'flame'), ((i - 2) * 0.12, Hd.c.y + 0.06, Hd.top + 0.2), rot=(-25, (i - 2) * 12, 0), bev=0.03)
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.2))
        p('cheek_flame', (0.04, 0.3, 0.14), mm('glow'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y + 0.1, Hd.c.z - 0.1))
    eyes(Hd, 0.36, 0.25, 0.12, iris='#ff8a1a', glow='#ffe14a', lash=True, brow='#c8281a', tilt=-8)
    use('body')
    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('belly'), 4, 0.9, 0.36)
    grid(B, 'l', 3, 2, mm('dark'), (0.2, 0.16), name='side_feather', offset=0.1)
    grid(B, 'r', 3, 2, mm('dark'), (0.2, 0.16), name='side_feather', offset=0.1)
    grid(B, 'u', 3, 2, mm('accent'), (0.2, 0.2), name='belly_feather', th=0.1)
    for sgn, n in LR:
        use('wing_' + n)
        wb = a.bx['wings'][0 if sgn < 0 else 1]
        for i in range(5):
            p('covert', (0.3, 0.24, 0.05), mm('belly' if i % 2 else 'accent'), (sgn * (B.s.x / 2 + 0.3 + i * 0.44), 0.0, wb.c.z + 0.12))
        use('leg_' + n)
        for j in range(2):
            p('leg_ring', (0.17, 0.17, 0.05), mm('dark'), (sgn * B.s.x * 0.24, 0.15, 0.1 + j * 0.08))
    use('body')
    for i in range(3):
        for j in range(3):
            p('back_feather', (0.28, 0.3, 0.05), mm('dark' if (i + j) % 2 else 'accent'), ((i - 1) * 0.3, B.c.y - 0.3 + j * 0.3, B.top + 0.03))
    # rarity 5: burning feather tips on the wings and the long tail (own glowing segment), orbiting embers, yellow aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for sgn, n in LR:
        use('wing_' + n)
        wb = a.bx['wings'][0 if sgn < 0 else 1]
        for i in range(6):
            x = sgn * (B.s.x / 2 + 0.24 + i * 0.4)
            b('flame_feather', (0.22, 0.5, 0.1), mm('flame' if i % 2 else 'glow'), (x, 0.9 - 0.04 * i, wb.c.z - 0.03), bev=0.03)
            p('flame_tip', (0.14, 0.16, 0.08), mm('glow2'), (x, 1.2 - 0.04 * i, wb.c.z - 0.03))
        use('glow')
    use('tail')
    for i in range(5):
        ang = (i - 2) * 17.5
        sx, cz = math.sin(math.radians(ang)), math.cos(math.radians(ang))
        p('tail_flame', (0.16, 0.3, 0.12), mm('glow' if i % 2 else 'glow2'), (sx * 0.6, 0.15 + 1.2 * 0.62 + 1.0, z0 + 0.2 + cz * 0.2 + 0.4))
        p('tail_ember', (0.1, 0.1, 0.1), mm('flame'), (sx * 0.7, 0.15 + 1.2 * 0.62 + 1.3, z0 + 0.2 + cz * 0.2 + 0.5), rot=(45, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(3):
        p('crest_tip', (0.1, 0.1, 0.12), mm('glow2'), ((i - 1) * 0.24, Hd.c.y - 0.06, Hd.top + 0.46))
    use('body')
    orbit_kit((0, 0.2, z0), 1.5, 6, 'glow', 'glow2', size=0.13, dz=0.3, shape='flame')
    aura_kit(1.5, 5, motes=10, mote_col='glow', height=1.2, style='petals')
    return finish(a)


def obsidian_pangolin(row):
    a = start(row, dict(main='#3a3048', belly='#c8a898', dark='#1e1828', accent='#8a7aa8', scale2='#5a4a6a',
                        **{'*glow': '#ff5a1a', '*glow2': '#ffd21a', '*gold': '#ffd84a'}), 2.3)
    B, Hd = quad(bw=1.2, bl=1.6, bh=0.9, legh=0.36, lw=0.3, hw=0.86, hd=0.84, hh=0.76, head_up=0.24, toe='belly', head_fwd=0.46,
                 leg_fl=0.5, ntoe=3, head_mat='belly')
    mz = muzzle(Hd, (0.36, 0.4, 0.28), -0.24, 'belly', nose=(0.14, 0.07, 0.09), nose_mat='dark')
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.16))
    eyes(Hd, 0.34, 0.25, 0.12, iris='#ff6a2a', glow='#ff5a1a', lash=True, brow='#1e1828', tilt=8)
    ears(Hd, 'round', 'belly', 'pink', x=0.4, h=0.14, w=0.16, lean=20)
    use('head')
    for i in range(3):
        b('head_scale', (0.3, 0.26, 0.12), mm('main' if i % 2 else 'scale2'), ((i - 1) * 0.28, Hd.c.y + 0.1, Hd.top + 0.05), bev=0.03)
    use('body')
    # overlapping scale armour rows (the silhouette): rows of tilted plates, larger towards the back
    for j in range(6):
        y = B.front + 0.1 + j * 0.28
        for i in range(4):
            x = (i - 1.5) * 0.3
            b('scale', (0.32, 0.3, 0.14), mm('main' if (i + j) % 2 else 'scale2'), (x, y, B.top + 0.06 + 0.02 * j), rot=(-20, 0, 0), bev=0.03)
        for sgn, n in LR:
            b('side_scale', (0.14, 0.3, 0.32), mm('scale2'), (sgn * (B.s.x / 2 + 0.06), y, B.c.z + 0.1), rot=(0, sgn * 15, 0), bev=0.03)
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)
    for ft in a.bx['feet']:
        use(ft.seg)
        p('claw_big', (0.12, 0.16, 0.08), mm('gold'), (ft.c.x, ft.front - 0.02, 0.05))
        for j in range(3):
            b('leg_scale', (ft.s.x + 0.06, 0.16, 0.12), mm('scale2'), (ft.c.x, ft.c.y + 0.1 - j * 0.06, 0.2 + j * 0.1), rot=(-20, 0, 0), bev=0.02)
    use('head')
    grid(Hd, 'l', 2, 2, mm('accent'), (0.1, 0.1), name='cheek_scale')
    grid(Hd, 'r', 2, 2, mm('accent'), (0.1, 0.1), name='cheek_scale')
    use('body')
    # big scaly tail (2 segments)
    tail_kit('thick', 'body', a.tail_j, 'main', 'scale2', size=0.22)
    for i in range(6):
        b('tail_scale', (0.36 - 0.03 * i, 0.24, 0.14), mm('scale2'), (0, a.tail_j[1] + 0.2 + i * 0.2, a.tail_j[2] + 0.22 - 0.02 * i), rot=(-20, 0, 0), bev=0.03)
    # rarity 6: magma glows between the scales, gem tail tip, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for j in range(5):
        p('scale_glow', (B.s.x * 0.9, 0.05, 0.05), mm('glow' if j % 2 else 'glow2'), (0, B.front + 0.24 + j * 0.28, B.top + 0.06 + 0.02 * j))
    for sgn, n in LR:
        for j in range(3):
            p('side_glow', (0.05, 0.05, 0.3), mm('glow'), (sgn * (B.s.x / 2 + 0.13), B.front + 0.24 + j * 0.56, B.c.z + 0.1))
    use('tail')
    b('tail_gem', (0.24, 0.24, 0.24), mm('glow2'), (0, a.tail_j[1] + 1.0, a.tail_j[2] - 0.1), rot=(45, 45, 0), bev=0.05)
    use('head')
    halo_kit(Hd, 'gold', r=0.44, n=8, dz=0.7, kind='gears')
    use('body')
    orbit_kit((0, 0.2, 1.4), 1.6, 6, 'glow', 'glow2', size=0.14, dz=0.3, shape='shard')
    orbit_kit((0, 0.2, 0.9), 1.9, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.15, shape='flame')
    aura_kit(1.7, 6, motes=12, mote_col='glow', mote_r=1.8, height=1.8, style='double')
    return finish(a)


ANIMALS = dict(furnace_stag_beetle=furnace_stag_beetle, obsidian_crab=obsidian_crab, caldera_toad=caldera_toad, magma_rhino=magma_rhino,
               phoenix=phoenix, obsidian_pangolin=obsidian_pangolin)
