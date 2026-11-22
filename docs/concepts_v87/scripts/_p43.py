import io


def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:70])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


sub('biome_18.py', [
    ("""    for i, (w, d, h) in enumerate(((2.2, 2.2, 0.5), (1.9, 1.9, 0.5), (1.5, 1.5, 0.5))):
        b('shell', (w, d, h), mm('shell' if i % 2 == 0 else 'shell2'), (0, B.c.y, B.top + 0.2 + i * 0.5), bev=0.08)
    for sgn, n in LR:
        b('frame_side', (0.2, 1.2, 1.2), mm('shell2'), (sgn * 0.6, B.c.y, B.top + 1.9), bev=0.05)
    b('frame_top', (1.4, 1.2, 0.2), mm('shell2'), (0, B.c.y, B.top + 2.6), bev=0.05)
    b('void', (1.0, 1.0, 1.0), mm('void'), (0, B.c.y, B.top + 1.9), bev=0.02)
    for i in range(6):
        for sgn, n in LR:
            p('shell_rim', (0.24, 0.24, 0.12), mm('accent'), (sgn * 1.1, B.c.y - 0.9 + i * 0.36, B.top + 0.22))
    grid(Box((0, B.c.y, B.top + 0.2), (2.2, 2.2, 0.5)), 'f', 5, 1, mm('shell2'), (0.24, 0.24), name='front_plate', span=(0.9, 0.1))
    grid(Box((0, B.c.y, B.top + 0.2), (2.2, 2.2, 0.5)), 'k', 5, 1, mm('shell2'), (0.24, 0.24), name='back_plate', span=(0.9, 0.1))
""", """    for i, (w, d, h) in enumerate(((2.7, 2.5, 0.4), (2.2, 2.0, 0.4), (1.6, 1.5, 0.3))):
        b('shell', (w, d, h), mm('shell' if i % 2 == 0 else 'shell2'), (0, B.c.y, B.top + 0.15 + i * 0.38), bev=0.08)
    # a portal arch standing across the back, open to the front, filled with a starry void (the silhouette)
    PZ = B.top + 1.65
    for sgn, n in LR:
        b('arch_side', (0.26, 0.34, 1.3), mm('shell2'), (sgn * 0.76, B.c.y, PZ), bev=0.05)
        b('arch_foot', (0.4, 0.5, 0.16), mm('shell'), (sgn * 0.76, B.c.y, PZ - 0.62), bev=0.04)
    b('arch_top', (1.8, 0.34, 0.26), mm('shell2'), (0, B.c.y, PZ + 0.74), bev=0.05)
    b('arch_key', (0.34, 0.4, 0.34), mm('accent'), (0, B.c.y, PZ + 0.9), rot=(0, 45, 0), bev=0.04)
    b('void', (1.26, 0.12, 1.2), mm('void'), (0, B.c.y, PZ), bev=0.02)
    for i in range(6):
        for sgn, n in LR:
            p('shell_rim', (0.24, 0.24, 0.12), mm('accent'), (sgn * 1.35, B.c.y - 0.95 + i * 0.38, B.top + 0.17))
    grid(Box((0, B.c.y, B.top + 0.15), (2.7, 2.5, 0.4)), 'f', 5, 1, mm('shell2'), (0.24, 0.24), name='front_plate', span=(0.9, 0.1))
    grid(Box((0, B.c.y, B.top + 0.15), (2.7, 2.5, 0.4)), 'k', 5, 1, mm('shell2'), (0.24, 0.24), name='back_plate', span=(0.9, 0.1))
"""),
    ("    SB = Box((0, B.c.y, B.top + 0.7), (1.9, 1.9, 0.5))\n", "    SB = Box((0, B.c.y, B.top + 0.53), (2.2, 2.0, 0.4))\n"),
    ("""    sg('glow', 'body', (0, B.c.y, B.top + 1.9))""", """    sg('glow', 'body', (0, B.c.y, PZ))"""),
    ("""        p('void_star', (s, s, s), mm('star' if i % 2 else 'glow2'), (x, B.c.y + y, B.top + 1.9 + z), rot=(45, 45, 0))""",
     """        for side in (-1, 1):
            p('void_star', (s, s, s), mm('star' if i % 2 else 'glow2'), (x * 1.4, B.c.y + side * 0.07, PZ + z), rot=(45, 45, 0))"""),
    ("""            p('frame_gem', (0.06, 0.14, 0.14), mm('glow'), (sgn * 0.71, B.c.y - 0.4 + j * 0.4, B.top + 1.9), rot=(45, 0, 0))""",
     """            p('frame_gem', (0.14, 0.06, 0.14), mm('glow'), (sgn * 0.76, B.c.y - 0.18, PZ - 0.4 + j * 0.4), rot=(0, 45, 0))"""),
])
print('ok')
