import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_21.py', [
    ("(0.0, 0.5, 4.2, 2.0, cap)", "(0.0, 0.5, 3.8, 1.9, cap)"),
    ("shelf2='#a8c86a', leg='#3a2a20'), 1.4)", "shelf2='#a8c86a', leg='#3a2a20'), 0.94)"),
    ("        p('shelf_rim', (w + 0.34, 0.06, 0.06), mm('accent'), (0.08 * (1 if i % 2 else -1), y - 0.17, 0.6))\n",
     "        p('shelf_rim', (w + 0.34, 0.06, 0.06), mm('accent'), (0.08 * (1 if i % 2 else -1), y - 0.17, 0.6))\n"
     "        p('shelf_dot', (0.1, 0.1, 0.04), mm('belly'), (0.08 * (1 if i % 2 else -1) + 0.15, y, 0.66))\n"),
    ("    p('mouth', (0.14, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 0.18))\n    use('body')\n",
     "    p('mouth', (0.14, 0.03, 0.04), mm('dark'), (0, Hd.front - 0.012, 0.18))\n"
     "    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='head_dot', span=(0.5, 0.5))\n"
     "    for sgn in (-1, 1):\n        p('mandible', (0.06, 0.08, 0.06), mm('dark'), (sgn * 0.1, Hd.front - 0.04, 0.12))\n"
     "    use('body')\n"),
    ("moss='#7aa04a', blush='#ff9ab4'), 1.6)", "moss='#7aa04a', blush='#ff9ab4'), 1.4)"),
    # slug
    ("    for j in range(7):\n        for sgn in (-1, 1):\n            p('mantle_frill', (0.08, 0.26, 0.14), mm('belly'), (sgn * 0.47, -0.5 + j * 0.27, 0.16))",
     "    for j in range(10):\n        for sgn in (-1, 1):\n            p('mantle_frill', (0.08, 0.18, 0.14), mm('belly'), (sgn * 0.47, -0.6 + j * 0.2, 0.16))\n"
     "    for j in range(6):\n        for sgn in (-1, 1):\n            p('back_stripe', (0.04, 0.16, 0.24), mm('dark'), (sgn * 0.41, -0.3 + j * 0.2, 0.56))\n"
     "    for j in range(4):\n        p('tail_ridge', (0.12, 0.16, 0.08), mm('dark'), (0, 1.0 + j * 0.16, 0.42 - j * 0.05))"),
    ("        for k_ in range(4):\n            ang = math.radians(k_ * 90 + 45)\n            p('cap_lamp', (0.12, 0.12, 0.14), mm('lamp'), (math.cos(ang) * s * 0.44, 0.3 + math.sin(ang) * s * 0.44, z - 0.22))\n",
     "        for k_ in range(8):\n            ang = math.radians(k_ * 45 + 22)\n            p('cap_lamp', (0.1, 0.1, 0.14), mm('lamp'), (math.cos(ang) * s * 0.44, 0.3 + math.sin(ang) * s * 0.44, z - 0.22))\n"
     "        grid(Box((0, 0.3, z), (s, s, 0.24)), 't', 2, 2, mm('belly'), (0.1, 0.1), name='cap_spot', span=(0.6, 0.6))\n"),
    ("    grid(Hd, 't', 2, 2, mm('belly'), (0.08, 0.08), name='head_dot', span=(0.5, 0.5))\n    use('body')\n    grid(Box((0, 0.2, 0.55)",
     "    grid(Hd, 't', 2, 2, mm('belly'), (0.08, 0.08), name='head_dot', span=(0.5, 0.5))\n"
     "    grid(Hd, 'l', 2, 2, mm('dark'), (0.07, 0.07), name='cheek_dot', span=(0.5, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('dark'), (0.07, 0.07), name='cheek_dot', span=(0.5, 0.5))\n"
     "    use('body')\n    grid(Box((0, 0.2, 0.55)"),
])
print('ok')
