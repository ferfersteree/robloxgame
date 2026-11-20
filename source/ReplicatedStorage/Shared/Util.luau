-- ReplicatedStorage/Shared/Util.luau
local Config = require(script.Parent.Config)

local Util = {}

function Util.rarity(r: number)
	return Config.RARITIES[math.clamp(r, 1, #Config.RARITIES)]
end

function Util.deepCopy<T>(t: T): T
	if type(t) ~= "table" then
		return t
	end
	local c = {}
	for k, v in t :: any do
		c[k] = Util.deepCopy(v)
	end
	return (c :: any) :: T
end

-- Приварить все детали модели к root (WeldConstraint), сняв якоря
function Util.weldTo(root: BasePart, model: Instance)
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d ~= root then
			d.Anchored = false
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.Massless = true
			local w = Instance.new("WeldConstraint")
			w.Part0 = root
			w.Part1 = d
			w.Parent = d
		end
	end
end

function Util.flat(v: Vector3): Vector3
	return Vector3.new(v.X, 0, v.Z)
end

-- Перекрасить модель (мутации); вернуть функцию отката
function Util.recolor(model: Instance, color: Color3?, material: Enum.Material?): () -> ()
	local saved = {}
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d.Transparency < 1 then
			table.insert(saved, { d, d.Color, d.Material })
			if color then
				local h, s, v = d.Color:ToHSV()
				local ch, cs, cv = color:ToHSV()
				d.Color = Color3.fromHSV(ch, math.clamp(cs * 0.8 + s * 0.2, 0, 1), math.clamp(v * 0.55 + cv * 0.5, 0, 1))
				local _ = h
			end
			if material then
				d.Material = material
			end
		end
	end
	return function()
		for _, s in saved do
			s[1].Color = s[2]
			s[1].Material = s[3]
		end
	end
end

-- Мутация: золото — металл, радуга — переливы (атрибут Rainbow для клиента)
function Util.applyMutation(model: Instance, mut: string?)
	if mut == "gold" then
		Util.recolor(model, Config.MUTATIONS.gold.color, Enum.Material.Plastic)
	elseif mut == "rainbow" then
		local i = 0
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") and d.Transparency < 1 then
				i += 1
				local _, s, v = d.Color:ToHSV()
				d.Color = Color3.fromHSV((i * 0.07) % 1, math.max(0.55, s), math.max(0.8, v))
				d:SetAttribute("RainbowPhase", (i * 0.07) % 1)
			end
		end
		model:SetAttribute("Rainbow", true)
	end
end

-- V70: деталь гантели/стойки: без коллизий, на якоре
local function mkPart(name: string, size: Vector3, cf: CFrame, mat: Enum.Material, color: Color3, parent: Instance): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cf
	p.Material = mat
	p.Color = color
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

-- V82: деталь из конфига в двух форматах: Vector3/Enum/color (старый) или {x,y,z}/строка/rgb/neon (контракт V82)
local function vec3(v: any, fallback: Vector3): Vector3
	if typeof(v) == "Vector3" then
		return v
	elseif type(v) == "table" then
		return Vector3.new(tonumber(v[1]) or tonumber(v.x) or 0, tonumber(v[2]) or tonumber(v.y) or 0, tonumber(v[3]) or tonumber(v.z) or 0)
	end
	return fallback
end
local function normPart(spec: any): any
	local mat: Enum.Material = Enum.Material.SmoothPlastic
	if typeof(spec.material) == "EnumItem" then
		mat = spec.material
	elseif type(spec.material) == "string" then
		local ok, m = pcall(function()
			return (Enum.Material :: any)[spec.material]
		end)
		mat = if ok and typeof(m) == "EnumItem" then m else Enum.Material.Metal
	end
	if spec.neon == true then
		mat = Enum.Material.Neon
	end
	local col = Color3.fromRGB(160, 160, 160)
	if typeof(spec.color) == "Color3" then
		col = spec.color
	elseif type(spec.rgb) == "table" then
		col = Color3.fromRGB(tonumber(spec.rgb[1]) or 160, tonumber(spec.rgb[2]) or 160, tonumber(spec.rgb[3]) or 160)
	end
	return {
		name = tostring(spec.name or "Part"), shape = spec.shape or "Block",
		size = vec3(spec.size, Vector3.new(0.5, 0.5, 0.5)), offset = vec3(spec.offset, Vector3.zero),
		material = mat, color = col, weight = spec.weight == true, mirror = spec.mirror == true,
	}
end

-- Гантель уровня level (1..15). Гриф вдоль Z модели (X концепта -> Z), PrimaryPart "Grip" в начале координат.
-- V85: гантели и стенды из мешей Claude Design (ReplicatedStorage.GymMeshes: DB_01..DB_15, ST_01..ST_15).
-- Меши загружены в Roblox и вставлены в место; если папки или модели нет, строим прежние модели из деталей.
-- Эффекты повторяют таблицу дизайнера (docs/concepts_v83/fx_table.md) без Beam и Trail: только свет и частицы.
local MESH_FX: { [number]: { c: Color3, rate: number, light: boolean } } = {
	[1] = { c = Color3.fromRGB(255, 242, 168), rate = 0.6, light = false },
	[3] = { c = Color3.fromRGB(255, 214, 120), rate = 0.8, light = false },
	[5] = { c = Color3.fromRGB(62, 240, 192), rate = 1.5, light = true },
	[6] = { c = Color3.fromRGB(255, 211, 77), rate = 2.5, light = true },
	[7] = { c = Color3.fromRGB(230, 244, 255), rate = 2, light = false },
	[8] = { c = Color3.fromRGB(185, 140, 255), rate = 3, light = true },
	[9] = { c = Color3.fromRGB(168, 85, 255), rate = 3, light = true },
	[10] = { c = Color3.fromRGB(191, 234, 255), rate = 3.5, light = true },
	[11] = { c = Color3.fromRGB(255, 122, 26), rate = 4, light = true },
	[12] = { c = Color3.fromRGB(159, 231, 255), rate = 4, light = true },
	[13] = { c = Color3.fromRGB(77, 255, 158), rate = 4, light = true },
	[14] = { c = Color3.fromRGB(232, 228, 255), rate = 4.5, light = true },
	[15] = { c = Color3.fromRGB(255, 90, 30), rate = 5, light = true },
}
local function meshSource(kind: string, tier: number): Model?
	local RS = game:GetService("ReplicatedStorage")
	local lib = RS:FindFirstChild("GymMeshes")
	local src = lib and lib:FindFirstChild(string.format("%s_%02d", kind, tier))
	return if src and src:IsA("Model") then src else nil
end
local function biggestPart(m: Model): BasePart?
	local best, bv = nil, -1
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") and d.Transparency < 1 then
			local v = d.Size.X * d.Size.Y * d.Size.Z
			if v > bv then
				best, bv = d, v
			end
		end
	end
	return best
end
local function addMeshFx(m: Model, tier: number, scale: number)
	local fx = MESH_FX[tier]
	local host = biggestPart(m)
	if not fx or not host then
		return
	end
	local e = Instance.new("ParticleEmitter")
	e.Name = "GymSparkle"
	e.Texture = "rbxasset://textures/sparkle.png"
	e.Color = ColorSequence.new(fx.c, Color3.new(1, 1, 1))
	e.LightEmission = 0.8
	e.Rate = fx.rate
	e.Lifetime = NumberRange.new(0.8, 1.6)
	e.Speed = NumberRange.new(0.2, 0.6)
	e.SpreadAngle = Vector2.new(180, 180)
	e.Shape = Enum.ParticleEmitterShape.Box
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.3, 0.32 * scale), NumberSequenceKeypoint.new(1, 0) })
	e.Transparency = NumberSequence.new(0.1, 1)
	e.Rotation = NumberRange.new(0, 360)
	e.RotSpeed = NumberRange.new(-80, 80)
	e.Parent = host
	if fx.light then
		local l = Instance.new("PointLight")
		l.Name = "GymGlow"
		l.Color = fx.c
		l.Brightness = 0.9
		l.Range = 5 * scale
		l.Shadows = false
		l.Parent = host
	end
end

function Util.dumbbell(level: number): Model
	local n = #Config.DUMBBELL_LOOK
	local lv0 = if level == level then level else 1
	local tier0 = math.clamp(math.floor(lv0), 1, n)
	local src = meshSource("DB", tier0)
	if src then
		-- меш: гриф вдоль X, начало в центре хвата; как у прежней модели — гриф вдоль Z и невидимый Grip в центре
		local m = src:Clone()
		m.Name = "Dumbbell"
		m:SetAttribute("Tier", tier0)
		m:SetAttribute("Mesh", true)
		m:PivotTo(CFrame.Angles(0, math.rad(90), 0))
		local grip = mkPart("Grip", Vector3.new(0.2, 0.2, 0.2), CFrame.new(), Enum.Material.SmoothPlastic, Color3.new(1, 1, 1), m)
		grip.Transparency = 1
		grip.CastShadow = false
		m.PrimaryPart = grip
		m.WorldPivot = CFrame.new()
		addMeshFx(m, tier0, 1)
		return m
	end
	return Util.dumbbellParts(tier0)
end

-- прежняя модель из деталей Config.DUMBBELL_LOOK (запасной путь)
function Util.dumbbellParts(level: number): Model
	local n = #Config.DUMBBELL_LOOK
	local lv = if level == level then level else 1
	local tier = math.clamp(math.floor(lv), 1, n)
	local look = Config.DUMBBELL_LOOK[tier]
	local m = Instance.new("Model")
	m.Name = "Dumbbell"
	m:SetAttribute("Tier", tier)
	local grip = mkPart("Grip", Vector3.new(0.2, 0.2, 0.2), CFrame.new(), Enum.Material.SmoothPlastic, look.color, m)
	grip.Transparency = 1
	grip.CastShadow = false
	for _, raw in look.parts do
		local spec = normPart(raw)
		local sides = spec.mirror and { 1, -1 } or { 1 }
		for _, sd in sides do
			local pos = Vector3.new(spec.offset.Z, spec.offset.Y, spec.offset.X * sd)
			local part: Part
			if spec.shape == "Cylinder" then
				part = mkPart(spec.name, spec.size, CFrame.new(pos) * CFrame.Angles(0, math.rad(90), 0), spec.material, spec.color, m)
				part.Shape = Enum.PartType.Cylinder
			elseif spec.shape == "Ball" then
				part = mkPart(spec.name, spec.size, CFrame.new(pos), spec.material, spec.color, m)
				part.Shape = Enum.PartType.Ball
			else
				-- Block и Wedge (клин как блок: свой WedgePart не нужен для гантелей)
				part = mkPart(spec.name, Vector3.new(spec.size.Z, spec.size.Y, spec.size.X), CFrame.new(pos), spec.material, spec.color, m)
			end
			if spec.weight then
				part:SetAttribute("Weight", true)
			end
			part:SetAttribute("OrigColor", spec.color)
			part:SetAttribute("OrigMaterial", spec.material.Name)
		end
	end
	m.PrimaryPart = grip
	return m
end

-- V85: стенд из меша уровня: начало = середина пола, +Z к игроку; текущая пара на месте из данных дизайнера (PairX, PairY)
local function meshRack(lv: number): Model?
	local src = meshSource("ST", lv)
	if not src then
		return nil
	end
	local rack = src:Clone()
	rack.Name = "GymRack"
	rack:SetAttribute("Level", lv)
	rack:SetAttribute("Mesh", true)
	local cur = Instance.new("Model")
	cur.Name = "Tier" .. lv
	cur:SetAttribute("Tier", lv)
	local px = tonumber(src:GetAttribute("PairX")) or 2.2
	local py = tonumber(src:GetAttribute("PairY")) or 2.4
	for _, side in { -1, 1 } do
		local d = Util.dumbbell(lv)
		-- Util.dumbbell отдаёт гриф вдоль Z; на стенде гриф вдоль X, как у дизайнера
		d:PivotTo(CFrame.new(side * px, py, 0) * CFrame.Angles(0, math.rad(90), 0))
		d.Parent = cur
	end
	cur.Parent = rack
	local fx = MESH_FX[lv]
	if fx and fx.light then
		local host = biggestPart(rack)
		if host then
			local l = Instance.new("PointLight")
			l.Name = "StandGlow"
			l.Color = fx.c
			l.Brightness = 1.2
			l.Range = 12
			l.Shadows = false
			l.Parent = host
		end
	end
	rack.WorldPivot = CFrame.new()
	return rack
end

-- Стойка CAMP GYM: начало = середина пола, +Z к игроку. V82: вид по Config.GYM_STAND[level]; текущая пара на верхней полке.
function Util.gymRack(level: number?): Model
	local n = #Config.DUMBBELL_LOOK
	local lvRaw = level or 1
	local lv = math.clamp(math.floor(if lvRaw == lvRaw then lvRaw else 1), 1, n)
	local mr = meshRack(lv)
	if mr then
		return mr
	end
	local st = (Config.GYM_STAND and (Config.GYM_STAND[lv] or Config.GYM_STAND[1])) or {}
	local pal = st.palette or {}
	local mats = st.materials or {}
	local function mat(key: string, def: Enum.Material): Enum.Material
		local ok, m = pcall(function()
			return (Enum.Material :: any)[mats[key]]
		end)
		return if ok and typeof(m) == "EnumItem" then m else def
	end
	local cWood = pal.wood or Color3.fromRGB(181, 122, 71)
	local cTrim = pal.trim or Color3.fromRGB(125, 80, 46)
	local cStone = pal.stone or Color3.fromRGB(84, 98, 101)
	local cSign = pal.sign or Color3.fromRGB(44, 117, 108)
	local mWood, mTrim, mStone = mat("wood", Enum.Material.Wood), mat("trim", Enum.Material.Wood), mat("stone", Enum.Material.Slate)
	local rack = Instance.new("Model")
	rack.Name = "GymRack"
	rack:SetAttribute("Level", lv)
	local function blk(name: string, size: Vector3, c: Vector3, m: Enum.Material, col: Color3, solid: boolean?): Part
		local p = mkPart(name, size, CFrame.new(c), m, col, rack)
		p.CanCollide = solid == true
		return p
	end
	for _, sx in { -1, 1 } do
		for _, sz in { -1, 1 } do
			blk("Footing", Vector3.new(0.48, 0.32, 0.5), Vector3.new(4.72 * sx, 0.16, 1.23 * sz), mStone, cStone, true)
			blk("Upright", Vector3.new(0.28, 3.34, 0.3), Vector3.new(4.72 * sx, 1.99, 1.23 * sz), mTrim, cTrim, true)
		end
	end
	for _, y in { 0.40, 1.98, 3.56 } do
		blk("Deck", Vector3.new(9.72, 0.16, 2.94), Vector3.new(0, y, 0), mWood, cWood, true)
	end
	for _, y in { 0.23, 1.81, 3.39 } do
		for _, sz in { -1, 1 } do
			blk("Stringer", Vector3.new(9.5, 0.18, 0.2), Vector3.new(0, y, 1.13 * sz), mTrim, cTrim)
		end
	end
	for _, sx in { -1, 1 } do
		blk("SignPost", Vector3.new(0.18, 2.4, 0.18), Vector3.new(1.05 * sx, 4.74, -1.62), mTrim, cTrim) -- вывеска чуть позади, чтобы большая гантель её не задевала
	end
	local sign = blk("Sign", Vector3.new(2.6, 0.54, 0.14), Vector3.new(0, 5.66, -1.54), mWood, cSign)
	local gui = Instance.new("SurfaceGui")
	gui.Name = "SignGui"
	gui.Face = Enum.NormalId.Back -- +Z грань
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 100
	gui.LightInfluence = 0
	gui.Parent = sign
	local lbl = Instance.new("TextLabel")
	lbl.BackgroundTransparency = 1
	lbl.Size = UDim2.fromScale(1, 1)
	lbl.Text = "CAMP GYM"
	lbl.Font = Enum.Font.FredokaOne
	lbl.TextScaled = true
	lbl.TextColor3 = pal.signText or Color3.new(1, 1, 1)
	lbl.TextStrokeColor3 = Color3.fromRGB(20, 25, 32)
	lbl.TextStrokeTransparency = 0
	lbl.Parent = gui
	-- украшения стадии
	for _, raw in (st.extras or {}) do
		local ok, err = pcall(function()
			local spec = normPart(raw)
			for _, sd in (if spec.mirror then { 1, -1 } else { 1 }) do
				local p = mkPart(spec.name, spec.size, CFrame.new(spec.offset.X * sd, spec.offset.Y, spec.offset.Z), spec.material, spec.color, rack)
				p.CanCollide = false
				if spec.shape == "Cylinder" then
					p.Shape = Enum.PartType.Cylinder
				elseif spec.shape == "Ball" then
					p.Shape = Enum.PartType.Ball
				end
			end
		end)
		if not ok then
			warn("[Util.gymRack] extra: " .. tostring(err))
		end
	end
	-- текущая пара на верхней полке в полный размер (V82: раньше высота ограничивалась 1.25, и поздние уровни с рогами,
	-- кристаллами и бивнями выходили меньше деревянных); ставится нижней точкой на полку, а не центром грифа
	local cur = Instance.new("Model")
	cur.Name = "Tier" .. lv
	cur:SetAttribute("Tier", lv)
	local glowC = st.light or (Config.DUMBBELL_LOOK[lv] and Config.DUMBBELL_LOOK[lv].color) or Color3.new(1, 1, 1)
	local TOP = 3.64 -- верх верхней полки
	-- поставить модель нижней точкой на высоту y (гриф вдоль rot)
	local function standOn(d: Model, x: number, y: number, z: number, rot: CFrame)
		d:PivotTo(CFrame.new(x, y, z) * rot)
		local bcf, bsz = d:GetBoundingBox()
		local bottom = bcf.Position.Y - bsz.Y / 2
		d:PivotTo(CFrame.new(x, y + (y - bottom), z) * rot)
	end
	for _, side in { -1, 1 } do
		local d = Util.dumbbell(lv)
		local _, dsz = d:GetBoundingBox()
		local z = side * (dsz.X / 2 + 0.03) -- dsz.X — глубина головки: пара встаёт вплотную по глубине полки
		standOn(d, 0, TOP, z, CFrame.Angles(0, math.rad(-90), 0)) -- гриф вдоль X стойки
		d.Parent = cur
		local grip = d:FindFirstChild("Grip")
		if grip then
			local l = Instance.new("PointLight")
			l.Name = "TierGlow"
			l.Brightness = 1
			l.Range = 6
			l.Color = glowC
			l.Parent = grip
		end
	end
	-- прошлые уровни уменьшенными на нижних полках (как на превью дизайнера): гриф поперёк полки, по 6 на полку,
	-- самые новые сверху; больше 12 прошлых уровней не показываем
	local prev = Instance.new("Model")
	prev.Name = "PreviousTiers"
	local slot = 0
	for t = lv - 1, math.max(1, lv - 12), -1 do
		local ok, d = pcall(Util.dumbbell, t)
		if ok and d then
			local _, dsz = d:GetBoundingBox()
			-- в длину полки поперёк (2.6 по глубине) и по высоте между полками (1.3)
			local k = math.min(0.62, 2.5 / math.max(dsz.Z, 0.1), 1.25 / math.max(dsz.Y, 0.1))
			d:ScaleTo(k)
			local deckTop = if slot < 6 then 2.06 else 0.48
			local col = slot % 6
			standOn(d, -4.0 + col * 1.6, deckTop, 0, CFrame.new())
			d.Parent = prev
			slot += 1
		end
	end
	prev.Parent = rack
	cur.Parent = rack
	rack.WorldPivot = CFrame.new()
	return rack
end

return Util
