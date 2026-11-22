import io
s = io.open('moves.py', encoding='utf-8').read()
a = "    kk(c, 'root', 1, loc=(0, D * 0.4, hz), scale=(0.0, 1.0, 1.0), ease='CONSTANT')\n    kk(c, 'root', 6, loc=(0, D * 0.4, hz), scale=(0.0, 1.0, 1.0))\n"
assert a in s
s = s.replace(a, "    kk(c, 'root', 1, loc=(0, D * 0.4, hz), scale=0.0, ease='CONSTANT')\n    kk(c, 'root', 6, loc=(0, D * 0.4, hz), scale=(0.02, 1.0, 1.0))\n")
io.open('moves.py', 'w', encoding='utf-8', newline='\n').write(s)
