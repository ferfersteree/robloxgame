import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_20.py', [
    ("'*glow2': '#ff6a6a'}), 4.5)", "'*glow2': '#ff6a6a'}), 4.8)"),
    ("        for t in range(3):\n            q = 0.25 + t * 0.25\n", "        for t in range(5):\n            q = 0.15 + t * 0.17\n"),
    ("        p('foot_magnet', (0.3, 0.3, 0.06), mm('accent'), (fx, fy, 0.16))\n",
     "        p('foot_magnet', (0.3, 0.3, 0.06), mm('accent'), (fx, fy, 0.16))\n"
     "        for t in range(3):\n"
     "            ta = r + math.radians((t - 1) * 40)\n"
     "            p('foot_claw', (0.1, 0.1, 0.08), mm('silver'), (fx + math.cos(ta) * 0.24, fy + math.sin(ta) * 0.24, 0.04))\n"),
    ("    grid(B, 'k', 3, 2, mm('dark'), (0.08, 0.08), name='vent', span=(0.6, 0.5))\n",
     "    grid(B, 'k', 3, 2, mm('dark'), (0.08, 0.08), name='vent', span=(0.6, 0.5))\n"
     "    grid(Box((0, 0, zb - 0.4), (1.36, 1.36, 0.2)), 'u', 3, 3, mm('silver'), (0.12, 0.12), name='under_light', span=(0.7, 0.7))\n"
     "    for k_ in range(8):\n"
     "        ang = math.radians(k_ * 45 + 22)\n"
     "        p('top_light', (0.1, 0.1, 0.06), mm('accent' if k_ % 2 else 'bolt'), (math.cos(ang) * 0.4, math.sin(ang) * 0.4, zb + 0.46))\n"),
    ("    b('magnet_base', (1.2, 0.34, 0.3), mm('accent'), (0, 0, zb + 0.6), bev=0.05)\n",
     "    b('magnet_base', (1.2, 0.34, 0.3), mm('accent'), (0, 0, zb + 0.6), bev=0.05)\n"
     "    for sgn in (-1, 1):\n"
     "        for t in range(2):\n"
     "            p('magnet_stripe', (0.32, 0.36, 0.05), mm('belly'), (sgn * 0.45, 0, zb + 0.85 + t * 0.25))\n"),
    ("    for i in range(6):\n        ang = math.radians(i * 60)\n        x, y, z = math.cos(ang) * 0.5",
     "    for i in range(8):\n        ang = math.radians(i * 45)\n        x, y, z = math.cos(ang) * 0.5"),
])
print('ok')
