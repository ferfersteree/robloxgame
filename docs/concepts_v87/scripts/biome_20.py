# Biome 20 - Rust Gardens: overgrown machine garden, copper leaves, gear flowers, old pipes
from kits import *
import kits, bushkit, moves
from bushkit import begin_bush, part, mat, finish_bush

NN = 20
GROUND = '#7a6a4a'
SKY = '#e8c89a'
THEME = dict(bits=['#c87a3a', '#6ac8a8'], dust='#a88a5a', glow='#ffb04a', splash='#e8d0a0', bit_name='ржавые болтики и медные листья')
FOOT = dict(iron_hound=1.15, clockwork_basilisk=1.2, magnet_tripod=1.05)
BUSH_NAME = 'ржавый куст: старая труба-клумба, медные листья, цветы-шестерёнки и капающий кран'


def bush():
    B = begin_bush(NN)
    rust = mat('rust', '#8a4a2a')
    rust2 = mat('rust2', '#b8683a')
    iron = mat('iron', '#5a5a64')
    copper = mat('copper', '#c87a3a')
    patina = mat('patina', '#5ab8a0')
    leaf = mat('leaf', '#4a8a5a')
    brass = mat('brass', '#e0b84a')
    lamp = mat('lamp', '#ffb04a', 'neon', 2.2)
    # a long half-buried pipe used as a planter
    part('big', (0, 0.3, 0.5), 'pipe')
    b('pipe', (6.2, 1.6, 1.0), rust, (0, 0.3, 0.5), bev=0.12)
    for x in (-2.6, 0.0, 2.6):
        b('pipe_ring', (0.3, 1.8, 1.2), iron, (x, 0.3, 0.55), bev=0.06)
        for z in (0.2, 0.9):
            p('rivet', (0.12, 0.08, 0.12), brass, (x, -0.62, z))
    p('rust_patch', (0.8, 0.06, 0.4), rust2, (-1.3, -0.52, 0.5))
    p('rust_patch', (0.6, 0.06, 0.3), patina, (1.3, -0.52, 0.6))
    # copper-leaf shrub growing out of the pipe
    for i, (x, h, s) in enumerate(((-1.6, 2.6, 1.2), (0.0, 3.2, 1.4), (1.6, 2.7, 1.2), (-0.8, 3.8, 1.0), (0.9, 3.9, 1.0))):
        part('big' if s > 1.1 else 'small', (x, 0.3, h), 'leafs_%d' % i)
        b('stem', (0.2, 0.2, h - 1.0), patina, (x * 0.8, 0.3, 1.0 + (h - 1.0) / 2), bev=0.03)
        b('leaf_ball', (s, s * 0.9, s * 0.8), leaf if i % 2 else copper, (x, 0.3, h), bev=0.15)
        for j in range(4):
            ang = math.radians(j * 90 + 20)
            p('copper_leaf', (0.3, 0.06, 0.2), copper if i % 2 else patina, (x + math.cos(ang) * s * 0.55, 0.3 - s * 0.46, h + math.sin(ang) * s * 0.3), rot=(0, j * 30, 0))
    # gear flowers on stalks
    for i, (x, h) in enumerate(((-2.8, 2.2), (2.8, 2.3), (-0.5, 4.3))):
        part('small', (x, 0.0, h), 'gear_%d' % i)
        b('gear_stalk', (0.12, 0.12, h - 1.0), iron, (x, 0.0, 1.0 + (h - 1.0) / 2), bev=0.02)
        b('gear', (0.7, 0.16, 0.7), brass, (x, 0.0, h), bev=0.04)
        for k_ in range(6):
            ang = math.radians(k_ * 60)
            p('gear_tooth', (0.16, 0.14, 0.16), brass, (x + math.cos(ang) * 0.42, 0.0, h + math.sin(ang) * 0.42), rot=(0, -k_ * 60, 0))
        p('gear_hub', (0.24, 0.2, 0.24), lamp, (x, -0.04, h))
    # dripping tap at the end
    part('small', (3.3, 0.3, 1.2), 'tap')
    b('tap', (0.5, 0.4, 0.4), iron, (3.3, 0.3, 1.2), bev=0.06)
    p('tap_wheel', (0.4, 0.08, 0.4), copper, (3.3, 0.3, 1.5))
    p('drip', (0.1, 0.1, 0.16), lamp, (3.5, 0.3, 0.85))
    return finish_bush(B, has_r6=True)


# ---------------------------------------------------------------- animals
def spring_strider(row):
    """a tin-can robot that hops on ONE pogo spring: round can body, big round eyes, two little propeller arms, one coiled spring leg"""
    a = start(row, dict(main='#c8d0d8', belly='#e8f0f8', dark='#4a5260', accent='#ff8a4a', spring='#e0b84a', rust='#b8683a', blush='#ff9ab4'), 2.55)
    LEG = 0.9
    zb = LEG + 0.55
    sg('body', 'root', (0, 0, zb))
    B = b('can', (1.0, 1.0, 1.1), mm('main'), (0, 0, zb), bev=0.16)
    for z in (-0.42, 0.42):
        p('can_rim', (1.04, 1.04, 0.1), mm('dark'), (0, 0, zb + z))
    b('lid', (0.7, 0.7, 0.12), mm('accent'), (0, 0, zb + 0.6), bev=0.04)
    p('lid_knob', (0.2, 0.2, 0.14), mm('dark'), (0, 0, zb + 0.72))
    grid(B, 'l', 2, 3, mm('rust'), (0.1, 0.1), name='rust_spot', span=(0.6, 0.6))
    grid(B, 'r', 2, 3, mm('rust'), (0.1, 0.1), name='rust_spot', span=(0.6, 0.6))
    grid(B, 'k', 3, 3, mm('dark'), (0.08, 0.08), name='rivet', span=(0.7, 0.7))
    sg('head', 'body', (0, -0.4, zb + 0.2))
    Hd = Box((0, 0.0, zb + 0.1), (1.0, 1.0, 1.0), 'head')
    p('face_plate', (0.8, 0.06, 0.6), mm('belly'), (0, -0.52, zb + 0.1))
    eyes(Hd, 0.32, 0.22, 0.08, iris='#3a8ad8', brow=None)
    p('mouth', (0.2, 0.03, 0.05), mm('dark'), (0, -0.56, zb - 0.12))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.3, -0.56, zb - 0.04))
    # propeller arms
    use('body')
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * 0.5, 0, zb + 0.1))
        a.arms.append(nm)
        b('arm', (0.4, 0.14, 0.14), mm('dark'), (sgn * 0.7, 0, zb + 0.1), bev=0.03)
        p('prop_hub', (0.14, 0.14, 0.14), mm('accent'), (sgn * 0.92, 0, zb + 0.1))
        for k_ in range(3):
            p('prop_blade', (0.06, 0.4, 0.1), mm('accent'), (sgn * 0.96, 0, zb + 0.1), rot=(k_ * 60, 0, 0))
    # the single pogo spring leg
    sg('leg_L', 'body', (0, 0, zb - 0.55))
    a.legs.append('leg_L')
    n_c = 7
    for i in range(n_c):
        z = zb - 0.6 - i * (LEG - 0.2) / n_c
        p('coil', (0.5, 0.5, 0.06), mm('spring'), (0, 0, z), rot=(0, 0, (i % 2) * 45))
        p('coil_bar', (0.08, 0.5, 0.08), mm('spring'), (0.22 * (1 if i % 2 else -1), 0, z - 0.05), rot=(20 if i % 2 else -20, 0, 0))
    b('foot', (0.7, 0.8, 0.2), mm('dark'), (0, -0.05, 0.1), bev=0.06)
    for sgn in (-1, 1):
        for t in (-1, 1):
            p('foot_bolt', (0.08, 0.08, 0.06), mm('spring'), (sgn * 0.26, -0.05 + t * 0.3, 0.22))
    p('foot_pad', (0.6, 0.7, 0.04), mm('accent'), (0, -0.05, 0.02))
    # antenna (ears) and a little exhaust tail
    use('head')
    for sgn, n in LR:
        nm = 'antenna_' + n
        sg(nm, 'head', (sgn * 0.2, 0, zb + 0.66))
        a.ears.append(nm)
        p('antenna', (0.05, 0.05, 0.36), mm('dark'), (sgn * 0.24, 0, zb + 0.84), rot=(0, sgn * 15, 0))
        p('antenna_ball', (0.12, 0.12, 0.12), mm('accent' if sgn > 0 else 'spring'), (sgn * 0.29, 0, zb + 1.04))
    use('body')
    tail_kit('stub', 'body', (0, 0.5, zb - 0.2), 'dark', 'rust', size=0.18)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, 0, zb + 0.3), Chest=(0, -0.55, zb), Hit=(0, 0, zb + 0.2))
    return finish(a)


def copper_weevil(row):
    """copper weevil: a pear-shaped riveted copper body, a very long down-curved snout with elbowed antennae
    sprouting from the middle of the snout, six short legs, patina spots"""
    a = start(row, dict(main='#c87a3a', belly='#e8a868', dark='#5a3020', accent='#5ab8a0', leg='#4a3a30', rivet='#e0b84a'), 1.55)
    sg('body', 'root', (0, 0.3, 0.7))
    B = b('abdomen', (1.2, 1.3, 1.1), mm('main'), (0, 0.5, 0.75), bev=0.2)
    b('abdomen_top', (0.9, 1.0, 0.3), mm('main'), (0, 0.55, 1.36), bev=0.1)
    p('wing_seam', (0.05, 1.2, 0.06), mm('dark'), (0, 0.5, 1.52))
    b('thorax', (0.8, 0.5, 0.7), mm('belly'), (0, -0.25, 0.75), bev=0.12)
    grid(B, 'l', 3, 2, mm('rivet'), (0.08, 0.08), name='rivet', span=(0.7, 0.5))
    grid(B, 'r', 3, 2, mm('rivet'), (0.08, 0.08), name='rivet', span=(0.7, 0.5))
    grid(B, 'k', 2, 2, mm('accent'), (0.16, 0.16), name='patina', span=(0.6, 0.5))
    grid(Box((0, 0.55, 1.36), (0.9, 1.0, 0.3)), 't', 2, 3, mm('accent'), (0.14, 0.14), name='patina_top', span=(0.7, 0.7))
    for i, y in enumerate((-0.3, 0.2, 0.7)):
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * 0.4, y, 0.5))
            a.legs.append(nm)
            b('leg_up', (0.4, 0.12, 0.12), mm('leg'), (sgn * 0.6, y, 0.46), rot=(0, -sgn * 30, 0), bev=0.02)
            b('leg_low', (0.12, 0.12, 0.4), mm('leg'), (sgn * 0.78, y, 0.2), bev=0.02)
            p('foot', (0.16, 0.2, 0.06), mm('dark'), (sgn * 0.78, y - 0.04, 0.03))
    sg('head', 'body', (0, -0.5, 0.8))
    Hd = b('head', (0.66, 0.5, 0.56), mm('main'), (0, -0.7, 0.86), bev=0.12)
    eyes(Hd, 0.32, 0.27, 0.16, iris='#3a2a1a', brow=None, lash=True)
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('belly'), (sgn * 0.24, Hd.front - 0.012, 0.74))
    # the long down-curved snout (the silhouette)
    for i in range(4):
        z = 0.72 - i * 0.12
        y = Hd.front - 0.12 - i * 0.24
        b('snout', (0.2 - 0.02 * i, 0.3, 0.2 - 0.02 * i), mm('belly' if i % 2 else 'main'), (0, y, z), rot=(25 + 8 * i, 0, 0), bev=0.04)
    p('snout_tip', (0.2, 0.12, 0.14), mm('dark'), (0, Hd.front - 1.05, 0.3))
    for sgn in (-1, 1):
        p('mandible', (0.05, 0.1, 0.06), mm('dark'), (sgn * 0.08, Hd.front - 1.1, 0.24))
        p('thorax_spot', (0.04, 0.14, 0.14), mm('accent'), (sgn * 0.41, -0.25, 0.8))
    for sgn, n in LR:
        nm = 'antenna_' + n
        sg(nm, 'head', (sgn * 0.1, Hd.front - 0.45, 0.62))
        a.ears.append(nm)
        b('antenna_a', (0.05, 0.05, 0.36), mm('dark'), (sgn * 0.2, Hd.front - 0.45, 0.78), rot=(0, sgn * 40, 0), bev=0.01)
        b('antenna_b', (0.05, 0.3, 0.05), mm('dark'), (sgn * 0.33, Hd.front - 0.6, 0.94), rot=(-30, 0, 0), bev=0.01)
        p('antenna_club', (0.1, 0.12, 0.1), mm('accent'), (sgn * 0.33, Hd.front - 0.78, 1.02))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.5, 0.7), Hit=(0, 0.5, 1.3))
    a.tail = []
    return finish(a)


def gear_sentinel(row):
    """a little guard robot whose whole torso is a big upright cog wheel; small dome head with a visor and antenna,
    stubby legs, one arm holds a huge wrench"""
    a = start(row, dict(main='#e0b84a', belly='#fff0c8', dark='#4a4040', accent='#3a8ad8', iron='#7a7a84', rust='#b8683a', visor='#3ae0ff',
                        blush='#ff9ab4'), 4.0)
    LEG = 0.7
    R = 0.9
    zc = LEG + R
    sg('body', 'root', (0, 0, zc))
    # the cog torso (the silhouette)
    B = b('cog', (1.5, 0.5, 1.5), mm('main'), (0, 0, zc), bev=0.1)
    for k_ in range(10):
        ang = math.radians(k_ * 36)
        b('cog_tooth', (0.36, 0.44, 0.3), mm('main'), (math.cos(ang) * R, 0, zc + math.sin(ang) * R), rot=(0, -k_ * 36, 0), bev=0.04)
    b('cog_hub', (0.6, 0.6, 0.6), mm('iron'), (0, 0, zc), rot=(0, 45, 0), bev=0.06)
    for k_ in range(4):
        ang = math.radians(k_ * 90 + 45)
        p('cog_hole', (0.22, 0.52, 0.22), mm('dark'), (math.cos(ang) * 0.5, 0, zc + math.sin(ang) * 0.5))
    p('hub_bolt', (0.2, 0.66, 0.2), mm('rust'), (0, 0, zc))
    grid(B, 'f', 3, 1, mm('rust'), (0.1, 0.1), name='rust_spot', span=(0.6, 0.1), offset=-0.45)
    grid(B, 'k', 3, 3, mm('iron'), (0.14, 0.14), name='back_plate', span=(0.7, 0.7))
    for k_ in range(10):
        ang = math.radians(k_ * 36 + 18)
        p('rim_rivet', (0.08, 0.08, 0.08), mm('rust'), (math.cos(ang) * 0.66, -0.26, zc + math.sin(ang) * 0.66))
        ang2 = math.radians(k_ * 36)
        p('tooth_cap', (0.2, 0.46, 0.08), mm('belly'), (math.cos(ang2) * (R + 0.16), 0, zc + math.sin(ang2) * (R + 0.16)), rot=(0, -k_ * 36 + 90, 0))
    p('emblem', (0.3, 0.05, 0.3), mm('accent'), (0, -0.36, zc), rot=(0, 45, 0))
    p('emblem_dot', (0.12, 0.06, 0.12), mm('belly'), (0, -0.38, zc), rot=(0, 45, 0))
    # head
    sg('head', 'body', (0, 0, zc + R))
    Hd = b('head', (0.8, 0.7, 0.6), mm('iron'), (0, 0, zc + R + 0.4), bev=0.14)
    b('dome', (0.6, 0.56, 0.2), mm('iron'), (0, 0, Hd.top + 0.06), bev=0.08)
    p('visor', (0.7, 0.05, 0.22), mm('dark'), (0, Hd.front - 0.01, Hd.c.z + 0.08))
    eyes(Hd, 0.28, 0.2, 0.12, iris='#3ae0ff', glow='#3ae0ff', brow=None)
    p('mouth_grill', (0.3, 0.03, 0.08), mm('dark'), (0, Hd.front - 0.012, Hd.c.z - 0.18))
    for sgn, n in LR:
        p('blush', (0.1, 0.03, 0.05), mm('blush'), (sgn * 0.26, Hd.front - 0.012, Hd.c.z - 0.1))
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.4, 0, Hd.c.z))
        a.ears.append(nm)
        b('ear_bolt', (0.12, 0.3, 0.3), mm('rust'), (sgn * 0.46, 0, Hd.c.z), bev=0.04)
    p('antenna', (0.05, 0.05, 0.4), mm('dark'), (0.2, 0.1, Hd.top + 0.3))
    p('antenna_lamp', (0.14, 0.14, 0.14), mm('accent'), (0.2, 0.1, Hd.top + 0.52))
    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='head_rivet', span=(0.6, 0.6), offset=0.2)
    grid(Hd, 'l', 2, 2, mm('dark'), (0.06, 0.06), name='side_rivet', span=(0.6, 0.5))
    grid(Hd, 'r', 2, 2, mm('dark'), (0.06, 0.06), name='side_rivet', span=(0.6, 0.5))
    # legs
    use('body')
    for sgn, n in LR:
        nm = 'leg_' + n
        sg(nm, 'body', (sgn * 0.35, 0, LEG))
        a.legs.append(nm)
        b('leg', (0.26, 0.26, LEG - 0.1), mm('iron'), (sgn * 0.35, 0, LEG / 2 + 0.05), bev=0.04)
        p('knee', (0.32, 0.32, 0.1), mm('rust'), (sgn * 0.35, 0, LEG / 2 + 0.1))
        for t in range(3):
            p('leg_bolt', (0.06, 0.04, 0.06), mm('main'), (sgn * 0.35, -0.14, 0.2 + t * 0.16))
        b('boot', (0.4, 0.56, 0.2), mm('dark'), (sgn * 0.35, -0.08, 0.1), bev=0.05)
        for t in range(2):
            p('boot_bolt', (0.08, 0.04, 0.08), mm('main'), (sgn * 0.35 + (t - 0.5) * 0.16, -0.37, 0.1))
    # arms; the right one holds a big wrench
    for sgn, n in LR:
        nm = 'arm_' + n
        sg(nm, 'body', (sgn * (R + 0.1), 0, zc + 0.2))
        a.arms.append(nm)
        b('arm', (0.2, 0.2, 0.6), mm('iron'), (sgn * (R + 0.2), 0, zc - 0.1), bev=0.04)
        b('hand', (0.3, 0.3, 0.26), mm('dark'), (sgn * (R + 0.2), 0, zc - 0.48), bev=0.05)
        b('shoulder', (0.34, 0.34, 0.2), mm('main'), (sgn * (R + 0.2), 0, zc + 0.24), bev=0.05)
        for t in range(2):
            p('arm_band', (0.24, 0.24, 0.05), mm('rust'), (sgn * (R + 0.2), 0, zc - 0.05 - t * 0.2))
    use('arm_R')
    b('wrench_handle', (0.16, 0.16, 1.4), mm('iron'), (R + 0.2, -0.1, zc - 0.1), bev=0.03)
    b('wrench_jaw', (0.5, 0.16, 0.2), mm('iron'), (R + 0.2, -0.1, zc + 0.66), bev=0.03)
    for sgn in (-1, 1):
        p('wrench_tooth', (0.12, 0.16, 0.24), mm('iron'), (R + 0.2 + sgn * 0.2, -0.1, zc + 0.82))
    p('wrench_grip', (0.2, 0.2, 0.4), mm('rust'), (R + 0.2, -0.1, zc - 0.55))
    for t in range(4):
        p('wrench_rivet', (0.06, 0.18, 0.06), mm('belly'), (R + 0.2, -0.1, zc - 0.2 + t * 0.2))
    use('body')
    tail_kit('stub', 'body', (0, 0.3, zc - 0.4), 'iron', 'rust', size=0.2)
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc), Hit=(0, 0, zc + 0.3))
    return finish(a)


def magnet_tripod(row):
    """magnet tripod: a round lamp-like body hung between three long stilt legs, a big red-and-silver horseshoe magnet
    on top with bolts floating toward it, one big round eye-lens face"""
    a = start(row, dict(main='#d8d8e0', belly='#f0f0f8', dark='#3a3a48', accent='#e83a3a', silver='#c0c8d8', bolt='#e0b84a', blush='#ff9ab4',
                        **{'*glow': '#3ae0ff', '*glow2': '#ff6a6a'}), 4.8)
    LEG = 2.4
    zb = LEG + 0.2
    sg('body', 'root', (0, 0, zb))
    B = b('body', (1.2, 1.2, 0.9), mm('main'), (0, 0, zb), bev=0.2)
    b('skirt', (1.36, 1.36, 0.2), mm('dark'), (0, 0, zb - 0.4), bev=0.06)
    p('belly_lamp', (0.5, 0.5, 0.1), mm('belly'), (0, 0, zb - 0.52))
    grid(B, 'l', 2, 2, mm('dark'), (0.08, 0.08), name='vent', span=(0.6, 0.5))
    grid(B, 'r', 2, 2, mm('dark'), (0.08, 0.08), name='vent', span=(0.6, 0.5))
    grid(B, 'k', 3, 2, mm('dark'), (0.08, 0.08), name='vent', span=(0.6, 0.5))
    grid(Box((0, 0, zb - 0.4), (1.36, 1.36, 0.2)), 'u', 3, 3, mm('silver'), (0.12, 0.12), name='under_light', span=(0.7, 0.7))
    for k_ in range(8):
        ang = math.radians(k_ * 45 + 22)
        p('top_light', (0.1, 0.1, 0.06), mm('accent' if k_ % 2 else 'bolt'), (math.cos(ang) * 0.4, math.sin(ang) * 0.4, zb + 0.46))
    for k_ in range(8):
        ang = math.radians(k_ * 45)
        p('skirt_bolt', (0.08, 0.08, 0.08), mm('bolt'), (math.cos(ang) * 0.69, math.sin(ang) * 0.69, zb - 0.4))
    sg('head', 'body', (0, -0.3, zb + 0.1))
    Hd = Box((0, 0, zb + 0.1), (1.2, 1.2, 0.9), 'head')
    eyes(Hd, 0.4, 0.2, 0.04, iris='#3ae0ff', glow='#3ae0ff', brow='#3a3a48')
    p('mouth', (0.2, 0.03, 0.05), mm('dark'), (0, -0.612, zb - 0.2))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.36, -0.612, zb - 0.12))
    # three long legs (front left, front right, back)
    use('body')
    for nm, ang in (('leg_L', 210), ('leg_R', 330), ('leg_B', 90)):
        r = math.radians(ang)
        hx, hy = math.cos(r) * 0.6, math.sin(r) * 0.6
        fx, fy = math.cos(r) * 1.4, math.sin(r) * 1.4
        sg(nm, 'body', (hx, hy, zb - 0.3))
        a.legs.append(nm)
        p('hip', (0.26, 0.26, 0.26), mm('dark'), (hx, hy, zb - 0.3))
        mx, my = (hx + fx) / 2, (hy + fy) / 2
        ln = math.sqrt((fx - hx) ** 2 + (fy - hy) ** 2 + (zb - 0.3) ** 2)
        tilt = math.degrees(math.atan2(math.sqrt((fx - hx) ** 2 + (fy - hy) ** 2), zb - 0.3))
        b('stilt', (0.14, 0.14, ln), mm('silver'), (mx, my, (zb - 0.3) / 2), rot=(0, -tilt, ang), bev=0.03)
        for t in range(5):
            q = 0.15 + t * 0.17
            p('stilt_band', (0.2, 0.2, 0.06), mm('accent' if t % 2 else 'dark'), (hx + (fx - hx) * q, hy + (fy - hy) * q, (zb - 0.3) * (1 - q)), rot=(0, -tilt, ang))
        b('foot', (0.4, 0.4, 0.14), mm('dark'), (fx, fy, 0.07), bev=0.04)
        p('foot_magnet', (0.3, 0.3, 0.06), mm('accent'), (fx, fy, 0.16))
        for t in range(3):
            ta = r + math.radians((t - 1) * 40)
            p('foot_claw', (0.1, 0.1, 0.08), mm('silver'), (fx + math.cos(ta) * 0.24, fy + math.sin(ta) * 0.24, 0.04))
    # horseshoe magnet on top (the silhouette)
    sg('magnet', 'body', (0, 0, zb + 0.45))
    a.ears.append('magnet')
    for sgn in (-1, 1):
        b('magnet_arm', (0.3, 0.34, 0.8), mm('accent'), (sgn * 0.45, 0, zb + 0.95), bev=0.05)
        b('magnet_tip', (0.32, 0.36, 0.24), mm('silver'), (sgn * 0.45, 0, zb + 1.45), bev=0.04)
    b('magnet_base', (1.2, 0.34, 0.3), mm('accent'), (0, 0, zb + 0.6), bev=0.05)
    for sgn in (-1, 1):
        for t in range(2):
            p('magnet_stripe', (0.32, 0.36, 0.05), mm('belly'), (sgn * 0.45, 0, zb + 0.85 + t * 0.25))
    # rarity 4: floating bolts (glow segment), spark between the magnet tips
    sg('glow', 'magnet', (0, 0, zb + 1.6))
    a.glow.append('glow')
    p('spark', (0.5, 0.08, 0.08), mm('glow'), (0, 0, zb + 1.55))
    p('spark2', (0.08, 0.08, 0.2), mm('glow'), (0.12, 0, zb + 1.6), rot=(0, 30, 0))
    for i in range(8):
        ang = math.radians(i * 45)
        x, y, z = math.cos(ang) * 0.5, math.sin(ang) * 0.3, zb + 1.85 + 0.15 * (i % 2)
        p('float_bolt', (0.08, 0.08, 0.2), mm('bolt'), (x, y, z), rot=(30 * i, 0, 45))
        p('bolt_head', (0.14, 0.14, 0.06), mm('glow2'), (x, y, z + 0.12), rot=(30 * i, 0, 45))
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=(0, -0.3, zb + 0.1), Chest=(0, -0.62, zb), Hit=(0, 0, zb + 0.4))
    a.tail = []
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=3.2)
    return finish(a)


def iron_hound(row):
    """iron hound built like a tiny steam engine: barrel boiler body with bands, a smoke stack on its back,
    wheels instead of paws, floppy riveted plate ears, cow-catcher grill under the chin"""
    a = start(row, dict(main='#4a4a58', belly='#8a8a98', dark='#22222a', accent='#e0b84a', red='#c83a3a', wheel='#2e2e36', blush='#ff9ab4',
                        **{'*glow': '#ffb04a', '*glow2': '#ff6a3a', '*steam': '#ffffff'}), 3.61)
    B, Hd = quad(bw=1.1, bl=2.0, bh=1.0, legh=0.6, lw=0.28, hw=1.0, hd=0.9, hh=0.86, head_up=0.5, toe='accent', head_fwd=0.3,
                 rump=False, chest=False, ntoe=0)
    use('body')
    # boiler bands and front boiler door
    for i in range(4):
        p('band', (B.s.x + 0.06, 0.1, B.s.z + 0.06), mm('accent'), (0, B.c.y - 0.75 + i * 0.5, B.c.z))
    grid(B, 'l', 4, 2, mm('accent'), (0.08, 0.08), name='rivet', span=(0.8, 0.6))
    grid(B, 'r', 4, 2, mm('accent'), (0.08, 0.08), name='rivet', span=(0.8, 0.6))
    grid(B, 'k', 2, 2, mm('belly'), (0.12, 0.12), name='back_plate', span=(0.6, 0.6))
    p('red_stripe_L', (0.04, B.s.y * 0.9, 0.12), mm('red'), (-B.s.x / 2 - 0.02, B.c.y, B.c.z - 0.2))
    p('red_stripe_R', (0.04, B.s.y * 0.9, 0.12), mm('red'), (B.s.x / 2 + 0.02, B.c.y, B.c.z - 0.2))
    # smoke stack on the back (the silhouette)
    b('stack', (0.36, 0.36, 0.7), mm('dark'), (0, B.c.y - 0.4, B.top + 0.35), bev=0.04)
    b('stack_top', (0.56, 0.56, 0.18), mm('dark'), (0, B.c.y - 0.4, B.top + 0.76), bev=0.04)
    p('stack_band', (0.4, 0.4, 0.06), mm('accent'), (0, B.c.y - 0.4, B.top + 0.4))
    b('dome', (0.4, 0.4, 0.3), mm('accent'), (0, B.c.y + 0.4, B.top + 0.15), bev=0.1)
    grid(B, 'u', 2, 3, mm('dark'), (0.12, 0.12), name='belly_plate', span=(0.6, 0.7))
    for k_ in range(4):
        ang = math.radians(k_ * 90 + 45)
        p('stack_bolt', (0.06, 0.06, 0.06), mm('accent'), (math.cos(ang) * 0.2, B.c.y - 0.4 + math.sin(ang) * 0.2, B.top + 0.7))
    p('collar', (B.s.x + 0.1, 0.16, B.s.z + 0.1), mm('red'), (0, B.front + 0.06, B.c.z))
    for k_ in range(4):
        p('collar_stud', (0.08, 0.06, 0.08), mm('accent'), ((k_ - 1.5) * 0.24, B.front - 0.03, B.c.z - B.s.z / 2 - 0.02))
    # wheels instead of paws
    for ft in a.bx['feet']:
        use(ft.seg)
        sgn = 1 if ft.c.x > 0 else -1
        b('wheel', (0.14, 0.56, 0.56), mm('wheel'), (ft.c.x + sgn * 0.06, ft.c.y, 0.28), bev=0.04)
        p('wheel_hub', (0.16, 0.2, 0.2), mm('accent'), (ft.c.x + sgn * 0.08, ft.c.y, 0.28))
        for k_ in range(6):
            p('spoke', (0.15, 0.06, 0.46), mm('belly'), (ft.c.x + sgn * 0.065, ft.c.y, 0.28), rot=(k_ * 30, 0, 0))
        p('rim', (0.16, 0.6, 0.06), mm('red'), (ft.c.x + sgn * 0.06, ft.c.y, 0.02))
    # head: floppy plate ears, grill under the chin, little lamp nose
    use('head')
    mz = muzzle(Hd, (0.5, 0.3, 0.3), -0.24, 'belly', nose=(0.18, 0.1, 0.12), nose_mat='dark')
    for sgn, n in LR:
        nm = 'ear_' + n
        sg(nm, 'head', (sgn * 0.45, Hd.c.y, Hd.top - 0.1))
        a.ears.append(nm)
        b('ear', (0.14, 0.4, 0.6), mm('main'), (sgn * 0.56, Hd.c.y, Hd.top - 0.36), rot=(0, sgn * -12, 0), bev=0.04)
        for t in range(2):
            p('ear_rivet', (0.04, 0.06, 0.06), mm('accent'), (sgn * 0.64, Hd.c.y + (t - 0.5) * 0.2, Hd.top - 0.2))
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.3, Hd.front - 0.012, Hd.c.z - 0.14))
    eyes(Hd, 0.3, 0.24, 0.14, iris='#ffb04a', glow='#ffb04a', brow='#22222a')
    for i in range(5):
        p('grill_bar', (0.06, 0.24, 0.3), mm('red'), ((i - 2) * 0.14, Hd.front - 0.06, Hd.bot - 0.12), rot=(-30, 0, 0))
    p('grill_top', (0.7, 0.08, 0.08), mm('accent'), (0, Hd.front - 0.08, Hd.bot))
    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='head_rivet', span=(0.6, 0.6))
    grid(Hd, 'l', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_plate', span=(0.6, 0.5))
    grid(Hd, 'r', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_plate', span=(0.6, 0.5))
    use('body')
    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.24)
    # rarity 5: firebox glow, headlamp, steam puffs over the stack (own segment), orbit of gears, yellow aura
    sg('glow', 'body', (0, B.c.y, B.c.z))
    a.glow.append('glow')
    for sgn in (-1, 1):
        for j in range(3):
            p('firebox', (0.04, 0.12, 0.12), mm('glow2'), (sgn * (B.s.x / 2 + 0.03), B.c.y + 0.3 + j * 0.2, B.c.z - 0.2))
    p('headlamp', (0.26, 0.1, 0.26), mm('glow'), (0, Hd.front - 0.02, Hd.top + 0.08), rot=(0, 45, 0))
    for i in range(6):
        b('steam', (0.2 + 0.06 * i, 0.2 + 0.06 * i, 0.16), mm('steam'), (0.1 * (i % 2), B.c.y - 0.4 - 0.08 * i, B.top + 1.0 + i * 0.22), bev=0.04)
    a.bx.update(body=B, head=Hd)
    orbit_kit((0, B.c.y, B.c.z + 0.3), 2.0, 6, 'accent', 'glow', size=0.16, dz=0.4, shape='gear')
    aura_kit(1.8, 5, motes=10, mote_col='glow', height=2.2, style='ring')
    return finish(a)


def clockwork_basilisk(row):
    """clockwork basilisk: a serpent rising in an S made of stacked clock discs (each one a little clock face with hands),
    a crowned lizard head with a pendulum beard, a big wind-up key in its back"""
    a = start(row, dict(main='#3a6a5a', belly='#f0e8d0', dark='#1e2a24', accent='#e0b84a', hand='#3a2a1a', red='#c83a3a', blush='#ff9ab4',
                        **{'*glow': '#ffd84a', '*glow2': '#6affc8', '*ruby': '#ff3a5a'}), 4.95)
    sg('body', 'root', (0, 0.4, 0.5))
    # coiled base of three flat discs on the ground
    B = None
    for i, (x, y, s) in enumerate(((0, 0.6, 1.2), (0.6, 1.1, 1.0), (-0.5, 1.3, 0.9))):
        bx = b('base_disc', (s, s, 0.5), mm('main'), (x, y, 0.25), bev=0.1)
        if i == 0:
            B = bx
        p('base_face', (s * 0.7, s * 0.7, 0.06), mm('belly'), (x, y, 0.52))
        p('base_hand', (0.06, s * 0.3, 0.07), mm('hand'), (x, y - s * 0.12, 0.55))
    # the rising S neck: chain of clock discs facing forward
    path = ((0, 0.3, 0.9), (0.25, 0.15, 1.5), (0.35, 0.0, 2.1), (0.2, -0.1, 2.7), (-0.1, -0.15, 3.25))
    par = 'body'
    a.neck = []
    for i, (x, y, z) in enumerate(path):
        nm = 'neck%d' % (i + 1)
        sg(nm, par, (x, y + 0.1, z - 0.3))
        a.neck.append(nm)
        s = 0.9 - 0.06 * i
        b('clock_disc', (s, 0.36, s), mm('main'), (x, y, z), rot=(0, 45 * (i % 2), 0), bev=0.08)
        p('clock_face', (s * 0.72, 0.05, s * 0.72), mm('belly'), (x, y - 0.19, z), rot=(0, 45 * (i % 2), 0))
        p('hand_h', (0.05, 0.03, s * 0.24), mm('hand'), (x, y - 0.22, z + s * 0.1))
        p('hand_m', (s * 0.3, 0.03, 0.04), mm('hand'), (x + s * 0.13, y - 0.22, z))
        p('pin', (0.06, 0.04, 0.06), mm('red'), (x, y - 0.24, z))
        for k_ in range(4):
            ang = math.radians(k_ * 90)
            p('tick', (0.05, 0.03, 0.05), mm('hand'), (x + math.cos(ang) * s * 0.3, y - 0.22, z + math.sin(ang) * s * 0.3))
        for sgn in (-1, 1):
            p('side_gear', (0.06, 0.24, 0.24), mm('accent'), (x + sgn * (s / 2 + 0.03), y, z), rot=(45, 0, 0))
        par = nm
    # head
    hx, hy, hz = -0.15, -0.35, 3.85
    sg('head', par, (hx, hy + 0.2, hz - 0.3))
    Hd = b('head', (0.9, 0.8, 0.66), mm('main'), (hx, hy, hz), bev=0.12)
    mz = muzzle(Hd, (0.56, 0.36, 0.3), -0.2, 'belly', nose=None, mouth=True)
    for sgn, n in LR:
        p('nostril', (0.06, 0.03, 0.04), mm('dark'), (hx + sgn * 0.12, Hd.front - 0.37, hz - 0.08))
        p('blush', (0.12, 0.03, 0.06), mm('blush'), (hx + sgn * 0.34, Hd.front - 0.012, hz - 0.12))
        nm = 'frill_' + n
        sg(nm, 'head', (hx + sgn * 0.45, hy + 0.2, hz))
        a.ears.append(nm)
        for j in range(3):
            b('frill', (0.08, 0.3, 0.4 - 0.08 * j), mm('accent'), (hx + sgn * (0.5 + 0.08 * j), hy + 0.2 + 0.08 * j, hz + 0.05), rot=(0, sgn * 20, 0), bev=0.02)
    eyes(Hd, 0.32, 0.24, 0.18, iris='#6affc8', glow='#6affc8', brow='#1e2a24', tilt=6)
    # pendulum beard
    sg('beard', 'head', (hx, hy - 0.1, Hd.bot))
    a.extra_idle.append(lambda c, n: [k(c, 'beard', x, rot=(0, r, 0)) for x, r in ((1, 0), (n // 4, 18), (3 * n // 4, -18), (n, 0))])
    p('pendulum_rod', (0.04, 0.04, 0.4), mm('accent'), (hx, hy - 0.1, Hd.bot - 0.2))
    b('pendulum_bob', (0.24, 0.1, 0.24), mm('accent'), (hx, hy - 0.1, Hd.bot - 0.44), rot=(0, 45, 0), bev=0.03)
    use('head')
    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_scale', span=(0.6, 0.6))
    # the tail chain behind
    use('body')
    par = 'body'
    a.tail = []
    for i in range(3):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        y0 = 1.7 + i * 0.5
        sg(nm, par, (0, y0 - 0.2, 0.3))
        a.tail.append(nm)
        s = 0.6 - 0.12 * i
        b('tail_disc', (s, 0.4, s), mm('main'), (0, y0, 0.3), bev=0.06)
        p('tail_gear', (s + 0.06, 0.1, s * 0.3), mm('accent'), (0, y0, 0.3))
        par = nm
    p('tail_tip', (0.2, 0.3, 0.2), mm('accent'), (0, 2.95, 0.3), rot=(0, 45, 0))
    # wind-up key on the back of the third disc (own segment so it can spin)
    sg('key', 'neck3', (0.35, 0.3, 2.1))
    a.extra_idle.append(lambda c, n: [k(c, 'key', x, rot=(0, r, 0)) for x, r in ((1, 0), (n, 360))])
    p('key_shaft', (0.1, 0.4, 0.1), mm('accent'), (0.35, 0.36, 2.1))
    for sgn in (-1, 1):
        b('key_bow', (0.36, 0.08, 0.36), mm('accent'), (0.35 + sgn * 0.24, 0.58, 2.1), rot=(0, 45, 0), bev=0.03)
        p('key_hole', (0.14, 0.1, 0.14), mm('dark'), (0.35 + sgn * 0.24, 0.58, 2.1), rot=(0, 45, 0))
    # rarity 6: glowing numerals ring on the base, ruby eyes on discs, crown, two orbits, red aura
    sg('glow', 'body', (0, 0.6, 0.6))
    a.glow.append('glow')
    for k_ in range(12):
        ang = math.radians(k_ * 30)
        p('numeral', (0.08, 0.08, 0.06), mm('glow' if k_ % 3 else 'ruby'), (math.cos(ang) * 0.42, 0.6 + math.sin(ang) * 0.42, 0.56))
    for i, (x, y, z) in enumerate(path):
        use('neck%d' % (i + 1))
        p('disc_gem', (0.1, 0.06, 0.1), mm('glow2'), (x, y - 0.25, z + (0.9 - 0.06 * i) * 0.3), rot=(0, 45, 0))
    halo_kit(Hd, 'accent', r=0.42, n=6, dz=0.65, kind='gears')
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(path[2][0], path[2][1] - 0.3, path[2][2]), Hit=(0, 0.3, 1.5))
    orbit_kit((0, 0.4, 2.4), 2.0, 6, 'glow', 'accent', size=0.14, dz=0.5, shape='gear')
    orbit_kit((0, 0.4, 1.0), 2.4, 8, 'glow2', 'glow', size=0.1, name='orbit2', dz=0.2, shape='cross')
    aura_kit(2.0, 6, motes=12, mote_col='glow', height=4.2, style='rays')
    return finish(a)


ANIMALS = dict(spring_strider=spring_strider, copper_weevil=copper_weevil, gear_sentinel=gear_sentinel, magnet_tripod=magnet_tripod,
               iron_hound=iron_hound, clockwork_basilisk=clockwork_basilisk)
