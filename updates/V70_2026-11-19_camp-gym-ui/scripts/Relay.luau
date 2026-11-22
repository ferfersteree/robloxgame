-- ServerScriptService/Server/Relay.luau
-- Пересылка того, что должны видеть все: позы, эффекты бросков/раскрытий, занятость дорожек зоны для кидания.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local Net = require(RS.Shared.Net)
local Config = require(RS.Shared.Config)
local PoseData = require(RS.Shared.PoseData) :: any
local Cosmetics = require(script.Parent.Cosmetics)
local Util = require(RS.Shared.Util)

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
