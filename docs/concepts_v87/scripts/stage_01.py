# Biome 01 Forest Edge: layout, checks, photo, video, export, json
import bpy, importlib, math, json, os, sys
import faunalib as L
from mathutils import Vector

SCN = 'Biome_01_ForestEdge'
NAME = 'forest_edge'
MODS = ['an_rabbit', 'an_squirrel', 'an_hedgehog', 'an_fox', 'an_dodo', 'an_moonrabbit']
ANG = [-78, -52, -26, 26, 52, 78]
RAD = 10.0
MQ = (0, 11.5, 0)


def spots():
    return [(round(RAD * math.sin(math.radians(a)), 2), round(RAD * math.cos(math.radians(a)) * 0.85 + 0.6, 2), 0) for a in ANG]


def mods():
    out = []
    for n in MODS:
        m = importlib.import_module(n)
        importlib.reload(m)
        out.append(m)
    return out


def show_all():
    sc = bpy.data.scenes[SCN]
    for c in sc.collection.children:
        c.hide_render = False
        c.hide_viewport = False
        for ch in c.children:
            ch.hide_render = False
            ch.hide_viewport = False
            for c2 in ch.children:
                c2.hide_render = False
                c2.hide_viewport = False


def objs_of(aid):
    c = bpy.data.collections['Bush_01' if aid == 'bush_01' else 'AN_' + aid]
    return list(c.all_objects)


def rest(aid):
    """segments to rest pose (FX objects keep their own keyed animation)"""
    L.rest_pose([o for o in objs_of(aid) if '_fx_' not in o.name])


def build_all(only=None, place=None):
    L.setup(SCN)
    show_all()
    import bush_01
    importlib.reload(bush_01)
    if only is None or 'bush_01' in only:
        bush_01.build((0, 0, 0))
        rest('bush_01')
    sp = spots()
    for m, p in zip(mods(), sp):
        if only is not None and m.ID not in only:
            continue
        m.build(place.get(m.ID, p) if place else p)
        rest(m.ID)
    L.mannequin(MQ)
    bpy.context.view_layer.update()


def fx_show(aid, clip=None):
    """bush FX: show only the sub-collection of the given Tease clip"""
    for c in bpy.data.collections['Bush_01'].children:
        for c2 in c.children:
            on = clip is not None and c2.name.endswith(clip.split('_')[1])
            c2.hide_render = not on
            c2.hide_viewport = not on


def play(aid, clip, offset=0):
    rest(aid)
    L.assign(clip, aid, offset)


def nla(aid, clip, start, extrap='HOLD'):
    pre = '%s_%s__' % (clip, aid)
    for a in bpy.data.actions:
        if a.name.startswith(pre):
            sname = a.name[len(pre):]
            ob = bpy.data.objects.get('%s_%s' % (aid, sname)) or bpy.data.objects.get(sname)
            if ob is None:
                continue
            ad = ob.animation_data_create()
            ad.action = None
            tr = ad.nla_tracks.new()
            st = tr.strips.new(a.name, int(start), a)
            st.extrapolation = extrap


def shift_fx(coll_name, d):
    for o in bpy.data.collections[coll_name].objects:
        if '_fx_' in o.name and o.animation_data and o.animation_data.action:
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.co.x += d
                    kp.handle_left.x += d
                    kp.handle_right.x += d
                fc.update()


def video_setup():
    """bush Tease_Epic (1-105) -> Open_Burst + Moon Rabbit Reveal (105-149) -> Idle (149-209)"""
    build_all(only=['moonrabbit', 'bush_01'], place={'moonrabbit': (0, -2.4, 0)})
    sc = bpy.data.scenes[SCN]
    for c in sc.collection.children:
        if c.name.startswith('AN_') and c.name != 'AN_moonrabbit':
            c.hide_render = True
            c.hide_viewport = True
        if c.name.startswith('Mannequin'):
            c.hide_render = True
            c.hide_viewport = True
    fx_show('bush_01', 'Tease_Epic')
    rest('bush_01')
    rest('moonrabbit')
    nla('bush_01', 'Tease_Epic', 1)
    nla('bush_01', 'Open_Burst', 105, 'HOLD_FORWARD')
    nla('moonrabbit', 'Reveal', 105)
    nla('moonrabbit', 'Idle', 149, 'HOLD_FORWARD')
    shift_fx('AN_moonrabbit_FX', 104)
    cam = sc.camera
    cam.location = (5.5, -17.5, 5.2)
    d = Vector((0, -1.0, 2.9)) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 35
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.frame_start, sc.frame_end = 1, 209
