-- StarterPlayerScripts/Client/DemoServer.luau
-- ФЕЙКОВЫЙ БЭКЕНД для демо-режима: та же логика и те же ответы, что описаны в docs/BACKEND.md,
-- но всё считается на клиенте. Настоящий сервер должен повторить эти обработчики на своей стороне.
local RS = game:GetService("ReplicatedStorage")

local Config = require(RS.Shared.Config)
local Roll = require(RS.Shared.Roll)
local Perks = require(script.Parent.Perks)

local Demo = {}

local rng = Random.new()
local d: any = nil
local nextId = 1
local tension: { token: number, crashAt: number, t0: number }? = nil
local token = 0
local lastRep = 0
local demoLuck = 1

local emitFn: (string, any) -> () = function() end
function Demo.setEmitter(fn: (string, any) -> ())
	emitFn = fn
end
local function notify(text: string, kind: string?)
	emitFn("notify", { text = text, kind = kind or "info" })
end

local function defaults()
	local q = {}
	for i = 1, 3 do
		local cq = Config.QUESTS[i]
		q[cq.id] = { p = 0, done = false, claimed = false }
	end
	return {
		coins = Config.START.coins,
		power = Config.START.power,
		level = 1,
		xp = 0,
		bagLvl = 1,
		bagCap = Config.BAG[1].cap,
		dumbbell = Config.START.dumbbell,
		spear = Config.START.spear,
		spears = { [Config.START.spear] = 0 },
		items = {},
		index = {},
		stats = { catches = 0, throws = 0, crashes = 0, bestMult = 1, bestDist = 0, sold = 0, earned = 0, rangeBest = 0, courseBest = 0 },
		quests = q,
		questNext = 4,
		boosts = {},
		collected = {},
		flags = {},
		tutorial = 1,
		settings = { music = true, sfx = true, skip = false, lowFx = false },
		market = { sold = {} },
	}
end
d = defaults()

function Demo.data(): any
	return d
end

-- Буст активен, если идёт зелье за монеты ИЛИ оплаченное время из Robux-магазина
local function boostOn(id: string): boolean
	local ends = d.boosts[id]
	return (type(ends) == "number" and ends > os.time()) or Perks.boostLeft(id) > 0
end

local function boostMult(id: string): number
	local on = boostOn(id)
	if id == "luck" then
		return Perks.luckMult(on)
	elseif id == "coins" then
		return Perks.coinMult(on)
	end
	local m = on and Config.BOOSTS[id].mult or 1
	-- V28: экзотика меняет дальность броска и устойчивость натяжения
	if id == "range" then
		m *= Perks.rangeMul()
	elseif id == "tension" then
		m *= Perks.gripMul()
	end
	return m
end

-- Вместимость сумки = уровень сумки + бонус пасса Big Game Bag
local function applyPerks()
	local lvl = math.clamp(math.floor(tonumber(d.bagLvl) or 1), 1, #Config.BAG)
	d.bagLvl = lvl
	d.bagCap = math.max(6, Config.BAG[lvl].cap + Perks.bagBonus())
end

local function addBoost(id: string, dur: number)
	local now = os.time()
	local cur = d.boosts[id]
	d.boosts[id] = math.max(cur or now, now) + dur
	emitFn("boost", { id = id, dur = dur })
end

local function addCoins(n: number)
	d.coins += n
	if n > 0 then
		d.stats.earned += n
	end
end

local function addXp(n: number)
	n = math.floor(n * Perks.xpMult() + 0.5)
	d.xp += n
	local ups = 0
	while d.xp >= Config.xpForLevel(d.level) do
		d.xp -= Config.xpForLevel(d.level)
		d.level += 1
		ups += 1
		local reward = Config.levelReward(d.level)
		addCoins(reward)
		emitFn("levelup", { level = d.level, reward = reward })
	end
	return ups
end

-- Прогресс заданий
local function progress(kind: string, arg: any, amount: number)
	for id, st in d.quests do
		local q = Config.QUEST_BY_ID[id]
		if q and not st.done and q.kind == kind then
			local ok = true
			if kind == "tier" or kind == "rarity" then
				ok = type(arg) == "number" and arg >= q.arg
			elseif kind == "zone" then
				ok = arg == q.arg
			elseif kind == "collect" then
				ok = type(arg) == "string" and arg:sub(1, #q.arg) == q.arg
			end
			if ok then
				if kind == "range" then
					st.p = math.max(st.p, amount)
				else
					st.p += amount
				end
				if st.p >= q.goal then
					st.p = q.goal
					st.done = true
					emitFn("quest", { id = id })
				end
			end
		end
	end
end

local function findItem(id: number): (any, number?)
	for i, it in d.items do
		if it.id == id then
			return it, i
		end
	end
	return nil, nil
end

local H: { [string]: (...any) -> ...any } = {}

H.Sync = function()
	return true, d
end

H.TensionStart = function(_lane: any)
	if #d.items >= d.bagCap then
		return false, "Bag full! Sell your catch at the market"
	end
	local st = Config.spearStats(d.spear, d.spears[d.spear])
	local alpha = st.alpha * boostMult("tension")
	token += 1
	local crashAt = Roll.crashPoint(alpha, rng)
	tension = { token = token, crashAt = crashAt, t0 = os.clock() }
	return true, { token = token, crashAt = crashAt, alpha = alpha }
end

H.Throw = function(args: any)
	local tn = tension
	if not tn or type(args) ~= "table" or args.token ~= tn.token then
		return false, "Start charging first"
	end
	tension = nil
	local held = os.clock() - tn.t0
	local chargedM = math.clamp(tonumber(args.m) or 1, 1, math.min(Config.tensionAt(held + 0.3), Config.TENSION.cap))
	local crashed = args.crashed == true or chargedM >= tn.crashAt
	-- A delayed frame must not add luck past the moment the grip slipped.
	if crashed then chargedM = math.min(chargedM, tn.crashAt) end
	local m = chargedM * (crashed and Config.TENSION.crashLuck or 1)
	local st = Config.spearStats(d.spear, d.spears[d.spear])
	-- Slipping lowers luck, while the spear still travels the charged trajectory.
	local frac = Config.distFrac(chargedM)
	local dist = Config.range(d.power) * st.range * boostMult("range") * frac
	dist = math.min(dist, Config.MAX_THROW_DISTANCE or Config.THROW.maxRange)
	local zone = Config.zoneFor(dist)
	local tier = Config.tierIndex(m)
	d.stats.throws += 1
	local luckBeforeCrash = chargedM * Config.distLuck(dist) * Config.powerLuck(d.power) * st.luck * boostMult("luck") * demoLuck
	local luck = luckBeforeCrash * (crashed and Config.TENSION.crashLuck or 1)
	local res: any = { m = m, chargedM = chargedM, tier = tier, crashed = crashed, dist = dist, zone = zone, luck = luck, luckBeforeCrash = luckBeforeCrash, xp = 0 }
	if crashed then
		d.stats.crashes += 1
	else
		d.stats.bestMult = math.max(d.stats.bestMult, m)
	end
	progress("tier", m, 1)
	d.stats.bestDist = math.max(d.stats.bestDist, dist)
	local sp = Roll.species(zone, luck, rng, Perks.capMul(boostOn("luck"), luck))
	res.sp = sp.id
	local can, why = Roll.canTake(st, sp)
	if not can then
		res.escaped = true
		res.reason = why
		res.need = Roll.spearFor(sp).name
		res.xp = 2
		addXp(2)
		return true, res
	end
	local w = Roll.weight(sp, luck, rng)
	local mut = Roll.mutation(luck, rng, Perks.mutMul())
	local price = Roll.price(sp, w, mut)
	local item = { id = nextId, sp = sp.id, w = w, price = price, mut = mut, wrapped = false, m = m, zone = zone, t = os.time() }
	nextId += 1
	table.insert(d.items, item)
	local rec = d.index[sp.id]
	local isNew = rec == nil
	local isRecord = false
	if not rec then
		rec = { n = 0, best = 0, bestPrice = 0, gold = false, rainbow = false }
		d.index[sp.id] = rec
	end
	rec.n += 1
	if w > rec.best then
		isRecord = not isNew
		rec.best = w
	end
	rec.bestPrice = math.max(rec.bestPrice, price)
	if mut == "gold" then
		rec.gold = true
	elseif mut == "rainbow" then
		rec.rainbow = true
	end
	d.stats.catches += 1
	local gain = math.floor(Config.XP.perRarity[sp.rarity] * (1 + Config.XP.tierBonus * (tier - 1)))
	local ups = addXp(gain)
	progress("catch", nil, 1)
	progress("zone", zone, 1)
	progress("rarity", sp.rarity, 1)
	res.item = item
	res.isNew = isNew
	res.isRecord = isRecord
	res.xp = gain
	res.levelUps = ups
	return true, res
end

H.TensionCancel = function()
	tension = nil
	return true
end

H.Sell = function(ids: any)
	local picked = {}
	local pickedSet = {}
	for _, it in d.items do
		if ids == "all" or (type(ids) == "table" and table.find(ids, it.id) ~= nil) then
			table.insert(picked, it)
			pickedSet[it.id] = true
		end
	end
	if #picked == 0 then
		return false, "Nothing to sell"
	end
	-- V25: цена проходит через рынок (спрос часа и насыщение по видам). Приёмник котировки - Config.marketQuote.
	local now = Config.marketNow()
	local flags = Perks.marketFlags()
	local total, count, _, counts = Config.marketQuote(picked, d, now, flags)
	total = math.floor(total * boostMult("coins"))
	if type(d.market) ~= "table" or type(d.market.sold) ~= "table" then
		d.market = { sold = {} }
	end
	for sp, n in counts do
		d.market.sold[sp] = { n = n, t = now }
	end
	local keep = {}
	for _, it in d.items do
		if not pickedSet[it.id] then
			table.insert(keep, it)
		end
	end
	d.items = keep
	addCoins(total)
	d.stats.sold += count
	progress("sell", nil, total)
	return true, total, count
end

H.WrapStart = function(id: any)
	local it = findItem(tonumber(id) or -1)
	if not it or it.wrapped then
		return false, "Nothing to wrap"
	end
	return true
end

H.WrapFinish = function(id: any)
	local it = findItem(tonumber(id) or -1)
	if not it or it.wrapped then
		return false
	end
	it.wrapped = true
	progress("wrap", nil, 1)
	return true, it.price * Config.WRAP_MULT
end

H.Rep = function()
	local now = os.clock()
	if now - lastRep < Config.REP_COOLDOWN * 0.8 then
		return false
	end
	lastRep = now
	local gain = Config.DUMBBELL[d.dumbbell].gain * Perks.repMult()
	d.power += gain
	progress("train", nil, 1)
	return true, gain
end

H.UpgradeDumbbell = function()
	local nxt = Config.DUMBBELL[d.dumbbell + 1]
	if not nxt then
		return false, "Your dumbbells are fully upgraded"
	end
	if d.coins < nxt.cost then
		return false, "Not enough coins"
	end
	addCoins(-nxt.cost)
	d.dumbbell += 1
	return true, d.dumbbell
end

H.BuySpear = function(id: any)
	local s = Config.SPEAR_BY_ID[id]
	if not s then
		return false, "That spear does not exist"
	end
	if d.spears[id] ~= nil then
		d.spear = id
		return true, "equip"
	end
	if d.coins < s.price then
		return false, "Not enough coins"
	end
	addCoins(-s.price)
	d.spears[id] = 0
	d.spear = id
	return true, "bought"
end

H.EquipSpear = function(id: any)
	if type(id) ~= "string" or d.spears[id] == nil then
		return false, "You do not own this spear"
	end
	d.spear = id
	return true
end

H.Forge = function()
	local lvl = d.spears[d.spear] or 0
	if lvl >= Perks.forgeMax() then
		if lvl < Config.FORGE.maxLevel then
			return false, "Master Smith (Shop) unlocks forge levels 6 and 7"
		end
		return false, "This spear is fully upgraded"
	end
	local cost = Perks.forgeCost(d.spear, lvl)
	if d.coins < cost then
		return false, "Not enough coins"
	end
	addCoins(-cost)
	d.spears[d.spear] = lvl + 1
	return true, lvl + 1
end

H.BuyBag = function()
	local nxt = Config.BAG[d.bagLvl + 1]
	if not nxt then
		return false, "Your bag is fully upgraded"
	end
	if d.coins < nxt.cost then
		return false, "Not enough coins"
	end
	addCoins(-nxt.cost)
	d.bagLvl += 1
	applyPerks()
	return true, d.bagCap
end

H.BuyPotion = function(i: any)
	local p = Config.POTIONS[tonumber(i) or 0]
	if not p then
		return false
	end
	local cost = Config.potionCost(p, d)
	if d.coins < cost then
		return false, "Not enough coins"
	end
	addCoins(-cost)
	addBoost(p.boost, p.dur)
	return true
end

H.QuestClaim = function(id: any)
	local st = d.quests[id]
	local q = Config.QUEST_BY_ID[id]
	if not st or not q or not st.done or st.claimed then
		return false, "This quest is not complete yet"
	end
	st.claimed = true
	d.quests[id] = nil
	local r = q.reward
	if r.coins then
		addCoins(r.coins)
	end
	if r.xp then
		addXp(r.xp)
	end
	if r.boost then
		addBoost(r.boost, r.dur or 120)
	end
	local nq = Config.QUESTS[d.questNext]
	if nq then
		d.quests[nq.id] = { p = 0, done = false, claimed = false }
		d.questNext += 1
	end
	return true, r
end

H.Collect = function(id: any)
	if type(id) ~= "string" or d.collected[id] then
		return false
	end
	d.collected[id] = true
	local kind = id:sub(1, 2) == "ff" and "firefly" or "egg"
	local r = Config.ACTIVITY[kind]
	addCoins(r.coins)
	addXp(r.xp)
	progress("collect", id, 1)
	return true, { coins = r.coins, xp = r.xp }
end

H.Activity = function(kind: any, payload: any)
	if kind == "range" then
		local pts = math.clamp(tonumber(payload) or 0, 0, 500)
		local coins = math.floor(pts * Config.ACTIVITY.range.coinPerPoint)
		addCoins(coins)
		addXp(math.floor(pts * Config.ACTIVITY.range.xpPerPoint))
		d.stats.rangeBest = math.max(d.stats.rangeBest, pts)
		progress("range", nil, pts)
		return true, { coins = coins }
	elseif kind == "course" then
		local got = math.clamp(tonumber(payload and payload.coins) or 0, 0, 50)
		local tm = tonumber(payload and payload.time) or 999
		local c = Config.ACTIVITY.course
		local coins = c.coins + got * c.coinPerCoin + (tm < c.parTime and 100 or 0)
		addCoins(coins)
		addXp(c.xp)
		progress("course", nil, 1)
		if d.stats.courseBest == 0 or tm < d.stats.courseBest then
			d.stats.courseBest = tm
		end
		return true, { coins = coins }
	elseif kind == "lookout" then
		if d.flags.lookout then
			return true, { coins = 0 }
		end
		d.flags.lookout = true
		addCoins(Config.ACTIVITY.lookout.coins)
		addXp(Config.ACTIVITY.lookout.xp)
		return true, { coins = Config.ACTIVITY.lookout.coins }
	elseif kind == "campfire" then
		local c = Config.ACTIVITY.campfire.coinsPerMin
		addCoins(c)
		return true, { coins = c }
	end
	return false
end

H.Settings = function(patch: any)
	if type(patch) == "table" then
		for k, v in patch do
			if d.settings[k] ~= nil and type(v) == type(d.settings[k]) then
				d.settings[k] = v
			end
		end
	end
	return true
end

H.Tutorial = function(step: any)
	d.tutorial = math.max(d.tutorial, tonumber(step) or d.tutorial)
	return true
end

-- Панель демо: читы для просмотра всего контента
H.Demo = function(cmd: any, arg: any)
	if cmd == "coins" then
		addCoins(tonumber(arg) or 1e6)
	elseif cmd == "power" then
		d.power += tonumber(arg) or 500
	elseif cmd == "luck" then
		demoLuck = tonumber(arg) or 1
		notify("Demo luck ×" .. tostring(demoLuck), "rare")
	elseif cmd == "spears" then
		for _, s in Config.SPEARS do
			d.spears[s.id] = d.spears[s.id] or 0
		end
	elseif cmd == "level" then
		addXp(Config.xpForLevel(d.level))
	elseif cmd == "boosts" then
		for id in Config.BOOSTS do
			if id ~= "server" then
				addBoost(id, 300)
			end
		end
	elseif cmd == "reset" then
		d = defaults()
		nextId = 1
		demoLuck = 1
		applyPerks()
	elseif cmd == "fake" then
		-- раскрытие без сумки (витрина): arg = { sp, mut, m }
		local sp = Config.SPECIES_BY_ID[arg and arg.sp]
		if not sp then
			return false
		end
		local w = Roll.weight(sp, 50, rng)
		local mut = arg.mut
		local item = { id = -1, sp = sp.id, w = w, price = Roll.price(sp, w, mut), mut = mut, m = arg.m or 1, zone = sp.zone, t = os.time() }
		return true, { m = item.m, tier = Config.tierIndex(item.m), crashed = false, dist = 0, zone = sp.zone, luck = 1, sp = sp.id, item = item, isNew = d.index[sp.id] == nil, isRecord = false, xp = 0, fake = true }
	else
		return false
	end
	return true
end

---------------------------------------------------------------------
-- Robux-магазин: то, что меняет экономику игрока
---------------------------------------------------------------------
-- Пасс Master Wrapper: после одной упаковки завернуть всё остальное в сумке
H.WrapAll = function()
	if not Perks.has("wrap") then
		return false
	end
	local n = 0
	for _, it in d.items do
		if not it.wrapped then
			it.wrapped = true
			n += 1
		end
	end
	if n > 0 then
		progress("wrap", nil, n)
	end
	return true, n
end

-- Покупка, подтверждённая сервером (Server/Shop кладёт её в очередь pending)
H.ShopGrant = function(g: any)
	if type(g) ~= "table" then
		return false
	end
	if g.kind == "coins" then
		local n = Config.shopCoins(d, tonumber(g.k) or 0)
		addCoins(n)
		return true, n
	elseif g.kind == "starter" then
		local st = Config.SHOP.STARTER
		if d.spears[st.spear] == nil then
			d.spears[st.spear] = 0
		end
		local cur = Config.SPEAR_BY_ID[d.spear]
		local new = Config.SPEAR_BY_ID[st.spear]
		if new and (not cur or cur.index < new.index) then
			d.spear = st.spear
		end
		d.bagLvl = math.max(d.bagLvl, st.bagLvl)
		applyPerks()
		addCoins(st.coins)
		return true, st.coins
	end
	return false
end

-- Загрузка сохранённого прогресса: берём только известные поля нужного типа
function Demo.load(saved: any): boolean
	if type(saved) ~= "table" then
		return false
	end
	local base = defaults()
	for k, v in saved do
		if base[k] ~= nil and type(v) == type(base[k]) then
			base[k] = v
		end
	end
	local fresh = defaults()
	for k, v in fresh.stats do
		if type(base.stats[k]) ~= "number" then
			base.stats[k] = v
		end
	end
	for k, v in fresh.settings do
		if type(base.settings[k]) ~= "boolean" then
			base.settings[k] = v
		end
	end
	for id in base.spears do
		if Config.SPEAR_BY_ID[id] == nil then
			base.spears[id] = nil
		end
	end
	if Config.SPEAR_BY_ID[base.spear] == nil or base.spears[base.spear] == nil then
		base.spear = Config.START.spear
		base.spears[base.spear] = base.spears[base.spear] or 0
	end
	local items = {}
	local maxId = 0
	for _, it in base.items do
		if type(it) == "table" and type(it.id) == "number" and type(it.price) == "number" and Config.SPECIES_BY_ID[it.sp] then
			table.insert(items, it)
			maxId = math.max(maxId, it.id)
		end
	end
	base.items = items
	if type(base.market) ~= "table" or type(base.market.sold) ~= "table" then
		base.market = { sold = {} }
	end
	for id in base.quests do
		if Config.QUEST_BY_ID[id] == nil then
			base.quests[id] = nil
		end
	end
	base.dumbbell = math.clamp(math.floor(base.dumbbell), 1, #Config.DUMBBELL)
	base.level = math.max(1, math.floor(base.level))
	base.coins = math.max(0, base.coins)
	base.power = math.max(Config.START.power, base.power)
	d = base
	nextId = maxId + 1
	tension = nil
	applyPerks()
	return true
end

function Demo.applyPerks()
	applyPerks()
end

function Demo.call(action: string, ...: any): ...any
	local fn = H[action]
	if not fn then
		return false, "Unknown action " .. tostring(action)
	end
	-- как у настоящего сервера: ошибка обработчика не ломает интерфейс, но видна в Output
	local r = table.pack(pcall(fn, ...))
	if not r[1] then
		task.spawn(error, "[Demo] " .. action .. ": " .. tostring(r[2]), 0)
		return false, "The demo could not complete this action"
	end
	return table.unpack(r, 2, r.n)
end

function Demo.demoLuck(): number
	return demoLuck
end

return Demo
