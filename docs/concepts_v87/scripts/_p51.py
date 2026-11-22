import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_21.py', [
    # bloomstalker
    ("'*glow2': '#d8a8ff'}), 4.5)", "'*glow2': '#d8a8ff'}), 4.05)"),
    ("        for t in range(3):\n            p('root_toe', (0.1, 0.24, 0.1), mm('root'), (sgn * 0.28 + (t - 1) * 0.14, -0.24, 0.05), rot=(0, 0, (t - 1) * 25))",
     "        for t in range(5):\n            p('root_toe', (0.08, 0.24, 0.1), mm('root'), (sgn * 0.28 + (t - 2) * 0.08, -0.24, 0.05), rot=(0, 0, (t - 2) * 18))"),
    ("    p('stem_ring', (1.1, 1.0, 0.16), mm('belly'), (0, 0, LEG + 1.2))\n",
     "    p('stem_ring', (1.1, 1.0, 0.16), mm('belly'), (0, 0, LEG + 1.2))\n"
     "    for j in range(3):\n        p('stem_band', (1.04, 0.94, 0.06), mm('root'), (0, 0, LEG + 0.15 + j * 0.2))\n"
     "    grid(B, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='stem_spot', span=(0.6, 0.5))\n"
     "    grid(B, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='stem_spot', span=(0.6, 0.5))\n"),
    ("        for j in range(4):\n            p('thread', (0.1, 0.1, 0.3), mm('belly'), (sgn * (0.6 + 0.12 * j), -0.06 * j, LEG + 0.9 - j * 0.26), rot=(0, sgn * 20, 0))",
     "        for j in range(6):\n            p('thread', (0.1, 0.1, 0.22), mm('belly'), (sgn * (0.6 + 0.085 * j), -0.04 * j, LEG + 0.92 - j * 0.18), rot=(0, sgn * 20, 0))"),
    ("    p('gills', (2.2, 2.0, 0.06), mm('belly'), (0, 0.05, zc - 0.27))\n",
     "    p('gills', (2.2, 2.0, 0.06), mm('belly'), (0, 0.05, zc - 0.27))\n"
     "    for k_ in range(4):\n        ang = math.radians(k_ * 90)\n        p('cap_rim', (0.5, 0.5, 0.08), mm('belly'), (math.cos(ang) * 0.75, 0.05 + math.sin(ang) * 0.7, zc + 0.22), rot=(0, 0, k_ * 90))\n"),
    # marauder
    ("'*glow2': '#ffe68a'}), 3.0)", "'*glow2': '#ffe68a'}), 3.82)"),
    ("    grid(Hd, 't', 3, 2, mm('dark'), (0.1, 0.1), name='wart', span=(0.6, 0.4))\n",
     "    grid(Hd, 't', 3, 2, mm('dark'), (0.1, 0.1), name='wart', span=(0.6, 0.4))\n"
     "    grid(Hd, 'l', 2, 2, mm('dark'), (0.1, 0.1), name='wart', span=(0.6, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('dark'), (0.1, 0.1), name='wart', span=(0.6, 0.5))\n"
     "    p('tongue', (0.3, 0.04, 0.08), mm('accent'), (0.2, Hd.front - 0.02, Hd.c.z - 0.26))\n"
     "    for k_ in range(8):\n"
     "        ang = math.radians(k_ * 45)\n"
     "        p('neck_frill', (0.24, 0.24, 0.12), mm('belly' if k_ % 2 else 'accent'), (math.cos(ang) * 0.7, Hd.c.y + math.sin(ang) * 0.5, Hd.bot - 0.02), rot=(0, 0, k_ * 45))\n"),
    ("    grid(B, 'r', 2, 3, mm('dark'), (0.12, 0.12), name='wart', span=(0.6, 0.6))\n    # puffball",
     "    grid(B, 'r', 2, 3, mm('dark'), (0.12, 0.12), name='wart', span=(0.6, 0.6))\n"
     "    grid(B, 'k', 3, 4, mm('belly'), (0.12, 0.12), name='back_spot', span=(0.7, 0.7))\n"
     "    p('belt', (B.s.x + 0.08, B.s.y + 0.08, 0.16), mm('wood'), (0, B.c.y, B.c.z - B.s.z * 0.3))\n"
     "    for k_ in range(6):\n"
     "        p('belt_stud', (0.1, 0.06, 0.1), mm('sac'), ((k_ - 2.5) * 0.24, B.front - 0.04, B.c.z - B.s.z * 0.3))\n"
     "    for i, (x, z, s) in enumerate(((-0.2, 0.0, 0.3), (0.3, 0.1, 0.34), (-0.8, 0.7, 0.3), (0.8, 0.8, 0.3))):\n"
     "        b('spore_sac_small', (s, s, s), mm('sac'), (x, B.back + 0.1, B.c.z + z), bev=0.06)\n"
     "        p('small_pore', (s * 0.3, 0.06, s * 0.3), mm('dark'), (x, B.back + 0.1 + s * 0.5, B.c.z + z))\n"
     "    # puffball"),
    ("    for k_ in range(5):\n        ang = math.radians(k_ * 72)\n        p('shield_dot'", "    for k_ in range(10):\n        ang = math.radians(k_ * 36)\n        p('shield_dot'"),
    ("p('shield_dot', (0.06, 0.2, 0.2)", "p('shield_dot', (0.06, 0.14, 0.14)"),
    ("    for k_ in range(4):\n        ang = math.radians(k_ * 90 + 45)\n        p('club_spike'", "    for k_ in range(8):\n        ang = math.radians(k_ * 45 + 22)\n        p('club_spike'"),
    ("    for i in range(6):\n        p('spore', (0.14, 0.14, 0.14)", "    for i in range(10):\n        p('spore', (0.12, 0.12, 0.12)"),
    ("B.c.z + 1.3 + 0.25 * i), rot=(45, 45, 0))", "B.c.z + 1.3 + 0.16 * i), rot=(45, 45, 0))"),
    # cap mantis
    ("'*glow3': '#ffe68a'}), 3.0)", "'*glow3': '#ffe68a'}), 3.42)"),
    ("    for k_ in range(7):\n        ang = math.radians(k_ * 30)\n        p('hood_dot'", "    for k_ in range(13):\n        ang = math.radians(k_ * 15)\n        p('hood_dot'"),
    ("p('hood_dot', (0.18, 0.06, 0.18)", "p('hood_dot', (0.12, 0.06, 0.12)"),
    ("            for k_ in range(3):\n                ang = math.radians(k_ * 120)\n                p('leg_cap_dot'", "            for k_ in range(5):\n                ang = math.radians(k_ * 72)\n                p('leg_cap_dot'"),
    ("        for t in range(3):\n            p('scythe_tooth', (0.06, 0.08, 0.1), mm('belly'), (sgn * 0.32, -1.4 - t * 0.2, zb + 0.06))",
     "        for t in range(5):\n            p('scythe_tooth', (0.06, 0.08, 0.1), mm('belly'), (sgn * 0.32, -1.3 - t * 0.14, zb + 0.06))"),
    ("    for k_ in range(9):\n        ang = math.radians(k_ * 22.5)\n        p('hood_glow'", "    for k_ in range(13):\n        ang = math.radians(k_ * 15)\n        p('hood_glow'"),
    ("    b('thorax', (0.8, 0.8, 0.5), mm('main'), (0, -0.4, zb + 0.1), bev=0.12)\n",
     "    b('thorax', (0.8, 0.8, 0.5), mm('main'), (0, -0.4, zb + 0.1), bev=0.12)\n"
     "    grid(B, 'l', 3, 2, mm('cap2'), (0.12, 0.12), name='side_spot', span=(0.7, 0.5))\n"
     "    grid(B, 'r', 3, 2, mm('cap2'), (0.12, 0.12), name='side_spot', span=(0.7, 0.5))\n"
     "    grid(Box((0, -0.4, zb + 0.1), (0.8, 0.8, 0.5)), 't', 2, 2, mm('accent'), (0.1, 0.1), name='thorax_dot', span=(0.6, 0.6))\n"
     "    for j in range(4):\n        p('back_stripe', (1.5, 0.06, 0.04), mm('dark'), (0, 0.1 + j * 0.4, zb + 0.26))\n"
     "    for j in range(4):\n        p('lobe_dot', (0.14, 0.14, 0.04), mm('dot'), ((j - 1.5) * 0.3, 1.0, zb + 0.52))\n"),
])
print('ok')
