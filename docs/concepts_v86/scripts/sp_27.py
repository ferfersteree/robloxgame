from spearlib import *

NAME = 'SP_27_ash_saw'
N = 27
BG = '#9a8688'        # ash haze
GROUND = '#7c6c6c'    # ash plain
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'saw_disc': 'im_disc_0', 'ash_ring': 'im_shock', 'ember': 'im_ember_0', 'spark': 'fl_spark_0'}


def mats():
    return dict(
        ash=toon('asw_ash', '#6f6a70', '#3a3540', '#aaa4ae', spec=0.8, rim=0.5, rimcol='#ff8a3a'),
        char=toon('asw_char', '#33303a', '#17141c', '#625d6c', spec=0.6, rimcol='#ff7a2a'),
        iron=toon('asw_iron', '#8d8f9c', '#4c4e5e', '#d6d8e4', spec=1.0, rimcol='#ffb070'),
        cloth=toon('asw_cloth', '#b8aca0', '#7a6e64', '#e8dccc', spec=0.2),
        rust=toon('asw_rust', '#a8512e', '#5e2a1a', '#e08a58'),
        ember=glow('asw_ember', '#ff6a1a', 2.2),
        hot=glow('asw_hot', '#ffc24a', 3.4),
    )


def pop(ob, t0, t1, sc=1.0, hold=40, over=1.15):
    s = (sc, sc, sc) if isinstance(sc, (int, float)) else tuple(sc)
    key(ob, IMPACT0, scale=0)
    key(ob, t0, scale=0)
    key(ob, t1, scale=tuple(x * over for x in s))
    key(ob, t1 + 3, scale=s)
    key(ob, IMPACT0 + hold, scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def toss(ob, p0, v, f, g=-0.03, floor=0.08, spin=(30, 20, 0), hold=36, s=1.0):
    key(ob, IMPACT0, loc=p0, scale=0)
    key(ob, f, loc=p0, scale=0.3 * s)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= floor or t > 34
        if done:
            p.z = floor
        key(ob, f + t, loc=p, scale=s, rot=(t * spin[0], t * spin[1], t * spin[2]), interp='LINEAR')
        if done:
            break
    key(ob, max(f + t + 2, IMPACT0 + hold), scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def saw_outline(z0, z1, w0, w1, teeth, depth):
    """left edge straight, right edge sawtoothed; closed XZ outline (counter-clockwise)"""
    def xe(z):
        t = (z - z0) / (z1 - z0)
        return w0 + (w1 - w0) * t
    pts = [(-w0, z0), (xe(z0), z0)]
    step = (z1 - 0.5 - z0) / teeth
    for k in range(teeth):
        z = z0 + 0.1 + k * step
        pts.append((xe(z) + depth * (1 - 0.5 * k / teeth), z + step * 0.25))
        pts.append((xe(z + step), z + step))
    pts.append((0.0, z1))
    pts.append((-w1, z1 - 1.0))
    return pts


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    ash, char, iron, cloth, rust, ember, hot = (M[k] for k in ('ash', 'char', 'iron', 'cloth', 'rust', 'ember', 'hot'))
    # ---- tail: ratchet-gear counterweight with an ember core
    lathe('tail_barrel', [(0.0, 0.0), (0.03, 0.14), (0.15, 0.25), (0.45, 0.27), (0.62, 0.2), (0.7, 0.0)], char, 14)
    star('tail_gear', 0.36, 0.26, 8, 0.1, iron, loc=(0, 0, 0.42))
    sphere('tail_core', 0.13, hot, 8, 5, loc=(0, 0, 0.14), ol=0)
    torus('tail_ring', 0.18, 0.045, rust, 14, 6, loc=(0, 0, 0.8))
    # ---- shaft: charred, with ember seams and cloth wraps
    rod('shaft_lo', 0.155, 0.7, 3.3, char, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, char, r1=0.145)
    coil('cloth_lo', 0.176, 0.034, 1.3, 1.9, 4, cloth, segs=5)
    torus('cloth_lo_cap', 0.18, 0.04, iron, 14, 6, loc=(0, 0, 1.92))
    coil('cloth_hi', 0.175, 0.034, 3.12, 3.7, 4, cloth, segs=5, phase=0.8)
    torus('cloth_hi_cap', 0.178, 0.035, iron, 14, 6, loc=(0, 0, 3.1))
    for i, z in enumerate((4.1, 4.9, 5.7)):
        torus('seam_%d' % i, 0.153, 0.025, ember, 14, 5, loc=(0, 0, z), ol=0)
    for i in range(3):
        z = 4.4 + i * 0.22
        cone('shaft_tooth_%d' % i, 0.06, 0.2, iron, 5, loc=(0.16 * math.cos(i * 2.1), 0.16 * math.sin(i * 2.1), z), rot=aim((math.cos(i * 2.1), math.sin(i * 2.1), 0.6)), ol=0.012)
    # ---- socket + round saw guard
    lathe('socket', [(5.95, 0.15), (6.1, 0.26), (6.35, 0.34), (6.6, 0.3), (6.7, 0.0)], iron, 14)
    torus('socket_ring', 0.3, 0.05, rust, 16, 6, loc=(0, 0, 6.1))
    star('guard_disc', 0.95, 0.76, 16, 0.1, iron, loc=(0, 0.22, 6.95), rot=(90, 0, 0))
    star('guard_disc_in', 0.5, 0.42, 10, 0.16, char, loc=(0, 0.24, 6.95), rot=(90, 0, 9))
    sphere('guard_gem', 0.14, ember, 8, 5, loc=(0, 0.3, 6.95), ol=0)
    # ---- the serrated saw blade
    out = saw_outline(6.75, TIP, 0.5, 0.24, 5, 0.5)
    blade('saw', out, 0.12, ash)
    core = [(x * 0.35 + 0.02, 6.95 + (z - 6.75) * 0.82) for (x, z) in saw_outline(6.75, TIP, 0.5, 0.24, 5, 0.0)]
    blade('saw_core', core, 0.13, ember, ol=0)
    tube('saw_spine', [(-0.38, 0, 6.8), (-0.34, 0, 7.8), (-0.2, 0, 8.7), (-0.05, 0, 9.2)], [0.09, 0.08, 0.06, 0.03], char, 6)
    for i in range(4):
        z = 7.1 + i * 0.5
        sphere('saw_rivet_%d' % i, 0.06, hot, 6, 4, loc=(-0.26 + 0.05 * i, 0.14, z), ol=0)
    # (lead fix) big hooked saw teeth along the right edge so the serration reads in silhouette
    for i in range(6):
        z = 7.0 + i * 0.36
        xe = 0.5 + (0.24 - 0.5) * (z - 6.75) / (TIP - 6.75)
        ln = 0.48 - 0.05 * i
        cone('big_tooth_%d' % i, 0.13 - 0.01 * i, ln, iron, 4, loc=(xe - 0.08, 0, z), rot=aim((1, 0, 0.55)), ol=0.018)
    for i in range(3):
        crystal('float_tooth_%d' % i, 0.07, 0.38, iron, 4, 0.5, 0.7, both=True, loc=(0.85 + 0.12 * i, -0.15 + 0.2 * i, 7.5 + 0.55 * i),
                rot=aim((0.8, 0, 0.5)), ol=0.015)
    for i in range(2):
        sphere('float_ember_%d' % i, 0.07, hot, 7, 4, loc=(-0.65 - 0.1 * i, 0.15, 8.0 + 0.4 * i), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2727)
    ashp = ghost('asw_ashp', '#4a4248', 0.6, 0.85, 1.0)
    heat = ghost('asw_heat', '#ff8a3a', 1.2, 0.05, 1.8)
    fl_o = glow('asw_fl_o', '#ff5a14', 3.0)
    fl_y = glow('asw_fl_y', '#ffc23a', 3.4)
    # ---------------- idle
    fx('idle')
    sphere('idle_heat', 0.6, heat, 14, 8, loc=(0.1, 0, 8.0), scale=(1.2, 0.8, 1.8))
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 0.9)
        flame('idle_ember_%d' % i, rnd.uniform(0.12, 0.22), 0.045, fl_y if i % 2 else fl_o, 0.1, 6,
              loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.4)))
    # ---------------- flight: sparks, ash puffs, spinning saw discs
    fx('flight')
    sparks = [sphere('fl_spark_%d' % i, 0.06, fl_y if i % 2 else fl_o, 6, 4) for i in range(12)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(sparks, lambda t, i: (sj[i][0] * (0.3 + 1.5 * t), sj[i][1] * (0.3 + 1.5 * t), 8.4 - 13.0 * t), smax=1.3)
    puffs = [sphere('fl_ash_%d' % i, 0.35, ashp, 12, 7) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.3 + 0.8 * t), pj[i][1] * (0.3 + 0.8 * t), 5.0 - 9.0 * t),
           smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    discs = [star('fl_disc_%d' % i, 0.3, 0.22, 10, 0.06, M['iron'] if i % 2 else M['char']) for i in range(5)]
    dj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(5)]
    stream(discs, lambda t, i: (dj[i][0] * (0.4 + 0.9 * t), dj[i][1] * (0.4 + 0.9 * t), 8.0 - 12.0 * t), smax=1.1,
           spin=lambda t, i: (60 + 40 * dj[i][0], 30 * dj[i][1], 720 * t))
    flms = [flame('fl_flame_%d' % i, 0.5, 0.11, fl_o if i % 2 else fl_y, 0.0, 6) for i in range(7)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(7)]
    stream(flms, lambda t, i: (fj[i][0] * (0.2 + 0.6 * t), fj[i][1] * (0.2 + 0.6 * t), 9.0 - 10.5 * t),
           smax=lambda t, i: (1.2 - 0.5 * t) * math.sin(math.pi * t) ** 0.5, spin=lambda t, i: (180, 0, 0))
    # ---------------- impact: saw discs skid across the ground, ash cloud, embers
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('asw_flash', '#ffd08a', 2.0, 0.65, 1.2), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.75)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    sc = sphere('im_scorch', 0.8, ghost('asw_scorch', '#18121a', 0.4, 0.8, 1.0), 16, 4, loc=(cx, 0, 0.03))
    key(sc, IMPACT0, scale=0, alpha=1)
    key(sc, f, scale=(0.5, 0.5, 0.02), alpha=1)
    key(sc, f + 10, scale=(2.6, 2.6, 0.03), alpha=0.9)
    key(sc, IMPACT0 + 40, scale=(3.0, 3.0, 0.03), alpha=0)
    tidy(sc, 'impact')
    sh = torus('im_shock', 0.5, 0.06, M['ember'], 32, 5, loc=(cx, 0, 0.05))
    key(sh, IMPACT0, scale=0, alpha=1)
    key(sh, f, scale=0.3, alpha=1)
    key(sh, f + 12, scale=5.0, alpha=0)
    tidy(sh, 'impact', interp='LINEAR')
    ease_keys(sh)
    # six spinning saw discs skid outward along the ground (forward-biased fan)
    for k in range(6):
        a = math.radians(-70 + k * 28)
        L_ = 2.6 + 0.5 * (k % 2)
        dc = star('im_disc_%d' % k, 0.34, 0.25, 10, 0.07, M['iron'] if k % 2 else M['char'], loc=(cx, 0, 0.08))
        t0 = f + (k % 3)
        end = (cx + L_ * math.cos(a), L_ * math.sin(a), 0.08)
        mid = (cx + 0.5 * L_ * math.cos(a), 0.5 * L_ * math.sin(a), 0.2)
        key(dc, IMPACT0, loc=(cx, 0, 0.08), scale=0, rot=(0, 0, 0))
        key(dc, t0, loc=(cx, 0, 0.08), scale=0.4, rot=(0, 0, 0))
        key(dc, t0 + 6, loc=mid, scale=1.1, rot=(0, 0, 360))
        key(dc, t0 + 24, loc=end, scale=1.0, rot=(0, 0, 1000))
        key(dc, t0 + 30, loc=end, scale=0.0, rot=(0, 0, 1100))
        tidy(dc, 'impact', interp='LINEAR')
        ember_t = glow('asw_trail', '#ff7a2a', 2.8)
        for j in range(2):
            tr = sphere('im_skid_%d_%d' % (k, j), 0.07, ember_t, 6, 4)
            key(tr, IMPACT0, loc=(cx, 0, 0.1), scale=0, alpha=1)
            key(tr, t0 + 4 + j * 4, loc=(cx + (0.3 + 0.8 * j) * L_ * 0.4 * math.cos(a), (0.3 + 0.8 * j) * L_ * 0.4 * math.sin(a), 0.1), scale=1.2, alpha=1)
            key(tr, t0 + 16 + j * 4, scale=0.0, alpha=0)
            tidy(tr, 'impact')
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.2)
        sm = sphere('im_ash_%d' % i, 0.42, ashp, 12, 7)
        t0 = f + 2 + rnd.randint(0, 8)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.8, 3.2))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.8, 2.6), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    for i in range(14):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.3, 1.6)
        em = flame('im_ember_%d' % i, rnd.uniform(0.14, 0.24), 0.05, fl_y if i % 2 else fl_o, 0.0, 6)
        t0 = f + rnd.randint(0, 10)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.15)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.4, 3.0))
        key(em, IMPACT0, loc=p0, scale=0)
        key(em, t0, loc=p0, scale=0.3)
        key(em, t0 + 6, scale=1.0)
        key(em, t0 + 30, loc=p1, scale=0.0)
        tidy(em, 'impact')
        ease_keys(em)
    for i in range(5):
        a = math.radians(i * 72 + 25)
        L_ = rnd.uniform(1.4, 2.2)
        pts = zigzag((cx, 0, 0.02), (cx + L_ * math.cos(a), L_ * math.sin(a), 0.02), 4, 0.12, seed=i + 5)
        for p in pts:
            p.z = 0.02
        cr = tube('im_crack_%d' % i, pts, [0.09, 0.07, 0.05, 0.03, 0.0], M['ember'], 4, smooth=False, ol=0)
        cr.scale = (1, 1, 0.3)
        key(cr, IMPACT0, scale=0, alpha=1)
        key(cr, f + i % 3, scale=0, alpha=1)
        key(cr, f + 5 + i % 3, scale=(1, 1, 0.3), alpha=1)
        key(cr, IMPACT0 + 34, alpha=1)
        key(cr, IMPACT0 + 44, scale=(1, 1, 0.3), alpha=0)
        tidy(cr, 'impact')
    return True
