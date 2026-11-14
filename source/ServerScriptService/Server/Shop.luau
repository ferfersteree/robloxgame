-- ServerScriptService/Server/Shop.luau
-- Серверная часть Robux-магазина и сохранение.
--   • чеки Developer Products (ProcessReceipt): выдать → сохранить → только потом PurchaseGranted;
--   • владение Game Pass (проверка при входе + покупка прямо в игре);
--   • оплаченное время бустов тикает только пока игрок на сервере;
--   • профиль в DataStore: покупки (shop) и снимок прогресса игрока (save).
-- Экономика пока считается на клиенте (Config.BACKEND = "Demo"), поэтому монеты и стартовый набор
-- сервер кладёт в очередь pending, клиент применяет их и подтверждает вместе с сохранением.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local MarketplaceService = game:GetService("MarketplaceService")
local DataStoreService = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local PolicyService = game:GetService("PolicyService")

local Config = require(RS.Shared.Config)
local SHOP = Config.SHOP

local Shop = {}

local IS_STUDIO = RunService:IsStudio()
local MAX_SAVE_BYTES = 600000
local AUTOSAVE = 120

local profiles: { [Player]: any } = {}
local serverLuck = 0
local store: any = nil
local ShopEv: RemoteEvent
local ShopFn: RemoteFunction

local PASS_BY_ID: { [number]: any } = {}
local PRODUCT_BY_ID: { [number]: any } = {}
for _, it in SHOP.PASSES do
	if it.id > 0 then
		PASS_BY_ID[it.id] = it
	end
end
for _, it in SHOP.PRODUCTS do
	if it.id > 0 then
		PRODUCT_BY_ID[it.id] = it
	end
end

local function newShop(): any
	return { boosts = {}, starter = false, receipts = {}, pending = {}, test = {}, spent = 0, lastGift = 0, exotic = { owned = {}, equipped = {}, level = {}, shards = 0, hatch = {} } }
end

local function deepCopy(t: any): any
	if type(t) ~= "table" then
		return t
	end
	local out = {}
	for k, v in t do
		out[k] = deepCopy(v)
	end
	return out
end

-- V26: ранг поддержки. Пассы считаются по владению (покупка на сайте тоже), товары по чекам.
local function spentOf(prof: any): number
	local total = tonumber(prof.shop.spent) or 0
	for _, it in SHOP.PASSES do
		if prof.passes[it.key] then
			total += it.price
		end
	end
	return total
end

local function rankOf(prof: any): number
	local spent = spentOf(prof)
	local r = 0
	for i, rk in SHOP.RANKS do
		if spent >= rk.at then
			r = i
		end
	end
	return r
end

local function stateOf(prof: any): any
	local boosts = {}
	for id, left in prof.shop.boosts do
		if type(left) == "number" and left > 0 then
			boosts[id] = left
		end
	end
	return {
		passes = prof.passes,
		boosts = boosts,
		server = serverLuck,
		starter = prof.shop.starter == true,
		spent = spentOf(prof),
		rank = rankOf(prof),
		exotic = prof.shop.exotic,
		eggsOff = prof.eggsOff ~= false, -- пока регион не узнан (nil), яйца закрыты
		gift = math.max(0, (tonumber(prof.shop.lastGift) or 0) + SHOP.GIFT_HOURS * 3600 - os.time()),
		pending = prof.shop.pending,
		studio = IS_STUDIO,
		loaded = prof.loaded == true,
	}
end

local function push(player: Player)
	local prof = profiles[player]
	if prof then
		-- V28: надетая экзотика в атрибут игрока ("id,id,id"): по нему клиенты рисуют питомцев с аурой, в том числе чужих
		local E = prof.shop.exotic
		local ids = {}
		for _, id in E.equipped do
			if (E.owned[id] or 0) > 0 and #ids < Config.EXOTIC.EQUIP_MAX then
				table.insert(ids, id)
			end
		end
		player:SetAttribute("Exo", table.concat(ids, ","))
		if prof.busy then
			return -- идёт выдача и сохранение: неподтверждённое не показываем клиенту, после неё будет push
		end
		ShopEv:FireClient(player, "state", stateOf(prof))
	end
end

local function pushAll()
	for player in profiles do
		push(player)
	end
end

---------------------------------------------------------------------
-- VIP: атрибут (читает чат на клиенте) и табличка над головой
---------------------------------------------------------------------
local function badgeOf(prof: any): (string?, Color3, Color3, number)
	local r = rankOf(prof)
	local rk = SHOP.RANKS[r]
	if prof.passes.founder then
		return "FOUNDER", Color3.fromRGB(196, 130, 255), Color3.fromRGB(190, 150, 255), 22
	elseif rk then
		return string.upper(rk.name), rk.color, rk.color, 6 + r * 4
	elseif prof.passes.vip then
		return "VIP", Color3.fromRGB(255, 210, 62), Color3.fromRGB(255, 210, 62), 5
	end
	return nil, Color3.new(1, 1, 1), Color3.new(1, 1, 1), 0
end

-- Метка над головой и аура: видны всем игрокам. Метка VIP и метка ранга - одна и та же табличка.
local function vipTag(player: Player)
	local prof = profiles[player]
	local char = player.Character
	if not prof or not char then
		return
	end
	local head = char:WaitForChild("Head", 5)
	if not head then
		return
	end
	local label, color, aura, rate = badgeOf(prof)
	local old = head:FindFirstChild("VipTag")
	if old then
		old:Destroy()
	end
	local oldAura = char:FindFirstChild("RankAura", true)
	if oldAura then
		oldAura:Destroy()
	end
	if not label then
		return
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = "VipTag"
	bb.Size = UDim2.fromOffset(110, 26)
	bb.StudsOffset = Vector3.new(0, 3.1, 0)
	bb.MaxDistance = 90
	bb.ResetOnSpawn = false
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Font = Enum.Font.FredokaOne
	l.Text = label
	l.TextScaled = true
	l.TextColor3 = color
	l.TextStrokeColor3 = Color3.fromRGB(74, 38, 0)
	l.TextStrokeTransparency = 0
	l.Parent = bb
	bb.Parent = head
	local root = char:FindFirstChild("HumanoidRootPart")
	if root and rate > 0 then
		local e = Instance.new("ParticleEmitter")
		e.Name = "RankAura"
		e.Rate = rate
		e.Lifetime = NumberRange.new(0.9, 1.5)
		e.Speed = NumberRange.new(0.5, 2)
		e.SpreadAngle = Vector2.new(180, 180)
		e.Acceleration = Vector3.new(0, 2.5, 0)
		e.LightEmission = 0.7
		e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 0) })
		e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1) })
		e.Color = ColorSequence.new(aura)
		e.Parent = root
	end
end

local function refreshVip(player: Player)
	local prof = profiles[player]
	if not prof then
		return
	end
	local label = badgeOf(prof)
	player:SetAttribute("VIP", prof.passes.vip == true)
	player:SetAttribute("Rank", rankOf(prof))
	if not label then
		return
	end
	if not prof.vipConn then
		prof.vipConn = player.CharacterAdded:Connect(function()
			task.defer(vipTag, player)
		end)
	end
	task.spawn(vipTag, player)
end

---------------------------------------------------------------------
-- DataStore
---------------------------------------------------------------------
local function keyOf(player: Player): string
	return "u_" .. tostring(player.UserId)
end

local function saveProfile(player: Player, prof: any): boolean
	if not prof.loaded then
		return false
	end
	if prof.noStore or not store then
		return true -- Studio без доступа к DataStore: играем без сохранения
	end
	local data = { v = 1, t = os.time(), save = prof.save, shop = prof.shop }
	local ok, err = pcall(function()
		store:SetAsync(keyOf(player), data, { player.UserId })
	end)
	if ok then
		prof.dirty = false
		prof.lastSave = os.clock()
	else
		warn("[Shop] save failed for " .. player.Name .. ": " .. tostring(err))
	end
	return ok
end

local function loadProfile(player: Player)
	local prof: any = { loaded = false, failed = false, noStore = false, save = nil, shop = newShop(), passes = {}, dirty = false, lastSave = os.clock(), lastReq = 0 }
	profiles[player] = prof
	local ok, data = false, nil
	if store then
		for attempt = 1, 3 do
			ok, data = pcall(function()
				return store:GetAsync(keyOf(player))
			end)
			if ok then
				break
			end
			warn("[Shop] load attempt " .. attempt .. " failed for " .. player.Name .. ": " .. tostring(data))
			task.wait(attempt * 2)
		end
	end
	if profiles[player] ~= prof then
		return -- игрок вышел, пока грузились
	end
	-- V28: правила Roblox для платных случайных предметов. В некоторых регионах их продавать нельзя. Спрашиваем PolicyService
	-- ДО того, как профиль станет loaded, чтобы клиент не увидел яйца раньше проверки. Если спросить не вышло,
	-- вне Studio считаем, что нельзя. Чек на яйцо, пришедший всё равно (игрок уже заплатил), выдаётся.
	do
		local okPol, pol = pcall(function()
			return PolicyService:GetPolicyInfoForPlayerAsync(player)
		end)
		if okPol and type(pol) == "table" then
			prof.eggsOff = pol.ArePaidRandomItemsRestricted == true
		else
			prof.eggsOff = not IS_STUDIO
		end
	end
	if profiles[player] ~= prof then
		return
	end
	if ok then
		if type(data) == "table" then
			if type(data.save) == "table" then
				prof.save = data.save
			end
			local s = data.shop
			if type(s) == "table" then
				local shop = prof.shop
				if type(s.boosts) == "table" then
					for id, left in s.boosts do
						if type(id) == "string" and type(left) == "number" and left > 0 then
							shop.boosts[id] = left
						end
					end
				end
				shop.starter = s.starter == true
				shop.spent = tonumber(s.spent) or 0
				shop.lastGift = tonumber(s.lastGift) or 0
				-- V28: экзотика (купленная, надетая, уровни, осколки, очередь вылупления): берём только значимые поля
				local ex = s.exotic
				if type(ex) == "table" then
					local E = shop.exotic
					for id, n in (type(ex.owned) == "table" and ex.owned or {}) do
						if type(id) == "string" and Config.EXOTIC_BY_ID[id] and type(n) == "number" and n > 0 then
							E.owned[id] = n
						end
					end
					for id, n in (type(ex.level) == "table" and ex.level or {}) do
						if type(id) == "string" and E.owned[id] and type(n) == "number" then
							E.level[id] = math.clamp(math.floor(n), 0, Config.EXOTIC.MAX_LEVEL)
						end
					end
					for _, id in (type(ex.equipped) == "table" and ex.equipped or {}) do
						if type(id) == "string" and E.owned[id] and not table.find(E.equipped, id) and #E.equipped < Config.EXOTIC.EQUIP_MAX then
							table.insert(E.equipped, id)
						end
					end
					E.shards = math.max(0, tonumber(ex.shards) or 0)
					for _, h in (type(ex.hatch) == "table" and ex.hatch or {}) do
						if type(h) == "table" and type(h.id) == "string" and type(h.sp) == "string" and Config.EXOTIC_BY_ID[h.sp] then
							table.insert(E.hatch, h)
						end
					end
				end
				if type(s.receipts) == "table" then
					shop.receipts = s.receipts
				end
				if type(s.pending) == "table" then
					shop.pending = s.pending
				end
				if type(s.test) == "table" then
					shop.test = s.test
				end
			end
		end
		prof.loaded = true
	elseif IS_STUDIO then
		prof.loaded = true
		prof.noStore = true
		warn("[Shop] DataStore is unavailable in Studio: playing without saving (enable Studio access to API services)")
	else
		prof.failed = true
		warn("[Shop] could not load data for " .. player.Name .. ": shop and saving are disabled for this session")
	end
	for _, it in SHOP.PASSES do
		if it.id > 0 then
			local okp, owns = pcall(function()
				return MarketplaceService:UserOwnsGamePassAsync(player.UserId, it.id)
			end)
			if okp and owns then
				prof.passes[it.key] = true
			end
		elseif IS_STUDIO and prof.shop.test[it.key] then
			prof.passes[it.key] = true
		end
	end
	if profiles[player] ~= prof then
		return
	end
	refreshVip(player)
	push(player)
end

---------------------------------------------------------------------
-- Выдача товара
---------------------------------------------------------------------
-- V28: яйцо. Бросок только здесь, на сервере, по таблице Config.EGGS (той же, что видит игрок). Вызывается из applyProduct,
-- а значит внутри processReceipt: чек и выдача сохраняются вместе, повтор чека не даст второе животное.
local eggRng = Random.new()
local function rollEgg(prof: any, item: any, purchaseId: string)
	local id = Config.eggRoll(item.key, eggRng)
	local ex = id and Config.EXOTIC_BY_ID[id]
	if not ex then
		return
	end
	local E = prof.shop.exotic
	local dupe = (E.owned[id] or 0) > 0
	E.owned[id] = (E.owned[id] or 0) + 1
	local shards = 0
	if dupe then
		shards = Config.EXOTIC.SHARDS[ex.rarity]
		E.shards += shards
	end
	table.insert(E.hatch, { id = purchaseId, sp = id, dupe = dupe, shards = shards, egg = item.key })
	while #E.hatch > 100 do
		table.remove(E.hatch, 1)
	end
end

local function applyProduct(prof: any, item: any, purchaseId: string)
	local s = prof.shop
	if item.kind == "boost" then
		for _, id in item.boosts do
			s.boosts[id] = (s.boosts[id] or 0) + item.dur
		end
	elseif item.kind == "egg" then
		rollEgg(prof, item, purchaseId)
	elseif item.kind == "server" then
		serverLuck += item.dur
	elseif item.kind == "coins" then
		table.insert(s.pending, { id = purchaseId, kind = "coins", k = item.k, key = item.key })
	elseif item.kind == "starter" then
		s.starter = true
		table.insert(s.pending, { id = purchaseId, kind = "starter", key = item.key })
		local st = SHOP.STARTER
		s.boosts[st.boost] = (s.boosts[st.boost] or 0) + st.dur
	end
end

local function afterGrant(player: Player, item: any)
	if item.kind == "server" then
		pushAll()
		ShopEv:FireAllClients("announce", player.DisplayName .. " activated Server Luck x2 for " .. math.floor(item.dur / 60) .. " min!")
	else
		push(player)
	end
	ShopEv:FireClient(player, "granted", item.key)
end

local function processReceipt(info: any): Enum.ProductPurchaseDecision
	local player = Players:GetPlayerByUserId(info.PlayerId)
	local prof = player and profiles[player]
	if not player or not prof or not prof.loaded or prof.busy then
		-- busy: другой чек сейчас выдаётся и сохраняется; Roblox повторит этот чек позже (иначе откат одного затирал бы другой)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local item = PRODUCT_BY_ID[info.ProductId]
	if not item then
		warn("[Shop] unknown product id " .. tostring(info.ProductId))
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local pid = tostring(info.PurchaseId)
	if table.find(prof.shop.receipts, pid) then
		return Enum.ProductPurchaseDecision.PurchaseGranted
	end
	local backup = deepCopy(prof.shop)
	local luckBackup = serverLuck
	prof.busy = true
	applyProduct(prof, item, pid)
	prof.shop.spent = (tonumber(prof.shop.spent) or 0) + (tonumber(info.CurrencySpent) or item.price)
	table.insert(prof.shop.receipts, pid)
	while #prof.shop.receipts > 80 do
		table.remove(prof.shop.receipts, 1)
	end
	local saved = saveProfile(player, prof)
	prof.busy = false
	if not saved then
		prof.shop = backup
		serverLuck = luckBackup
		push(player)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	afterGrant(player, item)
	refreshVip(player)
	return Enum.ProductPurchaseDecision.PurchaseGranted
end

---------------------------------------------------------------------
-- Запросы клиента
---------------------------------------------------------------------
local function onInvoke(player: Player, action: any, a: any, b: any): ...any
	if action == "load" then
		local t0 = os.clock()
		while os.clock() - t0 < 25 do
			local p = profiles[player]
			if p and (p.loaded or p.failed) then
				break
			end
			task.wait(0.2)
		end
		local prof = profiles[player]
		if not prof or not prof.loaded then
			return false
		end
		return true, prof.save, stateOf(prof)
	end
	local prof = profiles[player]
	if not prof or not prof.loaded or prof.busy then
		return false -- busy: идёт выдача покупки, запросы ждут (клиент повторит)
	end
	if action == "save" then
		local now = os.clock()
		if now - prof.lastReq < 1 or type(a) ~= "table" then
			return false
		end
		prof.lastReq = now
		local okJ, json = pcall(function()
			return HttpService:JSONEncode(a)
		end)
		if not okJ or #json > MAX_SAVE_BYTES then
			return false
		end
		prof.save = a
		prof.dirty = true
		if type(b) == "table" then
			local changed = false
			local pending = prof.shop.pending
			for _, id in b do
				for i = #pending, 1, -1 do
					if pending[i].id == id then
						table.remove(pending, i)
						changed = true
					end
				end
			end
			if changed then
				-- монеты уже в снимке: сразу пишем, чтобы не выдать их второй раз
				saveProfile(player, prof)
				push(player)
			end
		end
		return true
	elseif action == "testBuy" then
		-- Только Studio и только для товаров без id: проверить магазин без Robux
		local item = type(a) == "string" and Config.SHOP_BY_KEY[a] or nil
		if not IS_STUDIO or not item or item.id ~= 0 then
			return false
		end
		if item.kind == "egg" and prof.eggsOff then
			return false
		end
		if item.pass then
			prof.shop.test[item.key] = true
			prof.passes[item.key] = true
			prof.dirty = true
			refreshVip(player)
			push(player)
			ShopEv:FireClient(player, "granted", item.key)
		else
			applyProduct(prof, item, "test_" .. HttpService:GenerateGUID(false))
			prof.shop.spent = (tonumber(prof.shop.spent) or 0) + item.price
			prof.dirty = true
			afterGrant(player, item)
		end
		refreshVip(player)
		push(player)
		return true
	elseif action == "claimGift" then
		-- Ежедневный подарок: таймер на сервере, монеты идут через очередь pending
		local now = os.time()
		if now - (tonumber(prof.shop.lastGift) or 0) < SHOP.GIFT_HOURS * 3600 then
			return false
		end
		local r = rankOf(prof)
		local k = SHOP.RANKS[r] and SHOP.RANKS[r].gift or SHOP.GIFT_BASE
		if prof.passes.founder then
			k += 0.05
		end
		prof.shop.lastGift = now
		table.insert(prof.shop.pending, { id = "gift_" .. tostring(now), kind = "coins", k = k, key = "gift" })
		prof.dirty = true
		saveProfile(player, prof)
		push(player)
		return true
	elseif action == "exoticEquip" or action == "exoticUnequip" then
		-- V28: надеть / снять экзотику (только купленную, не больше EQUIP_MAX)
		local E = prof.shop.exotic
		if type(a) ~= "string" or (E.owned[a] or 0) <= 0 then
			return false
		end
		local i = table.find(E.equipped, a)
		if action == "exoticEquip" then
			if i or #E.equipped >= Config.EXOTIC.EQUIP_MAX then
				return false
			end
			table.insert(E.equipped, a)
		else
			if not i then
				return false
			end
			table.remove(E.equipped, i)
		end
		prof.dirty = true
		push(player)
		return true
	elseif action == "exoticUpgrade" then
		-- улучшить вид за осколки (их дают повторы)
		local E = prof.shop.exotic
		local ex = type(a) == "string" and Config.EXOTIC_BY_ID[a] or nil
		if not ex or (E.owned[a] or 0) <= 0 then
			return false
		end
		local lvl = E.level[a] or 0
		if lvl >= Config.EXOTIC.MAX_LEVEL then
			return false
		end
		local cost = Config.exoticUpgradeCost(ex, lvl)
		if E.shards < cost then
			return false
		end
		E.shards -= cost
		E.level[a] = lvl + 1
		prof.dirty = true
		saveProfile(player, prof)
		push(player)
		return true
	elseif action == "hatchAck" then
		-- клиент показал вылупление: убираем из очереди (само животное уже выдано)
		local E = prof.shop.exotic
		if type(a) == "table" then
			for _, hid in a do
				for i = #E.hatch, 1, -1 do
					if E.hatch[i].id == hid then
						table.remove(E.hatch, i)
					end
				end
			end
			prof.dirty = true
		end
		return true
	end
	return false
end

---------------------------------------------------------------------
function Shop.start()
	local folder = RS:WaitForChild("Remotes")
	local ev = folder:FindFirstChild("Shop")
	if not ev then
		ev = Instance.new("RemoteEvent")
		ev.Name = "Shop"
		ev.Parent = folder
	end
	local fn = folder:FindFirstChild("ShopRequest")
	if not fn then
		fn = Instance.new("RemoteFunction")
		fn.Name = "ShopRequest"
		fn.Parent = folder
	end
	ShopEv = ev :: RemoteEvent
	ShopFn = fn :: RemoteFunction

	local okStore, res = pcall(function()
		return DataStoreService:GetDataStore(SHOP.DATASTORE)
	end)
	if okStore then
		store = res
	else
		warn("[Shop] DataStore is unavailable: " .. tostring(res))
	end

	ShopFn.OnServerInvoke = onInvoke
	MarketplaceService.ProcessReceipt = processReceipt
	MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player: Player, passId: number, purchased: boolean)
		local item = PASS_BY_ID[passId]
		local prof = profiles[player]
		if purchased and item and prof then
			prof.passes[item.key] = true
			refreshVip(player)
			push(player)
			ShopEv:FireClient(player, "granted", item.key)
		end
	end)

	Players.PlayerAdded:Connect(function(player)
		task.spawn(loadProfile, player)
	end)
	for _, player in Players:GetPlayers() do
		task.spawn(loadProfile, player)
	end
	Players.PlayerRemoving:Connect(function(player)
		local prof = profiles[player]
		profiles[player] = nil
		if prof then
			if prof.vipConn then
				prof.vipConn:Disconnect()
			end
			saveProfile(player, prof)
		end
	end)
	game:BindToClose(function()
		local n = 0
		for player, prof in profiles do
			n += 1
			task.spawn(function()
				saveProfile(player, prof)
				n -= 1
			end)
		end
		local t0 = os.clock()
		while n > 0 and os.clock() - t0 < 20 do
			task.wait(0.1)
		end
	end)

	-- Оплаченное время идёт только пока игрок на сервере
	task.spawn(function()
		local sync = 0
		while true do
			local dt = task.wait(1)
			sync += dt
			local luckWas = serverLuck
			if serverLuck > 0 then
				serverLuck = math.max(0, serverLuck - dt)
			end
			for player, prof in profiles do
				if prof.loaded and not prof.busy then
					for id, left in prof.shop.boosts do
						local v = left - dt
						prof.shop.boosts[id] = if v > 0 then v else nil
						prof.dirty = true
					end
					if prof.dirty and os.clock() - prof.lastSave > AUTOSAVE then
						prof.lastSave = os.clock()
						task.spawn(saveProfile, player, prof)
					end
				end
			end
			if sync >= 30 or (luckWas > 0 and serverLuck == 0) then
				sync = 0
				pushAll()
			end
		end
	end)
end

-- Только Studio: хук для проверок (подмена DataStore, чеки, перезаход) без настоящих покупок.
if IS_STUDIO then
	Shop._test = {
		profiles = profiles,
		processReceipt = processReceipt,
		loadProfile = loadProfile,
		saveProfile = saveProfile,
		stateOf = stateOf,
		invoke = onInvoke,
		setStore = function(s: any)
			store = s
		end,
		addProduct = function(item: any)
			PRODUCT_BY_ID[item.id] = item
		end,
	}
end

return Shop
