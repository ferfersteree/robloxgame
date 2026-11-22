-- StarterPlayerScripts/Client/TrainCtl.luau
-- V82: тренировка с гантелями. На экране только шкала очков, кнопка Exit и Сила (чип HUD).
-- Подъёмы идут сами (авто) и по клику/Пробелу; очки копятся в шкалу, полная шкала даёт Силу.
-- Раз в 5-8 с появляется подсказка (круг или стрелка): успех даёт ×2 к очкам на 1 с (проверяет Backend "TrainBuff").
-- Вне тренировки у своего стенда показывается кнопка улучшения гантелей.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Config = require(RS.Shared.Config)
local PoseData = require(RS.Shared.PoseData)
local Num = require(RS.Shared.Num)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Fx = require(script.Parent.WorldFx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Animator = require(script.Parent.Animator)
local Activities = require(script.Parent.Activities)

local TrainCtl = {}
TrainCtl.active = false

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera
local C = Theme.C

local alive = false
local cooling = false
local coolT0 = 0
local auto = true -- авто-подъёмы всегда включены, клик/Пробел добавляют ручной подъём
local cycleDuration = PoseData.trainingCycle
local peakOffset = PoseData.trainingPeak
local nextAutoPeak = 0
local session = 0
local effortT0 = -math.huge
local total = 0
local camFrom, camTo, camT0 = CFrame.new(), CFrame.new(), 0

local BAR_W = UI.mobile and 460 or 640
local BAR_H = UI.mobile and 44 or 56
local BUFF_SHOW = 1.6 -- сколько висит подсказка
local GOLD = Color3.fromRGB(255, 214, 70)

-- элементы экрана тренировки
local barHolder: Frame? = nil
local barClip: Frame? = nil
local barLabel: TextLabel? = nil
local barGlow: Frame? = nil
local barIW, barIH = 0, 0
local promptGui: CanvasGroup? = nil
local curPrompt: { kind: string, hit: () -> () }? = nil

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

---------------------------------------------------------------------
-- Шкала
---------------------------------------------------------------------
local barLevel = 1 -- V86: уровень Силы, подпись шкалы
local function setBar(cur: number, bar: number, anim: boolean?)
	local clip, lbl = barClip, barLabel
	if not clip or not lbl then
		return
	end
	local dl = Backend.data -- V86: уровень всегда из данных (уровни приходят и из пропуска, и из демо-панели)
	barLevel = dl and tonumber(dl.strLvl) or barLevel
	local k = if bar > 0 then math.clamp(cur / bar, 0, 1) else 0
	local target = UDim2.fromOffset(math.floor(barIW * k), barIH)
	if anim then
		UI.tween(clip, 0.2, { Size = target }, Enum.EasingStyle.Quad)
	else
		clip.Size = target
	end
	clip.Visible = k > 0.001
	lbl.Text = "Lv " .. tostring(barLevel) .. "  ·  " .. Num.short(math.floor(cur)) .. " / " .. Num.short(bar)
end

local function syncBar(anim: boolean?)
	local d = Backend.data
	if d then
		-- V86: шкала уровня Силы, не гантелей
		local lvl = tonumber(d.strLvl) or 1
		barLevel = lvl
		setBar(tonumber(d.strXp) or 0, Config.strengthXp(lvl), anim)
	end
end

local function buildBar(): Frame
	local holder = Instance.new("Frame")
	holder.Name = "TrainBar"
	holder.BackgroundTransparency = 1
	holder.Size = UDim2.fromOffset(BAR_W, BAR_H)
	holder.AnchorPoint = Vector2.new(0.5, 1)
	holder.Position = UDim2.new(0.5, 0, 1, -34)
	holder.ZIndex = 40
	holder.Parent = UI.root
	-- золотое свечение под шкалой (бафф ×2)
	local glow = Instance.new("Frame")
	glow.Name = "Glow"
	glow.BackgroundColor3 = GOLD
	glow.BackgroundTransparency = 1
	glow.BorderSizePixel = 0
	glow.AnchorPoint = Vector2.new(0.5, 0.5)
	glow.Position = UDim2.fromScale(0.5, 0.5)
	glow.Size = UDim2.new(1, 26, 1, 20)
	glow.ZIndex = 39
	UI.corner(0.5, true).Parent = glow
	glow.Parent = holder
	barGlow = glow
	local track = UI.art("xp_track", { Name = "Track", Size = UDim2.fromScale(1, 1), Slice = { 22, 0, 22, 0 }, SliceScale = BAR_H / 48, ZIndex = 41, Parent = holder })
	local ix, iy = math.max(3, math.floor(BAR_H * 0.14)), math.max(3, math.floor(BAR_H * 0.16))
	barIW, barIH = BAR_W - 2 * ix, BAR_H - 2 * iy
	local clip = Instance.new("Frame")
	clip.Name = "Clip"
	clip.BackgroundTransparency = 1
	clip.BorderSizePixel = 0
	clip.ClipsDescendants = true
	clip.Position = UDim2.fromOffset(ix, iy)
	clip.Size = UDim2.fromOffset(0, barIH)
	clip.ZIndex = 42
	clip.Visible = false
	clip.Parent = track
	UI.art("xp_fill", { Name = "Fill", Size = UDim2.fromOffset(barIW, barIH), Slice = { 22, 0, 22, 0 }, SliceScale = barIH / 48, ZIndex = 42, Parent = clip })
	barClip = clip
	barLabel = UI.label({ Text = "", TextSize = UI.mobile and 22 or 28, Size = UDim2.fromScale(1, 1), ZIndex = 44, Stroke = 3, Parent = track })
	return holder
end

-- шкала заполнилась: вспышка, всплывающая Сила, звук
local function celebrate(res: any)
	local holder = barHolder
	if not holder then
		return
	end
	local bar = tonumber(res.bar) or 1
	setBar(bar, bar, true)
	UI.punch(holder, 0.08)
	Sfx.play("level", 1, 0.5)
	UI.confetti(Fx.lowFx and 10 or 26, { GOLD, C.green, C.orange })
	local f = UI.label({ Text = "+" .. Num.short(math.floor((tonumber(res.power) or 0) + 0.5)) .. " Strength · Lv " .. tostring(barLevel), TextSize = UI.mobile and 34 or 44, Color = GOLD, Size = UDim2.fromOffset(420, 54), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 0, -8), ZIndex = 50, Stroke = 3, Parent = holder })
	local sc = Instance.new("UIScale")
	sc.Scale = 0.4
	sc.Parent = f
	UI.tween(sc, 0.25, { Scale = 1 }, Enum.EasingStyle.Back)
	UI.tween(f, 1.2, { Position = UDim2.new(0.5, 0, 0, -80) }, Enum.EasingStyle.Quad)
	task.delay(0.8, function()
		UI.tween(f, 0.4, { TextTransparency = 1 })
		local st = f:FindFirstChildOfClass("UIStroke")
		if st then
			UI.tween(st, 0.4, { Transparency = 1 })
		end
	end)
	task.delay(1.3, function()
		f:Destroy()
	end)
	local cur = tonumber(res.cur) or 0
	task.delay(0.3, function()
		if alive and barClip then
			setBar(cur, bar, false)
		end
	end)
end

local function glowBuff()
	local g, holder = barGlow, barHolder
	if not g or not holder then
		return
	end
	g.BackgroundTransparency = 0.35
	UI.tween(g, 1, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad)
	UI.punch(holder, 0.06)
	Sfx.play("sparkle", 1.2, 0.5)
	local p = UI.screenPos(holder)
	UI.pop("x2!", GOLD, p - Vector2.new(0, 70), 56)
end

---------------------------------------------------------------------
-- Подъём
---------------------------------------------------------------------
local function awardRep(repSession: number)
	if not alive or session ~= repSession then return end
	local ok, res = Backend.call("Rep")
	if ok and alive and session == repSession and type(res) == "table" then
		total += tonumber(res.power) or 0
		effortT0 = os.clock()
		Sfx.play("rep", 0.95 + math.random() * 0.1, 0.35)
		if (tonumber(res.fills) or 0) > 0 then
			celebrate(res)
		else
			setBar(tonumber(res.cur) or 0, tonumber(res.bar) or 1, true)
		end
		local d = Backend.data
		if d and d.tutorial == 5 then Backend.call("Tutorial", 6) end
	end
end

local function rep()
	-- ручной подъём заменяет авто-удар этого цикла: чаще авто-ритма очки не набрать
	if not alive or cooling then return end
	local repSession = session
	cooling = true
	coolT0 = os.clock()
	Animator.play("Lift")
	task.wait(peakOffset)
	awardRep(repSession)
	local left = cycleDuration - (os.clock() - coolT0)
	if left > 0 and alive and session == repSession then task.wait(left) end
	if session == repSession then
		cooling = false
		if alive then
			Animator.play("Train")
			nextAutoPeak = os.clock() + peakOffset
		end
	end
end

RunService.RenderStepped:Connect(function()
	if not alive then
		return
	end
	local t = os.clock()
	local u = smooth((t - camT0) / 0.7)
	-- короткий лёгкий импульс на каждом подъёме
	local effort = math.max(0, 1 - (t - effortT0) / 0.16)
	local amount = (Fx.lowFx and 0.006 or 0.014) * effort
	camera.CFrame = camFrom:Lerp(camTo, u)
		* CFrame.new(math.sin(t * 57) * amount, math.cos(t * 63) * amount * 0.7, 0)
		* CFrame.Angles(math.sin(t * 0.6) * 0.002, math.sin(t * 0.4) * 0.003, math.sin(t * 53) * amount * 0.025)
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
		local p = curPrompt
		if p and p.kind == "circle" then
			p.hit() -- Пробел попадает по кругу вместо подъёма
			return
		end
		task.spawn(rep)
	elseif i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch then
		task.spawn(rep)
	end
end)

---------------------------------------------------------------------
-- Подсказка на ×2: круг (нажать) или стрелка (протянуть)
---------------------------------------------------------------------
local function charScreenPos(): Vector2
	local vp = camera.ViewportSize
	local c = player.Character
	local head = c and c:FindFirstChild("Head") :: BasePart?
	if head then
		local p, on = UI.worldToScreen(head.Position)
		if on then
			return p
		end
	end
	return vp / 2
end

local function runPrompt(kind: string, mySession: number)
	local vp = camera.ViewportSize
	local origin = charScreenPos()
	local side = math.random() < 0.5 and -1 or 1
	local pos = origin + Vector2.new(side * (170 + math.random() * 90), -90 + math.random() * 150)
	local dir = Vector2.new(1, 0)
	if kind == "arrow" then
		local a = math.rad(math.random(0, 7) * 45)
		dir = Vector2.new(math.cos(a), math.sin(a))
		local e = pos + dir * 160
		-- конец стрелки не должен уходить за экран
		if e.X < 80 or e.X > vp.X - 80 then dir = Vector2.new(-dir.X, dir.Y) end
		if e.Y < 120 or e.Y > vp.Y - 200 then dir = Vector2.new(dir.X, -dir.Y) end
	end
	pos = Vector2.new(math.clamp(pos.X, 150, math.max(151, vp.X - 150)), math.clamp(pos.Y, 190, math.max(191, vp.Y - 260)))

	local g = Instance.new("CanvasGroup")
	g.Name = "TrainPrompt"
	g.BackgroundTransparency = 1
	g.Size = UDim2.fromScale(1, 1)
	g.ZIndex = 65
	g.Parent = UI.top
	promptGui = g
	local done, hitFlag = false, false
	local function hit()
		if not done then
			done = true
			hitFlag = true
		end
	end
	curPrompt = { kind = if kind == "circle" then "circle" else "arrow", hit = hit }
	local conns: { RBXScriptConnection } = {}
	local at = UI.toCanvas(pos)
	local ring: Frame? = nil
	local arrow: ImageLabel? = nil
	local dragInput: InputObject? = nil
	local dragStart = Vector2.zero

	if kind == "circle" then
		local r = Instance.new("Frame")
		r.Name = "Ring"
		r.BackgroundTransparency = 1
		r.AnchorPoint = Vector2.new(0.5, 0.5)
		r.Position = at
		r.Size = UDim2.fromOffset(260, 260)
		r.ZIndex = 66
		UI.corner(0.5, true).Parent = r
		UI.stroke(GOLD, 6, 0, true).Parent = r
		r.Parent = g
		ring = r
		UI.tween(r, BUFF_SHOW, { Size = UDim2.fromOffset(128, 128) }, Enum.EasingStyle.Linear)
		local b = UI.artButton("badge", { Name = "Target", Size = UDim2.fromOffset(112, 112), AnchorPoint = Vector2.new(0.5, 0.5), Position = at, Color = GOLD, ZIndex = 68, Parent = g }, hit)
		b.Active = true
		UI.label({ Text = UI.mobile and "TAP!" or "CLICK / SPACE", TextSize = 24, Color = GOLD, Size = UDim2.fromOffset(240, 30), AnchorPoint = Vector2.new(0.5, 0), Position = at + UDim2.fromOffset(0, 70), ZIndex = 69, Stroke = 3, Parent = g })
	else
		local b = UI.artButton("badge", { Name = "Base", Size = UDim2.fromOffset(84, 84), AnchorPoint = Vector2.new(0.5, 0.5), Position = at, Color = GOLD, ZIndex = 68, Parent = g })
		local aw = UI.artSize("arrow_r")
		local ah = aw.X > 0 and 120 * aw.Y / aw.X or 92
		arrow = UI.art("arrow_r", { Name = "Arrow", Size = UDim2.fromOffset(120, ah), AnchorPoint = Vector2.new(0.5, 0.5), Position = at + UDim2.fromOffset(dir.X * 110, dir.Y * 110), Rotation = math.deg(math.atan2(dir.Y, dir.X)), Color = GOLD, ZIndex = 69, Parent = g })
		UI.label({ Text = "SWIPE!", TextSize = 24, Color = GOLD, Size = UDim2.fromOffset(200, 30), AnchorPoint = Vector2.new(0.5, 0), Position = at + UDim2.fromOffset(0, 58), ZIndex = 69, Stroke = 3, Parent = g })
		table.insert(conns, b.InputBegan:Connect(function(i)
			if i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch then
				dragInput = i
				dragStart = if i.UserInputType == Enum.UserInputType.Touch then Vector2.new(i.Position.X, i.Position.Y) else UserInputService:GetMouseLocation()
			end
		end))
		table.insert(conns, UserInputService.InputEnded:Connect(function(i)
			if i == dragInput or i.UserInputType == Enum.UserInputType.MouseButton1 then
				dragInput = nil
			end
		end))
	end

	local t0 = os.clock()
	while alive and session == mySession and not done and os.clock() - t0 < BUFF_SHOW do
		local di = dragInput
		if di then
			local cur = if di.UserInputType == Enum.UserInputType.Touch then Vector2.new(di.Position.X, di.Position.Y) else UserInputService:GetMouseLocation()
			local delta = cur - dragStart
			-- протянуть от основания не меньше 120 px, в пределах 35° от стрелки
			if delta.Magnitude >= 120 and delta.Unit:Dot(dir) >= math.cos(math.rad(35)) then
				hit()
			end
		end
		local ar = arrow
		if ar then
			local k = 100 + 26 * math.sin((os.clock() - t0) * 9)
			ar.Position = at + UDim2.fromOffset(dir.X * k, dir.Y * k)
		end
		task.wait()
	end
	curPrompt = nil
	for _, c in conns do
		c:Disconnect()
	end
	if ring then
		ring:Destroy()
	end
	if hitFlag and alive and session == mySession then
		Sfx.play("coin", 1.1, 0.5)
		UI.tween(g, 0.2, { GroupTransparency = 1 })
		task.spawn(function()
			local ok = Backend.call("TrainBuff")
			if ok and alive and session == mySession then
				glowBuff()
			end
		end)
	else
		UI.tween(g, 0.25, { GroupTransparency = 1 })
	end
	task.delay(0.3, function()
		g:Destroy()
	end)
	if promptGui == g then
		promptGui = nil
	end
end

---------------------------------------------------------------------
-- Вход / выход
---------------------------------------------------------------------
function TrainCtl.open(plot: Instance)
	if TrainCtl.active or Activities.busy then
		return
	end
	local gym = plot:FindFirstChild("Gym")
	local stand = gym and gym:FindFirstChild("Stand") :: BasePart?
	local root, h = hrp(), hum()
	if not stand or not root or not h or h.Health <= 0 or not Backend.data then
		return
	end
	TrainCtl.active = true
	Activities.busy = "train"
	alive = true
	session += 1
	auto = true
	cooling = false
	effortT0 = -math.huge
	total = 0
	curPrompt = nil
	Hud.setMode("busy")
	Hud.setTraining(true)
	-- лицом от хижины (во двор), камера спереди-сбоку
	local found = plot:FindFirstChild("Foundation") :: BasePart?
	local f = found and found.CFrame.LookVector or Vector3.new(0, 0, -1)
	local fwd = Vector3.new(f.X, 0, f.Z).Unit
	local y = stand.Position.Y + stand.Size.Y / 2 + h.HipHeight + root.Size.Y / 2
	local pos = Vector3.new(stand.Position.X, y, stand.Position.Z)
	local unlock = Activities.lockAt(CFrame.lookAt(pos, pos + fwd))
	Animator.play("Train")
	nextAutoPeak = os.clock() + peakOffset
	local savedFov = camera.FieldOfView
	camera.CameraType = Enum.CameraType.Scriptable
	camera.FieldOfView = 60
	local right = fwd:Cross(Vector3.yAxis)
	local focus = pos + Vector3.new(0, 0.4, 0)
	camFrom = camera.CFrame
	camTo = CFrame.lookAt(focus + fwd * 10 + right * 3 + Vector3.new(0, 1.8, 0), focus - right * 2.4)
	camT0 = os.clock()
	Sfx.play("open")
	local holder = buildBar()
	barHolder = holder
	syncBar(false)
	local exitBtn = UI.artButton("btn_red", { Name = "TrainExit", Text = "Exit", TextSize = 26, Size = UDim2.fromOffset(150, 41), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 20, 1, -24), ZIndex = 45, Parent = UI.root }, function()
		alive = false
	end)
	local diedConn = h.Died:Connect(function()
		alive = false
	end)
	local nextBuffAt = os.clock() + 3.5
	local promptBusy = false
	local promptKind = math.random(1, 2)
	while alive do
		local now = os.clock()
		if auto and now >= nextAutoPeak then
			-- пропущенные удары при тормозах не догоняем пачкой
			repeat nextAutoPeak += cycleDuration until nextAutoPeak > now
			if not cooling then
				cooling = true
				coolT0 = now - peakOffset
				local repSession = session
				task.spawn(function()
					awardRep(repSession)
					-- V83: пауза до конца цикла, иначе клик сразу после авто-подъёма давал лишний подъём
					local left = cycleDuration - peakOffset - (os.clock() - now)
					if left > 0 and alive and session == repSession then
						task.wait(left)
					end
					if session == repSession then
						cooling = false
					end
				end)
			end
		end
		if not promptBusy and now >= nextBuffAt then
			promptBusy = true
			local kind = if promptKind == 1 then "circle" else "arrow"
			promptKind = 3 - promptKind
			local mySession = session
			task.spawn(function()
				pcall(runPrompt, kind, mySession)
				curPrompt = nil
				nextBuffAt = os.clock() + 5 + math.random() * 3
				promptBusy = false
			end)
		end
		task.wait()
	end
	-- выход
	diedConn:Disconnect()
	while cooling do
		task.wait()
	end
	local waited = 0
	while promptBusy and waited < 2 do
		waited += task.wait()
	end
	local pg = promptGui
	if pg then
		pg:Destroy()
	end
	promptGui, curPrompt = nil, nil
	holder:Destroy()
	exitBtn:Destroy()
	barHolder, barClip, barLabel, barGlow = nil, nil, nil, nil
	auto = false
	session += 1
	unlock()
	Animator.stop()
	camera.CameraType = Enum.CameraType.Custom
	camera.FieldOfView = savedFov
	Hud.setTraining(false)
	Hud.setMode("normal")
	Activities.busy = nil
	TrainCtl.active = false
	if total > 0 then
		UI.toast("+" .. Num.short(math.floor(total + 0.5)) .. " strength this session", "good")
	end
end

---------------------------------------------------------------------
-- Кнопка улучшения у своего стенда (вне тренировки)
---------------------------------------------------------------------
local UP_RANGE = 10
local upBtn: ImageButton? = nil
local upContent: Frame? = nil
local upKey = ""
local upBusy = false

local function ownStand(): BasePart?
	local map = workspace:FindFirstChild("Map")
	local plots = map and map:FindFirstChild("Plots")
	if not plots then
		return nil
	end
	for _, p in plots:GetChildren() do
		if p:GetAttribute("OwnerId") == player.UserId then
			local gym = p:FindFirstChild("Gym")
			local st = gym and gym:FindFirstChild("Stand")
			if st and st:IsA("BasePart") then
				return st
			end
			return nil
		end
	end
	return nil
end

local function upgrade()
	if upBusy then
		return
	end
	upBusy = true
	local ok, res = Backend.call("UpgradeDumbbell")
	upBusy = false
	if not ok then
		Sfx.play("error")
		UI.toast(tostring(res or "Not enough coins"), "warn")
		return
	end
	local d = Backend.data
	local lvl = tonumber(res) or (d and d.dumbbell) or 1
	local info = Config.DUMBBELL[lvl]
	local look = Config.DUMBBELL_LOOK[lvl]
	if not info then
		return
	end
	Sfx.play("level")
	UI.confetti(50, { look and look.color or C.gold, C.gold, C.green })
	Hud.banner("NEW DUMBBELLS!", C.green, info.name .. " · +" .. Num.short(info.gain) .. " XP per rep", 2.2)
	upKey = "" -- перерисовать кнопку; вид стенда и гантелей в руках обновит Equip (Main.sendLook)
end

local function renderUpgrade(d: any)
	local btn = upBtn
	if not btn then
		return
	end
	local lvl = d.dumbbell
	local nxt = Config.DUMBBELL[lvl + 1]
	local can = nxt ~= nil and d.coins >= nxt.cost
	local key = lvl .. ":" .. tostring(can)
	if key == upKey then
		return
	end
	upKey = key
	if upContent then
		upContent:Destroy()
	end
	local content = Instance.new("Frame")
	content.Name = "Content"
	content.BackgroundTransparency = 1
	content.Size = UDim2.fromScale(1, 1)
	content.ZIndex = 52
	content.Parent = btn
	upContent = content
	UI.label({ Text = if nxt then "Upgrade Dumbbells" else "Dumbbells", TextSize = 24, Scaled = true, MaxSize = 26, Size = UDim2.new(1, -40, 0.42, 0), Position = UDim2.fromScale(0.5, 0.07), AnchorPoint = Vector2.new(0.5, 0), ZIndex = 53, Stroke = 3, Parent = content })
	local row = Instance.new("Frame")
	row.BackgroundTransparency = 1
	row.Size = UDim2.fromScale(1, 0.4)
	row.Position = UDim2.fromScale(0, 0.5)
	row.ZIndex = 53
	row.Parent = content
	UI.list(Enum.FillDirection.Horizontal, 6, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = row
	if nxt then
		UI.art("ic_coin", { Fit = true, Size = UDim2.fromOffset(26, 26), LayoutOrder = 1, ZIndex = 54, Parent = row })
		UI.label({ Text = Num.short(nxt.cost), TextSize = 22, Size = UDim2.fromOffset(10, 28), AutoX = true, LayoutOrder = 2, ZIndex = 54, Stroke = 2, Parent = row })
		UI.label({ Text = "Next: " .. nxt.name, TextSize = 20, Color = C.gold, Size = UDim2.fromOffset(10, 28), AutoX = true, LayoutOrder = 3, ZIndex = 54, Stroke = 2, Parent = row })
	else
		UI.label({ Text = "MAX", TextSize = 24, Color = C.gold, Size = UDim2.fromOffset(80, 28), ZIndex = 54, Stroke = 2, Parent = row })
	end
	UI.setEnabled(btn, can)
end

local function updateUpgradeButton()
	local d = Backend.data
	local show = false
	if d and Hud.mode == "normal" and not TrainCtl.active and Activities.busy == nil and not UI.windowOpen() and Config.DUMBBELL[d.dumbbell] then
		local root = hrp()
		local st = ownStand()
		if root and st then
			local dv = st.Position - root.Position
			show = Vector3.new(dv.X, 0, dv.Z).Magnitude <= UP_RANGE
		end
	end
	if show and not upBtn then
		upBtn = UI.artButton("btn_orange", { Name = "UpgradeDumbbells", Size = UDim2.fromOffset(340, 94), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -110), ZIndex = 50, Parent = UI.root }, upgrade)
		upKey = ""
	end
	local btn = upBtn
	if btn then
		btn.Visible = show
		if show and d then
			renderUpgrade(d)
		end
	end
end

task.spawn(function()
	while true do
		task.wait(0.2)
		local ok, err = pcall(updateUpgradeButton)
		if not ok then
			warn("[TrainCtl] upgrade button: " .. tostring(err))
		end
	end
end)

return TrainCtl
