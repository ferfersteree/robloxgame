local M = "../merge/"
local S150 = "../src150/ReplicatedStorage/Animation150/"
local env = setmetatable({}, { __index = _G })
env._G = env
local warnings = {}
env.warn = function(...) local t = {}; for i = 1, select("#", ...) do t[#t+1] = tostring((select(i, ...))) end; warnings[#warnings+1] = table.concat(t, " ") end
env.task = { wait = function() end, spawn = function(f, ...) f(...) end }

---------------- Vector3 ----------------
local V = {}
local VMT = {}
local function v3(x, y, z) return setmetatable({ X = x, Y = y, Z = z }, VMT) end
VMT.__index = function(t, k)
	if k == "Magnitude" then return math.sqrt(t.X*t.X + t.Y*t.Y + t.Z*t.Z) end
	if k == "Unit" then local m = math.sqrt(t.X*t.X + t.Y*t.Y + t.Z*t.Z); if m == 0 then return v3(0,0,0) end; return v3(t.X/m, t.Y/m, t.Z/m) end
	if k == "Dot" then return function(a, b) return a.X*b.X + a.Y*b.Y + a.Z*b.Z end end
	if k == "Cross" then return function(a, b) return v3(a.Y*b.Z - a.Z*b.Y, a.Z*b.X - a.X*b.Z, a.X*b.Y - a.Y*b.X) end end
	return nil
end
VMT.__add = function(a, b) return v3(a.X+b.X, a.Y+b.Y, a.Z+b.Z) end
VMT.__sub = function(a, b) return v3(a.X-b.X, a.Y-b.Y, a.Z-b.Z) end
VMT.__unm = function(a) return v3(-a.X, -a.Y, -a.Z) end
VMT.__mul = function(a, b)
	if type(a) == "number" then return v3(a*b.X, a*b.Y, a*b.Z) end
	if type(b) == "number" then return v3(a.X*b, a.Y*b, a.Z*b) end
	return v3(a.X*b.X, a.Y*b.Y, a.Z*b.Z)
end
VMT.__div = function(a, b) if type(b) == "number" then return v3(a.X/b, a.Y/b, a.Z/b) end; return v3(a.X/b.X, a.Y/b.Y, a.Z/b.Z) end
V.new = function(x, y, z) return v3(x or 0, y or 0, z or 0) end
V.one = v3(1,1,1); V.zero = v3(0,0,0)
env.Vector3 = V

---------------- CFrame ----------------
local C = {}
local CMT = {}
local function cf(x,y,z,a,b,c,d,e,f,g,h,i) return setmetatable({ x=x,y=y,z=z, a=a,b=b,c=c, d=d,e=e,f=f, g=g,h=h,i=i }, CMT) end
local function mul(p, q)
	return cf(
		p.a*q.x + p.b*q.y + p.c*q.z + p.x, p.d*q.x + p.e*q.y + p.f*q.z + p.y, p.g*q.x + p.h*q.y + p.i*q.z + p.z,
		p.a*q.a + p.b*q.d + p.c*q.g, p.a*q.b + p.b*q.e + p.c*q.h, p.a*q.c + p.b*q.f + p.c*q.i,
		p.d*q.a + p.e*q.d + p.f*q.g, p.d*q.b + p.e*q.e + p.f*q.h, p.d*q.c + p.e*q.f + p.f*q.i,
		p.g*q.a + p.h*q.d + p.i*q.g, p.g*q.b + p.h*q.e + p.i*q.h, p.g*q.c + p.h*q.f + p.i*q.i)
end
CMT.__mul = function(p, q)
	if getmetatable(q) == VMT then
		return v3(p.a*q.X + p.b*q.Y + p.c*q.Z + p.x, p.d*q.X + p.e*q.Y + p.f*q.Z + p.y, p.g*q.X + p.h*q.Y + p.i*q.Z + p.z)
	end
	return mul(p, q)
end
local function inverse(p)
	local tx = -(p.a*p.x + p.d*p.y + p.g*p.z)
	local ty = -(p.b*p.x + p.e*p.y + p.h*p.z)
	local tz = -(p.c*p.x + p.f*p.y + p.i*p.z)
	return cf(tx,ty,tz, p.a,p.d,p.g, p.b,p.e,p.h, p.c,p.f,p.i)
end
local function ortho(m)
	-- Gram-Schmidt on rows
	local function norm(a,b,c) local l = math.sqrt(a*a+b*b+c*c); if l == 0 then return 1,0,0 end; return a/l,b/l,c/l end
	local r1x,r1y,r1z = norm(m.a,m.b,m.c)
	local dot = m.d*r1x + m.e*r1y + m.f*r1z
	local r2x,r2y,r2z = norm(m.d-dot*r1x, m.e-dot*r1y, m.f-dot*r1z)
	local r3x,r3y,r3z = r1y*r2z - r1z*r2y, r1z*r2x - r1x*r2z, r1x*r2y - r1y*r2x
	return cf(m.x,m.y,m.z, r1x,r1y,r1z, r2x,r2y,r2z, r3x,r3y,r3z)
end
CMT.__index = function(t, k)
	if k == "Position" then return v3(t.x, t.y, t.z) end
	if k == "Rotation" then return cf(0,0,0, t.a,t.b,t.c, t.d,t.e,t.f, t.g,t.h,t.i) end
	if k == "Inverse" then return inverse end
	if k == "ToObjectSpace" then return function(s, o) return mul(inverse(s), o) end end
	if k == "ToWorldSpace" then return function(s, o) return mul(s, o) end end
	if k == "Lerp" then return function(s, g, al)
		local function l(a, b) return a + (b - a) * al end
		return ortho(cf(l(s.x,g.x),l(s.y,g.y),l(s.z,g.z), l(s.a,g.a),l(s.b,g.b),l(s.c,g.c), l(s.d,g.d),l(s.e,g.e),l(s.f,g.f), l(s.g,g.g),l(s.h,g.h),l(s.i,g.i)))
	end end
	if k == "VectorToWorldSpace" then return function(s, v) return v3(s.a*v.X+s.b*v.Y+s.c*v.Z, s.d*v.X+s.e*v.Y+s.f*v.Z, s.g*v.X+s.h*v.Y+s.i*v.Z) end end
	return nil
end
C.identity = cf(0,0,0, 1,0,0, 0,1,0, 0,0,1)
C.new = function(x, y, z, ...)
	if x == nil then return C.identity end
	if type(x) == "table" then return cf(x.X, x.Y, x.Z, 1,0,0, 0,1,0, 0,0,1) end
	if select("#", ...) == 0 then return cf(x, y, z, 1,0,0, 0,1,0, 0,0,1) end
	local a,b,c,d,e,f,g,h,i = ...
	assert(i ~= nil, "CFrame.new needs 3 or 12 numbers")
	return cf(x,y,z, a,b,c, d,e,f, g,h,i)
end
C.Angles = function(rx, ry, rz)
	local cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
	local Rx = cf(0,0,0, 1,0,0, 0,cx,-sx, 0,sx,cx)
	local Ry = cf(0,0,0, cy,0,sy, 0,1,0, -sy,0,cy)
	local Rz = cf(0,0,0, cz,-sz,0, sz,cz,0, 0,0,1)
	return mul(mul(Rx, Ry), Rz)
end
C.fromAxisAngle = function(axis, ang)
	local u = axis.Unit; local x,y,z = u.X,u.Y,u.Z; local c,s = math.cos(ang), math.sin(ang); local t = 1-c
	return cf(0,0,0, t*x*x+c, t*x*y-s*z, t*x*z+s*y, t*x*y+s*z, t*y*y+c, t*y*z-s*x, t*x*z-s*y, t*y*z+s*x, t*z*z+c)
end
env.CFrame = C
env.Color3 = { fromRGB = function(r,g,b) return {R=r/255,G=g/255,B=b/255} end, fromHex = function(h) return {hex=h} end, new = function(r,g,b) return {R=r,G=g,B=b} end }
env.Enum = setmetatable({}, { __index = function(t, k) local sub = setmetatable({}, { __index = function(_, n) return k .. "." .. n end }); rawset(t, k, sub); return sub end })

---------------- Instance ----------------
local HIER = {
	Part = { "Part", "BasePart", "PVInstance", "Instance" }, Model = { "Model", "PVInstance", "Instance" },
	Folder = { "Folder", "Instance" }, Motor6D = { "Motor6D", "JointInstance", "Instance" }, Weld = { "Weld", "JointInstance", "Instance" },
	StringValue = { "StringValue", "ValueBase", "Instance" }, ModuleScript = { "ModuleScript", "LuaSourceContainer", "Instance" },
	AnimationController = { "AnimationController", "Instance" }, Animator = { "Animator", "Instance" },
}
local IMT = {}
local function newInst(class)
	local o = { ClassName = class, Name = class, _children = {}, _attrs = {}, _scale = 1 }
	if class == "Part" then o.Size = V.one; o.CFrame = C.identity; o.Transparency = 0; o.Anchored = false end
	if class == "Motor6D" or class == "Weld" then o.C0 = C.identity; o.C1 = C.identity end
	return setmetatable(o, IMT)
end
local function descendants(o, out) for _, c in ipairs(o._children) do out[#out+1] = c; descendants(c, out) end; return out end
local function setParent(o, p)
	local old = rawget(o, "_parent")
	if old then for i, c in ipairs(old._children) do if c == o then table.remove(old._children, i); break end end end
	rawset(o, "_parent", p)
	if p then table.insert(p._children, o) end
end
local M2 = {}
function M2.IsA(o, cls) for _, c in ipairs(HIER[o.ClassName] or { o.ClassName }) do if c == cls then return true end end; return false end
function M2.FindFirstChild(o, name, rec) for _, c in ipairs(rec and descendants(o, {}) or o._children) do if c.Name == name then return c end end; return nil end
function M2.WaitForChild(o, name) local c = M2.FindFirstChild(o, name); assert(c, "WaitForChild missing " .. name .. " in " .. o.Name); return c end
function M2.FindFirstChildOfClass(o, cls) for _, c in ipairs(o._children) do if c.ClassName == cls then return c end end; return nil end
function M2.GetChildren(o) return table.clone(o._children) end
function M2.GetDescendants(o) return descendants(o, {}) end
function M2.SetAttribute(o, k, v) o._attrs[k] = v end
function M2.GetAttribute(o, k) return o._attrs[k] end
function M2.GetAttributes(o) return table.clone(o._attrs) end
function M2.GetFullName(o) local n, p = o.Name, rawget(o, "_parent"); while p do n = p.Name .. "." .. n; p = rawget(p, "_parent") end; return n end
function M2.Destroy(o) setParent(o, nil) end
function M2.IsDescendantOf(o, a) local p = rawget(o, "_parent"); while p do if p == a then return true end; p = rawget(p, "_parent") end; return false end
function M2.GetPivot(o) if o.PrimaryPart then return o.PrimaryPart.CFrame end; return C.identity end
function M2.GetScale(o) return o._scale end
function M2.PivotTo(o, target)
	local pivot = M2.GetPivot(o); local delta = target * pivot:Inverse()
	for _, d in ipairs(descendants(o, {})) do if d.ClassName == "Part" then d.CFrame = delta * d.CFrame end end
end
function M2.ScaleTo(o, s)
	local f = s / o._scale; o._scale = s
	local pivot = M2.GetPivot(o)
	for _, d in ipairs(descendants(o, {})) do
		if d.ClassName == "Part" then
			d.Size = d.Size * f
			local rel = pivot:ToObjectSpace(d.CFrame)
			d.CFrame = pivot * cf(rel.x*f, rel.y*f, rel.z*f, rel.a,rel.b,rel.c, rel.d,rel.e,rel.f, rel.g,rel.h,rel.i)
		elseif d.ClassName == "Motor6D" or d.ClassName == "Weld" then
			local c0 = d.C0; d.C0 = cf(c0.x*f, c0.y*f, c0.z*f, c0.a,c0.b,c0.c, c0.d,c0.e,c0.f, c0.g,c0.h,c0.i)
		end
	end
end
function M2.Clone(o)
	local c = newInst(o.ClassName)
	for k, v in pairs(o) do if k ~= "_children" and k ~= "_parent" and k ~= "_attrs" then rawset(c, k, v) end end
	c._attrs = table.clone(o._attrs)
	for _, ch in ipairs(o._children) do setParent(M2.Clone(ch), c) end
	return c
end
IMT.__newindex = function(o, k, v) if k == "Parent" then setParent(o, v) else rawset(o, k, v) end end
env.Instance = { new = function(cls, parent) local o = newInst(cls); if parent then setParent(o, parent) end; return o end }
-- Parent must be readable via rawget; give instances a real __index that handles it
IMT.__index = function(o, k)
	if k == "Parent" then return rawget(o, "_parent") end
	return M2[k]
end

---------------- module system ----------------
local requireCache = {}
local function requireMod(inst)
	if requireCache[inst] ~= nil then return requireCache[inst] end
	local menv = setmetatable({ script = inst }, { __index = env })
	menv.require = requireMod
	local fn = loadmod(inst.Source, inst.Name, menv)
	local r = fn()
	requireCache[inst] = r
	return r
end
env.require = requireMod
local services = {}
local game = { GetService = function(_, n) return services[n] end }
services.HttpService = { JSONDecode = function(_, s) return jsondecode(s) end }
services.RunService = { IsStudio = function() return false end }
env.game = game
local function module(name, src, parent) local m = newInst("ModuleScript"); m.Name = name; m.Source = src; setParent(m, parent); return m end

---------------- build the fake ReplicatedStorage ----------------
local RS = newInst("Folder"); RS.Name = "ReplicatedStorage"; services.ReplicatedStorage = RS
local lib = newInst("Folder"); lib.Name = "Animation150"; setParent(lib, RS)
module("Motion", readfile(S150 .. "Motion.ModuleScript.lua"), lib)
module("Profiles", readfile(S150 .. "Profiles.ModuleScript.lua"), lib)
for b = 1, 25 do local n = string.format("Biome%02d", b); module(n, readfile(S150 .. n .. ".ModuleScript.lua"), lib) end
local rd = newInst("Folder"); rd.Name = "SpearHunt_RenderData"; setParent(rd, RS)

local ids = {}
for id in string.gmatch(readfile(M .. "ids.txt"), "[^\n]+") do
	local v = newInst("StringValue"); v.Name = id; v.Value = readfile(M .. "rd/" .. id .. ".json"); setParent(v, rd)
	ids[#ids+1] = id
end
local FaunaInst = module("Fauna150", readfile(M .. "Fauna150.luau"), RS)
local Fauna = requireMod(FaunaInst)
print("ids", #ids)

local function finite(n) return n == n and math.abs(n) < 1e6 end
local function checkModel(m, label)
	local joints, parts = 0, 0
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then
			parts += 1
			local p = d.CFrame
			if not (finite(p.x) and finite(p.y) and finite(p.z) and finite(p.a) and finite(p.e) and finite(p.i)) then error(label .. ": bad part cf " .. d.Name) end
		elseif d:IsA("JointInstance") and d.ClassName == "Motor6D" then
			joints += 1
			local c = d.C0
			if not (finite(c.x) and finite(c.y) and finite(c.z) and finite(c.a)) then error(label .. ": bad joint " .. d.Name) end
		end
	end
	return parts, joints
end

local failures, bound = {}, 0
for n, id in ipairs(ids) do
	local ok, err = pcall(function()
		local m = Fauna.Create(id)
		assert(m, "Create returned nil")
		assert(m:GetAttribute("Fauna150") and m:GetAttribute("SpeciesId") == id)
		assert(Fauna.Attr(id, "Height") and Fauna.Attr(id, "MinY") and Fauna.Attr(id, "BoundsX"))
		local scale = (n % 3 == 0) and 1.7 or ((n % 3 == 1) and 1 or 0.45)
		if scale ~= 1 then m:ScaleTo(scale) end
		m:PivotTo(C.new(10, 2, -5))
		local native = Fauna.Bind(m)
		assert(native and native.play and native.step and native.destroy, "bad adapter")
		for _, st in ipairs({ "idle", "walk", "run", "hop", "flee", "sleep", "happy", "look" }) do
			native:play(st)
			for f = 1, 20 do native:step(1/30, 1) end
		end
		local parts, joints = checkModel(m, id)
		assert(parts > 20 and joints > 3, "model too small")
		assert(m.PrimaryPart and m.PrimaryPart.Name == "Root", "Motion root missing")
		native:destroy()
		bound += 1
	end)
	if not ok then failures[#failures+1] = id .. ": " .. tostring(err) end
end
print("bound ok:", bound, "of", #ids)
for i = 1, math.min(8, #failures) do print("FAIL", failures[i]) end
print("warnings:", #warnings); for i = 1, math.min(5, #warnings) do print("  W", warnings[i]) end
-- Template + Attr
local t = Fauna.Template("rabbit"); assert(t and Fauna.Template("rabbit") == t, "template cache")
print("template ok", Fauna.Has("amber_giraffe"), Fauna.Has("nope"), Fauna.Attr("primordial_titan", "Height"))

print("---- Config")
local cmod = newInst("ModuleScript"); cmod.Name = "Config"; cmod.Source = readfile(M .. "edits/Config.lua")
local Config = requireMod(cmod)
print("species", #Config.SPECIES, "zones", #Config.ZONES)
local seen, perZone, bad = {}, {}, {}
for _, sp in ipairs(Config.SPECIES) do
	if seen[sp.id] then bad[#bad+1] = "dup " .. sp.id end; seen[sp.id] = true
	if not Config.ZONES[sp.zone] then bad[#bad+1] = "zone " .. sp.id end
	if not Config.SPECIES_BY_ID[sp.id] then bad[#bad+1] = "byid " .. sp.id end
	if not (sp.price and sp.price > 0 and sp.wMin and sp.wMax and sp.wMax >= sp.wMin and sp.rarity >= 1 and sp.rarity <= #Config.RARITIES) then bad[#bad+1] = "fields " .. sp.id end
	perZone[sp.zone] = (perZone[sp.zone] or 0) + 1
end
for z = 1, #Config.ZONES do
	local zc = Config.ZONES[z]
	if zc.id ~= z then bad[#bad+1] = "zone id " .. z end
	if z > 1 and zc.from ~= Config.ZONES[z-1].to then bad[#bad+1] = "gap at zone " .. z end
	if perZone[z] ~= 6 then bad[#bad+1] = "zone " .. z .. " has " .. tostring(perZone[z]) .. " species" end
end
print("config problems:", #bad); for i = 1, math.min(10, #bad) do print("  ", bad[i]) end
print("zoneFor(6000)=", Config.zoneFor(6000), "zoneFor(12000)=", Config.zoneFor(12000), "zoneFor(100)=", Config.zoneFor(100))
