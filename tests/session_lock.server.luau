-- Test: session lock of the shop profile (V45), without a real DataStore.
-- How to run: in Studio create a Script in ServerScriptService, paste this file, press Play, read Output
-- (lines "LOCKTEST ..." with PASS / FAIL), then delete the Script.
-- It uses the Studio-only hook Shop._test (setStore, setJobId, setLockTimes, setKick) from ServerScriptService/Server/Shop.
local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")
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

-- a fake DataStore with an atomic UpdateAsync (a transform that returns nil cancels the update)
local data = {}
local fake = {}
local failUpdates = 0
function fake:GetAsync(k)
	local v = data[k]
	return v and HttpService:JSONDecode(v) or nil
end
function fake:SetAsync(k, v)
	data[k] = HttpService:JSONEncode(v)
end
function fake:UpdateAsync(k, fn)
	if failUpdates > 0 then
		failUpdates -= 1
		error("fake update failure")
	end
	local old = data[k] and HttpService:JSONDecode(data[k]) or nil
	local new = fn(old)
	if new == nil then
		return old
	end
	data[k] = HttpService:JSONEncode(new)
	return HttpService:JSONDecode(data[k])
end

local origJob = T.getJobId()
local kicked: string? = nil
T.setKick(function(_p, msg)
	kicked = msg
end)
T.setStore(fake)
T.setLockTimes(20, 5, 60) -- ttl 20 s, wait 5 s, refresh 60 s (ttl must outlast the wait plus one 2 s poll: with ttl 6 the lock expired before B gave up and 6 checks failed)
local key = "u_" .. player.UserId
local function rec()
	return data[key] and HttpService:JSONDecode(data[key]) or nil
end

-- A: server A loads a fresh profile and takes the lock
T.setJobId("A")
T.loadProfile(player)
local profA = T.profiles[player]
check("A loads", profA and profA.loaded == true)
check("A holds the lock", rec() and rec().lock and rec().lock.id == "A", rec() and rec().lock and rec().lock.id)

-- B: A saves a change, the lock stays with A
profA.shop.spent = 123
profA.dirty = true
check("A saves", T.saveProfile(player, profA) == true)
check("saved value is in the record", rec().shop.spent == 123, rec().shop.spent)
check("lock still A after the save", rec().lock.id == "A")

-- C: server B tries to load the same account while A holds it: waits, then gives up and asks the player to rejoin
T.setJobId("B")
local t0 = os.clock()
T.loadProfile(player)
local waited = os.clock() - t0
task.wait(0.3) -- the kick is deferred
local profB = T.profiles[player]
check("B waited for the lock", waited >= 4.5 and waited < 12, string.format("%.1fs", waited))
check("B is not loaded", profB.loaded ~= true and profB.failed == true)
check("B asked the player to rejoin", kicked ~= nil, kicked)
check("B did not touch the record", rec().shop.spent == 123 and rec().lock.id == "A")
check("B cannot save over A", T.saveProfile(player, profB) == false and rec().shop.spent == 123)

-- D: A leaves and releases the lock; B can load and sees A's data
T.setJobId("A")
check("A releases on leave", T.saveProfile(player, profA, true) == true and rec().lock == nil)
T.setJobId("B")
kicked = nil
T.loadProfile(player)
task.wait(0.3)
local profB2 = T.profiles[player]
check("B loads after the release", profB2.loaded == true and profB2.shop.spent == 123, profB2.shop and profB2.shop.spent)
check("B holds the lock", rec().lock and rec().lock.id == "B")
check("no kick on a clean load", kicked == nil)

-- E: a stale lock (server crashed, nobody refreshed it for longer than the ttl) is taken over
local r = rec()
r.lock = { id = "A", t = os.time() - 40 } -- older than the ttl
data[key] = HttpService:JSONEncode(r)
T.setJobId("C")
T.loadProfile(player)
local profC = T.profiles[player]
check("C takes over a stale lock", profC.loaded == true and rec().lock.id == "C")

-- F: C loses the lock to a newer server: its save must not overwrite
r = rec()
r.lock = { id = "B", t = os.time() }
r.shop.spent = 500
data[key] = HttpService:JSONEncode(r)
profC.shop.spent = 999
profC.dirty = true
kicked = nil
check("C refuses to overwrite", T.saveProfile(player, profC) == false)
task.wait(0.3)
check("record keeps the newer value", rec().shop.spent == 500 and rec().lock.id == "B", rec().shop.spent)
check("C is marked lost and asked to rejoin", profC.lockLost == true and kicked ~= nil)
check("C does not save again", T.saveProfile(player, profC) == false)

-- G: an old record without any lock (written before V45) loads and gets a lock, data is kept
data[key] = HttpService:JSONEncode({ v = 1, shop = { spent = 77 } })
T.setJobId("D")
T.loadProfile(player)
local profD = T.profiles[player]
check("old record loads", profD.loaded == true and profD.shop.spent == 77, profD.shop and profD.shop.spent)
check("old record gets a lock", rec().lock and rec().lock.id == "D" and rec().shop.spent == 77)

-- H: transient errors are retried
data[key] = nil
failUpdates = 2
T.setJobId("E")
t0 = os.clock()
T.loadProfile(player)
check("load retries after two failures", T.profiles[player].loaded == true and failUpdates == 0, string.format("%.1fs", os.clock() - t0))

-- I: a store without UpdateAsync still works (old behaviour)
local plain = {}
local store2 = {}
function store2:GetAsync(k) return plain[k] and HttpService:JSONDecode(plain[k]) or nil end
function store2:SetAsync(k, v) plain[k] = HttpService:JSONEncode(v) end
T.setStore(store2)
T.setJobId("F")
T.loadProfile(player)
local profF = T.profiles[player]
profF.shop.spent = 5
profF.dirty = true
check("store without UpdateAsync saves", T.saveProfile(player, profF) == true and HttpService:JSONDecode(plain[key]).shop.spent == 5)

-- clean up
T.setStore(nil)
T.setJobId(origJob)
T.setLockTimes(180, 30, 60)
T.setKick(nil)
local fails = 0
for _, line in results do
	if line:sub(1, 4) == "FAIL" then
		fails += 1
	end
end
print("LOCKTEST " .. (fails == 0 and "ALL PASS" or (fails .. " FAILED")))
for _, line in results do
	print("LOCKTEST " .. line)
end
