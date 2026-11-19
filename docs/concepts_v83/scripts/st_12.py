from gymlib import *
import db_12

NAME = 'ST_12_Storm'
T = 1.3


def seg_xz(name, a, b, w, th, mat, y, **kw):
    dx, dz = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dz)
    return box(name, (w, th, ln + w * 0.5), mat, bev=0.02, bsegs=1, loc=((a[0] + b[0]) / 2, y, (a[1] + b[1]) / 2),
               rot=(0, math.degrees(math.atan2(dx, dz)), 0), ol=0.015, **kw)


def build():
    begin(NAME, ol=0.04)
    M = db_12.mats()
    steel, steel2, dark, bolt_y, copper, cloud, node, silver = (M[k] for k in ('steel', 'steel2', 'dark', 'bolt', 'copper', 'cloud', 'node', 'silver'))
    s = stats(db_12.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    W = min(11.4, max(10.0, 2 * (cx + half) + 1.2))
    rnd = random.Random(1212)

    # ---- base, deck, sign
    box('base', (W - 0.6, 2.6, T - 0.3), steel, bev=0.08, loc=(0, 0, (T - 0.3) / 2))
    box('foot', (W - 0.3, 2.8, 0.2), dark, bev=0.05, loc=(0, 0, 0.1))
    box('deck', (W, 3.0, 0.3), steel2, bev=0.07, loc=(0, 0, T - 0.15))
    box('deck_trim', (W + 0.06, 0.08, 0.12), bolt_y, bev=0.03, bsegs=1, loc=(0, -1.5, T - 0.1), ol=0.02)
    box('base_glow', (W - 1.4, 0.04, 0.06), node, bev=0, loc=(0, -1.31, 0.3), ol=0)
    box('sign_frame', (5.5, 0.1, 1.0), steel2, bev=0.06, loc=(0, -1.33, 0.7))
    box('sign_plaque', (5.3, 0.12, 0.84), dark, bev=0.05, loc=(0, -1.38, 0.7), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, bolt_y, loc=(0, -1.47, 0.7), rot=(90, 0, 0))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        x0 = sx * (W / 2 - 1.1)
        pts = [(x0 - 0.3, 1.0), (x0 + 0.1, 0.78), (x0 - 0.1, 0.62), (x0 + 0.25, 0.36)]
        for i in range(3):
            seg_xz('base_bolt_%s%d' % (n, i), pts[i], pts[i + 1], 0.13, 0.06, bolt_y, -1.32)
    for i in range(4):
        sphere('deck_node_%d' % i, 0.09, node, 6, 4, loc=(-3.3 + 2.2 * i, -1.52, T - 0.05), ol=0.015)

    # ---- lightning-rod pylons
    tipsP = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('F' if sy < 0 else 'B')
            x, y = sx * (W / 2 - 0.4), sy * 1.0
            h = 4.2 if sy < 0 else 4.8
            box('pyl_base_' + n, (0.8, 0.8, 0.3), dark, bev=0.06, loc=(x, y, T + 0.15))
            cyl('pyl_pole_' + n, 0.13, h - T - 0.3, steel2, segs=8, bev=0.03, axis='Z', loc=(x, y, (h + T + 0.3) / 2))
            coil('pyl_coil_' + n, 0.19, 0.04, T + 0.45, h - 0.55, 5, copper, segs=5, steps=6, axis='Z', loc=(x, y, 0))
            torus('pyl_ring_a_' + n, 0.22, 0.05, silver, 10, 5, 'Z', loc=(x, y, T + 0.4), ol=0.02)
            torus('pyl_ring_b_' + n, 0.22, 0.05, bolt_y, 10, 5, 'Z', loc=(x, y, h - 0.45), ol=0.02)
            cone('pyl_spike_' + n, 0.1, 0.55, silver, 6, loc=(x, y, h), ol=0.02)
            sphere('pyl_node_' + n, 0.08, node, 6, 4, loc=(x, y, h + 0.58), ol=0.015)
            tipsP[(sx, sy)] = (x, y, h + 0.58)

    # ---- cloud canopy beam on the back pylons
    box('beam', (W - 0.6, 0.34, 0.26), steel, bev=0.06, loc=(0, 1.0, 4.7))
    box('beam_glow', (W - 1.4, 0.04, 0.05), node, bev=0, loc=(0, 0.81, 4.7), ol=0)
    for i in range(14):
        x = -W / 2 + 1.0 + (W - 2.0) * i / 13
        r = 0.26 + 0.12 * ((i * 7) % 4) / 3
        sphere('canopy_puff_%d' % i, r, cloud, 8, 5, loc=(x, 1.0 + 0.1 * math.sin(i * 2.1), 4.82 + r * 0.55 + 0.1 * ((i + 1) % 2)), ol=0.025)

    # ---- tesla rings behind each dumbbell
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        X = sx * cx
        R = 1.35
        zc = max(hz + 0.2, T + 0.15 + R)
        torus('tesla_ring_' + n, R, 0.08, steel2, 24, 6, 'Y', loc=(X, 1.25, zc))
        torus('tesla_ring_in_' + n, R - 0.17, 0.04, copper, 20, 5, 'Y', loc=(X, 1.25, zc), ol=0.02)
        for k in range(4):
            a = math.radians(45 + 90 * k)
            d = Vector((math.cos(a), 0, math.sin(a)))
            cone('tesla_fin_%s%d' % (n, k), 0.07, 0.3, bolt_y, 5, loc=Vector((X, 1.25, zc)) + d * (R + 0.06), rot=aim(d), ol=0.015)
        sphere('tesla_node_' + n, 0.1, node, 6, 4, loc=(X, 1.25, zc + R + 0.12), ol=0.015)

        # ---- cradles under the handle
        for e in (-1, 1):
            m = 'a' if e < 0 else 'b'
            px = X + e * 0.42
            ztop = hz - 0.22
            box('cr_plate_%s%s' % (n, m), (0.6, 0.7, 0.1), dark, bev=0.03, loc=(px, 0, T + 0.05))
            box('cr_post_%s%s' % (n, m), (0.3, 0.36, ztop - T - 0.1), steel, bev=0.05, loc=(px, 0, (ztop + T + 0.1) / 2))
            coil('cr_coil_%s%s' % (n, m), 0.2, 0.035, T + 0.15, ztop - 0.05, 3, copper, segs=4, steps=8, axis='Z', loc=(px, 0, 0))
            box('cr_saddle_%s%s' % (n, m), (0.34, 0.56, 0.12), copper, bev=0.04, loc=(px, 0, hz - 0.2))
            for f in (-1, 1):
                cone('cr_hook_%s%s%d' % (n, m, f), 0.06, 0.32, bolt_y, 5, loc=(px, f * 0.25, hz - 0.15), ol=0.015)

    fx(True)
    bolt_m = glow('storm_bolt', '#e8ffff', 3.2)
    spk = glow('storm_spark', '#fff3a0', 2.8)
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        bolt('fx_bolt_side_' + n, tipsP[(sx, -1)], tipsP[(sx, 1)], bolt_m, r=0.04, n=7, amp=0.25, seed=40 + sx)
        X = sx * cx
        zc = max(hz + 0.2, T + 0.15 + 1.35)
        bolt('fx_bolt_ring_' + n, (X, 1.25, zc + 1.5), (X, 1.0, 4.65), bolt_m, r=0.035, n=5, amp=0.15, seed=50 + sx)
        for i in range(7):
            a = 2 * math.pi * i / 7 + sx
            star('fx_spark_%s%d' % (n, i), rnd.uniform(0.08, 0.14), 0.03, 4, 0.02, spk,
                 loc=(X + 1.65 * math.cos(a), 1.2 + 0.2 * math.sin(i), zc + 1.65 * math.sin(a)), rot=(90, 0, rnd.uniform(0, 45)))
    bolt('fx_bolt_front', tipsP[(-1, -1)], tipsP[(1, -1)], bolt_m, r=0.04, n=10, amp=0.3, seed=61)
    bolt('fx_bolt_back', tipsP[(-1, 1)], tipsP[(1, 1)], bolt_m, r=0.045, n=12, amp=0.3, seed=62)
    sphere('fx_aura', 3.3, ghost('storm_aura', '#8ff0ff', 1.0, 0.1), 18, 10, loc=(0, 0.5, hz + 0.3), scale=(1.6, 0.6, 0.7))
    for i in range(5):
        sphere('fx_cloud_%d' % i, rnd.uniform(0.35, 0.55), ghost('storm_cloudghost', '#d8e6ff', 0.9, 0.12), 10, 6,
               loc=(-W / 2 + 1.5 + (W - 3) * i / 4, 1.0, 4.45), scale=(1.4, 1, 0.8))
    fx(False)
    display(NAME, db_12.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
