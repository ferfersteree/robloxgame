-- StarterPlayerScripts/Client/Main.client.luau
-- Точка входа клиента: подключает модули, маршрутизирует подсказки (ProximityPrompt) по ActionText,
-- показывает события бэкенда, применяет настройки, отправляет серверу внешний вид (копьё, стойка,
-- гантели) и выключает подсказки, пока игрок занят (засада, мини-игры, раскрытие).
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")

local Config = require(RS.Shared.Config)
local Net = require(RS.Shared.Net)
local Num = require(RS.Shared.Num)

local Client = script.Parent
local UI = require(Client.UIKit)
local Theme = require(Client.Theme)
local Sfx = require(Client.Sfx)
local Fx = require(Client.WorldFx)
local Backend = require(Client.Backend)
local Hud = require(Client.Hud)
local Prompts = require(Client.Prompts)
local Menus = require(Client.Menus)
local Dialog = require(Client.Dialog)
local HuntCtl = require(Client.HuntCtl)
local Reveal = require(Client.Reveal)
local SpearFx = require(Client.SpearFx)
local _ZoneFx = require(Client.ZoneFx)
local Ambient = require(Client.Ambient)
local Activities = require(Client.Activities)
local Showroom = require(Client.Showroom)
local WrapCtl = require(Client.WrapCtl)
local TrainCtl = require(Client.TrainCtl)
local Guide = require(Client.Guide)

local player = Players.LocalPlayer
local map = workspace:WaitForChild("Map")
-- Keep this edition's UI in English, including dynamically created panels.
local function keepEnglish(item: Instance)
	if item:IsA("GuiBase2d") or item:IsA("ProximityPrompt") then
		(item :: any).AutoLocalize = false
	end
end
local playerGui = player:WaitForChild("PlayerGui")
for _, item in playerGui:GetDescendants() do keepEnglish(item) end
for _, item in map:GetDescendants() do keepEnglish(item) end
playerGui.DescendantAdded:Connect(keepEnglish)
map.DescendantAdded:Connect(keepEnglish)
local C = Theme.C
local FxEv = Net.ev("Fx")
local EquipEv = Net.ev("Equip")

---------------------------------------------------------------------
-- Поиск владельцев подсказок
---------------------------------------------------------------------
local function ancestorWith(inst: Instance, attr: string): (any, Instance?)
	local p: Instance? = inst
	while p and p ~= map do
		local v = p:GetAttribute(attr)
		if v ~= nil then
			return v, p
		end
		p = p.Parent
	end
	return nil, nil
end

-- Своя хижина: подсказки «Упаковать» и «Тренироваться» работают только у владельца
local function ownPlot(prompt: ProximityPrompt): Instance?
	local _, plot = ancestorWith(prompt, "PlotIndex")
	if not plot then
		return nil
	end
	if plot:GetAttribute("OwnerId") ~= player.UserId then
		Sfx.play("error")
		local who = plot:GetAttribute("OwnerName")
		UI.toast(who and ("This cabin belongs to " .. tostring(who) .. ". Your cabin has your name on it") or "This cabin is vacant. Your cabin has your name on it", "warn")
		return nil
	end
	return plot
end

---------------------------------------------------------------------
-- Подсказки → действия
---------------------------------------------------------------------
Prompts.init(map)

Prompts.on("hide", function(pr)
	local m = pr.Parent and pr.Parent.Parent
	if m and m:IsA("Model") then
		HuntCtl.enter(m)
	end
end)
Prompts.on("wrap", function(pr)
	local plot = ownPlot(pr)
	if plot then
		WrapCtl.open(plot)
	end
end)
Prompts.on("train", function(pr)
	local plot = ownPlot(pr)
	if plot then
		TrainCtl.open(plot)
	end
end)
Prompts.on("sell", function()
	Menus.market()
end)
Prompts.on("upgrade", function()
	Menus.forge()
end)
Prompts.on("armory", function()
	Menus.spears()
end)
Prompts.on("quests", function()
	Menus.quests()
end)
Prompts.on("talk", function(pr)
	local id, model = ancestorWith(pr, "NPC")
	if type(id) == "string" then
		Dialog.open(id, model)
	end
end)
Prompts.on("lookout", function(pr)
	local _, model = ancestorWith(pr, "Activity")
	if model then
		Activities.lookout(model)
	end
end)
Prompts.on("range", function()
	Activities.range()
end)
Prompts.on("course", function()
	Activities.course()
end)
Prompts.on("reveal", function(pr)
	Showroom.reveal(pr)
end)
Prompts.on("inspect", function(pr)
	Showroom.inspect(pr)
end)
Prompts.on("demo", function()
	Showroom.chooser(nil)
end)

-- Пока игрок занят — подсказки скрыты
task.spawn(function()
	local last: boolean? = nil
	while true do
		local free = Hud.mode == "normal" and HuntCtl.state == "idle" and Activities.busy == nil and not Reveal.active
		if free ~= last then
			last = free
			Prompts.setEnabled(free)
		end
		task.wait(0.15)
	end
end)

---------------------------------------------------------------------
-- Настройки и внешний вид для сервера
---------------------------------------------------------------------
local lastLook = ""
local function sendLook(d: any)
	local owned = {}
	for id in d.spears do
		table.insert(owned, id)
	end
	table.sort(owned)
	local look = { spear = d.spear, owned = owned, dumbbell = d.dumbbell }
	local ok, key = pcall(HttpService.JSONEncode, HttpService, look)
	if not ok or key ~= lastLook then
		lastLook = ok and key or ""
		EquipEv:FireServer(look)
	end
end

local function applySettings(s: any)
	if type(s) ~= "table" then
		return
	end
	Sfx.enabled = s.sfx ~= false
	Sfx.setMusic(s.music ~= false)
	Fx.lowFx = s.lowFx == true
end

Backend.onChange(function(d)
	if not d then
		return
	end
	applySettings(d.settings)
	sendLook(d)
end)

---------------------------------------------------------------------
-- События бэкенда
---------------------------------------------------------------------
Backend.onEvent(function(name: string, p: any)
	p = type(p) == "table" and p or {}
	if name == "levelup" then
		Sfx.play("level")
		UI.confetti(70, { C.xp, C.gold, C.green })
		Hud.banner("LEVEL " .. tostring(p.level) .. "!", C.xp, p.reward and ("+" .. Num.short(p.reward) .. " 💰") or nil, 2.4)
		if p.reward and p.reward > 0 then
			Hud.flyCoins(Vector2.new(workspace.CurrentCamera.ViewportSize.X / 2, workspace.CurrentCamera.ViewportSize.Y * 0.4), p.reward)
		end
		local c = player.Character
		local root = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
		if root then
			Fx.burst(root.Position + Vector3.new(0, 2, 0), { tex = "star", color = C.xp, color2 = C.gold, n = 24, speed = NumberRange.new(6, 14), size = 0.7, life = 1, rot = true })
			FxEv:FireServer({ k = "levelup", pos = root.Position, m = tonumber(p.level) })
		end
	elseif name == "quest" then
		local q = Config.QUEST_BY_ID[p.id]
		Sfx.play("ping", 1.2, 0.6)
		UI.toast("Quest complete: \"" .. (q and q.title or tostring(p.id)) .. "\" - claim your reward in Quests", "quest", 4)
	elseif name == "boost" then
		local b = Config.BOOSTS[p.id]
		Sfx.play("sparkle")
		UI.toast((b and (b.icon .. " " .. b.name) or tostring(p.id)) .. " · " .. Num.time(tonumber(p.dur) or 0), "rare", 3)
	elseif name == "notify" then
		UI.toast(tostring(p.text or ""), p.kind or "info")
	end
end)

-- Чужой новый уровень — звёзды над игроком
FxEv.OnClientEvent:Connect(function(pl: any)
	if type(pl) == "table" and pl.k == "levelup" and typeof(pl.pos) == "Vector3" then
		Fx.burst(pl.pos + Vector3.new(0, 2, 0), { tex = "star", color = C.xp, n = 18, speed = NumberRange.new(5, 12), size = 0.6, life = 0.9, rot = true })
		Fx.text(pl.pos + Vector3.new(0, 5, 0), "⭐ LEVEL " .. tostring(pl.m or ""), C.xp, 30, 1.6)
	end
end)

-- Копьё упало — звери вокруг разбегаются
SpearFx.Landed.Event:Connect(function(pos: Vector3)
	Ambient.scare(pos, 28)
end)

---------------------------------------------------------------------
-- Запуск
---------------------------------------------------------------------
Ambient.init()
Activities.init()
Showroom.init()
require(script.Parent.NativeVendors).init()
Guide.init()
-- Robux-магазин, загрузка и сохранение прогресса. Сбой магазина не должен ломать игру.
do
	local ok, err = pcall(function()
		require(Client.Shop).init()
	end)
	if not ok then
		warn("[Shop] client init failed: " .. tostring(err))
	end
end
Backend.sync()
Sfx.startMusic()
do
	local ok, err = pcall(function()
		require(Client.Footsteps).init()
	end)
	if not ok then
		warn("[Footsteps] init failed: " .. tostring(err))
	end
end

task.delay(1, function()
	Hud.banner(string.upper(Config.GAME_NAME), C.gold, (Backend.mode == "Demo" and game:GetService("RunService"):IsStudio()) and "Demo mode - test panel in the menu" or nil, 2.6)
	Sfx.play("open")
end)

