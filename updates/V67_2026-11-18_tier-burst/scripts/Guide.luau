-- StarterPlayerScripts/Client/Guide.luau
-- Обучение: плашка с текущим шагом, светящаяся «нить» от игрока к цели и прыгающая стрелка над целью.
-- Шаги — Config.TUTORIAL (target: ambush | throw | market | armory | gym), прогресс — data.tutorial (1..N+1).
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local Config = require(RS.Shared.Config)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Fx = require(script.Parent.WorldFx)
local Activities = require(script.Parent.Activities)

local Guide = {}

local player = Players.LocalPlayer
local map = workspace:WaitForChild("Map")
local C = Theme.C
local N = #Config.TUTORIAL

local step = 0
local promptCache: { [string]: BasePart } = {}

-- Плашка шага (сверху по центру)
local card = UI.panel({ Color = C.cyan, Size = UDim2.fromOffset(600, 58), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 86), Radius = 16, ZIndex = 20, Parent = UI.root })
card.Visible = false
local cardText = UI.label({ Text = "", TextSize = 22, Size = UDim2.new(1, -24, 1, 0), Position = UDim2.fromOffset(12, 0), ZIndex = 22, Rich = true, Wrap = true, Parent = card })

-- Цель: невидимая опора с аттачментом и стрелкой
local anchor = Instance.new("Part")
anchor.Name = "GuideTarget"
anchor.Anchored = true
anchor.CanCollide = false
anchor.CanQuery = false
anchor.CanTouch = false
anchor.Transparency = 1
anchor.Size = Vector3.new(0.2, 0.2, 0.2)
anchor.Parent = Fx.folder
local a1 = Instance.new("Attachment")
a1.Parent = anchor
local bb = Instance.new("BillboardGui")
bb.Size = UDim2.fromOffset(90, 110)
bb.StudsOffsetWorldSpace = Vector3.new(0, 3.5, 0)
bb.AlwaysOnTop = true
bb.LightInfluence = 0
bb.Enabled = false
bb.Parent = anchor
local arrow = UI.label({ Text = "⬇", TextSize = 64, Color = C.cyan, Size = UDim2.fromOffset(90, 70), Parent = bb })
local dist = UI.label({ Text = "", TextSize = 20, Size = UDim2.new(1, 0, 0, 26), Position = UDim2.fromOffset(0, 76), Parent = bb })

local beam = Instance.new("Beam")
beam.Attachment1 = a1
beam.Texture = Fx.TEX.sparkle
beam.TextureMode = Enum.TextureMode.Wrap
beam.TextureLength = 3
beam.TextureSpeed = 1.6
beam.Width0 = 0.9
beam.Width1 = 0.9
beam.FaceCamera = true
beam.LightEmission = 1
beam.LightInfluence = 0
beam.Segments = 24
beam.CurveSize0 = 3
beam.CurveSize1 = -3
beam.Color = ColorSequence.new(C.cyan, Color3.new(1, 1, 1))
beam.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.9), NumberSequenceKeypoint.new(0.15, 0.15), NumberSequenceKeypoint.new(1, 0.2) })
beam.Enabled = false
beam.Parent = anchor

local a0: Attachment? = nil
local function bindChar(c: Model)
	local root = c:WaitForChild("HumanoidRootPart", 10) :: BasePart?
	if root then
		local a = Instance.new("Attachment")
		a.Name = "GuideA0"
		a.Position = Vector3.new(0, -2.4, 0)
		a.Parent = root
		a0 = a
		beam.Attachment0 = a
	end
end
player.CharacterAdded:Connect(bindChar)
if player.Character then
	task.spawn(bindChar, player.Character)
end

local function findPrompt(actionId: string, label: string): BasePart?
	local c = promptCache[actionId]
	if c and c.Parent then
		return c
	end
	for _, d in map:GetDescendants() do
		if d:IsA("ProximityPrompt") and (d:GetAttribute("ActionId") == actionId or d.ActionText == label) and d.Parent and d.Parent:IsA("BasePart") then
			promptCache[actionId] = d.Parent :: BasePart
			return d.Parent :: BasePart
		end
	end
	return nil
end

local function myPlot(): Instance?
	local plots = map:FindFirstChild("Plots")
	if not plots then
		return nil
	end
	for _, p in plots:GetChildren() do
		if p:GetAttribute("OwnerId") == player.UserId then
			return p
		end
	end
	return nil
end

local function nearestAmbush(from: Vector3): BasePart?
	local best, bd = nil, math.huge
	local folder = map:FindFirstChild("Ambushes")
	if not folder then
		return nil
	end
	for _, m in folder:GetChildren() do
		local occ = m:GetAttribute("Occupant")
		local pr = m:FindFirstChild("Prompt") :: BasePart?
		if pr and (occ == nil or occ == player.UserId) then
			local d = (pr.Position - from).Magnitude
			if d < bd then
				best, bd = pr, d
			end
		end
	end
	return best
end

local function targetFor(kind: string, from: Vector3): BasePart?
	if kind == "ambush" or kind == "throw" then
		return nearestAmbush(from)
	elseif kind == "market" then
		return findPrompt("sell", "Sell Parcels")
	elseif kind == "armory" then
		return findPrompt("armory", "Spear Shop")
	elseif kind == "gym" then
		local plot = myPlot()
		local gym = plot and plot:FindFirstChild("Gym")
		return gym and gym:FindFirstChild("Prompt") :: BasePart? or nil
	end
	return nil
end

local function setStep(s: number, live: boolean)
	if s == step then
		return
	end
	local prev = step
	step = s
	if s > N then
		bb.Enabled = false
		beam.Enabled = false
		if live and prev >= 1 then
			Sfx.play("win")
			UI.confetti(80)
			Hud.banner("TUTORIAL COMPLETE! 🎉", C.gold, "Find rare animals deeper in the forest", 2.6)
			cardText.Text = "🎉 Tutorial complete! Happy hunting!"
			UI.punch(card, 0.3)
			task.delay(3, function()
				if step > N then
					card.Visible = false
				end
			end)
		else
			card.Visible = false
		end
		return
	end
	if s < 1 then
		card.Visible = false
		return
	end
	cardText.Text = string.format("📍 <b>Step %d/%d</b> · %s", s, N, Config.TUTORIAL[s].text)
	if live and prev >= 1 then
		Sfx.play("level", 1.2, 0.5)
		UI.punch(card, 0.35)
		UI.shine(card, 0.6)
	end
end

function Guide.init()
	Backend.onChange(function(d)
		if d then
			setStep(tonumber(d.tutorial) or 1, true)
		end
	end)
	local d = Backend.data
	if d then
		setStep(tonumber(d.tutorial) or 1, false)
	end
	task.spawn(function()
		local t = 0
		while true do
			t += task.wait(0.05)
			local show = step >= 1 and step <= N
			local mode = Activities.busy and "busy" or Hud.mode
			-- V67: на точке броска на экране только шкала заряда, карточку обучения не показываем
			card.Visible = (show and mode == "normal") or (step > N and card.Visible and mode == "normal")
			local c = player.Character
			local root = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
			local tgt = (show and root and mode == "normal") and targetFor(Config.TUTORIAL[step].target, root.Position) or nil
			if tgt and root then
				anchor.CFrame = CFrame.new(tgt.Position)
				local dd = (tgt.Position - root.Position).Magnitude
				dist.Text = math.floor(dd) .. " m"
				local near = dd < 9
				bb.Enabled = true
				beam.Enabled = not near and a0 ~= nil
				arrow.Position = UDim2.fromOffset(0, math.abs(math.sin(t * 4)) * -14)
			else
				bb.Enabled = false
				beam.Enabled = false
			end
		end
	end)
end

return Guide
