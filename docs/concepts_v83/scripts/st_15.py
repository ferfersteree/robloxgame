from gymlib import *
import db_15

DROP = 1.4
SHELF = (1.5,)   # single deck - the stand holds only the current pair


def build():
    begin('ST_15_Primal', ol=0.045)
    M = db_15.mats()
    stone, crim, gold, bone, leather, lava, eye, ruby = (M[k] for k in ('stone', 'crim', 'gold', 'bone', 'leather', 'lava', 'eye', 'ruby'))
    obs = toon('obsidian_red', '#2c1219', shade='#12060c', light='#5a202b', spec=1.0)
    rnd = random.Random(15)

    # altar base (= shelf 1)
    box('base', (10.3, 3.0, 0.35), stone, bev=0.08, loc=(0, 0, 0.175 + DROP))
    box('base_trim', (10.4, 0.1, 0.1), gold, bev=0.03, loc=(0, -1.5, 0.3 + DROP))
    box('base_lava', (9.2, 0.05, 0.07), lava, bev=0, loc=(0, -1.51, 0.13 + DROP), ol=0)
    # totem posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            n = ('L' if sx < 0 else 'R') + ('F' if sy < 0 else 'B')
            x, y = sx * 4.78, sy * 1.12
            box('totem_lo_' + n, (0.66, 0.66, 0.9), crim, bev=0.08, loc=(x, y, 0.8 + DROP))
            box('totem_band_' + n, (0.74, 0.74, 0.12), gold, bev=0.04, loc=(x, y, 0.42 + DROP))
            if sy < 0:
                for j, zc in enumerate((0.82 + DROP,)):
                    for e in (-1, 1):
                        sphere('totem_eye_%s%d%s' % (n, j, 'a' if e < 0 else 'b'), 0.09, eye, 8, 4, loc=(x + e * 0.15, y - 0.33, zc + 0.12), scale=(1, 0.5, 0.7))
                    box('totem_brow_%s%d' % (n, j), (0.56, 0.12, 0.1), gold, bev=0.03, bsegs=1, loc=(x, y - 0.33, zc + 0.3), ol=0.02)
                    box('totem_mouth_%s%d' % (n, j), (0.42, 0.1, 0.14), obs, bev=0.03, bsegs=1, loc=(x, y - 0.33, zc - 0.2), ol=0.02)
                    for e in (-1, 1):
                        cone('totem_fang_%s%d%s' % (n, j, 'a' if e < 0 else 'b'), 0.05, 0.17, bone, 5, loc=(x + e * 0.12, y - 0.38, zc - 0.14), rot=(180, 0, 0), ol=0.012)
                    cone('totem_ear_%s%d' % (n, j), 0.12, 0.34, gold, 5, loc=(x + sx * 0.3, y, zc + 0.15), rot=aim((sx, 0, 0.5)), ol=0.02)
    # shelf 2 + top deck
    for i, (z, th) in enumerate(((2.9, 0.26),)):
        box('slab_%d' % i, (10.3, 2.85, th), obs, bev=0.06, loc=(0, 0, z - th / 2))
        box('slab_trim_%d' % i, (10.4, 0.1, th + 0.04), gold, bev=0.03, loc=(0, -1.44, z - th / 2))
        box('slab_lava_%d' % i, (9.0, 0.04, 0.05), lava, bev=0, loc=(0, -1.4, z - th - 0.05), ol=0)
    # altar block under the deck
    box('altar', (9.0, 2.4, 0.92), stone, bev=0.1, loc=(0, 0, 0.8 + DROP))
    for i, z in enumerate((0.5, 1.12)):
        box('altar_band_%d' % i, (9.1, 2.5, 0.1), gold, bev=0.03, loc=(0, 0, z + DROP), ol=0.025)
    for i, x in enumerate((-4.0, -3.5, -3.0, 3.0, 3.5, 4.0)):
        box('altar_rune_%d' % i, (0.1, 0.05, 0.42 - 0.1 * (i % 2)), lava, bev=0, loc=(x, -1.21, 0.8 + DROP), ol=0)
    for i in range(7):
        x = -3.6 + 1.2 * i
        cone('altar_tooth_%d' % i, 0.1, 0.3, bone, 5, loc=(x, 1.3, 0.35 + DROP), ol=0.02)
    # sign plaque on the deck front
    box('sign_plaque', (5.7, 0.16, 0.8), gold, bev=0.06, loc=(0, -1.28, 0.82 + DROP))
    box('sign_panel', (5.3, 0.1, 0.62), obs, bev=0.04, loc=(0, -1.35, 0.82 + DROP), ol=0.02)
    text('sign_text', 'CAMP GYM', 0.5, 0.05, lava, loc=(0, -1.42, 0.82 + DROP), rot=(90, 0, 0))
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        cone('sign_fang_' + n, 0.16, 0.6, bone, 7, loc=(sx * 3.05, -1.32, 0.35 + DROP), rot=(0, sx * 10, 0), ol=0.03)
        sphere('sign_ruby_' + n, 0.11, ruby, 8, 5, loc=(sx * 2.72, -1.38, 0.82 + DROP), ol=0.02)
    crystal('sign_crest', 0.2, 0.42, ruby, sides=4, tip=0.5, both=True, loc=(0, -1.32, 1.32 + DROP), ol=0.025)
    # giant horns sweeping out from the back
    tips = {}
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        pts = [(sx * 2.7, 1.15, 2.85), (sx * 3.7, 1.15, 3.5), (sx * 4.75, 1.15, 4.45), (sx * 5.4, 1.15, 5.3), (sx * 5.35, 1.15, 6.15)]
        tube('giant_horn_' + n, pts, [0.52, 0.48, 0.38, 0.24, 0.0], bone, segs=10)
        for i, t in enumerate((1, 2, 3)):
            tan = (Vector(pts[t + 1]) - Vector(pts[t - 1])).normalized()
            torus('giant_horn_ring_%s%d' % (n, i), (0.5, 0.4, 0.26)[i], 0.07, gold, 12, 5, 'Z', loc=pts[t], rot=aim(tan), ol=0.025)
        lathe('horn_socket_' + n, [(2.9, 0.52), (3.0, 0.55), (3.12, 0.5), (3.16, 0.46)], gold, 12, 'Z', loc=(sx * 2.75, 1.15, 0), caps=False, ol=0.03)
        tips[sx] = pts[-1]
        # fire bowls on the deck front corners
        lathe('bowl_' + n, [(2.9, 0), (2.9, 0.18), (3.0, 0.12), (3.1, 0.3), (3.22, 0.38), (3.26, 0.33), (3.16, 0.2), (3.16, 0)], gold, 10, 'Z', loc=(sx * 4.75, -1.05, 0), ol=0.03)
        sphere('bowl_coals_' + n, 0.24, lava, 8, 4, loc=(sx * 4.75, -1.05, 3.2), scale=(1, 1, 0.4))
        # levitation pedestals under the pair
        box('pedestal_' + n, (1.5, 1.5, 0.28), stone, bev=0.07, loc=(sx * 2.75, 0, 3.04))
        box('pedestal_trim_' + n, (1.6, 1.6, 0.1), gold, bev=0.03, loc=(sx * 2.75, 0, 3.0), ol=0.025)
        lathe('pedestal_rune_' + n, [(3.18, 0), (3.2, 0.5), (3.21, 0.38), (3.21, 0.3), (3.2, 0.0)], lava, 12, 'Z', loc=(sx * 2.75, 0, 0), ol=0)
        for k in range(4):
            a = math.radians(45 + 90 * k)
            cone('pedestal_spike_%s%d' % (n, k), 0.09, 0.3, bone, 5, loc=(sx * 2.75 + 0.66 * math.cos(a), 0.66 * math.sin(a), 3.16), ol=0.015)
    # nimbus ring behind the pair
    torus('nimbus', 1.85, 0.11, gold, 32, 6, 'Y', loc=(0, 1.3, 4.55))
    torus('nimbus_inner', 1.55, 0.035, lava, 32, 4, 'Y', loc=(0, 1.3, 4.55), ol=0)
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        crystal('nimbus_gem_%d' % k, 0.14, 0.34, lava if k % 2 else ruby, sides=4, tip=0.5, both=True,
                loc=(1.85 * math.cos(a), 1.2, 4.55 + 1.85 * math.sin(a)), rot=aim((math.cos(a), 0, math.sin(a))), ol=0 if k % 2 else 0.02)

    fx(True)
    fl_o = glow('flame_orange', '#ff6a1a', 2.0)
    fl_y = glow('flame_yellow', '#ffe66b', 2.4)
    fl_r = glow('flame_red', '#ff2a2a', 1.8)
    bolt_m = glow('bolt', '#fff7b0', 3.2)
    for sx in (-1, 1):
        n = 'L' if sx < 0 else 'R'
        for k in range(3):
            x, y = sx * 4.75 + (k - 1) * 0.14, -1.05 + (k % 2) * 0.1
            h = 0.8 + 0.3 * (k == 1)
            flame('fx_bowl_flame_%s%d' % (n, k), h, 0.17, fl_r if k == 0 else fl_o, bend=0.15, loc=(x, y, 3.22), rot=(0, 0, 120 * k))
            flame('fx_bowl_flame_in_%s%d' % (n, k), h * 0.55, 0.09, fl_y, bend=0.12, loc=(x, y - 0.03, 3.24), rot=(0, 0, 120 * k))
        bolt('fx_bolt_horn_' + n, tips[sx], (sx * 3.9, 1.3, 6.6), bolt_m, r=0.05, n=8, amp=0.3, seed=30 + sx)
        bolt('fx_bolt_ring_' + n, (sx * 1.85, 1.3, 4.55), (sx * 4.6, 1.2, 4.4), bolt_m, r=0.045, n=6, amp=0.22, seed=40 + sx)
        flame('fx_horn_flame_' + n, 0.9, 0.2, fl_o, bend=0.12, loc=(tips[sx][0], 1.15, 5.95), rot=(0, 0, 90))
    sphere('fx_aura_red', 3.2, ghost('aura_red', '#ff3a1a', 1.2, 0.12), 18, 10, loc=(0, 0.9, 4.6), scale=(1.5, 0.5, 0.85))
    sphere('fx_aura_gold', 2.2, ghost('aura_gold', '#ffc23a', 1.2, 0.07), 18, 10, loc=(0, 1.0, 4.75), scale=(1.2, 0.5, 1.0))
    for k in range(6):
        a = math.radians(60 * k + 15)
        crystal('fx_rune_stone_%d' % k, 0.14, 0.36, glow('lava', '#ff7a1a', 2.6), sides=4, tip=0.5, both=True,
                loc=(2.4 * math.cos(a), 1.35, 4.55 + 2.4 * math.sin(a)), rot=(rnd.uniform(-20, 20), rnd.uniform(-20, 20), 0))
    emb = glow('ember', '#ffb347', 3.0)
    for i in range(22):
        sphere('fx_ember_%d' % i, rnd.uniform(0.04, 0.08), emb, 6, 4,
               loc=(rnd.uniform(-5.4, 5.4), rnd.uniform(-1.4, 1.2), rnd.uniform(3.2, 7.0)))
    spk = glow('spark_white', '#ffffff', 2.5)
    for i in range(8):
        star('fx_sparkle_%d' % i, rnd.uniform(0.12, 0.22), 0.04, 4, 0.02, spk,
             loc=(rnd.uniform(-5.2, 5.2), -rnd.uniform(1.2, 1.6), rnd.uniform(1.9, 6.4)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)

    drop(DROP)
    display('ST_15_Primal', 'DB_15_Primal', [((-2.75, 0, 4.45 - DROP), (0, 0, 0)), ((2.75, 0, 4.45 - DROP), (0, 0, 0))],
            [], SHELF,
            pair_fx=lambda o: any(k in o.name for k in ('flame', 'ember', 'halo', 'bolt_horns')))
    return stats('ST_15_Primal')
