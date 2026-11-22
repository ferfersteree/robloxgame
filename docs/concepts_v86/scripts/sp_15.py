from spearlib import *

NAME = 'SP_15_mirage_lance'
N = 15
BG = '#c8a46e'        # desert haze
GROUND = '#efcf8e'    # dune sand
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'mirror': 'im_mirror_0', 'heat_ring': 'im_heat_0', 'glitter': 'im_glitter_0', 'shard': 'fl_shard_0'}
END = IMPACT0 + 44


def mats():
    return dict(
        pale=toon('s15_pale', '#efe2c4', '#bfa982', '#fff7e2', spec=0.4),
        sand=toon('s15_sand', '#f2dfb4', '#c9a676', '#fff6e2', spec=0.3),
        gold=toon('s15_gold', '#e8b64a', '#a8701e', '#ffe69a', spec=1.0),
        turq=toon('s15_turq', '#33bfb2', '#1a7a80', '#90f0e2', spec=0.9, emit=0.15),
        rose=toon('s15_rose', '#d9697e', '#8e3450', '#ff9fb0'),
        cloth=toon('s15_cloth', '#f6efe0', '#cbb99a', '#ffffff', spec=0.1),
        crys=toon('s15_crys', '#a8ecff', '#4d9fcf', '#e6fbff', spec=1.0, rim=0.7, emit=0.4, rimcol='#ffffff'),
        deep=toon('s15_deep', '#5e7fd0', '#34478e', '#a2bcff', spec=0.9, emit=0.2),
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


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    pale, sand, gold, turq, rose, cloth, crys, deep = (M[k] for k in ('pale', 'sand', 'gold', 'turq', 'rose', 'cloth', 'crys', 'deep'))
    # ---- tail: onion-dome finial
    lathe('finial', [(0, 0), (0.0, 0.1), (0.1, 0.22), (0.28, 0.27), (0.46, 0.2), (0.62, 0.1), (0.78, 0.0)], gold, 12)
    torus('finial_band', 0.2, 0.04, turq, 14, 6, loc=(0, 0, 0.82))
    sphere('finial_gem', 0.07, rose, 8, 5, loc=(0, 0.2, 0.3), ol=0.012)
    # ---- shaft: pale reed, cloth wraps
    rod('shaft_lo', 0.155, 0.7, 3.3, pale, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, pale, r1=0.14)
    coil('wrap_lo', 0.18, 0.032, 1.1, 1.7, 4, cloth, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, gold, 14, 6, loc=(0, 0, 1.94))
    torus('wrap_lo_cap2', 0.17, 0.035, rose, 14, 6, loc=(0, 0, 1.0))
    coil('wrap_hi', 0.178, 0.032, 3.08, 3.7, 4, cloth, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, gold, 14, 6, loc=(0, 0, 3.06))
    for i in range(3):
        sphere('inlay_%d' % i, 0.06, turq if i != 1 else rose, 8, 5, loc=(0.14 * math.cos(i * 2.2), 0.14 * math.sin(i * 2.2), 4.0 + i * 0.35), ol=0.012)
    # ---- sash with tassels and two cloth streamers
    torus('sash', 0.19, 0.05, rose, 14, 6, loc=(0, 0, 5.95))
    for i in range(4):
        a = math.radians(45 + i * 90)
        x, y = 0.22 * math.cos(a), 0.22 * math.sin(a)
        tube('tassel_cord_%d' % i, [(x, y, 5.95), (x * 1.05, y * 1.05, 5.75)], 0.022, gold, 5)
        cone('tassel_%d' % i, 0.07, 0.55, rose if i % 2 else turq, 7, loc=(x * 1.05, y * 1.05, 5.75), rot=(180, 0, 0), ol=0.015)
        sphere('tassel_knob_%d' % i, 0.055, gold, 7, 4, loc=(x * 1.05, y * 1.05, 5.72), ol=0.012)
    blade('streamer_R', [(0.3, 6.2), (0.3, 5.3), (1.0, 5.55), (1.25, 6.0)], 0.03, cloth, edge=0.5, ol=0.015)
    blade('streamer_L', [(-0.3, 6.2), (-0.3, 5.4), (-0.85, 5.6), (-1.0, 6.0)], 0.03, rose, edge=0.5, ol=0.015)
    # ---- gold cup guard + crystal clusters
    lathe('guard', [(6.4, 0.15), (6.55, 0.25), (6.8, 0.4), (7.0, 0.5), (7.08, 0.46), (6.95, 0.3), (6.95, 0)], gold, 12)
    torus('guard_rim', 0.48, 0.045, turq, 16, 6, loc=(0, 0, 7.05))
    torus('collar', 0.22, 0.045, sand, 14, 6, loc=(0, 0, 6.48))
    # main shimmering crystal (base on the guard, top = TIP)
    crystal('tip_crystal', 0.34, TIP - 7.0, crys, 6, 0.28, 0.8, loc=(0, 0, 7.0))
    crystal('tip_core', 0.15, TIP - 7.9, deep, 6, 0.3, 0.8, loc=(0, 0, 7.1), ol=0.012)
    torus('crystal_band', 0.33, 0.035, gold, 14, 5, loc=(0, 0, 7.6), ol=0.015)
    for i in range(5):
        a = math.radians(i * 72 + 18)
        crystal('crys_small_%d' % i, 0.11, 1.0 + 0.1 * (i % 2), crys if i % 2 else deep, 5, 0.35, 0.8,
                loc=(0.38 * math.cos(a), 0.38 * math.sin(a), 6.98), rot=aim((math.cos(a) * 0.5, math.sin(a) * 0.5, 1)), ol=0.018)
    # ---- charm: gold sun-coin on a cord
    tube('charm_cord', [(0.2, 0.03, 6.1), (0.34, 0.06, 5.5), (0.38, 0.07, 5.0)], 0.022, rose, 5)
    cyl('charm_coin', 0.15, 0.04, gold, 12, 0.01, axis='Y', loc=(0.38, 0.07, 4.85), ol=0.015)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1515)
    sandp = ghost('s15_sandp', '#f6e2b4', 1.0, 0.85, 1.1)
    sandp_dk = ghost('s15_sandp_dk', '#d8ab6a', 1.0, 0.85, 1.1)
    glint = glow('s15_glint', '#fffbe0', 2.8)
    cyan = glow('s15_cyan', '#a8f0ff', 2.4)
    mir = ghost('s15_mirror', '#b8f2ff', 1.8, 0.7, 1.0, edge=True)
    heat = ghost('s15_heat', '#ffd9a0', 1.4, 0.5, 1.2)
    # ---------------- idle: shimmering crystal glints and sand motes
    fx('idle')
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.55, 0.9)
        sphere('idle_mote_%d' % i, rnd.uniform(0.05, 0.09), sandp if i % 2 else sandp_dk, 8, 5,
               loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.4)))
    for i in range(4):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.35, 0.7), -0.3, 7.5 + i * 0.5),
             rot=(90, 0, 0))
    torus('idle_heat', 0.55, 0.03, heat, 24, 5, loc=(0, 0, 7.0))
    # ---------------- flight: crystal shards, sand puffs, heat-shimmer rings, glints
    fx('flight')
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.34, M['crys'] if i % 2 else M['deep'], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(8)]
    js = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(shards, lambda t, i: (js[i][0] * (0.35 + 0.9 * t), js[i][1] * (0.35 + 0.9 * t), 8.9 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (js[i][2] + 540 * t, 360 * t, 0))
    puffs = [sphere('fl_puff_%d' % i, 0.34, sandp if i % 3 else sandp_dk, 12, 7) for i in range(10)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.9 * t), jp[i][1] * (0.15 + 0.9 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.5, 0.04, heat, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.5 * t) * math.sin(math.pi * t) ** 0.4)
    gl = [star('fl_glint_%d' % i, 0.14, 0.035, 4, 0.02, glint, rot=(90, 0, 0)) for i in range(6)]
    jg = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(gl, lambda t, i: (jg[i][0] * (0.3 + 0.8 * t), jg[i][1] * (0.3 + 0.8 * t), 9.0 - 11.0 * t), smax=1.0)
    # ---------------- impact: three ghost mirror crystals flash around, heat-wave rings, sand glitter
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s15_flash', '#fffbe8', 2.0, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.2, alpha=0.8)
    key(flash, f + 10, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    # three mirror crystals (transparent copies) blink in around the spear
    for i, (ang, rr) in enumerate(((-55, 1.4), (45, 1.7), (125, 1.4))):
        a = math.radians(ang)
        px, py = cx + rr * math.cos(a), rr * math.sin(a)
        mc = crystal('im_mirror_%d' % i, 0.34, 2.0, mir, 6, 0.28, 0.8, loc=(px, py, 0.0), rot=aim((math.cos(a) * 0.35, math.sin(a) * 0.35, 1)), ol=0)
        t0 = f + i * 3
        key(mc, IMPACT0, scale=0, alpha=1)
        key(mc, t0, scale=0, alpha=1)
        key(mc, t0 + 3, scale=1.1, alpha=0.9)
        key(mc, t0 + 7, scale=1.0, alpha=0.1)
        key(mc, t0 + 10, scale=1.05, alpha=0.9)
        key(mc, t0 + 15, scale=1.0, alpha=0.15)
        key(mc, t0 + 19, scale=1.1, alpha=0.8)
        key(mc, END, scale=0.9, alpha=0)
        tidy(mc, 'impact', interp='LINEAR')
        ease_keys(mc)
    # heat-wave rings
    for k in range(4):
        hr = torus('im_heat_%d' % k, 0.7, 0.05, heat, 32, 5, loc=(cx, 0, 0.08 + 0.12 * k))
        expand(hr, f + k * 4, 0.3, 4.2 - k * 0.4, 20)
    sh = torus('im_shock', 0.5, 0.05, cyan, 32, 5, loc=(cx, 0, 0.06))
    expand(sh, f, 0.3, 5.0, 12)
    mound = rock('im_mound', 0.55, M['sand'], seed=6, sub=1, rough=0.18, loc=(cx, 0, -0.1))
    pop(mound, f, (1.6, 1.6, 0.5), grow=4)
    for i in range(5):
        a = math.radians(rnd.uniform(-130, 130))
        rr = rnd.uniform(0.8, 1.6)
        cs = crystal('im_crys_%d' % i, 0.08, 0.5, M['crys'] if i % 2 else M['deep'], 5, 0.35, 0.8,
                     loc=(cx + rr * math.cos(a), rr * math.sin(a), 0.0), rot=aim((math.cos(a) * 0.3, math.sin(a) * 0.3, 1)), ol=0.015)
        pop(cs, f + 2 + i, 1.0, grow=4)
    # sand glitter arcs (twinkling stars)
    g = -0.03
    for i in range(22):
        a = math.radians(rnd.uniform(-150, 150))
        sp = rnd.uniform(0.05, 0.12)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.22, 0.38)))
        st = star('im_glitter_%d' % i, 0.14, 0.035, 4, 0.02, glint, rot=(90, 0, 0))
        p0 = Vector((cx, 0, 0.2))
        key(st, IMPACT0, loc=p0, scale=0)
        key(st, f, loc=p0, scale=0.3)
        t = 0
        while True:
            t += 3
            p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
            if p.z <= 0.1 or t > 30:
                key(st, f + t, loc=Vector((p.x, p.y, 0.1)), scale=0)
                break
            key(st, f + t, loc=p, scale=1.0 if (t // 3) % 2 else 0.55, interp='LINEAR')
        tidy(st, 'impact')
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
    return True
