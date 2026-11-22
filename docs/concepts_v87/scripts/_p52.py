import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [
    ("('fossil_trilobite', 'Fossil Trilobite', 22, 1, 'ground', 1.4, 'bug')", "('fossil_trilobite', 'Fossil Trilobite', 22, 1, 'ground', 0.9, 'bug')"),
])
sub('biome_22.py', [
    ("leg='#6a5038', blush='#ff9ab4'), 1.4)", "leg='#6a5038', blush='#ff9ab4'), 1.17)"),
    ("    grid(Box((0, 0.8, 0.3), (1.2, 1.6, 0.28)), 't', 2, 4, mm('accent'), (0.08, 0.08), name='fossil_dot', span=(0.7, 0.8), offset=0.12)\n",
     "    grid(Box((0, 0.8, 0.3), (1.2, 1.6, 0.28)), 't', 2, 4, mm('accent'), (0.08, 0.08), name='fossil_dot', span=(0.7, 0.8), offset=0.12)\n"
     "    use('head')\n"
     "    grid(Hd, 't', 4, 1, mm('dark'), (0.08, 0.08), name='head_dot', span=(0.8, 0.1), offset=0.0)\n"
     "    for sgn in (-1, 1):\n        p('cheek_ridge', (0.3, 0.06, 0.06), mm('dark'), (sgn * 0.5, Hd.front - 0.01, 0.4))\n"
     "        p('mouth_hook', (0.04, 0.03, 0.06), mm('dark'), (sgn * 0.09, Hd.front - 0.012, 0.2))\n"
     "    use('body')\n"),
    ("'flower', '#e86a5a')", "'flower', '#e86a5a')"),
    ("frill2='#f4ecd8', horn='#fff8e8',\n                        blush='#ff9ab4'), 4.0)", "frill2='#f4ecd8', horn='#fff8e8',\n                        blush='#ff9ab4'), 2.91)"),
    ("    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.34)\n    a.bx.update(body=B, head=Hd)\n    return finish(a)\n\n\ndef skeletal_colossus",
     "    grid(B, 'k', 3, 2, mm('dark'), (0.12, 0.12), name='rump_scale', span=(0.7, 0.5))\n"
     "    for ft in a.bx['feet']:\n"
     "        use(ft.seg)\n"
     "        p('leg_band', (ft.s.x + 0.04, ft.s.y + 0.04, 0.08), mm('dark'), (ft.c.x, ft.c.y, 0.36))\n"
     "    use('head')\n"
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_scale', span=(0.5, 0.5))\n"
     "    for k_ in range(6):\n"
     "        ang = math.radians(15 + k_ * 30)\n"
     "        p('frill_spot', (0.12, 0.06, 0.12), mm('accent'), (math.cos(ang) * 0.85, FY - 0.13, FZ + math.sin(ang) * 0.68))\n"
     "    use('body')\n"
     "    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.34)\n    a.bx.update(body=B, head=Hd)\n    return finish(a)\n\n\ndef skeletal_colossus"),
])
print('ok')
