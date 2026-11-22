from spearlib import *

NAME = 'SP_43_bone_glaive'
N = 43
BG = '#7d6a5a'        # bone fields
GROUND = '#9c8a70'
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'rib': 'im_rib_0', 'vertebra': 'im_vert_0', 'dust': 'im_dust_0', 'bone_ring': 'im_ring'}


def mats():
    return dict(
        ivory=toon('bg_ivory', '#f4ead0', '#c4a880', '#fffaf0', spec=0.7, rim=0.5, rimcol='#ffc880'),
        bone=toon('bg_bone', '#d8c4a0', '#98785a', '#f2e4c8', spec=0.5),
        stone=toon('bg_stone', '#8a7a6a', '#524438', '#bca88e', spec=0.3),
        rust=toon('bg_rust', '#b8402e', '#6c1c18', '#e8785a'),
        gold=toon('bg_gold', '#e8b440', '#a0641c', '#fff0a0', spec=1.0),
        dark=toon('bg_dark', '#3a2e34', '#1a1218', '#6e5a64', spec=0.6),
        amber=glow('bg_amber', '#ffa028', 3.2),
        hot=glow('bg_hot', '#ffe090', 3.6),
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


def vert(nm, z, r, mat, **kw):
    return lathe(nm, [(z - 0.12, 0.15), (z - 0.1, r * 0.85), (z, r), (z + 0.1, r * 0.85), (z + 0.12, 0.15)], mat, 10, caps=False, **kw)


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    ivory, bone, stone, rust, gold, dark, amber, hot = (M[k] for k in ('ivory', 'bone', 'stone', 'rust', 'gold', 'dark', 'amber', 'hot'))
    # ---- tail: knuckle-bone pommel with a claw
    sphere('tail_knuckle', 0.3, ivory, 12, 7, loc=(0, 0, 0.36), scale=(1, 1, 0.9))
    sphere('tail_knob_a', 0.17, bone, 8, 5, loc=(0.24, 0, 0.18))
    sphere('tail_knob_b', 0.17, bone, 8, 5, loc=(-0.24, 0, 0.18))
    cone('tail_claw', 0.1, 0.3, ivory, 6, loc=(0, 0, 0.3), rot=(180, 0, 0), ol=0.015)
    torus('tail_ring', 0.2, 0.045, gold, 12, 5, loc=(0, 0, 0.68))
    # ---- shaft: bone shaft with rust cloth, fossil rings and vertebra pieces
    shaft_parts(bone, rust, gold, stone)
    for i in range(3):
        z = 4.2 + i * 0.6
        vert('vert_%d' % i, z, 0.27, ivory if i % 2 == 0 else bone)
        for s in (-1, 1):
            cone('vert_spur_%d%s' % (i, 'ab'[s > 0]), 0.06, 0.24, dark, 5, loc=(s * 0.25, 0, z), rot=aim((s, 0, 0.5)), ol=0.015)
    # ---- socket: pelvis-like bone cup with a glowing fossil eye
    lathe('socket', [(6.3, 0.14), (6.45, 0.23), (6.7, 0.34), (6.95, 0.3), (7.0, 0)], ivory, 12)
    torus('socket_ring', 0.33, 0.055, gold, 14, 5, loc=(0, 0, 6.55))
    sphere('socket_eye', 0.1, amber, 8, 5, loc=(0, -0.3, 6.75), ol=0)
    for i in range(5):
        a = math.radians(i * 72 + 18)
        cone('socket_tooth_%d' % i, 0.07, 0.26 if i % 2 else 0.2, ivory, 6, loc=(0.3 * math.cos(a), 0.3 * math.sin(a), 6.85),
             rot=aim((math.cos(a) * 0.4, math.sin(a) * 0.4, 1)), ol=0.015)
    # ---- the crescent: flat bone blade + thick rib along the outer edge + inner amber vein
    z0, z1 = 6.85, TIP
    outer, inner = [], []
    for i in range(1, 9):
        t = i / 9.0
        z = z0 + (z1 - z0) * t
        outer.append((1.05 * math.sin(math.pi * t ** 0.9) ** 0.9, z))
        inner.append((0.22 * math.sin(math.pi * t), z))
    cres = [(0.0, z0)] + outer + [(0.0, z1)] + inner[::-1]
    blade('crescent', cres, 0.12, ivory)
    blade('crescent_vein', [(x * 0.62, z) for (x, z) in cres[:1] + outer + [(0.0, z1 - 0.15)] + inner[::-1]], 0.15, amber, ol=0, edge=0.5)
    rib_pts = [(x * 0.99 + 0.02, 0, z) for (x, z) in [(0.0, z0)] + outer + [(0.02, z1)]]
    tube('rib_outer', rib_pts, [0.1, 0.14, 0.17, 0.18, 0.17, 0.16, 0.14, 0.11, 0.07, 0.0], bone, 8)
    for i in range(4):
        x, z = outer[i * 2][0], outer[i * 2][1]
        sphere('rib_knob_%d' % i, 0.11, ivory, 7, 4, loc=(x + 0.03, 0.0, z), ol=0.012)
    # left claw-rib (short counter curve)
    tube('claw_rib', [(-0.1, 0, 7.2), (-0.55, 0, 7.5), (-0.85, 0, 8.0), (-0.8, 0, 8.6)], [0.13, 0.12, 0.09, 0.0], ivory, 8)
    torus('blade_band_a', 0.22, 0.06, gold, 12, 5, loc=(0, 0, 7.0))
    # ---- floating: loose rib arcs and a vertebra, fossil embers
    for i, (x, z, rt) in enumerate(((-1.05, 9.0, 20), (1.35, 8.4, -30))):
        pts = [(0.45 * math.cos(math.radians(a)), 0, 0.45 * math.sin(math.radians(a))) for a in range(-30, 211, 30)]
        tube('float_rib_%d' % i, pts, [0.0, 0.05, 0.08, 0.09, 0.09, 0.08, 0.06, 0.05, 0.0][:len(pts)], ivory, 6, loc=(x, 0.2, z), rot=(0, rt, 0), ol=0.015)
    vert('float_vert', 0.0, 0.2, bone, loc=(-1.2, 0.3, 8.0), rot=(30, 0, 40), ol=0.015)
    for i in range(3):
        sphere('float_ember_%d' % i, 0.07, hot, 8, 5, loc=(1.3 * math.cos(i * 2.2), 0.5 * math.sin(i * 2.2), 7.4 + i * 0.7), ol=0)
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


def debris(ob, p0, v, f, spin=30, g=-0.03, r=0.08):
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
    rnd = random.Random(4343)
    dust = ghost('bg_dust', '#f2e8cc', 1.1, 0.85, 1.1)
    dust2 = ghost('bg_dust2', '#cdb890', 1.0, 0.85, 1.1)
    aura = ghost('bg_aura', '#ffd890', 1.2, 0.05, 1.8)
    hot = M['hot']
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0.2, 0, 8.0), scale=(1.4, 0.9, 1.7))
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.3)
        sphere('idle_dust_%d' % i, rnd.uniform(0.05, 0.09), dust if i % 2 else dust2, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.5)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, hot, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), -0.4, 7.2 + i * 0.8), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    bs = [crystal('fl_splinter_%d' % i, 0.06, 0.55, (M['ivory'], M['bone'])[i % 2], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(10)]
    bj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(bs, lambda t, i: (bj[i][0] * (0.35 + 1.0 * t), bj[i][1] * (0.35 + 1.0 * t), 8.6 - 12.5 * t), smax=1.1,
           spin=lambda t, i: (bj[i][2] + 500 * t, 300 * t, 0))
    puffs = [sphere('fl_dust_%d' % i, 0.3, dust if i % 2 else dust2, 10, 6) for i in range(9)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(9)]
    stream(puffs, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 8.0 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    vs = [vert('fl_vert_%d' % i, 0.0, 0.2, M['bone'], ol=0.012) for i in range(4)]
    vj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(4)]
    stream(vs, lambda t, i: (vj[i][0] * (0.5 + 1.0 * t), vj[i][1] * (0.5 + 1.0 * t), 8.4 - 12.0 * t), smax=1.0,
           spin=lambda t, i: (vj[i][2] + 400 * t, 200 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, M['amber'], 26, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 6.5 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    sps = [sphere('fl_ember_%d' % i, 0.06, hot, 6, 4) for i in range(6)]
    kj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(sps, lambda t, i: (kj[i][0] * (0.3 + 1.5 * t), kj[i][1] * (0.3 + 1.5 * t), 8.4 - 12.0 * t), smax=1.3)
    # ---------------- impact: ribs erupt in a ring and arch inward like a ribcage, bone dust
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.6, ghost('bg_flash', '#fff0c8', 2.0, 0.7, 1.2), 14, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 5, scale=2.2, alpha=0.7)
    key(flash, f + 12, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    rg = torus('im_ring', 0.9, 0.09, M['ivory'], 32, 6, loc=(cx, 0, 0.05), scale=(1, 1, 0.5))
    key(rg, IMPACT0, scale=0)
    key(rg, f, scale=0)
    key(rg, f + 6, scale=(2.2, 2.2, 0.6))
    key(rg, IMPACT0 + 38, scale=(2.3, 2.3, 0.6))
    key(rg, IMPACT0 + 44, scale=0)
    tidy(rg, 'impact')
    for i in range(10):
        a = i * 36 + 8
        R = 2.1
        pts = [(R * math.cos(math.radians(th)) - 0.0, 0, 2.5 * math.sin(math.radians(th))) for th in range(0, 86, 10)]
        rad = [0.17 - 0.015 * k for k in range(len(pts) - 1)] + [0.0]
        rb = tube('im_rib_%d' % i, pts, rad, M['ivory'] if i % 2 else M['bone'], 7, loc=(cx, 0, 0.0), rot=(0, 0, a))
        t0 = f + 2 + (i % 5)
        key(rb, IMPACT0, scale=0)
        key(rb, t0, scale=0)
        key(rb, t0 + 1, scale=(1, 1, 0.02))
        key(rb, t0 + 5, scale=(1, 1, 1.15))
        key(rb, t0 + 8, scale=(1, 1, 1.0))
        key(rb, IMPACT0 + 38, scale=(1, 1, 1.0))
        key(rb, IMPACT0 + 42, scale=(1, 1, 0.0))
        key(rb, IMPACT0 + 44, scale=0)
        tidy(rb, 'impact')
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        sp = rnd.uniform(0.05, 0.12)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.3, 0.42)))
        vb = vert('im_vert_%d' % i, 0.0, 0.18, M['bone'], ol=0.012)
        debris(vb, Vector((cx, 0, 0.3)), v, f, spin=35, r=0.15)
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        sp = rnd.uniform(0.06, 0.15)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.28, 0.42)))
        ch = rock('im_chip_%d' % i, rnd.uniform(0.08, 0.15), M['ivory'] if i % 2 else M['stone'], seed=i + 30, sub=1, rough=0.25, flat=True, ol=0.012)
        debris(ch, Vector((cx, 0, 0.3)), v, f, spin=28, r=0.06)
    for i in range(14):
        a = math.radians(i * 360 / 14 + rnd.uniform(-8, 8))
        r = rnd.uniform(1.4, 2.8) * (1.25 if math.cos(a) < 0 else 1.0)
        p = sphere('im_dust_%d' % i, 0.4, dust if i % 3 else dust2, 12, 7)
        fly(p, (cx, 0, 0.3), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.4, 1.2)), f + i % 4, rnd.uniform(1.5, 2.3))
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 2.0)
        sp_ = sphere('im_ember_%d' % i, 0.07, hot, 6, 4, ol=0)
        fly(sp_, (cx, 0, 0.4), (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.8, 2.6)), f + i % 5, 1.2)
    return True
