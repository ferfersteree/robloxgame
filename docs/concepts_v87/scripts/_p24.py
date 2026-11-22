import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_08.py', [
 ("    spec = ((-2.4, -0.2, 2.4, -38, 0), (-1.4, 0.9, 3.4, -18, 1), (0.0, 1.2, 4.1, 0, 2), (1.4, 0.9, 3.5, 18, 0), (2.4, -0.2, 2.5, 38, 1),",
  "    spec = ((-2.4, -0.2, 2.2, -38, 0), (-1.4, 0.9, 3.1, -18, 1), (0.0, 1.2, 3.6, 0, 2), (1.4, 0.9, 3.2, 18, 0), (2.4, -0.2, 2.3, 38, 1),"),
 ("snout='#4a5a62'), 2.2)", "snout='#4a5a62'), 1.95)"),
 ("leaf='#4fc85a', leaf2='#2f9a44'), 2.35)", "leaf='#4fc85a', leaf2='#2f9a44'), 3.3)"),
 ("**{'*glow': '#5aff8a'}), 2.6)", "**{'*glow': '#5aff8a'}), 2.3)"),
 ("**{'*glow': '#5aff8a', '*glow2': '#ffe14a', '*gold': '#ffd84a'}), 2.45)", "**{'*glow': '#5aff8a', '*glow2': '#ffe14a', '*gold': '#ffd84a'}), 2.75)"),
 # ant
 ("    a.extra_idle.append(leaf_idle)\n    use('body')\n    return finish(a)",
  "    a.extra_idle.append(leaf_idle)\n"
  "    for k_ in range(4):\n"
  "        for sgn, n in LR:\n"
  "            p('leaf_vein', (0.3, 0.12, 0.04), mm('leaf2'), (sgn * 0.26, Hd.front - 0.31 + 0.1 * k_, Hd.top + 0.42 + k_ * 0.4), rot=(12, sgn * 25, 0))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(3):\n"
  "            p('head_plate', (0.16, 0.16, 0.04), mm('belly'), (sgn * 0.24, Hd.c.y - 0.2 + j * 0.2, Hd.top + 0.02))\n"
  "        p('jaw_tooth', (0.06, 0.08, 0.06), mm('accent'), (sgn * 0.14, Hd.front - 0.28, Hd.bot + 0.1))\n"
  "    use('body')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(5):\n"
  "            p('abdomen_stud', (0.05, 0.12, 0.12), mm('accent'), (sgn * 0.46, B.back + 0.34 + j * 0.18, B.c.z + 0.2 - 0.06 * (j % 2)), rot=(45, 0, 0))\n"
  "        for j in range(3):\n"
  "            p('abdomen_hair', (0.05, 0.05, 0.12), mm('dark'), (sgn * 0.2, B.back + 0.5 + j * 0.26, B.c.z + 0.46))\n"
  "            p('thorax_stud', (0.1, 0.1, 0.05), mm('accent'), (sgn * 0.16, B.c.y - 0.2 + j * 0.2, B.top + 0.2))\n"
  "    for nm in a.legs:\n"
  "        use(nm)\n"
  "        j = a.joint[nm]\n"
  "        sgn = -1 if nm.endswith('L') else 1\n"
  "        p('leg_band', (0.08, 0.14, 0.14), mm('accent'), (j.x + sgn * 0.2, j.y, j.z + 0.04))\n"
  "    use('body')\n"
  "    return finish(a)"),
 # gorilla
 ("    # leaf skirt (accessory) and vine sash\n",
  "    for i in range(4):\n"
  "        for j in range(3):\n"
  "            p('back_fur', (0.26, 0.1, 0.2), mm('dark'), ((i - 1.5) * 0.34, B.back + 0.08, B.c.z + 0.34 - j * 0.26 + 0.06 * (i % 2)))\n"
  "    for i in range(6):\n"
  "        p('chest_hair', (0.14, 0.06, 0.14), mm('dark'), ((i - 2.5) * 0.16, B.front - 0.11, B.c.z + 0.46 - 0.05 * (i % 2)))\n"
  "    use('head')\n"
  "    for i in range(4):\n"
  "        p('head_fur', (0.2, 0.14, 0.2), mm('dark'), ((i - 1.5) * 0.26, Hd.back + 0.04, Hd.c.z + 0.1 * (i % 2)))\n"
  "        p('head_fur', (0.22, 0.2, 0.12), mm('dark'), ((i - 1.5) * 0.24, Hd.c.y + 0.2, Hd.top + 0.04))\n"
  "    for hb_ in a.bx['hands']:\n"
  "        use(hb_.seg)\n"
  "        sgn = 1 if hb_.c.x > 0 else -1\n"
  "        for j in range(4):\n"
  "            p('arm_fur_b', (0.3, 0.14, 0.2), mm('main' if j % 2 else 'dark'), (hb_.c.x, 0.32, hb_.c.z + 0.3 + j * 0.24))\n"
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        for j in range(4):\n"
  "            p('leg_fur', (0.14, 0.2, 0.14), mm('dark' if j % 2 else 'main'), (ft.c.x + (0.26 if ft.c.x > 0 else -0.26), ft.c.y + 0.2, 0.2 + j * 0.08))\n"
  "        p('toe_big', (0.14, 0.12, 0.1), mm('dark'), (ft.c.x - (0.2 if ft.c.x > 0 else -0.2), ft.front + 0.1, 0.06))\n"
  "    use('body')\n"
  "    # leaf skirt (accessory) and vine sash\n"),
 # frog
 ("    spots(B, 't', 5, mm('dark'), 0.16, seed=4, name='spot')\n",
  "    spots(B, 't', 5, mm('dark'), 0.16, seed=4, name='spot')\n"
  "    for i in range(4):\n"
  "        for j in range(2):\n"
  "            p('wart', (0.1, 0.1, 0.06), mm('dark' if (i + j) % 2 else 'belly'), ((i - 1.5) * 0.26, B.c.y + 0.1 + j * 0.3, B.top + 0.03))\n"
  "        p('belly_line', (0.5 - 0.08 * i, 0.04, 0.04), mm('accent'), (0, B.front - 0.08, B.c.z + 0.1 - i * 0.12))\n"
  "    use('head')\n"
  "    for i in range(5):\n"
  "        p('head_wart', (0.1, 0.1, 0.05), mm('dark'), ((i - 2) * 0.24, Hd.c.y + 0.2 + 0.1 * (i % 2), Hd.top + 0.03))\n"
  "        p('lip_dot', (0.06, 0.04, 0.05), mm('belly'), ((i - 2) * 0.22, Hd.front - 0.012, Hd.c.z - 0.28))\n"
  "    for sgn, n in LR:\n"
  "        p('eyelid', (0.58, 0.52, 0.08), mm('dark'), (sgn * 0.42, Hd.front + 0.3, Hd.top + 0.42))\n"
  "        p('tympanum', (0.05, 0.2, 0.2), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y + 0.1, Hd.c.z))\n"
  "        p('tympanum_in', (0.06, 0.1, 0.1), mm('accent'), (sgn * (Hd.s.x / 2 + 0.012), Hd.c.y + 0.1, Hd.c.z))\n"
  "    use('body')\n"
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        for j in range(3):\n"
  "            p('leg_band', (ft.s.x + 0.02, 0.08, ft.s.z + 0.02), mm('dark'), (ft.c.x, ft.c.y - 0.1 + j * 0.2, ft.c.z))\n"
  "        p('web', (ft.s.x + 0.14, 0.2, 0.04), mm('blue'), (ft.c.x, ft.front + 0.06, 0.03))\n"
  "    for arm in a.arms:\n"
  "        sgn = -1 if arm.endswith('L') else 1\n"
  "        use(arm)\n"
  "        for j in range(2):\n"
  "            p('arm_band', (0.26, 0.26, 0.05), mm('dark'), (sgn * (B.s.x / 2 - 0.19), 0.12 - B.s.y / 2 + 0.04, 0.2 + B.s.z * 0.42 - 0.08 - j * 0.12))\n"
  "    use('body')\n"),
])
print('ok')
