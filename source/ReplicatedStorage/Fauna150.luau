-- ReplicatedStorage/Fauna150
-- Единая фауна игры: 150 видов коллекции (SpearHunt_RenderData) + анатомические профили Animation150.
-- Модель собирается из данных (без task.wait, безопасно вызывать из интерфейса), двигается через Animation150.Motion.
-- Старые V16Fauna/ModelsData и ReplicatedStorage.Animals больше не используются.
local HttpService = game:GetService("HttpService")
local RS = game:GetService("ReplicatedStorage")

local Fauna = {}

local renderData = RS:WaitForChild("SpearHunt_RenderData")
local library = RS:WaitForChild("Animation150")
local Profiles = require(library:WaitForChild("Profiles")) :: any
local Motion = require(library:WaitForChild("Motion")) :: any

---------------------------------------------------------------------
-- Данные: геометрия коллекции + кости и походка из профиля
---------------------------------------------------------------------
local decoded: { [string]: any } = {}

function Fauna.Has(id: string): boolean
	return Profiles[id] ~= nil and renderData:FindFirstChild(id) ~= nil
end

function Fauna.Get(id: string): any?
	local cached = decoded[id]
	if cached ~= nil then
		return cached or nil
	end
	local profile = Profiles[id]
	local source = renderData:FindFirstChild(id)
	if not profile or not source or not source:IsA("StringValue") then
		decoded[id] = false
		return nil
	end
	local data = HttpService:JSONDecode(source.Value)
	data.groups = profile.groups
	data.bounds = profile.bounds
	data.h = profile.height
	data.w = profile.bounds[2][1] - profile.bounds[1][1]
	data.len = profile.bounds[2][3] - profile.bounds[1][3]
	data.rig = profile.mode
	data.zone = profile.biome
	data.animation = { profile = profile.gait }
	decoded[id] = data
	return data
end

-- Размеры и смещения, которые раньше лежали атрибутами на ReplicatedStorage.Animals.<id>
function Fauna.Attr(id: string, name: string): number?
	local d = Fauna.Get(id)
	if not d then
		return nil
	end
	if name == "Height" or name == "BoundsY" then
		return d.h
	elseif name == "BoundsX" or name == "Width" then
		return d.w
	elseif name == "BoundsZ" or name == "Len" then
		return d.len
	elseif name == "MinY" then
		return d.bounds[1][2]
	end
	return nil
end

---------------------------------------------------------------------
-- Модель (порт CollectionTools/Factory без пауз)
---------------------------------------------------------------------
local function part(name: string, size: Vector3, cf: CFrame, visible: boolean): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cf
	p.Anchored = false
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false -- звери не мешают лучам (выстрелы, брызги от копья)
	p.Massless = true
	p.CastShadow = visible
	if not visible then
		p.Transparency = 1
	end
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	return p
end

local function joint(child: BasePart, parent: BasePart)
	local motor = Instance.new("Motor6D")
	motor.Name = "Joint"
	motor.Part0 = parent
	motor.Part1 = child
	motor.C0 = parent.CFrame:ToObjectSpace(child.CFrame)
	motor.C1 = CFrame.identity
	motor.Parent = child
end

function Fauna.Create(id: string): Model?
	local data = Fauna.Get(id)
	if not data then
		return nil
	end
	local model = Instance.new("Model")
	model.Name = id
	local attrs: { [string]: any } = {
		SpeciesId = id, AssetId = id, AssetKind = "animal", DisplayName = data.displayName, BiomeId = data.zone,
		NativeV16 = true, NativeV15 = true, Fauna150 = true, GeometryVersion = 17, LocomotionProfile = data.animation.profile,
		SourcePartCount = #data.parts / 11, Height = data.h, Width = data.w, Len = data.len,
		BoundsX = data.w, BoundsY = data.h, BoundsZ = data.len, MinY = data.bounds[1][2],
		GroundOffsetY = 0, Rig = data.rig,
	}
	for k, v in attrs do
		model:SetAttribute(k, v)
	end
	local rig = Instance.new("Folder")
	rig.Name = "Rig"
	rig.Parent = model
	local root = part("B001_Root", Vector3.one * 0.01, CFrame.identity, false)
	root.Anchored = true
	root:SetAttribute("BoneIndex", 1)
	root.Parent = rig
	model.PrimaryPart = root
	local actor = part("B002_ActorBody", Vector3.one * 0.01, CFrame.identity, false)
	actor:SetAttribute("BoneIndex", 2)
	actor.Parent = rig
	joint(actor, root)
	local bones = {}
	for i, g in data.groups do
		local bone = part(string.format("B%03d_%s", i + 2, g.n), Vector3.one * 0.01, CFrame.new(table.unpack(g.j)), false)
		bone:SetAttribute("BoneIndex", i + 2)
		bone:SetAttribute("AnatomicalKind", g.kind or g.n)
		bone.Parent = rig
		bones[i] = bone
	end
	for i, g in data.groups do
		joint(bones[i], if g.p >= 0 then bones[g.p + 1] else actor)
	end
	local geometry = Instance.new("Model")
	geometry.Name = "Geometry"
	geometry.WorldPivot = CFrame.identity
	geometry.Parent = model
	local groups = {}
	for i, g in data.groups do
		local group = Instance.new("Model")
		group.Name = g.n
		group.WorldPivot = CFrame.new(table.unpack(g.j))
		group:SetAttribute("AnatomyGroup", i - 1)
		group.Parent = geometry
		groups[i] = group
	end
	local d = data.parts
	for i = 1, #d, 11 do
		local n = (i - 1) / 11 + 1
		local meta = data.partMeta[n]
		local anchor = meta.rigidAnchor or d[i]
		local cf = CFrame.new(d[i + 4], d[i + 5], d[i + 6])
		local ri = d[i + 10]
		if ri >= 0 then
			local q = ri * 9 + 1
			local r = data.rots
			cf = CFrame.new(d[i + 4], d[i + 5], d[i + 6], r[q], r[q + 1], r[q + 2], r[q + 3], r[q + 4], r[q + 5], r[q + 6], r[q + 7], r[q + 8])
		end
		local p = part(meta.semantic .. "_" .. n, Vector3.new(d[i + 1], d[i + 2], d[i + 3]), cf, true)
		local color = d[i + 7]
		p.Color = Color3.fromRGB(math.floor(color / 65536) % 256, math.floor(color / 256) % 256, color % 256)
		p.Material = if meta.material == "glow" then Enum.Material.Neon else Enum.Material.Plastic
		local surface = if meta.studs ~= false and meta.material ~= "glow" then Enum.SurfaceType.Inlet else Enum.SurfaceType.Smooth
		p.TopSurface = surface
		p.BottomSurface = surface
		p.FrontSurface = surface
		p.BackSurface = surface
		p.LeftSurface = surface
		p.RightSurface = surface
		p:SetAttribute("SourcePartIndex", n)
		p:SetAttribute("RigidBone", anchor + 1)
		p:SetAttribute("Semantic", meta.semantic)
		p.Parent = groups[anchor + 1]
		local weld = Instance.new("Weld")
		weld.Name = "RigidCube"
		weld.Part0 = bones[anchor + 1]
		weld.Part1 = p
		weld.C0 = bones[anchor + 1].CFrame:ToObjectSpace(cf)
		weld.C1 = CFrame.identity
		weld.Parent = p
	end
	local controller = Instance.new("AnimationController")
	controller.Name = "AnimationController"
	controller.Parent = model
	Instance.new("Animator").Parent = controller
	return model
end

-- Готовый шаблон для карточек и вьюпортов (не показывается в мире; потребители клонируют)
local templates: { [string]: any } = {}
function Fauna.Template(id: string): Model?
	local t = templates[id]
	if t == nil then
		t = Fauna.Create(id) or false
		templates[id] = t
	end
	return t or nil
end

---------------------------------------------------------------------
-- Движение: Animation150.Motion за интерфейсом, который ждёт AnimalRig (play/step/destroy)
---------------------------------------------------------------------
local STATE = {
	idle = "Idle", look = "Idle", stand = "Idle", sleep = "Idle", happy = "Idle",
	walk = "Move", hop = "Move", fly = "Move", swim = "Move", crawl = "Move",
	run = "FastMove", flee = "FastMove",
}

-- Модель могла быть увеличена/уменьшена (ScaleTo): длины профиля масштабируем так же
local function scaledProfile(p: any, s: number): any
	local c = table.clone(p)
	c.stride = p.stride * s
	c.height = p.height * s
	c.length = p.length * s
	local groups = table.create(#p.groups)
	for i, g in p.groups do
		local ng = table.clone(g)
		ng.j = { g.j[1] * s, g.j[2] * s, g.j[3] * s }
		groups[i] = ng
	end
	c.groups = groups
	return c
end

local function staticAdapter(): any
	return { play = function() end, step = function() end, destroy = function() end }
end

function Fauna.Bind(model: Model): any
	local id = model:GetAttribute("SpeciesId") or model.Name
	local base = Profiles[id]
	if not base then
		return staticAdapter()
	end
	local scale = model:GetScale()
	local profile = if math.abs(scale - 1) > 1e-3 then scaledProfile(base, scale) else base
	local ok, actor = pcall(Motion.Bind, model, profile)
	if not ok or not actor then
		warn("[Fauna150] motion for " .. tostring(id) .. ": " .. tostring(actor))
		return staticAdapter()
	end
	local native = {}
	function native:play(state: string)
		local target = STATE[state] or "Idle"
		if target == "FastMove" and not profile.fast then
			target = "Move"
		end
		if target ~= actor.state then
			actor:Play(target)
		end
	end
	function native:step(dt: number, speed: number?)
		actor.rate = speed or 1
		actor:Step(dt)
	end
	function native:destroy() end
	return native
end

return Fauna
