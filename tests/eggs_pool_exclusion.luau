-- Test: exotic animals can never appear in normal hunting.
-- How to run: paste into Studio's command bar (or execute_luau in Edit mode). Prints PASS/FAIL lines.
-- 1) no exotic id is in Config.SPECIES (Roll, Population, Ambient, Showroom and the collection all read it);
-- 2) every exotic base model exists in Config.SPECIES (so Fauna150 has a template);
-- 3) 60,000 normal rolls over all zones, luck levels and rarity-cap multipliers return no exotic;
-- 4) egg odds sum to 100% and each egg only lists known exotics; the roll matches the shown odds.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Shared.Config)
local Roll = require(RS.Shared.Roll)
local out = {}
local function check(name, cond, extra)
	table.insert(out, (cond and "PASS " or "FAIL ") .. name .. (extra ~= nil and (" [" .. tostring(extra) .. "]") or ""))
end

local speciesIds = {}
for _, sp in Config.SPECIES do
	speciesIds[sp.id] = true
end
local overlap = 0
for _, ex in Config.EXOTICS do
	if speciesIds[ex.id] then
		overlap += 1
	end
end
check("no exotic id in Config.SPECIES", overlap == 0, overlap)
local missing = 0
for _, ex in Config.EXOTICS do
	if not speciesIds[ex.base] then
		missing += 1
	end
end
check("every exotic base model is a normal species", missing == 0, missing)

local rng = Random.new(12345)
local leaks, rolls = 0, 0
local zones = Config.ZONES and #Config.ZONES or 25
for zone = 1, zones do
	for _, luck in { 1, 2, 4, 8 } do
		for _, capMul in { 1, 3, 6 } do
			for _ = 1, 50 do
				local sp = Roll.species(zone, luck, rng, capMul)
				rolls += 1
				if sp and Config.EXOTIC_BY_ID[sp.id] then
					leaks += 1
				end
			end
		end
	end
end
check("normal rolls never return an exotic", leaks == 0 and rolls >= 3000, leaks .. " leaks in " .. rolls .. " rolls")

local bad = 0
for key, egg in Config.EGGS do
	local sum = 0
	for _, o in Config.eggOdds(key) do
		sum += o.pct
		if not Config.EXOTIC_BY_ID[o.id] then
			bad += 1
		end
	end
	check(key .. " odds sum to 100%", math.abs(sum - 100) < 1e-6, sum)
	local counts, n = {}, 100000
	for _ = 1, n do
		local id = Config.eggRoll(key, rng)
		counts[id] = (counts[id] or 0) + 1
	end
	local worst = 0
	for _, o in Config.eggOdds(key) do
		worst = math.max(worst, math.abs((counts[o.id] or 0) / n * 100 - o.pct))
	end
	check(key .. " roll matches shown odds within 0.5 pp over 100k rolls", worst < 0.5, string.format("%.2f pp", worst))
end
check("egg tables list only known exotics", bad == 0, bad)
return table.concat(out, "\n")
