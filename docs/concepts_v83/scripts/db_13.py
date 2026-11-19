from gymlib import *

BG = '#0b3a36'
NAME = 'DB_13_Jade'


def mats():
    return dict(
        jade=toon('jade_green', '#1fb56a', shade='#0a5a3a', light='#7dffb8', spec=1.0),
        jade_dk=toon('jade_deep', '#0f7a4c', shade='#053a2a', light='#4fd890', spec=0.8),
        gold=toon('gold', '#ffcf4d', shade='#c2742a', light='#fff2a6', spec=1.0),
        red=toon('jade_red', '#d42a3a', shade='#7a1228', light='#ff7a86', spec=0.8),
        pearl=toon('jade_pearl', '#fdf6ee', shade='#c8b8e0', light='#ffffff', spec=1.0, rim=0.8),
        wisp=glow('jade_wisp', '#7dffc0', 2.6),
        eye=glow('jade_eye', '#fff2a0', 3.0),
    )


def dragon_pts(s, n=28):
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = math.radians(0 + 450 * t)
        R = 0.93 + 0.5 * max(0.0, (0.2 - t) / 0.2) ** 2
        pts.append((s * (0.78 + 1.2 * t), R * math.cos(ang), R * math.sin(ang)))
    return pts


def build():
    begin(NAME, ol=0.03)
    M = mats()
    jade, jade_dk, gold, red, pearl = (M[k] for k in ('jade', 'jade_dk', 'gold', 'red', 'pearl'))
    eye = M['eye']
    cyl('handle', 0.15, 1.5, jade_dk, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.45, 0.45, 4, gold, segs=5, steps=10, ol=0.012)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        torus('grip_end_' + n, 0.17, 0.045, gold, 12, 6, loc=(s * 0.54, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.24), (0.68, 0.3), (0.86, 0.48), (0.92, 0.48), (0.92, 0)], gold, 12, scale=(s, 1, 1))
        lathe('drum_' + n, [(0.92, 0), (0.92, 0.7), (1.0, 0.82), (1.4, 0.86), (1.48, 0.72), (1.55, 0.72), (1.62, 0.86), (2.02, 0.82), (2.1, 0.7), (2.1, 0)],
              jade, 16, scale=(s, 1, 1))
        for j, x in enumerate((1.0, 1.515, 2.04)):
            lathe('rim_%s%d' % (n, j), [(-0.07, 0.72 if j == 1 else 0.76), (-0.05, 0.9 if j != 1 else 0.82), (0.05, 0.9 if j != 1 else 0.82), (0.07, 0.72 if j == 1 else 0.76)],
                  gold, 14, loc=(s * x, 0, 0), caps=False, ol=0.025)
        lathe('cap_' + n, [(2.08, 0), (2.08, 0.62), (2.2, 0.6), (2.3, 0.4), (2.34, 0)], jade_dk, 12, scale=(s, 1, 1))
        # gold cloud scroll emblem + pearl on the end face
        for i, (y, z, R) in enumerate(((-0.2, -0.05, 0.13), (0.2, -0.05, 0.13), (0.0, 0.18, 0.15))):
            torus('scroll_%s%d' % (n, i), R, 0.035, gold, 10, 4, 'X', loc=(s * 2.3, y, z), ol=0.015)
        sphere('pearl_' + n, 0.1, pearl, 8, 5, loc=(s * 2.33, 0, 0.0), ol=0.02)
        # dragon coiling around the drum
        pts = dragon_pts(s)
        rad = [0.02 + 0.13 * math.sin(math.pi / 2 * i / 28) ** 0.8 for i in range(29)]
        tube('dragon_body_' + n, pts, rad, gold, 8)
        for i in range(4, 27, 4):
            p = Vector(pts[i])
            d = Vector((0, p.y, p.z)).normalized()
            cone('dragon_fin_%s%d' % (n, i), 0.07, 0.24, gold, 5, loc=p + d * 0.08, rot=aim(d + Vector((s * 0.3, 0, 0))), ol=0.015)
        hx, hz = s * 1.95, 1.02
        box('dragon_head_' + n, (0.4, 0.3, 0.24), gold, bev=0.07, loc=(hx, 0, hz))
        box('dragon_snout_' + n, (0.22, 0.26, 0.16), gold, bev=0.05, loc=(hx + s * 0.26, 0, hz - 0.03))
        box('dragon_jaw_' + n, (0.3, 0.22, 0.07), gold, bev=0.025, bsegs=1, loc=(hx + s * 0.18, 0, hz - 0.16))
        for e in (-1, 1):
            m = 'a' if e < 0 else 'b'
            sphere('dragon_eye_%s%s' % (n, m), 0.05, eye, 6, 4, loc=(hx + s * 0.08, e * 0.15, hz + 0.1), ol=0.01)
            cone('dragon_horn_%s%s' % (n, m), 0.07, 0.5, gold, 6, loc=(hx - s * 0.1, e * 0.1, hz + 0.1), rot=aim((-s * 0.55, e * 0.25, 1.0)), ol=0.02)
            tube('dragon_whisker_%s%s' % (n, m), [(hx + s * 0.34, e * 0.08, hz - 0.02), (hx + s * 0.42, e * 0.3, hz - 0.08), (hx + s * 0.3, e * 0.55, hz - 0.2), (hx + s * 0.15, e * 0.62, hz - 0.1)],
                 [0.03, 0.025, 0.018, 0.0], gold, segs=4)
        # red tassel hanging under the head
        sphere('tassel_knot_' + n, 0.1, red, 8, 5, loc=(s * 1.55, 0, -0.9), ol=0.02)
        for i, y in enumerate((-0.06, 0.0, 0.06)):
            tube('tassel_cord_%s%d' % (n, i), [(s * 1.55, y, -0.95), (s * 1.55, y * 2, -1.17)], [0.04, 0.0], red, segs=5)
        # jade-set gold studs on the rims

    # ---------------- FX
    fx(True)
    rnd = random.Random(13)
    petal = toon('jade_petal', '#ff9ec4', shade='#e0568c', light='#ffd6e6', spec=0.3)
    gsp = glow('jade_sparkle', '#ffe27a', 2.6)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_aura_' + n, 1.5, ghost('jade_aura', '#5dffa8', 1.1, 0.12), 16, 10, loc=(s * 1.55, 0, 0), scale=(1.3, 1, 1))
        torus('fx_halo_' + n, 1.25, 0.022, glow('jade_halo', '#ffd75a', 2.2), 28, 4, loc=(s * 1.55, 0, 0))
        for k in range(5):
            a = 2 * math.pi * k / 5 + 0.5 * s
            R = 1.1 + 0.15 * (k % 2)
            x0 = s * (1.0 + 0.3 * k)
            head = (x0, R * math.cos(a), R * math.sin(a) * 0.9)
            tail = [head, (x0 - s * 0.2, head[1] * 1.05 + 0.15, head[2] - 0.15), (x0 - s * 0.35, head[1] + 0.25, head[2] - 0.35), (x0 - s * 0.5, head[1] + 0.1, head[2] - 0.6)]
            sphere('fx_wisp_%s%d' % (n, k), 0.09, M['wisp'], 8, 5, loc=head)
            tube('fx_wisp_tail_%s%d' % (n, k), tail, [0.07, 0.055, 0.03, 0.0], M['wisp'], segs=5)
        for k in range(6):
            a = rnd.uniform(0, 360)
            R = rnd.uniform(1.0, 1.35)
            leaf('fx_petal_%s%d' % (n, k), 0.28, 0.16, petal, 0.03, 5, loc=(s * rnd.uniform(0.9, 2.3), R * math.cos(math.radians(a)), R * math.sin(math.radians(a))),
                 rot=(rnd.uniform(0, 180), rnd.uniform(0, 180), rnd.uniform(0, 360)))
        for k in range(5):
            star('fx_sparkle_%s%d' % (n, k), rnd.uniform(0.08, 0.14), 0.025, 4, 0.02, gsp,
                 loc=(s * rnd.uniform(0.8, 2.4), -rnd.uniform(0.9, 1.3), rnd.uniform(-0.9, 1.3)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    return stats(NAME)
