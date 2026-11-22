# Biome 12 - Coral Depths: underwater world, corals, sunken gates, glowing algae
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 12
GROUND = '#3a7a9a'
SKY = '#7ac8e8'
THEME = dict(bits=['#ff7a9a', '#5ad8a0'], dust='#c8e8f0', glow='#5affe0', splash='#c8f4ff', bit_name='кусочки коралла и пузыри')
FOOT = dict(abyss_leviathan=1.3, reef_lobster=1.2)
BUSH_NAME = 'коралловый куст с водорослями, губками, анемоном и светящимися пузырями'


def bush():
    B = begin_bush(NN)
    c1 = mat('coral', '#ff6a8a')
    c2 = mat('coral2', '#ffa05a')
    c3 = mat('coral3', '#b87af0')
    sp = mat('sponge', '#ffd84a')
    kelp = mat('kelp', '#3ab86a')
    kelp2 = mat('kelp2', '#5ad88a')
    rock = mat('rock', '#5a7a8a')
    rock2 = mat('rock2', '#7a9aa8')
    an = mat('anemone', '#ff8ad0')
    sand = mat('sand', '#e8dcb8')
    bub = mat('bubble', '#c8f8ff', 'neon', 1.4)
    glow = mat('algae', '#5affe0', 'neon', 2.0)
    # reef rock base
    part('big', (0, 0.3, 0.2), 'reef')
    b('reef', (5.0, 2.6, 1.0), rock, (0, 0.3, 0.5), bev=0.16)
    b('reef_top', (3.6, 2.0, 0.6), rock2, (0, 0.4, 1.2), bev=0.12)
    part('big', (0, -1.2, 0.02), 'sand')
    b('sand', (5.6, 1.2, 0.12), sand, (0, -1.1, 0.06), bev=0.04)
    for i, (x, w) in enumerate(((-1.6, 0.5), (0.4, 0.7), (1.9, 0.4))):
        p('sand_ripple', (w, 0.12, 0.03), mat('sand2', '#d0c098'), (x, -1.2, 0.13))
    # branching corals (antler style) in three colours
    for i, (x, y, s, m_) in enumerate(((-1.6, 0.4, 1.3, c1), (0.2, 0.8, 1.6, c3), (1.8, 0.5, 1.2, c2), (-0.6, -0.4, 0.9, c2), (1.0, -0.3, 0.8, c1))):
        part('big' if s > 1.1 else 'small', (x, y, 1.0), 'coral_%d' % i)
        b('trunk', (0.3 * s, 0.3 * s, 0.9 * s), m_, (x, y, 1.0 + 0.45 * s), bev=0.05)
        for j, (dx, dz, h) in enumerate(((-0.4, 0.6, 1.0), (0.4, 0.7, 1.1), (-0.2, 1.1, 0.8), (0.2, 1.2, 0.9), (0.0, 0.9, 1.4))):
            b('branch', (0.18 * s, 0.18 * s, h * s), m_, (x + dx * s, y, 1.0 + (dz + h / 2) * s), rot=(0, dx * 60, 0), bev=0.04)
            p('branch_tip', (0.2 * s, 0.2 * s, 0.1 * s), mat('tip', '#fff0f4'), (x + dx * s * 1.35, y, 1.0 + (dz + h) * s))
    # brain-coral and sponge blocks
    for i, (x, y, z) in enumerate(((-2.4, -0.4, 0.9), (2.5, -0.2, 0.9))):
        part('small', (x, y, z), 'brain_%d' % i)
        b('brain', (0.9, 0.8, 0.6), c3 if i else c2, (x, y, z + 0.3), bev=0.14)
        for j in range(3):
            p('brain_groove', (0.8, 0.06, 0.06), mat('groove', '#5a3a8a'), (x, y - 0.2 + j * 0.2, z + 0.62))
    for i, (x, y, h) in enumerate(((-1.0, 1.2, 1.4), (1.2, 1.3, 1.1))):
        part('small', (x, y, 1.4), 'sponge_%d' % i)
        b('sponge', (0.5, 0.5, h), sp, (x, y, 1.4 + h / 2), bev=0.06)
        p('sponge_hole', (0.3, 0.3, 0.05), mat('hole', '#c89a2a'), (x, y, 1.4 + h + 0.01))
        for j in range(3):
            p('sponge_pore', (0.08, 0.05, 0.08), mat('hole', '#c89a2a'), (x + (j - 1) * 0.14, y - 0.26, 1.6 + j * 0.3))
    # kelp ribbons (tall, they sway the most)
    for i, (x, y, h) in enumerate(((-2.8, 0.6, 3.4), (-2.2, 1.0, 4.0), (2.9, 0.8, 3.6), (2.3, 1.1, 4.2))):
        part('small', (x, y, 0.4), 'kelp_%d' % i)
        for j in range(4):
            b('kelp', (0.26, 0.1, h / 4 + 0.05), kelp if j % 2 else kelp2, (x + 0.12 * math.sin(j * 1.6), y, 0.4 + h / 4 * (j + 0.5)), rot=(0, 10 * math.sin(j * 1.6), 0), bev=0.03)
            p('kelp_float', (0.12, 0.12, 0.12), glow if j == 3 else kelp2, (x + 0.2, y, 0.4 + h / 4 * (j + 0.8)))
    # anemone with glowing tips
    part('small', (0.1, -0.7, 0.1), 'anemone')
    b('anemone_base', (0.8, 0.8, 0.4), an, (0.1, -0.7, 0.3), bev=0.1)
    for j in range(8):
        ang = math.radians(j * 45)
        b('tentacle', (0.1, 0.1, 0.5), an, (0.1 + math.cos(ang) * 0.3, -0.7 + math.sin(ang) * 0.3, 0.75), rot=(-math.sin(ang) * 25, math.cos(ang) * 25, 0), bev=0.03)
        p('tentacle_tip', (0.12, 0.12, 0.1), glow, (0.1 + math.cos(ang) * 0.4, -0.7 + math.sin(ang) * 0.4, 1.0))
    # bubbles rising
    for i, (x, y, z, s) in enumerate(((-0.4, 0.2, 3.4, 0.24), (0.6, 0.4, 3.8, 0.18), (-0.1, 0.5, 4.2, 0.14))):
        part('small', (x, y, z), 'bubble_%d' % i)
        b('bubble', (s, s, s), bub, (x, y, z), bev=s * 0.3)
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def pearl_nautilus(row):
    zc = 0.7
    a = start(row, dict(main='#fff0e6', belly='#ffd8c8', dark='#c86a4a', accent='#ff9a7a', tent='#ffb8a0'), 1.8, hover=2.2, z0=zc)
    # coiled shell body (the silhouette): stacked shrinking blocks forming a spiral, face in the opening
    sg('body', 'root', (0, 0.1, zc))
    B = b('shell', (0.9, 1.1, 1.2), mm('main'), (0, 0.3, zc + 0.05), bev=0.16)
    b('coil', (0.8, 0.7, 0.8), mm('main'), (0, 0.6, zc + 0.5), bev=0.14)
    b('coil_in', (0.6, 0.5, 0.5), mm('belly'), (0, 0.8, zc + 0.2), bev=0.12)
    for i in range(5):
        ang = math.radians(i * 60 + 30)
        p('stripe', (0.94, 0.12, 0.3), mm('dark'), (0, 0.3 + math.cos(ang) * 0.4, zc + 0.05 + math.sin(ang) * 0.45), rot=(-math.degrees(ang), 0, 0))
    for sgn, n in LR:
        p('shell_side', (0.04, 0.6, 0.6), mm('belly'), (sgn * 0.46, 0.4, zc + 0.2))
        p('shell_eye', (0.05, 0.2, 0.2), mm('accent'), (sgn * 0.47, 0.6, zc + 0.4))
    sg('head', 'body', (0, -0.2, zc))
    Hd = b('hood', (0.9, 0.4, 0.8), mm('accent'), (0, -0.24, zc - 0.05))
    b('hood_top', (0.8, 0.5, 0.2), mm('dark'), (0, -0.2, zc + 0.42), bev=0.05)
    p('mouth', (0.24, 0.03, 0.04), mm('line'), (0, Hd.front - 0.012, zc - 0.28))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, zc - 0.2))
    eyes(Hd, 0.42, 0.25, 0.12, iris='#5a3a8a', lash=True, brow='#c86a4a', tilt=8)
    # tentacle bunch: segment so it waves
    sg('tail', 'head', (0, -0.3, zc - 0.4))
    a.tail = ['tail']
    for i in range(6):
        x = (i - 2.5) * 0.14
        b('tentacle', (0.1, 0.1, 0.5 + 0.1 * (i % 2)), mm('tent'), (x, -0.36, zc - 0.66 - 0.05 * (i % 2)), bev=0.03)
        p('tentacle_tip', (0.12, 0.12, 0.08), mm('belly'), (x, -0.36, zc - 0.94 - 0.1 * (i % 2)))
    use('body')
    p('pearl', (0.2, 0.2, 0.2), smooth(a.id + '_pearl', '#ffffff', 0.05), (0, 0.6, zc + 0.92), rot=(45, 45, 0))
    grid(B, 'l', 3, 3, mm('accent'), (0.1, 0.1), name='shell_dot')
    grid(B, 'r', 3, 3, mm('accent'), (0.1, 0.1), name='shell_dot')
    grid(B, 't', 2, 3, mm('dark'), (0.12, 0.12), name='shell_dot')
    for i in range(4):
        p('coil_ring', (0.84, 0.08, 0.08), mm('dark'), (0, 0.4 + i * 0.12, zc + 0.86 - 0.03 * i))
    use('tail')
    for i in range(4):
        p('tentacle_ring', (0.12, 0.12, 0.05), mm('dark'), ((i - 1.5) * 0.28, -0.36, zc - 0.6))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.4, zc - 0.2), Hit=(0, 0.3, zc + 0.6))
    return finish(a)


def reef_ray(row):
    zc = 0.4
    a = start(row, dict(main='#3a8ad8', belly='#f0f8ff', dark='#1a4a8a', accent='#ffd84a', spot='#7ac8ff'), 1.0, hover=1.6, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (1.2, 1.4, 0.5), mm('main'), (0, 0.2, zc))
    b('body_top', (0.9, 1.0, 0.2), mm('main'), (0, 0.2, zc + 0.3), bev=0.06)
    b('belly', (1.0, 1.2, 0.08), mm('belly'), (0, 0.2, zc - 0.28), bev=0.03)
    spots(B, 't', 8, mm('spot'), 0.14, seed=4, name='spot')
    sg('head', 'body', (0, -0.4, zc))
    Hd = b('head', (0.9, 0.3, 0.5), mm('main'), (0, B.front - 0.1, zc + 0.04))
    p('mouth', (0.3, 0.03, 0.04), mm('line'), (0, Hd.front - 0.012, zc - 0.12))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.3, Hd.front - 0.012, zc - 0.06))
        b('horn_lobe', (0.2, 0.36, 0.14), mm('dark'), (sgn * 0.3, Hd.front - 0.12, zc - 0.1), bev=0.04)
    eyes(Hd, 0.5, 0.24, 0.16, iris='#1a3a8a', brow=None)
    # the wide wing-fins (segments wing_L/R): stepped plates
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.6, 0.2, zc))
        a.wings.append('wing_' + n)
        for i in range(3):
            w = 0.5
            d = 1.2 - 0.3 * i
            b('fin', (w, d, 0.16), mm('main'), (sgn * (0.6 + w * (i + 0.5)), 0.2 + 0.1 * i, zc + 0.03 * i), rot=(0, -sgn * 6, 0), bev=0.04)
            p('fin_rim', (w, 0.08, 0.17), mm('dark'), (sgn * (0.6 + w * (i + 0.5)), 0.2 + 0.1 * i - d / 2, zc + 0.03 * i))
            p('fin_spot', (0.14, 0.14, 0.03), mm('spot'), (sgn * (0.6 + w * (i + 0.5)), 0.2 + 0.1 * i, zc + 0.03 * i + 0.09))
    # long thin tail with a stinger-shaped (harmless) tip
    sg('tail', 'body', (0, B.back, zc))
    a.tail = ['tail']
    b('tail', (0.12, 1.2, 0.12), mm('dark'), (0, B.back + 0.6, zc), bev=0.03)
    p('tail_tip', (0.22, 0.22, 0.08), mm('accent'), (0, B.back + 1.24, zc), rot=(0, 0, 45))
    for j in range(3):
        p('tail_band', (0.16, 0.1, 0.16), mm('spot'), (0, B.back + 0.3 + j * 0.3, zc))
    use('body')
    for i in range(4):
        p('back_stripe', (0.08, 0.26, 0.04), mm('dark'), (0, B.c.y - 0.4 + i * 0.3, zc + 0.41))
    grid(B, 'u', 3, 3, mm('spot'), (0.1, 0.1), name='belly_dot', th=0.1)
    grid(B, 't', 2, 4, mm('accent'), (0.08, 0.08), name='back_dot', th=0.1, rot=(0, 0, 45))
    for sgn, n in LR:
        use('wing_' + n)
        for i in range(3):
            p('fin_dot', (0.08, 0.08, 0.03), mm('accent'), (sgn * (0.6 + 0.5 * (i + 0.5)), 0.2 + 0.1 * i + 0.3, zc + 0.03 * i + 0.09))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, Hd.front - 0.1, zc - 0.1), Hit=(0, 0.2, zc + 0.3))
    return finish(a)


def coral_seahorse(row):
    zc = 0.9
    a = start(row, dict(main='#ff9a3a', belly='#ffe0a0', dark='#c85a1a', accent='#ff6a8a', fin='#ffd0f0'), 3.4, hover=2.4, z0=zc)
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (0.7, 0.7, 1.0), mm('main'), (0, 0.1, zc))
    b('belly', (0.5, 0.16, 0.8), mm('belly'), (0, -0.28, zc - 0.04), bev=0.04)
    for j in range(5):
        p('belly_ring', (0.52, 0.18, 0.05), mm('dark'), (0, -0.29, zc - 0.36 + j * 0.18))
        p('back_ridge', (0.16, 0.12, 0.12), mm('dark'), (0, 0.48, zc - 0.36 + j * 0.18))
    sg('head', 'body', (0, 0.0, zc + 0.5))
    Hd = b('head', (0.74, 0.7, 0.7), mm('main'), (0, -0.1, zc + 0.86))
    b('snout', (0.3, 0.5, 0.26), mm('main'), (0, Hd.front - 0.2, zc + 0.74), bev=0.05)
    p('snout_tip', (0.3, 0.06, 0.26), mm('dark'), (0, Hd.front - 0.46, zc + 0.74))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.28, Hd.front - 0.012, zc + 0.7))
    eyes(Hd, 0.4, 0.25, 0.12, iris='#5a2a8a', lash=True, brow='#c85a1a', tilt=10)
    # coronet crown of coral (rarity 3 accessory) + pattern of spots
    use('head')
    for i in range(5):
        ang = math.radians(i * 72)
        b('coronet', (0.12, 0.12, 0.3), mm('accent'), (math.cos(ang) * 0.2, -0.1 + math.sin(ang) * 0.2, Hd.top + 0.14), bev=0.03)
        p('coronet_tip', (0.14, 0.14, 0.08), mm('fin'), (math.cos(ang) * 0.2, -0.1 + math.sin(ang) * 0.2, Hd.top + 0.32))
    spots(Hd, 'lr', 4, mm('belly'), 0.1, seed=2, name='spot')
    use('body')
    spots(B, 'lr', 6, mm('belly'), 0.1, seed=3, name='spot')
    grid(B, 'l', 2, 5, mm('dark'), (0.12, 0.06), name='side_ring')
    grid(B, 'r', 2, 5, mm('dark'), (0.12, 0.06), name='side_ring')
    for j in range(10):
        cn('back_spine', 0.05, 0.16, mm('accent'), (0, 0.52, zc - 0.4 + j * 0.09), (0, 1, 0.3))
    use('head')
    for j in range(3):
        p('snout_band', (0.32, 0.08, 0.28), mm('dark'), (0, Hd.front - 0.06 - j * 0.12, zc + 0.74))
    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_plate', span=(0.6, 0.4))
    for sgn, n in LR:
        p('cheek_fin', (0.06, 0.2, 0.2), mm('fin'), (sgn * 0.4, Hd.c.y + 0.1, zc + 0.8))
    use('body')
    # little back fin (wing segments) that flutters
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.3, 0.3, zc + 0.1))
        a.wings.append('wing_' + n)
        b('fin', (0.1, 0.3, 0.4), mm('fin'), (sgn * 0.38, 0.4, zc + 0.1), rot=(0, sgn * 20, 0), bev=0.03)
        for j in range(3):
            p('fin_ray', (0.11, 0.04, 0.38), mm('accent'), (sgn * 0.39, 0.32 + j * 0.08, zc + 0.1), rot=(0, sgn * 20, 0))
    # curled tail: chain of shrinking cubes spiralling down (2 segments)
    sg('tail', 'body', (0, 0.15, zc - 0.5))
    a.tail = ['tail']
    for i in range(4):
        s = 0.5 - 0.08 * i
        b('tail', (s, s, 0.3), mm('main' if i % 2 == 0 else 'dark'), (0, 0.15 + 0.06 * i, zc - 0.66 - i * 0.26), bev=0.05)
    sg('tail2', 'tail', (0, 0.35, zc - 1.6))
    a.tail.append('tail2')
    for i in range(4):
        ang = math.radians(i * 70)
        s = 0.24 - 0.03 * i
        b('tail_curl', (s, s, s), mm('main' if i % 2 else 'dark'), (0, 0.15 + math.cos(ang) * 0.24, zc - 1.66 + math.sin(ang) * 0.24), bev=0.04)
    use('tail')
    for i in range(4):
        for sgn, n in LR:
            p('tail_ring', (0.05, 0.3 - 0.06 * i, 0.06), mm('belly'), (sgn * (0.25 - 0.04 * i), 0.15 + 0.06 * i, zc - 0.66 - i * 0.26))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc + 0.1), Hit=(0, 0.1, zc + 0.3))
    return finish(a)


def hammer_shark(row):
    zc = 0.6
    a = start(row, dict(main='#7a8aa8', belly='#f0f4ff', dark='#4a5a78', accent='#ffd84a', **{'*glow': '#5affe0'}), 1.9, hover=2.6, z0=zc)
    B, Hd = fish(bw=1.0, bl=1.8, bh=1.0, face_h=0.8, fin=(0.6, 0.5, 0.12), tail=(0.14, 0.6, 1.2), dorsal=0.6, ntail=2, zc=zc)
    use('head')
    # the hammer: a wide flat bar with eyes at both ends (the silhouette)
    b('hammer', (2.0, 0.5, 0.4), mm('main'), (0, Hd.c.y - 0.02, zc + 0.12), bev=0.07)
    b('hammer_under', (1.8, 0.44, 0.08), mm('belly'), (0, Hd.c.y, zc - 0.1), bev=0.03)
    p('mouth', (0.5, 0.04, 0.05), mm('line'), (0, Hd.front - 0.012, zc - 0.26))
    for sgn, n in LR:
        p('tooth', (0.06, 0.04, 0.06), mm('white'), (sgn * 0.12, Hd.front - 0.012, zc - 0.3))
        p('gill', (0.04, 0.06, 0.3), mm('dark'), (sgn * (1.0 / 2 + 0.01), Hd.c.y + 0.24, zc - 0.05))
        p('gill', (0.04, 0.06, 0.26), mm('dark'), (sgn * (1.0 / 2 + 0.01), Hd.c.y + 0.36, zc - 0.05))
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.3, Hd.front - 0.012, zc - 0.16))
    em = Box((0, Hd.c.y - 0.02, zc + 0.12), (2.0, 0.5, 0.4), 'head')
    eyes(em, 0.9, 0.42, 0.0, iris='#1a5a6a', glow='#5affe0', brow=None, w=0.8)
    use('body')
    stripes(B, 'lr', 4, mm('dark'), 0.08, name='stripe', span=0.8)
    grid(B, 'l', 6, 2, mm('belly'), (0.12, 0.1), name='scale', offset=0.06)
    grid(B, 'r', 6, 2, mm('belly'), (0.12, 0.1), name='scale', offset=0.06)
    grid(B, 't', 2, 6, mm('dark'), (0.14, 0.14), name='back_plate')
    grid(B, 'u', 2, 5, mm('belly'), (0.2, 0.18), name='belly_plate', th=0.1)
    for sgn, n in LR:
        use('wing_' + n)
        for j in range(3):
            p('fin_band', (0.6 * 0.3, 0.06, 0.13), mm('dark'), (sgn * (1.0 / 2 + 0.6 * (0.2 + 0.25 * j)), 0.12 + 0.12 * j - 0.1, zc - 0.18))
    use('head')
    for i in range(6):
        p('hammer_dot', (0.1, 0.06, 0.1), mm('dark'), ((i - 2.5) * 0.3, Hd.c.y - 0.28, zc + 0.24))
    for sgn, n in LR:
        for j in range(3):
            p('tooth', (0.06, 0.04, 0.06), mm('white'), (sgn * (0.2 + 0.08 * j), Hd.front - 0.012, zc - 0.3))
    use('body')
    for i in range(4):
        p('belly_line', (0.6, 0.06, 0.03), mm('belly'), (0, B.front + 0.3 + i * 0.36, zc - 0.53))
    # rarity 4: glowing stripes on the dorsal fin and hammer, bubble sparks
    sg('glow', 'body', (0, 0.2, zc + 0.5))
    a.glow.append('glow')
    for i in range(3):
        p('dorsal_glow', (0.14, 0.16, 0.1), mm('glow'), (0, 0.05 + i * 0.36, zc + 0.5 + 0.6 * (0.5 - 0.125 * i) + 0.24))
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', 0, 0.1, (0.6, 0.06), mm('glow'), th=0.035, name='side_glow')
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, zc + 0.3))
    a.glow.append('glow_h')
    for sgn, n in LR:
        p('hammer_tip', (0.12, 0.3, 0.2), mm('glow'), (sgn * 1.02, Hd.c.y, zc + 0.12))
    p('hammer_mark', (0.4, 0.06, 0.05), mm('glow'), (0, Hd.c.y, zc + 0.33))
    use('body')
    aura_kit(1.4, 4, motes=8, mote_col='glow', height=1.2)
    return finish(a)


def abyss_leviathan(row):
    """deep-sea whale leviathan: huge round whale body swimming horizontally, angler lantern on a stalk, baleen grin, glowing freckles"""
    zc = 1.4
    a = start(row, dict(main='#2a3a7a', belly='#8ac8e8', dark='#141c48', accent='#5affe0', fin='#3a5ab8', horn='#e8f8ff',
                        **{'*glow': '#5affe0', '*glow2': '#ffd21a'}), 2.6, hover=3.0, z0=zc)
    B, Hd = fish(bw=1.8, bl=2.4, bh=1.6, face_h=1.4, fin=(0.9, 0.7, 0.14), tail=(0.18, 0.9, 1.6), dorsal=0.0, ntail=2, zc=zc)
    use('head')
    p('grin', (1.4, 0.04, 0.08), mm('dark'), (0, Hd.front - 0.012, zc - 0.36))
    for i in range(8):
        p('baleen', (0.1, 0.04, 0.18), mm('horn'), ((i - 3.5) * 0.17, Hd.front - 0.014, zc - 0.48))
    for sgn, n in LR:
        p('blush', (0.2, 0.03, 0.1), mm('pink'), (sgn * 0.62, Hd.front - 0.012, zc - 0.24))
        for j in range(3):
            p('chin_groove', (0.06, 0.04, 0.3), mm('belly'), (sgn * (0.2 + 0.2 * j), Hd.front - 0.012, zc - 0.66))
    eyes(Hd, 0.3, 0.3, 0.12, iris='#2a8ab0', glow='#5affe0', brow='#141c48', tilt=-4, sleepy=0.12)
    # angler lantern stalk curving forward over the head (the silhouette)
    sg('lure', 'head', (0, Hd.c.y, Hd.top))
    a.ears.append('lure')
    for j in range(4):
        b('stalk', (0.1, 0.1, 0.36), mm('dark'), (0, Hd.c.y - 0.1 * j * j, Hd.top + 0.16 + j * 0.3 - 0.04 * j * j), rot=(-20 * j, 0, 0), bev=0.02)
    b('lantern', (0.36, 0.36, 0.36), mm('glow2'), (0, Hd.c.y - 1.0, Hd.top + 1.0), rot=(45, 45, 0), bev=0.08)
    p('lantern_hi', (0.12, 0.12, 0.12), mm('white'), (-0.08, Hd.c.y - 1.12, Hd.top + 1.1))
    use('body')
    grid(B, 'u', 4, 5, mm('belly'), (0.3, 0.12), name='belly_groove', th=0.1)
    for sgn, n in LR:
        grid(B, 'l' if sgn < 0 else 'r', 5, 3, mm('dark'), (0.14, 0.14), name='side_spot', offset=0.1)
    for i in range(3):
        cn('back_bump', 0.16, 0.24, mm('fin'), (0, B.c.y - 0.5 + i * 0.5, zc + 0.8), (0, 0.3, 1))
    grid(B, 't', 3, 4, mm('fin'), (0.16, 0.16), name='back_spot', th=0.05)
    grid(B, 'k', 3, 3, mm('dark'), (0.14, 0.14), name='tail_spot')
    grid(B, 'f', 3, 2, mm('belly'), (0.12, 0.12), name='chin_spot', span=(0.8, 0.4))
    grid(B, 'u', 2, 2, mm('fin'), (0.2, 0.2), name='belly_spot', th=0.14)
    grid(B, 'k', 2, 3, mm('fin'), (0.12, 0.12), name='tail_band', th=0.08)
    use('head')
    grid(Hd, 't', 3, 1, mm('fin'), (0.16, 0.16), name='head_bump', span=(0.7, 0.2))
    grid(Hd, 'l', 2, 2, mm('dark'), (0.12, 0.12), name='head_spot')
    grid(Hd, 'r', 2, 2, mm('dark'), (0.12, 0.12), name='head_spot')
    use('body')
    # rarity 5: glowing freckle constellations, glowing fin edges, bubble orbit, yellow aura
    sg('glow', 'body', (0, 0.2, zc))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(5):
            p('freckle', (0.05, 0.1, 0.1), mm('glow' if j % 2 else 'glow2'), (sgn * 0.92, 0.2 - 0.8 + j * 0.4, zc + 0.3 - 0.1 * (j % 2)), rot=(45, 0, 0))
        use('wing_' + n)
        p('fin_glow', (0.8, 0.1, 0.06), mm('glow'), (sgn * (0.9 + 0.45), 0.12 + 0.36, zc - 0.28), rot=(0, sgn * 20, 0))
        use('glow')
    use('body')
    orbit_kit((0, 0.2, zc + 0.4), 2.2, 8, 'glow', 'glow2', size=0.16, dz=0.6, shape='bubble')
    aura_kit(2.2, 5, motes=10, mote_col='glow', height=2.6, style='double')
    return finish(a)


def reef_lobster(row):
    a = start(row, dict(main='#e8402a', belly='#ffb08a', dark='#8a1a1a', accent='#ffd84a', shell2='#ff7a4a',
                        **{'*glow': '#5affe0', '*glow2': '#ffd21a', '*gold': '#ffd84a'}), 2.6)
    B, Hd = bug(bw=1.2, bl=1.4, bh=0.8, legh=0.4, hw=1.0, hd=0.5, hh=0.72, nleg=3, leg_w=0.11, leg_span=0.46, claws=0.6, antenna=1.0,
                head_z=0.06, shell='main', under='belly', leg_mat='dark')
    use('head')
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.18))
        cn('rostrum', 0.07, 0.3, mm('dark'), (sgn * 0.1, Hd.front + 0.1, Hd.top - 0.04), (0, -1, 0.4))
    p('mouth', (0.3, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.22))
    eyes(Hd, 0.4, 0.25, 0.1, iris='#2a8a7a', glow='#5affe0', brow='#8a1a1a', tilt=-10)
    use('body')
    # segmented tail fan (the silhouette)
    for j in range(4):
        b('carapace_band', (B.s.x * (0.96 - 0.05 * j), 0.2, 0.14), mm('shell2' if j % 2 else 'dark'), (0, B.front + 0.2 + j * 0.32, B.top + 0.1), bev=0.03)
        for sgn, n in LR:
            p('band_spike', (0.08, 0.08, 0.12), mm('accent'), (sgn * 0.4, B.front + 0.2 + j * 0.32, B.top + 0.2))
    cur = Vector((0, B.back, B.c.z))
    par = 'body'
    a.tail = []
    for i in range(3):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        w = 0.9 - 0.15 * i
        b('tail_seg', (w, 0.4, 0.5 - 0.06 * i), mm('main'), (0, cur.y + 0.2, cur.z - 0.04 * i), bev=0.07)
        p('tail_band', (w + 0.02, 0.1, 0.52 - 0.06 * i), mm('dark'), (0, cur.y + 0.36, cur.z - 0.04 * i))
        cur = Vector((0, cur.y + 0.38, cur.z - 0.04))
        par = nm
    for j in range(5):
        ang = (j - 2) * 22
        b('fan', (0.24, 0.5, 0.1), mm('shell2' if j % 2 else 'main'), (math.sin(math.radians(ang)) * 0.4, cur.y + 0.24, cur.z - 0.1), rot=(0, 0, -ang), bev=0.03)
    grid(B, 'l', 3, 2, mm('accent'), (0.12, 0.12), name='side_dot')
    grid(B, 'r', 3, 2, mm('accent'), (0.12, 0.12), name='side_dot')
    for i, t in enumerate(a.tail):
        use(t)
        for sgn, n in LR:
            p('tail_plate', (0.05, 0.3, 0.3 - 0.06 * i), mm('dark'), (sgn * ((0.9 - 0.15 * i) / 2 + 0.01), B.back + 0.2 + i * 0.38, B.c.z - 0.04 * i))
        p('tail_dot', (0.1, 0.1, 0.05), mm('accent'), (0, B.back + 0.2 + i * 0.38, B.c.z + (0.5 - 0.06 * i) / 2 - 0.04 * i + 0.02))
    use('head')
    grid(Hd, 't', 2, 2, mm('dark'), (0.12, 0.12), name='head_plate')
    grid(Hd, 'f', 4, 1, mm('accent'), (0.08, 0.06), name='lip_dot', span=(0.7, 0.2), offset=0.0)
    use('body')
    grid(B, 't', 2, 2, mm('accent'), (0.1, 0.1), name='back_dot', th=0.25)
    # rarity 6: glowing claw gems and banding, glowing antenna tips, crown, two orbits, red aura
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for j in range(4):
        p('band_glow', (0.3, 0.08, 0.05), mm('glow' if j % 2 else 'glow2'), (0, B.front + 0.2 + j * 0.32, B.top + 0.18))
    for sgn, n in LR:
        on(B, 'l' if sgn < 0 else 'r', 0, 0, (0.18, 0.18), mm('glow'), th=0.035, name='side_gem', rot=(45, 0, 0))
    for arm in a.arms:
        sgn = -1 if arm.endswith('L') else 1
        use(arm)
        cx = sgn * (B.s.x * 0.4 + 0.6 * 0.95)
        p('claw_gem', (0.2, 0.2, 0.08), mm('glow'), (cx, 0.2 - B.s.y / 2 - 0.6 * 0.55, B.c.z + 0.32), rot=(0, 0, 45))
        p('claw_band', (0.5, 0.1, 0.36), mm('gold'), (cx, 0.2 - B.s.y / 2 - 0.1, B.c.z))
        for j in range(3):
            p('claw_stud', (0.1, 0.1, 0.06), mm('accent'), (cx + (j - 1) * 0.14, 0.2 - B.s.y / 2 - 0.5, B.c.z + 0.28))
    for e in a.ears:
        use(e)
        sgn = -1 if e.endswith('L') else 1
        p('antenna_glow', (0.14, 0.14, 0.14), mm('glow2'), (sgn * (Hd.s.x * 0.34 + 1.0 * 0.24), Hd.c.y - 0.2, Hd.c.z + Hd.s.z / 2 + 1.0), rot=(45, 45, 0))
    use(a.tail[-1])
    p('fan_glow', (0.6, 0.12, 0.08), mm('glow'), (0, cur.y + 0.1, cur.z - 0.04))
    use('head')
    halo_kit(Hd, 'gold', r=0.5, n=10, dz=0.8, kind='crown')
    use('body')
    for nm in a.legs:
        use(nm)
        j = a.joint[nm]
        sgn = -1 if nm.endswith('L') else 1
        p('leg_band', (0.08, 0.14, 0.14), mm('accent'), (j.x + sgn * 0.22, j.y, j.z + 0.04))
    use('body')
    orbit_kit((0, 0.2, 1.4), 1.8, 6, 'glow', 'glow2', size=0.14, dz=0.3, shape='gem')
    orbit_kit((0, 0.2, 0.9), 2.1, 8, 'gold', 'glow', size=0.09, name='orbit2', dz=0.15, shape='bubble')
    aura_kit(1.9, 6, motes=12, mote_col='glow', mote_r=2.0, height=1.8, style='petals')
    return finish(a)


ANIMALS = dict(pearl_nautilus=pearl_nautilus, reef_ray=reef_ray, coral_seahorse=coral_seahorse, hammer_shark=hammer_shark,
               abyss_leviathan=abyss_leviathan, reef_lobster=reef_lobster)
