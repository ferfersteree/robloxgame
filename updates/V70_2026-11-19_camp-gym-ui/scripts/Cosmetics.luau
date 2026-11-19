-- ServerScriptService/Server/Cosmetics.luau
-- Видимое другим: копьё в руке (инструмент), стойка купленных копий, гантели.
-- Данные приходят от клиента (в демо экономика на клиенте), сервер только проверяет id и строит модели.
local RS = game:GetService("ReplicatedStorage")

local Config = require(RS.Shared.Config)
local Plots = require(script.Parent.Plots)
local Util = require(RS.Shared.Util)

local Cosmetics = {}

export type Look = { spear: string, owned: { string }, dumbbell: number }
local looks: { [Player]: Look } = {}

local function spearTemplate(id: string): Model?
	local f = RS.Assets:FindFirstChild("Spears")
	-- V25: у копий 41-46 пока нет своей модели, берём Пик сингулярности
	local m = f and (f:FindFirstChild(id) or f:FindFirstChild("singularity_spire"))
	return (m and m:IsA("Model")) and m or nil
end

local function anchoredClone(tpl: Model): Model
	local m = tpl:Clone()
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
		end
	end
	return m
end

-- Копьё в инструменте: невидимая ручка + приваренная модель
function Cosmetics.refreshTool(player: Player)
	local look = looks[player]
	local id = look and look.spear or "stick"
	local tool: Tool? = nil
	local kids: { Instance } = player.Character and player.Character:GetChildren() or {}
	for _, c in kids do
		if c:IsA("Tool") and c:GetAttribute("Spear") then
			tool = c
		end
	end
	if not tool then
		local bp = player:FindFirstChildOfClass("Backpack")
		for _, c in (bp and bp:GetChildren() or {}) do
			if c:IsA("Tool") and c:GetAttribute("Spear") then
				tool = c
			end
		end
	end
	if player.Character then
		player.Character:SetAttribute("SpearId", id)
	end
	if not tool then
		return
	end
	local handle = tool:FindFirstChild("Handle") :: BasePart?
	if not handle then
		return
	end
	if tool:GetAttribute("Visual") == id and tool:FindFirstChild("Visual") then
		return
	end
	local old = tool:FindFirstChild("Visual")
	if old then
		old:Destroy()
	end
	local tpl = spearTemplate(id)
	if not tpl then
		return
	end
	local m = tpl:Clone()
	m.Name = "Visual"
	m:PivotTo(handle.CFrame)
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = false
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.Massless = true
			local w = Instance.new("WeldConstraint")
			w.Part0 = handle
			w.Part1 = d
			w.Parent = d
		end
	end
	m.Parent = tool
	tool:SetAttribute("Visual", id)
	tool:SetAttribute("SpearId", id)
	tool.ToolTip = (Config.SPEAR_BY_ID[id] or Config.SPEARS[1]).name
end

-- Стойка копий во дворе
local function refreshRack(plot: Model, owned: { string })
	local slots = plot:FindFirstChild("SpearSlots")
	if not slots then
		return
	end
	local shown = plot:FindFirstChild("RackSpears")
	if shown then
		shown:Destroy()
	end
	local f = Instance.new("Folder")
	f.Name = "RackSpears"
	local capacity=math.min(4,#slots:GetChildren())
	local first=math.max(1,#owned-capacity+1)
	for index, id in owned do
		local i=index-first+1
		local slot = slots:FindFirstChild("Slot" .. i) :: BasePart?
		local tpl = spearTemplate(id)
		if slot and tpl then
			local m = anchoredClone(tpl)
			local len = (m:GetAttribute("Length") :: number?) or 7
			m:PivotTo(CFrame.new(slot.Position + Vector3.new(0, len / 2 - 3.6, 0)) * CFrame.Angles(0, math.rad(90), math.rad(6)))
			m.Parent = f
		end
	end
	f.Parent = plot
end

-- Гантели на стойке (V70: новая стойка CAMP GYM вместо старой модели)
local LOCK_COLOR = Color3.fromRGB(38, 42, 50)

-- закрытый уровень: полупрозрачный «призрак» своего цвета (видно, что впереди); открытый: родной цвет и материал из атрибутов
local function setLocked(model: Instance, locked: boolean)
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") and p.Name ~= "Grip" then
			local c = p:GetAttribute("OrigColor")
			local mn = p:GetAttribute("OrigMaterial")
			if locked then
				p.Color = if typeof(c) == "Color3" then c:Lerp(LOCK_COLOR, 0.35) else LOCK_COLOR
				p.Material = Enum.Material.SmoothPlastic
				p.Transparency = 0.55
			elseif typeof(c) == "Color3" and type(mn) == "string" then
				p.Color = c
				p.Material = (Enum.Material :: any)[mn]
				p.Transparency = 0
			end
		end
	end
end

local function setGlow(model: Instance, on: boolean, color: Color3)
	for _, d in model:GetChildren() do
		local grip = d:FindFirstChild("Grip")
		if grip then
			local l = grip:FindFirstChild("TierGlow") :: PointLight?
			if on then
				if not l then
					l = Instance.new("PointLight")
					l.Name = "TierGlow"
					l.Brightness = 1
					l.Range = 6
					l.Parent = grip
				end
				if l then
					l.Color = color
				end
			elseif l then
				l:Destroy()
			end
		end
	end
end

local function bboxExtent(cf: CFrame, size: Vector3, dir: Vector3): number
	return math.abs(dir:Dot(cf.RightVector)) * size.X + math.abs(dir:Dot(cf.UpVector)) * size.Y + math.abs(dir:Dot(cf.LookVector)) * size.Z
end

-- один раз на двор: заменить старую стойку на новую
local function buildGym(gym: Instance)
	if gym:GetAttribute("V70Rack") then
		return
	end
	local old = gym:FindFirstChild("Display")
	local stand = gym:FindFirstChild("Stand") :: BasePart?
	if not (old and old:IsA("Model") and stand) then
		return
	end
	local cf, size = old:GetBoundingBox()
	local base = Vector3.new(cf.Position.X, cf.Position.Y - size.Y / 2, cf.Position.Z)
	local dir = Util.flat(stand.Position - base)
	if dir.Magnitude < 0.01 then
		dir = Util.flat(-cf.LookVector)
	end
	dir = dir.Unit
	base += dir * 0.5 -- чуть ближе к площадке: задом стойка не заходит в грядку за ней
	local perp = Vector3.new(-dir.Z, 0, dir.X)
	local s = math.clamp(bboxExtent(cf, size, perp) * 1.6 / 9.92, 0.6, 1.0)
	local rack = Util.gymRack()
	gym:SetAttribute("RackScale", s)
	rack:ScaleTo(s)
	rack:PivotTo(CFrame.lookAt(base, base - dir)) -- +Z смотрит на площадку игрока
	old:Destroy()
	rack.Name = "Display"
	rack.Parent = gym
	-- декоративная гантель на земле: запоминаем её место до замены
	local nat = gym:FindFirstChild("NativeDumbbell")
	if nat and nat:IsA("Model") then
		local ncf, nsize = nat:GetBoundingBox()
		gym:SetAttribute("NativePos", Vector3.new(ncf.Position.X, base.Y, ncf.Position.Z))
		local axis = nsize.X > nsize.Z and ncf.RightVector or ncf.LookVector -- длинная горизонтальная ось
		gym:SetAttribute("NativeAxis", Util.flat(axis).Unit)
		nat:Destroy()
	end
	gym:SetAttribute("V70Rack", true)
	gym:SetAttribute("ShownLevel", nil)
end

local function refreshNative(gym: Instance, level: number)
	local pos = gym:GetAttribute("NativePos")
	if typeof(pos) ~= "Vector3" then
		return
	end
	local cur = gym:FindFirstChild("NativeDumbbell")
	if cur and cur:GetAttribute("Tier") == level then
		return
	end
	if cur then
		cur:Destroy()
	end
	local m = Util.dumbbell(level)
	m:ScaleTo((gym:GetAttribute("RackScale") :: number?) or 1) -- в масштабе стойки, чтобы не лезть в неё
	local bcf, bsize = m:GetBoundingBox()
	local lift = -(bcf.Position.Y - bsize.Y / 2) -- низ на землю
	local axis = gym:GetAttribute("NativeAxis")
	local at = Vector3.new(pos.X, pos.Y + lift, pos.Z)
	m:PivotTo(typeof(axis) == "Vector3" and CFrame.lookAt(at, at + axis) or CFrame.new(at))
	m.Name = "NativeDumbbell"
	m.Parent = gym
end

local function refreshGym(plot: Model, level: number)
	local gym = plot:FindFirstChild("Gym")
	if not gym then
		return
	end
	if level ~= level then
		level = 1 -- NaN
	end
	level = math.clamp(math.floor(level), 1, #Config.DUMBBELL_LOOK)
	buildGym(gym)
	if gym:GetAttribute("ShownLevel") == level then
		return
	end
	local display = gym:FindFirstChild("Display")
	if display and gym:GetAttribute("V70Rack") then
		for i = 1, #Config.DUMBBELL_LOOK do
			local tm = display:FindFirstChild("Tier" .. i)
			if tm then
				setLocked(tm, i > level)
				setGlow(tm, i == level, Config.DUMBBELL_LOOK[i].color)
			end
		end
		refreshNative(gym, level)
		gym:SetAttribute("ShownLevel", level)
	end
end

-- Проверка и применение внешнего вида от клиента
function Cosmetics.apply(player: Player, raw: any)
	if type(raw) ~= "table" then
		return
	end
	local look: Look = looks[player] or { spear = "stick", owned = { "stick" }, dumbbell = 1 }
	if type(raw.spear) == "string" and Config.SPEAR_BY_ID[raw.spear] then
		look.spear = raw.spear
	end
	if type(raw.owned) == "table" then
		local owned = {}
		for _, s in Config.SPEARS do
			if table.find(raw.owned, s.id) then
				table.insert(owned, s.id)
			end
		end
		look.owned = owned
	end
	if type(raw.dumbbell) == "number" and raw.dumbbell == raw.dumbbell then
		look.dumbbell = math.clamp(math.floor(raw.dumbbell), 1, #Config.DUMBBELL)
	end
	looks[player] = look
	Cosmetics.refreshTool(player)
	local plot = Plots.get(player)
	if plot then
		refreshRack(plot, look.owned)
		refreshGym(plot, look.dumbbell)
	end
end

function Cosmetics.dumbbellLevel(player: Player): number
	local l = looks[player]
	return l and l.dumbbell or 1
end

function Cosmetics.release(player: Player, plot: Model?)
	looks[player] = nil
	if plot then
		refreshRack(plot, {})
		refreshGym(plot, 1)
	end
end

-- V70: заменить стойки во всех дворах при загрузке модуля
for _, plot in Plots.all() do
	local ok, err = pcall(refreshGym, plot, 1)
	if not ok then
		warn("[Cosmetics] gym rack: " .. tostring(err))
	end
end

return Cosmetics
