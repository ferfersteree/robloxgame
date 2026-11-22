# Check exported GLBs against creatures.json for every finished biome (system Python, no deps).
# python verify_out.py [NN]   - NN limits the output to one biome (checks of global uniqueness still use everything)
import json, struct, glob, os, sys

EXP = r'C:\SpearHuntAssets\fauna'
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_PARTS = {1: 80, 2: 80, 3: 120, 4: 120, 5: 180, 6: 180}
MAX_TRIS = {1: 8000, 2: 8000, 3: 8000, 4: 8000, 5: 8000, 6: 12000}


def glb(path):
    b = open(path, 'rb').read()
    n = struct.unpack('<I', b[12:16])[0]
    return json.loads(b[20:20 + n])


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def main():
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    bad = []
    data = json.load(open(os.path.join(OUT, 'creatures.json'), encoding='utf-8'))
    roster = json.load(open(os.path.join(OUT, 'roster.json'), encoding='utf-8'))
    pairs = {}
    by_biome = {}
    for c in data['creatures']:
        by_biome.setdefault(c['biome'], []).append(c)
        key = (c['method'], c['gesture'])
        errs = []
        if key in pairs:
            errs.append('pair %s duplicates %s' % (key, pairs[key]))
        pairs[key] = c['id']
        j = glb(os.path.join(EXP, c['glb']))
        nodes = {n['name']: n for n in j['nodes']}
        prim = [p for m in j['meshes'] for p in m['primitives']]
        tris = sum(j['accessors'][p['indices']]['count'] // 3 for p in prim)
        segs = [s for s in c['segments'] if not s['fx']]
        zone = {z['hex'] for s in segs for z in s['colors'] if z['hex']}
        if j.get('animations') or j.get('skins') or j.get('textures'):
            errs.append('has animations/skins/textures')
        if not all('TEXCOORD_0' in p['attributes'] for p in prim):
            errs.append('missing UV')
        if tris != c['tris']:
            errs.append('tris %d != json %d' % (tris, c['tris']))
        facs = [m['pbrMetallicRoughness'].get('baseColorFactor', [1, 1, 1, 1]) for m in j['materials']]
        if any('baseColorTexture' in m['pbrMetallicRoughness'] for m in j['materials']):
            errs.append('baked colour texture')
        for hx in zone:
            rgb = [lin(int(hx[i:i + 2], 16) / 255) for i in (1, 3, 5)]
            if not any(all(abs(f[i] - rgb[i]) < 0.01 for i in range(3)) for f in facs):
                errs.append('zone colour %s not a baseColorFactor' % hx)
        if len(zone) < 4:
            errs.append('fewer than 4 colours')
        for s in segs:
            if s['object'] not in nodes:
                errs.append('segment %s missing in glb' % s['object'])
        if any('_fx' in n['name'] for n in j['nodes']):
            errs.append('fx node inside model glb')
        for mk in ('Head', 'Chest', 'Hit'):
            if '%s_%s' % (c['id'], mk) not in nodes:
                errs.append('marker %s missing' % mk)
        if any('rotation' in n or 'scale' in n for n in j['nodes']):
            errs.append('non-rest rotation/scale on a node')
        if c['parts'] < MIN_PARTS[c['rarity']]:
            errs.append('parts %d < %d' % (c['parts'], MIN_PARTS[c['rarity']]))
        if c['tris'] > MAX_TRIS[c['rarity']]:
            errs.append('tris over budget')
        if not (24 <= c['reveal_frames'] <= 45):
            errs.append('reveal %d frames outside 0.8-1.5 s' % c['reveal_frames'])
        if not (30 <= c['idle_frames'] <= 60):
            errs.append('idle %d frames outside 1-2 s' % c['idle_frames'])
        if c['kind'] in ('air', 'water') and not c.get('hover_height'):
            errs.append('flyer / swimmer without hover height')
        # animation sanity
        rk = c['keys']['Reveal'].get('root', {})
        if rk.get('loc') and any(abs(v) > 0.002 for v in rk['loc'][-1][1:4]):
            errs.append('Reveal root does not end at the spot %s' % rk['loc'][-1][1:4])
        if rk.get('scale') and any(abs(v - 1) > 0.002 for v in rk['scale'][-1][1:4]):
            errs.append('Reveal root does not end at scale 1')
        if rk.get('rot') and any(abs(v / 360.0 - round(v / 360.0)) > 0.002 for v in rk['rot'][-1][1:4]):
            errs.append('Reveal root rotation does not end on a full turn')
        for sname, ch in c['keys']['Reveal'].items():
            if sname == 'root':
                continue
            for key2, rest in (('loc', 0.0), ('scale', 1.0)):
                if ch.get(key2) and any(abs(v - rest) > 0.002 for v in ch[key2][-1][1:4]):
                    errs.append('Reveal %s.%s does not end at rest' % (sname, key2))
            if ch.get('rot') and any(abs(v / 360.0 - round(v / 360.0)) > 0.002 for v in ch['rot'][-1][1:4]):
                errs.append('Reveal %s.rot does not end at rest' % sname)
        for sname, ch in c['keys']['Reveal'].items():
            rr = ch.get('rot') or []
            for q0, q1 in zip(rr, rr[1:]):
                # no unwinding: a segment must not spin back by a full turn or more between two keys unless it is a fast spin move
                if sname != 'root' and any(q1[i] - q0[i] <= -360 or q1[i] - q0[i] >= 720 for i in (1, 2, 3)) and q1[0] == c['reveal_frames']:
                    errs.append('Reveal %s unwinds %s -> %s on the last key' % (sname, q0[1:4], q1[1:4]))
        for sname, ch in c['keys']['Idle'].items():
            for key2 in ('loc', 'rot', 'scale'):
                if not ch.get(key2):
                    continue
                a, b = ch[key2][0][1:4], ch[key2][-1][1:4]
                for u, v in zip(a, b):
                    d = abs(u - v)
                    if key2 == 'rot':
                        d = abs(d / 180.0 - round(d / 180.0)) * 180.0 if sname.startswith('fxs_aura') else abs(d / 360.0 - round(d / 360.0)) * 360.0
                    if d > 0.002:
                        errs.append('Idle %s.%s does not loop' % (sname, key2))
                        break
        if any(s['name'] == 'eye_L' for s in segs):
            if 'scale' not in c['keys']['Idle'].get('eye_L', {}) or 'scale' not in c['keys']['Idle'].get('eye_R', {}):
                errs.append('no blink in Idle')
        r = next(x for x in roster['animals'] if x['id'] == c['id'])
        if (r['method'], r['gesture'], r['rarity'], r['biome']) != (c['method'], c['gesture'], c['rarity'], c['biome']):
            errs.append('differs from roster')
        if abs(c['height'] - r['height']) > 0.25 * r['height'] and c['biome'] > 1:
            errs.append('height %.2f far from roster %.2f' % (c['height'], r['height']))
        if only in (None, c['biome']):
            print('%-22s b%02d r%d parts %3d tris %4d mats %2d segs %2d H %5.2f cover %.2f R%d I%d %s' % (
                c['id'], c['biome'], c['rarity'], c['parts'], tris, len(j['materials']), len(segs), c['height'], c['cover_scale'],
                c['reveal_frames'], c['idle_frames'], 'OK' if not errs else 'FAIL: ' + '; '.join(errs)))
        bad += errs
    for bnum, cs in sorted(by_biome.items()):
        errs = []
        if len(cs) != 6:
            errs.append('biome %d has %d animals' % (bnum, len(cs)))
        if len({c['method'] for c in cs}) != len(cs):
            errs.append('biome %d repeats a method' % bnum)
        if len({c['gesture'] for c in cs}) != len(cs):
            errs.append('biome %d repeats a gesture' % bnum)
        if errs:
            print('FAIL: ' + '; '.join(errs))
        bad += errs
    for b in data['bushes']:
        j = glb(os.path.join(EXP, b['glb']))
        mesh_nodes = [n for n in j['nodes'] if 'mesh' in n]
        errs = []
        if len(mesh_nodes) != len(b['segments']):
            errs.append('bush parts %d != %d' % (len(mesh_nodes), len(b['segments'])))
        if j.get('animations'):
            errs.append('bush has animations')
        w, d, h = b['size']
        if not (6 <= w <= 8 and 4 <= h <= 5):
            errs.append('bush size %s outside 6-8 x 4-5' % b['size'])
        if not os.path.exists(os.path.join(EXP, b['fx_glb'])):
            errs.append('bush fx glb missing')
        key = roster['biomes'][str(b['biome'])]['key']
        for rel in (r'shots\biome_%02d_%s.png' % (b['biome'], key), r'biomes\biome_%02d_%s.blend' % (b['biome'], key)):
            if not os.path.exists(os.path.join(OUT, rel)):
                errs.append('missing ' + rel)
        if only in (None, b['biome']):
            print('%-22s parts %d of %d size %s %s' % (b['id'], len(mesh_nodes), b['parts'], b['size'], 'OK' if not errs else 'FAIL: ' + '; '.join(errs)))
        bad += errs
    for rel in ('studs_tile.png', 'reveal_table.md', 'creatures.json', 'roster.json', r'anim\biome_01_reveal.mp4'):
        if not os.path.exists(os.path.join(OUT, rel)):
            bad.append(rel)
            print('MISSING', rel)
    print('RESULT: %s (%d animals, %d bushes, %d unique pairs)' % ('PASS' if not bad else 'FAIL (%d)' % len(bad), len(data['creatures']),
                                                                 len(data['bushes']), len(pairs)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
