from spearlib import *

NAME = 'SP_34_aurora_weave'
N = 34
BG = '#2e4a6a'        # polar twilight haze
GROUND = '#2f4a62'    # blue snow
TIP = 9.4
TRAIL = 5.2
FX_EXPORT = {'aurora_ring': 'im_wave_0', 'light_shaft': 'im_curtain_0_0', 'ice_crystal': 'im_ice_0', 'fl_ring': 'fl_ring_0',
             'star': 'im_glint_0'}

BLADE = [(6.75, 0.0), (6.8, 0.2), (7.2, 0.42), (7.9, 0.5), (8.6, 0.36), (9.1, 0.17), (TIP, 0.0)]


def blade_r(z):
    for (z0, r0), (z1, r1) in zip(BLADE, BLADE[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / max(z1 - z0, 1e-6)
    return 0.0


def mats():
    return dict(
        ice=toon('aur_ice', '#9fe0e8', '#4a98b8', '#e0fcff', spec=1.0, rim=0.7, rimcol='#a8ffd8', emit=0.4),
        navy=toon('aur_navy', '#27386e', '#141c44', '#5a6cb0', spec=0.8),
        white=toon('aur_white', '#f2f8ff', '#a8bcd8', '#ffffff', spec=0.6),
        silver=toon('aur_silver', '#d8e4f2', '#8896b4', '#ffffff', spec=1.0),
        cord=toon('aur_cord', '#9ad8c8', '#4a8a88', '#d8fff0', spec=0.2),
        crys=toon('aur_crys', '#bfeeff', '#6ab0d8', '#f0fdff', spec=1.0, emit=0.4),
        green=glow('aur_green', '#5dffb0', 1.8),
        teal=glow('aur_teal', '#3be8ff', 1.8),
        violet=glow('aur_violet', '#b070ff', 1.8),
        hot=glow('aur_hot', '#f2fffc', 1.8),
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
    ice, navy, white, silver, cord, crys, green, teal, violet, hot = (M[k] for k in (
        'ice', 'navy', 'white', 'silver', 'cord', 'crys', 'green', 'teal', 'violet', 'hot'))
    bands = (green, teal, violet)
    # ---- tail: aurora orb in a silver cradle with two tilted rings
    sphere('pommel_orb', 0.22, violet, 10, 6, loc=(0, 0, 0.5), ol=0)
    lathe('pommel_cup', [(0.62, 0.0), (0.7, 0.12), (0.86, 0.27), (1.0, 0.2), (1.05, 0.0)], silver, 12, caps=False)
    torus('pommel_ring_a', 0.34, 0.03, green, 18, 5, loc=(0, 0, 0.5), rot=(55, 0, 0), ol=0)
    torus('pommel_ring_b', 0.34, 0.03, teal, 18, 5, loc=(0, 0, 0.5), rot=(-55, 25, 0), ol=0)
    torus('pommel_collar', 0.19, 0.045, silver, 14, 6, loc=(0, 0, 1.08))
    # ---- shaft: deep navy with frosted wraps and glowing rings
    rod('shaft_lo', 0.155, 0.95, 3.3, navy, r1=0.15)
    rod('shaft_hi', 0.15, 3.28, 6.2, navy, r1=0.145)
    coil('wrap_lo', 0.176, 0.034, 1.3, 1.9, 4, cord, segs=5)
    torus('wrap_lo_cap', 0.18, 0.04, silver, 14, 6, loc=(0, 0, 1.93))
    coil('wrap_hi', 0.175, 0.034, 3.12, 3.7, 4, cord, segs=5, phase=1.0)
    torus('wrap_hi_cap', 0.178, 0.035, silver, 14, 6, loc=(0, 0, 3.1))
    for i, z in enumerate((4.2, 4.5, 4.8)):
        torus('shaft_band_%d' % i, 0.153, 0.026, bands[i], 14, 5, loc=(0, 0, z), ol=0)
    for i in range(4):
        a = i * 1.9
        crystal('frost_stud_%d' % i, 0.05, 0.28, crys, 5, 0.4, 0.7, loc=(0.14 * math.cos(a), 0.14 * math.sin(a), 5.1 + 0.28 * i),
                rot=aim((math.cos(a), math.sin(a), 0.8)), ol=0.012)
    # ---- socket: frosted silver cup with a green seam
    lathe('socket', [(5.95, 0.15), (6.1, 0.27), (6.35, 0.36), (6.6, 0.33), (6.78, 0.0)], silver, 14)
    torus('socket_seam', 0.33, 0.03, green, 18, 5, loc=(0, 0, 6.25), ol=0)
    torus('socket_ring', 0.33, 0.05, navy, 16, 6, loc=(0, 0, 6.62))
    # ---- the weave blade: icy spindle with glowing aurora bands and floating rings
    body = lathe('blade', BLADE, ice, 14)
    body.scale = (1.0, 0.48, 1.0)
    zs = [6.95, 7.35, 7.75, 8.15, 8.55, 8.95]
    for i in range(len(zs) - 1):
        za, zb = zs[i] + 0.04, zs[i + 1] - 0.04
        prof = [(za, blade_r(za) + 0.03), (zb, blade_r(zb) + 0.03)]
        b_ = lathe('band_%d' % i, prof, bands[i % 3], 14, caps=False, ol=0)
        b_.scale = (1.0, 0.5, 1.0)
    for i, (z, R, tilt, col) in enumerate(((7.2, 0.62, 12, green), (7.75, 0.8, -14, teal), (8.3, 0.7, 10, violet), (8.8, 0.52, -10, green), (7.5, 0.95, 0, violet))):
        torus('float_ring_%d' % i, R, 0.035, col, 20, 5, loc=(0, 0, z), rot=(tilt, 8 * i, 0), ol=0)
    for s in (-1, 1):
        nm = 'a' if s < 0 else 'b'
        out = [(s * 0.35, 6.85), (s * 0.7, 7.25), (s * 0.55, 7.7), (s * 0.95, 8.1), (s * 0.7, 8.55), (s * 0.4, 8.35), (s * 0.3, 7.7)]
        if s > 0:
            out = out[::-1]
        blade('curtain_' + nm, out, 0.03, teal if s > 0 else green, ol=0)
    for i in range(3):
        a = math.radians(i * 120 + 40)
        crystal('float_ice_%d' % i, 0.06, 0.4, crys, 5, 0.4, 0.7, both=True, loc=(0.85 * math.cos(a), 0.85 * math.sin(a), 7.8 + 0.4 * i),
                rot=aim((math.cos(a) * 0.3, math.sin(a) * 0.3, 1)), ol=0.012)
        sphere('float_glint_%d' % i, 0.05, hot, 6, 4, loc=(0.85 * math.cos(a), 0.85 * math.sin(a), 7.8 + 0.4 * i + 0.3), ol=0)
    tube('charm_cord', [(0.15, 0.04, 5.9), (0.3, 0.08, 5.6), (0.36, 0.1, 5.3)], 0.02, cord, 5)
    star('charm_star', 0.15, 0.06, 5, 0.06, violet, loc=(0.36, 0.1, 5.15), rot=(90, 0, 0), ol=0)
    marker('Tip', TIP)
    marker('TrailRoot', TRAIL)
    build_fx(M)
    return stats(NAME)


def build_fx(M):
    rnd = random.Random(3434)
    green, teal, violet = M['green'], M['teal'], M['violet']
    cols = (green, teal, violet)
    aura = ghost('aur_aura', '#5dffb0', 1.2, 0.05, 1.8)
    puff = ghost('aur_puff', '#c8fff0', 1.2, 0.7, 1.2)
    glint = glow('aur_glint', '#f4fffc', 3.2)
    cur_g = ghost('aur_cur_g', '#5dffb0', 1.5, 0.35, 1.2)
    cur_v = ghost('aur_cur_v', '#b070ff', 1.5, 0.35, 1.2)
    cur_t = ghost('aur_cur_t', '#3be8ff', 1.5, 0.35, 1.2)
    # ---------------- idle
    fx('idle')
    sphere('idle_aura', 0.8, aura, 14, 8, loc=(0, 0, 8.0), scale=(1.5, 1.2, 1.7))
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.2)
        sphere('idle_mote_%d' % i, rnd.uniform(0.04, 0.07), cols[i % 3], 6, 4, loc=(r * math.cos(a), r * math.sin(a), rnd.uniform(6.9, 9.3)))
    for i in range(3):
        star('idle_glint_%d' % i, 0.15, 0.03, 4, 0.02, glint, loc=(rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.1), -0.3, 7.5 + i * 0.6), rot=(90, 0, 0))
    # ---------------- flight: coloured rings, ice crystals, glints, aurora puffs
    fx('flight')
    rings = [torus('fl_ring_%d' % i, 0.55, 0.05, cols[i % 3], 28, 5) for i in range(6)]
    stream(rings, lambda t, i: (0, 0, 9.3 - 7.5 * t), smax=lambda t, i: (0.5 + 1.8 * t) * math.sin(math.pi * t) ** 0.4,
           spin=lambda t, i: (8 * math.sin(6.28 * t + i), 8 * math.cos(6.28 * t + i), 0))
    cr = [crystal('fl_ice_%d' % i, 0.07, 0.38, M['crys'], 5, 0.4, 0.6, both=True, ol=0.012) for i in range(8)]
    cj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(cr, lambda t, i: (cj[i][0] * (0.3 + 1.0 * t), cj[i][1] * (0.3 + 1.0 * t), 8.6 - 12.5 * t),
           smax=1.0, spin=lambda t, i: (cj[i][2] + 540 * t, 360 * t, 0))
    st = [star('fl_glint_%d' % i, 0.16, 0.04, 4, 0.03, glint) for i in range(8)]
    sj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 360)) for _ in range(8)]
    stream(st, lambda t, i: (sj[i][0] * (0.3 + 1.2 * t), sj[i][1] * (0.3 + 1.2 * t), 8.4 - 12.0 * t), smax=1.3,
           spin=lambda t, i: (90, sj[i][2] + 300 * t, 0))
    pf = [sphere('fl_puff_%d' % i, 0.3, (cur_g, cur_t, cur_v)[i % 3], 12, 7) for i in range(6)]
    pj = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(6)]
    stream(pf, lambda t, i: (pj[i][0] * (0.2 + 0.8 * t), pj[i][1] * (0.2 + 0.8 * t), 7.4 - 11.0 * t),
           smax=lambda t, i: (0.6 + 1.6 * t) * math.sin(math.pi * t) ** 0.5)
    # ---------------- impact: stacked coloured rings rise in rippling waves, ice crystals sparkle
    fx('impact')
    piv, d = impact_spear(TIP, depth=0.65)
    f = IMPACT0 + 4
    cx = 0.45
    flash = sphere('im_flash', 0.5, ghost('aur_flash', '#e8fffa', 2.0, 0.6, 1.3), 14, 8, loc=(cx, 0, 0.25))
    key(flash, IMPACT0, scale=0, alpha=1)
    key(flash, f, scale=0.3, alpha=1)
    key(flash, f + 4, scale=2.0, alpha=0.7)
    key(flash, f + 10, scale=2.8, alpha=0)
    tidy(flash, 'impact', interp='LINEAR')
    gd = sphere('im_disc', 1.2, ghost('aur_disc', '#7affd0', 1.4, 0.4, 1.0), 16, 4, loc=(cx, 0, 0.03))
    key(gd, IMPACT0, scale=0, alpha=1)
    key(gd, f + 4, scale=(1.3, 1.3, 0.02), alpha=1)
    key(gd, IMPACT0 + 36, scale=(2.0, 2.0, 0.02), alpha=0.8)
    key(gd, IMPACT0 + 44, scale=(2.0, 2.0, 0.02), alpha=0)
    tidy(gd, 'impact')
    for k in range(9):
        w = torus('im_wave_%d' % k, 0.9, 0.05, cols[k % 3], 28, 5, loc=(cx, 0, 0.1))
        t0 = f + 3 * k // 2
        z_end = 0.4 + 0.3 * k
        key(w, IMPACT0, scale=0, alpha=1, rot=(0, 0, 0))
        key(w, t0, loc=(cx, 0, 0.1), scale=0.4, alpha=1, rot=(0, 0, 0))
        key(w, t0 + 6, loc=(cx, 0, 0.1 + z_end * 0.5), scale=1.0, alpha=1, rot=(8, 0, 0))
        key(w, t0 + 12, loc=(cx, 0, 0.1 + z_end * 0.8), scale=1.2, alpha=1, rot=(-8, 6, 0))
        key(w, t0 + 18, loc=(cx, 0, 0.1 + z_end), scale=1.4, alpha=0.9, rot=(6, -6, 0))
        key(w, t0 + 28, loc=(cx, 0, 0.3 + z_end * 1.1), scale=1.6, alpha=0.0, rot=(0, 0, 0))
        tidy(w, 'impact')
        ease_keys(w)
    # (lead fix) no translucent curtain sheets: rings of glowing light shafts (volumetric) instead
    for k, cm in enumerate((M['green'], M['teal'], M['violet'])):
        R = 0.85 + 0.2 * k
        for j in range(8):
            a = math.radians(j * 45 + k * 15)
            cu = tube('im_curtain_%d_%d' % (k, j), [(0, 0, 0), (0.05, 0, 1.2), (0, 0, 2.4)], [0.05, 0.035, 0.0], cm, 6,
                      loc=(cx + R * math.cos(a), R * math.sin(a), 0.0), ol=0)
            t0 = f + 2 + 3 * k + (j % 2)
            key(cu, IMPACT0, scale=0, alpha=1)
            key(cu, t0, scale=(1.0, 1.0, 0.1), alpha=1)
            key(cu, t0 + 8, scale=(1.0, 1.0, 1.0), alpha=1)
            key(cu, t0 + 18, scale=(1.1, 1.1, 1.2), alpha=0.8)
            key(cu, t0 + 28, scale=(1.2, 1.2, 1.3), alpha=0.0)
            tidy(cu, 'impact')
            ease_keys(cu)
    for i in range(14):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 2.0)
        x, y = cx + r * math.cos(a), r * math.sin(a)
        if x < cx + 0.1 and abs(y) < 0.4:
            x, y = cx + abs(r * math.cos(a)) + 0.2, r * math.sin(a)
        ic = crystal('im_ice_%d' % i, 0.07, rnd.uniform(0.4, 0.8), M['crys'], 5, 0.4, 0.7, loc=(x, y, 0.0),
                     rot=aim((math.cos(a) * 0.2, math.sin(a) * 0.2, 1)), ol=0.012)
        t0 = f + 4 + int(r * 4) + (i % 3)
        key(ic, IMPACT0, scale=0)
        key(ic, t0, scale=0)
        key(ic, t0 + 3, scale=(1.0, 1.0, 1.2))
        key(ic, t0 + 6, scale=1.0)
        key(ic, IMPACT0 + 34, scale=1.0)
        key(ic, IMPACT0 + 44, scale=0)
        tidy(ic, 'impact')
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.5, 2.0)
        g_ = star('im_glint_%d' % i, 0.2, 0.04, 4, 0.03, glint, loc=(cx + r * math.cos(a), r * math.sin(a), rnd.uniform(0.6, 2.2)), rot=(90, 0, 0))
        t0 = f + 6 + rnd.randint(0, 16)
        key(g_, IMPACT0, scale=0)
        key(g_, t0, scale=0)
        key(g_, t0 + 4, scale=1.3)
        key(g_, t0 + 12, scale=0)
        tidy(g_, 'impact')
    for i in range(8):
        a = math.radians(rnd.uniform(0, 360))
        sp_ = rnd.uniform(0.05, 0.13)
        v = Vector((sp_ * math.cos(a), sp_ * math.sin(a), rnd.uniform(0.28, 0.42)))
        sh = crystal('im_shard_%d' % i, 0.06, rnd.uniform(0.25, 0.4), M['crys'], 5, 0.4, 0.6, both=True, ol=0.012)
        toss(sh, Vector((cx, 0, 0.2)), v, f + rnd.randint(0, 4), floor=0.12, spin=(40, 25, 10), hold=38)
    for i in range(4):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.6, 1.6)
        sm = sphere('im_puff_%d' % i, 0.35, puff, 12, 7)
        t0 = f + 3 + rnd.randint(0, 6)
        p0 = (cx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.3)
        p1 = (cx + r * math.cos(a), r * math.sin(a), rnd.uniform(1.4, 2.4))
        key(sm, IMPACT0, loc=p0, scale=0, alpha=1)
        key(sm, t0, loc=p0, scale=0.4, alpha=1)
        key(sm, IMPACT0 + 44, loc=p1, scale=rnd.uniform(1.6, 2.2), alpha=0)
        tidy(sm, 'impact')
        ease_keys(sm)
    return True
