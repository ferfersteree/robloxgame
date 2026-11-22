import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('kits.py', [
    # more orbit shapes
    ("        elif shape == 'cross':\n            p('orbit_a', (size * 1.6, size * 0.5, size * 0.5), m_, q)\n            p('orbit_b', (size * 0.5, size * 0.5, size * 1.6), m_, q)\n",
     "        elif shape == 'cross':\n            p('orbit_a', (size * 1.6, size * 0.5, size * 0.5), m_, q)\n            p('orbit_b', (size * 0.5, size * 0.5, size * 1.6), m_, q)\n"
     "        elif shape == 'bubble':\n"
     "            s2 = size * (1.6 if i % 3 == 0 else 1.0)\n"
     "            p('orbit_bubble', (s2, s2, s2), m_, q)\n"
     "            p('orbit_bubble_hi', (s2 * 0.3, s2 * 0.3, s2 * 0.3), mm('white'), (q[0] - s2 * 0.25, q[1] - s2 * 0.5, q[2] + s2 * 0.25))\n"
     "        elif shape == 'shard':\n"
     "            p('orbit_shard', (size * 0.6, size * 0.6, size * 3.0), m_, q, rot=(0, 15 * (1 if i % 2 else -1), 45))\n"
     "            p('orbit_shard_tip', (size * 0.4, size * 0.4, size * 0.8), mm('white'), (q[0], q[1], q[2] + size * 1.8), rot=(0, 0, 45))\n"
     "        elif shape == 'flame':\n"
     "            p('orbit_flame', (size * 1.2, size * 1.2, size * 1.2), m_, q, rot=(45, 45, 0))\n"
     "            p('orbit_flame_tip', (size * 0.7, size * 0.7, size * 1.4), m_, (q[0], q[1], q[2] + size * 1.1))\n"
     "            p('orbit_flame_tip2', (size * 0.4, size * 0.4, size * 0.8), mm('white'), (q[0], q[1], q[2] + size * 1.9))\n"
     "        elif shape == 'leaf':\n"
     "            p('orbit_leaf', (size * 2.0, size * 0.3, size * 1.0), m_, q, rot=(30, 0, math.degrees(ang)))\n"
     "            p('orbit_leaf_vein', (size * 1.8, size * 0.34, size * 0.15), mm('white'), q, rot=(30, 0, math.degrees(ang)))\n"
     "        elif shape == 'star':\n"
     "            p('orbit_star_a', (size * 1.8, size * 0.4, size * 0.4), m_, q, rot=(0, 0, math.degrees(ang)))\n"
     "            p('orbit_star_b', (size * 0.4, size * 0.4, size * 1.8), m_, q, rot=(0, 0, math.degrees(ang)))\n"
     "            p('orbit_star_c', (size * 0.7, size * 0.7, size * 0.7), mm('white'), q, rot=(45, 45, 0))\n"
     "        elif shape == 'gear':\n"
     "            p('orbit_gear', (size * 1.6, size * 0.4, size * 1.6), m_, q, rot=(0, 0, math.degrees(ang)))\n"
     "            for t in range(4):\n"
     "                p('orbit_tooth', (size * 0.5, size * 0.42, size * 0.5), m_, (q[0] + math.cos(t * 1.571) * size * 0.95, q[1], q[2] + math.sin(t * 1.571) * size * 0.95))\n"),
    # more crown kinds
    ("        p('halo_plate', (0.2, 0.09, 0.09), mm(col), q, rot=(0, 0, math.degrees(ang) + 90))\n        if kind == 'crown' and i % 2 == 0:\n",
     "        if kind == 'shards':\n"
     "            p('crown_shard', (0.12, 0.12, 0.5 if i % 2 else 0.32), mm(col), (q[0], q[1], q[2] + (0.2 if i % 2 else 0.1)), rot=(0, 0, 45))\n"
     "            continue\n"
     "        if kind == 'flames':\n"
     "            p('crown_flame', (0.16, 0.16, 0.16), mm(col), q, rot=(45, 45, 0))\n"
     "            p('crown_flame_tip', (0.08, 0.08, 0.3 if i % 2 else 0.2), mm(col), (q[0], q[1], q[2] + 0.2))\n"
     "            continue\n"
     "        if kind == 'stars':\n"
     "            p('crown_star_a', (0.24, 0.06, 0.06), mm(col), q, rot=(0, 0, math.degrees(ang)))\n"
     "            p('crown_star_b', (0.06, 0.06, 0.24), mm(col), q)\n"
     "            continue\n"
     "        if kind == 'leaves':\n"
     "            p('crown_leaf', (0.1, 0.24, 0.3), mm(col), (q[0], q[1], q[2] + 0.08), rot=(25, 0, math.degrees(ang) + 90))\n"
     "            continue\n"
     "        if kind == 'gears':\n"
     "            p('crown_gear', (0.24, 0.08, 0.24), mm(col), q, rot=(0, 0, math.degrees(ang) + 90))\n"
     "            p('crown_gear_hub', (0.08, 0.1, 0.08), mm('white'), q, rot=(0, 0, math.degrees(ang) + 90))\n"
     "            continue\n"
     "        p('halo_plate', (0.2, 0.09, 0.09), mm(col), q, rot=(0, 0, math.degrees(ang) + 90))\n        if kind == 'crown' and i % 2 == 0:\n"),
    # aura variants: style changes the ring layout (colour stays the rarity colour from the brief)
    ("def aura_kit(radius, rarity, n=14, motes=10, mote_col='glow', mote_r=None, height=1.6):",
     "def aura_kit(radius, rarity, n=14, motes=10, mote_col='glow', mote_r=None, height=1.6, style='ring'):"),
])
print('ok')
