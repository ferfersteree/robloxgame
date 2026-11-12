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
	skyTop = rgb(132, 214, 255), skyMid = rgb(74, 166, 248), skyBot = rgb(38, 108, 218),
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
	charm = rgb(120, 255, 150), purse = rgb(255, 196, 70), wrap = rgb(255, 126, 190), bag = rgb(255, 157, 67),
	titan = rgb(255, 106, 122), vip = rgb(255, 216, 74),
	luck30 = rgb(110, 240, 130), coins30 = rgb(255, 200, 60), brew30 = rgb(80, 224, 213), server15 = rgb(110, 190, 255),
}
-- Основной цвет плитки товара (как зелёный x2 Cash, оранжевый VIP, синий Egg Growth в референсе)
local TILE = {
	charm = rgb(92, 214, 56), purse = rgb(255, 150, 24), wrap = rgb(236, 82, 170), bag = rgb(24, 188, 196),
	titan = rgb(236, 64, 72), vip = rgb(255, 170, 20),
	luck30 = rgb(84, 204, 70), coins30 = rgb(255, 172, 20), brew30 = rgb(56, 148, 255), server15 = rgb(52, 196, 96),
	coins1 = rgb(132, 214, 36), coins2 = rgb(132, 214, 36), coins3 = rgb(40, 190, 140), coins4 = rgb(80, 130, 255),
}

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

-- Ставит иконку товара в parent. Копья и звери берутся из самой игры.
local function icon(parent: Instance, kind: string, spin: number?)
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

-- Облачко из кругов с голубой обводкой
local function cloudShape(parent: Instance, w: number, z: number): Frame
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromOffset(w, w * 0.58)
	f.ZIndex = z
	local function blob(xf: number, yf: number, wf: number, hf: number, col: Color3, grow: number, zz: number)
		local c = Instance.new("Frame")
		c.BorderSizePixel = 0
		c.BackgroundColor3 = col
		c.Size = UDim2.fromOffset(wf * w + grow * 2, hf * w + grow * 2)
		c.Position = UDim2.fromOffset(xf * w - grow, yf * w - grow)
		c.ZIndex = zz
		UI.corner(0.5, true).Parent = c
		c.Parent = f
	end
	local specs = { { 0.02, 0.3, 0.36 }, { 0.17, 0.08, 0.46 }, { 0.44, 0.0, 0.52 }, { 0.66, 0.24, 0.34 } }
	for pass = 1, 2 do
		local col = pass == 1 and K.cloudEdge or K.cloud
		local grow = pass == 1 and 3 or 0
		for _, s in specs do
			blob(s[1], s[2], s[3], s[3], col, grow, z + pass - 1)
		end
		blob(0.05, 0.3, 0.88, 0.26, col, grow, z + pass - 1)
	end
	f.Parent = parent
	return f
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

-- Истребитель с языком пламени и тросом для баннера
local function jet(parent: Instance, o: Open): Frame
	local j = Instance.new("Frame")
	j.Name = "Jet"
	j.BackgroundTransparency = 1
	j.Size = UDim2.fromOffset(128, 44)
	j.AnchorPoint = Vector2.new(0, 0.5)
	j.ZIndex = 20
	local rope = Instance.new("Frame")
	rope.BorderSizePixel = 0
	rope.BackgroundColor3 = K.white
	rope.Size = UDim2.fromOffset(34, 3)
	rope.Position = UDim2.fromOffset(-30, 20)
	rope.ZIndex = 20
	rope.Parent = j
	local flame = Instance.new("Frame")
	flame.BorderSizePixel = 0
	flame.BackgroundColor3 = rgb(255, 170, 40)
	flame.Size = UDim2.fromOffset(34, 9)
	flame.Position = UDim2.fromOffset(2, 18)
	flame.ZIndex = 20
	UI.corner(0.5, true).Parent = flame
	local fg = Instance.new("UIGradient")
	fg.Color = ColorSequence.new(rgb(255, 244, 170), rgb(255, 120, 30))
	fg.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.5, 0.15), NumberSequenceKeypoint.new(1, 0) })
	fg.Parent = flame
	flame.Parent = j
	local function piece(size: Vector2, pos: Vector2, rot: number, top: Color3, bot: Color3, z: number, round: boolean): Frame
		local p = box({ Top = top, Bottom = bot, Line = rgb(44, 66, 104), LineThick = 2, Radius = round and 20 or 3, Size = UDim2.fromOffset(size.X, size.Y), Position = UDim2.fromOffset(pos.X, pos.Y), Rotation = rot, ZIndex = z, Parent = j })
		return p
	end
	piece(Vector2.new(18, 22), Vector2.new(28, 2), -22, rgb(150, 178, 214), rgb(98, 124, 168), 20, false) -- хвост
	piece(Vector2.new(46, 10), Vector2.new(44, 24), 24, rgb(150, 178, 214), rgb(98, 124, 168), 20, false) -- дальнее крыло
	piece(Vector2.new(92, 17), Vector2.new(30, 14), 0, rgb(246, 250, 255), rgb(150, 176, 210), 21, true) -- фюзеляж
	piece(Vector2.new(20, 8), Vector2.new(84, 16), 0, rgb(40, 96, 190), rgb(14, 40, 110), 22, true) -- кабина
	piece(Vector2.new(48, 11), Vector2.new(50, 22), 28, rgb(226, 238, 252), rgb(120, 148, 190), 22, false) -- ближнее крыло
	reg(o.anim, flame, function(t)
		flame.Size = UDim2.fromOffset(28 + math.sin(t * 60) * 7, 8 + math.sin(t * 47) * 2)
	end)
	j.Parent = parent
	return j
end

-- Анимация открытия: самолёт тянет баннер «Shop», потом разворачивается небо и выпрыгивают плитки
local function playIntro(o: Open, body: Frame, mask: Frame, ribbon: Frame, popTargets: { { any } })
	local function alive(): boolean
		return open == o and body.Parent ~= nil
	end
	local j = jet(body, o)
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
		{ "luck30", "Luck x2 " .. Num.time(st.dur), rgb(199, 125, 255) },
	}
	for i, t in tiles do
		local tile = box({ Top = K.tile, Bottom = K.tile, Line = t[3], LineThick = 2, Radius = 8, Size = UDim2.new(0.25, -6, 1, 0), LayoutOrder = i, Parent = row })
		tile.BackgroundTransparency = 0.3
		icon(holder(tile, UDim2.fromOffset(52, 52), UDim2.fromOffset(4, 8), 2), t[1], 0)
		UI.label({ Text = t[2], TextSize = 15, Stroke = 2, Wrap = true, Size = UDim2.new(1, -62, 1, -8), Position = UDim2.fromOffset(58, 4), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = tile })
	end
	UI.label({ Text = "One per hunter. Leaves the shop at level " .. tostring(SHOP.STARTER_MAX_LEVEL) .. ".", TextSize = 15, Color = K.white, StrokeColor = K.heroLine, Stroke = 2, Wrap = true, Size = UDim2.new(1, -400, 0, 40), Position = UDim2.fromOffset(170, 128), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
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
	UI.label({ Text = item.desc or "", TextSize = 15, Stroke = 2, StrokeColor = line, Wrap = true, Size = UDim2.new(1, -350, 0, 40), Position = UDim2.fromOffset(124, 46), XAlign = Enum.TextXAlignment.Left, YAlign = Enum.TextYAlignment.Top, ZIndex = 3, Parent = f })
	o.status[item.key] = UI.label({ Text = "", TextSize = 16, Color = K.goldText, Stroke = 2, StrokeColor = line, Size = UDim2.fromOffset(220, 22), Position = UDim2.fromOffset(124, 90), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = f })
	buyButton(item, UDim2.fromOffset(190, 44), UDim2.new(1, -204, 0.5, -24), 22, f).ZIndex = 4
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
	local art = holder(f, UDim2.fromOffset(96, 90), UDim2.new(0.5, -48, 0, 34), 2)
	icon(art, item.key, 0)
	bob(o, art, UDim2.new(0.5, -48, 0, 34), 3, order * 0.9)
	if kind == "pack" then
		UI.label({ Text = "+" .. Num.short(Config.shopCoins(Backend.data, item.k)) .. " Coins", TextSize = 22, Color = K.goldText, StrokeColor = line, Stroke = 3, Size = UDim2.new(1, -14, 0, 28), Position = UDim2.fromOffset(7, 126), ZIndex = 3, Parent = f })
		if item.best then
			local rib = box({ Top = rgb(255, 80, 88), Bottom = rgb(204, 22, 36), Line = rgb(84, 6, 22), LineThick = 2, Radius = 6, Size = UDim2.fromOffset(86, 18), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -8, 0, 36), ZIndex = 5, Parent = f })
			UI.label({ Text = "BEST VALUE", TextSize = 12, Stroke = 2, Size = UDim2.fromScale(1, 1), ZIndex = 6, Parent = rib })
		end
	else
		UI.label({ Text = item.desc or "", TextSize = 13, Stroke = 2, StrokeColor = line, Wrap = true, Size = UDim2.new(1, -14, 0, 30), Position = UDim2.fromOffset(7, 126), YAlign = Enum.TextYAlignment.Top, ZIndex = 3, Parent = f })
	end
	if item.pass and Perks.has(item.key) then
		local owned = box({ Top = rgb(255, 224, 102), Bottom = rgb(245, 163, 0), Line = rgb(74, 38, 0), LineThick = 2, Radius = 8, Size = UDim2.new(1, -20, 0, 34), Position = UDim2.fromOffset(10, 160), ZIndex = 3, Parent = f })
		UI.label({ Text = "OWNED", TextSize = 19, StrokeColor = rgb(107, 61, 0), Size = UDim2.fromScale(1, 1), Parent = owned })
	else
		buyButton(item, UDim2.new(1, -20, 0, 34), UDim2.fromOffset(10, 158), 19, f).ZIndex = 4
	end
	if kind == "boost" then
		o.status[item.key] = UI.label({ Text = "", TextSize = 13, Color = K.goldText, Stroke = 2, StrokeColor = line, Size = UDim2.new(1, -12, 0, 16), Position = UDim2.fromOffset(6, 34), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = f })
	end
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
	sectionBar(o, scroll, "Game Passes", nextOrder())
	local passes = grid(scroll, 3, 200, nextOrder())
	for i, it in SHOP.PASSES do
		renderTile(o, passes, it, i, "pass")
	end
	sectionBar(o, scroll, "Boosts", nextOrder())
	local server: any = nil
	local brews: { any } = {}
	local packs: { any } = {}
	for _, it in SHOP.PRODUCTS do
		if it.kind == "server" then
			server = it
		elseif it.kind == "boost" then
			table.insert(brews, it)
		elseif it.kind == "coins" then
			table.insert(packs, it)
		end
	end
	if server then
		renderBanner(o, scroll, server, nextOrder())
	end
	local boosts = grid(scroll, 3, 200, nextOrder())
	for i, it in brews do
		renderTile(o, boosts, it, i, "boost")
	end
	sectionBar(o, scroll, "Coins", nextOrder())
	local coins = grid(scroll, 4, 200, nextOrder())
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

	UI.label({ Text = "Shop", TextSize = 42, Color = K.white, StrokeColor = K.titleLine, Stroke = 4, Size = UDim2.fromOffset(200, HEAD_H), Position = UDim2.fromOffset(78, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 3, Parent = ribbon })
	local pillBox = box({ Top = rgb(12, 52, 130), Bottom = rgb(20, 78, 170), Line = K.frame, LineThick = 2, Radius = 9, Size = UDim2.fromOffset(170, 38), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -66, 0.5, 0), ZIndex = 3, Parent = ribbon })
	local coin = box({ Top = rgb(255, 233, 138), Bottom = rgb(240, 168, 0), Line = rgb(107, 61, 0), LineThick = 2, Radius = 13, Size = UDim2.fromOffset(26, 26), AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.new(0, 8, 0.5, 0), ZIndex = 4, Parent = pillBox })
	UI.label({ Text = "$", TextSize = 17, Stroke = 2, StrokeColor = rgb(107, 61, 0), Size = UDim2.fromScale(1, 1), ZIndex = 5, Parent = coin })
	o.pill = UI.label({ Text = "0", TextSize = 22, Stroke = 2, StrokeColor = K.frame, Size = UDim2.new(1, -46, 1, 0), Position = UDim2.fromOffset(40, 0), ZIndex = 4, Parent = pillBox })

	local cloudL = holder(head, UDim2.fromOffset(100, 58), UDim2.fromOffset(20, 15), 2)
	cloudL.AnchorPoint = Vector2.new(0.5, 0.5)
	cloudShape(cloudL, 100, 2)
	local cloudR = holder(head, UDim2.fromOffset(100, 58), UDim2.fromOffset(BW - 24, 15), 2)
	cloudR.AnchorPoint = Vector2.new(0.5, 0.5)
	cloudShape(cloudR, 100, 2)
	local basket = basketIcon(head, 4)
	basket.AnchorPoint = Vector2.new(0.5, 0.5)
	basket.Position = UDim2.fromOffset(40, 31)
	-- Кнопка закрытия лежит в обёртке: у самой кнопки уже есть свой UIScale (наведение), второй на неё не вешаем
	local closeHold = holder(head, UDim2.fromOffset(40, 40), UDim2.fromOffset(BW - 34, 26), 5)
	closeHold.AnchorPoint = Vector2.new(0.5, 0.5)
	local close = UI.button({ Text = "X", TextSize = 24, Color = K.red, Size = UDim2.fromScale(1, 1), ZIndex = 5, Sound = "press", Burst = false }, function()
		closeAnimated(o)
	end)
	close.Parent = closeHold
	reg(o.anim, cloudL, function(t)
		cloudL.Position = UDim2.fromOffset(20, 15 + math.sin(t * 1.3) * 2.5)
	end)
	reg(o.anim, cloudR, function(t)
		cloudR.Position = UDim2.fromOffset(BW - 24, 15 + math.sin(t * 1.3 + 2) * 2.5)
	end)
	reg(o.anim, basket, function(t)
		basket.Rotation = -8 + math.sin(t * 2) * 4
	end)

	-- Облака дрейфуют по небу, искорки мерцают
	local drift = { { 120, 0.5, 0.78 }, { 300, 0.35, 0.88 }, { 150, 0.7, 0.68 }, { 220, 0.45, 0.93 }, { 100, 0.6, 0.55 } }
	for i, d in drift do
		local c = cloudShape(sky, d[1], 1)
		local span = BW + d[1] + 80
		local off = i * 173
		reg(o.anim, c, function(t)
			c.Position = UDim2.fromOffset((off + t * (6 + i * 2.5)) % span - d[1] - 40, 20 + (i - 1) * 86)
		end)
	end
	for i = 1, 9 do
		sparkle(o.anim, sky, (i * 0.137) % 1, 0.1 + ((i * 0.31) % 0.8), 10 + (i % 3) * 4, i * 1.9, 1)
	end

	open = o
	renderBody(o)
	refreshLive(o)
	playIntro(o, body, mask, ribbon, { { cloudL, 0.55 }, { cloudR, 0.6 }, { basket, 0.68 }, { closeHold, 0.75 } })

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
