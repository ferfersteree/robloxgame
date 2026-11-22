#!/usr/bin/env python3
"""V87: convert docs/concepts_v87/creatures.json (Claude Design, Blender axes) into Luau data modules for the game.

    python tools/art87_data.py      # writes source/ReplicatedStorage/Art87/Data/B01.luau .. B25.luau

Axes. Blender: Z up, animals face -Y. Roblox imports the GLBs turned 180 degrees about Y, so a Blender point
(x, y, z) is Roblox (-x, z, y) and animals face -Z (the default LookVector). Everything written here is already in
Roblox axes:
  * position / joint / loc offset  (x, y, z)  -> (-x, z, y)
  * Euler XYZ degrees (a, b, c), Blender R = Rz(c) Ry(b) Rx(a)  -> Roblox R = Angles(0, c, 0) * Angles(0, 0, b) * Angles(-a, 0, 0)
    stored as {rx = -a, ry = c, rz = b} in radians, applied in the order Y, Z, X (see Art87.luau euler()).
  * scale (sx, sy, sz) -> (sx, sz, sy)

Track format (one per channel): flat array {frame, v1, v2, v3, interp, frame, ...} with interp 0 = constant,
1 = linear, 2 = ease (Blender bezier "B"). glow tracks: {frame, value, frame, value...}. fx alpha: {frame, a...}. Light fx (mat "light"): energy = {frame, brightness...}.

Module layout (B<NN>.luau):
  return {
    bush = { id, size, cover, frames = {Tease_Common=..}, epicGlow = {[5]=hex,[6]=hex},
             segs = { {name, object, parent(index or 0), jx, jy, jz}, ... }, clips = { Tease_Common = { [segIndex] = {loc=, rot=, scale=}, root = {...} } },  -- root = whole model
             fx = { {name, group, base, sx, sy, sz, color, mat, loc=, scale=, rot=, alpha=}, ... } },
    animals = { [id] = { rarity, kind, height, length, width, hover, cover, method, gesture, open, dist, revealFrames, idleFrames,
                         markers = {Head = {x,y,z}, ...}, segs, clips = {Reveal=, Idle=}, glow = {Idle = {[segIndex] = track}}, fx } },
  }
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs/concepts_v87/creatures.json"
OUT = ROOT / "source/ReplicatedStorage/Art87/Data"
INTERP = {"C": 0, "L": 1, "B": 2}
R = math.pi / 180


def n(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pos(p):
    return (-p[0], p[2], p[1])


def track_loc(keys):
    out = []
    for k in keys:
        x, y, z = pos(k[1:4])
        out += [k[0], x, y, z, INTERP.get(k[4] if len(k) > 4 else "B", 2)]
    return out


def track_rot(keys):
    out = []
    for k in keys:
        a, b, c = k[1] * R, k[2] * R, k[3] * R
        out += [k[0], -a, c, b, INTERP.get(k[4] if len(k) > 4 else "B", 2)]  # rx, ry, rz
    return out


def track_scale(keys):
    out = []
    for k in keys:
        out += [k[0], k[1], k[3], k[2], INTERP.get(k[4] if len(k) > 4 else "B", 2)]
    return out


def lua_arr(a) -> str:
    return "{" + ",".join(n(x) if isinstance(x, (int, float)) else json.dumps(x) for x in a) + "}"


def segs_lua(segs):
    index = {s["name"]: i + 1 for i, s in enumerate(segs)}
    rows = []
    for s in segs:
        jx, jy, jz = pos(s["joint"])
        rows.append('{"%s","%s",%d,%s,%s,%s}' % (s["name"], s["object"], index.get(s["parent"], 0), n(jx), n(jy), n(jz)))
    return "{" + ",".join(rows) + "}", index


def clips_lua(keys, index):
    parts = []
    for clip, per in keys.items():
        tr = []
        for seg, ch in per.items():
            if seg not in index and seg != "root":
                continue
            fields = []
            if "loc" in ch:
                fields.append("loc=" + lua_arr(track_loc(ch["loc"])))
            if "rot" in ch:
                fields.append("rot=" + lua_arr(track_rot(ch["rot"])))
            if "scale" in ch:
                fields.append("scale=" + lua_arr(track_scale(ch["scale"])))
            tr.append(("root={%s}" if seg == "root" else "[%d]={%%s}" % index[seg]) % ",".join(fields))
        parts.append("%s={%s}" % (clip, ",".join(tr)))
    return "{" + ",".join(parts) + "}"


def fx_lua(fx):
    rows = []
    for f in fx:
        if "light" in f:  # point light of epic bushes: energy in Blender watts, PointLight brightness = energy / 400
            col = "#%02x%02x%02x" % tuple(round(255 * max(0, min(1, v)) ** (1 / 2.2)) for v in f["light"]["color"])
            extra = ["loc=" + lua_arr([v for k in f["loc"] for v in (k[0], *pos(k[1:4]), 1)])]
            extra.append("energy=" + lua_arr([v for k in f.get("energy_keys", []) for v in (k[0], k[1] / 400)]))
            rows.append("{" + ",".join(['"%s"' % f["name"], '"%s"' % f.get("group", ""), '"light"', "0", "0", "0",
                                        '"%s"' % col, '"light"'] + extra) + "}")
            continue
        base = f["name"].rsplit("_", 1)[0] if f["name"].rsplit("_", 1)[-1].isdigit() else f["name"]
        sx, sy, sz = f["size"][0], f["size"][2], f["size"][1]
        fields = ['"%s"' % f["name"], '"%s"' % f.get("group", ""), '"%s"' % base, n(sx), n(sy), n(sz),
                  '"%s"' % f["color"], '"%s"' % f["material"]]
        extra = []
        if f.get("loc"):
            extra.append("loc=" + lua_arr([v for k in f["loc"] for v in (k[0], *pos(k[1:4]), 1)]))
        if f.get("scale"):
            extra.append("scale=" + lua_arr([v for k in f["scale"] for v in (k[0], k[1], k[3], k[2], 1)]))
        if f.get("rot"):
            extra.append("rot=" + lua_arr([v for k in f["rot"] for v in (k[0], -k[1] * R, k[3] * R, k[2] * R, 1)]))
        if f.get("alpha"):
            extra.append("alpha=" + lua_arr([v for k in f["alpha"] for v in (k[0], k[1])]))
        rows.append("{" + ",".join(fields + extra) + "}")
    return "{" + ",\n".join(rows) + "}"


def glow_lua(glow, index):
    parts = []
    for clip, per in glow.items():
        tr = []
        for seg, keys in per.items():
            if seg in index:
                tr.append("[%d]=%s" % (index[seg], lua_arr([v for k in keys for v in k])))
        parts.append("%s={%s}" % (clip, ",".join(tr)))
    return "{" + ",".join(parts) + "}"


def main() -> None:
    c = json.loads(SRC.read_text(encoding="utf-8"))
    bushes = {b["biome"]: b for b in c["bushes"]}
    by_biome: dict[int, list] = {}
    for cr in c["creatures"]:
        by_biome.setdefault(cr["biome"], []).append(cr)
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for biome in sorted(by_biome):
        b = bushes[biome]
        segs, idx = segs_lua(b["segments"])
        eg = ",".join('[%s]="%s"' % (k, v) for k, v in b.get("epic_glow", {}).items())
        frames = ",".join("%s=%d" % (k, v) for k, v in b["durations_frames"].items())
        sx, sy, sz = b["size"][0], b["size"][2], b["size"][1]
        lines = [f"-- V87 data for biome {biome}: bush and animals by Claude Design (generated by tools/art87_data.py, do not edit)",
                 "return {",
                 f'bush={{id="{b["id"]}",size={{{n(sx)},{n(sy)},{n(sz)}}},frames={{{frames}}},epicGlow={{{eg}}},',
                 f"segs={segs},", f"clips={clips_lua(b['keys'], idx)},", f"fx={fx_lua(b['fx'])}}},", "animals={"]
        for cr in by_biome[biome]:
            segs, idx = segs_lua(cr["segments"])
            mk = ",".join("%s={%s,%s,%s}" % (k, *map(n, pos(v))) for k, v in cr["markers"].items())
            lines.append(
                f'["{cr["id"]}"]={{rarity={cr["rarity"]},kind="{cr["kind"]}",height={n(cr["height"])},length={n(cr["length"])},'
                f'width={n(cr["width"])},hover={n(cr.get("hover_height", 0))},cover={n(cr.get("cover_scale", 1))},'
                f'method="{cr.get("method", "")}",gesture="{cr.get("gesture", "")}",open="{cr.get("bush_open", "Open_Part")}",'
                f'dist={n(cr.get("bush_distance", 2))},revealFrames={cr["reveal_frames"]},idleFrames={cr["idle_frames"]},'
                f"markers={{{mk}}},segs={segs},clips={clips_lua(cr['keys'], idx)},glow={glow_lua(cr.get('glow', {}), idx)},"
                f"fx={fx_lua(cr['fx'])}}},")
        lines += ["}", "}", ""]
        text = "\n".join(lines)
        (OUT / f"B{biome:02d}.luau").write_text(text, encoding="utf-8")
        total += len(text)
    print(f"{len(by_biome)} modules, {total // 1024} KB -> {OUT}")


if __name__ == "__main__":
    main()
