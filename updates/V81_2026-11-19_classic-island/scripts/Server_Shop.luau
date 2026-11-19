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
-- V45: замок сессии. Профиль в DataStore помечен номером сервера (game.JobId): второй сервер не может загрузить его
-- и перезаписать, пока первый не отпустил (выход игрока, закрытие сервера) или не затих дольше LOCK_TTL.
-- Раньше два сервера писали профиль через SetAsync «кто последний»: игрок, зашедший на второй сервер до сохранения
-- на первом, мог затереть свежие покупки, чеки и экзотику.
local JOB_ID: string = if game.JobId ~= "" then game.JobId else ("studio_" .. HttpService:GenerateGUID(false))
local LOCK_TTL = 180 -- замок, не обновлявшийся дольше, считается брошенным (сервер упал)
local LOCK_REFRESH = 60 -- как часто сервер подтверждает замок, даже если сохранять нечего
local LOCK_WAIT = 30 -- сколько секунд входящий игрок ждёт, пока прежний сервер отпустит профиль

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
	return { boosts = {}, starter = false, receipts = {}, pending = {}, test = {}, spent = 0, lastGift = 0, exotic = { owned = {}, equipped = {}, level = {}, shards = 0, hatch = {} }, hpass = { season = -1, premium = false, claimed = {} }, hpassCos = {}, hpassBundleXp = 0 }
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

-- V71: Hunter Pass. Цвет в сохранении: { r, g, b } 0..255 (Color3 в DataStore не кладём)
local function colorToSave(c: Color3): { number }
	return { math.floor(c.R * 255 + 0.5), math.floor(c.G * 255 + 0.5), math.floor(c.B * 255 + 0.5) }
end

local function colorFromSave(t: any): Color3?
	if type(t) ~= "table" then
		return nil
	end
	local r, g, b = tonumber(t[1]), tonumber(t[2]), tonumber(t[3])
	if not r or not g or not b or r ~= r or g ~= g or b ~= b then
		return nil
	end
	return Color3.fromRGB(math.clamp(r, 0, 255), math.clamp(g, 0, 255), math.clamp(b, 0, 255))
end

-- Тексты тегов и названия аур, которые пропуск вообще выдаёт (из сохранения берём только их)
local PASS_TAGS: { [string]: boolean } = {}
local PASS_AURAS: { [string]: boolean } = {}
for _, r in Config.PASS.REWARDS do
	for _, lane in { r.free, r.premium } do
		for _, it in lane do
			if it.type == "tag" then
				PASS_TAGS[it.text] = true
			elseif it.type == "aura" then
				PASS_AURAS[it.name] = true
			end
		end
	end
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
	-- V71: пропуск показываем только за текущий сезон (старый сезон = пусто)
	local hp = prof.shop.hpass
	local hpassCur = type(hp) == "table" and hp.season == Config.passSeason()
	return {
		hpass = {
			season = Config.passSeason(),
			premium = hpassCur and hp.premium == true,
			claimed = hpassCur and hp.claimed or {},
		},
		hpassCos = prof.shop.hpassCos,
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
	-- V71: тег и аура Hunter Pass, когда нет FOUNDER/ранга/VIP (аура у тех уже есть)
	local cos = prof.shop.hpassCos
	if type(cos) == "table" then
		local tag = type(cos.tag) == "string" and cos.tag or nil
		local tagColor = colorFromSave(cos.tagColor) or Color3.new(1, 1, 1)
		local auraColor = colorFromSave(cos.aura)
		if tag or auraColor then
			return tag, tagColor, auraColor or tagColor, auraColor and 6 or 0
		end
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
	if not label and rate == 0 then
		return
	end
	if label then
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
	end
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
	local label, _, _, rate = badgeOf(prof)
	player:SetAttribute("VIP", prof.passes.vip == true)
	player:SetAttribute("Rank", rankOf(prof))
	if not label and rate == 0 then
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

local function defaultKick(player: any, msg: string)
	if player.Parent then
		player:Kick(msg)
	end
end
local kick: (any, string) -> () = defaultKick

-- Держит ли профиль другой сервер (замок свежий и чужой)
local function lockedByOther(old: any): boolean
	if type(old) ~= "table" or type(old.lock) ~= "table" then
		return false
	end
	if old.lock.id == JOB_ID then
		return false
	end
	return os.time() - (tonumber(old.lock.t) or 0) < LOCK_TTL
end

-- release = true: убрать замок (игрок вышел, сервер закрывается). Если профиль уже у другого сервера, ничего не пишем.
local function saveProfile(player: Player, prof: any, release: boolean?): boolean
	if not prof.loaded then
		return false
	end
	if prof.noStore or not store then
		return true -- Studio без доступа к DataStore: играем без сохранения
	end
	if prof.lockLost then
		return false -- профиль теперь у другого сервера: не перезаписываем
	end
	local data: any = { v = 1, t = os.time(), save = prof.save, shop = prof.shop }
	local lost = false
	local ok, err = pcall(function()
		if store.UpdateAsync then
			store:UpdateAsync(keyOf(player), function(old)
				lost = false
				if lockedByOther(old) then
					lost = true
					return nil
				end
				data.lock = if release then nil else { id = JOB_ID, t = os.time() }
				return data, { player.UserId }
			end)
		else
			store:SetAsync(keyOf(player), data, { player.UserId })
		end
	end)
	if ok and lost then
		prof.lockLost = true
		warn("[Shop] profile of " .. player.Name .. " is held by another server: not saving, the player is asked to rejoin")
		task.defer(kick, player, "Your account was opened on another server. Please rejoin.")
		return false
	end
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
	local lockBlocked = false
	if store then
		local t0 = os.clock()
		local attempt = 0
		while true do
			attempt += 1
			local blocked = false
			ok, data = pcall(function()
				if store.UpdateAsync then
					-- забираем замок и читаем профиль одним атомарным действием
					return store:UpdateAsync(keyOf(player), function(old)
						blocked = false
						if lockedByOther(old) then
							blocked = true
							return nil
						end
						local rec: any = if type(old) == "table" then old else { v = 1 }
						rec.lock = { id = JOB_ID, t = os.time() }
						return rec, { player.UserId }
					end)
				end
				return store:GetAsync(keyOf(player))
			end)
			if ok and not blocked then
				break
			end
			if ok and blocked then
				-- прежний сервер ещё не отпустил профиль (игрок только что вышел): ждём
				if os.clock() - t0 >= LOCK_WAIT then
					lockBlocked = true
					ok = false
					break
				end
				task.wait(2)
			else
				warn("[Shop] load attempt " .. attempt .. " failed for " .. player.Name .. ": " .. tostring(data))
				if attempt >= 3 then
					break
				end
				task.wait(attempt * 2)
			end
			if profiles[player] ~= prof then
				return
			end
		end
	end
	if profiles[player] ~= prof then
		return -- игрок вышел, пока грузились
	end
	if lockBlocked then
		prof.failed = true
		prof.lockLost = true
		warn("[Shop] profile of " .. player.Name .. " is still held by another server: asking the player to rejoin")
		task.defer(kick, player, "Your previous session is still saving. Please rejoin in a minute.")
		return
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
					-- V71: Hunter Pass: премиум, забранные серверные награды, косметика (теги/ауры только из таблицы пропуска)
				local hp = s.hpass
				if type(hp) == "table" then
					local season = tonumber(hp.season)
					shop.hpass.season = if season and season == season then math.floor(season) else -1
					shop.hpass.premium = hp.premium == true
					for key, v in (type(hp.claimed) == "table" and hp.claimed or {}) do
						if type(key) == "string" and v == true and key:match("^[fp]%d+$") then
							shop.hpass.claimed[key] = true
						end
					end
				end
				local bx = tonumber(s.hpassBundleXp)
				shop.hpassBundleXp = if bx and bx == bx then math.clamp(bx, 0, 100000) else 0
				local cs = s.hpassCos
				if type(cs) == "table" then
					local cos = shop.hpassCos
					cos.tags = {}
					for _, t in (type(cs.tags) == "table" and cs.tags or {}) do
						if type(t) == "string" and PASS_TAGS[t] and not table.find(cos.tags, t) then
							table.insert(cos.tags, t)
						end
					end
					local tc = colorFromSave(cs.tagColor)
					if type(cs.tag) == "string" and PASS_TAGS[cs.tag] and tc then
						cos.tag = cs.tag
						cos.tagColor = colorToSave(tc)
					end
					local ac = colorFromSave(cs.aura)
					if type(cs.auraName) == "string" and PASS_AURAS[cs.auraName] and ac then
						cos.auraName = cs.auraName
						cos.aura = colorToSave(ac)
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
	elseif item.kind == "hpass" then
		-- V71: Hunter Pass: премиум на текущий сезон; бандл ещё кладёт опыт в очередь (клиент добавит и подтвердит)
		local n = Config.passSeason()
		if type(s.hpass) ~= "table" or s.hpass.season ~= n then
			s.hpass = { season = n, premium = false, claimed = {} }
			s.hpassBundleXp = 0
		end
		s.hpass.premium = true
		if item.xp then
			s.hpassBundleXp = (tonumber(s.hpassBundleXp) or 0) + item.xp
			table.insert(s.pending, { id = purchaseId, kind = "hpassxp", xp = item.xp, season = n, key = item.key })
		end
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
	-- выдача и сохранение в pcall: даже при ошибке busy снимается, иначе профиль завис бы до конца сессии
	local okRun, saved = pcall(function()
		applyProduct(prof, item, pid)
		prof.shop.spent = (tonumber(prof.shop.spent) or 0) + (tonumber(info.CurrencySpent) or item.price)
		table.insert(prof.shop.receipts, pid)
		while #prof.shop.receipts > 80 do
			table.remove(prof.shop.receipts, 1)
		end
		return saveProfile(player, prof)
	end)
	prof.busy = false
	if not okRun then
		warn("[Shop] receipt " .. pid .. " failed: " .. tostring(saved))
		saved = false
	end
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
-- V71: награда Hunter Pass серверного ряда (яйцо, буст, тег, аура)
---------------------------------------------------------------------
local function hpassClaim(player: Player, prof: any, tierArg: any, lane: any): boolean
	local P = Config.PASS
	local tier = tonumber(tierArg)
	if not tier or tier ~= tier or tier ~= math.floor(tier) or tier < 1 or tier > P.TIERS then
		return false
	end
	if lane ~= "f" and lane ~= "p" then
		return false
	end
	local n = Config.passSeason()
	local s = prof.shop
	if type(s.hpass) ~= "table" or s.hpass.season ~= n then
		s.hpass = { season = n, premium = false, claimed = {} }
		s.hpassBundleXp = 0
	end
	local hp = s.hpass
	if lane == "p" and not hp.premium then
		return false
	end
	local key = lane .. tier
	-- V74: часть премиум-уровней переехала с клиентской выдачи (монеты, Сила) на серверную: кто уже забрал такой
	-- уровень раньше, отмечен только в клиентском сохранении. Учитываем и эту отметку, чтобы не выдать второй раз.
	local sv = prof.save
	local svh = type(sv) == "table" and sv.hpass or nil
	if type(svh) == "table" and svh.season == n and type(svh.claimed) == "table" and svh.claimed[key] == true then
		return false
	end
	if hp.claimed[key] then
		return false
	end
	local r = P.REWARDS[tier]
	local list = r and (if lane == "f" then r.free else r.premium)
	if not list or Config.passSide(list) ~= "server" then
		return false
	end
	-- опыт берём из снимка клиента, но не выше того, что можно набрать за время сезона (+ бандл)
	local sv = type(prof.save) == "table" and prof.save.hpass or nil
	if type(sv) ~= "table" or sv.season ~= n then
		return false
	end
	local xp = tonumber(sv.xp) or 0
	if xp ~= xp then
		return false
	end
	if not IS_STUDIO then
		local cap = (Config.passDay() + 1) * 300 + (Config.passWeek() + 1) * 1200 + (tonumber(s.hpassBundleXp) or 0)
		xp = math.min(xp, cap)
	end
	xp = math.min(xp, P.TIERS * P.XP_PER_TIER)
	if Config.passTier(xp) < tier then
		return false
	end
	local backup = deepCopy(s)
	hp.claimed[key] = true -- метка до любых yield
	local rewardId = "hpass_" .. n .. "_" .. key
	local okG, err = pcall(function()
		for _, it in list do
			if it.type == "egg" then
				local egg = Config.SHOP_BY_KEY[it.key]
				if prof.eggsOff then
					table.insert(s.pending, { id = rewardId, kind = "coins", k = 0.5, key = "hpass" })
				elseif egg then
					rollEgg(prof, egg, rewardId)
				end
			elseif it.type == "boost" then
				local item = Config.SHOP_BY_KEY[it.key]
				if item and item.boosts then
					for _, id in item.boosts do
						s.boosts[id] = (s.boosts[id] or 0) + item.dur
					end
				end
			elseif it.type == "tag" then
				local cos = s.hpassCos
				cos.tags = cos.tags or {}
				if not table.find(cos.tags, it.text) then
					table.insert(cos.tags, it.text)
				end
				cos.tag = it.text
				cos.tagColor = colorToSave(it.color)
			elseif it.type == "shards" then
				-- V74: осколки питомцев
				local E = s.exotic
				E.shards = (tonumber(E.shards) or 0) + math.max(0, math.floor(tonumber(it.n) or 0))
			elseif it.type == "aura" then
				s.hpassCos.auraName = it.name
				s.hpassCos.aura = colorToSave(it.color)
			end
		end
	end)
	if not okG then
		warn("[Shop] hpassClaim " .. key .. " failed: " .. tostring(err))
		prof.shop = backup
		return false
	end
	prof.dirty = true
	-- busy: пока идёт сохранение, другие запросы (save/чеки) ждут, иначе откат вернул бы уже подтверждённое
	prof.busy = true
	local okS, saved = pcall(saveProfile, player, prof)
	prof.busy = false
	if not okS or not saved then
		prof.shop = backup
		push(player)
		return false
	end
	refreshVip(player)
	push(player)
	ShopEv:FireClient(player, "hpassGranted", { tier = tier, lane = lane })
	return true
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
	elseif action == "hpassClaim" then
		return hpassClaim(player, prof, a, b)
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
			saveProfile(player, prof, true)
		end
	end)
	game:BindToClose(function()
		local n = 0
		for player, prof in profiles do
			n += 1
			task.spawn(function()
				saveProfile(player, prof, true)
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
					if (prof.dirty and os.clock() - prof.lastSave > AUTOSAVE) or os.clock() - prof.lastSave > LOCK_REFRESH then
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
		-- V45: проверка замка сессии: притвориться другим сервером и сократить время ожидания
		setJobId = function(id: string)
			JOB_ID = id
		end,
		getJobId = function(): string
			return JOB_ID
		end,
		setKick = function(f: ((any, string) -> ())?)
			kick = f or defaultKick
		end,
		setLockTimes = function(ttl: number?, wait: number?, refresh: number?)
			LOCK_TTL = ttl or LOCK_TTL
			LOCK_WAIT = wait or LOCK_WAIT
			LOCK_REFRESH = refresh or LOCK_REFRESH
		end,
		addProduct = function(item: any)
			PRODUCT_BY_ID[item.id] = item
		end,
	}
end

return Shop
