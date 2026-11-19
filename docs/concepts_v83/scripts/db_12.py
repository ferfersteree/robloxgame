from gymlib import *

BG = '#2a3550'
NAME = 'DB_12_Storm'


def mats():
    return dict(
        steel=toon('storm_steel', '#2d4672', shade='#111c3a', light='#6a92c8', spec=0.9),
        steel2=toon('storm_steel_lt', '#4b6b9e', shade='#1d2f58', light='#9cc0ea', spec=0.9),
        dark=toon('storm_dark', '#1a2340', shade='#0a0f22', light='#3a4a78', spec=0.3),
        bolt=toon('storm_yellow', '#ffd92e', shade='#d08a12', light='#fff7a0', spec=1.0, emit=0.3),
        copper=toon('storm_copper', '#d2773c', shade='#7a301a', light='#ffbb82', spec=1.0),
        cloud=toon('storm_cloud', '#e6ebf5', shade='#8c97b6', light='#ffffff', spec=0.2),
        node=glow('storm_node', '#9ff6ff', 3.0),
        silver=toon('silver', '#dfe6f7', shade='#7f86c4', light='#ffffff', spec=1.0),
    )


def seg_yz(name, a, b, w, th, mat, x, **kw):
    """flat bar in the YZ plane (faces +-X) from a=(y,z) to b=(y,z)"""
    dy, dz = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dy, dz)
    return box(name, (th, w, ln + w * 0.5), mat, bev=0.02, bsegs=1, loc=(x, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2),
               rot=(math.degrees(math.atan2(-dy, dz)), 0, 0), ol=0.015, **kw)


def seg_xz(name, a, b, w, th, mat, y, **kw):
    """flat bar in the XZ plane (faces +-Y) from a=(x,z) to b=(x,z)"""
    dx, dz = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dz)
    return box(name, (w, th, ln + w * 0.5), mat, bev=0.02, bsegs=1, loc=((a[0] + b[0]) / 2, y, (a[1] + b[1]) / 2),
               rot=(0, math.degrees(math.atan2(dx, dz)), 0), ol=0.015, **kw)


def build():
    begin(NAME, ol=0.03)
    M = mats()
    steel, steel2, dark, bolt_y, copper, cloud, node, silver = (M[k] for k in ('steel', 'steel2', 'dark', 'bolt', 'copper', 'cloud', 'node', 'silver'))
    cyl('handle', 0.15, 1.5, dark, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.45, 0.45, 4, copper, segs=5, steps=10, ol=0.012)
    tips = {}
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        torus('grip_end_' + n, 0.17, 0.045, bolt_y, 12, 6, loc=(s * 0.54, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.26), (0.66, 0.3), (0.8, 0.46), (0.86, 0.46), (0.86, 0)], steel2, 12, scale=(s, 1, 1))
        lathe('drum_in_' + n, [(0.86, 0), (0.86, 0.62), (0.94, 0.76), (1.5, 0.8), (1.58, 0.7), (1.58, 0)], steel, 14, scale=(s, 1, 1))
        lathe('drum_out_' + n, [(1.6, 0), (1.6, 0.66), (1.68, 0.74), (2.15, 0.74), (2.24, 0.6), (2.24, 0)], steel2, 14, scale=(s, 1, 1))
        lathe('cap_' + n, [(2.2, 0), (2.2, 0.5), (2.27, 0.52), (2.31, 0.4), (2.31, 0)], copper, 12, scale=(s, 1, 1))
        # copper tesla coils wrapped on the drums
        coil('coil_in_' + n, 0.82, 0.05, s * 0.96, s * 1.5, 3, copper, segs=5, steps=8)
        coil('coil_out_' + n, 0.76, 0.05, s * 1.72, s * 2.12, 3, copper, segs=5, steps=8)
        torus('ring_a_' + n, 0.78, 0.06, silver, 14, 5, loc=(s * 1.59, 0, 0), ol=0.02)
        torus('ring_b_' + n, 0.66, 0.05, bolt_y, 14, 5, loc=(s * 2.22, 0, 0), ol=0.02)
        # glowing conductor nodes between the drums
        for k in range(4):
            d = radial(s, 90, k * 90 + 45)
            sphere('node_%s%d' % (n, k), 0.075, node, 6, 4, loc=Vector((s * 1.59, 0, 0)) + d * 0.84, ol=0.015)
        # lightning bolt_y emblem on the end cap
        xe = s * 2.31
        pts = [(0.12, 0.34), (-0.08, 0.02), (0.1, -0.02), (-0.1, -0.34)]
        for i in range(3):
            seg_yz('emblem_%s%d' % (n, i), pts[i], pts[i + 1], 0.1, 0.04, bolt_y, xe)
        # tesla prongs
        for k in range(4):
            ang = k * 90 + 45
            d = radial(s, 62, ang)
            base = Vector((s * 1.7, 0, 0)) + radial(s, 90, ang) * 0.66
            cone('prong_%s%d' % (n, k), 0.075, 0.75, copper, 6, loc=base, rot=aim(d), ol=0.02)
            tip = base + d * 0.75
            sphere('prong_tip_%s%d' % (n, k), 0.075, node, 6, 4, loc=tip, ol=0.015)
            tips[(s, k)] = tip
        # bolt_y-shaped fins (top big, bottom small)
        fin_t = [(1.0, 0.76), (1.35, 1.0), (1.15, 1.12), (1.55, 1.45)]
        for i in range(3):
            seg_xz('fin_top_%s%d' % (n, i), (s * fin_t[i][0], fin_t[i][1]), (s * fin_t[i + 1][0], fin_t[i + 1][1]), 0.14, 0.07, bolt_y, 0)
        fin_b = [(1.0, -0.76), (1.3, -0.95), (1.15, -1.05)]
        for i in range(2):
            seg_xz('fin_bot_%s%d' % (n, i), (s * fin_b[i][0], fin_b[i][1]), (s * fin_b[i + 1][0], fin_b[i + 1][1]), 0.12, 0.07, bolt_y, 0)
        # storm cloud puffs sitting on the head
        for i, (x, y, z, r) in enumerate(((1.95, -0.05, 0.84, 0.17), (2.12, 0.1, 0.8, 0.14), (1.8, 0.12, 0.82, 0.12))):
            sphere('puff_%s%d' % (n, i), r, cloud, 8, 5, loc=(s * x, y, z), ol=0.02)

    # ---------------- FX
    fx(True)
    rnd = random.Random(12)
    bolt_m = glow('storm_bolt', '#e8ffff', 3.2)
    spk = glow('storm_spark', '#fff3a0', 2.8)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        for k in range(4):
            bolt('fx_arc_%s%d' % (n, k), tips[(s, k)], tips[(s, (k + 1) % 4)], bolt_m, r=0.035, n=5, amp=0.14, seed=5 + k + 7 * s)
        bolt('fx_arc_x_' + n, tips[(s, 0)], tips[(s, 2)], bolt_m, r=0.03, n=6, amp=0.16, seed=31 + s)
        sphere('fx_aura_' + n, 1.5, ghost('storm_aura', '#8ff0ff', 1.0, 0.1), 16, 10, loc=(s * 1.55, 0, 0), scale=(1.25, 1, 1))
        for i in range(10):
            a = 2 * math.pi * i / 10 + 0.3 * s
            r = 1.15 + 0.1 * (i % 3)
            star('fx_spark_%s%d' % (n, i), rnd.uniform(0.08, 0.14), 0.03, 4, 0.02, spk,
                 loc=(s * (1.7 + 0.55 * math.sin(i * 1.7)), r * math.cos(a), r * math.sin(a)), rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
        for i, (x, y, z, r) in enumerate(((1.4, -0.9, 0.9, 0.3), (2.0, 0.8, 0.95, 0.25), (1.0, 0.9, -0.6, 0.22))):
            sphere('fx_cloud_%s%d' % (n, i), r, ghost('storm_cloudghost', '#d8e6ff', 0.9, 0.12), 10, 6, loc=(s * x, y, z))
    fx(False)
    return stats(NAME)
