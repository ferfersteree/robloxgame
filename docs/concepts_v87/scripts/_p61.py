import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_07.py', [
    ("    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='fore_mark', span=(0.4, 0.4))\n    use('body')\n    sg('tail', 'body', (0.2, 0.6, 0.25))",
     "    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='fore_mark', span=(0.4, 0.4))\n"
     "    for sgn in (-1, 1):\n        for j in range(2):\n            p('whisker', (0.24, 0.02, 0.02), mm('dark'), (sgn * 0.3, Hd.front - 0.12, 1.22 + j * 0.05))\n"
     "    use('body')\n    sg('tail', 'body', (0.2, 0.6, 0.25))"),
    ("ear_in='#ffb8b0'), 2.6)\n    LEG = 0.9", "ear_in='#ffb8b0'), 3.04)\n    LEG = 0.9"),
    ("    grid(B, 't', 2, 2, mm('dark'), (0.08, 0.08), name='top_dot', span=(0.5, 0.5))\n",
     "    grid(B, 't', 2, 2, mm('dark'), (0.08, 0.08), name='top_dot', span=(0.5, 0.5))\n"
     "    grid(B, 'u', 3, 3, mm('belly'), (0.08, 0.08), name='under_fur', span=(0.6, 0.6))\n"
     "    for k_ in range(8):\n        ang = math.radians(k_ * 45)\n        p('fur_tuft', (0.1, 0.1, 0.1), mm('belly'), (math.cos(ang) * 0.42, 0.1 + math.sin(ang) * 0.42, zb - 0.2))\n"),
    ("        p('ankle', (0.1, 0.1, 0.1), mm('accent'), (sgn * 0.3, 0.2, 0.5))\n",
     "        p('ankle', (0.1, 0.1, 0.1), mm('accent'), (sgn * 0.3, 0.2, 0.5))\n"
     "        for j in range(4):\n            p('leg_band', (0.1, 0.1, 0.04), mm('accent' if j % 2 else 'dark'), (sgn * 0.3, 0.2, 0.2 + j * 0.16))\n"),
])
sub('biome_15.py', [
    ("'*glow': '#d8a8ff', '*glow2': '#ff9ae8'}), 2.8)", "'*glow': '#d8a8ff', '*glow2': '#ff9ae8'}), 3.16)"),
    ("    grid(B, 't', 2, 3, mm('accent'), (0.08, 0.08), name='back_gem', span=(0.5, 0.7), rot=(0, 0, 45))\n",
     "    grid(B, 't', 2, 3, mm('accent'), (0.08, 0.08), name='back_gem', span=(0.5, 0.7), rot=(0, 0, 45))\n"
     "    grid(B, 'l', 3, 2, mm('belly'), (0.08, 0.08), name='side_fleck', span=(0.7, 0.5))\n"
     "    grid(B, 'r', 3, 2, mm('belly'), (0.08, 0.08), name='side_fleck', span=(0.7, 0.5))\n"
     "    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('crystal_sock', (ft.s.x + 0.03, ft.s.y + 0.03, 0.08), mm('crystal'), (ft.c.x, ft.c.y, ft.top + 0.04))\n"
     "    use('head')\n    grid(Hd, 't', 2, 2, mm('accent'), (0.06, 0.06), name='head_gem', span=(0.4, 0.4))\n    use('body')\n"),
])
sub('biome_11.py', [
    ("water='#a8e0ff'), 2.4, hover=2.2, z0=zc)", "water='#a8e0ff'), 2.12, hover=2.2, z0=zc)"),
    ("    grid(B, 't', 3, 3, mm('wing'), (0.08, 0.08), name='back_feather', span=(0.5, 0.6))\n",
     "    grid(B, 't', 3, 3, mm('wing'), (0.08, 0.08), name='back_feather', span=(0.5, 0.6))\n"
     "    grid(B, 'l', 4, 2, mm('belly'), (0.08, 0.08), name='side_feather', span=(0.8, 0.5))\n"
     "    grid(B, 'r', 4, 2, mm('belly'), (0.08, 0.08), name='side_feather', span=(0.8, 0.5))\n"
     "    grid(B, 'f', 3, 2, mm('belly'), (0.08, 0.08), name='chest_feather', span=(0.6, 0.5))\n"
     "    for j in range(6):\n        p('beak_line', (0.31, 0.12, 0.03), mm('pouch'), (0, Hd.front - 0.1 - j * 0.18, zc + 0.98))\n"
     "    for j in range(5):\n        p('pouch_fold', (0.42, 0.06, 0.4), mm('accent'), (0, Hd.front - 0.2 - j * 0.16, zc + 0.56))\n"
     "    use('head')\n    grid(Hd, 't', 2, 2, mm('wing'), (0.06, 0.06), name='head_feather', span=(0.4, 0.4))\n    use('body')\n"),
])
sub('biome_16.py', [
    ("leaf='#7ab8a8'),\n              2.2, hover=2.4, z0=zc)", "leaf='#7ab8a8'),\n              1.97, hover=2.4, z0=zc)"),
    ("    grid(B, 'k', 3, 3, mm('dark'), (0.08, 0.08), name='back_spot', span=(0.6, 0.6))\n",
     "    grid(B, 'k', 3, 3, mm('dark'), (0.08, 0.08), name='back_spot', span=(0.6, 0.6))\n"
     "    grid(B, 'l', 3, 3, mm('belly'), (0.08, 0.08), name='side_spot', span=(0.6, 0.6))\n"
     "    grid(B, 'r', 3, 3, mm('belly'), (0.08, 0.08), name='side_spot', span=(0.6, 0.6))\n"
     "    grid(B, 't', 3, 3, mm('dark'), (0.08, 0.08), name='crown_spot', span=(0.5, 0.5))\n"
     "    grid(B, 'u', 2, 2, mm('belly'), (0.1, 0.1), name='under_fluff', span=(0.5, 0.5))\n"
     "    for k_ in range(10):\n        ang = math.radians(k_ * 36)\n        p('disc_rim', (0.1, 0.06, 0.1), mm('main'), (math.cos(ang) * 0.5, -0.6, zc + 0.36 + math.sin(ang) * 0.36))\n"),
])
sub('biome_06.py', [
    ("'*glow': '#ffd84a', '*glow2': '#ff8a3a'}), 2.6, hover=2.0, z0=zc)", "'*glow': '#ffd84a', '*glow2': '#ff8a3a'}), 2.3, hover=2.0, z0=zc)"),
    ("    grid(B, 'k', 3, 4, mm('belly'), (0.1, 0.1), name='back_feather', span=(0.6, 0.7))\n",
     "    grid(B, 'k', 3, 4, mm('belly'), (0.1, 0.1), name='back_feather', span=(0.6, 0.7))\n"
     "    grid(B, 'f', 3, 3, mm('belly'), (0.1, 0.1), name='chest_feather', span=(0.6, 0.6))\n"
     "    grid(B, 't', 3, 3, mm('belly'), (0.1, 0.1), name='shoulder_feather', span=(0.6, 0.6))\n"
     "    for sgn in (-1, 1):\n        for j in range(6):\n            p('cloak_edge', (0.27, 0.12, 0.12), mm('dark'), (sgn * 0.72, -0.15 + j * 0.25, zc - 0.55 + j * 0.02))\n"),
    ("    b('rock_top', (1.1, 1.0, 0.24), mm('rock2'), (0, 0.4, zc - 0.62), bev=0.06)\n",
     "    b('rock_top', (1.1, 1.0, 0.24), mm('rock2'), (0, 0.4, zc - 0.62), bev=0.06)\n"
     "    grid(Box((0, 0.4, zc - 1.0), (1.6, 1.4, 0.6)), 'l', 3, 2, mm('rock2'), (0.14, 0.14), name='rock_crack', span=(0.8, 0.6))\n"
     "    grid(Box((0, 0.4, zc - 1.0), (1.6, 1.4, 0.6)), 'r', 3, 2, mm('rock2'), (0.14, 0.14), name='rock_crack', span=(0.8, 0.6))\n"
     "    for j in range(5):\n        p('pebble', (0.14, 0.14, 0.1), mm('rock2'), (-0.6 + j * 0.3, -0.35, zc - 1.25))\n"),
])
print('ok')
