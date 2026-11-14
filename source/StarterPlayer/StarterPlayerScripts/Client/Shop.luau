-- StarterPlayerScripts/Client/Shop.luau
-- Окно Robux-магазина: красная шапка с гирляндой, стартовый набор, пассы, бусты, паки монет.
-- Иконки — настоящие 3D-предметы во вьюпортах (копья и звери из игры, остальное собрано из деталей).
-- Покупка: MarketplaceService → сервер (Server/Shop) выдаёт → сюда приходит "granted".
-- Здесь же загрузка/сохранение прогресса и применение купленных монет и стартового набора.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local MarketplaceService = game:GetService("MarketplaceService")
local TextChatService = game:GetService("TextChatService")

local Config = require(RS.Shared.Config)
local Net = require(RS.Shared.Net)
local Num = require(RS.Shared.Num)
local UI = require(script.Parent.UIKit)
local Sfx = require(script.Parent.Sfx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Perks = require(script.Parent.Perks)
local Card = require(script.Parent.Card)

local Shop = {}
local SHOP = Config.SHOP
local player = Players.LocalPlayer
local ROBUX = utf8.char(0xE002)

local function rgb(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end

local RunService = game:GetService("RunService")
local Theme = require(script.Parent.Theme)

-- Палитра окна: «небо» — голубой градиент, облака, циановая шапка-баннер.
-- Ключи winLine/winGlow/deepRed/cream/... нужны экрану «получено» (unlock).
local K = {
	skyTop = rgb(104, 196, 255), skyMid = rgb(190, 234, 255), skyBot = rgb(104, 188, 78), -- луг Forest Edge: небо над зелёными холмами
	hill1 = rgb(132, 210, 92), hill2 = rgb(100, 186, 76), hill3 = rgb(78, 160, 62), trunk = rgb(122, 78, 40), leaf = rgb(58, 142, 70),
	frame = rgb(12, 36, 104), frameGlow = rgb(176, 232, 255),
	headTop = rgb(96, 228, 255), headBot = rgb(24, 132, 236), headPat = rgb(205, 246, 255),
	cloud = rgb(255, 255, 255), cloudEdge = rgb(150, 208, 250),
	barDark = rgb(10, 34, 88), gold = rgb(250, 186, 26), goldText = rgb(255, 216, 74),
	white = rgb(255, 255, 255), title = rgb(255, 255, 255), titleLine = rgb(10, 36, 104), navy = rgb(8, 24, 72),
	heroTop = rgb(158, 78, 240), heroMid = rgb(114, 42, 204), heroBot = rgb(62, 20, 142), heroLine = rgb(32, 10, 82),
	green = rgb(84, 214, 52), red = rgb(232, 50, 56),
	winLine = rgb(12, 36, 104), winGlow = rgb(176, 232, 255),
	cream = rgb(255, 255, 255), creamLine = rgb(10, 36, 104), deepRed = rgb(92, 13, 13),
	tile = rgb(10, 20, 70), cardLine = rgb(26, 16, 64), cardBot = rgb(59, 29, 122),
}
local ACCENT = {
	charm = rgb(120, 255, 150), insight = rgb(130, 200, 255), broker = rgb(210, 220, 235), smith = rgb(255, 150, 80),
	wrap = rgb(255, 126, 190), vip = rgb(255, 216, 74),
	fortune20 = rgb(255, 216, 74), jackpot20 = rgb(255, 120, 170), fair30 = rgb(100, 232, 214), server15 = rgb(110, 190, 255),
	founder = rgb(196, 130, 255), hour_bundle = rgb(255, 216, 74),
}
-- Основной цвет плитки товара (как зелёный x2 Cash, оранжевый VIP, синий Egg Growth в референсе)
local TILE = {
	charm = rgb(92, 214, 56), insight = rgb(70, 130, 240), broker = rgb(120, 140, 170), smith = rgb(236, 110, 40),
	wrap = rgb(236, 82, 170), vip = rgb(255, 170, 20),
	fortune20 = rgb(255, 172, 20), jackpot20 = rgb(226, 56, 120), fair30 = rgb(24, 188, 196), server15 = rgb(52, 196, 96),
	founder = rgb(132, 62, 214), hour_bundle = rgb(226, 120, 20),
	coins1 = rgb(132, 214, 36), coins2 = rgb(132, 214, 36), coins3 = rgb(40, 190, 140), coins4 = rgb(80, 130, 255),
}

-- Подписи под товаром читаются за секунду: крупно выгода, мелко срок или условие.
local PITCH: { [string]: { string } } = {
	charm = { "RARE CHANCE +50%", "forever" },
	insight = { "6H FORECAST", "see prices before they move" },
	broker = { "SELL FREELY", "prices drop far less" },
	smith = { "FORGE +2 LEVELS", "and 25% cheaper" },
	wrap = { "WRAP ALL", "one bow, whole bag" },
	vip = { "SELL ANYWHERE", "+15% XP · gold tag" },
	fortune20 = { "MORE MUTATIONS", "20 min · gold & rainbow" },
	jackpot20 = { "RARE CHANCE +100%", "20 min" },
	fair30 = { "NO PRICE DROPS", "30 min · always good demand" },
	server15 = { "LUCK ×2 FOR EVERYONE", "15 min · whole server" },
	founder = { "FOUNDER TAG + AURA", "limited · bigger daily gift" },
	hour_bundle = { "3 BOOSTS, SAVE 40%", "30 min · mutations, rare, fair" },
}

-- Мультяшные иллюстрации магазина (папка shop-art/ в репозитории). Номера берутся из Client/AudioIds (art_<имя>).
-- Пока пусто — вместо картинки показывается 3D-модель.
-- Ключи: id товара, "spear" (Starter Pack), "flyspear", "animal_<id>_R" (идёт вправо), "animal_<id>_F" (анфас).
local ART: { [string]: string } = {}
do
	-- номера картинок лежат в Client/AudioIds под ключами art_<имя> (их пишет tools/upload_to_roblox.py)
	local mod = script.Parent:FindFirstChild("AudioIds")
	if mod and mod:IsA("ModuleScript") then
		local ok, ids = pcall(require, mod)
		if ok and type(ids) == "table" then
			for k, v in ids do
				if type(k) == "string" and k:sub(1, 4) == "art_" and type(v) == "string" and v ~= "" and v ~= "rbxassetid://0" then
					ART[k:sub(5)] = v
				end
			end
		end
	end
end
local function artImage(parent: Instance, key: string): ImageLabel?
	local id = ART[key]
	if not id or id == "" then
		return nil
	end
	local img = Instance.new("ImageLabel")
	img.BackgroundTransparency = 1
	img.Image = id
	img.ScaleType = Enum.ScaleType.Fit
	img.Size = UDim2.fromScale(1, 1)
	img.ZIndex = 2
	img.Parent = parent
	return img
end

---------------------------------------------------------------------
-- 3D-иконки
---------------------------------------------------------------------
local BLOCK, BALL, CYL = Enum.PartType.Block, Enum.PartType.Ball, Enum.PartType.Cylinder
local GOLD, GOLD2 = rgb(255, 200, 50), rgb(236, 160, 24)

local function part(model: Model, shape: Enum.PartType, size: Vector3, cf: CFrame, color: Color3, material: Enum.Material?): Part
	local p = Instance.new("Part")
	p.Shape = shape
	p.Size = size
	p.CFrame = cf
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = model
	return p
end

-- Цилиндр, стоящий вертикально (ось детали Cylinder — X)
local function disc(model: Model, diameter: number, height: number, pos: Vector3, color: Color3, material: Enum.Material?): Part
	return part(model, CYL, Vector3.new(height, diameter, diameter), CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90)), color, material)
end

local function coinStack(model: Model, n: number, x: number, z: number)
	for i = 1, n do
		disc(model, 1, 0.17, Vector3.new(x + ((i % 2 == 0) and 0.04 or -0.03), (i - 0.5) * 0.19, z), (i % 2 == 0) and GOLD or GOLD2, Enum.Material.Metal)
	end
end

local function flask(model: Model, color: Color3, pos: Vector3, scale: number)
	part(model, BALL, Vector3.one * 1.3 * scale, CFrame.new(pos + Vector3.new(0, 0.65 * scale, 0)), color, Enum.Material.Neon)
	part(model, BALL, Vector3.one * 0.3 * scale, CFrame.new(pos + Vector3.new(-0.3 * scale, 0.95 * scale, -0.42 * scale)), rgb(255, 255, 255), Enum.Material.Neon)
	disc(model, 0.46 * scale, 0.55 * scale, pos + Vector3.new(0, 1.45 * scale, 0), rgb(214, 236, 244), Enum.Material.Glass)
	disc(model, 0.62 * scale, 0.14 * scale, pos + Vector3.new(0, 1.74 * scale, 0), rgb(214, 236, 244), Enum.Material.Glass)
	disc(model, 0.4 * scale, 0.3 * scale, pos + Vector3.new(0, 1.92 * scale, 0), rgb(150, 98, 56))
end

local function chest(model: Model)
	local wood, dark = rgb(150, 92, 48), rgb(104, 60, 30)
	part(model, BLOCK, Vector3.new(2.4, 1.1, 1.5), CFrame.new(0, 0.55, 0), wood, Enum.Material.Wood)
	part(model, BLOCK, Vector3.new(2.5, 0.22, 1.6), CFrame.new(0, 1.12, 0), dark, Enum.Material.Wood)
	part(model, BLOCK, Vector3.new(2.4, 0.2, 1.5), CFrame.new(0, 1.9, 0.72) * CFrame.Angles(math.rad(-62), 0, 0), dark, Enum.Material.Wood)
	for _, x in { -0.85, 0.85 } do
		part(model, BLOCK, Vector3.new(0.2, 1.14, 1.54), CFrame.new(x, 0.55, 0), GOLD2, Enum.Material.Metal)
	end
	part(model, BLOCK, Vector3.new(0.34, 0.4, 0.12), CFrame.new(0, 0.82, -0.78), GOLD, Enum.Material.Metal)
	for i = 1, 9 do
		local a = i * 2.4
		disc(model, 0.62, 0.14, Vector3.new(math.cos(a) * 0.75, 1.3 + (i % 3) * 0.12, math.sin(a) * 0.4), (i % 2 == 0) and GOLD or GOLD2, Enum.Material.Metal)
	end
end

local function buildIcon(kind: string): Model
	local m = Instance.new("Model")
	if kind == "coins1" then
		coinStack(m, 4, 0, 0)
		disc(m, 1, 0.17, Vector3.new(1.05, 0.09, -0.2), GOLD, Enum.Material.Metal)
		part(m, CYL, Vector3.new(0.17, 1, 1), CFrame.new(-0.95, 0.5, 0.3) * CFrame.Angles(0, math.rad(70), 0), GOLD2, Enum.Material.Metal)
	elseif kind == "coins2" then
		coinStack(m, 5, -0.6, 0.3)
		coinStack(m, 8, 0.55, 0.35)
		coinStack(m, 3, 0, -0.75)
	elseif kind == "coins3" then
		chest(m)
	elseif kind == "coins4" then
		chest(m)
		coinStack(m, 7, -1.9, -0.5)
		coinStack(m, 4, 1.9, -0.6)
		coinStack(m, 5, -1.2, -1.3)
		coinStack(m, 3, 1.1, -1.4)
	elseif kind == "purse" then
		local leather = rgb(170, 96, 44)
		part(m, BALL, Vector3.new(1.9, 1.7, 1.7), CFrame.new(0, 0.85, 0), leather)
		disc(m, 0.75, 0.5, Vector3.new(0, 1.75, 0), leather)
		disc(m, 0.95, 0.14, Vector3.new(0, 1.62, 0), GOLD, Enum.Material.Metal)
		disc(m, 0.9, 0.16, Vector3.new(0, 2.05, 0), GOLD2, Enum.Material.Metal)
		part(m, CYL, Vector3.new(0.14, 0.8, 0.8), CFrame.new(0, 0.85, -0.86) * CFrame.Angles(0, math.rad(90), 0), GOLD, Enum.Material.Metal)
		coinStack(m, 3, 1.35, -0.3)
	elseif kind == "wrap" then
		local paper, rope = rgb(214, 164, 104), rgb(224, 44, 50)
		part(m, BLOCK, Vector3.new(1.7, 1.4, 1.7), CFrame.new(0, 0.7, 0), paper)
		part(m, BLOCK, Vector3.new(1.76, 1.46, 0.22), CFrame.new(0, 0.7, 0), rope)
		part(m, BLOCK, Vector3.new(0.22, 1.46, 1.76), CFrame.new(0, 0.7, 0), rope)
		part(m, BALL, Vector3.new(0.7, 0.42, 0.42), CFrame.new(-0.36, 1.58, 0) * CFrame.Angles(0, 0, math.rad(-22)), rope)
		part(m, BALL, Vector3.new(0.7, 0.42, 0.42), CFrame.new(0.36, 1.58, 0) * CFrame.Angles(0, 0, math.rad(22)), rope)
		part(m, BALL, Vector3.one * 0.34, CFrame.new(0, 1.5, 0), GOLD)
	elseif kind == "bag" then
		local canvas, leather = rgb(96, 140, 78), rgb(132, 78, 38)
		part(m, BLOCK, Vector3.new(1.6, 1.8, 0.95), CFrame.new(0, 0.9, 0), canvas, Enum.Material.Fabric)
		part(m, BALL, Vector3.new(1.6, 0.8, 0.95), CFrame.new(0, 1.8, 0), canvas, Enum.Material.Fabric)
		part(m, BLOCK, Vector3.new(1.66, 0.75, 0.2), CFrame.new(0, 1.62, -0.44), leather)
		part(m, BLOCK, Vector3.new(1.05, 0.7, 0.26), CFrame.new(0, 0.55, -0.56), leather)
		part(m, BLOCK, Vector3.new(0.24, 0.24, 0.1), CFrame.new(0, 1.3, -0.56), GOLD, Enum.Material.Metal)
		part(m, BLOCK, Vector3.new(0.24, 0.2, 0.1), CFrame.new(0, 0.82, -0.7), GOLD, Enum.Material.Metal)
		for _, x in { -0.55, 0.55 } do
			part(m, BLOCK, Vector3.new(0.22, 1.7, 0.14), CFrame.new(x, 0.95, 0.52), leather)
		end
		disc(m, 1.5, 0.26, Vector3.new(0, 2.28, 0.05), rgb(214, 164, 104), Enum.Material.Fabric)
	elseif kind == "titan" then
		local look = Config.DUMBBELL_LOOK[#Config.DUMBBELL_LOOK]
		local plate = look and look.color or rgb(240, 232, 214)
		part(m, CYL, Vector3.new(2.6, 0.26, 0.26), CFrame.new(0, 0.8, 0), rgb(96, 100, 112), Enum.Material.Metal)
		for _, s in { -1, 1 } do
			part(m, CYL, Vector3.new(0.5, 1.6, 1.6), CFrame.new(s * 1.2, 0.8, 0), plate)
			part(m, CYL, Vector3.new(0.3, 1.15, 1.15), CFrame.new(s * 0.82, 0.8, 0), GOLD, Enum.Material.Metal)
			part(m, CYL, Vector3.new(0.14, 0.5, 0.5), CFrame.new(s * 1.5, 0.8, 0), rgb(96, 100, 112), Enum.Material.Metal)
		end
	elseif kind == "vip" then
		disc(m, 1.9, 0.5, Vector3.new(0, 0.25, 0), GOLD, Enum.Material.Metal)
		disc(m, 1.98, 0.14, Vector3.new(0, 0.06, 0), GOLD2, Enum.Material.Metal)
		for i = 1, 6 do
			local a = (i - 1) * math.pi / 3
			local x, z = math.cos(a) * 0.82, math.sin(a) * 0.82
			local tall = (i % 2 == 1) and 0.95 or 0.6
			part(m, BLOCK, Vector3.new(0.3, tall, 0.3), CFrame.new(x, 0.5 + tall / 2, z) * CFrame.Angles(0, -a, 0), GOLD, Enum.Material.Metal)
			part(m, BALL, Vector3.one * 0.36, CFrame.new(x, 0.56 + tall, z), (i % 2 == 1) and rgb(232, 50, 56) or rgb(78, 181, 255), Enum.Material.Neon)
		end
		part(m, BALL, Vector3.one * 0.34, CFrame.new(0, 0.26, -0.95), rgb(120, 255, 150), Enum.Material.Neon)
	elseif kind == "founder" then
		disc(m, 1.9, 0.4, Vector3.new(0, 0.2, 0), GOLD, Enum.Material.Metal)
		for i = 1, 5 do
			local a = (i - 1) * math.pi * 2 / 5
			local x, z = math.cos(a) * 0.75, math.sin(a) * 0.75
			part(m, BLOCK, Vector3.new(0.3, 1.2, 0.3), CFrame.new(x, 0.9, z) * CFrame.Angles(0, -a, 0), GOLD, Enum.Material.Metal)
			part(m, BALL, Vector3.one * 0.38, CFrame.new(x, 1.6, z), rgb(196, 130, 255), Enum.Material.Neon)
		end
		part(m, BALL, Vector3.one * 0.6, CFrame.new(0, 0.7, 0), rgb(120, 224, 255), Enum.Material.Neon)
	elseif kind == "hour_bundle" then
		flask(m, rgb(255, 200, 50), Vector3.new(-1.05, 0, 0.2), 0.85)
		flask(m, rgb(255, 90, 140), Vector3.new(0, 0, -0.35), 1)
		flask(m, rgb(90, 220, 200), Vector3.new(1.05, 0, 0.2), 0.85)
	elseif kind == "insight" then
		disc(m, 1.7, 0.3, Vector3.new(0, 0.15, 0), rgb(96, 70, 40), Enum.Material.Wood)
		local ball = part(m, BALL, Vector3.one * 1.7, CFrame.new(0, 1.15, 0), rgb(120, 190, 255), Enum.Material.Glass)
		ball.Transparency = 0.25
		part(m, BALL, Vector3.one * 0.5, CFrame.new(0.1, 1.2, 0.2), rgb(255, 240, 150), Enum.Material.Neon)
	elseif kind == "broker" then
		part(m, BLOCK, Vector3.new(0.22, 2.1, 0.22), CFrame.new(0, 1.05, 0), rgb(150, 156, 170), Enum.Material.Metal)
		part(m, BLOCK, Vector3.new(2.5, 0.14, 0.2), CFrame.new(0, 2.05, 0), GOLD, Enum.Material.Metal)
		for _, x in { -1.1, 1.1 } do
			disc(m, 0.95, 0.1, Vector3.new(x, 1.15, 0), rgb(214, 218, 230), Enum.Material.Metal)
			part(m, BLOCK, Vector3.new(0.05, 0.9, 0.05), CFrame.new(x, 1.6, 0), rgb(214, 218, 230), Enum.Material.Metal)
		end
		coinStack(m, 3, -1.1, 0)
		disc(m, 1.3, 0.3, Vector3.new(0, 0.15, 0), rgb(96, 100, 112), Enum.Material.Metal)
	elseif kind == "smith" then
		local iron = rgb(70, 74, 88)
		part(m, BLOCK, Vector3.new(1.7, 0.45, 0.9), CFrame.new(0, 0.22, 0), iron, Enum.Material.Metal)
		part(m, BLOCK, Vector3.new(0.8, 0.6, 0.6), CFrame.new(0, 0.75, 0), iron, Enum.Material.Metal)
		part(m, BLOCK, Vector3.new(2.1, 0.4, 0.85), CFrame.new(0, 1.2, 0), rgb(96, 100, 114), Enum.Material.Metal)
		part(m, BLOCK, Vector3.new(0.18, 1.5, 0.18), CFrame.new(0.4, 1.9, 0.1) * CFrame.Angles(0, 0, math.rad(-35)), rgb(150, 98, 56))
		part(m, BLOCK, Vector3.new(0.6, 0.42, 0.42), CFrame.new(-0.12, 2.5, 0.1), rgb(120, 124, 136), Enum.Material.Metal)
		part(m, BALL, Vector3.one * 0.3, CFrame.new(-0.6, 1.5, 0), rgb(255, 150, 40), Enum.Material.Neon)
	elseif kind == "fortune20" then
		flask(m, rgb(255, 200, 50), Vector3.zero, 1)
		for i = 1, 4 do
			local a = i * math.pi / 2 + 0.4
			part(m, BALL, Vector3.one * 0.28, CFrame.new(math.cos(a) * 1.3, 0.7 + (i % 2) * 0.8, math.sin(a) * 1.3), rgb(255, 236, 120), Enum.Material.Neon)
		end
	elseif kind == "jackpot20" then
		flask(m, rgb(255, 90, 140), Vector3.new(-0.3, 0, 0), 1)
		coinStack(m, 4, 1.45, -0.2)
		coinStack(m, 2, 1.0, 0.6)
	elseif kind == "fair30" then
		local reds = { rgb(232, 50, 56), rgb(255, 255, 255) }
		for i = 1, 6 do
			part(m, BLOCK, Vector3.new(0.4, 0.16, 1.9), CFrame.new(-1 + (i - 1) * 0.4, 1.85, 0), reds[(i % 2) + 1])
		end
		for _, p in { { -1, -0.85 }, { 1, -0.85 }, { -1, 0.85 }, { 1, 0.85 } } do
			part(m, BLOCK, Vector3.new(0.14, 1.8, 0.14), CFrame.new(p[1], 0.9, p[2]), rgb(150, 98, 56))
		end
		part(m, BLOCK, Vector3.new(1.7, 0.1, 1.5), CFrame.new(0, 0.08, 0), rgb(120, 190, 90))
		coinStack(m, 3, 0, 0)
	elseif kind == "luck30" or kind == "charm" then
		flask(m, rgb(90, 220, 110), Vector3.zero, 1)
	elseif kind == "coins30" then
		flask(m, rgb(255, 200, 50), Vector3.zero, 1)
	elseif kind == "brew30" then
		flask(m, rgb(90, 220, 110), Vector3.new(-1.05, 0, 0.2), 0.85)
		flask(m, rgb(255, 200, 50), Vector3.new(0, 0, -0.35), 1)
		flask(m, rgb(80, 170, 255), Vector3.new(1.05, 0, 0.2), 0.85)
	elseif kind == "server15" then
		flask(m, rgb(110, 190, 255), Vector3.zero, 1.15)
		for i = 1, 5 do
			local a = i * math.pi * 2 / 5
			part(m, BALL, Vector3.one * 0.3, CFrame.new(math.cos(a) * 1.35, 0.5 + (i % 2) * 0.9, math.sin(a) * 1.35), rgb(255, 240, 120), Enum.Material.Neon)
		end
	else
		coinStack(m, 3, 0, 0)
	end
	return m
end

---------------------------------------------------------------------
-- V27: мультяшные иконки магазина. Рисуются фигурами (Frame + UICorner + UIGradient + толстая UIStroke),
-- поэтому всегда чёткие и без загрузки картинок. Холст условный 100 x 100.
---------------------------------------------------------------------
local CARTOON_KEYS = {
	coins1 = true, coins2 = true, coins3 = true, coins4 = true, charm = true, insight = true, broker = true, smith = true,
	wrap = true, vip = true, founder = true, fortune20 = true, jackpot20 = true, fair30 = true, hour_bundle = true,
	server15 = true, bag = true, luck30 = true,
}

local function drawCartoon(parent: Instance, kind: string): boolean
	if not CARTOON_KEYS[kind] then
		return false
	end
	local W, BLACK = Color3.new(1, 1, 1), Color3.new(0, 0, 0)
	local function c(r: number, g: number, b: number): Color3
		return Color3.fromRGB(r, g, b)
	end
	local GOLD, RED, GREEN, BLUE, BROWN = c(255, 196, 36), c(236, 66, 72), c(76, 206, 92), c(84, 150, 255), c(176, 108, 52)
	local root = Instance.new("Frame")
	root.Name = "Cartoon"
	root.BackgroundTransparency = 1
	root.AnchorPoint = Vector2.new(0.5, 0.5)
	root.Position = UDim2.fromScale(0.5, 0.5)
	root.Size = UDim2.fromScale(1.1, 1.1)
	local ar = Instance.new("UIAspectRatioConstraint")
	ar.AspectRatio = 1
	ar.Parent = root
	local z = 1
	-- фигура с градиентом и толстой тёмной обводкой; shape: "circle" | "round" | "rect"
	local function S(shape: string, x: number, y: number, w: number, h: number, col: Color3, rot: number?, rad: number?): Frame
		z += 1
		local f = Instance.new("Frame")
		f.BorderSizePixel = 0
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.Position = UDim2.fromScale(x / 100, y / 100)
		f.Size = UDim2.fromScale(w / 100, h / 100)
		f.Rotation = rot or 0
		f.BackgroundColor3 = W
		f.ZIndex = z
		local cr = Instance.new("UICorner")
		cr.CornerRadius = UDim.new(rad or (shape == "circle" and 0.5 or (shape == "round" and 0.3 or 0.06)), 0)
		cr.Parent = f
		local g = Instance.new("UIGradient")
		g.Rotation = 90
		g.Color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, col:Lerp(W, 0.42)),
			ColorSequenceKeypoint.new(0.5, col),
			ColorSequenceKeypoint.new(1, col:Lerp(BLACK, 0.2)),
		})
		g.Parent = f
		local st = Instance.new("UIStroke")
		st.Thickness = 3
		st.Color = col:Lerp(BLACK, 0.74)
		st.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
		st.Parent = f
		f.Parent = root
		return f
	end
	-- блик
	local function H(x: number, y: number, w: number, h: number, rot: number?)
		z += 1
		local f = Instance.new("Frame")
		f.BorderSizePixel = 0
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.Position = UDim2.fromScale(x / 100, y / 100)
		f.Size = UDim2.fromScale(w / 100, h / 100)
		f.Rotation = rot or 0
		f.BackgroundColor3 = W
		f.BackgroundTransparency = 0.45
		f.ZIndex = z
		local cr = Instance.new("UICorner")
		cr.CornerRadius = UDim.new(0.5, 0)
		cr.Parent = f
		f.Parent = root
	end
	-- надпись с обводкой
	local function T(text: string, x: number, y: number, size: number, col: Color3)
		z += 1
		local l = Instance.new("TextLabel")
		l.BackgroundTransparency = 1
		l.AnchorPoint = Vector2.new(0.5, 0.5)
		l.Position = UDim2.fromScale(x / 100, y / 100)
		l.Size = UDim2.fromScale(size / 100, size / 100)
		l.Font = Enum.Font.FredokaOne
		l.Text = text
		l.TextScaled = true
		l.TextColor3 = col
		l.ZIndex = z
		local st = Instance.new("UIStroke")
		st.Thickness = 2.5
		st.Color = col:Lerp(BLACK, 0.72)
		st.Parent = l
		l.Parent = root
	end
	-- искорка
	local function SP(x: number, y: number, s: number, col: Color3?)
		S("rect", x, y, s, s, col or c(255, 244, 150), 45, 0.12)
	end
	local function coin(x: number, y: number, s: number)
		S("circle", x, y, s, s, GOLD)
		S("circle", x, y, s * 0.68, s * 0.68, c(255, 226, 96))
		T("$", x, y, s * 0.5, c(196, 124, 8))
		H(x - s * 0.18, y - s * 0.22, s * 0.22, s * 0.12, -30)
	end
	local function flask(x: number, y: number, sc: number, col: Color3)
		S("round", x, y - 30 * sc, 18 * sc, 26 * sc, c(206, 232, 255), 0, 0.3)
		S("round", x, y - 44 * sc, 16 * sc, 10 * sc, BROWN, 0, 0.3)
		S("circle", x, y, 56 * sc, 56 * sc, col)
		S("circle", x, y + 4 * sc, 40 * sc, 36 * sc, col:Lerp(W, 0.25))
		H(x - 14 * sc, y - 8 * sc, 12 * sc, 18 * sc, 20)
	end
	local function crown(body: Color3, gem1: Color3, gem2: Color3, gem3: Color3)
		S("rect", 24, 40, 22, 22, body, 45, 0.14)
		S("rect", 50, 30, 26, 26, body, 45, 0.14)
		S("rect", 76, 40, 22, 22, body, 45, 0.14)
		S("round", 50, 62, 66, 34, body, 0, 0.2)
		S("round", 50, 80, 70, 12, body:Lerp(BLACK, 0.12), 0, 0.5)
		S("circle", 24, 28, 12, 12, W)
		S("circle", 50, 17, 14, 14, W)
		S("circle", 76, 28, 12, 12, W)
		S("circle", 30, 62, 12, 12, gem1)
		S("circle", 50, 62, 14, 14, gem2)
		S("circle", 70, 62, 12, 12, gem3)
		H(36, 54, 22, 6, 0)
	end
	local function chest(extra: boolean)
		if extra then
			coin(22, 36, 22)
			coin(78, 34, 24)
			S("rect", 50, 22, 20, 20, c(110, 226, 255), 45, 0.12)
			H(46, 18, 6, 6, 0)
		end
		S("round", 50, 68, 72, 38, c(168, 98, 44), 0, 0.14)
		S("round", 50, 46, 72, 34, c(196, 124, 58), 0, 0.42)
		S("rect", 50, 56, 72, 7, GOLD)
		S("rect", 28, 56, 7, 38, GOLD)
		S("rect", 72, 56, 7, 38, GOLD)
		S("round", 50, 62, 14, 16, c(255, 226, 96), 0, 0.25)
		S("circle", 50, 62, 5, 5, c(120, 70, 10))
		H(34, 38, 26, 7, -8)
	end

	if kind == "coins1" then
		coin(50, 52, 62)
		coin(22, 78, 26)
		coin(80, 80, 22)
		SP(80, 22, 11)
	elseif kind == "coins2" then
		S("round", 50, 30, 28, 20, BROWN, 0, 0.3)
		S("circle", 50, 64, 66, 60, c(196, 124, 62))
		S("round", 50, 38, 38, 9, RED, 0, 0.5)
		coin(50, 68, 34)
		H(30, 56, 12, 20, 20)
		SP(82, 24, 10)
	elseif kind == "coins3" then
		chest(false)
		SP(84, 22, 11)
		SP(16, 30, 8)
	elseif kind == "coins4" then
		chest(true)
		SP(10, 14, 9)
		SP(92, 54, 8)
	elseif kind == "charm" then
		for _, p in { { 38, 36 }, { 62, 36 }, { 38, 60 }, { 62, 60 } } do
			S("circle", p[1], p[2], 32, 32, GREEN)
			H(p[1] - 6, p[2] - 7, 9, 6, -30)
		end
		S("circle", 50, 48, 18, 18, GOLD)
		S("round", 58, 86, 8, 22, c(52, 160, 70), 14, 0.5)
		SP(84, 22, 11)
		SP(16, 78, 8)
	elseif kind == "insight" then
		S("round", 50, 88, 56, 12, c(122, 80, 48), 0, 0.5)
		S("round", 50, 80, 40, 12, c(160, 108, 62), 0, 0.5)
		S("circle", 50, 44, 66, 66, c(118, 146, 255))
		S("circle", 50, 46, 46, 46, c(176, 202, 255))
		S("rect", 50, 46, 14, 14, c(255, 240, 140), 0, 0.1)
		S("rect", 50, 46, 14, 14, c(255, 240, 140), 45, 0.1)
		H(34, 28, 16, 9, -35)
		SP(84, 16, 9)
	elseif kind == "broker" then
		S("round", 50, 90, 44, 10, c(150, 160, 182), 0, 0.5)
		S("round", 50, 56, 9, 70, c(176, 186, 206), 0, 0.4)
		S("round", 50, 22, 78, 9, GOLD, 0, 0.5)
		S("circle", 50, 22, 14, 14, c(255, 226, 96))
		S("rect", 20, 38, 4, 24, c(176, 186, 206))
		S("rect", 80, 38, 4, 24, c(176, 186, 206))
		S("round", 20, 56, 32, 11, c(214, 224, 240), 0, 0.5)
		S("round", 80, 56, 32, 11, c(214, 224, 240), 0, 0.5)
		coin(20, 48, 16)
		coin(80, 48, 16)
	elseif kind == "smith" then
		S("round", 40, 84, 52, 12, c(86, 92, 108), 0, 0.3)
		S("round", 40, 70, 26, 16, c(70, 76, 92), 0, 0.3)
		S("round", 40, 56, 66, 18, c(110, 118, 136), 0, 0.25)
		S("round", 8, 56, 20, 12, c(110, 118, 136), 0, 0.4)
		S("round", 70, 38, 8, 50, BROWN, 34, 0.4)
		S("round", 80, 20, 32, 18, c(160, 168, 186), 34, 0.25)
		S("circle", 30, 38, 11, 11, c(255, 170, 40))
		S("circle", 18, 30, 7, 7, c(255, 236, 110))
		S("circle", 44, 28, 6, 6, c(255, 236, 110))
		H(30, 52, 20, 5, 0)
	elseif kind == "wrap" then
		S("round", 50, 66, 62, 46, c(240, 92, 172), 0, 0.14)
		S("rect", 50, 66, 12, 46, GOLD)
		S("round", 50, 42, 68, 18, c(252, 116, 188), 0, 0.3)
		S("rect", 50, 42, 12, 18, GOLD)
		S("circle", 37, 26, 22, 15, GOLD, -25)
		S("circle", 63, 26, 22, 15, GOLD, 25)
		S("circle", 50, 31, 11, 11, c(255, 226, 96))
		H(28, 62, 8, 22, 0)
	elseif kind == "vip" then
		crown(GOLD, RED, BLUE, GREEN)
		SP(90, 20, 10)
	elseif kind == "founder" then
		local glow = S("circle", 50, 48, 92, 92, c(255, 226, 120))
		glow.BackgroundTransparency = 0.6
		glow:FindFirstChildOfClass("UIStroke").Transparency = 0.6
		crown(c(160, 86, 238), c(255, 226, 96), c(110, 232, 255), c(255, 226, 96))
		SP(10, 20, 10)
		SP(92, 12, 8)
	elseif kind == "fortune20" then
		flask(50, 64, 1, GOLD)
		SP(18, 36, 11)
		SP(84, 44, 9)
		SP(76, 16, 7)
	elseif kind == "jackpot20" then
		S("round", 50, 54, 74, 66, c(226, 52, 74), 0, 0.14)
		S("round", 50, 20, 44, 16, GOLD, 0, 0.4)
		S("round", 50, 52, 60, 34, c(255, 250, 236), 0, 0.12)
		T("7", 33, 52, 24, RED)
		T("7", 50, 52, 24, RED)
		T("7", 67, 52, 24, RED)
		S("round", 90, 40, 6, 32, c(180, 190, 210), 0, 0.5)
		S("circle", 90, 24, 13, 13, RED)
		coin(28, 88, 17)
		coin(72, 88, 17)
	elseif kind == "fair30" then
		S("round", 22, 66, 8, 48, BROWN, 0, 0.3)
		S("round", 78, 66, 8, 48, BROWN, 0, 0.3)
		S("round", 50, 84, 70, 14, c(214, 156, 84), 0, 0.3)
		for i = 0, 4 do
			S("round", 20 + i * 15, 42, 16, 30, (i % 2 == 0) and RED or c(255, 252, 244), 0, 0.3)
		end
		S("round", 50, 24, 80, 14, RED, 0, 0.5)
		S("rect", 50, 10, 4, 12, c(190, 190, 200))
		S("rect", 58, 8, 14, 8, GOLD)
		coin(50, 70, 20)
	elseif kind == "hour_bundle" then
		flask(24, 66, 0.72, GOLD)
		flask(76, 66, 0.72, c(90, 220, 200))
		flask(50, 58, 0.92, c(255, 96, 150))
		SP(86, 22, 10)
		SP(14, 24, 8)
	elseif kind == "server15" then
		S("circle", 50, 52, 70, 70, c(70, 150, 255))
		S("circle", 38, 42, 26, 22, GREEN)
		S("circle", 62, 64, 24, 20, GREEN)
		S("circle", 66, 36, 12, 12, GREEN)
		T("x2", 50, 54, 34, c(255, 226, 96))
		H(34, 30, 14, 8, -35)
		SP(14, 18, 10)
		SP(88, 84, 9)
	elseif kind == "bag" then
		S("round", 24, 60, 8, 36, BROWN, 0, 0.4)
		S("round", 76, 60, 8, 36, BROWN, 0, 0.4)
		S("round", 50, 64, 54, 56, c(84, 176, 96), 0, 0.3)
		S("round", 50, 38, 54, 28, c(72, 156, 84), 0, 0.5)
		S("round", 50, 72, 34, 22, c(62, 134, 74), 0, 0.25)
		S("round", 50, 48, 12, 12, GOLD, 0, 0.25)
		H(34, 58, 8, 18, 0)
	elseif kind == "luck30" then
		flask(50, 64, 1, c(90, 220, 110))
		SP(80, 20, 9)
	end
	root.Parent = parent
	return true
end

Shop.cartoon = drawCartoon

-- Ставит иконку товара в parent. Копья и звери берутся из самой игры.
local function icon(parent: Instance, kind: string, spin: number?)
	-- V27: мультяшные иконки (чёткие, из фигур) важнее картинок и 3D-моделей
	if drawCartoon(parent, kind) then
		return
	end
	-- нарисованная иллюстрация (ART) важнее 3D-модели
	if artImage(parent, kind:sub(1, 6) == "spear:" and "spear" or kind) then
		return
	end
	local ok, err = pcall(function()
		if kind:sub(1, 6) == "spear:" then
			local Menus = require(script.Parent.Menus) :: any
			Menus.spearView(kind:sub(7), parent, spin or 0)
			return
		end
		-- Lucky Charm: радужный лунный кролик из самой игры (Card.model с мутацией возвращает копию)
		local model: Model? = if kind == "charm" then Card.model("moonrabbit", "rainbow") else nil
		local m: Model = model or buildIcon(kind)
		local vp = UI.viewport(m, nil, math.rad(-28), spin or 0)
		vp.Parent = parent
		m:Destroy()
	end)
	if not ok then
		warn("[Shop] icon " .. kind .. ": " .. tostring(err))
	end
end

---------------------------------------------------------------------
-- Кирпичики оформления
---------------------------------------------------------------------
local function box(p: { [string]: any }): Frame
	local f = Instance.new("Frame")
	f.BorderSizePixel = 0
	f.BackgroundColor3 = Color3.new(1, 1, 1)
	f.Size = p.Size or UDim2.fromOffset(100, 100)
	if p.Position then
		f.Position = p.Position
	end
	if p.AnchorPoint then
		f.AnchorPoint = p.AnchorPoint
	end
	if p.ZIndex then
		f.ZIndex = p.ZIndex
	end
	if p.LayoutOrder then
		f.LayoutOrder = p.LayoutOrder
	end
	if p.Name then
		f.Name = p.Name
	end
	if p.Rotation then
		f.Rotation = p.Rotation
	end
	if p.Clip then
		f.ClipsDescendants = true
	end
	local g = Instance.new("UIGradient")
	g.Rotation = 90
	if p.Mid then
		g.Color = ColorSequence.new({ ColorSequenceKeypoint.new(0, p.Top), ColorSequenceKeypoint.new(0.55, p.Mid), ColorSequenceKeypoint.new(1, p.Bottom) })
	else
		g.Color = ColorSequence.new(p.Top, p.Bottom or p.Top)
	end
	g.Parent = f
	UI.corner(p.Radius or 10).Parent = f
	if p.Line then
		UI.stroke(p.Line, p.LineThick or 3, 0, true).Parent = f
	end
	if p.Parent then
		f.Parent = p.Parent
	end
	return f
end

local function holder(parent: Instance, size: UDim2, pos: UDim2, z: number?): Frame
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = size
	f.Position = pos
	f.ZIndex = z or 2
	f.Parent = parent
	return f
end

local function glowSpot(parent: Instance, color: Color3, size: number, pos: UDim2, transp: number)
	local g = UI.glow(parent, color, size, transp)
	g.Position = pos
	g.ZIndex = 1
end

-- Заголовок раздела: тёмная плашка с золотыми линиями (Exclusives / Passes в референсе)
local function sectionBar(o, parent: Instance, text: string, order: number)
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = UDim2.new(1, 0, 0, 32)
	f.LayoutOrder = order
	-- f — место в списке; всё содержимое и масштаб «выпрыгивания» — во внутреннем кадре с центром-якорем
	local c = Instance.new("Frame")
	c.BackgroundTransparency = 1
	c.AnchorPoint = Vector2.new(0.5, 0.5)
	c.Position = UDim2.fromScale(0.5, 0.5)
	c.Size = UDim2.fromScale(1, 1)
	c.Parent = f
	local bar = Instance.new("Frame")
	bar.BorderSizePixel = 0
	bar.BackgroundColor3 = K.barDark
	bar.BackgroundTransparency = 0.3
	bar.Size = UDim2.new(1, 0, 1, -6)
	bar.Position = UDim2.fromOffset(0, 3)
	local fade = Instance.new("UIGradient")
	fade.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, 0), NumberSequenceKeypoint.new(0.8, 0), NumberSequenceKeypoint.new(1, 1),
	})
	fade.Parent = bar
	bar.Parent = c
	for side = 0, 1 do
		local l = Instance.new("Frame")
		l.BorderSizePixel = 0
		l.BackgroundColor3 = K.gold
		l.Size = UDim2.new(1, 0, 0, 2)
		l.Position = UDim2.new(0, 0, 0, side == 0 and 3 or 27)
		local g = Instance.new("UIGradient")
		g.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, 0), NumberSequenceKeypoint.new(0.75, 0), NumberSequenceKeypoint.new(1, 1),
		})
		g.Parent = l
		l.Parent = c
	end
	UI.label({ Text = text, TextSize = 21, Color = K.white, StrokeColor = K.navy, Stroke = 3, Size = UDim2.fromScale(1, 1), ZIndex = 3, Parent = c })
	f.Parent = parent
	if o.intro then
		o.n += 1
		local sc = Instance.new("UIScale")
		sc.Name = "Intro"
		sc.Scale = 0
		sc.Parent = c
		task.delay(0.6 + math.min(o.n, 14) * 0.045, function()
			if sc.Parent then
				UI.tween(sc, 0.35, { Scale = 1 }, Enum.EasingStyle.Back)
			end
		end)
	end
end

local function grid(parent: Instance, cols: number, cellHeight: number, order: number): Frame
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = UDim2.new(1, 0, 0, 0)
	f.AutomaticSize = Enum.AutomaticSize.Y
	f.LayoutOrder = order
	local g = Instance.new("UIGridLayout")
	g.CellSize = UDim2.new(1 / cols, -math.ceil(10 * (cols - 1) / cols), 0, cellHeight)
	g.CellPadding = UDim2.fromOffset(10, 10)
	g.SortOrder = Enum.SortOrder.LayoutOrder
	g.FillDirectionMaxCells = cols
	g.Parent = f
	f.Parent = parent
	return f
end

---------------------------------------------------------------------
-- Цены и покупка
---------------------------------------------------------------------
local priceCache: { [string]: number } = {}

local function priceText(item: any): string
	if item.id <= 0 and not Perks.state().studio then
		return "SOON"
	end
	return ROBUX .. " " .. tostring(priceCache[item.key] or item.price)
end

local function fetchPrice(item: any, btn: Frame)
	if item.id <= 0 or priceCache[item.key] then
		return
	end
	task.spawn(function()
		local ok, info = pcall(function()
			return MarketplaceService:GetProductInfo(item.id, item.pass and Enum.InfoType.GamePass or Enum.InfoType.Product)
		end)
		if ok and type(info) == "table" and type(info.PriceInRobux) == "number" then
			priceCache[item.key] = info.PriceInRobux
			if btn.Parent then
				UI.setText(btn, priceText(item))
			end
		end
	end)
end

local ShopEv: RemoteEvent? = nil
local ShopFn: RemoteFunction? = nil

local function buy(item: any)
	local st = Perks.state()
	if not st.loaded then
		UI.toast("The shop is still loading your data. Try again in a moment.", "warn")
		return
	end
	if item.id > 0 then
		if item.pass then
			MarketplaceService:PromptGamePassPurchase(player, item.id)
		else
			MarketplaceService:PromptProductPurchase(player, item.id)
		end
	elseif st.studio and ShopFn then
		local fn = ShopFn
		task.spawn(function()
			pcall(function()
				fn:InvokeServer("testBuy", item.key)
			end)
		end)
	else
		UI.toast("Coming soon!", "info")
	end
end

local function buyButton(item: any, size: UDim2, pos: UDim2, textSize: number, parent: Instance): Frame
	local b = UI.button({ Text = priceText(item), TextSize = textSize, Color = K.green, Size = size, Position = pos, Sound = "press" }, function()
		buy(item)
	end)
	b.Parent = parent
	fetchPrice(item, b)
	return b
end

---------------------------------------------------------------------
-- Экран «получено»
---------------------------------------------------------------------
local function unlock(item: any, ribbon: string)
	local ov = Instance.new("TextButton")
	ov.Name = "ShopUnlock"
	ov.Text = ""
	ov.AutoButtonColor = false
	ov.BorderSizePixel = 0
	ov.BackgroundColor3 = rgb(8, 6, 30)
	ov.BackgroundTransparency = 1
	ov.Size = UDim2.fromScale(1, 1)
	ov.ZIndex = 60
	ov.Parent = UI.top
	UI.tween(ov, 0.25, { BackgroundTransparency = 0.16 })
	local rays = UI.rays(ov, rgb(255, 220, 120), 14, 980, 22)
	rays.Position = UDim2.fromScale(0.5, 0.42)
	local pop = Instance.new("Frame")
	pop.BackgroundTransparency = 1
	pop.AnchorPoint = Vector2.new(0.5, 0.5)
	pop.Position = UDim2.fromScale(0.5, 0.4)
	pop.Size = UDim2.fromOffset(260, 260)
	pop.ZIndex = 3
	local sc = Instance.new("UIScale")
	sc.Scale = 0
	sc.Parent = pop
	pop.Parent = ov
	glowSpot(pop, rgb(255, 220, 120), 380, UDim2.fromScale(0.5, 0.5), 0.35)
	icon(holder(pop, UDim2.fromScale(1, 1), UDim2.new(), 3), item.key == "starter" and ("spear:" .. SHOP.STARTER.spear) or item.key, 1.2)
	UI.tween(sc, 0.55, { Scale = 1 }, Enum.EasingStyle.Back)
	local title = UI.label({ Text = string.upper(item.name), TextSize = 62, Color = K.goldText, StrokeColor = rgb(90, 42, 0), Stroke = 5, Size = UDim2.fromOffset(900, 70), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.66), ZIndex = 4, Parent = ov })
	local band = box({ Top = rgb(255, 90, 90), Bottom = rgb(200, 20, 28), Line = K.winLine, Size = UDim2.fromOffset(320, 50), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.76), ZIndex = 4, Parent = ov })
	UI.label({ Text = ribbon, TextSize = 28, StrokeColor = K.deepRed, Size = UDim2.fromScale(1, 1), Parent = band })
	UI.label({ Text = "Tap anywhere to continue", TextSize = 18, Stroke = 2, Size = UDim2.fromOffset(400, 24), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.86), ZIndex = 4, Parent = ov })
	UI.punch(title, 0.5)
	UI.punch(band, 0.4)
	Sfx.play("level")
	UI.confetti(60, { K.goldText, K.red, K.green, rgb(77, 184, 255) })
	local closed = false
	local function close()
		if closed then
			return
		end
		closed = true
		ov:Destroy()
	end
	task.delay(0.7, function()
		if not closed then
			ov.Activated:Connect(close)
		end
	end)
	task.delay(7, close)
end

---------------------------------------------------------------------
-- Окно
---------------------------------------------------------------------
---------------------------------------------------------------------
-- Окно: небо, облака, самолёт с баннером, плитки
---------------------------------------------------------------------
local BW = 768 -- ширина тела окна (окно 780 − 2×6)
local HEAD_H = 66

type Anim = { inst: Instance, fn: (number) -> () }
type Open = {
	win: Frame, scroll: ScrollingFrame, pill: TextLabel, status: { [string]: TextLabel },
	sky: Frame, headScale: UIScale, headGroup: Frame,
	anim: { Anim }, -- живёт всё время, пока открыто окно
	cards: { Anim }, -- пересоздаётся вместе с содержимым (renderBody)
	shiny: { GuiObject },
	intro: boolean, closing: boolean, n: number,
}
local open: Open? = nil

local function reg(list: { Anim }, inst: Instance, fn: (number) -> ())
	table.insert(list, { inst = inst, fn = fn })
end

-- Мерцающая искорка
local function sparkle(list: { Anim }, parent: Instance, x: number, y: number, size: number, phase: number, z: number?)
	local s = Instance.new("ImageLabel")
	s.BackgroundTransparency = 1
	s.Image = UI.IMG.sparkle
	s.ImageColor3 = K.white
	s.AnchorPoint = Vector2.new(0.5, 0.5)
	s.Position = UDim2.fromScale(x, y)
	s.Size = UDim2.fromOffset(size, size)
	s.ImageTransparency = 1
	s.ZIndex = z or 3
	s.Parent = parent
	reg(list, s, function(t)
		local k = math.sin(t * 2.3 + phase)
		s.ImageTransparency = k > 0 and (1 - k) * 0.85 or 1
		local sz = size * (0.55 + 0.45 * math.max(k, 0))
		s.Size = UDim2.fromOffset(sz, sz)
	end)
end

-- Зверёк из игры (настоящая модель из ReplicatedStorage.Animals) во вьюпорте; yaw: 90 — смотрит вправо, -18 — анфас
local function animalView(parent: Instance, id: string, yawDeg: number, w: number, h: number): Frame
	local f = Instance.new("Frame")
	f.Name = "Animal_" .. id
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromOffset(w, h)
	f.Parent = parent
	if artImage(f, "animal_" .. id .. (yawDeg > 0 and "_R" or "_F")) then
		return f
	end
	local ok, err = pcall(function()
		local m = Card.model(id)
		if m then
			UI.viewport(m, nil, math.rad(yawDeg), 0).Parent = f
		end
	end)
	if not ok then
		warn("[Shop] animal " .. id .. ": " .. tostring(err))
	end
	return f
end

-- Луг Forest Edge: солнце, холмы, деревья, цветы и зверьки, неспешно идущие вдоль холмов
local function buildMeadow(o: Open, sky: Frame)
	local function blob(pos: Vector2, size: Vector2, col: Color3, z: number): Frame
		local b = Instance.new("Frame")
		b.BorderSizePixel = 0
		b.BackgroundColor3 = col
		b.Position = UDim2.fromOffset(pos.X, pos.Y)
		b.Size = UDim2.fromOffset(size.X, size.Y)
		b.ZIndex = z
		UI.corner(0.5, true).Parent = b
		b.Parent = sky
		return b
	end
	local sun = UI.glow(sky, rgb(255, 246, 176), 300, 0.3)
	sun.Position = UDim2.fromOffset(BW - 120, 70)
	sun.ZIndex = 1
	blob(Vector2.new(-140, 300), Vector2.new(880, 520), K.hill1, 1)
	blob(Vector2.new(360, 350), Vector2.new(700, 460), K.hill2, 1)
	blob(Vector2.new(-320, 420), Vector2.new(900, 400), K.hill3, 1)
	-- деревья: ствол и круглая крона
	for i, t in { { 60, 292 }, { 150, 318 }, { 560, 330 }, { 680, 298 }, { 430, 346 } } do
		local s = 0.8 + (i % 3) * 0.18
		local trunk = Instance.new("Frame")
		trunk.BorderSizePixel = 0
		trunk.BackgroundColor3 = K.trunk
		trunk.Size = UDim2.fromOffset(8 * s, 26 * s)
		trunk.Position = UDim2.fromOffset(t[1] + 18 * s, t[2] + 30 * s)
		trunk.ZIndex = 1
		trunk.Parent = sky
		blob(Vector2.new(t[1], t[2]), Vector2.new(46 * s, 46 * s), K.leaf, 1)
		blob(Vector2.new(t[1] + 14 * s, t[2] - 12 * s), Vector2.new(34 * s, 34 * s), K.leaf, 1)
	end
	-- цветы
	local flowers = { rgb(255, 255, 255), rgb(255, 226, 90), rgb(255, 150, 190) }
	for i = 1, 16 do
		blob(Vector2.new((i * 53) % (BW - 10), 380 + (i * 37) % 150), Vector2.new(7, 7), flowers[i % 3 + 1], 1)
	end
	-- зверьки идут по лугу вправо, подпрыгивая
	local walkers = { { "rabbit", 54 }, { "squirrel", 62 }, { "hedgehog", 56 }, { "fox", 66 }, { "dodo", 60 }, { "moonrabbit", 58 } }
	for i, w in walkers do
		local f = animalView(sky, w[1], 90, w[2] + 26, w[2])
		f.ZIndex = 2
		local span = BW + 260
		local off = i * 131
		local base = 330 + (i % 3) * 58
		reg(o.anim, f, function(t)
			local x = (off + t * (14 + i * 3)) % span - 130
			f.Position = UDim2.fromOffset(x, base - math.abs(math.sin(t * 4 + i * 1.7)) * 6)
		end)
	end
	for i = 1, 9 do
		sparkle(o.anim, sky, (i * 0.137) % 1, 0.08 + ((i * 0.31) % 0.4), 10 + (i % 3) * 4, i * 1.9, 1)
	end
end

-- Красная корзинка (значок магазина)
local function basketIcon(parent: Instance, z: number): Frame
	local h = holder(parent, UDim2.fromOffset(56, 50), UDim2.fromOffset(0, 0), z)
	local handle = Instance.new("Frame")
	handle.BackgroundTransparency = 1
	handle.Size = UDim2.fromOffset(32, 32)
	handle.Position = UDim2.fromOffset(12, 0)
	handle.ZIndex = z
	UI.corner(0.5, true).Parent = handle
	UI.stroke(rgb(255, 222, 228), 5, 0, true).Parent = handle
	handle.Parent = h
	local body = box({ Top = rgb(255, 98, 108), Bottom = rgb(190, 22, 44), Line = rgb(84, 6, 22), LineThick = 3, Radius = 9, Size = UDim2.fromOffset(52, 28), Position = UDim2.fromOffset(2, 18), ZIndex = z + 1, Parent = h })
	for i = 1, 3 do
		local slit = Instance.new("Frame")
		slit.BorderSizePixel = 0
		slit.BackgroundColor3 = rgb(110, 6, 26)
		slit.BackgroundTransparency = 0.35
		slit.Size = UDim2.fromOffset(4, 14)
		slit.Position = UDim2.fromOffset(10 + (i - 1) * 14, 8)
		slit.ZIndex = z + 2
		UI.corner(2).Parent = slit
		slit.Parent = body
	end
	local rim = box({ Top = rgb(255, 150, 156), Bottom = rgb(236, 56, 72), Line = rgb(84, 6, 22), LineThick = 2, Radius = 5, Size = UDim2.fromOffset(58, 9), Position = UDim2.fromOffset(-1, 14), ZIndex = z + 3, Parent = h })
	rim.Name = "Rim"
	h.Rotation = -8
	return h
end

-- Летящее копьё (настоящая модель из игры) тянет баннер: острие вправо, позади искры и верёвка
local function flySpear(parent: Instance, o: Open): Frame
	local j = Instance.new("Frame")
	j.Name = "FlyingSpear"
	j.BackgroundTransparency = 1
	j.Size = UDim2.fromOffset(150, 150)
	j.AnchorPoint = Vector2.new(0, 0.5)
	j.ZIndex = 20
	local rope = Instance.new("Frame")
	rope.BorderSizePixel = 0
	rope.BackgroundColor3 = K.white
	rope.Size = UDim2.fromOffset(34, 3)
	rope.Position = UDim2.fromOffset(-26, 73)
	rope.ZIndex = 20
	rope.Parent = j
	for i, y in { 58, 90 } do
		local l = Instance.new("Frame")
		l.BorderSizePixel = 0
		l.BackgroundColor3 = K.white
		l.BackgroundTransparency = 0.45
		l.Size = UDim2.fromOffset(46 - i * 10, 3)
		l.Position = UDim2.fromOffset(-60 + i * 10, y)
		l.ZIndex = 20
		UI.corner(2).Parent = l
		l.Parent = j
	end
	local flat = artImage(j, "flyspear")
	if flat then
		flat.Size = UDim2.fromScale(1, 0.5)
		flat.Position = UDim2.fromScale(0, 0.25)
		flat.ZIndex = 21
	end
	local ok, err = pcall(function()
		if flat then
			return
		end
		local tpl = RS.Assets.Spears:FindFirstChild(SHOP.STARTER.spear)
		if not tpl or not tpl:IsA("Model") then
			return
		end
		local holder = Instance.new("Model")
		holder.WorldPivot = CFrame.new()
		local s = tpl:Clone()
		s:PivotTo(CFrame.Angles(0, 0, math.rad(90)))
		s.Parent = holder
		local vp = UI.viewport(holder, nil, 0, 0)
		vp.ZIndex = 21
		vp.Parent = j
		holder:Destroy()
	end)
	if not ok then
		warn("[Shop] flying spear: " .. tostring(err))
	end
	sparkle(o.anim, j, -0.05, 0.5, 16, 0.4, 22)
	sparkle(o.anim, j, -0.2, 0.4, 12, 1.9, 22)
	sparkle(o.anim, j, -0.14, 0.62, 12, 3.1, 22)
	j.Parent = parent
	return j
end

-- Анимация открытия: копьё тянет баннер «Shop», потом разворачивается небо и выпрыгивают плитки
local function playIntro(o: Open, body: Frame, mask: Frame, ribbon: Frame, popTargets: { { any } })
	local function alive(): boolean
		return open == o and body.Parent ~= nil
	end
	local j = flySpear(body, o)
	j.Position = UDim2.fromOffset(-150, 33)
	local lin = Enum.EasingStyle.Linear
	UI.tween(j, 0.14, { Position = UDim2.fromOffset(34, 33) }, lin)
	task.delay(0.14, function()
		if not alive() then
			return
		end
		Sfx.play("sparkle", 1.3, 0.35)
		UI.tween(j, 0.55, { Position = UDim2.fromOffset(BW + 34, 33) }, lin)
		UI.tween(mask, 0.55, { Size = UDim2.new(0, BW, 0, HEAD_H) }, lin)
	end)
	task.delay(0.69, function()
		if not alive() then
			return
		end
		UI.tween(j, 0.14, { Position = UDim2.fromOffset(BW + 230, 33) }, lin)
		UI.shine(ribbon, 0.7)
		UI.burst(mask.AbsolutePosition + Vector2.new(mask.AbsoluteSize.X - 20, mask.AbsoluteSize.Y / 2), K.frameGlow, 8, 240)
	end)
	task.delay(0.9, function()
		j:Destroy()
	end)
	-- облака, значок и кнопка «выпрыгивают»
	for _, t in popTargets do
		local obj, delay = t[1] :: GuiObject, t[2] :: number
		local sc = Instance.new("UIScale")
		sc.Name = "Pop"
		sc.Scale = 0
		sc.Parent = obj
		task.delay(delay, function()
			if sc.Parent then
				UI.tween(sc, 0.4, { Scale = 1 }, Enum.EasingStyle.Back)
			end
		end)
	end
	-- небо раскатывается вниз
	task.delay(0.42, function()
		if alive() then
			UI.tween(o.sky, 0.4, { Size = UDim2.new(1, 0, 1, -58) }, Enum.EasingStyle.Quad)
		end
	end)
	task.delay(1.7, function()
		o.intro = false
	end)
end

local function closeAnimated(o: Open)
	if o.closing then
		return
	end
	o.closing = true
	Sfx.play("close")
	o.scroll.Visible = false
	UI.tween(o.sky, 0.22, { Size = UDim2.new(1, 0, 0, 0) }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
	UI.tween(o.headScale, 0.3, { Scale = 0 }, Enum.EasingStyle.Back, Enum.EasingDirection.In)
	task.delay(0.3, function()
		if open == o then
			UI.closeWindow(true)
		end
	end)
end

---------------------------------------------------------------------
-- Содержимое
---------------------------------------------------------------------
local function boostLeftFor(item: any): number
	if item.kind == "server" then
		return Perks.serverLeft()
	end
	if not item.boosts then
		return 0 -- пассы (Founder) не бусты
	end
	local left = math.huge
	for _, id in item.boosts do
		left = math.min(left, Backend.boostLeft(id))
	end
	return left == math.huge and 0 or left
end

local function starterVisible(): boolean
	local d = Backend.data
	local st = Perks.state()
	if st.starter or not d then
		return false
	end
	return (d.level or 1) < SHOP.STARTER_MAX_LEVEL and (d.tutorial or 1) > 4
end

-- Плитка/баннер выпрыгивает при открытии окна (один раз, не при обновлении)
local function slot(parent: Instance, order: number, height: number?): Frame
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = UDim2.new(1, 0, 0, height or 0)
	f.LayoutOrder = order
	f.Parent = parent
	return f
end
local CENTER = { Size = UDim2.fromScale(1, 1), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5) }

local function introPop(o: Open, obj: GuiObject)
	if not o.intro then
		return
	end
	o.n += 1
	local sc = Instance.new("UIScale")
	sc.Name = "Intro"
	sc.Scale = 0
	sc.Parent = obj
	task.delay(0.6 + math.min(o.n, 14) * 0.045, function()
		if sc.Parent then
			UI.tween(sc, 0.38, { Scale = 1 }, Enum.EasingStyle.Back)
		end
	end)
end

-- Иконка покачивается
local function bob(o: Open, h: GuiObject, base: UDim2, amp: number, phase: number)
	reg(o.cards, h, function(t)
		h.Position = UDim2.new(base.X.Scale, base.X.Offset, base.Y.Scale, base.Y.Offset + math.sin(t * 2.1 + phase) * amp)
	end)
end

local function gloss(f: Frame, h: number)
	local g = Instance.new("Frame")
	g.BorderSizePixel = 0
	g.BackgroundColor3 = K.white
	g.BackgroundTransparency = 0.84
	g.Size = UDim2.new(1, -12, 0, h)
	g.Position = UDim2.fromOffset(6, 4)
	g.ZIndex = 2
	UI.corner(9).Parent = g
	g.Parent = f
end

local function renderHero(o: Open, parent: Instance, order: number)
	local item = Config.SHOP_BY_KEY.starter
	local st = SHOP.STARTER
	local f = box({ Top = K.heroTop, Mid = K.heroMid, Bottom = K.heroBot, Line = K.heroLine, Size = CENTER.Size, AnchorPoint = CENTER.AnchorPoint, Position = CENTER.Position, Clip = true, Parent = slot(parent, order, 176) })
	glowSpot(f, rgb(214, 170, 255), 460, UDim2.fromOffset(95, 92), 0.55)
	for i = 1, 6 do
		sparkle(o.cards, f, 0.1 + i * 0.14, 0.2 + (i % 3) * 0.28, 12 + (i % 3) * 4, i * 1.7, 2)
	end
	local art = holder(f, UDim2.fromOffset(150, 150), UDim2.fromOffset(10, 14), 2)
	glowSpot(art, rgb(255, 210, 90), 190, UDim2.fromScale(0.5, 0.5), 0.3)
	icon(holder(art, UDim2.fromScale(1, 1), UDim2.new(), 2), "spear:" .. st.spear, 0.7)
	bob(o, art, UDim2.fromOffset(10, 14), 4, 0)
	UI.label({ Text = "STARTER PACK!", TextSize = 32, Color = K.white, StrokeColor = K.heroLine, Stroke = 4, Size = UDim2.new(1, -330, 0, 36), Position = UDim2.fromOffset(170, 8), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	UI.label({ Text = "BEST DEAL!", TextSize = 22, Color = K.goldText, StrokeColor = rgb(90, 42, 0), Stroke = 3, Size = UDim2.fromOffset(150, 26), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -14, 0, 12), XAlign = Enum.TextXAlignment.Right, ZIndex = 3, Parent = f })
	local row = holder(f, UDim2.new(1, -182, 0, 68), UDim2.fromOffset(170, 50), 3)
	local lay = UI.list(Enum.FillDirection.Horizontal, 8, Enum.HorizontalAlignment.Left, Enum.VerticalAlignment.Center)
	lay.Parent = row
	local spear = Config.SPEAR_BY_ID[st.spear]
	local tiles = {
		{ "spear:" .. st.spear, spear and spear.name or "Spear", rgb(77, 184, 255) },
		{ "coins1", Num.short(st.coins) .. " Coins", rgb(255, 210, 62) },
		{ "bag", "Bag Level " .. tostring(st.bagLvl), rgb(92, 240, 106) },
		{ st.boost == "fortune" and "fortune20" or "luck30", (Config.BOOSTS[st.boost] and Config.BOOSTS[st.boost].name or "Boost") .. " " .. Num.time(st.dur), rgb(199, 125, 255) },
	}
	for i, t in tiles do
		local tile = box({ Top = K.tile, Bottom = K.tile, Line = t[3], LineThick = 2, Radius = 8, Size = UDim2.new(0.25, -6, 1, 0), LayoutOrder = i, Parent = row })
		tile.BackgroundTransparency = 0.3
		icon(holder(tile, UDim2.fromOffset(52, 52), UDim2.fromOffset(4, 8), 2), t[1], 0)
		UI.label({ Text = t[2], TextSize = 15, Stroke = 2, Wrap = true, Size = UDim2.new(1, -62, 1, -8), Position = UDim2.fromOffset(58, 4), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = tile })
	end
	UI.label({ Text = "One per hunter. Leaves the shop at level " .. tostring(SHOP.STARTER_MAX_LEVEL) .. ".", TextSize = 17, Color = K.white, StrokeColor = K.heroLine, Stroke = 2, Wrap = true, Size = UDim2.new(1, -400, 0, 40), Position = UDim2.fromOffset(170, 128), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	buyButton(item, UDim2.fromOffset(200, 42), UDim2.new(1, -212, 0, 126), 22, f).ZIndex = 4
	table.insert(o.shiny, f)
	introPop(o, f)
end

-- Широкий баннер (Server Luck! в референсе)
local function renderBanner(o: Open, parent: Instance, item: any, order: number)
	local base = TILE[item.key] or rgb(52, 196, 96)
	local top, bot, line = Theme.shades(base)
	local f = box({ Top = top, Bottom = bot, Line = line, Size = CENTER.Size, AnchorPoint = CENTER.AnchorPoint, Position = CENTER.Position, Clip = true, Parent = slot(parent, order, 120) })
	glowSpot(f, rgb(230, 255, 200), 340, UDim2.fromOffset(78, 60), 0.55)
	for i = 1, 5 do
		sparkle(o.cards, f, 0.2 + i * 0.15, 0.2 + (i % 2) * 0.5, 12 + (i % 3) * 3, i * 2.1, 2)
	end
	local art = holder(f, UDim2.fromOffset(100, 100), UDim2.fromOffset(12, 10), 2)
	glowSpot(art, rgb(255, 255, 200), 140, UDim2.fromScale(0.5, 0.5), 0.35)
	icon(art, item.key, 0)
	bob(o, art, UDim2.fromOffset(12, 10), 3, 1)
	UI.label({ Text = string.upper(item.name) .. "!", TextSize = 30, Color = K.white, StrokeColor = line, Stroke = 4, Size = UDim2.new(1, -350, 0, 34), Position = UDim2.fromOffset(124, 10), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	local pitch = PITCH[item.key] or { "", "" }
	UI.label({ Text = pitch[1], TextSize = 25, Color = K.goldText, StrokeColor = line, Stroke = 4, Size = UDim2.new(1, -350, 0, 30), Position = UDim2.fromOffset(124, 46), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	UI.label({ Text = pitch[2], TextSize = 16, Color = K.white, StrokeColor = line, Stroke = 3, Size = UDim2.new(1, -350, 0, 20), Position = UDim2.fromOffset(124, 80), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	o.status[item.key] = UI.label({ Text = "", TextSize = 16, Color = K.goldText, Stroke = 3, StrokeColor = line, Size = UDim2.fromOffset(220, 20), Position = UDim2.fromOffset(124, 100), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	if item.pass and Perks.has(item.key) then
		local owned = box({ Top = rgb(255, 224, 102), Bottom = rgb(245, 163, 0), Line = rgb(74, 38, 0), LineThick = 2, Radius = 8, Size = UDim2.fromOffset(190, 44), AnchorPoint = Vector2.new(0, 0), Position = UDim2.new(1, -204, 0.5, -24), ZIndex = 3, Parent = f })
		UI.label({ Text = "OWNED", TextSize = 22, StrokeColor = rgb(107, 61, 0), Size = UDim2.fromScale(1, 1), Parent = owned })
	else
		buyButton(item, UDim2.fromOffset(190, 44), UDim2.new(1, -204, 0.5, -24), 22, f).ZIndex = 4
	end
	table.insert(o.shiny, f)
	introPop(o, f)
end

-- Вертикальная плитка: пасс, буст или пак монет
local function renderTile(o: Open, parent: Instance, item: any, order: number, kind: string)
	local base = TILE[item.key] or rgb(70, 160, 245)
	local top, bot, line = Theme.shades(base)
	local f = box({ Top = top, Bottom = bot, Line = line, Radius = 12, Size = CENTER.Size, AnchorPoint = CENTER.AnchorPoint, Position = CENTER.Position, Clip = true, Parent = slot(parent, order) })
	gloss(f, 52)
	glowSpot(f, K.white, 170, UDim2.fromScale(0.5, 0.4), 0.6)
	sparkle(o.cards, f, 0.18, 0.4, 14, order * 1.3, 2)
	sparkle(o.cards, f, 0.82, 0.3, 11, order * 2.1 + 1, 2)
	local plate = Instance.new("Frame")
	plate.BorderSizePixel = 0
	plate.BackgroundColor3 = line
	plate.BackgroundTransparency = 0.45
	plate.Size = UDim2.new(1, -10, 0, 26)
	plate.Position = UDim2.fromOffset(5, 5)
	plate.ZIndex = 2
	UI.corner(8).Parent = plate
	plate.Parent = f
	UI.label({ Text = string.upper(item.name), TextSize = 19, Scaled = true, MaxSize = 19, Color = K.white, StrokeColor = line, Size = UDim2.new(1, -16, 0, 24), Position = UDim2.fromOffset(8, 6), ZIndex = 3, Parent = f })
	local art = holder(f, UDim2.fromOffset(112, 92), UDim2.new(0.5, -56, 0, 32), 2)
	icon(art, item.key, 0)
	bob(o, art, UDim2.new(0.5, -56, 0, 32), 3, order * 0.9)
	if kind == "pack" then
		UI.label({ Text = "+" .. Num.short(Config.shopCoins(Backend.data, item.k)) .. " COINS", TextSize = 24, Scaled = true, MaxSize = 24, Color = K.goldText, StrokeColor = line, Stroke = 4, Size = UDim2.new(1, -12, 0, 28), Position = UDim2.fromOffset(6, 128), ZIndex = 3, Parent = f })
		if item.best then
			local rib = box({ Top = rgb(255, 80, 88), Bottom = rgb(204, 22, 36), Line = rgb(84, 6, 22), LineThick = 2, Radius = 6, Size = UDim2.fromOffset(86, 18), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -8, 0, 36), ZIndex = 5, Parent = f })
			UI.label({ Text = "BEST VALUE", TextSize = 12, Stroke = 2, Size = UDim2.fromScale(1, 1), ZIndex = 6, Parent = rib })
		end
	else
		local pitch = PITCH[item.key] or { string.upper(item.name), "" }
		UI.label({ Text = pitch[1], TextSize = 24, Scaled = true, MaxSize = 24, Color = K.goldText, StrokeColor = line, Stroke = 4, Size = UDim2.new(1, -12, 0, 28), Position = UDim2.fromOffset(6, 124), ZIndex = 3, Parent = f })
		UI.label({ Text = pitch[2], TextSize = 14, Scaled = true, MaxSize = 14, Color = K.white, StrokeColor = line, Stroke = 3, Size = UDim2.new(1, -12, 0, 18), Position = UDim2.fromOffset(6, 152), ZIndex = 3, Parent = f })
	end
	if item.pass and Perks.has(item.key) then
		local owned = box({ Top = rgb(255, 224, 102), Bottom = rgb(245, 163, 0), Line = rgb(74, 38, 0), LineThick = 2, Radius = 8, Size = UDim2.new(1, -20, 0, 34), Position = UDim2.fromOffset(10, 172), ZIndex = 3, Parent = f })
		UI.label({ Text = "OWNED", TextSize = 19, StrokeColor = rgb(107, 61, 0), Size = UDim2.fromScale(1, 1), Parent = owned })
	else
		buyButton(item, UDim2.new(1, -20, 0, 34), UDim2.fromOffset(10, 172), 19, f).ZIndex = 4
	end
	if kind == "boost" then
		o.status[item.key] = UI.label({ Text = "", TextSize = 13, Color = K.goldText, Stroke = 2, StrokeColor = line, Size = UDim2.new(1, -12, 0, 16), Position = UDim2.fromOffset(6, 34), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = f })
	end
	table.insert(o.shiny, f)
	introPop(o, f)
end

-- V26: ранг поддержки и ежедневный подарок
local function fmtWait(sec: number): string
	return string.format("%dh %02dm", math.floor(sec / 3600), math.floor((sec % 3600) / 60))
end

local function rankPerks(rk: any): string
	local parts = {}
	if rk.bag > 0 then
		table.insert(parts, "+" .. rk.bag .. " bag slots")
	end
	table.insert(parts, "prices recover x" .. tostring(rk.recover))
	table.insert(parts, "daily gift " .. math.floor(rk.gift * 100) .. "%")
	if rk.insight then
		table.insert(parts, "free Market Insight")
	end
	return table.concat(parts, " · ")
end

local function renderRank(o: Open, parent: Instance, order: number)
	local R = SHOP.RANKS
	local st = Perks.state()
	local rank = Perks.rank()
	local spent = tonumber(st.spent) or 0
	local cur = R[rank]
	local nxt = R[rank + 1]
	local f = box({ Top = K.heroTop, Mid = K.heroMid, Bottom = K.heroBot, Line = K.heroLine, Size = CENTER.Size, AnchorPoint = CENTER.AnchorPoint, Position = CENTER.Position, Clip = true, Parent = slot(parent, order, 150) })
	glowSpot(f, rgb(214, 170, 255), 380, UDim2.fromOffset(80, 70), 0.6)
	UI.label({ Text = cur and (string.upper(cur.name) .. " SUPPORTER") or "SUPPORTER RANK", TextSize = 28, Color = cur and cur.color or K.white, StrokeColor = K.heroLine, Stroke = 4, Size = UDim2.new(1, -250, 0, 32), Position = UDim2.fromOffset(14, 8), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	UI.label({ Text = cur and rankPerks(cur) or "Spend Robux to earn a rank: a tag and aura everyone sees, a daily gift and perks.", TextSize = 15, Color = K.white, StrokeColor = K.heroLine, Stroke = 2, Wrap = true, Size = UDim2.new(1, -250, 0, 40), Position = UDim2.fromOffset(14, 44), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	local from = cur and cur.at or 0
	local frac = nxt and math.clamp((spent - from) / math.max(1, nxt.at - from), 0, 1) or 1
	local bar = Instance.new("Frame")
	bar.BorderSizePixel = 0
	bar.BackgroundColor3 = K.heroLine
	bar.Size = UDim2.new(1, -250, 0, 16)
	bar.Position = UDim2.fromOffset(14, 94)
	bar.ZIndex = 3
	UI.corner(8).Parent = bar
	bar.Parent = f
	local fill = Instance.new("Frame")
	fill.BorderSizePixel = 0
	fill.BackgroundColor3 = nxt and nxt.color or K.goldText
	fill.Size = UDim2.fromScale(frac, 1)
	fill.ZIndex = 4
	UI.corner(8).Parent = fill
	fill.Parent = bar
	UI.label({ Text = nxt and string.format("%d / %d R$ to %s: %s", spent, nxt.at, nxt.name, rankPerks(nxt)) or "Top rank reached. Thank you for supporting the game!", TextSize = 14, Color = K.white, StrokeColor = K.heroLine, Stroke = 2, Wrap = true, Size = UDim2.new(1, -250, 0, 34), Position = UDim2.fromOffset(14, 114), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	local left = Perks.giftLeft()
	local ready = left <= 0
	local k = (cur and cur.gift or SHOP.GIFT_BASE) + (Perks.has("founder") and 0.05 or 0)
	UI.label({ Text = "DAILY GIFT", TextSize = 22, Color = K.goldText, StrokeColor = K.heroLine, Stroke = 3, Size = UDim2.fromOffset(200, 26), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -14, 0, 14), XAlign = Enum.TextXAlignment.Right, ZIndex = 3, Parent = f })
	UI.label({ Text = "+" .. Num.short(Config.shopCoins(Backend.data, k)) .. " coins", TextSize = 18, Color = K.white, StrokeColor = K.heroLine, Stroke = 2, Size = UDim2.fromOffset(200, 22), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -14, 0, 42), XAlign = Enum.TextXAlignment.Right, ZIndex = 3, Parent = f })
	local btn = UI.button({ Text = ready and "CLAIM" or fmtWait(left), TextSize = 22, Color = ready and K.green or rgb(96, 96, 120), Size = UDim2.fromOffset(190, 44), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -14, 0, 74), Sound = "press" }, function()
		local fn = ShopFn
		if ready and fn then
			task.spawn(function()
				pcall(function()
					fn:InvokeServer("claimGift")
				end)
			end)
		end
	end)
	btn.ZIndex = 4
	btn.Parent = f
	table.insert(o.shiny, f)
	introPop(o, f)
end

local function renderBody(o: Open)
	local scroll = o.scroll
	for _, c in scroll:GetChildren() do
		if c:IsA("GuiObject") then
			c:Destroy()
		end
	end
	table.clear(o.status)
	table.clear(o.cards)
	table.clear(o.shiny)
	o.n = 0
	local order = 0
	local function nextOrder(): number
		order += 1
		return order
	end
	if starterVisible() then
		renderHero(o, scroll, nextOrder())
	end
	renderRank(o, scroll, nextOrder())
	sectionBar(o, scroll, "Game Passes", nextOrder())
	local passes = grid(scroll, 3, 212, nextOrder())
	local n = 0
	for _, it in SHOP.PASSES do
		if it.key ~= "founder" then
			n += 1
			renderTile(o, passes, it, n, "pass")
		end
	end
	local founder = Config.SHOP_BY_KEY.founder
	if founder then
		renderBanner(o, scroll, founder, nextOrder())
	end
	sectionBar(o, scroll, "Boosts", nextOrder())
	local server: any = nil
	local bundle: any = nil
	local brews: { any } = {}
	local packs: { any } = {}
	for _, it in SHOP.PRODUCTS do
		if it.kind == "server" then
			server = it
		elseif it.kind == "boost" and it.key == "hour_bundle" then
			bundle = it
		elseif it.kind == "boost" then
			table.insert(brews, it)
		elseif it.kind == "coins" then
			table.insert(packs, it)
		end
	end
	if server then
		renderBanner(o, scroll, server, nextOrder())
	end
	if bundle then
		renderBanner(o, scroll, bundle, nextOrder())
	end
	local boosts = grid(scroll, 3, 212, nextOrder())
	for i, it in brews do
		renderTile(o, boosts, it, i, "boost")
	end
	sectionBar(o, scroll, "Coins", nextOrder())
	local coins = grid(scroll, 4, 212, nextOrder())
	for i, it in packs do
		renderTile(o, coins, it, i, "pack")
	end
	local note = UI.label({ Text = "Coin packs grow with the price of your next spear. Boost timers run only while you play.", TextSize = 14, Color = K.white, Stroke = 2, StrokeColor = K.navy, Wrap = true, Size = UDim2.new(1, 0, 0, 36), LayoutOrder = nextOrder(), Parent = scroll })
	note.TextTransparency = 0.05
end

local function refreshLive(o: Open)
	local d = Backend.data
	o.pill.Text = d and Num.short(d.coins) or "0"
	for key, label in o.status do
		local item = Config.SHOP_BY_KEY[key]
		local left = item and boostLeftFor(item) or 0
		label.Text = left > 0 and ("ACTIVE " .. Num.time(left)) or ""
	end
end

function Shop.refresh()
	local o = open
	if o and o.win.Parent and not o.closing and UI.windowOpen("shop") then
		local pos = o.scroll.CanvasPosition
		renderBody(o)
		refreshLive(o)
		o.scroll.CanvasPosition = pos
	end
end

function Shop.open()
	local win, body = UI.window("shop", "", Vector2.new(780, 612), K.skyBot, function()
		open = nil
	end)
	-- Убираем стандартное оформление окна: вместо него небо, баннер и облака
	for _, c in win:GetChildren() do
		if c.Name == "Header" or c.Name == "Button" or c:IsA("UIStroke") or c:IsA("UIGradient") then
			c:Destroy()
		end
	end
	win.BackgroundTransparency = 1
	local winScale = win:FindFirstChildOfClass("UIScale")
	if winScale then
		UI.tween(winScale, 0.01, { Scale = 1 }) -- гасим стандартный «поп», у магазина своё появление
	end
	body.Position = UDim2.fromOffset(6, 6)
	body.Size = UDim2.new(1, -12, 1, -12)

	-- Небо с дрейфующими облаками; раскатывается вниз при открытии
	local sky = box({ Top = K.skyTop, Mid = K.skyMid, Bottom = K.skyBot, Line = K.frame, LineThick = 4, Radius = 16, Size = UDim2.new(1, 0, 0, 0), Position = UDim2.fromOffset(0, 58), ZIndex = 1, Clip = true, Parent = body })
	local scroll = UI.scroll(sky, UDim2.fromScale(1, 1), UDim2.new())
	scroll.ScrollBarImageColor3 = K.white
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, 14)
	pad.PaddingRight = UDim.new(0, 18)
	pad.PaddingTop = UDim.new(0, 22)
	pad.PaddingBottom = UDim.new(0, 16)
	pad.Parent = scroll
	UI.list(Enum.FillDirection.Vertical, 12).Parent = scroll

	-- Шапка: баннер, облака, корзинка, монеты, кнопка закрытия
	local head = Instance.new("Frame")
	head.Name = "Head"
	head.BackgroundTransparency = 1
	head.AnchorPoint = Vector2.new(0.5, 0.5)
	head.Position = UDim2.new(0.5, 0, 0, HEAD_H / 2)
	head.Size = UDim2.new(1, 0, 0, HEAD_H)
	head.ZIndex = 4
	local headScale = Instance.new("UIScale")
	headScale.Parent = head
	head.Parent = body

	local mask = Instance.new("Frame")
	mask.Name = "Mask"
	mask.BackgroundTransparency = 1
	mask.ClipsDescendants = true
	mask.Size = UDim2.fromOffset(0, HEAD_H)
	mask.ZIndex = 1
	mask.Parent = head
	local ribbon = box({ Top = K.headTop, Bottom = K.headBot, Line = K.frame, LineThick = 4, Radius = 14, Size = UDim2.fromOffset(BW - 8, HEAD_H - 8), Position = UDim2.fromOffset(4, 4), ZIndex = 1, Clip = true, Parent = mask })
	local shine = Instance.new("Frame")
	shine.BorderSizePixel = 0
	shine.BackgroundColor3 = K.white
	shine.BackgroundTransparency = 0.78
	shine.Size = UDim2.new(1, -16, 0, 9)
	shine.Position = UDim2.fromOffset(8, 4)
	shine.ZIndex = 2
	UI.corner(5).Parent = shine
	shine.Parent = ribbon

	local o: Open = {
		win = win, scroll = scroll, pill = nil :: any, status = {}, sky = sky, headScale = headScale, headGroup = head,
		anim = {}, cards = {}, shiny = {}, intro = true, closing = false, n = 0,
	}

	-- Узор шапки: треугольники-«самолётики» медленно плывут влево
	for row = 1, 2 do
		for i = 1, 11 do
			local tri = Instance.new("ImageLabel")
			tri.BackgroundTransparency = 1
			tri.Image = UI.IMG.triangle
			tri.ImageColor3 = K.headPat
			tri.ImageTransparency = 0.8
			tri.Size = UDim2.fromOffset(18, 18)
			tri.ZIndex = 2
			tri.Parent = ribbon
			local y = row == 1 and 12 or 34
			reg(o.anim, tri, function(t)
				tri.Position = UDim2.fromOffset((i * 70 + row * 35 - t * 16) % 770 - 20, y)
			end)
		end
	end

	UI.label({ Text = "Shop", TextSize = 42, Color = K.white, StrokeColor = K.titleLine, Stroke = 4, Size = UDim2.fromOffset(200, HEAD_H), Position = UDim2.fromOffset(88, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = ribbon })
	local pillBox = box({ Top = rgb(12, 52, 130), Bottom = rgb(20, 78, 170), Line = K.frame, LineThick = 2, Radius = 9, Size = UDim2.fromOffset(170, 38), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -66, 0.5, 0), ZIndex = 3, Parent = ribbon })
	local coin = box({ Top = rgb(255, 233, 138), Bottom = rgb(240, 168, 0), Line = rgb(107, 61, 0), LineThick = 2, Radius = 13, Size = UDim2.fromOffset(26, 26), AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.new(0, 8, 0.5, 0), ZIndex = 4, Parent = pillBox })
	UI.label({ Text = "$", TextSize = 17, Stroke = 2, StrokeColor = rgb(107, 61, 0), Size = UDim2.fromScale(1, 1), ZIndex = 5, Parent = coin })
	o.pill = UI.label({ Text = "0", TextSize = 22, Stroke = 2, StrokeColor = K.frame, Size = UDim2.new(1, -46, 1, 0), Position = UDim2.fromOffset(40, 0), ZIndex = 4, Parent = pillBox })

	-- Зверьки выглядывают из-за баннера (стоят позади него, видны только головы и уши)
	local peekers = {}
	for _, p in { { "squirrel", 270 }, { "moonrabbit", BW - 128 } } do
		local a = animalView(head, p[1], -18, 96, 96)
		a.AnchorPoint = Vector2.new(0.5, 1)
		a.Position = UDim2.fromOffset(p[2] + 48, 32)
		a.ZIndex = 0
		table.insert(peekers, a)
		local base = a.Position
		reg(o.anim, a, function(t)
			a.Position = UDim2.fromOffset(base.X.Offset, base.Y.Offset + math.sin(t * 1.8 + p[2]) * 3)
		end)
	end
	-- Корзинка на круглой плашке слева сверху: ничем не перекрыта
	local badgeRim = box({ Top = K.frame, Bottom = K.frame, Radius = 34, Size = UDim2.fromOffset(68, 68), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(38, 33), ZIndex = 5, Parent = head })
	local badge = box({ Top = rgb(130, 236, 255), Bottom = rgb(30, 140, 240), Line = K.white, LineThick = 3, Radius = 30, Size = UDim2.fromOffset(60, 60), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), ZIndex = 1, Parent = badgeRim })
	local basket = basketIcon(badge, 3)
	basket.AnchorPoint = Vector2.new(0.5, 0.5)
	basket.Position = UDim2.fromScale(0.5, 0.52)
	-- Кнопка закрытия лежит в обёртке: у самой кнопки уже есть свой UIScale (наведение), второй на неё не вешаем
	local closeHold = holder(head, UDim2.fromOffset(40, 40), UDim2.fromOffset(BW - 34, 26), 5)
	closeHold.AnchorPoint = Vector2.new(0.5, 0.5)
	local close = UI.button({ Text = "X", TextSize = 24, Color = K.red, Size = UDim2.fromScale(1, 1), ZIndex = 5, Sound = "press", Burst = false }, function()
		closeAnimated(o)
	end)
	close.Parent = closeHold
	reg(o.anim, basket, function(t)
		basket.Rotation = -8 + math.sin(t * 2) * 4
	end)

	buildMeadow(o, sky)

	open = o
	renderBody(o)
	refreshLive(o)
	playIntro(o, body, mask, ribbon, { { badgeRim, 0.5 }, { peekers[1], 0.62 }, { peekers[2], 0.68 }, { closeHold, 0.75 } })

	-- Единый цикл анимации; живёт, пока окно открыто
	local conn: RBXScriptConnection? = nil
	local nextShine = os.clock() + 1.6
	local nextLive = 0
	conn = RunService.RenderStepped:Connect(function()
		if open ~= o or not win.Parent then
			if conn then
				conn:Disconnect()
			end
			return
		end
		local t = os.clock()
		for _, a in o.anim do
			if a.inst.Parent then
				a.fn(t)
			end
		end
		for _, a in o.cards do
			if a.inst.Parent then
				a.fn(t)
			end
		end
		if t > nextShine and #o.shiny > 0 and not o.closing then
			nextShine = t + 0.8 + math.random() * 0.9
			local g = o.shiny[math.random(1, #o.shiny)]
			if g.Parent then
				UI.shine(g, 0.7)
			end
		end
		if t > nextLive then
			nextLive = t + 0.7
			refreshLive(o)
		end
	end)
end

---------------------------------------------------------------------
-- Сохранение и выдача покупок в экономику
---------------------------------------------------------------------
local canSave = false
local dirty = false
local saving = false
local applied: { [string]: boolean } = {}
local ackQueue: { string } = {}

local function saveNow(): boolean
	local fn = ShopFn
	if not canSave or not fn or saving or not Backend.data then
		return false
	end
	saving = true
	local acks = table.clone(ackQueue)
	local wasDirty = dirty
	dirty = false
	local ok, res = pcall(function()
		return fn:InvokeServer("save", Backend.data, acks)
	end)
	saving = false
	if ok and res == true then
		for _, id in acks do
			local i = table.find(ackQueue, id)
			if i then
				table.remove(ackQueue, i)
			end
		end
		return true
	end
	dirty = dirty or wasDirty
	return false
end

local function processPending(pending: any)
	if not canSave or type(pending) ~= "table" then
		return
	end
	local got = false
	for _, g in pending do
		if type(g) == "table" and type(g.id) == "string" and not applied[g.id] then
			applied[g.id] = true
			local ok, coins = Backend.call("ShopGrant", g)
			if ok then
				got = true
				table.insert(ackQueue, g.id)
				local n = tonumber(coins) or 0
				if n > 0 then
					local cam = workspace.CurrentCamera
					Sfx.play("buy")
					Hud.flyCoins(Vector2.new(cam.ViewportSize.X / 2, cam.ViewportSize.Y * 0.45), n)
				end
			end
		end
	end
	if got then
		task.spawn(function()
			for _ = 1, 5 do
				if saveNow() then
					break
				end
				task.wait(1.5)
			end
		end)
	end
end

local function onEvent(kind: any, payload: any)
	if kind == "state" then
		Perks.set(payload)
		processPending(Perks.state().pending)
	elseif kind == "granted" then
		local item = Config.SHOP_BY_KEY[payload]
		if not item then
			return
		end
		if item.pass then
			unlock(item, "UNLOCKED!")
		elseif item.kind == "starter" then
			unlock(item, "OPENED!")
		elseif item.kind == "coins" then
			UI.toast(item.name .. " delivered", "gold", 3)
		else
			Sfx.play("sparkle")
			UI.flash(ACCENT[item.key] or K.goldText, 0.35, 0.5)
			Hud.banner(string.upper(item.name), ACCENT[item.key] or K.goldText, "+" .. Num.time(item.dur), 2)
		end
	elseif kind == "announce" then
		Sfx.play("ping", 1.2, 0.6)
		UI.toast(tostring(payload), "rare", 5)
	end
end

function Shop.init()
	ShopEv = Net.ev("Shop")
	ShopFn = Net.fn("ShopRequest")
	local ev = ShopEv :: RemoteEvent
	local fn = ShopFn :: RemoteFunction
	ev.OnClientEvent:Connect(onEvent)

	Perks.Changed.Event:Connect(function()
		Backend.applyPerks()
		Shop.refresh()
	end)
	Backend.onChange(function()
		dirty = true
	end)

	task.spawn(function()
		local ok, good, save, state = pcall(function()
			return fn:InvokeServer("load")
		end)
		if ok and good == true then
			if type(save) == "table" then
				Backend.load(save)
			end
			canSave = true
			dirty = false
			if type(state) == "table" then
				Perks.set(state)
			end
			processPending(Perks.state().pending)
		else
			UI.toast("Could not load your save. Progress will not be saved this session - please rejoin.", "warn", 8)
		end
	end)

	task.spawn(function()
		while true do
			task.wait(20)
			if dirty or #ackQueue > 0 then
				saveNow()
			end
		end
	end)

	-- [VIP] перед именем в чате
	pcall(function()
		TextChatService.OnIncomingMessage = function(message: TextChatMessage)
			local props = Instance.new("TextChatMessageProperties")
			local src = message.TextSource
			if src then
				local p = Players:GetPlayerByUserId(src.UserId)
				if p and p:GetAttribute("VIP") then
					props.PrefixText = "<font color='#FFD23E'>[VIP]</font> " .. message.PrefixText
				end
			end
			return props
		end
	end)
end

return Shop
