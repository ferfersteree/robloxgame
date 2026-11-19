# SpearHunt Gym V83 - helper library for building toon dumbbells / stands in Blender 4.2
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler, noise

SCN = 'GymV83'
OUT = r"C:\Users\nikit\OneDrive\Рабочий стол\Роблокс\robloxgame\docs\concepts_v83"


class G:
    coll = None      # main collection
    fxc = None       # FX collection
    root = None
    fx = False       # FX mode
    ol = 0.035       # outline thickness
    remat = False    # True -> rebuild materials even if they exist


def scene():
    return bpy.data.scenes[SCN]


# ---------------------------------------------------------------- colours
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def H(h, a=1.0):
    h = h.lstrip('#')
    return (_lin(int(h[0:2], 16) / 255), _lin(int(h[2:4], 16) / 255), _lin(int(h[4:6], 16) / 255), a)


def _mixc(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3)) + (1.0,)


# ---------------------------------------------------------------- materials
def _mat(name):
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return m, nt


def outline_mat(name='GYM_Outline', col='#1c1016'):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m, nt = _mat(name)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = H(col)
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs['Surface'])
    m.use_backface_culling = True
    if hasattr(m, 'use_backface_culling_shadow'):
        m.use_backface_culling_shadow = True
    m['base'] = list(H(col))
    m['outline'] = 1
    return m


_MC = {}


def toon(name, base, shade=None, light=None, spec=0.7, rim=0.45, emit=0.0, rimcol='#ffffff'):
    """3-tone toon material. base/shade/light = hex strings."""
    key = 'T_' + name
    if key in _MC and _MC[key].name in bpy.data.materials:
        return _MC[key]
    if not G.remat and key in bpy.data.materials:
        _MC[key] = bpy.data.materials[key]
        return _MC[key]
    b = H(base)
    s = H(shade) if shade else _mixc(tuple(x * 0.5 for x in b[:3]) + (1,), H('#3a1c5a'), 0.22)
    l = H(light) if light else _mixc(b, (1, 1, 1, 1), 0.38)
    m, nt = _mat(key)
    N, L = nt.nodes.new, nt.links.new
    dif = N('ShaderNodeBsdfDiffuse')
    dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = N('ShaderNodeShaderToRGB')
    L(dif.outputs[0], s2r.inputs[0])
    ramp = N('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.interpolation = 'CONSTANT'
    cr.elements[0].position = 0.0
    cr.elements[0].color = s
    cr.elements[1].position = 0.2
    cr.elements[1].color = b
    e3 = cr.elements.new(0.72)
    e3.color = l
    L(s2r.outputs[0], ramp.inputs[0])
    # specular blob
    gl = N('ShaderNodeBsdfGlossy')
    gl.inputs['Roughness'].default_value = 0.28
    g2r = N('ShaderNodeShaderToRGB')
    L(gl.outputs[0], g2r.inputs[0])
    gm = N('ShaderNodeMath')
    gm.operation = 'GREATER_THAN'
    gm.inputs[1].default_value = 0.85
    L(g2r.outputs[0], gm.inputs[0])
    gs = N('ShaderNodeMath')
    gs.operation = 'MULTIPLY'
    gs.inputs[1].default_value = spec
    L(gm.outputs[0], gs.inputs[0])
    mx1 = N('ShaderNodeMixRGB')
    mx1.inputs['Color2'].default_value = (1, 1, 1, 1)
    L(gs.outputs[0], mx1.inputs['Fac'])
    L(ramp.outputs[0], mx1.inputs['Color1'])
    # rim light
    lw = N('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.32
    rm = N('ShaderNodeMath')
    rm.operation = 'GREATER_THAN'
    rm.inputs[1].default_value = 0.6
    L(lw.outputs['Facing'], rm.inputs[0])
    # rim only on lit side
    lit = N('ShaderNodeMath')
    lit.operation = 'GREATER_THAN'
    lit.inputs[1].default_value = 0.2
    L(s2r.outputs[0], lit.inputs[0])
    rr = N('ShaderNodeMath')
    rr.operation = 'MULTIPLY'
    L(rm.outputs[0], rr.inputs[0])
    L(lit.outputs[0], rr.inputs[1])
    rs = N('ShaderNodeMath')
    rs.operation = 'MULTIPLY'
    rs.inputs[1].default_value = rim
    L(rr.outputs[0], rs.inputs[0])
    mx2 = N('ShaderNodeMixRGB')
    mx2.inputs['Color2'].default_value = _mixc(l, H(rimcol), 0.6)
    L(rs.outputs[0], mx2.inputs['Fac'])
    L(mx1.outputs[0], mx2.inputs['Color1'])
    em = N('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 1.0 + emit
    L(mx2.outputs[0], em.inputs['Color'])
    out = N('ShaderNodeOutputMaterial')
    L(em.outputs[0], out.inputs['Surface'])
    m['base'] = list(b)
    m['emit'] = float(emit)
    _MC[key] = m
    return m


def glow(name, col, strength=4.0):
    key = 'G_' + name
    if key in _MC and _MC[key].name in bpy.data.materials:
        return _MC[key]
    if not G.remat and key in bpy.data.materials:
        _MC[key] = bpy.data.materials[key]
        return _MC[key]
    m, nt = _mat(key)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = H(col)
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs['Surface'])
    m['base'] = list(H(col))
    m['emit'] = float(strength)
    m['glow'] = 1
    _MC[key] = m
    return m


def ghost(name, col, strength=2.0, alpha=0.5, power=1.6, edge=False):
    """soft transparent emissive blob (aura / mist). edge=True -> bubble (bright rim)"""
    key = 'A_' + name
    if key in _MC and _MC[key].name in bpy.data.materials:
        return _MC[key]
    if not G.remat and key in bpy.data.materials:
        _MC[key] = bpy.data.materials[key]
        return _MC[key]
    m, nt = _mat(key)
    N, L = nt.nodes.new, nt.links.new
    lw = N('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.5
    inv = N('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    L(lw.outputs['Facing'], inv.inputs[1])
    pw = N('ShaderNodeMath')
    pw.operation = 'POWER'
    pw.inputs[1].default_value = power
    L((lw.outputs['Facing'] if edge else inv.outputs[0]), pw.inputs[0])
    ml = N('ShaderNodeMath')
    ml.operation = 'MULTIPLY'
    ml.inputs[1].default_value = alpha
    L(pw.outputs[0], ml.inputs[0])
    tr = N('ShaderNodeBsdfTransparent')
    e = N('ShaderNodeEmission')
    e.inputs['Color'].default_value = H(col)
    e.inputs['Strength'].default_value = strength
    mix = N('ShaderNodeMixShader')
    L(ml.outputs[0], mix.inputs[0])
    L(tr.outputs[0], mix.inputs[1])
    L(e.outputs[0], mix.inputs[2])
    o = N('ShaderNodeOutputMaterial')
    L(mix.outputs[0], o.inputs['Surface'])
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass
    try:
        m.blend_method = 'BLEND'
    except Exception:
        pass
    m['base'] = list(H(col))
    m['emit'] = float(strength)
    m['ghost'] = 1
    _MC[key] = m
    return m


# ---------------------------------------------------------------- collections
def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    par = parent or scene().collection
    if c.name not in [x.name for x in par.children]:
        par.children.link(c)
    return c


def _clear(c):
    for o in list(c.objects):
        d = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if d and d.users == 0 and isinstance(d, bpy.types.Mesh):
            bpy.data.meshes.remove(d)


def begin(name, ol=0.035):
    """start (or rebuild) a model: collection `name` + child `name_FX`, root empty at origin"""
    c = get_coll(name)
    f = get_coll(name + '_FX', c)
    _clear(c)
    _clear(f)
    d = bpy.data.collections.get(name + '_Display')
    if d:
        _clear(d)
    r = bpy.data.objects.new(name + '_root', None)
    r.empty_display_size = 0.3
    c.objects.link(r)
    G.coll, G.fxc, G.root, G.fx, G.ol = c, f, r, False, ol
    return r


def fx(on=True):
    G.fx = on


def drop(dz):
    """move everything built so far (main + FX) down by dz"""
    for c in (G.coll, G.fxc):
        for o in c.objects:
            if o is not G.root:
                o.location.z -= dz


# ---------------------------------------------------------------- object creation
def _finish(name, bm, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, ol='def', smooth=True, sharp=38, mat2=None):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    ang = math.radians(sharp)
    for f in bm.faces:
        f.smooth = smooth
    if smooth:
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
        G.fxc.objects.link(ob)
        ob.visible_shadow = False
    else:
        G.coll.objects.link(ob)
        t = G.ol if ol == 'def' else ol
        if mat.get('glow') or mat.get('ghost'):
            ob.visible_shadow = False
            if ol == 'def':
                t = 0
        if t:
            me.materials.append(outline_mat())
            md = ob.modifiers.new('Outline', 'SOLIDIFY')
            md.thickness = t
            md.offset = 1.0
            md.use_flip_normals = True
            md.use_rim = False
            md.material_offset = 1
            md.use_quality_normals = True
    ob.parent = G.root
    return ob


def _P(axis, a, u, v):
    if axis == 'X':
        return (a, u, v)
    if axis == 'Y':
        return (v, a, u)
    return (u, v, a)


def lathe(name, prof, mat, segs=16, axis='X', caps=True, **kw):
    """revolve profile [(a, r), ...] around axis"""
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


def cyl(name, r, length, mat, segs=16, bev=0.04, axis='X', **kw):
    h = length / 2
    b = min(bev, r * 0.45, h * 0.45)
    return lathe(name, [(-h, 0), (-h, r - b), (-h + b, r), (h - b, r), (h, r - b), (h, 0)], mat, segs, axis, **kw)


def sphere(name, r, mat, segs=14, rings=8, axis='Z', **kw):
    prof = [(-r * math.cos(math.pi * i / rings), r * math.sin(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe(name, prof, mat, segs, axis, **kw)


def cone(name, r, h, mat, segs=10, axis='Z', r2=0.0, **kw):
    return lathe(name, [(0, 0), (0, r), (h, r2)] + ([(h, 0)] if r2 > 0 else []), mat, segs, axis, **kw)


def torus(name, R, r, mat, segs=20, rsegs=8, axis='X', **kw):
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
    return _finish(name, bm, mat, smooth=not flat, **kw)


def crystal(name, r, h, mat, sides=6, tip=0.3, base=0.75, both=False, **kw):
    """faceted prism along +Z from z=0 (or centred double-terminated if both)"""
    bm = bmesh.new()
    z0 = 0.0
    zt = h * (1 - tip)
    def ring(z, rad):
        return [bm.verts.new((rad * math.cos(2 * math.pi * j / sides), rad * math.sin(2 * math.pi * j / sides), z)) for j in range(sides)]
    if both:
        zb = h * tip
        A = ring(zb, r)
        bot = bm.verts.new((0, 0, 0))
    else:
        A = ring(z0, r * base)
        bot = None
    Bv = ring(zt, r)
    top = bm.verts.new((0, 0, h))
    for j in range(sides):
        j2 = (j + 1) % sides
        bm.faces.new((A[j], A[j2], Bv[j2], Bv[j]))
        bm.faces.new((Bv[j], Bv[j2], top))
        if bot:
            bm.faces.new((A[j2], A[j], bot))
    if not bot:
        bm.faces.new(A)
    if both:
        bmesh.ops.translate(bm, vec=(0, 0, -h / 2), verts=bm.verts)
    kw.setdefault('smooth', False)
    return _finish(name, bm, mat, **kw)


def tube(name, pts, rad, mat, segs=8, closed=False, **kw):
    """sweep a circle along polyline. rad = float or list per point (0 => pointed tip)"""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    if isinstance(rad, (int, float)):
        rad = [rad] * n
    bm = bmesh.new()
    tans = []
    for i in range(n):
        if closed:
            t = pts[(i + 1) % n] - pts[i - 1]
        else:
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
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        A, B = rings[i], rings[(i + 1) % n]
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
    if not closed:
        for R in (rings[0], rings[-1]):
            if len(R) > 1:
                bm.faces.new(R)
    return _finish(name, bm, mat, **kw)


def coil(name, R, r, a0, a1, turns, mat, segs=6, steps=14, axis='X', R1=None, **kw):
    n = max(4, int(turns * steps))
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * turns * t
        rr = R if R1 is None else R + (R1 - R) * t
        pts.append(_P(axis, a0 + (a1 - a0) * t, rr * math.cos(ang), rr * math.sin(ang)))
    return tube(name, pts, r, mat, segs, **kw)


def arc_pts(c, R, a0, a1, n, plane='XZ'):
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        u, v = R * math.cos(a), R * math.sin(a)
        if plane == 'XZ':
            out.append((c[0] + u, c[1], c[2] + v))
        elif plane == 'YZ':
            out.append((c[0], c[1] + u, c[2] + v))
        else:
            out.append((c[0] + u, c[1] + v, c[2]))
    return out


def star(name, ro, ri, n, th, mat, **kw):
    """faceted n-point star in XY plane, thickness along Z"""
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
    kw.setdefault('smooth', False)
    return _finish(name, bm, mat, **kw)


def leaf(name, length, width, mat, th=0.05, n=5, **kw):
    """almond leaf in XY plane pointing +X from origin"""
    bm = bmesh.new()
    top, botm = [], []
    for i in range(1, n):
        t = i / n
        w = width * 0.5 * math.sin(math.pi * t) ** 0.8
        top.append(bm.verts.new((length * t, w, 0)))
        botm.append(bm.verts.new((length * t, -w, 0)))
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


def flame(name, h, r, mat, bend=0.15, segs=8, **kw):
    """teardrop flame along +Z"""
    prof = []
    N_ = 7
    for i in range(N_ + 1):
        t = i / N_
        rr = r * math.sin(math.pi * min(1.0, t * 1.25) ** 0.7) * (1 - t) ** 0.55 * 1.6
        prof.append((h * t, max(rr, 0.0)))
    prof[0] = (0, 0)
    prof[-1] = (h, 0)
    ob = lathe(name, prof, mat, segs, 'Z', **kw)
    for v in ob.data.vertices:
        v.co.x += bend * (v.co.z / max(h, 1e-5)) ** 2 * h
    return ob


def text(name, body, size, depth, mat, font=r"C:\Windows\Fonts\ariblk.ttf", res=2, bevel=0.0, spacing=1.0, **kw):
    cu = bpy.data.curves.new(name + '_cu', 'FONT')
    cu.body = body
    cu.size = size
    cu.extrude = depth
    cu.resolution_u = res
    cu.bevel_depth = bevel
    cu.bevel_resolution = 0
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.space_character = spacing
    try:
        cu.font = bpy.data.fonts.load(font, check_existing=True)
    except Exception:
        pass
    tmp = bpy.data.objects.new(name + '_tmp', cu)
    scene().collection.objects.link(tmp)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    kw.setdefault('smooth', False)
    kw.setdefault('ol', 0)
    return _finish(name, bm, mat, **kw)


def zigzag(a, b, n, amp, seed=0):
    """lightning polyline from a to b"""
    rnd = random.Random(seed)
    a, b = Vector(a), Vector(b)
    pts = [a]
    for i in range(1, n):
        p = a.lerp(b, i / n)
        p += Vector((rnd.uniform(-amp, amp), rnd.uniform(-amp, amp), rnd.uniform(-amp, amp)))
        pts.append(p)
    pts.append(b)
    return pts


def bolt(name, a, b, mat, r=0.04, n=6, amp=0.18, seed=0, **kw):
    pts = zigzag(a, b, n, amp, seed)
    rad = [r * (0.4 + 0.6 * math.sin(math.pi * i / (len(pts) - 1))) for i in range(len(pts))]
    rad[0] = rad[-1] = 0.0
    return tube(name, pts, rad, mat, segs=4, smooth=False, **kw)


def aim(d, roll=0.0):
    """euler degrees that rotate local +Z onto direction d"""
    q = Vector(d).normalized().to_track_quat('Z', 'Y')
    if roll:
        q = q @ Euler((0, 0, math.radians(roll))).to_quaternion()
    e = q.to_euler('XYZ')
    return tuple(math.degrees(x) for x in e)


def radial(s, tilt, ang):
    """unit direction: tilt degrees away from the X axis (sign s), rotated ang degrees around X"""
    t, a = math.radians(tilt), math.radians(ang)
    return Vector((s * math.cos(t), math.sin(t) * math.cos(a), math.sin(t) * math.sin(a)))


# ---------------------------------------------------------------- stats / copies
def stats(name):
    c = bpy.data.collections[name]
    objs = [o for o in c.objects if o.type == 'MESH']
    tris = 0
    for o in objs:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
    f = bpy.data.collections.get(name + '_FX')
    nfx = len(f.objects) if f else 0
    bpy.context.view_layer.update()
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    root = bpy.data.objects[name + '_root']
    inv = root.matrix_world.inverted()
    for o in objs:
        for v in o.data.vertices:
            p = o.matrix_basis @ v.co
            for i in range(3):
                mn[i] = min(mn[i], p[i])
                mx[i] = max(mx[i], p[i])
    return dict(name=name, elements=len(objs), tris=tris, fx=nfx,
                size=[round(mx[i] - mn[i], 2) for i in range(3)],
                min=[round(x, 2) for x in mn], max=[round(x, 2) for x in mx])


def grip_check(name, half=0.5, rmax=0.2):
    """max radius (from X axis) of geometry inside |x|<half ; should be ~0.15-0.2"""
    c = bpy.data.collections[name]
    root = bpy.data.objects[name + '_root']
    inv = root.matrix_world.inverted()
    worst = 0.0
    who = None
    for o in c.objects:
        if o.type != 'MESH':
            continue
        for v in o.data.vertices:
            p = o.matrix_basis @ v.co
            if abs(p.x) < half:
                d = math.hypot(p.y, p.z)
                if d > worst:
                    worst, who = d, o.name
    return dict(max_radius_in_grip=round(worst, 3), by=who, ok=worst <= rmax)


def place_copy(src, dest_coll, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, with_fx=False, tag='copy'):
    """linked-data copy of model `src` (collection name) under a new empty"""
    c = bpy.data.collections[src]
    r = bpy.data.objects.new('%s_%s' % (src, tag), None)
    r.empty_display_size = 0.2
    dest_coll.objects.link(r)
    r.location = loc
    r.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
    r.scale = (scale, scale, scale)
    srcs = [o for o in c.objects if o.type == 'MESH']
    if with_fx:
        fxo = [o for o in bpy.data.collections[src + '_FX'].objects if o.type == 'MESH']
        if callable(with_fx):
            fxo = [o for o in fxo if with_fx(o)]
        srcs += fxo
    for o in srcs:
        d = o.copy()
        dest_coll.objects.link(d)
        d.parent = r
        d.matrix_parent_inverse = Matrix()
    return r


def display(stand, pair_src, pair_pos, minis, shelf_z, pair_fx=True):
    """dress a stand for renders: full-size pair on top + 0.6-scale older levels on the shelves.
    pair_pos = [(loc, rot), ...] in stand-local coords; minis = [(src, shelf_index, slot_index), ...]"""
    st = bpy.data.collections[stand]
    d = get_coll(stand + '_Display', st)
    _clear(d)
    root = bpy.data.objects[stand + '_root']
    out = []
    for i, (loc, rot) in enumerate(pair_pos):
        r = place_copy(pair_src, d, loc, rot, 1.0, pair_fx, 'top%d' % i)
        out.append(r)
    for src, sh, slot in minis:
        mz = stats(src)['min'][2]
        r = place_copy(src, d, (-3.75 + 1.5 * slot, 0.0, shelf_z[sh] - 0.6 * mz + 0.01), (0, 0, 90), 0.6, False, 'mini')
        out.append(r)
    for r in out:
        r.parent = root
        r.matrix_parent_inverse = Matrix()
    return len(out)


# ---------------------------------------------------------------- scene setup
def setup():
    sc = bpy.data.scenes.get(SCN)
    if sc is None:
        sc = bpy.data.scenes.new(SCN)
    for w in bpy.context.window_manager.windows:
        w.scene = sc
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError as e:
        print('engine', e)
    sc.view_settings.view_transform = 'Standard'
    try:
        sc.view_settings.look = 'None'
    except Exception:
        pass
    sc.render.film_transparent = False
    ee = sc.eevee
    for k, v in (('taa_render_samples', 32), ('use_shadows', True), ('use_raytracing', False)):
        if hasattr(ee, k):
            try:
                setattr(ee, k, v)
            except Exception:
                pass
    # world
    w = bpy.data.worlds.get('GymV83_World') or bpy.data.worlds.new('GymV83_World')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    lp = nt.nodes.new('ShaderNodeLightPath')
    bg1 = nt.nodes.new('ShaderNodeBackground')
    bg1.name = 'AMB'
    bg1.inputs[0].default_value = (0.75, 0.8, 1.0, 1)
    bg1.inputs[1].default_value = 0.1
    bg2 = nt.nodes.new('ShaderNodeBackground')
    bg2.name = 'CAMBG'
    bg2.inputs[0].default_value = H('#f3e3c4')
    mix = nt.nodes.new('ShaderNodeMixShader')
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])
    nt.links.new(bg1.outputs[0], mix.inputs[1])
    nt.links.new(bg2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    env = get_coll('GYM_Env')
    # sun
    sun = bpy.data.objects.get('GYM_Sun')
    if sun is None:
        ld = bpy.data.lights.new('GYM_Sun', 'SUN')
        sun = bpy.data.objects.new('GYM_Sun', ld)
        env.objects.link(sun)
    sun.data.energy = 3.4
    sun.data.angle = math.radians(1.0)
    sun.rotation_euler = Euler((math.radians(52), math.radians(8), math.radians(-32)), 'XYZ')
    cam = bpy.data.objects.get('GYM_Cam')
    if cam is None:
        cd = bpy.data.cameras.new('GYM_Cam')
        cam = bpy.data.objects.new('GYM_Cam', cd)
        env.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.clip_start = 0.1
    cam.data.clip_end = 500
    sc.camera = cam
    # ground disc (shadow catcher, melts into bg)
    gr = bpy.data.objects.get('GYM_Ground')
    if gr is None:
        bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=1.0)
        me = bpy.data.meshes.new('GYM_Ground')
        bm.to_mesh(me)
        bm.free()
        gr = bpy.data.objects.new('GYM_Ground', me)
        env.objects.link(gr)
        me.materials.append(ground_mat('#f3e3c4'))
    gr.scale = (60, 60, 1)
    # compositor glow
    sc.use_nodes = True
    ct = sc.node_tree
    for n in list(ct.nodes):
        ct.nodes.remove(n)
    rl = ct.nodes.new('CompositorNodeRLayers')
    rl.scene = sc
    gl = ct.nodes.new('CompositorNodeGlare')
    types = [i.identifier for i in gl.bl_rna.properties['glare_type'].enum_items]
    gl.glare_type = 'BLOOM' if 'BLOOM' in types else 'FOG_GLOW'
    gl.threshold = 1.3
    gl.mix = -0.35
    gl.quality = 'HIGH'
    try:
        gl.size = 7
    except Exception:
        pass
    co = ct.nodes.new('CompositorNodeComposite')
    ct.links.new(rl.outputs[0], gl.inputs[0])
    ct.links.new(gl.outputs[0], co.inputs[0])
    print('setup ok', sc.render.engine, gl.glare_type, types)
    return sc


def ground_mat(col):
    m, nt = _mat('GYM_GroundMat')
    N, L = nt.nodes.new, nt.links.new
    dif = N('ShaderNodeBsdfDiffuse')
    dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = N('ShaderNodeShaderToRGB')
    L(dif.outputs[0], s2r.inputs[0])
    ramp = N('ShaderNodeValToRGB')
    ramp.name = 'RAMP'
    cr = ramp.color_ramp
    cr.interpolation = 'CONSTANT'
    cr.elements[0].position = 0
    cr.elements[1].position = 0.35
    L(s2r.outputs[0], ramp.inputs[0])
    em = N('ShaderNodeEmission')
    L(ramp.outputs[0], em.inputs['Color'])
    o = N('ShaderNodeOutputMaterial')
    L(em.outputs[0], o.inputs['Surface'])
    set_bg_nodes(m, col)
    return m


def set_bg_nodes(m, col):
    c = H(col)
    ramp = next(n for n in m.node_tree.nodes if n.type == 'VALTORGB')
    ramp.color_ramp.elements[1].color = c
    ramp.color_ramp.elements[0].color = _mixc(tuple(x * 0.62 for x in c[:3]) + (1,), H('#40245c'), 0.18)


def set_bg(col):
    w = scene().world
    n = w.node_tree.nodes['CAMBG']
    n.inputs[0].default_value = H(col)
    set_bg_nodes(bpy.data.materials['GYM_GroundMat'], col)


# ---------------------------------------------------------------- render
def _all_objs(c):
    out = list(c.objects)
    for ch in c.children:
        out += _all_objs(ch)
    return out


def _vis(show, hide_sub=()):
    """show = list of top-level collection names to render (GYM_Env always)"""
    for c in scene().collection.children:
        on = c.name in show or c.name == 'GYM_Env'
        c.hide_render = not on
        c.hide_viewport = not on

        def rec(cc):
            for ch in cc.children:
                h = ch.name in hide_sub
                ch.hide_render = h
                ch.hide_viewport = h
                rec(ch)
        rec(c)


def bbox(names):
    bpy.context.view_layer.update()
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for nme in names:
        for o in _all_objs(bpy.data.collections[nme]):
            if o.type != 'MESH' or o.hide_render:
                continue
            for cnr in o.bound_box:
                p = o.matrix_world @ Vector(cnr)
                for i in range(3):
                    mn[i] = min(mn[i], p[i])
                    mx[i] = max(mx[i], p[i])
    return mn, mx


def render(path, show, direction=(1, -1.6, 0.9), res=(1024, 1024), bg='#f3e3c4', margin=1.12,
           frame=None, hide_sub=(), samples=32, ground=True, pct=100, override=None):
    """ortho render of collections `show` (frame = names used for framing, default show)"""
    sc = scene()
    _vis(show, hide_sub)
    set_bg(bg)
    mn, mx = bbox(frame or show)
    ctr = (mn + mx) / 2
    cam = bpy.data.objects['GYM_Cam']
    d = Vector(direction).normalized()
    cam.location = ctr + d * 120
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    for x in (mn.x, mx.x):
        for y in (mn.y, mx.y):
            for z in (mn.z, mx.z):
                p = inv @ Vector((x, y, z))
                xs.append(p.x)
                ys.append(p.y)
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    asp = res[0] / res[1]
    cam.data.ortho_scale = max(w, h * asp) * margin
    # recentre on projected bbox
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    cam.location += cam.matrix_world.to_3x3() @ Vector((cx, cy, 0))
    gr = bpy.data.objects['GYM_Ground']
    gr.hide_render = not ground
    gr.location = (ctr.x, ctr.y, mn.z - 0.002)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = pct
    sc.render.filepath = path
    sc.render.image_settings.file_format = 'PNG'
    if hasattr(sc.eevee, 'taa_render_samples'):
        sc.eevee.taa_render_samples = samples
    for vl in sc.view_layers:
        vl.material_override = override
    bpy.ops.render.render(write_still=True)
    for vl in sc.view_layers:
        vl.material_override = None
    return path


def stitch(paths, out, cols=None):
    """tile equally sized PNGs into one image (row by row)"""
    import numpy as np
    arrs = []
    for p in paths:
        im = bpy.data.images.load(p, check_existing=False)
        w, h = im.size
        a = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(a)
        arrs.append(a.reshape(h, w, 4))
        bpy.data.images.remove(im)
    cols = cols or len(arrs)
    rows = [np.concatenate(arrs[i:i + cols], axis=1) for i in range(0, len(arrs), cols)]
    full = np.concatenate(rows[::-1], axis=0)
    h, w = full.shape[:2]
    o = bpy.data.images.new('stitch_tmp', w, h, alpha=True)
    o.pixels.foreach_set(full.ravel())
    o.filepath_raw = out
    o.file_format = 'PNG'
    o.save()
    bpy.data.images.remove(o)
    return out


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
    b.inputs['Roughness'].default_value = 0.55
    if m.get('glow'):
        b.inputs['Emission Color'].default_value = col
        b.inputs['Emission Strength'].default_value = float(m.get('emit', 1.0))
    return p


def export_glb(name, path):
    """join main collection (no FX, no outline) into one mesh at root origin and export GLB"""
    sc = scene()
    c = bpy.data.collections[name]
    root = bpy.data.objects[name + '_root']
    bpy.context.view_layer.update()
    inv = root.matrix_world.inverted()
    tmp = []
    for o in c.objects:
        if o.type != 'MESH':
            continue
        me = o.data.copy()
        me.transform(o.matrix_basis)
        src = o.data.materials[0]
        me.materials.clear()
        me.materials.append(_pbr(src))
        for p in me.polygons:
            p.material_index = 0
        t = bpy.data.objects.new('tmp_' + o.name, me)
        sc.collection.objects.link(t)
        tmp.append(t)
    for scn in bpy.data.scenes:
        for vl in scn.view_layers:
            for o in vl.objects:
                o.select_set(False, view_layer=vl)
    for t in tmp:
        t.select_set(True)
    bpy.context.view_layer.objects.active = tmp[0]
    with bpy.context.temp_override(active_object=tmp[0], selected_editable_objects=tmp, selected_objects=tmp, object=tmp[0]):
        bpy.ops.object.join()
    j = tmp[0]
    j.name = path.replace('\\', '/').split('/')[-1].replace('.glb', '')
    j.data.name = j.name
    j.select_set(True)
    j.data.calc_loop_triangles()
    tris = len(j.data.loop_triangles)
    bpy.ops.export_scene.gltf(filepath=path, use_selection=True, use_active_scene=True, export_format='GLB', export_apply=False)
    me = j.data
    bpy.data.objects.remove(j, do_unlink=True)
    bpy.data.meshes.remove(me)
    return tris


def save():
    import os
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT + r"\gym_anime.blend")
