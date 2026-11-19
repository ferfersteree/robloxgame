from gymlib import *

BG = '#0e1538'
NAME = 'DB_14_Celestial'
CX = 1.65   # planet centre (absolute x)


def mats():
    return dict(
        indigo=toon('cel_indigo', '#2a2f7a', shade='#0f1240', light='#6a74d8', spec=1.0, rim=0.6),
        navy=toon('cel_navy', '#151a4c', shade='#080a26', light='#3a468c', spec=0.5),
        gold=toon('gold', '#ffcf4d', shade='#c2742a', light='#fff2a6', spec=1.0),
        silver=toon('silver', '#dfe6f7', shade='#7f86c4', light='#ffffff', spec=1.0),
        core=glow('cel_core', '#fff4c2', 3.2),
        blue=glow('cel_blue', '#9fb8ff', 2.6),
    )


def spt(s, th, ph, k=1.03):
    """point on the planet surface: th = angle from outward axis, ph = angle around X"""
    t, p = math.radians(th), math.radians(ph)
    return (s * (CX + 0.85 * k * math.cos(t)), 0.88 * k * math.sin(t) * math.cos(p), 0.88 * k * math.sin(t) * math.sin(p))


def build():
    begin(NAME, ol=0.03)
    M = mats()
    indigo, navy, gold, silver, core, blue = (M[k] for k in ('indigo', 'navy', 'gold', 'silver', 'core', 'blue'))
    cyl('handle', 0.15, 1.5, navy, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.45, 0.45, 4, silver, segs=5, steps=10, ol=0.012)
    prof = [(CX - 0.85 * math.cos(math.pi * i / 8), 0.88 * math.sin(math.pi * i / 8)) for i in range(9)]
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        torus('grip_end_' + n, 0.17, 0.045, gold, 12, 6, loc=(s * 0.54, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.22), (0.66, 0.27), (0.8, 0.42), (0.88, 0.42), (0.88, 0)], silver, 12, scale=(s, 1, 1))
        torus('collar_ring_' + n, 0.45, 0.045, gold, 12, 5, loc=(s * 0.92, 0, 0), ol=0.02)
        lathe('planet_' + n, prof, indigo, 16, scale=(s, 1, 1))
        # glowing core star on the end
        star('core_star_' + n, 0.36, 0.13, 8, 0.1, core, loc=(s * 2.5, 0, 0), rot=(0, 90, 0), ol=0.02)
        star('core_star_small_' + n, 0.2, 0.08, 4, 0.08, silver, loc=(s * 2.42, 0, 0), rot=(0, 90, 45), ol=0.015)
        # two tilted gold halo rings
        torus('halo_a_' + n, 1.12, 0.045, gold, 20, 5, loc=(s * CX, 0, 0), rot=(0, 0, 32), ol=0.02)
        torus('halo_b_' + n, 1.12, 0.045, gold, 20, 5, loc=(s * CX, 0, 0), rot=(0, -32, 0), ol=0.02)
        # constellation lines with star studs
        for c, off in enumerate((0,)):
            cp = [(55, 100 + off), (68, 60 + off), (92, 72 + off), (104, 38 + off), (125, 52 + off)]
            P = [spt(s, a, b) for a, b in cp]
            for i in range(4):
                tube('const_%s%d%d' % (n, c, i), [P[i], P[i + 1]], 0.022, gold, segs=4, ol=0.01)
            for i in range(5):
                sphere('stud_%s%d%d' % (n, c, i), 0.055, core if i == 2 else gold, 6, 4, loc=P[i], ol=0.01)
        # crescent fins: one on top, two on the sides
        pts = arc_pts((s * CX, 0, 1.15), 0.35, -30, 210, 8, 'XZ')
        tube('crescent_top_' + n, pts, [0, 0.07, 0.1, 0.12, 0.13, 0.12, 0.1, 0.07, 0], silver, segs=6, ol=0.02)
        for e in (-1, 1):
            m = 'a' if e < 0 else 'b'
            pts = arc_pts((s * CX, e * 1.0, 0), 0.28, (-120 if e > 0 else 60), (120 if e > 0 else 300), 8, 'XY')
            tube('crescent_side_%s%s' % (n, m), pts, [0, 0.05, 0.08, 0.1, 0.1, 0.1, 0.08, 0.05, 0], silver, segs=6, ol=0.02)
        # silver star-point spikes
        for k in range(4):
            ang = k * 90 + 45
            d = radial(s, 70, ang)
            base = Vector((s * (CX + 0.35), 0, 0)) + radial(s, 90, ang) * 0.75
            crystal('spike_%s%d' % (n, k), 0.07, 0.6, silver, sides=4, tip=0.5, loc=base, rot=aim(d), ol=0.015)
            sphere('spike_node_%s%d' % (n, k), 0.05, blue, 6, 4, loc=base + d * 0.6, ol=0.01)

    # ---------------- FX
    fx(True)
    rnd = random.Random(14)
    star_m = glow('cel_star', '#fff0b8', 2.8)
    pl_m = glow('cel_planet', '#b0c4ff', 2.2)
    com_m = glow('cel_comet', '#d8e4ff', 3.0)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        tilt = math.radians(-18 * s)
        torus('fx_orbit_' + n, 1.45, 0.015, glow('cel_orbit', '#a8b8ff', 1.8), 32, 3, loc=(s * CX, 0, 0), rot=(0, 0, -18 * s))
        for i in range(9):
            a = 2 * math.pi * i / 9
            y0, z0 = 1.45 * math.cos(a), 1.45 * math.sin(a)
            p = (s * CX - y0 * math.sin(tilt), y0 * math.cos(tilt), z0)
            if i % 3 == 0:
                sphere('fx_planet_%s%d' % (n, i), 0.09, pl_m, 8, 5, loc=p)
            else:
                star('fx_ostar_%s%d' % (n, i), 0.14, 0.05, 4, 0.03, star_m, loc=p, rot=(90, 0, rnd.uniform(0, 45)))
        sphere('fx_aura_' + n, 1.55, ghost('cel_aura', '#a9a8ff', 1.1, 0.11), 16, 10, loc=(s * CX, 0, 0), scale=(1.15, 1, 1))
        for k in range(4):
            star('fx_sparkle_%s%d' % (n, k), rnd.uniform(0.08, 0.14), 0.03, 4, 0.02, star_m,
                 loc=(s * rnd.uniform(0.8, 2.4), -rnd.uniform(0.9, 1.4), rnd.uniform(-1.0, 1.4)), rot=(90, 0, rnd.uniform(0, 45)))
        # comet streak
        head = Vector((s * 2.2, -0.9, 1.5))
        tail = head + Vector((-s * 1.3, -0.15, 0.55))
        tube('fx_comet_' + n, [head, head.lerp(tail, 0.3), head.lerp(tail, 0.6), tail], [0.07, 0.06, 0.03, 0.0], com_m, segs=5)
        sphere('fx_comet_head_' + n, 0.1, com_m, 8, 5, loc=head)
    torus('fx_big_halo', 2.9, 0.02, glow('cel_halo', '#c8d0ff', 1.8), 48, 3, 'Y', loc=(0, 0.2, 0.2))
    fx(False)
    return stats(NAME)
