-- StarterPlayerScripts/Client/Showroom.luau
-- Lightweight showroom anchors keep every animal available for inspection.
-- Only the nearest exhibits have a full animated client model.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local Roll = require(RS.Shared.Roll)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Animator = require(script.Parent.Animator)
local AnimalRig = require(script.Parent.AnimalRig)
local Fx = require(script.Parent.WorldFx)
local SpearFx = require(script.Parent.SpearFx)
local Reveal = require(script.Parent.Reveal)
local SpearFactoryV15 = require(RS:WaitForChild("V15SpearPresentation"):WaitForChild("SpearFactoryV15"))
local Menus = require(script.Parent.Menus)

local Showroom = {}
local C = Theme.C
local player = Players.LocalPlayer
local camera = workspace.CurrentCamera
local hall: Instance? = nil
local statues: { [string]: any } = {}
local mutCycle: { [string]: number } = {}
local busy = false
local anchors: { [string]: Model } = {}
local hiddenUntil: { [string]: number } = {}
local hiddenState: { [string]: boolean } = {}
local streamConnection: RBXScriptConnection? = nil
local runtime: Folder? = nil
local generation = 0
local weaponAnchors: {[string]: Model}={}
local weapons: {[string]: Model}={}
local weaponRuntime: Folder?=nil

local function hide(rig: any, on: boolean)
	if not rig.alive or not rig.model.Parent then return end
	for _, d in rig.model:GetDescendants() do
		if d:IsA("BasePart") then
			d.LocalTransparencyModifier = on and 1 or 0
		end
	end
end

local function viewingPosition(): Vector3?
	local current = workspace.CurrentCamera
	if current then return current.CFrame.Position end
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if root and root:IsA("BasePart") then return root.Position end
	return nil
end

local function streamStatues()
	local position = viewingPosition()
	if not position or not runtime then return end
	-- Every exhibit stays alive for the whole session (distance LOD in AnimalRig keeps it cheap).
	local radius = math.huge
	local maximum = 200
	local candidates = {}
	for sid, anchor in anchors do
		if anchor.Parent then
			local distance = (anchor:GetPivot().Position - position).Magnitude
			if distance <= radius then table.insert(candidates, { sid = sid, anchor = anchor, distance = distance }) end
		end
	end
	table.sort(candidates, function(a, b)
		if a.distance == b.distance then return a.sid < b.sid end
		return a.distance < b.distance
	end)
	local wanted = {}
	for i = 1, math.min(maximum, #candidates) do wanted[candidates[i].sid] = true end
	for sid, rig in statues do
		if not wanted[sid] or not rig.alive or not rig.model.Parent then
			rig:destroy()
			statues[sid] = nil
			hiddenState[sid] = nil
		end
	end
	-- Spread the expensive native model bindings over several updates after teleporting.
	local spawned = 0
	for i = 1, math.min(maximum, #candidates) do
		local entry = candidates[i]
		local rig = statues[entry.sid]
		if not rig and spawned < 4 then
			local scale = entry.anchor:GetAttribute("ShowroomScale")
			if typeof(scale) ~= "number" or scale <= 0 then scale = 1 end
			rig = AnimalRig.spawn(entry.sid, entry.anchor:GetPivot(), runtime, nil, scale)
			spawned += 1
			if rig then
				rig.model.Name = entry.sid
				rig.model:SetAttribute("Showroom", false)
				rig.model:SetAttribute("ShowroomSpecies", entry.sid)
				rig:play("idle")
				statues[entry.sid] = rig
				hiddenState[entry.sid] = false
			end
		end
		if rig then
			local concealed = (hiddenUntil[entry.sid] or 0) > os.clock()
			if hiddenState[entry.sid] ~= concealed then
				hide(rig, concealed)
				hiddenState[entry.sid] = concealed
			end
		end
	end
end

local function streamWeapons()
	local position=viewingPosition()
	if not position or not weaponRuntime then return end
	local radius=math.huge
	local maximum=200
	local candidates={}
	for id,anchor in pairs(weaponAnchors) do
		if anchor.Parent then
			local distance=(anchor:GetPivot().Position-position).Magnitude
			if distance<radius then table.insert(candidates,{id=id,anchor=anchor,distance=distance}) end
		end
	end
	table.sort(candidates,function(a,b)return a.distance<b.distance end)
	local wanted={}
	for i=1,math.min(maximum,#candidates) do wanted[candidates[i].id]=true end
	for id,model in pairs(weapons) do if not wanted[id] then model:Destroy();weapons[id]=nil end end
	for i=1,math.min(maximum,#candidates) do
		local entry=candidates[i]
		if not weapons[entry.id] then
			local model=SpearFactoryV15.Create(entry.id)
			if not model then
				local template=RS.Assets.Spears:FindFirstChild(entry.id)
				if template and template:IsA("Model") then model=template:Clone() end
			end
			if model then
				for _,part in model:GetDescendants() do
					if part:IsA("BasePart") then
						part.Anchored=true;part.CanCollide=false;part.CanQuery=false;part.CanTouch=false;part.CastShadow=false
					end
				end
				model:ScaleTo(entry.anchor:GetAttribute("ShowroomScale") or 1)
				model:PivotTo(entry.anchor:GetPivot());model.Parent=weaponRuntime
				weapons[entry.id]=model
			end
			break -- one static weapon per update; no simultaneous forty-model burst
		end
	end
end

function Showroom.init()
	generation += 1
	if streamConnection then streamConnection:Disconnect(); streamConnection = nil end
	for _, rig in statues do rig:destroy() end
	table.clear(statues)
	table.clear(anchors)
	table.clear(hiddenUntil)
	table.clear(hiddenState)
	if runtime then runtime:Destroy(); runtime = nil end
	if weaponRuntime then weaponRuntime:Destroy();weaponRuntime=nil end
	table.clear(weapons);table.clear(weaponAnchors)
	hall = workspace.Map:FindFirstChild("Showroom")
	local animals = hall and hall:FindFirstChild("Animals")
	if not animals then return end
	for _, anchor in animals:GetChildren() do
		if anchor:IsA("Model") and anchor:GetAttribute("Showroom") then
			local sid = anchor:GetAttribute("Species")
			if typeof(sid) == "string" and Config.SPECIES_BY_ID[sid] then anchors[sid] = anchor end
		end
	end
	runtime = Instance.new("Folder")
	runtime.Name = "ClientStatues"
	runtime.Parent = hall
	local spearFolder=hall:FindFirstChild("Spears")
	if spearFolder then
		for _,anchor in spearFolder:GetChildren() do
			if anchor:IsA("Model") and anchor:GetAttribute("ShowroomSpear") then
				local id=anchor:GetAttribute("SpearId")
				if type(id)=="string" then weaponAnchors[id]=anchor end
			end
		end
	end
	weaponRuntime=Instance.new("Folder");weaponRuntime.Name="ClientSpears";weaponRuntime.Parent=hall
	streamStatues()
	streamWeapons()
	local streamClock, animationClock = 0, 0
	streamConnection = RunService.Heartbeat:Connect(function(dt)
		streamClock += dt
		animationClock += dt
		if streamClock >= 0.35 then streamClock = 0; streamStatues();streamWeapons() end
		if animationClock < 2.5 then return end
		animationClock = 0
		for sid, rig in statues do
			if rig.alive and (hiddenUntil[sid] or 0) <= os.clock() and math.random() < 0.12 then
				rig:play(math.random() < 0.4 and "happy" or "look")
				local token = generation
				task.delay(2, function()
					if generation == token and statues[sid] == rig and rig.alive then rig:play("idle") end
				end)
			end
		end
	end)
end

-- «Раскрыть»: витринная гача без сумки
function Showroom.reveal(prompt: ProximityPrompt)
	if busy or Reveal.active then
		return
	end
	local part = prompt:FindFirstAncestorWhichIsA("BasePart")
	if not part then return end
	local sid = part:GetAttribute("Species")
	if type(sid) ~= "string" or not Config.SPECIES_BY_ID[sid] then return end
	busy = true
	local k = (mutCycle[sid] or 0) % 3 + 1
	mutCycle[sid] = k
	local mut = k == 2 and "gold" or (k == 3 and "rainbow" or nil)
	local sp = Config.SPECIES_BY_ID[sid]
	local ok, res = Backend.call("Demo", "fake", { sp = sid, mut = mut, m = Config.TIERS[math.min(6, sp.rarity)].m })
	if ok then
		local rig = statues[sid]
		local anchor = anchors[sid]
		local pos = rig and rig.cf.Position or (anchor and anchor:GetPivot().Position or part.Position)
		hiddenUntil[sid] = math.huge
		if rig then
			hide(rig, true)
			hiddenState[sid] = true
		end
		local c = player.Character
		local from = c and c:GetPivot().Position or (pos + Vector3.new(10, 4, 0))
		local revealOk, revealError = xpcall(Reveal.play, debug.traceback, res, pos, { from = from, fake = true, pedestal = true })
		camera.CameraType = Enum.CameraType.Custom
		hiddenUntil[sid] = if revealOk then os.clock() + 6.2 else 0
		if not revealOk then
			if rig and rig.alive then hide(rig, false); hiddenState[sid] = false end
			busy = false
			warn(revealError)
			UI.toast("Could not show this animal. Please try again.", "warn")
			return
		end
		if k < 3 then
			UI.toast("Tap again for the " .. (k == 1 and "✨ gold" or "🌈 rainbow") .. " variant", "info")
		end
	end
	busy = false
end

-- «Осмотреть»: окно копья
function Showroom.inspect(prompt: ProximityPrompt)
	local id = (prompt.Parent :: Instance):GetAttribute("SpearId")
	local s = Config.SPEAR_BY_ID[id]
	if not s then
		return
	end
	local _, body = UI.window("inspect", "🔱 " .. s.name, Vector2.new(780, 460), C.blue)
	local left = Instance.new("Frame")
	left.BackgroundTransparency = 1
	left.Size = UDim2.new(0.42, 0, 1, 0)
	left.Parent = body
	Menus.spearView(s.id, left, 1.2)
	local right = Instance.new("Frame")
	right.BackgroundTransparency = 1
	right.Size = UDim2.new(0.56, 0, 1, 0)
	right.Position = UDim2.fromScale(0.44, 0)
	right.Parent = body
	UI.list(Enum.FillDirection.Vertical, 8).Parent = right
	local st = Config.spearStats(s.id, 0)
	local lines = {
		{ s.desc, 22, C.dim },
		{ "Sharpness: " .. s.sharp, 24, C.text },
		{ "Weight: " .. s.heavy, 24, C.text },
		{ string.format("Luck ×%.1f   ·   Range ×%.2f", st.luck, st.range), 24, C.text },
		{ "Chance to reach ×10: " .. Num.odds(Roll.reachChance(10, st.alpha)) .. "   ·   ×100: " .. Num.odds(Roll.reachChance(100, st.alpha)), 21, C.cyan },
		{ "Price: 💰 " .. Num.short(s.price), 26, C.gold },
	}
	for i, l in lines do
		-- V56: описание копья (до 62 знаков) занимает две строки; при высоте в одну вторая строка была обрезана у 36 из 46 копий
		local h = if i == 1 then l[2] * 2 + 12 else l[2] + 10
		UI.label({ Text = l[1], TextSize = l[2], Color = l[3], Size = UDim2.new(1, 0, 0, h), XAlign = Enum.TextXAlignment.Left, YAlign = if i == 1 then Enum.TextYAlignment.Top else nil, Wrap = true, LayoutOrder = i, Parent = right })
	end
	local r = Instance.new("Frame")
	r.BackgroundTransparency = 1
	r.Size = UDim2.new(1, 0, 0, 60)
	r.LayoutOrder = 10
	r.Parent = right
	local b = UI.button({ Text = "Open Shop", TextSize = 22, Color = C.green, Size = UDim2.fromOffset(230, 56) }, function()
		Menus.spears()
	end)
	b.Parent = r
	local t = UI.button({ Text = "🎯 Throw", TextSize = 22, Color = C.red, Size = UDim2.fromOffset(170, 56), Position = UDim2.fromOffset(244, 0) }, function()
		UI.closeWindow()
		Showroom.chooser(s.id)
	end)
	t.Parent = r
end

-- Тестовый бросок: выбор ступени
function Showroom.chooser(spearId: string?)
	local _, body = UI.window("demothrow", "🎯 Test Throw", Vector2.new(760, 330), C.red)
	UI.label({ Text = "Choose a multiplier to preview the throw, flight and catch reveal", TextSize = 22, Color = C.dim, Size = UDim2.new(1, 0, 0, 30), Parent = body })
	local g = Instance.new("Frame")
	g.BackgroundTransparency = 1
	g.Size = UDim2.new(1, 0, 1, -40)
	g.Position = UDim2.fromOffset(0, 40)
	g.Parent = body
	local grid = UI.grid(Vector2.new(225, 90), 12)
	grid.HorizontalAlignment = Enum.HorizontalAlignment.Center
	grid.Parent = g
	for i, t in Config.TIERS do
		local b = UI.button({ Text = "×" .. t.m .. "\n" .. t.name, TextSize = 24, Color = t.color2, Size = UDim2.fromOffset(225, 90), LayoutOrder = i }, function()
			UI.closeWindow(true)
			task.spawn(Showroom.demoThrow, i, spearId)
		end)
		b.Parent = g
	end
end

function Showroom.demoThrow(tierIdx: number, spearId: string?)
	if busy or Reveal.active or not hall then
		return
	end
	local stand = hall:FindFirstChild("Stand") :: BasePart?
	local c = player.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
	local hum = c and c:FindFirstChildOfClass("Humanoid")
	if not stand or not hrp or not hum then
		return
	end
	busy = true
	local tier = Config.TIERS[tierIdx]
	-- зверь подходящей редкости
	local pool = {}
	for _, sp in Config.SPECIES do
		if sp.rarity == math.min(6, tierIdx) then
			table.insert(pool, sp.id)
		end
	end
	local sid = pool[math.random(1, #pool)]
	local mut = tierIdx >= 6 and "rainbow" or (tierIdx == 5 and "gold" or nil)
	local ok, res = Backend.call("Demo", "fake", { sp = sid, mut = mut, m = tier.m })
	if not ok then
		busy = false
		return
	end
	res.tier = tierIdx
	local ws = hum.WalkSpeed
	hum.WalkSpeed = 0
	hrp.CFrame = CFrame.lookAt(stand.Position + Vector3.new(0, 3, 0), stand.Position + Vector3.new(0, 3, -10))
	Hud.setMode("cinematic")
	camera.CameraType = Enum.CameraType.Scriptable
	local base = CFrame.lookAt(stand.Position + Vector3.new(3, 6, 9), stand.Position + Vector3.new(0, 2, -30))
	camera.CFrame = base
	Animator.play("Charge")
	Hud.banner("×" .. tier.m .. " " .. tier.name, tier.color, "test throw", 1.2)
	for i = 1, tierIdx do
		Sfx.rise(i + 1, 0.4)
		task.wait(0.16)
	end
	Animator.play(tier.clip)
	task.wait(Animator.release(tier.clip))
	local from = Animator.handPosition(c) or (stand.Position + Vector3.new(0, 5, 0))
	local to = SpearFx.groundAt(Vector3.new(169 + math.random(-6, 6), 1, 140 - 60 - tierIdx * 4))
	local landed: Vector3? = nil
	local fl = SpearFx.launch({ spear = spearId or (Backend.data and Backend.data.spear) or "stick", from = from, to = to, tier = tierIdx, isLocal = true, onLand = function(p)
		landed = p
	end })
	local conn = RunService.RenderStepped:Connect(function(dt)
		local dir = Vector3.new(fl.dir.X, 0, fl.dir.Z)
		dir = dir.Magnitude > 1e-3 and dir.Unit or Vector3.new(0, 0, -1)
		local eye = fl.pos - dir * (10 + tierIdx) + Vector3.new(0, 4 + tierIdx * 0.4, 0)
		camera.CFrame = camera.CFrame:Lerp(CFrame.lookAt(eye, fl.pos + dir * 5), 1 - math.exp(-dt * 8))
	end)
	while not landed do
		task.wait()
	end
	conn:Disconnect()
	task.wait(0.2)
	fl.revealHeld = true
	local revealOk, revealError = xpcall(Reveal.play, debug.traceback, res, landed :: Vector3, { from = stand.Position, fake = true })
	fl.revealHeld = false
	if not revealOk then
		Animator.stop()
		hum.WalkSpeed = ws > 0 and ws or Config.WALK_SPEED
		camera.CameraType = Enum.CameraType.Custom
		Hud.setMode("normal")
		busy = false
		warn(revealError)
		UI.toast("Could not show the catch. Please try again.", "warn")
		return
	end
	if tierIdx >= 3 then
		Animator.play("Cheer")
		task.wait(1.2)
	end
	Animator.stop()
	hum.WalkSpeed = ws > 0 and ws or Config.WALK_SPEED
	camera.CameraType = Enum.CameraType.Custom
	Hud.setMode("normal")
	busy = false
end

return Showroom
