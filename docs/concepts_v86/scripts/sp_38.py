from spearlib import *

NAME = 'SP_38_void_scissors'
N = 38
BG = '#4a3868'        # void dusk
GROUND = '#34284c'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'slash': 'im_slash_a', 'void_bubble': 'im_void', 'shard': 'im_frag_0', 'crescent': 'fl_arc_0'}


def mats():
    return dict(
        blk=toon('vs_blk', '#1c1626', '#0a0710', '#5b4a78', spec=1.0, rim=0.7, rimcol='#c070ff'),
        steel=toon('vs_steel', '#cfcbe0', '#6a6590', '#ffffff', spec=1.0, rimcol='#d6a0ff'),
        plum=toon('vs_plum', '#6a2aa8', '#34126a', '#a460e8', emit=0.2),
        silver=toon('vs_silver', '#e4e2f2', '#8a86aa', '#ffffff', spec=1.0),
        vio=glow('vs_vio', '#b45cff', 3.2),
        pink=glow('vs_pink', '#ff6af0', 3.4),
        hot=glow('vs_hot', '#f2d8ff', 3.6),
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


def kris(L, W):
    """curved scissor-blade outline (x, z), base at z=0, bulging towards +x"""
    return [(0.0, 0.0), (W * 0.8, L * 0.2), (W, L * 0.55), (W * 0.7, L * 0.85), (W * 0.2, L), (-W * 0.15, L * 0.93),
            (-W * 0.2, L * 0.55), (-W * 0.2, L * 0.2)]


def mirror(pts):
    return [(-x, z) for (x, z) in pts][::-1]


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    blk, steel, plum, silver, vio, pink, hot = (M[k] for k in ('blk', 'steel', 'plum', 'silver', 'vio', 'pink', 'hot'))
    # ---- tail: black pommel with a violet gem and two mini-blades
    lathe('tail_cap', [(0.0, 0.0), (0.0, 0.1), (0.18, 0.24), (0.5, 0.22), (0.62, 0.15), (0.62, 0.0)], blk, 12)
    sphere('tail_gem', 0.12, vio, 8, 5, loc=(0, 0, 0.14), ol=0)
    for s in (-1, 1):
        blade('tail_blade_' + 'ab'[s > 0], kris(0.7, 0.14) if s > 0 else mirror(kris(0.7, 0.14)), 0.04, steel,
              loc=(s * 0.08, 0, 0.8), rot=(0, 180 - s * 12, 0), ol=0.015)
    torus('tail_ring', 0.2, 0.045, silver, 12, 5, loc=(0, 0, 0.66))
    # ---- shaft: black glass, silver rings, violet seams
    shaft_parts(blk, plum, silver, vio)
    for i in range(3):
        a = i * 2.2
        sphere('shaft_stud_%d' % i, 0.06, vio, 7, 4, loc=(0.15 * math.cos(a), 0.15 * math.sin(a), 5.1 + i * 0.4), ol=0)
    # ---- socket and pivot
    lathe('socket', [(6.3, 0.14), (6.45, 0.22), (6.7, 0.3), (6.9, 0.26), (7.05, 0.0)], blk, 12)
    torus('socket_rim', 0.3, 0.055, silver, 14, 5, loc=(0, 0, 6.55))
    cyl('pivot_disc', 0.36, 0.2, silver, 14, axis='Y', loc=(0, 0, 7.0))
    cyl('pivot_core', 0.2, 0.34, blk, 12, axis='Y', loc=(0, 0, 7.0), ol=0.015)
    sphere('pivot_gem', 0.14, pink, 8, 5, loc=(0, -0.2, 7.0), ol=0)
    # ---- the two open blades (scissors) with glowing edges, splayed around the void
    sh = kris(TIP - 7.0, 0.55)
    for s in (1, -1):
        nm = 'ab'[s > 0]
        ol_ = sh if s > 0 else mirror(sh)
        blade('blade_' + nm, ol_, 0.12, steel, loc=(s * 0.12, 0.05 * s, 7.0), rot=(0, s * 15, 0))
        ridge = [(x * 0.45, 0.25 + z * 0.85) for (x, z) in ol_]
        blade('blade_edge_' + nm, ridge, 0.15, vio, loc=(s * 0.12, 0.05 * s, 7.0), rot=(0, s * 15, 0), ol=0)
        torus('blade_guard_' + nm, 0.2, 0.05, plum, 12, 5, loc=(s * 0.16, 0, 7.35), rot=(0, 90 + s * 15, 0), scale=(1, 1.3, 1), ol=0.015)
    # ---- the void: dark orb between the blades, ringed and orbited by detached pieces
    sphere('void_orb', 0.5, ghost('vs_void', '#0b0514', 0.7, 0.9, 0.7), 14, 8, loc=(0, 0, 8.3), scale=(1.0, 1.0, 1.3))
    torus('void_ring', 0.72, 0.045, vio, 22, 4, loc=(0, 0, 8.3), rot=(90, 0, 0), ol=0)
    torus('void_ring_b', 0.58, 0.035, pink, 18, 4, loc=(0, 0, 8.3), rot=(90, 0, 55), ol=0)
    for i in range(6):
        a = math.radians(i * 60 + 10)
        crystal('float_shard_%d' % i, 0.07, 0.45, blk if i % 2 else plum, 5, 0.35, 0.6, both=True,
                loc=(0.95 * math.cos(a), 0.95 * math.sin(a), 7.5 + 0.28 * i), rot=aim((math.cos(a) * 0.5, math.sin(a) * 0.5, 1), i * 30), ol=0.015)
    for i in range(3):
        a = math.radians(i * 120 + 70)
        sphere('float_orb_%d' % i, 0.1, hot, 8, 5, loc=(0.6 * math.cos(a), 0.6 * math.sin(a), 8.3 + 0.3 * (i - 1)), ol=0)
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
    rnd = random.Random(3838)
    smoke = ghost('vs_smoke', '#4a1f78', 1.1, 0.85, 1.0)
    aura = ghost('vs_aura', '#a050f0', 1.2, 0.05, 1.8)
    sp = glow('vs_spark', '#f0d0ff', 3.2)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.2), scale=(1.5, 0.9, 1.7))
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.2)
        sphere('idle_mote_%d' % i, rnd.uniform(0.04, 0.08), sp if i % 2 else M['vio'], 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.6)))
    for i in range(2):
        star('idle_glint_%d' % i, 0.15, 0.035, 4, 0.02, sp, loc=(rnd.choice((-1, 1)) * 0.7, -0.3, 8.0 + i * 0.8), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    arcs = []
    for i in range(8):
        pts = [(0.5 * math.cos(math.radians(a)), 0.5 * math.sin(math.radians(a)), 0) for a in range(-80, 81, 20)]
        arcs.append(tube('fl_arc_%d' % i, pts, [0.0, 0.05, 0.08, 0.09, 0.08, 0.06, 0.05, 0.03, 0.0][:len(pts)], M['vio'] if i % 2 else M['pink'], 5, ol=0))
    aj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(arcs, lambda t, i: (aj[i][0] * (0.3 + 0.9 * t), aj[i][1] * (0.3 + 0.9 * t), 8.8 - 12.0 * t), smax=1.3,
           spin=lambda t, i: (90 + aj[i][2], aj[i][2] + 400 * t, 0))
    sh = [crystal('fl_shard_%d' % i, 0.07, 0.45, M['blk'] if i % 2 else M['plum'], 5, 0.35, 0.6, both=True, ol=0.014) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(sh, lambda t, i: (sj[i][0] * (0.35 + 1.0 * t), sj[i][1] * (0.35 + 1.0 * t), 8.6 - 12.0 * t), smax=1.1,
           spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    puffs = [sphere('fl_smoke_%d' % i, 0.32, smoke, 10, 6) for i in range(7)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(7)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.8 * t), pj[i][1] * (0.2 + 0.8 * t), 8.0 - 11.0 * t),
           smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, M['vio'], 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: X slash cut, swelling void bubble that pops into shards
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6, wobble=4)
    f = IMPACT0 + 4
    cx = 0.45
    for k, ang in enumerate((38, -38)):
        sl = box('im_slash_' + 'ab'[k], (3.6, 0.2, 0.05), M['vio'], bev=0.02, bsegs=1, loc=(cx, 0, 0.04), rot=(0, 0, ang), ol=0)
        core = box('im_slash_core_' + 'ab'[k], (3.4, 0.07, 0.07), M['hot'], bev=0.02, bsegs=1, loc=(cx, 0, 0.06), rot=(0, 0, ang), ol=0)
        for o in (sl, core):
            key(o, IMPACT0, scale=0, alpha=1)
            key(o, f + 2 + k * 3, scale=(0.1, 1, 1), alpha=1)
            key(o, f + 6 + k * 3, scale=(1.0, 1.4, 1), alpha=1)
            key(o, f + 24, scale=(1.0, 1.0, 1), alpha=1)
            key(o, IMPACT0 + 44, scale=(1.0, 0.1, 1), alpha=0)
            tidy(o, 'impact')
            ease_keys(o)
    void = sphere('im_void', 0.6, ghost('vs_bubble', '#c070ff', 2.0, 0.85, 1.6, edge=True), 16, 8, loc=(cx, 0, 0.9))
    key(void, IMPACT0, scale=0, alpha=1)
    key(void, f + 2, scale=0.2, alpha=1)
    key(void, f + 14, scale=2.0, alpha=1)
    key(void, f + 20, scale=2.3, alpha=1)
    key(void, f + 22, scale=2.9, alpha=0.2)
    key(void, f + 24, scale=3.3, alpha=0)
    tidy(void, 'impact', interp='LINEAR')
    core_ = sphere('im_void_core', 0.5, ghost('vs_core', '#0a0412', 0.7, 0.9, 0.7), 14, 8, loc=(cx, 0, 0.9))
    key(core_, IMPACT0, scale=0, alpha=1)
    key(core_, f + 2, scale=0.2, alpha=1)
    key(core_, f + 14, scale=1.7, alpha=1)
    key(core_, f + 20, scale=1.9, alpha=1)
    key(core_, f + 22, scale=0.2, alpha=0)
    tidy(core_, 'impact', interp='LINEAR')
    for i in range(12):
        a = math.radians(i * 30 + rnd.uniform(-8, 8))
        r = rnd.uniform(1.4, 3.0)
        fr = crystal('im_frag_%d' % i, 0.1, 0.5, M['blk'] if i % 2 else M['plum'], 5, 0.35, 0.6, both=True, ol=0.016)
        p0 = (cx, 0, 0.9)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.3, 2.4))
        key(fr, IMPACT0, loc=p0, scale=0, rot=(0, 0, 0))
        key(fr, f + 21, loc=p0, scale=0, rot=(0, 0, 0))
        key(fr, f + 23, loc=p0, scale=1.1, rot=(0, 0, 0))
        key(fr, f + 38, loc=p1, scale=0.9, rot=(rnd.uniform(200, 500), rnd.uniform(200, 500), 0))
        key(fr, IMPACT0 + 44, loc=p1, scale=0, rot=(rnd.uniform(500, 600), 300, 0))
        tidy(fr, 'impact')
        ease_keys(fr)
    ring = torus('im_pop_ring', 0.6, 0.07, M['pink'], 36, 5, loc=(cx, 0, 0.1))
    key(ring, IMPACT0, scale=0, alpha=1)
    key(ring, f + 21, scale=0.3, alpha=1)
    key(ring, f + 39, scale=5.0, alpha=0)
    tidy(ring, 'impact', interp='LINEAR')
    ease_keys(ring)
    for i in range(6):
        a = math.radians(i * 60 + 20)
        pts = [(0.5 * math.cos(math.radians(b)), 0.5 * math.sin(math.radians(b)), 0) for b in range(-80, 81, 20)]
        ac = tube('im_arc_%d' % i, pts, [0.0, 0.05, 0.08, 0.09, 0.08, 0.06, 0.05, 0.03, 0.0][:len(pts)], M['pink'] if i % 2 else M['vio'], 5, ol=0,
                  loc=(cx, 0, 0.1), rot=(0, 0, math.degrees(a)))
        key(ac, IMPACT0, scale=0, alpha=1, loc=(cx, 0, 0.1))
        key(ac, f + 4 + i % 3, scale=0.6, alpha=1, loc=(cx, 0, 0.1))
        key(ac, IMPACT0 + 44, scale=2.6, alpha=0, loc=(cx + 2.6 * math.cos(a), 2.6 * math.sin(a), 0.1))
        tidy(ac, 'impact')
        ease_keys(ac)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.8)
        sm = sphere('im_smoke_%d' % i, 0.4, smoke, 12, 7)
        fly(sm, (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.6, 2.8)), f + 20 + i % 3, 1.8)
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.2)
        sp_ = sphere('im_spark_%d' % i, 0.08, sp, 6, 4, ol=0)
        fly(sp_, (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.1), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.0, 3.0)), f + 2 + i, 1.2)
    return True
