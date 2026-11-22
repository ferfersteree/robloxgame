from spearlib import *

NAME = 'SP_04_feather'
N = 4
BG = '#93b97a'        # forest clearing
GROUND = '#93bd72'
TIP = 9.2
TRAIL = 5.2
FX_EXPORT = {'feather': 'im_feather_0', 'grass_blade': 'im_grass_0', 'leaf_ring': 'im_ring',
             'drift_feather': 'fl_feather_0'}


def mats():
    return dict(
        wood=toon('b04_wood', '#b4814a', '#74492a', '#dcaa72'),
        wood_dk=toon('b04_wood_dk', '#8a5a34', '#58351e', '#b78450'),
        leather=toon('b04_leather', '#c99a5a', '#8c5f30', '#eec98c'),
        cord=toon('b04_cord', '#efe0b8', '#b8a074', '#fff6dc', spec=0.2),
        flint=toon('b04_flint', '#8d97a6', '#4d5568', '#c5ccd8', spec=0.6),
        flint_lt=toon('b04_flint_lt', '#cfd4dc', '#8c93a4', '#f2f4f8', spec=0.6),
        resin=toon('b04_resin', '#e8a23a', '#a8641c', '#ffd27a', spec=0.9, emit=0.1),
        f_red=toon('b04_f_red', '#e0483a', '#9c2430', '#ff8a70', spec=0.2),
        f_teal=toon('b04_f_teal', '#2bb5a8', '#14757a', '#80e8dc', spec=0.2),
        f_yel=toon('b04_f_yel', '#f4c542', '#c0861e', '#fff09a', spec=0.2),
        f_blue=toon('b04_f_blue', '#3d7fd9', '#234a9c', '#8ab8f6', spec=0.2),
        f_white=toon('b04_f_white', '#f6f0e0', '#b8b0a0', '#ffffff', spec=0.2),
        f_orange=toon('b04_f_orange', '#f08a30', '#b0501a', '#ffbe7a', spec=0.2),
        grass=toon('b04_grass', '#5fbf4a', '#2f7a30', '#a8ec78', spec=0.2),
        grass_dk=toon('b04_grass_dk', '#3c9a3a', '#1e602a', '#7ed060', spec=0.2),
        glint=glow('b04_glint', '#fffbe0', 2.2),
        ring=glow('b04_ring', '#d8ffa8', 1.8),
        flash=ghost('b04_flash', '#f4ffd0', 1.8, 0.6, 1.2),
        down=ghost('b04_down', '#fffaf0', 1.0, 0.85, 1.1),
    )


def pop(ob, t0, s=1.0, end=39, over=1.15, rise=4):
    s = (s, s, s) if isinstance(s, (int, float)) else tuple(s)
    key(ob, IMPACT0, scale=0)
    key(ob, t0, scale=0)
    key(ob, t0 + rise, scale=tuple(a * over for a in s))
    key(ob, t0 + rise + 3, scale=s)
    key(ob, IMPACT0 + end, scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    FCOL = [M['f_red'], M['f_teal'], M['f_yel'], M['f_blue'], M['f_white'], M['f_orange']]
    wood, wood_dk, leather, cord, flint, flint_lt, resin = (M[k] for k in (
        'wood', 'wood_dk', 'leather', 'cord', 'flint', 'flint_lt', 'resin'))
    # ---- tail: acorn butt with three small tail feathers
    lathe('butt', [(0.1, 0), (0.1, 0.12), (0.3, 0.2), (0.55, 0.19), (0.75, 0.155), (0.75, 0)], wood_dk, 12)
    sphere('butt_knob', 0.14, resin, 8, 5, loc=(0, 0, 0.14))
    torus('butt_ring', 0.17, 0.04, cord, 12, 5, loc=(0, 0, 0.85))
    for i in range(3):
        az = i * 120 + 30
        leaf('tail_feather_%d' % i, 0.62, 0.2, FCOL[(i * 2) % 6], 0.025, 5, loc=(0, 0, 0.95), rot=(0, 72, az), ol=0.012)
    # ---- shaft: light ash, bare grip zone
    rod('shaft_lo', 0.155, 0.7, 3.3, wood, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, wood, segs=12, r1=0.14)
    coil('wrap_lo', 0.18, 0.03, 1.35, 1.88, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, cord, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.62, 4, leather, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, cord, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.0, 4.2, 4.4)):
        torus('band_%d' % i, 0.148, 0.025, (M['f_red'], M['f_yel'], M['f_teal'])[i], 12, 5, loc=(0, 0, z), ol=0.012)
    for i, (z, a) in enumerate(((1.6, 0.8), (4.8, 3.9))):
        sphere('knot_%d' % i, 0.065, wood_dk, 8, 5, loc=(0.13 * math.cos(a), 0.13 * math.sin(a), z), scale=(0.8, 1, 1.3), ol=0.012)
    # ---- feather tie: leather lashing + six big feathers fanning down and out
    coil('tie', 0.19, 0.04, 6.15, 6.5, 3, leather, segs=5)
    sphere('tie_knot', 0.09, resin, 8, 5, loc=(0.2, 0.06, 6.3), ol=0.012)
    for i in range(6):
        az = i * 60 + 10
        ca, sa = math.cos(math.radians(az)), math.sin(math.radians(az))
        base = (0.17 * ca, 0.17 * sa, 6.35)
        ln = 1.75 - 0.12 * (i % 2)
        leaf('feather_%d' % i, ln * 1.1, 0.62, FCOL[i], 0.035, 6, loc=base, rot=(0, 58, az), ol=0.015)
        leaf('feather_stripe_%d' % i, ln * 0.6, 0.2, FCOL[(i + 3) % 6], 0.035, 5, loc=(base[0] + 0.1 * ca, base[1] + 0.1 * sa, base[2] - 0.15),
             rot=(0, 58, az), ol=0.01)
        tube('quill_%d' % i, [base, (base[0] + 0.55 * ca * 0.55, base[1] + 0.55 * sa * 0.55, base[2] - 0.47)], 0.018, cord, 4, ol=0.0)
    # ---- socket + slim flint tip
    lathe('socket', [(6.4, 0.14), (6.55, 0.19), (6.8, 0.2), (7.0, 0.17), (7.1, 0.12), (7.1, 0)], wood_dk, 12)
    coil('socket_lash', 0.21, 0.03, 6.6, 6.98, 3, cord, segs=5)
    flint_pts = [(0.17, 7.0), (0.32, 7.45), (0.35, 8.0), (0.23, 8.6), (0.1, 9.0), (0.0, TIP),
                 (-0.1, 9.0), (-0.23, 8.6), (-0.35, 8.0), (-0.32, 7.45), (-0.17, 7.0)]
    blade('flint', flint_pts, 0.13, flint)
    blade('flint_core', [(x * 0.5, 7.2 + (z - 7.0) * 0.85) for (x, z) in flint_pts], 0.16, flint_lt, ol=0.012)
    for s in (-1, 1):
        cone('barb_%d' % (s + 1), 0.06, 0.34, flint, 5, loc=(s * 0.3, 0, 7.45), rot=(0, s * 150, 0), ol=0.012)
    for i in range(2):
        sphere('scar_%d' % i, 0.06, flint_lt, 6, 4, loc=(0.2 - i * 0.4, 0.1 * (1 - 2 * i), 7.9 + i * 0.4), scale=(1.3, 0.35, 0.9), ol=0.01)
    # ---- bead cord
    tube('charm_cord', [(0.17, 0.05, 6.45), (0.3, 0.1, 6.2), (0.34, 0.12, 5.9)], 0.02, cord, 5)
    for i, (z, m) in enumerate(((6.25, M['f_red']), (6.1, M['f_yel']), (5.95, M['f_teal']))):
        sphere('bead_%d' % i, 0.06, m, 8, 5, loc=(0.29 + i * 0.02, 0.11 + i * 0.005, z), ol=0.012)
    cone('tooth', 0.06, 0.26, M['f_white'], 6, loc=(0.34, 0.12, 5.9), rot=(180, 8, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(404)
    FCOL = [M['f_red'], M['f_teal'], M['f_yel'], M['f_blue'], M['f_white'], M['f_orange']]
    glint, ring_m, flash_m, down = M['glint'], M['ring'], M['flash'], M['down']
    # ---------------- idle: a few small feathers drifting near the head + glints
    fx('idle')
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 0.8)
        leaf('idle_feather_%d' % i, 0.3, 0.1, FCOL[i], 0.02, 4,
             loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.0)), rot=(rnd.uniform(0, 60), rnd.uniform(0, 360), rnd.uniform(0, 360)), ol=0.01)
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.35, 0.6), -0.2, 7.4 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: drifting feathers, down puffs, loose leaves
    fx('flight')
    fth = [leaf('fl_feather_%d' % i, 0.6, 0.22, FCOL[i % 6], 0.025, 5, ol=0.012) for i in range(10)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(fth, lambda t, i: (fj[i][0] * (0.2 + 0.9 * t) + 0.2 * math.sin(8 * t + i), fj[i][1] * (0.2 + 0.9 * t), 8.4 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (fj[i][2] + 360 * t, 40 * math.sin(6 * t + i), 180 * t))
    pf = [sphere('fl_down_%d' % i, 0.18, down, 10, 6) for i in range(8)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.8 * t), pj[i][1] * (0.2 + 0.8 * t), 7.0 - 10.0 * t),
           smax=lambda t, i: (0.6 + 1.2 * t) * math.sin(math.pi * t) ** 0.5)
    lv = [leaf('fl_leaf_%d' % i, 0.3, 0.14, M['grass'] if i % 2 else M['grass_dk'], 0.02, 4, ol=0.01) for i in range(6)]
    lj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(6)]
    stream(lv, lambda t, i: (lj[i][0] * (0.3 + 0.8 * t), lj[i][1] * (0.3 + 0.8 * t), 8.0 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (lj[i][2] + 540 * t, 300 * t, 0))
    # ---------------- impact: feathers burst up and spiral down, grass tufts pop up
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.3))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.0, alpha=0.7)
    key(fl, f + 10, scale=2.8, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    rg = torus('im_ring', 0.5, 0.05, ring_m, 32, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 13, scale=5.0, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    for i in range(18):
        a0 = rnd.uniform(0, 6.28)
        Rr = rnd.uniform(0.8, 1.4)
        H_ = rnd.uniform(1.6, 3.2)
        spin_dir = 1 if i % 2 else -1
        c = leaf('im_feather_%d' % i, 0.9, 0.3, FCOL[i % 6], 0.03, 6, ol=0.015)
        key(c, IMPACT0, loc=(cx, 0, 0.3), scale=0)
        key(c, f, loc=(cx, 0, 0.3), scale=0)
        for k in range(1, 13):
            u = k / 12.0
            ang = a0 + spin_dir * 2 * math.pi * 1.1 * u
            rr = (0.2 + Rr * u) * (1.0 if u < 0.9 else 0.9)
            z = 0.15 + H_ * math.sin(math.pi * u ** 0.65)
            p = (cx + rr * math.cos(ang), rr * math.sin(ang), z)
            key(c, f + k * 3, loc=p, rot=(25 * math.sin(2 * ang), 70 + 40 * math.cos(ang * 1.7), math.degrees(ang) + 90),
                scale=1.0 if k < 12 else 0.85)
        key(c, IMPACT0 + 44, scale=0)
        tidy(c, 'impact')
        ease_keys(c)
    # grass tufts pop up in a ring (3 blades each)
    for i in range(8):
        a = math.radians(i * 45 + rnd.uniform(-10, 10))
        rr = rnd.uniform(1.0, 2.0)
        bx, by = cx + rr * math.cos(a), rr * math.sin(a)
        t0 = f + 2 + i
        for j in range(3):
            b = math.radians(j * 120 + rnd.uniform(0, 40))
            tilt = aim((math.cos(b) * 0.45, math.sin(b) * 0.45, 1))
            blade_ob = cone('im_grass_%d' % (i * 3 + j), 0.07, 0.55 + 0.15 * (j % 2), M['grass'] if j % 2 else M['grass_dk'], 4,
                            loc=(bx + 0.06 * math.cos(b), by + 0.06 * math.sin(b), 0.0), rot=tilt, ol=0.012)
            pop(blade_ob, t0, 1.0, over=1.25, rise=5)
    # down puffs
    for i in range(6):
        a = math.radians(i * 60 + rnd.uniform(-10, 10))
        rr = rnd.uniform(1.0, 1.7)
        p = sphere('im_down_%d' % i, 0.22, down, 10, 6)
        end = (cx + rr * math.cos(a), rr * math.sin(a), 1.1)
        key(p, IMPACT0, loc=(cx, 0, 0.3), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.3), scale=0.3, alpha=1)
        key(p, f + 12, loc=end, scale=1.2, alpha=0.8)
        key(p, IMPACT0 + 44, loc=(end[0], end[1], end[2] + 0.8), scale=1.6, alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
