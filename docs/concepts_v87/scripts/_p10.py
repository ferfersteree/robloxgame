import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome.py', [
 ("""def radius(nn):
    return max(10.0, 7.0 + 1.0 * max(r['height'] for r in rows(nn)))


def spots(nn):
    rad = radius(nn)
    return [(round(rad * math.sin(math.radians(a)), 2), round(rad * math.cos(math.radians(a)) * 0.85 + 0.6, 2), 0) for a in ANG]
""",
"""def _layout(nn):
    \"\"\"semicircle behind the bush by rarity; every animal gets an arc share proportional to its footprint\"\"\"
    rs = rows(nn)
    fp = [max(2.8, 0.95 * r['height'] + 1.4) for r in rs]
    span = math.radians(74.0)
    rad = max(10.0, sum(fp[:3]) / span, sum(fp[3:]) / span)
    angs = []
    for side, a0 in ((fp[:3], -86.0), (fp[3:], 12.0)):
        tot = sum(side)
        cur = a0
        for f in side:
            w = 74.0 * f / tot
            angs.append(cur + w / 2)
            cur += w
    return rad, angs


def radius(nn):
    return _layout(nn)[0]


def spots(nn):
    rad, angs = _layout(nn)
    return [(round(rad * math.sin(math.radians(a)), 2), round(rad * math.cos(math.radians(a)) * 0.85 + 0.6, 2), 0) for a in angs]
"""),
])
sub('biome_03.py', [
 ("((-2.9, 0.4, 4, 3.4), (-1.6, 1.3, 3, 4.0), (0.3, 1.4, 4, 4.4), (2.3, 1.0, 3, 3.6), (3.1, -0.1, 3, 2.8), (-0.2, 0.7, 3, 4.2))",
  "((-2.9, 0.4, 4, 2.7), (-1.6, 1.3, 3, 3.3), (0.3, 1.4, 4, 3.7), (2.3, 1.0, 3, 2.9), (3.1, -0.1, 3, 2.2), (-0.2, 0.7, 3, 3.5))"),
 ("((-2.3, -0.6, 2.9), (-1.2, 0.0, 3.6), (1.0, 0.9, 3.9), (2.7, 0.5, 3.0), (0.9, -0.5, 2.4))",
  "((-2.3, -0.6, 2.3), (-1.2, 0.0, 2.9), (1.0, 0.9, 3.1), (2.7, 0.5, 2.4), (0.9, -0.5, 1.9))"),
 ("horn='#ecd9b0', snout='#553a2c'), 3.25)", "horn='#ecd9b0', snout='#553a2c'), 3.57)"),
 ("accent='#f6dcb4'), 2.3)", "accent='#f6dcb4'), 2.15)"),
 ("    for ft in a.bx['feet']:\n        p('pad', (ft.s.x * 0.6, 0.03, 0.06), mm('dark'), (ft.c.x, ft.back + 0.012, 0.06))\n    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.26)\n    return finish(a)",
  "    for ft in a.bx['feet']:\n        p('pad', (ft.s.x * 0.6, 0.03, 0.06), mm('dark'), (ft.c.x, ft.back + 0.012, 0.06))\n        p('elbow_tuft', (0.1, 0.12, 0.14), mm('dark'), (ft.c.x, ft.back + 0.1, 0.36))\n        p('leg_patch', (ft.s.x - 0.04, 0.03, 0.14), mm('belly'), (ft.c.x, ft.front + 0.07, 0.3))\n    use('head')\n    for sgn, n in LR:\n        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.2, mz.front - 0.008, mz.c.z + 0.06))\n        p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * 0.14, mz.front - 0.008, mz.c.z - 0.02))\n    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.26)\n    return finish(a)"),
 ("    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.16)\n    # rarity 4:",
  "    for ft in a.bx['feet']:\n        use(ft.seg)\n        p('leg_shag', (ft.s.x + 0.04, ft.s.y * 0.9, 0.1), mm('main'), (ft.c.x, ft.c.y + 0.02, 0.36))\n        p('leg_shag', (ft.s.x + 0.02, ft.s.y * 0.8, 0.07), mm('accent'), (ft.c.x, ft.c.y + 0.02, 0.27))\n        p('hoof_glow', (ft.s.x + 0.03, ft.s.y + 0.03, 0.035), mm('glow'), (ft.c.x, ft.c.y, ft.top + 0.01))\n    use('body')\n    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.16)\n    # rarity 4:"),
 ("**{'*glow': '#5affd0', '*glow2': '#ffe14a'}), 2.62)", "**{'*glow': '#5affd0', '*glow2': '#ffe14a'}), 2.35)"),
 ("        p('pad', (ft.s.x * 0.6, 0.03, 0.06), mm('dark'), (ft.c.x, ft.back + 0.012, 0.06))\n    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.28)",
  "        p('pad', (ft.s.x * 0.6, 0.03, 0.06), mm('dark'), (ft.c.x, ft.back + 0.012, 0.06))\n        use(ft.seg)\n        cn('leg_crystal', 0.06, 0.2, mm('glow'), (ft.c.x + (0.2 if ft.c.x > 0 else -0.2), ft.c.y + 0.1, 0.34), ((1 if ft.c.x > 0 else -1), 0, 0.6))\n        p('leg_moss', (0.14, 0.14, 0.06), mm('moss'), (ft.c.x, ft.c.y + 0.1, 0.52))\n        use('body')\n    for sgn, n in LR:\n        cn('shoulder_spike', 0.12, 0.3, mm('stone'), (sgn * (B.s.x / 2 - 0.1), B.front + 0.3, B.top + 0.02), (sgn * 0.6, -0.2, 1))\n        cn('shoulder_spike', 0.09, 0.22, mm('stone'), (sgn * (B.s.x / 2 - 0.06), B.front + 0.6, B.top + 0.02), (sgn * 0.7, 0, 1))\n    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.28)"),
 ("**{'*glow': '#5affd0', '*glow2': '#fff6a0', '*gold': '#ffd84a'}), 3.75)", "**{'*glow': '#5affd0', '*glow2': '#fff6a0', '*gold': '#ffd84a'}), 4.4)"),
])
print('ok')
