# Biome 8 - Emerald Jungle: broad leaves, vines, temples
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 8
GROUND = '#3f9652'
SKY = '#cdf2dc'
THEME = dict(bits=['#3fbe5a', '#ff5a8a'], dust='#cfe0b0', glow='#5aff8a', splash='#aef0d0', bit_name='листья и лепестки')
BUSH_NAME = 'куст из огромных листьев с лианами, тропическими цветами и замшелым камнем храма'


def bush():
    B = begin_bush(NN)
    l1 = mat('leaf', '#2fa84e')
    l2 = mat('leaf2', '#48c864')
    l3 = mat('leaf3', '#1f8a40')
    vein = mat('vein', '#9af0a0')
    stem = mat('stem', '#3a7a3a')
    stone = mat('stone', '#8a9a8a')
    stone2 = mat('stone2', '#6a7a6c')
    moss = mat('moss', '#5ab84a')
    fl1 = mat('flower', '#ff4a7a')
    fl2 = mat('flower2', '#ffb020')
    vine = mat('vine', '#4a9a3a')
    gem = mat('gem', '#5aff8a', 'neon', 2.0)
    # core mound of foliage
    part('big', (0, 0.3, 0.2), 'core')
    b('core', (3.6, 2.4, 1.6), l3, (0, 0.3, 0.8), bev=0.16)
    b('core_top', (2.4, 1.6, 0.8), l1, (0, 0.4, 1.9), bev=0.14)
    # giant leaves: each a stepped blade with a light midrib, fanning out
    spec = ((-2.4, -0.2, 2.2, -38, 0), (-1.4, 0.9, 3.1, -18, 1), (0.0, 1.2, 3.6, 0, 2), (1.4, 0.9, 3.2, 18, 0), (2.4, -0.2, 2.3, 38, 1),
            (-0.9, -0.9, 2.2, -24, 2), (0.9, -0.9, 2.3, 24, 0), (-3.0, 0.8, 1.6, -58, 2), (3.0, 0.8, 1.7, 58, 1))
    for i, (x, y, h, lean, mi) in enumerate(spec):
        part('big', (x * 0.6, y * 0.7 + 0.3, 0.8), 'leaf_%d' % i)
        m_ = (l1, l2, l3)[mi]
        r = math.radians(lean)
        for k_ in range(4):
            t = (k_ + 0.5) / 4.0
            w = (1.3, 1.6, 1.3, 0.8)[k_]
            cx = x * 0.6 + math.sin(r) * h * t
            cz = 0.8 + math.cos(r) * h * t
            b('blade', (w, 0.16, h / 4 + 0.06), m_, (cx, y * 0.7 + 0.3 - 0.06 * k_, cz), rot=(0, lean, 0), bev=0.05)
            p('midrib', (0.12, 0.18, h / 4), vein, (cx, y * 0.7 + 0.3 - 0.06 * k_ - 0.01, cz), rot=(0, lean, 0))
            if k_ in (1, 2):
                p('rib', (w * 0.8, 0.18, 0.06), vein, (cx, y * 0.7 + 0.3 - 0.06 * k_ - 0.01, cz), rot=(0, lean + 18, 0))
        p('tip', (0.3, 0.14, 0.3), m_, (x * 0.6 + math.sin(r) * (h + 0.1), y * 0.7 + 0.1, 0.8 + math.cos(r) * (h + 0.1)), rot=(0, lean + 45, 0))
    # mossy temple stone with a carved face and a glowing gem
    part('big', (2.6, -1.0, 0.1), 'idol')
    b('idol', (1.3, 1.1, 1.7), stone, (2.6, -1.0, 0.85), rot=(0, 0, -10), bev=0.1)
    b('idol_cap', (1.5, 1.3, 0.3), stone2, (2.6, -1.0, 1.84), rot=(0, 0, -10), bev=0.06)
    p('idol_moss', (1.0, 1.0, 0.12), moss, (2.6, -1.0, 2.04), rot=(0, 0, -10))
    for sgn in (-1, 1):
        p('idol_eye', (0.24, 0.05, 0.16), stone2, (2.6 + sgn * 0.26, -1.56, 1.2), rot=(0, 0, -10))
    p('idol_mouth', (0.6, 0.05, 0.12), stone2, (2.6, -1.56, 0.7), rot=(0, 0, -10))
    p('idol_gem', (0.2, 0.06, 0.2), gem, (2.6, -1.57, 1.52), rot=(0, 45, -10))
    part('big', (-2.8, -1.0, 0.1), 'slab')
    b('slab', (1.4, 0.9, 0.6), stone, (-2.8, -1.0, 0.3), rot=(0, 0, 12), bev=0.08)
    p('slab_moss', (1.0, 0.7, 0.1), moss, (-2.8, -1.0, 0.64), rot=(0, 0, 12))
    p('slab_rune', (0.6, 0.05, 0.1), stone2, (-2.85, -1.46, 0.36), rot=(0, 0, 12))
    # tropical flowers
    for i, (x, y, z, m_) in enumerate(((-1.4, -1.0, 1.2, fl1), (0.3, -1.0, 1.7, fl2), (1.6, -0.9, 1.3, fl1), (-0.5, 0.2, 2.5, fl2), (0.9, 0.3, 2.4, fl1))):
        part('small', (x, y, z), 'flower_%d' % i)
        for j in range(5):
            ang = math.radians(j * 72)
            b('petal', (0.3, 0.14, 0.3), m_, (x + math.cos(ang) * 0.26, y - 0.04, z + math.sin(ang) * 0.26), rot=(0, -math.degrees(ang), 0), bev=0.05)
        b('flower_core', (0.2, 0.2, 0.2), mat('core', '#fff0a0'), (x, y - 0.08, z), bev=0.05)
        p('stamen', (0.06, 0.2, 0.06), mat('core2', '#ff8a2a'), (x, y - 0.22, z))
    # hanging vines with small leaves
    for i, (x, y, h) in enumerate(((-1.9, -0.6, 1.8), (-0.3, -0.92, 1.3), (1.3, -0.7, 1.9), (2.0, 0.4, 1.4))):
        part('small', (x, y, 2.3), 'vine_%d' % i)
        b('vine', (0.1, 0.1, h), vine, (x, y, 2.3 - h / 2), bev=0.02)
        for j in range(3):
            p('vine_leaf', (0.24, 0.08, 0.16), l2, (x + 0.14 * (1 if j % 2 else -1), y, 2.2 - j * h * 0.3))
        p('vine_bud', (0.14, 0.14, 0.14), fl2 if i % 2 else fl1, (x, y, 2.3 - h - 0.04), rot=(45, 45, 0))
    # ferns at the feet
    for i, (x, y) in enumerate(((-1.6, -1.6), (0.2, -1.8), (1.4, -1.6))):
        part('small', (x, y, 0.1), 'fern_%d' % i)
        for k_ in range(5):
            ang = (k_ - 2) * 28
            b('fern', (0.2, 0.14, 0.9), l2 if k_ % 2 else l1, (x + math.sin(math.radians(ang)) * 0.4, y, 0.5), rot=(0, ang, 0), bev=0.03)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def jade_tapir(row):
    a = start(row, dict(main='#3a4a52', belly='#f2f6f4', dark='#24323a', accent='#7fd8b0', snout='#4a5a62'), 1.95)
    B, Hd = quad(bw=1.06, bl=1.44, bh=0.92, legh=0.4, lw=0.28, hw=1.12, hd=0.98, hh=0.94, head_up=0.36, toe='accent', head_fwd=0.36, ntoe=3)
    # short flexible trunk-snout (2 stacked blocks drooping down)
    use('head')
    b('snout', (0.46, 0.4, 0.4), mm('snout'), (0, Hd.front - 0.14, Hd.c.z - 0.2), bev=0.07)
    b('snout_tip', (0.34, 0.26, 0.3), mm('snout'), (0, Hd.front - 0.3, Hd.c.z - 0.46), bev=0.07)
    for sgn, n in LR:
        p('nostril', (0.07, 0.03, 0.05), mm('pink'), (sgn * 0.08, Hd.front - 0.435, Hd.c.z - 0.5))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.42, Hd.front - 0.012, Hd.c.z - 0.22))
        p('ear_rim', (0.16, 0.05, 0.06), mm('belly'), (sgn * 0.4 * Hd.s.x, Hd.c.y - 0.08, Hd.top + 0.26))
    eyes(Hd, 0.3, 0.27, 0.12, iris='#2a6a5a', brow='#24323a', tilt=10, lash=True)
    ears(Hd, 'round', 'main', 'pink', x=0.4, h=0.26, w=0.24, lean=14)
    use('body')
    # the white saddle (Malayan tapir) + jade speckles
    on(B, 't', 0, 0.16, (B.s.x + 0.04, B.s.y * 0.56), mm('belly'), name='saddle', th=0.06)
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', 0.16, 0.0, (B.s.y * 0.56, B.s.z + 0.02), mm('belly'), name='saddle', th=0.05)
        on(a.bx['rump'], 'l' if sgn < 0 else 'r', 0, 0, (0.5, 0.8), mm('belly'), name='saddle', th=0.035)
    on(a.bx['rump'], 't', 0, 0, (1.0, 0.5), mm('belly'), name='saddle', th=0.06)
    on(a.bx['rump'], 'k', 0, 0, (1.0, 0.76), mm('belly'), name='saddle', th=0.04)
    spots(B, 't', 5, mm('accent'), 0.1, seed=3, name='jade')
    fluff(a.bx['chest'], 'f', mm('dark'), 3, 0.9, 0.3)
    for i in range(4):
        b('mane', (0.16, 0.18, 0.14), mm('dark'), (0, B.front + 0.06 + i * 0.16, B.top + 0.06), bev=0.04)
    for ft in a.bx['feet']:
        p('ankle', (ft.s.x + 0.02, ft.s.y * 0.8, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.03, ft.top + 0.05))
    tail_kit('stub', 'body', a.tail_j, 'belly', 'dark', size=0.16)
    return finish(a)


def toucan(row):
    z0 = 0.26 + 0.46
    a = start(row, dict(main='#24242e', belly='#fff6d8', dark='#14141c', accent='#ffd21a', leg='#5a8ad8', beak='#ffb020', beak_tip='#e8402a',
                        beak2='#5ac85a'), 1.95, hover=3.0, z0=z0)
    B, Hd = bird(bw=0.9, bl=1.1, bh=0.92, legh=0.26, lw=0.13, hw=0.9, hd=0.82, hh=0.84, neck=0.06, beak=(0.42, 1.0, 0.46),
                 wing=(0.14, 0.8, 0.5), fly=True, wing_span=1.3, ntail=3, tail_l=0.5, tail_mat='dark', beak_low=True)
    bk = a.bx['beak']
    use('head')
    # the huge striped bill (the silhouette)
    p('beak_band', (0.44, 0.12, 0.48), mm('beak2'), (0, bk.c.y + 0.2, bk.c.z))
    p('beak_band', (0.44, 0.1, 0.48), mm('accent'), (0, bk.c.y - 0.06, bk.c.z))
    b('beak_tip', (0.34, 0.2, 0.34), mm('beak_tip'), (0, bk.front + 0.02, bk.c.z - 0.06), bev=0.06)
    p('beak_ridge', (0.14, 0.8, 0.06), mm('beak_tip'), (0, bk.c.y, bk.top + 0.02))
    b('bib', (0.86, 0.14, 0.5), mm('belly'), (0, Hd.front + 0.02, Hd.bot + 0.14), bev=0.05)
    p('bib_rim', (0.9, 0.12, 0.08), mm('beak_tip'), (0, Hd.front + 0.03, Hd.bot - 0.1))
    for sgn, n in LR:
        on(Hd, 'f', sgn * 0.25, 0.14, (0.36, 0.36), mm('leg'), name='eye_ring')
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.14))
    eyes(Hd, 0.34, 0.25, 0.14, iris='#24242e', brow=None)
    use('body')
    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('belly'), 3, 0.9, 0.36)
    for i in range(3):
        p('back_feather', (0.26, 0.3, 0.05), mm('dark'), ((i - 1) * 0.28, B.c.y + 0.1, B.top + 0.03))
    p('rump_red', (0.5, 0.2, 0.3), mm('beak_tip'), (0, B.back + 0.26, B.c.z + 0.2))
    for sgn, n in LR:
        use('wing_' + n)
        wb = a.bx['wings'][0 if sgn < 0 else 1]
        for i in range(3):
            p('wing_tip', (0.2, 0.2, 0.05), mm('leg'), (sgn * (B.s.x / 2 + 0.3 + i * 0.4), 0.76 - 0.06 * i, wb.c.z + 0.02))
    use('body')
    return finish(a)


def leafcutter_ant(row):
    a = start(row, dict(main='#b8502a', belly='#d8703a', dark='#6a2a16', accent='#ffb020', leaf='#4fc85a', leaf2='#2f9a44'), 3.3)
    B, Hd = bug(bw=0.74, bl=0.8, bh=0.6, legh=0.5, hw=0.92, hd=0.7, hh=0.74, nleg=3, leg_w=0.1, leg_span=0.44, antenna=0.44, head_z=0.16,
                shell='main', under='belly', leg_mat='dark')
    use('head')
    for sgn, n in LR:
        b('mandible', (0.12, 0.3, 0.12), mm('dark'), (sgn * 0.2, Hd.front - 0.12, Hd.bot + 0.1), rot=(0, 0, sgn * 20), bev=0.03)
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.2))
    eyes(Hd, 0.4, 0.25, 0.08, iris='#3a1a10', brow='#6a2a16', tilt=-10)
    use('body')
    # three body sections: thorax (the kit body), waist, big abdomen
    b('waist', (0.3, 0.3, 0.3), mm('dark'), (0, B.back + 0.1, B.c.z - 0.05), bev=0.06)
    ab = b('abdomen', (0.9, 1.0, 0.8), mm('main'), (0, B.back + 0.7, B.c.z + 0.02), bev=0.14)
    b('abdomen_tip', (0.5, 0.3, 0.44), mm('belly'), (0, B.back + 1.3, B.c.z - 0.06), bev=0.1)
    for j in range(3):
        p('abdomen_band', (0.94, 0.1, 0.84), mm('dark'), (0, B.back + 0.4 + j * 0.3, B.c.z + 0.02))
    for sgn, n in LR:
        cn('thorax_spine', 0.08, 0.26, mm('dark'), (sgn * 0.2, B.c.y, B.top + 0.1), (sgn * 0.4, 0.3, 1))
        p('thorax_plate', (0.05, 0.4, 0.3), mm('belly'), (sgn * (B.s.x / 2 + 0.01), B.c.y, B.c.z))
    # rarity 3 accessory: the big leaf it carries like a sail (own segment so it sways) + pattern on the leaf
    sg('leaf', 'head', (0, Hd.front - 0.2, Hd.bot + 0.14))
    b('leaf_stem', (0.08, 0.08, 1.0), mm('leaf2'), (0, Hd.front - 0.24, Hd.c.z + 0.5), rot=(12, 0, 0), bev=0.02)
    for k_ in range(4):
        w = (0.9, 1.3, 1.1, 0.6)[k_]
        b('leaf', (w, 0.1, 0.44), mm('leaf'), (0, Hd.front - 0.3 + 0.1 * k_, Hd.top + 0.5 + k_ * 0.4), rot=(12, 0, 0), bev=0.04)
        p('leaf_rib', (w * 0.8, 0.12, 0.05), mm('leaf2'), (0, Hd.front - 0.31 + 0.1 * k_, Hd.top + 0.5 + k_ * 0.4), rot=(12, 0, 8))
    p('leaf_midrib', (0.08, 0.12, 1.7), mm('leaf2'), (0, Hd.front - 0.16, Hd.top + 1.1), rot=(12, 0, 0))
    p('leaf_bite', (0.3, 0.14, 0.3), mm('leaf2'), (0.5, Hd.front - 0.16, Hd.top + 1.0), rot=(12, 45, 0))
    for i in range(3):
        p('leaf_dew', (0.1, 0.06, 0.1), mm('white'), (-0.3 + i * 0.3, Hd.front - 0.24 + 0.06 * i, Hd.top + 0.7 + i * 0.36))

    def leaf_idle(c, n):
        for x, r in ((1, 0), (n // 4, 6), (n // 2, 0), (3 * n // 4, -6), (n, 0)):
            k(c, 'leaf', x, rot=(0, r, 0))
    a.extra_idle.append(leaf_idle)
    for k_ in range(4):
        for sgn, n in LR:
            p('leaf_vein', (0.3, 0.12, 0.04), mm('leaf2'), (sgn * 0.26, Hd.front - 0.31 + 0.1 * k_, Hd.top + 0.42 + k_ * 0.4), rot=(12, sgn * 25, 0))
    use('head')
    for sgn, n in LR:
        for j in range(3):
            p('head_plate', (0.16, 0.16, 0.04), mm('belly'), (sgn * 0.24, Hd.c.y - 0.2 + j * 0.2, Hd.top + 0.02))
        p('jaw_tooth', (0.06, 0.08, 0.06), mm('accent'), (sgn * 0.14, Hd.front - 0.28, Hd.bot + 0.1))
    use('body')
    for sgn, n in LR:
        for j in range(5):
            p('abdomen_stud', (0.05, 0.12, 0.12), mm('accent'), (sgn * 0.46, B.back + 0.34 + j * 0.18, B.c.z + 0.2 - 0.06 * (j % 2)), rot=(45, 0, 0))
        for j in range(3):
            p('abdomen_hair', (0.05, 0.05, 0.12), mm('dark'), (sgn * 0.2, B.back + 0.5 + j * 0.26, B.c.z + 0.46))
            p('thorax_stud', (0.1, 0.1, 0.05), mm('accent'), (sgn * 0.16, B.c.y - 0.2 + j * 0.2, B.top + 0.2))
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_band', (0.08, 0.14, 0.14), mm('accent'), (j.x + sgn * 0.2, j.y, j.z + 0.04))
    use('body')
    return finish(a)


def jaguar(row):
    """stalking jaguar: long low slinky body pressed to the ground, legs bent, extra-long tail raised in a question mark"""
    a = start(row, dict(main='#f2b84a', belly='#fff4d8', dark='#3a2a22', accent='#d8863a', **{'*glow': '#5aff8a'}), 2.24)
    B, Hd = quad(bw=0.9, bl=2.0, bh=0.56, legh=0.26, lw=0.3, hw=1.1, hd=0.9, hh=0.8, head_up=0.2, toe='dark', leg_fl=0.5, head_fwd=0.5,
                 rump=False, chest=False)
    mz = muzzle(Hd, (0.5, 0.26, 0.28), -0.26, 'belly', nose=(0.2, 0.09, 0.12), nose_mat='pink', top='main', fangs=1)
    cheeks(Hd, 'belly', (0.26, 0.22, 0.28), -0.25, whisk=3)
    eyes(Hd, 0.36, 0.25, 0.12, iris='#2a8a4a', glow='#5aff8a', brow='#3a2a22', tilt=-16, sleepy=0.2)
    for sgn, n in LR:
        b('ear', (0.24, 0.12, 0.2), mm('main'), (sgn * 0.38, Hd.c.y + 0.1, Hd.top + 0.06), bev=0.05)
        p('ear_back', (0.24, 0.05, 0.14), mm('dark'), (sgn * 0.38, Hd.c.y + 0.17, Hd.top + 0.06))
    use('body')

    def rosette(box, f, u, v, s=0.2):
        on(box, f, u, v, (s, s), mm('dark'), name='rosette', th=0.03)
        on(box, f, u, v, (s * 0.5, s * 0.5), mm('accent'), name='rosette_in', th=0.04)
    for f in ('l', 'r', 't'):
        for i, (u, v) in enumerate(((-0.4, 0.2), (-0.2, -0.2), (0.0, 0.22), (0.2, -0.2), (0.4, 0.2))):
            rosette(B, f, u, v, 0.2)
    use('head')
    for i, (u, v) in enumerate(((-0.25, 0.2), (0.25, 0.2), (0.0, 0.0))):
        on(Hd, 't', u, v, (0.12, 0.12), mm('dark'), name='head_spot')
    use('body')
    for ft in a.bx['feet']:
        p('leg_spot', (0.1, 0.03, 0.1), mm('dark'), (ft.c.x, ft.c.y - 0.16, 0.2))
    # long question-mark tail held high (3 segments)
    sg('tail', 'body', (0, B.back - 0.04, B.c.z + 0.1))
    a.tail = ['tail']
    cur = Vector((0, B.back - 0.04, B.c.z + 0.1))
    par = 'tail'
    for i, d in enumerate(((0, 0.4, 0.3), (0, 0.2, 0.5), (0, -0.1, 0.4), (0, -0.3, 0.1))):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        if i:
            sg(nm, par, tuple(cur))
            a.tail.append(nm)
            par = nm
        c = cur + Vector(d) * 0.5
        b('tail', (0.2, 0.2, 0.2 + Vector(d).length * 0.8), mm('main' if i % 2 == 0 else 'accent'), tuple(c), rot=(-math.degrees(math.atan2(d[1], d[2])), 0, 0), bev=0.04)
        p('tail_ring', (0.22, 0.22, 0.06), mm('dark'), tuple(c))
        cur = cur + Vector(d)
    p('tail_tip', (0.22, 0.22, 0.22), mm('dark'), tuple(cur))
    use('body')
    # rarity 4: emerald temple runes on the back, glowing tail tip, firefly sparks
    glow_marks(B, ('t',), 4, 'glow', style='rune', size=0.14)
    use(a.tail[-1])
    p('tail_glow', (0.16, 0.16, 0.16), mm('glow'), tuple(cur + Vector((0, 0, 0.16))), rot=(45, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.top))
    a.glow.append('glow_h')
    on(Hd, 'f', 0, 0.36, (0.14, 0.14), mm('glow'), th=0.035, name='fore_rune', rot=(0, 45, 0))
    use('body')
    aura_kit(1.5, 4, motes=8, mote_col='glow', height=1.4)
    return finish(a)


def jungle_gorilla(row):
    a = start(row, dict(main='#3a3e4a', belly='#5a6070', dark='#24262e', accent='#c8d0dc', face='#7a7e8c', leaf='#3fbe5a',
                        **{'*glow': '#5aff8a', '*glow2': '#ffe14a'}), 2.95)
    B, Hd = biped(tw=1.6, td=1.0, th=1.1, legh=0.44, lw=0.46, hw=1.2, hd=1.0, hh=0.96, arm_l=1.4, arm_w=0.5, hand=0.6, shoulder=0.36,
                  foot='face', toe='dark', hand_mat='face')
    use('head')
    fc = b('face', (0.9, 0.1, 0.66), mm('face'), (0, Hd.front - 0.02, Hd.c.z - 0.1), bev=0.04)
    mz = muzzle(Hd, (0.56, 0.22, 0.32), -0.3, 'face', nose=None, mouth=True)
    for sgn, n in LR:
        p('nostril', (0.1, 0.04, 0.07), mm('dark'), (sgn * 0.09, mz.front - 0.01, mz.c.z + 0.1))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.34, fc.front - 0.012, Hd.c.z - 0.22))
        b('ear', (0.12, 0.18, 0.24), mm('face'), (sgn * (Hd.s.x / 2 + 0.04), Hd.c.y - 0.06, Hd.c.z + 0.08), bev=0.04)
    b('brow_ridge', (0.96, 0.16, 0.12), mm('main'), (0, Hd.front + 0.02, Hd.c.z + 0.42), bev=0.04)
    b('crest', (0.6, 0.6, 0.26), mm('main'), (0, Hd.c.y + 0.1, Hd.top + 0.14), bev=0.1)
    eyes(Hd, 0.3, 0.2, 0.1, iris='#2a8a4a', glow='#5aff8a', brow=None, tilt=0)
    use('body')
    # silver back, chest plates, fur tufts
    on(B, 'k', 0, 0.0, (B.s.x * 0.8, B.s.z * 0.8), mm('accent'), name='silverback', th=0.06)
    on(B, 't', 0, 0.2, (B.s.x * 0.7, 0.4), mm('accent'), name='silverback', th=0.05)
    for sgn, n in LR:
        b('pec', (0.6, 0.12, 0.44), mm('belly'), (sgn * 0.34, B.front - 0.04, B.c.z + 0.22), bev=0.06)
        for j in range(3):
            p('ab', (0.3, 0.06, 0.16), mm('belly'), (sgn * 0.17, B.front - 0.03, B.c.z - 0.14 - j * 0.18))
        for j in range(4):
            p('fur', (0.2, 0.26, 0.22), mm('dark' if j % 2 else 'main'), (sgn * (B.s.x / 2 + 0.03), B.c.y - 0.3 + j * 0.2, B.c.z + 0.3 - j * 0.2))
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        sgn = 1 if hb_.c.x > 0 else -1
        for j in range(3):
            p('arm_fur', (0.16, 0.5, 0.2), mm('dark' if j % 2 else 'main'), (hb_.c.x + sgn * 0.28, 0.05, hb_.c.z + 0.36 + j * 0.26))
        p('wrist_band', (hb_.s.x + 0.08, hb_.s.y + 0.08, 0.14), mm('leaf'), (hb_.c.x, 0.0, hb_.top + 0.06))
        p('wrist_gem', (0.16, 0.06, 0.16), mm('glow2'), (hb_.c.x, -hb_.s.y / 2 - 0.06, hb_.top + 0.06), rot=(0, 45, 0))
        p('knuckle', (hb_.s.x * 0.9, 0.08, 0.1), mm('dark'), (hb_.c.x, -hb_.s.y / 2 - 0.02, hb_.c.z + 0.1))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('ankle_fur', (ft.s.x + 0.06, ft.s.y * 0.7, 0.16), mm('main'), (ft.c.x, ft.c.y + 0.12, ft.top + 0.1))
        p('ankle_band', (ft.s.x + 0.08, ft.s.y * 0.72, 0.06), mm('leaf'), (ft.c.x, ft.c.y + 0.12, ft.top + 0.22))
    use('body')
    for i in range(4):
        for j in range(3):
            p('back_fur', (0.26, 0.1, 0.2), mm('dark'), ((i - 1.5) * 0.34, B.back + 0.08, B.c.z + 0.34 - j * 0.26 + 0.06 * (i % 2)))
    for i in range(8):
        p('hip_fur', (0.2, 0.12, 0.16), mm('dark' if i % 2 else 'main'), ((i - 3.5) * 0.2, B.back + 0.06, B.bot + 0.1))
    for i in range(6):
        p('chest_hair', (0.14, 0.06, 0.14), mm('dark'), ((i - 2.5) * 0.16, B.front - 0.11, B.c.z + 0.46 - 0.05 * (i % 2)))
    use('head')
    for i in range(4):
        p('head_fur', (0.2, 0.14, 0.2), mm('dark'), ((i - 1.5) * 0.26, Hd.back + 0.04, Hd.c.z + 0.1 * (i % 2)))
        p('head_fur', (0.22, 0.2, 0.12), mm('dark'), ((i - 1.5) * 0.24, Hd.c.y + 0.2, Hd.top + 0.04))
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        sgn = 1 if hb_.c.x > 0 else -1
        for j in range(4):
            p('arm_fur_b', (0.3, 0.14, 0.2), mm('main' if j % 2 else 'dark'), (hb_.c.x, 0.32, hb_.c.z + 0.3 + j * 0.24))
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(4):
            p('leg_fur', (0.14, 0.2, 0.14), mm('dark' if j % 2 else 'main'), (ft.c.x + (0.26 if ft.c.x > 0 else -0.26), ft.c.y + 0.2, 0.2 + j * 0.08))
        p('toe_big', (0.14, 0.12, 0.1), mm('dark'), (ft.c.x - (0.2 if ft.c.x > 0 else -0.2), ft.front + 0.1, 0.06))
    use('body')
    # leaf skirt (accessory) and vine sash
    for i in range(7):
        ang = (i - 3) * 22
        p('skirt_leaf', (0.26, 0.1, 0.34), mm('leaf'), (math.sin(math.radians(ang)) * 0.8, B.front - 0.02 + (1 - math.cos(math.radians(ang))) * 0.5, B.bot + 0.02))
    # rarity 5: glowing war paint, glowing leaf crown, orbiting leaves, yellow aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(3):
            p('paint', (0.34 - 0.06 * j, 0.04, 0.07), mm('glow'), (sgn * 0.34, B.front - 0.11, B.c.z + 0.36 - j * 0.12), rot=(0, sgn * 20, 0))
        on(B, 'l' if sgn < 0 else 'r', 0, 0.1, (0.3, 0.3), mm('glow'), th=0.3, name='shoulder_rune', rot=(45, 0, 0))
    for i in range(4):
        on(B, 'k', 0, 0.3 - i * 0.2, (0.5 - 0.1 * i, 0.07), mm('glow2' if i % 2 else 'glow'), th=0.1, name='back_rune')
    p('chest_gem', (0.2, 0.06, 0.2), mm('glow2'), (0, B.front - 0.12, B.c.z + 0.0), rot=(0, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(7):
        ang = math.radians(i * 30 - 0)
        cx, cy = math.cos(ang) * 0.6, Hd.c.y - math.sin(ang) * 0.5
        p('crown_leaf', (0.2, 0.1, 0.36 if i % 2 else 0.5), mm('glow' if i % 2 else 'glow2'), (cx, cy, Hd.top + 0.2), rot=(0, 0, math.degrees(ang) + 90))
    for sgn, n in LR:
        p('cheek_paint', (0.14, 0.04, 0.05), mm('glow'), (sgn * 0.36, Hd.front - 0.08, Hd.c.z - 0.2), rot=(0, sgn * 20, 0))
        p('cheek_paint', (0.1, 0.04, 0.05), mm('glow'), (sgn * 0.36, Hd.front - 0.08, Hd.c.z - 0.28), rot=(0, sgn * 20, 0))
    use('body')
    orbit_kit((0, 0.05, 1.5), 1.6, 6, 'glow', 'glow2', size=0.15, dz=0.5, shape='leaf')
    aura_kit(1.6, 5, motes=10, mote_col='glow', mote_r=1.7, height=2.4, style='diamond')
    return finish(a)


def emerald_treefrog(row):
    a = start(row, dict(main='#2fc85a', belly='#fff6c8', dark='#1a8a44', accent='#ff8a2a', blue='#3a8af0', iris='#ff3a2a',
                        **{'*glow': '#5aff8a', '*glow2': '#ffe14a', '*gold': '#ffd84a'}), 2.75)
    B, Hd = sit(bw=1.2, bd=1.0, bh=0.7, hw=1.44, hd=1.0, hh=0.8, arm=0.34, lw=0.22, foot_l=0.7, ntoe=3, foot='accent', toe='accent')
    use('head')
    # wide smiling mouth, nostrils, and bulging eye mounts on top of the head (the silhouette)
    p('mouth', (1.1, 0.04, 0.05), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.2))
    for sgn, n in LR:
        p('mouth_corner', (0.05, 0.04, 0.12), mm('dark'), (sgn * 0.56, Hd.front - 0.012, Hd.c.z - 0.15))
        p('nostril', (0.06, 0.04, 0.05), mm('dark'), (sgn * 0.1, Hd.front - 0.012, Hd.c.z + 0.02))
        p('blush', (0.2, 0.03, 0.1), mm('pink'), (sgn * 0.52, Hd.front - 0.012, Hd.c.z - 0.06))
        b('eye_mount', (0.56, 0.5, 0.5), mm('main'), (sgn * 0.42, Hd.front + 0.3, Hd.top + 0.14), bev=0.1)
    b('throat', (0.9, 0.2, 0.3), mm('belly'), (0, Hd.front + 0.04, Hd.bot + 0.06), bev=0.08)
    em = Box((0, Hd.front + 0.3, Hd.top + 0.14), (1.4, 0.5, 0.5), 'head')
    eyes(em, 0.8, 0.3, 0.0, iris='#ff3a2a', brow=None, w=0.9)
    use('body')
    # blue-and-yellow flanks, belly, orange toe pads
    for sgn, n in LR:
        f = 'l' if sgn < 0 else 'r'
        on(B, f, 0, -0.1, (B.s.y * 0.8, 0.4), mm('blue'), name='flank', th=0.04)
        for j in range(4):
            on(B, f, -0.3 + j * 0.2, -0.1, (0.07, 0.36), mm('belly'), name='flank_bar', th=0.05)
        p('thigh_blue', (0.05, 0.4, 0.3), mm('blue'), (sgn * (B.s.x / 2 + 0.19), 0.42, 0.3))
    spots(B, 't', 5, mm('dark'), 0.16, seed=4, name='spot')
    for i in range(5):
        for sgn, n in LR:
            p('back_stripe', (0.08, 0.14, 0.04), mm('gold'), (sgn * 0.5, B.c.y - 0.3 + i * 0.16, B.top + 0.03))
    for i in range(4):
        for j in range(2):
            p('wart', (0.1, 0.1, 0.06), mm('dark' if (i + j) % 2 else 'belly'), ((i - 1.5) * 0.26, B.c.y + 0.1 + j * 0.3, B.top + 0.03))
        p('belly_line', (0.5 - 0.08 * i, 0.04, 0.04), mm('accent'), (0, B.front - 0.08, B.c.z + 0.1 - i * 0.12))
    use('head')
    for i in range(5):
        p('head_wart', (0.1, 0.1, 0.05), mm('dark'), ((i - 2) * 0.24, Hd.c.y + 0.2 + 0.1 * (i % 2), Hd.top + 0.03))
        p('lip_dot', (0.06, 0.04, 0.05), mm('belly'), ((i - 2) * 0.22, Hd.front - 0.012, Hd.c.z - 0.28))
    for sgn, n in LR:
        p('eyelid', (0.58, 0.52, 0.08), mm('dark'), (sgn * 0.42, Hd.front + 0.3, Hd.top + 0.42))
        p('tympanum', (0.05, 0.2, 0.2), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y + 0.1, Hd.c.z))
        p('tympanum_in', (0.06, 0.1, 0.1), mm('accent'), (sgn * (Hd.s.x / 2 + 0.012), Hd.c.y + 0.1, Hd.c.z))
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(3):
            p('leg_band', (ft.s.x + 0.02, 0.08, ft.s.z + 0.02), mm('dark'), (ft.c.x, ft.c.y - 0.1 + j * 0.2, ft.c.z))
        p('web', (ft.s.x + 0.14, 0.2, 0.04), mm('blue'), (ft.c.x, ft.front + 0.06, 0.03))
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        for j in range(2):
            p('arm_band', (0.26, 0.26, 0.05), mm('dark'), (sgn * (B.s.x / 2 - 0.19), 0.12 - B.s.y / 2 + 0.04, 0.2 + B.s.z * 0.42 - 0.08 - j * 0.12))
    use('body')
    spots(Hd, 't', 3, mm('dark'), 0.14, seed=2, name='spot')
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(3):
            p('toe_pad', (0.12, 0.12, 0.08), mm('accent'), (ft.c.x + (j - 1) * 0.1, ft.front - 0.06, 0.05))
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        for j in range(3):
            p('finger_pad', (0.1, 0.1, 0.08), mm('accent'), (sgn * (B.s.x / 2 - 0.19) + (j - 1) * 0.09, 0.12 - B.s.y / 2 - 0.2, 0.2 + B.s.z * 0.42 - 0.34 + 0.0))
    use('body')
    # rarity 6: glowing emerald back gems, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i, (x, y, s) in enumerate(((0, -0.2, 0.2), (-0.3, 0.1, 0.14), (0.3, 0.1, 0.14), (0, 0.32, 0.16), (-0.36, -0.3, 0.1), (0.36, -0.3, 0.1))):
        p('back_gem', (s, s, 0.1), mm('glow' if i % 2 == 0 else 'glow2'), (x, B.c.y + y, B.top + 0.04), rot=(0, 0, 45))
    for sgn, n in LR:
        on(a.bx['body'], 'k', sgn * 0.3, 0.1, (0.16, 0.16), mm('glow'), th=0.5, name='rump_gem', rot=(0, 45, 0))
        p('thigh_gem', (0.06, 0.14, 0.14), mm('glow2'), (sgn * (B.s.x / 2 + 0.2), 0.42, 0.44), rot=(45, 0, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.c.z))
    a.glow.append('glow_h')
    p('fore_gem', (0.2, 0.05, 0.2), mm('glow2'), (0, Hd.front - 0.02, Hd.c.z + 0.2), rot=(0, 45, 0))
    for sgn, n in LR:
        p('cheek_gem', (0.1, 0.05, 0.1), mm('glow'), (sgn * 0.62, Hd.front - 0.02, Hd.c.z + 0.1), rot=(0, 45, 0))
        p('eye_ring', (0.6, 0.54, 0.05), mm('gold'), (sgn * 0.42, Hd.front + 0.3, Hd.top - 0.08))
    halo_kit(Hd, 'gold', r=0.46, n=8, dz=0.7, kind='halo')
    use('body')
    orbit_kit((0, 0.1, 1.2), 1.5, 6, 'glow', 'glow2', size=0.14, dz=0.4, shape='bubble')
    orbit_kit((0, 0.1, 0.7), 1.8, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.15, shape='leaf')
    aura_kit(1.6, 6, motes=12, mote_col='glow', mote_r=1.7, height=1.8, style='petals')
    return finish(a)


ANIMALS = dict(jade_tapir=jade_tapir, toucan=toucan, leafcutter_ant=leafcutter_ant, jaguar=jaguar, jungle_gorilla=jungle_gorilla,
               emerald_treefrog=emerald_treefrog)
