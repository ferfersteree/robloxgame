from spearlib import *

NAME = 'SP_22_thunder_split'
N = 22
BG = '#4a5490'        # thunder sky
GROUND = '#6c7590'    # storm slate
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'crack': 'im_crack_0', 'crack_core': 'im_core_0', 'arc': 'im_arc_0', 'shock_ring': 'im_shock', 'zig': 'fl_zig_0'}
END = IMPACT0 + 44


def mats():
    return dict(
        yellow=toon('s22_yellow', '#ffd93a', '#c28a12', '#fff3a0', spec=1.0, emit=0.5, rimcol='#ffffff'),
        navy=toon('s22_navy', '#27306e', '#121838', '#5560b4', spec=0.8, rim=0.6, rimcol='#8ea2ff'),
        navy_lt=toon('s22_navy_lt', '#4452a8', '#222a64', '#8a98e8', spec=0.8),
        steel=toon('s22_steel', '#a8b0cc', '#5e6686', '#eef2ff', spec=1.0),
        cream=toon('s22_cream', '#f4efd4', '#bdb48e', '#ffffff'),
        zap=glow('s22_zap', '#fff27a', 2.2),
        zap_bl=glow('s22_zap_bl', '#7a9cff', 2.2),
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


def flicker(ob, t0, dur=13):
    key(ob, IMPACT0, scale=0, alpha=1)
    key(ob, t0, scale=0, alpha=1)
    key(ob, t0 + 1, scale=1, alpha=1)
    key(ob, t0 + 3, scale=1, alpha=0.2)
    key(ob, t0 + 4, scale=1, alpha=1)
    key(ob, t0 + 7, scale=1, alpha=0.9)
    key(ob, t0 + dur - 1, scale=1, alpha=0.1)
    key(ob, t0 + dur, scale=0, alpha=0)
    tidy(ob, 'impact', interp='LINEAR')


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


def stroke(nm, p0, p1, w0, w1, th, mat, **kw):
    """thick straight stroke (blade) from p0 to p1 in the XZ plane; w = half widths"""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    L_ = math.hypot(dx, dz)
    nx, nz = -dz / L_, dx / L_
    pts = [(p0[0] + nx * w0, p0[1] + nz * w0), (p1[0] + nx * w1, p1[1] + nz * w1),
           (p1[0] - nx * w1, p1[1] - nz * w1), (p0[0] - nx * w0, p0[1] - nz * w0)]
    return blade(nm, pts, th, mat, **kw)


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    yellow, navy, navy_lt, steel, cream, zap, zap_bl = (M[k] for k in ('yellow', 'navy', 'navy_lt', 'steel', 'cream', 'zap', 'zap_bl'))
    # ---- tail: small lightning finial on a navy knob
    sphere('tail_knob', 0.22, navy, 10, 6, loc=(0, 0, 0.55), scale=(1, 1, 0.9))
    stroke('tail_zig_a', (0.0, 0.05), (0.18, 0.4), 0.08, 0.07, 0.07, yellow, ol=0.015)
    stroke('tail_zig_b', (0.18, 0.4), (-0.12, 0.62), 0.07, 0.06, 0.07, yellow, ol=0.015)
    torus('tail_ring', 0.2, 0.045, steel, 14, 6, loc=(0, 0, 0.9))
    # ---- shaft: navy with yellow chevrons
    rod('shaft_lo', 0.155, 0.7, 3.3, navy, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, navy, r1=0.14)
    coil('wrap_lo', 0.178, 0.03, 1.2, 1.7, 4, navy_lt, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, yellow, 14, 6, loc=(0, 0, 1.94))
    torus('wrap_lo_cap2', 0.17, 0.035, yellow, 14, 6, loc=(0, 0, 1.08))
    coil('wrap_hi', 0.176, 0.03, 3.08, 3.62, 4, navy_lt, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, yellow, 14, 6, loc=(0, 0, 3.06))
    bolt('chev_a', (0.19, 0.05, 4.0), (0.19, 0.05, 4.9), zap, r=0.045, n=5, amp=0.07, seed=11, ol=0)
    bolt('chev_b', (-0.18, -0.07, 4.2), (-0.18, -0.07, 5.2), zap, r=0.045, n=5, amp=0.07, seed=12, ol=0)
    bolt('chev_c', (0.05, -0.19, 1.3), (0.05, -0.19, 1.8), zap, r=0.04, n=4, amp=0.05, seed=13, ol=0)
    for i, z in enumerate((5.3, 5.5, 5.7)):
        torus('band_%d' % i, 0.16, 0.03 if i != 1 else 0.042, (steel, yellow, steel)[i], 14, 5, loc=(0, 0, z), ol=0.015)
    # ---- navy socket with yellow lashing
    lathe('socket', [(6.1, 0.15), (6.25, 0.25), (6.5, 0.3), (6.8, 0.28), (6.9, 0.2), (6.9, 0)], navy, 12)
    torus('socket_band', 0.28, 0.045, yellow, 14, 6, loc=(0, 0, 6.28))
    coil('socket_lash', 0.31, 0.03, 6.42, 6.8, 3, yellow, segs=5)
    # ---- open zigzag blade: four thick strokes (yellow) in a navy thorn cage
    P = [(0.0, 6.85), (0.62, 7.7), (-0.45, 8.15), (0.38, 8.8), (0.0, TIP - 0.015)]
    W = [0.2, 0.26, 0.26, 0.22, 0.02]
    for i in range(4):
        stroke('zig_%d' % i, P[i], P[i + 1], W[i], W[i + 1], 0.15, yellow)
    for i in (1, 2, 3):
        sphere('zig_knuckle_%d' % i, 0.2 - 0.02 * i, yellow, 8, 5, loc=(P[i][0], 0, P[i][1]), scale=(1, 0.8, 1), ol=0.015)
    for s, nm in ((0.17, 'F'), (-0.17, 'B')):
        tube('zig_core_' + nm, [(P[0][0], s, P[0][1] + 0.1), (P[1][0], s, P[1][1]), (P[2][0], s, P[2][1]), (P[3][0], s, P[3][1]), (P[4][0], s, P[4][1] - 0.1)],
             [0.0, 0.05, 0.05, 0.045, 0.0], zap, 5, ol=0)
    tube('cage_R', [(0.4, 0, 6.9), (0.95, 0, 7.4), (1.05, 0, 8.2), (0.75, 0, 8.9)], [0.13, 0.12, 0.09, 0.0], navy, 8, scale=(1, 0.7, 1))
    tube('cage_L', [(-0.4, 0, 6.9), (-0.95, 0, 7.2), (-0.95, 0, 7.9), (-0.7, 0, 8.55)], [0.13, 0.12, 0.09, 0.0], navy, 8, scale=(1, 0.7, 1))
    torus('cage_ring_R', 0.14, 0.035, steel, 10, 5, loc=(0.9, 0, 7.3), rot=(0, 55, 0), ol=0.015)
    torus('cage_ring_L', 0.14, 0.035, steel, 10, 5, loc=(-0.9, 0, 7.15), rot=(0, -55, 0), ol=0.015)
    sphere('cage_gem_R', 0.08, zap_bl, 8, 5, loc=(1.0, 0.1, 7.9), ol=0)
    sphere('cage_gem_L', 0.08, zap_bl, 8, 5, loc=(-0.93, 0.1, 7.6), ol=0)
    # ---- charm: steel feather-tag and cream bead
    tube('charm_cord', [(0.2, 0.03, 6.05), (0.34, 0.06, 5.75), (0.4, 0.07, 5.5)], 0.022, navy_lt, 5)
    sphere('charm_bead', 0.065, cream, 8, 5, loc=(0.34, 0.065, 5.78), ol=0.012)
    stroke('charm_tag', (0.4, 5.55), (0.4, 5.1), 0.06, 0.05, 0.03, steel, ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2222)
    zap = M['zap']
    zap_bl = M['zap_bl']
    smoke = ghost('s22_smoke', '#68709a', 0.8, 0.85, 1.0)
    # ---------------- idle: crackle sparks around the zigzag
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.0)
        sphere('idle_spark_%d' % i, rnd.uniform(0.04, 0.08), zap if i % 2 else zap_bl, 7, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.2, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, zap, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 0.9), -0.3, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: zigzag bolts, sparks, rings, glints
    fx('flight')
    zz = [bolt('fl_zig_%d' % i, (0, 0, 0), (0.0, 0, 0.6), zap if i % 2 else zap_bl, r=0.05, n=4, amp=0.11, seed=i) for i in range(10)]
    jz = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(zz, lambda t, i: (jz[i][0] * (0.3 + 1.0 * t), jz[i][1] * (0.3 + 1.0 * t), 8.8 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (jz[i][2] + 360 * t, 180 * t, 0))
    sparks = [sphere('fl_spark_%d' % i, 0.06, zap if i % 2 else zap_bl, 6, 4) for i in range(12)]
    jk = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(sparks, lambda t, i: (jk[i][0] * (0.3 + 1.5 * t), jk[i][1] * (0.3 + 1.5 * t), 8.6 - 13.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.45, 0.04, zap_bl if i % 2 else zap, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    gl = [star('fl_glint_%d' % i, 0.14, 0.035, 4, 0.02, zap, rot=(90, 0, 0)) for i in range(5)]
    jg = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(5)]
    stream(gl, lambda t, i: (jg[i][0] * (0.3 + 0.8 * t), jg[i][1] * (0.3 + 0.8 * t), 9.0 - 11.0 * t), smax=1.0)
    # ---------------- impact: a glowing zigzag crack splits the ground forward, bolt arcs jump along it
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s22_flash', '#fff8c8', 2.2, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.2, alpha=0.8)
    key(flash, f + 10, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    sh = torus('im_shock', 0.5, 0.05, zap, 32, 5, loc=(cx, 0, 0.06))
    expand(sh, f, 0.3, 5.0, 12)
    # main crack (forward, +X) and two side branches; crust is navy, core glows
    paths = []
    for i, (ang, L_) in enumerate(((0, 3.1), (-32, 2.0), (32, 2.0))):
        a = math.radians(ang)
        pts = zigzag((0, 0, 0), (L_, 0, 0), 7, 0.3, seed=i + 21)
        for p in pts:
            p.z = 0.0
        paths.append(pts)
        n = len(pts)
        crad = [0.2 * (1 - 0.7 * k / (n - 1)) for k in range(n)]
        cr = tube('im_crack_%d' % i, pts, crad, M['navy'], 4, smooth=False, ol=0, loc=(cx, 0, 0.02), rot=(0, 0, ang))
        co = tube('im_core_%d' % i, pts, [r_ * 0.45 for r_ in crad], zap, 4, smooth=False, ol=0, loc=(cx, 0, 0.06), rot=(0, 0, ang))
        t0 = f + i * 2
        # the crack sweeps outward along its own length (scale about the contact point)
        key(cr, IMPACT0, scale=0)
        key(cr, t0, scale=(0.05, 1, 0.3))
        key(cr, t0 + 8, scale=(1, 1, 0.3))
        key(cr, IMPACT0 + 38, scale=(1, 1, 0.3))
        key(cr, END, scale=0)
        tidy(cr, 'impact')
        key(co, IMPACT0, scale=0, alpha=1)
        key(co, t0, scale=(0.05, 1, 0.3), alpha=1)
        key(co, t0 + 8, scale=(1, 1, 0.3), alpha=1)
        key(co, IMPACT0 + 30, scale=(1, 1, 0.3), alpha=1)
        key(co, END, scale=(1, 1, 0.3), alpha=0)
        tidy(co, 'impact')
    tf = sphere('im_tipflash', 0.18, ghost('s22_tipflash', '#fff8c8', 2.4, 0.85, 1.0), 10, 6, loc=(cx, 0, 0.2))
    key(tf, IMPACT0, scale=0, alpha=1)
    key(tf, f, loc=(cx, 0, 0.2), scale=1.0, alpha=1)
    key(tf, f + 8, loc=(cx + 3.1, 0, 0.2), scale=1.4, alpha=1)
    key(tf, f + 13, loc=(cx + 3.1, 0, 0.2), scale=0, alpha=0)
    tidy(tf, 'impact', interp='LINEAR')
    # bolt arcs hop along the main crack, one after another
    main = paths[0]
    for i in range(6):
        k0 = i
        k1 = min(i + 2, len(main) - 1)
        a = Vector((cx + main[k0][0], main[k0][1], 0.1))
        b = Vector((cx + main[k1][0], main[k1][1], 0.1))
        pts = zigzag(a, b, 5, 0.1, seed=i + 40)
        for j, p in enumerate(pts):
            p.z = 0.1 + 0.55 * math.sin(math.pi * j / (len(pts) - 1))
        pts = [p - a for p in pts]
        ar = tube('im_arc_%d' % i, pts, [0.0] + [0.05] * (len(pts) - 2) + [0.0], zap if i % 2 == 0 else M['zap_bl'], 4, smooth=False, ol=0, loc=a)
        flicker(ar, f + 2 + i * 2, 11)
    g = -0.03
    for i in range(18):
        k = rnd.randint(0, len(main) - 1)
        p0 = Vector((cx + main[k][0], main[k][1], 0.15))
        a = math.radians(rnd.uniform(0, 360))
        sp = rnd.uniform(0.02, 0.06)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.2, 0.36)))
        sk = sphere('im_spark_%d' % i, rnd.uniform(0.04, 0.08), zap if i % 2 else zap_bl, 6, 4)
        t00 = f + 2 + k
        key(sk, IMPACT0, loc=p0, scale=0)
        key(sk, t00, loc=p0, scale=0.3)
        t = 0
        while True:
            t += 3
            p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
            if p.z <= 0.08 or t00 + t >= END - 1:
                key(sk, min(t00 + t, END), loc=Vector((p.x, p.y, max(p.z, 0.08))), scale=0)
                break
            key(sk, t00 + t, loc=p, scale=1.0, interp='LINEAR')
        tidy(sk, 'impact')
    for i in range(8):
        k = i % len(main)
        a = math.radians(rnd.uniform(-60, 60))
        sp = rnd.uniform(0.04, 0.09)
        v = Vector((sp * math.cos(a), sp * math.sin(a) + (0.03 if i % 2 else -0.03), rnd.uniform(0.24, 0.38)))
        c = rock('im_chunk_%d' % i, rnd.uniform(0.08, 0.14), M['navy'] if i % 2 else M['navy_lt'], seed=i + 30, sub=1, rough=0.25, flat=True)
        toss(c, (cx + main[k][0] * 0.6, main[k][1] * 0.6, 0.15), v, f)
    for i in range(6):
        k = 1 + i
        sd = crystal('im_shard_%d' % i, 0.07, 0.45, M['navy_lt'], 4, 0.4, 0.7,
                     loc=(cx + main[min(k, len(main) - 1)][0], main[min(k, len(main) - 1)][1] + (0.25 if i % 2 else -0.25), 0.0),
                     rot=aim((0.3 if i % 2 else -0.3, 0.2 if i % 2 else -0.2, 1)), ol=0.015)
        pop(sd, f + 3 + i, 1.0, grow=3)
    for i in range(5):
        a = math.radians(rnd.uniform(-100, 100))
        rr = rnd.uniform(0.8, 2.2)
        p = sphere('im_smoke_%d' % i, 0.3, smoke, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.6, 1.2))
        key(p, IMPACT0, loc=(cx, 0, 0.3), scale=0, alpha=1)
        key(p, f + 3, loc=(cx, 0, 0.3), scale=0.3, alpha=1)
        key(p, f + 12, loc=end, scale=rnd.uniform(1.2, 1.8), alpha=0.8)
        key(p, END, loc=(end[0], end[1], end[2] + 0.5), scale=rnd.uniform(2.0, 2.5), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
