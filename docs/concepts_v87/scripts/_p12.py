import io
s = io.open('moves.py', encoding='utf-8').read()
a = "    n = 40 + 4 * a.rarity\n    clip(c, n)"
assert a in s
s = s.replace(a, "    n = min(60, 40 + 4 * a.rarity)\n    clip(c, n)")
io.open('moves.py', 'w', encoding='utf-8', newline='\n').write(s)
