-- StarterPlayerScripts/Client/DemoServer.luau
-- ФЕЙКОВЫЙ БЭКЕНД для демо-режима: та же логика и те же ответы, что описаны в docs/BACKEND.md,
-- но всё считается на клиенте. Настоящий сервер должен повторить эти обработчики на своей стороне.
local RS = game:GetService("ReplicatedStorage")

local Config = require(RS.Shared.Config)
local Roll = require(RS.Shared.Roll)
local Perks = require(script.Parent.Perks)
local RunService = game:GetService("RunService")

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
		strLvl = 1, -- V86: уровень Силы (Сила = Config.strengthOf(strLvl))
		strXp = 0, -- V86: опыт на шкале текущего уровня Силы
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
		hpass = { season = -1, xp = 0, day = -1, week = -1, prog = {}, done = {}, claimed = {} },
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

---------------------------------------------------------------------
-- V71: Hunter Pass. Прогресс заданий пропуска лежит в d.hpass; сезон/день/неделя считаются по Config.pass*.
---------------------------------------------------------------------
local function hpassMax(): number
	return Config.PASS.TIERS * Config.PASS.XP_PER_TIER
end

-- Смена сезона обнуляет всё; смена дня чистит дневные задания, смена недели недельные
local function hpassRoll()
	local h = d.hpass
	local n = Config.passSeason()
	if h.season ~= n then
		h.season = n
		h.xp = 0
		h.claimed = {}
		h.prog = {}
		h.done = {}
		h.day = -1
		h.week = -1
	end
	local day, week = Config.passDay(), Config.passWeek()
	if h.day ~= day then
		for _, set in Config.PASS.DAILY do
			for _, m in set do
				h.prog[m.id] = nil
				h.done[m.id] = nil
			end
		end
		h.day = day
	end
	if h.week ~= week then
		for _, m in Config.PASS.WEEKLY do
			h.prog[m.id] = nil
			h.done[m.id] = nil
		end
		h.week = week
	end
end

-- Опыт пропуска (не выше потолка сезона)
local function hpassAddXp(n: number, text: string)
	local h = d.hpass
	local before = Config.passTier(h.xp)
	local old = h.xp
	h.xp = math.clamp(h.xp + n, 0, hpassMax())
	local after = Config.passTier(h.xp)
	emitFn("hpass", { text = text, xp = h.xp - old, tier = after, tierUp = after > before })
end

local function hpassProgress(kind: string, arg: any, amount: number)
	if type(amount) ~= "number" or amount ~= amount or amount <= 0 then
		return
	end
	hpassRoll()
	local h = d.hpass
	local function visit(m: any)
		if m.kind ~= kind or h.done[m.id] then
			return
		end
		local ok = true
		if kind == "tier" or kind == "rarity" then
			ok = type(arg) == "number" and arg >= m.arg
		elseif kind == "zone" then
			ok = arg == m.arg
		elseif kind == "collect" then
			ok = type(arg) == "string" and arg:sub(1, #m.arg) == m.arg
		end
		if not ok then
			return
		end
		-- range считается накопительно за пропуск (у квестов там максимум)
		local p = math.min((h.prog[m.id] or 0) + amount, m.goal)
		h.prog[m.id] = p
		if p >= m.goal then
			h.done[m.id] = true
			hpassAddXp(m.xp, m.text)
		end
	end
	for _, m in Config.passDaily() do
		visit(m)
	end
	for _, m in Config.PASS.WEEKLY do
		visit(m)
	end
end

-- Прогресс заданий
local function progress(kind: string, arg: any, amount: number)
	hpassProgress(kind, arg, amount)
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
	-- V68: множитель после срыва не ниже ×1
	local m = math.max(1, chargedM * (crashed and Config.TENSION.crashLuck or 1))
	local st = Config.spearStats(d.spear, d.spears[d.spear])
	-- Slipping lowers luck, while the spear still travels the charged trajectory.
	local dist = Config.throwDist(d.power, st, boostMult("range"), chargedM) -- V86: с потолком копья (Config.spearReach)
	local zone = Config.zoneFor(dist)
	local tier = Config.tierIndex(m)
	d.stats.throws += 1
	local luckBeforeCrash = chargedM * Config.distLuck(dist) * Config.powerLuck(d.power) * st.luck * boostMult("luck") * demoLuck
	local luck = luckBeforeCrash * (crashed and Config.TENSION.crashLuck or 1)
	-- V68: удача после срыва не ниже, чем у броска ×1
	luck = math.max(luck, luckBeforeCrash / math.max(chargedM, 1))
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

-- V82: бафф ×2 на 1 с от подсказки на экране; не чаще раза в ~4 с, клиенту на слово не верим
local buffUntil = 0
local buffOwed = false -- V83: бафф ещё не удвоил ни одного подъёма
local lastBuff = -math.huge
H.TrainBuff = function()
	local now = os.clock()
	if now - lastBuff < 4 then
		return false
	end
	lastBuff = now
	buffUntil = now + 1
	buffOwed = true
	return true
end

-- V86: уровни Силы растут независимо от гантелей. Подъём даёт опыт = gain гантелей; на каждый новый уровень +perLevel Силы.
local function addStrengthLevels(n: number): number
	local cur = tonumber(d.strLvl) or 1
	local add = math.min(math.max(0, math.floor(n)), Config.STRENGTH.maxLevel - cur)
	if add <= 0 then
		return 0
	end
	d.strLvl = cur + add
	d.power = Config.strengthOf(d.strLvl)
	return add
end

-- Подъём: опыт в шкалу уровня Силы; переполнение переносится на следующий уровень
H.Rep = function()
	local now = os.clock()
	if now - lastRep < Config.REP_COOLDOWN * 0.8 then
		return false
	end
	lastRep = now
	local info = Config.DUMBBELL[d.dumbbell] or Config.DUMBBELL[1]
	-- V83: авто-подъём идёт раз в 1.1 с, а бафф длится 1 с: если в окно не попал ни один подъём,
	-- удваиваем первый подъём после него (не позже 0.7 с), чтобы удачная подсказка не пропадала зря
	local buffed = now < buffUntil or (buffOwed and now < buffUntil + 0.7)
	buffOwed = false
	local added = info.gain * Perks.repMult() * (buffed and 2 or 1)
	local xp = (tonumber(d.strXp) or 0) + added
	local lvl = tonumber(d.strLvl) or 1
	local levels = 0
	local need = Config.strengthXp(lvl)
	while xp >= need and levels < 1000 and lvl < Config.STRENGTH.maxLevel do
		xp -= need
		lvl += 1
		levels += 1
		need = Config.strengthXp(lvl)
	end
	if lvl >= Config.STRENGTH.maxLevel then
		xp = math.min(xp, need) -- на потолке шкала стоит полной
	end
	local power = 0
	if levels > 0 then
		local before = d.power
		addStrengthLevels(levels)
		power = d.power - before
	end
	d.strXp = xp
	progress("train", nil, 1)
	return true, { pts = added, fills = levels, power = power, bar = need, cur = xp, level = d.strLvl }
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
		addStrengthLevels((tonumber(arg) or 500) / Config.STRENGTH.perLevel)
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
	elseif g.kind == "hpassxp" then
		-- бандл Premium + 10 уровней: опыт только в том сезоне, где куплен; выдачу подтверждаем в любом случае
		hpassRoll()
		local xp = tonumber(g.xp)
		if xp and xp == xp and xp > 0 and tonumber(g.season) == Config.passSeason() then
			hpassAddXp(math.min(xp, hpassMax()), "Pass bundle")
		end
		return true, 0
	end
	return false
end

-- V71: пропуск. Монеты: k от цены самого дорогого имеющегося копья (не меньше первого покупного)
local function hpassPrice(): number
	local P = 0
	for _, s in Config.SPEARS do
		if s.price > 0 then
			P = s.price
			break
		end
	end
	for id in d.spears do
		local s = Config.SPEAR_BY_ID[id]
		if s and s.price > P then
			P = s.price
		end
	end
	return P
end

H.HpassSync = function()
	hpassRoll()
	return true, d.hpass
end

H.HpassClaim = function(tier: any, lane: any)
	hpassRoll()
	local h = d.hpass
	local t = tonumber(tier)
	if not t or t ~= t or t ~= math.floor(t) or t < 1 or t > Config.PASS.TIERS then
		return false, "No such tier"
	end
	if t > Config.passTier(h.xp) then
		return false, "This tier is not unlocked yet"
	end
	if lane ~= "f" and lane ~= "p" then
		return false, "No such row"
	end
	if lane == "p" and not Perks.hpassPremium() then
		return false, "Premium row is locked"
	end
	local key = lane .. t
	if h.claimed[key] then
		return false, "Already claimed"
	end
	local r = Config.PASS.REWARDS[t]
	local list = r and (lane == "f" and r.free or r.premium)
	if not list or Config.passSide(list) ~= "client" then
		return false, "This reward is claimed from the server"
	end
	local coins, power = 0, 0
	local potions: { any } = {}
	for _, it in list do
		if it.type == "coins" then
			coins += math.ceil(it.k * hpassPrice())
		elseif it.type == "power" then
			power += it.n
		elseif it.type == "potion" and Config.BOOSTS[it.boost] and type(it.dur) == "number" then
			table.insert(potions, it)
		end
	end
	h.claimed[key] = true
	for _, it in potions do -- V74: зелье пропуска продлевает буст, как купленное у Травницы
		addBoost(it.boost, it.dur)
	end
	if coins > 0 then
		addCoins(coins)
	end
	if power > 0 then
		-- V86: награда «+N Силы» — это N / perLevel уровней Силы
		power = addStrengthLevels(power / Config.STRENGTH.perLevel) * Config.STRENGTH.perLevel
	end
	return true, { coins = coins, power = power, potions = #potions }
end

-- Только Studio: прибавить опыт пропуска для проверки
H.HpassDebugXp = function(n: any)
	if not RunService:IsStudio() then
		return false
	end
	local v = tonumber(n) or 300
	if v ~= v then
		return false
	end
	hpassRoll()
	hpassAddXp(math.clamp(math.floor(v), 0, hpassMax()), "Pass XP (Studio)")
	return true, d.hpass.xp
end

-- V71: d.hpass из сохранения чистим по полям (вложенные таблицы приходят от клиента)
local function cleanHpass(raw: any): any
	local h = defaults().hpass
	if type(raw) ~= "table" then
		return h
	end
	for _, k in { "season", "xp", "day", "week" } do
		local v = tonumber(raw[k])
		if v and v == v and v > -1e9 and v < 1e9 then
			h[k] = math.floor(v)
		end
	end
	h.xp = math.clamp(h.xp, 0, hpassMax())
	local known = {}
	for _, set in Config.PASS.DAILY do
		for _, m in set do
			known[m.id] = m
		end
	end
	for _, m in Config.PASS.WEEKLY do
		known[m.id] = m
	end
	if type(raw.prog) == "table" then
		for id, v in raw.prog do
			local m = type(id) == "string" and known[id] or nil
			local n = tonumber(v)
			if m and n and n == n then
				h.prog[id] = math.clamp(n, 0, m.goal)
			end
		end
	end
	if type(raw.done) == "table" then
		for id, v in raw.done do
			if type(id) == "string" and known[id] and v == true then
				h.done[id] = true
			end
		end
	end
	if type(raw.claimed) == "table" then
		for key, v in raw.claimed do
			if type(key) == "string" and v == true then
				local lane, num = key:match("^([fp])(%d+)$")
				local t = tonumber(num)
				if lane and t and t >= 1 and t <= Config.PASS.TIERS then
					h.claimed[key] = true
				end
			end
		end
	end
	return h
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
	base.hpass = cleanHpass(base.hpass)
	local db = tonumber(base.dumbbell)
	if db == nil or db ~= db or db == math.huge then
		db = 1 -- V83: NaN или мусор в сохранении не должны ронять загрузку
	end
	base.dumbbell = math.clamp(math.floor(db), 1, #Config.DUMBBELL)
	-- V86: Сила — это уровень. Старое сохранение (без strLvl): уровень, на котором базовая дальность не больше
	-- прежней 8·√Сила, чтобы бросок не стал дальше, чем был
	local lv = tonumber(saved.strLvl)
	if lv == nil or lv ~= lv or lv == math.huge or lv < 1 then
		local oldPower = tonumber(saved.power) or Config.START.power
		if oldPower ~= oldPower or oldPower == math.huge then
			oldPower = Config.START.power
		end
		local oldReach = 8 * math.sqrt(math.max(oldPower, 1))
		lv = 1
		while lv < Config.STRENGTH.maxLevel and Config.range(Config.strengthOf(lv + 1)) <= oldReach do
			lv += 1
		end
		base.strXp = 0
	end
	base.strLvl = math.clamp(math.floor(lv), 1, Config.STRENGTH.maxLevel)
	local sx = tonumber(base.strXp)
	if sx == nil or sx ~= sx or sx < 0 or sx == math.huge then
		sx = 0
	end
	base.strXp = math.min(sx, Config.strengthXp(base.strLvl) - 1e-6)
	base.power = Config.strengthOf(base.strLvl)
	base.level = math.max(1, math.floor(base.level))
	base.coins = math.max(0, base.coins)
	d = base
	nextId = maxId + 1
	tension = nil
	applyPerks()
	hpassRoll() -- старый сезон не должен светиться в бейдже до первого обработчика пропуска
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
