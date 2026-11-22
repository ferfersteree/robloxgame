import io


def patch(fn, new_build, anim_add, anchor):
    s = io.open(fn, encoding='utf-8').read()
    a = s.index('def build(place')
    b = s.index('def anims():')
    s = s[:a] + new_build.strip('\n') + '\n\n\n' + s[b:]
    assert anchor in s, (fn, anchor)
    if anim_add not in s:
        s = s.replace(anchor, anchor + anim_add, 1)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)


SQ = r'''
def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    fur = studs('sq_fur', '#f47c2c')
    cream = studs('sq_cream', '#fff0d2')
    dark = studs('sq_dark', '#a8481a')
    nose = smooth('sq_nose', '#3a2026', 0.2)
    line = smooth('sq_line', '#3a2620', 0.3)
    white = smooth('sq_tooth', '#ffffff', 0.15)
    pink = smooth('sq_pink', '#ff9db4', 0.35)
    acorn = studs('sq_acorn', '#d09a48')
    cap = studs('sq_cap', '#70482a')
    # ---- body: sits upright
    seg('body', 'root', (0, 0.05, 0.4))
    blk('body', (0.62, 0.58, 0.68), fur, (0, 0.06, 0.5))
    blk('hips', (0.7, 0.42, 0.36), fur, (0, 0.16, 0.3))
    blk('belly', (0.42, 0.06, 0.5), cream, (0, -0.24, 0.48), bev=0.02)
    for i, (w, z) in enumerate(((0.34, 0.76), (0.24, 0.69), (0.12, 0.62))):
        pix('chest_fluff_%d' % i, (w, 0.04, 0.08), cream, (0, -0.275 - i * 0.01, z))
    pix('stripe_c', (0.12, 0.03, 0.5), dark, (0, 0.365, 0.52))
    for sg, n in LR:
        pix('stripe_' + n, (0.07, 0.03, 0.44), cream, (sg * 0.13, 0.365, 0.52))
        pix('stripe_o' + n, (0.05, 0.03, 0.4), dark, (sg * 0.21, 0.365, 0.52))
        pix('side_' + n, (0.03, 0.2, 0.14), cream, (sg * 0.325, -0.02, 0.5))
        pix('side_b' + n, (0.03, 0.12, 0.1), cream, (sg * 0.325, 0.1, 0.42))
    # ---- head
    seg('head', 'body', (0, -0.02, 0.82))
    blk('head', (0.84, 0.72, 0.7), fur, (0, -0.08, 1.13))
    blk('head_top', (0.6, 0.5, 0.08), fur, (0, -0.08, 1.5), bev=0.03)
    blk('muzzle', (0.36, 0.14, 0.2), cream, (0, -0.47, 0.95), bev=0.03)
    blk('nose', (0.1, 0.06, 0.07), nose, (0, -0.56, 1.02), bev=0.015, ol=0.008)
    pix('mouth', (0.03, 0.03, 0.07), line, (0, -0.545, 0.94))
    pix('fore_c', (0.1, 0.03, 0.2), dark, (0, -0.445, 1.38))
    pix('fore_d', (0.2, 0.03, 0.06), dark, (0, -0.445, 1.45))
    for sg, n in LR:
        blk('cheek_' + n, (0.26, 0.22, 0.28), cream, (sg * 0.36, -0.36, 0.95), bev=0.05)
        pix('cheek_tuft_a' + n, (0.09, 0.09, 0.09), cream, (sg * 0.5, -0.34, 0.9))
        pix('cheek_tuft_b' + n, (0.07, 0.07, 0.07), cream, (sg * 0.5, -0.32, 1.03))
        pix('blush_' + n, (0.12, 0.03, 0.06), pink, (sg * 0.37, -0.475, 1.02))
        pix('tooth_' + n, (0.06, 0.03, 0.07), white, (sg * 0.035, -0.54, 0.87))
        for j, dz in enumerate((0.04, -0.03)):
            pix('whisker_%s%d' % (n, j), (0.18, 0.02, 0.02), white, (sg * 0.56, -0.4, 0.95 + dz), rot=(0, -sg * (10 if j == 0 else -10), sg * 10))
        pix('temple_' + n, (0.03, 0.2, 0.14), dark, (sg * 0.425, 0.0, 1.3))
    anime_eyes(0.27, 0.2, -0.445, 1.2, '#7a3f18', brow='#70401a', brow_tilt=-8, brow_dz=0.09)
    for sg, n in LR:
        seg('ear_' + n, 'head', (sg * 0.26, -0.05, 1.46))
        blk('ear_' + n, (0.2, 0.1, 0.26), fur, (sg * 0.28, -0.05, 1.58), bev=0.03)
        pix('ear_in_' + n, (0.1, 0.03, 0.16), pink, (sg * 0.28, -0.105, 1.57))
        pix('ear_tuft_a' + n, (0.1, 0.08, 0.14), dark, (sg * 0.3, -0.05, 1.76))
        pix('ear_tuft_b' + n, (0.06, 0.06, 0.1), dark, (sg * 0.33, -0.05, 1.86))
    # ---- arms hold the acorn
    for sg, n in LR:
        seg('leg_f' + n, 'body', (sg * 0.2, -0.2, 0.62))
        blk('arm_' + n, (0.13, 0.28, 0.13), fur, (sg * 0.18, -0.32, 0.56), rot=(-30, 0, 0), bev=0.02)
        blk('hand_' + n, (0.13, 0.12, 0.12), cream, (sg * 0.13, -0.44, 0.5), bev=0.02)
        for j in (-1, 1):
            pix('finger_%s%d' % (n, j), (0.04, 0.05, 0.05), dark, (sg * 0.13 + j * 0.035, -0.51, 0.5))
        seg('leg_b' + n, 'body', (sg * 0.28, 0.12, 0.28))
        blk('thigh_' + n, (0.18, 0.4, 0.34), fur, (sg * 0.36, 0.12, 0.24), bev=0.03)
        blk('foot_' + n, (0.19, 0.44, 0.1), cream, (sg * 0.36, -0.06, 0.05), bev=0.02)
        for j in (-1, 0, 1):
            pix('toe_%s%d' % (n, j + 1), (0.045, 0.04, 0.06), dark, (sg * 0.36 + j * 0.06, -0.29, 0.05))
    seg('acorn', 'body', (0, -0.5, 0.46))
    blk('acorn', (0.2, 0.2, 0.22), acorn, (0, -0.52, 0.44), bev=0.04)
    blk('acorn_cap', (0.24, 0.24, 0.09), cap, (0, -0.52, 0.57), bev=0.02)
    pix('acorn_stem', (0.04, 0.04, 0.07), cap, (0, -0.52, 0.65))
    pix('acorn_tip', (0.06, 0.06, 0.04), cap, (0, -0.52, 0.32))
    pix('acorn_shine', (0.05, 0.03, 0.08), cream, (-0.05, -0.625, 0.47))
    for j in (-1, 1):
        pix('acorn_dot_%d' % j, (0.05, 0.03, 0.04), acorn, (j * 0.06, -0.645, 0.57))
    # ---- huge stacked tail curling over the back
    seg('tail', 'body', (0, 0.34, 0.3))
    blk('tail_a', (0.36, 0.4, 0.36), fur, (0, 0.52, 0.34))
    blk('tail_b', (0.42, 0.4, 0.5), fur, (0, 0.72, 0.72))
    pix('tail_stripe_b', (0.14, 0.03, 0.4), dark, (0, 0.925, 0.72))
    pix('tail_tuft_b1', (0.12, 0.12, 0.12), fur, (0.22, 0.8, 0.5))
    pix('tail_tuft_b2', (0.12, 0.12, 0.12), fur, (-0.22, 0.66, 0.92))
    seg('tail_tip', 'tail', (0, 0.72, 0.97))
    blk('tail_c', (0.48, 0.46, 0.46), fur, (0, 0.7, 1.2))
    blk('tail_d', (0.42, 0.38, 0.34), cream, (0, 0.48, 1.48))
    blk('tail_e', (0.32, 0.26, 0.24), fur, (0, 0.28, 1.4), bev=0.04)
    pix('tail_stripe_c', (0.14, 0.03, 0.36), dark, (0, 0.935, 1.2))
    pix('tail_top', (0.14, 0.2, 0.03), dark, (0, 0.8, 1.44))
    pix('tail_tuft_c1', (0.12, 0.12, 0.12), cream, (0.22, 0.5, 1.62))
    pix('tail_tuft_c2', (0.12, 0.12, 0.12), cream, (-0.2, 0.42, 1.66))
    pix('tail_tuft_c3', (0.12, 0.12, 0.12), fur, (0.26, 0.74, 1.4))
    assemble()
    marker('Head', 'head', (0, -0.08, 1.13))
    marker('Chest', 'body', (0, -0.24, 0.55))
    marker('Hit', 'body', (0, 0.06, 0.6))
    anims()
    build_fx()
    return bake_actions()
'''
if __name__ == '__main__':
  patch('an_squirrel.py', SQ,
      "    blink(I, (28,))\n    blink(R, (26,))\n    for n in ('L', 'R'):\n        for f, a in ((1, 0), (30, 0), (32, 18), (34, 0), (40, 0)):\n            k(I, 'ear_' + n, f, rot=(a, 0, 0))\n",
      "        k(I, 'head', f, rot=(a, 0, 0))\n")

HH = r'''
def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    spine = studs('hh_spine', '#8a5a38')
    spine_tip = studs('hh_spine_tip', '#f0d8a8')
    face = studs('hh_face', '#f7d9ac')
    belly = studs('hh_belly', '#fff0d6')
    nose = smooth('hh_nose', '#2b1a20', 0.15)
    line = smooth('hh_line', '#3a2620', 0.3)
    apple = studs('hh_apple', '#f0402e')
    stem = studs('hh_stem', '#5a3a1c')
    leafm = studs('hh_leaf', '#5bbb36')
    leafo = studs('hh_leaf_o', '#f0a020')
    blush = smooth('hh_blush', '#ff9aa8', 0.4)
    shine = smooth('hh_shine', '#ffffff', 0.1)
    seg('body', 'root', (0, 0.05, 0.45))
    blk('body', (1.0, 1.05, 0.62), belly, (0, 0.08, 0.42))
    blk('coat', (1.12, 1.1, 0.6), spine, (0, 0.2, 0.62))
    blk('coat_top', (0.86, 0.86, 0.2), spine, (0, 0.22, 0.98))
    blk('coat_back', (0.9, 0.2, 0.5), spine, (0, 0.8, 0.55))
    for i, x in enumerate((-0.44, -0.22, 0.0, 0.22, 0.44)):
        pix('fringe_%d' % i, (0.16, 0.06, 0.12 if i % 2 else 0.18), spine_tip, (x, -0.36, 0.38 if i % 2 else 0.35))
    for sg, n in LR:
        for j, y in enumerate((-0.1, 0.2, 0.5)):
            pix('fringe_s%s%d' % (n, j), (0.04, 0.18, 0.12), spine_tip, (sg * 0.57, y, 0.36))
    # spikes: square pyramids (the silhouette)
    n = 0
    for i, x in enumerate((-0.36, -0.12, 0.12, 0.36)):
        for j, y in enumerate((-0.14, 0.12, 0.38, 0.62)):
            z = 1.06 if abs(x) < 0.2 else 0.9
            tilt = Vector((x * 0.9, 0.35 + y * 0.6, 1.0))
            cone('spike_t%d' % n, 0.12, 0.36, spine_tip if (i + j) % 2 else spine, 4, loc=(x, y, z), rot=aim(tilt, 45), ol=0.012)
            n += 1
    for s in (-1, 1):
        for y in (-0.1, 0.2, 0.5):
            cone('spike_s%d' % n, 0.11, 0.32, spine, 4, loc=(s * 0.55, y, 0.74), rot=aim((s, 0.4, 0.5), 45), ol=0.012)
            n += 1
        for y in (0.05, 0.38):
            cone('spike_s%d' % n, 0.1, 0.28, spine_tip, 4, loc=(s * 0.56, y, 0.52), rot=aim((s, 0.4, 0.15), 45), ol=0.012)
            n += 1
    for x in (-0.3, 0.0, 0.3):
        cone('spike_b%d' % n, 0.11, 0.32, spine_tip if x else spine, 4, loc=(x, 0.9, 0.62), rot=aim((x, 1, 0.4), 45), ol=0.012)
        n += 1
    blk('apple', (0.3, 0.3, 0.28), apple, (0.2, 0.3, 1.26), bev=0.06)
    pix('apple_stem', (0.05, 0.05, 0.1), stem, (0.2, 0.3, 1.44))
    pix('apple_leaf', (0.16, 0.08, 0.04), leafm, (0.29, 0.3, 1.46), rot=(0, -25, 0))
    pix('apple_shine', (0.06, 0.03, 0.1), shine, (0.12, 0.145, 1.3))
    pix('leaf_a', (0.2, 0.14, 0.04), leafo, (-0.28, 0.5, 1.2), rot=(15, 20, 30))
    pix('leaf_a_stem', (0.03, 0.08, 0.03), stem, (-0.2, 0.42, 1.18), rot=(15, 20, 30))
    # ---- big face
    seg('head', 'body', (0, -0.4, 0.5))
    blk('face', (0.86, 0.4, 0.62), face, (0, -0.58, 0.5))
    blk('hood', (0.92, 0.3, 0.16), spine, (0, -0.5, 0.85))
    for i, x in enumerate((-0.33, -0.11, 0.11, 0.33)):
        pix('hood_tip_%d' % i, (0.14, 0.05, 0.1), spine_tip if i % 2 else spine, (x, -0.66, 0.76))
    blk('snout', (0.32, 0.26, 0.22), face, (0, -0.9, 0.36), bev=0.04)
    blk('nose', (0.14, 0.09, 0.11), nose, (0, -1.05, 0.42), bev=0.02, ol=0.01)
    pix('mouth', (0.1, 0.03, 0.03), line, (0, -1.03, 0.29))
    for sg, nn in LR:
        blk('ear_' + nn, (0.18, 0.08, 0.18), face, (sg * 0.36, -0.62, 0.9), bev=0.03)
        pix('ear_in_' + nn, (0.09, 0.03, 0.09), blush, (sg * 0.36, -0.665, 0.9))
        pix('blush_' + nn, (0.13, 0.03, 0.07), blush, (sg * 0.3, -0.785, 0.34))
        pix('cheek_' + nn, (0.08, 0.08, 0.1), belly, (sg * 0.45, -0.72, 0.3))
        for j, (dx, dz) in enumerate(((0.0, 0.0), (0.06, 0.05))):
            pix('freckle_%s%d' % (nn, j), (0.03, 0.03, 0.03), spine, (sg * (0.2 + dx), -0.785, 0.42 + dz))
    anime_eyes(0.25, 0.21, -0.785, 0.6, '#5a7a2a', lash=True, brow='#8a5a38', brow_tilt=8, brow_dz=0.08, sleepy=0.14)
    for sg, nn in LR:
        for fb, y in (('f', -0.3), ('b', 0.4)):
            seg('leg_%s%s' % (fb, nn), 'body', (sg * 0.32, y, 0.2))
            blk('leg_%s%s' % (fb, nn), (0.18, 0.2, 0.18), face, (sg * 0.32, y, 0.13), bev=0.03)
            blk('paw_%s%s' % (fb, nn), (0.2, 0.26, 0.08), belly, (sg * 0.32, y - 0.04, 0.04), bev=0.015)
            for j in (-1, 0, 1):
                pix('toe_%s%s%d' % (fb, nn, j + 1), (0.045, 0.04, 0.05), spine, (sg * 0.32 + j * 0.065, y - 0.18, 0.035))
    seg('tail', 'body', (0, 0.9, 0.3))
    blk('tail', (0.14, 0.14, 0.12), face, (0, 0.95, 0.3), bev=0.02)
    pix('tail_tip', (0.08, 0.08, 0.08), belly, (0, 1.04, 0.32))
    assemble()
    marker('Head', 'head', (0, -0.6, 0.5))
    marker('Chest', 'body', (0, -0.38, 0.4))
    marker('Hit', 'body', (0, 0.2, 0.95))
    anims()
    build_fx()
    return bake_actions()
'''
if __name__ == '__main__':
  patch('an_hedgehog.py', HH,
      "    blink(I, (30,))\n    blink(R, (25,))\n    for f, a in ((1, 0), (26, 0), (29, 25), (32, -20), (35, 0), (40, 0)):\n        k(I, 'tail', f, rot=(0, 0, a))\n",
      "        k(I, 'head', f, rot=(a, 0, 0))\n")

FOX = r'''
def build(place=(0, 0, 0)):
    begin(ID, 'AN_' + ID, 'AN_%s_FX' % ID, place)
    fur = studs('fx_fur', '#f57f1f')
    dk = studs('fx_dk', '#c8551a')
    white = studs('fx_white', '#fff6e8')
    black = studs('fx_black', '#3a2a2e')
    scarf = studs('fx_scarf', '#3fbe4a')
    scarf_dk = studs('fx_scarf_dk', '#2a8a34')
    scarf_lt = studs('fx_scarf_lt', '#b6f070')
    tooth = smooth('fx_bone', '#fffaf0', 0.3)
    nose = smooth('fx_nose', '#24161c', 0.15)
    pink = smooth('fx_pink', '#ff9db4', 0.35)
    seg('body', 'root', (0, 0.1, 0.85))
    blk('body', (0.9, 1.3, 0.72), fur, (0, 0.25, 0.85))
    blk('chest', (0.66, 0.14, 0.6), white, (0, -0.42, 0.82))
    for i, w in enumerate((0.5, 0.38, 0.26, 0.14)):
        pix('bib_%d' % i, (w, 0.04, 0.09), white, (0, -0.5 - i * 0.008, 0.98 - i * 0.1))
    blk('belly', (0.6, 1.0, 0.08), white, (0, 0.25, 0.47))
    pix('back_stripe', (0.2, 0.9, 0.03), dk, (0, 0.3, 1.225))
    for i, (x, y) in enumerate(((-0.28, 0.0), (0.28, 0.2), (-0.26, 0.5), (0.27, 0.7))):
        pix('back_spot_%d' % i, (0.14, 0.14, 0.03), dk, (x, y, 1.225))
    for sg, n in LR:
        pix('side_tuft_a' + n, (0.03, 0.3, 0.14), white, (sg * 0.465, -0.1, 0.6))
        pix('side_tuft_b' + n, (0.03, 0.18, 0.1), white, (sg * 0.465, 0.1, 0.54))
        pix('hip_' + n, (0.03, 0.26, 0.26), dk, (sg * 0.465, 0.65, 0.95))
    # accessory: leaf-green scarf with a bone charm (rarity 3)
    blk('scarf', (0.98, 0.56, 0.22), scarf, (0, -0.36, 1.16))
    blk('scarf_knot', (0.26, 0.14, 0.2), scarf_dk, (0.26, -0.56, 1.02), bev=0.03)
    blk('scarf_end_a', (0.18, 0.08, 0.34), scarf, (0.36, -0.57, 0.8), rot=(0, 12, 0), bev=0.03)
    blk('scarf_end_b', (0.16, 0.08, 0.26), scarf_dk, (0.2, -0.58, 0.84), rot=(0, -8, 0), bev=0.03)
    for sg, n in LR:
        for j in range(3):
            pix('scarf_dot_%s%d' % (n, j), (0.03, 0.09, 0.09), scarf_lt, (sg * 0.495, -0.52 + 0.17 * j, 1.16))
    pix('charm', (0.2, 0.05, 0.06), tooth, (-0.2, -0.52, 1.0))
    pix('charm_a', (0.07, 0.06, 0.1), tooth, (-0.3, -0.52, 1.0))
    pix('charm_b', (0.07, 0.06, 0.1), tooth, (-0.1, -0.52, 1.0))
    # ---- head: big cube
    seg('head', 'body', (0, -0.35, 1.15))
    blk('head', (1.16, 0.9, 0.92), fur, (0, -0.55, 1.6))
    blk('head_top', (0.8, 0.6, 0.08), fur, (0, -0.55, 2.08), bev=0.03)
    blk('snout', (0.46, 0.34, 0.3), white, (0, -1.12, 1.34))
    blk('snout_top', (0.3, 0.3, 0.08), fur, (0, -1.1, 1.52), bev=0.02)
    blk('nose', (0.16, 0.08, 0.11), nose, (0, -1.31, 1.44), bev=0.02, ol=0.01)
    pix('mouth_line', (0.03, 0.03, 0.08), nose, (0, -1.295, 1.34))
    pix('fore_mark_a', (0.14, 0.03, 0.2), white, (0, -1.005, 1.92))
    pix('fore_mark_b', (0.08, 0.03, 0.1), white, (0, -1.005, 1.78))
    for sg, n in LR:
        blk('cheek_' + n, (0.34, 0.3, 0.34), white, (sg * 0.5, -0.84, 1.34), bev=0.05)
        pix('cheek_tuft_a' + n, (0.12, 0.12, 0.12), white, (sg * 0.7, -0.8, 1.26))
        pix('cheek_tuft_b' + n, (0.1, 0.1, 0.1), white, (sg * 0.71, -0.78, 1.42))
        pix('cheek_tuft_c' + n, (0.08, 0.08, 0.08), white, (sg * 0.69, -0.76, 1.53))
        pix('mouth_' + n, (0.12, 0.03, 0.03), nose, (sg * 0.07, -1.295, 1.29))
        pix('fang_' + n, (0.05, 0.03, 0.07), tooth, (sg * 0.13, -1.295, 1.24))
        pix('blush_' + n, (0.16, 0.03, 0.08), pink, (sg * 0.5, -0.995, 1.4))
        for j, dz in enumerate((0.05, -0.04)):
            pix('whisker_%s%d' % (n, j), (0.2, 0.02, 0.02), black, (sg * 0.36, -1.2, 1.36 + dz), rot=(0, -sg * (12 if j == 0 else -12), sg * 25))
        pix('temple_' + n, (0.03, 0.24, 0.2), dk, (sg * 0.585, -0.3, 1.8))
    anime_eyes(0.32, 0.28, -1.005, 1.72, '#f2a81e', brow='#3a2a2e', brow_tilt=-14, brow_dz=0.11)
    for sg, n in LR:
        seg('ear_' + n, 'head', (sg * 0.36, -0.5, 2.05))
        blk('ear_base_' + n, (0.34, 0.16, 0.26), fur, (sg * 0.37, -0.5, 2.16))
        blk('ear_mid_' + n, (0.26, 0.15, 0.22), fur, (sg * 0.39, -0.5, 2.38))
        blk('ear_tip_' + n, (0.16, 0.14, 0.18), black, (sg * 0.41, -0.5, 2.56), bev=0.03)
        pix('ear_in_' + n, (0.2, 0.03, 0.2), white, (sg * 0.37, -0.585, 2.16))
        pix('ear_in_b' + n, (0.12, 0.03, 0.16), white, (sg * 0.39, -0.58, 2.36))
        pix('ear_tuft_' + n, (0.06, 0.05, 0.1), white, (sg * 0.26, -0.6, 2.1))
    for sg, n in LR:
        for fb, y in (('f', -0.22), ('b', 0.72)):
            seg('leg_%s%s' % (fb, n), 'body', (sg * 0.28, y, 0.6))
            blk('leg_%s%s' % (fb, n), (0.26, 0.28, 0.4), fur, (sg * 0.28, y, 0.44))
            blk('sock_%s%s' % (fb, n), (0.28, 0.3, 0.2), black, (sg * 0.28, y, 0.2))
            blk('paw_%s%s' % (fb, n), (0.3, 0.36, 0.12), black, (sg * 0.28, y - 0.04, 0.06), bev=0.03)
            for j in (-1, 0, 1):
                pix('toe_%s%s%d' % (fb, n, j + 1), (0.05, 0.04, 0.06), white, (sg * 0.28 + j * 0.09, y - 0.225, 0.05))
    # ---- big bushy tail with a white tip
    seg('tail', 'body', (0, 0.88, 1.0))
    blk('tail_a', (0.4, 0.46, 0.4), fur, (0, 1.08, 1.08))
    blk('tail_b', (0.6, 0.6, 0.6), fur, (0, 1.52, 1.3))
    blk('tail_c', (0.5, 0.4, 0.5), white, (0, 1.96, 1.5))
    blk('tail_tip', (0.26, 0.16, 0.26), white, (0, 2.2, 1.58), bev=0.04)
    pix('tail_ring', (0.56, 0.06, 0.56), dk, (0, 1.8, 1.42))
    for i, (x, y, z, m) in enumerate(((0.3, 1.5, 1.62, fur), (-0.32, 1.4, 1.1, fur), (0.1, 1.6, 0.98, fur),
                                       (0.26, 2.0, 1.74, white), (-0.24, 2.05, 1.3, white))):
        pix('tail_tuft_%d' % i, (0.14, 0.14, 0.14), m, (x, y, z))
    assemble()
    marker('Head', 'head', (0, -0.55, 1.6))
    marker('Chest', 'body', (0, -0.48, 0.85))
    marker('Hit', 'body', (0, 0.25, 1.2))
    anims()
    build_fx()
    return bake_actions()
'''
if __name__ == '__main__':
  patch('an_fox.py', FOX, "    blink(I, (22,))\n    blink(R, (40,))\n", "        k(I, 'head', f, rot=(0, a, 0))\n")
if __name__ == '__main__':
  print('ok')
