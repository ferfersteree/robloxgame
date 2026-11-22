#!/usr/bin/env python3
"""V87: build the Luau that bakes the uploaded Claude Design GLBs into ReplicatedStorage.Art87 inside Studio.

    python tools/bake87.py OUT.lua key1 key2 ...     # keys = GLB names without .glb (an_rabbit, bush_01, sp_01_stick...)
    python tools/bake87.py OUT.lua --all --from N --count K

The generated code (run it with execute_luau in the Edit datamodel of the local V87 place):
  * InsertService:LoadAsset(assetId) for each key (ids from docs/concepts_v87/roblox/asset_ids.json),
  * takes the imported "SH <key>" model, recolours every MeshPart from manifest.json (colour, kind, size check),
    S parts get a SurfaceAppearance (AlphaMode Overlay) with the studs overlay texture, N/G parts are Neon, A parts are see-through,
  * anchors everything, turns off collisions/queries, keeps the node hierarchy (Model "<node>_Node"),
  * sets WorldPivot to the asset origin and stores it as ReplicatedStorage.Art87.<Folder>.<key>:
      an_*  -> Animals,  fx_<animal|bush_NN> -> FX,  bush_* -> Bushes,  sp_NN_id -> Spears,  sp_NN_id_fx_* -> SpearFX.
It returns one line per key: ok / size mismatches / load errors.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "docs/concepts_v87/roblox"
STUDS_TEXTURE = "rbxassetid://79283429423267"  # docs/concepts_v87/roblox/studs_overlay.png


def folder(key: str) -> str:
    if key.startswith("an_"):
        return "Animals"
    if key.startswith("bush_"):
        return "Bushes"
    if key.startswith("fx_"):
        return "FX"
    if re.match(r"^sp_\d+_.*_fx_", key):
        return "SpearFX"
    return "Spears"


def main() -> None:
    out = sys.argv[1]
    args = sys.argv[2:]
    ids = json.loads((D / "asset_ids.json").read_text(encoding="utf-8"))
    man = json.loads((D / "manifest.json").read_text(encoding="utf-8"))
    if args and args[0] == "--all":
        start = int(args[args.index("--from") + 1]) if "--from" in args else 0
        count = int(args[args.index("--count") + 1]) if "--count" in args else 10 ** 9
        keys = sorted(k for k in man if k in ids)[start:start + count]
    else:
        keys = args
    specs = []
    for k in keys:
        if k not in ids or k not in man:
            print("skip (no id or manifest):", k)
            continue
        parts = ",".join('{"%s",%s,"%s",%.3f,%.3f,%.3f}' % (p[0], "0x" + p[1][1:], p[2], p[3], p[4], p[5]) for p in man[k])
        specs.append('{k="%s",id=%s,f="%s",p={%s}}' % (k, ids[k], folder(k), parts))
    lua = LUA.replace("--SPECS--", ",\n".join(specs)).replace("--TEX--", STUDS_TEXTURE)
    Path(out).write_text(lua, encoding="utf-8")
    print(f"{len(specs)} keys -> {out} ({len(lua)} chars)")


LUA = r'''
local RS = game:GetService("ReplicatedStorage")
local IS = game:GetService("InsertService")
local root = RS:FindFirstChild("Art87") or Instance.new("Folder")
root.Name = "Art87"
root.Parent = RS
local function sub(name)
	local f = root:FindFirstChild(name)
	if not f then f = Instance.new("Folder") f.Name = name f.Parent = root end
	return f
end
local SPECS = {
--SPECS--
}
local log = {}
for _, s in SPECS do
	local ok, res = pcall(function() return IS:LoadAsset(s.id) end)
	if not ok then table.insert(log, s.k .. " LOAD " .. tostring(res)) continue end
	local m = res:FindFirstChildWhichIsA("Model")
	if not m then table.insert(log, s.k .. " no model") res:Destroy() continue end
	local byName = {}
	for _, p in s.p do byName[p[1]] = p end
	local bad, n, miss = 0, 0, 0
	for _, d in m:GetDescendants() do
		if d:IsA("MeshPart") then
			n += 1
			local p = byName[d.Name]
			if p then
				local sz = d.Size
				local a = { p[4], p[5], p[6] }
				table.sort(a)
				local b = { sz.X, sz.Y, sz.Z }
				table.sort(b)
				if math.abs(a[1] - b[1]) + math.abs(a[2] - b[2]) + math.abs(a[3] - b[3]) > 0.08 then bad += 1 end
				d.Color = Color3.fromHex(string.format("%06x", p[2]))
				local kind = p[3]
				if kind == "N" or kind == "G" then
					d.Material = Enum.Material.Neon
					d.CastShadow = false
				elseif kind == "A" then
					d.Material = Enum.Material.SmoothPlastic
					d.Transparency = 0.35
					d.CastShadow = false
				else
					d.Material = Enum.Material.SmoothPlastic
					d.CastShadow = true
				end
				if kind == "S" then
					-- шипы: прозрачная картинка поверх цвета детали (TextureID давал чёрный цвет)
					local sa = Instance.new("SurfaceAppearance")
					sa.AlphaMode = Enum.AlphaMode.Overlay
					sa.ColorMap = "--TEX--"
					sa.Parent = d
				end
				d:SetAttribute("Kind", kind)
			else
				miss += 1
			end
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.Massless = true
		end
	end
	m.Name = s.k
	m.WorldPivot = CFrame.new()
	m:SetAttribute("AssetId", s.id)
	local dest = sub(s.f)
	local old = dest:FindFirstChild(s.k)
	if old then old:Destroy() end
	m.Parent = dest
	res:Destroy()
	table.insert(log, string.format("%s ok parts=%d bad=%d miss=%d", s.k, n, bad, miss))
end
return table.concat(log, "\n")
'''

if __name__ == "__main__":
    main()
