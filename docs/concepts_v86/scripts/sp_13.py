from spearlib import *

NAME = 'SP_13_canyon_hook'
N = 13
BG = '#c07a5a'        # canyon haze
GROUND = '#c9704b'    # red rock
TIP = 9.35
TRAIL = 5.2
FX_EXPORT = {'mesa': 'im_mesa_0', 'mesa_cap': 'im_cap_0', 'chip': 'im_chip_0', 'shock_ring': 'im_shock',
             'dust_ring': 'fl_ring_0'}
END = IMPACT0 + 44


def mats():
    return dict(
        red=toon('s13_red', '#c4492f', '#7a2a2a', '#ee7d55', spec=0.4, rimcol='#ffc48a'),
        tan=toon('s13_tan', '#e6b87a', '#a8703f', '#fbe0b0', spec=0.3),
        ochre=toon('s13_ochre', '#e08a3c', '#a4521f', '#ffc06a'),
        dark=toon('s13_dark', '#7a2e24', '#451a1e', '#a8503c'),
        wood=toon('s13_wood', '#a8693a', '#6a3b22', '#d39a64'),
        leather=toon('s13_leather', '#d9a25a', '#9b6531', '#f2c98a'),
        cord=toon('s13_cord', '#b4332a', '#6e1a22', '#e8665a', spec=0.2),
        turq=toon('s13_turq', '#2fb8b0', '#1a7a80', '#8ae8dc', spec=0.9, emit=0.15),
    )


def pop(ob, t0, s1=1.0, grow=5, hold=IMPACT0 + 38):
    """scale 0 -> s1, hold, 0 at the end (impact)"""
    t0 = min(t0, END - 8)
    key(ob, IMPACT0, scale=0)
    if t0 > IMPACT0:
        key(ob, t0, scale=0)
    key(ob, t0 + grow, scale=s1)
    key(ob, max(hold, t0 + grow + 1), scale=s1)
    key(ob, END, scale=0)
    tidy(ob, 'impact')
    ease_keys(ob)


def expand(ob, t0, s0, s1, dur):
    """glow/ghost ring: grows and fades"""
    key(ob, IMPACT0, scale=0, alpha=1)
    key(ob, t0, scale=s0, alpha=1)
    key(ob, min(t0 + dur, END), scale=s1, alpha=0)
    tidy(ob, 'impact', interp='LINEAR')
    ease_keys(ob)


def toss(c, p0, v, f, g=-0.03, zg=0.08):
    """ballistic debris that lands and stays until the end"""
    p0 = Vector(p0)
    key(c, IMPACT0, loc=p0, scale=0)
    key(c, f, loc=p0, scale=0.3)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= zg or t > 34
        if done:
            p.z = zg
        key(c, f + t, loc=p, scale=1, rot=(t * 30, t * 20, 0), interp='LINEAR')
        if done:
            break
    key(c, max(f + t + 2, IMPACT0 + 36), scale=1)
    key(c, END, scale=0)
    tidy(c, 'impact')


def strata_blade(nm, z0, z1, w, th, mat):
    return blade(nm, [(-w, z0), (w, z0), (w, z1), (-w, z1)], th, mat, ol=0.015)


def mesa(nm, r, h, mat, p):
    prof = [(0, 0), (0, r), (h * 0.38, r), (h * 0.38, r * 0.82), (h * 0.72, r * 0.82), (h * 0.72, r * 0.64), (h, r * 0.64), (h, 0)]
    return lathe(nm, prof, mat, 8, loc=p)


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    red, tan, ochre, dark, wood, leather, cord, turq = (M[k] for k in (
        'red', 'tan', 'ochre', 'dark', 'wood', 'leather', 'cord', 'turq'))
    # ---- tail: stepped sandstone pommel
    lathe('pommel', [(0, 0), (0, 0.16), (0.08, 0.2), (0.2, 0.2), (0.22, 0.25), (0.42, 0.25), (0.44, 0.2), (0.62, 0.2),
                     (0.64, 0.17), (0.7, 0.17)], dark, 10)
    rock('tail_stone', 0.15, tan, seed=3, sub=1, rough=0.15, flat=True, loc=(0, 0, 0.12), scale=(1, 1, 0.6))
    torus('butt_band', 0.19, 0.04, ochre, 14, 6, loc=(0, 0, 0.9))
    torus('butt_band2', 0.18, 0.035, tan, 14, 6, loc=(0, 0, 1.08))
    # ---- shaft (grip zone 2.0-3.0 is bare wood)
    rod('shaft_lo', 0.155, 0.6, 3.3, wood, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.3, wood, r1=0.14)
    coil('wrap_lo', 0.178, 0.03, 1.35, 1.92, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, ochre, 14, 6, loc=(0, 0, 1.94))
    coil('wrap_hi', 0.175, 0.03, 3.08, 3.62, 4, leather, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.176, 0.04, ochre, 14, 6, loc=(0, 0, 3.06))
    # layered sandstone strata on the upper shaft
    for i in range(5):
        cyl('strata_%d' % i, 0.215 if i % 2 == 0 else 0.19, 0.15, (red, tan, ochre, tan, red)[i], 10, 0.02,
            loc=(0, 0, 4.15 + i * 0.2))
    torus('strata_cap', 0.2, 0.035, dark, 14, 6, loc=(0, 0, 5.22))
    # ---- socket: flared sandstone cup, red lashing
    lathe('socket', [(6.1, 0.15), (6.25, 0.22), (6.6, 0.3), (6.95, 0.27), (7.05, 0.2), (7.05, 0)], tan, 12)
    torus('collar_a', 0.24, 0.045, dark, 14, 6, loc=(0, 0, 6.3))
    torus('collar_b', 0.27, 0.04, ochre, 14, 6, loc=(0, 0, 6.88))
    coil('lash', 0.31, 0.03, 6.42, 6.78, 3, cord, segs=5)
    # ---- blade: layered red stone with strata bands
    blade('blade_main', [(0, 6.9), (0.34, 7.2), (0.44, 7.9), (0.32, 8.65), (0, TIP), (-0.32, 8.65), (-0.44, 7.9), (-0.34, 7.2)],
          0.15, red)
    strata_blade('band_0', 7.3, 7.5, 0.41, 0.19, tan)
    strata_blade('band_1', 7.78, 8.0, 0.47, 0.19, ochre)
    strata_blade('band_2', 8.25, 8.42, 0.41, 0.18, tan)
    # canyon-arch hook: three strata segments sweeping out and back in
    P = [(0.28, 0, 7.0), (0.72, 0, 7.08), (1.08, 0, 7.42), (1.2, 0, 7.95), (1.02, 0, 8.45), (0.68, 0, 8.72)]
    R_ = [0.22, 0.21, 0.19, 0.17, 0.13, 0.0]
    tube('hook_a', P[0:3], R_[0:3], red, 8, scale=(1, 0.6, 1))
    tube('hook_b', P[2:5], R_[2:5], tan, 8, scale=(1, 0.6, 1))
    tube('hook_c', P[4:6], R_[4:6], dark, 8, scale=(1, 0.6, 1))
    tube('spur', [(-0.28, 0, 6.98), (-0.62, 0, 7.05), (-0.86, 0, 7.3), (-0.9, 0, 7.7)], [0.18, 0.16, 0.12, 0.0], ochre, 8,
         scale=(1, 0.6, 1))
    for i, (x, y, z) in enumerate(((1.12, 0.1, 7.45), (1.18, -0.1, 7.95), (0.95, 0.08, 8.5))):
        rock('arch_rock_%d' % i, 0.12 - i * 0.015, tan if i != 1 else ochre, seed=i + 1, sub=1, rough=0.2, flat=True, loc=(x, y, z))
    sphere('gem_0', 0.07, turq, 8, 5, loc=(0.0, 0.17, 7.15), ol=0.012)
    # ---- charm: cord, turquoise bead, carved stone tablet
    tube('charm_cord', [(0.2, 0.03, 6.05), (0.33, 0.06, 5.8), (0.38, 0.07, 5.55)], 0.022, cord, 5)
    sphere('charm_bead_0', 0.065, turq, 8, 5, loc=(0.33, 0.065, 5.82), ol=0.012)
    sphere('charm_bead_1', 0.06, ochre, 8, 5, loc=(0.37, 0.07, 5.62), ol=0.012)
    rock('charm_tablet', 0.16, dark, seed=4, sub=1, rough=0.12, flat=True, loc=(0.38, 0.07, 5.38), scale=(0.8, 0.3, 1.2), ol=0.015)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1313)
    dust = ghost('s13_dust', '#e8956a', 1.0, 0.85, 1.1)
    dust_dk = ghost('s13_dust_dk', '#b04a34', 1.0, 0.85, 1.1)
    glint = glow('s13_glint', '#ffe2a8', 2.4)
    ring_m = glow('s13_airring', '#ffc88a', 1.8)
    # ---------------- idle: drifting sand motes and glints
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 0.95)
        sphere('idle_mote_%d' % i, rnd.uniform(0.05, 0.09), dust if i % 2 else dust_dk, 8, 5,
               loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.8, 9.2)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 0.9), -0.25, 7.4 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: red dust puffs, stone chips, shards, dust rings
    fx('flight')
    puffs = [sphere('fl_puff_%d' % i, 0.36, dust if i % 3 else dust_dk, 12, 7) for i in range(10)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.9 * t), jp[i][1] * (0.15 + 0.9 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    chips = [rock('fl_chip_%d' % i, 0.1, (M['red'], M['tan'], M['ochre'])[i % 3], seed=i, sub=1, rough=0.22, flat=True) for i in range(10)]
    jc = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(chips, lambda t, i: (jc[i][0] * (0.3 + 0.9 * t), jc[i][1] * (0.3 + 0.9 * t), 8.4 - 13.0 * t),
           smax=1.0, spin=lambda t, i: (jc[i][2] + 720 * t, 540 * t, 0))
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.34, M['red'] if i % 2 else M['dark'], 4, 0.4, 0.7, both=True, ol=0.012) for i in range(6)]
    js = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(shards, lambda t, i: (js[i][0] * (0.35 + 1.0 * t), js[i][1] * (0.35 + 1.0 * t), 8.9 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (js[i][2] + 540 * t, 360 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.45, 0.035, ring_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: stepped mesa pillars rise in a ring, red dust, chips
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s13_flash', '#ffd8a0', 2.0, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.2, alpha=0.8)
    key(flash, f + 10, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    shock = torus('im_shock', 0.5, 0.05, glow('s13_shock', '#ffb877', 1.8), 32, 5, loc=(cx, 0, 0.06))
    expand(shock, f, 0.3, 5.2, 12)
    scar = torus('im_scar', 0.9, 0.12, M['dark'], 20, 6, loc=(cx, 0, 0.0))
    pop(scar, f, (1.0, 1.0, 0.45), grow=4)
    # six mesa pillars (tiered, tan cap slabs) + five small stepped blocks
    for i, (ang, rr, s) in enumerate(((-125, 1.6, 0.85), (-75, 1.95, 1.15), (-25, 1.6, 0.9), (28, 1.95, 1.1), (78, 1.6, 0.8), (128, 1.95, 1.0))):
        a = math.radians(ang)
        px, py = cx + rr * math.cos(a), rr * math.sin(a)
        t0 = f + i
        pm = mesa('im_mesa_%d' % i, 0.4, 1.4, M['red'] if i % 2 else M['ochre'], (px, py, 0.0))
        pop(pm, t0, (1, 1, s), grow=5)
        cap = cyl('im_cap_%d' % i, 0.3, 0.14, M['tan'], 8, 0.03, loc=(px, py, 0.2))
        key(cap, IMPACT0, scale=0)
        key(cap, t0, loc=(px, py, 0.2), scale=0)
        key(cap, t0 + 5, loc=(px, py, 1.4 * s + 0.05), scale=1.0)
        key(cap, IMPACT0 + 38, scale=1.0)
        key(cap, END, scale=0)
        tidy(cap, 'impact')
        ease_keys(cap)
    for i, (ang, s) in enumerate(((-110, 0.5), (-55, 0.7), (0, 0.55), (55, 0.8), (110, 0.6))):
        a = math.radians(ang)
        pm = mesa('im_step_%d' % i, 0.26, 0.9, M['tan'] if i % 2 else M['red'], (cx + 2.6 * math.cos(a), 2.6 * math.sin(a), 0.0))
        pop(pm, f + 3 + i, (1, 1, s), grow=5)
    for i in range(6):
        a = math.radians(i * 60 + 20)
        L_ = rnd.uniform(0.9, 1.5)
        pts = [(0, 0, 0), (0.5 * L_ * math.cos(a + 0.15), 0.5 * L_ * math.sin(a + 0.15), 0), (L_ * math.cos(a), L_ * math.sin(a), 0)]
        if abs(math.cos(a)) > 0.95 and math.cos(a) < 0:
            continue
        cr = tube('im_crack_%d' % i, pts, [0.07, 0.05, 0.0], M['dark'], 4, ol=0, loc=(cx, 0, 0.02))
        pop(cr, f, (1, 1, 0.3), grow=4)
    for i in range(12):
        a = math.radians(i * 360 / 12 + rnd.uniform(-10, 10))
        rr = rnd.uniform(1.4, 2.6)
        p = sphere('im_dust_%d' % i, 0.35, dust if i % 3 else dust_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.9))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.4, 2.0), alpha=0.9)
        key(p, END, loc=(end[0], end[1], end[2] + 0.5), scale=rnd.uniform(2.2, 2.8), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    for i in range(14):
        a = math.radians(rnd.uniform(-140, 140))
        sp = rnd.uniform(0.06, 0.12)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.26, 0.4)))
        c = rock('im_chip_%d' % i, rnd.uniform(0.08, 0.14), (M['red'], M['tan'], M['ochre'])[i % 3], seed=i + 30, sub=1, rough=0.25, flat=True)
        toss(c, (cx, 0, 0.15), v, f)
    for i in range(4):
        a = math.radians(rnd.uniform(-120, 120))
        sp = rnd.uniform(0.05, 0.09)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.2, 0.3)))
        c = rock('im_boulder_%d' % i, rnd.uniform(0.17, 0.24), M['dark'] if i % 2 else M['red'], seed=i + 50, sub=1, rough=0.25, flat=True)
        toss(c, (cx, 0, 0.15), v, f, zg=0.14)
    return True
