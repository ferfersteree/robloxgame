import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_10.py', [
 # yak +24
 ("    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.18)\n    return finish(a)\n\n\ndef thunder_eagle",
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        for j in range(3):\n"
  "            p('leg_hair', (ft.s.x + 0.06, ft.s.y + 0.04, 0.08), mm('main' if j % 2 else 'dark'), (ft.c.x, ft.c.y, 0.24 + j * 0.1))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(3):\n"
  "            p('cheek_hair', (0.1, 0.2, 0.24 - 0.04 * j), mm('main'), (sgn * (Hd.s.x / 2 + 0.04), Hd.front + 0.2 + j * 0.2, Hd.c.z - 0.2))\n"
  "    use('body')\n"
  "    for i in range(6):\n"
  "        p('back_hair', (0.26, 0.2, 0.08), mm('dark' if i % 2 else 'accent'), ((i % 3 - 1) * 0.36, B.c.y + 0.5 + 0.2 * (i // 3), B.top + 0.04))\n"
  "    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.18)\n    return finish(a)\n\n\ndef thunder_eagle"),
 # griffin bigger + details
 ("beak_tip='#e8a020', **{'*glow': '#7ac8ff', '*glow2': '#ffe14a'}), 3.4, hover=5.0, z0=z0)",
  "beak_tip='#e8a020', **{'*glow': '#7ac8ff', '*glow2': '#ffe14a'}), 4.6, hover=5.5, z0=z0)"),
 ("    spots(B, 'lr', 4, mm('accent'), 0.14, seed=3, name='fleck')\n    on(B, 't', 0, 0.2, (0.3, B.s.y * 0.5), mm('accent'), name='back_stripe', th=0.04)\n",
  "    spots(B, 'lr', 4, mm('accent'), 0.14, seed=3, name='fleck')\n    on(B, 't', 0, 0.2, (0.3, B.s.y * 0.5), mm('accent'), name='back_stripe', th=0.04)\n"
  "    stripes(B, 'lr', 4, mm('dark'), 0.08, name='stripe', span=0.8)\n"
  "    stripes(a.bx['rump'], 'lr', 2, mm('dark'), 0.08, name='stripe', span=0.6)\n"
  "    for i in range(3):\n"
  "        for j in range(3):\n"
  "            p('back_feather', (0.28, 0.24, 0.06), mm('head' if (i + j) % 2 else 'accent'), ((i - 1) * 0.3, B.front + 0.16 + j * 0.2, B.top + 0.04))\n"
  "    for i in range(6):\n"
  "        p('chest_feather', (0.2, 0.06, 0.16), mm('accent'), ((i % 3 - 1) * 0.26, B.front - 0.14, B.c.z + 0.1 - 0.2 * (i // 3)))\n"),
 ("    p('tail_glow', (0.16, 0.16, 0.16), mm('glow'), (0, a.tail_j[1] + 0.46, a.tail_j[2] - 0.2), rot=(45, 45, 0))\n    use('body')\n    orbit_kit((0, 0.2, z0), 1.6, 6, 'glow', 'glow2', size=0.13, dz=0.3, shape='cross')",
  "    p('tail_glow', (0.16, 0.16, 0.16), mm('glow'), (0, a.tail_j[1] + 0.46, a.tail_j[2] - 0.2), rot=(45, 45, 0))\n"
  "    for sgn, n in LR:\n"
  "        use('wing_' + n)\n"
  "        for i in range(6):\n"
  "            x = sgn * (1.1 / 2 + 0.2 + i * 0.4)\n"
  "            z = B.top - 0.05 + math.tan(math.radians(24)) * (0.2 + i * 0.4)\n"
  "            b('flight_feather', (0.26, 0.4, 0.1), mm('main' if i % 2 else 'head'), (x, B.c.y + 1.1, z - 0.04), rot=(0, -sgn * 24, 0), bev=0.03)\n"
  "            p('covert', (0.24, 0.2, 0.05), mm('accent'), (x, B.c.y + 0.1, z + 0.08), rot=(0, -sgn * 24, 0))\n"
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        p('leg_feather', (ft.s.x + 0.08, ft.s.y * 0.8, 0.14), mm('head'), (ft.c.x, ft.c.y + 0.04, 0.4))\n"
  "        p('leg_glow', (ft.s.x + 0.06, ft.s.y * 0.8, 0.04), mm('glow'), (ft.c.x, ft.c.y + 0.04, 0.3))\n"
  "    use('body')\n    orbit_kit((0, 0.2, z0), 1.6, 6, 'glow', 'glow2', size=0.13, dz=0.3, shape='cross')"),
 # pterosaur narrower + details
 ("span=3.2, depth=1.3, th=0.14, mat='main', bone='dark', web='belly', n=4, up=16)", "span=2.4, depth=1.3, th=0.14, mat='main', bone='dark', web='belly', n=4, up=16)"),
 ("            ln = 3.2 / 4\n", "            ln = 2.4 / 4\n"),
 ("    p('beak_tip_glow', (0.24, 0.14, 0.2), mm('glow'), (0, bk.front + 0.06, bk.c.z))\n",
  "    p('beak_tip_glow', (0.24, 0.14, 0.2), mm('glow'), (0, bk.front + 0.06, bk.c.z))\n"
  "    for i in range(5):\n"
  "        p('beak_stripe', (0.36, 0.08, 0.05), mm('dark'), (0, Hd.front - 0.2 - i * 0.16, Hd.c.z - 0.02))\n"
  "    for sgn, n in LR:\n"
  "        for j in range(3):\n"
  "            p('cheek_scale', (0.04, 0.14, 0.14), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y - 0.2 + j * 0.2, Hd.c.z))\n"
  "    use('body')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(4):\n"
  "            p('fur', (0.06, 0.22, 0.2), mm('belly'), (sgn * (0.9 / 2 + 0.02), B.c.y - 0.36 + j * 0.24, B.c.z))\n"
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        p('leg_band', (ft.s.x + 0.04, ft.s.y * 0.8, 0.06), mm('dark'), (ft.c.x, ft.c.y + 0.04, 0.2))\n"
  "    use('head')\n"),
])
print('ok')
