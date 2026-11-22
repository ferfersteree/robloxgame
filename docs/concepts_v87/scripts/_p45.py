import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_19.py', [
    # stag
    ("'*glow3': '#ffe68a'}), 4.4)", "'*glow3': '#ffe68a'}), 5.56)"),
    ("    grid(Hd, 't', 2, 2, mm('accent'), (0.06, 0.06), name='face_star', span=(0.5, 0.5), rot=(0, 0, 45))\n",
     "    grid(Hd, 't', 2, 2, mm('accent'), (0.06, 0.06), name='face_star', span=(0.5, 0.5), rot=(0, 0, 45))\n"
     "    grid(Hd, 'l', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_dot', span=(0.6, 0.5))\n"
     "    grid(Hd, 'r', 2, 2, mm('belly'), (0.08, 0.08), name='cheek_dot', span=(0.6, 0.5))\n"),
    ("            b('hoof', (0.24, 0.3, 0.16), mm('hoof'), (sgn * bw / 2, fy + 0.02, 0.08), bev=0.04)\n",
     "            b('hoof', (0.24, 0.3, 0.16), mm('hoof'), (sgn * bw / 2, fy + 0.02, 0.08), bev=0.04)\n"
     "            p('hoof_band', (0.2, 0.2, 0.05), mm('accent'), (sgn * bw / 2, fy + 0.04, 0.2))\n"),
    ("    for i in range(6):\n        p('dust', (0.07, 0.07, 0.07)", "    for i in range(10):\n        p('dust', (0.07, 0.07, 0.07)"),
    ("(0.2 * math.sin(i * 2.1), by - 0.6 + i * 0.24, zb + 0.2 * math.cos(i * 1.7))", "(0.22 * math.sin(i * 2.1), by - 0.65 + i * 0.145, zb + 0.22 * math.cos(i * 1.7))"),
    # jelly
    ("'*glow2': '#ffe68a'}), 2.4, hover=3.4, z0=zc)", "'*glow2': '#ffe68a'}), 3.87, hover=3.4, z0=zc)"),
    ("            for t in range(3):\n                p('tentacle', (0.12, 0.06, 0.3), mm('main' if (t + j) % 2 else 'belly'), (x, y, zc - 0.36 - j * 0.9 - t * 0.3), rot=(0, 0, i * 60))",
     "            for t in range(4):\n                p('tentacle', (0.12, 0.06, 0.24), mm('main' if (t + j) % 2 else 'belly'), (x, y, zc - 0.32 - j * 0.9 - t * 0.225), rot=(0, 0, i * 60))"),
    ("        p('skirt', (0.3, 0.3, 0.24), mm('frill' if i % 2 else 'accent'), (math.cos(ang) * 0.95, math.sin(ang) * 0.95, zc - 0.08), rot=(0, 0, i * 30))\n",
     "        p('skirt', (0.3, 0.3, 0.24), mm('frill' if i % 2 else 'accent'), (math.cos(ang) * 0.95, math.sin(ang) * 0.95, zc - 0.08), rot=(0, 0, i * 30))\n"
     "        p('skirt_dot', (0.1, 0.1, 0.1), mm('belly'), (math.cos(ang) * 1.01, math.sin(ang) * 1.01, zc + 0.1), rot=(0, 0, i * 30))\n"),
    ("            p('oral_frill', (0.36, 0.08, 0.12), mm('accent'), (math.cos(ang) * 0.25, math.sin(ang) * 0.25, zc - 0.3 - j * 0.38), rot=(0, 0, 45 * j + i * 90))\n",
     "            p('oral_frill', (0.36, 0.08, 0.12), mm('accent'), (math.cos(ang) * 0.25, math.sin(ang) * 0.25, zc - 0.3 - j * 0.38), rot=(0, 0, 45 * j + i * 90))\n"
     "            p('oral_dot', (0.08, 0.08, 0.08), mm('belly'), (math.cos(ang) * 0.38, math.sin(ang) * 0.38, zc - 0.45 - j * 0.38))\n"),
    ("    for i in range(8):\n        ang = math.radians(i * 45 + 22)\n        p('bell_glow'", "    for i in range(12):\n        ang = math.radians(i * 30 + 15)\n        p('bell_glow'"),
    ("p('bell_glow', (0.14, 0.14, 0.14)", "p('bell_glow', (0.12, 0.12, 0.12)"),
    # dragon
    ("'*star': '#ffffff'}), 2.6, hover=3.0, z0=zc)", "'*star': '#ffffff'}), 3.82, hover=3.0, z0=zc)"),
    ("            p('wing_claw', (0.1, 0.1, 0.14), mm('horn'),",
     "            p('wing_edge', (ln * 0.8, 0.07, 0.06), mm('accent'), (cx, 0.52, cz - 0.33), rot=(0, -sgn * ang, 0))\n"
     "            p('wing_claw', (0.1, 0.1, 0.14), mm('horn'),"),
    ("    grid(B, 'k', 2, 3, mm('dark'), (0.12, 0.12), name='back_scale')\n",
     "    grid(B, 'k', 2, 3, mm('dark'), (0.12, 0.12), name='back_scale')\n"
     "    grid(B, 'l', 2, 2, mm('dark'), (0.1, 0.1), name='side_scale')\n"
     "    grid(B, 'r', 2, 2, mm('dark'), (0.1, 0.1), name='side_scale')\n"),
])
print('ok')
