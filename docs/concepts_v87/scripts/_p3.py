import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)

sub('moves.py', [
 ("    l = (a.legs or a.arms)[-1 if not a.legs else 1 if len(a.legs) > 1 else 0]\n",
  "    cand = [x for x in ('leg_fR', 'leg_R', 'leg_1R') if x in a.segs] + a.arms + a.legs\n    l = cand[0]\n"),
 ("    kk(c, 'root', f0, rot=(0, 0, 0), loc=(0, 0, 0))\n    kk(c, 'root', _t(f0, n, 0.85), rot=(0, 0, 360), loc=(0, 0, 0))\n",
  "    kk(c, 'root', f0, rot=rb(a, 0), loc=(0, 0, 0))\n    kk(c, 'root', _t(f0, n, 0.85), rot=rb(a, 360), loc=(0, 0, 0))\n"),
 ("    kk(c, 'root', f0, rot=(0, 0, 0))\n    kk(c, 'root', _t(f0, n, 0.35), rot=(0, 0, 40))\n    kk(c, 'root', _t(f0, n, 0.7), rot=(0, 0, 40))\n    kk(c, 'root', f0 + n, rot=(0, 0, 0))\n",
  "    kk(c, 'root', f0, rot=rb(a, 0))\n    kk(c, 'root', _t(f0, n, 0.35), rot=rb(a, 40))\n    kk(c, 'root', _t(f0, n, 0.7), rot=rb(a, 40))\n    kk(c, 'root', f0 + n, rot=rb(a, 0))\n"),
 ("    kk(c, 'root', f0, rot=(0, 0, 0))\n    kk(c, 'root', _t(f0, n, 0.9), rot=(0, 0, 360))\n",
  "    kk(c, 'root', f0, rot=rb(a, 0))\n    kk(c, 'root', _t(f0, n, 0.9), rot=rb(a, 360))\n"),
 ("def has(a, s):\n", "def rb(a, dz):\n    \"\"\"root rotation = where the method left it (may be a multiple of 360) + extra yaw\"\"\"\n    r = a.rbase\n    return (r[0], r[1], r[2] + dz)\n\n\ndef has(a, s):\n"),
 ("    T = METHODS[a.method](a, c)\n",
  "    a.rbase = (0, 0, 0)\n    T = METHODS[a.method](a, c)\n    rk = [d for d in G.keys[c].get('root', []) if d['rot'] is not None]\n    if rk:\n        a.rbase = max(rk, key=lambda d: d['f'])['rot']\n"),
 ("    rz = getattr(a, 'root_rot_end', None)\n    last = {}\n    for s, keys in G.keys[c].items():\n        pass\n", ""),
])
sub('kits.py', [
 ("    a.glow, a.orbits, a.fx_notes = [], [], []\n    return a\n",
  "    a.glow, a.orbits, a.fx_notes = [], [], []\n    bs = getattr(K, 'bush', (7.0, 3.6, 4.6))\n    a.bush_h, a.bush_depth = bs[2], bs[1]\n    a.cover = round(max(1.0, 1.12 * a.H / bs[2]), 2)\n    a.len_est = a.H * 0.9\n    return a\n"),
 ("rarity=a.rarity, kind=a.kind,\n", "rarity=a.rarity, kind=a.kind, cover=a.cover, reveal=a.reveal_len, idle=a.idle_len,\n"),
])
print('ok')
