import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_22.py', [
    # colossus
    ("**{'*glow': '#ff6a8a', '*glow2': '#ffe08a'}), 4.4)", "**{'*glow': '#ff6a8a', '*glow2': '#ffe08a'}), 3.73)"),
    ("        p('spine_fin', (0.1, 0.16, 0.24), mm('joint'), (0, -0.6 + i * 0.36, zb + 0.74))\n",
     "        p('spine_fin', (0.1, 0.16, 0.24), mm('joint'), (0, -0.6 + i * 0.36, zb + 0.74))\n"
     "        for sgn in (-1, 1):\n            p('vert_process', (0.2, 0.1, 0.08), mm('joint'), (sgn * 0.24, -0.6 + i * 0.36, zb + 0.52))\n"),
    ("    b('pelvis', (0.8, 0.5, 0.4), mm('main'), (0, 1.3, zb + 0.4), bev=0.08)\n",
     "    b('pelvis', (0.8, 0.5, 0.4), mm('main'), (0, 1.3, zb + 0.4), bev=0.08)\n"
     "    for sgn in (-1, 1):\n        p('hip_knob', (0.2, 0.2, 0.2), mm('joint'), (sgn * 0.42, 1.3, zb + 0.66))\n"),
    ("    b('neck_bone', (0.24, 0.5, 0.24), mm('main'), (0, -0.95, zb + 0.75), rot=(-30, 0, 0), bev=0.04)\n",
     "    b('neck_bone', (0.24, 0.5, 0.24), mm('main'), (0, -0.95, zb + 0.75), rot=(-30, 0, 0), bev=0.04)\n"
     "    for j in range(4):\n        p('neck_knob', (0.3, 0.08, 0.1), mm('joint'), (0, -0.78 - j * 0.1, zb + 0.62 + j * 0.06))\n"),
    ("    b('jaw', (0.8, 0.8, 0.24), mm('joint'), (0, -1.62, zb + 0.6), bev=0.06)\n",
     "    b('jaw', (0.8, 0.8, 0.24), mm('joint'), (0, -1.62, zb + 0.6), bev=0.06)\n"
     "    for sgn in (-1, 1):\n        p('jaw_hinge', (0.1, 0.2, 0.2), mm('accent'), (sgn * 0.42, -1.3, zb + 0.66))\n"),
    # reaper
    ("'*glow': '#ffd84a', '*glow2': '#ff8a3a'}), 3.0)", "'*glow': '#ffd84a', '*glow2': '#ff8a3a'}), 1.91)"),
    ("            for t in range(2):\n                p('leg_hair', (0.06, 0.06, 0.12), mm('hair'), (sgn * (0.75 + 0.2 * t), y, 0.5 - 0.08 * t))",
     "            for t in range(4):\n                p('leg_hair', (0.06, 0.06, 0.12), mm('hair'), (sgn * (0.7 + 0.12 * t), y, 0.52 - 0.06 * t))\n"
     "            p('leg_foot', (0.18, 0.2, 0.06), mm('jaw'), (sgn * 1.1, y - 0.03, 0.03))"),
    ("            p('jaw_tooth', (0.06, 0.08, 0.1), mm('belly'), (x - sgn * 0.12, y, 0.4))",
     "            p('jaw_tooth', (0.06, 0.08, 0.1), mm('belly'), (x - sgn * 0.12, y, 0.4))\n"
     "            p('jaw_tooth2', (0.06, 0.06, 0.08), mm('belly'), (x - sgn * 0.12, y - 0.12, 0.4))"),
    ("    b('thorax', (1.2, 0.7, 0.8), mm('main'), (0, -0.5, 0.6), bev=0.16)\n",
     "    b('thorax', (1.2, 0.7, 0.8), mm('main'), (0, -0.5, 0.6), bev=0.16)\n"
     "    TB = Box((0, -0.5, 0.6), (1.2, 0.7, 0.8))\n"
     "    grid(TB, 't', 3, 2, mm('belly'), (0.1, 0.1), name='thorax_spot', span=(0.7, 0.6))\n"
     "    grid(TB, 'l', 2, 2, mm('hair'), (0.1, 0.1), name='thorax_hair', span=(0.6, 0.5))\n"
     "    grid(TB, 'r', 2, 2, mm('hair'), (0.1, 0.1), name='thorax_hair', span=(0.6, 0.5))\n"),
    ("    eyes(Hd, 0.4, 0.26, 0.2, iris='#e86a3a', brow='#5a3a20')\n",
     "    eyes(Hd, 0.4, 0.26, 0.2, iris='#e86a3a', brow='#5a3a20')\n"
     "    grid(Hd, 't', 3, 2, mm('hair'), (0.1, 0.1), name='head_bristle', span=(0.7, 0.6))\n"),
    ("    for j in range(5):\n        p('sand_stream', (0.3 - 0.04 * j, 0.2, 0.3)", "    for j in range(9):\n        p('sand_stream', (0.3 - 0.02 * j, 0.2, 0.2)"),
    ("(0.1 * (j % 2), 1.95 + j * 0.06, 1.2 - j * 0.24))", "(0.1 * (j % 2), 1.95 + j * 0.04, 1.2 - j * 0.13))"),
    # vulture
    ("'*glow3': '#c88aff'}), 2.0, hover=4.0, z0=zc)", "'*glow3': '#c88aff'}), 2.53, hover=4.0, z0=zc)"),
    ("    grid(B, 't', 3, 4, mm('belly'), (0.12, 0.12), name='back_feather', span=(0.7, 0.8))\n",
     "    grid(B, 't', 4, 5, mm('belly'), (0.1, 0.1), name='back_feather', span=(0.7, 0.8))\n"),
    ("    for k_ in range(10):\n        ang = math.radians(k_ * 36)\n        p('ruff'", "    for k_ in range(16):\n        ang = math.radians(k_ * 22.5)\n        p('ruff'"),
    ("p('ruff', (0.3, 0.3, 0.26), mm('ruff'), (math.cos(ang) * 0.48, -0.5, zc + math.sin(ang) * 0.42), rot=(0, -k_ * 36, 0))",
     "p('ruff', (0.24, 0.3, 0.22), mm('ruff'), (math.cos(ang) * 0.48, -0.5, zc + math.sin(ang) * 0.42), rot=(0, -k_ * 22.5, 0))"),
    ("    for j in range(3):\n        b('neck', (0.26, 0.3, 0.26), mm('accent'), (0, -0.7 - j * 0.24, zc - 0.1 - j * 0.12), bev=0.05)\n",
     "    for j in range(3):\n        b('neck', (0.26, 0.3, 0.26), mm('accent'), (0, -0.7 - j * 0.24, zc - 0.1 - j * 0.12), bev=0.05)\n"
     "        p('neck_wrinkle', (0.28, 0.06, 0.28), mm('main'), (0, -0.6 - j * 0.24, zc - 0.06 - j * 0.12))\n"),
    ("        p('wing_elbow', (0.3, 0.3, 0.3), mm('bone'), (sgn * 1.9, 0.2, zc + 1.0))\n",
     "        p('wing_elbow', (0.3, 0.3, 0.3), mm('bone'), (sgn * 1.9, 0.2, zc + 1.0))\n"
     "        for j in range(5):\n            p('covert', (0.26, 0.3, 0.16), mm('main' if j % 2 else 'belly'), (sgn * (0.6 + j * 0.28), 0.12, zc + 0.36 + j * 0.15))\n"),
    ("    for j in range(5):\n        ang = (j - 2) * 18\n        b('tail_ray'", "    for j in range(7):\n        ang = (j - 3) * 13\n        b('tail_ray'"),
    ("    eyes(Hd, 0.34, 0.25, 0.08, iris='#ff5a6a', glow='#ff5a6a', brow=None)\n",
     "    eyes(Hd, 0.34, 0.25, 0.08, iris='#ff5a6a', glow='#ff5a6a', brow=None)\n"
     "    grid(Hd, 'l', 2, 2, mm('main'), (0.08, 0.08), name='head_spot', span=(0.5, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('main'), (0.08, 0.08), name='head_spot', span=(0.5, 0.5))\n"),
])
print('ok')
