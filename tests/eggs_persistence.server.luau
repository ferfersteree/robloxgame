-- Test: eggs and exotics survive saves, rejoins, retries and failures, without a real DataStore.
-- How to run: in Studio create a Script in ServerScriptService, paste this file, press Play, read Output
-- (a line "EGGTEST" followed by PASS/FAIL lines), then delete the Script.
-- It uses the Studio-only hook Shop._test from ServerScriptService/Server/Shop to swap in a fake DataStore.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")
local Config = require(RS.Shared.Config)
local Shop = require(game.ServerScriptService.Server.Shop)
local T = Shop._test
while not T do
	task.wait(0.2)
	T = Shop._test
end
local player = Players:GetPlayers()[1] or Players.PlayerAdded:Wait()
task.wait(4)
local results = {}
local function check(name, cond, extra)
	table.insert(results, (cond and "PASS " or "FAIL ") .. name .. (extra ~= nil and (" [" .. tostring(extra) .. "]") or ""))
end
local data = {}
local fake = {}
local failSet, slow = false, 0
function fake:GetAsync(k)
	local v = data[k]
	return v and HttpService:JSONDecode(v) or nil
end
function fake:SetAsync(k, v)
	if slow > 0 then
		task.wait(slow)
	end
	if failSet then
		error("fake set failure")
	end
	data[k] = HttpService:JSONEncode(v)
end
T.setStore(fake)
local item = {}
for k, v in Config.SHOP_BY_KEY.egg_mystic do
	item[k] = v
end
item.id = 990001
T.addProduct(item)
local key = "u_" .. player.UserId
local prof
local function load()
	T.loadProfile(player)
	prof = T.profiles[player]
end
local function owned()
	local n = 0
	for _, c in prof.shop.exotic.owned do
		n += c
	end
	return n
end
local G, N = Enum.ProductPurchaseDecision.PurchaseGranted, Enum.ProductPurchaseDecision.NotProcessedYet
local function rc(id)
	return { PlayerId = player.UserId, ProductId = 990001, PurchaseId = id, CurrencySpent = 99 }
end
local ok, err = pcall(function()
	load()
	check("loaded empty, eggsOff resolved false in Studio", prof.loaded and owned() == 0 and prof.eggsOff == false, prof.eggsOff)
	check("state eggsOff false", T.stateOf(prof).eggsOff == false)
	prof.eggsOff = nil
	check("state eggsOff true while unknown (nil)", T.stateOf(prof).eggsOff == true)
	prof.eggsOff = false
	check("receipt granted", T.processReceipt(rc("r1")) == G and owned() == 1)
	local first = prof.shop.exotic.hatch[1].sp
	T.processReceipt(rc("r1"))
	check("same receipt again: still one, spent once", owned() == 1 and prof.shop.spent == 99, owned())
	load()
	check("rejoin keeps animal, hatch, receipt", owned() == 1 and prof.shop.exotic.owned[first] == 1 and #prof.shop.exotic.hatch == 1 and table.find(prof.shop.receipts, "r1") ~= nil)
	T.processReceipt(rc("r1"))
	check("retry after rejoin no dupe", owned() == 1)
	check("hatchAck ok", T.invoke(player, "hatchAck", { prof.shop.exotic.hatch[1].id }) == true)
	T.saveProfile(player, prof)
	load()
	check("after ack rejoin: no replay, animal kept", #prof.shop.exotic.hatch == 0 and owned() == 1)
	failSet = true
	local before = owned()
	check("save failure -> NotProcessedYet", T.processReceipt(rc("r2")) == N)
	check("rolled back, not busy", owned() == before and table.find(prof.shop.receipts, "r2") == nil and #prof.shop.exotic.hatch == 0 and not prof.busy)
	failSet = false
	check("retry granted once", T.processReceipt(rc("r2")) == G and owned() == before + 1 and prof.shop.spent == 198, owned())
	-- two receipts at once, the first save is slow and then fails
	local base = owned()
	slow = 0.6
	failSet = true
	local resA
	task.spawn(function()
		resA = T.processReceipt(rc("rA"))
	end)
	task.wait(0.2)
	check("busy while A saves", prof.busy == true)
	check("B during A returns NotProcessedYet (no interleave)", T.processReceipt(rc("rB")) == N)
	check("equip during A refused", T.invoke(player, "exoticEquip", next(prof.shop.exotic.owned)) == false)
	task.wait(0.8)
	check("A failed -> NotProcessedYet and rolled back", resA == N and owned() == base and table.find(prof.shop.receipts, "rA") == nil)
	failSet = false
	slow = 0
	check("A retry granted once", T.processReceipt(rc("rA")) == G and owned() == base + 1)
	check("B retry granted once", T.processReceipt(rc("rB")) == G and owned() == base + 2)
	-- an error inside the grant must not leave the profile busy
	local realAdd = item.kind
	item.kind = "egg"
	local oldRoll = Config.eggRoll
	Config.eggRoll = function()
		error("boom")
	end
	local rBoom = T.processReceipt(rc("rBoom"))
	Config.eggRoll = oldRoll
	check("error in grant -> NotProcessedYet, not busy, nothing granted", rBoom == N and not prof.busy and table.find(prof.shop.receipts, "rBoom") == nil)
	item.kind = realAdd
	for i = 1, 30 do
		T.processReceipt(rc("bulk" .. i))
	end
	check("30 unacknowledged hatches all kept (cap 100)", #prof.shop.exotic.hatch >= 30, #prof.shop.exotic.hatch)
	data[key] = HttpService:JSONEncode({ v = 1, t = 0, save = {}, shop = { boosts = {}, starter = false, spent = 5, receipts = {}, pending = {}, test = {} } })
	load()
	check("old save without exotic loads", prof.loaded and owned() == 0 and prof.shop.spent == 5)
	data[key] = HttpService:JSONEncode({ v = 1, t = 0, save = {}, shop = { exotic = { owned = { ghost = 3, candy_hopper = "x", neon_fox = -2 }, equipped = { "ghost", 5 }, level = { candy_hopper = 99 }, shards = -5, hatch = { { id = "x", sp = "nope" }, 7 } } } })
	load()
	check("corrupt data dropped", owned() == 0 and #prof.shop.exotic.equipped == 0 and prof.shop.exotic.shards == 0 and #prof.shop.exotic.hatch == 0)
	data[key] = HttpService:JSONEncode({ v = 1, t = 0, save = {}, shop = { exotic = { owned = { candy_hopper = 2, neon_fox = 1, bubble_boar = 1, glow_wolf = 1 }, equipped = { "candy_hopper", "neon_fox", "bubble_boar", "glow_wolf" }, level = { candy_hopper = 99 }, shards = 40 } } })
	load()
	check("equip limit and level clamp on load", #prof.shop.exotic.equipped == 3 and prof.shop.exotic.level.candy_hopper == 5)
	prof.eggsOff = true
	check("testBuy egg refused when region-restricted", T.invoke(player, "testBuy", "egg_mystic") == false)
	prof.eggsOff = false
	check("testBuy egg allowed otherwise", T.invoke(player, "testBuy", "egg_mystic") == true)
end)
if not ok then
	table.insert(results, "ERROR " .. tostring(err))
end
T.setStore(nil)
print("EGGTEST\n" .. table.concat(results, "\n"))
