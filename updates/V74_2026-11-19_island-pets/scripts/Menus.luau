-- StarterPlayerScripts/Client/Menus.luau
-- Окна: Сумка, Копья (магазин/выбор), Кузница, Рынок, Коллекция, Задания, Hunter Pass, Зелья, Настройки, Демо.
-- Все действия — через Backend.call; после ответа окно перерисовывается на месте.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

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

-- V53: разговор с NPC закрывается, когда открывается любое окно (раньше окно оказывалось под диалогом, который лежит поверх)
local function closeDialog()
	local ok, D = pcall(require, script.Parent.Dialog)
	if ok and type(D) == "table" and D.close then
		D.close()
	end
end

local function show(id: string, title: string, size: Vector2, color: Color3, render: (Frame, any) -> (), state: { [string]: any }?)
	closeDialog()
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

---------------------------------------------------------------------
-- V74: помощники для окон на арт-спрайтах (иконка + текст, ячейки, кнопки, вкладки, пагинатор, фишки рынка)
---------------------------------------------------------------------
-- Shop.luau большой: берём лениво, при ошибке возвращаем nil
local function petShop(): any
	local ok, shop = pcall(require, script.Parent.Shop)
	if ok and type(shop) == "table" then
		return shop
	end
	warn("[Pets] " .. tostring(shop))
	return nil
end

-- строка «иконка + текст»; o: Center, AutoX, Size, Position, AnchorPoint, LayoutOrder, ZIndex, Rich
local function iconLine(parent: Instance, icon: string?, text: string, ts: number, color: Color3?, o: { [string]: any }?): (Frame, TextLabel)
	local p = o or {}
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = p.Size or (if p.AutoX then UDim2.fromOffset(0, ts + 10) else UDim2.new(1, 0, 0, ts + 10))
	if p.AutoX then
		f.AutomaticSize = Enum.AutomaticSize.X
	end
	if p.Position then
		f.Position = p.Position
	end
	if p.AnchorPoint then
		f.AnchorPoint = p.AnchorPoint
	end
	if p.LayoutOrder then
		f.LayoutOrder = p.LayoutOrder
	end
	f.ZIndex = p.ZIndex or 4
	f.Parent = parent
	UI.list(Enum.FillDirection.Horizontal, 6, if p.Center then Enum.HorizontalAlignment.Center else Enum.HorizontalAlignment.Left, Enum.VerticalAlignment.Center).Parent = f
	local z = f.ZIndex + 1
	if icon then
		UI.art(icon, { Size = UDim2.fromOffset(ts + 8, ts + 8), Fit = true, LayoutOrder = 1, ZIndex = z, Parent = f })
	end
	local l = UI.label({ Name = "Label", Text = text, TextSize = ts, Color = color, Rich = p.Rich, Size = UDim2.fromOffset(0, ts + 8), AutoX = true, LayoutOrder = 2, ZIndex = z, Parent = f })
	return f, l
end

-- тёмная ячейка со слева иконкой (cell_dark)
local function statCell(parent: Instance, size: UDim2, h: number, icon: string, text: string, ts: number, pos: UDim2?, order: number?): Frame
	local f = UI.art("cell_dark", { Size = size, Position = pos, LayoutOrder = order, Slice = { 30, 0, 30, 0 }, SliceScale = h / 79, ZIndex = 3, Parent = parent })
	UI.art(icon, { Size = UDim2.fromOffset(h - 10, h - 10), Position = UDim2.fromOffset(10, 5), Fit = true, ZIndex = 4, Parent = f })
	UI.label({ Name = "Text", Text = text, TextSize = ts, Rich = true, Size = UDim2.new(1, -(h + 20), 1, 0), Position = UDim2.fromOffset(h + 8, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = f })
	return f
end

-- глянцевая кнопка-спрайт (3-slice по горизонтали). o: Text, TextSize, Icon (иконка перед текстом), Price (текст цены с ic_coin), Position, AnchorPoint, LayoutOrder, Parent, Sound
local function glossy(key: string, w: number, h: number, o: { [string]: any }, onClick: (() -> ())?): ImageButton
	local ts = o.TextSize or 24
	local plain = o.Icon == nil and o.Price == nil
	local b = UI.artButton(key, {
		Name = o.Name, Size = UDim2.fromOffset(w, h), Position = o.Position, AnchorPoint = o.AnchorPoint, LayoutOrder = o.LayoutOrder,
		Slice = { 30, 0, 30, 0 }, SliceScale = h / UI.artSize(key).Y, Text = if plain then o.Text else nil, TextSize = ts, Sound = o.Sound, ZIndex = 4, Parent = o.Parent,
	}, onClick)
	if not plain then
		local cf = Instance.new("Frame")
		cf.BackgroundTransparency = 1
		cf.Size = UDim2.fromScale(1, 1)
		cf.ZIndex = 5
		cf.Parent = b
		UI.list(Enum.FillDirection.Horizontal, 6, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = cf
		if o.Price ~= nil then
			if o.Text then
				UI.label({ Text = o.Text, TextSize = ts, Size = UDim2.fromOffset(0, ts + 8), AutoX = true, LayoutOrder = 1, ZIndex = 6, Parent = cf })
			end
			UI.art("ic_coin", { Size = UDim2.fromOffset(ts + 6, ts + 6), Fit = true, LayoutOrder = 2, ZIndex = 6, Parent = cf })
			UI.label({ Name = "Label", Text = o.Price, TextSize = ts, Size = UDim2.fromOffset(0, ts + 8), AutoX = true, LayoutOrder = 3, ZIndex = 6, Parent = cf })
		else
			UI.art(o.Icon, { Size = UDim2.fromOffset(ts + 6, ts + 6), Fit = true, LayoutOrder = 1, ZIndex = 6, Parent = cf })
			UI.label({ Name = "Label", Text = o.Text or "", TextSize = ts, Size = UDim2.fromOffset(0, ts + 8), AutoX = true, LayoutOrder = 2, ZIndex = 6, Parent = cf })
		end
	end
	return b
end

-- вкладка tab_on / tab_off с иконкой и текстом
local function tabBtn(parent: Instance, on: boolean, w: number, h: number, icon: string?, text: string, ts: number, onClick: () -> (), pos: UDim2?, order: number?): ImageButton
	local b = UI.artButton(if on then "tab_on" else "tab_off", { Size = UDim2.fromOffset(w, h), Position = pos, LayoutOrder = order, Slice = { 36, 0, 36, 0 }, SliceScale = h / 77, ZIndex = 4, Parent = parent }, onClick)
	iconLine(b, icon, text, ts, nil, { Center = true, Size = UDim2.fromScale(1, 1), ZIndex = 5 })
	return b
end

-- пагинатор: стрелки + плашка «1 / N» по центру внизу родителя; st[key] - текущая страница
local function pager(parent: Instance, st: { [string]: any }, key: string, pages: number)
	local f = Instance.new("Frame")
	f.Name = "Pager"
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromOffset(240, 42)
	f.AnchorPoint = Vector2.new(0.5, 1)
	f.Position = UDim2.new(0.5, 0, 1, 0)
	f.ZIndex = 3
	f.Parent = parent
	local prev = UI.artButton("arrow_l", { Size = UDim2.fromOffset(54, 42), ZIndex = 4, Parent = f }, function()
		st[key] -= 1
		Menus.refresh()
	end)
	UI.setEnabled(prev, st[key] > 1)
	local pill = UI.art("pill_dark", { Size = UDim2.fromOffset(116, 42), Position = UDim2.fromOffset(62, 0), Slice = { 30, 0, 30, 0 }, SliceScale = 42 / 65, ZIndex = 3, Parent = f })
	UI.label({ Text = string.format("%d / %d", st[key], pages), TextSize = 22, Size = UDim2.fromScale(1, 1), ZIndex = 4, Parent = pill })
	local nxt = UI.artButton("arrow_r", { Size = UDim2.fromOffset(54, 42), Position = UDim2.fromOffset(186, 0), ZIndex = 4, Parent = f }, function()
		st[key] += 1
		Menus.refresh()
	end)
	UI.setEnabled(nxt, st[key] < pages)
end

-- сводка рынка: список фишек { text, key (рамка chip_*), icon }
local CHIP_BY_RARITY = { "chip_blue", "chip_blue", "chip_blue", "chip_violet", "chip_gold", "chip_red" }
local function marketChips(now: number, mflags: any, base: number, quote: number): { { text: string, key: string, icon: string } }
	local M = Config.MARKET
	local ev = Config.marketEvents(now)
	local ratio = base > 0 and quote / base or 1
	local hot = math.clamp(ev.hotRarity, 1, 6)
	local cold = math.clamp(ev.coldRarity, 1, 6)
	local chips = {
		{ text = string.format("Market ×%.2f", ratio), key = "chip_gold", icon = "ic_sell" },
		{ text = string.format("%s ×%.1f", Config.RARITIES[ev.hotRarity].name, M.HOT_RARITY), key = CHIP_BY_RARITY[hot], icon = "gem_" .. hot },
		{ text = string.format("%s ×%.2f", Config.RARITIES[ev.coldRarity].name, M.COLD_RARITY), key = "chip_blue", icon = "gem_" .. cold },
		{ text = string.format("%s ×%.1f", ev.craze.name, M.CRAZE), key = "chip_violet", icon = "ic_paw" },
		{ text = string.format("%s ×%.1f", ev.glut.name, M.GLUT), key = "chip_red", icon = "ic_paw" },
	}
	if Perks.has("insight") then
		local seq = {}
		for k = 1, Config.SHOP.PERK.forecastHours do
			table.insert(seq, Config.RARITIES[Config.marketEvents(now + k * M.HOUR).hotRarity].name)
		end
		table.insert(chips, { text = "Hot next: " .. table.concat(seq, " › "), key = "chip_violet", icon = "ic_star" })
	end
	if mflags.fair then
		table.insert(chips, { text = "Trade Fair", key = "chip_gold", icon = "p_fair" })
	end
	table.insert(chips, { text = "Wrapped ×" .. Config.WRAP_MULT, key = "chip_gold", icon = "p_rope" })
	return chips
end

-- ряд фишек с переносом; h - высота фишки
local function chipRow(parent: Instance, chips: { { text: string, key: string, icon: string } }, h: number, size: UDim2, pos: UDim2?, order: number?): Frame
	local f = Instance.new("Frame")
	f.Name = "Chips"
	f.BackgroundTransparency = 1
	f.Size = size
	if pos then
		f.Position = pos
	end
	if order then
		f.LayoutOrder = order
	end
	f.ZIndex = 3
	f.Parent = parent
	local l = Instance.new("UIListLayout")
	l.FillDirection = Enum.FillDirection.Horizontal
	l.Wraps = true
	l.Padding = UDim.new(0, 6)
	l.HorizontalAlignment = Enum.HorizontalAlignment.Center
	l.VerticalAlignment = Enum.VerticalAlignment.Top
	l.SortOrder = Enum.SortOrder.LayoutOrder
	l.Parent = f
	for i, c in chips do
		local w = math.clamp(math.floor(h * 1.1 + #c.text * 9.5 + 24), 150, 460)
		local chip = UI.art(c.key, { Size = UDim2.fromOffset(w, h), Slice = { 45, 0, 45, 0 }, SliceScale = h / 91, LayoutOrder = i, ZIndex = 3, Parent = f })
		UI.art(c.icon, { Size = UDim2.fromOffset(h - 8, h - 8), Position = UDim2.fromOffset(12, 4), Fit = true, ZIndex = 4, Parent = chip })
		UI.label({ Text = c.text, TextSize = 18, Size = UDim2.new(1, -(h + 22), 1, 0), Position = UDim2.fromOffset(h + 6, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = chip })
	end
	return f
end

-- карточка зверя на спрайте card_N (1..6 по редкости вида). o: w, h, locked, count, selected, spin, layoutOrder, parent, onClick
local function animalCard(spId: string, item: any?, o: { [string]: any }): Frame
	local sp = Config.SPECIES_BY_ID[spId]
	local w, h = o.w or 140, o.h or 180
	local r = if sp then math.clamp(sp.rarity, 1, 6) else 1
	local locked = o.locked == true
	local f = Instance.new("Frame")
	f.Name = "Card_" .. spId
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromOffset(w, h)
	f.LayoutOrder = o.layoutOrder or 0
	f.ZIndex = 3
	UI.art("card_" .. r, { Name = "Frame", Size = UDim2.fromScale(1, 1), Slice = 40, SliceScale = math.min(1, w / 172), Color = if locked then Color3.fromRGB(70, 70, 80) else nil, ZIndex = 3, Parent = f })
	-- 3D-портрет
	local ix = math.floor(w * 0.09)
	local ph = math.floor(h * 0.5)
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	holder.Size = UDim2.fromOffset(w - 2 * ix, ph)
	holder.Position = UDim2.fromOffset(ix, 12)
	holder.ZIndex = 4
	holder.Parent = f
	local model = Card.model(spId, if item then item.mut else nil)
	if model then
		local vp = UI.viewport(model, { ZIndex = 5 }, math.rad(-30), o.spin)
		if locked then
			-- силуэт непойманного
			vp.Ambient = Color3.new(0, 0, 0)
			vp.LightColor = Color3.new(0, 0, 0)
			vp.ImageColor3 = Color3.fromRGB(30, 30, 40)
		end
		vp.Parent = holder
	else
		UI.art("ic_deer", { Size = UDim2.fromScale(1, 1), Fit = true, ZIndex = 5, Parent = holder })
	end
	if not locked then
		UI.art("gem_" .. r, { Size = UDim2.fromOffset(24, 24), Position = UDim2.fromOffset(8, 8), Fit = true, ZIndex = 6, Parent = f })
	end
	-- множитель броска
	if item and item.m and item.m > 1.01 then
		local ti = Theme.tier(Config.tierIndex(item.m))
		local mb = UI.label({ Text = Num.mult(item.m), TextSize = 18, Color = ti.color, Size = UDim2.fromOffset(64, 24), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -8, 0, 8), XAlign = Enum.TextXAlignment.Right, ZIndex = 7, Parent = f })
		mb.Rotation = 8
	end
	local ny = 12 + ph
	UI.label({ Text = if locked then "???" else (if sp then sp.name else spId), TextSize = 18, Size = UDim2.new(1, -12, 0, 22), Position = UDim2.fromOffset(6, ny), ZIndex = 6, Scaled = true, MaxSize = 18, Parent = f })
	if item and not locked then
		local mult = if item.wrapped then Config.WRAP_MULT else 1
		UI.label({ Text = Num.weight(item.w), TextSize = 14, Color = C.dim, Size = UDim2.new(1, -12, 0, 18), Position = UDim2.fromOffset(6, ny + 22), Stroke = 2, ZIndex = 6, Parent = f })
		iconLine(f, "ic_coin", Num.short(item.price * mult), 16, C.gold, { Center = true, Size = UDim2.new(1, -12, 0, 24), Position = UDim2.fromOffset(6, ny + 40), ZIndex = 6 })
	elseif o.count and not locked then
		UI.label({ Text = "Caught: " .. tostring(o.count), TextSize = 14, Color = C.dim, Size = UDim2.new(1, -12, 0, 18), Position = UDim2.fromOffset(6, ny + 24), Stroke = 2, ZIndex = 6, Parent = f })
	elseif locked and sp then
		UI.label({ Text = Config.ZONES[sp.zone].name, TextSize = 14, Color = C.dim, Size = UDim2.new(1, -12, 0, 18), Position = UDim2.fromOffset(6, ny + 24), Stroke = 2, ZIndex = 6, Parent = f })
	end
	-- мутация
	if item and item.mut and not locked then
		local mt = Config.MUTATIONS[item.mut]
		local mb = UI.panel({ Color = mt.color, Size = UDim2.fromOffset(10, 22), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 0, ny - 4), Radius = 10, LineThick = 2, ZIndex = 7, Parent = f })
		mb.AutomaticSize = Enum.AutomaticSize.X
		UI.pad(6, 0).Parent = mb
		UI.label({ Text = string.upper(mt.name) .. " ×" .. mt.mult, TextSize = 14, Size = UDim2.new(0, 10, 1, 0), AutoX = true, ZIndex = 8, Stroke = 2, Parent = mb })
	end
	if item and item.wrapped then
		UI.art("p_rope", { Size = UDim2.fromOffset(30, 26), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -8, 0, 12 + ph), Fit = true, ZIndex = 7, Parent = f })
	end
	if o.selected then
		local sel = Instance.new("Frame")
		sel.BackgroundTransparency = 1
		sel.Size = UDim2.fromScale(1, 1)
		sel.ZIndex = 9
		UI.corner(18).Parent = sel
		UI.stroke(Color3.new(1, 1, 1), 4, 0, true).Parent = sel
		sel.Parent = f
	end
	if o.onClick then
		local b = Instance.new("TextButton")
		b.BackgroundTransparency = 1
		b.Text = ""
		b.Size = UDim2.fromScale(1, 1)
		b.ZIndex = 10
		b.Parent = f
		local sc = Instance.new("UIScale")
		sc.Parent = f
		b.MouseEnter:Connect(function()
			UI.tween(sc, 0.12, { Scale = 1.05 }, Enum.EasingStyle.Back)
		end)
		b.MouseLeave:Connect(function()
			UI.tween(sc, 0.12, { Scale = 1 })
		end)
		b.Activated:Connect(function()
			sc.Scale = 0.92
			UI.tween(sc, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
			local cb = o.onClick
			if cb then
				task.spawn(cb)
			end
		end)
	end
	if o.parent then
		f.Parent = o.parent
	end
	return f
end

-- иконки наград/бонусов
local BOOST_ART: { [string]: string } = { luck = "potion_clover", coins = "potion_coin", range = "potion_bow", tension = "potion_arm" }

-- Копьё во вьюпорте (наискосок)
local swayers: { { vp: ViewportFrame, model: Model, base: CFrame, speed: number, t: number } } = {}
local swayAcc = 0
RunService.RenderStepped:Connect(function(dt)
	swayAcc += dt
	if swayAcc < 1 / 30 then
		return
	end
	local step = math.min(swayAcc, 0.1)
	swayAcc = 0
	for i = #swayers, 1, -1 do
		local s = swayers[i]
		if not s.vp.Parent or not s.model.Parent then
			table.remove(swayers, i)
		elseif s.vp.AbsoluteSize.X > 0 then
			-- за пределами прокручиваемого списка модель не двигаем
			local sc = s.vp:FindFirstAncestorWhichIsA("ScrollingFrame")
			local seen = true
			if sc then
				local p, z = s.vp.AbsolutePosition, s.vp.AbsoluteSize
				seen = p.Y + z.Y >= sc.AbsolutePosition.Y and p.Y <= sc.AbsolutePosition.Y + sc.AbsoluteSize.Y
			end
			if seen then
				s.t += step * s.speed
				s.model:PivotTo(CFrame.Angles(0, math.sin(s.t) * 0.85, 0) * s.base)
			end
		end
	end
end)
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
	local vp = UI.viewport(holder, nil, math.rad(20), 0) -- сам вьюпорт не вращает: ниже модель качается
	vp.Parent = parent
	holder:Destroy()
	-- V58: плоская модель копья (толщина два кубика) при полном вращении поворачивалась ребром и была видна как нитка, кроме того
	-- вращалась по кругу вокруг точки хвата. Теперь она стоит по центру и качается на ±49° вокруг вертикальной оси.
	local m = vp:FindFirstChildOfClass("Model")
	if m then
		local bb = m:GetBoundingBox()
		m:PivotTo(CFrame.new(-bb.Position) * m:GetPivot())
		table.insert(swayers, { vp = vp, model = m, base = m:GetPivot(), speed = (spin or 0.6) * 2, t = math.random() * 6.28 })
	end
	return vp
end
Menus.spearView = spearView

local function stars(n: number, max: number): string
	if n > max then return "★ " .. tostring(n) end
	return string.rep("★", math.max(0,n)) .. string.rep("☆", math.max(0,max - n))
end

---------------------------------------------------------------------
-- Сумка: вкладки «Catch» (улов, страницы по 12) и «Pets» (питомцы, страницы по 6)
---------------------------------------------------------------------
local function itemValue(it: any): number
	return it.price * (it.wrapped and Config.WRAP_MULT or 1)
end

local function renderCatch(body: Frame, st: { [string]: any })
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
	local top = row(body, 50)
	top.Position = UDim2.fromOffset(0, 58)
	statCell(top, UDim2.fromOffset(190, 50), 50, "ic_bag2", string.format("%d / %d", #items, d.bagCap), 22, UDim2.fromOffset(0, 0))
	statCell(top, UDim2.fromOffset(240, 50), 50, "ic_coin", Num.short(mq * Backend.boostMult("coins")), 22, UDim2.fromOffset(200, 0))
	if market then
		local n = 0
		for _, it in items do
			if st.sel[it.id] then
				n += 1
			end
		end
		local b = glossy("btn_yellow", 230, 48, { Icon = "ic_sell", Text = n > 0 and ("Sell (" .. n .. ")") or "Sell All", TextSize = 22, AnchorPoint = Vector2.new(1, 0), Position = UDim2.fromScale(1, 0), Parent = top }, function()
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
				UI.toast(string.format("Sold %d for %s coins", cnt, Num.short(gain)), "gold")
				Menus.refresh()
			end
		end)
		UI.setEnabled(b, #items > 0)
	else
		iconLine(top, "ic_coin", "Sell your catch at the Market", 18, C.dim, { Size = UDim2.new(0.4, 0, 1, 0), Position = UDim2.fromScale(0.6, 0), ZIndex = 4 })
	end
	local per = 12
	local pages = math.max(1, math.ceil(#items / per))
	st.page = math.clamp(st.page, 1, pages)
	local grid = Instance.new("Frame")
	grid.BackgroundTransparency = 1
	grid.Size = UDim2.new(1, 0, 0, 370)
	grid.Position = UDim2.fromOffset(0, 116)
	grid.ZIndex = 3
	grid.Parent = body
	local g = UI.grid(Vector2.new(140, 180), 10)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = grid
	if #items == 0 then
		-- V42: не внутри сетки (UIGridLayout сжимал текст до ширины ячейки): отдельная подпись по центру окна
		txt(body, "Your bag is empty. Head to the forest hide and throw your spear!", 24, C.dim, { XAlign = Enum.TextXAlignment.Center, YAlign = Enum.TextYAlignment.Center, Size = UDim2.new(1, -40, 0, 90), Position = UDim2.new(0, 20, 0, 200), Wrap = true })
	end
	for i = (st.page - 1) * per + 1, math.min(#items, st.page * per) do
		local it = items[i]
		animalCard(it.sp, it, { w = 140, h = 180, selected = st.sel[it.id] == true, layoutOrder = i, parent = grid, onClick = market and function()
			st.sel[it.id] = not st.sel[it.id] or nil
			Sfx.play("select") -- V42: свой звук выбора карточки (раньше общий press)
			Menus.refresh()
		end or nil })
	end
	chipRow(body, marketChips(now, mflags, total, mq), 34, UDim2.new(1, 0, 0, 80), UDim2.fromOffset(0, 490))
	pager(body, st, "page", pages)
end

-- вкладка питомцев: сетка 3x2 карточек card_N по редкости питомца
local function renderPets(body: Frame, st: { [string]: any })
	local shop = petShop()
	local list: { any } = {}
	local eq, mx = 0, 3
	if shop then
		local ok, res = pcall(shop.petList)
		if ok and type(res) == "table" then
			list = res
		end
		local ok2, a, b = pcall(shop.petEquipped)
		if ok2 and type(a) == "number" and type(b) == "number" then
			eq, mx = a, b
		end
	end
	local pill = UI.art("pill_dark", { Name = "EquippedPill", Size = UDim2.fromOffset(230, 44), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, 0, 0, 3), Slice = { 30, 0, 30, 0 }, SliceScale = 44 / 65, ZIndex = 3, Parent = body })
	iconLine(pill, "ic_paw", string.format("Equipped %d/%d", eq, mx), 20, nil, { Center = true, Size = UDim2.fromScale(1, 1), ZIndex = 4 })
	if #list == 0 then
		txt(body, "No pets yet. Hatch an egg in the Shop!", 26, C.dim, { XAlign = Enum.TextXAlignment.Center, YAlign = Enum.TextYAlignment.Center, Size = UDim2.new(1, -40, 0, 60), Position = UDim2.new(0, 20, 0, 190), Wrap = true })
		glossy("btn_green", 260, 60, { Text = "Open Shop", TextSize = 26, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 270), Parent = body }, function()
			Menus.shop()
		end)
		return
	end
	local per = 6
	local pages = math.max(1, math.ceil(#list / per))
	st.ppage = math.clamp(st.ppage or 1, 1, pages)
	local grid = Instance.new("Frame")
	grid.BackgroundTransparency = 1
	grid.Size = UDim2.new(1, 0, 0, 510)
	grid.Position = UDim2.fromOffset(0, 58)
	grid.ZIndex = 3
	grid.Parent = body
	local g = UI.grid(Vector2.new(290, 250), 12)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = grid
	for i = (st.ppage - 1) * per + 1, math.min(#list, st.ppage * per) do
		local p = list[i]
		local card = Instance.new("Frame")
		card.Name = "Pet_" .. tostring(p.id)
		card.BackgroundTransparency = 1
		card.LayoutOrder = i
		card.ZIndex = 3
		card.Parent = grid
		UI.art("card_" .. math.clamp(p.rarity, 1, 7), { Name = "Frame", Size = UDim2.fromScale(1, 1), Slice = 40, SliceScale = 0.9, ZIndex = 3, Parent = card })
		local holder = Instance.new("Frame")
		holder.BackgroundTransparency = 1
		holder.Size = UDim2.fromOffset(240, 108)
		holder.Position = UDim2.fromOffset(25, 14)
		holder.ZIndex = 4
		holder.Parent = card
		local vp = shop and shop.petPortrait(holder, p.id)
		if not vp then
			UI.art("ic_paw", { Size = UDim2.fromScale(1, 1), Fit = true, ZIndex = 5, Parent = holder })
		end
		UI.label({ Text = tostring(p.name) .. ((p.owned or 1) > 1 and (" ×" .. tostring(p.owned)) or ""), TextSize = 24, Size = UDim2.new(1, -20, 0, 28), Position = UDim2.fromOffset(10, 124), ZIndex = 6, Scaled = true, MaxSize = 24, Parent = card })
		local lv = UI.art("pill_dark", { Size = UDim2.fromOffset(96, 24), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(145, 154), Slice = { 30, 0, 30, 0 }, SliceScale = 24 / 65, ZIndex = 5, Parent = card })
		iconLine(lv, "ic_star", "Lv." .. tostring(p.level), 15, nil, { Center = true, Size = UDim2.fromScale(1, 1), ZIndex = 6 })
		local fx = UI.label({ Text = tostring(p.fx or ""), TextSize = 14, Color = C.dim, Size = UDim2.new(1, -28, 0, 18), Position = UDim2.fromOffset(14, 180), Stroke = 2, ZIndex = 6, Parent = card })
		fx.TextTruncate = Enum.TextTruncate.AtEnd
		local busy = st.busy == true
		local btn
		local function toggle()
			if st.busy or not shop then
				return
			end
			st.busy = true
			UI.setEnabled(btn, false)
			local ok = shop.petToggle(p.id)
			st.busy = false
			if ok then
				Sfx.play("equip")
			else
				UI.toast("Could not change this pet", "bad")
				Sfx.play("error")
			end
			Menus.refresh()
		end
		if p.equipped then
			btn = glossy("btn_green", 220, 38, { Icon = "p_check", Text = "Equipped", TextSize = 20, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(145, 204), Parent = card }, toggle)
		else
			btn = glossy("btn_blue", 220, 38, { Icon = "ic_bagup", Text = "Equip", TextSize = 20, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(145, 204), Parent = card }, toggle)
		end
		UI.setEnabled(btn, not busy)
	end
	pager(body, st, "ppage", pages)
	glossy("btn_purple", 200, 44, { Icon = "ic_paw", Text = "Collection", TextSize = 20, AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(1, 1), Parent = body }, function()
		local sh = petShop()
		if sh then
			sh.openPets()
		else
			UI.toast("The collection is unavailable right now", "warn")
		end
	end)
end

local function renderBag(body: Frame, st: { [string]: any })
	if not Backend.data then
		return
	end
	st.tab = st.tab or "catch"
	local function mk(key: string, icon: string, text: string, x: number)
		tabBtn(body, st.tab == key, 200, 50, icon, text, 24, function()
			if st.tab ~= key then
				st.tab = key
				Menus.refresh()
			end
		end, UDim2.fromOffset(x, 0))
	end
	mk("catch", "ic_net", "Catch", 0)
	mk("pets", "ic_paw", "Pets", 208)
	if st.tab == "pets" then
		renderPets(body, st)
	else
		renderCatch(body, st)
	end
end

function Menus.bag()
	show("bag", "🎒 Bag", Vector2.new(940, 690), C.orange, renderBag)
end

---------------------------------------------------------------------
-- Копья: магазин + выбор
---------------------------------------------------------------------
local function spearStatsText(id: string, lvl: number): string
	local s = Config.spearStats(id, lvl)
	-- V58: дальность и шанс с учётом постоянных бонусов питомцев-экзотики (дальность броска и хват), как в настоящем броске
	local rangeMul, gripMul = Perks.rangeMul(), Perks.gripMul()
	local rangeText = string.format("%.2f", s.range * rangeMul)
	if math.abs(rangeMul - 1) > 0.005 then
		rangeText ..= string.format(" (%+d%%)", math.floor((rangeMul - 1) * 100 + 0.5))
	end
	return string.format("Sharpness %s  ·  Power %s\nLuck ×%.1f  ·  Range ×%s\nChance to reach ×10: %s", stars(s.sharp, 6), stars(s.heavy, 5), s.luck, rangeText, Num.odds(Roll.reachChance(10, s.alpha * gripMul)))
end

local function renderSpears(body: Frame, st: { [string]: any })
	local d = Backend.data
	if not d then
		return
	end
	local pageSize = 6
	local pages = math.ceil(#Config.SPEARS / pageSize)
	st.page = math.clamp(st.page or 1, 1, pages)
	local sc = UI.scroll(body, UDim2.new(1, 0, 1, -58))
	UI.list(Enum.FillDirection.Vertical, 10).Parent = sc
	UI.pad(4, 4).Parent = sc
	for i = (st.page - 1) * pageSize + 1, math.min(st.page * pageSize, #Config.SPEARS) do
		local s = Config.SPEARS[i]
		local owned = d.spears[s.id] ~= nil
		local lvl = d.spears[s.id] or 0
		local inHand = d.spear == s.id
		local rowF = UI.art("row_slate", { Name = "Spear_" .. s.id, Size = UDim2.new(1, -16, 0, 128), Slice = 24, SliceScale = 0.8, Color = if inHand then Color3.fromRGB(160, 235, 175) else nil, LayoutOrder = i, ZIndex = 3, Parent = sc })
		local vpH = Instance.new("Frame")
		vpH.BackgroundTransparency = 1
		vpH.Size = UDim2.fromOffset(120, 120)
		vpH.Position = UDim2.fromOffset(6, 4)
		vpH.ZIndex = 4
		vpH.Parent = rowF
		-- V50: модель копья (сотни деталей) строится по одной на кадр, а не шесть сразу: окно открывалось за ~250 мс
		local spinSpeed = inHand and 1.2 or 0.4
		task.delay(0.04 * (i - (st.page - 1) * pageSize - 1), function()
			if vpH.Parent then
				spearView(s.id, vpH, spinSpeed)
			end
		end)
		UI.label({ Text = s.name .. (owned and lvl > 0 and ("  +" .. lvl) or ""), TextSize = 28, Size = UDim2.new(0.5, 0, 0, 34), Position = UDim2.fromOffset(134, 6), XAlign = Enum.TextXAlignment.Left, Color = s.trail[1]:Lerp(Color3.new(1, 1, 1), 0.4), ZIndex = 4, Parent = rowF })
		UI.label({ Text = spearStatsText(s.id, lvl), TextSize = 17, Size = UDim2.new(0.55, 0, 0, 66), Position = UDim2.fromOffset(134, 40), XAlign = Enum.TextXAlignment.Left, YAlign = Enum.TextYAlignment.Top, Color = C.dim, Stroke = 2, ZIndex = 4, Parent = rowF })
		UI.label({ Text = s.desc, TextSize = 15, Size = UDim2.new(0.55, 0, 0, 20), Position = UDim2.fromOffset(134, 104), XAlign = Enum.TextXAlignment.Left, Color = C.gray, Stroke = 2, ZIndex = 4, Parent = rowF })
		local pos, anchor = UDim2.new(1, -14, 0.5, 0), Vector2.new(1, 0.5)
		local b: ImageButton
		if inHand then
			b = glossy("btn_green", 190, 56, { Icon = "p_check", Text = "Equipped", TextSize = 24, AnchorPoint = anchor, Position = pos, Parent = rowF })
			UI.setEnabled(b, false)
		elseif owned then
			b = glossy("btn_blue", 190, 56, { Text = "Equip", TextSize = 24, AnchorPoint = anchor, Position = pos, Parent = rowF }, function()
				if call("EquipSpear", s.id) then
					Sfx.play("equip")
				end
			end)
		else
			local can = d.coins >= s.price
			b = glossy(if can then "btn_green" else "btn_grey", 190, 56, { Price = Num.short(s.price), TextSize = 24, AnchorPoint = anchor, Position = pos, Parent = rowF }, function()
				local ok = call("BuySpear", s.id)
				if ok then
					Sfx.play("buy")
					UI.confetti(40, { s.trail[1], s.trail[2], C.gold })
					Hud.banner("NEW SPEAR!", C.gold, s.name, 2)
					if Backend.data.tutorial == 4 then
						Backend.call("Tutorial", 5)
					end
				end
			end)
			UI.setEnabled(b, can)
		end
	end
	local footer = row(body, 48)
	footer.Position = UDim2.new(0, 0, 1, -48)
	pager(footer, st, "page", pages)
	UI.label({ Text = string.format("%d spears", #Config.SPEARS), TextSize = 20, Color = C.dim, Size = UDim2.fromOffset(200, 42), AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(1, 1), XAlign = Enum.TextXAlignment.Right, ZIndex = 4, Parent = footer })
end

function Menus.spears()
	show("spears", "🔱 Spears", Vector2.new(880, 660), C.blue, renderSpears)
end

---------------------------------------------------------------------
-- Кузница: улучшение текущего копья (0..5)
---------------------------------------------------------------------
local function renderForge(body: Frame, _st: { [string]: any })
	local d = Backend.data
	if not d then
		return
	end
	local id = d.spear
	local s = Config.SPEAR_BY_ID[id]
	local lvl = d.spears[id] or 0
	local maxL = Perks.forgeMax()
	-- подложка под копьём
	UI.art("cell_dark", { Name = "SpearBack", Size = UDim2.new(0.42, 0, 1, 0), Slice = 30, SliceScale = 0.8, ZIndex = 2, Parent = body })
	local left = Instance.new("Frame")
	left.BackgroundTransparency = 1
	left.Size = UDim2.new(0.42, 0, 1, 0)
	left.ZIndex = 4
	left.Parent = body
	spearView(id, left, 1)
	-- звёзды уровня: залитые ic_star до lvl, остальные потемнены
	local starRow = Instance.new("Frame")
	starRow.BackgroundTransparency = 1
	starRow.Size = UDim2.new(1, 0, 0, 44)
	starRow.Position = UDim2.new(0, 0, 1, -52)
	starRow.ZIndex = 5
	starRow.Parent = left
	UI.list(Enum.FillDirection.Horizontal, 4, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = starRow
	for i = 1, maxL do
		UI.art("ic_star", { Size = UDim2.fromOffset(38, 38), Fit = true, LayoutOrder = i, Color = if i <= lvl then nil else Color3.fromRGB(70, 74, 84), Transparency = if i <= lvl then 0 else 0.25, ZIndex = 6, Parent = starRow })
	end
	local right = Instance.new("Frame")
	right.BackgroundTransparency = 1
	right.Size = UDim2.new(0.56, 0, 1, 0)
	right.Position = UDim2.fromScale(0.44, 0)
	right.ZIndex = 3
	right.Parent = body
	UI.list(Enum.FillDirection.Vertical, 8).Parent = right
	txt(right, s.name .. "  +" .. lvl, 34, C.text, { LayoutOrder = 1 })
	local a, b = Config.spearStats(id, lvl), Config.spearStats(id, math.min(maxL, lvl + 1))
	local function cmp(name: string, icon: string, x: string, y: string, order: number)
		local r = UI.art("row_slate", { Size = UDim2.new(1, 0, 0, 48), Slice = 24, SliceScale = 0.6, LayoutOrder = order, ZIndex = 3, Parent = right })
		iconLine(r, icon, string.format("%s: <b>%s</b>%s", name, x, lvl < maxL and ("  →  <font color=\"#7CFF8A\">" .. y .. "</font>") or ""), 20, C.text, { Rich = true, Size = UDim2.new(1, -24, 1, 0), Position = UDim2.fromOffset(14, 0), ZIndex = 4 })
	end
	cmp("Luck", "ic_star", string.format("×%.2f", a.luck), string.format("×%.2f", b.luck), 2)
	cmp("Range", "p_target", string.format("×%.2f", a.range), string.format("×%.2f", b.range), 3)
	cmp("Reach ×10", "ic_spear", Num.odds(Roll.reachChance(10, a.alpha)), Num.odds(Roll.reachChance(10, b.alpha)), 4)
	cmp("Reach ×25", "ic_spear", Num.odds(Roll.reachChance(25, a.alpha)), Num.odds(Roll.reachChance(25, b.alpha)), 5)
	if lvl >= maxL then
		txt(right, lvl >= Config.FORGE.maxLevel and "This spear is fully upgraded!" or "Free forge limit reached. Master Smith (Shop) unlocks 2 more levels.", 24, C.gold, { LayoutOrder = 6, Wrap = true, Size = UDim2.new(1, 0, 0, 60) })
		return
	end
	local cost = Perks.forgeCost(id, lvl)
	local can = d.coins >= cost
	local holder = row(right, 64, 7)
	local btn = glossy(if can then "btn_orange" else "btn_grey", 340, 60, { Text = "Upgrade", Price = Num.short(cost), TextSize = 26, Parent = holder }, function()
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
	UI.setEnabled(btn, can)
	txt(right, "Upgrades stay with each spear. Equip any spear you own to upgrade it.", 17, C.gray, { LayoutOrder = 8, Wrap = true, Size = UDim2.new(1, 0, 0, 50) })
end

function Menus.forge()
	show("forge", "🔨 Forge", Vector2.new(840, 480), C.orange, renderForge)
end

---------------------------------------------------------------------
-- Рынок: продажа + сумка побольше
---------------------------------------------------------------------
local function renderMarket(body: Frame, _st: { [string]: any })
	local d = Backend.data
	if not d then
		return
	end
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
	local W = UDim2.new(0.5, -8, 0, 64)
	statCell(body, W, 64, "ic_bag2", string.format("In your bag: <b>%d</b>%s", #d.items, wrapped > 0 and (" (wrapped: " .. wrapped .. ")") or ""), 24, UDim2.fromOffset(0, 0))
	statCell(body, W, 64, "ic_coin", string.format("Value: <font color=\"#FFCC34\">%s coins</font>%s", Num.short(mq * cm), cm > 1 and " (×2!)" or ""), 24, UDim2.new(0.5, 8, 0, 0))
	local sell = glossy("btn_yellow", 366, 64, { Icon = "ic_sell", Text = "Sell All", TextSize = 30, Position = UDim2.fromOffset(0, 78), Parent = body }, function()
		local ok, gain, cnt = call("Sell", "all")
		if ok then
			Sfx.play("buy")
			for i = 1, math.min(8, cnt) do
				task.delay(i * 0.06, function()
					Sfx.play("coin", 1.6 + i * 0.05, 0.4)
				end)
			end
			Hud.flyCoins(UI.screenPos(body), gain)
			Hud.banner("+" .. Num.short(gain) .. " coins", C.gold, "Sold: " .. cnt, 1.8)
			if Backend.data.tutorial == 3 then
				Backend.call("Tutorial", 4)
			end
		end
	end)
	sell.AnchorPoint = Vector2.new(0, 0)
	UI.setEnabled(sell, #d.items > 0)
	local pick = glossy("btn_blue", 366, 64, { Text = "Select", TextSize = 30, AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, 0, 0, 78), Parent = body }, function()
		Menus.bag()
	end)
	UI.setEnabled(pick, #d.items > 0)
	chipRow(body, marketChips(now, mflags, total, mq), 40, UDim2.new(1, 0, 0, 136), UDim2.fromOffset(0, 156))
	local nxt = Config.BAG[d.bagLvl + 1]
	local r2 = UI.art("row_slate", { Name = "BagUpgrade", Size = UDim2.new(1, 0, 0, 96), AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0, 1), Slice = 24, SliceScale = 0.9, ZIndex = 3, Parent = body })
	UI.art("ic_bagup", { Size = UDim2.fromOffset(80, 84), Position = UDim2.fromOffset(12, 6), Fit = true, ZIndex = 4, Parent = r2 })
	if nxt then
		UI.label({ Text = string.format("Bigger bag: %d → <b>%d</b> slots", d.bagCap, d.bagCap + nxt.cap - (Config.BAG[d.bagLvl] and Config.BAG[d.bagLvl].cap or nxt.cap)), Rich = true, TextSize = 26, Size = UDim2.new(0.6, -100, 1, 0), Position = UDim2.fromOffset(100, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = r2 })
		local can = d.coins >= nxt.cost
		local b = glossy(if can then "btn_yellow" else "btn_grey", 190, 58, { Price = Num.short(nxt.cost), TextSize = 26, AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -16, 0.5, 0), Parent = r2 }, function()
			if call("BuyBag") then
				Sfx.play("buy")
				Hud.banner("BIGGER BAG!", C.green, Backend.data.bagCap .. " slots", 1.6)
			end
		end)
		UI.setEnabled(b, can)
	else
		UI.label({ Text = "Maximum bag capacity: " .. d.bagCap .. " slots", TextSize = 26, Size = UDim2.new(1, -120, 1, 0), Position = UDim2.fromOffset(100, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = r2 })
	end
end

function Menus.market()
	show("market", "💰 Market", Vector2.new(780, 520), C.gold, renderMarket)
end

---------------------------------------------------------------------
-- Коллекция: 24 вида по зонам, силуэты непойманных
---------------------------------------------------------------------
local function detail(parent: Frame, sp: any, rec: any)
	local sr = math.clamp(sp.rarity, 1, 6)
	local rar = Config.RARITIES[sr]
	local ov = UI.art("cell_dark", { Name = "Detail", Size = UDim2.fromScale(1, 1), Slice = 30, SliceScale = 0.8, ZIndex = 20, Parent = parent })
	-- кликом по пустому месту подложка не пропускает нажатия в сетку
	local blocker = Instance.new("TextButton")
	blocker.BackgroundTransparency = 1
	blocker.Text = ""
	blocker.Size = UDim2.fromScale(1, 1)
	blocker.ZIndex = 21
	blocker.Parent = ov
	local vpH = Instance.new("Frame")
	vpH.BackgroundTransparency = 1
	vpH.Size = UDim2.new(0.42, 0, 1, -40)
	vpH.Position = UDim2.fromOffset(20, 20)
	vpH.ZIndex = 22
	vpH.Parent = ov
	local model = Card.model(sp.id, rec and (rec.rainbow and "rainbow" or (rec.gold and "gold" or nil)) or nil)
	if model then
		local vp = UI.viewport(model, nil, math.rad(-30), 0.8)
		vp.Parent = vpH
	end
	local info = Instance.new("Frame")
	info.BackgroundTransparency = 1
	info.Size = UDim2.new(0.55, 0, 1, -40)
	info.Position = UDim2.new(0.44, 0, 0, 20)
	info.ZIndex = 22
	info.Parent = ov
	UI.list(Enum.FillDirection.Vertical, 6).Parent = info
	txt(info, sp.name, 36, rar.color, { LayoutOrder = 1, ZIndex = 23 })
	iconLine(info, "gem_" .. sr, rar.name .. "  ·  " .. Config.ZONES[sp.zone].name, 22, C.dim, { LayoutOrder = 2, ZIndex = 23 })
	txt(info, "«" .. sp.fact .. "»", 20, C.text, { LayoutOrder = 3, Wrap = true, Size = UDim2.new(1, 0, 0, 52), ZIndex = 23 })
	txt(info, string.format("Caught: <b>%d</b>   ·   Best: <b>%s</b>", rec.n, Num.weight(rec.best)), 22, C.text, { LayoutOrder = 4, ZIndex = 23 })
	iconLine(info, "ic_coin", "Best value: " .. Num.short(rec.bestPrice), 22, C.gold, { LayoutOrder = 5, ZIndex = 23 })
	iconLine(info, "p_aura", rec.gold and "Gold discovered" or "Gold undiscovered", 20, if rec.gold then C.gold else C.dim, { LayoutOrder = 6, ZIndex = 23 })
	iconLine(info, "p_aura", rec.rainbow and "Rainbow discovered" or "Rainbow undiscovered", 20, if rec.rainbow then C.pink else C.dim, { LayoutOrder = 7, ZIndex = 23 })
	iconLine(info, "ic_spear", "Required spear: “" .. Roll.spearFor(sp).name .. "»", 20, C.cyan, { LayoutOrder = 8, ZIndex = 23 })
	glossy("btn_blue", 140, 48, { Text = "Back", TextSize = 22, AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -14, 1, -14), Parent = ov, Name = "Back" }, function()
		ov:Destroy()
	end).ZIndex = 24
end

local function renderIndex(body: Frame, st: { [string]: any })
	local d = Backend.data
	if not d then
		return
	end
	st.zone = st.zone or 1
	local total, got = #Config.SPECIES, 0
	for _ in d.index do
		got += 1
	end
	local tabs = Instance.new("ScrollingFrame")
	tabs.Name = "BiomeTabs"
	tabs.BackgroundTransparency = 1
	tabs.BorderSizePixel = 0
	tabs.Size = UDim2.new(1, 0, 0, 54)
	tabs.ScrollingDirection = Enum.ScrollingDirection.X
	tabs.AutomaticCanvasSize = Enum.AutomaticSize.X
	tabs.CanvasSize = UDim2.new()
	tabs.ScrollBarThickness = 5
	tabs.ScrollBarImageColor3 = C.gold
	tabs.ZIndex = 3
	tabs.Parent = body
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
		tabBtn(tabs, st.zone == z, 220, 48, nil, zc.name .. " " .. n .. "/" .. all, 18, function()
			st.zone = z
			Menus.refresh()
		end, nil, z)
	end
	local sc = UI.scroll(body, UDim2.new(1, 0, 1, -106), UDim2.fromOffset(0, 60))
	local g = UI.grid(Vector2.new(140, 186), 10)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = sc
	UI.pad(4, 4).Parent = sc
	for _, sp in Config.SPECIES do
		if sp.zone == st.zone then
			local rec = d.index[sp.id]
			animalCard(sp.id, nil, { w = 140, h = 186, locked = rec == nil, count = rec and rec.n or nil, layoutOrder = sp.rarity, parent = sc, spin = rec and 0.5 or nil, onClick = rec and function()
				detail(body, sp, rec)
			end or nil })
		end
	end
	local bar = UI.bar({ Size = UDim2.new(1, -20, 0, 26), Position = UDim2.new(0, 10, 1, -32), Color = C.gold, TextSize = 18, Parent = body })
	bar.set(got / total, string.format("Collection: %d / %d", got, total))
end

function Menus.index()
	show("index", "📖 Collection", Vector2.new(940, 680), C.purple, renderIndex)
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

-- награда задания строкой из иконок (монеты, опыт, зелье)
local function rewardRow(parent: Instance, r: any, ts: number, size: UDim2, pos: UDim2)
	local f = Instance.new("Frame")
	f.BackgroundTransparency = 1
	f.Size = size
	f.Position = pos
	f.ZIndex = 4
	f.Parent = parent
	UI.list(Enum.FillDirection.Horizontal, 14, Enum.HorizontalAlignment.Left, Enum.VerticalAlignment.Center).Parent = f
	if r.coins then
		iconLine(f, "ic_coin", Num.short(r.coins), ts, C.gold, { AutoX = true, LayoutOrder = 1, ZIndex = 4 })
	end
	if r.xp then
		iconLine(f, "ic_star", r.xp .. " XP", ts, C.gold, { AutoX = true, LayoutOrder = 2, ZIndex = 4 })
	end
	if r.boost then
		local b = Config.BOOSTS[r.boost]
		iconLine(f, BOOST_ART[r.boost] or "ic_potion", b.name .. " " .. Num.time(r.dur or 120), ts, C.gold, { AutoX = true, LayoutOrder = 3, ZIndex = 4 })
	end
end

local function renderQuests(body: Frame, _st: { [string]: any })
	local d = Backend.data
	if not d then
		return
	end
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
		txt(sc, "All quests complete! You are a forest legend", 26, C.gold)
	end
	for i, e in list do
		local q, s = e.q, e.st
		local npc = Config.NPC[q.npc]
		local f = UI.art("row_slate", { Name = "Quest_" .. tostring(q.id), Size = UDim2.new(1, -16, 0, 116), Slice = 24, SliceScale = 0.9, Color = if s.done then Color3.fromRGB(160, 235, 175) else nil, LayoutOrder = i, ZIndex = 3, Parent = sc })
		UI.art("ic_quests", { Size = UDim2.fromOffset(66, 72), Position = UDim2.fromOffset(14, 22), Fit = true, ZIndex = 4, Parent = f })
		UI.label({ Text = q.title, TextSize = 28, Size = UDim2.new(0.55, 0, 0, 32), Position = UDim2.fromOffset(96, 6), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = f })
		UI.label({ Text = (npc and npc.name or "") .. ": " .. q.text, TextSize = 18, Color = C.dim, Size = UDim2.new(0.58, 0, 0, 24), Position = UDim2.fromOffset(96, 38), XAlign = Enum.TextXAlignment.Left, Stroke = 2, ZIndex = 4, Parent = f })
		rewardRow(f, q.reward, 18, UDim2.new(0.58, 0, 0, 26), UDim2.fromOffset(96, 62))
		local bar = UI.bar({ Size = UDim2.new(0.55, 0, 0, 18), Position = UDim2.fromOffset(96, 92), Color = C.cyan, TextSize = 14, ZIndex = 4, Parent = f })
		bar.set(math.min(1, s.p / q.goal), Num.short(math.min(s.p, q.goal)) .. " / " .. Num.short(q.goal))
		local b = glossy(if s.done then "btn_yellow" else "btn_grey", 190, 56, { Text = s.done and "Claim!" or "In Progress", TextSize = 24, AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -14, 0.5, 0), Parent = f }, function()
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
	if not d then
		return
	end
	local g = UI.grid(Vector2.new(372, 190), 14)
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	g.Parent = body
	for i, p in Config.POTIONS do
		local b = Config.BOOSTS[p.boost]
		local pc = Config.potionCost(p, d)
		local f = UI.art("row_slate", { Name = "Potion_" .. p.boost, Size = UDim2.fromOffset(372, 190), Slice = 24, SliceScale = 1, LayoutOrder = i, ZIndex = 3, Parent = body })
		UI.art(BOOST_ART[p.boost] or "ic_potion", { Size = UDim2.fromOffset(92, 118), Position = UDim2.fromOffset(12, 14), Fit = true, ZIndex = 4, Parent = f })
		UI.label({ Text = b.name, TextSize = 26, Size = UDim2.new(1, -120, 0, 32), Position = UDim2.fromOffset(108, 14), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = f })
		local left = Backend.boostLeft(p.boost)
		iconLine(f, "p_clock", Num.time(p.dur), 19, C.dim, { Size = UDim2.new(1, -120, 0, 28), Position = UDim2.fromOffset(108, 52), ZIndex = 4 })
		if left > 0 then
			UI.label({ Text = "active: " .. Num.time(left), TextSize = 18, Color = C.green, Size = UDim2.new(1, -120, 0, 24), Position = UDim2.fromOffset(108, 84), XAlign = Enum.TextXAlignment.Left, Stroke = 2, ZIndex = 4, Parent = f })
		end
		local can = d.coins >= pc
		local btn = glossy(if can then "btn_green" else "btn_grey", 220, 54, { Price = Num.short(pc), TextSize = 24, AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -12), Parent = f }, function()
			if call("BuyPotion", i) then
				Sfx.play("buy")
				UI.flash(b.color, 0.3, 0.6)
				Hud.banner(b.name, b.color, "for " .. Num.time(p.dur), 1.6)
			end
		end)
		UI.setEnabled(btn, can)
	end
end

function Menus.potions()
	show("potions", "🧪 Herbalist Potions", Vector2.new(800, 480), C.pink, renderPotions)
end

---------------------------------------------------------------------
-- Настройки
---------------------------------------------------------------------
local function renderSettings(body: Frame, _st: { [string]: any })
	if not Backend.data then
		return
	end
	local s = Backend.data.settings
	UI.list(Enum.FillDirection.Vertical, 12).Parent = body
	local opts = {
		{ "music", "Music" },
		{ "sfx", "Sound Effects" },
		{ "skip", "Quick Catch Reveal" },
		{ "lowFx", "Reduced Effects (Better Performance)" },
	}
	for i, o in opts do
		local r = UI.art("row_slate", { Size = UDim2.new(1, 0, 0, 66), Slice = 24, SliceScale = 0.8, LayoutOrder = i, ZIndex = 3, Parent = body })
		UI.label({ Text = o[2], TextSize = 26, Scaled = true, MaxSize = 26, Size = UDim2.new(0.7, 0, 1, 0), Position = UDim2.fromOffset(18, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = r })
		local on = s[o[1]] == true
		glossy(if on then "btn_green" else "btn_red", 130, 50, { Text = on and "ON" or "OFF", TextSize = 22, Sound = on and "toggle_off" or "toggle_on", AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -12, 0.5, 0), Parent = r }, function()
			call("Settings", { [o[1]] = not on })
		end)
	end
	txt(body, "Spear Hunt v" .. Config.VERSION, 18, C.gray, { LayoutOrder = 9 })
end

function Menus.settings()
	show("settings", "⚙️ Settings", Vector2.new(640, 440), C.gray, renderSettings)
end

---------------------------------------------------------------------
-- Hunter Pass (боевой пропуск)
---------------------------------------------------------------------
local ROBUX = utf8.char(0xE002)
local PASS_STEP, PASS_TILE = 120, 112 -- шаг колонки и сторона плитки
local PASS_INK = Color3.fromRGB(86, 52, 22) -- тёмно-коричневый текст на кремовых строках
local passBusy: { [string]: boolean } = {} -- идущие запросы наград (переживают закрытие окна)
local PASS_BOOST_ART = { fortune20 = "p_potion", jackpot20 = "p_dice", fair30 = "p_fair" }
-- V74: зелья Травницы в наградах пропуска (те же картинки, что в окне Травницы)
local PASS_POTION_ART: { [string]: string } = { luck = "potion_clover", coins = "potion_coin", range = "potion_bow", tension = "potion_arm" }
local PASS_EGG_ART = { egg_forest = "p_egg_forest", egg_amber = "p_egg_amber", egg_storm = "p_egg_storm", egg_tide = "egg_tide" }
local MISSION_ART = { catch = "p_paw", zone = "p_paw", rarity = "p_paw", collect = "p_paw", train = "p_dumbbell", wrap = "p_rope", tier = "p_target", range = "p_target", sell = "p_coins", course = "p_clock" }

-- Shop.luau большой и грузится по требованию
local function getShop(): any
	local ok, shop = pcall(require, script.Parent.Shop)
	if ok and type(shop) == "table" then
		return shop
	end
	warn("[Pass] " .. tostring(shop))
	return nil
end

-- подпись: до 2 строк, размер не меньше 14
local function fitLabel(parent: Instance, text: string, maxSize: number, color: Color3?, props: { [string]: any }?): TextLabel
	local p: { [string]: any } = { Text = text, TextSize = maxSize, Scaled = true, MaxSize = maxSize, Color = color or C.text, Stroke = 2, Parent = parent }
	if props then
		for k, v in props do
			p[k] = v
		end
	end
	local l = UI.label(p)
	local c = l:FindFirstChildOfClass("UITextSizeConstraint")
	if c then
		c.MinTextSize = 14
	end
	return l
end

local function fmtLeft(sec: number): string
	sec = math.max(0, math.floor(sec))
	local dd, hh, mm = sec // 86400, (sec // 3600) % 24, (sec // 60) % 60
	if dd > 0 then
		return string.format("%dd %dh", dd, hh)
	elseif hh > 0 then
		return string.format("%dh %dm", hh, mm)
	end
	return string.format("%dm", mm)
end

-- P для монетных наград: цена самого дорогого купленного копья, не меньше цены первого покупного
local function passSpearPrice(d: any): number
	local best = if Config.SPEARS[2] then Config.SPEARS[2].price else 1
	for _, s in Config.SPEARS do
		if d and d.spears and d.spears[s.id] ~= nil and s.price > best then
			best = s.price
		end
	end
	return best
end

-- значки и короткая подпись награды (несколько предметов в одной плитке: несколько значков, подписи склеиваем)
local function passItemView(items: { any }, price: number): ({ string }, string)
	local icons, names = {}, {}
	for _, r in items do
		if r.type == "coins" then
			table.insert(icons, "p_coins")
			table.insert(names, "+" .. Num.short(math.ceil((tonumber(r.k) or 0) * price - 1e-9)) .. " Coins")
		elseif r.type == "power" then
			table.insert(icons, "p_power")
			table.insert(names, "+" .. Num.short(tonumber(r.n) or 0) .. " Strength")
		elseif r.type == "egg" then
			if Perks.state().eggsOff == true then
				-- V72: где яйца закрыты, сервер выдаёт вместо яйца монеты: плитка показывает то, что игрок получит
				table.insert(icons, "p_coins")
				table.insert(names, "Coin Pack")
			else
				local it = Config.SHOP_BY_KEY[r.key]
				table.insert(icons, PASS_EGG_ART[r.key] or "p_egg_forest")
				table.insert(names, it and it.name or "Egg")
			end
		elseif r.type == "boost" then
			local it = Config.SHOP_BY_KEY[r.key]
			table.insert(icons, PASS_BOOST_ART[r.key] or "p_potion")
			table.insert(names, it and it.name or "Boost")
		elseif r.type == "potion" then
			local b = Config.BOOSTS[r.boost]
			table.insert(icons, PASS_POTION_ART[r.boost] or "p_potion")
			table.insert(names, (b and b.name or "Potion") .. " " .. math.floor((tonumber(r.dur) or 0) / 60) .. "m")
		elseif r.type == "shards" then
			table.insert(icons, if UI.ART.p_shards then "p_shards" else "p_aura")
			table.insert(names, "+" .. tostring(r.n or 0) .. " Pet Shards")
		elseif r.type == "tag" then
			table.insert(icons, "p_tag")
			table.insert(names, tostring(r.text or "Tag"))
		elseif r.type == "aura" then
			table.insert(icons, "p_aura")
			table.insert(names, tostring(r.name or "Aura"))
		end
	end
	return icons, table.concat(names, " + ")
end

-- обратный отсчёт сезона для таблички: 27d 14h 36m
local function fmtEnds(sec: number): string
	sec = math.max(0, math.floor(sec))
	return string.format("%dd %dh %dm", sec // 86400, (sec // 3600) % 24, (sec // 60) % 60)
end

-- полоса с обрезанной заливкой: дорожка xp_track, поверх Frame шириной в долю с ClipsDescendants и xp_fill во всю ширину
local function passBar(parent: Instance, w: number, h: number, frac: number, text: string, textSize: number, pos: UDim2, z: number)
	local sl = { 22, 0, 22, 0 }
	local ss = h / 48
	UI.art("xp_track", { Name = "BarTrack", Size = UDim2.fromOffset(w, h), Position = pos, ZIndex = z, Slice = sl, SliceScale = ss, Parent = parent })
	local clip = Instance.new("Frame")
	clip.Name = "BarClip"
	clip.BackgroundTransparency = 1
	clip.BorderSizePixel = 0
	clip.ClipsDescendants = true
	clip.Size = UDim2.fromOffset(math.floor(w * math.clamp(frac, 0, 1)), h)
	clip.Position = pos
	clip.ZIndex = z + 1
	clip.Parent = parent
	UI.art("xp_fill", { Name = "BarFill", Size = UDim2.fromOffset(w, h), ZIndex = z + 1, Slice = sl, SliceScale = ss, Parent = clip })
	UI.label({ Name = "BarText", Text = text, TextSize = textSize, Size = UDim2.fromOffset(w, h), Position = pos, ZIndex = z + 3, Parent = parent })
end

local function renderPass(body: Frame, st: { [string]: any })
	local PASS: any = Config.PASS
	if type(PASS) ~= "table" or type(Config.passTier) ~= "function" or type(Config.passSeason) ~= "function" then
		UI.label({ Text = "Hunter Pass is not available right now", TextSize = 26, Size = UDim2.fromScale(1, 1), Parent = body })
		return
	end
	-- стандартное оформление окна убираем (идемпотентно: перерисовка его не возвращает), рисуем концепт сами
	local win = body.Parent
	if win and win:IsA("GuiObject") then
		win.BackgroundTransparency = 1
		for _, c in win:GetChildren() do
			if c.Name == "Header" or c.Name == "Button" or c.Name == "WinArt" or c:IsA("UIStroke") or c:IsA("UIGradient") then
				c:Destroy()
			end
		end
	end
	body.Position = UDim2.fromOffset(0, 0)
	body.Size = UDim2.fromScale(1, 1)

	local d = Backend.data
	local hp = d and d.hpass
	local seasonN, seasonStart, seasonEnd = Config.passSeason()
	local fresh = type(hp) == "table" and hp.season == seasonN
	local xp = if fresh then (tonumber(hp.xp) or 0) else 0
	local tier = Config.passTier(xp)
	local maxTier = PASS.TIERS
	local premium = type(Perks.hpassPremium) == "function" and Perks.hpassPremium() == true
	local price = passSpearPrice(d)
	local rewards = PASS.REWARDS or {}

	local function isClaimed(key: string): boolean
		if fresh and type(hp.claimed) == "table" and hp.claimed[key] then
			return true
		end
		return type(Perks.hpassServerClaimed) == "function" and Perks.hpassServerClaimed(key) == true
	end
	local function isReady(t: number, lane: string): boolean
		local r = rewards[t]
		local items = r and (if lane == "f" then r.free else r.premium)
		return items ~= nil and t <= tier and (lane == "f" or premium) and not isClaimed(lane .. t)
	end

	-- Шапка: картинка во всю ширину (4:1), чуть выше окна, чтобы табличка встала как в концепте
	UI.art("pass_header", { Name = "PassHeader", Size = UDim2.fromOffset(1120, 280), Position = UDim2.fromOffset(0, -50), Crop = true, ZIndex = 1, Parent = body })
	UI.artButton("p_x", { Name = "PassClose", Size = UDim2.fromOffset(52, 52), AnchorPoint = Vector2.new(1, 0), Position = UDim2.fromOffset(1112, 4), ZIndex = 9, Sound = "close" }, function()
		UI.closeWindow()
	end).Parent = body
	UI.art("chip_dark", { Name = "SeasonPlate", Size = UDim2.fromOffset(270, 34), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(560, 114), Slice = { 30, 0, 30, 0 }, SliceScale = 34 / 81, ZIndex = 5, Parent = body })
	UI.label({ Name = "SeasonText", Text = "Season: " .. tostring(PASS.season), TextSize = 20, Size = UDim2.fromOffset(270, 34), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(560, 114), ZIndex = 6, Parent = body })
	UI.art("timer", { Name = "TimerPlaque", Size = UDim2.fromOffset(380, 34), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(560, 146), Slice = { 100, 0, 30, 0 }, SliceScale = 34 / 92, ZIndex = 5, Parent = body })
	local endLbl = UI.label({ Name = "TimerText", Text = "", TextSize = 19, Size = UDim2.fromOffset(300, 34), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(572, 146), ZIndex = 6, Parent = body })
	local function tickEnd()
		endLbl.Text = "Season Ends In: " .. fmtEnds(seasonEnd - Config.marketNow())
	end
	tickEnd()
	task.spawn(function()
		while endLbl.Parent do
			task.wait(5)
			if endLbl.Parent then
				tickEnd()
			end
		end
	end)

	-- Левый блок: деревянная рама (9-slice), щит уровня, полоса опыта, трек
	local track = UI.art("wood_panel", { Name = "TrackPanel", Size = UDim2.fromOffset(772, 368), Position = UDim2.fromOffset(6, 182), Slice = { 96, 84, 96, 56 }, SliceScale = 0.5, ZIndex = 2, Parent = body })
	local into = xp - tier * PASS.XP_PER_TIER
	if tier >= maxTier then
		passBar(track, 490, 34, 1, "MAX", 20, UDim2.fromOffset(200, 16), 3)
	else
		passBar(track, 490, 34, into / PASS.XP_PER_TIER, string.format("%d / %d XP", into, PASS.XP_PER_TIER), 20, UDim2.fromOffset(200, 16), 3)
	end
	local shield = UI.art("shield", { Name = "LevelShield", Size = UDim2.fromOffset(112, 96), Position = UDim2.fromOffset(84, 150), ZIndex = 5, Parent = body })
	UI.label({ Text = "Level", TextSize = 17, Size = UDim2.new(1, 0, 0, 22), Position = UDim2.fromOffset(0, 18), ZIndex = 6, Parent = shield })
	UI.label({ Text = tostring(tier), TextSize = 42, Size = UDim2.new(1, 0, 0, 44), Position = UDim2.fromOffset(0, 36), ZIndex = 6, Parent = shield })

	-- подписи полос слева закреплены
	local function laneLabel(text: string, key: string, icon: string, iconSize: Vector2, tint: Color3?, y: number, textSize: number)
		local f = UI.art(key, { Name = "Lane_" .. text, Size = UDim2.fromOffset(132, 112), Position = UDim2.fromOffset(14, y), Color = tint, ZIndex = 4, Parent = track })
		UI.art(icon, { Size = UDim2.fromOffset(iconSize.X, iconSize.Y), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 14), Fit = true, ZIndex = 5, Parent = f })
		UI.label({ Text = text, TextSize = textSize, Size = UDim2.new(1, 0, 0, 30), Position = UDim2.fromOffset(0, 70), ZIndex = 5, Parent = f })
	end
	laneLabel("FREE", "tile_free", "p_free", Vector2.new(54, 54), Color3.fromRGB(110, 140, 112), 116, 26)
	laneLabel("PREMIUM", "tile_premium", "p_premium", Vector2.new(78, 52), nil, 232, 21)

	local sc = Instance.new("ScrollingFrame")
	sc.Name = "Track"
	sc.BackgroundTransparency = 1
	sc.BorderSizePixel = 0
	sc.Size = UDim2.fromOffset(604, 298)
	sc.Position = UDim2.fromOffset(154, 56)
	sc.ScrollingDirection = Enum.ScrollingDirection.X
	sc.AutomaticCanvasSize = Enum.AutomaticSize.None
	sc.CanvasSize = UDim2.fromOffset(maxTier * PASS_STEP + 8, 0)
	sc.ScrollBarThickness = 6
	sc.ScrollBarImageColor3 = Color3.fromRGB(255, 226, 150)
	sc.ScrollBarImageTransparency = 0.2
	sc.ZIndex = 4
	sc.Parent = track

	-- забрать награду (клиентские полосы через Backend, серверные через Shop)
	local function claim(tile: GuiObject, t: number, lane: string, items: { any })
		local key = lane .. t
		if passBusy[key] then
			return
		end
		passBusy[key] = true
		local pos = UI.screenPos(tile)
		task.spawn(function()
			if Config.passSide(items) == "client" then
				local ok, r = call("HpassClaim", t, lane)
				if ok then
					Sfx.play("level")
					UI.confetti(30)
					if type(r) == "table" then
						if (r.coins or 0) > 0 then
							Hud.flyCoins(pos, r.coins)
						end
						if (r.power or 0) > 0 then
							UI.toast("+" .. Num.short(r.power) .. " Strength", "good")
						end
						if (r.potions or 0) > 0 then
							UI.toast("Potion activated! Check the timers on the right", "good")
						end
					end
				end
			else
				local shop = getShop()
				if not shop then
					UI.toast("The pass is unavailable right now", "warn")
				elseif shop.hpassClaim(t, lane) then
					Sfx.play("level")
					UI.confetti(30)
				end
			end
			passBusy[key] = nil
			Menus.refresh()
		end)
	end

	for t = 1, maxTier do
		local x = (t - 1) * PASS_STEP + 4
		local reached = t <= tier
		-- вымпел с номером тира
		UI.art("pennant", { Name = "Pennant" .. t, Size = UDim2.fromOffset(96, 56), Position = UDim2.fromOffset(x + 8, 2), Color = if reached then nil else Color3.fromRGB(150, 150, 150), ZIndex = 4, Parent = sc })
		UI.label({ Text = tostring(t), TextSize = 26, Size = UDim2.fromOffset(96, 36), Position = UDim2.fromOffset(x + 8, 10), ZIndex = 5, Parent = sc })
		local r = rewards[t]
		for li, lane in { "f", "p" } do
			local items = r and (if lane == "f" then r.free else r.premium)
			if items then
				local y = 60 + (li - 1) * 116
				local claimed = isClaimed(lane .. t)
				local ready = isReady(t, lane)
				local lockedPremium = lane == "p" and not premium
				local dim = not reached and not claimed
				local tileKey = if lane == "f" then "tile_free" else "tile_premium"
				local tint: Color3? = if dim then Color3.fromRGB(120, 120, 128) else nil
				local tile: GuiObject
				if ready then
					-- пульсирующее свечение под плиткой (сосед по ZIndex, не ребёнок)
					local g = UI.glow(sc, C.gold, 170, 0.45)
					g.Position = UDim2.fromOffset(x + PASS_TILE / 2, y + PASS_TILE / 2)
					g.ZIndex = 3
					TweenService:Create(g, TweenInfo.new(0.7, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), { ImageTransparency = 0.85 }):Play()
					tile = UI.artButton(tileKey, { Name = "Tile_" .. lane .. t, Size = UDim2.fromOffset(PASS_TILE, PASS_TILE), Position = UDim2.fromOffset(x, y), ZIndex = 4, Parent = sc }, function()
						claim(tile, t, lane, items)
					end)
					UI.setEnabled(tile :: any, not passBusy[lane .. t])
				else
					tile = UI.art(tileKey, { Name = "Tile_" .. lane .. t, Size = UDim2.fromOffset(PASS_TILE, PASS_TILE), Position = UDim2.fromOffset(x, y), Color = tint, ZIndex = 4, Parent = sc })
				end
				local icons, name = passItemView(items, price)
				local n = math.max(#icons, 1)
				local isz = if n > 1 then 46 else 62
				for i, key in icons do
					UI.art(key, { Size = UDim2.fromOffset(isz, if n > 1 then 46 else 54), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new((i - 0.5) / n, 0, 0, 8), Color = if dim then Color3.fromRGB(150, 150, 150) else nil, Fit = true, ZIndex = 5, Parent = tile })
				end
				local nm = fitLabel(tile, name, 16, nil, { Size = UDim2.fromOffset(104, if ready then 26 else 46), Position = UDim2.fromOffset(4, if ready then 58 else 62), ZIndex = 5 })
				if dim then
					nm.TextTransparency = 0.3
				end
				if ready then
					UI.art("btn_green", { Name = "ClaimPlate", Size = UDim2.fromOffset(86, 24), Position = UDim2.fromOffset(13, 82), Slice = { 30, 0, 30, 0 }, SliceScale = 24 / 74, ZIndex = 6, Parent = tile })
					UI.label({ Text = "CLAIM", TextSize = 16, Size = UDim2.fromOffset(86, 24), Position = UDim2.fromOffset(13, 82), ZIndex = 7, Parent = tile })
				end
				if claimed then
					UI.art("p_check", { Name = "Check", Size = UDim2.fromOffset(34, 28), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -3, 0, 3), Fit = true, ZIndex = 7, Parent = tile })
				elseif lockedPremium then
					UI.art("p_lock", { Name = "Lock", Size = UDim2.fromOffset(26, 30), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -4, 0, 4), Fit = true, ZIndex = 7, Parent = tile })
				end
				-- шансы яйца
				for _, it in items do
					if it.type == "egg" and Perks.state().eggsOff ~= true then
						UI.artButton("chip_dark", { Name = "Odds", Size = UDim2.fromOffset(44, 20), Position = UDim2.fromOffset(4, 4), Slice = { 30, 0, 30, 0 }, SliceScale = 20 / 81, Text = "ODDS", TextSize = 13, ZIndex = 8 }, function()
							local shop = getShop()
							if shop then
								shop.openOdds(it.key)
							end
						end).Parent = tile
						break
					end
				end
			end
		end
	end

	-- прокрутка: к первой готовой награде, иначе к текущему уровню; при перерисовке сохраняем позицию
	if st.scrollX == nil then
		local target = math.max(1, tier)
		for t = 1, tier do
			if isReady(t, "f") or isReady(t, "p") then
				target = t
				break
			end
		end
		st.scrollX = math.max(0, (target - 2) * PASS_STEP)
	end
	local wantX: number = st.scrollX
	sc.CanvasPosition = Vector2.new(wantX, 0)
	task.defer(function()
		if not sc.Parent then
			return
		end
		sc.CanvasPosition = Vector2.new(wantX, 0)
		task.wait() -- раскладка могла ещё не посчитаться: повторяем через кадр
		if not sc.Parent then
			return
		end
		sc.CanvasPosition = Vector2.new(wantX, 0)
		sc:GetPropertyChangedSignal("CanvasPosition"):Connect(function()
			st.scrollX = sc.CanvasPosition.X
		end)
	end)

	-- Низ: покупка по центру
	local prem = Config.SHOP_BY_KEY.pass_premium
	local bund = Config.SHOP_BY_KEY.pass_bundle
	local premPrice = if prem then prem.price else 299
	local bundPrice = if bund then bund.price else 499
	local canBundle = not premium and xp <= (PASS.BUNDLE_MAX_XP or 6000)
	if premium then
		UI.art("chip_xp", { Name = "PremiumActive", Size = UDim2.fromOffset(380, 56), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(560, 558), Slice = { 40, 0, 40, 0 }, SliceScale = 56 / 76, ZIndex = 5, Parent = body })
		UI.label({ Text = "PREMIUM ACTIVE", TextSize = 26, Size = UDim2.fromOffset(380, 56), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(560, 558), ZIndex = 6, Parent = body })
	else
		local function buyBtn(text: string, textSize: number, w: number, h: number, x: number, key: string)
			local b = UI.artButton("btn_big", { Name = "Buy_" .. key, Size = UDim2.fromOffset(w, h), Position = UDim2.fromOffset(x, 616 - h), Slice = { 110, 0, 110, 0 }, SliceScale = h / 109, Text = text, TextSize = textSize, ZIndex = 5 }, function()
				local shop = getShop()
				if shop then
					shop.buyKey(key)
				else
					UI.toast("The shop is unavailable right now", "warn")
				end
			end)
			b.Parent = body
		end
		if canBundle then
			buyBtn("Get Premium  " .. ROBUX .. " " .. premPrice, 26, 420, 62, 130, "pass_premium") -- V71: кнопки целиком внутри окна
			buyBtn("Premium + 10 Tiers  " .. ROBUX .. " " .. bundPrice, 20, 420, 56, 570, "pass_bundle")
		else
			buyBtn("Get Premium  " .. ROBUX .. " " .. premPrice, 28, 480, 62, 320, "pass_premium")
		end
	end

	-- Миссии справа: деревянная рама, заголовок, Daily / Weekly
	local mp = UI.art("wood_panel", { Name = "MissionPanel", Size = UDim2.fromOffset(332, 368), Position = UDim2.fromOffset(782, 182), Slice = { 96, 84, 96, 56 }, SliceScale = 0.5, ZIndex = 2, Parent = body })
	UI.art("p_target", { Size = UDim2.fromOffset(52, 52), Position = UDim2.fromOffset(52, -14), Fit = true, ZIndex = 5, Parent = mp })
	UI.label({ Text = "Missions", TextSize = 32, Size = UDim2.fromOffset(190, 44), Position = UDim2.fromOffset(108, 6), ZIndex = 5, Parent = mp })
	local ms = UI.scroll(mp, UDim2.fromOffset(304, 292), UDim2.fromOffset(14, 58))
	ms.ZIndex = 4
	ms.ScrollBarThickness = 6
	ms.CanvasPosition = Vector2.new(0, st.msY or 0)
	UI.list(Enum.FillDirection.Vertical, 5).Parent = ms
	local dayOk = fresh and hp.day == Config.passDay()
	local weekOk = fresh and hp.week == Config.passWeek()
	local now = Config.marketNow()
	local nextDay = (math.floor(now / 86400) + 1) * 86400
	local nextWeek = seasonStart + (Config.passWeek() + 1) * 7 * 86400
	local order = 0
	local function section(title: string, resetIn: number)
		order += 1
		local f = UI.art("chip_dark", { Name = "Section_" .. title, Size = UDim2.fromOffset(290, 32), LayoutOrder = order, Slice = { 30, 0, 30, 0 }, SliceScale = 32 / 81, ZIndex = 5, Parent = ms })
		UI.art("p_calendar", { Size = UDim2.fromOffset(24, 24), Position = UDim2.fromOffset(8, 4), Fit = true, ZIndex = 6, Parent = f })
		UI.label({ Text = title, TextSize = 21, XAlign = Enum.TextXAlignment.Left, Size = UDim2.fromOffset(100, 32), Position = UDim2.fromOffset(40, 0), ZIndex = 6, Parent = f })
		UI.label({ Text = "resets in " .. fmtLeft(resetIn), TextSize = 13, Color = Color3.fromRGB(200, 236, 200), XAlign = Enum.TextXAlignment.Right, Size = UDim2.fromOffset(130, 32), Position = UDim2.fromOffset(150, 0), ZIndex = 6, Parent = f })
	end
	local function mission(m: any, valid: boolean)
		order += 1
		local goal = math.max(tonumber(m.goal) or 1, 1)
		local done = valid and type(hp.done) == "table" and hp.done[m.id] == true
		local p = if valid and type(hp.prog) == "table" then (tonumber(hp.prog[m.id]) or 0) else 0
		local f = UI.art("row_cream", { Name = "Mission_" .. tostring(m.id), Size = UDim2.fromOffset(290, 66), LayoutOrder = order, Slice = { 30, 0, 30, 0 }, SliceScale = 66 / 82, Color = if done then Color3.fromRGB(206, 236, 200) else nil, ZIndex = 5, Parent = ms })
		UI.art(MISSION_ART[m.kind] or "p_paw", { Size = UDim2.fromOffset(34, 34), Position = UDim2.fromOffset(8, 16), Fit = true, ZIndex = 6, Parent = f })
		fitLabel(f, tostring(m.text or ""), 16, PASS_INK, { Stroke = 0, XAlign = Enum.TextXAlignment.Left, Size = UDim2.fromOffset(164, 38), Position = UDim2.fromOffset(48, 1), YAlign = Enum.TextYAlignment.Center, ZIndex = 6 }) -- V71: две строки, название не обрезается
		local shown = if done then goal else math.min(p, goal)
		passBar(f, 160, 17, shown / goal, Num.short(shown) .. " / " .. Num.short(goal), 13, UDim2.fromOffset(48, 43), 6)
		UI.art("chip_xp", { Name = "XpChip", Size = UDim2.fromOffset(66, 26), Position = UDim2.fromOffset(216, 20), Color = if done then Color3.fromRGB(190, 190, 190) else nil, Slice = { 30, 0, 30, 0 }, SliceScale = 26 / 76, ZIndex = 6, Parent = f })
		UI.label({ Text = "+" .. tostring(m.xp or 0) .. " XP", TextSize = 13, Size = UDim2.fromOffset(66, 26), Position = UDim2.fromOffset(216, 20), ZIndex = 7, Parent = f })
		if done then
			UI.art("p_check", { Name = "Check", Size = UDim2.fromOffset(24, 20), Position = UDim2.fromOffset(26, 38), Fit = true, ZIndex = 9, Parent = f })
		end
	end
	section("Daily", nextDay - now)
	for _, m in Config.passDaily() do
		mission(m, dayOk)
	end
	section("Weekly", nextWeek - now)
	for _, m in PASS.WEEKLY do
		mission(m, weekOk)
	end
	local wantY: number = st.msY or 0
	task.defer(function()
		if not ms.Parent then
			return
		end
		ms.CanvasPosition = Vector2.new(0, wantY)
		task.wait() -- раскладка ещё не посчитана: повторяем через кадр
		if not ms.Parent then
			return
		end
		ms.CanvasPosition = Vector2.new(0, wantY)
		ms:GetPropertyChangedSignal("CanvasPosition"):Connect(function()
			st.msY = ms.CanvasPosition.Y
		end)
	end)
end

function Menus.pass()
	-- свежий сезон/день/неделя на сервере экономики (ошибка не мешает открыть окно)
	pcall(Backend.call, "HpassSync")
	show("pass", "Hunter Pass", Vector2.new(1120, 630), Color3.fromRGB(46, 138, 76), renderPass)
	local shop = getShop()
	if shop then
		-- обновляем окно при покупке/выдаче, сам хук снимается, когда окно закрыто
		shop.onHpassChange = function()
			if UI.windowOpen("pass") then
				Menus.refresh()
			else
				shop.onHpassChange = nil
			end
		end
	end
end

-- Событие миссии/уровня пропуска
Backend.onEvent(function(name: string, payload: any)
	if name ~= "hpass" or type(payload) ~= "table" then
		return
	end
	if (tonumber(payload.xp) or 0) > 0 then -- на максимуме опыт не добавляется: «+0 Pass XP» не показываем
		UI.toast("+" .. tostring(payload.xp) .. " Pass XP · " .. tostring(payload.text or "Mission"), "good", 3)
	end
	if payload.tierUp then
		Sfx.play("level")
		Hud.banner("PASS TIER " .. tostring(payload.tier or "") .. "!", C.gold, "New rewards unlocked", 2.2)
	end
end)

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
		{ "🎟️ +300 PASS XP", C.gold, function()
			call("HpassDebugXp", 300)
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
	show("demo", "🧪 Developer Tools", Vector2.new(840, 470), C.purple, renderDemo)
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

-- питомцы изменились (надели/сняли/вылупили): перерисовать вкладку Pets, если она открыта
Perks.Changed.Event:Connect(function()
	local w = cur
	if w and w.id == "bag" and w.state.tab == "pets" and UI.windowOpen("bag") then
		Menus.refresh()
	end
end)

Hud.MenuClicked.Event:Connect(function(name: string)
	local f = (Menus :: any)[name]
	if type(f) == "function" then
		closeDialog()
		if UI.windowOpen(name) then
			UI.closeWindow()
		else
			f()
		end
	end
end)

return Menus
