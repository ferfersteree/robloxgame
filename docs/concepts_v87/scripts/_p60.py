import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [("('wolf', 'Wolf', 2, 3, 'ground', 3.6, 'quad')", "('wolf', 'Wolf', 2, 3, 'ground', 2.6, 'quad')")])
sub('biome_07.py', [
    ("        b('tail', (0.3, 0.3, 0.26), mm('main' if j < 4 else 'dark'), (math.cos(ang) * 0.5, 0.3 + math.sin(ang) * 0.45 - 0.2, 0.14), bev=0.08)\n    return finish(a)",
     "        b('tail', (0.3, 0.3, 0.26), mm('main' if j < 4 else 'dark'), (math.cos(ang) * 0.5, 0.3 + math.sin(ang) * 0.45 - 0.2, 0.14), bev=0.08)\n"
     "    a.bx.update(body=B, head=Hd)\n    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.2, 0.7), Hit=(0, 0.25, 0.9))\n    return finish(a)"),
])
sub('biome_03.py', [
    ("antler='#f0e0c0'), 2.4)", "antler='#f0e0c0'), 2.19)"),
    ("    tail_kit('pom', 'body', (0, 1.25, 0.5), 'main', 'belly', size=0.18)\n",
     "    grid(B, 'k', 2, 2, mm('belly'), (0.1, 0.1), name='rump_spot', span=(0.5, 0.5))\n"
     "    use('head')\n    grid(Hd, 't', 2, 2, mm('accent'), (0.08, 0.08), name='head_spot', span=(0.4, 0.4))\n    use('body')\n"
     "    tail_kit('pom', 'body', (0, 1.25, 0.5), 'main', 'belly', size=0.18)\n"),
])
sub('biome_04.py', [("nest='#a8784a', egg='#a8e0ff'), 3.0)", "nest='#a8784a', egg='#a8e0ff'), 4.57)")])
sub('biome_02.py', [
    ("tongue='#ff7a8a'), 2.6)", "tongue='#ff7a8a'), 1.75)"),
    ("    grid(Hd, 't', 2, 2, mm('dark'), (0.08, 0.08), name='brow_mark', span=(0.5, 0.5))\n",
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.08, 0.08), name='brow_mark', span=(0.5, 0.5))\n"
     "    grid(Hd, 'l', 2, 2, mm('accent'), (0.08, 0.08), name='cheek_fur', span=(0.5, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('accent'), (0.08, 0.08), name='cheek_fur', span=(0.5, 0.5))\n"
     "    use('body')\n"
     "    grid(B, 'u', 2, 4, mm('accent'), (0.1, 0.1), name='belly_fur', span=(0.6, 0.8))\n"
     "    for k_ in range(8):\n        ang = math.radians(k_ * 45)\n        p('ruff_tuft', (0.16, 0.16, 0.16), mm('belly'), (math.cos(ang) * 0.45, -0.62, zb + math.sin(ang) * 0.42))\n"
     "    for nm in [l for l in a.legs]:\n        use(nm)\n        sgn = -1 if nm.endswith('L') else 1\n        fy = -1.3 if '_f' in nm else 2.05\n        fz = zb - 0.72 if '_f' in nm else zb - 0.85\n"
     "        for t in range(3):\n            p('toe', (0.06, 0.05, 0.06), mm('dark'), (sgn * 0.26 + (t - 1) * 0.07, fy - (0.14 if '_f' in nm else -0.14), fz))\n"),
    # lynx +16
    ("    sg('tail', 'body', (0, 1.2, 0.5))\n    a.tail = ['tail']\n    b('bobtail'",
     "    grid(B, 'f', 3, 1, mm('belly'), (0.1, 0.1), name='chest_fur', span=(0.7, 0.1))\n"
     "    use('head')\n    grid(Hd, 't', 2, 2, mm('dark'), (0.06, 0.06), name='brow_spot', span=(0.4, 0.4))\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_spot', span=(0.4, 0.4))\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.06, 0.06), name='cheek_spot', span=(0.4, 0.4))\n    use('body')\n"
     "    sg('tail', 'body', (0, 1.2, 0.5))\n    a.tail = ['tail']\n    b('bobtail'"),
])
print('ok')
