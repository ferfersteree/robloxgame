from spearlib import *

NAME = 'SP_01_stick'
N = 1
BG = '#d9ecc8'        # meadow
GROUND = '#a8cf86'
TIP = 9.25
TRAIL = 5.2


def mats():
    return dict(
        wood=toon('st_wood', '#b8763f', '#7a4424', '#dca06a'),
        wood_dk=toon('st_wood_dk', '#8a5530', '#5a321c', '#b37a4a'),
        leather=toon('st_leather', '#d9a25a', '#9b6531', '#f2c98a'),
        cord=toon('st_cord', '#e9d9b0', '#b39a72', '#fff3d6', spec=0.2),
        flint=toon('st_flint', '#8b93a0', '#4f5566', '#c0c7d0', spec=0.5),
        flint_lt=toon('st_flint_lt', '#c9ccd2', '#8a8f9c', '#eef0f3', spec=0.5),
        ochre=toon('st_ochre', '#e0543a', '#a3302a', '#ff8a66'),
        bone=toon('st_bone', '#f3e7c8', '#c4ae86', '#fffaf0'),
        teal=toon('st_teal', '#33b7a6', '#1d7a78', '#7fe3d2'),
        stone=toon('st_stone', '#9a9184', '#655c55', '#c8beb0'),
    )


def knapped(z0, z1, wmax, wbase, peak=0.28, n=9, notch=0.08):
    """leaf outline with a knapped (scalloped) edge, in XZ"""
    right, left = [], []
    for i in range(n + 1):
        t = i / n
        if t < peak:
            w = wbase + (wmax - wbase) * math.sin(0.5 * math.pi * t / peak)
        else:
            u = (t - peak) / (1 - peak)
            w = wmax * (1 - u ** 1.35)
        z = z0 + (z1 - z0) * t
        sc = 1 - notch * (i % 2) if 0 < i < n else 1
        right.append((w * sc, z))
        left.append((-w * (1 - notch * ((i + 1) % 2)) if 0 < i < n else -w, z))
    pts = right[:-1] + [(0, z1)] + left[-2:0:-1] + [left[0]]
    return pts


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    wood, wood_dk, leather, cord, flint, flint_lt, ochre, bone, teal, stone = (M[k] for k in (
        'wood', 'wood_dk', 'leather', 'cord', 'flint', 'flint_lt', 'ochre', 'bone', 'teal', 'stone'))
    # ---- tail
    rock('pommel', 0.27, stone, seed=3, sub=2, rough=0.12, loc=(0, 0, 0.26), scale=(1, 1, 0.85))
    lathe('butt_knob', [(0.32, 0), (0.32, 0.17), (0.4, 0.2), (0.55, 0.19), (0.66, 0.155), (0.66, 0)], wood_dk, 14)
    coil('butt_wrap', 0.175, 0.03, 0.68, 1.05, 4, leather, segs=5)
    torus('butt_band', 0.17, 0.035, ochre, 14, 6, loc=(0, 0, 1.12))
    # ---- shaft (grip zone 2.0-3.0 is bare wood, r 0.15)
    rod('shaft_lo', 0.155, 0.6, 3.3, wood, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.55, wood, r1=0.14)
    sphere('knot_a', 0.07, wood_dk, 8, 5, loc=(0.13, 0.02, 4.1), scale=(0.7, 1, 1.3))
    sphere('knot_b', 0.06, wood_dk, 8, 5, loc=(-0.12, -0.06, 1.55), scale=(0.7, 1, 1.3))
    coil('wrap_lo', 0.18, 0.032, 1.35, 1.92, 5, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, leather, 14, 6, loc=(0, 0, 1.94))
    coil('wrap_hi', 0.175, 0.032, 3.08, 3.62, 5, leather, segs=6, phase=1.0)
    torus('wrap_hi_cap', 0.175, 0.04, leather, 14, 6, loc=(0, 0, 3.06))
    for i, z in enumerate((4.55, 4.75, 4.95)):
        torus('ochre_band_%d' % i, 0.148, 0.022 if i != 1 else 0.032, ochre if i != 1 else bone, 14, 5, loc=(0, 0, z), ol=0.015)
    # ---- socket: swollen split end + rawhide lashing
    lathe('socket', [(6.3, 0.14), (6.45, 0.17), (6.7, 0.2), (6.95, 0.19), (7.05, 0.15), (7.05, 0)], wood, 14)
    coil('lash', 0.205, 0.035, 6.42, 6.98, 6, cord, segs=5)
    for s in (-1, 1):
        tube('lash_x%d' % (s + 1), [(-0.2, s * 0.13, 6.95), (0.0, s * 0.11, 7.15), (0.2, s * 0.13, 7.38)], 0.03, cord, 6)
    sphere('lash_knot', 0.07, cord, 8, 5, loc=(0.2, 0.06, 6.5))
    # ---- flint head: knapped body + lighter ridge layer + knap scars
    blade('head', knapped(6.8, TIP, 0.64, 0.28, notch=0.13), 0.16, flint)
    blade('head_core', [(x * 0.55, 6.95 + (z - 6.85) * 0.8) for (x, z) in knapped(6.8, TIP, 0.64, 0.28, notch=0)], 0.19, flint_lt, ol=0.015)
    rnd = random.Random(11)
    for i in range(4):
        z = 7.4 + i * 0.38
        side = -1 if i % 2 else 1
        rock('scar_%d' % i, 0.07, flint_lt, seed=i + 5, sub=1, rough=0.15, flat=True,
             loc=(side * (0.3 - i * 0.05), side * 0.09, z), scale=(1.3, 0.35, 0.9), ol=0.01)
    # ---- charm: cord with beads, tooth and two feathers
    pts = [(0.19, 0.03, 6.55), (0.33, 0.06, 6.3), (0.4, 0.07, 5.95), (0.42, 0.08, 5.7)]
    tube('charm_cord', pts, 0.022, cord, 5)
    for i, (z, m) in enumerate(((6.32, ochre), (6.12, teal), (5.95, bone))):
        sphere('bead_%d' % i, 0.065, m, 8, 5, loc=(0.35 + i * 0.03, 0.065, z), ol=0.012)
    cone('tooth', 0.07, 0.3, bone, 6, loc=(0.42, 0.08, 5.72), rot=(180, 12, 0), ol=0.015)
    leaf('feather_a', 0.85, 0.24, ochre, 0.03, 6, loc=(0.42, 0.06, 5.75), rot=(0, 78, 15), ol=0.015)
    leaf('feather_b', 0.7, 0.2, bone, 0.03, 6, loc=(0.45, 0.1, 5.78), rot=(0, 100, -20), ol=0.015)
    tube('feather_a_quill', [(0.42, 0.04, 5.75), (0.37, 0.04, 4.95)], [0.018, 0.008], wood_dk, 4, ol=0.0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(101)
    dust = ghost('st_dust', '#f1dfb8', 1.1, 0.85, 1.1)
    dust_dk = ghost('st_dust_dk', '#c99f6c', 1.0, 0.85, 1.1)
    glint = glow('st_glint', '#fff6d8', 2.4)
    # ---------------- idle: a few dust motes and glints around the head
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.45, 0.75)
        sphere('idle_mote_%d' % i, rnd.uniform(0.05, 0.09), dust_dk if i % 2 else dust, 8, 5,
               loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.6, 9.0)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.35, 0.6), -0.2, 7.3 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: dust puffs + tumbling pebbles + air rings, 1 s loop
    fx('flight')
    puffs = [sphere('fl_puff_%d' % i, 0.36, dust if i % 3 else dust_dk, 12, 7) for i in range(12)]
    jit = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(puffs, lambda t, i: (jit[i][0] * (0.15 + 0.9 * t), jit[i][1] * (0.15 + 0.9 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    peb = [rock('fl_pebble_%d' % i, 0.09, M['stone'] if i % 2 else M['wood_dk'], seed=i, sub=1, rough=0.2, flat=True) for i in range(7)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(7)]
    stream(peb, lambda t, i: (pj[i][0] * (0.3 + 0.8 * t), pj[i][1] * (0.3 + 0.8 * t), 8.4 - 13.5 * t),
           smax=1.0, spin=lambda t, i: (pj[i][2] + 720 * t, 540 * t, 0))
    ring_m = glow('st_airring', '#fff2d2', 1.6)
    rings = [torus('fl_ring_%d' % i, 0.45, 0.035, ring_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: crater, cracks, dust burst, clods
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    crater = torus('im_crater', 0.55, 0.16, M['wood_dk'], 18, 6, loc=(0.35, 0, 0.0), scale=(1, 1, 0.45))
    key(crater, IMPACT0, scale=0)
    key(crater, f, scale=0)
    key(crater, f + 3, scale=(1.15, 1.15, 0.5))
    key(crater, f + 6, scale=(1, 1, 0.45))
    key(crater, IMPACT0 + 40, scale=(1, 1, 0.45))
    key(crater, IMPACT0 + 44, scale=0)
    tidy(crater, 'impact')
    for i in range(6):
        a = math.radians(i * 60 + 15)
        L_ = rnd.uniform(0.9, 1.5)
        pts = [(0.35 + 0.5 * math.cos(a), 0.5 * math.sin(a), 0.01), (0.35 + (0.5 + L_ * 0.5) * math.cos(a + 0.15), (0.5 + L_ * 0.5) * math.sin(a + 0.15), 0.01),
               (0.35 + (0.5 + L_) * math.cos(a - 0.05), (0.5 + L_) * math.sin(a - 0.05), 0.01)]
        cr = tube('im_crack_%d' % i, pts, [0.06, 0.045, 0.0], M['wood_dk'], 4, ol=0, scale=(1, 1, 1))
        cr.scale = (1, 1, 0.3)
        key(cr, IMPACT0, scale=0)
        key(cr, f, scale=0)
        key(cr, f + 4, scale=(1, 1, 0.3))
        key(cr, IMPACT0 + 40, scale=(1, 1, 0.3))
        key(cr, IMPACT0 + 44, scale=0)
        tidy(cr, 'impact')
    shock = torus('im_shock', 0.5, 0.05, glow('st_shock', '#fff0cc', 1.6), 32, 5, loc=(0.35, 0, 0.06))
    key(shock, IMPACT0, scale=0, alpha=1)
    key(shock, f, scale=0.3, alpha=1)
    key(shock, f + 12, scale=5.0, alpha=0)
    tidy(shock, 'impact', interp='LINEAR')
    ease_keys(shock)
    for i in range(14):
        a = math.radians(i * 360 / 14 + rnd.uniform(-10, 10))
        rr = rnd.uniform(1.4, 2.6) * (1.3 if math.cos(a) < 0 else 1.0)
        p = sphere('im_dust_%d' % i, 0.35, dust if i % 3 else dust_dk, 12, 7)
        end = (0.35 + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.9))
        key(p, IMPACT0, loc=(0.35, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(0.35, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.4, 2.0), alpha=0.9)
        key(p, IMPACT0 + 44, loc=(end[0], end[1], end[2] + 0.5), scale=rnd.uniform(2.2, 2.8), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    g = -0.028
    for i in range(12):
        a = math.radians(rnd.uniform(0, 360))
        sp = rnd.uniform(0.08, 0.17)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.2, 0.34)))
        m = M['wood_dk'] if i % 3 else M['stone']
        c = rock('im_clod_%d' % i, rnd.uniform(0.09, 0.17), m, seed=i + 20, sub=1, rough=0.25, flat=True)
        p0 = Vector((0.35, 0, 0.15))
        key(c, IMPACT0, loc=p0, scale=0)
        key(c, f, loc=p0, scale=0.2)
        t = 0
        rot0 = rnd.uniform(0, 360)
        while True:
            t += 2
            p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
            if p.z <= 0.05 or t > 34:
                p.z = 0.05
                key(c, f + t, loc=p, scale=1, rot=(rot0 + t * 25, t * 18, 0), interp='LINEAR')
                break
            key(c, f + t, loc=p, scale=1, rot=(rot0 + t * 25, t * 18, 0), interp='LINEAR')
        land = f + t
        p2 = p + Vector((v.x * 3, v.y * 3, 0))
        key(c, land + 4, loc=(p2.x, p2.y, 0.12), rot=(rot0 + t * 25 + 60, t * 18, 0))
        key(c, land + 7, loc=(p2.x * 1.02, p2.y * 1.02, 0.05))
        key(c, max(land + 8, IMPACT0 + 38), scale=1)
        key(c, IMPACT0 + 44, scale=0)
        tidy(c, 'impact')
    return True
