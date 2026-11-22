from spearlib import *

NAME = 'SP_12_solar_trident'
N = 12
BG = '#c69a4e'        # savanna sun
GROUND = '#d8b45a'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'sun_ray': 'im_ray_0', 'sun_disc': 'im_sun', 'fire_ring_flame': 'im_flame_0',
             'flame_tongue': 'fl_tongue_0', 'sun_ring': 'fl_ring_0'}


def mats():
    return dict(
        gold=toon('b12_gold', '#f5b53a', '#b0641e', '#ffe39a', spec=1.0, rim=0.6, rimcol='#fff0b0'),
        gold_lt=toon('b12_gold_lt', '#ffd868', '#d8921e', '#fff6c0', spec=1.0, emit=0.4),
        gold_dk=toon('b12_gold_dk', '#c8861e', '#7a4410', '#eab04a', spec=0.8),
        sun=toon('b12_sun', '#ffcf45', '#e8861a', '#fff09a', spec=0.6, emit=0.9),
        wood=toon('b12_wood', '#9a3a1e', '#5a1c10', '#d0683e'),
        cream=toon('b12_cream', '#f0e0b8', '#b8a074', '#fff6dc', spec=0.2),
        ruby=toon('b12_ruby', '#d83a2a', '#8a1418', '#ff7a5a', spec=1.0, emit=0.3),
        turq=toon('b12_turq', '#2ab8a8', '#127a78', '#7ae8d8', spec=0.8),
        ray=glow('b12_ray', '#ffd24a', 2.2),
        ray_hot=glow('b12_ray_hot', '#fff0a8', 2.2),
        fl_o=glow('b12_fl_o', '#ff6a1a', 2.2),
        fl_y=glow('b12_fl_y', '#ffc23a', 2.2),
        ring=glow('b12_ring', '#ffb52a', 2.2),
        halo=ghost('b12_halo', '#ffd868', 1.6, 0.5, 1.2),
        aura=ghost('b12_aura', '#ffc23a', 1.4, 0.12, 1.6),
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


def build():
    begin(NAME, N, ol=0.032)
    M = mats()
    gold, gold_lt, gold_dk, sun, wood, cream, ruby, turq = (M[k] for k in (
        'gold', 'gold_lt', 'gold_dk', 'sun', 'wood', 'cream', 'ruby', 'turq'))
    # ---- tail: golden pommel with a ruby
    sphere('pommel', 0.27, gold, 12, 7, loc=(0, 0, 0.3))
    sphere('pommel_ruby', 0.11, ruby, 8, 5, loc=(0, 0, 0.12), ol=0.015)
    lathe('pommel_neck', [(0.5, 0), (0.5, 0.17), (0.62, 0.21), (0.78, 0.18), (0.9, 0.155), (0.9, 0)], gold_dk, 12)
    torus('pommel_ring', 0.2, 0.045, gold_lt, 12, 5, loc=(0, 0, 0.55))
    # ---- shaft: red acacia, bare grip zone
    rod('shaft_lo', 0.155, 0.85, 3.3, wood, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, wood, segs=12, r1=0.14)
    coil('wrap_lo', 0.18, 0.03, 1.35, 1.88, 4, cream, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, gold, 12, 5, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.03, 3.1, 3.62, 4, cream, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.04, gold, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.2, 4.45, 4.7)):
        torus('band_%d' % i, 0.148, 0.025 if i != 1 else 0.035, (turq, gold_lt, turq)[i], 12, 5, loc=(0, 0, z), ol=0.012)
    # ---- socket and the arched crossbar
    lathe('socket', [(6.0, 0.14), (6.2, 0.22), (6.5, 0.3), (6.75, 0.28), (6.9, 0.2), (6.9, 0)], gold, 14)
    torus('socket_ring', 0.3, 0.05, gold_lt, 14, 5, loc=(0, 0, 6.3))
    tube('crossbar', [(-0.64, 0, 7.4), (-0.46, 0, 7.05), (0, 0, 6.95), (0.46, 0, 7.05), (0.64, 0, 7.4)], 0.13, gold, 8)
    # ---- three prongs: central long blade + two side blades, on collared stems
    tube('stem_c', [(0, 0, 6.9), (0, 0, 7.4), (0, 0, 7.95)], [0.15, 0.14, 0.12], gold, 8)
    pc = [(0.14, 7.9), (0.25, 8.2), (0.24, 8.7), (0.11, 9.1), (0.0, TIP), (-0.11, 9.1), (-0.24, 8.7), (-0.25, 8.2), (-0.14, 7.9)]
    blade('prong_c', pc, 0.12, gold_lt)
    blade('prong_c_core', [(x * 0.45, 8.0 + (z - 7.9) * 0.88) for (x, z) in pc], 0.15, sun, ol=0.0)
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'
        tube('stem_' + nm, [(s * 0.64, 0, 7.3), (s * 0.66, 0, 7.6), (s * 0.64, 0, 7.95)], [0.12, 0.11, 0.1], gold, 8)
        blade('prong_' + nm, [(s * 0.64 + x * 0.8, 7.9 + (z - 7.9) * 0.75) for (x, z) in pc], 0.11, gold_lt)
        torus('collar_' + nm, 0.14, 0.04, ruby, 10, 5, loc=(s * 0.65, 0, 7.55), ol=0.012)
    torus('collar_c', 0.16, 0.045, ruby, 10, 5, loc=(0, 0, 7.55), ol=0.012)
    # ---- the sun disc behind the prongs: face, rim, alternating long/short rays
    cyl('sun_disc', 0.66, 0.1, sun, 24, 0.03, axis='Y', loc=(0, 0.22, 7.75))
    torus('sun_rim', 0.72, 0.06, gold, 24, 5, axis='Y', loc=(0, 0.22, 7.75))
    ring_f = torus('sun_face_ring', 0.42, 0.035, M['ray_hot'], 20, 4, axis='Y', loc=(0, 0.16, 7.75), ol=0)
    for k in range(12):
        a = math.radians(k * 30)
        ca, sa = math.cos(a), math.sin(a)
        ln = 0.45 if k % 2 == 0 else 0.3
        cone('sun_ray_%d' % k, 0.1 if k % 2 == 0 else 0.08, ln, gold_lt if k % 2 == 0 else gold, 5,
             loc=(0.78 * ca, 0.22, 7.75 + 0.78 * sa), rot=aim((ca, 0, sa)), ol=0.015)
    # ---- charm: ruby bead and a small sun medallion
    tube('charm_cord', [(0.2, 0.04, 6.0), (0.32, 0.08, 5.75), (0.36, 0.1, 5.55)], 0.02, cream, 5)
    sphere('charm_bead', 0.07, ruby, 8, 5, loc=(0.34, 0.09, 5.8), ol=0.012)
    cyl('charm_sun', 0.12, 0.04, sun, 12, 0.01, axis='Y', loc=(0.36, 0.1, 5.4), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(1212)
    ray, hot, fl_o, fl_y, ring_m, halo, aura = (M[k] for k in ('ray', 'ray_hot', 'fl_o', 'fl_y', 'ring', 'halo', 'aura'))
    FL = (fl_o, fl_y)
    # ---------------- idle: a faint aura, glints, tiny flames
    fx('idle')
    sphere('idle_aura', 0.7, aura, 16, 9, loc=(0, 0.1, 7.9), scale=(1.5, 0.8, 1.6))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, hot, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.0), -0.25, 7.5 + i * 0.6),
             rot=(90, 0, 0))
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.7, 1.1)
        flame('idle_flame_%d' % i, rnd.uniform(0.18, 0.28), 0.05, FL[i % 2], 0.1, 6, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.0)))
    # ---------------- flight: flame tongues, golden sparks, sun rings, light quills
    fx('flight')
    tg = [flame('fl_tongue_%d' % i, 0.7, 0.15, FL[i % 2], 0.0, 8) for i in range(8)]
    fj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.8, 1.4)) for _ in range(8)]
    stream(tg, lambda t, i: (fj[i][0] * (0.2 + 0.8 * t), fj[i][1] * (0.2 + 0.8 * t), 9.0 - 11.5 * t),
           smax=lambda t, i: fj[i][2] * (1.4 - 0.6 * t) * math.sin(math.pi * t) ** 0.5,
           spin=lambda t, i: (180 + fj[i][0] * 20, fj[i][1] * 20, 0))
    sp = [sphere('fl_spark_%d' % i, 0.06, ray if i % 2 else hot, 6, 4) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(sp, lambda t, i: (sj[i][0] * (0.3 + 1.6 * t), sj[i][1] * (0.3 + 1.6 * t), 8.4 - 13.0 * t), smax=1.2)
    rings = [torus('fl_ring_%d' % i, 0.6, 0.055, ring_m, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.3 - 6.0 * t), smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (0, 0, 360 * t))
    qs = [cone('fl_quill_%d' % i, 0.05, 1.0, ray, 5, rot=(180, 0, 0)) for i in range(6)]
    qj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(qs, lambda t, i: (qj[i][0] * (0.3 + 0.9 * t), qj[i][1] * (0.3 + 0.9 * t), 8.8 - 12.0 * t),
           smax=lambda t, i: 1.2 * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: sun burst - long thin rays shoot out sideways, a sun rises and fades, a fire ring
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, halo, 16, 8, loc=(cx, 0, 0.4))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.4, alpha=0.8)
    key(fl, f + 11, scale=3.2, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    rg = torus('im_ring', 0.5, 0.06, ring_m, 32, 5, loc=(cx, 0, 0.05))
    key(rg, IMPACT0, scale=0, alpha=1)
    key(rg, f, scale=0.3, alpha=1)
    key(rg, f + 13, scale=5.0, alpha=0)
    tidy(rg, 'impact', interp='LINEAR')
    ease_keys(rg)
    # 18 long thin rays, shot out horizontally from the contact point
    for k in range(18):
        a = math.radians(k * 20 + 5)
        ca, sa = math.cos(a), math.sin(a)
        long_ = k % 2 == 0
        h = 3.6 if long_ else 2.4
        rm = cone('im_ray_%d' % k, 0.07 if long_ else 0.06, h, ray if long_ else hot, 5, loc=(cx, 0, 0.3),
                  rot=aim((ca, sa, 0.04)))
        key(rm, IMPACT0, scale=0, alpha=1)
        key(rm, f, scale=(1, 1, 0.05), alpha=1)
        key(rm, f + 3, scale=(1.3, 1.3, 1.1), alpha=1)
        key(rm, f + 8, scale=(1.0, 1.0, 1.0), alpha=1)
        key(rm, f + 14, scale=(0.6, 0.6, 1.0), alpha=0.5)
        key(rm, f + 24, scale=(0.2, 0.2, 1.0), alpha=0)
        key(rm, IMPACT0 + 44, scale=0, alpha=0)
        tidy(rm, 'impact', interp='LINEAR')
    # the sun disc rises behind the spear and fades; eight short rays travel with it
    su = cyl('im_sun', 1.0, 0.1, ray, 28, 0.02, axis='Y', loc=(cx, 0.4, 0.3))
    key(su, IMPACT0, scale=0, alpha=1)
    key(su, f + 1, loc=(cx, 0.4, 0.3), scale=0.3, alpha=1)
    key(su, f + 10, loc=(cx, 0.4, 1.6), scale=1.0, alpha=1)
    key(su, f + 22, loc=(cx, 0.4, 2.9), scale=1.35, alpha=0.5)
    key(su, f + 32, loc=(cx, 0.4, 3.4), scale=1.5, alpha=0)
    key(su, IMPACT0 + 44, scale=0, alpha=0)
    tidy(su, 'impact', interp='LINEAR')
    sh = sphere('im_sun_halo', 1.5, halo, 20, 10, loc=(cx, 0.45, 0.3))
    key(sh, IMPACT0, scale=0, alpha=1)
    key(sh, f + 1, loc=(cx, 0.45, 0.3), scale=(0.3, 0.06, 0.3), alpha=1)
    key(sh, f + 10, loc=(cx, 0.45, 1.6), scale=(1.0, 0.2, 1.0), alpha=0.8)
    key(sh, f + 24, loc=(cx, 0.45, 2.9), scale=(1.4, 0.2, 1.4), alpha=0)
    key(sh, IMPACT0 + 44, scale=0, alpha=0)
    tidy(sh, 'impact', interp='LINEAR')
    for k in range(8):
        a = math.radians(k * 45 + 22)
        ca, sa = math.cos(a), math.sin(a)
        sr = cone('im_sunray_%d' % k, 0.09, 0.6, hot, 5, loc=(cx, 0.4, 0.3), rot=aim((ca, 0, sa)))
        key(sr, IMPACT0, scale=0, alpha=1)
        key(sr, f + 1, loc=(cx + 1.1 * 0.3 * ca, 0.4, 0.3 + 1.1 * 0.3 * sa), scale=0.3, alpha=1)
        key(sr, f + 10, loc=(cx + 1.15 * ca, 0.4, 1.6 + 1.15 * sa), scale=1.0, alpha=1)
        key(sr, f + 22, loc=(cx + 1.6 * ca, 0.4, 2.9 + 1.6 * sa), scale=1.2, alpha=0.4)
        key(sr, f + 30, loc=(cx + 1.8 * ca, 0.4, 3.3 + 1.8 * sa), scale=0.4, alpha=0)
        key(sr, IMPACT0 + 44, scale=0, alpha=0)
        tidy(sr, 'impact', interp='LINEAR')
    # fire ring: twelve flames on the ground
    for i in range(12):
        a = math.radians(i * 30 + 8)
        rr = 1.55
        fm = flame('im_flame_%d' % i, 0.95, 0.22, FL[i % 2], 0.1, 8, loc=(cx + rr * math.cos(a), rr * math.sin(a), 0.0))
        t0 = f + 5 + (i % 6)
        key(fm, IMPACT0, scale=0)
        key(fm, t0 - 1, scale=0)
        key(fm, t0, scale=(0.3, 0.3, 0.1))
        key(fm, t0 + 4, scale=(1.0, 1.0, 1.35))
        key(fm, t0 + 9, scale=(0.9, 0.9, 1.0))
        key(fm, t0 + 15, scale=(1.0, 1.0, 1.2))
        key(fm, IMPACT0 + 38, scale=(0.5, 0.5, 0.5))
        key(fm, IMPACT0 + 44, scale=0)
        tidy(fm, 'impact')
        ease_keys(fm)
    g = -0.028
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        s_ = rnd.uniform(0.05, 0.14)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.25, 0.38)))
        sk = sphere('im_spark_%d' % i, 0.06, ray if i % 2 else hot, 6, 4)
        spark_arc(sk, (cx, 0, 0.3), v, f + i % 4, g, 26, s=1.2)
    return True
