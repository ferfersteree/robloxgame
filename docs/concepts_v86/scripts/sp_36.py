from spearlib import *

NAME = 'SP_36_sky_harpoon'
N = 36
BG = '#6fa9e3'        # high sky
GROUND = '#93b4e0'    # cloud deck
TIP = 9.5
TRAIL = 5.2
FX_EXPORT = {'barb': 'im_barb_0', 'wind_ring': 'im_wind_0', 'cloud_puff': 'im_puff_0'}


def mats():
    return dict(
        sky=toon('sh_sky', '#4fb4ff', '#2468c8', '#a5defd', spec=0.8, emit=0.1),
        brass=toon('sh_brass', '#e8b43e', '#a8621c', '#ffe590', spec=1.0),
        steel=toon('sh_steel', '#9fb3cc', '#56698c', '#e6f0fb', spec=1.0, rimcol='#a0d8ff'),
        rope=toon('sh_rope', '#ecd9a6', '#a8894e', '#fff2c8', spec=0.2),
        navy=toon('sh_navy', '#2c4fa8', '#1b2f70', '#6f93e6'),
        white=toon('sh_white', '#ffffff', '#b8cdea', '#ffffff', spec=0.3),
        cyan=glow('sh_cyan', '#5fe8ff', 1.6),
        sun=glow('sh_sun', '#fff0a0', 3.4),
    )


def shaft_parts(body, wrap, cap, ring, z0=0.6, top=6.4):
    rod('shaft_lo', 0.155, z0, 3.3, body, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, top, body, r1=0.145)
    coil('wrap_lo', 0.178, 0.032, 1.4, 1.88, 3, wrap, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, cap, 12, 5, loc=(0, 0, 1.93))
    torus('wrap_lo_base', 0.18, 0.04, cap, 12, 5, loc=(0, 0, 1.33))
    coil('wrap_hi', 0.175, 0.032, 3.12, 3.62, 3, wrap, segs=5, phase=1.2)
    torus('wrap_hi_cap', 0.178, 0.04, cap, 12, 5, loc=(0, 0, 3.08))
    torus('wrap_hi_top', 0.178, 0.04, cap, 12, 5, loc=(0, 0, 3.66))
    for i, z in enumerate((4.3, 4.6, 4.9)):
        torus('shaft_ring_%d' % i, 0.155, 0.03, ring, 12, 4, loc=(0, 0, z), ol=0.015)


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    sky, brass, steel, rope, navy, white, cyan, sun = (M[k] for k in ('sky', 'brass', 'steel', 'rope', 'navy', 'white', 'cyan', 'sun'))
    # ---- tail: brass counterweight with a rope eye and two fins
    sphere('tail_weight', 0.3, brass, 12, 7, loc=(0, 0, 0.34), scale=(1, 1, 1.15))
    torus('tail_band', 0.28, 0.05, navy, 14, 5, loc=(0, 0, 0.36))
    torus('tail_eye', 0.14, 0.035, rope, 12, 5, loc=(0, 0.0, 0.14), rot=(90, 0, 0))
    for s in (-1, 1):
        leaf('tail_fin_%s' % ('ab'[s > 0]), 0.75, 0.3, white, 0.04, 5, loc=(s * 0.12, 0, 0.9), rot=(90, -(90 - s * 55), 0), ol=0.015)
    # ---- shaft: sky blue, rope wraps, a big rope coil, gold caps
    shaft_parts(sky, rope, brass, navy)
    coil('rope_big', 0.21, 0.05, 4.1, 5.3, 3, rope, segs=5, phase=0.5)
    torus('rope_big_cap_a', 0.215, 0.05, brass, 12, 5, loc=(0, 0, 4.0))
    torus('rope_big_cap_b', 0.215, 0.05, brass, 12, 5, loc=(0, 0, 5.4))
    # ---- socket: brass cup
    lathe('socket', [(6.3, 0.14), (6.45, 0.2), (6.7, 0.28), (6.95, 0.22), (7.05, 0.1), (7.1, 0)], brass, 14)
    torus('socket_ring', 0.27, 0.05, navy, 14, 5, loc=(0, 0, 6.5))
    torus('socket_ring_b', 0.22, 0.04, cyan, 14, 4, loc=(0, 0, 6.95), ol=0)
    # ---- harpoon head: long steel blade, glowing core, two pairs of big barbs
    ol_ = [(0, 6.9), (0.36, 7.2), (0.5, 7.9), (0.42, 8.7), (0.17, 9.2), (0, TIP), (-0.17, 9.2), (-0.42, 8.7), (-0.5, 7.9), (-0.36, 7.2)]
    blade('harpoon', ol_, 0.14, steel)
    blade('harpoon_core', [(x * 0.45, 7.2 + (z - 6.9) * 0.78) for (x, z) in ol_], 0.15, cyan, ol=0)
    for k, (z0, sc_) in enumerate(((8.5, 1.0), (7.55, 0.8))):
        for s in (-1, 1):
            nm = 'barb_%d%s' % (k, 'ab'[s > 0])
            pts = [(s * 0.25, 0, z0 - 0.1), (s * 0.7 * sc_, 0, z0 + 0.1), (s * 1.05 * sc_, 0, z0 - 0.25 * sc_), (s * 1.12 * sc_, 0, z0 - 0.8 * sc_)]
            tube(nm, pts, [0.12, 0.12, 0.09, 0.0], brass, 6)
            sphere(nm + '_nub', 0.09, sun, 6, 4, loc=(s * 1.02 * sc_, 0, z0 - 0.5 * sc_), ol=0)
    torus('blade_band_a', 0.4, 0.06, brass, 14, 5, loc=(0, 0, 7.25), scale=(1, 0.45, 1))
    torus('blade_band_b', 0.36, 0.06, navy, 14, 5, loc=(0, 0, 8.6), scale=(1, 0.45, 1))
    # ---- floating: three detached brass rings and cloud puffs, glowing orbs
    for i, z in enumerate((7.7, 8.45, 9.1)):
        torus('float_ring_%d' % i, 0.62 - 0.1 * i, 0.05, brass if i != 1 else cyan, 18, 5, loc=(0, 0, z), rot=(0, 0, 0), ol=0.02 if i != 1 else 0)
    for i, (x, y, z) in enumerate(((0.95, 0.3, 6.9), (-1.0, -0.2, 7.2), (0.6, -0.6, 9.4))):
        sphere('float_puff_%d' % i, 0.22, white, 8, 5, loc=(x, y, z))
    for i in range(3):
        a = math.radians(40 + i * 120)
        sphere('float_orb_%d' % i, 0.09, sun, 8, 5, loc=(0.78 * math.cos(a), 0.78 * math.sin(a), 8.0 + 0.25 * i), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def fly(ob, p0, p1, a, s1, alpha=True, s0=0.3):
    key(ob, IMPACT0, loc=p0, scale=0, alpha=1 if alpha else None)
    key(ob, a, loc=p0, scale=s0, alpha=1 if alpha else None)
    if alpha:
        key(ob, IMPACT0 + 44, loc=p1, scale=s1, alpha=0)
    else:
        key(ob, IMPACT0 + 30, loc=p1, scale=s1)
        key(ob, IMPACT0 + 44, loc=p1, scale=0)
    tidy(ob, 'impact')
    ease_keys(ob)


def build_fx(M):
    rnd = random.Random(3636)
    cl = ghost('sh_cloudfx', '#ffffff', 1.3, 0.9, 1.0)
    cl2 = ghost('sh_cloudfx2', '#cfe6ff', 1.2, 0.9, 1.0)
    aura = ghost('sh_aura', '#bfeaff', 1.2, 0.05, 1.8)
    wind = glow('sh_wind', '#e8fbff', 2.4)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.7, aura, 14, 8, loc=(0, 0, 8.2), scale=(1.4, 0.9, 1.7))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.035, 4, 0.02, M['sun'], loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.0), -0.3, 7.5 + i * 0.7), rot=(90, 0, 0))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.1)
        sphere('idle_mote_%d' % i, rnd.uniform(0.06, 0.1), cl if i % 2 else cl2, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.5)))
    # ---------------- flight
    fx('flight')
    puffs = [sphere('fl_puff_%d' % i, 0.3, cl if i % 2 else cl2, 10, 6) for i in range(10)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 8.0 - 12.0 * t),
           smax=lambda t, i: (0.6 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    fe = [leaf('fl_feather_%d' % i, 0.65, 0.22, (M['white'], M['sky'], M['brass'])[i % 3], 0.04, 5, ol=0.012) for i in range(9)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(9)]
    stream(fe, lambda t, i: (fj[i][0] * (0.4 + 1.0 * t), fj[i][1] * (0.4 + 1.0 * t), 8.8 - 12.5 * t), smax=1.0,
           spin=lambda t, i: (fj[i][2] + 300 * t, 90, fj[i][2]))
    rings = [torus('fl_wind_%d' % i, 0.55, 0.05, wind, 26, 5) for i in range(4)]
    stream(rings, lambda t, i: (0, 0, 9.4 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (0, 0, 360 * t))
    sps = [star('fl_spark_%d' % i, 0.14, 0.035, 4, 0.02, M['sun']) for i in range(5)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(5)]
    stream(sps, lambda t, i: (sj[i][0] * (0.4 + 1.0 * t), sj[i][1] * (0.4 + 1.0 * t), 8.4 - 11.0 * t), smax=1.4,
           spin=lambda t, i: (90, 0, 360 * t))
    # ---------------- impact: 3 harpoon barbs anchor in the ground, cloud puffs, wind rings spiral up
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.6, ghost('sh_flash', '#ffffff', 2.0, 0.7, 1.2), 14, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 5, scale=2.4, alpha=0.7)
    key(flash, f + 12, scale=3.2, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    hook = [(0, 0, -0.2), (0, 0, 0.5), (-0.12, 0, 1.0), (-0.5, 0, 1.4), (-0.95, 0, 1.5)]
    for i in range(3):
        a = i * 120 + 60
        ar = math.radians(a)
        R = 1.7
        b = tube('im_barb_%d' % i, hook, [0.16, 0.14, 0.11, 0.07, 0.0], M['brass'], 8, loc=(cx + R * math.cos(ar), R * math.sin(ar), 0), rot=(0, 0, a))
        nub = sphere('im_barb_glow_%d' % i, 0.12, M['sun'], 8, 5, loc=(cx + R * math.cos(ar), R * math.sin(ar), 0.02), ol=0)
        t0 = f + 2 + i * 2
        for o, sc_ in ((b, (1, 1, 1)), (nub, (1, 1, 1))):
            key(o, IMPACT0, scale=0)
            key(o, t0, scale=0)
            key(o, t0 + 3, scale=(1.1, 1.1, 1.25))
            key(o, t0 + 8, scale=sc_)
            key(o, IMPACT0 + 38, scale=sc_)
            key(o, IMPACT0 + 44, scale=0)
            tidy(o, 'impact')
    for i in range(12):
        a = math.radians(i * 30 + rnd.uniform(-8, 8))
        r = rnd.uniform(1.2, 3.0) * (1.25 if math.cos(a) < 0 else 1.0)
        p = sphere('im_puff_%d' % i, 0.45, cl if i % 2 else cl2, 12, 7)
        fly(p, (cx, 0, 0.3), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.5, 1.8)), f + i % 4, rnd.uniform(1.6, 2.4))
    for k in range(6):
        rg = torus('im_wind_%d' % k, 0.6, 0.05, wind, 30, 5, loc=(cx, 0, 0.2 + 0.2 * k), rot=(14, 0, 0))
        t0 = f + k * 2
        key(rg, IMPACT0, scale=0, alpha=1, rot=(14, 0, 0))
        key(rg, t0, loc=(cx, 0, 0.2 + 0.2 * k), scale=0.5, alpha=1, rot=(14, 0, 0))
        key(rg, IMPACT0 + 44, loc=(cx, 0, 4.2 + 0.2 * k), scale=2.4 - 0.15 * k, alpha=0, rot=(14, 0, 720))
        tidy(rg, 'impact')
        ease_keys(rg)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.2)
        fm = leaf('im_feather_%d' % i, 0.8, 0.28, (M['white'], M['sky'], M['brass'])[i % 3], 0.04, 5, ol=0.012)
        p0 = (cx, 0, 0.3)
        pm = (cx + 0.5 * r * math.cos(a), 0.5 * r * math.sin(a), rnd.uniform(2.2, 3.4))
        p1 = (cx + r * math.cos(a + 0.9), r * math.sin(a + 0.9), rnd.uniform(0.3, 1.0))
        t0 = f + rnd.randint(0, 6)
        key(fm, IMPACT0, loc=p0, scale=0, rot=(90, 0, 0))
        key(fm, t0, loc=p0, scale=0.4, rot=(90, -80, a * 57))
        key(fm, t0 + 14, loc=pm, scale=1.0, rot=(90, -40, a * 57 + 160))
        key(fm, IMPACT0 + 44, loc=p1, scale=0, rot=(90, 20, a * 57 + 420))
        tidy(fm, 'impact')
        ease_keys(fm)
    for i in range(3):
        a = math.radians(i * 120 + 60)
        ar = torus('im_anchor_ring_%d' % i, 0.3, 0.05, M['sun'], 20, 4, loc=(cx + 1.7 * math.cos(a), 1.7 * math.sin(a), 0.06), ol=0)
        key(ar, IMPACT0, scale=0, alpha=1)
        key(ar, f + 4 + i * 2, scale=0.3, alpha=1)
        key(ar, f + 18 + i * 2, scale=2.2, alpha=0)
        tidy(ar, 'impact', interp='LINEAR')
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.8, 2.0)
        st = star('im_spark_%d' % i, 0.18, 0.045, 4, 0.02, M['sun'], rot=(90, 0, 0))
        fly(st, (cx, 0, 0.5), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.4, 3.2)), f + 2 + i, 1.2)
    return True
