import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_23.py', [
    # angler
    ("**{'*glow': '#8affe8', '*glow2': '#ffe68a'}), 2.6, hover=2.4, z0=zc)", "**{'*glow': '#8affe8', '*glow2': '#ffe68a'}), 2.33, hover=2.4, z0=zc)"),
    ("    for t in range(6):\n        p('tooth_top', (0.1, 0.08, 0.14), mm('tooth'), ((t - 2.5) * 0.18, -0.67, zc - 0.06))\n        p('tooth_bot', (0.1, 0.08, 0.12), mm('tooth'), ((t - 2.5) * 0.18 + 0.09, -0.67, zc - 0.44))",
     "    for t in range(8):\n        p('tooth_top', (0.08, 0.08, 0.14), mm('tooth'), ((t - 3.5) * 0.13, -0.67, zc - 0.06))\n        p('tooth_bot', (0.08, 0.08, 0.12), mm('tooth'), ((t - 3.5) * 0.13 + 0.06, -0.67, zc - 0.44))"),
    ("        for j in range(4):\n            p('photophore', (0.04, 0.1, 0.1), mm('glow'), (sgn * 0.81, -0.3 + j * 0.25, zc - 0.5))",
     "        for j in range(7):\n            p('photophore', (0.04, 0.08, 0.08), mm('glow'), (sgn * 0.81, -0.4 + j * 0.15, zc - 0.5))"),
    ("    grid(B, 'r', 3, 3, mm('accent'), (0.1, 0.1), name='spot', span=(0.6, 0.6))\n    sg('head', 'body', (0, -0.5, zc + 0.2))",
     "    grid(B, 'r', 3, 3, mm('accent'), (0.1, 0.1), name='spot', span=(0.6, 0.6))\n"
     "    grid(B, 'k', 3, 3, mm('accent'), (0.1, 0.1), name='spot', span=(0.6, 0.6))\n"
     "    grid(B, 'u', 3, 3, mm('belly'), (0.12, 0.12), name='under_dot', span=(0.6, 0.6))\n"
     "    for j in range(4):\n        p('dorsal_spike', (0.06, 0.1, 0.2), mm('accent'), (0, 0.1 + j * 0.16, zc + 1.0 + 0.04 * j))\n"
     "    sg('head', 'body', (0, -0.5, zc + 0.2))"),
    ("        for t in range(3):\n            p('fin_ray', (0.36, 0.04, 0.04), mm('accent'), (sgn * 0.96, 0.1 + t * 0.1, zc - 0.1))",
     "        for t in range(4):\n            p('fin_ray', (0.36, 0.04, 0.04), mm('accent'), (sgn * 0.96, 0.08 + t * 0.08, zc - 0.1))"),
    # colossus
    ("glass='#9ad8ff', face='#ffd8c0', blush='#ff9ab4', **{'*glow': '#8ae8ff', '*glow2': '#ffe68a'}), 3.0)",
     "glass='#9ad8ff', face='#ffd8c0', blush='#ff9ab4', **{'*glow': '#8ae8ff', '*glow2': '#ffe68a'}), 5.23)"),
    ("    grid(B, 'f', 3, 3, mm('belly'), (0.14, 0.14), name='canvas_patch', span=(0.6, 0.6))\n",
     "    grid(B, 'f', 3, 3, mm('belly'), (0.14, 0.14), name='canvas_patch', span=(0.6, 0.6))\n"
     "    grid(B, 'l', 2, 3, mm('belly'), (0.14, 0.14), name='canvas_patch', span=(0.6, 0.6))\n"
     "    grid(B, 'r', 2, 3, mm('belly'), (0.14, 0.14), name='canvas_patch', span=(0.6, 0.6))\n"),
    ("    for k_ in range(6):\n        p('plate_bolt', (0.08, 0.06, 0.08), mm('dark'), ((k_ - 2.5) * 0.18, B.front - 0.06, B.top - 0.08))",
     "    for k_ in range(10):\n        p('plate_bolt', (0.06, 0.06, 0.06), mm('dark'), ((k_ - 4.5) * 0.1, B.front - 0.06, B.top - 0.08))"),
    ("    for k_ in range(4):\n        p('belt_weight', (0.24, 0.12, 0.24), mm('lead'), ((k_ - 1.5) * 0.4, B.front - 0.05, B.c.z - B.s.z * 0.3))",
     "    for k_ in range(6):\n        p('belt_weight', (0.2, 0.12, 0.24), mm('lead'), ((k_ - 2.5) * 0.26, B.front - 0.05, B.c.z - B.s.z * 0.3))"),
    ("    p('tank_valve', (0.2, 0.2, 0.2), mm('accent'), (0, B.back + 0.25, B.c.z + 0.8))\n",
     "    p('tank_valve', (0.2, 0.2, 0.2), mm('accent'), (0, B.back + 0.25, B.c.z + 0.8))\n"
     "    for k_ in range(6):\n        p('tank_rivet', (0.06, 0.06, 0.06), mm('dark'), ((k_ % 3 - 1) * 0.2, B.back + 0.51, B.c.z - 0.2 + (k_ // 3) * 0.6))\n"),
    ("    for j in range(6):\n        ang = math.radians(j * 30)\n        p('hose'", "    for j in range(10):\n        ang = math.radians(j * 18)\n        p('hose'"),
    ("    p('porthole_glass', (0.66, 0.1, 0.56), mm('face'), (0, Hd.front - 0.17, Hd.c.z))\n",
     "    p('porthole_glass', (0.66, 0.1, 0.56), mm('face'), (0, Hd.front - 0.17, Hd.c.z))\n"
     "    for k_ in range(8):\n        ang = math.radians(k_ * 45)\n        p('port_rivet', (0.06, 0.06, 0.06), mm('dark'), (math.cos(ang) * 0.44, Hd.front - 0.2, Hd.c.z + math.sin(ang) * 0.4))\n"
     "    for j in range(2):\n        p('helmet_band', (Hd.s.x + 0.24, Hd.s.y + 0.24, 0.06), mm('accent'), (Hd.c.x, Hd.c.y, Hd.c.z + 0.42 + j * 0.12))\n"),
    ("        p('wrist_ring', (0.5, 0.5, 0.1), mm('brass'), (hx, hy, hz + 0.3))\n",
     "        p('wrist_ring', (0.5, 0.5, 0.1), mm('brass'), (hx, hy, hz + 0.3))\n"
     "        for t in range(3):\n            p('arm_band', (0.48, 0.48, 0.06), mm('belly'), (hx, hy, hz + 0.45 + t * 0.12))\n"
     "        for t in (-1, 1):\n            for q in range(2):\n                p('clamp_tooth', (0.06, 0.08, 0.08), mm('brass'), (hx + t * 0.1, hy - 0.2, hz - 0.4 - q * 0.14))\n"),
    ("        p('knee_pad', (0.5, 0.2, 0.3), mm('brass'), (sgn * 0.42, -0.3, 0.6))\n",
     "        p('knee_pad', (0.5, 0.2, 0.3), mm('brass'), (sgn * 0.42, -0.3, 0.6))\n"
     "        for t in range(3):\n            p('leg_stitch', (0.56, 0.06, 0.04), mm('belly'), (sgn * 0.42, -0.29, 0.25 + t * 0.12))\n"
     "        p('buckle', (0.12, 0.06, 0.12), mm('dark'), (sgn * 0.42, -0.46, 0.3))\n"),
    # octopus
    ("'*glow3': '#ff6ad0'}),\n              3.4, hover=2.6, z0=zc)", "'*glow3': '#ff6ad0'}),\n              4.14, hover=2.6, z0=zc)"),
])
print('ok')
