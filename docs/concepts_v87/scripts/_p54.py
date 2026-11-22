import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [
    ("('citadel_cuttlefish', 'Citadel Cuttlefish', 23, 2, 'water', 2.6, 'fish')", "('citadel_cuttlefish', 'Citadel Cuttlefish', 23, 2, 'water', 1.8, 'fish')"),
])
sub('biome_23.py', [
    ("tip='#e8c8ff', blush='#ff9ab4'), 1.6)", "tip='#e8c8ff', blush='#ff9ab4'), 2.16)"),
    ("        for t in range(3):\n            p('tube_foot', (0.08, 0.08, 0.16), mm('belly'), (sgn * 0.25, (t - 1) * 0.25, 0.08))",
     "        for t in range(5):\n            p('tube_foot', (0.08, 0.08, 0.16), mm('belly'), (sgn * 0.25, (t - 2) * 0.16, 0.08))"),
    ("    a.bx.update(body=B, head=Hd)\n    a.marks = dict(Head=(0, -0.3, zc), Chest=(0, -0.5, zc), Hit=(0, 0, zc + 0.4))\n",
     "    grid(B, 'u', 3, 3, mm('belly'), (0.12, 0.12), name='under_dot', span=(0.6, 0.6))\n"
     "    a.bx.update(body=B, head=Hd)\n    a.marks = dict(Head=(0, -0.3, zc), Chest=(0, -0.5, zc), Hit=(0, 0, zc + 0.4))\n"),
    ("stripe='#8a4a2a', blush='#ff9ab4'),\n              1.4, hover=2.2, z0=zc)", "stripe='#8a4a2a', blush='#ff9ab4'),\n              0.98, hover=2.2, z0=zc)"),
    # clam
    ("    for j in range(5):\n        p('shell_rib', (0.12, 1.44, 0.5), mm('belly'), ((j - 2) * 0.4, 0.2, 0.32))",
     "    for j in range(9):\n        p('shell_rib', (0.1, 1.44, 0.5), mm('belly'), ((j - 4) * 0.22, 0.2, 0.32))\n"
     "    grid(B, 'l', 2, 2, mm('dark'), (0.1, 0.1), name='shell_dot', span=(0.6, 0.5))\n"
     "    grid(B, 'r', 2, 2, mm('dark'), (0.1, 0.1), name='shell_dot', span=(0.6, 0.5))\n"
     "    grid(B, 'k', 4, 1, mm('dark'), (0.1, 0.1), name='shell_dot', span=(0.8, 0.1))\n"
     "    for k_ in range(6):\n        p('barnacle', (0.14, 0.14, 0.1), mm('stone') if False else mm('belly'), (-0.9 + k_ * 0.36, 0.7, 0.62))"),
    ("    for k_ in range(10):\n        p('mantle_frill', (0.18, 0.12, 0.14), mm('accent'), (-0.9 + k_ * 0.2, -0.42, 0.78 + 0.05 * (k_ % 2)))",
     "    for k_ in range(16):\n        p('mantle_frill', (0.12, 0.12, 0.14), mm('accent'), (-0.9 + k_ * 0.12, -0.42, 0.78 + 0.05 * (k_ % 2)))"),
    ("    p('pearl_shine', (0.12, 0.06, 0.12), mm('white'), (-0.12, 0.0, 1.26))\n",
     "    p('pearl_shine', (0.12, 0.06, 0.12), mm('white'), (-0.12, 0.0, 1.26))\n"
     "    for k_ in range(6):\n        ang = math.radians(k_ * 60)\n        p('pearl_cup', (0.14, 0.14, 0.1), mm('accent'), (math.cos(ang) * 0.3, 0.3 + math.sin(ang) * 0.3, 0.86))\n"),
    ("        b('arch', (0.42, 0.3, 0.42), mm('main'), (x, 0.85, z), rot=(0, 45 if i == 3 else 0, 0), bev=0.06)\n",
     "        b('arch', (0.42, 0.3, 0.42), mm('main'), (x, 0.85, z), rot=(0, 45 if i == 3 else 0, 0), bev=0.06)\n"
     "        p('arch_stud', (0.12, 0.08, 0.12), mm('accent'), (x, 0.68, z))\n"),
    ("    p('spire_tip', (0.12, 0.12, 0.2), mm('glass2'), (0, 0.85, 2.96))\n",
     "    p('spire_tip', (0.12, 0.12, 0.2), mm('glass2'), (0, 0.85, 2.96))\n"
     "    for k_ in range(4):\n        p('spire_rib', (0.28, 0.3, 0.05), mm('dark'), (0, 0.85, 2.4 + k_ * 0.14))\n"
     "    for j, (x, z, m_) in enumerate(((-0.25, 0.75, 'glass2'), (0.25, 0.75, 'glass1'), (-0.75, 0.75, 'glass3'), (0.75, 0.75, 'glass1'),\n"
     "                                    (-0.25, 1.85, 'glass1'), (0.25, 1.85, 'glass3'))):\n"
     "        p('glass_small', (0.2, 0.1, 0.22), mm(m_), (x, 0.88, z))\n"),
    ("        p('foot', (0.3, 0.4, 0.1), mm('mantle'), (sgn * 0.6, 0.2, 0.04))\n",
     "        p('foot', (0.3, 0.4, 0.1), mm('mantle'), (sgn * 0.6, 0.2, 0.04))\n"
     "        for t in range(3):\n            p('foot_toe', (0.08, 0.08, 0.06), mm('accent'), (sgn * 0.6 + (t - 1) * 0.1, -0.02, 0.03))\n"),
])
print('ok')
