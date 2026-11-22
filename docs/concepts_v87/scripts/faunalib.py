# SpearHunt V87 fauna - helper library (Blender 4.2, EEVEE Next)
# Units: 1 Blender unit = 1 stud. Z up, animals face -Y. Origin of every animal = ground under body centre.
# Animals are rigid segments (one mesh object per segment, origin at the joint) parented in a hierarchy.
# Surface: SH_Studs node group (UV-driven stud grid). UVs: box projection in segment-local studs, 1 UV = UVSPAN studs.
import bpy, bmesh, math, random, os, json
from mathutils import Vector, Matrix, Euler, Quaternion, noise

OUT = r"C:\Users\nikit\OneDrive\Рабочий стол\Роблокс\robloxgame\docs\concepts_v87"
EXP = r"C:\SpearHuntAssets\fauna"
STUD = 0.25          # stud pitch in studs (Blender units)
UVSPAN = STUD * 4    # one 512 px tile = 4 studs
FPS = 30


class G:
    scene = None
    aid = None        # current animal / bush id
    coll = None       # main collection
    fxc = None        # FX collection
    seg = None        # current segment name
    parts = {}        # seg -> [objects]
    segs = {}         # seg -> dict(parent, joint)
    tmp = None        # temp collection for parts
    fx = False
    ol = 0.025
    nparts = 0
    keys = {}         # clip -> seg -> [(frame, dloc, rot, scale)]
    clips = {}        # clip -> length frames


def scene():
    return G.scene


# ---------------------------------------------------------------- colours
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def H(h, a=1.0):
    h = h.lstrip('#')
    return (_lin(int(h[0:2], 16) / 255), _lin(int(h[2:4], 16) / 255), _lin(int(h[4:6], 16) / 255), a)


# ---------------------------------------------------------------- SH_Studs node group
def studs_group():
    ng = bpy.data.node_groups.get('SH_Studs')
    if ng:
        return ng
    ng = bpy.data.node_groups.new('SH_Studs', 'ShaderNodeTree')
    itf = ng.interface
    itf.new_socket('Color', in_out='INPUT', socket_type='NodeSocketColor').default_value = (0.8, 0.2, 0.2, 1)
    s = itf.new_socket('Tint', in_out='INPUT', socket_type='NodeSocketFloat')
    s.default_value = 0.07
    s = itf.new_socket('StudSize', in_out='INPUT', socket_type='NodeSocketFloat')
    s.default_value = STUD
    s = itf.new_socket('Strength', in_out='INPUT', socket_type='NodeSocketFloat')
    s.default_value = 0.35
    itf.new_socket('BSDF', in_out='OUTPUT', socket_type='NodeSocketShader')
    N, Lk = ng.nodes.new, ng.links.new
    gi = N('NodeGroupInput')
    go = N('NodeGroupOutput')
    tc = N('ShaderNodeTexCoord')
    # p = UV * UVSPAN / StudSize  (stud units)
    dv = N('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[0].default_value = UVSPAN
    Lk(gi.outputs['StudSize'], dv.inputs[1])
    p = N('ShaderNodeVectorMath'); p.operation = 'SCALE'
    Lk(tc.outputs['UV'], p.inputs[0]); Lk(dv.outputs[0], p.inputs['Scale'])
    # f = fract(p) - 0.5 ; q = |f| - 0.22 ; d = length(max(q,0)) - 0.12
    fr = N('ShaderNodeVectorMath'); fr.operation = 'FRACTION'; Lk(p.outputs[0], fr.inputs[0])
    sb = N('ShaderNodeVectorMath'); sb.operation = 'SUBTRACT'; Lk(fr.outputs[0], sb.inputs[0]); sb.inputs[1].default_value = (0.5, 0.5, 0.0)
    ab = N('ShaderNodeVectorMath'); ab.operation = 'ABSOLUTE'; Lk(sb.outputs[0], ab.inputs[0])
    q = N('ShaderNodeVectorMath'); q.operation = 'SUBTRACT'; Lk(ab.outputs[0], q.inputs[0]); q.inputs[1].default_value = (0.2, 0.2, 0.0)
    mx = N('ShaderNodeVectorMath'); mx.operation = 'MAXIMUM'; Lk(q.outputs[0], mx.inputs[0]); mx.inputs[1].default_value = (0, 0, 0)
    ln = N('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; Lk(mx.outputs[0], ln.inputs[0])
    d = N('ShaderNodeMath'); d.operation = 'SUBTRACT'; Lk(ln.outputs['Value'], d.inputs[0]); d.inputs[1].default_value = 0.1
    # mask: 1 inside stud, soft edge
    mr = N('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'
    Lk(d.outputs[0], mr.inputs['Value'])
    mr.inputs['From Min'].default_value = 0.035
    mr.inputs['From Max'].default_value = -0.035
    # rim ring (thin shadow around the stud edge)
    ring = N('ShaderNodeMath'); ring.operation = 'ABSOLUTE'; Lk(d.outputs[0], ring.inputs[0])
    rr = N('ShaderNodeMapRange'); rr.interpolation_type = 'SMOOTHSTEP'
    Lk(ring.outputs[0], rr.inputs['Value'])
    rr.inputs['From Min'].default_value = 0.045
    rr.inputs['From Max'].default_value = 0.0
    # checker: 2x2-stud cells -> parity
    hp = N('ShaderNodeVectorMath'); hp.operation = 'SCALE'; Lk(p.outputs[0], hp.inputs[0]); hp.inputs['Scale'].default_value = 0.5
    fl = N('ShaderNodeVectorMath'); fl.operation = 'FLOOR'; Lk(hp.outputs[0], fl.inputs[0])
    sep = N('ShaderNodeSeparateXYZ'); Lk(fl.outputs[0], sep.inputs[0])
    ad = N('ShaderNodeMath'); ad.operation = 'ADD'; Lk(sep.outputs[0], ad.inputs[0]); Lk(sep.outputs[1], ad.inputs[1])
    md = N('ShaderNodeMath'); md.operation = 'FLOORED_MODULO'; Lk(ad.outputs[0], md.inputs[0]); md.inputs[1].default_value = 2.0
    # tint factor = 1 + Tint*(2*parity-1)
    t2 = N('ShaderNodeMath'); t2.operation = 'MULTIPLY_ADD'; Lk(md.outputs[0], t2.inputs[0]); t2.inputs[1].default_value = 2.0; t2.inputs[2].default_value = -1.0
    t3 = N('ShaderNodeMath'); t3.operation = 'MULTIPLY_ADD'; Lk(t2.outputs[0], t3.inputs[0]); Lk(gi.outputs['Tint'], t3.inputs[1]); t3.inputs[2].default_value = 1.0
    # darken inside stud a little + ring shadow
    dk = N('ShaderNodeMath'); dk.operation = 'MULTIPLY_ADD'; Lk(mr.outputs[0], dk.inputs[0]); dk.inputs[1].default_value = -0.05; dk.inputs[2].default_value = 1.0
    dr = N('ShaderNodeMath'); dr.operation = 'MULTIPLY_ADD'; Lk(rr.outputs[0], dr.inputs[0]); dr.inputs[1].default_value = -0.2; dr.inputs[2].default_value = 1.0
    f1 = N('ShaderNodeMath'); f1.operation = 'MULTIPLY'; Lk(t3.outputs[0], f1.inputs[0]); Lk(dk.outputs[0], f1.inputs[1])
    f2 = N('ShaderNodeMath'); f2.operation = 'MULTIPLY'; Lk(f1.outputs[0], f2.inputs[0]); Lk(dr.outputs[0], f2.inputs[1])
    cm = N('ShaderNodeVectorMath'); cm.operation = 'SCALE'
    Lk(gi.outputs['Color'], cm.inputs[0]); Lk(f2.outputs[0], cm.inputs['Scale'])
    bump = N('ShaderNodeBump')
    Lk(mr.outputs[0], bump.inputs['Height'])
    Lk(gi.outputs['Strength'], bump.inputs['Strength'])
    bump.inputs['Distance'].default_value = 0.02
    bsdf = N('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.55
    for k in ('Specular IOR Level',):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = 0.35
    Lk(cm.outputs[0], bsdf.inputs['Base Color'])
    Lk(bump.outputs[0], bsdf.inputs['Normal'])
    Lk(bsdf.outputs[0], go.inputs['BSDF'])
    return ng


_MC = {}


def _mat(name):
    m = bpy.data.materials.get(name)
    if m and not G.remat:
        return m, None
    if m is None:          # never remove materials in use (that crashed Blender); rebuild nodes in place
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return m, nt


G.remat = True


def studs(name, col, tint=0.07, strength=0.8):
    """matte stud plastic (zone colour)"""
    m, nt = _mat('S_' + name)
    if nt is None:
        return m
    g = nt.nodes.new('ShaderNodeGroup')
    g.node_tree = studs_group()
    g.inputs['Color'].default_value = H(col)
    g.inputs['Tint'].default_value = tint
    g.inputs['StudSize'].default_value = STUD
    g.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(g.outputs[0], o.inputs['Surface'])
    m['base'] = list(H(col))
    m['hex'] = col
    m['kind'] = 'studs'
    m.diffuse_color = H(col)
    return m


def smooth(name, col, rough=0.25):
    """smooth plastic (eyes, claws, horns)"""
    m, nt = _mat('P_' + name)
    if nt is None:
        return m
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = H(col)
    b.inputs['Roughness'].default_value = rough
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(b.outputs[0], o.inputs['Surface'])
    m['base'] = list(H(col))
    m['hex'] = col
    m['kind'] = 'smooth'
    m['rough'] = rough
    m.diffuse_color = H(col)
    return m


def neon(name, col, strength=3.0):
    """Neon glow; object colour alpha fades it (keyframe ob.color[3])"""
    m, nt = _mat('N_' + name)
    if nt is None:
        return m
    N, Lk = nt.nodes.new, nt.links.new
    oi = N('ShaderNodeObjectInfo')
    e = N('ShaderNodeEmission')
    e.inputs['Color'].default_value = H(col)
    e.inputs['Strength'].default_value = strength
    tr = N('ShaderNodeBsdfTransparent')
    mix = N('ShaderNodeMixShader')
    Lk(oi.outputs['Alpha'], mix.inputs[0])
    Lk(tr.outputs[0], mix.inputs[1])
    Lk(e.outputs[0], mix.inputs[2])
    o = N('ShaderNodeOutputMaterial')
    Lk(mix.outputs[0], o.inputs['Surface'])
    m['base'] = list(H(col))
    m['hex'] = col
    m['kind'] = 'neon'
    m['emit'] = strength
    m.diffuse_color = H(col)
    return m


def ghost(name, col, strength=1.5, alpha=0.5, power=1.4):
    """soft volumetric-looking puff (dust, aura); object alpha fades it"""
    m, nt = _mat('A_' + name)
    if nt is None:
        return m
    N, Lk = nt.nodes.new, nt.links.new
    lw = N('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    inv = N('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    Lk(lw.outputs['Facing'], inv.inputs[1])
    pw = N('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = power
    Lk(inv.outputs[0], pw.inputs[0])
    ml = N('ShaderNodeMath'); ml.operation = 'MULTIPLY'; ml.inputs[1].default_value = alpha
    Lk(pw.outputs[0], ml.inputs[0])
    oi = N('ShaderNodeObjectInfo')
    ma = N('ShaderNodeMath'); ma.operation = 'MULTIPLY'
    Lk(ml.outputs[0], ma.inputs[0]); Lk(oi.outputs['Alpha'], ma.inputs[1])
    tr = N('ShaderNodeBsdfTransparent')
    e = N('ShaderNodeEmission'); e.inputs['Color'].default_value = H(col); e.inputs['Strength'].default_value = strength
    mix = N('ShaderNodeMixShader')
    Lk(ma.outputs[0], mix.inputs[0]); Lk(tr.outputs[0], mix.inputs[1]); Lk(e.outputs[0], mix.inputs[2])
    o = N('ShaderNodeOutputMaterial')
    Lk(mix.outputs[0], o.inputs['Surface'])
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass
    m['base'] = list(H(col))
    m['hex'] = col
    m['kind'] = 'ghost'
    m.diffuse_color = H(col)
    return m


def outline_mat():
    name = 'SH_Outline'
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = H('#24161c')
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs['Surface'])
    m.use_backface_culling = True
    m['outline'] = 1
    return m


# ---------------------------------------------------------------- collections
def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    par = parent or G.scene.collection
    if c.name not in [x.name for x in par.children]:
        par.children.link(c)
    return c


def _clear(c):
    for ch in list(c.children):
        _clear(ch)
    for o in list(c.objects):
        d = o.data
        ad = o.animation_data
        bpy.data.objects.remove(o, do_unlink=True)
        if d and d.users == 0 and isinstance(d, bpy.types.Mesh):
            bpy.data.meshes.remove(d)


def _drop_actions(prefix):
    for a in list(bpy.data.actions):
        if a.name.startswith(prefix):
            a.use_fake_user = False
            bpy.data.actions.remove(a)


# ---------------------------------------------------------------- model building
def begin(aid, coll_name, fx_name, place=(0, 0, 0), ol=0.025):
    """start (or rebuild) an animal or bush. place = where it stands in the biome scene"""
    c = get_coll(coll_name)
    f = get_coll(fx_name, c)
    _clear(c)
    _drop_actions('%s__' % aid)
    for clip in ('Reveal', 'Idle', 'Tease_Common', 'Tease_Rare', 'Tease_Epic', 'Open_Burst', 'Open_Part'):
        _drop_actions('%s_%s__' % (clip, aid))
    G.aid, G.coll, G.fxc = aid, c, f
    G.parts, G.segs, G.keys, G.clips = {}, {}, {}, {}
    G.glow = {}
    G.nparts = 0
    G.ol = ol
    G.fx = False
    G.tmp = get_coll('_tmp_parts')
    root = bpy.data.objects.new('%s_root' % aid, None)
    root.empty_display_size = 0.4
    c.objects.link(root)
    root.location = place
    root['rest_loc'] = list(place)
    G.root = root
    G.segs['root'] = dict(parent=None, joint=Vector((0, 0, 0)), obj=root)
    G.seg = None
    return root


def seg(name, parent='root', joint=(0, 0, 0)):
    """declare a rigid segment; joint = pivot in animal rest space. Following parts belong to it."""
    G.segs[name] = dict(parent=parent, joint=Vector(joint), obj=None)
    G.parts.setdefault(name, [])
    G.seg = name


def use(name):
    G.seg = name


def fx(on=True):
    G.fx = on


def _finish(name, bm, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, ol='def', smooth_=True, sharp=40):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ang = math.radians(sharp)
    for f in bm.faces:
        f.smooth = smooth_
    if smooth_:
        for e in bm.edges:
            if len(e.link_faces) == 2:
                e.smooth = e.calc_face_angle(0.0) < ang
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
    me.materials.append(mat)
    if G.fx:
        ob.name = '%s_fx_%s' % (G.aid, name)
        G.fxc.objects.link(ob)
        ob.visible_shadow = False
        ob.location = Vector(loc) + G.root.location
        return ob
    ob['ol'] = G.ol if ol == 'def' else ol
    if mat.get('kind') in ('neon', 'ghost') and ol == 'def':
        ob['ol'] = 0
    G.tmp.objects.link(ob)
    G.parts[G.seg].append(ob)
    G.nparts += 1
    return ob


def _P(axis, a, u, v):
    if axis == 'X':
        return (a, u, v)
    if axis == 'Y':
        return (v, a, u)
    return (u, v, a)


def lathe(name, prof, mat, segs=16, axis='Z', caps=True, **kw):
    bm = bmesh.new()
    rings = []
    for (a, r) in prof:
        if r < 1e-5:
            rings.append([bm.verts.new(_P(axis, a, 0, 0))])
        else:
            rings.append([bm.verts.new(_P(axis, a, r * math.cos(2 * math.pi * j / segs), r * math.sin(2 * math.pi * j / segs)))
                          for j in range(segs)])
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for j in range(segs):
            j2 = (j + 1) % segs
            if len(A) == 1:
                bm.faces.new((A[0], B[j2], B[j]))
            elif len(B) == 1:
                bm.faces.new((A[j], A[j2], B[0]))
            else:
                bm.faces.new((A[j], A[j2], B[j2], B[j]))
    if caps:
        for R in (rings[0], rings[-1]):
            if len(R) > 1:
                bm.faces.new(R)
    return _finish(name, bm, mat, **kw)


def ball(name, r, mat, segs=16, rings=10, **kw):
    """sphere (use scale=(sx,sy,sz) for ellipsoids / capsule-ish blobs)"""
    prof = [(-r * math.cos(math.pi * i / rings), r * math.sin(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe(name, prof, mat, segs, 'Z', **kw)


def capsule(name, r, length, mat, segs=14, axis='Z', **kw):
    """rounded capsule along axis, centred"""
    h = length / 2
    n = 5
    prof = [(-h - r * math.cos(math.pi / 2 * i / n), r * math.sin(math.pi / 2 * i / n)) for i in range(n + 1)]
    prof += [(h + r * math.sin(math.pi / 2 * i / n), r * math.cos(math.pi / 2 * i / n)) for i in range(n + 1)]
    return lathe(name, prof, mat, segs, axis, **kw)


def cyl(name, r, length, mat, segs=14, bev=0.04, axis='Z', r1=None, **kw):
    h = length / 2
    r1 = r if r1 is None else r1
    b = min(bev, r * 0.4, h * 0.45)
    return lathe(name, [(-h, 0), (-h, r - b), (-h + b, r), (h - b, r1), (h, r1 - b), (h, 0)], mat, segs, axis, **kw)


def cone(name, r, h, mat, segs=10, axis='Z', r2=0.0, **kw):
    return lathe(name, [(0, 0), (0, r), (h, r2)] + ([(h, 0)] if r2 > 0 else []), mat, segs, axis, **kw)


def torus(name, R, r, mat, segs=20, rsegs=8, axis='Z', **kw):
    prof = [(r * math.cos(2 * math.pi * i / rsegs), R + r * math.sin(2 * math.pi * i / rsegs)) for i in range(rsegs + 1)]
    return lathe(name, prof, mat, segs, axis, caps=False, **kw)


def box(name, size, mat, bev=0.06, bsegs=2, **kw):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    b = min(bev, min(size) * 0.45)
    if b > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=b, segments=bsegs, profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(name, bm, mat, **kw)


def rock(name, r, mat, seed=0, sub=2, rough=0.22, freq=1.1, flat=False, **kw):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    off = Vector((seed * 7.31, seed * 3.17, seed * 1.93))
    for v in bm.verts:
        n = noise.noise(v.co * freq + off)
        v.co *= r * (1.0 + rough * n * 2.0)
    kw.setdefault('smooth_', not flat)
    return _finish(name, bm, mat, **kw)


def tube(name, pts, rad, mat, segs=8, closed=False, **kw):
    pts = [Vector(p) for p in pts]
    n = len(pts)
    if isinstance(rad, (int, float)):
        rad = [rad] * n
    bm = bmesh.new()
    tans = []
    for i in range(n):
        t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        tans.append(t.normalized())
    up = Vector((0, 0, 1))
    if abs(tans[0].dot(up)) > 0.9:
        up = Vector((0, 1, 0))
    nrm = tans[0].cross(up).normalized()
    rings = []
    for i in range(n):
        if i > 0:
            ax = tans[i - 1].cross(tans[i])
            if ax.length > 1e-6:
                q = Matrix.Rotation(tans[i - 1].angle(tans[i]), 3, ax.normalized())
                nrm = (q @ nrm).normalized()
        nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        bn = tans[i].cross(nrm)
        if rad[i] < 1e-5:
            rings.append([bm.verts.new(pts[i])])
        else:
            rings.append([bm.verts.new(pts[i] + (nrm * math.cos(2 * math.pi * j / segs) + bn * math.sin(2 * math.pi * j / segs)) * rad[i])
                          for j in range(segs)])
    for i in range(n - 1):
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for j in range(segs):
            j2 = (j + 1) % segs
            if len(A) == 1:
                bm.faces.new((A[0], B[j2], B[j]))
            elif len(B) == 1:
                bm.faces.new((A[j], A[j2], B[0]))
            else:
                bm.faces.new((A[j], A[j2], B[j2], B[j]))
    for R in (rings[0], rings[-1]):
        if len(R) > 1:
            bm.faces.new(R)
    return _finish(name, bm, mat, **kw)


def leaf(name, length, width, mat, th=0.05, n=5, cup=0.0, **kw):
    """almond leaf in XY plane pointing +X from origin; cup bends the sides up"""
    bm = bmesh.new()
    top, botm = [], []
    for i in range(1, n):
        t = i / n
        w = width * 0.5 * math.sin(math.pi * t) ** 0.8
        top.append(bm.verts.new((length * t, w, cup * w * w / max(width, 1e-3))))
        botm.append(bm.verts.new((length * t, -w, cup * w * w / max(width, 1e-3))))
    a = bm.verts.new((0, 0, 0))
    z = bm.verts.new((length, 0, 0.0))
    loop = [a] + top + [z] + botm[::-1]
    f = bm.verts.new((length * 0.5, 0, th))
    b = bm.verts.new((length * 0.5, 0, -th))
    m = len(loop)
    for i in range(m):
        bm.faces.new((loop[i], loop[(i + 1) % m], f))
        bm.faces.new((loop[(i + 1) % m], loop[i], b))
    kw.setdefault('sharp', 80)
    return _finish(name, bm, mat, **kw)


def star(name, ro, ri, n, th, mat, **kw):
    bm = bmesh.new()
    ring = []
    for i in range(n * 2):
        a = math.pi * i / n + math.pi / 2
        rr = ro if i % 2 == 0 else ri
        ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), 0)))
    f = bm.verts.new((0, 0, th / 2))
    b = bm.verts.new((0, 0, -th / 2))
    m = len(ring)
    for i in range(m):
        bm.faces.new((ring[i], ring[(i + 1) % m], f))
        bm.faces.new((ring[(i + 1) % m], ring[i], b))
    kw.setdefault('smooth_', False)
    return _finish(name, bm, mat, **kw)


def aim(d, roll=0.0):
    """euler degrees rotating local +Z onto direction d"""
    q = Vector(d).normalized().to_track_quat('Z', 'Y')
    if roll:
        q = q @ Euler((0, 0, math.radians(roll))).to_quaternion()
    return tuple(math.degrees(x) for x in q.to_euler('XYZ'))


def eye(name, r, loc, look=(0, -1, 0), white='#ffffff', iris='#20141c', glow_col=None):
    """big cartoon eye: white ball + dark pupil + 2 highlight dots (smooth, no studs)"""
    loc = Vector(loc)
    d = Vector(look).normalized()
    ball(name + '_white', r, smooth('eye_white', white, 0.2), 12, 8, loc=loc, ol=0.015)
    pm = neon('eye_' + glow_col.lstrip('#'), glow_col, 3.0) if glow_col else smooth('eye_pupil', iris, 0.12)
    ball(name + '_pupil', r * 0.68, pm, 12, 8, loc=loc + d * r * 0.45, ol=0)
    hm = smooth('eye_shine', '#ffffff', 0.05)
    side = d.cross(Vector((0, 0, 1))).normalized()
    ball(name + '_shine', r * 0.22, hm, 8, 5, loc=loc + d * r * 1.02 + Vector((0, 0, r * 0.35)) + side * r * 0.25, ol=0)
    ball(name + '_shine2', r * 0.1, hm, 6, 4, loc=loc + d * r * 1.0 - Vector((0, 0, r * 0.25)) - side * r * 0.2, ol=0)


def blk(name, size, mat, loc=(0, 0, 0), rot=(0, 0, 0), bev=0.04, **kw):
    """blocky part (Minecraft-like): bevelled box centred at loc"""
    return box(name, size, mat, bev=bev, bsegs=1, loc=loc, rot=rot, **kw)


def eye_sq(name, s, loc, white='#ffffff', iris='#1f1520', glow_col=None, wide=1.0):
    """square cartoon eye on a -Y facing surface: white block + dark pupil block + shine pixel"""
    x, y, z = loc
    blk(name + '_white', (s * wide, 0.05, s), smooth('eye_w_' + white.lstrip('#'), white, 0.2), (x, y, z), bev=0.012, ol=0.012)
    pm = neon('eye_' + glow_col.lstrip('#'), glow_col, 3.0) if glow_col else smooth('eye_p_' + iris.lstrip('#'), iris, 0.12)
    blk(name + '_pupil', (s * 0.55 * wide, 0.06, s * 0.7), pm, (x + (0.08 * s if x > 0 else -0.08 * s) * 0, y - 0.012, z - s * 0.1), bev=0.01, ol=0)
    blk(name + '_shine', (s * 0.2, 0.07, s * 0.2), smooth('eye_shine', '#ffffff', 0.05), (x - s * 0.12, y - 0.02, z + s * 0.1), bev=0.005, ol=0)


LR = ((-1, 'L'), (1, 'R'))


def pix(name, size, mat, loc=(0, 0, 0), rot=(0, 0, 0), **kw):
    """small sharp detail cube (12 tris, no outline): patterns, pixels, toes"""
    kw.setdefault('ol', 0)
    return box(name, size, mat, bev=0, loc=loc, rot=rot, smooth_=False, **kw)


def anime_eyes(s, x, y, z, iris, head='head', lash=False, brow=None, brow_tilt=0.0, brow_dz=0.16, pupil='#1f1520',
               glow=None, w=0.82, sleepy=0.0):
    """two big anime eyes on a -Y face, each its own segment 'eye_L/R' (blink = scale Z).
    layers: dark frame, white, coloured iris, pupil, 2 highlights, top lash bar (+ lash cubes), brow on the head"""
    dark = smooth('eye_dark', '#1f1520', 0.2)
    wm = smooth('eye_w_ffffff', '#ffffff', 0.2)
    im = neon('eye_g_' + glow.lstrip('#'), glow, 2.6) if glow else smooth('eye_i_' + iris.lstrip('#'), iris, 0.15)
    pm = smooth('eye_p_' + pupil.lstrip('#'), pupil, 0.1)
    hm = smooth('eye_shine', '#ffffff', 0.05)
    W = s * w
    for sg, n in LR:
        cx = sg * x
        seg('eye_' + n, head, (cx, y, z))
        pix('eye%s_frame' % n, (W + 0.05, 0.03, s + 0.05), dark, (cx, y, z))
        pix('eye%s_white' % n, (W, 0.03, s), wm, (cx, y - 0.012, z))
        pix('eye%s_iris' % n, (W * 0.74, 0.03, s * 0.82), im, (cx, y - 0.024, z - s * 0.06))
        pix('eye%s_pupil' % n, (W * 0.42, 0.03, s * 0.52), pm, (cx, y - 0.036, z - s * 0.1))
        pix('eye%s_hi' % n, (s * 0.26, 0.03, s * 0.26), hm, (cx - W * 0.2, y - 0.048, z + s * 0.2))
        pix('eye%s_hi2' % n, (s * 0.13, 0.03, s * 0.13), hm, (cx + W * 0.22, y - 0.048, z - s * 0.24))
        pix('eye%s_lid' % n, (W + 0.09, 0.05, s * (0.08 + sleepy)), dark, (cx, y - 0.04, z + s * (0.5 - sleepy / 2)))
        if lash:
            pix('eye%s_lash1' % n, (0.05, 0.04, 0.09), dark, (cx + sg * (W / 2 + 0.05), y - 0.03, z + s * 0.5 + 0.03), rot=(0, sg * 30, 0))
            pix('eye%s_lash2' % n, (0.05, 0.04, 0.07), dark, (cx + sg * (W / 2 + 0.07), y - 0.03, z + s * 0.36), rot=(0, sg * 60, 0))
    use(head)
    if brow:
        bm_ = smooth('brow_' + brow.lstrip('#'), brow, 0.4)
        for sg, n in LR:
            pix('brow_' + n, (W * 0.8, 0.04, 0.06), bm_, (sg * x, y - 0.02, z + s * 0.5 + brow_dz), rot=(0, sg * brow_tilt, 0))


def blink(clipname, frames):
    """blink keys for eye_L/eye_R (scale Z squash) at the given clip frames"""
    L = G.clips[clipname]
    for n in ('L', 'R'):
        e = 'eye_' + n
        k(clipname, e, 1, scale=1.0)
        for f in frames:
            k(clipname, e, f - 2, scale=1.0)
            k(clipname, e, f, scale=(1.0, 1.0, 0.1))
            k(clipname, e, f + 2, scale=1.0)
        k(clipname, e, L, scale=1.0)


def pulse(clipname, segname, period=20, amp=0.15):
    """glow flicker for a Neon segment: scale pulse in Blender + 'glow' channel (0..1) stored for creatures.json"""
    L = G.clips[clipname]
    ch = []
    f, up = 1, False
    while f <= L:
        k(clipname, segname, f, scale=1.0 + (amp if up else 0.0))
        ch.append([f, 1.0 if up else 0.55])
        up = not up
        f += period // 2
    if ch[-1][0] != L:
        k(clipname, segname, L, scale=1.0)
        ch.append([L, 0.55])
    G.glow.setdefault(clipname, {})[segname] = ch


# ---------------------------------------------------------------- UV + segment assembly
def box_uv(me):
    """box projection in object-local studs: uv = coords / UVSPAN (uniform density everywhere)"""
    if not me.uv_layers:
        me.uv_layers.new(name='UVMap')
    uv = me.uv_layers.active.data
    me.calc_loop_triangles()
    for p in me.polygons:
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if ax == 0:
                u, v = co.y * (1 if n.x > 0 else -1), co.z
            elif ax == 1:
                u, v = co.x * (-1 if n.y > 0 else 1), co.z
            else:
                u, v = co.x, co.y * (1 if n.z > 0 else -1)
            uv[li].uv = (u / UVSPAN + 0.5, v / UVSPAN + 0.5)


def assemble():
    """join parts into one mesh per segment (origin at joint), build hierarchy, add outline, UVs"""
    sc = G.scene
    objs = {'root': G.root}
    order = [s for s in G.segs if s != 'root']
    for s in order:
        info = G.segs[s]
        parts = G.parts.get(s, [])
        me = bpy.data.meshes.new('%s_%s' % (G.aid, s))
        bm = bmesh.new()
        mats = []
        olmax = 0.0
        olw = []
        for p in parts:
            pm = p.data.copy()
            olw.append((len(pm.vertices), p.get('ol', 0)))
            M = Matrix.Translation(-info['joint']) @ p.matrix_basis
            pm.transform(M)
            if M.determinant() < 0:
                pm.flip_normals()
            # material remap
            remap = []
            for m in p.data.materials:
                if m not in mats:
                    mats.append(m)
                remap.append(mats.index(m))
            for poly in pm.polygons:
                poly.material_index = remap[poly.material_index] if remap else 0
            bm.from_mesh(pm)
            bpy.data.meshes.remove(pm)
            olmax = max(olmax, p.get('ol', 0))
        bm.to_mesh(me)
        bm.free()
        for m in mats:
            me.materials.append(m)
        # per-part smooth flags survive from_mesh; recompute normals
        box_uv(me)
        ob = bpy.data.objects.new('%s_%s' % (G.aid, s), me)
        (G.fxc if s.startswith('fxs_') else G.coll).objects.link(ob)
        ob['parts'] = len(parts)
        ob['segment'] = s
        info['obj'] = ob
        objs[s] = ob
        if olmax > 0:
            me.materials.append(outline_mat())
            md = ob.modifiers.new('Outline', 'SOLIDIFY')
            md.thickness = olmax
            md.offset = 1.0
            md.use_flip_normals = True
            md.use_rim = False
            md.material_offset = len(mats)
            md.use_quality_normals = True
            vg = ob.vertex_groups.new(name='ol')
            i0 = 0
            for nv, w in olw:
                if w > 0:
                    vg.add(list(range(i0, i0 + nv)), min(1.0, w / olmax), 'REPLACE')
                i0 += nv
            md.vertex_group = 'ol'
            md.thickness_vertex_group = 0.0
    for s in order:
        info = G.segs[s]
        ob = info['obj']
        par = G.segs[info['parent']]
        ob.parent = par['obj']
        ob.matrix_parent_inverse = Matrix()
        ob.location = info['joint'] - par['joint']
        info['rest'] = ob.location.copy()
        ob['rest_loc'] = list(ob.location)
    for s in order:
        for p in G.parts.get(s, []):
            d = p.data
            bpy.data.objects.remove(p, do_unlink=True)
            if d.users == 0:
                bpy.data.meshes.remove(d)
    return objs


def marker(name, segname, pos):
    """Head / Chest / Hit empties, pos in animal rest space"""
    s = G.segs[segname]
    e = bpy.data.objects.new('%s_%s' % (G.aid, name), None)
    e.empty_display_type = 'SPHERE'
    e.empty_display_size = 0.15
    G.coll.objects.link(e)
    e.parent = s['obj']
    e.location = Vector(pos) - s['joint']
    e['rest_space'] = list(pos)
    return e


# ---------------------------------------------------------------- animation (clip-local frames, keys as offsets from rest)
def clip(name, length):
    G.clips[name] = length
    G.keys.setdefault(name, {})


def k(clipname, segname, f, loc=None, rot=None, scale=None, ease='BEZIER'):
    """key segment at clip frame f. loc = offset from rest (studs), rot = degrees XYZ, scale = factor"""
    lst = G.keys.setdefault(clipname, {}).setdefault(segname, [])
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    lst.append(dict(f=f, loc=tuple(loc) if loc is not None else None, rot=tuple(rot) if rot is not None else None,
                    scale=tuple(scale) if scale is not None else None, ease=ease))


def _obj_for(segname):
    if segname in G.segs:
        return G.segs[segname]['obj']
    return bpy.data.objects.get(segname)


def bake_actions():
    """create one Action per segment per clip: '<Clip>_<aid>__<seg>' (fake user), clip-local frames from 1"""
    out = {}
    for cname, segs in G.keys.items():
        for sname, keys in segs.items():
            ob = _obj_for(sname)
            rest_loc = ob.location.copy() if sname not in G.segs else G.segs[sname].get('rest', ob.location.copy())
            if sname in G.segs and sname != 'root':
                rest_loc = G.segs[sname]['rest']
            elif sname == 'root':
                rest_loc = G.root.location.copy()
            rest_rot = ob.get('rest_rot', [0, 0, 0])
            act = bpy.data.actions.new('%s_%s__%s' % (cname, G.aid, sname))
            act.use_fake_user = True
            keys = sorted(keys, key=lambda d: d['f'])
            for path, n in (('location', 3), ('rotation_euler', 3), ('scale', 3)):
                fld = {'location': 'loc', 'rotation_euler': 'rot', 'scale': 'scale'}[path]
                ks = [d for d in keys if d[fld] is not None]
                if not ks:
                    continue
                for i in range(n):
                    fc = act.fcurves.new(path, index=i)
                    for d in ks:
                        v = d[fld][i]
                        if path == 'location':
                            v = rest_loc[i] + v
                        elif path == 'rotation_euler':
                            v = math.radians(v + rest_rot[i])
                        kp = fc.keyframe_points.insert(d['f'], v, options={'FAST'})
                        kp.interpolation = 'LINEAR' if d['ease'] == 'LINEAR' else ('CONSTANT' if d['ease'] == 'CONSTANT' else 'BEZIER')
                    fc.update()
            out.setdefault(cname, {})[sname] = act.name
    G.root['glow'] = json.dumps(G.glow)
    return out


def assign(cname, aid=None, offset=0):
    """assign clip actions to the segments (others -> rest). offset shifts via NLA strip start"""
    aid = aid or G.aid
    pre = '%s_%s__' % (cname, aid)
    for a in bpy.data.actions:
        if a.name.startswith(pre):
            sname = a.name[len(pre):]
            ob = bpy.data.objects.get('%s_%s' % (aid, sname)) or bpy.data.objects.get(sname)
            if ob is None:
                continue
            ad = ob.animation_data_create()
            if offset:
                ad.action = None
                tr = ad.nla_tracks.new()
                tr.strips.new(a.name, int(1 + offset), a)
            else:
                ad.action = a


def clear_anim(objs):
    for ob in objs:
        if ob.animation_data:
            ob.animation_data.action = None
            for t in list(ob.animation_data.nla_tracks):
                ob.animation_data.nla_tracks.remove(t)


def rest_pose(objs):
    clear_anim(objs)
    for ob in objs:
        if 'rest_loc' in ob:
            ob.location = ob['rest_loc']
        ob.rotation_euler = Euler([math.radians(a) for a in ob.get('rest_rot', [0, 0, 0])], 'XYZ')
        ob.scale = (1, 1, 1)
        if ob.type == 'MESH' or ob.type == 'EMPTY':
            c = list(ob.color)
            c[3] = 1.0
            ob.color = c


def fxkey(ob, f, loc=None, rot=None, scale=None, alpha=None, interp=None):
    """absolute keys for FX objects (scene time)"""
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert('location', frame=f)
    if rot is not None:
        ob.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
        ob.keyframe_insert('rotation_euler', frame=f)
    if scale is not None:
        if isinstance(scale, (int, float)):
            scale = (scale, scale, scale)
        ob.scale = scale
        ob.keyframe_insert('scale', frame=f)
    if alpha is not None:
        c = list(ob.color)
        c[3] = alpha
        ob.color = c
        ob.keyframe_insert('color', index=3, frame=f)
    if interp and ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - f) < 0.01:
                    kp.interpolation = interp


# ---------------------------------------------------------------- stats
def stats(aid, coll_name):
    c = bpy.data.collections[coll_name]
    objs = [o for o in c.objects if o.type == 'MESH']
    tris = 0
    for o in objs:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
    bpy.context.view_layer.update()
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    root = bpy.data.objects['%s_root' % aid]
    inv = root.matrix_world.inverted()
    for o in objs:
        M = inv @ o.matrix_world
        for v in o.data.vertices:
            p = M @ v.co
            for i in range(3):
                mn[i] = min(mn[i], p[i])
                mx[i] = max(mx[i], p[i])
    mats = set()
    for o in objs:
        for m in o.data.materials:
            if m and not m.get('outline'):
                mats.add(m.name)
    return dict(id=aid, segments=len(objs), parts=sum(o.get('parts', 1) for o in objs), tris=tris, materials=len(mats),
                size=[round(mx[i] - mn[i], 2) for i in range(3)], min=[round(x, 2) for x in mn], max=[round(x, 2) for x in mx])


# ---------------------------------------------------------------- scene setup
def setup(scn_name):
    sc = bpy.data.scenes.get(scn_name) or bpy.data.scenes.new(scn_name)
    G.scene = sc
    for w in bpy.context.window_manager.windows:
        w.scene = sc
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError as e:
        print(e)
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, 200
    sc.view_settings.view_transform = 'Standard'
    ee = sc.eevee
    for kk, v in (('taa_render_samples', 32), ('use_shadows', True), ('use_raytracing', False), ('use_gtao', True)):
        if hasattr(ee, kk):
            try:
                setattr(ee, kk, v)
            except Exception:
                pass
    w = bpy.data.worlds.get(scn_name + '_World') or bpy.data.worlds.new(scn_name + '_World')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    lp = nt.nodes.new('ShaderNodeLightPath')
    amb = nt.nodes.new('ShaderNodeBackground')
    amb.name = 'AMB'
    amb.inputs[0].default_value = (0.85, 0.9, 1.0, 1)
    amb.inputs[1].default_value = 0.9
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.name = 'CAMBG'
    bg.inputs[0].default_value = H('#bfe6ff')
    mix = nt.nodes.new('ShaderNodeMixShader')
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])
    nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    env = get_coll('Env_' + scn_name)
    sun = bpy.data.objects.get('Sun_' + scn_name)
    if sun is None:
        sun = bpy.data.objects.new('Sun_' + scn_name, bpy.data.lights.new('Sun_' + scn_name, 'SUN'))
        env.objects.link(sun)
    sun.data.energy = 3.2
    sun.data.angle = math.radians(4)
    sun.rotation_euler = Euler((math.radians(50), math.radians(12), math.radians(-28)), 'XYZ')
    cam = bpy.data.objects.get('Cam_' + scn_name)
    if cam is None:
        cam = bpy.data.objects.new('Cam_' + scn_name, bpy.data.cameras.new('Cam_' + scn_name))
        env.objects.link(cam)
    cam.data.clip_end = 600
    sc.camera = cam
    sc.use_nodes = True
    ct = sc.node_tree
    for n in list(ct.nodes):
        ct.nodes.remove(n)
    rl = ct.nodes.new('CompositorNodeRLayers')
    rl.scene = sc
    gl = ct.nodes.new('CompositorNodeGlare')
    types = [i.identifier for i in gl.bl_rna.properties['glare_type'].enum_items]
    gl.glare_type = 'BLOOM' if 'BLOOM' in types else 'FOG_GLOW'
    gl.threshold = 1.9
    gl.mix = -0.4
    try:
        gl.size = 7
    except Exception:
        pass
    co = ct.nodes.new('CompositorNodeComposite')
    ct.links.new(rl.outputs[0], gl.inputs[0])
    ct.links.new(gl.outputs[0], co.inputs[0])
    G.env = env
    return sc


def ground(col, size=60, name=None):
    name = name or 'Ground_' + G.scene.name
    gr = bpy.data.objects.get(name)
    if gr is None:
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size)
        bm.to_mesh(me)
        bm.free()
        gr = bpy.data.objects.new(name, me)
        G.env.objects.link(gr)
        box_uv(me)
        me.materials.append(studs('ground_' + col.lstrip('#'), col, 0.06, 0.25))
    return gr


def mannequin(loc=(0, 0, 0), tag='MQ'):
    c = get_coll('Mannequin_' + G.scene.name)
    _clear(c)
    grey = studs('mq_grey', '#a3a2a5')
    blue = studs('mq_blue', '#0d69ac')
    yel = studs('mq_yellow', '#f5cd30')
    r = bpy.data.objects.new(tag + '_root', None)
    c.objects.link(r)
    r.location = loc

    def blk(nm, size, p, mat):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.05, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
        me = bpy.data.meshes.new(tag + '_' + nm)
        bm.to_mesh(me)
        bm.free()
        box_uv(me)
        o = bpy.data.objects.new(tag + '_' + nm, me)
        me.materials.append(mat)
        c.objects.link(o)
        o.parent = r
        o.location = p
    blk('leg_l', (0.95, 0.95, 2.0), (-0.5, 0, 1.0), blue)
    blk('leg_r', (0.95, 0.95, 2.0), (0.5, 0, 1.0), blue)
    blk('torso', (2.0, 1.0, 2.0), (0, 0, 3.0), grey)
    blk('arm_l', (0.95, 0.95, 2.0), (-1.5, 0, 3.0), yel)
    blk('arm_r', (0.95, 0.95, 2.0), (1.5, 0, 3.0), yel)
    blk('head', (1.15, 1.0, 1.0), (0, 0, 4.5), yel)
    return r


# ---------------------------------------------------------------- export
def _pbr(m):
    key = 'PBR_' + m.name
    p = bpy.data.materials.get(key)
    if p:
        return p
    p = bpy.data.materials.new(key)
    p.use_nodes = True
    b = next(n for n in p.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    col = list(m.get('base', (0.8, 0.8, 0.8, 1)))
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = float(m.get('rough', 0.55))
    if m.get('kind') == 'neon':
        b.inputs['Emission Color'].default_value = col
        b.inputs['Emission Strength'].default_value = float(m.get('emit', 2.0))
    return p


def export_hierarchy(root, path, exclude_fx=True):
    """copy root + mesh descendants (rest pose, PBR mats, no outline, no anim) and export one GLB with hierarchy"""
    sc = G.scene
    tmpc = get_coll('_export_tmp')
    _clear(tmpc)
    mp = {}

    def dup(o, parent):
        if o.type == 'MESH':
            me = o.data.copy()
            first = None           # swap slots in place (materials.clear() would reset every face to slot 0)
            for i, m in enumerate(me.materials):
                if m and not m.get('outline'):
                    me.materials[i] = _pbr(m)
                    first = first or me.materials[i]
            for i, m in enumerate(me.materials):
                if m is None or m.get('outline'):
                    me.materials[i] = first
            c = bpy.data.objects.new(o.name + '__x', me)
        elif o.type == 'EMPTY':
            c = bpy.data.objects.new(o.name + '__x', None)
            c.empty_display_type = o.empty_display_type
        else:
            return
        tmpc.objects.link(c)
        c.parent = parent
        c.matrix_parent_inverse = Matrix()
        if parent is None:
            c.location = (0, 0, 0)
            c.rotation_euler = (0, 0, 0)
        else:
            c.location = o['rest_loc'] if 'rest_loc' in o else o.location
            c.rotation_euler = Euler([math.radians(a) for a in o.get('rest_rot', [0, 0, 0])], 'XYZ')
        c.scale = (1, 1, 1)
        mp[o.name] = c
        for ch in o.children:
            if exclude_fx and any(cc.name.endswith('_FX') for cc in ch.users_collection):
                continue
            dup(ch, c)
    dup(root, None)
    # give copies the original names (originals renamed temporarily)
    ren = []
    for nm, c in mp.items():
        o = bpy.data.objects[nm]
        o.name = nm + '__orig'
        c.name = nm
        ren.append((o, nm))
    for scn in bpy.data.scenes:
        for vl in scn.view_layers:
            for o in vl.objects:
                try:
                    o.select_set(False, view_layer=vl)
                except Exception:
                    pass
    try:
        for c in tmpc.objects:
            c.select_set(True)
        bpy.context.view_layer.objects.active = tmpc.objects[0]
        bpy.ops.export_scene.gltf(filepath=path, use_selection=True, use_active_scene=True, export_format='GLB',
                                  export_apply=False, export_animations=False, export_yup=True, export_texcoords=True,
                                  export_normals=True, export_extras=False)
        n = len(tmpc.objects)
    finally:
        _clear(tmpc)
        bpy.data.collections.remove(tmpc)
        for o, nm in ren:
            o.name = nm
    return n
