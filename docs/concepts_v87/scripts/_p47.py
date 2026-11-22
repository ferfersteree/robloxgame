import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_20.py', [
    ("(-0.5, 4.5))", "(-0.5, 4.3))"),
    ("rust='#b8683a', blush='#ff9ab4'), 2.0)", "rust='#b8683a', blush='#ff9ab4'), 2.55)"),
    ("    b('foot', (0.7, 0.8, 0.2), mm('dark'), (0, -0.05, 0.1), bev=0.06)\n",
     "    b('foot', (0.7, 0.8, 0.2), mm('dark'), (0, -0.05, 0.1), bev=0.06)\n"
     "    for sgn in (-1, 1):\n"
     "        for t in (-1, 1):\n"
     "            p('foot_bolt', (0.08, 0.08, 0.06), mm('spring'), (sgn * 0.26, -0.05 + t * 0.3, 0.22))\n"),
    ("leg='#4a3a30', rivet='#e0b84a'), 2.0)", "leg='#4a3a30', rivet='#e0b84a'), 1.55)"),
    ("    p('snout_tip', (0.2, 0.12, 0.14), mm('dark'), (0, Hd.front - 1.05, 0.3))\n",
     "    p('snout_tip', (0.2, 0.12, 0.14), mm('dark'), (0, Hd.front - 1.05, 0.3))\n"
     "    for sgn in (-1, 1):\n"
     "        p('mandible', (0.05, 0.1, 0.06), mm('dark'), (sgn * 0.08, Hd.front - 1.1, 0.24))\n"
     "        p('thorax_spot', (0.04, 0.14, 0.14), mm('accent'), (sgn * 0.41, -0.25, 0.8))\n"),
    # sentinel +55
    ("    grid(B, 'f', 3, 1, mm('rust'), (0.1, 0.1), name='rust_spot', span=(0.6, 0.1), offset=-0.45)\n",
     "    grid(B, 'f', 3, 1, mm('rust'), (0.1, 0.1), name='rust_spot', span=(0.6, 0.1), offset=-0.45)\n"
     "    grid(B, 'k', 3, 3, mm('iron'), (0.14, 0.14), name='back_plate', span=(0.7, 0.7))\n"
     "    for k_ in range(10):\n"
     "        ang = math.radians(k_ * 36 + 18)\n"
     "        p('rim_rivet', (0.08, 0.08, 0.08), mm('rust'), (math.cos(ang) * 0.66, -0.26, zc + math.sin(ang) * 0.66))\n"
     "        ang2 = math.radians(k_ * 36)\n"
     "        p('tooth_cap', (0.2, 0.46, 0.08), mm('belly'), (math.cos(ang2) * (R + 0.16), 0, zc + math.sin(ang2) * (R + 0.16)), rot=(0, -k_ * 36 + 90, 0))\n"
     "    p('emblem', (0.3, 0.05, 0.3), mm('accent'), (0, -0.36, zc), rot=(0, 45, 0))\n"
     "    p('emblem_dot', (0.12, 0.06, 0.12), mm('belly'), (0, -0.38, zc), rot=(0, 45, 0))\n"),
    ("    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='head_rivet', span=(0.6, 0.6), offset=0.2)\n",
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='head_rivet', span=(0.6, 0.6), offset=0.2)\n"
     "    grid(Hd, 'l', 2, 2, mm('dark'), (0.06, 0.06), name='side_rivet', span=(0.6, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('dark'), (0.06, 0.06), name='side_rivet', span=(0.6, 0.5))\n"),
    ("        p('knee', (0.32, 0.32, 0.1), mm('rust'), (sgn * 0.35, 0, LEG / 2 + 0.1))\n",
     "        p('knee', (0.32, 0.32, 0.1), mm('rust'), (sgn * 0.35, 0, LEG / 2 + 0.1))\n"
     "        for t in range(3):\n"
     "            p('leg_bolt', (0.06, 0.04, 0.06), mm('main'), (sgn * 0.35, -0.14, 0.2 + t * 0.16))\n"),
    ("        b('hand', (0.3, 0.3, 0.26), mm('dark'), (sgn * (R + 0.2), 0, zc - 0.48), bev=0.05)\n",
     "        b('hand', (0.3, 0.3, 0.26), mm('dark'), (sgn * (R + 0.2), 0, zc - 0.48), bev=0.05)\n"
     "        b('shoulder', (0.34, 0.34, 0.2), mm('main'), (sgn * (R + 0.2), 0, zc + 0.24), bev=0.05)\n"
     "        for t in range(2):\n"
     "            p('arm_band', (0.24, 0.24, 0.05), mm('rust'), (sgn * (R + 0.2), 0, zc - 0.05 - t * 0.2))\n"),
    ("    p('wrench_grip', (0.2, 0.2, 0.4), mm('rust'), (R + 0.2, -0.1, zc - 0.55))\n",
     "    p('wrench_grip', (0.2, 0.2, 0.4), mm('rust'), (R + 0.2, -0.1, zc - 0.55))\n"
     "    for t in range(4):\n"
     "        p('wrench_rivet', (0.06, 0.18, 0.06), mm('belly'), (R + 0.2, -0.1, zc - 0.2 + t * 0.2))\n"),
])
print('ok')
