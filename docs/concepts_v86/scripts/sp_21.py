from spearlib import *

NAME = 'SP_21_storm_trident'
N = 21
BG = '#5a5a8a'        # storm sky
GROUND = '#7a8296'    # wet slate
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'bolt': 'im_bolt_0', 'bolt_halo': 'im_halo_0', 'elec_ring': 'im_ring_0', 'spark': 'im_spark_0', 'zig': 'fl_zig_0'}
END = IMPACT0 + 44


def mats():
    return dict(
        slate=toon('s21_slate', '#6b6a8a', '#3a3852', '#a4a4c8', spec=0.6, rimcol='#e0d8ff'),
        dark=toon('s21_dark', '#3d3b58', '#1e1c32', '#6c6a92', spec=0.5),
        purple=toon('s21_purple', '#7a4fb0', '#40236e', '#b890ec', spec=0.8, emit=0.15),
        cloud=toon('s21_cloud', '#cfd0e8', '#8a8aac', '#ffffff', spec=0.2),
        steel=toon('s21_steel', '#a4aac0', '#5e6480', '#e4e8f8', spec=1.0, rimcol='#ffffff'),
        gold=toon('s21_gold', '#e8c04a', '#9a6a1e', '#fff0a0', spec=1.0),
        zap=glow('s21_zap', '#ffe45a', 2.2),
        zap_pu=glow('s21_zap_pu', '#9a6cff', 2.2),
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
    """instant lightning flash: appears at t0, flickers, fades out"""
    key(ob, IMPACT0, scale=0, alpha=1)
    key(ob, t0, scale=0, alpha=1)
    key(ob, t0 + 1, scale=1, alpha=1)
    key(ob, t0 + 3, scale=1, alpha=0.2)
    key(ob, t0 + 4, scale=1, alpha=1)
    key(ob, t0 + 7, scale=1, alpha=0.9)
    key(ob, t0 + dur - 1, scale=1, alpha=0.1)
    key(ob, t0 + dur, scale=0, alpha=0)
    tidy(ob, 'impact', interp='LINEAR')


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    slate, dark, purple, cloud, steel, gold, zap, zap_pu = (M[k] for k in (
        'slate', 'dark', 'purple', 'cloud', 'steel', 'gold', 'zap', 'zap_pu'))
    # ---- tail: small storm cloud with a lightning-rod spike
    for i, (x, y, r) in enumerate(((0.0, 0.0, 0.26), (0.18, 0.1, 0.17), (-0.16, -0.1, 0.18))):
        sphere('tail_cloud_%d' % i, r, cloud if i == 0 else slate, 10, 6, loc=(x, y, 0.35 + 0.05 * i))
    cone('tail_rod', 0.07, 0.35, steel, 7, loc=(0, 0, 0.35), rot=(180, 0, 0), ol=0.015)
    torus('tail_ring', 0.2, 0.045, gold, 14, 6, loc=(0, 0, 0.78))
    # ---- shaft: slate with purple and gold bands, lightning ornaments
    rod('shaft_lo', 0.155, 0.65, 3.3, slate, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, slate, r1=0.14)
    coil('wrap_lo', 0.178, 0.03, 1.2, 1.7, 4, dark, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, gold, 14, 6, loc=(0, 0, 1.94))
    torus('wrap_lo_cap2', 0.17, 0.035, purple, 14, 6, loc=(0, 0, 1.05))
    coil('wrap_hi', 0.176, 0.03, 3.08, 3.62, 4, dark, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, gold, 14, 6, loc=(0, 0, 3.06))
    for i, z in enumerate((4.2, 4.4, 4.6)):
        torus('band_%d' % i, 0.16, 0.03 if i != 1 else 0.04, (purple, gold, purple)[i], 14, 5, loc=(0, 0, z), ol=0.015)
    bolt('orn_a', (0.19, 0.06, 4.9), (0.19, 0.06, 5.9), zap, r=0.045, n=5, amp=0.07, seed=1, ol=0)
    bolt('orn_b', (-0.18, -0.07, 5.0), (-0.18, -0.07, 5.9), zap_pu, r=0.045, n=5, amp=0.07, seed=2, ol=0)
    bolt('orn_c', (0.06, -0.19, 1.3), (0.06, -0.19, 1.8), zap, r=0.04, n=4, amp=0.05, seed=3, ol=0)
    # ---- storm-cloud socket
    lathe('socket', [(6.1, 0.15), (6.25, 0.24), (6.5, 0.28), (6.8, 0.26), (6.9, 0.2), (6.9, 0)], dark, 12)
    for i in range(5):
        a = math.radians(i * 72 + 15)
        sphere('socket_cloud_%d' % i, 0.2, cloud if i % 2 else slate, 10, 6, loc=(0.3 * math.cos(a), 0.3 * math.sin(a), 6.5 + 0.1 * (i % 2)))
    torus('socket_band', 0.26, 0.045, purple, 14, 6, loc=(0, 0, 6.25))
    # ---- forked double tip: U-arch + two blade prongs + lightning in the gap
    tube('fork_arch', [(-0.45, 0, 7.15), (-0.25, 0, 6.85), (0.0, 0, 6.78), (0.25, 0, 6.85), (0.45, 0, 7.15)], 0.16, steel, 8, scale=(1, 0.7, 1))
    blade('prong_R', [(0.25, 7.1), (0.58, 7.2), (0.64, 8.2), (0.46, 9.0), (0.12, TIP), (0.24, 8.2)], 0.13, steel)
    blade('prong_L', [(-0.25, 7.1), (-0.24, 8.2), (-0.12, TIP), (-0.46, 9.0), (-0.64, 8.2), (-0.58, 7.2)], 0.13, steel)
    blade('prong_rib_R', [(0.4, 7.3), (0.5, 7.3), (0.52, 8.5), (0.42, 8.5)], 0.18, purple, ol=0.012)
    blade('prong_rib_L', [(-0.5, 7.3), (-0.4, 7.3), (-0.42, 8.5), (-0.52, 8.5)], 0.18, purple, ol=0.012)
    tube('core_bolt', [(0.0, 0, 7.2), (0.13, 0, 7.6), (-0.1, 0, 8.0), (0.11, 0, 8.4), (-0.08, 0, 8.8), (0.0, 0, 9.0)],
         [0.0, 0.05, 0.05, 0.045, 0.04, 0.0], zap, 5, ol=0)
    torus('fork_band', 0.4, 0.045, gold, 14, 5, loc=(0, 0, 7.05), scale=(1, 0.4, 1), ol=0.015)
    for s in (-1, 1):
        sphere('prong_gem_%d' % (s + 1), 0.07, zap, 8, 5, loc=(s * 0.47, 0.17, 7.6), ol=0)
    # ---- charm: gold bolt pendant on a cord
    tube('charm_cord', [(0.2, 0.03, 6.05), (0.34, 0.06, 5.75), (0.4, 0.07, 5.55)], 0.022, dark, 5)
    bolt('charm_bolt', (0.4, 0.07, 5.55), (0.4, 0.07, 5.15), zap, r=0.05, n=3, amp=0.06, seed=4, ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2121)
    zap = M['zap']
    zap_pu = M['zap_pu']
    smoke = ghost('s21_smoke', '#6a6884', 0.8, 0.85, 1.0)
    cloudp = ghost('s21_cloudp', '#d2d2ec', 1.0, 0.8, 1.1)
    # ---------------- idle: crackling sparks between the prongs
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 0.9)
        sphere('idle_spark_%d' % i, rnd.uniform(0.04, 0.08), zap if i % 2 else zap_pu, 7, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.2, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, zap, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.8), -0.3, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: cloud puffs, sparks, bolt shards, electric rings
    fx('flight')
    puffs = [sphere('fl_cloud_%d' % i, 0.34, cloudp if i % 2 else smoke, 12, 7) for i in range(8)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.9 * t), jp[i][1] * (0.15 + 0.9 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    sparks = [sphere('fl_spark_%d' % i, 0.06, zap if i % 2 else zap_pu, 6, 4) for i in range(12)]
    jk = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(sparks, lambda t, i: (jk[i][0] * (0.3 + 1.5 * t), jk[i][1] * (0.3 + 1.5 * t), 8.6 - 13.0 * t), smax=1.2)
    zz = [bolt('fl_zig_%d' % i, (0, 0, 0), (0.0, 0, 0.55), zap if i % 2 else zap_pu, r=0.05, n=4, amp=0.1, seed=i) for i in range(6)]
    jz = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(zz, lambda t, i: (jz[i][0] * (0.3 + 0.9 * t), jz[i][1] * (0.3 + 0.9 * t), 8.8 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (jz[i][2] + 360 * t, 180 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.45, 0.04, zap_pu if i % 2 else zap, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: three lightning strikes, electric ring and arcs, sparks
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s21_flash', '#fff6c0', 2.2, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.2, alpha=0.8)
    key(flash, f + 10, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    strikes = []
    for i, (ang, rr) in enumerate(((-60, 1.4), (50, 1.7), (125, 1.4))):
        a = math.radians(ang)
        tx, ty = cx + rr * math.cos(a), rr * math.sin(a)
        strikes.append((tx, ty))
        top = (tx + 0.5 * math.cos(a + 1.0), ty + 0.5 * math.sin(a + 1.0), 6.0)
        pts = zigzag(top, (tx, ty, 0.03), 8, 0.3, seed=i + 7)
        pts[-1].z = 0.03
        pts = [p - Vector((tx, ty, 0.0)) for p in pts]
        rad = [0.05] + [0.075] * 7 + [0.05]
        core = tube('im_bolt_%d' % i, pts, [r_ * 0.6 for r_ in rad], zap, 4, smooth=False, ol=0, loc=(tx, ty, 0.0))
        halo = tube('im_halo_%d' % i, pts, [r_ * 2.2 for r_ in rad], zap_pu, 4, smooth=False, ol=0, loc=(tx, ty, 0.0))
        t0 = f + i * 3
        flicker(core, t0)
        flicker(halo, t0)
        sf = sphere('im_strike_%d' % i, 0.3, ghost('s21_strike', '#fff2a0', 2.2, 0.8, 1.1), 10, 6, loc=(tx, ty, 0.2))
        key(sf, IMPACT0, scale=0, alpha=1)
        key(sf, t0, scale=0, alpha=1)
        key(sf, t0 + 2, scale=1.6, alpha=1)
        key(sf, t0 + 9, scale=2.4, alpha=0)
        tidy(sf, 'impact', interp='LINEAR')
        sc_ = cyl('im_scorch_%d' % i, 0.45, 0.04, M['dark'], 12, 0.01, loc=(tx, ty, 0.02))
        pop(sc_, t0, 1.0, grow=3)
    # electric ground rings and a ring of small arcs
    for k in range(2):
        er = torus('im_ring_%d' % k, 0.6, 0.05, zap if k == 0 else zap_pu, 36, 5, loc=(cx, 0, 0.06 + 0.04 * k))
        expand(er, f + k * 4, 0.3, 4.6 - k * 0.6, 14)
    for i in range(8):
        a = math.radians(i * 45 + 22)
        if abs(math.cos(a)) > 0.9 and math.cos(a) < 0:
            continue
        p0 = (1.3 * math.cos(a), 1.3 * math.sin(a), 0.1)
        p1 = (1.3 * math.cos(a + 0.5), 1.3 * math.sin(a + 0.5), 0.1)
        ar = tube('im_arc_%d' % i, zigzag(p0, p1, 4, 0.1, seed=i), [0.03, 0.05, 0.05, 0.05, 0.03], zap, 4, smooth=False, ol=0, loc=(cx, 0, 0.0))
        flicker(ar, f + 3 + i, 10)
    g = -0.03
    for i in range(20):
        sx, sy = strikes[i % 3]
        a = math.radians(rnd.uniform(0, 360))
        sp = rnd.uniform(0.02, 0.07)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.18, 0.34)))
        sk = sphere('im_spark_%d' % i, rnd.uniform(0.04, 0.08), zap if i % 2 else zap_pu, 6, 4)
        p0 = Vector((sx, sy, 0.15))
        t00 = f + (i % 3) * 3
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
    for i in range(6):
        a = math.radians(i * 60 + rnd.uniform(-10, 10))
        rr = rnd.uniform(1.0, 2.0)
        p = sphere('im_smoke_%d' % i, 0.32, smoke if i % 2 else cloudp, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.6, 1.2))
        key(p, IMPACT0, loc=(cx, 0, 0.3), scale=0, alpha=1)
        key(p, f + 3, loc=(cx, 0, 0.3), scale=0.3, alpha=1)
        key(p, f + 12, loc=end, scale=rnd.uniform(1.2, 1.8), alpha=0.8)
        key(p, END, loc=(end[0], end[1], end[2] + 0.5), scale=rnd.uniform(2.0, 2.5), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
