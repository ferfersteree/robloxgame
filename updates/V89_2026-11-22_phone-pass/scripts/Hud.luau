-- StarterPlayerScripts/Client/Hud.luau
-- Экран: верхняя панель (четыре карточки: монеты, сила, сумка, уровень+опыт), рамка-меню слева, бусты и задания справа,
-- внизу — шкала натяжения и кнопка броска (телефон), баннеры зон. Режимы: normal | hunt | busy | cinematic.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local GuiService = game:GetService("GuiService")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Backend = require(script.Parent.Backend)
local Perks = require(script.Parent.Perks)

local Hud = {}
Hud.mode = "normal"
Hud.ThrowDown = Instance.new("BindableEvent")
Hud.ThrowUp = Instance.new("BindableEvent")
Hud.throwTouch = nil :: any -- касание (InputObject), которое сейчас держит кнопку броска
Hud.ExitClicked = Instance.new("BindableEvent")
Hud.MenuClicked = Instance.new("BindableEvent") -- (name)

local C = Theme.C
local root = UI.root

---------------------------------------------------------------------
-- Верхняя панель: четыре крупные карточки (монеты, сила, сумка, уровень)
---------------------------------------------------------------------
local compactMenu = UI.mobile or RS:GetAttribute("ForceMobileUI") == true

local topBar = Instance.new("Frame")
topBar.Name = "TopBar"
topBar.BackgroundTransparency = 1
topBar.AnchorPoint = Vector2.new(0.5, 0)
topBar.Position = UDim2.new(0.5, 0, 0, 2) -- карточки кончаются на y=83: ниже стоят карточки Guide/Activities (y=86)
topBar.Size = UDim2.fromOffset(1024, 81) -- четыре карточки 250×81 и три зазора по 8
UI.list(Enum.FillDirection.Horizontal, 8, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = topBar
if compactMenu then
	-- телефон: сжимаем до ширины старой полосы, чтобы не лезть на кнопки меню и правую панель
	local ts = Instance.new("UIScale")
	ts.Name = "PhoneScale"
	ts.Scale = 0.8
	ts.Parent = topBar
end
topBar.Parent = root

type Pill = { frame: ImageLabel, value: TextLabel, icon: ImageLabel, shown: number, caption: TextLabel? }
local badges: { GuiObject } = {}

-- полоса из арта: дорожка bar_track и заливка, обрезанная по доле (картинка не сжимается)
-- p: W, H (в единицах), Position, AnchorPoint, ZIndex, Parent, Fill (ключ арта), FillColor, TextSize
local function artBar(p: { [string]: any }): any
	local w, h = p.W, p.H
	local z = p.ZIndex or 2
	local track = UI.art("bar_track", { Name = "Bar", Size = UDim2.fromOffset(w, h), Position = p.Position, AnchorPoint = p.AnchorPoint, ZIndex = z, Slice = { 12, 0, 12, 0 }, SliceScale = h / 23, Parent = p.Parent })
	local ix, iy = math.max(2, math.floor(h * 0.13)), math.max(2, math.floor(h * 0.1))
	local iw, ih = w - 2 * ix, h - 2 * iy
	local clip = Instance.new("Frame")
	clip.Name = "Clip"
	clip.BackgroundTransparency = 1
	clip.BorderSizePixel = 0
	clip.ClipsDescendants = true
	clip.Position = UDim2.fromOffset(ix, iy)
	clip.Size = UDim2.fromOffset(0, ih)
	clip.ZIndex = z + 1
	clip.Visible = false
	clip.Parent = track
	local fill = UI.art(p.Fill or "bar_green", { Name = "Fill", Size = UDim2.fromOffset(iw, ih), ZIndex = z + 1, Slice = if (p.Fill :: any) == "btn_yellow" then { 14, 0, 14, 0 } else { 10, 0, 10, 0 }, SliceScale = ih / (if (p.Fill :: any) == "btn_yellow" then 64 else 21), Color = p.FillColor, Parent = clip })
	local lbl = UI.label({ Text = "", TextSize = p.TextSize or 16, Size = UDim2.fromScale(1, 1), ZIndex = z + 2, Stroke = 2, Parent = track })
	local bar = { frame = track, fill = fill, clip = clip, label = lbl }
	bar.set = function(k: number, text: string?, anim: boolean?)
		k = math.clamp(k, 0, 1)
		local target = UDim2.fromOffset(math.floor(iw * k), ih)
		if anim then
			UI.tween(clip, 0.35, { Size = target }, Enum.EasingStyle.Quad)
		else
			clip.Size = target
		end
		clip.Visible = k > 0.001
		if text then
			lbl.Text = text
		end
	end
	return bar
end

-- карточка: рамка-спрайт и значок слева (внутри рамки)
local TX, TW = 84, 152 -- область текста карточки: начало и ширина
local function chipBase(order: number, chipKey: string, iconKey: string): (ImageLabel, ImageLabel)
	local f = UI.art(chipKey, { Name = chipKey, Size = UDim2.fromOffset(250, 81), LayoutOrder = order, Parent = topBar })
	local ic = UI.art(iconKey, { Name = "Icon", Fit = true, Size = UDim2.fromOffset(58, 58), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0, 45, 0.5, 0), ZIndex = 3, Parent = f })
	table.insert(badges, ic)
	return f, ic
end

-- карточка «подпись + крупное значение»
local function pill(iconKey: string, caption: string, chipKey: string, order: number): Pill
	local f, ic = chipBase(order, chipKey, iconKey)
	local cap = UI.label({ Text = caption, TextSize = 20, Size = UDim2.fromOffset(TW, 22), Position = UDim2.fromOffset(TX, 8), ZIndex = 4, Stroke = 2, Parent = f })
	local v = UI.label({ Text = "0", TextSize = 34, Size = UDim2.fromOffset(TW, 36), Position = UDim2.fromOffset(TX, 29), Scaled = true, MaxSize = 34, ZIndex = 4, Parent = f })
	return { frame = f, value = v, icon = ic, shown = 0, caption = cap }
end
local coins = pill("ic_coin", "Coins", "chip_gold", 1)
local power = pill("ic_power", "Strength", "chip_red", 2)
local bag = pill("ic_bag", "Bag", "chip_blue", 3)

-- уровень: звезда, «Level N» и полоса опыта
local lvlFrame, star = chipBase(4, "chip_violet", "ic_star")
local lvlNum = UI.label({ Text = "Level 1", TextSize = 22, Size = UDim2.fromOffset(TW, 24), Position = UDim2.fromOffset(TX, 7), ZIndex = 4, Stroke = 2, Parent = lvlFrame })
local xpBar = artBar({ W = TW, H = 22, Position = UDim2.fromOffset(TX, 40), ZIndex = 4, Fill = "bar_cyan", TextSize = 15, Parent = lvlFrame })

-- Верхняя панель: анимации (вход, «дыхание» иконок, всплывающие +N, шкала рюкзака, уровень)
local pills = { coins, power, bag }
local bagFull = false
local starBusy = false
local lastLevel: number? = nil
local primed: { [any]: boolean } = {}


-- всплывающая цифра над панелью
local function floatText(frame: GuiObject, text: string, color: Color3)
	local l = UI.label({ Text = text, TextSize = 26, Color = color, Size = UDim2.fromOffset(140, 30), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 1, -6), ZIndex = 12, Stroke = 3, Parent = frame })
	local st = l:FindFirstChildOfClass("UIStroke")
	UI.tween(l, 0.95, { Position = UDim2.new(0.5, 0, 1, 22) }, Enum.EasingStyle.Quad)
	task.delay(0.5, function()
		UI.tween(l, 0.45, { TextTransparency = 1 })
		if st then
			UI.tween(st, 0.45, { Transparency = 1 })
		end
	end)
	task.delay(1.05, function()
		l:Destroy()
	end)
end

-- редкие «искорки» на значках
task.spawn(function()
	while true do
		task.wait(2.2 + math.random() * 2.6)
		local b = badges[math.random(1, #badges)]
		if b and b.Parent then
			local sp = Instance.new("ImageLabel")
			sp.BackgroundTransparency = 1
			sp.Image = UI.IMG.sparkle
			sp.ImageColor3 = Color3.new(1, 1, 1)
			sp.AnchorPoint = Vector2.new(0.5, 0.5)
			sp.Position = UDim2.fromScale(0.78, 0.2)
			sp.Size = UDim2.fromOffset(0, 0)
			sp.ZIndex = 8
			sp.Parent = b
			UI.tween(sp, 0.3, { Size = UDim2.fromOffset(18, 18), Rotation = 45 }, Enum.EasingStyle.Back)
			task.delay(0.35, function()
				UI.tween(sp, 0.35, { Size = UDim2.fromOffset(0, 0), Rotation = 120 })
			end)
			task.delay(0.75, function()
				sp:Destroy()
			end)
		end
	end
end)

-- появление панелей по очереди
for i, f in { coins.frame, power.frame, bag.frame, lvlFrame } do
	local sc = Instance.new("UIScale")
	sc.Name = "Intro"
	sc.Scale = 0
	sc.Parent = f
	task.delay(0.15 + (i - 1) * 0.09, function()
		UI.tween(sc, 0.45, { Scale = 1 }, Enum.EasingStyle.Back)
	end)
end

-- «дыхание» иконок, тревога при полном рюкзаке, редкие блики
do
	local base: { [any]: UDim2 } = {}
	for _, p in pills do
		base[p] = p.icon.Position
	end
	local t0 = os.clock()
	local nextShine = os.clock() + 4
	RunService.RenderStepped:Connect(function()
		local t = os.clock() - t0
		for i, p in pills do
			local b = base[p]
			p.icon.Position = UDim2.new(b.X.Scale, b.X.Offset, b.Y.Scale, b.Y.Offset + math.sin(t * 2.2 + i * 1.3) * 1.6)
			if not (bagFull and p == bag) then
				p.icon.Rotation = math.sin(t * 1.7 + i) * 5
			end
		end
		if not starBusy then
			star.Rotation = math.sin(t * 1.4) * 8
		end
		if bagFull then
			local k = (math.sin(t * 7) + 1) / 2
			bag.value.TextColor3 = C.red:Lerp(C.text, k * 0.6)
			bag.icon.Rotation = math.sin(t * 18) * 9
		end
		if os.clock() > nextShine then
			nextShine = os.clock() + 5 + math.random() * 4
			UI.shine(pills[math.random(1, #pills)].frame, 0.9)
		end
	end)
end

local function setPill(p: Pill, value: number, text: string?)
	if math.abs(value - p.shown) < 1e-6 then
		if text then
			p.value.Text = text
		end
		return
	end
	local from = p.shown
	p.shown = value
	if text then
		p.value.Text = text
	else
		UI.countUp(p.value, from, value, 0.45, Num.short, false)
	end
	UI.punch(p.frame, value > from and 0.14 or 0.06)
	UI.punch(p.icon, 0.4)
	-- первое заполнение при загрузке данных — без эффектов
	if not primed[p] then
		primed[p] = true
		return
	end
	local up = value > from
	local delta = math.abs(value - from)
	floatText(p.frame, (if up then "+" else "-") .. Num.short(delta), if up then (if p == bag then C.blue else C.gold) else C.red)
	if p ~= bag then
		p.value.TextColor3 = if up then C.green else C.red
		UI.tween(p.value, 0.8, { TextColor3 = C.text })
	end
	if up then
		UI.shine(p.frame, 0.6)
		if p ~= coins then
			pcall(function()
				UI.burst(UI.screenPos(p.icon), if p == power then C.red else C.blue, 7, 200)
			end)
		end
	end
end

local function setLevel(level: number)
	lvlNum.Text = "Level " .. tostring(level)
	if lastLevel and level > lastLevel then
		starBusy = true
		star.Rotation = 0
		UI.tween(star, 0.8, { Rotation = 360 }, Enum.EasingStyle.Back)
		task.delay(0.85, function()
			star.Rotation = 0
			starBusy = false
		end)
		UI.punch(star, 0.6)
		UI.punch(lvlNum, 0.5)
		UI.punch(lvlFrame, 0.2)
		UI.shine(lvlFrame, 0.8)
		floatText(lvlFrame, "LEVEL " .. level, C.gold)
		pcall(function()
			UI.burst(UI.screenPos(star), C.gold, 16, 320)
		end)
	end
	lastLevel = level
end

---------------------------------------------------------------------
-- Меню слева
---------------------------------------------------------------------
-- Меню слева. V57: на телефоне (только сенсорный ввод) оно компактное. Столбец из 7 кнопок посередине экрана лежал на зоне штатного
-- стика движения, а цель касания у кнопки с подписью была около 27 пикселей (экран высотой 375). Теперь вверху слева две кнопки по
-- 96 единиц (46 пикселей на таком экране): «Shop» (всегда на виду) и «📋», которая открывает остальное сеткой 3×2 и закрывает её после
-- выбора. Проверка на ПК: атрибут ReplicatedStorage.ForceMobileUI = true включает тот же вид.
---------------------------------------------------------------------
local menuButtons: { [string]: any } = {}
-- id, значок (ключ арта), подпись, кнопка (ключ арта), оттенок кнопки
local MENU: { { any } } = {
	{ "shop", "ic_shop", "Shop", "btn_red", nil },
	{ "bag", "ic_bag2", "Bag", "btn_blue", nil },
	{ "spears", "ic_spear", "Spears", "btn_orange", nil },
	{ "index", "ic_deer", "Animals", "btn_green", nil },
	{ "quests", "ic_quests", "Quests", "btn_purple", nil },
	{ "pass", "ic_pass", "Pass", "btn_yellow", nil },
	{ "potions", "ic_potion", "Potions", "btn_purple", Color3.fromRGB(255, 170, 225) },
	{ "settings", "ic_gear", "Settings", "btn_grey", nil },
}
-- Панель читов видна только разработчику в Студии, в живой игре её нет
if Config.BACKEND == "Demo" and RunService:IsStudio() then
	table.insert(MENU, { "demo", "ic_gear", "DEMO", "btn_grey", Color3.fromRGB(255, 110, 110) })
end

-- ПК: рамка panel_menu (9-slice 48 px: углы с верёвкой не тянутся), внутри столбец кнопок 208×56
local BTN_W, BTN_H, BTN_GAP = 208, 56, 8
local left: GuiObject -- контейнер с раскладкой (кнопки)
local leftBox: GuiObject -- то, что показываем и прячем
if compactMenu then
	left = UI.art("panel_menu", { Name = "LeftMenu", Size = UDim2.fromOffset(340, 10), Position = UDim2.new(0, 10, 0, 116), Slice = 48, SliceScale = 0.6, Parent = root })
	left.AutomaticSize = Enum.AutomaticSize.Y
	UI.pad(18, 30).Parent = left
	leftBox = left
else
	local n = #MENU
	leftBox = UI.art("panel_menu", {
		Name = "LeftMenu", Size = UDim2.fromOffset(256, n * BTN_H + (n - 1) * BTN_GAP + 64),
		Position = UDim2.new(0, 12, 0, 108), Slice = 48, SliceScale = 0.7, Parent = root,
	})
	local inner = Instance.new("Frame")
	inner.Name = "Buttons"
	inner.BackgroundTransparency = 1
	inner.Size = UDim2.fromScale(1, 1)
	UI.pad(24, 32).Parent = inner
	inner.Parent = leftBox
	left = inner
end
local menuOpen = false -- только для компактного меню
local menuToggle: any = nil
local readyQuests, bagIsFull, readyPass = 0, false, 0
local function updateMenuBadge()
	if menuToggle then
		local n = readyQuests + readyPass + (bagIsFull and 1 or 0)
		UI.badge(menuToggle, if n > 0 then n else nil)
	end
end
if compactMenu then
	local grid = Instance.new("UIGridLayout")
	grid.CellSize = UDim2.fromOffset(96, 96)
	grid.CellPadding = UDim2.fromOffset(8, 8)
	grid.FillDirectionMaxCells = 3
	grid.HorizontalAlignment = Enum.HorizontalAlignment.Center
	grid.SortOrder = Enum.SortOrder.LayoutOrder
	grid.Parent = left
	left.Visible = false
else
	UI.list(Enum.FillDirection.Vertical, BTN_GAP, Enum.HorizontalAlignment.Center).Parent = left
end

local function setMenuOpen(on: boolean)
	menuOpen = on
	leftBox.Visible = on and Hud.mode == "normal"
end

-- плитка телефона: slot, значок сверху, подпись снизу
local function tileButton(iconKey: string, text: string, p: { [string]: any }, onClick: () -> ()): ImageButton
	p.Text = text
	p.TextSize = 16
	local b = UI.artButton("slot", p, onClick)
	local lbl = b:FindFirstChild("Label") :: TextLabel?
	if lbl then
		lbl.Size = UDim2.new(1, 0, 0, 22)
		lbl.Position = UDim2.new(0, 0, 1, -26)
	end
	UI.art(iconKey, { Name = "Icon", Fit = true, Size = UDim2.fromOffset(56, 56), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 8), ZIndex = 3, Parent = b })
	return b
end

for i, m in MENU do
	local alone = compactMenu and m[1] == "shop" -- «Shop» на телефоне стоит отдельно, всегда на виду
	local function onClick()
		if compactMenu then
			setMenuOpen(false)
		end
		Hud.MenuClicked:Fire(m[1])
	end
	local b: ImageButton
	if compactMenu then
		b = tileButton(m[2], m[3], { Size = UDim2.fromOffset(96, 96), LayoutOrder = i, Position = if alone then UDim2.new(0, 10, 0, 10) else nil }, onClick)
	else
		b = UI.artButton(m[4], { Size = UDim2.fromOffset(BTN_W, BTN_H), LayoutOrder = i, Text = m[3], TextSize = 26, Color = m[5] }, onClick)
		-- значок слева, подпись после него (как на концепте)
		local lbl = b:FindFirstChild("Label") :: TextLabel?
		if lbl then
			lbl.Position = UDim2.fromOffset(64, 0)
			lbl.Size = UDim2.new(1, -70, 1, 0)
			lbl.TextXAlignment = Enum.TextXAlignment.Left
		end
		UI.art(m[2], { Name = "Icon", Fit = true, Size = UDim2.fromOffset(48, 48), AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.new(0, 10, 0.5, 0), ZIndex = 3, Parent = b })
	end
	b.Parent = if alone then root else left
	menuButtons[m[1]] = b
end
if compactMenu then
	local toggle = tileButton("ic_quests", "Menu", { Size = UDim2.fromOffset(96, 96), Position = UDim2.new(0, 114, 0, 10), Name = "MenuToggle" }, function()
		setMenuOpen(not menuOpen)
	end)
	toggle.Parent = root
	menuToggle = toggle
end

function Hud.menuButton(name: string): any
	return menuButtons[name]
end

-- Hunter Pass: число наград, которые можно забрать. Никогда не падает, если d.hpass нет
local function passReadyCount(d: any): number
	local ok, n = pcall(function(): number
		local hp = d and d.hpass
		local cfg: any = Config
		local perks: any = Perks
		if type(hp) ~= "table" or type(cfg.PASS) ~= "table" or type(cfg.passTier) ~= "function" or type(cfg.passSeason) ~= "function" then
			return 0
		end
		if hp.season ~= cfg.passSeason() then
			return 0 -- сезон сменился: прогресс обнулится при следующем обращении к серверу
		end
		local tier = cfg.passTier(tonumber(hp.xp) or 0)
		local premium = type(perks.hpassPremium) == "function" and perks.hpassPremium() == true
		local claimedFn = perks.hpassServerClaimed
		local cnt = 0
		for t = 1, tier do
			local r = cfg.PASS.REWARDS and cfg.PASS.REWARDS[t]
			if r then
				for _, lane in { "f", "p" } do
					local items = if lane == "f" then r.free else r.premium
					local key = lane .. t
					local claimed = (type(hp.claimed) == "table" and hp.claimed[key] == true) or (type(claimedFn) == "function" and claimedFn(key) == true)
					if items and not claimed and (lane == "f" or premium) then
						cnt += 1
					end
				end
			end
		end
		return cnt
	end)
	return if ok and type(n) == "number" then n else 0
end

local function updatePassBadge(d: any)
	readyPass = passReadyCount(d)
	local pb = menuButtons.pass
	if pb then
		UI.badge(pb, readyPass)
	end
	updateMenuBadge()
end

---------------------------------------------------------------------
-- Справа: бусты и задания
---------------------------------------------------------------------
local QW = compactMenu and 260 or 330 -- ширина правой колонки (V72: шире, как на концепте)
local QIN = QW - 52 -- ширина содержимого панели заданий
local QROW, QGAP = compactMenu and 78 or 54, compactMenu and 6 or 8 -- высота строки задания и зазор (V89: на телефоне строка выше: две строки названия)
local right = Instance.new("Frame")
right.Name = "RightPanel"
right.BackgroundTransparency = 1
-- ПК: под верхней панелью; телефон: как раньше (по центру правого края)
right.AnchorPoint = if compactMenu then Vector2.new(1, 0.5) else Vector2.new(1, 0)
right.Position = if compactMenu then UDim2.new(1, -12, 0.42, 0) else UDim2.new(1, -12, 0, 108)
right.Size = UDim2.fromOffset(QW, 420)
UI.list(Enum.FillDirection.Vertical, 8, Enum.HorizontalAlignment.Right).Parent = right
right.Parent = root

local boostBox = Instance.new("Frame")
boostBox.BackgroundTransparency = 1
boostBox.Size = UDim2.fromOffset(QW, 10)
boostBox.AutomaticSize = Enum.AutomaticSize.Y
boostBox.LayoutOrder = 1
UI.list(Enum.FillDirection.Vertical, 6, Enum.HorizontalAlignment.Right).Parent = boostBox
boostBox.Parent = right

-- панель заданий: panel_quests (9-slice 48 px), внутри столбец; высота считается в refreshQuests
local questBox = UI.art("panel_quests", { Name = "QuestTracker", Size = UDim2.fromOffset(QW, 100), Slice = 56, SliceScale = 0.7, LayoutOrder = 2, Parent = right })
local questList = Instance.new("Frame")
questList.Name = "List"
questList.BackgroundTransparency = 1
questList.Size = UDim2.fromScale(1, 1)
do
	local pd = Instance.new("UIPadding")
	pd.PaddingLeft = UDim.new(0, 26)
	pd.PaddingRight = UDim.new(0, 26)
	pd.PaddingTop = UDim.new(0, 24)
	pd.PaddingBottom = UDim.new(0, 20)
	pd.Parent = questList
end
UI.list(Enum.FillDirection.Vertical, QGAP, Enum.HorizontalAlignment.Left).Parent = questList
questList.Parent = questBox
do
	local head = Instance.new("Frame")
	head.Name = "Header"
	head.BackgroundTransparency = 1
	head.Size = UDim2.new(1, 0, 0, 36)
	head.LayoutOrder = 0
	head.ZIndex = 4
	UI.list(Enum.FillDirection.Horizontal, 8, Enum.HorizontalAlignment.Left, Enum.VerticalAlignment.Center).Parent = head
	UI.art("ic_quests", { Name = "Icon", Fit = true, Size = UDim2.fromOffset(36, 36), ZIndex = 4, LayoutOrder = 1, Parent = head })
	UI.label({ Text = "Quests", TextSize = 30, Size = UDim2.new(1, -46, 1, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, LayoutOrder = 2, Parent = head })
	head.Parent = questList
end
local questRows: { Frame } = {}
local QFILL = { "bar_green", "bar_cyan", "bar_purple" }

local boostRows: { [string]: { frame: GuiObject, label: TextLabel } } = {}
local function refreshBoosts()
	for id, b in Config.BOOSTS do
		local left_ = Backend.boostLeft(id)
		local row = boostRows[id]
		if left_ > 0 then
			if not row then
				-- тёмная плашка из bar_track (3-slice по краям), цвет буста — в подписи
				local f = UI.art("bar_track", { Name = "Boost", Size = UDim2.fromOffset(QW - 40, 42), Slice = { 12, 0, 12, 0 }, SliceScale = 42 / 23, Parent = boostBox })
				UI.label({ Text = b.icon, TextSize = 26, Size = UDim2.fromOffset(40, 42), Position = UDim2.fromOffset(6, 0), ZIndex = 4, Stroke = 2, Parent = f })
				local l = UI.label({ Text = "", TextSize = 18, Color = b.color:Lerp(Color3.new(1, 1, 1), 0.45), Size = UDim2.new(1, -56, 1, 0), Position = UDim2.fromOffset(48, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = f })
				row = { frame = f, label = l }
				boostRows[id] = row
				UI.punch(f, 0.3)
				UI.shine(f, 0.8)
			end
			(row :: any).label.Text = b.name .. "  " .. Num.time(left_)
		elseif row then
			row.frame:Destroy()
			boostRows[id] = nil
		end
	end
end
task.spawn(function()
	while true do
		refreshBoosts()
		task.wait(1)
	end
end)

local function refreshQuests(d: any)
	for _, r in questRows do
		r:Destroy()
	end
	table.clear(questRows)
	local list = {}
	for id, st in d.quests do
		table.insert(list, { q = Config.QUEST_BY_ID[id], st = st })
	end
	table.sort(list, function(a, b)
		return a.q.index < b.q.index
	end)
	local ready = 0
	for i, e in list do
		local done = e.st.done
		local f = Instance.new("Frame")
		f.Name = "Row"
		f.BackgroundTransparency = 1
		f.Size = UDim2.new(1, 0, 0, QROW)
		f.LayoutOrder = i
		f.ZIndex = 4
		-- V72: название задания в две строки, не мельче 13 (длинные раньше ужимались до нечитаемых)
		-- V89: на телефоне название задания на всю ширину панели (в две строки), счётчик справа от полоски: раньше название
		-- ужималось в 78 пикселей и было видно только «Catch an». У шрифта большой межстрочный интервал (около 1,6), поэтому
		-- две строки по 17 единиц требуют высоты около 56
		local titleW = if compactMenu then 0 else (if done then -112 else -70)
		local titleH = if compactMenu then 58 else 34
		local ql = UI.label({ Text = e.q.text, TextSize = 18, Size = UDim2.new(1, titleW, 0, titleH), XAlign = Enum.TextXAlignment.Left, YAlign = if compactMenu then Enum.TextYAlignment.Bottom else Enum.TextYAlignment.Center, ZIndex = 4, Stroke = 2, Scaled = true, MaxSize = if compactMenu then 17 else 18, Parent = f })
		local qc = ql:FindFirstChildOfClass("UITextSizeConstraint")
		if qc then
			qc.MinTextSize = if compactMenu then 11 else 13
		end
		local countW = if done then 108 else 66
		UI.label({
			Text = if done then "DONE! Claim" else (Num.short(e.st.p) .. "/" .. Num.short(e.q.goal)), TextSize = 17,
			Color = if done then C.gold else C.text, Size = UDim2.fromOffset(countW, if compactMenu then 18 else 34), AnchorPoint = Vector2.new(1, 0),
			Position = if compactMenu then UDim2.fromOffset(QIN, titleH + 1) else UDim2.new(1, 0, 0, 0), XAlign = Enum.TextXAlignment.Right, ZIndex = 4, Stroke = 2, Parent = f,
		})
		local bar = artBar({ W = if compactMenu then QIN - countW - 4 else QIN, H = 16, Position = UDim2.fromOffset(0, if compactMenu then titleH + 2 else 36), ZIndex = 4, Fill = if done then "btn_yellow" else QFILL[(i - 1) % #QFILL + 1], TextSize = 10, Parent = f })
		bar.set(if done then 1 else e.st.p / e.q.goal)
		if done then
			ready += 1
		end
		f.Parent = questList
		table.insert(questRows, f)
	end
	questBox.Size = UDim2.fromOffset(QW, 44 + 52 + #list * (QROW + QGAP)) -- V71: +16, нижняя рама не заходит на последнюю полоску
	questBox.Visible = #list > 0
	local qb = menuButtons.quests
	if qb then
		UI.badge(qb, ready)
	end
	readyQuests = ready
	updateMenuBadge()
end

---------------------------------------------------------------------
-- Натяжение (внизу по центру) и кнопка броска
---------------------------------------------------------------------
local hunt = Instance.new("Frame")
hunt.Name = "Hunt"
hunt.BackgroundTransparency = 1
hunt.Size = UDim2.fromScale(1, 1)
hunt.Visible = false
hunt.Parent = root

local meter = Instance.new("Frame")
meter.Name = "Meter"
meter.BackgroundTransparency = 1
meter.AnchorPoint = Vector2.new(0.5, 1)
meter.Position = UDim2.new(0.5, 0, 1, -24)
meter.Size = UDim2.fromOffset(620, 190)
meter.Parent = hunt
local meterScale = Instance.new("UIScale")
meterScale.Parent = meter

local multLabel = UI.label({ Text = "×1.0", TextSize = 84, Size = UDim2.fromOffset(400, 90), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 0), Stroke = 5, Parent = meter })
local tierLabel = UI.label({ Text = "PRESS AND HOLD", TextSize = 30, Size = UDim2.fromOffset(500, 34), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 86), Parent = meter })
local barBg = Instance.new("Frame")
barBg.BackgroundColor3 = Color3.fromRGB(16, 18, 30)
barBg.Size = UDim2.fromOffset(600, 30)
barBg.AnchorPoint = Vector2.new(0.5, 0)
barBg.Position = UDim2.new(0.5, 0, 0, 128)
UI.corner(1, true).Parent = barBg
local barStroke = UI.stroke(Color3.new(0, 0, 0), 4, 0, true)
barStroke.Parent = barBg
barBg.Parent = meter
local barFill = Instance.new("Frame")
barFill.BorderSizePixel = 0
barFill.BackgroundColor3 = Color3.new(1, 1, 1)
barFill.Size = UDim2.fromScale(0, 1)
UI.corner(1, true).Parent = barFill
local fillGrad = UI.gradient(C.green, C.green, 0)
fillGrad.Parent = barFill
barFill.Parent = barBg
-- отметки ступеней (лог-шкала)
local LN = math.log(Config.TENSION.cap)
local ticks: { [number]: Frame } = {} -- V67: отметка каждой ступени (для вспышки при переходе)
for i, t in Config.TIERS do
	if i > 1 then
		local x = math.log(t.m) / LN
		local tick = Instance.new("Frame")
		ticks[i] = tick
		tick.BorderSizePixel = 0
		tick.BackgroundColor3 = t.color
		tick.Size = UDim2.fromOffset(4, 38)
		tick.AnchorPoint = Vector2.new(0.5, 0.5)
		tick.Position = UDim2.new(x, 0, 0.5, 0)
		tick.ZIndex = 3
		UI.stroke(Color3.new(0, 0, 0), 2, 0, true).Parent = tick
		tick.Parent = barBg
		UI.label({ Text = "×" .. t.m, TextSize = 18, Color = t.color, Size = UDim2.fromOffset(60, 20), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(x, 0, 1, 4), ZIndex = 3, Stroke = 2, Parent = barBg })
	end
end
local hint = UI.label({ Text = "", TextSize = 20, Color = C.dim, Size = UDim2.fromOffset(600, 24), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 0, -6), Stroke = 2, Parent = meter })

-- красная виньетка при дрожи
local vignette = Instance.new("Frame")
vignette.BackgroundTransparency = 1
vignette.Size = UDim2.fromScale(1, 1)
vignette.Parent = hunt
local vigParts: { Frame } = {}
for i, rot in { 90, 270, 0, 180 } do
	local f = Instance.new("Frame")
	f.BorderSizePixel = 0
	f.BackgroundColor3 = C.red
	f.BackgroundTransparency = 0
	if i <= 2 then
		f.Size = UDim2.new(1, 0, 0.22, 0)
		f.Position = i == 1 and UDim2.new(0, 0, 0, 0) or UDim2.new(0, 0, 0.78, 0)
	else
		f.Size = UDim2.new(0.18, 0, 1, 0)
		f.Position = i == 3 and UDim2.new(0, 0, 0, 0) or UDim2.new(0.82, 0, 0, 0)
	end
	local g = Instance.new("UIGradient")
	g.Rotation = rot
	g.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1) })
	g.Parent = f
	f.Visible = false
	f.Parent = vignette
	table.insert(vigParts, f)
end

-- кнопка броска (телефон и мышь)
local throwBtn = Instance.new("ImageButton")
throwBtn.Name = "Throw"
throwBtn.BackgroundColor3 = Color3.fromRGB(255, 120, 40)
throwBtn.AutoButtonColor = false
throwBtn.Size = UDim2.fromOffset(150, 150)
throwBtn.AnchorPoint = Vector2.new(1, 1)
throwBtn.Position = UDim2.new(1, -40, 1, -40)
throwBtn.Image = ""
UI.corner(1, true).Parent = throwBtn
UI.stroke(Color3.fromRGB(80, 30, 0), 5, 0, true).Parent = throwBtn
local tg = UI.gradient(Color3.fromRGB(255, 200, 80), Color3.fromRGB(240, 90, 20), 90)
tg.Parent = throwBtn
UI.label({ Text = "🗡️", TextSize = 60, Size = UDim2.fromScale(1, 0.6), ZIndex = 3, Stroke = 2, Parent = throwBtn })
local throwText = UI.label({ Text = "HOLD", TextSize = 28, Size = UDim2.new(1, 0, 0.3, 0), Position = UDim2.fromScale(0, 0.58), ZIndex = 3, Parent = throwBtn })
local throwScale = Instance.new("UIScale")
throwScale.Parent = throwBtn
throwBtn.Parent = hunt
throwBtn.MouseEnter:Connect(function()
	UI.tween(throwScale, 0.16, { Scale = 1.05 }, Enum.EasingStyle.Back)
	Sfx.ui("hover")
end)
throwBtn.MouseLeave:Connect(function()
	UI.tween(throwScale, 0.16, { Scale = 1 })
end)
throwBtn.InputBegan:Connect(function(input)
	if input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1 then
		UI.tween(throwScale, 0.08, { Scale = 0.9 })
		-- V55: HuntCtl запоминает касание, которое держит заряд (через поле модуля: событие Bindable копирует таблицы)
		Hud.throwTouch = if input.UserInputType == Enum.UserInputType.Touch then input else nil
		Hud.ThrowDown:Fire()
	end
end)
throwBtn.InputEnded:Connect(function(input)
	if input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1 then
		UI.tween(throwScale, 0.25, { Scale = 1 }, Enum.EasingStyle.Back)
		Hud.throwTouch = nil
		Hud.ThrowUp:Fire()
	end
end)

local exitBtn = UI.button({ Text = "Leave", Icon = "⬅️", TextSize = 22, Color = C.red, Size = UDim2.fromOffset(150, 52), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 20, 1, -24) }, function()
	Hud.ExitClicked:Fire()
end)
exitBtn.Parent = hunt
local chanceLabel = UI.label({ Text = "", TextSize = 18, Color = C.dim, Size = UDim2.fromOffset(300, 80), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 20, 1, -90), XAlign = Enum.TextXAlignment.Left, YAlign = Enum.TextYAlignment.Bottom, Stroke = 2, Rich = true, Parent = hunt })

-- V67: переход отметки ×N на шкале. Отметка вспыхивает и раздувается, от неё расходится кольцо и летят искры,
-- над шкалой крупно выскакивает «×N ИМЯ!», экран вспыхивает цветом ступени, шкала вздрагивает.
-- (Толчок камеры, столб света и молнии вокруг героя добавляет HuntCtl.)
local METER_POS = UDim2.new(0.5, 0, 1, -24)
local crossToken = 0
local function crossFx(ti: number, t: any)
	crossToken += 1
	local token = crossToken
	local tick = ticks[ti]
	if tick then
		local sc = tick:FindFirstChildOfClass("UIScale")
		if not sc then
			sc = Instance.new("UIScale")
			sc.Parent = tick
		end
		local tickScale = sc :: UIScale
		tickScale.Scale = 2.8
		UI.tween(tickScale, 0.4, { Scale = 1 }, Enum.EasingStyle.Back)
		UI.burst(UI.screenPos(tick), t.color, 16 + ti * 4, 420)
		-- кольцо от отметки
		local ring = Instance.new("Frame")
		ring.BackgroundTransparency = 1
		ring.AnchorPoint = Vector2.new(0.5, 0.5)
		ring.Position = UDim2.new(tick.Position.X.Scale, 0, 0.5, 0)
		ring.Size = UDim2.fromOffset(24, 24)
		ring.ZIndex = 6
		UI.corner(1, true).Parent = ring
		local rs = UI.stroke(t.color, 6, 0, true)
		rs.Parent = ring
		ring.Parent = barBg
		UI.tween(ring, 0.45, { Size = UDim2.fromOffset(170 + ti * 20, 170 + ti * 20) })
		UI.tween(rs, 0.45, { Transparency = 1 })
		task.delay(0.5, function()
			ring:Destroy()
		end)
	end
	-- «×N ИМЯ!» над шкалой
	local pop = UI.label({ Text = "×" .. t.m .. "  " .. t.name .. "!", TextSize = 58, Color = t.color, Size = UDim2.fromOffset(760, 66), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 0, -36), ZIndex = 30, Stroke = 4, Parent = meter })
	local ps = Instance.new("UIScale")
	ps.Scale = 2.4
	ps.Parent = pop
	UI.tween(ps, 0.28, { Scale = 1 }, Enum.EasingStyle.Back)
	task.delay(0.6, function()
		UI.tween(pop, 0.35, { TextTransparency = 1, Position = UDim2.new(0.5, 0, 0, -80) })
		local st = pop:FindFirstChildOfClass("UIStroke")
		if st then
			UI.tween(st, 0.35, { Transparency = 1 })
		end
		task.delay(0.4, function()
			pop:Destroy()
		end)
	end)
	UI.flash(t.color, 0.35, 0.16 + 0.05 * ti)
	Sfx.play(if ti >= 4 then "boom" else "pop", 1 + ti * 0.04, 0.55)
	-- шкала вздрагивает
	task.spawn(function()
		local t0 = os.clock()
		while os.clock() - t0 < 0.35 and token == crossToken do
			local k = 1 - (os.clock() - t0) / 0.35
			local n = os.clock() * 50
			meter.Position = UDim2.new(0.5, math.noise(n, 3.1) * 16 * k, 1, -24 + math.noise(4.2, n) * 10 * k)
			RunService.RenderStepped:Wait()
		end
		if token == crossToken then
			meter.Position = METER_POS
		end
	end)
end

local lastTier = 0
function Hud.tension(m: number, tremble: number, state: string?)
	local ti = Config.tierIndex(m)
	local t = Theme.tier(ti)
	multLabel.Text = Num.mult(m)
	multLabel.TextColor3 = t.color
	m = math.max(m, 1) -- V68: шкала не опускается ниже ×1
	local x = math.log(m) / LN
	barFill.Size = UDim2.fromScale(math.clamp(x, 0.02, 1), 1)
	fillGrad.Color = ColorSequence.new(t.color2, t.color)
	if state then
		tierLabel.Text = state
	else
		local nxt = Config.TIERS[ti + 1]
		tierLabel.Text = t.name .. (nxt and ("  →  ×" .. nxt.m .. " " .. nxt.name) or "  MAXIMUM!")
	end
	tierLabel.TextColor3 = t.color
	if ti ~= lastTier then
		if ti > lastTier and lastTier > 0 then
			UI.punch(multLabel, 0.45)
			UI.punch(barBg, 0.15)
			Sfx.rise(ti + 2, 0.4)
			UI.burst(UI.screenPos(multLabel), t.color, 10 + ti * 3, 300)
			pcall(crossFx, ti, t)
		end
		lastTier = ti
	end
	-- дрожь
	local k = math.clamp(tremble, 0, 1)
	local amp = 2 + k * 14
	local s = os.clock() * 60
	multLabel.Position = UDim2.new(0.5, math.noise(s, 1) * amp * (0.3 + k), 0, math.noise(s, 2) * amp * (0.3 + k))
	barStroke.Color = k > 0.05 and C.red:Lerp(Color3.new(0, 0, 0), (math.sin(os.clock() * 30) + 1) / 2) or Color3.new(0, 0, 0)
	for _, v in vigParts do
		v.Visible = k > 0.02
		v.BackgroundTransparency = 1 - k * 0.75
	end
	meterScale.Scale = 1 + 0.06 * math.log(math.max(m, 1)) / LN
	throwText.Text = Num.mult(m)
end

function Hud.tensionReset(text: string?)
	lastTier = 0
	multLabel.Text = "×1.0"
	multLabel.TextColor3 = Config.TIERS[1].color
	multLabel.Position = UDim2.new(0.5, 0, 0, 0)
	tierLabel.Text = text or "PRESS AND HOLD"
	tierLabel.TextColor3 = C.text
	barFill.Size = UDim2.fromScale(0, 1)
	barStroke.Color = Color3.new(0, 0, 0)
	meterScale.Scale = 1
	throwText.Text = "HOLD"
	for _, v in vigParts do
		v.Visible = false
	end
end

function Hud.setHint(text: string)
	hint.Text = text
end

function Hud.setChances(text: string)
	chanceLabel.Text = text
end

function Hud.meterVisible(on: boolean)
	meter.Visible = on
	-- V67: на экране броска только шкала: заряд держит ЛКМ, Пробел или палец в любом месте экрана
	throwBtn.Visible = false
end

---------------------------------------------------------------------
-- Баннер зоны и крупные надписи
---------------------------------------------------------------------
local function kp(t: number, v: number)
	return NumberSequenceKeypoint.new(t, v)
end
local bannerHolder = Instance.new("Frame")
bannerHolder.Name = "BannerHolder"
bannerHolder.BackgroundTransparency = 1
bannerHolder.AnchorPoint = Vector2.new(0.5, 0.5)
bannerHolder.Position = UDim2.new(0.5, 0, 0.22, 0)
bannerHolder.Size = UDim2.fromOffset(900, 90)
bannerHolder.Visible = false
bannerHolder.Parent = UI.top

-- Цветная полоса за текстом с мягкими краями
local BAND_W = 2600
local band = Instance.new("Frame")
band.Name = "Band"
band.BorderSizePixel = 0
band.BackgroundColor3 = Color3.new(1, 1, 1)
band.AnchorPoint = Vector2.new(0.5, 0.5)
band.Position = UDim2.new(0.5, 0, 0.5, 18)
band.Size = UDim2.fromOffset(BAND_W, 0)
band.ZIndex = 1
do
	local g = Instance.new("UIGradient")
	g.Transparency = NumberSequence.new({ kp(0, 1), kp(0.2, 0.82), kp(0.5, 0.5), kp(0.8, 0.82), kp(1, 1) })
	g.Parent = band
end
band.Parent = bannerHolder

local banner = UI.label({ Text = "", TextSize = 64, Size = UDim2.fromOffset(900, 80), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Stroke = 5, ZIndex = 3, Parent = bannerHolder })
local bannerScale = Instance.new("UIScale")
bannerScale.Parent = banner
local bannerStroke = banner:FindFirstChildOfClass("UIStroke")
local bannerSub = UI.label({ Text = "", TextSize = 26, Size = UDim2.fromOffset(900, 30), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 1, 10), ZIndex = 3, Parent = banner })
local chip = UI.label({ Text = "", TextSize = 22, Size = UDim2.fromOffset(300, 26), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 0, -2), Color = C.dim, ZIndex = 3, Parent = banner })
local rule = Instance.new("Frame")
rule.Name = "Rule"
rule.BorderSizePixel = 0
rule.AnchorPoint = Vector2.new(0.5, 0)
rule.Position = UDim2.new(0.5, 0, 1, 0)
rule.Size = UDim2.fromOffset(0, 4)
rule.ZIndex = 3
UI.corner(2).Parent = rule
rule.Parent = banner

local bannerRays: Frame? = nil
local bannerToken = 0

local function showBanner(text: string, color: Color3, sub: string?, dur: number?, chipText: string?, fancy: boolean?)
	bannerToken += 1
	local my = bannerToken
	if bannerRays then
		bannerRays:Destroy()
		bannerRays = nil
	end
	banner.Text = text
	banner.TextColor3 = color
	bannerSub.Text = sub or ""
	chip.Text = chipText or ""
	band.BackgroundColor3 = color
	rule.BackgroundColor3 = color
	bannerHolder.Visible = true

	-- стартовое состояние
	bannerScale.Scale = 1.7
	banner.TextTransparency = 1
	if bannerStroke then
		bannerStroke.Transparency = 1
	end
	bannerSub.TextTransparency = 1
	bannerSub.Position = UDim2.new(0.5, 0, 1, 26)
	chip.TextTransparency = 1
	rule.Size = UDim2.fromOffset(0, 4)
	band.Size = UDim2.fromOffset(BAND_W, 0)

	-- вход
	UI.tween(band, 0.35, { Size = UDim2.fromOffset(BAND_W, 112) }, Enum.EasingStyle.Quint)
	UI.tween(bannerScale, 0.5, { Scale = 1 }, Enum.EasingStyle.Back)
	UI.tween(banner, 0.25, { TextTransparency = 0 })
	if bannerStroke then
		UI.tween(bannerStroke, 0.25, { Transparency = 0 })
	end
	UI.tween(rule, 0.55, { Size = UDim2.fromOffset(math.clamp(#text * 12, 220, 620), 4) }, Enum.EasingStyle.Quint)
	task.delay(0.18, function()
		if my ~= bannerToken then
			return
		end
		UI.tween(bannerSub, 0.4, { TextTransparency = 0, Position = UDim2.new(0.5, 0, 1, 10) }, Enum.EasingStyle.Quint)
		UI.tween(chip, 0.4, { TextTransparency = 0 })
	end)
	if fancy then
		pcall(function()
			local r = UI.rays(bannerHolder, color, 10, 620, 16)
			for _, ray in r:GetChildren() do
				if ray:IsA("Frame") then
					ray.BackgroundTransparency = 0.55
				end
			end
			local rs = Instance.new("UIScale")
			rs.Scale = 0
			rs.Parent = r
			UI.tween(rs, 0.6, { Scale = 1 }, Enum.EasingStyle.Back)
			bannerRays = r
			UI.burst(UI.screenPos(banner), color, 16, 280, UI.top)
		end)
	end

	-- выход
	task.delay(dur or 2.2, function()
		if my ~= bannerToken then
			return
		end
		UI.tween(bannerSub, 0.25, { TextTransparency = 1 })
		UI.tween(chip, 0.25, { TextTransparency = 1 })
		UI.tween(rule, 0.3, { Size = UDim2.fromOffset(0, 4) })
		UI.tween(banner, 0.4, { TextTransparency = 1 })
		if bannerStroke then
			UI.tween(bannerStroke, 0.4, { Transparency = 1 })
		end
		UI.tween(bannerScale, 0.4, { Scale = 0.9 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		UI.tween(band, 0.4, { Size = UDim2.fromOffset(BAND_W, 0) }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		local rs = bannerRays and bannerRays:FindFirstChildOfClass("UIScale")
		if rs then
			UI.tween(rs, 0.35, { Scale = 0 })
		end
		task.wait(0.42)
		if my == bannerToken then
			bannerHolder.Visible = false
			if bannerRays then
				bannerRays:Destroy()
				bannerRays = nil
			end
		end
	end)
end

function Hud.banner(text: string, color: Color3, sub: string?, dur: number?)
	showBanner(text, color, sub, dur, nil, false)
end

function Hud.zone(z: number)
	local zc = Config.ZONES[z]
	if zc then
		showBanner(zc.icon .. " " .. string.upper(zc.name) .. " " .. zc.icon, zc.color, zc.desc, 3.2, string.format("ZONE %d / %d", z, #Config.ZONES), true)
		UI.flash(zc.color, 0.6, 0.16)
		Sfx.play("whoosh")
	end
end

---------------------------------------------------------------------
-- Полёт иконок к счётчикам
---------------------------------------------------------------------
function Hud.coinsPos(): Vector2
	return UI.screenPos(coins.icon)
end
function Hud.bagPos(): Vector2
	return UI.screenPos(bag.icon)
end

function Hud.fly(icon: string, from: Vector2, to: Vector2, n: number?, onArrive: (() -> ())?)
	local count = n or 8
	for i = 1, count do
		task.delay((i - 1) * 0.045, function()
			local l = UI.label({ Text = icon, TextSize = 34, Size = UDim2.fromOffset(40, 40), AnchorPoint = Vector2.new(0.5, 0.5), Position = UI.toCanvas(from), ZIndex = 70, Stroke = 2, Parent = UI.top })
			local mid = from + Vector2.new(math.random(-120, 120), math.random(-140, 40))
			local t0 = os.clock()
			local dur = 0.55 + math.random() * 0.15
			local conn
			conn = RunService.RenderStepped:Connect(function()
				local k = math.clamp((os.clock() - t0) / dur, 0, 1)
				local e = k * k
				local a = from:Lerp(mid, k)
				local b = mid:Lerp(to, k)
				local p = a:Lerp(b, e)
				l.Position = UI.toCanvas(p)
				l.TextSize = 34 - 12 * k
				if k >= 1 then
					conn:Disconnect()
					l:Destroy()
					Sfx.play("coin", 1.6 + i * 0.05, 0.25)
					if i == count and onArrive then
						onArrive()
					end
				end
			end)
		end)
	end
end

function Hud.flyCoins(from: Vector2, amount: number)
	local n = math.clamp(math.floor(math.log10(math.max(amount, 1)) * 3) + 4, 4, 18)
	Hud.fly("💰", from, Hud.coinsPos(), n, function()
		UI.punch(coins.frame, 0.25)
		UI.burst(Hud.coinsPos(), C.gold, 12, 260)
	end)
	UI.pop("+" .. Num.short(amount) .. " 💰", C.gold, from, 40)
end

---------------------------------------------------------------------
-- Хотбар внизу по центру: слот 1 = копьё игрока (Tool с атрибутом Spear, как в Cosmetics.refreshTool).
-- Штатную панель инструментов Roblox прячем; клик или клавиша 1 берёт копьё в руку и убирает его.
---------------------------------------------------------------------
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local StarterGui = game:GetService("StarterGui")
local lp = Players.LocalPlayer

task.spawn(function()
	for _ = 1, 10 do
		local ok = pcall(function()
			StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack, false)
		end)
		if ok then
			break
		end
		task.wait(0.5)
	end
end)

-- копьё: (инструмент, в руке ли)
local function findSpear(): (Tool?, boolean)
	local char = lp.Character
	if char then
		for _, c in char:GetChildren() do
			if c:IsA("Tool") and c:GetAttribute("Spear") then
				return c, true
			end
		end
	end
	local bp = lp:FindFirstChildOfClass("Backpack")
	if bp then
		for _, c in bp:GetChildren() do
			if c:IsA("Tool") and c:GetAttribute("Spear") then
				return c, false
			end
		end
	end
	return nil, false
end

local function toggleSpear()
	local char = lp.Character
	local hum = if char then char:FindFirstChildOfClass("Humanoid") else nil
	if not hum or hum.Health <= 0 then
		return
	end
	local tool, equipped = findSpear()
	if not tool then
		return
	end
	if equipped then
		hum:UnequipTools()
	else
		hum:EquipTool(tool)
	end
end

local hotbar = UI.artButton("slot", { Name = "Hotbar1", Size = UDim2.fromOffset(88, 85), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -16), Parent = root }, toggleSpear)
UI.art("ic_spear", { Name = "Icon", Fit = true, Size = UDim2.fromOffset(58, 58), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 0.5, 2), ZIndex = 3, Parent = hotbar })
UI.label({ Name = "Key", Text = "1", TextSize = 20, Size = UDim2.fromOffset(24, 22), Position = UDim2.fromOffset(9, 4), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Stroke = 2, Parent = hotbar })
task.spawn(function()
	local selected = false
	while true do
		local _, eq = findSpear()
		if eq ~= selected then
			selected = eq
			UI.artApply(hotbar, if eq then "slot_sel" else "slot")
			hotbar.Size = if eq then UDim2.fromOffset(98, 96) else UDim2.fromOffset(88, 85)
		end
		task.wait(0.2)
	end
end)
UserInputService.InputBegan:Connect(function(input, processed)
	if processed or input.KeyCode ~= Enum.KeyCode.One then
		return
	end
	if Hud.mode ~= "normal" then -- V72: в тренировке и упаковке слот тоже скрыт и клавиша не работает
		return
	end
	toggleSpear()
end)

---------------------------------------------------------------------
-- Режимы и обновление данных
---------------------------------------------------------------------
local hintToken = 0
function Hud.setMode(mode: string)
	local prev = Hud.mode
	Hud.mode = mode
	Sfx.setMood(mode)
	local normal = mode == "normal"
	if compactMenu then
		if not normal then
			menuOpen = false
		end
		leftBox.Visible = normal and menuOpen
		menuButtons.shop.Visible = normal
		if menuToggle then
			menuToggle.Visible = normal
		end
	else
		leftBox.Visible = normal
	end
	-- V67: на точке броска на экране только шкала заряда: без монет, заданий, шансов и кнопки броска
	right.Visible = normal
	topBar.Visible = mode ~= "cinematic" and mode ~= "hunt"
	hotbar.Visible = normal -- V72: только в обычном режиме (в тренировке он торчал из-под кнопки LIFT)
	hunt.Visible = mode == "hunt"
	chanceLabel.Visible = false
	exitBtn.Visible = true -- V68: кнопка выхода видна всегда (и на ПК, вместе с Q)
	pcall(function()
		GuiService.TouchControlsEnabled = mode ~= "hunt" and mode ~= "cinematic" and mode ~= "busy"
	end)
	if mode == "hunt" then
		Hud.tensionReset()
		Hud.meterVisible(true)
		-- V64: на телефоне заряд держит палец в любом месте экрана (кнопка 🗡️ тоже работает)
		Hud.setHint(UI.mobile and "Hold anywhere on the screen, release in time" or "Hold LMB / Space · release before SLIP · Q to leave")
		-- V67: подсказка видна 3.5 с при входе на точку броска и гаснет; после броска (возврат из сцены улова) не показывается
		hintToken += 1
		local token = hintToken
		local hs = hint:FindFirstChildOfClass("UIStroke")
		if prev == "cinematic" then
			hint.TextTransparency = 1
			if hs then
				hs.Transparency = 1
			end
		else
			hint.TextTransparency = 0
			if hs then
				hs.Transparency = 0
			end
			task.delay(3.5, function()
				if token == hintToken and Hud.mode == "hunt" then
					UI.tween(hint, 0.5, { TextTransparency = 1 })
					if hs then
						UI.tween(hs, 0.5, { Transparency = 1 })
					end
				end
			end)
		end
	end
end

-- V82: в тренировке из верхней панели остаётся только Сила (список сам центрирует её)
function Hud.setTraining(on: boolean)
	coins.frame.Visible = not on
	bag.frame.Visible = not on
	lvlFrame.Visible = not on
end

-- центр карточки Силы на экране (для всплывающих чисел), nil если не видна
function Hud.powerPos(): Vector2?
	local f = power.frame
	if not f or not f.Visible then
		return nil
	end
	return f.AbsolutePosition + f.AbsoluteSize / 2
end

function Hud.refresh(d: any)
	if not d then
		return
	end
	setPill(coins, d.coins)
	setPill(power, d.power, Num.short(d.power))
	local n = #d.items
	setPill(bag, n, string.format("%d/%d", n, d.bagCap))
	bagFull = n >= d.bagCap
	if not bagFull then
		bag.value.TextColor3 = C.text
		bag.icon.Rotation = 0
	end
	setLevel(d.level)
	local need = Config.xpForLevel(d.level)
	xpBar.set(d.xp / need, Num.short(d.xp) .. "/" .. Num.short(need) .. " XP", true)
	refreshQuests(d)
	local bb = menuButtons.bag
	if bb then
		UI.badge(bb, n >= d.bagCap and n or nil)
	end
	bagIsFull = n >= d.bagCap
	updatePassBadge(d)
end

Backend.onChange(Hud.refresh)
Perks.Changed.Event:Connect(function()
	updatePassBadge(Backend.data)
end)

return Hud
