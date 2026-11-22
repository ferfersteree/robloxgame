from spearlib import *

NAME = 'SP_19_mangrove_root'
N = 19
BG = '#6f8460'        # swamp haze
GROUND = '#72814f'    # murky moss
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'root_arch': 'im_arch_0', 'root_spike': 'im_spike_0', 'mud_clump': 'im_mud_0', 'moss': 'im_moss_0'}
END = IMPACT0 + 44


def mats():
    return dict(
        root=toon('s19_root', '#7c502e', '#42291a', '#b88a56', spec=0.3),
        root_dk=toon('s19_root_dk', '#4a301f', '#26170f', '#7c5a3c', spec=0.3),
        root_lt=toon('s19_root_lt', '#c0955e', '#82592e', '#e8c48e', spec=0.3),
        moss=toon('s19_moss', '#62a03c', '#3a6a2a', '#a4d468', spec=0.2),
        moss_lt=toon('s19_moss_lt', '#9ad260', '#5a9a3a', '#d4f69a', spec=0.2),
        mud=toon('s19_mud', '#5b4632', '#33261a', '#8a6c4c', spec=0.1),
        orchid=toon('s19_orchid', '#ea6ab8', '#a8337e', '#ffa8dc', spec=0.5),
        teal=toon('s19_teal', '#7fe8c8', '#2e9a88', '#c8fff0', spec=0.9, emit=0.3),
    )


def pop(ob, t0, s1=1.0, grow=5, hold=IMPACT0 + 38):
    t0 = min(t0, END - 8)
    key(ob, IMPACT0, scale=0)
    if t0 > IMPACT0:
        key(ob, t0, scale=0)
    key(ob, t0 + grow, scale=s1)
    key(ob, max(hold, t0 + grow + 1), scale=s1)
    key(ob, END, scale=0)
    tidy(ob, 'impact')
    ease_keys(ob)


def expand(ob, t0, s0, s1, dur):
    key(ob, IMPACT0, scale=0, alpha=1)
    key(ob, t0, scale=s0, alpha=1)
    key(ob, min(t0 + dur, END), scale=s1, alpha=0)
    tidy(ob, 'impact', interp='LINEAR')
    ease_keys(ob)


def toss(c, p0, v, f, g=-0.03, zg=0.08):
    p0 = Vector(p0)
    key(c, IMPACT0, loc=p0, scale=0)
    key(c, f, loc=p0, scale=0.3)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= zg or t > 34
        if done:
            p.z = zg
        key(c, f + t, loc=p, scale=1, rot=(t * 30, t * 20, 0), interp='LINEAR')
        if done:
            break
    key(c, max(f + t + 2, IMPACT0 + 36), scale=1)
    key(c, END, scale=0)
    tidy(c, 'impact')


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    root, root_dk, root_lt, moss, moss_lt, mud, orchid, teal = (M[k] for k in (
        'root', 'root_dk', 'root_lt', 'moss', 'moss_lt', 'mud', 'orchid', 'teal'))
    # ---- tail: knot with four stilt roots
    sphere('tail_knot', 0.24, root_dk, 10, 6, loc=(0, 0, 0.62), scale=(1, 1, 0.9))
    for i in range(4):
        a = math.radians(i * 90 + 30)
        ca, sa = math.cos(a), math.sin(a)
        tube('tail_root_%d' % i, [(0.12 * ca, 0.12 * sa, 0.9), (0.34 * ca, 0.34 * sa, 0.62), (0.5 * ca, 0.5 * sa, 0.28), (0.55 * ca, 0.55 * sa, 0.03)],
             [0.09, 0.075, 0.05, 0.0], root, 6)
    torus('tail_ring', 0.2, 0.04, moss, 14, 6, loc=(0, 0, 1.1))
    # ---- shaft: straight core (bare grip) with two twisting roots wound around it above and below
    rod('shaft_lo', 0.155, 0.8, 3.3, root_dk, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.3, root_dk, r1=0.14)
    coil('root_lo_a', 0.2, 0.06, 1.2, 1.9, 2, root, segs=5)
    coil('root_lo_b', 0.2, 0.05, 1.2, 1.9, 2, root_lt, segs=5, phase=math.pi)
    torus('root_lo_cap', 0.18, 0.04, moss, 14, 6, loc=(0, 0, 1.94))
    coil('root_hi_a', 0.2, 0.06, 3.15, 5.9, 3, root, segs=5)
    coil('root_hi_b', 0.2, 0.05, 3.15, 5.9, 3, root_lt, segs=5, phase=math.pi)
    torus('root_hi_cap', 0.18, 0.04, moss, 14, 6, loc=(0, 0, 3.06))
    for i in range(6):
        a = i * 1.7
        z = 1.15 + i * 0.12 if i < 3 else 3.5 + (i - 3) * 0.9
        rock('moss_%d' % i, 0.1, moss if i % 2 else moss_lt, seed=i, sub=1, rough=0.25, flat=True,
             loc=(0.24 * math.cos(a), 0.24 * math.sin(a), z), scale=(1, 1, 0.7), ol=0.012)
    # ---- socket: gnarled root knot with a pink orchid
    lathe('socket', [(6.0, 0.15), (6.15, 0.26), (6.4, 0.3), (6.7, 0.26), (6.85, 0.18), (6.85, 0)], root_dk, 12)
    sphere('socket_knot_a', 0.12, root, 8, 5, loc=(0.28, 0.08, 6.4), ol=0.012)
    sphere('socket_knot_b', 0.1, root, 8, 5, loc=(-0.26, -0.1, 6.65), ol=0.012)
    torus('socket_band', 0.28, 0.045, moss, 14, 6, loc=(0, 0, 6.2))
    star('orchid', 0.2, 0.09, 5, 0.06, orchid, loc=(0.3, -0.16, 6.62), rot=(70, 0, 20), ol=0.015)
    sphere('orchid_heart', 0.05, teal, 7, 4, loc=(0.3, -0.2, 6.62), ol=0.012)
    # ---- the root blade: broad wooden leaf with grain ribs, twisting roots and moss
    blade('blade_root', [(0, 6.7), (0.4, 7.0), (0.62, 7.7), (0.5, 8.5), (0.2, 9.1), (0, TIP), (-0.2, 9.1), (-0.5, 8.5), (-0.62, 7.7), (-0.4, 7.0)],
          0.15, root_lt)
    for s in (-1, 1):
        nm = 'F' if s > 0 else 'B'
        tube('rib_mid_' + nm, [(0.0, s * 0.17, 6.9), (0.1, s * 0.18, 7.8), (0.05, s * 0.17, 8.7), (0.0, s * 0.12, TIP - 0.2)], [0.07, 0.06, 0.045, 0.0], root, 6)
        tube('rib_side_' + nm, [(0.3, s * 0.15, 7.1), (0.42, s * 0.16, 7.7), (0.32, s * 0.15, 8.3)], [0.05, 0.05, 0.0], root_dk, 6)
    coil('twist_a', 0.72, 0.06, 6.6, 8.7, 1.5, root_dk, segs=5, R1=0.5)
    coil('twist_b', 0.72, 0.05, 6.6, 8.7, 1.5, root, segs=5, R1=0.5, phase=math.pi)
    tube('tendril_a', [(0.5, 0, 7.2), (0.9, 0, 7.5), (1.05, 0, 8.0), (0.9, 0, 8.3), (0.72, 0, 8.2)], [0.06, 0.055, 0.045, 0.035, 0.0], root, 6)
    tube('tendril_b', [(-0.5, 0, 7.6), (-0.85, 0, 7.9), (-0.95, 0, 8.4)], [0.055, 0.045, 0.0], root, 6)
    for i, (x, y, z) in enumerate(((0.3, 0.19, 7.4), (-0.25, -0.19, 8.1), (0.22, 0.19, 8.6))):
        rock('blade_moss_%d' % i, 0.11, moss_lt if i % 2 else moss, seed=i + 10, sub=1, rough=0.25, flat=True, loc=(x, y, z), scale=(1, 0.8, 0.7), ol=0.012)
    # ---- charm: three hanging mangrove pods
    for i in range(3):
        a = i * 2.1 + 0.4
        x, y = 0.26 * math.cos(a), 0.26 * math.sin(a)
        tube('pod_cord_%d' % i, [(x * 0.7, y * 0.7, 6.0), (x, y, 5.75)], 0.018, root_dk, 4)
        cone('pod_%d' % i, 0.06, 0.45, moss if i % 2 else teal, 6, loc=(x, y, 5.75), rot=(180, 0, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1919)
    dust = ghost('s19_dust', '#b49a74', 1.0, 0.85, 1.1)
    dust_dk = ghost('s19_dust_dk', '#6e5638', 1.0, 0.85, 1.1)
    spore = glow('s19_spore', '#9affc8', 2.2)
    glint = glow('s19_glint', '#e8ffd0', 2.4)
    # ---------------- idle: spores and glints
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.55, 1.0)
        sphere('idle_spore_%d' % i, rnd.uniform(0.05, 0.09), spore, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 0.9), -0.3, 7.4 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: moss leaf scraps, wood chips, mud puffs, rings
    fx('flight')
    leaves = [leaf('fl_leaf_%d' % i, 0.34, 0.15, M['moss'] if i % 2 else M['moss_lt'], 0.03, 5, ol=0.012) for i in range(10)]
    jl = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(leaves, lambda t, i: (jl[i][0] * (0.3 + 1.0 * t), jl[i][1] * (0.3 + 1.0 * t), 8.4 - 12.5 * t),
           smax=1.1, spin=lambda t, i: (jl[i][2] + 360 * t, 240 * t, jl[i][2] * 0.5))
    chips = [rock('fl_chip_%d' % i, 0.09, M['root'] if i % 2 else M['root_dk'], seed=i, sub=1, rough=0.22, flat=True) for i in range(8)]
    jc = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(chips, lambda t, i: (jc[i][0] * (0.3 + 0.9 * t), jc[i][1] * (0.3 + 0.9 * t), 8.4 - 13.0 * t),
           smax=1.0, spin=lambda t, i: (jc[i][2] + 720 * t, 540 * t, 0))
    puffs = [sphere('fl_puff_%d' % i, 0.34, dust if i % 3 else dust_dk, 12, 7) for i in range(8)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.9 * t), jp[i][1] * (0.15 + 0.9 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.45, 0.035, glow('s19_airring', '#b8ffd8', 1.6), 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: arching roots burst out, mud splashes, brown dust
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s19_flash', '#e8d4a8', 1.8, 0.65, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.8)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    mr = torus('im_mudring', 0.6, 0.12, M['mud'], 24, 6, loc=(cx, 0, 0.02))
    key(mr, IMPACT0, scale=0)
    key(mr, f, scale=0)
    key(mr, f + 6, scale=(3.2, 3.2, 0.5))
    key(mr, IMPACT0 + 36, scale=(3.6, 3.6, 0.3))
    key(mr, END, scale=0)
    tidy(mr, 'impact')
    ease_keys(mr)
    # six arching prop-roots (half-ellipse hoops) and six thrusting spike roots
    ap = []
    for k in range(9):
        ph = math.pi * k / 8
        ap.append((-math.cos(ph), 0, math.sin(ph)))
    arad = [0.0] + [0.13] * 7 + [0.0]
    for i, (ang, rr, R, hgt) in enumerate(((-120, 1.5, 0.7, 1.3), (-70, 1.9, 0.8, 1.6), (-20, 1.5, 0.7, 1.2), (30, 1.9, 0.9, 1.5), (80, 1.5, 0.7, 1.3), (130, 1.9, 0.8, 1.4))):
        a = math.radians(ang)
        pts = [(R * p[0], 0, hgt * p[2]) for p in ap]
        ar = tube('im_arch_%d' % i, pts, arad, M['root'] if i % 2 else M['root_dk'], 6, loc=(cx + rr * math.cos(a), rr * math.sin(a), 0.0),
                  rot=(0, 0, ang + 90))
        t0 = f + i
        key(ar, IMPACT0, scale=0)
        key(ar, t0, scale=0)
        key(ar, t0 + 4, scale=1.2)
        key(ar, t0 + 7, scale=1.0)
        key(ar, IMPACT0 + 38, scale=1.0)
        key(ar, END, scale=0)
        tidy(ar, 'impact')
        ease_keys(ar)
    sp0 = [(0, 0, 0), (0.15, 0, 0.6), (0.4, 0, 1.2), (0.8, 0, 1.6)]
    for i in range(6):
        ang = -110 + i * 44 + rnd.uniform(-8, 8)
        a = math.radians(ang)
        rr = 0.9
        sk = tube('im_spike_%d' % i, sp0, [0.14, 0.1, 0.07, 0.0], M['root_lt'], 6, loc=(cx + rr * math.cos(a), rr * math.sin(a), 0.0), rot=(0, 0, ang))
        pop(sk, f + 1 + i, 1.0, grow=5)
    for i in range(6):
        a = math.radians(rnd.uniform(-140, 140))
        rr = rnd.uniform(2.0, 2.6)
        mo = rock('im_moss_%d' % i, 0.16, M['moss'] if i % 2 else M['moss_lt'], seed=i + 20, sub=1, rough=0.25, flat=True,
                  loc=(cx + rr * math.cos(a), rr * math.sin(a), 0.05), scale=(1, 1, 0.6))
        pop(mo, f + 4 + i, 1.0, grow=4)
    for i in range(16):
        a = math.radians(rnd.uniform(-150, 150))
        sp = rnd.uniform(0.05, 0.12)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.26, 0.42)))
        c = rock('im_mud_%d' % i, rnd.uniform(0.1, 0.2), M['mud'] if i % 3 else M['root_dk'], seed=i + 30, sub=1, rough=0.3, flat=True)
        toss(c, (cx, 0, 0.15), v, f)
    for i in range(10):
        a = math.radians(rnd.uniform(-150, 150))
        sp = rnd.uniform(0.03, 0.08)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.3, 0.45)))
        dr = sphere('im_splash_%d' % i, rnd.uniform(0.05, 0.09), M['mud'], 7, 4)
        toss(dr, (cx, 0, 0.2), v, f, zg=0.06)
    for i in range(10):
        a = math.radians(i * 36 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.3, 2.4)
        p = sphere('im_dust_%d' % i, 0.32, dust if i % 3 else dust_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.8))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.3, 1.9), alpha=0.9)
        key(p, END, loc=(end[0], end[1], end[2] + 0.4), scale=rnd.uniform(2.0, 2.6), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
