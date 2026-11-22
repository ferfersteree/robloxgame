import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_02.py', [
 ("accent='#ffffff', horn='#e9d8b0'), 3.0)", "accent='#ffffff', horn='#e9d8b0'), 2.8)"),
 ("snout='#f0a0a8'), 2.25)", "snout='#f0a0a8'), 1.95)"),
 ("light='#b6bcc8'), 1.72)", "light='#b6bcc8'), 1.5)"),
 ("accent='#c9d3ea'), 2.75)", "accent='#c9d3ea'), 2.6)"),
 ("**{'*glow': '#c8ff5a', '*glow2': '#ffe14a'}), 2.55)", "**{'*glow': '#c8ff5a', '*glow2': '#ffe14a'}), 2.3)"),
 ("tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.2)", "tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)"),
 ("'main', 'accent', size=0.17)\n    p('tail_band', (0.36, 0.1, 0.3), mm('dark'), (0, a.tail_j[1] + 0.3, a.tail_j[2] - 0.1))",
  "'main', 'accent', size=0.11)\n    p('tail_band', (0.24, 0.08, 0.2), mm('dark'), (0, a.tail_j[1] + 0.2, a.tail_j[2] - 0.1))"),
 ("(3.4, 2.2, 1.7), (4.05, 1.4, 1.2))", "(3.35, 2.2, 1.7), (3.9, 1.4, 1.2))"),
 ("    part('small', (0, 0.2, 4.5), 'top')\n    cn('top', 0.3, 0.6, pine3, (0, 0.2, 4.5), n=4)", "    part('small', (0, 0.2, 4.3), 'top')\n    cn('top', 0.3, 0.5, pine3, (0, 0.2, 4.35), n=4)"),
 ("        p('saber_ring', (0.16, 0.16, 0.04), mm('glow'), (sgn * 0.2, mz.front + 0.08, mz.bot - 0.02))\n",
  "        p('saber_ring', (0.16, 0.16, 0.04), mm('glow'), (sgn * 0.2, mz.front + 0.08, mz.bot - 0.02))\n        on(Hd, 'f', sgn * 0.4, -0.32, (0.08, 0.08), mm('glow2'), th=0.035, name='cheek_star', rot=(0, 45, 0))\n"
  "    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('paw_glow', (ft.s.x + 0.03, ft.s.y * 0.5, 0.05), mm('glow'), (ft.c.x, ft.c.y + 0.1, ft.top + 0.06))\n"
  "    use('tail')\n    p('tail_glow', (0.24, 0.1, 0.24), mm('glow2'), (0, a.tail_j[1] + 0.25, a.tail_j[2]))\n    use('tail2')\n    p('tail_glow', (0.2, 0.1, 0.2), mm('glow'), (0, a.tail_j[1] + 0.7, a.tail_j[2] + 0.05))\n"),
])
print('ok')
