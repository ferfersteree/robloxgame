# Biome 18 - Twilight Rift: dark rifts, glowing spores, impossible ledges
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 18
GROUND = '#4a3a6a'
SKY = '#c8b0e0'
THEME = dict(bits=['#5a3a8a', '#ff8ae0'], dust='#8a7aa8', glow='#ff8ae0', splash='#d8c0ff', bit_name='тёмные споры')
FOOT = dict(void_behemoth=1.15, rift_axolotl=1.25)
BUSH_NAME = 'куст тёмных спор: шары-дождевики на ножках, светящиеся споры и трещина разлома в земле'


def bush():
    B = begin_bush(NN)
    rock = mat('rock', '#3a2e50')
    rock2 = mat('rock2', '#54446e')
    puff = mat('puff', '#5a3a8a')
    puff2 = mat('puff2', '#7a54a8')
    stem = mat('stem', '#d8c8e8')
    leaf = mat('leaf', '#2e6a5a')
    rift = mat('rift', '#ff8ae0', 'neon', 2.4)
    spore = mat('spore', '#8affe8', 'neon', 2.2)
    # cracked ledge with a glowing rift
    part('big', (0, 0.3, 0.2), 'ledge')
    b('ledge', (6.4, 2.8, 0.7), rock, (0, 0.3, 0.35), bev=0.12)
    b('ledge_top', (5.6, 2.2, 0.2), rock2, (0, 0.3, 0.8), bev=0.06)
    for i, (x, y, w, rz) in enumerate(((-1.2, -0.4, 1.4, 20), (0.2, -0.6, 1.0, -15), (1.4, -0.2, 1.2, 30))):
        p('rift', (w, 0.14, 0.05), rift, (x, y, 0.91), rot=(0, 0, rz))
    # puffball spore pods on stems (the bush)
    spec = ((0, 0.6, 2.0, 1.5, puff), (-1.4, 0.4, 1.6, 1.2, puff2), (1.4, 0.5, 1.7, 1.3, puff), (-0.6, 1.0, 2.8, 1.0, puff2), (0.8, 0.9, 2.7, 0.9, puff2),
            (-2.5, 0.0, 1.2, 0.8, puff), (2.5, 0.1, 1.2, 0.8, puff2), (0.0, -0.6, 1.3, 0.7, puff2))
    for i, (x, y, h, s, m_) in enumerate(spec):
        part('big' if s > 1.0 else 'small', (x, y, 0.9), 'pod_%d' % i)
        b('stem', (0.24 * s, 0.24 * s, h - 0.9), stem, (x, y, 0.9 + (h - 0.9) / 2), bev=0.04)
        b('pod', (s, s, s * 0.9), m_, (x, y, h + s * 0.4), bev=0.18 * s)
        b('pod_cap', (s * 0.6, s * 0.6, s * 0.2), m_, (x, y, h + s * 0.9), bev=0.08)
        for j in range(4):
            ang = math.radians(j * 90 + 45)
            p('pod_dot', (0.12 * s, 0.06, 0.12 * s), spore, (x + math.cos(ang) * s * 0.3, y - s * 0.51, h + s * 0.4 + math.sin(ang) * s * 0.25))
        p('pod_pore', (0.2 * s, 0.2 * s, 0.05), spore, (x, y, h + s * 1.01))
    # dark ferns at the feet
    for i, (x, y) in enumerate(((-1.8, -1.0), (1.8, -0.9), (-0.6, -1.3))):
        part('small', (x, y, 0.8), 'fern_%d' % i)
        for k_ in range(4):
            ang = (k_ - 1.5) * 30
            b('fern', (0.16, 0.12, 0.8), leaf, (x + math.sin(math.radians(ang)) * 0.3, y, 1.2), rot=(0, ang, 0), bev=0.03)
            p('fern_glow', (0.08, 0.08, 0.08), spore, (x + math.sin(math.radians(ang)) * 0.6, y, 1.6))
    # floating spores
    for i, (x, y, z) in enumerate(((-0.8, 0.0, 3.8), (0.6, 0.2, 4.1), (1.6, 0.1, 3.2), (-1.8, 0.2, 3.0))):
        part('small', (x, y, z), 'spore_%d' % i)
        b('spore', (0.2, 0.2, 0.2), spore, (x, y, z), rot=(45, 45, 0), bev=0.05)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def void_lamprey(row):
    """floating lamprey: a chunky tube that ends in a big round sucker-mouth disc (with a ring of tiny cute teeth), seven gill dots"""
    zc = 0.5
    a = start(row, dict(main='#3ab8a8', belly='#c8fff0', dark='#1a6a6a', accent='#ff8ac8', ring='#ffd0e8'), 1.45, hover=2.4, z0=zc)
    sg('body', 'root', (0, 0.2, zc))
    B = b('body', (0.7, 0.9, 0.7), mm('main'), (0, 0.2, zc), bev=0.12)
    p('belly', (0.5, 0.8, 0.06), mm('belly'), (0, 0.2, zc - 0.36))
    sg('head', 'body', (0, -0.25, zc))
    Hd = b('head', (0.84, 0.5, 0.84), mm('main'), (0, -0.44, zc), bev=0.12)
    # the round sucker disc (the silhouette)
    b('disc', (1.0, 0.14, 1.0), mm('ring'), (0, Hd.front - 0.04, zc - 0.06), rot=(0, 45, 0), bev=0.1)
    b('disc_in', (0.6, 0.15, 0.6), mm('accent'), (0, Hd.front - 0.06, zc - 0.06), rot=(0, 45, 0), bev=0.06)
    for i in range(8):
        ang = math.radians(i * 45)
        p('tooth', (0.08, 0.06, 0.08), mm('white'), (math.cos(ang) * 0.24, Hd.front - 0.13, zc - 0.06 + math.sin(ang) * 0.24), rot=(0, 45, 0))
    p('mouth_hole', (0.16, 0.06, 0.16), mm('dark'), (0, Hd.front - 0.14, zc - 0.06), rot=(0, 45, 0))
    # eyes sit on top of the head looking forward
    em = Box((0, Hd.front + 0.02, zc + 0.5), (0.84, 0.2, 0.36), 'head')
    use('head')
    b('brow_ridge', (0.84, 0.3, 0.3), mm('main'), (0, Hd.front + 0.16, zc + 0.48), bev=0.06)
    eyes(em, 0.8, 0.27, 0.0, iris='#ff8ac8', lash=True, brow=None)
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('accent'), (sgn * 0.34, Hd.front + 0.01, zc + 0.3))
    use('body')
    for sgn, n in LR:
        for j in range(7):
            p('gill', (0.04, 0.08, 0.08), mm('accent'), (sgn * 0.36, -0.3 + j * 0.12, zc + 0.1))
    # chunky tube tail in 4 segments with a dorsal ribbon fin
    cur = Vector((0, 0.6, zc))
    par = 'body'
    a.tail = []
    for i in range(4):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        w = 0.62 - 0.1 * i
        b('tube', (w, 0.6, w), mm('main' if i % 2 == 0 else 'dark'), (0, cur.y + 0.3, zc), bev=0.1)
        b('fin', (0.06, 0.5, 0.2), mm('accent'), (0, cur.y + 0.3, zc + w / 2 + 0.08), bev=0.02)
        p('fin_low', (0.06, 0.4, 0.14), mm('ring'), (0, cur.y + 0.3, zc - w / 2 - 0.06))
        for sgn, n in LR:
            p('spot', (0.04, 0.12, 0.12), mm('belly'), (sgn * (w / 2 + 0.01), cur.y + 0.3, zc + 0.08))
        cur = Vector((0, cur.y + 0.58, zc))
        par = nm
    b('tail_tip', (0.12, 0.4, 0.5), mm('accent'), (0, cur.y + 0.16, zc), bev=0.03)
    grid(B, 't', 2, 3, mm('dark'), (0.12, 0.12), name='back_spot')
    use('head')
    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_dot', span=(0.6, 0.5))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, Hd.front - 0.2, zc - 0.1), Hit=(0, 0.6, zc + 0.3))
    return finish(a)


def dusk_panther(row):
    """dusk panther lying in a sphinx pose: belly on the ground, front paws stretched forward, head held high, moon cheek marks"""
    a = start(row, dict(main='#3a2e5a', belly='#6a5a9a', dark='#1e1830', accent='#c8a8ff', star='#ffe8a8'), 1.77)
    B, Hd = quad(bw=0.9, bl=1.7, bh=0.6, legh=0.06, lw=0.26, hw=1.1, hd=0.9, hh=0.9, head_up=0.9, toe='accent', head_fwd=0.16, leg_fl=0.9,
                 rump=True, chest=True)
    use('head')
    mz = muzzle(Hd, (0.46, 0.24, 0.28), -0.26, 'belly', nose=(0.16, 0.08, 0.1), nose_mat='accent')
    cheeks(Hd, 'belly', (0.2, 0.2, 0.26), -0.26, whisk=3, wmat='star')
    for sgn, n in LR:
        b('ear', (0.26, 0.14, 0.3), mm('main'), (sgn * 0.38, Hd.c.y, Hd.top + 0.12), bev=0.05)
        p('ear_in', (0.14, 0.04, 0.18), mm('accent'), (sgn * 0.38, Hd.c.y - 0.08, Hd.top + 0.12))
        # crescent cheek marks
        p('cheek_moon', (0.06, 0.03, 0.2), mm('star'), (sgn * 0.44, Hd.front - 0.012, Hd.c.z + 0.04))
        p('cheek_moon2', (0.12, 0.03, 0.05), mm('star'), (sgn * 0.4, Hd.front - 0.012, Hd.c.z + 0.14))
    eyes(Hd, 0.32, 0.25, 0.14, iris='#c8a8ff', lash=True, brow='#1e1830', tilt=10, sleepy=0.2)
    use('body')
    # stretched front paws lying flat forward (the sphinx silhouette)
    for ft in a.bx['feet'][:2]:
        use(ft.seg)
        b('fore_arm', (0.28, 0.9, 0.26), mm('main'), (ft.c.x, ft.c.y - 0.4, 0.14), bev=0.05)
        b('fore_paw', (0.32, 0.3, 0.2), mm('belly'), (ft.c.x, ft.c.y - 0.9, 0.1), bev=0.05)
        for j in range(3):
            p('toe', (0.07, 0.05, 0.07), mm('accent'), (ft.c.x + (j - 1) * 0.1, ft.c.y - 1.06, 0.08))
    for ft in a.bx['feet'][2:]:
        use(ft.seg)
        b('haunch', (0.34, 0.6, 0.4), mm('main'), (ft.c.x + (0.12 if ft.c.x > 0 else -0.12), ft.c.y, 0.24), bev=0.06)
    use('body')
    # star freckles across the back (pattern), long tail curled around the side
    grid(B, 't', 3, 5, mm('star'), (0.06, 0.06), name='star_freckle', th=0.04, offset=0.08, rot=(0, 0, 45))
    grid(B, 'l', 4, 2, mm('belly'), (0.1, 0.1), name='side_spot')
    grid(B, 'r', 4, 2, mm('belly'), (0.1, 0.1), name='side_spot')
    sg('tail', 'body', a.tail_j)
    a.tail = ['tail']
    for i in range(6):
        ang = math.radians(i * 30)
        b('tail', (0.2, 0.3, 0.2), mm('main' if i % 2 else 'dark'), (0.3 + math.sin(ang) * 0.5, a.tail_j[1] + math.cos(ang) * 0.3, 0.12), bev=0.04)
    p('tail_tip', (0.22, 0.22, 0.22), mm('accent'), (0.3 + 0.5, a.tail_j[1] - 0.5, 0.12))
    return finish(a)


def gloom_sloth(row):
    """gloom sloth hanging upside down... no: hugging a crooked lantern-post with all four long arms, cheek mask, moss in its fur,
    a little glowing lantern hanging from the post (accessory)"""
    a = start(row, dict(main='#8a8270', belly='#c8c0a8', dark='#3a3428', accent='#5a8a5a', mask='#2e2a24', post='#5a4a3a', lamp='#ffe08a'), 3.0)
    # the post (part of body so it moves with it)
    sg('body', 'root', (0, 0.3, 1.0))
    b('post', (0.3, 0.3, 3.0), mm('post'), (0, 0.5, 1.5), bev=0.05)
    b('post_top', (0.9, 0.24, 0.24), mm('post'), (0.3, 0.5, 2.9), bev=0.05)
    for j in range(4):
        p('post_ring', (0.34, 0.34, 0.06), mm('dark'), (0, 0.5, 0.4 + j * 0.7))
    b('post_base', (0.8, 0.8, 0.2), mm('dark'), (0, 0.5, 0.1), bev=0.04)
    # the sloth hugging the post, body tilted against it
    B = b('torso', (0.8, 0.6, 1.0), mm('main'), (0, 0.16, 1.5), bev=0.12)
    b('belly', (0.6, 0.1, 0.8), mm('belly'), (0, -0.16, 1.5), bev=0.04)
    for j in range(4):
        p('fur_streak', (0.06, 0.04, 0.6), mm('dark'), ((j - 1.5) * 0.14, -0.21, 1.5))
    for i, (x, z) in enumerate(((-0.3, 1.9), (0.3, 1.2), (0.0, 1.0))):
        p('moss', (0.2, 0.06, 0.16), mm('accent'), (x, -0.13, z))
    sg('head', 'body', (0, 0.0, 2.0))
    Hd = b('head', (0.9, 0.7, 0.7), mm('belly'), (0, -0.04, 2.36))
    for sgn, n in LR:
        # the typical sloth eye mask streak
        on(Hd, 'f', sgn * 0.24, 0.0, (0.34, 0.2), mm('mask'), name='mask', rot=(0, sgn * 15, 0))
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, 2.2))
    p('nose', (0.18, 0.06, 0.12), mm('dark'), (0, Hd.front - 0.03, 2.28))
    p('smile', (0.3, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 2.14))
    b('hair_cap', (0.8, 0.6, 0.2), mm('main'), (0, -0.02, 2.76), bev=0.06)
    eyes(Hd, 0.26, 0.24, 0.0, iris='#3a2a1a', brow=None, sleepy=0.3)
    # four long arms wrapped round the post
    for sgn, n in LR:
        for k_, (z, nm) in enumerate(((1.9, 'arm_' + n), (1.1, 'leg_' + n))):
            sg(nm, 'body', (sgn * 0.36, 0.2, z))
            (a.arms if k_ == 0 else a.legs).append(nm)
            b('limb', (0.22, 0.8, 0.22), mm('main'), (sgn * 0.3, 0.5, z), rot=(0, 0, -sgn * 25), bev=0.05)
            b('hand', (0.24, 0.24, 0.24), mm('dark'), (sgn * 0.12, 0.78, z), bev=0.04)
            for t in range(3):
                p('claw', (0.04, 0.16, 0.04), mm('belly'), (sgn * 0.04 + (t - 1) * 0.06, 0.92, z))
    # hanging lantern (accessory) on the top bar
    sg('lantern', 'body', (0.7, 0.5, 2.8))
    p('lantern_rope', (0.03, 0.03, 0.3), mm('dark'), (0.7, 0.5, 2.62))
    b('lantern', (0.24, 0.24, 0.3), mm('lamp'), (0.7, 0.5, 2.36), bev=0.04)
    p('lantern_cap', (0.3, 0.3, 0.06), mm('dark'), (0.7, 0.5, 2.54))
    p('lantern_base', (0.3, 0.3, 0.06), mm('dark'), (0.7, 0.5, 2.18))
    for j in range(4):
        p('lantern_bar', (0.03, 0.26, 0.28), mm('dark'), (0.7 + (j - 1.5) * 0.08, 0.5, 2.36))
    a.extra_idle.append(lambda c, n: [k(c, 'lantern', x, rot=(0, r, 0)) for x, r in ((1, 0), (n // 4, 8), (3 * n // 4, -8), (n, 0))])
    use('body')
    # shaggy fur blocks on back and sides, moss on the post, little mushrooms at the base, vine
    TB = Box((0, 0.16, 1.5), (0.8, 0.6, 1.0))
    grid(TB, 'l', 3, 4, mm('dark'), (0.1, 0.14), name='fur_tuft', span=(0.8, 0.8))
    grid(TB, 'r', 3, 4, mm('dark'), (0.1, 0.14), name='fur_tuft', span=(0.8, 0.8))
    grid(TB, 'k', 3, 4, mm('belly'), (0.12, 0.12), name='back_fur', span=(0.8, 0.8))
    for j in range(8):
        ang = math.radians(j * 77)
        p('post_moss', (0.12, 0.08, 0.14), mm('accent'), (math.cos(ang) * 0.16, 0.5 + math.sin(ang) * 0.16, 0.3 + j * 0.32))
    for i, (x, y, s) in enumerate(((-0.4, 0.2, 1.0), (0.4, 0.9, 0.8), (-0.3, 0.9, 0.7), (0.45, 0.2, 0.6))):
        p('shroom_stem', (0.06 * s, 0.06 * s, 0.2 * s), mm('belly'), (x, y, 0.2 + 0.1 * s))
        p('shroom_cap', (0.22 * s, 0.22 * s, 0.08 * s), mm('lamp'), (x, y, 0.2 + 0.22 * s))
    for j in range(6):
        p('vine', (0.05, 0.05, 0.3), mm('accent'), (0.16 * math.sin(j), 0.66, 2.8 - j * 0.3), rot=(0, 20 * math.sin(j * 1.3), 0))
        p('vine_leaf', (0.14, 0.04, 0.08), mm('accent'), (0.16 * math.sin(j) + 0.08, 0.68, 2.72 - j * 0.3))
    use('head')
    grid(Hd, 't', 3, 2, mm('main'), (0.12, 0.12), name='hair_tuft', offset=0.2)
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 1.6), Hit=(0, 0.16, 1.8))
    a.tail = []
    return finish(a)


def shadow_mantis(row):
    """upright praying mantis: thin standing thorax, triangle head, big folded raptorial arms, leaf wing covers, four thin legs"""
    a = start(row, dict(main='#3a2a4a', belly='#8a6aa8', dark='#1a1424', accent='#ff6ad0', wing='#5a4a7a', **{'*glow': '#ff6ad0'}), 3.3)
    sg('body', 'root', (0, 0.3, 0.8))
    B = b('abdomen', (0.6, 1.4, 0.5), mm('main'), (0, 0.6, 0.9), rot=(-15, 0, 0), bev=0.1)
    for j in range(4):
        p('abdomen_band', (0.62, 0.08, 0.52), mm('belly'), (0, 0.2 + j * 0.3, 0.8 + j * 0.08), rot=(-15, 0, 0))
    # wing covers like folded leaves over the abdomen
    b('wing_cover', (0.66, 1.3, 0.1), mm('wing'), (0, 0.6, 1.18), rot=(-15, 0, 0), bev=0.03)
    p('wing_vein', (0.06, 1.2, 0.11), mm('accent'), (0, 0.6, 1.18), rot=(-15, 0, 0))
    # tall thorax rising up (the silhouette)
    b('thorax', (0.3, 0.3, 1.2), mm('main'), (0, -0.1, 1.6), rot=(10, 0, 0), bev=0.05)
    sg('head', 'body', (0, -0.2, 2.2))
    Hd = b('head', (0.9, 0.5, 0.6), mm('main'), (0, -0.3, 2.44), bev=0.08)
    b('jaw', (0.36, 0.3, 0.24), mm('belly'), (0, -0.46, 2.1), bev=0.04)
    p('mouth', (0.16, 0.03, 0.04), mm('dark'), (0, -0.62, 2.08))
    for sgn, n in LR:
        b('eye_bulge', (0.26, 0.3, 0.36), mm('dark'), (sgn * 0.48, -0.3, 2.5), bev=0.06)
        p('blush', (0.1, 0.03, 0.05), mm('accent'), (sgn * 0.26, Hd.front - 0.012, 2.3))
        sg('antenna_' + n, 'head', (sgn * 0.12, -0.3, Hd.top))
        a.ears.append('antenna_' + n)
        b('antenna', (0.04, 0.04, 0.6), mm('dark'), (sgn * 0.2, -0.36, Hd.top + 0.3), rot=(-25, sgn * 20, 0), bev=0.01)
    use('head')
    eyes(Hd, 0.5, 0.24, 0.08, iris='#ff6ad0', glow='#ff6ad0', brow=None)
    # raptorial arms folded in front ("praying")
    for sgn, n in LR:
        sg('claw_' + n, 'body', (sgn * 0.16, -0.2, 1.9))
        a.arms.append('claw_' + n)
        b('coxa', (0.14, 0.14, 0.5), mm('main'), (sgn * 0.2, -0.3, 1.66), rot=(20, 0, 0), bev=0.03)
        b('femur', (0.16, 0.6, 0.18), mm('belly'), (sgn * 0.2, -0.56, 1.5), rot=(-30, 0, 0), bev=0.03)
        b('tibia', (0.12, 0.12, 0.5), mm('main'), (sgn * 0.2, -0.82, 1.7), rot=(15, 0, 0), bev=0.02)
        for t in range(3):
            p('spike', (0.05, 0.05, 0.1), mm('accent'), (sgn * 0.2, -0.5 - t * 0.1, 1.4 + t * 0.06))
    # four thin legs
    for i, y in enumerate((0.3, 0.8)):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.24, y, 0.9))
            a.legs.append(nm)
            b('leg_up', (0.6, 0.08, 0.08), mm('dark'), (sgn * 0.54, y, 1.0), rot=(0, -sgn * 30, 0), bev=0.02)
            b('leg_low', (0.08, 0.08, 0.9), mm('dark'), (sgn * 0.82, y, 0.45), bev=0.02)
            p('foot', (0.14, 0.18, 0.04), mm('accent'), (sgn * 0.82, y - 0.04, 0.02))
    use('body')
    AB = Box((0, 0.6, 0.9), (0.6, 1.4, 0.5))
    grid(AB, 'l', 4, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))
    grid(AB, 'r', 4, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))
    grid(AB, 'u', 2, 4, mm('dark'), (0.1, 0.1), name='belly_plate', span=(0.6, 0.8))
    for j in range(5):
        p('thorax_ring', (0.34, 0.34, 0.05), mm('belly'), (0, -0.1 - j * 0.02, 1.1 + j * 0.22))
    for sgn in (-1, 1):
        p('cercus', (0.05, 0.3, 0.05), mm('accent'), (sgn * 0.12, 1.4, 1.12), rot=(-25, 0, sgn * 15))
    for j in range(6):
        for sgn in (-1, 1):
            p('wing_cell', (0.12, 0.14, 0.04), mm('belly'), (sgn * 0.18, 0.1 + j * 0.2, 1.3 - j * 0.055), rot=(-15, 0, 0))
    for i, y in enumerate((0.3, 0.8)):
        for sgn, n in LR:
            use('leg_%d%s' % (i + 1, n))
            p('knee', (0.14, 0.14, 0.14), mm('belly'), (sgn * 0.82, y, 0.9))
            p('shin_band', (0.1, 0.1, 0.05), mm('accent'), (sgn * 0.82, y, 0.4))
    use('head')
    grid(Hd, 'f', 3, 1, mm('belly'), (0.08, 0.06), name='face_dot', span=(0.5, 0.1), offset=0.1)
    for sgn, n in LR:
        for j in range(3):
            p('eye_facet', (0.04, 0.08, 0.08), mm('belly'), (sgn * 0.61, -0.3 + (j - 1) * 0.1, 2.5 + (j % 2) * 0.08))
    use('body')
    # rarity 4: glowing wing veins and claw spikes, spore sparks
    sg('glow', 'body', (0, 0.6, 1.2))
    a.glow.append('glow')
    for j in range(4):
        p('wing_glow', (0.5, 0.05, 0.12), mm('glow'), (0, 0.3 + j * 0.24, 1.25 - j * 0.06), rot=(-15, 0, 0))
    for sgn, n in LR:
        use('claw_' + n)
        p('claw_glow', (0.06, 0.12, 0.06), mm('glow'), (sgn * 0.2, -0.88, 1.98))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 1.7), Hit=(0, 0.6, 1.2))
    a.tail = []
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=2.6)
    return finish(a)


def rift_axolotl(row):
    """sky axolotl swimming through the air: wide flat head with a big smile, three frilly gill branches on each side,
    four tiny legs, long tail fin"""
    zc = 0.6
    a = start(row, dict(main='#ffb0d8', belly='#fff0f8', dark='#d8609a', accent='#ff6aa8', gill='#ff4a8a', spot='#ffd8ec',
                        **{'*glow': '#ff8ae0', '*glow2': '#8affe8'}), 1.2, hover=3.2, z0=zc)
    sg('body', 'root', (0, 0.3, zc))
    B = b('body', (0.9, 1.4, 0.6), mm('main'), (0, 0.4, zc), bev=0.12)
    b('belly', (0.7, 1.2, 0.08), mm('belly'), (0, 0.4, zc - 0.32), bev=0.03)
    grid(B, 't', 2, 4, mm('spot'), (0.12, 0.12), name='back_spot', offset=0.1)
    sg('head', 'body', (0, -0.3, zc))
    Hd = b('head', (1.4, 0.8, 0.6), mm('main'), (0, -0.6, zc + 0.04), bev=0.12)
    p('smile', (0.8, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, zc - 0.14))
    for sgn, n in LR:
        p('smile_end', (0.04, 0.03, 0.08), mm('dark'), (sgn * 0.4, Hd.front - 0.012, zc - 0.1))
        p('blush', (0.16, 0.03, 0.08), mm('accent'), (sgn * 0.52, Hd.front - 0.012, zc - 0.04))
    eyes(Hd, 0.34, 0.3, 0.2, iris='#3a2a4a', brow=None)
    # frilly gills: three branches per side with feathery side-blocks (the silhouette)
    for sgn, n in LR:
        sg('gill_' + n, 'head', (sgn * 0.7, -0.5, zc + 0.1))
        a.ears.append('gill_' + n)
        for j, ang in enumerate((40, 5, -30)):
            r = math.radians(ang)
            ln = 0.8
            cx, cz = sgn * (0.7 + math.cos(r) * ln * 0.5), zc + 0.1 + math.sin(r) * ln * 0.5
            b('gill_stalk', (ln, 0.1, 0.1), mm('gill'), (cx, -0.5 + 0.1 * j, cz), rot=(0, -sgn * ang, 0), bev=0.02)
            for t in range(3):
                tx, tz = sgn * (0.7 + math.cos(r) * ln * (0.35 + t * 0.25)), zc + 0.1 + math.sin(r) * ln * (0.35 + t * 0.25)
                p('gill_frill', (0.08, 0.08, 0.22), mm('accent'), (tx, -0.5 + 0.1 * j, tz + 0.1), rot=(0, -sgn * ang, 0))
                p('gill_frill_b', (0.08, 0.08, 0.18), mm('accent'), (tx, -0.5 + 0.1 * j, tz - 0.1), rot=(0, -sgn * ang, 0))
    use('body')
    for i, y in enumerate((0.0, 0.8)):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.45, y, zc - 0.1))
            a.legs.append(nm)
            b('leg', (0.3, 0.14, 0.14), mm('main'), (sgn * 0.6, y, zc - 0.2), bev=0.03)
            for t in range(3):
                p('toe', (0.06, 0.1, 0.05), mm('belly'), (sgn * 0.76, y - 0.06 + (t - 1) * 0.06, zc - 0.24))
    sg('tail', 'body', (0, 1.1, zc))
    a.tail = ['tail']
    b('tail', (0.5, 1.0, 0.4), mm('main'), (0, 1.6, zc), bev=0.08)
    b('tail_fin', (0.1, 1.4, 0.8), mm('belly'), (0, 1.6, zc), bev=0.03)
    p('tail_fin_edge', (0.12, 1.3, 0.08), mm('accent'), (0, 1.6, zc + 0.4))
    p('tail_fin_edge2', (0.12, 1.3, 0.08), mm('accent'), (0, 1.6, zc - 0.4))
    use('body')
    grid(B, 'l', 4, 2, mm('spot'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))
    grid(B, 'r', 4, 2, mm('spot'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))
    grid(B, 'u', 2, 4, mm('belly'), (0.12, 0.12), name='belly_dot', offset=0.06)
    use('head')
    grid(Hd, 't', 3, 2, mm('spot'), (0.12, 0.12), name='head_spot', span=(0.7, 0.6))
    grid(Hd, 'l', 2, 2, mm('spot'), (0.08, 0.08), name='cheek_spot')
    grid(Hd, 'r', 2, 2, mm('spot'), (0.08, 0.08), name='cheek_spot')
    use('tail')
    for j in range(6):
        for sgn in (-1, 1):
            p('fin_dot', (0.12, 0.1, 0.1), mm('spot'), (sgn * 0.01, 1.05 + j * 0.22, zc + 0.22 * sgn * (1 if j % 2 else 0.6)))
    for j in range(6):
        p('tail_band', (0.52, 0.08, 0.42), mm('dark'), (0, 1.25 + j * 0.15, zc))
    use('body')
    # rarity 5: glowing gill tips and back spots (own segments), bubble orbit, yellow aura
    for sgn, n in LR:
        use('gill_' + n)
        for j, ang in enumerate((40, 5, -30)):
            r = math.radians(ang)
            p('gill_glow', (0.12, 0.12, 0.12), mm('glow' if j % 2 else 'glow2'), (sgn * (0.7 + math.cos(r) * 0.86), -0.5 + 0.1 * j, zc + 0.1 + math.sin(r) * 0.86), rot=(45, 45, 0))
    sg('glow', 'body', (0, 0.4, zc + 0.3))
    a.glow.append('glow')
    for j in range(5):
        p('spine_glow', (0.12, 0.12, 0.06), mm('glow' if j % 2 else 'glow2'), (0, -0.1 + j * 0.25, zc + 0.31), rot=(0, 0, 45))
    for sgn, n in LR:
        for j in range(3):
            p('side_glow', (0.04, 0.1, 0.1), mm('glow2'), (sgn * 0.46, 0.0 + j * 0.4, zc + 0.1), rot=(45, 0, 0))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, Hd.front - 0.1, zc - 0.1), Hit=(0, 0.4, zc + 0.3))
    orbit_kit((0, 0.4, zc), 1.8, 8, 'glow', 'glow2', size=0.13, dz=0.3, shape='bubble')
    aura_kit(1.6, 5, motes=10, mote_col='glow', height=1.2, style='petals')
    return finish(a)


def void_behemoth(row):
    """void behemoth: a gigantic tortoise-like titan with pillar legs, tiny friendly head with two curved horns,
    and a hollow window in its back shell that shows a starry void"""
    a = start(row, dict(main='#3a2e6a', belly='#8a7ac8', dark='#1a1430', accent='#ffd84a', shell='#2a2050', shell2='#5a4a9a', horn='#f0e0ff',
                        void='#0e0a1e', **{'*glow': '#c88aff', '*glow2': '#ffe06a', '*star': '#ffffff'}), 4.3)
    B, Hd = quad(bw=1.6, bl=1.8, bh=0.9, legh=0.7, lw=0.5, hw=0.9, hd=0.8, hh=0.76, head_up=0.36, toe='accent', head_fwd=0.6, leg_fl=0.6,
                 rump=False, chest=False, ntoe=3)
    use('head')
    mz = muzzle(Hd, (0.5, 0.2, 0.26), -0.26, 'belly', nose=None, mouth=True)
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.16))
        for j in range(3):
            b('horn', (0.12, 0.12, 0.24), mm('horn'), (sgn * (0.26 + 0.1 * j), Hd.c.y + 0.06 * j, Hd.top + 0.1 + 0.18 * j), rot=(0, sgn * 20 * j, 0), bev=0.03)
    eyes(Hd, 0.36, 0.25, 0.1, iris='#c88aff', glow='#c88aff', brow='#1a1430', tilt=8)
    use('body')
    # the shell: a tall stepped dome with a hollow window cut in it (the silhouette)
    for i, (w, d, h) in enumerate(((2.7, 2.5, 0.4), (2.2, 2.0, 0.4), (1.6, 1.5, 0.3))):
        b('shell', (w, d, h), mm('shell' if i % 2 == 0 else 'shell2'), (0, B.c.y, B.top + 0.15 + i * 0.38), bev=0.08)
    # a portal arch standing across the back, open to the front, filled with a starry void (the silhouette)
    PZ = B.top + 1.65
    for sgn, n in LR:
        b('arch_side', (0.26, 0.34, 1.3), mm('shell2'), (sgn * 0.76, B.c.y, PZ), bev=0.05)
        b('arch_foot', (0.4, 0.5, 0.16), mm('shell'), (sgn * 0.76, B.c.y, PZ - 0.62), bev=0.04)
    b('arch_top', (1.8, 0.34, 0.26), mm('shell2'), (0, B.c.y, PZ + 0.74), bev=0.05)
    b('arch_key', (0.34, 0.4, 0.34), mm('accent'), (0, B.c.y, PZ + 0.9), rot=(0, 45, 0), bev=0.04)
    b('void', (1.26, 0.12, 1.2), mm('void'), (0, B.c.y, PZ), bev=0.02)
    for i in range(6):
        for sgn, n in LR:
            p('shell_rim', (0.24, 0.24, 0.12), mm('accent'), (sgn * 1.35, B.c.y - 0.95 + i * 0.38, B.top + 0.17))
    grid(Box((0, B.c.y, B.top + 0.15), (2.7, 2.5, 0.4)), 'f', 5, 1, mm('shell2'), (0.24, 0.24), name='front_plate', span=(0.9, 0.1))
    grid(Box((0, B.c.y, B.top + 0.15), (2.7, 2.5, 0.4)), 'k', 5, 1, mm('shell2'), (0.24, 0.24), name='back_plate', span=(0.9, 0.1))
    for ft in a.bx['feet']:
        use(ft.seg)
        b('pillar_ring', (ft.s.x + 0.1, ft.s.y + 0.1, 0.16), mm('shell2'), (ft.c.x, ft.c.y + 0.1, 0.5), bev=0.04)
        for j in range(3):
            p('toenail', (0.12, 0.08, 0.1), mm('horn'), (ft.c.x + (j - 1) * 0.16, ft.front - 0.04, 0.06))
    use('body')
    tail_kit('stub', 'body', (0, B.back, B.c.z), 'main', 'shell2', size=0.3)
    SB = Box((0, B.c.y, B.top + 0.53), (2.2, 2.0, 0.4))
    grid(SB, 'l', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))
    grid(SB, 'r', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))
    grid(SB, 'f', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))
    grid(SB, 'k', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))
    grid(B, 'u', 3, 3, mm('belly'), (0.24, 0.24), name='belly_plate')
    # rarity 6: stars floating inside the void window (own segment), glowing rim gems, gear-free star crown, two orbits, red aura
    sg('glow', 'body', (0, B.c.y, PZ))
    a.glow.append('glow')
    for i, (x, y, z, s) in enumerate(((-0.2, 0.0, 0.2, 0.14), (0.25, -0.1, -0.2, 0.1), (0.0, 0.2, -0.05, 0.18), (-0.3, -0.2, -0.3, 0.08),
                                      (0.3, 0.2, 0.3, 0.08), (0.1, -0.3, 0.35, 0.06))):
        for side in (-1, 1):
            p('void_star', (s, s, s), mm('star' if i % 2 else 'glow2'), (x * 1.4, B.c.y + side * 0.07, PZ + z), rot=(45, 45, 0))
    for sgn, n in LR:
        for j in range(3):
            p('frame_gem', (0.14, 0.06, 0.14), mm('glow'), (sgn * 0.76, B.c.y - 0.18, PZ - 0.4 + j * 0.4), rot=(0, 45, 0))
    halo_kit(Hd, 'accent', r=0.42, n=8, dz=0.8, kind='stars')
    use('body')
    orbit_kit((0, B.c.y, 3.0), 2.4, 6, 'glow', 'glow2', size=0.16, dz=0.6, shape='star')
    orbit_kit((0, B.c.y, 2.0), 2.8, 8, 'accent', 'glow', size=0.1, name='orbit2', dz=0.2, shape='shard')
    aura_kit(2.4, 6, motes=12, mote_col='glow', height=3.6, style='diamond')
    return finish(a)


ANIMALS = dict(void_lamprey=void_lamprey, dusk_panther=dusk_panther, gloom_sloth=gloom_sloth, shadow_mantis=shadow_mantis,
               rift_axolotl=rift_axolotl, void_behemoth=void_behemoth)
