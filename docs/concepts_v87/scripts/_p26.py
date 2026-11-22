import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_08.py', [
 ("accent='#c8d0dc', face='#4a4e5a', leaf='#3fbe5a',", "accent='#c8d0dc', face='#7a7e8c', leaf='#3fbe5a',"),
 ("    b('brow_ridge', (0.96, 0.2, 0.16), mm('main'), (0, Hd.front + 0.04, Hd.c.z + 0.34), bev=0.05)",
  "    b('brow_ridge', (0.96, 0.16, 0.12), mm('main'), (0, Hd.front + 0.02, Hd.c.z + 0.42), bev=0.04)"),
 ("    eyes(Hd, 0.28, 0.2, 0.08, iris='#2a8a4a', glow='#5aff8a', brow=None, tilt=0)", "    eyes(Hd, 0.3, 0.2, 0.1, iris='#2a8a4a', glow='#5aff8a', brow=None, tilt=0)"),
 ("        p('cheek_paint', (0.2, 0.04, 0.06), mm('glow'), (sgn * 0.3, Hd.front - 0.08, Hd.c.z - 0.02), rot=(0, sgn * 20, 0))\n        p('cheek_paint', (0.14, 0.04, 0.05), mm('glow'), (sgn * 0.3, Hd.front - 0.08, Hd.c.z - 0.12), rot=(0, sgn * 20, 0))",
  "        p('cheek_paint', (0.14, 0.04, 0.05), mm('glow'), (sgn * 0.36, Hd.front - 0.08, Hd.c.z - 0.2), rot=(0, sgn * 20, 0))\n        p('cheek_paint', (0.1, 0.04, 0.05), mm('glow'), (sgn * 0.36, Hd.front - 0.08, Hd.c.z - 0.28), rot=(0, sgn * 20, 0))"),
])
print('ok')
