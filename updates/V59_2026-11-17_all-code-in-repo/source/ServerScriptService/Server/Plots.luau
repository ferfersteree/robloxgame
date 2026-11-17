-- ServerScriptService/Server/Plots.luau
-- Хижины игроков (5 штук): выдача, спавн во дворе, таблички с именем.
local Plots = {}

local folder = workspace:WaitForChild("Map"):WaitForChild("Plots")
local list: { Model } = {}
for _, m in folder:GetChildren() do
	if m:IsA("Model") then
		table.insert(list, m)
	end
end
table.sort(list, function(a, b)
	return (a:GetAttribute("PlotIndex") or 0) < (b:GetAttribute("PlotIndex") or 0)
end)

local owner: { [Model]: Player } = {}
local byPlayer: { [Player]: Model } = {}

local function setText(holder: Instance?, text: string)
	if not holder then
		return
	end
	local gui = holder:FindFirstChildWhichIsA("SurfaceGui")
	local label = gui and gui:FindFirstChildWhichIsA("TextLabel")
	if label then
		label.Text = text
	end
end

local function setSigns(plot: Model, who: Player?)
	setText(plot:FindFirstChild("Sign"), who and ("Cabin: " .. who.DisplayName) or "Available Cabin")
	setText(plot:FindFirstChild("OwnerSign"), who and string.upper(who.DisplayName) or "AVAILABLE CABIN")
end

for _, plot in list do
	setSigns(plot, nil)
end

function Plots.all(): { Model }
	return list
end

function Plots.assign(player: Player): Model?
	for _, plot in list do
		if not owner[plot] then
			owner[plot] = player
			byPlayer[player] = plot
			plot:SetAttribute("OwnerId", player.UserId)
			plot:SetAttribute("OwnerName", player.DisplayName)
			player:SetAttribute("Plot", plot:GetAttribute("PlotIndex") or 0)
			setSigns(plot, player)
			return plot
		end
	end
	return nil
end

function Plots.release(player: Player)
	local plot = byPlayer[player]
	if not plot then
		return
	end
	byPlayer[player] = nil
	owner[plot] = nil
	plot:SetAttribute("OwnerId", nil)
	plot:SetAttribute("OwnerName", nil)
	setSigns(plot, nil)
end

function Plots.get(player: Player): Model?
	return byPlayer[player]
end

function Plots.spawn(player: Player)
	local plot = byPlayer[player]
	local char = player.Character
	if not plot or not char then
		return
	end
	local sp = (plot:FindFirstChild("YardSpawn") or plot:FindFirstChild("Spawn")) :: BasePart?
	if sp then
		char:PivotTo(sp.CFrame + Vector3.new(0, 3.2, 0))
	end
end

return Plots
