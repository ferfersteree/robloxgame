from spearlib import *

NAME = 'SP_40_singularity_spire'
N = 40
BG = '#3a2c58'        # deep space
GROUND = '#271c3a'
TIP = 9.35
TRAIL = 5.2
FX_EXPORT = {'pillar': 'im_pillar_0', 'horizon_ring': 'im_flash_ring_0', 'dark_disc': 'im_disc', 'particle': 'im_pull_0'}


def mats():
    return dict(
        blk=toon('ss_blk', '#18121f', '#08050d', '#4c3e66', spec=1.0, rim=0.8, rimcol='#ffa040'),
        blk2=toon('ss_blk2', '#2c2238', '#120c1c', '#6a5a88', spec=0.9, rim=0.7, rimcol='#c080ff'),
        silver=toon('ss_silver', '#d8d6e6', '#767296', '#ffffff', spec=1.0),
        plum=toon('ss_plum', '#5a2a90', '#2c1252', '#9a60d8', emit=0.2),
        ember=glow('ss_ember', '#ff9a2a', 2.4),
        white=glow('ss_white', '#fff2d0', 2.6),
        vio=glow('ss_vio', '#a45aff', 2.2),
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
    blk, blk2, silver, plum, ember, white, vio = (M[k] for k in ('blk', 'blk2', 'silver', 'plum', 'ember', 'white', 'vio'))
    # ---- tail: stepped black counter-spire with an ember core
    for i, (r, z) in enumerate(((0.3, 0.9), (0.22, 0.6), (0.14, 0.34))):
        cyl('tail_step_%d' % i, r, 0.3, blk if i != 1 else blk2, 6, 0.03, loc=(0, 0, z))
    cone('tail_point', 0.1, 0.22, blk, 6, loc=(0, 0, 0.22), rot=(180, 0, 0), ol=0.015)
    sphere('tail_core', 0.1, ember, 8, 5, loc=(0, 0, 0.62), scale=(1.5, 1.5, 0.5), ol=0)
    # ---- shaft: black glass with silver rings and violet seams
    shaft_parts(blk, plum, silver, vio, z0=1.0)
    for i in range(3):
        a = i * 2.1
        sphere('shaft_star_%d' % i, 0.055, white, 6, 4, loc=(0.15 * math.cos(a), 0.15 * math.sin(a), 5.2 + 0.35 * i), ol=0)
    # ---- socket
    lathe('socket', [(6.3, 0.14), (6.45, 0.22), (6.7, 0.34), (6.95, 0.3), (7.0, 0)], blk2, 12)
    torus('socket_rim', 0.33, 0.055, silver, 14, 5, loc=(0, 0, 6.55))
    torus('socket_glow', 0.3, 0.04, ember, 14, 4, loc=(0, 0, 6.85), ol=0)
    # ---- the spire: five hexagonal steps shrinking to a needle
    zs = 6.95
    for i, (r, h) in enumerate(((0.66, 0.42), (0.53, 0.4), (0.41, 0.38), (0.3, 0.36), (0.2, 0.3))):
        cyl('spire_step_%d' % i, r, h, blk if i % 2 == 0 else blk2, 6, 0.035, loc=(0, 0, zs + h / 2))
        torus('spire_edge_%d' % i, r + 0.02, 0.03, ember if i % 2 == 0 else vio, 12, 4, loc=(0, 0, zs + h), ol=0)
        zs += h
    cone('spire_needle', 0.14, TIP - zs, blk, 6, loc=(0, 0, zs))
    sphere('spire_eye', 0.12, white, 8, 5, loc=(0, -0.5, 7.15), ol=0)
    # ---- event-horizon frame: solid ring with a glowing inner edge, plus a flat accretion ring, all floating
    torus('horizon_frame', 1.15, 0.09, blk2, 28, 6, loc=(0, 0, 7.55), rot=(14, 0, 0))
    torus('horizon_glow', 1.07, 0.05, ember, 28, 4, loc=(0, 0, 7.55), rot=(14, 0, 0), ol=0)
    torus('accretion', 0.9, 0.06, vio, 24, 5, loc=(0, 0, 7.55), rot=(14, 0, 0), scale=(1, 1, 0.5), ol=0)
    torus('accretion_b', 1.3, 0.04, vio, 24, 4, loc=(0, 0, 7.55), rot=(14, 0, 0), scale=(1, 1, 0.4), ol=0)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        sphere('horizon_star_%d' % i, 0.09, white, 8, 5, loc=(1.3 * math.cos(a), 1.3 * math.sin(a), 7.55 + 0.3 * math.sin(a)), ol=0)
    for i in range(4):
        a = math.radians(i * 90 + 15)
        crystal('float_shard_%d' % i, 0.07, 0.42, blk if i % 2 else plum, 5, 0.35, 0.6, both=True,
                loc=(0.8 * math.cos(a), 0.8 * math.sin(a), 6.95 + 0.6 * i), rot=aim((math.cos(a) * 0.4, math.sin(a) * 0.4, 1), i * 40), ol=0.015)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


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
    rnd = random.Random(4040)
    smoke = ghost('ss_smoke', '#3a1a5a', 1.0, 0.85, 1.0)
    aura = ghost('ss_aura', '#8a50e0', 1.2, 0.05, 1.8)
    voidm = ghost('ss_void', '#06030a', 0.6, 0.9, 0.7)
    white = M['white']
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.0), scale=(1.5, 1.0, 1.6))
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.5)
        sphere('idle_mote_%d' % i, rnd.uniform(0.04, 0.08), white if i % 2 else M['ember'], 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.5)))
    for i in range(2):
        star('idle_glint_%d' % i, 0.15, 0.035, 4, 0.02, white, loc=(rnd.choice((-1, 1)) * 0.8, -0.3, 7.6 + i * 1.0), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    pts = [sphere('fl_mote_%d' % i, 0.07, white if i % 2 else M['ember'], 6, 4) for i in range(12)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(pts, lambda t, i: (pj[i][0] * (1.6 - 1.3 * t), pj[i][1] * (1.6 - 1.3 * t), 9.0 - 12.0 * t), smax=1.4)
    blocks = [cyl('fl_block_%d' % i, 0.14, 0.2, M['blk2'], 6, 0.02, ol=0.014) for i in range(6)]
    bj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(blocks, lambda t, i: (bj[i][0] * (0.4 + 0.9 * t), bj[i][1] * (0.4 + 0.9 * t), 8.6 - 12.0 * t), smax=1.1,
           spin=lambda t, i: (bj[i][2] + 500 * t, 300 * t, 0))
    puffs = [sphere('fl_smoke_%d' % i, 0.32, smoke, 10, 6) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (sj[i][0] * (0.2 + 0.8 * t), sj[i][1] * (0.2 + 0.8 * t), 8.0 - 11.0 * t),
           smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 1.0, 0.05, M['ember'] if i % 2 else M['vio'], 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.4 - 6.8 * t), smax=lambda t, i: (1.2 - 1.0 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: implosion, then a flash ring, then stepped black pillars rise
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6, wobble=3)
    f = IMPACT0 + 4
    cx = 0.45
    c0 = (cx, 0, 0.9)
    disc = sphere('im_disc', 1.0, voidm, 16, 8, loc=(cx, 0, 0.9))
    key(disc, IMPACT0, scale=0, alpha=1)
    key(disc, f + 2, scale=0.3, alpha=1)
    key(disc, f + 8, scale=1.2, alpha=1)
    key(disc, f + 15, scale=0.8, alpha=1)
    key(disc, f + 17, scale=0.1, alpha=0)
    tidy(disc, 'impact', interp='LINEAR')
    for i in range(26):
        a = math.radians(i * 360 / 26 + rnd.uniform(-5, 5))
        r = rnd.uniform(2.4, 3.8)
        p0 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.4, 2.6))
        pm = (cx + 0.55 * r * math.cos(a + 0.4), 0.55 * r * math.sin(a + 0.4), 0.9 + (p0[2] - 0.9) * 0.55)
        pp = sphere('im_pull_%d' % i, 0.09, white if i % 2 else M['ember'], 6, 4, ol=0)
        key(pp, IMPACT0, loc=p0, scale=0, alpha=1)
        key(pp, f + 1, loc=p0, scale=1.0, alpha=1)
        key(pp, f + 10, loc=pm, scale=1.2, alpha=1)
        key(pp, f + 16, loc=c0, scale=0.3, alpha=1)
        key(pp, f + 17, loc=c0, scale=0, alpha=0)
        tidy(pp, 'impact', interp='LINEAR')
    fl = sphere('im_flash', 0.6, ghost('ss_flash', '#ffe8c0', 2.4, 0.8, 1.2), 14, 8, loc=c0)
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f + 15, scale=0.2, alpha=1)
    key(fl, f + 19, scale=2.8, alpha=0.8)
    key(fl, f + 26, scale=3.6, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    for k in range(2):
        rg = torus('im_flash_ring_%d' % k, 0.6, 0.08 - 0.03 * k, M['ember'] if k == 0 else M['white'], 40, 5, loc=(cx, 0, 0.08))
        key(rg, IMPACT0, scale=0, alpha=1)
        key(rg, f + 16 + k * 2, scale=0.3, alpha=1)
        key(rg, f + 36 + k * 2, scale=6.0 - k, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
        ease_keys(rg)
    prof = [(0, 0), (0, 0.42), (0.55, 0.42), (0.55, 0.34), (1.1, 0.34), (1.1, 0.26), (1.65, 0.26), (1.65, 0.18), (2.1, 0.18), (2.1, 0.0)]
    for i in range(7):
        a = math.radians(i * 360 / 7 + 12)
        r = 1.75 + 0.35 * (i % 2)
        p = lathe('im_pillar_%d' % i, prof, M['blk'] if i % 2 else M['blk2'], 6, loc=(cx + r * math.cos(a), r * math.sin(a), 0), ol=0.02)
        e = torus('im_pillar_glow_%d' % i, 0.45, 0.03, M['ember'], 12, 4, loc=(cx + r * math.cos(a), r * math.sin(a), 0.56), ol=0)
        t0 = f + 16 + i
        for o in (p, e):
            key(o, IMPACT0, scale=0)
            key(o, t0, scale=0)
            key(o, t0 + 6, scale=(1.0, 1.0, 1.15))
            key(o, t0 + 10, scale=1.0)
            key(o, IMPACT0 + 38, scale=1.0)
            key(o, IMPACT0 + 44, scale=0)
            tidy(o, 'impact')
    return True
