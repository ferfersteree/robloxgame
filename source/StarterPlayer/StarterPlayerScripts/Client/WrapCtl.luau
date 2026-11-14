-- StarterPlayerScripts/Client/WrapCtl.luau
-- Стол упаковки в СВОЕЙ хижине. Выбери добычу → зверёк прыгает на бумагу → тапни 4 края (клапаны
-- складываются в коробку) → зажми, чтобы обмотать верёвкой (2 петли) → тапни бантик → штамп «×2»,
-- свёрток улетает в сумку. Сервер: WrapStart(id) → WrapFinish(id) (цена × Config.WRAP_MULT).
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Fauna150 = require(game:GetService("ReplicatedStorage"):WaitForChild("Fauna150"))
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local UI = require(script.Parent.UIKit)
local Perks = require(script.Parent.Perks)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Fx = require(script.Parent.WorldFx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Animator = require(script.Parent.Animator)
local AnimalRig = require(script.Parent.AnimalRig)
local Card = require(script.Parent.Card)
local Activities = require(script.Parent.Activities)

local WrapCtl = {}
WrapCtl.active = false

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera
local C = Theme.C

-- Коробка (студы): дно A×A, стенки высотой H, бумага толщиной T, верёвка RW
local A = 2.0
local H = 1.1
local T = 0.06
local RW = 0.1
local FOLD_TIME = 0.45
local ROPE_TIME = 1.8
-- Клапаны: поворот вокруг Y (0 — вправо, 90 — к игроку), длина верхней части b, высота стенки h.
-- Передний/задний чуть выше и шире — их верх ложится поверх боковых без мерцания.
local FLAPS = {
	{ yaw = 0, b = A / 2, h = H, w = A },
	{ yaw = 90, b = 0.7, h = H + T, w = A + T },
	{ yaw = 180, b = A / 2, h = H, w = A },
	{ yaw = 270, b = 0.7, h = H + T, w = A + T },
}
-- Верёвка: 2 петли по 3 видимых отрезка (в координатах поверхности стола)
local HX = A / 2 + T / 2 + RW / 2 + 0.01
local TY = H + 2 * T + RW / 2 + 0.01
local TY2 = TY + RW * 0.9
local SEGS = {
	{ Vector3.new(-HX, 0.03, 0), Vector3.new(-HX, TY, 0) },
	{ Vector3.new(-HX - RW / 2, TY, 0), Vector3.new(HX + RW / 2, TY, 0) },
	{ Vector3.new(HX, TY, 0), Vector3.new(HX, 0.03, 0) },
	{ Vector3.new(0, 0.03, -HX), Vector3.new(0, TY2, -HX) },
	{ Vector3.new(0, TY2, -HX - RW / 2), Vector3.new(0, TY2, HX + RW / 2) },
	{ Vector3.new(0, TY2, HX), Vector3.new(0, 0.03, HX) },
}
local BOW_Y = TY2 + RW / 2
-- Бумага и верёвка по редкости
local STYLE = {
	{ paper = Color3.fromRGB(226, 196, 146), mat = Enum.Material.Plastic, rope = Color3.fromRGB(196, 58, 48) },
	{ paper = Color3.fromRGB(150, 222, 150), mat = Enum.Material.Plastic, rope = Color3.fromRGB(255, 255, 255) },
	{ paper = Color3.fromRGB(124, 184, 255), mat = Enum.Material.Plastic, rope = Color3.fromRGB(255, 255, 255) },
	{ paper = Color3.fromRGB(190, 134, 255), mat = Enum.Material.Plastic, rope = Color3.fromRGB(255, 214, 80) },
	{ paper = Color3.fromRGB(255, 206, 84), mat = Enum.Material.Plastic, rope = Color3.fromRGB(214, 40, 60) },
	{ paper = Color3.fromRGB(255, 120, 160), mat = Enum.Material.Plastic, rope = Color3.fromRGB(255, 255, 255), rainbow = true },
}

type Flap = { def: any, a: Part, b: Part, u: number, goal: number, handle: TextButton? }
type Parcel = {
	model: Model,
	style: any,
	flaps: { Flap },
	segs: { Part },
	bow: { { p: Part, off: CFrame, size: Vector3 } },
	painted: { Part },
	rig: any,
}

-- Состояние сессии
local alive = false
local S = CFrame.new() -- центр поверхности стола: Y вверх, −Z к игроку
local cur: Parcel? = nil
local presses: { Vector2 } = {} -- клики/тапы мимо интерфейса; (-1,-1) — Пробел
local holdingInput = false
local holdingBtn = false
local camFrom, camTo, camT0, camDur = CFrame.new(), CFrame.new(), 0, 1
local val: TextLabel? = nil
local handles: { [TextButton]: () -> Vector3 } = {}

local function hrp(): BasePart?
	local c = player.Character
	return c and c:FindFirstChild("HumanoidRootPart") :: BasePart? or nil
end
local function hum(): Humanoid?
	local c = player.Character
	return c and c:FindFirstChildOfClass("Humanoid") or nil
end

local function smooth(x: number): number
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end
local function backOut(x: number): number
	local c1 = 1.70158
	return 1 + (c1 + 1) * (x - 1) ^ 3 + c1 * (x - 1) ^ 2
end

local function hint(text: string)
	if val then
		val.Text = text
	end
end

local function pending(): { any }
	local list = {}
	local d = Backend.data
	if d then
		for _, it in d.items do
			if not it.wrapped then
				table.insert(list, it)
			end
		end
	end
	table.sort(list, function(a, b)
		return a.price > b.price
	end)
	return list
end

local function styleFor(item: any): any
	local sp = Config.SPECIES_BY_ID[item.sp]
	local r = math.clamp(sp and sp.rarity or 1, 1, #STYLE)
	if item.mut == "gold" then
		return STYLE[5]
	elseif item.mut == "rainbow" then
		return STYLE[6]
	end
	return STYLE[r]
end

local function newPart(name: string, size: Vector3, color: Color3, mat: Enum.Material, parent: Instance): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Size = size
	p.Color = color
	p.Material = Enum.Material.Plastic
	p.TopSurface=Enum.SurfaceType.Studs
	p.BottomSurface=Enum.SurfaceType.Studs
	p.LeftSurface=Enum.SurfaceType.Studs
	p.RightSurface=Enum.SurfaceType.Studs
	p.FrontSurface=Enum.SurfaceType.Studs
	p.BackSurface=Enum.SurfaceType.Studs
	p.CastShadow=false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function camFly(to: CFrame, dur: number)
	camFrom = camera.CFrame
	camTo = to
	camT0 = os.clock()
	camDur = dur
end

---------------------------------------------------------------------
-- Геометрия свёртка
---------------------------------------------------------------------
local function placeFlap(fl: Flap)
	local f = fl.def
	local a = math.rad(90) * backOut(math.clamp(fl.u / 0.62, 0, 1))
	local b = math.rad(90) * smooth((fl.u - 0.45) / 0.55)
	local hinge = S * CFrame.Angles(0, math.rad(f.yaw), 0) * CFrame.new(A / 2, T / 2, 0) * CFrame.Angles(0, 0, a)
	fl.a.CFrame = hinge * CFrame.new(f.h / 2, 0, 0)
	fl.b.CFrame = hinge * CFrame.new(f.h, 0, 0) * CFrame.Angles(0, 0, b) * CFrame.new(f.b / 2, 0, 0)
end

local function flapSpot(fl: Flap): Vector3
	local f = fl.def
	return (S * CFrame.Angles(0, math.rad(f.yaw), 0) * CFrame.new(A / 2 + (f.h + f.b) * 0.55, T, 0)).Position
end

local function placeSeg(P: Parcel, i: number, g: number)
	local s = SEGS[i]
	local p = P.segs[i]
	local d = s[2] - s[1]
	local len = d.Magnitude * g
	if len < 0.02 then
		p.Transparency = 1
		return
	end
	p.Transparency = 0
	local ax, ay, az = math.abs(d.X), math.abs(d.Y), math.abs(d.Z)
	if ax >= ay and ax >= az then
		p.Size = Vector3.new(len, RW, RW)
	elseif ay >= az then
		p.Size = Vector3.new(RW, len, RW)
	else
		p.Size = Vector3.new(RW, RW, len)
	end
	p.CFrame = S * CFrame.new(s[1] + d * (g / 2))
end

local function placeBow(P: Parcel, k: number)
	local base = S * CFrame.new(0, BOW_Y, 0)
	for _, e in P.bow do
		local off = e.off
		e.p.Size = e.size * math.max(k, 0.02)
		e.p.CFrame = base * CFrame.new(off.Position * k) * off.Rotation
		e.p.Transparency = k < 0.02 and 1 or 0
	end
end

local function newParcel(item: any): Parcel
	local st = styleFor(item)
	local m = Instance.new("Model")
	m.Name = "WrapParcel"
	local P: Parcel = { model = m, style = st, flaps = {}, segs = {}, bow = {}, painted = {}, rig = nil }
	local base = newPart("Paper", Vector3.new(A, T, A), st.paper, st.mat, m)
	base.CFrame = S * CFrame.new(0, T / 2, 0)
	table.insert(P.painted, base)
	for i, f in FLAPS do
		local a = newPart("FlapA" .. i, Vector3.new(f.h, T, f.w), st.paper, st.mat, m)
		local b = newPart("FlapB" .. i, Vector3.new(f.b, T, f.w), st.paper, st.mat, m)
		a.CanQuery = true
		b.CanQuery = true
		table.insert(P.painted, a)
		table.insert(P.painted, b)
		local fl: Flap = { def = f, a = a, b = b, u = 0, goal = 0, handle = nil }
		table.insert(P.flaps, fl)
		placeFlap(fl)
	end
	for i = 1, #SEGS do
		local p = newPart("Rope", Vector3.new(RW, RW, RW), st.rope, Enum.Material.Plastic, m)
		p.Transparency = 1
		p.CastShadow = false
		P.segs[i] = p
	end
	-- бантик: узел, 2 петли, 2 хвостика
	local function add(shape: Enum.PartType, size: Vector3, off: CFrame)
		local p = newPart("Bow", size, st.rope, Enum.Material.Plastic, m)
		p.Shape = shape
		p.Transparency = 1
		table.insert(P.bow, { p = p, off = off, size = size })
	end
	add(Enum.PartType.Block, Vector3.new(0.3, 0.22, 0.3), CFrame.new(0, 0.1, 0))
	for _, sx in { -1, 1 } do
		add(Enum.PartType.Cylinder, Vector3.new(0.14, 0.62, 0.62), CFrame.new(sx * 0.36, 0.28, 0) * CFrame.Angles(0, 0, math.rad(-sx * 28)) * CFrame.Angles(0, math.rad(90), 0))
		add(Enum.PartType.Block, Vector3.new(0.14, 0.05, 0.62), CFrame.new(sx * 0.2, 0.03, -0.36) * CFrame.Angles(0, math.rad(sx * 28), 0))
	end
	placeBow(P, 0)
	m.Parent = Fx.folder
	return P
end

local function destroyParcel(P: Parcel?)
	if not P then
		return
	end
	if P.rig then
		P.rig:destroy()
		P.rig = nil
	end
	P.model:Destroy()
end

---------------------------------------------------------------------
-- Ручки-подсказки (кружки над краями бумаги)
---------------------------------------------------------------------
local function makeHandle(icon: string, at: () -> Vector3, onTap: () -> ()): TextButton
	local b = Instance.new("TextButton")
	b.Name = "WrapHandle"
	b.Text = icon
	b.TextSize = 34
	b.Font = Theme.FONT
	b.TextColor3 = Color3.new(1, 1, 1)
	b.AutoButtonColor = false
	b.BackgroundColor3 = C.orange
	b.BackgroundTransparency = 0.1
	b.Size = UDim2.fromOffset(74, 74)
	b.AnchorPoint = Vector2.new(0.5, 0.5)
	b.ZIndex = 40
	UI.corner(0.5, true).Parent = b
	UI.stroke(Color3.new(1, 1, 1), 4, 0, true).Parent = b
	local sc = Instance.new("UIScale")
	sc.Scale = 0.2
	sc.Parent = b
	UI.tween(sc, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
	b.Activated:Connect(onTap)
	b.Parent = UI.top
	handles[b] = at
	return b
end

local function dropHandle(b: TextButton?)
	if not b then
		return
	end
	handles[b] = nil
	local sc = b:FindFirstChildOfClass("UIScale")
	if sc then
		UI.tween(sc, 0.15, { Scale = 0 })
	end
	task.delay(0.16, function()
		b:Destroy()
	end)
end

---------------------------------------------------------------------
-- Кадр: камера, клапаны, ручки, радужная бумага
---------------------------------------------------------------------
RunService.RenderStepped:Connect(function(dt)
	if not alive then
		return
	end
	local t = os.clock()
	local u = smooth((t - camT0) / camDur)
	camera.CFrame = camFrom:Lerp(camTo, u) * CFrame.Angles(math.sin(t * 0.7) * 0.004, math.sin(t * 0.5) * 0.006, 0)
	local P = cur
	if P then
		for _, fl in P.flaps do
			if fl.u ~= fl.goal then
				local step = dt / FOLD_TIME
				fl.u = fl.goal > fl.u and math.min(fl.goal, fl.u + step) or math.max(fl.goal, fl.u - step)
				placeFlap(fl)
			end
		end
		if P.style.rainbow then
			for i, p in P.painted do
				p.Color = Theme.rainbow(t + i * 0.09, 0.55, 1)
			end
		end
	end
	local s = UI.scale()
	for b, at in handles do
		local px, on = UI.worldToScreen(at())
		b.Visible = on
		b.Position = UDim2.fromOffset(px.X / s, px.Y / s)
		b.Rotation = math.sin(t * 5) * 8
	end
end)

UserInputService.InputBegan:Connect(function(i, gp)
	if not alive then
		return
	end
	if i.KeyCode == Enum.KeyCode.Q and not gp then
		alive = false
		return
	end
	if gp then
		return
	end
	if i.KeyCode == Enum.KeyCode.Space then
		holdingInput = true
		table.insert(presses, Vector2.new(-1, -1)) -- Пробел
	elseif i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch then
		holdingInput = true
		table.insert(presses, Vector2.new(i.Position.X, i.Position.Y))
	end
end)
UserInputService.InputEnded:Connect(function(i)
	if i.KeyCode == Enum.KeyCode.Space or i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch then
		holdingInput = false
		holdingBtn = false
	end
end)

local function takePress(): Vector2?
	local p = table.remove(presses, 1)
	return p
end

---------------------------------------------------------------------
-- Этапы
---------------------------------------------------------------------
local function pickItem(): any?
	local items = pending()
	if #items == 0 then
		return nil
	end
	hint("Choose a catch to wrap")
	local chosen: any = nil
	local panel = UI.panel({ Color = C.panel, Size = UDim2.fromOffset(920, 280), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -14), Radius = 22, ZIndex = 30, Parent = UI.root })
	local sc = Instance.new("UIScale")
	sc.Scale = 0.6
	sc.Parent = panel
	UI.tween(sc, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
	UI.label({ Text = "Choose a catch 📦 Sale bonus ×" .. Config.WRAP_MULT, TextSize = 26, Size = UDim2.new(1, -24, 0, 34), Position = UDim2.fromOffset(12, 8), ZIndex = 32, Parent = panel })
	local sf = Instance.new("ScrollingFrame")
	sf.BackgroundTransparency = 1
	sf.BorderSizePixel = 0
	sf.Size = UDim2.new(1, -24, 1, -52)
	sf.Position = UDim2.fromOffset(12, 46)
	sf.ScrollingDirection = Enum.ScrollingDirection.X
	sf.AutomaticCanvasSize = Enum.AutomaticSize.X
	sf.CanvasSize = UDim2.new()
	sf.ScrollBarThickness = 8
	sf.ScrollBarImageColor3 = Color3.new(1, 1, 1)
	sf.ZIndex = 32
	sf.Parent = panel
	UI.list(Enum.FillDirection.Horizontal, 12, Enum.HorizontalAlignment.Left, Enum.VerticalAlignment.Top).Parent = sf
	for i, it in items do
		local holder = Instance.new("Frame")
		holder.BackgroundTransparency = 1
		holder.Size = UDim2.fromOffset(130, 214)
		holder.LayoutOrder = i
		holder.ZIndex = 33
		holder.Parent = sf
		local card = Card.new(it.sp, it, {
			size = Vector2.new(130, 174),
			showPrice = true,
			zIndex = 33,
			onClick = function()
				chosen = it
			end,
		})
		card.Parent = holder
		UI.label({ Text = "📦 " .. Num.short(it.price * Config.WRAP_MULT), TextSize = 22, Color = C.green, Size = UDim2.new(1, 0, 0, 30), Position = UDim2.fromOffset(0, 180), ZIndex = 34, Parent = holder })
	end
	while alive and not chosen do
		task.wait()
	end
	panel:Destroy()
	return chosen
end

local function spawnAnimal(P: Parcel, item: any)
	if not Fauna150.Has(item.sp) then
		return
	end
	local len = Fauna150.Attr(item.sp, "Len") or 3
	local hgt = Fauna150.Attr(item.sp, "Height") or 2
	local wid = Fauna150.Attr(item.sp, "Width") or 2
	local sc = math.min((A - 0.4) / math.max(len, wid, 0.5), (H - 0.12) / math.max(hgt, 0.5))
	local rest = S * CFrame.new(0, T, 0)
	local rig = AnimalRig.spawn(item.sp, rest * CFrame.new(0, 3, 0), P.model, item.mut, sc)
	if not rig then
		return
	end
	P.rig = rig
	rig:play("hop")
	-- падение на бумагу
	local t0 = os.clock()
	while alive and os.clock() - t0 < 0.35 do
		local u = (os.clock() - t0) / 0.35
		rig:setCF(rest * CFrame.new(0, 3 * (1 - u * u), 0))
		task.wait()
	end
	rig:setCF(rest)
	rig:play("happy")
	Sfx.play("pop", 1.1, 0.6)
	Fx.burst(rest.Position + Vector3.new(0, 0.1, 0), { tex = "smoke", color = Color3.fromRGB(240, 230, 210), n = 8, speed = NumberRange.new(1, 3), size = 0.5, life = 0.5 })
	task.delay(0.8, function()
		if P.rig == rig then
			rig:play("idle")
		end
	end)
end

local function foldPhase(P: Parcel): boolean
	local folded = 0
	local function fold(fl: Flap)
		if fl.goal == 1 or not alive then
			return
		end
		fl.goal = 1
		folded += 1
		dropHandle(fl.handle)
		fl.handle = nil
		Sfx.play("rustle", 0.85 + folded * 0.1, 0.8)
		Sfx.play("whoosh", 1.3, 0.25)
		task.delay(FOLD_TIME * 0.9, function()
			if alive then
				Fx.burst((S * CFrame.new(0, H, 0)).Position, { tex = "star", color = P.style.paper, n = 5, speed = NumberRange.new(2, 5), size = 0.35, life = 0.5, rot = true })
			end
		end)
		if folded == 2 and P.rig then
			P.rig:play("sleep")
		end
		hint(string.format("Fold the paper edges  %d/4", folded))
	end
	hint(UI.mobile and "Tap the paper edges  0/4" or "Click the paper edges (or Space)  0/4")
	for _, fl in P.flaps do
		fl.handle = makeHandle("👆", function()
			return flapSpot(fl)
		end, function()
			fold(fl)
		end)
	end
	local function nextFlap()
		for _, fl in P.flaps do
			if fl.goal == 0 then
				fold(fl)
				return
			end
		end
	end
	local btn = UI.button({ Text = "Fold edge", Icon = "📄", TextSize = 26, Color = C.orange, Size = UDim2.fromOffset(280, 76), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -28), ZIndex = 40, Parent = UI.root, Sound = "rustle" }, nextFlap)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	local parts = {}
	for _, fl in P.flaps do
		table.insert(parts, fl.a)
		table.insert(parts, fl.b)
	end
	params.FilterDescendantsInstances = parts
	table.clear(presses)
	while alive do
		local pr = takePress()
		while pr do
			if pr.X < 0 then
				nextFlap()
			else
				local ray = camera:ScreenPointToRay(pr.X, pr.Y)
				local hit = workspace:Raycast(ray.Origin, ray.Direction * 50, params)
				if hit then
					for _, fl in P.flaps do
						if hit.Instance == fl.a or hit.Instance == fl.b then
							fold(fl)
						end
					end
				end
			end
			pr = takePress()
		end
		local moving = false
		for _, fl in P.flaps do
			if fl.u < 1 then
				moving = true
			end
		end
		if folded >= 4 and not moving then
			break
		end
		task.wait()
	end
	btn:Destroy()
	for _, fl in P.flaps do
		dropHandle(fl.handle)
		fl.handle = nil
	end
	if not alive then
		return false
	end
	-- зверёк спит внутри: убираем модель
	if P.rig then
		P.rig:destroy()
		P.rig = nil
	end
	Sfx.play("pop", 0.8, 0.5)
	return true
end

local function ropePhase(P: Parcel): boolean
	hint(UI.mobile and "Hold the button to wind the rope" or "Hold the button, LMB or Space to wind the rope")
	local r = 0
	holdingBtn = false
	holdingInput = false
	local hb = UI.button({ Text = "Hold to wrap", Icon = "🧵", TextSize = 28, Color = C.orange, Size = UDim2.fromOffset(340, 92), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -28), ZIndex = 40, Parent = UI.root, Burst = false, Sound = "rustle" }, nil)
	local btn = hb:FindFirstChild("Btn") :: TextButton
	btn.InputBegan:Connect(function(i)
		if i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch then
			holdingBtn = true
		end
	end)
	btn.InputEnded:Connect(function(i)
		if i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch then
			holdingBtn = false
		end
	end)
	local bar = UI.bar({ Size = UDim2.fromOffset(340, 26), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -134), Color = C.orange, ZIndex = 40, Parent = UI.root })
	bar.set(0, "0 / 2 loops")
	local lastTick = 0
	local done = 0
	while alive and r < 1 do
		local dt = task.wait()
		if holdingBtn or holdingInput then
			r = math.min(1, r + dt / ROPE_TIME)
			if os.clock() - lastTick > 0.085 then
				lastTick = os.clock()
				Sfx.play("tick", 0.7 + r * 0.9, 0.22)
			end
		end
		local x = r * #SEGS
		for i = 1, #SEGS do
			placeSeg(P, i, math.clamp(x - (i - 1), 0, 1))
		end
		local nd = math.floor(x + 1e-6)
		if nd > done then
			done = nd
			if nd % 3 == 0 then
				Sfx.play("snap", 1 + nd * 0.03, 0.7)
				UI.punch(hb, 0.25)
				Fx.burst((S * CFrame.new(0, TY2 + 0.1, 0)).Position, { tex = "star", color = P.style.rope, n = 8, speed = NumberRange.new(2, 6), size = 0.4, life = 0.6, rot = true })
			end
		end
		bar.set(r, string.format("%d / 2 loops", math.floor(r * 2 + 1e-6)))
	end
	hb:Destroy()
	bar.frame:Destroy()
	return alive
end

local function bowPhase(P: Parcel): boolean
	hint("Tie the bow! 🎀")
	local tapped = false
	local btn = UI.button({ Text = "Tie bow!", Icon = "🎀", TextSize = 30, Color = C.pink, Size = UDim2.fromOffset(280, 92), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -28), ZIndex = 40, Parent = UI.root, Shine = true }, function()
		tapped = true
	end)
	local hdl = makeHandle("🎀", function()
		return (S * CFrame.new(0, BOW_Y + 0.4, 0)).Position
	end, function()
		tapped = true
	end)
	table.clear(presses)
	while alive and not tapped do
		if takePress() then
			tapped = true
		end
		task.wait()
	end
	btn:Destroy()
	dropHandle(hdl)
	if not alive then
		return false
	end
	Sfx.play("sparkle", 1, 0.7)
	Sfx.play("pop", 1.3, 0.6)
	local t0 = os.clock()
	while os.clock() - t0 < 0.35 do
		local u = (os.clock() - t0) / 0.35
		placeBow(P, backOut(u))
		task.wait()
	end
	placeBow(P, 1)
	Fx.burst((S * CFrame.new(0, BOW_Y + 0.3, 0)).Position, { tex = "sparkle", color = P.style.rope, color2 = C.gold, n = 18, speed = NumberRange.new(3, 8), size = 0.5, life = 0.8 })
	return true
end

-- Штамп «×2» поверх свёртка
local function stampAt(px: Vector2, text: string, color: Color3)
	local s = UI.scale()
	local l = UI.label({ Text = text, TextSize = 96, Color = color, Size = UDim2.fromOffset(260, 120), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(px.X / s, px.Y / s), Rotation = -14, ZIndex = 60, Parent = UI.top })
	local sc = Instance.new("UIScale")
	sc.Scale = 2.6
	sc.Parent = l
	UI.tween(sc, 0.18, { Scale = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
	task.delay(0.18, function()
		Sfx.play("stamp", 1, 0.9)
		UI.punch(l, 0.3)
		Fx.shake(0.12, 0.2)
	end)
	task.delay(1.6, function()
		UI.tween(l, 0.3, { TextTransparency = 1 })
		local st = l:FindFirstChildOfClass("UIStroke")
		if st then
			UI.tween(st, 0.3, { Transparency = 1 })
		end
	end)
	task.delay(2, function()
		l:Destroy()
	end)
end

local function finishParcel(P: Parcel, item: any, startedAt: number): boolean
	local left = Config.WRAP_MIN_TIME - (os.clock() - startedAt)
	if left > 0 then
		task.wait(left)
	end
	if not alive then
		return false
	end
	local ok, price = Backend.call("WrapFinish", item.id)
	if not ok then
		Sfx.play("error")
		UI.toast("Could not finish wrapping", "bad")
		return false
	end
	local center = (S * CFrame.new(0, H / 2, 0)).Position
	local px = UI.worldToScreen(center + Vector3.new(0, H, 0))
	stampAt(px, "×" .. Config.WRAP_MULT, C.green)
	-- цена: было → стало
	local s = UI.scale()
	local pl = UI.label({ Text = "", TextSize = 38, Color = C.gold, Size = UDim2.fromOffset(420, 50), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(px.X / s, px.Y / s + 90), ZIndex = 60, Parent = UI.top })
	local newPrice = tonumber(price) or item.price * Config.WRAP_MULT
	UI.countUp(pl, item.price, newPrice, 0.8, function(n: number)
		return "💰 " .. Num.short(item.price) .. " → " .. Num.short(math.floor(n))
	end, true)
	local sp = Config.SPECIES_BY_ID[item.sp]
	if (sp and sp.rarity >= 5) or item.mut then
		UI.confetti(50, { P.style.paper, P.style.rope, C.gold })
	end
	task.wait(1.1)
	pl:Destroy()
	-- свёрток подпрыгивает, крутится, уменьшается и улетает в сумку
	local pivot = S * CFrame.new(0, H / 2, 0)
	P.model.WorldPivot = pivot
	Sfx.play("whoosh", 1.2, 0.5)
	local t0 = os.clock()
	while os.clock() - t0 < 0.5 do
		local u = (os.clock() - t0) / 0.5
		P.model:ScaleTo(math.max(0.05, 1 - 0.6 * u))
		P.model:PivotTo(pivot * CFrame.new(0, 2.2 * math.sin(u * math.pi * 0.5), 0) * CFrame.Angles(0, u * math.pi * 2, 0))
		task.wait()
	end
	local from = UI.worldToScreen(P.model:GetPivot().Position)
	Fx.burst(P.model:GetPivot().Position, { tex = "sparkle", color = C.gold, n = 10, speed = NumberRange.new(2, 6), size = 0.4, life = 0.6 })
	destroyParcel(P)
	if cur == P then
		cur = nil
	end
	Hud.fly("📦", from, Hud.bagPos(), 1, function()
		Sfx.play("pop", 1.2, 0.6)
	end)
	return true
end

---------------------------------------------------------------------
-- Вход / выход
---------------------------------------------------------------------
function WrapCtl.open(plot: Instance)
	if WrapCtl.active or Activities.busy then
		return
	end
	local wt = plot:FindFirstChild("WrapTable")
	local top = wt and wt:FindFirstChild("Top") :: BasePart?
	local stand = wt and wt:FindFirstChild("Stand") :: BasePart?
	local root, h = hrp(), hum()
	if not top or not root or not h or h.Health <= 0 then
		return
	end
	if #pending() == 0 then
		Sfx.play("error")
		UI.toast("Nothing to wrap — catch an animal first 🗡️", "warn")
		return
	end
	WrapCtl.active = true
	Activities.busy = "wrap"
	alive = true
	Hud.setMode("busy")
	-- поверхность стола, −Z смотрит на игрока
	local surf = top.CFrame * CFrame.new(0, top.Size.Y / 2, 0)
	local standPos = stand and stand.Position or (surf.Position + top.CFrame.LookVector * 4)
	local dir = Vector3.new(standPos.X - surf.X, 0, standPos.Z - surf.Z)
	dir = dir.Magnitude > 0.1 and dir.Unit or top.CFrame.LookVector
	S = CFrame.lookAt(surf.Position, surf.Position + dir)
	local y = standPos.Y + (stand and stand.Size.Y / 2 or 0) + h.HipHeight + root.Size.Y / 2
	local unlock = Activities.lockAt(CFrame.lookAt(Vector3.new(standPos.X, y, standPos.Z), Vector3.new(surf.X, y, surf.Z)))
	Animator.play("Wrap")
	local savedFov = camera.FieldOfView
	camera.CameraType = Enum.CameraType.Scriptable
	camera.FieldOfView = 62
	local eye = (S * CFrame.new(0, 5.4, -2.9)).Position
	camFly(CFrame.lookAt(eye, (S * CFrame.new(0, 0.3, -0.2)).Position), 0.7)
	Sfx.play("open")
	local bar, v = Activities.bar("📦 WRAPPING · sale bonus ×" .. Config.WRAP_MULT, C.orange, function()
		alive = false
	end)
	val = v
	local diedConn = h.Died:Connect(function()
		alive = false
	end)
	local wrapped = 0
	while alive do
		local item = pickItem()
		if not item or not alive then
			break
		end
		local ok, err = Backend.call("WrapStart", item.id)
		if not ok then
			Sfx.play("error")
			UI.toast(tostring(err or "Cannot wrap this catch"), "warn")
			continue
		end
		local started = os.clock()
		local P = newParcel(item)
		cur = P
		spawnAnimal(P, item)
		if not (alive and foldPhase(P) and ropePhase(P) and bowPhase(P) and finishParcel(P, item, started)) then
			break
		end
		wrapped += 1
		-- Пасс Master Wrapper: один бантик заворачивает всю сумку
		if Perks.has("wrap") then
			local okAll, more = Backend.call("WrapAll")
			if okAll and (tonumber(more) or 0) > 0 then
				UI.toast("Master Wrapper: " .. tostring(more) .. " more wrapped", "good", 3)
			end
		end
		if #pending() == 0 then
			hint("Everything is wrapped!")
			Hud.banner("ALL WRAPPED! 📦", C.green, "Parcels sell for ×" .. Config.WRAP_MULT .. " at the market", 2.2)
			task.wait(1.4)
			break
		end
	end
	-- выход
	alive = false
	diedConn:Disconnect()
	destroyParcel(cur)
	cur = nil
	for b in handles do
		b:Destroy()
	end
	table.clear(handles)
	table.clear(presses)
	bar:Destroy()
	val = nil
	unlock()
	Animator.stop()
	camera.CameraType = Enum.CameraType.Custom
	camera.FieldOfView = savedFov
	Hud.setMode("normal")
	Activities.busy = nil
	WrapCtl.active = false
	if wrapped > 0 then
		UI.toast("Wrapped: " .. wrapped .. " 📦", "good")
	end
end

return WrapCtl
