from spearlib import *

NAME = 'SP_31_amethyst_geode'
N = 31
BG = '#9b84bd'        # crystal cave glow
GROUND = '#a190b4'    # amethyst-dust floor
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'dome_crystal': 'im_dome_0', 'shard': 'im_shard_0', 'geode_ring': 'im_ring', 'fl_crystal': 'fl_crys_0'}


def mats():
    return dict(
        ame=toon('amg_ame', '#9a4ee0', '#5a22a0', '#d6a0ff', spec=1.0, rim=0.6, rimcol='#ffd0ff', emit=0.4),
        ame_lt=toon('amg_amelt', '#c996ff', '#7a46c0', '#f2dcff', spec=1.0, emit=0.5),
        ame_dk=toon('amg_amedk', '#5a2a9a', '#2c1058', '#9a66dc', spec=0.9),
        geode=toon('amg_geode', '#7a6a78', '#443a48', '#b8a8b8', spec=0.4),
        silver=toon('amg_silver', '#d8dce8', '#8890a8', '#ffffff', spec=1.0),
        quartz=toon('amg_quartz', '#f2eaff', '#b8a8d8', '#ffffff', spec=1.0, emit=0.3),
        cord=toon('amg_cord', '#b08ad0', '#6a4a8a', '#e0c4f6', spec=0.2),
        core=glow('amg_core', '#c46aff', 3.0),
        hot=glow('amg_hot', '#f0c8ff', 3.6),
    )


def toss(ob, p0, v, f, g=-0.03, floor=0.08, spin=(30, 20, 0), hold=36, s=1.0):
    key(ob, IMPACT0, loc=p0, scale=0)
    if f > IMPACT0 + 1:
        key(ob, f - 1, loc=p0, scale=0)
    key(ob, f, loc=p0, scale=0.3 * s)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= floor or f + t >= IMPACT0 + 40
        if done:
            p.z = floor
        key(ob, f + t, loc=p, scale=s, rot=(t * spin[0], t * spin[1], t * spin[2]), interp='LINEAR')
        if done:
            break
    key(ob, max(f + t + 2, IMPACT0 + hold), scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    ame, ame_lt, ame_dk, geode, silver, quartz, cord, core, hot = (M[k] for k in (
        'ame', 'ame_lt', 'ame_dk', 'geode', 'silver', 'quartz', 'cord', 'core', 'hot'))
    # ---- tail: crystal cluster counterweight
    rock('pommel', 0.27, geode, seed=31, sub=1, rough=0.16, loc=(0, 0, 0.45), scale=(1, 1, 0.9))
    for i in range(3):
        a = math.radians(i * 120 + 20)
        crystal('pommel_crys_%d' % i, 0.09, 0.4, ame_lt, 6, 0.35, 0.7, loc=(0.16 * math.cos(a), 0.16 * math.sin(a), 0.5),
                rot=aim((math.cos(a) * 0.5, math.sin(a) * 0.5, -1)), ol=0.015)
    torus('pommel_ring', 0.2, 0.05, silver, 14, 6, loc=(0, 0, 0.92))
    # ---- shaft: deep violet with silver bands and crystal studs
    rod('shaft_lo', 0.155, 0.8, 3.3, ame_dk, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.1, ame_dk, r1=0.145)
    coil('cord_lo', 0.176, 0.034, 1.3, 1.9, 4, cord, segs=5)
    torus('cord_lo_cap', 0.18, 0.04, silver, 14, 6, loc=(0, 0, 1.92))
    coil('cord_hi', 0.175, 0.034, 3.12, 3.7, 4, cord, segs=5, phase=1.0)
    torus('cord_hi_cap', 0.178, 0.035, silver, 14, 6, loc=(0, 0, 3.1))
    for i in range(5):
        a = i * 2.4
        z = 4.1 + i * 0.4
        crystal('shaft_stud_%d' % i, 0.06, 0.3, ame_lt if i % 2 else quartz, 5, 0.35, 0.7,
                loc=(0.13 * math.cos(a), 0.13 * math.sin(a), z), rot=aim((math.cos(a), math.sin(a), 0.7)), ol=0.012)
    for i, z in enumerate((4.0, 5.9)):
        torus('shaft_band_%d' % i, 0.153, 0.03, silver, 14, 5, loc=(0, 0, z), ol=0.015)
    # ---- geode bowl: rough stone cup lined with quartz studs
    lathe('bowl', [(5.95, 0.15), (6.1, 0.3), (6.4, 0.52), (6.75, 0.6), (6.95, 0.52), (7.0, 0.0)], geode, 16)
    torus('bowl_rim', 0.54, 0.06, silver, 20, 6, loc=(0, 0, 6.95))
    for i in range(8):
        a = math.radians(i * 45 + 10)
        crystal('rim_stud_%d' % i, 0.07, 0.34, quartz, 5, 0.35, 0.7, loc=(0.56 * math.cos(a), 0.56 * math.sin(a), 6.95),
                rot=aim((math.cos(a) * 0.6, math.sin(a) * 0.6, 1)), ol=0.012)
    rock('bowl_chunk_a', 0.16, geode, seed=5, sub=0, rough=0.25, flat=True, loc=(0.35, -0.5, 6.3), ol=0.015)
    rock('bowl_chunk_b', 0.14, geode, seed=6, sub=0, rough=0.25, flat=True, loc=(-0.42, -0.4, 6.35), ol=0.015)
    # ---- the hollow crown: ring of tall amethyst crystals around a glowing core orb
    sphere('core_orb', 0.42, core, 12, 7, loc=(0, 0, 7.9), ol=0)
    sphere('core_hot', 0.22, hot, 10, 6, loc=(0, 0, 7.9), ol=0)
    for i in range(8):
        a = math.radians(i * 45)
        ca, sa = math.cos(a), math.sin(a)
        h = 1.7 + 0.15 * (i % 2)
        crystal('crown_%d' % i, 0.15, h, ame if i % 2 else ame_lt, 6, 0.3, 0.8, loc=(0.34 * ca, 0.34 * sa, 6.95),
                rot=aim((ca * 0.33, sa * 0.33, 1)), ol=0.02)
    for i in range(6):
        a = math.radians(i * 60 + 30)
        ca, sa = math.cos(a), math.sin(a)
        crystal('crown_lo_%d' % i, 0.1, 0.95, ame_dk if i % 2 else ame, 6, 0.3, 0.8, loc=(0.5 * ca, 0.5 * sa, 6.9),
                rot=aim((ca * 0.5, sa * 0.5, 1)), ol=0.018)
    crystal('crown_peak', 0.22, 1.0, ame_lt, 6, 0.4, 0.5, loc=(0, 0, TIP - 1.0), ol=0.02)
    torus('peak_ring', 0.3, 0.035, silver, 16, 5, loc=(0, 0, TIP - 1.12), rot=(0, 0, 0))
    for i in range(3):
        a = math.radians(i * 120 + 60)
        crystal('float_shard_%d' % i, 0.07, 0.4, ame_lt, 5, 0.4, 0.6, both=True,
                loc=(0.95 * math.cos(a), 0.95 * math.sin(a), 7.6 + 0.35 * i), rot=aim((math.cos(a) * 0.3, math.sin(a) * 0.3, 1)), ol=0.015)
    tube('charm_cord', [(0.15, 0.04, 5.9), (0.3, 0.08, 5.6), (0.36, 0.1, 5.3)], 0.02, cord, 5)
    crystal('charm_crystal', 0.07, 0.34, ame, 5, 0.4, 0.6, both=True, loc=(0.36, 0.1, 5.2), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(3131)
    aura = ghost('amg_aura', '#c46aff', 1.2, 0.05, 1.8)
    puff = ghost('amg_puff', '#e0b8ff', 1.2, 0.7, 1.2)
    glint = glow('amg_glint', '#f6e0ff', 3.0)
    ringm = glow('amg_ring', '#c46aff', 2.6)
    mote = glow('amg_mote', '#e8b0ff', 2.8)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 7.9), scale=(1.4, 1.4, 1.6))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.1)
        sphere('idle_mote_%d' % i, rnd.uniform(0.04, 0.07), mote, 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.2)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 0.9), -0.4, 7.4 + i * 0.6), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    cr = [crystal('fl_crys_%d' % i, 0.08, 0.4, M['ame_lt'] if i % 2 else M['ame'], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(10)]
    cj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(cr, lambda t, i: (cj[i][0] * (0.3 + 1.0 * t), cj[i][1] * (0.3 + 1.0 * t), 8.8 - 12.5 * t),
           smax=1.1, spin=lambda t, i: (cj[i][2] + 540 * t, 360 * t, 0))
    st = [star('fl_star_%d' % i, 0.16, 0.04, 4, 0.03, glint) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(st, lambda t, i: (sj[i][0] * (0.3 + 1.2 * t), sj[i][1] * (0.3 + 1.2 * t), 8.4 - 12.0 * t), smax=1.3,
           spin=lambda t, i: (90, sj[i][2] + 300 * t, 0))
    pf = [sphere('fl_puff_%d' % i, 0.3, puff, 12, 7) for i in range(6)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.8 * t), pj[i][1] * (0.2 + 0.8 * t), 7.6 - 11.0 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.055, ringm, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: a geode dome of inward-pointing crystals grows around the spear, then cracks open
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    C = Vector((cx, 0, 0.3))
    flash = sphere('im_flash', 0.5, ghost('amg_flash', '#f0d0ff', 2.0, 0.6, 1.3), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.7)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    sd = Vector((-math.cos(math.radians(35)), 0, math.sin(math.radians(35))))     # the stuck shaft direction
    R = 1.8
    n = 0
    for e_deg, cnt, ph in ((14, 10, 0.0), (40, 7, 0.3), (68, 3, 0.1)):
        for j in range(cnt):
            az = 2 * math.pi * j / cnt + ph
            e = math.radians(e_deg)
            rad = Vector((math.cos(e) * math.cos(az), math.cos(e) * math.sin(az), math.sin(e)))
            p = C + rad * R
            rel = p - C
            dist = rel.cross(sd).length
            if dist < 0.55:
                continue
            h = 0.95 + 0.25 * ((j + n) % 3)
            c = crystal('im_dome_%d' % n, 0.17, h, M['ame'] if (j + n) % 2 else M['ame_lt'], 6, 0.3, 0.8, loc=tuple(p), rot=aim(-rad), ol=0.018)
            t0 = f + int(e_deg / 14) + (j % 3)
            out1 = p + rad * 0.9
            out2 = p + rad * 1.7
            key(c, IMPACT0, loc=tuple(p), scale=0)
            key(c, t0, loc=tuple(p), scale=0)
            key(c, t0 + 5, loc=tuple(p), scale=1.15)
            key(c, t0 + 8, loc=tuple(p), scale=1.0)
            key(c, f + 20, loc=tuple(p), scale=1.0)
            key(c, f + 25, loc=tuple(out1), scale=1.0)
            key(c, f + 33, loc=tuple(out2), scale=0.0)
            tidy(c, 'impact')
            ease_keys(c)
            n += 1
    orb = sphere('im_orb', 0.9, ghost('amg_orb', '#d89aff', 1.6, 0.35, 1.5), 14, 8, loc=tuple(C))
    key(orb, IMPACT0, scale=0, alpha=1)
    key(orb, f + 4, scale=0.4, alpha=0.8)
    key(orb, f + 14, scale=1.0, alpha=1)
    key(orb, f + 22, scale=1.2, alpha=1)
    key(orb, f + 30, scale=2.4, alpha=0)
    tidy(orb, 'impact')
    ease_keys(orb)
    for k in range(2):
        rg = torus('im_ring' if k == 0 else 'im_ring_%d' % k, 0.6, 0.06, ringm, 36, 5, loc=(cx, 0, 0.05))
        t0 = f + 20 + k * 5
        key(rg, IMPACT0, scale=0, alpha=1)
        key(rg, t0 - 1, scale=0, alpha=1)
        key(rg, t0, scale=0.3, alpha=1)
        key(rg, t0 + 14, scale=5.0 - k, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
        ease_keys(rg)
    gd = sphere('im_glowdisc', 1.2, ghost('amg_disc', '#c46aff', 1.4, 0.4, 1.0), 16, 4, loc=(cx, 0, 0.03))
    key(gd, IMPACT0, scale=0, alpha=1)
    key(gd, f + 6, scale=(1.4, 1.4, 0.02), alpha=1)
    key(gd, IMPACT0 + 36, scale=(1.6, 1.6, 0.02), alpha=0.8)
    key(gd, IMPACT0 + 44, scale=(1.6, 1.6, 0.02), alpha=0)
    tidy(gd, 'impact')
    for i in range(12):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.06, 0.16)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.12, 0.2)))
        sh = crystal('im_shard_%d' % i, 0.08, rnd.uniform(0.28, 0.45), M['ame_lt'] if i % 2 else M['ame'], 5, 0.4, 0.6, both=True, ol=0.012)
        toss(sh, Vector((cx, 0, 0.6)), v, f + 20 + rnd.randint(0, 3), g=-0.045, floor=0.12, spin=(40, 25, 10), hold=38)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.8)
        sp2 = star('im_spark_%d' % i, 0.18, 0.04, 4, 0.03, glint, loc=(cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.4, 1.6)), rot=(90, 0, 0))
        t0 = f + 18 + rnd.randint(0, 12)
        key(sp2, IMPACT0, scale=0)
        key(sp2, t0, scale=0)
        key(sp2, t0 + 4, scale=1.2)
        key(sp2, t0 + 12, scale=0)
        tidy(sp2, 'impact')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.8, 2.0)
        sm = sphere('im_dust_%d' % i, 0.35, puff, 12, 7)
        t0 = f + 18 + rnd.randint(0, 6)
        p0 = (cx + 0.5 * math.cos(a), 0.5 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.0, 2.0))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.2), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    return True
