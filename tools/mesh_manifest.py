#!/usr/bin/env python3
"""V87: colour/material manifest for the Claude Design GLBs (animals, bushes, spears and their effects).

    python tools/mesh_manifest.py            # writes docs/concepts_v87/roblox/manifest.json

When Roblox imports a GLB through the Open Cloud assets API, every glTF node becomes a Model "<node>_Node" and every
primitive of the node's mesh becomes a grey MeshPart named "<node>", "<node>2", "<node>3"... in primitive order.
The colours are lost, so the bake in Studio recolours each MeshPart from this manifest.

For every GLB (key = file name without .glb) the manifest has a list of parts:
    [meshPartName, "#rrggbb", kind, sizeX, sizeY, sizeZ]
kind is the letter after PBR_ in the material name:
    S = studs surface (gets the studs overlay texture), P / T = plain smooth, N / G = neon glow, A = see-through effect.
Size is the primitive's bounding box in studs (used by the bake to check that the order is right).
"""
from __future__ import annotations

import glob
import json
import os
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\SpearHuntAssets")
OUT = ROOT / "docs/concepts_v87/roblox/manifest.json"


def read_glb(path: str) -> dict:
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    return json.loads(b[20:20 + n])


def srgb(c: float) -> int:
    c = max(0.0, min(1.0, c))
    v = c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return round(v * 255)


def hexcol(f) -> str:
    return "#%02x%02x%02x" % (srgb(f[0]), srgb(f[1]), srgb(f[2]))


def main() -> None:
    out = {}
    files = sorted(glob.glob(str(SRC / "fauna" / "*.glb")) + glob.glob(str(SRC / "spears" / "*.glb")))
    for f in files:
        g = read_glb(f)
        mats = g.get("materials", [])
        acc = g.get("accessors", [])
        parts = []
        for node in g.get("nodes", []):
            if "mesh" not in node:
                continue
            name = node.get("name", "")
            for i, prim in enumerate(g["meshes"][node["mesh"]]["primitives"]):
                m = mats[prim["material"]] if "material" in prim else {"name": "PBR_P_default"}
                mname = m.get("name", "PBR_P_x")
                kind = mname.split("_")[1] if mname.startswith("PBR_") and len(mname.split("_")) > 1 else "P"
                base = m.get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1])
                pos = acc[prim["attributes"]["POSITION"]]
                mn, mx = pos.get("min", [0, 0, 0]), pos.get("max", [0, 0, 0])
                size = [round(mx[k] - mn[k], 3) for k in range(3)]
                parts.append([name if i == 0 else f"{name}{i + 1}", hexcol(base), kind, *size])
        out[os.path.basename(f)[:-4]] = parts
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"{len(out)} files, {sum(len(v) for v in out.values())} parts -> {OUT}")


if __name__ == "__main__":
    main()
