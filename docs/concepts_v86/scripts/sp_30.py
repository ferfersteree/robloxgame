from spearlib import *

NAME = 'SP_30_phoenix_wing'
N = 30
BG = '#c98a6a'        # sunset caldera
GROUND = '#85594a'    # scorched earth
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'wing_feather': 'im_wing_a0', 'ember_flame': 'im_ember_0', 'fire_ring': 'im_ring', 'fall_feather': 'im_feather_0',
             'flame_tongue': 'fl_flame_0'}


def mats():
    return dict(
        red=toon('phw_red', '#e0342a', '#8a1420', '#ff7a5a', spec=0.7, emit=0.25, rimcol='#ffd06a'),
        orange=toon('phw_orange', '#ff8a2a', '#c04a14', '#ffc06a', spec=0.7, emit=0.3, rimcol='#fff0a0'),
        gold=toon('phw_gold', '#ffc83a', '#c07a1a', '#fff0a0', spec=1.0, emit=0.3),
        dark=toon('phw_dark', '#5a1a24', '#2a0a12', '#964050', spec=0.5),
        cream=toon('phw_cream', '#fff0d0', '#d8b080', '#ffffff', spec=0.4),
        ember=glow('phw_ember', '#ff6a1a', 2.2),
        hot=glow('phw_hot', '#ffd24a', 2.2),
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
    red, orange, gold, dark, cream, ember, hot = (M[k] for k in ('red', 'orange', 'gold', 'dark', 'cream', 'ember', 'hot'))
    # ---- tail: ember orb with three hanging plumes
    sphere('pommel_orb', 0.2, ember, 10, 6, loc=(0, 0, 1.0), ol=0)
    lathe('pommel_cup', [(0.85, 0.0), (0.9, 0.1), (1.0, 0.26), (1.12, 0.22), (1.18, 0.0)], gold, 12, caps=False)
    for i, (ph, col) in enumerate(((75, red), (90, orange), (105, red))):
        leaf('plume_%d' % i, 0.85, 0.3, col, 0.04, 5, loc=(0, 0, 1.0), rot=(90 if i != 1 else 90, ph, 0), ol=0.015)
    torus('pommel_ring', 0.19, 0.045, gold, 14, 6, loc=(0, 0, 1.25))
    # ---- shaft: crimson lacquer with gold bands and feather trim
    rod('shaft_lo', 0.155, 1.2, 3.3, dark, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.0, dark, r1=0.145)
    coil('trim_lo', 0.176, 0.034, 1.4, 1.9, 4, gold, segs=5)
    torus('trim_lo_cap', 0.18, 0.04, red, 14, 6, loc=(0, 0, 1.92))
    coil('trim_hi', 0.175, 0.034, 3.12, 3.7, 4, gold, segs=5, phase=1.0)
    torus('trim_hi_cap', 0.178, 0.035, red, 14, 6, loc=(0, 0, 3.1))
    for i, z in enumerate((4.2, 4.45, 4.7)):
        torus('seam_%d' % i, 0.152, 0.025, ember if i != 1 else hot, 14, 5, loc=(0, 0, z), ol=0)
    for i in range(3):
        a = i * 2.1 + 0.4
        leaf('shaft_feather_%d' % i, 0.5, 0.16, cream if i % 2 else orange, 0.03, 5, loc=(0.16 * math.cos(a), 0.16 * math.sin(a), 5.0 + 0.2 * i),
             rot=(0, 70, math.degrees(a)), ol=0.012)
    # ---- feather-fan grip collar: six drooping feathers around the socket
    lathe('socket', [(5.95, 0.15), (6.1, 0.26), (6.3, 0.32), (6.55, 0.28), (6.65, 0.0)], gold, 14)
    for i in range(6):
        a = math.radians(i * 60 + 15)
        leaf('fan_%d' % i, 0.95, 0.34, red if i % 2 else orange, 0.04, 5, loc=(0.2 * math.cos(a), 0.2 * math.sin(a), 6.35),
             rot=(0, 50, math.degrees(a)), ol=0.015)
    torus('socket_ring', 0.26, 0.05, gold, 16, 6, loc=(0, 0, 6.55))
    sphere('socket_gem', 0.12, hot, 8, 5, loc=(0, -0.3, 6.5), ol=0)
    # ---- the phoenix blade: flame spike with two feathered wings
    spike = tube('spike', [(0, 0, 6.65), (0.02, 0, 7.4), (0.0, 0, 8.2), (-0.02, 0, 8.85), (0.0, 0, TIP)], [0.3, 0.34, 0.28, 0.17, 0.0], orange, 10)
    spike.scale = (1.0, 0.6, 1.0)
    tube('spike_core', [(0, -0.1, 6.9), (0, -0.1, 7.6), (0, -0.1, 8.4), (0, -0.08, 9.0)], [0.12, 0.16, 0.11, 0.0], hot, 6, ol=0)
    for s in (-1, 1):
        nm = 'a' if s < 0 else 'b'
        for k in range(5):
            th = 18 + k * 16
            ln = (1.65, 1.6, 1.45, 1.2, 0.95)[k]
            ph = -th if s > 0 else th - 180
            col = (red, orange, gold, orange, red)[k]
            leaf('wing_%s%d' % (nm, k), ln, 0.36 - 0.02 * k, col, 0.05, 6, loc=(s * 0.2, 0.0 + 0.012 * k, 6.95 + 0.1 * k), rot=(90, ph, 0), ol=0.018)
            a = math.radians(th)
            sphere('wing_tip_%s%d' % (nm, k), 0.06, hot, 6, 4, loc=(s * (0.2 + ln * math.cos(a)), 0.0, 6.95 + 0.1 * k + ln * math.sin(a)), ol=0)
        tube('wing_bone_' + nm, [(s * 0.15, 0, 6.85), (s * 0.6, 0, 7.05), (s * 1.1, 0, 7.45)], [0.08, 0.07, 0.04], dark, 6)
    for i, (x, y, z) in enumerate(((0.85, 0.2, 8.6), (-0.85, 0.2, 8.5), (0.55, -0.25, 9.0))):
        sphere('float_ember_%d' % i, 0.08, hot, 7, 4, loc=(x, y, z), ol=0)
    tube('charm_cord', [(0.15, 0.04, 5.9), (0.3, 0.08, 5.6), (0.36, 0.1, 5.3)], 0.02, gold, 5)
    star('charm_star', 0.16, 0.07, 6, 0.06, hot, loc=(0.36, 0.1, 5.15), rot=(90, 0, 0), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(3030)
    fl_o = glow('phw_fl_o', '#ff6a1a', 3.0)
    fl_y = glow('phw_fl_y', '#ffd24a', 3.4)
    fl_r = glow('phw_fl_r', '#e0302a', 2.6)
    heat = ghost('phw_heat', '#ff9a3a', 1.2, 0.05, 1.8)
    glint = glow('phw_glint', '#fff2c0', 3.0)
    # ---------------- idle
    fx('idle')
    sphere('idle_heat', 0.7, heat, 14, 8, loc=(0, 0, 7.9), scale=(2.0, 0.8, 1.5))
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.1)
        flame('idle_ember_%d' % i, rnd.uniform(0.12, 0.22), 0.045, fl_y if i % 2 else fl_o, 0.1, 6,
              loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.2)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.3), -0.25, 7.5 + i * 0.5), rot=(90, 0, 0))
    # ---------------- flight: flame feathers, drifting feather blades, embers, rings
    fx('flight')
    flames = [flame('fl_flame_%d' % i, 0.7, 0.16, (fl_o, fl_y, fl_r)[i % 3], 0.0, 8) for i in range(10)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.8, 1.4)) for _ in range(10)]
    stream(flames, lambda t, i: (fj[i][0] * (0.2 + 0.8 * t), fj[i][1] * (0.2 + 0.8 * t), 9.0 - 11.5 * t),
           smax=lambda t, i: fj[i][2] * (1.4 - 0.6 * t) * math.sin(math.pi * t) ** 0.5,
           spin=lambda t, i: (180 + fj[i][0] * 20, fj[i][1] * 20, 0))
    fe = [leaf('fl_feather_%d' % i, 0.7, 0.24, fl_y if i % 2 else fl_o, 0.03, 5) for i in range(8)]
    ej = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(fe, lambda t, i: (ej[i][0] * (0.4 + 1.1 * t), ej[i][1] * (0.4 + 1.1 * t), 8.4 - 12.0 * t), smax=1.1,
           spin=lambda t, i: (ej[i][2] + 200 * t, 90 + 60 * math.sin(6 * t + i), 180 + 40 * ej[i][0]))
    sps = [sphere('fl_spark_%d' % i, 0.06, fl_y, 6, 4) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(sps, lambda t, i: (sj[i][0] * (0.3 + 1.6 * t), sj[i][1] * (0.3 + 1.6 * t), 8.4 - 13.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.6, 0.055, fl_o if i % 2 else fl_y, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.0 * t), smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (0, 0, 360 * t))
    # ---------------- impact: two fire wings unfold, flap once and dissolve into embers
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('phw_flash', '#ffe0a0', 2.0, 0.65, 1.2), 14, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.2, alpha=0.75)
    key(flash, f + 10, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    for k in range(2):
        rg = torus('im_ring' if k == 0 else 'im_ring_%d' % k, 0.6, 0.06, fl_y if k == 0 else fl_o, 36, 5, loc=(cx, 0, 0.05))
        key(rg, IMPACT0, scale=0, alpha=1)
        key(rg, f + k * 5, scale=0.3, alpha=1)
        key(rg, f + k * 5 + 14, scale=4.4 - k, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
        ease_keys(rg)
    # wings: two fans of flame feathers in vertical planes at +-55 degrees from the spear plane
    for w, (psi, nm) in enumerate(((-55, 'a'), (55, 'b'))):
        for k in range(6):
            alpha_k = 10 + k * 15
            hh = (2.3, 2.6, 2.8, 2.6, 2.2, 1.8)[k]
            fe_ = flame('im_wing_%s%d' % (nm, k), hh, 0.27, (fl_o, fl_y, fl_r)[k % 3], 0.0, 8, loc=(cx + 0.15, 0.0, 0.1), rot=(0, 0, psi))
            t0 = f + k
            key(fe_, IMPACT0, scale=0, rot=(0, 5, psi))
            key(fe_, t0, scale=0.3, rot=(0, 5, psi))
            key(fe_, t0 + 6, scale=(1.0, 1.0, 1.0), rot=(0, alpha_k, psi))
            key(fe_, t0 + 12, scale=(0.9, 0.9, 0.9), rot=(0, alpha_k * 0.5, psi))
            key(fe_, t0 + 18, scale=(1.0, 1.0, 1.05), rot=(0, alpha_k * 1.12, psi))
            key(fe_, t0 + 26, scale=(0.9, 0.9, 1.0), rot=(0, alpha_k * 1.05, psi))
            key(fe_, t0 + 32, scale=(0.4, 0.4, 0.5), rot=(0, alpha_k * 1.25, psi))
            key(fe_, t0 + 34, scale=0, rot=(0, alpha_k * 1.3, psi))
            tidy(fe_, 'impact')
            ease_keys(fe_)
    core = flame('im_core', 2.2, 0.45, fl_y, 0.0, 10, loc=(cx, 0, 0))
    key(core, IMPACT0, scale=0)
    key(core, f, scale=(0.5, 0.5, 0.2))
    key(core, f + 5, scale=(1.0, 1.0, 1.1))
    key(core, f + 12, scale=(0.5, 0.5, 0.6))
    key(core, f + 18, scale=0)
    tidy(core, 'impact')
    # embers released as the wings dissolve
    for i in range(14):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 2.2)
        em = flame('im_ember_%d' % i, rnd.uniform(0.14, 0.22), 0.05, fl_y if i % 2 else fl_o, 0.0, 6)
        t0 = f + 14 + rnd.randint(0, 10)
        p0 = (cx + r * 0.5 * math.cos(a), r * 0.5 * math.sin(a), rnd.uniform(0.8, 2.0))
        p1 = (cx + r * math.cos(a), r * math.sin(a), p0[2] + rnd.uniform(1.0, 1.8))
        key(em, IMPACT0, loc=p0, scale=0)
        key(em, t0, loc=p0, scale=0.3)
        key(em, t0 + 5, scale=1.0)
        key(em, min(t0 + 24, IMPACT0 + 44), loc=p1, scale=0.0)
        tidy(em, 'impact')
        ease_keys(em)
    # glowing feathers that drift down and sway
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.0)
        ft = leaf('im_feather_%d' % i, 0.5, 0.18, fl_y if i % 2 else fl_o, 0.03, 5)
        t0 = f + 8 + rnd.randint(0, 10)
        pa = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(2.6, 3.4))
        pb = (pa[0] + 0.3, pa[1] + 0.2, 1.7)
        pc = (pa[0] + 0.1, pa[1] - 0.1, 0.5)
        key(ft, IMPACT0, loc=pa, scale=0, rot=(0, 0, 0))
        key(ft, t0, loc=pa, scale=0.3, rot=(10, 80, 0))
        key(ft, t0 + 5, scale=1.0)
        key(ft, t0 + 14, loc=pb, scale=1.0, rot=(40, 120, 90))
        key(ft, min(t0 + 24, IMPACT0 + 40), loc=pc, scale=0.8, rot=(80, 200, 160))
        key(ft, IMPACT0 + 44, loc=pc, scale=0)
        tidy(ft, 'impact')
        ease_keys(ft)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 1.8)
        sp2 = star('im_spark_%d' % i, 0.18, 0.04, 4, 0.03, glint, loc=(cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.5, 2.0)), rot=(90, 0, 0))
        t0 = f + 6 + rnd.randint(0, 14)
        key(sp2, IMPACT0, scale=0)
        key(sp2, t0, scale=0)
        key(sp2, t0 + 4, scale=1.2)
        key(sp2, t0 + 12, scale=0)
        tidy(sp2, 'impact')
    return True
