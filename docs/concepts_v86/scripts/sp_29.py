from spearlib import *

NAME = 'SP_29_magma_tongue'
N = 29
BG = '#5e4048'        # volcanic haze
GROUND = '#55403f'    # cooled basalt
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'lava_geyser': 'im_geyser_0', 'lava_blob': 'im_blob_0', 'crust_rock': 'im_crust_0', 'lava_crack': 'im_crack',
             'fire_ring': 'fl_ring_0'}


def mats():
    return dict(
        basalt=toon('mgt_basalt', '#3a3136', '#1a1418', '#6e5f66', spec=0.9, rim=0.6, rimcol='#ff7a2a'),
        stone=toon('mgt_stone', '#5a4a4c', '#2c2326', '#8f7c7e', spec=0.5, rimcol='#ff9a4a'),
        leather=toon('mgt_leather', '#7a2a2a', '#42161a', '#b8584a'),
        gold=toon('mgt_gold', '#e6a73a', '#9a5a1c', '#ffe39a', spec=1.0),
        crust=toon('mgt_crust', '#2a2226', '#120e10', '#5a4a52', spec=0.4),
        lava=glow('mgt_lava', '#ff5a1a', 2.0),
        lava_hot=glow('mgt_lavahot', '#ffc040', 2.3),
        lava_red=glow('mgt_lavared', '#e0301a', 1.8),
    )


def pop(ob, t0, t1, sc=1.0, hold=40, over=1.15):
    s = (sc, sc, sc) if isinstance(sc, (int, float)) else tuple(sc)
    key(ob, IMPACT0, scale=0)
    key(ob, t0, scale=0)
    key(ob, t1, scale=tuple(x * over for x in s))
    key(ob, t1 + 3, scale=s)
    key(ob, IMPACT0 + hold, scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


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
    begin(NAME, N, ol=0.034)
    M = mats()
    basalt, stone, leather, gold, crust, lava, lava_hot, lava_red = (M[k] for k in (
        'basalt', 'stone', 'leather', 'gold', 'crust', 'lava', 'lava_hot', 'lava_red'))
    # ---- tail: basalt drip pommel with a molten bead
    lathe('pommel', [(0.0, 0.0), (0.03, 0.13), (0.15, 0.25), (0.4, 0.28), (0.62, 0.2), (0.72, 0.0)], basalt, 14)
    sphere('pommel_bead', 0.12, lava, 8, 5, loc=(0, 0, 0.12), ol=0)
    torus('pommel_seam', 0.27, 0.03, lava, 16, 5, loc=(0, 0, 0.42), ol=0)
    torus('pommel_ring', 0.19, 0.05, gold, 14, 6, loc=(0, 0, 0.82))
    # ---- shaft: black basalt with a spiralling lava seam and leather wraps
    rod('shaft_lo', 0.155, 0.75, 3.3, basalt, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, basalt, r1=0.145)
    coil('wrap_lo', 0.176, 0.034, 1.3, 1.9, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, gold, 14, 6, loc=(0, 0, 1.92))
    coil('wrap_hi', 0.175, 0.034, 3.12, 3.7, 4, leather, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.035, gold, 14, 6, loc=(0, 0, 3.1))
    coil('lava_spiral', 0.152, 0.022, 4.0, 5.7, 3, lava, segs=4, ol=0)
    for i, (z, a) in enumerate(((3.9, 0.5), (5.0, 2.6), (5.7, 4.4))):
        rock('crust_%d' % i, 0.1, crust, seed=i + 70, sub=0, rough=0.2, flat=True, loc=(0.15 * math.cos(a), 0.15 * math.sin(a), z), scale=(1, 1, 0.7), ol=0.012)
    # ---- socket: black stone cup with glowing seam
    lathe('socket', [(5.95, 0.15), (6.1, 0.28), (6.35, 0.4), (6.65, 0.42), (6.85, 0.34), (6.95, 0.0)], basalt, 14)
    torus('socket_rim', 0.4, 0.06, gold, 18, 6, loc=(0, 0, 6.65))
    torus('socket_glow', 0.36, 0.03, lava, 18, 5, loc=(0, 0, 6.2), ol=0)
    # ---- the lava tongue blade
    tp = [(0.0, 0, 6.8), (0.05, 0, 7.5), (0.14, 0, 8.2), (0.12, 0, 8.8), (0.0, 0, TIP)]
    tr = [0.4, 0.5, 0.44, 0.3, 0.0]
    tg = tube('tongue', tp, tr, lava, 10)
    tg.scale = (1.0, 0.5, 1.0)
    tc = tube('tongue_core', [(0.04, 0, 7.0), (0.08, 0, 7.7), (0.13, 0, 8.3), (0.1, 0, 8.8)], [0.2, 0.26, 0.2, 0.0], lava_hot, 8, ol=0)
    tc.scale = (1.0, 0.8, 1.0)
    for k, (z, sd, h, bend) in enumerate(((7.4, 1, 0.7, 0.2), (7.9, -1, 0.65, -0.2), (8.4, 1, 0.5, 0.15))):
        flame('lick_%d' % k, h, 0.13, lava_red if k != 1 else lava_hot, bend * sd, 6, loc=(sd * 0.42, 0, z), rot=(0, sd * 55, 0), ol=0)
    for i, (x, y, z, r) in enumerate(((0.3, -0.15, 7.15, 0.07), (-0.28, -0.14, 7.6, 0.06), (0.42, 0.0, 6.95, 0.06))):
        sphere('drip_%d' % i, r, lava_hot, 7, 4, loc=(x, y, z), ol=0)
    # ---- black stone frame: curved claws hugging the tongue + crossbands
    for s in (-1, 1):
        nm = 'a' if s < 0 else 'b'
        tube('claw_' + nm, [(s * 0.46, 0, 6.8), (s * 0.78, 0, 7.4), (s * 0.78, 0, 8.1), (s * 0.5, 0, 8.65), (s * 0.28, 0, 8.95)],
             [0.13, 0.12, 0.1, 0.07, 0.0], stone, 8)
        sphere('claw_boss_' + nm, 0.09, gold, 7, 4, loc=(s * 0.78, 0, 7.75), ol=0.012)
        rock('frost_rock_' + nm, 0.16, crust, seed=s + 80, sub=0, rough=0.2, flat=True, loc=(s * 0.62, 0.1, 6.95), ol=0.015)
    for z, R, x in ((7.2, 0.6, 0.04), (8.0, 0.5, 0.1)):
        torus('band_%d' % int(z * 10), R, 0.05, basalt, 16, 6, loc=(x, 0, z), scale=(1.0, 0.6, 1.0))
    for i in range(3):
        a = math.radians(i * 120 + 30)
        sphere('float_blob_%d' % i, 0.09, lava_hot if i % 2 else lava, 7, 4, loc=(0.9 * math.cos(a), 0.6 * math.sin(a), 7.6 + 0.4 * i), ol=0)
    rock('float_crust', 0.12, crust, seed=95, sub=0, rough=0.25, flat=True, loc=(-0.95, 0.15, 8.4), ol=0.015)
    tube('charm_cord', [(0.15, 0.04, 6.4), (0.3, 0.08, 6.1), (0.36, 0.1, 5.8)], 0.022, leather, 5)
    sphere('charm_ember', 0.09, lava, 7, 4, loc=(0.36, 0.1, 5.7), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2929)
    smoke = ghost('mgt_smoke', '#4a3a40', 0.6, 0.85, 1.0)
    heat = ghost('mgt_heat', '#ff7a2a', 1.2, 0.05, 1.8)
    lava, lava_hot, lava_red = M['lava'], M['lava_hot'], M['lava_red']
    # ---------------- idle
    fx('idle')
    sphere('idle_heat', 0.6, heat, 14, 8, loc=(0.1, 0, 8.0), scale=(1.4, 0.8, 2.0))
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 0.9)
        flame('idle_ember_%d' % i, rnd.uniform(0.12, 0.22), 0.045, lava_hot if i % 2 else lava, 0.1, 6,
              loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.4)))
    for i in range(2):
        sphere('idle_drip_%d' % i, 0.06, lava_hot, 6, 4, loc=(0.45 + 0.2 * i, 0.1, 6.6 - 0.35 * i))
    # ---------------- flight: lava blobs, flame tongues, smoke, sparks, fire rings
    fx('flight')
    blobs = [sphere('fl_blob_%d' % i, 0.14, lava_hot if i % 2 else lava, 8, 5) for i in range(8)]
    bj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.8, 1.4)) for _ in range(8)]
    stream(blobs, lambda t, i: (bj[i][0] * (0.3 + 0.8 * t), bj[i][1] * (0.3 + 0.8 * t), 8.6 - 11.0 * t),
           smax=lambda t, i: bj[i][2] * (1.2 - 0.4 * t) * math.sin(math.pi * t) ** 0.5)
    flames = [flame('fl_flame_%d' % i, 0.7, 0.15, (lava, lava_hot, lava_red)[i % 3], 0.0, 8) for i in range(8)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.8, 1.3)) for _ in range(8)]
    stream(flames, lambda t, i: (fj[i][0] * (0.2 + 0.6 * t), fj[i][1] * (0.2 + 0.6 * t), 9.0 - 11.0 * t),
           smax=lambda t, i: fj[i][2] * (1.3 - 0.5 * t) * math.sin(math.pi * t) ** 0.5, spin=lambda t, i: (180, 0, 0))
    puffs = [sphere('fl_smoke_%d' % i, 0.35, smoke, 12, 7) for i in range(6)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.3 + 0.8 * t), pj[i][1] * (0.3 + 0.8 * t), 4.0 - 8.5 * t),
           smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    sps = [sphere('fl_spark_%d' % i, 0.06, lava_hot, 6, 4) for i in range(6)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(sps, lambda t, i: (sj[i][0] * (0.3 + 1.5 * t), sj[i][1] * (0.3 + 1.5 * t), 8.4 - 13.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.055, lava if i % 2 else lava_hot, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: the ground cracks forward, lava geysers jet from the crack, blobs and crust rocks rain down
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('mgt_flash', '#ffc878', 2.0, 0.65, 1.2), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.75)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    pud = sphere('im_puddle', 0.8, lava, 14, 4, loc=(cx, 0, 0.03))
    key(pud, IMPACT0, scale=0, alpha=1)
    key(pud, f, scale=(0.3, 0.3, 0.03), alpha=1)
    key(pud, f + 12, scale=(2.0, 2.0, 0.05), alpha=1)
    key(pud, IMPACT0 + 36, scale=(2.2, 2.2, 0.05), alpha=0.9)
    key(pud, IMPACT0 + 44, scale=(2.2, 2.2, 0.05), alpha=0)
    tidy(pud, 'impact')
    pts = zigzag((cx, 0, 0.02), (cx + 3.2, 0, 0.02), 6, 0.14, seed=5)
    for p in pts:
        p.z = 0.02
    cr = tube('im_crack', pts, [0.12, 0.11, 0.1, 0.09, 0.08, 0.06, 0.0], lava, 4, smooth=False, ol=0)
    cr.scale = (1, 1, 0.3)
    key(cr, IMPACT0, scale=0, alpha=1)
    key(cr, f, scale=0, alpha=1)
    key(cr, f + 6, scale=(1, 1, 0.3), alpha=1)
    key(cr, IMPACT0 + 34, scale=(1, 1, 0.3), alpha=1)
    key(cr, IMPACT0 + 44, scale=(1, 1, 0.3), alpha=0)
    tidy(cr, 'impact')
    for k, (dx, dy) in enumerate(((0.9, 0.5), (1.9, -0.5))):
        br = tube('im_branch_%d' % k, [(cx + dx, 0.0, 0.02), (cx + dx + 0.2, dy * 0.6, 0.02), (cx + dx + 0.3, dy * 1.4, 0.02)],
                  [0.08, 0.06, 0.0], lava_red, 4, smooth=False, ol=0)
        br.scale = (1, 1, 0.3)
        key(br, IMPACT0, scale=0, alpha=1)
        key(br, f + 5 + k * 2, scale=0, alpha=1)
        key(br, f + 10 + k * 2, scale=(1, 1, 0.3), alpha=1)
        key(br, IMPACT0 + 34, scale=(1, 1, 0.3), alpha=1)
        key(br, IMPACT0 + 44, scale=(1, 1, 0.3), alpha=0)
        tidy(br, 'impact')
    for k, (dx, h) in enumerate(((0.7, 2.8), (1.7, 2.2), (2.6, 1.6))):
        t0 = f + 3 + k * 3
        g1 = flame('im_geyser_%d' % k, h, 0.34, lava, 0.0, 8, loc=(cx + dx, 0, 0.0))
        g2 = flame('im_gcore_%d' % k, h * 0.85, 0.2, lava_hot, 0.0, 8, loc=(cx + dx, 0, 0.0))
        for g_ in (g1, g2):
            key(g_, IMPACT0, scale=0)
            key(g_, t0, scale=(0.3, 0.3, 0.1))
            key(g_, t0 + 4, scale=(1.0, 1.0, 1.25))
            key(g_, t0 + 10, scale=(0.85, 0.85, 1.0))
            key(g_, t0 + 18, scale=(0.9, 0.9, 1.1))
            key(g_, t0 + 25, scale=(0.3, 0.3, 0.2))
            key(g_, t0 + 29, scale=0)
            tidy(g_, 'impact')
            ease_keys(g_)
    for i in range(12):
        a = math.radians(rnd.uniform(-70, 70))
        sp_ = rnd.uniform(0.05, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.26, 0.34)))
        bl = sphere('im_blob_%d' % i, rnd.uniform(0.08, 0.16), lava_hot if i % 3 == 0 else lava, 7, 4)
        toss(bl, Vector((cx + 0.7 + (i % 3) * 0.9, 0, 0.3)), v, f + 3 + (i % 3) * 3 + rnd.randint(0, 2), g=-0.03, floor=0.08, spin=(0, 0, 0), hold=36)
    for i in range(8):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.25, 0.4)))
        rk = rock('im_crust_%d' % i, rnd.uniform(0.12, 0.2), M['crust'], seed=i + 30, sub=1, rough=0.25, flat=True, ol=0.015)
        toss(rk, Vector((cx + 0.5, 0, 0.3)), v, f + 2, g=-0.03, floor=0.1, spin=(30, 20, 0), hold=36)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.3, 1.8)
        em = flame('im_ember_%d' % i, rnd.uniform(0.14, 0.22), 0.05, lava_hot if i % 2 else lava, 0.0, 6)
        t0 = f + 2 + rnd.randint(0, 10)
        p0 = (cx + 1.0 + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.2)
        p1 = (cx + 1.0 + r * math.cos(a), r * math.sin(a), rnd.uniform(1.6, 3.2))
        key(em, IMPACT0, loc=p0, scale=0)
        key(em, t0, loc=p0, scale=0.3)
        key(em, t0 + 6, scale=1.0)
        key(em, t0 + 28, loc=p1, scale=0.0)
        tidy(em, 'impact')
        ease_keys(em)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 2.0)
        sm = sphere('im_smoke_%d' % i, 0.4, smoke, 12, 7)
        t0 = f + 4 + rnd.randint(0, 8)
        p0 = (cx + 1.0 + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.4)
        p1 = (cx + 1.0 + r * math.cos(a), r * math.sin(a), rnd.uniform(2.2, 3.6))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.8, 2.6), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    return True
