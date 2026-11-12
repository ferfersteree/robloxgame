-- StarterPlayerScripts/Client/SpearFx.luau
-- Полёт копья: дуга, вращение, следы по цветам копья, эффекты ступени (кольца, искры, молнии, радуга),
-- замедление у вершины и перед ударом, удар по типу копья, копьё втыкается в землю.
-- Свои броски запускает HuntCtl/Showroom; чужие приходят через Fx remote (k = "throw").
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local Config = require(RS.Shared.Config)
local Net = require(RS.Shared.Net)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Fx = require(script.Parent.WorldFx)
local Animator = require(script.Parent.Animator)
local NativeAssets = RS:WaitForChild("V15SpearPresentation")
local NativeFactory = require(NativeAssets.SpearFactoryV15)
local NativeFlight = require(NativeAssets.LiveSpearV15)

local SpearFx = {}
SpearFx.Landed = Instance.new("BindableEvent") -- (pos, tier) — любое приземление копья (своё и чужое)

export type Flight = {
	model: Model?,
	from: Vector3,
	to: Vector3,
	pos: Vector3,
	dir: Vector3,
	u: number,
	dur: number,
	h: number,
	tier: number,
	crashed: boolean,
	done: boolean,
	spear: string,
	isLocal: boolean,
	onLand: ((Vector3) -> ())?,
	t: number,
	nextBolt: number,
	trails: { Trail },
	landPos: Vector3?,
	revealHeld: boolean?,
	v15: any?,
}

local flights: { Flight } = {}
local flightSounds: { [any]: Sound } = {} -- свист копья в полёте, снимается при посадке
local camera = workspace.CurrentCamera

local GROUND_NAMES = { Ground = true, FarGround = true, Field = true, Floor = true, Path = true, Terrain = true }
local function groundAt(p: Vector3): Vector3
	-- Обычный одиночный луч мог поймать крону, куст или крышу: тогда копьё
	-- визуально «приземлялось» высоко в воздухе. Пропускаем всё, кроме земли.
	local ignored: { Instance } = { Fx.folder, Players.LocalPlayer.Character or Fx.folder }
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	for _ = 1, 24 do
		params.FilterDescendantsInstances = ignored
		local r = workspace:Raycast(p + Vector3.new(0, 60, 0), Vector3.new(0, -180, 0), params)
		if not r then
			break
		end
		local hit = r.Instance
		if hit:IsA("Terrain") or GROUND_NAMES[hit.Name] then
			return r.Position
		end
		table.insert(ignored, hit)
	end
	return Vector3.new(p.X, Config.GROUND_Y, p.Z)
end
SpearFx.groundAt = groundAt

local function attach(part: BasePart, pos: Vector3, name: string): Attachment
	local a = Instance.new("Attachment")
	a.Name = name
	a.Position = pos
	a.Parent = part
	return a
end

local function makeTrail(shaft: BasePart, w: number, c1: Color3, c2: Color3, life: number, light: number, transp: number): Trail
	local a0 = attach(shaft, Vector3.new(w, -2.2, 0), "TrA")
	local a1 = attach(shaft, Vector3.new(-w, -2.2, 0), "TrB")
	local tr = Instance.new("Trail")
	tr.Attachment0 = a0
	tr.Attachment1 = a1
	tr.FaceCamera = true
	tr.Lifetime = life
	tr.MinLength = 0.05
	tr.Color = ColorSequence.new(c1, c2)
	tr.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, transp), NumberSequenceKeypoint.new(0.6, transp * 0.4 + 0.45), NumberSequenceKeypoint.new(1, 1) })
	tr.WidthScale = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 0.05) })
	tr.LightEmission = light
	tr.LightInfluence = 0
	tr.Parent = shaft
	return tr
end

-- Скорость прохождения дуги: медленнее у вершины и перед ударом (slow-mo ступени)
local function warp(f: Flight, u: number): number
	if f.crashed then
		return 1
	end
	local tier = Config.TIERS[f.tier]
	local s = tier and tier.slowmo or 0
	local k = 1 - s * 0.55 * math.exp(-((u - 0.45) / 0.16) ^ 2)
	if f.tier >= 4 and u > 0.86 then
		k *= 0.45
	end
	return math.max(0.2, k)
end

local function pathAt(f: Flight, u: number): (Vector3, Vector3)
	local d = f.to - f.from
	local p = f.from + d * u + Vector3.yAxis * (4 * f.h * u * (1 - u))
	local v = d + Vector3.yAxis * (4 * f.h * (1 - 2 * u))
	return p, (v.Magnitude > 1e-3 and v.Unit or Vector3.yAxis)
end

export type LaunchOpts = {
	spear: string,
	from: Vector3,
	to: Vector3,
	tier: number,
	crashed: boolean?,
	isLocal: boolean?,
	onLand: ((Vector3) -> ())?,
}

function SpearFx.launch(o: LaunchOpts): Flight
	local s = Config.SPEAR_BY_ID[o.spear] or Config.SPEARS[1]
	local tierIdx = math.clamp(o.tier or 1, 1, #Config.TIERS)
	local tier = Config.TIERS[tierIdx]
	local to = groundAt(o.to)
	local dist = (Vector3.new(to.X, 0, to.Z) - Vector3.new(o.from.X, 0, o.from.Z)).Magnitude
	local f: Flight = {
		model = Animator.spearModel(o.spear),
		from = o.from,
		to = to + Vector3.new(0, 0.4, 0),
		pos = o.from,
		dir = (to - o.from).Unit,
		u = 0,
		dur = o.crashed and 0.9 or Config.flightTime(dist),
		h = o.crashed and 3 or math.clamp(dist * Config.THROW.arcFrac * (1 + 0.08 * (tierIdx - 1)),4,42),
		tier = tierIdx,
		crashed = o.crashed == true,
		done = false,
		spear = o.spear,
		isLocal = o.isLocal == true,
		onLand = o.onLand,
		t = 0,
		nextBolt = 0.15,
		trails = {},
		landPos = nil,
	}
	local m = f.model
	if m then
		local shaft = m.PrimaryPart :: BasePart
		if not f.crashed and not m:GetAttribute("V15Spear") then
			local w = 0.22 + 0.1 * tierIdx
			table.insert(f.trails, makeTrail(shaft, w, s.trail[1], s.trail[2], 0.25 + 0.07 * tierIdx, 0.3 + 0.12 * tierIdx, 0.05))
			if tierIdx >= 3 then
				table.insert(f.trails, makeTrail(shaft, w * 2.6, tier.color, tier.color2, 0.18 + 0.06 * tierIdx, 1, 0.65))
			end
			local glow = shaft:FindFirstChild("GlowAtt") :: Attachment?
			if glow and tierIdx >= 3 then
				Fx.emitter(glow, { tex = tierIdx >= 6 and "star" or "sparkle", color = tier.color, color2 = s.trail[1], size = 0.5 + 0.12 * tierIdx, life = 0.6, rate = 18 * tierIdx, speed = NumberRange.new(0.5, 3), rot = true })
			end
			if glow and tierIdx >= 5 then
				local l = Instance.new("PointLight")
				l.Color = tier.color
				l.Range = 14 + tierIdx * 2
				l.Brightness = 3
				l.Shadows = false
				l.Parent = glow
			end
			if s.impact == "fire" then
				local tail = shaft:FindFirstChild("TailAtt") :: Attachment?
				if tail then
					Fx.emitter(tail, { tex = "fire", color = s.trail[1], color2 = s.trail[2], size = 1.2, life = 0.5, rate = 40 })
				end
			end
		end
		local hand = o.isLocal and Players.LocalPlayer.Character and Players.LocalPlayer.Character:FindFirstChild("RightHand")
		if m:GetAttribute("V15Spear") and hand and hand:IsA("BasePart") then
			m:PivotTo(NativeFactory.AtGrip(m,hand.CFrame*CFrame.new(.02,-.1,-.07)*CFrame.Angles(math.pi,0,0)))
		else
			m:PivotTo(Animator.spearCF(o.from, f.dir))
		end
		m.Parent = Fx.folder
		if not f.crashed then
			local fly = Sfx.attachLoop(m, "fly", 0.1 + 0.015 * tierIdx)
			if fly then
				flightSounds[f] = fly
			end
		end
		if m:GetAttribute("V15Spear") and not f.crashed then f.v15 = NativeFlight.Attach(m,o.spear,tierIdx) end
	end
	-- старт
	if f.crashed then
		Sfx.at(o.from, "crash", 1, 0.8)
	else
		Sfx.at(o.from, "throw", 1.12 - 0.05 * tierIdx, 0.55 + 0.07 * tierIdx)
		if not f.v15 and tierIdx >= 2 then
			Fx.ring(o.from - Vector3.new(0, 1.6, 0), tier.color, 3 + tierIdx * 1.5, 0.45)
		end
		if not f.v15 and tierIdx >= 4 then
			Fx.sphere(o.from, tier.color, 2 + tierIdx * 0.6, 0.35)
			Fx.light(o.from, tier.color, 20, 6, 0.4)
			if f.isLocal then
				Fx.shake(tier.shake * 0.6, 0.35)
			end
		end
		if not f.v15 and tierIdx >= 5 then
			Sfx.at(o.from, "thunder", 1, 0.8)
		end
	end
	table.insert(flights, f)
	return f
end

local function land(f: Flight)
	f.done = true
	local fly = flightSounds[f]
	if fly then
		fly:Destroy()
		flightSounds[f] = nil
	end
	local s = Config.SPEAR_BY_ID[f.spear] or Config.SPEARS[1]
	local tier = Config.TIERS[f.tier]
	local p = f.to
	f.landPos = p
	local m = f.model
	if m then
		for _, tr in f.trails do
			tr.Enabled = false
		end
		for _, e in m:GetDescendants() do
			if e:IsA("ParticleEmitter") then
				e.Enabled = false
			end
		end
		if f.crashed then
			-- падает плашмя
			m:PivotTo(CFrame.fromMatrix(p + Vector3.new(0, 0.3, 0), Vector3.yAxis:Cross(f.dir.Unit), Vector3.new(f.dir.X, 0, f.dir.Z).Unit) * CFrame.Angles(0, 0, 0))
		elseif m:GetAttribute("V15Spear") then
			m:PivotTo(NativeFactory.AtTip(m,p-Vector3.yAxis*.35,f.dir))
		else
			-- втыкается остриём в землю
			local dir = Vector3.new(f.dir.X, math.min(f.dir.Y, -0.6), f.dir.Z).Unit
			m:PivotTo(Animator.spearCF(p - dir * 4.2, dir))
		end
		task.delay(f.isLocal and 4 or 2.5, function()
			-- The bush reveal can last longer than the normal landed-spear lifetime.
			-- Its owner releases this hold after the result card closes.
			while f.revealHeld and m.Parent do task.wait(0.1) end
			if m.Parent then
				for _, d in m:GetDescendants() do
					if d:IsA("BasePart") then
						Fx.tween(d, 0.6, { Transparency = 1 })
					end
				end
				task.wait(0.65)
				m:Destroy()
			end
		end)
	end
	if f.v15 then
		f.v15:Land(p-Vector3.yAxis*.35,f.dir)
		Sfx.at(p,"hit",1.1-f.tier*.06,.7+f.tier*.05)
	elseif f.crashed then
		Fx.impact("dust", p, s.trail[1], s.trail[2], 1)
		Sfx.at(p, "hit_ground", nil, 0.7)
	else
		local k = 1 + 0.35 * (f.tier - 1)
		Fx.impact(s.impact, p, s.trail[1], s.trail[2], k)
		Fx.ring(p + Vector3.new(0, 0.2, 0), tier.color, 4 + f.tier * 2.2, 0.55 + f.tier * 0.05)
		if f.tier >= 3 then
			Fx.ring(p + Vector3.new(0, 0.3, 0), s.trail[1], 2 + f.tier * 1.4, 0.4)
			Fx.light(p + Vector3.new(0, 2, 0), tier.color, 18 + f.tier * 4, 4 + f.tier, 0.6)
		end
		if f.tier >= 5 then
			Fx.lightning(p + Vector3.new(math.random(-10, 10), 70, math.random(-10, 10)), p, tier.color, 10, 0.5)
			Sfx.at(p, "boom", 0.9, 1)
		end
		Sfx.at(p, "hit", 1.1 - f.tier * 0.06, 0.7 + f.tier * 0.05)
		local camDist = (camera.CFrame.Position - p).Magnitude
		if f.isLocal or camDist < 60 then
			Fx.shake(tier.shake, 0.4 + tier.shake * 0.4)
		end
	end
	if f.onLand then
		task.spawn(f.onLand, p)
	end
	SpearFx.Landed:Fire(p, f.tier)
end

RunService.RenderStepped:Connect(function(dt)
	for i = #flights, 1, -1 do
		local f = flights[i]
		if f.done then
			table.remove(flights, i)
			continue
		end
		f.t += dt
		f.u = math.min(1, f.u + dt / f.dur * warp(f, f.u))
		local p, dir = pathAt(f, f.u)
		f.pos = p
		f.dir = dir
		local m = f.model
		if m then
			local cf
			if f.crashed then
				-- кувыркается
				local spin = f.t * 14
				cf = Animator.spearCF(p, dir) * CFrame.Angles(spin, 0, spin * 0.3)
			elseif f.v15 then
				cf = f.v15:Frame(p,dir,f.u,f.t)
			else
				local roll = f.tier >= 3 and f.t * (6 + f.tier) or 0
				cf = Animator.spearCF(p - dir * 1.5, dir) * CFrame.Angles(0, roll, 0)
			end
			m:PivotTo(cf)
			-- радужный след легенды
			if f.tier >= 6 and #f.trails > 0 then
				local c = Theme.rainbow(f.t * 2)
				f.trails[1].Color = ColorSequence.new(c, Theme.rainbow(f.t * 2 + 1.2))
			end
		end
		-- молнии вдоль полёта (ГРОМ и выше)
		if not f.v15 and not f.crashed and f.tier >= 5 and f.t >= f.nextBolt then
			f.nextBolt = f.t + (f.tier >= 6 and 0.18 or 0.3)
			local tier = Config.TIERS[f.tier]
			Fx.lightning(p + Vector3.new(math.random(-14, 14), 45, math.random(-14, 14)), p, tier.color, 8, 0.3)
			if math.random() < 0.4 then
				Sfx.at(p, "thunder", 1.1 + math.random() * 0.3, 0.4)
			end
		end
		if f.u >= 1 then
			land(f)
		end
	end
end)

-- Точка приземления по дальности: вперёд (−Z) от засады с небольшим разбросом
function SpearFx.targetFor(from: Vector3, look: Vector3, dist: number, spread: number?): Vector3
	local fwd = Vector3.new(look.X, 0, look.Z)
	fwd = fwd.Magnitude > 1e-3 and fwd.Unit or Vector3.new(0, 0, -1)
	local side = fwd:Cross(Vector3.yAxis)
	local sp = math.min((spread or 0.12) * dist,8)
	local p = from + fwd * dist + side * (math.random() * 2 - 1) * sp
	return groundAt(p)
end

-- Чужие броски
Net.ev("Fx").OnClientEvent:Connect(function(pl: any)
	if type(pl) ~= "table" then
		return
	end
	if pl.k == "throw" and typeof(pl.from) == "Vector3" and typeof(pl.to) == "Vector3" then
		SpearFx.launch({ spear = pl.spear or "stick", from = pl.from, to = pl.to, tier = pl.tier or 1, crashed = pl.crashed == true, isLocal = false })
	elseif pl.k == "tier" and typeof(pl.pos) == "Vector3" then
		local tier = Config.TIERS[math.clamp(pl.tier or 1, 1, #Config.TIERS)]
		Fx.ring(pl.pos, tier.color, 3 + (pl.tier or 1), 0.4)
		Fx.burst(pl.pos + Vector3.new(0, 2, 0), { tex = "sparkle", color = tier.color, n = 8, speed = NumberRange.new(4, 8), size = 0.6, life = 0.6, accel = Vector3.new(0, 6, 0) })
	end
end)

return SpearFx
