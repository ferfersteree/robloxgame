import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_14.py', [
    ("    spec = ((-1.8, 0.4, 1.1, 3.4, -12), (-0.5, 0.9, 1.3, 4.3, -4), (0.9, 0.8, 1.2, 3.8, 8), (2.2, 0.3, 1.0, 2.9, 16), (-2.8, -0.3, 0.8, 2.0, -24),",
     "    spec = ((-1.8, 0.4, 1.1, 3.0, -12), (-0.5, 0.9, 1.3, 3.6, -4), (0.9, 0.8, 1.2, 3.3, 8), (2.2, 0.3, 1.0, 2.6, 16), (-2.8, -0.3, 0.8, 1.8, -24),"),
    ("**{'*glow': '#ffb02a', '*glow2': '#ffe14a', '*flame': '#ff4a1a'}), 2.0, hover=5.0, z0=z0)",
     "**{'*glow': '#ffb02a', '*glow2': '#ffe14a', '*flame': '#ff4a1a'}), 2.6, hover=5.0, z0=z0)"),
    # toad +32
    ("    accessory('scarf', Box((0, B.front + 0.2, B.top + 0.1), (B.s.x * 0.9, 0.6, 0.3)), '#3a8ad8', '#ffd84a', z=B.top + 0.06)\n",
     "    accessory('scarf', Box((0, B.front + 0.2, B.top + 0.1), (B.s.x * 0.9, 0.6, 0.3)), '#3a8ad8', '#ffd84a', z=B.top + 0.06)\n"
     "    grid(B, 'k', 3, 2, mm('wart'), (0.12, 0.12), name='rump_wart')\n"
     "    grid(B, 'f', 3, 2, mm('accent'), (0.1, 0.06), name='belly_line', span=(0.6, 0.5))\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('wart'), (0.1, 0.1), name='head_wart')\n"
     "    grid(Hd, 'r', 2, 2, mm('wart'), (0.1, 0.1), name='head_wart')\n"
     "    for sgn, n in LR:\n"
     "        p('tympanum', (0.05, 0.2, 0.2), mm('dark'), (sgn * (Hd.s.x / 2 + 0.01), Hd.c.y + 0.1, Hd.c.z))\n"
     "        p('tympanum_in', (0.06, 0.1, 0.1), mm('accent'), (sgn * (Hd.s.x / 2 + 0.012), Hd.c.y + 0.1, Hd.c.z))\n"
     "    for i in range(5):\n"
     "        p('lip_dot', (0.06, 0.04, 0.05), mm('belly'), ((i - 2) * 0.2, Hd.front - 0.012, Hd.c.z - 0.28))\n"
     "    use('body')\n"),
    # rhino +20
    ("    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)\n    for ft in a.bx['feet']:\n        p('ankle', (ft.s.x + 0.02, ft.s.y * 0.8, 0.08), mm('belly'), (ft.c.x, ft.c.y + 0.04, ft.top + 0.06))\n    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)\n    # rarity 4: magma seams",
     "    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)\n    for ft in a.bx['feet']:\n        p('ankle', (ft.s.x + 0.02, ft.s.y * 0.8, 0.08), mm('belly'), (ft.c.x, ft.c.y + 0.04, ft.top + 0.06))\n"
     "        p('knee_plate', (ft.s.x + 0.04, 0.1, 0.16), mm('main'), (ft.c.x, ft.front + 0.04, 0.34))\n"
     "    grid(a.bx['rump'], 'k', 3, 2, mm('belly'), (0.16, 0.16), name='rump_plate')\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.14, 0.14), name='cheek_plate')\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.14, 0.14), name='cheek_plate')\n"
     "    use('body')\n"
     "    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)\n    # rarity 4: magma seams"),
    # phoenix +32
    ("    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('belly'), 4, 0.9, 0.36)\n    for i in range(3):\n        for j in range(3):\n            p('back_feather', (0.28, 0.3, 0.05), mm('dark' if (i + j) % 2 else 'accent'),",
     "    fluff(Box((0, B.front - 0.08, B.c.z), (B.s.x * 0.76, 0.12, B.s.z * 0.76)), 'f', mm('belly'), 4, 0.9, 0.36)\n"
     "    grid(B, 'l', 3, 2, mm('dark'), (0.2, 0.16), name='side_feather', offset=0.1)\n"
     "    grid(B, 'r', 3, 2, mm('dark'), (0.2, 0.16), name='side_feather', offset=0.1)\n"
     "    grid(B, 'u', 3, 2, mm('accent'), (0.2, 0.2), name='belly_feather', th=0.1)\n"
     "    for sgn, n in LR:\n"
     "        use('wing_' + n)\n"
     "        wb = a.bx['wings'][0 if sgn < 0 else 1]\n"
     "        for i in range(5):\n"
     "            p('covert', (0.3, 0.24, 0.05), mm('belly' if i % 2 else 'accent'), (sgn * (B.s.x / 2 + 0.3 + i * 0.44), 0.0, wb.c.z + 0.12))\n"
     "        use('leg_' + n)\n"
     "        for j in range(2):\n"
     "            p('leg_ring', (0.17, 0.17, 0.05), mm('dark'), (sgn * B.s.x * 0.24, 0.15, 0.1 + j * 0.08))\n"
     "    use('body')\n"
     "    for i in range(3):\n        for j in range(3):\n            p('back_feather', (0.28, 0.3, 0.05), mm('dark' if (i + j) % 2 else 'accent'),"),
    # pangolin +28
    ("    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)\n    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('claw_big', (0.12, 0.16, 0.08), mm('gold'), (ft.c.x, ft.front - 0.02, 0.05))\n",
     "    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.9, 0.3)\n    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('claw_big', (0.12, 0.16, 0.08), mm('gold'), (ft.c.x, ft.front - 0.02, 0.05))\n"
     "        for j in range(3):\n"
     "            b('leg_scale', (ft.s.x + 0.06, 0.16, 0.12), mm('scale2'), (ft.c.x, ft.c.y + 0.1 - j * 0.06, 0.2 + j * 0.1), rot=(-20, 0, 0), bev=0.02)\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('accent'), (0.1, 0.1), name='cheek_scale')\n"
     "    grid(Hd, 'r', 2, 2, mm('accent'), (0.1, 0.1), name='cheek_scale')\n"),
])
print('ok')
