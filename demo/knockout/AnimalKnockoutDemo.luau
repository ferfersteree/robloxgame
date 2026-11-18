-- demo/knockout/AnimalKnockoutDemo.luau
-- Показ «выбивания» животного из куста БЕЗ копья. Копия игры, в которой этот файл лежит на месте Client/Guide (туториала):
-- Main вызывает Guide.init() после запуска всех систем, и вместо подсказок туториала здесь крутится одна сцена:
--   куст шуршит → «?» → свечение растёт по цветам редкостей → (эпик и выше) темнеет небо, столб света, сердцебиение →
--   взрыв листвы и звёзд → створки куста раскрываются → зверь выходит и встаёт на место → карточка с цифрами.
-- Сама сцена не написана заново: это настоящий Client/Reveal игры (тот же код, что и после броска), только вместо
-- результата броска ему отдают «фальшивый» ответ демо-бэкенда, как делает зал Showroom по кнопке «Reveal».
-- Копьё, бросок и охота не участвуют.
--
-- Клавиши: N или стрелка вправо: следующий зверь; P или влево: предыдущий; R: повторить; 1-6: первый зверь этой редкости;
-- G: самая крупная особь (вкл/выкл); L: крутить одного зверя без конца (вкл/выкл); Пробел, Enter или E: закрыть карточку результата.
-- Фильтр (поле под подсказкой): впишите слова через пробел и нажмите Enter, и по кругу пойдут только подходящие звери:
-- имя или id (wolf, дракон не ищется, имена английские), биом (zone 12), манера выхода (rise, leap, burst, swoop...),
-- жест (roar, spin, coil...), редкость (epic). Все слова должны подходить сразу. Пустое поле: снова все 150.
-- Текущий показ закрывается Пробелом (или идёт до конца), следующим будет первый зверь из фильтра.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")
local UserInputService = game:GetService("UserInputService")

local Guide = {}

local STAGE = Vector3.new(-60, 0.1, 60) -- где зверь остановится: ровная поляна у деревни, вокруг ничего нет
local VIEWER = STAGE + Vector3.new(0, 3, 30) -- откуда смотрит камера (игрок стоит здесь, камера сцены ближе к кусту)
local GAP = 6.6 -- пауза между показами: зверь стоит на месте ещё 6 секунд после карточки, новый куст не должен появиться раньше

local function makeLabel(): (TextLabel, TextBox)
	local gui = Instance.new("ScreenGui")
	gui.Name = "KnockoutDemoHelp"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 200
	gui.IgnoreGuiInset = true
	gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
	local l = Instance.new("TextLabel")
	l.BackgroundColor3 = Color3.fromRGB(10, 12, 30)
	l.BackgroundTransparency = 0.35
	l.AnchorPoint = Vector2.new(0, 0)
	l.Position = UDim2.fromOffset(12, 12)
	l.Size = UDim2.fromOffset(640, 56)
	l.Font = Enum.Font.GothamBold
	l.TextSize = 17
	l.TextWrapped = true
	l.TextXAlignment = Enum.TextXAlignment.Left
	l.TextColor3 = Color3.new(1, 1, 1)
	l.Text = ""
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, 10)
	pad.PaddingRight = UDim.new(0, 10)
	pad.Parent = l
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 10)
	corner.Parent = l
	l.Parent = gui
	local box = Instance.new("TextBox")
	box.Name = "Filter"
	box.BackgroundColor3 = Color3.fromRGB(30, 34, 70)
	box.BackgroundTransparency = 0.15
	box.Position = UDim2.fromOffset(12, 74)
	box.Size = UDim2.fromOffset(640, 34)
	box.Font = Enum.Font.Gotham
	box.TextSize = 16
	box.TextXAlignment = Enum.TextXAlignment.Left
	box.TextColor3 = Color3.new(1, 1, 1)
	box.PlaceholderColor3 = Color3.fromRGB(170, 175, 200)
	box.PlaceholderText = "Filter: name, id, zone 12, rise / leap / burst / swoop..., roar / spin..., epic. Enter applies, empty = all"
	box.ClearTextOnFocus = false
	box.Text = ""
	local bpad = Instance.new("UIPadding")
	bpad.PaddingLeft = UDim.new(0, 10)
	bpad.Parent = box
	local bcorner = Instance.new("UICorner")
	bcorner.CornerRadius = UDim.new(0, 10)
	bcorner.Parent = box
	box.Parent = gui
	return l, box
end

function Guide.init()
	task.spawn(function()
		local player = Players.LocalPlayer
		local Client = script.Parent
		local Config = require(RS:WaitForChild("Shared"):WaitForChild("Config"))
		local Backend = require(Client:WaitForChild("Backend"))
		local Reveal = require(Client:WaitForChild("Reveal"))
		local UI = require(Client:WaitForChild("UIKit"))
		while not Backend.data do
			task.wait(0.25)
		end
		task.wait(1.5)

		-- чистый кадр: без панелей игры и без интерфейса Roblox
		local hud = UI.root:FindFirstAncestorOfClass("ScreenGui")
		if hud then
			hud.Enabled = false
		end
		pcall(function()
			StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, false)
		end)
		local label, box = makeLabel()
		local Stage = require(RS:WaitForChild("V15Covers"):WaitForChild("Stage"))

		local all = Config.SPECIES
		local species: { any } = all
		local filterText = ""
		local firstOfRarity: { [number]: number } = {}
		local function rebuildRarity()
			table.clear(firstOfRarity)
			for i, sp in species do
				if not firstOfRarity[sp.rarity] then
					firstOfRarity[sp.rarity] = i
				end
			end
		end
		rebuildRarity()
		-- все слова фильтра должны найтись в имени, id, номере биома, манере выхода, жесте или названии редкости
		local function matches(sp: any, words: { string }): boolean
			local spec = Stage.Spec(sp.id)
			local rar = Config.RARITIES[sp.rarity]
			local hay = table.concat({ sp.id, string.lower(sp.name or ""), "zone " .. tostring(sp.zone), tostring(sp.zone), spec.fam, spec.flo, string.lower(rar and rar.name or "") }, " | ")
			for _, w in words do
				if not string.find(hay, w, 1, true) then
					return false
				end
			end
			return true
		end
		local pending: any = nil
		local giantMode = false -- клавиша G показывает самую тяжёлую (самую крупную) особь вида
		local loopOne = false -- клавиша L крутит одного и того же зверя
		local idx = 1
		local filterNote = ""
		box.FocusLost:Connect(function()
			local text = string.lower(box.Text)
			local words = {}
			for w in string.gmatch(text, "[^%s,]+") do
				table.insert(words, w)
			end
			local found = {}
			for _, sp in all do
				if matches(sp, words) then
					table.insert(found, sp)
				end
			end
			if #found == 0 then
				filterNote = "nothing matches '" .. box.Text .. "', still showing the previous list"
				return
			end
			species = found
			filterText = box.Text
			filterNote = ""
			idx = 1
			pending = "restart"
			rebuildRarity()
		end)
		UserInputService.InputBegan:Connect(function(input: InputObject, processed: boolean)
			if processed then
				return
			end
			local k = input.KeyCode
			if k == Enum.KeyCode.N or k == Enum.KeyCode.Right then
				pending = "next"
			elseif k == Enum.KeyCode.P or k == Enum.KeyCode.Left then
				pending = "prev"
			elseif k == Enum.KeyCode.R then
				pending = "replay"
			elseif k == Enum.KeyCode.G then
				giantMode = not giantMode
				pending = "replay"
			elseif k == Enum.KeyCode.L then
				loopOne = not loopOne
			else
				for r, code in ipairs({ Enum.KeyCode.One, Enum.KeyCode.Two, Enum.KeyCode.Three, Enum.KeyCode.Four, Enum.KeyCode.Five, Enum.KeyCode.Six }) do
					if k == code then
						pending = r
					end
				end
			end
		end)

		while true do
			-- игрок стоит на месте и не мешает кадру
			local char = player.Character
			local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			if hrp then
				hrp.Anchored = false
				char:PivotTo(CFrame.new(VIEWER))
				hrp.Anchored = true
			end
			idx = math.clamp(idx, 1, #species)
			local sp = species[idx]
			local rarity = Config.RARITIES[sp.rarity]
			local spec = Stage.Spec(sp.id)
			label.Text = string.format("%s · %s · zone %d · %s + %s  (%d of %d%s)\nN next · P previous · R replay · 1-6 rarity · G giant %s · L loop one %s · Space closes the card%s", sp.name, rarity and rarity.name or "?", sp.zone or 0, spec.fam, spec.flo, idx, #species, filterText ~= "" and (", filter: " .. filterText) or "", giantMode and "ON" or "off", loopOne and "ON" or "off", filterNote ~= "" and ("\n" .. filterNote) or "")
			Reveal.count = 0 -- без кнопки «Skip» и без ускоренного показа
			local ok, res = Backend.call("Demo", "fake", { sp = sp.id, mut = nil, m = Config.TIERS[math.min(#Config.TIERS, sp.rarity)].m })
			if ok and res then
				if giantMode and res.item then
					res.item.w = sp.wMax
				end
				local okPlay, err = pcall(Reveal.play, res, STAGE, { from = VIEWER, fake = true, pedestal = true })
				if not okPlay then
					warn("[KnockoutDemo] reveal failed for " .. sp.id .. ": " .. tostring(err))
					task.wait(1)
				end
			else
				warn("[KnockoutDemo] demo backend refused " .. sp.id)
				task.wait(1)
			end
			task.wait(GAP)
			if pending == "restart" then
				idx = 1
			elseif pending == "prev" then
				idx = (idx - 2) % #species + 1
			elseif pending == "replay" or (loopOne and pending == nil) then
				idx = idx
			elseif type(pending) == "number" then
				idx = firstOfRarity[pending] or idx
			else
				idx = idx % #species + 1
			end
			pending = nil
		end
	end)
end

return Guide
