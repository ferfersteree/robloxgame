import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('biome.py', [
 ("    L.ground(m.GROUND)\n",
  "    gr = L.ground(m.GROUND)\n    for nd in gr.data.materials[0].node_tree.nodes:\n        if nd.type == 'GROUP':\n            nd.inputs['Color'].default_value = L.H(m.GROUND)\n"),
 ("    fp = [max(2.8, 0.95 * r['height'] + 1.4) for r in rs]\n",
  "    fp = [max(2.8, 0.95 * r['height'] + 1.4) * (1.25 if r['rarity'] >= 5 else 1.0) for r in rs]\n"),
])
sub('biome_04.py', [
 ("GROUND = '#cfe2ea'", "GROUND = '#8fb4c8'"),
 ("    orbit_kit((0, 0.2, 1.7), 1.9, 6, 'glow', 'glow2', size=0.14, dz=0.5, shape='cross')\n    aura_kit(1.9, 5, motes=10, mote_col='glow', height=2.2)",
  "    orbit_kit((0, 0.2, 1.7), 1.4, 6, 'glow', 'glow2', size=0.14, dz=0.5, shape='cross')\n    aura_kit(1.45, 5, motes=10, mote_col='glow', mote_r=1.5, height=2.2)"),
 ("    orbit_kit((0, 0.05, 1.5), 1.9, 6, 'glow', 'glow2', size=0.15, dz=0.5, shape='cross')\n    orbit_kit((0, 0.05, 0.9), 2.3, 8, 'gold', 'glow', size=0.1, name='orbit2', dz=0.2, shape='ring')\n    aura_kit(1.9, 6, motes=12, mote_col='glow', height=2.6)",
  "    orbit_kit((0, 0.05, 1.5), 1.5, 6, 'glow', 'glow2', size=0.15, dz=0.5, shape='cross')\n    orbit_kit((0, 0.05, 0.9), 1.8, 8, 'gold', 'glow', size=0.1, name='orbit2', dz=0.2, shape='ring')\n    aura_kit(1.5, 6, motes=12, mote_col='glow', mote_r=1.6, height=2.6)"),
 ("a = start(row, dict(main='#f4f8ff', belly='#cfe6f6',", "a = start(row, dict(main='#eef4ff', belly='#cfe6f6',"),
])
print('ok')
