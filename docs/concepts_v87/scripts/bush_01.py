from faunalib import *

ID = 'bush_01'
BIOME, NAME = 1, 'Forest Edge'
COVER = {}            # CoverScale per animal id (1.0 = this bush as is)
LEN = {'Tease_Common': 75, 'Tease_Rare': 90, 'Tease_Epic': 105, 'Open_Burst': 15, 'Open_Part': 15}
EPIC_GLOW = {5: '#ffd21a', 6: '#ff2a2a'}


def build(place=(0, 0, 0)):
    begin(ID, 'Bush_01', 'Bush_01_FX', place, ol=0.03)
    leaf = studs('b1_leaf', '#3fa83a')
    leaf2 = studs('b1_leaf2', '#5cc23e')
    leaf3 = studs('b1_leaf3', '#2e8a34')
    stem = studs('b1_stem', '#6b4a2a')
    petal_p = studs('b1_petal_pink', '#ff8fc0')
    petal_y = studs('b1_petal_yel', '#ffd84a')
    petal_w = studs('b1_petal_wht', '#ffffff')
    core = studs('b1_core', '#ffb020')
    berry = studs('b1_berry', '#e8343a')
    rnd = random.Random(101)
    G.bush_parts = []
    # trunk / stems
    seg('stem_0', 'root', (0, 0.3, 0))
    blk('stem_0', (0.5, 0.5, 1.6), stem, (0, 0.3, 0.8))
    for i, (x, y) in enumerate(((-1.2, 0.2), (1.3, 0.4))):
        seg('stem_%d' % (i + 1), 'root', (x * 0.5, 0.3, 0.6))
        blk('stem_%d' % (i + 1), (0.3, 0.3, 1.3), stem, (x, y, 1.0), rot=(0, -x * 25, 0))
    # leaf blocks: three layers of big cubes (each a separate part that can sway / fly)
    layout = [(-2.4, 0.2, 1.0, 1.7), (-1.0, -0.3, 0.9, 1.9), (0.6, -0.4, 0.95, 2.0), (2.2, 0.0, 1.0, 1.8),
              (-1.7, 0.9, 1.1, 1.9), (0.0, 0.9, 1.2, 2.1), (1.7, 1.0, 1.1, 1.9),
              (-1.3, 0.2, 2.5, 1.8), (0.4, 0.1, 2.7, 2.0), (1.8, 0.4, 2.4, 1.7), (-0.5, 0.8, 3.6, 1.7), (1.0, 0.7, 3.5, 1.5),
              (-2.6, -0.2, 2.2, 1.2), (2.7, -0.1, 2.0, 1.2)]
    mats = [leaf, leaf2, leaf3]
    for i, (x, y, z, s) in enumerate(layout):
        seg('leaf_%d' % i, 'root', (x, y, max(0.0, z - s / 2)))
        blk('leaf_%d' % i, (s, s * 0.95, s * 0.9), mats[i % 3], (x, y, z), rot=(0, 0, rnd.uniform(-12, 12)), bev=0.1)
    # flowers on top/front: stalk + 4 petals + core, one segment each
    flw = [(-2.0, -0.85, 1.9, petal_p), (-0.6, -1.25, 1.5, petal_y), (0.9, -1.3, 2.0, petal_w), (2.3, -0.9, 1.7, petal_p),
           (-1.0, -0.6, 3.3, petal_y), (0.9, -0.5, 3.6, petal_p), (-0.1, 0.0, 4.4, petal_w), (2.0, -0.4, 3.0, petal_y)]
    for i, (x, y, z, pm) in enumerate(flw):
        seg('flower_%d' % i, 'root', (x, y + 0.2, z - 0.1))
        for j, (dx, dz) in enumerate(((0.16, 0), (-0.16, 0), (0, 0.16), (0, -0.16))):
            blk('flower_%d_p%d' % (i, j), (0.2, 0.08, 0.2), pm, (x + dx, y, z + dz), bev=0.03)
        blk('flower_%d_c' % i, (0.16, 0.1, 0.16), core, (x, y - 0.04, z), bev=0.03, ol=0.012)
    # berries
    for i in range(5):
        x, z = rnd.uniform(-2.2, 2.2), rnd.uniform(0.8, 3.2)
        seg('berry_%d' % i, 'root', (x, -1.2, z))
        blk('berry_%d' % i, (0.18, 0.18, 0.18), berry, (x, -1.25, z), bev=0.04, ol=0.012)
    assemble()
    for s in list(G.segs):
        if s != 'root':
            G.bush_parts.append(s)
    anims()
    build_fx()
    return bake_actions()


def _shake(clipname, parts, f0, f1, amp, freq=3, seed=0, z=False):
    rnd = random.Random(seed)
    for p in parts:
        ph = rnd.uniform(0, 6.28)
        a0 = amp * rnd.uniform(0.6, 1.0)
        f = f0
        i = 0
        while f <= f1:
            s = 1 if i % 2 == 0 else -1
            k(clipname, p, f, rot=(s * a0 * 0.5, s * a0, s * a0 * 0.3 if z else 0))
            f += freq
            i += 1
        k(clipname, p, f1 + freq, rot=(0, 0, 0))


def anims():
    parts = G.bush_parts
    leaves = [p for p in parts if p.startswith('leaf')]
    flowers = [p for p in parts if p.startswith('flower')]
    small = [p for p in parts if p.startswith('flower') or p.startswith('berry')]
    for cname in ('Tease_Common', 'Tease_Rare', 'Tease_Epic'):
        clip(cname, LEN[cname])
        L_ = LEN[cname]
        for p in parts:
            k(cname, p, 1, rot=(0, 0, 0), loc=(0, 0, 0), scale=1.0)
        # phase 1: quiet rustle (a few leaves only)
        for i, p in enumerate(leaves[:5]):
            for f, a in ((8 + i * 3, 4), (11 + i * 3, -4), (14 + i * 3, 0)):
                k(cname, p, f, rot=(0, a, 0))
        # phase 2: stronger shaking
        _shake(cname, leaves, 28, 46, 6, 3, seed=1)
        _shake(cname, small, 28, 46, 14, 3, seed=2)
        # fake pause: silence
        for p in parts:
            k(cname, p, 52, rot=(0, 0, 0), loc=(0, 0, 0), scale=1.0)
        hold_end = 60 if cname == 'Tease_Common' else 66
        for p in parts:
            k(cname, p, hold_end, rot=(0, 0, 0), loc=(0, 0, 0), scale=1.0)
        # phase 3: big shake to the end, front leaves bulge
        amp = {'Tease_Common': 8, 'Tease_Rare': 11, 'Tease_Epic': 14}[cname]
        _shake(cname, leaves, hold_end + 2, L_ - 4, amp, 2, seed=3, z=True)
        for p in leaves[:4]:
            k(cname, p, L_ - 6, scale=(1.08, 1.12, 1.06), loc=(0, -0.15, 0))
            k(cname, p, L_, scale=1.0, loc=(0, 0, 0), rot=(0, 0, 0))
        # epic: whole bush hops / ground shake
        if cname == 'Tease_Epic':
            for i, f in enumerate(range(72, 100, 2)):
                k(cname, 'root', f, loc=(0.06 * (1 if i % 2 else -1), 0, 0.05 * (i % 2)))
            k(cname, 'root', 1, loc=(0, 0, 0))
            k(cname, 'root', 71, loc=(0, 0, 0))
            k(cname, 'root', 101, loc=(0, 0, 0))
            k(cname, 'root', 105, loc=(0, 0, 0))
    # Open_Burst: parts fly outward/up and shrink (15 frames). Open_Part: parts slide to the sides and back down (15 frames)
    clip('Open_Burst', 15)
    clip('Open_Part', 15)
    rnd = random.Random(9)
    for p in parts:
        j = G.segs[p]['joint']
        d = Vector((j.x, -0.6, 0.6)).normalized() if abs(j.x) > 0.2 else Vector((rnd.uniform(-0.5, 0.5), -0.6, 1)).normalized()
        dist = 3.0 if p.startswith('leaf') else 4.5
        k('Open_Burst', p, 1, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0)
        k('Open_Burst', p, 8, loc=tuple(d * dist * 0.7), rot=(rnd.uniform(-90, 90), rnd.uniform(-90, 90), 0), scale=0.8)
        k('Open_Burst', p, 15, loc=tuple(d * dist + Vector((0, 0, -0.8))), rot=(rnd.uniform(-180, 180), rnd.uniform(-180, 180), 0), scale=0.0)
        side = -1 if j.x < 0 else 1
        k('Open_Part', p, 1, loc=(0, 0, 0), rot=(0, 0, 0))
        k('Open_Part', p, 7, loc=(side * 1.6, 0.2, 0), rot=(0, side * 25, 0))
        k('Open_Part', p, 15, loc=(side * 1.8, 0.3, 0), rot=(0, side * 30, 0))


def build_fx():
    """three FX sets in clip-local frames: <Bush_01_FX_Common/Rare/Epic>"""
    base = G.root.location
    for cname in ('Tease_Common', 'Tease_Rare', 'Tease_Epic'):
        sub = get_coll('Bush_01_FX_' + cname.split('_')[1], G.fxc)
        keep = G.fxc
        G.fxc = sub
        fx(True)
        L_ = LEN[cname]
        rnd = random.Random(len(cname))
        leafm = studs('b1_fx_leaf', '#5cc23e')
        petal = studs('b1_fx_petal', '#ff8fc0')
        n_leaves = {'Tease_Common': 8, 'Tease_Rare': 12, 'Tease_Epic': 18}[cname]
        for i in range(n_leaves):
            t0 = rnd.randint(28, L_ - 12)
            ob = blk('%s_leaf_%d' % (cname, i), (0.24, 0.24, 0.05), leafm if i % 3 else petal, (0, 0, 0), bev=0.02)
            p0 = base + Vector((rnd.uniform(-1.8, 1.8), rnd.uniform(-0.8, 0.4), rnd.uniform(1.5, 3.8)))
            p1 = p0 + Vector((rnd.uniform(-1.5, 1.5), rnd.uniform(-1.8, -0.3), rnd.uniform(0.6, 1.6)))
            fxkey(ob, 1, loc=p0, scale=0)
            fxkey(ob, t0, loc=p0, scale=0)
            fxkey(ob, t0 + 2, loc=p0, scale=1)
            fxkey(ob, t0 + 10, loc=p1, rot=(rnd.uniform(0, 360), 160, 90))
            fxkey(ob, t0 + 22, loc=(p1.x, p1.y, max(0.05, p1.z - 2.0)), rot=(rnd.uniform(0, 360), 300, 180), scale=0.0)
        if cname != 'Tease_Common':
            col = '#fff36a' if cname == 'Tease_Rare' else '#ffd21a'
            em = neon('b1_eyes_' + cname, col, 4.0)
            hole_m = smooth('b1_hole', '#0e1a10', 0.9)
            for (fa, fb_, x) in ((40, 50, -0.8), (70, 78, 0.9)):
                hole = blk('%s_hole_%d' % (cname, fa), (0.9, 0.06, 0.5), hole_m, (0, 0, 0), bev=0.05, ol=0)
                ph = base + Vector((x, -1.56, 1.4))
                fxkey(hole, 1, loc=ph, scale=0)
                fxkey(hole, fa - 1, loc=ph, scale=0)
                fxkey(hole, fa + 1, scale=1)
                fxkey(hole, fb_, scale=1)
                fxkey(hole, fb_ + 2, scale=0)
                for s in (-1, 1):
                    e = blk('%s_eye_%d_%d' % (cname, fa, s), (0.16, 0.05, 0.12), em, (0, 0, 0), bev=0.02)
                    p = base + Vector((x + s * 0.22, -1.62, 1.42))
                    fxkey(e, 1, loc=p, scale=0, alpha=1)
                    fxkey(e, fa, loc=p, scale=0, alpha=1)
                    fxkey(e, fa + 2, loc=p, scale=1, alpha=1)
                    fxkey(e, fa + 5, scale=(1, 1, 0.1))      # blink
                    fxkey(e, fa + 6, scale=1)
                    fxkey(e, fb_, scale=1)
                    fxkey(e, fb_ + 2, scale=0)
        if cname == 'Tease_Epic':
            glow = neon('b1_epic_glow', EPIC_GLOW[5], 5.0)
            core = blk('Tease_Epic_core', (1.2, 1.2, 1.2), glow, (0, 0, 0), bev=0.2)
            p = base + Vector((0, 0.1, 1.8))
            fxkey(core, 1, loc=p, scale=0, alpha=1)
            fxkey(core, 60, scale=0, alpha=1)
            fxkey(core, 75, scale=1.4, alpha=0.6)
            fxkey(core, 95, scale=2.3, alpha=0.8, rot=(0, 0, 45))
            fxkey(core, 101, scale=2.8, alpha=1, rot=(0, 0, 90))
            fxkey(core, 105, scale=3.6, alpha=0)
            for r in range(3):
                ring = torus('Tease_Epic_ring_%d' % r, 1.5, 0.08, glow, 4, 4)
                pr = base + Vector((0, 0, 0.06))
                t0 = 72 + r * 9
                fxkey(ring, 1, loc=pr, scale=0, alpha=1, rot=(0, 0, 45))
                fxkey(ring, t0, scale=0.4, alpha=1)
                fxkey(ring, t0 + 14, scale=3.5, alpha=0)
            for i in range(14):
                sp = blk('Tease_Epic_spark_%d' % i, (0.12, 0.12, 0.12), glow, (0, 0, 0), bev=0.02)
                a = math.radians(i * 360 / 14)
                p0 = base + Vector((math.cos(a) * 1.0, math.sin(a) * 0.6, 2.0))
                p1 = p0 + Vector((math.cos(a) * 2.2, math.sin(a) * 1.4, rnd.uniform(0.5, 2.0)))
                t0 = 78 + (i % 5) * 4
                fxkey(sp, 1, loc=p0, scale=0, alpha=1)
                fxkey(sp, t0, loc=p0, scale=1, alpha=1)
                fxkey(sp, t0 + 14, loc=p1, scale=0.3, alpha=0, rot=(90, 90, 0))
            for i in range(10):
                d = blk('Tease_Epic_dust_%d' % i, (0.35, 0.35, 0.35), ghost('b1_dust', '#efe0bc', 1.1, 0.85, 1.2), (0, 0, 0), bev=0.07)
                a = math.radians(i * 36)
                p0 = base + Vector((math.cos(a) * 2.6, math.sin(a) * 1.6, 0.15))
                fxkey(d, 1, loc=p0, scale=0, alpha=1)
                fxkey(d, 72 + i, loc=p0, scale=0.4, alpha=1)
                fxkey(d, 92 + i, loc=p0 + Vector((math.cos(a), math.sin(a), 0.5)), scale=1.6, alpha=0)
            ld = bpy.data.lights.get('Bush_01_EpicLight') or bpy.data.lights.new('Bush_01_EpicLight', 'POINT')
            lo = bpy.data.objects.get('Bush_01_EpicLight') or bpy.data.objects.new('Bush_01_EpicLight', ld)
            if lo.name not in sub.objects:
                sub.objects.link(lo)
            lo.location = base + Vector((0, -1.5, 2.0))
            ld.color = H(EPIC_GLOW[5])[:3]
            ld.shadow_soft_size = 1.0
            for f, e in ((1, 0), (60, 0), (80, 800), (95, 1500), (101, 4000), (105, 0)):
                ld.energy = e
                ld.keyframe_insert('energy', frame=f)
        fx(False)
        G.fxc = keep
