# Biome deliverables: photo, GLB export, creatures.json (used with stage_01)
import bpy, importlib, math, json, os
import faunalib as L
from mathutils import Vector
import stage_01 as S


def cover_scale(st):
    """how much to scale the bush so the animal is fully hidden inside (1.0 = as is)"""
    b = L.stats('bush_01', 'Bush_01')['size']
    w, ln, h = st['size']
    return round(max(1.0, 1.25 * w / b[0], 1.1 * ln / b[1], 1.15 * h / b[2]), 2)


def photo_setup():
    S.build_all()
    sc = bpy.data.scenes[S.SCN]
    S.fx_show('bush_01', None)
    cam = sc.camera
    cam.location = (0, -21, 14.5)
    d = Vector((0, 3.4, 1.2)) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 36
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
    sc.frame_start, sc.frame_end = 1, 105
    sc.frame_set(1)
    bpy.context.view_layer.update()


def photo(raw_path, labels_path):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes[S.SCN]
    sc.eevee.taa_render_samples = 48
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = raw_path
    bpy.ops.render.render(scene=sc.name)          # warm-up
    bpy.ops.render.render(write_still=True, scene=sc.name)
    labs = []
    for m in S.mods():
        st = L.stats(m.ID, 'AN_' + m.ID)
        r = bpy.data.objects[m.ID + '_root']
        top = r.matrix_world.translation + Vector((0, 0, st['max'][2] + 0.5))
        v = world_to_camera_view(sc, sc.camera, top)
        labs.append(dict(name=m.NAME, rarity=m.RARITY, x=v.x * 1920, y=(1 - v.y) * 1080))
    for nm, p in (('Bush 01', Vector((0, -1.9, -0.4))), ('5 studs', Vector(S.MQ) + Vector((0, 0, 5.9)))):
        v = world_to_camera_view(sc, sc.camera, p)
        labs.append(dict(name=nm, rarity=0, x=v.x * 1920, y=(1 - v.y) * 1080))
    json.dump(labs, open(labels_path, 'w'))
    return labs


def export_fx(coll_name, path, prefix):
    """reveal / tease FX meshes laid out in a row at scale 1 (one of each kind)"""
    seen, objs = set(), []

    def walk(c):
        for o in c.objects:
            if o.type != 'MESH':
                continue
            if '_fx_' in o.name:
                kind = o.name.split('_fx_')[-1].rstrip('0123456789').rstrip('_')
            else:
                kind = o.get('segment', o.name)
            if kind in seen:
                continue
            seen.add(kind)
            objs.append((kind, o))
        for ch in c.children:
            walk(ch)
    walk(bpy.data.collections[coll_name])
    if not objs:
        return []
    tmpc = L.get_coll('_export_tmp')
    for vl in bpy.data.scenes[S.SCN].view_layers:
        for o in vl.objects:
            o.select_set(False)
    names = []
    for i, (kind, o) in enumerate(objs):
        me = o.data.copy()
        first = None
        for mi, m in enumerate(me.materials):
            if m and not m.get('outline'):
                me.materials[mi] = L._pbr(m)
                first = first or me.materials[mi]
        for mi, m in enumerate(me.materials):
            if m is None or m.get('outline'):
                me.materials[mi] = first
        L.box_uv(me)
        c = bpy.data.objects.new('%s_%s' % (prefix, kind), me)
        tmpc.objects.link(c)
        c.location = (i * 2.0, 0, 0)
        c.select_set(True)
        names.append(kind)
    bpy.context.view_layer.objects.active = tmpc.objects[0]
    bpy.ops.export_scene.gltf(filepath=path, use_selection=True, use_active_scene=True, export_format='GLB',
                              export_apply=False, export_animations=False, export_yup=True, export_texcoords=True,
                              export_normals=True, export_extras=False)
    L._clear(tmpc)
    bpy.data.collections.remove(tmpc)
    return names


def export_all():
    os.makedirs(L.EXP, exist_ok=True)
    out = {}
    L.G.scene = bpy.data.scenes[S.SCN]
    out['bush_01'] = L.export_hierarchy(bpy.data.objects['bush_01_root'], os.path.join(L.EXP, 'bush_01.glb'))
    out['fx_bush_01'] = export_fx('Bush_01_FX', os.path.join(L.EXP, 'fx_bush_01.glb'), 'fx_bush_01')
    for m in S.mods():
        out[m.ID] = L.export_hierarchy(bpy.data.objects[m.ID + '_root'], os.path.join(L.EXP, 'an_%s.glb' % m.ID))
        out['fx_' + m.ID] = export_fx('AN_%s_FX' % m.ID, os.path.join(L.EXP, 'fx_%s.glb' % m.ID), 'fx_' + m.ID)
    return out


def _keys(aid, clip):
    out = {}
    pre = '%s_%s__' % (clip, aid)
    for a in bpy.data.actions:
        if not a.name.startswith(pre):
            continue
        sname = a.name[len(pre):]
        ob = bpy.data.objects.get('%s_%s' % (aid, sname))
        if ob is None:
            continue
        rest = Vector(ob.get('rest_loc', (0, 0, 0)))
        d = {}
        for path, key in (('location', 'loc'), ('rotation_euler', 'rot'), ('scale', 'scale')):
            fcs = [a.fcurves.find(path, index=i) for i in range(3)]
            if not all(fcs):
                continue
            frames = sorted({int(round(kp.co.x)) for fc in fcs for kp in fc.keyframe_points})
            rows = []
            for f in frames:
                v = [fc.evaluate(f) for fc in fcs]
                if key == 'loc':
                    v = [v[i] - rest[i] for i in range(3)]
                if key == 'rot':
                    v = [math.degrees(x) for x in v]
                ip = next((kp.interpolation for kp in fcs[0].keyframe_points if int(round(kp.co.x)) == f), 'BEZIER')
                rows.append([f] + [round(x, 4) for x in v] + [ip[0]])
            d[key] = rows
        out[sname] = d
    return out


def _segments(aid):
    root = bpy.data.objects[aid + '_root']
    segs = []

    def walk(o, base):
        for ch in o.children:
            if ch.type != 'MESH' or 'segment' not in ch:
                continue
            j = base + Vector(ch.get('rest_loc', ch.location))
            mats = [m for m in ch.data.materials if m and not m.get('outline')]
            ch.data.calc_loop_triangles()
            segs.append(dict(name=ch['segment'], object=ch.name, parent=(o['segment'] if 'segment' in o else 'root'),
                             joint=[round(x, 4) for x in j], color=(mats[0].get('hex') if mats else None),
                             colors=[dict(hex=m.get('hex'), kind=m.get('kind')) for m in mats],
                             parts=ch.get('parts', 1), tris=len(ch.data.loop_triangles),
                             fx=ch['segment'].startswith('fxs_')))
            walk(ch, j)
    walk(root, Vector((0, 0, 0)))
    return segs


def _fxkeys(coll_name, root_loc):
    out = []

    def walk(c):
        for o in c.objects:
            if not o.animation_data or not o.animation_data.action or 'segment' in o:
                continue
            a = o.animation_data.action
            d = dict(name=o.name.split('_fx_')[-1], group=c.name)
            if o.type == 'MESH':
                m = o.data.materials[0] if o.data.materials else None
                bb = Vector(o.bound_box[6]) - Vector(o.bound_box[0])
                d['size'] = [round(x, 3) for x in bb]
                d['color'] = m.get('hex') if m else None
                d['material'] = m.get('kind') if m else None
            elif o.type == 'LIGHT':
                d['light'] = dict(type=o.data.type, color=[round(x, 3) for x in o.data.color], energy=o.data.energy)
                ad = o.data.animation_data
                if ad and ad.action:
                    fc = ad.action.fcurves.find('energy')
                    if fc:
                        d['energy_keys'] = [[int(round(kp.co.x)), round(kp.co.y, 2)] for kp in fc.keyframe_points]
            for path, key, n in (('location', 'loc', 3), ('scale', 'scale', 3), ('color', 'alpha', 4), ('rotation_euler', 'rot', 3)):
                fcs = [a.fcurves.find(path, index=i) for i in range(n)]
                if key == 'alpha':
                    fcs = [fcs[3]] if fcs[3] else []
                if not fcs or not all(fcs):
                    continue
                frames = sorted({int(round(kp.co.x)) for fc in fcs for kp in fc.keyframe_points})
                rows = []
                for f in frames:
                    v = [fc.evaluate(f) for fc in fcs]
                    if key == 'loc':
                        v = [v[i] - root_loc[i] for i in range(3)]
                    if key == 'rot':
                        v = [math.degrees(x) for x in v]
                    rows.append([f] + [round(x, 3) for x in v])
                d[key] = rows
            out.append(d)
        for ch in c.children:
            walk(ch)
    walk(bpy.data.collections[coll_name])
    return out


def creatures_json(path, registry_path):
    import bush_01
    data = dict(
        conventions=dict(
            units='1 Blender unit = 1 Roblox stud', fps=30,
            axes='Blender: Z up, animal faces -Y, origin on the ground under the body centre. GLB files are glTF Y-up: '
                 'Blender (x, y, z) -> glTF (x, z, -y). All numbers in this file are in Blender axes.',
            joints='segment.joint = pivot of the segment in the animal rest space (studs, from the animal origin)',
            keys='per clip, per segment: loc = offset from the rest position [frame, dx, dy, dz, interp], rot = Euler XYZ degrees '
                 '[frame, rx, ry, rz, interp], scale = factor [frame, sx, sy, sz, interp]; interp B = bezier ease, L = linear, '
                 'C = constant. Frames are clip-local and start at 1.',
            root='the root segment is the whole animal: Reveal keys of root are offsets from the final standing spot; '
                 'the bush centre is at (0, +bush_distance, 0) from that spot',
            fx='fx objects are not in an_<id>.glb. fx keys: loc relative to the final spot (bush fx: relative to the bush origin), '
               'scale factor, alpha 0..1. Segments named fxs_* are permanent effects (aura, sparks, motes): ParticleEmitters in Roblox.',
            glow='glow = brightness channel 0..1 for Neon segments [frame, value] (in Blender it is shown as a scale pulse)',
            stud_material='stud pitch 0.25 stud; UV: 1 UV unit = 1 stud of length = 4 studs of the grid = one studs_tile.png; '
                          'checker cells are 2x2 grid studs; box projection with the same density on every part'),
        biomes=[], bushes=[], creatures=[])
    bs = L.stats('bush_01', 'Bush_01')
    data['biomes'].append(dict(id=1, name='Forest Edge', scene=S.SCN, bush='bush_01', creatures=[m.ID for m in S.mods()]))
    data['bushes'].append(dict(
        id='bush_01', biome=1, glb='bush_01.glb', fx_glb='fx_bush_01.glb', size=bs['size'], tris=bs['tris'], parts=bs['parts'],
        durations_frames=dict(bush_01.LEN), epic_glow={str(k): v for k, v in bush_01.EPIC_GLOW.items()},
        segments=_segments('bush_01'),
        keys={c: _keys('bush_01', c) for c in bush_01.LEN},
        fx=_fxkeys('Bush_01_FX', (0, 0, 0))))
    reg = []
    for m in S.mods():
        st = L.stats(m.ID, 'AN_' + m.ID)
        root = bpy.data.objects[m.ID + '_root']
        segs = _segments(m.ID)
        zone = []
        for s in segs:
            for c in s['colors']:
                if c['hex'] and c not in zone:
                    zone.append(c)
        mk = {}
        for nm in ('Head', 'Chest', 'Hit'):
            e = bpy.data.objects['%s_%s' % (m.ID, nm)]
            mk[nm] = [round(x, 3) for x in e['rest_space']]
        rev_len = max(int(a.frame_range[1]) for a in bpy.data.actions if a.name.startswith('Reveal_%s__' % m.ID))
        idle_len = max(int(a.frame_range[1]) for a in bpy.data.actions if a.name.startswith('Idle_%s__' % m.ID))
        data['creatures'].append(dict(
            id=m.ID, name=m.NAME, rarity=m.RARITY, biome=m.BIOME, kind=m.KIND, glb='an_%s.glb' % m.ID, fx_glb='fx_%s.glb' % m.ID,
            height=st['size'][2], length=st['size'][1], width=st['size'][0], tris=st['tris'], parts=st['parts'],
            hover_height=0, markers=mk, zone_colors=zone, cover_scale=cover_scale(st),
            method=m.METHOD, gesture=m.GESTURE, bush_open=m.OPEN, bush_distance=m.BUSH_D,
            reveal_frames=rev_len, idle_frames=idle_len,
            segments=segs,
            keys=dict(Reveal=_keys(m.ID, 'Reveal'), Idle=_keys(m.ID, 'Idle')),
            glow=json.loads(root.get('glow', '{}')),
            fx=_fxkeys('AN_%s_FX' % m.ID, root.get('rest_loc', (0, 0, 0)))))
        reg.append([m.ID, m.BIOME, m.METHOD, m.GESTURE])
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump(dict(note='unique (method, gesture) pairs across all 150 animals', pairs=reg), open(registry_path, 'w'), indent=1)
    return {c['id']: (c['parts'], c['tris'], c['cover_scale'], c['reveal_frames'], c['idle_frames']) for c in data['creatures']}
