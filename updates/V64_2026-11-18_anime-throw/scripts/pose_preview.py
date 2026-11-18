"""Стик-фигуры поз и клипов R15 из PoseData.luau: посмотреть анимацию, не запуская Roblox.

    python tools/pose_preview.py poses out.png [имя позы ...]      лист поз (вид сбоку, спереди)
    python tools/pose_preview.py clips out.png Throw1 Throw5 ...   раскадровка клипов (12 кадров, вид сбоку)

Правила те же, что в Client/Animator.luau: Motor6D.Transform = fromEulerAnglesYXZ(x, y, z) в градусах, у Root ещё и
смещение root. Скелет приблизительный (стандартный R15), копьё рисуется по направлению таза с подъёмом 0.3.
Сверено на известных позах: kneel, aim, release выглядят как в игре. Нужен Pillow.
"""
import math, re, sys
from PIL import Image, ImageDraw

def rx(a):
    c, s = math.cos(a), math.sin(a); return [[1,0,0],[0,c,-s],[0,s,c]]
def ry(a):
    c, s = math.cos(a), math.sin(a); return [[c,0,s],[0,1,0],[-s,0,c]]
def rz(a):
    c, s = math.cos(a), math.sin(a); return [[c,-s,0],[s,c,0],[0,0,1]]
def mm(a, b): return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(a, v): return [sum(a[i][k]*v[k] for k in range(3)) for i in range(3)]
def add(a, b): return [a[i]+b[i] for i in range(3)]
I3 = [[1,0,0],[0,1,0],[0,0,1]]
def euler_yxz(d):  # градусы {x,y,z} -> R = Ry*Rx*Rz
    x, y, z = [math.radians(v) for v in d]
    return mm(ry(y), mm(rx(x), rz(z)))

# сустав: (родитель, точка сустава в координатах родителя, дальний конец кости в координатах самой кости)
J = {
    'Root': (None, [0,-1.0,0], [0,0.4,0]),            # таз; конец = сустав Waist
    'Waist': ('Root', [0,0.4,0], [0,1.6,0]),          # конец = шея
    'Neck': ('Waist', [0,1.6,0], [0,0.9,0]),          # конец = макушка
    'RightShoulder': ('Waist', [1.0,1.36,0], [0.25,-0.75,0]),
    'RightElbow': ('RightShoulder', [0.25,-0.75,0], [0,-0.75,0]),
    'RightWrist': ('RightElbow', [0,-0.75,0], [0,-0.3,0]),
    'LeftShoulder': ('Waist', [-1.0,1.36,0], [-0.25,-0.75,0]),
    'LeftElbow': ('LeftShoulder', [-0.25,-0.75,0], [0,-0.75,0]),
    'LeftWrist': ('LeftElbow', [0,-0.75,0], [0,-0.3,0]),
    'RightHip': ('Root', [0.5,0.0,0], [0,-0.85,0]),
    'RightKnee': ('RightHip', [0,-0.85,0], [0,-0.9,0]),
    'RightAnkle': ('RightKnee', [0,-0.9,0], [0,-0.25,-0.45]),
    'LeftHip': ('Root', [-0.5,0.0,0], [0,-0.85,0]),
    'LeftKnee': ('LeftHip', [0,-0.85,0], [0,-0.9,0]),
    'LeftAnkle': ('LeftKnee', [0,-0.9,0], [0,-0.25,-0.45]),
}
ORDER = ['Root','Waist','Neck','RightShoulder','RightElbow','RightWrist','LeftShoulder','LeftElbow','LeftWrist','RightHip','RightKnee','RightAnkle','LeftHip','LeftKnee','LeftAnkle']

def fk(pose):
    """pose: {joint: [x,y,z] градусы, 'root': [x,y,z] смещение}. Возвращает {joint: (start, end, R)} в координатах HRP."""
    out = {}
    for j in ORDER:
        par, at, tip = J[j]
        if par is None:
            pr, pp = I3, [0,0,0]
            off = pose.get('root', [0,0,0])
            start = add(add(pp, mv(pr, at)), off)
        else:
            ps, pe, pr = out[par]
            start = add(ps, mv(pr, at))
        R = mm(pr, euler_yxz(pose.get(j, [0,0,0])))
        out[j] = (start, add(start, mv(R, tip)), R)
    return out

def load_poses(path):
    s = open(path, encoding='utf8').read()
    i = s.index('poses = {')
    poses = {}
    for m in re.finditer(r'\n\t\t(\w+) = \{(.*?)\n\t\t\},', s[i:], re.S):
        p = {}
        for jm in re.finditer(r'(\w+) = \{([-\d., ]+)\}', m.group(2)):
            p[jm.group(1)] = [float(v) for v in jm.group(2).split(',')]
        poses[m.group(1)] = p
    return poses

COL = {'Right': (230, 70, 60), 'Left': (60, 120, 235)}
def draw(dr, ox, oy, sc, pose, view, spear=None, label=None):
    sk = fk(pose)
    def P(v):
        if view == 'side':   # камера справа (+X), смотрит на -X: вправо на экране = -Z (вперёд)
            return (ox - v[2]*sc, oy - v[1]*sc, v[0])
        if view == 'front':  # камера спереди, смотрит на +Z: вправо на экране = +X... зеркально: правая рука слева
            return (ox - v[0]*sc, oy - v[1]*sc, -v[2])
        return (ox + v[0]*sc, oy + v[2]*sc, v[1])  # top: вперёд = вверх экрана
    dr.line([ox-60, oy+3.0*sc, ox+60, oy+3.0*sc], fill=(90, 90, 90), width=1)
    segs = []
    for j in ORDER:
        s, e, R = sk[j]
        c = COL['Right'] if j.startswith('Right') else COL['Left'] if j.startswith('Left') else (235, 235, 235)
        a, b = P(s), P(e)
        segs.append(((a[2]+b[2])/2, a, b, c, 5 if j in ('Root','Waist') else 4))
    # плечевой пояс и таз
    for a, b in ((sk['RightShoulder'][0], sk['LeftShoulder'][0]), (sk['RightHip'][0], sk['LeftHip'][0])):
        pa, pb = P(a), P(b); segs.append(((pa[2]+pb[2])/2, pa, pb, (200, 200, 200), 3))
    if spear:
        hand = sk['RightWrist'][1]
        d = spear
        a = P(add(hand, [-d[0]*1.5, -d[1]*1.5, -d[2]*1.5])); b = P(add(hand, [d[0]*5, d[1]*5, d[2]*5]))
        segs.append(((a[2]+b[2])/2 + 0.01, a, b, (240, 200, 60), 2))
    for _, a, b, c, w in sorted(segs, key=lambda t: t[0]):
        dr.line([a[0], a[1], b[0], b[1]], fill=c, width=w)
    h = P(sk['Neck'][1]); n = P(sk['Neck'][0])
    cx, cy = (h[0]+n[0])/2, (h[1]+n[1])/2
    dr.ellipse([cx-0.42*sc, cy-0.42*sc, cx+0.42*sc, cy+0.42*sc], outline=(255, 255, 255), width=2)
    # нос: куда смотрит голова
    Rn = sk['Neck'][2]; nose = P(add([(sk['Neck'][0][i]+sk['Neck'][1][i])/2 for i in range(3)], mv(Rn, [0, 0, -0.6])))
    dr.line([cx, cy, nose[0], nose[1]], fill=(255, 255, 255), width=2)
    if label: dr.text((ox-55, oy+3.0*sc+6), label, fill=(255, 255, 255))

def sheet(items, path, cols=6, views=('side', 'front'), sc=26):
    cw, ch = 150, 190
    rows = (len(items) + cols - 1)//cols
    img = Image.new('RGB', (cw*cols, ch*rows*len(views)), (38, 40, 46))
    dr = ImageDraw.Draw(img)
    for i, it in enumerate(items):
        label, pose = it[0], it[1]; spear = it[2] if len(it) > 2 else None
        for vi, v in enumerate(views):
            ox = (i % cols)*cw + cw//2; oy = ((i//cols)*len(views) + vi)*ch + 95
            draw(dr, ox, oy, sc, pose, v, spear, label + ' ' + v)
    img.save(path); print('saved', path)


POSE_FILE = 'source/ReplicatedStorage/Shared/PoseData.luau'


def load_clip(src, name):
    m = re.search(r'\n\t\t' + name + r' = \{(.*?)\n\t\t\},', src, re.S)
    body = m.group(1)
    keys = re.search(r'keys = \{(.*)\},\n', body).group(1)
    ks = [(float(a), b, c or None) for a, b, c in re.findall(r'\{([\d.]+), "(\w+)"(?:, "(\w+)")?\}', keys)]
    rel = re.search(r'release = ([\d.]+)', body)
    return ks, float(rel.group(1)) if rel else None


def ease(kind, u):
    u = max(0, min(1, u))
    if kind == 'in': return u*u
    if kind == 'out': return 1-(1-u)*(1-u)
    if kind == 'lin': return u
    return u*u*(3-2*u)


def clip_strips(names, path, frames=12):
    src = open(POSE_FILE, encoding='utf8').read()
    poses = load_poses(POSE_FILE)
    JN = ORDER + ['root']
    def blend(a, b, u):
        return {j: [a.get(j, [0,0,0])[i] + (b.get(j, [0,0,0])[i] - a.get(j, [0,0,0])[i])*u for i in range(3)] for j in JN}
    def at(ks, t):
        for (ta, pa, _), (tb, pb, eb) in zip(ks, ks[1:]):
            if t <= tb:
                return blend(poses[pa], poses[pb], ease(eb, (t-ta)/max(tb-ta, 1e-3)))
        return blend(poses[ks[-1][1]], poses[ks[-1][1]], 0)
    cw, ch, sc = 132, 330, 24
    img = Image.new('RGB', (cw*frames, ch*len(names)), (38, 40, 46)); dr = ImageDraw.Draw(img)
    for r, name in enumerate(names):
        ks, rel = load_clip(src, name)
        end = min(ks[-1][0], (rel or 0.5) + 0.75)
        for i in range(frames):
            t = end*i/(frames-1)
            po = at(ks, t)
            yaw = math.radians(po['Root'][1]); d = [-math.sin(yaw), 0.3, -math.cos(yaw)]
            n = math.sqrt(sum(v*v for v in d)); d = [v/n for v in d]
            mark = ' *' if rel and abs(t-rel) < end/(frames-1)/2 else ''
            draw(dr, i*cw + cw//2, r*ch + 215, sc, po, 'side', d if (rel is None or t < rel) else None, '%s %.2f%s' % (name, t, mark))
    img.save(path); print('saved', path)


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('poses', 'clips'):
        sys.exit(__doc__)
    if sys.argv[1] == 'clips':
        clip_strips(sys.argv[3:], sys.argv[2])
    else:
        poses = load_poses(POSE_FILE)
        names = sys.argv[3:] or sorted(poses)
        sheet([(n, poses[n], [0, 0.3, -1]) for n in names if n in poses], sys.argv[2])
