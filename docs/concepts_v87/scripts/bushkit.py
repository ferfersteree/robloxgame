# SpearHunt V87 - bush kit: parts as separate segments + the three Tease clips, two Open clips and their FX.
import random as _random
from faunalib import *
import faunalib as L
import kits
from kits import K, b, p, cn, sg, on, V, Box
import moves

LEN = {'Tease_Common': 75, 'Tease_Rare': 90, 'Tease_Epic': 105, 'Open_Burst': 15, 'Open_Part': 15}
EPIC_GLOW = {5: '#ffd21a', 6: '#ff2a2a'}


class Bush:
    pass


def begin_bush(nn, scale=1.0, place=(0, 0, 0)):
    B = Bush()
    B.nn, B.id = nn, 'bush_%02d' % nn
    B.coll, B.fxname = 'Bush_%02d' % nn, 'Bush_%02d_FX' % nn
    B.groups = {'big': [], 'small': []}
    B.segs, B.joint, B.bx = [], {}, {}
    B.id_ = B.id
    B.place = place
    begin(B.id, B.coll, B.fxname, place, ol=0.03)
    K.a, K.S, K.Z0, K.m = B, scale, 0.0, {}
    B.n = 0
    return B


def part(group, joint, name=None):
    """start a new bush part (own segment, pivot = joint). group: big (leaves, rocks) / small (flowers, crystals, details)"""
    B = K.a
    B.n += 1
    nm = name or '%s_%02d' % (group, B.n)
    sg(nm, 'root', joint)
    B.groups[group].append(nm)
    return nm


def mat(key, hexc, kind='studs', strength=2.8):
    aid = K.a.id
    if kind == 'neon':
        m = neon('%s_%s' % (aid, key), hexc, strength)
    elif kind == 'smooth':
        m = smooth('%s_%s' % (aid, key), hexc, 0.3)
    else:
        m = studs('%s_%s' % (aid, key), hexc)
    m['hex'] = hexc
    K.m[key] = m
    return m


def _shake(c, parts, f0, f1, amp, step=3, seed=0, z=False):
    rnd = _random.Random(seed)
    for pn in parts:
        f = f0 + rnd.randint(0, 1)
        while f <= f1:
            a_ = amp * rnd.uniform(0.5, 1.0) * rnd.choice((-1, 1))
            k(c, pn, f, rot=(a_ * 0.4, a_, a_ * 0.3), loc=(0, 0, abs(a_) * 0.012 if z else 0))
            f += step
        k(c, pn, f1 + step, rot=(0, 0, 0), loc=(0, 0, 0))


def anims(B):
    big, small = B.groups['big'], B.groups['small']
    parts = big + small
    for cname in ('Tease_Common', 'Tease_Rare', 'Tease_Epic'):
        clip(cname, LEN[cname])
        L_ = LEN[cname]
        for pn in parts:
            k(cname, pn, 1, rot=(0, 0, 0), loc=(0, 0, 0), scale=1.0)
        for i, pn in enumerate(big[:5]):                       # quiet rustle
            for f, a_ in ((8 + i * 3, 4), (11 + i * 3, -4), (14 + i * 3, 0)):
                k(cname, pn, f, rot=(0, a_, 0))
        _shake(cname, big, 28, 46, 6, 3, seed=1)               # stronger
        _shake(cname, small, 28, 46, 14, 3, seed=2)
        hold_end = 60 if cname == 'Tease_Common' else 66       # fake pause
        for pn in parts:
            k(cname, pn, 52, rot=(0, 0, 0), loc=(0, 0, 0), scale=1.0)
            k(cname, pn, hold_end, rot=(0, 0, 0), loc=(0, 0, 0), scale=1.0)
        amp = {'Tease_Common': 8, 'Tease_Rare': 11, 'Tease_Epic': 14}[cname]
        _shake(cname, big, hold_end + 2, L_ - 6, amp, 2, seed=3, z=True)
        _shake(cname, small, hold_end + 2, L_ - 6, amp * 1.6, 2, seed=4, z=True)
        for pn in big[:4]:
            k(cname, pn, L_ - 4, scale=(1.08, 1.12, 1.06), loc=(0, -0.15, 0))
        for pn in parts:
            k(cname, pn, L_, scale=1.0, loc=(0, 0, 0), rot=(0, 0, 0))
        if cname == 'Tease_Epic':
            for i, f in enumerate(range(72, 100, 2)):
                k(cname, 'root', f, loc=(0.06 * (1 if i % 2 else -1), 0, 0.05 * (i % 2)))
            for f in (1, 71, 101, 105):
                k(cname, 'root', f, loc=(0, 0, 0))
    clip('Open_Burst', 15)
    clip('Open_Part', 15)
    rnd = _random.Random(9)
    for pn in parts:
        j = Vector(V(B.joint[pn]))
        d = Vector((j.x, -0.6, 0.6)).normalized() if abs(j.x) > 0.2 else Vector((rnd.uniform(-0.5, 0.5), -0.6, 1)).normalized()
        dist = 3.0 if pn in big else 4.5
        k('Open_Burst', pn, 1, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0)
        k('Open_Burst', pn, 8, loc=tuple(d * dist * 0.7), rot=(rnd.uniform(-90, 90), rnd.uniform(-90, 90), 0), scale=0.8)
        k('Open_Burst', pn, 15, loc=tuple(d * dist + Vector((0, 0, -0.8))), rot=(rnd.uniform(-180, 180), rnd.uniform(-180, 180), 0), scale=0.0)
        side = -1 if j.x < 0 else 1
        k('Open_Part', pn, 1, loc=(0, 0, 0), rot=(0, 0, 0))
        k('Open_Part', pn, 7, loc=(side * 1.6, 0.2, 0), rot=(0, side * 25, 0))
        k('Open_Part', pn, 15, loc=(side * 1.8, 0.3, 0), rot=(0, side * 30, 0))


def fx_build(B, size, has_r6=True):
    """FX sets in clip-local frames: Bush_NN_FX_Common / _Rare / _Epic5 / _Epic6"""
    th = moves.THEME
    base = Vector(B.place)
    W, D, H = size
    notes = {}
    variants = [('Tease_Common', 'Common', None), ('Tease_Rare', 'Rare', None), ('Tease_Epic', 'Epic5', 5)]
    if has_r6:
        variants.append(('Tease_Epic', 'Epic6', 6))
    root_fx = G.fxc
    for cname, tag, rar in variants:
        sub = get_coll('%s_%s' % (B.fxname, tag), root_fx)
        G.fxc = sub
        fx(True)
        L_ = LEN[cname]
        rnd = _random.Random(len(tag) * 17 + B.nn)
        bits = [studs('%s_fxbit%d' % (B.id, i), h) for i, h in enumerate(th['bits'])]
        nl = {'Common': 8, 'Rare': 12}.get(tag, 18)
        for i in range(nl):
            t0 = rnd.randint(28, L_ - 12)
            ob = blk('%s_bit_%d' % (tag, i), (0.24, 0.24, 0.06), bits[i % len(bits)], (0, 0, 0), bev=0.02)
            p0 = base + Vector((rnd.uniform(-0.28, 0.28) * W, rnd.uniform(-0.25, 0.1) * D, rnd.uniform(0.35, 0.85) * H))
            p1 = p0 + Vector((rnd.uniform(-1.5, 1.5), rnd.uniform(-1.8, -0.3), rnd.uniform(0.6, 1.6)))
            fxkey(ob, 1, loc=p0, scale=0)
            fxkey(ob, t0, loc=p0, scale=0)
            fxkey(ob, t0 + 2, loc=p0, scale=1)
            fxkey(ob, t0 + 10, loc=p1, rot=(rnd.uniform(0, 360), 160, 90))
            fxkey(ob, t0 + 22, loc=(p1.x, p1.y, max(0.05, p1.z - 2.0)), rot=(rnd.uniform(0, 360), 300, 180), scale=0.0)
        note = ['28–%d: %d частиц (%s, %s) вылетают из куста' % (L_ - 12, nl, th['bit_name'], ' / '.join(th['bits']))]
        if tag != 'Common':
            col = th['glow'] if tag == 'Rare' else EPIC_GLOW[rar]
            em = neon('%s_eyes_%s' % (B.id, tag), col, 4.0)
            em['hex'] = col
            hole_m = smooth('%s_hole' % B.id, '#0e1016', 0.9)
            yf = -D * 0.5 + 0.1
            for (fa, fb_, x) in ((40, 50, -0.12 * W), (70, 78, 0.14 * W)):
                hole = blk('%s_hole_%d' % (tag, fa), (0.9, 0.06, 0.5), hole_m, (0, 0, 0), bev=0.05, ol=0)
                ph = base + Vector((x, yf - 0.06, 0.3 * H))
                fxkey(hole, 1, loc=ph, scale=0)
                fxkey(hole, fa - 1, loc=ph, scale=0)
                fxkey(hole, fa + 1, scale=1)
                fxkey(hole, fb_, scale=1)
                fxkey(hole, fb_ + 2, scale=0)
                for s in (-1, 1):
                    e = blk('%s_eye_%d_%s' % (tag, fa, 'L' if s < 0 else 'R'), (0.16, 0.05, 0.12), em, (0, 0, 0), bev=0.02)
                    q = base + Vector((x + s * 0.22, yf - 0.12, 0.3 * H + 0.02))
                    fxkey(e, 1, loc=q, scale=0, alpha=1)
                    fxkey(e, fa, loc=q, scale=0, alpha=1)
                    fxkey(e, fa + 2, loc=q, scale=1, alpha=1)
                    fxkey(e, fa + 5, scale=(1, 1, 0.1))
                    fxkey(e, fa + 6, scale=1)
                    fxkey(e, fb_, scale=1)
                    fxkey(e, fb_ + 2, scale=0)
            # glowing elements growing on the bush itself
            ng = 6 if tag == 'Rare' else 10
            for i in range(ng):
                g_ = blk('%s_gem_%d' % (tag, i), (0.22, 0.22, 0.3), em, (0, 0, 0), bev=0.05)
                ang = math.radians(i * 360.0 / ng + 20)
                q = base + Vector((math.cos(ang) * W * 0.36, -abs(math.sin(ang)) * D * 0.42, H * (0.35 + 0.5 * ((i * 5) % ng) / ng)))
                t0 = 30 + i * 3
                fxkey(g_, 1, loc=q, scale=0, alpha=1, rot=(20, 30, 0))
                fxkey(g_, t0, scale=0, alpha=1)
                fxkey(g_, t0 + 5, scale=1.2, alpha=1)
                fxkey(g_, t0 + 9, scale=0.8, alpha=1)
                fxkey(g_, L_ - 8, scale=1.3, alpha=1, rot=(20, 30, 90))
                fxkey(g_, L_, scale=0, alpha=1)
            note.append('40–50 и 70–78: два светящихся глаза %s в тёмной «дыре», моргают и прячутся' % col)
            note.append('с 30 кадра на кусте загораются %d светящихся элементов %s (Neon), гаснут к концу' % (ng, col))
        if rar:
            col = EPIC_GLOW[rar]
            glow = neon('%s_epic%d' % (B.id, rar), col, 5.0)
            glow['hex'] = col
            core = blk('%s_core' % tag, (1.2, 1.2, 1.2), glow, (0, 0, 0), bev=0.2)
            q = base + Vector((0, 0.1, H * 0.4))
            fxkey(core, 1, loc=q, scale=0, alpha=1)
            fxkey(core, 60, scale=0, alpha=1)
            fxkey(core, 75, scale=1.4, alpha=0.6)
            fxkey(core, 95, scale=2.3, alpha=0.8, rot=(0, 0, 45))
            fxkey(core, 101, scale=2.8, alpha=1, rot=(0, 0, 90))
            fxkey(core, 105, scale=3.6, alpha=0)
            for r in range(3):
                ring = torus('%s_ring_%d' % (tag, r), 1.5, 0.08, glow, 4, 4)
                pr = base + Vector((0, 0, 0.06))
                t0 = 72 + r * 9
                fxkey(ring, 1, loc=pr, scale=0, alpha=1, rot=(0, 0, 45))
                fxkey(ring, t0, scale=0.4, alpha=1)
                fxkey(ring, t0 + 14, scale=W * 0.5, alpha=0)
            for i in range(14):
                sp = blk('%s_spark_%d' % (tag, i), (0.12, 0.12, 0.12), glow, (0, 0, 0), bev=0.02)
                ang = math.radians(i * 360 / 14)
                p0 = base + Vector((math.cos(ang) * 1.0, math.sin(ang) * 0.6, H * 0.45))
                p1 = p0 + Vector((math.cos(ang) * 2.2, math.sin(ang) * 1.4, rnd.uniform(0.5, 2.0)))
                t0 = 78 + (i % 5) * 4
                fxkey(sp, 1, loc=p0, scale=0, alpha=1)
                fxkey(sp, t0, loc=p0, scale=1, alpha=1)
                fxkey(sp, t0 + 14, loc=p1, scale=0.3, alpha=0, rot=(90, 90, 0))
            for i in range(10):
                d_ = blk('%s_dust_%d' % (tag, i), (0.35, 0.35, 0.35), ghost('%s_dust' % B.id, th['dust'], 1.1, 0.85, 1.2), (0, 0, 0), bev=0.07)
                ang = math.radians(i * 36)
                p0 = base + Vector((math.cos(ang) * W * 0.4, math.sin(ang) * D * 0.45, 0.15))
                fxkey(d_, 1, loc=p0, scale=0, alpha=1)
                fxkey(d_, 72 + i, loc=p0, scale=0.4, alpha=1)
                fxkey(d_, 92 + i, loc=p0 + Vector((math.cos(ang), math.sin(ang), 0.5)), scale=1.6, alpha=0)
            ln = '%s_EpicLight%d' % (B.coll, rar)
            ld = bpy.data.lights.get(ln) or bpy.data.lights.new(ln, 'POINT')
            lo = bpy.data.objects.get(ln) or bpy.data.objects.new(ln, ld)
            if lo.name not in sub.objects:
                sub.objects.link(lo)
            lo.location = base + Vector((0, -D * 0.45, H * 0.45))
            ld.color = H_(col)
            ld.shadow_soft_size = 1.0
            for f, e in ((1, 0), (60, 0), (80, 800), (95, 1500), (101, 4000), (105, 0)):
                ld.energy = e
                ld.keyframe_insert('energy', frame=f)
            note.append('60–105: внутри разгорается ядро света %s, 72–100 куст подпрыгивает и земля трясётся, 3 кольца по земле (72, 81, 90), 14 искр, 10 облачков пыли, 101–105 вспышка'
                        % col)
            note.append('PointLight %s: Brightness 0 → 8 → 15 → 40 (кадры 60 / 80 / 95 / 101) → 0, Range 16; тряска камеры 0.06 stud' % col)
        notes[tag] = note
        fx(False)
    G.fxc = root_fx
    return notes


def H_(col):
    return H(col)[:3]


def finish_bush(B, has_r6=True, target_w=7.0):
    """assemble, clips, FX, bake. returns stats dict"""
    assemble()
    anims(B)
    st = L.stats(B.id, B.coll)
    notes = fx_build(B, st['size'], has_r6)
    bake_actions()
    G.root['info'] = json.dumps(dict(fx_notes=notes, has_r6=has_r6, groups={k_: len(v) for k_, v in B.groups.items()}))
    return st
