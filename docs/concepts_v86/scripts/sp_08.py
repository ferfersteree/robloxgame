from spearlib import *

NAME = 'SP_08_fire'
N = 8
BG = '#a06a48'        # canyon
GROUND = '#b8794a'
TIP = 9.2
TRAIL = 5.2
FX_EXPORT = {'flame': 'im_ringflame_0', 'fire_ring': 'fl_ring_0', 'scorch': 'im_scorch',
             'ember': 'im_ember_0', 'flame_tongue': 'fl_tongue_0'}


def mats():
    return dict(
        iron=toon('b08_iron', '#4a4450', '#26222c', '#7e7688', spec=0.8, rim=0.6, rimcol='#ff8a3a'),
        iron_hot=toon('b08_iron_hot', '#8a3a2a', '#4a1a18', '#e06a3a', spec=0.7, rim=0.6, rimcol='#ffc27a', emit=0.4),
        char=toon('b08_char', '#3a2c28', '#1c1412', '#6a504a', spec=0.2),
        char_lt=toon('b08_char_lt', '#5a463c', '#2c211c', '#8a6e60', spec=0.2),
        leather=toon('b08_leather', '#6a3a26', '#3a1c14', '#a0603e'),
        cord=toon('b08_cord', '#e0642a', '#9a2a1a', '#ffa060', spec=0.2),
        gold=toon('b08_gold', '#f0b43a', '#a8661c', '#ffe39a', spec=1.0),
        ember=glow('b08_ember', '#ff6a1a', 2.2),
        hot=glow('b08_hot', '#ffd25a', 2.2),
        fl_o=glow('b08_fl_o', '#ff5a14', 2.2),
        fl_y=glow('b08_fl_y', '#ffc23a', 2.2),
        fl_r=glow('b08_fl_r', '#e0302a', 2.2),
        smoke=ghost('b08_smoke', '#4a3a3a', 0.7, 0.8, 1.0),
        heat=ghost('b08_heat', '#ff8a3a', 1.6, 0.12, 1.8),
        ball=glow('b08_ball', '#ff7a22', 2.2),
        scorch=toon('b08_scorch', '#2c201c', '#161010', '#4a3830', spec=0.1),
    )


def spark_arc(ob, p0, v, f, g, life, rest=0.03, s=1.0):
    p0, v = Vector(p0), Vector(v)
    key(ob, IMPACT0, loc=p0, scale=0, alpha=1)
    key(ob, f - 1, loc=p0, scale=0, alpha=1)
    key(ob, f, loc=p0, scale=0.3 * s, alpha=1)
    t = 2
    while t < life:
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        if p.z < rest:
            p.z = rest
        key(ob, f + t, loc=p, scale=s, alpha=1, interp='LINEAR')
        t += 2
    key(ob, f + life, scale=0.3 * s, alpha=0)
    key(ob, IMPACT0 + 44, scale=0, alpha=0)
    tidy(ob, 'impact')


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    iron, iron_hot, char, char_lt, leather, cord, gold, ember, hot = (M[k] for k in (
        'iron', 'iron_hot', 'char', 'char_lt', 'leather', 'cord', 'gold', 'ember', 'hot'))
    # ---- tail: charred iron cap with a glowing ember
    lathe('tail_cap', [(0.1, 0), (0.1, 0.12), (0.3, 0.21), (0.55, 0.2), (0.75, 0.16), (0.75, 0)], iron, 12)
    sphere('tail_ember', 0.14, ember, 8, 5, loc=(0, 0, 0.16), ol=0)
    torus('tail_ring', 0.2, 0.04, gold, 12, 5, loc=(0, 0, 0.8))
    # ---- shaft: charred wood with glowing seams
    rod('shaft_lo', 0.155, 0.7, 3.3, char, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.1, char_lt, segs=12, r1=0.14)
    torus('seam_0', 0.157, 0.024, ember, 12, 5, loc=(0, 0, 1.15), ol=0)
    torus('seam_1', 0.152, 0.024, ember, 12, 5, loc=(0, 0, 4.4), ol=0)
    coil('wrap_lo', 0.18, 0.03, 1.35, 1.88, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, gold, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.62, 4, leather, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, gold, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.75, 4.95)):
        torus('cord_band_%d' % i, 0.148, 0.028, cord, 12, 5, loc=(0, 0, z), ol=0.012)
    for i, (z, a) in enumerate(((3.9, 1.0), (5.3, 4.2))):
        sphere('burn_knot_%d' % i, 0.07, char_lt, 8, 5, loc=(0.13 * math.cos(a), 0.13 * math.sin(a), z), scale=(0.8, 1, 1.3), ol=0.012)
    # ---- socket: iron collar with an ember seam
    lathe('socket', [(5.9, 0.14), (6.1, 0.22), (6.4, 0.28), (6.7, 0.3), (6.85, 0.24), (6.85, 0)], iron, 14)
    torus('socket_ring', 0.3, 0.05, gold, 14, 5, loc=(0, 0, 6.4))
    torus('socket_seam', 0.285, 0.03, ember, 14, 5, loc=(0, 0, 6.75), ol=0)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        sphere('rivet_%d' % i, 0.05, gold, 7, 4, loc=(0.27 * math.cos(a), 0.27 * math.sin(a), 6.55), ol=0.012)
    # ---- iron blade with a glowing ember core
    bl = [(0.28, 6.8), (0.48, 7.2), (0.52, 7.8), (0.4, 8.4), (0.2, 8.9), (0.0, TIP),
          (-0.2, 8.9), (-0.4, 8.4), (-0.52, 7.8), (-0.48, 7.2), (-0.28, 6.8)]
    blade('blade', bl, 0.14, iron)
    blade('blade_core', [(x * 0.5, 7.0 + (z - 6.8) * 0.85) for (x, z) in bl], 0.18, ember, ol=0)
    blade('blade_hot', [(x * 0.22, 7.2 + (z - 6.8) * 0.75) for (x, z) in bl], 0.2, hot, ol=0)
    # ---- flame-shaped side vanes
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        flame('vane_big_' + nm, 1.7, 0.24, M['iron_hot'], s * 0.25, 8, loc=(s * 0.45, 0, 6.85), rot=(0, 0, 0), scale=(1, 0.55, 1))
        flame('vane_small_' + nm, 1.0, 0.17, iron, s * 0.3, 8, loc=(s * 0.62, 0, 6.6), rot=(0, 0, 0), scale=(1, 0.55, 1))
    # ---- ember charm
    tube('charm_cord', [(0.2, 0.04, 5.95), (0.32, 0.08, 5.7), (0.36, 0.1, 5.5)], 0.02, cord, 5)
    sphere('charm_ember', 0.07, ember, 8, 5, loc=(0.36, 0.1, 5.42), ol=0)
    flame('charm_tag', 0.4, 0.1, M['iron_hot'], 0.0, 6, loc=(0.36, 0.1, 5.05), rot=(180, 0, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(808)
    fl_o, fl_y, fl_r, ember, hot, smoke, heat, ball = (M[k] for k in ('fl_o', 'fl_y', 'fl_r', 'ember', 'hot', 'smoke', 'heat', 'ball'))
    FL = (fl_o, fl_y, fl_r)
    # ---------------- idle: heat aura, small flames and embers around the blade
    fx('idle')
    sphere('idle_heat', 0.6, heat, 16, 9, loc=(0, 0, 8.0), scale=(1.1, 0.8, 2.0))
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 0.8)
        flame('idle_flame_%d' % i, rnd.uniform(0.2, 0.3), 0.06, FL[i % 2], 0.1, 6, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.0)))
    for i in range(3):
        a = rnd.uniform(0, 6.28)
        sphere('idle_ember_%d' % i, 0.04, hot, 6, 4, loc=(0.6 * math.cos(a), 0.6 * math.sin(a), rnd.uniform(7.2, 9.4)))
    # ---------------- flight: flame tongues + sparks + fire rings + smoke
    fx('flight')
    tongues = [flame('fl_tongue_%d' % i, 0.7, 0.16, FL[i % 3], 0.0, 8) for i in range(12)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.8, 1.4)) for _ in range(12)]
    stream(tongues, lambda t, i: (fj[i][0] * (0.2 + 0.7 * t), fj[i][1] * (0.2 + 0.7 * t), 9.0 - 11.5 * t),
           smax=lambda t, i: fj[i][2] * (1.4 - 0.6 * t) * math.sin(math.pi * t) ** 0.5,
           spin=lambda t, i: (180 + fj[i][0] * 20, fj[i][1] * 20, 0))
    sparks = [sphere('fl_spark_%d' % i, 0.06, fl_y, 6, 4) for i in range(10)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(sparks, lambda t, i: (sj[i][0] * (0.3 + 1.5 * t), sj[i][1] * (0.3 + 1.5 * t), 8.4 - 13.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, fl_o if i % 2 else fl_y, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.3 - 6.0 * t), smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (0, 0, 360 * t))
    puffs = [sphere('fl_smoke_%d' % i, 0.3, smoke, 10, 6) for i in range(4)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(4)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.3 + 0.7 * t), pj[i][1] * (0.3 + 0.7 * t), 3.5 - 7.0 * t),
           smax=lambda t, i: (0.6 + 1.3 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: fire explosion sphere, then a burning ring of small flames that smoulders and dies
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    fb = sphere('im_fireball', 0.6, ball, 16, 9, loc=(cx, 0, 0.5))
    key(fb, IMPACT0, scale=0, alpha=1)
    key(fb, f, scale=0.4, alpha=1)
    key(fb, f + 4, scale=2.6, alpha=0.95)
    key(fb, f + 9, scale=3.2, alpha=0.5)
    key(fb, f + 14, scale=3.6, alpha=0)
    key(fb, IMPACT0 + 44, scale=0, alpha=0)
    tidy(fb, 'impact', interp='LINEAR')
    fc = sphere('im_fireball_core', 0.5, hot, 14, 8, loc=(cx, 0, 0.5))
    key(fc, IMPACT0, scale=0, alpha=1)
    key(fc, f, scale=0.3, alpha=1)
    key(fc, f + 3, scale=1.8, alpha=0.9)
    key(fc, f + 8, scale=2.4, alpha=0)
    key(fc, IMPACT0 + 44, scale=0, alpha=0)
    tidy(fc, 'impact', interp='LINEAR')
    sc_ = cyl('im_scorch', 1.9, 0.05, M['scorch'], 28, 0.01, loc=(cx, 0, 0.02), ol=0.0)
    key(sc_, IMPACT0, scale=0)
    key(sc_, f + 2, scale=0)
    key(sc_, f + 8, scale=1.0)
    key(sc_, IMPACT0 + 38, scale=1.0)
    key(sc_, IMPACT0 + 44, scale=0)
    tidy(sc_, 'impact')
    gr = torus('im_glowring', 1.6, 0.07, ember, 32, 5, loc=(cx, 0, 0.06))
    key(gr, IMPACT0, scale=0, alpha=1)
    key(gr, f + 2, scale=0.3, alpha=1)
    key(gr, f + 10, scale=1.0, alpha=1)
    key(gr, IMPACT0 + 30, scale=1.0, alpha=0.7)
    key(gr, IMPACT0 + 44, scale=1.05, alpha=0)
    tidy(gr, 'impact', interp='LINEAR')
    # the burning ring: outer ring of 14 flames, inner ring of 6
    for i in range(20):
        outer = i < 14
        if outer:
            a = math.radians(i * 360 / 14 + 5)
            rr, h, w = 1.6, 0.85, 0.2
        else:
            a = math.radians((i - 14) * 60 + 30)
            rr, h, w = 0.95, 0.6, 0.15
        fm = flame('im_ringflame_%d' % i, h, w, FL[i % 3], 0.1, 8, loc=(cx + rr * math.cos(a), rr * math.sin(a), 0.0))
        t0 = f + 5 + (i % 7)
        key(fm, IMPACT0, scale=0)
        key(fm, t0 - 1, scale=0)
        key(fm, t0, scale=(0.3, 0.3, 0.1))
        key(fm, t0 + 4, scale=(1.0, 1.0, 1.35))
        key(fm, t0 + 9, scale=(0.9, 0.9, 1.0))
        key(fm, t0 + 14, scale=(1.0, 1.0, 1.25))
        key(fm, t0 + 20, scale=(0.8, 0.8, 0.9))
        key(fm, IMPACT0 + 41, scale=(0.5, 0.5, 0.45))
        key(fm, IMPACT0 + 44, scale=0)
        tidy(fm, 'impact')
        ease_keys(fm)
    # flying embers
    g = -0.028
    for i in range(12):
        a = rnd.uniform(0, 6.28)
        sp = rnd.uniform(0.05, 0.14)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.2, 0.35)))
        em = sphere('im_ember_%d' % i, 0.06, hot if i % 2 else ember, 6, 4)
        spark_arc(em, (cx, 0, 0.4), v, f + i % 4, g, 26, s=1.2)
    # smoulder smoke
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.6)
        s = sphere('im_smoke_%d' % i, 0.35, smoke, 10, 6)
        t0 = f + 8 + rnd.randint(0, 8)
        p0 = (cx + r * math.cos(a), r * math.sin(a), 0.4)
        p1 = (cx + (r + 0.3) * math.cos(a), (r + 0.3) * math.sin(a), rnd.uniform(2.2, 3.4))
        key(s, IMPACT0, loc=p0, scale=0, alpha=1)
        key(s, t0 - 1, loc=p0, scale=0, alpha=1)
        key(s, t0, loc=p0, scale=0.4, alpha=1)
        key(s, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.3), alpha=0)
        tidy(s, 'impact')
        ease_keys(s)
    return True
