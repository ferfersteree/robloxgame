-- StarterPlayerScripts/Client/HuntCtl.luau
-- Охота «Натяжение»: засада → зажал (множитель растёт e^t) → копьё дрожит перед СРЫВОМ → отпустил вовремя →
-- бросок по ступени (×1…×100) → камера летит за копьём через зоны → раскрытие добычи → снова в засаду.
-- ПК: ЛКМ/Пробел — держать, Q — выйти. Телефон: кнопка 🗡️, «Выйти».
-- V36: вместо пяти одиночных засад одна зона «Throwing Grounds» (Workspace/Map/Ambushes/ThrowingGrounds) с несколькими
-- дорожками: подсказка одна, сервер выдаёт свободную дорожку (Stands/StandN), лампа дорожки зелёная/красная.
-- V64: место для броска одно (сервер убирает лишние дорожки). Вход: шагнуть на площадку или нажать подсказку,
-- экран темнеет, героя переносит. Камера от третьего лица сбоку, чуть выше головы. Пока зажата ЛКМ или палец
-- в любом месте экрана, герой заряжает бросок: стойка, аура, камни, линии скорости. Бросок по ступеням со своей
-- хореографией (PoseData) и эффектами выпуска.
local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local Roll = require(RS.Shared.Roll)
local Net = require(RS.Shared.Net)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Fx = require(script.Parent.WorldFx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Animator = require(script.Parent.Animator)
local SpearFx = require(script.Parent.SpearFx)
local Reveal = require(script.Parent.Reveal)

local HuntCtl = {}
HuntCtl.state = "idle" -- idle | entering | ready | charging | throwing | leaving
HuntCtl.Changed = Instance.new("BindableEvent")

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera
local AmbushFn = Net.fn("Ambush")
local FxEv = Net.ev("Fx")
local ambushFolder = workspace:WaitForChild("Map"):WaitForChild("Ambushes")

local cur: Model? = nil
local stand: BasePart? = nil
local saved: { [string]: any } = {}
local camMode = "side" -- side | throw | follow | free
local followFlight: any = nil
local holding = false
local tension: any = nil
local chargeT0 = 0
local lastTierSent = 1
local cooldownUntil = 0
local fovTarget = 70
local chargeSound: Sound? = nil

-- V64: все числа для подгонки вида лежат здесь. Смещения камеры заданы от корня героя на площадке:
-- X вправо от героя, Y вверх, Z назад (герой смотрит в −Z).
local ANIME = {
	fadeIn = 0.22, -- затемнение при входе, секунды
	fadeOut = 0.45, -- проявление после переноса
	walkIn = 2.3, -- радиус площадки: зашёл внутрь, начинается перенос
	walkOut = 4.6, -- дальше этого радиуса вход снова взводится
	sideEye = Vector3.new(8.4, 3.5, 2.4), -- камера в покое: сбоку справа, чуть выше головы, немного сзади
	sideEyeFull = Vector3.new(5.6, 2.2, -1.3), -- на полном заряде: ближе, на уровне головы, чуть спереди
	sideLook = Vector3.new(0, 1.1, -0.4), -- куда смотрит камера (грудь героя)
	sideFov = 62,
	sideFovFull = 50,
	sideRoll = -5, -- наклон горизонта на полном заряде, градусы
	throwEye = Vector3.new(4.6, -1.6, -2.6), -- на замахе: низко спереди-сбоку, снизу вверх на героя
	throwFov = 78,
	throwRoll = 9,
}
local chargeLevel = 0 -- 0..1: натяжение в логарифмической шкале (поза, камера, аура)
local chargeSmooth = 0 -- то же, сглаженное для камеры
local camSnap = false -- следующий кадр камеры ставится сразу, без подлёта
local aura: any = nil
local lines: any = nil
local linesTarget, linesNow = 0, 0
local chargeCC: ColorCorrectionEffect? = nil
local stopChargeFx: () -> () = function() end

local function stopChargeSound()
	if chargeSound then
		chargeSound:Destroy()
		chargeSound = nil
	end
end

local function setState(s: string)
	HuntCtl.state = s
	-- V64: эффекты заряда живут, только пока герой заряжает или бросает
	if s ~= "charging" and s ~= "throwing" then
		stopChargeFx()
	end
	HuntCtl.Changed:Fire(s)
end

---------------------------------------------------------------------
-- Зона для кидания: лампы дорожек (зелёная - свободна, красная - занята) и подсказка со счётом свободных
---------------------------------------------------------------------
local LAMP_FREE = Color3.fromRGB(70, 220, 110)
local LAMP_BUSY = Color3.fromRGB(235, 70, 60)

local function promptOf(m: Model): ProximityPrompt?
	local p = m:FindFirstChild("Prompt")
	return p and p:FindFirstChildOfClass("ProximityPrompt") or nil
end

local function watchZone(m: Instance)
	if not m:IsA("Model") then
		return
	end
	local model = m :: Model
	task.spawn(function()
		local stands = model:WaitForChild("Stands", 15)
		if not stands then
			return
		end
		local lamps = model:FindFirstChild("Lamps")
		local function upd(instant: boolean?)
			local free, total = 0, 0
			for _, s in stands:GetChildren() do
				if s:IsA("BasePart") then
					total += 1
					local occ = s:GetAttribute("Occupant")
					if occ == nil then
						free += 1
					end
					local lamp = lamps and lamps:FindFirstChild("Lamp" .. tostring(s:GetAttribute("Index"))) :: BasePart?
					if lamp then
						local col = occ == nil and LAMP_FREE or LAMP_BUSY
						if instant then
							lamp.Color = col
						else
							TweenService:Create(lamp, TweenInfo.new(0.3), { Color = col }):Play()
						end
						local pl = lamp:FindFirstChildOfClass("PointLight")
						if pl then
							pl.Color = col
						end
					end
				end
			end
			local pr = promptOf(model)
			if pr then
				-- V62: место одиночное, занятости нет
				pr.Enabled = total > 0
				pr.ObjectText = tostring(model:GetAttribute("Title") or "Throwing Grounds") .. " · private"
			end
		end
		for _, s in stands:GetChildren() do
			s:GetAttributeChangedSignal("Occupant"):Connect(function()
				upd(false)
			end)
		end
		upd(true)
	end)
end
for _, m in ambushFolder:GetChildren() do
	watchZone(m)
end
ambushFolder.ChildAdded:Connect(watchZone)

-- Высокие части въездного домика (крыша, фронтон, вывеска) могут закрыть камеру полёта копья в первые секунды:
-- пока игрок на дорожке, они у него невидимы (LocalTransparencyModifier и SurfaceGui только на этом клиенте).
local function fadeTall(zone: Model?, on: boolean)
	local g = zone and zone:FindFirstChild("Gatehouse")
	if not g then
		return
	end
	for _, p in g:GetDescendants() do
		if p:IsA("BasePart") and p.Position.Y > 8.3 then
			p.LocalTransparencyModifier = on and 1 or 0
			for _, gui in p:GetChildren() do
				if gui:IsA("SurfaceGui") then
					gui.Enabled = not on
				end
			end
		end
	end
end

---------------------------------------------------------------------
-- Камера
---------------------------------------------------------------------
-- V64: в покое и на заряде камера стоит сбоку справа, чуть выше головы; с зарядом подъезжает и кренится.
-- На замахе: низко спереди-сбоку, смотрит снизу вверх и следит за телом (прыжок, зависание в воздухе).
local function heroBase(): Vector3
	local s = stand :: BasePart
	return s.Position + Vector3.new(0, 3.1, 0)
end

local function sideCam(k: number): CFrame
	local base = heroBase()
	local eye = base + ANIME.sideEye:Lerp(ANIME.sideEyeFull, k)
	return CFrame.lookAt(eye, base + ANIME.sideLook) * CFrame.Angles(0, 0, math.rad(ANIME.sideRoll * k))
end

local function throwCam(): CFrame
	local base = heroBase()
	local focusY = base.Y + 1.2
	local c = player.Character
	local torso = c and c:FindFirstChild("UpperTorso") :: BasePart?
	if torso then
		-- тело в прыжке уходит вверх: камера смотрит за ним, сама остаётся у земли
		focusY = math.max(focusY, torso.Position.Y + 0.4)
	end
	return CFrame.lookAt(base + ANIME.throwEye, Vector3.new(base.X, focusY, base.Z)) * CFrame.Angles(0, 0, math.rad(ANIME.throwRoll))
end

local orbitT = 0
RunService:BindToRenderStep("HuntCam", Enum.RenderPriority.Camera.Value + 1, function(dt)
	if HuntCtl.state == "idle" or Reveal.active or camMode == "free" then
		return
	end
	if not stand then
		-- идёт перенос на площадку (экран тёмный): камеру не трогаем
		return
	end
	camera.CameraType = Enum.CameraType.Scriptable
	chargeSmooth += (chargeLevel - chargeSmooth) * (1 - math.exp(-dt * 5))
	local a = 1 - math.exp(-dt * 6)
	local target: CFrame
	if camMode == "follow" and followFlight then
		local fl = followFlight
		local tier = Config.TIERS[fl.tier] or Config.TIERS[1]
		orbitT += dt
		local dir = fl.dir
		local flat = Vector3.new(dir.X, 0, dir.Z)
		flat = flat.Magnitude > 1e-3 and flat.Unit or Vector3.new(0, 0, -1)
		local ang = tier.orbit * math.sin(orbitT * 1.1) * 1.3
		local back = (CFrame.Angles(0, ang, 0) * -flat)
		local eye = fl.pos + back * (11 + fl.tier) + Vector3.new(0, 4 + fl.tier * 0.5, 0)
		target = CFrame.lookAt(eye, fl.pos + flat * 6)
		a = 1 - math.exp(-dt * 9)
	elseif camMode == "throw" then
		target = throwCam()
		a = 1 - math.exp(-dt * 10)
	else
		target = sideCam(chargeSmooth)
		fovTarget = ANIME.sideFov + (ANIME.sideFovFull - ANIME.sideFov) * chargeSmooth
	end
	if camMode ~= "follow" then
		-- Очень слабое «дыхание» камеры вместо мёртвой статичной картинки.
		local t = os.clock()
		local power = HuntCtl.state == "charging" and 1.8 or 1
		target *= CFrame.Angles(
			math.noise(t * 0.32, 4) * 0.006 * power,
			math.noise(7, t * 0.28) * 0.008 * power,
			math.noise(t * 0.24, 11) * 0.004 * power
		)
	end
	if camSnap then
		camSnap = false
		camera.CFrame = target
		camera.FieldOfView = fovTarget
	else
		camera.CFrame = camera.CFrame:Lerp(target, a)
		camera.FieldOfView += (fovTarget - camera.FieldOfView) * (1 - math.exp(-dt * 8))
	end
	-- линии скорости подтягиваются к своей цели
	local l = lines
	if l then
		linesNow += (linesTarget - linesNow) * (1 - math.exp(-dt * 9))
		l.set(linesNow)
	end
end)

---------------------------------------------------------------------
-- Вход / выход
---------------------------------------------------------------------
local function hum(): Humanoid?
	local c = player.Character
	return c and c:FindFirstChildOfClass("Humanoid") or nil
end

local function placeOnStand()
	local c = player.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
	local s = stand
	if hrp and s then
		hrp.AssemblyLinearVelocity = Vector3.zero
		hrp.CFrame = CFrame.lookAt(s.Position + Vector3.new(0, 3.1, 0), s.Position + Vector3.new(0, 3.1, -10))
	end
end

function HuntCtl.enter(model: Model)
	if HuntCtl.state ~= "idle" then
		return
	end
	local h = hum()
	if not h or h.Health <= 0 then
		return
	end
	setState("entering")
	-- V64: экран темнеет, под затемнением героя переносит на площадку
	pcall(UI.fade, 1, ANIME.fadeIn)
	local t0 = os.clock()
	local function abort(msg: string?)
		pcall(UI.fade, 0, ANIME.fadeOut)
		if msg then
			UI.toast(msg, "warn")
		end
		if HuntCtl.state == "entering" then
			setState("idle")
		end
	end
	-- сервер отдаёт площадку и возвращает её номер
	local called, ok, lane = pcall(AmbushFn.InvokeServer, AmbushFn, "enter")
	local left = ANIME.fadeIn - (os.clock() - t0)
	if left > 0 then
		task.wait(left)
	end
	if not called then
		abort(nil)
		return
	end
	if not ok then
		abort(tostring(lane or "The Throwing Grounds are full"))
		return
	end
	-- пока ждали сервер, персонаж мог погибнуть или состояние сброситься: возвращаем площадку
	if HuntCtl.state ~= "entering" or hum() ~= h or h.Health <= 0 then
		task.spawn(function()
			AmbushFn:InvokeServer("leave")
		end)
		abort(nil)
		return
	end
	local stands = model:FindFirstChild("Stands")
	local st = stands and stands:FindFirstChild("Stand" .. tostring(lane)) :: BasePart?
	if not st then
		task.spawn(function()
			AmbushFn:InvokeServer("leave")
		end)
		abort(nil)
		return
	end
	saved = { ws = h.WalkSpeed, jp = h.JumpPower, jh = h.JumpHeight, ar = h.AutoRotate, fov = camera.FieldOfView }
	local okPlace, errPlace = pcall(function()
		cur = model
		stand = st
		fadeTall(model, true)
		h.WalkSpeed = 0
		h.JumpPower = 0
		h.JumpHeight = 0
		h.AutoRotate = false
		placeOnStand()
		Animator.play("Hide")
		camMode = "side"
		camSnap = true
		chargeLevel = 0
		chargeSmooth = 0
		fovTarget = ANIME.sideFov
		Hud.setMode("hunt")
		Hud.setChances("")
		Sfx.play("rustle", 1.2, 0.6)
	end)
	if not okPlace then
		-- V64: что-то сломалось при постановке на площадку: возвращаем игроку управление, а не оставляем его
		-- замороженным в состоянии «entering» (из него нет выхода ни по Q, ни по кнопке)
		warn("[HuntCtl] enter: " .. tostring(errPlace))
		pcall(fadeTall, model, false)
		pcall(function()
			h.WalkSpeed = saved.ws or Config.WALK_SPEED
			h.JumpPower = saved.jp or 50
			h.JumpHeight = saved.jh or 7.2
			h.AutoRotate = true
		end)
		pcall(Animator.stop)
		cur = nil
		stand = nil
		camera.CameraType = Enum.CameraType.Custom
		camera.FieldOfView = saved.fov or 70
		pcall(Hud.setMode, "normal")
		task.spawn(function()
			AmbushFn:InvokeServer("leave")
		end)
		abort("Could not enter the Throwing Grounds")
		return
	end
	setState("ready")
	pcall(UI.fade, 0, ANIME.fadeOut)
	local d = Backend.data
	if d and d.tutorial < 2 then
		Backend.call("Tutorial", 2)
	end
	HuntCtl.updateChances(1)
end

function HuntCtl.leave()
	if HuntCtl.state == "idle" or HuntCtl.state == "leaving" then
		return
	end
	if HuntCtl.state == "charging" and tension then
		Backend.call("TensionCancel")
		tension = nil
	end
	stopChargeSound()
	setState("leaving")
	holding = false
	pcall(UI.fade, 1, 0) -- V64: перенос обратно тоже под затемнением
	fadeTall(cur, false)
	task.spawn(function()
		AmbushFn:InvokeServer("leave")
	end)
	Animator.stop()
	local h = hum()
	if h then
		h.WalkSpeed = saved.ws or Config.WALK_SPEED
		h.JumpPower = saved.jp or 50
		h.JumpHeight = saved.jh or 7.2
		h.AutoRotate = true
	end
	-- шаг из засады к подсказке
	local c = player.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
	local pr = cur and cur:FindFirstChild("Prompt") :: BasePart?
	local ex = cur and cur:FindFirstChild("Exit") :: BasePart?
	if hrp and ex then
		hrp.AssemblyLinearVelocity = Vector3.zero
		hrp.CFrame = CFrame.lookAt(ex.Position, ex.Position + Vector3.new(0, 0, 10))
	elseif hrp and pr then
		hrp.CFrame = CFrame.lookAt(pr.Position + Vector3.new(0, 1.5, 3), pr.Position + Vector3.new(0, 1.5, 10))
	end
	camera.CameraType = Enum.CameraType.Custom
	camera.FieldOfView = saved.fov or 70
	Hud.setMode("normal")
	cur = nil
	stand = nil
	followFlight = nil
	camMode = "side"
	setState("idle")
	pcall(UI.fade, 0, ANIME.fadeOut)
end

---------------------------------------------------------------------
-- Шансы (подсказка над шкалой)
---------------------------------------------------------------------
local lastChance = 0
function HuntCtl.updateChances(m: number)
	local d = Backend.data
	if not d then
		return
	end
	local st = Config.spearStats(d.spear, d.spears[d.spear])
	local dist = Config.range(d.power) * st.range * Backend.boostMult("range") * Config.distFrac(m)
	local zone = Config.zoneFor(dist)
	local luck = m * Config.distLuck(dist) * Config.powerLuck(d.power) * st.luck * Backend.boostMult("luck") * Backend.demoLuck()
	local list = Roll.tierChances(zone, luck, Backend.capMul(luck))
	local best = list[#list]
	local zc = Config.ZONES[zone]
	local txt = zc.icon .. " " .. zc.name .. " · " .. math.floor(dist) .. " m"
	if best and best.rarity > 1 then
		local rr = Config.RARITIES[best.rarity]
		txt ..= string.format("  ·  <font color=\"#%s\">%s</font> %s", rr.color:ToHex(), rr.name, Num.odds(best.chance))
	end
	Hud.setChances(txt)
end

---------------------------------------------------------------------
-- V64: эффекты заряда и броска. Любой сбой эффекта не должен ломать сам бросок: всё создаётся под pcall.
---------------------------------------------------------------------
local WHITE = Color3.new(1, 1, 1)
local DUST = Color3.fromRGB(196, 170, 130)

-- точка на площадке под ногами героя
local function feetPos(): Vector3?
	local s = stand
	return if s then s.Position + Vector3.new(0, s.Size.Y / 2, 0) else nil
end

-- куда стягивается энергия: рука с копьём
local function gatherPos(): Vector3?
	local c = player.Character
	local hand = c and c:FindFirstChild("RightHand") :: BasePart?
	if hand then
		return hand.Position
	end
	local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
	return if hrp then hrp.Position else nil
end

stopChargeFx = function()
	chargeLevel = 0
	linesTarget = 0
	linesNow = 0
	pcall(Animator.setCharge, nil)
	local a = aura
	aura = nil
	if a then
		pcall(a.destroy)
	end
	local l = lines
	lines = nil
	if l then
		pcall(l.destroy)
	end
	local cc = chargeCC
	chargeCC = nil
	if cc then
		cc:Destroy()
	end
end

local function startChargeFx()
	stopChargeFx()
	pcall(function()
		local feet = feetPos()
		if feet then
			aura = Fx.aura(feet)
		end
		if Fx.lowFx ~= true then
			lines = UI.focusLines(26)
		end
		local cc = Instance.new("ColorCorrectionEffect")
		cc.Name = "ChargeCC"
		cc.Parent = Lighting
		chargeCC = cc
	end)
end

-- каждый кадр заряда: аура, линии скорости, цвет картинки
local function updateChargeFx(dt: number, tier: any, tremble: number)
	local k = chargeLevel
	local a = aura
	if a then
		pcall(a.update, dt, k, tier.color, tier.color2, tremble, gatherPos())
	end
	linesTarget = math.clamp((k - 0.12) * 0.9, 0, 0.7) + tremble * 0.2
	local cc = chargeCC
	if cc then
		cc.Saturation = 0.3 * k
		cc.Contrast = 0.16 * k
		cc.TintColor = WHITE:Lerp(tier.color, 0.14 * k)
	end
end

-- новая ступень заряда: волна, вспышка ауры, имя ступени над героем, нота выше
local function tierUpFx(ti: number, tier: any, at: Vector3)
	local a = aura
	if a then
		pcall(a.pulse, tier.color)
	end
	local l = lines
	if l then
		pcall(l.set, linesNow, WHITE:Lerp(tier.color, 0.45))
	end
	Fx.text(at + Vector3.new(0, 4.4, 0), tier.name, tier.color, 30 + ti * 2, 0.9)
	pcall(Sfx.rise, ti, 0.4)
end

-- срыв: накопленное гаснет без выброса
local function crashFx()
	local a = aura
	aura = nil
	if a then
		pcall(a.destroy)
	end
	local cc = chargeCC
	chargeCC = nil
	if cc then
		cc:Destroy()
	end
	linesTarget = 0
end

-- события клипа броска: прыжок, приземление, топот опорной ноги
local function clipFx(kind: string, tierIdx: number)
	local feet = feetPos()
	if not feet then
		return
	end
	local tier = Config.TIERS[tierIdx]
	local onCamera = camMode == "throw" -- после выпуска камера уже летит за копьём: её не трясём
	if kind == "jump" then
		Fx.ring(feet + Vector3.new(0, 0.15, 0), tier.color, 4 + tierIdx, 0.4)
		Fx.burst(feet + Vector3.new(0, 0.3, 0), { tex = "smoke", color = DUST, n = 12, speed = NumberRange.new(4, 9), size = 1.6, size2 = 3, life = 0.8, light = 0, accel = Vector3.new(0, 2, 0), transp = 0.3 })
		Fx.streak(feet + Vector3.new(0, 0.5, 0), feet + Vector3.new(0, 6 + tierIdx, 0), tier.color, 0.5, 0.3)
		if onCamera then
			Fx.shake(0.12, 0.2)
		end
		Sfx.play("rustle", 1.4, 0.5)
	elseif kind == "land" then
		Fx.ring(feet + Vector3.new(0, 0.15, 0), tier.color, 7 + tierIdx * 1.5, 0.55)
		Fx.ring(feet + Vector3.new(0, 0.2, 0), WHITE, 4 + tierIdx, 0.35)
		Fx.burst(feet + Vector3.new(0, 0.3, 0), { tex = "smoke", color = DUST, n = 18, speed = NumberRange.new(6, 13), size = 1.8, size2 = 3.6, life = 0.9, light = 0, accel = Vector3.new(0, 2, 0), transp = 0.3 })
		if onCamera then
			Fx.shake(0.25 + tier.shake * 0.5, 0.4)
		end
		Sfx.at(feet, "hit_ground", 0.9, 0.8)
	else
		Fx.ring(feet + Vector3.new(0, 0.15, 0), tier.color, 4 + tierIdx, 0.4)
		Fx.burst(feet + Vector3.new(0, 0.3, 0), { tex = "smoke", color = DUST, n = 8, speed = NumberRange.new(4, 8), size = 1.2, size2 = 2.4, life = 0.6, light = 0, accel = Vector3.new(0, 2, 0), transp = 0.35 })
		if onCamera then
			Fx.shake(0.1 + tier.shake * 0.3, 0.25)
		end
	end
end

local function watchClip(clip: string, tierIdx: number)
	local evs = Animator.events(clip)
	if #evs == 0 then
		return
	end
	local t0 = os.clock()
	task.spawn(function()
		for _, ev in evs do
			local w = (ev[1] :: number) - (os.clock() - t0)
			if w > 0 then
				task.wait(w)
			end
			local now = Animator.current()
			if HuntCtl.state ~= "throwing" or now ~= clip then
				return
			end
			pcall(clipFx, ev[2], tierIdx)
		end
	end)
end

-- выпуск копья: накопленное выбрасывает наружу, хлопок поперёк броска, росчерк, белый кадр, рывок камеры
local function launchFx(from: Vector3, to: Vector3, tierIdx: number, crashed: boolean)
	local tier = Config.TIERS[tierIdx]
	local flat = Vector3.new(to.X - from.X, 0, to.Z - from.Z)
	flat = if flat.Magnitude > 1e-3 then flat.Unit else Vector3.new(0, 0, -1)
	local d = (flat + Vector3.yAxis * 0.3).Unit
	if crashed then
		-- срыв: накопленное уже погасло (crashFx), копьё просто срывается с руки
		Fx.shockRing(from + d * 1.2, d, WHITE, 1.8, 0.24)
		Fx.streak(from, from + d * 7, WHITE, 0.25, 0.2)
		return
	end
	local a = aura
	aura = nil
	if a then
		pcall(a.release)
	end
	local cc = chargeCC
	chargeCC = nil
	if cc then
		Fx.tween(cc, 0.35, { Saturation = 0, Contrast = 0, TintColor = WHITE })
		task.delay(0.4, function()
			cc:Destroy()
		end)
	end
	linesNow = 1
	linesTarget = 0
	Fx.shockRing(from + d * 1.2, d, WHITE, 2 + tierIdx * 0.8, 0.26)
	if tierIdx >= 2 then
		Fx.shockRing(from + d * 4, d, tier.color, 3 + tierIdx * 1.2, 0.38)
	end
	if tierIdx >= 4 and Fx.lowFx ~= true then
		Fx.shockRing(from + d * 8, d, tier.color2, 4.5 + tierIdx * 1.5, 0.52)
	end
	Fx.streak(from, from + d * (9 + tierIdx * 5), if tierIdx >= 2 then tier.color else WHITE, 0.3 + tierIdx * 0.08, 0.22)
	Fx.burst(from, { tex = "smoke", color = WHITE, n = 6 + tierIdx * 2, speed = NumberRange.new(12, 26), size = 1, size2 = 2.2, life = 0.45, spread = 20, dir = d, accel = Vector3.zero, light = 0, transp = 0.45, drag = 3 })
	Fx.burst(from, { tex = "star", color = tier.color, color2 = WHITE, n = 6 + tierIdx * 3, speed = NumberRange.new(14, 30), size = 0.5 + tierIdx * 0.08, life = 0.45, spread = 28, dir = d, accel = Vector3.zero, rot = true })
	UI.flash(WHITE, 0.14, if tierIdx >= 3 then 0.7 else 0.35)
	if tierIdx >= 4 then
		task.delay(0.07, function()
			UI.flash(tier.color, 0.25, 0.35)
		end)
	end
	camera.FieldOfView = math.min(camera.FieldOfView + 5 + tierIdx * 2, 110)
	Fx.shake(0.16 + tier.shake * 0.7, 0.35)
	-- волна по земле от ног (у прыжковых бросков герой в воздухе: волна будет при приземлении)
	local feet = feetPos()
	if feet and from.Y - feet.Y < 7.5 then
		Fx.ring(feet + Vector3.new(0, 0.15, 0), tier.color, 5 + tierIdx * 1.4, 0.45)
		Fx.burst(feet + Vector3.new(0, 0.3, 0), { tex = "smoke", color = DUST, n = 10, speed = NumberRange.new(5, 11), size = 1.4, size2 = 2.8, life = 0.7, light = 0, accel = Vector3.new(0, 2, 0), transp = 0.3 })
	end
end

---------------------------------------------------------------------
-- Натяжение
---------------------------------------------------------------------
local pressed = false -- кнопка броска зажата сейчас
local starting = false
local function startCharge()
	if HuntCtl.state ~= "ready" or starting then
		return
	end
	starting = true
	local left = cooldownUntil - os.clock()
	if left > 0 then
		-- нажал во время отката: натяжение начнётся, как только он кончится, если кнопка ещё зажата
		task.wait(left)
		if not pressed or HuntCtl.state ~= "ready" then
			starting = false
			return
		end
	end
	holding = true
	local ok, info = Backend.call("TensionStart", cur and cur:GetAttribute("Lane"))
	starting = false
	if HuntCtl.state ~= "ready" then
		-- пока ждали ответ, игрок вышел или погиб: натяжение не начинаем
		if ok then
			Backend.call("TensionCancel")
		end
		holding = false
		return
	end
	if not ok then
		holding = false
		UI.toast(tostring(info or "Cannot throw right now"), "warn")
		Hud.tensionReset("BAG FULL")
		return
	end
	if not holding then
		-- отпустил, пока ждали сервер → обычный бросок ×1
		tension = info
		chargeT0 = os.clock()
		HuntCtl.release(false)
		return
	end
	tension = info
	chargeT0 = os.clock()
	lastTierSent = 1
	startChargeFx()
	Animator.setCharge(0, 0)
	Animator.play("Charge")
	chargeSound = Sfx.loop("creak", 0.72, 0.1)
	Hud.tensionReset()
	Sfx.play("creak", 1, 0.5)
	setState("charging")
end

function HuntCtl.release(crashed: boolean)
	if not tension then
		return
	end
	local info = tension
	tension = nil
	holding = false
	stopChargeSound()
	local held = os.clock() - chargeT0
	local m = held < Config.TENSION.minHold and 1 or Config.tensionAt(held)
	if crashed then
		m = info.crashAt
	end
	m = math.min(m, Config.TENSION.cap)
	setState("throwing")
	local effectiveM = m * (crashed and Config.TENSION.crashLuck or 1)
	local tierIdx = Config.tierIndex(effectiveM)
	local tier = Config.TIERS[tierIdx]
	local clip = tier.clip
	Animator.play(clip)
	-- V64: замах: камера уходит вниз и вперёд, линии скорости на максимум, события клипа дают пыль и толчки
	camMode = "throw"
	fovTarget = ANIME.throwFov
	linesTarget = if crashed then 0 else 0.9
	watchClip(clip, tierIdx)
	if crashed then
		crashFx()
		Hud.tension(effectiveM, 1, "SLIP · LUCK ×0.25")
		Hud.banner("SLIP!", Theme.C.red, Num.mult(m) .. " → " .. Num.mult(effectiveM) .. " · the spear keeps flying", 1.6)
		UI.flash(Theme.C.red, 0.3, 0.5)
		Fx.shake(0.4, 0.4)
		Sfx.play("crash", 1, 0.9)
	else
		Hud.tension(m, 0, tier.name .. "!")
		if tierIdx >= 2 then
			Hud.banner(tier.name .. "!", tier.color, Num.mult(m), 1.3)
		end
	end
	-- результат с «сервера» параллельно с замахом
	local res: any = nil
	local failed = false
	task.spawn(function()
		local ok, r = Backend.call("Throw", { token = info.token, m = m, crashed = crashed })
		if ok then
			res = r
		else
			failed = true
			UI.toast(tostring(r or "Throw failed"), "bad")
		end
	end)
	task.wait(Animator.release(clip))
	local t0 = os.clock()
	while not res and not failed and os.clock() - t0 < 5 do
		task.wait()
	end
	if HuntCtl.state ~= "throwing" or not stand then
		-- пока шёл замах, игрок вышел или погиб
		return
	end
	if not res then
		Animator.play("Hide")
		Hud.tensionReset()
		camMode = "side"
		setState("ready")
		return
	end
	-- полёт
	local c = player.Character
	local s = stand :: BasePart
	local from = Animator.handPosition(c) or (s.Position + Vector3.new(0, 5, 0))
	local throwDist = math.max(4, res.dist)
	local to = SpearFx.targetFor(s.Position, Vector3.new(0, 0, -1), throwDist, 0.1)
	Fx.burst(from, { tex = "sparkle", color = tier.color, color2 = tier.color2, n = 4 + tierIdx * 2, speed = NumberRange.new(3, 9), size = 0.35 + tierIdx * 0.06, life = 0.55, accel = Vector3.new(0, 2, 0) })
	local d = Backend.data
	local spearId = d and d.spear or "stick"
	local landed: Vector3? = nil
	local flight = SpearFx.launch({ spear = spearId, from = from, to = to, tier = res.tier or tierIdx, crashed = false, isLocal = true, onLand = function(p)
		landed = p
	end })
	FxEv:FireServer({ k = "throw", spear = spearId, from = from, to = to, tier = res.tier or tierIdx, crashed = false })
	local okFx, errFx = pcall(launchFx, from, to, tierIdx, crashed)
	if not okFx then
		warn("[HuntCtl] launch fx: " .. tostring(errFx))
	end
	followFlight = flight
	camMode = "follow"
	orbitT = 0
	fovTarget = 70 + tier.slowmo * 10
	local lastZone = 1
	while not landed do
		local dz = math.max(0, s.Position.Z - flight.pos.Z)
		local z = Config.zoneFor(dz)
		if z > lastZone then
			lastZone = z
			Hud.zone(z)
		end
		task.wait()
	end
	followFlight = nil
	camMode = "free"
	task.wait(0.25)
	-- раскрытие
	flight.revealHeld = true
	local revealOk, revealError = xpcall(Reveal.play, debug.traceback, res, landed :: Vector3, { from = s.Position + Vector3.new(0, 4, 4) })
	flight.revealHeld = false
	if not revealOk then
		warn(revealError)
		UI.toast("Could not show the catch. You can throw again.", "warn")
		HuntCtl.leave()
		return
	end
	if cur == nil then
		return
	end
	-- V64: назад к герою без пролёта через всю карту: короткое затемнение и сразу вид сбоку
	pcall(UI.fade, 1, 0)
	camMode = "side"
	camSnap = true
	chargeLevel = 0
	chargeSmooth = 0
	fovTarget = ANIME.sideFov
	pcall(UI.fade, 0, 0.35)
	if res.escaped then
		Animator.play("Shrug")
		Sfx.play("miss") -- V42: зверь ушёл
	elseif res.item and Config.SPECIES_BY_ID[res.sp] and Config.SPECIES_BY_ID[res.sp].rarity >= 3 then
		Animator.play("Cheer")
		task.wait(1.4)
	end
	if d and d.tutorial < 3 and res.item then
		Backend.call("Tutorial", 3)
	end
	if HuntCtl.state ~= "throwing" then
		return
	end
	Animator.play("Hide")
	Hud.tensionReset()
	cooldownUntil = os.clock() + Config.TENSION.cooldown
	setState("ready")
	HuntCtl.updateChances(1)
	if Backend.bagCount() >= (Backend.data and Backend.data.bagCap or 12) then
		Hud.tensionReset("BAG FULL")
		UI.toast("Bag full! Sell your catch at the market 💰", "warn", 3.5)
	end
end

-- Каждый кадр, пока держим
RunService.Heartbeat:Connect(function(dt)
	if HuntCtl.state ~= "charging" or not tension then
		return
	end
	local t = os.clock() - chargeT0
	local m = Config.tensionAt(t)
	local crashT = Config.timeFor(tension.crashAt)
	local tell = Config.TENSION.tellTime
	local tremble = math.clamp((t - (crashT - tell)) / tell, 0, 1)
	-- V64: уровень заряда 0..1 ведёт стойку героя, камеру и ауру
	chargeLevel = math.clamp(math.log(math.max(m, 1)) / math.log(Config.TENSION.cap), 0, 1)
	Animator.setCharge(chargeLevel, tremble)
	updateChargeFx(dt, Config.TIERS[Config.tierIndex(m)], tremble)
	if chargeSound then
		local k = math.clamp(math.log(m) / math.log(Config.TENSION.cap), 0, 1)
		chargeSound.PlaybackSpeed = 0.68 + k * 0.72 + tremble * 0.25
		chargeSound.Volume = 0.075 + k * 0.065
	end
	Hud.tension(m, tremble)
	local ti = Config.tierIndex(m)
	if ti > lastTierSent then
		lastTierSent = ti
		local tier = Config.TIERS[ti]
		local c = player.Character
		local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
		if hrp then
			Fx.ring(hrp.Position - Vector3.new(0, 2.8, 0), tier.color, 3 + ti, 0.4)
			FxEv:FireServer({ k = "tier", tier = ti, pos = hrp.Position - Vector3.new(0, 2.8, 0) })
			pcall(tierUpFx, ti, tier, hrp.Position)
		end
		Fx.shake(0.04 * ti, 0.2)
	end
	if tremble > 0 then
		Fx.shake(0.05 + tremble * 0.18, 0.1)
	end
	if os.clock() - lastChance > 0.12 then
		lastChance = os.clock()
		HuntCtl.updateChances(m)
	end
	if m >= tension.crashAt then
		HuntCtl.release(true)
	elseif m >= Config.TENSION.cap then
		HuntCtl.release(false)
	elseif not holding then
		HuntCtl.release(false)
	end
end)

---------------------------------------------------------------------
-- Ввод
---------------------------------------------------------------------
-- V55: на телефоне заряд держит одно касание (кнопка 🗡️). Раньше бросок отпускало отпускание ЛЮБОГО пальца:
-- зажал кнопку одним пальцем, коснулся экрана вторым и убрал его, и бросок срывался раньше времени
local chargeTouch: any = nil
local function down(touch: any?)
	-- V64: пока заряд уже держит одно нажатие, новые его не перехватывают (второй палец на кнопке 🗡️, пробел
	-- во время касания). Исключение: палец-владелец уже снят, а событие об этом потерялось
	if pressed then
		local owner = chargeTouch
		local stale = false
		if owner ~= nil then
			local okState, st = pcall(function()
				return owner.UserInputState
			end)
			stale = not okState or st == Enum.UserInputState.End or st == Enum.UserInputState.Cancel
		end
		if not stale then
			return
		end
	end
	pressed = true
	chargeTouch = touch
	if HuntCtl.state == "ready" then
		task.spawn(startCharge)
	end
end
local function up()
	pressed = false
	holding = false
	chargeTouch = nil
end
-- V64: мышь, пробел, геймпад и кнопка 🗡️ под мышью отпускают только заряд, начатый не пальцем.
-- Заряд, который держит палец, отпускает только этот палец (touchEnded)
local function upKeys()
	if chargeTouch == nil then
		up()
	end
end
-- касание закончилось: отпускает бросок только то, что его держало (вынесено в функцию, чтобы проверять без телефона)
function HuntCtl.touchEnded(input: any): boolean
	if chargeTouch ~= nil and input == chargeTouch then
		up()
		return true
	end
	return false
end

Hud.ThrowDown.Event:Connect(function()
	down(Hud.throwTouch)
end)
Hud.ThrowUp.Event:Connect(upKeys)
Hud.ExitClicked.Event:Connect(function()
	if HuntCtl.state == "ready" then
		HuntCtl.leave()
	end
end)

UserInputService.InputBegan:Connect(function(i, gp)
	if HuntCtl.state == "idle" then
		return
	end
	if i.KeyCode == Enum.KeyCode.Q and not gp then
		if HuntCtl.state == "ready" then
			HuntCtl.leave()
		end
	elseif (i.UserInputType == Enum.UserInputType.MouseButton1 and not gp) or (i.KeyCode == Enum.KeyCode.Space and not gp) or i.KeyCode == Enum.KeyCode.ButtonR2 then
		down()
	elseif i.UserInputType == Enum.UserInputType.Touch and not gp and not pressed and chargeTouch == nil then
		-- V64: заряд держит палец в любом месте экрана (кроме кнопок интерфейса). Пока заряд держит одно касание,
		-- остальные не считаются: иначе второй палец срывал бы бросок (ошибка, исправленная в V55)
		down(i)
	end
end)
UserInputService.InputEnded:Connect(function(i)
	if i.UserInputType == Enum.UserInputType.Touch then
		HuntCtl.touchEnded(i)
	elseif i.UserInputType == Enum.UserInputType.MouseButton1 or i.KeyCode == Enum.KeyCode.Space or i.KeyCode == Enum.KeyCode.ButtonR2 then
		upKeys()
	end
end)

-- Смерть/респаун — выйти
player.CharacterAdded:Connect(function()
	if HuntCtl.state ~= "idle" then
		stopChargeSound()
		fadeTall(cur, false)
		cur = nil
		stand = nil
		followFlight = nil
		tension = nil
		holding = false
		camMode = "side"
		camera.CameraType = Enum.CameraType.Custom
		camera.FieldOfView = saved.fov or 70
		Hud.setMode("normal")
		setState("idle")
		pcall(UI.fade, 0, 0.3)
	end
end)

-- Держать персонажа на месте (физика иногда сдвигает)
RunService.Heartbeat:Connect(function()
	if HuntCtl.state == "ready" or HuntCtl.state == "charging" or HuntCtl.state == "throwing" then
		local c = player.Character
		local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
		local s = stand
		if hrp and s and (hrp.Position - (s.Position + Vector3.new(0, 3.1, 0))).Magnitude > 1.5 then
			placeOnStand()
		end
	end
end)

---------------------------------------------------------------------
-- V64: вход шагом на площадку. Площадка одна (Stands, наименьший Index). Вход взводится, когда игрок отошёл от неё
-- дальше walkOut: после выхода, неудачного входа или отказа сервера нужно сначала отойти, иначе вход дёргался бы
-- каждый кадр. Подсказка у входа в зону работает как раньше.
---------------------------------------------------------------------
local function soloSpot(): (Model?, BasePart?)
	for _, zone in ambushFolder:GetChildren() do
		local stands = zone:FindFirstChild("Stands")
		if zone:IsA("Model") and stands then
			local best: BasePart? = nil
			local bestIndex = math.huge
			for _, st in stands:GetChildren() do
				local index = st:GetAttribute("Index")
				if st:IsA("BasePart") and type(index) == "number" and index < bestIndex then
					best = st
					bestIndex = index
				end
			end
			if best then
				return zone, best
			end
		end
	end
	return nil, nil
end

local walkArmed = false
local nextWalkCheck = 0
RunService.Heartbeat:Connect(function()
	local now = os.clock()
	if now < nextWalkCheck then
		return
	end
	nextWalkCheck = now + 0.1
	if HuntCtl.state ~= "idle" then
		return
	end
	local c = player.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
	local h = hum()
	if not hrp or not h or h.Health <= 0 then
		return
	end
	local zone, spot = soloSpot()
	if not zone or not spot then
		return
	end
	local delta = hrp.Position - spot.Position
	local flat = Vector3.new(delta.X, 0, delta.Z).Magnitude
	if flat > ANIME.walkOut or math.abs(delta.Y - 3) > 6 then
		walkArmed = true
	elseif walkArmed and flat < ANIME.walkIn and math.abs(delta.Y - 3) < 4 and not Reveal.active and not UI.windowOpen() then
		walkArmed = false
		task.spawn(HuntCtl.enter, zone)
	end
end)

-- Подсветка площадки, пока на ней никто не стоит: мягко пульсирующий круг и надпись (только у этого клиента)
task.spawn(function()
	local okGlow, errGlow = pcall(function()
		local spot: BasePart? = nil
		for _ = 1, 40 do
			local _, found = soloSpot()
			if found then
				spot = found
				break
			end
			task.wait(0.5)
		end
		if not spot then
			return
		end
		local st = spot :: BasePart
		local glow = Instance.new("Part")
		glow.Name = "ThrowSpotGlow"
		glow.Shape = Enum.PartType.Cylinder
		glow.Anchored = true
		glow.CanCollide = false
		glow.CanQuery = false
		glow.CanTouch = false
		glow.CastShadow = false
		glow.Material = Enum.Material.Neon
		glow.Color = Theme.C.gold
		glow.Transparency = 0.6
		glow.Size = Vector3.new(0.06, ANIME.walkIn * 2, ANIME.walkIn * 2)
		local function place()
			glow.CFrame = CFrame.new(st.Position + Vector3.new(0, st.Size.Y / 2 + 0.05, 0)) * CFrame.Angles(0, 0, math.rad(90))
		end
		place()
		st:GetPropertyChangedSignal("CFrame"):Connect(place)
		local bb = Instance.new("BillboardGui")
		bb.Size = UDim2.fromOffset(240, 44)
		bb.StudsOffsetWorldSpace = Vector3.new(0, 5.2, 0)
		bb.MaxDistance = 70
		bb.LightInfluence = 0
		local label = Instance.new("TextLabel")
		label.BackgroundTransparency = 1
		label.Size = UDim2.fromScale(1, 1)
		label.Font = Theme.FONT
		label.Text = "🗡️ STEP IN TO THROW"
		label.TextColor3 = Theme.C.gold
		label.TextSize = 22
		local stroke = Instance.new("UIStroke")
		stroke.Thickness = 2.5
		stroke.Parent = label
		label.Parent = bb
		bb.Parent = glow
		glow.Parent = Fx.folder
		TweenService:Create(glow, TweenInfo.new(1.1, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), { Transparency = 0.86 }):Play()
		local function show()
			local idle = HuntCtl.state == "idle"
			glow.LocalTransparencyModifier = if idle then 0 else 1
			bb.Enabled = idle
		end
		HuntCtl.Changed.Event:Connect(show)
		show()
	end)
	if not okGlow then
		warn("[HuntCtl] throw spot glow: " .. tostring(errGlow))
	end
end)

---------------------------------------------------------------------
-- V62: одиночное место. Игрок с атрибутом Solo (его ставит сервер на время броска) для остальных невидим и
-- «не твёрдый»: его персонаж, предметы и эффекты на нём скрыты только на этом клиенте. Копья и добыча таких игроков
-- сервер другим не рассылает (Relay). Хижина игрока (его участок) не трогается и видна всем.
---------------------------------------------------------------------
-- на каждого скрытого игрока: что именно поменяли и подписка на новые предметы персонажа
local hidden: { [Player]: { saved: { [Instance]: { [string]: any } }, conn: RBXScriptConnection? } } = {}

local ENABLED_CLASSES = {
	"ParticleEmitter", "Trail", "Beam", "Light", "BillboardGui", "SurfaceGui", "Highlight", "Fire", "Smoke", "Sparkles",
}

local function isEnabledKind(d: Instance): boolean
	for _, cls in ENABLED_CLASSES do
		if d:IsA(cls) then
			return true
		end
	end
	return false
end

local function hideInst(rec: { saved: { [Instance]: { [string]: any } } }, d: Instance)
	if rec.saved[d] then
		return
	end
	if d:IsA("BasePart") then
		rec.saved[d] = { cq = d.CanQuery, ct = d.CanTouch }
		d.LocalTransparencyModifier = 1
		d.CanQuery = false
		d.CanTouch = false
	elseif d:IsA("Decal") or d:IsA("Texture") then
		rec.saved[d] = { dec = true }
		pcall(function()
			(d :: any).LocalTransparencyModifier = 1
		end)
	elseif d:IsA("ForceField") then
		rec.saved[d] = { ff = d.Visible }
		d.Visible = false
	elseif d:IsA("Humanoid") then
		rec.saved[d] = { dd = d.DisplayDistanceType }
		d.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	elseif isEnabledKind(d) then
		rec.saved[d] = { en = (d :: any).Enabled }
		;(d :: any).Enabled = false
	end
end

local function showAll(p: Player)
	local rec = hidden[p]
	if not rec then
		return
	end
	hidden[p] = nil
	if rec.conn then
		rec.conn:Disconnect()
	end
	for d, st in rec.saved do
		pcall(function()
			if d:IsA("BasePart") then
				d.LocalTransparencyModifier = 0
				d.CanQuery = st.cq
				d.CanTouch = st.ct
			elseif st.dec then
				(d :: any).LocalTransparencyModifier = 0
			elseif st.ff ~= nil then
				(d :: any).Visible = st.ff
			elseif st.dd ~= nil then
				(d :: any).DisplayDistanceType = st.dd
			elseif st.en ~= nil then
				(d :: any).Enabled = st.en
			end
		end)
	end
end

local function hideAll(p: Player)
	showAll(p)
	local char = p.Character
	if not char then
		return
	end
	local rec = { saved = {}, conn = nil :: RBXScriptConnection? }
	hidden[p] = rec
	for _, d in char:GetDescendants() do
		hideInst(rec, d)
	end
	rec.conn = char.DescendantAdded:Connect(function(d)
		hideInst(rec, d)
	end)
end

local function watchSolo(p: Player)
	if p == player then
		return
	end
	local function refresh()
		if p:GetAttribute("Solo") == true then
			hideAll(p)
		else
			showAll(p)
		end
	end
	p:GetAttributeChangedSignal("Solo"):Connect(refresh)
	p.CharacterAdded:Connect(function()
		task.defer(refresh)
	end)
	p.CharacterRemoving:Connect(function()
		showAll(p)
	end)
	refresh()
end
for _, p in Players:GetPlayers() do
	watchSolo(p)
end
Players.PlayerAdded:Connect(watchSolo)
Players.PlayerRemoving:Connect(showAll)

return HuntCtl
