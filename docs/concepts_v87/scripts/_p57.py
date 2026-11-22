import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [
    ("('storm_harrier', 'Storm Harrier', 24, 5, 'air', 8.0, 'bird')", "('storm_harrier', 'Storm Harrier', 24, 5, 'air', 5.5, 'bird')"),
])
sub('biome_24.py', [
    # revenant
    ("'*glow3': '#8ae8ff'}), 2.4, hover=2.4, z0=zc)", "'*glow3': '#8ae8ff'}), 3.71, hover=2.4, z0=zc)"),
    ("    for i in range(8):\n        ang = math.radians(i * 45 + 22)\n        p('cloak_prism', (0.3, 0.3, 0.6)",
     "    grid(B, 'f', 2, 3, mm('belly'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))\n"
     "    grid(B, 'k', 2, 3, mm('belly'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))\n"
     "    grid(B, 'l', 2, 3, mm('prism2'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))\n"
     "    grid(B, 'r', 2, 3, mm('prism1'), (0.1, 0.1), name='cloak_facet', span=(0.6, 0.7))\n"
     "    for i in range(16):\n        ang = math.radians(i * 22.5 + 11)\n        p('cloak_prism', (0.22, 0.22, 0.6)"),
    ("rot=(0, 0, i * 45 + 45))\n    # hem breaking", "rot=(0, 0, i * 22.5 + 45))\n    # hem breaking"),
    ("    for i in range(7):\n        ang = math.radians(i * 51)\n        p('hem_shard'", "    for i in range(12):\n        ang = math.radians(i * 30)\n        p('hem_shard'"),
    ("    grid(Hd, 't', 2, 2, mm('prism1'), (0.1, 0.1), name='hood_gem', span=(0.5, 0.5))\n",
     "    grid(Hd, 't', 2, 2, mm('prism1'), (0.1, 0.1), name='hood_gem', span=(0.5, 0.5))\n"
     "    grid(Hd, 'l', 2, 2, mm('prism3'), (0.1, 0.1), name='hood_gem', span=(0.5, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('prism2'), (0.1, 0.1), name='hood_gem', span=(0.5, 0.5))\n"),
    ("        for t in range(3):\n            p('finger_shard', (0.06, 0.06, 0.2), mm('belly'), (sgn * 1.0 + (t - 1) * 0.08, -0.42, zc + 0.3))",
     "        for t in range(5):\n            p('finger_shard', (0.05, 0.05, 0.2), mm('belly'), (sgn * 1.0 + (t - 2) * 0.06, -0.42, zc + 0.3))\n"
     "        for t in range(2):\n            p('cuff', (0.4, 0.44, 0.06), mm('accent'), (sgn * 0.7, -0.1, zc + 0.05 + t * 0.3))"),
    ("    b('chest_gem', (0.3, 0.1, 0.3), mm('glow'), (0, B.front - 0.02, zc + 0.1), rot=(0, 45, 0), bev=0.02)\n",
     "    b('chest_gem', (0.3, 0.1, 0.3), mm('glow'), (0, B.front - 0.02, zc + 0.1), rot=(0, 45, 0), bev=0.02)\n"
     "    for i in range(4):\n        ang = math.radians(i * 90)\n        p('gem_frame', (0.08, 0.08, 0.08), mm('glow2'), (math.cos(ang) * 0.24, B.front - 0.03, zc + 0.1 + math.sin(ang) * 0.24))\n"
     "    for i in range(6):\n        ang = math.radians(i * 60)\n        p('float_shard', (0.1, 0.1, 0.18), mm('glow3' if i % 2 else 'glow2'), (math.cos(ang) * 1.0, 0.05 + math.sin(ang) * 0.8, zc + 1.3 + 0.1 * (i % 2)), rot=(0, 0, 45))\n"),
    # harrier
    ("**{'*glow': '#ffe84a', '*glow2': '#8ae8ff'}), 2.6, hover=3.4, z0=zc)", "**{'*glow': '#ffe84a', '*glow2': '#8ae8ff'}), 1.79, hover=3.4, z0=zc)"),
    ("    grid(B, 't', 2, 4, mm('wing2'), (0.1, 0.1), name='back_feather', span=(0.6, 0.8))\n",
     "    grid(B, 't', 3, 6, mm('wing2'), (0.08, 0.08), name='back_feather', span=(0.6, 0.8))\n"
     "    grid(B, 'u', 2, 4, mm('belly'), (0.1, 0.1), name='belly_feather', span=(0.6, 0.8))\n"
     "    grid(B, 'l', 3, 2, mm('wing2'), (0.1, 0.1), name='side_feather', span=(0.7, 0.5))\n"
     "    grid(B, 'r', 3, 2, mm('wing2'), (0.1, 0.1), name='side_feather', span=(0.7, 0.5))\n"),
    ("    eyes(Hd, 0.32, 0.25, 0.16, iris='#ffe84a', brow='#1a1e3a', tilt=-12)\n",
     "    eyes(Hd, 0.32, 0.25, 0.16, iris='#ffe84a', brow='#1a1e3a', tilt=-12)\n"
     "    grid(Hd, 'l', 2, 2, mm('wing2'), (0.08, 0.08), name='cheek_feather', span=(0.5, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('wing2'), (0.08, 0.08), name='cheek_feather', span=(0.5, 0.5))\n"
     "    grid(Hd, 't', 2, 2, mm('wing2'), (0.08, 0.08), name='head_feather', span=(0.5, 0.5))\n"),
    ("    for j in range(4):\n        p('crest', (0.08, 0.2, 0.3 - 0.04 * j), mm('accent'), (0, -0.62 + j * 0.16, Hd.top + 0.08 + 0.02 * j), rot=(40, 0, 0))",
     "    for j in range(6):\n        p('crest', (0.08, 0.16, 0.3 - 0.03 * j), mm('accent'), (0, -0.66 + j * 0.11, Hd.top + 0.08 + 0.02 * j), rot=(40, 0, 0))"),
    ("        for j in range(5):\n            b('primary', (0.22, 1.4 - 0.12 * j, 0.08), mm('wing2' if j % 2 else 'wing'), (sgn * (0.75 + 0.12 * j), 1.1 + 0.1 * j, zc + 0.35 + 0.02 * j),\n              rot=(-15, 0, sgn * (8 + 4 * j)), bev=0.02)\n        p('wing_bolt', (0.08, 0.6, 0.09), mm('accent'), (sgn * 0.8, 0.9, zc + 0.42), rot=(-15, 0, sgn * 10))",
     "        for j in range(8):\n            b('primary', (0.16, 1.4 - 0.08 * j, 0.08), mm('wing2' if j % 2 else 'wing'), (sgn * (0.72 + 0.08 * j), 1.1 + 0.07 * j, zc + 0.35 + 0.015 * j),\n              rot=(-15, 0, sgn * (8 + 3 * j)), bev=0.02)\n"
     "        for j in range(6):\n            p('covert', (0.2, 0.2, 0.1), mm('main' if j % 2 else 'wing2'), (sgn * (0.5 + 0.08 * j), 0.1 + 0.15 * j, zc + 0.26))\n"
     "        for j in range(3):\n            p('wing_bolt', (0.08, 0.4, 0.09), mm('accent'), (sgn * (0.7 + 0.1 * j), 0.8 + 0.3 * j, zc + 0.42), rot=(-15, 0, sgn * (10 + 20 * (j % 2))))"),
    ("        p('fork_tip', (0.2, 0.24, 0.09), mm('accent'), (sgn * 0.3, 2.3, zc + 0.48), rot=(-12, 0, sgn * 40))\n",
     "        p('fork_tip', (0.2, 0.24, 0.09), mm('accent'), (sgn * 0.3, 2.3, zc + 0.48), rot=(-12, 0, sgn * 40))\n"
     "        for t in range(3):\n            p('tail_bar', (0.2, 0.06, 0.09), mm('dark'), (sgn * (0.16 + 0.04 * t), 1.35 + 0.25 * t, zc + 0.3 + 0.05 * t))\n"),
    ("        b('leg', (0.12, 0.3, 0.12), mm('beak'), (sgn * 0.2, 0.75, zc - 0.36), bev=0.02)\n",
     "        b('leg', (0.12, 0.3, 0.12), mm('beak'), (sgn * 0.2, 0.75, zc - 0.36), bev=0.02)\n"
     "        for t in range(2):\n            p('leg_feather', (0.16, 0.12, 0.12), mm('belly'), (sgn * 0.2, 0.62 + t * 0.1, zc - 0.28))\n"),
    ("        for j in range(5):\n            p('wing_tip_glow', (0.1, 0.16, 0.1), mm('glow' if j % 2 else 'glow2'), (sgn * (0.75 + 0.12 * j + 0.06 * j), 1.1 + 0.1 * j + (1.4 - 0.12 * j) / 2, zc + 0.4))",
     "        for j in range(8):\n            p('wing_tip_glow', (0.08, 0.14, 0.08), mm('glow' if j % 2 else 'glow2'), (sgn * (0.72 + 0.08 * j + 0.05 * j), 1.1 + 0.07 * j + (1.4 - 0.08 * j) / 2, zc + 0.4))"),
    ("    for i in range(6):\n        p('spark_trail'", "    for i in range(10):\n        p('spark_trail'"),
    ("(0.2 * math.sin(i * 1.7), 2.4 + i * 0.25, zc + 0.5 + 0.1 * i), rot=(45, 45, 0))", "(0.2 * math.sin(i * 1.7), 2.4 + i * 0.16, zc + 0.5 + 0.06 * i), rot=(45, 45, 0))"),
    # serpent
    ("'*glow3': '#ff6ad0'}), 3.0)\n    R = 1.3", "'*glow3': '#ff6ad0'}), 3.4)\n    R = 1.3"),
    ("    for j in range(5):\n        p('mane', (0.16, 0.3, 0.3), mm('accent'), (hx + 0.1 + (j - 2) * 0.16, 0.3, Hd.top - 0.05 + 0.06 * (2 - abs(j - 2))), rot=(30, 0, 0))",
     "    for j in range(9):\n        p('mane', (0.1, 0.3, 0.3), mm('accent'), (hx + 0.1 + (j - 4) * 0.09, 0.3, Hd.top - 0.05 + 0.03 * (4 - abs(j - 4))), rot=(30, 0, 0))"),
])
print('ok')
