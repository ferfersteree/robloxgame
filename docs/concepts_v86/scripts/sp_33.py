from spearlib import *

NAME = 'SP_33_lunar_crescent'
N = 33
BG = '#5d6f9e'        # moonlit glacier haze
GROUND = '#56668f'    # snow
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'moon_blade': 'im_crescent_0', 'moon_disc': 'im_moon', 'frost_crystal': 'im_frost_0', 'halo': 'im_halo',
             'fl_crescent': 'fl_cres_0'}


def mats():
    return dict(
        silver=toon('lcr_silver', '#e4eaf6', '#8e9ab8', '#ffffff', spec=1.0, rim=0.6, rimcol='#bfe8ff', emit=0.2),
        silver_dk=toon('lcr_silverdk', '#9aa8c8', '#56638a', '#d6e0f6', spec=0.9),
        navy=toon('lcr_navy', '#2c3a6e', '#161e44', '#6272b4', spec=0.8),
        moon=toon('lcr_moon', '#e8f2ff', '#a8bce0', '#ffffff', spec=1.0, emit=0.6, rimcol='#c8f0ff'),
        ice=toon('lcr_ice', '#bfeaff', '#6fb0d8', '#f0fcff', spec=1.0, emit=0.35),
        fur=toon('lcr_fur', '#f4f6fa', '#b8c0d4', '#ffffff', spec=0.2),
        gold=toon('lcr_gold', '#e8c46a', '#9a7428', '#fff0b0', spec=1.0),
        glow_m=glow('lcr_glow', '#bfe6ff', 2.6),
        hot=glow('lcr_hot', '#f4fcff', 3.6),
    )


def arc_xz(cz, R, a0, a1, n, cx=0.0, y=0.0):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + R * math.cos(a), y, cz + R * math.sin(a)))
    return pts


def taper(n, peak, power=0.7):
    return [peak * math.sin(math.pi * i / n) ** power if 0 < i < n else 0.0 for i in range(n + 1)]


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
    silver, silver_dk, navy, moon, ice, fur, gold, glow_m, hot = (M[k] for k in (
        'silver', 'silver_dk', 'navy', 'moon', 'ice', 'fur', 'gold', 'glow_m', 'hot'))
    # ---- tail: little crescent cap over a moonstone bead
    tube('tail_crescent', arc_xz(0.0, 0.4, 20, 160, 8), taper(8, 0.075), silver, 6)
    sphere('tail_bead', 0.17, moon, 10, 6, loc=(0, 0, 0.2), ol=0.015)
    rod('tail_stem', 0.1, 0.35, 0.95, silver, segs=8)
    torus('tail_ring', 0.19, 0.045, gold, 14, 6, loc=(0, 0, 0.95))
    # ---- shaft: midnight navy, silver rings, white fur wrap
    rod('shaft_lo', 0.155, 0.85, 3.3, navy, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.15, navy, r1=0.145)
    coil('fur_lo', 0.18, 0.04, 1.3, 1.9, 4, fur, segs=5)
    torus('fur_lo_cap', 0.18, 0.04, silver, 14, 6, loc=(0, 0, 1.93))
    coil('fur_hi', 0.178, 0.04, 3.12, 3.7, 4, fur, segs=5, phase=1.0)
    torus('fur_hi_cap', 0.178, 0.035, silver, 14, 6, loc=(0, 0, 3.1))
    for i, z in enumerate((4.2, 4.45, 4.7)):
        torus('moon_band_%d' % i, 0.152, 0.025, glow_m if i == 1 else silver_dk, 14, 5, loc=(0, 0, z), ol=0 if i == 1 else 0.015)
    for i in range(3):
        a = i * 2.1 + 0.3
        crystal('frost_stud_%d' % i, 0.05, 0.28, ice, 5, 0.4, 0.7, loc=(0.14 * math.cos(a), 0.14 * math.sin(a), 5.0 + 0.3 * i),
                rot=aim((math.cos(a), math.sin(a), 0.8)), ol=0.012)
    # ---- socket: silver cup with frost drips
    lathe('socket', [(5.95, 0.15), (6.1, 0.26), (6.35, 0.36), (6.65, 0.34), (6.85, 0.22), (6.9, 0.0)], silver, 14)
    torus('socket_ring_a', 0.3, 0.05, gold, 16, 6, loc=(0, 0, 6.2))
    torus('socket_ring_b', 0.3, 0.045, navy, 16, 6, loc=(0, 0, 6.75))
    for i in range(5):
        a = math.radians(i * 72 + 20)
        cone('socket_icicle_%d' % i, 0.05, 0.3 + 0.08 * (i % 2), ice, 5, loc=(0.34 * math.cos(a), 0.34 * math.sin(a), 6.3),
             rot=(180, 0, 0), ol=0.012)
    # ---- the crescent: big silver moon-bowl with a moonstone in the cradle and a spike above it
    cres = tube('crescent', arc_xz(8.2, 1.25, 160, 380, 12), taper(12, 0.3, 0.6), silver, 8)
    cres.scale = (1.0, 0.36, 1.0)
    inner = tube('crescent_inner', arc_xz(8.2, 1.25, 175, 365, 12), taper(12, 0.17, 0.6), glow_m, 6, ol=0)
    inner.scale = (1.0, 0.5, 1.0)
    for i in range(7):
        a = math.radians(170 + i * 33)
        ca, sa = math.cos(a), math.sin(a)
        crystal('rim_frost_%d' % i, 0.06, 0.34 + 0.1 * (i % 2), ice, 5, 0.4, 0.8, loc=(1.5 * ca, 0, 8.2 + 1.5 * sa),
                rot=aim((ca, 0, sa)), ol=0.012)
    for i, (a_deg, nm) in enumerate(((195, 'a'), (345, 'b'))):
        a = math.radians(a_deg)
        sphere('horn_stud_' + nm, 0.1, gold, 8, 5, loc=(1.25 * math.cos(a), 0.0, 8.2 + 1.25 * math.sin(a)), ol=0.015)
    for i, (x, z, r) in enumerate(((-0.95, 7.7, 0.08), (0.9, 7.8, 0.07), (-0.55, 7.25, 0.06))):
        sphere('crater_%d' % i, r, silver_dk, 7, 4, loc=(x, -0.14, z), scale=(1, 0.5, 1), ol=0.01)
    sphere('moonstone', 0.42, moon, 14, 8, loc=(0, 0, 7.65))
    torus('moon_collar', 0.3, 0.05, gold, 16, 6, loc=(0, 0, 8.0))
    spike = tube('spike', [(0, 0, 8.0), (0, 0, 8.6), (0, 0, 9.05), (0, 0, TIP)], [0.2, 0.2, 0.12, 0.0], silver, 8)
    spike.scale = (1.0, 0.55, 1.0)
    tube('spike_glow', [(0, -0.07, 8.15), (0, -0.07, 8.8), (0, -0.05, 9.2)], [0.0, 0.05, 0.0], glow_m, 4, ol=0)
    sphere('moon_glow', 0.2, hot, 8, 5, loc=(0, -0.3, 7.65), ol=0)
    for i in range(3):
        a = math.radians(i * 120 + 90)
        crystal('float_ice_%d' % i, 0.06, 0.4, ice, 5, 0.4, 0.7, both=True, loc=(0.4 * math.cos(a), 0.4 * math.sin(a), 8.95 + 0.0 * i + 0.2 * (i == 1)),
                rot=aim((math.cos(a) * 0.3, math.sin(a) * 0.3, 1)), ol=0.012)
    tube('charm_cord', [(0.15, 0.04, 5.9), (0.3, 0.08, 5.6), (0.36, 0.1, 5.3)], 0.02, fur, 5)
    star('charm_star', 0.15, 0.06, 5, 0.06, gold, loc=(0.36, 0.1, 5.15), rot=(90, 0, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(3333)
    aura = ghost('lcr_aura', '#bfe6ff', 1.2, 0.05, 1.8)
    puff = ghost('lcr_puff', '#f0f8ff', 1.2, 0.7, 1.2)
    glint = glow('lcr_glint', '#f4fcff', 3.2)
    ringm = glow('lcr_ring', '#bfe6ff', 2.4)
    moonm = glow('lcr_moonfx', '#e6f4ff', 2.0)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.0), scale=(1.6, 0.8, 1.4))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.2)
        sphere('idle_snow_%d' % i, rnd.uniform(0.04, 0.08), puff, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.4)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.3), -0.3, 7.6 + i * 0.5), rot=(90, 0, 0))
    # ---------------- flight: small crescents, snow puffs, glints, frost rings
    fx('flight')
    cs = [tube('fl_cres_%d' % i, arc_xz(0.0, 0.3, -70, 70, 6), taper(6, 0.05), M['silver'], 5, ol=0.01) for i in range(8)]
    cj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(cs, lambda t, i: (cj[i][0] * (0.3 + 1.0 * t), cj[i][1] * (0.3 + 1.0 * t), 8.6 - 12.5 * t),
           smax=1.2, spin=lambda t, i: (cj[i][2], 200 * t, 360 * t + cj[i][2]))
    pf = [sphere('fl_snow_%d' % i, 0.3, puff, 12, 7) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 7.6 - 11.5 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    st = [star('fl_glint_%d' % i, 0.15, 0.04, 4, 0.03, glint) for i in range(6)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(st, lambda t, i: (sj[i][0] * (0.3 + 1.2 * t), sj[i][1] * (0.3 + 1.2 * t), 8.4 - 12.0 * t), smax=1.3,
           spin=lambda t, i: (90, sj[i][2] + 300 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, ringm, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: ice crescents sweep out along the ground, a moon rises above, frost spreads
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('lcr_flash', '#eaf6ff', 2.0, 0.6, 1.3), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.7)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    fd = sphere('im_frostdisc', 1.2, ghost('lcr_frost', '#d8f0ff', 1.3, 0.5, 1.0), 16, 4, loc=(cx, 0, 0.03))
    key(fd, IMPACT0, scale=0, alpha=1)
    key(fd, f + 4, scale=(1.0, 1.0, 0.02), alpha=1)
    key(fd, f + 20, scale=(2.2, 2.2, 0.02), alpha=0.9)
    key(fd, IMPACT0 + 40, scale=(2.4, 2.4, 0.02), alpha=0)
    tidy(fd, 'impact')
    rg = torus('im_ring', 0.6, 0.05, ringm, 36, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 14, scale=5.0, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    # six ice crescents skid outward in a wide fan, spinning
    for k in range(6):
        a = math.radians(-75 + k * 30)
        L_ = 2.8 + 0.4 * (k % 2)
        pts = [(0.75 * math.cos(math.radians(q)), 0.75 * math.sin(math.radians(q)), 0.0) for q in range(-70, 71, 20)]
        cr = tube('im_crescent_%d' % k, pts, taper(len(pts) - 1, 0.2), M['ice'], 7, loc=(cx, 0, 0.14))
        t0 = f + (k % 3)
        end = (cx + L_ * math.cos(a), L_ * math.sin(a), 0.14)
        mid = (cx + 0.45 * L_ * math.cos(a), 0.45 * L_ * math.sin(a), 0.14)
        key(cr, IMPACT0, loc=(cx, 0, 0.14), scale=0, rot=(0, 0, 0))
        key(cr, t0, loc=(cx, 0, 0.14), scale=(0.4, 0.4, 0.2), rot=(0, 0, 0))
        key(cr, t0 + 6, loc=mid, scale=(1.1, 1.1, 0.5), rot=(0, 0, 360))
        key(cr, t0 + 22, loc=end, scale=(1.0, 1.0, 0.45), rot=(0, 0, 900))
        key(cr, t0 + 29, loc=end, scale=0, rot=(0, 0, 1050))
        tidy(cr, 'impact', interp='LINEAR')
        for j in range(2):
            fc = crystal('im_frost_%d' % (k * 2 + j), 0.07, 0.4 + 0.1 * j, M['ice'], 5, 0.4, 0.8,
                         loc=(cx + (0.5 + 0.5 * j) * L_ * 0.7 * math.cos(a), (0.5 + 0.5 * j) * L_ * 0.7 * math.sin(a), 0.0),
                         rot=aim((0.1, 0.1, 1)), ol=0.012)
            tt = t0 + 5 + 4 * j
            key(fc, IMPACT0, scale=0)
            key(fc, tt, scale=0)
            key(fc, tt + 3, scale=(1.0, 1.0, 1.2))
            key(fc, tt + 6, scale=1.0)
            key(fc, IMPACT0 + 34, scale=1.0)
            key(fc, IMPACT0 + 44, scale=0)
            tidy(fc, 'impact')
    # the moon rises above and in front of the spear
    mn = sphere('im_moon', 0.8, moonm, 16, 9, loc=(cx + 1.1, 0.0, 2.2))
    key(mn, IMPACT0, scale=0, alpha=1)
    key(mn, f + 4, loc=(cx + 1.1, 0.0, 2.2), scale=(0.3, 0.05, 0.3), alpha=1)
    key(mn, f + 14, loc=(cx + 1.1, 0.0, 3.2), scale=(1.0, 0.15, 1.0), alpha=1)
    key(mn, IMPACT0 + 34, loc=(cx + 1.1, 0.0, 3.6), scale=(1.05, 0.15, 1.05), alpha=0.8)
    key(mn, IMPACT0 + 44, loc=(cx + 1.1, 0.0, 3.8), scale=(1.1, 0.15, 1.1), alpha=0)
    tidy(mn, 'impact')
    ease_keys(mn)
    hl = torus('im_halo', 1.0, 0.04, ringm, 36, 5, loc=(cx + 1.1, 0.0, 2.2), axis='Y')
    key(hl, IMPACT0, scale=0, alpha=1)
    key(hl, f + 4, loc=(cx + 1.1, 0.0, 2.2), scale=0.3, alpha=1)
    key(hl, f + 16, loc=(cx + 1.1, 0.0, 3.2), scale=1.1, alpha=1)
    key(hl, IMPACT0 + 34, loc=(cx + 1.1, 0.0, 3.6), scale=1.4, alpha=0.6)
    key(hl, IMPACT0 + 44, loc=(cx + 1.1, 0.0, 3.8), scale=1.6, alpha=0)
    tidy(hl, 'impact')
    ease_keys(hl)
    for i in range(10):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.14)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.28, 0.44)))
        sh = crystal('im_shard_%d' % i, 0.07, rnd.uniform(0.28, 0.42), M['ice'], 5, 0.4, 0.6, both=True, ol=0.012)
        toss(sh, Vector((cx, 0, 0.2)), v, f + rnd.randint(0, 4), floor=0.12, spin=(40, 25, 10), hold=38)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.8)
        sm = sphere('im_snow_%d' % i, 0.35, puff, 12, 7)
        t0 = f + 3 + rnd.randint(0, 6)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.4, 2.6))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.4), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.8)
        sp2 = star('im_spark_%d' % i, 0.18, 0.04, 4, 0.03, glint, loc=(cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.4, 1.8)), rot=(90, 0, 0))
        t0 = f + 4 + rnd.randint(0, 14)
        key(sp2, IMPACT0, scale=0)
        key(sp2, t0, scale=0)
        key(sp2, t0 + 4, scale=1.2)
        key(sp2, t0 + 12, scale=0)
        tidy(sp2, 'impact')
    return True
