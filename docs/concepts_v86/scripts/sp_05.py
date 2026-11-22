from spearlib import *

NAME = 'SP_05_iron'
N = 5
BG = '#b59a5e'        # savanna
GROUND = '#d9bf6e'
TIP = 9.1
TRAIL = 5.2
FX_EXPORT = {'slab': 'im_slab_0', 'spark': 'im_spark_0', 'groove': 'im_groove', 'pebble': 'im_pebble_0',
             'iron_ring': 'fl_ring_0'}


def mats():
    return dict(
        iron=toon('b05_iron', '#6a7480', '#38404c', '#a6b2c0', spec=0.9, rim=0.5, rimcol='#e8f0ff'),
        iron_dk=toon('b05_iron_dk', '#4a5360', '#262c36', '#7e8a98', spec=0.6),
        steel=toon('b05_steel', '#c4ceda', '#7a8698', '#f4f8ff', spec=1.0),
        rust=toon('b05_rust', '#c4602a', '#8a3a1a', '#f09050', spec=0.3),
        oak=toon('b05_oak', '#6e4a2e', '#3e2818', '#9c7048'),
        leather=toon('b05_leather', '#8a5530', '#52301a', '#c08450'),
        cord=toon('b05_cord', '#b8352a', '#74181c', '#ee6a52', spec=0.2),
        bone=toon('b05_bone', '#f0e4c4', '#b8a07a', '#fffaf0'),
        slab=toon('b05_slab', '#a89c84', '#6a6050', '#d4c8b0'),
        slab_dk=toon('b05_slab_dk', '#7a6e5c', '#463e32', '#a89c84'),
        spark=glow('b05_spark', '#ff9a3a', 2.2),
        hot=glow('b05_hot', '#ffd27a', 2.2),
        ring=glow('b05_ring', '#ffc27a', 1.8),
        flash=ghost('b05_flash', '#ffb15a', 2.0, 0.6, 1.2),
        dust=ghost('b05_dust', '#dcc592', 1.0, 0.85, 1.1),
        dust_dk=ghost('b05_dust_dk', '#b69a68', 0.9, 0.85, 1.1),
    )


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
    iron, iron_dk, steel, rust, oak, leather, cord, bone = (M[k] for k in (
        'iron', 'iron_dk', 'steel', 'rust', 'oak', 'leather', 'cord', 'bone'))
    # ---- tail: iron spike ferrule
    cone('butt_spike', 0.15, 0.45, iron, 8, loc=(0, 0, 0.45), rot=(180, 0, 0))
    cyl('butt_cap', 0.2, 0.16, iron_dk, 14, loc=(0, 0, 0.55))
    torus('butt_band', 0.19, 0.04, steel, 12, 5, loc=(0, 0, 0.8))
    # ---- shaft: dark oak, bare grip zone
    rod('shaft_lo', 0.155, 0.7, 3.3, oak, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, oak, segs=12, r1=0.14)
    coil('wrap_lo', 0.18, 0.03, 1.35, 1.88, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, iron, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.62, 4, leather, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, iron, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.2, 4.9)):
        cyl('iron_band_%d' % i, 0.19, 0.16, iron, 14, loc=(0, 0, z))
    for i, z in enumerate((4.56,)):
        torus('rust_band', 0.152, 0.03, rust, 12, 5, loc=(0, 0, z), ol=0.012)
    # langets: iron straps up the shaft under the socket
    for s in (-1, 1):
        box('langet_%d' % (s + 1), (0.07, 0.12, 1.0), iron, bev=0.02, bsegs=1, loc=(s * 0.165, 0, 5.55))
        for k, z in enumerate((5.2, 5.9)):
            sphere('langet_rivet_%d%d' % (s + 1, k), 0.05, steel, 6, 4, loc=(s * 0.2, 0, z), ol=0.01)
    # ---- socket and cross-lug wings
    lathe('socket', [(6.1, 0.15), (6.3, 0.22), (6.6, 0.28), (6.85, 0.26), (7.0, 0.2), (7.0, 0)], iron, 14)
    cyl('lug_bar', 0.13, 1.5, iron_dk, 10, 0.03, axis='X', loc=(0, 0, 6.75))
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        tube('wing_' + nm, [(s * 0.7, 0, 6.75), (s * 0.95, 0, 6.8), (s * 1.12, 0, 6.6), (s * 1.12, 0, 6.3)], [0.12, 0.1, 0.085, 0.0], iron, 8)
        sphere('lug_knob_' + nm, 0.15, steel, 10, 6, loc=(s * 0.78, 0, 6.75))
    torus('socket_ring', 0.28, 0.05, steel, 14, 5, loc=(0, 0, 6.42))
    # ---- wide boar blade: edge layer, body, raised rib, rivets, rust
    leaf_pts = [(0.3, 7.0), (0.58, 7.35), (0.78, 7.85), (0.74, 8.3), (0.5, 8.7), (0.24, 9.0), (0.0, TIP),
                (-0.24, 9.0), (-0.5, 8.7), (-0.74, 8.3), (-0.78, 7.85), (-0.58, 7.35), (-0.3, 7.0)]
    blade('blade_edge', leaf_pts, 0.1, steel, edge=0.5)
    blade('blade_body', [(x * 0.8, 7.18 + (z - 7.0) * 0.9) for (x, z) in leaf_pts], 0.17, iron)
    blade('blade_rib', [(0.1, 7.15), (0.11, 7.9), (0.06, 8.8), (0.0, 9.0), (-0.06, 8.8), (-0.11, 7.9), (-0.1, 7.15)], 0.25, iron_dk, ol=0.015)
    for i, (x, z) in enumerate(((0.42, 7.4), (-0.42, 7.4), (0.5, 7.9), (-0.5, 7.9))):
        sphere('blade_rivet_%d' % i, 0.06, steel, 7, 4, loc=(x, 0.19 if i % 2 else -0.19, z), ol=0.012)
    for i, (x, z, sg) in enumerate(((0.32, 8.2, 1), (-0.3, 7.6, -1))):
        sphere('rust_spot_%d' % i, 0.07, rust, 6, 4, loc=(x, sg * 0.18, z), scale=(1.5, 0.4, 1.0), ol=0.01)
    # ---- boar tusk charm on a red cord
    tube('charm_cord', [(0.2, 0.04, 6.2), (0.34, 0.08, 5.95), (0.38, 0.1, 5.75)], 0.02, cord, 5)
    tube('tusk', [(0.38, 0.1, 5.75), (0.5, 0.1, 5.45), (0.52, 0.1, 5.15), (0.4, 0.1, 4.95)], [0.07, 0.06, 0.04, 0.0], bone, 6, ol=0.012)
    torus('charm_ring', 0.05, 0.02, steel, 10, 4, loc=(0.38, 0.1, 5.8), rot=(90, 0, 0), ol=0.01)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def skid(ob, y, L_, f, dur, h=0.08):
    """glow spark skidding forward along the ground (x grows), fading at the end"""
    x0 = 0.6
    key(ob, IMPACT0, loc=(x0, y, h), scale=0, alpha=1)
    key(ob, f - 1, loc=(x0, y, h), scale=0, alpha=1)
    key(ob, f, loc=(x0, y, h), scale=0.3, alpha=1)
    key(ob, f + dur // 2, loc=(x0 + L_ * 0.6, y, h + 0.12), scale=1.0, alpha=1)
    key(ob, f + dur, loc=(x0 + L_, y, h), scale=0.5, alpha=0)
    key(ob, IMPACT0 + 44, scale=0, alpha=0)
    tidy(ob, 'impact')


def build_fx(M):
    rnd = random.Random(505)
    spark, hot, ring_m, flash_m, dust, dust_dk = M['spark'], M['hot'], M['ring'], M['flash'], M['dust'], M['dust_dk']
    # ---------------- idle: glints + a few hot specks near the blade
    fx('idle')
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, hot, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 0.85), -0.2, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.55, 0.95)
        sphere('idle_speck_%d' % i, 0.04, spark, 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.2)))
    # ---------------- flight: orange sparks, iron flecks, dust and rings
    fx('flight')
    sps = [crystal('fl_spark_%d' % i, 0.04, 0.5, spark if i % 2 else hot, 4, 0.5, 0.7, both=True) for i in range(12)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.7, 1.3)) for _ in range(12)]
    stream(sps, lambda t, i: (sj[i][0] * (0.2 + 0.9 * t), sj[i][1] * (0.2 + 0.9 * t), 8.6 - 12.0 * t),
           smax=lambda t, i: sj[i][2] * math.sin(math.pi * t) ** 0.6, spin=lambda t, i: (0, 0, 0))
    fl = [rock('fl_fleck_%d' % i, 0.09, M['iron'] if i % 2 else M['rust'], seed=i + 3, sub=1, rough=0.2, flat=True) for i in range(6)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(fl, lambda t, i: (fj[i][0] * (0.3 + 0.8 * t), fj[i][1] * (0.3 + 0.8 * t), 8.2 - 13.0 * t),
           smax=1.0, spin=lambda t, i: (fj[i][2] + 720 * t, 540 * t, 0))
    pf = [sphere('fl_puff_%d' % i, 0.32, dust if i % 2 else dust_dk, 10, 6) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.9 * t), pj[i][1] * (0.2 + 0.9 * t), 7.2 - 11.0 * t),
           smax=lambda t, i: (0.5 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.5, 0.05, ring_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.3 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: HEAVY - ground slabs crack and tilt up, spark line skids forward, dust
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.7, wobble=5)
    f = IMPACT0 + 4
    cx = 0.45
    fl_ = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.3))
    key(fl_, IMPACT0, scale=0, alpha=1)
    key(fl_, f, scale=0.4, alpha=1)
    key(fl_, f + 4, scale=2.0, alpha=0.7)
    key(fl_, f + 10, scale=2.8, alpha=0)
    tidy(fl_, 'impact', interp='LINEAR')
    for i in range(4):
        a = math.radians(i * 90 + 45)
        r = 1.35
        sl = box('im_slab_%d' % i, (1.15, 0.85, 0.3), M['slab'] if i % 2 else M['slab_dk'], bev=0.06, bsegs=1,
                 loc=(cx + r * math.cos(a), r * math.sin(a), 0.0), rot=(0, 0, math.degrees(a)), ol=0.02)
        p = (cx + r * math.cos(a), r * math.sin(a))
        az = math.degrees(a)
        t0 = f + i
        key(sl, IMPACT0, scale=0)
        key(sl, t0, loc=(p[0], p[1], 0.0), rot=(0, 0, az), scale=0)
        key(sl, t0 + 1, loc=(p[0], p[1], 0.1), rot=(0, 3, az), scale=1.0)
        key(sl, t0 + 5, loc=(p[0], p[1], 0.3), rot=(0, 34, az), scale=1.05)
        key(sl, t0 + 9, loc=(p[0], p[1], 0.24), rot=(0, 26, az), scale=1.0)
        key(sl, IMPACT0 + 38, scale=1.0)
        key(sl, IMPACT0 + 44, scale=0)
        tidy(sl, 'impact')
        for j in range(1):
            cr = tube('im_crack_%d' % i, [(cx + 0.45 * math.cos(a + 0.4), 0.45 * math.sin(a + 0.4), 0.01),
                                          (cx + 0.9 * math.cos(a + 0.5), 0.9 * math.sin(a + 0.5), 0.01),
                                          (cx + 1.5 * math.cos(a + 0.3), 1.5 * math.sin(a + 0.3), 0.01)], [0.07, 0.05, 0.0], M['iron_dk'], 4, ol=0)
            cr.scale = (1, 1, 0.3)
            key(cr, IMPACT0, scale=0)
            key(cr, f, scale=0)
            key(cr, f + 4, scale=(1, 1, 0.3))
            key(cr, IMPACT0 + 40, scale=(1, 1, 0.3))
            key(cr, IMPACT0 + 44, scale=0)
            tidy(cr, 'impact')
    # skid groove + the orange spark line
    gv = box('im_groove', (4.0, 0.2, 0.05), M['iron_dk'], bev=0.01, bsegs=1, loc=(cx + 2.0, 0, 0.03), ol=0.0)
    key(gv, IMPACT0, scale=0)
    key(gv, f, loc=(cx + 0.05, 0, 0.03), scale=(0.01, 1, 1))
    key(gv, f + 10, loc=(cx + 2.0, 0, 0.03), scale=(1, 1, 1))
    key(gv, IMPACT0 + 38, loc=(cx + 2.0, 0, 0.03), scale=(1, 1, 1))
    key(gv, IMPACT0 + 44, loc=(cx + 2.0, 0, 0.03), scale=0)
    tidy(gv, 'impact')
    for i in range(14):
        sp = crystal('im_spark_%d' % i, 0.04, 0.5, spark if i % 2 else hot, 4, 0.5, 0.7, both=True, rot=(0, 90, 0))
        skid(sp, rnd.uniform(-0.25, 0.25), rnd.uniform(1.6, 4.2), f + i % 4, 14 + i % 5)
    # dust and stones
    for i in range(10):
        a = math.radians(i * 36 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.4, 2.4) * (1.3 if math.cos(a) > 0 else 1.0)
        p = sphere('im_dust_%d' % i, 0.36, dust if i % 3 else dust_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.8))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.3, 1.8), alpha=0.9)
        key(p, IMPACT0 + 44, loc=(end[0], end[1], end[2] + 0.5), scale=rnd.uniform(2.0, 2.6), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    for i in range(10):
        a = math.radians(rnd.uniform(0, 360))
        s_ = rnd.uniform(0.07, 0.15)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.22, 0.36)))
        c = rock('im_pebble_%d' % i, rnd.uniform(0.09, 0.17), M['slab'] if i % 2 else M['iron_dk'], seed=i + 40, sub=1, rough=0.25, flat=True)
        ballistic(c, (cx, 0, 0.15), v, f, rot0=rnd.uniform(0, 360))
    return True
