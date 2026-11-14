-- StarterPlayerScripts/Client/Hud.luau
-- Экран: верхняя панель (монеты, сила, сумка, уровень+опыт), меню слева, бусты и задания справа,
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

local Hud = {}
Hud.mode = "normal"
Hud.ThrowDown = Instance.new("BindableEvent")
Hud.ThrowUp = Instance.new("BindableEvent")
Hud.ExitClicked = Instance.new("BindableEvent")
Hud.MenuClicked = Instance.new("BindableEvent") -- (name)

local C = Theme.C
local root = UI.root

---------------------------------------------------------------------
-- Верхняя панель
---------------------------------------------------------------------
local topBar = Instance.new("Frame")
topBar.Name = "TopBar"
topBar.BackgroundTransparency = 1
topBar.AnchorPoint = Vector2.new(0.5, 0)
topBar.Position = UDim2.new(0.5, 0, 0, 8)
topBar.Size = UDim2.fromOffset(820, 64)
UI.list(Enum.FillDirection.Horizontal, 14, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = topBar
topBar.Parent = root

type Pill = { frame: Frame, value: TextLabel, icon: TextLabel, shown: number }
local function pill(icon: string, color: Color3, width: number, order: number): Pill
	local f = UI.panel({ Color = color, Size = UDim2.fromOffset(width, 48), Radius = 24, LineThick = 3, LayoutOrder = order, Parent = topBar })
	local ic = UI.label({ Text = icon, TextSize = 38, Size = UDim2.fromOffset(56, 56), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0, 6, 0.5, 0), ZIndex = 4, Stroke = 2, Parent = f })
	local v = UI.label({ Text = "0", TextSize = 28, Size = UDim2.new(1, -44, 1, 0), Position = UDim2.fromOffset(36, 0), ZIndex = 4, Parent = f })
	return { frame = f, value = v, icon = ic, shown = 0 }
end
local coins = pill("💰", Color3.fromRGB(255, 186, 40), 190, 1)
local power = pill("💪", Color3.fromRGB(255, 96, 80), 150, 2)
local bag = pill("🎒", Color3.fromRGB(80, 170, 255), 150, 3)

-- уровень: звезда + полоса опыта
local lvlFrame = UI.panel({ Color = Color3.fromRGB(110, 90, 230), Size = UDim2.fromOffset(220, 48), Radius = 24, LineThick = 3, LayoutOrder = 4, Parent = topBar })
local star = UI.label({ Text = "⭐", TextSize = 50, Size = UDim2.fromOffset(60, 60), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0, 8, 0.5, 0), ZIndex = 4, Stroke = 2, Parent = lvlFrame })
local lvlNum = UI.label({ Text = "1", TextSize = 22, Size = UDim2.fromOffset(60, 60), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0, 8, 0.5, 2), ZIndex = 5, Parent = lvlFrame })
local xpBar = UI.bar({ Color = C.xp, Size = UDim2.new(1, -68, 0, 22), Position = UDim2.fromOffset(54, 13), ZIndex = 4, TextSize = 14, Parent = lvlFrame })
local _ = star

-- Верхняя панель: анимации (вход, «дыхание» иконок, всплывающие +N, шкала рюкзака, уровень)
local pills = { coins, power, bag }
local bagFull = false
local starBusy = false
local lastLevel: number? = nil
local primed: { [any]: boolean } = {}

-- тонкая шкала заполнения рюкзака под числом
local bagFillBack = Instance.new("Frame")
bagFillBack.Name = "FillBack"
bagFillBack.BorderSizePixel = 0
bagFillBack.BackgroundColor3 = Color3.fromRGB(10, 40, 80)
bagFillBack.BackgroundTransparency = 0.35
bagFillBack.Position = UDim2.new(0, 58, 1, -9)
bagFillBack.Size = UDim2.new(1, -72, 0, 4)
bagFillBack.ZIndex = 4
UI.corner(3).Parent = bagFillBack
local bagFillBar = Instance.new("Frame")
bagFillBar.Name = "Fill"
bagFillBar.BorderSizePixel = 0
bagFillBar.BackgroundColor3 = Color3.fromRGB(170, 225, 255)
bagFillBar.Size = UDim2.fromScale(0, 1)
bagFillBar.ZIndex = 5
UI.corner(3).Parent = bagFillBar
bagFillBar.Parent = bagFillBack
bagFillBack.Parent = bag.frame
bag.value.Position = UDim2.fromOffset(50, -4)

local function setBagFill(n: number, cap: number)
	local k = if cap > 0 then math.clamp(n / cap, 0, 1) else 0
	local col = if k >= 1 then C.red elseif k > 0.75 then C.orange else Color3.fromRGB(170, 225, 255)
	UI.tween(bagFillBar, 0.35, { Size = UDim2.fromScale(k, 1), BackgroundColor3 = col }, Enum.EasingStyle.Quint)
end

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

-- Оформление: иконки живут в круглых бейджах ВНУТРИ панели, глянец, искорки
local function decoratePill(frame: Frame, color: Color3, glyphs: { TextLabel }, glyphSize: number): Frame
	local top, bottom, line = Theme.shades(color)
	local badge = Instance.new("Frame")
	badge.Name = "Badge"
	badge.AnchorPoint = Vector2.new(0.5, 0.5)
	badge.Position = UDim2.new(0, 25, 0.5, 0)
	badge.Size = UDim2.fromOffset(36, 36)
	badge.BackgroundColor3 = Color3.new(1, 1, 1)
	badge.BorderSizePixel = 0
	badge.ZIndex = 3
	UI.corner(18).Parent = badge
	UI.stroke(line, 2, 0, true).Parent = badge
	UI.gradient(bottom:Lerp(top, 0.25), bottom:Lerp(Color3.new(0, 0, 0), 0.25), 90).Parent = badge
	badge.Parent = frame
	for _, g in glyphs do
		g.Parent = badge
		g.AnchorPoint = Vector2.new(0.5, 0.5)
		g.Position = UDim2.fromScale(0.5, 0.5)
		g.Size = UDim2.fromOffset(36, 36)
		g.TextSize = glyphSize
		g.ZIndex = 5
	end
	local gloss = Instance.new("Frame")
	gloss.Name = "Gloss"
	gloss.BackgroundColor3 = Color3.new(1, 1, 1)
	gloss.BackgroundTransparency = 0.8
	gloss.BorderSizePixel = 0
	gloss.Position = UDim2.new(0, 52, 0, 4)
	gloss.Size = UDim2.new(1, -64, 0, 7)
	gloss.ZIndex = 3
	UI.corner(4).Parent = gloss
	gloss.Parent = frame
	return badge
end

local badges: { Frame } = {}
do
	local specs = {
		{ coins, Color3.fromRGB(255, 186, 40) },
		{ power, Color3.fromRGB(255, 96, 80) },
		{ bag, Color3.fromRGB(80, 170, 255) },
	}
	for _, s in specs do
		local p: Pill = s[1]
		table.insert(badges, decoratePill(p.frame, s[2], { p.icon }, 24))
		p.value.Position = UDim2.fromOffset(50, 0)
		p.value.Size = UDim2.new(1, -58, 1, 0)
	end
	local lb = decoratePill(lvlFrame, Color3.fromRGB(110, 90, 230), { star }, 30)
	table.insert(badges, lb)
	lvlNum.Parent = lb
	lvlNum.AnchorPoint = Vector2.new(0.5, 0.5)
	lvlNum.Position = UDim2.fromScale(0.5, 0.54)
	lvlNum.Size = UDim2.fromOffset(36, 36)
	lvlNum.TextSize = 15
	lvlNum.ZIndex = 6
end

-- редкие «искорки» на бейджах
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
			UI.tween(sp, 0.3, { Size = UDim2.fromOffset(16, 16), Rotation = 45 }, Enum.EasingStyle.Back)
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
	lvlNum.Text = tostring(level)
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
local left = UI.panel({
	Name = "LeftMenu", Color = C.panel, Transparency = 0.12,
	Size = UDim2.fromOffset(190, 10), AnchorPoint = Vector2.new(0, 0.5),
	Position = UDim2.new(0, 12, 0.5, 0), Radius = 22, LineThick = 2, Parent = root,
})
left.AutomaticSize = Enum.AutomaticSize.Y
UI.pad(10, 10).Parent = left
UI.list(Enum.FillDirection.Vertical, 9, Enum.HorizontalAlignment.Center).Parent = left
UI.label({ Text = "🌲 CAMP", TextSize = 18, Color = C.dim, Size = UDim2.fromOffset(168, 28), LayoutOrder = 0, Parent = left })

local menuButtons: { [string]: Frame } = {}
local MENU = {
	{ "shop", "🎁", "Shop", Color3.fromRGB(232, 64, 62) },
	{ "bag", "🎒", "Bag", Color3.fromRGB(78, 174, 239) },
	{ "spears", "🔱", "Spears", Color3.fromRGB(242, 145, 66) },
	{ "index", "🐾", "Animals", Color3.fromRGB(103, 195, 112) },
	{ "quests", "📜", "Quests", Color3.fromRGB(62, 190, 181) },
	{ "potions", "🧪", "Potions", Color3.fromRGB(190, 112, 210) },
	{ "settings", "⚙️", "Settings", Color3.fromRGB(117, 139, 145) },
}
-- Панель читов видна только разработчику в Studio, в живой игре её нет
if Config.BACKEND == "Demo" and RunService:IsStudio() then
	table.insert(MENU, { "demo", "🛠️", "DEMO", Color3.fromRGB(225, 85, 115) })
end
for i, m in MENU do
	local b = UI.button({
		Text = string.upper(m[3]), Icon = m[2], IconSize = 29, TextSize = 18,
		Color = m[4], Size = UDim2.fromOffset(168, 56), LayoutOrder = i,
		Shine = i == 1,
	}, function()
		Hud.MenuClicked:Fire(m[1])
	end)
	b.Parent = left
	menuButtons[m[1]] = b
end

function Hud.menuButton(name: string): Frame?
	return menuButtons[name]
end

---------------------------------------------------------------------
-- Справа: бусты и задания
---------------------------------------------------------------------
local right = Instance.new("Frame")
right.Name = "RightPanel"
right.BackgroundTransparency = 1
right.AnchorPoint = Vector2.new(1, 0.5)
right.Position = UDim2.new(1, -12, 0.42, 0)
right.Size = UDim2.fromOffset(250, 420)
UI.list(Enum.FillDirection.Vertical, 8, Enum.HorizontalAlignment.Right).Parent = right
right.Parent = root

local boostBox = Instance.new("Frame")
boostBox.BackgroundTransparency = 1
boostBox.Size = UDim2.fromOffset(250, 10)
boostBox.AutomaticSize = Enum.AutomaticSize.Y
boostBox.LayoutOrder = 1
UI.list(Enum.FillDirection.Vertical, 6, Enum.HorizontalAlignment.Right).Parent = boostBox
boostBox.Parent = right

local questBox = UI.panel({ Color = Color3.fromRGB(40, 48, 84), Size = UDim2.fromOffset(250, 10), Radius = 14, LineThick = 3, LayoutOrder = 2, Parent = right })
questBox.AutomaticSize = Enum.AutomaticSize.Y
UI.pad(10, 8).Parent = questBox
UI.list(Enum.FillDirection.Vertical, 6, Enum.HorizontalAlignment.Left).Parent = questBox
UI.label({ Text = "📜 QUESTS", TextSize = 20, Size = UDim2.new(1, 0, 0, 24), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, LayoutOrder = 0, Parent = questBox })
local questRows: { Frame } = {}

local boostRows: { [string]: { frame: Frame, label: TextLabel } } = {}
local function refreshBoosts()
	for id, b in Config.BOOSTS do
		local left_ = Backend.boostLeft(id)
		local row = boostRows[id]
		if left_ > 0 then
			if not row then
				local f = UI.panel({ Color = b.color, Size = UDim2.fromOffset(200, 40), Radius = 20, LineThick = 3, Parent = boostBox })
				UI.label({ Text = b.icon, TextSize = 28, Size = UDim2.fromOffset(40, 40), Position = UDim2.fromOffset(2, 0), ZIndex = 4, Stroke = 2, Parent = f })
				local l = UI.label({ Text = "", TextSize = 18, Size = UDim2.new(1, -46, 1, 0), Position = UDim2.fromOffset(40, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Parent = f })
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
		local f = Instance.new("Frame")
		f.BackgroundTransparency = 1
		f.Size = UDim2.new(1, 0, 0, 44)
		f.LayoutOrder = i
		f.ZIndex = 4
		UI.label({ Text = e.q.text, TextSize = 15, Size = UDim2.new(1, 0, 0, 18), XAlign = Enum.TextXAlignment.Left, ZIndex = 4, Stroke = 2, Scaled = true, MaxSize = 15, Parent = f })
		local bar = UI.bar({ Color = e.st.done and C.gold or C.green, Size = UDim2.new(1, 0, 0, 18), Position = UDim2.fromOffset(0, 22), ZIndex = 4, TextSize = 13, Parent = f })
		bar.set(e.st.p / e.q.goal, e.st.done and "DONE! Claim your reward" or (Num.short(e.st.p) .. " / " .. Num.short(e.q.goal)))
		if e.st.done then
			ready += 1
		end
		f.Parent = questBox
		table.insert(questRows, f)
	end
	questBox.Visible = #list > 0
	local qb = menuButtons.quests
	if qb then
		UI.badge(qb, ready)
	end
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
for i, t in Config.TIERS do
	if i > 1 then
		local x = math.log(t.m) / LN
		local tick = Instance.new("Frame")
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
		Hud.ThrowDown:Fire()
	end
end)
throwBtn.InputEnded:Connect(function(input)
	if input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1 then
		UI.tween(throwScale, 0.25, { Scale = 1 }, Enum.EasingStyle.Back)
		Hud.ThrowUp:Fire()
	end
end)

local exitBtn = UI.button({ Text = "Leave", Icon = "⬅️", TextSize = 22, Color = C.red, Size = UDim2.fromOffset(150, 52), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 20, 1, -24) }, function()
	Hud.ExitClicked:Fire()
end)
exitBtn.Parent = hunt
local chanceLabel = UI.label({ Text = "", TextSize = 18, Color = C.dim, Size = UDim2.fromOffset(300, 80), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 20, 1, -90), XAlign = Enum.TextXAlignment.Left, YAlign = Enum.TextYAlignment.Bottom, Stroke = 2, Rich = true, Parent = hunt })

local lastTier = 0
function Hud.tension(m: number, tremble: number, state: string?)
	local ti = Config.tierIndex(m)
	local t = Theme.tier(ti)
	multLabel.Text = Num.mult(m)
	multLabel.TextColor3 = t.color
	local x = math.log(math.max(m, 1)) / LN
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
	throwBtn.Visible = on
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
-- Режимы и обновление данных
---------------------------------------------------------------------
function Hud.setMode(mode: string)
	Hud.mode = mode
	Sfx.setMood(mode)
	local normal = mode == "normal"
	left.Visible = normal
	right.Visible = normal or mode == "hunt"
	topBar.Visible = mode ~= "cinematic"
	hunt.Visible = mode == "hunt"
	pcall(function()
		GuiService.TouchControlsEnabled = mode ~= "hunt" and mode ~= "cinematic" and mode ~= "busy"
	end)
	if mode == "hunt" then
		Hud.tensionReset()
		Hud.meterVisible(true)
		Hud.setHint(UI.mobile and "Hold the 🗡️ button, then release in time" or "Hold LMB / Space · release before SLIP · Q to leave")
	end
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
	setBagFill(n, d.bagCap)
	setLevel(d.level)
	local need = Config.xpForLevel(d.level)
	xpBar.set(d.xp / need, Num.short(d.xp) .. " / " .. Num.short(need), true)
	refreshQuests(d)
	local bb = menuButtons.bag
	if bb then
		UI.badge(bb, n >= d.bagCap and n or nil)
	end
end

Backend.onChange(Hud.refresh)

return Hud
