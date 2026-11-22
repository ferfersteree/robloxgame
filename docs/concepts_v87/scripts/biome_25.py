# Biome 25 - Primordial Caldera: young volcano crater, lava rivers, giant ferns, first life
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 25
GROUND = '#4a3a34'
SKY = '#e8a87a'
THEME = dict(bits=['#ff8a3a', '#3a3a3a'], dust='#6a5a50', glow='#ff8a3a', splash='#ffc88a', bit_name='пепел и угольки')
FOOT = dict(primordial_titan=1.35, volcanic_wyrm=1.2, magma_hippo=1.05)
BUSH_NAME = 'первобытный куст: древние папоротники на чёрном базальте, между камнями течёт лава'


def bush():
    B = begin_bush(NN)
    basalt = mat('basalt', '#2e2a2e')
    basalt2 = mat('basalt2', '#4a4248')
    fern = mat('fern', '#4a8a3a')
    fern2 = mat('fern2', '#6aaa4a')
    trunk = mat('trunk', '#6a4a30')
    lava = mat('lava', '#ff6a1a', 'neon', 2.4)
    ember = mat('ember', '#ffd84a', 'neon', 2.4)
    part('big', (0, 0.3, 0.4), 'basalt')
    for i, x in enumerate((-2.2, -0.8, 0.6, 2.0)):
        b('column', (1.2, 2.0, 0.6 + 0.3 * (i % 2)), basalt if i % 2 else basalt2, (x, 0.3, 0.35 + 0.15 * (i % 2)), bev=0.08)
    for x in (-1.5, -0.1, 1.3):
        p('lava_seam', (0.2, 2.0, 0.1), lava, (x, 0.3, 0.55))
    # tree ferns: trunks with crowns of drooping fronds
    for i, (x, y, h) in enumerate(((-1.4, 0.4, 3.6), (0.4, 0.6, 4.2), (2.0, 0.2, 3.0))):
        part('big', (x, y, h), 'treefern_%d' % i)
        b('trunk', (0.4, 0.4, h - 0.7), trunk, (x, y, 0.7 + (h - 0.7) / 2), bev=0.06)
        for j in range(6):
            ang = math.radians(j * 60)
            b('frond', (1.2, 0.3, 0.1), fern if j % 2 else fern2, (x + math.cos(ang) * 0.6, y + math.sin(ang) * 0.6, h - 0.1), rot=(0, 20, j * 60), bev=0.03)
        p('fern_heart', (0.3, 0.3, 0.2), ember, (x, y, h + 0.05))
    for i, (x, y) in enumerate(((-2.6, -0.6), (2.7, -0.5), (-0.4, -0.8))):
        part('small', (x, y, 0.9), 'small_fern_%d' % i)
        for j in range(4):
            p('small_frond', (0.6, 0.12, 0.08), fern2, (x, y, 0.9), rot=(0, 30, j * 45))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def caldera_tarsier(row):
    """caldera tarsier sitting on its folded long hind legs: GIANT round eyes taking most of its face, big round ears,
    long thin fingers, a long bare tail pointing straight up with a fluffy ember tuft"""
    a = start(row, dict(main='#a87a5a', belly='#e8d0b0', dark='#3a2a1e', accent='#ff8a3a', ear='#ffb8a8', iris='#ffb84a', blush='#ff9ab4',
                        **{'*ember': '#ffb84a'}), 2.5)
    sg('body', 'root', (0, 0.1, 0.6))
    B = b('body', (0.7, 0.6, 0.8), mm('main'), (0, 0.15, 0.6), bev=0.16)
    b('belly', (0.5, 0.1, 0.6), mm('belly'), (0, -0.16, 0.55), bev=0.04)
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.3, 0.2, 0.3))
        a.legs.append(nm)
        b('thigh', (0.26, 0.6, 0.36), mm('main'), (sgn * 0.38, 0.2, 0.22), bev=0.06)
        b('long_foot', (0.18, 0.7, 0.1), mm('belly'), (sgn * 0.36, -0.1, 0.05), bev=0.03)
        for t in range(3):
            p('toe_pad', (0.07, 0.07, 0.06), mm('ear'), (sgn * 0.36 + (t - 1) * 0.07, -0.45, 0.04))
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.3, -0.1, 0.8))
        a.arms.append(nm)
        b('arm', (0.12, 0.12, 0.4), mm('main'), (sgn * 0.3, -0.25, 0.6), rot=(25, 0, 0), bev=0.02)
        for t in range(3):
            p('long_finger', (0.04, 0.04, 0.2), mm('belly'), (sgn * 0.3 + (t - 1) * 0.05, -0.36, 0.38))
            p('finger_pad', (0.06, 0.06, 0.06), mm('ear'), (sgn * 0.3 + (t - 1) * 0.05, -0.36, 0.28))
    sg('head', 'body', (0, 0.1, 1.0))
    Hd = b('head', (1.0, 0.7, 0.9), mm('main'), (0, 0.0, 1.38), bev=0.18)
    # giant eyes (the silhouette): own big rims
    for sgn in (-1, 1):
        p('brow_fur', (0.3, 0.06, 0.08), mm('belly'), (sgn * 0.24, Hd.front - 0.01, 1.72))
    eyes(Hd, 0.5, 0.24, 0.05, iris='#ffb84a', brow=None, w=0.96)
    p('nose', (0.1, 0.04, 0.06), mm('dark'), (0, Hd.front - 0.012, 1.12))
    p('mouth', (0.12, 0.03, 0.03), mm('dark'), (0, Hd.front - 0.012, 1.04))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('blush'), (sgn * 0.4, Hd.front - 0.012, 1.12))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.4, 0.05, Hd.top - 0.1))
        a.ears.append(nm)
        b('ear', (0.34, 0.1, 0.4), mm('main'), (sgn * 0.5, 0.05, Hd.top + 0.08), rot=(0, sgn * 25, 0), bev=0.05)
        p('ear_in', (0.22, 0.04, 0.28), mm('ear'), (sgn * 0.5, -0.01, Hd.top + 0.08), rot=(0, sgn * 25, 0))
    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='head_stripe', span=(0.4, 0.5))
    grid(Hd, 'l', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_fluff', span=(0.5, 0.5))
    grid(Hd, 'r', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_fluff', span=(0.5, 0.5))
    use('body')
    for j in range(3):
        p('belly_dot', (0.08, 0.04, 0.08), mm('ear'), (0, -0.22, 0.45 + j * 0.15))
    for sgn in (-1, 1):
        p('chest_tuft', (0.14, 0.08, 0.12), mm('belly'), (sgn * 0.12, -0.18, 0.92))
    grid(B, 'k', 2, 2, mm('dark'), (0.08, 0.08), name='back_spot', span=(0.5, 0.5))
    # long tail straight up with an ember tuft
    sg('tail', 'body', (0, 0.45, 0.4))
    a.tail = ['tail']
    for j in range(8):
        p('tail', (0.08, 0.08, 0.24), mm('main' if j % 2 else 'dark'), (0, 0.5 + 0.025 * j, 0.48 + j * 0.22))
    b('tail_tuft', (0.24, 0.24, 0.4), mm('ember'), (0, 0.72, 2.3), bev=0.06)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 0.6), Hit=(0, 0.15, 0.9))
    return finish(a)


def ember_salamander(row):
    """ember salamander standing on its hind legs and hugging its own flaming tail like a torch, round belly,
    wide smiling frog-like mouth, yellow spots on black skin"""
    a = start(row, dict(main='#2e2a2e', belly='#ffb84a', dark='#141214', accent='#ffd84a', spot='#ffd84a', blush='#ff8a6a',
                        **{'*flame': '#ff7a1a', '*flame2': '#ffd84a'}), 2.0)
    sg('body', 'root', (0, 0.1, 0.8))
    B = b('body', (0.8, 0.7, 1.0), mm('main'), (0, 0.1, 0.85), bev=0.2)
    b('belly', (0.6, 0.1, 0.7), mm('belly'), (0, -0.25, 0.8), bev=0.05)
    grid(B, 'k', 2, 3, mm('spot'), (0.12, 0.12), name='spot', span=(0.6, 0.7))
    grid(B, 'l', 2, 2, mm('spot'), (0.1, 0.1), name='spot', span=(0.6, 0.6))
    grid(B, 'r', 2, 2, mm('spot'), (0.1, 0.1), name='spot', span=(0.6, 0.6))
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.3, 0.1, 0.4))
        a.legs.append(nm)
        b('leg', (0.26, 0.3, 0.4), mm('main'), (sgn * 0.3, 0.1, 0.2), bev=0.06)
        b('foot', (0.3, 0.4, 0.1), mm('main'), (sgn * 0.3, -0.05, 0.05), bev=0.03)
        for t in range(4):
            p('toe', (0.06, 0.12, 0.05), mm('spot'), (sgn * 0.3 + (t - 1.5) * 0.08, -0.28, 0.04))
    sg('head', 'body', (0, 0.05, 1.3))
    Hd = b('head', (1.0, 0.8, 0.6), mm('main'), (0, 0.0, 1.62), bev=0.18)
    p('mouth', (0.7, 0.03, 0.05), mm('dark'), (0, Hd.front - 0.012, 1.46))
    for sgn in (-1, 1):
        p('mouth_end', (0.05, 0.03, 0.08), mm('dark'), (sgn * 0.35, Hd.front - 0.012, 1.5))
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.38, Hd.front - 0.012, 1.54))
        p('nostril', (0.04, 0.03, 0.03), mm('dark'), (sgn * 0.08, Hd.front - 0.012, 1.66))
    eyes(Hd, 0.32, 0.27, 0.2, iris='#ffd84a', brow=None)
    grid(Hd, 't', 3, 2, mm('spot'), (0.1, 0.1), name='head_spot', span=(0.7, 0.6))
    use('body')
    for j in range(4):
        p('back_ridge', (0.12, 0.12, 0.1), mm('accent'), (0, 0.46, 0.5 + j * 0.2))
    use('head')
    # arms hug the tail that curls up in front of the belly like a torch (the silhouette)
    use('body')
    sg('tail', 'body', (0, 0.4, 0.5))
    a.tail = ['tail']
    path = ((0, 0.5, 0.35), (0.3, 0.3, 0.2), (0.55, -0.1, 0.3), (0.6, -0.4, 0.5), (0.62, -0.5, 0.75))
    for j, (x, y, z) in enumerate(path):
        s = 0.34 - 0.04 * j
        b('tail', (s, s, s), mm('main'), (x, y, z), bev=0.06)
        p('tail_spot', (0.08, 0.08, 0.04), mm('spot'), (x, y, z + s / 2 + 0.01))
    b('torch_flame', (0.3, 0.3, 0.44), mm('flame'), (0.64, -0.5, 1.08), rot=(0, 0, 45), bev=0.06)
    b('torch_flame_in', (0.18, 0.18, 0.3), mm('flame2'), (0.64, -0.52, 1.14), rot=(0, 0, 45), bev=0.04)
    p('flame_lick', (0.1, 0.1, 0.2), mm('flame'), (0.56, -0.48, 1.34), rot=(0, 20, 0))
    p('flame_lick2', (0.08, 0.08, 0.16), mm('flame2'), (0.74, -0.52, 1.38), rot=(0, -20, 0))
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.4, -0.05, 1.1))
        a.arms.append(nm)
        b('arm', (0.18, 0.4, 0.18), mm('main'), (sgn * 0.32 + 0.2, -0.3, 0.85), rot=(0, 0, sgn * 30), bev=0.04)
        for t in range(3):
            p('finger', (0.05, 0.1, 0.05), mm('spot'), (0.6 + sgn * 0.12 + (t - 1) * 0.05, -0.52, 0.8))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, 0.9), Hit=(0, 0.1, 1.2))
    return finish(a)


def magma_hippo(row):
    """magma hippo lounging in a little ring-shaped lava pool, only its round back and huge head out;
    its mouth is opened in an enormous happy yawn with four stubby tusks"""
    a = start(row, dict(main='#7a6a8a', belly='#e8a8b8', dark='#3a2e40', accent='#ff8a3a', mouth='#d84a6a', tusk='#fff4e0', rock='#3a3034',
                        blush='#ff9ab4', **{'*lava': '#ff6a1a', '*lava2': '#ffb84a'}), 2.02)
    sg('body', 'root', (0, 0.4, 0.6))
    # the pool ring (part of the body)
    for k_ in range(20):
        ang = math.radians(k_ * 18)
        b('pool_rock', (0.56, 0.44, 0.4 + 0.12 * (k_ % 2)), mm('rock'), (math.cos(ang) * 1.9, 0.5 + math.sin(ang) * 1.7, 0.2), rot=(0, 0, k_ * 18 + 90), bev=0.08)
    p('lava_pool', (3.2, 2.9, 0.06), mm('lava'), (0, 0.5, 0.22))
    B = b('back', (2.0, 2.0, 0.9), mm('main'), (0, 0.8, 0.5), bev=0.3)
    grid(B, 't', 4, 4, mm('dark'), (0.12, 0.12), name='back_spot', span=(0.6, 0.6), offset=0.2)
    grid(B, 'l', 2, 3, mm('belly'), (0.12, 0.12), name='side_spot', span=(0.6, 0.4))
    grid(B, 'r', 2, 3, mm('belly'), (0.12, 0.12), name='side_spot', span=(0.6, 0.4))
    for sgn in (-1, 1):
        b('ear_bump', (0.4, 0.4, 0.3), mm('main'), (sgn * 0.7, 1.4, 0.6), bev=0.1)
    # huge head with the yawning mouth (the silhouette)
    sg('head', 'body', (0, -0.2, 0.8))
    Hd = b('head', (1.6, 1.0, 0.7), mm('main'), (0, -0.4, 1.35), bev=0.2)
    b('upper_jaw', (1.5, 0.9, 0.5), mm('main'), (0, -0.85, 1.6), rot=(-25, 0, 0), bev=0.16)
    b('lower_jaw', (1.5, 0.9, 0.4), mm('main'), (0, -0.85, 0.65), rot=(15, 0, 0), bev=0.14)
    b('mouth_inside', (1.3, 0.7, 0.8), mm('mouth'), (0, -0.85, 1.1), bev=0.1)
    p('tongue', (0.8, 0.5, 0.12), mm('belly'), (0, -0.95, 0.86))
    for sgn in (-1, 1):
        b('tusk_low', (0.16, 0.16, 0.36), mm('tusk'), (sgn * 0.5, -1.15, 0.98), bev=0.03)
        b('tusk_up', (0.14, 0.14, 0.26), mm('tusk'), (sgn * 0.3, -1.18, 1.38), bev=0.03)
        p('nostril', (0.1, 0.06, 0.08), mm('dark'), (sgn * 0.3, -1.12, 1.92))
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.6, -0.2, Hd.top))
        a.ears.append(nm)
        b('ear', (0.24, 0.16, 0.24), mm('main'), (sgn * 0.62, -0.2, Hd.top + 0.08), bev=0.04)
        p('ear_in', (0.12, 0.04, 0.14), mm('belly'), (sgn * 0.62, -0.29, Hd.top + 0.08))
        p('blush', (0.16, 0.03, 0.08), mm('blush'), (sgn * 0.6, Hd.front - 0.012, 1.3))
    eyes(Box((0, -0.4, Hd.top - 0.05), (1.4, 1.0, 0.4), 'head'), 0.6, 0.27, 0.0, iris='#3a2e40', brow='#3a2e40', sleepy=0.45)
    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_spot', span=(0.5, 0.4))
    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_spot', span=(0.5, 0.4))
    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_spot', span=(0.5, 0.4))
    for t in range(6):
        p('small_tooth', (0.08, 0.08, 0.1), mm('tusk'), ((t - 2.5) * 0.18, -1.2, 0.82))
    for sgn in (-1, 1):
        for t in range(2):
            p('whisker', (0.2, 0.02, 0.02), mm('dark'), (sgn * 0.62, -1.2, 1.8 + t * 0.08), rot=(0, sgn * (10 - 20 * t), 0))
    # legs hidden in lava except front paws on the rim
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.7, 0.0, 0.4))
        a.legs.append(nm)
        b('paw', (0.4, 0.5, 0.3), mm('main'), (sgn * 0.85, -0.6, 0.35), bev=0.08)
        for t in range(3):
            p('toe', (0.1, 0.06, 0.08), mm('tusk'), (sgn * 0.85 + (t - 1) * 0.12, -0.86, 0.3))
    sg('tail', 'body', (0, 1.8, 0.6))
    a.tail = ['tail']
    p('tail', (0.2, 0.3, 0.2), mm('main'), (0, 1.85, 0.7))
    # lava bubbles in the pool
    for k_ in range(10):
        ang = math.radians(k_ * 36 + 15)
        p('lava_bubble', (0.18, 0.18, 0.14), mm('lava2'), (math.cos(ang) * 1.4, 0.5 + math.sin(ang) * 1.25, 0.28))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -1.2, 1.1), Hit=(0, 0.8, 1.0))
    return finish(a)


def lava_dragonfly(row):
    """lava dragonfly hovering level: a long thin segmented abdomen, two pairs of long narrow glassy wings in an X,
    a big round head that is almost all compound eye, six thin legs folded under"""
    zc = 0.4
    a = start(row, dict(main='#c83a1a', belly='#ffb84a', dark='#3a1a10', accent='#ffd84a', wing='#ffe8c8', vein='#ff8a3a', blush='#ff9ab4',
                        **{'*glow': '#ff8a3a', '*glow2': '#ffd84a'}), 1.1, hover=2.6, z0=zc)
    sg('body', 'root', (0, 0.0, zc))
    B = b('thorax', (0.6, 0.7, 0.6), mm('main'), (0, 0.0, zc), bev=0.12)
    grid(B, 't', 2, 2, mm('accent'), (0.1, 0.1), name='thorax_spot', span=(0.5, 0.5))
    grid(B, 'l', 2, 2, mm('dark'), (0.08, 0.08), name='thorax_side', span=(0.5, 0.5))
    grid(B, 'r', 2, 2, mm('dark'), (0.08, 0.08), name='thorax_side', span=(0.5, 0.5))
    sg('head', 'body', (0, -0.35, zc))
    Hd = b('head', (0.84, 0.6, 0.66), mm('main'), (0, -0.62, zc + 0.05), bev=0.18)
    for sgn in (-1, 1):
        b('compound_eye', (0.4, 0.5, 0.56), mm('accent'), (sgn * 0.28, -0.62, zc + 0.12), bev=0.14)
        for t in range(3):
            p('facet', (0.04, 0.1, 0.1), mm('belly'), (sgn * 0.49, -0.7 + t * 0.14, zc + 0.2))
    grid(Hd, 't', 2, 2, mm('dark'), (0.08, 0.08), name='head_dot', span=(0.4, 0.4), offset=0.1)
    eyes(Box((0, -0.62, zc + 0.05), (0.84, 0.66, 0.66), 'head'), 0.36, 0.28, 0.08, iris='#c83a1a', brow=None)
    p('smile', (0.14, 0.03, 0.04), mm('dark'), (0, -0.962, zc - 0.16))
    for sgn, n in LR:
        p('blush', (0.08, 0.03, 0.04), mm('blush'), (sgn * 0.2, -0.962, zc - 0.1))
        nm = 'antenna_' + n
        sg(nm, 'head', (sgn * 0.1, -0.7, zc + 0.35))
        a.ears.append(nm)
        p('antenna', (0.03, 0.03, 0.2), mm('dark'), (sgn * 0.12, -0.8, zc + 0.44), rot=(-30, sgn * 20, 0))
    # long thin abdomen in 4 segments (tail chain)
    use('body')
    par = 'body'
    a.tail = []
    for i in range(5):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        y0 = 0.35 + i * 0.6
        sg(nm, par, (0, y0, zc))
        a.tail.append(nm)
        for j in range(2):
            s = 0.24 - 0.018 * i
            b('abdomen', (s, 0.28, s), mm('main' if j == 0 else 'dark'), (0, y0 + 0.15 + j * 0.3, zc), bev=0.03)
            p('abd_ring', (s + 0.02, 0.06, s + 0.02), mm('accent'), (0, y0 + 0.3 + j * 0.3, zc))
        par = nm
    p('tail_tip', (0.1, 0.24, 0.1), mm('accent'), (0, 3.45, zc))
    # X wings: two pairs of long narrow wings (the silhouette)
    for sgn, n in LR:
        nm = 'wing_' + n
        sg(nm, 'body', (sgn * 0.3, 0.0, zc + 0.3))
        a.wings.append(nm)
        for k_, (dy, ang) in enumerate(((-0.15, -12), (0.2, 12))):
            b('wing', (1.8, 0.36, 0.04), mm('wing'), (sgn * 1.15, dy + math.sin(math.radians(ang)) * sgn * 0.9, zc + 0.32), rot=(0, 0, ang * sgn), bev=0.02)
            p('wing_vein', (1.7, 0.04, 0.05), mm('vein'), (sgn * 1.15, dy + math.sin(math.radians(ang)) * sgn * 0.9, zc + 0.33), rot=(0, 0, ang * sgn))
            p('wing_spot', (0.16, 0.2, 0.05), mm('vein'), (sgn * 1.9, dy + math.sin(math.radians(ang)) * sgn * 1.65, zc + 0.33), rot=(0, 0, ang * sgn))
            for q in range(4):
                rr = 0.5 + q * 0.32
                p('wing_cell', (0.04, 0.32, 0.05), mm('vein'), (sgn * rr, dy + math.sin(math.radians(ang)) * sgn * (rr - 0.25), zc + 0.33), rot=(0, 0, ang * sgn))
    # six folded legs
    for i, y in enumerate((-0.2, 0.0, 0.2)):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.2, y, zc - 0.3))
            a.legs.append(nm)
            p('leg', (0.04, 0.04, 0.3), mm('dark'), (sgn * 0.24, y - 0.05, zc - 0.42), rot=(-25, sgn * 10, 0))
            p('leg_foot', (0.06, 0.1, 0.04), mm('accent'), (sgn * 0.26, y - 0.12, zc - 0.56))
    # rarity 4: glowing abdomen rings and wing tips (glow seg)
    sg('glow', 'body', (0, 0.0, zc + 0.3))
    a.glow.append('glow')
    for sgn in (-1, 1):
        for k_, (dy, ang) in enumerate(((-0.15, -12), (0.2, 12))):
            p('wing_glow', (0.12, 0.12, 0.06), mm('glow2'), (sgn * 2.0, dy + math.sin(math.radians(ang)) * sgn * 1.75, zc + 0.34))
            p('wing_glow_root', (0.1, 0.1, 0.06), mm('glow'), (sgn * 0.4, dy + math.sin(math.radians(ang)) * sgn * 0.15, zc + 0.34))
    for i in range(8):
        p('ember_dot', (0.07, 0.07, 0.07), mm('glow'), (0.1 * math.sin(i * 2), 0.6 + i * 0.36, zc + 0.2), rot=(45, 45, 0))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, zc - 0.1), Hit=(0, 0.2, zc + 0.3))
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=1.6)
    return finish(a)


def volcanic_wyrm(row):
    """volcanic wyrm swimming through the ground: three basalt-plated humps arch out of lava rings in a row,
    the horned head rises from the front ring, the tail fin pokes out of the last one"""
    a = start(row, dict(main='#3a3034', belly='#ff9a5a', dark='#1a1416', accent='#ffb84a', plate='#5a4a50', horn='#e8d8c8', blush='#ff9ab4',
                        **{'*lava': '#ff6a1a', '*glow': '#ffb84a', '*glow2': '#ff4a2a'}), 3.9)
    sg('body', 'root', (0, 0.6, 0.4))
    B = None
    a.tail = []
    a.neck = []
    hump_y = (0.4, 1.6, 2.8)
    for hi, hy in enumerate(hump_y):
        nm = 'body' if hi == 0 else ('tail' if hi == 1 else 'tail2')
        if hi > 0:
            sg(nm, 'body' if hi == 1 else 'tail', (0, hy, 0.4))
            a.tail.append(nm)
        else:
            use('body')
        # lava rings where the body enters and leaves the ground
        for ry in (hy - 0.55, hy + 0.55):
            p('lava_ring', (0.9, 0.5, 0.06), mm('lava'), (0, ry, 0.04))
            p('rock_rim', (1.0, 0.1, 0.14), mm('dark'), (0, ry - 0.28, 0.07))
        r = 0.55 - 0.08 * hi
        for k_ in range(7):
            th = math.radians(k_ * 30)
            y = hy - math.cos(th) * r
            z = math.sin(th) * (0.9 - 0.15 * hi)
            s = 0.5 - 0.06 * hi
            bx = b('coil', (s, 0.3, s), mm('main'), (0, y, z + 0.1), rot=(-math.degrees(th) + 90, 0, 0), bev=0.06)
            if hi == 0 and k_ == 3:
                B = bx
            p('plate', (s + 0.06, 0.2, 0.1), mm('plate'), (0, y, z + 0.1 + s / 2 + 0.02), rot=(-math.degrees(th) + 90, 0, 0))
            p('belly_glow', (s * 0.6, 0.22, 0.05), mm('belly'), (0, y, z + 0.1 - s / 2 - 0.01), rot=(-math.degrees(th) + 90, 0, 0))
            for sgn in (-1, 1):
                p('lava_crack', (0.04, 0.16, 0.08), mm('lava'), (sgn * (s / 2 + 0.01), y, z + 0.1))
    # head rises from the first ring
    sg('neck1', 'body', (0, -0.2, 0.4))
    a.neck.append('neck1')
    for j in range(3):
        b('neck', (0.5, 0.4, 0.5), mm('main'), (0, -0.25 - 0.05 * j, 0.5 + j * 0.42), bev=0.06)
        p('neck_plate', (0.56, 0.2, 0.1), mm('plate'), (0, -0.05 - 0.05 * j, 0.6 + j * 0.42), rot=(70, 0, 0))
    sg('head', 'neck1', (0, -0.4, 1.7))
    Hd = b('head', (0.9, 0.9, 0.7), mm('main'), (0, -0.55, 1.95), bev=0.14)
    b('jaw', (0.7, 0.5, 0.26), mm('belly'), (0, Hd.front - 0.1, 1.68), bev=0.06)
    eyes(Hd, 0.3, 0.25, 0.16, iris='#ffb84a', glow='#ffb84a', brow='#1a1416', tilt=8)
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.32, Hd.front - 0.012, 1.86))
        nm = 'horn_' + n
        sg(nm, 'head', (sgn * 0.3, -0.5, Hd.top))
        a.ears.append(nm)
        for j in range(3):
            p('horn', (0.14 - 0.03 * j, 0.14 - 0.03 * j, 0.24), mm('horn'), (sgn * (0.32 + 0.08 * j), -0.45 + 0.1 * j, Hd.top + 0.1 + 0.2 * j), rot=(-25, sgn * 20, 0))
    grid(Hd, 't', 2, 2, mm('plate'), (0.12, 0.12), name='head_plate', span=(0.6, 0.6))
    grid(Hd, 'l', 2, 1, mm('lava'), (0.08, 0.08), name='cheek_crack', span=(0.5, 0.1))
    grid(Hd, 'r', 2, 1, mm('lava'), (0.08, 0.08), name='cheek_crack', span=(0.5, 0.1))
    # tail fin out of the last ring
    use('tail2')
    b('tail_fin', (0.1, 0.6, 0.9), mm('plate'), (0, 3.6, 0.5), rot=(-20, 0, 0), bev=0.03)
    p('fin_edge', (0.12, 0.08, 0.8), mm('lava'), (0, 3.85, 0.6), rot=(-20, 0, 0))
    # rarity 5: magma spout from the head (glow seg), orbit, yellow aura
    sg('glow', 'head', (0, -0.55, Hd.top + 0.2))
    a.glow.append('glow')
    for i in range(4):
        p('ember_spout', (0.16 - 0.02 * i, 0.16 - 0.02 * i, 0.16 - 0.02 * i), mm('glow' if i % 2 else 'glow2'), (0.1 * math.sin(i), -0.55, Hd.top + 0.5 + i * 0.25), rot=(45, 45, 0))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.7, 1.2), Hit=(0, 1.6, 0.8))
    orbit_kit((0, 1.6, 1.2), 2.6, 6, 'glow', 'glow2', size=0.16, dz=0.4, shape='flame')
    aura_kit(2.4, 5, motes=10, mote_col='glow', height=2.4, style='diamond')
    return finish(a)


def primordial_titan(row):
    """primordial titan: a huge mossy stone giant standing with both arms raised, holding a small blazing sun above its head;
    tree ferns grow on its shoulders, a lava heart glows through a crack in its chest"""
    a = start(row, dict(main='#6a6258', belly='#8a8070', dark='#2e2a28', accent='#ffb84a', moss='#4a8a3a', moss2='#6aaa4a', trunk='#6a4a30',
                        blush='#ff9ab4', **{'*sun': '#ffd84a', '*sun2': '#ff8a3a', '*lava': '#ff6a1a'}), 5.46)
    B, Hd = biped(tw=1.8, td=1.2, th=1.6, legh=0.9, lw=0.6, hw=1.1, hd=1.0, hh=1.0, arm_l=0.3, arm_w=0.36, hand=0.3, ntoe=3, foot='main', toe='dark')
    use('body')
    grid(B, 'f', 4, 3, mm('belly'), (0.14, 0.14), name='stone_block', span=(0.7, 0.4), offset=-0.5)
    grid(B, 'k', 3, 3, mm('belly'), (0.16, 0.16), name='stone_block', span=(0.7, 0.7))
    grid(B, 'l', 2, 3, mm('moss'), (0.14, 0.14), name='moss_patch', span=(0.6, 0.6))
    grid(B, 'r', 2, 3, mm('moss'), (0.14, 0.14), name='moss_patch', span=(0.6, 0.6))
    b('chest_crack', (0.36, 0.1, 0.7), mm('dark'), (0, B.front - 0.02, B.c.z + 0.1), rot=(0, 15, 0), bev=0.02)
    # shoulder tree ferns
    for sgn in (-1, 1):
        sx = sgn * 0.72
        b('shoulder_moss', (0.6, 0.8, 0.2), mm('moss'), (sx, B.c.y, B.top + 0.08), bev=0.05)
        b('fern_trunk', (0.14, 0.14, 0.6), mm('trunk'), (sx, B.c.y + 0.2, B.top + 0.4), bev=0.02)
        for j in range(7):
            ang = math.radians(j * 51.4)
            b('fern_frond', (0.6, 0.16, 0.06), mm('moss2' if j % 2 else 'moss'), (sx + math.cos(ang) * 0.3, B.c.y + 0.2 + math.sin(ang) * 0.3, B.top + 0.7), rot=(0, 15, j * 51.4), bev=0.02)
        for t in range(2):
            p('shoulder_rock', (0.2, 0.2, 0.16), mm('belly'), (sx + sgn * 0.2, B.c.y - 0.3 + t * 0.4, B.top + 0.2))
    # face
    use('head')
    mz = muzzle(Hd, (0.5, 0.2, 0.3), -0.3, 'belly', nose=None, mouth=True)
    eyes(Hd, 0.32, 0.25, 0.12, iris='#ffb84a', glow='#ffb84a', brow='#2e2a28')
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('blush'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.16))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.5, Hd.c.y, Hd.c.z))
        a.ears.append(nm)
        b('stone_ear', (0.16, 0.3, 0.36), mm('main'), (sgn * 0.6, Hd.c.y, Hd.c.z), bev=0.04)
    b('moss_hair', (Hd.s.x + 0.06, Hd.s.y + 0.06, 0.24), mm('moss'), (0, Hd.c.y, Hd.top + 0.06), bev=0.06)
    for j in range(8):
        p('moss_drip', (0.1, 0.14, 0.2 + 0.06 * (j % 2)), mm('moss2'), ((j - 3.5) * 0.14, Hd.c.y - Hd.s.y / 2 - 0.02, Hd.top - 0.1))
    grid(Hd, 'l', 2, 2, mm('moss'), (0.1, 0.1), name='face_moss', span=(0.5, 0.5))
    # both arms raised holding the sun (the silhouette)
    for sgn, n in LR:
        use('arm_' + n)
        b('raised_arm', (0.44, 0.44, 2.0), mm('belly'), (sgn * 1.0, B.c.y - 0.2, B.top + 0.9), rot=(0, sgn * -9, 0), bev=0.08)
        b('raised_hand', (0.54, 0.54, 0.44), mm('main'), (sgn * 0.82, B.c.y - 0.2, B.top + 2.0), bev=0.08)
        for t in range(3):
            p('arm_moss', (0.2, 0.2, 0.12), mm('moss'), (sgn * (1.25 - 0.1 * t), B.c.y - 0.2, B.top + 0.3 + 0.35 * t))
    # rarity 6: the sun (glow seg between the hands), lava heart, crown, two orbits, red aura
    sg('glow', 'body', (0, B.c.y - 0.2, B.top + 2.45))
    a.glow.append('glow')
    b('sun', (0.9, 0.9, 0.9), mm('sun'), (0, B.c.y - 0.2, B.top + 2.45), bev=0.2)
    for k_ in range(12):
        ang = math.radians(k_ * 30)
        p('sun_ray', (0.14, 0.14, 0.36), mm('sun2'), (math.cos(ang) * 0.68, B.c.y - 0.2, B.top + 2.45 + math.sin(ang) * 0.68), rot=(0, 90 - k_ * 30, 0))
    use('body')
    b('lava_heart', (0.24, 0.12, 0.5), mm('lava'), (0, B.front - 0.06, B.c.z + 0.1), rot=(0, 15, 0), bev=0.02)
    halo_kit(Hd, 'sun', r=0.46, n=6, dz=0.7, kind='leaves')
    use('body')
    a.bx.update(body=B, head=Hd)
    orbit_kit((0, B.c.y, B.c.z + 0.8), 2.8, 6, 'sun', 'sun2', size=0.18, dz=0.6, shape='leaf')
    orbit_kit((0, B.c.y, B.c.z - 0.2), 3.2, 8, 'lava', 'sun', size=0.12, name='orbit2', dz=0.2, shape='flame')
    aura_kit(2.6, 6, motes=12, mote_col='sun2', height=4.4, style='double')
    return finish(a)


ANIMALS = dict(caldera_tarsier=caldera_tarsier, ember_salamander=ember_salamander, magma_hippo=magma_hippo,
               lava_dragonfly=lava_dragonfly, volcanic_wyrm=volcanic_wyrm, primordial_titan=primordial_titan)
