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

-- Плоское кольцо-волна по земле
function Fx.ring(pos: Vector3, color: Color3, radius: number, dur: number?, thick: number?)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Cylinder
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Material = Enum.Material.Neon
	p.Color = color
	p.Transparency = 0.15
	p.Size = Vector3.new(thick or 0.3, 1, 1)
	p.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	p.Parent = folder
	local d = dur or 0.6
	tween(p, d, { Size = Vector3.new(0.05, radius * 2, radius * 2), Transparency = 1 })
	Debris:AddItem(p, d + 0.1)
end

-- Сфера-вспышка
function Fx.sphere(pos: Vector3, color: Color3, r: number, dur: number?)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Material = Enum.Material.Neon
	p.Color = color
	p.Transparency = 0.2
	p.Size = Vector3.one * 0.5
	p.CFrame = CFrame.new(pos)
	p.CastShadow = false
	p.Parent = folder
	local d = dur or 0.4
	tween(p, d, { Size = Vector3.one * r * 2, Transparency = 1 })
	Debris:AddItem(p, d + 0.1)
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

-- Столб света из неба (редкие раскрытия)
function Fx.pillar(pos: Vector3, color: Color3, height: number, dur: number, width: number?): Part
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Cylinder
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Material = Enum.Material.Neon
	p.Color = color
	p.Transparency = 1
	p.CastShadow = false
	local w = width or 3
	p.Size = Vector3.new(height, w * 0.2, w * 0.2)
	p.CFrame = CFrame.new(pos + Vector3.new(0, height / 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
	p.Parent = folder
	tween(p, 0.35, { Transparency = 0.25, Size = Vector3.new(height, w, w) }, Enum.EasingStyle.Back)
	task.delay(math.max(0.4, dur - 0.5), function()
		tween(p, 0.5, { Transparency = 1, Size = Vector3.new(height, 0.1, 0.1) })
	end)
	Debris:AddItem(p, dur + 0.2)
	return p
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

return Fx
