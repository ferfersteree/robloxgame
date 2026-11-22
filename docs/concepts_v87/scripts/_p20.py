import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome.py', [
 ("    fp = [max(2.8, 0.95 * r['height'] + 1.4) * (1.25 if r['rarity'] >= 5 else 1.0) for r in rs]\n",
  "    foot = getattr(sys.modules.get('biome_%02d' % nn), 'FOOT', {})\n"
  "    fp = [max(2.8, 0.95 * r['height'] + 1.4) * (1.25 if r['rarity'] >= 5 else 1.0) * foot.get(r['id'], 1.0) for r in rs]\n"),
 ("    return rad, angs\n", "    return rad, angs, fp\n"),
 ("    rad, angs = _layout(nn)\n", "    rad, angs, fp = _layout(nn)\n"),
 ("    rad = radius(nn)\n    hmax = max(r['height'] for r in rows(nn))\n    cam = sc.camera\n",
  "    rad0, angs, fp = _layout(nn)\n    rad = rad0 + 0.28 * max(fp[0], fp[-1]) - 1.0\n    hmax = max(r['height'] for r in rows(nn))\n    cam = sc.camera\n"),
])
sub('biome_06.py', [
 ("BUSH_NAME = ", "FOOT = dict(canyon_condor=1.7, redthorn_lizard=1.35)\nBUSH_NAME = "),
 ("accent='#c8a482'), 1.52)", "accent='#c8a482'), 1.38)"),
 ("horn='#5a4a40'), 2.7)", "horn='#5a4a40'), 2.42)"),
 ("B, Hd = quad(bw=1.2, bl=2.0, bh=0.72, legh=0.34,", "B, Hd = quad(bw=1.2, bl=1.6, bh=0.72, legh=0.34,"),
 ("    for j in range(8):\n        y = B.front + 0.16 + j * 0.25\n        cn('thorn',", "    for j in range(8):\n        y = B.front + 0.14 + j * 0.2\n        cn('thorn',"),
 ("    for j in range(8):\n        y = B.front + 0.16 + j * 0.25\n        p('thorn_base'", "    for j in range(8):\n        y = B.front + 0.14 + j * 0.2\n        p('thorn_base'"),
 ("tail_kit('long', 'body', (0, B.back + 0.1, B.c.z), 'main', 'thorn', n=3, size=0.3, dark='dark')",
  "tail_kit('long', 'body', (0, B.back + 0.1, B.c.z), 'main', 'thorn', n=3, size=0.22, dark='dark')"),
 ("(0, B.back + 0.4 + i * 0.6, B.c.z + 0.14 + i * 0.075), (0, 0.3, 1))\n        cn('tail_thorn', 0.08, 0.26 - 0.04 * i, mm('thorn'), (0, B.back + 0.7 + i * 0.6,",
  "(0, B.back + 0.3 + i * 0.43, B.c.z + 0.11 + i * 0.055), (0, 0.3, 1))\n        cn('tail_thorn', 0.08, 0.26 - 0.04 * i, mm('thorn'), (0, B.back + 0.5 + i * 0.43,"),
 # roadrunner +16
 ("    accessory('scarf', Box((0, B.front + 0.2, B.top + 0.2), (0.5, 0.5, 0.3)), '#e8443a', '#a82a2a', z=B.top + 0.2)\n",
  "    accessory('scarf', Box((0, B.front + 0.2, B.top + 0.2), (0.5, 0.5, 0.3)), '#e8443a', '#a82a2a', z=B.top + 0.2)\n"
  "    for sgn, n in LR:\n"
  "        use('wing_' + n)\n"
  "        for j in range(4):\n"
  "            p('wing_spot', (0.04, 0.12, 0.1), mm('belly'), (sgn * (B.s.x / 2 + 0.13), B.c.y - 0.1 + j * 0.16, B.c.z + 0.1 - 0.06 * j))\n"
  "        use('leg_' + n)\n"
  "        for j in range(4):\n"
  "            p('leg_scale', (0.14, 0.14, 0.04), mm('dark'), (sgn * B.s.x * 0.24, 0.15, 0.2 + j * 0.14))\n"
  "    use('body')\n"),
 # armadillo +22
 ("    tail_kit('long', 'body', (0, B.back - 0.02, B.c.z - 0.2), 'shell', 'dark', n=2, size=0.12, dark='dark')\n",
  "    for i in range(5):\n"
  "        for j in range(2):\n"
  "            p('band_stud', (0.1, 0.06, 0.04), mm('accent'), ((i - 2) * 0.2, B.front + 0.5 + j * 0.26, B.c.z + 0.55))\n"
  "    for ft in a.bx['feet']:\n"
  "        use(ft.seg)\n"
  "        p('leg_scale', (ft.s.x + 0.02, ft.s.y * 0.7, 0.05), mm('shell'), (ft.c.x, ft.c.y + 0.06, 0.2))\n"
  "        p('leg_scale', (ft.s.x + 0.02, ft.s.y * 0.6, 0.04), mm('dark'), (ft.c.x, ft.c.y + 0.06, 0.27))\n"
  "        p('claw_big', (0.08, 0.1, 0.06), mm('belly'), (ft.c.x, ft.front - 0.02, 0.04))\n"
  "    use('body')\n"
  "    tail_kit('long', 'body', (0, B.back - 0.02, B.c.z - 0.2), 'shell', 'dark', n=2, size=0.12, dark='dark')\n"),
 # condor +16
 ("    use('body')\n    orbit_kit((0, 0.2, z0), 1.5, 6, 'glow', 'glow2', size=0.13, dz=0.3)\n    aura_kit(1.5, 5, motes=10, mote_col='glow', height=1.2)",
  "    use('body')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(4):\n"
  "            p('flank_feather', (0.05, 0.3, 0.24), mm('dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.4 + j * 0.26, B.c.z - 0.26))\n"
  "            p('thigh_feather', (0.2, 0.2, 0.14), mm('belly' if j % 2 else 'dark'), (sgn * (0.2 + 0.1 * (j % 2)), B.c.y - 0.1 + j * 0.12, B.bot - 0.04))\n"
  "    orbit_kit((0, 0.2, z0), 1.5, 6, 'glow', 'glow2', size=0.13, dz=0.3)\n    aura_kit(1.5, 5, motes=10, mote_col='glow', height=1.2)"),
])
print('ok')
