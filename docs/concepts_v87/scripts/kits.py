# SpearHunt V87 - body kits: archetype skeletons, face kit, pattern fillers, rarity kits.
# Animals are designed in "nominal" units (a chibi about 2 units tall) and scaled to the target height (K.S).
# Every helper returns a Box (nominal centre + size) so details can be placed relative to a block face.
import random as _random
from faunalib import *
import faunalib as L


class K:
    S = 1.0        # nominal -> studs
    Z0 = 0.0       # nominal z of the origin (0 = ground; body centre for flyers / swimmers)
    a = None
    m = {}         # palette: key -> material


class Box:
    def __init__(self, c, s, seg=None):
        self.c, self.s, self.seg = Vector(c), Vector(s), seg

    def pt(self, f, u=0.0, v=0.0, out=0.0):
        """point on a face: f front(-Y) k back(+Y) l(-X) r(+X) t top u under; u,v in -0.5..0.5 of the face"""
        c, s = self.c, self.s
        if f == 'f':
            return Vector((c.x + u * s.x, c.y - s.y / 2 - out, c.z + v * s.z))
        if f == 'k':
            return Vector((c.x + u * s.x, c.y + s.y / 2 + out, c.z + v * s.z))
        if f == 'l':
            return Vector((c.x - s.x / 2 - out, c.y + u * s.y, c.z + v * s.z))
        if f == 'r':
            return Vector((c.x + s.x / 2 + out, c.y + u * s.y, c.z + v * s.z))
        if f == 't':
            return Vector((c.x + u * s.x, c.y + v * s.y, c.z + s.z / 2 + out))
        return Vector((c.x + u * s.x, c.y + v * s.y, c.z - s.z / 2 - out))

    @property
    def top(self):
        return self.c.z + self.s.z / 2

    @property
    def bot(self):
        return self.c.z - self.s.z / 2

    @property
    def front(self):
        return self.c.y - self.s.y / 2

    @property
    def back(self):
        return self.c.y + self.s.y / 2


class Animal:
    pass


def V(p):
    return (p[0] * K.S, p[1] * K.S, (p[2] - K.Z0) * K.S)


def b(name, size, mat, loc, rot=(0, 0, 0), bev=0.04, **kw):
    """bevelled structural block (nominal units)"""
    blk(name, [x * K.S for x in size], mat, V(loc), rot, bev=bev * K.S, **kw)
    return Box(loc, size, G.seg)


def p(name, size, mat, loc, rot=(0, 0, 0), **kw):
    """sharp detail cube, 12 tris, no outline"""
    pix(name, [x * K.S for x in size], mat, V(loc), rot, **kw)
    return Box(loc, size, G.seg)


def cn(name, r, h, mat, loc, d=(0, 0, 1), n=4, ol=0.012, roll=45):
    """square pyramid spike / horn pointing along d"""
    cone(name, r * K.S, h * K.S, mat, n, loc=V(loc), rot=aim(d, roll), ol=ol * K.S ** 0.5)
    return Box(loc, (r * 2, r * 2, h), G.seg)


def sg(name, parent, joint):
    seg(name, parent, V(joint))
    if name not in K.a.segs:
        K.a.segs.append(name)
    K.a.joint[name] = Vector(joint)


def on(box, f, u, v, size, mat, th=0.03, name='d', rot=(0, 0, 0)):
    """detail plate lying on a face of box. size = (along u, along v) nominal"""
    c = box.pt(f, u, v, th / 2 - 0.004)
    if f in 'fk':
        s = (size[0], th, size[1])
    elif f in 'lr':
        s = (th, size[0], size[1])
    else:
        s = (size[0], size[1], th)
    return p(name, s, mat, c, rot)


def spots(box, faces, n, mat, size=0.16, seed=0, name='spot', jitter=0.5):
    """n square patches scattered on the given faces of a block (pattern filler)"""
    rnd = _random.Random(seed * 7919 + len(faces) * 31 + n)
    out = []
    cells = [(-0.3, -0.25), (0.3, 0.25), (0.0, 0.0), (-0.3, 0.28), (0.3, -0.28), (0.0, 0.32), (0.0, -0.32), (-0.33, 0.0), (0.33, 0.0)]
    i = 0
    while len(out) < n:
        f = faces[i % len(faces)]
        u, v = cells[(i // len(faces) + seed) % len(cells)]
        u += rnd.uniform(-0.06, 0.06) * jitter
        v += rnd.uniform(-0.06, 0.06) * jitter
        sz = size * rnd.choice((0.75, 1.0, 1.0, 1.25))
        out.append(on(box, f, u, v, (sz, sz), mat, name=name))
        i += 1
    return out


def stripes(box, faces, n, mat, w=0.09, name='stripe', span=0.8, vertical=True):
    """n stripes on each listed face (vertical on side faces, across on top)"""
    out = []
    for f in faces:
        for i in range(n):
            t = (i + 0.5) / n - 0.5
            if f in 'lr':
                ln = box.s.z * 0.55 * (1.0 if i % 2 == 0 else 0.75)
                out.append(on(box, f, t * span, 0.5 - ln / box.s.z / 2 - 0.02, (w, ln), mat, name=name))
            elif f in 'tu':
                out.append(on(box, f, 0, t * span, (box.s.x * 0.7 * (1.0 if i % 2 == 0 else 0.7), w), mat, name=name))
            else:
                ln = box.s.z * 0.5
                out.append(on(box, f, t * span, 0.5 - ln / box.s.z / 2 - 0.02, (w, ln), mat, name=name))
    return out


def fluff(box, f, mat, rows=3, w0=0.6, top=0.3, name='fluff', th=0.05):
    """stepped bib / fringe: rows of shrinking plates going down from v=top"""
    out = []
    for i in range(rows):
        w = box.s.x * w0 * (1 - i / (rows + 0.6)) if f in 'fktu' else box.s.y * w0 * (1 - i / (rows + 0.6))
        out.append(on(box, f, 0, top - i * 0.12 / max(box.s.z, 0.3) * 1.0, (w, 0.1), mat, th=th - i * 0.008, name=name))
    return out


def tufts(pts, size, mat, name='tuft'):
    return [p(name, (size, size, size), mat, q) for q in pts]


def toes(foot, n, mat, size=(0.06, 0.05, 0.07), name='toe'):
    out = []
    for j in range(n):
        u = ((j + 0.5) / n - 0.5) * 0.72
        c = foot.pt('f', u, 0.0, size[1] / 2 - 0.01)
        out.append(p(name, size, mat, (c.x, c.y, foot.c.z)))
    return out


# ---------------------------------------------------------------- palette
def begin_animal(row, pal, nominal_h, hover=0.0, z0=0.0, ol=0.025):
    """row = roster row. pal = dict key -> hex (studs) ; keys starting with '!' are smooth, '*' neon"""
    a = Animal()
    a.row, a.id, a.name, a.rarity, a.kind = row, row['id'], row['name'], row['rarity'], row['kind']
    a.H = row['height']
    a.method, a.gesture, a.open = row['method'], row['gesture'], row['open']
    a.segs, a.joint, a.bx = [], {}, {}
    a.legs, a.arms, a.ears, a.wings, a.tail, a.extra_idle, a.extra_reveal = [], [], [], [], [], [], []
    a.hover = hover
    a.place = getattr(K, 'place', (0, 0, 0))
    K.a = a
    K.S = a.H / nominal_h
    K.Z0 = z0
    a.S = K.S
    pl = (a.place[0], a.place[1], a.place[2] + hover)
    begin(a.id, 'AN_' + a.id, 'AN_%s_FX' % a.id, pl, ol=ol * max(1.0, K.S) ** 0.6)
    K.m = {}
    base = dict(pal)
    base.setdefault('!line', '#2a2030')
    base.setdefault('!white', '#ffffff')
    base.setdefault('!pink', '#ff9db4')
    base.setdefault('!nose', '#2b1a20')
    for k, v in base.items():
        setm(k, v)
    return a


def setm(k, v, strength=None):
    aid = K.a.id
    if k.startswith('!'):
        K.m[k[1:]] = smooth('%s_%s' % (aid, k[1:]), v, 0.3)
    elif k.startswith('*'):
        K.m[k[1:]] = neon('%s_%s' % (aid, k[1:]), v, strength or 2.8)
    else:
        K.m[k] = studs('%s_%s' % (aid, k), v)
    K.m[k.lstrip('!*')]['hex'] = v
    return K.m[k.lstrip('!*')]


def mm(k):
    return K.m[k]


# ---------------------------------------------------------------- face kit
def eyes(hb, size=0.34, ex=0.25, ez=0.08, iris='#7a4a22', lash=False, brow=None, tilt=0.0, sleepy=0.0, glow=None, w=0.82,
         pupil='#1f1520', head='head', bdz=0.5):
    """big anime eyes on the front face of the head block; each eye is its own segment (blink = scale Z)"""
    k = K.S
    s = size * hb.s.z
    y = hb.front
    z = hb.c.z + ez * hb.s.z
    x = ex * hb.s.x
    dark = smooth('eye_dark', '#1f1520', 0.2)
    wm = smooth('eye_w_ffffff', '#ffffff', 0.2)
    im = neon('eye_g_' + glow.lstrip('#'), glow, 2.6) if glow else smooth('eye_i_' + iris.lstrip('#'), iris, 0.15)
    pm = smooth('eye_p_' + pupil.lstrip('#'), pupil, 0.1)
    hm = smooth('eye_shine', '#ffffff', 0.05)
    W = s * w
    t = 0.03
    for sgn, n in LR:
        cx = sgn * x
        sg('eye_' + n, head, (cx, y, z))
        p('eye_frame', (W + 0.05, t, s + 0.05), dark, (cx, y, z))
        p('eye_white', (W, t, s), wm, (cx, y - 0.012, z))
        p('eye_iris', (W * 0.74, t, s * 0.82), im, (cx, y - 0.024, z - s * 0.06))
        p('eye_pupil', (W * 0.42, t, s * 0.52), pm, (cx, y - 0.036, z - s * 0.1))
        p('eye_hi', (s * 0.26, t, s * 0.26), hm, (cx - W * 0.2, y - 0.048, z + s * 0.2))
        p('eye_hi2', (s * 0.13, t, s * 0.13), hm, (cx + W * 0.22, y - 0.048, z - s * 0.24))
        p('eye_lid', (W + 0.09, 0.05, s * (0.08 + sleepy)), dark, (cx, y - 0.04, z + s * (0.5 - sleepy / 2)))
        if lash:
            p('eye_lash', (0.05, 0.04, 0.09), dark, (cx + sgn * (W / 2 + 0.05), y - 0.03, z + s * 0.5 + 0.03), rot=(0, sgn * 30, 0))
            p('eye_lash', (0.05, 0.04, 0.07), dark, (cx + sgn * (W / 2 + 0.07), y - 0.03, z + s * 0.36), rot=(0, sgn * 60, 0))
    use(head)
    if brow:
        bm_ = smooth('brow_' + brow.lstrip('#'), brow, 0.4)
        for sgn, n in LR:
            p('brow', (W * 0.8, 0.04, 0.06), bm_, (sgn * x, y - 0.02, z + s * bdz + 0.14), rot=(0, sgn * tilt, 0))
    K.a.eye = dict(s=s, x=x, y=y, z=z)


def muzzle(hb, size=(0.46, 0.16, 0.3), dz=-0.28, mat='belly', nose=(0.16, 0.07, 0.1), nose_mat='nose', top=None,
           teeth=0, fangs=0, mouth=True, tongue=False, name='muzzle'):
    """muzzle block on the front of the head with nose, mouth line and teeth. returns the muzzle Box"""
    use(hb.seg or 'head')
    c = (0, hb.front - size[1] / 2 + 0.02, hb.c.z + dz * hb.s.z)
    mz = b(name, size, mm(mat), c)
    if top:
        b('muzzle_top', (size[0] * 0.55, size[1] * 0.8, 0.1), mm(top), (0, c[1], c[2] + size[2] / 2 + 0.03), bev=0.02)
    if nose:
        b('nose', nose, mm(nose_mat), (0, mz.front - nose[1] / 2 + 0.02, c[2] + size[2] * 0.36), bev=0.02, ol=0.01)
    if mouth:
        p('mouth', (0.03, 0.03, size[2] * 0.3), mm('line'), (0, mz.front - 0.008, c[2] + size[2] * 0.02))
        for sgn, n in LR:
            p('mouth', (size[0] * 0.24, 0.03, 0.03), mm('line'), (sgn * size[0] * 0.13, mz.front - 0.008, c[2] - size[2] * 0.14))
    for sgn, n in LR:
        if teeth:
            p('tooth', (0.08, 0.04, 0.1), mm('white'), (sgn * 0.045, mz.front - 0.005, c[2] - size[2] * 0.36))
        if fangs:
            p('fang', (0.06, 0.04, 0.09 * fangs), mm('white'), (sgn * size[0] * 0.3, mz.front - 0.005, c[2] - size[2] * 0.3 - 0.03 * fangs))
    if tongue:
        p('tongue', (0.1, 0.04, 0.08), mm('pink'), (0, mz.front - 0.006, c[2] - size[2] * 0.36))
    K.a.bx['muzzle'] = mz
    return mz


def cheeks(hb, mat='belly', size=(0.22, 0.2, 0.3), dz=-0.26, blush=True, whisk=3, wmat='white', tuft=True):
    """fluffy cheeks with tufts, blush and whiskers on both sides of the head"""
    use(hb.seg or 'head')
    z = hb.c.z + dz * hb.s.z
    for sgn, n in LR:
        x = sgn * (hb.s.x / 2 - size[0] * 0.25)
        if size:
            b('cheek', size, mm(mat), (x, hb.front + size[1] * 0.45, z), bev=0.04)
        if tuft:
            p('cheek_tuft', (0.1, 0.1, 0.1), mm(mat), (x + sgn * size[0] * 0.55, hb.front + 0.14, z - 0.06))
            p('cheek_tuft', (0.08, 0.08, 0.08), mm(mat), (x + sgn * size[0] * 0.6, hb.front + 0.16, z + 0.08))
        if blush:
            p('blush', (0.16, 0.03, 0.08), mm('pink'), (sgn * hb.s.x * 0.34, hb.front - 0.012, z + 0.02))
        for j in range(whisk):
            dz2 = (j - (whisk - 1) / 2) * 0.06
            p('whisker', (0.22, 0.02, 0.02), mm(wmat), (sgn * (hb.s.x / 2 + 0.14), hb.front + 0.06, z + dz2),
              rot=(0, -sgn * dz2 * 200, sgn * 12))


def ears(hb, kind='point', mat='main', inner='pink', tip=None, x=0.3, h=0.5, w=0.3, lean=8, y=None):
    """ear segments ear_L / ear_R on top of the head. kinds: point, round, long, flop, tuft"""
    a = K.a
    y = hb.c.y if y is None else y
    for sgn, n in LR:
        cx = sgn * x * hb.s.x
        sg('ear_' + n, 'head', (cx, y, hb.top - 0.04))
        a.ears.append('ear_' + n)
        r = (0, sgn * lean, 0)
        if kind == 'round':
            b('ear', (w, 0.14, h), mm(mat), (cx, y, hb.top + h / 2 - 0.06), rot=r, bev=0.08)
            p('ear_in', (w * 0.55, 0.03, h * 0.55), mm(inner), (cx, y - 0.08, hb.top + h / 2 - 0.08), rot=r)
        elif kind == 'long':
            b('ear_base', (w, 0.16, h * 0.32), mm(mat), (cx, y, hb.top + h * 0.14), rot=r)
            b('ear', (w * 0.86, 0.14, h * 0.6), mm(mat), (cx + sgn * h * 0.05, y, hb.top + h * 0.56), rot=r)
            b('ear_tip', (w * 0.66, 0.13, h * 0.2), mm(tip or mat), (cx + sgn * h * 0.1, y, hb.top + h * 0.92), rot=r, bev=0.04)
            p('ear_in', (w * 0.46, 0.03, h * 0.56), mm(inner), (cx + sgn * h * 0.05, y - 0.08, hb.top + h * 0.52), rot=r)
        elif kind == 'flop':
            b('ear', (w, 0.16, h), mm(mat), (cx + sgn * w * 0.4, y, hb.top - h * 0.42), rot=(0, sgn * 18, 0), bev=0.05)
            p('ear_in', (w * 0.5, 0.03, h * 0.6), mm(inner), (cx + sgn * w * 0.4, y - 0.09, hb.top - h * 0.46), rot=(0, sgn * 18, 0))
        else:  # point / tuft: stepped triangle
            b('ear_base', (w, 0.16, h * 0.46), mm(mat), (cx, y, hb.top + h * 0.2), rot=r)
            b('ear_mid', (w * 0.74, 0.15, h * 0.34), mm(mat), (cx + sgn * 0.02, y, hb.top + h * 0.56), rot=r)
            b('ear_tip', (w * 0.46, 0.14, h * 0.26), mm(tip or mat), (cx + sgn * 0.04, y, hb.top + h * 0.84), rot=r, bev=0.03)
            p('ear_in', (w * 0.56, 0.03, h * 0.36), mm(inner), (cx, y - 0.085, hb.top + h * 0.2), rot=r)
            p('ear_in', (w * 0.34, 0.03, h * 0.24), mm(inner), (cx + sgn * 0.02, y - 0.08, hb.top + h * 0.52), rot=r)
            if kind == 'tuft':
                p('ear_tuft', (0.06, 0.06, h * 0.3), mm(tip or 'dark'), (cx + sgn * 0.05, y, hb.top + h * 1.08), rot=r)
    use('head')


# ---------------------------------------------------------------- limbs
def leg(name, parent, x, y, top, lw, mat='main', foot='belly', toe='dark', hoof=None, ntoe=3, sock=None, fl=None, arm=False):
    """straight leg segment standing on the ground: joint at (x, y, top). returns foot Box"""
    a = K.a
    sg(name, parent, (x, y, top))
    hgt = top
    b('leg', (lw, lw * 1.06, hgt * 0.72), mm(mat), (x, y, hgt * 0.62))
    if sock:
        b('sock', (lw + 0.02, lw * 1.1, hgt * 0.3), mm(sock), (x, y, hgt * 0.3))
    fl = fl or lw * 1.35
    if hoof:
        ft = b('hoof', (lw + 0.05, lw * 1.2, min(0.16, hgt * 0.3)), mm(hoof), (x, y - 0.02, min(0.08, hgt * 0.15)), bev=0.03)
        p('hoof_split', (0.03, 0.04, min(0.16, hgt * 0.3)), mm('line'), (x, y - 0.02 - lw * 0.6, min(0.08, hgt * 0.15)))
    else:
        ft = b('paw', (lw + 0.05, fl, 0.12), mm(foot), (x, y - (fl - lw) / 2, 0.06), bev=0.03)
        toes(ft, ntoe, mm(toe))
    (a.arms if arm else a.legs).append(name)
    return ft


def tail_kit(kind, parent, j, mat='main', tip='belly', n=2, size=0.3, dark='dark'):
    """tail segments. kinds: pom, bushy, long, thick, tuft, stub. j = joint (x, y, z) nominal"""
    a = K.a
    x, y, z = j
    sg('tail', parent, j)
    a.tail = ['tail']
    if kind == 'pom':
        b('tail', (size * 1.2, size, size * 1.2), mm(tip), (x, y + size * 0.4, z + size * 0.2))
        b('tail_b', (size * 0.8, size * 0.5, size * 0.8), mm(tip), (x, y + size * 1.0, z + size * 0.3), bev=0.03)
        tufts([(x + size * 0.35, y + size * 0.8, z + size * 0.75), (x - size * 0.45, y + size * 0.7, z - size * 0.15)], size * 0.36, mm(tip))
    elif kind == 'bushy':
        b('tail_a', (size * 1.3, size * 1.5, size * 1.3), mm(mat), (x, y + size * 0.6, z + size * 0.25))
        b('tail_b', (size * 2.0, size * 2.0, size * 2.0), mm(mat), (x, y + size * 2.1, z + size * 1.0))
        b('tail_c', (size * 1.6, size * 1.3, size * 1.6), mm(tip), (x, y + size * 3.5, z + size * 1.6))
        b('tail_d', (size * 0.9, size * 0.5, size * 0.9), mm(tip), (x, y + size * 4.3, z + size * 1.9), bev=0.04)
        p('tail_ring', (size * 1.85, 0.06, size * 1.85), mm(dark), (x, y + size * 3.0, z + size * 1.38))
        tufts([(x + size, y + size * 2.0, z + size * 2.0), (x - size * 1.05, y + size * 1.7, z + size * 0.3), (x + size * 0.8, y + size * 3.6, z + size * 2.4),
               (x - size * 0.8, y + size * 3.8, z + size * 1.0)], size * 0.45, mm(mat))
    elif kind == 'long':
        segs = max(2, n)
        cur = Vector(j)
        par = 'tail'
        for i in range(segs):
            ln = size * 2.2
            w = size * (1.0 - 0.5 * i / segs)
            if i:
                nm = 'tail%d' % (i + 1)
                sg(nm, par, tuple(cur))
                a.tail.append(nm)
                par = nm
            b('tail', (w, ln, w), mm(mat), (cur.x, cur.y + ln / 2 - 0.03, cur.z + i * size * 0.25), rot=(-12 * (i + 1) / segs * 0, 0, 0))
            if i % 2 == 1:
                p('tail_band', (w + 0.02, ln * 0.3, w + 0.02), mm(dark), (cur.x, cur.y + ln * 0.5, cur.z + i * size * 0.25))
            cur = Vector((cur.x, cur.y + ln - 0.06, cur.z + size * 0.25))
        b('tail_tip', (size * 0.9, size * 0.9, size * 0.9), mm(tip), (cur.x, cur.y + size * 0.3, cur.z), bev=0.05)
    elif kind == 'thick':
        b('tail_a', (size * 2.0, size * 2.2, size * 1.6), mm(mat), (x, y + size * 0.9, z))
        b('tail_b', (size * 1.4, size * 2.0, size * 1.1), mm(mat), (x, y + size * 2.7, z - size * 0.15))
        b('tail_c', (size * 0.8, size * 1.4, size * 0.7), mm(tip), (x, y + size * 4.2, z - size * 0.3), bev=0.04)
    elif kind == 'tuft':
        b('tail', (size * 0.5, size * 2.4, size * 0.5), mm(mat), (x, y + size * 1.1, z - size * 0.3), rot=(25, 0, 0), bev=0.03)
        b('tail_tuft', (size * 1.1, size * 1.1, size * 1.1), mm(tip), (x, y + size * 2.3, z - size * 0.9))
        tufts([(x + size * 0.4, y + size * 2.7, z - size * 1.3), (x - size * 0.4, y + size * 2.6, z - size * 0.5)], size * 0.4, mm(tip))
    else:  # stub
        b('tail', (size * 0.8, size * 0.8, size * 0.7), mm(mat), (x, y + size * 0.3, z), bev=0.03)
        p('tail_tip', (size * 0.45, size * 0.4, size * 0.45), mm(tip), (x, y + size * 0.8, z + size * 0.1))
    use(parent)


# ---------------------------------------------------------------- archetype: quadruped
def quad(bw=0.9, bl=1.3, bh=0.72, legh=0.5, lw=0.26, hw=1.12, hd=0.9, hh=0.92, neck=0.0, head_fwd=0.22, head_up=0.62,
         belly=True, chest=True, hoof=None, sock=None, ntoe=3, leg_mat='main', foot='belly', toe='dark', hump=0.0, rump=True,
         leg_fl=None, leg_back_x=None, head_mat='main'):
    """four legs, big cube head. segments: body, head, leg_fL leg_fR leg_bL leg_bR. returns (body Box, head Box)"""
    a = K.a
    zb = legh + bh / 2
    by = 0.2
    sg('body', 'root', (0, by, zb))
    B = b('body', (bw, bl, bh), mm('main'), (0, by, zb))
    if rump:
        a.bx['rump'] = b('rump', (bw * 1.06, bl * 0.36, bh * 0.86), mm('main'), (0, by + bl * 0.36, zb - bh * 0.05))
    if hump:
        b('hump', (bw * 0.86, bl * 0.42, hump), mm('main'), (0, by - bl * 0.18, zb + bh / 2 + hump / 2 - 0.04))
        a.bx['hump'] = Box((0, by - bl * 0.18, zb + bh / 2 + hump / 2 - 0.04), (bw * 0.86, bl * 0.42, hump))
    if belly:
        b('belly', (bw * 0.68, bl * 0.8, 0.08), mm('belly'), (0, by, zb - bh / 2 - 0.02), bev=0.02)
    if chest:
        a.bx['chest'] = b('chest', (bw * 0.72, 0.14, bh * 0.82), mm('belly'), (0, by - bl / 2 - 0.03, zb - bh * 0.04))
    hj = (0, by - bl / 2 + 0.25, legh + bh * 0.9 + neck * 0.5)
    sg('head', 'body', hj)
    hc = (0, by - bl / 2 - hd * head_fwd, legh + bh * head_up + neck + hh / 2)
    if neck > 0.05:
        b('neck', (bw * 0.6, bw * 0.6, neck + bh * 0.3), mm('main'), (0, by - bl / 2 + 0.2, legh + bh * 0.85 + neck / 2))
    Hd = b('head', (hw, hd, hh), mm(head_mat), hc)
    b('head_top', (hw * 0.74, hd * 0.7, 0.08), mm(head_mat), (0, hc[1], hc[2] + hh / 2 + 0.02), bev=0.03)
    lx = bw / 2 - lw / 2 + 0.02
    fy, ky = by - bl / 2 + lw / 2 + 0.14, by + bl / 2 - lw / 2 - 0.04
    feet = []
    for sgn, n in LR:
        feet.append(leg('leg_f' + n, 'body', sgn * lx, fy, legh + 0.1, lw, leg_mat, foot, toe, hoof, ntoe, sock, leg_fl))
    for sgn, n in LR:
        feet.append(leg('leg_b' + n, 'body', sgn * (leg_back_x or lx), ky, legh + 0.1, lw, leg_mat, foot, toe, hoof, ntoe, sock, leg_fl))
    use('body')
    a.bx.update(body=B, head=Hd, feet=feet)
    a.tail_j = (0, by + bl / 2 + (bl * 0.08 if rump else 0), zb + bh * 0.2)
    a.marks = dict(Head=hc, Chest=(0, by - bl / 2 - 0.1, zb), Hit=(0, by, zb + bh / 2 + hump))
    return B, Hd


# ---------------------------------------------------------------- archetype: upright sitter (rabbit, meerkat, frog ...)
def sit(bw=0.86, bd=0.95, bh=0.72, hw=1.08, hd=0.9, hh=0.9, arm=0.28, lw=0.22, foot_l=0.66, belly=True, ntoe=3, thigh=True,
        foot='belly', toe='dark'):
    """sits upright on big back feet, small front paws. segments: body, head, leg_fL/R (arms), leg_bL/R (feet)"""
    a = K.a
    zb = 0.2 + bh / 2
    sg('body', 'root', (0, 0.1, zb - 0.05))
    B = b('body', (bw, bd, bh), mm('main'), (0, 0.12, zb))
    b('rump', (bw * 1.08, bd * 0.52, bh * 0.86), mm('main'), (0, 0.12 + bd * 0.4, zb - bh * 0.07))
    if belly:
        b('belly', (bw * 0.72, 0.1, bh * 0.72), mm('belly'), (0, 0.12 - bd / 2 - 0.02, zb - bh * 0.1))
    sg('head', 'body', (0, -0.2, 0.2 + bh * 0.97))
    hc = (0, -0.25, 0.2 + bh * 0.93 + hh / 2)
    Hd = b('head', (hw, hd, hh), mm('main'), hc)
    b('head_top', (hw * 0.74, hd * 0.72, 0.1), mm('main'), (0, hc[1], hc[2] + hh / 2 + 0.03), bev=0.03)
    feet = []
    for sgn, n in LR:
        x = sgn * (bw / 2 - lw / 2 - 0.08)
        sg('leg_f' + n, 'body', (x, 0.12 - bd / 2 + 0.07, 0.2 + bh * 0.42))
        b('arm', (lw, lw, arm), mm('main'), (x, 0.12 - bd / 2 + 0.04, 0.2 + bh * 0.42 - arm / 2 + 0.04))
        ft = b('paw', (lw + 0.04, lw + 0.08, 0.12), mm(foot), (x, 0.12 - bd / 2 - 0.02, 0.2 + bh * 0.42 - arm + 0.02), bev=0.03)
        toes(ft, ntoe, mm(toe))
        a.arms.append('leg_f' + n)
        a.legs.append('leg_f' + n)
    for sgn, n in LR:
        x = sgn * (bw / 2 + 0.06)
        sg('leg_b' + n, 'body', (sgn * (bw / 2 - 0.04), 0.42, 0.38))
        if thigh:
            b('thigh', (0.24, bd * 0.52, 0.42), mm('main'), (x, 0.42, 0.3))
        ft = b('foot', (0.26, foot_l, 0.13), mm(foot), (x, 0.42 - foot_l * 0.4, 0.065), bev=0.03)
        toes(ft, ntoe, mm(toe))
        p('pad', (0.14, 0.03, 0.07), mm('pink'), (x, ft.front - 0.012, 0.07))
        feet.append(ft)
        a.legs.append('leg_b' + n)
    use('body')
    a.bx.update(body=B, head=Hd, feet=feet)
    a.tail_j = (0, 0.12 + bd * 0.66, zb - bh * 0.05)
    a.marks = dict(Head=hc, Chest=(0, 0.12 - bd / 2 - 0.05, zb), Hit=(0, 0.15, zb + bh * 0.35))
    return B, Hd


# ---------------------------------------------------------------- archetype: biped (yeti, gorilla, golem, titan)
def biped(tw=1.3, td=0.9, th=1.0, legh=0.5, lw=0.4, hw=1.2, hd=0.95, hh=0.95, arm_l=1.0, arm_w=0.36, hand=0.44, ntoe=3,
          belly=True, shoulder=0.0, foot='belly', toe='dark', hand_mat='belly'):
    """stands on two legs with big arms. segments: body, head, arm_L/R, leg_L/R"""
    a = K.a
    zt = legh + th / 2
    sg('body', 'root', (0, 0.05, legh + 0.1))
    B = b('body', (tw, td, th), mm('main'), (0, 0.05, zt))
    b('hips', (tw * 0.86, td * 0.92, th * 0.3), mm('main'), (0, 0.07, legh + th * 0.1))
    if belly:
        b('belly', (tw * 0.66, 0.1, th * 0.7), mm('belly'), (0, 0.05 - td / 2 - 0.02, zt - th * 0.06))
    sg('head', 'body', (0, -0.05, legh + th * 0.95))
    hc = (0, -0.16, legh + th * 0.9 + hh / 2)
    Hd = b('head', (hw, hd, hh), mm('main'), hc)
    b('head_top', (hw * 0.74, hd * 0.72, 0.1), mm('main'), (0, hc[1], hc[2] + hh / 2 + 0.03), bev=0.03)
    hands, feet = [], []
    for sgn, n in LR:
        x = sgn * (tw / 2 + arm_w / 2 - 0.04)
        zs = legh + th * 0.86
        sg('arm_' + n, 'body', (x, 0.05, zs))
        if shoulder:
            b('shoulder', (arm_w * 1.3, td * 0.7, shoulder), mm('main'), (x, 0.05, zs + shoulder * 0.2))
        b('arm', (arm_w, arm_w * 1.05, arm_l * 0.7), mm('main'), (x, 0.05, zs - arm_l * 0.35))
        hb_ = b('hand', (hand, hand, hand * 0.9), mm(hand_mat), (x, 0.0, zs - arm_l * 0.78), bev=0.05)
        for j in range(3):
            p('finger', (hand * 0.22, 0.06, hand * 0.3), mm(toe), (x + (j - 1) * hand * 0.3, -hand / 2 - 0.02, zs - arm_l * 0.78 - hand * 0.2))
        hands.append(hb_)
        a.arms.append('arm_' + n)
    for sgn, n in LR:
        x = sgn * tw * 0.26
        sg('leg_' + n, 'body', (x, 0.07, legh + 0.08))
        b('leg', (lw, lw * 1.05, legh * 0.8), mm('main'), (x, 0.07, legh * 0.6))
        ft = b('foot', (lw + 0.08, lw * 1.7, 0.16), mm(foot), (x, 0.07 - lw * 0.3, 0.08), bev=0.04)
        toes(ft, ntoe, mm(toe), size=(0.09, 0.07, 0.1))
        feet.append(ft)
        a.legs.append('leg_' + n)
    use('body')
    a.bx.update(body=B, head=Hd, feet=feet, hands=hands)
    a.tail_j = (0, 0.05 + td / 2, legh + th * 0.2)
    a.marks = dict(Head=hc, Chest=(0, 0.05 - td / 2 - 0.05, zt), Hit=(0, 0.05, zt + th * 0.3))
    return B, Hd


# ---------------------------------------------------------------- archetype: bird
def bird(bw=1.2, bl=1.3, bh=1.05, legh=0.55, lw=0.16, hw=1.1, hd=0.95, hh=0.95, neck=0.3, beak=(0.46, 0.5, 0.3), beak_low=True,
         wing=(0.16, 0.85, 0.6), fly=False, leg_mat='leg', beak_mat='beak', beak_tip='beak_tip', wing_span=0.0, ntail=3, tail_l=0.45,
         tail_mat='belly', head_mat='main'):
    """bird: body, head, wing_L/R, leg_L/R, tail. fly=True: wings spread wide (wing_span), legs tucked short"""
    a = K.a
    zb = legh + bh / 2
    sg('body', 'root', (0, 0.1, zb))
    B = b('body', (bw, bl, bh), mm('main'), (0, 0.15, zb))
    b('rump', (bw * 0.8, bl * 0.3, bh * 0.7), mm('main'), (0, 0.15 + bl * 0.55, zb + bh * 0.08))
    b('belly', (bw * 0.76, 0.12, bh * 0.76), mm('belly'), (0, 0.15 - bl / 2 - 0.02, zb - bh * 0.06))
    b('belly_low', (bw * 0.8, bl * 0.76, 0.1), mm('belly'), (0, 0.1, zb - bh / 2 - 0.02), bev=0.03)
    hj = (0, 0.15 - bl * 0.3, legh + bh * 0.92)
    sg('head', 'body', hj)
    hc = (0, 0.15 - bl * 0.42, legh + bh * 0.9 + neck + hh / 2)
    if neck > 0.05:
        b('neck', (hw * 0.55, hd * 0.55, neck + 0.2), mm('main'), (0, 0.15 - bl * 0.34, legh + bh * 0.9 + neck / 2))
        p('ruff', (hw * 0.68, hd * 0.68, 0.07), mm('belly'), (0, 0.15 - bl * 0.34, legh + bh * 0.98))
    Hd = b('head', (hw, hd, hh), mm(head_mat), hc)
    bz = hc[2] - hh * 0.18
    bk = b('beak', beak, mm(beak_mat), (0, Hd.front - beak[1] / 2 + 0.04, bz))
    if beak_low:
        b('beak_low', (beak[0] * 0.8, beak[1] * 0.72, beak[2] * 0.36), mm(beak_tip), (0, Hd.front - beak[1] * 0.36 + 0.04, bz - beak[2] * 0.6), bev=0.03)
    for sgn, n in LR:
        p('nostril', (0.05, 0.08, 0.04), mm('line'), (sgn * beak[0] * 0.2, bk.front + beak[1] * 0.3, bz + beak[2] / 2 + 0.005))
    wings = []
    for sgn, n in LR:
        x = sgn * (bw / 2 + wing[0] / 2 - 0.03)
        sg('wing_' + n, 'body', (sgn * bw / 2, 0.05, zb + bh * 0.28))
        a.wings.append('wing_' + n)
        if fly and wing_span:
            # spread wing: 3 stepped slabs going outward, feathers along the trailing edge
            for i in range(3):
                ln = wing_span / 3
                cx = sgn * (bw / 2 + ln * (i + 0.5))
                dep = wing[1] * (1.0 - 0.22 * i)
                wb = b('wing', (ln + 0.02, dep, wing[0] * (1.2 - 0.25 * i)), mm('main'), (cx, 0.12 + i * 0.06, zb + bh * 0.28))
                p('wing_cover', (ln * 0.8, dep * 0.6, 0.03), mm('dark'), (cx, 0.05 + i * 0.06, zb + bh * 0.28 + wing[0] * (0.6 - 0.12 * i) + 0.01))
                for j in range(2):
                    b('feather', (ln * 0.42, dep * 0.34, wing[0] * 0.7), mm('belly' if (i + j) % 2 else 'dark'),
                      (cx + (j - 0.5) * ln * 0.5, 0.12 + i * 0.06 + dep * 0.6, zb + bh * 0.26), bev=0.03)
            wings.append(Box((sgn * (bw / 2 + wing_span / 2), 0.15, zb + bh * 0.28), (wing_span, wing[1], wing[0])))
        else:
            wb = b('wing', wing, mm('main'), (x, 0.2, zb + bh * 0.02))
            p('wing_layer', (0.04, wing[1] * 0.72, wing[2] * 0.6), mm('dark'), (x + sgn * (wing[0] / 2 + 0.01), 0.22, zb + bh * 0.06))
            p('wing_layer', (0.04, wing[1] * 0.42, wing[2] * 0.34), mm('belly'), (x + sgn * (wing[0] / 2 + 0.03), 0.2, zb + bh * 0.1))
            for j in range(3):
                b('wing_tip', (wing[0] * 0.9, wing[1] * 0.24, wing[2] * 0.3), mm('dark'), (x, 0.2 + wing[1] * 0.56, zb + bh * 0.2 - j * wing[2] * 0.32), bev=0.03)
            wings.append(wb)
    feet = []
    for sgn, n in LR:
        x = sgn * bw * 0.24
        sg('leg_' + n, 'body', (x, 0.15, legh + 0.04))
        a.legs.append('leg_' + n)
        p('pants', (lw + 0.12, lw + 0.12, 0.1), mm('main'), (x, 0.15, legh))
        b('leg', (lw, lw, legh * 0.86), mm(leg_mat), (x, 0.15, legh * 0.55), bev=0.03)
        p('knee', (lw + 0.05, lw + 0.05, 0.07), mm(beak_tip), (x, 0.15, legh * 0.62))
        ft = b('foot', (lw * 1.8, lw * 1.8, 0.1), mm(leg_mat), (x, 0.06, 0.05), bev=0.03)
        for j, dx in enumerate((-0.13, 0.0, 0.13)):
            b('toe', (0.09, 0.3, 0.08), mm(leg_mat), (x + dx * 1.2, -0.18, 0.04), rot=(0, 0, dx * 120), bev=0.02)
            p('claw', (0.05, 0.07, 0.05), mm('white'), (x + dx * 1.6, -0.35, 0.04))
        feet.append(ft)
    sg('tail', 'body', (0, 0.15 + bl * 0.62, zb + bh * 0.22))
    a.tail = ['tail']
    for i in range(ntail):
        ang = (i - (ntail - 1) / 2) * (70.0 / max(ntail - 1, 1))
        sx, cz = math.sin(math.radians(ang)), math.cos(math.radians(ang))
        b('tail_feather', (0.16, tail_l, 0.16), mm(tail_mat), (sx * 0.34, 0.15 + bl * 0.62 + tail_l * 0.4, zb + bh * 0.22 + cz * 0.2), rot=(-35, ang, 0), bev=0.04)
    use('body')
    a.bx.update(body=B, head=Hd, beak=bk, feet=feet, wings=wings)
    a.marks = dict(Head=hc, Chest=(0, 0.15 - bl / 2 - 0.05, zb), Hit=(0, 0.15, zb + bh * 0.35))
    return B, Hd


# ---------------------------------------------------------------- archetype: bug / crab (shell body, many legs)
def bug(bw=1.3, bl=1.4, bh=0.7, legh=0.35, hw=0.9, hd=0.5, hh=0.62, nleg=3, leg_w=0.12, leg_span=0.5, shell='main', under='belly',
        claws=0.0, antenna=0.4, head_z=0.0, leg_mat='dark'):
    """low shelled body, nleg pairs of jointed legs. segments: body, head, leg_1L.. , claw_L/R, antenna_L/R"""
    a = K.a
    zb = legh + bh / 2
    sg('body', 'root', (0, 0.15, zb))
    B = b('body', (bw, bl, bh), mm(shell), (0, 0.2, zb))
    b('under', (bw * 0.8, bl * 0.86, 0.12), mm(under), (0, 0.2, legh - 0.02), bev=0.03)
    b('shell_top', (bw * 0.74, bl * 0.74, 0.14), mm(shell), (0, 0.24, zb + bh / 2 + 0.05))
    sg('head', 'body', (0, 0.2 - bl / 2 + 0.1, zb + head_z))
    hc = (0, 0.2 - bl / 2 - hd * 0.3, zb + head_z + 0.02)
    Hd = b('head', (hw, hd, hh), mm(under), hc)
    for sgn, n in LR:
        if antenna:
            sg('antenna_' + n, 'head', (sgn * hw * 0.3, hc[1] - 0.05, hc[2] + hh / 2))
            b('antenna', (0.05, 0.05, antenna), mm(leg_mat), (sgn * hw * 0.34, hc[1] - 0.08, hc[2] + hh / 2 + antenna / 2), rot=(-15, sgn * 14, 0), bev=0.01)
            p('antenna_tip', (0.1, 0.1, 0.1), mm('accent'), (sgn * (hw * 0.34 + antenna * 0.24), hc[1] - 0.2, hc[2] + hh / 2 + antenna), rot=(0, 45, 0))
            a.ears.append('antenna_' + n)
    for i in range(nleg):
        y = 0.2 + ((i + 0.5) / nleg - 0.5) * bl * 0.8
        for sgn, n in LR:
            nm = 'leg_%d%s' % (i + 1, n)
            sg(nm, 'body', (sgn * bw * 0.46, y, legh + 0.12))
            a.legs.append(nm)
            x1 = sgn * (bw * 0.46 + leg_span * 0.5)
            b('leg_up', (leg_span, leg_w, leg_w), mm(leg_mat), (x1, y, legh + 0.16), rot=(0, -sgn * 18, 0), bev=0.02)
            b('leg_low', (leg_w, leg_w, legh + 0.14), mm(leg_mat), (sgn * (bw * 0.46 + leg_span * 0.95), y, (legh + 0.14) / 2), bev=0.02)
            p('leg_tip', (leg_w * 1.3, leg_w * 1.5, 0.05), mm('accent'), (sgn * (bw * 0.46 + leg_span * 0.95), y - 0.02, 0.025))
            p('leg_joint', (leg_w * 1.4, leg_w * 1.4, leg_w * 1.4), mm(under), (sgn * (bw * 0.46 + leg_span * 0.95), y, legh + 0.16))
    if claws:
        for sgn, n in LR:
            sg('claw_' + n, 'body', (sgn * bw * 0.4, 0.2 - bl / 2 + 0.05, zb - 0.05))
            a.arms.append('claw_' + n)
            x = sgn * (bw * 0.4 + claws * 0.5)
            b('claw_arm', (claws * 0.9, 0.16, 0.16), mm(leg_mat), (x, 0.2 - bl / 2 - 0.06, zb - 0.05), rot=(0, 0, -sgn * 30), bev=0.03)
            b('claw', (claws * 0.7, claws * 0.9, claws * 0.5), mm(shell), (sgn * (bw * 0.4 + claws * 0.95), 0.2 - bl / 2 - claws * 0.55, zb - 0.02))
            b('claw_top', (claws * 0.26, claws * 0.6, claws * 0.22), mm(shell), (sgn * (bw * 0.4 + claws * 1.15), 0.2 - bl / 2 - claws * 1.2, zb + claws * 0.14), bev=0.03)
            b('claw_low', (claws * 0.26, claws * 0.5, claws * 0.18), mm(under), (sgn * (bw * 0.4 + claws * 0.78), 0.2 - bl / 2 - claws * 1.15, zb - claws * 0.14), bev=0.03)
    use('body')
    a.bx.update(body=B, head=Hd)
    a.tail_j = (0, 0.2 + bl / 2, zb)
    a.marks = dict(Head=hc, Chest=(0, 0.2 - bl / 2, zb), Hit=(0, 0.2, zb + bh / 2))
    return B, Hd


# ---------------------------------------------------------------- archetype: serpent / wyrm (nested chain rising in an S)
def serp(w=0.8, n=4, seg_l=0.9, hw=1.15, hd=1.0, hh=0.95, rise=0.55, coil=True, belly='belly', taper=0.12, ntail=3):
    """snake-like: body (coiled base on the ground) -> neck1..n -> head ; tail chain behind. returns (base Box, head Box, [neck boxes])"""
    a = K.a
    sg('body', 'root', (0, 0.3, w * 0.5))
    B = b('body', (w * 1.5, w * 1.7, w), mm('main'), (0, 0.4, w * 0.5))
    b('body_belly', (w * 1.1, w * 1.3, 0.08), mm(belly), (0, 0.4, 0.03), bev=0.02)
    if coil:
        b('coil', (w * 1.9, w * 0.9, w * 0.8), mm('main'), (0, 0.4 + w * 1.1, w * 0.4))
        b('coil_side', (w * 0.8, w * 1.4, w * 0.7), mm('main'), (w * 0.95, 0.4 + w * 0.3, w * 0.35))
    cur = Vector((0, 0.1, w * 0.9))
    par = 'body'
    necks = []
    a.neck = []
    for i in range(n):
        nm = 'neck%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.neck.append(nm)
        ww = w * (1.0 - taper * i)
        fwd = -0.16 if i < n - 1 else -0.3
        c = (0, cur.y + fwd * seg_l * 0.5, cur.z + seg_l * rise * 0.5 + 0.05)
        nb = b('neck', (ww, ww, seg_l * 0.95), mm('main'), c, rot=(12, 0, 0))
        p('neck_belly', (ww * 0.66, 0.04, seg_l * 0.7), mm(belly), (0, c[1] - ww / 2 - 0.01, c[2] - 0.02), rot=(12, 0, 0))
        necks.append(nb)
        cur = Vector((0, cur.y + fwd * seg_l, cur.z + seg_l * rise + 0.08))
        par = nm
    sg('head', par, tuple(cur))
    hc = (0, cur.y - hd * 0.2, cur.z + hh * 0.36)
    Hd = b('head', (hw, hd, hh), mm('main'), hc)
    b('head_top', (hw * 0.74, hd * 0.7, 0.08), mm('main'), (0, hc[1], hc[2] + hh / 2 + 0.02), bev=0.03)
    cur = Vector((0, 0.4 + w * (1.5 if coil else 0.8), w * 0.4))
    par = 'body'
    a.tail = []
    for i in range(ntail):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        ww = w * (0.8 - 0.2 * i)
        b('tail', (ww, seg_l, ww * 0.9), mm('main'), (cur.x, cur.y + seg_l / 2 - 0.04, ww * 0.45))
        p('tail_belly', (ww * 0.6, seg_l * 0.8, 0.04), mm(belly), (cur.x, cur.y + seg_l / 2, 0.02))
        cur = Vector((cur.x, cur.y + seg_l - 0.08, ww * 0.4))
        par = nm
    use('body')
    a.bx.update(body=B, head=Hd, necks=necks)
    a.tail_end = tuple(cur)
    a.marks = dict(Head=hc, Chest=(0, necks[0].c.y - w / 2, necks[0].c.z), Hit=(0, 0.4, w))
    return B, Hd, necks


# ---------------------------------------------------------------- archetype: fish / swimmer (origin at body centre)
def fish(bw=1.0, bl=1.5, bh=1.1, face_h=0.9, fin=(0.5, 0.5, 0.12), tail=(0.14, 0.5, 0.9), dorsal=0.35, belly=True, ntail=1, zc=None):
    """chubby fish facing -Y, eyes on the front face. segments: body, head(=face block), wing_L/R (side fins), tail"""
    a = K.a
    zc = K.Z0 if zc is None else zc
    sg('body', 'root', (0, 0.1, zc))
    B = b('body', (bw, bl, bh), mm('main'), (0, 0.2, zc))
    b('body_back', (bw * 0.76, bl * 0.4, bh * 0.76), mm('main'), (0, 0.2 + bl * 0.58, zc))
    if belly:
        b('belly', (bw * 0.7, bl * 0.8, 0.08), mm('belly'), (0, 0.2, zc - bh / 2 - 0.02), bev=0.03)
    sg('head', 'body', (0, 0.2 - bl / 2 + 0.2, zc))
    hc = (0, 0.2 - bl / 2 - 0.1, zc + (bh - face_h) * 0.1)
    Hd = b('head', (bw * 1.06, 0.6, face_h), mm('main'), hc)
    if dorsal:
        for i in range(3):
            b('dorsal', (0.12, bl * 0.2, dorsal * (1.0 - 0.25 * i)), mm('accent'), (0, 0.05 + i * bl * 0.2, zc + bh / 2 + dorsal * (0.5 - 0.125 * i) - 0.03), bev=0.03)
    for sgn, n in LR:
        sg('wing_' + n, 'body', (sgn * bw / 2, 0.05, zc - bh * 0.15))
        a.wings.append('wing_' + n)
        b('fin', fin, mm('accent'), (sgn * (bw / 2 + fin[0] / 2 - 0.04), 0.12, zc - bh * 0.18), rot=(0, sgn * 20, 0), bev=0.03)
        p('fin_ray', (fin[0] * 0.7, 0.05, fin[2] + 0.02), mm('dark'), (sgn * (bw / 2 + fin[0] / 2), 0.12, zc - bh * 0.2), rot=(0, sgn * 20, 0))
        p('fin_tip', (fin[0] * 0.3, fin[1] * 0.6, fin[2]), mm('belly'), (sgn * (bw / 2 + fin[0] * 0.95), 0.2, zc - bh * 0.3), rot=(0, sgn * 20, 0))
    cur = Vector((0, 0.2 + bl * 0.76, zc))
    par = 'body'
    a.tail = []
    for i in range(ntail):
        nm = 'tail' if i == 0 else 'tail%d' % (i + 1)
        sg(nm, par, tuple(cur))
        a.tail.append(nm)
        if i < ntail - 1:
            b('tail_stem', (bw * 0.5, 0.5, bh * 0.5), mm('main'), (0, cur.y + 0.22, zc))
            cur = Vector((0, cur.y + 0.44, zc))
            par = nm
    b('tail_stem', (bw * 0.36, 0.3, bh * 0.36), mm('main'), (0, cur.y + 0.1, zc))
    b('tail_fin_up', (tail[0], tail[1], tail[2] * 0.5), mm('accent'), (0, cur.y + 0.2 + tail[1] / 2, zc + tail[2] * 0.26), rot=(-20, 0, 0), bev=0.03)
    b('tail_fin_low', (tail[0], tail[1], tail[2] * 0.5), mm('accent'), (0, cur.y + 0.2 + tail[1] / 2, zc - tail[2] * 0.26), rot=(20, 0, 0), bev=0.03)
    use('body')
    a.bx.update(body=B, head=Hd)
    a.marks = dict(Head=hc, Chest=(0, hc[1] - 0.3, zc - bh * 0.2), Hit=(0, 0.2, zc + bh / 2))
    return B, Hd


# ---------------------------------------------------------------- archetype: blob (anemone, urchin, clam, starfish)
def blob(w=1.4, d=1.3, h=1.1, base=True):
    """round-ish creature whose body is the head: segments body, head (face plate)"""
    a = K.a
    sg('body', 'root', (0, 0.1, h * 0.4))
    B = b('body', (w, d, h), mm('main'), (0, 0.1, h / 2 + 0.06), bev=0.1)
    if base:
        b('base', (w * 1.12, d * 1.1, 0.16), mm('dark'), (0, 0.1, 0.08), bev=0.05)
    b('top', (w * 0.74, d * 0.74, 0.14), mm('main'), (0, 0.1, h + 0.1), bev=0.05)
    sg('head', 'body', (0, 0.1 - d / 2 + 0.1, h * 0.55))
    hc = (0, 0.1 - d / 2 + 0.02, h * 0.58)
    Hd = b('head', (w * 0.86, 0.12, h * 0.7), mm('belly'), hc, bev=0.04)
    use('body')
    a.bx.update(body=B, head=Hd)
    a.tail_j = (0, 0.1 + d / 2, h * 0.3)
    a.marks = dict(Head=hc, Chest=(0, hc[1] - 0.1, h * 0.4), Hit=(0, 0.1, h + 0.1))
    return B, Hd


# ---------------------------------------------------------------- shared add-ons
def wings_big(parent, j, span=2.0, depth=1.0, th=0.12, mat='accent', bone='dark', web='belly', n=3, up=18):
    """bat / dragon wings as segments wing_L / wing_R at joint j (mirrored)"""
    a = K.a
    for sgn, nn in LR:
        sg('wing_' + nn, parent, (sgn * j[0], j[1], j[2]))
        a.wings.append('wing_' + nn)
        for i in range(n):
            ln = span / n
            cx = sgn * (j[0] + ln * (i + 0.5))
            dep = depth * (1.0 - 0.2 * i)
            z = j[2] + math.tan(math.radians(up)) * ln * (i + 0.5)
            b('wing_bone', (ln + 0.04, th * 1.3, th * 1.3), mm(bone), (cx, j[1] - dep * 0.1, z + th * 0.2), rot=(0, -sgn * up, 0), bev=0.03)
            b('wing_web', (ln, dep, th * 0.6), mm(mat), (cx, j[1] + dep * 0.42, z), rot=(0, -sgn * up, 0), bev=0.03)
            p('wing_web_in', (ln * 0.7, dep * 0.6, th * 0.62), mm(web), (cx, j[1] + dep * 0.46, z + 0.005), rot=(0, -sgn * up, 0))
            b('wing_claw', (th, th, th * 2.2), mm('white'), (sgn * (j[0] + ln * (i + 1)), j[1] + dep * 0.92, z - th), rot=(0, -sgn * up, 0), bev=0.02)
    use(parent)


def horns(hb, kind='cone', mat='horn', x=0.3, h=0.5, r=0.11, d=(0.3, 0, 1), n=1, seg_parent='head'):
    """horns on top of the head (part of the head segment). kinds: cone, antler, curl, stub"""
    use(seg_parent)
    for sgn, nn in LR:
        bx = sgn * x * hb.s.x
        if kind == 'cone':
            cn('horn', r, h, mm(mat), (bx, hb.c.y, hb.top - 0.03), (sgn * d[0], d[1], d[2]))
        elif kind == 'stub':
            b('horn', (r * 2, r * 2, h), mm(mat), (bx, hb.c.y, hb.top + h / 2 - 0.04), bev=0.04)
        elif kind == 'curl':
            b('horn_a', (r * 2.4, r * 2.4, h * 0.5), mm(mat), (bx, hb.c.y, hb.top + h * 0.2), bev=0.04)
            b('horn_b', (h * 0.7, r * 2.2, r * 2.2), mm(mat), (bx + sgn * h * 0.3, hb.c.y, hb.top + h * 0.45), bev=0.04)
            b('horn_c', (r * 2.0, r * 2.0, h * 0.5), mm(mat), (bx + sgn * h * 0.62, hb.c.y, hb.top + h * 0.22), bev=0.04)
            b('horn_d', (h * 0.36, r * 1.8, r * 1.8), mm(mat), (bx + sgn * h * 0.46, hb.c.y - 0.02, hb.top + h * 0.0), bev=0.03)
        else:  # antler: stepped branches
            b('antler', (r * 1.6, r * 1.6, h), mm(mat), (bx + sgn * h * 0.1, hb.c.y, hb.top + h / 2 - 0.04), rot=(0, sgn * 14, 0), bev=0.03)
            for i in range(n):
                t = (i + 1) / (n + 1)
                ln = h * (0.5 - 0.1 * i)
                b('antler_tine', (ln, r * 1.3, r * 1.3), mm(mat), (bx + sgn * (h * 0.22 * t + ln / 2 + h * 0.06), hb.c.y, hb.top + h * t), rot=(0, -sgn * 25, 0), bev=0.02)
                p('antler_tip', (r * 1.3, r * 1.3, h * 0.2), mm(mat), (bx + sgn * (h * 0.22 * t + ln + h * 0.03), hb.c.y, hb.top + h * t + h * 0.22))
            p('antler_top', (r * 1.3, r * 1.3, h * 0.2), mm(mat), (bx + sgn * h * 0.22, hb.c.y, hb.top + h * 1.05))


def accessory(kind, box, col='#3fbe4a', col2='#2a8a34', z=None):
    """rarity-3 accessory around the neck / on the head. kinds: scarf, bow, flower, necklace, bandana, bell"""
    a = K.a
    setm('acc', col)
    setm('acc2', col2)
    if kind == 'scarf':
        z = box.top - 0.06 if z is None else z
        b('scarf', (box.s.x + 0.12, box.s.x * 0.62, 0.24), mm('acc'), (0, box.front + box.s.x * 0.28, z))
        b('scarf_knot', (0.28, 0.16, 0.22), mm('acc2'), (0.3, box.front - 0.06, z - 0.1), bev=0.03)
        b('scarf_end', (0.2, 0.08, 0.4), mm('acc'), (0.42, box.front - 0.08, z - 0.34), rot=(0, 12, 0), bev=0.03)
        b('scarf_end', (0.18, 0.08, 0.3), mm('acc2'), (0.22, box.front - 0.09, z - 0.3), rot=(0, -8, 0), bev=0.03)
        for sgn, n in LR:
            for j in range(3):
                p('scarf_dot', (0.03, 0.09, 0.09), mm('white'), (sgn * (box.s.x / 2 + 0.065), box.front + 0.1 + 0.18 * j, z))
    elif kind == 'bow':
        z = box.top if z is None else z
        b('bow_knot', (0.16, 0.14, 0.16), mm('acc2'), (0.34 * box.s.x, box.c.y - 0.1, z + 0.08), bev=0.03)
        for sgn in (-1, 1):
            b('bow_wing', (0.26, 0.12, 0.26), mm('acc'), (0.34 * box.s.x + sgn * 0.2, box.c.y - 0.1, z + 0.1), rot=(0, sgn * 20, 0), bev=0.04)
            p('bow_fold', (0.1, 0.13, 0.12), mm('acc2'), (0.34 * box.s.x + sgn * 0.14, box.c.y - 0.1, z + 0.1))
            b('bow_tail', (0.1, 0.1, 0.22), mm('acc'), (0.34 * box.s.x + sgn * 0.1, box.c.y - 0.08, z - 0.08), rot=(0, sgn * 25, 0), bev=0.02)
    elif kind == 'flower':
        z = box.top if z is None else z
        c0 = (-0.3 * box.s.x, box.c.y - 0.15, z + 0.06)
        p('flower_core', (0.12, 0.12, 0.08), mm('acc2'), c0)
        for i in range(5):
            ang = math.radians(i * 72)
            p('petal', (0.13, 0.13, 0.05), mm('acc'), (c0[0] + math.cos(ang) * 0.14, c0[1] + math.sin(ang) * 0.14, c0[2] - 0.01))
        p('flower_leaf', (0.16, 0.08, 0.04), studs(a.id + '_accleaf', '#5bbb36'), (c0[0] + 0.2, c0[1] + 0.12, c0[2] - 0.02), rot=(0, 0, 30))
    elif kind in ('necklace', 'bell'):
        z = box.top - 0.1 if z is None else z
        b('collar', (box.s.x + 0.1, box.s.x * 0.6, 0.12), mm('acc'), (0, box.front + box.s.x * 0.27, z))
        for i in range(5):
            u = (i - 2) * 0.2
            p('bead', (0.1, 0.06, 0.1), mm('acc2' if i % 2 else 'white'), (u * box.s.x, box.front - 0.04, z - 0.02 - (0.06 if i == 2 else 0)), rot=(0, 45, 0))
        if kind == 'bell':
            b('bell', (0.2, 0.16, 0.2), mm('acc2'), (0, box.front - 0.08, z - 0.2), bev=0.05)
            p('bell_slot', (0.12, 0.03, 0.04), mm('line'), (0, box.front - 0.165, z - 0.24))
        else:
            p('pendant', (0.16, 0.06, 0.16), mm('acc2'), (0, box.front - 0.07, z - 0.2), rot=(0, 45, 0))
    elif kind == 'bandana':
        z = box.top - 0.02 if z is None else z
        b('bandana', (box.s.x + 0.06, box.s.y + 0.06, 0.16), mm('acc'), (0, box.c.y, z))
        b('bandana_knot', (0.16, 0.14, 0.16), mm('acc2'), (box.s.x * 0.3, box.back + 0.06, z), bev=0.03)
        b('bandana_tail', (0.12, 0.3, 0.08), mm('acc'), (box.s.x * 0.36, box.back + 0.24, z - 0.06), rot=(-20, 0, 10), bev=0.02)
        b('bandana_tail', (0.1, 0.24, 0.08), mm('acc2'), (box.s.x * 0.22, box.back + 0.22, z - 0.1), rot=(-30, 0, -10), bev=0.02)
        for i in range(4):
            p('bandana_dot', (0.08, 0.03, 0.08), mm('white'), ((i - 1.5) * box.s.x * 0.22, box.front - 0.035, z), rot=(0, 45, 0))


def glow_marks(box, faces=('l', 'r'), n=3, col='glow', seg_name='glow', parent='body', style='rune', col2=None, size=0.14):
    """rarity 4+: glowing Neon marks on a body block, in their own segment so they can flicker"""
    a = K.a
    if seg_name not in a.segs:
        sg(seg_name, parent, tuple(box.c))
        a.glow.append(seg_name)
    else:
        use(seg_name)
    k = 0
    for f in faces:
        for i in range(n):
            t = (i + 0.5) / n - 0.5
            m_ = mm(col2) if (col2 and i % 2) else mm(col)
            if style == 'stripe':
                on(box, f, t * 0.8, 0.0, (size * 0.6, box.s.z * 0.5 if f in 'lrfk' else box.s.y * 0.5), m_, th=0.035, name='glow_stripe')
            elif style == 'star':
                on(box, f, t * 0.8, 0.12 * (1 if i % 2 else -1), (size, size), m_, th=0.035, name='glow_star',
                   rot=((45, 0, 0) if f in 'lr' else ((0, 45, 0) if f in 'fk' else (0, 0, 45))))
            else:
                on(box, f, t * 0.8, 0.1 * (1 if i % 2 else -1), (size, size * 0.85), m_, th=0.035, name='glow_rune')
                on(box, f, t * 0.8 + 0.12, 0.1 * (1 if i % 2 else -1) + 0.16, (size * 0.42, size * 0.42), m_, th=0.035, name='glow_dot')
            k += 1
    use(parent)


def orbit_kit(center, radius, n=6, col='glow', col2=None, size=0.12, name='orbit', dz=0.4, shape='gem', parent='root', big=None):
    """floating pieces circling the body (rarity 5-6): own segment, pivot on the body axis"""
    a = K.a
    sg(name, parent, center)
    a.orbits.append(name)
    for i in range(n):
        ang = math.radians(i * 360.0 / n + 40)
        q = (center[0] + math.cos(ang) * radius, center[1] + math.sin(ang) * radius, center[2] + ((i % 3) - 1) * dz)
        m_ = mm(col2) if (col2 and i % 2) else mm(col)
        if shape == 'ring':
            p('orbit_plate', (size * 2.2, size * 0.8, size * 0.5), m_, q, rot=(0, 0, math.degrees(ang) + 90))
        elif shape == 'cross':
            p('orbit_a', (size * 1.6, size * 0.5, size * 0.5), m_, q)
            p('orbit_b', (size * 0.5, size * 0.5, size * 1.6), m_, q)
        elif shape == 'bubble':
            s2 = size * (1.6 if i % 3 == 0 else 1.0)
            p('orbit_bubble', (s2, s2, s2), m_, q)
            p('orbit_bubble_hi', (s2 * 0.3, s2 * 0.3, s2 * 0.3), mm('white'), (q[0] - s2 * 0.25, q[1] - s2 * 0.5, q[2] + s2 * 0.25))
        elif shape == 'shard':
            p('orbit_shard', (size * 0.6, size * 0.6, size * 3.0), m_, q, rot=(0, 15 * (1 if i % 2 else -1), 45))
            p('orbit_shard_tip', (size * 0.4, size * 0.4, size * 0.8), mm('white'), (q[0], q[1], q[2] + size * 1.8), rot=(0, 0, 45))
        elif shape == 'flame':
            p('orbit_flame', (size * 1.2, size * 1.2, size * 1.2), m_, q, rot=(45, 45, 0))
            p('orbit_flame_tip', (size * 0.7, size * 0.7, size * 1.4), m_, (q[0], q[1], q[2] + size * 1.1))
            p('orbit_flame_tip2', (size * 0.4, size * 0.4, size * 0.8), mm('white'), (q[0], q[1], q[2] + size * 1.9))
        elif shape == 'leaf':
            p('orbit_leaf', (size * 2.0, size * 0.3, size * 1.0), m_, q, rot=(30, 0, math.degrees(ang)))
            p('orbit_leaf_vein', (size * 1.8, size * 0.34, size * 0.15), mm('white'), q, rot=(30, 0, math.degrees(ang)))
        elif shape == 'star':
            p('orbit_star_a', (size * 1.8, size * 0.4, size * 0.4), m_, q, rot=(0, 0, math.degrees(ang)))
            p('orbit_star_b', (size * 0.4, size * 0.4, size * 1.8), m_, q, rot=(0, 0, math.degrees(ang)))
            p('orbit_star_c', (size * 0.7, size * 0.7, size * 0.7), mm('white'), q, rot=(45, 45, 0))
        elif shape == 'gear':
            p('orbit_gear', (size * 1.6, size * 0.4, size * 1.6), m_, q, rot=(0, 0, math.degrees(ang)))
            for t in range(4):
                p('orbit_tooth', (size * 0.5, size * 0.42, size * 0.5), m_, (q[0] + math.cos(t * 1.571) * size * 0.95, q[1], q[2] + math.sin(t * 1.571) * size * 0.95))
        else:
            p('orbit_gem', (size, size, size * 1.5), m_, q, rot=(45, 0, math.degrees(ang)))
            p('orbit_gem_c', (size * 0.5, size * 0.5, size * 0.5), mm('white'), (q[0], q[1], q[2] + size * 1.0), rot=(45, 45, 0))
    if big:
        big(center, radius)
    use('body')


def halo_kit(hb, col='glow', r=0.55, n=8, dz=0.45, kind='halo'):
    """rarity 6: floating crown / halo above the head (own segment under head, spins in Idle)"""
    a = K.a
    c = (hb.c.x, hb.c.y, hb.top + dz)
    sg('halo', 'head', c)
    a.orbits.append('halo')
    for i in range(n):
        ang = math.radians(i * 360.0 / n)
        q = (c[0] + math.cos(ang) * r, c[1] + math.sin(ang) * r, c[2])
        if kind == 'shards':
            p('crown_shard', (0.12, 0.12, 0.5 if i % 2 else 0.32), mm(col), (q[0], q[1], q[2] + (0.2 if i % 2 else 0.1)), rot=(0, 0, 45))
            continue
        if kind == 'flames':
            p('crown_flame', (0.16, 0.16, 0.16), mm(col), q, rot=(45, 45, 0))
            p('crown_flame_tip', (0.08, 0.08, 0.3 if i % 2 else 0.2), mm(col), (q[0], q[1], q[2] + 0.2))
            continue
        if kind == 'stars':
            p('crown_star_a', (0.24, 0.06, 0.06), mm(col), q, rot=(0, 0, math.degrees(ang)))
            p('crown_star_b', (0.06, 0.06, 0.24), mm(col), q)
            continue
        if kind == 'leaves':
            p('crown_leaf', (0.1, 0.24, 0.3), mm(col), (q[0], q[1], q[2] + 0.08), rot=(25, 0, math.degrees(ang) + 90))
            continue
        if kind == 'gears':
            p('crown_gear', (0.24, 0.08, 0.24), mm(col), q, rot=(0, 0, math.degrees(ang) + 90))
            p('crown_gear_hub', (0.08, 0.1, 0.08), mm('white'), q, rot=(0, 0, math.degrees(ang) + 90))
            continue
        p('halo_plate', (0.2, 0.09, 0.09), mm(col), q, rot=(0, 0, math.degrees(ang) + 90))
        if kind == 'crown' and i % 2 == 0:
            p('crown_spike', (0.1, 0.09, 0.26), mm(col), (q[0], q[1], q[2] + 0.16), rot=(0, 0, math.degrees(ang) + 90))
            p('crown_gem', (0.08, 0.08, 0.08), mm('white'), (q[0], q[1], q[2] + 0.34), rot=(45, 45, 0))
    use('head')


def aura_kit(radius, rarity, n=14, motes=10, mote_col='glow', mote_r=None, height=1.6, style='ring'):
    """permanent FX segments (not exported with the model): aura ring at the feet (r5 yellow, r6 red), drifting motes, r4 sparks"""
    a = K.a
    z = K.Z0 - (a.hover / K.S if a.hover else 0.0)        # ground level in nominal units
    if rarity >= 5:
        col = '#ffe600' if rarity == 5 else '#ff2a2a'
        am = neon('%s_aura' % a.id, col, 3.4)
        am['hex'] = col
        sg('fxs_aura', 'root', (0, 0.1, z + 0.03))
        for i in range(n):
            ang = math.radians(i * 360.0 / n)
            cx, cy = math.cos(ang) * radius, 0.1 + math.sin(ang) * radius
            if style == 'diamond':
                p('aura', (0.16, 0.16, 0.06), am, (cx, cy, z + 0.04), rot=(0, 0, 45))
            elif style == 'rays':
                p('aura', (0.36, 0.06, 0.05), am, (cx, cy, z + 0.04), rot=(0, 0, math.degrees(ang)))
            elif style == 'double':
                p('aura', (0.24, 0.05, 0.05), am, (cx, cy, z + 0.04), rot=(0, 0, math.degrees(ang) + 90))
                p('aura2', (0.18, 0.05, 0.05), am, (cx * 0.86, 0.1 + (cy - 0.1) * 0.86, z + 0.04), rot=(0, 0, math.degrees(ang) + 90))
            elif style == 'petals':
                p('aura', (0.3, 0.14, 0.05), am, (cx, cy, z + 0.04), rot=(0, 0, math.degrees(ang) + 45))
            else:
                p('aura', (0.2, 0.12, 0.05 if i % 2 else 0.1), am, (cx, cy, z + 0.04), rot=(0, 0, math.degrees(ang) + 90))
        for i in range(n // 2 + 1):
            ang = math.radians(i * 360.0 / (n // 2 + 1) + 20)
            p('aura_in', (0.08, 0.08, 0.04), am, (math.cos(ang) * radius * 0.78, 0.1 + math.sin(ang) * radius * 0.78, z + 0.03), rot=(0, 0, 45))
        if rarity >= 6:
            for i in range(n):
                ang = math.radians(i * 360.0 / n + 13)
                p('aura_out', (0.12, 0.1, 0.18), am, (math.cos(ang) * radius * 1.22, 0.1 + math.sin(ang) * radius * 1.22, z + 0.09),
                  rot=(0, 0, math.degrees(ang) + 90))
    mr = mote_r or radius * 1.25
    sg('fxs_motes', 'root', (0, 0.1, z + height * 0.6))
    for i in range(motes):
        ang = math.radians(i * 360.0 / motes + 10)
        rr = mr * (1.0 + (i % 3) * 0.16)
        p('mote', (0.07, 0.07, 0.07), mm(mote_col), (math.cos(ang) * rr, 0.1 + math.sin(ang) * rr, z + 0.3 + (i * 7 % 10) * height * 0.11), rot=(45, 45, 0))
    use('body')


def finish(a, cover_margin=1.0):
    """assemble, markers, animation + FX from the roster method/gesture, bake"""
    import moves
    objs = assemble()
    for nm, pos in a.marks.items():
        segn = 'head' if nm == 'Head' else 'body'
        marker(nm, segn, V(pos))
    moves.build(a)
    acts = bake_actions()
    G.root['hover'] = a.hover
    G.root['info'] = json.dumps(dict(method=a.method, gesture=a.gesture, open=a.open, bush_d=a.bush_d, rarity=a.rarity, kind=a.kind, cover=a.cover, reveal=a.reveal_len, idle=a.idle_len,
                                     name=a.name, biome=a.row['biome'], fx_notes=a.fx_notes))
    return acts


def start(row, pal, nominal_h, hover=0.0, z0=0.0):
    a = begin_animal(row, pal, nominal_h, hover, z0)
    a.glow, a.orbits, a.fx_notes = [], [], []
    bs = getattr(K, 'bush', (7.0, 3.6, 4.6))
    a.bush_h, a.bush_depth = bs[2], bs[1]
    a.cover = round(max(1.0, 1.12 * a.H / bs[2]), 2)
    a.len_est = a.H * 0.9
    return a



def grid(box, f, nu, nv, mat, size=(0.14, 0.14), name='plate', span=(0.8, 0.8), th=0.03, offset=0.0, rot=(0, 0, 0)):
    """regular grid of detail plates on one face (scales, rivets, rows of spots)"""
    out = []
    for i in range(nu):
        for j in range(nv):
            u = ((i + 0.5) / nu - 0.5) * span[0] + (offset if j % 2 else 0.0)
            v = ((j + 0.5) / nv - 0.5) * span[1]
            out.append(on(box, f, u, v, size, mat, th=th, name=name, rot=rot))
    return out
