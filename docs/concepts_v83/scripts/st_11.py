from gymlib import *
import db_11

NAME = 'ST_11_Magma'
T = 1.3


def build():
    begin(NAME, ol=0.04)
    M = db_11.mats()
    basalt, basalt2, iron, ember, lava, hot = (M[k] for k in ('basalt', 'basalt2', 'iron', 'ember', 'lava', 'hot'))
    s = stats(db_11.NAME)
    half = s['size'][0] / 2
    cx = half + 0.2
    hz = T + 0.1 - s['min'][2]
    top = hz + s['max'][2]
    rnd = random.Random(11)

    # ---- forge altar
    box('plinth', (10.0, 3.0, 0.3), basalt, bev=0.06, loc=(0, 0, 0.15))
    box('altar', (9.4, 2.6, 0.8), basalt2, bev=0.08, loc=(0, 0, 0.7))
    box('deck', (9.8, 2.9, 0.2), iron, bev=0.05, loc=(0, 0, 1.2))
    box('deck_trim', (9.9, 0.08, 0.1), iron, bev=0.02, bsegs=1, loc=(0, -1.46, 1.22), ol=0.025)
    box('deck_glow', (9.0, 0.04, 0.05), lava, bev=0, loc=(0, -1.48, 1.08), ol=0)
    for i, y in enumerate((-1.2, 1.2)):
        # lava channels on the deck top
        box('channel_%d' % i, (8.8, 0.14, 0.03), lava, bev=0, loc=(0, y, T + 0.015), ol=0)
    for i, x in enumerate((-4.3, -3.8, -3.3, 3.3, 3.8, 4.3)):
        box('altar_rune_%d' % i, (0.06, 0.04, 0.5 - 0.12 * (i % 2)), hot, bev=0, loc=(x, -1.31, 0.7), ol=0)
    for i, x in enumerate((-4.6, 4.6)):
        box('altar_band_%d' % i, (0.2, 2.7, 0.85), iron, bev=0.04, bsegs=1, loc=(x, 0, 0.72), ol=0.025)
    # ---- sign
    box('sign_plaque', (5.2, 0.12, 0.76), iron, bev=0.05, loc=(0, -1.3, 0.7))
    box('sign_panel', (4.9, 0.1, 0.64), basalt, bev=0.04, bsegs=1, loc=(0, -1.37, 0.7), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.58, 0.05, lava, loc=(0, -1.42, 0.7), rot=(90, 0, 0))
    for sx in (-1, 1):
        sphere('sign_gem_%s' % ('L' if sx < 0 else 'R'), 0.11, ember, 8, 5, loc=(sx * 2.45, -1.4, 0.7), ol=0.02)

    # ---- cradles: basalt posts with charred iron claws
    topc = hz - 0.15
    for sx in (-1, 1):
        for dx in (-0.42, 0.42):
            x = sx * cx + dx
            n = '%s%s' % ('L' if sx < 0 else 'R', 'a' if dx < 0 else 'b')
            ph = topc - 0.3 - T
            box('post_' + n, (0.3, 0.5, ph), basalt2, bev=0.05, bsegs=1, loc=(x, 0, T + ph / 2))
            box('cap_' + n, (0.34, 0.8, 0.12), iron, bev=0.03, bsegs=1, loc=(x, 0, topc - 0.24), ol=0.025)
            for sy in (-1, 1):
                crystal('prong_%s%d' % (n, sy), 0.07, 0.5, iron, sides=4, tip=0.4, loc=(x, sy * 0.27, topc - 0.2), ol=0.02)

    # ---- basalt columns, forge beam, vents, braziers
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        for j, (y, h) in enumerate(((1.0, 4.6), (-0.95, 3.0))):
            lathe('column_%s%d' % (n, j), [(0.3, 0), (0.3, 0.5), (0.34, 0.5), (h * 0.5 + 0.3, 0.44), (h * 0.5 + 1.5, 0.44), (h + 0.3, 0.5), (h + 0.3, 0)],
                  basalt, 6, 'Z', loc=(sx * 4.8, y, 0), smooth=False)
            lathe('column_ring_%s%d' % (n, j), [(-0.07, 0.46), (-0.05, 0.55), (0.05, 0.55), (0.07, 0.46)], iron, 6, 'Z',
                  loc=(sx * 4.8, y, h * 0.5 + 0.9), caps=False, ol=0.025)
            for z in (1.0 + 0.1 * j, 1.8, 2.6):
                if z < h:
                    box('column_crack_%s%d_%d' % (n, j, int(z * 10)), (0.28, 0.06, 0.04), hot, bev=0, loc=(sx * 4.8, y - 0.39, z), ol=0)
        lathe('brazier_' + n, [(0, 0), (0, 0.16), (0.1, 0.12), (0.26, 0.3), (0.34, 0.34), (0.34, 0.28), (0.26, 0.2), (0.26, 0)],
              iron, 10, 'Z', loc=(sx * 4.3, -1.05, T), ol=0.03)
        sphere('brazier_coals_' + n, 0.26, lava, 8, 4, loc=(sx * 4.3, -1.05, T + 0.32), scale=(1, 1, 0.4), ol=0)
        for k in range(3):
            cone('brazier_spike_%s%d' % (n, k), 0.07, 0.3, iron, 5, loc=(sx * 4.3 + 0.28 * math.cos(2.1 * k), -1.05 + 0.28 * math.sin(2.1 * k), T + 0.3), ol=0.015)
    box('forge_beam', (9.6, 0.4, 0.36), iron, bev=0.06, loc=(0, 1.0, 4.85))
    box('forge_beam_glow', (9.0, 0.04, 0.06), lava, bev=0, loc=(0, 0.78, 4.85), ol=0)
    for j, x in enumerate((-2.5, 0.0, 2.5)):
        cone('beam_vent_%d' % j, 0.35, 0.35, basalt, 8, r2=0.15, loc=(x, 1.0, 5.03))
        sphere('beam_vent_glow_%d' % j, 0.16, lava, 8, 4, loc=(x, 1.0, 5.38), scale=(1, 1, 0.4), ol=0)
    for j, x in enumerate((-3.4, -1.7, -0.9, 0.9, 1.7, 3.4)):
        lathe('beam_drip_%d' % j, [(0, 0), (0, 0.09), (-0.25, 0.06), (-0.45, 0.11), (-0.58, 0)], lava, 6, 'Z', loc=(x, 0.85, 4.67), ol=0)
    for sx in (-1, 1):
        rock('rubble_%s' % ('L' if sx < 0 else 'R'), 0.45, basalt2, seed=3, sub=1, flat=True, loc=(sx * 3.7, 1.15, T + 0.1), scale=(1.3, 1.0, 0.8))

    fx(True)
    fl_o = glow('mag_flame_o', '#ff6a1a', 2.0)
    fl_y = glow('mag_flame_y', '#ffe66b', 2.4)
    fl_r = glow('mag_flame_r', '#ff2a2a', 1.8)
    emb = glow('mag_ember_fx', '#ffb347', 3.0)
    aura = ghost('mag_aura', '#ff6a1a', 1.2, 0.1)
    smoke = ghost('mag_smoke', '#2a2024', 0.6, 0.12)
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        for k in range(3):
            x, y = sx * 4.3 + (k - 1) * 0.12, -1.05 + (k % 2) * 0.1
            h = 0.8 + 0.3 * (k == 1)
            flame('fx_brazier_%s%d' % (n, k), h, 0.17, fl_r if k == 0 else fl_o, bend=0.15, loc=(x, y, T + 0.36), rot=(0, 0, 120 * k))
            flame('fx_brazier_in_%s%d' % (n, k), h * 0.55, 0.09, fl_y, bend=0.12, loc=(x, y - 0.03, T + 0.38), rot=(0, 0, 120 * k))
    for j, x in enumerate((-2.5, 0.0, 2.5)):
        flame('fx_vent_%d' % j, 0.5, 0.15, fl_o, bend=0.12, loc=(x, 1.0, 5.4), rot=(0, 0, 40 * j))
    sphere('fx_smoke_0', 0.6, smoke, 10, 6, loc=(0.2, 1.0, 5.5), scale=(1.1, 1.0, 0.8))
    sphere('fx_aura', 3.2, aura, 16, 9, loc=(0, 0.9, 3.0), scale=(1.5, 0.5, 0.9))
    for i in range(6):
        sx = -1 if i % 2 else 1
        rock('fx_float_rock_%d' % i, rnd.uniform(0.14, 0.24), basalt, seed=i, sub=1, flat=True,
             loc=(sx * rnd.uniform(1.0, 5.0), rnd.uniform(-0.8, 1.2), rnd.uniform(4.0, 4.6) if i % 2 else rnd.uniform(2.9, 3.5)))
    for i in range(20):
        sphere('fx_ember_%d' % i, rnd.uniform(0.04, 0.08), emb, 6, 4,
               loc=(rnd.uniform(-5.0, 5.0), rnd.uniform(-1.4, 1.2), rnd.uniform(2.0, 5.2)))
    fx(False)

    display(NAME, db_11.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
