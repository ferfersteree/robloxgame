# Biome 16 redesigns so they do not echo earlier animals (wolf b2, bears b3, rabbit b1)
from redo_dragons import splice

HARE = r'''
def arctic_hare(row):
    """crouched snowball hare: low wide round body, ears laid flat back along the spine, giant snowshoe hind feet sticking forward"""
    a = start(row, dict(main='#ffffff', belly='#f0f4ff', dark='#3a3e4a', accent='#d0dcf0', tip='#2a2e3a', pad='#ffc8d8'), 2.1)
    B, Hd = quad(bw=1.3, bl=1.2, bh=0.9, legh=0.14, lw=0.24, hw=1.1, hd=0.86, hh=0.8, head_up=0.42, toe='dark', head_fwd=0.2, leg_fl=0.4,
                 rump=True, chest=False)
    use('body')
    b('fluff_top', (1.1, 1.0, 0.3), mm('main'), (0, B.c.y + 0.1, B.top + 0.1), bev=0.12)
    for sgn, n in LR:
        for j in range(3):
            b('side_fluff', (0.2, 0.36, 0.36), mm('accent' if j % 2 else 'main'), (sgn * (B.s.x / 2 + 0.06), B.c.y - 0.3 + j * 0.3, B.c.z - 0.1), bev=0.08)
    mz = muzzle(Hd, (0.4, 0.14, 0.24), -0.3, 'belly', nose=(0.14, 0.06, 0.08), nose_mat='pad', teeth=1)
    for sgn, n in LR:
        p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * 0.36, Hd.front - 0.012, Hd.c.z - 0.2))
        for j in range(3):
            p('whisker', (0.26, 0.02, 0.02), mm('dark'), (sgn * 0.48, Hd.front - 0.02, Hd.c.z - 0.24 + (j - 1) * 0.05), rot=(0, -sgn * (j - 1) * 10, sgn * 10))
    eyes(Hd, 0.4, 0.26, 0.06, iris='#6a5ad8', lash=True, brow='#d0dcf0', tilt=14, sleepy=0.1)
    # ears laid flat along the back (the silhouette): long slabs pointing backwards
    for sgn, n in LR:
        sg('ear_' + n, 'head', (sgn * 0.24, Hd.c.y + 0.1, Hd.top - 0.06))
        a.ears.append('ear_' + n)
        b('ear', (0.26, 0.9, 0.12), mm('main'), (sgn * 0.26, Hd.c.y + 0.56, Hd.top - 0.02), rot=(8, 0, sgn * 6), bev=0.04)
        p('ear_in', (0.14, 0.7, 0.04), mm('pad'), (sgn * 0.26, Hd.c.y + 0.5, Hd.top + 0.04), rot=(8, 0, sgn * 6))
        b('ear_tip', (0.27, 0.18, 0.13), mm('tip'), (sgn * 0.27, Hd.c.y + 1.02, Hd.top - 0.08), rot=(8, 0, sgn * 6), bev=0.03)
    use('body')
    # huge snowshoe hind feet that poke forward under the body
    for ft in a.bx['feet'][2:]:
        use(ft.seg)
        b('snowshoe', (0.36, 0.9, 0.12), mm('accent'), (ft.c.x + (0.08 if ft.c.x > 0 else -0.08), ft.c.y - 0.5, 0.06), bev=0.04)
        for j in range(3):
            p('shoe_fur', (0.1, 0.1, 0.08), mm('main'), (ft.c.x + (j - 1) * 0.1, ft.c.y - 0.96, 0.08))
            p('shoe_pad', (0.08, 0.08, 0.03), mm('pad'), (ft.c.x + (j - 1) * 0.1, ft.c.y - 0.6, 0.0))
    use('body')
    grid(B, 't', 3, 2, mm('accent'), (0.14, 0.14), name='frost', th=0.32)
    grid(a.bx['rump'], 'k', 3, 2, mm('accent'), (0.14, 0.14), name='rump_frost')
    tail_kit('pom', 'body', a.tail_j, 'main', 'main', size=0.3)
    return finish(a)
'''

WOLF = r'''
def lunar_wolf(row):
    """howling moon wolf: sits upright on its haunches (not standing), long tapered snout, tall crescent mane plates, moon pendant"""
    a = start(row, dict(main='#9aa8d8', belly='#eef2ff', dark='#3a4478', accent='#c8d0f0', mane='#5a68a8', **{'*glow': '#9ae0ff'}), 3.6)
    B, Hd = sit(bw=0.9, bd=0.9, bh=1.2, hw=0.96, hd=0.86, hh=0.8, arm=0.6, lw=0.24, foot_l=0.7, ntoe=3, foot='belly', toe='dark')
    use('head')
    sn = b('snout', (0.4, 0.6, 0.3), mm('main'), (0, Hd.front - 0.24, Hd.c.z - 0.16), bev=0.05)
    p('snout_belly', (0.34, 0.5, 0.06), mm('belly'), (0, Hd.front - 0.24, Hd.c.z - 0.33))
    b('nose', (0.18, 0.1, 0.12), mm('dark'), (0, sn.front - 0.02, sn.top - 0.06), bev=0.02)
    p('mouth', (0.04, 0.03, 0.1), mm('line'), (0, sn.front - 0.008, sn.c.z - 0.06))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.16))
    eyes(Hd, 0.32, 0.25, 0.14, iris='#5a8ad8', glow='#9ae0ff', brow='#3a4478', tilt=-14)
    # tall narrow ears leaning back
    for sgn, n in LR:
        sg('ear_' + n, 'head', (sgn * 0.26, Hd.c.y + 0.1, Hd.top))
        a.ears.append('ear_' + n)
        b('ear', (0.22, 0.14, 0.7), mm('mane'), (sgn * 0.28, Hd.c.y + 0.18, Hd.top + 0.3), rot=(-15, sgn * 8, 0), bev=0.03)
        p('ear_in', (0.1, 0.04, 0.5), mm('accent'), (sgn * 0.28, Hd.c.y + 0.1, Hd.top + 0.28), rot=(-15, sgn * 8, 0))
    use('body')
    # crescent mane: stacked plates curving from the head down the back (the silhouette)
    for i in range(6):
        ang = math.radians(20 + i * 22)
        r = 0.9
        b('mane_plate', (0.7 - 0.06 * i, 0.22, 0.3), mm('mane' if i % 2 else 'dark'), (0, 0.1 + math.sin(ang) * r * 0.6, 0.2 + 1.2 * 0.9 + math.cos(ang) * r * 0.5), rot=(math.degrees(ang) - 20, 0, 0), bev=0.04)
    fluff(Box((0, B.front - 0.07, B.c.z), (B.s.x * 0.72, 0.1, B.s.z * 0.7)), 'f', mm('belly'), 5, 1.0, 0.42)
    grid(B, 'l', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    grid(B, 'r', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    accessory('necklace', Box((0, B.front + 0.3, B.top + 0.02), (B.s.x, B.s.x, 0.2)), '#3a4478', '#ffd84a', z=B.top - 0.04)
    tail_kit('tuft', 'body', (0, a.tail_j[1], 0.3), 'main', 'belly', size=0.24)
    # rarity 4: glowing crescent moon on the chest, glowing ear tips and mane edge, star sparks
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    for i, (dx, dz, w, h) in enumerate(((-0.1, 0.0, 0.08, 0.36), (0.0, 0.2, 0.18, 0.08), (0.0, -0.2, 0.18, 0.08))):
        p('chest_moon', (w, 0.04, h), mm('glow'), (dx, B.front - 0.13, B.c.z + 0.1 + dz))
    for i in range(3):
        p('mane_glow', (0.5, 0.05, 0.05), mm('glow'), (0, 0.1 + math.sin(math.radians(20 + i * 44)) * 0.54 + 0.12, 0.2 + 1.08 + math.cos(math.radians(20 + i * 44)) * 0.45 + 0.1))
    for sgn, n in LR:
        use('ear_' + n)
        p('ear_glow', (0.1, 0.1, 0.12), mm('glow'), (sgn * 0.28, Hd.c.y + 0.3, Hd.top + 0.66))
    use('body')
    aura_kit(1.3, 4, motes=8, mote_col='glow', height=2.0)
    return finish(a)
'''

BEAR = r'''
def aurora_bear(row):
    """spirit polar bear standing up on its hind legs (biped), long neck, flowing aurora cape on the back, ice claws, star crown"""
    a = start(row, dict(main='#f6f8ff', belly='#e0eafa', dark='#5a6a9a', accent='#c8d8f0', nose='#3a3e5a',
                        **{'*glow': '#7affc8', '*glow2': '#c88aff', '*glow3': '#7ac8ff', '*gold': '#ffd84a'}), 3.0)
    B, Hd = biped(tw=1.2, td=1.0, th=1.5, legh=0.6, lw=0.5, hw=1.0, hd=1.1, hh=0.86, arm_l=1.2, arm_w=0.42, hand=0.5, shoulder=0.0,
                  foot='belly', toe='dark', hand_mat='belly')
    use('head')
    # long bear snout pointing forward, small round ears
    sn = b('snout', (0.5, 0.56, 0.4), mm('main'), (0, Hd.front - 0.24, Hd.c.z - 0.14), bev=0.07)
    b('nose', (0.22, 0.12, 0.14), mm('nose'), (0, sn.front - 0.02, sn.top - 0.08), bev=0.03)
    p('mouth', (0.04, 0.03, 0.12), mm('line'), (0, sn.front - 0.008, sn.c.z - 0.08))
    for sgn, n in LR:
        p('blush', (0.14, 0.03, 0.07), mm('pink'), (sgn * 0.34, Hd.front - 0.012, Hd.c.z - 0.2))
        b('ear', (0.24, 0.12, 0.22), mm('main'), (sgn * 0.4, Hd.c.y + 0.1, Hd.top + 0.08), bev=0.06)
        p('ear_in', (0.12, 0.04, 0.12), mm('accent'), (sgn * 0.4, Hd.c.y + 0.03, Hd.top + 0.08))
    eyes(Hd, 0.3, 0.24, 0.16, iris='#5a8ad8', glow='#7affc8', lash=True, brow='#5a6a9a', tilt=6)
    use('body')
    fluff(Box((0, B.front - 0.05, B.c.z), (B.s.x * 0.66, 0.1, B.s.z * 0.7)), 'f', mm('belly'), 5, 1.2, 0.42, th=0.07)
    grid(B, 'l', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    grid(B, 'r', 3, 3, mm('accent'), (0.12, 0.12), name='frost_fur')
    for hb_ in a.bx['hands']:
        use(hb_.seg)
        for j in range(3):
            cn('ice_claw', 0.05, 0.22, mm('glow3'), (hb_.c.x + (j - 1) * 0.14, -hb_.s.y / 2 - 0.02, hb_.c.z - 0.1), (0, -1, -0.5))
        p('wrist_frost', (hb_.s.x + 0.06, hb_.s.y + 0.06, 0.1), mm('accent'), (hb_.c.x, 0.0, hb_.top + 0.04))
    for ft in a.bx['feet']:
        use(ft.seg)
        p('foot_frost', (ft.s.x + 0.04, ft.s.y * 0.8, 0.08), mm('accent'), (ft.c.x, ft.c.y + 0.06, ft.top + 0.1))
    use('body')
    tail_kit('stub', 'body', a.tail_j, 'main', 'accent', size=0.26)
    # rarity 6: aurora cape of glowing ribbons hanging down the back (own segment, flickers), star crown, star orbits, red aura (petals)
    sg('cape', 'body', (0, B.back, B.top))
    a.glow.append('cape')
    for i, m_ in enumerate(('glow', 'glow3', 'glow2', 'glow3', 'glow')):
        x = (i - 2) * 0.24
        for j in range(4):
            p('cape_ribbon', (0.2, 0.08, 0.36), mm(m_), (x + 0.05 * math.sin(j * 1.3 + i), B.back + 0.06 + 0.06 * j, B.top - 0.2 - j * 0.38))
    p('cape_clasp', (0.9, 0.12, 0.12), mm('gold'), (0, B.back + 0.04, B.top + 0.02))
    sg('glow', 'body', tuple(B.c))
    a.glow.append('glow')
    p('chest_star', (0.26, 0.06, 0.26), mm('glow'), (0, B.front - 0.13, B.c.z + 0.3), rot=(0, 45, 0))
    use('head')
    sg('glow_h', 'head', (0, Hd.front, Hd.top))
    a.glow.append('glow_h')
    on(Hd, 'f', 0, 0.38, (0.16, 0.16), mm('glow'), th=0.035, name='fore_star', rot=(0, 45, 0))
    halo_kit(Hd, 'gold', r=0.6, n=8, dz=0.85, kind='stars')
    use('body')
    orbit_kit((0, 0.05, 1.8), 1.7, 8, 'glow', 'glow2', size=0.14, dz=0.5, shape='star')
    aura_kit(1.7, 6, motes=12, mote_col='glow', mote_r=1.8, height=2.8, style='petals')
    return finish(a)
'''

if __name__ == '__main__':
    splice('biome_16.py', 'arctic_hare', HARE)
    splice('biome_16.py', 'lunar_wolf', WOLF)
    splice('biome_16.py', 'aurora_bear', BEAR)
    print('ok')
