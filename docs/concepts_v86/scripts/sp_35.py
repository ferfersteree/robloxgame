from spearlib import *

NAME = 'SP_35_cloud_feather'
N = 35
BG = '#78aee6'        # open sky
GROUND = '#9dbbe2'    # cloud floor
SKY = '#6aa6e0'
TIP = 9.45
TRAIL = 5.2
FX_EXPORT = {'cloud_puff': 'im_puff_0', 'feather': 'im_feather_0', 'rainbow_ring': 'im_rainbow_0'}

RAINBOW = ('#ff4a5a', '#ff9a3a', '#ffe14a', '#5ae06a', '#3ad8ff', '#4a7aff', '#b05aff')


def mats():
    return dict(
        white=toon('cf_white', '#ffffff', '#b9cfee', '#ffffff', spec=0.5, rim=0.5, rimcol='#9fd4ff'),
        sky=toon('cf_sky', '#58b7ff', '#2a74d0', '#a8dcff', spec=0.8, emit=0.15),
        gold=toon('cf_gold', '#ffd35a', '#c88a1e', '#fff0a8', spec=1.0),
        rose=toon('cf_rose', '#ff9ec4', '#d5588c', '#ffd2e4', emit=0.2),
        cloud=toon('cf_cloud', '#f4f9ff', '#aac4e8', '#ffffff', spec=0.2),
        navy=toon('cf_navy', '#3a5fbf', '#24398a', '#7a9cef'),
        halo=glow('cf_halo', '#9fe6ff', 1.7),
        sun=glow('cf_sun', '#fff2a0', 3.4),
    )


def feather_outline(z0, z1, W, n=8, notch=0.12):
    R, L = [], []
    for i in range(1, n):
        t = i / n
        w = W * math.sin(math.pi * t ** 0.7) ** 0.9
        z = z0 + (z1 - z0) * t
        R.append((w * (1 - notch * (i % 2)), z))
        L.append((-w * (1 - notch * ((i + 1) % 2)), z))
    return [(0, z0)] + R + [(0, z1)] + L[::-1]


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
    white, sky, gold, rose, cloud, navy, halo, sun = (M[k] for k in ('white', 'sky', 'gold', 'rose', 'cloud', 'navy', 'halo', 'sun'))
    # ---- tail: cloud-puff pommel + little plume
    sphere('tail_puff_a', 0.32, cloud, 10, 6, loc=(0, 0, 0.34))
    sphere('tail_puff_b', 0.24, cloud, 8, 5, loc=(0.24, 0, 0.22))
    sphere('tail_puff_c', 0.22, white, 8, 5, loc=(-0.22, 0.06, 0.24))
    leaf('tail_plume', 0.8, 0.26, rose, 0.04, 5, loc=(0, 0.05, 0.8), rot=(0, 95, 10), ol=0.015)
    torus('tail_ring', 0.2, 0.045, gold, 14, 6, loc=(0, 0, 0.64))
    # ---- shaft: sky lacquer, white cloth wraps, gold caps
    shaft_parts(sky, white, gold, navy)
    for i in range(3):
        a = i * 2.1
        sphere('shaft_bead_%d' % i, 0.055, sun, 7, 4, loc=(0.15 * math.cos(a), 0.15 * math.sin(a), 5.2 + i * 0.35), ol=0.0)
    # ---- socket: gold cup ringed by cloud puffs
    lathe('socket', [(6.35, 0.14), (6.5, 0.2), (6.8, 0.26), (7.05, 0.2), (7.15, 0)], gold, 14)
    torus('socket_ring', 0.27, 0.05, navy, 14, 6, loc=(0, 0, 6.62))
    for i in range(5):
        a = math.radians(i * 72 + 20)
        sphere('collar_puff_%d' % i, 0.2, cloud if i % 2 else white, 8, 5, loc=(0.34 * math.cos(a), 0.34 * math.sin(a), 6.95 - 0.1 * (i % 2)))
    # ---- the feather head: layered quill blade + wing feathers
    tube('quill', [(0, 0, 6.9), (0, 0, 7.8), (0, 0, 8.8), (0, 0, TIP)], [0.085, 0.07, 0.05, 0.0], gold, 8)
    blade('feather', feather_outline(6.95, TIP, 0.82), 0.12, white)
    blade('feather_core', feather_outline(7.3, TIP - 0.5, 0.42, notch=0), 0.15, sky, ol=0.015)
    blade('feather_spark', feather_outline(7.9, TIP - 1.1, 0.18, notch=0), 0.17, sun, ol=0)
    for s in (-1, 1):
        nm = 'a' if s < 0 else 'b'
        phi = 55 if s > 0 else 125
        leaf('wing_big_' + nm, 1.55, 0.7, white, 0.05, 6, loc=(0, 0, 7.15), rot=(90, -phi, 0), ol=0.02)
        leaf('wing_mid_' + nm, 1.2, 0.5, sky, 0.05, 6, loc=(0, 0.03, 7.35), rot=(90, -(phi + s * -18), 0), ol=0.015)
        leaf('wing_tip_' + nm, 0.8, 0.34, rose, 0.04, 5, loc=(0, 0.06, 7.55), rot=(90, -(phi + s * -34), 0), ol=0.012)
    # ---- floating legendary bits: detached feathers, puffs, halo
    fl = ((0.95, 0.15, 8.5, 70, gold), (-0.9, -0.1, 8.3, 110, rose), (0.2, 0.55, 8.6, 85, sky))
    for i, (x, y, z, phi, m) in enumerate(fl):
        leaf('float_feather_%d' % i, 0.7, 0.25, m, 0.04, 5, loc=(x, y, z), rot=(90, -phi, 20 * i), ol=0.015)
    for i, (x, y, z) in enumerate(((1.0, 0.2, 7.5), (-1.05, 0.0, 8.0), (0.7, -0.5, 9.3))):
        sphere('float_puff_%d' % i, 0.2 - 0.03 * i, cloud, 8, 5, loc=(x, y, z))
    torus('float_halo', 0.95, 0.035, halo, 22, 4, loc=(0, 0, 7.6), rot=(72, 0, 0), ol=0)
    torus('float_halo_b', 0.72, 0.03, sun, 18, 4, loc=(0, 0, 8.4), rot=(-65, 0, 25), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def life(ob, a, s=1.0, hold=IMPACT0 + 38):
    sc = s if isinstance(s, tuple) else (s, s, s)
    key(ob, IMPACT0, scale=0)
    if a > IMPACT0:
        key(ob, a, scale=0)
    key(ob, a + 5, scale=sc)
    key(ob, hold, scale=sc)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')
    ease_keys(ob)


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
    rnd = random.Random(3535)
    cl = ghost('cf_cloudfx', '#ffffff', 1.3, 0.9, 1.0)
    cl2 = ghost('cf_cloudfx2', '#cfe8ff', 1.2, 0.9, 1.0)
    aura = ghost('cf_aura', '#cfeeff', 1.2, 0.05, 1.8)
    sp = glow('cf_sparkle', '#fffbe0', 3.0)
    rb = [glow('cf_rb_%d' % i, c, 2.8) for i, c in enumerate(RAINBOW)]
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.7, aura, 14, 8, loc=(0, 0, 8.0), scale=(1.4, 0.9, 1.8))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.035, 4, 0.02, sp, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.9), -0.3, 7.4 + i * 0.7), rot=(90, 0, 0))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.0)
        sphere('idle_mote_%d' % i, rnd.uniform(0.06, 0.11), cl if i % 2 else cl2, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.5)))
    # ---------------- flight
    fx('flight')
    puffs = [sphere('fl_puff_%d' % i, 0.3, cl if i % 2 else cl2, 10, 6) for i in range(10)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 8.0 - 12.0 * t),
           smax=lambda t, i: (0.6 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    fe = [leaf('fl_feather_%d' % i, 0.7, 0.24, (M['white'], M['rose'], M['sky'], M['gold'])[i % 4], 0.04, 5, ol=0.012) for i in range(10)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(fe, lambda t, i: (fj[i][0] * (0.4 + 1.0 * t), fj[i][1] * (0.4 + 1.0 * t), 8.8 - 12.5 * t), smax=1.0,
           spin=lambda t, i: (fj[i][2] + 300 * t, 90 + 40 * math.sin(6.28 * t), fj[i][2]))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, rb[(i * 2) % 7], 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    sps = [star('fl_spark_%d' % i, 0.14, 0.035, 4, 0.02, sp) for i in range(6)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(sps, lambda t, i: (sj[i][0] * (0.4 + 1.0 * t), sj[i][1] * (0.4 + 1.0 * t), 8.4 - 11.0 * t), smax=1.4,
           spin=lambda t, i: (90, 0, 360 * t))
    # ---------------- impact: big cloud burst, drifting feathers, rainbow ring set
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.6, ghost('cf_flash', '#ffffff', 2.0, 0.7, 1.2), 14, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 5, scale=2.6, alpha=0.7)
    key(flash, f + 12, scale=3.4, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    mat = sphere('im_cloudmat', 0.8, cl2, 14, 8, loc=(cx, 0, 0.1), scale=(2.4, 2.4, 0.35))
    key(mat, IMPACT0, scale=0, alpha=1)
    key(mat, f + 2, scale=(0.6, 0.6, 0.1), alpha=1)
    key(mat, f + 14, scale=(3.2, 3.2, 0.5), alpha=0.8)
    key(mat, IMPACT0 + 44, scale=(3.6, 3.6, 0.5), alpha=0)
    tidy(mat, 'impact')
    for i in range(18):
        a = math.radians(i * 20 + rnd.uniform(-8, 8))
        r = rnd.uniform(1.2, 3.0) * (1.25 if math.cos(a) < 0 else 1.0)
        p = sphere('im_puff_%d' % i, 0.45, cl if i % 2 else cl2, 12, 7)
        fly(p, (cx, 0, 0.3), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.5, 1.8)), f + i % 4, rnd.uniform(1.6, 2.5))
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.2)
        fm = leaf('im_feather_%d' % i, 0.8, 0.28, (M['white'], M['rose'], M['sky'], M['gold'])[i % 4], 0.04, 5, ol=0.012)
        t0 = f + rnd.randint(0, 6)
        p0 = (cx, 0, 0.3)
        pm = (cx + 0.5 * r * math.cos(a), 0.5 * r * math.sin(a), rnd.uniform(2.2, 3.4))
        p1 = (cx + r * math.cos(a + 0.9), r * math.sin(a + 0.9), rnd.uniform(0.3, 1.0))
        key(fm, IMPACT0, loc=p0, scale=0, rot=(90, 0, 0))
        key(fm, t0, loc=p0, scale=0.4, rot=(90, -80, a * 57))
        key(fm, t0 + 14, loc=pm, scale=1.0, rot=(90, -40, a * 57 + 160))
        key(fm, IMPACT0 + 44, loc=p1, scale=0, rot=(90, 20, a * 57 + 420))
        tidy(fm, 'impact')
        ease_keys(fm)
    for k in range(7):
        rg = torus('im_rainbow_%d' % k, 0.55 + 0.13 * k, 0.05, rb[k], 36, 5, loc=(cx, 0, 0.05 + 0.01 * k))
        key(rg, IMPACT0, scale=0, alpha=1)
        key(rg, f + k, scale=0.3, alpha=1)
        key(rg, f + k + 22, scale=2.6, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
        ease_keys(rg)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.8, 2.2)
        st = star('im_spark_%d' % i, 0.18, 0.045, 4, 0.02, sp, rot=(90, 0, 0))
        fly(st, (cx, 0, 0.5), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.4, 3.0)), f + 2 + i, 1.2)
    return True
