from spearlib import *

NAME = 'SP_39_astral_armillary'
N = 39
BG = '#2c3c70'        # starry night
GROUND = '#202e56'
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'armillary_ring': 'im_ring_0', 'star': 'im_star_0', 'ground_star': 'im_groundstar'}


def mats():
    return dict(
        gold=toon('ar_gold', '#ffc83a', '#b8641c', '#fff0a0', spec=1.0, rim=0.6, rimcol='#fff6c0'),
        gold2=toon('ar_gold2', '#ffe27a', '#d0902c', '#fffbd0', spec=1.0, emit=0.2),
        night=toon('ar_night', '#27357a', '#141b4a', '#5a70d0', spec=0.8, rimcol='#8aa0ff'),
        navy=toon('ar_navy', '#182052', '#0a0f30', '#3a4a9a'),
        silver=toon('ar_silver', '#dfe6ff', '#7a86b8', '#ffffff', spec=1.0),
        sun=glow('ar_sun', '#ffe680', 3.4),
        cyan=glow('ar_cyan', '#7ae8ff', 3.0),
        pink=glow('ar_pink', '#ff8ad8', 3.0),
        hot=glow('ar_hot', '#fffbe0', 3.6),
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
    gold, gold2, night, navy, silver, sun, cyan, pink, hot = (M[k] for k in ('gold', 'gold2', 'night', 'navy', 'silver', 'sun', 'cyan', 'pink', 'hot'))
    # ---- tail: mini armillary globe
    sphere('tail_globe', 0.26, night, 12, 7, loc=(0, 0, 0.36))
    torus('tail_orbit_a', 0.38, 0.04, gold, 16, 5, loc=(0, 0, 0.36), rot=(65, 0, 0))
    torus('tail_orbit_b', 0.38, 0.04, gold2, 16, 5, loc=(0, 0, 0.36), rot=(-65, 0, 45))
    sphere('tail_star', 0.09, sun, 8, 5, loc=(0, 0, 0.0 + 0.1), ol=0)
    # ---- shaft: midnight lacquer, gold rings, star studs
    shaft_parts(night, navy, gold, silver)
    for i in range(5):
        a = i * 1.3
        star('shaft_star_%d' % i, 0.09, 0.04, 5, 0.04, sun, loc=(0.16 * math.cos(a), 0.16 * math.sin(a), 4.2 + i * 0.33),
             rot=aim((math.cos(a), math.sin(a), 0), 0), ol=0)
    # ---- socket: gold crown cup with four prongs that hold the inner ring
    lathe('socket', [(6.3, 0.14), (6.45, 0.22), (6.7, 0.32), (6.95, 0.28), (7.05, 0.15), (7.1, 0)], gold, 14)
    torus('socket_ring', 0.3, 0.055, navy, 14, 5, loc=(0, 0, 6.55))
    torus('socket_ring_b', 0.28, 0.04, sun, 14, 4, loc=(0, 0, 6.9), ol=0)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        tube('prong_%d' % i, [(0.28 * math.cos(a), 0.28 * math.sin(a), 6.9), (0.5 * math.cos(a), 0.5 * math.sin(a), 7.3), (0.52 * math.cos(a), 0.52 * math.sin(a), 7.8)],
             [0.07, 0.06, 0.0], gold2, 6)
    # ---- the tip: layered golden blade with a bright core
    ol_ = [(0, 6.95), (0.34, 7.4), (0.42, 8.1), (0.26, 8.8), (0, TIP), (-0.26, 8.8), (-0.42, 8.1), (-0.34, 7.4)]
    blade('tip', ol_, 0.14, gold)
    blade('tip_core', [(x * 0.5, 7.4 + (z - 6.95) * 0.75) for (x, z) in ol_], 0.17, sun, ol=0)
    sphere('tip_gem', 0.17, hot, 10, 6, loc=(0, 0, 8.0), ol=0)
    # ---- floating armillary: three tilted gold rings around the head, planets on them, loose stars
    c = 8.0
    for i, (R, rot, m) in enumerate(((1.15, (0, 0, 0), gold), (1.0, (62, 0, 0), gold2), (0.86, (-62, 0, 60), gold))):
        torus('orbit_ring_%d' % i, R, 0.055, m, 22, 4, loc=(0, 0, c), rot=rot)
        torus('orbit_inner_%d' % i, R - 0.09, 0.025, [cyan, pink, sun][i], 18, 4, loc=(0, 0, c), rot=rot, ol=0)
    for i, (a, R, tilt, m) in enumerate(((20, 1.15, 0, cyan), (200, 1.15, 0, pink), (110, 1.0, 62, sun), (300, 1.0, 62, cyan), (60, 0.86, -62, pink))):
        ar = math.radians(a)
        t = math.radians(tilt)
        sphere('planet_%d' % i, 0.12, m, 8, 5, loc=(R * math.cos(ar), R * math.sin(ar) * math.cos(t), c + R * math.sin(ar) * math.sin(t)), ol=0)
    for i in range(4):
        a = math.radians(i * 90 + 50)
        star('float_star_%d' % i, 0.17, 0.07, 5, 0.06, sun if i % 2 else hot, loc=(1.35 * math.cos(a), 1.35 * math.sin(a), 7.2 + 0.6 * i), rot=(90, 0, i * 20), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def arc_orbit(ob, tilt, r, a0, turns, t0, t1, zc=1.3, cx=0.45):
    tl = math.radians(tilt)
    key(ob, IMPACT0, loc=(cx, 0, zc), scale=0)
    for t in range(t0, t1 + 1, 2):
        u = (t - t0) / float(t1 - t0)
        ang = math.radians(a0 + turns * 360 * u)
        rr = r * (0.3 + 0.7 * math.sin(math.pi * 0.5 * min(1.0, u * 2.0)))
        key(ob, t, loc=(cx + rr * math.cos(ang), rr * math.sin(ang) * math.cos(tl), zc + rr * math.sin(ang) * math.sin(tl)),
            scale=1.0 * (1 - max(0.0, u - 0.7) / 0.3) + 0.0001)
    key(ob, t1 + 2, scale=0)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact', interp='LINEAR')


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
    rnd = random.Random(3939)
    aura = ghost('ar_aura', '#ffe8a0', 1.2, 0.05, 1.8)
    tw = glow('ar_twinkle', '#fffbe0', 3.2)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.1), scale=(1.5, 1.0, 1.7))
    for i in range(4):
        star('idle_twinkle_%d' % i, 0.16, 0.035, 4, 0.02, tw, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.2), -0.3, 7.0 + i * 0.8), rot=(90, 0, 0))
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.4)
        sphere('idle_mote_%d' % i, rnd.uniform(0.04, 0.08), tw, 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.6)))
    # ---------------- flight
    fx('flight')
    sts = [star('fl_star_%d' % i, 0.2, 0.08, 5, 0.06, (M['sun'], tw, M['cyan'])[i % 3], ol=0) for i in range(10)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(sts, lambda t, i: (sj[i][0] * (0.4 + 1.1 * t), sj[i][1] * (0.4 + 1.1 * t), 8.6 - 12.5 * t), smax=1.2,
           spin=lambda t, i: (90, sj[i][2], sj[i][2] + 540 * t))
    rings = [torus('fl_ring_%d' % i, 0.6, 0.045, (M['sun'], M['cyan'], M['pink'])[i], 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (50 * (i - 1), 30 * (1 - i), 360 * t))
    sps = [sphere('fl_spark_%d' % i, 0.06, tw, 6, 4) for i in range(10)]
    kj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(sps, lambda t, i: (kj[i][0] * (0.3 + 1.6 * t), kj[i][1] * (0.3 + 1.6 * t), 8.4 - 12.0 * t), smax=1.3)
    dust = ghost('ar_dust', '#ffd870', 1.3, 0.8, 1.0)
    dps = [sphere('fl_dust_%d' % i, 0.28, dust, 10, 6) for i in range(5)]
    dj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(5)]
    stream(dps, lambda t, i: (dj[i][0] * (0.2 + 0.7 * t), dj[i][1] * (0.2 + 0.7 * t), 8.0 - 11.0 * t),
           smax=lambda t, i: (0.5 + 1.2 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: armillary rings expand at different tilts and spin, golden stars sparkle
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6, wobble=4)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.6, ghost('ar_flash', '#fff0b0', 2.0, 0.7, 1.2), 14, 8, loc=(cx, 0, 0.4))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 5, scale=2.4, alpha=0.7)
    key(flash, f + 12, scale=3.2, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    gs = star('im_groundstar', 1.6, 0.75, 8, 0.05, M['sun'], loc=(cx, 0, 0.03), ol=0)
    key(gs, IMPACT0, scale=0, alpha=1, rot=(0, 0, 0))
    key(gs, f + 2, scale=0.4, alpha=1, rot=(0, 0, 0))
    key(gs, f + 14, scale=1.5, alpha=1, rot=(0, 0, 90))
    key(gs, IMPACT0 + 44, scale=1.7, alpha=0, rot=(0, 0, 160))
    tidy(gs, 'impact')
    for i in range(6):
        tilt = (0, 60, -60, 30, -30, 90)[i]
        m = (M['sun'], M['cyan'], M['pink'], M['sun'], M['cyan'], M['hot'])[i]
        rg = torus('im_ring_%d' % i, 0.7 + 0.1 * (i % 3), 0.05, m, 32, 5, loc=(cx, 0, 1.3))
        t0 = f + i
        key(rg, IMPACT0, scale=0, alpha=1, rot=(tilt, 0, 0))
        key(rg, t0, scale=0.4, alpha=1, rot=(tilt, 0, 0))
        key(rg, t0 + 18, scale=2.2 + 0.25 * i, alpha=0.9, rot=(tilt, 0, 360 * (1 if i % 2 else -1)))
        key(rg, IMPACT0 + 44, scale=2.8 + 0.25 * i, alpha=0, rot=(tilt, 0, 560 * (1 if i % 2 else -1)))
        tidy(rg, 'impact')
        ease_keys(rg)
    for i in range(6):
        pl = sphere('im_planet_%d' % i, 0.14, (M['cyan'], M['pink'], M['sun'])[i % 3], 8, 5, ol=0)
        arc_orbit(pl, (0, 60, -60)[i % 3], 1.9 + 0.25 * (i // 3), i * 55, 1.0, f + 2, f + 32, 1.3)
    for i in range(14):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.8, 2.6)
        st = star('im_star_%d' % i, rnd.uniform(0.16, 0.26), 0.07, 5, 0.05, M['sun'] if i % 2 else tw, rot=(90, 0, 0), ol=0)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.6)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.0, 3.2))
        key(st, IMPACT0, loc=p0, scale=0, alpha=1, rot=(90, 0, 0))
        key(st, f + 1 + i % 5, loc=p0, scale=0.3, alpha=1, rot=(90, 0, 0))
        key(st, f + 12, loc=p1, scale=1.3, alpha=1, rot=(90, 0, 200))
        key(st, IMPACT0 + 44, loc=(p1[0], p1[1], p1[2] + 0.4), scale=0.2, alpha=0, rot=(90, 0, 520))
        tidy(st, 'impact')
        ease_keys(st)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.0)
        sp_ = sphere('im_spark_%d' % i, 0.07, tw, 6, 4, ol=0)
        fly(sp_, (cx, 0, 0.3), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.6, 2.4)), f + i, 1.2)
    for i in range(6):
        a = math.radians(i * 60 + 30)
        r = rnd.uniform(1.5, 2.6)
        dm = star('im_dust_%d' % i, 0.12, 0.05, 4, 0.03, M['hot'], rot=(90, 0, 0), ol=0)
        fly(dm, (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.4), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(2.4, 3.8)), f + 4 + i, 1.0)
    return True
