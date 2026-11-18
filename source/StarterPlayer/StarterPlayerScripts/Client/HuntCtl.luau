-- StarterPlayerScripts/Client/HuntCtl.luau
-- Охота «Натяжение»: засада → зажал (множитель растёт e^t) → копьё дрожит перед СРЫВОМ → отпустил вовремя →
-- бросок по ступени (×1…×100) → камера летит за копьём через зоны → раскрытие добычи → снова в засаду.
-- ПК: ЛКМ/Пробел — держать, Q — выйти. Телефон: кнопка 🗡️, «Выйти».
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

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
local camBase: CFrame = CFrame.new()
local camMode = "ambush" -- ambush | follow | free
local followFlight: any = nil
local holding = false
local tension: any = nil
local chargeT0 = 0
local lastTierSent = 1
local cooldownUntil = 0
local fovTarget = 70
local chargeSound: Sound? = nil

local function stopChargeSound()
	if chargeSound then
		chargeSound:Destroy()
		chargeSound = nil
	end
end

local function setState(s: string)
	HuntCtl.state = s
	HuntCtl.Changed:Fire(s)
end

---------------------------------------------------------------------
-- Маскировка засад: открыта, когда пусто; закрывается, когда кто-то сел (видят все)
---------------------------------------------------------------------
local camoBase: { [BasePart]: CFrame } = {}
local function camoSet(m: Model, closed: boolean, instant: boolean?)
	local f = m:FindFirstChild("Camo")
	if not f then
		return
	end
	for _, p in f:GetChildren() do
		if p:IsA("BasePart") then
			local base = camoBase[p]
			if not base then
				base = p.CFrame
				camoBase[p] = base
			end
			local off = Vector3.new(p:GetAttribute("ox") or 0, p:GetAttribute("oy") or 0, p:GetAttribute("oz") or 0)
			local target = closed and base or (base + off)
			if instant then
				p.CFrame = target
			else
				Fx.tween(p, 0.5, { CFrame = target }, Enum.EasingStyle.Back)
			end
		end
	end
	if not instant then
		Sfx.at((m:GetPivot()).Position, "rustle", closed and 1.1 or 0.9, 0.5)
	end
end

local function promptOf(m: Model): ProximityPrompt?
	local p = m:FindFirstChild("Prompt")
	return p and p:FindFirstChildOfClass("ProximityPrompt") or nil
end

local function watchAmbush(m: Instance)
	if not m:IsA("Model") then
		return
	end
	local model = m :: Model
	local function upd(instant: boolean?)
		local occ = model:GetAttribute("Occupant")
		camoSet(model, occ ~= nil, instant)
		local pr = promptOf(model)
		if pr then
			pr.Enabled = occ == nil
			pr.ObjectText = occ and ("Occupied: " .. tostring(model:GetAttribute("OccupantName") or "")) or tostring(model:GetAttribute("Title") or "Hunting Blind")
		end
	end
	model:GetAttributeChangedSignal("Occupant"):Connect(function()
		upd(false)
	end)
	upd(true)
end
for _, m in ambushFolder:GetChildren() do
	watchAmbush(m)
end

---------------------------------------------------------------------
-- Камера
---------------------------------------------------------------------
local function ambushCam(): CFrame
	local s = stand :: BasePart
	local p = s.Position + Vector3.new(0, 3, 0)
	return CFrame.lookAt(p + Vector3.new(2.4, 4.2, 9.5), p + Vector3.new(0, 1, -45))
end

local orbitT = 0
RunService:BindToRenderStep("HuntCam", Enum.RenderPriority.Camera.Value + 1, function(dt)
	if HuntCtl.state == "idle" or Reveal.active or camMode == "free" then
		return
	end
	camera.CameraType = Enum.CameraType.Scriptable
	local a = 1 - math.exp(-dt * 6)
	local target = camBase
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
	elseif HuntCtl.state == "charging" then
		-- лёгкий наезд по мере натяжения
		local m = tension and Config.tensionAt(os.clock() - chargeT0) or 1
		local k = math.log(m) / math.log(Config.TENSION.cap)
		target = camBase * CFrame.new(0, -k * 0.8, -k * 3.5)
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
	camera.CFrame = camera.CFrame:Lerp(target, a)
	camera.FieldOfView += (fovTarget - camera.FieldOfView) * (1 - math.exp(-dt * 8))
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
	local idx = model:GetAttribute("Index")
	local h = hum()
	if not h or h.Health <= 0 or type(idx) ~= "number" then
		return
	end
	setState("entering")
	local ok, err = AmbushFn:InvokeServer("enter", idx)
	if not ok then
		UI.toast(tostring(err or "This hunting blind is occupied"), "warn")
		setState("idle")
		return
	end
	cur = model
	stand = model:FindFirstChild("Stand") :: BasePart?
	if not stand then
		setState("idle")
		return
	end
	saved = { ws = h.WalkSpeed, jp = h.JumpPower, jh = h.JumpHeight, ar = h.AutoRotate, fov = camera.FieldOfView }
	h.WalkSpeed = 0
	h.JumpPower = 0
	h.JumpHeight = 0
	h.AutoRotate = false
	placeOnStand()
	Animator.play("Hide")
	camBase = ambushCam()
	camMode = "ambush"
	fovTarget = 70
	Hud.setMode("hunt")
	Hud.setChances("")
	Sfx.play("rustle", 1.2, 0.6)
	setState("ready")
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
	if hrp and pr then
		hrp.CFrame = CFrame.lookAt(pr.Position + Vector3.new(0, 1.5, 3), pr.Position + Vector3.new(0, 1.5, 10))
	end
	camera.CameraType = Enum.CameraType.Custom
	camera.FieldOfView = saved.fov or 70
	Hud.setMode("normal")
	cur = nil
	stand = nil
	followFlight = nil
	setState("idle")
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
	fovTarget = 72 + tierIdx * 1.2
	local clip = tier.clip
	Animator.play(clip)
	if crashed then
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
	if not res then
		Animator.play("Hide")
		Hud.tensionReset()
		setState("ready")
		return
	end
	-- полёт
	local c = player.Character
	local from = Animator.handPosition(c) or ((stand :: BasePart).Position + Vector3.new(0, 5, 0))
	local s = stand :: BasePart
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
	camMode = "ambush"
	camBase = ambushCam()
	fovTarget = 70
	if res.escaped then
		Animator.play("Shrug")
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
RunService.Heartbeat:Connect(function()
	if HuntCtl.state ~= "charging" or not tension then
		return
	end
	local t = os.clock() - chargeT0
	local m = Config.tensionAt(t)
	local crashT = Config.timeFor(tension.crashAt)
	local tell = Config.TENSION.tellTime
	local tremble = math.clamp((t - (crashT - tell)) / tell, 0, 1)
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
		end
		fovTarget = 70 - ti * 2
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
local function down()
	pressed = true
	if HuntCtl.state == "ready" then
		task.spawn(startCharge)
	end
end
local function up()
	pressed = false
	holding = false
end

Hud.ThrowDown.Event:Connect(down)
Hud.ThrowUp.Event:Connect(up)
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
	end
end)
UserInputService.InputEnded:Connect(function(i)
	if i.UserInputType == Enum.UserInputType.MouseButton1 or i.KeyCode == Enum.KeyCode.Space or i.KeyCode == Enum.KeyCode.ButtonR2 or i.UserInputType == Enum.UserInputType.Touch then
		up()
	end
end)

-- Смерть/респаун — выйти
player.CharacterAdded:Connect(function()
	if HuntCtl.state ~= "idle" then
		stopChargeSound()
		cur = nil
		stand = nil
		followFlight = nil
		tension = nil
		camera.CameraType = Enum.CameraType.Custom
		Hud.setMode("normal")
		setState("idle")
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

return HuntCtl
