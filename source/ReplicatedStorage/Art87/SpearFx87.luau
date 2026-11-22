--!strict
-- ReplicatedStorage/Art87/SpearFx87
-- V87: проигрыватель эффектов копий Claude Design. Данные: Art87/SpearFxData1 (копья 1-23) и SpearFxData2 (24-46),
-- схема: docs/concepts_v87/roblox/SPEAR_FX_SCHEMA.md. Меши эффектов: ReplicatedStorage.Art87.SpearFX.sp_NN_<id>_fx_<имя>.
-- API (только клиент):
--   Fx87.has(id)                       -- есть ли данные эффектов у копья
--   Fx87.attachIdle(model, id, isLocal?)  -- в руке: частицы и свет на вложениях TipAtt/TrailRoot/Grip модели
--   Fx87.attachFlight(model, id)       -- в полёте: частицы, свет и воздушные кольца; handle:stop() выключает всё
--   Fx87.impact(id, groundCFrame, opts?) -- удар: свет, залпы частиц, анимированные меши; сам убирается за duration
-- Лент (Trail) и лучей (Beam) здесь нет по требованию дизайнера. Все поля данных необязательные, неизвестные имена
-- заменяются запасными, ошибка одной записи не ломает бросок (pcall).
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")

local Fx87 = {}

-- V87: те же текстуры, что в WorldFx (они точно грузятся); формы без своей текстуры берут ближайшую
local T_SPARKLE = "rbxasset://textures/particles/sparkles_main.dds"
local T_SMOKE = "rbxasset://textures/particles/smoke_main.dds"
local T_FIRE = "rbxasset://textures/particles/fire_main.dds"
local T_SPARKS = "rbxasset://textures/particles/fire_sparks_main.dds"
local T_SQUARE = "rbxasset://textures/particles/SquareParticle.png"
local T_GLOW = "rbxasset://textures/glow.png"
local T_STAR = "rbxasset://textures/sparkle.png"
local T_CIRCLE = "rbxasset://textures/whiteCircle.png"
local T_TRIANGLE = "rbxasset://textures/triangle.png"
local TEX: { [string]: string } = {
	sparkle = T_SPARKLE, star = T_STAR, smoke = T_SMOKE, dust = T_SMOKE, spark = T_SPARKS, rock = T_SQUARE,
	leaf = T_TRIANGLE, feather = T_TRIANGLE, snow = T_CIRCLE, fire = T_FIRE, bubble = T_CIRCLE, crystal = T_TRIANGLE,
	shard = T_TRIANGLE, spore = T_GLOW, gear = T_SQUARE, bolt = T_SPARKS, drop = T_CIRCLE,
}

local EASE: { [string]: Enum.EasingStyle } = {
	Quad = Enum.EasingStyle.Quad, Back = Enum.EasingStyle.Back, Sine = Enum.EasingStyle.Sine,
	Linear = Enum.EasingStyle.Linear, Bounce = Enum.EasingStyle.Bounce,
}

-- Лимиты: дёшево и без накопления
local MAX_LIVE_RINGS = 24 -- колец полёта одновременно (на все копья)
local MAX_IMPACTS = 4 -- ударов одновременно; сверх этого меши не строятся, залпы вдвое меньше
local MESH_CAP = 24 -- мешей (с копиями) на один удар
local MESH_CAP_LOW = 10
local BURST_CAP = 60 -- частиц в одном залпе

---------------------------------------------------------------------
-- Данные
---------------------------------------------------------------------
local data: { [string]: any } = {}
for _, name in { "SpearFxData1", "SpearFxData2" } do
	local mod = script.Parent:WaitForChild(name, 5)
	if mod and mod:IsA("ModuleScript") then
		local ok, res = pcall(require, mod)
		if ok and type(res) == "table" then
			for k, v in res do
				data[k] = v
			end
		else
			warn("[SpearFx87] " .. name .. ": " .. tostring(res))
		end
	end
end

function Fx87.has(id: string): boolean
	return data[id] ~= nil
end

---------------------------------------------------------------------
-- Мелочи
---------------------------------------------------------------------
local function lowFx(): boolean
	local lp = Players.LocalPlayer
	return lp ~= nil and lp:GetAttribute("LowFx") == true
end

local function num(v: any, default: number): number
	return if type(v) == "number" and v == v and math.abs(v) < math.huge then v else default
end

-- число или пара {a, b} -> a, b
local function pair(v: any, d1: number, d2: number?): (number, number)
	if type(v) == "number" then
		return v, v
	elseif type(v) == "table" then
		local a = num(v[1], d1)
		return a, num(v[2], a)
	end
	return d1, d2 or d1
end

local function color(hex: any, default: Color3?): Color3
	if type(hex) == "string" then
		local n = tonumber((hex:gsub("#", "")), 16)
		if n then
			return Color3.fromRGB(bit32.band(bit32.rshift(n, 16), 255), bit32.band(bit32.rshift(n, 8), 255), bit32.band(n, 255))
		end
	end
	return default or Color3.new(1, 1, 1)
end

local fxFolder: Folder? = nil
local function folder(): Folder
	local f = fxFolder
	if f and f.Parent then
		return f
	end
	local found = workspace:FindFirstChild("SpearFx87") :: Folder?
	if not found then
		local made = Instance.new("Folder")
		made.Name = "SpearFx87"
		made.Parent = workspace
		found = made
	end
	fxFolder = found
	return found :: Folder
end

local warned: { [string]: boolean } = {}
local function warnOnce(key: string, msg: string)
	if not warned[key] then
		warned[key] = true
		warn("[SpearFx87] " .. msg)
	end
end

---------------------------------------------------------------------
-- Шаблоны мешей эффектов (Art87.SpearFX)
---------------------------------------------------------------------
local fxIndex: { [string]: Instance } = {}
local fxCount = -1
local function fxMesh(id: string, name: string): BasePart?
	local art = RS:FindFirstChild("Art87")
	local dir = art and art:FindFirstChild("SpearFX")
	if not dir then
		return nil
	end
	local kids = dir:GetChildren()
	if #kids ~= fxCount then
		fxCount = #kids
		table.clear(fxIndex)
		for _, k in kids do
			local sid, mesh = string.match(k.Name, "^sp_%d+_(.-)_fx_(.+)$")
			if sid then
				fxIndex[sid .. "/" .. mesh] = k
			end
		end
	end
	local t = fxIndex[id .. "/" .. name]
	if not t then
		return nil
	end
	if t:IsA("BasePart") then
		return t
	end
	return t:FindFirstChildWhichIsA("BasePart", true) :: BasePart? -- Model: берём первую деталь
end

local function plain(p: BasePart)
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.CastShadow = false
	p.Massless = true
end

---------------------------------------------------------------------
-- Частицы и свет
---------------------------------------------------------------------
-- mode: "idle" | "flight" | "impact". low: «Reduced Effects»
local function buildEmitter(e: any, parent: Instance, mode: string, low: boolean): ParticleEmitter
	local em = Instance.new("ParticleEmitter")
	em.Texture = TEX[e.texture] or T_SPARKLE
	em.Color = ColorSequence.new(color(e.c0), color(e.c1 or e.c0))
	local s0, s1 = num(e.s0, 0.3), num(e.s1, 0)
	if type(e.smid) == "number" then
		em.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, s0), NumberSequenceKeypoint.new(0.5, e.smid), NumberSequenceKeypoint.new(1, s1) })
	else
		em.Size = NumberSequence.new(s0, s1)
	end
	em.Transparency = NumberSequence.new(math.clamp(num(e.t0, 0), 0, 1), math.clamp(num(e.t1, 1), 0, 1))
	local l1, l2 = pair(e.life, 1)
	em.Lifetime = NumberRange.new(math.min(l1, l2), math.max(l1, l2))
	local v1, v2 = pair(e.speed, 1)
	em.Speed = NumberRange.new(math.min(v1, v2), math.max(v1, v2))
	local sx, sy = pair(e.spread, 25)
	em.SpreadAngle = Vector2.new(math.clamp(sx, 0, 180), math.clamp(sy, 0, 180))
	local accel = Vector3.zero
	if type(e.accel) == "table" then
		accel = Vector3.new(num(e.accel[1], 0), num(e.accel[2], 0), num(e.accel[3], 0))
	end
	-- Направление: у копья (idle/flight) ось +Y вдоль древка, у удара ось Y вверх, -Z по ходу копья
	local d = e.dir
	if d == "back" then
		em.EmissionDirection = if mode == "impact" then Enum.NormalId.Back else Enum.NormalId.Bottom
	elseif d == "forward" then
		em.EmissionDirection = if mode == "impact" then Enum.NormalId.Front else Enum.NormalId.Top
	elseif d == "out" then
		em.EmissionDirection = Enum.NormalId.Top
		em.SpreadAngle = Vector2.new(180, 180)
	else
		em.EmissionDirection = Enum.NormalId.Top
		if mode ~= "impact" then
			-- «вверх по миру» при вращающемся копье: слабый разброс и подъём ускорением (оно задано в мире)
			em.SpreadAngle = Vector2.new(sx, sy)
			em.Speed = NumberRange.new(math.min(v1, v2) * 0.3, math.max(v1, v2) * 0.3)
			accel += Vector3.new(0, (v1 + v2) * 0.5 * 1.5, 0)
		end
	end
	em.Acceleration = accel
	if type(e.drag) == "number" then
		em.Drag = e.drag
	end
	local rot = num(e.rot, 0)
	em.Rotation = NumberRange.new(0, 360)
	em.RotSpeed = NumberRange.new(-math.abs(rot), math.abs(rot))
	local light = math.clamp(num(e.light, 0), 0, 1)
	em.LightEmission = light
	em.LightInfluence = if light > 0.5 then 0 else 0.4
	em.Orientation = Enum.ParticleOrientation.FacingCamera
	if e.count ~= nil and mode == "impact" then
		em.Rate = 0
		em.Enabled = false
	else
		em.Rate = num(e.rate, 8) * (if low then 0.5 else 1)
	end
	em.Parent = parent
	return em
end

local function buildLight(l: any, parent: Instance): PointLight
	local pl = Instance.new("PointLight")
	pl.Color = color(l.color)
	pl.Range = math.clamp(num(l.range, 8), 1, 40)
	pl.Brightness = math.clamp(num(l.brightness, 1), 0, 8)
	pl.Shadows = false
	pl.Parent = parent
	return pl
end

-- Точка на копье: at = "tip" | "trail" | "grip" (ground у копья = trail)
local function pointOf(model: Model, at: any): Instance?
	local pv = model.PrimaryPart
	if not pv then
		return nil
	end
	local name = if at == "grip" then "Grip" elseif at == "trail" or at == "ground" then "TrailRoot" else "TipAtt"
	return pv:FindFirstChild(name) or pv
end

local function fill(model: Model, def: any, mode: string, low: boolean): ({ ParticleEmitter }, { PointLight })
	local ems: { ParticleEmitter } = {}
	local lights: { PointLight } = {}
	local list = def.emitters
	if type(list) == "table" then
		for i, e in list do
			if i > 6 then
				break -- по схеме не больше 6 эмиттеров на копьё
			end
			local at = pointOf(model, e.at)
			if at then
				table.insert(ems, buildEmitter(e, at, mode, low))
			end
		end
	end
	if type(def.light) == "table" and not low then
		local at = pointOf(model, def.light.at or "tip")
		if at then
			table.insert(lights, buildLight(def.light, at))
		end
	end
	return ems, lights
end

---------------------------------------------------------------------
-- Idle: копьё в руке
---------------------------------------------------------------------
function Fx87.attachIdle(model: Model, id: string, isLocal: boolean?): any
	local entry = data[id]
	local def = entry and entry.idle
	if type(def) ~= "table" then
		return nil
	end
	local low = lowFx()
	if low and isLocal == false then
		return nil -- на слабой графике чужие копья без частиц
	end
	local ok, ems, lights = pcall(fill, model, def, "idle", low)
	if not ok then
		warnOnce("idle_" .. id, "idle " .. id .. ": " .. tostring(ems))
		return nil
	end
	local h: any = { Emitters = ems, Lights = lights }
	function h.stop()
		for _, e in ems do
			if e.Parent then
				e.Enabled = false
			end
		end
		for _, l in lights do
			l:Destroy()
		end
	end
	return h
end

---------------------------------------------------------------------
-- Flight: копьё в полёте
---------------------------------------------------------------------
local flights: { any } = {}
local flightConn: RBXScriptConnection? = nil
local liveRings = 0

local function spawnRing(h: any, r: any)
	if liveRings >= MAX_LIVE_RINGS then
		return
	end
	local tpl = fxMesh(h.Id, tostring(r.mesh or "air_ring"))
	local pv = (h.Model :: Model).PrimaryPart
	if not tpl or not pv or not pv.Parent then
		return
	end
	local tipAtt = pv:FindFirstChild("TipAtt") :: Attachment?
	local cf = pv.CFrame
	local pos = if tipAtt then tipAtt.WorldPosition else cf.Position
	local axis = cf.UpVector
	local base = tpl.Size
	local life = math.max(0.2, num(r.life, 1))
	local p = tpl:Clone()
	for _, c in p:GetChildren() do
		if not c:IsA("SpecialMesh") and not c:IsA("SurfaceAppearance") then
			c:Destroy()
		end
	end
	plain(p)
	p.Material = Enum.Material.Neon
	p.Color = color(r.color)
	p.Size = base * num(r.s0, 0.6)
	p.Transparency = math.clamp(num(r.a0, 0.2), 0, 1)
	local rot = cf.Rotation
	p.CFrame = rot + pos
	p.Parent = folder()
	liveRings += 1
	-- кольцо остаётся в мире и уходит назад вдоль оси, которая была у копья в момент появления
	local tw = TweenService:Create(p, TweenInfo.new(life, Enum.EasingStyle.Linear), {
		Size = base * num(r.s1, 2),
		Transparency = 1,
		CFrame = rot + (pos - axis * num(r.travel, 6.5)),
	})
	tw.Completed:Once(function()
		liveRings -= 1
		p:Destroy()
	end)
	tw:Play()
end

local function flightStep(dt: number)
	for i = #flights, 1, -1 do
		local h = flights[i]
		local m = h.Model :: Model
		if h.Stopped or not m.Parent then
			h:stop()
			continue
		end
		for _, r in h.Rings do
			r.acc += dt
			if r.acc >= r.every then
				r.acc -= r.every
				if r.acc > r.every then
					r.acc = 0
				end
				spawnRing(h, r.def)
			end
		end
	end
end

local function dropFlight(h: any)
	local i = table.find(flights, h)
	if i then
		table.remove(flights, i)
	end
	if #flights == 0 and flightConn then
		flightConn:Disconnect()
		flightConn = nil
	end
end

function Fx87.attachFlight(model: Model, id: string): any
	local entry = data[id]
	local def = entry and entry.flight
	if type(def) ~= "table" then
		return nil
	end
	local low = lowFx()
	local ok, ems, lights = pcall(fill, model, def, "flight", low)
	if not ok then
		warnOnce("flight_" .. id, "flight " .. id .. ": " .. tostring(ems))
		return nil
	end
	local rings: { any } = {}
	if not low and type(def.rings) == "table" then
		for i, r in def.rings do
			if i > 3 then
				break
			end
			table.insert(rings, { def = r, every = math.max(0.1, num(r.every, 0.33)), acc = 0 })
		end
	end
	local h: any = { Id = id, Model = model, Emitters = ems, Lights = lights, Rings = rings, Stopped = false }
	function h.stop(self: any)
		if self.Stopped and #self.Emitters == 0 then
			return
		end
		self.Stopped = true
		for _, e in self.Emitters do
			if e.Parent then
				e.Enabled = false
			end
		end
		for _, l in self.Lights do
			l:Destroy()
		end
		table.clear(self.Emitters)
		table.clear(self.Lights)
		table.clear(self.Rings)
		dropFlight(self)
	end
	if #rings > 0 then
		table.insert(flights, h)
		if not flightConn then
			flightConn = RunService.Heartbeat:Connect(flightStep)
		end
	end
	return h
end

---------------------------------------------------------------------
-- Impact: удар в землю
---------------------------------------------------------------------
local liveMeshes: { any } = {}
local meshConn: RBXScriptConnection? = nil
local activeImpacts = 0

local function makeMeshPart(r: any): BasePart?
	local md = r.md
	local p: BasePart? = nil
	local name = tostring(md.mesh or "part")
	if name == "part" or name == "ball" or name == "cyl" then
		local q = Instance.new("Part")
		q.Shape = if name == "ball" then Enum.PartType.Ball elseif name == "cyl" then Enum.PartType.Cylinder else Enum.PartType.Block
		q.TopSurface = Enum.SurfaceType.Smooth
		q.BottomSurface = Enum.SurfaceType.Smooth
		p = q
	else
		local tpl = fxMesh(r.id, name)
		if not tpl then
			warnOnce("mesh_" .. r.id .. name, "нет меша " .. r.id .. "_fx_" .. name)
			return nil
		end
		p = tpl:Clone()
		for _, c in (p :: BasePart):GetChildren() do
			if not c:IsA("SpecialMesh") and not c:IsA("SurfaceAppearance") then
				c:Destroy()
			end
		end
	end
	local part = p :: BasePart
	r.cyl = name == "cyl" -- цилиндр Roblox лежит осью вдоль X: размеры X/Y меняем местами и кладём диск
	plain(part)
	part.Material = if md.neon == false then Enum.Material.SmoothPlastic else Enum.Material.Neon
	part.Color = color(md.color)
	part.Size = if r.cyl then Vector3.new(r.size0.Y, r.size0.X, r.size0.Z) else r.size0
	part.Transparency = r.a0
	part.CFrame = if r.cyl then r.base * CFrame.Angles(0, 0, math.pi / 2) else r.base
	part.Parent = folder()
	return part
end

local function meshStep()
	local now = os.clock()
	for i = #liveMeshes, 1, -1 do
		local r = liveMeshes[i]
		local t = now - r.start
		if t < r.t0 then
			continue
		end
		if not r.part then
			local okM, made = pcall(makeMeshPart, r)
			r.part = if okM then made else nil
			if not r.part then
				table.remove(liveMeshes, i)
				continue
			end
		end
		local part = r.part :: BasePart
		if t >= r.tEnd or not part.Parent then
			part:Destroy()
			table.remove(liveMeshes, i)
			continue
		end
		local a = if r.t1 > r.t0 then math.clamp((t - r.t0) / (r.t1 - r.t0), 0, 1) else 1
		local k = TweenService:GetValue(a, r.ease, Enum.EasingDirection.Out)
		local size = r.size0:Lerp(r.size1, k)
		part.Size = if r.cyl then Vector3.new(size.Y, size.X, size.Z) else size
		part.Transparency = math.clamp(r.a0 + (r.a1 - r.a0) * k, 0, 1)
		local y = r.y0 + (r.y1 - r.y0) * k
		local cf = r.base * CFrame.new(0, y, 0) * CFrame.Angles(0, math.rad(r.spin) * (t - r.t0), 0)
		part.CFrame = if r.cyl then cf * CFrame.Angles(0, 0, math.pi / 2) else cf
	end
	if #liveMeshes == 0 and meshConn then
		meshConn:Disconnect()
		meshConn = nil
	end
end

local function vec3(v: any, default: Vector3): Vector3
	if type(v) == "table" then
		return Vector3.new(num(v[1], default.X), num(v[2], default.Y), num(v[3], default.Z))
	end
	return default
end

local function runImpact(id: string, def: any, ground: CFrame, opts: any, low: boolean)
	local crowded = activeImpacts >= MAX_IMPACTS
	local scale = num(opts.scale, 1)
	local duration = math.clamp(num(def.duration, 1.5), 0.3, 4)
	local holder = Instance.new("Part")
	holder.Name = "Impact_" .. id
	holder.Transparency = 1
	holder.Size = Vector3.one * 0.2
	plain(holder)
	holder.CFrame = ground
	holder.Parent = folder()
	local lastAt = duration

	activeImpacts += 1
	local okB, errB = pcall(function()
		-- свет: гаснет к t1
		if type(def.light) == "table" and not low then
			local pl = buildLight(def.light, holder)
			local t1 = math.max(0.05, num(def.light.t1, 0.4))
			TweenService:Create(pl, TweenInfo.new(t1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Brightness = 0 }):Play()
		end

		-- залпы частиц
		if type(def.bursts) == "table" then
			for i, e in def.bursts do
				if i > 6 then
					break
				end
				local em = buildEmitter(e, holder, "impact", low)
				local count = math.floor(num(e.count, 8) * (if low or crowded then 0.5 else 1))
				count = math.clamp(count, 1, BURST_CAP)
				local delay = math.max(0, num(e.delay, 0))
				local _, lmax = pair(e.life, 1)
				lastAt = math.max(lastAt, delay + lmax)
				if delay <= 0 then
					em:Emit(count)
				else
					task.delay(delay, function()
						if em.Parent then
							em:Emit(count)
						end
					end)
				end
			end
		end

		-- меши: строятся лениво в meshStep (один общий цикл)
		if type(def.meshes) == "table" and not crowded then
			local cap = if low then MESH_CAP_LOW else MESH_CAP
			local total = 0
			local now = os.clock()
			for _, md in def.meshes do
				local count = math.max(1, math.floor(num(md.count, 1)))
				local rad = num(md.r, 0) * scale
				local t0 = math.max(0, num(md.t0, 0))
				local t1 = math.max(t0, num(md.t1, t0 + 0.4))
				local tEnd = math.min(duration, t1 + math.max(0, num(md.hold, 0)))
				local s0 = vec3(md.size0, Vector3.one * 0.3) * scale
				local s1 = vec3(md.size1, Vector3.one) * scale
				for j = 1, count do
					if total >= cap then
						break
					end
					total += 1
					local ang = (j - 1) / count * math.pi * 2
					local off = if count > 1 or rad > 0 then Vector3.new(math.cos(ang) * rad, 0, math.sin(ang) * rad) else Vector3.zero
					table.insert(liveMeshes, {
						id = id, md = md, base = ground * CFrame.new(off) * CFrame.Angles(0, -ang, 0),
						start = now, t0 = t0, t1 = t1, tEnd = tEnd, size0 = s0, size1 = s1,
						a0 = math.clamp(num(md.a0, 0), 0, 1), a1 = math.clamp(num(md.a1, 1), 0, 1),
						y0 = num(md.y0, 0) * scale, y1 = num(md.y1, 0) * scale, spin = num(md.spin, 0),
						ease = EASE[md.easing] or Enum.EasingStyle.Quad,
					})
				end
			end
			if #liveMeshes > 0 and not meshConn then
				meshConn = RunService.Heartbeat:Connect(meshStep)
			end
		end

	end)
	if not okB then
		warnOnce("impact_" .. id, "impact " .. id .. ": " .. tostring(errB))
	end
	task.delay(lastAt + 0.2, function()
		activeImpacts -= 1
		holder:Destroy()
	end)
end

-- groundCFrame: точка касания, Y вверх, LookVector по ходу копья (вдоль земли)
function Fx87.impact(id: string, groundCFrame: CFrame, opts: any?)
	local entry = data[id]
	local def = entry and entry.impact
	if type(def) ~= "table" then
		return
	end
	local ok, err = pcall(runImpact, id, def, groundCFrame, opts or {}, lowFx())
	if not ok then
		warnOnce("impact_" .. id, "impact " .. id .. ": " .. tostring(err))
	end
end

return Fx87
