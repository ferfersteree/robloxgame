from spearlib import *

NAME = 'SP_10_star'
N = 10
BG = '#3e4a86'        # desert night
GROUND = '#3b4378'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'ground_star': 'im_groundstar', 'flying_star': 'im_star_0', 'star_dust': 'im_dust_0',
             'drift_star': 'fl_star_0', 'flash_ring': 'im_ring'}


def mats():
    return dict(
        night=toon('b10_night', '#202c6a', '#10163a', '#4a5cb4', spec=0.4),
        night_lt=toon('b10_night_lt', '#34449a', '#1a2262', '#6a80d8', spec=0.4),
        meteor=toon('b10_meteor', '#4e4a58', '#26222e', '#8a8696', spec=0.7, rim=0.6, rimcol='#ffd27a'),
        meteor_lt=toon('b10_meteor_lt', '#7a7688', '#3e3a4a', '#b8b4c6', spec=0.9, rim=0.5, rimcol='#ffe9a8'),
        gold=toon('b10_gold', '#f4c04a', '#b0701e', '#ffe9a0', spec=1.0),
        silver=toon('b10_silver', '#c8d2e0', '#7a88a0', '#ffffff', spec=1.0),
        violet=toon('b10_violet', '#8a6ae0', '#4a30a0', '#c8b4ff', spec=0.6, emit=0.2),
        star=glow('b10_star', '#ffe27a', 2.2),
        star_w=glow('b10_star_w', '#fff6c8', 2.2),
        teal=glow('b10_teal', '#4ad8e8', 2.2),
        mark=glow('b10_mark', '#ffd24a', 2.2),
        flash=ghost('b10_flash', '#ffe9a8', 2.0, 0.65, 1.2),
        neb=ghost('b10_neb', '#7a5ad8', 1.2, 0.7, 1.1),
    )


def ballistic(c, p0, v, f, g=-0.028, spin=(25, 18), hold=IMPACT0 + 36, rest=0.05, sc=1.0, rot0=0.0):
    p0 = Vector(p0)
    key(c, IMPACT0, loc=p0, scale=0)
    if f - 1 > IMPACT0:
        key(c, f - 1, loc=p0, scale=0)
    key(c, f, loc=p0, scale=0.2 * sc)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= rest or t > 34
        if done:
            p.z = rest
        key(c, f + t, loc=p, scale=sc, rot=(rot0 + t * spin[0], t * spin[1], 0), interp='LINEAR')
        if done:
            break
    key(c, max(f + t + 2, hold), scale=sc)
    key(c, IMPACT0 + 44, scale=0)
    tidy(c, 'impact')
    return p


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    night, night_lt, meteor, meteor_lt, gold, silver, violet, star_g, star_w, teal = (M[k] for k in (
        'night', 'night_lt', 'meteor', 'meteor_lt', 'gold', 'silver', 'violet', 'star', 'star_w', 'teal'))
    # ---- tail: pitted meteorite pommel with a gold ring and a glowing star stud
    rock('tail_meteor', 0.3, meteor, seed=7, sub=1, rough=0.12, loc=(0, 0, 0.4), scale=(1, 1, 0.95))
    torus('tail_ring', 0.2, 0.045, gold, 12, 5, loc=(0, 0, 0.72))
    star('tail_star', 0.16, 0.07, 5, 0.04, star_g, loc=(0, -0.28, 0.35), rot=(90, 0, 0), ol=0)
    # ---- shaft: night-blue lacquer with gold star inlays, bare grip zone
    rod('shaft_lo', 0.155, 0.8, 3.3, night, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.1, night_lt, segs=12, r1=0.14)
    coil('wrap_lo', 0.18, 0.03, 1.35, 1.88, 4, silver, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, gold, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.62, 4, silver, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, gold, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((1.1, 4.0, 4.5, 5.0, 5.5)):
        a = i * 2.2 + 0.4
        ca, sa = math.cos(a), math.sin(a)
        star('inlay_%d' % i, 0.12, 0.05, 5, 0.03, gold if i % 2 else star_g, loc=(0.152 * ca, 0.152 * sa, z), rot=aim((ca, sa, 0.0), 0), ol=0.01)
    for i, z in enumerate((4.2, 4.75)):
        torus('band_%d' % i, 0.148, 0.025, (violet, teal)[i], 12, 5, loc=(0, 0, z), ol=0.012)
    # ---- socket with rivets
    lathe('socket', [(5.95, 0.14), (6.15, 0.21), (6.4, 0.27), (6.65, 0.29), (6.8, 0.22), (6.8, 0)], silver, 14)
    torus('socket_ring', 0.28, 0.05, gold, 14, 5, loc=(0, 0, 6.3))
    for i in range(4):
        a = math.radians(i * 90 + 45)
        sphere('rivet_%d' % i, 0.05, gold, 7, 4, loc=(0.26 * math.cos(a), 0.26 * math.sin(a), 6.55), ol=0.012)
    # ---- star-shaped guard (vertical, behind the blade) + meteorite blade
    star('guard', 0.98, 0.42, 5, 0.14, gold, loc=(0, 0, 7.05), rot=(90, 0, 0))
    star('guard_inner', 0.62, 0.28, 5, 0.18, meteor_lt, loc=(0, 0, 7.05), rot=(90, 0, 0), ol=0.012)
    bl = [(0.26, 6.8), (0.5, 7.2), (0.62, 7.8), (0.5, 8.4), (0.28, 8.9), (0.0, TIP),
          (-0.28, 8.9), (-0.5, 8.4), (-0.62, 7.8), (-0.5, 7.2), (-0.26, 6.8)]
    blade('blade', bl, 0.17, meteor)
    blade('blade_core', [(x * 0.55, 7.0 + (z - 6.8) * 0.85) for (x, z) in bl], 0.2, meteor_lt, ol=0.012)
    for i, (x, z, sg) in enumerate(((0.3, 7.4, 1), (-0.28, 8.6, -1), (0.18, 8.7, 1))):
        rock('pit_%d' % i, 0.09, meteor, seed=i + 3, sub=1, rough=0.2, flat=True, loc=(x, sg * 0.16, z), scale=(1.2, 0.5, 1.0), ol=0.01)
    star('blade_star_f', 0.34, 0.15, 5, 0.1, star_w, loc=(0, -0.2, 8.0), rot=(90, 0, 0), ol=0)
    star('blade_star_b', 0.34, 0.15, 5, 0.1, star_w, loc=(0, 0.2, 8.0), rot=(90, 0, 0), ol=0)
    # ---- star charms on a night cord
    tube('charm_cord', [(0.2, 0.04, 5.95), (0.32, 0.08, 5.7), (0.36, 0.1, 5.5)], 0.02, night, 5)
    for i, (z, r_) in enumerate(((5.7, 0.12), (5.45, 0.16), (5.15, 0.2))):
        star('charm_star_%d' % i, r_, r_ * 0.45, 5, 0.04, (gold, star_g, violet)[i], loc=(0.36, 0.1 + 0.01 * i, z), rot=(90, 0, 15 * i), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1010)
    star_g, star_w, teal, mark, flash_m, neb = M['star'], M['star_w'], M['teal'], M['mark'], M['flash'], M['neb']
    # ---------------- idle: a few small stars and motes near the head
    fx('idle')
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.7, 1.0)
        star('idle_star_%d' % i, rnd.uniform(0.1, 0.16), 0.04, 5, 0.02, star_g if i % 2 else star_w,
             loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.2)), rot=(90, 0, rnd.uniform(0, 70)))
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        sphere('idle_mote_%d' % i, 0.04, teal, 6, 4, loc=(0.6 * math.cos(a), 0.6 * math.sin(a), rnd.uniform(7.2, 9.3)))
    # ---------------- flight: tumbling stars, sparks, star rings, nebula puffs
    fx('flight')
    sts = [star('fl_star_%d' % i, 0.2, 0.08, 5, 0.03, star_g if i % 2 else star_w, rot=(90, 0, 0)) for i in range(10)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(sts, lambda t, i: (sj[i][0] * (0.3 + 1.0 * t), sj[i][1] * (0.3 + 1.0 * t), 8.8 - 12.5 * t),
           smax=lambda t, i: 1.2 * math.sin(math.pi * t) ** 0.5, spin=lambda t, i: (90, 0, sj[i][2] + 540 * t))
    sp = [sphere('fl_spark_%d' % i, 0.05, teal, 6, 4) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(sp, lambda t, i: (pj[i][0] * (0.2 + 1.3 * t), pj[i][1] * (0.2 + 1.3 * t), 8.3 - 12.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.5, 0.045, mark, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.4 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    nb = [sphere('fl_neb_%d' % i, 0.3, neb, 10, 6) for i in range(5)]
    nj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(5)]
    stream(nb, lambda t, i: (nj[i][0] * (0.2 + 0.8 * t), nj[i][1] * (0.2 + 0.8 * t), 6.8 - 10.0 * t),
           smax=lambda t, i: (0.5 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: flash, five stars fly out in a circle and fall, a star-shaped glow mark stays on the ground
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.35))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.4, alpha=0.8)
    key(fl, f + 11, scale=3.2, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    rg = torus('im_ring', 0.5, 0.05, mark, 32, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 13, scale=5.0, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    # the ground mark: big flat five-point star that glows, spins slightly and fades slowly
    gs = star('im_groundstar', 2.0, 0.85, 5, 0.04, mark, loc=(cx, 0, 0.03))
    key(gs, IMPACT0, scale=0, alpha=1, rot=(0, 0, 0))
    key(gs, f + 2, scale=0.2, alpha=1, rot=(0, 0, -40))
    key(gs, f + 10, scale=1.0, alpha=1, rot=(0, 0, 0))
    key(gs, IMPACT0 + 32, scale=1.0, alpha=0.7, rot=(0, 0, 6))
    key(gs, IMPACT0 + 44, scale=1.05, alpha=0, rot=(0, 0, 8))
    tidy(gs, 'impact', interp='LINEAR')
    gi = star('im_groundstar_in', 1.0, 0.42, 5, 0.04, star_w, loc=(cx, 0, 0.05), rot=(0, 0, 36))
    key(gi, IMPACT0, scale=0, alpha=1)
    key(gi, f + 2, scale=0.2, alpha=1)
    key(gi, f + 10, scale=1.0, alpha=1)
    key(gi, IMPACT0 + 30, scale=1.0, alpha=0.6)
    key(gi, IMPACT0 + 44, scale=1.1, alpha=0)
    tidy(gi, 'impact', interp='LINEAR')
    # five big stars launch up and out on a circle, spin and fall
    for k in range(5):
        a = math.radians(k * 72 + 18)
        ca, sa = math.cos(a), math.sin(a)
        st = star('im_star_%d' % k, 0.4, 0.17, 5, 0.1, star_g if k % 2 else star_w, rot=(90, 0, 0), ol=0)
        t0 = f + k
        spn = 720 if k % 2 else -720
        key(st, IMPACT0, loc=(cx, 0, 0.4), scale=0, alpha=1, rot=(90, 0, 0))
        key(st, t0 - 1, loc=(cx, 0, 0.4), scale=0, alpha=1, rot=(90, 0, 0))
        key(st, t0, loc=(cx, 0, 0.4), scale=0.3, alpha=1, rot=(90, 0, 0))
        key(st, t0 + 6, loc=(cx + 0.9 * ca, 0.9 * sa, 2.4), scale=1.3, alpha=1, rot=(90, 0, spn * 0.35))
        key(st, t0 + 14, loc=(cx + 1.7 * ca, 1.7 * sa, 2.7), scale=1.1, alpha=1, rot=(90, 0, spn * 0.7))
        key(st, t0 + 24, loc=(cx + 2.2 * ca, 2.2 * sa, 0.45), scale=0.9, alpha=1, rot=(90, 0, spn))
        key(st, t0 + 30, loc=(cx + 2.25 * ca, 2.25 * sa, 0.3), scale=0.6, alpha=0.6, rot=(90, 0, spn))
        key(st, IMPACT0 + 44, scale=0, alpha=0)
        tidy(st, 'impact')
        ease_keys(st)
    # small sparkle stars follow on a wider circle
    for k in range(10):
        a = math.radians(k * 36 + 9)
        ca, sa = math.cos(a), math.sin(a)
        ss = star('im_sparkle_%d' % k, 0.15, 0.06, 4, 0.03, teal if k % 2 else star_g, rot=(90, 0, 0), ol=0)
        t0 = f + 3 + k % 4
        key(ss, IMPACT0, loc=(cx, 0, 0.4), scale=0, alpha=1)
        key(ss, t0 - 1, loc=(cx, 0, 0.4), scale=0, alpha=1)
        key(ss, t0, loc=(cx, 0, 0.4), scale=0.3, alpha=1)
        key(ss, t0 + 8, loc=(cx + 1.4 * ca, 1.4 * sa, 1.6), scale=1.1, alpha=1)
        key(ss, t0 + 18, loc=(cx + 2.6 * ca, 2.6 * sa, 0.5), scale=0.7, alpha=0.5)
        key(ss, t0 + 24, loc=(cx + 2.8 * ca, 2.8 * sa, 0.2), scale=0.2, alpha=0)
        key(ss, IMPACT0 + 44, scale=0, alpha=0)
        tidy(ss, 'impact')
    # stardust rising from the mark
    for i in range(18):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.2, 1.9)
        dp = sphere('im_dust_%d' % i, 0.06, star_g if i % 2 else teal, 6, 4)
        t0 = f + rnd.randint(2, 18)
        p0 = (cx + rr * math.cos(a), rr * math.sin(a), 0.1)
        p1 = (cx + (rr + 0.2) * math.cos(a), (rr + 0.2) * math.sin(a), rnd.uniform(1.4, 3.0))
        key(dp, IMPACT0, loc=p0, scale=0, alpha=1)
        key(dp, t0 - 1, loc=p0, scale=0, alpha=1)
        key(dp, t0, loc=p0, scale=0.3, alpha=1)
        key(dp, t0 + 8, scale=1.2, alpha=1)
        key(dp, min(t0 + 24, IMPACT0 + 43), loc=p1, scale=0.2, alpha=0)
        key(dp, IMPACT0 + 44, scale=0, alpha=0)
        tidy(dp, 'impact')
    # meteorite chips
    for i in range(6):
        a = math.radians(rnd.uniform(0, 360))
        s_ = rnd.uniform(0.08, 0.15)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.22, 0.34)))
        c = rock('im_chip_%d' % i, rnd.uniform(0.08, 0.14), M['meteor'] if i % 2 else M['meteor_lt'], seed=i + 50, sub=1, rough=0.25, flat=True)
        ballistic(c, (cx, 0, 0.15), v, f, rot0=rnd.uniform(0, 360))
    # violet nebula puffs
    for i in range(4):
        a = math.radians(i * 90 + 20)
        rr = rnd.uniform(0.9, 1.6)
        p = sphere('im_neb_%d' % i, 0.32, neb, 10, 6)
        end = (cx + rr * math.cos(a), rr * math.sin(a), 0.8)
        key(p, IMPACT0, loc=(cx, 0, 0.3), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.3), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=1.3, alpha=0.8)
        key(p, IMPACT0 + 44, loc=(end[0], end[1], end[2] + 0.6), scale=1.9, alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
