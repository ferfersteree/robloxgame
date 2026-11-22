# Biome 2 - Deep Woods: shady pines, mist, fireflies, cobwebs
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 2
GROUND = '#4f9a58'
SKY = '#b4d6cc'
THEME = dict(bits=['#2f8a52', '#9a6a3a'], dust='#d9cdb2', glow='#c8ff5a', splash='#bfeaff', bit_name='хвоя и шишки')
BUSH_NAME = 'молодая ель с папоротником, грибами, шишками и паутиной'


def bush():
    B = begin_bush(NN)
    pine = mat('pine', '#2f8a52')
    pine2 = mat('pine2', '#246e44')
    pine3 = mat('pine3', '#44a866')
    fern = mat('fern', '#5cbf4a')
    trunk = mat('trunk', '#7a5234')
    cap = mat('cap', '#e8483c')
    stem = mat('stem', '#f6ead2')
    cone_m = mat('cone', '#9a6a3a')
    web = mat('web', '#f4f8ff', 'smooth')
    snow = mat('tip', '#bfe8c8')
    # trunk + stump
    part('big', (0, 0.2, 0.4), 'trunk')
    b('trunk', (0.7, 0.7, 1.6), trunk, (0, 0.2, 0.8))
    p('trunk_ring', (0.76, 0.76, 0.1), mat('trunk2', '#5e3e26'), (0, 0.2, 0.5))
    p('trunk_knot', (0.16, 0.05, 0.2), mat('trunk2', '#5e3e26'), (0.1, -0.17, 1.0))
    # spruce tiers (each tier = own part): stepped square slabs with a lighter fringe
    tiers = ((1.0, 4.6, 3.0), (1.85, 3.8, 2.6), (2.65, 3.0, 2.2), (3.35, 2.2, 1.7), (3.9, 1.4, 1.2))
    for i, (z, w, d) in enumerate(tiers):
        part('big', (0, 0.2, z), 'tier_%d' % i)
        m_ = (pine, pine2, pine, pine2, pine3)[i]
        T = b('tier', (w, d, 0.75), m_, (0, 0.2, z + 0.1))
        b('tier_top', (w * 0.7, d * 0.7, 0.3), m_, (0, 0.2, z + 0.55))
        nf = max(3, int(w / 0.75))
        for j in range(nf):
            u = (j + 0.5) / nf - 0.5
            p('fringe', (w / nf * 0.62, 0.1, 0.22), pine3 if j % 2 else m_, (u * w, 0.2 - d / 2 - 0.04, z - 0.3 - (0.06 if j % 2 else 0)))
            p('fringe', (w / nf * 0.62, 0.1, 0.22), pine3 if j % 2 == 0 else m_, (u * w, 0.2 + d / 2 + 0.04, z - 0.3))
        for sgn in (-1, 1):
            for j in range(2):
                p('fringe_side', (0.1, d * 0.3, 0.22), pine3, (sgn * (w / 2 + 0.04), 0.2 + (j - 0.5) * d * 0.5, z - 0.3))
        if i < 4:
            p('tier_tip', (0.16, 0.16, 0.05), snow, (-w * 0.3, 0.2 - d * 0.25, z + 0.49))
            p('tier_tip', (0.16, 0.16, 0.05), snow, (w * 0.28, 0.2 + d * 0.2, z + 0.49))
    part('small', (0, 0.2, 4.3), 'top')
    cn('top', 0.3, 0.5, pine3, (0, 0.2, 4.35), n=4)
    # ferns on both sides (low, wide) - they push the width to ~7 studs
    for sgn, n in LR:
        part('big', (sgn * 2.6, 0.0, 0.2), 'fern_base_' + n)
        b('fern_mound', (1.7, 1.6, 0.9), fern, (sgn * 2.6, 0.0, 0.5))
        b('fern_mound_top', (1.1, 1.1, 0.5), mat('fern2', '#48a83e'), (sgn * 2.55, 0.05, 1.1))
        for j, (dx, dy, rz) in enumerate(((0.75, -0.6, 30), (0.95, 0.2, 0), (0.5, 0.8, -35), (-0.2, -0.85, 70))):
            part('small', (sgn * (2.6 + dx * 0.4), dy * 0.4, 0.9), 'frond_%s%d' % (n, j))
            for k_ in range(4):
                t = k_ / 3.0
                b('frond', (0.5 - 0.1 * k_, 0.34 - 0.05 * k_, 0.12), fern if k_ % 2 else mat('fern3', '#74d85a'),
                  (sgn * (2.6 + dx * (0.5 + 0.55 * t)), dy * (0.5 + 0.55 * t), 0.95 + 0.34 * math.sin(math.pi * t * 0.9)), rot=(0, 0, sgn * rz), bev=0.03)
    # mushrooms
    for i, (x, y, s) in enumerate(((-1.2, -1.45, 1.0), (-0.75, -1.6, 0.65), (1.35, -1.5, 0.85), (1.9, -1.2, 0.55))):
        part('small', (x, y, 0.0), 'mushroom_%d' % i)
        b('stem', (0.2 * s, 0.2 * s, 0.4 * s), stem, (x, y, 0.2 * s), bev=0.03)
        b('cap', (0.56 * s, 0.56 * s, 0.26 * s), cap, (x, y, 0.5 * s), bev=0.06)
        p('cap_top', (0.3 * s, 0.3 * s, 0.1 * s), cap, (x, y, 0.66 * s))
        for dx, dy in ((-0.14, -0.1), (0.12, 0.08), (0.0, 0.16)):
            p('cap_dot', (0.1 * s, 0.1 * s, 0.03), stem, (x + dx * s, y + dy * s, 0.635 * s))
        p('cap_dot_f', (0.1 * s, 0.03, 0.08 * s), stem, (x + 0.1 * s, y - 0.285 * s, 0.5 * s))
    # pine cones hanging on the tiers
    for i, (x, y, z) in enumerate(((-1.6, -1.2, 0.72), (1.1, -1.05, 1.5), (-0.6, -0.9, 2.3), (0.9, 1.5, 0.7))):
        part('small', (x, y, z + 0.2), 'cone_%d' % i)
        b('cone', (0.22, 0.22, 0.32), cone_m, (x, y, z), bev=0.05)
        p('cone_scale', (0.26, 0.26, 0.06), mat('cone2', '#7a4e28'), (x, y, z + 0.05))
        p('cone_scale', (0.24, 0.24, 0.06), mat('cone2', '#7a4e28'), (x, y, z - 0.08))
        p('cone_stem', (0.05, 0.05, 0.1), trunk, (x, y, z + 0.2))
    # cobweb between the spruce and the right fern
    part('small', (1.7, -1.0, 1.4), 'web')
    for i, (ln, rz) in enumerate(((1.3, 0), (1.3, 45), (1.3, 90), (1.3, 135))):
        p('web_line', (ln, 0.02, 0.025), web, (1.7, -1.02, 1.4), rot=(0, rz, 0))
    for r in (0.25, 0.48):
        for i in range(4):
            ang = math.radians(i * 90 + 45)
            p('web_ring', (r * 1.42, 0.02, 0.022), web, (1.7 + math.cos(ang) * r, -1.02, 1.4 + math.sin(ang) * r), rot=(0, math.degrees(ang) + 90, 0))
    p('web_spider', (0.1, 0.06, 0.1), mat('spider', '#3a2a40'), (1.82, -1.05, 1.28))
    return finish_bush(B, has_r6=False)


# ---------------------------------------------------------------- animals
def roe(row):
    a = start(row, dict(main='#d2894a', belly='#fff1dc', dark='#7a4a26', accent='#ffffff', horn='#e9d8b0'), 2.8)
    B, Hd = quad(bw=0.74, bl=1.15, bh=0.62, legh=0.72, lw=0.18, hw=1.0, hd=0.84, hh=0.86, neck=0.2, hoof='dark', head_fwd=0.3)
    mz = muzzle(Hd, (0.42, 0.26, 0.28), -0.26, 'belly', nose=(0.16, 0.08, 0.1))
    cheeks(Hd, 'belly', (0.18, 0.16, 0.24), -0.26, whisk=0)
    eyes(Hd, 0.36, 0.25, 0.1, iris='#6a3a1c', lash=True, brow='#7a4a26', tilt=10)
    ears(Hd, 'long', 'main', 'pink', tip='dark', x=0.34, h=0.62, w=0.26, lean=24)
    horns(Hd, 'stub', 'horn', x=0.16, h=0.14, r=0.05)
    on(Hd, 'f', 0, 0.36, (0.2, 0.16), mm('belly'), name='fore_spot')
    on(Hd, 'f', 0, 0.22, (0.1, 0.1), mm('belly'), name='fore_spot')
    use('body')
    spots(B, 'tlr', 9, mm('accent'), 0.11, seed=2, name='fawn_spot')
    spots(a.bx['rump'], 'tlr', 6, mm('accent'), 0.1, seed=5, name='fawn_spot')
    fluff(a.bx['chest'], 'f', mm('accent'), 3, 0.8, 0.34)
    on(a.bx['rump'], 'k', 0, 0.1, (0.5, 0.36), mm('accent'), name='rump_patch')
    on(B, 't', 0, 0, (0.12, 0.9), mm('dark'), name='back_stripe')
    for ft in a.bx['feet']:
        p('sock', (ft.s.x - 0.02, ft.s.y - 0.04, 0.12), mm('belly'), (ft.c.x, ft.c.y + 0.02, ft.top + 0.08))
        p('knee', (0.06, 0.04, 0.08), mm('dark'), (ft.c.x, ft.front + 0.02, 0.5))
    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.26)
    return finish(a)


def boar(row):
    a = start(row, dict(main='#946a4c', belly='#c9a385', dark='#4e3528', accent='#fff6e0', snout='#f0a0a8'), 1.95)
    B, Hd = quad(bw=1.08, bl=1.35, bh=0.86, legh=0.34, lw=0.27, hw=1.16, hd=0.95, hh=0.92, head_up=0.36, hoof='dark', head_fwd=0.3)
    mz = muzzle(Hd, (0.52, 0.26, 0.38), -0.2, 'snout', nose=None, mouth=False)
    for sgn, n in LR:
        p('nostril', (0.1, 0.03, 0.14), mm('line'), (sgn * 0.11, mz.front - 0.008, mz.c.z + 0.03))
        b('tusk', (0.1, 0.1, 0.26), mm('accent'), (sgn * 0.3, mz.front + 0.06, mz.c.z + 0.02), rot=(0, sgn * 14, 0), bev=0.03)
        p('tusk_tip', (0.06, 0.06, 0.1), mm('accent'), (sgn * 0.34, mz.front + 0.06, mz.c.z + 0.2))
        p('jowl', (0.2, 0.2, 0.2), mm('belly'), (sgn * 0.42, Hd.front + 0.06, Hd.c.z - 0.3))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.4, Hd.front - 0.012, Hd.c.z - 0.1))
    p('snout_rim', (0.56, 0.05, 0.06), mm('dark'), (0, mz.front + 0.1, mz.top + 0.01))
    eyes(Hd, 0.3, 0.25, 0.16, iris='#5a2e1a', brow='#4e3528', tilt=-12, bdz=0.5)
    ears(Hd, 'point', 'main', 'pink', tip='dark', x=0.36, h=0.34, w=0.3, lean=30)
    use('body')
    # bristle mohawk along the head and back (the silhouette)
    for i in range(7):
        y = B.front + 0.05 + i * 0.2
        b('bristle', (0.2, 0.17, 0.24 + 0.1 * math.sin(i * 0.9)), mm('dark'), (0, y, B.top + 0.1 + 0.03 * math.sin(i * 0.9)), bev=0.04)
        p('bristle_tip', (0.1, 0.1, 0.1), mm('main'), (0, y, B.top + 0.3 + 0.08 * math.sin(i * 0.9)))
    use('head')
    for i in range(3):
        b('bristle', (0.2, 0.17, 0.22), mm('dark'), (0, Hd.c.y - 0.2 + i * 0.22, Hd.top + 0.1), bev=0.04)
    use('body')
    spots(B, 'lr', 6, mm('dark'), 0.2, seed=3, name='mud')
    spots(a.bx['rump'], 'lr', 4, mm('belly'), 0.16, seed=4, name='patch')
    fluff(a.bx['chest'], 'f', mm('main'), 3, 0.9, 0.3)
    for ft in a.bx['feet']:
        p('fetlock', (ft.s.x + 0.02, ft.s.y, 0.06), mm('belly'), (ft.c.x, ft.c.y, ft.top + 0.05))
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)
    return finish(a)


def badger(row):
    a = start(row, dict(main='#7a808e', belly='#34323c', dark='#2a2830', accent='#ffffff', light='#b6bcc8'), 1.5)
    B, Hd = quad(bw=1.02, bl=1.26, bh=0.62, legh=0.26, lw=0.27, hw=1.06, hd=0.96, hh=0.82, head_up=0.28, head_mat='accent',
                 leg_mat='dark', foot='dark', toe='accent', head_fwd=0.34)
    # two black stripes through the eyes, over the top of the head
    for sgn, n in LR:
        on(Hd, 'f', sgn * 0.25, 0.06, (0.27, Hd.s.z * 0.9), mm('dark'), name='mask')
        on(Hd, 't', sgn * 0.25, 0, (0.27, Hd.s.y * 0.94), mm('dark'), name='mask', th=0.12)
        on(Hd, 'l' if sgn < 0 else 'r', 0.0, 0.1, (Hd.s.y * 0.6, 0.3), mm('dark'), name='mask_side')
    mz = muzzle(Hd, (0.4, 0.3, 0.28), -0.26, 'accent', nose=(0.18, 0.09, 0.12))
    cheeks(Hd, 'accent', (0.2, 0.18, 0.24), -0.28, whisk=2)
    eyes(Hd, 0.32, 0.25, 0.1, iris='#8a5a2a', brow=None, sleepy=0.16)
    ears(Hd, 'round', 'dark', 'pink', x=0.4, h=0.22, w=0.24, lean=0)
    for sgn, n in LR:
        p('ear_rim', (0.26, 0.15, 0.06), mm('accent'), (sgn * 0.4 * Hd.s.x, Hd.c.y, Hd.top + 0.2))
    use('body')
    on(B, 't', 0, 0, (0.3, B.s.y * 0.96), mm('light'), name='back_stripe', th=0.05)
    on(a.bx['rump'], 't', 0, 0, (0.3, 0.5), mm('light'), name='back_stripe', th=0.05)
    stripes(B, 'lr', 4, mm('light'), 0.07, name='fur_streak', span=0.84)
    spots(a.bx['rump'], 'lr', 4, mm('light'), 0.12, seed=1, name='fur_fleck')
    fluff(a.bx['chest'], 'f', mm('dark'), 2, 0.8, 0.2)
    for ft in a.bx['feet']:
        p('claw_pad', (ft.s.x * 0.6, 0.03, 0.05), mm('light'), (ft.c.x, ft.back + 0.012, 0.06))
    tail_kit('thick', 'body', (a.tail_j[0], a.tail_j[1], a.tail_j[2] - 0.1), 'main', 'accent', size=0.11)
    p('tail_band', (0.24, 0.08, 0.2), mm('dark'), (0, a.tail_j[1] + 0.2, a.tail_j[2] - 0.1))
    return finish(a)


def wolf(row):
    """wolf frozen mid-leap: body stretched long and level, front legs reaching far forward, hind legs kicked back,
    ears flat back, tail streaming straight behind, mouth open in a happy pant"""
    a = start(row, dict(main='#7a8494', belly='#e8ecf0', dark='#3a3e48', accent='#b8c0cc', tongue='#ff7a8a'), 1.75)
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
    grid(Hd, 'l', 2, 2, mm('accent'), (0.08, 0.08), name='cheek_fur', span=(0.5, 0.5))
    grid(Hd, 'r', 2, 2, mm('accent'), (0.08, 0.08), name='cheek_fur', span=(0.5, 0.5))
    use('body')
    grid(B, 'u', 2, 4, mm('accent'), (0.1, 0.1), name='belly_fur', span=(0.6, 0.8))
    for k_ in range(8):
        ang = math.radians(k_ * 45)
        p('ruff_tuft', (0.16, 0.16, 0.16), mm('belly'), (math.cos(ang) * 0.45, -0.62, zb + math.sin(ang) * 0.42))
    for nm in [l for l in a.legs]:
        use(nm)
        sgn = -1 if nm.endswith('L') else 1
        fy = -1.3 if '_f' in nm else 2.05
        fz = zb - 0.72 if '_f' in nm else zb - 0.85
        for t in range(3):
            p('toe', (0.06, 0.05, 0.06), mm('dark'), (sgn * 0.26 + (t - 1) * 0.07, fy - (0.14 if '_f' in nm else -0.14), fz))
    use('body')
    sg('tail', 'body', (0, 1.35, zb + 0.15))
    a.tail = ['tail']
    for j in range(4):
        b('tail', (0.3 - 0.02 * j, 0.4, 0.3 - 0.02 * j), mm('main' if j < 3 else 'belly'), (0, 1.55 + j * 0.36, zb + 0.2 + 0.04 * j), bev=0.08)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.7, zb), Hit=(0, 0.4, zb + 0.35))
    return finish(a)


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
    grid(B, 'f', 3, 1, mm('belly'), (0.1, 0.1), name='chest_fur', span=(0.7, 0.1))
    use('head')
    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='brow_spot', span=(0.4, 0.4))
    grid(Hd, 'l', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_spot', span=(0.4, 0.4))
    grid(Hd, 'r', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_spot', span=(0.4, 0.4))
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


def sabertooth(row):
    a = start(row, dict(main='#f09a3a', belly='#fff0d0', dark='#8e4a1a', accent='#fffaf0', mane='#ffc060',
                        **{'*glow': '#c8ff5a', '*glow2': '#ffe14a'}), 2.3)
    B, Hd = quad(bw=1.06, bl=1.42, bh=0.86, legh=0.5, lw=0.33, hw=1.26, hd=1.0, hh=1.0, hump=0.16, toe='accent', leg_fl=0.5)
    mz = muzzle(Hd, (0.56, 0.3, 0.32), -0.26, 'belly', nose=(0.2, 0.09, 0.12), nose_mat='pink', top='main')
    for sgn, n in LR:      # the sabers: long, rounded, cute
        b('saber', (0.14, 0.14, 0.46), mm('accent'), (sgn * 0.2, mz.front + 0.08, mz.bot - 0.16), bev=0.05)
        b('saber_tip', (0.1, 0.1, 0.2), mm('accent'), (sgn * 0.2, mz.front + 0.09, mz.bot - 0.44), bev=0.04)
        b('mane', (0.26, 0.34, 0.5), mm('mane'), (sgn * (Hd.s.x / 2 + 0.06), Hd.c.y + 0.12, Hd.c.z - 0.16), bev=0.05)
        p('mane_tuft', (0.16, 0.2, 0.2), mm('mane'), (sgn * (Hd.s.x / 2 + 0.18), Hd.c.y + 0.1, Hd.c.z - 0.44))
        p('mane_tuft', (0.14, 0.18, 0.18), mm('mane'), (sgn * (Hd.s.x / 2 + 0.2), Hd.c.y + 0.16, Hd.c.z + 0.1))
        for j in range(3):
            on(Hd, 'l' if sgn < 0 else 'r', -0.2 + j * 0.02, 0.3 - j * 0.24, (0.34 - j * 0.06, 0.08), mm('dark'), name='cheek_stripe')
            on(Hd, 'f', sgn * (0.36 + j * 0.04), 0.4 - j * 0.02, (0.06, 0.16 - j * 0.03), mm('dark'), name='fore_stripe')
    cheeks(Hd, 'belly', (0.3, 0.26, 0.32), -0.26, whisk=3)
    for sgn, n in LR:
        for j in range(3):
            p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * (0.12 + 0.07 * j), mz.front - 0.008, mz.c.z + 0.02 + 0.05 * (j % 2)))
    eyes(Hd, 0.33, 0.25, 0.1, iris='#3a8a2a', glow='#c8ff5a', brow='#8e4a1a', tilt=-6, lash=False)
    ears(Hd, 'round', 'main', 'pink', x=0.36, h=0.3, w=0.32, lean=8)
    for i in range(4):
        b('crest', (0.2, 0.2, 0.2 + 0.06 * (i % 2)), mm('mane'), (0, Hd.c.y - 0.3 + i * 0.2, Hd.top + 0.1), bev=0.05)
    use('body')
    stripes(B, 'lr', 5, mm('dark'), 0.1, name='stripe', span=0.86)
    stripes(B, 't', 5, mm('dark'), 0.1, name='stripe', span=0.86)
    stripes(a.bx['rump'], 'lr', 2, mm('dark'), 0.1, name='stripe', span=0.6)
    stripes(a.bx['hump'], 't', 2, mm('dark'), 0.1, name='stripe', span=0.6)
    fluff(a.bx['chest'], 'f', mm('mane'), 4, 0.95, 0.38)
    for sgn, n in LR:
        for j in range(3):
            p('shoulder_fur', (0.16, 0.24, 0.2 - 0.03 * j), mm('mane'), (sgn * (B.s.x / 2 + 0.03), B.front + 0.16 + j * 0.03, B.top - 0.08 - j * 0.17))
    for ft in a.bx['feet']:
        for j in range(2):
            p('leg_band', (ft.s.x - 0.02, 0.36, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.07, 0.3 + j * 0.16))
    tail_kit('long', 'body', a.tail_j, 'main', 'dark', n=2, size=0.2, dark='dark')
    # rarity 5: glowing pattern, glowing saber tips, floating leaves, yellow aura
    glow_marks(B, ('l', 'r'), 4, 'glow', style='stripe', size=0.12, col2='glow2')
    use('glow')
    for i in range(4):
        on(B, 't', 0, -0.36 + i * 0.24, (0.14, 0.14), mm('glow2' if i % 2 else 'glow'), th=0.045, name='glow_star', rot=(0, 0, 45))
    for sgn, n in LR:
        on(a.bx['rump'], 'l' if sgn < 0 else 'r', 0, 0.1, (0.16, 0.16), mm('glow'), th=0.035, name='glow_star', rot=(45, 0, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.c.z + 0.4))
    a.glow.append('glow_h')
    for i, (dx, dz, w, h) in enumerate(((0, 0.0, 0.1, 0.16), (-0.1, 0.06, 0.07, 0.07), (0.1, 0.06, 0.07, 0.07), (0, 0.15, 0.06, 0.06))):
        p('fore_rune', (w, 0.03, h), mm('glow'), (dx, Hd.front - 0.012, Hd.c.z + 0.34 + dz))
    for sgn, n in LR:
        p('saber_glow', (0.11, 0.11, 0.08), mm('glow2'), (sgn * 0.2, mz.front + 0.09, mz.bot - 0.56))
        p('saber_ring', (0.16, 0.16, 0.04), mm('glow'), (sgn * 0.2, mz.front + 0.08, mz.bot - 0.02))
        on(Hd, 'f', sgn * 0.4, -0.32, (0.08, 0.08), mm('glow2'), th=0.035, name='cheek_star', rot=(0, 45, 0))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('paw_glow', (ft.s.x + 0.03, ft.s.y * 0.5, 0.05), mm('glow'), (ft.c.x, ft.c.y + 0.1, ft.top + 0.06))
    use('tail')
    p('tail_glow', (0.24, 0.1, 0.24), mm('glow2'), (0, a.tail_j[1] + 0.25, a.tail_j[2]))
    use('tail2')
    p('tail_glow', (0.2, 0.1, 0.2), mm('glow'), (0, a.tail_j[1] + 0.7, a.tail_j[2] + 0.05))
    use('body')
    orbit_kit((0, 0.2, 1.25), 1.5, 6, 'glow', 'glow2', size=0.13, dz=0.4, shape='flame')
    aura_kit(1.55, 5, motes=10, mote_col='glow', height=1.9, style='rays')
    return finish(a)


ANIMALS = dict(roe=roe, boar=boar, badger=badger, wolf=wolf, lynx=lynx, sabertooth=sabertooth)
