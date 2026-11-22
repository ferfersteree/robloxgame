import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_24.py', [
    ("glass='#d8f4ff', leg='#2a4a8a', blush='#ff9ab4'), 1.6)", "glass='#d8f4ff', leg='#2a4a8a', blush='#ff9ab4'), 2.22)"),
    ("                        **{'*shard': '#8ae8ff'}), 4.0)", "                        **{'*shard': '#8ae8ff'}), 3.54)"),
    ("    eyes(Hd, 0.3, 0.24, 0.14, iris='#4a2a1e', brow='#4a2a1e', lash=True)\n",
     "    eyes(Hd, 0.3, 0.24, 0.14, iris='#4a2a1e', brow='#4a2a1e', lash=True)\n"
     "    grid(Hd, 't', 2, 2, mm('dark'), (0.08, 0.08), name='head_spot', span=(0.5, 0.5))\n"
     "    use('body')\n"
     "    grid(B, 'l', 2, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.5, 0.5))\n"
     "    grid(B, 'r', 2, 2, mm('belly'), (0.1, 0.1), name='side_spot', span=(0.5, 0.5))\n"),
    # centaur
    ("            p('hoof', (0.34, 0.38, 0.16), mm('hoof'), (sgn * 0.35, fy - 0.02, 0.08))\n",
     "            p('hoof', (0.34, 0.38, 0.16), mm('hoof'), (sgn * 0.35, fy - 0.02, 0.08))\n"
     "            p('knee_band', (0.34, 0.34, 0.08), mm('accent'), (sgn * 0.35, fy, LEG * 0.6))\n"
     "            for t in (-1, 1):\n                p('fetlock', (0.1, 0.1, 0.14), mm('cloud'), (sgn * 0.35 + t * 0.1, fy - 0.16, 0.3))\n"),
    ("    grid(B, 't', 2, 3, mm('belly'), (0.12, 0.12), name='dapple', span=(0.6, 0.6), offset=0.2)\n",
     "    grid(B, 't', 2, 3, mm('belly'), (0.12, 0.12), name='dapple', span=(0.6, 0.6), offset=0.2)\n"
     "    grid(B, 'k', 2, 2, mm('belly'), (0.12, 0.12), name='dapple', span=(0.6, 0.5))\n"
     "    grid(B, 'u', 2, 3, mm('dark'), (0.12, 0.12), name='under_spot', span=(0.6, 0.6))\n"),
    ("    p('bolt_emblem', (0.2, 0.05, 0.3), mm('accent'), (0, TB.front - 0.01, B.top + 0.5), rot=(0, 20, 0))\n",
     "    p('bolt_emblem', (0.2, 0.05, 0.3), mm('accent'), (0, TB.front - 0.01, B.top + 0.5), rot=(0, 20, 0))\n"
     "    grid(TB, 'k', 2, 2, mm('belly'), (0.1, 0.1), name='shirt_dot', span=(0.5, 0.5))\n"
     "    grid(TB, 'l', 2, 2, mm('belly'), (0.08, 0.08), name='shirt_dot', span=(0.5, 0.5))\n"
     "    grid(TB, 'r', 2, 2, mm('belly'), (0.08, 0.08), name='shirt_dot', span=(0.5, 0.5))\n"
     "    p('scarf', (0.7, 0.5, 0.12), mm('accent'), (0, B.front + 0.3, B.top + 0.92))\n"
     "    for t in range(2):\n        p('scarf_tail', (0.12, 0.08, 0.3), mm('accent'), (0.2 + t * 0.12, TB.front - 0.02, B.top + 0.72 - t * 0.06))\n"),
    ("        p('sleeve', (0.26, 0.26, 0.2), mm('shirt'), (sgn * 0.52, B.front + 0.3, B.top + 0.75))\n",
     "        p('sleeve', (0.26, 0.26, 0.2), mm('shirt'), (sgn * 0.52, B.front + 0.3, B.top + 0.75))\n"
     "        p('bracelet', (0.26, 0.26, 0.06), mm('accent'), (sgn * 0.52, B.front + 0.18, B.top + 0.3))\n"),
    ("    p('javelin_tip2', (0.16, 0.1, 0.3), mm('accent'), (0.6, B.front, B.top + 1.86), rot=(0, -20, 0))\n",
     "    p('javelin_tip2', (0.16, 0.1, 0.3), mm('accent'), (0.6, B.front, B.top + 1.86), rot=(0, -20, 0))\n"
     "    for t in range(3):\n        p('javelin_wrap', (0.12, 0.12, 0.06), mm('cloud'), (0.56, B.front, B.top + 0.3 + t * 0.12))\n"),
    ("        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.26, Hd.front - 0.012, Hd.c.z - 0.12))\n        nm = 'ear_' + n\n        sg(nm, 'head', (sgn * 0.4, Hd.c.y, Hd.top - 0.1))",
     "        p('blush', (0.12, 0.03, 0.06), mm('blush'), (sgn * 0.26, Hd.front - 0.012, Hd.c.z - 0.12))\n"
     "        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.2, Hd.front - 0.013, Hd.c.z - 0.06))\n"
     "        nm = 'ear_' + n\n        sg(nm, 'head', (sgn * 0.4, Hd.c.y, Hd.top - 0.1))"),
])
print('ok')
