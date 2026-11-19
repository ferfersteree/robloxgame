from gymlib import *
import db_04

NAME = 'ST_04_Iron'
T = 1.4


def build():
    begin(NAME, ol=0.04)
    M = db_04.mats()
    iron, steel, dark, rivet = M['iron'], M['steel'], M['dark'], M['rivet']
    enamel, cold, hot = M['enamel'], M['cold'], M['hot']
    s = stats(db_04.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    zs = top + 0.8                       # sign centre height
    zb = min(zs + 0.9, 5.15)             # top beam height
    rnd = random.Random(4)

    # ---- base, legs, deck, apron
    box('base', (10.0, 3.0, 0.3), dark, bev=0.08, loc=(0, 0, 0.15))
    for i in range(10):
        sphere('base_rivet_%d' % i, 0.07, rivet, 6, 3, loc=(-4.5 + i, -1.5, 0.15), ol=0.012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('leg_%d%d' % (sx, sy), (0.5, 0.5, T - 0.6), iron, bev=0.05, bsegs=1, loc=(sx * 4.2, sy * 1.0, 0.3 + (T - 0.6) / 2))
    box('deck', (9.6, 2.7, 0.3), iron, bev=0.06, loc=(0, 0, T - 0.15))
    box('apron', (9.2, 0.12, 0.4), steel, bev=0.03, bsegs=1, loc=(0, -1.38, T - 0.5))
    for i in range(12):
        sphere('apron_rivet_%d' % i, 0.05, rivet, 6, 3, loc=(-4.4 + 0.8 * i, -1.45, T - 0.5), ol=0.012)
    box('forge_glow', (7.0, 0.04, 0.06), hot, bev=0, loc=(0, -1.37, T - 0.15), ol=0)

    # ---- cradles: iron posts with seat, prongs and a rivet
    zt = hz - 0.2
    for ci, sx in enumerate((-cx, cx)):
        for fi, dx in enumerate((-0.42, 0.42)):
            x = sx + dx
            nm = '%d%d' % (ci, fi)
            lathe('cradle_post_' + nm, [(T, 0), (T, 0.28), (T + 0.1, 0.28), (T + 0.2, 0.18), (zt - 0.12, 0.15), (zt - 0.04, 0.22), (zt, 0.22), (zt, 0)],
                  iron, 8, 'Z', loc=(x, 0, 0), sharp=20)
            box('cradle_seat_' + nm, (0.34, 0.5, 0.1), steel, bev=0.03, bsegs=1, loc=(x, 0, zt + 0.05))
            for sy in (-1, 1):
                box('cradle_prong_%s%s' % (nm, 'a' if sy < 0 else 'b'), (0.2, 0.09, 0.3), steel, bev=0.03, bsegs=1,
                    loc=(x, sy * 0.24, zt + 0.2), rot=(sy * 8, 0, 0))
            sphere('cradle_rivet_' + nm, 0.05, rivet, 6, 3, loc=(x, -0.2, T + 0.3), ol=0.012)

    # ---- back frame: posts, beam, chains, sign plate
    ph = zb + 0.18 - 0.3
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        box('post_' + n, (0.4, 0.4, ph), iron, bev=0.05, bsegs=1, loc=(sx * 4.5, 1.15, 0.3 + ph / 2))
        box('post_cap_' + n, (0.5, 0.5, 0.15), steel, bev=0.04, bsegs=1, loc=(sx * 4.5, 1.15, zb + 0.25))
        for i, z in enumerate((T + 0.4, T + 1.3)):
            sphere('post_rivet_%s%d' % (n, i), 0.06, rivet, 6, 3, loc=(sx * 4.5, 0.94, z), ol=0.012)
    box('beam', (9.9, 0.4, 0.35), iron, bev=0.06, loc=(0, 1.15, zb))
    for i in range(6):
        sphere('beam_rivet_%d' % i, 0.06, rivet, 6, 3, loc=(-3.0 + 1.2 * i, 0.94, zb), ol=0.012)
    for sx in (-1, 1):
        for k in range(6):
            torus('chain_%d_%d' % (sx, k), 0.1, 0.025, steel, 8, 4, 'X' if k % 2 == 0 else 'Y',
                  loc=(sx * 3.9, 1.0, zb - 0.3 - 0.27 * k), ol=0.012)
    box('sign_plate', (4.9, 0.2, 1.0), iron, bev=0.06, loc=(0, 1.25, zs))
    for sz in (-1, 1):
        box('sign_trim_%d' % sz, (5.05, 0.26, 0.1), steel, bev=0.03, bsegs=1, loc=(0, 1.25, zs + sz * 0.55))
    for sx in (-1, 1):
        box('sign_rod_%d' % sx, (0.16, 0.16, 0.3), steel, bev=0.03, bsegs=1, loc=(sx * 2.0, 1.25, zs + 0.65))
        for sz in (-1, 1):
            cyl('sign_bolt_%d%d' % (sx, sz), 0.07, 0.08, rivet, segs=6, bev=0.015, axis='Y', loc=(sx * 2.3, 1.13, zs + sz * 0.36), ol=0.012)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, hot, loc=(0, 1.05, zs), rot=(90, 0, 0))

    # ---- anvil (left) and forge pot (right) on the deck
    ax = -4.15
    box('anvil_base', (0.9, 0.6, 0.22), dark, bev=0.04, bsegs=1, loc=(ax, 0, T + 0.11))
    box('anvil_waist', (0.5, 0.4, 0.3), iron, bev=0.04, bsegs=1, loc=(ax, 0, T + 0.37))
    box('anvil_top', (0.6, 0.9, 0.26), steel, bev=0.04, bsegs=1, loc=(ax, 0, T + 0.65))
    cone('anvil_horn', 0.28, 0.4, steel, 8, r2=0.06, loc=(ax, 0.45, T + 0.65), rot=aim((0, 1, 0)))
    box('anvil_hot_bar', (0.4, 0.12, 0.07), hot, bev=0, loc=(ax, -0.1, T + 0.82), ol=0)
    fx_ = 4.15
    cyl('forge_pedestal', 0.45, 0.35, iron, segs=8, bev=0.05, axis='Z', loc=(fx_, 0, T + 0.175), sharp=20)
    zq = T + 0.35
    lathe('forge_bowl', [(zq, 0), (zq, 0.4), (zq + 0.15, 0.55), (zq + 0.4, 0.62), (zq + 0.45, 0.62), (zq + 0.43, 0.5), (zq + 0.27, 0)],
          steel, 10, 'Z', loc=(fx_, 0, 0), sharp=20)
    sphere('forge_coals', 0.45, hot, 10, 6, loc=(fx_, 0, zq + 0.35), scale=(1, 1, 0.3))
    torus('forge_rim', 0.62, 0.04, rivet, 10, 4, 'Z', loc=(fx_, 0, zq + 0.45), ol=0.015)

    # ---- effects: sparks around the forge + faint cold sheen
    fx(True)
    sp1 = glow('iron_spark', '#ffa63a', 2.8)
    sp2 = glow('iron_spark2', '#ffe27a', 2.8)
    for i in range(6):
        p = (4.1 + rnd.uniform(-0.6, 0.6), rnd.uniform(-0.5, 0.4), T + rnd.uniform(1.2, 2.1))
        star('fx_spark_%d' % i, rnd.uniform(0.09, 0.15), 0.03, 4, 0.02, sp1 if i % 2 == 0 else sp2, loc=p, rot=(90, 0, rnd.uniform(0, 45)))
    for i in range(3):
        a = (4.1 + rnd.uniform(-0.5, 0.5), rnd.uniform(-0.4, 0.3), T + rnd.uniform(1.0, 1.8))
        b = (a[0] + rnd.uniform(0.1, 0.25), a[1], a[2] + rnd.uniform(0.12, 0.25))
        tube('fx_streak_%d' % i, [a, b], [0.025, 0.0], sp2, segs=4)
    sphere('fx_sheen', 1.5, ghost('iron_sheen', '#8fc4ff', 0.9, 0.1), 14, 8, loc=(4.15, 0.0, T + 1.0), scale=(0.7, 0.7, 0.8))
    fx(False)

    display(NAME, db_04.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
