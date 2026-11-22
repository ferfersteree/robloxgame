import io
s = io.open('biome.py', encoding='utf-8').read()
a = "    rad = rad0 + 0.28 * max(fp[0], fp[-1]) - 1.0\n"
assert a in s
s = s.replace(a, "    rad = rad0 + 0.1 * max(fp[0], fp[-1]) - 1.0\n")
io.open('biome.py', 'w', encoding='utf-8', newline='\n').write(s)
