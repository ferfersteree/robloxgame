# SpearHunt Spears V86 - helper library: toon spears + animated FX in Blender 4.2 (EEVEE Next)
# Coordinates: build in "tail space" (tail at z=0, tip ~9). Root empty = grip (z=2.5); children are stored
# relative to it, so the GLB origin is the grip. FX: <NAME>_FX_Idle / _FX_Flight / _FX_Impact.
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, Euler, noise

SCN = 'SpearsV86'
OUT = r"C:\Users\nikit\OneDrive\Рабочий стол\Роблокс\robloxgame\docs\concepts_v86"
EXP = r"C:\SpearHuntAssets\spears"
GRIP = 2.5
FPS = 30
FLIGHT = (1, 30)      # loop frames (31 == 1)
IMPACT0 = 101         # impact animation starts here
TILT = 35.0           # spear angle above the ground at impact (degrees)


class G:
    name = ''
    coll = None
    fxc = {}
    root = None
    rig = None        # impact rig empty (ground contact point)
    mode = None       # None | 'idle' | 'flight' | 'impact'
    ol = 0.03
    remat = False
    X = 0.0


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


def _blend(m):
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass
    try:
        m.blend_method = 'BLEND'
    except Exception:
        pass


def outline_mat(name='SPV_Outline', col='#1c1016'):
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


def _cached(key):
    if key in _MC and _MC[key].name in bpy.data.materials:
        return _MC[key]
    if not G.remat and key in bpy.data.materials:
        _MC[key] = bpy.data.materials[key]
        return _MC[key]
    return None


def toon(name, base, shade=None, light=None, spec=0.7, rim=0.45, emit=0.0, rimcol='#ffffff'):
    """3-tone toon material (object colour alpha fades it out)."""
    key = 'T_' + name
    c = _cached(key)
    if c:
        return c
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
    lw = N('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.32
    rm = N('ShaderNodeMath')
    rm.operation = 'GREATER_THAN'
    rm.inputs[1].default_value = 0.6
    L(lw.outputs['Facing'], rm.inputs[0])
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


def glow(name, col, strength=3.0):
    """emissive; object colour alpha = fade (keyframe ob.color[3])"""
    key = 'G_' + name
    c = _cached(key)
    if c:
        return c
    m, nt = _mat(key)
    N, L = nt.nodes.new, nt.links.new
    oi = N('ShaderNodeObjectInfo')
    e = N('ShaderNodeEmission')
    e.inputs['Color'].default_value = H(col)
    e.inputs['Strength'].default_value = strength
    tr = N('ShaderNodeBsdfTransparent')
    mix = N('ShaderNodeMixShader')
    L(oi.outputs['Alpha'], mix.inputs[0])
    L(tr.outputs[0], mix.inputs[1])
    L(e.outputs[0], mix.inputs[2])
    o = N('ShaderNodeOutputMaterial')
    L(mix.outputs[0], o.inputs['Surface'])
    m['base'] = list(H(col))
    m['emit'] = float(strength)
    m['glow'] = 1
    _MC[key] = m
    return m


def ghost(name, col, strength=2.0, alpha=0.5, power=1.6, edge=False):
    """soft transparent emissive blob (aura / smoke). edge=True -> bubble (bright rim). object alpha fades it."""
    key = 'A_' + name
    c = _cached(key)
    if c:
        return c
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
    oi = N('ShaderNodeObjectInfo')
    ma = N('ShaderNodeMath')
    ma.operation = 'MULTIPLY'
    L(ml.outputs[0], ma.inputs[0])
    L(oi.outputs['Alpha'], ma.inputs[1])
    tr = N('ShaderNodeBsdfTransparent')
    e = N('ShaderNodeEmission')
    e.inputs['Color'].default_value = H(col)
    e.inputs['Strength'].default_value = strength
    mix = N('ShaderNodeMixShader')
    L(ma.outputs[0], mix.inputs[0])
    L(tr.outputs[0], mix.inputs[1])
    L(e.outputs[0], mix.inputs[2])
    o = N('ShaderNodeOutputMaterial')
    L(mix.outputs[0], o.inputs['Surface'])
    _blend(m)
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
        if o.animation_data and o.animation_data.action:
            a = o.animation_data.action
            o.animation_data.action = None
            if a.users == 0:
                bpy.data.actions.remove(a)
        bpy.data.objects.remove(o, do_unlink=True)
        if d and d.users == 0 and isinstance(d, bpy.types.Mesh):
            bpy.data.meshes.remove(d)


def lineup_x(n):
    return (n - 1) * 3.0


def begin(name, n, ol=0.03):
    """start (or rebuild) spear `name` (e.g. SP_01_stick), number n"""
    c = get_coll(name)
    fxc = {k: get_coll('%s_FX_%s' % (name, k.capitalize()), c) for k in ('idle', 'flight', 'impact')}
    _clear(c)
    for f in fxc.values():
        _clear(f)
    G.X = lineup_x(n)
    r = bpy.data.objects.new(name + '_root', None)
    r.empty_display_size = 0.4
    c.objects.link(r)
    r.location = (G.X, 0, GRIP)
    rig = bpy.data.objects.new(name + '_ImpactRig', None)
    rig.empty_display_type = 'SPHERE'
    rig.empty_display_size = 0.3
    fxc['impact'].objects.link(rig)
    rig.location = (G.X, -40, 0)
    G.name, G.coll, G.fxc, G.root, G.rig, G.mode, G.ol = name, c, fxc, r, rig, None, ol
    return r


def fx(mode=None):
    """None = main model, 'idle' / 'flight' (spear space) , 'impact' (rig space: ground point at 0, z up)"""
    G.mode = mode


def marker(name, z):
    e = bpy.data.objects.new('%s_%s' % (G.name, name), None)
    e.empty_display_type = 'SINGLE_ARROW' if name == 'Tip' else 'PLAIN_AXES'
    e.empty_display_size = 0.35
    G.coll.objects.link(e)
    e.parent = G.root
    e.location = (0, 0, z - GRIP)
    e['tail_space_z'] = z
    return e


# ---------------------------------------------------------------- object creation
def _finish(name, bm, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, ol='def', smooth=True, sharp=38, parent=None):
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
    full = '%s_%s' % (G.name.split('_')[0] + G.name.split('_')[1], name)   # SP01_<name>
    me = bpy.data.meshes.new(full)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(full, me)
    me.materials.append(mat)
    loc = Vector(loc)
    if G.mode in (None, 'idle', 'flight'):
        loc.z -= GRIP                  # tail space -> grip space
        par = G.root
    else:
        par = G.rig
    ob.location = loc
    ob.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
    if G.mode:
        G.fxc[G.mode].objects.link(ob)
        ob.visible_shadow = False
    else:
        G.coll.objects.link(ob)
    t = G.ol if ol == 'def' else ol
    if (mat.get('glow') or mat.get('ghost')):
        ob.visible_shadow = False
        if ol == 'def':
            t = 0
    if G.mode and ol == 'def' and not mat.get('glow') and not mat.get('ghost'):
        t = G.ol * 0.8
    if t:
        me.materials.append(outline_mat())
        md = ob.modifiers.new('Outline', 'SOLIDIFY')
        md.thickness = t
        md.offset = 1.0
        md.use_flip_normals = True
        md.use_rim = False
        md.material_offset = 1
        md.use_quality_normals = True
    ob.parent = parent or par
    return ob


def _P(axis, a, u, v):
    if axis == 'X':
        return (a, u, v)
    if axis == 'Y':
        return (v, a, u)
    return (u, v, a)


def lathe(name, prof, mat, segs=16, axis='Z', caps=True, **kw):
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


def cyl(name, r, length, mat, segs=16, bev=0.03, axis='Z', **kw):
    h = length / 2
    b = min(bev, r * 0.45, h * 0.45)
    return lathe(name, [(-h, 0), (-h, r - b), (-h + b, r), (h - b, r), (h, r - b), (h, 0)], mat, segs, axis, **kw)


def rod(name, r, z0, z1, mat, segs=12, bev=0.02, r1=None, **kw):
    """vertical shaft piece from z0 to z1 (tail space), optional taper to r1"""
    r1 = r if r1 is None else r1
    b = min(bev, r * 0.4, (z1 - z0) * 0.3)
    prof = [(z0, 0), (z0, r - b), (z0 + b, r), (z1 - b, r1), (z1, r1 - b), (z1, 0)]
    return lathe(name, prof, mat, segs, 'Z', **kw)


def sphere(name, r, mat, segs=14, rings=8, axis='Z', **kw):
    prof = [(-r * math.cos(math.pi * i / rings), r * math.sin(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe(name, prof, mat, segs, axis, **kw)


def cone(name, r, h, mat, segs=10, axis='Z', r2=0.0, **kw):
    return lathe(name, [(0, 0), (0, r), (h, r2)] + ([(h, 0)] if r2 > 0 else []), mat, segs, axis, **kw)


def torus(name, R, r, mat, segs=20, rsegs=8, axis='Z', **kw):
    prof = [(r * math.cos(2 * math.pi * i / rsegs), R + r * math.sin(2 * math.pi * i / rsegs)) for i in range(rsegs + 1)]
    return lathe(name, prof, mat, segs, axis, caps=False, **kw)


def box(name, size, mat, bev=0.04, bsegs=2, **kw):
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

    def ring(z, rad):
        return [bm.verts.new((rad * math.cos(2 * math.pi * j / sides), rad * math.sin(2 * math.pi * j / sides), z)) for j in range(sides)]
    zt = h * (1 - tip)
    if both:
        A = ring(h * tip, r)
        bot = bm.verts.new((0, 0, 0))
    else:
        A = ring(0.0, r * base)
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


def blade(name, outline2d, th, mat, edge=0.35, **kw):
    """flat-ish blade from a closed 2D outline in the XZ plane [(x, z), ...] (counter-clockwise).
    th = half thickness at the centre ridge; edges taper to `edge`*th. Centre ridge along the centroid."""
    bm = bmesh.new()
    pts = [Vector((p[0], 0, p[1])) for p in outline2d]
    c = sum(pts, Vector()) / len(pts)
    # inner ring (bevel of the cutting edge) at 55% towards centre-line
    inner = [c.lerp(p, 0.55) for p in pts]
    inner = [Vector((p.x * 1.0, 0, p.z)) for p in inner]
    O = [bm.verts.new((p.x, 0, p.z)) for p in pts]
    IF = [bm.verts.new((p.x, th, p.z)) for p in inner]
    IB = [bm.verts.new((p.x, -th, p.z)) for p in inner]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((O[i], O[j], IF[j], IF[i]))
        bm.faces.new((O[j], O[i], IB[i], IB[j]))
    bm.faces.new(IF)
    bm.faces.new(IB[::-1])
    kw.setdefault('sharp', 30)
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


def coil(name, R, r, z0, z1, turns, mat, segs=6, steps=9, R1=None, phase=0.0, **kw):
    """helix around the Z axis from z0 to z1 (wraps, bindings)"""
    n = max(4, int(turns * steps))
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * turns * t + phase
        rr = R if R1 is None else R + (R1 - R) * t
        pts.append((rr * math.cos(ang), rr * math.sin(ang), z0 + (z1 - z0) * t))
    return tube(name, pts, r, mat, segs, **kw)


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
        prof.append((h * t, max(rr, r * 0.12)))   # keep every inner ring open so the flame reaches full height
    prof[0] = (0, 0)
    prof[-1] = (h, 0)
    ob = lathe(name, prof, mat, segs, 'Z', **kw)
    for v in ob.data.vertices:
        v.co.x += bend * (v.co.z / max(h, 1e-5)) ** 2 * h
    return ob


def zigzag(a, b, n, amp, seed=0):
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


# ---------------------------------------------------------------- animation
def key(ob, f, loc=None, rot=None, scale=None, alpha=None, interp=None):
    """keyframe object at frame f. loc in parent space (tail space z for idle/flight objects is NOT converted)."""
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


def tidy(ob, kind, cyclic=False, interp=None):
    """name the object's action <spear>_<kind>_<obj>; optional cycles modifier"""
    ad = ob.animation_data
    if not ad or not ad.action:
        return
    nm = ob.name[len(G.name) + 1:] if ob.name.startswith(G.name) else ob.name.split('_', 1)[1]
    ad.action.name = '%s_%s_%s' % (G.name, kind, nm)
    for fc in ad.action.fcurves:
        if interp:
            for kp in fc.keyframe_points:
                kp.interpolation = interp
        if cyclic and not any(m.type == 'CYCLES' for m in fc.modifiers):
            fc.modifiers.new('CYCLES')


def zp(z):
    """tail-space z -> grip-space z (for keyframes on idle/flight objects)"""
    return z - GRIP


def stream(objs, path, period=30, f0=1, smax=1.0, spin=None, kind='flight'):
    """loop each obj along path(t, i)->(x,y,z tail space) for t 0..1 over `period` frames, staggered.
    scale 0 -> smax -> 0, seamless (cycles modifier)."""
    n = len(objs)
    for i, ob in enumerate(objs):
        ph = period * i / n
        K = 6
        for k in range(K + 1):
            t = k / K
            p = Vector(path(t, i))
            p.z -= GRIP
            if callable(smax):
                s = smax(t, i) if 0 < k < K else 0.0
            else:
                s = smax * math.sin(math.pi * t) ** 0.6 if 0 < k < K else 0.0
            r = spin(t, i) if spin else None
            key(ob, f0 + ph + t * period, loc=p, scale=s, rot=r)
        tidy(ob, kind, cyclic=True, interp='LINEAR')


def ease_keys(ob):
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.easing = 'EASE_OUT'


# ---------------------------------------------------------------- impact: spear copy that sticks in
def impact_spear(tip_z, depth=0.55, fly=6.0, wobble=7.0, f_hit=None, approach=4):
    """linked copy of the main model under the impact rig: flies in along its axis and sticks into the ground
    at TILT degrees above the horizon, tip `depth` under the ground, then wobbles. returns (pivot, dir)"""
    f_hit = f_hit or IMPACT0 + approach
    t = math.radians(TILT)
    d = Vector((math.cos(t), 0, -math.sin(t)))          # spear forward (tip direction) in rig space
    piv = bpy.data.objects.new(G.name + '_ImpactSpear', None)
    piv.empty_display_size = 0.25
    G.fxc['impact'].objects.link(piv)
    piv.parent = G.rig
    off = bpy.data.objects.new(G.name + '_ImpactSpearOff', None)
    off.empty_display_size = 0.1
    G.fxc['impact'].objects.link(off)
    off.parent = piv
    off.location = (0, 0, -(tip_z - GRIP))
    for o in G.coll.objects:
        if o.type != 'MESH':
            continue
        c = o.copy()
        c.animation_data_clear()
        G.fxc['impact'].objects.link(c)
        c.parent = off
        c.matrix_parent_inverse = Matrix()
        c.location, c.rotation_euler, c.scale = o.location.copy(), o.rotation_euler.copy(), o.scale.copy()
    rot = Vector((0, 0, 1)).rotation_difference(d).to_euler('XYZ')
    R = [math.degrees(a) for a in rot]
    end = d * depth
    key(piv, IMPACT0, loc=end - d * fly, rot=R, interp='LINEAR')
    key(piv, f_hit, loc=end, rot=R)
    # wobble around the rig Y axis (in the spear's plane)
    amps = [wobble, -wobble * 0.6, wobble * 0.35, -wobble * 0.15, 0]
    for i, a in enumerate(amps):
        key(piv, f_hit + 3 + i * 3, rot=(R[0], R[1] + a, R[2]))
    for fc in piv.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            if kp.co.x < f_hit - 0.5:
                kp.interpolation = 'LINEAR'
    tidy(piv, 'impact')
    return piv, d


def snap_tip(name):
    """move the Tip marker onto the highest vertex of the main model (grip space)"""
    best = None
    for o in bpy.data.collections[name].objects:
        if o.type != 'MESH':
            continue
        for v in o.data.vertices:
            p = o.matrix_basis @ v.co
            if best is None or p.z > best.z:
                best = p
    tip = bpy.data.objects[name + '_Tip']
    tip.location = best
    tip['tail_space_z'] = best.z + GRIP
    return best


# ---------------------------------------------------------------- stats
def stats(name):
    c = bpy.data.collections[name]
    objs = [o for o in c.objects if o.type == 'MESH']
    tris = 0
    for o in objs:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
    nfx = {k: len([o for o in bpy.data.collections['%s_FX_%s' % (name, k)].objects if o.type == 'MESH'])
           for k in ('Idle', 'Flight', 'Impact')}
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for v in o.data.vertices:
            p = o.matrix_basis @ v.co
            for i in range(3):
                mn[i] = min(mn[i], p[i])
                mx[i] = max(mx[i], p[i])
    mats = set()
    for o in objs:
        if o.data.materials:
            mats.add(o.data.materials[0].name)
    return dict(name=name, elements=len(objs), tris=tris, fx=nfx, materials=len(mats),
                size=[round(mx[i] - mn[i], 2) for i in range(3)],
                tail_z=round(mn.z + GRIP, 3), top_z=round(mx.z + GRIP, 3))


def grip_check(name, z0=2.0, z1=3.0, rmax=0.175):
    """everything with vertices in tail-space z0..z1: max radius from the axis and which objects are there"""
    c = bpy.data.collections[name]
    worst, who, objs = 0.0, None, set()
    for o in c.objects:
        if o.type != 'MESH':
            continue
        V = [o.matrix_basis @ v.co for v in o.data.vertices]
        for e in o.data.edges:
            a, b = V[e.vertices[0]], V[e.vertices[1]]
            for k in range(11):
                p = a.lerp(b, k / 10)
                z = p.z + GRIP
                if z0 <= z <= z1:
                    objs.add(o.name)
                    d = math.hypot(p.x, p.y)
                    if d > worst:
                        worst, who = d, o.name
    return dict(max_radius=round(worst, 3), by=who, objects=sorted(objs), ok=worst <= rmax + 1e-4)


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
    sc.render.fps = FPS
    sc.render.fps_base = 1.0
    sc.frame_start, sc.frame_end = 1, 150
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
    w = bpy.data.worlds.get('SpearsV86_World') or bpy.data.worlds.new('SpearsV86_World')
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
    bg2.inputs[0].default_value = H('#cfe7d0')
    mix = nt.nodes.new('ShaderNodeMixShader')
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])
    nt.links.new(bg1.outputs[0], mix.inputs[1])
    nt.links.new(bg2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    env = get_coll('SPV_Env')
    sun = bpy.data.objects.get('SPV_Sun')
    if sun is None:
        ld = bpy.data.lights.new('SPV_Sun', 'SUN')
        sun = bpy.data.objects.new('SPV_Sun', ld)
        env.objects.link(sun)
    sun.data.energy = 3.4
    sun.data.angle = math.radians(1.0)
    sun.rotation_euler = Euler((math.radians(48), math.radians(10), math.radians(-35)), 'XYZ')
    cam = bpy.data.objects.get('SPV_Cam')
    if cam is None:
        cd = bpy.data.cameras.new('SPV_Cam')
        cam = bpy.data.objects.new('SPV_Cam', cd)
        env.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.clip_start = 0.1
    cam.data.clip_end = 600
    sc.camera = cam
    gr = bpy.data.objects.get('SPV_Ground')
    if gr is None:
        bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=1.0)
        me = bpy.data.meshes.new('SPV_Ground')
        bm.to_mesh(me)
        bm.free()
        gr = bpy.data.objects.new('SPV_Ground', me)
        env.objects.link(gr)
        me.materials.append(ground_mat('#cfe7d0'))
    gr.scale = (80, 80, 1)
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
    print('setup ok', sc.render.engine, gl.glare_type)
    return sc


def ground_mat(col):
    m, nt = _mat('SPV_GroundMat')
    N, L = nt.nodes.new, nt.links.new
    dif = N('ShaderNodeBsdfDiffuse')
    dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = N('ShaderNodeShaderToRGB')
    L(dif.outputs[0], s2r.inputs[0])
    ramp = N('ShaderNodeValToRGB')
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


def set_bg(col, ground_col=None):
    w = scene().world
    n = next(x for x in w.node_tree.nodes if x.type == 'BACKGROUND' and x.name == 'CAMBG')
    n.inputs[0].default_value = H(col)
    set_bg_nodes(bpy.data.materials['SPV_GroundMat'], ground_col or col)


# ---------------------------------------------------------------- visibility / render
def _all_objs(c):
    out = list(c.objects)
    for ch in c.children:
        out += _all_objs(ch)
    return out


def _vis(show, hide_sub=()):
    """show = top-level collection names to render (SPV_Env always); hide_sub = child collections to hide.
    Collections stay enabled; visibility is set per object (collection toggles reach animation renders late)."""
    def rec(cc, on):
        if cc.hide_render or cc.hide_viewport:
            cc.hide_render = False
            cc.hide_viewport = False
        for o in cc.objects:
            if o.name == 'SPV_Ground':
                continue
            o.hide_render = not on
            o.hide_viewport = not on
        for ch in cc.children:
            rec(ch, on and ch.name not in hide_sub)
    for c in scene().collection.children:
        rec(c, c.name in show or c.name == 'SPV_Env')


def _main_vis(name, on):
    for o in bpy.data.collections[name].objects:
        o.hide_render = not on
        o.hide_viewport = not on


def bbox_objs(objs):
    bpy.context.view_layer.update()
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != 'MESH':
            continue
        for cnr in o.bound_box:
            p = o.matrix_world @ Vector(cnr)
            for i in range(3):
                mn[i] = min(mn[i], p[i])
                mx[i] = max(mx[i], p[i])
    return mn, mx


def cam_look(direction, up=(0, 0, 1)):
    """camera rotation looking along -direction (direction = from target towards the eye) with given up"""
    cam = bpy.data.objects['SPV_Cam']
    f = -Vector(direction).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f).normalized()
    M = Matrix((r, u, -f)).transposed()
    cam.rotation_euler = M.to_euler()
    return cam


def frame_box(mn, mx, direction, res, margin=1.1, up=(0, 0, 1)):
    cam = cam_look(direction, up)
    ctr = (mn + mx) / 2
    d = Vector(direction).normalized()
    cam.location = ctr + d * 150
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
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    cam.location += cam.matrix_world.to_3x3() @ Vector((cx, cy, 0))
    return cam


def _out(sc, path, res, pct, samples, movie=False):
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = pct
    sc.render.filepath = path
    if hasattr(sc.eevee, 'taa_render_samples'):
        sc.eevee.taa_render_samples = samples
    ims = sc.render.image_settings
    if movie:
        fmts = [i.identifier for i in ims.bl_rna.properties['file_format'].enum_items]
        ims.file_format = 'FFMPEG' if 'FFMPEG' in fmts else fmts[0]
        ff = sc.render.ffmpeg
        cons = [i.identifier for i in ff.bl_rna.properties['format'].enum_items]
        ff.format = 'MPEG4' if 'MPEG4' in cons else cons[0]
        cods = [i.identifier for i in ff.bl_rna.properties['codec'].enum_items]
        ff.codec = 'H264' if 'H264' in cods else cods[0]
        try:
            ff.constant_rate_factor = 'HIGH'
        except Exception:
            pass
        try:
            ff.audio_codec = 'NONE'
        except Exception:
            pass
    else:
        ims.file_format = 'PNG'
        ims.color_mode = 'RGB'


def _warm(sc):
    # tiny throwaway render: the first render after visibility changes comes out empty otherwise
    bpy.context.view_layer.update()
    keep = (sc.render.resolution_percentage, sc.render.filepath)
    sc.render.resolution_percentage = 5
    bpy.ops.render.render(write_still=False)
    sc.render.resolution_percentage, sc.render.filepath = keep


def ground(on, z=0.0, at=(0, 0)):
    gr = bpy.data.objects['SPV_Ground']
    gr.hide_render = not on
    gr.hide_viewport = not on
    gr.location = (at[0], at[1], z - 0.002)


def render_model(name, path, bg, res=(1024, 1024), pct=100, samples=32, pose=(0, -24, 0), direction=(1, -1.5, 0.75)):
    """3/4 render of the model + FX_Idle; the root is temporarily tilted so the head reads in a square frame"""
    sc = scene()
    _vis([name], hide_sub=(name + '_FX_Flight', name + '_FX_Impact'))
    _main_vis(name, True)
    root = bpy.data.objects[name + '_root']
    keep = root.rotation_euler.copy()
    root.rotation_euler = Euler([math.radians(a) for a in pose], 'XYZ')
    sc.frame_set(1)
    objs = [o for o in bpy.data.collections[name].objects] + list(bpy.data.collections[name + '_FX_Idle'].objects)
    mn, mx = bbox_objs(objs)
    set_bg(bg)
    ground(False)
    frame_box(mn, mx, direction, res, 1.08)
    _out(sc, path, res, pct, samples)
    _warm(sc)
    bpy.ops.render.render(write_still=True)
    root.rotation_euler = keep
    return path


def render_flight(name, path, bg, res=(1280, 720), pct=100, samples=12, frames=(1, 60), box=None, still=None):
    """side view, spear horizontal (tip to the right), loop rendered twice (1-60)"""
    sc = scene()
    _vis([name], hide_sub=(name + '_FX_Idle', name + '_FX_Impact'))
    _main_vis(name, True)
    root = bpy.data.objects[name + '_root']
    R = root.matrix_world.translation
    mn = Vector((R.x - 0.8, -0.8, -3.8))
    mx = Vector((R.x + 0.8, 0.8, 9.9))
    if box:
        mn, mx = Vector(box[0]) + Vector((R.x, 0, 0)), Vector(box[1]) + Vector((R.x, 0, 0))
    set_bg(bg)
    ground(False)
    frame_box(mn, mx, (0.0, -1.0, 0.42), res, 1.04, up=(-1, 0, 0))
    _out(sc, path, res, pct, samples, movie=still is None)
    if still is None:
        sc.frame_start, sc.frame_end = frames
    sc.frame_set(still if still is not None else frames[0])
    _warm(sc)
    if still is not None:
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
    return path


def render_impact(name, path, bg, ground_col, res=(1280, 720), pct=100, samples=12, frames=None, half=(8.2, 5.9),
                  still=None, direction=(0.3, -1.0, 0.38)):
    sc = scene()
    _vis([name], hide_sub=(name + '_FX_Idle', name + '_FX_Flight'))
    _main_vis(name, False)
    rig = bpy.data.objects[name + '_ImpactRig']
    P = rig.matrix_world.translation
    mn = Vector((P.x - half[0], P.y - 2.0, P.z - 0.3))
    mx = Vector((P.x + half[0] * 0.55, P.y + 2.0, P.z + half[1]))
    set_bg(bg, ground_col)
    ground(True, P.z, (P.x, P.y))
    frame_box(mn, mx, direction, res, 1.0)
    _out(sc, path, res, pct, samples, movie=still is None)
    frames = frames or (IMPACT0, IMPACT0 + 44)
    if still is None:
        sc.frame_start, sc.frame_end = frames
    sc.frame_set(still if still is not None else frames[0])
    _warm(sc)
    if still is not None:
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
    _main_vis(name, True)
    return path


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
    if m.get('glow') or m.get('emit', 0) > 0.3:
        b.inputs['Emission Color'].default_value = col
        b.inputs['Emission Strength'].default_value = float(max(1.0, m.get('emit', 1.0)))
    return p


def export_objs(objs, path, origin=None):
    """join copies of the given mesh objects (no outline modifier, PBR mats) into one mesh, export one-node GLB.
    origin: matrix to make the GLB origin (default: object's parent space)"""
    sc = scene()
    bpy.context.view_layer.update()
    tmp = []
    for o in objs:
        if o.type != 'MESH':
            continue
        me = o.data.copy()
        M = o.matrix_basis if origin is None else origin.inverted() @ o.matrix_world
        me.transform(M)
        if M.determinant() < 0:
            me.flip_normals()
        mats = [_pbr(m) for m in me.materials if m and not m.get('outline')]
        me.materials.clear()
        for m in mats:
            me.materials.append(m)
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
    j.name = os.path.basename(path).replace('.glb', '')
    j.data.name = j.name
    j.select_set(True)
    j.data.calc_loop_triangles()
    tris = len(j.data.loop_triangles)
    bpy.ops.export_scene.gltf(filepath=path, use_selection=True, use_active_scene=True, export_format='GLB',
                              export_apply=False, export_animations=False, export_yup=True)
    me = j.data
    bpy.data.objects.remove(j, do_unlink=True)
    bpy.data.meshes.remove(me)
    return tris


def save():
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT + r"\spears_anime.blend")
