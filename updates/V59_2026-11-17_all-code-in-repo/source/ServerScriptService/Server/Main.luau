-- ServerScriptService/Server/Main.server.luau
-- Минимальный сервер v2: хижины и спавн, засады, ретрансляция поз и эффектов, видимые копья.
-- Экономика в демо-режиме живёт на клиенте (Client/DemoServer). Контракт настоящего бэкенда — docs/BACKEND.md.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

-- Remotes есть в .rbxlx; если игра собрана из отдельных .rbxm — создаём недостающие
do
	local folder = RS:FindFirstChild("Remotes") or Instance.new("Folder")
	folder.Name = "Remotes"
	local list: { [string]: boolean } = { Request = true, Ambush = true, State = false, Notify = false, Pose = false, Fx = false, Equip = false }
	for name, isFn in list do
		if not folder:FindFirstChild(name) then
			local r: Instance = if isFn then Instance.new("RemoteFunction") else Instance.new("RemoteEvent")
			r.Name = name
			r.Parent = folder
		end
	end
	folder.Parent = RS
end

local Config = require(RS.Shared.Config)
local Net = require(RS.Shared.Net)
local Plots = require(script.Parent.Plots)
local Cosmetics = require(script.Parent.Cosmetics)
local Relay = require(script.Parent.Relay)
require(script.Parent.Population).start()
-- Robux-магазин и сохранение. Сбой магазина не должен ломать сервер.
do
	local ok, err = pcall(function()
		require(script.Parent.Shop).start()
	end)
	if not ok then
		warn("[Shop] server start failed: " .. tostring(err))
	end
end

-- Внешний вид (копьё, стойка, гантели) — от клиента
Net.ev("Equip").OnServerEvent:Connect(function(player: Player, look: any)
	Cosmetics.apply(player, look)
end)

-- Заглушка удалённого бэкенда: в режиме Remote сюда подключается настоящий сервер (см. docs/BACKEND.md)
Net.fn("Request").OnServerInvoke = function(_player: Player, action: any)
	return false, "Backend is not connected (" .. tostring(action) .. "). Set Config.BACKEND = \"Demo\""
end

local function onCharacter(player: Player, char: Model)
	local hum = char:WaitForChild("Humanoid") :: Humanoid
	hum.WalkSpeed = Config.WALK_SPEED
	hum.Died:Connect(function()
		Relay.onDied(player)
	end)
	task.defer(function()
		Plots.spawn(player)
	end)
	task.delay(0.6, function()
		Cosmetics.refreshTool(player)
	end)
end

local function onPlayer(player: Player)
	Plots.assign(player)
	player.CharacterAdded:Connect(function(char)
		onCharacter(player, char)
	end)
	if player.Character then
		task.spawn(onCharacter, player, player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayer)
for _, p in Players:GetPlayers() do
	task.spawn(onPlayer, p)
end

Players.PlayerRemoving:Connect(function(player)
	local plot = Plots.get(player)
	Relay.onLeave(player)
	Cosmetics.release(player, plot)
	Plots.release(player)
end)
