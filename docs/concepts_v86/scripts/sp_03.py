from spearlib import *

NAME = 'SP_03_bronze'
N = 3
BG = '#8fb36e'        # forest
GROUND = '#7fae62'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'spark': 'im_spark_0', 'shock_ring': 'im_shock_0', 'gong_ring': 'im_gong_0',
             'bronze_flake': 'fl_flake_0', 'dent': 'im_dent'}


def mats():
    return dict(
        bronze=toon('b03_bronze', '#c98a3a', '#7a4a1c', '#f5c77a', spec=1.0, rim=0.5, rimcol='#ffe0a0'),
        bronze_dk=toon('b03_bronze_dk', '#9a5f26', '#5a3414', '#d9944a', spec=0.8),
        bronze_lt=toon('b03_bronze_lt', '#e8b35a', '#a8702c', '#fff0b8', spec=1.0, emit=0.1),
        wood=toon('b03_wood', '#6b4a30', '#3d2818', '#9a7048'),
        leather=toon('b03_leather', '#8a3f2c', '#52221a', '#c0694a'),
        patina=toon('b03_patina', '#3aa58f', '#1d6a5e', '#86e0cc', spec=0.6),
        cord=toon('b03_cord', '#c23a2f', '#7a1a1e', '#f06a54', spec=0.2),
        spark=glow('b03_spark', '#ffd27a', 2.2),
        spark_hot=glow('b03_spark_hot', '#fff1c0', 2.2),
        ring=glow('b03_ring', '#ffb347', 2.2),
        flash=ghost('b03_flash', '#ffe2a0', 2.0, 0.7, 1.2),
        puff=ghost('b03_puff', '#d9c9a0', 0.9, 0.8, 1.1),
        disc=ghost('b03_disc', '#ffc566', 1.8, 0.6, 1.0, edge=True),
        dent=toon('b03_dent', '#6b4a30', '#3d2818', '#9a7048'),
    )


def spark_arc(ob, p0, v, f, g, life, rest=0.03, s=1.0):
    """glow spark flying along its own velocity (aim), fading out after `life` frames"""
    p0, v = Vector(p0), Vector(v)
    key(ob, IMPACT0, loc=p0, scale=0, alpha=1)
    key(ob, f - 1, loc=p0, scale=0, alpha=1)
    key(ob, f, loc=p0, rot=aim(v), scale=0.2 * s, alpha=1)
    t = 2
    while t < life:
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        if p.z < rest:
            p.z = rest
        vel = v + Vector((0, 0, g * t))
        key(ob, f + t, loc=p, rot=aim(vel), scale=s, alpha=1, interp='LINEAR')
        t += 2
    key(ob, f + life, scale=0.3 * s, alpha=0)
    key(ob, IMPACT0 + 44, scale=0, alpha=0)
    tidy(ob, 'impact')


def ballistic(c, p0, v, f, g=-0.028, spin=(25, 18), hold=IMPACT0 + 36, rest=0.05, sc=1.0, rot0=0.0):
    p0 = Vector(p0)
    key(c, IMPACT0, loc=p0, scale=0)
    if f - 1 > IMPACT0:
        key(c, f - 1, loc=p0, scale=0)
    key(c, f, loc=p0, scale=0.2 * sc)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= rest or t > 34
        if done:
            p.z = rest
        key(c, f + t, loc=p, scale=sc, rot=(rot0 + t * spin[0], t * spin[1], 0), interp='LINEAR')
        if done:
            break
    key(c, max(f + t + 2, hold), scale=sc)
    key(c, IMPACT0 + 44, scale=0)
    tidy(c, 'impact')
    return p


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    bronze, bronze_dk, bronze_lt, wood, leather, patina, cord = (M[k] for k in (
        'bronze', 'bronze_dk', 'bronze_lt', 'wood', 'leather', 'patina', 'cord'))
    # ---- tail: round cast pommel with a stud and a collar
    sphere('pommel', 0.3, bronze, 12, 7, loc=(0, 0, 0.32), scale=(1, 1, 0.95))
    cone('pommel_stud', 0.07, 0.16, bronze_lt, 6, loc=(0, 0, 0.17), rot=(180, 0, 0), ol=0.015)
    lathe('pommel_neck', [(0.5, 0), (0.5, 0.17), (0.62, 0.22), (0.78, 0.19), (0.9, 0.155), (0.9, 0)], bronze_dk, 12)
    torus('pommel_ring', 0.22, 0.045, bronze_lt, 12, 5, loc=(0, 0, 0.55))
    # ---- shaft: dark ash wood, bare grip zone
    rod('shaft_lo', 0.155, 0.85, 3.3, wood, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.25, wood, segs=12, r1=0.14)
    cyl('collar_lo', 0.215, 0.2, bronze, 14, loc=(0, 0, 1.08))
    coil('wrap_lo', 0.18, 0.03, 1.35, 1.88, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, bronze_lt, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.64, 4, leather, segs=5, phase=1.2)
    torus('wrap_hi_cap', 0.178, 0.04, bronze_lt, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.35, 4.55, 4.75)):
        torus('cord_band_%d' % i, 0.148, 0.025 if i != 1 else 0.035, cord, 12, 5, loc=(0, 0, z), ol=0.015)
    for i, z in enumerate((4.15, 5.1, 5.55)):
        a = i * 2.1 + 0.4
        sphere('stud_%d' % i, 0.055, bronze_lt, 8, 5, loc=(0.145 * math.cos(a), 0.145 * math.sin(a), z), ol=0.012)
    cyl('collar_hi', 0.2, 0.2, bronze, 14, loc=(0, 0, 6.08))
    # ---- flared socket with rim and rivets
    lathe('socket', [(6.2, 0.15), (6.4, 0.2), (6.7, 0.29), (6.95, 0.36), (7.1, 0.34), (7.15, 0.2), (7.15, 0)], bronze, 14)
    torus('socket_rim', 0.35, 0.05, bronze_lt, 14, 5, loc=(0, 0, 6.98))
    for i in range(4):
        a = math.radians(i * 90 + 45)
        sphere('rivet_%d' % i, 0.05, bronze_lt, 8, 5, loc=(0.3 * math.cos(a), 0.3 * math.sin(a), 6.78), ol=0.012)
    # ---- heavy cast leaf blade: bright edge layer, darker body, raised mid-rib
    leaf_pts = [(0.3, 7.1), (0.52, 7.45), (0.64, 7.9), (0.6, 8.35), (0.44, 8.8), (0.22, 9.15), (0.0, TIP),
                (-0.22, 9.15), (-0.44, 8.8), (-0.6, 8.35), (-0.64, 7.9), (-0.52, 7.45), (-0.3, 7.1)]
    blade('blade_edge', leaf_pts, 0.1, bronze_lt, edge=0.5)
    blade('blade_body', [(x * 0.8, 7.28 + (z - 7.1) * 0.9) for (x, z) in leaf_pts], 0.17, bronze)
    blade('blade_rib', [(0.1, 7.2), (0.11, 8.0), (0.06, 8.9), (0.0, 9.2), (-0.06, 8.9), (-0.11, 8.0), (-0.1, 7.2)], 0.24, bronze_dk, ol=0.015)
    for i, (x, z, sg) in enumerate(((0.32, 7.65, 1), (-0.35, 8.1, -1), (0.2, 8.55, 1))):
        sphere('patina_%d' % i, 0.07, patina, 6, 4, loc=(x, sg * 0.15, z), scale=(1.4, 0.5, 1.0), ol=0.01)
    # ---- bell charm on a red cord
    tube('charm_cord', [(0.22, 0.04, 6.1), (0.34, 0.07, 5.85), (0.38, 0.08, 5.6)], 0.022, cord, 5)
    torus('charm_ring', 0.06, 0.02, bronze_lt, 10, 4, loc=(0.38, 0.08, 5.66), rot=(90, 0, 0), ol=0.01)
    lathe('bell', [(0.0, 0.14), (0.04, 0.12), (0.16, 0.08), (0.22, 0.0)], bronze_lt, 10, loc=(0.38, 0.08, 5.38), rot=(0, 0, 0), ol=0.012)
    # (lead fix) cast bronze ox-horn guard under the blade + patina studs, so the silhouette is not just a leaf
    for s in (-1, 1):
        n_ = 'L' if s < 0 else 'R'
        tube('horn_' + n_, [(s * 0.18, 0, 7.05), (s * 0.45, 0, 7.0), (s * 0.66, 0, 6.82), (s * 0.7, 0, 6.55)], [0.09, 0.08, 0.06, 0.0],
             M['bronze_dk'], 8)
        sphere('horn_stud_' + n_, 0.06, M['patina'], 7, 4, loc=(s * 0.45, 0, 7.0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(303)
    spark, hot, ring_m, flash_m, puff = M['spark'], M['spark_hot'], M['ring'], M['flash'], M['puff']
    # ---------------- idle: glints and tiny floating sparks around the blade
    fx('idle')
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, hot, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.7), -0.2, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 0.85)
        crystal('idle_spark_%d' % i, 0.03, 0.18, spark, 4, 0.5, 0.7, both=True,
                loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.2)), rot=(rnd.uniform(0, 40), rnd.uniform(0, 40), 0))
    # ---------------- flight: elongated sparks, bronze flakes, clang rings, warm puffs
    fx('flight')
    sps = [crystal('fl_spark_%d' % i, 0.04, 0.6, spark if i % 2 else hot, 4, 0.5, 0.7, both=True) for i in range(14)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.7, 1.3)) for _ in range(14)]
    stream(sps, lambda t, i: (sj[i][0] * (0.2 + 0.9 * t), sj[i][1] * (0.2 + 0.9 * t), 8.8 - 12.5 * t),
           smax=lambda t, i: sj[i][2] * math.sin(math.pi * t) ** 0.6, spin=lambda t, i: (0, 0, 0))
    flakes = [leaf('fl_flake_%d' % i, 0.28, 0.12, M['bronze_lt'] if i % 2 else M['bronze'], 0.025, 4, ol=0.012) for i in range(6)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(flakes, lambda t, i: (fj[i][0] * (0.3 + 0.8 * t), fj[i][1] * (0.3 + 0.8 * t), 8.4 - 13.0 * t),
           smax=1.0, spin=lambda t, i: (fj[i][2] + 720 * t, 540 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.5, 0.045, ring_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.4 - 6.5 * t), smax=lambda t, i: (0.6 + 1.5 * t) * math.sin(math.pi * t) ** 0.4)
    pf = [sphere('fl_puff_%d' % i, 0.3, puff, 10, 6) for i in range(4)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(4)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.7 * t), pj[i][1] * (0.2 + 0.7 * t), 6.0 - 9.0 * t),
           smax=lambda t, i: (0.5 + 1.2 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: CLANG - flat shock rings, a vertical gong ring, forward fan of sparks
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.55, wobble=9)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.35))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.0, alpha=0.8)
    key(fl, f + 10, scale=2.8, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    for k in range(2):
        sr = torus('im_shock_%d' % k, 0.5, 0.07 - 0.02 * k, ring_m, 36, 5, loc=(cx, 0, 0.05 + 0.02 * k))
        key(sr, IMPACT0, scale=0, alpha=1)
        key(sr, f + 5 * k - 1, scale=0, alpha=1)
        key(sr, f + 5 * k, scale=0.3, alpha=1)
        key(sr, f + 5 * k + 13, scale=5.2 - 1.0 * k, alpha=0)
        tidy(sr, 'impact', interp='LINEAR')
        ease_keys(sr)
    for k in range(3):
        gr = torus('im_gong_%d' % k, 0.8, 0.06, ring_m, 32, 5, axis='X', loc=(cx - 0.05, 0, 1.0))
        key(gr, IMPACT0, scale=0, alpha=1)
        key(gr, f + 4 * k - 1, scale=0, alpha=1)
        key(gr, f + 4 * k, scale=0.3, alpha=1)
        key(gr, f + 4 * k + 18, scale=2.4 + 0.5 * k, alpha=0)
        tidy(gr, 'impact', interp='LINEAR')
        ease_keys(gr)
    gd = cyl('im_gong_disc', 0.8, 0.05, M['disc'], 24, 0.01, axis='X', loc=(cx - 0.05, 0, 1.0))
    key(gd, IMPACT0, scale=0, alpha=1)
    key(gd, f, scale=0.3, alpha=0.9)
    key(gd, f + 12, scale=2.6, alpha=0)
    tidy(gd, 'impact', interp='LINEAR')
    dent = torus('im_dent', 0.5, 0.14, M['dent'], 18, 6, loc=(cx, 0, 0.0))
    key(dent, IMPACT0, scale=0)
    key(dent, f, scale=0)
    key(dent, f + 3, scale=(1.12, 1.12, 0.5))
    key(dent, f + 6, scale=(1, 1, 0.45))
    key(dent, IMPACT0 + 40, scale=(1, 1, 0.45))
    key(dent, IMPACT0 + 44, scale=0)
    tidy(dent, 'impact')
    # forward fan fountain: long thin sparks
    g = -0.03
    for i in range(18):
        ph = math.radians(-42 + 84 * i / 17 + rnd.uniform(-3, 3))
        el = math.radians(rnd.uniform(38, 62))
        sp = rnd.uniform(0.2, 0.3)
        v = Vector((sp * math.cos(el) * math.cos(ph), sp * math.cos(el) * math.sin(ph), sp * math.sin(el) + 0.05))
        s_ob = crystal('im_spark_%d' % i, 0.04, 0.55, spark if i % 2 else hot, 4, 0.5, 0.7, both=True)
        spark_arc(s_ob, (cx + 0.15, 0, 0.2), v, f + i % 3, g, 26)
    for i in range(6):
        a = math.radians(rnd.uniform(110, 250))
        sp = rnd.uniform(0.1, 0.17)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.2, 0.3)))
        s_ob = crystal('im_spark_b%d' % i, 0.035, 0.4, spark, 4, 0.5, 0.7, both=True)
        spark_arc(s_ob, (cx, 0, 0.2), v, f, g, 20)
    # bronze flakes and dust
    for i in range(6):
        a = math.radians(rnd.uniform(0, 360))
        sp = rnd.uniform(0.08, 0.15)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.22, 0.34)))
        c = leaf('im_flake_%d' % i, 0.26, 0.11, M['bronze_lt'] if i % 2 else M['bronze_dk'], 0.025, 4, ol=0.012)
        ballistic(c, (cx, 0, 0.2), v, f, -0.028, spin=(40, 25), rot0=rnd.uniform(0, 360), rest=0.04)
    for i in range(6):
        a = math.radians(i * 60 + rnd.uniform(-10, 10))
        rr = rnd.uniform(1.2, 1.8)
        p = sphere('im_puff_%d' % i, 0.32, puff, 10, 6)
        end = (cx + rr * math.cos(a), rr * math.sin(a), 0.3)
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=(1.3, 1.3, 0.8), alpha=0.8)
        key(p, IMPACT0 + 44, loc=(end[0], end[1], end[2] + 0.4), scale=(1.9, 1.9, 1.0), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
