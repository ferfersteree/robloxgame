import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_09.py', [
 ("accent='#5ac8d8', spot='#c8e85a'), 1.45)", "accent='#5ac8d8', spot='#c8e85a'), 1.6)"),
 ("    for i in range(4):\n        p('belly_band', (B.s.x * 0.7, 0.1, 0.03), mm('belly'), (0, B.front + 0.2 + i * 0.3, B.bot - 0.03))\n",
  "    for i in range(4):\n        p('belly_band', (B.s.x * 0.7, 0.1, 0.03), mm('belly'), (0, B.front + 0.2 + i * 0.3, B.bot - 0.03))\n"
  "    for sgn, n in LR:\n"
  "        for j in range(3):\n"
  "            p('side_stripe', (0.03, 0.3, 0.06), mm('dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.3 + j * 0.3, B.c.z + 0.2))\n"
  "            p('side_dot', (0.03, 0.08, 0.08), mm('accent'), (sgn * (B.s.x / 2 + 0.012), B.c.y - 0.2 + j * 0.3, B.c.z - 0.1))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        p('cheek_spot', (0.08, 0.03, 0.08), mm('spot'), (sgn * 0.2, Hd.front - 0.012, Hd.c.z + 0.06))\n"
  "        p('lid', (0.38, 0.36, 0.06), mm('dark'), (sgn * 0.26, Hd.c.y + 0.1, Hd.top + 0.24))\n"
  "    use('body')\n"),
 ("    use('body')\n    for nm in a.legs:\n        use(nm)\n        j = a.joint[nm]\n        sgn = -1 if nm.endswith('L') else 1\n        p('leg_band', (0.08, 0.13, 0.13), mm('accent'), (j.x + sgn * 0.2, j.y, j.z + 0.04))\n    use('body')\n    return finish(a)",
  "    use('body')\n    for nm in a.legs:\n        use(nm)\n        j = a.joint[nm]\n        sgn = -1 if nm.endswith('L') else 1\n        p('leg_band', (0.08, 0.13, 0.13), mm('accent'), (j.x + sgn * 0.2, j.y, j.z + 0.04))\n"
  "        p('leg_hair', (0.04, 0.04, 0.1), mm('belly'), (j.x + sgn * 0.36, j.y, j.z + 0.1))\n"
  "    use('claw_L')\n"
  "    for j in range(2):\n"
  "        p('small_claw_dot', (0.08, 0.08, 0.04), mm('accent'), (-(B.s.x * 0.4 + 0.2 + 0.1 * j), B.front - 0.2, B.c.z + 0.1))\n"
  "    use('body')\n"
  "    for i in range(4):\n"
  "        p('back_bump', (0.12, 0.12, 0.05), mm('belly'), ((i - 1.5) * 0.26, B.c.y + 0.3, B.top + 0.13))\n"
  "    for sgn, n in LR:\n"
  "        p('under_band', (0.4, 0.06, 0.03), mm('dark'), (sgn * 0.2, B.c.y, B.bot - 0.08))\n"
  "    return finish(a)"),
])
print('ok')
