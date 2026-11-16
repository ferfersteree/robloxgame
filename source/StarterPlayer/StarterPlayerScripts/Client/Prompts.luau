-- StarterPlayerScripts/Client/Prompts.luau
-- Свои подсказки ProximityPrompt в стиле игры (FredokaOne, клавиша-«пузырь», полоса удержания,
-- на телефоне — нажимаемая плашка). Actions use stable ActionId attributes.
local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")

local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)

local Prompts = {}
local handlers: { [string]: (ProximityPrompt) -> () } = {}
local ACTION_TEXT: { [string]: string } = {
	hide = "Throw", sell = "Sell Parcels", armory = "Spear Shop", upgrade = "Upgrade Spear",
	talk = "Talk", quests = "Quests", reveal = "Reveal", demo = "Demo Throw",
	wrap = "Wrap Catch", train = "Train", inspect = "Inspect",
	lookout = "Climb", range = "Throw at Targets", course = "Start",
}
local ACTION_IDS: { [string]: string } = {}
for id, text in ACTION_TEXT do
	ACTION_IDS[id] = id
	ACTION_IDS[text] = id
end
local COLORS: { [string]: Color3 } = {
	hide = Theme.C.green, sell = Theme.C.gold, armory = Theme.C.blue,
	upgrade = Theme.C.orange, talk = Theme.C.cyan, quests = Theme.C.cyan,
	reveal = Theme.C.purple, demo = Theme.C.red,
	wrap = Theme.C.orange, train = Theme.C.red, inspect = Theme.C.blue,
	lookout = Theme.C.cyan, range = Theme.C.orange, course = Theme.C.green,
}

local player = Players.LocalPlayer
local pgui = player:WaitForChild("PlayerGui")

function Prompts.on(action: string, fn: (ProximityPrompt) -> ())
	handlers[ACTION_IDS[action] or action] = fn
end

function Prompts.idFor(action: string): string?
	return ACTION_IDS[action]
end

function Prompts.actionId(prompt: ProximityPrompt): string?
	local id = prompt:GetAttribute("ActionId")
	if type(id) == "string" and ACTION_TEXT[id] then
		return id
	end
	return ACTION_IDS[prompt.ActionText]
end

-- Interaction uses a stable ID, so changing the visible label cannot break it.
function Prompts.trigger(prompt: ProximityPrompt, who: Player?): boolean
	if who ~= nil and who ~= player then
		return false
	end
	local id = Prompts.actionId(prompt)
	local handler = id and handlers[id]
	if not handler then
		return false
	end
	Sfx.play("press")
	task.spawn(handler, prompt)
	return true
end

function Prompts.setEnabled(on: boolean)
	ProximityPromptService.Enabled = on
end

local function keyText(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType): string
	if inputType == Enum.ProximityPromptInputType.Touch then
		return "👆"
	elseif inputType == Enum.ProximityPromptInputType.Gamepad then
		return "X"
	end
	local k = prompt.KeyboardKeyCode
	return k == Enum.KeyCode.E and "E" or (UserInputService:GetStringForKeyCode(k) ~= "" and UserInputService:GetStringForKeyCode(k) or "E")
end

local function build(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType): () -> ()
	local color = COLORS[Prompts.actionId(prompt) or ""] or Theme.C.blue
	local s = UI.scale()
	local bb = Instance.new("BillboardGui")
	bb.Name = "SpearPrompt"
	bb.AlwaysOnTop = true
	bb.Size = UDim2.fromOffset(math.floor(300 * s), math.floor(84 * s))
	bb.StudsOffset = Vector3.new(0, 1.2, 0)
	bb.Adornee = prompt.Parent :: any
	bb.Active = true
	bb.Parent = pgui
	local btn = Instance.new("TextButton")
	btn.Text = ""
	btn.AutoButtonColor = false
	btn.BackgroundTransparency = 1
	btn.Size = UDim2.fromScale(1, 1)
	btn.Parent = bb
	local sc = Instance.new("UIScale")
	sc.Scale = 0.3
	sc.Parent = btn
	TweenService:Create(sc, TweenInfo.new(0.22, Enum.EasingStyle.Back), { Scale = 1 }):Play()
	local panel = UI.panel({ Color = Theme.C.panel, Size = UDim2.new(1, -math.floor(70 * s), 1, -math.floor(14 * s)), Position = UDim2.new(0, math.floor(60 * s), 0, math.floor(7 * s)), Radius = math.floor(14 * s), LineThick = 3, Parent = btn })
	panel.BackgroundTransparency = 0.1
	local key = UI.panel({ Color = color, Size = UDim2.fromOffset(math.floor(68 * s), math.floor(68 * s)), AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.new(0, 0, 0.5, 0), Radius = math.floor(34 * s), LineThick = 3, Parent = btn })
	key.ZIndex = 3
	UI.label({ Text = keyText(prompt, inputType), TextSize = math.floor(34 * s), Size = UDim2.fromScale(1, 1), ZIndex = 4, Parent = key })
	-- кольцо удержания (полоса снизу)
	local hold = Instance.new("Frame")
	hold.BackgroundColor3 = color
	hold.BorderSizePixel = 0
	hold.Size = UDim2.new(0, 0, 0, math.floor(6 * s))
	hold.Position = UDim2.new(0, math.floor(14 * s), 1, -math.floor(10 * s))
	hold.Parent = panel
	UI.corner(1, true).Parent = hold
	UI.label({ Text = prompt.ActionText, TextSize = math.floor(28 * s), Size = UDim2.new(1, -math.floor(26 * s), 0.6, 0), Position = UDim2.new(0, math.floor(18 * s), 0, 0), XAlign = Enum.TextXAlignment.Left, Scaled = true, MaxSize = math.floor(30 * s), Parent = panel })
	if prompt.ObjectText ~= "" then
		UI.label({ Text = prompt.ObjectText, TextSize = math.floor(18 * s), Color = Theme.C.dim, Size = UDim2.new(1, -math.floor(26 * s), 0.38, 0), Position = UDim2.new(0, math.floor(18 * s), 0.56, 0), XAlign = Enum.TextXAlignment.Left, Scaled = true, MaxSize = math.floor(18 * s), Stroke = 2, Parent = panel })
	end
	local conns: { RBXScriptConnection } = {}
	local holdTween: Tween? = nil
	table.insert(conns, prompt.PromptButtonHoldBegan:Connect(function()
		if prompt.HoldDuration > 0 then
			hold.Size = UDim2.new(0, 0, 0, hold.Size.Y.Offset)
			holdTween = TweenService:Create(hold, TweenInfo.new(prompt.HoldDuration, Enum.EasingStyle.Linear), { Size = UDim2.new(1, -math.floor(28 * s), 0, hold.Size.Y.Offset) })
			;(holdTween :: Tween):Play()
		end
		TweenService:Create(sc, TweenInfo.new(0.1), { Scale = 0.92 }):Play()
	end))
	table.insert(conns, prompt.PromptButtonHoldEnded:Connect(function()
		if holdTween then
			holdTween:Cancel()
		end
		hold.Size = UDim2.new(0, 0, 0, hold.Size.Y.Offset)
		TweenService:Create(sc, TweenInfo.new(0.15, Enum.EasingStyle.Back), { Scale = 1 }):Play()
	end))
	table.insert(conns, prompt.Triggered:Connect(function()
		UI.punch(key, 0.3)
	end))
	if inputType == Enum.ProximityPromptInputType.Touch or prompt.ClickablePrompt then
		table.insert(conns, btn.InputBegan:Connect(function(i)
			if i.UserInputType == Enum.UserInputType.Touch or i.UserInputType == Enum.UserInputType.MouseButton1 then
				prompt:InputHoldBegin()
			end
		end))
		table.insert(conns, btn.InputEnded:Connect(function(i)
			if i.UserInputType == Enum.UserInputType.Touch or i.UserInputType == Enum.UserInputType.MouseButton1 then
				prompt:InputHoldEnd()
			end
		end))
	end
	Sfx.play("hover")
	return function()
		for _, c in conns do
			c:Disconnect()
		end
		TweenService:Create(sc, TweenInfo.new(0.12), { Scale = 0 }):Play()
		task.delay(0.13, function()
			bb:Destroy()
		end)
	end
end

local function style(d: Instance)
	if d:IsA("ProximityPrompt") then
		local id = Prompts.actionId(d)
		if id then
			d:SetAttribute("ActionId", id)
			d.ActionText = ACTION_TEXT[id]
		end
		d.Style = Enum.ProximityPromptStyle.Custom
		d.RequiresLineOfSight = false
	end
end

function Prompts.init(root: Instance)
	for _, d in root:GetDescendants() do
		style(d)
	end
	root.DescendantAdded:Connect(style)
	ProximityPromptService.PromptShown:Connect(function(prompt, inputType)
		if prompt.Style ~= Enum.ProximityPromptStyle.Custom then
			return
		end
		local cleanup = build(prompt, inputType)
		local c: RBXScriptConnection? = nil
		c = prompt.PromptHidden:Connect(function()
			if c then
				c:Disconnect()
			end
			cleanup()
		end)
	end)
	ProximityPromptService.PromptTriggered:Connect(Prompts.trigger)
end

return Prompts
