# Redesigns of animals that echoed an earlier animal's body plan (user: no two creatures may look alike)
from redo_dragons import splice

CAVEBEAR = r'''
def cavebear(row):
    """seated mountain bear: sits like a boulder, round belly, arms hugging a mossy stone, mushroom garden growing on its head and shoulders"""
    a = start(row, dict(main='#8e8a80', belly='#d8d2c0', dark='#5a564e', accent='#f6f0dc', moss='#6aa84a', stone='#6e7068',
                        **{'*glow': '#5affd0', '*glow2': '#ffe14a'}), 1.6)
    B, Hd = sit(bw=1.6, bd=1.3, bh=1.5, hw=1.4, hd=1.1, hh=1.0, arm=0.7, lw=0.4, foot_l=0.8, ntoe=4, foot='belly', toe='dark')
    use('body')
    b('belly_round', (1.2, 0.2, 1.1), mm('belly'), (0, B.front - 0.06, B.c.z - 0.1), bev=0.12)
    for j in range(4):
        p('belly_fur', (0.9 - 0.15 * j, 0.06, 0.1), mm('accent'), (0, B.front - 0.17, B.c.z + 0.3 - j * 0.22))
    for sgn, n in LR:
        b('hip', (0.36, 0.7, 0.6), mm('main'), (sgn * (B.s.x / 2 + 0.1), 0.42, 0.5), bev=0.08)
        for j in range(3):
            p('side_fur', (0.06, 0.24, 0.26), mm('dark'), (sgn * (B.s.x / 2 + 0.01), B.c.y - 0.3 + j * 0.3, B.c.z + 0.3))
    use('head')
    mz = muzzle(Hd, (0.6, 0.3, 0.38), -0.25, 'belly', nose=(0.26, 0.12, 0.15), fangs=0)
    for sgn, n in LR:
        p('blush', (0.18, 0.03, 0.09), mm('pink'), (sgn * 0.48, Hd.front - 0.012, Hd.c.z - 0.2))
        b('ear', (0.3, 0.14, 0.3), mm('main'), (sgn * 0.52, Hd.c.y, Hd.top + 0.1), bev=0.07)
        p('ear_in', (0.16, 0.04, 0.16), mm('accent'), (sgn * 0.52, Hd.c.y - 0.08, Hd.top + 0.1))
    eyes(Hd, 0.26, 0.24, 0.14, iris='#2a6a5a', glow='#5affd0', brow='#5a564e', tilt=10, sleepy=0.22)
    # the mossy stone it hugs (own segment, rocks in Idle)
    sg('stone', 'body', (0, B.front - 0.4, B.c.z - 0.3))
    b('hug_stone', (1.0, 0.6, 0.8), mm('stone'), (0, B.front - 0.4, B.c.z - 0.3), bev=0.14)
    b('hug_moss', (0.8, 0.5, 0.2), mm('moss'), (0, B.front - 0.4, B.c.z + 0.16), bev=0.06)
    for j in range(3):
        p('stone_spot', (0.16, 0.05, 0.16), mm('dark'), ((j - 1) * 0.3, B.front - 0.71, B.c.z - 0.3 + 0.1 * (j % 2)))
    a.extra_idle.append(lambda c, n: [k(c, 'stone', x, rot=(0, r, 0)) for x, r in ((1, 0), (n // 2, 4), (n, 0))])
    use('body')
    tail_kit('stub', 'body', (0, a.tail_j[1], 0.3), 'main', 'dark', size=0.24)
    # rarity 5: glowing mushroom garden on the head and shoulders (own segment), leaf orbit, yellow aura
    sg('glow', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow')
    for i, (x, y, s) in enumerate(((-0.34, 0.0, 1.0), (0.3, 0.1, 0.8), (0.0, 0.3, 1.2), (-0.1, -0.24, 0.6))):
        p('shroom_stem', (0.1 * s, 0.1 * s, 0.3 * s), mm('accent'), (x, Hd.c.y + y, Hd.top + 0.15 * s))
        b('shroom_cap', (0.36 * s, 0.36 * s, 0.14 * s), mm('glow'), (x, Hd.c.y + y, Hd.top + 0.36 * s), bev=0.04)
        p('shroom_dot', (0.07 * s, 0.07 * s, 0.03), mm('glow2'), (x + 0.08 * s, Hd.c.y + y - 0.06 * s, Hd.top + 0.44 * s))
    b('head_moss', (1.0, 0.8, 0.1), mm('moss'), (0, Hd.c.y, Hd.top + 0.04), bev=0.03)
    use('body')
    for sgn, n in LR:
        b('shoulder_moss', (0.5, 0.5, 0.1), mm('moss'), (sgn * 0.5, B.c.y, B.top + 0.04), bev=0.03)
        for j in range(2):
            p('shoulder_shroom', (0.2, 0.2, 0.1), mm('glow2' if j else 'glow'), (sgn * (0.4 + 0.2 * j), B.c.y + 0.1 * j, B.top + 0.18))
    orbit_kit((0, 0.1, 1.6), 1.7, 6, 'glow', 'glow2', size=0.13, dz=0.4, shape='leaf')
    aura_kit(1.7, 5, motes=10, mote_col='glow', height=2.2, style='double')
    return finish(a)
'''

ICEMAMMOTH = r'''
def icemammoth(row):
    """glacier mammoth: stilt-tall legs and a short high body, trunk curled up in an S, spiral tusks rising like horns, ice-shard ridge"""
    a = start(row, dict(main='#bfe4f6', belly='#eaf8ff', dark='#5a9ac8', accent='#8fc8ea', horn='#ffffff', snow='#ffffff',
                        **{'*glow': '#7fe0ff', '*glow2': '#fff6a0'}), 3.4)
    B, Hd = quad(bw=1.1, bl=1.2, bh=1.0, legh=1.4, lw=0.36, hw=1.1, hd=0.96, hh=1.0, head_up=0.6, toe='horn', leg_fl=0.46, head_fwd=0.3,
                 ntoe=3, hump=0.0, rump=False)
    use('head')
    for sgn, n in LR:
        # tusks spiral upward like horns (silhouette), not forward
        for j in range(5):
            ang = math.radians(j * 55)
            b('tusk', (0.16 - 0.015 * j, 0.16 - 0.015 * j, 0.24), mm('horn'), (sgn * (0.3 + 0.18 * math.cos(ang)), Hd.front + 0.1 - 0.18 * math.sin(ang), Hd.bot + 0.2 + j * 0.22), bev=0.04)
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.42, Hd.front - 0.012, Hd.c.z - 0.24))
        b('ear', (0.14, 0.5, 0.5), mm('accent'), (sgn * (Hd.s.x / 2 + 0.06), Hd.c.y + 0.1, Hd.c.z), bev=0.05)
    # trunk curled up in an S (two segments)
    sg('trunk', 'head', (0, Hd.front, Hd.c.z - 0.2))
    b('trunk_a', (0.34, 0.3, 0.44), mm('main'), (0, Hd.front - 0.12, Hd.c.z - 0.4), bev=0.06)
    sg('trunk2', 'trunk', (0, Hd.front - 0.2, Hd.c.z - 0.6))
    b('trunk_b', (0.28, 0.4, 0.26), mm('main'), (0, Hd.front - 0.4, Hd.c.z - 0.66), bev=0.06)
    b('trunk_c', (0.24, 0.24, 0.4), mm('main'), (0, Hd.front - 0.6, Hd.c.z - 0.44), bev=0.05)
    p('trunk_tip', (0.2, 0.08, 0.1), mm('pink'), (0, Hd.front - 0.64, Hd.c.z - 0.22))
    for j in range(3):
        p('trunk_ring', (0.3, 0.32, 0.04), mm('accent'), (0, Hd.front - 0.12 - 0.14 * j, Hd.c.z - 0.36 - 0.1 * j))
    a.trunk = ['trunk', 'trunk2']
    a.extra_idle.append(lambda c, n: [k(c, 'trunk2', x, rot=(r, 0, 0)) for x, r in ((1, 0), (n // 2, -12), (n, 0))])
    eyes(Hd, 0.26, 0.27, 0.14, iris='#2a7ab0', glow='#7fe0ff', brow='#5a9ac8', tilt=8, lash=True)
    use('body')
    # short shaggy coat hanging like an icicle skirt
    for sgn, n in LR:
        for j in range(4):
            b('coat', (0.1, 0.28, 0.5), mm('accent' if j % 2 else 'snow'), (sgn * (B.s.x / 2 + 0.05), B.front + 0.16 + j * 0.28, B.bot + 0.1), bev=0.03)
            p('icicle', (0.06, 0.08, 0.2), mm('glow'), (sgn * (B.s.x / 2 + 0.05), B.front + 0.16 + j * 0.28, B.bot - 0.24))
    for j in range(4):
        b('coat_front', (0.24, 0.1, 0.46), mm('snow'), ((j - 1.5) * 0.26, B.front - 0.05, B.bot + 0.08), bev=0.03)
    grid(B, 't', 3, 3, mm('snow'), (0.16, 0.16), name='snow', th=0.06)
    for ft in a.bx['feet']:
        use(ft.seg)
        for j in range(3):
            p('leg_ring', (ft.s.x + 0.04, ft.s.y + 0.04, 0.06), mm('dark' if j % 2 else 'accent'), (ft.c.x, ft.c.y, 0.4 + j * 0.34))
    use('body')
    tail_kit('tuft', 'body', (0, B.back + 0.04, B.c.z), 'main', 'snow', size=0.14)
    # rarity 5: ice-shard ridge along the spine (own glowing segment), glowing trunk tip, cross orbit, yellow aura
    sg('glow', 'body', (0, B.c.y, B.top))
    a.glow.append('glow')
    for j in range(5):
        cn('ridge_shard', 0.14, 0.7 - 0.08 * abs(j - 2), mm('glow' if j % 2 else 'glow2'), (0, B.front + 0.12 + j * 0.24, B.top - 0.02), (0, 0.2, 1))
    for sgn, n in LR:
        cn('side_shard', 0.08, 0.36, mm('glow'), (sgn * 0.4, B.c.y, B.top - 0.02), (sgn * 0.8, 0, 0.8))
    use('trunk2')
    p('trunk_glow', (0.16, 0.06, 0.1), mm('glow'), (0, Hd.front - 0.66, Hd.c.z - 0.2))
    use('body')
    orbit_kit((0, 0.2, 2.6), 1.6, 6, 'glow', 'glow2', size=0.14, dz=0.5, shape='shard')
    aura_kit(1.6, 5, motes=10, mote_col='glow', height=3.2, style='diamond')
    return finish(a)
'''

LEVIATHAN = r'''
def abyss_leviathan(row):
    """deep-sea whale leviathan: huge round whale body swimming horizontally, angler lantern on a stalk, baleen grin, glowing freckles"""
    zc = 1.4
    a = start(row, dict(main='#2a3a7a', belly='#8ac8e8', dark='#141c48', accent='#5affe0', fin='#3a5ab8', horn='#e8f8ff',
                        **{'*glow': '#5affe0', '*glow2': '#ffd21a'}), 2.6, hover=3.0, z0=zc)
    B, Hd = fish(bw=1.8, bl=2.4, bh=1.6, face_h=1.4, fin=(0.9, 0.7, 0.14), tail=(0.18, 0.9, 1.6), dorsal=0.0, ntail=2, zc=zc)
    use('head')
    p('grin', (1.4, 0.04, 0.08), mm('dark'), (0, Hd.front - 0.012, zc - 0.36))
    for i in range(8):
        p('baleen', (0.1, 0.04, 0.18), mm('horn'), ((i - 3.5) * 0.17, Hd.front - 0.014, zc - 0.48))
    for sgn, n in LR:
        p('blush', (0.2, 0.03, 0.1), mm('pink'), (sgn * 0.62, Hd.front - 0.012, zc - 0.24))
        for j in range(3):
            p('chin_groove', (0.06, 0.04, 0.3), mm('belly'), (sgn * (0.2 + 0.2 * j), Hd.front - 0.012, zc - 0.66))
    eyes(Hd, 0.3, 0.3, 0.12, iris='#2a8ab0', glow='#5affe0', brow='#141c48', tilt=-4, sleepy=0.12)
    # angler lantern stalk curving forward over the head (the silhouette)
    sg('lure', 'head', (0, Hd.c.y, Hd.top))
    a.ears.append('lure')
    for j in range(4):
        b('stalk', (0.1, 0.1, 0.36), mm('dark'), (0, Hd.c.y - 0.1 * j * j, Hd.top + 0.16 + j * 0.3 - 0.04 * j * j), rot=(-20 * j, 0, 0), bev=0.02)
    b('lantern', (0.36, 0.36, 0.36), mm('glow2'), (0, Hd.c.y - 1.0, Hd.top + 1.0), rot=(45, 45, 0), bev=0.08)
    p('lantern_hi', (0.12, 0.12, 0.12), mm('white'), (-0.08, Hd.c.y - 1.12, Hd.top + 1.1))
    use('body')
    grid(B, 'u', 4, 5, mm('belly'), (0.3, 0.12), name='belly_groove', th=0.1)
    for sgn, n in LR:
        grid(B, 'l' if sgn < 0 else 'r', 5, 3, mm('dark'), (0.14, 0.14), name='side_spot', offset=0.1)
    for i in range(3):
        cn('back_bump', 0.16, 0.24, mm('fin'), (0, B.c.y - 0.5 + i * 0.5, zc + 0.8), (0, 0.3, 1))
    # rarity 5: glowing freckle constellations, glowing fin edges, bubble orbit, yellow aura
    sg('glow', 'body', (0, 0.2, zc))
    a.glow.append('glow')
    for sgn, n in LR:
        for j in range(5):
            p('freckle', (0.05, 0.1, 0.1), mm('glow' if j % 2 else 'glow2'), (sgn * 0.92, 0.2 - 0.8 + j * 0.4, zc + 0.3 - 0.1 * (j % 2)), rot=(45, 0, 0))
        use('wing_' + n)
        p('fin_glow', (0.8, 0.1, 0.06), mm('glow'), (sgn * (0.9 + 0.45), 0.12 + 0.36, zc - 0.28), rot=(0, sgn * 20, 0))
        use('glow')
    use('body')
    orbit_kit((0, 0.2, zc + 0.4), 2.2, 8, 'glow', 'glow2', size=0.16, dz=0.6, shape='bubble')
    aura_kit(2.2, 5, motes=10, mote_col='glow', height=2.6, style='double')
    return finish(a)
'''

EMBERBOAR = r'''
def ember_boar(row):
    """ember warthog that stands on its hind legs like a little brawler: barrel body, big tusked face with warts, burning mohawk"""
    a = start(row, dict(main='#4a3a3a', belly='#8a6a5a', dark='#241c1e', accent='#ffe0c0', snout='#ff9a8a', **{'*glow': '#ff8a2a'}), 2.0)
    B, Hd = biped(tw=1.2, td=1.0, th=1.0, legh=0.4, lw=0.36, hw=1.2, hd=1.0, hh=0.9, arm_l=0.7, arm_w=0.3, hand=0.36, shoulder=0.0,
                  foot='dark', toe='belly', hand_mat='dark')
    use('head')
    sn = b('snout', (0.56, 0.32, 0.4), mm('snout'), (0, Hd.front - 0.12, Hd.c.z - 0.2), bev=0.07)
    for sgn, n in LR:
        p('nostril', (0.1, 0.03, 0.14), mm('line'), (sgn * 0.11, sn.front - 0.008, sn.c.z + 0.03))
        b('tusk', (0.1, 0.1, 0.34), mm('accent'), (sgn * 0.34, sn.front + 0.06, sn.c.z + 0.1), rot=(0, sgn * 18, 0), bev=0.03)
        b('wart', (0.16, 0.12, 0.16), mm('belly'), (sgn * 0.5, Hd.front + 0.04, Hd.c.z - 0.06), bev=0.04)
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z + 0.02))
        b('ear', (0.26, 0.12, 0.3), mm('main'), (sgn * 0.56, Hd.c.y, Hd.top - 0.02), rot=(0, sgn * 40, 0), bev=0.04)
    eyes(Hd, 0.28, 0.24, 0.2, iris='#c84a1a', glow='#ff8a2a', brow='#241c1e', tilt=-16)
    use('body')
    b('barrel', (1.3, 1.1, 0.7), mm('main'), (0, 0.05, 0.4 + 0.5), bev=0.1)
    b('belly_patch', (0.8, 0.1, 0.6), mm('belly'), (0, -0.52, 0.86), bev=0.04)
    for sgn, n in LR:
        grid(B, 'l' if sgn < 0 else 'r', 3, 2, mm('dark'), (0.14, 0.14), name='bristle_patch')
    setm('belt', '#a85a2a')
    b('belt', (1.36, 1.16, 0.14), mm('belt'), (0, 0.05, 0.62), bev=0.03)
    p('buckle', (0.24, 0.06, 0.18), mm('glow'), (0, -0.54, 0.62))
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        b('glove', (hb_.s.x + 0.1, hb_.s.y + 0.1, hb_.s.z + 0.06), mm('belt'), hb_.c, bev=0.06)
        p('glove_band', (hb_.s.x + 0.12, hb_.s.y + 0.12, 0.06), mm('accent'), (hb_.c.x, hb_.c.y, hb_.top + 0.04))
    use('body')
    tail_kit('tuft', 'body', a.tail_j, 'main', 'dark', size=0.14)
    # rarity 4: burning mohawk running from head down the back (own segment), ember sparks
    sg('glow', 'head', (0, Hd.c.y, Hd.top))
    a.glow.append('glow')
    for i in range(5):
        b('mohawk', (0.18, 0.18, 0.3 + 0.1 * math.sin(i * 0.9)), mm('glow'), (0, Hd.c.y - 0.3 + i * 0.18, Hd.top + 0.14), bev=0.04)
        p('mohawk_tip', (0.1, 0.1, 0.12), mm('accent'), (0, Hd.c.y - 0.3 + i * 0.18, Hd.top + 0.34 + 0.05 * math.sin(i * 0.9)))
    use('body')
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=1.6)
    return finish(a)
'''

MAGMARHINO = r'''
def magma_rhino(row):
    """volcano rhino: carries a stepped volcano cone on its back that glows at the crater, single fat horn, stumpy elephant legs"""
    a = start(row, dict(main='#4a3a3e', belly='#8a6a6a', dark='#24181c', accent='#ffd0a0', horn='#3a2a30', rock='#5a4a4a', **{'*glow': '#ff5a1a', '*glow2': '#ffd21a'}), 2.4)
    B, Hd = quad(bw=1.5, bl=1.4, bh=0.9, legh=0.3, lw=0.48, hw=1.2, hd=1.0, hh=0.9, head_up=0.2, toe='accent', leg_fl=0.52, head_fwd=0.36,
                 rump=False)
    mz = muzzle(Hd, (0.8, 0.4, 0.46), -0.24, 'belly', nose=None, mouth=True)
    for sgn, n in LR:
        p('nostril', (0.1, 0.03, 0.07), mm('line'), (sgn * 0.2, mz.front - 0.008, mz.c.z + 0.08))
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.44, Hd.front - 0.012, Hd.c.z - 0.24))
        b('ear', (0.2, 0.12, 0.26), mm('main'), (sgn * 0.5, Hd.c.y + 0.1, Hd.top + 0.04), rot=(0, sgn * 30, 0), bev=0.04)
    b('horn', (0.36, 0.36, 0.5), mm('horn'), (0, mz.c.y - 0.04, mz.top + 0.24), bev=0.08)
    p('horn_tip', (0.2, 0.2, 0.2), mm('rock'), (0, mz.c.y - 0.04, mz.top + 0.56))
    eyes(Hd, 0.28, 0.27, 0.12, iris='#c84a1a', glow='#ff5a1a', brow='#24181c', tilt=-14)
    use('body')
    # the volcano on its back (the silhouette): stepped cone of rock
    for i, (w, h) in enumerate(((1.4, 0.4), (1.1, 0.4), (0.8, 0.36), (0.6, 0.3))):
        b('cone', (w, w * 0.9, h), mm('rock' if i % 2 else 'main'), (0, B.c.y + 0.06, B.top + 0.2 + i * 0.38), bev=0.06)
    b('crater_rim', (0.66, 0.6, 0.12), mm('dark'), (0, B.c.y + 0.06, B.top + 1.48), bev=0.03)
    for sgn, n in LR:
        for j in range(3):
            p('lava_drip', (0.08, 0.05, 0.3 - 0.06 * j), mm('glow'), (sgn * (0.3 + 0.12 * j), B.c.y + 0.06 - 0.4 + 0.06 * j, B.top + 0.9 - 0.36 * j))
    for ft in a.bx['feet']:
        use(ft.seg)
        b('foot_pad', (ft.s.x + 0.1, ft.s.y + 0.1, 0.12), mm('rock'), (ft.c.x, ft.c.y + 0.04, 0.06), bev=0.03)
        for j in range(3):
            p('toenail', (0.1, 0.06, 0.08), mm('accent'), (ft.c.x + (j - 1) * 0.14, ft.front - 0.04, 0.06))
    use('body')
    grid(B, 'l', 3, 2, mm('rock'), (0.18, 0.18), name='rock_plate')
    grid(B, 'r', 3, 2, mm('rock'), (0.18, 0.18), name='rock_plate')
    tail_kit('stub', 'body', a.tail_j, 'main', 'dark', size=0.2)
    # rarity 4: glowing crater and lava cracks (own segment), smoke-ember sparks
    sg('glow', 'body', (0, B.c.y + 0.06, B.top + 1.4))
    a.glow.append('glow')
    b('crater_lava', (0.46, 0.42, 0.1), mm('glow2'), (0, B.c.y + 0.06, B.top + 1.5), bev=0.03)
    for i in range(3):
        p('crater_spark', (0.1, 0.1, 0.16), mm('glow'), ((i - 1) * 0.14, B.c.y + 0.06, B.top + 1.66 + 0.06 * (i % 2)))
    for sgn, n in LR:
        p('flank_crack', (0.05, 0.6, 0.06), mm('glow'), (sgn * (B.s.x / 2 + 0.02), B.c.y, B.c.z))
    aura_kit(1.6, 4, motes=8, mote_col='glow', height=2.2)
    return finish(a)
'''

JAGUAR = r'''
def jaguar(row):
    """stalking jaguar: long low slinky body pressed to the ground, legs bent, extra-long tail raised in a question mark"""
    a = start(row, dict(main='#f2b84a', belly='#fff4d8', dark='#3a2a22', accent='#d8863a', **{'*glow': '#5aff8a'}), 1.7)
    B, Hd = quad(bw=0.9, bl=2.0, bh=0.56, legh=0.26, lw=0.3, hw=1.1, hd=0.9, hh=0.8, head_up=0.2, toe='dark', leg_fl=0.5, head_fwd=0.5,
                 rump=False, chest=False)
    mz = muzzle(Hd, (0.5, 0.26, 0.28), -0.26, 'belly', nose=(0.2, 0.09, 0.12), nose_mat='pink', top='main', fangs=1)
    cheeks(Hd, 'belly', (0.26, 0.22, 0.28), -0.25, whisk=3)
    eyes(Hd, 0.36, 0.25, 0.12, iris='#2a8a4a', glow='#5aff8a', brow='#3a2a22', tilt=-16, sleepy=0.2)
    for sgn, n in LR:
        b('ear', (0.24, 0.12, 0.2), mm('main'), (sgn * 0.38, Hd.c.y + 0.1, Hd.top + 0.06), bev=0.05)
        p('ear_back', (0.24, 0.05, 0.14), mm('dark'), (sgn * 0.38, Hd.c.y + 0.17, Hd.top + 0.06))
    use('body')

    def rosette(box, f, u, v, s=0.2):
        on(box, f, u, v, (s, s), mm('dark'), name='rosette', th=0.03)
        on(box, f, u, v, (s * 0.5, s * 0.5), mm('accent'), name='rosette_in', th=0.04)
    for f in ('l', 'r', 't'):
        for i, (u, v) in enumerate(((-0.4, 0.2), (-0.2, -0.2), (0.0, 0.22), (0.2, -0.2), (0.4, 0.2))):
            rosette(B, f, u, v, 0.2)
    use('head')
    for i, (u, v) in enumerate(((-0.25, 0.2), (0.25, 0.2), (0.0, 0.0))):
        on(Hd, 't', u, v, (0.12, 0.12), mm('dark'), name='head_spot')
    use('body')
    for ft in a.bx['feet']:
        p('leg_spot', (0.1, 0.03, 0.1), mm('dark'), (ft.c.x, ft.c.y - 0.16, 0.2))
    # long question-mark tail held high (3 segments)
    sg('tail', 'body', (0, B.back - 0.04, B.c.z + 0.1))
    a.tail = ['tail']
    cur = Vector((0, B.back - 0.04, B.c.z + 0.1))
    par = 'tail'
    for i, d in enumerate(((0, 0.4, 0.3), (0, 0.2, 0.5), (0, -0.1, 0.4), (0, -0.3, 0.1))):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        if i:
            sg(nm, par, tuple(cur))
            a.tail.append(nm)
            par = nm
        c = cur + Vector(d) * 0.5
        b('tail', (0.2, 0.2, 0.2 + Vector(d).length * 0.8), mm('main' if i % 2 == 0 else 'accent'), tuple(c), rot=(-math.degrees(math.atan2(d[1], d[2])), 0, 0), bev=0.04)
        p('tail_ring', (0.22, 0.22, 0.06), mm('dark'), tuple(c))
        cur = cur + Vector(d)
    p('tail_tip', (0.22, 0.22, 0.22), mm('dark'), tuple(cur))
    use('body')
    # rarity 4: emerald temple runes on the back, glowing tail tip, firefly sparks
    glow_marks(B, ('t',), 4, 'glow', style='rune', size=0.14)
    use(a.tail[-1])
    p('tail_glow', (0.16, 0.16, 0.16), mm('glow'), tuple(cur + Vector((0, 0, 0.16))), rot=(45, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.top))
    a.glow.append('glow_h')
    on(Hd, 'f', 0, 0.36, (0.14, 0.14), mm('glow'), th=0.035, name='fore_rune', rot=(0, 45, 0))
    use('body')
    aura_kit(1.5, 4, motes=8, mote_col='glow', height=1.4)
    return finish(a)
'''

if __name__ == '__main__':
    splice('biome_03.py', 'cavebear', CAVEBEAR)
    splice('biome_04.py', 'icemammoth', ICEMAMMOTH)
    splice('biome_12.py', 'abyss_leviathan', LEVIATHAN)
    splice('biome_13.py', 'ember_boar', EMBERBOAR)
    splice('biome_14.py', 'magma_rhino', MAGMARHINO)
    splice('biome_08.py', 'jaguar', JAGUAR)
    print('ok')
