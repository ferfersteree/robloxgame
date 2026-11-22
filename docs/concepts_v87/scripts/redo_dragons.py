# New, clearly different designs for coral_wyvern (b11) and quartz_dragon (b15). Spliced into the biome files by splice().
import io

CORAL = r'''
def coral_wyvern(row):
    """sea wyvern: stands on two webbed legs, long S-neck, seahorse-like head with a fan frill, fin-sail wings, eel tail with a fluke"""
    zc = 1.4
    a = start(row, dict(main='#2ab8b0', belly='#fff0d8', dark='#14706a', accent='#ff7a8a', coral='#ff9a5a', fin='#7ae8ff', horn='#fff4e0',
                        **{'*glow': '#5ae8ff', '*glow2': '#ffd21a'}), 3.6, hover=2.4, z0=zc)
    # upright pear-shaped torso
    sg('body', 'root', (0, 0.2, zc))
    B = b('body', (0.9, 0.8, 1.1), mm('main'), (0, 0.2, zc))
    b('hips', (1.0, 0.9, 0.5), mm('main'), (0, 0.3, zc - 0.55), bev=0.08)
    b('belly', (0.6, 0.12, 0.9), mm('belly'), (0, -0.22, zc - 0.05), bev=0.04)
    for j in range(5):
        p('belly_plate', (0.62, 0.14, 0.06), mm('coral'), (0, -0.26, zc - 0.42 + j * 0.2))
    for sgn, n in LR:
        for j in range(3):
            p('side_scale', (0.05, 0.22, 0.2), mm('dark'), (sgn * 0.46, 0.1 + j * 0.2, zc + 0.2 - j * 0.24))
            b('shoulder_coral', (0.1, 0.1, 0.34 - 0.08 * j), mm('coral'), (sgn * (0.3 + 0.12 * j), 0.3, zc + 0.6 + 0.14 * (2 - j)), rot=(0, sgn * 25, 0), bev=0.02)
    # S-neck: three thin segments curving forward
    cur = Vector((0, 0.0, zc + 0.5))
    par = 'body'
    a.neck = []
    for i, (dy, dz) in enumerate(((-0.1, 0.5), (-0.3, 0.45), (-0.1, 0.4))):
        nm = 'neck%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.neck.append(nm)
        c = cur + Vector((0, dy * 0.5, dz * 0.5))
        b('neck', (0.38 - 0.03 * i, 0.38 - 0.03 * i, 0.5), mm('main'), tuple(c), rot=(-dy * 60, 0, 0), bev=0.06)
        p('neck_belly', (0.24, 0.05, 0.4), mm('belly'), (0, c.y - 0.19, c.z), rot=(-dy * 60, 0, 0))
        b('neck_fin', (0.06, 0.2, 0.3), mm('fin'), (0, c.y + 0.2, c.z), bev=0.02)
        cur = cur + Vector((0, dy, dz))
        par = nm
    # long seahorse head
    sg('head', par, tuple(cur))
    hc = (0, cur.y - 0.2, cur.z + 0.25)
    Hd = b('head', (0.74, 0.7, 0.62), mm('main'), hc)
    sn = b('snout', (0.34, 0.6, 0.3), mm('main'), (0, Hd.front - 0.26, hc[2] - 0.1), bev=0.05)
    p('snout_tip', (0.36, 0.08, 0.26), mm('dark'), (0, sn.front + 0.02, sn.c.z))
    p('mouth', (0.2, 0.03, 0.03), mm('line'), (0, sn.front - 0.006, sn.c.z - 0.06))
    for sgn, n in LR:
        p('blush', (0.12, 0.03, 0.06), mm('pink'), (sgn * 0.26, Hd.front - 0.012, hc[2] - 0.16))
        b('barbel', (0.05, 0.05, 0.36), mm('fin'), (sgn * 0.16, sn.front + 0.06, sn.bot - 0.16), rot=(0, sgn * 15, 0), bev=0.01)
        p('barbel_tip', (0.1, 0.1, 0.1), mm('glow'), (sgn * 0.2, sn.front + 0.06, sn.bot - 0.34))
    # fan frill behind the head (the silhouette)
    for i in range(7):
        ang = math.radians(-60 + i * 20)
        ln = 0.6 + 0.12 * (3 - abs(i - 3))
        b('frill_spine', (0.06, 0.06, ln), mm('dark'), (math.sin(ang) * ln * 0.5, Hd.back + 0.04, Hd.top - 0.1 + math.cos(ang) * ln * 0.5), rot=(0, math.degrees(ang), 0), bev=0.01)
        p('frill_web', (0.16, 0.04, ln * 0.8), mm('fin' if i % 2 else 'accent'), (math.sin(ang) * ln * 0.45, Hd.back + 0.06, Hd.top - 0.1 + math.cos(ang) * ln * 0.45), rot=(0, math.degrees(ang) + 10, 0))
    eyes(Hd, 0.38, 0.25, 0.14, iris='#2a8ab0', glow='#5ae8ff', lash=True, brow='#14706a', tilt=-6)
    # two webbed legs (bird-like stance)
    for sgn, n in LR:
        sg('leg_' + n, 'body', (sgn * 0.34, 0.3, zc - 0.7))
        a.legs.append('leg_' + n)
        b('thigh', (0.32, 0.4, 0.5), mm('main'), (sgn * 0.36, 0.34, zc - 0.9), bev=0.05)
        b('shin', (0.2, 0.2, 0.5), mm('dark'), (sgn * 0.36, 0.46, zc - 1.26), bev=0.03)
        b('foot', (0.44, 0.5, 0.1), mm('fin'), (sgn * 0.36, 0.3, zc - 1.52), bev=0.03)
        for j in range(3):
            p('toe_claw', (0.07, 0.1, 0.07), mm('horn'), (sgn * 0.36 + (j - 1) * 0.14, 0.04, zc - 1.52))
    # tiny front claws
    for sgn, n in LR:
        sg('arm_' + n, 'body', (sgn * 0.4, -0.1, zc + 0.2))
        a.arms.append('arm_' + n)
        b('arm', (0.14, 0.14, 0.34), mm('main'), (sgn * 0.44, -0.16, zc + 0.04), rot=(-30, 0, 0), bev=0.03)
        p('claw', (0.16, 0.12, 0.1), mm('horn'), (sgn * 0.44, -0.26, zc - 0.12))
    # fin-sail wings: spines fanning up and back with webbing
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.42, 0.4, zc + 0.4))
        a.wings.append('wing_' + n)
        for i in range(5):
            ang = math.radians(10 + i * 18)
            ln = 1.2 + 0.25 * (2 - abs(i - 2))
            ex, ez = math.cos(ang) * ln, math.sin(ang) * ln
            b('wing_spine', (ln, 0.08, 0.08), mm('dark'), (sgn * (0.42 + ex / 2), 0.45 + i * 0.08, zc + 0.4 + ez / 2), rot=(0, -sgn * math.degrees(ang), 0), bev=0.02)
            p('wing_web', (ln * 0.9, 0.05, 0.22), mm('fin' if i % 2 else 'accent'), (sgn * (0.42 + ex * 0.48), 0.48 + i * 0.08, zc + 0.4 + ez * 0.48 - 0.12), rot=(0, -sgn * math.degrees(ang), 0))
            p('wing_tip', (0.12, 0.12, 0.12), mm('glow' if i % 2 else 'glow2'), (sgn * (0.42 + ex), 0.45 + i * 0.08, zc + 0.4 + ez), rot=(45, 45, 0))
    # long eel tail curling down with a fluke
    cur = Vector((0, 0.7, zc - 0.5))
    par = 'body'
    a.tail = []
    for i in range(4):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        w = 0.42 - 0.07 * i
        d = Vector((0, 0.45, -0.18 + 0.1 * i))
        b('tail', (w, 0.5, w), mm('main' if i % 2 == 0 else 'dark'), tuple(cur + d * 0.5), bev=0.05)
        p('tail_fin', (0.05, 0.36, w + 0.2), mm('fin'), tuple(cur + d * 0.5 + Vector((0, 0, w / 2 + 0.06))))
        cur = cur + d
        par = nm
    b('fluke', (0.9, 0.3, 0.12), mm('fin'), tuple(cur + Vector((0, 0.16, 0))), bev=0.04)
    p('fluke_glow', (0.6, 0.12, 0.13), mm('glow'), tuple(cur + Vector((0, 0.26, 0))))
    use('body')
    # rarity 5: glowing coral tips and belly gem, bubble orbit, yellow aura (diamond style)
    sg('glow', 'body', (0, 0.2, zc))
    a.glow.append('glow')
    p('chest_pearl', (0.2, 0.08, 0.2), mm('glow2'), (0, -0.33, zc + 0.3), rot=(0, 45, 0))
    for sgn, n in LR:
        for j in range(3):
            p('coral_glow', (0.08, 0.08, 0.08), mm('glow'), (sgn * (0.3 + 0.12 * j), 0.3, zc + 0.6 + 0.14 * (2 - j) + 0.2 - 0.04 * j))
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=hc, Chest=(0, -0.3, zc + 0.1), Hit=(0, 0.2, zc + 0.5))
    orbit_kit((0, 0.2, zc + 0.6), 1.6, 8, 'glow', 'glow2', size=0.12, dz=0.4, shape='bubble')
    aura_kit(1.4, 5, motes=10, mote_col='glow', height=2.2, style='diamond')
    return finish(a)
'''

QUARTZ = r'''
def quartz_dragon(row):
    """crystal golem-dragon: wide low armoured body on short pillar legs, a folded fan of crystal slabs instead of membrane wings,
    blunt head with a forest of crystal horns, club tail with a crystal cluster"""
    a = start(row, dict(main='#b8b0d8', belly='#e8e4f8', dark='#5a4e7a', accent='#8a7ab8', crystal='#e8d8ff', blue='#8ae0ff', rock='#6a6088',
                        **{'*glow': '#c88aff', '*glow2': '#7ae8ff', '*gem': '#ff8ad8'}), 2.7)
    B, Hd = quad(bw=1.8, bl=1.9, bh=0.9, legh=0.36, lw=0.46, hw=1.3, hd=0.9, hh=0.8, head_up=0.3, toe='crystal', head_fwd=0.36,
                 leg_fl=0.6, ntoe=3, leg_mat='rock', foot='rock', rump=True, chest=False)
    use('head')
    # blunt boxy jaw
    b('jaw', (1.2, 0.5, 0.36), mm('rock'), (0, Hd.front - 0.12, Hd.bot + 0.1), bev=0.06)
    for i in range(4):
        p('tooth', (0.1, 0.06, 0.12), mm('crystal'), ((i - 1.5) * 0.24, Hd.front - 0.37, Hd.bot + 0.24))
    for sgn, n in LR:
        p('nostril', (0.1, 0.04, 0.06), mm('line'), (sgn * 0.2, Hd.front - 0.012, Hd.c.z - 0.06))
        p('blush', (0.18, 0.03, 0.09), mm('pink'), (sgn * 0.48, Hd.front - 0.012, Hd.c.z - 0.2))
    eyes(Hd, 0.3, 0.27, 0.16, iris='#5a3aa8', glow='#c88aff', brow='#5a4e7a', tilt=-14)
    # forest of crystal horns on the head (the silhouette)
    for i, (x, y, h, d) in enumerate(((0, 0.0, 0.9, (0, 0.2, 1)), (-0.36, 0.1, 0.7, (-0.5, 0.3, 1)), (0.36, 0.1, 0.7, (0.5, 0.3, 1)),
                                      (-0.5, 0.3, 0.5, (-0.8, 0.5, 0.6)), (0.5, 0.3, 0.5, (0.8, 0.5, 0.6)), (0, 0.3, 0.5, (0, 0.8, 0.8)))):
        cn('horn_crystal', 0.12 + 0.03 * (i == 0), h, mm('crystal' if i % 2 == 0 else 'blue'), (x, Hd.c.y + y, Hd.top - 0.04), d)
    use('body')
    # armour: rows of square rock plates with crystal studs (no membrane, no scales)
    for i in range(4):
        for j in range(4):
            b('plate', (0.4, 0.4, 0.14), mm('rock' if (i + j) % 2 else 'main'), ((i - 1.5) * 0.44, B.front + 0.26 + j * 0.46, B.top + 0.06), bev=0.04)
    for sgn, n in LR:
        for j in range(4):
            b('side_plate', (0.12, 0.4, 0.5), mm('rock'), (sgn * (B.s.x / 2 + 0.05), B.front + 0.26 + j * 0.46, B.c.z), bev=0.04)
            cn('side_crystal', 0.08, 0.3, mm('blue'), (sgn * (B.s.x / 2 + 0.12), B.front + 0.26 + j * 0.46, B.c.z + 0.1), (sgn * 1, 0, 0.4))
    b('belly', (1.4, 1.6, 0.1), mm('belly'), (0, B.c.y, B.bot - 0.02), bev=0.03)
    # folded crystal-slab "wings": two fans of tall flat crystals rising from the shoulders, leaning outwards
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * 0.6, B.front + 0.5, B.top))
        a.wings.append('wing_' + n)
        for i in range(5):
            h = 1.6 - 0.22 * i
            x = sgn * (0.6 + 0.16 * i)
            y = B.front + 0.5 + i * 0.32
            b('slab', (0.14, 0.42, h), mm('crystal' if i % 2 == 0 else 'blue'), (x + sgn * h * 0.18, y, B.top + h / 2), rot=(0, sgn * 20, 0), bev=0.03)
            p('slab_edge', (0.16, 0.08, h * 0.9), mm('dark'), (x + sgn * h * 0.18, y + 0.2, B.top + h / 2), rot=(0, sgn * 20, 0))
            cn('slab_tip', 0.12, 0.3, mm('crystal'), (x + sgn * h * 0.36, y, B.top + h - 0.02), (sgn * 0.35, 0, 1))
    # short pillar legs get crystal knee caps
    for ft in a.bx['feet']:
        use(ft.seg)
        b('knee_cap', (ft.s.x + 0.06, ft.s.y * 0.8, 0.16), mm('main'), (ft.c.x, ft.c.y + 0.06, 0.34), bev=0.04)
        cn('knee_crystal', 0.07, 0.24, mm('blue'), (ft.c.x, ft.front + 0.1, 0.4), (0, -0.6, 0.8))
    use('body')
    # club tail ending in a crystal cluster
    tail_kit('thick', 'body', a.tail_j, 'rock', 'main', size=0.26)
    use('tail')
    for i, (dx, dz, d) in enumerate(((0, 0.2, (0, 0.6, 1)), (-0.2, 0.0, (-0.8, 0.4, 0.6)), (0.2, 0.0, (0.8, 0.4, 0.6)), (0, -0.1, (0, 1, 0.2)))):
        cn('club_crystal', 0.1, 0.45, mm('crystal' if i % 2 else 'blue'), (dx, a.tail_j[1] + 0.26 * 4.2, a.tail_j[2] - 0.08 + dz), d)
    # rarity 6: glowing gem cores in the slabs and plates, a floating ring of shards (not a gold crown), shard orbit, red aura (rays)
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i in range(4):
        p('plate_gem', (0.16, 0.16, 0.06), mm('glow' if i % 2 else 'glow2'), ((i - 1.5) * 0.44, B.front + 0.95, B.top + 0.16), rot=(0, 0, 45))
    p('chest_gem', (0.3, 0.08, 0.3), mm('gem'), (0, B.front - 0.06, B.c.z), rot=(0, 45, 0))
    for sgn, n in LR:
        use('wing_' + n)
        for i in range(5):
            h = 1.6 - 0.22 * i
            p('slab_core', (0.15, 0.2, h * 0.5), mm('glow' if i % 2 == 0 else 'glow2'), (sgn * (0.6 + 0.16 * i) + sgn * h * 0.18, B.front + 0.5 + i * 0.32, B.top + h / 2), rot=(0, sgn * 20, 0))
    use('head')
    halo_kit(Hd, 'glow2', r=0.7, n=10, dz=1.2, kind='shards')
    use('body')
    orbit_kit((0, 0.3, 1.6), 2.0, 8, 'glow', 'glow2', size=0.14, dz=0.4, shape='shard')
    aura_kit(2.1, 6, motes=12, mote_col='glow', mote_r=2.2, height=2.4, style='rays')
    return finish(a)
'''


def splice(fn, name, code):
    s = io.open(fn, encoding='utf-8').read()
    a = s.index('\ndef %s(' % name)
    b = s.index('\ndef ', a + 5) if '\ndef ' in s[a + 5:] else s.index('\nANIMALS', a)
    nxt = s.find('\nANIMALS', a)
    if nxt != -1 and nxt < b:
        b = nxt
    s = s[:a] + '\n' + code.strip('\n') + '\n\n' + s[b:]
    io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)


if __name__ == '__main__':
    splice('biome_11.py', 'coral_wyvern', CORAL)
    splice('biome_15.py', 'quartz_dragon', QUARTZ)
    print('ok')
