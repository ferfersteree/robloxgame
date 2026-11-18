-- ReplicatedStorage/Shared/Roll.luau
-- Чистая логика случайностей: срыв натяжения, вид, вес, мутация, цена. Без побочных эффектов.
local Config = require(script.Parent.Config)

local Roll = {}

-- byZone[zone][rarity] = { species, ... }
local byZone: { [number]: { [number]: { any } } } = {}
for _, sp in Config.SPECIES do
	byZone[sp.zone] = byZone[sp.zone] or {}
	local pools = byZone[sp.zone]
	pools[sp.rarity] = pools[sp.rarity] or {}
	table.insert(pools[sp.rarity], sp)
end
Roll.byZone = byZone
local baselineByZone: { [number]: number } = {}
for zone, pools in byZone do
	local baseline = #Config.RARITIES
	for rarity in pools do baseline = math.min(baseline, rarity) end
	baselineByZone[zone] = baseline
end
Roll.baselineByZone = baselineByZone

-- Habitat weights apply only inside a rarity after the rarity roll succeeds.
-- They never replace or multiply the global rarity odds.
local function pickSpecies(list: { any }, rng: Random): any
	local total = 0
	for _, sp in list do total += math.max(0, sp.populationWeight or 1) end
	if total <= 0 then return list[rng:NextInteger(1, #list)] end
	local draw = rng:NextNumber() * total
	local cumulative = 0
	for _, sp in list do
		cumulative += math.max(0, sp.populationWeight or 1)
		if draw < cumulative then return sp end
	end
	return list[#list]
end

-- Скрытая точка срыва: P(m* ≥ m) = m^(-alpha). math.huge — не сорвётся до капа.
function Roll.crashPoint(alpha: number, rng: Random): number
	local u = math.max(rng:NextNumber(), 1e-9)
	local m = u ^ (-1 / math.max(alpha, 0.05))
	if m >= Config.TENSION.cap then
		return math.huge
	end
	return math.max(1.0, m)
end

-- Шанс дотянуть до множителя m (для подсказок)
function Roll.reachChance(m: number, alpha: number): number
	return math.min(1, math.max(m, 1) ^ -alpha)
end

local function tierChance(rarity: number, luck: number, capMul: number?): number
	local value = if luck == luck then math.max(0, luck) else 0
	local chance = math.min(1, value / Config.RARITIES[rarity].odds)
	local cap = Config.RARITY_CHANCE_CAPS and Config.RARITY_CHANCE_CAPS[rarity]
	-- capMul: Robux-магазин поднимает потолки редкостей (Lucky Charm, бусты удачи)
	if cap then
		cap = math.min(1, cap * math.max(capMul or 1, 1))
	end
	return math.min(chance, cap or 1)
end
Roll.tierChance = tierChance

-- Бросок от самой редкой категории к обычной («1 из N», удача делит N)
function Roll.species(zone: number, luck: number, rng: Random, capMul: number?)
	local pools = byZone[zone] or byZone[1]
	local baseline = baselineByZone[zone] or baselineByZone[1]
	for r = #Config.RARITIES, baseline + 1, -1 do
		local list = pools[r]
		if list and #list > 0 and rng:NextNumber() < tierChance(r, luck, capMul) then
			return pickSpecies(list, rng)
		end
	end
	return pickSpecies(pools[baseline], rng)
end

-- Итоговые шансы категорий в зоне при данной удаче (для интерфейса)
function Roll.tierChances(zone: number, luck: number, capMul: number?): { { rarity: number, chance: number } }
	local pools = byZone[zone] or byZone[1]
	local baseline = baselineByZone[zone] or baselineByZone[1]
	local out = {}
	local rest = 1
	for r = #Config.RARITIES, baseline + 1, -1 do
		local list = pools[r]
		if list and #list > 0 then
			local p = tierChance(r, luck, capMul)
			table.insert(out, 1, { rarity = r, chance = rest * p })
			rest *= (1 - p)
		end
	end
	table.insert(out, 1, { rarity = baseline, chance = rest })
	return out
end

-- Вес: чем выше удача, тем тяжелее в среднем
function Roll.weight(sp, luck: number, rng: Random): (number, number)
	local e = math.clamp(2.2 - 0.22 * math.log(math.max(luck, 1)), 0.8, 2.2)
	local r = rng:NextNumber() ^ e
	local w = sp.wMin + (sp.wMax - sp.wMin) * r
	if w < 10 then
		w = math.floor(w * 100 + 0.5) / 100
	else
		w = math.floor(w * 10 + 0.5) / 10
	end
	return w, r
end

-- mul > 1 (Golden Hour из магазина): шанс мутации x mul, потолок x1.5.
function Roll.mutation(luck: number, rng: Random, mul: number?): string?
	local k = mul or 1
	local ck = k > 1 and 1.5 or 1
	local s = math.sqrt(math.max(luck, 1)) * k
	local rb = Config.MUTATIONS.rainbow
	if rng:NextNumber() < math.min(rb.cap * ck, s / rb.base) then
		return "rainbow"
	end
	local g = Config.MUTATIONS.gold
	if rng:NextNumber() < math.min(g.cap * ck, s / g.base) then
		return "gold"
	end
	return nil
end

function Roll.price(sp, w: number, mut: string?): number
	local avg = (sp.wMin + sp.wMax) / 2
	local p = sp.price * (w / avg) ^ 0.85
	if mut and Config.MUTATIONS[mut] then
		p *= Config.MUTATIONS[mut].mult
	end
	return math.max(1, math.floor(p + 0.5))
end

-- Может ли копьё взять этот вид
function Roll.canTake(spear: any, sp: any): (boolean, string?)
	if sp.sharp > spear.sharp then
		return false, "Hide is too tough"
	end
	if sp.weight > spear.heavy then
		return false, "Animal is too heavy"
	end
	return true, nil
end

-- Первое копьё, которое берёт вид
function Roll.spearFor(sp: any): any
	for _, s in Config.SPEARS do
		if s.sharp >= sp.sharp and s.heavy >= sp.weight then
			return s
		end
	end
	return Config.SPEARS[#Config.SPEARS]
end

return Roll
