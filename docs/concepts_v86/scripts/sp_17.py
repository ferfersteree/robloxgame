from spearlib import *

NAME = 'SP_17_emerald_vine'
N = 17
BG = '#5e9a6a'        # jungle mist
GROUND = '#78b254'    # mossy floor
TIP = 9.35
TRAIL = 5.2
FX_EXPORT = {'vine': 'im_vine_0', 'leaf': 'im_leaf_0', 'bud': 'im_bud_0', 'shock_ring': 'im_shock'}
END = IMPACT0 + 44


def mats():
    return dict(
        emerald=toon('s17_emerald', '#2fd68a', '#127a58', '#9af5c6', spec=1.0, rim=0.7, emit=0.35, rimcol='#e8fff0'),
        emerald_dk=toon('s17_emerald_dk', '#1a9a6a', '#0a5040', '#5ee0a8', spec=1.0, emit=0.2),
        vine=toon('s17_vine', '#4c9a3a', '#2a5a2a', '#88d060'),
        leaf=toon('s17_leaf', '#7bd05a', '#3e8a3a', '#c4f090', spec=0.4),
        bark=toon('s17_bark', '#7a5232', '#46301f', '#a87a4e'),
        gold=toon('s17_gold', '#eab83e', '#a8701e', '#fff0a0', spec=1.0),
        pink=toon('s17_pink', '#ff6fa0', '#c23a6e', '#ffb0cc', spec=0.5),
        cream=toon('s17_cream', '#f6efc8', '#c4b27c', '#ffffff'),
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
    emerald, emerald_dk, vine, leafm, bark, gold, pink, cream = (M[k] for k in (
        'emerald', 'emerald_dk', 'vine', 'leaf', 'bark', 'gold', 'pink', 'cream'))
    # ---- tail: root bulb with a bud crystal and three hanging leaves
    lathe('bulb', [(0.25, 0), (0.25, 0.1), (0.37, 0.24), (0.57, 0.29), (0.8, 0.22), (0.97, 0.14), (1.03, 0.0)], bark, 12)
    crystal('tail_bud', 0.1, 0.45, emerald_dk, 5, 0.35, 0.8, loc=(0, 0, 0.45), rot=(180, 0, 0), ol=0.015)
    for i in range(3):
        a = i * 120 + 20
        leaf('tail_leaf_%d' % i, 0.5, 0.2, leafm, 0.03, 5, loc=(0.2 * math.cos(math.radians(a)), 0.2 * math.sin(math.radians(a)), 0.95),
             rot=(0, 55, a), ol=0.015)
    torus('bulb_band', 0.2, 0.04, gold, 14, 6, loc=(0, 0, 1.08))
    # ---- shaft: mossy wood, vine wraps with leaves, bare grip
    rod('shaft_lo', 0.155, 0.7, 3.3, bark, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, bark, r1=0.14)
    coil('vine_lo', 0.18, 0.034, 1.0, 1.92, 5, vine, segs=5)
    torus('vine_lo_cap', 0.18, 0.04, gold, 14, 6, loc=(0, 0, 1.94))
    coil('vine_hi', 0.178, 0.034, 3.08, 5.6, 8, vine, segs=5, phase=1.0)
    torus('vine_hi_cap', 0.178, 0.04, gold, 14, 6, loc=(0, 0, 3.06))
    for i, z in enumerate((1.0, 1.3, 1.55)):
        a = i * 2.4
        leaf('vine_leaf_lo_%d' % i, 0.42, 0.18, leafm, 0.03, 5, loc=(0.19 * math.cos(a), 0.19 * math.sin(a), z), rot=(0, -40, math.degrees(a)), ol=0.012)
    for i, z in enumerate((3.7, 4.2, 4.7, 5.2)):
        a = i * 2.4 + 1.0
        leaf('vine_leaf_hi_%d' % i, 0.42, 0.18, leafm, 0.03, 5, loc=(0.19 * math.cos(a), 0.19 * math.sin(a), z), rot=(0, -40, math.degrees(a)), ol=0.012)
    for i in range(3):
        sphere('vine_flower_%d' % i, 0.07, pink if i % 2 == 0 else cream, 7, 4, loc=(0.19 * math.cos(i * 2.9 + 0.5), 0.19 * math.sin(i * 2.9 + 0.5), 4.0 + i * 0.5), ol=0.012)
    # ---- socket: bark cup with a flower
    lathe('socket', [(6.1, 0.15), (6.25, 0.25), (6.5, 0.3), (6.8, 0.27), (6.9, 0.2), (6.9, 0)], bark, 12)
    torus('socket_band', 0.28, 0.045, gold, 14, 6, loc=(0, 0, 6.3))
    coil('socket_vine', 0.3, 0.032, 6.4, 6.85, 3, vine, segs=5)
    star('flower', 0.2, 0.09, 5, 0.07, pink, loc=(0.3, 0.12, 6.55), rot=(90, 0, 20), ol=0.015)
    sphere('flower_heart', 0.06, gold, 7, 4, loc=(0.3, 0.17, 6.55), ol=0.012)
    # ---- emerald blade: main crystal + side crystals, wrapped by a spiral vine with leaves
    crystal('emerald', 0.45, TIP - 6.75, emerald, 6, 0.3, 0.8, loc=(0, 0, 6.75), scale=(1, 0.72, 1))
    for s in (-1, 1):
        crystal('emerald_side_%s' % ('L' if s < 0 else 'R'), 0.17, 1.4, emerald_dk, 6, 0.35, 0.7, loc=(s * 0.45, 0, 6.8),
                rot=aim((s * 0.35, 0, 1)), ol=0.02)
    coil('vine_blade', 0.44, 0.045, 6.9, 8.9, 3, vine, segs=5, R1=0.22)
    for i in range(5):
        a = i * 1.9
        z = 7.0 + i * 0.4
        leaf('blade_leaf_%d' % i, 0.5, 0.2, leafm, 0.03, 5, loc=(0.42 * math.cos(a) * (1 - i * 0.12), 0.42 * math.sin(a) * (1 - i * 0.12), z),
             rot=(0, -50, math.degrees(a)), ol=0.012)
    tube('tendril', [(0.4, 0, 7.2), (0.72, 0, 7.4), (0.92, 0, 7.8), (0.82, 0, 8.1), (0.6, 0, 8.0), (0.55, 0, 7.8)], 0.04, vine, 6)
    crystal('tendril_bud', 0.07, 0.3, emerald, 5, 0.35, 0.8, loc=(0.55, 0, 7.82), ol=0.012)
    tube('tendril_b', [(-0.4, 0, 7.6), (-0.7, 0, 7.8), (-0.88, 0, 8.2), (-0.7, 0, 8.45)], 0.035, vine, 6)
    crystal('tendril_bud_b', 0.06, 0.28, emerald, 5, 0.35, 0.8, loc=(-0.7, 0, 8.45), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1717)
    spore = glow('s17_spore', '#b8ff9a', 2.2)
    mist = ghost('s17_mist', '#d2f8bc', 1.0, 0.8, 1.1)
    mist_dk = ghost('s17_mist_dk', '#7ec06a', 1.0, 0.8, 1.1)
    glint = glow('s17_glint', '#f4ffd0', 2.6)
    # ---------------- idle: glowing spores and glints around the blade
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.55, 0.95)
        sphere('idle_spore_%d' % i, rnd.uniform(0.05, 0.09), spore, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.4)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.8), -0.3, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: leaves, emerald shards, mist, green rings
    fx('flight')
    leaves = [leaf('fl_leaf_%d' % i, 0.4, 0.17, M['leaf'] if i % 2 else M['vine'], 0.03, 5, ol=0.012) for i in range(12)]
    jl = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(12)]
    stream(leaves, lambda t, i: (jl[i][0] * (0.3 + 1.0 * t), jl[i][1] * (0.3 + 1.0 * t), 8.4 - 12.5 * t),
           smax=1.1, spin=lambda t, i: (jl[i][2] + 360 * t, 240 * t, jl[i][2] * 0.5))
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.34, M['emerald'] if i % 2 else M['emerald_dk'], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(8)]
    js = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(shards, lambda t, i: (js[i][0] * (0.35 + 0.9 * t), js[i][1] * (0.35 + 0.9 * t), 8.9 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (js[i][2] + 540 * t, 360 * t, 0))
    puffs = [sphere('fl_mist_%d' % i, 0.34, mist if i % 2 else mist_dk, 12, 7) for i in range(6)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.8 * t), jp[i][1] * (0.15 + 0.8 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.45, 0.035, glow('s17_airring', '#a8f08a', 1.7), 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: vines sprout and curl, leaves unfold, emerald buds pop on them
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s17_flash', '#e4ffc8', 2.0, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.8)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    sh = torus('im_shock', 0.5, 0.05, glow('s17_shock', '#c8ff9a', 1.8), 32, 5, loc=(cx, 0, 0.06))
    expand(sh, f, 0.3, 5.0, 12)
    cp = [(0, 0, 0), (0.05, 0, 0.5), (0.2, 0, 0.95), (0.45, 0, 1.25), (0.75, 0, 1.35), (0.95, 0, 1.15), (0.95, 0, 0.88), (0.78, 0, 0.78), (0.65, 0, 0.9)]
    cr = [0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.0]
    for i, (ang, rr) in enumerate(((-115, 1.3), (-65, 1.7), (-15, 1.3), (35, 1.7), (85, 1.3), (135, 1.7))):
        a = math.radians(ang)
        B = (cx + rr * math.cos(a), rr * math.sin(a))
        az = ang + 90
        caz, saz = math.cos(math.radians(az)), math.sin(math.radians(az))
        t0 = f + i
        v = tube('im_vine_%d' % i, cp, cr, M['vine'], 6, loc=(B[0], B[1], 0.0), rot=(0, 0, az))
        pop(v, t0, 1.0, grow=7)
        for k, idx in enumerate((2, 4)):
            lx, lz = cp[idx][0], cp[idx][2]
            lf = leaf('im_leaf_%d' % (i * 2 + k), 0.5, 0.22, M['leaf'], 0.03, 5, loc=(B[0] + lx * caz, B[1] + lx * saz, lz),
                      rot=(0, -35, az + (50 if k == 0 else -50)), ol=0.012)
            pop(lf, t0 + 6 + k * 2, 1.0, grow=4)
        bx, bz = cp[7][0], cp[7][2]
        bd = crystal('im_bud_%d' % i, 0.09, 0.4, M['emerald'] if i % 2 == 0 else M['emerald_dk'], 5, 0.35, 0.8,
                     loc=(B[0] + bx * caz, B[1] + bx * saz, bz), ol=0.015)
        key(bd, IMPACT0, scale=0)
        key(bd, t0 + 8, scale=0)
        key(bd, t0 + 11, scale=1.3)
        key(bd, t0 + 14, scale=1.0)
        key(bd, IMPACT0 + 38, scale=1.0)
        key(bd, END, scale=0)
        tidy(bd, 'impact')
    for i in range(10):
        a = math.radians(rnd.uniform(-150, 150))
        sp = rnd.uniform(0.04, 0.1)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.28, 0.42)))
        lf = leaf('im_flyleaf_%d' % i, 0.28, 0.12, M['leaf'] if i % 2 else M['vine'], 0.02, 4, ol=0.01)
        toss(lf, (cx, 0, 0.2), v, f, g=-0.022, zg=0.1)
    for i in range(10):
        a0 = rnd.uniform(0, 360)
        t0 = f + rnd.randint(0, 10)
        sp_ = sphere('im_spore_%d' % i, 0.07, spore, 6, 4)
        key(sp_, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        for k in range(1, 6):
            u = k / 5.0
            ang = math.radians(a0 + 300 * u)
            p = (cx + (0.3 + 1.0 * u) * math.cos(ang), (0.3 + 1.0 * u) * math.sin(ang), 0.2 + 2.4 * u)
            key(sp_, t0 + int(u * (END - t0)) if k < 5 else END, loc=p, scale=1.0 if k < 5 else 0.0, alpha=1 if k < 5 else 0)
        tidy(sp_, 'impact', interp='LINEAR')
    for i in range(10):
        a = math.radians(i * 36 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.3, 2.3)
        p = sphere('im_mist_%d' % i, 0.32, mist if i % 2 else mist_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.8))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.3, 1.9), alpha=0.9)
        key(p, END, loc=(end[0], end[1], end[2] + 0.4), scale=rnd.uniform(2.0, 2.6), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
