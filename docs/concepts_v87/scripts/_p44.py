import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_19.py', [
    ("(0, 0.6, 4.2, 0)", "(0, 0.6, 3.9, 0)"),
    ("(0.9, 0.1, 4.8)", "(0.9, 0.1, 4.5)"),
    ("claw='#3a2e6a', freckle='#8ad8ff'), 1.6)", "claw='#3a2e6a', freckle='#8ad8ff'), 1.24)"),
    ("**{'*tip': '#ffffff'}), 1.6)", "**{'*tip': '#ffffff'}), 1.23)"),
    ("(math.cos(ang) * 1.5 + 0.1, 0.35 + math.sin(ang) * 1.35,", "(math.cos(ang) * 1.25 + 0.1, 0.35 + math.sin(ang) * 1.15,"),
    ("    a.bx.update(body=B, head=Hd)\n    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 0.5), Hit=(0, 0.4, 0.9))\n",
     "    use('head')\n    grid(Hd, 't', 2, 2, mm('belly'), (0.08, 0.08), name='head_star', span=(0.5, 0.5), rot=(0, 0, 45))\n    use('body')\n"
     "    a.bx.update(body=B, head=Hd)\n    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 0.5), Hit=(0, 0.4, 0.9))\n"),
    ("dot='#fff0d8', iris='#3a2e6a'), 2.4)", "dot='#fff0d8', iris='#3a2e6a'), 3.46)"),
    ("    p('crown_bar', (0.36, 0.05, 0.04), mm('accent'), (0, 0, zc + 1.58))\n",
     "    p('crown_bar', (0.36, 0.05, 0.04), mm('accent'), (0, 0, zc + 1.58))\n"
     "    use('body')\n"
     "    for i in range(10):\n"
     "        ang = math.radians(i * 36 + 18)\n"
     "        p('core_dot', (0.08, 0.06, 0.08), mm('accent' if i % 2 else 'dot'), (math.sin(ang) * 0.42, 0.22, zc + math.cos(ang) * 0.42), rot=(0, 45, 0))\n"
     "    for i in range(4):\n"
     "        p('back_ridge', (0.14, 0.1, 0.14), mm('dark'), ((i - 1.5) * 0.18, 0.27, zc + 0.1), rot=(0, 45, 0))\n"),
])
print('ok')
