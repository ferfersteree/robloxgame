# second round of look-alike fixes: bison (vs bear), storm_ram (vs mountain_goat), geode_mole (vs rock_hyrax)
from redo_dragons import splice

BISON = r'''
def bison(row):
    """swamp bison: front-heavy wedge - a giant golden shaggy mane cloak over the front half with the face peeking out low,
    slim charcoal hindquarters, wide crescent horns sweeping sideways"""
    a = start(row, dict(main='#3a3438', belly='#5a5258', dark='#24202a', accent='#e0a85a', mane='#d8963a', mane2='#f0c070', horn='#f6ecd8',
                        **{'*glow': '#5affd0'}), 2.12)
    B, Hd = quad(bw=1.0, bl=1.5, bh=0.8, legh=0.48, lw=0.26, hw=1.0, hd=0.9, hh=0.86, head_up=0.06, hoof='dark', leg_mat='dark',
                 head_mat='main', head_fwd=0.5, rump=True, chest=False)
    use('body')
    # the mane cloak: a big stepped block hugging the front half of the body, taller than the head (the silhouette)
    b('mane', (1.6, 0.9, 1.5), mm('mane'), (0, B.front + 0.3, B.c.z + 0.3), bev=0.16)
    b('mane_top', (1.2, 0.7, 0.4), mm('mane2'), (0, B.front + 0.34, B.c.z + 1.16), bev=0.12)
    for sgn, n in LR:
        for j in range(4):
            b('mane_lock', (0.16, 0.3, 0.5 - 0.06 * j), mm('mane' if j % 2 else 'mane2'), (sgn * 0.82, B.front + 0.0 + j * 0.2, B.c.z - 0.1 - 0.12 * j), bev=0.04)
    for i in range(5):
        b('mane_fringe', (0.28, 0.14, 0.34 + 0.08 * (i % 2)), mm('mane2'), ((i - 2) * 0.3, B.front - 0.16, B.c.z - 0.36), bev=0.04)
    grid(Box((0, B.front + 0.3, B.c.z + 0.3), (1.6, 0.9, 1.5)), 'l', 3, 3, mm('mane2'), (0.14, 0.14), name='mane_tuft', th=0.06)
    grid(Box((0, B.front + 0.3, B.c.z + 0.3), (1.6, 0.9, 1.5)), 'r', 3, 3, mm('mane2'), (0.14, 0.14), name='mane_tuft', th=0.06)
    # slim dark hindquarters with a light saddle line
    p('saddle_line', (0.2, 0.8, 0.04), mm('belly'), (0, B.back - 0.4, B.top + 0.01))
    grid(a.bx['rump'], 'k', 2, 2, mm('belly'), (0.12, 0.12), name='rump_spot')
    use('head')
    mz = muzzle(Hd, (0.56, 0.3, 0.32), -0.28, 'belly', nose=(0.26, 0.1, 0.14), nose_mat='dark')
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.22))
        # wide crescent horns sweeping out sideways
        for j in range(4):
            b('horn', (0.32, 0.18 - 0.02 * j, 0.18 - 0.02 * j), mm('horn'), (sgn * (Hd.s.x / 2 + 0.12 + j * 0.26), Hd.c.y, Hd.top - 0.02 + 0.03 * j * j), rot=(0, -sgn * 10 * j, 0), bev=0.04)
    eyes(Hd, 0.3, 0.25, 0.1, iris='#2a6a5a', glow='#5affd0', brow='#24202a', tilt=-10)
    for i in range(4):
        b('forelock', (0.22, 0.2, 0.22), mm('mane2'), ((i - 1.5) * 0.24, Hd.front + 0.14, Hd.top + 0.04), bev=0.05)
    b('beard', (0.44, 0.24, 0.4), mm('mane'), (0, Hd.front + 0.16, Hd.bot - 0.16), bev=0.06)
    use('body')
    for ft in a.bx['feet']:
        use(ft.seg)
        p('hoof_glow', (ft.s.x + 0.03, ft.s.y + 0.03, 0.035), mm('glow'), (ft.c.x, ft.c.y, ft.top + 0.01))
        p('leg_band', (ft.s.x + 0.02, ft.s.y * 0.8, 0.06), mm('belly'), (ft.c.x, ft.c.y + 0.02, 0.3))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'mane', size=0.16)
    # rarity 4: glowing runes on the mane cloak, glowing horn tips, sparks
    sg('glow', 'body', (0, B.front + 0.3, B.c.z + 0.3))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(3):
            p('mane_rune', (0.06, 0.16, 0.16), mm('glow'), (sgn * 0.81, B.front + 0.1 + j * 0.3, B.c.z + 0.5), rot=(45, 0, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow_h')
    for sgn, n in LR:
        p('horn_tip', (0.16, 0.14, 0.14), mm('glow'), (sgn * (Hd.s.x / 2 + 0.12 + 3 * 0.26 + 0.14), Hd.c.y, Hd.top + 0.27))
    use('body')
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=1.8)
    return finish(a)
'''

RAM = r'''
def storm_ram(row):
    """storm ram: sleek slate-grey short coat (no wool), zig-zag lightning horns pointing up, a little thundercloud
    floating as a forelock and as its tail"""
    a = start(row, dict(main='#5a6478', belly='#9aa4b8', dark='#2e3444', accent='#c8d0e0', bolt='#ffd84a', cloud='#e8eef8', cloud2='#a8b4c8'), 2.8)
    B, Hd = quad(bw=0.84, bl=1.2, bh=0.7, legh=0.6, lw=0.2, hw=0.86, hd=0.86, hh=0.8, head_fwd=0.34, hoof='dark', leg_mat='main', head_mat='main')
    mz = muzzle(Hd, (0.4, 0.32, 0.26), -0.28, 'belly', nose=(0.14, 0.06, 0.08), nose_mat='dark')
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.32, Hd.front - 0.012, Hd.c.z - 0.18))
        b('ear', (0.26, 0.1, 0.12), mm('main'), (sgn * 0.52, Hd.c.y + 0.06, Hd.c.z + 0.12), rot=(0, sgn * 25, 0), bev=0.03)
        p('ear_in', (0.14, 0.04, 0.06), mm('pink'), (sgn * 0.52, Hd.c.y, Hd.c.z + 0.12), rot=(0, sgn * 25, 0))
    eyes(Hd, 0.34, 0.25, 0.1, iris='#ffb02a', brow='#2e3444', tilt=-14)
    # zig-zag lightning horns going straight up (the silhouette)
    use('head')
    for sgn, n in LR:
        x0 = sgn * 0.26
        for j, (dx, dz) in enumerate(((0.0, 0.0), (0.16, 0.24), (0.0, 0.48), (0.16, 0.72), (0.04, 0.96))):
            b('bolt_horn', (0.16, 0.16, 0.3), mm('bolt'), (x0 + sgn * dx, Hd.c.y, Hd.top + 0.14 + dz), rot=(0, sgn * (30 if j % 2 else -30), 0), bev=0.03)
        p('horn_base', (0.24, 0.24, 0.1), mm('dark'), (x0, Hd.c.y, Hd.top + 0.02))
    # thundercloud forelock
    for i, (x, z, s) in enumerate(((0, 0.12, 0.34), (-0.18, 0.06, 0.26), (0.18, 0.06, 0.26))):
        b('cloud_lock', (s, s, s * 0.8), mm('cloud' if i == 0 else 'cloud2'), (x, Hd.front + 0.2, Hd.top + z), bev=0.08)
    use('body')
    # short sleek coat with lightning stripes (pattern)
    for sgn, n in LR:
        for j, (u, v, rz) in enumerate(((-0.3, 0.1, 30), (-0.1, -0.1, -30), (0.1, 0.1, 30), (0.3, -0.1, -30))):
            on(B, 'l' if sgn < 0 else 'r', u, v, (0.22, 0.07), mm('accent'), name='zig', rot=(rz, 0, 0))
    on(B, 't', 0, 0, (0.16, B.s.y * 0.9), mm('dark'), name='back_stripe')
    fluff(a.bx['chest'], 'f', mm('belly'), 3, 0.8, 0.3)
    for ft in a.bx['feet']:
        p('sock', (ft.s.x + 0.02, ft.s.y + 0.02, 0.14), mm('dark'), (ft.c.x, ft.c.y, ft.top + 0.08))
    # thundercloud tail with a dangling bolt
    sg('tail', 'body', a.tail_j)
    a.tail = ['tail']
    for i, (dy, dz, s) in enumerate(((0.2, 0.1, 0.34), (0.42, 0.18, 0.28), (0.3, 0.32, 0.24))):
        b('tail_cloud', (s, s, s * 0.8), mm('cloud' if i % 2 == 0 else 'cloud2'), (0, a.tail_j[1] + dy, a.tail_j[2] + dz), bev=0.08)
    b('tail_bolt', (0.08, 0.08, 0.3), mm('bolt'), (0, a.tail_j[1] + 0.36, a.tail_j[2] - 0.12), rot=(0, 25, 0), bev=0.02)
    return finish(a)
'''

MOLE = r'''
def geode_mole(row):
    """geode mole: lives inside a split-open geode egg - the round shell is its body/house, crystals inside, the mole leans out
    the front with huge pink digging hands and a star nose; miner lamp on the shell"""
    a = start(row, dict(main='#6a5a6a', belly='#d8c8d0', dark='#3a2e3a', accent='#ff9ac8', nose='#ff7aa8', shell='#8a8292', shell2='#b0a8b8',
                        crystal='#a86af0', crystal2='#6ad8ff'), 1.9)
    # the geode shell (body segment): a hollow box opened to the front, crystal lining inside
    sg('body', 'root', (0, 0.2, 0.6))
    B = b('shell_back', (1.5, 0.3, 1.3), mm('shell'), (0, 0.6, 0.7), bev=0.16)
    b('shell_floor', (1.5, 1.1, 0.24), mm('shell'), (0, 0.2, 0.12), bev=0.08)
    for sgn, n in LR:
        b('shell_side', (0.24, 1.0, 1.2), mm('shell'), (sgn * 0.66, 0.24, 0.66), bev=0.1)
        p('shell_crack', (0.26, 0.06, 0.6), mm('dark'), (sgn * 0.66, -0.25, 0.7), rot=(0, sgn * 20, 0))
        grid(Box((sgn * 0.66, 0.24, 0.66), (0.24, 1.0, 1.2)), 'l' if sgn < 0 else 'r', 3, 3, mm('shell2'), (0.14, 0.14), name='shell_spot')
    b('shell_top', (1.5, 1.0, 0.24), mm('shell2'), (0, 0.26, 1.34), bev=0.1)
    # crystal lining (inside)
    for i, (x, z, d, m_) in enumerate(((-0.4, 1.1, (0.3, 0.3, -1), 'crystal'), (0.4, 1.1, (-0.3, 0.3, -1), 'crystal2'), (-0.5, 0.4, (0.6, 0, 0.6), 'crystal2'),
                                       (0.5, 0.4, (-0.6, 0, 0.6), 'crystal'), (0, 1.1, (0, 0.2, -1), 'crystal'), (-0.2, 0.6, (0, -0.8, 0.2), 'crystal'),
                                       (0.24, 0.7, (0, -0.8, 0.3), 'crystal2'))):
        cn('lining', 0.1, 0.36, mm(m_), (x, 0.42, z), d)
    # the mole: head and arms leaning out of the front
    sg('head', 'body', (0, -0.1, 0.6))
    Hd = b('head', (0.84, 0.76, 0.7), mm('main'), (0, -0.36, 0.66))
    b('cheek_fur', (0.9, 0.4, 0.3), mm('belly'), (0, -0.44, 0.42), bev=0.06)
    for i in range(6):
        ang = math.radians(i * 60)
        p('nose_ray', (0.08, 0.1, 0.08), mm('nose'), (math.cos(ang) * 0.13, Hd.front - 0.04, 0.5 + math.sin(ang) * 0.13))
    p('nose_core', (0.14, 0.1, 0.14), mm('nose'), (0, Hd.front - 0.03, 0.5))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.3, Hd.front - 0.012, 0.58))
    eyes(Hd, 0.26, 0.24, 0.24, iris='#3a2e3a', brow='#3a2e3a', tilt=8, sleepy=0.24)
    for sgn, n in LR:
        sg('arm_' + n, 'body', (sgn * 0.42, -0.2, 0.5))
        a.arms.append('arm_' + n)
        b('arm', (0.2, 0.4, 0.2), mm('main'), (sgn * 0.48, -0.42, 0.4), rot=(-20, 0, 0), bev=0.04)
        b('hand', (0.4, 0.2, 0.36), mm('accent'), (sgn * 0.56, -0.66, 0.3), bev=0.06)
        for j in range(4):
            p('claw', (0.07, 0.14, 0.07), mm('belly'), (sgn * 0.56 + (j - 1.5) * 0.09, -0.8, 0.16))
    # miner lamp on top of the shell (accessory)
    use('body')
    setm('lamp', '#fff6c0')
    setm('hat', '#ffd84a')
    b('lamp_box', (0.3, 0.3, 0.2), mm('hat'), (0, -0.16, 1.54), bev=0.05)
    b('lamp', (0.2, 0.12, 0.16), mm('lamp'), (0, -0.34, 1.54), bev=0.03)
    p('lamp_rim', (0.24, 0.06, 0.2), mm('dark'), (0, -0.3, 1.54))
    for j in range(3):
        cn('top_crystal', 0.1, 0.36 - 0.06 * j, mm('crystal' if j % 2 else 'crystal2'), ((j - 1) * 0.36, 0.5, 1.44), ((j - 1) * 0.4, 0.2, 1))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=tuple(Hd.c), Chest=(0, -0.5, 0.4), Hit=(0, 0.3, 1.4))
    return finish(a)
'''

if __name__ == '__main__':
    splice('biome_03.py', 'bison', BISON)
    splice('biome_10.py', 'storm_ram', RAM)
    splice('biome_15.py', 'geode_mole', MOLE)
    print('ok')
