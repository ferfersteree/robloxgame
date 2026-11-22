import io
s = io.open('biome.py', encoding='utf-8').read()
a = "    cam.location = (0, -2.1 * rad, 1.45 * rad)\n    d = Vector((0, 0.34 * rad, 0.12 * rad + 0.1 * hmax)) - cam.location\n"
assert a in s
s = s.replace(a, "    cam.location = (0, -1.75 * rad, 1.3 * rad)\n    d = Vector((0, 0.4 * rad, 0.05 * rad + 0.12 * hmax)) - cam.location\n")
io.open('biome.py', 'w', encoding='utf-8', newline='\n').write(s)
