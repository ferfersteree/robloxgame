from spearlib import *

NAME = 'SP_06_obsidian'
N = 6
BG = '#b08560'        # savanna dusk
GROUND = '#cf9e68'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'glass_spike': 'im_spike_0', 'glass_shard': 'im_shard_0', 'ember_ring': 'im_ring',
             'drift_shard': 'fl_shard_0'}


def mats():
    return dict(
        obs=toon('b06_obs', '#2a2236', '#120c1a', '#6a5a88', spec=1.0, rim=0.7, rimcol='#ff6a4a'),
        obs_lt=toon('b06_obs_lt', '#5a3f8a', '#2a1a52', '#a88ae0', spec=1.0, rim=0.6, rimcol='#ffb0a0', emit=0.15),
        wood=toon('b06_wood', '#8a5a3a', '#52301c', '#b88458'),
        wood_dk=toon('b06_wood_dk', '#6a4228', '#3e2414', '#9a6a44'),
        cord=toon('b06_cord', '#c8322a', '#7a1620', '#f06a56', spec=0.2),
        leather=toon('b06_leather', '#4a3426', '#281a12', '#7a5a42'),
        bone=toon('b06_bone', '#efe2c2', '#b8a07a', '#fffaf0'),
        ember=glow('b06_ember', '#ff6a4a', 2.2),
        hot=glow('b06_hot', '#ffc7a0', 2.2),
        ring=glow('b06_ring', '#ff5a3a', 2.2),
        spark=glow('b06_spark', '#e8d2ff', 2.2),
        flash=ghost('b06_flash', '#9a6af0', 1.8, 0.6, 1.2),
        smoke=ghost('b06_smoke', '#4a3858', 0.8, 0.8, 1.1),
    )


def pop(ob, t0, s=1.0, end=39, over=1.15, rise=4):
    s = (s, s, s) if isinstance(s, (int, float)) else tuple(s)
    key(ob, IMPACT0, scale=0)
    key(ob, t0, scale=0)
    key(ob, t0 + rise, scale=tuple(a * over for a in s))
    key(ob, t0 + rise + 3, scale=s)
    key(ob, IMPACT0 + end, scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def ballistic(c, p0, v, f, g=-0.028, spin=(25, 18), hold=IMPACT0 + 36, rest=0.05, sc=1.0, rot0=0.0, tmax=34):
    p0 = Vector(p0)
    key(c, IMPACT0, loc=p0, scale=0)
    if f - 1 > IMPACT0:
        key(c, f - 1, loc=p0, scale=0)
    key(c, f, loc=p0, scale=0.2 * sc)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= rest or t >= tmax
        if done:
            p.z = max(rest, min(p.z, rest)) if p.z <= rest else p.z
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
    obs, obs_lt, wood, wood_dk, cord, leather, bone = (M[k] for k in (
        'obs', 'obs_lt', 'wood', 'wood_dk', 'cord', 'leather', 'bone'))
    # ---- tail: chipped obsidian counterweight, red tassel
    crystal('tail_chip', 0.17, 0.62, obs, 5, 0.3, 0.75, both=True, loc=(0, 0, 0.33), ol=0.02)
    lathe('tail_cap', [(0.5, 0), (0.5, 0.17), (0.62, 0.2), (0.8, 0.17), (0.92, 0.155), (0.92, 0)], wood_dk, 12)
    torus('tail_ring', 0.19, 0.04, cord, 12, 5, loc=(0, 0, 0.55))
    cone('tail_tassel', 0.07, 0.3, cord, 6, loc=(0.0, 0.0, 0.5), rot=(180, 0, 0), ol=0.012)
    # ---- shaft: warm hardwood, bare grip zone
    rod('shaft_lo', 0.155, 0.85, 3.3, wood, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 5.9, wood, segs=12, r1=0.14)
    coil('wrap_lo', 0.18, 0.03, 1.35, 1.88, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, cord, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.62, 4, leather, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, cord, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.3, 4.5, 4.7)):
        torus('red_band_%d' % i, 0.148, 0.025 if i != 1 else 0.035, cord if i != 1 else bone, 12, 5, loc=(0, 0, z), ol=0.012)
    # ---- split haft: the wood forks and clamps the glass blade
    lathe('fork_base', [(5.8, 0.14), (5.95, 0.2), (6.15, 0.22), (6.3, 0.18), (6.3, 0)], wood_dk, 12)
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        tube('prong_' + nm, [(s * 0.1, 0, 6.2), (s * 0.2, 0, 6.6), (s * 0.31, 0, 7.05), (s * 0.29, 0, 7.45)], [0.14, 0.13, 0.115, 0.0], wood, 8)
        cone('prong_cap_' + nm, 0.1, 0.22, wood_dk, 6, loc=(s * 0.3, 0, 6.95), rot=(0, 0, 0), ol=0.01)
    coil('lash_lo', 0.2, 0.035, 6.3, 6.75, 4, cord, segs=5)
    coil('lash_hi', 0.3, 0.035, 6.8, 7.15, 3, cord, segs=5, phase=1.0)
    sphere('lash_knot', 0.09, cord, 8, 5, loc=(0.3, 0.1, 6.75), ol=0.012)
    # ---- faceted obsidian blade: black body + violet inner glass + flank shards + edge barbs
    crystal('blade', 0.55, 2.55, obs, 4, 0.4, 0.8, loc=(0, 0, 6.75), rot=(0, 0, 0), scale=(1, 0.32, 1))
    crystal('blade_glass', 0.36, 2.0, obs_lt, 4, 0.42, 0.8, loc=(0, 0.04, 6.95), rot=(0, 0, 0), scale=(1, 0.42, 1), ol=0.012)
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        crystal('flank_' + nm, 0.2, 1.1, obs, 4, 0.4, 0.8, loc=(s * 0.38, 0, 6.85), rot=(0, s * 24, 0), scale=(1, 0.4, 1))
    for i, (x, z, sg) in enumerate(((0.4, 7.7, 1), (-0.38, 8.0, -1), (0.28, 8.5, 1), (-0.22, 8.8, -1))):
        crystal('barb_%d' % i, 0.09, 0.42, obs_lt if i % 2 else obs, 4, 0.4, 0.8, loc=(x, 0, z), rot=(0, sg * 78, 0), scale=(1, 0.5, 1), ol=0.012)
    # ---- charm cord with bone beads and a glass chip
    tube('charm_cord', [(0.18, 0.04, 6.2), (0.3, 0.07, 5.95), (0.34, 0.09, 5.7)], 0.02, cord, 5)
    for i, z in enumerate((6.05, 5.88, 5.72)):
        sphere('bead_%d' % i, 0.055, bone if i != 1 else cord, 8, 5, loc=(0.27 + i * 0.03, 0.07 + i * 0.01, z), ol=0.012)
    crystal('charm_chip', 0.07, 0.3, obs_lt, 4, 0.4, 0.8, loc=(0.34, 0.09, 5.52), rot=(180, 0, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(606)
    ember, hot, ring_m, spark, flash_m, smoke = M['ember'], M['hot'], M['ring'], M['spark'], M['flash'], M['smoke']
    # ---------------- idle: glints + tiny floating glass chips
    fx('idle')
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, spark, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.45, 0.8), -0.2, 7.6 + i * 0.6),
             rot=(90, 0, 0))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 0.95)
        crystal('idle_chip_%d' % i, 0.04, 0.2, M['obs'], 4, 0.4, 0.8, both=True,
                loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.2)), rot=(rnd.uniform(0, 60), rnd.uniform(0, 60), 0), ol=0.01)
    # ---------------- flight: glass shards, red embers, heat rings
    fx('flight')
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.4, M['obs'] if i % 3 else M['obs_lt'], 4, 0.4, 0.8, both=True, ol=0.012) for i in range(12)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(12)]
    stream(shards, lambda t, i: (sj[i][0] * (0.3 + 1.0 * t), sj[i][1] * (0.3 + 1.0 * t), 8.8 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    embers = [sphere('fl_ember_%d' % i, 0.07, ember if i % 2 else hot, 6, 4) for i in range(8)]
    ej = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(embers, lambda t, i: (ej[i][0] * (0.2 + 1.1 * t), ej[i][1] * (0.2 + 1.1 * t), 8.4 - 12.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.5, 0.05, ring_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.4 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    sm = [sphere('fl_smoke_%d' % i, 0.28, smoke, 10, 6) for i in range(4)]
    mj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(4)]
    stream(sm, lambda t, i: (mj[i][0] * (0.2 + 0.7 * t), mj[i][1] * (0.2 + 0.7 * t), 6.5 - 9.0 * t),
           smax=lambda t, i: (0.5 + 1.2 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: glass spikes erupt as a 6-point star, then shatter into flying fragments
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.3))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.0, alpha=0.7)
    key(fl, f + 10, scale=2.8, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    rg = torus('im_ring', 0.5, 0.06, ring_m, 32, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 13, scale=5.0, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    g = -0.03
    shat = f + 15
    for k in range(6):
        a = math.radians(k * 60 + 10)
        ca, sa = math.cos(a), math.sin(a)
        # lit crack along each ray
        cr = tube('im_crack_%d' % k, zigzag((cx + 0.3 * ca, 0.3 * sa, 0.02), (cx + 2.1 * ca, 2.1 * sa, 0.02), 4, 0.1, seed=k),
                  [0.0, 0.06, 0.07, 0.05, 0.0], ring_m, 4, smooth=False, ol=0)
        cr.scale = (1, 1, 0.3)
        key(cr, IMPACT0, scale=0, alpha=1)
        key(cr, f, scale=0, alpha=1)
        key(cr, f + 4, scale=(1, 1, 0.3), alpha=1)
        key(cr, IMPACT0 + 30, scale=(1, 1, 0.3), alpha=1)
        key(cr, IMPACT0 + 44, scale=(1, 1, 0.3), alpha=0)
        tidy(cr, 'impact')
        for j, (rr, h, r_) in enumerate(((0.8, 1.0, 0.16), (1.55, 1.7, 0.22))):
            n_ = k * 2 + j
            p0 = (cx + rr * ca, rr * sa, -0.05)
            sp = crystal('im_spike_%d' % n_, r_, h, M['obs'] if j else M['obs_lt'], 5, 0.35, 0.8, loc=p0,
                         rot=aim((ca * 0.3, sa * 0.3, 1.0)), ol=0.02)
            t0 = f + 1 + j * 2 + k % 2
            key(sp, IMPACT0, scale=0)
            key(sp, t0, scale=0)
            key(sp, t0 + 3, scale=(1.15, 1.15, 1.2))
            key(sp, t0 + 6, scale=1.0)
            key(sp, shat - 1, scale=1.0)
            key(sp, shat + 1, scale=0)
            key(sp, IMPACT0 + 44, scale=0)
            tidy(sp, 'impact')
            # shatter: two fragments per spike fly out when the spike vanishes
            for q in range(2):
                m_ = 2 * n_ + q
                fr = crystal('im_shard_%d' % m_, 0.07, 0.34, M['obs'] if (m_ % 3) else M['obs_lt'], 4, 0.4, 0.8, both=True, ol=0.012)
                b = math.radians(rnd.uniform(-70, 70)) + a
                s_ = rnd.uniform(0.08, 0.17)
                v = Vector((s_ * math.cos(b), s_ * math.sin(b), rnd.uniform(0.08, 0.2)))
                start = (cx + rr * ca, rr * sa, 0.2 + h * 0.35)
                ballistic(fr, start, v, shat, g, spin=(40, 30), rest=0.06, tmax=22, rot0=rnd.uniform(0, 360))
    for i in range(6):
        a = math.radians(i * 60 + 40)
        gl = star('im_glint_%d' % i, 0.16, 0.04, 4, 0.02, spark, loc=(cx + 1.2 * math.cos(a), 1.2 * math.sin(a), 0.8 + 0.2 * (i % 2)), rot=(90, 0, 0))
        key(gl, IMPACT0, scale=0, alpha=1)
        key(gl, shat, scale=0, alpha=1)
        key(gl, shat + 3, scale=1.4, alpha=1)
        key(gl, shat + 14, scale=0.2, alpha=0)
        key(gl, IMPACT0 + 44, scale=0, alpha=0)
        tidy(gl, 'impact')
    return True
