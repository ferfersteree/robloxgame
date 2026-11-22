import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('kits.py', [
 ("         leg_fl=None, leg_back_x=None):", "         leg_fl=None, leg_back_x=None, head_mat='main'):"),
 ("    Hd = b('head', (hw, hd, hh), mm('main'), hc)\n    b('head_top', (hw * 0.74, hd * 0.7, 0.08), mm('main'), (0, hc[1], hc[2] + hh / 2 + 0.02), bev=0.03)\n    lx = bw / 2",
  "    Hd = b('head', (hw, hd, hh), mm(head_mat), hc)\n    b('head_top', (hw * 0.74, hd * 0.7, 0.08), mm(head_mat), (0, hc[1], hc[2] + hh / 2 + 0.02), bev=0.03)\n    lx = bw / 2"),
 ("    if rump:\n        b('rump', (bw * 1.06, bl * 0.36, bh * 0.86), mm('main'), (0, by + bl * 0.36, zb - bh * 0.05))\n",
  "    if rump:\n        a.bx['rump'] = b('rump', (bw * 1.06, bl * 0.36, bh * 0.86), mm('main'), (0, by + bl * 0.36, zb - bh * 0.05))\n"),
 ("    if chest:\n        b('chest', (bw * 0.72, 0.14, bh * 0.82), mm('belly'), (0, by - bl / 2 - 0.03, zb - bh * 0.04))\n",
  "    if chest:\n        a.bx['chest'] = b('chest', (bw * 0.72, 0.14, bh * 0.82), mm('belly'), (0, by - bl / 2 - 0.03, zb - bh * 0.04))\n"),
 ("    c = (0, hb.front - size[1] / 2 + 0.02, hb.c.z + dz * hb.s.z)\n    mz = b(name,", "    use(hb.seg or 'head')\n    c = (0, hb.front - size[1] / 2 + 0.02, hb.c.z + dz * hb.s.z)\n    mz = b(name,"),
 ("    z = hb.c.z + dz * hb.s.z\n    for sgn, n in LR:\n        x = sgn * (hb.s.x / 2 - size[0] * 0.25)", "    use(hb.seg or 'head')\n    z = hb.c.z + dz * hb.s.z\n    for sgn, n in LR:\n        x = sgn * (hb.s.x / 2 - size[0] * 0.25)"),
 ("    for sgn, nn in LR:\n        bx = sgn * x * hb.s.x\n        if kind == 'cone':", "    use(seg_parent)\n    for sgn, nn in LR:\n        bx = sgn * x * hb.s.x\n        if kind == 'cone':"),
])
print('ok')
