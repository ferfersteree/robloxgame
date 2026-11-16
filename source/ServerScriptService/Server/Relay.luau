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
	local tpl = RS.Assets:FindFirstChild("Dumbbell")
	if not tpl or not tpl:IsA("Model") then
		return
	end
	local level = Cosmetics.dumbbellLevel(player)
	local look = Config.DUMBBELL_LOOK[math.clamp(level, 1, #Config.DUMBBELL_LOOK)]
	for _, side in { "RightHand", "LeftHand" } do
		local hand = char:FindFirstChild(side) :: BasePart?
		if hand then
			local m = tpl:Clone()
			m.Name = "HeldDumbbell"
			for _, p in m:GetDescendants() do
				if p:IsA("BasePart") and p:GetAttribute("Weight") then
					p.Color = look.color
					p.Material = look.material
				end
			end
			m:ScaleTo(look.size * 0.8)
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

-- Эффекты: копируем только известные поля нужных типов
local FX_KINDS = { throw = true, reveal = true, crash = true, bounce = true, levelup = true, collect = true, tier = true }
local FIELDS = {
	tier = "number", spear = "string", from = "Vector3", to = "Vector3", t = "number", sp = "string",
	rarity = "number", mut = "string", pos = "Vector3", m = "number", lane = "number", escaped = "boolean", crashed = "boolean",
}
FxEv.OnServerEvent:Connect(function(player: Player, payload: any)
	if type(payload) ~= "table" or not FX_KINDS[payload.k] then
		return
	end
	if not allow(player, "fx", 8) then
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
local MAX_DISTANCE = 30 -- вход только вблизи зоны (подсказка работает с 14 студов, остальное запас на лаг)
local HOLD_DISTANCE = 25 -- дальше этого от своей дорожки дольше HOLD_GRACE секунд держать её нельзя
local HOLD_GRACE = 3
local farSince: { [Player]: number } = {}

local function leaveAmbush(player: Player)
	farSince[player] = nil
	local s = occupied[player]
	if s then
		occupied[player] = nil
		if s.Parent then
			s:SetAttribute("Occupant", nil)
			s:SetAttribute("OccupantName", nil)
		end
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
	-- уже стоит на дорожке: оставляем её
	local mine = occupied[player]
	if mine and mine.Parent and mine:GetAttribute("Occupant") == player.UserId then
		return true, mine:GetAttribute("Index")
	end
	leaveAmbush(player)
	local pick: BasePart? = nil
	if type(lane) == "number" then
		for _, s in stands do
			if s:GetAttribute("Index") == math.floor(lane) and s:GetAttribute("Occupant") == nil then
				pick = s
				break
			end
		end
	end
	if not pick then
		local best = math.huge
		for _, s in stands do
			if s:GetAttribute("Occupant") == nil then
				local d = (s.Position - hrp.Position).Magnitude
				if d < best then
					best, pick = d, s
				end
			end
		end
	end
	if not pick then
		return false, "Throwing Grounds are full"
	end
	occupied[player] = pick
	pick:SetAttribute("Occupant", player.UserId)
	pick:SetAttribute("OccupantName", player.DisplayName)
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

function Relay.onLeave(player: Player)
	leaveAmbush(player)
	buckets[player] = nil
end

function Relay.onDied(player: Player)
	leaveAmbush(player)
end

return Relay
