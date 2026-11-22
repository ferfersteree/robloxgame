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

-- Гантель уровня level (1..7). Гриф вдоль Z модели (X концепта -> Z), PrimaryPart "Grip" в начале координат.
function Util.dumbbell(level: number): Model
	local tier = math.clamp(math.floor(level), 1, #Config.DUMBBELL_LOOK)
	local look = Config.DUMBBELL_LOOK[tier]
	local m = Instance.new("Model")
	m.Name = "Dumbbell"
	m:SetAttribute("Tier", tier)
	local grip = mkPart("Grip", Vector3.new(0.2, 0.2, 0.2), CFrame.new(), Enum.Material.SmoothPlastic, look.color, m)
	grip.Transparency = 1
	grip.CastShadow = false
	for _, spec in look.parts do
		local sides = spec.mirror and { 1, -1 } or { 1 }
		for _, sd in sides do
			local pos = Vector3.new(spec.offset.Z, spec.offset.Y, spec.offset.X * sd)
			local part: Part
			if spec.shape == "Cylinder" then
				part = mkPart(spec.name, spec.size, CFrame.new(pos) * CFrame.Angles(0, math.rad(90), 0), spec.material, spec.color, m)
				part.Shape = Enum.PartType.Cylinder
			else
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

-- Стойка CAMP GYM: начало = середина пола, +Z к игроку. Парные гантели лежат в слотах "Tier1".."Tier7".
local RACK_SLOTS = {
	{ -3.05, 0.84 }, { -0.23, 0.88 }, { 2.85, 0.93 }, { -2.17, 2.55 }, { 1.82, 2.60 }, { -2.37, 4.21 }, { 2.16, 4.26 },
}
function Util.gymRack(): Model
	local rack = Instance.new("Model")
	rack.Name = "GymRack"
	local slate, wood = Enum.Material.Slate, Enum.Material.Wood
	local function blk(name: string, size: Vector3, c: Vector3, mat: Enum.Material, r: number, g: number, b: number, solid: boolean?): Part
		local p = mkPart(name, size, CFrame.new(c), mat, Color3.fromRGB(r, g, b), rack)
		p.CanCollide = solid == true
		return p
	end
	for _, sx in { -1, 1 } do
		for _, sz in { -1, 1 } do
			blk("Footing", Vector3.new(0.48, 0.32, 0.5), Vector3.new(4.72 * sx, 0.16, 1.23 * sz), slate, 84, 98, 101, true)
			blk("Upright", Vector3.new(0.28, 3.34, 0.3), Vector3.new(4.72 * sx, 1.99, 1.23 * sz), wood, 109, 67, 42, true)
		end
	end
	for _, y in { 0.40, 1.98, 3.56 } do
		blk("Deck", Vector3.new(9.72, 0.16, 2.94), Vector3.new(0, y, 0), wood, 181, 122, 71, true)
	end
	for _, y in { 0.23, 1.81, 3.39 } do
		for _, sz in { -1, 1 } do
			blk("Stringer", Vector3.new(9.5, 0.18, 0.2), Vector3.new(0, y, 1.13 * sz), wood, 125, 80, 46)
		end
	end
	for _, sx in { -1, 1 } do
		blk("SignPost", Vector3.new(0.18, 2.4, 0.18), Vector3.new(1.05 * sx, 4.74, -1.62), wood, 125, 80, 46) -- V70: вывеска чуть позади, чтобы мамонтовая гантель её не задевала
	end
	local sign = blk("Sign", Vector3.new(2.6, 0.54, 0.14), Vector3.new(0, 5.66, -1.54), wood, 44, 117, 108) -- V70: выше бивней верхней полки, надпись видна целиком
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
	lbl.TextColor3 = Color3.new(1, 1, 1)
	lbl.TextStrokeColor3 = Color3.fromRGB(20, 25, 32)
	lbl.TextStrokeTransparency = 0
	lbl.Parent = gui
	for i, slot in RACK_SLOTS do
		local tm = Instance.new("Model")
		tm.Name = "Tier" .. i
		tm:SetAttribute("Tier", i)
		for _, sz in { -0.68, 0.68 } do
			local d = Util.dumbbell(i)
			d:PivotTo(CFrame.new(slot[1], slot[2], sz) * CFrame.Angles(0, math.rad(-90), 0)) -- гриф вдоль X стойки
			d.Parent = tm
		end
		tm.Parent = rack
	end
	rack.WorldPivot = CFrame.new()
	return rack
end

return Util
