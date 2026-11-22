from spearlib import *

NAME = 'SP_09_ice'
N = 9
BG = '#4f74a0'        # frozen
GROUND = '#9fbcd6'
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'ice_spike': 'im_spike_0', 'frost_disc': 'im_frostdisc', 'frost_ring': 'im_frostring',
             'ice_shard': 'im_shard_0', 'drift_shard': 'fl_shard_0'}


def mats():
    return dict(
        ice=toon('b09_ice', '#bfe9ff', '#5a9ad8', '#f0fbff', spec=1.0, rim=0.7, rimcol='#ffffff', emit=0.4),
        ice_dp=toon('b09_ice_dp', '#6ab4f0', '#2a62b8', '#b8e0ff', spec=1.0, rim=0.6, rimcol='#e8f8ff', emit=0.3),
        ice_core=toon('b09_ice_core', '#e8fbff', '#9ad4f4', '#ffffff', spec=1.0, emit=0.8),
        frost=toon('b09_frost', '#eef8ff', '#a8c4e0', '#ffffff', spec=0.6),
        fur=toon('b09_fur', '#f2f6fb', '#aab8cc', '#ffffff', spec=0.1),
        shaft=toon('b09_shaft', '#7a98c0', '#44608e', '#b0cbee'),
        navy=toon('b09_navy', '#3a5890', '#1e3262', '#6a8ed0'),
        silver=toon('b09_silver', '#c8d2e0', '#7a88a0', '#ffffff', spec=1.0),
        cyan=glow('b09_cyan', '#8af0ff', 2.2),
        white=glow('b09_white', '#f4fcff', 2.2),
        ring=glow('b09_ring', '#9ae8ff', 2.0),
        flash=ghost('b09_flash', '#d0f6ff', 1.8, 0.6, 1.2),
        puff=ghost('b09_puff', '#f4fbff', 1.0, 0.85, 1.1),
        disc=ghost('b09_disc', '#bfeeff', 1.3, 0.55, 1.0, edge=True),
    )


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    ice, ice_dp, ice_core, frost, fur, shaft, navy, silver, cyan = (M[k] for k in (
        'ice', 'ice_dp', 'ice_core', 'frost', 'fur', 'shaft', 'navy', 'silver', 'cyan'))
    # ---- tail: frosted cap with an ice drop
    lathe('tail_cap', [(0.4, 0), (0.4, 0.14), (0.52, 0.2), (0.72, 0.19), (0.86, 0.155), (0.86, 0)], frost, 12)
    crystal('tail_drop', 0.15, 0.55, ice, 6, 0.4, 0.8, loc=(0, 0, 0.55), rot=(180, 0, 0), ol=0.02)
    torus('tail_ring', 0.2, 0.04, silver, 12, 5, loc=(0, 0, 0.95))
    # ---- shaft: frost-blue lacquer, bare grip zone
    rod('shaft_lo', 0.155, 0.9, 3.3, shaft, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.0, navy, segs=12, r1=0.14)
    # white fur wraps (chunky coils + tufts), outside the grip zone
    coil('fur_lo', 0.19, 0.055, 1.35, 1.82, 4, fur, segs=5)
    torus('fur_lo_cap', 0.19, 0.045, silver, 12, 5, loc=(0, 0, 1.93))
    for i in range(6):
        a = math.radians(i * 60 + 15)
        ca, sa = math.cos(a), math.sin(a)
        cone('fur_tuft_%d' % i, 0.07, 0.3, fur, 5, loc=(0.2 * ca, 0.2 * sa, 1.65 - 0.1 * (i % 2)), rot=aim((ca, sa, -0.7)), ol=0.012)
    coil('fur_hi', 0.185, 0.055, 3.12, 3.62, 4, fur, segs=5, phase=1.0)
    torus('fur_hi_cap', 0.19, 0.045, silver, 12, 5, loc=(0, 0, 3.07))
    for i in range(3):
        a = math.radians(i * 120 + 50)
        ca, sa = math.cos(a), math.sin(a)
        cone('fur_tuft_hi_%d' % i, 0.07, 0.28, fur, 5, loc=(0.2 * ca, 0.2 * sa, 3.6), rot=aim((ca, sa, -0.7)), ol=0.012)
    for i, z in enumerate((4.3, 4.5, 4.7)):
        torus('band_%d' % i, 0.148, 0.025 if i != 1 else 0.035, (silver, cyan, silver)[i], 12, 5, loc=(0, 0, z), ol=0.012)
    # ---- frosted collar with hanging icicles
    lathe('collar', [(5.9, 0.14), (6.1, 0.22), (6.35, 0.3), (6.6, 0.36), (6.75, 0.3), (6.75, 0)], frost, 14)
    torus('collar_ring', 0.36, 0.055, silver, 14, 5, loc=(0, 0, 6.35))
    for i in range(4):
        a = math.radians(i * 90 + 45)
        cone('frost_spur_%d' % i, 0.07, 0.4, ice, 5, loc=(0.34 * math.cos(a), 0.34 * math.sin(a), 6.7), rot=aim((math.cos(a), math.sin(a), 1.0)), ol=0.012)
    for i in range(6):
        a = math.radians(i * 60)
        ln = 0.9 - 0.18 * (i % 3)
        cone('icicle_%d' % i, 0.075, ln, ice if i % 2 else ice_dp, 5, loc=(0.34 * math.cos(a), 0.34 * math.sin(a), 6.4), rot=(180, 0, 0), ol=0.012)
    # ---- the long ice crystal blade
    crystal('blade', 0.5, 2.9, ice, 6, 0.36, 0.85, loc=(0, 0, 6.5), scale=(1, 0.62, 1))
    crystal('blade_core', 0.28, 2.3, ice_core, 6, 0.36, 0.85, loc=(0, 0, 6.8), scale=(1, 0.7, 1), ol=0.0)
    for i, (x, z, h, sg) in enumerate(((0.4, 7.2, 1.1, 1), (-0.4, 7.2, 1.1, -1), (0.3, 8.0, 0.75, 1), (-0.3, 8.0, 0.75, -1))):
        crystal('fringe_%d' % i, 0.12, h, ice_dp if i < 2 else ice, 5, 0.38, 0.8, loc=(x, 0, z), rot=(0, sg * 28, 0), ol=0.015)
    for i in range(3):
        a = math.radians(i * 120 + 90)
        crystal('base_crystal_%d' % i, 0.14, 0.95 - 0.1 * i, ice_dp, 5, 0.38, 0.8, loc=(0.38 * math.cos(a), 0.38 * math.sin(a), 6.55),
                rot=aim((math.cos(a) * 0.6, math.sin(a) * 0.6, 1.0)), ol=0.015)
    # ---- charm: blue cord with a frozen drop and a fur puff
    tube('charm_cord', [(0.2, 0.04, 5.9), (0.34, 0.08, 5.65), (0.38, 0.1, 5.45)], 0.02, navy, 5)
    sphere('charm_puff', 0.1, fur, 8, 5, loc=(0.38, 0.1, 5.4), ol=0.012)
    crystal('charm_drop', 0.07, 0.34, ice, 5, 0.35, 0.8, loc=(0.38, 0.1, 5.28), rot=(180, 0, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


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


def build_fx(M):
    rnd = random.Random(909)
    white, cyan, ring_m, flash_m, puff, disc = M['white'], M['cyan'], M['ring'], M['flash'], M['puff'], M['disc']
    # ---------------- idle: glints and drifting snow motes
    fx('idle')
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.03, 4, 0.02, white, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.45, 0.8), -0.2, 7.5 + i * 0.7),
             rot=(90, 0, 0))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.55, 0.9)
        sphere('idle_snow_%d' % i, rnd.uniform(0.04, 0.07), puff, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.2)))
    # ---------------- flight: ice shards, snow puffs, frost rings, snowflakes
    fx('flight')
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.4, M['ice'] if i % 2 else M['ice_dp'], 5, 0.4, 0.8, both=True, ol=0.012) for i in range(10)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(shards, lambda t, i: (sj[i][0] * (0.3 + 1.0 * t), sj[i][1] * (0.3 + 1.0 * t), 8.9 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    pf = [sphere('fl_puff_%d' % i, 0.3, puff, 10, 6) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 7.4 - 11.0 * t),
           smax=lambda t, i: (0.5 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.5, 0.045, ring_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.5 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    fk = [star('fl_flake_%d' % i, 0.2, 0.07, 6, 0.02, white, rot=(90, 0, 0)) for i in range(5)]
    kj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(5)]
    stream(fk, lambda t, i: (kj[i][0] * (0.3 + 1.0 * t), kj[i][1] * (0.3 + 1.0 * t), 8.2 - 12.0 * t),
           smax=lambda t, i: 1.2 * math.sin(math.pi * t) ** 0.5, spin=lambda t, i: (90, 0, 360 * t))
    # ---------------- impact: ice spikes erupt in a radial burst, frost disc spreads
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.3))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.0, alpha=0.7)
    key(fl, f + 10, scale=2.8, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    fd = cyl('im_frostdisc', 2.7, 0.04, M['frost'], 36, 0.01, loc=(cx, 0, 0.02), ol=0.0)
    key(fd, IMPACT0, scale=0)
    key(fd, f, scale=0.1)
    key(fd, f + 12, scale=1.0)
    key(fd, IMPACT0 + 38, scale=1.0)
    key(fd, IMPACT0 + 44, scale=0)
    tidy(fd, 'impact')
    ease_keys(fd)
    fg = cyl('im_frostglow', 2.5, 0.03, disc, 36, 0.01, loc=(cx, 0, 0.05), ol=0.0)
    key(fg, IMPACT0, scale=0, alpha=1)
    key(fg, f, scale=0.1, alpha=0.9)
    key(fg, f + 12, scale=1.1, alpha=0.5)
    key(fg, IMPACT0 + 34, scale=1.1, alpha=0.3)
    key(fg, IMPACT0 + 44, scale=1.1, alpha=0)
    tidy(fg, 'impact', interp='LINEAR')
    fr = torus('im_frostring', 0.5, 0.06, ring_m, 36, 5, loc=(cx, 0, 0.06))
    key(fr, IMPACT0, scale=0, alpha=1)
    key(fr, f, scale=0.3, alpha=1)
    key(fr, f + 12, scale=5.0, alpha=0)
    tidy(fr, 'impact', interp='LINEAR')
    ease_keys(fr)
    # three radial rings of spikes, erupting from the inside out
    cfg = ((6, 0.9, 1.35, 0.2, 15), (10, 1.65, 1.0, 0.16, 5), (12, 2.35, 0.7, 0.12, 0))
    n_ = 0
    for ri, (cnt, rr, h, r_, off) in enumerate(cfg):
        for k in range(cnt):
            a = math.radians(k * 360 / cnt + off)
            ca, sa = math.cos(a), math.sin(a)
            h_ = h * rnd.uniform(0.85, 1.2)
            sp = crystal('im_spike_%d' % n_, r_, h_, M['ice'] if (k + ri) % 2 else M['ice_dp'], 6, 0.35, 0.8,
                         loc=(cx + rr * ca, rr * sa, -0.05), rot=aim((ca * 0.35, sa * 0.35, 1.0), rnd.uniform(0, 60)), ol=0.02)
            t0 = f + 1 + ri * 2 + k % 3
            key(sp, IMPACT0, scale=0)
            key(sp, t0, scale=0)
            key(sp, t0 + 3, scale=(1.15, 1.15, 1.3))
            key(sp, t0 + 6, scale=1.0)
            key(sp, IMPACT0 + 38, scale=1.0)
            key(sp, IMPACT0 + 44, scale=0)
            tidy(sp, 'impact')
            n_ += 1
    for i in range(10):
        a = math.radians(rnd.uniform(0, 360))
        s_ = rnd.uniform(0.08, 0.16)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.22, 0.36)))
        c = crystal('im_shard_%d' % i, 0.06, 0.3, M['ice'] if i % 2 else M['ice_dp'], 5, 0.4, 0.8, both=True, ol=0.012)
        ballistic(c, (cx, 0, 0.2), v, f, rot0=rnd.uniform(0, 360), spin=(40, 30), rest=0.08)
    for i in range(8):
        a = math.radians(i * 45 + rnd.uniform(-10, 10))
        rr = rnd.uniform(1.0, 2.0)
        p = sphere('im_snow_%d' % i, 0.3, puff, 10, 6)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.6, 1.2))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=1.3, alpha=0.8)
        key(p, IMPACT0 + 44, loc=(end[0], end[1], end[2] + 0.6), scale=1.9, alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
