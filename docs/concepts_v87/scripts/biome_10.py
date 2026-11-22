# Biome 10 - Storm Highlands: crags, storm clouds, lightning obelisks
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 10
GROUND = '#7a9a8a'
SKY = '#c8d4e4'
THEME = dict(bits=['#8a7ab8', '#9aa8a0'], dust='#c8ccd4', glow='#7ac8ff', splash='#c8e8ff', bit_name='вереск и каменная крошка')
FOOT = dict(thunder_eagle=1.4, storm_griffin=1.45, tempest_pterosaur=1.5)
BUSH_NAME = 'горный вереск у скалы с осколком грозового обелиска и маленькой тучкой'


def bush():
    B = begin_bush(NN)
    rk = mat('rock', '#7e8a96')
    rk2 = mat('rock2', '#5e6874')
    rk3 = mat('rock3', '#a4b0bc')
    he = mat('heather', '#9a6ad8')
    he2 = mat('heather2', '#c08af0')
    gr = mat('grass', '#6a9a5a')
    gr2 = mat('grass2', '#8aba6a')
    obel = mat('obelisk', '#3e4658')
    cloud = mat('cloud', '#e8eef6')
    cloud2 = mat('cloud2', '#b8c4d4')
    bolt = mat('bolt', '#ffe14a', 'neon', 2.6)
    rune = mat('rune', '#7ac8ff', 'neon', 2.4)
    # crag: stacked slabs
    for i, (x, y, w, d, h, rz) in enumerate(((-1.6, 0.6, 2.6, 2.0, 2.2, 8), (1.4, 0.7, 2.4, 1.8, 1.6, -10), (-0.2, 1.2, 1.8, 1.4, 3.1, 4))):
        part('big', (x, y, 0.2), 'crag_%d' % i)
        b('crag', (w, d, h), (rk, rk2, rk)[i], (x, y, h / 2), rot=(0, 0, rz), bev=0.14)
        b('crag_top', (w * 0.7, d * 0.7, 0.3), rk3, (x + 0.1, y, h + 0.1), rot=(0, 0, rz), bev=0.08)
        p('crag_crack', (0.06, 0.05, h * 0.5), rk2, (x + w * 0.2, y - d / 2 - 0.01, h * 0.45), rot=(0, 0, rz))
        p('crag_moss', (w * 0.5, 0.06, 0.2), gr, (x - w * 0.1, y - d / 2 - 0.02, h * 0.8), rot=(0, 0, rz))
    # obelisk shard with glowing runes (the storm landmark)
    part('big', (0.9, 0.2, 0.3), 'obelisk')
    b('obelisk', (0.6, 0.6, 2.8), obel, (0.9, 0.2, 1.6), rot=(0, 8, 0), bev=0.06)
    cn('obelisk_tip', 0.42, 0.7, obel, (1.1, 0.2, 3.0), (0.14, 0, 1))
    for j in range(4):
        p('obelisk_rune', (0.24, 0.05, 0.14 if j % 2 else 0.24), rune, (0.9 + 0.03 * j, -0.11, 0.8 + j * 0.5), rot=(0, 8, 0))
    # little storm cloud with a bolt over the crag
    part('small', (-0.6, 0.6, 3.9), 'cloud')
    for i, (x, y, z, w) in enumerate(((-0.6, 0.6, 4.0, 1.2), (-1.2, 0.6, 3.9, 0.8), (0.0, 0.6, 3.9, 0.9), (-0.7, 0.6, 4.4, 0.7))):
        b('cloud', (w, w * 0.8, w * 0.6), cloud if i % 2 == 0 else cloud2, (x, y, z), bev=0.12)
    b('bolt', (0.12, 0.12, 0.5), bolt, (-0.7, 0.4, 3.4), rot=(0, 20, 0), bev=0.02)
    b('bolt', (0.12, 0.12, 0.4), bolt, (-0.56, 0.4, 3.0), rot=(0, -25, 0), bev=0.02)
    # heather clumps (the bush part that shakes most)
    k_ = 0
    for (cx, cy, s) in ((-2.6, -0.6, 1.0), (-1.2, -1.0, 1.2), (0.3, -1.1, 1.1), (1.8, -0.8, 1.0), (2.9, 0.2, 0.8), (-2.9, 0.9, 0.8)):
        part('small', (cx, cy, 0.2), 'heather_%d' % k_)
        b('heather_mound', (1.1 * s, 0.9 * s, 0.7 * s), gr, (cx, cy, 0.35 * s), bev=0.1)
        for j in range(5):
            ang = math.radians(j * 72 + 20)
            h = 0.6 + 0.2 * (j % 2)
            b('heather_spike', (0.16, 0.16, h * s), he if j % 2 else he2, (cx + math.cos(ang) * 0.3 * s, cy + math.sin(ang) * 0.25 * s, 0.7 * s + h * s / 2), bev=0.03)
            p('heather_tip', (0.12, 0.12, 0.14), he2, (cx + math.cos(ang) * 0.3 * s, cy + math.sin(ang) * 0.25 * s, 0.7 * s + h * s + 0.06))
        k_ += 1
    # scree and grass tufts
    for i, (x, y, s) in enumerate(((-0.4, -1.7, 0.5), (1.2, -1.7, 0.4), (2.6, -1.3, 0.6), (-2.2, -1.6, 0.4))):
        part('small', (x, y, 0.1), 'scree_%d' % i)
        b('scree', (0.8 * s, 0.7 * s, 0.6 * s), rk3 if i % 2 else rk, (x, y, 0.3 * s), rot=(0, 0, 25 * i), bev=0.08)
        p('scree_spark', (0.2 * s, 0.05, 0.08), rune, (x, y - 0.35 * s, 0.4 * s), rot=(0, 30, 0))
        for j in range(3):
            b('tuft', (0.1, 0.1, 0.5), gr2, (x + 0.4 * s + j * 0.12, y, 0.25), rot=(0, (j - 1) * 14, 0), bev=0.02)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def storm_stone_spider(row):
    a = start(row, dict(main='#6e7884', belly='#a8b4c0', dark='#3e4652', accent='#7ac8ff', moss='#7aaa5a'), 1.5)
    B, Hd = bug(bw=1.1, bl=1.1, bh=0.66, legh=0.4, hw=0.9, hd=0.5, hh=0.64, nleg=4, leg_w=0.11, leg_span=0.5, antenna=0.3, head_z=0.04,
                shell='main', under='belly', leg_mat='dark')
    use('head')
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.18))
        p('fang', (0.08, 0.1, 0.12), mm('belly'), (sgn * 0.12, Hd.front - 0.04, Hd.bot + 0.04))
        p('mini_eye', (0.08, 0.04, 0.08), mm('dark'), (sgn * 0.12, Hd.front - 0.012, Hd.top - 0.06))
    eyes(Hd, 0.42, 0.25, 0.06, iris='#3a6ac8', brow='#3e4652', tilt=10, lash=True)
    use('body')
    # pebble back: stacked stones, moss and a lichen spot (pattern)
    for i, (x, y, s) in enumerate(((-0.24, -0.2, 0.36), (0.22, -0.1, 0.3), (0.0, 0.24, 0.4), (-0.3, 0.3, 0.24), (0.32, 0.34, 0.26))):
        b('pebble', (s, s, s * 0.6), mm('belly' if i % 2 else 'main'), (x, B.c.y + y, B.top + 0.14 + s * 0.2), rot=(0, 0, 20 * i), bev=0.06)
    for i in range(4):
        p('moss', (0.18, 0.18, 0.05), mm('moss'), ((i - 1.5) * 0.24, B.c.y - 0.42, B.top + 0.13))
    for sgn, n in LR:
        for j in range(3):
            p('side_stone', (0.05, 0.22, 0.2), mm('belly'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.3 + j * 0.3, B.c.z))
    p('lightning_mark', (0.1, 0.24, 0.04), mm('accent'), (0, B.c.y + 0.0, B.top + 0.42), rot=(0, 0, 25))
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_band', (0.08, 0.14, 0.14), mm('belly'), (j.x + sgn * 0.22, j.y, j.z + 0.04))
    use('body')
    return finish(a)


def storm_ram(row):
    """storm ram: sleek slate-grey short coat (no wool), zig-zag lightning horns pointing up, a little thundercloud
    floating as a forelock and as its tail"""
    a = start(row, dict(main='#5a6478', belly='#9aa4b8', dark='#2e3444', accent='#c8d0e0', bolt='#ffd84a', cloud='#e8eef8', cloud2='#a8b4c8'), 2.8)
    B, Hd = quad(bw=0.84, bl=1.2, bh=0.7, legh=0.6, lw=0.2, hw=0.86, hd=0.86, hh=0.8, head_fwd=0.34, hoof='dark', leg_mat='main', head_mat='main')
    mz = muzzle(Hd, (0.4, 0.32, 0.26), -0.28, 'belly', nose=(0.14, 0.06, 0.08), nose_mat='dark')
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.18))
        b('ear', (0.26, 0.1, 0.12), mm('main'), (sgn * 0.52, Hd.c.y + 0.06, Hd.c.z + 0.12), rot=(0, sgn * 25, 0), bev=0.03)
        p('ear_in', (0.14, 0.04, 0.06), mm('pink'), (sgn * 0.52, Hd.c.y, Hd.c.z + 0.12), rot=(0, sgn * 25, 0))
    eyes(Hd, 0.34, 0.25, 0.1, iris='#ffb02a', brow='#2e3444', tilt=-14)
    # zig-zag lightning horns going straight up (the silhouette)
    use('head')
    for sgn, n in LR:
        x0 = sgn * 0.26
        for j, (dx, dz) in enumerate(((0.0, 0.0), (0.16, 0.24), (0.0, 0.48), (0.16, 0.72), (0.04, 0.96))):
            b('bolt_horn', (0.16, 0.16, 0.3), mm('bolt'), (x0 + sgn * dx, Hd.c.y, Hd.top + 0.14 + dz), rot=(0, sgn * (30 if j % 2 else -30), 0), bev=0.03)
        p('horn_base', (0.24, 0.24, 0.1), mm('dark'), (x0, Hd.c.y, Hd.top + 0.02))
    # thundercloud forelock
    for i, (x, z, s) in enumerate(((0, 0.12, 0.34), (-0.18, 0.06, 0.26), (0.18, 0.06, 0.26))):
        b('cloud_lock', (s, s, s * 0.8), mm('cloud' if i == 0 else 'cloud2'), (x, Hd.front + 0.2, Hd.top + z), bev=0.08)
    use('body')
    # short sleek coat with lightning stripes (pattern)
    for sgn, n in LR:
        for j, (u, v, rz) in enumerate(((-0.3, 0.1, 30), (-0.1, -0.1, -30), (0.1, 0.1, 30), (0.3, -0.1, -30))):
            on(B, 'l' if sgn < 0 else 'r', u, v, (0.22, 0.07), mm('accent'), name='zig', rot=(rz, 0, 0))
    on(B, 't', 0, 0, (0.16, B.s.y * 0.9), mm('dark'), name='back_stripe')
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.8, 0.3)
    for ft in a.bx['feet']:
        p('sock', (ft.s.x + 0.02, ft.s.y + 0.02, 0.14), mm('dark'), (ft.c.x, ft.c.y, ft.top + 0.08))
    # thundercloud tail with a dangling bolt
    sg('tail', 'body', a.tail_j)
    a.tail = ['tail']
    for i, (dy, dz, s) in enumerate(((0.2, 0.1, 0.34), (0.42, 0.18, 0.28), (0.3, 0.32, 0.24))):
        b('tail_cloud', (s, s, s * 0.8), mm('cloud' if i % 2 == 0 else 'cloud2'), (0, a.tail_j[1] + dy, a.tail_j[2] + dz), bev=0.08)
    b('tail_bolt', (0.08, 0.08, 0.3), mm('bolt'), (0, a.tail_j[1] + 0.36, a.tail_j[2] - 0.12), rot=(0, 25, 0), bev=0.02)
    return finish(a)


def highland_yak(row):
    a = start(row, dict(main='#6a4e3e', belly='#8a6a54', dark='#3e2c22', accent='#a8846a', horn='#f2e6d0', face='#4a3428'), 2.4)
    B, Hd = quad(bw=1.3, bl=1.6, bh=1.0, legh=0.36, lw=0.34, hw=1.08, hd=0.96, hh=0.92, head_up=0.3, hump=0.34, hoof='dark', leg_mat='dark',
                 head_mat='face', head_fwd=0.36)
    mz = muzzle(Hd, (0.5, 0.3, 0.32), -0.28, 'accent', nose=(0.24, 0.1, 0.12))
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.4, Hd.front - 0.012, Hd.c.z - 0.2))
        b('horn_base', (0.28, 0.2, 0.2), mm('horn'), (sgn * (Hd.s.x / 2 + 0.06), Hd.c.y, Hd.top - 0.12), bev=0.05)
        b('horn_up', (0.18, 0.18, 0.44), mm('horn'), (sgn * (Hd.s.x / 2 + 0.22), Hd.c.y, Hd.top + 0.12), rot=(0, sgn * 18, 0), bev=0.05)
        p('horn_tip', (0.12, 0.12, 0.16), mm('dark'), (sgn * (Hd.s.x / 2 + 0.3), Hd.c.y, Hd.top + 0.38))
    eyes(Hd, 0.28, 0.24, 0.12, iris='#4a2a16', brow='#3e2c22', tilt=6, sleepy=0.16)
    ears(Hd, 'flop', 'face', 'pink', x=0.5, h=0.2, w=0.18)
    use('head')
    for i in range(5):
        b('fringe', (0.22, 0.2, 0.3 + 0.06 * (i % 2)), mm('main'), ((i - 2) * 0.2, Hd.front + 0.1, Hd.top - 0.06), bev=0.05)
    use('body')
    # long skirt of hair (the silhouette) in layered strands
    for sgn, n in LR:
        for j in range(6):
            b('skirt', (0.12, 0.26, 0.6 - 0.08 * (j % 2)), mm('main' if j % 2 else 'dark'), (sgn * (B.s.x / 2 + 0.06), B.front + 0.14 + j * 0.26, B.bot - 0.06), bev=0.04)
    for j in range(4):
        b('skirt_front', (0.28, 0.12, 0.5), mm('main'), ((j - 1.5) * 0.3, B.front - 0.06, B.bot - 0.04), bev=0.04)
    hp = a.bx['hump']
    for i in range(3):
        p('hump_hair', (0.3, 0.34, 0.12), mm('dark'), ((i - 1) * 0.3, hp.c.y, hp.top + 0.04))
    # rarity 3 accessory: a woven saddle blanket with a bell
    setm('cloth', '#3a7ad8')
    setm('cloth2', '#ffd84a')
    b('blanket', (B.s.x + 0.1, 0.7, 0.1), mm('cloth'), (0, B.c.y + 0.2, B.top + 0.05), bev=0.03)
    for sgn, n in LR:
        b('blanket_side', (0.08, 0.7, 0.5), mm('cloth'), (sgn * (B.s.x / 2 + 0.1), B.c.y + 0.2, B.top - 0.22), bev=0.03)
        for j in range(3):
            p('blanket_zig', (0.1, 0.14, 0.14), mm('cloth2'), (sgn * (B.s.x / 2 + 0.15), B.c.y + j * 0.2, B.top - 0.2), rot=(45, 0, 0))
    for j in range(3):
        p('blanket_stripe', (B.s.x * 0.8, 0.07, 0.11), mm('cloth2'), (0, B.c.y + 0.0 + j * 0.2, B.top + 0.06))
    accessory('bell', Box((0, B.front + 0.4, B.top - 0.1), (B.s.x * 0.8, 0.8, 0.3)), '#a8463a', '#ffd84a', z=B.top - 0.2)
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(3):
            p('leg_hair', (ft.s.x + 0.06, ft.s.y + 0.04, 0.08), mm('main' if j % 2 else 'dark'), (ft.c.x, ft.c.y, 0.24 + j * 0.1))
    use('head')
    for sgn, n in LR:
        for j in range(3):
            p('cheek_hair', (0.1, 0.2, 0.24 - 0.04 * j), mm('main'), (sgn * (Hd.s.x / 2 + 0.04), Hd.front + 0.2 + j * 0.2, Hd.c.z - 0.2))
    use('body')
    for i in range(6):
        p('back_hair', (0.26, 0.2, 0.08), mm('dark' if i % 2 else 'accent'), ((i % 3 - 1) * 0.36, B.c.y + 0.5 + 0.2 * (i // 3), B.top + 0.04))
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.18)
    return finish(a)


def thunder_eagle(row):
    z0 = 0.26 + 0.5
    a = start(row, dict(main='#5a6ad8', belly='#ffffff', dark='#2a3a8a', accent='#ffd84a', leg='#ffd84a', beak='#ffd84a', beak_tip='#e8a020',
                        **{'*glow': '#7ac8ff', '*bolt': '#ffe14a'}), 2.5, hover=4.0, z0=z0)
    B, Hd = bird(bw=1.0, bl=1.2, bh=0.96, legh=0.26, lw=0.14, hw=0.94, hd=0.86, hh=0.84, neck=0.1, beak=(0.36, 0.5, 0.34),
                 wing=(0.16, 0.9, 0.56), fly=True, wing_span=2.2, ntail=5, tail_l=0.56, tail_mat='dark', head_mat='belly')
    bk = a.bx['beak']
    use('head')
    b('hook', (0.26, 0.16, 0.3), mm('beak_tip'), (0, bk.front + 0.02, bk.c.z - 0.14), bev=0.04)
    for i in range(4):
        b('crest', (0.12, 0.2, 0.36 - 0.06 * i), mm('main'), ((i - 1.5) * 0.14, Hd.c.y + 0.2, Hd.top + 0.14), rot=(-30, (i - 1.5) * 10, 0), bev=0.03)
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.2))
        on(Hd, 'l' if sgn < 0 else 'r', 0, 0.0, (0.5, 0.12), mm('main'), name='head_stripe')
    eyes(Hd, 0.34, 0.25, 0.14, iris='#3a6ac8', glow='#7ac8ff', brow='#2a3a8a', tilt=-14)
    use('body')
    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('belly'), 4, 0.9, 0.36)
    for i in range(3):
        for j in range(3):
            p('back_feather', (0.28, 0.3, 0.05), mm('dark' if (i + j) % 2 else 'main'), ((i - 1) * 0.3, B.c.y - 0.3 + j * 0.3, B.top + 0.03))
    # rarity 4: lightning-bolt marks on the wings, glowing primaries, crackling sparks
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for sgn, n in LR:
        use('wing_' + n)
        wb = a.bx['wings'][0 if sgn < 0 else 1]
        for i in range(5):
            x = sgn * (B.s.x / 2 + 0.3 + i * 0.4)
            b('primary', (0.22, 0.46, 0.1), mm('dark'), (x, 0.84 - 0.05 * i, wb.c.z - 0.03), bev=0.03)
        use('glow')
        for i, (dx, dy, rz) in enumerate(((0.4, -0.1, 30), (0.7, 0.1, -30), (1.0, -0.1, 30), (1.3, 0.1, -30))):
            p('wing_bolt', (0.3, 0.1, 0.05), mm('bolt'), (sgn * (B.s.x / 2 + dx), 0.2 + dy, wb.c.z + 0.12), rot=(0, 0, sgn * rz))
        p('wing_glow', (0.2, 0.2, 0.06), mm('glow'), (sgn * (B.s.x / 2 + 2.0), 0.9, wb.c.z - 0.03))
    on(B, 't', 0, 0, (0.14, 0.4), mm('bolt'), th=0.1, name='back_bolt', rot=(0, 0, 20))
    use('tail')
    for i in range(5):
        ang = (i - 2) * 17.5
        p('tail_glow', (0.12, 0.14, 0.08), mm('glow'), (math.sin(math.radians(ang)) * 0.42, 0.15 + 1.2 * 0.62 + 0.56, z0 + 0.42 + math.cos(math.radians(ang)) * 0.2 + 0.24))
    use('body')
    aura_kit(1.4, 4, motes=8, mote_col='glow', height=1.2)
    return finish(a)


def _quad_flyer(a, wing_span, wing_depth, bw=1.1, bl=1.4, bh=0.9, legh=0.44, lw=0.28, hw=1.0, hd=0.9, hh=0.9, neck=0.2, wmat='accent'):
    B, Hd = quad(bw=bw, bl=bl, bh=bh, legh=legh, lw=lw, hw=hw, hd=hd, hh=hh, neck=neck, toe='horn', head_fwd=0.3, leg_fl=0.5)
    wings_big('body', (bw / 2 - 0.05, B.c.y - 0.1, B.top - 0.05), span=wing_span, depth=wing_depth, th=0.14, mat=wmat, bone='dark', web='belly', n=3, up=22)
    return B, Hd


def storm_griffin(row):
    z0 = 0.44 + 0.45
    a = start(row, dict(main='#e8b84a', belly='#fff4d8', dark='#5a4ab0', accent='#f6f0ff', horn='#ffd84a', head='#ffffff', beak='#ffc93c',
                        beak_tip='#e8a020', **{'*glow': '#7ac8ff', '*glow2': '#ffe14a'}), 2.6, hover=5.5, z0=z0)
    B, Hd = quad(bw=1.1, bl=1.45, bh=0.9, legh=0.44, lw=0.28, hw=1.0, hd=0.9, hh=0.9, neck=0.2, toe='horn', head_fwd=0.3, leg_fl=0.5,
                 head_mat='head')
    use('head')
    bk = b('beak', (0.4, 0.5, 0.34), mm('beak'), (0, Hd.front - 0.2, Hd.c.z - 0.14))
    b('hook', (0.3, 0.2, 0.3), mm('beak_tip'), (0, bk.front + 0.02, bk.c.z - 0.12), bev=0.05)
    for sgn, n in LR:
        p('nostril', (0.05, 0.08, 0.04), mm('line'), (sgn * 0.08, bk.c.y, bk.top + 0.005))
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.24))
        for j in range(3):
            b('ear_feather', (0.12, 0.14, 0.3 - 0.05 * j), mm('dark'), (sgn * (0.3 + 0.08 * j), Hd.c.y + 0.2, Hd.top + 0.14), rot=(-30, sgn * 20, 0), bev=0.03)
    for i in range(3):
        p('head_feather', (0.3, 0.2, 0.05), mm('dark'), ((i - 1) * 0.3, Hd.c.y + 0.2, Hd.top + 0.03))
    eyes(Hd, 0.32, 0.25, 0.12, iris='#3a6ac8', glow='#7ac8ff', brow='#5a4ab0', tilt=-12)
    use('body')
    # feathered ruff (eagle front) blending into the lion body
    for j in range(4):
        b('ruff', (1.0 - 0.12 * j, 0.2, 0.24), mm('head'), (0, B.front - 0.04 + 0.03 * j, B.top - 0.06 - j * 0.2), bev=0.05)
    spots(B, 'lr', 4, mm('accent'), 0.14, seed=3, name='fleck')
    on(B, 't', 0, 0.2, (0.3, B.s.y * 0.5), mm('accent'), name='back_stripe', th=0.04)
    stripes(B, 'lr', 4, mm('dark'), 0.08, name='stripe', span=0.8)
    stripes(a.bx['rump'], 'lr', 2, mm('dark'), 0.08, name='stripe', span=0.6)
    for i in range(3):
        for j in range(3):
            p('back_feather', (0.28, 0.24, 0.06), mm('head' if (i + j) % 2 else 'accent'), ((i - 1) * 0.3, B.front + 0.16 + j * 0.2, B.top + 0.04))
    for i in range(6):
        p('chest_feather', (0.2, 0.06, 0.16), mm('accent'), ((i % 3 - 1) * 0.26, B.front - 0.14, B.c.z + 0.1 - 0.2 * (i // 3)))
    for ft in a.bx['feet']:
        p('talon_cuff', (ft.s.x + 0.04, ft.s.y * 0.8, 0.1), mm('beak'), (ft.c.x, ft.c.y + 0.04, ft.top + 0.08))
    wings_big('body', (1.1 / 2 - 0.05, B.c.y - 0.1, B.top - 0.05), span=2.6, depth=1.2, th=0.14, mat='dark', bone='main', web='accent', n=3, up=24)
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.2)
    # rarity 5: lightning veins on the wings, glowing crest and claws, orbiting sparks, yellow aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for sgn, n in LR:
        use('wing_' + n)
        for i in range(3):
            ln = 2.6 / 3
            cx = sgn * (1.1 / 2 - 0.05 + ln * (i + 0.5))
            z = B.top - 0.05 + math.tan(math.radians(24)) * ln * (i + 0.5)
            p('wing_bolt', (ln * 0.6, 0.12, 0.1), mm('glow2' if i % 2 else 'glow'), (cx, B.c.y + 0.5, z + 0.06), rot=(0, -sgn * 24, sgn * 25))
        use('glow')
    for i in range(3):
        on(B, 't', 0, -0.3 + i * 0.3, (0.14, 0.14), mm('glow2'), th=0.05, name='back_rune', rot=(0, 0, 45))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        p('ear_glow', (0.08, 0.08, 0.1), mm('glow'), (sgn * 0.46, Hd.c.y + 0.36, Hd.top + 0.36))
    on(Hd, 'f', 0, 0.38, (0.14, 0.14), mm('glow2'), th=0.035, name='fore_bolt', rot=(0, 30, 0))
    use(a.tail[0])
    p('tail_glow', (0.16, 0.16, 0.16), mm('glow'), (0, a.tail_j[1] + 0.46, a.tail_j[2] - 0.2), rot=(45, 45, 0))
    for sgn, n in LR:
        use('wing_' + n)
        for i in range(6):
            x = sgn * (1.1 / 2 + 0.2 + i * 0.4)
            z = B.top - 0.05 + math.tan(math.radians(24)) * (0.2 + i * 0.4)
            b('flight_feather', (0.26, 0.4, 0.1), mm('main' if i % 2 else 'head'), (x, B.c.y + 1.1, z - 0.04), rot=(0, -sgn * 24, 0), bev=0.03)
            p('covert', (0.24, 0.2, 0.05), mm('accent'), (x, B.c.y + 0.1, z + 0.08), rot=(0, -sgn * 24, 0))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_feather', (ft.s.x + 0.08, ft.s.y * 0.8, 0.14), mm('head'), (ft.c.x, ft.c.y + 0.04, 0.4))
        p('leg_glow', (ft.s.x + 0.06, ft.s.y * 0.8, 0.04), mm('glow'), (ft.c.x, ft.c.y + 0.04, 0.3))
    use('body')
    orbit_kit((0, 0.2, z0), 1.6, 6, 'glow', 'glow2', size=0.13, dz=0.3, shape='cross')
    aura_kit(1.6, 5, motes=10, mote_col='glow', height=1.4, style='rays')
    return finish(a)


def tempest_pterosaur(row):
    z0 = 0.3 + 0.4
    a = start(row, dict(main='#5aa8e8', belly='#e8f6ff', dark='#2a4a8a', accent='#ffd84a', horn='#ffffff', crest='#ff6a8a',
                        **{'*glow': '#7ac8ff', '*glow2': '#ffe14a', '*gold': '#ffd84a'}), 3.0, hover=5.5, z0=z0)
    B, Hd = quad(bw=0.9, bl=1.1, bh=0.8, legh=0.3, lw=0.2, hw=0.9, hd=0.84, hh=0.8, neck=0.4, toe='horn', head_fwd=0.3, leg_fl=0.36,
                 chest=True, rump=False)
    use('head')
    # long beak and the big swept-back crest (the silhouette)
    bk = b('beak', (0.34, 1.0, 0.26), mm('accent'), (0, Hd.front - 0.46, Hd.c.z - 0.16), bev=0.05)
    b('beak_low', (0.28, 0.8, 0.12), mm('belly'), (0, Hd.front - 0.38, Hd.c.z - 0.32), bev=0.03)
    p('mouth', (0.3, 0.86, 0.03), mm('line'), (0, Hd.front - 0.42, Hd.c.z - 0.27))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.2))
    for i in range(4):
        b('crest', (0.12, 0.3 + 0.06 * i, 0.3), mm('crest'), (0, Hd.back + 0.1 + i * 0.22, Hd.top + 0.1 + i * 0.12), rot=(-30, 0, 0), bev=0.04)
    eyes(Hd, 0.36, 0.25, 0.1, iris='#3a6ac8', glow='#7ac8ff', brow='#2a4a8a', tilt=-8)
    use('body')
    spots(B, 't', 5, mm('dark'), 0.14, seed=3, name='spot')
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)
    wings_big('body', (0.9 / 2 - 0.05, B.c.y - 0.2, B.top - 0.08), span=2.4, depth=1.3, th=0.14, mat='main', bone='dark', web='belly', n=4, up=16)
    tail_kit('long', 'body', (0, B.back - 0.02, B.c.z), 'main', 'crest', n=2, size=0.12, dark='dark')
    # rarity 6: storm-glowing wing veins, crest gems, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for sgn, n in LR:
        use('wing_' + n)
        for i in range(4):
            ln = 2.4 / 4
            cx = sgn * (0.9 / 2 - 0.05 + ln * (i + 0.5))
            z = B.top - 0.08 + math.tan(math.radians(16)) * ln * (i + 0.5)
            p('wing_vein', (ln * 0.7, 0.1, 0.1), mm('glow' if i % 2 else 'glow2'), (cx, B.c.y + 0.4, z + 0.04), rot=(0, -sgn * 16, sgn * 20))
            p('wing_star', (0.12, 0.12, 0.1), mm('glow2'), (cx, B.c.y + 0.9, z + 0.04), rot=(0, 0, 45))
        use('glow')
    for i in range(3):
        on(B, 't', 0, -0.3 + i * 0.3, (0.14, 0.14), mm('glow'), th=0.05, name='back_gem', rot=(0, 0, 45))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(4):
        p('crest_gem', (0.14, 0.1, 0.12), mm('glow2' if i % 2 else 'glow'), (0, Hd.back + 0.24 + i * 0.22, Hd.top + 0.22 + i * 0.12))
    p('beak_tip_glow', (0.24, 0.14, 0.2), mm('glow'), (0, bk.front + 0.06, bk.c.z))
    for i in range(5):
        p('beak_stripe', (0.36, 0.08, 0.05), mm('dark'), (0, Hd.front - 0.2 - i * 0.16, Hd.c.z - 0.02))
    for sgn, n in LR:
        for j in range(3):
            p('cheek_scale', (0.04, 0.14, 0.14), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y - 0.2 + j * 0.2, Hd.c.z))
    use('body')
    for sgn, n in LR:
        for j in range(6):
            p('fur', (0.06, 0.16, 0.18), mm('belly'), (sgn * (0.9 / 2 + 0.02), B.c.y - 0.4 + j * 0.16, B.c.z - 0.04 * (j % 2)))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_band', (ft.s.x + 0.04, ft.s.y * 0.8, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.04, 0.2))
    use('head')
    halo_kit(Hd, 'gold', r=0.44, n=8, dz=0.7, kind='shards')
    use('body')
    orbit_kit((0, 0.2, z0), 1.5, 6, 'glow', 'glow2', size=0.13, dz=0.3, shape='star')
    orbit_kit((0, 0.2, z0 - 0.2), 1.8, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.15, shape='cross')
    aura_kit(1.6, 6, motes=12, mote_col='glow', height=1.4, style='double')
    return finish(a)


ANIMALS = dict(storm_stone_spider=storm_stone_spider, storm_ram=storm_ram, highland_yak=highland_yak, thunder_eagle=thunder_eagle,
               storm_griffin=storm_griffin, tempest_pterosaur=tempest_pterosaur)
