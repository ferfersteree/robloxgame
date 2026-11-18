-- StarterPlayerScripts/Client/Menus.luau
-- Окна: Сумка, Копья (магазин/выбор), Кузница, Рынок, Коллекция, Задания, Зелья, Настройки, Демо.
-- Все действия — через Backend.call; после ответа окно перерисовывается на месте.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local Roll = require(RS.Shared.Roll)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Card = require(script.Parent.Card)
local Prompts = require(script.Parent.Prompts)
local Perks = require(script.Parent.Perks)
local SpearFactoryV15 = require(RS:WaitForChild("V15SpearPresentation"):WaitForChild("SpearFactoryV15"))

local Menus = {}
local C = Theme.C
local player = Players.LocalPlayer
local map = workspace:WaitForChild("Map")

type Win = { id: string, body: Frame, render: (Frame, any) -> (), state: { [string]: any } }
local cur: Win? = nil

local function clear(body: Frame)
	for _, c in body:GetChildren() do
		c:Destroy()
	end
end

local function show(id: string, title: string, size: Vector2, color: Color3, render: (Frame, any) -> (), state: { [string]: any }?)
	local w: Win? = nil
	local _, body = UI.window(id, title, size, color, function()
		if cur == w then
			cur = nil
		end
	end)
	w = { id = id, body = body, render = render, state = state or {} }
	cur = w
	render(body, (w :: Win).state)
end

function Menus.refresh()
	local w = cur
	if w and UI.windowOpen(w.id) then
		clear(w.body)
		w.render(w.body, w.state)
	end
end

local function call(action: string, ...: any): (boolean, ...any)
	local r = table.pack(Backend.call(action, ...))
	if not r[1] then
		if r[2] then
			UI.toast(tostring(r[2]), "bad")
		end
		Sfx.play("error")
	end
	return table.unpack(r, 1, r.n)
end

local function nearPrompt(action: string, radius: number): boolean
	local c = player.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hrp then
		return false
	end
	local actionId = Prompts.idFor(action) or action
	for _, d in map:GetDescendants() do
		if d:IsA("ProximityPrompt") and Prompts.actionId(d) == actionId then
			local p = d.Parent :: BasePart
			if p:IsA("BasePart") and (p.Position - hrp.Position).Magnitude < radius then
				return true
			end
		end
	end
	return false
end
Menus.nearPrompt = nearPrompt

local function row(parent: Instance, h: number, order: number?): Frame
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = UDim2.new(1, 0, 0, h)
	f.LayoutOrder = order or 0
	f.Parent = parent
	return f
end

local function txt(parent: Instance, text: string, size: number, color: Color3?, props: { [string]: any }?): TextLabel
	local p: { [string]: any } = { Text = text, TextSize = size, Color = color or C.text, Size = UDim2.new(1, 0, 0, size + 8), XAlign = Enum.TextXAlignment.Left, Parent = parent, Rich = true }
	if props then
		for k, v in props do
			p[k] = v
		end
	end
	return UI.label(p)
end

-- Копьё во вьюпорте (наискосок)
local function spearView(id: string, parent: Instance, spin: number?): ViewportFrame?
	local s = SpearFactoryV15.Create(id)
	if not s then
		local template = RS.Assets.Spears:FindFirstChild(id)
		if not template or not template:IsA("Model") then return nil end
		s = template:Clone()
	end
	local holder = Instance.new("Model")
	holder.WorldPivot = CFrame.new()
	s:PivotTo(CFrame.Angles(0, 0, math.rad(-42)))
	s.Parent = holder
	local vp = UI.viewport(holder, nil, math.rad(20), spin or 0.6)
	vp.Parent = parent
	holder:Destroy()
	return vp
end
Menus.spearView = spearView

local function stars(n: number, max: number): string
	if n > max then return "★ " .. tostring(n) end
	return string.rep("★", math.max(0,n)) .. string.rep("☆", math.max(0,max - n))
end

---------------------------------------------------------------------
-- Сумка (страницы по 12)
---------------------------------------------------------------------
local function itemValue(it: any): number
	return it.price * (it.wrapped and Config.WRAP_MULT or 1)
end

-- V25: строка рынка под сумкой и на прилавке. base - цена без рынка, quote - с рынком.
local function marketLine(now: number, mflags: any, base: number, quote: number): string
	local M = Config.MARKET
	local ev = Config.marketEvents(now)
	local ratio = base > 0 and quote / base or 1
	local parts = {
		string.format("📈 Market ×%.2f", ratio),
		string.format("🔥 %s ×%.1f", Config.RARITIES[ev.hotRarity].name, M.HOT_RARITY),
		string.format("❄ %s ×%.2f", Config.RARITIES[ev.coldRarity].name, M.COLD_RARITY),
		string.format("⭐ %s ×%.1f", ev.craze.name, M.CRAZE),
		string.format("📉 %s ×%.1f", ev.glut.name, M.GLUT),
	}
	if Perks.has("insight") then
		local seq = {}
		for k = 1, Config.SHOP.PERK.forecastHours do
			table.insert(seq, Config.RARITIES[Config.marketEvents(now + k * M.HOUR).hotRarity].name)
		end
		table.insert(parts, "🔮 hot next: " .. table.concat(seq, " › "))
	end
	if mflags.fair then
		table.insert(parts, "🎪 Trade Fair")
	end
	return table.concat(parts, "  ·  ")
end

local function renderBag(body: Frame, st: { [string]: any })
	local d = Backend.data
	local items = table.clone(d.items)
	table.sort(items, function(a, b)
		return itemValue(a) > itemValue(b)
	end)
	st.sel = st.sel or {}
	st.page = st.page or 1
	local market = nearPrompt("sell", 22) or Perks.sellAnywhere() -- VIP Hunter: продажа откуда угодно
	local total = 0
	for _, it in items do
		total += itemValue(it)
	end
	local now = Config.marketNow()
	local mflags = Perks.marketFlags()
	local mq = Config.marketQuote(items, d, now, mflags)
	local top = row(body, 44)
	txt(top, string.format("🎒 %d / %d   ·   💰 %s", #items, d.bagCap, Num.short(mq * Backend.boostMult("coins"))), 26, C.text, { Size = UDim2.new(0.6, 0, 1, 0) })
	if market then
		local n = 0
		local selSum = 0
		for _, it in items do
			if st.sel[it.id] then
				n += 1
				selSum += itemValue(it)
			end
		end
		local b = UI.button({ Text = n > 0 and ("Sell (" .. n .. ")") or "Sell All", TextSize = 22, Color = C.gold, Size = UDim2.fromOffset(220, 44), AnchorPoint = Vector2.new(1, 0), Position = UDim2.fromScale(1, 0), Shine = true }, function()
			local ids: any = "all"
			if n > 0 then
				ids = {}
				for id in st.sel do
					table.insert(ids, id)
				end
			end
			local ok, gain, cnt = call("Sell", ids)
			if ok then
				st.sel = {}
				Sfx.play("buy")
				Hud.flyCoins(UI.screenPos(body), gain)
				UI.toast(string.format("Sold %d for %s 💰", cnt, Num.short(gain)), "gold")
				Menus.refresh()
			end
		end)
		b.Parent = top
		UI.setEnabled(b, #items > 0)
	else
		txt(top, "Sell your catch at the Market 💰", 18, C.dim, { Size = UDim2.new(0.4, 0, 1, 0), Position = UDim2.fromScale(0.6, 0), XAlign = Enum.TextXAlignment.Right })
	end
	local per = 12
	local pages = math.max(1, math.ceil(#items / per))
	st.page = math.clamp(st.page, 1, pages)
	local grid = Instance.new("Frame")
	grid.BackgroundTransparency = 1
	grid.Size = UDim2.new(1, 0, 1, -104)
	grid.Position = UDim2.fromOffset(0, 50)
	grid.Parent = body
	local g = UI.grid(Vector2.new(128, 168), 10)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = grid
	if #items == 0 then
		txt(grid, "Your bag is empty. Head to the forest hide and throw your spear! 🗡️", 24, C.dim, { XAlign = Enum.TextXAlignment.Center, Size = UDim2.new(1, 0, 0, 60), Wrap = true })
	end
	for i = (st.page - 1) * per + 1, math.min(#items, st.page * per) do
		local it = items[i]
		Card.new(it.sp, it, { size = Vector2.new(128, 168), selected = st.sel[it.id] == true, layoutOrder = i, parent = grid, onClick = market and function()
			st.sel[it.id] = not st.sel[it.id] or nil
			Sfx.play("press")
			Menus.refresh()
		end or nil })
	end
	local bot = row(body, 46)
	bot.Position = UDim2.new(0, 0, 1, -46)
	bot.AnchorPoint = Vector2.new(0, 0)
	local prev = UI.button({ Text = "◀", TextSize = 26, Color = C.blue, Size = UDim2.fromOffset(60, 44) }, function()
		st.page -= 1
		Menus.refresh()
	end)
	prev.Parent = bot
	UI.setEnabled(prev, st.page > 1)
	txt(bot, string.format("%d / %d", st.page, pages), 24, C.text, { Size = UDim2.fromOffset(100, 44), Position = UDim2.fromOffset(70, 0), XAlign = Enum.TextXAlignment.Center })
	local nxt = UI.button({ Text = "▶", TextSize = 26, Color = C.blue, Size = UDim2.fromOffset(60, 44), Position = UDim2.fromOffset(180, 0) }, function()
		st.page += 1
		Menus.refresh()
	end)
	nxt.Parent = bot
	UI.setEnabled(nxt, st.page < pages)
	txt(bot, marketLine(now, mflags, total, mq) .. "\n📦 Wrapped catch sells for ×" .. Config.WRAP_MULT, 14, C.dim, { Size = UDim2.new(1, -260, 1, 0), Position = UDim2.fromOffset(260, 0), XAlign = Enum.TextXAlignment.Right, Wrap = true })
end

function Menus.bag()
	show("bag", "🎒 Bag", Vector2.new(900, 620), C.orange, renderBag)
end

---------------------------------------------------------------------
-- Копья: магазин + выбор
---------------------------------------------------------------------
local function spearStatsText(id: string, lvl: number): string
	local s = Config.spearStats(id, lvl)
	return string.format("Sharpness %s  ·  Power %s\nLuck ×%.1f  ·  Range ×%.2f\nChance to reach ×10: %s", stars(s.sharp, 6), stars(s.heavy, 5), s.luck, s.range, Num.odds(Roll.reachChance(10, s.alpha)))
end

local function renderSpears(body: Frame, st: { [string]: any })
	local d = Backend.data
	local pageSize=6
	local pages=math.ceil(#Config.SPEARS/pageSize)
	st.page=math.clamp(st.page or 1,1,pages)
	local sc = UI.scroll(body,UDim2.new(1,0,1,-58))
	UI.list(Enum.FillDirection.Vertical, 10).Parent = sc
	UI.pad(4, 4).Parent = sc
	for i=(st.page-1)*pageSize+1,math.min(st.page*pageSize,#Config.SPEARS) do
		local s=Config.SPEARS[i]
		local owned = d.spears[s.id] ~= nil
		local lvl = d.spears[s.id] or 0
		local inHand = d.spear == s.id
		local rowF = UI.panel({ Color = inHand and Color3.fromRGB(60, 110, 70) or C.card, Size = UDim2.new(1, -16, 0, 128), Radius = 16, LayoutOrder = i, Parent = sc })
		local vpH = Instance.new("Frame")
		vpH.BackgroundTransparency = 1
		vpH.Size = UDim2.fromOffset(120, 120)
		vpH.Position = UDim2.fromOffset(6, 4)
		vpH.Parent = rowF
		spearView(s.id, vpH, inHand and 1.2 or 0.4)
		UI.label({ Text = s.name .. (owned and lvl > 0 and ("  +" .. lvl) or ""), TextSize = 28, Size = UDim2.new(0.5, 0, 0, 34), Position = UDim2.fromOffset(134, 6), XAlign = Enum.TextXAlignment.Left, Color = s.trail[1]:Lerp(Color3.new(1, 1, 1), 0.4), Parent = rowF })
		UI.label({ Text = spearStatsText(s.id, lvl), TextSize = 17, Size = UDim2.new(0.55, 0, 0, 66), Position = UDim2.fromOffset(134, 40), XAlign = Enum.TextXAlignment.Left, YAlign = Enum.TextYAlignment.Top, Color = C.dim, Stroke = 2, Parent = rowF })
		UI.label({ Text = s.desc, TextSize = 15, Size = UDim2.new(0.55, 0, 0, 20), Position = UDim2.fromOffset(134, 104), XAlign = Enum.TextXAlignment.Left, Color = C.gray, Stroke = 2, Parent = rowF })
		local text, color, enabled = "", C.green, true
		if inHand then
			text, color, enabled = "Equipped ✓", C.gray, false
		elseif owned then
			text, color = "Equip", C.blue
		else
			text, color = "💰 " .. Num.short(s.price), C.gold
			enabled = d.coins >= s.price
		end
		local b = UI.button({ Text = text, TextSize = 24, Color = color, Size = UDim2.fromOffset(190, 56), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -14, 0.5, 0), Shine = not owned and enabled }, function()
			if owned then
				if call("EquipSpear", s.id) then
					Sfx.play("equip")
				end
			else
				local ok = call("BuySpear", s.id)
				if ok then
					Sfx.play("buy")
					UI.confetti(40, { s.trail[1], s.trail[2], C.gold })
					Hud.banner("NEW SPEAR!", C.gold, s.name, 2)
					if Backend.data.tutorial == 4 then
						Backend.call("Tutorial", 5)
					end
				end
			end
		end)
		b.Parent = rowF
		UI.setEnabled(b, enabled)
	end
	local footer=row(body,48)
	footer.Position=UDim2.new(0,0,1,-48)
	local prev=UI.button({Text="◀ Previous",TextSize=22,Color=C.blue,Size=UDim2.fromOffset(180,44),Parent=footer},function()
		st.page-=1;Menus.refresh()
	end)
	UI.setEnabled(prev,st.page>1)
	UI.label({Text=string.format("%d / %d  ·  %d spears",st.page,pages,#Config.SPEARS),TextSize=21,Color=C.dim,
		Size=UDim2.new(1,-380,1,0),Position=UDim2.fromOffset(190,0),Parent=footer})
	local nextPage=UI.button({Text="Next ▶",TextSize=22,Color=C.blue,Size=UDim2.fromOffset(180,44),
		AnchorPoint=Vector2.new(1,0),Position=UDim2.fromScale(1,0),Parent=footer},function()
		st.page+=1;Menus.refresh()
	end)
	UI.setEnabled(nextPage,st.page<pages)
end

function Menus.spears()
	show("spears", "🔱 Spears", Vector2.new(880, 640), C.blue, renderSpears)
end

---------------------------------------------------------------------
-- Кузница: улучшение текущего копья (0..5)
---------------------------------------------------------------------
local function renderForge(body: Frame, _st: { [string]: any })
	local d = Backend.data
	local id = d.spear
	local s = Config.SPEAR_BY_ID[id]
	local lvl = d.spears[id] or 0
	local maxL = Perks.forgeMax()
	local left = Instance.new("Frame")
	left.BackgroundTransparency = 1
	left.Size = UDim2.new(0.42, 0, 1, 0)
	left.Parent = body
	spearView(id, left, 1)
	UI.label({ Text = stars(lvl, maxL), TextSize = 40, Color = C.gold, Size = UDim2.new(1, 0, 0, 44), Position = UDim2.new(0, 0, 1, -48), Parent = left })
	local right = Instance.new("Frame")
	right.BackgroundTransparency = 1
	right.Size = UDim2.new(0.56, 0, 1, 0)
	right.Position = UDim2.fromScale(0.44, 0)
	right.Parent = body
	UI.list(Enum.FillDirection.Vertical, 8).Parent = right
	txt(right, s.name .. "  +" .. lvl, 34, C.text, { LayoutOrder = 1 })
	local a, b = Config.spearStats(id, lvl), Config.spearStats(id, math.min(maxL, lvl + 1))
	local function cmp(name: string, x: string, y: string, order: number)
		txt(right, string.format("%s: <b>%s</b>%s", name, x, lvl < maxL and ("  →  <font color=\"#7CFF8A\">" .. y .. "</font>") or ""), 22, C.dim, { LayoutOrder = order })
	end
	cmp("Luck", string.format("×%.2f", a.luck), string.format("×%.2f", b.luck), 2)
	cmp("Range", string.format("×%.2f", a.range), string.format("×%.2f", b.range), 3)
	cmp("Reach ×10", Num.odds(Roll.reachChance(10, a.alpha)), Num.odds(Roll.reachChance(10, b.alpha)), 4)
	cmp("Reach ×25", Num.odds(Roll.reachChance(25, a.alpha)), Num.odds(Roll.reachChance(25, b.alpha)), 5)
	if lvl >= maxL then
		txt(right, lvl >= Config.FORGE.maxLevel and "This spear is fully upgraded! 🔥" or "Free forge limit reached. Master Smith (Shop) unlocks 2 more levels.", 24, C.gold, { LayoutOrder = 6, Wrap = true, Size = UDim2.new(1, 0, 0, 60) })
		return
	end
	local cost = Perks.forgeCost(id, lvl)
	local holder = row(right, 64, 7)
	local btn = UI.button({ Text = "🔨 Upgrade · " .. Num.short(cost), TextSize = 26, Color = C.orange, Size = UDim2.fromOffset(330, 60), Shine = d.coins >= cost }, function()
		local ok, nl = call("Forge")
		if ok then
			for i = 1, 4 do
				task.delay(i * 0.12, function()
					if Sfx.has("hit_wood") then
						Sfx.play("hit_wood", 0.9 + i * 0.07, 0.6)
					else
						Sfx.play("hit", 1.4 + i * 0.1, 0.6)
					end
					UI.burst(UI.screenPos(left), C.orange, 14, 420)
				end)
			end
			UI.flash(C.orange, 0.3, 0.6)
			Hud.banner("+" .. tostring(nl) .. " " .. s.name, C.orange, "Your spear is stronger", 1.8)
		end
	end)
	btn.Parent = holder
	UI.setEnabled(btn, d.coins >= cost)
	txt(right, "Upgrades stay with each spear. Equip any spear you own to upgrade it.", 17, C.gray, { LayoutOrder = 8, Wrap = true, Size = UDim2.new(1, 0, 0, 50) })
end

function Menus.forge()
	show("forge", "🔨 Forge", Vector2.new(820, 470), C.orange, renderForge)
end

---------------------------------------------------------------------
-- Рынок: продажа + сумка побольше
---------------------------------------------------------------------
local function renderMarket(body: Frame, _st: { [string]: any })
	local d = Backend.data
	UI.list(Enum.FillDirection.Vertical, 12).Parent = body
	local total, wrapped = 0, 0
	for _, it in d.items do
		total += itemValue(it)
		if it.wrapped then
			wrapped += 1
		end
	end
	local cm = Backend.boostMult("coins")
	local now = Config.marketNow()
	local mflags = Perks.marketFlags()
	local mq = Config.marketQuote(d.items, d, now, mflags)
	txt(body, string.format("In your bag: <b>%d</b> (📦 wrapped: %d)", #d.items, wrapped), 26, C.text, { LayoutOrder = 1 })
	txt(body, string.format("Value: <font color=\"#FFCC34\">💰 %s</font>%s", Num.short(mq * cm), cm > 1 and "  (×2 boost!)" or ""), 26, C.text, { LayoutOrder = 2 })
	local r1 = row(body, 64, 3)
	local sell = UI.button({ Text = "Sell All", TextSize = 28, Color = C.gold, Size = UDim2.fromOffset(280, 60), Shine = #d.items > 0 }, function()
		local ok, gain, cnt = call("Sell", "all")
		if ok then
			Sfx.play("buy")
			for i = 1, math.min(8, cnt) do
				task.delay(i * 0.06, function()
					Sfx.play("coin", 1.6 + i * 0.05, 0.4)
				end)
			end
			Hud.flyCoins(UI.screenPos(body), gain)
			Hud.banner("+" .. Num.short(gain) .. " 💰", C.gold, "Sold: " .. cnt, 1.8)
			if Backend.data.tutorial == 3 then
				Backend.call("Tutorial", 4)
			end
		end
	end)
	sell.Parent = r1
	UI.setEnabled(sell, #d.items > 0)
	local pick = UI.button({ Text = "Select…", TextSize = 24, Color = C.blue, Size = UDim2.fromOffset(200, 60), Position = UDim2.fromOffset(296, 0) }, function()
		Menus.bag()
	end)
	pick.Parent = r1
	UI.setEnabled(pick, #d.items > 0)
	txt(body, marketLine(now, mflags, total, mq) .. "\n📦 Catch wrapped at your cabin table sells for ×" .. Config.WRAP_MULT .. "!", 18, C.dim, { LayoutOrder = 4, Wrap = true, Size = UDim2.new(1, 0, 0, 70) })
	local nxt = Config.BAG[d.bagLvl + 1]
	local r2 = UI.panel({ Color = C.card, Size = UDim2.new(1, 0, 0, 90), Radius = 16, LayoutOrder = 5, Parent = body })
	if nxt then
		UI.label({ Text = string.format("🎒 Bigger bag: %d → <b>%d</b> slots", d.bagCap, nxt.cap), Rich = true, TextSize = 26, Size = UDim2.new(0.6, 0, 1, 0), Position = UDim2.fromOffset(16, 0), XAlign = Enum.TextXAlignment.Left, Parent = r2 })
		local b = UI.button({ Text = "💰 " .. Num.short(nxt.cost), TextSize = 24, Color = C.green, Size = UDim2.fromOffset(200, 56), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -16, 0.5, 0), Shine = d.coins >= nxt.cost }, function()
			if call("BuyBag") then
				Sfx.play("buy")
				Hud.banner("BIGGER BAG!", C.green, Backend.data.bagCap .. " slots", 1.6)
			end
		end)
		b.Parent = r2
		UI.setEnabled(b, d.coins >= nxt.cost)
	else
		UI.label({ Text = "🎒 Maximum bag capacity: " .. d.bagCap .. " slots", TextSize = 26, Size = UDim2.new(1, -32, 1, 0), Position = UDim2.fromOffset(16, 0), XAlign = Enum.TextXAlignment.Left, Parent = r2 })
	end
end

function Menus.market()
	show("market", "💰 Market", Vector2.new(760, 470), C.gold, renderMarket)
end

---------------------------------------------------------------------
-- Коллекция: 24 вида по зонам, силуэты непойманных
---------------------------------------------------------------------
local function detail(parent: Frame, sp: any, rec: any)
	local ov = UI.panel({ Color = C.panel2, Size = UDim2.fromScale(1, 1), Radius = 18, ZIndex = 20, Parent = parent })
	local rar = Config.RARITIES[sp.rarity]
	local vpH = Instance.new("Frame")
	vpH.BackgroundTransparency = 1
	vpH.Size = UDim2.new(0.42, 0, 1, -20)
	vpH.Position = UDim2.fromOffset(10, 10)
	vpH.Parent = ov
	local model = Card.model(sp.id, rec and (rec.rainbow and "rainbow" or (rec.gold and "gold" or nil)) or nil)
	if model then
		local vp = UI.viewport(model, nil, math.rad(-30), 0.8)
		vp.Parent = vpH
	end
	local info = Instance.new("Frame")
	info.BackgroundTransparency = 1
	info.Size = UDim2.new(0.55, 0, 1, -20)
	info.Position = UDim2.new(0.44, 0, 0, 10)
	info.Parent = ov
	UI.list(Enum.FillDirection.Vertical, 6).Parent = info
	txt(info, sp.icon .. " " .. sp.name, 36, rar.color, { LayoutOrder = 1 })
	txt(info, rar.name .. "  ·  " .. Config.ZONES[sp.zone].icon .. " " .. Config.ZONES[sp.zone].name, 22, C.dim, { LayoutOrder = 2 })
	txt(info, "«" .. sp.fact .. "»", 20, C.text, { LayoutOrder = 3, Wrap = true, Size = UDim2.new(1, 0, 0, 52) })
	txt(info, string.format("Caught: <b>%d</b>   ·   Best: <b>%s</b>", rec.n, Num.weight(rec.best)), 22, C.text, { LayoutOrder = 4 })
	txt(info, "Best value: 💰 " .. Num.short(rec.bestPrice), 22, C.gold, { LayoutOrder = 5 })
	txt(info, (rec.gold and "✨ Gold discovered" or "✨ Gold undiscovered") .. "   ·   " .. (rec.rainbow and "🌈 Rainbow discovered" or "🌈 Rainbow undiscovered"), 20, C.dim, { LayoutOrder = 6 })
	txt(info, "Required spear: “" .. Roll.spearFor(sp).name .. "»", 20, C.cyan, { LayoutOrder = 7 })
	local back = UI.button({ Text = "Back", TextSize = 22, Color = C.blue, Size = UDim2.fromOffset(140, 48), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -10, 1, -10) }, function()
		ov:Destroy()
	end)
	back.Parent = ov
end

local function renderIndex(body: Frame, st: { [string]: any })
	local d = Backend.data
	st.zone = st.zone or 1
	local total, got = #Config.SPECIES, 0
	for _ in d.index do
		got += 1
	end
	local tabs = Instance.new("ScrollingFrame")
	tabs.Name="BiomeTabs"
	tabs.BackgroundTransparency=1;tabs.BorderSizePixel=0
	tabs.Size=UDim2.new(1,0,0,54)
	tabs.ScrollingDirection=Enum.ScrollingDirection.X
	tabs.AutomaticCanvasSize=Enum.AutomaticSize.X
	tabs.CanvasSize=UDim2.new()
	tabs.ScrollBarThickness=5;tabs.ScrollBarImageColor3=C.gold
	tabs.Parent=body
	UI.list(Enum.FillDirection.Horizontal, 8).Parent = tabs
	for z, zc in Config.ZONES do
		local n, all = 0, 0
		for _, sp in Config.SPECIES do
			if sp.zone == z then
				all += 1
				if d.index[sp.id] then
					n += 1
				end
			end
		end
		local b = UI.button({ Text = zc.icon .. " " .. zc.name .. " " .. n .. "/" .. all, TextSize = 19, Color = st.zone == z and zc.color or C.gray, Size = UDim2.fromOffset(196, 46), LayoutOrder = z }, function()
			st.zone = z
			Menus.refresh()
		end)
		b.Parent = tabs
	end
	local grid = Instance.new("Frame")
	grid.BackgroundTransparency = 1
	grid.Size = UDim2.new(1, 0, 1, -100)
	grid.Position = UDim2.fromOffset(0, 58)
	grid.Parent = body
	local g = UI.grid(Vector2.new(170, 222), 14)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = grid
	local i = 0
	for _, sp in Config.SPECIES do
		if sp.zone == st.zone then
			i += 1
			local rec = d.index[sp.id]
			Card.new(sp.id, nil, { size = Vector2.new(170, 222), locked = rec == nil, count = rec and rec.n or nil, layoutOrder = sp.rarity, parent = grid, spin = rec and 0.5 or nil, onClick = rec and function()
				detail(body, sp, rec)
			end or nil })
		end
	end
	local bar = UI.bar({ Size = UDim2.new(1, -20, 0, 26), Position = UDim2.new(0, 10, 1, -32), Color = C.gold, TextSize = 18, Parent = body })
	bar.set(got / total, string.format("Collection: %d / %d", got, total))
end

function Menus.index()
	show("index", "📖 Collection", Vector2.new(900, 640), C.purple, renderIndex)
end

---------------------------------------------------------------------
-- Задания
---------------------------------------------------------------------
local function rewardText(r: any): string
	local parts = {}
	if r.coins then
		table.insert(parts, "💰 " .. Num.short(r.coins))
	end
	if r.xp then
		table.insert(parts, "⭐ " .. r.xp .. " XP")
	end
	if r.boost then
		local b = Config.BOOSTS[r.boost]
		table.insert(parts, b.icon .. " " .. b.name .. " " .. Num.time(r.dur or 120))
	end
	return table.concat(parts, "   ")
end
Menus.rewardText = rewardText

local function renderQuests(body: Frame, _st: { [string]: any })
	local d = Backend.data
	local sc = UI.scroll(body)
	UI.list(Enum.FillDirection.Vertical, 10).Parent = sc
	UI.pad(4, 4).Parent = sc
	local list = {}
	for id, q in d.quests do
		table.insert(list, { q = Config.QUEST_BY_ID[id], st = q })
	end
	table.sort(list, function(a, b)
		return a.q.index < b.q.index
	end)
	if #list == 0 then
		txt(sc, "All quests complete! You are a forest legend 🏆", 26, C.gold)
	end
	for i, e in list do
		local q, s = e.q, e.st
		local npc = Config.NPC[q.npc]
		local f = UI.panel({ Color = s.done and Color3.fromRGB(60, 120, 70) or C.card, Size = UDim2.new(1, -16, 0, 116), Radius = 16, LayoutOrder = i, Parent = sc })
		UI.label({ Text = q.title, TextSize = 28, Size = UDim2.new(0.6, 0, 0, 32), Position = UDim2.fromOffset(16, 6), XAlign = Enum.TextXAlignment.Left, Parent = f })
		UI.label({ Text = (npc and npc.name or "") .. ": " .. q.text, TextSize = 19, Color = C.dim, Size = UDim2.new(0.62, 0, 0, 24), Position = UDim2.fromOffset(16, 38), XAlign = Enum.TextXAlignment.Left, Stroke = 2, Parent = f })
		UI.label({ Text = rewardText(q.reward), TextSize = 19, Color = C.gold, Size = UDim2.new(0.62, 0, 0, 24), Position = UDim2.fromOffset(16, 62), XAlign = Enum.TextXAlignment.Left, Stroke = 2, Parent = f })
		local bar = UI.bar({ Size = UDim2.new(0.6, 0, 0, 18), Position = UDim2.fromOffset(16, 90), Color = C.cyan, TextSize = 14, Parent = f })
		bar.set(math.min(1, s.p / q.goal), Num.short(math.min(s.p, q.goal)) .. " / " .. Num.short(q.goal))
		local b = UI.button({ Text = s.done and "Claim!" or "In Progress", TextSize = 24, Color = s.done and C.gold or C.gray, Size = UDim2.fromOffset(200, 56), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -14, 0.5, 0), Shine = s.done }, function()
			local ok, r = call("QuestClaim", q.id)
			if ok then
				Sfx.play("level")
				UI.confetti(40)
				Hud.banner("QUEST COMPLETE!", C.gold, rewardText(r), 2)
				if r.coins then
					Hud.flyCoins(UI.screenPos(f), r.coins)
				end
			end
		end)
		b.Parent = f
		UI.setEnabled(b, s.done)
	end
end

function Menus.quests()
	show("quests", "📜 Quests", Vector2.new(820, 600), C.cyan, renderQuests)
end

---------------------------------------------------------------------
-- Зелья Травницы
---------------------------------------------------------------------
local function renderPotions(body: Frame, _st: { [string]: any })
	local d = Backend.data
	local g = UI.grid(Vector2.new(360, 170), 14)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = body
	for i, p in Config.POTIONS do
		local b = Config.BOOSTS[p.boost]
		local pc = Config.potionCost(p, d)
		local f = UI.panel({ Color = b.color:Lerp(C.panel, 0.55), Size = UDim2.fromOffset(360, 170), Radius = 18, LayoutOrder = i, Parent = body })
		UI.label({ Text = "🧪", TextSize = 64, Size = UDim2.fromOffset(90, 100), Position = UDim2.fromOffset(8, 10), Parent = f })
		UI.label({ Text = b.icon .. " " .. b.name, TextSize = 26, Size = UDim2.new(1, -110, 0, 32), Position = UDim2.fromOffset(100, 14), XAlign = Enum.TextXAlignment.Left, Parent = f })
		local left = Backend.boostLeft(p.boost)
		UI.label({ Text = "⏱ " .. Num.time(p.dur) .. (left > 0 and ("  ·  active: " .. Num.time(left)) or ""), TextSize = 19, Color = C.dim, Size = UDim2.new(1, -110, 0, 24), Position = UDim2.fromOffset(100, 50), XAlign = Enum.TextXAlignment.Left, Stroke = 2, Parent = f })
		local btn = UI.button({ Text = "💰 " .. Num.short(pc), TextSize = 24, Color = C.green, Size = UDim2.fromOffset(200, 54), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -12), Shine = d.coins >= pc }, function()
			if call("BuyPotion", i) then
				Sfx.play("buy")
				UI.flash(b.color, 0.3, 0.6)
				Hud.banner(b.icon .. " " .. b.name, b.color, "for " .. Num.time(p.dur), 1.6)
			end
		end)
		btn.Parent = f
		UI.setEnabled(btn, d.coins >= pc)
	end
end

function Menus.potions()
	show("potions", "🧪 Herbalist Potions", Vector2.new(800, 480), C.pink, renderPotions)
end

---------------------------------------------------------------------
-- Настройки
---------------------------------------------------------------------
local function renderSettings(body: Frame, _st: { [string]: any })
	local s = Backend.data.settings
	UI.list(Enum.FillDirection.Vertical, 12).Parent = body
	local opts = {
		{ "music", "🎵 Music" },
		{ "sfx", "🔊 Sound Effects" },
		{ "skip", "⏩ Quick Catch Reveal" },
		{ "lowFx", "📱 Reduced Effects (Better Performance)" },
	}
	for i, o in opts do
		local r = UI.panel({ Color = C.card, Size = UDim2.new(1, 0, 0, 66), Radius = 14, LayoutOrder = i, Parent = body })
		UI.label({ Text = o[2], TextSize = 26, Size = UDim2.new(0.7, 0, 1, 0), Position = UDim2.fromOffset(16, 0), XAlign = Enum.TextXAlignment.Left, Parent = r })
		local on = s[o[1]] == true
		local b = UI.button({ Text = on and "ON" or "OFF", TextSize = 22, Color = on and C.green or C.red, Size = UDim2.fromOffset(130, 50), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -12, 0.5, 0) }, function()
			call("Settings", { [o[1]] = not on })
		end)
		b.Parent = r
	end
	txt(body, "Spear Hunt v" .. Config.VERSION, 18, C.gray, { LayoutOrder = 9 })
end

function Menus.settings()
	show("settings", "⚙️ Settings", Vector2.new(640, 440), C.gray, renderSettings)
end

---------------------------------------------------------------------
-- Демо-панель (только Config.BACKEND = "Demo")
---------------------------------------------------------------------
local function renderDemo(body: Frame, _st: { [string]: any })
	local g = UI.grid(Vector2.new(250, 60), 12)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = body
	local luck = Backend.demoLuck()
	local list = {
		{ "💰 +1M Coins", C.gold, function()
			call("Demo", "coins", 1e6)
		end },
		{ "💰 +1B Coins", C.gold, function()
			call("Demo", "coins", 1e9)
		end },
		{ "💪 +500 Strength", C.orange, function()
			call("Demo", "power", 500)
		end },
		{ "💪 +50K Strength", C.orange, function()
			call("Demo", "power", 50000)
		end },
		{ "🍀 Luck ×1" .. (luck == 1 and " ✓" or ""), C.green, function()
			call("Demo", "luck", 1)
		end },
		{ "🍀 Luck ×20" .. (luck == 20 and " ✓" or ""), C.green, function()
			call("Demo", "luck", 20)
		end },
		{ "🍀 Luck ×500" .. (luck == 500 and " ✓" or ""), C.green, function()
			call("Demo", "luck", 500)
		end },
		{ "🔱 All Spears", C.blue, function()
			call("Demo", "spears")
		end },
		{ "⭐ +1 Level", C.cyan, function()
			call("Demo", "level")
		end },
		{ "🧪 All Boosts", C.pink, function()
			call("Demo", "boosts")
		end },
		{ "🏛️ Visit Showroom", C.purple, function()
			UI.closeWindow()
			local c = player.Character
			if c and map:FindFirstChild("Showroom") then
				c:PivotTo(CFrame.lookAt(Vector3.new(169, 4, 36), Vector3.new(169, 4, 80)))
			end
		end },
		{ "♻️ Reset", C.red, function()
			call("Demo", "reset")
		end },
	}
	for i, e in list do
		local b = UI.button({ Text = e[1], TextSize = 22, Color = e[2], Size = UDim2.fromOffset(250, 60), LayoutOrder = i }, e[3])
		b.Parent = body
	end
end

function Menus.demo()
	if Backend.mode ~= "Demo" or not game:GetService("RunService"):IsStudio() then
		UI.toast("Developer tools are available in Demo mode only", "warn")
		return
	end
	show("demo", "🧪 Developer Tools", Vector2.new(840, 400), C.purple, renderDemo)
end

---------------------------------------------------------------------
-- Robux-магазин (отдельный модуль, грузится при первом открытии)
function Menus.shop()
	local ok, shop = pcall(require, script.Parent.Shop)
	if ok and type(shop) == "table" then
		shop.open()
	else
		warn("[Shop] " .. tostring(shop))
		UI.toast("The shop is unavailable right now", "warn")
	end
end

Backend.onChange(function()
	Menus.refresh()
end)

Hud.MenuClicked.Event:Connect(function(name: string)
	local f = (Menus :: any)[name]
	if type(f) == "function" then
		if UI.windowOpen(name) then
			UI.closeWindow()
		else
			f()
		end
	end
end)

return Menus
