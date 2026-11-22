# Biome 13 - Ash Plateau: cooled lava, dark sand, embers
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 13
GROUND = '#a8a0aa'
SKY = '#e8c8b8'
THEME = dict(bits=['#3a3640', '#ff7a2a'], dust='#a8a0a8', glow='#ff8a2a', splash='#ffd0a0', bit_name='пепел и угольки')
FOOT = dict(lava_golem=1.2, ember_mandrill=1.2)
BUSH_NAME = 'тлеющий пепельный холм с обугленным пнём, колючей сухой травой и трещинами лавы'


def bush():
    B = begin_bush(NN)
    ash = mat('ash', '#6a6470')
    ash2 = mat('ash2', '#8a8490')
    ash3 = mat('ash3', '#4a4450')
    char = mat('char', '#2e2a30')
    char2 = mat('char2', '#4a3a36')
    grass = mat('grass', '#a89a6a')
    grass2 = mat('grass2', '#c8b880')
    lava = mat('lava', '#ff6a1a', 'neon', 2.6)
    ember = mat('ember', '#ffb02a', 'neon', 3.0)
    rock = mat('rock', '#3a3640')
    # ash mounds with glowing cracks
    for i, (x, y, w, d, h) in enumerate(((0, 0.3, 5.2, 2.8, 1.2), (-1.0, 0.5, 3.0, 2.0, 2.2), (1.4, 0.4, 2.4, 1.8, 1.7))):
        part('big', (x, y, 0.2), 'mound_%d' % i)
        b('mound', (w, d, h), (ash, ash2, ash)[i], (x, y, h / 2), bev=0.16)
        b('mound_top', (w * 0.66, d * 0.66, 0.26), ash2 if i % 2 == 0 else ash3, (x, y, h + 0.1), bev=0.08)
        for j in range(3):
            p('crack', (0.5 - 0.1 * j, 0.06, 0.07), lava, (x - w * 0.25 + j * w * 0.22, y - d / 2 - 0.01, h * (0.3 + 0.2 * j)), rot=(0, 25 * (1 - j), 0))
    # charred stump with a glowing heart (the landmark)
    part('big', (-0.9, 0.7, 2.0), 'stump')
    b('stump', (1.0, 1.0, 1.6), char, (-0.9, 0.7, 2.8), bev=0.1)
    b('stump_top', (0.9, 0.9, 0.12), char2, (-0.9, 0.7, 3.62), bev=0.03)
    p('stump_heart', (0.4, 0.4, 0.06), lava, (-0.9, 0.7, 3.69))
    for j in range(3):
        p('bark_crack', (0.08, 0.05, 0.9), lava, (-1.2 + j * 0.3, 0.19, 2.8))
    b('branch', (0.9, 0.24, 0.24), char, (-0.3, 0.7, 3.3), rot=(0, -35, 0), bev=0.05)
    p('branch_tip', (0.2, 0.2, 0.2), ember, (0.06, 0.7, 3.56), rot=(45, 45, 0))
    # dry thorny grass tufts
    k_ = 0
    for (cx, cy, z, n, h0) in ((-2.4, -0.4, 0.9, 5, 1.8), (0.4, -0.6, 1.0, 5, 2.0), (2.2, -0.4, 1.2, 4, 1.7), (1.4, 0.8, 1.7, 4, 1.5), (-2.8, 0.8, 0.9, 4, 1.4)):
        part('small', (cx, cy, z), 'grass_%d' % k_)
        for i in range(n):
            lean = (i - (n - 1) / 2) * 14
            h = h0 - 0.25 * abs(i - (n - 1) / 2)
            b('blade', (0.12, 0.1, h), grass if i % 2 else grass2, (cx + (i - (n - 1) / 2) * 0.16 + math.sin(math.radians(lean)) * h / 2, cy, z + h / 2), rot=(0, lean, 0), bev=0.02)
            p('blade_ember', (0.08, 0.08, 0.12), ember, (cx + (i - (n - 1) / 2) * 0.16 + math.sin(math.radians(lean)) * h, cy, z + h)) if i % 2 == 0 else None
        k_ += 1
    # lava rocks and ember pebbles
    for i, (x, y, s) in enumerate(((-2.6, -1.3, 0.9), (-0.6, -1.5, 0.6), (1.4, -1.5, 0.8), (2.9, -0.6, 0.7), (2.9, 0.9, 0.6))):
        part('small', (x, y, 0.1), 'rock_%d' % i)
        b('rock', (0.9 * s, 0.8 * s, 0.7 * s), rock, (x, y, 0.35 * s), rot=(0, 0, 20 * i), bev=0.1)
        p('rock_vein', (0.5 * s, 0.05, 0.08), lava, (x, y - 0.41 * s, 0.4 * s), rot=(0, 25, 20 * i))
        p('rock_top', (0.5 * s, 0.5 * s, 0.06), ash3, (x, y, 0.72 * s))
    # smoke puffs (ghost blocks would fade; these are matte grey cubes rising)
    for i, (x, y, z, s) in enumerate(((-0.9, 0.7, 4.0, 0.4), (-0.7, 0.8, 4.5, 0.3))):
        part('small', (x, y, z), 'smoke_%d' % i)
        b('smoke', (s, s, s), ash2, (x, y, z), bev=s * 0.3)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def cinder_porcupine(row):
    a = start(row, dict(main='#5a4a4a', belly='#a8908a', dark='#2e2628', accent='#ff8a2a', quill='#3a3236', tip='#ffb070'), 1.55)
    B, Hd = quad(bw=1.0, bl=1.1, bh=0.66, legh=0.22, lw=0.22, hw=0.92, hd=0.8, hh=0.78, head_up=0.24, toe='dark', head_fwd=0.36)
    mz = muzzle(Hd, (0.4, 0.24, 0.26), -0.26, 'belly', nose=(0.16, 0.08, 0.1), teeth=1)
    cheeks(Hd, 'belly', (0.2, 0.18, 0.24), -0.26, whisk=2)
    eyes(Hd, 0.36, 0.25, 0.1, iris='#8a3a1a', lash=True, brow='#2e2628', tilt=10)
    ears(Hd, 'round', 'main', 'pink', x=0.4, h=0.14, w=0.16, lean=20)
    use('body')
    # quills (the silhouette): long pyramids with warm tips, fanned backwards
    n = 0
    for i, x in enumerate((-0.36, -0.12, 0.12, 0.36)):
        for j, y in enumerate((-0.3, 0.0, 0.3, 0.55)):
            z = B.top - 0.02
            d = (x * 1.2, 0.6 + 0.3 * j, 1.0)
            cn('quill', 0.08, 0.6 + 0.1 * (j % 2), mm('quill' if (i + j) % 2 else 'dark'), (x, B.c.y + y, z), d)
            p('quill_tip', (0.08, 0.08, 0.08), mm('tip'), (x + d[0] * 0.38, B.c.y + y + d[1] * 0.38, z + 0.38))
            n += 1
    for sgn, n_ in LR:
        for j in range(3):
            cn('quill_side', 0.07, 0.4, mm('quill'), (sgn * 0.5, B.c.y - 0.2 + j * 0.3, B.c.z + 0.1), (sgn * 1, 0.5, 0.5))
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)
    for ft in a.bx['feet']:
        p('pad', (ft.s.x * 0.6, 0.03, 0.05), mm('pink'), (ft.c.x, ft.back + 0.012, 0.05))
    tail_kit('stub', 'body', a.tail_j, 'main', 'tip', size=0.2)
    return finish(a)


def ash_lizard(row):
    a = start(row, dict(main='#7a7480', belly='#d8d0c8', dark='#4a4450', accent='#ff9a4a', frill='#ffb07a'), 1.25)
    B, Hd = quad(bw=0.9, bl=1.4, bh=0.5, legh=0.24, lw=0.22, hw=0.9, hd=0.8, hh=0.62, head_up=0.3, toe='accent', head_fwd=0.4, leg_fl=0.42,
                 ntoe=4, leg_back_x=0.5, rump=False)
    mz = muzzle(Hd, (0.5, 0.3, 0.24), -0.22, 'belly', nose=None, mouth=True, tongue=True)
    for sgn, n in LR:
        p('nostril', (0.05, 0.03, 0.04), mm('line'), (sgn * 0.1, mz.front - 0.008, mz.c.z + 0.06))
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.12))
        # little neck frill
        b('frill', (0.1, 0.24, 0.44), mm('frill'), (sgn * (Hd.s.x / 2 + 0.06), Hd.back - 0.06, Hd.c.z), rot=(0, 0, sgn * 25), bev=0.03)
        for j in range(2):
            p('frill_ray', (0.11, 0.24, 0.05), mm('accent'), (sgn * (Hd.s.x / 2 + 0.07), Hd.back - 0.06, Hd.c.z - 0.1 + j * 0.2), rot=(0, 0, sgn * 25))
    eyes(Hd, 0.4, 0.26, 0.14, iris='#c86a1a', brow='#4a4450', tilt=10)
    use('body')
    for j in range(6):
        p('back_scale', (0.18, 0.14, 0.08), mm('accent' if j % 2 else 'dark'), (0, B.front + 0.14 + j * 0.22, B.top + 0.04))
    stripes(B, 'lr', 4, mm('dark'), 0.1, name='band', span=0.86)
    grid(B, 't', 2, 4, mm('belly'), (0.1, 0.1), name='ash_spot', span=(0.6, 0.8))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.05), mm('dark'), (ft.c.x, ft.c.y + 0.1, 0.18))
    use('body')
    tail_kit('long', 'body', (0, B.back, B.c.z), 'main', 'accent', n=3, size=0.18, dark='dark')
    return finish(a)


def ash_anteater(row):
    a = start(row, dict(main='#8a7a70', belly='#d8c8b0', dark='#3a3030', accent='#ff9a4a', snout='#6a5a54'), 2.5)
    B, Hd = quad(bw=0.96, bl=1.4, bh=0.82, legh=0.46, lw=0.26, hw=0.84, hd=0.8, hh=0.78, toe='belly', head_fwd=0.3, leg_fl=0.46, ntoe=3)
    use('head')
    # very long snout (the silhouette) with a tiny mouth and tongue
    b('snout', (0.36, 1.0, 0.34), mm('snout'), (0, Hd.front - 0.46, Hd.c.z - 0.14), rot=(8, 0, 0), bev=0.06)
    b('snout_tip', (0.26, 0.2, 0.26), mm('dark'), (0, Hd.front - 0.98, Hd.c.z - 0.22), bev=0.05)
    p('tongue', (0.06, 0.24, 0.04), mm('pink'), (0, Hd.front - 1.16, Hd.c.z - 0.3))
    for j in range(3):
        p('snout_ring', (0.38, 0.08, 0.36), mm('belly'), (0, Hd.front - 0.2 - j * 0.24, Hd.c.z - 0.12 - 0.02 * j), rot=(8, 0, 0))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.16))
    eyes(Hd, 0.34, 0.25, 0.14, iris='#5a3a2a', brow='#3a3030', tilt=8, sleepy=0.16)
    ears(Hd, 'round', 'main', 'pink', x=0.42, h=0.16, w=0.18, lean=20)
    use('body')
    # the diagonal dark shoulder stripe with a white edge (pattern) and a backpack of ember-berries (accessory)
    for sgn, n in LR:
        f = 'l' if sgn < 0 else 'r'
        on(B, f, -0.2, 0.1, (0.6, 0.2), mm('dark'), name='shoulder_stripe', th=0.04, rot=(30, 0, 0))
        on(B, f, -0.2, 0.26, (0.6, 0.06), mm('belly'), name='stripe_edge', th=0.045, rot=(30, 0, 0))
    on(B, 't', 0, -0.2, (0.5, 0.3), mm('dark'), name='back_stripe', th=0.05)
    grid(B, 'l', 4, 2, mm('belly'), (0.1, 0.1), name='fleck', span=(0.8, 0.5), offset=0.05)
    grid(B, 'r', 4, 2, mm('belly'), (0.1, 0.1), name='fleck', span=(0.8, 0.5), offset=0.05)
    grid(B, 'k', 3, 2, mm('dark'), (0.14, 0.14), name='rump_fleck')
    use('head')
    grid(Hd, 't', 3, 2, mm('dark'), (0.1, 0.1), name='head_fleck')
    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='head_fleck')
    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='head_fleck')
    use('body')
    setm('bag', '#a85a3a')
    b('pouch', (0.6, 0.5, 0.36), mm('bag'), (0, B.c.y + 0.3, B.top + 0.2), bev=0.07)
    p('pouch_flap', (0.62, 0.3, 0.06), mm('dark'), (0, B.c.y + 0.2, B.top + 0.4))
    for i in range(3):
        p('ember_berry', (0.14, 0.14, 0.14), mm('accent'), ((i - 1) * 0.16, B.c.y + 0.44, B.top + 0.44), rot=(45, 45, 0))
    for sgn, n in LR:
        p('strap', (0.06, 0.1, B.s.z * 0.9), mm('bag'), (sgn * (B.s.x / 2 + 0.03), B.c.y + 0.3, B.c.z))
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)
    for ft in a.bx['feet']:
        use(ft.seg)
        p('claw_big', (0.1, 0.14, 0.08), mm('belly'), (ft.c.x, ft.front - 0.02, 0.05))
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.06), mm('belly'), (ft.c.x, ft.c.y + 0.06, 0.4))
    use('body')
    # big fluffy fan tail
    sg('tail', 'body', a.tail_j)
    a.tail = ['tail']
    for i in range(4):
        b('tail_fan', (0.5 + 0.1 * i, 0.3, 0.5 + 0.12 * i), mm('main' if i % 2 else 'dark'), (0, a.tail_j[1] + 0.2 + i * 0.24, a.tail_j[2] + 0.1 + i * 0.12), bev=0.07)
        p('tail_tuft', (0.12, 0.12, 0.12), mm('belly'), (0.3 + 0.05 * i, a.tail_j[1] + 0.2 + i * 0.24, a.tail_j[2] + 0.4 + i * 0.16))
    return finish(a)


def ember_boar(row):
    """ember warthog that stands on its hind legs like a little brawler: barrel body, big tusked face with warts, burning mohawk"""
    a = start(row, dict(main='#4a3a3a', belly='#8a6a5a', dark='#241c1e', accent='#ffe0c0', snout='#ff9a8a', **{'*glow': '#ff8a2a'}), 2.65)
    B, Hd = biped(tw=1.2, td=1.0, th=1.0, legh=0.4, lw=0.36, hw=1.2, hd=1.0, hh=0.9, arm_l=0.7, arm_w=0.3, hand=0.36, shoulder=0.0,
                  foot='dark', toe='belly', hand_mat='dark')
    use('head')
    sn = b('snout', (0.56, 0.32, 0.4), mm('snout'), (0, Hd.front - 0.12, Hd.c.z - 0.2), bev=0.07)
    for sgn, n in LR:
        p('nostril', (0.1, 0.03, 0.14), mm('line'), (sgn * 0.11, sn.front - 0.008, sn.c.z + 0.03))
        b('tusk', (0.1, 0.1, 0.34), mm('accent'), (sgn * 0.34, sn.front + 0.06, sn.c.z + 0.1), rot=(0, sgn * 18, 0), bev=0.03)
        b('wart', (0.16, 0.12, 0.16), mm('belly'), (sgn * 0.5, Hd.front + 0.04, Hd.c.z - 0.06), bev=0.04)
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z + 0.02))
        b('ear', (0.26, 0.12, 0.3), mm('main'), (sgn * 0.56, Hd.c.y, Hd.top - 0.02), rot=(0, sgn * 40, 0), bev=0.04)
    eyes(Hd, 0.28, 0.24, 0.2, iris='#c84a1a', glow='#ff8a2a', brow='#241c1e', tilt=-16)
    use('body')
    b('barrel', (1.3, 1.1, 0.7), mm('main'), (0, 0.05, 0.4 + 0.5), bev=0.1)
    b('belly_patch', (0.8, 0.1, 0.6), mm('belly'), (0, -0.52, 0.86), bev=0.04)
    for sgn, n in LR:
        grid(B, 'l' if sgn < 0 else 'r', 3, 2, mm('dark'), (0.14, 0.14), name='bristle_patch')
    setm('belt', '#a85a2a')
    b('belt', (1.36, 1.16, 0.14), mm('belt'), (0, 0.05, 0.62), bev=0.03)
    p('buckle', (0.24, 0.06, 0.18), mm('glow'), (0, -0.54, 0.62))
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        b('glove', (hb_.s.x + 0.1, hb_.s.y + 0.1, hb_.s.z + 0.06), mm('belt'), hb_.c, bev=0.06)
        p('glove_band', (hb_.s.x + 0.12, hb_.s.y + 0.12, 0.06), mm('accent'), (hb_.c.x, hb_.c.y, hb_.top + 0.04))
    use('body')
    grid(B, 'k', 3, 3, mm('dark'), (0.14, 0.14), name='back_bristle')
    grid(B, 'f', 3, 2, mm('belly'), (0.1, 0.1), name='chest_dot', span=(0.6, 0.4))
    grid(B, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='side_dot')
    grid(B, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='side_dot')
    use('head')
    grid(Hd, 't', 2, 2, mm('dark'), (0.12, 0.12), name='head_bristle')
    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_wart')
    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_wart')
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        p('hoof_band', (ft.s.x + 0.04, ft.s.y * 0.8, 0.06), mm('belt'), (ft.c.x, ft.c.y, ft.top + 0.06))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)
    # rarity 4: burning mohawk running from head down the back (own segment), ember sparks
    sg('glow', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow')
    for i in range(5):
        b('mohawk', (0.18, 0.18, 0.3 + 0.1 * math.sin(i * 0.9)), mm('glow'), (0, Hd.c.y - 0.3 + i * 0.18, Hd.top + 0.14), bev=0.04)
        p('mohawk_tip', (0.1, 0.1, 0.12), mm('accent'), (0, Hd.c.y - 0.3 + i * 0.18, Hd.top + 0.34 + 0.05 * math.sin(i * 0.9)))
    use('body')
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=1.6)
    return finish(a)


def lava_golem(row):
    a = start(row, dict(main='#3a3438', belly='#5a5258', dark='#24202a', accent='#8a8288', face='#4a4248',
                        **{'*glow': '#ff6a1a', '*glow2': '#ffd21a'}), 3.0)
    B, Hd = biped(tw=1.7, td=1.1, th=1.1, legh=0.5, lw=0.52, hw=1.1, hd=0.96, hh=0.86, arm_l=1.4, arm_w=0.56, hand=0.7, shoulder=0.4,
                  foot='face', toe='dark', hand_mat='face')
    use('head')
    # rocky head with a glowing visor-face and cute features
    b('brow', (1.14, 0.2, 0.2), mm('main'), (0, Hd.front + 0.06, Hd.top - 0.08), bev=0.05)
    for sgn, n in LR:
        cn('head_rock', 0.12, 0.3, mm('accent'), (sgn * 0.34, Hd.c.y, Hd.top - 0.02), (sgn * 0.4, 0.2, 1))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.24))
    p('mouth', (0.3, 0.03, 0.05), mm('glow'), (0, Hd.front - 0.012, Hd.c.z - 0.3))
    eyes(Hd, 0.34, 0.24, 0.0, iris='#ff6a1a', glow='#ff6a1a', brow=None)
    use('body')
    # boulder plates over the body, magma seams between them (the silhouette)
    for i in range(3):
        for j in range(2):
            b('plate', (0.5, 0.14, 0.46), mm('main' if (i + j) % 2 else 'belly'), ((i - 1) * 0.54, B.front - 0.05, B.c.z + 0.24 - j * 0.5), bev=0.06)
    for sgn, n in LR:
        for j in range(3):
            b('side_rock', (0.16, 0.36, 0.34), mm('accent' if j % 2 else 'main'), (sgn * (B.s.x / 2 + 0.06), B.c.y - 0.3 + j * 0.3, B.c.z + 0.2 - j * 0.16), bev=0.05)
    grid(B, 'k', 3, 2, mm('belly'), (0.3, 0.3), name='back_rock', th=0.12)
    grid(B, 'f', 3, 3, mm('accent'), (0.1, 0.1), name='pebble', th=0.2, offset=0.1)
    grid(B, 'l', 3, 3, mm('accent'), (0.12, 0.12), name='side_pebble', th=0.16)
    grid(B, 'r', 3, 3, mm('accent'), (0.12, 0.12), name='side_pebble', th=0.16)
    grid(B, 't', 3, 2, mm('belly'), (0.2, 0.2), name='top_rock', th=0.1)
    use('head')
    grid(Hd, 't', 3, 2, mm('accent'), (0.14, 0.14), name='head_pebble')
    grid(Hd, 'l', 2, 2, mm('belly'), (0.14, 0.14), name='head_rock')
    grid(Hd, 'r', 2, 2, mm('belly'), (0.14, 0.14), name='head_rock')
    use('body')
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        for j in range(6):
            p('arm_stud', (0.12, 0.12, 0.12), mm('belly'), (hb_.c.x + (j % 2 - 0.5) * 0.4, -0.26, hb_.c.z + 0.4 + (j // 2) * 0.3))
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(4):
            p('leg_stud', (0.12, 0.12, 0.12), mm('belly'), (ft.c.x + (j % 2 - 0.5) * 0.3, ft.front + 0.2, 0.2 + (j // 2) * 0.2))
    use('body')
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        sgn = 1 if hb_.c.x > 0 else -1
        for j in range(3):
            b('arm_rock', (0.6, 0.6, 0.3), mm('main' if j % 2 else 'accent'), (hb_.c.x, 0.05, hb_.c.z + 0.4 + j * 0.34), bev=0.06)
        p('fist_crack', (hb_.s.x + 0.02, 0.06, 0.06), mm('glow'), (hb_.c.x, -hb_.s.y / 2 - 0.01, hb_.c.z))
    for ft in a.bx['feet']:
        use(ft.seg)
        b('leg_rock', (0.6, 0.6, 0.3), mm('accent'), (ft.c.x, ft.c.y + 0.16, 0.34), bev=0.06)
        p('foot_crack', (ft.s.x + 0.02, 0.06, 0.06), mm('glow'), (ft.c.x, ft.front + 0.02, 0.1))
    use('body')
    # rarity 5: magma core and seams (own segment flickers), molten shoulders, orbiting embers, yellow aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    b('core', (0.4, 0.1, 0.4), mm('glow2'), (0, B.front - 0.14, B.c.z + 0.0), rot=(0, 45, 0), bev=0.05)
    for i in range(2):
        p('seam_v', (0.06, 0.16, 1.0), mm('glow'), ((i - 0.5) * 0.54, B.front - 0.06, B.c.z))
    p('seam_h', (1.5, 0.16, 0.06), mm('glow'), (0, B.front - 0.06, B.c.z - 0.01))
    for sgn, n in LR:
        for j in range(3):
            p('side_seam', (0.18, 0.06, 0.06), mm('glow'), (sgn * (B.s.x / 2 + 0.06), B.c.y - 0.15 + j * 0.3, B.c.z + 0.04 - j * 0.16))
    for i in range(3):
        on(B, 'k', (i - 1) * 0.3, 0.2, (0.08, 0.5), mm('glow'), th=0.14, name='back_seam')
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        sgn = 1 if hb_.c.x > 0 else -1
        cn('shoulder_flame', 0.16, 0.5, mm('glow'), (hb_.c.x, 0.05, hb_.c.z + 1.42), (sgn * 0.3, 0, 1))
        cn('shoulder_flame', 0.1, 0.34, mm('glow2'), (hb_.c.x + sgn * 0.2, 0.15, hb_.c.z + 1.42), (sgn * 0.5, 0.2, 1))
        for j in range(2):
            p('arm_seam', (0.62, 0.62, 0.05), mm('glow'), (hb_.c.x, 0.05, hb_.c.z + 0.55 + j * 0.34))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(3):
        p('crown_ember', (0.14, 0.14, 0.2), mm('glow2' if i == 1 else 'glow'), ((i - 1) * 0.24, Hd.c.y, Hd.top + 0.1), rot=(0, 45, 0))
    use('body')
    orbit_kit((0, 0.05, 1.7), 1.7, 6, 'glow', 'glow2', size=0.16, dz=0.5, shape='flame')
    aura_kit(1.8, 5, motes=10, mote_col='glow', height=2.6, style='diamond')
    return finish(a)


def ember_mandrill(row):
    a = start(row, dict(main='#5a4a52', belly='#c8b0a0', dark='#2e2430', accent='#ffd84a', face='#ff5a3a', nose_b='#3a8ad8', mane='#ff9a3a',
                        **{'*glow': '#ff6a1a', '*glow2': '#ffd21a', '*gold': '#ffd84a'}), 3.1)
    B, Hd = biped(tw=1.4, td=0.9, th=1.0, legh=0.5, lw=0.42, hw=1.16, hd=0.96, hh=0.96, arm_l=1.2, arm_w=0.4, hand=0.5, shoulder=0.3,
                  foot='belly', toe='dark', hand_mat='belly')
    use('head')
    # the famous mandrill face: red nose ridge with blue ridged cheeks (the silhouette) + golden beard
    b('nose_ridge', (0.26, 0.36, 0.6), mm('face'), (0, Hd.front - 0.12, Hd.c.z - 0.06), bev=0.06)
    p('nose_tip', (0.3, 0.1, 0.16), mm('face'), (0, Hd.front - 0.31, Hd.c.z - 0.3))
    for sgn, n in LR:
        b('cheek', (0.26, 0.3, 0.46), mm('nose_b'), (sgn * 0.3, Hd.front - 0.08, Hd.c.z - 0.12), bev=0.06)
        for j in range(3):
            p('cheek_ridge', (0.28, 0.32, 0.04), mm('dark'), (sgn * 0.3, Hd.front - 0.08, Hd.c.z - 0.28 + j * 0.14))
        p('nostril', (0.06, 0.04, 0.05), mm('line'), (sgn * 0.06, Hd.front - 0.37, Hd.c.z - 0.3))
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.46, Hd.front - 0.012, Hd.c.z - 0.3))
        for j in range(3):
            p('side_mane', (0.12, 0.24, 0.24), mm('mane'), (sgn * (Hd.s.x / 2 + 0.05), Hd.c.y + 0.1, Hd.c.z + 0.2 - j * 0.24))
    for i in range(4):
        p('beard', (0.2, 0.14, 0.2 - 0.03 * i), mm('accent'), ((i - 1.5) * 0.18, Hd.front + 0.06, Hd.bot - 0.06))
    p('mouth', (0.24, 0.03, 0.04), mm('line'), (0, Hd.front - 0.012, Hd.c.z - 0.42))
    eyes(Hd, 0.28, 0.27, 0.22, iris='#ffb02a', glow='#ff6a1a', brow='#2e2430', tilt=-10)
    for i in range(4):
        b('head_mane', (0.24, 0.24, 0.24), mm('mane'), ((i - 1.5) * 0.26, Hd.c.y + 0.1, Hd.top + 0.08), bev=0.05)
    use('body')
    fluff(Box((0, B.front - 0.05, B.c.z), (B.s.x * 0.66, 0.1, B.s.z * 0.7)), 'f', mm('belly'), 4, 1.3, 0.42, th=0.07)
    for sgn, n in LR:
        for j in range(4):
            p('fur', (0.16, 0.22, 0.2), mm('mane' if j % 2 else 'main'), (sgn * (B.s.x / 2 + 0.03), B.c.y - 0.3 + j * 0.2, B.c.z + 0.3 - j * 0.2))
    grid(B, 'k', 3, 2, mm('dark'), (0.2, 0.16), name='back_fur')
    grid(B, 'l', 3, 3, mm('main'), (0.14, 0.14), name='side_fur', th=0.08)
    grid(B, 'r', 3, 3, mm('main'), (0.14, 0.14), name='side_fur', th=0.08)
    grid(B, 't', 3, 2, mm('mane'), (0.2, 0.2), name='top_fur')
    use('head')
    grid(Hd, 't', 3, 2, mm('dark'), (0.12, 0.12), name='head_fur', span=(0.8, 0.5))
    use('body')
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        sgn = 1 if hb_.c.x > 0 else -1
        p('wrist_band', (hb_.s.x + 0.08, hb_.s.y + 0.08, 0.12), mm('gold'), (hb_.c.x, 0.0, hb_.top + 0.06))
        for j in range(2):
            p('arm_fur', (0.14, 0.4, 0.2), mm('mane'), (hb_.c.x + sgn * 0.22, 0.05, hb_.c.z + 0.4 + j * 0.3))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('ankle_band', (ft.s.x + 0.06, ft.s.y * 0.7, 0.08), mm('gold'), (ft.c.x, ft.c.y + 0.12, ft.top + 0.12))
    use('body')
    # colourful rump and a short tail
    tail_kit('stub', 'body', a.tail_j, 'face', 'nose_b', size=0.24)
    # rarity 6: ember war paint, glowing mane tips, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(3):
            p('chest_paint', (0.3 - 0.06 * j, 0.04, 0.06), mm('glow' if j % 2 else 'glow2'), (sgn * 0.3, B.front - 0.11, B.c.z + 0.36 - j * 0.12), rot=(0, sgn * 20, 0))
        on(B, 'l' if sgn < 0 else 'r', 0, 0.1, (0.24, 0.24), mm('glow'), th=0.3, name='shoulder_rune', rot=(45, 0, 0))
    p('chest_gem', (0.2, 0.06, 0.2), mm('glow2'), (0, B.front - 0.12, B.c.z - 0.1), rot=(0, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(4):
        p('mane_flame', (0.14, 0.14, 0.2), mm('glow' if i % 2 else 'glow2'), ((i - 1.5) * 0.26, Hd.c.y + 0.1, Hd.top + 0.3), rot=(0, 45, 0))
    halo_kit(Hd, 'gold', r=0.6, n=10, dz=0.9, kind='flames')
    use('body')
    orbit_kit((0, 0.05, 1.6), 1.7, 6, 'glow', 'glow2', size=0.15, dz=0.5, shape='flame')
    orbit_kit((0, 0.05, 1.0), 2.0, 8, 'gold', 'glow', size=0.1, name='orbit2', dz=0.2, shape='star')
    aura_kit(1.7, 6, motes=12, mote_col='glow', mote_r=1.8, height=2.6, style='rays')
    return finish(a)


ANIMALS = dict(cinder_porcupine=cinder_porcupine, ash_lizard=ash_lizard, ash_anteater=ash_anteater, ember_boar=ember_boar,
               lava_golem=lava_golem, ember_mandrill=ember_mandrill)
