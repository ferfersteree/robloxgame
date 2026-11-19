from gymlib import *

BG = '#3b2466'
NAME = 'DB_06_Golden'


def mats():
    return dict(
        gold=toon('gold', '#ffcf4d', shade='#c2742a', light='#fff2a6', spec=1.0),
        deep=toon('gold_deep', '#e6a52a', shade='#8a4a14', light='#ffe07a', spec=1.0),
        ruby=toon('gold_ruby', '#ff2d55', shade='#a00f3c', light='#ff9ab0', spec=1.0, rim=1.0, emit=0.4),
        emerald=toon('gold_emerald', '#22d67a', shade='#0a7a4a', light='#b4ffd2', spec=1.0, rim=1.0, emit=0.3),
        sapph=toon('gold_sapphire', '#3a7bff', shade='#1a3aa6', light='#a8c8ff', spec=1.0, rim=1.0, emit=0.3),
        pearl=toon('gold_pearl', '#fff4ef', shade='#c9b5c8', light='#ffffff', spec=1.0),
        velvet=toon('gold_velvet', '#b01c3c', shade='#5a0c24', light='#e0485a', spec=0.2),
        glint=glow('gold_glint', '#ffd860', 2.2),
        spark=glow('spark_white', '#ffffff', 2.5),
    )


def build():
    begin(NAME, ol=0.03)
    M = mats()
    gold, deep, ruby, emerald, sapph, pearl, glint, spark = (M[k] for k in ('gold', 'deep', 'ruby', 'emerald', 'sapph', 'pearl', 'glint', 'spark'))

    cyl('handle', 0.15, 1.5, deep, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.42, 0.42, 4, gold, segs=5, steps=10, ol=0.012)
    gem_cycle = (emerald, sapph, emerald, sapph)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        torus('grip_end_' + n, 0.16, 0.03, gold, 12, 6, loc=(s * 0.535, 0, 0), ol=0.02)
        lathe('collar_' + n, [(0.56, 0), (0.56, 0.24), (0.62, 0.28), (0.74, 0.28), (0.8, 0.34), (0.86, 0.3), (0.86, 0)], gold, 12, scale=(s, 1, 1))
        # layered chamfered plates
        lathe('plate_a_' + n, [(0.86, 0), (0.86, 0.5), (0.92, 0.58), (1.08, 0.58), (1.14, 0.5), (1.14, 0)], deep, 14, scale=(s, 1, 1))
        lathe('plate_b_' + n, [(1.14, 0), (1.14, 0.62), (1.22, 0.76), (1.42, 0.76), (1.5, 0.62), (1.5, 0)], gold, 14, scale=(s, 1, 1))
        lathe('plate_c_' + n, [(1.5, 0), (1.5, 0.52), (1.58, 0.56), (1.64, 0.52), (1.68, 0.4), (1.68, 0)], deep, 14, scale=(s, 1, 1))
        # big gem in the end cap + bezel
        crystal('end_gem_' + n, 0.32, 0.34, ruby if s < 0 else sapph, sides=6, tip=0.3, both=True,
                loc=(s * 1.6, 0, 0), rot=aim((s, 0, 0)), ol=0.02)
        torus('bezel_' + n, 0.33, 0.045, gold, 14, 6, loc=(s * 1.66, 0, 0), ol=0.02)
        # crown ring of points
        for k in range(8):
            ang = k * 45
            d = radial(s, 90, ang)
            cone('crown_pt_%s%d' % (n, k), 0.085, 0.26, gold, 6, loc=Vector((s * 1.32, 0, 0)) + d * 0.74, rot=aim(d), ol=0.018)
        # gems on the rim
        for k, ang in enumerate((22.5, 112.5, 202.5, 292.5)):
            d = radial(s, 90, ang)
            crystal('rim_gem_%s%d' % (n, k), 0.11, 0.24, gem_cycle[k], sides=6, tip=0.35,
                    loc=Vector((s * 1.32, 0, 0)) + d * 0.72, rot=aim(d), ol=0.018)
        # pearl studs on the first plate
        for k in range(4):
            d = radial(s, 90, k * 90 + 45)
            sphere('pearl_%s%d' % (n, k), 0.07, pearl, 8, 5, loc=Vector((s * 0.99, 0, 0)) + d * 0.58, ol=0.015)
        # filigree rings
        torus('filigree_a_' + n, 0.54, 0.03, deep, 16, 5, loc=(s * 0.88, 0, 0), ol=0.015)
        torus('filigree_b_' + n, 0.62, 0.035, deep, 16, 5, loc=(s * 1.51, 0, 0), ol=0.015)

    # ---------------- FX
    fx(True)
    rnd = random.Random(66)
    aura = ghost('gold_aura', '#ffcf5a', 1.0, 0.1)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_aura_' + n, 1.1, aura, 14, 8, loc=(s * 1.25, 0, 0), scale=(1.2, 1, 1))
    for i in range(4):
        s = -1 if i % 2 else 1
        crystal('fx_glint_%d' % i, 0.06, 0.2, glint, sides=4, tip=0.4, both=True,
                loc=(s * rnd.uniform(0.8, 1.8), rnd.uniform(-0.8, 0.6), rnd.uniform(0.9, 1.5)),
                rot=(rnd.uniform(0, 40), rnd.uniform(0, 40), rnd.uniform(0, 90)))
    for i in range(9):
        s = -1 if i % 2 else 1
        star('fx_sparkle_%d' % i, rnd.uniform(0.1, 0.2), 0.03, 4, 0.02, spark if i % 3 else glint,
             loc=(s * rnd.uniform(0.7, 1.9), -rnd.uniform(0.9, 1.3), rnd.uniform(-0.8, 1.2)), rot=(90, 0, rnd.uniform(0, 45)))
    fx(False)
    return stats(NAME)
