-- StarterPlayerScripts/Client/Ambient.luau
-- Живой мир (только на клиенте): звери бродят по своим зонам и разбегаются от копья, бабочки,
-- светлячки, огоньки духов, снег, дым из труб, прыгающие лягушки.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Config = require(RS.Shared.Config)
local Fx = require(script.Parent.WorldFx)
local AnimalRig = require(script.Parent.AnimalRig)
local Fauna150 = require(RS:WaitForChild("Fauna150"))

local Ambient = {}

local map = workspace:WaitForChild("Map")
local rng = Random.new()
local LANES = { 0 }
local FOREST_X = 120
local GY = Config.GROUND_Y

local folder = Instance.new("Folder")
folder.Name = "Ambient"
folder.Parent = workspace

local function laneDist(x: number): number
	local d = math.huge
	for _, l in LANES do
		d = math.min(d, math.abs(x - l))
	end
	return d
end

local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = { folder, Fx.folder }
local function ground(x: number, z: number): number
	local r = workspace:Raycast(Vector3.new(x, 40, z), Vector3.new(0, -80, 0), params)
	if r and r.Position.Y < 6 then
		return r.Position.Y
	end
	return GY
end

---------------------------------------------------------------------
-- Звери
---------------------------------------------------------------------
type Walker = { rig: any, anchor: BasePart, species: string, flee: number }
local walkers: { [BasePart]: Walker } = {}
local population: Instance? = nil
local streamClock=0

local function zoneRange(z: number): (number, number)
 local zone=Config.ZONES[z]
 local origin=Config.FOREST_ORIGIN_Z or -3
 return origin-zone.from-2,origin-zone.to+2
end

local function streamAnimals()
 local camera=workspace.CurrentCamera
 if not population or not camera then return end
 local distanceLimit=if Fx.lowFx then 170 else 260
 local maximum=if Fx.lowFx then 8 else 14
 local candidates={}
 for _,anchor in ipairs(population:GetChildren()) do
  if anchor:IsA("BasePart") then
   local distance=(anchor.Position-camera.CFrame.Position).Magnitude
   if distance<distanceLimit then table.insert(candidates,{anchor=anchor,distance=distance}) end
  end
 end
 table.sort(candidates,function(a,b)return a.distance<b.distance end)
 local visible={}
 for i,entry in ipairs(candidates) do
  if i>maximum then break end
  visible[entry.anchor]=true
 end
 -- Release old detailed rigs before allocating the next area's models.
 for anchor,walker in pairs(walkers) do
  if not visible[anchor] or not anchor.Parent then walker.rig:destroy();walkers[anchor]=nil end
 end
 local spawned=0
 for i,entry in ipairs(candidates) do
  if i>maximum then break end
  local anchor=entry.anchor
  local species=anchor:GetAttribute("SpeciesId")
  local old=walkers[anchor]
  if old and old.species~=species then old.rig:destroy();walkers[anchor]=nil;old=nil end
  if not old and type(species)=="string" and spawned<(if Fx.lowFx then 1 else 2) then
   local rig=AnimalRig.spawn(species,anchor.CFrame,folder,nil,Fauna150.WorldScale(species)) -- V61: настоящий размер рядом с игроком
   spawned+=1
   if rig then walkers[anchor]={rig=rig,anchor=anchor,species=species,flee=0} end
  end
 end
end

local function spawnWalkers()
 population=map:WaitForChild("WorldPopulation",20)
 if population then streamAnimals() end
end

function Ambient.scare(pos: Vector3, radius: number?)
 for anchor,walker in pairs(walkers) do
  if (anchor.Position-pos).Magnitude<(radius or 22) then walker.flee=2.5 end
 end
end

local function stepWalkers(dt: number)
 streamClock+=dt
 if streamClock>=.5 then streamClock=0;streamAnimals() end
 for anchor,walker in pairs(walkers) do
  if walker.rig.alive and anchor.Parent then
   local state=anchor:GetAttribute("AnimationState") or "idle"
   local speed=anchor:GetAttribute("AnimationSpeed") or 1
   if walker.flee>0 then walker.flee-=dt;state="flee";speed=1.6 end
   walker.rig:play(state,speed)
   walker.rig:setCF(walker.rig.cf:Lerp(anchor.CFrame,1-math.exp(-dt*10)))
  end
 end
end

-- Local lightweight ambient particles. Detailed wildlife follows shared anchors.
type Mote = { part: BasePart, base: Vector3, ph: number, sp: number, r: number, kind: string, wings: { BasePart }? }
local motes: { Mote } = {}

local function ghostPart(size: Vector3, color: Color3, neon: boolean): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Size = size
	p.Color = color
	p.Material = neon and Enum.Material.Neon or Enum.Material.Plastic
	p.Parent = folder
	return p
end

local BUTTERFLY = { Color3.fromRGB(255, 160, 60), Color3.fromRGB(120, 200, 255), Color3.fromRGB(255, 120, 200), Color3.fromRGB(255, 240, 120) }
local function butterfly(base: Vector3)
	local c = BUTTERFLY[rng:NextInteger(1, #BUTTERFLY)]
	local body = ghostPart(Vector3.new(0.12, 0.12, 0.45), Color3.fromRGB(40, 30, 30), false)
	local l = ghostPart(Vector3.new(0.5, 0.05, 0.45), c, false)
	local r = ghostPart(Vector3.new(0.5, 0.05, 0.45), c, false)
	table.insert(motes, { part = body, base = base, ph = rng:NextNumber(0, 10), sp = rng:NextNumber(0.4, 0.8), r = rng:NextNumber(3, 7), kind = "butterfly", wings = { l, r } })
end

local function firefly(base: Vector3, color: Color3, kind: string)
	local p = ghostPart(Vector3.one * (kind == "wisp" and 0.6 or 0.22), color, true)
	if kind == "wisp" and rng:NextNumber() < 0.35 then
		local l = Instance.new("PointLight")
		l.Color = color
		l.Range = 8
		l.Brightness = 1.2
		l.Shadows = false
		l.Parent = p
	end
	table.insert(motes, { part = p, base = base, ph = rng:NextNumber(0, 10), sp = rng:NextNumber(0.2, 0.6), r = rng:NextNumber(2, 5), kind = kind })
end

local function stepMotes(_dt: number)
	local t = os.clock()
	for _, m in motes do
		local k = t * m.sp + m.ph
		local pos = m.base + Vector3.new(math.noise(k, 0, m.ph) * m.r * 2, math.noise(0, k, m.ph) * 1.5, math.noise(m.ph, 0, k) * m.r * 2)
		if m.kind == "butterfly" then
			local dirv = Vector3.new(math.noise(k + 0.05, 0, m.ph) - math.noise(k, 0, m.ph), 0, math.noise(m.ph, 0, k + 0.05) - math.noise(m.ph, 0, k))
			local yaw = dirv.Magnitude > 1e-4 and math.atan2(-dirv.X, -dirv.Z) or 0
			local cf = CFrame.new(pos) * CFrame.Angles(0, yaw, 0)
			m.part.CFrame = cf
			local flap = math.sin(t * 22 + m.ph) * 0.9
			if m.wings then
				m.wings[1].CFrame = cf * CFrame.Angles(0, 0, flap) * CFrame.new(-0.27, 0, 0)
				m.wings[2].CFrame = cf * CFrame.Angles(0, 0, -flap) * CFrame.new(0.27, 0, 0)
			end
		else
			m.part.CFrame = CFrame.new(pos + (m.kind == "wisp" and Vector3.new(0, math.sin(k * 2) * 1.2, 0) or Vector3.zero))
			m.part.Transparency = 0.2 + 0.8 * math.max(0, math.sin(t * (m.kind == "wisp" and 1.2 or 3) + m.ph * 3))
		end
	end
end

---------------------------------------------------------------------
-- Лягушки (модели карты прыгают на месте — локально)
---------------------------------------------------------------------
type Frog = { model: Model, home: CFrame, next: number, t: number, from: CFrame, to: CFrame }
local frogs: { Frog } = {}
local function stepFrogs(dt: number)
	local now = os.clock()
	for _, f in frogs do
		if f.t < 1 then
			f.t = math.min(1, f.t + dt / 0.45)
			local cf = f.from:Lerp(f.to, f.t)
			f.model:PivotTo(cf + Vector3.new(0, math.sin(f.t * math.pi) * 1.2, 0))
		elseif now > f.next then
			f.next = now + rng:NextNumber(1.5, 5)
			f.from = f.model:GetPivot()
			local off = Vector3.new(rng:NextNumber(-2.5, 2.5), 0, rng:NextNumber(-2.5, 2.5))
			local tp = f.home.Position + off
			f.to = CFrame.lookAt(tp, tp + (tp - f.from.Position) * Vector3.new(1, 0, 1) + Vector3.new(0, 0, 0.001))
			f.t = 0
		end
	end
end

---------------------------------------------------------------------
-- Дым, снег
---------------------------------------------------------------------
local function smoke(part: BasePart)
	local a = Instance.new("Attachment")
	a.Parent = part
	Fx.emitter(a, { tex = "smoke", color = Color3.fromRGB(230, 230, 235), size = 1.6, size2 = 4.5, life = 4, rate = 3, speed = NumberRange.new(1.5, 3), spread = 12, accel = Vector3.new(0.6, 0.8, 0), light = 0, transp = 0.45, drag = 0.4 })
end

local function snow()
	local z0, z1 = zoneRange(16)
	local p = ghostPart(Vector3.new(FOREST_X * 2, 1, math.abs(z1 - z0)), Color3.new(1, 1, 1), false)
	p.Transparency = 1
	p.CFrame = CFrame.new(0, 45, (z0 + z1) / 2)
	local e = Instance.new("ParticleEmitter")
	e.Texture = Fx.TEX.circle
	e.Color = ColorSequence.new(Color3.new(1, 1, 1))
	e.Size = NumberSequence.new(0.25)
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 0.6) })
	e.Lifetime = NumberRange.new(12, 16)
	e.Rate = Fx.lowFx and 40 or 120
	e.Speed = NumberRange.new(2, 4)
	e.EmissionDirection = Enum.NormalId.Bottom
	e.SpreadAngle = Vector2.new(15, 15)
	e.Acceleration = Vector3.new(1, 0, 0.5)
	e.LightInfluence = 0.6
	e.Parent = p
end

---------------------------------------------------------------------
-- Запуск
---------------------------------------------------------------------
function Ambient.init()
	task.spawn(spawnWalkers)
	-- бабочки над Опушкой и деревней
	for _ = 1, 10 do
		local x = rng:NextNumber(-110, 110)
		butterfly(Vector3.new(x, GY + rng:NextNumber(2, 4), rng:NextNumber(-30, -8)))
	end
	for _ = 1, 8 do
		butterfly(Vector3.new(rng:NextNumber(-120, 120), GY + rng:NextNumber(2, 4), rng:NextNumber(20, 140)))
	end
	-- светлячки в Чаще и Глуши
	for _ = 1, 26 do
		local z = rng:NextNumber(-138, -40)
		firefly(Vector3.new(rng:NextNumber(-115, 115), GY + rng:NextNumber(1, 4), z), z < -80 and Color3.fromRGB(150, 255, 120) or Color3.fromRGB(255, 240, 120), "firefly")
	end
	-- огоньки духов в Древнем лесу
	for _ = 1, 14 do
		firefly(Vector3.new(rng:NextNumber(-110, 110), GY + rng:NextNumber(3, 9), rng:NextNumber(-225, -145)), Color3.fromRGB(140, 220, 255), "wisp")
	end
	snow()
	for _, d in map:GetDescendants() do
		if d:IsA("BasePart") and d:GetAttribute("Smoke") then
			smoke(d)
		elseif d:IsA("Model") and d:GetAttribute("Critter") == "frog" then
			local cf = d:GetPivot()
			table.insert(frogs, { model = d, home = cf, next = os.clock() + rng:NextNumber(1, 6), t = 1, from = cf, to = cf })
		end
	end
	RunService.Heartbeat:Connect(function(dt)
		stepWalkers(dt)
		stepMotes(dt)
		stepFrogs(dt)
	end)
end

return Ambient
