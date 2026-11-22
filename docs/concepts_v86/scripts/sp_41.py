from spearlib import *

NAME = 'SP_41_gear_pike'
N = 41
BG = '#6e5a48'        # clockwork workshop
GROUND = '#9a7650'
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'gear': 'im_gear_0', 'spring': 'im_spring_0', 'steam': 'im_steam_0', 'gear_mark': 'im_gearmark'}


def mats():
    return dict(
        copper=toon('gp_copper', '#d8743a', '#8a3a1c', '#ffb07a', spec=1.0, rim=0.5, rimcol='#ffd0a0'),
        brass=toon('gp_brass', '#f0c040', '#a8681c', '#fff0a0', spec=1.0),
        iron=toon('gp_iron', '#5a5260', '#2c2832', '#9a92a8', spec=0.8),
        cream=toon('gp_cream', '#f6ecd0', '#c4ae84', '#fffaf0', spec=0.4),
        leather=toon('gp_leather', '#7a3a24', '#40180e', '#b66a48'),
        teal=toon('gp_teal', '#2a9a9a', '#146066', '#6adcd0', emit=0.1),
        amber=glow('gp_amber', '#ffb030', 3.2),
        hot=glow('gp_hot', '#fff0b0', 3.6),
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


def gear(nm, R, n, th, mat, loc, rot=(90, 0, 0), ol=0.02):
    return star(nm, R, R * 0.82, n, th, mat, loc=loc, rot=rot, ol=ol)


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    copper, brass, iron, cream, leather, teal, amber, hot = (M[k] for k in ('copper', 'brass', 'iron', 'cream', 'leather', 'teal', 'amber', 'hot'))
    # ---- tail: spring counterweight with a gear
    coil('tail_spring', 0.2, 0.035, 0.12, 0.62, 3, iron, segs=5)
    gear('tail_gear', 0.36, 10, 0.1, brass, (0, 0, 0.72), rot=(90, 0, 0))
    cyl('tail_hub', 0.12, 0.2, copper, 10, 0.02, axis='Y', loc=(0, 0, 0.72))
    sphere('tail_bolt', 0.07, amber, 6, 4, loc=(0, -0.12, 0.72), ol=0)
    # ---- shaft: copper tube, leather wraps, brass caps, teal rivet rings
    shaft_parts(copper, leather, brass, teal)
    for i in range(3):
        a = i * 2.1
        sphere('rivet_%d' % i, 0.05, brass, 6, 4, loc=(0.15 * math.cos(a), 0.15 * math.sin(a), 5.15 + 0.3 * i), ol=0.01)
    # ---- socket: iron cup with a brass band
    lathe('socket', [(6.3, 0.14), (6.45, 0.22), (6.7, 0.3), (6.95, 0.26), (7.05, 0.14), (7.1, 0)], iron, 12)
    torus('socket_band', 0.3, 0.06, brass, 14, 5, loc=(0, 0, 6.55))
    torus('socket_band_b', 0.27, 0.04, amber, 14, 4, loc=(0, 0, 6.9), ol=0)
    # ---- pike head: copper spear point behind a stack of big gears and a clock face
    ol_ = [(0, 6.95), (0.28, 7.4), (0.32, 8.4), (0.0, TIP), (-0.32, 8.4), (-0.28, 7.4)]
    blade('pike', ol_, 0.13, copper)
    blade('pike_core', [(x * 0.45, 7.8 + (z - 6.95) * 0.58) for (x, z) in ol_], 0.16, amber, ol=0)
    gear('gear_big', 0.98, 12, 0.14, brass, (0.0, -0.22, 7.55))
    torus('gear_big_rim', 0.7, 0.05, copper, 22, 5, loc=(0, -0.3, 7.55), rot=(90, 0, 0))
    cyl('gear_big_hub', 0.2, 0.34, iron, 10, 0.03, axis='Y', loc=(0, -0.25, 7.55))
    gear('gear_mid', 0.62, 10, 0.12, copper, (0.62, 0.22, 8.45))
    cyl('gear_mid_hub', 0.14, 0.3, brass, 8, 0.02, axis='Y', loc=(0.62, 0.22, 8.45))
    gear('gear_small', 0.48, 9, 0.12, teal, (-0.58, 0.2, 7.0))
    cyl('gear_small_hub', 0.12, 0.28, brass, 8, 0.02, axis='Y', loc=(-0.58, 0.2, 7.0))
    # clock face with hands and amber hour marks
    cyl('clock_face', 0.5, 0.1, cream, 16, 0.02, axis='Y', loc=(0, -0.42, 7.55))
    torus('clock_rim', 0.5, 0.05, iron, 18, 4, loc=(0, -0.45, 7.55), rot=(90, 0, 0))
    for i in range(4):
        a = math.radians(i * 90)
        sphere('clock_tick_%d' % i, 0.05, amber, 6, 4, loc=(0.4 * math.sin(a), -0.5, 7.55 + 0.4 * math.cos(a)), ol=0)
    tube('clock_hand_a', [(0, -0.5, 7.55), (0.12, -0.52, 7.85)], [0.04, 0.02], iron, 4, ol=0)
    tube('clock_hand_b', [(0, -0.5, 7.55), (-0.2, -0.52, 7.45)], [0.04, 0.02], iron, 4, ol=0)
    # ---- floating cogs and a hovering spring
    for i, (x, y, z, R_, m) in enumerate(((1.2, -0.1, 9.0, 0.32, brass), (-1.15, 0.1, 8.3, 0.28, copper), (0.95, 0.3, 6.8, 0.24, teal))):
        gear('float_gear_%d' % i, R_, 8, 0.08, m, (x, y, z), rot=(90, 0, i * 30))
    coil('float_spring', 0.16, 0.03, 8.6, 9.1, 3, iron, segs=5, loc=(-0.95, 0.1, 0))
    for i in range(3):
        sphere('float_spark_%d' % i, 0.08, hot, 8, 5, loc=(1.05 * math.cos(i * 2.1 + 1), 0.9 * math.sin(i * 2.1 + 1), 7.5 + i * 0.5), ol=0)
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


def debris(ob, p0, v, f, rnd, spin=30, g=-0.03, r=0.08):
    key(ob, IMPACT0, loc=p0, scale=0)
    key(ob, f, loc=p0, scale=0.3)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= r or t > 34
        if done:
            p.z = r
        key(ob, f + t, loc=p, scale=1, rot=(t * spin, t * spin * 0.6, 0), interp='LINEAR')
        if done:
            break
    key(ob, max(f + t + 2, IMPACT0 + 36), scale=1)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def build_fx(M):
    rnd = random.Random(4141)
    steam = ghost('gp_steam', '#ffffff', 1.2, 0.85, 1.0)
    steam2 = ghost('gp_steam2', '#f3dcb8', 1.1, 0.85, 1.0)
    aura = ghost('gp_aura', '#ffc060', 1.2, 0.05, 1.8)
    hot = M['hot']
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 7.9), scale=(1.5, 1.0, 1.6))
    for i in range(3):
        sphere('idle_steam_%d' % i, rnd.uniform(0.09, 0.14), steam, 8, 5, loc=(rnd.uniform(-0.5, 0.5), 0.5, 8.2 + i * 0.4))
    for i in range(4):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, hot, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), -0.6, 7.0 + i * 0.7), rot=(90, 0, 0))
    for i in range(3):
        sphere('idle_spark_%d' % i, 0.05, M['amber'], 6, 4, loc=(rnd.uniform(-1, 1), rnd.uniform(-0.6, 0.6), rnd.uniform(7.0, 9.4)))
    # ---------------- flight
    fx('flight')
    gs = [star('fl_cog_%d' % i, 0.26, 0.21, 8, 0.07, (M['brass'], M['copper'], M['teal'])[i % 3], ol=0.012) for i in range(8)]
    gj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(gs, lambda t, i: (gj[i][0] * (0.35 + 1.0 * t), gj[i][1] * (0.35 + 1.0 * t), 8.6 - 12.5 * t), smax=1.2,
           spin=lambda t, i: (gj[i][2] + 200 * t, 90 + 60 * t, gj[i][2] + 540 * t))
    puffs = [sphere('fl_steam_%d' % i, 0.3, steam if i % 2 else steam2, 10, 6) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 8.0 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, M['amber'], 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (0, 0, 360 * t))
    sps = [sphere('fl_spark_%d' % i, 0.06, hot, 6, 4) for i in range(8)]
    kj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(sps, lambda t, i: (kj[i][0] * (0.3 + 1.6 * t), kj[i][1] * (0.3 + 1.6 * t), 8.4 - 12.0 * t), smax=1.3)
    # ---------------- impact: gears fly out spinning, springs bounce, steam puffs
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.6, ghost('gp_flash', '#ffe2a0', 2.0, 0.7, 1.2), 14, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 5, scale=2.2, alpha=0.7)
    key(flash, f + 12, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    gm = star('im_gearmark', 1.5, 1.2, 14, 0.04, M['amber'], loc=(cx, 0, 0.03), ol=0)
    key(gm, IMPACT0, scale=0, alpha=1, rot=(0, 0, 0))
    key(gm, f + 2, scale=0.4, alpha=1, rot=(0, 0, 0))
    key(gm, f + 12, scale=1.4, alpha=1, rot=(0, 0, 60))
    key(gm, IMPACT0 + 44, scale=1.6, alpha=0, rot=(0, 0, 130))
    tidy(gm, 'impact')
    for i in range(7):
        a = math.radians(i * 51 + rnd.uniform(-10, 10))
        sp = rnd.uniform(0.07, 0.15)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.3, 0.45)))
        g_ = star('im_gear_%d' % i, rnd.uniform(0.3, 0.5), 0.25, 9, 0.1, (M['brass'], M['copper'], M['teal'])[i % 3], ol=0.015)
        debris(g_, Vector((cx, 0, 0.3)), v, f, rnd, spin=45, r=0.12)
    for i in range(8):
        a = math.radians(rnd.uniform(0, 360))
        sp = rnd.uniform(0.06, 0.14)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.25, 0.4)))
        bt = sphere('im_bolt_%d' % i, 0.07, M['iron'], 6, 4, ol=0.01)
        debris(bt, Vector((cx, 0, 0.3)), v, f, rnd, spin=20, r=0.07)
    for i in range(3):
        a = math.radians(i * 120 + 40)
        sp_ = coil('im_spring_%d' % i, 0.17, 0.035, 0.0, 0.7, 3, M['iron'], segs=5, loc=(cx + 1.3 * math.cos(a), 1.3 * math.sin(a), 0.0))
        t0 = f + 2 + i * 2
        key(sp_, IMPACT0, scale=0)
        key(sp_, t0, scale=(1, 1, 0.1))
        for k, zs in enumerate((1.7, 0.6, 1.3, 0.8, 1.1, 1.0)):
            key(sp_, t0 + 3 + k * 4, scale=(1, 1, zs))
        key(sp_, IMPACT0 + 38, scale=(1, 1, 1.0))
        key(sp_, IMPACT0 + 44, scale=0)
        tidy(sp_, 'impact')
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.8)
        st = sphere('im_steam_%d' % i, 0.4, steam if i % 2 else steam2, 12, 7)
        fly(st, (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.8, 3.4)), f + rnd.randint(0, 8), rnd.uniform(1.4, 2.2))
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.8, 2.4)
        sp_ = sphere('im_spark_%d' % i, 0.07, hot, 6, 4, ol=0)
        fly(sp_, (cx, 0, 0.4), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.5, 2.4)), f + i % 5, 1.2)
    return True
