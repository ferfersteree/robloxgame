from spearlib import *

NAME = 'SP_32_quartz_needle'
N = 32
BG = '#8a9cc0'        # pale crystal cave
GROUND = '#6f7ea0'    # quartz grit
TIP = 9.45
TRAIL = 5.2
FX_EXPORT = {'needle': 'im_needle_0', 'glint': 'im_glint_0', 'glow_ring': 'im_ring', 'fl_needle': 'fl_needle_0'}


def mats():
    return dict(
        quartz=toon('qzn_quartz', '#e8f4ff', '#9ab4d8', '#ffffff', spec=1.0, rim=0.7, rimcol='#a8e8ff', emit=0.35),
        quartz_dk=toon('qzn_quartzdk', '#a8c4e8', '#5a78b0', '#e0f0ff', spec=1.0, emit=0.25),
        silver=toon('qzn_silver', '#dfe6f2', '#8a96b0', '#ffffff', spec=1.0),
        navy=toon('qzn_navy', '#34406e', '#1a2244', '#6a7cb8', spec=0.8),
        cord=toon('qzn_cord', '#9fb4dc', '#5a6e9c', '#d8e6ff', spec=0.2),
        rose=toon('qzn_rose', '#f4b6d0', '#c06a90', '#ffe4f0', spec=0.9, emit=0.3),
        core=glow('qzn_core', '#8ce6ff', 3.0),
        hot=glow('qzn_hot', '#f0fcff', 3.6),
    )


def toss(ob, p0, v, f, g=-0.03, floor=0.08, spin=(30, 20, 0), hold=36, s=1.0):
    key(ob, IMPACT0, loc=p0, scale=0)
    if f > IMPACT0 + 1:
        key(ob, f - 1, loc=p0, scale=0)
    key(ob, f, loc=p0, scale=0.3 * s)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= floor or f + t >= IMPACT0 + 40
        if done:
            p.z = floor
        key(ob, f + t, loc=p, scale=s, rot=(t * spin[0], t * spin[1], t * spin[2]), interp='LINEAR')
        if done:
            break
    key(ob, max(f + t + 2, IMPACT0 + hold), scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    quartz, quartz_dk, silver, navy, cord, rose, core, hot = (M[k] for k in (
        'quartz', 'quartz_dk', 'silver', 'navy', 'cord', 'rose', 'core', 'hot'))
    # ---- tail: counter-needle with a silver bead
    crystal('tail_needle', 0.12, 0.9, quartz_dk, 6, 0.4, 0.9, loc=(0, 0, 0.9), rot=(180, 0, 0), ol=0.02)
    sphere('tail_bead', 0.17, silver, 10, 6, loc=(0, 0, 1.0), scale=(1, 1, 0.9))
    torus('tail_ring_a', 0.2, 0.04, silver, 14, 6, loc=(0, 0, 1.25))
    torus('tail_ring_b', 0.18, 0.035, rose, 14, 5, loc=(0, 0, 1.12))
    # ---- shaft: slim navy with silver wire and cord
    rod('shaft_lo', 0.15, 1.2, 3.3, navy, r1=0.148)
    rod('shaft_hi', 0.148, 3.28, 6.2, navy, r1=0.14)
    coil('cord_lo', 0.17, 0.03, 1.35, 1.9, 4, cord, segs=5)
    torus('cord_lo_cap', 0.172, 0.038, silver, 14, 6, loc=(0, 0, 1.93))
    coil('cord_hi', 0.168, 0.03, 3.12, 3.7, 4, cord, segs=5, phase=1.0)
    torus('cord_hi_cap', 0.17, 0.034, silver, 14, 6, loc=(0, 0, 3.1))
    for i in range(5):
        a = i * 2.4
        crystal('shaft_stud_%d' % i, 0.045, 0.3, quartz if i % 2 else rose, 5, 0.4, 0.7, loc=(0.13 * math.cos(a), 0.13 * math.sin(a), 4.05 + i * 0.4),
                rot=aim((math.cos(a), math.sin(a), 0.8)), ol=0.012)
    for i, z in enumerate((4.0, 5.9)):
        torus('shaft_band_%d' % i, 0.152, 0.028, silver, 14, 5, loc=(0, 0, z), ol=0.015)
    # ---- slim crystal socket: silver vase with thin crystal claws
    lathe('socket', [(5.95, 0.14), (6.1, 0.2), (6.35, 0.3), (6.6, 0.26), (6.72, 0.2), (6.75, 0.0)], silver, 14)
    torus('socket_ring_a', 0.22, 0.04, rose, 14, 6, loc=(0, 0, 6.2))
    torus('socket_ring_b', 0.27, 0.045, navy, 14, 6, loc=(0, 0, 6.62))
    for i in range(4):
        a = math.radians(i * 90 + 45)
        ca, sa = math.cos(a), math.sin(a)
        crystal('claw_%d' % i, 0.06, 1.05, quartz_dk, 6, 0.3, 0.9, loc=(0.24 * ca, 0.24 * sa, 6.6), rot=aim((ca * 0.35, sa * 0.35, 1)), ol=0.015)
    for i in range(4):
        a = math.radians(i * 90)
        ca, sa = math.cos(a), math.sin(a)
        crystal('claw_lo_%d' % i, 0.045, 0.62, quartz, 6, 0.3, 0.9, loc=(0.27 * ca, 0.27 * sa, 6.55), rot=aim((ca * 0.7, sa * 0.7, 1)), ol=0.012)
    # ---- the needle: very long, thin, clear; silver wire spiral and glowing rings
    crystal('needle', 0.2, 2.95, quartz, 6, 0.22, 1.0, loc=(0, 0, 6.5), ol=0.026)
    crystal('needle_side_a', 0.085, 1.65, quartz_dk, 6, 0.3, 1.0, loc=(0.34, 0, 6.6), rot=aim((0.22, 0, 1)), ol=0.018)
    crystal('needle_side_b', 0.085, 1.45, quartz_dk, 6, 0.3, 1.0, loc=(-0.34, 0, 6.6), rot=aim((-0.22, 0, 1)), ol=0.018)
    coil('wire_spiral', 0.24, 0.02, 7.0, 8.7, 3, silver, segs=4)
    for i, z in enumerate((7.45, 8.1, 8.7)):
        torus('needle_ring_%d' % i, 0.215 - 0.02 * i, 0.022, core, 16, 5, loc=(0, 0, z), ol=0)
    sphere('needle_gem', 0.1, rose, 8, 5, loc=(0, -0.2, 6.85), ol=0.012)
    for i in range(3):
        a = math.radians(i * 120 + 70)
        crystal('float_shard_%d' % i, 0.04, 0.55, quartz, 5, 0.4, 0.8, both=True, loc=(0.62 * math.cos(a), 0.62 * math.sin(a), 7.5 + 0.55 * i),
                rot=aim((math.cos(a) * 0.1, math.sin(a) * 0.1, 1)), ol=0.012)
        sphere('float_glint_%d' % i, 0.045, hot, 6, 4, loc=(0.62 * math.cos(a), 0.62 * math.sin(a), 7.5 + 0.55 * i + 0.35), ol=0)
    tube('charm_cord', [(0.15, 0.04, 5.9), (0.3, 0.08, 5.6), (0.36, 0.1, 5.3)], 0.02, cord, 5)
    crystal('charm_crystal', 0.05, 0.4, quartz, 5, 0.4, 0.8, both=True, loc=(0.36, 0.1, 5.2), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(3232)
    aura = ghost('qzn_aura', '#a8e8ff', 1.2, 0.05, 1.8)
    puff = ghost('qzn_puff', '#f0fcff', 1.2, 0.7, 1.2)
    glint = glow('qzn_glint', '#f4feff', 3.2)
    ringm = glow('qzn_ring', '#8ce6ff', 2.6)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.5, aura, 12, 7, loc=(0, 0, 8.0), scale=(1.0, 1.0, 3.2))
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 0.8)
        sphere('idle_mote_%d' % i, rnd.uniform(0.04, 0.07), glint, 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.3)))
    for i in range(4):
        star('idle_glint_%d' % i, 0.16, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.3, 0.6), -0.3, 7.5 + i * 0.5), rot=(90, 0, 0))
    # ---------------- flight: needle streaks, glints, rings, frost puffs
    fx('flight')
    nd = [crystal('fl_needle_%d' % i, 0.04, 0.9, M['quartz'] if i % 2 else M['quartz_dk'], 5, 0.4, 0.8, both=True, ol=0.01) for i in range(14)]
    nj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(14)]
    stream(nd, lambda t, i: (nj[i][0] * (0.25 + 1.0 * t), nj[i][1] * (0.25 + 1.0 * t), 9.0 - 12.5 * t), smax=lambda t, i: 1.0 + 0.8 * t)
    st = [star('fl_glint_%d' % i, 0.16, 0.04, 4, 0.03, glint) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(st, lambda t, i: (sj[i][0] * (0.3 + 1.2 * t), sj[i][1] * (0.3 + 1.2 * t), 8.6 - 12.0 * t), smax=1.3,
           spin=lambda t, i: (90, sj[i][2] + 300 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.4, 0.035, ringm, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.4 - 7.5 * t), smax=lambda t, i: (0.5 + 1.8 * t) * math.sin(math.pi * t) ** 0.4)
    pf = [sphere('fl_puff_%d' % i, 0.25, puff, 12, 7) for i in range(5)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(5)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.7 * t), pj[i][1] * (0.2 + 0.7 * t), 6.5 - 10.0 * t),
           smax=lambda t, i: (0.5 + 1.4 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: a dense forest of thin quartz needles shoots up in a disc
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('qzn_flash', '#e8fcff', 2.0, 0.6, 1.3), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.7)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    gd = sphere('im_disc', 1.2, ghost('qzn_disc', '#a8e8ff', 1.4, 0.4, 1.0), 16, 4, loc=(cx, 0, 0.03))
    key(gd, IMPACT0, scale=0, alpha=1)
    key(gd, f + 4, scale=(1.4, 1.4, 0.02), alpha=1)
    key(gd, IMPACT0 + 36, scale=(2.0, 2.0, 0.02), alpha=0.8)
    key(gd, IMPACT0 + 44, scale=(2.0, 2.0, 0.02), alpha=0)
    tidy(gd, 'impact')
    rg = torus('im_ring', 0.6, 0.05, ringm, 36, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 12, scale=4.4, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    GA = 2.39996
    n = 0
    NN = 46
    for i in range(NN):
        r = 0.35 + 2.15 * math.sqrt(i / NN)
        a = i * GA
        x, y = cx + r * math.cos(a), r * math.sin(a)
        if x < cx + 0.15 and abs(y) < 0.42:
            continue                                  # keep the stuck shaft clear
        h = rnd.uniform(0.9, 1.5) + 0.7 * (1 - r / 2.5)
        lean = 0.12 + 0.2 * r / 2.5
        nd_ = crystal('im_needle_%d' % n, rnd.uniform(0.05, 0.085), h, M['quartz'] if n % 3 else M['quartz_dk'], 5, 0.3, 1.0,
                      loc=(x, y, -0.05), rot=aim((math.cos(a) * lean, math.sin(a) * lean, 1)), ol=0.015)
        t0 = f + int(r * 2.2) + (n % 2)
        te = f + 22 + int(r * 3) + (n % 3)
        key(nd_, IMPACT0, scale=0)
        key(nd_, t0, scale=(1, 1, 0.05))
        key(nd_, t0 + 3, scale=(1.0, 1.0, 1.2))
        key(nd_, t0 + 6, scale=1.0)
        key(nd_, te, scale=1.0)
        key(nd_, te + 5, scale=(0.9, 0.9, 0.05))
        key(nd_, te + 6, scale=0)
        tidy(nd_, 'impact')
        ease_keys(nd_)
        n += 1
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 2.0)
        g_ = star('im_glint_%d' % i, 0.2, 0.04, 4, 0.03, glint, loc=(cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.9, 1.9)), rot=(90, 0, 0))
        t0 = f + 4 + rnd.randint(0, 16)
        key(g_, IMPACT0, scale=0)
        key(g_, t0, scale=0)
        key(g_, t0 + 4, scale=1.3)
        key(g_, t0 + 12, scale=0)
        tidy(g_, 'impact')
    for i in range(8):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.28, 0.42)))
        sh = crystal('im_chip_%d' % i, 0.04, rnd.uniform(0.25, 0.4), M['quartz'], 5, 0.4, 0.8, both=True, ol=0.012)
        toss(sh, Vector((cx, 0, 0.2)), v, f + rnd.randint(0, 4), floor=0.1, spin=(40, 25, 10), hold=38)
    return True
