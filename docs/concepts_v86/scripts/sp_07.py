from spearlib import *

NAME = 'SP_07_crystal'
N = 7
BG = '#5f6a9a'        # canyon
GROUND = '#7d86b0'
TIP = 9.3
TRAIL = 5.2
FX_EXPORT = {'chime_ring': 'im_chime_0', 'hex_crystal': 'im_hex_0', 'hex_ring': 'im_hexring',
             'sparkle': 'im_spark_0', 'drift_crystal': 'fl_shard_0'}


def mats():
    return dict(
        crys=toon('b07_crys', '#6fc8ff', '#2f78d0', '#d8f4ff', spec=1.0, rim=0.7, rimcol='#ffffff', emit=0.45),
        crys_core=toon('b07_crys_core', '#c8f4ff', '#6fc8ff', '#ffffff', spec=1.0, emit=0.9),
        crys_vio=toon('b07_crys_vio', '#9a8aff', '#5a3ad0', '#d8d0ff', spec=1.0, emit=0.4),
        silver=toon('b07_silver', '#c8d2e0', '#7a88a0', '#ffffff', spec=1.0, rim=0.5),
        silver_dk=toon('b07_silver_dk', '#8e9ab2', '#505c78', '#d0d8e8', spec=0.8),
        indigo=toon('b07_indigo', '#4a5a98', '#283468', '#8a9ae0'),
        indigo_dk=toon('b07_indigo_dk', '#34407a', '#1a224c', '#6070b8'),
        cyan=glow('b07_cyan', '#5ff0ff', 2.2),
        white=glow('b07_white', '#f0fcff', 2.2),
        ring=glow('b07_ring', '#7fe6ff', 2.2),
        aura=ghost('b07_aura', '#9adcff', 1.4, 0.14, 1.6),
        flash=ghost('b07_flash', '#c8f8ff', 1.8, 0.6, 1.2),
        sand=toon('b07_sand', '#a8643e', '#6a3a22', '#d89a6a'),
    )


def twinkle(ob, t0, p0, p1, s=1.2, life=22):
    key(ob, IMPACT0, loc=p0, scale=0)
    key(ob, t0, loc=p0, scale=0)
    key(ob, t0 + 4, loc=Vector(p0).lerp(Vector(p1), 0.35), scale=s)
    key(ob, t0 + life // 2, loc=Vector(p0).lerp(Vector(p1), 0.7), scale=s * 0.5)
    key(ob, t0 + life, loc=p1, scale=0)
    key(ob, IMPACT0 + 44, scale=0)
    tidy(ob, 'impact')


def build():
    begin(NAME, N, ol=0.03)
    M = mats()
    crys, core, vio, silver, silver_dk, indigo, indigo_dk, cyan = (M[k] for k in (
        'crys', 'crys_core', 'crys_vio', 'silver', 'silver_dk', 'indigo', 'indigo_dk', 'cyan'))
    # ---- tail: silver cap with a violet crystal drop
    lathe('tail_cap', [(0.35, 0), (0.35, 0.15), (0.5, 0.21), (0.7, 0.2), (0.85, 0.16), (0.85, 0)], silver, 12)
    crystal('tail_drop', 0.15, 0.5, vio, 5, 0.35, 0.7, loc=(0, 0, 0.52), rot=(180, 0, 0), ol=0.02)
    torus('tail_ring', 0.2, 0.04, silver_dk, 12, 5, loc=(0, 0, 0.62))
    # ---- shaft: indigo lacquer, bare grip zone
    rod('shaft_lo', 0.155, 0.85, 3.3, indigo, segs=12, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.0, indigo_dk, segs=12, r1=0.14)
    coil('wire_lo', 0.175, 0.022, 1.35, 1.88, 5, silver, segs=5)
    torus('wire_lo_cap', 0.18, 0.04, silver, 12, 5, loc=(0, 0, 1.93))
    coil('wire_hi', 0.172, 0.022, 3.1, 3.62, 5, silver, segs=5, phase=1.0)
    torus('wire_hi_cap', 0.178, 0.04, silver, 12, 5, loc=(0, 0, 3.07))
    for i, z in enumerate((4.05, 4.25, 4.45)):
        torus('band_%d' % i, 0.148, 0.025, (silver, cyan, silver)[i], 12, 5, loc=(0, 0, z), ol=0.012)
    # small crystal studs radiating from the shaft (outside the grip zone)
    for i, z in enumerate((1.5, 1.6, 3.35, 3.8, 4.7, 5.05, 5.4)):
        a = i * 2.4 + 0.5
        ca, sa = math.cos(a), math.sin(a)
        crystal('stud_%d' % i, 0.06, 0.26, crys if i % 2 else vio, 5, 0.35, 0.8, loc=(0.13 * ca, 0.13 * sa, z),
                rot=aim((ca, sa, 0.35)), ol=0.012)
    # ---- silver claw setting
    lathe('socket', [(5.95, 0.14), (6.15, 0.22), (6.45, 0.3), (6.7, 0.34), (6.85, 0.3), (6.85, 0)], silver, 14)
    torus('socket_ring', 0.3, 0.05, silver_dk, 14, 5, loc=(0, 0, 6.22))
    torus('socket_ring_hi', 0.34, 0.05, cyan, 14, 5, loc=(0, 0, 6.8), ol=0.012)
    for i in range(5):
        a = math.radians(i * 72 + 36)
        ca, sa = math.cos(a), math.sin(a)
        pts = [(0.32 * ca, 0.32 * sa, 6.75), (0.5 * ca, 0.5 * sa, 7.25), (0.44 * ca, 0.44 * sa, 7.8), (0.26 * ca, 0.26 * sa, 8.2)]
        tube('claw_%d' % i, pts, [0.075, 0.07, 0.055, 0.0], silver, 6)
    torus('claw_ring', 0.47, 0.035, silver_dk, 14, 5, loc=(0, 0, 7.45), ol=0.012)
    # ---- the crystal: main point, inner bright core, base cluster
    crystal('gem', 0.44, 2.75, crys, 6, 0.36, 0.85, loc=(0, 0, 6.55))
    crystal('gem_core', 0.2, 2.1, core, 6, 0.36, 0.85, loc=(0, 0, 6.85), ol=0.0)
    for i in range(3):
        a = math.radians(i * 120 + 20)
        crystal('cluster_%d' % i, 0.17, 1.15 - 0.1 * i, crys if i != 1 else vio, 5, 0.35, 0.8,
                loc=(0.4 * math.cos(a), 0.4 * math.sin(a), 6.7), rot=aim((math.cos(a) * 0.55, math.sin(a) * 0.55, 1.0)), ol=0.02)
    # ---- silver chain charm with a crystal drop
    tube('charm_chain', [(0.2, 0.04, 5.95), (0.32, 0.08, 5.7), (0.36, 0.1, 5.45)], 0.02, silver, 5)
    crystal('charm_drop', 0.09, 0.4, crys, 5, 0.35, 0.8, loc=(0.36, 0.1, 5.1), ol=0.012)
    torus('charm_ring', 0.05, 0.02, silver_dk, 10, 4, loc=(0.36, 0.1, 5.5), rot=(90, 0, 0), ol=0.01)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(707)
    cyan, white, ring_m, aura, flash_m = M['cyan'], M['white'], M['ring'], M['aura'], M['flash']
    # ---------------- idle: faint aura, glints, tiny floating crystals
    fx('idle')
    sphere('idle_aura', 0.6, aura, 16, 9, loc=(0, 0, 7.9), scale=(1.0, 0.9, 2.1))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.03, 4, 0.02, white, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.45, 0.8), -0.2, 7.5 + i * 0.7),
             rot=(90, 0, 0))
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 0.95)
        crystal('idle_mote_%d' % i, 0.035, 0.18, M['crys'], 4, 0.4, 0.8, both=True,
                loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(7.0, 9.2)), rot=(rnd.uniform(0, 40), rnd.uniform(0, 40), 0), ol=0.01)
    # ---------------- flight: crystal shards, sparkle stars, chime rings
    fx('flight')
    shards = [crystal('fl_shard_%d' % i, 0.07, 0.36, M['crys'] if i % 2 else M['crys_vio'], 5, 0.4, 0.8, both=True, ol=0.012) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(shards, lambda t, i: (sj[i][0] * (0.3 + 0.9 * t), sj[i][1] * (0.3 + 0.9 * t), 8.8 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (sj[i][2] + 540 * t, 360 * t, 0))
    stars = [star('fl_star_%d' % i, 0.16, 0.04, 4, 0.02, white if i % 2 else cyan, rot=(90, 0, 0)) for i in range(8)]
    tj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(8)]
    stream(stars, lambda t, i: (tj[i][0] * (0.3 + 1.0 * t), tj[i][1] * (0.3 + 1.0 * t), 8.5 - 12.0 * t),
           smax=lambda t, i: 1.3 * math.sin(math.pi * t) ** 0.5)
    rings = [torus('fl_ring_%d' % i, 0.5, 0.04, ring_m, 24, 5) for i in range(4)]
    stream(rings, lambda t, i: (0, 0, 9.4 - 7.0 * t), smax=lambda t, i: (0.5 + 1.6 * t) * math.sin(math.pi * t) ** 0.4)
    mt = [sphere('fl_mote_%d' % i, 0.05, white, 6, 4) for i in range(4)]
    mj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(4)]
    stream(mt, lambda t, i: (mj[i][0] * (0.2 + 1.1 * t), mj[i][1] * (0.2 + 1.1 * t), 8.0 - 11.0 * t), smax=1.2)
    # ---------------- impact: CHIME - rings rise like sound waves, a crystal hexagon grows, sparkles
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    fl = sphere('im_flash', 0.5, flash_m, 16, 8, loc=(cx, 0, 0.3))
    key(fl, IMPACT0, scale=0, alpha=1)
    key(fl, f, scale=0.4, alpha=1)
    key(fl, f + 4, scale=2.0, alpha=0.7)
    key(fl, f + 10, scale=2.8, alpha=0)
    tidy(fl, 'impact', interp='LINEAR')
    sh = torus('im_shock', 0.5, 0.05, ring_m, 32, 5, loc=(cx, 0, 0.05))
    key(sh, IMPACT0, scale=0, alpha=1)
    key(sh, f, scale=0.3, alpha=1)
    key(sh, f + 12, scale=4.4, alpha=0)
    tidy(sh, 'impact', interp='LINEAR')
    ease_keys(sh)
    # three big chime rings + three inner ones rising and widening
    for k in range(6):
        big = k < 3
        rg = torus('im_chime_%d' % k, 0.6 if big else 0.4, 0.055 if big else 0.04, ring_m, 32, 5, loc=(cx, 0, 0.2))
        t0 = f + (k % 3) * 5
        key(rg, IMPACT0, scale=0, alpha=1, loc=(cx, 0, 0.2))
        key(rg, t0 - 1, scale=0, alpha=1, loc=(cx, 0, 0.2))
        key(rg, t0, scale=0.4, alpha=1, loc=(cx, 0, 0.2))
        key(rg, t0 + 10, scale=(1.5 if big else 1.0), alpha=0.8, loc=(cx, 0, 1.6 + (0 if big else 0.4)))
        key(rg, t0 + 22, scale=(2.3 if big else 1.5), alpha=0, loc=(cx, 0, 3.4 + (0 if big else 0.6)))
        key(rg, IMPACT0 + 44, scale=0, alpha=0)
        tidy(rg, 'impact', interp='LINEAR')
    # hexagon of six crystals at a fixed radius + a hexagonal glow ring
    hx = torus('im_hexring', 1.5, 0.05, ring_m, 6, 4, loc=(cx, 0, 0.04))
    key(hx, IMPACT0, scale=0, alpha=1)
    key(hx, f + 2, scale=0, alpha=1)
    key(hx, f + 8, scale=1.0, alpha=1)
    key(hx, IMPACT0 + 32, scale=1.0, alpha=0.9)
    key(hx, IMPACT0 + 44, scale=0, alpha=0)
    tidy(hx, 'impact')
    for k in range(6):
        a = math.radians(k * 60)
        ca, sa = math.cos(a), math.sin(a)
        t0 = f + 2 + k
        c = crystal('im_hex_%d' % k, 0.2, 1.15, M['crys'] if k % 2 else M['crys_vio'], 6, 0.35, 0.8,
                    loc=(cx + 1.5 * ca, 1.5 * sa, -0.05), rot=aim((ca * 0.15, sa * 0.15, 1.0)), ol=0.02)
        key(c, IMPACT0, scale=0)
        key(c, t0, scale=0)
        key(c, t0 + 4, scale=(1.15, 1.15, 1.25))
        key(c, t0 + 8, scale=1.0)
        key(c, IMPACT0 + 38, scale=1.0)
        key(c, IMPACT0 + 44, scale=0)
        tidy(c, 'impact')
        b = crystal('im_babyhex_%d' % k, 0.1, 0.5, M['crys_vio'] if k % 2 else M['crys'], 5, 0.35, 0.8,
                    loc=(cx + 1.2 * math.cos(a + 0.5), 1.2 * math.sin(a + 0.5), -0.03), rot=aim((0.0, 0.0, 1.0)), ol=0.015)
        t1 = t0 + 3
        key(b, IMPACT0, scale=0)
        key(b, t1, scale=0)
        key(b, t1 + 4, scale=1.2)
        key(b, t1 + 7, scale=1.0)
        key(b, IMPACT0 + 38, scale=1.0)
        key(b, IMPACT0 + 44, scale=0)
        tidy(b, 'impact')
    # sparkles
    for i in range(14):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.3, 1.9)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(1.5, 3.5))
        sp = star('im_spark_%d' % i, 0.16, 0.04, 4, 0.02, white if i % 2 else cyan, rot=(90, 0, 0))
        twinkle(sp, f + rnd.randint(0, 14), p0, p1, rnd.uniform(1.0, 1.6))
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.6, 1.8)
        p0 = (cx + 0.2 * math.cos(a), 0.2 * math.sin(a), 0.2)
        p1 = (cx + rr * math.cos(a), rr * math.sin(a), rnd.uniform(2.0, 3.6))
        mo = sphere('im_mote_%d' % i, 0.06, white, 6, 4)
        twinkle(mo, f + rnd.randint(0, 12), p0, p1, 1.2, life=26)
    return True
