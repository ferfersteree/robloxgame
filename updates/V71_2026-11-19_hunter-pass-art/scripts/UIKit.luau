-- StarterPlayerScripts/Client/UIKit.luau
-- Кирпичики интерфейса: текст с обводкой, сочные кнопки (градиент, тень, «пружина», блик, искры, звук),
-- окна, карточки-плашки, всплывающие цифры, тосты, конфетти, вспышки, лучи, счётчики, вьюпорты.
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local GuiService = game:GetService("GuiService")
local Lighting = game:GetService("Lighting")

local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)

local UI = {}
UI.C = Theme.C
UI.FONT = Theme.FONT
UI.mobile = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled

local player = Players.LocalPlayer
local pgui = player:WaitForChild("PlayerGui")
local camera = workspace.CurrentCamera

local IMG = {
	sparkle = "rbxasset://textures/sparkle.png",
	glow = "rbxasset://textures/glow.png",
	circle = "rbxasset://textures/whiteCircle.png",
	dot = "rbxasset://textures/ui/traildot.png",
	triangle = "rbxasset://textures/triangle.png",
}
UI.IMG = IMG

-- ScreenGui + «холст» с UIScale (холст всегда во весь экран)
local canvases: { { frame: Frame, scale: UIScale } } = {}
local function screen(name: string, order: number, ignoreInset: boolean): Frame
	local g = Instance.new("ScreenGui")
	g.Name = name
	g.ResetOnSpawn = false
	g.IgnoreGuiInset = ignoreInset
	g.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	g.DisplayOrder = order
	local f = Instance.new("Frame")
	f.Name = "Canvas"
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromScale(1, 1)
	local sc = Instance.new("UIScale")
	sc.Parent = f
	f.Parent = g
	g.Parent = pgui
	table.insert(canvases, { frame = f, scale = sc })
	return f
end
UI.root = screen("SpearHud", 1, false)
UI.win = screen("SpearWindows", 5, true)
UI.reveal = screen("SpearReveal", 7, true)
UI.top = screen("SpearFx", 10, true)

local S = 1
local HS = 1 -- масштаб экранных панелей (UI.root); у окон и слоёв эффектов остаётся S
local RSvc = game:GetService("ReplicatedStorage")
-- Проверка на ПК: атрибут ReplicatedStorage.ForceViewport (Vector2, например 812×375) рисует интерфейс в прямоугольнике такого
-- размера в левом верхнем углу (эмуляция телефона), ForceMobileUI = true включает телефонные вещи. Без атрибутов всё как раньше.
local function viewport(): (Vector2, boolean)
	local forced = RSvc:GetAttribute("ForceViewport")
	if typeof(forced) == "Vector2" and forced.X >= 200 and forced.Y >= 200 then
		return forced, true
	end
	return camera.ViewportSize, false
end
local function rescale()
	local vp, forced = viewport()
	S = math.clamp(math.min(vp.Y / 820, vp.X / 1200), 0.48, 1.35)
	-- V60: на телефоне окна высотой 600-650 единиц держат масштаб не выше 0,48-0,55 (иначе не влезут), а панели по
	-- краям экрана (верхняя полоса, задания, кнопки) можно держать крупнее: текст читается и попадать пальцем легче
	HS = S
	if UI.mobile or RSvc:GetAttribute("ForceMobileUI") == true then
		HS = math.clamp(math.min(vp.Y / 820 * 1.25, vp.X / 1400), S, 0.62)
	end
	for _, c in canvases do
		local k = if c.frame == UI.root then HS else S
		c.scale.Scale = k
		if forced then
			-- у UI.root отступ сверху (верхняя полоска Roblox), как у настоящего экрана
			local h = vp.Y
			if c.frame == UI.root then
				h -= GuiService:GetGuiInset().Y
			end
			c.frame.Size = UDim2.fromOffset(vp.X / k, h / k)
			c.frame.ClipsDescendants = true
		else
			c.frame.Size = UDim2.fromScale(1 / k, 1 / k)
			c.frame.ClipsDescendants = false
		end
	end
end
rescale()
camera:GetPropertyChangedSignal("ViewportSize"):Connect(rescale)
RSvc:GetAttributeChangedSignal("ForceViewport"):Connect(rescale)
RSvc:GetAttributeChangedSignal("ForceMobileUI"):Connect(rescale)

function UI.scale(): number
	return S
end

-- Экранные пиксели → смещение на холсте с IgnoreGuiInset
function UI.toCanvas(px: Vector2): UDim2
	return UDim2.fromOffset(px.X / S, px.Y / S)
end

-- Центр объекта в экранных пикселях (с поправкой на верхнюю панель Roblox)
function UI.screenPos(obj: GuiObject): Vector2
	local p = obj.AbsolutePosition + obj.AbsoluteSize / 2
	local sg = obj:FindFirstAncestorWhichIsA("ScreenGui")
	if sg and not sg.IgnoreGuiInset then
		p += GuiService:GetGuiInset()
	end
	return p
end

function UI.worldToScreen(pos: Vector3): (Vector2, boolean)
	local v, on = camera:WorldToViewportPoint(pos)
	return Vector2.new(v.X, v.Y), on and v.Z > 0
end

---------------------------------------------------------------------
-- Базовые
---------------------------------------------------------------------
function UI.new(class: string, props: { [string]: any }?, children: { Instance }?): any
	local inst = Instance.new(class)
	local parent = nil
	if props then
		for k, v in props do
			if k == "Parent" then
				parent = v
			else
				(inst :: any)[k] = v
			end
		end
	end
	if children then
		for _, c in children do
			c.Parent = inst
		end
	end
	if parent then
		inst.Parent = parent
	end
	return inst
end

function UI.corner(r: number?, scale: boolean?): UICorner
	local c = Instance.new("UICorner")
	c.CornerRadius = scale and UDim.new(r or 0.5, 0) or UDim.new(0, r or 14)
	return c
end

function UI.stroke(color: Color3?, thick: number?, transp: number?, border: boolean?): UIStroke
	local s = Instance.new("UIStroke")
	s.Color = color or Theme.C.stroke
	s.Thickness = thick or Theme.STROKE
	s.Transparency = transp or 0
	s.LineJoinMode = Enum.LineJoinMode.Round
	if border then
		s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	end
	return s
end

function UI.pad(px: number, py: number?): UIPadding
	local p = Instance.new("UIPadding")
	p.PaddingLeft = UDim.new(0, px)
	p.PaddingRight = UDim.new(0, px)
	p.PaddingTop = UDim.new(0, py or px)
	p.PaddingBottom = UDim.new(0, py or px)
	return p
end

function UI.list(dir: Enum.FillDirection?, gap: number?, halign: Enum.HorizontalAlignment?, valign: Enum.VerticalAlignment?): UIListLayout
	local l = Instance.new("UIListLayout")
	l.FillDirection = dir or Enum.FillDirection.Vertical
	l.Padding = UDim.new(0, gap or 8)
	l.HorizontalAlignment = halign or Enum.HorizontalAlignment.Center
	l.VerticalAlignment = valign or Enum.VerticalAlignment.Top
	l.SortOrder = Enum.SortOrder.LayoutOrder
	return l
end

function UI.grid(cell: Vector2, gap: number?): UIGridLayout
	local g = Instance.new("UIGridLayout")
	g.CellSize = UDim2.fromOffset(cell.X, cell.Y)
	g.CellPadding = UDim2.fromOffset(gap or 10, gap or 10)
	g.SortOrder = Enum.SortOrder.LayoutOrder
	g.HorizontalAlignment = Enum.HorizontalAlignment.Center
	return g
end

function UI.gradient(c1: Color3, c2: Color3, rot: number?): UIGradient
	local g = Instance.new("UIGradient")
	g.Color = ColorSequence.new(c1, c2)
	g.Rotation = rot or 90
	return g
end

function UI.tween(inst: Instance, t: number, props: { [string]: any }, style: Enum.EasingStyle?, dir: Enum.EasingDirection?): Tween
	local tw = TweenService:Create(inst, TweenInfo.new(t, style or Enum.EasingStyle.Quad, dir or Enum.EasingDirection.Out), props)
	tw:Play()
	return tw
end

-- Текст: белый, FredokaOne, чёрная обводка 3px
function UI.label(p: { [string]: any }): TextLabel
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Font = p.Font or Theme.FONT
	l.Text = p.Text or ""
	l.TextColor3 = p.Color or Theme.C.text
	l.TextSize = p.TextSize or 22
	l.TextScaled = p.Scaled == true
	l.RichText = p.Rich == true
	l.TextWrapped = p.Wrap == true or p.Scaled == true
	l.TextXAlignment = p.XAlign or Enum.TextXAlignment.Center
	l.TextYAlignment = p.YAlign or Enum.TextYAlignment.Center
	l.Size = p.Size or UDim2.fromOffset(200, 30)
	if p.Position then
		l.Position = p.Position
	end
	if p.AnchorPoint then
		l.AnchorPoint = p.AnchorPoint
	end
	if p.ZIndex then
		l.ZIndex = p.ZIndex
	end
	if p.LayoutOrder then
		l.LayoutOrder = p.LayoutOrder
	end
	if p.AutoX then
		l.AutomaticSize = Enum.AutomaticSize.X
	end
	if p.Rotation then
		l.Rotation = p.Rotation
	end
	if p.Name then
		l.Name = p.Name
	end
	if p.Stroke ~= 0 then
		local s = UI.stroke(p.StrokeColor or Theme.C.stroke, p.Stroke or Theme.STROKE)
		s.Parent = l
	end
	if p.MaxSize then
		local c = Instance.new("UITextSizeConstraint")
		c.MaxTextSize = p.MaxSize
		c.Parent = l
	end
	if p.Gradient then
		UI.gradient(p.Gradient[1], p.Gradient[2], 90).Parent = l
	end
	if p.Parent then
		l.Parent = p.Parent
	end
	return l
end

-- Панель: скруглённая, с градиентом и тёмной рамкой
function UI.panel(p: { [string]: any }): Frame
	local f = Instance.new("Frame")
	f.BackgroundColor3 = p.Color or Theme.C.panel
	f.BackgroundTransparency = p.Transparency or 0
	f.Size = p.Size or UDim2.fromOffset(200, 100)
	f.BorderSizePixel = 0
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
	UI.corner(p.Radius or 16).Parent = f
	if p.Line ~= false then
		UI.stroke(p.LineColor or Theme.C.panelLine, p.LineThick or 3, 0, true).Parent = f
	end
	if p.Gradient ~= false then
		local top, bottom = Theme.shades(f.BackgroundColor3)
		UI.gradient(top, bottom, 90).Parent = f
		f.BackgroundColor3 = Color3.new(1, 1, 1)
	end
	if p.Clip then
		f.ClipsDescendants = true
	end
	if p.Parent then
		f.Parent = p.Parent
	end
	return f
end

---------------------------------------------------------------------
-- Искры, всплывашки, вспышки
---------------------------------------------------------------------
type Particle = { g: GuiObject, v: Vector2, life: number, t: number, spin: number, grav: number, fade: boolean, s0: number }
local parts: { Particle } = {}
RunService.RenderStepped:Connect(function(dt)
	for i = #parts, 1, -1 do
		local p = parts[i]
		p.t += dt
		if p.t >= p.life or not p.g.Parent then
			p.g:Destroy()
			table.remove(parts, i)
		else
			p.v += Vector2.new(0, p.grav * dt)
			local pos = p.g.Position
			p.g.Position = UDim2.fromOffset(pos.X.Offset + p.v.X * dt, pos.Y.Offset + p.v.Y * dt)
			p.g.Rotation += p.spin * dt
			local k = p.t / p.life
			if p.g:IsA("ImageLabel") then
				p.g.ImageTransparency = k ^ 2
			elseif p.g:IsA("TextLabel") then
				p.g.TextTransparency = k ^ 2
			else
				p.g.BackgroundTransparency = k ^ 2
			end
			local sz = p.s0 * (1 - 0.5 * k)
			p.g.Size = UDim2.fromOffset(sz, sz * (p.g:GetAttribute("AR") or 1))
		end
	end
end)

-- Взрыв искр в экранной точке (пиксели)
function UI.burst(px: Vector2, color: Color3?, n: number?, speed: number?, layer: Frame?, img: string?)
	local at = px / S
	for _ = 1, n or 10 do
		local a = math.random() * math.pi * 2
		local sp = (speed or 320) * (0.4 + math.random() * 0.8)
		local size = 14 + math.random() * 18
		local g = Instance.new("ImageLabel")
		g.BackgroundTransparency = 1
		g.Image = img or IMG.sparkle
		g.ImageColor3 = color or Theme.C.gold
		g.AnchorPoint = Vector2.new(0.5, 0.5)
		g.Size = UDim2.fromOffset(size, size)
		g.Position = UDim2.fromOffset(at.X, at.Y)
		g.ZIndex = 50
		g.Parent = layer or UI.top
		table.insert(parts, { g = g, v = Vector2.new(math.cos(a), math.sin(a)) * sp, life = 0.5 + math.random() * 0.4, t = 0, spin = (math.random() - 0.5) * 600, grav = 500, fade = true, s0 = size })
	end
end

-- Конфетти сверху экрана
function UI.confetti(n: number?, colors: { Color3 }?)
	local cols = colors or { Theme.C.gold, Theme.C.pink, Theme.C.blue, Theme.C.green, Theme.C.purple, Theme.C.orange }
	local w = camera.ViewportSize.X / S
	for _ = 1, n or 60 do
		local f = Instance.new("Frame")
		f.BorderSizePixel = 0
		f.BackgroundColor3 = cols[math.random(1, #cols)]
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		local s = 8 + math.random() * 10
		f.Size = UDim2.fromOffset(s, s * 0.55)
		f:SetAttribute("AR", 0.55)
		f.Position = UDim2.fromOffset(math.random() * w, -20 - math.random() * 120)
		f.ZIndex = 60
		f.Parent = UI.top
		table.insert(parts, { g = f, v = Vector2.new((math.random() - 0.5) * 200, 120 + math.random() * 260), life = 2.2 + math.random(), t = 0, spin = (math.random() - 0.5) * 720, grav = 160, fade = true, s0 = s })
	end
end

-- Всплывающий текст в экранной точке
function UI.pop(text: string, color: Color3?, px: Vector2?, size: number?, layer: Frame?)
	local vp = camera.ViewportSize
	local at = (px or Vector2.new(vp.X / 2, vp.Y * 0.42)) / S
	local l = UI.label({
		Text = text,
		Color = color or Theme.C.text,
		TextSize = size or 34,
		Size = UDim2.fromOffset(400, (size or 34) + 10),
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromOffset(at.X + math.random(-14, 14), at.Y),
		ZIndex = 55,
		Parent = layer or UI.top,
	})
	local sc = Instance.new("UIScale")
	sc.Scale = 0.3
	sc.Parent = l
	UI.tween(sc, 0.25, { Scale = 1 }, Enum.EasingStyle.Back)
	UI.tween(l, 1.1, { Position = l.Position - UDim2.fromOffset(0, 70) }, Enum.EasingStyle.Quad)
	task.delay(0.65, function()
		UI.tween(l, 0.45, { TextTransparency = 1 })
		local st = l:FindFirstChildOfClass("UIStroke")
		if st then
			UI.tween(st, 0.45, { Transparency = 1 })
		end
	end)
	task.delay(1.2, function()
		l:Destroy()
	end)
end

function UI.popAt(pos: Vector3, text: string, color: Color3?, size: number?)
	local p, on = UI.worldToScreen(pos)
	if on then
		UI.pop(text, color, p, size)
	end
end

-- Вспышка на весь экран
function UI.flash(color: Color3?, dur: number?, alpha: number?)
	local f = Instance.new("Frame")
	f.BorderSizePixel = 0
	f.BackgroundColor3 = color or Color3.new(1, 1, 1)
	f.BackgroundTransparency = 1 - (alpha or 0.8)
	f.Size = UDim2.fromScale(1, 1)
	f.ZIndex = 80
	f.Parent = UI.top
	UI.tween(f, dur or 0.5, { BackgroundTransparency = 1 })
	task.delay((dur or 0.5) + 0.05, function()
		f:Destroy()
	end)
end

-- V64: затемнение экрана (переход на площадку броска). UI.fade(1, 0.2) темнит, UI.fade(0, 0.4) возвращает.
-- Чёрный экран не может остаться навсегда: через hold секунд (по умолчанию 3) он уходит сам.
local fadeFrame: Frame? = nil
local fadeToken = 0
function UI.fade(alpha: number, dur: number?, hold: number?)
	local f = fadeFrame
	if not f or not f.Parent then
		f = Instance.new("Frame")
		f.Name = "Fade"
		f.BorderSizePixel = 0
		f.BackgroundColor3 = Color3.new(0, 0, 0)
		f.BackgroundTransparency = 1
		f.Size = UDim2.fromScale(1, 1)
		f.ZIndex = 500
		f.Parent = UI.top
		fadeFrame = f
	end
	local frame = f :: Frame
	fadeToken += 1
	local token = fadeToken
	local target = 1 - math.clamp(alpha, 0, 1)
	if dur and dur > 0 then
		UI.tween(frame, dur, { BackgroundTransparency = target }, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)
	else
		frame.BackgroundTransparency = target
	end
	if alpha > 0 then
		task.delay((dur or 0) + (hold or 3), function()
			if fadeToken == token and frame.Parent then
				UI.tween(frame, 0.4, { BackgroundTransparency = 1 })
			end
		end)
	end
end

-- V64: линии скорости по краям экрана (как в аниме): пучок полос из центра, середина прозрачная, полосы мерцают.
-- Возвращает объект: set(alpha, color?) и destroy().
function UI.focusLines(count: number?): any
	local holder = Instance.new("Frame")
	holder.Name = "FocusLines"
	holder.BackgroundTransparency = 1
	holder.Size = UDim2.fromScale(1, 1)
	holder.ClipsDescendants = true
	holder.ZIndex = 60
	holder.Visible = false
	local lines: { Frame } = {}
	for _ = 1, count or 26 do
		local l = Instance.new("Frame")
		l.BorderSizePixel = 0
		l.BackgroundColor3 = Color3.new(1, 1, 1)
		l.AnchorPoint = Vector2.new(0.5, 0.5)
		l.Position = UDim2.fromScale(0.5, 0.5)
		l.Size = UDim2.new(1.7, 0, 0, 3)
		l.Rotation = math.random() * 180
		l.ZIndex = 60
		local g = Instance.new("UIGradient")
		g.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.15),
			NumberSequenceKeypoint.new(0.2, 0.7),
			NumberSequenceKeypoint.new(0.3, 1),
			NumberSequenceKeypoint.new(0.7, 1),
			NumberSequenceKeypoint.new(0.8, 0.7),
			NumberSequenceKeypoint.new(1, 0.15),
		})
		g.Parent = l
		l.Parent = holder
		table.insert(lines, l)
	end
	holder.Parent = UI.top
	local self: any = { alpha = 0 }
	local nextFlick = 0
	local conn
	conn = RunService.RenderStepped:Connect(function()
		if not holder.Parent then
			conn:Disconnect()
			return
		end
		if self.alpha <= 0.01 then
			return
		end
		local now = os.clock()
		if now < nextFlick then
			return
		end
		nextFlick = now + 0.05
		-- V65: длина каждой линии по её углу, чтобы край экрана приходился на её яркие концы (на широком экране
		-- концы длиной 1.7 экрана уходили за края, и линии были почти не видны)
		local sc = math.max(UI.scale(), 1e-3)
		local W = math.max(holder.AbsoluteSize.X / sc, 1)
		local H = math.max(holder.AbsoluteSize.Y / sc, 1)
		for _, l in lines do
			local rot = math.random() * 180
			l.Rotation = rot
			local r = math.rad(rot)
			local half = math.min(W / 2 / math.max(math.abs(math.cos(r)), 1e-3), H / 2 / math.max(math.abs(math.sin(r)), 1e-3))
			l.Size = UDim2.new(0, half * 2 * 1.05, 0, 1 + math.random() * 5 * (0.4 + self.alpha))
			l.BackgroundTransparency = 1 - self.alpha * (0.35 + 0.65 * math.random())
		end
	end)
	function self.set(alpha: number, color: Color3?)
		self.alpha = math.clamp(alpha, 0, 1)
		holder.Visible = self.alpha > 0.01
		if color then
			for _, l in lines do
				l.BackgroundColor3 = color
			end
		end
	end
	function self.destroy()
		self.alpha = 0
		holder:Destroy()
	end
	return self
end

-- Лучи (вращающиеся), вернуть Frame; удалить :Destroy()
function UI.rays(parent: Instance, color: Color3, n: number?, size: number?, speed: number?): Frame
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	holder.Position = UDim2.fromScale(0.5, 0.5)
	holder.Size = UDim2.fromOffset(size or 600, size or 600)
	holder.ZIndex = 1
	local count = n or 12
	for i = 1, count do
		local r = Instance.new("Frame")
		r.BorderSizePixel = 0
		r.BackgroundColor3 = color
		r.AnchorPoint = Vector2.new(0.5, 0.5)
		r.Position = UDim2.fromScale(0.5, 0.5)
		r.Size = UDim2.new(1, 0, 0, (size or 600) * 0.07)
		r.Rotation = i * 180 / count
		r.ZIndex = 1
		local g = Instance.new("UIGradient")
		g.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.2, 0.75),
			NumberSequenceKeypoint.new(0.5, 0.25),
			NumberSequenceKeypoint.new(0.8, 0.75),
			NumberSequenceKeypoint.new(1, 1),
		})
		g.Parent = r
		r.Parent = holder
	end
	holder.Parent = parent
	local sp = speed or 25
	local conn
	conn = RunService.RenderStepped:Connect(function(dt)
		if not holder.Parent then
			conn:Disconnect()
			return
		end
		holder.Rotation += sp * dt
	end)
	return holder
end

-- Свечение (круг)
function UI.glow(parent: Instance, color: Color3, size: number, transp: number?): ImageLabel
	local g = Instance.new("ImageLabel")
	g.BackgroundTransparency = 1
	g.Image = IMG.glow
	g.ImageColor3 = color
	g.ImageTransparency = transp or 0.2
	g.AnchorPoint = Vector2.new(0.5, 0.5)
	g.Position = UDim2.fromScale(0.5, 0.5)
	g.Size = UDim2.fromOffset(size, size)
	g.ZIndex = 0
	g.Parent = parent
	return g
end

-- Бегущие цифры
function UI.countUp(label: TextLabel, from: number, to: number, dur: number, fmt: (number) -> string, ticks: boolean?)
	local t0 = os.clock()
	local lastTick = 0
	task.spawn(function()
		while true do
			local k = math.clamp((os.clock() - t0) / dur, 0, 1)
			local e = 1 - (1 - k) ^ 3
			label.Text = fmt(from + (to - from) * e)
			if ticks and os.clock() - lastTick > 0.05 and k < 1 then
				lastTick = os.clock()
				Sfx.play("tick", 1 + k * 1.2, 0.18)
			end
			if k >= 1 then
				break
			end
			RunService.RenderStepped:Wait()
		end
	end)
end

-- «Пружина»: короткий панч масштаба
function UI.punch(obj: GuiObject, amount: number?)
	local sc = obj:FindFirstChild("Punch") :: UIScale?
	if not sc then
		local n = Instance.new("UIScale")
		n.Name = "Punch"
		n.Parent = obj
		sc = n
	end
	local s = sc :: UIScale
	s.Scale = 1 + (amount or 0.2)
	UI.tween(s, 0.35, { Scale = 1 }, Enum.EasingStyle.Back)
end

-- Блик-полоса по объекту (один проход)
function UI.shine(obj: GuiObject, dur: number?)
	local f = obj:FindFirstChild("Shine") :: Frame?
	if not f then
		local n = Instance.new("Frame")
		n.Name = "Shine"
		n.BackgroundColor3 = Color3.new(1, 1, 1)
		n.BorderSizePixel = 0
		n.Size = UDim2.fromScale(1, 1)
		n.ZIndex = obj.ZIndex + 2
		local cr = obj:FindFirstChildOfClass("UICorner")
		if cr then
			cr:Clone().Parent = n
		end
		local g = Instance.new("UIGradient")
		g.Name = "G"
		g.Rotation = 20
		g.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.42, 1),
			NumberSequenceKeypoint.new(0.5, 0.45),
			NumberSequenceKeypoint.new(0.58, 1),
			NumberSequenceKeypoint.new(1, 1),
		})
		g.Offset = Vector2.new(-1, 0)
		g.Parent = n
		n.Parent = obj
		f = n
	end
	local g = (f :: Frame):FindFirstChild("G") :: UIGradient
	g.Offset = Vector2.new(-1, 0)
	UI.tween(g, dur or 0.6, { Offset = Vector2.new(1, 0) }, Enum.EasingStyle.Sine)
end

---------------------------------------------------------------------
-- Кнопка: градиент, тень, обводка, «пружина», блик, искры, звук
---------------------------------------------------------------------
export type ButtonProps = {
	Text: string?,
	Icon: string?,
	Size: UDim2?,
	Position: UDim2?,
	AnchorPoint: Vector2?,
	Color: Color3?,
	TextSize: number?,
	Parent: Instance?,
	Shine: boolean?,
	Sound: string?,
	ZIndex: number?,
	LayoutOrder: number?,
	Round: boolean?,
	Name: string?,
	Burst: boolean?,
	IconSize: number?,
}

local shiny: { [Frame]: boolean } = {}
task.spawn(function()
	while true do
		task.wait(2.6)
		for h in shiny do
			if not h.Parent then
				shiny[h] = nil
			elseif h.Visible then
				local b = h:FindFirstChild("Btn") :: GuiObject?
				if b then
					UI.shine(b, 0.7)
				end
			end
		end
	end
end)

function UI.button(p: ButtonProps, onClick: (() -> ())?): Frame
	local color = p.Color or Theme.C.green
	local top, bottom, line, shadowC = Theme.shades(color)
	local h = Instance.new("Frame")
	h.Name = p.Name or "Button"
	h.BackgroundTransparency = 1
	h.Size = p.Size or UDim2.fromOffset(180, 56)
	if p.Position then
		h.Position = p.Position
	end
	if p.AnchorPoint then
		h.AnchorPoint = p.AnchorPoint
	end
	if p.LayoutOrder then
		h.LayoutOrder = p.LayoutOrder
	end
	local z = p.ZIndex or 2
	h.ZIndex = z
	local sc = Instance.new("UIScale")
	sc.Parent = h
	local rad = p.Round and UDim.new(0.5, 0) or UDim.new(0, 14)
	local shadow = Instance.new("Frame")
	shadow.Name = "Shadow"
	shadow.BorderSizePixel = 0
	shadow.BackgroundColor3 = shadowC
	shadow.Size = UDim2.fromScale(1, 1)
	shadow.Position = UDim2.fromOffset(0, 5)
	shadow.ZIndex = z
	local c1 = Instance.new("UICorner")
	c1.CornerRadius = rad
	c1.Parent = shadow
	shadow.Parent = h
	local b = Instance.new("TextButton")
	b.Name = "Btn"
	b.AutoButtonColor = false
	b.Text = ""
	b.BorderSizePixel = 0
	b.BackgroundColor3 = Color3.new(1, 1, 1)
	b.Size = UDim2.fromScale(1, 1)
	b.ZIndex = z + 1
	local c2 = Instance.new("UICorner")
	c2.CornerRadius = rad
	c2.Parent = b
	local grad = Instance.new("UIGradient")
	grad.Name = "Grad"
	grad.Color = ColorSequence.new(top, bottom)
	grad.Rotation = 90
	grad.Parent = b
	local st = UI.stroke(line, 3, 0, true)
	st.Name = "Line"
	st.Parent = b
	-- верхний «глянец»
	local gloss = Instance.new("Frame")
	gloss.Name = "Gloss"
	gloss.BorderSizePixel = 0
	gloss.BackgroundColor3 = Color3.new(1, 1, 1)
	gloss.BackgroundTransparency = 0.78
	gloss.Size = UDim2.new(1, -10, 0.38, 0)
	gloss.Position = UDim2.fromOffset(5, 3)
	gloss.ZIndex = z + 1
	local c3 = Instance.new("UICorner")
	c3.CornerRadius = p.Round and UDim.new(0.5, 0) or UDim.new(0, 10)
	c3.Parent = gloss
	gloss.Parent = b
	local row = Instance.new("Frame")
	row.Name = "Row"
	row.BackgroundTransparency = 1
	row.Size = UDim2.fromScale(1, 1)
	row.ZIndex = z + 3
	local lay = UI.list(Enum.FillDirection.Horizontal, 6, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center)
	lay.Parent = row
	row.Parent = b
	if p.Icon then
		local ic = UI.label({ Name = "Icon", Text = p.Icon, TextSize = p.IconSize or ((p.TextSize or 24) + 6), Size = UDim2.fromOffset((p.IconSize or (p.TextSize or 24) + 6) + 4, (p.IconSize or (p.TextSize or 24) + 6) + 4), ZIndex = z + 3, Stroke = 2, LayoutOrder = 1 })
		ic.Parent = row
	end
	if p.Text and p.Text ~= "" then
		local tl = UI.label({ Name = "Label", Text = p.Text, TextSize = p.TextSize or 24, Size = UDim2.new(0, 10, 1, 0), AutoX = true, ZIndex = z + 3, LayoutOrder = 2 })
		tl.Parent = row
	end
	b.Parent = h

	local enabled = true
	b.MouseEnter:Connect(function()
		if not enabled then
			return
		end
		UI.tween(sc, 0.15, { Scale = 1.06 }, Enum.EasingStyle.Back)
		Sfx.ui("hover")
		UI.shine(b, 0.45)
		local icon = b:FindFirstChild("Icon", true) :: TextLabel?
		if icon then
			UI.punch(icon, 0.12)
		end
	end)
	b.MouseLeave:Connect(function()
		UI.tween(sc, 0.15, { Scale = 1 })
	end)
	b.MouseButton1Down:Connect(function()
		if not enabled then
			return
		end
		UI.tween(sc, 0.08, { Scale = 0.9 })
		shadow.Position = UDim2.fromOffset(0, 2)
		b.Position = UDim2.fromOffset(0, 3)
	end)
	local function up()
		shadow.Position = UDim2.fromOffset(0, 5)
		b.Position = UDim2.fromOffset(0, 0)
	end
	b.MouseButton1Up:Connect(up)
	b.Activated:Connect(function()
		up()
		if not enabled then
			Sfx.play("error")
			UI.tween(sc, 0.06, { Scale = 0.96 })
			task.delay(0.07, function()
				UI.tween(sc, 0.2, { Scale = 1 }, Enum.EasingStyle.Back)
			end)
			return
		end
		if p.Sound == "open" then
			Sfx.ui("open")
		elseif p.Sound then
			Sfx.play(p.Sound)
		else
			Sfx.ui("press")
		end
		sc.Scale = 0.88
		UI.tween(sc, 0.35, { Scale = 1 }, Enum.EasingStyle.Back)
		if p.Burst ~= false then
			UI.burst(UI.screenPos(b), top, 7, 220)
		end
		if onClick then
			task.spawn(onClick)
		end
	end)
	if p.Shine then
		shiny[h] = true
	end
	h:SetAttribute("Enabled", true)
	h:GetAttributeChangedSignal("Enabled"):Connect(function()
		enabled = h:GetAttribute("Enabled") == true
		grad.Color = enabled and ColorSequence.new(top, bottom) or ColorSequence.new(Color3.fromRGB(150, 150, 156), Color3.fromRGB(100, 100, 108))
		st.Color = enabled and line or Color3.fromRGB(60, 60, 66)
	end)
	if p.Parent then
		h.Parent = p.Parent
	end
	return h
end

---------------------------------------------------------------------
-- V71: картинки интерфейса (рамки, кнопки, иконки, фоны по концептам)
---------------------------------------------------------------------
-- V71: картинки интерфейса. Нарисованы Астрой по концептам (ui-art/source), нарезаны и собраны в 5 листов (ui-art/atlas),
-- загружены в Roblox. ART[имя] = { лист, x, y, ширина, высота } в пикселях листа 1024x1024.
local ART_PAGES = {
	"rbxassetid://112688474389659",
	"rbxassetid://117687606442061",
	"rbxassetid://82021756938807",
	"rbxassetid://138724800947424",
	"rbxassetid://132249786424867",
}
local ART_FULL = { pass_header = { "rbxassetid://103338025764986", 1024, 256 }, shop_banner = { "rbxassetid://123718365046762", 1024, 341 } }
local ART: { [string]: { number } } = {
	badge = { 1, 958, 3, 54, 54 }, bar_cyan = { 1, 250, 988, 238, 21 }, bar_green = { 1, 491, 988, 238, 21 }, bar_purple = { 1, 732, 988, 236, 21 },
	bar_track = { 1, 3, 988, 244, 23 }, broker = { 4, 3, 3, 200, 170 }, btn_big = { 4, 346, 645, 601, 109 }, btn_blue = { 5, 561, 88, 275, 74 },
	btn_buy = { 4, 3, 645, 340, 119 }, btn_green = { 5, 497, 3, 276, 74 }, btn_grey = { 4, 151, 956, 239, 64 }, btn_orange = { 5, 3, 88, 276, 74 },
	btn_purple = { 4, 393, 956, 237, 64 }, btn_red = { 5, 282, 88, 276, 74 }, btn_x = { 2, 893, 632, 122, 120 }, btn_yellow = { 4, 633, 956, 237, 64 },
	charm = { 2, 470, 3, 198, 200 }, chip_blue = { 4, 3, 862, 277, 91 }, chip_dark = { 4, 565, 862, 206, 81 }, chip_gold = { 4, 354, 767, 280, 91 },
	chip_red = { 4, 637, 767, 278, 91 }, chip_violet = { 4, 283, 862, 279, 90 }, chip_xp = { 4, 774, 862, 216, 76 }, coins_chest = { 4, 206, 3, 200, 168 },
	coins_crate = { 3, 603, 408, 200, 189 }, coins_satchel = { 4, 815, 3, 200, 167 }, coins_vault = { 3, 3, 408, 200, 191 }, egg_amber = { 2, 559, 429, 180, 200 },
	egg_forest = { 2, 3, 632, 178, 200 }, egg_tide = { 2, 391, 226, 190, 200 }, founder = { 3, 806, 408, 200, 187 }, ic_bag = { 2, 191, 429, 181, 200 },
	ic_bag2 = { 2, 584, 226, 186, 200 }, ic_coin = { 1, 827, 730, 192, 200 }, ic_deer = { 2, 742, 429, 179, 200 }, ic_gear = { 3, 3, 206, 200, 199 },
	ic_pass = { 4, 409, 3, 200, 168 }, ic_potion = { 2, 869, 3, 146, 200 }, ic_power = { 2, 3, 226, 191, 200 }, ic_quests = { 2, 773, 226, 186, 200 },
	ic_shop = { 3, 815, 206, 200, 192 }, ic_spear = { 2, 3, 429, 185, 200 }, ic_star = { 3, 409, 206, 200, 196 }, insight = { 4, 612, 3, 200, 168 },
	leaves = { 4, 3, 956, 145, 65 }, p_aura = { 2, 3, 835, 200, 186 }, p_calendar = { 2, 671, 3, 195, 200 }, p_check = { 4, 3, 176, 198, 166 },
	p_clock = { 2, 717, 632, 173, 200 }, p_coins = { 4, 813, 176, 200, 145 }, p_dice = { 4, 204, 176, 200, 160 }, p_dumbbell = { 4, 157, 499, 200, 136 },
	p_egg_amber = { 2, 540, 632, 174, 200 }, p_egg_forest = { 2, 184, 632, 175, 200 }, p_egg_storm = { 2, 362, 632, 175, 200 }, p_fair = { 3, 206, 408, 200, 191 },
	p_free = { 3, 409, 408, 191, 191 }, p_lock = { 3, 3, 3, 172, 200 }, p_paw = { 3, 736, 793, 200, 177 }, p_potion = { 2, 375, 429, 181, 200 },
	p_power = { 3, 206, 793, 200, 180 }, p_premium = { 4, 360, 499, 200, 132 }, p_rope = { 4, 610, 176, 200, 154 }, p_tag = { 4, 563, 499, 200, 120 },
	p_target = { 3, 206, 206, 200, 199 }, p_x = { 3, 889, 602, 120, 119 }, panel_menu = { 1, 3, 3, 261, 724 }, panel_quests = { 1, 267, 3, 413, 321 },
	pennant = { 4, 766, 499, 145, 91 }, potion_clover = { 3, 663, 3, 157, 200 }, potion_hands = { 3, 823, 3, 157, 200 }, potion_people = { 3, 178, 3, 159, 200 },
	potion_sun = { 3, 502, 3, 158, 200 }, potion_target = { 3, 340, 3, 159, 200 }, row_cream = { 5, 3, 3, 491, 82 }, shield = { 1, 683, 3, 272, 234 },
	shop_header = { 4, 3, 345, 1000, 151 }, slot = { 4, 3, 499, 151, 143 }, slot_sel = { 2, 859, 835, 152, 155 }, smith = { 3, 3, 793, 200, 187 },
	starter = { 2, 197, 226, 191, 200 }, tile_blue = { 2, 206, 835, 324, 181 }, tile_free = { 2, 240, 3, 227, 219 }, tile_green = { 3, 3, 602, 440, 188 },
	tile_orange = { 3, 409, 793, 324, 179 }, tile_premium = { 2, 3, 3, 234, 220 }, tile_purple = { 2, 533, 835, 323, 180 }, tile_red = { 3, 446, 602, 440, 188 },
	timer = { 4, 3, 767, 348, 92 }, vip = { 4, 407, 176, 200, 160 }, wood_panel = { 1, 3, 730, 821, 255 }, wrap = { 3, 612, 206, 200, 194 },
	xp_fill = { 5, 3, 165, 596, 48 }, xp_track = { 5, 3, 216, 596, 48 },
}
UI.ART = ART

-- размер картинки в пикселях (для пропорций)
function UI.artSize(key: string): Vector2
	local full = ART_FULL[key]
	if full then
		return Vector2.new(full[2], full[3])
	end
	local a = ART[key]
	return if a then Vector2.new(a[4], a[5]) else Vector2.new(1, 1)
end

-- назначить картинку уже созданному ImageLabel / ImageButton. slice: число или { слева, сверху, справа, снизу }
-- (сколько пикселей картинки не растягивается по краям: рамка сохраняет углы при любом размере)
function UI.artApply(img: any, key: string, slice: any?, sliceScale: number?)
	local full = ART_FULL[key]
	local w, h
	if full then
		img.Image = full[1]
		img.ImageRectOffset = Vector2.zero
		img.ImageRectSize = Vector2.zero
		w, h = full[2], full[3]
	else
		local a = ART[key]
		if not a then
			warn("[UI.art] unknown art key " .. tostring(key))
			return
		end
		img.Image = ART_PAGES[a[1]]
		img.ImageRectOffset = Vector2.new(a[2], a[3])
		img.ImageRectSize = Vector2.new(a[4], a[5])
		w, h = a[4], a[5]
	end
	if slice then
		local l, t, r, b
		if type(slice) == "number" then
			l, t, r, b = slice, slice, slice, slice
		else
			l, t, r, b = slice[1], slice[2], slice[3], slice[4]
		end
		img.ScaleType = Enum.ScaleType.Slice
		img.SliceCenter = Rect.new(l, t, w - r, h - b)
		img.SliceScale = sliceScale or 1
	else
		img.ScaleType = Enum.ScaleType.Stretch
	end
end

local function artProps(img: any, key: string, p: { [string]: any })
	img.BackgroundTransparency = 1
	img.BorderSizePixel = 0
	img.Name = p.Name or key
	img.Size = p.Size or UDim2.fromOffset(UI.artSize(key).X, UI.artSize(key).Y)
	if p.Position then
		img.Position = p.Position
	end
	if p.AnchorPoint then
		img.AnchorPoint = p.AnchorPoint
	end
	if p.ZIndex then
		img.ZIndex = p.ZIndex
	end
	if p.LayoutOrder then
		img.LayoutOrder = p.LayoutOrder
	end
	if p.Rotation then
		img.Rotation = p.Rotation
	end
	if p.Color then
		img.ImageColor3 = p.Color
	end
	if p.Transparency then
		img.ImageTransparency = p.Transparency
	end
	UI.artApply(img, key, p.Slice, p.SliceScale)
	if p.Fit then
		img.ScaleType = Enum.ScaleType.Fit -- иконка целиком, пропорции сохраняются
	elseif p.Crop then
		img.ScaleType = Enum.ScaleType.Crop -- фон: заполняет рамку, лишнее обрезается
	end
end

-- Картинка. p: Size, Position, AnchorPoint, ZIndex, LayoutOrder, Name, Parent, Rotation, Color, Transparency,
-- Slice (см. artApply), SliceScale, Fit = true (иконки), Crop = true (фоны)
function UI.art(key: string, p: { [string]: any }?): ImageLabel
	local props = p or {}
	local img = Instance.new("ImageLabel")
	artProps(img, key, props)
	if props.Parent then
		img.Parent = props.Parent
	end
	return img
end

-- Кнопка-картинка: наведение и нажатие с масштабом и звуком. p как у UI.art, плюс Text, TextSize, TextColor, Sound.
-- Подпись лежит в дочернем TextLabel "Label" (UI.setText работает).
function UI.artButton(key: string, p: { [string]: any }?, onClick: (() -> ())?): ImageButton
	local props = p or {}
	local b = Instance.new("ImageButton")
	b.AutoButtonColor = false
	artProps(b, key, props)
	local sc = Instance.new("UIScale")
	sc.Parent = b
	if props.Text then
		local l = UI.label({ Name = "Label", Text = props.Text, TextSize = props.TextSize or 24, Color = props.TextColor, Size = UDim2.fromScale(1, 1), ZIndex = (props.ZIndex or 1) + 1, Stroke = props.Stroke })
		l.Parent = b
	end
	b:SetAttribute("Enabled", true)
	b.MouseEnter:Connect(function()
		if b:GetAttribute("Enabled") then
			UI.tween(sc, 0.15, { Scale = 1.06 }, Enum.EasingStyle.Back)
			Sfx.ui("hover")
		end
	end)
	b.MouseLeave:Connect(function()
		UI.tween(sc, 0.15, { Scale = 1 })
	end)
	b.MouseButton1Down:Connect(function()
		if b:GetAttribute("Enabled") then
			UI.tween(sc, 0.08, { Scale = 0.92 })
		end
	end)
	b.Activated:Connect(function()
		if not b:GetAttribute("Enabled") then
			Sfx.play("error")
			return
		end
		if props.Sound == "open" then
			Sfx.ui("open")
		elseif props.Sound then
			Sfx.play(props.Sound)
		else
			Sfx.ui("press")
		end
		sc.Scale = 0.9
		UI.tween(sc, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
		if onClick then
			task.spawn(onClick)
		end
	end)
	b:GetAttributeChangedSignal("Enabled"):Connect(function()
		b.ImageColor3 = if b:GetAttribute("Enabled") then (props.Color or Color3.new(1, 1, 1)) else Color3.fromRGB(130, 130, 136)
	end)
	if props.Parent then
		b.Parent = props.Parent
	end
	return b
end

function UI.setText(btn: Frame, text: string)
	local l = btn:FindFirstChild("Label", true) :: TextLabel?
	if l then
		l.Text = text
	end
end

function UI.setColor(btn: Frame, color: Color3)
	local top, bottom, line, shadowC = Theme.shades(color)
	local b = btn:FindFirstChild("Btn") :: TextButton?
	if not b then
		return
	end
	(b:FindFirstChild("Grad") :: UIGradient).Color = ColorSequence.new(top, bottom);
	(b:FindFirstChild("Line") :: UIStroke).Color = line;
	(btn:FindFirstChild("Shadow") :: Frame).BackgroundColor3 = shadowC
end

function UI.setEnabled(btn: Frame, on: boolean)
	btn:SetAttribute("Enabled", on)
end

-- Красный кружок-счётчик на кнопке
function UI.badge(btn: Frame, n: number?)
	local b = btn:FindFirstChild("Badge") :: Frame?
	if not n or n <= 0 then
		if b then
			b.Visible = false
		end
		return
	end
	if not b then
		local nb = Instance.new("Frame")
		nb.Name = "Badge"
		nb.BackgroundColor3 = Theme.C.red
		nb.Size = UDim2.fromOffset(26, 26)
		nb.AnchorPoint = Vector2.new(0.5, 0.5)
		nb.Position = UDim2.new(1, -4, 0, 4)
		nb.ZIndex = 20
		UI.corner(1, true).Parent = nb
		UI.stroke(Color3.new(0, 0, 0), 2, 0, true).Parent = nb
		UI.label({ Name = "N", Text = "", TextSize = 16, Size = UDim2.fromScale(1, 1), ZIndex = 21, Stroke = 2, Parent = nb })
		nb.Parent = btn
		b = nb
	end
	local bb = b :: Frame
	bb.Visible = true
	local lbl = bb:FindFirstChild("N") :: TextLabel
	local txt = n > 99 and "99+" or tostring(n)
	if lbl.Text ~= txt then
		lbl.Text = txt
		UI.punch(bb, 0.4)
	end
end

---------------------------------------------------------------------
-- Полоса прогресса
---------------------------------------------------------------------
export type Bar = { frame: Frame, fill: Frame, label: TextLabel, set: (number, string?, boolean?) -> () }
function UI.bar(p: { [string]: any }): Bar
	local f = Instance.new("Frame")
	f.BackgroundColor3 = Color3.fromRGB(20, 22, 40)
	f.Size = p.Size or UDim2.fromOffset(200, 22)
	if p.Position then
		f.Position = p.Position
	end
	if p.AnchorPoint then
		f.AnchorPoint = p.AnchorPoint
	end
	if p.LayoutOrder then
		f.LayoutOrder = p.LayoutOrder
	end
	f.ZIndex = p.ZIndex or 2
	UI.corner(1, true).Parent = f
	UI.stroke(Color3.new(0, 0, 0), 3, 0, true).Parent = f
	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.BorderSizePixel = 0
	fill.BackgroundColor3 = Color3.new(1, 1, 1)
	fill.Size = UDim2.fromScale(0, 1)
	fill.ZIndex = f.ZIndex + 1
	UI.corner(1, true).Parent = fill
	local top, bottom = Theme.shades(p.Color or Theme.C.green)
	local g = UI.gradient(top, bottom, 90)
	g.Parent = fill
	fill.Parent = f
	local lbl = UI.label({ Text = "", TextSize = p.TextSize or 16, Size = UDim2.fromScale(1, 1), ZIndex = f.ZIndex + 2, Stroke = 2, Parent = f })
	local bar: Bar = {
		frame = f,
		fill = fill,
		label = lbl,
		set = function(_k: number, _t: string?, _anim: boolean?) end,
	}
	bar.set = function(k: number, text: string?, anim: boolean?)
		k = math.clamp(k, 0, 1)
		if anim then
			UI.tween(fill, 0.35, { Size = UDim2.fromScale(k, 1) }, Enum.EasingStyle.Quad)
		else
			fill.Size = UDim2.fromScale(k, 1)
		end
		fill.Visible = k > 0.001
		if text then
			lbl.Text = text
		end
	end
	if p.Parent then
		f.Parent = p.Parent
	end
	return bar
end

---------------------------------------------------------------------
-- Тосты (сверху по центру)
---------------------------------------------------------------------
local TOAST = {
	info = { Theme.C.blue, "💬" },
	good = { Theme.C.green, "✅" },
	warn = { Theme.C.orange, "⚠️" },
	bad = { Theme.C.red, "⛔" },
	gold = { Theme.C.gold, "💰" },
	rare = { Theme.C.purple, "✨" },
	quest = { Theme.C.cyan, "📜" },
}
local toastHolder = Instance.new("Frame")
toastHolder.Name = "Toasts"
toastHolder.BackgroundTransparency = 1
toastHolder.AnchorPoint = Vector2.new(0.5, 0)
toastHolder.Position = UDim2.new(0.5, 0, 0, 150)
toastHolder.Size = UDim2.fromOffset(560, 300)
UI.list(Enum.FillDirection.Vertical, 8).Parent = toastHolder
toastHolder.Parent = UI.top

function UI.toast(text: string, kind: string?, dur: number?)
	local k = TOAST[kind or "info"] or TOAST.info
	local f = UI.panel({ Color = k[1], Size = UDim2.fromOffset(10, 50), Radius = 14, Parent = toastHolder })
	f.AutomaticSize = Enum.AutomaticSize.X
	UI.pad(16, 6).Parent = f
	UI.list(Enum.FillDirection.Horizontal, 8, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = f
	UI.label({ Text = k[2], TextSize = 26, Size = UDim2.fromOffset(32, 36), Stroke = 2, LayoutOrder = 1, Parent = f })
	UI.label({ Text = text, TextSize = 24, Size = UDim2.fromOffset(10, 36), AutoX = true, LayoutOrder = 2, Parent = f })
	local sc = Instance.new("UIScale")
	sc.Scale = 0.3
	sc.Parent = f
	UI.tween(sc, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
	if kind == "bad" or kind == "warn" then
		Sfx.play("error")
	end
	task.delay(dur or 2.6, function()
		UI.tween(sc, 0.2, { Scale = 0 })
		task.wait(0.22)
		f:Destroy()
	end)
end

---------------------------------------------------------------------
-- Окна (одно открыто за раз)
---------------------------------------------------------------------
local blur = Lighting:FindFirstChild("Blur") :: BlurEffect?
local current: { id: string, overlay: Frame, win: Frame, onClose: (() -> ())? }? = nil

function UI.closeWindow(silent: boolean?)
	local c = current
	if not c then
		return
	end
	current = nil
	-- Release 3D previews immediately; the inexpensive window frame can finish
	-- its closing tween without retaining another page of models.
	for _,node in c.win:GetDescendants() do
		if node:IsA("ViewportFrame") then node:Destroy() end
	end
	if not silent then
		Sfx.play("close")
	end
	local sc = c.win:FindFirstChildOfClass("UIScale")
	if sc then
		UI.tween(sc, 0.16, { Scale = 0.7 })
	end
	UI.tween(c.overlay, 0.18, { BackgroundTransparency = 1 })
	if blur then
		UI.tween(blur, 0.2, { Size = 0 })
	end
	task.delay(0.17, function()
		c.overlay:Destroy()
	end)
	if c.onClose then
		task.spawn(c.onClose)
	end
end

function UI.windowOpen(id: string?): boolean
	if id then
		return current ~= nil and current.id == id
	end
	return current ~= nil
end

function UI.window(id: string, title: string, size: Vector2, color: Color3?, onClose: (() -> ())?): (Frame, Frame)
	UI.closeWindow(true)
	local overlay = Instance.new("TextButton")
	overlay.Name = "Overlay_" .. id
	overlay.Text = ""
	overlay.AutoButtonColor = false
	overlay.BackgroundColor3 = Color3.new(0, 0, 0)
	overlay.BackgroundTransparency = 1
	overlay.Size = UDim2.fromScale(1, 1)
	overlay.ZIndex = 1
	overlay.Parent = UI.win
	UI.tween(overlay, 0.2, { BackgroundTransparency = 0.45 })
	if blur then
		UI.tween(blur, 0.25, { Size = 10 })
	end
	local win = UI.panel({ Color = Theme.C.panel, Size = UDim2.fromOffset(size.X, size.Y), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.53), Radius = 22, LineThick = 4, ZIndex = 2 })
	win.Name = "Window"
	-- V71: рамка окна из картинки (бирюзовая рама с верёвочными углами, как панели на главном экране).
	-- Свою заливку и обводку панель теряет; окна со своим оформлением (магазин, пропуск) убирают WinArt сами.
	win.BackgroundTransparency = 1
	for _, c in win:GetChildren() do
		if c:IsA("UIStroke") or c:IsA("UIGradient") then
			c:Destroy()
		end
	end
	UI.art("panel_quests", { Name = "WinArt", Size = UDim2.new(1, 12, 1, 12), Position = UDim2.fromOffset(-6, -6), Slice = 58, SliceScale = 0.75, ZIndex = 2, Parent = win })
	local sc = Instance.new("UIScale")
	sc.Scale = 0.55
	sc.Parent = win
	win.Parent = overlay
	UI.tween(sc, 0.32, { Scale = 1 }, Enum.EasingStyle.Back)
	local hc = color or Theme.C.blue
	local header = UI.panel({ Color = hc, Size = UDim2.new(1, -28, 0, 58), Position = UDim2.fromOffset(14, -20), Radius = 16, LineThick = 4, ZIndex = 4, Parent = win })
	header.Name = "Header"
	UI.label({ Text = title, TextSize = 36, Size = UDim2.new(1, -80, 1, 0), Position = UDim2.fromOffset(16, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 6, Parent = header })
	UI.shine(header, 0.8)
	local close = UI.artButton("btn_x", { Name = "Button", Size = UDim2.fromOffset(56, 55), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(1, -10, 0, -12), ZIndex = 8, Sound = "close" }, function()
		UI.closeWindow()
	end)
	close.Parent = win
	local body = Instance.new("Frame")
	body.Name = "Body"
	body.BackgroundTransparency = 1
	body.Position = UDim2.fromOffset(16, 48)
	body.Size = UDim2.new(1, -32, 1, -62)
	body.ZIndex = 3
	body.Parent = win
	overlay.Activated:Connect(function()
		-- клик мимо окна закрывает
		local m = UserInputService:GetMouseLocation()
		local p, s = win.AbsolutePosition, win.AbsoluteSize
		if m.X < p.X or m.Y < p.Y or m.X > p.X + s.X or m.Y > p.Y + s.Y then
			UI.closeWindow()
		end
	end)
	current = { id = id, overlay = overlay :: any, win = win, onClose = onClose }
	Sfx.play("open")
	return win, body
end

-- Прокручиваемый список/сетка внутри тела окна
function UI.scroll(parent: Instance, size: UDim2?, pos: UDim2?): ScrollingFrame
	local s = Instance.new("ScrollingFrame")
	s.BackgroundTransparency = 1
	s.BorderSizePixel = 0
	s.Size = size or UDim2.fromScale(1, 1)
	if pos then
		s.Position = pos
	end
	s.ScrollBarThickness = 8
	s.ScrollBarImageColor3 = Color3.fromRGB(255, 255, 255)
	s.ScrollBarImageTransparency = 0.4
	s.AutomaticCanvasSize = Enum.AutomaticSize.Y
	s.CanvasSize = UDim2.new()
	s.ScrollingDirection = Enum.ScrollingDirection.Y
	s.ZIndex = 3
	s.Parent = parent
	return s
end

---------------------------------------------------------------------
-- Вьюпорт с моделью (автокадр, медленное вращение)
---------------------------------------------------------------------
local spinning: { [ViewportFrame]: { model: Model, yaw: number, speed: number, center: CFrame } } = {}
local function viewportVisible(vp: ViewportFrame): boolean
	if not vp:IsDescendantOf(pgui) or not vp.Visible then return false end
	local at,size=vp.AbsolutePosition,vp.AbsoluteSize
	if size.X<=0 or size.Y<=0 then return false end
	local p: Instance?=vp.Parent
	while p and p~=pgui do
		if p:IsA("GuiObject") then
			if not p.Visible then return false end
			if p.ClipsDescendants then
				local origin,extent=p.AbsolutePosition,p.AbsoluteSize
				if at.X+size.X<origin.X or at.Y+size.Y<origin.Y or at.X>origin.X+extent.X or at.Y>origin.Y+extent.Y then return false end
			end
		elseif p:IsA("LayerCollector") and not p.Enabled then return false end
		p=p.Parent
	end
	return true
end
local viewportClock=0
RunService.RenderStepped:Connect(function(dt)
	viewportClock+=dt
	if viewportClock<1/30 then return end
	dt=math.min(viewportClock,.1);viewportClock=0
	for vp, s in spinning do
		if not vp.Parent then
			spinning[vp] = nil
		elseif viewportVisible(vp) then
			s.yaw += s.speed * dt
			s.model:PivotTo(s.center * CFrame.Angles(0, s.yaw, 0))
		end
	end
end)

function UI.viewport(model: Model, props: { [string]: any }?, yaw: number?, spin: number?): ViewportFrame
	local vp = Instance.new("ViewportFrame")
	vp.BackgroundTransparency = 1
	vp.Size = UDim2.fromScale(1, 1)
	vp.Ambient = Color3.fromRGB(170, 170, 180)
	vp.LightColor = Color3.fromRGB(255, 250, 240)
	vp.LightDirection = Vector3.new(-0.5, -1, -0.6)
	if props then
		for k, v in props do
			(vp :: any)[k] = v
		end
	end
	local m = model:Clone()
	for _,d in m:GetDescendants() do
		if d:IsA("LuaSourceContainer") then d:Destroy() end
	end
	m:PivotTo(CFrame.new())
	local cf, ext = m:GetBoundingBox()
	local center = CFrame.new(-cf.Position + Vector3.new(0, 0, 0))
	m:PivotTo(center * CFrame.Angles(0, yaw or math.rad(-35), 0))
	m.Parent = vp
	local cam = Instance.new("Camera")
	cam.FieldOfView = 30
	local r = math.max(ext.X, ext.Y, ext.Z) * 0.5
	local dist = r / math.tan(math.rad(15)) * 1.05
	cam.CFrame = CFrame.lookAt(Vector3.new(0, r * 0.35, -dist), Vector3.new(0, 0, 0))
	cam.Parent = vp
	vp.CurrentCamera = cam
	if spin and spin ~= 0 then
		spinning[vp] = { model = m, yaw = yaw or math.rad(-35), speed = spin, center = center }
	end
	return vp
end

return UI
