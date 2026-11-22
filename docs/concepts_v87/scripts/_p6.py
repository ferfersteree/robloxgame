import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_02.py', [
 ("    B, Hd = quad(bw=1.02, bl=1.5, bh=0.62,", "    B, Hd = quad(bw=1.02, bl=1.26, bh=0.62,"),
 ("    cheeks(Hd, 'belly', (0.3, 0.26, 0.32), -0.26, whisk=3)\n    eyes(Hd, 0.33, 0.25, 0.1, iris='#3a8a2a', glow='#c8ff5a', brow='#8e4a1a'",
  "    cheeks(Hd, 'belly', (0.3, 0.26, 0.32), -0.26, whisk=3)\n    for sgn, n in LR:\n        for j in range(3):\n            p('freckle', (0.04, 0.03, 0.04), mm('dark'), (sgn * (0.12 + 0.07 * j), mz.front - 0.008, mz.c.z + 0.02 + 0.05 * (j % 2)))\n    eyes(Hd, 0.33, 0.25, 0.1, iris='#3a8a2a', glow='#c8ff5a', brow='#8e4a1a'"),
])
print('ok')
