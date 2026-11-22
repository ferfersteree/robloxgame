from spearlib import *

NAME = 'SP_02_bone'
N = 2
BG = '#8fb87a'        # meadow
GROUND = '#b5d68a'
TIP = 9.2
TRAIL = 5.2
FX_EXPORT = {'bone_splinter': 'im_splinter_0', 'dust_ring': 'im_ring', 'crater': 'im_crater',
             'pebble': 'im_pebble_0', 'chip': 'fl_chip_0'}


def mats():
    return dict(
        bone=toon('b02_bone', '#f1e6c8', '#b99f72', '#fffaf0', spec=0.5),
        bone_dk=toon('b02_bone_dk', '#cdb68a', '#8f7650', '#ece0bd', spec=0.3),
        sinew=toon('b02_sinew', '#c98f5a', '#8a5530', '#f0bd88', spec=0.2),
        ochre=toon('b02_ochre', '#d9562f', '#9c2e22', '#ff8a60'),
        teal=toon('b02_teal', '#2fb3a0', '#177a78', '#7fe6d2'),
        char=toon('b02_char', '#4a3a36', '#241a1c', '#7a6660', spec=0.3),
        dust=ghost('b02_dust', '#f4ecd6', 1.1, 0.85, 1.1),
        dust_dk=ghost('b02_dust_dk', '#cfc09a', 1.0, 0.85, 1.1),
        glint=glow('b02_glint', '#fffbe6', 2.2),
        ring=glow('b02_ring', '#fff6dc', 1.8),
        stone=toon('b02_stone', '#a59c8c', '#6a6258', '#d0c7b6'),
    )


def pop(ob, t0, s=1.0, end=39, over=1.15, rise=4):
    """scale 0 -> overshoot -> s, hold, back to 0 by IMPACT0 + 44"""
    s = (s, s, s) if isinstance(s, (int, float)) else tuple(s)
    key(ob, IMPACT0, scale=0)
    key(ob, t0, scale=0)
    key(ob, t0 + rise, scale=tuple(a * over for a in s))
    key(ob, t0 + rise + 3, scale=s)
    key(ob, IMPACT0 + end, scale=s)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def ballistic(c, p0, v, f, g=-0.028, spin=(25, 18), hold=IMPACT0 + 36, rest=0.05, sc=1.0, rot0=0.0):
    p0 = Vector(p0)
    key(c, IMPACT0, loc=p0, scale=0)
    if f - 1 > IMPACT0:
        key(c, f - 1, loc=p0, scale=0)
    key(c, f, loc=p0, scale=0.2 * sc)
    t = 0
    while True:
        t += 2
        p = p0 + v * t + Vector((0, 0, 0.5 * g * t * t))
        done = p.z <= rest or t > 34
        if done:
            p.z = rest
        key(c, f + t, loc=p, scale=sc, rot=(rot0 + t * spin[0], t * spin[1], 0), interp='LINEAR')
        if done:
            break
    key(c, max(f + t + 2, hold), scale=sc)
    key(c, IMPACT0 + 44, scale=0)
    tidy(c, 'impact')
    return p


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    bone, bone_dk, sinew, ochre, teal, char = (M[k] for k in ('bone', 'bone_dk', 'sinew', 'ochre', 'teal', 'char'))
    # ---- tail: femur condyles (two knobs) + flared neck
    sphere('tail_knob_a', 0.25, bone, 10, 6, loc=(-0.11, 0.0, 0.29), scale=(1, 1.05, 1.1))
    sphere('tail_knob_b', 0.25, bone, 10, 6, loc=(0.11, 0.0, 0.29), scale=(1, 1.05, 1.1))
    lathe('tail_neck', [(0.35, 0), (0.35, 0.2), (0.5, 0.2), (0.7, 0.17), (0.82, 0.155), (0.82, 0)], bone_dk, 12)
    torus('tail_band', 0.2, 0.04, ochre, 12, 5, loc=(0, 0, 0.5))
    coil('tail_wrap', 0.175, 0.03, 0.88, 1.2, 3, sinew, segs=5)
    # ---- shaft: bone, bare in the grip zone 2.0-3.0
    rod('shaft_lo', 0.155, 0.8, 3.3, bone, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.3, bone, segs=12, r1=0.14)
    coil('sinew_lo', 0.18, 0.03, 1.4, 1.9, 4, sinew, segs=5)
    torus('sinew_lo_cap', 0.18, 0.04, ochre, 12, 5, loc=(0, 0, 1.93))
    coil('sinew_hi', 0.175, 0.03, 3.1, 3.66, 4, sinew, segs=5, phase=1.0)
    torus('sinew_hi_cap', 0.175, 0.04, ochre, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.35, 4.55, 4.75)):
        torus('band_%d' % i, 0.148, 0.025 if i != 1 else 0.035, teal if i == 1 else ochre, 12, 5, loc=(0, 0, z), ol=0.015)
    for i, (z, a, r) in enumerate(((1.62, 0.5, 0.075), (4.15, 2.6, 0.085), (5.3, 4.4, 0.08))):
        sphere('bump_%d' % i, r, bone_dk, 8, 5, loc=(0.14 * math.cos(a), 0.14 * math.sin(a), z), scale=(1, 1, 1.4), ol=0.012)
    # ---- knobby head: femur ball + five knuckles + collar
    lathe('socket', [(6.15, 0.14), (6.3, 0.2), (6.55, 0.26), (6.8, 0.24), (6.95, 0.17), (6.95, 0)], bone_dk, 12)
    coil('lash', 0.265, 0.035, 6.3, 6.75, 4, sinew, segs=5, phase=0.5)
    torus('socket_ring', 0.27, 0.045, ochre, 12, 5, loc=(0, 0, 6.2))
    sphere('head_ball', 0.38, bone, 12, 7, loc=(0, 0, 6.85), scale=(1, 0.9, 0.85))
    for i in range(5):
        a = math.radians(i * 72 + 20)
        sphere('knuckle_%d' % i, 0.13, bone_dk if i % 2 else bone, 8, 5, loc=(0.38 * math.cos(a), 0.34 * math.sin(a), 6.85 + 0.06 * (i % 2)), ol=0.015)
    # ---- jagged bone point: broken femur shard + side splinters
    shard = [(0.26, 6.9), (0.40, 7.25), (0.27, 7.45), (0.34, 7.9), (0.19, 8.1), (0.2, 8.6), (0.08, 8.85), (0.0, TIP),
             (-0.07, 8.8), (-0.18, 8.4), (-0.2, 7.95), (-0.34, 7.6), (-0.3, 7.15), (-0.2, 6.9)]
    shard = [(x * 1.5, z) for (x, z) in shard]   # (lead fix) wider shard
    blade('point', shard, 0.15, bone)
    blade('point_core', [(x * 0.5, 7.15 + (z - 7.0) * 0.82) for (x, z) in shard], 0.17, bone_dk, ol=0.012)
    cone('jag_a', 0.1, 0.55, bone, 5, loc=(0.5, 0.0, 7.55), rot=(0, 62, 0), ol=0.015)
    cone('jag_b', 0.085, 0.5, bone, 5, loc=(-0.45, 0.0, 7.85), rot=(0, -64, 0), ol=0.015)
    cone('jag_c', 0.07, 0.4, bone_dk, 5, loc=(0.3, 0.0, 8.2), rot=(0, 58, 0), ol=0.015)
    # ---- sinew cord + skull charm
    tube('charm_cord', [(0.22, 0.04, 6.4), (0.36, 0.07, 6.1), (0.42, 0.09, 5.8)], 0.022, sinew, 5)
    for i, (z, m) in enumerate(((6.2, teal), (6.0, ochre))):
        sphere('bead_%d' % i, 0.06, m, 8, 5, loc=(0.34 + i * 0.04, 0.07 + i * 0.01, z), ol=0.012)
    sphere('skull', 0.17, bone, 10, 6, loc=(0.42, 0.09, 5.6), scale=(1.0, 0.9, 0.95))
    box('skull_jaw', (0.15, 0.12, 0.09), bone_dk, bev=0.02, bsegs=1, loc=(0.42, 0.0, 5.4))
    for s in (-1, 1):
        sphere('skull_eye_%d' % (s + 1), 0.04, char, 6, 4, loc=(0.42 + s * 0.06, -0.04, 5.62), ol=0.0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(202)
    dust, dust_dk, glint, ring_m = M['dust'], M['dust_dk'], M['glint'], M['ring']
    # ---------------- idle: bone dust motes + glints near the head
    fx('idle')
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.45, 0.75)
        sphere('idle_mote_%d' % i, rnd.uniform(0.05, 0.09), dust_dk if i % 2 else dust, 8, 5,
               loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.0)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.13, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.35, 0.6), -0.2, 7.4 + i * 0.6),
             rot=(90, 0, 0))
    # ---------------- flight: pale dust puffs + tumbling bone chips + air rings
    fx('flight')
    puffs = [sphere('fl_puff_%d' % i, 0.34, dust if i % 3 else dust_dk, 12, 7) for i in range(10)]
    jit = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(10)]
    stream(puffs, lambda t, i: (jit[i][0] * (0.15 + 0.9 * t), jit[i][1] * (0.15 + 0.9 * t), 7.6 - 12.0 * t),
           smax=lambda t, i: (0.5 + 1.5 * t) * math.sin(math.pi * t) ** 0.5)
    chips = [cone('fl_chip_%d' % i, 0.07, 0.34, M['bone'] if i % 2 else M['bone_dk'], 5, ol=0.012) for i in range(8)]
    cj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(chips, lambda t, i: (cj[i][0] * (0.3 + 0.8 * t), cj[i][1] * (0.3 + 0.8 * t), 8.6 - 13.0 * t),
           smax=1.0, spin=lambda t, i: (cj[i][2] + 720 * t, 540 * t, 0))
    rings = [torus('fl_ring_%d' % i, 0.45, 0.035, ring_m, 24, 5) for i in range(3)]
    stream(rings, lambda t, i: (0, 0, 9.5 - 6.5 * t), smax=lambda t, i: (0.6 + 1.4 * t) * math.sin(math.pi * t) ** 0.4)
    spk = [sphere('fl_speck_%d' % i, 0.05, glint, 6, 4) for i in range(4)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(4)]
    stream(spk, lambda t, i: (sj[i][0] * (0.3 + 1.2 * t), sj[i][1] * (0.3 + 1.2 * t), 8.2 - 11.0 * t), smax=1.0)
    # ---------------- impact: low dust ring, bone splinters stick upright in a fan, pebbles
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.6)
    f = IMPACT0 + 4
    cx = 0.45
    crater = torus('im_crater', 0.5, 0.15, M['bone_dk'], 18, 6, loc=(cx, 0, 0.0))
    key(crater, IMPACT0, scale=0)
    key(crater, f, scale=0)
    key(crater, f + 3, scale=(1.15, 1.15, 0.5))
    key(crater, f + 6, scale=(1, 1, 0.45))
    key(crater, IMPACT0 + 40, scale=(1, 1, 0.45))
    key(crater, IMPACT0 + 44, scale=0)
    tidy(crater, 'impact')
    for i in range(5):
        a = math.radians(i * 72 + 20)
        L_ = rnd.uniform(0.8, 1.3)
        pts = [(cx + 0.45 * math.cos(a), 0.45 * math.sin(a), 0.01), (cx + (0.45 + L_ * 0.5) * math.cos(a + 0.15), (0.45 + L_ * 0.5) * math.sin(a + 0.15), 0.01),
               (cx + (0.45 + L_) * math.cos(a - 0.05), (0.45 + L_) * math.sin(a - 0.05), 0.01)]
        cr = tube('im_crack_%d' % i, pts, [0.055, 0.04, 0.0], M['char'], 4, ol=0)
        cr.scale = (1, 1, 0.3)
        key(cr, IMPACT0, scale=0)
        key(cr, f, scale=0)
        key(cr, f + 4, scale=(1, 1, 0.3))
        key(cr, IMPACT0 + 40, scale=(1, 1, 0.3))
        key(cr, IMPACT0 + 44, scale=0)
        tidy(cr, 'impact')
    shock = torus('im_ring', 0.5, 0.05, M['ring'], 32, 5, loc=(cx, 0, 0.05))
    key(shock, IMPACT0, scale=0, alpha=1)
    key(shock, f, scale=0.3, alpha=1)
    key(shock, f + 12, scale=4.6, alpha=0)
    tidy(shock, 'impact', interp='LINEAR')
    ease_keys(shock)
    # low dust ring: flat puffs that roll outwards along the ground
    for i in range(14):
        a = math.radians(i * 360 / 14 + rnd.uniform(-8, 8))
        rr = rnd.uniform(1.5, 2.3) * (1.25 if math.cos(a) < 0 else 1.0)
        p = sphere('im_dust_%d' % i, 0.34, dust if i % 3 else dust_dk, 12, 7)
        end = (cx + rr * math.cos(a), rr * math.sin(a), 0.22)
        key(p, IMPACT0, loc=(cx, 0, 0.15), scale=0, alpha=1)
        key(p, f, loc=(cx, 0, 0.15), scale=(0.3, 0.3, 0.2), alpha=1)
        key(p, f + 10, loc=end, scale=(1.5, 1.5, 0.8), alpha=0.9)
        key(p, IMPACT0 + 44, loc=(end[0] * 1.04 - 0.02, end[1] * 1.04, end[2] + 0.2), scale=(2.1, 2.1, 1.0), alpha=0)
        tidy(p, 'impact')
        ease_keys(p)
    # five bone splinters fly back and stick upright in a fan behind the spear
    for i in range(5):
        a = math.radians(150 + i * 15)
        rr = 1.5 + 0.25 * (i % 2)
        land = (cx + rr * math.cos(a), rr * math.sin(a), -0.08)
        mid = (cx + 0.5 * rr * math.cos(a), 0.5 * rr * math.sin(a), 1.9)
        sp = cone('im_splinter_%d' % i, 0.09, 0.95 - 0.1 * (i % 2), M['bone'] if i % 2 else M['bone_dk'], 5, loc=(cx, 0, 0.3), ol=0.02)
        rl = aim((math.cos(a) * 0.3, math.sin(a) * 0.3, 1.0))
        key(sp, IMPACT0, loc=(cx, 0, 0.3), scale=0)
        key(sp, f, loc=(cx, 0, 0.3), rot=(0, -80, 0), scale=0)
        key(sp, f + 1, loc=(cx, 0, 0.4), rot=(0, -90, 0), scale=0.6)
        key(sp, f + 5, loc=mid, rot=(140, -150, 0), scale=1.0)
        key(sp, f + 10 + i, loc=land, rot=rl, scale=1.0)
        key(sp, f + 13 + i, loc=(land[0], land[1], land[2] + 0.06), rot=rl, scale=1.0)
        key(sp, IMPACT0 + 38, scale=1.0)
        key(sp, IMPACT0 + 44, scale=0)
        tidy(sp, 'impact')
    # pebbles and small bone chips
    g = -0.028
    for i in range(14):
        a = math.radians(rnd.uniform(0, 360))
        s_ = rnd.uniform(0.08, 0.17)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.2, 0.34)))
        m = M['stone'] if i % 3 else M['bone_dk']
        c = rock('im_pebble_%d' % i, rnd.uniform(0.08, 0.16), m, seed=i + 30, sub=1, rough=0.25, flat=True)
        ballistic(c, (cx, 0, 0.15), v, f, g, rot0=rnd.uniform(0, 360))
    for i in range(6):
        a = math.radians(rnd.uniform(90, 270))
        s_ = rnd.uniform(0.1, 0.18)
        v = Vector((s_ * math.cos(a), s_ * math.sin(a), rnd.uniform(0.25, 0.4)))
        c = cone('im_chip_%d' % i, 0.05, 0.22, M['bone'], 4, loc=(0, 0, 0), ol=0.01)
        ballistic(c, (cx, 0, 0.2), v, f, g, spin=(35, 20), rot0=rnd.uniform(0, 360), rest=0.04)
    return True
