from spearlib import *

NAME = 'SP_46_primal_fang'
N = 46
BG = '#6a4256'        # caldera night
GROUND = '#5e4446'    # ash
TIP = 9.45
TRAIL = 5.2


def mats():
    return dict(
        obs=toon('pf_obsidian', '#3a2f45', '#1c1626', '#6e5a86', spec=1.0, rim=0.6, rimcol='#ff9a4a'),
        ivory=toon('pf_ivory', '#f6ead0', '#c99f78', '#fffaf0', spec=0.8, rim=0.5, rimcol='#ffb070'),
        gold=toon('pf_gold', '#f5b53a', '#b0641e', '#ffe39a', spec=1.0),
        leather=toon('pf_leather', '#9a2d2d', '#5c1620', '#d0574a'),
        bone=toon('pf_bone', '#d9c3a0', '#9a7a5c', '#f4e6cc', spec=0.5),
        magma=glow('pf_magma', '#ff6a1a', 3.2),
        hot=glow('pf_hot', '#ffd25a', 3.6),
    )


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    obs, ivory, gold, leather, bone, magma, hot = (M[k] for k in ('obs', 'ivory', 'gold', 'leather', 'bone', 'magma', 'hot'))
    # ---- tail: obsidian counter-fang with a hot core and a floating ring
    tube('tail_fang', [(0, 0, 1.0), (0.04, 0, 0.6), (0.12, 0, 0.25), (0.2, 0, 0.0)], [0.2, 0.17, 0.1, 0.0], obs, 10)
    sphere('tail_core', 0.15, hot, 10, 6, loc=(0, 0, 1.05))
    torus('tail_collar_a', 0.19, 0.05, gold, 16, 6, loc=(0, 0, 0.95))
    torus('tail_collar_b', 0.17, 0.045, gold, 16, 6, loc=(0, 0, 1.18))
    torus('tail_float_ring', 0.38, 0.035, magma, 28, 5, loc=(0, 0, 0.55), rot=(12, 0, 0))
    # ---- shaft: charred bone with magma seams, leather wraps around the bare grip
    rod('shaft_lo', 0.155, 1.15, 3.3, bone, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, bone, r1=0.145)
    for i, z in enumerate((1.4, 3.75, 5.85)):
        torus('seam_%d' % i, 0.153, 0.025, magma, 16, 5, loc=(0, 0, z), ol=0)
    coil('wrap_lo', 0.178, 0.032, 1.45, 1.88, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.045, gold, 16, 6, loc=(0, 0, 1.92))
    coil('wrap_hi', 0.175, 0.032, 3.1, 3.58, 4, leather, segs=5, phase=1.2)
    torus('wrap_hi_cap', 0.178, 0.045, gold, 16, 6, loc=(0, 0, 3.08))
    # vertebrae column
    for i in range(4):
        z = 4.05 + i * 0.42
        lathe('vert_%d' % i, [(z - 0.12, 0.15), (z - 0.1, 0.25), (z, 0.29), (z + 0.1, 0.25), (z + 0.12, 0.15)], bone, 12, caps=False)
        for s in (-1, 1):
            cone('vert_spur_%d%s' % (i, 'ab'[s > 0]), 0.06, 0.22, obs, 5, loc=(s * 0.26, 0, z), rot=aim((s, 0, 0.5)), ol=0.015)
    # ---- jaw socket: basalt cup with a crown of teeth and two tusks
    lathe('jaw', [(5.95, 0.15), (6.1, 0.3), (6.35, 0.42), (6.6, 0.44), (6.75, 0.36), (6.8, 0)], obs, 16)
    torus('jaw_rim', 0.42, 0.06, gold, 20, 6, loc=(0, 0, 6.6))
    torus('jaw_seam', 0.37, 0.03, magma, 20, 5, loc=(0, 0, 6.2), ol=0)
    for i in range(8):
        a = i * 45 + 22.5
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        cone('tooth_%d' % i, 0.08, 0.32 if i % 2 else 0.24, ivory, 6, loc=(0.38 * ca, 0.38 * sa, 6.6), rot=aim((ca * 0.4, sa * 0.4, 1)), ol=0.015)
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        pts = [(s * 0.35, 0, 6.35), (s * 0.7, 0, 6.5), (s * 0.92, 0, 6.95), (s * 0.88, 0, 7.45)]
        tube('tusk_' + nm, pts, [0.13, 0.11, 0.07, 0.0], ivory, 9)
        torus('tusk_band_' + nm, 0.12, 0.035, gold, 12, 5, loc=(s * 0.62, 0, 6.47), rot=(0, s * 70, 0), ol=0.015)
    # ---- the fang: curved ivory blade with glowing cracks and a hot tip
    fp = [(0, 0, 6.65), (0.06, 0, 7.2), (0.14, 0, 7.8), (0.15, 0, 8.4), (0.08, 0, 8.95), (-0.08, 0, TIP)]
    fr = [0.42, 0.44, 0.38, 0.29, 0.16, 0.0]
    fang = tube('fang', fp, fr, ivory, 12)
    fang.scale = (1.0, 0.62, 1.0)
    tube('fang_tip_glow', [(0.035, 0, 8.6), (0.0, 0, 9.0), (-0.07, 0, 9.36)], [0.11, 0.07, 0.0], hot, 8, scale=(1.08, 0.7, 1.0), ol=0)
    rnd = random.Random(4646)
    for s in (-1, 1):
        for k in range(2):
            z0 = 6.95 + k * 0.75
            pts = []
            for i in range(5):
                z = z0 + i * 0.22
                # stay on the fang's surface (front/back faces y = +-r*0.62)
                t = (z - 6.65) / (TIP - 6.65)
                rr = 0.43 * (1 - t ** 1.6)
                x = 0.1 * math.sin(t * 3) + rnd.uniform(-0.12, 0.12)
                pts.append((x, s * (rr * 0.62 + 0.02), z))
            tube('crack_%s%d' % ('ab'[s > 0], k), pts, [0.0, 0.06, 0.065, 0.05, 0.0], magma, 4, smooth=False, ol=0)
    # ---- floating legendary bits: obsidian shards + broken halo
    for i in range(3):
        a = math.radians(i * 120 + 30)
        crystal('float_shard_%d' % i, 0.09, 0.5, obs, 5, 0.35, 0.6, both=True,
                loc=(0.72 * math.cos(a), 0.72 * math.sin(a), 7.35 + 0.2 * i), rot=aim((math.cos(a) * 0.3, math.sin(a) * 0.3, 1)), ol=0.018)
        sphere('float_ember_%d' % i, 0.06, hot, 8, 5, loc=(0.72 * math.cos(a), 0.72 * math.sin(a), 7.35 + 0.2 * i))
    for k, (a0, a1) in enumerate(((20, 150), (200, 330))):
        pts = [(0.95 * math.cos(math.radians(a)), 0.25, 7.5 + 0.95 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 13)]
        tube('halo_%d' % k, pts, 0.04, gold, 6)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(46)
    fl_o = glow('pf_flame_o', '#ff5a14', 3.0)
    fl_y = glow('pf_flame_y', '#ffc23a', 3.4)
    fl_r = glow('pf_flame_r', '#e0302a', 2.6)
    smoke = ghost('pf_smoke', '#4a3440', 0.6, 0.85, 1.0)
    heat = ghost('pf_heat', '#ff8a3a', 1.6, 0.12, 1.8)
    # ---------------- idle: heat aura on the fang + rising embers
    fx('idle')
    sphere('idle_heat', 0.6, heat, 16, 9, loc=(0.05, 0, 8.0), scale=(1.1, 0.8, 2.1))
    torus('idle_base_glow', 0.46, 0.05, M['hot'], 24, 5, loc=(0, 0, 6.72))
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.3, 0.8)
        flame('idle_ember_%d' % i, rnd.uniform(0.14, 0.24), 0.05, fl_y if i % 2 else fl_o, 0.1, 6,
              loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.6)))
    # ---------------- flight: comet of flame tongues + sparks + fire rings + smoke puffs
    fx('flight')
    flames = [flame('fl_flame_%d' % i, 0.7, 0.16, (fl_o, fl_y, fl_r)[i % 3], 0.0, 8) for i in range(14)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.8, 1.4)) for _ in range(14)]
    # flame tongues point backwards (-Z) along the trail
    stream(flames, lambda t, i: (fj[i][0] * (0.2 + 0.7 * t), fj[i][1] * (0.2 + 0.7 * t), 9.0 - 11.5 * t),
           smax=lambda t, i: fj[i][2] * (1.4 - 0.6 * t) * math.sin(math.pi * t) ** 0.5,
           spin=lambda t, i: (180 + fj[i][0] * 20, fj[i][1] * 20, 0))
    sparks = [sphere('fl_spark_%d' % i, 0.06, fl_y, 6, 4) for i in range(12)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(sparks, lambda t, i: (sj[i][0] * (0.3 + 1.6 * t), sj[i][1] * (0.3 + 1.6 * t), 8.4 - 13.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.6, 0.06, fl_o if i % 2 else fl_y, 28, 6) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.3 - 6.0 * t), smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (0, 0, 360 * t))
    puffs = [sphere('fl_smoke_%d' % i, 0.35, smoke, 12, 7) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.3 + 0.8 * t), pj[i][1] * (0.3 + 0.8 * t), 3.5 - 8.0 * t),
           smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: caldera eruption - glowing cracks, lava ring, fire pillars, molten rocks, smoke
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.8, wobble=4)
    f = IMPACT0 + 4
    cx = 0.5
    flash = sphere('im_flash', 0.5, ghost('pf_flash', '#ffd08a', 2.2, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.4, alpha=0.8)
    key(flash, f + 10, scale=3.2, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    for i in range(9):
        a = math.radians(i * 40 + rnd.uniform(-8, 8))
        L_ = rnd.uniform(1.6, 2.6)
        pts = zigzag((cx, 0, 0.02), (cx + L_ * math.cos(a), L_ * math.sin(a), 0.02), 5, 0.15, seed=i)
        for p in pts:
            p.z = 0.02
        cr = tube('im_crack_%d' % i, pts, [0.11, 0.09, 0.07, 0.05, 0.03, 0.0], M['magma'], 4, smooth=False)
        cr.scale = (1, 1, 0.3)
        key(cr, IMPACT0, scale=0, alpha=1)
        key(cr, f + i % 3, scale=0)
        key(cr, f + 5 + i % 3, scale=(1, 1, 0.3), alpha=1)
        key(cr, IMPACT0 + 34, alpha=1)
        key(cr, IMPACT0 + 44, scale=(1, 1, 0.3), alpha=0)
        tidy(cr, 'impact')
    lava = torus('im_lava_ring', 0.9, 0.14, M['magma'], 32, 6, loc=(cx, 0, 0.02), scale=(1, 1, 0.25))
    key(lava, IMPACT0, scale=0)
    key(lava, f + 2, scale=0)
    key(lava, f + 9, scale=(1.5, 1.5, 0.3))
    key(lava, IMPACT0 + 36, scale=(1.6, 1.6, 0.3))
    key(lava, IMPACT0 + 44, scale=(1.7, 1.7, 0.0))
    tidy(lava, 'impact')
    for i in range(7):
        a = math.radians(i * 360 / 7 + 10)
        r = 1.45
        p = (cx + r * math.cos(a), r * math.sin(a), 0.0)
        fp = flame('im_pillar_%d' % i, 1.6, 0.32, (fl_o, fl_y, fl_r)[i % 3], 0.1, 8, loc=p)
        t0 = f + 3 + i
        key(fp, IMPACT0, scale=0)
        key(fp, t0, scale=(0.4, 0.4, 0.1))
        key(fp, t0 + 4, scale=(1.0, 1.0, 1.25))
        key(fp, t0 + 9, scale=(0.8, 0.8, 0.9))
        key(fp, t0 + 16, scale=(0.3, 0.3, 0.35))
        key(fp, t0 + 20, scale=0)
        tidy(fp, 'impact')
        ease_keys(fp)
    core = flame('im_core_burst', 2.6, 0.55, fl_y, 0.0, 10, loc=(cx, 0, 0))
    key(core, IMPACT0, scale=0)
    key(core, f, scale=(0.5, 0.5, 0.2))
    key(core, f + 5, scale=(1.0, 1.0, 1.1))
    key(core, f + 12, scale=(0.5, 0.5, 0.6))
    key(core, f + 18, scale=0)
    tidy(core, 'impact')
    g = -0.03
    for i in range(10):
        a = math.radians(rnd.uniform(0, 360))
        sp = rnd.uniform(0.07, 0.16)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.28, 0.42)))
        c = rock('im_molten_%d' % i, rnd.uniform(0.1, 0.17), M['obs'] if i % 2 else M['magma'], seed=i + 60, sub=1, rough=0.25, flat=True, ol=0.015)
        p0 = Vector((cx, 0, 0.2))
        key(c, IMPACT0, loc=p0, scale=0)
        key(c, f, loc=p0, scale=0.3)
        t = 0
        while True:
            t += 2
            p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
            done = p.z <= 0.08 or t > 34
            if done:
                p.z = 0.08
            key(c, f + t, loc=p, scale=1, rot=(t * 30, t * 20, 0), interp='LINEAR')
            if done:
                break
        key(c, max(f + t + 2, IMPACT0 + 36), scale=1)
        key(c, IMPACT0 + 44, scale=0)
        tidy(c, 'impact')
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.0)
        s = sphere('im_smoke_%d' % i, 0.4, smoke, 12, 7)
        t0 = f + 4 + rnd.randint(0, 8)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(2.2, 3.6))
        key(s, IMPACT0, loc=p0, scale=0, alpha=1)
        key(s, t0, loc=p0, scale=0.4, alpha=1)
        key(s, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.8, 2.6), alpha=0)
        tidy(s, 'impact')
        ease_keys(s)
    return True
