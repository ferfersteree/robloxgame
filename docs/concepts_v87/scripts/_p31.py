import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)


GRID = '''


def grid(box, f, nu, nv, mat, size=(0.14, 0.14), name='plate', span=(0.8, 0.8), th=0.03, offset=0.0, rot=(0, 0, 0)):
    """regular grid of detail plates on one face (scales, rivets, rows of spots)"""
    out = []
    for i in range(nu):
        for j in range(nv):
            u = ((i + 0.5) / nu - 0.5) * span[0] + (offset if j % 2 else 0.0)
            v = ((j + 0.5) / nv - 0.5) * span[1]
            out.append(on(box, f, u, v, size, mat, th=th, name=name, rot=rot))
    return out
'''
s = io.open('kits.py', encoding='utf-8').read()
if 'def grid(' not in s:
    io.open('kits.py', 'w', encoding='utf-8', newline='\n').write(s.rstrip('\n') + '\n' + GRID)

sub('roster.py', [("('reef_ray', 'Reef Ray', 12, 2, 'water', 2.0, 'fish')", "('reef_ray', 'Reef Ray', 12, 2, 'water', 1.4, 'fish')")])

sub('biome_12.py', [
    ("    p('pearl', (0.2, 0.2, 0.2), smooth(a.id + '_pearl', '#ffffff', 0.05), (0, 0.6, zc + 0.92), rot=(45, 45, 0))\n",
     "    p('pearl', (0.2, 0.2, 0.2), smooth(a.id + '_pearl', '#ffffff', 0.05), (0, 0.6, zc + 0.92), rot=(45, 45, 0))\n"
     "    grid(B, 'l', 3, 3, mm('accent'), (0.1, 0.1), name='shell_dot')\n"
     "    grid(B, 'r', 3, 3, mm('accent'), (0.1, 0.1), name='shell_dot')\n"
     "    grid(B, 't', 2, 3, mm('dark'), (0.12, 0.12), name='shell_dot')\n"
     "    for i in range(4):\n"
     "        p('coil_ring', (0.84, 0.08, 0.08), mm('dark'), (0, 0.4 + i * 0.12, zc + 0.86 - 0.03 * i))\n"
     "    use('tail')\n"
     "    for i in range(4):\n"
     "        p('tentacle_ring', (0.12, 0.12, 0.05), mm('dark'), ((i - 1.5) * 0.28, -0.36, zc - 0.6))\n"
     "    use('body')\n"),
    ("    for i in range(4):\n        p('back_stripe', (0.08, 0.26, 0.04), mm('dark'), (0, B.c.y - 0.4 + i * 0.3, zc + 0.41))\n",
     "    for i in range(4):\n        p('back_stripe', (0.08, 0.26, 0.04), mm('dark'), (0, B.c.y - 0.4 + i * 0.3, zc + 0.41))\n"
     "    grid(B, 'u', 3, 3, mm('spot'), (0.1, 0.1), name='belly_dot', th=0.1)\n"
     "    grid(B, 't', 2, 4, mm('accent'), (0.08, 0.08), name='back_dot', th=0.1, rot=(0, 0, 45))\n"
     "    for sgn, n in LR:\n"
     "        use('wing_' + n)\n"
     "        for i in range(3):\n"
     "            p('fin_dot', (0.08, 0.08, 0.03), mm('accent'), (sgn * (0.6 + 0.5 * (i + 0.5)), 0.2 + 0.1 * i + 0.3, zc + 0.03 * i + 0.09))\n"
     "    use('body')\n"),
    ("accent='#ff6a8a', fin='#ffd0f0'), 2.4, hover=2.4, z0=zc)", "accent='#ff6a8a', fin='#ffd0f0'), 3.4, hover=2.4, z0=zc)"),
    ("    spots(B, 'lr', 6, mm('belly'), 0.1, seed=3, name='spot')\n",
     "    spots(B, 'lr', 6, mm('belly'), 0.1, seed=3, name='spot')\n"
     "    grid(B, 'l', 2, 5, mm('dark'), (0.12, 0.06), name='side_ring')\n"
     "    grid(B, 'r', 2, 5, mm('dark'), (0.12, 0.06), name='side_ring')\n"
     "    for j in range(5):\n"
     "        cn('back_spine', 0.05, 0.16, mm('accent'), (0, 0.52, zc - 0.36 + j * 0.18), (0, 1, 0.3))\n"
     "    use('head')\n"
     "    for j in range(3):\n"
     "        p('snout_band', (0.32, 0.08, 0.28), mm('dark'), (0, Hd.front - 0.06 - j * 0.12, zc + 0.74))\n"
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_plate', span=(0.6, 0.4))\n"
     "    for sgn, n in LR:\n"
     "        p('cheek_fin', (0.06, 0.2, 0.2), mm('fin'), (sgn * 0.4, Hd.c.y + 0.1, zc + 0.8))\n"
     "    use('body')\n"),
    ("    a.bx.update(body=B, head=Hd)\n    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc + 0.1), Hit=(0, 0.1, zc + 0.3))",
     "    use('tail')\n"
     "    for i in range(4):\n"
     "        for sgn, n in LR:\n"
     "            p('tail_ring', (0.05, 0.3 - 0.06 * i, 0.06), mm('belly'), (sgn * (0.25 - 0.04 * i), 0.15 + 0.06 * i, zc - 0.66 - i * 0.26))\n"
     "    use('body')\n"
     "    a.bx.update(body=B, head=Hd)\n    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.3, zc + 0.1), Hit=(0, 0.1, zc + 0.3))"),
    ("    stripes(B, 'lr', 4, mm('dark'), 0.08, name='stripe', span=0.8)\n    for i in range(4):\n        p('belly_line',",
     "    stripes(B, 'lr', 4, mm('dark'), 0.08, name='stripe', span=0.8)\n"
     "    grid(B, 'l', 6, 2, mm('belly'), (0.12, 0.1), name='scale', offset=0.06)\n"
     "    grid(B, 'r', 6, 2, mm('belly'), (0.12, 0.1), name='scale', offset=0.06)\n"
     "    grid(B, 't', 2, 6, mm('dark'), (0.14, 0.14), name='back_plate')\n"
     "    grid(B, 'u', 2, 5, mm('belly'), (0.2, 0.18), name='belly_plate', th=0.1)\n"
     "    for sgn, n in LR:\n"
     "        use('wing_' + n)\n"
     "        for j in range(3):\n"
     "            p('fin_band', (0.6 * 0.3, 0.06, 0.13), mm('dark'), (sgn * (1.0 / 2 + 0.6 * (0.2 + 0.25 * j)), 0.12 + 0.12 * j - 0.1, zc - 0.18))\n"
     "    use('head')\n"
     "    for i in range(6):\n"
     "        p('hammer_dot', (0.1, 0.06, 0.1), mm('dark'), ((i - 2.5) * 0.3, Hd.c.y - 0.28, zc + 0.24))\n"
     "    for sgn, n in LR:\n"
     "        for j in range(3):\n"
     "            p('tooth', (0.06, 0.04, 0.06), mm('white'), (sgn * (0.2 + 0.08 * j), Hd.front - 0.012, zc - 0.3))\n"
     "    use('body')\n"
     "    for i in range(4):\n        p('belly_line',"),
    ("    use('body')\n    for i in range(4):\n        p('body_band', (B.s.x + 0.04, 0.12, B.s.z + 0.04), mm('dark'), (0, B.front + 0.2 + i * 0.36, B.c.z))\n",
     "    use('body')\n    for i in range(4):\n        p('body_band', (B.s.x + 0.04, 0.12, B.s.z + 0.04), mm('dark'), (0, B.front + 0.2 + i * 0.36, B.c.z))\n"
     "    grid(B, 't', 3, 3, mm('fin'), (0.16, 0.16), name='back_scale')\n"
     "    for i, (nm, nb) in enumerate(zip(a.neck, necks)):\n"
     "        use(nm)\n"
     "        for sgn, n in LR:\n"
     "            for j in range(2):\n"
     "                p('neck_spot', (0.04, 0.12, 0.12), mm('belly'), (sgn * (nb.s.x / 2 + 0.012), nb.c.y - 0.12 + j * 0.24, nb.c.z + 0.3), rot=(12, 0, 0))\n"
     "        p('neck_ring', (nb.s.x + 0.04, nb.s.y + 0.04, 0.08), mm('dark'), (0, nb.c.y, nb.c.z - 0.3), rot=(12, 0, 0))\n"
     "    use('body')\n"),
    ("    # rarity 6: glowing claw gems and banding",
     "    grid(B, 'l', 3, 2, mm('accent'), (0.12, 0.12), name='side_dot')\n"
     "    grid(B, 'r', 3, 2, mm('accent'), (0.12, 0.12), name='side_dot')\n"
     "    for i, t in enumerate(a.tail):\n"
     "        use(t)\n"
     "        for sgn, n in LR:\n"
     "            p('tail_plate', (0.05, 0.3, 0.3 - 0.06 * i), mm('dark'), (sgn * ((0.9 - 0.15 * i) / 2 + 0.01), B.back + 0.2 + i * 0.38, B.c.z - 0.04 * i))\n"
     "        p('tail_dot', (0.1, 0.1, 0.05), mm('accent'), (0, B.back + 0.2 + i * 0.38, B.c.z + (0.5 - 0.06 * i) / 2 - 0.04 * i + 0.02))\n"
     "    use('head')\n"
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.12, 0.12), name='head_plate')\n"
     "    use('body')\n"
     "    # rarity 6: glowing claw gems and banding"),
])
print('ok')
