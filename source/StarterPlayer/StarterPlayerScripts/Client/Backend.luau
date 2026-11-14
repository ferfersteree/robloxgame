-- StarterPlayerScripts/Client/Backend.luau
-- Единая точка связи интерфейса с «сервером». Config.BACKEND = "Demo" | "Remote".
-- Backend.call(action, ...) → ok, ...   Backend.data — последний снимок данных.
-- Backend.onChange(fn) — подписка на изменения; Backend.onEvent(fn(name, payload)) — события (levelup, quest, boost, notify).
local RS = game:GetService("ReplicatedStorage")

local Config = require(RS.Shared.Config)
local Net = require(RS.Shared.Net)
local Perks = require(script.Parent.Perks)

local Backend = {}
Backend.mode = Config.BACKEND
Backend.data = nil :: any

local listeners: { [(any) -> ()]: boolean } = {}
local evListeners: { [(string, any) -> ()]: boolean } = {}
local hold = false
local pendingChange = false
local pendingEvents: { { any } } = {}

local function fireChange()
	if hold then
		pendingChange = true
		return
	end
	for fn in listeners do
		task.spawn(fn, Backend.data)
	end
end

local function fireEvent(name: string, payload: any)
	if hold and name ~= "notify" then
		table.insert(pendingEvents, { name, payload })
		return
	end
	for fn in evListeners do
		task.spawn(fn, name, payload)
	end
end

function Backend.onChange(fn: (any) -> ())
	listeners[fn] = true
	if Backend.data then
		task.spawn(fn, Backend.data)
	end
end

function Backend.onEvent(fn: (string, any) -> ())
	evListeners[fn] = true
end

-- Во время раскрытия не спойлерим интерфейс (сумка/монеты обновятся после)
function Backend.hold(on: boolean)
	hold = on
	if not on then
		if pendingChange then
			pendingChange = false
			fireChange()
		end
		local evs = pendingEvents
		pendingEvents = {}
		for _, e in evs do
			fireEvent(e[1], e[2])
		end
	end
end

local Demo: any = nil
local Request: RemoteFunction? = nil

if Backend.mode == "Demo" then
	Demo = require(script.Parent.DemoServer)
	Demo.setEmitter(fireEvent)
	Backend.data = Demo.data()
else
	Request = Net.fn("Request")
	Net.ev("State").OnClientEvent:Connect(function(d)
		Backend.data = d
		fireChange()
	end)
	Net.ev("Notify").OnClientEvent:Connect(function(name, payload)
		fireEvent(name, payload)
	end)
end

function Backend.call(action: string, ...: any): ...any
	if Demo then
		if Config.DEMO_LATENCY > 0 and action ~= "TensionStart" then
			task.wait(Config.DEMO_LATENCY)
		end
		local r = table.pack(Demo.call(action, ...))
		Backend.data = Demo.data()
		if action ~= "TensionStart" and action ~= "Sync" then
			fireChange()
		end
		return table.unpack(r, 1, r.n)
	end
	local req = Request :: RemoteFunction
	local r = table.pack(pcall(req.InvokeServer, req, action, ...))
	if not r[1] then
		return false, "Cannot reach the server"
	end
	return table.unpack(r, 2, r.n)
end

function Backend.sync()
	if Demo then
		Backend.data = Demo.data()
		fireChange()
	else
		Backend.call("Sync")
	end
end

function Backend.boostLeft(id: string): number
	local d = Backend.data
	local ends = d and d.boosts and d.boosts[id]
	local left = type(ends) == "number" and math.max(0, ends - os.time()) or 0
	-- зелье за монеты и оплаченное время идут одновременно: показываем большее
	return math.max(left, Perks.boostLeft(id))
end

function Backend.boostMult(id: string): number
	local on = Backend.boostLeft(id) > 0
	if id == "luck" then
		return Perks.luckMult(on)
	elseif id == "coins" then
		return Perks.coinMult(on)
	end
	if on then
		return Config.BOOSTS[id].mult
	end
	return 1
end

-- Множитель потолков редкостей от Robux-магазина (для подсказки шансов)
function Backend.capMul(luck: number?): number
	return Perks.capMul(Backend.boostLeft("luck") > 0, luck)
end

-- Подставить сохранённый прогресс (демо-бэкенд)
function Backend.load(saved: any): boolean
	if Demo and Demo.load(saved) then
		Backend.data = Demo.data()
		fireChange()
		return true
	end
	return false
end

-- Пассы изменились: пересчитать зависящие от них поля (вместимость сумки)
function Backend.applyPerks()
	if Demo then
		Demo.applyPerks()
		Backend.data = Demo.data()
	end
	fireChange()
end

function Backend.demoLuck(): number
	return Demo and Demo.demoLuck() or 1
end

function Backend.bagCount(): number
	return Backend.data and #Backend.data.items or 0
end

return Backend
