import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_11.py', [
 ("shell='#f2e6ff', shell2='#a88ae8'), 1.75)", "shell='#f2e6ff', shell2='#a88ae8'), 2.4)"),
 ("**{'*glow': '#5ae8ff', '*glow2': '#ffd21a', '*gold': '#ffd84a'}), 1.25)", "**{'*glow': '#5ae8ff', '*glow2': '#ffd21a', '*gold': '#ffd84a'}), 2.0)"),
 # pelican +10
 ("            b('primary', (0.22, 0.44, 0.1), mm('dark'), (x, 0.84 - 0.05 * i, wb.c.z - 0.03), bev=0.03)\n    use('body')\n    return finish(a)",
  "            b('primary', (0.22, 0.44, 0.1), mm('dark'), (x, 0.84 - 0.05 * i, wb.c.z - 0.03), bev=0.03)\n"
  "    for sgn, n in LR:\n"
  "        use('leg_' + n)\n"
  "        p('web', (0.4, 0.3, 0.04), mm('leg'), (sgn * 1.1 * 0.24, -0.1, 0.03))\n"
  "    use('body')\n"
  "    for i in range(6):\n"
  "        p('chest_feather', (0.2, 0.06, 0.14), mm('main'), ((i % 3 - 1) * 0.28, B.front - 0.14, B.c.z + 0.2 - 0.2 * (i // 3)))\n"
  "    return finish(a)"),
 # sea lion +28
 ("    spots(B, 'lr', 4, mm('dark'), 0.14, seed=3, name='spot')\n    tail_kit('stub', 'body', (0, a.tail_j[1], 0.3), 'dark', 'dark', size=0.18)\n",
  "    spots(B, 'lr', 4, mm('dark'), 0.14, seed=3, name='spot')\n"
  "    spots(B, 'k', 4, mm('dark'), 0.14, seed=5, name='spot')\n"
  "    for i in range(5):\n"
  "        p('neck_fold', (B.s.x * 0.9 - 0.06 * i, 0.06, 0.05), mm('belly'), (0, B.front - 0.06, B.top - 0.1 - i * 0.2))\n"
  "    for arm in a.arms:\n"
  "        sgn = -1 if arm.endswith('L') else 1\n"
  "        use(arm)\n"
  "        for j in range(3):\n"
  "            p('flipper_line', (0.22, 0.06, 0.06), mm('belly'), (sgn * (0.9 / 2 + 0.04), 0.12 - 0.5 + 0.0, 0.3 + j * 0.12), rot=(0, sgn * 20, 0))\n"
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        sgn = 1 if ft.c.x > 0 else -1\n"
  "        b('hind_flipper', (0.36, 0.5, 0.08), mm('dark'), (ft.c.x + sgn * 0.12, ft.c.y + 0.3, 0.05), rot=(0, 0, sgn * 30), bev=0.03)\n"
  "        for j in range(3):\n"
  "            p('hind_line', (0.06, 0.4, 0.05), mm('belly'), (ft.c.x + sgn * (0.04 + j * 0.1), ft.c.y + 0.3, 0.1), rot=(0, 0, sgn * 30))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(3):\n"
  "            p('whisker_dot', (0.03, 0.03, 0.03), mm('dark'), (sgn * (0.08 + 0.06 * j), mz.front - 0.008, mz.c.z - 0.02))\n"
  "    use('body')\n"
  "    tail_kit('stub', 'body', (0, a.tail_j[1], 0.3), 'dark', 'dark', size=0.18)\n"),
 # wyvern +45
 ("    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('leg_fin', (0.06, 0.24, 0.22), mm('accent'), (ft.c.x + (0.2 if ft.c.x > 0 else -0.2), ft.c.y + 0.14, 0.34))\n    use('body')\n    tail_kit('long', 'body', a.tail_j, 'main', 'accent', n=3, size=0.2, dark='dark')\n",
  "    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('leg_fin', (0.06, 0.24, 0.22), mm('accent'), (ft.c.x + (0.2 if ft.c.x > 0 else -0.2), ft.c.y + 0.14, 0.34))\n"
  "        for j in range(2):\n"
  "            p('leg_scale', (ft.s.x + 0.02, 0.08, 0.1), mm('dark'), (ft.c.x, ft.front + 0.06, 0.24 + j * 0.14))\n"
  "    use('body')\n"
  "    for i in range(4):\n"
  "        for sgn, n in LR:\n"
  "            p('belly_scale', (0.24, 0.24, 0.04), mm('belly'), (sgn * 0.15, B.front + 0.24 + i * 0.3, B.bot - 0.05))\n"
  "            cn('side_coral', 0.06, 0.2, mm('coral'), (sgn * (B.s.x / 2 - 0.02), B.front + 0.3 + i * 0.3, B.top - 0.1), (sgn * 1, 0.2, 0.6))\n"
  "    for i in range(4):\n"
  "        p('neck_scale', (0.3, 0.05, 0.16), mm('belly'), (0, B.front - 0.06, B.top + 0.3 + i * 0.16))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(3):\n"
  "            p('cheek_scale', (0.04, 0.16, 0.16), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y - 0.2 + j * 0.2, Hd.c.z - 0.1))\n"
  "    use('body')\n"
  "    tail_kit('long', 'body', a.tail_j, 'main', 'accent', n=3, size=0.2, dark='dark')\n"
  "    for i, t in enumerate(a.tail):\n"
  "        use(t)\n"
  "        b('tail_fin', (0.1, 0.3, 0.3 - 0.06 * i), mm('accent'), (0, a.tail_j[1] + 0.3 + i * 0.42, a.tail_j[2] + 0.2 + i * 0.05), bev=0.03)\n"
  "    use('body')\n"),
 # horseshoe +50
 ("    sg('tail', 'body', (0, B.back + 0.6, B.c.z))\n",
  "    for i in range(4):\n"
  "        for j in range(2):\n"
  "            p('dome_dot', (0.12, 0.12, 0.05), mm('accent'), ((i - 1.5) * 0.38, B.c.y - 0.6 + j * 0.9, B.top + 0.33))\n"
  "    for sgn, n in LR:\n"
  "        for j in range(4):\n"
  "            p('rim_plate', (0.1, 0.2, 0.12), mm('dark'), (sgn * 1.32, B.c.y - 0.5 + j * 0.26, B.top - 0.04))\n"
  "        for j in range(3):\n"
  "            p('rear_band', (0.3, 0.08, 0.05), mm('dark'), (sgn * 0.26, B.back + 0.14 + j * 0.18, B.c.z + 0.23))\n"
  "    for i in range(5):\n"
  "        p('front_rim', (0.36, 0.1, 0.12), mm('dark'), ((i - 2) * 0.4, B.c.y - 0.76, B.top + 0.04))\n"
  "    for i in range(4):\n"
  "        p('under_gill', (0.6, 0.12, 0.04), mm('belly'), (0, B.c.y + 0.1 + i * 0.16, B.bot - 0.06))\n"
  "    sg('tail', 'body', (0, B.back + 0.6, B.c.z))\n"),
])
print('ok')
