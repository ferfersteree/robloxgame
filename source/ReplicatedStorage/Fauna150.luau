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

-- V87: новые звери Claude Design (Art87.Lib). Lib подключается лениво и под pcall: нет мешей/данных — старый путь.
local LibMod: any = nil
local libTried = false
local function art(): any?
	if not libTried then
		libTried = true
		local folder = RS:FindFirstChild("Art87")
		local mod = folder and folder:FindFirstChild("Lib")
		if mod and folder and folder:FindFirstChild("Data") then
			local ok, res = pcall(require, mod)
			if ok then
				LibMod = res
			else
				warn("[Fauna150] Art87.Lib: " .. tostring(res))
			end
		end
	end
	return LibMod
end

local newHas: { [string]: boolean } = {}
local function hasNew(id: string): boolean
	local c = newHas[id]
	if c == nil then
		local L = art()
		local ok, has = false, false
		if L then
			ok, has = pcall(L.hasAnimal, id)
		end
		c = ok and has == true
		newHas[id] = c
	end
	return c
end

-- V87: размеры нового зверя в формате старых данных (h/w/len/bounds), нужны Attr, WorldScale и Reveal через Factory.Get
local newData: { [string]: any } = {}
local function getNew(id: string): any?
	local c = newData[id]
	if c ~= nil then
		return c or nil
	end
	if not hasNew(id) then
		return nil
	end
	local L = art()
	local ok, ad = pcall(L.animalData, id)
	if not ok or not ad then
		newHas[id] = false
		return nil
	end
	local w, h, len = ad.width or 1, ad.height or 1, ad.length or 1
	local d = {
		art87 = true, h = h, w = w, len = len, hover = ad.hover or 0, rig = "art87",
		bounds = { { -w / 2, 0, -len / 2 }, { w / 2, h, len / 2 } },
		animation = { profile = "art87" },
	}
	newData[id] = d
	return d
end

function Fauna.Has(id: string): boolean
	return hasNew(id) or (Profiles[id] ~= nil and renderData:FindFirstChild(id) ~= nil)
end

local function getOld(id: string): any?
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

-- V87: сначала новый зверь (если есть меши), иначе прежние данные коллекции
function Fauna.Get(id: string): any?
	return getNew(id) or getOld(id)
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
-- V61: размер в мире. Рисунки моделей нормированы для карточек, а в сцене зверь должен быть настоящего размера рядом с игроком.
-- Значения лежат в tools/creature_data.py (python tools/creature_data.py patch перепишет блок ниже).
---------------------------------------------------------------------
-- BEGIN V61 SIZES (tools/creature_data.py)
local SIZE_M: { [string]: number } = {
	rabbit = 0.45,
	squirrel = 0.35,
	hedgehog = 0.25,
	fox = 1.0,
	dodo = 0.9,
	moonrabbit = 0.55,
	roe = 1.2,
	boar = 1.5,
	badger = 0.75,
	wolf = 1.4,
	lynx = 1.0,
	sabertooth = 2.0,
	deer = 2.0,
	moose = 3.0,
	bear = 2.0,
	bison = 3.0,
	cavebear = 2.6,
	spiritdeer = 2.4,
	megadeer = 3.2,
	rhino = 3.5,
	mammoth = 5.5,
	cavelion = 2.8,
	icemammoth = 6.0,
	yeti = 2.8,
	gazelle = 1.4,
	hyena = 1.4,
	sunlion = 2.4,
	mountain_goat = 1.5,
	armadillo = 0.6,
	canyon_condor = 1.2,
	fennec = 0.6,
	dune_scorpion = 0.6,
	sand_wyrm = 5.0,
	toucan = 0.65,
	jaguar = 1.7,
	jungle_gorilla = 1.7,
	otter = 1.2,
	crocodile = 3.5,
	marsh_hydra = 3.5,
	storm_ram = 1.6,
	thunder_eagle = 1.1,
	storm_griffin = 3.0,
	sea_turtle = 1.4,
	sea_lion = 2.0,
	coral_wyvern = 3.0,
	reef_ray = 1.8,
	hammer_shark = 3.0,
	abyss_leviathan = 7.0,
	ash_lizard = 0.9,
	ember_boar = 1.8,
	lava_golem = 3.5,
	obsidian_crab = 1.4,
	magma_rhino = 3.8,
	phoenix = 2.2,
	crystal_bat = 1.0,
	amethyst_fox = 1.2,
	quartz_dragon = 5.0,
	arctic_hare = 0.7,
	lunar_wolf = 1.8,
	aurora_bear = 2.8,
	cloud_sheep = 1.4,
	sky_stag = 2.8,
	sky_drake = 4.0,
	dusk_panther = 1.9,
	shadow_mantis = 2.0,
	void_behemoth = 5.0,
	comet_fox = 1.3,
	stellar_stag = 3.0,
	astral_dragon = 6.0,
	watchful_meerkat = 0.4,
	savanna_ostrich = 2.4,
	amber_giraffe = 5.0,
	rock_hyrax = 0.5,
	canyon_roadrunner = 0.7,
	redthorn_lizard = 0.4,
	oasis_scarab = 0.4,
	dune_jerboa = 0.2,
	mirage_camel = 3.0,
	jade_tapir = 2.0,
	leafcutter_ant = 0.5,
	emerald_treefrog = 0.4,
	mudskipper = 0.3,
	mangrove_fiddler = 0.4,
	mangrove_flamingo = 1.5,
	storm_stone_spider = 1.8,
	highland_yak = 2.5,
	tempest_pterosaur = 2.5,
	spiral_hermit_crab = 1.0,
	lagoon_pelican = 1.4,
	azure_horseshoe_crab = 0.6,
	pearl_nautilus = 1.4,
	coral_seahorse = 2.0,
	reef_lobster = 1.2,
	cinder_porcupine = 1.1,
	ash_anteater = 1.8,
	ember_mandrill = 1.7,
	furnace_stag_beetle = 0.9,
	caldera_toad = 1.0,
	obsidian_pangolin = 1.6,
	prism_moth = 1.2,
	geode_mole = 1.0,
	crystal_anemone = 1.4,
	aurora_weasel = 0.9,
	moon_owl = 1.4,
	tundra_muskox = 2.2,
	aether_ribbonfish = 2.0,
	island_chameleon = 0.8,
	cloud_glider = 2.2,
	void_lamprey = 1.8,
	gloom_sloth = 1.3,
	rift_axolotl = 0.9,
	nebula_tardigrade = 0.8,
	astral_starfish = 1.0,
	orbital_jellyfish = 2.0,
	spring_strider = 2.2,
	copper_weevil = 1.0,
	gear_sentinel = 4.0,
	magnet_tripod = 2.6,
	iron_hound = 2.0,
	clockwork_basilisk = 4.0,
	shelf_millipede = 1.2,
	peat_leech = 0.9,
	lantern_slug = 1.2,
	mycelium_bloomstalker = 2.8,
	spore_marauder = 3.0,
	cap_mantis = 2.2,
	fossil_trilobite = 0.5,
	dune_ankylosaur = 4.0,
	fossil_ceratopsian = 5.0,
	skeletal_colossus = 7.0,
	sand_reaper = 3.5,
	bone_vulture = 2.0,
	abyss_sea_urchin = 1.0,
	citadel_cuttlefish = 1.2,
	cathedral_clam = 1.6,
	trench_angler = 3.0,
	pressure_colossus = 6.0,
	abyss_octopus = 3.0,
	fulgurite_cricket = 1.0,
	rift_kangaroo = 2.2,
	thunder_centaur = 3.2,
	prism_revenant = 3.2,
	storm_harrier = 1.6,
	rift_serpent = 6.0,
	caldera_tarsier = 0.9,
	ember_salamander = 1.8,
	magma_hippo = 3.5,
	lava_dragonfly = 1.5,
	volcanic_wyrm = 8.0,
	primordial_titan = 12.0,
}
-- END V61 SIZES

local STUDS_PER_M = 3.0 -- игрок ростом 1,8 м занимает около 5,4 студа
local MIN_STUDS, MAX_STUDS = 1.0, 36

-- Во сколько раз нарисованную модель нужно увеличить или уменьшить, чтобы она была настоящего размера;
-- size (необязательно): множитель конкретной особи, см. SizeFromWeight.
function Fauna.WorldScale(id: string, size: number?): number
	local d = Fauna.Get(id)
	local m = SIZE_M[id]
	local k = size or 1
	if not d or not m then
		return k
	end
	local biggest = math.max(d.h, d.len, 0.5)
	-- гиганты крупнее вида, но не выше 48 студов
	local target = math.min(math.clamp(m * STUDS_PER_M, MIN_STUDS, MAX_STUDS) * k, 48)
	return target / biggest
end

-- Настоящий размер вида в студах (самая большая сторона)
function Fauna.WorldStuds(id: string): number?
	local m = SIZE_M[id]
	return m and math.clamp(m * STUDS_PER_M, MIN_STUDS, MAX_STUDS) or nil
end

-- Размер конкретной особи по её весу: никогда меньше обычного (x1,0), тяжёлые крупнее; верхняя пятая весового
-- диапазона даёт «гигантов» (до x1,7). Одно и то же число считается везде (сцена, чужие игроки), сохранять его не нужно.
function Fauna.SizeFromWeight(id: string, w: number?): number
	if type(w) ~= "number" then
		return 1
	end
	local sp = require(RS:WaitForChild("Shared"):WaitForChild("Config")).SPECIES_BY_ID[id]
	if not sp or sp.wMax <= sp.wMin then
		return 1
	end
	local r = math.clamp((w - sp.wMin) / (sp.wMax - sp.wMin), 0, 1)
	local giant = math.clamp((r - 0.8) / 0.2, 0, 1)
	return 1 + 0.3 * r + 0.4 * giant * giant
end

function Fauna.IsGiant(size: number): boolean
	return size >= 1.25
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
	-- V87: новая модель Claude Design; не собралась — прежний кубический зверь
	if hasNew(id) then
		local ok, model = pcall(art().animal, id)
		if ok and model then
			return model
		end
		newHas[id] = false
		newData[id] = nil
	end
	local data = getOld(id)
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

---------------------------------------------------------------------
-- V87: адаптер для зверей Art87: клипы Idle/Reveal из Lib, ходьба = Idle быстрее + процедурное подпрыгивание корня
---------------------------------------------------------------------
-- f: циклов фазы в секунду, a: подъём корня в долях роста, roll/pitch: наклоны (рад), hop: прыжок (парабола), wave: плавное качание
local BOB: { [string]: any } = {
	walk = { f = 2.6, a = 0.035, roll = 0.035, pitch = 0 },
	run = { f = 4.2, a = 0.05, roll = 0.04, pitch = 0.03 },
	flee = { f = 4.5, a = 0.05, roll = 0.04, pitch = 0.03 },
	hop = { f = 3.0, a = 0.16, roll = 0, pitch = 0.1, hop = true },
	crawl = { f = 2.0, a = 0.012, roll = 0.03, pitch = 0 },
	swim = { f = 1.2, a = 0.03, roll = 0.05, pitch = 0.02, wave = true },
	fly = { f = 1.6, a = 0.04, roll = 0.05, pitch = 0.03, wave = true },
}
local MOVE_RATE: { [string]: number } = { walk = 1.4, crawl = 1.4, swim = 1.4, hop = 1.6, fly = 1.6, run = 1.8, flee = 1.8 }

local function bindNew(model: Model): any
	local rig: any = art().bind(model)
	if not rig then
		return { play = function() end, step = function() end, destroy = function() end }
	end
	local height = (model:GetAttribute("Height") :: number?) or 2
	local adapter: any = { rig = rig, state = "idle", rate = 1, bob = nil, ph = math.random(), revealing = false, dirty = false }

	-- idle/look/stand/sleep/happy — Idle; движение — Idle быстрее + подпрыгивание в step
	function adapter:play(state: string)
		if state == self.state then
			return
		end
		self.state = state
		self.rate = MOVE_RATE[state] or 1
		self.bob = BOB[state]
		if not self.revealing and rig.clip ~= "Idle" then
			rig:play("Idle", true)
		end
	end

	function adapter:step(dt: number, speed: number?)
		local sp = math.clamp(speed or 1, 0.5, 1.6)
		local b = self.bob
		if self.revealing or not b then
			rig.rate = 1
		else
			rig.rate = self.rate * sp
		end
		rig:step(dt)
		local rm: Motor6D? = rig.rootMotor
		if not rm or self.revealing then
			return
		end
		if not b then
			if self.dirty and rig.clip == nil then
				rm.Transform = CFrame.identity
				self.dirty = false
			end
			return
		end
		-- V87: Motor6D.Transform не масштабируется ScaleTo, поэтому рост берём в мировых единицах
		local ph = (self.ph + dt * b.f * sp) % 1
		self.ph = ph
		local off, pitch
		if b.hop then
			off = math.sin(ph * math.pi)
			pitch = math.sin(ph * math.pi * 2) * b.pitch
		elseif b.wave then
			off = math.sin(ph * math.pi * 2)
			pitch = off * b.pitch
		else
			off = math.abs(math.sin(ph * math.pi))
			pitch = b.pitch * off
		end
		local roll = math.sin(ph * math.pi * 2) * b.roll
		local base = rm.Transform
		if rig.clip == nil then
			base = CFrame.identity
			self.dirty = true
		end
		rm.Transform = base * CFrame.new(0, off * b.a * height * model:GetScale(), 0) * CFrame.Angles(pitch, 0, roll)
	end

	-- Появление: клип Reveal один раз, потом снова Idle/текущее состояние
	function adapter:reveal(onDone: (() -> ())?)
		self.revealing = true
		rig.rate = 1
		rig:play("Reveal", false, function()
			self.revealing = false
			if rig.dead then
				return
			end
			rig:play("Idle", true)
			if onDone then
				onDone()
			end
		end)
	end

	function adapter:destroy()
		rig:destroy()
	end

	-- стартовая фаза Idle случайная: звери рядом не качаются в унисон
	rig:play("Idle", true)
	rig.frame = 1 + math.random() * math.max(rig:length("Idle") - 1, 1)
	return adapter
end

function Fauna.Bind(model: Model): any
	if model:GetAttribute("Art87") == true and art() then
		return bindNew(model)
	end
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
