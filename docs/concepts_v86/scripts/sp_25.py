from spearlib import *

NAME = 'SP_25_abyss_anchor'
N = 25
BG = '#78b4cf'        # deep water, lit
GROUND = '#9fc0c4'    # seafloor silt
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'crown_spike': 'im_crown_0', 'shock_ring': 'im_shock', 'chain_link': 'im_link_0', 'bubble': 'im_bubble_0',
             'water_ring': 'fl_ring_0'}


def mats():
    return dict(
        iron=toon('aan_iron', '#53647a', '#2a3446', '#8fa3bd', spec=0.9, rim=0.55, rimcol='#7ff0e0'),
        dark=toon('aan_dark', '#2e3a4e', '#161d2a', '#566883', spec=0.7),
        patina=toon('aan_patina', '#3fae9c', '#1e6a68', '#8fe6d0', spec=0.6),
        barn=toon('aan_barn', '#e9e0c6', '#b3a785', '#fffaf0', spec=0.3),
        rope=toon('aan_rope', '#d9c28a', '#957a46', '#f6e4ae', spec=0.2),
        brass=toon('aan_brass', '#d9a53a', '#8c5a1c', '#ffe59a', spec=1.0),
        water=toon('aan_water', '#6fc8ee', '#2f7fb8', '#d2f4ff', spec=1.0, emit=0.3),
        glowc=glow('aan_core', '#58ffe0', 2.8),
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


def bounce(ob, p0, vh, f, spin, g=-0.05, rest=0.5, floor=0.1):
    """chain link drops, bounces on the ground, settles, then shrinks"""
    key(ob, IMPACT0, loc=p0, scale=0)
    key(ob, f, loc=p0, scale=1.0, rot=(0, 0, 0))
    p = Vector(p0)
    vz = 0.0
    t = 0
    while t < 30:
        t += 2
        vz += g * 2
        p = p + Vector((vh[0] * 2, vh[1] * 2, vz * 2))
        if p.z <= floor:
            p.z = floor
            vz = -vz * rest
            if abs(vz) < 0.08:
                vz = 0.0
                vh = (vh[0] * 0.3, vh[1] * 0.3)
        key(ob, f + t, loc=(p.x, p.y, p.z), scale=1.0, rot=(spin[0] * t, spin[1] * t, spin[2] * t), interp='LINEAR')
    key(ob, IMPACT0 + 38, scale=1.0)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    iron, dark, patina, barn, rope, brass, water, glowc = (M[k] for k in (
        'iron', 'dark', 'patina', 'barn', 'rope', 'brass', 'water', 'glowc'))
    # ---- tail: anchor ring pommel
    torus('pommel_ring', 0.3, 0.07, iron, 16, 6, loc=(0, 0, 0.45), axis='Y')
    sphere('pommel_boss', 0.2, dark, 10, 6, loc=(0, 0, 0.95), scale=(1, 1, 0.8))
    torus('pommel_collar', 0.17, 0.045, brass, 14, 6, loc=(0, 0, 1.12))
    # ---- shaft: dark iron with chain and rope wraps
    rod('shaft_lo', 0.155, 0.9, 3.3, dark, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.4, dark, r1=0.145)
    coil('chain_lo', 0.178, 0.04, 1.3, 1.9, 4, iron, segs=5)
    torus('chain_lo_cap', 0.18, 0.04, brass, 14, 6, loc=(0, 0, 1.92))
    coil('chain_hi', 0.176, 0.04, 3.12, 3.72, 4, iron, segs=5, phase=1.0)
    torus('chain_hi_cap', 0.178, 0.035, brass, 14, 6, loc=(0, 0, 3.1))
    for i, z in enumerate((4.2, 4.4)):
        torus('rope_band_%d' % i, 0.155, 0.03, rope, 14, 5, loc=(0, 0, z), ol=0.015)
    coil('rope_wrap', 0.165, 0.028, 4.6, 5.0, 4, rope, segs=5)
    # hanging chain draped from the socket
    for i in range(6):
        torus('hang_link_%d' % i, 0.085, 0.03, iron if i % 2 else dark, 10, 5, loc=(0.26, 0.0, 5.0 + i * 0.2), axis='X' if i % 2 else 'Y', ol=0.012)
    for i, (z, a) in enumerate(((3.9, 0.5), (5.3, 3.0), (5.6, 5.0))):
        sphere('barn_%d' % i, 0.07, barn, 7, 4, loc=(0.145 * math.cos(a), 0.145 * math.sin(a), z), scale=(1, 1, 0.8), ol=0.012)
    # ---- socket: iron collar with glowing abyssal gem
    lathe('socket', [(6.3, 0.14), (6.45, 0.2), (6.7, 0.28), (6.95, 0.3), (7.05, 0.2), (7.1, 0.0)], iron, 14)
    torus('socket_ring_a', 0.22, 0.05, brass, 14, 6, loc=(0, 0, 6.5))
    torus('socket_ring_b', 0.3, 0.05, patina, 14, 6, loc=(0, 0, 6.98))
    sphere('socket_gem', 0.12, glowc, 8, 5, loc=(0, -0.27, 6.75), ol=0.0)
    # ---- the anchor head: thick spike shank + stock + two curved arms with big flukes
    shank = tube('shank', [(0, 0, 6.95), (0, 0, 7.6), (0, 0, 8.3), (0, 0, 8.9), (0, 0, TIP)], [0.3, 0.32, 0.27, 0.17, 0.0], iron, 10)
    shank.scale = (1.0, 0.72, 1.0)
    cyl('stock', 0.1, 1.5, dark, 10, loc=(0, 0, 8.2), axis='X')
    for s in (-1, 1):
        nm = 'a' if s < 0 else 'b'
        sphere('stock_ball_' + nm, 0.15, patina, 8, 5, loc=(s * 0.78, 0, 8.2), ol=0.012)
        arm = tube('arm_' + nm, [(s * 0.1, 0, 7.0), (s * 0.55, 0, 6.85), (s * 0.95, 0, 7.05), (s * 1.12, 0, 7.5), (s * 1.08, 0, 7.8)],
                   [0.2, 0.2, 0.17, 0.14, 0.1], iron, 8)
        arm.scale = (1.0, 0.75, 1.0)
        blade('fluke_' + nm, [(s * 1.1, 7.55), (s * 1.62, 7.7), (s * 1.28, 8.25), (s * 0.98, 8.0)] if s > 0 else
              [(-0.98, 8.0), (-1.28, 8.25), (-1.62, 7.7), (-1.1, 7.55)], 0.09, patina)
        sphere('fluke_rivet_' + nm, 0.07, brass, 7, 4, loc=(s * 1.1, 0.1, 7.7), ol=0.01)
    glowseam = tube('shank_seam', [(0, -0.2, 7.3), (0, -0.2, 7.9), (0, -0.16, 8.6)], [0.0, 0.05, 0.0], glowc, 5, ol=0)
    for i, (x, z, r) in enumerate(((0.28, 7.5, 0.08), (-0.25, 8.0, 0.07), (0.2, 8.7, 0.06), (-0.95, 7.1, 0.08), (0.9, 7.15, 0.07))):
        sphere('head_barn_%d' % i, r, barn, 7, 4, loc=(x, -0.18 if i < 3 else -0.15, z), scale=(1, 0.7, 0.7), ol=0.01)
    # ---- shell charm
    tube('charm_cord', [(0.15, 0.04, 6.4), (0.32, 0.08, 6.1), (0.4, 0.1, 5.8)], 0.02, rope, 5)
    cone('charm_hook', 0.07, 0.3, brass, 6, loc=(0.4, 0.1, 5.82), rot=(180, 0, 0), ol=0.012)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(2525)
    bub = ghost('aan_bubble', '#d8fbff', 1.4, 0.85, 2.2, edge=True)
    aura = ghost('aan_aura', '#4fffe0', 1.2, 0.05, 1.8)
    ring_m = glow('aan_ring', '#58ffe0', 2.4)
    spray = ghost('aan_spray', '#eaffff', 1.2, 0.75, 1.1)
    glint = glow('aan_glint', '#c8fff4', 2.8)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.7, aura, 14, 8, loc=(0, 0, 7.7), scale=(1.5, 0.8, 1.5))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 1.0)
        sphere('idle_bubble_%d' % i, rnd.uniform(0.06, 0.12), bub, 10, 6, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.14, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.4, 1.0), -0.3, 7.2 + i * 0.6), rot=(90, 0, 0))
    # ---------------- flight
    fx('flight')
    bubs = [sphere('fl_bubble_%d' % i, 0.15, bub, 10, 6) for i in range(12)]
    bj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.6, 1.3)) for _ in range(12)]
    stream(bubs, lambda t, i: (bj[i][0] * (0.25 + 1.0 * t) + 0.2 * math.sin(6 * t + i), bj[i][1] * (0.25 + 1.0 * t), 8.4 - 12.0 * t),
           smax=lambda t, i: bj[i][2] * (0.7 + 1.0 * t) * math.sin(math.pi * t) ** 0.4)
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.34, M['patina'], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(shards, lambda t, i: (sj[i][0] * (0.35 + 0.9 * t), sj[i][1] * (0.35 + 0.9 * t), 8.8 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    links = [torus('fl_link_%d' % i, 0.09, 0.03, M['iron'], 10, 5, axis='X' if i % 2 else 'Y') for i in range(5)]
    lj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(5)]
    stream(links, lambda t, i: (lj[i][0] * (0.4 + 0.8 * t), lj[i][1] * (0.4 + 0.8 * t), 8.0 - 12.0 * t),
           smax=1.3, spin=lambda t, i: (lj[i][2] + 360 * t, 200 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, ring_m, 28, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.0 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    # ---------------- impact: shockwave + water crown, chain links drop and bounce
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.7)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('aan_flash', '#c8fff4', 1.8, 0.6, 1.3), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.7)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    for k in range(3):
        sh = torus('im_shock' if k == 0 else 'im_shock_%d' % k, 0.5, 0.07 - k * 0.012, ring_m, 40, 5, loc=(cx, 0, 0.05 + k * 0.01))
        key(sh, IMPACT0, scale=0, alpha=1)
        key(sh, f + k * 3, scale=0.3, alpha=1)
        key(sh, f + k * 3 + 14, scale=6.0 - k * 1.2, alpha=0)
        tidy(sh, 'impact', interp='LINEAR')
        ease_keys(sh)
    # splash crown: 12 curved water spikes around the spear
    for k in range(12):
        a = math.radians(k * 30 + 8)
        R = 0.7 + 0.12 * (k % 2)
        h = 1.2 + 0.4 * (k % 3 == 0)
        sp = tube('im_crown_%d' % k, [(0, 0, 0), (0.06, 0, h * 0.45), (0.22, 0, h * 0.85), (0.45, 0, h)], [0.15, 0.12, 0.08, 0.0], M['water'], 6,
                  loc=(cx + R * math.cos(a), R * math.sin(a), 0.0), rot=(0, 0, math.degrees(a)))
        t0 = f + (k % 4)
        key(sp, IMPACT0, scale=0)
        key(sp, t0, scale=(0.4, 0.6, 0.1))
        key(sp, t0 + 5, scale=(1.0, 1.0, 1.2))
        key(sp, t0 + 10, scale=(1.0, 1.0, 1.0))
        key(sp, t0 + 20, scale=(0.9, 0.9, 0.5))
        key(sp, t0 + 28, scale=0)
        tidy(sp, 'impact')
        ease_keys(sp)
    # chain links raining down and bouncing
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.4, 1.6)
        lk = torus('im_link_%d' % i, 0.1, 0.035, M['iron'] if i % 2 else M['dark'], 10, 5, axis='X' if i % 2 else 'Y', ol=0.015)
        p0 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(2.6, 4.2))
        bounce(lk, p0, (0.012 * math.cos(a), 0.012 * math.sin(a)), f + rnd.randint(0, 6), (rnd.uniform(-8, 8), rnd.uniform(-8, 8), rnd.uniform(-10, 10)))
    for i in range(12):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.3, 0.46)))
        dp = sphere('im_drop_%d' % i, rnd.uniform(0.07, 0.13), M['water'], 7, 4)
        toss(dp, Vector((cx, 0, 0.2)), v, f + rnd.randint(0, 4), floor=0.06, spin=(0, 0, 0), hold=30)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.2, 1.4)
        b = sphere('im_bubble_%d' % i, rnd.uniform(0.08, 0.2), bub, 10, 6)
        t0 = f + rnd.randint(0, 12)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.1)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(2.0, 3.4))
        key(b, IMPACT0, loc=p0, scale=0)
        key(b, t0, loc=p0, scale=0.3)
        key(b, t0 + 6, scale=1.0)
        key(b, min(t0 + 24, IMPACT0 + 44), loc=p1, scale=0.0)
        tidy(b, 'impact')
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.8)
        sm = sphere('im_mist_%d' % i, 0.35, spray, 12, 7)
        t0 = f + 3 + rnd.randint(0, 6)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.6, 2.6))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.2), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    return True
