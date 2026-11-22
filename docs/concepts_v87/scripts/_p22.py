import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_07.py', [
 ("GROUND = '#e8cc86'", "GROUND = '#d6b266'"),
 ("    p('tail_plate', (0.5, 0.1, 0.3), mm('dark'), (0, B.back + 0.03, B.c.z - 0.1))\n",
  "    p('tail_plate', (0.5, 0.1, 0.3), mm('dark'), (0, B.back + 0.03, B.c.z - 0.1))\n"
  "    for sgn, n in LR:\n"
  "        for j in range(2):\n"
  "            p('vein', (0.03, 0.36, 0.03), mm('shine'), (sgn * (0.1 + 0.26 * j), B.c.y + 0.1, B.top + 0.135))\n"
  "            p('belly_stud', (0.12, 0.12, 0.05), mm('accent'), (sgn * 0.2, B.c.y - 0.3 + j * 0.6, B.bot - 0.16))\n"),
 ("    accessory('necklace', Box((0, B.front + 0.3, B.top + 0.02), (B.s.x, B.s.x, 0.2)), '#e8782a', '#5ae8e0', z=B.top - 0.02)\n",
  "    accessory('necklace', Box((0, B.front + 0.3, B.top + 0.02), (B.s.x, B.s.x, 0.2)), '#e8782a', '#5ae8e0', z=B.top - 0.02)\n"
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        for j in range(3):\n"
  "            p('foot_band', (ft.s.x + 0.02, 0.07, ft.s.z + 0.02), mm('accent'), (ft.c.x, ft.c.y - 0.2 + j * 0.24, ft.c.z))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(2):\n"
  "            p('freckle', (0.03, 0.03, 0.03), mm('dark'), (sgn * (0.1 + 0.06 * j), mz.front - 0.008, mz.c.z + 0.02 + 0.04 * j))\n"
  "            on(Hd, 'l' if sgn < 0 else 'r', 0.1, 0.2 - 0.3 * j, (0.24, 0.1), mm('accent'), name='temple')\n"
  "    use('body')\n"),
 ("    use('body')\n    aura_kit(1.5, 4, motes=8, mote_col='glow', height=1.4)",
  "    for arm in a.arms:\n"
  "        sgn = -1 if arm.endswith('L') else 1\n"
  "        use(arm)\n"
  "        for j in range(3):\n"
  "            p('claw_stud', (0.08, 0.08, 0.05), mm('accent'), (sgn * (B.s.x * 0.4 + 0.3 + 0.1 * j), B.front - 0.2 - 0.14 * j, B.c.z + 0.2))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        on(Hd, 't', sgn * 0.26, 0, (0.16, 0.2), mm('shell'), name='head_plate', th=0.05)\n"
  "        p('cheek_stud', (0.08, 0.04, 0.08), mm('accent'), (sgn * 0.36, Hd.front - 0.02, Hd.c.z + 0.16), rot=(0, 45, 0))\n"
  "    use('body')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(4):\n"
  "            p('rim_stud', (0.06, 0.08, 0.08), mm('accent'), (sgn * (B.s.x / 2 + 0.03), B.c.y - 0.5 + j * 0.34, B.c.z + 0.2))\n"
  "    aura_kit(1.5, 4, motes=8, mote_col='glow', height=1.4)"),
 ("        for sgn, n in LR:\n            p('scale', (0.04, 0.24, 0.24), mm('accent'), (sgn * (nb.s.x / 2 + 0.01), nb.c.y, nb.c.z), rot=(12, 0, 0))\n",
  "        for sgn, n in LR:\n            p('scale', (0.04, 0.24, 0.24), mm('accent'), (sgn * (nb.s.x / 2 + 0.01), nb.c.y, nb.c.z), rot=(12, 0, 0))\n"
  "            p('scale', (0.04, 0.16, 0.16), mm('dark'), (sgn * (nb.s.x / 2 + 0.012), nb.c.y + 0.1, nb.c.z - 0.26), rot=(12, 0, 0))\n"
  "            p('scale', (0.04, 0.16, 0.16), mm('belly'), (sgn * (nb.s.x / 2 + 0.012), nb.c.y - 0.1, nb.c.z + 0.28), rot=(12, 0, 0))\n"
  "            cn('side_spike', 0.07, 0.24, mm('horn'), (sgn * (nb.s.x / 2 - 0.02), nb.back - 0.06, nb.c.z + 0.2), (sgn * 1, 0.6, 0.3))\n"),
 ("    for sgn, n in LR:\n        for i in range(3):\n            p('body_scale', (0.04, 0.26, 0.3), mm('accent'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.4 + i * 0.4, B.c.z + 0.05))\n",
  "    for sgn, n in LR:\n        for i in range(3):\n            p('body_scale', (0.04, 0.26, 0.3), mm('accent'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.4 + i * 0.4, B.c.z + 0.05))\n"
  "            cn('body_spike', 0.09, 0.3, mm('horn'), (sgn * 0.4, B.c.y - 0.4 + i * 0.4, B.top - 0.02), (sgn * 0.5, 0.2, 1))\n"
  "    for i in range(4):\n"
  "        b('body_fin', (0.14, 0.26, 0.3), mm('fin'), (0, B.front + 0.24 + i * 0.36, B.top + 0.12), bev=0.04)\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(3):\n"
  "            p('tooth', (0.07, 0.04, 0.08), mm('white'), (sgn * (0.08 + 0.1 * j), mz.front - 0.006, mz.bot + 0.03))\n"
  "        b('barbel', (0.06, 0.06, 0.34), mm('fin'), (sgn * 0.36, mz.front + 0.04, mz.bot - 0.14), rot=(0, sgn * 16, 0), bev=0.02)\n"
  "        p('barbel_tip', (0.1, 0.1, 0.1), mm('glow'), (sgn * 0.41, mz.front + 0.04, mz.bot - 0.34))\n"
  "    use('body')\n"),
 ("        p('tail_band', (0.86 * (0.8 - 0.2 * i) + 0.04, 0.12, 0.86 * (0.8 - 0.2 * i) * 0.9 + 0.04), mm('dark'), (j.x, j.y + 0.45, 0.86 * (0.8 - 0.2 * i) * 0.45))\n",
  "        p('tail_band', (0.86 * (0.8 - 0.2 * i) + 0.04, 0.12, 0.86 * (0.8 - 0.2 * i) * 0.9 + 0.04), mm('dark'), (j.x, j.y + 0.45, 0.86 * (0.8 - 0.2 * i) * 0.45))\n"
  "        p('tail_band', (0.86 * (0.8 - 0.2 * i) + 0.04, 0.08, 0.86 * (0.8 - 0.2 * i) * 0.9 + 0.04), mm('accent'), (j.x, j.y + 0.2, 0.86 * (0.8 - 0.2 * i) * 0.45))\n"
  "        for sgn, n in LR:\n"
  "            p('tail_scale', (0.04, 0.2, 0.2), mm('accent'), (j.x + sgn * (0.43 * (0.8 - 0.2 * i) + 0.01), j.y + 0.62, 0.86 * (0.8 - 0.2 * i) * 0.45))\n"),
 ("**{'*glow': '#5ae8e0', '*glow2': '#ff8ad0', '*gold': '#ffd84a'}), 3.75)", "**{'*glow': '#5ae8e0', '*glow2': '#ff8ad0', '*gold': '#ffd84a'}), 4.6)"),
 ("        p('knee_pad', (ft.s.x + 0.04, ft.s.y * 0.7, 0.12), mm('dark'), (ft.c.x, ft.c.y + 0.05, 0.6))\n",
  "        p('knee_pad', (ft.s.x + 0.04, ft.s.y * 0.7, 0.12), mm('dark'), (ft.c.x, ft.c.y + 0.05, 0.6))\n"
  "        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.06), mm('accent'), (ft.c.x, ft.c.y + 0.05, 0.86))\n"
  "        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.6, 0.05), mm('accent'), (ft.c.x, ft.c.y + 0.05, 0.36))\n"),
 ("    for j in range(4):\n        p('neck_fur', (0.3, 0.14, 0.2), mm('dark'), (0, nk.front - 0.04, nk.c.z + 0.4 - j * 0.26))\n",
  "    for j in range(4):\n        p('neck_fur', (0.3, 0.14, 0.2), mm('dark'), (0, nk.front - 0.04, nk.c.z + 0.4 - j * 0.26))\n"
  "        for sgn, n in LR:\n"
  "            p('neck_patch', (0.04, 0.2, 0.16), mm('accent'), (sgn * (nk.s.x / 2 + 0.01), nk.c.y, nk.c.z + 0.36 - j * 0.24))\n"),
])
print('ok')
