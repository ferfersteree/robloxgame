# SpearsV86 - lineup, mannequin, renders, videos, exports, json
import importlib, json, os, math
import bpy
from mathutils import Vector, Matrix, Euler
import spearlib as L

IDS = ['stick', 'bone', 'bronze', 'feather', 'iron', 'obsidian', 'crystal', 'fire', 'ice', 'star',
       'amber_sting', 'solar_trident', 'canyon_hook', 'condor_quill', 'mirage_lance', 'scorpion_sting', 'emerald_vine',
       'temple_guard', 'mangrove_root', 'hydra_fangs', 'storm_trident', 'thunder_split', 'coral_branch', 'tide_crest',
       'abyss_anchor', 'leviathan_fang', 'ash_saw', 'golem_heart', 'magma_tongue', 'phoenix_wing', 'amethyst_geode',
       'quartz_needle', 'lunar_crescent', 'aurora_weave', 'cloud_feather', 'sky_harpoon', 'rift_shards', 'void_scissors',
       'astral_armillary', 'singularity_spire', 'gear_pike', 'spore_halberd', 'bone_glaive', 'pearl_lance',
       'rift_conductor', 'primal_fang']


def name(n):
    return 'SP_%02d_%s' % (n, IDS[n - 1])


def mod(n):
    m = importlib.import_module('sp_%02d' % n)
    importlib.reload(m)
    return m


def build(n, remat=True):
    importlib.reload(L)
    m = mod(n)
    L.G.remat = remat
    s = m.build()
    L.G.remat = False
    L.snap_tip(name(n))
    return s


# ---------------------------------------------------------------- mannequin
def _mq_mat():
    return L.toon('mq_grey', '#b9bcc6', '#7d8090', '#e4e6ee', spec=0.2), L.toon('mq_blue', '#5b7bd1', '#384f96', '#93acef', spec=0.2)


def mannequin(coll, loc=(0, 0, 0), arm_fwd=18, tag='MQ'):
    """5-stud block figure; right hand (at +X side) ends near z=2.4. returns root empty"""
    grey, blue = _mq_mat()
    r = bpy.data.objects.new(tag + '_root', None)
    coll.objects.link(r)
    r.location = loc

    def blk(nm, size, p, mat, rot=(0, 0, 0)):
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.06, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
        me = bpy.data.meshes.new(tag + '_' + nm)
        bm.to_mesh(me)
        bm.free()
        for f in me.polygons:
            f.use_smooth = False
        o = bpy.data.objects.new(tag + '_' + nm, me)
        me.materials.append(mat)
        me.materials.append(L.outline_mat())
        md = o.modifiers.new('Outline', 'SOLIDIFY')
        md.thickness, md.offset, md.use_flip_normals, md.use_rim, md.material_offset = 0.04, 1.0, True, False, 1
        coll.objects.link(o)
        o.parent = r
        o.location = p
        o.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
        return o
    blk('leg_l', (0.9, 0.9, 2.0), (-0.48, 0, 1.0), blue)
    blk('leg_r', (0.9, 0.9, 2.0), (0.48, 0, 1.0), blue)
    blk('torso', (1.95, 0.95, 2.0), (0, 0, 3.0), grey)
    blk('head', (1.0, 1.0, 1.0), (0, 0, 4.5), grey)
    blk('arm_l', (0.9, 0.9, 2.0), (-1.45, 0, 3.0), grey)
    # right arm, rotated forward around the shoulder (pivot at z=4)
    a = math.radians(arm_fwd)
    c = Vector((1.45, 0, 4.0)) + Vector((0, -math.sin(a), -math.cos(a))) * 1.0
    blk('arm_r', (0.9, 0.9, 2.0), tuple(c), grey, rot=(-arm_fwd, 0, 0))
    hand = Vector((1.45, 0, 4.0)) + Vector((0, -math.sin(a), -math.cos(a))) * 1.75
    return r, hand


# ---------------------------------------------------------------- layout
def layout():
    st = L.get_coll('SPV_Stage')
    for o in list(st.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    mannequin(st, (-3.5, 0, 0), arm_fwd=0, tag='MQ_lineup')


def spear_copy(n, coll, at, with_idle=True, tag='copy'):
    """linked copy of spear n (model + idle FX) with its grip placed at `at`"""
    nm = name(n)
    r = bpy.data.objects.new('%s_%s' % (nm, tag), None)
    coll.objects.link(r)
    r.location = at
    srcs = [o for o in bpy.data.collections[nm].objects if o.type == 'MESH']
    if with_idle:
        srcs += [o for o in bpy.data.collections[nm + '_FX_Idle'].objects if o.type == 'MESH']
    for o in srcs:
        c = o.copy()
        c.animation_data_clear()
        coll.objects.link(c)
        c.parent = r
        c.matrix_parent_inverse = Matrix()
        c.location, c.rotation_euler, c.scale = o.location.copy(), o.rotation_euler.copy(), o.scale.copy()
    return r


def render_scale(levels=(1, 23, 46), path=None):
    sc = L.scene()
    col = bpy.data.collections.get('SPV_Scale')
    if col:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    col = L.get_coll('SPV_Scale')
    for i, n in enumerate(levels):
        x0 = -60 + i * 6.5
        r, hand = mannequin(col, (x0, -80, 0), arm_fwd=38, tag='MQ_%02d' % n)
        g = Vector((x0, -80, 0)) + hand + Vector((0, 0, 0.0))
        g.z = L.GRIP
        spear_copy(n, col, (g.x, g.y, g.z), True, 'scale')
    L._vis(['SPV_Scale'])
    sc.frame_set(1)
    mn, mx = L.bbox_objs(col.objects)
    L.set_bg('#e8e1f0', '#c9c0d8')
    L.ground(True, 0.0, ((mn.x + mx.x) / 2, -80))
    path = path or L.OUT + r"\scale.png"
    res = (2400, 1350)
    L.frame_box(mn, mx, (0.35, -1.0, 0.22), res, 1.12)
    L._out(sc, path, res, 100, 32)
    L._warm(sc)
    bpy.ops.render.render(write_still=True)
    return path


# ---------------------------------------------------------------- per-spear outputs
def grab(mp4, frames, out_prefix):
    """decode frames of a video to PNG through a temporary compositor scene (removed afterwards)"""
    img = bpy.data.images.load(mp4, check_existing=False)
    img.source = 'MOVIE'
    sc = bpy.data.scenes.new('SpearsV86_vidcheck')
    sc.view_settings.view_transform = 'Standard'
    sc.use_nodes = True
    nt = sc.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    im = nt.nodes.new('CompositorNodeImage')
    im.image = img
    im.frame_duration = img.frame_duration
    im.frame_start = 1
    co = nt.nodes.new('CompositorNodeComposite')
    nt.links.new(im.outputs[0], co.inputs[0])
    sc.render.resolution_x, sc.render.resolution_y = img.size[0], img.size[1]
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    outs = []
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = out_prefix + '_%03d.png' % f
        with bpy.context.temp_override(scene=sc):
            bpy.ops.render.render(write_still=True, scene=sc.name)
        outs.append(sc.render.filepath)
    bpy.data.scenes.remove(sc)
    bpy.data.images.remove(img)
    return outs


def _busy(png):
    """fraction of pixels that differ clearly from the corner colour (0 = empty frame)"""
    import numpy as np
    im = bpy.data.images.load(png, check_existing=False)
    w, h = im.size
    a = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    a = a.reshape(h, w, 4)[::4, ::4, :3]
    ref = a[2, 2]
    return float((np.abs(a - ref).sum(axis=2) > 0.12).mean())


def check_video(mp4, frames, tag):
    outs = grab(mp4, frames, os.path.join(L.OUT, 'scripts', '_chk_' + tag))
    return [round(_busy(p), 4) for p in outs]


def outputs(n, pct=100, still=True, video=True, samples_v=16):
    m = mod(n)
    nm = name(n)
    base = 'sp_%02d_%s' % (n, IDS[n - 1])
    res = {}
    if still:
        res['render'] = L.render_model(nm, L.OUT + r"\renders\%s.png" % base, m.BG, pct=pct)
    if video:
        for kind in ('flight', 'impact'):
            p = L.OUT + r"\anim\%s_%s.mp4" % (base, kind)
            for attempt in range(3):
                if kind == 'flight':
                    L.render_flight(nm, p, getattr(m, 'SKY', m.BG), pct=pct, samples=samples_v)
                    fr = (1, 30)
                else:
                    L.render_impact(nm, p, m.BG, m.GROUND, pct=pct, samples=samples_v)
                    fr = (5, 15, 40)
                b = check_video(p, fr, '%s_%s' % (base, kind))
                if min(b) > 0.01:
                    break
            else:
                raise RuntimeError('%s: video still empty after 3 attempts %s' % (p, b))
            res[kind] = (p, b, attempt)
    return res


FX_EXPORT = {    # n -> {suffix: FX object name (without the SPnn_ prefix)}
    1: {'air_ring': 'fl_ring_0', 'crater': 'im_crater', 'clod': 'im_clod_0', 'shock_ring': 'im_shock'},
    23: {'coral_crystal': 'im_crys_0', 'ripple_ring': 'im_ripple_0', 'shard': 'fl_shard_0', 'sand_mound': 'im_sandmound'},
    46: {'flame': 'im_pillar_0', 'fire_ring': 'fl_ring_0', 'lava_ring': 'im_lava_ring', 'molten_rock': 'im_molten_0',
         'flame_tongue': 'fl_flame_0'},
}


def export(n):
    nm = name(n)
    base = 'sp_%02d_%s' % (n, IDS[n - 1])
    os.makedirs(L.EXP, exist_ok=True)
    out = {}
    objs = [o for o in bpy.data.collections[nm].objects if o.type == 'MESH']
    out[base + '.glb'] = L.export_objs(objs, os.path.join(L.EXP, base + '.glb'))
    pre = nm.split('_')[0] + nm.split('_')[1] + '_'
    for suf, names in (FX_EXPORT.get(n) or getattr(mod(n), 'FX_EXPORT', {})).items():
        # one representative mesh per FX kind, exported at its own origin, scale 1
        src = bpy.data.objects.get(pre + names)
        if not src:
            continue
        me = src.data
        tmp = bpy.data.objects.new('fxtmp', me)
        L.scene().collection.objects.link(tmp)
        out[base + '_fx_' + suf + '.glb'] = L.export_objs([tmp], os.path.join(L.EXP, base + '_fx_' + suf + '.glb'))
        bpy.data.objects.remove(tmp, do_unlink=True)
    return out


def spear_info(n, tris_glb=None):
    nm = name(n)
    s = L.stats(nm)
    tip = bpy.data.objects[nm + '_Tip']
    tr = bpy.data.objects[nm + '_TrailRoot']
    tz, rz = tip.location.z + L.GRIP, tr.location.z + L.GRIP
    return dict(
        n=n, id=IDS[n - 1], collection=nm, glb='sp_%02d_%s.glb' % (n, IDS[n - 1]),
        tail_space={'Grip': [0, round(L.GRIP, 3), 0], 'Tip': [round(tip.location.x, 3), round(tz, 3), round(-tip.location.y, 3)],
                    'TrailRoot': [0, round(rz, 3), 0],
                    'note': 'Roblox/GLB axes (Y up), tail at 0 - same frame as SpearFactoryV15 grip={0,2.5,0}'},
        glb_origin_space={'Grip': [0, 0, 0], 'Tip': [round(tip.location.x, 3), round(tz - L.GRIP, 3), round(-tip.location.y, 3)],
                          'TrailRoot': [0, round(rz - L.GRIP, 3), 0],
                          'note': 'relative to the GLB origin (= grip)'},
        length=round(s['top_z'] - s['tail_z'], 3), bbox=s['size'], elements=s['elements'], tris=s['tris'], glb_tris=tris_glb,
        grip_check=L.grip_check(nm))


def write_json(levels, glb_tris=None):
    p = L.OUT + r"\spears.json"
    data = {}
    if os.path.exists(p):
        try:
            data = {d['id']: d for d in json.load(open(p, encoding='utf-8'))['spears']}
        except Exception:
            data = {}
    for n in levels:
        data[IDS[n - 1]] = spear_info(n, (glb_tris or {}).get(n))
    arr = sorted(data.values(), key=lambda d: d['n'])
    json.dump({'units': '1 Blender unit = 1 stud', 'spears': arr}, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return p
