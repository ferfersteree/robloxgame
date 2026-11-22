from spearlib import *

NAME = 'SP_37_rift_shards'
N = 37
BG = '#4e3a72'        # rift dusk
GROUND = '#3b2b58'
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'rift_disc': 'im_rift', 'rift_rim': 'im_rift_rim', 'shard': 'im_shard_0', 'crack': 'im_crack_0'}


def mats():
    return dict(
        obs=toon('rs_obs', '#2a2038', '#120c1e', '#6a5290', spec=1.0, rim=0.7, rimcol='#c070ff'),
        obs2=toon('rs_obs2', '#443358', '#201530', '#8a70b4', spec=0.9, rim=0.6, rimcol='#e090ff'),
        silver=toon('rs_silver', '#c8c4dc', '#6c6690', '#f4f2ff', spec=1.0),
        plum=toon('rs_plum', '#7a2fb0', '#3d1470', '#b66cf0', emit=0.2),
        vio=glow('rs_vio', '#b45cff', 3.2),
        pink=glow('rs_pink', '#ff7ae8', 3.4),
        hot=glow('rs_hot', '#f2d2ff', 3.6),
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
    obs, obs2, silver, plum, vio, pink, hot = (M[k] for k in ('obs', 'obs2', 'silver', 'plum', 'vio', 'pink', 'hot'))
    # ---- tail: broken-crystal counterweight with a floating shard
    crystal('tail_crystal', 0.2, 0.9, obs, 6, 0.4, 0.7, loc=(0, 0, 0.95), rot=(180, 0, 0))
    sphere('tail_core', 0.11, vio, 8, 5, loc=(0, 0, 0.58), ol=0)
    torus('tail_ring', 0.2, 0.045, silver, 12, 5, loc=(0, 0, 0.7))
    crystal('tail_float_shard', 0.07, 0.4, plum, 5, 0.35, 0.6, both=True, loc=(0.3, 0.1, 0.4), rot=(160, 20, 0), ol=0.015)
    # ---- shaft: black glass lacquer, silver rings, violet seams
    shaft_parts(obs, plum, silver, vio)
    for i in range(2):
        a = i * 3.0
        crystal('shaft_stud_%d' % i, 0.05, 0.2, vio, 5, 0.4, 0.8, loc=(0.15 * math.cos(a), 0.15 * math.sin(a), 5.2 + i * 0.5),
                rot=aim((math.cos(a), math.sin(a), 0.2)), ol=0)
    # ---- socket: obsidian claw cup with glowing seam
    lathe('socket', [(6.3, 0.14), (6.45, 0.22), (6.75, 0.34), (7.0, 0.3), (7.15, 0.0)], obs, 12)
    torus('socket_rim', 0.33, 0.055, silver, 14, 5, loc=(0, 0, 6.72))
    torus('socket_seam', 0.3, 0.035, vio, 14, 4, loc=(0, 0, 6.5), ol=0)
    for i in range(5):
        a = math.radians(i * 72 + 18)
        crystal('claw_%d' % i, 0.1, 0.9 if i % 2 else 0.7, obs2, 5, 0.4, 0.8, loc=(0.34 * math.cos(a), 0.34 * math.sin(a), 6.85),
                rot=aim((math.cos(a) * 0.6, math.sin(a) * 0.6, 1)), ol=0.018)
    # ---- the head: tall black crystal with a violet glowing core
    crystal('head', 0.48, TIP - 6.95, obs, 6, 0.42, 0.75, loc=(0, 0, 6.95))
    crystal('head_core', 0.25, TIP - 7.5, vio, 6, 0.42, 0.7, loc=(0, 0, 7.3), ol=0)
    crystal('head_ridge_a', 0.16, 1.5, obs2, 5, 0.4, 0.8, loc=(0.4, 0.06, 7.25), rot=(0, 12, 0), ol=0.015)
    crystal('head_ridge_b', 0.14, 1.3, obs2, 5, 0.4, 0.8, loc=(-0.4, -0.06, 7.3), rot=(0, -12, 0), ol=0.015)
    # ---- floating shard cloud (two orbit layers) + broken halos
    for i in range(10):
        a = math.radians(i * 36 + (14 if i % 2 else 0))
        r = 0.85 if i % 2 else 1.25
        z = 6.9 + 0.2 * i
        crystal('float_shard_%d' % i, 0.07 + 0.012 * (i % 3), 0.45 + 0.1 * (i % 4), obs if i % 3 else plum, 5, 0.35, 0.6, both=True,
                loc=(r * math.cos(a), r * math.sin(a), z), rot=aim((math.cos(a) * 0.5, math.sin(a) * 0.5, 1), i * 40), ol=0.016)
    for i in range(4):
        a = math.radians(i * 90 + 30)
        sphere('float_spark_%d' % i, 0.07, hot, 8, 5, loc=(1.05 * math.cos(a), 1.05 * math.sin(a), 7.4 + i * 0.55), ol=0)
    for k, (a0, a1) in enumerate(((10, 140), (190, 320))):
        pts = [(1.1 * math.cos(math.radians(a)), 0.3, 8.0 + 1.1 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 16)]
        tube('halo_%d' % k, pts, [0.0] + [0.04] * (len(pts) - 2) + [0.0], pink if k else vio, 6, ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def orbit(ob, a0, r0, z0, t0, t1, turns, s, cx=0.45):
    """spiral inwards over frames t0..t1 and vanish at the centre"""
    key(ob, IMPACT0, loc=(cx, 0, z0), scale=0)
    for t in range(t0, t1 + 1, 2):
        u = (t - t0) / float(t1 - t0)
        ang = math.radians(a0 + turns * 360 * u)
        r = r0 * (1 - u) ** 1.1
        key(ob, t, loc=(cx + r * math.cos(ang), r * math.sin(ang), 0.3 + z0 * (1 - u)), scale=s * min(1.0, 0.2 + u * 6) * (1 - u ** 3),
            rot=(u * 500, u * 360, a0))
    key(ob, t1 + 2, scale=0)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact', interp='LINEAR')


def build_fx(M):
    rnd = random.Random(3737)
    smoke = ghost('rs_smoke', '#5a2a8a', 1.1, 0.85, 1.0)
    aura = ghost('rs_aura', '#b06cff', 1.2, 0.05, 1.8)
    voidm = ghost('rs_void', '#0e0618', 0.8, 0.9, 0.8)
    sp = glow('rs_spark', '#f0d0ff', 3.2)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.1), scale=(1.5, 1.0, 1.7))
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.2)
        sphere('idle_mote_%d' % i, rnd.uniform(0.04, 0.08), sp if i % 2 else M['vio'], 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.8)))
    for i in range(2):
        star('idle_glint_%d' % i, 0.15, 0.035, 4, 0.02, sp, loc=(rnd.choice((-1, 1)) * 0.6, -0.3, 7.8 + i * 0.9), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    sh = [crystal('fl_shard_%d' % i, 0.08, 0.5, M['obs'] if i % 3 else M['plum'], 5, 0.35, 0.6, both=True, ol=0.014) for i in range(12)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(12)]
    stream(sh, lambda t, i: (sj[i][0] * (0.35 + 1.0 * t), sj[i][1] * (0.35 + 1.0 * t), 8.8 - 12.5 * t), smax=1.1,
           spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    puffs = [sphere('fl_smoke_%d' % i, 0.32, smoke, 10, 6) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.8 * t), pj[i][1] * (0.2 + 0.8 * t), 8.0 - 11.0 * t),
           smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, M['vio'] if i % 2 else M['pink'], 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    sps = [sphere('fl_spark_%d' % i, 0.06, sp, 6, 4) for i in range(8)]
    kj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(sps, lambda t, i: (kj[i][0] * (0.3 + 1.6 * t), kj[i][1] * (0.3 + 1.6 * t), 8.4 - 12.0 * t), smax=1.3)
    # ---------------- impact: a rift opens, shards and motes are sucked in, then it implodes
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6, wobble=4)
    f = IMPACT0 + 4
    cx = 0.45
    disc = sphere('im_rift', 1.0, voidm, 16, 8, loc=(cx, 0, 0.03))
    rim = torus('im_rift_rim', 1.0, 0.07, M['vio'], 36, 5, loc=(cx, 0, 0.05), ol=0)
    rim2 = torus('im_rift_rim2', 1.0, 0.04, M['pink'], 36, 4, loc=(cx, 0, 0.07), ol=0)
    for ob, k in ((disc, (3.0, 3.0, 0.06)), (rim, (3.0, 3.0, 0.25)), (rim2, (2.4, 2.4, 0.2))):
        key(ob, IMPACT0, scale=0, alpha=1)
        key(ob, f, scale=(0.3 * k[0] / 3, 0.3 * k[1] / 3, k[2]), alpha=1)
        key(ob, f + 8, scale=k, alpha=1)
        key(ob, f + 28, scale=(k[0] * 1.05, k[1] * 1.05, k[2]), alpha=1)
        key(ob, f + 34, scale=(0.15, 0.15, k[2]), alpha=1)
        key(ob, f + 36, scale=0, alpha=0)
        tidy(ob, 'impact')
    for i in range(6):
        a = math.radians(i * 60 + 20)
        L_ = rnd.uniform(1.6, 2.4)
        pts = zigzag((0, 0, 0.0), (L_ * math.cos(a), L_ * math.sin(a), 0.0), 4, 0.15, seed=i + 7)
        cr = tube('im_crack_%d' % i, pts, [0.0, 0.07, 0.07, 0.05, 0.0], M['vio'], 4, smooth=False, ol=0, loc=(cx, 0, 0.04))
        key(cr, IMPACT0, scale=0, alpha=1)
        key(cr, f + 2, scale=(1, 1, 0.3), alpha=1)
        key(cr, f + 30, scale=(1, 1, 0.3), alpha=1)
        key(cr, f + 36, scale=0, alpha=0)
        tidy(cr, 'impact')
    for i in range(10):
        c = crystal('im_shard_%d' % i, 0.1, 0.55, M['obs'] if i % 3 else M['plum'], 5, 0.35, 0.6, both=True, ol=0.016)
        orbit(c, i * 36, rnd.uniform(2.3, 3.2), rnd.uniform(0.8, 2.2), f + i % 3, f + 28 + i % 3, 1.3, 1.2)
    for i in range(16):
        m_ = sphere('im_mote_%d' % i, 0.07, sp if i % 2 else M['vio'], 6, 4, ol=0)
        orbit(m_, i * 22.5, rnd.uniform(1.8, 3.4), rnd.uniform(0.3, 1.8), f + 2, f + 26 + i % 4, 1.6, 1.4)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(1.0, 2.8)
        em = sphere('im_ember_%d' % i, 0.08, sp, 6, 4, ol=0)
        key(em, IMPACT0, loc=(cx, 0, 0.5), scale=0, alpha=1)
        key(em, f + 34, loc=(cx, 0, 0.5), scale=0.4, alpha=1)
        key(em, IMPACT0 + 44, loc=(cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.8, 2.6)), scale=1.2, alpha=0)
        tidy(em, 'impact')
        ease_keys(em)
    pop = sphere('im_implode', 0.5, ghost('rs_pop', '#e6b8ff', 2.2, 0.8, 1.2, edge=True), 16, 8, loc=(cx, 0, 0.5))
    key(pop, IMPACT0, scale=0, alpha=1)
    key(pop, f + 32, scale=0.3, alpha=1)
    key(pop, f + 35, scale=3.0, alpha=0.8)
    key(pop, f + 40, scale=4.2, alpha=0)
    tidy(pop, 'impact', interp='LINEAR')
    sh_ = torus('im_shock', 0.6, 0.07, M['pink'], 36, 5, loc=(cx, 0, 0.08))
    key(sh_, IMPACT0, scale=0, alpha=1)
    key(sh_, f + 33, scale=0.3, alpha=1)
    key(sh_, f + 40, scale=5.0, alpha=0)
    tidy(sh_, 'impact', interp='LINEAR')
    ease_keys(sh_)
    return True
