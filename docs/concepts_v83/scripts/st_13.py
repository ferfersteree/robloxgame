from gymlib import *
import db_13

NAME = 'ST_13_Jade'
T = 1.3


def build():
    begin(NAME, ol=0.04)
    M = db_13.mats()
    jade, jade_dk, gold, red, pearl, wisp, eye = (M[k] for k in ('jade', 'jade_dk', 'gold', 'red', 'pearl', 'wisp', 'eye'))
    s = stats(db_13.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    W = min(10.75, max(10.0, 2 * (cx + half) + 1.2))
    pt = min(4.42, max(4.3, top + 0.45))     # pillar top
    rnd = random.Random(1313)

    # ---- base, deck, sign
    box('base', (W - 0.6, 2.6, T - 0.3), jade_dk, bev=0.08, loc=(0, 0, (T - 0.3) / 2))
    box('foot', (W - 0.3, 2.8, 0.2), gold, bev=0.05, loc=(0, 0, 0.1))
    box('deck', (W, 3.0, 0.3), jade, bev=0.07, loc=(0, 0, T - 0.15))
    box('deck_trim', (W + 0.06, 0.08, 0.12), gold, bev=0.03, bsegs=1, loc=(0, -1.5, T - 0.1), ol=0.02)
    box('sign_frame', (5.5, 0.1, 1.0), gold, bev=0.06, loc=(0, -1.33, 0.7))
    box('sign_plaque', (5.3, 0.12, 0.84), jade_dk, bev=0.05, loc=(0, -1.38, 0.7), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, gold, loc=(0, -1.47, 0.7), rot=(90, 0, 0))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        x0 = sx * (W / 2 - 1.1)
        for i, (dx, z, R) in enumerate(((-0.25, 0.55, 0.16), (0.1, 0.8, 0.2), (0.3, 0.5, 0.14))):
            torus('base_scroll_%s%d' % (n, i), R, 0.04, gold, 12, 4, 'Y', loc=(x0 + dx, -1.33, z), ol=0.015)

    # ---- pillars with dragons
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('F' if sy < 0 else 'B')
            x, y = sx * (W / 2 - 0.45), sy * 1.05
            box('pil_plinth_' + n, (0.75, 0.75, 0.3), jade_dk, bev=0.06, loc=(x, y, T + 0.15))
            cyl('pil_col_' + n, 0.2, pt - T - 0.5, red, segs=10, bev=0.03, axis='Z', loc=(x, y, (pt + T + 0.3) / 2 - 0.1))
            torus('pil_band_lo_' + n, 0.22, 0.05, gold, 10, 5, 'Z', loc=(x, y, T + 0.45), ol=0.02)
            torus('pil_band_hi_' + n, 0.22, 0.05, gold, 10, 5, 'Z', loc=(x, y, pt - 0.35), ol=0.02)
            box('pil_cap_' + n, (0.62, 0.62, 0.2), gold, bev=0.05, loc=(x, y, pt - 0.1))
            if sy < 0:
                pts = []
                nn = 18
                for i in range(nn + 1):
                    t = i / nn
                    a = 2 * math.pi * 1.5 * t + (0 if sx < 0 else math.pi)
                    pts.append((x + 0.25 * math.cos(a), y + 0.25 * math.sin(a), T + 0.55 + (pt - T - 1.1) * t))
                tube('pil_dragon_' + n, pts, [0.03 + 0.07 * t / nn for t in range(nn + 1)], gold, 6)
                hp = (x, y - 0.2, pt - 0.45)
                box('pil_dhead_' + n, (0.3, 0.3, 0.22), gold, bev=0.06, loc=hp)
                for e in (-1, 1):
                    cone('pil_dhorn_%s%d' % (n, e), 0.05, 0.3, gold, 5, loc=(hp[0] + e * 0.08, hp[1], hp[2] + 0.1), rot=aim((e * 0.5, -0.2, 1)), ol=0.015)

    # ---- pavilion roof with upturned eaves
    hx, hy = (W - 0.2) / 2, 1.5
    box('roof_slab', (W - 0.2, 3.0, 0.2), gold, bev=0.05, loc=(0, 0, pt + 0.1))
    box('roof_fascia', (W - 0.5, 2.7, 0.14), jade_dk, bev=0.04, loc=(0, 0, pt - 0.03))
    R = (hx - 0.1) / 0.7071
    z0 = pt + 0.2
    roof = lathe('roof', [(z0, 0), (z0, R), (z0 + 0.1, R * 0.94), (z0 + 0.28, R * 0.62), (z0 + 0.48, R * 0.3), (z0 + 0.62, R * 0.1), (z0 + 0.66, 0)],
                 jade, 4, 'Z')
    roof.data.transform(Matrix.Rotation(math.radians(45), 4, 'Z'))
    roof.data.transform(Matrix.Diagonal((1.0, (hy - 0.1) / (hx - 0.1), 1.0, 1.0)))
    sphere('roof_finial', 0.09, pearl, 8, 5, loc=(0, 0, z0 + 0.72), ol=0.02)
    tube('roof_ridge', [(-hx + 0.8, 0, z0 + 0.28), (0, 0, z0 + 0.7), (hx - 0.8, 0, z0 + 0.28)], [0.05, 0.08, 0.05], gold, segs=5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('F' if sy < 0 else 'B')
            pts = [(sx * (hx - 0.1), sy * (hy - 0.1), pt + 0.15), (sx * (hx + 0.1), sy * (hy - 0.05), pt + 0.25),
                   (sx * (hx + 0.3), sy * (hy - 0.02), pt + 0.45), (sx * (hx + 0.4), sy * (hy - 0.02), pt + 0.75)]
            tube('eave_' + n, pts, [0.15, 0.12, 0.09, 0.0], gold, 6)
        # hanging lanterns at the front corners
        n = 'L' if sx < 0 else 'R'
        lx, ly = sx * (W / 2 - 0.45), -1.3
        tube('lantern_cord_' + n, [(lx, ly, pt), (lx, ly, pt - 0.5)], 0.02, gold, segs=4)
        sphere('lantern_body_' + n, 0.26, red, 10, 6, loc=(lx, ly, pt - 0.8), scale=(1, 1, 1.2))
        box('lantern_cap_' + n, (0.3, 0.3, 0.07), gold, bev=0.02, bsegs=1, loc=(lx, ly, pt - 0.52), ol=0.015)
        box('lantern_base_' + n, (0.3, 0.3, 0.07), gold, bev=0.02, bsegs=1, loc=(lx, ly, pt - 1.1), ol=0.015)
        tube('lantern_tassel_' + n, [(lx, ly, pt - 1.12), (lx, ly, pt - 1.45)], [0.05, 0.0], red, segs=5)

    # ---- moon gate behind the pair + floor petals
    zc = hz + 0.15
    torus('moon_gate', 1.75, 0.09, gold, 28, 5, 'Y', loc=(0, 1.3, zc))
    torus('moon_gate_in', 1.55, 0.05, jade, 24, 4, 'Y', loc=(0, 1.3, zc), ol=0.02)
    sphere('moon_pearl', 0.14, pearl, 8, 5, loc=(0, 1.3, zc + 1.75), ol=0.02)
    petal = toon('jade_petal', '#ff9ec4', shade='#e0568c', light='#ffd6e6', spec=0.3)
    for i in range(8):
        leaf('floor_petal_%d' % i, 0.22, 0.12, petal, 0.02, 4, loc=(rnd.uniform(-W / 2 + 0.8, W / 2 - 0.8), rnd.uniform(-1.25, 1.2), T + 0.02),
             rot=(0, 0, rnd.uniform(0, 360)), ol=0.01)

    # ---- dragon-claw cradles
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        X = sx * cx
        for e in (-1, 1):
            m = 'a' if e < 0 else 'b'
            px = X + e * 0.42
            ztop = hz - 0.22
            box('cr_plate_%s%s' % (n, m), (0.6, 0.7, 0.1), gold, bev=0.03, loc=(px, 0, T + 0.05))
            box('cr_post_%s%s' % (n, m), (0.3, 0.36, ztop - T - 0.1), jade, bev=0.05, loc=(px, 0, (ztop + T + 0.1) / 2))
            torus('cr_band_%s%s' % (n, m), 0.22, 0.04, gold, 8, 4, 'Z', loc=(px, 0, T + 0.5), ol=0.015)
            box('cr_saddle_%s%s' % (n, m), (0.34, 0.56, 0.12), gold, bev=0.04, loc=(px, 0, hz - 0.2))
            for f in (-1, 1):
                cone('cr_claw_%s%s%d' % (n, m, f), 0.06, 0.34, gold, 5, loc=(px, f * 0.25, hz - 0.15), rot=aim((0, -f * 0.25, 1)), ol=0.015)

    fx(True)
    wisp_m = glow('jade_wisp', '#7dffc0', 2.6)
    gsp = glow('jade_sparkle', '#ffe27a', 2.6)
    sphere('fx_aura', 3.3, ghost('jade_aura', '#5dffa8', 1.1, 0.12), 18, 10, loc=(0, 0.4, hz + 0.3), scale=(1.6, 0.6, 0.7))
    torus('fx_halo', 1.95, 0.022, glow('jade_halo', '#ffd75a', 2.2), 36, 4, 'Y', loc=(0, 1.3, zc))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        sphere('fx_lantern_glow_' + n, 0.17, glow('jade_lantern', '#ffd36a', 2.6), 8, 5, loc=(sx * (W / 2 - 0.45), -1.3, pt - 0.8))
    for k in range(10):
        x0 = rnd.uniform(-W / 2 + 0.8, W / 2 - 0.8)
        y0 = rnd.uniform(-1.2, 1.2)
        z0f = rnd.uniform(T + 0.4, pt - 0.3)
        head = (x0, y0, z0f)
        tail = [head, (x0 - 0.15, y0 + 0.1, z0f - 0.2), (x0 - 0.1, y0 + 0.2, z0f - 0.45), (x0 - 0.25, y0 + 0.15, z0f - 0.7)]
        sphere('fx_wisp_%d' % k, 0.09, wisp_m, 8, 5, loc=head)
        tube('fx_wisp_tail_%d' % k, tail, [0.07, 0.055, 0.03, 0.0], wisp_m, segs=5)
    for k in range(14):
        leaf('fx_petal_%d' % k, 0.3, 0.17, petal, 0.03, 5, loc=(rnd.uniform(-W / 2 + 0.6, W / 2 - 0.6), rnd.uniform(-1.4, 1.3), rnd.uniform(T + 0.3, pt + 0.2)),
             rot=(rnd.uniform(0, 180), rnd.uniform(0, 180), rnd.uniform(0, 360)))
    for k in range(8):
        star('fx_sparkle_%d' % k, rnd.uniform(0.1, 0.18), 0.03, 4, 0.02, gsp,
             loc=(rnd.uniform(-W / 2 + 0.6, W / 2 - 0.6), -rnd.uniform(1.2, 1.6), rnd.uniform(T + 0.5, pt)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    display(NAME, db_13.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
