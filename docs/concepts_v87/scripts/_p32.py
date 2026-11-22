import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)

sub('biome_12.py', [
    ("accent='#ffd84a', spot='#7ac8ff'), 1.2, hover=1.6, z0=zc)", "accent='#ffd84a', spot='#7ac8ff'), 1.0, hover=1.6, z0=zc)"),
    ("    for j in range(5):\n        cn('back_spine', 0.05, 0.16,", "    for j in range(10):\n        cn('back_spine', 0.05, 0.16,"),
    ("(0, 0.52, zc - 0.36 + j * 0.18), (0, 1, 0.3))", "(0, 0.52, zc - 0.4 + j * 0.09), (0, 1, 0.3))"),
    ("    grid(B, 't', 3, 3, mm('fin'), (0.16, 0.16), name='back_scale')\n",
     "    grid(B, 't', 3, 3, mm('fin'), (0.16, 0.16), name='back_scale')\n"
     "    grid(B, 'l', 4, 2, mm('belly'), (0.14, 0.14), name='side_scale', offset=0.08)\n"
     "    grid(B, 'r', 4, 2, mm('belly'), (0.14, 0.14), name='side_scale', offset=0.08)\n"
     "    grid(B, 'k', 3, 2, mm('dark'), (0.14, 0.14), name='back_scale2')\n"),
    ("    grid(Hd, 't', 2, 2, mm('dark'), (0.12, 0.12), name='head_plate')\n    use('body')\n    # rarity 6",
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.12, 0.12), name='head_plate')\n"
     "    grid(Hd, 'f', 4, 1, mm('accent'), (0.08, 0.06), name='lip_dot', span=(0.7, 0.2), offset=0.0)\n"
     "    use('body')\n"
     "    grid(B, 't', 2, 2, mm('accent'), (0.1, 0.1), name='back_dot', th=0.25)\n"
     "    # rarity 6"),
])
print('ok')
