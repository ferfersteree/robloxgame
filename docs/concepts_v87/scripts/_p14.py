import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('moves.py', [
 ("            if any(abs(u - v) > 1e-4 for u, v in zip(last[fld], restv)):\n                kk(c, s, L_, **{fld: restv})\n",
  "            if fld == 'rot':\n"
  "                # a whole number of turns is the rest pose too: never unwind it\n"
  "                if all(abs(u / 360.0 - round(u / 360.0)) < 1e-4 for u in last[fld]):\n"
  "                    continue\n"
  "                kk(c, s, L_, rot=tuple(360.0 * round(u / 360.0) for u in last[fld]))\n"
  "            elif any(abs(u - v) > 1e-4 for u, v in zip(last[fld], restv)):\n"
  "                kk(c, s, L_, **{fld: restv})\n"),
 ("    cand = [x for x in ('leg_fR', 'leg_R', 'leg_1R') if x in a.segs] + a.arms + a.legs\n    l = cand[0]\n",
  "    cand = [x for x in ('leg_fR', 'leg_R', 'leg_1R') if x in a.segs] + a.arms + a.legs + ['body']\n    l = cand[0]\n"),
 ("    arm = ([l for l in a.arms if l.endswith('R')] or [l for l in a.legs if l.endswith('R')])[0]\n",
  "    arm = ([l for l in a.arms if l.endswith('R')] or [l for l in a.legs if l.endswith('R')] or a.wings or ['body'])[0]\n"),
])
sub('verify_out.py', [
 ("        for sname, ch in c['keys']['Idle'].items():\n            for key2 in ('loc', 'rot', 'scale'):",
  "        for sname, ch in c['keys']['Reveal'].items():\n"
  "            rr = ch.get('rot') or []\n"
  "            for q0, q1 in zip(rr, rr[1:]):\n"
  "                # no unwinding: a segment must not spin back by a full turn or more between two keys unless it is a fast spin move\n"
  "                if sname != 'root' and any(q1[i] - q0[i] <= -360 or q1[i] - q0[i] >= 720 for i in (1, 2, 3)) and q1[0] == c['reveal_frames']:\n"
  "                    errs.append('Reveal %s unwinds %s -> %s on the last key' % (sname, q0[1:4], q1[1:4]))\n"
  "        for sname, ch in c['keys']['Idle'].items():\n            for key2 in ('loc', 'rot', 'scale'):"),
])
sub('biome_04.py', [
 ("accent='#6e4e3a', horn='#f2e6cc'), 2.1)", "accent='#6e4e3a', horn='#f2e6cc'), 1.92)"),
 ("**{'*glow': '#7fe0ff', '*glow2': '#fff6a0'}), 3.0)", "**{'*glow': '#7fe0ff', '*glow2': '#fff6a0'}), 2.78)"),
 ("**{'*glow': '#7fe0ff', '*glow2': '#fff6a0', '*gold': '#ffd84a'}), 3.25)", "**{'*glow': '#7fe0ff', '*glow2': '#fff6a0', '*gold': '#ffd84a'}), 3.6)"),
 ("        p('leg_glow', (ft.s.x + 0.04, ft.s.y * 0.8, 0.04), mm('glow'), (ft.c.x, ft.c.y + 0.04, 0.44))\n    use('body')\n",
  "        p('leg_glow', (ft.s.x + 0.04, ft.s.y * 0.8, 0.04), mm('glow'), (ft.c.x, ft.c.y + 0.04, 0.44))\n"
  "        p('leg_stripe', (ft.s.x + 0.02, 0.1, 0.2), mm('accent'), (ft.c.x, ft.front + 0.2, 0.26))\n"
  "        p('toe_frost', (ft.s.x * 0.7, 0.1, 0.04), mm('snow'), (ft.c.x, ft.front + 0.08, ft.top + 0.01))\n"
  "    use('head')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(2):\n"
  "            p('tusk_band', (0.2, 0.08, 0.2), mm('accent'), (sgn * 0.36, Hd.front - 0.3 - 0.2 * j, Hd.bot + 0.09))\n"
  "        p('cheek_frost', (0.16, 0.2, 0.2), mm('snow'), (sgn * (Hd.s.x / 2 + 0.02), Hd.front + 0.3, Hd.c.z - 0.34))\n"
  "        p('cheek_frost', (0.12, 0.16, 0.14), mm('snow'), (sgn * (Hd.s.x / 2 + 0.03), Hd.front + 0.5, Hd.c.z - 0.44))\n"
  "    for i in range(5):\n"
  "        p('chin_icicle', (0.08, 0.08, 0.16 + 0.06 * (i % 2)), mm('glow'), ((i - 2) * 0.2, Hd.front + 0.2, Hd.bot - 0.08))\n"
  "    use('body')\n"
  "    for i in range(5):\n"
  "        p('belly_icicle', (0.1, 0.1, 0.2 + 0.08 * (i % 2)), mm('glow'), ((i - 2) * 0.22, B.c.y - 0.3 + 0.16 * (i % 2), B.bot - 0.12))\n"),
 ("    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('ankle_fur', (ft.s.x + 0.06, ft.s.y * 0.7, 0.16), mm('main'), (ft.c.x, ft.c.y + 0.12, ft.top + 0.1))\n",
  "    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('ankle_fur', (ft.s.x + 0.06, ft.s.y * 0.7, 0.16), mm('main'), (ft.c.x, ft.c.y + 0.12, ft.top + 0.1))\n"
  "        for j in range(3):\n"
  "            p('leg_fur', (0.14, 0.2, 0.16), mm('accent' if j % 2 else 'main'), (ft.c.x + (0.26 if ft.c.x > 0 else -0.26), ft.c.y + 0.2, 0.24 + j * 0.1))\n"
  "        p('toe_claw', (ft.s.x * 0.8, 0.06, 0.05), mm('glow2'), (ft.c.x, ft.front + 0.0, 0.03))\n"),
 ("    use('body')\n    # rarity 6: frost constellation on the belly",
  "    use('head')\n"
  "    for i in range(5):\n"
  "        p('nape_fur', (0.24, 0.14, 0.24), mm('accent' if i % 2 else 'main'), ((i - 2) * 0.24, Hd.back + 0.04, Hd.c.z - 0.2 + 0.08 * (i % 2)))\n"
  "    for sgn, n in LR:\n"
  "        p('ear', (0.1, 0.16, 0.2), mm('face'), (sgn * (Hd.s.x / 2 + 0.03), Hd.c.y - 0.1, Hd.c.z + 0.1))\n"
  "        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.3, Hd.front - 0.08, Hd.c.z - 0.14))\n"
  "        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.38, Hd.front - 0.08, Hd.c.z - 0.1))\n"
  "    use('body')\n"
  "    for i in range(6):\n"
  "        p('chest_fur', (0.22, 0.1, 0.18), mm('accent'), ((i % 3 - 1) * 0.5, B.front - 0.04, B.top - 0.14 - 0.2 * (i // 3)))\n"
  "    # rarity 6: frost constellation on the belly"),
])
print('ok')
