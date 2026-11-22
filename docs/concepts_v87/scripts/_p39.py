import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_03.py', [
    ("**{'*glow': '#5affd0', '*glow2': '#ffe14a'}), 1.6)\n    B, Hd = sit(", "**{'*glow': '#5affd0', '*glow2': '#ffe14a'}), 3.14)\n    B, Hd = sit("),
    ("    tail_kit('stub', 'body', (0, a.tail_j[1], 0.3), 'main', 'dark', size=0.24)\n    # rarity 5: glowing mushroom garden",
     "    grid(B, 'l', 4, 4, mm('dark'), (0.12, 0.12), name='fur_tuft', offset=0.06)\n"
     "    grid(B, 'r', 4, 4, mm('dark'), (0.12, 0.12), name='fur_tuft', offset=0.06)\n"
     "    grid(B, 'k', 4, 3, mm('accent'), (0.14, 0.14), name='back_tuft')\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 3, 2, mm('accent'), (0.12, 0.12), name='cheek_tuft')\n"
     "    grid(Hd, 'r', 3, 2, mm('accent'), (0.12, 0.12), name='cheek_tuft')\n"
     "    grid(Hd, 'k', 3, 2, mm('dark'), (0.12, 0.12), name='nape_tuft')\n"
     "    use('body')\n"
     "    for ft in a.bx['feet']:\n"
     "        use(ft.seg)\n"
     "        for j in range(4):\n"
     "            p('claw', (0.08, 0.1, 0.08), mm('accent'), (ft.c.x + (j - 1.5) * 0.08, ft.front - 0.04, 0.08))\n"
     "    use('body')\n"
     "    tail_kit('stub', 'body', (0, a.tail_j[1], 0.3), 'main', 'dark', size=0.24)\n    # rarity 5: glowing mushroom garden"),
])
sub('biome_04.py', [
    ("    grid(B, 't', 3, 3, mm('snow'), (0.16, 0.16), name='snow', th=0.06)\n",
     "    grid(B, 't', 3, 3, mm('snow'), (0.16, 0.16), name='snow', th=0.06)\n"
     "    grid(B, 'l', 4, 2, mm('dark'), (0.12, 0.12), name='fur_ring', offset=0.06)\n"
     "    grid(B, 'r', 4, 2, mm('dark'), (0.12, 0.12), name='fur_ring', offset=0.06)\n"
     "    grid(B, 'k', 3, 3, mm('accent'), (0.14, 0.14), name='rump_fur')\n"
     "    grid(B, 'f', 3, 2, mm('snow'), (0.14, 0.14), name='chest_frost')\n"
     "    use('head')\n"
     "    grid(Hd, 't', 3, 2, mm('snow'), (0.14, 0.14), name='head_snow', th=0.06)\n"
     "    grid(Hd, 'f', 3, 1, mm('accent'), (0.1, 0.1), name='brow_frost', span=(0.6, 0.2), offset=0.0)\n"
     "    use('body')\n"),
])
sub('biome_08.py', [
    ("    a = start(row, dict(main='#f2b84a', belly='#fff4d8', dark='#3a2a22', accent='#d8863a', **{'*glow': '#5aff8a'}), 1.7)",
     "    a = start(row, dict(main='#f2b84a', belly='#fff4d8', dark='#3a2a22', accent='#d8863a', **{'*glow': '#5aff8a'}), 2.24)"),
])
sub('biome_12.py', [
    ("    for i in range(3):\n        cn('back_bump', 0.16, 0.24, mm('fin'), (0, B.c.y - 0.5 + i * 0.5, zc + 0.8), (0, 0.3, 1))\n",
     "    for i in range(3):\n        cn('back_bump', 0.16, 0.24, mm('fin'), (0, B.c.y - 0.5 + i * 0.5, zc + 0.8), (0, 0.3, 1))\n"
     "    grid(B, 't', 3, 4, mm('fin'), (0.16, 0.16), name='back_spot', th=0.05)\n"
     "    grid(B, 'k', 3, 3, mm('dark'), (0.14, 0.14), name='tail_spot')\n"
     "    use('head')\n"
     "    grid(Hd, 't', 3, 1, mm('fin'), (0.16, 0.16), name='head_bump', span=(0.7, 0.2))\n"
     "    grid(Hd, 'l', 2, 2, mm('dark'), (0.12, 0.12), name='head_spot')\n"
     "    grid(Hd, 'r', 2, 2, mm('dark'), (0.12, 0.12), name='head_spot')\n"
     "    use('body')\n"),
])
sub('biome_13.py', [
    ("**{'*glow': '#ff8a2a'}), 2.0)\n    B, Hd = biped(", "**{'*glow': '#ff8a2a'}), 2.65)\n    B, Hd = biped("),
    ("    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)\n    # rarity 4: burning mohawk",
     "    grid(B, 'k', 3, 3, mm('dark'), (0.14, 0.14), name='back_bristle')\n"
     "    grid(B, 'f', 3, 2, mm('belly'), (0.1, 0.1), name='chest_dot', span=(0.6, 0.4))\n"
     "    use('head')\n"
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.12, 0.12), name='head_bristle')\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_wart')\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_wart')\n"
     "    use('body')\n"
     "    for ft in a.bx['feet']:\n"
     "        use(ft.seg)\n"
     "        p('hoof_band', (ft.s.x + 0.04, ft.s.y * 0.8, 0.06), mm('belt'), (ft.c.x, ft.c.y, ft.top + 0.06))\n"
     "    use('body')\n"
     "    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)\n    # rarity 4: burning mohawk"),
])
sub('biome_14.py', [
    ("**{'*glow': '#ff5a1a', '*glow2': '#ffd21a'}), 2.4)", "**{'*glow': '#ff5a1a', '*glow2': '#ffd21a'}), 3.0)"),
    ("    grid(B, 'l', 3, 2, mm('rock'), (0.18, 0.18), name='rock_plate')\n    grid(B, 'r', 3, 2, mm('rock'), (0.18, 0.18), name='rock_plate')\n",
     "    grid(B, 'l', 4, 3, mm('rock'), (0.14, 0.14), name='rock_plate', offset=0.06)\n    grid(B, 'r', 4, 3, mm('rock'), (0.14, 0.14), name='rock_plate', offset=0.06)\n"
     "    grid(B, 'k', 3, 2, mm('rock'), (0.16, 0.16), name='rump_plate')\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('rock'), (0.12, 0.12), name='cheek_plate')\n"
     "    grid(Hd, 'r', 2, 2, mm('rock'), (0.12, 0.12), name='cheek_plate')\n"
     "    use('body')\n"),
])
print('ok')
