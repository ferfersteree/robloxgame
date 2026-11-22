-- StarterPlayerScripts/Client/TrainCtl.luau
-- Continuous dumbbell curls at the player's own training station.
-- One reward per completed peak; pausing keeps the dumbbells and permits single reps.
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
local auto = false
local cycleDuration = PoseData.trainingCycle
local peakOffset = PoseData.trainingPeak
local nextAutoPeak = 0
local session = 0
local effortT0 = -math.huge
local spaceHeld = false
local combo = 0
local lastRep = 0
local total = 0
local camFrom, camTo, camT0 = CFrame.new(), CFrame.new(), 0
local panel: Frame? = nil
local panelKey = ""
local val: TextLabel? = nil
local cool: Frame? = nil
local comboLbl: TextLabel? = nil

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

local function updateVal()
	local d = Backend.data
	if val and d then
		local g = Config.DUMBBELL[d.dumbbell].gain
		val.Text = string.format("Strength: %s  ·  +%s per rep%s", Num.short(d.power), Num.short(g), total > 0 and ("  ·  session +" .. Num.short(total)) or "")
	end
end

local function dumbbellModel(level: number): Model?
	local assets = RS:FindFirstChild("Assets")
	local tpl = assets and assets:FindFirstChild("Dumbbell")
	if not tpl or not tpl:IsA("Model") then
		return nil
	end
	local m = tpl:Clone()
	local look = Config.DUMBBELL_LOOK[math.clamp(level, 1, #Config.DUMBBELL_LOOK)]
	for _, p in m:GetDescendants() do
		if p:IsA("BasePart") and p:GetAttribute("Weight") then
			p.Color = look.color
			p.Material = look.material
		end
	end
	return m
end

---------------------------------------------------------------------
-- Улучшение гантелей
---------------------------------------------------------------------
local function upgrade()
	local ok, res = Backend.call("UpgradeDumbbell")
	if not ok then
		Sfx.play("error")
		UI.toast(tostring(res or "Not enough coins"), "warn")
		return
	end
	local lvl = tonumber(res) or Backend.data.dumbbell
	local info = Config.DUMBBELL[lvl]
	Sfx.play("level")
	UI.confetti(50, { Config.DUMBBELL_LOOK[lvl].color, C.gold, C.green })
	Hud.banner("NEW DUMBBELLS!", C.green, info.name .. " · +" .. Num.short(info.gain) .. " 💪 per rep", 2.2)
	-- Refresh the equipped weight after an upgrade, then restart a whole cycle.
	local upgradeSession = session
	task.delay(0.4, function()
		if alive and session == upgradeSession then
			Animator.play(nil)
			task.wait(0.1)
			if alive and session == upgradeSession then
				Animator.play(auto and "Train" or "TrainRest")
				nextAutoPeak = os.clock() + peakOffset
			end
		end
	end)
end

local function renderPanel(force: boolean?)
	local p = panel
	local d = Backend.data
	if not p or not d then
		return
	end
	local lvl = d.dumbbell
	local nxt = Config.DUMBBELL[lvl + 1]
	local can = nxt ~= nil and d.coins >= nxt.cost
	local key = lvl .. ":" .. tostring(can)
	if key == panelKey and not force then
		return
	end
	panelKey = key
	for _, c in p:GetChildren() do
		if c:IsA("GuiObject") then
			c:Destroy()
		end
	end
	local info = Config.DUMBBELL[lvl]
	local look = Config.DUMBBELL_LOOK[lvl]
	UI.label({ Text = "🏋️ Dumbbells", TextSize = 28, Size = UDim2.new(1, 0, 0, 34), Position = UDim2.fromOffset(0, 10), ZIndex = 32, Parent = p })
	local vh = Instance.new("Frame")
	vh.BackgroundTransparency = 1
	vh.Size = UDim2.new(1, -20, 0, 130)
	vh.Position = UDim2.fromOffset(10, 46)
	vh.ZIndex = 32
	vh.Parent = p
	local m = dumbbellModel(lvl)
	if m then
		local vp = UI.viewport(m, { ZIndex = 32 }, math.rad(30), 0.8)
		vp.Parent = vh
		m:Destroy()
	end
	UI.label({ Text = info.name, TextSize = 26, Color = look.color, Size = UDim2.new(1, 0, 0, 30), Position = UDim2.fromOffset(0, 180), ZIndex = 32, Parent = p })
	UI.label({ Text = "+" .. Num.short(info.gain) .. " 💪 per rep", TextSize = 22, Color = C.green, Size = UDim2.new(1, 0, 0, 26), Position = UDim2.fromOffset(0, 210), ZIndex = 32, Parent = p })
	local row = Instance.new("Frame")
	row.BackgroundTransparency = 1
	row.Size = UDim2.new(1, 0, 0, 24)
	row.Position = UDim2.fromOffset(0, 244)
	row.ZIndex = 32
	row.Parent = p
	UI.list(Enum.FillDirection.Horizontal, 8, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = row
	for i = 1, #Config.DUMBBELL do
		local dot = Instance.new("Frame")
		dot.Size = UDim2.fromOffset(22, 22)
		dot.BackgroundColor3 = i <= lvl and Config.DUMBBELL_LOOK[i].color or Color3.fromRGB(40, 44, 66)
		dot.LayoutOrder = i
		dot.ZIndex = 33
		UI.corner(0.5, true).Parent = dot
		UI.stroke(i == lvl and Color3.new(1, 1, 1) or Color3.new(0, 0, 0), i == lvl and 3 or 2, 0, true).Parent = dot
		dot.Parent = row
	end
	if nxt then
		UI.label({ Text = "Next: " .. nxt.name .. " · +" .. Num.short(nxt.gain), TextSize = 20, Color = C.dim, Size = UDim2.new(1, -20, 0, 26), Position = UDim2.fromOffset(10, 278), ZIndex = 32, Parent = p })
		local b = UI.button({ Text = "Upgrade · " .. Num.short(nxt.cost) .. " 💰", TextSize = 24, Color = C.orange, Size = UDim2.fromOffset(300, 64), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 314), ZIndex = 33, Parent = p, Shine = can }, upgrade)
		UI.setEnabled(b, can)
	else
		UI.label({ Text = "The best dumbbells in camp! 🏆", TextSize = 22, Color = C.gold, Size = UDim2.new(1, -20, 0, 60), Position = UDim2.fromOffset(10, 290), ZIndex = 32, Wrap = true, Parent = p })
	end
end

Backend.onChange(function()
	if alive then
		renderPanel()
		updateVal()
	end
end)

---------------------------------------------------------------------
-- Подъём
---------------------------------------------------------------------
local function awardRep(repSession: number)
	if not alive or session ~= repSession then return end
	local ok, gain = Backend.call("Rep")
	if ok and alive and session == repSession then
		total += gain
		combo = (os.clock() - lastRep < cycleDuration + 0.9) and combo + 1 or 1
		lastRep = os.clock()
		effortT0 = lastRep
		local c = player.Character
		local head = c and c:FindFirstChild("Head") :: BasePart?
		local at = head and head.Position or camera.Focus.Position
		local k = math.min(combo, 15)
		UI.popAt(at + Vector3.new((math.random() - 0.5) * 1.2, 1.4, 0), "+" .. Num.short(gain) .. " 💪", C.green, 28 + math.min(k, 5))
		Sfx.play("rep", 0.9 + k * 0.03, 0.35)
		local cl = comboLbl
		if cl then
			cl.Visible = combo >= 3
			cl.Text = "COMBO ×" .. combo
			if combo >= 3 then UI.punch(cl, 0.12) end
		end
		if combo % 10 == 0 then
			Sfx.rise(math.min(8, combo // 10 + 2), 0.35)
			Fx.burst(at + Vector3.new(0, 1, 0), { tex = "star", color = C.gold, n = Fx.lowFx and 4 or 8, speed = NumberRange.new(3, 7), size = 0.4, life = 0.6, rot = true })
		end
		local d = Backend.data
		if d and d.tutorial == 5 then Backend.call("Tutorial", 6) end
		updateVal()
	end
end

local function rep()
	-- Auto mode owns the rhythm, so extra taps cannot duplicate its reward.
	if not alive or cooling or auto then return end
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
			Animator.play(auto and "Train" or "TrainRest")
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
	-- A brief, subtle effort pulse at each completed lift, rather than a constant shake.
	local effort = math.max(0, 1 - (t - effortT0) / 0.16)
	local amount = (Fx.lowFx and 0.006 or 0.014) * effort
	camera.CFrame = camFrom:Lerp(camTo, u)
		* CFrame.new(math.sin(t * 57) * amount, math.cos(t * 63) * amount * 0.7, 0)
		* CFrame.Angles(math.sin(t * 0.6) * 0.002, math.sin(t * 0.4) * 0.003, math.sin(t * 53) * amount * 0.025)
	local cf = cool
	if cf then
		local k = if auto then math.clamp((nextAutoPeak - t) / cycleDuration, 0, 1)
			else (cooling and math.clamp(1 - (t - coolT0) / cycleDuration, 0, 1) or 0)
		cf.Size = UDim2.fromScale(1, k)
		cf.Visible = k > 0.01
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
		spaceHeld = true
		task.spawn(rep)
	elseif i.UserInputType == Enum.UserInputType.MouseButton1 or i.UserInputType == Enum.UserInputType.Touch then
		task.spawn(rep)
	end
end)
UserInputService.InputEnded:Connect(function(i)
	if i.KeyCode == Enum.KeyCode.Space then
		spaceHeld = false
	end
end)

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
	spaceHeld = false
	combo = 0
	total = 0
	Hud.setMode("busy")
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
	local bar, v = Activities.bar("💪 TRAINING", C.green, function()
		alive = false
	end)
	val = v
	updateVal()
	-- кнопка подъёма с заливкой перезарядки
	local lift = UI.button({ Text = "LIFT", Icon = "💪", TextSize = 36, Color = C.green, Size = UDim2.fromOffset(320, 110), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -30), ZIndex = 40, Parent = UI.root, Burst = false }, rep)
	local btn = lift:FindFirstChild("Btn") :: TextButton
	local cf = Instance.new("Frame")
	cf.Name = "Cool"
	cf.BackgroundColor3 = Color3.new(0, 0, 0)
	cf.BackgroundTransparency = 0.55
	cf.BorderSizePixel = 0
	cf.AnchorPoint = Vector2.new(0, 1)
	cf.Position = UDim2.fromScale(0, 1)
	cf.Size = UDim2.fromScale(1, 0)
	cf.ZIndex = btn.ZIndex + 1
	UI.corner(14).Parent = cf
	cf.Parent = btn
	cool = cf
	local autoBtn: Frame
	autoBtn = UI.button({ Text = "Auto: ON", Icon = "🔁", TextSize = 22, Color = C.green, Size = UDim2.fromOffset(200, 64), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0.5, 180, 1, -52), ZIndex = 40, Parent = UI.root }, function()
		auto = not auto
		if not cooling then Animator.play(auto and "Train" or "TrainRest") end
		nextAutoPeak = os.clock() + peakOffset
		UI.setText(autoBtn, auto and "Auto: ON" or "Auto: OFF")
		UI.setColor(autoBtn, auto and C.green or C.gray)
	end)
	local cl = UI.label({ Text = "", TextSize = 40, Color = C.gold, Size = UDim2.fromOffset(320, 48), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -150), ZIndex = 40, Parent = UI.root })
	cl.Visible = false
	comboLbl = cl
	UI.label({ Text = UI.mobile and "Auto curls are running · pause for single lifts" or "Auto curls · pause for Click / Space · Q to leave", TextSize = 18, Color = C.dim, Size = UDim2.fromOffset(420, 24), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -4), ZIndex = 40, Parent = lift })
	local p = UI.panel({ Color = C.panel, Size = UDim2.fromOffset(330, 400), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -18, 0.5, 30), Radius = 20, ZIndex = 30, Parent = UI.root })
	panel = p
	panelKey = ""
	renderPanel(true)
	local diedConn = h.Died:Connect(function()
		alive = false
	end)
	while alive do
		local now = os.clock()
		if auto and now >= nextAutoPeak then
			-- Drop missed beats under a slow frame; never issue catch-up reward bursts.
			repeat nextAutoPeak += cycleDuration until nextAutoPeak > now
			if not cooling then
				cooling = true
				coolT0 = now - peakOffset
				local repSession = session
				task.spawn(function()
					awardRep(repSession)
					if session == repSession then
						cooling = false
						if alive and not auto then Animator.play("TrainRest") end
					end
				end)
			end
		elseif not auto and spaceHeld and not cooling then
			task.spawn(rep)
		end
		if combo > 0 and now - lastRep > cycleDuration + 0.9 then
			combo = 0
			cl.Visible = false
		end
		task.wait()
	end
	-- выход
	diedConn:Disconnect()
	while cooling do
		task.wait()
	end
	bar:Destroy()
	lift:Destroy()
	autoBtn:Destroy()
	cl:Destroy()
	p:Destroy()
	panel, val, cool, comboLbl = nil, nil, nil, nil
	spaceHeld = false
	auto = false
	session += 1
	unlock()
	Animator.stop()
	camera.CameraType = Enum.CameraType.Custom
	camera.FieldOfView = savedFov
	Hud.setMode("normal")
	Activities.busy = nil
	TrainCtl.active = false
	if total > 0 then
		UI.toast("+" .. Num.short(total) .. " strength this session 💪", "good")
	end
end

return TrainCtl
