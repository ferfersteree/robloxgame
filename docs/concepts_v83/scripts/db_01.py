from gymlib import *


def build():
    begin('DB_01_Wooden', ol=0.03)
    wood = toon('wood', '#c07a3c', light='#e3a35c')
    dark = toon('wood_dark', '#8b5229', light='#b3743f')
    bark = toon('bark', '#74482a', shade='#3d2320', light='#96633a', spec=0.2)
    cut = toon('wood_cut', '#f0cf93', light='#fff0c4', spec=0.3)
    ringc = toon('wood_ring', '#c98f4e', spec=0.0, rim=0.0)
    rope = toon('rope', '#e2c07d', shade='#9a7340', light='#f7e2a8', spec=0.2)
    strap = toon('leather', '#6b3d22', light='#93592f', spec=0.3)
    leafm = toon('leaf', '#62c53c', shade='#2c7a35', light='#a8e85a')
    berry = toon('berry', '#e8403a', light='#ff8a6a', spec=1.0)
    shroom = toon('shroom_cap', '#e8553a', light='#ff9a6a', spec=1.0)
    white = toon('cream', '#fff3d8', spec=0.2)

    cyl('handle', 0.15, 1.5, dark, segs=12, bev=0.02)
    coil('grip_strap', 0.152, 0.03, -0.45, 0.45, 5, strap, segs=5, steps=10, ol=0.015)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        coil('rope_collar_' + n, 0.2, 0.055, s * 0.565, s * 0.70, 2.5, rope, segs=6, steps=10, ol=0.02)
        lathe('collar_' + n, [(0.64, 0), (0.64, 0.36), (0.67, 0.42), (0.73, 0.42), (0.76, 0.36), (0.76, 0)], dark, 14, scale=(s, 1, 1))
        lathe('log_' + n, [(0.73, 0), (0.73, 0.50), (0.79, 0.59), (0.96, 0.63), (1.13, 0.59), (1.19, 0.50), (1.19, 0)], bark, 16, scale=(s, 1, 1))
        torus('band_a_' + n, 0.615, 0.05, rope, 18, 6, loc=(s * 0.85, 0, 0), ol=0.02)
        torus('band_b_' + n, 0.615, 0.05, rope, 18, 6, loc=(s * 1.07, 0, 0), ol=0.02)
        lathe('face_' + n, [(1.17, 0), (1.17, 0.47), (1.22, 0.47), (1.25, 0.43), (1.25, 0)], cut, 16, scale=(s, 1, 1))
        torus('ring_a_' + n, 0.33, 0.022, ringc, 16, 4, loc=(s * 1.25, 0, 0), ol=0)
        torus('ring_b_' + n, 0.2, 0.022, ringc, 14, 4, loc=(s * 1.25, 0, 0), ol=0)
        lathe('plug_' + n, [(1.24, 0), (1.24, 0.12), (1.29, 0.12), (1.31, 0.09), (1.31, 0)], dark, 10, scale=(s, 1, 1), ol=0.02)
        # knots on bark
        for i, (ang, xx) in enumerate(((35, 0.9), (150, 1.02), (255, 0.93))):
            a = math.radians(ang + (20 if s > 0 else 0))
            sphere('knot_%s%d' % (n, i), 0.09, cut, 8, 5, loc=(s * xx, 0.6 * math.cos(a), 0.6 * math.sin(a)),
                   scale=(1, 1, 1), ol=0.02)
        # branch stub
        a = math.radians(205 if s > 0 else -25)
        dirv = (0.25 * s, math.cos(a), math.sin(a))
        p0 = Vector((s * 0.96, 0.55 * math.cos(a), 0.55 * math.sin(a)))
        p1 = p0 + Vector(dirv).normalized() * 0.26
        tube('stub_' + n, [p0, p1], [0.1, 0.085], bark, segs=7)
        sphere('stub_cut_' + n, 0.075, cut, 7, 4, loc=p1, ol=0)

    # sprout with leaves and berries on right head
    tube('sprout', [(0.96, 0, 0.58), (0.99, -0.02, 0.78), (1.06, -0.05, 0.93), (1.16, -0.08, 1.0)], [0.045, 0.04, 0.03, 0.02], leafm, segs=5, ol=0.02)
    leaf('leaf_a', 0.5, 0.26, leafm, loc=(1.02, -0.03, 0.86), rot=(70, -55, 20), ol=0.025)
    leaf('leaf_b', 0.42, 0.22, leafm, loc=(1.0, -0.02, 0.78), rot=(-60, -140, -10), ol=0.025)
    leaf('leaf_c', 0.3, 0.16, leafm, loc=(1.15, -0.08, 1.0), rot=(80, -20, -30), ol=0.02)
    sphere('berry_a', 0.075, berry, 8, 5, loc=(0.86, -0.16, 0.66), ol=0.02)
    sphere('berry_b', 0.06, berry, 8, 5, loc=(0.96, -0.24, 0.62), ol=0.02)
    # mushroom + leaf on left head
    tube('shroom_stem', [(-0.95, 0.05, 0.58), (-0.97, 0.05, 0.78)], [0.06, 0.05], white, segs=6, ol=0.02)
    lathe('shroom_cap', [(0.74, 0.17), (0.80, 0.15), (0.86, 0.08), (0.88, 0)], shroom, 10, 'Z', loc=(-0.97, 0.05, 0), ol=0.025)
    sphere('shroom_dot_a', 0.03, white, 6, 4, loc=(-0.91, -0.04, 0.83), ol=0)
    sphere('shroom_dot_b', 0.025, white, 6, 4, loc=(-1.04, 0.0, 0.84), ol=0)
    leaf('leaf_d', 0.36, 0.2, leafm, loc=(-0.82, -0.1, 0.6), rot=(60, -40, 200), ol=0.025)

    fx(True)
    sp = glow('spark_warm', '#fff2a8', 3.0)
    star('fx_sparkle_a', 0.11, 0.03, 4, 0.02, sp, loc=(1.32, -0.5, 0.72), rot=(90, 0, 20))
    star('fx_sparkle_b', 0.07, 0.02, 4, 0.02, sp, loc=(-1.25, -0.55, 0.45), rot=(90, 0, 0))
    leaf('fx_falling_leaf', 0.2, 0.11, toon('leaf', '#62c53c'), loc=(0.2, -0.3, 0.75), rot=(40, 20, 60))
    fx(False)
    return stats('DB_01_Wooden')
