-- StarterPlayerScripts/Client/Perks.luau
-- Что игроку даёт Robux-магазин прямо сейчас: пассы, оплаченное время бустов, серверная удача.
-- Состояние приходит с сервера (Server/Shop), здесь только чтение и формулы.
-- Бонусы одной характеристики складываются: Удача = 1 + зелье + пасс + сервер.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Shared.Config)

local K = Config.SHOP.PERK

local Perks = {}
Perks.Changed = Instance.new("BindableEvent")

local state: any = { passes = {}, boosts = {}, server = 0, starter = false, studio = false, loaded = false, pending = {}, spent = 0, rank = 0, gift = 0 }
local stamp = os.clock()

function Perks.set(s: any)
	if type(s) ~= "table" then
		return
	end
	state = {
		passes = type(s.passes) == "table" and s.passes or {},
		boosts = type(s.boosts) == "table" and s.boosts or {},
		server = tonumber(s.server) or 0,
		starter = s.starter == true,
		studio = s.studio == true,
		loaded = s.loaded == true,
		pending = type(s.pending) == "table" and s.pending or {},
		spent = tonumber(s.spent) or 0,
		rank = tonumber(s.rank) or 0,
		gift = tonumber(s.gift) or 0,
	}
	stamp = os.clock()
	Perks.Changed:Fire()
end

function Perks.state(): any
	return state
end

function Perks.has(key: string): boolean
	if key == "insight" and Perks.rankInfo() and Perks.rankInfo().insight then
		return true -- Diamond получает Market Insight бесплатно
	end
	return state.passes[key] == true
end

-- Ранг поддержки (0 = нет) и его плюшки; считает сервер по сумме Robux.
function Perks.rank(): number
	return math.clamp(math.floor(tonumber(state.rank) or 0), 0, #Config.SHOP.RANKS)
end

function Perks.rankInfo(): any
	return Config.SHOP.RANKS[Perks.rank()]
end

-- Секунд до следующего ежедневного подарка (0 = можно забрать).
function Perks.giftLeft(): number
	return math.max(0, (tonumber(state.gift) or 0) - (os.clock() - stamp))
end

function Perks.serverLeft(): number
	return math.max(0, state.server - (os.clock() - stamp))
end

-- Оплаченное время буста (идёт только пока игрок в игре)
function Perks.boostLeft(id: string): number
	if id == "server" then
		return Perks.serverLeft()
	end
	local v = tonumber(state.boosts[id]) or 0
	return math.max(0, v - (os.clock() - stamp))
end

function Perks.luckMult(boostOn: boolean): number
	local m = 1
	if boostOn then
		m += 1
	end
	if Perks.has("charm") then
		m += K.charmLuck
	end
	if Perks.serverLeft() > 0 then
		m += K.serverLuck
	end
	return m
end

-- Множитель потолков редкостей (Config.RARITY_CHANCE_CAPS).
-- Слагаемые: зелье удачи, Lucky Charm, Jackpot Hour, серверная удача. luck (необязательно) добавляет
-- бонус копья Config.capLuckMul, чтобы удача поздних копий снова что-то значила.
function Perks.capMul(boostOn: boolean, luck: number?): number
	local m = 1
	if boostOn then
		m += K.boostCaps
	end
	if Perks.has("charm") then
		m += K.charmCaps
	end
	if Perks.boostLeft("jackpot") > 0 then
		m += K.jackpotCaps
	end
	if Perks.serverLeft() > 0 then
		m += K.serverCaps
	end
	if luck then
		m *= Config.capLuckMul(luck)
	end
	return m
end

-- Монеты от продажи: только зелье за монеты. Постоянных множителей монет в магазине больше нет.
function Perks.coinMult(boostOn: boolean): number
	return boostOn and 2 or 1
end

function Perks.xpMult(): number
	return Perks.has("vip") and (1 + K.vipXp) or 1
end

-- Золотой час: шанс мутаций x3.
function Perks.mutMul(): number
	return Perks.boostLeft("fortune") > 0 and K.fortuneMutMul or 1
end

-- Рынок: Silver Broker смягчает насыщение, Trade Fair его убирает.
function Perks.marketFlags(): { broker: boolean, fair: boolean, recover: number }
	local rk = Perks.rankInfo()
	return { broker = Perks.has("broker"), fair = Perks.boostLeft("fair") > 0, recover = rk and rk.recover or 1 }
end

-- Продажа из любого места, а также панель рынка: пасс VIP Hunter.
function Perks.sellAnywhere(): boolean
	return Perks.has("vip")
end

-- Кузница: 5 бесплатных уровней, пасс Master Smith даёт ещё 2 и скидку.
function Perks.forgeMax(): number
	return Config.FORGE.freeMax + (Perks.has("smith") and K.smithLevels or 0)
end

function Perks.forgeCost(id: string, lvl: number): number
	local c = Config.forgeCost(id, lvl)
	if Perks.has("smith") then
		c = math.floor(c * (1 - K.smithDiscount))
	end
	return c
end

-- Оставлено для совместимости (товаров с этим эффектом больше нет).
function Perks.repMult(): number
	return 1
end

-- Слоты сумки сверх бесплатных 100: только у рангов поддержки.
function Perks.bagBonus(): number
	local rk = Perks.rankInfo()
	return rk and rk.bag or 0
end

return Perks
