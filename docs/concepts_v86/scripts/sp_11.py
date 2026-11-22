from spearlib import *

NAME = 'SP_11_amber_sting'
N = 11
BG = '#8fb46a'        # jungle
GROUND = '#6fae4e'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'honey_puddle': 'im_puddle', 'honey_comb': 'im_comb_0', 'honey_drop': 'im_drop_0',
             'hex_ring': 'fl_hex_0', 'golden_spark': 'im_spark_0'}


def mats():
    return dict(
        amber=toon('b11_amber', '#f5a623', '#b05a10', '#ffe08a', spec=1.0, rim=0.7, rimcol='#fff0b0', emit=0.5),
        amber_lt=toon('b11_amber_lt', '#ffd45a', '#d88a1a', '#fff4b8', spec=1.0, rim=0.6, rimcol='#ffffff', emit=0.7),
        amber_dk=toon('b11_amber_dk', '#c8741a', '#7a3a0c', '#f0a850', spec=0.8, emit=0.2),
        black=toon('b11_black', '#2a2018', '#100a06', '#5a4638', spec=0.4),
        yellow=toon('b11_yellow', '#ffd22a', '#c8861a', '#fff28a', spec=0.5),
        wing=toon('b11_wing', '#e8f2ff', '#9ab0d0', '#ffffff', spec=0.9),
        leaf=toon('b11_leaf', '#4ab84a', '#1e7a34', '#8ae878', spec=0.3),
        honey=glow('b11_honey', '#ffc83a', 2.2),
        spark=glow('b11_spark', '#ffe27a', 2.2),
        flash=ghost('b11_flash', '#ffd86a', 2.0, 0.6, 1.2),
        bub=ghost('b11_bub', '#ffe6a0', 1.2, 0.8, 2.0, edge=True),
    )


def spark_arc(ob, p0, v, f, g, life, rest=0.03, s=1.0):
    p0, v = Vector(p0), Vector(v)
    key(ob, IMPACT0, loc=p0, scale=0, alpha=1)
    key(ob, f - 1, loc=p0, scale=0, alpha=1)
    key(ob, f, loc=p0, scale=0.3 * s, alpha=1)
    t = 2
    while t < life:
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        if p.z < rest:
            p.z = rest
        key(ob, f + t, loc=p, scale=s, alpha=1, interp='LINEAR')
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
    amber, amber_lt, amber_dk, black, yellow, wing, leaf_m = (M[k] for k in (
        'amber', 'amber_lt', 'amber_dk', 'black', 'yellow', 'wing', 'leaf'))
    # ---- tail: amber bead with a black stinger cap
    sphere('tail_amber', 0.25, amber, 10, 6, loc=(0, 0, 0.3), scale=(1, 1, 1.1))
    lathe('tail_cap', [(0.5, 0), (0.5, 0.16), (0.62, 0.2), (0.8, 0.17), (0.92, 0.155), (0.92, 0)], black, 12)
    torus('tail_ring', 0.2, 0.045, yellow, 12, 5, loc=(0, 0, 1.0))
    # ---- shaft: black with chunky yellow wasp stripes (none in the grip zone)
    rod('shaft_lo', 0.155, 0.9, 3.3, black, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.0, black, segs=12, r1=0.14)
    coil('wrap_lo', 0.178, 0.03, 1.3, 1.85, 4, amber_dk, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, yellow, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.55, 4, amber_dk, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, yellow, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((3.85, 4.2, 4.55, 4.9, 5.25, 5.6)):
        cyl('stripe_%d' % i, 0.172, 0.2, yellow, 12, 0.03, loc=(0, 0, z), ol=0.02)
    # ---- honeycomb collar: three hexagonal rings and a black socket
    lathe('socket', [(5.9, 0.14), (6.1, 0.22), (6.35, 0.27), (6.6, 0.3), (6.75, 0.24), (6.75, 0)], black, 14)
    for i, z in enumerate((6.1, 6.35, 6.6)):
        torus('hex_ring_%d' % i, 0.3 + 0.03 * i, 0.05, yellow if i != 1 else amber, 6, 4, loc=(0, 0, z), ol=0.02)
    # ---- the amber blade: dark back layer, bright front layer, glassy core
    bl = [(0.3, 6.75), (0.52, 7.15), (0.58, 7.75), (0.46, 8.4), (0.24, 8.9), (0.0, TIP),
          (-0.24, 8.9), (-0.46, 8.4), (-0.58, 7.75), (-0.52, 7.15), (-0.3, 6.75)]
    blade('amber_back', bl, 0.17, amber_dk)
    blade('amber_front', [(x * 0.88, 6.85 + (z - 6.75) * 0.95) for (x, z) in bl], 0.2, amber, ol=0.015)
    blade('amber_core', [(x * 0.5, 7.1 + (z - 6.75) * 0.8) for (x, z) in bl], 0.23, amber_lt, ol=0.0)
    for s in (-1, 1):
        cone('sting_barb_%d' % (s + 1), 0.09, 0.5, amber, 6, loc=(s * 0.52, 0, 7.55), rot=(0, s * 140, 0), ol=0.015)
    for i, (x, z) in enumerate(((0.28, 7.3), (-0.3, 7.9), (0.22, 8.35), (-0.15, 8.65))):
        sphere('bubble_%d' % i, 0.05 + 0.01 * (i % 2), amber_lt, 7, 4, loc=(x, -0.2, z), ol=0.01)
    # ---- the trapped insect (half sunk into the front face)
    sphere('bug_body', 0.2, black, 10, 6, loc=(0, -0.16, 7.95), scale=(0.7, 0.55, 1.15), ol=0.015)
    torus('bug_stripe_a', 0.13, 0.03, yellow, 10, 4, loc=(0, -0.16, 7.9), ol=0.01)
    torus('bug_stripe_b', 0.12, 0.03, yellow, 10, 4, loc=(0, -0.16, 8.03), ol=0.01)
    sphere('bug_head', 0.1, black, 8, 5, loc=(0, -0.17, 8.28), ol=0.012)
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        leaf('bug_wing_' + nm, 0.55, 0.22, wing, 0.02, 4, loc=(s * 0.06, -0.22, 8.0), rot=(90, -50 if s > 0 else -130, 0), ol=0.01)
    # ---- charm: leaf and honey drop on a cord
    tube('charm_cord', [(0.2, 0.04, 5.95), (0.32, 0.08, 5.7), (0.36, 0.1, 5.5)], 0.02, amber_dk, 5)
    sphere('charm_drop', 0.1, amber, 8, 5, loc=(0.36, 0.1, 5.4), scale=(1, 1, 1.3), ol=0.012)
    leaf('charm_leaf', 0.4, 0.17, leaf_m, 0.02, 4, loc=(0.2, 0.05, 5.95), rot=(0, 120, 20), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1111)
    honey, spark, flash_m, bub = M['honey'], M['spark'], M['flash'], M['bub']
    # ---------------- idle: bubbles in the amber + glints
    fx('idle')
    for i in range(3):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 0.8)
        sphere('idle_bubble_%d' % i, rnd.uniform(0.06, 0.1), bub, 10, 6, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.2, 9.0)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, spark, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.7), -0.25, 7.5 + i * 0.7),
             rot=(90, 0, 0))
    for i in range(2):
        a = rnd.uniform(0, 6.28)
        sphere('idle_mote_%d' % i, 0.04, honey, 6, 4, loc=(0.65 * math.cos(a), 0.65 * math.sin(a), rnd.uniform(7.4, 9.2)))
    # ---------------- flight: honey drops, golden sparks, hex rings
    fx('flight')
    dr = [sphere('fl_drop_%d' % i, 0.14, M['amber'] if i % 2 else M['amber_lt'], 8, 5, scale=(1, 1, 1.3)) for i in range(10)]
    dj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(dr, lambda t, i: (dj[i][0] * (0.25 + 1.0 * t), dj[i][1] * (0.25 + 1.0 * t), 8.6 - 12.5 * t),
           smax=lambda t, i: (0.7 + 0.8 * t) * math.sin(math.pi * t) ** 0.5)
    sp = [sphere('fl_spark_%d' % i, 0.06, spark if i % 2 else honey, 6, 4) for i in range(10)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(sp, lambda t, i: (sj[i][0] * (0.2 + 1.4 * t), sj[i][1] * (0.2 + 1.4 * t), 8.3 - 12.0 * t), smax=1.2)
    hx = [torus('fl_hex_%d' % i, 0.5, 0.05, honey, 6, 4) for i in range(3)]
    stream(hx, lambda t, i: (0, 0, 9.4 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (0, 0, 120 * t))
    wg = [leaf('fl_wing_%d' % i, 0.45, 0.18, M['wing'], 0.02, 4, ol=0.01) for i in range(4)]
    wj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(4)]
    stream(wg, lambda t, i: (wj[i][0] * (0.3 + 0.8 * t), wj[i][1] * (0.3 + 0.8 * t), 8.0 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (wj[i][2] + 360 * t, 200 * t, 0))
    # ---------------- impact: honey droplets, a spreading puddle, seven honeycomb prisms rise, golden sparks
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.3))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.0, alpha=0.7)
    key(fl, f + 10, scale=2.8, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    rg = torus('im_ring', 0.5, 0.05, honey, 32, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 13, scale=4.6, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    pd = cyl('im_puddle', 2.0, 0.08, M['amber'], 28, 0.02, loc=(cx, 0, 0.04), ol=0.02)
    key(pd, IMPACT0, scale=0)
    key(pd, f + 1, scale=0.1)
    key(pd, f + 14, scale=1.0)
    key(pd, IMPACT0 + 38, scale=1.0)
    key(pd, IMPACT0 + 44, scale=0)
    tidy(pd, 'impact')
    ease_keys(pd)
    for i in range(5):
        a = math.radians(i * 72 + 20)
        rr = rnd.uniform(1.7, 2.2)
        bl_ = sphere('im_blob_%d' % i, 0.4, M['amber_lt'] if i % 2 else M['amber'], 10, 6, loc=(cx + rr * math.cos(a), rr * math.sin(a), 0.05), ol=0.015)
        t0 = f + 6 + i
        key(bl_, IMPACT0, scale=0)
        key(bl_, t0, scale=0)
        key(bl_, t0 + 6, scale=(1.2, 1.2, 0.25))
        key(bl_, IMPACT0 + 38, scale=(1.0, 1.0, 0.22))
        key(bl_, IMPACT0 + 44, scale=0)
        tidy(bl_, 'impact')
    # seven hexagonal prisms (a honeycomb flower) forward of the spear
    hcx = cx + 1.7
    spots = [(0.0, 0.0, 1.5)] + [(0.77 * math.cos(math.radians(30 + 60 * k)), 0.77 * math.sin(math.radians(30 + 60 * k)), 0.7 + 0.25 * (k % 3)) for k in range(6)]
    for k, (dx, dy, h) in enumerate(spots):
        pr = lathe('im_comb_%d' % k, [(0, 0), (0, 0.4), (h, 0.4), (h, 0)], M['amber_lt'] if k % 2 else M['amber'], 6,
                   loc=(hcx + dx, dy, -0.02), ol=0.02)
        t0 = f + 3 + k
        key(pr, IMPACT0, scale=0)
        key(pr, t0 - 1, scale=0)
        key(pr, t0, scale=(1, 1, 0.02))
        key(pr, t0 + 4, scale=(1.0, 1.0, 1.2))
        key(pr, t0 + 8, scale=1.0)
        key(pr, IMPACT0 + 38, scale=1.0)
        key(pr, IMPACT0 + 44, scale=0)
        tidy(pr, 'impact')
    g = -0.028
    for i in range(14):
        a = math.radians(rnd.uniform(0, 360))
        s_ = rnd.uniform(0.07, 0.16)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.22, 0.36)))
        dp = sphere('im_drop_%d' % i, rnd.uniform(0.09, 0.15), M['amber'] if i % 2 else M['amber_lt'], 8, 5)
        ballistic(dp, (cx, 0, 0.2), v, f, g, spin=(0, 0), rest=0.08)
    for i in range(14):
        a = math.radians(rnd.uniform(0, 360))
        s_ = rnd.uniform(0.05, 0.13)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.25, 0.38)))
        sk = sphere('im_spark_%d' % i, 0.06, spark if i % 2 else honey, 6, 4)
        spark_arc(sk, (cx, 0, 0.3), v, f + i % 4, g, 26, s=1.2)
    return True
