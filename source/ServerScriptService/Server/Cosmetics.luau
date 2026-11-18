-- ServerScriptService/Server/Cosmetics.luau
-- Видимое другим: копьё в руке (инструмент), стойка купленных копий, гантели.
-- Данные приходят от клиента (в демо экономика на клиенте), сервер только проверяет id и строит модели.
local RS = game:GetService("ReplicatedStorage")

local Config = require(RS.Shared.Config)
local Plots = require(script.Parent.Plots)

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

-- Гантели на стойке
local function refreshGym(plot: Model, level: number)
	local gym = plot:FindFirstChild("Gym")
	local display = gym and gym:FindFirstChild("Display")
	local look = Config.DUMBBELL_LOOK[math.clamp(level, 1, #Config.DUMBBELL_LOOK)]
	if display then
		for _, p in display:GetDescendants() do
			if p:IsA("BasePart") and p:GetAttribute("Weight") then
				p.Color = look.color
				p.Material = look.material
			end
		end
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
	if type(raw.dumbbell) == "number" then
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

return Cosmetics
