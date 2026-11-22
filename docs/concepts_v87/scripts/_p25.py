import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_08.py', [
 ("    for i in range(6):\n        p('chest_hair',",
  "    for i in range(8):\n        p('hip_fur', (0.2, 0.12, 0.16), mm('dark' if i % 2 else 'main'), ((i - 3.5) * 0.2, B.back + 0.06, B.bot + 0.1))\n"
  "    for i in range(6):\n        p('chest_hair',"),
 ("    for i in range(4):\n        for j in range(2):\n            p('wart',",
  "    for i in range(5):\n        for sgn, n in LR:\n            p('back_stripe', (0.08, 0.14, 0.04), mm('gold'), (sgn * 0.5, B.c.y - 0.3 + i * 0.16, B.top + 0.03))\n"
  "    for i in range(4):\n        for j in range(2):\n            p('wart',"),
])
print('ok')
