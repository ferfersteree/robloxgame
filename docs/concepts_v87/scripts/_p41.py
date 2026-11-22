import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('roster.py', [
    ("('cloud_glider', 'Cloud Glider', 17, 5, 'air', 5.0, 'fish')", "('cloud_glider', 'Cloud Glider', 17, 5, 'air', 2.6, 'fish')"),
    ("('sky_drake', 'Sky Drake', 17, 6, 'air', 11.0, 'dragon')", "('sky_drake', 'Sky Drake', 17, 6, 'air', 7.0, 'dragon')"),
])
sub('biome_17.py', [
    ("GROUND = '#9ac8e8'", "GROUND = '#6a9ad0'"),
    ("FOOT = dict(cloud_glider=1.3, sky_drake=1.4, sky_stag=1.1)", "FOOT = dict(cloud_glider=1.8, sky_drake=2.0, sky_stag=1.1)"),
    # ribbonfish +20
    ("    b('tail_tip', (0.5, 0.3, 0.06), mm('accent'), (0, cur.y + 0.1, zc), rot=(0, 0, 45), bev=0.02)\n",
     "    b('tail_tip', (0.5, 0.3, 0.06), mm('accent'), (0, cur.y + 0.1, zc), rot=(0, 0, 45), bev=0.02)\n"
     "    use('body')\n"
     "    grid(B, 't', 2, 2, mm('belly'), (0.12, 0.12), name='back_dot')\n"
     "    grid(B, 'u', 2, 2, mm('accent'), (0.12, 0.12), name='belly_dot')\n"
     "    for sgn, n in LR:\n"
     "        use('wing_' + n)\n"
     "        for j in range(3):\n"
     "            p('fin_ray', (0.36, 0.05, 0.07), mm('accent'), (sgn * 0.55, 0.1 - 0.12 + j * 0.12, zc))\n"
     "    use('head')\n"
     "    grid(Hd, 't', 2, 2, mm('belly'), (0.1, 0.1), name='head_dot')\n"),
    # sheep +12
    ("    tail_kit('pom', 'body', (0, 0.9, 0.9), 'main', 'main', size=0.2)\n    return finish(a)\n\n\ndef island_chameleon",
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('dark'), (0.08, 0.08), name='face_dot')\n"
     "    grid(Hd, 'r', 2, 2, mm('dark'), (0.08, 0.08), name='face_dot')\n"
     "    use('body')\n"
     "    for i in range(4):\n"
     "        p('rain_drop', (0.08, 0.08, 0.12), mm('accent'), ((i - 1.5) * 0.3, 0.2 + (i % 2) * 0.3, 0.3))\n"
     "    tail_kit('pom', 'body', (0, 0.9, 0.9), 'main', 'main', size=0.2)\n    return finish(a)\n\n\ndef island_chameleon"),
    # chameleon +32
    ("    grid(B, 'u', 2, 3, mm('belly'), (0.14, 0.14), name='belly_scale')\n",
     "    grid(B, 'u', 2, 3, mm('belly'), (0.14, 0.14), name='belly_scale')\n"
     "    grid(B, 't', 2, 4, mm('stripe'), (0.08, 0.08), name='back_dot', span=(0.5, 0.8))\n"
     "    grid(B, 'l', 4, 2, mm('belly'), (0.06, 0.06), name='side_dot', span=(0.8, 0.5), offset=0.05)\n"
     "    grid(B, 'r', 4, 2, mm('belly'), (0.06, 0.06), name='side_dot', span=(0.8, 0.5), offset=0.05)\n"
     "    use('head')\n"
     "    grid(Hd, 'l', 2, 2, mm('stripe'), (0.08, 0.08), name='cheek_dot')\n"
     "    grid(Hd, 'r', 2, 2, mm('stripe'), (0.08, 0.08), name='cheek_dot')\n"
     "    use('body')\n"),
    # glider: smaller membrane + details
    ("    b('belly', (0.5, 0.9, 0.08), mm('belly'), (0, 0.2, zc - 0.28), bev=0.03)\n    p('back_stripe', (0.12, 1.0, 0.04), mm('stripe'), (0, 0.2, zc + 0.27))\n",
     "    b('belly', (0.5, 0.9, 0.08), mm('belly'), (0, 0.2, zc - 0.28), bev=0.03)\n    p('back_stripe', (0.12, 1.0, 0.04), mm('stripe'), (0, 0.2, zc + 0.27))\n"
     "    grid(B, 't', 2, 4, mm('accent'), (0.08, 0.08), name='back_dot', th=0.06)\n"
     "    grid(B, 'u', 2, 3, mm('accent'), (0.1, 0.1), name='belly_dot', th=0.1)\n"),
    ("        for j in range(3):\n            p('membrane_spot', (0.16, 0.16, 0.07), mm('accent'), (sgn * (0.6 + j * 0.3), 0.2 + (j - 1) * 0.3, zc - 0.03))\n",
     "        for j in range(3):\n            p('membrane_spot', (0.16, 0.16, 0.07), mm('accent'), (sgn * (0.6 + j * 0.3), 0.2 + (j - 1) * 0.3, zc - 0.03))\n"
     "        for j in range(5):\n            p('membrane_rib', (0.04, 1.2, 0.07), mm('stripe'), (sgn * (0.5 + j * 0.2), 0.2, zc - 0.03))\n"
     "        for j in range(4):\n            p('fringe', (0.2, 0.1, 0.1), mm('belly'), (sgn * (0.5 + j * 0.28), 0.2 + 0.68, zc - 0.04))\n"
     "            p('fringe', (0.2, 0.1, 0.1), mm('belly'), (sgn * (0.5 + j * 0.28), 0.2 - 0.68, zc - 0.04))\n"),
    ("    for j in range(3):\n        p('tail_fluff', (0.6, 0.1, 0.14), mm('belly'), (0, 0.9 + j * 0.24, zc))\n",
     "    for j in range(3):\n        p('tail_fluff', (0.6, 0.1, 0.14), mm('belly'), (0, 0.9 + j * 0.24, zc))\n"
     "    for j in range(4):\n        p('tail_band', (0.52, 0.08, 0.17), mm('stripe'), (0, 0.84 + j * 0.2, zc))\n"
     "    use('head')\n"
     "    grid(Hd, 't', 2, 2, mm('stripe'), (0.1, 0.1), name='head_dot')\n"
     "    for sgn, n in LR:\n"
     "        for j in range(3):\n"
     "            p('whisker', (0.22, 0.02, 0.02), mm('dark'), (sgn * 0.5, Hd.front + 0.06, zc - 0.06 + (j - 1) * 0.05), rot=(0, -sgn * (j - 1) * 10, sgn * 10))\n"
     "    use('tail')\n"),
    # drake: shorter chain, more detail
    ("    path = ((0, 0.6, 0.3), (0, 0.6, 0.3), (0, 0.6, 0.0), (0, 0.6, -0.3), (0, 0.6, -0.3), (0, 0.6, 0.0), (0, 0.5, 0.25))",
     "    path = ((0, 0.45, 0.3), (0, 0.45, 0.25), (0, 0.45, -0.1), (0, 0.45, -0.3), (0, 0.4, -0.2), (0, 0.4, 0.1), (0, 0.35, 0.25))"),
    ("        b('fin', (0.08, 0.3, 0.26), mm('mane'), (0, c.y, c.z + w / 2 + 0.1), bev=0.02)\n",
     "        b('fin', (0.08, 0.3, 0.26), mm('mane'), (0, c.y, c.z + w / 2 + 0.1), bev=0.02)\n"
     "        for sgn, n in LR:\n"
     "            p('scale', (0.04, 0.2, 0.2), mm('dark'), (sgn * (w / 2 + 0.01), c.y, c.z))\n"
     "            p('scale2', (0.04, 0.12, 0.12), mm('accent'), (sgn * (w / 2 + 0.012), c.y + 0.14, c.z + 0.12))\n"
     "        p('plate_line', (w * 0.72, 0.06, 0.06), mm('dark'), (0, c.y + 0.18, c.z - w / 2 - 0.02))\n"),
    ("    for i in range(5):\n        p('spine_glow', (0.1, 0.1, 0.1), mm('glow'), (0, 0.4 + i * 0.6, zc + 0.5 + 0.2 * math.sin(i)))\n",
     "    for i in range(5):\n        p('spine_glow', (0.1, 0.1, 0.1), mm('glow'), (0, 0.4 + i * 0.45, zc + 0.5 + 0.2 * math.sin(i)))\n"),
])
print('ok')
