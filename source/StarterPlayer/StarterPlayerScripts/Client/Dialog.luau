-- StarterPlayerScripts/Client/Dialog.luau
-- Диалоги NPC: портрет, имя, текст печатается по буквам, «Дальше», кнопки дела (зелья, копья, задания…),
-- готовое задание этого NPC можно сдать прямо здесь.
local RS = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Config = require(RS.Shared.Config)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)
local Sfx = require(script.Parent.Sfx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Menus = require(script.Parent.Menus)
local NativeVendors = require(script.Parent.NativeVendors)

local Dialog = {}
local C = Theme.C
local open: Frame? = nil
local lineIdx: { [string]: number } = {}
local activeVendor: Instance? = nil
local vendorRoles={smith="npc0",trainer="npc1",armorer="npc2",merchant="npc3",tracker="npc4",herbalist="npc5",hunter="npc6"}

local ACTIONS: { [string]: { { any } } } = {
	hunter = { { "📜 Quests", C.cyan, Menus.quests } },
	herbalist = { { "🧪 Potions", C.pink, Menus.potions }, { "📜 Quests", C.cyan, Menus.quests } },
	tracker = { { "📖 Collection", C.purple, Menus.index }, { "📜 Quests", C.cyan, Menus.quests } },
	armorer = { { "🔱 Spears", C.blue, Menus.spears } },
	merchant = { { "💰 Market", C.gold, Menus.market } },
	smith = { { "🔨 Forge", C.orange, Menus.forge } },
}

function Dialog.close()
	if activeVendor then NativeVendors.react(activeVendor,"farewell");activeVendor=nil end
	if open then
		local f = open
		open = nil
		local sc = f:FindFirstChildOfClass("UIScale")
		if sc then
			UI.tween(sc, 0.15, { Scale = 0 })
		end
		task.delay(0.16, function()
			f:Destroy()
		end)
	end
end

local function typeText(label: TextLabel, text: string)
	label.Text = text
	label.MaxVisibleGraphemes = 0
	local n = utf8.len(text) or #text
	task.spawn(function()
		for i = 1, n do
			if label.Parent == nil then
				return
			end
			label.MaxVisibleGraphemes = i
			if i % 3 == 0 then
				if Sfx.has("blip") then
					Sfx.play("blip", nil, 0.16)
				else
					Sfx.play("hover", 1.4 + (i % 5) * 0.05, 0.12)
				end
			end
			task.wait(0.018)
		end
		label.MaxVisibleGraphemes = -1
	end)
end

function Dialog.open(npc: string, model: Instance?)
	Dialog.close()
	UI.closeWindow(true)
	local info = Config.NPC[npc]
	if not info then
		return
	end
	activeVendor=if model and model:GetAttribute("NativeSemanticWrapper") then model.Parent else model
	NativeVendors.react(activeVendor,"talk")
	local f = UI.panel({ Color = C.panel, Size = UDim2.fromOffset(820, 230), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -20), Radius = 22, LineThick = 4, ZIndex = 30, Parent = UI.win })
	open = f
	local sc = Instance.new("UIScale")
	sc.Scale = 0.4
	sc.Parent = f
	UI.tween(sc, 0.28, { Scale = 1 }, Enum.EasingStyle.Back)
	Sfx.play("open")
	-- портрет
	local face = UI.panel({ Color = info.color, Size = UDim2.fromOffset(170, 170), Position = UDim2.fromOffset(20, 30), Radius = 18, Parent = f })
	local assets=RS:FindFirstChild("Assets")
	local vendorLibrary=assets and assets:FindFirstChild("V11Vendors")
	local portrait=(vendorLibrary and vendorRoles[npc] and vendorLibrary:FindFirstChild(vendorRoles[npc])) or model
	if portrait and portrait:IsA("Model") then
		local ok, vp = pcall(UI.viewport, portrait, nil, math.rad(180), 0)
		if ok and vp then
			vp.Parent = face
			local cam = vp.CurrentCamera
			if cam then
				-- ближе к лицу
				local _, size = portrait:GetBoundingBox()
				cam.CFrame = CFrame.lookAt(Vector3.new(0, size.Y * 0.3, -size.Y * 0.9), Vector3.new(0, size.Y * 0.28, 0))
			end
		end
	end
	local name = UI.panel({ Color = info.color, Size = UDim2.fromOffset(10, 44), Position = UDim2.fromOffset(210, -18), Radius = 14, Parent = f })
	name.AutomaticSize = Enum.AutomaticSize.X
	UI.pad(16, 0).Parent = name
	UI.label({ Text = info.name, TextSize = 28, Size = UDim2.new(0, 10, 1, 0), AutoX = true, Parent = name })
	local text = UI.label({ Text = "", TextSize = 25, Size = UDim2.new(1, -240, 0, 110), Position = UDim2.fromOffset(212, 36), XAlign = Enum.TextXAlignment.Left, YAlign = Enum.TextYAlignment.Top, Wrap = true, Parent = f })
	local idx = lineIdx[npc] or 0
	local function nextLine()
		idx = idx % #info.lines + 1
		lineIdx[npc] = idx
		typeText(text, info.lines[idx])
	end
	nextLine()
	local bar = Instance.new("Frame")
	bar.BackgroundTransparency = 1
	bar.Size = UDim2.new(1, -240, 0, 58)
	bar.Position = UDim2.new(0, 212, 1, -74)
	bar.Parent = f
	UI.list(Enum.FillDirection.Horizontal, 10).Parent = bar
	local order = 0
	local function add(label: string, color: Color3, fn: () -> (), w: number?)
		order += 1
		local b = UI.button({ Text = label, TextSize = 21, Color = color, Size = UDim2.fromOffset(w or 170, 54), LayoutOrder = order }, fn)
		b.Parent = bar
	end
	-- готовое задание этого NPC
	local d = Backend.data
	for id, st in d.quests do
		local q = Config.QUEST_BY_ID[id]
		if q and q.npc == npc and st.done and not st.claimed then
			add("🎁 Reward", C.gold, function()
				local ok, r = Backend.call("QuestClaim", id)
				if ok then
					Sfx.play("level")
					UI.confetti(40)
					Hud.banner("QUEST COMPLETE!", C.gold, Menus.rewardText(r), 2)
					typeText(text, "Great work! Here is your reward. Check Quests for your next challenge.")
				end
			end, 160)
			break
		end
	end
	local acts: { any } = ACTIONS[npc] or {}
	for _, a in acts do
		add(a[1], a[2], function()
			Dialog.close()
			a[3]()
		end)
	end
	add("Next ▶", C.green, nextLine, 140)
	local close = UI.button({ Text = "✕", TextSize = 26, Color = C.red, Size = UDim2.fromOffset(48, 48), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(1, -6, 0, 6), Round = true, Sound = "close" }, Dialog.close)
	close.Parent = f
	-- уйти далеко — закрыть
	task.spawn(function()
		local player = game:GetService("Players").LocalPlayer
		local anchor = model and model:IsA("Model") and model:GetPivot().Position or nil
		while open == f do
			task.wait(0.3)
			local c = player.Character
			local hrp = c and c:FindFirstChild("HumanoidRootPart") :: BasePart?
			if anchor and hrp and (hrp.Position - anchor).Magnitude > 22 then
				Dialog.close()
			end
		end
	end)
end

UserInputService.InputBegan:Connect(function(i, gp)
	if not gp and open and i.KeyCode == Enum.KeyCode.Escape then
		Dialog.close()
	end
end)

return Dialog
