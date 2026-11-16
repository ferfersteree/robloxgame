"""World of SpearHunt_World_v15.html -> Lua data modules for the in-game streamer (V37).

Usage:  python -I -X utf8 tools/html_world_build.py <world_data.bin> <out_dir>
  world_data.bin  the 24.8 MB JSON that the HTML keeps gzip+base64 inside its second <script>
                  (window.WORLD_DATA_READY=...atob("...")): base64 -> gzip.decompress -> save as world_data.bin.
  out_dir         e.g. source/ReplicatedStorage/HtmlWorld  (Protos.luau, Index.luau, Zxx.luau are written there)

What it does (all rules ported from the HTML's own scripts):
  * placements (14 412 plants / trees / rocks / crystals) -> model id (modelIdFor), scale (quarter steps, clamped),
    yaw = (digits of the id mod 4) * 90 degrees;
  * every (model, scale) becomes ONE prototype: the voxel cells (0.5 stud) are coarsened by the smallest block size k
    that keeps the prototype under a box budget, then merged into boxes (tools/vox2boxes.merge);
  * the 75 hero models of the 25 zones (structure / canopy / feature) and the 18 landmark models are unique entries;
  * everything is put on the game's own flat ground (top y = 0.1), z is shifted by ForestOriginZ (-3);
  * placements are dropped when they sit on the existing map: zones 17-18 (the game has a narrow sky path there),
    outside the ground, on safe camps / landmarks / streams / signs / stepped rocks, near animal spawn pockets
    (tools/html_world_keepout.txt, read from the open place by Studio), or inside a hero / landmark footprint.
The Roblox side (Client/HtmlWorld) builds parts only around the camera, so the part count stays small.
"""
import collections
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vox2boxes import merge, quant  # noqa: E402

CELL = 0.5
ZSHIFT = -3.0            # Biome ForestOriginZ: world z = -3 - distance
GROUND_Y = 0.1           # top of every Biome Ground
SKIP_ZONES = {17, 18}    # the game has a 24 stud wide sky path there, the HTML flora would hang in the air
CLASS_OF_CAT = {"tree": 1, "decor": 2, "crystal": 2, "bush": 3, "ground": 3, "coral": 3}
BUDGET_CAT = {"tree": 56, "crystal": 20, "decor": 14, "bush": 12, "coral": 12, "ground": 6}
BUDGET_HERO = 420
BUDGET_LANDMARK = 220
HERO_QSTEP = 48
LM_QSTEP = 32

widths = [190, 194, 202, 220, 238, 234, 240, 250, 256, 246, 276, 296, 260, 264, 244, 268, 276, 270, 284, 286, 302, 290, 320, 304, 320]


def js_round(x):
    return math.floor(x + 0.5)


M32 = 0xFFFFFFFF


def rng(seed):
    s = [seed & M32]

    def r():
        x = s[0]
        x ^= (x << 13) & M32
        x ^= x >> 17
        x ^= (x << 5) & M32
        s[0] = x
        return x / 4294967296
    return r


def load_world(path):
    return json.load(open(path, encoding="utf-8"))


def model_id_for(p, models):
    z, t, a = p["zone"], p["type"], p.get("args") or []
    a0 = a[0] if a else None
    if t == "birch":
        i = "snow_birch" if a0 else "birch"
    elif t == "pine":
        i = "snow_pine" if a0 else "pine"
    elif t == "broadleaf":
        i = "acacia" if a0 == "acacia" else "jungle_tree" if a0 == "jungle" else "cloud_tree" if z == 17 else "oak"
    elif t == "palm":
        i = "palm"
    elif t == "mangrove":
        i = "mangrove"
    elif t == "deadTree":
        i = "shadow_tree" if z >= 18 else "dead_tree"
    elif t == "shrub":
        i = ("savanna_bush" if z == 5 else "mountain_bush" if z == 6 else "dune_bush" if z == 7 else "jungle_bush" if z == 8
             else "marsh_bush" if z == 9 else "mountain_bush" if z == 10 else "dry_roots" if z == 13 else "frost_bush" if z == 16
             else "shadow_bush" if z == 18 else "star_bush" if z == 19 else "berry_bush" if a0 else "forest_bush" if z in (2, 3) else "bush")
    elif t == "grass":
        i = ("cloud_grass" if z == 17 else "snow_flower" if z in (4, 16) else "shadow_bush" if z == 18 else "star_bush" if z == 19
             else "dune_bush" if z == 7 else "savanna_bush" if z == 5 else "flower" if a0 else "grass")
    elif t == "fern":
        i = "fern"
    elif t == "reed":
        i = "reed"
    elif t == "mushroom":
        i = "glow_mushroom" if z == 18 else "mushroom"
    elif t == "crystal":
        i = ("ember_crystal" if z == 14 else "amethyst_cluster" if z in (15, 18) else "ice_cluster" if z == 16
             else "star_crystal" if z == 19 else "quartz_cluster")
    elif t == "coral":
        n = int(re.sub(r"\D", "", p["id"]) or 0)
        i = ["branch_coral", "fan_coral", "table_coral", "tube_coral"][n % 4]
    elif t == "seagrass":
        i = "seagrass"
    elif t == "log":
        i = "snow_log" if z == 4 else "charred_log" if z == 13 else "moss_log"
    elif t == "rock":
        i = "sandstone_rock" if z in (6, 7) else "basalt_rock" if z in (13, 14) else "ice_rock" if z in (4, 16) else "shell_cluster" if z == 11 else "rock"
    else:
        i = t
    if i not in models:
        alt = {"cloud_grass": "grass", "snow_birch": "birch", "forest_bush": "bush", "snow_flower": "flower",
               "glow_mushroom": "mushroom", "shell_cluster": "rock"}
        i = alt.get(i, i)
    return i if i in models else None


def factor_for(p, m):
    height = (m.get("bounds") or {}).get("size", [0, 1, 0])[1] or 1
    b = p.get("bounds") or {}
    try:
        target = b["max"][1] - b["min"][1]
    except Exception:
        target = None
    f = (target / height) if target is not None and math.isfinite(target) else 1
    cat = m.get("category")
    rg = (0.75, 2 if p.get("landmark") else 1.5) if cat == "tree" else (0.25, 1.75) if cat == "decor" else (0.5, 1.5)
    return max(rg[0], min(rg[1], js_round(f * 4) / 4))


def resample(model, factor):
    """The HTML's resampleModel: keeps cells 0.5 cubes while scaling the model. -> [(ix,iy,iz,colour)]"""
    if abs(factor - 1) < 0.001:
        return [(v[0], v[1], v[2], v[3]) for v in model["voxels"]]
    o = model.get("origin") or [0, 0.25, 0]
    vmap = {(v[0], v[1], v[2]): v for v in model["voxels"]}
    b = model.get("bounds") or {}
    mn = b.get("min", [0, 0, 0])
    mx = b.get("max", [0, 1, 0])
    low = [math.floor((mn[i] * factor - o[i]) / CELL) - 1 for i in range(3)]
    high = [math.ceil((mx[i] * factor - o[i]) / CELL) + 1 for i in range(3)]
    out = []
    for x in range(low[0], high[0] + 1):
        ix = js_round(((x * CELL + o[0]) / factor - o[0]) / CELL)
        for y in range(low[1], high[1] + 1):
            iy = js_round(((y * CELL + o[1]) / factor - o[1]) / CELL)
            for z in range(low[2], high[2] + 1):
                iz = js_round(((z * CELL + o[2]) / factor - o[2]) / CELL)
                v = vmap.get((ix, iy, iz))
                if v:
                    out.append((x, y, z, v[3]))
    return out


def coarsen(vox, k, qstep):
    if k == 1 and not qstep:
        return [[a, b, c, col, 0] for a, b, c, col in vox]
    blocks = collections.defaultdict(collections.Counter)
    for a, b, c, col in vox:
        if qstep:
            r, g, bl = quant(col, qstep)
            col = (r << 16) | (g << 8) | bl
        blocks[(a // k, b // k, c // k)][col] += 1
    return [[bx, by, bz, cnt.most_common(1)[0][0], 0] for (bx, by, bz), cnt in blocks.items()]


def boxes_for(vox, origin, ks, budget, qstep=0):
    """Smallest block size from ks whose merged box count fits the budget. -> (k, [boxes in quarter studs], radius)"""
    chosen = None
    for k in ks:
        cells = coarsen(vox, k, qstep)
        boxes = merge(cells, 1)
        chosen = (k, boxes)
        if len(boxes) <= budget:
            break
    k, boxes = chosen
    out = []
    rmax = 0.0
    xmn = zmn = 1e9
    xmx = zmx = -1e9
    for x0, y0, z0, x1, y1, z1, col in boxes:
        xmin = (x0 * k) * CELL + origin[0] - CELL / 2
        xmax = (x1 * k + k - 1) * CELL + origin[0] + CELL / 2
        ymin = (y0 * k) * CELL + origin[1] - CELL / 2
        ymax = (y1 * k + k - 1) * CELL + origin[1] + CELL / 2
        zmin = (z0 * k) * CELL + origin[2] - CELL / 2
        zmax = (z1 * k + k - 1) * CELL + origin[2] + CELL / 2
        out.append((round((xmin + xmax) * 2), round((ymin + ymax) * 2), round((zmin + zmax) * 2),
                    round((xmax - xmin) * 4), round((ymax - ymin) * 4), round((zmax - zmin) * 4),
                    (col[0] << 16) | (col[1] << 8) | col[2]))
        xmn, xmx, zmn, zmx = min(xmn, xmin), max(xmx, xmax), min(zmn, zmin), max(zmx, zmax)
        rmax = max(rmax, math.hypot(max(abs(xmin), abs(xmax)), max(abs(zmin), abs(zmax))))
    return k, out, rmax, (xmn, xmx, zmn, zmx)


def parse_keepout(path):
    rects, pockets, grounds = [], [], {}
    mode = None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line in ("FOOTPRINTS", "POCKETS", "GROUNDS"):
            mode = line
            continue
        f = line.split("|")
        if mode == "FOOTPRINTS":
            zone, name, x0, x1, z0, z1 = int(f[0]), f[1], float(f[2]), float(f[3]), float(f[4]), float(f[5])
            if name == "Water Volume":
                continue  # flora belongs under water
            rects.append((zone, name, x0, x1, z0, z1))
        elif mode == "POCKETS":
            pockets.append((int(f[0]), float(f[1]), float(f[2]), float(f[3])))
        elif mode == "GROUNDS":
            grounds[int(f[0])] = (float(f[1]), float(f[2]), float(f[3]), float(f[4]))
    return rects, pockets, grounds


def circle_hits_rect(cx, cz, r, rect):
    x0, x1, z0, z1 = rect
    dx = max(x0 - cx, 0, cx - x1)
    dz = max(z0 - cz, 0, cz - z1)
    return dx * dx + dz * dz < r * r


def main():
    world_path, out_dir = sys.argv[1], sys.argv[2]
    d = load_world(world_path)
    cat = d["VOXEL_CATALOG"]
    models = {m["id"]: m for m in cat["models"]}
    placements = d["VOXEL_PLACEMENTS"]["placements"]
    zones = {z["id"]: z for z in d["WORLD_CATALOG"]["zones"]}
    env = {m["id"]: m for m in d["ENVIRONMENT_MODELS"]["models"]}
    landmark_models = d["VOXEL_PLACEMENTS"]["landmarkModels"]
    rects, pockets, grounds = parse_keepout(os.path.join(HERE, "html_world_keepout.txt"))
    print("keep-out rects", len(rects), "pockets", len(pockets), "grounds", len(grounds))

    # ---- unique entries: heroes + landmarks, per zone ------------------------------------------------------------
    unique = collections.defaultdict(list)   # zone -> [dict(cls,id,x,z,boxes,aabb)]
    uniq_drop = collections.Counter()
    for zid in range(1, 26):
        if zid in SKIP_ZONES:
            continue
        z = zones[zid]
        w = widths[zid - 1]
        start, end = z["from"], z["to"]
        length = end - start
        r = rng(13069 + zid * 593)
        for kind, sx, u in (("structure", -.33, .24), ("canopy", .31, .5), ("feature", -.29, .76)):
            x = w * sx + (r() - .5) * 10
            zz = -(start + length * max(.1, min(.9, u + (r() - .5) * .32)))
            m = env["env_%02d_%s" % (zid, kind)]
            vox = [(v[0], v[1], v[2], v[3]) for v in m["voxels"]]
            o = m.get("origin") or [0, 0.25, 0]
            k, boxes, rad, bb = boxes_for(vox, o, (2, 3, 4), BUDGET_HERO, HERO_QSTEP)
            wz = zz + ZSHIFT
            aabb = (x + bb[0], x + bb[1], wz + bb[2], wz + bb[3])
            hit = None
            g = grounds[zid]
            if aabb[0] < g[0] + 1 or aabb[1] > g[1] - 1 or aabb[2] < g[2] + 1 or aabb[3] > g[3] - 1:
                hit = "edge"
            for rc in rects:
                if rc[0] == zid and not (aabb[1] < rc[2] or aabb[0] > rc[3] or aabb[3] < rc[4] or aabb[2] > rc[5]):
                    hit = "map:" + rc[1]
            for pk in pockets:
                if pk[0] == zid and circle_hits_rect(pk[1], pk[2], 4.0, aabb):
                    hit = "pocket"
            if hit:
                uniq_drop["hero " + hit] += 1
                continue
            unique[zid].append({"cls": 4, "id": m["id"], "x": x, "z": wz, "boxes": boxes, "aabb": aabb, "k": k})
    for m in landmark_models:
        zid = m["zone"]
        if zid in SKIP_ZONES:
            continue
        vox = [(v[0], v[1], v[2], v[3]) for v in m["voxels"]]
        o = m.get("origin") or [0, 0.25, 0]
        k, boxes, rad, bb = boxes_for(vox, o, (2, 3, 4), BUDGET_LANDMARK, LM_QSTEP)
        x, wz = m["position"][0], m["position"][2] + ZSHIFT
        aabb = (x + bb[0], x + bb[1], wz + bb[2], wz + bb[3])
        hit = None
        g = grounds[zid]
        if aabb[0] < g[0] + 1 or aabb[1] > g[1] - 1 or aabb[2] < g[2] + 1 or aabb[3] > g[3] - 1:
            hit = "edge"
        for rc in rects:
            if rc[0] == zid and not (aabb[1] < rc[2] or aabb[0] > rc[3] or aabb[3] < rc[4] or aabb[2] > rc[5]):
                hit = "map:" + rc[1]
        if hit:
            uniq_drop["landmark " + hit] += 1
            continue
        unique[zid].append({"cls": 5, "id": m["id"], "x": x, "z": wz, "boxes": boxes, "aabb": aabb, "k": k})
    print("unique entries:", sum(len(v) for v in unique.values()), "dropped:", dict(uniq_drop))

    # ---- flora prototypes + placements ----------------------------------------------------------------------------
    protos = []          # [id, class, boxes, radius]
    proto_of = {}
    flora = collections.defaultdict(list)    # zone -> [(code, x, z)]
    drop = collections.Counter()
    ks_hist = collections.Counter()
    for p in placements:
        zid = p["zone"]
        if zid in SKIP_ZONES:
            drop["zone 17/18"] += 1
            continue
        mid = model_id_for(p, models)
        if not mid:
            drop["no model"] += 1
            continue
        m = models[mid]
        f = factor_for(p, m)
        key = (mid, f, bool(p.get("landmark")))
        if key not in proto_of:
            vox = resample(m, f)
            if not vox:
                proto_of[key] = None
            else:
                catg = m.get("category")
                k, boxes, rad, _ = boxes_for(vox, m.get("origin") or [0, 0.25, 0], (1, 2, 3, 4, 5, 6, 8), BUDGET_CAT.get(catg, 8))
                cls = 5 if p.get("landmark") else CLASS_OF_CAT.get(catg, 3)
                ks_hist[(catg, k)] += 1
                proto_of[key] = len(protos)
                protos.append(["%s_%s" % (mid, f), cls, boxes, rad])
        idx = proto_of[key]
        if idx is None:
            drop["empty"] += 1
            continue
        x, wz = p["position"][0], p["position"][2] + ZSHIFT
        rad = protos[idx][3]
        g = grounds[zid]
        if not (g[0] + 1 <= x <= g[1] - 1 and g[2] + 1 <= wz <= g[3] - 1):
            drop["off ground"] += 1
            continue
        bad = None
        for rc in rects:
            if rc[0] == zid and circle_hits_rect(x, wz, rad * 0.7 + 2, (rc[2], rc[3], rc[4], rc[5])):
                bad = "map"
                break
        if not bad:
            for pk in pockets:
                if pk[0] == zid and math.hypot(x - pk[1], wz - pk[2]) < rad * 0.7 + 7:
                    bad = "pocket"
                    break
        if not bad:
            for e in unique.get(zid, ()):
                if circle_hits_rect(x, wz, rad * 0.5, (e["aabb"][0] - 1.5, e["aabb"][1] + 1.5, e["aabb"][2] - 1.5, e["aabb"][3] + 1.5)):
                    bad = "hero"
                    break
        if bad:
            drop[bad] += 1
            continue
        yaw = 0 if p.get("landmark") else (int(re.sub(r"\D", "", p["id"]) or 0) % 4)
        flora[zid].append((idx * 4 + yaw, round(x * 10), round(wz * 10)))
    print("flora placements kept:", sum(len(v) for v in flora.values()), "dropped:", dict(drop))
    print("prototypes:", len(protos), "boxes total:", sum(len(p[2]) for p in protos))
    print("block sizes used (category,k):prototypes:", dict(sorted(ks_hist.items())))

    # ---- write Lua --------------------------------------------------------------------------------------------------
    os.makedirs(out_dir, exist_ok=True)
    head = ("-- ReplicatedStorage/HtmlWorld/%s\n-- Generated by tools/html_world_build.py from SpearHunt_World_v15.html (V37). Do not edit by hand.\n")

    def box_list(boxes):
        return ",".join(",".join(str(n) for n in b) for b in boxes)

    with open(os.path.join(out_dir, "Protos.luau"), "w", encoding="utf-8", newline="\n") as f:
        f.write(head % "Protos")
        f.write("-- { id, class, boxes }: class 1 tree, 2 rock/crystal, 3 ground cover, 5 landmark-sized plant.\n")
        f.write("-- boxes is a flat list, 7 numbers per box: cx, cy, cz, sx, sy, sz in quarter studs (pivot = bottom centre), colour as 0xRRGGBB integer.\n")
        f.write("return {\n")
        for pid, cls, boxes, _ in protos:
            f.write('{"%s",%d,{%s}},\n' % (pid, cls, box_list(boxes)))
        f.write("}\n")
    index = []
    for zid in range(1, 26):
        if zid in SKIP_ZONES:
            continue
        z = zones[zid]
        fl, un = flora.get(zid, []), unique.get(zid, [])
        index.append((zid, z["from"], z["to"], len(fl), len(un)))
        with open(os.path.join(out_dir, "Z%02d.luau" % zid), "w", encoding="utf-8", newline="\n") as f:
            f.write(head % ("Z%02d" % zid))
            f.write("-- v: flat list of 3 numbers per plant: code = prototype index * 4 + yaw quarter turns (index 0 based), x and z in tenth studs.\n")
            f.write("-- u: unique models (hero buildings and landmarks): { class, id, x, z (tenth studs), boxes }.\n")
            f.write("return {\nv={")
            f.write(",".join("%d,%d,%d" % t for t in fl))
            f.write("},\nu={\n")
            for e in un:
                f.write('{%d,"%s",%d,%d,{%s}},\n' % (e["cls"], e["id"], round(e["x"] * 10), round(e["z"] * 10), box_list(e["boxes"])))
            f.write("}\n}\n")
    with open(os.path.join(out_dir, "Index.luau"), "w", encoding="utf-8", newline="\n") as f:
        f.write(head % "Index")
        f.write("-- { zone, from, to (distance, studs), plants, unique models }; world z = -3 - distance\n")
        f.write("return {\n")
        for row in index:
            f.write("{%d,%d,%d,%d,%d},\n" % row)
        f.write("}\n")
    sizes = {n: os.path.getsize(os.path.join(out_dir, n)) for n in sorted(os.listdir(out_dir))}
    print("files:", sizes, "total bytes", sum(sizes.values()))

    # ---- live part simulation (chunk level, like the streamer) ----------------------------------------------------
    CHUNK = 70
    RAD = {1: 260, 2: 200, 3: 100, 4: 420, 5: 600}   # keep equal to RADIUS in Client/HtmlWorld
    chunks = collections.defaultdict(int)   # (cz, cls) -> parts
    for zid, lst in flora.items():
        for code, x10, z10 in lst:
            pr = protos[code // 4]
            chunks[(int(-(z10 / 10) // CHUNK), pr[1])] += len(pr[2])
    for zid, lst in unique.items():
        for e in lst:
            chunks[(int(-e["z"] // CHUNK), e["cls"])] += len(e["boxes"])
    live = []
    for camz in range(0, 12700, 25):
        total = 0
        by_cls = collections.Counter()
        for (cz, cls), n in chunks.items():
            zlo, zhi = -(cz + 1) * CHUNK, -cz * CHUNK
            dz = zlo - (-camz) if -camz < zlo else (-camz) - zhi if -camz > zhi else 0
            if dz <= RAD[cls]:
                total += n
                by_cls[cls] += n
        live.append((total, camz, dict(by_cls)))
    live.sort(key=lambda t: t[0])
    tot = [t[0] for t in live]
    print("live parts around a camera on the lane: avg %d, p50 %d, p90 %d, p99 %d, max %d" % (
        sum(tot) / len(tot), tot[len(tot) // 2], tot[int(len(tot) * .9)], tot[int(len(tot) * .99)], tot[-1]))
    for t in live[-5:]:
        print("   peak at z=-%d: %d parts, by class %s" % (t[1], t[0], t[2]))
    print("parts per class (all zones):", {c: sum(n for (cz, cl), n in chunks.items() if cl == c) for c in (1, 2, 3, 4, 5)})


if __name__ == "__main__":
    main()
