-- ReplicatedStorage/Art87/Lib
-- V87: звери, кусты и эффекты Claude Design. Меши лежат в ReplicatedStorage.Art87 (Animals, Bushes, FX, Spears,
-- SpearFX; их собирает tools/bake87.py в Studio), ключи анимаций — в Art87.Data.B01..B25 (tools/art87_data.py,
-- уже в осях Roblox: зверь смотрит в −Z, начало координат на земле под центром тела).
--
-- Модель: анкерная опора Base (PrimaryPart) -> Motor6D -> кость Root (весь зверь) -> Motor6D -> кость каждого сегмента
-- (в точке сустава). Меши сегмента приварены к его кости. Анимация пишет Motor6D.Transform, поэтому работают
-- Model:ScaleTo (гиганты), перекраска деталей (золото, радуга, силуэт) и PivotTo как у прежних моделей Fauna150.
-- Ключи масштаба сегментов (лёгкое «дыхание») не повторяются: Motor6D не масштабирует; ключ масштаба корня во
-- время появления заменён на ScaleTo (см. Rig:step).
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Lib = {}

local root = RS:WaitForChild("Art87")
local dataFolder = root:WaitForChild("Data")
local FPS = 30

local Config: any = nil
local function config(): any
	if not Config then
		Config = require(RS:WaitForChild("Shared"):WaitForChild("Config"))
	end
	return Config
end

---------------------------------------------------------------------
-- Данные
---------------------------------------------------------------------
local biomes: { [number]: any } = {}
function Lib.biome(n: number): any?
	local d = biomes[n]
	if d == nil then
		local mod = dataFolder:FindFirstChild(string.format("B%02d", n))
		local ok, res = false, nil
		if mod then
			ok, res = pcall(require, mod)
		end
		d = if ok then res else false
		biomes[n] = d
	end
	return d or nil
end

local function zoneOf(id: string): number?
	local sp = config().SPECIES_BY_ID[id]
	return sp and sp.zone or nil
end

function Lib.animalData(id: string): any?
	local z = zoneOf(id)
	local b = z and Lib.biome(z)
	return b and b.animals[id] or nil
end

function Lib.bushData(biome: number): any?
	local b = Lib.biome(biome)
	return b and b.bush or nil
end

function Lib.hasAnimal(id: string): boolean
	local f = root:FindFirstChild("Animals")
	return f ~= nil and f:FindFirstChild("an_" .. id) ~= nil and Lib.animalData(id) ~= nil
end

function Lib.hasBush(biome: number): boolean
	local f = root:FindFirstChild("Bushes")
	return f ~= nil and f:FindFirstChild(string.format("bush_%02d", biome)) ~= nil and Lib.bushData(biome) ~= nil
end

---------------------------------------------------------------------
-- Выборка ключей
---------------------------------------------------------------------
local function ease(t: number): number
	return t * t * (3 - 2 * t)
end

-- трек {frame, a, b, c, interp, ...}: значения на кадре f (до первого ключа — первый, после последнего — последний)
local function sample3(tr: { number }, f: number): (number, number, number)
	local n = #tr
	if n == 0 then
		return 0, 0, 0
	end
	if f <= tr[1] then
		return tr[2], tr[3], tr[4]
	end
	if f >= tr[n - 4] then
		return tr[n - 3], tr[n - 2], tr[n - 1]
	end
	local i = 1
	while i + 5 <= n and tr[i + 5] <= f do
		i += 5
	end
	local f0, f1 = tr[i], tr[i + 5]
	local mode = tr[i + 4]
	local t = if f1 > f0 then (f - f0) / (f1 - f0) else 1
	if mode == 0 then
		t = 0
	elseif mode == 2 then
		t = ease(t)
	end
	return tr[i + 1] + (tr[i + 6] - tr[i + 1]) * t, tr[i + 2] + (tr[i + 7] - tr[i + 2]) * t, tr[i + 3] + (tr[i + 8] - tr[i + 3]) * t
end

-- трек {frame, v, frame, v, ...}, линейно
local function sample1(tr: { number }, f: number): number
	local n = #tr
	if n == 0 then
		return 0
	end
	if f <= tr[1] then
		return tr[2]
	end
	if f >= tr[n - 1] then
		return tr[n]
	end
	local i = 1
	while i + 2 <= n and tr[i + 2] <= f do
		i += 2
	end
	local t = (f - tr[i]) / math.max(tr[i + 2] - tr[i], 1e-6)
	return tr[i + 1] + (tr[i + 3] - tr[i + 1]) * t
end
Lib.sample3 = sample3
Lib.sample1 = sample1

-- поворот из трека: rx, ry, rz уже в осях Roblox, порядок Y * Z * X (см. tools/art87_data.py)
local function euler(rx: number, ry: number, rz: number): CFrame
	return CFrame.Angles(0, ry, 0) * CFrame.Angles(0, 0, rz) * CFrame.Angles(rx, 0, 0)
end
Lib.euler = euler

-- длина клипа в кадрах (последний ключ любого трека)
local function clipLength(clip: any): number
	local last = 1
	for _, ch in clip :: any do
		for _, key in { "loc", "rot", "scale" } do
			local tr = ch[key]
			if tr and #tr >= 5 then
				last = math.max(last, tr[#tr - 4])
			end
		end
	end
	return last
end
Lib.clipLength = clipLength

---------------------------------------------------------------------
-- Сборка модели с костями
---------------------------------------------------------------------
local function bonePart(name: string, cf: CFrame, anchored: boolean): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = Vector3.one * 0.05
	p.CFrame = cf
	p.Transparency = 1
	p.Anchored = anchored
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Massless = true
	p.CastShadow = false
	return p
end

local function motor(name: string, p0: BasePart, p1: BasePart): Motor6D
	local m = Instance.new("Motor6D")
	m.Name = name
	m.Part0 = p0
	m.Part1 = p1
	m.C0 = p0.CFrame:ToObjectSpace(p1.CFrame)
	m.C1 = CFrame.identity
	m.Parent = p1
	return m
end

-- segs: {name, object, parentIndex, jx, jy, jz}. Возвращает модель и список Motor6D по индексу сегмента.
local function rigUp(model: Model, segs: { any }, fxLib: Instance?): ({ [number]: Motor6D }, Motor6D, { [number]: { BasePart } })
	local rig = Instance.new("Folder")
	rig.Name = "Rig"
	rig.Parent = model
	local base = bonePart("Base", CFrame.identity, true)
	base.Parent = rig
	local rootBone = bonePart("Root", CFrame.identity, false)
	rootBone.Parent = rig
	local rootMotor = motor("Root", base, rootBone)
	local bones: { [number]: BasePart } = {}
	for i, s in segs do
		local b = bonePart("Bone_" .. s[1], CFrame.new(s[4], s[5], s[6]), false)
		b.Parent = rig
		bones[i] = b
	end
	local motors: { [number]: Motor6D } = {}
	local parts: { [number]: { BasePart } } = {}
	for i, s in segs do
		local parent = if s[3] > 0 then bones[s[3]] else rootBone
		motors[i] = motor(s[1], parent, bones[i])
		local list = {}
		local node: Instance? = model:FindFirstChild(s[2] .. "_Node", true)
		if not node and fxLib then
			-- V87: постоянные эффекты (ауры, огоньки, сегменты *_fxs_*) лежат в библиотеке fx_<id>, а не в модели зверя
			local src = fxLib:FindFirstChild("fx_" .. s[2])
			if src then
				local copy = src:Clone()
				copy.Parent = model
				for _, d in copy:GetDescendants() do
					if d:IsA("BasePart") then
						d.CastShadow = false
					end
				end
				node = copy
			end
		end
		if node then
			for _, d in node:GetChildren() do
				if d:IsA("BasePart") then
					d.Anchored = false
					d.Massless = true
					local w = Instance.new("WeldConstraint")
					w.Part0 = bones[i]
					w.Part1 = d
					w.Parent = d
					table.insert(list, d)
				end
			end
		end
		parts[i] = list
	end
	-- меши вне сегментов (маркеры, мелочь) — к корню
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d.Anchored and d ~= base then
			d.Anchored = false
			d.Massless = true
			local w = Instance.new("WeldConstraint")
			w.Part0 = rootBone
			w.Part1 = d
			w.Parent = d
		end
	end
	model.PrimaryPart = base
	return motors, rootMotor, parts
end

---------------------------------------------------------------------
-- Rig: проигрывает клипы на Motor6D
---------------------------------------------------------------------
export type Rig = {
	model: Model,
	data: any,
	motors: { [number]: Motor6D },
	rootMotor: Motor6D,
	parts: { [number]: { BasePart } },
	clip: string?,
	frame: number,
	loop: boolean,
	rate: number,
	onDone: (() -> ())?,
	play: (self: Rig, clip: string, loop: boolean?, onDone: (() -> ())?) -> (),
	step: (self: Rig, dt: number) -> (),
	pose: (self: Rig, clip: string, frame: number) -> (),
	length: (self: Rig, clip: string) -> number,
	destroy: (self: Rig) -> (),
}

local RigMeta = {}
RigMeta.__index = RigMeta

function RigMeta.length(self: any, clip: string): number
	local c = self.data.clips[clip]
	if not c then
		return 1
	end
	self.lengths = self.lengths or {}
	local l = self.lengths[clip]
	if not l then
		l = clipLength(c)
		local frames = self.data.frames and self.data.frames[clip]
		if clip == "Reveal" and self.data.revealFrames then
			frames = self.data.revealFrames
		elseif clip == "Idle" and self.data.idleFrames then
			frames = self.data.idleFrames
		end
		if frames then
			l = math.max(l, frames)
		end
		self.lengths[clip] = l
	end
	return l
end

function RigMeta.pose(self: any, clip: string, frame: number)
	local c = self.data.clips[clip]
	if not c then
		return
	end
	local segs = self.data.segs
	-- V87: Model:ScaleTo масштабирует C0/C1 моторов, но не Transform: смещения из клипа домножаем на масштаб сами
	local k = self.scaleLoc or self.model:GetScale()
	for i, m in self.motors do
		local ch = c[i]
		if ch then
			local cf = CFrame.identity
			if ch.loc then
				local x, y, z = sample3(ch.loc, frame)
				cf = CFrame.new(x * k, y * k, z * k)
			end
			if ch.rot then
				local rx, ry, rz = sample3(ch.rot, frame)
				cf *= euler(rx, ry, rz)
			end
			m.Transform = cf
		elseif segs[i] then
			m.Transform = CFrame.identity
		end
	end
	-- корень: ключи всего зверя (появление из куста: смещение от места, где он встанет)
	local rc = c.root
	if self.rootMotor then
		local cf = CFrame.identity
		if rc and rc.loc then
			local x, y, z = sample3(rc.loc, frame)
			local kr = self.rootScaleLoc or k
			cf = CFrame.new(x * kr, y * kr, z * kr)
		end
		if rc and rc.rot then
			local rx, ry, rz = sample3(rc.rot, frame)
			cf *= euler(rx, ry, rz)
		end
		self.rootMotor.Transform = cf
	end
	-- glow: яркость неона 0..1
	local g = self.data.glow and self.data.glow[clip]
	if g then
		for i, tr in g do
			local v = sample1(tr, frame)
			for _, p in self.parts[i] or {} do
				if p.Material == Enum.Material.Neon then
					p.Transparency = math.clamp(0.75 - 0.75 * v, 0, 0.9)
				end
			end
		end
	end
end

function RigMeta.play(self: any, clip: string, loop: boolean?, onDone: (() -> ())?)
	if not self.data.clips[clip] then
		if onDone then
			task.spawn(onDone)
		end
		return
	end
	self.clip = clip
	self.frame = 1
	self.loop = loop == true
	self.onDone = onDone
	self:pose(clip, 1)
end

function RigMeta.step(self: any, dt: number)
	local clip = self.clip
	if not clip or self.dead then
		return
	end
	self.frame += dt * FPS * (self.rate or 1)
	local len = self:length(clip)
	if self.frame > len then
		if self.loop then
			self.frame = 1 + (self.frame - 1) % math.max(len - 1, 1)
		else
			self.frame = len
			self:pose(clip, len)
			self.clip = nil
			local cb = self.onDone
			self.onDone = nil
			if cb then
				task.spawn(cb)
			end
			return
		end
	end
	self:pose(clip, self.frame)
end

function RigMeta.destroy(self: any)
	self.dead = true
	self.clip = nil
end

local function newRig(model: Model, data: any, fxLib: Instance?): any
	local motors, rootMotor, parts = rigUp(model, data.segs, fxLib)
	local self = setmetatable({ model = model, data = data, motors = motors, rootMotor = rootMotor, parts = parts, frame = 1, rate = 1 }, RigMeta)
	return self
end

---------------------------------------------------------------------
-- Звери и кусты
---------------------------------------------------------------------
-- Новая модель зверя (нет мешей или данных — nil). Атрибуты как у Fauna150.Create.
function Lib.animal(id: string): (Model?, any?)
	local data = Lib.animalData(id)
	local src = root:FindFirstChild("Animals") and root.Animals:FindFirstChild("an_" .. id)
	if not data or not src then
		return nil, nil
	end
	local model = src:Clone()
	model.Name = id
	local fxRoot = root:FindFirstChild("FX")
	local rig = newRig(model, data, fxRoot and fxRoot:FindFirstChild("fx_" .. id))
	local attrs = {
		SpeciesId = id, AssetId = id, AssetKind = "animal", Art87 = true, Fauna150 = true, NativeV16 = true, NativeV15 = true,
		Height = data.height, Width = data.width, Len = data.length, BoundsX = data.width, BoundsY = data.height,
		BoundsZ = data.length, MinY = 0, GroundOffsetY = data.hover or 0, Rig = "art87", BiomeId = zoneOf(id),
		HabitatKind = data.kind, RevealFrames = data.revealFrames, BushDistance = data.dist,
	}
	for k, v in attrs do
		model:SetAttribute(k, v)
	end
	for name, p in data.markers do
		local a = Instance.new("Attachment")
		a.Name = name
		a.Position = Vector3.new(p[1], p[2], p[3])
		a.Parent = model.PrimaryPart
	end
	return model, rig
end

-- Подхватить Rig у уже собранной модели (клон шаблона Fauna150.Template / AnimalRig): кости есть, моторов ищем по имени
function Lib.bind(model: Model): any?
	local id = model:GetAttribute("SpeciesId")
	local data = type(id) == "string" and Lib.animalData(id) or nil
	local rigFolder = model:FindFirstChild("Rig")
	if not data or not rigFolder or model:GetAttribute("Art87") ~= true then
		return nil
	end
	local motors, parts = {}, {}
	local boneIndex: { [Instance]: number } = {}
	for i, s in data.segs do
		local bone = rigFolder:FindFirstChild("Bone_" .. s[1])
		motors[i] = bone and bone:FindFirstChild(s[1]) :: Motor6D
		parts[i] = {}
		if bone then
			boneIndex[bone] = i
		end
	end
	-- V87: один обход деталей вместо обхода на каждый сегмент
	for _, d in model:GetDescendants() do
		if d:IsA("WeldConstraint") then
			local i = d.Part0 and boneIndex[d.Part0]
			if i and d.Part1 then
				table.insert(parts[i], d.Part1)
			end
		end
	end
	local rootBone = rigFolder:FindFirstChild("Root")
	return setmetatable({ model = model, data = data, motors = motors, rootMotor = rootBone and rootBone:FindFirstChild("Root"), parts = parts, frame = 1, rate = 1 }, RigMeta)
end

-- Куст биома с костями; клипы Tease_Common/Rare/Epic, Open_Burst, Open_Part
function Lib.bush(biome: number): (Model?, any?)
	local data = Lib.bushData(biome)
	local src = root:FindFirstChild("Bushes") and root.Bushes:FindFirstChild(string.format("bush_%02d", biome))
	if not data or not src then
		return nil, nil
	end
	local model = src:Clone()
	model.Name = "Bush87_" .. biome
	local rig = newRig(model, data)
	model:SetAttribute("Art87", true)
	model:SetAttribute("BiomeId", biome)
	return model, rig
end

---------------------------------------------------------------------
-- Эффекты из ключей (пыль, листья, вспышки, свет). fx = data.fx (зверь или куст), group — фильтр по группе
-- ("" = все), origin — CFrame точки, к которой привязаны ключи (место зверя или центр куста).
-- Возвращает папку; эффекты сами исчезают после последнего ключа.
---------------------------------------------------------------------
local FX_MAT = {
	studs = Enum.Material.SmoothPlastic,
	smooth = Enum.Material.SmoothPlastic,
	neon = Enum.Material.Neon,
	ghost = Enum.Material.Neon,
}
local active: { any } = {}

-- Меш эффекта из библиотеки fx_<ключ>: модель узла называется "<библиотека>_<base>", внутри MeshPart.
-- Сначала точное имя, иначе самое длинное общее начало (имена вида eye_70_- после экспорта). Кэш по библиотеке.
local tplCache: { [Instance]: { [string]: BasePart | false } } = {}
local function fxTemplate(lib: Instance?, base: string): BasePart?
	if not lib then
		return nil
	end
	local cache = tplCache[lib]
	if not cache then
		cache = {}
		tplCache[lib] = cache
	end
	local hit = cache[base]
	if hit ~= nil then
		return hit or nil
	end
	local prefix = lib.Name .. "_"
	local want = prefix .. base
	local node = lib:FindFirstChild(want)
	if not node then
		local best, bestLen = nil, 0
		for _, c in lib:GetChildren() do
			local n = c.Name
			local l = 0
			for i = 1, math.min(#n, #want) do
				if string.byte(n, i) ~= string.byte(want, i) then
					break
				end
				l = i
			end
			if l > #prefix and l > bestLen then
				best, bestLen = c, l
			end
		end
		node = best
	end
	local mp: BasePart? = nil
	if node then
		mp = if node:IsA("BasePart") then node :: BasePart else node:FindFirstChildWhichIsA("BasePart", true)
	end
	cache[base] = mp or false
	return mp
end

function Lib.playFx(fx: { any }, origin: CFrame, opts: any?): Folder
	local o = opts or {}
	local folder = Instance.new("Folder")
	folder.Name = "Art87Fx"
	folder.Parent = o.parent or workspace
	local lib = o.lib
	local scale = o.scale or 1
	local items = {}
	local last = 1
	local cap = o.max or 120
	for _, f in fx do
		if #items >= cap then
			break
		end
		local group = f[2]
		if o.group and o.group ~= "" and not string.find(group, o.group, 1, true) then
			continue
		end
		local inst: Instance
		if f[8] == "light" then
			local holder = Instance.new("Part")
			holder.Transparency = 1
			holder.Size = Vector3.one * 0.1
			holder.Anchored = true
			holder.CanCollide = false
			holder.CanQuery = false
			holder.CanTouch = false
			local l = Instance.new("PointLight")
			l.Color = Color3.fromHex(f[7])
			l.Range = 14 * scale
			l.Brightness = 0
			l.Shadows = false
			l.Parent = holder
			inst = holder
		else
			local tpl = fxTemplate(lib, f[3])
			local p: BasePart
			if tpl then
				p = tpl:Clone()
				for _, c in p:GetChildren() do
					if not c:IsA("SurfaceAppearance") then
						c:Destroy()
					end
				end
			else
				p = Instance.new("Part")
			end
			p.Anchored = true
			p.CanCollide = false
			p.CanQuery = false
			p.CanTouch = false
			p.CastShadow = false
			p.Color = Color3.fromHex(f[7])
			p.Material = FX_MAT[f[8]] or Enum.Material.SmoothPlastic
			if f[8] == "ghost" then
				p.Transparency = 0.4
			end
			p.Size = Vector3.new(math.max(f[4], 0.02), math.max(f[5], 0.02), math.max(f[6], 0.02)) * scale
			p.Transparency = 1
			inst = p
		end
		inst.Parent = folder
		local it = { inst = inst, f = f, size = Vector3.new(f[4], f[5], f[6]) * scale }
		for _, key in { "loc", "scale", "rot" } do
			local tr = f[key]
			if tr and #tr >= 5 then
				last = math.max(last, tr[#tr - 4])
			end
		end
		if f.alpha and #f.alpha >= 2 then
			last = math.max(last, f.alpha[#f.alpha - 1])
		end
		if f.energy and #f.energy >= 2 then
			last = math.max(last, f.energy[#f.energy - 1])
		end
		table.insert(items, it)
	end
	local job = { folder = folder, items = items, origin = origin, scale = scale, frame = o.startFrame or 1, last = o.endFrame or last }
	table.insert(active, job)
	return folder
end

local function stepFx(job: any, dt: number): boolean
	job.frame += dt * FPS
	local f = job.frame
	if f > job.last or not job.folder.Parent then
		job.folder:Destroy()
		return false
	end
	local cfs, parts = {}, {}
	for _, it in job.items do
		local d = it.f
		local x, y, z = 0, 0, 0
		if d.loc then
			x, y, z = sample3(d.loc, f)
		end
		local cf = job.origin * CFrame.new(x * job.scale, y * job.scale, z * job.scale)
		if d.rot then
			local rx, ry, rz = sample3(d.rot, f)
			cf *= euler(rx, ry, rz)
		end
		local inst = it.inst
		if d[8] == "light" then
			inst.CFrame = cf
			local l = inst:FindFirstChildOfClass("PointLight")
			if l and d.energy then
				l.Brightness = math.min(sample1(d.energy, f), 12)
			end
		else
			local sx, sy, sz = 1, 1, 1
			if d.scale then
				sx, sy, sz = sample3(d.scale, f)
			end
			local visible = (sx + sy + sz) > 0.02
			local a = if d.alpha then sample1(d.alpha, f) else 1
			inst.Transparency = if visible then math.clamp(1 - a + (if d[8] == "ghost" then 0.35 else 0), 0, 1) else 1
			if visible then
				inst.Size = Vector3.new(math.max(it.size.X * sx, 0.01), math.max(it.size.Y * sy, 0.01), math.max(it.size.Z * sz, 0.01))
			end
			table.insert(parts, inst)
			table.insert(cfs, cf)
		end
	end
	if #parts > 0 then
		workspace:BulkMoveTo(parts, cfs, Enum.BulkMoveMode.FireCFrameChanged)
	end
	return true
end

RunService.Heartbeat:Connect(function(dt)
	for i = #active, 1, -1 do
		local ok, alive = pcall(stepFx, active[i], dt)
		if not ok or not alive then
			if not ok then
				warn("[Art87] fx: " .. tostring(alive))
				pcall(function()
					active[i].folder:Destroy()
				end)
			end
			table.remove(active, i)
		end
	end
end)

-- Готовые библиотеки эффектов
function Lib.fxLib(key: string): Instance?
	local f = root:FindFirstChild("FX")
	return f and f:FindFirstChild(key) or nil
end

return Lib
