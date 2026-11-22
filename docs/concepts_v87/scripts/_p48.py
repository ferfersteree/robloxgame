import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_20.py', [
    ("'*steam': '#ffffff'}), 4.6)", "'*steam': '#ffffff'}), 3.61)"),
    ("'*ruby': '#ff3a5a'}), 3.0)", "'*ruby': '#ff3a5a'}), 4.95)"),
    ("        for k_ in range(4):\n            p('spoke', (0.15, 0.06, 0.46), mm('belly'), (ft.c.x + sgn * 0.065, ft.c.y, 0.28), rot=(k_ * 45, 0, 0))",
     "        for k_ in range(6):\n            p('spoke', (0.15, 0.06, 0.46), mm('belly'), (ft.c.x + sgn * 0.065, ft.c.y, 0.28), rot=(k_ * 30, 0, 0))"),
    ("    for i in range(4):\n        b('steam'", "    for i in range(6):\n        b('steam'"),
    ("(0.24 + 0.08 * i, 0.24 + 0.08 * i, 0.2), mm('steam'), (0.1 * (i % 2), B.c.y - 0.4 - 0.1 * i, B.top + 1.0 + i * 0.3)",
     "(0.2 + 0.06 * i, 0.2 + 0.06 * i, 0.16), mm('steam'), (0.1 * (i % 2), B.c.y - 0.4 - 0.08 * i, B.top + 1.0 + i * 0.22)"),
    ("    b('dome', (0.4, 0.4, 0.3), mm('accent'), (0, B.c.y + 0.4, B.top + 0.15), bev=0.1)\n",
     "    b('dome', (0.4, 0.4, 0.3), mm('accent'), (0, B.c.y + 0.4, B.top + 0.15), bev=0.1)\n"
     "    grid(B, 'u', 2, 3, mm('dark'), (0.12, 0.12), name='belly_plate', span=(0.6, 0.7))\n"
     "    for k_ in range(4):\n"
     "        ang = math.radians(k_ * 90 + 45)\n"
     "        p('stack_bolt', (0.06, 0.06, 0.06), mm('accent'), (math.cos(ang) * 0.2, B.c.y - 0.4 + math.sin(ang) * 0.2, B.top + 0.7))\n"
     "    p('collar', (B.s.x + 0.1, 0.16, B.s.z + 0.1), mm('red'), (0, B.front + 0.06, B.c.z))\n"
     "    for k_ in range(4):\n"
     "        p('collar_stud', (0.08, 0.06, 0.08), mm('accent'), ((k_ - 1.5) * 0.24, B.front - 0.03, B.c.z - B.s.z / 2 - 0.02))\n"),
    ("    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='head_rivet', span=(0.6, 0.6))\n    use('body')\n    tail_kit('stub', 'body', a.tail_j",
     "    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='head_rivet', span=(0.6, 0.6))\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_plate', span=(0.6, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_plate', span=(0.6, 0.5))\n"
     "    use('body')\n    tail_kit('stub', 'body', a.tail_j"),
])
print('ok')
