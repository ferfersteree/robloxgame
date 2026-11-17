-- StarterPlayerScripts/Client/Animator.luau
-- Процедурные позы R15 для ВСЕХ персонажей: засада, натяжение, 6 бросков по ступеням, срыв, радость,
-- гантели, упаковка. Свой персонаж — мгновенно (Animator.play), остальные — по атрибутам Pose/PoseT (Relay).
-- Во время поз инструмент скрыт, а в руке рисуется клиентская копия копья (атрибут персонажа SpearId).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local RS = game:GetService("ReplicatedStorage")

local PoseData = require(RS.Shared.PoseData) :: any
local Net = require(RS.Shared.Net)

local Animator = {}
local NativeAssets = RS:WaitForChild("V15SpearPresentation")
local NativeFactory = require(NativeAssets.SpearFactoryV15)
local NativeThrow = require(NativeAssets.PlayerThrowV15)
local THROW_POWER = {Throw1=.25,Throw2=.42,Throw5=.58,Throw10=.72,Throw25=.88,Throw100=1}
for name,power in pairs(THROW_POWER) do
	local clip = PoseData.clips[name]
	if clip then
		local timing = NativeThrow.Timing(power)
		clip.release = timing.Release
		clip.keys = {{0,clip.keys[1][2]},{timing.Duration,clip.keys[#clip.keys][2]}}
	end
end

local JOINTS = {
	"Root", "Waist", "Neck",
	"LeftShoulder", "LeftElbow", "LeftWrist",
	"RightShoulder", "RightElbow", "RightWrist",
	"LeftHip", "LeftKnee", "LeftAnkle",
	"RightHip", "RightKnee", "RightAnkle",
}
-- клипы, где копьё в руке (до момента выпуска release)
local HOLD = { Hide = true, Charge = true, Throw1 = true, Throw2 = true, Throw5 = true, Throw10 = true, Throw25 = true, Throw100 = true, Crash = true }
local ZERO = { 0, 0, 0 }

type Rig = {
	char: Model,
	hum: Humanoid,
	motors: { [string]: Motor6D | AnimationConstraint },
	cur: { [string]: { number } },
	active: boolean,
	spear: Model?,
	spearId: string?,
	tool: Tool?,
}

local rigs: { [Model]: Rig } = {}
local player = Players.LocalPlayer
local PoseEv = Net.ev("Pose")
local localClip: string? = nil
local localT0 = 0
local holdOverride: boolean? = nil -- принудительно показать/скрыть копьё в руке (витрина)

local spearsFolder = Instance.new("Folder")
spearsFolder.Name = "HandSpears"
spearsFolder.Parent = workspace

local function smooth(u: number): number
	u = math.clamp(u, 0, 1)
	return u * u * (3 - 2 * u)
end

local function wrap(d: number): number
	return (d + 180) % 360 - 180
end

local poseOut: { [string]: { number } } = {}
for _, j in JOINTS do
	poseOut[j] = { 0, 0, 0 }
end
poseOut.root = { 0, 0, 0 }

local function blendInto(a: any, b: any, u: number)
	for _, j in JOINTS do
		local va = a[j] or ZERO
		local vb = b[j] or ZERO
		local o = poseOut[j]
		o[1] = va[1] + (vb[1] - va[1]) * u
		o[2] = va[2] + (vb[2] - va[2]) * u
		o[3] = va[3] + (vb[3] - va[3]) * u
	end
	local ra = a.root or ZERO
	local rb = b.root or ZERO
	local o = poseOut.root
	o[1] = ra[1] + (rb[1] - ra[1]) * u
	o[2] = ra[2] + (rb[2] - ra[2]) * u
	o[3] = ra[3] + (rb[3] - ra[3]) * u
end

-- Имя клипа после переходов after и локальное время
local function resolve(name: string, t: number, depth: number?): (string?, number)
	local clip = PoseData.clips[name]
	if not clip then
		return nil, 0
	end
	local keys = clip.keys
	local dur = keys[#keys][1]
	if clip.loop then
		return name, t % math.max(dur, 1e-3)
	end
	if t >= dur and clip.after and (depth or 0) < 4 then
		return resolve(clip.after, t - dur, (depth or 0) + 1)
	end
	return name, math.min(t, dur)
end

local function evalClip(name: string, t: number)
	local power = THROW_POWER[name]
	if power then
		local sample = NativeThrow.SampleAngles(t,power)
		for _,j in JOINTS do
			local value = sample[j] or ZERO
			local result = poseOut[j]
			result[1],result[2],result[3] = math.deg(value[1]),math.deg(value[2]),math.deg(value[3])
		end
		local root = sample.root or ZERO
		poseOut.root[1],poseOut.root[2],poseOut.root[3] = root[1],root[2],root[3]
		return
	end
	local keys = PoseData.clips[name].keys
	for i = 1, #keys - 1 do
		local a, b = keys[i], keys[i + 1]
		if t <= b[1] then
			local u = (t - a[1]) / math.max(b[1] - a[1], 1e-3)
			blendInto(PoseData.poses[a[2]], PoseData.poses[b[2]], smooth(u))
			return
		end
	end
	local last = PoseData.poses[keys[#keys][2]]
	blendInto(last, last, 0)
end

local function clipOf(rig: Rig): (string?, number)
	if rig.char == player.Character then
		if not localClip then
			return nil, 0
		end
		return resolve(localClip, os.clock() - localT0)
	end
	local pose = rig.char:GetAttribute("Pose")
	if type(pose) ~= "string" then
		return nil, 0
	end
	local t0 = rig.char:GetAttribute("PoseT")
	local t = workspace:GetServerTimeNow() - (type(t0) == "number" and t0 or 0)
	return resolve(pose, math.max(t, 0))
end

local function findTool(char: Model): Tool?
	for _, c in char:GetChildren() do
		if c:IsA("Tool") and c:GetAttribute("Spear") then
			return c
		end
	end
	return nil
end

local function setToolHidden(rig: Rig, hidden: boolean)
	local tool = findTool(rig.char)
	if hidden and tool then
		if rig.tool ~= tool then
			rig.tool = tool
			for _, d in tool:GetDescendants() do
				if d:IsA("BasePart") then
					d.LocalTransparencyModifier = 1
				end
			end
		end
	elseif not hidden and rig.tool then
		for _, d in rig.tool:GetDescendants() do
			if d:IsA("BasePart") then
				d.LocalTransparencyModifier = 0
			end
		end
		rig.tool = nil
	end
end

local function dropSpear(rig: Rig)
	if rig.spear then
		rig.spear:Destroy()
		rig.spear = nil
		rig.spearId = nil
	end
end

-- Копия копья для руки/полёта (без коллизий)
function Animator.spearModel(id: string?): Model?
	local authored = NativeFactory.Create(id or "stick")
	if authored then return authored end
	local folder = RS:FindFirstChild("Assets") and RS.Assets:FindFirstChild("Spears")
	local tpl = folder and (folder:FindFirstChild(id or "stick") or folder:FindFirstChild("stick"))
	if not tpl or not tpl:IsA("Model") then
		return nil
	end
	local m = tpl:Clone()
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.CastShadow = false
		end
	end
	return m
end

-- CFrame копья: хват (Grip, y = −1.5 от центра древка) в точке grip, остриё по dir
function Animator.spearCF(grip: Vector3, dir: Vector3): CFrame
	local up = dir.Unit
	local side = up:Cross(Vector3.yAxis)
	if side.Magnitude < 1e-3 then
		side = Vector3.xAxis
	end
	side = side.Unit
	local back = side:Cross(up)
	return CFrame.fromMatrix(grip + up * 1.5, side, up, back)
end

local function register(char: Model)
	local hum = char:WaitForChild("Humanoid", 10)
	if not hum or not hum:IsA("Humanoid") or hum.RigType ~= Enum.HumanoidRigType.R15 then
		return
	end
	local motors: { [string]: Motor6D | AnimationConstraint } = {}
	local t0 = os.clock()
	while os.clock() - t0 < 10 do
		local missing = false
		for _, j in JOINTS do
			if not motors[j] then
				local m = char:FindFirstChild(j, true)
				if m and (m:IsA("Motor6D") or m:IsA("AnimationConstraint")) then
					motors[j] = m
				else
					missing = true
				end
			end
		end
		if not missing then
			break
		end
		task.wait(0.25)
	end
	if not char.Parent then
		return
	end
	rigs[char] = { char = char, hum = hum, motors = motors, cur = {}, active = false, spear = nil, spearId = nil, tool = nil }
	char.AncestryChanged:Connect(function()
		if not char:IsDescendantOf(workspace) then
			local rig = rigs[char]
			if rig then
				dropSpear(rig)
			end
			rigs[char] = nil
		end
	end)
end

local function watchPlayer(p: Player)
	p.CharacterAdded:Connect(function(c)
		if p == player then
			localClip = nil
		end
		task.spawn(register, c)
	end)
	if p.Character then
		task.spawn(register, p.Character)
	end
end
Players.PlayerAdded:Connect(watchPlayer)
for _, p in Players:GetPlayers() do
	watchPlayer(p)
end

-- Суставы: после стандартных анимаций, до физики
RunService.PreSimulation:Connect(function(dt)
	local a = 1 - math.exp(-dt * 20)
	for _, rig in rigs do
		local clip, t = clipOf(rig)
		if clip and PoseData.clips[clip] then
			if not rig.active then
				rig.active = true
				rig.cur = {}
			end
			evalClip(clip, t)
			local s = math.clamp(rig.hum.HipHeight / 2, 0.5, 2)
			for _, j in JOINTS do
				local m = rig.motors[j]
				if m then
					local target = poseOut[j]
					local c = rig.cur[j]
					if not c then
						c = { target[1], target[2], target[3] }
						rig.cur[j] = c
					end
					-- 360° ≡ 0°: сглаживаем по кратчайшей дуге (броски с разворотом)
					c[1] += wrap(target[1] - c[1]) * a
					c[2] += wrap(target[2] - c[2]) * a
					c[3] += wrap(target[3] - c[3]) * a
					local cf = CFrame.fromEulerAnglesYXZ(math.rad(c[1]), math.rad(c[2]), math.rad(c[3]))
					if j == "Root" then
						local r = rig.cur.root
						local rt = poseOut.root
						if not r then
							r = { rt[1], rt[2], rt[3] }
							rig.cur.root = r
						end
						r[1] += (rt[1] - r[1]) * a
						r[2] += (rt[2] - r[2]) * a
						r[3] += (rt[3] - r[3]) * a
						cf = CFrame.new(r[1] * s, r[2] * s, r[3] * s) * cf
					end
					m.Transform = cf
				end
			end
		elseif rig.active then
			rig.active = false
			rig.cur = {}
			dropSpear(rig)
			setToolHidden(rig, false)
		end
	end
end)

-- Копьё в руке (после физики, чтобы рука уже стояла на месте)
RunService.PreRender:Connect(function()
	for char, rig in rigs do
		local clip, t = clipOf(rig)
		local inHand = false
		if clip then
			local c = PoseData.clips[clip]
			inHand = HOLD[clip] == true and (c.release == nil or t < c.release)
			if rig.char == player.Character and holdOverride ~= nil then
				inHand = holdOverride
			end
		end
		if not clip and findTool(char) then inHand=true end
		if clip or inHand then
			setToolHidden(rig, true)
		elseif rig.tool then
			setToolHidden(rig, false)
		end
		local hand = char:FindFirstChild("RightHand") :: BasePart?
		local torso = (char:FindFirstChild("UpperTorso") or char:FindFirstChild("HumanoidRootPart")) :: BasePart?
		if inHand and hand and torso then
			local id = char:GetAttribute("SpearId")
			id = type(id) == "string" and id or "stick"
			if rig.spear and rig.spearId ~= id then
				dropSpear(rig)
			end
			if not rig.spear then
				rig.spear = Animator.spearModel(id :: string)
				rig.spearId = id :: string
				if rig.spear then
					rig.spear.Parent = spearsFolder
				end
			end
			local sp = rig.spear
			if sp then
				local fwd = torso.CFrame.LookVector
				local dir
				if clip == "Hide" then
					dir = (Vector3.yAxis * 0.95 + fwd * 0.3).Unit
				else
					dir = (fwd + Vector3.yAxis * 0.16).Unit
				end
				if sp:GetAttribute("V15Spear") and (THROW_POWER[clip] or not clip) then
					local orientation = if THROW_POWER[clip] then CFrame.Angles(math.pi,0,0) else CFrame.identity
					sp:PivotTo(NativeFactory.AtGrip(sp,hand.CFrame*CFrame.new(.02,-.1,-.07)*orientation))
				else
					sp:PivotTo(Animator.spearCF(hand.Position - dir * 0.2, dir))
				end
			end
		elseif rig.spear then
			dropSpear(rig)
		end
	end
end)

-- Своя поза: сразу локально + остальным через сервер
function Animator.play(clip: string?, silent: boolean?)
	if clip and not PoseData.clips[clip] then
		return
	end
	localClip = clip
	localT0 = os.clock()
	if not silent then
		PoseEv:FireServer(clip)
	end
end

function Animator.stop()
	Animator.play(nil)
end

function Animator.current(): (string?, number)
	if not localClip then
		return nil, 0
	end
	return resolve(localClip, os.clock() - localT0)
end

function Animator.release(clip: string): number
	local c = PoseData.clips[clip]
	return c and c.release or 0.2
end

function Animator.setHold(on: boolean?)
	holdOverride = on
end

function Animator.handPosition(char: Model?): Vector3?
	local hand = char and char:FindFirstChild("RightHand") :: BasePart?
	return hand and hand.Position or nil
end

-- Копьё из руки (для старта полёта): CFrame и id
function Animator.handSpearCF(char: Model?): CFrame?
	local rig = char and rigs[char]
	if rig and rig.spear then
		return rig.spear:GetPivot()
	end
	return nil
end

return Animator
