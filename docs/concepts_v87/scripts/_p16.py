import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('faunalib.py', [("    gl.threshold = 1.2\n", "    gl.threshold = 1.9\n")])
sub('biome_04.py', [("a = start(row, dict(main='#eef4ff', belly='#cfe6f6',", "a = start(row, dict(main='#dde7f6', belly='#bcd8ee',")])
print('ok')
