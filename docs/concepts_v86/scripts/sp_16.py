from spearlib import *

NAME = 'SP_16_scorpion_sting'
N = 16
BG = '#b98a5a'        # desert glare
GROUND = '#e8c88c'    # sand
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'claw': 'im_claw_0', 'venom_drop': 'im_drop_0', 'crack': 'im_crack_0', 'shock_ring': 'im_shock'}
END = IMPACT0 + 44


def mats():
    return dict(
        chitin=toon('s16_chitin', '#3b2a24', '#1c1214', '#74544a', spec=0.9, rim=0.6, rimcol='#ffb060'),
        armor=toon('s16_armor', '#b07a48', '#6e4426', '#e0a870', spec=0.6),
        amber=toon('s16_amber', '#eaa22e', '#a8601c', '#ffd878', spec=1.0, emit=0.2),
        bone=toon('s16_bone', '#f0e4c4', '#bba884', '#fffaf0', spec=0.4),
        red=toon('s16_red', '#a8381e', '#5e1a16', '#e06a44'),
        bronze=toon('s16_bronze', '#c78f3c', '#7e5018', '#f2c878', spec=1.0),
        venom=glow('s16_venom', '#9be848', 2.2),
        venom_dk=toon('s16_venom_dk', '#5ea832', '#2c6a22', '#b6ec78', spec=0.9, emit=0.3),
    )


def pop(ob, t0, s1=1.0, grow=5, hold=IMPACT0 + 38):
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
    key(ob, IMPACT0, scale=0, alpha=1)
    key(ob, t0, scale=s0, alpha=1)
    key(ob, min(t0 + dur, END), scale=s1, alpha=0)
    tidy(ob, 'impact', interp='LINEAR')
    ease_keys(ob)


def toss(c, p0, v, f, g=-0.03, zg=0.08):
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


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    chitin, armor, amber, bone, red, bronze, venom, venom_dk = (M[k] for k in (
        'chitin', 'armor', 'amber', 'bone', 'red', 'bronze', 'venom', 'venom_dk'))
    # ---- tail: spiked counterweight
    sphere('tail_ball', 0.26, chitin, 10, 6, loc=(0, 0, 0.3), scale=(1, 1, 1.15))
    for i in range(4):
        a = math.radians(i * 90 + 45)
        cone('tail_spike_%d' % i, 0.07, 0.3, bone, 6, loc=(0.2 * math.cos(a), 0.2 * math.sin(a), 0.3), rot=aim((math.cos(a), math.sin(a), 0.2)), ol=0.015)
    torus('tail_ring', 0.19, 0.045, bronze, 14, 6, loc=(0, 0, 0.7))
    # ---- shaft with armoured segment plates
    rod('shaft_lo', 0.155, 0.5, 3.3, chitin, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, chitin, r1=0.14)
    for i in range(4):
        z = 0.85 + i * 0.25
        lathe('plate_lo_%d' % i, [(z, 0.17), (z + 0.05, 0.23), (z + 0.2, 0.22), (z + 0.24, 0.17)], armor if i % 2 == 0 else red, 10, caps=False)
    torus('plate_lo_cap', 0.18, 0.04, bronze, 14, 6, loc=(0, 0, 1.93))
    torus('plate_hi_cap', 0.18, 0.04, bronze, 14, 6, loc=(0, 0, 3.07))
    for i in range(4):
        z = 3.14 + i * 0.27
        lathe('plate_hi_%d' % i, [(z, 0.17), (z + 0.05, 0.23), (z + 0.21, 0.22), (z + 0.25, 0.17)], armor if i % 2 == 0 else red, 10, caps=False)
    for i in range(3):
        sphere('rivet_%d' % i, 0.05, bronze, 7, 4, loc=(0.15 * math.cos(i * 2.1), 0.15 * math.sin(i * 2.1), 4.5 + i * 0.4), ol=0.01)
    # ---- armoured socket
    lathe('socket', [(6.1, 0.15), (6.25, 0.28), (6.5, 0.34), (6.8, 0.3), (6.9, 0.22), (6.9, 0)], armor, 12)
    torus('socket_band', 0.3, 0.045, bronze, 14, 6, loc=(0, 0, 6.3))
    torus('socket_band2', 0.3, 0.04, red, 14, 6, loc=(0, 0, 6.78))
    # ---- segmented stinger: four tail segments then the curved sting
    cs = [((0.0, 0, 7.0), 0.34), ((0.16, 0, 7.55), 0.31), ((0.3, 0, 8.05), 0.27), ((0.36, 0, 8.5), 0.22)]
    for k, (c, r) in enumerate(cs):
        sphere('seg_%d' % k, r, chitin if k % 2 == 0 else red, 10, 6, loc=c, scale=(1, 1, 1.18))
        cone('seg_spike_%d' % k, 0.06, 0.24, bone, 6, loc=(c[0] - r * 0.85, 0, c[2] + 0.04), rot=(0, -90, 0), ol=0.015)
    tube('sting', [(0.36, 0, 8.5), (0.36, 0, 8.9), (0.24, 0, TIP - 0.12), (0.06, 0, TIP)], [0.16, 0.13, 0.08, 0.0], amber, 8)
    tube('sting_core', [(0.36, 0, 8.75), (0.34, 0, 9.0), (0.2, 0, TIP - 0.2)], [0.07, 0.05, 0.0], venom, 6, ol=0)
    sphere('venom_gland', 0.1, venom, 8, 5, loc=(0.38, 0.18, 8.3), ol=0)
    # ---- pincer claws flanking the base
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        tube('claw_' + nm, [(s * 0.25, 0, 6.7), (s * 0.7, 0, 6.85), (s * 0.9, 0, 7.35), (s * 0.78, 0, 7.9), (s * 0.53, 0, 8.0)],
             [0.15, 0.14, 0.12, 0.08, 0.0], armor, 8, scale=(1, 0.7, 1))
        torus('claw_band_' + nm, 0.14, 0.035, bronze, 10, 5, loc=(s * 0.64, 0, 6.88), rot=(0, 90 - s * 18, 0), ol=0.015)
        for k in range(2):
            cone('claw_spike_%s%d' % (nm, k), 0.05, 0.22, bone, 5, loc=(s * (0.9 + 0.05 * k), 0, 7.2 + k * 0.4), rot=aim((s, 0, 0.3)), ol=0.012)
    # ---- charm: bone fang and amber bead
    tube('charm_cord', [(0.2, 0.03, 6.05), (0.34, 0.06, 5.75), (0.38, 0.07, 5.5)], 0.022, red, 5)
    sphere('charm_bead', 0.07, amber, 8, 5, loc=(0.34, 0.065, 5.78), ol=0.012)
    cone('charm_fang', 0.07, 0.3, bone, 6, loc=(0.38, 0.07, 5.5), rot=(180, 0, 0), ol=0.015)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1616)
    sandp = ghost('s16_sandp', '#f2dba8', 1.0, 0.85, 1.1)
    sandp_dk = ghost('s16_sandp_dk', '#c9a068', 1.0, 0.85, 1.1)
    glint = glow('s16_glint', '#d8ff9a', 2.4)
    ven = M['venom']
    # ---------------- idle: venom beads and glints around the sting
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 0.9)
        sphere('idle_drop_%d' % i, rnd.uniform(0.04, 0.08), ven, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.2, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.7), -0.3, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: sand puffs, chitin shards, venom drops, green rings
    fx('flight')
    puffs = [sphere('fl_puff_%d' % i, 0.34, sandp if i % 3 else sandp_dk, 12, 7) for i in range(8)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.9 * t), jp[i][1] * (0.15 + 0.9 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.36, M['chitin'] if i % 2 else M['armor'], 4, 0.4, 0.7, both=True, ol=0.012) for i in range(8)]
    js = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(shards, lambda t, i: (js[i][0] * (0.35 + 1.0 * t), js[i][1] * (0.35 + 1.0 * t), 8.9 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (js[i][2] + 540 * t, 360 * t, 0))
    drops = [sphere('fl_drop_%d' % i, 0.08, ven, 8, 5) for i in range(10)]
    jd = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(drops, lambda t, i: (jd[i][0] * (0.2 + 0.7 * t), jd[i][1] * (0.2 + 0.7 * t), 9.0 - 11.0 * t), smax=1.3)
    rings = [torus('fl_ring_%d' % i, 0.45, 0.035, glow('s16_airring', '#c2f07a', 1.6), 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: ground splits, two claws burst out and snap closed, sand, venom
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s16_flash', '#f2ffb8', 2.0, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.8)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    sh = torus('im_shock', 0.5, 0.05, glow('s16_shock', '#e8ffb0', 1.8), 32, 5, loc=(cx, 0, 0.06))
    expand(sh, f, 0.3, 5.0, 12)
    # ground splits: dark cracks with a venom vein
    for i, ang in enumerate((-100, -50, 0, 55, 105)):
        a = math.radians(ang + rnd.uniform(-8, 8))
        L_ = rnd.uniform(1.4, 2.3)
        pts = zigzag((0, 0, 0), (L_ * math.cos(a), L_ * math.sin(a), 0), 5, 0.14, seed=i + 3)
        for p in pts:
            p.z = 0.0
        rad = [0.13, 0.11, 0.09, 0.07, 0.05, 0.0]
        cr = tube('im_crack_%d' % i, pts, rad, M['chitin'], 4, smooth=False, ol=0, loc=(cx, 0, 0.02))
        pop(cr, f + i % 2, (1, 1, 0.3), grow=4)
        vn = tube('im_vein_%d' % i, pts, [r_ * 0.45 for r_ in rad], ven, 4, smooth=False, ol=0, loc=(cx, 0, 0.05))
        key(vn, IMPACT0, scale=0, alpha=1)
        key(vn, f + 4 + i % 2, scale=0, alpha=1)
        key(vn, f + 10, scale=(1, 1, 0.3), alpha=1)
        key(vn, IMPACT0 + 32, scale=(1, 1, 0.3), alpha=1)
        key(vn, END, scale=(1, 1, 0.3), alpha=0)
        tidy(vn, 'impact')
    mound = rock('im_mound', 0.55, M['armor'], seed=8, sub=1, rough=0.18, loc=(cx, 0, -0.1))
    pop(mound, f, (1.5, 1.5, 0.5), grow=4)
    # two hooked claws burst out on both sides and snap shut over the contact point
    cp = [(0, 0, 0), (0.28, 0, 0.55), (0.42, 0, 1.15), (0.34, 0, 1.7), (0.1, 0, 2.05)]
    cr_ = [0.2, 0.18, 0.14, 0.09, 0.0]
    for i, s in enumerate((-1, 1)):
        cl = tube('im_claw_%d' % i, cp, cr_, M['chitin'] if i == 0 else M['armor'], 6, loc=(cx, s * 0.95, 0.0), rot=(0, -38, 90 if s < 0 else -90), ol=0.02)
        t0 = f + 1
        key(cl, IMPACT0, scale=0)
        key(cl, t0, scale=0)
        key(cl, t0 + 5, scale=1.0, rot=(0, -38, 90 if s < 0 else -90))
        key(cl, t0 + 10, scale=1.0, rot=(0, -38, 90 if s < 0 else -90))
        key(cl, t0 + 13, scale=1.0, rot=(0, 26, 90 if s < 0 else -90), interp='LINEAR')
        key(cl, IMPACT0 + 36, scale=1.0, rot=(0, 26, 90 if s < 0 else -90))
        key(cl, END, scale=0)
        tidy(cl, 'impact')
        tp = sphere('im_clawtip_%d' % i, 0.09, ven, 7, 4, loc=(cx, -s * 0.04, 1.8))
        pop(tp, t0 + 13, 1.0, grow=3, hold=IMPACT0 + 30)
    for i in range(10):
        a = math.radians(i * 36 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.3, 2.4)
        p = sphere('im_dust_%d' % i, 0.32, sandp if i % 3 else sandp_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.8))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.3, 1.9), alpha=0.9)
        key(p, END, loc=(end[0], end[1], end[2] + 0.4), scale=rnd.uniform(2.0, 2.6), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    for i in range(14):
        a = math.radians(rnd.uniform(-140, 140))
        sp = rnd.uniform(0.04, 0.11)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.28, 0.42)))
        dr = sphere('im_drop_%d' % i, rnd.uniform(0.06, 0.1), ven, 7, 4)
        toss(dr, (cx, 0, 0.2), v, f, zg=0.06)
    for i in range(6):
        a = math.radians(rnd.uniform(-130, 130))
        sp = rnd.uniform(0.05, 0.1)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.25, 0.38)))
        c = rock('im_chip_%d' % i, rnd.uniform(0.08, 0.14), M['armor'] if i % 2 else M['chitin'], seed=i + 40, sub=1, rough=0.25, flat=True)
        toss(c, (cx, 0, 0.15), v, f)
    return True
