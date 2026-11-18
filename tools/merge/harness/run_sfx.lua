local M = "../merge/"
local S150 = "../src150/ReplicatedStorage/Animation150/"
local env = setmetatable({}, { __index = _G })
env._G = env
local warnings = {}
env.warn = function(...) local t = {}; for i = 1, select("#", ...) do t[#t+1] = tostring((select(i, ...))) end; warnings[#warnings+1] = table.concat(t, " ") end
local now, queue = 0, {}
local function resume(co, ...) local ok, err = coroutine.resume(co, ...); if not ok then error(err, 0) end end
env.task = {
	wait = function(t) local co = coroutine.running(); table.insert(queue, { at = now + (t or 0.03), co = co }); return coroutine.yield() end,
	spawn = function(f, ...) local co = coroutine.create(f); resume(co, ...); return co end,
	defer = function(f, ...) local co = coroutine.create(f); table.insert(queue, { at = now, co = co, args = { ... } }) end,
	delay = function(t, f) local co = coroutine.create(f); table.insert(queue, { at = now + t, co = co }) end,
}
local function advance(dt)
	now += dt
	table.sort(queue, function(a, b) return a.at < b.at end)
	local due = {}
	while queue[1] and queue[1].at <= now do table.insert(due, table.remove(queue, 1)) end
	for _, q in ipairs(due) do if coroutine.status(q.co) == "suspended" then resume(q.co, table.unpack(q.args or {})) end end
end

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


---------------- extra stubs for Sfx ----------------
local function signal()
	local s = { _f = {} }
	function s:Once(f) table.insert(self._f, f) end
	function s:Connect(f) table.insert(self._f, f); return { Disconnect = function() end } end
	return s
end
HIER.Sound = { "Sound", "Instance" }; HIER.Attachment = { "Attachment", "Instance" }
local baseNew = env.Instance.new
env.Instance = { new = function(cls, parent)
	local o = baseNew(cls, parent)
	if cls == "Sound" then rawset(o, "Ended", signal()); rawset(o, "Volume", 0.5); rawset(o, "PlaybackSpeed", 1); rawset(o, "Looped", false)
		rawset(o, "Play", nil) end
	return o
end }
M2.Play = function(o) rawset(o, "Playing", true); o._plays = (o._plays or 0) + 1 end
M2.FindFirstChildWhichIsA = function(o, cls, rec) for _, d in ipairs(rec and descendants(o, {}) or o._children) do if M2.IsA(d, cls) then return d end end; return nil end
services.SoundService = newInst("Folder"); services.SoundService.Name = "SoundService"
services.TweenService = { Create = function(_, inst, info, props) return { Play = function() for k, v in pairs(props) do rawset(inst, k, v) end end } end }
env.TweenInfo = { new = function() return {} end }
env.workspace = { Terrain = newInst("Folder") }
local plays = {}

-- count Sound:Play calls through a wrapper on Clone results
local origClone = M2.Clone
M2.Clone = function(o) local c = origClone(o); if o.ClassName == "Sound" then rawset(c, "Ended", signal()) end; return c end
local Client = newInst("Folder"); Client.Name = "Client"
local function mod(name, src) local m = newInst("ModuleScript"); m.Name = name; m.Source = src; setParent(m, Client); return m end
local ids = {}
local function runScenario(label, audio)
	requireCache = {}
	for _, c in ipairs(table.clone(Client._children)) do setParent(c, nil) end
	mod("AudioIds", "return " .. audio)
	local sfxInst = mod("Sfx", readfile(M .. "../sound/Sfx.luau"))
	local Sfx = requireMod(sfxInst)
	local function count(folder) local n = 0; for _, d in ipairs(descendants(folder, {})) do if d.ClassName == "Sound" and d.Playing then n += 1 end end; return n end
	-- one-shots
	for _, n in ipairs({ "hover", "press", "open", "close", "coin", "buy", "error", "pop", "stamp", "rustle", "heart", "boom", "sparkle", "creak", "crash", "level", "bounce", "whoosh", "thunder", "ping", "click", "swoosh", "throw", "hit", "tick", "win", "select", "back", "blip", "rep", "miss", "hit_ground", "hit_wood", "pickup", "coin_burst", "jump", "land" }) do
		advance(0.1); Sfx.play(n); Sfx.play(n, 1.1, 0.3)
	end
	Sfx.ui("press"); Sfx.ui("open"); Sfx.ui("hover")
	Sfx.at(v3(0, 0, 0), "hit_ground", nil, 0.7); Sfx.at(v3(1, 2, 3), "throw", 1.1, 0.6); Sfx.at(v3(0, 0, 0), "boom", 0.9, 1)
	Sfx.note(-5, 0.4); Sfx.rise(3, 0.4)
	local l = Sfx.loop("creak", 0.72, 0.1); assert(l == nil or l.Looped)
	local part = newInst("Part"); local snd = Sfx.attachLoop(part, "fly", 0.12)
	Sfx.step("grass", 0.3); Sfx.step("stone"); Sfx.step("wood", 0.2)
	print(label, "has(press)=", Sfx.has("press"), "has(step_grass)=", Sfx.has("step_grass"), "attachLoop=", snd ~= nil)
	-- music: start, switch mood, stop
	Sfx.setMusic(true); Sfx.startMusic()
	for i = 1, 20 do advance(0.5) end
	Sfx.setMood("hunt"); for i = 1, 10 do advance(0.5) end
	Sfx.setMood("normal"); for i = 1, 10 do advance(0.5) end
	Sfx.setMood("cinematic"); advance(1)
	Sfx.setMusic(false); advance(1); Sfx.setMusic(true); advance(3)
	local mus = 0
	for _, d in ipairs(descendants(services.SoundService, {})) do if d.Name == "SpearHuntMusic" then mus += 1; print("   music id:", d.SoundId) end end
	print(label, "music sounds alive:", mus)
end
runScenario("EMPTY", "{}")
runScenario("FILLED", [[{ ui_hover_1="rbxassetid://1", ui_hover_2="rbxassetid://2", ui_press_1="rbxassetid://3", ui_press_2="rbxassetid://4", ui_open="rbxassetid://5", ui_close="rbxassetid://6", coin="rbxassetid://7", buy="rbxassetid://8", pop="rbxassetid://9", note_marimba="rbxassetid://10", spear_throw="rbxassetid://11", spear_fly="rbxassetid://12", spear_charge="rbxassetid://13", spear_hit_soft_1="rbxassetid://14", spear_hit_ground_1="rbxassetid://15", step_grass_1="rbxassetid://16", step_stone_1="rbxassetid://17", step_wood_1="rbxassetid://18", train_rep_1="rbxassetid://19", dialog_blip_1="rbxassetid://20", music_meadow="rbxassetid://21", music_cozy="rbxassetid://22", music_hunt="rbxassetid://23", amb_forest="rbxassetid://24", jump="rbxassetid://25", land="rbxassetid://26" }]])
print("done")
