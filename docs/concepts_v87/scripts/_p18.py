import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome_05.py', [
 ("accent='#b88a54'), 2.2)", "accent='#b88a54'), 2.0)"),
 ("**{'*glow': '#ffb020'}), 2.5)", "**{'*glow': '#ffb020'}), 2.3)"),
 ("**{'*glow': '#ffb020', '*glow2': '#fff0a0', '*gold': '#ffd84a'}), 5.1)", "**{'*glow': '#ffb020', '*glow2': '#fff0a0', '*gold': '#ffd84a'}), 5.9)"),
 ("    accessory('bow', Box((0, Hd.c.y + 0.06, Hd.bot - 1.0), (0.5, 0.5, 0.2)), '#ffb020', '#e8782a', z=Hd.bot - 0.98)\n",
  "    accessory('bow', Box((0, Hd.c.y + 0.06, Hd.bot - 1.0), (0.5, 0.5, 0.2)), '#ffb020', '#e8782a', z=Hd.bot - 0.98)\n"
  "    use('body')\n"
  "    for sgn, n in LR:\n"
  "        for j in range(4):\n"
  "            p('side_feather', (0.05, 0.26, 0.22), mm('dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.42 + j * 0.2, B.c.z - 0.3))\n"
  "            p('rump_plume', (0.2, 0.2, 0.2), mm('belly'), (sgn * (0.16 + 0.14 * (j % 2)), B.back + 0.3 + 0.05 * j, B.c.z + 0.3 - 0.14 * j))\n"),
])
print('ok')
