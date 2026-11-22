from spearlib import *

NAME = 'SP_28_golem_heart'
N = 28
BG = '#6f6070'        # basalt dust
GROUND = '#968470'    # packed ash and stone
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'golem_fist': 'im_fist_a', 'core_ring': 'im_pulse', 'stone_chip': 'im_chip_0', 'air_ring': 'fl_ring_0'}


def mats():
    return dict(
        stone=toon('glh_stone', '#8f8678', '#544c44', '#c8bfae', spec=0.3, rim=0.4, rimcol='#ffb070'),
        stone_dk=toon('glh_stonedk', '#5f574f', '#322d2a', '#948a7c', spec=0.3),
        stone_lt=toon('glh_stonelt', '#c4b8a2', '#8a7e6a', '#f2e8d4', spec=0.4),
        moss=toon('glh_moss', '#6f9a4a', '#3a5a2e', '#a8d070', spec=0.2),
        rope=toon('glh_rope', '#b58a52', '#6e4a2a', '#e0b87a', spec=0.2),
        gold=toon('glh_gold', '#e8b040', '#9a6220', '#ffe39a', spec=1.0),
        core=glow('glh_core', '#ff8a2a', 3.0),
        hot=glow('glh_hot', '#ffd25a', 3.6),
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
    stone, stone_dk, stone_lt, moss, rope, gold, core, hot = (M[k] for k in (
        'stone', 'stone_dk', 'stone_lt', 'moss', 'rope', 'gold', 'core', 'hot'))
    # ---- tail: stone fist-knuckle pommel with a glowing bead
    rock('pommel', 0.3, stone, seed=28, sub=1, rough=0.14, loc=(0, 0, 0.42), scale=(1, 1, 0.9))
    for i in range(4):
        a = math.radians(i * 90 + 45)
        rock('pommel_knuckle_%d' % i, 0.12, stone_dk, seed=i + 3, sub=0, rough=0.15, flat=True,
             loc=(0.24 * math.cos(a), 0.24 * math.sin(a), 0.55), ol=0.015)
    sphere('pommel_bead', 0.1, hot, 8, 5, loc=(0, 0, 0.1), ol=0)
    torus('pommel_ring', 0.2, 0.05, gold, 14, 6, loc=(0, 0, 0.98))
    # ---- shaft: stone-grey with moss and rope wraps, glowing rune bands
    rod('shaft_lo', 0.155, 0.8, 3.3, stone, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, stone, r1=0.145)
    coil('rope_lo', 0.176, 0.034, 1.3, 1.9, 4, rope, segs=5)
    torus('rope_lo_cap', 0.18, 0.04, gold, 14, 6, loc=(0, 0, 1.92))
    coil('rope_hi', 0.175, 0.034, 3.12, 3.7, 4, rope, segs=5, phase=0.9)
    torus('rope_hi_cap', 0.178, 0.035, gold, 14, 6, loc=(0, 0, 3.1))
    for i, z in enumerate((4.2, 4.5, 4.8)):
        torus('rune_band_%d' % i, 0.153, 0.025, core, 14, 5, loc=(0, 0, z), ol=0)
    for i, (z, a) in enumerate(((3.9, 0.6), (5.2, 2.8), (5.55, 4.7))):
        rock('moss_%d' % i, 0.1, moss, seed=i + 40, sub=0, rough=0.2, flat=True, loc=(0.15 * math.cos(a), 0.15 * math.sin(a), z), scale=(1, 1, 0.6), ol=0.012)
    # ---- socket: stone cup with gold rim
    lathe('socket', [(5.95, 0.15), (6.1, 0.28), (6.35, 0.4), (6.65, 0.42), (6.9, 0.34), (7.0, 0.0)], stone_dk, 14)
    torus('socket_rim', 0.4, 0.06, gold, 18, 6, loc=(0, 0, 6.7))
    torus('socket_glow', 0.35, 0.03, core, 18, 5, loc=(0, 0, 6.25), ol=0)
    for i in range(4):
        a = math.radians(i * 90)
        rock('socket_stud_%d' % i, 0.11, stone_lt, seed=i + 9, sub=0, rough=0.15, flat=True, loc=(0.4 * math.cos(a), 0.4 * math.sin(a), 6.4), ol=0.015)
    # ---- golem heart: glowing core in layered stone plates
    sphere('core', 0.38, core, 12, 7, loc=(0, 0, 7.75), ol=0)
    sphere('core_hot', 0.22, hot, 10, 6, loc=(0, 0, 7.75), ol=0)
    for k, (tilt, ang) in enumerate(((35, 10), (-35, 100))):
        torus('core_ring_%d' % k, 0.46, 0.03, hot, 16, 5, loc=(0, 0, 7.75), rot=(tilt, ang, 0), ol=0)
    for k in range(4):
        a = math.radians(45 + k * 90)
        ca, sa = math.cos(a), math.sin(a)
        box('plate_out_%d' % k, (0.2, 0.7, 1.6), stone, bev=0.04, bsegs=1, loc=(0.6 * ca, 0.6 * sa, 7.75), rot=(0, 14, math.degrees(a)))
        box('plate_rune_%d' % k, (0.05, 0.12, 0.6), core, bev=0.0, bsegs=1, loc=(0.72 * ca, 0.72 * sa, 7.75), rot=(0, 14, math.degrees(a)), ol=0)
    for k in range(4):
        a = math.radians(k * 90)
        ca, sa = math.cos(a), math.sin(a)
        box('plate_in_%d' % k, (0.15, 0.5, 1.15), stone_dk, bev=0.03, bsegs=1, loc=(0.4 * ca, 0.4 * sa, 7.55), rot=(0, 8, math.degrees(a)))
    for k in range(4):
        a = math.radians(45 + k * 90)
        cone('plate_spike_%d' % k, 0.09, 0.4, stone_lt, 5, loc=(0.62 * math.cos(a), 0.62 * math.sin(a), 8.5), rot=aim((math.cos(a) * 0.7, math.sin(a) * 0.7, 1)), ol=0.015)
    lathe('crown', [(8.3, 0.0), (8.3, 0.36), (8.55, 0.38), (8.75, 0.28), (9.05, 0.16), (TIP, 0.0)], stone_lt, 10)
    torus('crown_ring', 0.36, 0.05, gold, 14, 6, loc=(0, 0, 8.45))
    sphere('crown_gem', 0.09, hot, 8, 5, loc=(0, -0.3, 8.7), ol=0)
    for i in range(3):
        a = math.radians(i * 120 + 50)
        rock('float_rock_%d' % i, 0.13, stone_lt, seed=i + 60, sub=0, rough=0.2, flat=True,
             loc=(0.95 * math.cos(a), 0.95 * math.sin(a), 7.2 + 0.5 * i), ol=0.015)
        sphere('float_spark_%d' % i, 0.05, hot, 6, 4, loc=(0.95 * math.cos(a), 0.95 * math.sin(a), 7.2 + 0.5 * i + 0.2), ol=0)
    # charm: stone fist amulet
    tube('charm_cord', [(0.15, 0.04, 6.4), (0.32, 0.08, 6.1), (0.38, 0.1, 5.8)], 0.022, rope, 5)
    rock('charm_stone', 0.1, stone_lt, seed=77, sub=0, rough=0.2, flat=True, loc=(0.38, 0.1, 5.7), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2828)
    dust = ghost('glh_dust', '#d8c8a8', 1.1, 0.8, 1.1)
    aura = ghost('glh_aura', '#ff9a3a', 1.2, 0.05, 1.8)
    spark = glow('glh_spark', '#ffc24a', 3.2)
    ring_m = glow('glh_ring', '#ff8a2a', 2.6)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 7.75), scale=(1.3, 1.3, 1.6))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.0)
        sphere('idle_spark_%d' % i, rnd.uniform(0.04, 0.07), spark, 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.0)))
    for i in range(3):
        rock('idle_pebble_%d' % i, 0.07, M['stone_lt'], seed=i, sub=1, rough=0.2, flat=True, loc=(0.7 * math.cos(i * 2.1), 0.7 * math.sin(i * 2.1), 8.2 + i * 0.35), ol=0.012)
    # ---------------- flight: stone chips, sparks, dust puffs, core pulse rings
    fx('flight')
    chips = [rock('fl_chip_%d' % i, 0.1, M['stone'] if i % 2 else M['stone_dk'], seed=i, sub=1, rough=0.22, flat=True) for i in range(8)]
    cj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(chips, lambda t, i: (cj[i][0] * (0.3 + 0.9 * t), cj[i][1] * (0.3 + 0.9 * t), 8.4 - 13.0 * t),
           smax=1.0, spin=lambda t, i: (cj[i][2] + 720 * t, 540 * t, 0))
    sps = [sphere('fl_spark_%d' % i, 0.06, spark, 6, 4) for i in range(10)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(sps, lambda t, i: (sj[i][0] * (0.3 + 1.4 * t), sj[i][1] * (0.3 + 1.4 * t), 8.0 - 12.5 * t), smax=1.2)
    puffs = [sphere('fl_dust_%d' % i, 0.34, dust, 12, 7) for i in range(7)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(7)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.3 + 0.9 * t), pj[i][1] * (0.3 + 0.9 * t), 6.0 - 10.0 * t),
           smax=lambda t, i: (0.6 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.055, ring_m, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.0 - 6.5 * t), smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: two stone fists rise and slam together in front of the spear
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    mx = cx + 1.4                                   # where the fists meet
    flash = sphere('im_flash', 0.5, ghost('glh_flash', '#ffd08a', 2.0, 0.65, 1.2), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=1.8, alpha=0.7)
    key(flash, f + 10, scale=2.4, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    for s, nm in ((-1, 'a'), (1, 'b')):
        # (name, builder, offset relative to the fist centre)
        pieces = []
        pieces.append((rock('im_fist_' + nm, 0.58, M['stone'], seed=11 + s, sub=2, rough=0.12, scale=(1.0, 1.0, 0.9)), (0, 0, 0)))
        for j, (ox, oz) in enumerate(((-0.28, 0.22), (0.0, 0.3), (0.28, 0.22))):
            pieces.append((rock('im_knuck_%s%d' % (nm, j), 0.19, M['stone_lt'], seed=20 + j, sub=1, rough=0.15, flat=True, ol=0.015),
                           (ox, -s * 0.5, oz)))
        pieces.append((tube('im_arm_' + nm, [(0, 0, 0), (0, 0, 0.8), (0, 0, 1.5)], [0.36, 0.34, 0.36], M['stone_dk'], 8), (0, s * 0.1, -1.5)))
        pieces.append((sphere('im_palm_' + nm, 0.2, M['hot'] if False else glow('glh_palm', '#ffb03a', 3.0), 8, 5), (0, s * 0.5, 0.0)))
        for ob, off in pieces:
            def P(y, z, off=off):
                return (mx + off[0], y + off[1], z + off[2])
            key(ob, IMPACT0, loc=P(s * 2.0, -0.7), scale=0)
            key(ob, f + 1, loc=P(s * 2.0, -0.7), scale=0.2)
            key(ob, f + 7, loc=P(s * 2.0, 0.95), scale=1.0)
            key(ob, f + 12, loc=P(s * 2.0, 1.15), scale=1.0)
            key(ob, f + 16, loc=P(s * 0.62, 1.1), scale=1.1)
            key(ob, f + 19, loc=P(s * 0.7, 1.1), scale=1.0)
            key(ob, IMPACT0 + 34, loc=P(s * 0.7, 1.1), scale=1.0)
            key(ob, IMPACT0 + 43, loc=P(s * 0.7, -0.6), scale=0.8)
            key(ob, IMPACT0 + 44, loc=P(s * 0.7, -0.7), scale=0)
            tidy(ob, 'impact')
            ease_keys(ob)
    # slam: shock ring on the ground + core pulse ring at the spear + sparks
    f2 = f + 16
    sh = torus('im_shock', 0.5, 0.07, ring_m, 36, 5, loc=(mx, 0, 0.05))
    key(sh, IMPACT0, scale=0, alpha=1)
    key(sh, f2 - 1, scale=0, alpha=1)
    key(sh, f2, scale=0.3, alpha=1)
    key(sh, f2 + 14, scale=5.0, alpha=0)
    tidy(sh, 'impact', interp='LINEAR')
    ease_keys(sh)
    for k in range(2):
        pr = torus('im_pulse' if k == 0 else 'im_pulse_%d' % k, 0.5, 0.05, M['hot'], 32, 5, loc=(cx, 0, 0.08))
        key(pr, IMPACT0, scale=0, alpha=1)
        key(pr, f + k * 8, scale=0.3, alpha=1)
        key(pr, f + k * 8 + 14, scale=4.0 - k, alpha=0)
        tidy(pr, 'impact', interp='LINEAR')
        ease_keys(pr)
    for i in range(12):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.1, 0.2)))
        sk = sphere('im_spark_%d' % i, rnd.uniform(0.05, 0.09), spark, 6, 4)
        toss(sk, Vector((mx, 0, 1.1)), v, f2 + rnd.randint(0, 2), floor=0.1, spin=(0, 0, 0), hold=34)
    for i in range(8):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.1, 0.2)))
        ch = rock('im_chip_%d' % i, rnd.uniform(0.1, 0.18), M['stone'] if i % 2 else M['stone_dk'], seed=i + 90, sub=1, rough=0.25, flat=True, ol=0.015)
        toss(ch, Vector((mx, 0, 1.0)), v, f2 + rnd.randint(0, 2), floor=0.1, spin=(30, 20, 0), hold=36)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.0)
        sm = sphere('im_dust_%d' % i, 0.4, dust, 12, 7)
        t0 = f + 1 + (i % 2) * 14
        p0 = (mx + 0.3 * math.cos(a), (-1 if i % 2 else 1) * 1.0 + 0.3 * math.sin(a), 0.3)
        p1 = (mx + r * math.cos(a), p0[1] + r * math.sin(a), rnd.uniform(1.4, 2.6))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.4), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    return True
