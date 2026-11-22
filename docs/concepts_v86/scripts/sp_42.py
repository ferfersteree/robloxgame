from spearlib import *

NAME = 'SP_42_spore_halberd'
N = 42
BG = '#2f4c5c'        # spore cave
GROUND = '#3a4b49'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'mushroom': 'im_mush_0', 'spore_cloud': 'im_cloud_0', 'spore': 'im_spore_0', 'ground_ring': 'im_ring'}


def mats():
    return dict(
        bone=toon('sph_bone', '#f2ecd8', '#b8ae94', '#ffffff', spec=0.7, rim=0.5, rimcol='#a8ffd0'),
        wood=toon('sph_wood', '#6a4a3a', '#3a241c', '#a07a62'),
        moss=toon('sph_moss', '#4ea860', '#256a3a', '#92e090'),
        cap=toon('sph_cap', '#e86ab8', '#a02a78', '#ffb0e0', spec=0.8, emit=0.5, rimcol='#ffd0f0'),
        cap2=toon('sph_cap2', '#4ad8c0', '#1a8a86', '#a8fff0', spec=0.8, emit=0.5),
        gold=toon('sph_gold', '#e8c458', '#a0701e', '#fff0a0', spec=1.0),
        green=glow('sph_green', '#9affb0', 3.2),
        teal=glow('sph_teal', '#5cf0e0', 3.0),
        pink=glow('sph_pink', '#ff9ae0', 3.2),
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


MUSH = [(0, 0), (0, 0.1), (0.35, 0.08), (0.55, 0.1), (0.55, 0.42), (0.7, 0.62), (0.9, 0.6), (1.05, 0.4), (1.12, 0.0)]


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    bone, wood, moss, cap, cap2, gold, green, teal, pink = (M[k] for k in ('bone', 'wood', 'moss', 'cap', 'cap2', 'gold', 'green', 'teal', 'pink'))
    # ---- tail: upside-down mushroom pommel
    lathe('tail_mush', [(0.0, 0.0), (0.0, 0.1), (0.14, 0.2), (0.34, 0.3), (0.52, 0.2), (0.6, 0.1), (0.62, 0.0)], cap2, 12)
    sphere('tail_spot', 0.07, green, 6, 4, loc=(0.2, 0.18, 0.12), ol=0)
    sphere('tail_spot_b', 0.06, green, 6, 4, loc=(-0.18, 0.12, 0.14), ol=0)
    torus('tail_ring', 0.19, 0.045, gold, 12, 5, loc=(0, 0, 0.66))
    # ---- shaft: dark root wood, moss wraps, gold rings
    shaft_parts(wood, moss, gold, teal)
    for i, (z, a) in enumerate(((4.1, 0.5), (5.0, 3.4), (5.7, 5.2))):
        lathe('shelf_%d' % i, [(0.0, 0.0), (0.0, 0.2), (0.1, 0.19), (0.14, 0.0)], cap if i % 2 else cap2, 8,
              loc=(0.14 * math.cos(a), 0.14 * math.sin(a), z), rot=aim((math.cos(a), math.sin(a), 0.5)), ol=0.012)
    # ---- socket: bone cup with moss
    lathe('socket', [(6.3, 0.14), (6.45, 0.22), (6.7, 0.3), (6.95, 0.26), (7.05, 0.1), (7.1, 0)], bone, 12)
    torus('socket_ring', 0.3, 0.055, gold, 14, 5, loc=(0, 0, 6.55))
    for i in range(4):
        a = math.radians(i * 90 + 30)
        sphere('socket_moss_%d' % i, 0.13, moss, 7, 4, loc=(0.3 * math.cos(a), 0.3 * math.sin(a), 6.7 + 0.12 * (i % 2)), ol=0.012)
    # ---- halberd: pale broad blade, axe-wing on one side, spike hook on the other
    ol_ = [(0, 6.95), (0.4, 7.25), (0.62, 8.0), (0.5, 8.7), (0.15, 9.15), (0, TIP), (-0.15, 9.1), (-0.4, 8.6), (-0.46, 7.9), (-0.32, 7.3)]
    blade('blade', ol_, 0.13, bone)
    blade('blade_core', [(x * 0.45, 7.35 + (z - 6.95) * 0.75) for (x, z) in ol_], 0.16, cap2, ol=0.012)
    wing = [(0.3, 7.5), (0.95, 7.7), (1.35, 8.2), (1.05, 8.55), (0.5, 8.35)]
    blade('axe_wing', wing, 0.1, bone)
    blade('axe_wing_glow', [(0.3 + (x - 0.3) * 0.6, 7.55 + (z - 7.5) * 0.7) for (x, z) in wing], 0.12, green, ol=0)
    tube('hook', [(-0.3, 0, 7.7), (-0.75, 0, 7.8), (-1.1, 0, 8.2), (-1.1, 0, 8.7)], [0.09, 0.08, 0.06, 0.0], bone, 7)
    sphere('hook_pod', 0.1, green, 8, 5, loc=(-1.05, 0, 8.4), ol=0)
    # ---- the mushroom cap behind the blade, glowing, with gills and spots
    # (lead fix) the cap is a real umbrella dome around the blade base, so the blade rises out of the mushroom
    lathe('cap', [(7.0, 0.0), (7.0, 1.0), (7.08, 1.04), (7.26, 0.9), (7.44, 0.62), (7.58, 0.3), (7.63, 0.0)], cap, 18)
    torus('cap_gills', 0.92, 0.05, pink, 24, 4, loc=(0, 0, 6.98), ol=0)
    cyl('cap_stem', 0.24, 0.35, bone, 10, 0.03, loc=(0, 0, 6.85))
    for i in range(6):
        a = math.radians(i * 60 + 20)
        rr = 0.5 + 0.25 * (i % 2)
        zz = 7.0 + 0.6 * max(0.0, 1 - (rr / 1.0) ** 2) ** 0.5
        sphere('cap_spot_%d' % i, 0.11 - 0.015 * (i % 2), green if i % 2 else teal, 8, 5,
               loc=(rr * math.cos(a), rr * math.sin(a), zz), ol=0)
    # ---- floating spores
    for i in range(7):
        a = math.radians(i * 51 + 15)
        sphere('float_spore_%d' % i, 0.08 + 0.02 * (i % 3), green if i % 2 else pink, 8, 5,
               loc=(1.25 * math.cos(a), 0.4 * math.sin(a) - 0.3, 6.9 + 0.38 * i), ol=0)
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
    rnd = random.Random(4242)
    cloud = ghost('sph_cloud', '#8affb8', 1.3, 0.8, 1.0)
    cloud2 = ghost('sph_cloud2', '#7af0e8', 1.2, 0.8, 1.0)
    cloud3 = ghost('sph_cloud3', '#ff9ee0', 1.2, 0.75, 1.0)
    aura = ghost('sph_aura', '#9affc0', 1.2, 0.05, 1.8)
    green, teal, pink = M['green'], M['teal'], M['pink']
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, -0.2, 8.1), scale=(1.5, 1.0, 1.5))
    for i in range(9):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.3)
        sphere('idle_spore_%d' % i, rnd.uniform(0.04, 0.08), (green, teal, pink)[i % 3], 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.6)))
    for i in range(2):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, green, loc=(rnd.choice((-1, 1)) * 0.8, -0.7, 7.6 + i * 0.9), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    puffs = [sphere('fl_cloud_%d' % i, 0.3, (cloud, cloud2, cloud3)[i % 3], 10, 6) for i in range(9)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(9)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 8.0 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    ms = [lathe('fl_mush_%d' % i, MUSH, M['cap'] if i % 2 else M['cap2'], 8, ol=0.012) for i in range(6)]
    mj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(ms, lambda t, i: (mj[i][0] * (0.4 + 1.0 * t), mj[i][1] * (0.4 + 1.0 * t), 8.6 - 12.0 * t), smax=0.32,
           spin=lambda t, i: (mj[i][2] + 300 * t, 200 * t, 0))
    sps = [sphere('fl_spore_%d' % i, 0.07, (green, teal, pink)[i % 3], 6, 4) for i in range(12)]
    kj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(sps, lambda t, i: (kj[i][0] * (0.3 + 1.5 * t), kj[i][1] * (0.3 + 1.5 * t), 8.4 - 12.0 * t), smax=1.3)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, green if i % 2 else teal, 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: glowing spore cloud, mushrooms sprout around
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.6, ghost('sph_flash', '#d8ffe8', 2.0, 0.7, 1.2), 14, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 5, scale=2.2, alpha=0.7)
    key(flash, f + 12, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    rg = torus('im_ring', 0.6, 0.06, green, 36, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 18, scale=4.2, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    for i in range(16):
        a = math.radians(i * 22.5 + rnd.uniform(-8, 8))
        r = rnd.uniform(1.0, 2.8) * (1.2 if math.cos(a) < 0 else 1.0)
        p = sphere('im_cloud_%d' % i, 0.45, (cloud, cloud2, cloud3)[i % 3], 12, 7)
        fly(p, (cx, 0, 0.3), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.8, 2.6)), f + i % 5, rnd.uniform(1.5, 2.4))
    for i in range(20):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.8, 3.0)
        sp = sphere('im_spore_%d' % i, rnd.uniform(0.06, 0.1), (green, teal, pink)[i % 3], 6, 4, ol=0)
        p0 = (cx + 0.4 * math.cos(a), 0.4 * math.sin(a), 0.4)
        key(sp, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sp, f + i % 6, loc=p0, scale=0.4, alpha=1)
        key(sp, f + 16, loc=(cx + 0.7 * r * math.cos(a), 0.7 * r * math.sin(a), rnd.uniform(1.2, 2.2)), scale=1.2, alpha=1)
        key(sp, IMPACT0 + 44, loc=(cx + r * math.cos(a + 0.5), r * math.sin(a + 0.5), rnd.uniform(2.6, 4.2)), scale=0.6, alpha=0)
        tidy(sp, 'impact')
        ease_keys(sp)
    for i in range(7):
        a = math.radians(i * 360 / 7 + 20)
        r = 1.5 + 0.5 * (i % 3)
        sc_ = rnd.uniform(0.7, 1.1)
        m = lathe('im_mush_%d' % i, MUSH, M['cap'] if i % 2 else M['cap2'], 10, loc=(cx + r * math.cos(a), r * math.sin(a), 0.0), ol=0.02)
        t0 = f + 3 + i
        key(m, IMPACT0, scale=0)
        key(m, t0, scale=0)
        key(m, t0 + 4, scale=(sc_ * 1.2, sc_ * 1.2, sc_ * 0.8))
        key(m, t0 + 7, scale=(sc_ * 0.95, sc_ * 0.95, sc_ * 1.15))
        key(m, t0 + 10, scale=sc_)
        key(m, IMPACT0 + 38, scale=sc_)
        key(m, IMPACT0 + 44, scale=0)
        tidy(m, 'impact')
        dot = sphere('im_mush_dot_%d' % i, 0.09 * sc_, green, 6, 4, loc=(cx + r * math.cos(a), r * math.sin(a) - 0.0, 0.95 * sc_), ol=0)
        key(dot, IMPACT0, scale=0, alpha=1)
        key(dot, t0 + 4, scale=0, alpha=1)
        key(dot, t0 + 10, scale=1.0, alpha=1)
        key(dot, IMPACT0 + 38, scale=1.0, alpha=1)
        key(dot, IMPACT0 + 44, scale=0, alpha=0)
        tidy(dot, 'impact')
    return True
