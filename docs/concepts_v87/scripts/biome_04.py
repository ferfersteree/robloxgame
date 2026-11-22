# Biome 4 - Ancient Forest: giant trees, crystals, spirit lights, snow
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 4
GROUND = '#8fb4c8'
SKY = '#dcecf6'
THEME = dict(bits=['#ffffff', '#9fe8ff'], dust='#eef6ff', glow='#9fe8ff', splash='#cfefff', bit_name='снег и льдинки')
BUSH_NAME = 'заснеженный пень древнего дерева с корнями, ледяными кристаллами и огоньками духов'


def bush():
    B = begin_bush(NN)
    bark = mat('bark', '#7a5a44')
    bark2 = mat('bark2', '#5e4232')
    ring = mat('ring', '#e8cfa0')
    snow = mat('snow', '#ffffff')
    snow2 = mat('snow2', '#dff0fa')
    ice = mat('ice', '#9fe8ff', 'smooth')
    ice2 = mat('ice2', '#5ac8f0', 'smooth')
    core = mat('core', '#c8f6ff', 'neon', 2.2)
    fern = mat('fern', '#8fd0c0')
    fern2 = mat('fern2', '#bfeee0')
    stone = mat('stone', '#8a96a6')
    wisp = mat('wisp', '#fff6a0', 'neon', 2.6)
    # giant stump
    part('big', (0, 0.3, 0.2), 'stump')
    b('stump', (2.8, 2.4, 1.9), bark, (0, 0.3, 0.95), bev=0.12)
    b('stump_top', (2.5, 2.1, 0.16), ring, (0, 0.3, 1.94), bev=0.04)
    p('stump_ring', (1.6, 1.3, 0.03), mat('ring2', '#c8a878'), (0, 0.3, 2.03))
    p('stump_ring', (0.8, 0.6, 0.03), ring, (0, 0.3, 2.045))
    for i, x in enumerate((-1.0, -0.3, 0.5, 1.1)):
        p('bark_groove', (0.12, 0.05, 1.3 - 0.2 * (i % 2)), bark2, (x, -0.92, 0.9))
    p('knot', (0.4, 0.06, 0.4), bark2, (0.3, -0.925, 1.3))
    p('knot_in', (0.2, 0.07, 0.2), mat('hole', '#2a1c18'), (0.3, -0.93, 1.3))
    # broken trunk shard rising behind
    part('big', (-0.6, 0.9, 1.9), 'shard')
    b('shard', (1.0, 0.7, 1.6), bark, (-0.6, 0.9, 2.7), rot=(0, -6, 0), bev=0.1)
    b('shard_tip', (0.5, 0.5, 0.9), bark, (-0.8, 0.9, 3.7), rot=(0, -10, 0), bev=0.08)
    p('shard_snow', (0.6, 0.6, 0.14), snow, (-0.86, 0.9, 4.2))
    # roots
    for i, (x, y, rz, ln) in enumerate(((-2.0, -0.5, 20, 2.0), (2.0, -0.4, -25, 2.1), (-1.9, 1.2, -30, 1.6), (2.1, 1.1, 30, 1.7), (0.2, -1.5, 90, 1.3))):
        part('big', (x * 0.6, y * 0.6 + 0.3, 0.4), 'root_%d' % i)
        b('root', (ln, 0.6, 0.6), bark, (x, y, 0.4), rot=(0, 0, rz), bev=0.1)
        b('root_tip', (ln * 0.5, 0.4, 0.36), bark2, (x * 1.5, y * 1.5, 0.22), rot=(0, 0, rz), bev=0.08)
        p('root_snow', (ln * 0.7, 0.44, 0.12), snow, (x, y, 0.74), rot=(0, 0, rz))
    # snow caps
    part('big', (0.6, 0.3, 2.0), 'snowcap')
    b('snowcap', (1.4, 1.5, 0.4), snow, (0.6, 0.4, 2.2), bev=0.12)
    b('snowcap_b', (0.8, 0.9, 0.3), snow2, (0.8, 0.5, 2.5), bev=0.1)
    for i, x in enumerate((0.1, 0.6, 1.1)):
        p('icicle', (0.12, 0.1, 0.4 - 0.1 * (i % 2)), ice, (x, -0.95, 1.7 + 0.05 * (i % 2)))
    # boulders
    for i, (x, y, s) in enumerate(((-3.0, 0.4, 1.0), (3.0, 0.0, 0.8))):
        part('big', (x, y, 0.1), 'boulder_%d' % i)
        b('boulder', (1.3 * s, 1.2 * s, 1.1 * s), stone, (x, y, 0.55 * s), rot=(0, 0, 15 * (1 - 2 * i)), bev=0.14)
        b('boulder_snow', (1.1 * s, 1.0 * s, 0.24), snow, (x, y, 1.14 * s), rot=(0, 0, 15 * (1 - 2 * i)), bev=0.08)
        p('boulder_moss', (0.4 * s, 0.05, 0.3 * s), fern, (x + 0.1, y - 0.61 * s, 0.5 * s))
    # ice crystal clusters (smooth plastic, glowing cores)
    for i, (x, y, z, s) in enumerate(((-2.2, -0.9, 0.3, 1.2), (1.6, -1.2, 0.3, 1.0), (-1.2, 0.4, 2.0, 1.5), (1.5, 1.2, 0.6, 1.9), (-3.2, -0.5, 0.2, 0.8), (2.9, 0.9, 0.2, 1.1))):
        part('small', (x, y, z), 'crystal_%d' % i)
        cn('crystal', 0.26 * s, 1.25 * s, ice, (x, y, z), (0.08, 0, 1))
        cn('crystal', 0.18 * s, 0.8 * s, ice2, (x + 0.3 * s, y + 0.1, z), (0.5, 0.1, 1))
        cn('crystal', 0.15 * s, 0.62 * s, ice, (x - 0.28 * s, y - 0.08, z), (-0.55, -0.1, 1))
        cn('crystal', 0.12 * s, 0.45 * s, ice2, (x + 0.05, y - 0.26 * s, z), (0.1, -0.6, 1))
        p('crystal_core', (0.12 * s, 0.12 * s, 0.5 * s), core, (x, y, z + 0.45 * s))
    # frozen ferns
    for i, (x, y, rz) in enumerate(((-1.5, -1.5, 20), (0.9, -1.75, -15), (2.5, -0.9, -40), (-2.7, 1.2, 60))):
        part('small', (x, y, 0.1), 'fern_%d' % i)
        for k_ in range(4):
            t = k_ / 3.0
            b('frond', (0.56 - 0.1 * k_, 0.34 - 0.05 * k_, 0.1), fern if k_ % 2 else fern2,
              (x + math.cos(math.radians(rz + 90)) * 0.0, y - 0.3 * t, 0.2 + 0.5 * math.sin(math.pi * t * 0.8)), rot=(0, 0, rz), bev=0.03)
        p('frond_frost', (0.2, 0.14, 0.04), snow, (x, y - 0.15, 0.62), rot=(0, 0, rz))
    # spirit lights on thin stalks
    for i, (x, y, h) in enumerate(((-0.9, -1.2, 1.5), (1.9, 0.3, 2.3), (-2.2, 0.6, 1.9))):
        part('small', (x, y, 0.2), 'wisp_%d' % i)
        b('wisp_stalk', (0.06, 0.06, h), fern2, (x, y, h / 2 + 0.1), bev=0.01)
        b('wisp', (0.28, 0.28, 0.28), wisp, (x, y, h + 0.26), rot=(45, 45, 0), bev=0.05)
        p('wisp_cap', (0.14, 0.14, 0.08), fern, (x, y, h + 0.1))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def megadeer(row):
    """giant deer whose antlers are a little TREE: two trunks branching up into a leafy crown with a bird nest, shaggy neck mane"""
    a = start(row, dict(main='#8a6240', belly='#e8d0a8', dark='#3a2414', accent='#c89a5c', bark='#6a4a30', leaf='#5aa83a', leaf2='#8ac84a',
                        nest='#a8784a', egg='#a8e0ff'), 4.57)
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


def rhino(row):
    a = start(row, dict(main='#8e6a50', belly='#b08a68', dark='#5a4030', accent='#6e4e3a', horn='#f2e6cc'), 1.92)
    B, Hd = quad(bw=1.28, bl=1.62, bh=1.0, legh=0.4, lw=0.36, hw=1.2, hd=1.1, hh=1.0, head_up=0.22, hump=0.3, toe='horn',
                 leg_fl=0.5, head_fwd=0.4)
    mz = muzzle(Hd, (0.7, 0.4, 0.46), -0.24, 'belly', nose=None, mouth=True)
    for sgn, n in LR:
        p('nostril', (0.1, 0.03, 0.07), mm('line'), (sgn * 0.18, mz.front - 0.008, mz.c.z + 0.08))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.44, Hd.front - 0.012, Hd.c.z - 0.26))
    # two horns: big front one, small second (the silhouette)
    b('horn_base', (0.3, 0.3, 0.2), mm('horn'), (0, mz.c.y - 0.04, mz.top + 0.08), bev=0.05)
    cn('horn', 0.14, 0.66, mm('horn'), (0, mz.c.y - 0.04, mz.top + 0.14), (0, -0.25, 1))
    cn('horn2', 0.1, 0.3, mm('horn'), (0, Hd.front + 0.16, Hd.top - 0.02), (0, -0.2, 1))
    eyes(Hd, 0.26, 0.28, 0.14, iris='#4a2a16', brow='#5a4030', tilt=-6, sleepy=0.1)
    ears(Hd, 'point', 'main', 'pink', tip='dark', x=0.4, h=0.3, w=0.22, lean=20)
    use('body')
    hp = a.bx['hump']
    # woolly coat: stepped shag on the back and flanks
    for i in range(3):
        for j in range(4):
            p('wool', (0.36, 0.3, 0.14), mm('accent' if (i + j) % 2 else 'dark'), ((i - 1) * 0.38, B.front + 0.2 + j * 0.36, B.top + 0.06 + (0.3 if j < 2 else 0.0) + 0.02 * ((i + j) % 2)))
    for sgn, n in LR:
        for j in range(5):
            p('wool_side', (0.07, 0.28, 0.34 - 0.03 * (j % 2)), mm('accent'), (sgn * (B.s.x / 2 + 0.02), B.front + 0.14 + j * 0.3, B.c.z - 0.2))
    fluff(a.bx['chest'], 'f', mm('accent'), 3, 0.9, 0.3, th=0.07)
    spots(a.bx['rump'], 'lr', 2, mm('accent'), 0.2, seed=3, name='patch')
    for ft in a.bx['feet']:
        p('ankle', (ft.s.x + 0.02, ft.s.y * 0.8, 0.08), mm('accent'), (ft.c.x, ft.c.y + 0.04, ft.top + 0.06))
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)
    return finish(a)


def _mammoth(a, wool='accent'):
    """shared mammoth body: domed head, trunk (2 segments), tusks, big ears"""
    B, Hd = quad(bw=1.34, bl=1.5, bh=1.12, legh=0.6, lw=0.42, hw=1.3, hd=1.1, hh=1.16, head_up=0.5, hump=0.22, toe='horn',
                 leg_fl=0.52, head_fwd=0.3, ntoe=3)
    use('head')
    b('dome', (0.9, 0.8, 0.3), mm('main'), (0, Hd.c.y, Hd.top + 0.14), bev=0.1)
    for i in range(3):
        b('dome_tuft', (0.26, 0.26, 0.2), mm(wool), ((i - 1) * 0.26, Hd.c.y - 0.1, Hd.top + 0.36), bev=0.05)
    for sgn, n in LR:
        p('blush', (0.18, 0.03, 0.09), mm('pink'), (sgn * 0.46, Hd.front - 0.012, Hd.c.z - 0.2))
        # tusks curving forward and up
        b('tusk_a', (0.18, 0.3, 0.18), mm('horn'), (sgn * 0.3, Hd.front - 0.1, Hd.bot + 0.14), bev=0.05)
        b('tusk_b', (0.17, 0.44, 0.17), mm('horn'), (sgn * 0.36, Hd.front - 0.42, Hd.bot + 0.08), rot=(-12, 0, sgn * 10), bev=0.05)
        b('tusk_c', (0.15, 0.3, 0.15), mm('horn'), (sgn * 0.42, Hd.front - 0.74, Hd.bot + 0.18), rot=(-45, 0, sgn * 10), bev=0.05)
        p('tusk_tip', (0.1, 0.12, 0.14), mm('horn'), (sgn * 0.44, Hd.front - 0.86, Hd.bot + 0.34))
    p('mouth', (0.3, 0.03, 0.04), mm('line'), (0, Hd.front - 0.008, Hd.bot + 0.1))
    # trunk: two segments so it can swing
    sg('trunk', 'head', (0, Hd.front, Hd.c.z - 0.1))
    b('trunk_a', (0.4, 0.34, 0.5), mm('main'), (0, Hd.front - 0.12, Hd.c.z - 0.3), bev=0.06)
    p('trunk_ring', (0.42, 0.36, 0.05), mm(wool), (0, Hd.front - 0.12, Hd.c.z - 0.34))
    sg('trunk2', 'trunk', (0, Hd.front - 0.14, Hd.c.z - 0.54))
    b('trunk_b', (0.32, 0.3, 0.5), mm('main'), (0, Hd.front - 0.16, Hd.c.z - 0.76), bev=0.06)
    p('trunk_ring', (0.34, 0.32, 0.05), mm(wool), (0, Hd.front - 0.16, Hd.c.z - 0.8))
    b('trunk_tip', (0.26, 0.34, 0.22), mm('main'), (0, Hd.front - 0.26, Hd.c.z - 1.06), bev=0.06)
    p('trunk_nose', (0.14, 0.04, 0.1), mm('pink'), (0, Hd.front - 0.44, Hd.c.z - 1.06))
    a.trunk = ['trunk', 'trunk2']

    def trunk_idle(c, n):
        for x, r in ((1, 0), (n // 4, 10), (n // 2, 0), (3 * n // 4, -10), (n, 0)):
            k(c, 'trunk', x, rot=(-4 if r else 0, 0, r))
            k(c, 'trunk2', min(n, x), rot=(-abs(r) * 1.4, 0, r * 0.8))

    def trunk_show(c, T, n):
        for x, r in ((0, 0), (0.3, -70), (0.5, -60), (0.7, -70), (1.0, 0)):
            k(c, 'trunk', int(T + n * x), rot=(r, 0, 0))
            k(c, 'trunk2', int(T + n * x), rot=(r * 0.9, 0, 0))
    a.extra_idle.append(trunk_idle)
    a.extra_reveal.append(trunk_show)
    use('head')
    return B, Hd


def mammoth(row):
    a = start(row, dict(main='#8a5c3c', belly='#a8785a', dark='#4e3222', accent='#6a4028', horn='#fff2d8'), 2.9)
    B, Hd = _mammoth(a)
    eyes(Hd, 0.26, 0.27, 0.18, iris='#4a2a16', brow='#4e3222', tilt=8, lash=True)
    ears(Hd, 'flop', 'main', 'belly', x=0.52, h=0.7, w=0.44)
    use('body')
    hp = a.bx['hump']
    for i in range(3):
        for j in range(4):
            p('wool', (0.38, 0.3, 0.14), mm('accent' if (i + j) % 2 else 'dark'), ((i - 1) * 0.4, B.front + 0.16 + j * 0.34, B.top + 0.06 + (0.22 if j < 2 else 0.0)))
    for sgn, n in LR:
        for j in range(5):
            p('wool_side', (0.07, 0.26, 0.4 - 0.05 * (j % 2)), mm('accent'), (sgn * (B.s.x / 2 + 0.02), B.front + 0.12 + j * 0.28, B.c.z - 0.26))
    fluff(a.bx['chest'], 'f', mm('accent'), 3, 0.9, 0.3, th=0.07)
    # rarity 3: woven blanket with a pattern + head band with a gem
    setm('cloth', '#e8443a')
    setm('cloth2', '#ffd84a')
    setm('cloth3', '#3fa8d8')
    b('blanket', (B.s.x + 0.1, 0.8, 0.1), mm('cloth'), (0, B.c.y + 0.1, B.top + 0.05), bev=0.03)
    for sgn, n in LR:
        b('blanket_side', (0.08, 0.8, 0.56), mm('cloth'), (sgn * (B.s.x / 2 + 0.05), B.c.y + 0.1, B.top - 0.26), bev=0.03)
        p('blanket_trim', (0.1, 0.84, 0.08), mm('cloth2'), (sgn * (B.s.x / 2 + 0.055), B.c.y + 0.1, B.top - 0.56))
        for j in range(3):
            p('blanket_diamond', (0.1, 0.16, 0.16), mm('cloth3' if j == 1 else 'cloth2'), (sgn * (B.s.x / 2 + 0.06), B.c.y - 0.16 + j * 0.26, B.top - 0.24), rot=(45, 0, 0))
            p('blanket_tassel', (0.06, 0.08, 0.14), mm('cloth2'), (sgn * (B.s.x / 2 + 0.055), B.c.y - 0.2 + j * 0.3, B.top - 0.66))
    for j in range(4):
        p('blanket_stripe', (B.s.x * 0.8, 0.07, 0.11), mm('cloth2' if j % 2 else 'cloth3'), (0, B.c.y - 0.2 + j * 0.2, B.top + 0.06))
    use('head')
    b('head_band', (Hd.s.x + 0.06, 0.1, 0.14), mm('cloth'), (0, Hd.front + 0.03, Hd.top - 0.1), bev=0.02)
    p('head_gem', (0.2, 0.06, 0.2), mm('cloth3'), (0, Hd.front - 0.04, Hd.top - 0.1), rot=(0, 45, 0))
    for sgn, n in LR:
        p('head_bead', (0.1, 0.06, 0.1), mm('cloth2'), (sgn * 0.3, Hd.front - 0.03, Hd.top - 0.1), rot=(0, 45, 0))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)
    return finish(a)


def cavelion(row):
    a = start(row, dict(main='#e8d8b8', belly='#fff8e8', dark='#a88a5a', accent='#c8b088', **{'*glow': '#9fe8ff'}), 2.45)
    B, Hd = quad(bw=0.98, bl=1.4, bh=0.78, legh=0.58, lw=0.3, hw=1.2, hd=0.96, hh=0.96, toe='dark', leg_fl=0.46, hump=0.08)
    mz = muzzle(Hd, (0.5, 0.26, 0.3), -0.26, 'belly', nose=(0.2, 0.09, 0.12), nose_mat='pink', top='main', fangs=1)
    cheeks(Hd, 'belly', (0.28, 0.24, 0.3), -0.25, whisk=3)
    eyes(Hd, 0.33, 0.25, 0.1, iris='#3a8ab0', glow='#9fe8ff', brow='#a88a5a', tilt=-10)
    ears(Hd, 'round', 'main', 'pink', x=0.4, h=0.26, w=0.3, lean=8)
    # short ruff mane around the neck and cheeks
    for sgn, n in LR:
        b('ruff', (0.22, 0.4, 0.6), mm('accent'), (sgn * (Hd.s.x / 2 + 0.04), Hd.c.y + 0.16, Hd.c.z - 0.1), bev=0.06)
        p('ruff_tuft', (0.16, 0.2, 0.2), mm('accent'), (sgn * (Hd.s.x / 2 + 0.14), Hd.c.y + 0.12, Hd.c.z - 0.46))
        p('ruff_tuft', (0.14, 0.2, 0.18), mm('accent'), (sgn * (Hd.s.x / 2 + 0.16), Hd.c.y + 0.2, Hd.c.z + 0.2))
    for i in range(4):
        b('ruff_top', (0.24, 0.22, 0.18), mm('accent'), ((i - 1.5) * 0.26, Hd.back + 0.02, Hd.top + 0.02), bev=0.05)
    use('body')
    for j in range(3):
        b('ruff_chest', (0.7 - 0.14 * j, 0.14, 0.2), mm('accent'), (0, B.front - 0.1 - 0.01 * j, B.top - 0.12 - j * 0.2), bev=0.04)
    spots(B, 'lr', 6, mm('dark'), 0.12, seed=5, name='spot')
    spots(a.bx['rump'], 'tlr', 5, mm('dark'), 0.11, seed=8, name='spot')
    on(B, 't', 0, 0.1, (0.22, B.s.y * 0.7), mm('accent'), name='back_stripe')
    for ft in a.bx['feet']:
        p('leg_band', (ft.s.x - 0.02, ft.s.y * 0.6, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.08, 0.36))
        p('pad', (ft.s.x * 0.6, 0.03, 0.06), mm('pink'), (ft.c.x, ft.back + 0.012, 0.06))
    tail_kit('tuft', 'body', a.tail_j, 'main', 'accent', size=0.2)
    # rarity 4: frost runes, glowing tail tuft and brow crystal, snow sparks
    glow_marks(B, ('l', 'r'), 3, 'glow', style='star', size=0.15)
    use('glow')
    for i in range(3):
        on(B, 't', 0, -0.32 + i * 0.26, (0.14, 0.14), mm('glow'), th=0.035, name='glow_back', rot=(0, 0, 45))
    use('tail')
    p('tail_glow', (0.16, 0.16, 0.16), mm('glow'), (0, a.tail_j[1] + 0.5, a.tail_j[2] - 0.22), rot=(45, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.top))
    a.glow.append('glow_h')
    cn('brow_crystal', 0.09, 0.3, mm('glow'), (0, Hd.front + 0.1, Hd.top - 0.02), (0, -0.3, 1))
    for sgn, n in LR:
        cn('brow_crystal', 0.06, 0.18, mm('glow'), (sgn * 0.16, Hd.front + 0.1, Hd.top - 0.02), (sgn * 0.4, -0.3, 1))
        on(Hd, 'f', sgn * 0.4, -0.3, (0.08, 0.08), mm('glow'), th=0.035, name='cheek_star', rot=(0, 45, 0))
    aura_kit(1.4, 4, motes=8, mote_col='glow', height=1.8)
    return finish(a)


def icemammoth(row):
    """glacier mammoth: stilt-tall legs and a short high body, trunk curled up in an S, spiral tusks rising like horns, ice-shard ridge"""
    a = start(row, dict(main='#bfe4f6', belly='#eaf8ff', dark='#5a9ac8', accent='#8fc8ea', horn='#ffffff', snow='#ffffff',
                        **{'*glow': '#7fe0ff', '*glow2': '#fff6a0'}), 3.4)
    B, Hd = quad(bw=1.1, bl=1.2, bh=1.0, legh=1.4, lw=0.36, hw=1.1, hd=0.96, hh=1.0, head_up=0.6, toe='horn', leg_fl=0.46, head_fwd=0.3,
                 ntoe=3, hump=0.0, rump=False)
    use('head')
    for sgn, n in LR:
        # tusks spiral upward like horns (silhouette), not forward
        for j in range(5):
            ang = math.radians(j * 55)
            b('tusk', (0.16 - 0.015 * j, 0.16 - 0.015 * j, 0.24), mm('horn'), (sgn * (0.3 + 0.18 * math.cos(ang)), Hd.front + 0.1 - 0.18 * math.sin(ang), Hd.bot + 0.2 + j * 0.22), bev=0.04)
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.42, Hd.front - 0.012, Hd.c.z - 0.24))
        b('ear', (0.14, 0.5, 0.5), mm('accent'), (sgn * (Hd.s.x / 2 + 0.06), Hd.c.y + 0.1, Hd.c.z), bev=0.05)
    # trunk curled up in an S (two segments)
    sg('trunk', 'head', (0, Hd.front, Hd.c.z - 0.2))
    b('trunk_a', (0.34, 0.3, 0.44), mm('main'), (0, Hd.front - 0.12, Hd.c.z - 0.4), bev=0.06)
    sg('trunk2', 'trunk', (0, Hd.front - 0.2, Hd.c.z - 0.6))
    b('trunk_b', (0.28, 0.4, 0.26), mm('main'), (0, Hd.front - 0.4, Hd.c.z - 0.66), bev=0.06)
    b('trunk_c', (0.24, 0.24, 0.4), mm('main'), (0, Hd.front - 0.6, Hd.c.z - 0.44), bev=0.05)
    p('trunk_tip', (0.2, 0.08, 0.1), mm('pink'), (0, Hd.front - 0.64, Hd.c.z - 0.22))
    for j in range(3):
        p('trunk_ring', (0.3, 0.32, 0.04), mm('accent'), (0, Hd.front - 0.12 - 0.14 * j, Hd.c.z - 0.36 - 0.1 * j))
    a.trunk = ['trunk', 'trunk2']
    a.extra_idle.append(lambda c, n: [k(c, 'trunk2', x, rot=(r, 0, 0)) for x, r in ((1, 0), (n // 2, -12), (n, 0))])
    eyes(Hd, 0.26, 0.27, 0.14, iris='#2a7ab0', glow='#7fe0ff', brow='#5a9ac8', tilt=8, lash=True)
    use('body')
    # short shaggy coat hanging like an icicle skirt
    for sgn, n in LR:
        for j in range(4):
            b('coat', (0.1, 0.28, 0.5), mm('accent' if j % 2 else 'snow'), (sgn * (B.s.x / 2 + 0.05), B.front + 0.16 + j * 0.28, B.bot + 0.1), bev=0.03)
            p('icicle', (0.06, 0.08, 0.2), mm('glow'), (sgn * (B.s.x / 2 + 0.05), B.front + 0.16 + j * 0.28, B.bot - 0.24))
    for j in range(4):
        b('coat_front', (0.24, 0.1, 0.46), mm('snow'), ((j - 1.5) * 0.26, B.front - 0.05, B.bot + 0.08), bev=0.03)
    grid(B, 't', 3, 3, mm('snow'), (0.16, 0.16), name='snow', th=0.06)
    grid(B, 'l', 4, 2, mm('dark'), (0.12, 0.12), name='fur_ring', offset=0.06)
    grid(B, 'r', 4, 2, mm('dark'), (0.12, 0.12), name='fur_ring', offset=0.06)
    grid(B, 'k', 3, 3, mm('accent'), (0.14, 0.14), name='rump_fur')
    grid(B, 'f', 3, 2, mm('snow'), (0.14, 0.14), name='chest_frost')
    grid(B, 'u', 3, 3, mm('accent'), (0.16, 0.16), name='belly_frost', th=0.08)
    use('head')
    grid(Hd, 't', 3, 2, mm('snow'), (0.14, 0.14), name='head_snow', th=0.06)
    grid(Hd, 'f', 3, 1, mm('accent'), (0.1, 0.1), name='brow_frost', span=(0.6, 0.2), offset=0.0)
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(3):
            p('leg_ring', (ft.s.x + 0.04, ft.s.y + 0.04, 0.06), mm('dark' if j % 2 else 'accent'), (ft.c.x, ft.c.y, 0.4 + j * 0.34))
    use('body')
    tail_kit('tuft', 'body', (0, B.back + 0.04, B.c.z), 'main', 'snow', size=0.14)
    # rarity 5: ice-shard ridge along the spine (own glowing segment), glowing trunk tip, cross orbit, yellow aura
    sg('glow', 'body', (0, B.c.y, B.top))
    a.glow.append('glow')
    for j in range(5):
        cn('ridge_shard', 0.14, 0.7 - 0.08 * abs(j - 2), mm('glow' if j % 2 else 'glow2'), (0, B.front + 0.12 + j * 0.24, B.top - 0.02), (0, 0.2, 1))
    for sgn, n in LR:
        cn('side_shard', 0.08, 0.36, mm('glow'), (sgn * 0.4, B.c.y, B.top - 0.02), (sgn * 0.8, 0, 0.8))
    use('trunk2')
    p('trunk_glow', (0.16, 0.06, 0.1), mm('glow'), (0, Hd.front - 0.66, Hd.c.z - 0.2))
    use('body')
    orbit_kit((0, 0.2, 2.6), 1.6, 6, 'glow', 'glow2', size=0.14, dz=0.5, shape='shard')
    aura_kit(1.6, 5, motes=10, mote_col='glow', height=3.2, style='diamond')
    return finish(a)


def yeti(row):
    a = start(row, dict(main='#dde7f6', belly='#bcd8ee', dark='#6aa8d8', accent='#dbeafa', face='#7fbfe8', horn='#e8f4ff',
                        **{'*glow': '#7fe0ff', '*glow2': '#fff6a0', '*gold': '#ffd84a'}), 3.6)
    B, Hd = biped(tw=1.5, td=1.0, th=1.12, legh=0.5, lw=0.46, hw=1.3, hd=1.0, hh=1.02, arm_l=1.34, arm_w=0.46, hand=0.58,
                  shoulder=0.34, foot='face', toe='dark', hand_mat='face')
    use('head')
    fc = b('face', (0.96, 0.1, 0.7), mm('face'), (0, Hd.front - 0.02, Hd.c.z - 0.08), bev=0.04)
    mz = muzzle(Hd, (0.5, 0.2, 0.3), -0.3, 'face', nose=(0.2, 0.08, 0.12), nose_mat='dark', fangs=0)
    for sgn, n in LR:
        p('tooth_up', (0.08, 0.04, 0.12), mm('white'), (sgn * 0.14, mz.front - 0.005, mz.c.z - 0.02))
        p('blush', (0.18, 0.03, 0.09), mm('pink'), (sgn * 0.36, fc.front - 0.012, Hd.c.z - 0.24))
        cn('horn', 0.12, 0.34, mm('horn'), (sgn * 0.46, Hd.c.y, Hd.top - 0.04), (sgn * 0.5, 0, 1))
        for j in range(3):
            p('cheek_fur', (0.16, 0.2, 0.2 - 0.03 * j), mm('main'), (sgn * (Hd.s.x / 2 + 0.03), Hd.front + 0.2 + j * 0.2, Hd.c.z - 0.3 + 0.06 * j))
    for i in range(5):
        b('brow_fur', (0.26, 0.2, 0.2 + 0.05 * (i % 2)), mm('main'), ((i - 2) * 0.25, Hd.front + 0.04, Hd.top - 0.02), bev=0.05)
    eyes(Hd, 0.3, 0.2, 0.06, iris='#2a7ab0', glow='#7fe0ff', brow='#6aa8d8', tilt=-10)
    use('body')
    # fluffy coat: stepped tufts on shoulders, chest, hips
    for i in range(4):
        for sgn, n in LR:
            p('fur', (0.2, 0.24, 0.22), mm('accent' if i % 2 else 'main'), (sgn * (B.s.x / 2 + 0.03), B.c.y - 0.3 + i * 0.2, B.c.z + 0.3 - i * 0.22))
    fluff(Box((0, B.front - 0.05, B.c.z), (B.s.x * 0.66, 0.1, B.s.z * 0.7)), 'f', mm('main'), 4, 1.3, 0.42, th=0.07)
    for i in range(5):
        p('hip_fur', (0.26, 0.14, 0.22), mm('main'), ((i - 2) * 0.28, B.front - 0.02, B.bot + 0.06))
        p('back_fur', (0.3, 0.14, 0.26), mm('accent'), ((i - 2) * 0.28, B.back + 0.04, B.c.z + 0.1 * (i % 2)))
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        sgn = 1 if hb_.c.x > 0 else -1
        for j in range(3):
            p('arm_fur', (0.16, 0.5, 0.18), mm('accent' if j % 2 else 'main'), (hb_.c.x + sgn * 0.26, 0.05, hb_.c.z + 0.34 + j * 0.24))
        p('wrist_fur', (hb_.s.x + 0.08, hb_.s.y + 0.08, 0.14), mm('main'), (hb_.c.x, 0.0, hb_.top + 0.04))
        cn('shoulder_ice', 0.14, 0.5, mm('glow'), (hb_.c.x + sgn * 0.02, 0.05, hb_.c.z + 1.36), (sgn * 0.45, 0, 1))
        cn('shoulder_ice', 0.1, 0.34, mm('glow'), (hb_.c.x - sgn * 0.2, 0.2, hb_.c.z + 1.36), (sgn * 0.1, 0.4, 1))
        cn('shoulder_ice', 0.09, 0.28, mm('glow2'), (hb_.c.x + sgn * 0.16, -0.14, hb_.c.z + 1.36), (sgn * 0.7, -0.3, 1))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('ankle_fur', (ft.s.x + 0.06, ft.s.y * 0.7, 0.16), mm('main'), (ft.c.x, ft.c.y + 0.12, ft.top + 0.1))
        for j in range(3):
            p('leg_fur', (0.14, 0.2, 0.16), mm('accent' if j % 2 else 'main'), (ft.c.x + (0.26 if ft.c.x > 0 else -0.26), ft.c.y + 0.2, 0.24 + j * 0.1))
        p('toe_claw', (ft.s.x * 0.8, 0.06, 0.05), mm('glow2'), (ft.c.x, ft.front + 0.0, 0.03))
        p('foot_glow', (ft.s.x + 0.03, ft.s.y + 0.03, 0.04), mm('glow'), (ft.c.x, ft.c.y, ft.top + 0.01))
    use('head')
    for i in range(5):
        p('nape_fur', (0.24, 0.14, 0.24), mm('accent' if i % 2 else 'main'), ((i - 2) * 0.24, Hd.back + 0.04, Hd.c.z - 0.2 + 0.08 * (i % 2)))
    for sgn, n in LR:
        p('ear', (0.1, 0.16, 0.2), mm('face'), (sgn * (Hd.s.x / 2 + 0.03), Hd.c.y - 0.1, Hd.c.z + 0.1))
        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.3, Hd.front - 0.08, Hd.c.z - 0.14))
        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.38, Hd.front - 0.08, Hd.c.z - 0.1))
    use('body')
    for i in range(6):
        p('chest_fur', (0.22, 0.1, 0.18), mm('accent'), ((i % 3 - 1) * 0.5, B.front - 0.04, B.top - 0.14 - 0.2 * (i // 3)))
    # rarity 6: frost constellation on the belly, ice crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i, (dx, dz, w) in enumerate(((0, 0.0, 0.2), (0, 0.24, 0.1), (0, -0.24, 0.1), (-0.24, 0, 0.1), (0.24, 0, 0.1), (-0.17, 0.17, 0.07), (0.17, 0.17, 0.07),
                                     (-0.17, -0.17, 0.07), (0.17, -0.17, 0.07))):
        p('belly_flake', (w, 0.04, w), mm('glow' if i < 5 else 'glow2'), (dx, B.front - 0.1, B.c.z - 0.06 + dz), rot=(0, 45, 0))
    for sgn, n in LR:
        on(B, 'k', sgn * 0.26, 0.2, (0.18, 0.18), mm('glow'), th=0.2, name='back_rune', rot=(0, 45, 0))
        on(B, 'k', sgn * 0.1, -0.1, (0.12, 0.12), mm('glow2'), th=0.2, name='back_rune', rot=(0, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for i in range(5):
        ang = (i - 2) * 22
        cn('crown_ice', 0.1 if i != 2 else 0.14, 0.4 if i != 2 else 0.62, mm('glow'), ((i - 2) * 0.2, Hd.c.y + 0.1, Hd.top + 0.02), (math.sin(math.radians(ang)), 0, 1))
        p('crown_gem', (0.08, 0.08, 0.08), mm('glow2'), ((i - 2) * 0.2, Hd.c.y - 0.04, Hd.top + 0.06), rot=(45, 45, 0))
    halo_kit(Hd, 'gold', r=0.62, n=10, dz=1.0, kind='shards')
    use('body')
    orbit_kit((0, 0.05, 1.5), 1.5, 6, 'glow', 'glow2', size=0.15, dz=0.5, shape='shard')
    orbit_kit((0, 0.05, 0.9), 1.8, 8, 'gold', 'glow', size=0.1, name='orbit2', dz=0.2, shape='bubble')
    aura_kit(1.5, 6, motes=12, mote_col='glow', mote_r=1.6, height=2.6, style='rays')
    return finish(a)


ANIMALS = dict(megadeer=megadeer, rhino=rhino, mammoth=mammoth, cavelion=cavelion, icemammoth=icemammoth, yeti=yeti)
