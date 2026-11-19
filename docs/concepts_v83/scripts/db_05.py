from gymlib import *

BG = '#8d97a6'
NAME = 'DB_05_Granite'


def mats():
    return dict(
        granite=toon('gran_stone', '#8e919b', shade='#4d5163', light='#c9ccd6', spec=0.25),
        cap=toon('gran_cap', '#5d6272', shade='#2f3342', light='#8a90a4', spec=0.25),
        sd=toon('gran_speck_d', '#2f323d', shade='#1a1c26', light='#4a4e5c', spec=0.1),
        sl=toon('gran_speck_l', '#f0ece4', shade='#bdb6a8', light='#ffffff', spec=0.2),
        iron=toon('gran_iron', '#3b4252', shade='#1c212c', light='#6b7690', spec=0.9),
        brass=toon('gran_brass', '#c8963c', shade='#7a4a1c', light='#ffe08a', spec=1.0),
        rune=glow('gran_rune', '#3cffc4', 2.6),
        spark=glow('spark_white', '#ffffff', 2.5),
    )


# rune glyphs: (dx along bar, dt tangential, size along X, size tangential)
GLYPHS = [
    [(0, 0, 0.46, 0.05), (0.1, 0, 0.05, 0.28), (-0.14, 0, 0.05, 0.16)],
    [(0, 0.1, 0.4, 0.05), (0, -0.1, 0.4, 0.05), (0, 0, 0.05, 0.25)],
    [(0, 0, 0.05, 0.34), (-0.12, 0.1, 0.22, 0.05), (0.12, -0.1, 0.22, 0.05)],
    [(0, 0, 0.34, 0.05), (0.17, 0.08, 0.05, 0.18), (-0.17, -0.08, 0.05, 0.18)],
]


def tang(ang):
    a = math.radians(ang)
    return Vector((0, math.sin(a), -math.cos(a)))


def build():
    begin(NAME, ol=0.03)
    M = mats()
    granite, cap, sd, sl, iron, brass, rune, spark = (M[k] for k in ('granite', 'cap', 'sd', 'sl', 'iron', 'brass', 'rune', 'spark'))

    cyl('handle', 0.15, 1.5, iron, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.42, 0.42, 4, brass, segs=5, steps=10, ol=0.012)
    rnd = random.Random(5)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        torus('grip_end_' + n, 0.16, 0.03, brass, 12, 6, loc=(s * 0.535, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.56, 0), (0.56, 0.25), (0.62, 0.29), (0.72, 0.29), (0.76, 0.24), (0.76, 0)], iron, 12, scale=(s, 1, 1))
        # octagonal granite block (flats face 0/45/90 ... degrees)
        lathe('block_' + n, [(0.76, 0), (0.76, 0.58), (0.86, 0.72), (1.5, 0.72), (1.6, 0.62), (1.6, 0)], granite, 8,
              scale=(s, 1, 1), rot=(22.5, 0, 0))
        lathe('cap_' + n, [(1.6, 0), (1.6, 0.5), (1.66, 0.46), (1.675, 0.34), (1.675, 0)], cap, 8,
              scale=(s, 1, 1), rot=(22.5, 0, 0))
        for j, x in enumerate((0.92, 1.5)):
            lathe('band_%s%d' % (n, j), [(-0.06, 0.7), (-0.04, 0.77), (0.04, 0.77), (0.06, 0.7)], iron, 8,
                  loc=(s * x, 0, 0), rot=(22.5, 0, 0), caps=False, ol=0.02)
        # carved glowing runes on four faces
        for gi, ang in enumerate((90, 135, 180, 225)):
            base = Vector((s * 1.18, 0, 0)) + radial(s, 90, ang) * 0.66
            tg = tang(ang)
            for bi, (dx, dt, sx, st) in enumerate(GLYPHS[(gi + (0 if s < 0 else 2)) % 4]):
                box('rune_%s%d_%d' % (n, gi, bi), (sx, st, 0.05), rune, bev=0, loc=base + Vector((s * dx, 0, 0)) + tg * dt,
                    rot=(ang - 90, 0, 0), ol=0)
        # obelisk corner studs
        for k, ang in enumerate((67.5, 112.5, 247.5, 292.5)):
            d = radial(s, 90, ang)
            cone('stud_%s%d' % (n, k), 0.14, 0.4, cap, 4, r2=0.05, loc=Vector((s * 1.18, 0, 0)) + d * 0.7, rot=aim(d), ol=0.02)
        # speckles
        for i in range(6):
            ang = rnd.choice((0, 45, 90, 135, 180, 225, 270, 315))
            p = Vector((s * (1.18 + rnd.uniform(-0.4, 0.4)), 0, 0)) + radial(s, 90, ang) * 0.668 + tang(ang) * rnd.uniform(-0.2, 0.2)
            box('speck_%s%d' % (n, i), (rnd.uniform(0.05, 0.1), rnd.uniform(0.04, 0.08), 0.03), sd if i % 2 == 0 else sl,
                bev=0, loc=p, rot=(ang - 90, 0, 0), ol=0)
        # end-cap chevron emblem
        for e in (-1, 1):
            box('emblem_%s%d' % (n, e), (0.04, 0.26, 0.06), rune, bev=0, loc=(s * 1.665, e * 0.1, 0), rot=(e * 45, 0, 0), ol=0)

    # ---------------- FX
    fx(True)
    rnd = random.Random(55)
    aura = ghost('gran_aura', '#3cffb4', 1.0, 0.1)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_aura_' + n, 1.0, aura, 14, 8, loc=(s * 1.2, 0, 0), scale=(1.15, 1, 1))
    for i in range(4):
        s = -1 if i % 2 else 1
        crystal('fx_chip_%d' % i, 0.07, 0.2, rune, sides=4, tip=0.4, both=True,
                loc=(s * rnd.uniform(0.9, 1.9), rnd.uniform(-0.9, 0.5), rnd.uniform(0.9, 1.5)),
                rot=(rnd.uniform(0, 40), rnd.uniform(0, 40), rnd.uniform(0, 90)))
    for i in range(3):
        s = -1 if i % 2 else 1
        star('fx_sparkle_%d' % i, rnd.uniform(0.1, 0.16), 0.03, 4, 0.02, spark,
             loc=(s * rnd.uniform(0.9, 1.9), -rnd.uniform(0.9, 1.2), rnd.uniform(0.3, 1.2)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    return stats(NAME)
