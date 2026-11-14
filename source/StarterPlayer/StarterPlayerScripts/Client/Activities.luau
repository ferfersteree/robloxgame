-- StarterPlayerScripts/Client/Activities.luau
-- Активности деревни (награды — заглушки через Backend): тир с мишенями, полоса препятствий с таймером
-- и монетками, батуты, смотровая вышка с облётом леса, светлячки/яйца, костёр с музыкой и монетками.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Fx = require(script.Parent.WorldFx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Animator = require(script.Parent.Animator)
local SpearFx = require(script.Parent.SpearFx)

local Activities = {}
Activities.busy = nil :: string?

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera
local map = workspace:WaitForChild("Map")

local function hrp(): BasePart?
	local c = player.Character
	return c and c:FindFirstChild("HumanoidRootPart") :: BasePart? or nil
end
local function hum(): Humanoid?
	local c = player.Character
	return c and c:FindFirstChildOfClass("Humanoid") or nil
end

local function reward(r: any, at: Vector3?)
	if type(r) ~= "table" then
		return
	end
	if r.coins and r.coins > 0 then
		local from = at and UI.worldToScreen(at) or Vector2.new(camera.ViewportSize.X / 2, camera.ViewportSize.Y / 2)
		Hud.flyCoins(from, r.coins)
		UI.toast("+" .. Num.short(r.coins) .. " coins", "gold")
	end
end

-- Верхняя плашка активности: заголовок, значение, «Выйти»
local function activityBar(title: string, color: Color3, onExit: () -> ()): (Frame, TextLabel)
	local bar = UI.panel({ Color = color, Size = UDim2.fromOffset(460, 70), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 86), Radius = 18, ZIndex = 30, Parent = UI.root })
	UI.label({ Text = title, TextSize = 24, Size = UDim2.new(1, -150, 0, 28), Position = UDim2.fromOffset(16, 4), XAlign = Enum.TextXAlignment.Left, ZIndex = 32, Parent = bar })
	local val = UI.label({ Text = "", TextSize = 30, Size = UDim2.new(1, -150, 0, 34), Position = UDim2.fromOffset(16, 30), XAlign = Enum.TextXAlignment.Left, ZIndex = 32, Parent = bar })
	local ex = UI.button({ Text = "Exit", TextSize = 22, Color = Theme.C.red, Size = UDim2.fromOffset(120, 48), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -12, 0.5, 0), ZIndex = 34 }, onExit)
	ex.Parent = bar
	local sc = Instance.new("UIScale")
	sc.Scale = 0.4
	sc.Parent = bar
	UI.tween(sc, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
	return bar, val
end
Activities.bar = activityBar

-- Поставить персонажа в точку и обездвижить (упаковка, тренировка). Возвращает функцию «отпустить».
function Activities.lockAt(cf: CFrame): () -> ()
	local h, root = hum(), hrp()
	if not h or not root then
		return function() end
	end
	local ws, jp, jh = h.WalkSpeed, h.JumpPower, h.JumpHeight
	h.WalkSpeed = 0
	h.JumpPower = 0
	h.JumpHeight = 0
	h.AutoRotate = false
	root.AssemblyLinearVelocity = Vector3.zero
	root.CFrame = cf
	return function()
		h.WalkSpeed = ws > 0 and ws or Config.WALK_SPEED
		h.JumpPower = jp > 0 and jp or 50
		h.JumpHeight = jh > 0 and jh or 7.2
		h.AutoRotate = true
	end
end

---------------------------------------------------------------------
-- Тир: 6 бросков по движущимся мишеням (клик/тап по точке)
---------------------------------------------------------------------
-- V33: тир с шкалой заряда. Держишь кнопку (ЛКМ / Пробел / палец): шкала растёт; отпустить нужно в ЗЕЛЁНОЙ зоне.
-- Слабо - копьё не долетает, хорошо - небольшой разброс, идеально - точно в прицел, перебор (красная зона) - срыв.
-- Это тренировка перед охотой: там тоже надо отпускать до срыва. Баги прежней версии, исправленные здесь:
--  * SpearFx.launch прижимает цель к земле: копьё падало под мишень; теперь оно втыкается в точку попадания и едет вместе с мишенью;
--  * мишени двигались, пока копьё летело: очки считались по точке на момент клика, а копьё садилось в пустое место;
--  * зависший полёт или гибель персонажа навсегда блокировали тир (Activities.busy не снимался);
--  * заголовок плашки обрезался кнопкой Exit; клики во время броска молча терялись.
local RANGE_CHARGE = 1.7 -- секунд до полной шкалы
local RANGE_ZONES = { weak = 0.35, good = 0.65, perfect = 0.92 } -- границы зон шкалы
function Activities.range()
	if Activities.busy then
		return
	end
	local rangeM = map:FindFirstChild("TargetRange")
	local stand = rangeM and rangeM:FindFirstChild("Stand") :: BasePart?
	local targets = rangeM and rangeM:FindFirstChild("Targets")
	local root, h = hrp(), hum()
	if not stand or not targets or not root or not h then
		return
	end
	local GuiService = game:GetService("GuiService")
	Activities.busy = "range"
	Hud.setMode("busy")
	local cfg = Config.ACTIVITY.range
	local shots, score = cfg.shots, 0
	local done = false
	local savedWS = h.WalkSpeed
	h.WalkSpeed = 0
	root.CFrame = CFrame.lookAt(stand.Position + Vector3.new(0, 3, 0), stand.Position + Vector3.new(0, 3, -10))
	local base: { [Model]: CFrame } = {}
	for _, t in targets:GetChildren() do
		if t:IsA("Model") then
			base[t] = t:GetPivot()
		end
	end
	local bar, val = activityBar("🎯 TARGET RANGE", Theme.C.orange, function()
		done = true
	end)
	local function upd()
		val.Text = string.format("Score: %d   ·   Throws: %d", score, shots)
	end
	upd()

	-- шкала заряда (внизу по центру)
	local panel = UI.panel({ Color = Color3.fromRGB(28, 22, 60), Size = UDim2.fromOffset(580, 124), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -28), Radius = 18, LineThick = 3, ZIndex = 30, Parent = UI.root })
	local hint = UI.label({ Text = "", TextSize = 26, Scaled = true, MaxSize = 26, Size = UDim2.new(1, -24, 0, 32), Position = UDim2.fromOffset(12, 6), ZIndex = 32, Stroke = 3, Parent = panel })
	local barBg = Instance.new("Frame")
	barBg.BackgroundColor3 = Color3.fromRGB(12, 12, 24)
	barBg.BorderSizePixel = 0
	barBg.Size = UDim2.fromOffset(540, 30)
	barBg.Position = UDim2.fromOffset(20, 48)
	barBg.ZIndex = 31
	UI.corner(8).Parent = barBg
	UI.stroke(Color3.new(0, 0, 0), 3, 0, true).Parent = barBg
	barBg.ClipsDescendants = true
	barBg.Parent = panel
	local ZN = RANGE_ZONES
	local zoneDefs = {
		{ 0, ZN.weak, Color3.fromRGB(120, 130, 170), "WEAK" },
		{ ZN.weak, ZN.good, Color3.fromRGB(255, 205, 60), "GOOD" },
		{ ZN.good, ZN.perfect, Color3.fromRGB(84, 214, 52), "PERFECT" },
		{ ZN.perfect, 1, Color3.fromRGB(232, 50, 56), "SLIP" },
	}
	for _, z in zoneDefs do
		local f = Instance.new("Frame")
		f.BorderSizePixel = 0
		f.BackgroundColor3 = z[3]
		f.BackgroundTransparency = 0.35
		f.Position = UDim2.fromScale(z[1], 0)
		f.Size = UDim2.fromScale(z[2] - z[1], 1)
		f.ZIndex = 31
		f.Parent = barBg
		UI.label({ Text = z[4], TextSize = 14, Color = z[3], Size = UDim2.fromOffset(90, 16), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(20 + (z[1] + z[2]) / 2 * 540, 80), ZIndex = 32, Stroke = 2, Parent = panel })
	end
	local fill = Instance.new("Frame")
	fill.BorderSizePixel = 0
	fill.BackgroundColor3 = Color3.new(1, 1, 1)
	fill.BackgroundTransparency = 0.55
	fill.Size = UDim2.fromScale(0, 1)
	fill.ZIndex = 32
	fill.Parent = barBg
	local marker = Instance.new("Frame")
	marker.BorderSizePixel = 0
	marker.BackgroundColor3 = Color3.new(1, 1, 1)
	marker.AnchorPoint = Vector2.new(0.5, 0.5)
	marker.Size = UDim2.fromOffset(6, 44)
	marker.Position = UDim2.new(0, 0, 0.5, 0)
	marker.ZIndex = 34
	UI.stroke(Color3.new(0, 0, 0), 2, 0, true).Parent = marker
	marker.Parent = barBg
	local function setHint(text: string, color: Color3?)
		hint.Text = text
		hint.TextColor3 = color or Theme.C.text
	end
	local IDLE_HINT = UI.mobile and "HOLD the screen, release in the GREEN" or "AIM with the mouse · HOLD LMB or Space · release in the GREEN"
	setHint(IDLE_HINT)

	camera.CameraType = Enum.CameraType.Scriptable
	local eye = stand.Position + Vector3.new(0, 6, 9)
	camera.CFrame = CFrame.lookAt(eye, stand.Position + Vector3.new(0, 2.5, -24))
	local t0 = os.clock()
	local mover = RunService.RenderStepped:Connect(function()
		local t = os.clock() - t0
		for m, cf in base do
			local i = tonumber(m.Name:match("%d+")) or 1
			m:PivotTo(cf * CFrame.new(math.sin(t * (0.8 + i * 0.35) + i) * (1 + i), 0, 0))
		end
	end)

	local busyShot = false
	local charging = false
	local chargeT0 = 0
	local chargeInput: InputObject? = nil
	local aim = Vector2.new(camera.ViewportSize.X / 2, camera.ViewportSize.Y / 2)
	local lastTick = 0

	local function mouseAim()
		local m = UserInputService:GetMouseLocation()
		return Vector2.new(m.X, m.Y - GuiService:GetGuiInset().Y)
	end

	local function shoot(screen: Vector2, power: number)
		busyShot = true
		shots -= 1
		upd()
		local class = power >= ZN.perfect and "slip" or (power < ZN.weak and "weak" or (power < ZN.good and "good" or "perfect"))
		local ray = camera:ScreenPointToRay(screen.X, screen.Y)
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Exclude
		params.FilterDescendantsInstances = { player.Character :: Instance, Fx.folder }
		local aimHit = workspace:Raycast(ray.Origin, ray.Direction * 200, params)
		local aimDist = aimHit and (aimHit.Position - ray.Origin).Magnitude or 40
		local dir = ray.Direction
		-- разброс зависит от того, где отпустили шкалу
		local spread = class == "perfect" and 0.3 or (class == "good" and 1.7 or (class == "weak" and 3 or 0))
		if spread > 0 then
			local right = dir:Cross(Vector3.yAxis).Unit
			local up = right:Cross(dir).Unit
			local a = math.random() * math.pi * 2
			local r = math.sqrt(math.random()) * spread
			dir = (dir * aimDist + right * math.cos(a) * r + up * math.sin(a) * r).Unit
		end
		local hit = workspace:Raycast(ray.Origin, dir * 200, params)
		local to = hit and hit.Position or (ray.Origin + dir * 40)
		local tgt: Model? = nil
		if class == "weak" then
			-- не долетело: копьё падает на землю на полпути
			to = SpearFx.groundAt(ray.Origin + dir * (aimDist * 0.5))
			hit = nil
		elseif class == "slip" then
			to = SpearFx.groundAt(stand.Position + Vector3.new(math.random(-2, 2), 0, -9))
			hit = nil
		end
		local pts = 0
		local localOff: Vector3? = nil
		if hit then
			for m in base do
				if hit.Instance:IsDescendantOf(m) then
					tgt = m
				end
			end
		end
		if tgt then
			local ring = tgt:FindFirstChild("Ring") :: BasePart?
			local c = ring and ring.Position or to
			local off = (to - c).Magnitude
			local p = tgt:GetAttribute("Points") :: number? or 10
			local k = off < 0.8 and 2 or (off < 1.6 and 1.5 or 1)
			pts = math.floor(p * k)
			localOff = tgt:GetPivot():PointToObjectSpace(to) -- точка попадания в системе мишени: копьё поедет вместе с ней
		end
		if class == "perfect" then
			setHint("PERFECT!", Theme.C.green)
		elseif class == "good" then
			setHint("GOOD", Color3.fromRGB(255, 205, 60))
		elseif class == "weak" then
			setHint("TOO WEAK, it fell short", Theme.C.gray)
		else
			setHint("SLIP! You held too long", Theme.C.red)
			Sfx.play("crash", 1, 0.6)
		end
		Animator.play("Throw1")
		task.wait(Animator.release("Throw1"))
		local from = Animator.handPosition(player.Character) or (stand.Position + Vector3.new(0, 5, 0))
		local d = Backend.data
		local fl = SpearFx.launch({ spear = d and d.spear or "stick", from = from, to = to, tier = pts >= 50 and 3 or (pts > 0 and 2 or 1), crashed = class == "slip", isLocal = true })
		if class ~= "slip" then
			fl.dur = 0.45
			fl.h = 1.5
		end
		if tgt and localOff and hit then
			-- SpearFx прижал цель к земле; возвращаем точку попадания и сопровождаем мишень
			local tg, off = tgt :: Model, localOff :: Vector3
			fl.to = to
			local glue: RBXScriptConnection? = nil
			glue = RunService.Heartbeat:Connect(function()
				if fl.done or not tg.Parent then
					if glue then
						glue:Disconnect()
					end
					return
				end
				fl.to = tg:GetPivot():PointToWorldSpace(off)
			end)
		end
		-- защита от вечного полёта: тир не должен зависнуть
		local ft = os.clock()
		while not fl.done and os.clock() - ft < 3 do
			task.wait()
		end
		if not fl.done then
			fl.done = true
			if fl.model then
				fl.model:Destroy()
			end
		end
		if pts > 0 then
			score += pts
			upd()
			UI.popAt(fl.to + Vector3.new(0, 2, 0), "+" .. pts .. (pts >= 50 and " BULLSEYE!" or ""), pts >= 50 and Theme.C.gold or Theme.C.green, 40)
			Sfx.rise(math.min(6, math.floor(pts / 10)), 0.5)
			Fx.burst(fl.to, { tex = "star", color = Theme.C.gold, n = 14, speed = NumberRange.new(6, 14), size = 0.8, life = 0.8, rot = true })
		elseif class ~= "slip" then
			UI.popAt(to + Vector3.new(0, 2, 0), class == "weak" and "short" or "miss", Theme.C.gray, 30)
		end
		task.wait(0.35)
		Animator.stop()
		busyShot = false
		if shots <= 0 then
			done = true
		else
			setHint(IDLE_HINT)
		end
	end

	local function release()
		if not charging then
			return
		end
		charging = false
		chargeInput = nil
		fill.Size = UDim2.fromScale(0, 1)
		marker.Position = UDim2.new(0, 0, 0.5, 0)
		local power = math.min(1, (os.clock() - chargeT0) / RANGE_CHARGE)
		local at = aim
		task.spawn(shoot, at, power)
	end
	local function startCharge(input: InputObject)
		if charging or busyShot or shots <= 0 or done then
			return
		end
		charging = true
		chargeT0 = os.clock()
		chargeInput = input
		if input.UserInputType == Enum.UserInputType.Touch then
			aim = Vector2.new(input.Position.X, input.Position.Y)
		else
			aim = mouseAim()
		end
		Animator.play("Charge")
		Sfx.play("creak", 1, 0.4)
	end

	local chargeConn = RunService.RenderStepped:Connect(function()
		if not charging then
			return
		end
		local ci = chargeInput
		if ci and ci.UserInputType ~= Enum.UserInputType.Touch then
			aim = mouseAim()
		end
		local p = math.min(1, (os.clock() - chargeT0) / RANGE_CHARGE)
		fill.Size = UDim2.fromScale(p, 1)
		marker.Position = UDim2.new(p, 0, 0.5, 0)
		if p < ZN.weak then
			setHint("Keep holding...", Theme.C.text)
		elseif p < ZN.good then
			setHint("Almost! Keep holding", Color3.fromRGB(255, 205, 60))
		elseif p < ZN.perfect then
			setHint("RELEASE NOW!", Theme.C.green)
		else
			setHint("TOO MUCH! Release!", Theme.C.red)
		end
		if os.clock() - lastTick > 0.32 - 0.22 * p then
			lastTick = os.clock()
			Sfx.play("tick", 0.8 + p * 0.9, 0.35)
		end
		if p >= 1 then
			release() -- перегрузили: срыв
		end
	end)
	local inputBegan = UserInputService.InputBegan:Connect(function(i, gp)
		if gp then
			return
		end
		if i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch or i.KeyCode == Enum.KeyCode.Space then
			startCharge(i)
		end
	end)
	local inputChanged = UserInputService.InputChanged:Connect(function(i)
		if charging and i == chargeInput and i.UserInputType == Enum.UserInputType.Touch then
			aim = Vector2.new(i.Position.X, i.Position.Y)
		end
	end)
	local inputEnded = UserInputService.InputEnded:Connect(function(i)
		if charging and (i == chargeInput or (i.UserInputType == Enum.UserInputType.MouseButton1 and chargeInput and chargeInput.UserInputType == Enum.UserInputType.MouseButton1) or (i.KeyCode == Enum.KeyCode.Space and chargeInput and chargeInput.KeyCode == Enum.KeyCode.Space)) then
			release()
		end
	end)

	while not done do
		task.wait(0.1)
		-- персонаж погиб или заменён: выходим, чтобы тир и камера не остались заблокированными
		local nr, nh = hrp(), hum()
		if nr ~= root or not nh or nh ~= h or nh.Health <= 0 then
			done = true
		end
	end
	charging = false
	local waitT = os.clock()
	while busyShot and os.clock() - waitT < 6 do
		task.wait(0.1)
	end
	inputBegan:Disconnect()
	inputChanged:Disconnect()
	inputEnded:Disconnect()
	chargeConn:Disconnect()
	mover:Disconnect()
	for m, cf in base do
		m:PivotTo(cf)
	end
	Animator.stop()
	panel:Destroy()
	bar:Destroy()
	if score > 0 then
		local ok, r = Backend.call("Activity", "range", score)
		Hud.banner("🎯 " .. score .. " POINTS", Theme.C.orange, ok and ("+" .. Num.short(r.coins) .. " coins") or nil, 2.2)
		if ok then
			reward(r, stand.Position + Vector3.new(0, 4, -10))
		end
		if score >= 100 then
			UI.confetti(60)
		end
	end
	local nh = hum()
	if nh then
		nh.WalkSpeed = savedWS > 0 and savedWS or Config.WALK_SPEED
	end
	camera.CameraType = Enum.CameraType.Custom
	Hud.setMode("normal")
	Activities.busy = nil
end

---------------------------------------------------------------------
-- Полоса препятствий: таймер, монетки, финиш
---------------------------------------------------------------------
local courseCoins: { BasePart } = {}
local finishPad: BasePart? = nil
local startPad: BasePart? = nil
function Activities.course()
	if Activities.busy then
		return
	end
	local root = hrp()
	if not root or not startPad or not finishPad then
		return
	end
	Activities.busy = "course"
	local t0 = os.clock()
	local got = 0
	local quit = false
	local taken: { [BasePart]: boolean } = {}
	local bar, val = activityBar("🏃 OBSTACLE COURSE", Theme.C.green, function()
		quit = true
	end)
	root.CFrame = CFrame.new(startPad.Position + Vector3.new(0, 3.5, 0))
	for _, c in courseCoins do
		c.LocalTransparencyModifier = 0
	end
	Sfx.play("level", 1.4, 0.4)
	Hud.banner("3… 2… 1… GO!", Theme.C.green, "Collect coins and reach the flag", 1.4)
	local finished = false
	local par = Config.ACTIVITY.course.parTime
	while not quit and not finished do
		local t = os.clock() - t0
		val.Text = string.format("⏱ %s   ·   🪙 %d/%d   ·   target: %s", Num.time(t), got, #courseCoins, Num.time(par))
		val.TextColor3 = t <= par and Theme.C.text or Theme.C.orange
		local r = hrp()
		if not r or t > 180 then
			break
		end
		for _, c in courseCoins do
			if not taken[c] and (c.Position - r.Position).Magnitude < 4 then
				taken[c] = true
				got += 1
				c.LocalTransparencyModifier = 1
				Sfx.play("coin")
				Fx.burst(c.Position, { tex = "star", color = Theme.C.gold, n = 10, speed = NumberRange.new(5, 10), size = 0.7, life = 0.6 })
			end
		end
		local fp = finishPad :: BasePart
		local rel = fp.CFrame:PointToObjectSpace(r.Position)
		if math.abs(rel.X) < fp.Size.X / 2 + 1 and math.abs(rel.Z) < fp.Size.Z / 2 + 1 and rel.Y > -1 and rel.Y < 6 then
			finished = true
		end
		task.wait()
	end
	bar:Destroy()
	for _, c in courseCoins do
		c.LocalTransparencyModifier = 0
	end
	if finished then
		local tm = os.clock() - t0
		local ok, r = Backend.call("Activity", "course", { coins = got, time = tm })
		Hud.banner("🏁 FINISHED! " .. Num.time(tm), Theme.C.green, tm < par and "Beat the target time! +100 coins" or ("Coins: " .. got), 2.6)
		UI.confetti(70)
		Sfx.play("win", 1, 0.6)
		if ok then
			reward(r, finishPad.Position)
		end
	elseif not quit then
		UI.toast("Time is up — try again!", "warn")
	end
	Activities.busy = nil
end

-- Батуты: подбрасывают всегда (не только на полосе)
local bounceCd = 0
RunService.Heartbeat:Connect(function()
	local r = hrp()
	local h = hum()
	if not r or not h or os.clock() < bounceCd then
		return
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { player.Character :: Instance }
	local hit = workspace:Raycast(r.Position, Vector3.new(0, -3.6, 0), params)
	local b = hit and hit.Instance:GetAttribute("Bounce")
	if hit and type(b) == "number" and r.AssemblyLinearVelocity.Y <= 1 then
		bounceCd = os.clock() + 0.35
		r.AssemblyLinearVelocity = Vector3.new(r.AssemblyLinearVelocity.X, b, r.AssemblyLinearVelocity.Z)
		h:ChangeState(Enum.HumanoidStateType.Jumping)
		Sfx.play("bounce", 0.9 + math.random() * 0.2, 0.7)
		Fx.ring(hit.Position + Vector3.new(0, 0.2, 0), Theme.C.pink, 5, 0.35)
		local part = hit.Instance :: BasePart
		local s0 = part:GetAttribute("S0") :: Vector3?
		if not s0 then
			s0 = part.Size
			part:SetAttribute("S0", s0)
		end
		local s = s0 :: Vector3
		part.Size = Vector3.new(s.X * 1.08, s.Y * 0.5, s.Z * 1.08)
		Fx.tween(part, 0.4, { Size = s }, Enum.EasingStyle.Elastic)
	end
end)

---------------------------------------------------------------------
-- Смотровая вышка: подъём и облёт всех зон
---------------------------------------------------------------------
function Activities.lookout(model: Instance)
	if Activities.busy then
		return
	end
	local top = model:FindFirstChild("Top") :: BasePart?
	local root = hrp()
	if not top or not root then
		return
	end
	Activities.busy = "lookout"
	root.CFrame = CFrame.lookAt(top.Position + Vector3.new(0, 1, 0), top.Position + Vector3.new(0, 1, -10))
	Hud.setMode("cinematic")
	camera.CameraType = Enum.CameraType.Scriptable
	local shots = {
		{ CFrame.lookAt(top.Position + Vector3.new(0, 4, 4), Vector3.new(0, 0, -20)), 0 },
		{ CFrame.lookAt(Vector3.new(-20, 40, -10), Vector3.new(0, 0, -40)), 1 },
		{ CFrame.lookAt(Vector3.new(10, 50, -50), Vector3.new(0, 0, -100)), 2 },
		{ CFrame.lookAt(Vector3.new(-10, 60, -105), Vector3.new(0, 0, -170)), 3 },
		{ CFrame.lookAt(Vector3.new(0, 80, -160), Vector3.new(0, 0, -240)), 4 },
		{ CFrame.lookAt(Vector3.new(60, 130, 120), Vector3.new(0, 0, -40)), 0 },
	}
	local skip = false
	local sb = UI.button({ Text = "Skip ⏩", TextSize = 22, Color = Theme.C.blue, Size = UDim2.fromOffset(200, 50), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -20, 1, -20), ZIndex = 40 }, function()
		skip = true
	end)
	sb.Parent = UI.top
	for i, s in shots do
		if skip then
			break
		end
		local from = camera.CFrame
		local t0 = os.clock()
		local dur = i == 1 and 1.2 or 2.2
		if s[2] > 0 then
			Hud.zone(s[2])
		end
		while os.clock() - t0 < dur and not skip do
			local k = (os.clock() - t0) / dur
			camera.CFrame = from:Lerp(s[1], k * k * (3 - 2 * k))
			RunService.RenderStepped:Wait()
		end
	end
	sb:Destroy()
	camera.CameraType = Enum.CameraType.Custom
	Hud.setMode("normal")
	local ok, r = Backend.call("Activity", "lookout")
	if ok and r.coins > 0 then
		Hud.banner("🔭 THE WHOLE FOREST IN VIEW", Theme.C.cyan, "+" .. r.coins .. " coins for your first climb", 2.4)
		reward(r, top.Position)
	end
	Activities.busy = nil
end

---------------------------------------------------------------------
-- Светлячки и яйца
---------------------------------------------------------------------
local collectibles: { [string]: { part: BasePart, base: CFrame } } = {}
local function refreshCollected(d: any)
	for id, c in collectibles do
		local got = d and d.collected and d.collected[id]
		c.part.LocalTransparencyModifier = got and 1 or 0
		for _, x in c.part:GetDescendants() do
			if x:IsA("PointLight") or x:IsA("ParticleEmitter") then
				x.Enabled = not got
			end
		end
	end
end
local pending: { [string]: boolean } = {}
RunService.Heartbeat:Connect(function()
	local r = hrp()
	local t = os.clock()
	local d = Backend.data
	for id, c in collectibles do
		local got = d and d.collected and d.collected[id]
		if got then
			continue
		end
		local egg = id:sub(1, 3) == "egg"
		c.part.CFrame = c.base * CFrame.new(0, math.sin(t * 2 + #id) * (egg and 0.15 or 0.5), 0) * CFrame.Angles(0, egg and t * 1.5 or 0, 0)
		if r and not pending[id] and (c.part.Position - r.Position).Magnitude < 4.5 then
			pending[id] = true
			task.spawn(function()
				local ok, res = Backend.call("Collect", id)
				if ok then
					Sfx.play(egg and "level" or "sparkle", egg and 1.3 or 1, 0.6)
					Fx.burst(c.part.Position, { tex = "star", color = egg and Theme.C.pink or Color3.fromRGB(255, 240, 120), n = 16, speed = NumberRange.new(6, 12), size = 0.8, life = 0.8, rot = true })
					UI.toast((egg and "🥚 Egg found! " or "✨ Firefly found! ") .. "+" .. res.coins .. " 💰", egg and "rare" or "gold")
					Hud.flyCoins(UI.worldToScreen(c.part.Position), res.coins)
				end
				pending[id] = nil
			end)
		end
	end
end)

---------------------------------------------------------------------
-- Костёр: музыка рядом, монетки, пока сидишь
---------------------------------------------------------------------
local MELODY = { 0, 4, 7, 12, 7, 4, 2, 5, 9, 5, 2, -1, 0, 4, 7, 4 }
local function campfire(model: Instance)
	local music = model:FindFirstChild("Music") :: BasePart?
	local radius = music and (music:GetAttribute("MusicRadius") :: number?) or 30
	local core = model:FindFirstChild("FireCore") :: BasePart?
	if core then
		local a = Instance.new("Attachment")
		a.Parent = core
		Fx.emitter(a, { tex = "fire", color = Color3.fromRGB(255, 200, 80), color2 = Color3.fromRGB(255, 80, 20), size = 2.2, life = 0.9, rate = 26, speed = NumberRange.new(3, 6), spread = 14, accel = Vector3.new(0, 6, 0) })
		Fx.emitter(a, { tex = "sparks", color = Color3.fromRGB(255, 200, 90), size = 0.25, life = 1.6, rate = 6, speed = NumberRange.new(4, 8), spread = 25, accel = Vector3.new(0, 3, 0) })
	end
	task.spawn(function()
		local i = 0
		local seated = 0
		while true do
			task.wait(0.42)
			local r = hrp()
			local h = hum()
			if not r or not music then
				continue
			end
			local d = (r.Position - music.Position).Magnitude
			if d < radius then
				i = i % #MELODY + 1
				local vol = 0.22 * (1 - d / radius)
				Sfx.note(MELODY[i] - 5, vol, "ping")
				if i % 4 == 1 then
					Sfx.note(MELODY[i] - 17, vol * 0.8, "tick")
				end
			end
			local seat = h and h.SeatPart
			if seat and seat:IsDescendantOf(model) then
				seated += 0.42
				if seated >= 60 then
					seated = 0
					local ok, res = Backend.call("Activity", "campfire")
					if ok then
						UI.toast("🔥 Cozy by the campfire: +" .. res.coins .. " 💰", "gold")
					end
				end
			else
				seated = 0
			end
		end
	end)
end

---------------------------------------------------------------------
function Activities.init()
	for _, d in map:GetDescendants() do
		if d:IsA("BasePart") then
			local cid = d:GetAttribute("Collectible")
			if type(cid) == "string" then
				collectibles[cid] = { part = d, base = d.CFrame }
			elseif d:GetAttribute("CourseCoin") then
				table.insert(courseCoins, d)
			elseif d:GetAttribute("Finish") then
				finishPad = d
			elseif d.Name == "StartPad" then
				startPad = d
			end
		end
	end
	local cf = map:FindFirstChild("Campfire")
	if cf then
		campfire(cf)
	end
	Backend.onChange(refreshCollected)
	-- монетки полосы крутятся
	RunService.RenderStepped:Connect(function()
		local t = os.clock()
		for _, c in courseCoins do
			local b = c:GetAttribute("B0") :: CFrame?
			if not b then
				c:SetAttribute("B0", c.CFrame)
				b = c.CFrame
			end
			c.CFrame = (b :: CFrame) * CFrame.Angles(0, t * 3, 0)
		end
	end)
end

return Activities
