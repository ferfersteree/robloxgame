import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('moves.py', [
 ("            on_ = (i % 2 == 1) if j % 2 == 0 else (i % 2 == 0 and 0 < i < 7)\n",
  "            on_ = ((i % 2 == 1) if j % 2 == 0 else (i % 2 == 0)) and 0 < i < 7\n"),
 ("    kk(c, 'root', L_, loc=(0, 0, 0), scale=1.0)\n",
  "    kk(c, 'root', L_, loc=(0, 0, 0), scale=1.0)\n"
  "    # safety net: every segment is back at rest on the last frame\n"
  "    for s, keys in list(G.keys[c].items()):\n"
  "        if s == 'root' or s.startswith('fxs_'):\n"
  "            continue\n"
  "        for fld, restv in (('loc', (0, 0, 0)), ('rot', (0, 0, 0)), ('scale', (1.0, 1.0, 1.0))):\n"
  "            ks = [d for d in keys if d[fld] is not None]\n"
  "            if not ks:\n"
  "                continue\n"
  "            last = max(ks, key=lambda d: d['f'])\n"
  "            if any(abs(u - v) > 1e-4 for u, v in zip(last[fld], restv)):\n"
  "                kk(c, s, max(L_, last['f'] + 2) if last['f'] >= L_ - 1 else L_, **{fld: restv})\n"),
])
print('ok')
