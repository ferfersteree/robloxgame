import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_15.py', [
    # moth +28
    ("    tail_kit('stub', 'body', (0, 1.1, zc - 0.05), 'main', 'accent', size=0.12)\n",
     "    tail_kit('stub', 'body', (0, 1.1, zc - 0.05), 'main', 'accent', size=0.12)\n"
     "    use('body')\n"
     "    grid(B, 'l', 3, 2, mm('belly'), (0.1, 0.1), name='fur_tuft')\n"
     "    grid(B, 'r', 3, 2, mm('belly'), (0.1, 0.1), name='fur_tuft')\n"
     "    grid(B, 't', 2, 3, mm('accent'), (0.1, 0.1), name='back_dot')\n"
     "    use('head')\n"
     "    grid(Hd, 't', 2, 2, mm('belly'), (0.12, 0.12), name='head_fluff')\n"
     "    for sgn, n in LR:\n"
     "        use('wing_' + n)\n"
     "        for j in range(4):\n"
     "            p('wing_vein', (0.04, 0.5, 0.09), mm('dark'), (sgn * (B.s.x / 2 + 0.2 + j * 0.22), B.c.y - 0.2, zc + 0.3), rot=(0, -sgn * 20, sgn * 20))\n"
     "    use('body')\n"),
    # bat +12
    ("    cn('back_crystal', 0.1, 0.4, mm('crystal'), (0, 0.3, B.top - 0.02), (0, 0.3, 1))\n",
     "    cn('back_crystal', 0.1, 0.4, mm('crystal'), (0, 0.3, B.top - 0.02), (0, 0.3, 1))\n"
     "    grid(B, 'k', 3, 2, mm('dark'), (0.12, 0.12), name='back_fur')\n"
     "    use('head')\n"
     "    grid(Hd, 't', 3, 2, mm('dark'), (0.1, 0.1), name='head_fur')\n"
     "    use('body')\n"),
    # mole +24
    ("    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.14)\n    return finish(a)\n\n\ndef amethyst_fox",
     "    grid(B, 't', 3, 2, mm('dark'), (0.12, 0.12), name='back_fleck', span=(0.8, 0.4))\n"
     "    grid(a.bx['rump'], 'k', 3, 2, mm('belly'), (0.12, 0.12), name='rump_fleck')\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='head_fleck')\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='head_fleck')\n"
     "    for sgn, n in LR:\n"
     "        p('hat_rivet', (0.06, 0.06, 0.06), mm('dark'), (sgn * 0.3, Hd.c.y - 0.36, Hd.top + 0.1))\n"
     "    use('body')\n"
     "    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.14)\n    return finish(a)\n\n\ndef amethyst_fox"),
    # fox +8
    ("    tail_kit('bushy', 'body', a.tail_j, 'main', 'belly', size=0.22, dark='dark')\n    # rarity 4: glowing crystal tail tip",
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('dark'), (0.1, 0.1), name='temple_facet', rot=(45, 0, 0))\n"
     "    grid(Hd, 'r', 2, 2, mm('dark'), (0.1, 0.1), name='temple_facet', rot=(45, 0, 0))\n"
     "    use('body')\n"
     "    tail_kit('bushy', 'body', a.tail_j, 'main', 'belly', size=0.22, dark='dark')\n    # rarity 4: glowing crystal tail tip"),
    # anemone
    ("**{'*glow': '#c88aff', '*glow2': '#7ae8ff'}), 2.6)", "**{'*glow': '#c88aff', '*glow2': '#7ae8ff'}), 3.3)"),
    ("    for i in range(8):\n        ang = math.radians(i * 45 + 22.5)\n        x, y = math.cos(ang) * 0.6, 0.1 + math.sin(ang) * 0.5\n",
     "    for i in range(12):\n        ang = math.radians(i * 30 + 15)\n        x, y = math.cos(ang) * 0.6, 0.1 + math.sin(ang) * 0.5\n"),
    ("        p('tentacle_ring', (0.24, 0.24, 0.06), mm('accent'), (x * 1.05, y + (y - 0.1) * 0.05, 1.3))\n",
     "        p('tentacle_ring', (0.24, 0.24, 0.06), mm('accent'), (x * 1.05, y + (y - 0.1) * 0.05, 1.3))\n"
     "        p('tentacle_ring', (0.24, 0.24, 0.06), mm('accent'), (x * 1.08, y + (y - 0.1) * 0.08, 1.2 + h * 0.6))\n"
     "        p('sucker', (0.08, 0.08, 0.08), mm('belly'), (x * 1.08 + 0.1, y + (y - 0.1) * 0.08, 1.2 + h * 0.35))\n"
     "        p('sucker', (0.08, 0.08, 0.08), mm('belly'), (x * 1.1 + 0.1, y + (y - 0.1) * 0.1, 1.2 + h * 0.8))\n"),
    ("    grid(B, 'l', 3, 2, mm('accent'), (0.14, 0.14), name='side_gem', rot=(45, 0, 0))\n    grid(B, 'r', 3, 2, mm('accent'), (0.14, 0.14), name='side_gem', rot=(45, 0, 0))\n    grid(B, 'k', 3, 2, mm('accent'), (0.14, 0.14), name='back_gem', rot=(0, 45, 0))\n    for i in range(8):\n        ang = math.radians(i * 45)\n",
     "    grid(B, 'l', 4, 3, mm('accent'), (0.12, 0.12), name='side_gem', rot=(45, 0, 0))\n    grid(B, 'r', 4, 3, mm('accent'), (0.12, 0.12), name='side_gem', rot=(45, 0, 0))\n    grid(B, 'k', 4, 3, mm('accent'), (0.12, 0.12), name='back_gem', rot=(0, 45, 0))\n    for i in range(16):\n        ang = math.radians(i * 22.5)\n"),
])
print('ok')
