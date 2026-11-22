from spearlib import *

NAME = 'SP_45_rift_conductor'
N = 45
BG = '#3e3066'        # rift storm
GROUND = '#34295a'
TIP = 9.45
TRAIL = 5.2
FX_EXPORT = {'electric_ring': 'im_ring_0', 'bolt': 'im_bolt_0_0', 'node': 'im_node_0', 'ground_crack': 'im_crack_0'}


def mats():
    return dict(
        steel=toon('rc_steel', '#4a4a68', '#22223a', '#8a8ab4', spec=1.0, rim=0.7, rimcol='#c080ff'),
        dark=toon('rc_dark', '#241e38', '#0e0a1a', '#5a4c84', spec=0.8, rim=0.6, rimcol='#e0a0ff'),
        silver=toon('rc_silver', '#e2e0f4', '#7c78a8', '#ffffff', spec=1.0),
        gold=toon('rc_gold', '#f0c040', '#a8681c', '#fff0a0', spec=1.0),
        plum=toon('rc_plum', '#7a30c0', '#3c1478', '#b878f0', emit=0.25),
        vio=glow('rc_vio', '#b45cff', 3.2),
        cyan=glow('rc_cyan', '#7af0ff', 3.2),
        white=glow('rc_white', '#f4eaff', 3.6),
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
    begin(NAME, N, ol=0.032)
    M = mats()
    steel, dark, silver, gold, plum, vio, cyan, white = (M[k] for k in ('steel', 'dark', 'silver', 'gold', 'plum', 'vio', 'cyan', 'white'))
    # ---- tail: grounding spike with a violet core
    tube('tail_spike', [(0, 0, 1.0), (0.0, 0, 0.55), (0.0, 0, 0.0)], [0.2, 0.15, 0.0], steel, 8)
    sphere('tail_core', 0.12, vio, 8, 5, loc=(0, 0, 1.0), ol=0)
    torus('tail_ring', 0.21, 0.05, gold, 12, 5, loc=(0, 0, 0.9))
    torus('tail_float', 0.4, 0.035, vio, 20, 4, loc=(0, 0, 0.5), rot=(14, 0, 0), ol=0)
    # ---- shaft: steel with violet stripes
    shaft_parts(steel, plum, gold, vio, z0=1.05)
    for i in range(3):
        torus('stripe_%d' % i, 0.158, 0.03, vio if i != 1 else cyan, 12, 4, loc=(0, 0, 5.15 + 0.3 * i), ol=0)
    # ---- socket: dark conductor cup with insulator discs
    lathe('socket', [(6.3, 0.14), (6.45, 0.24), (6.7, 0.34), (6.95, 0.28), (7.05, 0.16), (7.1, 0)], dark, 12)
    for i, z in enumerate((6.5, 6.72)):
        cyl('insulator_%d' % i, 0.4 - 0.05 * i, 0.12, silver if i == 0 else gold, 14, 0.03, loc=(0, 0, z))
    # ---- spire: tapering conductor rod with violet stripes and a glowing coil
    tube('spire', [(0, 0, 6.9), (0, 0, 7.7), (0, 0, 8.6), (0, 0, TIP)], [0.3, 0.26, 0.17, 0.0], steel, 10)
    for i, (z, r) in enumerate(((7.1, 0.29), (7.5, 0.265), (7.9, 0.225), (8.3, 0.19), (8.7, 0.13))):
        torus('spire_stripe_%d' % i, r + 0.01, 0.035, vio if i % 2 == 0 else white, 12, 4, loc=(0, 0, z), ol=0)
    coil('spire_coil', 0.34, 0.04, 7.2, 8.4, 3, gold, segs=5)
    sphere('spire_tip', 0.1, white, 8, 5, loc=(0, 0, TIP - 0.15), ol=0)
    # ---- prongs: curved fork arms with glowing electrodes
    for k, (dx, dy) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
        reach = 1.1 if k < 2 else 0.8
        up = 8.5 if k < 2 else 8.1
        pts = [(0.3 * dx, 0.3 * dy, 6.95), (0.75 * dx * reach, 0.75 * dy * reach, 7.2), (1.0 * dx * reach, 1.0 * dy * reach, 7.8), (0.95 * dx * reach, 0.95 * dy * reach, up)]
        tube('prong_%d' % k, pts, [0.1, 0.09, 0.075, 0.05], dark, 7)
        sphere('electrode_%d' % k, 0.14, cyan if k < 2 else vio, 8, 5, loc=pts[-1], ol=0)
        torus('prong_ring_%d' % k, 0.1, 0.035, gold, 10, 4, loc=(pts[2][0], pts[2][1], pts[2][2]), ol=0.012)
    # ---- floating: arcs between the electrodes, orbiting charge orbs, broken ring
    bolt('arc_a', (1.1 * 0.95, 0, 8.5), (-1.1 * 0.95, 0, 8.5), cyan, 0.045, 5, 0.18, seed=3, ol=0)
    bolt('arc_b', (0.0, 0.76, 8.1), (0.0, -0.76, 8.1), vio, 0.04, 4, 0.15, seed=9, ol=0)
    for i in range(4):
        a = math.radians(i * 90 + 30)
        sphere('float_orb_%d' % i, 0.1, white if i % 2 else cyan, 8, 5, loc=(1.35 * math.cos(a), 0.9 * math.sin(a), 7.0 + 0.55 * i), ol=0)
    pts = [(1.3 * math.cos(math.radians(a)), 0.35, 8.0 + 1.0 * math.sin(math.radians(a))) for a in range(20, 161, 20)]
    tube('float_arc', pts, [0.0] + [0.04] * (len(pts) - 2) + [0.0], vio, 5, ol=0)
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
    rnd = random.Random(4545)
    aura = ghost('rc_aura', '#b070ff', 1.2, 0.05, 1.8)
    smoke = ghost('rc_smoke', '#5a2a90', 1.0, 0.8, 1.0)
    white, vio, cyan = M['white'], M['vio'], M['cyan']
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.1), scale=(1.5, 1.0, 1.6))
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.3)
        sphere('idle_spark_%d' % i, rnd.uniform(0.04, 0.08), (white, vio, cyan)[i % 3], 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.6)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.03, 4, 0.02, white, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), -0.4, 7.4 + i * 0.8), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    bs = [bolt('fl_bolt_%d' % i, (0, 0, 0), (0, 0, 0.9), (white, vio, cyan)[i % 3], 0.05, 4, 0.14, seed=i + 5, ol=0) for i in range(9)]
    bj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(9)]
    stream(bs, lambda t, i: (bj[i][0] * (0.35 + 1.0 * t), bj[i][1] * (0.35 + 1.0 * t), 8.8 - 12.5 * t), smax=1.3,
           spin=lambda t, i: (bj[i][2] + 400 * t, bj[i][2] * 0.5 + 300 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, vio if i % 2 else cyan, 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.3 - 6.8 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    sps = [sphere('fl_spark_%d' % i, 0.06, white, 6, 4) for i in range(10)]
    kj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(sps, lambda t, i: (kj[i][0] * (0.3 + 1.6 * t), kj[i][1] * (0.3 + 1.6 * t), 8.4 - 12.0 * t), smax=1.3)
    puffs = [sphere('fl_smoke_%d' % i, 0.3, smoke, 10, 6) for i in range(6)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(puffs, lambda t, i: (sj[i][0] * (0.2 + 0.8 * t), sj[i][1] * (0.2 + 0.8 * t), 8.0 - 11.0 * t),
           smax=lambda t, i: (0.5 + 1.3 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: lightning converges from a ring of nodes into the spear, violet electric ring
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6, wobble=4)
    f = IMPACT0 + 4
    cx = 0.45
    T = Vector((cx - 0.3, 0, 0.55))
    NN = 8
    for i in range(NN):
        a = math.radians(i * 360 / NN + 10)
        R = 3.1
        hgt = 2.3 + 0.4 * (i % 2)
        pos = Vector((cx + R * math.cos(a), R * math.sin(a), hgt))
        nd = sphere('im_node_%d' % i, 0.16, white if i % 2 else cyan, 8, 5, loc=pos, ol=0)
        t0 = f + (i % 4)
        key(nd, IMPACT0, scale=0, alpha=1)
        key(nd, t0 - 2, scale=0, alpha=1)
        key(nd, t0 + 1, scale=1.3, alpha=1)
        key(nd, f + 22, scale=1.0, alpha=1)
        key(nd, f + 28, scale=0, alpha=0)
        tidy(nd, 'impact', interp='LINEAR')
        for k in range(2):
            b = bolt('im_bolt_%d_%d' % (i, k), (0, 0, 0), T - pos, white if k else (vio if i % 2 else cyan), 0.07 - 0.025 * k, 6, 0.32, seed=i * 5 + k * 17,
                     loc=pos, ol=0)
            tt = t0 + 1 + k
            key(b, IMPACT0, scale=0, alpha=1)
            key(b, tt, scale=0, alpha=1)
            key(b, tt + 1, scale=1, alpha=1)
            key(b, tt + 3, scale=1, alpha=1)
            key(b, tt + 4, scale=0, alpha=0)
            key(b, tt + 7, scale=1, alpha=1)
            key(b, tt + 9, scale=1, alpha=1)
            key(b, tt + 10, scale=0, alpha=0)
            key(b, tt + 13, scale=1, alpha=1)
            key(b, tt + 17, scale=0, alpha=0)
            tidy(b, 'impact', interp='LINEAR')
    core = sphere('im_core', 0.5, ghost('rc_core', '#e8c8ff', 2.4, 0.8, 1.2), 14, 8, loc=(T.x, 0, T.z))
    key(core, IMPACT0, scale=0, alpha=1)
    key(core, f + 2, scale=0.3, alpha=1)
    key(core, f + 8, scale=1.8, alpha=0.9)
    key(core, f + 16, scale=1.4, alpha=0.8)
    key(core, f + 26, scale=2.4, alpha=0)
    tidy(core, 'impact', interp='LINEAR')
    for k in range(3):
        rg = torus('im_ring_%d' % k, 0.6, 0.08 - 0.02 * k, (vio, white, cyan)[k], 40, 5, loc=(cx, 0, 0.06 + 0.02 * k))
        key(rg, IMPACT0, scale=0, alpha=1)
        key(rg, f + 5 + k * 3, scale=0.3, alpha=1)
        key(rg, f + 26 + k * 3, scale=5.2 - 0.6 * k, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
        ease_keys(rg)
    for i in range(6):
        a = math.radians(i * 60 + 25)
        L_ = rnd.uniform(1.4, 2.4)
        pts = zigzag((0, 0, 0.0), (L_ * math.cos(a), L_ * math.sin(a), 0.0), 4, 0.14, seed=i + 3)
        cr = tube('im_crack_%d' % i, pts, [0.0, 0.07, 0.07, 0.05, 0.0], vio, 4, smooth=False, ol=0, loc=(cx, 0, 0.04))
        key(cr, IMPACT0, scale=0, alpha=1)
        key(cr, f + 8 + i % 3, scale=(1, 1, 0.3), alpha=1)
        key(cr, f + 28, scale=(1, 1, 0.3), alpha=1)
        key(cr, IMPACT0 + 40, scale=0, alpha=0)
        tidy(cr, 'impact')
    for i in range(12):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.4)
        sp = sphere('im_spark_%d' % i, 0.07, (white, vio, cyan)[i % 3], 6, 4, ol=0)
        fly(sp, (cx, 0, 0.5), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.8, 3.0)), f + 6 + i % 6, 1.3)
    return True
