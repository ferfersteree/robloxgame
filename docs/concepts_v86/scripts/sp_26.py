from spearlib import *

NAME = 'SP_26_leviathan_fang'
N = 26
BG = '#6fa6c4'        # cold abyss shallows
GROUND = '#a9c4d2'    # frozen silt
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'ice_fang': 'im_fang', 'frost_ring': 'im_frost', 'ice_shard': 'im_shard_0', 'frost_glow': 'im_glowring',
             'air_ring': 'fl_ring_0'}


def mats():
    return dict(
        ice=toon('lfg_ice', '#cdf1ff', '#7fb4d4', '#f4fdff', spec=1.0, rim=0.6, rimcol='#8fe8ff', emit=0.25),
        ice_dk=toon('lfg_icedk', '#5fa9d8', '#2b5f9a', '#a8dcf8', spec=0.9, emit=0.2),
        iron=toon('lfg_iron', '#59657a', '#2a3142', '#98a8c0', spec=0.9, rimcol='#8fe8ff'),
        dark=toon('lfg_dark', '#2f394c', '#161c28', '#58688a'),
        hide=toon('lfg_hide', '#7a5a4a', '#46302a', '#b08a74', spec=0.2),
        brass=toon('lfg_brass', '#d9a53a', '#8c5a1c', '#ffe59a', spec=1.0),
        barn=toon('lfg_barn', '#ece6d0', '#b3a98a', '#ffffff', spec=0.3),
        core=glow('lfg_core', '#6ff0ff', 3.0),
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
    key(ob, f, loc=p0, scale=0.3 * s)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= floor or t > 34
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
    ice, ice_dk, iron, dark, hide, brass, barn, core = (M[k] for k in (
        'ice', 'ice_dk', 'iron', 'dark', 'hide', 'brass', 'barn', 'core'))
    # ---- tail: iron cap with three small ice teeth and a glowing orb
    lathe('tail_cap', [(0.0, 0.0), (0.04, 0.14), (0.2, 0.26), (0.5, 0.26), (0.7, 0.18), (0.78, 0.0)], iron, 14)
    sphere('tail_orb', 0.13, core, 8, 5, loc=(0, 0, 0.9), ol=0)
    for i in range(3):
        a = math.radians(i * 120 + 20)
        cone('tail_tooth_%d' % i, 0.07, 0.26, ice, 6, loc=(0.2 * math.cos(a), 0.2 * math.sin(a), 0.3),
             rot=aim((math.cos(a) * 0.5, math.sin(a) * 0.5, -1)), ol=0.015)
    torus('tail_ring', 0.2, 0.05, brass, 14, 6, loc=(0, 0, 0.78))
    # ---- shaft: dark iron, hide wraps, ice vertebra discs
    rod('shaft_lo', 0.155, 0.75, 3.3, dark, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.15, dark, r1=0.145)
    coil('hide_lo', 0.176, 0.034, 1.3, 1.9, 4, hide, segs=5)
    torus('hide_lo_cap', 0.18, 0.04, brass, 14, 6, loc=(0, 0, 1.92))
    coil('hide_hi', 0.175, 0.034, 3.12, 3.7, 4, hide, segs=5, phase=1.2)
    torus('hide_hi_cap', 0.178, 0.035, brass, 14, 6, loc=(0, 0, 3.1))
    for i in range(3):
        z = 4.2 + i * 0.5
        lathe('vert_%d' % i, [(z - 0.1, 0.15), (z - 0.08, 0.24), (z, 0.27), (z + 0.08, 0.24), (z + 0.1, 0.15)], ice_dk, 12, caps=False)
        for s in (-1, 1):
            cone('vert_spur_%d%s' % (i, 'ab'[s > 0]), 0.055, 0.2, ice, 5, loc=(s * 0.24, 0, z), rot=aim((s, 0, 0.6)), ol=0.012)
    for i, (z, a) in enumerate(((3.85, 0.8), (5.5, 2.9), (5.75, 4.8))):
        sphere('barn_%d' % i, 0.07, barn, 7, 4, loc=(0.145 * math.cos(a), 0.145 * math.sin(a), z), scale=(1, 1, 0.8), ol=0.012)
    # ---- reinforced iron socket: cup + six gripping claws + glowing seam
    lathe('socket', [(5.95, 0.15), (6.1, 0.3), (6.35, 0.46), (6.65, 0.5), (6.85, 0.42), (6.9, 0.0)], iron, 16)
    torus('socket_rim', 0.46, 0.065, brass, 20, 6, loc=(0, 0, 6.7))
    torus('socket_seam', 0.4, 0.03, core, 20, 5, loc=(0, 0, 6.22), ol=0)
    for i in range(6):
        a = math.radians(i * 60 + 10)
        ca, sa = math.cos(a), math.sin(a)
        cone('claw_%d' % i, 0.09, 0.55, iron, 6, loc=(0.46 * ca, 0.3 * sa, 6.7), rot=aim((ca * 0.3, sa * 0.2, 1)), ol=0.015)
    # ---- the leviathan fang: huge curved ice tooth, iron straps, glowing cracks
    fp = [(0.0, 0, 6.75), (0.08, 0, 7.35), (0.2, 0, 8.0), (0.18, 0, 8.65), (0.0, 0, 9.1), (-0.3, 0, TIP)]
    fr = [0.5, 0.54, 0.46, 0.34, 0.19, 0.0]
    fang = tube('fang', fp, fr, ice, 12)
    fang.scale = (1.0, 0.62, 1.0)
    for z, x, R in ((7.35, 0.08, 0.56), (8.0, 0.2, 0.47)):
        torus('strap_%d' % int(z * 10), R, 0.05, iron, 16, 6, loc=(x, 0, z), scale=(1.0, 0.68, 1.0))
    for s in (-1, 1):
        nm = 'a' if s < 0 else 'b'
        tube('frame_arch_' + nm, [(s * 0.45, 0, 6.75), (s * 0.72, 0, 7.3), (s * 0.66, 0, 8.0), (s * 0.38, 0, 8.6)], [0.07, 0.07, 0.06, 0.04], iron, 6)
        sphere('frame_rivet_' + nm, 0.075, brass, 7, 4, loc=(s * 0.66, 0, 7.95), ol=0.012)
        # smaller flanking fangs
        tube('fang_small_' + nm, [(s * 0.5, 0, 6.6), (s * 0.95, 0, 6.95), (s * 1.12, 0, 7.5), (s * 1.0, 0, 8.05)],
             [0.2, 0.17, 0.11, 0.0], ice_dk, 8)
        torus('fang_small_band_' + nm, 0.17, 0.04, iron, 12, 5, loc=(s * 0.78, 0, 6.8), rot=(0, s * 55, 0), ol=0.015)
    rnd = random.Random(2626)
    for s in (-1, 1):
        pts = []
        for i in range(4):
            z = 7.2 + i * 0.32 + (0.3 if s > 0 else 0)
            t = (z - 6.75) / (TIP - 6.75)
            pts.append((0.1 + rnd.uniform(-0.1, 0.1) - 0.2 * t, s * (0.5 * (1 - t ** 1.5) * 0.62 + 0.02), z))
        tube('crack_%s' % ('ab'[s > 0]), pts, [0.0, 0.055, 0.05, 0.0], core, 4, smooth=False, ol=0)
    tube('tip_glow', [(0.1, 0, 8.7), (0.0, 0, 9.0), (-0.28, 0, 9.36)], [0.1, 0.07, 0.0], core, 6, scale=(1.05, 0.68, 1.0), ol=0)
    # floating frost shards
    for i in range(2):
        a = math.radians(i * 180 + 60)
        crystal('float_shard_%d' % i, 0.08, 0.45, ice, 5, 0.35, 0.6, both=True, loc=(0.85 * math.cos(a), 0.55 * math.sin(a) + 0.1, 8.2 + 0.3 * i),
                rot=aim((math.cos(a) * 0.3, 0, 1)), ol=0.015)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2626 + 1)
    frost = ghost('lfg_frost', '#d8f6ff', 1.4, 0.8, 1.2)
    aura = ghost('lfg_aura', '#7fe8ff', 1.2, 0.05, 1.8)
    ring_m = glow('lfg_ring', '#8ff2ff', 2.6)
    glint = glow('lfg_glint', '#e6fcff', 2.8)
    # ---------------- idle: frost aura, snow motes, glints
    fx('idle')
    sphere('idle_aura', 0.7, aura, 14, 8, loc=(0.0, 0, 8.0), scale=(1.5, 0.9, 1.7))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.1)
        sphere('idle_snow_%d' % i, rnd.uniform(0.05, 0.09), frost, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.4)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.9), -0.4, 7.4 + i * 0.6), rot=(90, 0, 0))
    # ---------------- flight: ice shards, frost puffs, frost rings, snow glints
    fx('flight')
    shards = [crystal('fl_shard_%d' % i, 0.08, 0.4, M['ice'], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(10)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(shards, lambda t, i: (sj[i][0] * (0.3 + 1.0 * t), sj[i][1] * (0.3 + 1.0 * t), 8.8 - 12.5 * t),
           smax=1.1, spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    puffs = [sphere('fl_frost_%d' % i, 0.32, frost, 12, 7) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 7.6 - 11.5 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.55, 0.055, ring_m, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    sn = [star('fl_snow_%d' % i, 0.14, 0.04, 6, 0.03, glint) for i in range(6)]
    nj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(sn, lambda t, i: (nj[i][0] * (0.3 + 1.2 * t), nj[i][1] * (0.3 + 1.2 * t), 8.4 - 12.0 * t), smax=1.2,
           spin=lambda t, i: (90, nj[i][2] + 300 * t, 0))
    # ---------------- impact: a giant ice fang rises behind the spear, frozen ring, ice shards
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.7)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('lfg_flash', '#dcfbff', 1.8, 0.6, 1.3), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.7)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    # the giant fang stands on the far (+Y) side so the spear stays readable
    big = tube('im_fang', [(0, 0, 0), (0.1, 0, 1.2), (0.05, 0, 2.4), (-0.4, 0, 3.4)], [0.7, 0.58, 0.34, 0.0], M['ice'], 10,
               loc=(cx + 0.9, 1.5, -0.1), rot=(0, 0, 0))
    key(big, IMPACT0, scale=0)
    key(big, f + 2, scale=(0.5, 0.7, 0.05))
    key(big, f + 9, scale=(1.05, 0.72, 1.12))
    key(big, f + 14, scale=(1.0, 0.7, 1.0))
    key(big, IMPACT0 + 32, scale=(1.0, 0.7, 1.0))
    key(big, IMPACT0 + 43, scale=(0.9, 0.65, 0.05))
    key(big, IMPACT0 + 44, scale=0)
    tidy(big, 'impact')
    ease_keys(big)
    for k, (x, y, h, ph) in enumerate(((1.7, 0.9, 1.7, 6), (0.2, 1.9, 1.5, 8), (1.9, 2.0, 1.3, 10))):
        sm = tube('im_fang_s%d' % k, [(0, 0, 0), (0.06, 0, h * 0.5), (-0.2, 0, h)], [0.3, 0.22, 0.0], M['ice_dk'], 8,
                  loc=(cx + x, y, -0.05))
        key(sm, IMPACT0, scale=0)
        key(sm, f + ph - 4, scale=0)
        key(sm, f + ph + 3, scale=(1.1, 0.8, 1.15))
        key(sm, f + ph + 6, scale=(1.0, 0.8, 1.0))
        key(sm, IMPACT0 + 32, scale=(1.0, 0.8, 1.0))
        key(sm, IMPACT0 + 44, scale=0)
        tidy(sm, 'impact')
    fz = torus('im_frost', 0.9, 0.12, M['ice'], 32, 6, loc=(cx, 0, 0.04))
    key(fz, IMPACT0, scale=0)
    key(fz, f, scale=0)
    key(fz, f + 8, scale=(1.5, 1.5, 0.5))
    key(fz, IMPACT0 + 38, scale=(1.7, 1.7, 0.4))
    key(fz, IMPACT0 + 44, scale=0)
    tidy(fz, 'impact')
    gr = torus('im_glowring', 0.6, 0.06, ring_m, 36, 5, loc=(cx, 0, 0.06))
    key(gr, IMPACT0, scale=0, alpha=1)
    key(gr, f, scale=0.3, alpha=1)
    key(gr, f + 14, scale=4.0, alpha=0.0)
    tidy(gr, 'impact', interp='LINEAR')
    ease_keys(gr)
    for i in range(5):
        a = math.radians(i * 72 + 20)
        L_ = rnd.uniform(1.4, 2.2)
        cr = tube('im_icecrack_%d' % i, [(cx + 0.5 * math.cos(a), 0.5 * math.sin(a), 0.02),
                                           (cx + (0.5 + L_ * 0.5) * math.cos(a + 0.12), (0.5 + L_ * 0.5) * math.sin(a + 0.12), 0.02),
                                           (cx + (0.5 + L_) * math.cos(a), (0.5 + L_) * math.sin(a), 0.02)], [0.06, 0.045, 0.0], ring_m, 4, ol=0)
        cr.scale = (1, 1, 0.3)
        key(cr, IMPACT0, scale=0, alpha=1)
        key(cr, f, scale=0, alpha=1)
        key(cr, f + 5, scale=(1, 1, 0.3), alpha=1)
        key(cr, IMPACT0 + 34, scale=(1, 1, 0.3), alpha=1)
        key(cr, IMPACT0 + 44, scale=(1, 1, 0.3), alpha=0)
        tidy(cr, 'impact')
    for i in range(14):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.06, 0.16)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.28, 0.45)))
        sh = crystal('im_shard_%d' % i, 0.08, rnd.uniform(0.28, 0.45), M['ice'] if i % 3 else M['ice_dk'], 5, 0.4, 0.6, both=True, ol=0.012)
        toss(sh, Vector((cx, 0, 0.2)), v, f + rnd.randint(0, 4), floor=0.12, spin=(40, 25, 10), hold=38)
    for i in range(6):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.06, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.2, 0.32)))
        rk = rock('im_chunk_%d' % i, rnd.uniform(0.1, 0.17), M['ice_dk'], seed=i + 26, sub=1, rough=0.25, flat=True, ol=0.015)
        toss(rk, Vector((cx, 0, 0.15)), v, f, floor=0.08, spin=(25, 18, 0), hold=38)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.8)
        sm = sphere('im_snow_%d' % i, 0.35, frost, 12, 7)
        t0 = f + 3 + rnd.randint(0, 6)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.6, 2.8))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.4), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.6)
        sp2 = star('im_spark_%d' % i, 0.18, 0.04, 4, 0.03, glint, loc=(cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.3, 1.3)), rot=(90, 0, 0))
        t0 = f + 4 + rnd.randint(0, 10)
        key(sp2, IMPACT0, scale=0)
        key(sp2, t0, scale=0)
        key(sp2, t0 + 4, scale=1.2)
        key(sp2, t0 + 12, scale=0)
        tidy(sp2, 'impact')
    return True
