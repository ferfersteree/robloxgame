import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_19.py', [
    ("        ang = math.radians(80 - i * 32)\n        r = 0.95\n", "        ang = math.radians(95 - i * 20)\n        r = 0.95\n"),
    ("rot=(0, 0, -i * 32), bev=0.08)", "rot=(0, 0, -i * 20), bev=0.08)"),
    ("        ang = math.radians(60 - i * 32)\n        p('tail_spark'", "        ang = math.radians(70 - i * 22)\n        p('tail_spark'"),
    ("    Hd = Box((0, 0, zc + 0.05), (0.9, 0.5, 0.8), 'body')\n", "    Hd = Box((0, -0.08, zc + 0.05), (0.9, 0.5, 0.8), 'body')\n"),
    ("    p('smile', (0.24, 0.03, 0.04), mm('dark'), (0, -0.27, zc - 0.16))", "    p('smile', (0.24, 0.03, 0.04), mm('dark'), (0, -0.335, zc - 0.16))"),
    ("        p('blush', (0.12, 0.03, 0.06), mm('dark'), (sgn * 0.26, -0.27, zc - 0.08))", "        p('blush', (0.12, 0.03, 0.06), mm('dark'), (sgn * 0.26, -0.335, zc - 0.08))"),
])
print('ok')
