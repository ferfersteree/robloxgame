# Biome 17 - Sky Islands: floating rocks, cloud bridges, wind runes
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 17
GROUND = '#6a9ad0'
SKY = '#e8f6ff'
THEME = dict(bits=['#ffffff', '#ffd0e8'], dust='#f6fbff', glow='#7ae8ff', splash='#e8f8ff', bit_name='облачка и лепестки')
FOOT = dict(cloud_glider=1.8, sky_drake=2.0, sky_stag=1.1)
BUSH_NAME = 'облако-куст на парящем островке с ветряными рунами и цветами'


def bush():
    B = begin_bush(NN)
    cl = mat('cloud', '#ffffff')
    cl2 = mat('cloud2', '#e6f2ff')
    cl3 = mat('cloud3', '#cfe2f6')
    rock = mat('rock', '#a89ab8')
    rock2 = mat('rock2', '#8a7ca0')
    grass = mat('grass', '#8ad86a')
    fl = mat('flower', '#ff9ad8')
    fl2 = mat('flower2', '#ffe06a')
    rune = mat('rune', '#7ae8ff', 'neon', 2.0)
    # floating rock islet under the cloud (the base)
    part('big', (0, 0.3, 0.6), 'islet')
    b('islet', (4.6, 2.6, 0.6), rock, (0, 0.3, 0.9), bev=0.12)
    b('islet_mid', (3.4, 2.0, 0.5), rock2, (0, 0.3, 0.4), bev=0.1)
    b('islet_low', (1.8, 1.2, 0.4), rock, (0, 0.3, 0.0 + 0.2), bev=0.08)
    b('islet_grass', (4.4, 2.4, 0.12), grass, (0, 0.3, 1.24), bev=0.04)
    for i, x in enumerate((-1.4, -0.2, 1.1)):
        p('rune', (0.3, 0.05, 0.3), rune, (x, -1.0, 0.86), rot=(0, 45, 0))
    # cloud puffs (the bush): big cubes, stepped
    for i, (x, y, z, s, m_) in enumerate(((0, 0.4, 2.2, 2.2, cl), (-1.6, 0.2, 1.9, 1.6, cl2), (1.6, 0.3, 1.9, 1.7, cl), (-0.6, 0.8, 3.2, 1.6, cl2),
                                          (0.8, 0.6, 3.1, 1.5, cl), (0.0, 0.5, 3.9, 1.2, cl3), (-2.6, -0.2, 1.6, 1.0, cl3), (2.6, -0.1, 1.6, 1.0, cl2))):
        part('big', (x, y, z - s * 0.3), 'puff_%d' % i)
        b('puff', (s, s * 0.9, s * 0.8), m_, (x, y, z), bev=0.2)
        b('puff_top', (s * 0.6, s * 0.6, s * 0.3), cl, (x + 0.1, y, z + s * 0.48), bev=0.1)
    # flowers poking out, wind swirls
    for i, (x, y, z, m_) in enumerate(((-1.2, -0.7, 1.6, fl), (0.4, -0.8, 1.8, fl2), (1.8, -0.6, 1.5, fl), (-0.2, -0.6, 2.8, fl2))):
        part('small', (x, y, z), 'flower_%d' % i)
        for j in range(4):
            ang = math.radians(j * 90 + 45)
            p('petal', (0.2, 0.1, 0.2), m_, (x + math.cos(ang) * 0.14, y - 0.06, z + math.sin(ang) * 0.14), rot=(0, 45, 0))
        p('core', (0.12, 0.12, 0.12), mat('core', '#ffffff'), (x, y - 0.1, z))
    for i, (x, z) in enumerate(((-2.2, 3.0), (2.4, 3.1))):
        part('small', (x, 0.0, z), 'swirl_%d' % i)
        for j in range(5):
            ang = math.radians(j * 60)
            p('swirl', (0.3, 0.08, 0.08), rune, (x + math.cos(ang) * 0.3 * (1 + j * 0.1), 0.0, z + math.sin(ang) * 0.3 * (1 + j * 0.1)), rot=(0, -math.degrees(ang), 0))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def aether_ribbonfish(row):
    """a long flat ribbon that swims through the air in waves: tiny head, chain of thin plates, frilly fins along both edges"""
    zc = 0.4
    a = start(row, dict(main='#9ad8ff', belly='#ffffff', dark='#4a8ad8', accent='#ffb0e0', fin='#ffe0f6'), 1.0, hover=2.6, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (0.7, 0.6, 0.3), mm('main'), (0, 0.1, zc), bev=0.06)
    sg('head', 'body', (0, -0.2, zc))
    Hd = b('head', (0.8, 0.5, 0.56), mm('main'), (0, -0.4, zc + 0.04))
    p('mouth', (0.14, 0.03, 0.04), mm('line'), (0, Hd.front - 0.012, zc - 0.14))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('pink'), (sgn * 0.26, Hd.front - 0.012, zc - 0.08))
        b('whisker_fin', (0.3, 0.06, 0.14), mm('fin'), (sgn * 0.5, Hd.c.y, zc - 0.08), rot=(0, sgn * 20, 0), bev=0.02)
    for i in range(3):
        b('crest', (0.06, 0.14, 0.3 - 0.06 * i), mm('accent'), (0, Hd.c.y + 0.1 + i * 0.12, Hd.top + 0.1), bev=0.02)
    eyes(Hd, 0.5, 0.24, 0.08, iris='#4a5ad8', lash=True, brow=None)
    use('body')
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.35, 0.1, zc))
        a.wings.append('wing_' + n)
        b('fin', (0.4, 0.4, 0.06), mm('fin'), (sgn * 0.55, 0.1, zc), bev=0.02)
    # the ribbon: 6 segments, each a thin flat plate with edge frills and a stripe
    cur = Vector((0, 0.4, zc))
    par = 'body'
    a.tail = []
    for i in range(6):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        w = 0.66 - 0.07 * i
        b('ribbon', (w, 0.5, 0.12), mm('main' if i % 2 == 0 else 'dark'), (0, cur.y + 0.25, zc), bev=0.03)
        p('ribbon_stripe', (w * 0.4, 0.4, 0.13), mm('belly'), (0, cur.y + 0.25, zc))
        for sgn, n in LR:
            p('frill', (0.1, 0.36, 0.05), mm('accent' if i % 2 else 'fin'), (sgn * (w / 2 + 0.04), cur.y + 0.25, zc))
            p('frill_dot', (0.06, 0.06, 0.06), mm('belly'), (sgn * (w / 2 + 0.1), cur.y + 0.25, zc + 0.02))
        cur = Vector((0, cur.y + 0.48, zc))
        par = nm
    b('tail_tip', (0.5, 0.3, 0.06), mm('accent'), (0, cur.y + 0.1, zc), rot=(0, 0, 45), bev=0.02)
    use('body')
    grid(B, 't', 2, 2, mm('belly'), (0.12, 0.12), name='back_dot')
    grid(B, 'u', 2, 2, mm('accent'), (0.12, 0.12), name='belly_dot')
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(3):
            p('fin_ray', (0.36, 0.05, 0.07), mm('accent'), (sgn * 0.55, 0.1 - 0.12 + j * 0.12, zc))
    use('head')
    grid(Hd, 't', 2, 2, mm('belly'), (0.1, 0.1), name='head_dot')

    def wave(c, n):
        for i, t in enumerate(a.tail):
            for x, r in ((1, 0), (n // 4, 14), (n // 2, 0), (3 * n // 4, -14), (n, 0)):
                k(c, t, max(1, min(n, x + i * 2 if 0 < x < n else x)), rot=(r, 0, 0))
    a.extra_idle.append(wave)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, Hd.front - 0.1, zc - 0.05), Hit=(0, 0.6, zc + 0.1))
    return finish(a)


def cloud_sheep(row):
    """a sheep that is mostly cloud: a huge cumulus of wool puffs, tiny legs and a little dark face peeking out, no horns"""
    a = start(row, dict(main='#ffffff', belly='#eef4ff', dark='#3a3e5a', accent='#d8e6f6', face='#4a4e6a', hoof='#2a2e40'), 1.9)
    B, Hd = quad(bw=0.9, bl=1.0, bh=0.7, legh=0.36, lw=0.14, hw=0.6, hd=0.56, hh=0.6, head_up=0.3, hoof='hoof', leg_mat='face', head_mat='face',
                 head_fwd=0.4, rump=False, chest=False)
    use('head')
    mz = muzzle(Hd, (0.3, 0.12, 0.2), -0.28, 'face', nose=(0.1, 0.05, 0.06), nose_mat='pink')
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.06), mm('pink'), (sgn * 0.2, Hd.front - 0.012, Hd.c.z - 0.12))
        b('ear', (0.24, 0.1, 0.1), mm('face'), (sgn * 0.38, Hd.c.y, Hd.c.z + 0.1), rot=(0, sgn * 20, 0), bev=0.03)
    eyes(Hd, 0.36, 0.25, 0.12, iris='#5a6ad8', lash=True, brow=None)
    b('fringe', (0.5, 0.3, 0.2), mm('main'), (0, Hd.c.y, Hd.top + 0.04), bev=0.08)
    use('body')
    # the cumulus: big wool puffs far bigger than the body (the silhouette)
    for i, (x, y, z, s) in enumerate(((0, 0.2, 0.9, 1.0), (-0.5, 0.1, 0.8, 0.7), (0.5, 0.1, 0.8, 0.7), (0, -0.2, 1.2, 0.7), (0, 0.6, 1.0, 0.7),
                                      (-0.4, 0.5, 1.3, 0.55), (0.4, 0.5, 1.3, 0.55), (0, 0.2, 1.5, 0.6), (-0.6, -0.2, 0.9, 0.45), (0.6, -0.2, 0.9, 0.45))):
        b('wool', (s, s, s * 0.85), mm('main' if i % 3 else 'belly'), (x, y, z), bev=s * 0.22)
        p('wool_shade', (s * 0.6, s * 0.6, 0.05), mm('accent'), (x, y, z - s * 0.44))
    for i in range(6):
        ang = math.radians(i * 60)
        p('wisp', (0.2, 0.2, 0.1), mm('accent'), (math.cos(ang) * 0.9, 0.2 + math.sin(ang) * 0.8, 0.5))
    for ft in a.bx['feet']:
        p('fetlock', (ft.s.x + 0.06, ft.s.y + 0.06, 0.1), mm('main'), (ft.c.x, ft.c.y, 0.32))
    use('head')
    grid(Hd, 'l', 2, 2, mm('dark'), (0.08, 0.08), name='face_dot')
    grid(Hd, 'r', 2, 2, mm('dark'), (0.08, 0.08), name='face_dot')
    use('body')
    for i in range(4):
        p('rain_drop', (0.08, 0.08, 0.12), mm('accent'), ((i - 1.5) * 0.3, 0.2 + (i % 2) * 0.3, 0.3))
    tail_kit('pom', 'body', (0, 0.9, 0.9), 'main', 'main', size=0.2)
    return finish(a)


def island_chameleon(row):
    """chameleon: tall helmet casque, cone eyes, tail rolled into a spiral, gripping two-toe feet; wears a flower and a leaf cape"""
    a = start(row, dict(main='#7ad86a', belly='#e8ffb0', dark='#3a9a4a', accent='#ff9ad8', casque='#5ac8a8', stripe='#ffe06a'), 2.0)
    B, Hd = quad(bw=0.7, bl=1.2, bh=0.8, legh=0.5, lw=0.16, hw=0.8, hd=0.8, hh=0.8, head_up=0.36, toe='dark', head_fwd=0.3, ntoe=2,
                 rump=False, chest=False)
    use('head')
    # casque: stepped helmet rising backwards
    for i in range(3):
        b('casque', (0.7 - 0.15 * i, 0.5 - 0.06 * i, 0.3), mm('casque'), (0, Hd.c.y + 0.1 + i * 0.16, Hd.top + 0.1 + i * 0.22), bev=0.05)
    p('mouth', (0.5, 0.03, 0.04), mm('line'), (0, Hd.front - 0.012, Hd.c.z - 0.22))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.14))
        # turret eye cones on the sides of the head
        b('eye_turret', (0.2, 0.36, 0.36), mm('main'), (sgn * (Hd.s.x / 2 + 0.06), Hd.front + 0.24, Hd.c.z + 0.1), bev=0.07)
        for j in range(3):
            p('turret_ring', (0.22, 0.04, 0.38 - 0.08 * j), mm('dark'), (sgn * (Hd.s.x / 2 + 0.06), Hd.front + 0.08 + 0.1 * j, Hd.c.z + 0.1))
    eyes(Hd, 0.32, 0.3, 0.1, iris='#ff8a2a', brow='#3a9a4a', tilt=8, w=0.7)
    use('body')
    # dorsal crest teeth and colour bands (pattern)
    for j in range(6):
        b('crest', (0.08, 0.14, 0.16), mm('dark'), (0, B.front + 0.1 + j * 0.2, B.top + 0.06), bev=0.02)
    for sgn, n in LR:
        for j in range(4):
            on(B, 'l' if sgn < 0 else 'r', -0.36 + j * 0.24, 0.0, (0.1, 0.7), mm('stripe' if j % 2 else 'dark'), name='band')
    grid(B, 'u', 2, 3, mm('belly'), (0.14, 0.14), name='belly_scale')
    grid(B, 't', 2, 4, mm('stripe'), (0.08, 0.08), name='back_dot', span=(0.5, 0.8))
    grid(B, 'l', 4, 2, mm('belly'), (0.06, 0.06), name='side_dot', span=(0.8, 0.5), offset=0.05)
    grid(B, 'r', 4, 2, mm('belly'), (0.06, 0.06), name='side_dot', span=(0.8, 0.5), offset=0.05)
    use('head')
    grid(Hd, 'l', 2, 2, mm('stripe'), (0.08, 0.08), name='cheek_dot')
    grid(Hd, 'r', 2, 2, mm('stripe'), (0.08, 0.08), name='cheek_dot')
    use('body')
    # accessory: flower on the casque and a little leaf cape
    setm('leaf', '#3fb85a')
    use('head')
    for j in range(5):
        ang = math.radians(j * 72)
        p('flower_petal', (0.14, 0.14, 0.06), mm('accent'), (0.2 + math.cos(ang) * 0.1, Hd.c.y + 0.3 + math.sin(ang) * 0.1, Hd.top + 0.66))
    p('flower_core', (0.1, 0.1, 0.08), mm('stripe'), (0.2, Hd.c.y + 0.3, Hd.top + 0.7))
    use('body')
    b('leaf_cape', (0.8, 0.8, 0.06), mm('leaf'), (0, B.c.y, B.top + 0.1), rot=(0, 0, 45), bev=0.02)
    p('leaf_vein', (0.06, 1.0, 0.07), mm('belly'), (0, B.c.y, B.top + 0.11), rot=(0, 0, 45))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('grip', (ft.s.x + 0.1, 0.1, 0.1), mm('dark'), (ft.c.x, ft.front + 0.04, 0.05))
    use('body')
    # tail rolled into a spiral (the silhouette)
    sg('tail', 'body', (0, B.back, B.c.z))
    a.tail = ['tail']
    for i in range(9):
        ang = math.radians(i * 40)
        r = 0.5 - 0.045 * i
        s = 0.26 - 0.018 * i
        b('tail_coil', (s, s, s), mm('main' if i % 2 else 'dark'), (0, B.back + 0.4 + math.sin(ang) * r, B.c.z - 0.1 + math.cos(ang) * r), bev=0.03)
    return finish(a)


def sky_stag(row):
    """sky stag: slender high-legged stag whose antlers are fans of white feathers, a cloud collar and cloud hooves, wind-rune glow"""
    a = start(row, dict(main='#c8d8f8', belly='#ffffff', dark='#6a7ab8', accent='#e8f0ff', feather='#ffffff', feather2='#ffd0f0',
                        **{'*glow': '#7ae8ff'}), 3.5)
    B, Hd = quad(bw=0.7, bl=1.1, bh=0.6, legh=1.0, lw=0.14, hw=0.8, hd=0.86, hh=0.74, neck=0.5, hoof='accent', head_fwd=0.36)
    mz = muzzle(Hd, (0.34, 0.36, 0.24), -0.26, 'belly', nose=(0.12, 0.06, 0.08), nose_mat='pink')
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.14))
    eyes(Hd, 0.38, 0.25, 0.12, iris='#5a6ad8', lash=True, brow='#6a7ab8', tilt=6)
    ears(Hd, 'long', 'main', 'pink', tip='feather2', x=0.5, h=0.3, w=0.16, lean=60)
    # feather-fan antlers (the silhouette)
    use('head')
    for sgn, n in LR:
        b('antler_base', (0.1, 0.1, 0.3), mm('dark'), (sgn * 0.18, Hd.c.y, Hd.top + 0.12), rot=(0, sgn * 15, 0), bev=0.02)
        for i in range(6):
            ang = math.radians(10 + i * 18)
            ln = 0.7 + 0.1 * (i % 2)
            b('feather', (0.12, 0.06, ln), mm('feather' if i % 2 else 'feather2'),
              (sgn * (0.24 + math.sin(ang) * ln * 0.5), Hd.c.y + 0.04 * i, Hd.top + 0.26 + math.cos(ang) * ln * 0.5), rot=(0, sgn * math.degrees(ang), 0), bev=0.02)
            p('feather_vane', (0.04, 0.07, ln * 0.8), mm('dark'), (sgn * (0.24 + math.sin(ang) * ln * 0.5), Hd.c.y + 0.04 * i - 0.01, Hd.top + 0.26 + math.cos(ang) * ln * 0.5), rot=(0, sgn * math.degrees(ang), 0))
    use('body')
    # cloud collar and cloud hooves
    for i in range(5):
        ang = math.radians(i * 72)
        b('collar_puff', (0.3, 0.3, 0.26), mm('accent'), (math.cos(ang) * 0.36, B.front + 0.1 + math.sin(ang) * 0.24, B.top + 0.1), bev=0.08)
    for ft in a.bx['feet']:
        use(ft.seg)
        b('cloud_hoof', (0.34, 0.36, 0.2), mm('accent'), (ft.c.x, ft.c.y, 0.2), bev=0.08)
    use('body')
    on(a.bx['rump'], 'k', 0, 0.1, (0.5, 0.4), mm('belly'), name='rump_patch')
    grid(B, 'l', 3, 2, mm('accent'), (0.1, 0.1), name='dapple')
    grid(B, 'r', 3, 2, mm('accent'), (0.1, 0.1), name='dapple')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'feather', size=0.16)
    # rarity 4: glowing wind runes on the flanks and feather tips, sparks
    glow_marks(B, ('l', 'r'), 2, 'glow', style='rune', size=0.14)
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        for i in (1, 3, 5):
            ang = math.radians(10 + i * 18)
            p('feather_glow', (0.1, 0.08, 0.12), mm('glow'), (sgn * (0.24 + math.sin(ang) * 0.75), Hd.c.y + 0.04 * i, Hd.top + 0.26 + math.cos(ang) * 0.75))
    on(Hd, 'f', 0, 0.36, (0.12, 0.12), mm('glow'), th=0.035, name='fore_rune', rot=(0, 45, 0))
    use('body')
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=2.4)
    return finish(a)


def cloud_glider(row):
    """sugar-glider shaped sky kite: spreads a flat square membrane between all four legs, big round eyes, fluffy flat tail as a rudder"""
    zc = 0.4
    a = start(row, dict(main='#b8c8f0', belly='#ffffff', dark='#5a6aa8', accent='#ffd0f0', membrane='#e0e8ff', stripe='#6a7ac8',
                        **{'*glow': '#7ae8ff', '*glow2': '#ffe06a'}), 1.2, hover=4.0, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (0.7, 1.1, 0.5), mm('main'), (0, 0.2, zc))
    b('belly', (0.5, 0.9, 0.08), mm('belly'), (0, 0.2, zc - 0.28), bev=0.03)
    p('back_stripe', (0.12, 1.0, 0.04), mm('stripe'), (0, 0.2, zc + 0.27))
    grid(B, 't', 2, 4, mm('accent'), (0.08, 0.08), name='back_dot', th=0.06)
    grid(B, 'u', 2, 3, mm('accent'), (0.1, 0.1), name='belly_dot', th=0.1)
    grid(B, 'l', 4, 2, mm('belly'), (0.08, 0.08), name='side_dot')
    grid(B, 'r', 4, 2, mm('belly'), (0.08, 0.08), name='side_dot')
    sg('head', 'body', (0, -0.3, zc + 0.1))
    Hd = b('head', (0.84, 0.66, 0.66), mm('main'), (0, -0.56, zc + 0.12))
    mz = muzzle(Hd, (0.3, 0.14, 0.2), -0.28, 'belly', nose=(0.12, 0.06, 0.08), nose_mat='pink')
    p('face_stripe', (0.1, 0.03, 0.4), mm('stripe'), (0, Hd.front - 0.012, zc + 0.3))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, zc - 0.04))
        sg('ear_' + n, 'head', (sgn * 0.3, Hd.c.y, Hd.top))
        a.ears.append('ear_' + n)
        b('ear', (0.24, 0.1, 0.3), mm('main'), (sgn * 0.34, Hd.c.y, Hd.top + 0.12), rot=(0, sgn * 20, 0), bev=0.04)
        p('ear_in', (0.12, 0.04, 0.18), mm('accent'), (sgn * 0.34, Hd.c.y - 0.06, Hd.top + 0.12), rot=(0, sgn * 20, 0))
    use('head')
    eyes(Hd, 0.46, 0.25, 0.08, iris='#2a2a4a', lash=True, brow=None, w=0.9)
    use('body')
    # the membrane kite (the silhouette): four limbs stretched to the corners with a flat sheet between
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.35, 0.2, zc))
        a.wings.append('wing_' + n)
        b('membrane', (1.1, 1.3, 0.06), mm('membrane'), (sgn * 0.9, 0.2, zc - 0.04), bev=0.02)
        p('membrane_edge', (1.12, 0.08, 0.08), mm('stripe'), (sgn * 0.9, 0.2 - 0.65, zc - 0.04))
        p('membrane_edge', (1.12, 0.08, 0.08), mm('stripe'), (sgn * 0.9, 0.2 + 0.65, zc - 0.04))
        p('membrane_edge2', (0.08, 1.3, 0.08), mm('stripe'), (sgn * 1.46, 0.2, zc - 0.04))
        for j, y in enumerate((-0.6, 0.6)):
            b('paw', (0.2, 0.2, 0.14), mm('belly'), (sgn * 1.46, 0.2 + y, zc - 0.04), bev=0.04)
            for t in range(3):
                p('toe', (0.05, 0.06, 0.05), mm('dark'), (sgn * 1.46 + (t - 1) * 0.06, 0.2 + y - 0.12, zc - 0.04))
        for j in range(3):
            p('membrane_spot', (0.16, 0.16, 0.07), mm('accent'), (sgn * (0.6 + j * 0.3), 0.2 + (j - 1) * 0.3, zc - 0.03))
        for j in range(5):
            p('membrane_rib', (0.04, 1.2, 0.07), mm('stripe'), (sgn * (0.5 + j * 0.2), 0.2, zc - 0.03))
        for j in range(4):
            p('fringe', (0.2, 0.1, 0.1), mm('belly'), (sgn * (0.5 + j * 0.28), 0.2 + 0.68, zc - 0.04))
            p('fringe', (0.2, 0.1, 0.1), mm('belly'), (sgn * (0.5 + j * 0.28), 0.2 - 0.68, zc - 0.04))
    sg('tail', 'body', (0, 0.75, zc))
    a.tail = ['tail']
    b('tail', (0.5, 1.0, 0.16), mm('main'), (0, 1.25, zc), bev=0.05)
    p('tail_tip', (0.5, 0.3, 0.17), mm('stripe'), (0, 1.62, zc))
    for j in range(3):
        p('tail_fluff', (0.6, 0.1, 0.14), mm('belly'), (0, 0.9 + j * 0.24, zc))
    for j in range(4):
        p('tail_band', (0.52, 0.08, 0.17), mm('stripe'), (0, 0.84 + j * 0.2, zc))
    use('head')
    grid(Hd, 't', 2, 2, mm('stripe'), (0.1, 0.1), name='head_dot')
    for sgn, n in LR:
        for j in range(3):
            p('whisker', (0.22, 0.02, 0.02), mm('dark'), (sgn * 0.5, Hd.front + 0.06, zc - 0.06 + (j - 1) * 0.05), rot=(0, -sgn * (j - 1) * 10, sgn * 10))
    use('tail')
    # rarity 5: glowing star-dots on the membrane (own segment), star orbit, yellow aura
    sg('glow', 'body', (0, 0.2, zc))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(4):
            p('star_dot', (0.1, 0.1, 0.08), mm('glow' if j % 2 else 'glow2'), (sgn * (0.6 + j * 0.24), 0.2 + 0.4 - j * 0.26, zc - 0.0), rot=(0, 0, 45))
    p('back_glow', (0.1, 0.8, 0.05), mm('glow'), (0, 0.2, zc + 0.29))
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(6):
            p('membrane_star', (0.08, 0.08, 0.075), mm('glow2' if j % 2 else 'glow'), (sgn * (0.55 + j * 0.16), 0.2 + 0.5 - j * 0.2, zc - 0.03), rot=(0, 0, 45))
    use('glow')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, Hd.front - 0.1, zc - 0.1), Hit=(0, 0.2, zc + 0.3))
    orbit_kit((0, 0.2, zc), 2.0, 8, 'glow', 'glow2', size=0.12, dz=0.3, shape='star')
    aura_kit(1.6, 5, motes=10, mote_col='glow', height=1.2, style='petals')
    return finish(a)


def sky_drake(row):
    """eastern sky dragon (no wings): long serpent body floating in an S, lion-like mane, deer antlers, long whiskers, pearl in a claw"""
    zc = 1.0
    a = start(row, dict(main='#6ac8f8', belly='#fff6d8', dark='#2a6ab8', accent='#ffd84a', mane='#ffffff', horn='#ffe8a8',
                        **{'*glow': '#7ae8ff', '*glow2': '#ffe06a', '*gold': '#ffd84a'}), 2.4, hover=4.0, z0=zc)
    # head first, body trails behind in a floating S of segments
    sg('body', 'root', (0, 0.4, zc))
    B = b('body', (0.7, 0.9, 0.7), mm('main'), (0, 0.4, zc), bev=0.08)
    p('belly', (0.5, 0.8, 0.06), mm('belly'), (0, 0.4, zc - 0.36))
    sg('head', 'body', (0, -0.05, zc + 0.2))
    Hd = b('head', (0.9, 0.9, 0.7), mm('main'), (0, -0.4, zc + 0.36))
    sn = b('snout', (0.6, 0.5, 0.36), mm('main'), (0, Hd.front - 0.2, zc + 0.24), bev=0.06)
    b('jaw', (0.5, 0.4, 0.14), mm('belly'), (0, Hd.front - 0.16, zc + 0.02), bev=0.03)
    p('nose_pad', (0.3, 0.08, 0.14), mm('dark'), (0, sn.front - 0.02, sn.top - 0.08))
    for sgn, n in LR:
        p('nostril', (0.06, 0.04, 0.04), mm('line'), (sgn * 0.1, sn.front - 0.06, sn.top - 0.08))
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.34, Hd.front - 0.012, zc + 0.2))
        # long whiskers (the silhouette)
        for j in range(3):
            b('whisker', (0.05, 0.36, 0.05), mm('accent'), (sgn * (0.28 + 0.08 * j), sn.front + 0.2 - 0.3 * j, sn.c.z - 0.1 * j), rot=(10 * j, 0, sgn * (25 + 10 * j)), bev=0.01)
        # deer antlers
        b('antler', (0.1, 0.1, 0.6), mm('horn'), (sgn * 0.26, Hd.c.y + 0.1, Hd.top + 0.28), rot=(-20, sgn * 15, 0), bev=0.02)
        b('antler_tine', (0.3, 0.08, 0.08), mm('horn'), (sgn * 0.4, Hd.c.y + 0.16, Hd.top + 0.4), rot=(0, -sgn * 30, 0), bev=0.02)
        b('antler_tine2', (0.08, 0.08, 0.26), mm('horn'), (sgn * 0.3, Hd.c.y + 0.24, Hd.top + 0.62), rot=(-20, sgn * 30, 0), bev=0.02)
    eyes(Hd, 0.36, 0.25, 0.14, iris='#ffb02a', glow='#7ae8ff', brow='#2a6ab8', tilt=-10)
    # flowing mane around the head
    use('head')
    for i in range(8):
        ang = math.radians(-80 + i * 23)
        b('mane', (0.16, 0.2, 0.4), mm('mane'), (math.sin(ang) * 0.5, Hd.back + 0.04, Hd.c.z + math.cos(ang) * 0.4), rot=(0, math.degrees(ang), 0), bev=0.04)
    use('body')
    for sgn, n in LR:
        sg('arm_' + n, 'body', (sgn * 0.35, 0.1, zc - 0.2))
        a.arms.append('arm_' + n)
        b('arm', (0.16, 0.16, 0.36), mm('main'), (sgn * 0.4, 0.06, zc - 0.36), bev=0.03)
        b('claw', (0.2, 0.2, 0.12), mm('accent'), (sgn * 0.4, 0.0, zc - 0.56), bev=0.03)
    # long body chain in an S curve, each with a dorsal mane tuft and belly plates
    cur = Vector((0, 0.85, zc))
    par = 'body'
    a.tail = []
    path = ((0, 0.45, 0.3), (0, 0.45, 0.25), (0, 0.45, -0.1), (0, 0.45, -0.3), (0, 0.4, -0.2), (0, 0.4, 0.1), (0, 0.35, 0.25))
    for i, d in enumerate(path):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        w = 0.6 - 0.05 * i
        c = cur + Vector(d) * 0.5
        b('coil', (w, 0.66, w), mm('main'), tuple(c), rot=(-math.degrees(math.atan2(d[2], d[1])), 0, 0), bev=0.06)
        p('plate', (w * 0.7, 0.5, 0.05), mm('belly'), (0, c.y, c.z - w / 2 - 0.01))
        b('fin', (0.08, 0.3, 0.26), mm('mane'), (0, c.y, c.z + w / 2 + 0.1), bev=0.02)
        for sgn, n in LR:
            p('scale', (0.04, 0.2, 0.2), mm('dark'), (sgn * (w / 2 + 0.01), c.y, c.z))
            p('scale2', (0.04, 0.12, 0.12), mm('accent'), (sgn * (w / 2 + 0.012), c.y + 0.14, c.z + 0.12))
        p('plate_line', (w * 0.72, 0.06, 0.06), mm('dark'), (0, c.y + 0.18, c.z - w / 2 - 0.02))
        if i in (2, 5):
            for sgn, n in LR:
                b('leg', (0.14, 0.14, 0.3), mm('main'), (sgn * (w / 2 + 0.06), c.y, c.z - 0.24), bev=0.03)
                p('leg_claw', (0.18, 0.16, 0.1), mm('accent'), (sgn * (w / 2 + 0.06), c.y - 0.04, c.z - 0.42))
        cur = cur + Vector(d)
        par = nm
    for j in range(4):
        b('tail_tuft', (0.1, 0.3, 0.3), mm('mane'), ((j - 1.5) * 0.12, cur.y + 0.1, cur.z + 0.1), rot=(0, (j - 1.5) * 20, 0), bev=0.02)
    # rarity 6: pearl of wishes in the claw, glowing whisker tips and spine, cloud crown, two orbits, red aura
    use('arm_R')
    b('pearl', (0.3, 0.3, 0.3), mm('glow2'), (0.4, -0.06, zc - 0.76), rot=(45, 45, 0), bev=0.08)
    sg('glow', 'body', (0, 0.4, zc))
    a.glow.append('glow')
    for i in range(5):
        p('spine_glow', (0.1, 0.1, 0.1), mm('glow'), (0, 0.4 + i * 0.45, zc + 0.5 + 0.2 * math.sin(i)))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        p('whisker_glow', (0.08, 0.08, 0.08), mm('glow'), (sgn * 0.44, sn.front - 0.4, sn.c.z - 0.2))
    p('brow_gem', (0.16, 0.05, 0.16), mm('glow2'), (0, Hd.front - 0.02, Hd.top - 0.1), rot=(0, 45, 0))
    for i in range(8):
        p('mane_glow', (0.08, 0.08, 0.08), mm('glow'), (math.sin(math.radians(-80 + i * 23)) * 0.6, Hd.back + 0.1, Hd.c.z + math.cos(math.radians(-80 + i * 23)) * 0.5))
    grid(Hd, 'l', 2, 2, mm('dark'), (0.12, 0.12), name='cheek_scale')
    grid(Hd, 'r', 2, 2, mm('dark'), (0.12, 0.12), name='cheek_scale')
    grid(Hd, 't', 2, 2, mm('accent'), (0.1, 0.1), name='head_dot')
    for sgn, n in LR:
        p('antler_glow', (0.08, 0.08, 0.08), mm('glow2'), (sgn * 0.3, Hd.c.y + 0.3, Hd.top + 0.76))
    halo_kit(Hd, 'gold', r=0.5, n=8, dz=0.9, kind='halo')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.1, zc), Hit=(0, 1.5, zc + 0.5))
    use('body')
    orbit_kit((0, 1.2, zc), 2.2, 6, 'glow', 'glow2', size=0.16, dz=0.5, shape='bubble')
    orbit_kit((0, 1.2, zc), 2.6, 8, 'gold', 'glow', size=0.1, name='orbit2', dz=0.2, shape='leaf')
    aura_kit(1.8, 6, motes=12, mote_col='glow', height=2.0, style='double')
    return finish(a)


ANIMALS = dict(aether_ribbonfish=aether_ribbonfish, cloud_sheep=cloud_sheep, island_chameleon=island_chameleon, sky_stag=sky_stag,
               cloud_glider=cloud_glider, sky_drake=sky_drake)
