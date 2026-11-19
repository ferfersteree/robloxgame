from gymlib import *

BG = '#e6ddcd'
NAME = 'DB_02_Stone'


def mats():
    return dict(
        stone=toon('stone_grey', '#a29d92', shade='#625d5c', light='#d4cec0', spec=0.25),
        dark=toon('stone_dark', '#7a756e', shade='#4a4650', light='#aaa498', spec=0.2),
        moss=toon('stone_moss', '#72b040', shade='#3b7a2c', light='#b9e46a', spec=0.2),
        rope=toon('stone_rope', '#cf9f5c', shade='#82562e', light='#f3d598', spec=0.2),
        crack=toon('stone_crack', '#2f2b33', shade='#17141b', light='#47424c', spec=0.0, rim=0.0),
        sand=toon('stone_sand', '#dcc79c', shade='#9a8260', light='#f8ecc8', spec=0.3),
        lichen=toon('stone_lichen', '#e6a93c', shade='#a8691f', light='#ffd978', spec=0.2),
        wood=toon('stone_wood', '#8e5c36', shade='#55331c', light='#c08a58', spec=0.3),
    )


def build():
    begin(NAME, ol=0.03)
    M = mats()
    stone, dark, moss = M['stone'], M['dark'], M['moss']
    rope, crack, sand, lichen, wood = M['rope'], M['crack'], M['sand'], M['lichen'], M['wood']

    # ---- handle: wood bar wrapped with rope
    cyl('handle', 0.15, 1.5, wood, segs=8, bev=0.02, sharp=20)
    coil('grip_rope', 0.155, 0.028, -0.44, 0.44, 5, rope, segs=4, steps=8, ol=0.015)
    for i, x in enumerate((-0.46, 0.46)):
        torus('grip_knot_%d' % i, 0.15, 0.03, rope, 12, 4, loc=(x, 0, 0), ol=0.015)

    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sd = 4 if s > 0 else 11
        # stone-ring collar (sandstone neck) + pebbles around it
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.24), (0.64, 0.3), (0.74, 0.33), (0.82, 0.28), (0.84, 0)],
              sand, 8, scale=(s, 1, 1), sharp=20)
        for k in range(4):
            d = radial(s, 90, k * 90 + 20)
            rock('collar_pebble_%s%d' % (n, k), 0.09, dark, seed=sd + k, sub=1, rough=0.12,
                 loc=Vector((s * 0.7, 0, 0)) + d * 0.36)
        # lumpy main boulder
        rock('boulder_' + n, 0.7, stone, seed=sd, sub=2, rough=0.14, freq=1.3, loc=(s * 1.02, 0, 0), scale=(0.55, 1.0, 1.0))
        # extra lumps
        for k, a in enumerate((70, 190, 310)):
            d = radial(s, 90, a + (15 if s > 0 else -15))
            rock('lump_%s%d' % (n, k), 0.27 - 0.03 * k, dark, seed=sd + 10 + k, sub=1, rough=0.2,
                 loc=Vector((s * (1.0 + 0.08 * (k - 1)), 0, 0)) + d * 0.62)
        # standing-stone crown (little megalith slabs leaning outward)
        for k in range(5):
            a = k * 72 + (0 if s > 0 else 36)
            d = radial(s, 90, a)
            d2 = Vector((s * 0.35, d.y, d.z)).normalized()
            box('slab_%s%d' % (n, k), (0.1, 0.22, 0.36), stone, bev=0.04, bsegs=1,
                loc=Vector((s * 0.82, 0, 0)) + d * 0.5, rot=aim(d2, 0))
        # rope / vine bindings
        for i, (bx, br) in enumerate(((1.0, 0.72), (1.24, 0.6))):
            torus('rope_%s%d' % (n, i), br, 0.05, rope, 12, 4, loc=(s * bx, 0, 0), ol=0.02)
        # moss + lichen patches (flattened rocks lying on the surface)
        for k, a in enumerate((100, 235)):
            d = radial(s, 90, a)
            rock('moss_%s%d' % (n, k), 0.27, moss, seed=sd + 20 + k, sub=1, rough=0.1, ol=0.02,
                 loc=Vector((s * 1.08, 0, 0)) + d * 0.66, rot=aim(d), scale=(1, 1, 0.32))
        d = radial(s, 90, 330)
        rock('lichen_' + n, 0.17, lichen, seed=sd + 30, sub=1, rough=0.1, ol=0.02,
             loc=Vector((s * 1.0, 0, 0)) + d * 0.68, rot=aim(d), scale=(1, 1, 0.3))
        # dark cracks inlaid on the boulder
        for k, a0 in enumerate((150, 215)):
            pts = []
            for (dx, da, rr) in ((-0.2, 0, 0.6), (-0.08, 10, 0.69), (0.06, -8, 0.7), (0.2, 6, 0.6)):
                ang = math.radians(a0 + da)
                pts.append((s * (1.02 + dx), rr * math.cos(ang), rr * math.sin(ang)))
            tube('crack_%s%d' % (n, k), pts, [0.0, 0.03, 0.03, 0.0], crack, segs=4, smooth=False, ol=0)
        # carved end plate with spiral emblem
        cyl('end_plate_' + n, 0.4, 0.12, dark, segs=10, bev=0.035, loc=(s * 1.36, 0, 0), sharp=20)
        torus('plate_ring_' + n, 0.4, 0.045, sand, 12, 4, loc=(s * 1.36, 0, 0), ol=0.02)
        coil('spiral_' + n, 0.27, 0.022, s * 1.43, s * 1.43, 2.2, crack, segs=4, steps=12, R1=0.05, ol=0.012)

    # ---- effects: nearly none
    fx(True)
    dust = ghost('stone_dust', '#f1e6cc', 1.0, 0.12)
    for i, (p, r) in enumerate((((-1.1, -0.55, -0.7), 0.3), ((1.15, -0.6, -0.72), 0.26), ((0.1, -0.7, -0.8), 0.2))):
        sphere('fx_dust_%d' % i, r, dust, 10, 6, loc=p, scale=(1.4, 1.0, 0.6))
    for i, p in enumerate(((-1.65, -0.4, -0.3), (1.7, -0.5, 0.1))):
        rock('fx_pebble_%d' % i, 0.05, dark, seed=40 + i, sub=1, loc=p, ol=0.012)
    fx(False)
    return stats(NAME)
