# SpearHunt V87 - generic biome stage: build, layout, photo, export, creatures.json merge, reveal table, save.
# Usage in Blender:  import biome as B; B.build(2); B.photo(2); B.deliver(2)
import bpy, importlib, math, json, os, sys, io
import faunalib as L
import kits, moves, bushkit
from mathutils import Vector

ANG = [-78, -52, -26, 26, 52, 78]


def roster():
    return json.load(open(os.path.join(L.OUT, 'roster.json'), encoding='utf-8'))


def rows(nn):
    return [r for r in roster()['animals'] if r['biome'] == nn]


def scn_name(nn):
    r = roster()['biomes'][str(nn)]
    return 'Biome_%02d_%s' % (nn, r['name'].replace(' ', ''))


def mod(nn):
    for n in ('kits', 'moves', 'bushkit'):
        importlib.reload(sys.modules[n])
    m = importlib.import_module('biome_%02d' % nn)
    importlib.reload(m)
    return m


def _layout(nn):
    """semicircle behind the bush by rarity; every animal gets an arc share proportional to its footprint"""
    rs = rows(nn)
    foot = getattr(sys.modules.get('biome_%02d' % nn), 'FOOT', {})
    fp = [max(2.8, 0.95 * r['height'] + 1.4) * (1.25 if r['rarity'] >= 5 else 1.0) * foot.get(r['id'], 1.0) for r in rs]
    span = math.radians(74.0)
    rad = max(10.0, sum(fp[:3]) / span, sum(fp[3:]) / span)
    angs = []
    for side, a0 in ((fp[:3], -86.0), (fp[3:], 12.0)):
        tot = sum(side)
        cur = a0
        for f in side:
            w = 74.0 * f / tot
            angs.append(cur + w / 2)
            cur += w
    return rad, angs, fp


def radius(nn):
    return _layout(nn)[0]


def spots(nn):
    rad, angs, fp = _layout(nn)
    return [(round(rad * math.sin(math.radians(a)), 2), round(rad * math.cos(math.radians(a)) * 0.85 + 0.6, 2), 0) for a in angs]


def show_all(nn, bush_fx=None):
    sc = bpy.data.scenes[scn_name(nn)]

    def rec(c, depth):
        c.hide_render = False
        c.hide_viewport = False
        for ch in c.children:
            rec(ch, depth + 1)
    rec(sc.collection, 0)
    fxc = bpy.data.collections.get('Bush_%02d_FX' % nn)
    if fxc:
        for c2 in fxc.children:
            on = bush_fx is not None and c2.name.endswith(bush_fx)
            c2.hide_render = not on
            c2.hide_viewport = not on


def objs_of(aid):
    c = bpy.data.collections['Bush_' + aid[5:] if aid.startswith('bush_') else 'AN_' + aid]
    return list(c.all_objects)


def rest(aid):
    L.rest_pose([o for o in objs_of(aid) if '_fx_' not in o.name and o.type != 'LIGHT'])


def build(nn, only=None, place=None):
    """(re)build the bush and the animals of biome nn in its own scene. only = list of ids ('bush' for the bush)"""
    m = mod(nn)
    sc = L.setup(scn_name(nn))
    gr = L.ground(m.GROUND, 140)
    for nd in gr.data.materials[0].node_tree.nodes:
        if nd.type == 'GROUP':
            nd.inputs['Color'].default_value = L.H(m.GROUND)
    w = sc.world.node_tree.nodes.get('CAMBG')
    if w and getattr(m, 'SKY', None):
        w.inputs[0].default_value = L.H(m.SKY)
    show_all(nn)
    moves.THEME = m.THEME
    out = {}
    if only is None or 'bush' in only:
        kits.K.place = (0, 0, 0)
        st = m.bush()
        rest('bush_%02d' % nn)
        out['bush'] = (st['parts'], st['tris'], st['size'])
    bst = L.stats('bush_%02d' % nn, 'Bush_%02d' % nn)
    kits.K.bush = tuple(bst['size'])
    for r, sp in zip(rows(nn), spots(nn)):
        if only is not None and r['id'] not in only:
            continue
        kits.K.place = (place or {}).get(r['id'], sp)
        m.ANIMALS[r['id']](r)
        rest(r['id'])
        st = L.stats(r['id'], 'AN_' + r['id'])
        out[r['id']] = (st['parts'], st['tris'], st['size'])
    rad = radius(nn)
    L.mannequin((0, rad * 0.85 + 3.0, 0))
    bpy.context.view_layer.update()
    cam_photo(nn)
    sc.frame_set(1)
    return out


def cam_photo(nn):
    sc = bpy.data.scenes[scn_name(nn)]
    rad0, angs, fp = _layout(nn)
    rad = rad0 + 0.1 * max(fp[0], fp[-1]) - 1.0
    hmax = max(r['height'] for r in rows(nn))
    cam = sc.camera
    cam.location = (0, -1.75 * rad, 1.3 * rad)
    d = Vector((0, 0.4 * rad, 0.05 * rad + 0.12 * hmax)) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 36 if hmax < 9 else 33
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100


def play(nn, clip='Reveal', bush_clip=None):
    """assign a clip to every animal (for look checks)"""
    for r in rows(nn):
        rest(r['id'])
        L.assign(clip, r['id'])
    if bush_clip:
        rest('bush_%02d' % nn)
        L.assign(bush_clip, 'bush_%02d' % nn)


def rest_all(nn):
    for r in rows(nn):
        rest(r['id'])
    rest('bush_%02d' % nn)
    bpy.data.scenes[scn_name(nn)].frame_set(1)
    bpy.context.view_layer.update()


def photo(nn):
    from bpy_extras.object_utils import world_to_camera_view
    for w in bpy.context.window_manager.windows:
        w.scene = bpy.data.scenes[scn_name(nn)]
    rest_all(nn)
    show_all(nn)
    cam_photo(nn)
    sc = bpy.data.scenes[scn_name(nn)]
    key = roster()['biomes'][str(nn)]['key']
    sp = os.environ.get('TEMP', L.OUT)
    raw = os.path.join(sp, 'biome%02d_raw.png' % nn)
    lab = os.path.join(sp, 'biome%02d_labels.json' % nn)
    sc.eevee.taa_render_samples = 48
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = raw
    bpy.ops.render.render(scene=sc.name)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    labs = []
    for r in rows(nn):
        st = L.stats(r['id'], 'AN_' + r['id'])
        ro = bpy.data.objects[r['id'] + '_root']
        top = ro.matrix_world.translation + Vector((0, 0, st['max'][2] + 0.06 * r['height'] + 0.4))
        v = world_to_camera_view(sc, sc.camera, top)
        labs.append(dict(name=r['name'], rarity=r['rarity'], x=v.x * 1920, y=(1 - v.y) * 1080))
    bst = L.stats('bush_%02d' % nn, 'Bush_%02d' % nn)
    rad = radius(nn)
    for nm, q in (('Bush %02d' % nn, Vector((0, bst['min'][1] - 0.5, -0.4))), ('5 studs', Vector((0, rad * 0.85 + 3.0, 5.9)))):
        v = world_to_camera_view(sc, sc.camera, q)
        labs.append(dict(name=nm, rarity=0, x=v.x * 1920, y=(1 - v.y) * 1080))
    json.dump(labs, open(lab, 'w'))
    out = os.path.join(L.OUT, 'shots', 'biome_%02d_%s.png' % (nn, key))
    title = 'Biome %02d - %s' % (nn, roster()['biomes'][str(nn)]['name'])
    return raw, lab, out, title


# ---------------------------------------------------------------- export
def _swap_mats(me):
    first = None
    for i, m_ in enumerate(me.materials):
        if m_ and not m_.get('outline'):
            me.materials[i] = L._pbr(m_)
            first = first or me.materials[i]
    for i, m_ in enumerate(me.materials):
        if m_ is None or m_.get('outline'):
            me.materials[i] = first


def export_fx(nn, coll_name, path, prefix):
    seen, objs = set(), []

    def walk(c):
        for o in c.objects:
            if o.type != 'MESH':
                continue
            kind = o.name.split('_fx_')[-1].rstrip('0123456789').rstrip('_') if '_fx_' in o.name else o.get('segment', o.name)
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
    for vl in bpy.data.scenes[scn_name(nn)].view_layers:
        for o in vl.objects:
            o.select_set(False)
    names = []
    for i, (kind, o) in enumerate(objs):
        me = o.data.copy()
        _swap_mats(me)
        L.box_uv(me)
        c = bpy.data.objects.new('%s_%s' % (prefix, kind), me)
        tmpc.objects.link(c)
        c.location = (i * 3.0, 0, 0)
        c.select_set(True)
        names.append(kind)
    bpy.context.view_layer.objects.active = tmpc.objects[0]
    bpy.ops.export_scene.gltf(filepath=path, use_selection=True, use_active_scene=True, export_format='GLB', export_apply=False,
                              export_animations=False, export_yup=True, export_texcoords=True, export_normals=True, export_extras=False)
    L._clear(tmpc)
    bpy.data.collections.remove(tmpc)
    return names


def export(nn):
    os.makedirs(L.EXP, exist_ok=True)
    L.G.scene = bpy.data.scenes[scn_name(nn)]
    for w in bpy.context.window_manager.windows:
        w.scene = L.G.scene
    rest_all(nn)
    show_all(nn)
    for m_ in list(bpy.data.materials):
        if m_.name.startswith('PBR_') and m_.users == 0:
            bpy.data.materials.remove(m_)
    bid = 'bush_%02d' % nn
    out = {bid: L.export_hierarchy(bpy.data.objects[bid + '_root'], os.path.join(L.EXP, bid + '.glb'))}
    out['fx_' + bid] = len(export_fx(nn, 'Bush_%02d_FX' % nn, os.path.join(L.EXP, 'fx_%s.glb' % bid), 'fx_' + bid))
    for r in rows(nn):
        out[r['id']] = L.export_hierarchy(bpy.data.objects[r['id'] + '_root'], os.path.join(L.EXP, 'an_%s.glb' % r['id']))
        out['fx_' + r['id']] = len(export_fx(nn, 'AN_%s_FX' % r['id'], os.path.join(L.EXP, 'fx_%s.glb' % r['id']), 'fx_' + r['id']))
    show_all(nn)
    return out


# ---------------------------------------------------------------- json
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
        rest_ = Vector(ob.get('rest_loc', (0, 0, 0)))
        d = {}
        for path, key in (('location', 'loc'), ('rotation_euler', 'rot'), ('scale', 'scale')):
            fcs = [a.fcurves.find(path, index=i) for i in range(3)]
            if not all(fcs):
                continue
            frames = sorted({int(round(kp.co.x)) for fc in fcs for kp in fc.keyframe_points})
            rws = []
            for f in frames:
                v = [fc.evaluate(f) for fc in fcs]
                if key == 'loc':
                    v = [v[i] - rest_[i] for i in range(3)]
                if key == 'rot':
                    v = [math.degrees(x) for x in v]
                ip = next((kp.interpolation for kp in fcs[0].keyframe_points if int(round(kp.co.x)) == f), 'BEZIER')
                rws.append([f] + [round(x, 4) for x in v] + [ip[0]])
            d[key] = rws
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
            mats = [m_ for m_ in ch.data.materials if m_ and not m_.get('outline')]
            ch.data.calc_loop_triangles()
            segs.append(dict(name=ch['segment'], object=ch.name, parent=(o['segment'] if 'segment' in o else 'root'),
                             joint=[round(x, 4) for x in j], color=(mats[0].get('hex') if mats else None),
                             colors=[dict(hex=m_.get('hex'), kind=m_.get('kind')) for m_ in mats],
                             parts=ch.get('parts', 1), tris=len(ch.data.loop_triangles), fx=ch['segment'].startswith('fxs_')))
            walk(ch, j)
    walk(root, Vector((0, 0, 0)))
    return segs


def _fxkeys(coll_name, root_loc):
    out = []

    def walk(c):
        for o in c.objects:
            if not o.animation_data or not o.animation_data.action or 'segment' in o:
                if o.type != 'LIGHT':
                    continue
            d = dict(name=o.name.split('_fx_')[-1], group=c.name)
            if o.type == 'MESH':
                m_ = o.data.materials[0] if o.data.materials else None
                bb = Vector(o.bound_box[6]) - Vector(o.bound_box[0])
                d['size'] = [round(x, 3) for x in bb]
                d['color'] = m_.get('hex') if m_ else None
                d['material'] = m_.get('kind') if m_ else None
            elif o.type == 'LIGHT':
                d['light'] = dict(type=o.data.type, color=[round(x, 3) for x in o.data.color])
                d['loc'] = [[1] + [round(o.location[i] - root_loc[i], 3) for i in range(3)]]
                ad = o.data.animation_data
                if ad and ad.action:
                    fc = ad.action.fcurves.find('energy')
                    if fc:
                        d['energy_keys'] = [[int(round(kp.co.x)), round(kp.co.y, 2)] for kp in fc.keyframe_points]
                out.append(d)
                continue
            a = o.animation_data.action
            for path, key, n in (('location', 'loc', 3), ('scale', 'scale', 3), ('color', 'alpha', 4), ('rotation_euler', 'rot', 3)):
                fcs = [a.fcurves.find(path, index=i) for i in range(n)]
                if key == 'alpha':
                    fcs = [fcs[3]] if fcs[3] else []
                if not fcs or not all(fcs):
                    continue
                frames = sorted({int(round(kp.co.x)) for fc in fcs for kp in fc.keyframe_points})
                rws = []
                for f in frames:
                    v = [fc.evaluate(f) for fc in fcs]
                    if key == 'loc':
                        v = [v[i] - root_loc[i] for i in range(3)]
                    if key == 'rot':
                        v = [math.degrees(x) for x in v]
                    rws.append([f] + [round(x, 3) for x in v])
                d[key] = rws
            out.append(d)
        for ch in c.children:
            walk(ch)
    walk(bpy.data.collections[coll_name])
    return out


def head_ratio(aid):
    """head block height / total height without ears, from the head mesh bounds"""
    return None


def to_json(nn):
    rest_all(nn)
    path = os.path.join(L.OUT, 'creatures.json')
    data = json.load(open(path, encoding='utf-8'))
    ro = roster()
    bid = 'bush_%02d' % nn
    bs = L.stats(bid, 'Bush_%02d' % nn)
    binfo = json.loads(bpy.data.objects[bid + '_root'].get('info', '{}'))
    data['biomes'] = [b for b in data['biomes'] if b['id'] != nn] + [dict(
        id=nn, name=ro['biomes'][str(nn)]['name'], scene=scn_name(nn), bush=bid, creatures=[r['id'] for r in rows(nn)])]
    data['bushes'] = [b for b in data['bushes'] if b['id'] != bid] + [dict(
        id=bid, biome=nn, glb=bid + '.glb', fx_glb='fx_%s.glb' % bid, size=bs['size'], tris=bs['tris'], parts=bs['parts'],
        durations_frames=dict(bushkit.LEN), epic_glow={str(k): v for k, v in bushkit.EPIC_GLOW.items()},
        fx_sets=sorted(c.name for c in bpy.data.collections['Bush_%02d_FX' % nn].children),
        segments=_segments(bid), keys={c: _keys(bid, c) for c in bushkit.LEN}, fx=_fxkeys('Bush_%02d_FX' % nn, (0, 0, 0)),
        notes=binfo.get('fx_notes', {}))]
    ids = {r['id'] for r in rows(nn)}
    data['creatures'] = [c for c in data['creatures'] if c['id'] not in ids]
    res = {}
    for r in rows(nn):
        aid = r['id']
        st = L.stats(aid, 'AN_' + aid)
        root = bpy.data.objects[aid + '_root']
        info = json.loads(root.get('info', '{}'))
        segs = _segments(aid)
        zone = []
        for s in segs:
            for c in s['colors']:
                if c['hex'] and c not in zone and not s['fx']:
                    zone.append(c)
        mk = {nm: [round(x, 3) for x in bpy.data.objects['%s_%s' % (aid, nm)]['rest_space']] for nm in ('Head', 'Chest', 'Hit')}
        hover = float(root.get('hover', 0.0))
        rl = list(root.get('rest_loc', (0, 0, 0)))
        ground = (rl[0], rl[1], rl[2] - hover)
        hd = bpy.data.objects.get(aid + '_head')
        head_h = None
        if hd:
            zs = [v.co.z for v in hd.data.vertices]
            head_h = round(max(zs) - min(zs), 2)
        rec = dict(
            id=aid, name=r['name'], rarity=r['rarity'], biome=nn, kind=r['kind'], glb='an_%s.glb' % aid, fx_glb='fx_%s.glb' % aid,
            height=st['size'][2], length=st['size'][1], width=st['size'][0], tris=st['tris'], parts=st['parts'],
            hover_height=hover, origin=('body centre' if hover else 'ground under the body centre'), head_height=head_h,
            markers=mk, zone_colors=zone, cover_scale=info.get('cover', 1.0),
            method=r['method'], gesture=r['gesture'], bush_open=r['open'], bush_distance=info.get('bush_d'),
            reveal_frames=info.get('reveal'), idle_frames=info.get('idle'),
            segments=segs, keys=dict(Reveal=_keys(aid, 'Reveal'), Idle=_keys(aid, 'Idle')),
            glow=json.loads(root.get('glow', '{}')), fx=_fxkeys('AN_%s_FX' % aid, ground), fx_notes=info.get('fx_notes', []))
        data['creatures'].append(rec)
        res[aid] = (rec['parts'], rec['tris'], rec['height'], rec['cover_scale'], rec['reveal_frames'], rec['idle_frames'], head_h)
    order = {r['id']: i for i, r in enumerate(ro['animals'])}
    data['creatures'].sort(key=lambda c: order[c['id']])
    data['biomes'].sort(key=lambda b: b['id'])
    data['bushes'].sort(key=lambda b: b['id'])
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    pairs = [[c['id'], c['biome'], c['method'], c['gesture']] for c in data['creatures']]
    json.dump(dict(note='unique (method, gesture) pairs across all 150 animals', pairs=pairs),
              open(os.path.join(L.OUT, 'reveal_pairs.json'), 'w'), indent=1)
    table(nn, data)
    # mark the roster rows as done (freezes their method / gesture)
    for a in ro['animals']:
        if a['biome'] == nn:
            a['status'] = 'done'
    json.dump(ro, open(os.path.join(L.OUT, 'roster.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return res


def table(nn, data):
    """(re)write the section of reveal_table.md for biome nn from the data"""
    ro = roster()
    bname = ro['biomes'][str(nn)]['name']
    bush = next(b for b in data['bushes'] if b['biome'] == nn)
    m = sys.modules.get('biome_%02d' % nn)
    L_ = ['', '<!-- biome %02d -->' % nn, '# Биом %d — %s' % (nn, bname), '']
    L_.append('## Куст bush_%02d — %s' % (nn, getattr(m, 'BUSH_NAME', '')))
    L_.append('')
    L_.append('Размер %.2f × %.2f × %.2f studs, %d подвижных частей из %d деталей, %d треугольников. Клипы и приёмы — как у куста биома 1 '
              '(Tease_Common 75 кадров, Tease_Rare 90, Tease_Epic 105, Open_Burst 15, Open_Part 15); отличаются частицы и цвета.'
              % (bush['size'][0], bush['size'][1], bush['size'][2], len(bush['segments']), bush['parts'], bush['tris']))
    L_.append('')
    for tag, title in (('Common', 'Tease_Common (r1–r2)'), ('Rare', 'Tease_Rare (r3–r4)'), ('Epic5', 'Tease_Epic для r5'), ('Epic6', 'Tease_Epic для r6')):
        if tag in bush.get('notes', {}):
            L_.append('- **%s.** %s.' % (title, '; '.join(bush['notes'][tag])))
    L_.append('')
    L_.append('| Зверь | Редкость | Способ → жест | Reveal | Idle | Куст | CoverScale | Рост | Деталей | Треугольников |')
    L_.append('|---|---|---|---|---|---|---|---|---|---|')
    cs = [c for c in data['creatures'] if c['biome'] == nn]
    for c in cs:
        L_.append('| %s | r%d | %s → %s | %d | %d | %s | %s | %.1f | %d | %d |' % (
            c['name'], c['rarity'], c['method'], c['gesture'], c['reveal_frames'], c['idle_frames'], c['bush_open'], c['cover_scale'],
            c['height'], c['parts'], c['tris']))
    L_.append('')
    for c in cs:
        mt = moves.M_TXT[c['method']]
        segn = [s['name'] for s in c['segments']]
        hang = ''
        L_.append('### %s (%s, r%d)' % (c['name'], c['id'], c['rarity']))
        L_.append('')
        kindtxt = {'air': 'летающий, зависает на высоте %.1f' % c['hover_height'], 'water': 'водный, плавает на высоте %.1f' % c['hover_height'],
                   'shore': 'береговой', 'ground': 'наземный'}[c['kind']]
        L_.append('- **Появление, %d кадров (%s).** Зверь: %s. Затем жест: %s. Куст стоит в %.1f studs позади точки и раскрывается клипом %s.'
                  % (c['reveal_frames'], kindtxt, mt[0], moves.G_TXT[c['gesture']], c['bush_distance'], c['bush_open']))
        if c['fx_notes']:
            L_.append('- **Эффекты.** ' + '; '.join(c['fx_notes']) + '.')
        idl = ['дыхание (тело ×1.03)', 'поворот головы', 'моргание']
        if any(s.startswith('ear_') or s.startswith('antenna_') for s in segn):
            idl.append('ухо или усик дёргается')
        if any(s.startswith('tail') for s in segn):
            idl.append('хвост покачивается')
        if c['kind'] in ('air', 'water'):
            idl.append('парит вверх-вниз и машет крыльями/плавниками')
        if c['glow']:
            idl.append('светящиеся детали мерцают (канал glow)')
        if any(s in ('orbit', 'orbit2', 'halo') for s in segn):
            idl.append('парящие детали делают полный оборот')
        if 'fxs_aura' in segn:
            idl.append('аура у ног медленно вращается')
        L_.append('- **Idle, %d кадров.** %s.' % (c['idle_frames'], ', '.join(idl).capitalize()))
        rob = [mt[1]]
        if c['rarity'] >= 4:
            neon = [z['hex'] for z in c['zone_colors'] if z['kind'] == 'neon']
            if neon:
                rob.append('Neon-части: ' + ', '.join('`%s`' % h for h in neon[:4]))
        if 'fxs_aura' in segn:
            rob.append('аура — ParticleEmitter на плоском кольце у ног, цвет `%s`, LightEmission 1, + PointLight Range %d'
                       % ('#ffe600' if c['rarity'] == 5 else '#ff2a2a', int(6 + c['height'])))
        if 'fxs_motes' in segn or 'fxs_sparks' in segn:
            rob.append('парящие искры — ParticleEmitter, Rate 4–6, размер 0.1')
        L_.append('- **Roblox.** ' + '; '.join(rob) + '.')
        L_.append('')
    L_.append('<!-- /biome %02d -->' % nn)
    path = os.path.join(L.OUT, 'reveal_table.md')
    s = io.open(path, encoding='utf-8').read()
    a, b = '<!-- biome %02d -->' % nn, '<!-- /biome %02d -->' % nn
    if a in s:
        s = s[:s.index(a) - 1].rstrip('\n') + '\n' + s[s.index(b) + len(b):]
    s = s.rstrip('\n') + '\n' + '\n'.join(L_) + '\n'
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


def save(nn):
    """main work file + a clean per-biome .blend holding only this biome's scene and its actions"""
    key = roster()['biomes'][str(nn)]['key']
    path = os.path.join(L.OUT, 'biomes', 'biome_%02d_%s.blend' % (nn, key))
    sc = bpy.data.scenes[scn_name(nn)]
    ids = ['bush_%02d' % nn] + [r['id'] for r in rows(nn)]
    blocks = {sc}
    for a in bpy.data.actions:
        nm = a.name
        if any(('_%s__' % i) in nm for i in ids):
            blocks.add(a)
    bpy.data.libraries.write(path, blocks, fake_user=True)
    bpy.ops.wm.save_mainfile()
    return path, len(blocks)


def deliver(nn):
    out = export(nn)
    res = to_json(nn)
    pth = save(nn)
    return out, res, pth
