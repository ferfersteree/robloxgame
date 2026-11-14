-- StarterPlayerScripts/Client/AnimalRig.luau
-- Оживление воксельных зверей. Группы модели (Body, Head, Leg*, Arm*, Wing*, Tail) крепятся Motor6D
-- к суставам (атрибуты jx,jy,jz относительно Root). Root якорный — двигаем его, остальное едет само.
-- rig = AnimalRig.new(clone); rig:play("idle"|"walk"|"run"|"hop"|"happy"|"flee"|"look"|"sleep"); rig:setCF(cf)
local RunService = game:GetService("RunService")
local NativeMotion = require(script.Parent.NativeMotion)
local FaunaFactoryV16 = require(game:GetService("ReplicatedStorage"):WaitForChild("V16Fauna"):WaitForChild("Factory"))
local Fauna150 = require(game:GetService("ReplicatedStorage"):WaitForChild("Fauna150"))

local AnimalRig = {}
AnimalRig.__index = AnimalRig

export type Group = { name: string, motor: Motor6D, side: number, front: number }
export type Rig = typeof(setmetatable({} :: {
	model: Model,
	root: BasePart,
	groups: { Group },
	kind: string,
	state: string,
	t: number,
	cf: CFrame,
	h: number,
	seed: number,
	alive: boolean,
	lod: number,
	acc: number,
	stateT: number,
	speed: number,
	onUpdate: ((any, number) -> ())?,
	native: any?,
}, AnimalRig))

local all: { [any]: boolean } = {}
local camera = workspace.CurrentCamera

local function setup(model: Model): (BasePart, { Group })
	local root = (model.PrimaryPart or model:FindFirstChild("Root")) :: BasePart
	root.Anchored = true
	local rootCF = root.CFrame
	local sc = model:GetScale() -- шаблон мог быть уменьшен ScaleTo до сборки
	local joints: { [string]: { part: BasePart, model: Model } } = {}
	for _, g in model:GetChildren() do
		if g:IsA("Model") and g:GetAttribute("jx") ~= nil then
			local jp = Instance.new("Part")
			jp.Name = "J_" .. g.Name
			jp.Size = Vector3.new(0.1, 0.1, 0.1)
			jp.Transparency = 1
			jp.CanCollide = false
			jp.CanQuery = false
			jp.CanTouch = false
			jp.Massless = true
			jp.Anchored = false
			jp.CFrame = rootCF * CFrame.new((g:GetAttribute("jx") :: number) * sc, (g:GetAttribute("jy") :: number) * sc, (g:GetAttribute("jz") :: number) * sc)
			jp.Parent = g
			joints[g.Name] = { part = jp, model = g }
		end
	end
	-- детали групп к суставам; без сустава — к Root
	for _, g in model:GetChildren() do
		if g:IsA("Model") then
			local j = joints[g.Name]
			local anchor = j and j.part or root
			for _, d in g:GetDescendants() do
				if d:IsA("BasePart") and d ~= anchor then
					d.Anchored = false
					d.CanCollide = false
					d.CanQuery = false
					d.CanTouch = false
					d.Massless = true
					local w = Instance.new("Weld")
					w.Part0 = anchor
					w.Part1 = d
					w.C0 = anchor.CFrame:ToObjectSpace(d.CFrame)
					w.Parent = d
				end
			end
		end
	end
	local groups: { Group } = {}
	for name, j in joints do
		local pn = j.model:GetAttribute("parent")
		local p0 = (type(pn) == "string" and joints[pn] and joints[pn].part) or root
		local m = Instance.new("Motor6D")
		m.Name = "M_" .. name
		m.Part0 = p0
		m.Part1 = j.part
		m.C0 = p0.CFrame:ToObjectSpace(j.part.CFrame)
		m.C1 = CFrame.new()
		m.Parent = j.part
		local jx = j.model:GetAttribute("jx") :: number
		local jz = j.model:GetAttribute("jz") :: number
		table.insert(groups, { name = name, motor = m, side = jx < -0.01 and -1 or (jx > 0.01 and 1 or 0), front = jz < 0 and 1 or -1 })
	end
	return root, groups
end

function AnimalRig.new(model: Model, parent: Instance?): Rig
	if not model:GetAttribute("NativeV16") then
		local id=model:GetAttribute("SpeciesId") or model.Name
		local replacement=FaunaFactoryV16.Create(id)
		if replacement then
			local cf=model:GetPivot();local scale=model:GetScale()
			replacement:PivotTo(cf);if scale~=1 then replacement:ScaleTo(scale) end
			model:Destroy();model=replacement
		end
	end
	-- Фауна коллекции (Fauna150) двигается через Animation150; старые запеченные клипы остаются запасным путём
	local native = if model:GetAttribute("Fauna150") then Fauna150.Bind(model) elseif model:GetAttribute("NativeV11") then NativeMotion.bind(model) else nil
	local root, groups
	if native then
		root=model.PrimaryPart
		assert(root,"Native animal has no root")
		root.Anchored=true;groups={}
	else root,groups=setup(model) end
	local self = setmetatable({
		model = model,
		root = root,
		groups = groups,
		kind = (model:GetAttribute("Rig") :: string?) or "quad",
		state = "idle",
		t = math.random() * 10,
		cf = root.CFrame,
		h = (model:GetAttribute("Height") :: number?) or 2,
		seed = math.random() * 100,
		alive = true,
		lod = 0,
		acc = 0,
		stateT = 0,
		speed = 1,
		onUpdate = nil,
	}, AnimalRig)
	self.native = native
	model.Parent = parent or workspace
	all[self] = true
	return self
end

function AnimalRig.play(self: Rig, state: string, speed: number?)
	if self.native then self.native:play(state) end
	if self.state ~= state then
		self.state = state
		self.stateT = 0
	end
	self.speed = speed or 1
end

function AnimalRig.setCF(self: Rig, cf: CFrame)
	self.cf = cf
end

function AnimalRig.destroy(self: Rig)
	self.alive = false
	all[self] = nil
	if self.native then self.native:destroy();self.native=nil end
	self.model:Destroy()
end

local sin, rad = math.sin, math.rad

-- Позы групп: возвращает (смещение корня, наклон корня) и пишет Transform моторов
function AnimalRig.step(self: Rig, dt: number)
	if self.native then
		self.t+=dt*self.speed;self.stateT+=dt
		if self.root.CFrame~=self.cf then self.root.CFrame=self.cf end
		self.native:step(dt,self.speed)
		if self.onUpdate then self.onUpdate(self,dt) end
		return
	end
	self.t += dt * self.speed
	self.stateT += dt
	local t, st, kind = self.t, self.state, self.kind
	local s = math.clamp(self.h / 3, 0.4, 3) -- масштаб амплитуд по росту
	local bob, pitch, roll, yaw = 0, 0, 0, 0
	local w = 0 -- частота шага
	local amp = 0 -- размах ног
	if st == "walk" then
		w, amp = 7, 28
	elseif st == "run" or st == "flee" then
		w, amp = 13, 42
	elseif st == "hop" then
		w, amp = 6, 0
	end
	local ph = t * w
	local happy = st == "happy"
	local hopping = kind == "hop" and (st == "walk" or st == "run" or st == "flee" or st == "hop")
	if hopping then
		local k = (t * (st == "walk" and 3.2 or 4.5)) % 1
		bob = sin(k * math.pi) * 0.55 * s
		pitch = -sin(k * math.pi * 2) * 10
	elseif st == "walk" or st == "run" or st == "flee" then
		bob = math.abs(sin(ph)) * 0.08 * s * (st == "walk" and 1 or 1.8)
		roll = sin(ph) * (kind == "biped" and 4 or 1.5)
	elseif happy then
		local k = (self.stateT * 1.6) % 1
		bob = math.abs(sin(k * math.pi)) * 0.9 * s
		yaw = (self.stateT < 0.62) and self.stateT / 0.62 * 360 or 0
		roll = sin(self.stateT * 12) * 6
	elseif st == "sleep" then
		bob = -0.05 * s
		pitch = 4 + sin(t * 1.2) * 1.5
	else
		bob = sin(t * 2.2 + self.seed) * 0.02 * s
	end
	for _, g in self.groups do
		local n = g.name
		local cf = CFrame.new()
		if n == "Body" then
			cf = CFrame.Angles(rad(pitch + (st == "idle" and sin(t * 2.2) * 1.2 or 0)), 0, rad(roll))
		elseif n == "Head" then
			if st == "idle" or st == "look" then
				local look = sin(t * 0.7 + self.seed) * 28
				local nod = sin(t * 1.9 + self.seed) * 5
				if st == "look" then
					look = sin(t * 2.4) * 50
				end
				cf = CFrame.Angles(rad(nod), rad(look), 0)
			elseif happy then
				cf = CFrame.Angles(rad(-15 + sin(self.stateT * 18) * 10), 0, rad(sin(self.stateT * 9) * 14))
			elseif st == "sleep" then
				cf = CFrame.Angles(rad(22), rad(10), 0)
			else
				cf = CFrame.Angles(rad(sin(ph * 2) * 4 - (st == "flee" and 10 or 0)), 0, 0)
			end
		elseif n:sub(1, 3) == "Leg" then
			local swing = 0
			if hopping then
				local k = (t * (st == "walk" and 3.2 or 4.5)) % 1
				swing = (g.front > 0 and -1 or 1) * sin(k * math.pi) * 35
			elseif amp > 0 then
				-- диагональные пары у четвероногих, поочерёдно у двуногих/птиц
				local off = 0
				if n == "LegFR" or n == "LegBL" or n == "LegR" then
					off = math.pi
				end
				swing = sin(ph + off) * amp
			elseif happy then
				swing = sin(self.stateT * 20 + g.side) * 20
			elseif st == "sleep" then
				swing = g.front > 0 and -60 or 50
			end
			cf = CFrame.Angles(rad(swing), 0, 0)
		elseif n:sub(1, 3) == "Arm" then
			local swing = 0
			local lift = 0
			if amp > 0 then
				swing = -sin(ph + (n == "ArmR" and math.pi or 0)) * amp * 0.8
			elseif happy then
				lift = 120 + sin(self.stateT * 16) * 25
			else
				swing = sin(t * 1.6 + g.side) * 4
			end
			cf = CFrame.Angles(rad(swing), 0, rad(-g.side * lift))
		elseif n:sub(1, 4) == "Wing" then
			local flap = 0
			if happy or st == "flee" or st == "run" then
				flap = sin(t * 26) * 55 + 20
			elseif st == "walk" then
				flap = sin(t * 8) * 8 + 6
			else
				flap = sin(t * 1.5) * 3
			end
			cf = CFrame.Angles(0, 0, rad(g.side * flap))
		elseif n == "Tail" then
			local wag = sin(t * (happy and 22 or (amp > 0 and 9 or 3))) * (happy and 30 or 14)
			cf = CFrame.Angles(rad(happy and -20 or 0), rad(wag), 0)
		end
		g.motor.Transform = cf
	end
	self.root.CFrame = self.cf * CFrame.new(0, bob, 0) * CFrame.Angles(0, rad(yaw), 0)
	if self.onUpdate then
		self.onUpdate(self, dt)
	end
end

-- LOD: ближние — каждый кадр, дальние — реже, совсем далёкие/за спиной — стоят
RunService.RenderStepped:Connect(function(dt)
	local cam = camera.CFrame
	local cpos = cam.Position
	for r in all do
		local rig = r :: Rig
		if not rig.model.Parent then
			all[rig] = nil
			continue
		end
		local d = (rig.cf.Position - cpos).Magnitude
		local every = d < 65 and (rig.model:GetAttribute("NativeV15") and 1/60 or 1/30) or (d < 130 and 1/15 or (d < 260 and 1/8 or math.huge))
		local ahead = cam.LookVector:Dot(rig.cf.Position - cpos) > -10
		if not ahead then
			every = math.max(every, 1 / 4)
		end
		rig.acc += dt
		if rig.acc >= every then
			rig:step(rig.acc)
			rig.acc = 0
		end
	end
end)

-- Клон шаблона из ReplicatedStorage.Animals, оживлённый и поставленный в cf
function AnimalRig.spawn(spId: string, cf: CFrame, parent: Instance?, mut: string?, scale: number?): Rig?
	local RS = game:GetService("ReplicatedStorage")
	local tpl = RS:FindFirstChild("Animals") and RS.Animals:FindFirstChild(spId)
	local m=FaunaFactoryV16.Create(spId)
	if not m then
		if not tpl or not tpl:IsA("Model") then return nil end
		m=tpl:Clone()
	end
	if mut then
		local Util = require(RS.Shared.Util)
		Util.applyMutation(m, mut)
	end
	m:PivotTo(cf)
	if scale and scale ~= 1 then
		m:ScaleTo(scale)
	end
	local rig = AnimalRig.new(m, parent)
	-- Baked poses are cached from the shared template; runtime copies need geometry only.
	local poses=m:FindFirstChild("BakedMotion")
	if poses then poses:Destroy() end
	rig.cf = cf
	rig.h *= scale or 1
	return rig
end

return AnimalRig
