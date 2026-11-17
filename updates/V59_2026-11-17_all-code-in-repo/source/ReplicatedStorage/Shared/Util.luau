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

return Util
