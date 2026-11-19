from gymlib import *


def mats():
    return dict(
        stone=toon('primal_stone', '#6b2028', shade='#2e0f1c', light='#9a2f33', spec=0.3),
        crim=toon('primal_crimson', '#d32b30', shade='#7a1230', light='#ff6a4a', spec=0.8),
        gold=toon('gold', '#ffcf4d', shade='#c2742a', light='#fff2a6', spec=1.0),
        bone=toon('bone', '#f6e8c8', shade='#b08f78', light='#ffffff', spec=0.5),
        leather=toon('primal_leather', '#3b1a1e', shade='#1c0c14', light='#5c2a2a', spec=0.2),
        lava=glow('lava', '#ff7a1a', 2.6),
        eye=glow('eye_gold', '#ffe14a', 3.5),
        ruby=toon('ruby', '#ff2d55', shade='#a00f3c', light='#ff9ab0', spec=1.0, rim=1.0, emit=0.4),
    )


def horn(name, base, s, side, mat, gold, scale=1.0):
    """curved horn; s = which head (+-1), side = +-1 (y)"""
    b = Vector(base)
    k = scale
    pts = [b, b + Vector((s * 0.05, side * 0.42, 0.3)) * k, b + Vector((s * 0.15, side * 0.7, 0.8)) * k,
           b + Vector((s * 0.3, side * 0.68, 1.3)) * k, b + Vector((s * 0.42, side * 0.45, 1.68)) * k]
    tube(name, pts, [0.24 * k, 0.22 * k, 0.17 * k, 0.1 * k, 0.0], mat, segs=8)
    for i, t in enumerate((1, 2)):
        tan = (Vector(pts[t + 1]) - Vector(pts[t - 1])).normalized()
        r = (0.23, 0.18)[i] * k
        torus('%s_ring%d' % (name, i), r, 0.04 * k, gold, 10, 5, 'Z', loc=pts[t], rot=aim(tan), ol=0.015)
    return pts[-1]


def build():
    begin('DB_15_Primal', ol=0.035)
    M = mats()
    stone, crim, gold, bone, leather, lava, eye, ruby = (M[k] for k in ('stone', 'crim', 'gold', 'bone', 'leather', 'lava', 'eye', 'ruby'))

    cyl('handle', 0.15, 1.5, leather, segs=12, bev=0.02)
    coil('grip_spiral', 0.152, 0.026, -0.45, 0.45, 4, gold, segs=5, steps=10, ol=0.012)
    tips = {}
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        torus('grip_end_' + n, 0.17, 0.045, gold, 12, 6, loc=(s * 0.54, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.58, 0), (0.58, 0.26), (0.66, 0.3), (0.8, 0.5), (0.9, 0.54), (0.94, 0.48), (0.94, 0)], gold, 12, scale=(s, 1, 1))
        for k in range(4):
            d = radial(s, 90, k * 90 + 45)
            sphere('collar_ruby_%s%d' % (n, k), 0.085, ruby, 8, 5, loc=Vector((s * 0.86, 0, 0)) + d * 0.52, ol=0.015)
        lathe('drum_' + n, [(0.9, 0), (0.9, 0.7), (0.98, 0.82), (1.5, 0.88), (2.05, 0.82), (2.14, 0.7), (2.14, 0)], stone, 14, scale=(s, 1, 1))
        for j, x in enumerate((1.02, 2.02)):
            lathe('rim_%s%d' % (n, j), [(-0.1, 0.8), (-0.08, 0.9), (0.08, 0.9), (0.1, 0.8)], gold, 14, loc=(s * x, 0, 0), caps=False, ol=0.03)
        # glowing rune inlays between the rims
        for k in range(6):
            ang = k * 60 + 30
            d = radial(s, 90, ang)
            p = Vector((s * 1.52, 0, 0)) + d * 0.865
            box('rune_bar_%s%d' % (n, k), (0.5, 0.07, 0.06), lava, bev=0.02, bsegs=1, loc=p, rot=(ang - 90, 0, 0), ol=0)
            crystal('rune_gem_%s%d' % (n, k), 0.1, 0.12, lava, sides=4, tip=0.5, both=True,
                    loc=Vector((s * (1.3 if k % 2 else 1.74), 0, 0)) + d * 0.87, rot=aim(d), ol=0)
        # sun-ray crown around the outer rim
        for k in range(8):
            ang = k * 45 + 22.5
            d = radial(s, 78, ang)
            cone('ray_%s%d' % (n, k), 0.11, 0.36, gold, 5, loc=Vector((s * 2.08, 0, 0)) + radial(s, 90, ang) * 0.84, rot=aim(d), ol=0.02)
        # beast mask (faces outward)
        lathe('mask_' + n, [(2.12, 0), (2.12, 0.76), (2.22, 0.78), (2.3, 0.7), (2.34, 0.4), (2.34, 0)], crim, 12, scale=(s, 1, 1))
        box('snout_' + n, (0.3, 0.56, 0.34), gold, bev=0.07, loc=(s * 2.45, 0, -0.1))
        box('nose_' + n, (0.1, 0.2, 0.12), stone, bev=0.04, bsegs=1, loc=(s * 2.6, 0, 0.0), ol=0.015)
        box('jaw_' + n, (0.2, 0.62, 0.16), bone, bev=0.05, loc=(s * 2.42, 0, -0.5))
        for side in (-1, 1):
            m = 'a' if side < 0 else 'b'
            box('brow_%s%s' % (n, m), (0.16, 0.42, 0.14), stone, bev=0.04, bsegs=1, loc=(s * 2.4, side * 0.34, 0.4), rot=(side * -22, 0, 0))
            sphere('eye_%s%s' % (n, m), 0.13, eye, 8, 5, loc=(s * 2.36, side * 0.34, 0.2), scale=(0.6, 1, 0.75))
            cone('fang_up_%s%s' % (n, m), 0.07, 0.24, bone, 6, loc=(s * 2.52, side * 0.2, -0.26), rot=(180, 0, 0), ol=0.015)
            cone('fang_lo_%s%s' % (n, m), 0.075, 0.3, bone, 6, loc=(s * 2.46, side * 0.27, -0.44), ol=0.015)
            # tusks
            tube('tusk_%s%s' % (n, m), [(s * 2.2, side * 0.6, -0.36), (s * 2.42, side * 0.9, -0.55), (s * 2.56, side * 1.08, -0.38), (s * 2.58, side * 1.1, -0.02)],
                 [0.13, 0.12, 0.08, 0.0], bone, segs=7)
            tips[(s, side)] = horn('horn_%s%s' % (n, m), (s * 1.5, side * 0.55, 0.55), s, side, bone, gold)
        crystal('brow_gem_' + n, 0.13, 0.3, ruby, sides=4, tip=0.5, both=True, loc=(s * 2.37, 0, 0.5), rot=(0, 0, 0), ol=0.02)
        for j, (x, h) in enumerate(((1.15, 0.34), (1.5, 0.48), (1.85, 0.34))):
            cone('spine_%s%d' % (n, j), 0.13, h, bone, 6, loc=(s * x, 0, 0.84), ol=0.02)
        for j, x in enumerate((1.25, 1.75)):
            cone('chin_spike_%s%d' % (n, j), 0.11, 0.26, bone, 6, loc=(s * x, 0, -0.84), rot=(180, 0, 0), ol=0.02)

    # ---------------- FX
    fx(True)
    rnd = random.Random(15)
    fl_o = glow('flame_orange', '#ff6a1a', 2.0)
    fl_y = glow('flame_yellow', '#ffe66b', 2.4)
    fl_r = glow('flame_red', '#ff2a2a', 1.8)
    bolt_m = glow('bolt', '#fff7b0', 3.2)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_aura_red_' + n, 1.75, ghost('aura_red', '#ff3a1a', 1.2, 0.12), 16, 10, loc=(s * 1.6, 0, 0.25), scale=(1, 1, 1.15))
        sphere('fx_aura_gold_' + n, 1.25, ghost('aura_gold', '#ffc23a', 1.2, 0.07), 16, 10, loc=(s * 1.6, 0, 0.1))
        for k in range(6):
            x = s * rnd.uniform(1.0, 2.2)
            y = rnd.uniform(0.1, 0.7)
            h = rnd.uniform(0.7, 1.25)
            z = 0.75 + rnd.uniform(0, 0.25)
            rz = rnd.uniform(0, 360)
            flame('fx_flame_%s%d' % (n, k), h, 0.2, fl_r if k % 3 == 0 else fl_o, bend=0.18, loc=(x, y, z), rot=(0, 0, rz))
            flame('fx_flame_in_%s%d' % (n, k), h * 0.55, 0.11, fl_y, bend=0.15, loc=(x, y, z + 0.03), rot=(0, 0, rz))
        bolt('fx_bolt_horns_' + n, tips[(s, -1)], tips[(s, 1)], bolt_m, r=0.035, n=7, amp=0.22, seed=3 + s)
        bolt('fx_bolt_wrap_a_' + n, (s * 0.95, -0.6, 0.7), (s * 2.5, -1.0, -0.6), bolt_m, r=0.04, n=7, amp=0.2, seed=8 + s)
        bolt('fx_bolt_wrap_b_' + n, tips[(s, -1)], (s * 2.9, -0.5, 1.2), bolt_m, r=0.035, n=5, amp=0.16, seed=12 + s)
        torus('fx_halo_' + n, 1.35, 0.03, glow('halo_gold', '#ffd75a', 2.2), 28, 4, loc=(s * 1.55, 0, 0), rot=(0, 0, s * 12))
    bolt('fx_bolt_bridge', (-0.9, -0.2, 0.6), (0.9, -0.2, 0.6), bolt_m, r=0.035, n=8, amp=0.16, seed=21)
    emb = glow('ember', '#ffb347', 3.0)
    for i in range(14):
        s = -1 if i % 2 else 1
        sphere('fx_ember_%d' % i, rnd.uniform(0.03, 0.06), emb, 6, 4,
               loc=(s * rnd.uniform(0.6, 2.8), rnd.uniform(-1.3, 0.6), rnd.uniform(0.2, 2.6)))
    spk = glow('spark_white', '#ffffff', 2.5)
    for i in range(6):
        s = -1 if i % 2 else 1
        star('fx_sparkle_%d' % i, rnd.uniform(0.1, 0.18), 0.03, 4, 0.02, spk,
             loc=(s * rnd.uniform(1.0, 2.7), -rnd.uniform(1.0, 1.4), rnd.uniform(-0.5, 1.8)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    return stats('DB_15_Primal')
