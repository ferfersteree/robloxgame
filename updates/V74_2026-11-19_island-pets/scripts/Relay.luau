-- ServerScriptService/Server/Relay.luau
-- Пересылка того, что должны видеть все: позы, эффекты бросков/раскрытий, занятость дорожек зоны для кидания.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Net = require(RS.Shared.Net)
local Config = require(RS.Shared.Config)
local PoseData = require(RS.Shared.PoseData) :: any
local Cosmetics = require(script.Parent.Cosmetics)
local Util = require(RS.Shared.Util)

-- false: не менять материалы стартового острова (одна строка выключает весь проход)
local RESTYLE_MATERIALS = true

local Relay = {}

local PoseEv = Net.ev("Pose")
local FxEv = Net.ev("Fx")
local AmbushFn = Net.fn("Ambush")

-- антиспам: ведро токенов на игрока и канал
local buckets: { [Player]: { [string]: { n: number, t: number } } } = {}
local function allow(player: Player, chan: string, rate: number): boolean
	local b = buckets[player]
	if not b then
		b = {}
		buckets[player] = b
	end
	local now = os.clock()
	local s = b[chan]
	if not s then
		s = { n = rate, t = now }
		b[chan] = s
	end
	s.n = math.min(rate, s.n + (now - s.t) * rate)
	s.t = now
	if s.n < 1 then
		return false
	end
	s.n -= 1
	return true
end

-- Гантели в руках, пока поза Train/Lift
local function setDumbbells(player: Player, on: boolean)
	local char = player.Character
	if not char then
		return
	end
	local has = char:FindFirstChild("HeldDumbbell") ~= nil
	if on == has then
		return
	end
	if not on then
		for _, c in char:GetChildren() do
			if c.Name == "HeldDumbbell" then
				c:Destroy()
			end
		end
		return
	end
	local level = Cosmetics.dumbbellLevel(player)
	local tpl = RS.Assets:FindFirstChild("Dumbbell")
	for _, side in { "RightHand", "LeftHand" } do
		local hand = char:FindFirstChild(side) :: BasePart?
		if hand then
			local ok, built = pcall(Util.dumbbell, level)
			local m: Model? = ok and built or nil
			if not m and tpl and tpl:IsA("Model") then
				-- запасной путь: старый шаблон, перекрашенный
				local look = Config.DUMBBELL_LOOK[math.clamp(level, 1, #Config.DUMBBELL_LOOK)]
				m = tpl:Clone()
				for _, p in (m :: Model):GetDescendants() do
					if p:IsA("BasePart") and p:GetAttribute("Weight") then
						p.Color = look.color
						p.Material = look.material
					end
				end
			end
			if not m then
				continue
			end
			m.Name = "HeldDumbbell"
			-- новые модели уже нужного размера; у запасного шаблона прежний масштаб по уровню
			m:ScaleTo(if ok and built then 0.85 else Config.DUMBBELL_LOOK[math.clamp(level, 1, #Config.DUMBBELL_LOOK)].size * 0.8)
			local root = m.PrimaryPart
			if root then
				m:PivotTo(hand.CFrame * CFrame.new(0, -0.1, 0) * CFrame.Angles(0, math.rad(90), 0))
				Util.weldTo(root, m)
				root.Anchored = false
				root.Massless = true
				root.CanCollide = false
				local w = Instance.new("WeldConstraint")
				w.Part0 = hand
				w.Parent = root
				w.Part1 = root
				m.Parent = char
			else
				m:Destroy()
			end
		end
	end
end

PoseEv.OnServerEvent:Connect(function(player: Player, clip: any)
	if not allow(player, "pose", 12) then
		return
	end
	local char = player.Character
	if not char then
		return
	end
	if clip ~= nil and (type(clip) ~= "string" or not PoseData.clips[clip]) then
		return
	end
	char:SetAttribute("Pose", clip)
	char:SetAttribute("PoseT", workspace:GetServerTimeNow())
	setDumbbells(player, clip == "Train" or clip == "TrainRest" or clip == "Lift")
end)

-- V62: до какого момента (os.clock) эффекты игрока ещё не рассылаются после схода с одиночного места
local soloUntil: { [Player]: number } = {}

-- Эффекты: копируем только известные поля нужных типов
local FX_KINDS = { throw = true, reveal = true, crash = true, bounce = true, levelup = true, collect = true, tier = true }
local FIELDS = {
	tier = "number", spear = "string", from = "Vector3", to = "Vector3", t = "number", sp = "string",
	rarity = "number", mut = "string", pos = "Vector3", m = "number", lane = "number", escaped = "boolean", crashed = "boolean", sz = "number",
}
FxEv.OnServerEvent:Connect(function(player: Player, payload: any)
	if type(payload) ~= "table" or not FX_KINDS[payload.k] then
		return
	end
	if not allow(player, "fx", 8) then
		return
	end
	-- V62: броски, раскрытия и добыча игрока на одиночном месте другим не показываются
	if player:GetAttribute("Solo") or (soloUntil[player] or 0) > os.clock() then
		return
	end
	local out = { k = payload.k, by = player.UserId }
	for key, ty in FIELDS do
		local v = payload[key]
		if v ~= nil and typeof(v) == ty then
			if ty == "string" and #(v :: string) > 24 then
				continue
			end
			if ty == "number" and (v ~= v or math.abs(v :: number) > 1e7) then
				continue
			end
			out[key] = v
		end
	end
	for _, p in Players:GetPlayers() do
		if p ~= player then
			FxEv:FireClient(p, out)
		end
	end
end)

-- V36: зона для кидания (Workspace/Map/Ambushes/ThrowingGrounds). Одна зона, в ней несколько дорожек
-- (Stands/Stand1..N): на одной дорожке один игрок, остальные бросают рядом одновременно.
-- Занятость хранится атрибутами Occupant / OccupantName на самой дорожке, их видят все клиенты.
local ambushFolder = workspace:WaitForChild("Map"):WaitForChild("Ambushes")
local occupied: { [Player]: BasePart } = {}
local MAX_DISTANCE = 36 -- вход только вблизи зоны: V65 вход с любой точки пола (дальний угол ~27 от точки Prompt), остальное запас на лаг
local HOLD_DISTANCE = 9 -- V65: дальше этого от точки броска дольше HOLD_GRACE секунд Solo снимается (было 25)
local HOLD_GRACE = 3
local farSince: { [Player]: number } = {}

-- V64: одно место для броска. Из дорожек зоны остаётся одна и встаёт по центру (напротив входа); лампы занятости
-- и перегородки между дорожками убираются. Делается при старте сервера: в файле места дорожки лежат как были.
local function consolidateZone(zone: Instance)
	local stands = zone:FindFirstChild("Stands")
	if not stands then
		return
	end
	local keep: BasePart? = nil
	local sum, count = Vector3.zero, 0
	for _, s in stands:GetChildren() do
		if s:IsA("BasePart") and type(s:GetAttribute("Index")) == "number" then
			sum += s.Position
			count += 1
			if not keep or (s:GetAttribute("Index") :: number) < (keep:GetAttribute("Index") :: number) then
				keep = s
			end
		end
	end
	if not keep or count < 2 then
		return
	end
	local index = keep:GetAttribute("Index")
	for _, s in stands:GetChildren() do
		if s ~= keep then
			s:Destroy()
		end
	end
	local keepLane: Instance? = nil
	local lanes = zone:FindFirstChild("Lanes")
	if lanes then
		for _, lane in lanes:GetChildren() do
			if lane.Name == "Lane" .. tostring(index) then
				keepLane = lane
			else
				lane:Destroy()
			end
		end
	end
	for _, name in { "Lamps", "Dividers" } do
		local f = zone:FindFirstChild(name)
		if f then
			f:Destroy()
		end
	end
	-- центр ряда дорожек: туда и переезжает оставшаяся
	local center = sum / count
	local shift = Vector3.new(center.X - keep.Position.X, 0, center.Z - keep.Position.Z)
	if shift.Magnitude > 0.05 then
		keep.CFrame += shift
		if keepLane then
			for _, d in keepLane:GetDescendants() do
				if d:IsA("BasePart") then
					d.CFrame += shift
				end
			end
		end
	end
	if keepLane then
		-- на площадке был номер дорожки: теперь она одна
		for _, d in keepLane:GetDescendants() do
			if d:IsA("TextLabel") and tonumber(d.Text) then
				d.Text = "🗡️"
			end
		end
	end
	zone:SetAttribute("Lanes", 1)
end
-- V65: вместо ворот красный пол. Ворота (Gatehouse) убираются, весь настил зоны (Deck) красится в красный:
-- шагнул на красный пол, и клиент (HuntCtl) переносит героя на точку броска. Подсказка у ворот выключается, её
-- деталь Prompt остаётся (по ней ведёт Guide и проверяется расстояние). Выход ставится у входа, за краем пола.
local RED = { Color3.fromRGB(196, 52, 52), Color3.fromRGB(178, 40, 44), Color3.fromRGB(210, 66, 60), Color3.fromRGB(186, 46, 48) }
local RED_TRIM = Color3.fromRGB(122, 26, 30)
local function redZone(zone: Instance)
	local deck = zone:FindFirstChild("Deck")
	if not deck then
		return
	end
	-- ворота, забор по переднему краю пола со столбиками и фонарями (Rail) и (V66) домики по бокам от ворот:
	-- стены и крыши (Lodge), окна и ящики с цветами на задней стене (Details), всё внутри (Interior).
	-- Остальные заборы карты не трогаются: они лежат не в зоне броска
	for _, name in { "Gatehouse", "Rail", "Lodge", "Details", "Interior" } do
		local f = zone:FindFirstChild(name)
		if f then
			f:Destroy()
		end
	end
	local minX, maxX, maxZ, top = math.huge, -math.huge, -math.huge, -math.huge
	for _, p in deck:GetDescendants() do
		if p:IsA("BasePart") then
			if string.sub(p.Name, 1, 4) == "Trim" then
				p.Color = RED_TRIM
			else
				-- оттенок по месту доски: пол пёстрый, как был деревянный, но красный
				local k = math.floor(math.abs(p.Position.X * 7 + p.Position.Z * 13)) % #RED + 1
				p.Color = RED[k]
			end
			local half = p.Size / 2
			minX = math.min(minX, p.Position.X - half.X)
			maxX = math.max(maxX, p.Position.X + half.X)
			maxZ = math.max(maxZ, p.Position.Z + half.Z)
			top = math.max(top, p.Position.Y + half.Y)
		end
	end
	local pr = zone:FindFirstChild("Prompt")
	local pp = pr and pr:FindFirstChildOfClass("ProximityPrompt")
	if pp then
		pp.Enabled = false
	end
	local ex = zone:FindFirstChild("Exit")
	if ex and ex:IsA("BasePart") and maxZ > -math.huge then
		-- у входа на дорожку к спавну: 3.9 стада за задним краем пола, корень героя на 3.4 над землёй входа
		ex.CFrame = CFrame.new((minX + maxX) / 2, 3.4, maxZ + 3.9)
	end
	zone:SetAttribute("RedFloor", true)
end

for _, zone in ambushFolder:GetChildren() do
	local okZone, errZone = pcall(consolidateZone, zone)
	if not okZone then
		warn("[Relay] single throwing spot: " .. tostring(errZone))
	end
	local okRed, errRed = pcall(redZone, zone)
	if not okRed then
		warn("[Relay] red throwing floor: " .. tostring(errRed))
	end
end

---------------------------------------------------------------------
-- Остров при старте сервера: музей убран, полоса препятствий пересобрана, материалы посвежее.
-- Инструмент сборки меняет только скрипты, карту в файле места не правит, поэтому всё делается кодом.
-- Порядок: музей и полоса (синхронно, до входа игроков), материалы (отдельным потоком, с паузами).
---------------------------------------------------------------------
do
	local mapRoot = ambushFolder.Parent :: Instance
	local GROUND = 0.1 -- верх земли острова (Village/Ground)
	local MAT = Enum.Material

	local function mk(parent: Instance, name: string, size: Vector3, cf: CFrame, color: Color3, mat: Enum.Material, cyl: boolean?): Part
		local p = Instance.new("Part")
		p.Name = name
		if cyl then
			p.Shape = Enum.PartType.Cylinder
		end
		p.Anchored = true
		p.Size = size
		p.CFrame = cf
		p.Color = color
		p.Material = mat
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		p.Parent = parent
		return p
	end
	-- вертикальный цилиндр от y0 до y1 (у цилиндра Part ось X, поэтому поворот на 90 градусов вокруг Z)
	local function column(parent: Instance, name: string, x: number, z: number, y0: number, y1: number, dia: number, color: Color3, mat: Enum.Material): Part
		return mk(parent, name, Vector3.new(y1 - y0, dia, dia), CFrame.new(x, (y0 + y1) / 2, z) * CFrame.Angles(0, 0, math.rad(90)), color, mat, true)
	end

	-------------------------------------------------------------------
	-- 1. Музей: здание и дорога к нему убираются, на его месте небольшая роща.
	-- Plot6Access / RearEntrance* на модели не читает ни один скрипт, а участков всего пять, так что пол прохода не нужен.
	-------------------------------------------------------------------
	local function buildGrove()
		local grove = Instance.new("Folder")
		grove.Name = "MuseumGrove"
		local rng = Random.new(73)
		local stone = Color3.fromRGB(150, 146, 138)
		local bark = Color3.fromRGB(112, 78, 48)
		local greens = { Color3.fromRGB(86, 150, 70), Color3.fromRGB(98, 166, 78), Color3.fromRGB(70, 132, 64), Color3.fromRGB(118, 174, 84) }
		-- дорожка из плит вдоль бывшего зала (10 деталей)
		for i = 0, 9 do
			mk(grove, "PathStone", Vector3.new(5, 0.2, 9.4), CFrame.new(169, GROUND + 0.1, 30 + i * 11.5), stone, MAT.Cobblestone)
		end
		-- деревья из блоков (11 по 4 детали)
		local placed: { Vector3 } = {}
		local tries = 0
		while #placed < 11 and tries < 300 do
			tries += 1
			local x, z = rng:NextNumber(134, 204), rng:NextNumber(34, 138)
			local ok = math.abs(x - 169) > 8
			for _, q in placed do
				if (q.X - x) * (q.X - x) + (q.Z - z) * (q.Z - z) < 110 then
					ok = false
					break
				end
			end
			if ok then
				table.insert(placed, Vector3.new(x, 0, z))
				local th = rng:NextNumber(5, 7)
				local g = greens[rng:NextInteger(1, #greens)]
				mk(grove, "TreeTrunk", Vector3.new(1.6, th, 1.6), CFrame.new(x, GROUND + th / 2, z), bark, MAT.Wood)
				mk(grove, "TreeLeaves", Vector3.new(7, 2.6, 7), CFrame.new(x, GROUND + th + 0.8, z), g, MAT.LeafyGrass)
				mk(grove, "TreeLeaves", Vector3.new(5, 2.4, 5), CFrame.new(x, GROUND + th + 2.8, z), g, MAT.LeafyGrass)
				mk(grove, "TreeLeaves", Vector3.new(3, 2, 3), CFrame.new(x, GROUND + th + 4.8, z), g, MAT.LeafyGrass)
			end
		end
		-- кусты (12)
		for _ = 1, 12 do
			local x, z = rng:NextNumber(134, 204), rng:NextNumber(32, 140)
			if math.abs(x - 169) < 5 then
				x += if x < 169 then -6 else 6
			end
			local s = rng:NextNumber(2.4, 3.6)
			mk(grove, "Bush", Vector3.new(s, 1.6, s), CFrame.new(x, GROUND + 0.8, z), greens[rng:NextInteger(1, #greens)], MAT.LeafyGrass)
		end
		-- скамейки у дорожки (3 по 4 детали)
		for i, z in { 55, 85, 115 } do
			local side = if i % 2 == 1 then -1 else 1
			local bx = 169 + side * 5
			mk(grove, "BenchSeat", Vector3.new(1.4, 0.4, 4.4), CFrame.new(bx, GROUND + 1.5, z), Color3.fromRGB(176, 128, 76), MAT.WoodPlanks)
			mk(grove, "BenchBack", Vector3.new(0.3, 1.1, 4.4), CFrame.new(bx + side * 0.6, GROUND + 2.2, z), Color3.fromRGB(150, 104, 62), MAT.WoodPlanks)
			for _, dz in { -1.8, 1.8 } do
				mk(grove, "BenchLeg", Vector3.new(1.2, 1.3, 0.4), CFrame.new(bx, GROUND + 0.65, z + dz), bark, MAT.Wood)
			end
		end
		-- фонари (4 по 2 детали)
		for _, z in { 50, 118 } do
			for _, side in { -1, 1 } do
				column(grove, "LampPost", 169 + side * 4.2, z, GROUND, GROUND + 6, 0.4, Color3.fromRGB(60, 52, 46), MAT.Metal)
				mk(grove, "LampLight", Vector3.new(1.1, 1.1, 1.1), CFrame.new(169 + side * 4.2, GROUND + 6.4, z), Color3.fromRGB(255, 214, 130), MAT.Neon)
			end
		end
		-- клумбы (4 по 2 детали)
		for i = 1, 4 do
			local x = if i % 2 == 1 then 150 else 188
			local z = 48 + i * 20
			mk(grove, "FlowerBed", Vector3.new(4, 0.6, 4), CFrame.new(x, GROUND + 0.3, z), Color3.fromRGB(110, 82, 58), MAT.Wood)
			mk(grove, "Flowers", Vector3.new(3.2, 0.5, 3.2), CFrame.new(x, GROUND + 0.8, z), if i % 2 == 1 then Color3.fromRGB(232, 96, 130) else Color3.fromRGB(246, 200, 70), MAT.Grass)
		end
		grove.Parent = mapRoot
	end

	local function removeMuseum()
		if mapRoot:GetAttribute("MuseumRemoved") then
			return
		end
		local hall = mapRoot:FindFirstChild("Showroom")
		if hall then
			hall:Destroy()
		end
		local roads = mapRoot:FindFirstChild("Roads")
		if roads then
			for _, r in roads:GetChildren() do
				if string.sub(r.Name, 1, 10) == "MuseumRoad" then
					r:Destroy()
				end
			end
		end
		mapRoot:SetAttribute("MuseumRemoved", true)
		local okGrove, errGrove = pcall(buildGrove)
		if not okGrove then
			warn("[Relay] museum grove: " .. tostring(errGrove))
		end
	end

	-------------------------------------------------------------------
	-- 2. Полоса препятствий. Старт (StartPad/Start/Prompt/StartSign) остаётся, финиш и батуты переезжают,
	-- ступени, брёвна и монетки строятся заново. Клиент (Activities.course) ищет детали по атрибутам
	-- CourseCoin / Finish / Bounce, так что они сохранены.
	-- Площадки в таблице: { вид, x, z, ширина, глубина, верх y [, фаза мигания] }, у круглых (stump, mush) глубина 0.
	-- Ходьба: WalkSpeed 20, прыжок ~7 в высоту и ~11 в длину. Зазор считается от края до края (по настоящей форме),
	-- пределы: зазор не больше 8.5 вниз/вровень, 7 при подъёме до 3, 5.5 при подъёме до 5.5; подъём за раз не больше 5.5.
	-- Подвижные препятствия не возят игрока, их надо пережидать: стены (3), крутящаяся балка (4), мигающие
	-- площадки (4 и 6), качающиеся брёвна (7). Падение никого не убивает: с земли до площадок отдыха (pad) до 5 в высоту
	-- запрыгнуть можно, так что вернуться к нужному этапу можно пешком. Батуты (этап 5) стоят на пути как обычные площадки.
	--
	--   N   откуда -> куда    зазор  подъём  (куда: x, z, верх y)
	--   1  start -> stump  gap  4.4  dy +0.6   (-140.5, 30) y 1.1
	--   2  stump -> stump  gap  5.5  dy +0.5   (-148, 31.5) y 1.6
	--   3  stump -> stump  gap  6.0  dy +0.5   (-155.5, 29) y 2.1
	--   4  stump -> stump  gap  6.5  dy +0.5   (-163, 32.5) y 2.6
	--   5  stump -> stump  gap  6.3  dy +0.5   (-170, 36.5) y 3.1
	--   6  stump -> pad    gap  5.1  dy +0.4   (-172, 45.5) y 3.5
	--   7  pad   -> plank  gap  5.5  dy +0.4   (-162.5, 51) y 3.9
	--   8  plank -> plank  gap  5.5  dy +0.4   (-155, 47) y 4.3
	--   9  plank -> plank  gap  5.7  dy +0.4   (-148, 52) y 4.7
	--  10  plank -> plank  gap  5.1  dy +0.3   (-141, 48) y 5
	--  11  plank -> pad    gap  6.3  dy +0.0   (-139, 58) y 5
	--  12  pad   -> log    gap  6.3  dy +0.0   (-150.5, 64) y 5
	--  13  log   -> slab   gap  4.5  dy +0.0   (-163.5, 66) y 5
	--  14  slab  -> log    gap  4.0  dy +0.0   (-176, 66) y 5
	--  15  log   -> pad    gap  6.8  dy +0.0   (-176, 77) y 5
	--  16  pad   -> slab   gap  5.0  dy +0.0   (-163, 80) y 5
	--  17  slab  -> ghost  gap  5.5  dy +0.0   (-151, 81) y 5
	--  18  ghost -> ghost  gap  5.6  dy +0.0   (-143, 86.5) y 5
	--  19  ghost -> ghost  gap  3.8  dy +0.0   (-138.5, 93) y 5
	--  20  ghost -> pad    gap  4.5  dy +0.0   (-143, 102) y 5
	--  21  pad   -> mush   gap  4.3  dy -0.6   (-151.5, 104) y 4.4
	--  22  mush  -> mush   gap  6.1  dy -0.6   (-159, 100) y 3.8
	--  23  mush  -> tramp  gap  5.1  dy -0.8   (-168, 105) y 3
	--  24  tramp -> tramp  gap  5.0  dy +0.0   (-168, 116) y 3
	--  25  tramp -> mush   gap  4.4  dy +1.4   (-159.5, 120) y 4.4
	--  26  mush  -> mush   gap  5.8  dy +0.6   (-152, 117) y 5
	--  27  mush  -> pad    gap  5.3  dy +0.0   (-144, 124) y 5
	--  28  pad   -> ghost  gap  3.0  dy +1.0   (-146.5, 131.5) y 6
	--  29  ghost -> ghost  gap  4.1  dy +1.0   (-153.5, 135.5) y 7
	--  30  ghost -> ghost  gap  3.8  dy +1.0   (-160, 131) y 8
	--  31  ghost -> pad    gap  3.5  dy +1.0   (-169, 133) y 9
	--  32  pad   -> slab   gap  3.6  dy +0.0   (-160, 141) y 9
	--  33  slab  -> slab   gap  5.0  dy +0.5   (-151, 145) y 9.5
	--  34  slab  -> slab   gap  5.0  dy +0.5   (-142, 141) y 10
	--  35  slab  -> stump  gap  5.0  dy +2.0   (-140, 149) y 12
	--  36  stump -> stump  gap  6.2  dy +1.8   (-147, 153) y 13.8
	--  37  stump -> stump  gap  5.8  dy +1.6   (-154.5, 152) y 15.4
	--  38  stump -> stump  gap  6.3  dy +1.6   (-162, 149) y 17
	--  39  stump -> finish  gap  5.1  dy +1.0   (-171, 149) y 18
	--
	-- Этапы: 1 пеньки (1-6), 2 доски зигзагом (7-11), 3 раздвижные стены (12-15), 4 балка и мигающие (16-20),
	-- 5 грибы и батуты (21-27), 6 мигающий небесный путь (28-31), 7 качающиеся брёвна (32-34), 8 башня к финишу (35-39).
	-------------------------------------------------------------------
	local NODES: { { any } } = {
		{ "start", -132, 30, 6, 6, 0.5 },
		{ "stump", -140.5, 30, 2.2, 0, 1.1 },
		{ "stump", -148, 31.5, 2, 0, 1.6 },
		{ "stump", -155.5, 29, 1.8, 0, 2.1 },
		{ "stump", -163, 32.5, 1.8, 0, 2.6 },
		{ "stump", -170, 36.5, 1.8, 0, 3.1 },
		{ "pad", -172, 45.5, 6, 6, 3.5 },
		{ "plank", -162.5, 51, 2.6, 1.4, 3.9 },
		{ "plank", -155, 47, 2.6, 1.4, 4.3 },
		{ "plank", -148, 52, 2.6, 1.4, 4.7 },
		{ "plank", -141, 48, 2.6, 1.4, 5 },
		{ "pad", -139, 58, 6, 6, 5 },
		{ "log", -150.5, 64, 5, 2.4, 5 },
		{ "slab", -163.5, 66, 12, 9, 5 },
		{ "log", -176, 66, 5, 2.4, 5 },
		{ "pad", -176, 77, 6, 6, 5 },
		{ "slab", -163, 80, 10, 10, 5 },
		{ "ghost", -151, 81, 3, 3, 5, 0 },
		{ "ghost", -143, 86.5, 3, 3, 5, -1 },
		{ "ghost", -138.5, 93, 3, 3, 5, -2 },
		{ "pad", -143, 102, 6, 6, 5 },
		{ "mush", -151.5, 104, 2.4, 0, 4.4 },
		{ "mush", -159, 100, 2.4, 0, 3.8 },
		{ "mush", -159.5, 120, 2.4, 0, 4.4 },
		{ "mush", -152, 117, 2.2, 0, 5 },
		{ "pad", -144, 124, 6, 6, 5 },
		{ "ghost", -146.5, 131.5, 3, 3, 6, -0.5 },
		{ "ghost", -153.5, 135.5, 3, 3, 7, -1.5 },
		{ "ghost", -160, 131, 3, 3, 8, -2.5 },
		{ "pad", -169, 133, 8, 8, 9 },
		{ "slab", -160, 141, 4, 4, 9 },
		{ "slab", -151, 145, 4, 4, 9.5 },
		{ "slab", -142, 141, 4, 4, 10 },
		{ "stump", -140, 149, 2, 0, 12 },
		{ "stump", -147, 153, 1.8, 0, 13.8 },
		{ "stump", -154.5, 152, 1.8, 0, 15.4 },
		{ "stump", -162, 149, 1.8, 0, 17 },
		{ "finish", -171, 149, 6, 6, 18 },
	}

	-- монетки (10): между пеньками, над площадками и высоко над батутами (верх батута 3, монета на 12.5)
	local COINS = {
		Vector3.new(-151.8, 8.4, 30.2), Vector3.new(-148, 7.9, 52), Vector3.new(-163.5, 8.2, 66), Vector3.new(-163, 9.5, 80),
		Vector3.new(-143, 8.2, 86.5), Vector3.new(-168, 12.5, 105), Vector3.new(-168, 12.5, 116), Vector3.new(-153.5, 10.2, 135.5),
		Vector3.new(-151, 12.7, 145), Vector3.new(-154.5, 18.6, 152),
	}
	-- места батутов: первые два на пути, ещё два рядом (яма из четырёх)
	local BOUNCE = 56
	local TRAMPS = { Vector2.new(-168, 105), Vector2.new(-168, 116), Vector2.new(-176, 105), Vector2.new(-176, 116) }
	local OLD_ROUTE = { CStump = true, CStumpTop = true, CLog = true, CRock = true, CPlank = true, CRope = true, CMushroom = true, CStem = true }

	local function buildCourse()
		local course = mapRoot:FindFirstChild("ObstacleCourse")
		if not course or course:GetAttribute("CourseV2") then
			return
		end
		local route = Instance.new("Folder")
		route.Name = "Route"
		local movers: { (number) -> () } = {}

		local cBark = Color3.fromRGB(112, 78, 48)
		local cWood = Color3.fromRGB(150, 104, 62)
		local cPlank = Color3.fromRGB(196, 152, 98)
		local cStone = Color3.fromRGB(112, 120, 114)
		local cPad = Color3.fromRGB(172, 126, 78)
		local cGhost = Color3.fromRGB(96, 206, 232)
		local finish: Vector3? = nil

		-- мигающая площадка: цикл 4 с, твёрдая 2.8 с, последние 0.7 с мигает, потом исчезает (CanCollide и прозрачность)
		local function addGhost(p: Part, phase: number)
			local solid, tr = true, 0
			table.insert(movers, function(t)
				local u = (t + phase) % 4
				local wantSolid = u < 2.8
				local wantTr = if u < 2.1 then 0 elseif u < 2.8 then (if math.floor(u * 6) % 2 == 0 then 0.5 else 0.1) else 0.85
				if wantSolid ~= solid then
					solid = wantSolid
					p.CanCollide = wantSolid
				end
				if wantTr ~= tr then
					tr = wantTr
					p.Transparency = wantTr
				end
			end)
		end

		for _, n in NODES do
			local kind, x, z, w, dd, y = n[1], n[2], n[3], n[4], n[5], n[6]
			if kind == "stump" then
				column(route, "Stump", x, z, GROUND, y - 0.15, w * 0.85, cBark, MAT.Wood)
				column(route, "StumpTop", x, z, y - 0.15, y, w, Color3.fromRGB(206, 164, 108), MAT.Wood)
			elseif kind == "mush" then
				column(route, "MushStem", x, z, GROUND, y - 0.5, 0.9, Color3.fromRGB(240, 230, 208), MAT.SmoothPlastic)
				column(route, "MushCap", x, z, y - 0.5, y, w, Color3.fromRGB(206, 62, 56), MAT.SmoothPlastic)
			elseif kind == "plank" then
				mk(route, "Plank", Vector3.new(w, 0.4, dd), CFrame.new(x, y - 0.2, z), cPlank, MAT.WoodPlanks)
				column(route, "PlankPost", x, z, GROUND, y - 0.4, 0.5, cBark, MAT.Wood)
			elseif kind == "log" then
				mk(route, "Log", Vector3.new(w, 0.9, dd), CFrame.new(x, y - 0.45, z), cWood, MAT.Wood)
				column(route, "LogPost", x, z, GROUND, y - 0.9, 0.9, cBark, MAT.Wood)
			elseif kind == "slab" then
				mk(route, "Slab", Vector3.new(w, 1, dd), CFrame.new(x, y - 0.5, z), cStone, MAT.Cobblestone)
				column(route, "SlabPillar", x, z, GROUND, y - 1, math.min(2, w * 0.5), cStone, MAT.Slate)
			elseif kind == "pad" then
				mk(route, "RestPad", Vector3.new(w, 0.6, dd), CFrame.new(x, y - 0.3, z), cPad, MAT.WoodPlanks)
				mk(route, "RestPadTrim", Vector3.new(w + 0.4, 0.2, dd + 0.4), CFrame.new(x, y - 0.7, z), cBark, MAT.Wood)
				column(route, "RestPadPillar", x, z, GROUND, y - 0.8, 1.2, cBark, MAT.Wood)
			elseif kind == "ghost" then
				local p = mk(route, "Ghost", Vector3.new(w, 0.5, dd), CFrame.new(x, y - 0.25, z), cGhost, MAT.SmoothPlastic)
				addGhost(p, n[7] or 0)
			elseif kind == "finish" then
				finish = Vector3.new(x, y, z)
				column(route, "FinishPillar", x, z, GROUND, y - 0.5, 1.4, cBark, MAT.Wood)
			end
		end

		-- этап 3: три стены ездят поперёк настила (шаг 4.6, цикл 4.4 с); соседние в противофазе, высота 7.5 выше прыжка
		local function addWall(x: number, phase: number)
			local base = CFrame.new(x, 5 + 3.75, 63.7)
			local p = mk(route, "SlidingWall", Vector3.new(1, 7.5, 4.4), base, Color3.fromRGB(176, 72, 58), MAT.Brick)
			table.insert(movers, function(t)
				local k = (math.sin((t / 4.4 + phase) * 2 * math.pi) + 1) / 2
				p.CFrame = base + Vector3.new(0, 0, 4.6 * k)
			end)
		end
		addWall(-159.5, 0)
		addWall(-163.5, 0.5)
		addWall(-167.5, 0)

		-- этап 4: балка крутится над настилом (оборот 4 с), прыгнуть надо над ней (верх 6.1 при настиле 5)
		column(route, "SpinnerHub", -163, 80, 5, 6.2, 1.4, cBark, MAT.Wood)
		local beam = mk(route, "SpinnerBeam", Vector3.new(9.4, 1.1, 0.9), CFrame.new(-163, 5.55, 80), Color3.fromRGB(196, 84, 60), MAT.Wood)
		table.insert(movers, function(t)
			beam.CFrame = CFrame.new(-163, 5.55, 80) * CFrame.Angles(0, (t % 4) * 2 * math.pi / 4, 0)
		end)

		-- этап 7: над площадками висит бревно на раме и качается +-50 градусов (цикл 3.6 с); низ бревна в 1.8 над настилом
		local LEN = 7.4
		local function addPendulum(sx: number, sz: number, top: number, phase: number)
			local py = top + 9.2
			for _, dz in { -2.7, 2.7 } do
				column(route, "GantryPost", sx, sz + dz, GROUND, py + 0.4, 0.6, cBark, MAT.Wood)
			end
			mk(route, "GantryBeam", Vector3.new(0.7, 0.7, 6.1), CFrame.new(sx, py + 0.05, sz), cBark, MAT.Wood)
			local log = mk(route, "SwingLog", Vector3.new(LEN, 1.2, 1.2), CFrame.new(sx, py - LEN / 2, sz) * CFrame.Angles(0, 0, math.rad(90)), Color3.fromRGB(132, 92, 56), MAT.Wood, true)
			table.insert(movers, function(t)
				local a = math.rad(50) * math.sin((t % 3.6) * 2 * math.pi / 3.6 + phase)
				log.CFrame = CFrame.new(sx, py, sz) * CFrame.Angles(0, 0, a) * CFrame.new(0, -LEN / 2, 0) * CFrame.Angles(0, 0, math.rad(90))
			end)
		end
		addPendulum(-160, 141, 9, 0)
		addPendulum(-151, 145, 9.5, -1.4) -- второе отстаёт на ~0.8 с: игрок, прыгнувший с первой площадки в безопасный момент, попадает во второй безопасный

		-- монетки: шаблон берётся у старой (атрибут CourseCoin и вид сохраняются)
		local tpl: BasePart? = nil
		for _, d in course:GetChildren() do
			if d:IsA("BasePart") and d:GetAttribute("CourseCoin") then
				tpl = d:Clone()
				break
			end
		end
		if not tpl then
			local c = Instance.new("Part")
			c.Name = "CourseCoin"
			c.Shape = Enum.PartType.Cylinder
			c.Size = Vector3.new(0.2, 1, 1)
			c.Color = Color3.fromRGB(255, 205, 60)
			c.Material = MAT.SmoothPlastic
			c.Anchored = true
			c.CanCollide = false
			c:SetAttribute("CourseCoin", true)
			tpl = c
		end
		local tplPart = tpl :: BasePart
		local rot = tplPart.CFrame - tplPart.CFrame.Position
		for _, pos in COINS do
			local c = tplPart:Clone()
			c.CFrame = CFrame.new(pos) * rot
			c.Parent = route
		end

		-- батуты: детали Trampoline/TrampStem/TrampDot переезжают на новые места целыми группами
		local tramps: { BasePart } = {}
		local others: { BasePart } = {}
		for _, d in course:GetChildren() do
			if d:IsA("BasePart") then
				if d.Name == "Trampoline" then
					table.insert(tramps, d)
				elseif d.Name == "TrampStem" or d.Name == "TrampDot" then
					table.insert(others, d)
				end
			end
		end
		table.sort(tramps, function(a, b)
			return a.Position.X < b.Position.X or (a.Position.X == b.Position.X and a.Position.Z < b.Position.Z)
		end)
		local shifts: { Vector3 } = {}
		for i, t in tramps do
			local tp = TRAMPS[math.min(i, #TRAMPS)]
			shifts[i] = Vector3.new(tp.X - t.Position.X, 0, tp.Y - t.Position.Z)
		end
		local movedParts: { BasePart } = {}
		local movedBy: { Vector3 } = {}
		for _, o in others do
			local best, bi = math.huge, 0
			for i, t in tramps do
				local d = Vector3.new(t.Position.X - o.Position.X, 0, t.Position.Z - o.Position.Z).Magnitude
				if d < best then
					best, bi = d, i
				end
			end
			if bi > 0 then
				table.insert(movedParts, o)
				table.insert(movedBy, shifts[bi])
			end
		end
		for i, t in tramps do
			table.insert(movedParts, t)
			table.insert(movedBy, shifts[i])
		end
		for i, part in movedParts do
			part.CFrame += movedBy[i]
		end
		-- у старых батутов Bounce 90-150 (до 57 в высоту): с таким подбросом можно перелететь на финиш,
		-- поэтому подброс выравнивается: 56 даёт ~8 вверх от батута и не доносит до настила небесного пути (верх 9, 10 вбок)
		for _, t in tramps do
			t:SetAttribute("Bounce", BOUNCE)
		end

		-- финиш: площадка, столбы и табличка переезжают целиком на верх башни
		local pad = course:FindFirstChild("FinishPad") :: BasePart?
		if pad and finish then
			local delta = Vector3.new(finish.X, finish.Y - pad.Size.Y / 2, finish.Z) - pad.Position
			for _, d in course:GetChildren() do
				if d:IsA("BasePart") and string.sub(d.Name, 1, 6) == "Finish" then
					d.CFrame += delta
				end
			end
		end

		-- старая трасса и старые монетки убираются, новая включается
		for _, d in course:GetChildren() do
			if OLD_ROUTE[d.Name] or d.Name == "CourseCoin" then
				d:Destroy()
			end
		end
		route.Parent = course
		course:SetAttribute("CourseV2", true)

		if #movers > 0 then
			local acc = 0
			RunService.Heartbeat:Connect(function(dt)
				acc += dt
				if acc < 1 / 30 then
					return
				end
				acc = 0
				local now = workspace:GetServerTimeNow()
				for i = #movers, 1, -1 do
					local ok, err = pcall(movers[i], now)
					if not ok then
						warn("[Relay] course mover: " .. tostring(err))
						table.remove(movers, i)
					end
				end
			end)
		end
	end

	-------------------------------------------------------------------
	-- 3. Материалы стартового острова: пластик с шипами заменяется по цвету и месту. Цвета не меняются.
	-- Серые: тёмные Slate, плоские у земли Cobblestone (дороги Asphalt), крупные Rock, светлые Concrete;
	-- белые Marble (плоские большие) или SmoothPlastic; зелёные плоские Grass, остальные LeafyGrass; красные Brick;
	-- коричневые Wood (тонкие и плоские большие WoodPlanks); песочные Sand (плоские у земли) или Sandstone;
	-- остальное SmoothPlastic. Neon, прозрачное и отражающее остаются как были; модели с Humanoid не трогаются.
	-------------------------------------------------------------------
	local ROOTS = { "StartIslandV15", "Plaza", "Village", "Roads", "Plots", "Market", "Herbalist", "Armory", "Forge", "Tracker", "Campfire", "Lookout", "TargetRange", "ObstacleCourse" }

	local function pick(p: BasePart, rootName: string, nameLow: string): Enum.Material
		local h, s, v = p.Color:ToHSV()
		local sz = p.Size
		local mn = math.min(sz.X, sz.Y, sz.Z)
		local mx = math.max(sz.X, sz.Y, sz.Z)
		local area = sz.X * sz.Z
		local flat = p.CFrame.UpVector.Y > 0.95 and sz.Y < math.min(sz.X, sz.Z) * 0.5
		if s < 0.14 then
			if v > 0.86 then
				return if flat and area >= 24 then MAT.Marble else MAT.SmoothPlastic
			elseif v < 0.22 then
				return MAT.Slate
			elseif rootName == "Roads" and flat then
				return MAT.Asphalt
			elseif flat and p.Position.Y < 1.6 then
				return MAT.Cobblestone
			elseif sz.X * sz.Y * sz.Z > 80 and v < 0.7 then
				return MAT.Rock
			end
			return if v < 0.5 then MAT.Slate else MAT.Concrete
		end
		if h >= 0.17 and h <= 0.46 then
			return if flat and area >= 12 then MAT.Grass else MAT.LeafyGrass
		end
		if (h < 0.04 or h >= 0.94) and s >= 0.4 then
			return MAT.Brick
		end
		if h < 0.17 then
			if s >= 0.4 and h >= 0.04 and h < 0.09 and string.find(nameLow, "roof", 1, true) then
				return MAT.Brick
			elseif v >= 0.62 and s <= 0.55 and h >= 0.07 then
				return if flat and p.Position.Y < 1.6 then MAT.Sand else MAT.Sandstone
			elseif s > 0.6 and v > 0.7 then
				return MAT.SmoothPlastic
			end
			return if (mn < 1 and mx >= 3) or (flat and area >= 16) then MAT.WoodPlanks else MAT.Wood
		end
		return MAT.SmoothPlastic
	end

	local function restyle()
		if not RESTYLE_MATERIALS or mapRoot:GetAttribute("MaterialsRestyled") then
			return
		end
		local lists: { { Instance } } = {}
		local names: { string } = {}
		local skipParts: { [Instance]: boolean } = {}
		for _, rn in ROOTS do
			local root = mapRoot:FindFirstChild(rn)
			if root then
				local list: { Instance } = {}
				if rn == "ObstacleCourse" then
					-- новая трасса (Route) уже со своими материалами
					for _, ch in root:GetChildren() do
						if ch.Name ~= "Route" then
							table.insert(list, ch)
							for _, d in ch:GetDescendants() do
								table.insert(list, d)
							end
						end
					end
				else
					list = root:GetDescendants()
				end
				for _, d in list do
					if d:IsA("Humanoid") and d.Parent then
						for _, q in d.Parent:GetDescendants() do
							skipParts[q] = true
						end
					end
				end
				table.insert(lists, list)
				table.insert(names, rn)
			end
		end
		local SMOOTH = Enum.SurfaceType.Smooth
		local n = 0
		for li, list in lists do
			local rootName = names[li]
			for _, d in list do
				local cn = d.ClassName
				if cn == "Part" or cn == "WedgePart" or cn == "CornerWedgePart" then
					local p = d :: Part
					if p.Material == MAT.Plastic then
						if p.Transparency < 0.1 and p.Reflectance == 0 and not skipParts[p] then
							p.Material = pick(p, rootName, string.lower(p.Name))
							if p.MaterialVariant ~= "" then
								p.MaterialVariant = ""
							end
						end
						-- шипы убираются у любого пластика (в том числе у стекла и деталей NPC)
						if p.TopSurface ~= SMOOTH then
							p.TopSurface = SMOOTH
						end
						if p.BottomSurface ~= SMOOTH then
							p.BottomSurface = SMOOTH
						end
						if p.LeftSurface ~= SMOOTH then
							p.LeftSurface = SMOOTH
						end
						if p.RightSurface ~= SMOOTH then
							p.RightSurface = SMOOTH
						end
						if p.FrontSurface ~= SMOOTH then
							p.FrontSurface = SMOOTH
						end
						if p.BackSurface ~= SMOOTH then
							p.BackSurface = SMOOTH
						end
					end
					n += 1
					if n % 3000 == 0 then
						task.wait()
					end
				end
			end
		end
		mapRoot:SetAttribute("MaterialsRestyled", true)
	end

	local okMuseum, errMuseum = pcall(removeMuseum)
	if not okMuseum then
		warn("[Relay] remove museum: " .. tostring(errMuseum))
	end
	local okCourse, errCourse = pcall(buildCourse)
	if not okCourse then
		warn("[Relay] obstacle course: " .. tostring(errCourse))
	end
	task.spawn(function()
		local okStyle, errStyle = pcall(restyle)
		if not okStyle then
			warn("[Relay] island materials: " .. tostring(errStyle))
		end
	end)
end

local function leaveAmbush(player: Player)
	farSince[player] = nil
	-- V62: игрок снова виден остальным; ещё несколько секунд его запоздалые эффекты не рассылаются
	-- (только если он действительно стоял на одиночном месте)
	if occupied[player] or player:GetAttribute("Solo") then
		soloUntil[player] = os.clock() + 8
	end
	occupied[player] = nil
	if player.Parent then
		player:SetAttribute("Solo", nil)
	end
end

-- все дорожки всех зон по порядку Index
local function allStands(): { BasePart }
	local list: { BasePart } = {}
	for _, zone in ambushFolder:GetChildren() do
		local stands = zone:FindFirstChild("Stands")
		if stands then
			for _, s in stands:GetChildren() do
				if s:IsA("BasePart") and type(s:GetAttribute("Index")) == "number" then
					table.insert(list, s)
				end
			end
		end
	end
	table.sort(list, function(a, b)
		return (a:GetAttribute("Index") :: number) < (b:GetAttribute("Index") :: number)
	end)
	return list
end

-- action "enter": lane (необязательно) - желаемая дорожка; иначе берётся свободная ближайшая к игроку.
-- Возвращает true и номер дорожки, либо false и текст ошибки.
AmbushFn.OnServerInvoke = function(player: Player, action: any, lane: any)
	-- выход не режем лимитером: иначе дорожка может остаться занятой
	if action == "leave" then
		leaveAmbush(player)
		return true
	end
	if not allow(player, "ambush", 4) then
		return false, "Please wait a moment"
	end
	if action ~= "enter" or player.Parent == nil then
		return false, "bad"
	end
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not hrp or not hum or hum.Health <= 0 then
		return false, "bad"
	end
	local stands = allStands()
	if #stands == 0 then
		return false, "Throwing Grounds not found"
	end
	local zone = stands[1].Parent and stands[1].Parent.Parent
	local pr = zone and zone:FindFirstChild("Prompt") :: BasePart?
	if not pr or (hrp.Position - pr.Position).Magnitude > MAX_DISTANCE then
		return false, "You are too far from the Throwing Grounds"
	end
	-- V62: одно место для всех. Игрок на нём невидим для остальных (атрибут Solo читают клиенты),
	-- поэтому на одной дорожке могут стоять сколько угодно игроков, каждый бросает «сам с собой».
	local pick = stands[1]
	-- V65: повторный «enter» от того, кто уже стоит на точке, не обнуляет отсчёт ухода с неё
	if not occupied[player] then
		farSince[player] = nil
	end
	occupied[player] = pick
	player:SetAttribute("Solo", true)
	return true, pick:GetAttribute("Index")
end

-- Раз в секунду: дорожку освобождаем, если игрока нет, он мёртв или стоит далеко от неё дольше HOLD_GRACE секунд
task.spawn(function()
	while true do
		task.wait(1)
		for player, s in occupied do
			local char = player.Character
			local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			local hum = char and char:FindFirstChildOfClass("Humanoid")
			local away = player.Parent == nil or not s.Parent or not hrp or not hum or hum.Health <= 0
				or (hrp.Position - s.Position).Magnitude > HOLD_DISTANCE
			if away then
				local t0 = farSince[player] or os.clock()
				farSince[player] = t0
				if os.clock() - t0 > HOLD_GRACE then
					leaveAmbush(player)
				end
			else
				farSince[player] = nil
			end
		end
	end
end)

-- V62: столкновения. Игроки на одиночном месте не толкают друг друга и остальных (они стоят в одной точке),
-- но по-прежнему стоят на земле (группа Solo сталкивается с Default).
local PhysicsService = game:GetService("PhysicsService")
local G_SOLO, G_CHAR = "SoloThrow", "PlayerChars"
-- V64: группы регистрируются на Workspace (методы PhysicsService устарели); старый путь оставлен запасным
local function registerGroup(name: string)
	local ok = pcall(function()
		(workspace :: any):RegisterCollisionGroup(name)
	end)
	if not ok then
		pcall(PhysicsService.RegisterCollisionGroup, PhysicsService, name)
	end
end
local function setCollidable(a: string, b: string, on: boolean)
	local ok = pcall(function()
		(workspace :: any):CollisionGroupSetCollidable(a, b, on)
	end)
	if not ok then
		pcall(PhysicsService.CollisionGroupSetCollidable, PhysicsService, a, b, on)
	end
end
for _, g in { G_SOLO, G_CHAR } do
	registerGroup(g)
end
setCollidable(G_SOLO, G_SOLO, false)
setCollidable(G_SOLO, G_CHAR, false)

local function applyGroup(player: Player, char: Model)
	local g = player:GetAttribute("Solo") and G_SOLO or G_CHAR
	for _, d in char:GetDescendants() do
		if d:IsA("BasePart") then
			d.CollisionGroup = g
		end
	end
end

local function watchCharacter(player: Player, char: Model)
	applyGroup(player, char)
	char.DescendantAdded:Connect(function(d)
		if d:IsA("BasePart") then
			d.CollisionGroup = player:GetAttribute("Solo") and G_SOLO or G_CHAR
		end
	end)
end

local function watchPlayer(player: Player)
	player:GetAttributeChangedSignal("Solo"):Connect(function()
		if player.Character then
			applyGroup(player, player.Character)
		end
	end)
	player.CharacterAdded:Connect(function(char)
		watchCharacter(player, char)
	end)
	if player.Character then
		watchCharacter(player, player.Character)
	end
end
Players.PlayerAdded:Connect(watchPlayer)
for _, p in Players:GetPlayers() do
	watchPlayer(p)
end

function Relay.onLeave(player: Player)
	leaveAmbush(player)
	soloUntil[player] = nil
	buckets[player] = nil
end

function Relay.onDied(player: Player)
	leaveAmbush(player)
end

return Relay
