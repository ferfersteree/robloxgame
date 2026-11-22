import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [
    ("('rift_axolotl', 'Rift Axolotl', 18, 5, 'air', 5.0, 'fish')", "('rift_axolotl', 'Rift Axolotl', 18, 5, 'air', 3.2, 'fish')"),
])
sub('biome_18.py', [
    ("wing='#5a4a7a', **{'*glow': '#ff6ad0'}), 4.0)", "wing='#5a4a7a', **{'*glow': '#ff6ad0'}), 3.3)"),
    ("void='#0e0a1e', **{'*glow': '#c88aff', '*glow2': '#ffe06a', '*star': '#ffffff'}), 2.6)",
     "void='#0e0a1e', **{'*glow': '#c88aff', '*glow2': '#ffe06a', '*star': '#ffffff'}), 4.3)"),
    # mantis +60
    ("    # rarity 4: glowing wing veins and claw spikes, spore sparks\n",
     "    use('body')\n"
     "    AB = Box((0, 0.6, 0.9), (0.6, 1.4, 0.5))\n"
     "    grid(AB, 'l', 4, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))\n"
     "    grid(AB, 'r', 4, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))\n"
     "    grid(AB, 'u', 2, 4, mm('dark'), (0.1, 0.1), name='belly_plate', span=(0.6, 0.8))\n"
     "    for j in range(5):\n"
     "        p('thorax_ring', (0.34, 0.34, 0.05), mm('belly'), (0, -0.1 - j * 0.02, 1.1 + j * 0.22))\n"
     "    for j in range(6):\n"
     "        for sgn in (-1, 1):\n"
     "            p('wing_cell', (0.12, 0.14, 0.04), mm('belly'), (sgn * 0.18, 0.1 + j * 0.2, 1.3 - j * 0.055), rot=(-15, 0, 0))\n"
     "    for i, y in enumerate((0.3, 0.8)):\n"
     "        for sgn, n in LR:\n"
     "            use('leg_%d%s' % (i + 1, n))\n"
     "            p('knee', (0.14, 0.14, 0.14), mm('belly'), (sgn * 0.82, y, 0.9))\n"
     "            p('shin_band', (0.1, 0.1, 0.05), mm('accent'), (sgn * 0.82, y, 0.4))\n"
     "    use('head')\n"
     "    grid(Hd, 'f', 3, 1, mm('belly'), (0.08, 0.06), name='face_dot', span=(0.5, 0.1), offset=0.1)\n"
     "    for sgn, n in LR:\n"
     "        for j in range(3):\n"
     "            p('eye_facet', (0.04, 0.08, 0.08), mm('belly'), (sgn * 0.61, -0.3 + (j - 1) * 0.1, 2.5 + (j % 2) * 0.08))\n"
     "    use('body')\n"
     "    # rarity 4: glowing wing veins and claw spikes, spore sparks\n"),
    # axolotl +55
    ("    # rarity 5: glowing gill tips and back spots (own segments), bubble orbit, yellow aura\n",
     "    use('body')\n"
     "    grid(B, 'l', 4, 2, mm('spot'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))\n"
     "    grid(B, 'r', 4, 2, mm('spot'), (0.1, 0.1), name='side_spot', span=(0.8, 0.5))\n"
     "    grid(B, 'u', 2, 4, mm('belly'), (0.12, 0.12), name='belly_dot', offset=0.06)\n"
     "    use('head')\n"
     "    grid(Hd, 't', 3, 2, mm('spot'), (0.12, 0.12), name='head_spot', span=(0.7, 0.6))\n"
     "    grid(Hd, 'l', 2, 2, mm('spot'), (0.08, 0.08), name='cheek_spot')\n"
     "    grid(Hd, 'r', 2, 2, mm('spot'), (0.08, 0.08), name='cheek_spot')\n"
     "    use('tail')\n"
     "    for j in range(6):\n"
     "        for sgn in (-1, 1):\n"
     "            p('fin_dot', (0.12, 0.1, 0.1), mm('spot'), (sgn * 0.01, 1.05 + j * 0.22, zc + 0.22 * sgn * (1 if j % 2 else 0.6)))\n"
     "    for j in range(4):\n"
     "        p('tail_band', (0.52, 0.08, 0.42), mm('dark'), (0, 1.3 + j * 0.2, zc))\n"
     "    use('body')\n"
     "    # rarity 5: glowing gill tips and back spots (own segments), bubble orbit, yellow aura\n"),
    # behemoth +25
    ("    tail_kit('stub', 'body', (0, B.back, B.c.z), 'main', 'shell2', size=0.3)\n",
     "    tail_kit('stub', 'body', (0, B.back, B.c.z), 'main', 'shell2', size=0.3)\n"
     "    SB = Box((0, B.c.y, B.top + 0.7), (1.9, 1.9, 0.5))\n"
     "    grid(SB, 'l', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))\n"
     "    grid(SB, 'r', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))\n"
     "    grid(SB, 'f', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))\n"
     "    grid(SB, 'k', 4, 1, mm('accent'), (0.16, 0.16), name='shell_stud', span=(0.8, 0.1))\n"
     "    grid(B, 'u', 3, 3, mm('belly'), (0.24, 0.24), name='belly_plate')\n"),
])
print('ok')
