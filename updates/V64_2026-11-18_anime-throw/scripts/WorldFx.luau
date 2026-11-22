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
	local shell = ghost(Vector3.new(13, 13, 13), CFrame.new(feet + Vector3.new(0, 4, 0)))
	local gather = Instance.new("ParticleEmitter")
	gather.Texture = TEX.glow
	gather.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(1, 0.08) })
	gather.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, 0.1), NumberSequenceKeypoint.new(1, 0.4) })
	gather.Lifetime = NumberRange.new(0.42, 0.5)
	gather.Speed = NumberRange.new(13, 14)
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
			rad = rng:NextNumber(2.2, 4.8),
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
		local radius = 2.4 + 2.8 * k + pulse * 0.25
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
