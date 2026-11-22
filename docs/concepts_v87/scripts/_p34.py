import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_13.py', [
    ("    grid(B, 'lr'[0], 3, 1, mm('accent'), (0.1, 0.1), name='fleck', span=(0.6, 0.2)) if False else None\n",
     "    grid(B, 'l', 4, 2, mm('belly'), (0.1, 0.1), name='fleck', span=(0.8, 0.5), offset=0.05)\n"
     "    grid(B, 'r', 4, 2, mm('belly'), (0.1, 0.1), name='fleck', span=(0.8, 0.5), offset=0.05)\n"
     "    grid(B, 'k', 3, 2, mm('dark'), (0.14, 0.14), name='rump_fleck')\n"
     "    use('head')\n"
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.12, 0.12), name='head_fleck')\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='head_fleck')\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='head_fleck')\n"
     "    use('body')\n"),
    ("    grid(B, 't', 2, 3, mm('belly'), (0.16, 0.16), name='patch')\n",
     "    grid(B, 't', 2, 3, mm('belly'), (0.16, 0.16), name='patch')\n"
     "    grid(B, 'l', 4, 2, mm('belly'), (0.12, 0.12), name='mud', offset=0.06)\n"
     "    grid(B, 'r', 4, 2, mm('belly'), (0.12, 0.12), name='mud', offset=0.06)\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('dark'), (0.12, 0.12), name='head_patch')\n"
     "    grid(Hd, 'r', 2, 2, mm('dark'), (0.12, 0.12), name='head_patch')\n"
     "    use('body')\n"),
    ("    grid(B, 'k', 3, 2, mm('belly'), (0.3, 0.3), name='back_rock', th=0.12)\n",
     "    grid(B, 'k', 3, 2, mm('belly'), (0.3, 0.3), name='back_rock', th=0.12)\n"
     "    grid(B, 'f', 3, 3, mm('accent'), (0.1, 0.1), name='pebble', th=0.2, offset=0.1)\n"
     "    grid(B, 'l', 3, 3, mm('accent'), (0.12, 0.12), name='side_pebble', th=0.16)\n"
     "    grid(B, 'r', 3, 3, mm('accent'), (0.12, 0.12), name='side_pebble', th=0.16)\n"
     "    grid(B, 't', 3, 2, mm('belly'), (0.2, 0.2), name='top_rock', th=0.1)\n"
     "    use('head')\n"
     "    grid(Hd, 't', 3, 2, mm('accent'), (0.14, 0.14), name='head_pebble')\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.14, 0.14), name='head_rock')\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.14, 0.14), name='head_rock')\n"
     "    use('body')\n"
     "    for hb_ in a.bx['hands']:\n"
     "        use(hb_.seg)\n"
     "        for j in range(6):\n"
     "            p('arm_stud', (0.12, 0.12, 0.12), mm('belly'), (hb_.c.x + (j % 2 - 0.5) * 0.4, -0.26, hb_.c.z + 0.4 + (j // 2) * 0.3))\n"
     "    for ft in a.bx['feet']:\n"
     "        use(ft.seg)\n"
     "        for j in range(4):\n"
     "            p('leg_stud', (0.12, 0.12, 0.12), mm('belly'), (ft.c.x + (j % 2 - 0.5) * 0.3, ft.front + 0.2, 0.2 + (j // 2) * 0.2))\n"
     "    use('body')\n"),
    ("    grid(B, 'k', 3, 2, mm('dark'), (0.2, 0.16), name='back_fur')\n",
     "    grid(B, 'k', 3, 2, mm('dark'), (0.2, 0.16), name='back_fur')\n"
     "    grid(B, 'l', 3, 3, mm('main'), (0.14, 0.14), name='side_fur', th=0.08)\n"
     "    grid(B, 'r', 3, 3, mm('main'), (0.14, 0.14), name='side_fur', th=0.08)\n"
     "    grid(B, 't', 3, 2, mm('mane'), (0.2, 0.2), name='top_fur')\n"
     "    use('head')\n"
     "    grid(Hd, 't', 3, 2, mm('dark'), (0.12, 0.12), name='head_fur', span=(0.8, 0.5))\n"
     "    use('body')\n"),
])
print('ok')
