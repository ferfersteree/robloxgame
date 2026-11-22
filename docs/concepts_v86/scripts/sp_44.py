from spearlib import *

NAME = 'SP_44_pearl_lance'
N = 44
BG = '#8fd8da'        # sunken citadel waters
GROUND = '#d8caa4'
TIP = 9.45
TRAIL = 5.2
FX_EXPORT = {'bubble_dome': 'im_dome', 'ice_spike': 'im_spike_0', 'pearl': 'im_pearl_0', 'shell_rib': 'im_shell_0'}


def mats():
    return dict(
        gold=toon('pl_gold', '#f6c448', '#b0681e', '#fff2a8', spec=1.0, rim=0.5, rimcol='#fff6c0'),
        coral=toon('pl_coral', '#ff7a68', '#c0384e', '#ffb8a0', spec=0.6, emit=0.1),
        pink=toon('pl_pink', '#ffb0c8', '#d06088', '#ffe0ea', spec=0.7, emit=0.15),
        pearl=toon('pl_pearl', '#f6f0ff', '#b4a8e4', '#ffffff', spec=1.0, rim=0.7, emit=0.3, rimcol='#c8f4ff'),
        teal=toon('pl_teal', '#2aa8b0', '#146078', '#70e0d8', emit=0.1),
        navy=toon('pl_navy', '#2e5aa8', '#1b3170', '#6a96e4'),
        sand=toon('pl_sand', '#f4e2b8', '#c8a874', '#fff6e0', spec=0.3),
        ice=toon('pl_ice', '#c8f6ff', '#6ab8d8', '#ffffff', spec=1.0, emit=0.4),
        aqua=glow('pl_aqua', '#7ff4ff', 3.0),
        sun=glow('pl_sun', '#fff0b0', 3.4),
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
    gold, coral, pink, pearl, teal, navy, sand, aqua, sun = (M[k] for k in ('gold', 'coral', 'pink', 'pearl', 'teal', 'navy', 'sand', 'aqua', 'sun'))
    # ---- tail: conch-gold cap with a small pearl
    lathe('tail_cap', [(0.0, 0.0), (0.0, 0.12), (0.14, 0.26), (0.36, 0.3), (0.55, 0.2), (0.66, 0.0)], coral, 12)
    sphere('tail_pearl', 0.13, pearl, 8, 5, loc=(0, 0, 0.1))
    torus('tail_ring', 0.2, 0.045, gold, 12, 5, loc=(0, 0, 0.7))
    # ---- shaft: teal lacquer, rope wraps, gold caps, pearl inlays
    shaft_parts(teal, pink, gold, navy)
    for i in range(4):
        a = i * 1.6
        sphere('pearl_inlay_%d' % i, 0.06, pearl, 7, 4, loc=(0.145 * math.cos(a), 0.145 * math.sin(a), 4.1 + i * 0.4), ol=0.01)
    # ---- clam socket: coral bowl, gold lip, fan of scallop ribs behind the pearl
    lathe('clam_bowl', [(6.3, 0.14), (6.45, 0.35), (6.7, 0.62), (7.0, 0.74), (7.2, 0.68)], coral, 16, caps=True)
    torus('clam_lip', 0.7, 0.06, gold, 20, 5, loc=(0, 0, 7.18))
    for i in range(6):
        a = math.radians(i * 60 + 15)
        cone('clam_ridge_%d' % i, 0.07, 0.3, pink, 5, loc=(0.4 * math.cos(a), 0.4 * math.sin(a), 6.55), rot=aim((math.cos(a), math.sin(a), 0.3)), ol=0.012)
    for i in range(7):
        phi = 20 + i * 20
        leaf('clam_fan_%d' % i, 1.25 - 0.1 * abs(i - 3), 0.42, coral if i % 2 else pink, 0.05, 5, loc=(0, 0.42, 7.15), rot=(90, -phi, 0), ol=0.018)
    # ---- the big pearl floating in the clam, ringed by a gold orbit
    sphere('pearl', 0.58, pearl, 18, 10, loc=(0, 0, 7.75))
    sphere('pearl_shine', 0.14, M['sun'], 8, 5, loc=(-0.22, -0.4, 7.95), ol=0)
    torus('pearl_orbit', 0.82, 0.04, gold, 22, 4, loc=(0, 0, 7.75), rot=(75, 0, 20))
    torus('pearl_orbit_b', 0.7, 0.03, aqua, 20, 4, loc=(0, 0, 7.75), rot=(-60, 0, -30), ol=0)
    # ---- the lance: slim gold blade rising out of the pearl with a coral rib
    ol_ = [(0, 8.1), (0.26, 8.45), (0.34, 8.95), (0.15, 9.25), (0, TIP), (-0.15, 9.25), (-0.34, 8.95), (-0.26, 8.45)]
    blade('lance', ol_, 0.12, gold)
    blade('lance_core', [(x * 0.45, 8.5 + (z - 8.1) * 0.65) for (x, z) in ol_], 0.15, aqua, ol=0)
    tube('lance_neck', [(0, 0, 7.5), (0, 0, 8.1)], [0.1, 0.1], gold, 8)
    torus('lance_collar', 0.15, 0.05, coral, 12, 5, loc=(0, 0, 8.15))
    # ---- coral sprigs on the clam sides
    for s in (-1, 1):
        nm = 'ab'[s > 0]
        tube('coral_' + nm, [(s * 0.6, 0, 6.8), (s * 0.95, 0, 7.15), (s * 1.0, 0, 7.6), (s * 1.2, 0, 7.95)], [0.11, 0.09, 0.07, 0.0], coral, 7)
        sphere('coral_nub_' + nm, 0.1, sun, 7, 4, loc=(s * 1.0, 0, 7.6), ol=0)
    # ---- floating pearls and bubbles
    for i in range(5):
        a = math.radians(i * 72 + 20)
        sphere('float_pearl_%d' % i, 0.1 + 0.02 * (i % 2), pearl, 8, 5, loc=(1.1 * math.cos(a), 1.1 * math.sin(a) * 0.6, 7.0 + 0.45 * i))
    for i in range(3):
        a = math.radians(i * 120 + 60)
        sphere('float_bubble_%d' % i, 0.16, ghost('pl_bubble', '#e6ffff', 1.4, 0.9, 2.2, edge=True), 10, 6,
               loc=(0.95 * math.cos(a), 0.95 * math.sin(a), 8.4 + 0.25 * i))
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
    rnd = random.Random(4444)
    bub = ghost('pl_bubblefx', '#dffbff', 1.4, 0.9, 2.2, edge=True)
    aura = ghost('pl_aura', '#c8f8ff', 1.2, 0.05, 1.8)
    sun = M['sun']
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.0), scale=(1.4, 1.0, 1.6))
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.3)
        sphere('idle_bubble_%d' % i, rnd.uniform(0.06, 0.12), bub, 10, 6, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.4)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, sun, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), -0.5, 7.4 + i * 0.7), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    bubs = [sphere('fl_bubble_%d' % i, 0.16, bub, 10, 6) for i in range(14)]
    bj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.5, 1.4)) for _ in range(14)]
    stream(bubs, lambda t, i: (bj[i][0] * (0.25 + 1.0 * t) + 0.25 * math.sin(6 * t + i), bj[i][1] * (0.25 + 1.0 * t), 8.6 - 12.5 * t),
           smax=lambda t, i: bj[i][2] * (0.7 + 1.0 * t) * math.sin(math.pi * t) ** 0.4)
    prs = [sphere('fl_pearl_%d' % i, 0.1, M['pearl'], 8, 5, ol=0.012) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(prs, lambda t, i: (pj[i][0] * (0.4 + 1.0 * t), pj[i][1] * (0.4 + 1.0 * t), 8.6 - 12.5 * t), smax=1.2)
    shs = [leaf('fl_shell_%d' % i, 0.5, 0.36, M['pink'] if i % 2 else M['coral'], 0.04, 5, ol=0.012) for i in range(6)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(shs, lambda t, i: (sj[i][0] * (0.4 + 1.0 * t), sj[i][1] * (0.4 + 1.0 * t), 8.8 - 12.0 * t), smax=1.1,
           spin=lambda t, i: (sj[i][2] + 300 * t, 90, sj[i][2]))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, M['aqua'], 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: bubble dome, ice spikes in a clam-shell fan, scattered pearls
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    dome = sphere('im_dome', 1.0, ghost('pl_dome', '#d8fcff', 1.5, 0.55, 2.0, edge=True), 18, 10, loc=(cx, 0, 0.0))
    key(dome, IMPACT0, scale=0, alpha=1)
    key(dome, f, scale=0.4, alpha=1)
    key(dome, f + 8, scale=(2.7, 2.7, 2.1), alpha=0.9)
    key(dome, f + 26, scale=(2.9, 2.9, 2.25), alpha=0.8)
    key(dome, f + 34, scale=(3.4, 3.4, 2.6), alpha=0)
    tidy(dome, 'impact')
    ease_keys(dome)
    flash = sphere('im_flash', 0.6, ghost('pl_flash', '#ffffff', 2.0, 0.7, 1.2), 14, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 5, scale=2.2, alpha=0.7)
    key(flash, f + 12, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    for i in range(7):
        phi = -90 + i * 30
        pr = math.radians(phi)
        lf = leaf('im_shell_%d' % i, 1.5, 0.75, M['coral'] if i % 2 else M['pink'], 0.05, 5, loc=(cx, 0, 0.04), rot=(0, 0, phi), ol=0.015)
        t0 = f + 1 + abs(i - 3)
        key(lf, IMPACT0, scale=0)
        key(lf, t0, scale=0)
        key(lf, t0 + 5, scale=(1.5, 1.5, 1))
        key(lf, IMPACT0 + 36, scale=(1.5, 1.5, 1))
        key(lf, IMPACT0 + 44, scale=0)
        tidy(lf, 'impact')
    for i in range(11):
        phi = math.radians(-100 + i * 20)
        r = 1.3 + 0.5 * (i % 2) + 0.35 * (1 - abs(i - 5) / 5.0)
        h = 1.3 + 0.7 * (1 - abs(i - 5) / 5.0) + (0.25 if i % 2 else 0)
        c = crystal('im_spike_%d' % i, 0.16, h, M['ice'], 6, 0.35, 0.8,
                    loc=(cx + 0.4 + r * math.cos(phi), r * math.sin(phi), 0.0), rot=aim((math.cos(phi) * 0.35, math.sin(phi) * 0.35, 1), 0), ol=0.018)
        t0 = f + 2 + abs(i - 5)
        key(c, IMPACT0, scale=0)
        key(c, t0, scale=0)
        key(c, t0 + 4, scale=(1.1, 1.1, 1.2))
        key(c, t0 + 7, scale=1.0)
        key(c, IMPACT0 + 38, scale=1.0)
        key(c, IMPACT0 + 44, scale=0)
        tidy(c, 'impact')
    g = -0.03
    for i in range(9):
        a = math.radians(rnd.uniform(-90, 90) + (0 if i % 3 else 180))
        sp = rnd.uniform(0.07, 0.15)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.3, 0.45)))
        pr_ = sphere('im_pearl_%d' % i, rnd.uniform(0.11, 0.17), M['pearl'], 10, 6, ol=0.012)
        p0 = Vector((cx, 0, 0.3))
        key(pr_, IMPACT0, loc=p0, scale=0)
        key(pr_, f, loc=p0, scale=0.3)
        t = 0
        p = p0
        vz = v.z
        pos = p0.copy()
        bounces = 0
        while t < 36:
            t += 2
            pos = pos + Vector((v.x * 2, v.y * 2, vz * 2))
            vz += g * 2
            if pos.z <= 0.15:
                pos.z = 0.15
                vz = -vz * 0.45
                v = v * 0.6
                bounces += 1
            key(pr_, f + t, loc=pos, scale=1, interp='LINEAR')
            if bounces >= 3:
                break
        key(pr_, max(f + t + 2, IMPACT0 + 36), scale=1)
        key(pr_, IMPACT0 + 44, scale=0)
        tidy(pr_, 'impact')
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.2, 1.6)
        b = sphere('im_bubble_%d' % i, rnd.uniform(0.08, 0.2), bub, 10, 6)
        fly(b, (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.1), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(2.2, 3.8)), f + rnd.randint(0, 12), 1.0)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.8, 2.2)
        st = star('im_spark_%d' % i, 0.16, 0.04, 4, 0.02, sun, rot=(90, 0, 0), ol=0)
        fly(st, (cx, 0, 0.5), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.0, 2.8)), f + i, 1.2)
    return True
