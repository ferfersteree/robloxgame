import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [
    ("('lava_dragonfly', 'Lava Dragonfly', 25, 4, 'air', 3.5, 'flyer')", "('lava_dragonfly', 'Lava Dragonfly', 25, 4, 'air', 2.5, 'flyer')"),
])
sub('biome_25.py', [
    # dragonfly
    ("**{'*glow': '#ff8a3a', '*glow2': '#ffd84a'}), 1.6, hover=2.6, z0=zc)", "**{'*glow': '#ff8a3a', '*glow2': '#ffd84a'}), 1.1, hover=2.6, z0=zc)"),
    ("    grid(B, 't', 2, 2, mm('accent'), (0.1, 0.1), name='thorax_spot', span=(0.5, 0.5))\n",
     "    grid(B, 't', 2, 2, mm('accent'), (0.1, 0.1), name='thorax_spot', span=(0.5, 0.5))\n"
     "    grid(B, 'l', 2, 2, mm('dark'), (0.08, 0.08), name='thorax_side', span=(0.5, 0.5))\n"
     "    grid(B, 'r', 2, 2, mm('dark'), (0.08, 0.08), name='thorax_side', span=(0.5, 0.5))\n"),
    ("    for sgn in (-1, 1):\n        b('compound_eye', (0.4, 0.5, 0.56), mm('accent'), (sgn * 0.28, -0.62, zc + 0.12), bev=0.14)\n",
     "    for sgn in (-1, 1):\n        b('compound_eye', (0.4, 0.5, 0.56), mm('accent'), (sgn * 0.28, -0.62, zc + 0.12), bev=0.14)\n"
     "        for t in range(3):\n            p('facet', (0.04, 0.1, 0.1), mm('belly'), (sgn * 0.49, -0.7 + t * 0.14, zc + 0.2))\n"
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.08, 0.08), name='head_dot', span=(0.4, 0.4), offset=0.1)\n"),
    ("    for i in range(4):\n        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)\n        y0 = 0.35 + i * 0.6",
     "    for i in range(5):\n        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)\n        y0 = 0.35 + i * 0.6"),
    ("            s = 0.24 - 0.02 * i\n", "            s = 0.24 - 0.018 * i\n"),
    ("    p('tail_tip', (0.1, 0.24, 0.1), mm('accent'), (0, 2.85, zc))", "    p('tail_tip', (0.1, 0.24, 0.1), mm('accent'), (0, 3.45, zc))"),
    ("            p('wing_spot', (0.16, 0.2, 0.05), mm('vein'), (sgn * 1.9, dy + math.sin(math.radians(ang)) * sgn * 1.65, zc + 0.33), rot=(0, 0, ang * sgn))\n",
     "            p('wing_spot', (0.16, 0.2, 0.05), mm('vein'), (sgn * 1.9, dy + math.sin(math.radians(ang)) * sgn * 1.65, zc + 0.33), rot=(0, 0, ang * sgn))\n"
     "            for q in range(4):\n"
     "                rr = 0.5 + q * 0.32\n"
     "                p('wing_cell', (0.04, 0.32, 0.05), mm('vein'), (sgn * rr, dy + math.sin(math.radians(ang)) * sgn * (rr - 0.25), zc + 0.33), rot=(0, 0, ang * sgn))\n"),
    ("            p('leg', (0.04, 0.04, 0.3), mm('dark'), (sgn * 0.24, y - 0.05, zc - 0.42), rot=(-25, sgn * 10, 0))\n",
     "            p('leg', (0.04, 0.04, 0.3), mm('dark'), (sgn * 0.24, y - 0.05, zc - 0.42), rot=(-25, sgn * 10, 0))\n"
     "            p('leg_foot', (0.06, 0.1, 0.04), mm('accent'), (sgn * 0.26, y - 0.12, zc - 0.56))\n"),
    ("            p('wing_glow', (0.12, 0.12, 0.06), mm('glow2'), (sgn * 2.0, dy + math.sin(math.radians(ang)) * sgn * 1.75, zc + 0.34))\n",
     "            p('wing_glow', (0.12, 0.12, 0.06), mm('glow2'), (sgn * 2.0, dy + math.sin(math.radians(ang)) * sgn * 1.75, zc + 0.34))\n"
     "            p('wing_glow_root', (0.1, 0.1, 0.06), mm('glow'), (sgn * 0.4, dy + math.sin(math.radians(ang)) * sgn * 0.15, zc + 0.34))\n"),
    ("    for i in range(4):\n        p('ember_dot', (0.08, 0.08, 0.08), mm('glow'), (0.1 * math.sin(i * 2), 0.6 + i * 0.55, zc + 0.2), rot=(45, 45, 0))",
     "    for i in range(8):\n        p('ember_dot', (0.07, 0.07, 0.07), mm('glow'), (0.1 * math.sin(i * 2), 0.6 + i * 0.36, zc + 0.2), rot=(45, 45, 0))"),
    # wyrm
    ("blush='#ff9ab4',\n                        **{'*lava': '#ff6a1a', '*glow': '#ffb84a', '*glow2': '#ff4a2a'}), 3.0)",
     "blush='#ff9ab4',\n                        **{'*lava': '#ff6a1a', '*glow': '#ffb84a', '*glow2': '#ff4a2a'}), 3.9)"),
    ("    grid(Hd, 't', 2, 2, mm('plate'), (0.12, 0.12), name='head_plate', span=(0.6, 0.6))\n",
     "    grid(Hd, 't', 2, 2, mm('plate'), (0.12, 0.12), name='head_plate', span=(0.6, 0.6))\n"
     "    grid(Hd, 'l', 2, 1, mm('lava'), (0.08, 0.08), name='cheek_crack', span=(0.5, 0.1))\n"
     "    grid(Hd, 'r', 2, 1, mm('lava'), (0.08, 0.08), name='cheek_crack', span=(0.5, 0.1))\n"),
    # titan
    ("'*sun2': '#ff8a3a', '*lava': '#ff6a1a'}), 4.0)", "'*sun2': '#ff8a3a', '*lava': '#ff6a1a'}), 5.46)"),
    ("    grid(B, 'f', 3, 2, mm('belly'), (0.16, 0.16), name='stone_block', span=(0.7, 0.4), offset=-0.5)\n",
     "    grid(B, 'f', 4, 3, mm('belly'), (0.14, 0.14), name='stone_block', span=(0.7, 0.4), offset=-0.5)\n"),
    ("        for j in range(5):\n            ang = math.radians(j * 72)\n            b('fern_frond'", "        for j in range(7):\n            ang = math.radians(j * 51.4)\n            b('fern_frond'"),
    ("rot=(0, 15, j * 72), bev=0.02)", "rot=(0, 15, j * 51.4), bev=0.02)\n        for t in range(2):\n            p('shoulder_rock', (0.2, 0.2, 0.16), mm('belly'), (sx + sgn * 0.2, B.c.y - 0.3 + t * 0.4, B.top + 0.2))"),
    ("    for j in range(5):\n        p('moss_drip', (0.14, 0.14, 0.2), mm('moss2'), ((j - 2) * 0.24, Hd.c.y - Hd.s.y / 2 - 0.02, Hd.top - 0.1))",
     "    for j in range(8):\n        p('moss_drip', (0.1, 0.14, 0.2 + 0.06 * (j % 2)), mm('moss2'), ((j - 3.5) * 0.14, Hd.c.y - Hd.s.y / 2 - 0.02, Hd.top - 0.1))\n"
     "    grid(Hd, 'l', 2, 2, mm('moss'), (0.1, 0.1), name='face_moss', span=(0.5, 0.5))"),
    ("    for k_ in range(8):\n        ang = math.radians(k_ * 45)\n        p('sun_ray'", "    for k_ in range(12):\n        ang = math.radians(k_ * 30)\n        p('sun_ray'"),
    ("rot=(0, 90 - k_ * 45, 0))", "rot=(0, 90 - k_ * 30, 0))"),
])
print('ok')
