from spearlib import *

NAME = 'SP_23_coral_branch'
N = 23
BG = '#c6eef0'        # reef shallows
GROUND = '#f1dcae'    # sand
TIP = 9.35
TRAIL = 5.2


def mats():
    return dict(
        coral=toon('co_coral', '#ff6f5e', '#c23a4a', '#ffab8f', spec=0.6, emit=0.1),
        coral_tip=toon('co_coral_tip', '#ffc9a6', '#f08870', '#fff1e0', spec=0.8, emit=0.35),
        teal=toon('co_teal', '#1aa3a8', '#0e6278', '#5fd6d0'),
        navy=toon('co_navy', '#2b5aa6', '#1b3570', '#5f8fde'),
        sand=toon('co_sand', '#f4dfb6', '#c9a676', '#fff6e2', spec=0.3),
        shell=toon('co_shell', '#ffd2c6', '#d98a8a', '#fff3ee', spec=0.8),
        pearl=toon('co_pearl', '#eef3ff', '#a9b4d8', '#ffffff', spec=1.0, emit=0.2),
        glass=toon('co_glass', '#7fe8cc', '#3aa59a', '#d2fff2', spec=1.0, emit=0.25),
        rope=toon('co_rope', '#e8cf95', '#a98950', '#fff0c4', spec=0.2),
    )


def branch(nm, p0, d, length, r0, mat, bend=(0, 0, 0), n=6, r1=None, tip=None, segs=8):
    d = Vector(d).normalized()
    b = Vector(bend)
    pts, rad = [], []
    r1 = r0 * 0.5 if r1 is None else r1
    for i in range(n + 1):
        t = i / n
        pts.append(Vector(p0) + d * length * t + b * math.sin(math.pi * t * 0.9))
        rad.append(r0 + (r1 - r0) * t)
    if tip == 'point':
        rad[-1] = 0.0
    tube(nm, pts, rad, mat, segs)
    return pts[-1], (pts[-1] - pts[-2]).normalized()


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    coral, coral_tip, teal, navy, sand, shell, pearl, glass, rope = (M[k] for k in (
        'coral', 'coral_tip', 'teal', 'navy', 'sand', 'shell', 'pearl', 'glass', 'rope'))
    # ---- tail: spiral conch pommel
    lathe('conch', [(0.0, 0.0), (0.02, 0.1), (0.12, 0.22), (0.3, 0.27), (0.5, 0.24), (0.66, 0.17), (0.72, 0.0)], shell, 14)
    coil('conch_spiral', 0.24, 0.045, 0.08, 0.62, 2.2, shell, segs=6, R1=0.16)
    cone('conch_spike', 0.06, 0.2, shell, 6, loc=(0, 0, 0.2), rot=(180, 0, 0), ol=0.015)
    torus('tail_ring', 0.17, 0.045, navy, 14, 6, loc=(0, 0, 0.78))
    # ---- shaft: teal lacquered driftwood
    rod('shaft_lo', 0.155, 0.75, 3.3, teal, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.45, teal, r1=0.145)
    for i, z in enumerate((1.25, 1.5, 1.75)):
        torus('glass_ring_%d' % i, 0.17, 0.045, glass if i != 1 else navy, 14, 6, loc=(0, 0, z))
    torus('glass_cap', 0.168, 0.03, sand, 14, 5, loc=(0, 0, 1.95), ol=0.015)
    coil('rope_wrap', 0.172, 0.032, 3.08, 3.7, 5, rope, segs=5)
    torus('rope_cap', 0.172, 0.04, navy, 14, 6, loc=(0, 0, 3.05))
    for i in range(4):
        a = i * 1.7
        sphere('pearl_inlay_%d' % i, 0.06, pearl, 8, 5, loc=(0.135 * math.cos(a), 0.135 * math.sin(a), 4.2 + i * 0.42), ol=0.012)
    for i, (z, a) in enumerate(((5.1, 0.6), (5.35, 3.5), (2.6 + 2.6, 5.0))):
        lathe('barnacle_%d' % i, [(0, 0.07), (0.05, 0.065), (0.09, 0.03), (0.09, 0)], sand, 7, 'Z',
              loc=(0.14 * math.cos(a), 0.14 * math.sin(a), z), rot=aim((math.cos(a), math.sin(a), 0.3)), ol=0.012)
    torus('neck_ring', 0.165, 0.045, navy, 14, 6, loc=(0, 0, 6.35))
    # ---- scallop-shell socket: cup of ribbed petals
    lathe('socket', [(6.3, 0.14), (6.45, 0.2), (6.75, 0.26), (6.95, 0.2), (7.0, 0)], sand, 14)
    for i in range(6):
        a = i * 60 + 30
        leaf('shell_%d' % i, 0.62, 0.34, shell, 0.04, 5, loc=(0.12 * math.cos(math.radians(a)), 0.12 * math.sin(math.radians(a)), 6.55),
             rot=(0, -62, a), ol=0.015)
    # ---- coral: main spike + branching arms with glowing tips
    top, _ = branch('coral_main', (0, 0, 6.85), (0, 0, 1), TIP - 6.85, 0.24, coral, bend=(0.06, 0, 0), n=7, tip='point')
    arms = [((0.05, 0, 7.1), (1, 0.15, 1.15), 1.25, 0.12, (0, 0.1, 0.1)),
            ((-0.05, 0, 7.25), (-1, -0.1, 1.0), 1.15, 0.115, (0, -0.1, 0.1)),
            ((0.0, 0.05, 7.55), (0.25, 1, 1.25), 0.9, 0.095, (0.1, 0, 0.05)),
            ((0.0, -0.05, 7.75), (-0.2, -1, 1.4), 0.85, 0.09, (-0.1, 0, 0.05)),
            ((0.03, 0, 8.25), (1, -0.3, 1.8), 0.6, 0.075, (0, 0, 0))]
    tips = []
    for i, (p0, d, ln, r0, bd) in enumerate(arms):
        ln, r0 = ln * 1.35, r0 * 1.2
        e, dd = branch('coral_arm_%d' % i, p0, d, ln, r0, coral, bend=bd, n=5)
        tips.append((e, r0 * 0.5))
        if i < 4:
            mid = Vector(p0) + Vector(d).normalized() * ln * 0.55
            side = Vector((-d[1], d[0], 0.6)) if i % 2 else Vector((d[1], -d[0], 0.6))
            e2, _ = branch('coral_twig_%d' % i, mid, Vector(d).normalized() * 0.4 + side.normalized() * 0.6 + Vector((0, 0, 0.6)), 0.5, r0 * 0.6, coral, n=4)
            tips.append((e2, r0 * 0.32))
    for i, (p, r) in enumerate(tips):
        sphere('coral_nub_%d' % i, r * 1.35, coral_tip, 8, 5, loc=p, ol=0.012)
    # polyps (bumps) along the main spike
    for i in range(5):
        a = i * 2.3
        z = 7.0 + i * 0.36
        rr = 0.2 * (1 - (z - 6.85) / (TIP - 6.85)) + 0.02
        sphere('polyp_%d' % i, 0.055, coral_tip, 7, 4, loc=(rr * math.cos(a), rr * math.sin(a), z), ol=0.01)
    # ---- starfish charm
    tube('charm_cord', [(0.15, 0.05, 6.4), (0.3, 0.1, 6.15), (0.34, 0.12, 5.85)], 0.02, rope, 5)
    star('starfish', 0.22, 0.09, 5, 0.09, coral_tip, loc=(0.36, 0.13, 5.68), rot=(90, 0, 15), ol=0.015)
    sphere('charm_pearl', 0.07, pearl, 8, 5, loc=(0.3, 0.1, 6.12), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2323)
    bub = ghost('co_bubble', '#dffbff', 1.4, 0.9, 2.2, edge=True)
    aqua = glow('co_aqua', '#7ff6ff', 2.2)
    pink = glow('co_pink', '#ff9fb6', 2.6)
    cr_pink = toon('co_crys_pink', '#ff8fb0', '#d0507a', '#ffd3e1', spec=1.0, emit=0.5)
    cr_aqua = toon('co_crys_aqua', '#6fe9e0', '#2a9fb0', '#d6fffb', spec=1.0, emit=0.5)
    # ---------------- idle: slow bubbles around the coral, tiny glints
    fx('idle')
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 0.9)
        sphere('idle_bubble_%d' % i, rnd.uniform(0.06, 0.12), bub, 10, 6, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.4)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, pink, loc=(rnd.uniform(-0.7, 0.7), -0.3, 7.6 + i * 0.5), rot=(90, 0, 0))
    # ---------------- flight: bubble stream + coral crystal shards + water rings
    fx('flight')
    bubs = [sphere('fl_bubble_%d' % i, 0.16, bub, 10, 6) for i in range(16)]
    bj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.5, 1.4)) for _ in range(16)]
    stream(bubs, lambda t, i: (bj[i][0] * (0.25 + 1.0 * t) + 0.25 * math.sin(6 * t + i), bj[i][1] * (0.25 + 1.0 * t), 8.6 - 12.5 * t),
           smax=lambda t, i: bj[i][2] * (0.7 + 1.0 * t) * math.sin(math.pi * t) ** 0.4)
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.32, cr_pink if i % 2 else cr_aqua, 5, 0.4, 0.6, both=True, ol=0.012) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(shards, lambda t, i: (sj[i][0] * (0.35 + 0.9 * t), sj[i][1] * (0.35 + 0.9 * t), 8.9 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.045, aqua, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.0 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: reef bloom - crystal-coral grows in a spiral, ripple rings, bubble fountain
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.7)
    f = IMPACT0 + 4
    cx = 0.45
    for k in range(3):
        rp = torus('im_ripple_%d' % k, 0.6, 0.05, aqua, 36, 5, loc=(cx, 0, 0.04))
        key(rp, IMPACT0, scale=0, alpha=1)
        key(rp, f + k * 5, scale=0.2, alpha=1)
        key(rp, f + k * 5 + 16, scale=4.2 - k * 0.6, alpha=0)
        tidy(rp, 'impact', interp='LINEAR')
        ease_keys(rp)
    # sand ring
    sand = rock('im_sandmound', 0.55, M['sand'], seed=4, sub=2, rough=0.18, loc=(cx, 0, -0.12), scale=(1.6, 1.6, 0.4))
    key(sand, IMPACT0, scale=0)
    key(sand, f, scale=0)
    key(sand, f + 4, scale=(1.7, 1.7, 0.5))
    key(sand, f + 7, scale=(1.6, 1.6, 0.4))
    key(sand, IMPACT0 + 40, scale=(1.6, 1.6, 0.4))
    key(sand, IMPACT0 + 44, scale=0)
    tidy(sand, 'impact')
    # coral crystals grow in a golden-angle spiral around the spear
    for i in range(16):
        a = i * 2.4
        r = 0.7 + 0.16 * i
        p = (cx + r * math.cos(a), r * math.sin(a), 0.0)
        h = 1.3 - i * 0.045 + rnd.uniform(-0.1, 0.1)
        lean = Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 1))
        c = crystal('im_crys_%d' % i, 0.13 + 0.05 * (1 - i / 16), h, cr_pink if i % 3 else cr_aqua, 6, 0.32, 0.8,
                    loc=p, rot=aim(lean, rnd.uniform(0, 60)), ol=0.018)
        t0 = f + 2 + int(i * 1.2)
        key(c, IMPACT0, scale=0)
        key(c, t0, scale=0)
        key(c, t0 + 5, scale=(1.15, 1.15, 1.2))
        key(c, t0 + 8, scale=1.0)
        key(c, IMPACT0 + 39, scale=1.0)
        key(c, IMPACT0 + 44, scale=0)
        tidy(c, 'impact')
    # coral branches pop from the sand right at the spear
    for i in range(4):
        a = i * 1.57 + 0.6
        base = Vector((cx + 0.4 * math.cos(a), 0.4 * math.sin(a), 0))
        nm = 'im_coral_%d' % i
        b = tube(nm, [base, base + Vector((math.cos(a) * 0.3, math.sin(a) * 0.3, 0.55)), base + Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 0.95))],
                 [0.09, 0.07, 0.05], M['coral'], 7)
        nub = sphere(nm + '_nub', 0.075, M['coral_tip'], 8, 5, loc=base + Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 0.95)))
        for o in (b, nub):
            key(o, IMPACT0, scale=0)
            key(o, f + 1 + i, scale=0)
            key(o, f + 7 + i, scale=1.0)
            key(o, IMPACT0 + 40, scale=1.0)
            key(o, IMPACT0 + 44, scale=0)
            tidy(o, 'impact')
        # nub positions are scaled about their own origin -> keep them near the tip
    # bubble fountain
    for i in range(18):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.1, 1.4)
        b = sphere('im_bubble_%d' % i, rnd.uniform(0.08, 0.2), bub, 10, 6)
        t0 = f + rnd.randint(0, 14)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.1)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(2.2, 3.8))
        key(b, IMPACT0, loc=p0, scale=0)
        key(b, t0, loc=p0, scale=0.3)
        key(b, t0 + 6, scale=1.0)
        key(b, min(t0 + 24, IMPACT0 + 44), loc=p1, scale=0.0)
        tidy(b, 'impact')
    flash = sphere('im_flash', 0.6, ghost('co_flash', '#c8ffff', 1.5, 0.55, 1.6), 16, 8, loc=(cx, 0, 0.2))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 5, scale=1.5, alpha=0.7)
    key(flash, f + 12, scale=2.1, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    return True
