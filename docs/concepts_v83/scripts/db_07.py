from gymlib import *

BG = '#4a5f8a'
NAME = 'DB_07_Mammoth'

# bone knuckle body profile (axial, radius)
BODY = [(0.62, 0), (0.62, 0.3), (0.7, 0.46), (0.95, 0.6), (1.25, 0.68), (1.5, 0.66), (1.62, 0.58), (1.66, 0.5), (1.66, 0)]


def mats():
    return dict(
        bone=toon('bone', '#f6e8c8', shade='#b08f78', light='#ffffff', spec=0.5),
        knuckle=toon('mam_knuckle', '#e8d4ae', shade='#a8876c', light='#fff4dc', spec=0.4),
        fur=toon('mam_fur', '#7a4a2a', shade='#3e2214', light='#a87040', spec=0.1),
        leather=toon('mam_leather', '#4a2c1c', shade='#241210', light='#6e4630', spec=0.2),
        red=toon('mam_red', '#d23a3a', shade='#7a1620', light='#ff7a6a', spec=0.4),
        teal=toon('mam_teal', '#2fb8b0', shade='#126a70', light='#9af0e6', spec=0.5),
        dark=toon('mam_dark', '#2a1c1c', shade='#120a0c', light='#4a3030', spec=0.1),
        snow=glow('mam_snow', '#e6f4ff', 2.4),
        spark=glow('spark_white', '#ffffff', 2.5),
    )


def r_at(x):
    for i in range(len(BODY) - 1):
        a, b = BODY[i], BODY[i + 1]
        if a[0] <= x <= b[0] and b[0] > a[0]:
            return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])
    return 0.5


def build():
    begin(NAME, ol=0.03)
    M = mats()
    bone, knuckle, fur, leather, red, teal, dark, snow, spark = (
        M[k] for k in ('bone', 'knuckle', 'fur', 'leather', 'red', 'teal', 'dark', 'snow', 'spark'))

    cyl('handle', 0.15, 1.5, leather, segs=12, bev=0.02)
    coil('grip_wrap', 0.152, 0.026, -0.42, 0.42, 4, bone, segs=5, steps=10, ol=0.012)
    stripe_x = (1.02, 1.17, 1.32)
    stripe_m = (teal, red, teal)
    bead_m = (teal, red, bone, red, teal)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        torus('grip_end_' + n, 0.16, 0.03, leather, 12, 6, loc=(s * 0.535, 0, 0), ol=0.02)
        lathe('body_' + n, BODY, knuckle, 14, scale=(s, 1, 1))
        # fur ruff
        for k in range(10):
            ang = k * 36
            d = radial(s, 75, ang)
            cone('ruff_%s%d' % (n, k), 0.12, 0.36, fur, 5, loc=Vector((s * 0.74, 0, 0)) + radial(s, 90, ang) * 0.46, rot=aim(d), ol=0.02)
        # painted stripes
        for j, x in enumerate(stripe_x):
            r = r_at(x)
            lathe('stripe_%s%d' % (n, j), [(-0.04, r + 0.01), (-0.04, r + 0.04), (0.04, r + 0.04), (0.04, r + 0.01)],
                  stripe_m[j], 14, loc=(s * x, 0, 0), caps=False, ol=0.015)
        # leather strap
        torus('strap_' + n, r_at(0.88) + 0.02, 0.04, leather, 14, 5, loc=(s * 0.88, 0, 0), ol=0.02)
        # bead string draped around the lower half
        for j in range(5):
            ang = 200 + 35 * j
            a = math.radians(ang)
            x = s * (1.45 - 0.06 * math.sin(math.pi * j / 4))
            sphere('bead_%s%d' % (n, j), 0.065, bead_m[j], 8, 5, loc=(x, (r_at(1.45) + 0.05) * math.cos(a), (r_at(1.45) + 0.05) * math.sin(a)), ol=0.015)
        # totem face on the end cap
        lathe('face_plate_' + n, [(1.66, 0), (1.66, 0.5), (1.72, 0.5), (1.78, 0.44), (1.78, 0)], leather, 14, scale=(s, 1, 1))
        for e in (-1, 1):
            sphere('face_eye_%s%d' % (n, e), 0.075, teal, 8, 5, loc=(s * 1.8, e * 0.17, 0.1), scale=(0.5, 1, 1), ol=0.015)
        box('face_brow_' + n, (0.08, 0.46, 0.09), red, bev=0.02, bsegs=1, loc=(s * 1.8, 0, 0.27), ol=0.018)
        box('face_mouth_' + n, (0.08, 0.28, 0.09), dark, bev=0.02, bsegs=1, loc=(s * 1.8, 0, -0.2), ol=0.015)
        # curved mammoth tusks sweeping out and up
        for side in (-1, 1):
            m = 'a' if side < 0 else 'b'
            pts = [(s * 0.9, side * 0.5, 0.05), (s * 1.2, side * 0.76, -0.08), (s * 1.5, side * 0.84, 0.02),
                   (s * 1.64, side * 0.78, 0.3), (s * 1.74, side * 0.6, 0.62), (s * 1.72, side * 0.4, 0.98)]
            tube('tusk_%s%s' % (n, m), pts, [0.17, 0.17, 0.15, 0.12, 0.08, 0.0], bone, segs=8)
            tan = (Vector(pts[2]) - Vector(pts[0])).normalized()
            torus('tusk_strap_%s%s' % (n, m), 0.19, 0.035, red, 10, 5, 'Z', loc=pts[1], rot=aim(tan), ol=0.015)

    # ---------------- FX
    fx(True)
    rnd = random.Random(77)
    breath = ghost('mam_breath', '#cfe8ff', 1.0, 0.1)
    for s in (-1, 1):
        n = 'L' if s < 0 else 'R'
        sphere('fx_breath_a_' + n, 0.34, breath, 12, 7, loc=(s * 2.1, -0.15, 0.15))
        sphere('fx_breath_b_' + n, 0.24, breath, 12, 7, loc=(s * 2.45, -0.3, 0.3))
        sphere('fx_breath_c_' + n, 0.17, breath, 10, 6, loc=(s * 2.7, -0.4, 0.5))
    for i in range(3):
        s = -1 if i % 2 else 1
        star('fx_flake_%d' % i, rnd.uniform(0.14, 0.2), 0.05, 6, 0.02, snow,
             loc=(s * rnd.uniform(0.9, 1.9), -rnd.uniform(0.9, 1.3), rnd.uniform(0.6, 1.5)), rot=(90, 0, rnd.uniform(0, 45)))
    star('fx_sparkle', 0.12, 0.03, 4, 0.02, spark, loc=(0.2, -1.1, 0.9), rot=(90, 0, 20))
    for i in range(4):
        s = -1 if i % 2 else 1
        sphere('fx_speck_%d' % i, rnd.uniform(0.03, 0.05), snow, 6, 4,
               loc=(s * rnd.uniform(0.8, 2.1), rnd.uniform(-1.0, 0.8), rnd.uniform(0.4, 1.6)))
    fx(False)
    return stats(NAME)
