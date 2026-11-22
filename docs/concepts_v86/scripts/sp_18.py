from spearlib import *

NAME = 'SP_18_temple_guard'
N = 18
BG = '#8a8a68'        # temple haze
GROUND = '#a89e84'    # worn flagstone
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'pillar': 'im_pillar_0', 'glyph': 'im_glyph_0', 'spark': 'im_spark_0', 'shock_ring': 'im_shock'}
END = IMPACT0 + 44


def mats():
    return dict(
        stone=toon('s18_stone', '#b9ad8e', '#7d7360', '#e6dcc0', spec=0.3),
        stone_dk=toon('s18_stone_dk', '#7d7360', '#463f36', '#a89e84', spec=0.3),
        gold=toon('s18_gold', '#f2b93a', '#a8701e', '#fff0a0', spec=1.0, rimcol='#fff4c0'),
        turq=toon('s18_turq', '#35c4b4', '#1a7a80', '#8af0de', spec=0.9, emit=0.2),
        lapis=toon('s18_lapis', '#2f5fb8', '#1a3678', '#6c92e8', spec=0.8),
        cord=toon('s18_cord', '#b03a30', '#6a1c1e', '#e0665a', spec=0.2),
        eye=glow('s18_eye', '#ffd86a', 2.2),
        rune=glow('s18_rune', '#ffd24a', 2.2),
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
    stone, stone_dk, gold, turq, lapis, cord, eye, rune = (M[k] for k in (
        'stone', 'stone_dk', 'gold', 'turq', 'lapis', 'cord', 'eye', 'rune'))
    # ---- tail: carved stone counterweight with a gold cap
    box('tail_block', (0.42, 0.42, 0.55), stone_dk, 0.05, 1, loc=(0, 0, 0.62), rot=(0, 0, 45))
    cone('tail_cap', 0.2, 0.34, gold, 4, loc=(0, 0, 0.36), rot=(180, 0, 45), ol=0.015)
    torus('tail_ring', 0.19, 0.045, gold, 14, 6, loc=(0, 0, 0.95))
    torus('tail_ring2', 0.18, 0.035, turq, 14, 6, loc=(0, 0, 1.08))
    # ---- shaft: stone-grey with lapis wraps and glyph inlays
    rod('shaft_lo', 0.155, 0.6, 3.3, stone, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, stone, r1=0.14)
    coil('wrap_lo', 0.178, 0.03, 1.2, 1.7, 4, lapis, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, gold, 14, 6, loc=(0, 0, 1.94))
    torus('wrap_lo_cap2', 0.17, 0.035, gold, 14, 6, loc=(0, 0, 1.15))
    coil('wrap_hi', 0.176, 0.03, 3.08, 3.6, 4, lapis, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, gold, 14, 6, loc=(0, 0, 3.06))
    for i in range(5):
        a = i * 1.26
        box('glyph_%d' % i, (0.06, 0.05, 0.2), turq if i % 2 else gold, 0.012, 1,
            loc=(0.15 * math.cos(a), 0.15 * math.sin(a), 3.9 + i * 0.4), rot=(0, 0, math.degrees(a)), ol=0.012)
    for i, z in enumerate((5.05, 5.25, 5.45)):
        torus('gold_ring_%d' % i, 0.16, 0.03 if i != 1 else 0.04, gold if i != 1 else cord, 14, 5, loc=(0, 0, z), ol=0.015)
    # ---- socket with a carved mask face and a gold crest
    lathe('socket', [(6.1, 0.15), (6.25, 0.25), (6.5, 0.3), (6.8, 0.27), (6.9, 0.2), (6.9, 0)], stone, 12)
    torus('socket_band', 0.28, 0.045, gold, 14, 6, loc=(0, 0, 6.3))
    box('mask', (0.56, 0.16, 0.72), stone_dk, 0.05, 1, loc=(0, -0.3, 6.78))
    for s in (-1, 1):
        sphere('mask_eye_%d' % (s + 1), 0.065, eye, 8, 5, loc=(s * 0.14, -0.4, 6.93), scale=(1.2, 0.6, 0.8), ol=0)
    box('mask_nose', (0.1, 0.14, 0.28), stone, 0.02, 1, loc=(0, -0.42, 6.72))
    box('mask_mouth', (0.3, 0.05, 0.07), gold, 0.012, 1, loc=(0, -0.4, 6.5), ol=0.012)
    for i in range(3):
        cone('mask_crest_%d' % i, 0.07, 0.3 + 0.1 * (i == 1), gold, 5, loc=(-0.2 + i * 0.2, -0.3, 7.12), ol=0.015)
    # ---- halberd head: gold spear point + stone axe blade + hook spur
    blade('blade_main', [(0, 6.9), (0.3, 7.2), (0.36, 8.0), (0.22, 8.8), (0, TIP), (-0.22, 8.8), (-0.36, 8.0), (-0.3, 7.2)], 0.14, gold)
    blade('blade_rib', [(-0.08, 7.3), (0.08, 7.3), (0.07, 8.7), (-0.07, 8.7)], 0.2, stone_dk, ol=0.012)
    blade('axe', [(0.25, 7.3), (0.9, 6.95), (1.35, 7.5), (1.3, 8.1), (0.9, 8.35), (0.3, 8.1)], 0.13, stone)
    tube('axe_edge', [(0.9, 0, 6.95), (1.3, 0, 7.4), (1.38, 0, 7.8), (1.28, 0, 8.15)], 0.05, gold, 6)
    sphere('axe_gem', 0.09, turq, 8, 5, loc=(0.78, 0.13, 7.65), ol=0.012)
    tube('spur', [(-0.25, 0, 7.4), (-0.7, 0, 7.55), (-1.0, 0, 7.9), (-1.05, 0, 8.35)], [0.13, 0.11, 0.08, 0.0], stone, 8, scale=(1, 0.7, 1))
    torus('spur_ring', 0.12, 0.035, gold, 10, 5, loc=(-0.6, 0, 7.55), rot=(0, 75, 0), ol=0.015)
    sphere('blade_gem', 0.08, rune, 8, 5, loc=(0, 0.17, 7.3), ol=0)
    # ---- charm: ankh-ring on a red cord
    tube('charm_cord', [(0.2, 0.03, 6.05), (0.34, 0.06, 5.75), (0.4, 0.07, 5.5)], 0.022, cord, 5)
    torus('charm_ring', 0.1, 0.03, gold, 12, 5, loc=(0.4, 0.07, 5.35), rot=(90, 0, 0), ol=0.012)
    cone('charm_tail', 0.04, 0.22, gold, 5, loc=(0.4, 0.07, 5.25), rot=(180, 0, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1818)
    gold_sp = glow('s18_spark', '#ffd24a', 2.8)
    dust = ghost('s18_dust', '#e6dcc0', 1.0, 0.8, 1.1)
    dust_dk = ghost('s18_dust_dk', '#b0a48a', 1.0, 0.8, 1.1)
    glint = glow('s18_glint', '#fff2b0', 2.6)
    # ---------------- idle: gold sparks and glints around the halberd
    fx('idle')
    for i in range(6):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.0)
        sphere('idle_spark_%d' % i, rnd.uniform(0.04, 0.08), gold_sp, 7, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.8), -0.4, 7.4 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: sparks, stone chips, rune stars, gold rings
    fx('flight')
    sparks = [sphere('fl_spark_%d' % i, 0.06, gold_sp, 6, 4) for i in range(12)]
    jk = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(12)]
    stream(sparks, lambda t, i: (jk[i][0] * (0.3 + 1.4 * t), jk[i][1] * (0.3 + 1.4 * t), 8.6 - 13.0 * t), smax=1.2)
    chips = [rock('fl_chip_%d' % i, 0.09, M['stone'] if i % 2 else M['stone_dk'], seed=i, sub=1, rough=0.22, flat=True) for i in range(8)]
    jc = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(chips, lambda t, i: (jc[i][0] * (0.3 + 0.9 * t), jc[i][1] * (0.3 + 0.9 * t), 8.4 - 13.0 * t),
           smax=1.0, spin=lambda t, i: (jc[i][2] + 720 * t, 540 * t, 0))
    runes = [star('fl_rune_%d' % i, 0.16, 0.05, 4, 0.03, M['rune']) for i in range(6)]
    jr = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(runes, lambda t, i: (jr[i][0] * (0.4 + 0.8 * t), jr[i][1] * (0.4 + 0.8 * t), 8.8 - 12.0 * t),
           smax=1.0, spin=lambda t, i: (90, 0, 360 * t))
    rings = [torus('fl_ring_%d' % i, 0.45, 0.04, gold_sp, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.6 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: stone glyph ring, four rune pillars, golden spark fountain
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('s18_flash', '#fff0b0', 2.0, 0.7, 1.2), 16, 8, loc=(cx, 0, 0.3))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.4, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.8)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    sh = torus('im_shock', 0.5, 0.05, gold_sp, 32, 5, loc=(cx, 0, 0.06))
    expand(sh, f, 0.3, 5.0, 12)
    # carved stone glyph ring (r 1.8) with eight glowing glyphs and an inner ring
    ring = torus('im_ring', 1.8, 0.1, M['stone_dk'], 36, 6, loc=(cx, 0, 0.05))
    pop(ring, f, (1, 1, 0.5), grow=5)
    inner = torus('im_ring_in', 1.15, 0.06, M['rune'], 32, 5, loc=(cx, 0, 0.08))
    key(inner, IMPACT0, scale=0, alpha=1)
    key(inner, f + 2, scale=0, alpha=1)
    key(inner, f + 8, scale=1.0, alpha=1)
    key(inner, IMPACT0 + 34, scale=1.0, alpha=1)
    key(inner, END, scale=1.0, alpha=0)
    tidy(inner, 'impact', interp='LINEAR')
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        gl = box('im_glyph_%d' % i, (0.3, 0.12, 0.04), M['rune'], 0.01, 1, loc=(cx + 1.48 * math.cos(a), 1.48 * math.sin(a), 0.07),
                 rot=(0, 0, math.degrees(a) + 90), ol=0)
        t0 = f + 3 + i
        key(gl, IMPACT0, scale=0, alpha=1)
        key(gl, t0, scale=0, alpha=1)
        key(gl, t0 + 4, scale=1.2, alpha=1)
        key(gl, t0 + 7, scale=1.0, alpha=1)
        key(gl, IMPACT0 + 34, scale=1.0, alpha=1)
        key(gl, END, scale=1.0, alpha=0)
        tidy(gl, 'impact')
    # four rune pillars rise on the ring
    for i, ang in enumerate((-110, -40, 40, 110)):
        a = math.radians(ang)
        px, py = cx + 1.8 * math.cos(a), 1.8 * math.sin(a)
        pl = lathe('im_pillar_%d' % i, [(0, 0), (0, 0.3), (1.1, 0.3), (1.15, 0.37), (1.3, 0.37), (1.3, 0)], M['stone'] if i % 2 else M['stone_dk'],
                   4, loc=(px, py, 0.0), rot=(0, 0, 45))
        t0 = f + 4 + i * 2
        pop(pl, t0, 1.0, grow=6)
        rn = star('im_rune_%d' % i, 0.18, 0.06, 4, 0.04, M['rune'], loc=(px, py, 0.4), rot=(90, 0, 0))
        key(rn, IMPACT0, scale=0, alpha=1)
        key(rn, t0, loc=(px, py, 0.4), scale=0, alpha=1)
        key(rn, t0 + 6, loc=(px, py, 1.7), scale=1.2, alpha=1)
        key(rn, IMPACT0 + 36, loc=(px, py, 1.85), scale=1.0, alpha=1)
        key(rn, END, loc=(px, py, 1.9), scale=0.5, alpha=0)
        tidy(rn, 'impact', interp='LINEAR')
    # golden fountain
    g = -0.03
    for i in range(24):
        a = math.radians(rnd.uniform(0, 360))
        sp = rnd.uniform(0.01, 0.045)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.3, 0.46)))
        sk = sphere('im_spark_%d' % i, rnd.uniform(0.05, 0.09), gold_sp, 6, 4)
        p0 = Vector((cx, 0, 0.2))
        t00 = f + (i % 6)
        key(sk, IMPACT0, loc=p0, scale=0)
        key(sk, t00, loc=p0, scale=0.3)
        t = 0
        while True:
            t += 3
            p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
            if p.z <= 0.1 or t00 + t >= END - 1:
                key(sk, min(t00 + t, END), loc=Vector((p.x, p.y, max(p.z, 0.1))), scale=0)
                break
            key(sk, t00 + t, loc=p, scale=1.0, interp='LINEAR')
        tidy(sk, 'impact')
    for i in range(8):
        a = math.radians(i * 45 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.3, 2.4)
        p = sphere('im_dust_%d' % i, 0.3, dust if i % 2 else dust_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.3, 0.8))
        key(p, IMPACT0, loc=(cx, 0, 0.2), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.2), scale=0.3, alpha=1)
        key(p, f + 10, loc=end, scale=rnd.uniform(1.2, 1.8), alpha=0.9)
        key(p, END, loc=(end[0], end[1], end[2] + 0.4), scale=rnd.uniform(2.0, 2.5), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    for i in range(6):
        a = math.radians(rnd.uniform(-130, 130))
        sp = rnd.uniform(0.05, 0.1)
        v = Vector((sp * math.cos(a), sp * math.sin(a), rnd.uniform(0.25, 0.38)))
        c = rock('im_chip_%d' % i, rnd.uniform(0.08, 0.14), M['stone'] if i % 2 else M['stone_dk'], seed=i + 40, sub=1, rough=0.25, flat=True)
        toss(c, (cx, 0, 0.15), v, f)
    return True
