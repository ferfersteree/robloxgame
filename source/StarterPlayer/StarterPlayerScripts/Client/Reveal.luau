-- StarterPlayerScripts/Client/Reveal.luau
-- Гача-раскрытие добычи: куст шуршит → «?» → свечение растёт по цветам редкостей → (эпик+) темнеет небо,
-- столб света, стук сердца → взрыв лучей и конфетти → зверь выпрыгивает и радуется → карточка с цифрами,
-- штампы «НОВЫЙ ВИД!/РЕКОРД!» → карточка летит в сумку. Со 2-го раскрытия — «Пропустить».
local RS = game:GetService("ReplicatedStorage")
local Fauna150 = require(game:GetService("ReplicatedStorage"):WaitForChild("Fauna150"))
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Lighting = game:GetService("Lighting")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local Net = require(RS.Shared.Net)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Fx = require(script.Parent.WorldFx)
local AnimalRig = require(script.Parent.AnimalRig)
local Backend = require(script.Parent.Backend)
local Hud = require(script.Parent.Hud)
local Occlusion = require(script.Parent.RevealOcclusion)
local CoverLibraryV15 = RS:WaitForChild("V15Covers")
local CoverFactoryV15 = require(CoverLibraryV15:WaitForChild("Factory"))
local CoverMotionV15 = require(CoverLibraryV15:WaitForChild("Motion"))
local CoverStageV15 = require(CoverLibraryV15:WaitForChild("Stage"))
local FaunaFactoryV15 = require(RS:WaitForChild("V16Fauna"):WaitForChild("Factory"))
local activeCoverCleanup: (() -> ())? = nil

local Reveal = {}
Reveal.active = false
Reveal.count = 0

local camera = workspace.CurrentCamera
local FxEv = Net.ev("Fx")

-- отдельная цветокоррекция раскрытия (не мешает ZoneFx)
local cc = Instance.new("ColorCorrectionEffect")
cc.Name = "RevealCC"
cc.Parent = Lighting

local function rarityOf(spId: string): (any, any)
	local sp = Config.SPECIES_BY_ID[spId]
	return sp, Config.RARITIES[sp and sp.rarity or 1]
end

-- The filled centre belongs to two rigid halves; .5-stud cubes never scale.
local function makeBush(plan: any, zoneId: number)
	local model = assert(CoverFactoryV15.CreateCover(zoneId, plan.Frame, Fx.folder))
	model.Name = "RevealCoverV15"
	model:SetAttribute("Stage", "anticipation")
	local motion = CoverMotionV15.new(model, {ZoneId=zoneId, Spread=plan.Spread})
	game:GetService("Debris"):AddItem(model,60)
	local function shake(amplitude: number)
		motion:Rustle(amplitude)
	end
	local function open()
		model:SetAttribute("Stage", "opening")
		motion:Open(.7,plan.Spread)
	end
	local function cleanup()
		motion:Destroy()
		if model.Parent then model:Destroy() end
	end
	local color1,color2 = CoverFactoryV15.BiomeColors(zoneId)
	return model,shake,open,cleanup,color1,color2
end

local function questionMark(pos: Vector3): (BillboardGui, TextLabel)
	local part = Fx.anchor(pos, 30)
	local bb = Instance.new("BillboardGui")
	bb.Size = UDim2.fromOffset(160, 160)
	bb.AlwaysOnTop = true
	bb.LightInfluence = 0
	bb.Parent = part
	local glow = Instance.new("ImageLabel")
	glow.BackgroundTransparency = 1
	glow.Image = UI.IMG.glow
	glow.Size = UDim2.fromScale(1.6, 1.6)
	glow.Position = UDim2.fromScale(-0.3, -0.3)
	glow.ImageTransparency = 0.3
	glow.Parent = bb
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Font = Theme.FONT
	l.Text = "?"
	l.TextScaled = true
	l.TextColor3 = Color3.new(1, 1, 1)
	local s = Instance.new("UIStroke")
	s.Thickness = 5
	s.Parent = l
	l.Parent = bb
	return bb, l
end

-- Ждать с возможностью «перемотки»
local skipFlag = false
local function wait(t: number)
	local t0 = os.clock()
	while os.clock() - t0 < t do
		if skipFlag then
			return
		end
		RunService.RenderStepped:Wait()
	end
end

local function camShot(pos: Vector3, h: number, from: Vector3): CFrame
	local back = Vector3.new(from.X - pos.X, 0, from.Z - pos.Z)
	back = back.Magnitude > 1e-3 and back.Unit or Vector3.new(0, 0, 1)
	local dist = 7 + h * 1.5
	local eye = pos + back * dist + Vector3.new(0, 2.5 + h * 0.55, 0)
	return CFrame.lookAt(eye, pos + Vector3.new(0, h * 0.45, 0))
end

local function moveCam(target: CFrame, dur: number)
	camera.CameraType = Enum.CameraType.Scriptable
	local start = camera.CFrame
	local t0 = os.clock()
	while true do
		local k = math.min(1, (os.clock() - t0) / dur)
		local e = 1 - (1 - k) ^ 3
		camera.CFrame = start:Lerp(target, e)
		if k >= 1 then
			break
		end
		RunService.RenderStepped:Wait()
	end
end

-- Срыв — отдельная короткая сцена неудачи, без гачи, животного и награды.
function Reveal.playCrash(_res: any, pos: Vector3, o: any)
	local opts = o or {}
	Reveal.active = true
	Backend.hold(true)
	local prevMode = Hud.mode
	Hud.setMode("cinematic")
	Occlusion.begin(pos, 1.5)
	local from = opts.from or camera.CFrame.Position
	if not opts.noCam then
		task.spawn(moveCam, camShot(pos, 1.5, from), 0.35)
	end
	Fx.ring(pos + Vector3.new(0, 0.2, 0), Theme.C.red, 7, 0.5)
	Fx.burst(pos + Vector3.new(0, 0.6, 0), { tex = "smoke", color = Color3.fromRGB(190, 180, 165), n = 14, speed = NumberRange.new(3, 8), size = 1.4, size2 = 2.6, life = 0.9, light = 0, accel = Vector3.new(0, 3, 0), transp = 0.25 })
	Fx.text(pos + Vector3.new(0, 4, 0), "💨 MISS · THE SPEAR SLIPPED", Theme.C.red, 28, 1.8)
	UI.pop("SLIP · NO CATCH", Theme.C.red, nil, 42)
	UI.toast("Missed throw: no catch or reward", "warn", 2.4)
	Sfx.note(-5, 0.45)
	task.delay(0.18, function()
		Sfx.note(-9, 0.4)
	end)
	FxEv:FireServer({ k = "crash", pos = pos })
	task.wait(1.25)
	Hud.setMode(prevMode == "cinematic" and "normal" or prevMode)
	Backend.hold(false)
	Reveal.active = false
	Occlusion.finish()
end

-- Нижняя карточка результата
local function resultPanel(res: any, sp: any, rar: any, fast: boolean): (Frame, () -> ())
	local item = res.item
	local escaped = res.escaped == true
	local col = escaped and Theme.C.red or rar.color
	local panel = UI.panel({ Color = Theme.C.panel, Size = UDim2.fromOffset(600, 250), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -24), Radius = 24, LineThick = 4, ZIndex = 20, Parent = UI.reveal })
	local sc = Instance.new("UIScale")
	sc.Scale = 0.3
	sc.Parent = panel
	UI.tween(sc, 0.35, { Scale = 1 }, Enum.EasingStyle.Back)
	local rays = UI.rays(panel, col, 12, 900, 18)
	rays.ZIndex = 19
	-- шапка с редкостью
	local head = UI.panel({ Color = col, Size = UDim2.new(0, 10, 0, 44), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 0, 0), Radius = 14, ZIndex = 24, Parent = panel })
	head.AutomaticSize = Enum.AutomaticSize.X
	UI.pad(18, 0).Parent = head
	local rname = escaped and "ESCAPED!" or string.upper(rar.name)
	if item and item.mut then
		rname = (item.mut == "gold" and "✨ GOLDEN · " or "🌈 RAINBOW · ") .. rname
	end
	UI.label({ Text = rname, TextSize = 28, Size = UDim2.new(0, 10, 1, 0), AutoX = true, ZIndex = 26, Parent = head })
	UI.shine(head, 0.9)
	UI.label({ Text = (sp and sp.icon or "") .. " " .. (sp and sp.name or "?"), TextSize = 52, Size = UDim2.new(1, -40, 0, 60), Position = UDim2.fromOffset(20, 30), ZIndex = 24, Gradient = { Color3.new(1, 1, 1), col }, Parent = panel })
	local finished = false
	local stats = Instance.new("Frame")
	stats.BackgroundTransparency = 1
	stats.Size = UDim2.new(1, -40, 0, 70)
	stats.Position = UDim2.fromOffset(20, 96)
	stats.ZIndex = 24
	stats.Parent = panel
	UI.list(Enum.FillDirection.Horizontal, 12, Enum.HorizontalAlignment.Center).Parent = stats
	local function stat(icon: string, color: Color3, order: number): TextLabel
		local b = UI.panel({ Color = Theme.C.panel2, Size = UDim2.fromOffset(176, 64), Radius = 14, ZIndex = 25, LayoutOrder = order, Parent = stats })
		UI.label({ Text = icon, TextSize = 30, Size = UDim2.fromOffset(40, 64), Position = UDim2.fromOffset(6, 0), ZIndex = 27, Stroke = 2, Parent = b })
		return UI.label({ Text = "0", TextSize = 30, Color = color, Size = UDim2.new(1, -52, 1, 0), Position = UDim2.fromOffset(46, 0), XAlign = Enum.TextXAlignment.Left, ZIndex = 27, Parent = b })
	end
	local tierInfo = Config.TIERS[math.max(1, res.tier or 1)]
	if escaped then
		UI.label({ Text = "This spear cannot pierce its hide!", TextSize = 26, Color = Theme.C.dim, Size = UDim2.new(1, -40, 0, 30), Position = UDim2.fromOffset(20, 104), ZIndex = 24, Parent = panel })
		UI.label({ Text = "Requires: " .. tostring(res.need or "a better spear") .. " 🔱", TextSize = 30, Color = Theme.C.gold, Size = UDim2.new(1, -40, 0, 36), Position = UDim2.fromOffset(20, 138), ZIndex = 24, Parent = panel })
	else
		local wl = stat("⚖️", Theme.C.text, 1)
		local pl = stat("💰", Theme.C.gold, 2)
		local ml = stat("🔥", tierInfo.color, 3)
		local w, price, m = item and item.w or 0, item and item.price or 0, res.m or 1
		if fast then
			wl.Text = Num.weight(w)
			pl.Text = Num.short(price)
			ml.Text = Num.mult(m)
		else
			task.spawn(function()
				UI.countUp(wl, 0, w, 0.6, Num.weight, true)
				UI.countUp(pl, 0, price, 0.8, Num.short, true)
				UI.countUp(ml, 1, m, 0.5, Num.mult, false)
			end)
		end
		local zone = Config.ZONES[res.zone or (sp and sp.zone) or 1]
		UI.label({ Text = zone.icon .. " " .. zone.name .. (res.dist and res.dist > 0 and ("  ·  " .. math.floor(res.dist) .. " m") or "") .. (res.xp and res.xp > 0 and ("  ·  +" .. res.xp .. " XP") or ""), TextSize = 22, Color = Theme.C.dim, Size = UDim2.new(1, -40, 0, 26), Position = UDim2.fromOffset(20, 168), ZIndex = 24, Stroke = 2, Parent = panel })
	end
	-- штампы
	local stamps = {}
	if res.isNew and not escaped then
		table.insert(stamps, { "NEW SPECIES!", Theme.C.gold, -16 })
	end
	if res.isRecord and not escaped then
		table.insert(stamps, { "NEW RECORD!", Theme.C.pink, 12 })
	end
	task.spawn(function()
		if not fast then
			task.wait(0.9)
		end
		for i, s in stamps do
			local st = UI.label({ Text = s[1], TextSize = 40, Color = s[2], Size = UDim2.fromOffset(240, 50), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(i == 1 and 0.86 or 0.14, 0, 0, 10), Rotation = s[3], ZIndex = 30, Parent = panel })
			local ss = Instance.new("UIScale")
			ss.Scale = 3
			ss.Parent = st
			UI.tween(ss, 0.22, { Scale = 1 }, Enum.EasingStyle.Back)
			Sfx.play("stamp")
			UI.punch(panel, 0.04)
			task.wait(0.3)
		end
	end)
	local btn = UI.button({ Text = escaped and "Oh well…" or "Collect!", TextSize = 30, Color = escaped and Theme.C.orange or Theme.C.green, Size = UDim2.fromOffset(220, 58), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 1, -8), ZIndex = 28, Shine = true }, function()
		finished = true
	end)
	btn.Parent = panel
	local function waitDone()
		local t0 = os.clock()
		local auto = fast and 1.6 or 6
		local conn = UserInputService.InputBegan:Connect(function(i, gp)
			if not gp and (i.KeyCode == Enum.KeyCode.Space or i.KeyCode == Enum.KeyCode.Return or i.KeyCode == Enum.KeyCode.E) then
				finished = true
			end
		end)
		while not finished and os.clock() - t0 < auto do
			task.wait()
		end
		conn:Disconnect()
	end
	return panel, waitDone
end

export type RevealOpts = { from: Vector3?, fake: boolean?, noCam: boolean?, pedestal: boolean? }

-- Главное: res — ответ Throw (или Demo fake), pos — точка на земле. Блокирует до конца.
function Reveal.play(res: any, pos: Vector3, o: RevealOpts?)
	local opts: RevealOpts = o or {}
	-- A tension bust still produces a normal hunt with reduced luck.
	if res.failed == true then
		Reveal.playCrash(res, pos, opts)
		return
	end
	local sp, rar = rarityOf(res.sp)
	local r = sp and sp.rarity or 1
	local escaped = res.escaped == true
	Reveal.active = true
	Backend.hold(true)
	Reveal.count += 1
	local settings = Backend.data and Backend.data.settings
	local fast = Reveal.count > 1 and settings ~= nil and settings.skip == true
	skipFlag = false
	local skipBtn: Frame? = nil
	local skipConn: RBXScriptConnection? = nil
	if Reveal.count > 1 and not fast then
		local sb = UI.button({ Text = "Skip ⏩", TextSize = 24, Color = Theme.C.blue, Size = UDim2.fromOffset(210, 52), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -20, 0, 90), ZIndex = 40 }, function()
			skipFlag = true
		end)
		sb.Parent = UI.reveal
		skipBtn = sb
		-- ПК: Пробел / E / Enter тоже пропускают
		skipConn = UserInputService.InputBegan:Connect(function(i, gp)
			if not gp and (i.KeyCode == Enum.KeyCode.Space or i.KeyCode == Enum.KeyCode.Return or i.KeyCode == Enum.KeyCode.E) then
				skipFlag = true
			end
		end)
	end
	local prevMode = Hud.mode
	Hud.setMode("cinematic")
	local h = sp and Fauna150.Attr(sp.id, "Height") or 2
	h = h or 2
	local from = opts.from or camera.CFrame.Position
	local zoneId = res.zone or (sp and sp.zone) or 1
	local coverSpec = assert(CoverFactoryV15.Get(string.format("spawn_cover_%02d",math.clamp(zoneId,1,25))))
	local visualAnimal = FaunaFactoryV15.Get(res.sp)
	if visualAnimal then h=visualAnimal.h end
	local plan = CoverStageV15.Plan(pos,from,coverSpec,visualAnimal)
	local effectPos = plan.Center
	Occlusion.begin(plan.Focus, math.max(h,plan.Height))
	if not opts.noCam then
		task.spawn(moveCam, camShot(plan.Focus,plan.Height,from), fast and 0.3 or 0.7)
	end
	local bushSize = math.clamp(h * 0.55, 1.6, 5)
	local bush,shake,openCover,cleanupCover,coverColor,coverColor2 = makeBush(plan,zoneId)
	local shakeConn: RBXScriptConnection? = nil
	local emergingRig: any = nil
	local emergenceDone = false
	local function cleanupScene()
		if shakeConn then shakeConn:Disconnect();shakeConn=nil end
		cleanupCover()
		if not emergenceDone and emergingRig and emergingRig.alive then emergingRig:destroy() end
	end
	activeCoverCleanup = cleanupScene
	local glowLight = Fx.light(effectPos + Vector3.new(0, 2, 0), Color3.new(1, 1, 1), 16, 0, 60)
	local bb, q = questionMark(effectPos + Vector3.new(0, bushSize + 2.5, 0))
	bb.Enabled = false
	local amp = 0.4
	local alive = true
	shakeConn = RunService.RenderStepped:Connect(function()
		if alive then
			shake(amp)
		end
	end)
	Sfx.at(effectPos, "rustle", 1, 0.9)
	Fx.burst(effectPos + Vector3.new(0, bushSize * 0.6, 0), { tex = "square", color = coverColor, n = 10, speed = NumberRange.new(4, 9), size = 0.35, life = 1.2, rot = true, accel = Vector3.new(0, -14, 0), light = 0 })
	wait(fast and 0.15 or 0.55)
	-- «?» и рост редкости
	bb.Enabled = true
	Sfx.play("pop")
	local qs = Instance.new("UIScale")
	qs.Scale = 0.2
	qs.Parent = q
	UI.tween(qs, 0.25, { Scale = 1 }, Enum.EasingStyle.Back)
	local steps = escaped and math.min(r, 3) or r
	if not fast then
		wait(0.25)
		for i = 1, steps do
			if skipFlag then
				break
			end
			local rc = Config.RARITIES[i]
			q.TextColor3 = rc.color
			glowLight.Color = rc.color
			glowLight.Brightness = 1 + i * 1.2
			amp = 0.4 + i * 0.35
			Sfx.rise(i, 0.6)
			UI.punch(q, 0.25)
			Fx.burst(effectPos + Vector3.new(0, bushSize, 0), { tex = "sparkle", color = rc.color, n = 6 + i * 3, speed = NumberRange.new(4, 10), size = 0.6 + i * 0.1, life = 0.8, accel = Vector3.new(0, 4, 0) })
			if i >= 4 and i == 4 then
				-- эпик+: небо темнеет, столб света, сердце
				UI.tween(cc, 0.6, { Brightness = -0.32, Contrast = 0.25, Saturation = -0.25, TintColor = Theme.lerp(Color3.new(1, 1, 1), rar.color, 0.35) })
				Fx.pillar(effectPos, rar.color, 160, 4.5, 2.4 + r * 0.6)
				Sfx.play("thunder", 0.8, 0.7)
				task.spawn(function()
					for _ = 1, 4 do
						if skipFlag or not alive then
							break
						end
						Sfx.play("heart", 1, 0.9)
						task.wait(0.5)
					end
				end)
			end
			if i >= 5 then
				Fx.lightning(effectPos + Vector3.new(math.random(-8, 8), 80, math.random(-8, 8)), effectPos, rc.color, 10, 0.6)
				Fx.shake(0.25, 0.4)
			end
			wait(i >= 4 and 0.62 or 0.38)
		end
		if r >= 4 and not escaped then
			wait(0.5)
		end
	end
	-- взрыв
	alive = false
	if shakeConn then shakeConn:Disconnect();shakeConn=nil end
	bb:Destroy()
	local col = escaped and Theme.C.red or rar.color
	Fx.burst(effectPos + Vector3.new(0, bushSize * 0.5, 0), { tex = "square", color = coverColor, color2 = coverColor2, n = 30, speed = NumberRange.new(10, 22), size = 0.5, life = 1.4, rot = true, accel = Vector3.new(0, -30, 0), light = 0 })
	Fx.burst(effectPos + Vector3.new(0, bushSize * 0.5, 0), { tex = "star", color = col, n = 12 + r * 6, speed = NumberRange.new(12, 26), size = 1 + r * 0.15, life = 1.2, rot = true, accel = Vector3.new(0, -6, 0) })
	Fx.sphere(effectPos + Vector3.new(0, h * 0.5, 0), col, 3 + h * 0.6, 0.35)
	Fx.ring(effectPos + Vector3.new(0, 0.2, 0), col, 8 + r * 2, 0.6)
	openCover()
	glowLight.Brightness = 0
	UI.flash(col, 0.35, r >= 4 and 0.15 or 0.45)
	if r >= 3 and not escaped then
		UI.confetti(30 + r * 15, { rar.color, Theme.C.gold, Color3.new(1, 1, 1) })
	end
	Sfx.play(r >= 4 and "boom" or "pop", 1, 0.9)
	if r >= 4 and not escaped then
		Sfx.play("win", 1, 0.6)
	end
	UI.tween(cc, 0.8, { Brightness = 0, Contrast = 0, Saturation = 0, TintColor = Color3.new(1, 1, 1) })
	-- Open enough before any animal geometry is created. Skip shortens rarity
	-- anticipation, never the physical curtain clearance.
	local openStarted=os.clock()
	while os.clock()-openStarted<.45 and bush.Parent do RunService.RenderStepped:Wait() end
	local look = Vector3.new(from.X,pos.Y,from.Z)
	if (look-pos).Magnitude<.1 then look=pos+Vector3.zAxis end
	local rig = AnimalRig.spawn(res.sp,CFrame.lookAt(plan.Start,plan.Start+plan.Direction),Fx.folder,res.item and res.item.mut or nil)
	emergingRig=rig
	if rig then CoverStageV15.Walk(rig,plan) end
	emergenceDone=true
	cleanupScene()
	if activeCoverCleanup==cleanupScene then activeCoverCleanup=nil end
	-- чужим игрокам
	FxEv:FireServer({ k = "reveal", sp = res.sp, rarity = r, mut = res.item and res.item.mut or nil, pos = pos, escaped = escaped })
	if skipBtn then
		skipBtn:Destroy()
		skipBtn = nil
	end
	if skipConn then
		skipConn:Disconnect()
		skipConn = nil
	end
	local panel, waitDone = resultPanel(res, sp, rar, fast or skipFlag)
	if escaped then
		task.delay(0.9, function()
			if rig and rig.model.Parent then
				rig:play("flee", 1.4)
				local start = rig.cf
				local dir = (pos - look).Unit
				local t0 = os.clock()
				rig.onUpdate = function(self, _dt)
					local k = os.clock() - t0
					self.cf = CFrame.lookAt(start.Position + dir * k * 24, start.Position + dir * (k * 24 + 1))
				end
			end
			Sfx.note(-5, 0.6)
			task.wait(0.25)
			Sfx.note(-9, 0.6)
		end)
	end
	waitDone()
	-- карточка улетает в сумку
	local center = UI.screenPos(panel)
	local sc = panel:FindFirstChildOfClass("UIScale")
	if sc then
		UI.tween(sc, 0.25, { Scale = 0 }, Enum.EasingStyle.Back, Enum.EasingDirection.In)
	end
	if not escaped and not opts.fake then
		Hud.fly(sp and sp.icon or "🐾", center, Hud.bagPos(), 3, function()
			Sfx.play("coin", 1.2, 0.6)
		end)
	end
	task.delay(0.3, function()
		panel:Destroy()
	end)
	if rig then
		local m = rig.model
		task.delay(opts.pedestal and 6 or 1.2, function()
			if m.Parent then
				Fx.burst(rig.cf.Position + Vector3.new(0, h * 0.5, 0), { tex = "smoke", color = Color3.new(1, 1, 1), n = 10, speed = NumberRange.new(3, 7), size = 2, size2 = 3, life = 0.8, light = 0, accel = Vector3.zero, transp = 0.3 })
				rig:destroy()
			end
		end)
	end
	Hud.setMode(prevMode == "cinematic" and "normal" or prevMode)
	Backend.hold(false)
	Reveal.active = false
	Occlusion.finish()
end

-- Always restore local visibility if a reveal is interrupted by a script error.
local playScene = Reveal.play
function Reveal.play(res: any, pos: Vector3, opts: RevealOpts?)
	local ok, problem = xpcall(playScene, debug.traceback, res, pos, opts)
	if activeCoverCleanup then local cleanup=activeCoverCleanup;activeCoverCleanup=nil;cleanup() end
	Occlusion.finish()
	if not ok then
		Backend.hold(false)
		Reveal.active = false
		Hud.setMode("normal")
		error(problem, 0)
	end
end

-- Чужие раскрытия: короткая версия без интерфейса
FxEv.OnClientEvent:Connect(function(pl: any)
	if type(pl) ~= "table" or pl.k ~= "reveal" or typeof(pl.pos) ~= "Vector3" or type(pl.sp) ~= "string" then
		return
	end
	local sp, rar = rarityOf(pl.sp)
	if not sp then
		return
	end
	local pos = pl.pos :: Vector3
	if (camera.CFrame.Position - pos).Magnitude > 300 then
		return
	end
	local col = pl.escaped and Theme.C.red or rar.color
	Fx.sphere(pos + Vector3.new(0, 1.5, 0), col, 4, 0.35)
	Fx.burst(pos + Vector3.new(0, 1.5, 0), { tex = "star", color = col, n = 16, speed = NumberRange.new(8, 18), size = 1, life = 1, rot = true })
	if sp.rarity >= 4 then
		Fx.pillar(pos, rar.color, 140, 3, 3)
	end
	local rig = AnimalRig.spawn(pl.sp, CFrame.new(pos) * CFrame.Angles(0, math.random() * 6, 0), Fx.folder, pl.mut)
	if rig then
		rig:play(pl.escaped and "flee" or "happy")
	end
	local who = Players:GetPlayerByUserId(pl.by or 0)
	Fx.text(pos + Vector3.new(0, 5, 0), (who and who.DisplayName .. ": " or "") .. sp.icon .. " " .. sp.name, col, 30, 2.4)
	task.delay(2.6, function()
		if rig then
			rig:destroy()
		end
	end)
end)

return Reveal


