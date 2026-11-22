import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [
    ("('magma_hippo', 'Magma Hippo', 25, 3, 'ground', 5.5, 'quad')", "('magma_hippo', 'Magma Hippo', 25, 3, 'ground', 3.0, 'quad')"),
])
sub('biome_25.py', [
    # tarsier
    ("                        **{'*ember': '#ffb84a'}), 1.6)", "                        **{'*ember': '#ffb84a'}), 2.5)"),
    ("    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='head_stripe', span=(0.4, 0.5))\n    use('body')\n    grid(B, 'k'",
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='head_stripe', span=(0.4, 0.5))\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_fluff', span=(0.5, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_fluff', span=(0.5, 0.5))\n"
     "    use('body')\n"
     "    for j in range(3):\n        p('belly_dot', (0.08, 0.04, 0.08), mm('ear'), (0, -0.22, 0.45 + j * 0.15))\n"
     "    for sgn in (-1, 1):\n        p('chest_tuft', (0.14, 0.08, 0.12), mm('belly'), (sgn * 0.12, -0.18, 0.92))\n"
     "    grid(B, 'k'"),
    ("    for j in range(5):\n        p('tail', (0.08, 0.08, 0.36), mm('main'), (0, 0.5 + 0.04 * j, 0.5 + j * 0.34))",
     "    for j in range(8):\n        p('tail', (0.08, 0.08, 0.24), mm('main' if j % 2 else 'dark'), (0, 0.5 + 0.025 * j, 0.48 + j * 0.22))"),
    # salamander
    ("    grid(Hd, 't', 3, 2, mm('spot'), (0.1, 0.1), name='head_spot', span=(0.7, 0.6))\n",
     "    grid(Hd, 't', 3, 2, mm('spot'), (0.1, 0.1), name='head_spot', span=(0.7, 0.6))\n"
     "    use('body')\n"
     "    for j in range(4):\n        p('back_ridge', (0.12, 0.12, 0.1), mm('accent'), (0, 0.46, 0.5 + j * 0.2))\n"
     "    use('head')\n"),
    # hippo
    ("blush='#ff9ab4', **{'*lava': '#ff6a1a', '*lava2': '#ffb84a'}), 4.0)", "blush='#ff9ab4', **{'*lava': '#ff6a1a', '*lava2': '#ffb84a'}), 2.02)"),
    ("    for k_ in range(14):\n        ang = math.radians(k_ * (360 / 14))\n        b('pool_rock', (0.7, 0.5, 0.4 + 0.12 * (k_ % 2)), mm('rock'), (math.cos(ang) * 1.9, 0.5 + math.sin(ang) * 1.7, 0.2), rot=(0, 0, k_ * (360 / 14) + 90), bev=0.08)",
     "    for k_ in range(20):\n        ang = math.radians(k_ * 18)\n        b('pool_rock', (0.56, 0.44, 0.4 + 0.12 * (k_ % 2)), mm('rock'), (math.cos(ang) * 1.9, 0.5 + math.sin(ang) * 1.7, 0.2), rot=(0, 0, k_ * 18 + 90), bev=0.08)"),
    ("    grid(B, 't', 3, 3, mm('dark'), (0.14, 0.14), name='back_spot', span=(0.6, 0.6), offset=0.2)\n",
     "    grid(B, 't', 4, 4, mm('dark'), (0.12, 0.12), name='back_spot', span=(0.6, 0.6), offset=0.2)\n"
     "    grid(B, 'l', 2, 3, mm('belly'), (0.12, 0.12), name='side_spot', span=(0.6, 0.4))\n"
     "    grid(B, 'r', 2, 3, mm('belly'), (0.12, 0.12), name='side_spot', span=(0.6, 0.4))\n"),
    ("    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_spot', span=(0.5, 0.4))\n",
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.1, 0.1), name='head_spot', span=(0.5, 0.4))\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_spot', span=(0.5, 0.4))\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='cheek_spot', span=(0.5, 0.4))\n"
     "    for t in range(6):\n        p('small_tooth', (0.08, 0.08, 0.1), mm('tusk'), ((t - 2.5) * 0.18, -1.2, 0.82))\n"
     "    for sgn in (-1, 1):\n        for t in range(2):\n            p('whisker', (0.2, 0.02, 0.02), mm('dark'), (sgn * 0.62, -1.2, 1.8 + t * 0.08), rot=(0, sgn * (10 - 20 * t), 0))\n"),
    ("    for k_ in range(6):\n        ang = math.radians(k_ * 60 + 15)\n        p('lava_bubble'", "    for k_ in range(10):\n        ang = math.radians(k_ * 36 + 15)\n        p('lava_bubble'"),
])
print('ok')
