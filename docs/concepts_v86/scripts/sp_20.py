from spearlib import *

NAME = 'SP_20_hydra_fangs'
N = 20
BG = '#5f8a62'        # swamp dusk
GROUND = '#5f7242'    # marsh
TIP = 9.35
TRAIL = 5.2
FX_EXPORT = {'fang': 'im_fang_0', 'shard': 'im_shard_0', 'venom_drop': 'im_drop_0', 'shock_ring': 'im_shock'}
END = IMPACT0 + 44


def mats():
    return dict(
        scale=toon('s20_scale', '#2f9a5a', '#145a3a', '#7de0a0', spec=0.7, rimcol='#c8ffd8'),
        scale_dk=toon('s20_scale_dk', '#1c6a40', '#0c3a28', '#4cb078', spec=0.6),
        ivory=toon('s20_ivory', '#f4f0d8', '#b8b090', '#ffffff', spec=0.7, rimcol='#d8ffc0'),
        iron=toon('s20_iron', '#5e6878', '#323a48', '#a0acc0', spec=1.0),
        gold=toon('s20_gold', '#dba83c', '#8e5a1a', '#ffe08a', spec=1.0),
        leather=toon('s20_leather', '#4a3a2c', '#241a14', '#7a6048'),
        venom=glow('s20_venom', '#a8ff4a', 2.2),
        eye=glow('s20_eye', '#ff5a3a', 2.2),
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
    scale, scale_dk, ivory, iron, gold, leather, venom, eye = (M[k] for k in (
        'scale', 'scale_dk', 'ivory', 'iron', 'gold', 'leather', 'venom', 'eye'))
    # ---- tail: coiled serpent tail with a spike
    coil('tail_curl', 0.2, 0.09, 0.3, 1.05, 2, scale, segs=6, R1=0.1)
    cone('tail_spike', 0.1, 0.32, ivory, 7, loc=(0, 0, 0.32), rot=(180, 0, 0), ol=0.015)
    torus('tail_ring', 0.18, 0.04, gold, 14, 6, loc=(0, 0, 1.12))
    # ---- shaft: dark green, leather grip wraps, iron bands
    rod('shaft_lo', 0.155, 0.9, 3.3, scale_dk, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, scale_dk, r1=0.14)
    coil('wrap_lo', 0.178, 0.03, 1.3, 1.82, 4, leather, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, iron, 14, 6, loc=(0, 0, 1.94))
    coil('wrap_hi', 0.176, 0.03, 3.08, 3.62, 4, leather, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, iron, 14, 6, loc=(0, 0, 3.06))
    for i in range(5):
        a = i * 1.4
        cone('shaft_scale_%d' % i, 0.07, 0.2, scale, 5, loc=(0.14 * math.cos(a), 0.14 * math.sin(a), 4.0 + i * 0.32),
             rot=aim((math.cos(a), math.sin(a), -0.5)), ol=0.012)
    for i, z in enumerate((5.3, 5.5)):
        torus('iron_band_%d' % i, 0.17, 0.04, iron if i == 0 else gold, 14, 6, loc=(0, 0, z), ol=0.015)
    # ---- serpent-head socket: reinforced snout, red eyes, frill spikes, iron frame
    lathe('head', [(5.95, 0.15), (6.1, 0.28), (6.5, 0.4), (6.9, 0.46), (7.1, 0.36), (7.15, 0)], scale, 14)
    torus('head_band_a', 0.38, 0.05, iron, 16, 6, loc=(0, 0, 6.3))
    torus('head_band_b', 0.4, 0.05, gold, 16, 6, loc=(0, 0, 7.0))
    for s in (-1, 1):
        sphere('eye_%d' % (s + 1), 0.09, eye, 8, 5, loc=(s * 0.3, -0.3, 6.8), ol=0)
        cone('brow_%d' % (s + 1), 0.07, 0.28, scale_dk, 6, loc=(s * 0.34, -0.3, 6.95), rot=aim((s, -0.3, 0.8)), ol=0.015)
    for i in range(6):
        a = math.radians(i * 60 + 30)
        cone('frill_%d' % i, 0.07, 0.34, scale_dk, 6, loc=(0.32 * math.cos(a), 0.32 * math.sin(a), 6.25),
             rot=aim((math.cos(a), math.sin(a), -0.9)), ol=0.015)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        sphere('rivet_%d' % i, 0.045, gold, 6, 4, loc=(0.43 * math.cos(a), 0.43 * math.sin(a), 7.0), ol=0.01)
    # ---- the twin fangs: curved ivory blades that bite inward, banded in iron
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        pts = [(s * 0.42, 0, 6.85), (s * 0.58, 0, 7.6), (s * 0.5, 0, 8.4), (s * 0.3, 0, 9.0), (s * 0.08, 0, TIP)]
        tube('fang_' + nm, pts, [0.3, 0.3, 0.24, 0.14, 0.0], ivory, 10, scale=(1, 0.55, 1))
        tube('fang_vein_' + nm, [(s * 0.55, -0.1, 7.3), (s * 0.58, -0.1, 7.9), (s * 0.5, -0.09, 8.5)], [0.0, 0.05, 0.0], venom, 5, ol=0)
        torus('fang_band_a_' + nm, 0.3, 0.045, iron, 14, 5, loc=(s * 0.55, 0, 7.2), scale=(1, 0.62, 1), ol=0.015)
        torus('fang_band_b_' + nm, 0.24, 0.04, gold, 14, 5, loc=(s * 0.55, 0, 7.95), scale=(1, 0.62, 1), ol=0.015)
        crystal('fang_tip_' + nm, 0.05, 0.28, venom, 4, 0.4, 0.8, loc=(s * 0.2, 0, 9.0), rot=(0, -s * 25, 0), ol=0)
    # ---- charm: ivory milk-tooth on a cord
    tube('charm_cord', [(0.2, 0.03, 6.0), (0.34, 0.06, 5.75), (0.4, 0.07, 5.5)], 0.022, leather, 5)
    cone('charm_tooth', 0.07, 0.3, ivory, 6, loc=(0.4, 0.07, 5.5), rot=(180, 0, 0), ol=0.015)
    sphere('charm_bead', 0.06, venom, 8, 5, loc=(0.34, 0.065, 5.78), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2020)
    mist = ghost('s20_mist', '#c8f0c0', 1.0, 0.8, 1.1)
    mist_dk = ghost('s20_mist_dk', '#5a8a5a', 1.0, 0.8, 1.1)
    ven = M['venom']
    glint = glow('s20_glint', '#e4ffb8', 2.6)
    # ---------------- idle: venom beads and glints around the fangs
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.0)
        sphere('idle_drop_%d' % i, rnd.uniform(0.04, 0.08), ven, 8, 5, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.2, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 0.9), -0.3, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: shards, venom drops, mist, rings
    fx('flight')
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.36, M['ivory'] if i % 2 else M['scale'], 4, 0.4, 0.7, both=True, ol=0.012) for i in range(10)]
    js = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(10)]
    stream(shards, lambda t, i: (js[i][0] * (0.35 + 1.0 * t), js[i][1] * (0.35 + 1.0 * t), 8.9 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (js[i][2] + 540 * t, 360 * t, 0))
    drops = [sphere('fl_drop_%d' % i, 0.08, ven, 8, 5) for i in range(10)]
    jd = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(drops, lambda t, i: (jd[i][0] * (0.2 + 0.7 * t), jd[i][1] * (0.2 + 0.7 * t), 9.0 - 11.0 * t), smax=1.3)
    puffs = [sphere('fl_mist_%d' % i, 0.34, mist if i % 2 else mist_dk, 12, 7) for i in range(6)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.8 * t), jp[i][1] * (0.15 + 0.8 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.45, 0.035, glow('s20_airring', '#c2ff80', 1.7), 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: two fangs snap up from the ground and cross in an X, green shard spray
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s20_flash', '#e0ffb0', 2.0, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.8)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    sh = torus('im_shock', 0.5, 0.05, glow('s20_shock', '#c8ff80', 1.8), 32, 5, loc=(cx, 0, 0.06))
    expand(sh, f, 0.3, 5.0, 12)
    fp = [(0, 0, 0), (0.35, 0, 0.8), (0.9, 0, 1.5), (1.45, 0, 2.0)]
    fr = [0.3, 0.26, 0.17, 0.0]
    fp2 = [(-x, y, z) for (x, y, z) in fp]
    for i in range(2):
        base = (cx + 0.15, 0.0, 0.0) if i == 0 else (cx + 1.55, 0.0, 0.0)
        fg = tube('im_fang_%d' % i, fp if i == 0 else fp2, fr, M['ivory'], 8, loc=base, scale=(1, 0.6, 1), ol=0.02)
        t0 = f + i * 2
        key(fg, IMPACT0, scale=0)
        key(fg, t0, scale=0)
        key(fg, t0 + 3, scale=1.18)
        key(fg, t0 + 7, scale=1.0)
        key(fg, IMPACT0 + 38, scale=1.0)
        key(fg, END, scale=0)
        tidy(fg, 'impact')
        ease_keys(fg)
        ho = sphere('im_hole_%d' % i, 0.34, M['scale_dk'], 10, 6, loc=(base[0], 0, 0.0))
        pop(ho, f + i * 2, (1, 0.8, 0.12), grow=3)
        vn = tube('im_fangvein_%d' % i, [(0.35 * (1 if i == 0 else -1), -0.1, 0.9), (0.85 * (1 if i == 0 else -1), -0.1, 1.55)], [0.0, 0.05],
                  ven, 4, loc=base, ol=0)
        vn.scale = (1, 1, 1)
        key(vn, IMPACT0, scale=0, alpha=1)
        key(vn, t0 + 4, scale=0, alpha=1)
        key(vn, t0 + 8, scale=1, alpha=1)
        key(vn, IMPACT0 + 34, scale=1, alpha=1)
        key(vn, END, scale=1, alpha=0)
        tidy(vn, 'impact')
    for i in range(5):
        a = math.radians(-100 + i * 50)
        L_ = rnd.uniform(1.3, 2.2)
        pts = zigzag((0, 0, 0), (L_ * math.cos(a), L_ * math.sin(a), 0), 4, 0.12, seed=i + 5)
        for p in pts:
            p.z = 0.0
        cr = tube('im_crack_%d' % i, pts, [0.11, 0.09, 0.07, 0.04, 0.0], M['scale_dk'], 4, smooth=False, ol=0, loc=(cx + 0.7, 0, 0.02))
        pop(cr, f + i % 3, (1, 1, 0.3), grow=4)
    for i in range(6):
        a = math.radians(-120 + i * 48 + rnd.uniform(-6, 6))
        rr = rnd.uniform(1.9, 2.5)
        tt = cone('im_tooth_%d' % i, 0.1, 0.55, M['ivory'], 6, loc=(cx + 0.7 + rr * math.cos(a), rr * math.sin(a), 0.0), rot=aim((math.cos(a) * 0.4, math.sin(a) * 0.4, 1)), ol=0.015)
        pop(tt, f + 3 + i, 1.0, grow=4)
    for i in range(24):
        a = math.radians(rnd.uniform(-150, 150))
        sp = rnd.uniform(0.04, 0.09)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.26, 0.4)))
        sd = crystal('im_shard_%d' % i, 0.06, rnd.uniform(0.28, 0.45), M['scale'] if i % 3 else M['ivory'], 4, 0.4, 0.7, both=True, ol=0.012)
        toss(sd, (cx + 0.7, 0, 0.2), v, f)
    for i in range(10):
        a = math.radians(rnd.uniform(-150, 150))
        sp = rnd.uniform(0.03, 0.08)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.3, 0.46)))
        dr = sphere('im_drop_%d' % i, rnd.uniform(0.05, 0.09), ven, 7, 4)
        toss(dr, (cx + 0.7, 0, 0.2), v, f, zg=0.06)
    for i in range(8):
        a = math.radians(i * 45 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.3, 2.4)
        p = sphere('im_mist_%d' % i, 0.32, mist if i % 2 else mist_dk, 12, 7)
        end = (cx + 0.5 + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.8))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.3, 1.9), alpha=0.9)
        key(p, END, loc=(end[0], end[1], end[2] + 0.4), scale=rnd.uniform(2.0, 2.6), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    return True
