# Biome 16 - Lunar Tundra: snowy plains, glowing ice, silver moon
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 16
GROUND = '#7a94c0'
SKY = '#d0d8f0'
THEME = dict(bits=['#ffffff', '#9ae0ff'], dust='#f0f6ff', glow='#9ae0ff', splash='#e0f4ff', bit_name='снег и иней')
FOOT = dict(moon_owl=1.2, tundra_muskox=1.2, aurora_bear=1.3)
BUSH_NAME = 'сугроб с инеем, полярной ивой, ледяными сосульками и лунными цветами'


def bush():
    B = begin_bush(NN)
    sn = mat('snow', '#ffffff')
    sn2 = mat('snow2', '#e0ecfa')
    sn3 = mat('snow3', '#c8daf0')
    ice = mat('ice', '#9ae0ff', 'smooth')
    ice2 = mat('ice2', '#c8f0ff', 'smooth')
    wil = mat('willow', '#7a9a8a')
    wil2 = mat('willow2', '#a8c8b0')
    twig = mat('twig', '#6a5a5a')
    fl = mat('moonflower', '#f0f0ff')
    glow = mat('moon', '#e8f4ff', 'neon', 2.4)
    aur = mat('aurora', '#7affc8', 'neon', 1.8)
    # snowdrift mounds with frosty rims
    for i, (x, y, w, d, h) in enumerate(((0, 0.3, 5.6, 3.0, 1.4), (-1.2, 0.5, 3.0, 2.2, 2.5), (1.3, 0.5, 2.6, 2.0, 2.1), (-0.1, 0.8, 1.6, 1.2, 3.4))):
        part('big', (x, y, 0.2), 'drift_%d' % i)
        b('drift', (w, d, h), (sn, sn2, sn, sn2)[i], (x, y, h / 2), bev=0.18)
        b('drift_top', (w * 0.66, d * 0.66, 0.24), sn, (x, y, h + 0.08), bev=0.1)
        for j in range(3):
            p('frost', (0.3, 0.06, 0.2), sn3, (x - w * 0.3 + j * w * 0.3, y - d / 2 - 0.01, h * 0.6))
    # icicle fringe on the drifts
    for i, (x, y, z) in enumerate(((-2.2, -0.62, 2.0), (-0.4, -0.62, 2.0), (1.2, -0.52, 1.6), (2.4, -0.52, 1.6))):
        part('small', (x, y, z), 'icicles_%d' % i)
        for j in range(3):
            b('icicle', (0.14, 0.14, 0.5 - 0.12 * j), ice if j % 2 else ice2, (x + (j - 1) * 0.22, y, z - 0.25 + 0.06 * j), bev=0.03)
    # polar willow: low twiggy shrub with silver-green leaves
    k_ = 0
    for (cx, cy, z, n) in ((-2.6, 0.1, 1.0, 5), (2.5, 0.4, 1.2, 5), (-0.4, 0.9, 3.4, 4), (1.0, 1.1, 2.4, 4)):
        part('small', (cx, cy, z), 'willow_%d' % k_)
        for i in range(n):
            lean = (i - (n - 1) / 2) * 18
            h = 1.0 - 0.15 * abs(i - (n - 1) / 2)
            b('twig', (0.08, 0.08, h), twig, (cx + math.sin(math.radians(lean)) * h / 2, cy, z + h / 2), rot=(0, lean, 0), bev=0.02)
            b('catkin', (0.2, 0.16, 0.3), wil if i % 2 else wil2, (cx + math.sin(math.radians(lean)) * h, cy, z + h), rot=(0, lean, 0), bev=0.04)
            p('frost_tip', (0.12, 0.12, 0.06), sn, (cx + math.sin(math.radians(lean)) * (h + 0.16), cy, z + h + 0.16))
        k_ += 1
    # moon flowers with glowing hearts
    for i, (x, y, z) in enumerate(((-1.4, -1.2, 0.3), (0.4, -1.4, 0.3), (1.8, -1.1, 0.3), (-3.0, -0.8, 0.3))):
        part('small', (x, y, z), 'moonflower_%d' % i)
        b('stem', (0.06, 0.06, 0.5), wil, (x, y, z + 0.25), bev=0.01)
        for j in range(4):
            ang = math.radians(j * 90 + 45)
            p('petal', (0.18, 0.18, 0.06), fl, (x + math.cos(ang) * 0.14, y + math.sin(ang) * 0.14, z + 0.52))
        p('heart', (0.12, 0.12, 0.12), glow, (x, y, z + 0.58))
    # ice crystals with aurora glow
    for i, (x, y, s) in enumerate(((2.9, -0.9, 1.0), (-0.2, 1.6, 1.1))):
        part('small', (x, y, 0.2), 'ice_crystal_%d' % i)
        cn('crystal', 0.2 * s, 1.2 * s, ice, (x, y, 0.2), (0.1, 0, 1))
        cn('crystal', 0.14 * s, 0.8 * s, ice2, (x + 0.24 * s, y, 0.2), (0.5, 0, 1))
        p('crystal_core', (0.08 * s, 0.08 * s, 0.5 * s), aur, (x, y, 0.6 * s))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def aurora_weasel(row):
    a = start(row, dict(main='#f6f8ff', belly='#ffffff', dark='#2a2e3a', accent='#c8e0ff', aur='#9ae8d0'), 1.4)
    B, Hd = quad(bw=0.66, bl=1.4, bh=0.52, legh=0.24, lw=0.2, hw=0.86, hd=0.76, hh=0.72, head_up=0.3, toe='dark', head_fwd=0.3)
    mz = muzzle(Hd, (0.36, 0.24, 0.22), -0.26, 'belly', nose=(0.13, 0.06, 0.08))
    cheeks(Hd, 'belly', (0.18, 0.16, 0.22), -0.26, whisk=3, wmat='dark')
    eyes(Hd, 0.38, 0.25, 0.1, iris='#2a2e5a', lash=True, brow='#c8e0ff', tilt=8)
    ears(Hd, 'round', 'main', 'pink', x=0.4, h=0.16, w=0.2, lean=14)
    use('body')
    # long ermine body with subtle aurora-tinted stripes (pattern)
    for i in range(4):
        on(B, 't', 0, -0.36 + i * 0.24, (0.4, 0.06), mm('aur' if i % 2 else 'accent'), name='aurora_stripe')
    grid(B, 'l', 4, 1, mm('accent'), (0.12, 0.1), name='side_dot', span=(0.8, 0.2))
    grid(B, 'r', 4, 1, mm('accent'), (0.12, 0.1), name='side_dot', span=(0.8, 0.2))
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)
    for ft in a.bx['feet']:
        p('pad', (ft.s.x * 0.6, 0.03, 0.05), mm('pink'), (ft.c.x, ft.back + 0.012, 0.05))
    # black-tipped tail (the ermine signature)
    tail_kit('long', 'body', (0, B.back + 0.04, B.c.z + 0.06), 'main', 'dark', n=2, size=0.14, dark='accent')
    return finish(a)


def arctic_hare(row):
    """crouched snowball hare: low wide round body, ears laid flat back along the spine, giant snowshoe hind feet sticking forward"""
    a = start(row, dict(main='#ffffff', belly='#f0f4ff', dark='#3a3e4a', accent='#d0dcf0', tip='#2a2e3a', pad='#ffc8d8'), 1.44)
    B, Hd = quad(bw=1.3, bl=1.2, bh=0.9, legh=0.14, lw=0.24, hw=1.1, hd=0.86, hh=0.8, head_up=0.42, toe='dark', head_fwd=0.2, leg_fl=0.4,
                 rump=True, chest=False)
    use('body')
    b('fluff_top', (1.1, 1.0, 0.3), mm('main'), (0, B.c.y + 0.1, B.top + 0.1), bev=0.12)
    for sgn, n in LR:
        for j in range(3):
            b('side_fluff', (0.2, 0.36, 0.36), mm('accent' if j % 2 else 'main'), (sgn * (B.s.x / 2 + 0.06), B.c.y - 0.3 + j * 0.3, B.c.z - 0.1), bev=0.08)
    mz = muzzle(Hd, (0.4, 0.14, 0.24), -0.3, 'belly', nose=(0.14, 0.06, 0.08), nose_mat='pad', teeth=1)
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.2))
        for j in range(3):
            p('whisker', (0.26, 0.02, 0.02), mm('dark'), (sgn * 0.48, Hd.front - 0.02, Hd.c.z - 0.24 + (j - 1) * 0.05), rot=(0, -sgn * (j - 1) * 10, sgn * 10))
    eyes(Hd, 0.4, 0.26, 0.06, iris='#6a5ad8', lash=True, brow='#d0dcf0', tilt=14, sleepy=0.1)
    # ears laid flat along the back (the silhouette): long slabs pointing backwards
    for sgn, n in LR:
        sg('ear_' + n, 'head', (sgn * 0.24, Hd.c.y + 0.1, Hd.top - 0.06))
        a.ears.append('ear_' + n)
        b('ear', (0.26, 0.9, 0.12), mm('main'), (sgn * 0.26, Hd.c.y + 0.56, Hd.top - 0.02), rot=(8, 0, sgn * 6), bev=0.04)
        p('ear_in', (0.14, 0.7, 0.04), mm('pad'), (sgn * 0.26, Hd.c.y + 0.5, Hd.top + 0.04), rot=(8, 0, sgn * 6))
        b('ear_tip', (0.27, 0.18, 0.13), mm('tip'), (sgn * 0.27, Hd.c.y + 1.02, Hd.top - 0.08), rot=(8, 0, sgn * 6), bev=0.03)
    use('body')
    # huge snowshoe hind feet that poke forward under the body
    for ft in a.bx['feet'][2:]:
        use(ft.seg)
        b('snowshoe', (0.36, 0.9, 0.12), mm('accent'), (ft.c.x + (0.08 if ft.c.x > 0 else -0.08), ft.c.y - 0.5, 0.06), bev=0.04)
        for j in range(3):
            p('shoe_fur', (0.1, 0.1, 0.08), mm('main'), (ft.c.x + (j - 1) * 0.1, ft.c.y - 0.96, 0.08))
            p('shoe_pad', (0.08, 0.08, 0.03), mm('pad'), (ft.c.x + (j - 1) * 0.1, ft.c.y - 0.6, 0.0))
    use('body')
    grid(B, 't', 3, 2, mm('accent'), (0.14, 0.14), name='frost', th=0.32)
    grid(a.bx['rump'], 'k', 3, 2, mm('accent'), (0.14, 0.14), name='rump_frost')
    tail_kit('pom', 'body', a.tail_j, 'main', 'main', size=0.3)
    return finish(a)


def moon_owl(row):
    """moon owl: a perfectly round puffball owl with tiny folded wings, a big heart-shaped face disc, long ear tufts,
    perched on a short floating branch it grips with both feet"""
    zc = 0.9
    a = start(row, dict(main='#c8d0e8', belly='#f4f6ff', dark='#3a3e5a', accent='#ffe14a', disc='#ffffff', branch='#6a5a4a', leaf='#7ab8a8'),
              1.97, hover=2.4, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (1.2, 1.1, 1.2), mm('main'), (0, 0.1, zc), bev=0.42)
    b('belly', (0.8, 0.1, 0.8), mm('belly'), (0, -0.46, zc - 0.15), bev=0.2)
    for j in range(3):
        for k_ in range(3):
            p('chevron', (0.12, 0.04, 0.06), mm('dark'), ((k_ - 1) * 0.2 + (0.1 if j % 2 else 0), -0.52, zc - 0.35 + j * 0.18))
    grid(B, 'k', 3, 3, mm('dark'), (0.08, 0.08), name='back_spot', span=(0.6, 0.6))
    grid(B, 'l', 3, 3, mm('belly'), (0.08, 0.08), name='side_spot', span=(0.6, 0.6))
    grid(B, 'r', 3, 3, mm('belly'), (0.08, 0.08), name='side_spot', span=(0.6, 0.6))
    grid(B, 't', 3, 3, mm('dark'), (0.08, 0.08), name='crown_spot', span=(0.5, 0.5))
    grid(B, 'u', 2, 2, mm('belly'), (0.1, 0.1), name='under_fluff', span=(0.5, 0.5))
    grid(B, 'f', 4, 2, mm('belly'), (0.06, 0.06), name='breast_dot', span=(0.5, 0.2), offset=-0.3)
    for j in range(6):
        p('branch_bark', (0.1, 0.2, 0.2), mm('leaf') if j % 3 == 0 else mm('branch'), (-0.75 + j * 0.3, 0.0, zc - 0.72))
    for k_ in range(10):
        ang = math.radians(k_ * 36)
        p('disc_rim', (0.1, 0.06, 0.1), mm('main'), (math.cos(ang) * 0.5, -0.6, zc + 0.36 + math.sin(ang) * 0.36))
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


def lunar_wolf(row):
    """howling moon wolf: sits upright on its haunches (not standing), long tapered snout, tall crescent mane plates, moon pendant"""
    a = start(row, dict(main='#9aa8d8', belly='#eef2ff', dark='#3a4478', accent='#c8d0f0', mane='#5a68a8', **{'*glow': '#9ae0ff'}), 2.9)
    B, Hd = sit(bw=0.9, bd=0.9, bh=1.2, hw=0.96, hd=0.86, hh=0.8, arm=0.6, lw=0.24, foot_l=0.7, ntoe=3, foot='belly', toe='dark')
    use('head')
    sn = b('snout', (0.4, 0.6, 0.3), mm('main'), (0, Hd.front - 0.24, Hd.c.z - 0.16), bev=0.05)
    p('snout_belly', (0.34, 0.5, 0.06), mm('belly'), (0, Hd.front - 0.24, Hd.c.z - 0.33))
    b('nose', (0.18, 0.1, 0.12), mm('dark'), (0, sn.front - 0.02, sn.top - 0.06), bev=0.02)
    p('mouth', (0.04, 0.03, 0.1), mm('line'), (0, sn.front - 0.008, sn.c.z - 0.06))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.16))
    eyes(Hd, 0.32, 0.25, 0.14, iris='#5a8ad8', glow='#9ae0ff', brow='#3a4478', tilt=-14)
    # tall narrow ears leaning back
    for sgn, n in LR:
        sg('ear_' + n, 'head', (sgn * 0.26, Hd.c.y + 0.1, Hd.top))
        a.ears.append('ear_' + n)
        b('ear', (0.22, 0.14, 0.7), mm('mane'), (sgn * 0.28, Hd.c.y + 0.18, Hd.top + 0.3), rot=(-15, sgn * 8, 0), bev=0.03)
        p('ear_in', (0.1, 0.04, 0.5), mm('accent'), (sgn * 0.28, Hd.c.y + 0.1, Hd.top + 0.28), rot=(-15, sgn * 8, 0))
    use('body')
    # crescent mane: stacked plates curving from the head down the back (the silhouette)
    for i in range(6):
        ang = math.radians(20 + i * 22)
        r = 0.9
        b('mane_plate', (0.7 - 0.06 * i, 0.22, 0.3), mm('mane' if i % 2 else 'dark'), (0, 0.1 + math.sin(ang) * r * 0.6, 0.2 + 1.2 * 0.9 + math.cos(ang) * r * 0.5), rot=(math.degrees(ang) - 20, 0, 0), bev=0.04)
    fluff(Box((0, B.front - 0.07, B.c.z), (B.s.x * 0.72, 0.1, B.s.z * 0.7)), 'f', mm('belly'), 5, 1.0, 0.42)
    grid(B, 'l', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    grid(B, 'r', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    accessory('necklace', Box((0, B.front + 0.3, B.top + 0.02), (B.s.x, B.s.x, 0.2)), '#3a4478', '#ffd84a', z=B.top - 0.04)
    grid(B, 'k', 3, 3, mm('accent'), (0.12, 0.12), name='back_fur')
    use('head')
    grid(Hd, 'l', 2, 2, mm('accent'), (0.1, 0.1), name='cheek_fur')
    grid(Hd, 'r', 2, 2, mm('accent'), (0.1, 0.1), name='cheek_fur')
    for i in range(3):
        p('snout_band', (0.42, 0.06, 0.32), mm('dark'), (0, Hd.front - 0.1 - i * 0.16, Hd.c.z - 0.16))
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        p('ankle_fur', (ft.s.x + 0.06, 0.16, 0.12), mm('accent'), (ft.c.x, ft.c.y + 0.2, 0.18))
    use('body')
    tail_kit('tuft', 'body', (0, a.tail_j[1], 0.3), 'main', 'belly', size=0.24)
    # rarity 4: glowing crescent moon on the chest, glowing ear tips and mane edge, star sparks
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i, (dx, dz, w, h) in enumerate(((-0.1, 0.0, 0.08, 0.36), (0.0, 0.2, 0.18, 0.08), (0.0, -0.2, 0.18, 0.08))):
        p('chest_moon', (w, 0.04, h), mm('glow'), (dx, B.front - 0.13, B.c.z + 0.1 + dz))
    for i in range(3):
        p('mane_glow', (0.5, 0.05, 0.05), mm('glow'), (0, 0.1 + math.sin(math.radians(20 + i * 44)) * 0.54 + 0.12, 0.2 + 1.08 + math.cos(math.radians(20 + i * 44)) * 0.45 + 0.1))
    for sgn, n in LR:
        use('ear_' + n)
        p('ear_glow', (0.1, 0.1, 0.12), mm('glow'), (sgn * 0.28, Hd.c.y + 0.3, Hd.top + 0.66))
    use('body')
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=2.0)
    return finish(a)


def tundra_muskox(row):
    a = start(row, dict(main='#5a4a42', belly='#8a7a6a', dark='#2e2420', accent='#c8b8a0', horn='#f0e8d8', snow='#ffffff',
                        **{'*glow': '#9ae0ff', '*glow2': '#ffe14a'}), 2.9)
    B, Hd = quad(bw=1.4, bl=1.6, bh=1.0, legh=0.36, lw=0.34, hw=1.1, hd=1.0, hh=0.92, head_up=0.24, hump=0.3, hoof='dark', leg_mat='dark',
                 head_mat='belly', head_fwd=0.36)
    mz = muzzle(Hd, (0.52, 0.3, 0.32), -0.28, 'accent', nose=(0.24, 0.1, 0.12))
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.4, Hd.front - 0.012, Hd.c.z - 0.22))
        # the boss horns: a helmet across the forehead curving down and up (the silhouette)
        b('boss', (0.5, 0.5, 0.26), mm('horn'), (sgn * 0.26, Hd.c.y, Hd.top + 0.06), bev=0.07)
        b('horn_down', (0.2, 0.24, 0.5), mm('horn'), (sgn * (Hd.s.x / 2 + 0.06), Hd.c.y - 0.06, Hd.c.z + 0.1), bev=0.05)
        b('horn_up', (0.24, 0.2, 0.18), mm('horn'), (sgn * (Hd.s.x / 2 + 0.2), Hd.c.y - 0.14, Hd.c.z - 0.14), bev=0.04)
        p('horn_tip', (0.12, 0.12, 0.2), mm('dark'), (sgn * (Hd.s.x / 2 + 0.32), Hd.c.y - 0.16, Hd.c.z - 0.04))
    eyes(Hd, 0.28, 0.25, 0.1, iris='#4a2a16', glow='#9ae0ff', brow='#2e2420', tilt=-6, sleepy=0.12)
    use('body')
    # long shaggy skirt with snow on top (pattern) and frost
    for sgn, n in LR:
        for j in range(6):
            b('skirt', (0.14, 0.28, 0.66 - 0.08 * (j % 2)), mm('main' if j % 2 else 'dark'), (sgn * (B.s.x / 2 + 0.07), B.front + 0.14 + j * 0.26, B.bot - 0.08), bev=0.04)
    for j in range(4):
        b('skirt_front', (0.3, 0.12, 0.56), mm('main'), ((j - 1.5) * 0.32, B.front - 0.06, B.bot - 0.06), bev=0.04)
    hp = a.bx['hump']
    b('snow_cap', (1.1, 0.8, 0.16), mm('snow'), (0, hp.c.y + 0.1, hp.top + 0.06), bev=0.06)
    b('snow_cap2', (1.0, 0.6, 0.14), mm('snow'), (0, B.c.y + 0.5, B.top + 0.05), bev=0.06)
    grid(B, 't', 3, 2, mm('accent'), (0.16, 0.16), name='frost', span=(0.8, 0.4))
    grid(B, 'l', 4, 3, mm('dark'), (0.14, 0.14), name='shag', th=0.1, offset=0.06)
    grid(B, 'r', 4, 3, mm('dark'), (0.14, 0.14), name='shag', th=0.1, offset=0.06)
    grid(B, 'k', 4, 3, mm('dark'), (0.16, 0.14), name='rump_shag', th=0.08)
    grid(hp, 't', 4, 2, mm('snow'), (0.14, 0.14), name='snow_lump', th=0.22)
    for sgn, n in LR:
        for j in range(4):
            b('skirt_b', (0.1, 0.22, 0.5), mm('accent'), (sgn * (B.s.x / 2 + 0.14), B.front + 0.26 + j * 0.36, B.bot - 0.02), bev=0.03)
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(3):
            p('leg_hair', (ft.s.x + 0.08, ft.s.y + 0.06, 0.08), mm('main' if j % 2 else 'dark'), (ft.c.x, ft.c.y, 0.2 + j * 0.1))
    use('head')
    grid(Hd, 'l', 3, 2, mm('main'), (0.12, 0.12), name='cheek_shag')
    grid(Hd, 'r', 3, 2, mm('main'), (0.12, 0.12), name='cheek_shag')
    for sgn, n in LR:
        for j in range(2):
            p('horn_ring', (0.22, 0.26, 0.05), mm('accent'), (sgn * (Hd.s.x / 2 + 0.06), Hd.c.y - 0.06, Hd.c.z - 0.04 + j * 0.2))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.16)
    # rarity 5: glowing frost runes on the skirt and boss, orbiting snowflakes, yellow aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(3):
            p('skirt_rune', (0.05, 0.14, 0.14), mm('glow' if j % 2 else 'glow2'), (sgn * (B.s.x / 2 + 0.15), B.front + 0.4 + j * 0.5, B.bot + 0.06), rot=(45, 0, 0))
    for i in range(4):
        p('back_rune', (0.16, 0.16, 0.05), mm('glow'), ((i - 1.5) * 0.3, B.c.y + 0.5, B.top + 0.14), rot=(0, 0, 45))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        p('boss_rune', (0.2, 0.2, 0.05), mm('glow'), (sgn * 0.26, Hd.c.y, Hd.top + 0.2), rot=(0, 0, 45))
    use('body')
    orbit_kit((0, 0.2, 1.7), 1.9, 6, 'glow', 'glow2', size=0.15, dz=0.5, shape='cross')
    aura_kit(1.9, 5, motes=10, mote_col='glow', height=2.4, style='double')
    return finish(a)


def aurora_bear(row):
    """spirit polar bear standing up on its hind legs (biped), long neck, flowing aurora cape on the back, ice claws, star crown"""
    a = start(row, dict(main='#f6f8ff', belly='#e0eafa', dark='#5a6a9a', accent='#c8d8f0', nose='#3a3e5a',
                        **{'*glow': '#7affc8', '*glow2': '#c88aff', '*glow3': '#7ac8ff', '*gold': '#ffd84a'}), 3.78)
    B, Hd = biped(tw=1.2, td=1.0, th=1.5, legh=0.6, lw=0.5, hw=1.0, hd=1.1, hh=0.86, arm_l=1.2, arm_w=0.42, hand=0.5, shoulder=0.0,
                  foot='belly', toe='dark', hand_mat='belly')
    use('head')
    # long bear snout pointing forward, small round ears
    sn = b('snout', (0.5, 0.56, 0.4), mm('main'), (0, Hd.front - 0.24, Hd.c.z - 0.14), bev=0.07)
    b('nose', (0.22, 0.12, 0.14), mm('nose'), (0, sn.front - 0.02, sn.top - 0.08), bev=0.03)
    p('mouth', (0.04, 0.03, 0.12), mm('line'), (0, sn.front - 0.008, sn.c.z - 0.08))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.2))
        b('ear', (0.24, 0.12, 0.22), mm('main'), (sgn * 0.4, Hd.c.y + 0.1, Hd.top + 0.08), bev=0.06)
        p('ear_in', (0.12, 0.04, 0.12), mm('accent'), (sgn * 0.4, Hd.c.y + 0.03, Hd.top + 0.08))
    eyes(Hd, 0.3, 0.24, 0.16, iris='#5a8ad8', glow='#7affc8', lash=True, brow='#5a6a9a', tilt=6)
    use('body')
    fluff(Box((0, B.front - 0.05, B.c.z), (B.s.x * 0.66, 0.1, B.s.z * 0.7)), 'f', mm('belly'), 5, 1.2, 0.42, th=0.07)
    grid(B, 'l', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    grid(B, 'r', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        for j in range(3):
            cn('ice_claw', 0.05, 0.22, mm('glow3'), (hb_.c.x + (j - 1) * 0.14, -hb_.s.y / 2 - 0.02, hb_.c.z - 0.1), (0, -1, -0.5))
        p('wrist_frost', (hb_.s.x + 0.06, hb_.s.y + 0.06, 0.1), mm('accent'), (hb_.c.x, 0.0, hb_.top + 0.04))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('foot_frost', (ft.s.x + 0.04, ft.s.y * 0.8, 0.08), mm('accent'), (ft.c.x, ft.c.y + 0.06, ft.top + 0.1))
    use('body')
    grid(B, 'k', 3, 3, mm('accent'), (0.14, 0.14), name='back_fur')
    grid(B, 't', 3, 2, mm('accent'), (0.14, 0.14), name='shoulder_fur')
    use('head')
    grid(Hd, 'l', 2, 2, mm('accent'), (0.12, 0.12), name='cheek_fur')
    grid(Hd, 'r', 2, 2, mm('accent'), (0.12, 0.12), name='cheek_fur')
    grid(Hd, 't', 2, 2, mm('accent'), (0.12, 0.12), name='head_fur')
    use('body')
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        for j in range(3):
            p('arm_fur', (0.5, 0.5, 0.1), mm('accent' if j % 2 else 'main'), (hb_.c.x, 0.05, hb_.c.z + 0.4 + j * 0.24))
    use('body')
    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.26)
    # rarity 6: aurora cape of glowing ribbons hanging down the back (own segment, flickers), star crown, star orbits, red aura (petals)
    sg('cape', 'body', (0, B.back, B.top))
    a.glow.append('cape')
    for i, m_ in enumerate(('glow', 'glow3', 'glow2', 'glow3', 'glow')):
        x = (i - 2) * 0.24
        for j in range(4):
            p('cape_ribbon', (0.2, 0.08, 0.36), mm(m_), (x + 0.05 * math.sin(j * 1.3 + i), B.back + 0.06 + 0.06 * j, B.top - 0.2 - j * 0.38))
    p('cape_clasp', (0.9, 0.12, 0.12), mm('gold'), (0, B.back + 0.04, B.top + 0.02))
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    p('chest_star', (0.26, 0.06, 0.26), mm('glow'), (0, B.front - 0.13, B.c.z + 0.3), rot=(0, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.top))
    a.glow.append('glow_h')
    on(Hd, 'f', 0, 0.38, (0.16, 0.16), mm('glow'), th=0.035, name='fore_star', rot=(0, 45, 0))
    halo_kit(Hd, 'gold', r=0.6, n=8, dz=0.85, kind='stars')
    use('body')
    orbit_kit((0, 0.05, 1.8), 1.7, 8, 'glow', 'glow2', size=0.14, dz=0.5, shape='star')
    aura_kit(1.7, 6, motes=12, mote_col='glow', mote_r=1.8, height=2.8, style='petals')
    return finish(a)


ANIMALS = dict(aurora_weasel=aurora_weasel, arctic_hare=arctic_hare, moon_owl=moon_owl, lunar_wolf=lunar_wolf, tundra_muskox=tundra_muskox,
               aurora_bear=aurora_bear)
