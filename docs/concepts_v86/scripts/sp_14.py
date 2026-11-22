from spearlib import *

NAME = 'SP_14_condor_quill'
N = 14
BG = '#c9946a'        # canyon sky
GROUND = '#d08e5e'    # sandstone
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'feather': 'im_feather_0', 'wind_ring': 'im_wind_0', 'shock_ring': 'im_shock', 'puff': 'fl_puff_0'}
END = IMPACT0 + 44


def mats():
    return dict(
        ivory=toon('s14_ivory', '#f4ecd8', '#c7b896', '#ffffff', spec=0.5, rimcol='#ffd9a0'),
        black=toon('s14_black', '#2c2a36', '#14131c', '#5e5a72', spec=0.7, rimcol='#ffb070'),
        white=toon('s14_white', '#ffffff', '#cdd6e6', '#ffffff', spec=0.3),
        rust=toon('s14_rust', '#c9602f', '#80331f', '#f09060'),
        gold=toon('s14_gold', '#f2b53c', '#b0701e', '#ffe69a', spec=1.0),
        wood=toon('s14_wood', '#3d3544', '#201a28', '#6d6078'),
        sky=toon('s14_sky', '#4fb0e0', '#2a6fa8', '#a8e4ff', spec=0.8, emit=0.15),
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
    ivory, black, white, rust, gold, wood, sky = (M[k] for k in ('ivory', 'black', 'white', 'rust', 'gold', 'wood', 'sky'))
    # ---- tail: three feather fins (z 0..1.75) + quill cap
    for i in range(3):
        blade('tail_fin_%d' % i, [(0.1, 1.75), (0.1, 0.7), (0.35, 0.05), (0.62, 0.0), (0.5, 0.6), (0.3, 1.3)], 0.05,
              (black, white, black)[i], rot=(0, 0, i * 120), ol=0.02)
    sphere('tail_cap', 0.21, ivory, 10, 6, loc=(0, 0, 0.3), scale=(1, 1, 1.2))
    cone('tail_quill', 0.1, 0.3, gold, 8, loc=(0, 0, 0.3), rot=(180, 0, 0), ol=0.015)
    torus('tail_band', 0.2, 0.04, gold, 14, 6, loc=(0, 0, 1.82))
    # ---- shaft: dark wood, white-down wraps
    rod('shaft_lo', 0.155, 0.6, 3.3, wood, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.3, wood, r1=0.14)
    coil('wrap_lo', 0.178, 0.03, 1.2, 1.7, 4, white, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, rust, 14, 6, loc=(0, 0, 1.94))
    coil('wrap_hi', 0.175, 0.03, 3.08, 3.62, 4, white, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.176, 0.04, rust, 14, 6, loc=(0, 0, 3.06))
    for i in range(4):
        sphere('fluff_%d' % i, 0.1 - i * 0.012, white, 8, 5, loc=(0.17 * math.cos(i * 2.1), 0.17 * math.sin(i * 2.1), 4.15 + i * 0.4), ol=0.012)
    for i, z in enumerate((4.75, 4.95, 5.15)):
        torus('stripe_%d' % i, 0.155, 0.03, (rust, gold, rust)[i], 14, 5, loc=(0, 0, z), ol=0.015)
    # ---- quill socket + feather ruff drooping from it
    lathe('socket', [(6.0, 0.15), (6.1, 0.22), (6.4, 0.25), (6.7, 0.21), (6.85, 0.14), (6.85, 0)], ivory, 12)
    torus('socket_band', 0.25, 0.04, gold, 14, 6, loc=(0, 0, 6.12))
    torus('socket_band2', 0.22, 0.035, rust, 14, 6, loc=(0, 0, 6.62))
    for i in range(8):
        a = i * 45
        leaf('ruff_%d' % i, 0.72, 0.26, black if i % 2 else white, 0.03, 5,
             loc=(0.17 * math.cos(math.radians(a)), 0.17 * math.sin(math.radians(a)), 6.2), rot=(0, 38, a), ol=0.015)
    # ---- the quill blade: spine + two black-tipped vanes
    tube('rachis', [(0, 0, 6.3), (0, 0, 7.5), (0, 0, 8.6), (0, 0, TIP)], [0.11, 0.1, 0.07, 0.0], ivory, 8)
    blade('vane_R', [(0.0, 6.6), (0.5, 6.9), (0.78, 7.6), (0.7, 8.4), (0.3, 9.0), (0.0, TIP)], 0.13, ivory)
    blade('vane_L', [(0.0, 6.6), (0.0, TIP), (-0.25, 8.9), (-0.62, 8.3), (-0.7, 7.5), (-0.45, 6.9)], 0.13, ivory)
    blade('vane_tip_R', [(0.0, 8.0), (0.74, 8.0), (0.71, 8.4), (0.31, 9.02), (0.0, TIP)], 0.17, black, ol=0.015)
    blade('vane_tip_L', [(0.0, 8.0), (0.0, TIP), (-0.26, 8.92), (-0.63, 8.32), (-0.66, 8.0)], 0.17, black, ol=0.015)
    blade('vane_stripe_R', [(0.0, 7.3), (0.78, 7.3), (0.79, 7.55), (0.0, 7.55)], 0.16, rust, ol=0.015)
    blade('vane_stripe_L', [(-0.7, 7.3), (0.0, 7.3), (0.0, 7.55), (-0.7, 7.55)], 0.16, rust, ol=0.015)
    sphere('quill_gem', 0.08, sky, 8, 5, loc=(0, 0.16, 6.95), ol=0.012)
    # ---- charm: small hanging feather on a cord
    tube('charm_cord', [(0.2, 0.03, 6.05), (0.34, 0.06, 5.75), (0.4, 0.07, 5.5)], 0.022, rust, 5)
    leaf('charm_feather', 0.6, 0.2, sky, 0.03, 5, loc=(0.4, 0.07, 5.5), rot=(0, 90, 20), ol=0.015)
    sphere('charm_bead', 0.06, gold, 8, 5, loc=(0.34, 0.065, 5.78), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1414)
    cloud = ghost('s14_cloud', '#fff4e4', 1.0, 0.85, 1.1)
    cloud_dk = ghost('s14_cloud_dk', '#d6a77a', 1.0, 0.85, 1.1)
    glint = glow('s14_glint', '#fff2c8', 2.4)
    wind_m = glow('s14_wind', '#bfeaff', 1.8)
    # ---------------- idle: loose feather motes and glints
    fx('idle')
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.0)
        leaf('idle_feather_%d' % i, 0.3, 0.1, (M['white'], M['black'], M['rust'])[i % 3], 0.02, 4,
             loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.2)), rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 360)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.5, 0.9), -0.25, 7.4 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: feathers + cloud puffs + wind rings
    fx('flight')
    feathers = [leaf('fl_feather_%d' % i, 0.55, 0.2, (M['black'], M['white'], M['rust'])[i % 3], 0.03, 5, ol=0.012) for i in range(14)]
    jf = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(14)]
    stream(feathers, lambda t, i: (jf[i][0] * (0.3 + 1.0 * t), jf[i][1] * (0.3 + 1.0 * t), 8.4 - 12.5 * t),
           smax=1.1, spin=lambda t, i: (jf[i][2] + 360 * t, 200 * t, jf[i][2] * 0.5))
    puffs = [sphere('fl_puff_%d' % i, 0.34, cloud if i % 2 else cloud_dk, 12, 7) for i in range(8)]
    jp = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(puffs, lambda t, i: (jp[i][0] * (0.15 + 0.8 * t), jp[i][1] * (0.15 + 0.8 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.5, 0.035, wind_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.5 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: updraft - feathers spiral up a helix, stacked wind rings rise
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s14_flash', '#fff0d0', 2.0, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.2, alpha=0.8)
    key(flash, f + 10, scale=3.0, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    shock = torus('im_shock', 0.5, 0.05, wind_m, 32, 5, loc=(cx, 0, 0.06))
    expand(shock, f, 0.3, 5.0, 12)
    col = lathe('im_column', [(0, 0), (0, 0.8), (3.2, 0.8), (3.2, 0)], ghost('s14_column', '#dff4ff', 1.2, 0.12, 1.4), 16, loc=(cx, 0, 0.0))
    key(col, IMPACT0, scale=0, alpha=1)
    key(col, f + 2, scale=(0.3, 0.3, 0.1), alpha=1)
    key(col, f + 12, scale=(1, 1, 1), alpha=0.8)
    key(col, END, scale=(1.2, 1.2, 1.1), alpha=0)
    tidy(col, 'impact', interp='LINEAR')
    ease_keys(col)
    # 18 feathers corkscrew upward
    for i in range(18):
        a0 = i * 137.5
        t0 = f + (i % 6) * 2
        fe = leaf('im_feather_%d' % i, 0.6, 0.2, (M['black'], M['white'], M['rust'])[i % 3], 0.03, 5, ol=0.012)
        key(fe, IMPACT0, loc=(cx, 0, 0.2), scale=0)
        frames = list(range(t0, END, 3)) + [END]
        for fr in frames:
            u = (fr - t0) / float(END - t0)
            ang = math.radians(a0 + 520 * u)
            rr = 0.35 + 0.65 * u
            p = (cx + rr * math.cos(ang), rr * math.sin(ang), 0.2 + 3.2 * u ** 0.9)
            s = 0.0 if (fr == t0 or fr == END) else 1.0
            key(fe, fr, loc=p, rot=(u * 300 + a0, 40, a0 + u * 260), scale=s, interp='LINEAR')
        tidy(fe, 'impact')
    # stacked wind rings rise
    for k in range(5):
        rg = torus('im_wind_%d' % k, 0.9, 0.05, wind_m, 28, 5, loc=(cx, 0, 0.3))
        t0 = f + k * 3
        key(rg, IMPACT0, scale=0, alpha=1)
        key(rg, t0, loc=(cx, 0, 0.3), scale=0.5, alpha=1)
        key(rg, min(t0 + 26, END), loc=(cx, 0, 0.3 + 2.0 + k * 0.25), scale=1.5 - k * 0.1, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
        ease_keys(rg)
    # low dust swirl and golden motes
    for i in range(10):
        a = math.radians(i * 36 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.2, 2.3)
        p = sphere('im_dust_%d' % i, 0.3, cloud if i % 2 else cloud_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.8))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.2, 1.8), alpha=0.9)
        key(p, END, loc=(end[0], end[1], end[2] + 0.4), scale=rnd.uniform(2.0, 2.5), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    for i in range(10):
        a0 = rnd.uniform(0, 360)
        t0 = f + rnd.randint(0, 10)
        mo = sphere('im_mote_%d' % i, 0.07, glint, 6, 4)
        key(mo, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        for k in range(1, 6):
            u = k / 5.0
            ang = math.radians(a0 + 400 * u)
            p = (cx + (0.3 + 0.7 * u) * math.cos(ang), (0.3 + 0.7 * u) * math.sin(ang), 0.2 + 3.0 * u)
            key(mo, t0 + int(u * (END - t0)) if k < 5 else END, loc=p, scale=1.0 if k < 5 else 0.0, alpha=1 if k < 5 else 0)
        tidy(mo, 'impact', interp='LINEAR')
    return True
