# Contact sheet: one small 3/4 render per animal (rest pose), for spotting look-alikes across biomes.
import bpy, os, math, json
from mathutils import Vector
import faunalib as L
import biome as Bm

OUTDIR = os.path.join(os.environ.get('TEMP', L.OUT), 'v87_contact')


def tile(nn, aid, size=320, view=(0.9, -1.0, 0.45)):
    sc = bpy.data.scenes[Bm.scn_name(nn)]
    for w in bpy.context.window_manager.windows:
        w.scene = sc
    root = bpy.data.objects[aid + '_root']
    objs = [o for o in bpy.data.collections['AN_' + aid].objects if o.type == 'MESH']
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            mn = Vector((min(mn[i], p[i]) for i in range(3)))
            mx = Vector((max(mx[i], p[i]) for i in range(3)))
    ctr = (mn + mx) / 2
    rad = max((mx - mn).length / 2, 0.5)
    cam = bpy.data.objects.get('_contact_cam')
    if cam is None:
        cam = bpy.data.objects.new('_contact_cam', bpy.data.cameras.new('_contact_cam'))
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    cam.data.lens = 50
    d = Vector(view).normalized()
    cam.location = ctr + d * rad * 2.9
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    old = (sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath, sc.eevee.taa_render_samples)
    # hide everything but this animal (keep env)
    hidden = []
    for c in sc.collection.children:
        if c.name.startswith('Env_'):
            continue
        keep = c.name == 'AN_' + aid
        if not c.hide_render and not keep:
            c.hide_render = True
            hidden.append(c)
        if keep:
            for ch in c.children:
                if not ch.hide_render:
                    ch.hide_render = True
                    hidden.append(ch)
    gr = bpy.data.objects.get('Ground_' + sc.name)
    sc.camera = cam
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.eevee.taa_render_samples = 8
    os.makedirs(OUTDIR, exist_ok=True)
    sc.render.filepath = os.path.join(OUTDIR, '%02d_%s.png' % (nn, aid))
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for c in hidden:
        c.hide_render = False
    sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath, sc.eevee.taa_render_samples = old
    sc.collection.objects.unlink(cam)
    return sc.render.filepath


def biome_tiles(nn):
    Bm.rest_all(nn)
    return [tile(nn, r['id']) for r in Bm.rows(nn)]
