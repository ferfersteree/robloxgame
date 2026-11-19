-- StarterPlayerScripts/Client/WorldFx.luau
-- Эффекты в мире: всплески частиц, кольца-ударные волны, вспышки света, столбы света, молнии,
-- тряска камеры, всплывающий текст. Только встроенные текстуры движка.
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local Theme = require(script.Parent.Theme)

local Fx = {}
Fx.lowFx = false

local folder = Instance.new("Folder")
folder.Name = "ClientFx"
folder.Parent = workspace
Fx.folder = folder

local camera = workspace.CurrentCamera

local TEX = {
	sparkle = "rbxasset://textures/particles/sparkles_main.dds",
	smoke = "rbxasset://textures/particles/smoke_main.dds",
	fire = "rbxasset://textures/particles/fire_main.dds",
	sparks = "rbxasset://textures/particles/fire_sparks_main.dds",
	square = "rbxasset://textures/particles/SquareParticle.png",
	glow = "rbxasset://textures/glow.png",
	star = "rbxasset://textures/sparkle.png",
	circle = "rbxasset://textures/whiteCircle.png",
	triangle = "rbxasset://textures/triangle.png",
}
Fx.TEX = TEX

local function tween(i: Instance, t: number, p: { [string]: any }, style: Enum.EasingStyle?, dir: Enum.EasingDirection?): Tween
	local tw = TweenService:Create(i, TweenInfo.new(t, style or Enum.EasingStyle.Quad, dir or Enum.EasingDirection.Out), p)
	tw:Play()
	return tw
end
Fx.tween = tween

function Fx.anchor(pos: Vector3, life: number?): (Part, Attachment)
	local p = Instance.new("Part")
	p.Name = "FxAnchor"
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Transparency = 1
	p.Size = Vector3.new(0.2, 0.2, 0.2)
	p.CFrame = CFrame.new(pos)
	local a = Instance.new("Attachment")
	a.Parent = p
	p.Parent = folder
	if life then
		Debris:AddItem(p, life)
	end
	return p, a
end

export type BurstOpts = {
	tex: string?,
	color: Color3?,
	color2: Color3?,
	n: number?,
	speed: NumberRange?,
	size: number?,
	size2: number?,
	life: number?,
	spread: number?,
	accel: Vector3?,
	light: number?,
	drag: number?,
	rot: boolean?,
	dir: Vector3?,
	transp: number?,
}

-- Разовый всплеск частиц
function Fx.burst(pos: Vector3, o: BurstOpts)
	local life = o.life or 0.9
	local _, a = Fx.anchor(pos, life + 0.6)
	local e = Instance.new("ParticleEmitter")
	e.Texture = TEX[o.tex or "sparkle"] or o.tex or TEX.sparkle
	local c1 = o.color or Color3.new(1, 1, 1)
	e.Color = ColorSequence.new(c1, o.color2 or c1)
	local s = o.size or 0.8
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, s), NumberSequenceKeypoint.new(1, o.size2 or s * 0.2) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, o.transp or 0), NumberSequenceKeypoint.new(0.7, (o.transp or 0) * 0.5 + 0.2), NumberSequenceKeypoint.new(1, 1) })
	e.Lifetime = NumberRange.new(life * 0.6, life)
	e.Speed = o.speed or NumberRange.new(8, 18)
	e.SpreadAngle = Vector2.new(o.spread or 180, o.spread or 180)
	e.Acceleration = o.accel or Vector3.new(0, -12, 0)
	e.Drag = o.drag or 2
	e.LightEmission = o.light or 0.6
	e.LightInfluence = 0
	e.Rate = 0
	e.RotSpeed = o.rot and NumberRange.new(-260, 260) or NumberRange.new(0, 0)
	e.Rotation = o.rot and NumberRange.new(0, 360) or NumberRange.new(0, 0)
	if o.dir then
		a.WorldCFrame = CFrame.lookAt(pos, pos + o.dir) * CFrame.Angles(-math.pi / 2, 0, 0)
	end
	e.Parent = a
	local n = o.n or 20
	if Fx.lowFx then
		n = math.ceil(n * 0.4)
	end
	e:Emit(n)
end

-- Готовые наборы удара копья
local IMPACTS: { [string]: (Vector3, Color3, Color3, number) -> () } = {
	dust = function(p, _c1, _c2, k)
		Fx.burst(p, { tex = "smoke", color = Color3.fromRGB(196, 170, 130), n = 14 * k, speed = NumberRange.new(4, 10), size = 2.2, size2 = 4, life = 1.2, accel = Vector3.new(0, 2, 0), light = 0, transp = 0.3 })
	end,
	sparks = function(p, c1, c2, k)
		Fx.burst(p, { tex = "sparks", color = c1, color2 = c2, n = 24 * k, speed = NumberRange.new(14, 30), size = 0.6, life = 0.7, accel = Vector3.new(0, -40, 0), light = 1 })
	end,
	feathers = function(p, c1, c2, k)
		Fx.burst(p, { tex = "square", color = c1, color2 = c2, n = 16 * k, speed = NumberRange.new(6, 14), size = 0.5, size2 = 0.4, life = 2.2, accel = Vector3.new(0, -3, 0), drag = 3, rot = true, light = 0 })
	end,
	shards = function(p, c1, c2, k)
		Fx.burst(p, { tex = "triangle", color = c1, color2 = c2, n = 18 * k, speed = NumberRange.new(12, 24), size = 0.7, life = 1, accel = Vector3.new(0, -50, 0), rot = true, light = 0.5 })
	end,
	crystal = function(p, c1, c2, k)
		Fx.burst(p, { tex = "star", color = c1, color2 = c2, n = 22 * k, speed = NumberRange.new(8, 20), size = 1.2, life = 1.2, accel = Vector3.new(0, 4, 0), rot = true, light = 1 })
	end,
	fire = function(p, c1, c2, k)
		Fx.burst(p, { tex = "fire", color = c1, color2 = c2, n = 20 * k, speed = NumberRange.new(4, 12), size = 2.5, size2 = 0.5, life = 1.1, accel = Vector3.new(0, 14, 0), light = 1 })
		Fx.burst(p, { tex = "sparks", color = c1, n = 18 * k, speed = NumberRange.new(14, 28), size = 0.5, life = 0.8, accel = Vector3.new(0, -30, 0), light = 1 })
	end,
	ice = function(p, c1, c2, k)
		Fx.burst(p, { tex = "square", color = c1, color2 = c2, n = 20 * k, speed = NumberRange.new(10, 22), size = 0.5, life = 1.1, accel = Vector3.new(0, -40, 0), rot = true, light = 0.4 })
		Fx.burst(p, { tex = "smoke", color = Color3.fromRGB(220, 240, 255), n = 8 * k, speed = NumberRange.new(2, 6), size = 3, size2 = 5, life = 1.6, accel = Vector3.new(0, 1, 0), light = 0.2, transp = 0.4 })
	end,
	stars = function(p, c1, c2, k)
		Fx.burst(p, { tex = "star", color = c1, color2 = c2, n = 30 * k, speed = NumberRange.new(10, 26), size = 1.4, life = 1.4, accel = Vector3.new(0, -6, 0), rot = true, light = 1 })
	end,
}
function Fx.impact(kind: string, pos: Vector3, c1: Color3, c2: Color3, k: number?)
	local f = IMPACTS[kind] or IMPACTS.dust
	f(pos, c1, c2, math.max(1, k or 1))
	if kind ~= "dust" then
		IMPACTS.dust(pos, c1, c2, 0.6)
	end
end

-- V67: кольцо на земле — полая светящаяся окружность, а не залитый диск. Одна неподвижная деталь, сверху SurfaceGui:
-- круг (UICorner) с двумя обводками UIStroke: тонкая яркая линия и широкий мягкий ореол того же цвета.
-- Проверено в Studio: (1) на полностью прозрачной детали (Transparency = 1) SurfaceGui не рисуется, поэтому 0.99;
-- (2) если размер детали меняется каждый кадр, SurfaceGui не успевает перерисоваться и кольца не видно,
-- поэтому деталь сразу полного размера, а растёт содержимое: общий контейнер с UIScale.
-- (3) SurfaceGui видна только с одной стороны: у кольца в воздухе (вершина полёта копья, выпуск в прыжке) камера
-- снизу, поэтому там рисунок дублируется на нижнюю грань (bothSides).
-- Возвращает деталь, списки обводок (ядра, ореолы), контейнеров и их UIScale (по одному на сторону), поле (margin,
-- стады) и плотность (пикселей на стад).
local WHITE = Color3.new(1, 1, 1)
local function ringGui(pos: Vector3, color: Color3, radius: number, core: number, halo: number, bothSides: boolean?): (Part, { UIStroke }, { UIStroke }, { Frame }, { UIScale }, number, number)
	-- радиус не меньше половины ореола плюс линия (иначе у кружков отрицательный размер) и не больше 60 стадов
	radius = math.clamp(radius, halo * 0.5 + core + 0.2, 60)
	local margin = halo + 0.15
	local size = 2 * (radius + margin)
	local pps = math.clamp(math.floor(420 / size), 6, 40)
	local p = Instance.new("Part")
	p.Name = "FxRing"
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Material = Enum.Material.SmoothPlastic
	p.Transparency = 0.99
	p.Size = Vector3.new(size, 0.05, size)
	p.CFrame = CFrame.new(pos)
	local cores, halos, holders, scales = {}, {}, {}, {}
	local function circle(holder: Frame, th: number, transp: number, col: Color3): UIStroke
		local inset = margin + th / 2
		local f = Instance.new("Frame")
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.Position = UDim2.fromScale(0.5, 0.5)
		f.Size = UDim2.new(1, -2 * inset * pps, 1, -2 * inset * pps)
		f.BackgroundTransparency = 1
		f.BorderSizePixel = 0
		local c = Instance.new("UICorner")
		c.CornerRadius = UDim.new(0.5, 0)
		c.Parent = f
		local s = Instance.new("UIStroke")
		s.Color = col
		s.Thickness = th * pps
		s.Transparency = transp
		s.Parent = f
		f.Parent = holder
		return s
	end
	for _, face in (if bothSides then { Enum.NormalId.Top, Enum.NormalId.Bottom } else { Enum.NormalId.Top }) do
		local g = Instance.new("SurfaceGui")
		g.Face = face
		g.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		g.PixelsPerStud = pps
		g.LightInfluence = 0
		g.Brightness = 2
		g.Parent = p
		local holder = Instance.new("Frame")
		holder.Name = "Holder"
		holder.AnchorPoint = Vector2.new(0.5, 0.5)
		holder.Position = UDim2.fromScale(0.5, 0.5)
		holder.Size = UDim2.fromScale(1, 1)
		holder.BackgroundTransparency = 1
		holder.BorderSizePixel = 0
		local sc = Instance.new("UIScale")
		sc.Parent = holder
		holder.Parent = g
		table.insert(halos, circle(holder, halo, 0.7, color))
		table.insert(cores, circle(holder, core, 0.05, color:Lerp(WHITE, 0.4)))
		table.insert(holders, holder)
		table.insert(scales, sc)
	end
	return p, cores, halos, holders, scales, margin, pps
end
Fx.ringGui = ringGui

-- Есть ли земля (не эффекты и не персонажи) в паре стадов под точкой
local groundParams = RaycastParams.new()
groundParams.FilterType = Enum.RaycastFilterType.Exclude
local function nearGround(pos: Vector3): boolean
	local skip: { Instance } = { folder }
	for _, pl in game:GetService("Players"):GetPlayers() do
		if pl.Character then
			table.insert(skip, pl.Character)
		end
	end
	groundParams.FilterDescendantsInstances = skip
	return workspace:Raycast(pos + Vector3.new(0, 0.5, 0), Vector3.new(0, -2.5, 0), groundParams) ~= nil
end

-- Кольцо-волна по земле: расходится от центра, линия к концу тоньше, сначала яркая, потом гаснет
function Fx.ring(pos: Vector3, color: Color3, radius: number, dur: number?, thick: number?)
	local d = dur or 0.6
	local core = thick or math.clamp(radius * 0.05, 0.14, 0.8)
	local halo = core * 3.2
	local p, cores, halos, _, scales = ringGui(pos, color, radius, core, halo, not nearGround(pos))
	for i, sc in scales do
		local sCore, sHalo = cores[i], halos[i]
		-- UIScale уменьшает и обводки, поэтому в начале линия толще, чтобы маленькое кольцо читалось
		sc.Scale = 0.12
		sCore.Thickness *= 2.4
		sHalo.Thickness *= 1.6
		tween(sc, d, { Scale = 1 }, Enum.EasingStyle.Quart)
		tween(sCore, d, { Transparency = 1, Thickness = sCore.Thickness * 0.3 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		tween(sHalo, d * 0.85, { Transparency = 1, Thickness = sHalo.Thickness * 0.5 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
	end
	p.Parent = folder
	Debris:AddItem(p, d + 0.1)
end

-- V67: знак под пойманным зверем: светящееся кольцо с бледной заливкой и искрами, которые поднимаются с круга.
-- Появляется с отскоком, мерцает, пока на детали нет атрибута Fading, а с ним за 0.35 с гаснет.
-- Деталь почти прозрачна (0.99), поэтому прежний код Reveal (Fading, Transparency → 1, Destroy) работает как раньше.
function Fx.glyph(pos: Vector3, color: Color3, radius: number): Part
	local core = math.clamp(radius * 0.07, 0.12, 0.55)
	local halo = core * 3.6
	local p, cores, halos, holders, scales, margin, pps = ringGui(pos, color, radius, core, halo)
	local sCore, sHalo, holder, sc = cores[1], halos[1], holders[1], scales[1]
	p.Name = "RevealGlyph"
	-- бледная заливка круга
	local fill = Instance.new("Frame")
	fill.AnchorPoint = Vector2.new(0.5, 0.5)
	fill.Position = UDim2.fromScale(0.5, 0.5)
	fill.Size = UDim2.new(1, -2 * (margin + core) * pps, 1, -2 * (margin + core) * pps)
	fill.BackgroundColor3 = color
	fill.BackgroundTransparency = 1
	fill.BorderSizePixel = 0
	local fc = Instance.new("UICorner")
	fc.CornerRadius = UDim.new(0.5, 0)
	fc.Parent = fill
	fill.ZIndex = 0
	fill.Parent = holder
	sCore.Transparency = 1
	sHalo.Transparency = 1
	sc.Scale = 0.2
	p.Parent = folder
	tween(sc, 0.5, { Scale = 1 }, Enum.EasingStyle.Back)
	tween(sCore, 0.35, { Transparency = 0.05 })
	tween(sHalo, 0.5, { Transparency = 0.72 })
	tween(fill, 0.5, { BackgroundTransparency = 0.82 })
	-- искры, поднимающиеся с круга (в «Reduced Effects» реже)
	local e = Instance.new("ParticleEmitter")
	e.Texture = TEX.sparkle
	e.Color = ColorSequence.new(WHITE, color)
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, math.clamp(radius * 0.12, 0.25, 0.9)), NumberSequenceKeypoint.new(1, 0) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.1), NumberSequenceKeypoint.new(1, 1) })
	e.Lifetime = NumberRange.new(0.9, 1.6)
	e.Speed = NumberRange.new(1.5, 3.5)
	e.SpreadAngle = Vector2.new(10, 10)
	e.EmissionDirection = Enum.NormalId.Top
	e.Shape = Enum.ParticleEmitterShape.Disc
	e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface
	e.Acceleration = Vector3.new(0, 1.5, 0)
	e.LightEmission = 1
	e.LightInfluence = 0
	e.Rate = math.clamp(radius * 6, 6, 30) * (if Fx.lowFx then 0.35 else 1)
	e.Parent = p
	task.spawn(function()
		local t0 = os.clock()
		while p.Parent and not p:GetAttribute("Fading") do
			local t = os.clock() - t0
			if t > 0.55 then
				sHalo.Transparency = 0.72 + 0.1 * math.sin(t * 4)
				fill.BackgroundTransparency = 0.82 + 0.05 * math.sin(t * 4 + 1)
			end
			RunService.RenderStepped:Wait()
		end
		e.Enabled = false
		if p.Parent then
			tween(sCore, 0.35, { Transparency = 1 })
			tween(sHalo, 0.35, { Transparency = 1 })
			tween(fill, 0.35, { BackgroundTransparency = 1 })
		end
	end)
	return p
end

-- V64: кольцо ударной волны поперёк направления (звуковой хлопок при броске)
function Fx.shockRing(pos: Vector3, dir: Vector3, color: Color3, radius: number, dur: number?)
	local d = if dir.Magnitude > 1e-3 then dir.Unit else Vector3.new(0, 0, -1)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Cylinder
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Material = Enum.Material.Neon
	p.Color = color
	p.Transparency = 0.3
	p.Size = Vector3.new(0.2, 1, 1)
	-- ось цилиндра (локальная X) ставится вдоль направления
	p.CFrame = CFrame.lookAt(pos, pos + d) * CFrame.Angles(0, math.rad(90), 0)
	p.Parent = folder
	local t = dur or 0.35
	tween(p, t, { Size = Vector3.new(0.04, radius * 2, radius * 2), Transparency = 1 })
	Debris:AddItem(p, t + 0.1)
end

-- V64: светящийся росчерк между двумя точками (след рывка)
function Fx.streak(a: Vector3, b: Vector3, color: Color3, width: number?, dur: number?)
	local len = (b - a).Magnitude
	if len < 0.05 then
		return
	end
	local w = width or 0.3
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Material = Enum.Material.Neon
	p.Color = color
	p.Transparency = 0.2
	p.Size = Vector3.new(w, w, len)
	p.CFrame = CFrame.lookAt((a + b) / 2, b)
	p.Parent = folder
	local t = dur or 0.25
	tween(p, t, { Size = Vector3.new(0.02, 0.02, len), Transparency = 1 })
	Debris:AddItem(p, t + 0.1)
end

-- Сфера-вспышка. V67: вместо плотного неонового шара мягкая вспышка: билборд из трёх кругов (белое ядро,
-- цветная середина, бледный ореол), который раздувается и гаснет, и под ним едва заметный шар
function Fx.sphere(pos: Vector3, color: Color3, r: number, dur: number?)
	local d = dur or 0.4
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Material = Enum.Material.Neon
	p.Color = color
	p.Transparency = 0.72
	p.Size = Vector3.one * 0.5
	p.CFrame = CFrame.new(pos)
	p.CastShadow = false
	p.Parent = folder
	tween(p, d, { Size = Vector3.one * r * 1.6, Transparency = 1 })
	Debris:AddItem(p, d + 0.15)
	local bb = Instance.new("BillboardGui")
	bb.Size = UDim2.fromScale(r * 0.6, r * 0.6)
	bb.LightInfluence = 0
	bb.Brightness = 3
	bb.Adornee = p
	bb.Parent = p
	local layers = {
		{ s = 1, t = 0.8, c = color },
		{ s = 0.62, t = 0.5, c = color:Lerp(WHITE, 0.35) },
		{ s = 0.3, t = 0.05, c = WHITE },
	}
	for i, L in layers do
		local f = Instance.new("Frame")
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.Position = UDim2.fromScale(0.5, 0.5)
		f.Size = UDim2.fromScale(L.s, L.s)
		f.BackgroundColor3 = L.c
		f.BackgroundTransparency = L.t
		f.BorderSizePixel = 0
		f.ZIndex = i
		local c = Instance.new("UICorner")
		c.CornerRadius = UDim.new(0.5, 0)
		c.Parent = f
		f.Parent = bb
		tween(f, d, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
	end
	tween(bb, d, { Size = UDim2.fromScale(r * 2.6, r * 2.6) }, Enum.EasingStyle.Quart)
end

function Fx.light(pos: Vector3, color: Color3, range: number, brightness: number, dur: number?): PointLight
	local part = Fx.anchor(pos, (dur or 0.5) + 0.2)
	local l = Instance.new("PointLight")
	l.Color = color
	l.Range = range
	l.Brightness = brightness
	l.Shadows = false
	l.Parent = part
	tween(l, dur or 0.5, { Brightness = 0 })
	return l
end

-- Столб света из неба (редкие раскрытия). V67: вместо сплошного неонового цилиндра луч из трёх полупрозрачных
-- лент (Beam, всегда лицом к камере): белое ядро, цветная середина и широкий бледный ореол. Луч вырастает из земли
-- вверх, к верху растворяется, слегка пульсирует, а внутри поднимаются искры; у основания кольцо и свет.
-- Возвращает невидимую деталь-основание (как и раньше, Part); если её удалить, луч и искры гаснут сразу
-- (кольцо и свет у основания догорают сами).
function Fx.pillar(pos: Vector3, color: Color3, height: number, dur: number, width: number?): Part
	local w = width or 3
	height = height or 120
	dur = math.max(dur or 3, 0.2)
	local base = Instance.new("Part")
	base.Name = "FxPillar"
	base.Anchored = true
	base.CanCollide = false
	base.CanQuery = false
	base.CanTouch = false
	base.CastShadow = false
	base.Transparency = 1
	base.Size = Vector3.new(0.2, 0.2, 0.2)
	base.CFrame = CFrame.new(pos)
	local a0 = Instance.new("Attachment")
	a0.Parent = base
	local a1 = Instance.new("Attachment")
	a1.Position = Vector3.new(0, 0.2, 0)
	a1.Parent = base
	local hot = color:Lerp(WHITE, 0.6)
	local layers = {
		{ w = w * 0.32, t = 0, c0 = WHITE, c1 = hot },
		{ w = w * 0.95, t = 0.45, c0 = hot, c1 = color },
		{ w = w * 2.6, t = 0.87, c0 = color, c1 = color },
	}
	local beams = {}
	for _, L in layers do
		local b = Instance.new("Beam")
		b.Attachment0 = a0
		b.Attachment1 = a1
		b.FaceCamera = true
		b.LightEmission = 1
		b.LightInfluence = 0
		b.Segments = 1
		b.Color = ColorSequence.new(L.c0, L.c1)
		b.Width0 = 0
		b.Width1 = 0
		b.Parent = base
		table.insert(beams, { b = b, L = L })
	end
	local spark: ParticleEmitter? = nil
	if not Fx.lowFx then
		local e = Instance.new("ParticleEmitter")
		e.Texture = TEX.sparkle
		e.Color = ColorSequence.new(WHITE, color)
		e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.35 + w * 0.08), NumberSequenceKeypoint.new(1, 0) })
		e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.8, 0.3), NumberSequenceKeypoint.new(1, 1) })
		e.Lifetime = NumberRange.new(1.4, 2.6)
		e.Speed = NumberRange.new(12, 28)
		e.SpreadAngle = Vector2.new(7, 7)
		e.Drag = 0.35
		e.LightEmission = 1
		e.LightInfluence = 0
		e.Rate = 22
		e.Parent = a0
		spark = e
	end
	base.Parent = folder
	Fx.ring(pos + Vector3.new(0, 0.15, 0), color, w * 2.2, 0.7)
	Fx.light(pos + Vector3.new(0, 3, 0), color, 26 + w * 3, 6, dur)
	-- угасание: последние 0.55 с, но у короткого луча не раньше его середины
	local grow, fadeAt = 0.35, math.max(dur * 0.5, dur - 0.55)
	local t0 = os.clock()
	local conn: RBXScriptConnection? = nil
	conn = RunService.RenderStepped:Connect(function()
		local t = os.clock() - t0
		if not base.Parent or t >= dur then
			-- луч погас; основание с искрами ещё живёт, пока последние искры не долетят (Debris ниже)
			if conn then
				conn:Disconnect()
			end
			for _, it in beams do
				it.b.Enabled = false
			end
			if spark then
				spark.Enabled = false
			end
			return
		end
		local up = math.clamp(t / grow, 0, 1)
		up = 1 - (1 - up) ^ 3
		local fade = math.clamp((t - fadeAt) / (dur - fadeAt), 0, 1)
		a1.Position = Vector3.new(0, math.max(0.2, height * up), 0)
		-- ширина: раскрытие с небольшим перехлёстом, лёгкая пульсация, к концу луч сужается
		local open = math.clamp(t / 0.28, 0, 1)
		local k = (open * (1 + 0.25 * math.sin(open * math.pi))) * (1 + 0.07 * math.sin(t * 9)) * (1 - 0.85 * fade)
		for _, it in beams do
			local L = it.L
			it.b.Width0 = L.w * k
			it.b.Width1 = L.w * k * 1.25
			local tb = L.t + (1 - L.t) * fade
			it.b.Transparency = NumberSequence.new({
				NumberSequenceKeypoint.new(0, tb),
				NumberSequenceKeypoint.new(0.55, math.min(1, tb * 0.5 + 0.38 + 0.6 * fade)),
				NumberSequenceKeypoint.new(1, 1),
			})
		end
		if spark and fade > 0 then
			spark.Enabled = false
		end
	end)
	Debris:AddItem(base, dur + 3)
	return base
end

-- Ломаная молния между точками
function Fx.lightning(a: Vector3, b: Vector3, color: Color3?, segs: number?, width: number?)
	local n = segs or 9
	local prev = a
	local dir = b - a
	local side = dir:Cross(Vector3.yAxis)
	if side.Magnitude < 1e-3 then
		side = Vector3.xAxis
	end
	side = side.Unit
	local fwd = dir.Unit:Cross(side)
	for i = 1, n do
		local k = i / n
		local p = a + dir * k
		if i < n then
			local j = dir.Magnitude * 0.06
			p += side * (math.random() * 2 - 1) * j + fwd * (math.random() * 2 - 1) * j
		end
		local seg = Instance.new("Part")
		seg.Anchored = true
		seg.CanCollide = false
		seg.CanQuery = false
		seg.CanTouch = false
		seg.Material = Enum.Material.Neon
		seg.Color = color or Color3.fromRGB(200, 230, 255)
		seg.CastShadow = false
		local len = (p - prev).Magnitude
		seg.Size = Vector3.new(width or 0.35, width or 0.35, len)
		seg.CFrame = CFrame.lookAt((p + prev) / 2, p)
		seg.Parent = folder
		tween(seg, 0.35, { Transparency = 1 })
		Debris:AddItem(seg, 0.4)
		prev = p
	end
end

-- Тряска камеры (после скриптов камеры)
local shakeAmp, shakeEnd, shakeDur = 0, 0, 1
RunService:BindToRenderStep("SpearShake", Enum.RenderPriority.Camera.Value + 2, function()
	local now = os.clock()
	if now < shakeEnd and shakeAmp > 0 then
		local k = (shakeEnd - now) / shakeDur
		local a = shakeAmp * k
		local t = now * 40
		camera.CFrame *= CFrame.new(math.noise(t, 0) * a, math.noise(0, t) * a, 0) * CFrame.Angles(0, 0, math.noise(t, t) * a * 0.03)
	end
end)
function Fx.shake(amp: number, dur: number?)
	if amp <= 0 then
		return
	end
	local now = os.clock()
	if now < shakeEnd and shakeAmp > amp then
		return
	end
	shakeAmp = amp
	shakeDur = dur or 0.5
	shakeEnd = now + shakeDur
end

-- Всплывающий текст в мире
function Fx.text(pos: Vector3, text: string, color: Color3?, size: number?, dur: number?)
	local part = Fx.anchor(pos, (dur or 1.4) + 0.2)
	local bb = Instance.new("BillboardGui")
	bb.Size = UDim2.fromOffset(300, 80)
	bb.AlwaysOnTop = true
	bb.LightInfluence = 0
	bb.MaxDistance = 400
	bb.Parent = part
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Font = Theme.FONT
	l.Text = text
	l.TextColor3 = color or Color3.new(1, 1, 1)
	l.TextSize = size or 40
	local s = Instance.new("UIStroke")
	s.Thickness = 3
	s.Parent = l
	l.Parent = bb
	local d = dur or 1.4
	tween(bb, d, { StudsOffsetWorldSpace = Vector3.new(0, 4, 0) })
	task.delay(d * 0.6, function()
		tween(l, d * 0.4, { TextTransparency = 1 })
		tween(s, d * 0.4, { Transparency = 1 })
	end)
end

-- Временный эмиттер на вложении (след копья, шлейф)
function Fx.emitter(att: Attachment, o: BurstOpts & { rate: number? }): ParticleEmitter
	local e = Instance.new("ParticleEmitter")
	e.Texture = TEX[o.tex or "sparkle"] or o.tex or TEX.sparkle
	local c1 = o.color or Color3.new(1, 1, 1)
	e.Color = ColorSequence.new(c1, o.color2 or c1)
	local s = o.size or 0.6
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, s), NumberSequenceKeypoint.new(1, o.size2 or 0) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, o.transp or 0), NumberSequenceKeypoint.new(1, 1) })
	e.Lifetime = NumberRange.new((o.life or 0.6) * 0.6, o.life or 0.6)
	e.Speed = o.speed or NumberRange.new(0.5, 2)
	e.SpreadAngle = Vector2.new(o.spread or 180, o.spread or 180)
	e.Acceleration = o.accel or Vector3.zero
	e.Drag = o.drag or 1
	e.LightEmission = o.light or 1
	e.LightInfluence = 0
	e.Rate = (o.rate or 30) * (Fx.lowFx and 0.4 or 1)
	e.RotSpeed = o.rot and NumberRange.new(-200, 200) or NumberRange.new(0, 0)
	e.Parent = att
	return e
end

---------------------------------------------------------------------
-- V66: волна по земле, как по кубикам Minecraft. От точки удара во все стороны по очереди поднимаются кубы цвета
-- земли под ними, чуть кренятся и опускаются обратно: небольшое землетрясение. В покое куб спрятан под землёй
-- (верх на 0.05 ниже поверхности), поэтому видно только сам подъём. Кубы стоят только на земле (Terrain или детали
-- с именами земли), не на деревьях и крышах. Всё лежит только у этого клиента и убирается само после волны.
-- center: точка удара на земле; radius: радиус волны (стады); height: наибольший подъём куба (стады).
---------------------------------------------------------------------
local GROUND_NAMES = { Ground = true, FarGround = true, Field = true, Floor = true, Path = true, Terrain = true }
local WAVE_SPEED = 24 -- стадов в секунду
local WAVE_BUMP = 0.42 -- сколько длится подъём и опускание одного куба, секунд

function Fx.groundWave(center: Vector3, radius: number, height: number)
	local low = Fx.lowFx == true
	local R = math.clamp(radius * (if low then 0.7 else 1), 2, 16)
	local cell = math.max(1.3, R / (if low then 4.5 else 6.5))
	local n = math.floor(R / cell)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	local ignore: { Instance } = { folder }
	local lp = game:GetService("Players").LocalPlayer
	if lp and lp.Character then
		table.insert(ignore, lp.Character)
	end
	params.FilterDescendantsInstances = ignore
	local terrain = workspace.Terrain
	local rng = Random.new()
	local cubes: { { part: BasePart, rest: CFrame, t0: number, amp: number, tilt: Vector3 } } = {}
	local parts: { BasePart } = {}
	local chipColor: Color3? = nil
	for ix = -n, n do
		for iz = -n, n do
			local off = Vector3.new(ix * cell, 0, iz * cell)
			local d = off.Magnitude
			if d <= R + 0.01 then
				local hit = workspace:Raycast(center + off + Vector3.new(0, 6, 0), Vector3.new(0, -14, 0), params)
				local inst = hit and hit.Instance
				if hit and inst and (inst == terrain or GROUND_NAMES[inst.Name]) and math.abs(hit.Position.Y - center.Y) < 4 then
					local color: Color3
					local mat = hit.Material
					if inst == terrain then
						local okColor, c = pcall(function()
							return terrain:GetMaterialColor(mat)
						end)
						color = if okColor and typeof(c) == "Color3" then c else Color3.fromRGB(110, 160, 80)
					else
						color = (inst :: BasePart).Color
					end
					chipColor = chipColor or color
					local p = Instance.new("Part")
					p.Name = "WaveCube"
					p.Anchored = true
					p.CanCollide = false
					p.CanQuery = false
					p.CanTouch = false
					p.CastShadow = false
					p.Size = Vector3.new(cell, cell, cell)
					p.Color = color:Lerp(Color3.new(0, 0, 0), rng:NextNumber(0, 0.12))
					pcall(function()
						p.Material = mat
					end)
					if inst ~= terrain then
						p.TopSurface = (inst :: BasePart).TopSurface
					end
					local rest = CFrame.new(hit.Position.X, hit.Position.Y - cell / 2 - 0.05, hit.Position.Z)
					p.CFrame = rest
					p.Parent = folder
					local fall = 1 - (d / R) * 0.65
					table.insert(cubes, {
						part = p,
						rest = rest,
						t0 = d / WAVE_SPEED,
						amp = height * fall * rng:NextNumber(0.8, 1.15),
						tilt = Vector3.new(rng:NextNumber(-0.25, 0.25), rng:NextNumber(-0.2, 0.2), rng:NextNumber(-0.25, 0.25)),
					})
					table.insert(parts, p)
				end
			end
		end
	end
	if #cubes == 0 then
		return
	end
	-- осколки земли из точки удара, как при ломании блока
	Fx.burst(center + Vector3.new(0, 0.4, 0), { tex = "square", color = chipColor, color2 = (chipColor :: Color3):Lerp(Color3.new(0, 0, 0), 0.25), n = if low then 6 else 16, speed = NumberRange.new(8, 16), size = 0.55, size2 = 0.4, life = 0.8, rot = true, accel = Vector3.new(0, -45, 0), light = 0, spread = 70 })
	local t0 = os.clock()
	local last = R / WAVE_SPEED + WAVE_BUMP
	local cfs: { CFrame } = table.create(#cubes)
	local conn: RBXScriptConnection? = nil
	local function finish()
		if conn then
			conn:Disconnect()
			conn = nil
		end
		for _, p in parts do
			p:Destroy()
		end
	end
	conn = RunService.Heartbeat:Connect(function()
		local t = os.clock() - t0
		if t > last + 0.05 then
			finish()
			return
		end
		for i, c in cubes do
			local u = (t - c.t0) / WAVE_BUMP
			if u <= 0 or u >= 1 then
				cfs[i] = c.rest
			else
				local s = math.sin(math.pi * u)
				cfs[i] = c.rest * CFrame.new(0, c.amp * s, 0) * CFrame.Angles(c.tilt.X * s, c.tilt.Y * s, c.tilt.Z * s)
			end
		end
		local okMove = pcall(function()
			workspace:BulkMoveTo(parts, cfs, Enum.BulkMoveMode.FireCFrameChanged)
		end)
		if not okMove then
			for i, c in cubes do
				c.part.CFrame = cfs[i]
			end
		end
	end)
	Debris:AddItem(parts[1], last + 2) -- страховка: если цикл не дошёл до конца, первый куб всё равно уйдёт
	task.delay(last + 1, finish)
end

---------------------------------------------------------------------
-- V64: аура заряда вокруг героя («как в аниме»): пламя и искры вверх, энергия стягивается к копью, круг и руны
-- на земле, камни отрываются от земли и кружат, на высоком заряде бьют разряды.
-- feet: точка на земле под героем. Возвращает объект: update(dt, k, c1, c2, tremble, chest), pulse(color),
-- release() (выброс при броске, сам себя убирает), destroy(). Всё лежит только у этого клиента.
---------------------------------------------------------------------
function Fx.aura(feet: Vector3): any
	local low = Fx.lowFx == true
	local model = Instance.new("Folder")
	model.Name = "ChargeAura"
	local function ghost(size: Vector3, cf: CFrame): Part
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.CastShadow = false
		p.Transparency = 1
		p.Size = size
		p.CFrame = cf
		p.Parent = model
		return p
	end
	local white = Color3.new(1, 1, 1)
	-- пламя и искры идут вверх из площадки под ногами
	local base = ghost(Vector3.new(4.2, 0.2, 4.2), CFrame.new(feet + Vector3.new(0, 0.2, 0)))
	local flame = Instance.new("ParticleEmitter")
	flame.Texture = TEX.fire
	flame.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 2.4), NumberSequenceKeypoint.new(1, 0.6) })
	flame.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, 0.55), NumberSequenceKeypoint.new(1, 1) })
	flame.Lifetime = NumberRange.new(0.45, 0.8)
	flame.Speed = NumberRange.new(6, 11)
	flame.SpreadAngle = Vector2.new(6, 6)
	flame.Acceleration = Vector3.new(0, 6, 0)
	flame.LightEmission = 1
	flame.LightInfluence = 0
	flame.EmissionDirection = Enum.NormalId.Top
	flame.Rate = 0
	flame.Parent = base
	local sparks = Instance.new("ParticleEmitter")
	sparks.Texture = TEX.sparkle
	sparks.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 0) })
	sparks.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(1, 1) })
	sparks.Lifetime = NumberRange.new(0.5, 0.9)
	sparks.Speed = NumberRange.new(9, 17)
	sparks.SpreadAngle = Vector2.new(10, 10)
	sparks.Drag = 1
	sparks.LightEmission = 1
	sparks.LightInfluence = 0
	sparks.EmissionDirection = Enum.NormalId.Top
	sparks.Rate = 0
	sparks.Parent = base
	-- энергия стягивается к копью: частицы рождаются на сфере и летят внутрь
	-- V65: оболочка 10 стадов (было 13): частицы не рождаются за камерой перед героем
	local shell = ghost(Vector3.new(10, 10, 10), CFrame.new(feet + Vector3.new(0, 4, 0)))
	local gather = Instance.new("ParticleEmitter")
	gather.Texture = TEX.glow
	gather.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(1, 0.08) })
	gather.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, 0.1), NumberSequenceKeypoint.new(1, 0.4) })
	gather.Lifetime = NumberRange.new(0.42, 0.5)
	gather.Speed = NumberRange.new(10, 11)
	gather.LightEmission = 1
	gather.LightInfluence = 0
	gather.Rate = 0
	pcall(function()
		gather.Shape = Enum.ParticleEmitterShape.Sphere
		gather.ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward
		gather.ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface
	end)
	gather.Parent = shell
	-- круг на земле
	local disc = Instance.new("Part")
	disc.Shape = Enum.PartType.Cylinder
	disc.Anchored = true
	disc.CanCollide = false
	disc.CanQuery = false
	disc.CanTouch = false
	disc.CastShadow = false
	disc.Material = Enum.Material.Neon
	disc.Transparency = 1
	disc.Size = Vector3.new(0.08, 4, 4)
	disc.CFrame = CFrame.new(feet + Vector3.new(0, 0.1, 0)) * CFrame.Angles(0, 0, math.rad(90))
	disc.Parent = model
	-- руны по кругу
	local runes: { Part } = {}
	for _ = 1, (if low then 0 else 6) do
		local r = Instance.new("Part")
		r.Anchored = true
		r.CanCollide = false
		r.CanQuery = false
		r.CanTouch = false
		r.CastShadow = false
		r.Material = Enum.Material.Neon
		r.Transparency = 1
		r.Size = Vector3.new(0.45, 0.1, 1.2)
		r.Parent = model
		table.insert(runes, r)
	end
	-- камни, которые отрывает от земли
	local rocks: { { part: Part, ang: number, rad: number, lift: number, spin: Vector3, phase: number } } = {}
	local rng = Random.new()
	for _ = 1, (if low then 4 else 11) do
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.CastShadow = false
		p.Material = Enum.Material.Slate
		p.Color = Color3.fromRGB(118, 104, 92):Lerp(Color3.fromRGB(70, 66, 64), rng:NextNumber())
		local s = rng:NextNumber(0.22, 0.6)
		p.Size = Vector3.new(s, s * rng:NextNumber(0.6, 1), s * rng:NextNumber(0.7, 1.2))
		p.Transparency = 1
		p.Parent = model
		table.insert(rocks, {
			part = p,
			ang = rng:NextNumber(0, math.pi * 2),
			rad = rng:NextNumber(2.0, 3.2), -- V65: не дальше перил перед точкой броска (3.4)
			lift = rng:NextNumber(0.8, 4.6),
			spin = Vector3.new(rng:NextNumber(-3, 3), rng:NextNumber(-3, 3), rng:NextNumber(-3, 3)),
			phase = rng:NextNumber(0, 6),
		})
	end
	local light = Instance.new("PointLight")
	light.Shadows = false
	light.Brightness = 0
	light.Range = 12
	light.Parent = shell
	model.Parent = folder

	local self: any = { k = 0, t = 0, dead = false, color = white, nextBolt = 0, flashUntil = 0 }
	local rate = if low then 0.4 else 1

	local function setColor(c1: Color3, c2: Color3)
		if self.color == c1 then
			return
		end
		self.color = c1
		flame.Color = ColorSequence.new(c1, c2)
		sparks.Color = ColorSequence.new(white, c1)
		gather.Color = ColorSequence.new(c1, white)
		disc.Color = c1
		light.Color = c1
		for _, r in runes do
			r.Color = c1
		end
	end

	function self.update(dt: number, k: number, c1: Color3, c2: Color3, tremble: number, chest: Vector3?)
		if self.dead then
			return
		end
		k = math.clamp(k, 0, 1)
		self.k = k
		self.t += dt
		local t = self.t
		setColor(c1, c2)
		flame.Rate = (6 + 42 * k) * rate
		sparks.Rate = (4 + 46 * k * k) * rate
		gather.Rate = (10 + 70 * k) * rate
		if chest then
			shell.CFrame = CFrame.new(chest)
		end
		local pulse = 0.5 + 0.5 * math.sin(t * (5 + 9 * k))
		light.Brightness = 0.4 + 2.6 * k + pulse * 0.5 * k
		light.Range = 10 + 12 * k
		local radius = math.min(2.4 + 2.8 * k + pulse * 0.25, 3.2) -- V65: круг не уходит за перила
		disc.Size = Vector3.new(0.08, radius * 2, radius * 2)
		disc.Transparency = 0.86 - 0.3 * k - pulse * 0.06
		for i, r in runes do
			local a = t * (0.7 + 3.2 * k) + i * math.pi * 2 / #runes
			local p = feet + Vector3.new(math.cos(a) * radius * 0.9, 0.18, math.sin(a) * radius * 0.9)
			r.CFrame = CFrame.lookAt(p, feet + Vector3.new(0, 0.18, 0))
			r.Transparency = 0.5 - 0.35 * k
		end
		local shake = 0.02 + 0.1 * tremble
		for _, rock in rocks do
			local a = rock.ang + t * (0.25 + 0.9 * k)
			local up = rock.lift * (k * k * (3 - 2 * k)) + math.sin(t * 2.2 + rock.phase) * 0.18 * k
			local p = feet + Vector3.new(math.cos(a) * rock.rad, 0.15 + up, math.sin(a) * rock.rad)
			p += Vector3.new(math.noise(t * 30, rock.phase) * shake, math.noise(rock.phase, t * 30) * shake, 0)
			rock.part.CFrame = CFrame.new(p) * CFrame.Angles(rock.spin.X * t * k, rock.spin.Y * t * k, rock.spin.Z * t * k)
			rock.part.Transparency = if k > 0.04 then 0 else 1
		end
		-- разряды между копьём и землёй на высоком заряде
		if not low and k > 0.55 and t >= self.nextBolt and chest then
			self.nextBolt = t + 0.42 - 0.26 * k
			local a = rng:NextNumber(0, math.pi * 2)
			local r = rng:NextNumber(1.5, radius)
			Fx.lightning(chest + Vector3.new(rng:NextNumber(-1, 1), rng:NextNumber(0.5, 2), rng:NextNumber(-1, 1)), feet + Vector3.new(math.cos(a) * r, 0.1, math.sin(a) * r), c1, 6, 0.14 + 0.1 * k)
		end
	end

	-- новая ступень заряда: вспышка и волна
	function self.pulse(color: Color3)
		if self.dead then
			return
		end
		Fx.ring(feet + Vector3.new(0, 0.25, 0), color, 6 + self.k * 6, 0.45)
		Fx.sphere(feet + Vector3.new(0, 3, 0), color, 3.2 + self.k * 2.5, 0.3)
		sparks:Emit(if low then 8 else 26)
		flame:Emit(if low then 4 else 10)
	end

	function self.destroy()
		if self.dead then
			return
		end
		self.dead = true
		model:Destroy()
	end

	-- бросок: всё, что копилось, разлетается наружу
	function self.release()
		if self.dead then
			return
		end
		self.dead = true
		flame.Rate = 0
		sparks.Rate = 0
		gather.Rate = 0
		sparks:Emit(if low then 10 else 40)
		for _, r in runes do
			tween(r, 0.3, { Transparency = 1 })
		end
		local d = disc.Size.Y
		tween(disc, 0.45, { Size = Vector3.new(0.04, d * 2.4, d * 2.4), Transparency = 1 })
		tween(light, 0.5, { Brightness = 0 })
		for _, rock in rocks do
			local p = rock.part.Position
			local out = Vector3.new(p.X - feet.X, 0, p.Z - feet.Z)
			out = if out.Magnitude > 1e-3 then out.Unit else Vector3.xAxis
			tween(rock.part, 0.55, { CFrame = CFrame.new(p + out * (7 + rock.rad * 2) + Vector3.new(0, -math.max(0, p.Y - feet.Y) + 0.2, 0)), Transparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		end
		Debris:AddItem(model, 1.1)
	end

	return self
end

return Fx
