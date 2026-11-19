from gymlib import *
import db_02

NAME = 'ST_02_Stone'
T = 1.3


def build():
    begin(NAME, ol=0.04)
    M = db_02.mats()
    stone, dark, moss = M['stone'], M['dark'], M['moss']
    rope, crack, sand, lichen = M['rope'], M['crack'], M['sand'], M['lichen']
    s = stats(db_02.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    zs = top + 0.8            # sign centre height
    lint = zs + 0.95          # lintel height

    # ---- ground pad + slab table on stub stones
    box('ground_slab', (10.0, 3.0, 0.3), dark, bev=0.12, loc=(0, 0, 0.15))
    box('table_slab', (9.2, 2.7, 0.45), stone, bev=0.12, loc=(0, 0, T - 0.225))
    for i, (x, y) in enumerate(((-3.9, -0.8), (0, -0.8), (3.9, -0.8), (-3.9, 0.8), (0, 0.8), (3.9, 0.8))):
        rock('stub_%d' % i, 0.55, dark, seed=60 + i, sub=1, rough=0.12, loc=(x, y, 0.6), scale=(1.0, 1.0, 0.62))

    # ---- cradles: rough stone posts with seat and two prongs
    zt = hz - 0.2
    for ci, sx in enumerate((-cx, cx)):
        for fi, dx in enumerate((-0.42, 0.42)):
            x = sx + dx
            nm = '%d%d' % (ci, fi)
            lathe('cradle_post_' + nm, [(T, 0), (T, 0.26), (T + 0.12, 0.24), (T + 0.3, 0.17), (zt - 0.1, 0.16), (zt, 0.2), (zt, 0)],
                  dark, 7, 'Z', loc=(x, 0, 0), sharp=20)
            box('cradle_seat_' + nm, (0.34, 0.5, 0.12), stone, bev=0.04, bsegs=1, loc=(x, 0, zt + 0.04))
            for sy in (-1, 1):
                box('cradle_prong_%s%s' % (nm, 'a' if sy < 0 else 'b'), (0.2, 0.1, 0.3), stone, bev=0.03, bsegs=1,
                    loc=(x, sy * 0.24, zt + 0.2), rot=(sy * 8, 0, 0))

    # ---- dolmen: two uprights + lintel, plaque hanging by ropes
    h = lint + 0.15 - T
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        rock('upright_' + n, 1.0, stone, seed=5 + sx, sub=2, rough=0.08, loc=(sx * 4.4, 1.05, T + 0.46 * h - 0.1),
             scale=(0.5, 0.42, 0.46 * h))
        torus('rune_ring_' + n, 0.22, 0.03, crack, 10, 4, 'Y', loc=(sx * 4.4, 0.6, T + 1.4), ol=0.015)
        cyl('rune_dot_' + n, 0.06, 0.05, crack, segs=6, bev=0.01, axis='Y', loc=(sx * 4.4, 0.6, T + 1.4), ol=0.01)
    box('lintel', (10.0, 1.3, 0.45), stone, bev=0.12, loc=(0, 1.05, lint))
    for i, x in enumerate((-3.6, -0.5, 3.0)):
        rock('lintel_moss_%d' % i, 0.45 - 0.05 * (i == 1), moss, seed=70 + i, sub=1, rough=0.1, ol=0.02,
             loc=(x, 1.05, lint + 0.22), scale=(1.0, 0.9, 0.25))
    for sx in (-1, 1):
        x = sx * 3.4
        tube('vine_%d' % sx, [(x, 0.7, lint - 0.22), (x + 0.05, 0.7, lint - 0.5), (x - 0.05, 0.7, lint - 0.8), (x, 0.7, lint - 1.1)],
             [0.03, 0.035, 0.03, 0.0], moss, segs=4, ol=0.015)
        tube('sign_rope_%d' % sx, [(sx * 2.3, 1.25, lint - 0.2), (sx * 2.3, 1.25, zs + 0.5)], 0.04, rope, segs=5, ol=0.015)
    # sign slab
    box('sign_slab', (5.2, 0.22, 1.0), dark, bev=0.1, loc=(0, 1.25, zs))
    for i, x in enumerate((-1.3, 1.5)):
        rock('sign_moss_%d' % i, 0.4, moss, seed=80 + i, sub=1, rough=0.1, ol=0.02, loc=(x, 1.25, zs + 0.52), scale=(1.0, 0.45, 0.3))
    for i, (x, z, a) in enumerate(((-2.2, zs - 0.3, 35), (2.15, zs + 0.28, -30))):
        box('sign_crack_%d' % i, (0.6, 0.03, 0.045), crack, bev=0, loc=(x, 1.13, z), rot=(0, a, 0), ol=0)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, sand, loc=(0, 1.04, zs), rot=(90, 0, 0))

    # ---- cairns at both table ends
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        for k, (r, z, dx) in enumerate(((0.42, 0.3, 0.0), (0.3, 0.78, 0.05), (0.2, 1.13, -0.03))):
            rock('cairn_%s%d' % (n, k), r, stone if k != 1 else dark, seed=90 + k + sx, sub=1, rough=0.15,
                 loc=(sx * 4.1 + dx, -0.2, T + z), scale=(1.0, 1.0, 0.85))
        rock('cairn_moss_' + n, 0.2, moss, seed=95, sub=1, rough=0.1, ol=0.02, loc=(sx * 4.1, -0.2, T + 1.28), scale=(1, 1, 0.4))
    # corner boulders on the ground pad
    for i, (x, y) in enumerate(((-4.7, -1.1), (4.7, -1.1), (-4.7, 1.1), (4.7, 1.1))):
        rock('corner_rock_%d' % i, 0.36, dark if i % 2 else stone, seed=100 + i, sub=1, rough=0.15, loc=(x, y, 0.5), scale=(1, 1, 0.85))
    for i, (x, y) in enumerate(((-4.7, -1.1), (4.7, 1.1))):
        rock('corner_moss_%d' % i, 0.25, moss, seed=110 + i, sub=1, rough=0.1, ol=0.02, loc=(x, y, 0.84), scale=(1, 1, 0.3))
    # pebbles at the front edge, moss + lichen on the table
    for i in range(5):
        rock('pebble_%d' % i, 0.1, dark if i % 2 else stone, seed=120 + i, sub=1, rough=0.15,
             loc=(-3.6 + 1.8 * i, -1.15, T + 0.06), scale=(1, 1, 0.8), ol=0.02)
    for i, (x, y, r) in enumerate(((-3.2, -0.55, 0.3), (0.0, -0.5, 0.26), (3.0, 0.5, 0.28), (-0.2, 0.7, 0.24))):
        rock('deck_moss_%d' % i, r, moss, seed=130 + i, sub=1, rough=0.1, ol=0.02, loc=(x, y, T + 0.01), scale=(1, 1, 0.22))
    for i, (x, y) in enumerate(((-3.7, 0.3), (3.6, -0.5), (0.2, 0.2))):
        rock('deck_lichen_%d' % i, 0.17, lichen, seed=140 + i, sub=1, rough=0.1, ol=0.015, loc=(x, y, T + 0.01), scale=(1, 1, 0.2))

    # ---- effects: nearly none
    fx(True)
    dust = ghost('stone_dust', '#f1e6cc', 1.0, 0.12)
    for i, (p, r) in enumerate((((-3.6, -1.0, 0.55), 0.35), ((3.7, -1.0, 0.55), 0.3), ((0.0, -1.0, 0.5), 0.25))):
        sphere('fx_dust_%d' % i, r, dust, 10, 6, loc=p, scale=(1.5, 1.0, 0.6))
    for i, p in enumerate(((-4.2, -0.9, 2.3), (4.3, -0.8, 2.6))):
        rock('fx_pebble_%d' % i, 0.06, dark, seed=150 + i, sub=1, loc=p, ol=0.012)
    fx(False)

    display(NAME, db_02.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
