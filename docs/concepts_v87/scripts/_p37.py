import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_16.py', [
    ("(0, 0.3, 5.6, 3.0, 1.2), (-1.2, 0.5, 3.0, 2.2, 2.1), (1.3, 0.5, 2.6, 2.0, 1.7), (-0.1, 0.8, 1.6, 1.2, 2.8)",
     "(0, 0.3, 5.6, 3.0, 1.4), (-1.2, 0.5, 3.0, 2.2, 2.5), (1.3, 0.5, 2.6, 2.0, 2.1), (-0.1, 0.8, 1.6, 1.2, 3.4)"),
    ("    grid(a.bx['rump'], 'k', 3, 2, mm('accent'), (0.12, 0.12), name='rump_fleck')\n",
     "    grid(a.bx['rump'], 'k', 3, 2, mm('accent'), (0.12, 0.12), name='rump_fleck')\n"
     "    grid(a.bx['rump'], 't', 2, 2, mm('accent'), (0.12, 0.12), name='rump_fleck')\n"),
    # muskox +80
    ("    grid(B, 't', 3, 2, mm('accent'), (0.16, 0.16), name='frost', span=(0.8, 0.4))\n",
     "    grid(B, 't', 3, 2, mm('accent'), (0.16, 0.16), name='frost', span=(0.8, 0.4))\n"
     "    grid(B, 'l', 4, 3, mm('dark'), (0.14, 0.14), name='shag', th=0.1, offset=0.06)\n"
     "    grid(B, 'r', 4, 3, mm('dark'), (0.14, 0.14), name='shag', th=0.1, offset=0.06)\n"
     "    grid(B, 'k', 4, 3, mm('dark'), (0.16, 0.14), name='rump_shag', th=0.08)\n"
     "    grid(hp, 't', 3, 2, mm('snow'), (0.16, 0.16), name='snow_lump', th=0.22)\n"
     "    for sgn, n in LR:\n"
     "        for j in range(4):\n"
     "            b('skirt_b', (0.1, 0.22, 0.5), mm('accent'), (sgn * (B.s.x / 2 + 0.14), B.front + 0.26 + j * 0.36, B.bot - 0.02), bev=0.03)\n"
     "    for ft in a.bx['feet']:\n"
     "        use(ft.seg)\n"
     "        for j in range(3):\n"
     "            p('leg_hair', (ft.s.x + 0.08, ft.s.y + 0.06, 0.08), mm('main' if j % 2 else 'dark'), (ft.c.x, ft.c.y, 0.2 + j * 0.1))\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('main'), (0.14, 0.14), name='cheek_shag')\n"
     "    grid(Hd, 'r', 2, 2, mm('main'), (0.14, 0.14), name='cheek_shag')\n"
     "    for sgn, n in LR:\n"
     "        for j in range(2):\n"
     "            p('horn_ring', (0.22, 0.26, 0.05), mm('accent'), (sgn * (Hd.s.x / 2 + 0.06), Hd.c.y - 0.06, Hd.c.z - 0.04 + j * 0.2))\n"
     "    use('body')\n"),
    # bear +22
    ("    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.28)\n    # rarity 6: aurora ribbons",
     "    grid(B, 'k', 3, 2, mm('accent'), (0.16, 0.16), name='rump_frost')\n"
     "    use('head')\n"
     "    grid(Hd, 't', 3, 2, mm('accent'), (0.14, 0.14), name='head_frost', span=(0.7, 0.5))\n"
     "    use('body')\n"
     "    for ft in a.bx['feet']:\n"
     "        use(ft.seg)\n"
     "        p('leg_frost', (ft.s.x + 0.04, ft.s.y * 0.8, 0.1), mm('accent'), (ft.c.x, ft.c.y + 0.04, 0.36))\n"
     "        p('leg_glow', (ft.s.x + 0.05, ft.s.y * 0.8, 0.04), mm('glow3'), (ft.c.x, ft.c.y + 0.04, 0.44))\n"
     "    use('body')\n"
     "    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.28)\n    # rarity 6: aurora ribbons"),
])
print('ok')
