from gymlib import *

import importlib

ALL = {1: 'Wooden', 2: 'Stone', 3: 'Bronze', 4: 'Iron', 5: 'Granite', 6: 'Golden', 7: 'Mammoth', 8: 'Crystal',
       9: 'Obsidian', 10: 'Frost', 11: 'Magma', 12: 'Storm', 13: 'Jade', 14: 'Celestial', 15: 'Primal'}
LEVELS = dict(ALL)
BG = {1: '#f3e3c4', 8: '#2a2350', 15: '#3a1420'}
SCALE_LEVELS = (1, 8, 15)


def build_level(n, what='both'):
    """(re)build one level from its scripts; returns stats dicts"""
    out = {}
    db = importlib.import_module('db_%02d' % n)
    importlib.reload(db)
    BG[n] = getattr(db, 'BG', BG.get(n, '#f3e3c4'))
    if what in ('both', 'db'):
        r = bpy.data.objects.get(dbn(n) + '_root')
        if r:
            r.location = (0, 0, 0)
        out['db'] = db.build()
    if what in ('both', 'st'):
        st = importlib.import_module('st_%02d' % n)
        importlib.reload(st)
        r = bpy.data.objects.get(dbn(n) + '_root')
        if r:
            r.location = (0, 0, 0)
        out['st'] = st.build()
    return out


def preview(n, pct=50):
    R = OUT + r"\renders"
    a = render(R + r"\_pv_db_%02d.png" % n, [dbn(n)], direction=(1, -1.6, 0.9), res=(1024, 1024), bg=BG[n], pct=pct, samples=16)
    b = render(R + r"\_pv_st_%02d.png" % n, [stn(n)], direction=(0.2, -1, 0.38), res=(1600, 1000), bg=BG[n], pct=pct, samples=16, margin=1.08)
    return a, b
STEP = 14.0
ST_Y = 16.0


def dbn(n):
    return 'DB_%02d_%s' % (n, ALL[n])


def stn(n):
    return 'ST_%02d_%s' % (n, ALL[n])


def xof(n):
    return (n - 8) * STEP


def mannequin(prefix, x, y, hold=None, face=1):
    """blocky 5-stud dummy. hold = dumbbell collection name -> right arm forward holding it"""
    skin = toon('dummy_skin', '#f2c94c', light='#ffe58a', spec=0.2)
    shirt = toon('dummy_shirt', '#4a90d9', light='#8cc0f5', spec=0.2)
    pants = toon('dummy_pants', '#5a8f3c', light='#8fc46a', spec=0.2)
    dark = toon('dummy_dark', '#2b2b3a', spec=0.0, rim=0.0)
    for sx in (-1, 1):
        box('%s_leg_%d' % (prefix, sx), (0.96, 0.96, 2.0), pants, bev=0.08, loc=(x + sx * 0.5, y, 1.0))
    box(prefix + '_torso', (2.0, 1.0, 2.0), shirt, bev=0.08, loc=(x, y, 3.0))
    box(prefix + '_head', (1.2, 1.2, 1.0), skin, bev=0.2, loc=(x, y, 4.5))
    for sx in (-1, 1):
        box('%s_eye_%d' % (prefix, sx), (0.14, 0.06, 0.26), dark, bev=0.03, bsegs=1, loc=(x + sx * 0.24, y - 0.6, 4.58), ol=0)
    box(prefix + '_smile', (0.5, 0.06, 0.1), dark, bev=0.03, bsegs=1, loc=(x, y - 0.6, 4.25), ol=0)
    box(prefix + '_arm_L', (0.96, 0.96, 2.0), skin, bev=0.08, loc=(x - 1.5, y, 3.0))
    if hold:
        box(prefix + '_arm_R', (0.96, 2.0, 0.96), skin, bev=0.08, loc=(x + 1.5, y - 0.52, 3.5))
        r = place_copy(hold, G.coll, (x + 1.5, y - 1.0, 3.5), (0, 0, 0), 1.0, True, 'held')
        r.parent = G.root
        r.matrix_parent_inverse = Matrix()
    else:
        box(prefix + '_arm_R', (0.96, 0.96, 2.0), skin, bev=0.08, loc=(x + 1.5, y, 3.0))


def layout():
    """put models in two rows, pedestals with numbers, scale dummies"""
    have = [n for n in ALL if (dbn(n) + '_root') in bpy.data.objects and (stn(n) + '_root') in bpy.data.objects]
    LEVELS.clear()
    LEVELS.update({n: ALL[n] for n in have})
    for n in LEVELS:
        bpy.data.objects[dbn(n) + '_root'].location = (0, 0, 0)
        bpy.data.objects[stn(n) + '_root'].location = (0, 0, 0)
    bpy.context.view_layer.update()
    begin('GYM_Stage', ol=0.04)
    ped = toon('pedestal', '#b9b3c9', shade='#6f6a94', light='#e6e2f0', spec=0.3)
    ped2 = toon('pedestal_top', '#f2ead8', spec=0.3)
    num = toon('pedestal_num', '#3a2a50', spec=0.0, rim=0.0)
    info = {}
    for n in LEVELS:
        s = stats(dbn(n))
        x = xof(n)
        half = s['size'][0] / 2
        lathe('ped_%02d' % n, [(0, 0), (0, half * 0.75 + 0.3), (0.12, half * 0.75 + 0.3), (0.2, half * 0.75 + 0.15), (0.68, half * 0.75 + 0.1), (0.8, half * 0.75 + 0.2), (0.8, 0)],
              ped, 20, 'Z', loc=(x, 0, 0), scale=(1.25, 0.8, 1))
        zc = 0.8 - s['min'][2] + 0.06
        for sx in (-1, 1):
            tube('ped_fork_%02d_%d' % (n, sx), [(x + sx * 0.42, 0, 0.8), (x + sx * 0.42, 0, zc - 0.14)], 0.09, ped2, segs=6, ol=0.025)
        text('ped_num_%02d' % n, str(n), 0.5, 0.04, num, loc=(x, -(half * 0.75 + 0.14) * 0.8 - 0.02, 0.44), rot=(90, 0, 0))
        info[n] = zc
    fx(False)
    for n in LEVELS:
        bpy.data.objects[dbn(n) + '_root'].location = (xof(n), 0, info[n])
        bpy.data.objects[stn(n) + '_root'].location = (xof(n), ST_Y, 0)
    # scale dummies: one beside the row, one beside each stand holding that level's dumbbell
    begin('GYM_Mannequin', ol=0.04)
    mannequin('dummy_row', xof(1) - 6.0, 0)
    for n in SCALE_LEVELS:
        begin('GYM_Scale_%02d' % n, ol=0.04)
        mannequin('dummy_%02d' % n, xof(n) - 4.2, ST_Y - 4.6, hold=dbn(n))
    bpy.context.view_layer.update()


def render_all(pct=100, only=None):
    R = OUT + r"\renders"
    out = []
    for n in LEVELS:
        if only and n not in only:
            continue
        low = ALL[n].lower()
        out.append(render(R + r"\db_%02d_%s.png" % (n, low), [dbn(n)], direction=(1, -1.6, 0.9), res=(1024, 1024), bg=BG[n], pct=pct, samples=48))
        out.append(render(R + r"\st_%02d_%s.png" % (n, low), [stn(n)], direction=(0.2, -1, 0.38), res=(1600, 1000), bg=BG[n], pct=pct, samples=48, margin=1.08))
    return out


def render_scale(pct=100):
    R = OUT + r"\renders"
    ps = []
    for n in SCALE_LEVELS:
        p = R + r"\_scale_%02d.png" % n
        render(p, [stn(n), 'GYM_Scale_%02d' % n], direction=(0.35, -1, 0.3), res=(1200, 900), bg=BG[n], pct=pct, samples=32, margin=1.06)
        ps.append(p)
    return stitch(ps, OUT + r"\scale.png")


def silhouettes():
    R = OUT + r"\renders"
    m = bpy.data.materials.get('GYM_Black')
    if m is None:
        m = bpy.data.materials.new('GYM_Black')
        m.use_nodes = True
        nt = m.node_tree
        for nd in list(nt.nodes):
            nt.nodes.remove(nd)
        e = nt.nodes.new('ShaderNodeEmission')
        e.inputs['Color'].default_value = (0, 0, 0, 1)
        o = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(e.outputs[0], o.inputs['Surface'])
    ps = []
    for n in LEVELS:
        p = R + r"\_sil_db_%02d.png" % n
        render(p, [dbn(n)], direction=(0.3, -1, 0.25), res=(512, 384), bg='#ffffff', hide_sub=(dbn(n) + '_FX',), ground=False, override=m, samples=8)
        ps.append(p)
    for n in LEVELS:
        p = R + r"\_sil_st_%02d.png" % n
        render(p, [stn(n)], direction=(0, -1, 0.1), res=(512, 384), bg='#ffffff',
               hide_sub=(stn(n) + '_FX', stn(n) + '_Display'), ground=False, override=m, samples=8)
        ps.append(p)
    return stitch(ps, R + r"\_silhouettes.png", cols=3)


def export_all():
    res = {}
    for n in LEVELS:
        low = ALL[n].lower()
        for kind, name in (('db', dbn(n)), ('st', stn(n))):
            root = bpy.data.objects[name + '_root']
            res[name] = export_glb(name, OUT + r"\export\%s_%02d_%s.glb" % (kind, n, low))
    return res
