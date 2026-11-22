-- StarterPlayerScripts/Client/Dialog.luau
-- Диалоги NPC. V84: окно собрано из картинок (рама, рамка портрета, плашка реплики, табличка имени, кнопки),
-- реплики идут по порядку: приветствие, задание этого NPC, подсказка по прогрессу игрока, дальше советы по кругу.
-- Клик по плашке реплики или «Next»: допечатать текст сразу, следующий клик — следующая реплика.
local RS = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local UI = require(script.Parent.UIKit)
local Sfx = require(script.Parent.Sfx)
local Hud = require(script.Parent.Hud)
local Backend = require(script.Parent.Backend)
local Menus = require(script.Parent.Menus)
local NativeVendors = require(script.Parent.NativeVendors)

local Dialog = {}
local open: Frame? = nil
local lineIdx: { [string]: number } = {}
local greeted: { [string]: boolean } = {}
local activeVendor: Instance? = nil
local vendorRoles={smith="npc0",trainer="npc1",armorer="npc2",merchant="npc3",tracker="npc4",herbalist="npc5",hunter="npc6"}

local W, H = 880, 270
local LEFT = 222 -- левый край текста и кнопок (правее портрета и хвостика плашки)
local INK = Color3.fromRGB(74, 48, 28) -- текст на кремовой плашке
local INK_DIM = Color3.fromRGB(150, 118, 84)
local GOLD = Color3.fromRGB(255, 205, 70)

-- Картинки окна: свои (лист 7, если загружен) или из общих листов. { ключ, срез, масштаб среза }
local function pick(own: string, ownSlice: any, ownScale: number?, fallback: string, slice: any, scale: number?): { any }
	if UI.ART[own] then
		return { own, ownSlice, ownScale }
	end
	return { fallback, slice, scale }
end
local A_PANEL = pick("dlg_panel", 110, 0.8, "panel_quests", 58, 0.75)
local A_FACE = pick("dlg_portrait", nil, nil, "card_7", 34, 0.8)
local A_SPEECH = pick("dlg_speech", { 80, 0, 50, 0 }, nil, "row_cream", 26, 0.9) -- без масштаба: высота делится пополам (UI.artApply)
local A_NAME = pick("dlg_name", { 100, 0, 40, 0 }, nil, "sign_wood", { 60, 0, 60, 0 }, nil)
local HAS_NEXT_ART = UI.ART["dlg_next"] ~= nil
local OWN_FACE = UI.ART["dlg_portrait"] ~= nil
local OWN_SPEECH = UI.ART["dlg_speech"] ~= nil
local OWN_NAME = UI.ART["dlg_name"] ~= nil

-- Кнопки дела: { подпись, картинка кнопки, иконка, действие }
local ACTIONS: { [string]: { { any } } } = {
	hunter = { { "Quests", "btn_blue", "ic_quests", Menus.quests } },
	herbalist = { { "Potions", "btn_purple", "ic_potion", Menus.potions }, { "Quests", "btn_blue", "ic_quests", Menus.quests } },
	tracker = { { "Collection", "btn_purple", "ic_deer", Menus.index }, { "Quests", "btn_blue", "ic_quests", Menus.quests } },
	armorer = { { "Spears", "btn_blue", "ic_spear", Menus.spears } },
	merchant = { { "Market", "btn_yellow", "ic_sell", Menus.market } },
	smith = { { "Forge", "btn_orange", "st_forge", Menus.forge } },
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

---------------------------------------------------------------------
-- Реплики по прогрессу игрока (только чтение Backend.data)
---------------------------------------------------------------------
-- задание этого NPC: готовое к сдаче важнее того, что ещё в работе
local function questOf(npc: string): (any, any)
	local d = Backend.data
	local best, bestSt = nil, nil
	if not d or type(d.quests) ~= "table" then
		return nil, nil
	end
	for id, st in d.quests do
		local q = Config.QUEST_BY_ID[id]
		if q and q.npc == npc and type(st) == "table" and not st.claimed then
			if st.done then
				return q, st
			end
			if not best or q.index < best.index then
				best, bestSt = q, st
			end
		end
	end
	return best, bestSt
end

local function questLine(q: any, st: any): string
	if st.done then
		return "You did it: " .. q.title .. "! Take your reward, you earned it."
	end
	local p = math.min(tonumber(st.p) or 0, q.goal)
	return "I have a job for you. " .. q.title .. ": " .. q.text .. ". So far: " .. Num.short(p) .. " of " .. Num.short(q.goal) .. "."
end

local HINTS: { [string]: (d: any) -> string? } = {
	tracker = function(d)
		-- как в DemoServer: Сила × дальность копья в руках (с ковкой), не дальше края мира (V88); зелья и питомцы не учитываем
		local lvl = type(d.spears) == "table" and tonumber(d.spears[d.spear]) or 0
		local spearRange = Config.spearStats(d.spear, lvl).range
		local cap = Config.spearReach(d.spear)
		local raw = Config.range(tonumber(d.power) or 1) * spearRange
		local reach = math.min(raw, cap)
		local z = Config.zoneFor(reach)
		local zone = Config.ZONES[z]
		local nxt = Config.ZONES[z + 1]
		if not zone then
			return nil
		end
		-- V88: потолка полёта нет, но копьё берёт зверей только до своей зоны (Config.spearMaxZone): дальше они уходят
		local catchZ = Config.spearMaxZone(d.spear)
		if z > catchZ then
			local takes = Config.ZONES[catchZ]
			return "With this spear, a full throw reaches about the " .. zone.name .. ", but it only takes animals up to the " .. takes.name .. ". Farther out they get away: buy a better spear."
		end
		if not nxt then
			return "With this spear, a full throw reaches the " .. zone.name .. ". There is nothing beyond it but the volcano."
		end
		-- сколько Силы нужно, чтобы долететь до следующей зоны, а если копьё дальше не берёт, то до края своей зоны
		local atEdge = z >= catchZ
		local target = if atEdge then zone.to - 0.01 else nxt.from
		if raw >= target then
			return "You are strong enough: this spear takes animals up to the " .. zone.name .. ". Buy a better spear to hunt in the " .. nxt.name .. "."
		end
		local L = tonumber(d.strLvl) or 1
		local guard = 0
		while Config.range(Config.strengthOf(L)) * spearRange < target and guard < 5000 do
			L += 1
			guard += 1
		end
		local need = Config.strengthOf(L)
		-- со слабым копьём даже максимальная Сила не долетает до цели
		if Config.range(need) * spearRange < target - 0.5 then
			return "With this spear, a full throw reaches about the " .. zone.name .. ". Even maximum Strength will not carry it further: buy a better spear."
		end
		if not atEdge then
			return "With this spear, a full throw reaches about the " .. zone.name .. ". Around " .. Num.short(need) .. " Strength will carry it into the " .. nxt.name .. "."
		end
		return "With this spear, a full throw reaches about the " .. zone.name .. ". Around " .. Num.short(need) .. " Strength will carry it to the far end of this zone."
	end,
	armorer = function(d)
		local coins = tonumber(d.coins) or 0
		for _, s in Config.SPEARS do
			if type(d.spears) == "table" and d.spears[s.id] == nil and (s.price or 0) > 0 then
				if coins >= s.price then
					return "You can afford the " .. s.name .. " right now: " .. Num.short(s.price) .. " coins."
				end
				return "Next on the rack is the " .. s.name .. " for " .. Num.short(s.price) .. " coins. You need " .. Num.short(s.price - coins) .. " more."
			end
		end
		return "You own every spear on my rack. I have nothing left to teach you."
	end,
	merchant = function(d)
		local n = if type(d.items) == "table" then #d.items else 0
		if n == 0 then
			return "Your bag is empty. Come back with a catch and I will pay on the spot."
		end
		return "I see " .. n .. (if n == 1 then " catch" else " catches") .. " in your bag. Open the Market and I will weigh them."
	end,
	smith = function(d)
		local s = Config.SPEAR_BY_ID[d.spear]
		local lvl = type(d.spears) == "table" and tonumber(d.spears[d.spear]) or 0
		if not s then
			return nil
		end
		if lvl >= Config.FORGE.maxLevel then
			return "Your " .. s.name .. " is forged as far as it goes. Fine work, if I say so myself."
		elseif lvl >= Config.FORGE.freeMax then
			return "Your " .. s.name .. " is at forge level " .. lvl .. " of " .. Config.FORGE.maxLevel .. ". The last levels need the Master Smith pass from the Shop."
		end
		return "Your " .. s.name .. " is at forge level " .. lvl .. " of " .. Config.FORGE.maxLevel .. "."
	end,
	hunter = function(d)
		local n, ready = 0, 0
		if type(d.quests) == "table" then
			for id, st in d.quests do
				if Config.QUEST_BY_ID[id] and type(st) == "table" and not st.claimed then
					n += 1
					if st.done then
						ready += 1
					end
				end
			end
		end
		if n == 0 then
			return "Every job on the board is done. You are a forest legend!"
		elseif ready > 0 then
			return ready .. (if ready == 1 then " job is" else " jobs are") .. " finished and waiting for you. Open Quests to collect."
		end
		return "There " .. (if n == 1 then "is 1 job" else "are " .. n .. " jobs") .. " on the board right now."
	end,
}

---------------------------------------------------------------------
-- Окно
---------------------------------------------------------------------
local function artBtn(key: string, w: number, h: number, text: string, icon: string?, order: number, fn: () -> ()): ImageButton
	local b = UI.artButton(key, { Size = UDim2.fromOffset(w, h), LayoutOrder = order, Slice = { 30, 0, 30, 0 }, SliceScale = h / UI.artSize(key).Y, ZIndex = 5 }, fn)
	local row = Instance.new("Frame")
	row.Name = "Row"
	row.BackgroundTransparency = 1
	row.Size = UDim2.fromScale(1, 1)
	row.ZIndex = 6
	row.Parent = b
	UI.list(Enum.FillDirection.Horizontal, 6, Enum.HorizontalAlignment.Center, Enum.VerticalAlignment.Center).Parent = row
	if icon and UI.ART[icon] then
		UI.art(icon, { Size = UDim2.fromOffset(h - 20, h - 20), Fit = true, LayoutOrder = 1, ZIndex = 7, Parent = row })
	end
	UI.label({ Name = "Label", Text = text, TextSize = 21, Size = UDim2.fromOffset(10, h - 8), AutoX = true, LayoutOrder = 2, ZIndex = 7, Parent = row })
	return b
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
	local f = Instance.new("Frame")
	f.Name = "Dialog"
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromOffset(W, H)
	f.AnchorPoint = Vector2.new(0.5, 1)
	f.Position = UDim2.new(0.5, 0, 1, -22)
	f.ZIndex = 30
	f.Parent = UI.win
	open = f
	local sc = Instance.new("UIScale")
	sc.Scale = 0.4
	sc.Parent = f
	UI.tween(sc, 0.28, { Scale = 1 }, Enum.EasingStyle.Back)
	Sfx.play("open")
	UI.art(A_PANEL[1], { Name = "Frame", Size = UDim2.new(1, 12, 1, 12), Position = UDim2.fromOffset(-6, -6), Slice = A_PANEL[2], SliceScale = A_PANEL[3], ZIndex = 1, Parent = f })

	-- портрет: рамка-картинка, внутри цвет NPC и сам персонаж
	local face = UI.art(A_FACE[1], { Name = "Portrait", Size = UDim2.fromOffset(160, 160), Position = UDim2.fromOffset(38, 40), Slice = A_FACE[2], SliceScale = A_FACE[3], ZIndex = 2, Parent = f })
	local inner = Instance.new("Frame")
	inner.Name = "Inner"
	inner.BorderSizePixel = 0
	inner.ClipsDescendants = true
	-- окно своей рамки (небо с травой) занимает 22..138 из 160; у запасной карточки поля по 14
	inner.Size = if OWN_FACE then UDim2.fromOffset(116, 116) else UDim2.new(1, -28, 1, -28)
	inner.Position = if OWN_FACE then UDim2.fromOffset(22, 22) else UDim2.fromOffset(14, 14)
	inner.ZIndex = 3
	if OWN_FACE then
		inner.BackgroundTransparency = 1 -- на своей рамке уже нарисованы небо и трава
	else
		inner.BackgroundColor3 = info.color
		UI.gradient(Color3.new(1, 1, 1), Color3.fromRGB(200, 205, 215), 90).Parent = inner
	end
	UI.corner(12).Parent = inner
	inner.Parent = face
	local assets=RS:FindFirstChild("Assets")
	local vendorLibrary=assets and assets:FindFirstChild("V11Vendors")
	local portrait=(vendorLibrary and vendorRoles[npc] and vendorLibrary:FindFirstChild(vendorRoles[npc])) or model
	if portrait and portrait:IsA("Model") then
		local ok, vp = pcall(UI.viewport, portrait, nil, math.rad(180), 0)
		if ok and vp then
			vp.ZIndex = 4
			vp.Parent = inner
			local cam = vp.CurrentCamera
			if cam then
				-- ближе к лицу
				local _, size = portrait:GetBoundingBox()
				cam.CFrame = CFrame.lookAt(Vector3.new(0, size.Y * 0.3, -size.Y * 0.9), Vector3.new(0, size.Y * 0.28, 0))
			end
		end
	end

	-- табличка имени над рамой и подпись роли под портретом
	local nameW = math.clamp((if OWN_NAME then 116 else 96) + (utf8.len(info.name) or #info.name) * 17, 200, 380)
	local plate = UI.art(A_NAME[1], { Name = "NamePlate", Size = UDim2.fromOffset(nameW, 56), Position = UDim2.fromOffset(LEFT - 14, -26), Slice = A_NAME[2], SliceScale = 56 / UI.artSize(A_NAME[1]).Y, ZIndex = 6, Parent = f })
	UI.label({ Name = "Name", Text = info.name, TextSize = 30, Size = UDim2.new(1, if OWN_NAME then -56 else -36, 1, -6), Position = UDim2.fromOffset(if OWN_NAME then 40 else 18, 0), ZIndex = 7, Parent = plate })
	if type(info.role) == "string" then
		UI.label({ Name = "Role", Text = info.role, TextSize = 15, Color = info.color, Size = UDim2.fromOffset(176, 18), Position = UDim2.fromOffset(30, 206), Scaled = true, MaxSize = 15, ZIndex = 3, Parent = f })
	end

	-- плашка реплики
	local speech = Instance.new("ImageButton")
	speech.Name = "Speech"
	speech.AutoButtonColor = false
	speech.BackgroundTransparency = 1
	-- у своей плашки слева хвостик облачка: она начинается от портрета, текст сдвинут правее хвостика
	local speechX = if OWN_SPEECH then LEFT - 24 else LEFT
	speech.Size = UDim2.new(1, -speechX - 38, 0, 112)
	speech.Position = UDim2.fromOffset(speechX, 40)
	speech.ZIndex = 2
	UI.artApply(speech, A_SPEECH[1], A_SPEECH[2], A_SPEECH[3] or 112 / UI.artSize(A_SPEECH[1]).Y)
	speech.Parent = f
	local text = UI.label({ Name = "Text", Text = "", TextSize = 23, Color = INK, Stroke = 0, Size = UDim2.new(1, if OWN_SPEECH then -66 else -40, 1, -24), Position = UDim2.fromOffset(if OWN_SPEECH then 44 else 22, 11), XAlign = Enum.TextXAlignment.Left, YAlign = Enum.TextYAlignment.Top, Wrap = true, ZIndex = 3, Parent = speech })
	local pageL = UI.label({ Name = "Page", Text = "", TextSize = 14, Color = INK_DIM, Stroke = 0, Size = UDim2.fromOffset(60, 16), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -44, 1, -9), XAlign = Enum.TextXAlignment.Right, ZIndex = 3, Parent = speech })
	-- значок «дальше»: появляется, когда реплика допечатана, и покачивается
	local more: GuiObject
	if HAS_NEXT_ART then
		more = UI.art("dlg_next", { Name = "More", Size = UDim2.fromOffset(24, 24), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -16, 1, -10), Fit = true, ZIndex = 4, Parent = speech })
	else
		more = UI.label({ Name = "More", Text = "▼", TextSize = 18, Color = GOLD, Stroke = 2, Size = UDim2.fromOffset(24, 24), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -16, 1, -10), ZIndex = 4, Parent = speech })
	end
	more.Visible = false
	task.spawn(function()
		local t = 0
		while open == f do
			t += task.wait()
			more.Position = UDim2.new(1, -16, 1, -10 + math.sin(t * 6) * 3)
		end
	end)

	-- печать по буквам: новый вызов отменяет прошлый (gen), повторный клик допечатывает сразу
	local gen = 0
	local typing = false
	local function typeText(s: string)
		gen += 1
		local my = gen
		typing = true
		more.Visible = false
		text.Text = s
		text.MaxVisibleGraphemes = 0
		local n = utf8.len(s) or #s
		task.spawn(function()
			for i = 1, n do
				if gen ~= my or open ~= f then
					return
				end
				text.MaxVisibleGraphemes = i
				if i % 3 == 0 then
					if Sfx.has("blip") then
						Sfx.play("blip", nil, 0.16)
					else
						Sfx.play("hover", 1.4 + (i % 5) * 0.05, 0.12)
					end
				end
				task.wait(0.018)
			end
			if gen == my and open == f then
				text.MaxVisibleGraphemes = -1
				typing = false
				more.Visible = true
			end
		end)
	end
	local function finishTyping()
		gen += 1
		typing = false
		text.MaxVisibleGraphemes = -1
		more.Visible = true
	end

	-- очередь: приветствие, задание, подсказка; потом советы по кругу
	local d = Backend.data
	local queue: { string } = {}
	if not greeted[npc] and type(info.greet) == "table" and #info.greet > 0 then
		table.insert(queue, info.greet[1])
	elseif type(info.greet) == "table" and #info.greet > 1 then
		table.insert(queue, info.greet[math.random(2, #info.greet)])
	end
	greeted[npc] = true
	local q, st = questOf(npc)
	if q and st then
		table.insert(queue, questLine(q, st))
	end
	local hint = HINTS[npc]
	if hint and d then
		local ok, line = pcall(hint, d)
		if ok and type(line) == "string" then
			table.insert(queue, line)
		end
	end
	local qi = 0
	local tips: { string } = info.lines or {}
	local function nextLine()
		if qi < #queue then
			qi += 1
			pageL.Text = ""
			typeText(queue[qi])
		elseif #tips > 0 then
			local idx = (lineIdx[npc] or 0) % #tips + 1
			lineIdx[npc] = idx
			pageL.Text = "Tip " .. idx .. " / " .. #tips
			typeText(tips[idx])
		end
	end
	local function advance()
		if typing then
			finishTyping()
		else
			nextLine()
		end
	end
	speech.Activated:Connect(advance)
	nextLine()

	-- кнопки: награда за готовое задание, дела NPC, «Next». Худший случай: 124 + 150 + 150 + 118 и три зазора по 8 = 566 из 620
	local bar = Instance.new("Frame")
	bar.Name = "Buttons"
	bar.BackgroundTransparency = 1
	bar.Size = UDim2.new(1, -LEFT - 38, 0, 52)
	bar.Position = UDim2.new(0, LEFT, 1, -92)
	bar.ZIndex = 4
	bar.Parent = f
	UI.list(Enum.FillDirection.Horizontal, 8, Enum.HorizontalAlignment.Right, Enum.VerticalAlignment.Center).Parent = bar
	local order = 0
	if q and st and st.done then
		order += 1
		local rewardBtn: ImageButton
		rewardBtn = artBtn("btn_yellow", 124, 50, "Reward", "ic_coin", order, function()
			local ok, r = Backend.call("QuestClaim", q.id)
			if ok then
				rewardBtn.Visible = false
				-- задание сдано: реплики очереди про него и подсказка по прогрессу устарели
				for i = #queue, qi + 1, -1 do
					table.remove(queue, i)
				end
				Sfx.play("level")
				UI.confetti(40)
				Hud.banner("QUEST COMPLETE!", GOLD, Menus.rewardText(r), 2)
				pageL.Text = ""
				typeText("Great work! Here is your reward. Check Quests for your next challenge.")
			end
		end)
		rewardBtn.Parent = bar
	end
	for _, a in ACTIONS[npc] or {} do
		order += 1
		artBtn(a[2], 150, 50, a[1], a[3], order, function()
			Dialog.close()
			a[4]()
		end).Parent = bar
	end
	order += 1
	artBtn("btn_green", 118, 50, "Next ▶", nil, order, advance).Parent = bar

	local close = UI.artButton("btn_x", { Name = "Close", Size = UDim2.fromOffset(52, 51), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(1, -10, 0, -4), ZIndex = 8, Sound = "close" }, Dialog.close)
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
