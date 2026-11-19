from gymlib import *

BG = '#aab6c8'
NAME = 'DB_04_Iron'


def mats():
    return dict(
        iron=toon('iron_plate', '#4b5262', shade='#22283a', light='#8592ad', spec=1.0, rim=0.6),
        steel=toon('iron_steel', '#7d879c', shade='#3b4259', light='#c4cee6', spec=1.0),
        dark=toon('iron_black', '#2c313d', shade='#13151d', light='#4d556b', spec=0.8),
        rivet=toon('iron_rivet', '#a8b3c9', shade='#4d5672', light='#ffffff', spec=1.0),
        enamel=toon('iron_enamel', '#2f86e0', shade='#164a92', light='#a6dcff', spec=1.0, rim=0.9, emit=0.15),
        cold=glow('iron_cold', '#62b8ff', 2.2),
        hot=glow('iron_forge', '#ff7a1a', 2.4),
    )


def build():
    begin(NAME, ol=0.03)
    M = mats()
    iron, steel, dark, rivet, enamel, cold = M['iron'], M['steel'], M['dark'], M['rivet'], M['enamel'], M['cold']

    # ---- knurled grip
    cyl('handle', 0.15, 1.5, dark, segs=8, bev=0.02, sharp=20)
    for i, x in enumerate((-0.4, -0.2, 0.0, 0.2, 0.4)):
        torus('knurl_%d' % i, 0.15, 0.022, steel, 8, 4, loc=(x, 0, 0), ol=0.012)
    for i, x in enumerate((-0.3, 0.3)):
        lathe('grip_band_%d' % i, [(-0.05, 0.15), (-0.04, 0.17), (0.04, 0.17), (0.05, 0.15)], enamel, 8,
              loc=(x, 0, 0), caps=False, ol=0.012, sharp=20)

    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        # hex flange collar
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.26), (0.66, 0.3), (0.78, 0.44), (0.9, 0.5), (0.96, 0.5), (0.96, 0)],
              steel, 6, scale=(s, 1, 1), sharp=20)
        # heavy octagonal dark-steel block
        lathe('block_' + n, [(0.96, 0), (0.96, 0.64), (1.04, 0.76), (1.28, 0.76), (1.36, 0.64), (1.36, 0)],
              iron, 8, scale=(s, 1, 1), sharp=20)
        # riveted bands
        for i, bx in enumerate((1.06, 1.3)):
            lathe('band_%s%d' % (n, i), [(bx - 0.05, 0.7), (bx - 0.05, 0.84), (bx + 0.05, 0.84), (bx + 0.05, 0.7)],
                  steel, 8, scale=(s, 1, 1), sharp=20)
        # cold-blue glowing strip between the bands
        lathe('glow_strip_' + n, [(1.14, 0.7), (1.14, 0.775), (1.22, 0.775), (1.22, 0.7)], cold, 8, scale=(s, 1, 1))
        # rivets on the outer band (one per octagon face)
        for k in range(8):
            a = math.radians(22.5 + 45 * k)
            sphere('rivet_%s%d' % (n, k), 0.055, rivet, 6, 3,
                   loc=(s * 1.3, 0.776 * math.cos(a), 0.776 * math.sin(a)), ol=0.012)
        # protruding hex bolt heads
        for k in range(4):
            d = radial(s, 90, 22.5 + 90 * k)
            cyl('bolt_%s%d' % (n, k), 0.1, 0.22, rivet, segs=6, bev=0.03, axis='Z',
                loc=Vector((s * 1.18, 0, 0)) + d * 0.74, rot=aim(d), ol=0.02)
        # anvil horns at the corners
        for k in range(4):
            a = 45 + 90 * k
            d = radial(s, 65, a)
            cone('horn_%s%d' % (n, k), 0.17, 0.5, steel, 4, r2=0.05,
                 loc=Vector((s * 1.2, 0, 0)) + radial(s, 90, a) * 0.6, rot=aim(d), sharp=20)
        # blue enamel end plate with an anvil emblem
        cyl('end_plate_' + n, 0.5, 0.1, enamel, segs=8, bev=0.03, loc=(s * 1.41, 0, 0), sharp=20)
        x = s * 1.51
        box('anvil_top_' + n, (0.1, 0.5, 0.12), steel, bev=0.02, bsegs=1, loc=(x, 0, 0.12), ol=0.015)
        box('anvil_waist_' + n, (0.1, 0.2, 0.16), steel, bev=0.02, bsegs=1, loc=(x, 0, 0.0), ol=0.015)
        box('anvil_base_' + n, (0.1, 0.4, 0.1), steel, bev=0.02, bsegs=1, loc=(x, 0, -0.13), ol=0.015)
        cone('anvil_horn_' + n, 0.1, 0.24, steel, 6, r2=0.03, loc=(x, 0.25, 0.12), rot=aim((0, 1, 0)), ol=0.012)

    # ---- effects: sparks and a faint cold sheen
    fx(True)
    sp1 = glow('iron_spark', '#ffa63a', 2.8)
    sp2 = glow('iron_spark2', '#ffe27a', 2.8)
    for i, (p, r) in enumerate((((1.0, -0.95, 0.75), 0.14), ((-1.1, -1.0, 0.55), 0.11), ((1.7, -0.8, 0.2), 0.1), ((-1.75, -0.8, -0.1), 0.12))):
        star('fx_spark_%d' % i, r, 0.03, 4, 0.02, sp1 if i % 2 == 0 else sp2, loc=p, rot=(90, 0, 20 * i))
    for i, (a, b) in enumerate((((0.6, -1.0, 0.9), (0.85, -1.0, 1.1)), ((-0.7, -1.0, 0.8), (-0.95, -1.0, 1.0)))):
        tube('fx_streak_%d' % i, [a, b], [0.025, 0.0], sp2, segs=4)
    for s in (-1, 1):
        sphere('fx_sheen_' + ('L' if s < 0 else 'R'), 1.0, ghost('iron_sheen', '#8fc4ff', 0.9, 0.1), 14, 8,
               loc=(s * 1.2, 0, 0), scale=(0.9, 1, 1))
    fx(False)
    return stats(NAME)
