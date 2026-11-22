from spearlib import *

NAME = 'SP_24_tide_crest'
N = 24
BG = '#7cc4d8'        # reef shallows
GROUND = '#efdcae'    # sand
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'wave_slab': 'im_wave_0', 'foam_ring': 'im_foam', 'ice_flake': 'im_flake_0', 'water_ring': 'fl_ring_0',
             'splash': 'im_drop_0'}


def mats():
    return dict(
        sea=toon('tcr_sea', '#1f7fd6', '#124a9a', '#6fc0f5', spec=0.8, emit=0.15),
        deep=toon('tcr_deep', '#17408f', '#0c224f', '#3f73c8'),
        aqua=toon('tcr_aqua', '#4fd8e6', '#1f95b5', '#b8f6ff', spec=1.0, emit=0.3),
        foam=toon('tcr_foam', '#f4fcff', '#a9d4e6', '#ffffff', spec=0.6, emit=0.15),
        sand=toon('tcr_sand', '#f1dcae', '#c3a373', '#fff4d6', spec=0.3),
        shell=toon('tcr_shell', '#ffc9b8', '#d98a8a', '#fff1ea', spec=0.9),
        ice=toon('tcr_ice', '#bfeeff', '#6fb4d8', '#f0fcff', spec=1.0, emit=0.35),
        rope=toon('tcr_rope', '#e8d29c', '#a98950', '#fff0c4', spec=0.2),
        gold=toon('tcr_gold', '#f2c24a', '#b07a1e', '#ffe9a0', spec=1.0),
    )


def pop(ob, t0, t1, sc=1.0, hold=40, over=1.15):
    s = (sc, sc, sc) if isinstance(sc, (int, float)) else tuple(sc)
    key(ob, IMPACT0, scale=0)
    key(ob, t0, scale=0)
    key(ob, t1, scale=tuple(x * over for x in s))
    key(ob, t1 + 3, scale=s)
    key(ob, IMPACT0 + hold, scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def toss(ob, p0, v, f, g=-0.03, floor=0.08, spin=(30, 20, 0), hold=36, s=1.0):
    key(ob, IMPACT0, loc=p0, scale=0)
    key(ob, f, loc=p0, scale=0.3 * s)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= floor or t > 34
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
    sea, deep, aqua, foam, sand, shell, ice, rope, gold = (M[k] for k in (
        'sea', 'deep', 'aqua', 'foam', 'sand', 'shell', 'ice', 'rope', 'gold'))
    # ---- tail: pearl-and-shell counterweight
    sphere('pommel', 0.27, foam, 12, 7, loc=(0, 0, 0.3), scale=(1, 1, 0.9))
    for i in range(5):
        a = math.radians(i * 72)
        cone('pommel_spike_%d' % i, 0.06, 0.2, aqua, 5, loc=(0.22 * math.cos(a), 0.22 * math.sin(a), 0.22),
             rot=aim((math.cos(a), math.sin(a), -0.5)), ol=0.012)
    lathe('pommel_cup', [(0.52, 0.14), (0.62, 0.24), (0.78, 0.26), (0.92, 0.16)], deep, 12, caps=False)
    torus('pommel_ring', 0.19, 0.045, gold, 14, 6, loc=(0, 0, 1.0))
    # ---- shaft: sea-blue lacquer with rope wraps
    rod('shaft_lo', 0.155, 0.9, 3.3, sea, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, sea, r1=0.145)
    coil('rope_lo', 0.175, 0.032, 1.3, 1.9, 5, rope, segs=5)
    torus('rope_lo_cap', 0.18, 0.04, aqua, 14, 6, loc=(0, 0, 1.92))
    coil('rope_hi', 0.173, 0.032, 3.12, 3.7, 5, rope, segs=5, phase=1.0)
    torus('rope_hi_cap', 0.175, 0.035, aqua, 14, 6, loc=(0, 0, 3.1))
    for i, z in enumerate((4.3, 4.55, 4.8)):
        torus('wave_band_%d' % i, 0.15, 0.025, foam if i == 1 else deep, 14, 5, loc=(0, 0, z), ol=0.015)
    for i in range(4):
        a = i * 2.1
        sphere('bubble_inlay_%d' % i, 0.06, ice, 8, 5, loc=(0.14 * math.cos(a), 0.14 * math.sin(a), 5.2 + i * 0.27), ol=0.012)
    # ---- socket: shell cup with two wave ridges
    lathe('socket', [(6.3, 0.14), (6.45, 0.2), (6.75, 0.27), (7.0, 0.23), (7.05, 0.0)], deep, 14)
    torus('socket_ring_a', 0.2, 0.05, aqua, 14, 6, loc=(0, 0, 6.5))
    torus('socket_ring_b', 0.25, 0.05, foam, 14, 6, loc=(0, 0, 6.85))
    for s in (-1, 1):
        nm = 'a' if s < 0 else 'b'
        leaf('fin_' + nm, 0.95, 0.34, aqua, 0.05, 5, loc=(s * 0.2, 0.0, 6.75), rot=(0, -50 if s > 0 else -130, 0), ol=0.015)
        tube('fin_curl_' + nm, [(s * 0.3, 0, 6.55), (s * 0.62, 0, 6.65), (s * 0.82, 0, 6.95), (s * 0.7, 0, 7.2)],
             [0.07, 0.06, 0.045, 0.0], foam, 6)
    # ---- the wave-crest blade: tall flattened sweep curling forward at the top
    sp = [(0.0, 0, 6.8), (-0.06, 0, 7.5), (-0.04, 0, 8.2), (0.1, 0, 8.7), (0.4, 0, 9.0), (0.78, 0, 8.95), (1.02, 0, 8.6)]
    rr = [0.4, 0.46, 0.42, 0.34, 0.24, 0.13, 0.0]
    wave = tube('wave_blade', sp, rr, sea, 10)
    wave.scale = (1.0, 0.34, 1.0)
    sp2 = [(0.06, 0.0, 7.0), (0.0, 0.0, 7.6), (0.03, 0.0, 8.2), (0.17, 0.0, 8.65), (0.45, 0.0, 8.9), (0.7, 0.0, 8.8)]
    rr2 = [0.26, 0.3, 0.27, 0.2, 0.12, 0.0]
    inner = tube('wave_inner', sp2, rr2, aqua, 8, ol=0.015)
    inner.scale = (1.0, 0.5, 1.0)
    # foam tips along the curling crest + detached droplets
    for i, (x, z, r) in enumerate(((0.08, 8.95, 0.1), (0.4, 9.2, 0.12), (0.72, 9.15, 0.1), (0.95, 8.88, 0.09), (1.1, 8.55, 0.08))):
        sphere('foam_tip_%d' % i, r, foam, 8, 5, loc=(x, 0.02, z), ol=0.012)
    for i, (x, y, z) in enumerate(((1.2, 0.2, 8.2), (1.0, -0.25, 8.0), (-0.55, 0.15, 8.4))):
        sphere('drop_%d' % i, 0.07, ice, 8, 5, loc=(x, y, z), ol=0.012)
    for i in range(3):
        crystal('ice_flake_%d' % i, 0.06, 0.32, ice, 5, 0.4, 0.6, both=True, loc=(-0.5 + i * 0.05, -0.18 + i * 0.18, 7.3 + i * 0.5),
                rot=aim((-0.4, 0.1, 1)), ol=0.012)
    # ---- shell charm
    tube('charm_cord', [(0.15, 0.04, 6.4), (0.3, 0.08, 6.05), (0.34, 0.1, 5.75)], 0.02, rope, 5)
    star('starfish', 0.2, 0.08, 5, 0.08, shell, loc=(0.36, 0.12, 5.55), rot=(90, 0, 15), ol=0.015)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2424)
    bub = ghost('tcr_bubble', '#e2fbff', 1.4, 0.85, 2.2, edge=True)
    puffm = ghost('tcr_spray', '#f2fdff', 1.3, 0.7, 1.2)
    aq = glow('tcr_aq', '#6ff0ff', 2.4)
    foamg = glow('tcr_foamg', '#f0ffff', 2.0)
    glint = glow('tcr_glint', '#c8fbff', 2.8)
    # ---------------- idle: bubbles drifting off the crest + glints
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 0.9)
        sphere('idle_bubble_%d' % i, rnd.uniform(0.06, 0.12), bub, 10, 6, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.2, 9.4)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, glint, loc=(rnd.uniform(0.2, 0.9), -0.3, 8.2 + i * 0.4), rot=(90, 0, 0))
    # ---------------- flight: spray puffs + ice flakes + water rings
    fx('flight')
    sprays = [sphere('fl_spray_%d' % i, 0.3, puffm, 12, 7) for i in range(12)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.7, 1.3)) for _ in range(12)]
    stream(sprays, lambda t, i: (sj[i][0] * (0.2 + 0.9 * t), sj[i][1] * (0.2 + 0.9 * t), 8.4 - 12.0 * t),
           smax=lambda t, i: sj[i][2] * (0.6 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    flakes = [crystal('fl_flake_%d' % i, 0.07, 0.34, M['ice'], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(8)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(flakes, lambda t, i: (fj[i][0] * (0.35 + 1.0 * t), fj[i][1] * (0.35 + 1.0 * t), 8.8 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (fj[i][2] + 540 * t, 360 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, aq, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.2 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    drops = [sphere('fl_drop_%d' % i, 0.07, aq, 6, 4) for i in range(6)]
    dj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(drops, lambda t, i: (dj[i][0] * (0.3 + 1.4 * t), dj[i][1] * (0.3 + 1.4 * t), 8.6 - 13.0 * t), smax=1.2)
    # ---------------- impact: breaking wave wall, collapse, foam ring, splash, ice flakes
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('tcr_flash', '#d8ffff', 1.6, 0.55, 1.4), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 5, scale=1.8, alpha=0.6)
    key(flash, f + 12, scale=2.4, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    # the wave wall: 9 curled slabs on an arc in front of the spear; rise, curl over, collapse
    for k in range(9):
        a = math.radians(-84 + k * 21)
        R = 1.25
        loc = (cx + R * math.cos(a), R * math.sin(a), 0.0)
        slab = tube('im_wave_%d' % k, [(0, 0, 0), (0.0, 0, 0.7), (-0.18, 0, 1.3), (-0.55, 0, 1.55)], [0.32, 0.3, 0.24, 0.0], M['sea'], 8,
                    loc=loc, rot=(0, 0, math.degrees(a)))
        t0 = f + abs(k - 4)
        key(slab, IMPACT0, scale=0)
        key(slab, t0, scale=(0.4, 0.45, 0.05))
        key(slab, t0 + 6, scale=(1.0, 0.5, 1.15))
        key(slab, t0 + 12, scale=(1.05, 0.5, 1.0))
        key(slab, t0 + 20, scale=(1.5, 0.6, 0.45))
        key(slab, t0 + 27, scale=(1.9, 0.7, 0.08))
        key(slab, t0 + 30, scale=0)
        tidy(slab, 'impact')
        ease_keys(slab)
        cap = sphere('im_wavefoam_%d' % k, 0.2, M['foam'], 8, 5, loc=(loc[0] - 0.55 * math.cos(a), loc[1] - 0.55 * math.sin(a), 1.55))
        crest = (loc[0] - 0.55 * math.cos(a), loc[1] - 0.55 * math.sin(a), 1.55)
        key(cap, IMPACT0, loc=crest, scale=0)
        key(cap, t0, loc=crest, scale=0)
        key(cap, t0 + 7, loc=crest, scale=1.0)
        key(cap, t0 + 12, loc=crest, scale=1.0)
        key(cap, t0 + 24, loc=(cx + 0.5 * math.cos(a), 0.5 * math.sin(a), 0.2), scale=0.7)
        key(cap, t0 + 30, scale=0)
        tidy(cap, 'impact')
    fr = torus('im_foam', 0.6, 0.09, foamg, 36, 5, loc=(cx, 0, 0.05))
    key(fr, IMPACT0, scale=0, alpha=1)
    key(fr, f, scale=0.3, alpha=1)
    key(fr, f + 14, scale=3.2, alpha=0.8)
    key(fr, IMPACT0 + 40, scale=4.4, alpha=0)
    tidy(fr, 'impact', interp='LINEAR')
    ease_keys(fr)
    for k in range(2):
        rg = torus('im_ripple_%d' % k, 0.6, 0.05, aq, 36, 5, loc=(cx, 0, 0.03))
        key(rg, IMPACT0, scale=0, alpha=1)
        key(rg, f + k * 6, scale=0.3, alpha=1)
        key(rg, f + k * 6 + 16, scale=3.8 - k * 0.7, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
        ease_keys(rg)
    for i in range(16):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.14)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.3, 0.46)))
        dp = sphere('im_drop_%d' % i, rnd.uniform(0.07, 0.13), aq if i % 2 else M['foam'], 7, 4)
        toss(dp, Vector((cx, 0, 0.2)), v, f + rnd.randint(0, 4), g=-0.03, floor=0.06, spin=(0, 0, 0), hold=30)
    for i in range(10):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.06, 0.15)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.26, 0.4)))
        fk = crystal('im_flake_%d' % i, 0.07, 0.3, M['ice'], 5, 0.4, 0.6, both=True, ol=0.012)
        toss(fk, Vector((cx, 0, 0.2)), v, f + rnd.randint(0, 3), g=-0.028, floor=0.12, spin=(40, 25, 10), hold=38)
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.8)
        sm = sphere('im_mist_%d' % i, 0.35, puffm, 12, 7)
        t0 = f + 3 + rnd.randint(0, 6)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.6, 2.6))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.2), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    return True
