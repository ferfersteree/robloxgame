--!nonstrict
-- PetAnimations: анимации питомцев SpearHunt, перенесённые из веб-прототипа формула в формулу.
-- Сгенерировано автоматически из кода прототипа. Не править вручную.
--
-- PetAnimations[petId] = { idle, move, react, hatch, rootMotion = { idle, move, react, hatch }, hd, rd, mv, joints }
--   idle(t, set), move(t, set): t — время в секундах
--   react(u, set), hatch(u, set): u — от 0 до 1; длительность реакции rd сек., появления hd сек.
--   set(имяСустава, CFrame) — значение для Motor6D "<имяСустава>_Joint".Transform
--   rootMotion.hatch(u) → CFrame смещения корня, масштаб модели
local PetAnimations = {}

-- ===== общая математика прототипа (совпадает с core.js) =====
local PI, TAU = math.pi, math.pi * 2
local sin, cos, abs, max, min, sqrt = math.sin, math.cos, math.abs, math.max, math.min, math.sqrt
local SCALE = 1.5 -- 1 единица прототипа = 1.5 стада

local function truthy(v) return v ~= nil and v ~= false and v ~= 0 and v ~= "" end
local function orv(a, b) if truthy(a) then return a end return b end
local function iff(c, a, b) if c then return a end return b end
local function forEach(arr, f) for i = 1, #arr do f(arr[i], i - 1) end end
local function map(arr, f) local r = {} for i = 1, #arr do r[i] = f(arr[i], i - 1) end return r end
local function round(x) return math.floor(x + 0.5) end
local function sign(x) if x > 0 then return 1 elseif x < 0 then return -1 end return 0 end
local function hypot(x, y) return sqrt(x * x + y * y) end
local function clamp(x, a, b) a = a or 0 b = b or 1 if x < a then return a elseif x > b then return b end return x end
local function lerp(a, b, t) return a + (b - a) * t end
local function ss(a, b, x) x = clamp((x - a) / (b - a)) return x * x * (3 - 2 * x) end
-- kf(u, u0,v0, u1,v1, ...) — сглаженные ключи
local function kf(u, ...)
	local k = { ... }
	if u <= k[1] then return k[2] end
	for i = 3, #k, 2 do
		if u <= k[i] then
			local d = k[i] - k[i - 2]
			if d == 0 then d = 1e-6 end
			local t = (u - k[i - 2]) / d
			return lerp(k[i - 1], k[i + 1], t * t * (3 - 2 * t))
		end
	end
	return k[#k]
end
local function wave(t, f, ph) return sin(TAU * (t * f + (ph or 0))) end
local function pulse(t, period, dur, off)
	local x = (t + (off or 0)) % period
	if x < dur then return sin(PI * x / dur) end
	return 0
end
local function bump(u, a, b) if u <= a or u >= b then return 0 end return sin(PI * (u - a) / (b - a)) end
local function outBack(t) t = clamp(t) local c = 1.70158 return 1 + (c + 1) * (t - 1) ^ 3 + c * (t - 1) ^ 2 end

-- ===== поза: те же аккумуляторы R/T/S, что в прототипе (оси прототипа, перевод в Roblox — в flush) =====
local VOX = 0.085 -- размер кубика питомца в единицах прототипа

local function newPose(rest)
	local acc = {}
	for name, r in pairs(rest) do acc[name] = { dp = { 0, 0, 0 }, dr = { 0, 0, 0 }, ds = { 1, 1, 1 }, sh = 0 } end
	local A = { w = 1 }
	function A.R(n, x, y, z)
		local a = acc[n] if not a then return A end
		local w = A.w
		a.dr[1] = a.dr[1] + (x or 0) * w a.dr[2] = a.dr[2] + (y or 0) * w a.dr[3] = a.dr[3] + (z or 0) * w
		return A
	end
	function A.T(n, x, y, z)
		local a = acc[n] if not a then return A end
		local w = A.w
		a.dp[1] = a.dp[1] + (x or 0) * w a.dp[2] = a.dp[2] + (y or 0) * w a.dp[3] = a.dp[3] + (z or 0) * w
		return A
	end
	-- МАСШТАБ: Motor6D не умеет масштаб. root → копится в ds и уходит в rootMotion.scale.
	-- Остальные суставы: уменьшение заменено втягиванием к родителю (sh), увеличение игнорируется.
	function A.S(n, x, y, z)
		local a = acc[n] if not a then return A end
		local w = A.w
		if y == nil then y = x end
		if z == nil then z = x end
		a.ds[1] = a.ds[1] * (1 + (x - 1) * w) a.ds[2] = a.ds[2] * (1 + (y - 1) * w) a.ds[3] = a.ds[3] * (1 + (z - 1) * w)
		return A
	end
	function A.chain(pre, n, t, f, ax, ay, az, lag, grow)
		for i = 1, n do
			local ph = -(truthy(lag) and lag or 0.12) * i
			local k = 1 + (grow or 0) * i
			A.R(pre .. i, (ax or 0) * k * wave(t, f, ph), (ay or 0) * k * wave(t, f, ph), (az or 0) * k * wave(t, f, ph))
		end
		return A
	end
	-- МОРГАНИЕ: в прототипе глаз сплющивается (S). Здесь глаз утапливается в голову на 1.4 кубика.
	function A.blink(t, seed)
		seed = seed or 0
		local b = pulse(t, 3.7, 0.16, seed) + pulse(t, 9.1, 0.14, seed + 1.3)
		if b > 0 then
			local k = min(1, b)
			A.T("eyeL", 0, 0, -VOX * 1.4 * k) A.T("eyeR", 0, 0, -VOX * 1.4 * k)
			A.T("browL", 0, -0.012 * b, 0) A.T("browR", 0, -0.012 * b, 0)
		end
		return A
	end
	function A.brows(v, tilt)
		A.T("browL", 0, v, 0) A.T("browR", 0, v, 0)
		if truthy(tilt) then A.R("browL", 0, 0, -tilt) A.R("browR", 0, 0, tilt) end
		return A
	end
	return acc, A
end

-- ===== общие кирпичики движения (lib.js) =====
local L = {}
function L.base(a, t, o)
	o = o or {}
	local f, b, k = orv(o.f, 0.42), orv(o.body, "body"), orv(o.k, 1)
	a.S(b, 1 + 0.012 * k * wave(t, f), 1 + 0.022 * k * wave(t, f, 0.25), 1 + 0.014 * k * wave(t, f))
	a.blink(t, orv(o.seed, 0))
	if o.head ~= 0 then
		local h = orv(o.hn, "head")
		local lk = o.look == nil and 1 or o.look
		a.R(h, 0.035 * wave(t, 0.23, orv(o.seed, 0)), 0.16 * lk * wave(t, 0.097, 0.3 + orv(o.seed, 0)) + 0.07 * lk * wave(t, 0.31), 0.035 * wave(t, 0.17, 0.6))
	end
end
function L.step(a, n, ph, amp, lift, knee)
	local s, c = sin(TAU * ph), cos(TAU * ph)
	a.R(n, -amp * s, 0, 0)
	if truthy(lift) then a.T(n, 0, lift * max(0, c), 0) end
	if truthy(knee) then a.R(n .. "2", knee * max(0, c), 0, 0) end
end
function L.sideStep(a, n, s, ph, amp, lift, knee)
	local sn, c = sin(TAU * ph), cos(TAU * ph)
	a.R(n, 0, -s * amp * sn, s * lift * max(0, c))
	if truthy(knee) then a.R(n .. "2", 0, 0, -s * knee * max(0, c)) end
end
function L.rise(a, u, y, sc) a.T("root", 0, y, 0) a.S("root", sc) end
function L.squash(a, u, a0, a1, amt, j)
	local b = bump(u, a0, a1) * orv(amt, 0.16)
	a.S(orv(j, "root"), 1 + b * 0.7, 1 - b, 1 + b * 0.7)
end
function L.shake(a, u, a0, a1, amt, f)
	if u > a0 and u < a1 then
		local k = (u - a0) / (a1 - a0)
		a.R("root", 0, orv(amt, 0.25) * sin(k * TAU * orv(f, 4)) * (1 - k), 0)
	end
end
function L.flap(a, ang, l, rn) a.R(orv(l, "wingL"), 0, 0, -ang) a.R(orv(rn, "wingR"), 0, 0, ang) end

-- ===== регистрация питомца =====
-- rest[joint] = { px, py, pz, rx, ry, rz } в единицах и осях прототипа (three.js: перед = +Z).
-- Перевод в Roblox (перед = -Z, лево = -X): поворот на 180° вокруг Y, т.е. x → -x, z → -z для сдвигов
-- и углов вокруг X и Z; порядок Эйлера XYZ совпадает с CFrame.fromEulerAnglesXYZ.
local function restCF(r, dp, dr, sc)
	local k = SCALE * sc
	return CFrame.new(-(r[1] + dp[1]) * k, (r[2] + dp[2]) * k, -(r[3] + dp[3]) * k)
		* CFrame.fromEulerAnglesXYZ(-(r[4] + dr[1]), r[5] + dr[2], -(r[6] + dr[3]))
end
local ZERO = { 0, 0, 0 }

local function register(id, info, self)
	local rest, order = info.rest, info.joints
	local acc, A = newPose(rest)
	local entry = { id = id, name = info.name, hd = info.hd, rd = info.rd, mv = info.mv, joints = order, rest = rest, raw = self, acc = acc }
	local function begin()
		for _, a in pairs(acc) do
			a.dp[1], a.dp[2], a.dp[3] = 0, 0, 0 a.dr[1], a.dr[2], a.dr[3] = 0, 0, 0 a.ds[1], a.ds[2], a.ds[3] = 1, 1, 1
		end
	end
	local function add(name, t, w) A.w = w == nil and 1 or w self[name](t, A) end
	-- flush: пишет Transform каждого сустава (кроме root) и возвращает движение корня
	local function flush(set, sc)
		sc = sc or 1
		for i = 1, #order do
			local n = order[i]
			if n ~= "root" then
				local r, a = rest[n], acc[n]
				local dp = a.dp
				local m = (a.ds[1] * a.ds[2] * a.ds[3]) ^ (1 / 3)
				if m < 1 and not entry.noShift then -- S → сдвиг: втягиваем сустав к родителю
					if m < 0 then m = 0 end
					dp = { dp[1] + (m - 1) * r[1], dp[2] + (m - 1) * r[2], dp[3] + (m - 1) * r[3] }
				end
				set(n, restCF(r, ZERO, ZERO, sc):Inverse() * restCF(r, dp, a.dr, sc))
			end
		end
		local a = acc.root
		local rootScale = (a.ds[1] * a.ds[2] * a.ds[3]) ^ (1 / 3)
		local k = SCALE * sc
		return CFrame.new(-a.dp[1] * k, a.dp[2] * k, -a.dp[3] * k) * CFrame.fromEulerAnglesXYZ(-a.dr[1], a.dr[2], -a.dr[3]), rootScale
	end
	entry.begin, entry.add, entry.flush = begin, add, flush
	entry.rootMotion = {}
	local function noop() end
	for _, an in ipairs({ "idle", "move", "react", "hatch" }) do
		-- f(t, set [, scale]): idle/move — t в секундах; react/hatch — u от 0 до 1 (доля от rd / hd)
		entry[an] = function(t, set, sc) begin() add(an, t, 1) flush(set, sc) end
		entry.rootMotion[an] = function(t, sc) begin() add(an, t, 1) return flush(noop, sc) end
	end
	PetAnimations[id] = entry
end


-- ============ clover_beetle — ÐšÐ»ÐµÐ²ÐµÑ€Ð½Ñ‹Ð¹ Ð¶ÑƒÑ‡Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.2})
local tw = pulse(t, 3.1, 0.5)
for _, s in ipairs({1, (-1)}) do
local n = iff((s > 0), "antL", "antR")
local ph = iff((s > 0), 0, 0.33)
a.R((n .. "1"), ((0.1 * wave(t, 0.6, ph)) + ((0.3 * tw) * iff((s > 0), 1, 0.4))), 0, (0.1 * wave(t, 0.43, ph)))
a.R((n .. "2"), ((0.22 * wave(t, 0.6, (ph - 0.2))) + (0.4 * tw)), 0, (((-s) * 0.12) * wave(t, 0.9, ph)))
end
local tap = pulse(t, 4.6, 0.5, 1)
a.R("l1L", 0, 0, (0.5 * tap))
a.R("l1L2", 0, 0, ((-0.5) * tap))
a.R("wingL", 0, (0.03 * wave(t, 0.5)), 0)
a.R("wingR", 0, ((-0.03) * wave(t, 0.5)), 0)
end
self.move = function(t, a)
local f = 3.4
a.T("body", 0, (0.025 * wave(t, (f * 2))), 0)
a.R("body", (0.03 * wave(t, f, 0.1)), (0.05 * wave(t, f)), (0.045 * wave(t, f, 0.25)))
a.R("head", (0.05 * wave(t, (f * 2), 0.2)), ((-0.06) * wave(t, f)), 0)
a.blink(t)
forEach({"l1L", "l2R", "l3L"}, function(n, i)
return L.sideStep(a, n, iff((i == 1), (-1), 1), (t * f), 0.55, 0.42, 0.3)
end)
forEach({"l1R", "l2L", "l3R"}, function(n, i)
return L.sideStep(a, n, iff((i == 1), 1, (-1)), ((t * f) + 0.5), 0.55, 0.42, 0.3)
end)
for _, s in ipairs({1, (-1)}) do
local n = iff((s > 0), "antL", "antR")
a.R((n .. "1"), (0.35 + (0.12 * wave(t, f, 0.15))), 0, (0.08 * wave(t, (f * 0.5))))
a.R((n .. "2"), (0.3 + (0.25 * wave(t, f, (-0.1)))), 0, 0)
end
end
self.react = function(u, a)
local e = bump(u, 0, 1)
local bz = ((sin((u * 90)) * 0.1) * e)
a.T("root", 0, (0.5 * bump(u, 0.12, 0.8)), 0)
a.R("wingL", ((-0.25) * e), ((1.05 * e) + bz), (0.35 * e))
a.R("wingR", ((-0.25) * e), (((-1.05) * e) - bz), ((-0.35) * e))
a.R("antL1", ((-0.5) * e), 0, (0.3 * e))
a.R("antR1", ((-0.5) * e), 0, ((-0.3) * e))
a.brows((0.03 * e))
a.R("head", ((-0.2) * e), 0, 0)
forEach({"l1L", "l2L", "l3L"}, function(n)
return a.R(n, 0, 0, (0.35 * e))
end)
forEach({"l1R", "l2R", "l3R"}, function(n)
return a.R(n, 0, 0, ((-0.35) * e))
end)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.3, 0.2, 0.72, 0.36, 0.7, 0.46, 0.55, 0.6, 1.95, 0.78, 0, 1, 0), kf(u, 0, 0.42, 0.44, 0.5, 0.62, 1.04, 0.74, 1, 1, 1))
local pk = bump(u, 0.04, 0.44)
a.R("antL1", (((-0.5) * pk) + ((0.5 * pk) * wave(u, 9))), 0, 0)
a.R("antR1", (((-0.5) * pk) + ((0.5 * pk) * wave(u, 9, 0.5))), 0, 0)
a.R("head", ((-0.35) * pk), ((0.6 * pk) * wave(u, 4.2)), 0)
local fl = bump(u, 0.48, 0.8)
local bz = ((sin((u * 160)) * 0.12) * fl)
a.R("wingL", ((-0.2) * fl), ((1.1 * fl) + bz), (0.3 * fl))
a.R("wingR", ((-0.2) * fl), (((-1.1) * fl) - bz), ((-0.3) * fl))
a.R("root", (((-0.35) * bump(u, 0.46, 0.62)) + (0.2 * bump(u, 0.62, 0.78))), 0, 0)
L.squash(a, u, 0.76, 0.9, 0.2)
local sp = bump(u, 0.76, 0.92)
forEach({"l1L", "l2L", "l3L"}, function(n)
return a.R(n, 0, 0, ((-0.3) * sp))
end)
forEach({"l1R", "l2R", "l3R"}, function(n)
return a.R(n, 0, 0, (0.3 * sp))
end)
L.shake(a, u, 0.84, 0.99, 0.22, 3)
end
register("clover_beetle", {
	name = "ÐšÐ»ÐµÐ²ÐµÑ€Ð½Ñ‹Ð¹ Ð¶ÑƒÑ‡Ð¾Ðº", hd = 2.7, rd = 1.2, mv = { sp = 1.5, rad = 1.25, side = false },
	joints = { "root", "body", "wingL", "wingR", "head", "eyeL", "browL", "eyeR", "browR", "antL1", "antL2", "antR1", "antR2", "l1L", "l1L2", "l2L", "l2L2", "l3L", "l3L2", "l1R", "l1R2", "l2R", "l2R2", "l3R", "l3R2" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.6, -0.05, 0, 0, 0 },
		wingL = { 0, 0.55, 0.34, 0, 0, 0 },
		wingR = { 0, 0.55, 0.34, 0, 0, 0 },
		head = { 0, -0.1, 0.93, 0, 0, 0 },
		eyeL = { 0.19, 0.05, 0.345, 0, 0.1, 0 },
		browL = { 0.19, 0.22, 0.345, -0.25, 0.1, -0.12 },
		eyeR = { -0.19, 0.05, 0.345, 0, -0.1, 0 },
		browR = { -0.19, 0.22, 0.345, -0.25, -0.1, 0.12 },
		antL1 = { 0.2, 0.26, 0.08, -0.25, 0, -0.35 },
		antL2 = { 0, 0.35, 0, 0.5, 0, -0.25 },
		antR1 = { -0.2, 0.26, 0.08, -0.25, 0, 0.35 },
		antR2 = { 0, 0.35, 0, 0.5, 0, 0.25 },
		l1L = { 0.6, -0.2, 0.52, 0, -0.35, 0 },
		l1L2 = { 0.27, -0.22, 0, 0, 0, 0 },
		l2L = { 0.6, -0.2, 0, 0, 0, 0 },
		l2L2 = { 0.27, -0.22, 0, 0, 0, 0 },
		l3L = { 0.6, -0.2, -0.52, 0, 0.35, 0 },
		l3L2 = { 0.27, -0.22, 0, 0, 0, 0 },
		l1R = { -0.6, -0.2, 0.52, 0, 0.35, 0 },
		l1R2 = { -0.27, -0.22, 0, 0, 0, 0 },
		l2R = { -0.6, -0.2, 0, 0, 0, 0 },
		l2R2 = { -0.27, -0.22, 0, 0, 0, 0 },
		l3R = { -0.6, -0.2, -0.52, 0, -0.35, 0 },
		l3R2 = { -0.27, -0.22, 0, 0, 0, 0 }
	},
}, self)
end

-- ============ moss_bunny — ÐœÐ¾Ñ…Ð¾Ð²Ð¾Ð¹ Ð·Ð°Ð¹Ñ‡Ð¾Ð½Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.5})
local g = pulse(t, 2.9, 1.1)
a.T("nose", 0, ((0.014 * wave(t, 7)) * g), 0)
a.S("nose", (1 + ((0.04 * wave(t, 7)) * g)))
a.R("earL", 0, 0, (0.3 * pulse(t, 4.3, 0.32)))
a.R("earR", (0.3 * pulse(t, 5.9, 0.36, 1)), 0, ((-0.12) * pulse(t, 5.9, 0.36, 1)))
a.R("earL", (0.04 * wave(t, 0.4)), 0, 0)
a.R("earR", (0.04 * wave(t, 0.4, 0.3)), 0, 0)
a.R("tail", 0, ((0.35 * pulse(t, 3.3, 0.5, 2)) * wave(t, 6)), 0)
a.R("head", 0, 0, (0.14 * pulse(t, 7.5, 2.2, 3)))
end
self.move = function(t, a)
local p = ((t * 1.55) % 1)
a.blink(t)
a.T("root", 0, kf(p, 0, 0, 0.16, (-0.07), 0.5, 0.62, 0.84, 0, 1, 0), 0)
a.R("body", kf(p, 0, 0.08, 0.16, 0.2, 0.36, (-0.4), 0.66, 0.12, 0.86, 0.26, 1, 0.08), 0, 0)
local sq = kf(p, 0, 0, 0.16, 0.14, 0.3, (-0.12), 0.6, (-0.04), 0.86, 0.16, 1, 0)
a.S("body", (1 + (sq * 0.5)), (1 - sq), (1 + (sq * 0.5)))
local lg = kf(p, 0, 0, 0.16, (-0.3), 0.36, 1.0, 0.62, (-0.5), 0.86, (-0.25), 1, 0)
a.R("legL", lg)
a.R("legR", lg)
a.R("footL", ((-lg) * 0.7))
a.R("footR", ((-lg) * 0.7))
local ar = kf(p, 0, 0, 0.3, 0.55, 0.6, (-0.75), 0.86, (-0.15), 1, 0)
a.R("armL", ar)
a.R("armR", ar)
local er = kf(p, 0, 0, 0.2, (-0.15), 0.42, 0.7, 0.66, 0.35, 0.9, (-0.4), 1, 0)
a.R("earL", er)
a.R("earR", ((er * 0.85) + 0.05))
a.R("head", kf(p, 0, 0, 0.3, 0.28, 0.7, (-0.15), 0.9, 0.18, 1, 0), 0, 0)
a.R("tail", (0.4 * bump(p, 0.2, 0.6)), 0, 0)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.T("root", 0, (0.8 * bump(u, 0.1, 0.85)), 0)
a.R("root", 0, (TAU * ss(0.12, 0.82, u)), 0)
a.R("earL", 0, 0, ((0.5 * e) * wave(u, 3)))
a.R("earR", 0, 0, (((-0.5) * e) * wave(u, 3)))
a.R("legL", (0.7 * bump(u, 0.1, 0.5)))
a.R("legR", (0.7 * bump(u, 0.1, 0.5)))
a.R("armL", ((-0.6) * e))
a.R("armR", ((-0.6) * e))
a.brows((0.03 * e))
L.squash(a, u, 0.82, 1, 0.14)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.22, 0.2, 0.6, 0.36, 0.56, 0.46, 0.42, 0.6, 2.3, 0.8, 0, 1, 0), kf(u, 0, 0.44, 0.44, 0.5, 0.6, 1.03, 0.76, 1, 1, 1))
local pk = bump(u, 0.03, 0.44)
a.R("earL", ((-0.2) * pk), 0, ((0.45 * pk) * wave(u, 7)))
a.R("earR", ((-0.2) * pk), 0, (((-0.45) * pk) * wave(u, 7, 0.3)))
a.R("head", ((-0.2) * pk), ((0.35 * pk) * wave(u, 3.2)), 0)
local j = bump(u, 0.46, 0.8)
a.R("legL", (0.9 * j))
a.R("legR", (0.9 * j))
a.R("footL", ((-0.6) * j))
a.R("footR", ((-0.6) * j))
a.R("armL", ((-0.5) * j))
a.R("armR", ((-0.5) * j))
a.R("root", (((-0.3) * bump(u, 0.46, 0.62)) + (0.22 * bump(u, 0.64, 0.8))), 0, 0)
local fl = kf(u, 0, 0, 0.46, 0, 0.6, 0.6, 0.78, 0.2, 0.84, (-0.7), 0.92, 0.25, 1, 0)
a.R("earL", fl)
a.R("earR", (fl * 0.9))
L.squash(a, u, 0.78, 0.92, 0.24)
a.R("tail", 0, ((0.5 * bump(u, 0.84, 1)) * wave(u, 14)), 0)
end
register("moss_bunny", {
	name = "ÐœÐ¾Ñ…Ð¾Ð²Ð¾Ð¹ Ð·Ð°Ð¹Ñ‡Ð¾Ð½Ð¾Ðº", hd = 2.8, rd = 1.3, mv = { sp = 1.7, rad = 1.3, side = false },
	joints = { "root", "body", "tail", "legL", "footL", "armL", "legR", "footR", "armR", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.6, -0.3, 0, 0, 0 },
		tail = { 0, -0.08, -0.82, 0, 0, 0 },
		legL = { 0.44, -0.16, -0.2, 0, 0, 0 },
		footL = { 0.1, -0.33, 0.3, 0, 0, 0 },
		armL = { 0.24, -0.12, 0.66, 0, 0, 0 },
		legR = { -0.44, -0.16, -0.2, 0, 0, 0 },
		footR = { -0.1, -0.33, 0.3, 0, 0, 0 },
		armR = { -0.24, -0.12, 0.66, 0, 0, 0 },
		head = { 0, 0.5, 0.74, 0, 0, 0 },
		eyeL = { 0.27, 0.05, 0.535, 0, 0.42, 0 },
		browL = { 0.27, 0.29, 0.475, -0.25, 0.42, -0.22 },
		eyeR = { -0.27, 0.05, 0.535, 0, -0.42, 0 },
		browR = { -0.27, 0.29, 0.475, -0.25, -0.42, 0.22 },
		nose = { 0, -0.12, 0.56, 0, 0, 0 },
		earL = { 0.24, 0.4, -0.04, -0.1, 0, -0.22 },
		earR = { -0.24, 0.4, -0.04, -0.1, 0, 0.22 }
	},
}, self)
end

-- ============ hazel_squirrel — ÐžÑ€ÐµÑ…Ð¾Ð²Ñ‹Ð¹ Ð±ÐµÐ»ÑŒÑ‡Ð¾Ð½Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.8, look = 0.6})
local g = pulse(t, 3.4, 1.5)
a.R("armL", ((-0.4) * g))
a.R("armR", ((-0.4) * g))
a.T("nut", 0, (0.15 * g), ((-0.03) * g))
a.R("head", ((0.3 * g) + ((0.04 * wave(t, 8)) * g)), 0, 0)
a.T("nose", 0, ((0.01 * wave(t, 8)) * g), 0)
a.chain("t", 5, t, 0.45, 0.05, 0, 0.05, 0.16, 0.22)
a.R("t5", (0.18 * pulse(t, 2.3, 0.6)), 0, 0)
a.R("earL", 0, 0, (0.25 * pulse(t, 5.1, 0.25)))
a.R("earR", 0, 0, ((-0.25) * pulse(t, 3.7, 0.25, 1.5)))
end
self.move = function(t, a)
local f = 2.3
local p = ((t * f) % 1)
a.blink(t)
local ht = kf(p, 0, 0, 0.14, (-0.05), 0.5, 0.4, 0.86, 0, 1, 0)
local pt = kf(p, 0, 0.5, 0.3, 0.32, 0.6, 0.62, 1, 0.5)
a.T("root", 0, ht, 0)
a.R("body", pt, 0, 0)
a.R("head", ((-pt) * 0.75), 0, 0)
local lg = kf(p, 0, (-0.2), 0.2, 0.85, 0.6, (-0.6), 1, (-0.2))
a.R("legL", (lg - (pt * 0.6)))
a.R("legR", (lg - (pt * 0.6)))
a.R("footL", ((-lg) * 0.5))
a.R("footR", ((-lg) * 0.5))
a.R("armL", ((-0.2) * wave(t, f, 0.3)))
a.R("armR", ((-0.2) * wave(t, f, 0.3)))
a.R("t1", ((-0.55) - (0.3 * wave(t, f, (-0.12)))))
a.R("t2", ((-0.2) - (0.25 * wave(t, f, (-0.24)))))
a.R("t3", ((-0.15) - (0.22 * wave(t, f, (-0.36)))))
a.R("t4", ((-0.2) * wave(t, f, (-0.48))))
a.R("t5", ((-0.25) * wave(t, f, (-0.6))))
a.R("earL", (0.3 * bump(p, 0.3, 0.8)))
a.R("earR", (0.3 * bump(p, 0.3, 0.8)))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.T("root", 0, (0.35 * bump(u, 0.1, 0.6)), 0)
a.R("armL", ((-1.3) * e))
a.R("armR", ((-1.3) * e))
a.T("nut", 0, (0.55 * e), ((-0.12) * e))
a.R("head", ((-0.3) * e), 0, 0)
a.brows((0.03 * e))
for i = 1, 5 do
a.S(("t" .. i), (1 + (0.14 * e)))
a.R(("t" .. i), 0, 0, ((0.12 * e) * sin(((u * 40) + i))))
end
L.squash(a, u, 0.62, 0.9, 0.12)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.18, 0.24, 0.3, 0.4, 0.34, 0.5, 0.24, 0.64, 1.9, 0.8, 0, 1, 0), kf(u, 0, 0.4, 0.44, 0.46, 0.62, 1.03, 0.76, 1, 1, 1))
a.T("nut", 0, kf(u, 0, 0, 0.08, 0, 0.22, 2.6, 0.36, 0.6, 0.44, 0, 0.52, 0, 0.64, 0.9, 0.74, 0.2, 0.8, 0, 1, 0), kf(u, 0, 0, 0.22, (-0.2), 0.44, 0, 1, 0))
local lk = bump(u, 0.1, 0.42)
a.R("head", ((-0.5) * lk), 0, 0)
a.brows((0.03 * lk))
local j = bump(u, 0.5, 0.8)
a.R("armL", ((-1.5) * j))
a.R("armR", ((-1.5) * j))
a.R("legL", (0.8 * j))
a.R("legR", (0.8 * j))
a.R("root", ((-0.25) * bump(u, 0.5, 0.64)), 0, 0)
L.squash(a, u, 0.78, 0.92, 0.22)
local tw = (ss(0.5, 0.62, u) * (1 - ss(0.8, 1, u)))
for i = 1, 5 do
a.R(("t" .. i), (((-0.3) * tw) * sin(((u * 30) - (i * 0.9)))), 0, 0)
end
local fl = bump(u, 0.8, 1)
for i = 1, 5 do
a.S(("t" .. i), (1 + (0.18 * fl)))
end
end
register("hazel_squirrel", {
	name = "ÐžÑ€ÐµÑ…Ð¾Ð²Ñ‹Ð¹ Ð±ÐµÐ»ÑŒÑ‡Ð¾Ð½Ð¾Ðº", hd = 2.9, rd = 1.3, mv = { sp = 1.9, rad = 1.3, side = false },
	joints = { "root", "body", "legL", "footL", "armL", "legR", "footR", "armR", "nut", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR", "t1", "t2", "t3", "t4", "t5" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.56, 0.05, 0, 0, 0 },
		legL = { 0.36, -0.26, 0.08, 0, 0, 0 },
		footL = { 0.03, -0.21, 0.2, 0, 0, 0 },
		armL = { 0.42, 0.2, 0.12, 0, 0, 0 },
		legR = { -0.36, -0.26, 0.08, 0, 0, 0 },
		footR = { -0.03, -0.21, 0.2, 0, 0, 0 },
		armR = { -0.42, 0.2, 0.12, 0, 0, 0 },
		nut = { 0, -0.02, 0.54, 0, 0, 0 },
		head = { 0, 0.96, 0.14, 0, 0, 0 },
		eyeL = { 0.23, 0.04, 0.45, 0, 0.42, 0 },
		browL = { 0.23, 0.26, 0.39, -0.25, 0.42, -0.22 },
		eyeR = { -0.23, 0.04, 0.45, 0, -0.42, 0 },
		browR = { -0.23, 0.26, 0.39, -0.25, -0.42, 0.22 },
		nose = { 0, -0.1, 0.49, 0, 0, 0 },
		earL = { 0.3, 0.34, -0.02, 0, 0, -0.3 },
		earR = { -0.3, 0.34, -0.02, 0, 0, 0.3 },
		t1 = { 0, -0.36, -0.38, -0.3, 0, 0 },
		t2 = { 0, 0.6084, 0, 0.15, 0, 0 },
		t3 = { 0, 0.624, 0, -0.55, 0, 0 },
		t4 = { 0, 0.5772, 0, -0.9, 0, 0 },
		t5 = { 0, 0.4836, 0, -1, 0, 0 }
	},
}, self)
end

-- ============ flower_hedgehog — Ð¦Ð²ÐµÑ‚Ð¾Ñ‡Ð½Ñ‹Ð¹ Ñ‘Ð¶Ð¸Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 1.1, look = 0.7})
local g = pulse(t, 3.6, 1.6)
a.R("head", (((-0.22) * g) + ((0.05 * wave(t, 5)) * g)), 0, 0)
a.S("nose", (1 + ((0.06 * wave(t, 7)) * g)))
a.T("nose", 0, ((0.012 * wave(t, 7)) * g), 0)
for i = 1, 5 do
a.R(("sp" .. i), (0.07 * wave(t, 0.55, ((-i) * 0.17))), 0, (0.02 * wave(t, 0.4, (i * 0.2))))
end
a.R("earL", 0, 0, (0.3 * pulse(t, 4.4, 0.25)))
a.R("earR", 0, 0, ((-0.3) * pulse(t, 6.1, 0.25, 2)))
end
self.move = function(t, a)
local f = 2.9
a.blink(t)
a.R("body", (0.03 * wave(t, (f * 2))), (0.05 * wave(t, f, 0.25)), (0.085 * wave(t, f)))
a.T("body", 0, (0.022 * wave(t, (f * 2), 0.1)), 0)
a.R("head", (0.05 * wave(t, (f * 2), 0.3)), ((-0.08) * wave(t, f, 0.25)), ((-0.06) * wave(t, f)))
L.step(a, "flL", (t * f), 0.5, 0.05)
L.step(a, "blR", ((t * f) + 0.05), 0.5, 0.05)
L.step(a, "flR", ((t * f) + 0.5), 0.5, 0.05)
L.step(a, "blL", ((t * f) + 0.55), 0.5, 0.05)
for i = 1, 5 do
a.R(("sp" .. i), (0.06 * wave(t, (f * 2), ((-i) * 0.12))), 0, (0.06 * wave(t, f, ((-i) * 0.1))))
end
a.S("nose", (1 + (0.04 * wave(t, 6))))
end
self.react = function(u, a)
local e = min(1, (bump(u, 0, 1) * 1.6))
for i = 1, 5 do
a.R(("sp" .. i), ((0.42 * e) + ((0.05 * e) * sin(((u * 50) + i)))), 0, 0)
a.S(("sp" .. i), (1 + (0.12 * e)))
end
a.R("head", (0.75 * e), 0, 0)
a.T("head", 0, ((-0.1) * e), ((-0.12) * e))
a.T("body", 0, ((-0.06) * e), 0)
forEach({"flL", "flR", "blL", "blR"}, function(n)
return a.T(n, 0, (0.08 * e), 0)
end)
a.brows(((-0.02) * e), (0.15 * e))
for i = 1, 3 do
a.S(("f" .. i), (1 + (0.5 * bump(u, 0.3, 0.8))))
end
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.28, 0.3, 0.42, 0.44, 0.32, 0.6, 1.7, 0.78, 0, 1, 0), kf(u, 0, 0.42, 0.44, 0.48, 0.62, 1.03, 0.76, 1, 1, 1))
local ball = (1 - ss(0.74, 0.88, u))
a.R("head", (1.05 * ball), 0, 0)
a.T("head", 0, ((-0.18) * ball), ((-0.2) * ball))
forEach({"flL", "flR", "blL", "blR"}, function(n)
return a.T(n, 0, (0.16 * ball), 0)
end)
for i = 1, 5 do
a.R(("sp" .. i), (0.3 * ball), 0, 0)
end
a.R("root", (((TAU * 2) * ss(0.3, 0.76, u)) + ((0.25 * bump(u, 0.05, 0.3)) * wave(u, 8))), 0, 0)
a.T("root", 0, ((0.46 * ball) * iff((u > 0.3), 1, ss(0.0, 0.3, u))), 0)
L.squash(a, u, 0.76, 0.9, 0.2)
local pop = bump(u, 0.8, 0.96)
a.R("head", ((-0.3) * pop), 0, 0)
a.brows((0.03 * pop))
L.shake(a, u, 0.86, 1, 0.3, 3.5)
for i = 1, 5 do
a.R(("sp" .. i), ((0.2 * bump(u, 0.86, 1)) * sin(((u * 60) + i))), 0, 0)
end
end
register("flower_hedgehog", {
	name = "Ð¦Ð²ÐµÑ‚Ð¾Ñ‡Ð½Ñ‹Ð¹ Ñ‘Ð¶Ð¸Ðº", hd = 3, rd = 1.4, mv = { sp = 1, rad = 1.25, side = false },
	joints = { "root", "body", "sp1", "sp2", "sp3", "sp4", "sp5", "f1", "f2", "f3", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR", "flL", "blL", "flR", "blR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.44, -0.12, 0, 0, 0 },
		sp1 = { 0, 0.06, 0.42, 0, 0, 0 },
		sp2 = { 0, 0.06, 0.12, 0, 0, 0 },
		sp3 = { 0, 0.06, -0.18, 0, 0, 0 },
		sp4 = { 0, 0.06, -0.48, 0, 0, 0 },
		sp5 = { 0, 0.06, -0.78, 0, 0, 0 },
		f1 = { -0.2, 0.8, -0.3, -0.7, 0, 0.25 },
		f2 = { 0.3, 0.76, -0.34, -0.7, 0, -0.4 },
		f3 = { 0.42, 0.42, -0.5, -1, 0, -0.9 },
		head = { 0, 0.02, 0.84, 0, 0, 0 },
		eyeL = { 0.24, 0.07, 0.415, 0, 0.46, 0 },
		browL = { 0.24, 0.28, 0.355, -0.25, 0.46, -0.24 },
		eyeR = { -0.24, 0.07, 0.415, 0, -0.46, 0 },
		browR = { -0.24, 0.28, 0.355, -0.25, -0.46, 0.24 },
		nose = { 0, -0.08, 0.44, 0, 0, 0 },
		earL = { 0.37, 0.27, -0.04, 0, 0, -0.3 },
		earR = { -0.37, 0.27, -0.04, 0, 0, 0.3 },
		flL = { 0.4, -0.2, 0.46, 0, 0, 0 },
		blL = { 0.4, -0.2, -0.52, 0, 0, 0 },
		flR = { -0.4, -0.2, 0.46, 0, 0, 0 },
		blR = { -0.4, -0.2, -0.52, 0, 0, 0 }
	},
}, self)
end

-- ============ guardian_fawn — Ð¥Ñ€Ð°Ð½Ð¸Ñ‚ÐµÐ»ÑŒ-Ð¾Ð»ÐµÐ½Ñ‘Ð½Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 1.6, hn = "neck", look = 0.8})
a.R("head", 0, (0.1 * wave(t, 0.13, 0.2)), (0.16 * pulse(t, 6.3, 2.4, 1)))
a.R("earL", 0, (0.5 * pulse(t, 3.9, 0.28)), (0.2 * pulse(t, 3.9, 0.28)))
a.R("earR", 0, ((-0.5) * pulse(t, 5.3, 0.28, 1.2)), ((-0.2) * pulse(t, 5.3, 0.28, 1.2)))
a.R("tail", 0, 0, ((0.6 * pulse(t, 2.7, 0.7)) * wave(t, 5)))
a.T("body", (0.02 * wave(t, 0.2)), 0, 0)
a.R("body", 0, 0, (0.015 * wave(t, 0.2)))
a.R("flL", (0.05 * wave(t, 0.2)))
a.R("lfL", 0, 0, (0.05 * wave(t, 0.6)))
a.R("lfR", 0, 0, (0.05 * wave(t, 0.6, 0.3)))
end
self.move = function(t, a)
local f = 1.45
a.blink(t)
a.T("body", 0, (0.035 * wave(t, (f * 2), 0.1)), 0)
a.R("body", (0.02 * wave(t, (f * 2))), 0, (0.02 * wave(t, f)))
a.R("neck", (0.07 * wave(t, (f * 2), 0.2)), 0, 0)
a.R("head", ((-0.05) * wave(t, (f * 2), 0.3)), 0, 0)
L.step(a, "flL", (t * f), 0.5, 0.06, 0.75)
L.step(a, "blR", ((t * f) + 0.06), 0.45, 0.05, (-0.6))
L.step(a, "flR", ((t * f) + 0.5), 0.5, 0.06, 0.75)
L.step(a, "blL", ((t * f) + 0.56), 0.45, 0.05, (-0.6))
a.R("tail", (0.2 * wave(t, (f * 2))), 0, (0.15 * wave(t, f)))
a.R("earL", 0, 0, (0.08 * wave(t, (f * 2), 0.4)))
a.R("earR", 0, 0, ((-0.08) * wave(t, (f * 2), 0.4)))
a.R("lfL", (0.06 * wave(t, (f * 2), 0.5)))
a.R("lfR", (0.06 * wave(t, (f * 2), 0.5)))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("body", ((-0.3) * e), 0, 0)
a.T("body", 0, (0.12 * e), 0)
a.R("flL", ((-0.5) * e))
a.R("flR", ((-0.8) * e))
a.R("flL2", (1.0 * e))
a.R("flR2", (1.2 * e))
a.R("blL", (0.3 * e))
a.R("blR", (0.3 * e))
a.R("neck", ((-0.1) * e), 0, 0)
a.R("head", (0.15 * e), ((0.3 * e) * wave(u, 2)), 0)
a.R("earL", 0, 0, (0.3 * e))
a.R("earR", 0, 0, ((-0.3) * e))
a.R("tail", (0.5 * e), 0, ((0.5 * e) * wave(u, 5)))
a.brows((0.03 * e))
a.S("lfL", (1 + (0.2 * e)))
a.S("lfR", (1 + (0.2 * e)))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.1, 0.3, 0.2, 0.5, 0.3, 0.58, 0.22, 0.7, 1.05, 0.82, 0, 1, 0), kf(u, 0, 0.36, 0.3, 0.42, 0.56, 0.6, 0.7, 1.02, 0.8, 1, 1, 1))
local fold = (1 - ss(0.2, 0.56, u))
local wb = (ss(0.2, 0.4, u) * (1 - ss(0.56, 0.66, u)))
forEach({"flL", "flR"}, function(n)
a.R(n, ((-1.2) * fold))
a.R((n .. "2"), (2.2 * fold))
end)
forEach({"blL", "blR"}, function(n)
a.R(n, (1.0 * fold))
a.R((n .. "2"), ((-2.0) * fold))
end)
a.T("body", 0, ((-0.62) * fold), 0)
a.R("body", 0, 0, ((0.12 * wb) * wave(u, 7)))
a.R("flL", 0, 0, (((0.25 * wb) * (1 + wave(u, 6))) * 0.5))
a.R("flR", 0, 0, ((((-0.25) * wb) * (1 + wave(u, 6, 0.5))) * 0.5))
a.R("blL", 0, 0, (0.2 * wb))
a.R("blR", 0, 0, ((-0.2) * wb))
a.R("neck", ((0.5 * fold) - (0.3 * bump(u, 0.84, 1))), 0, 0)
a.R("head", ((-0.2) * fold), ((0.25 * wb) * wave(u, 3)), 0)
local j = bump(u, 0.58, 0.82)
a.R("flL", ((-0.4) * j))
a.R("flR", ((-0.4) * j))
a.R("blL", (0.4 * j))
a.R("blR", (0.4 * j))
L.squash(a, u, 0.8, 0.92, 0.14)
local lf = kf(u, 0, 0.02, 0.8, 0.02, 0.93, 1.2, 1, 1)
a.S("lfL", lf)
a.S("lfR", lf)
a.R("earL", 0, 0, (0.4 * bump(u, 0.84, 0.98)))
a.R("earR", 0, 0, ((-0.4) * bump(u, 0.84, 0.98)))
a.R("tail", 0, 0, ((0.6 * bump(u, 0.84, 1)) * wave(u, 16)))
end
register("guardian_fawn", {
	name = "Ð¥Ñ€Ð°Ð½Ð¸Ñ‚ÐµÐ»ÑŒ-Ð¾Ð»ÐµÐ½Ñ‘Ð½Ð¾Ðº", hd = 3.6, rd = 1.4, mv = { sp = 1.5, rad = 1.35, side = false },
	joints = { "root", "body", "tail", "neck", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "antL", "lfL", "earR", "antR", "lfR", "flL", "flL2", "blL", "blL2", "flR", "flR2", "blR", "blR2" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 1.25, -0.05, 0, 0, 0 },
		tail = { 0, 0.2, -0.7, -0.75, 0, 0 },
		neck = { 0, 0.2, 0.52, 0.42, 0, 0 },
		head = { 0, 0.74, 0.02, -0.42, 0, 0 },
		eyeL = { 0.23, 0.04, 0.42, 0, 0.44, 0 },
		browL = { 0.23, 0.26, 0.36, -0.25, 0.44, -0.22 },
		eyeR = { -0.23, 0.04, 0.42, 0, -0.44, 0 },
		browR = { -0.23, 0.26, 0.36, -0.25, -0.44, 0.22 },
		nose = { 0, -0.12, 0.44, 0, 0, 0 },
		earL = { 0.38, 0.16, -0.06, 0, -0.2, -1.05 },
		antL = { 0.17, 0.38, -0.03, -0.1, 0, -0.12 },
		lfL = { 0, 0.52, 0, 0, 0, 0 },
		earR = { -0.38, 0.16, -0.06, 0, 0.2, 1.05 },
		antR = { -0.17, 0.38, -0.03, -0.1, 0, 0.12 },
		lfR = { 0, 0.52, 0, 0, 0, 0 },
		flL = { 0.25, -0.18, 0.46, 0, 0, 0 },
		flL2 = { 0, -0.5, 0, 0, 0, 0 },
		blL = { 0.27, -0.12, -0.5, 0, 0, 0 },
		blL2 = { 0, -0.55, 0, 0, 0, 0 },
		flR = { -0.25, -0.18, 0.46, 0, 0, 0 },
		flR2 = { 0, -0.5, 0, 0, 0, 0 },
		blR = { -0.27, -0.12, -0.5, 0, 0, 0 },
		blR2 = { 0, -0.55, 0, 0, 0, 0 }
	},
}, self)
end

-- ============ sand_jerboa — ÐŸÐµÑÑ‡Ð°Ð½Ñ‹Ð¹ Ñ‚ÑƒÑˆÐºÐ°Ð½Ñ‡Ð¸Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.3})
a.R("earL", 0, (0.5 * pulse(t, 3.3, 0.3)), (0.2 * pulse(t, 3.3, 0.3)))
a.R("earR", 0, ((-0.5) * pulse(t, 4.7, 0.3, 1)), ((-0.2) * pulse(t, 4.7, 0.3, 1)))
a.chain("t", 5, t, 0.5, 0.04, 0.07, 0, 0.15, 0.2)
local g = pulse(t, 5.2, 1.4)
a.R("armL", (((-0.9) * g) + ((0.2 * g) * wave(t, 6))))
a.R("armR", (((-0.9) * g) + ((0.2 * g) * wave(t, 6, 0.5))))
a.R("head", (0.2 * g), 0, 0)
a.S("nose", (1 + ((0.05 * wave(t, 8)) * pulse(t, 2.6, 1))))
end
self.move = function(t, a)
local p = ((t * 1.7) % 1)
a.blink(t)
a.T("root", 0, kf(p, 0, 0, 0.14, (-0.1), 0.5, 0.75, 0.86, 0, 1, 0), 0)
a.R("body", kf(p, 0, 0.1, 0.14, 0.3, 0.34, (-0.3), 0.66, 0.15, 0.88, 0.35, 1, 0.1))
local lg = kf(p, 0, 0, 0.14, (-0.5), 0.34, 0.9, 0.62, (-0.5), 0.86, (-0.3), 1, 0)
a.R("legL", lg)
a.R("legR", lg)
a.R("shinL", ((-lg) * 1.2))
a.R("shinR", ((-lg) * 1.2))
a.R("footL", ((lg * 0.6) + (0.5 * bump(p, 0.3, 0.8))))
a.R("footR", ((lg * 0.6) + (0.5 * bump(p, 0.3, 0.8))))
local er = kf(p, 0, 0, 0.3, 0.6, 0.66, 0.3, 0.9, (-0.3), 1, 0)
a.R("earL", er)
a.R("earR", er)
a.R("t1", kf(p, 0, 0, 0.3, (-0.5), 0.7, 0.5, 1, 0))
a.R("t2", kf(p, 0, 0, 0.36, (-0.3), 0.76, 0.4, 1, 0))
a.R("t3", kf(p, 0, 0, 0.42, (-0.3), 0.82, 0.4, 1, 0))
a.R("t5", (0.4 * wave(t, 1.7, 0.6)))
a.R("armL", ((-0.3) * bump(p, 0.2, 0.8)))
a.R("armR", ((-0.3) * bump(p, 0.2, 0.8)))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
local h = (bump(((u * 2) % 1), 0, 1) * iff((u < 0.9), 1, 0))
a.T("root", 0, (0.35 * h), 0)
a.R("legL", (0.5 * h))
a.R("legR", (0.5 * h))
a.R("shinL", ((-0.6) * h))
a.R("shinR", ((-0.6) * h))
a.R("earL", ((-0.2) * e), 0, (0.25 * e))
a.R("earR", ((-0.2) * e), 0, ((-0.25) * e))
a.brows((0.03 * e))
a.R("t1", ((0.4 * e) * wave(u, 3)))
a.R("head", ((-0.15) * e), ((0.3 * e) * wave(u, 2)), 0)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, (-0.1), 0.22, 0.3, 0.38, 0.26, 0.46, 0.1, 0.62, 2.2, 0.8, 0, 1, 0), kf(u, 0, 0.42, 0.44, 0.5, 0.6, 1.03, 0.76, 1, 1, 1))
local pk = bump(u, 0.02, 0.44)
a.R("earL", 0, ((0.6 * pk) * wave(u, 6)), (0.3 * pk))
a.R("earR", 0, (((-0.6) * pk) * wave(u, 6, 0.4)), ((-0.3) * pk))
a.R("head", ((-0.2) * pk), ((0.5 * pk) * wave(u, 3)), 0)
local j = bump(u, 0.46, 0.8)
a.R("legL", (0.9 * j))
a.R("legR", (0.9 * j))
a.R("shinL", ((-1.1) * j))
a.R("shinR", ((-1.1) * j))
a.R("footL", (0.7 * j))
a.R("footR", (0.7 * j))
a.R("root", (((-0.3) * bump(u, 0.46, 0.62)) + (0.2 * bump(u, 0.64, 0.8))), 0, 0)
local er = kf(u, 0, 0, 0.46, 0, 0.6, 0.7, 0.78, 0.2, 0.84, (-0.5), 0.92, 0.2, 1, 0)
a.R("earL", er)
a.R("earR", er)
L.squash(a, u, 0.78, 0.92, 0.2)
for i = 1, 5 do
a.R(("t" .. i), ((0.35 * bump(u, 0.6, 1)) * sin(((u * 26) - (i * 0.8)))), 0, 0)
end
end
register("sand_jerboa", {
	name = "ÐŸÐµÑÑ‡Ð°Ð½Ñ‹Ð¹ Ñ‚ÑƒÑˆÐºÐ°Ð½Ñ‡Ð¸Ðº", hd = 2.8, rd = 1.2, mv = { sp = 2.1, rad = 1.35, side = false },
	joints = { "root", "body", "legL", "shinL", "footL", "armL", "legR", "shinR", "footR", "armR", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR", "t1", "t2", "t3", "t4", "t5" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.95, -0.05, 0.25, 0, 0 },
		legL = { 0.32, -0.2, -0.08, 0, 0, 0 },
		shinL = { 0.02, -0.2, 0.1, -0.25, 0, 0 },
		footL = { 0, -0.46, 0, 0, 0, 0 },
		armL = { 0.2, 0.1, 0.4, -0.9, 0, 0 },
		legR = { -0.32, -0.2, -0.08, 0, 0, 0 },
		shinR = { -0.02, -0.2, 0.1, -0.25, 0, 0 },
		footR = { 0, -0.46, 0, 0, 0, 0 },
		armR = { -0.2, 0.1, 0.4, -0.9, 0, 0 },
		head = { 0, 0.66, 0.12, -0.25, 0, 0 },
		eyeL = { 0.2068, 0.04, 0.4074, 0, 0.44, 0 },
		browL = { 0.2068, 0.261, 0.3474, -0.25, 0.44, -0.22 },
		eyeR = { -0.2068, 0.04, 0.4074, 0, -0.44, 0 },
		browR = { -0.2068, 0.261, 0.3474, -0.25, -0.44, 0.22 },
		nose = { 0, -0.1, 0.441, 0, 0, 0 },
		earL = { 0.27, 0.28, -0.06, -0.1, 0, -0.42 },
		earR = { -0.27, 0.28, -0.06, -0.1, 0, 0.42 },
		t1 = { 0, -0.36, -0.36, -0.9, 0, 0 },
		t2 = { 0, 0, -0.3, 0.35, 0, 0 },
		t3 = { 0, 0, -0.3, 0.5, 0, 0 },
		t4 = { 0, 0, -0.3, 0.55, 0, 0 },
		t5 = { 0, 0, -0.28, 0.4, 0, 0 }
	},
}, self)
end

-- ============ amber_armadillo — Ð¯Ð½Ñ‚Ð°Ñ€Ð½Ñ‹Ð¹ Ð±Ñ€Ð¾Ð½ÐµÐ½Ð¾ÑÐµÑ† ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.7, look = 0.6})
local g = pulse(t, 4.1, 1.8)
a.R("head", ((0.3 * g) + ((0.04 * g) * wave(t, 6))), ((0.15 * g) * wave(t, 1.2)), 0)
a.S("nose", (1 + ((0.05 * wave(t, 7)) * g)))
a.S("shell", (1 + (0.01 * wave(t, 0.42))), (1 + (0.012 * wave(t, 0.42, 0.2))), 1)
a.chain("t", 5, t, 0.5, 0.03, 0.06, 0, 0.14, 0.2)
a.R("earL", 0, 0, (0.3 * pulse(t, 3.1, 0.25)))
a.R("earR", 0, 0, ((-0.3) * pulse(t, 4.3, 0.25, 1)))
end
self.move = function(t, a)
local f = 3.2
a.blink(t)
a.T("body", 0, (0.03 * wave(t, (f * 2))), 0)
a.R("body", (0.03 * wave(t, (f * 2), 0.1)), (0.04 * wave(t, f)), (0.05 * wave(t, f, 0.2)))
a.R("shell", ((-0.03) * wave(t, (f * 2), 0.3)), 0, ((-0.03) * wave(t, f, 0.35)))
a.R("head", (0.12 + (0.05 * wave(t, (f * 2), 0.25))), ((-0.08) * wave(t, f)), 0)
L.step(a, "flL", (t * f), 0.6, 0.06)
L.step(a, "blR", ((t * f) + 0.05), 0.6, 0.06)
L.step(a, "flR", ((t * f) + 0.5), 0.6, 0.06)
L.step(a, "blL", ((t * f) + 0.55), 0.6, 0.06)
a.chain("t", 5, t, f, 0.05, 0.1, 0, 0.12, 0.25)
end
self.react = function(u, a)
local c = (ss(0, 0.2, u) * (1 - ss(0.78, 1, u)))
a.R("head", (1.3 * c), 0, 0)
a.T("head", 0, ((-0.2) * c), ((-0.26) * c))
forEach({"flL", "flR", "blL", "blR"}, function(n)
return a.T(n, 0, (0.2 * c), 0)
end)
for i = 1, 5 do
a.R(("t" .. i), ((-0.5) * c), 0, 0)
end
a.T("root", 0, ((0.2 * c) + (0.25 * bump(u, 0.2, 0.5))), 0)
a.R("root", (TAU * ss(0.2, 0.78, u)), 0, 0)
a.S("shell", (1 + (0.05 * c)))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.3, 0.26, 0.45, 0.4, 0.35, 0.52, 1.5, 0.64, 0.2, 0.72, 0.7, 0.8, 0, 1, 0), kf(u, 0, 0.42, 0.4, 0.5, 0.56, 1.02, 0.7, 1, 1, 1))
local c = (1 - ss(0.78, 0.9, u))
a.R("head", (1.3 * c), 0, 0)
a.T("head", 0, ((-0.2) * c), ((-0.26) * c))
forEach({"flL", "flR", "blL", "blR"}, function(n)
return a.T(n, 0, (0.2 * c), 0)
end)
for i = 1, 5 do
a.R(("t" .. i), ((-0.5) * c), 0, 0)
end
a.T("root", 0, (0.22 * c), 0)
a.R("root", (((TAU * 3) * ss(0.26, 0.8, u)) + ((0.2 * bump(u, 0.02, 0.26)) * wave(u, 9))), 0, 0)
L.squash(a, u, 0.8, 0.92, 0.18)
a.R("head", ((-0.25) * bump(u, 0.86, 1)), 0, 0)
L.shake(a, u, 0.88, 1, 0.25, 3)
end
register("amber_armadillo", {
	name = "Ð¯Ð½Ñ‚Ð°Ñ€Ð½Ñ‹Ð¹ Ð±Ñ€Ð¾Ð½ÐµÐ½Ð¾ÑÐµÑ†", hd = 3, rd = 1.5, mv = { sp = 1.3, rad = 1.3, side = false },
	joints = { "root", "body", "shell", "flL", "blL", "flR", "blR", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR", "t1", "t2", "t3", "t4", "t5" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.6, -0.08, 0, 0, 0 },
		shell = { 0, 0.02, 0, 0, 0, 0 },
		flL = { 0.4, -0.28, 0.42, 0, 0, 0 },
		blL = { 0.4, -0.28, -0.5, 0, 0, 0 },
		flR = { -0.4, -0.28, 0.42, 0, 0, 0 },
		blR = { -0.4, -0.28, -0.5, 0, 0, 0 },
		head = { 0, -0.04, 0.84, 0, 0, 0 },
		eyeL = { 0.21, 0.05, 0.4, 0, 0.5, 0 },
		browL = { 0.21, 0.25, 0.34, -0.25, 0.5, -0.22 },
		eyeR = { -0.21, 0.05, 0.4, 0, -0.5, 0 },
		browR = { -0.21, 0.25, 0.34, -0.25, -0.5, 0.22 },
		nose = { 0, -0.1, 0.4, 0, 0, 0 },
		earL = { 0.27, 0.26, -0.12, 0, 0, -0.3 },
		earR = { -0.27, 0.26, -0.12, 0, 0, 0.3 },
		t1 = { 0, -0.14, -0.82, -0.25, 0, 0 },
		t2 = { 0, 0, -0.26, -0.05, 0, 0 },
		t3 = { 0, 0, -0.22, 0.05, 0, 0 },
		t4 = { 0, 0, -0.2, 0.1, 0, 0 },
		t5 = { 0, 0, -0.18, 0.1, 0, 0 }
	},
}, self)
end

-- ============ sun_lion_cub — Ð¡Ð¾Ð»Ð½ÐµÑ‡Ð½Ñ‹Ð¹ Ð»ÑŒÐ²Ñ‘Ð½Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.9})
a.R("head", 0, 0, (0.15 * pulse(t, 6.5, 2.2, 2)))
a.chain("t", 3, t, 0.6, 0.05, 0.1, 0, 0.2, 0.3)
a.R("tuft", 0, ((0.5 * pulse(t, 2.4, 0.4)) * wave(t, 5)), 0)
a.R("earL", 0, 0, (0.3 * pulse(t, 3.6, 0.25)))
a.R("earR", 0, 0, ((-0.3) * pulse(t, 5.2, 0.25, 1)))
a.R("maneL", 0, (0.04 * wave(t, 0.5)), (0.03 * wave(t, 0.42)))
a.R("maneR", 0, ((-0.04) * wave(t, 0.5)), ((-0.03) * wave(t, 0.42)))
a.R("maneT", (0.05 * wave(t, 0.42, 0.2)))
local y = pulse(t, 9, 1.6, 4)
a.R("head", ((-0.35) * y), 0, 0)
a.T("nose", 0, ((-0.04) * y), 0)
a.S("eyeL", 1, (1 - (0.8 * y)), 1)
a.S("eyeR", 1, (1 - (0.8 * y)), 1)
end
self.move = function(t, a)
local f = 1.9
local p = ((t * f) % 1)
a.blink(t)
a.T("root", 0, kf(p, 0, 0, 0.5, 0.3, 1, 0), 0)
a.R("body", (0.4 + kf(p, 0, 0.1, 0.3, (-0.2), 0.7, 0.2, 1, 0.1)))
a.R("head", (-0.4), 0, 0)
local fr = kf(p, 0, 0.3, 0.3, (-0.8), 0.7, 0.5, 1, 0.3)
local bk = kf(p, 0, (-0.4), 0.25, 0.8, 0.7, (-0.5), 1, (-0.4))
a.R("armL", (fr - 0.4))
a.R("armR", (fr - 0.3))
a.R("legL", bk)
a.R("legR", bk)
a.R("footL", ((-bk) * 0.6))
a.R("footR", ((-bk) * 0.6))
a.R("maneL", 0, (0.12 * wave(t, f, 0.3)), 0)
a.R("maneR", 0, ((-0.12) * wave(t, f, 0.3)), 0)
a.R("maneT", (0.15 * wave(t, f, 0.3)))
a.chain("t", 3, t, f, 0.25, 0.05, 0, 0.15, 0.2)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("head", ((-0.45) * e), 0, 0)
a.T("nose", 0, ((-0.05) * e), 0)
a.S("maneL", (1 + (0.2 * e)))
a.S("maneR", (1 + (0.2 * e)))
a.S("maneT", (1 + (0.25 * e)))
a.R("maneL", 0, 0, ((0.05 * e) * sin((u * 50))))
a.R("maneR", 0, 0, (((-0.05) * e) * sin((u * 50))))
a.R("armR", ((-1.0) * e), 0, 0)
a.brows(((-0.02) * e), (0.2 * e))
a.R("tuft", 0, ((0.6 * e) * wave(u, 4)), 0)
a.T("root", 0, (0.08 * e), 0)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.2, 0.3, 0.34, 0.44, 0.25, 0.6, 1.5, 0.78, 0, 1, 0), kf(u, 0, 0.42, 0.44, 0.5, 0.6, 1.03, 0.76, 1, 1, 1))
local pk = bump(u, 0.02, 0.44)
a.R("head", ((-0.2) * pk), ((0.4 * pk) * wave(u, 3)), 0)
a.R("earL", 0, 0, ((0.4 * pk) * wave(u, 8)))
a.R("earR", 0, 0, (((-0.4) * pk) * wave(u, 8, 0.3)))
local j = bump(u, 0.46, 0.8)
a.R("body", (0.7 * j))
a.R("head", ((-0.5) * j), 0, 0)
a.R("armL", ((-1.3) * j))
a.R("armR", ((-1.3) * j))
a.R("legL", (0.8 * j))
a.R("legR", (0.8 * j))
L.squash(a, u, 0.76, 0.9, 0.2)
local sh = bump(u, 0.84, 1)
a.R("head", 0, 0, ((0.4 * sh) * sin((u * 70))))
a.S("maneL", (1 + (0.15 * sh)))
a.S("maneR", (1 + (0.15 * sh)))
a.S("maneT", (1 + (0.2 * sh)))
a.R("tuft", 0, ((0.6 * sh) * wave(u, 18)), 0)
end
register("sun_lion_cub", {
	name = "Ð¡Ð¾Ð»Ð½ÐµÑ‡Ð½Ñ‹Ð¹ Ð»ÑŒÐ²Ñ‘Ð½Ð¾Ðº", hd = 3, rd = 1.4, mv = { sp = 1.7, rad = 1.3, side = false },
	joints = { "root", "body", "armL", "legL", "footL", "armR", "legR", "footR", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR", "maneL", "maneR", "maneT", "t1", "t2", "t3", "tuft" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.62, -0.12, 0, 0, 0 },
		armL = { 0.26, -0.04, 0.42, 0, 0, 0 },
		legL = { 0.42, -0.24, -0.02, 0, 0, 0 },
		footL = { 0.04, -0.28, 0.32, 0, 0, 0 },
		armR = { -0.26, -0.04, 0.42, 0, 0, 0 },
		legR = { -0.42, -0.24, -0.02, 0, 0, 0 },
		footR = { -0.04, -0.28, 0.32, 0, 0, 0 },
		head = { 0, 0.84, 0.22, 0, 0, 0 },
		eyeL = { 0.2444, 0.048, 0.4656, 0, 0.44, 0 },
		browL = { 0.2444, 0.2872, 0.4056, -0.25, 0.44, -0.22 },
		eyeR = { -0.2444, 0.048, 0.4656, 0, -0.44, 0 },
		browR = { -0.2444, 0.2872, 0.4056, -0.25, -0.44, 0.22 },
		nose = { 0, -0.12, 0.504, 0, 0, 0 },
		earL = { 0.37, 0.38, 0, 0, 0, 0 },
		earR = { -0.37, 0.38, 0, 0, 0, 0 },
		maneL = { 0, -0.02, -0.14, 0, 0, 0 },
		maneR = { 0, -0.02, -0.14, 0, 0, 0 },
		maneT = { 0, 0, -0.1, 0, 0, 0 },
		t1 = { 0, -0.3, -0.56, 0.7, 0, 0 },
		t2 = { 0, 0, -0.25, 0.5, 0, 0 },
		t3 = { 0, 0, -0.25, 0.45, 0, 0 },
		tuft = { 0, 0, -0.24, 0, 0, 0 }
	},
}, self)
end

-- ============ honey_griffin — ÐœÐµÐ´Ð¾Ð²Ñ‹Ð¹ Ð³Ñ€Ð¸Ñ„Ð¾Ð½Ñ‡Ð¸Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 1.3, head = 0})
local k = math.floor((t / 1.7))
local e = ss(0, 0.12, ((t / 1.7) % 1))
local h = function(n)
return (sin((n * 12.9898)) * 0.5)
end
a.R("head", (0.06 * h((k + 2))), (0.5 * (h(k) + ((h((k + 1)) - h(k)) * e))), (0.25 * (h((k + 5)) + ((h((k + 6)) - h((k + 5))) * e))))
local ru = pulse(t, 5.5, 1.2)
L.flap(a, (((0.25 * ru) + (0.03 * wave(t, 0.42))) + ((0.08 * ru) * wave(t, 7))))
a.R("crest", ((0.15 * ru) + (0.04 * wave(t, 0.5))))
a.chain("t", 3, t, 0.5, 0.04, 0.1, 0, 0.2, 0.3)
a.R("tuft", 0, ((0.4 * pulse(t, 2.9, 0.4)) * wave(t, 5)), 0)
end
self.move = function(t, a)
local f = 1.7
a.blink(t)
a.T("body", 0, (0.04 * wave(t, (f * 2), 0.1)), 0)
a.R("body", (0.02 * wave(t, (f * 2))), 0, (0.02 * wave(t, f)))
a.R("head", (0.05 * wave(t, (f * 2), 0.3)), 0, 0)
L.step(a, "flL", (t * f), 0.5, 0.07, 0.7)
L.step(a, "blR", ((t * f) + 0.06), 0.45, 0.05, (-0.5))
L.step(a, "flR", ((t * f) + 0.5), 0.5, 0.07, 0.7)
L.step(a, "blL", ((t * f) + 0.56), 0.45, 0.05, (-0.5))
L.flap(a, (0.55 + (0.4 * wave(t, (f * 2), 0.15))))
a.R("crest", (0.12 * wave(t, (f * 2), 0.4)))
a.chain("t", 3, t, f, 0.1, 0.12, 0, 0.15, 0.2)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
L.flap(a, ((1.25 * e) + ((0.1 * e) * sin((u * 40)))))
a.R("head", ((-0.5) * e), 0, 0)
a.R("nose", (((0.25 * e) * (1 + sin((u * 40)))) * 0.5))
a.R("crest", (0.4 * e))
a.R("body", ((-0.25) * e))
a.T("body", 0, (0.1 * e), 0)
a.R("flL", ((-0.6) * e))
a.R("flR", ((-0.3) * e))
a.R("blL", (0.25 * e))
a.R("blR", (0.25 * e))
a.brows(((-0.02) * e), (0.25 * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.15, 0.3, 0.3, 0.42, 0.22, 0.58, 1.5, 0.7, 1.2, 0.82, 0, 1, 0), kf(u, 0, 0.4, 0.4, 0.46, 0.56, 1.02, 0.7, 1, 1, 1))
L.flap(a, kf(u, 0, (-0.25), 0.26, (-0.25), 0.42, 1.3, 0.5, 0.2, 0.58, 1.35, 0.66, 0.3, 0.74, 1.25, 0.82, 0.6, 0.92, 0.9, 1, 0))
a.R("wingL", ((-0.3) * bump(u, 0.26, 0.8)))
a.R("wingR", ((-0.3) * bump(u, 0.26, 0.8)))
local cr = (1 - ss(0.3, 0.5, u))
a.R("head", ((0.5 * cr) - (0.3 * bump(u, 0.84, 1))), 0, 0)
forEach({"flL", "flR"}, function(n)
a.R(n, (((-0.9) * cr) - (0.4 * bump(u, 0.5, 0.8))))
a.R((n .. "2"), ((1.6 * cr) + (0.6 * bump(u, 0.5, 0.8))))
end)
forEach({"blL", "blR"}, function(n)
a.R(n, ((0.8 * cr) + (0.4 * bump(u, 0.5, 0.8))))
a.R((n .. "2"), ((-1.4) * cr))
end)
a.T("body", 0, ((-0.4) * cr), 0)
L.squash(a, u, 0.8, 0.92, 0.15)
a.R("crest", (0.4 * bump(u, 0.84, 1)))
a.chain("t", 3, (u * 8), 1, (0.15 * bump(u, 0.4, 1)), 0.1, 0, 0.2, 0.2)
end
register("honey_griffin", {
	name = "ÐœÐµÐ´Ð¾Ð²Ñ‹Ð¹ Ð³Ñ€Ð¸Ñ„Ð¾Ð½Ñ‡Ð¸Ðº", hd = 3.4, rd = 1.4, mv = { sp = 1.6, rad = 1.35, side = false },
	joints = { "root", "body", "blL", "blL2", "flL", "flL2", "wingL", "blR", "blR2", "flR", "flR2", "wingR", "t1", "t2", "t3", "tuft", "head", "eyeL", "browL", "eyeR", "browR", "nose", "crest" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.8, -0.12, 0, 0, 0 },
		blL = { 0.3, -0.1, -0.42, 0, 0, 0 },
		blL2 = { 0, -0.3, 0, 0, 0, 0 },
		flL = { 0.24, -0.12, 0.44, 0, 0, 0 },
		flL2 = { 0, -0.32, 0, 0, 0, 0 },
		wingL = { 0.3, 0.26, -0.02, 0, 0, -0.32 },
		blR = { -0.3, -0.1, -0.42, 0, 0, 0 },
		blR2 = { 0, -0.3, 0, 0, 0, 0 },
		flR = { -0.24, -0.12, 0.44, 0, 0, 0 },
		flR2 = { 0, -0.32, 0, 0, 0, 0 },
		wingR = { -0.3, 0.26, -0.02, 0, 0, 0.32 },
		t1 = { 0, -0.05, -0.62, 0.2, 0, 0 },
		t2 = { 0, 0, -0.25, 0.55, 0, 0 },
		t3 = { 0, 0, -0.25, 0.6, 0, 0 },
		tuft = { 0, 0, -0.22, 0, 0, 0 },
		head = { 0, 0.56, 0.5, 0, 0, 0 },
		eyeL = { 0.2, 0.05, 0.345, 0, 0.55, 0 },
		browL = { 0.2, 0.26, 0.295, -0.25, 0.55, -0.3 },
		eyeR = { -0.2, 0.05, 0.345, 0, -0.55, 0 },
		browR = { -0.2, 0.26, 0.295, -0.25, -0.55, 0.3 },
		nose = { 0, -0.06, 0.36, 0, 0, 0 },
		crest = { 0, 0.28, -0.08, 0, 0, 0 }
	},
}, self)
end

-- ============ amber_basilisk — Ð¯Ð½Ñ‚Ð°Ñ€Ð½Ñ‹Ð¹ Ð²Ð°ÑÐ¸Ð»Ð¸ÑÐº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 1.9, look = 0.5})
a.R("head", 0, (0.3 * wave(t, 0.07)), 0)
for i = 1, 5 do
a.S(("cr" .. i), (1 + (0.05 * wave(t, 0.5, (i * 0.13)))))
end
a.R("crest", (0.05 * wave(t, 0.42)))
a.chain("t", 5, t, 0.3, 0, 0.14, 0, 0.14, 0.25)
a.T("body", 0, (0.01 * wave(t, 0.42)), 0)
a.R("nose", (0.1 * pulse(t, 6, 0.5)))
end
self.move = function(t, a)
local f = 1.5
a.blink(t)
a.R("body", 0, (0.16 * wave(t, f)), (0.03 * wave(t, f)))
a.R("head", 0, ((-0.2) * wave(t, f, 0.05)), 0)
a.T("body", 0, (0.015 * wave(t, (f * 2))), 0)
forEach({{"flL", 1, 0}, {"blR", (-1), 0.04}, {"flR", (-1), 0.5}, {"blL", 1, 0.54}}, function(q)
L.sideStep(a, q[1], q[2], ((t * f) + q[3]), 0.55, 0.3, 0.3)
end)
a.chain("t", 5, t, f, 0, 0.2, 0, 0.16, 0.25)
for i = 1, 5 do
a.R(("cr" .. i), (0.04 * wave(t, (f * 2), (i * 0.1))))
end
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("body", ((-0.3) * e))
a.T("body", 0, (0.12 * e), 0)
a.R("head", ((-0.3) * e), 0, 0)
a.R("nose", (0.3 * e))
a.R("crest", ((-0.3) * e))
for i = 1, 5 do
a.S(("cr" .. i), (1 + (0.3 * e)))
a.R(("cr" .. i), 0, 0, ((0.04 * e) * sin(((u * 60) + i))))
end
a.R("flL", 0, 0, (0.3 * e))
a.R("flR", 0, 0, ((-0.3) * e))
a.chain("t", 5, (u * 3), 1, 0, (0.25 * e), 0, 0.15, 0.2)
a.brows(((-0.03) * e), (0.3 * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, (-0.25), 0.3, 0.35, 0.46, 0.3, 0.62, 0.8, 0.78, 0, 1, 0), kf(u, 0, 0.5, 0.3, 0.56, 0.6, 1.02, 0.74, 1, 1, 1))
for i = 1, 5 do
a.S(("cr" .. i), kf(u, 0, 0.3, (0.06 + (i * 0.04)), 0.3, (0.16 + (i * 0.04)), 1.3, (0.3 + (i * 0.04)), 1, 0.84, 1, 0.92, 1.25, 1, 1))
end
a.R("head", (((-0.5) * bump(u, 0, 0.4)) + (0.3 * bump(u, 0.46, 0.7))), ((0.5 * bump(u, 0.1, 0.46)) * wave(u, 2.5)), 0)
a.R("root", 0, (TAU * ss(0.4, 0.8, u)), 0)
a.R("body", 0, ((0.3 * bump(u, 0.4, 0.8)) * wave(u, 6)), 0)
a.chain("t", 5, (u * 7), 1, 0, (0.3 * bump(u, 0.3, 0.9)), 0, 0.16, 0.2)
forEach({{"flL", 1, 0}, {"blR", (-1), 0.04}, {"flR", (-1), 0.5}, {"blL", 1, 0.54}}, function(q)
return L.sideStep(a, q[1], q[2], ((u * 9) + q[3]), (0.5 * bump(u, 0.4, 0.82)), 0.3, 0.3)
end)
local fl = bump(u, 0.82, 1)
a.R("body", ((-0.25) * fl))
a.R("head", ((-0.25) * fl), 0, 0)
a.R("crest", ((-0.25) * fl))
a.R("nose", (0.25 * fl))
a.brows(((-0.02) * fl), (0.25 * fl))
end
register("amber_basilisk", {
	name = "Ð¯Ð½Ñ‚Ð°Ñ€Ð½Ñ‹Ð¹ Ð²Ð°ÑÐ¸Ð»Ð¸ÑÐº", hd = 4, rd = 1.5, mv = { sp = 1.3, rad = 1.35, side = false },
	joints = { "root", "body", "flL", "flL2", "blL", "blL2", "flR", "flR2", "blR", "blR2", "t1", "t2", "t3", "t4", "t5", "head", "eyeL", "browL", "eyeR", "browR", "nose", "crest", "cr1", "cr2", "cr3", "cr4", "cr5" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.44, -0.05, 0, 0, 0 },
		flL = { 0.4, -0.06, 0.46, 0, 0, 0 },
		flL2 = { 0.33, -0.04, 0, 0, 0, 0 },
		blL = { 0.4, -0.06, -0.46, 0, 0, 0 },
		blL2 = { 0.33, -0.04, 0, 0, 0, 0 },
		flR = { -0.4, -0.06, 0.46, 0, 0, 0 },
		flR2 = { -0.33, -0.04, 0, 0, 0, 0 },
		blR = { -0.4, -0.06, -0.46, 0, 0, 0 },
		blR2 = { -0.33, -0.04, 0, 0, 0, 0 },
		t1 = { 0, -0.02, -0.72, 0.05, 0, 0 },
		t2 = { 0, 0, -0.3, 0.02, 0, 0 },
		t3 = { 0, 0, -0.3, 0.08, 0, 0 },
		t4 = { 0, 0, -0.28, 0.12, 0, 0 },
		t5 = { 0, 0, -0.26, 0.15, 0, 0 },
		head = { 0, 0.14, 0.8, 0, 0, 0 },
		eyeL = { 0.25, 0.1, 0.35, 0, 0.55, 0 },
		browL = { 0.25, 0.32, 0.29, -0.25, 0.55, -0.26 },
		eyeR = { -0.25, 0.1, 0.35, 0, -0.55, 0 },
		browR = { -0.25, 0.32, 0.29, -0.25, -0.55, 0.26 },
		nose = { 0, -0.08, 0.36, 0, 0, 0 },
		crest = { 0, 0.3, -0.1, -0.15, 0, 0 },
		cr1 = { 0, 0, 0, 0, 0, 0 },
		cr2 = { 0.057531065, 0, -0.03, 0, 0, -0.5 },
		cr3 = { -0.057531065, 0, -0.03, 0, 0, 0.5 },
		cr4 = { 0.097609861, 0, -0.057, 0, 0, -0.95 },
		cr5 = { -0.097609861, 0, -0.057, 0, 0, 0.95 }
	},
}, self)
end

-- ============ bubble_crab — ÐŸÑƒÐ·Ñ‹Ñ€ÑŒÐºÐ¾Ð²Ñ‹Ð¹ ÐºÑ€Ð°Ð±Ð¸Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.4, head = 0})
local sn = pulse(t, 2.6, 0.5)
local s2 = pulse(t, 3.7, 0.4, 1)
a.R("pinL", 0, 0, ((((-0.5) * sn) * (1 + wave(t, 7))) * 0.5))
a.R("clawL2", 0, 0, (0.1 * wave(t, 0.4)))
a.R("pinR", 0, 0, (0.6 * s2))
a.R("clawR", 0, 0, (0.12 * wave(t, 0.5)))
a.R("stalkL", (0.1 * wave(t, 0.31)), 0, (0.22 * wave(t, 0.19)))
a.R("stalkR", (0.1 * wave(t, 0.27, 0.4)), 0, (0.22 * wave(t, 0.23, 0.5)))
a.T("bubA", 0, (0.03 * wave(t, 0.6)), 0)
a.T("bubB", 0, (0.025 * wave(t, 0.8, 0.3)), 0)
a.S("bubA", (1 + (0.04 * wave(t, 0.9))))
a.R("body", 0, 0, (0.03 * wave(t, 0.3)))
for i = 1, 4 do
a.R((("l" .. i) .. "L"), 0, 0, (0.08 * pulse(t, 4.8, 0.3, (i * 0.2))))
a.R((("l" .. i) .. "R"), 0, 0, ((-0.08) * pulse(t, 5.6, 0.3, (i * 0.2))))
end
end
self.move = function(t, a)
local f = 3.6
a.blink(t)
a.T("body", 0, (0.03 * wave(t, (f * 2))), 0)
a.R("body", 0, 0, ((-0.06) + (0.03 * wave(t, f))))
for i = 1, 4 do
local ph = ((t * f) + iff(truthy((i % 2)), 0, 0.5))
for _, s in ipairs({1, (-1)}) do
local n = (("l" .. i) .. iff((s > 0), "L", "R"))
local c = cos((TAU * (ph + iff((s > 0), 0, 0.5))))
local sn = sin((TAU * (ph + iff((s > 0), 0, 0.5))))
a.R(n, 0, 0, (((-0.4) * sn) + ((s * 0.3) * max(0, c))))
a.R((n .. "2"), 0, 0, (0.35 * sn))
end
end
a.R("stalkL", 0, 0, (0.12 + (0.08 * wave(t, f))))
a.R("stalkR", 0, 0, (0.12 + (0.08 * wave(t, f, 0.2))))
a.R("clawL", 0, 0, (0.1 * wave(t, f, 0.3)))
a.R("pinL", 0, 0, ((-0.3) * pulse(t, 0.8, 0.3)))
a.T("bubA", 0, (0.03 * wave(t, f, 0.5)), 0)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
local sn = ((1 + sin((u * 50))) * 0.5)
a.R("clawL", 0, 0, (0.3 * e))
a.R("clawL2", 0, 0, ((-0.3) * e))
a.R("pinL", 0, 0, (((-0.7) * e) * sn))
a.R("clawR", 0, 0, ((-1.3) * e))
a.R("clawR2", 0, 0, (0.6 * e))
a.R("pinR", 0, 0, ((0.8 * e) * sn))
a.T("stalkL", 0, (0.1 * e), 0)
a.T("stalkR", 0, (0.1 * e), 0)
a.S("eyeL", (1 + (0.25 * e)))
a.S("eyeR", (1 + (0.25 * e)))
a.T("body", 0, (0.14 * e), 0)
a.S("bubA", (1 + (0.3 * e)))
a.brows((0.03 * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, (-0.1), 0.3, 0.42, 0.46, 0.36, 0.6, 0.7, 0.74, 0, 1, 0), kf(u, 0, 0.44, 0.44, 0.5, 0.6, 1.02, 0.72, 1, 1, 1))
local pk = bump(u, 0.02, 0.46)
a.R("clawL", 0, 0, (0.2 * pk))
a.R("pinL", 0, 0, ((((-0.7) * pk) * (1 + sin((u * 70)))) * 0.5))
a.T("stalkL", 0, (0.14 * pk), 0)
a.T("stalkR", 0, (0.14 * pk), 0)
a.R("stalkL", 0, 0, ((0.4 * pk) * wave(u, 4)))
a.R("stalkR", 0, 0, ((0.4 * pk) * wave(u, 4, 0.2)))
a.T("root", kf(u, 0, 0, 0.46, 0, 0.6, 0.7, 0.76, 0, 1, 0), 0, 0)
local w = bump(u, 0.44, 0.8)
for i = 1, 4 do
for _, s in ipairs({1, (-1)}) do
local n = (("l" .. i) .. iff((s > 0), "L", "R"))
local ph = (((u * 14) + iff(truthy((i % 2)), 0, 0.5)) + iff((s > 0), 0, 0.5))
a.R(n, 0, 0, (w * (((-0.4) * sin((TAU * ph))) + ((s * 0.3) * max(0, cos((TAU * ph)))))))
end
end
L.squash(a, u, 0.74, 0.88, 0.16)
a.S("bubA", kf(u, 0, 0.01, 0.8, 0.01, 0.93, 1.3, 1, 1))
a.S("bubB", kf(u, 0, 0.01, 0.84, 0.01, 0.96, 1.3, 1, 1))
a.S("bubC", kf(u, 0, 0.01, 0.86, 0.01, 0.98, 1.3, 1, 1))
a.R("clawR", 0, 0, ((-0.8) * bump(u, 0.84, 1)))
end
register("bubble_crab", {
	name = "ÐŸÑƒÐ·Ñ‹Ñ€ÑŒÐºÐ¾Ð²Ñ‹Ð¹ ÐºÑ€Ð°Ð±Ð¸Ðº", hd = 2.9, rd = 1.2, mv = { sp = 1.5, rad = 1.3, side = true },
	joints = { "root", "body", "bubA", "bubB", "bubC", "stalkL", "eyeL", "browL", "l1L", "l1L2", "l2L", "l2L2", "l3L", "l3L2", "l4L", "l4L2", "stalkR", "eyeR", "browR", "l1R", "l1R2", "l2R", "l2R2", "l3R", "l3R2", "l4R", "l4R2", "clawL", "clawL2", "pinL", "clawR", "clawR2", "pinR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.52, 0, 0, 0, 0 },
		bubA = { 0.3, 0.56, 0.08, 0, 0, 0 },
		bubB = { -0.22, 0.5, 0.2, 0, 0, 0 },
		bubC = { 0.62, 0.2, 0.3, 0, 0, 0 },
		stalkL = { 0.2, 0, 0.52, 0, 0, 0 },
		eyeL = { 0, 0.36, 0.04, 0, 0, 0 },
		browL = { 0, 0.53, 0.08, -0.2, 0, -0.2 },
		l1L = { 0.6, -0.12, 0.38, 0, 0.45, 0 },
		l1L2 = { 0.46, -0.06, 0, 0, 0, 0 },
		l2L = { 0.6, -0.12, 0.14, 0, 0.15, 0 },
		l2L2 = { 0.46, -0.06, 0, 0, 0, 0 },
		l3L = { 0.6, -0.12, -0.12, 0, -0.15, 0 },
		l3L2 = { 0.46, -0.06, 0, 0, 0, 0 },
		l4L = { 0.6, -0.12, -0.36, 0, -0.45, 0 },
		l4L2 = { 0.46, -0.06, 0, 0, 0, 0 },
		stalkR = { -0.2, 0, 0.52, 0, 0, 0 },
		eyeR = { 0, 0.36, 0.04, 0, 0, 0 },
		browR = { 0, 0.53, 0.08, -0.2, 0, 0.2 },
		l1R = { -0.6, -0.12, 0.38, 0, -0.45, 0 },
		l1R2 = { -0.46, -0.06, 0, 0, 0, 0 },
		l2R = { -0.6, -0.12, 0.14, 0, -0.15, 0 },
		l2R2 = { -0.46, -0.06, 0, 0, 0, 0 },
		l3R = { -0.6, -0.12, -0.12, 0, 0.15, 0 },
		l3R2 = { -0.46, -0.06, 0, 0, 0, 0 },
		l4R = { -0.6, -0.12, -0.36, 0, 0.45, 0 },
		l4R2 = { -0.46, -0.06, 0, 0, 0, 0 },
		clawL = { 0.62, 0.02, 0.3, 0, 0, -0.2 },
		clawL2 = { 0.04, 0.36, 0, 0, 0, 0.5 },
		pinL = { -0.14, 0.34, 0, 0, 0, 0.5 },
		clawR = { -0.56, -0.1, 0.44, 0, 0, 0.9 },
		clawR2 = { 0, 0.22, 0, 0, 0, -1.3 },
		pinR = { 0.08, 0.12, 0, 0, 0, -0.5 }
	},
}, self)
end

-- ============ coral_turtle — ÐšÐ¾Ñ€Ð°Ð»Ð»Ð¾Ð²Ð°Ñ Ñ‡ÐµÑ€ÐµÐ¿Ð°ÑˆÐºÐ° ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.6, hn = "neck", look = 0.6})
a.R("neck", ((-0.1) * pulse(t, 5, 2)), 0, 0)
a.R("head", (0.08 * wave(t, 0.2)), 0, (0.1 * pulse(t, 6.4, 2, 1)))
a.S("shell", (1 + (0.012 * wave(t, 0.42))))
a.R("flL", 0, (0.12 * pulse(t, 3.9, 0.7)), (0.12 * pulse(t, 3.9, 0.7)))
a.R("flR", 0, ((-0.1) * pulse(t, 5.1, 0.7, 2)), ((-0.12) * pulse(t, 5.1, 0.7, 2)))
a.R("tail", 0, ((0.4 * pulse(t, 3.3, 0.5)) * wave(t, 4)), 0)
end
self.move = function(t, a)
local f = 0.85
local p = ((t * f) % 1)
a.blink(t)
a.T("root", 0, (0.55 + (0.1 * wave(t, f, 0.2))), 0)
a.R("body", ((-0.12) + (0.1 * wave(t, f, 0.1))), 0, (0.05 * wave(t, (f / 2))))
local st = kf(p, 0, 0, 0.35, 1, 0.55, 0.2, 1, 0)
local sw = kf(p, 0, 0.5, 0.3, (-0.2), 0.6, (-0.5), 1, 0.5)
a.R("flL", 0, sw, ((0.9 * st) - 0.3))
a.R("flR", 0, (-sw), (((-0.9) * st) + 0.3))
a.R("blL", 0, (0.2 * wave(t, (f * 2))), (0.3 * wave(t, (f * 2), 0.25)))
a.R("blR", 0, ((-0.2) * wave(t, (f * 2), 0.5)), ((-0.3) * wave(t, (f * 2), 0.75)))
a.R("neck", (0.25 - (0.1 * wave(t, f, 0.3))), 0, 0)
a.R("head", (-0.15), 0, 0)
a.R("tail", 0, (0.3 * wave(t, (f * 2))), 0)
end
self.react = function(u, a)
local c = (ss(0, 0.18, u) * (1 - ss(0.6, 0.78, u)))
local pop = bump(u, 0.62, 0.98)
a.S("neck", (1 - (0.75 * c)), (1 - (0.9 * c)), (1 - (0.75 * c)))
a.T("neck", 0, ((-0.02) * c), ((-0.3) * c))
forEach({"flL", "flR", "blL", "blR"}, function(n)
return a.S(n, (1 - (0.82 * c)))
end)
a.S("tail", (1 - (0.9 * c)))
a.T("body", 0, ((-0.1) * c), 0)
a.R("body", 0, (((0.5 * c) * sin((u * 30))) * (1 - u)), 0)
a.R("neck", ((-0.3) * pop), 0, 0)
a.brows((0.03 * pop))
a.S("shell", (1 + (0.06 * pop)))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.1, 0.3, 0.4, 0.48, 0.9, 0.66, 1.25, 0.84, 0, 1, 0), kf(u, 0, 0.42, 0.4, 0.5, 0.56, 1.02, 0.7, 1, 1, 1))
local pd = bump(u, 0.05, 0.84)
local p = ((u * 7) % 1)
local st = kf(p, 0, 0, 0.35, 1, 0.55, 0.2, 1, 0)
a.R("flL", 0, ((0.4 * pd) * wave(u, 7)), (pd * ((0.9 * st) - 0.2)))
a.R("flR", 0, (((-0.4) * pd) * wave(u, 7)), ((-pd) * ((0.9 * st) - 0.2)))
a.R("blL", 0, 0, ((0.4 * pd) * wave(u, 14)))
a.R("blR", 0, 0, (((-0.4) * pd) * wave(u, 14, 0.5)))
a.R("root", (((-0.5) * bump(u, 0.26, 0.6)) + (0.3 * bump(u, 0.6, 0.84))), (TAU * ss(0.4, 0.84, u)), 0)
local nk = (1 - ss(0.02, 0.3, u))
a.S("neck", (1 - (0.7 * nk)), (1 - (0.85 * nk)), (1 - (0.7 * nk)))
a.T("neck", 0, 0, ((-0.28) * nk))
L.squash(a, u, 0.82, 0.94, 0.12)
a.R("neck", ((-0.2) * bump(u, 0.86, 1)), 0, 0)
a.R("tail", 0, ((0.5 * bump(u, 0.86, 1)) * wave(u, 14)), 0)
end
register("coral_turtle", {
	name = "ÐšÐ¾Ñ€Ð°Ð»Ð»Ð¾Ð²Ð°Ñ Ñ‡ÐµÑ€ÐµÐ¿Ð°ÑˆÐºÐ°", hd = 3.2, rd = 1.5, mv = { sp = 1.2, rad = 1.3, side = false },
	joints = { "root", "body", "shell", "co1", "co2", "co3", "neck", "head", "eyeL", "browL", "eyeR", "browR", "flL", "blL", "flR", "blR", "tail" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.42, -0.05, 0, 0, 0 },
		shell = { 0, 0, 0, 0, 0, 0 },
		co1 = { 0.38, 0.36, 0.1, 0, 0, -0.4 },
		co2 = { 0.14, 0.38, -0.42, -0.4, 0, 0 },
		co3 = { -0.1, 0.42, 0.12, 0, 0, 0.3 },
		neck = { 0, 0.02, 0.72, 0.5, 0, 0 },
		head = { 0, 0.36, 0.04, -0.5, 0, 0 },
		eyeL = { 0.17, 0.08, 0.32, 0, 0.45, 0 },
		browL = { 0.17, 0.28, 0.27, -0.25, 0.45, -0.2 },
		eyeR = { -0.17, 0.08, 0.32, 0, -0.45, 0 },
		browR = { -0.17, 0.28, 0.27, -0.25, -0.45, 0.2 },
		flL = { 0.56, -0.1, 0.42, 0, -1.05, -0.12 },
		blL = { 0.5, -0.1, -0.5, 0, -2.3, -0.1 },
		flR = { -0.56, -0.1, 0.42, 0, 1.05, 0.12 },
		blR = { -0.5, -0.1, -0.5, 0, 2.3, 0.1 },
		tail = { 0, -0.06, -0.84, 0, 0, 0 }
	},
}, self)
end

-- ============ pearl_axolotl — Ð–ÐµÐ¼Ñ‡ÑƒÐ¶Ð½Ñ‹Ð¹ Ð°ÐºÑÐ¾Ð»Ð¾Ñ‚Ð»ÑŒ ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.2, look = 0.6})
for i = 1, 3 do
for _, s in ipairs({1, (-1)}) do
local n = (("g" .. i) .. iff((s > 0), "L", "R"))
a.R(n, (0.1 * wave(t, 0.5, (i * 0.18))), 0, ((s * 0.1) * wave(t, 0.42, (i * 0.2))))
a.R((n .. "2"), (0.12 * wave(t, 0.5, ((i * 0.18) - 0.2))), 0, ((s * 0.18) * wave(t, 0.42, ((i * 0.2) - 0.2))))
end
end
a.chain("t", 4, t, 0.35, 0, 0.16, 0, 0.16, 0.3)
a.R("head", 0, 0, (0.12 * pulse(t, 5.7, 2.2, 1)))
a.R("flL", (0.1 * pulse(t, 4.4, 0.5)))
a.T("body", 0, (0.012 * wave(t, 0.42)), 0)
end
self.move = function(t, a)
local f = 1.4
a.blink(t)
a.R("body", 0, (0.14 * wave(t, f)), (0.03 * wave(t, f)))
a.R("head", 0, ((-0.16) * wave(t, f, 0.05)), 0)
a.T("body", 0, (0.04 + (0.03 * wave(t, (f * 2)))), 0)
L.step(a, "flL", (t * f), 0.6, 0.08)
L.step(a, "blR", ((t * f) + 0.05), 0.6, 0.08)
L.step(a, "flR", ((t * f) + 0.5), 0.6, 0.08)
L.step(a, "blL", ((t * f) + 0.55), 0.6, 0.08)
a.chain("t", 4, t, f, 0, 0.3, 0, 0.18, 0.25)
for i = 1, 3 do
for _, s in ipairs({1, (-1)}) do
local n = (("g" .. i) .. iff((s > 0), "L", "R"))
a.R(n, (0.3 + (0.1 * wave(t, (f * 2), (i * 0.1)))), 0, 0)
a.R((n .. "2"), (0.2 * wave(t, (f * 2), ((i * 0.1) - 0.2))), 0, 0)
end
end
end
self.react = function(u, a)
local e = bump(u, 0, 1)
for i = 1, 3 do
for _, s in ipairs({1, (-1)}) do
local n = (("g" .. i) .. iff((s > 0), "L", "R"))
a.R(n, ((-0.2) * e), 0, ((((-s) * 0.25) * e) + (((s * 0.08) * e) * sin(((u * 40) + i)))))
a.S(n, (1 + (0.25 * e)))
end
end
a.R("body", 0, 0, ((0.12 * e) * sin((u * 26))))
a.T("root", 0, (0.2 * bump(u, 0.1, 0.7)), 0)
a.R("head", ((-0.2) * e), 0, 0)
a.brows((0.03 * e))
a.chain("t", 4, (u * 4), 1, 0, (0.3 * e), 0, 0.15, 0.2)
a.S("eyeL", 1, (1 - (0.5 * bump(u, 0.3, 0.8))), 1)
a.S("eyeR", 1, (1 - (0.5 * bump(u, 0.3, 0.8))), 1)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.05, 0.32, 0.4, 0.5, 1.0, 0.68, 0.9, 0.84, 0, 1, 0), kf(u, 0, 0.42, 0.4, 0.5, 0.56, 1.02, 0.7, 1, 1, 1))
local w = bump(u, 0.05, 0.86)
a.R("body", 0, ((0.3 * w) * wave(u, 6)), 0)
a.R("head", ((-0.3) * bump(u, 0.1, 0.5)), (((-0.3) * w) * wave(u, 6, 0.05)), 0)
a.chain("t", 4, (u * 6), 1, 0, (0.5 * w), 0, 0.18, 0.25)
a.R("root", (((-0.6) * bump(u, 0.2, 0.52)) + (0.2 * bump(u, 0.6, 0.84))), 0, 0)
for i = 1, 3 do
for _, s in ipairs({1, (-1)}) do
local n = (("g" .. i) .. iff((s > 0), "L", "R"))
local k = kf(u, 0, 0.25, (0.5 + (i * 0.06)), 0.25, (0.62 + (i * 0.06)), 1.25, (0.76 + (i * 0.06)), 1)
a.S(n, k)
a.R(n, (0.5 * (1 - ss(0.5, (0.7 + (i * 0.06)), u))), 0, 0)
end
end
forEach({"flL", "flR", "blL", "blR"}, function(n, i)
return a.R(n, ((0.6 * w) * wave(u, 8, (i * 0.25))), 0, 0)
end)
L.squash(a, u, 0.82, 0.94, 0.14)
end
register("pearl_axolotl", {
	name = "Ð–ÐµÐ¼Ñ‡ÑƒÐ¶Ð½Ñ‹Ð¹ Ð°ÐºÑÐ¾Ð»Ð¾Ñ‚Ð»ÑŒ", hd = 3.2, rd = 1.4, mv = { sp = 1.1, rad = 1.3, side = false },
	joints = { "root", "body", "flL", "blL", "flR", "blR", "t1", "t2", "t3", "t4", "head", "eyeL", "browL", "eyeR", "browR", "g1L", "g1L2", "g2L", "g2L2", "g3L", "g3L2", "g1R", "g1R2", "g2R", "g2R2", "g3R", "g3R2" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.44, -0.12, 0, 0, 0 },
		flL = { 0.42, -0.16, 0.42, 0, 0, 0.35 },
		blL = { 0.42, -0.16, -0.44, 0, 0, 0.35 },
		flR = { -0.42, -0.16, 0.42, 0, 0, -0.35 },
		blR = { -0.42, -0.16, -0.44, 0, 0, -0.35 },
		t1 = { 0, 0.04, -0.66, 0.2, 0, 0 },
		t2 = { 0, 0, -0.3, 0.12, 0, 0 },
		t3 = { 0, 0, -0.3, 0.1, 0, 0 },
		t4 = { 0, 0, -0.3, 0.1, 0, 0 },
		head = { 0, 0.08, 0.76, 0, 0, 0 },
		eyeL = { 0.3, 0.07, 0.36, 0, 0.5, 0 },
		browL = { 0.3, 0.27, 0.32, -0.25, 0.5, -0.2 },
		eyeR = { -0.3, 0.07, 0.36, 0, -0.5, 0 },
		browR = { -0.3, 0.27, 0.32, -0.25, -0.5, 0.2 },
		g1L = { 0.52, 0.12, -0.04, 0, 0, -0.45 },
		g1L2 = { 0, 0.44, 0, 0, 0, 0.3 },
		g2L = { 0.52, 0, -0.02, 0, 0, -1 },
		g2L2 = { 0, 0.44, 0, 0, 0, 0.3 },
		g3L = { 0.52, -0.12, 0, 0, 0, -1.55 },
		g3L2 = { 0, 0.44, 0, 0, 0, 0.3 },
		g1R = { -0.52, 0.12, -0.04, 0, 0, 0.45 },
		g1R2 = { 0, 0.44, 0, 0, 0, -0.3 },
		g2R = { -0.52, 0, -0.02, 0, 0, 1 },
		g2R2 = { 0, 0.44, 0, 0, 0, -0.3 },
		g3R = { -0.52, -0.12, 0, 0, 0, 1.55 },
		g3R2 = { 0, 0.44, 0, 0, 0, -0.3 }
	},
}, self)
end

-- ============ tide_ray — ÐŸÑ€Ð¸Ð»Ð¸Ð²Ð½Ñ‹Ð¹ ÑÐºÐ°Ñ‚Ð¸Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.9, head = 0})
a.T("root", 0, (0.06 * wave(t, 0.3)), 0)
a.R("body", (0.04 * wave(t, 0.3, 0.2)), (0.1 * wave(t, 0.1)), (0.03 * wave(t, 0.2)))
a.R("wingL", 0, 0, (0.16 * wave(t, 0.42)))
a.R("wingL2", 0, 0, (0.3 * wave(t, 0.42, (-0.2))))
a.R("wingR", 0, 0, ((-0.16) * wave(t, 0.42)))
a.R("wingR2", 0, 0, ((-0.3) * wave(t, 0.42, (-0.2))))
a.chain("t", 4, t, 0.3, 0.06, 0.12, 0, 0.16, 0.3)
a.R("lobeL", 0, (0.2 * wave(t, 0.6)), 0)
a.R("lobeR", 0, ((-0.2) * wave(t, 0.6, 0.3)), 0)
a.S("pearl", (1 + (0.03 * wave(t, 0.6))))
end
self.move = function(t, a)
local f = 0.95
a.blink(t)
a.T("root", 0, (0.12 * wave(t, f, 0.3)), 0)
a.R("body", ((-0.14) + (0.08 * wave(t, f, 0.1))), 0, (-0.16))
a.R("wingL", 0, 0, (0.5 * wave(t, f)))
a.R("wingL2", 0, 0, (0.7 * wave(t, f, (-0.18))))
a.R("wingR", 0, 0, ((-0.5) * wave(t, f)))
a.R("wingR2", 0, 0, ((-0.7) * wave(t, f, (-0.18))))
a.chain("t", 4, t, f, 0.14, 0.08, 0, 0.18, 0.25)
a.R("lobeL", (0.2 * wave(t, f)))
a.R("lobeR", (0.2 * wave(t, f)))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("root", 0, 0, (TAU * ss(0.1, 0.85, u)))
a.T("root", 0, (0.25 * e), 0)
a.R("wingL", 0, 0, ((-0.4) * e))
a.R("wingR", 0, 0, (0.4 * e))
a.R("wingL2", 0, 0, ((-0.5) * e))
a.R("wingR2", 0, 0, (0.5 * e))
a.brows((0.03 * e))
a.chain("t", 4, (u * 3), 1, (0.2 * e), 0, 0, 0.15, 0.2)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, (-0.7), 0.34, 0.1, 0.56, 0.75, 0.78, 0.2, 0.9, (-0.06), 1, 0), kf(u, 0, 0.42, 0.3, 0.5, 0.52, 1.02, 0.66, 1, 1, 1))
a.R("root", (kf(u, 0, (-1.45), 0.34, (-1.45), 0.52, (-0.9), 0.66, (TAU - 1.2), 0.8, (TAU - 0.2), 0.9, TAU, 1, TAU) + 0), 0, 0)
local f = kf(u, 0, (-0.9), 0.3, (-0.9), 0.44, 0.5, 0.56, (-0.6), 0.68, 0.5, 0.8, (-0.3), 0.9, 0.2, 1, 0)
a.R("wingL", 0, 0, f)
a.R("wingL2", 0, 0, (f * 1.3))
a.R("wingR", 0, 0, (-f))
a.R("wingR2", 0, 0, ((-f) * 1.3))
a.chain("t", 4, (u * 6), 1, (0.3 * bump(u, 0.2, 1)), 0, 0, 0.18, 0.2)
a.R("lobeL", 0, ((0.4 * bump(u, 0, 0.34)) * wave(u, 9)), 0)
a.R("lobeR", 0, (((-0.4) * bump(u, 0, 0.34)) * wave(u, 9)), 0)
end
register("tide_ray", {
	name = "ÐŸÑ€Ð¸Ð»Ð¸Ð²Ð½Ñ‹Ð¹ ÑÐºÐ°Ñ‚Ð¸Ðº", hd = 3.4, rd = 1.6, mv = { sp = 1.5, rad = 1.35, side = false },
	joints = { "root", "body", "pearl", "head", "eyeL", "browL", "eyeR", "browR", "lobeL", "lobeR", "wingL", "wingL2", "wingR", "wingR2", "t1", "t2", "t3", "t4", "tip" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.95, 0, 0, 0, 0 },
		pearl = { 0, 0.2, -0.1, 0, 0, 0 },
		head = { 0, 0, 0.56, 0, 0, 0 },
		eyeL = { 0.17, 0.12, 0.22, -0.45, 0.4, 0 },
		browL = { 0.17, 0.31, 0.2, -0.7, 0.4, -0.2 },
		eyeR = { -0.17, 0.12, 0.22, -0.45, -0.4, 0 },
		browR = { -0.17, 0.31, 0.2, -0.7, -0.4, 0.2 },
		lobeL = { 0.24, -0.06, 0.22, 0, 0.2, 0 },
		lobeR = { -0.24, -0.06, 0.22, 0, -0.2, 0 },
		wingL = { 0.36, 0.02, -0.02, 0, 0, 0 },
		wingL2 = { 0.74, 0, 0, 0, 0, 0 },
		wingR = { -0.36, 0.02, -0.02, 0, 0, 0 },
		wingR2 = { -0.74, 0, 0, 0, 0, 0 },
		t1 = { 0, 0, -0.56, 0.1, 0, 0 },
		t2 = { 0, 0, -0.3, 0.18, 0, 0 },
		t3 = { 0, 0, -0.3, 0.25, 0, 0 },
		t4 = { 0, 0, -0.3, 0.3, 0, 0 },
		tip = { 0, 0, -0.3, 0, 0, 0 }
	},
}, self)
end

-- ============ little_leviathan — ÐœÐ°Ð»ÐµÐ½ÑŒÐºÐ¸Ð¹ Ð»ÐµÐ²Ð¸Ð°Ñ„Ð°Ð½ ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.5, body = "s3", look = 0.5})
for i = 1, 7 do
a.R(("s" .. i), (0.07 * wave(t, 0.3, ((-i) * 0.14))), 0, (0.05 * wave(t, 0.22, ((-i) * 0.12))))
end
a.R("head", ((-0.1) * wave(t, 0.3, (-1.1))), 0, 0)
a.R("earL", 0, (0.3 * wave(t, 0.5)), 0)
a.R("earR", 0, ((-0.3) * wave(t, 0.5, 0.2)), 0)
a.R("finL", 0, 0, (0.25 * wave(t, 0.6)))
a.R("finR", 0, 0, ((-0.25) * wave(t, 0.6, 0.3)))
a.chain("t", 3, t, 0.3, 0, 0.15, 0, 0.2, 0.3)
a.R("fluke", 0, (0.3 * wave(t, 0.3, (-0.6))), 0)
end
self.move = function(t, a)
local f = 1.1
a.blink(t)
for i = 1, 7 do
a.R(("s" .. i), (0.06 * wave(t, f, ((-i) * 0.15))), 0, (0.2 * wave(t, f, ((-i) * 0.16))))
end
a.R("s1", 0.5, 0, 0)
a.R("s3", (-0.3), 0, 0)
a.R("s5", 0.3, 0, 0)
a.R("head", (-0.3), 0, ((-0.15) * wave(t, f, (-1.2))))
a.T("root", 0, (0.1 + (0.05 * wave(t, (f * 2)))), 0)
a.chain("t", 3, t, f, 0, 0.3, 0, 0.2, 0.3)
a.R("fluke", 0, (0.5 * wave(t, f, (-0.7))), 0)
a.R("earL", 0, (-0.4), 0)
a.R("earR", 0, 0.4, 0)
a.R("finL", 0, 0, (0.5 * wave(t, (f * 2))))
a.R("finR", 0, 0, ((-0.5) * wave(t, (f * 2))))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("s2", ((-0.3) * e))
a.R("s4", ((-0.3) * e))
a.R("s5", (0.4 * e))
a.R("s6", (0.3 * e))
a.R("head", ((-0.2) * e), 0, 0)
a.S("earL", (1 + (0.3 * e)))
a.S("earR", (1 + (0.3 * e)))
a.R("earL", 0, (0.5 * e), ((-0.2) * e))
a.R("earR", 0, ((-0.5) * e), (0.2 * e))
a.R("finL", 0, 0, ((-0.6) * e))
a.R("finR", 0, 0, (0.6 * e))
a.R("nose", (0.25 * e))
a.brows(((-0.02) * e), (0.25 * e))
a.R("fluke", 0, ((0.6 * e) * wave(u, 5)), 0)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, (-1.3), 0.2, (-0.9), 0.56, 0.25, 0.72, 0.1, 0.86, 0, 1, 0), kf(u, 0, 0.6, 0.3, 0.7, 0.56, 1.03, 0.72, 1, 1, 1))
local c = (1 - ss(0.2, 0.62, u))
a.R("s2", ((-0.7) * c))
a.R("s3", ((-0.8) * c))
a.R("s4", ((-0.4) * c))
a.R("s5", (0.8 * c))
a.R("s6", (0.6 * c))
a.R("head", (0.2 * c), 0, 0)
local sw = bump(u, 0.1, 0.9)
for i = 1, 7 do
a.R(("s" .. i), 0, 0, ((0.16 * sw) * sin(((u * 20) - (i * 0.9)))))
end
a.R("head", 0, ((0.5 * bump(u, 0.3, 0.7)) * wave(u, 2.5)), (((-0.1) * sw) * sin(((u * 20) - 7))))
local fl = kf(u, 0, 0.2, 0.6, 0.2, 0.76, 1.35, 0.9, 1, 1, 1)
a.S("earL", fl)
a.S("earR", fl)
a.S("finL", fl)
a.S("finR", fl)
a.R("earL", 0, ((0.5 * bump(u, 0.7, 1)) * wave(u, 10)), 0)
a.R("earR", 0, (((-0.5) * bump(u, 0.7, 1)) * wave(u, 10)), 0)
a.chain("t", 3, (u * 5), 1, 0, (0.4 * sw), 0, 0.2, 0.2)
a.R("nose", (0.25 * bump(u, 0.84, 1)))
a.brows(((-0.02) * bump(u, 0.84, 1)), (0.2 * bump(u, 0.84, 1)))
end
register("little_leviathan", {
	name = "ÐœÐ°Ð»ÐµÐ½ÑŒÐºÐ¸Ð¹ Ð»ÐµÐ²Ð¸Ð°Ñ„Ð°Ð½", hd = 4.2, rd = 1.6, mv = { sp = 1.2, rad = 1.3, side = false },
	joints = { "root", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "finL", "finR", "t1", "t2", "t3", "fluke", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		s1 = { 0, 0.3, 0.2, -1.3, 0, 0 },
		s2 = { 0, 0.34, 0, 0.9, 0, 0 },
		s3 = { 0, 0.36, 0, 0.9, 0, 0 },
		s4 = { 0, 0.36, 0, 0.5, 0, 0 },
		s5 = { 0, 0.34, 0, -0.9, 0, 0 },
		s6 = { 0, 0.34, 0, -0.7, 0, 0 },
		s7 = { 0, 0.32, 0, 0.5, 0, 0 },
		finL = { 0.22, 0.2, 0.05, 0, 0.3, -1.2 },
		finR = { -0.22, 0.2, 0.05, 0, -0.3, 1.2 },
		t1 = { 0, 0.26, 0.3, -0.15, 3.141592654, 0 },
		t2 = { 0, 0, -0.34, -0.1, 0.5, 0 },
		t3 = { 0, 0, -0.32, 0, 0.5, 0 },
		fluke = { 0, 0, -0.3, 0, 0, 0 },
		head = { 0, 0.36, 0.06, 0.2, 0, 0 },
		eyeL = { 0.22, 0.06, 0.36, 0, 0.5, 0 },
		browL = { 0.22, 0.27, 0.31, -0.25, 0.5, -0.3 },
		eyeR = { -0.22, 0.06, 0.36, 0, -0.5, 0 },
		browR = { -0.22, 0.27, 0.31, -0.25, -0.5, 0.3 },
		nose = { 0, -0.1, 0.36, 0, 0, 0 },
		earL = { 0.38, 0.06, -0.06, 0, 0.5, -1.1 },
		earR = { -0.38, 0.06, -0.06, 0, -0.5, 1.1 }
	},
}, self)
end

-- ============ spark_salamander — Ð˜ÑÐºÑ€Ð¾Ð²Ð°Ñ ÑÐ°Ð»Ð°Ð¼Ð°Ð½Ð´Ñ€Ð° ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.3, look = 0.8})
local z = pulse(t, 2.7, 0.3)
a.R("tip", 0, ((0.6 * z) * sin((t * 60))), ((0.4 * z) * sin((t * 47))))
for i = 1, 3 do
a.S(("sp" .. i), ((1 + (0.08 * wave(t, 0.9, (i * 0.2)))) + (0.3 * pulse(t, 2.7, 0.25, ((-i) * 0.06)))))
end
a.chain("t", 6, t, 0.4, 0, 0.13, 0, 0.14, 0.2)
a.R("head", 0, 0, (0.2 * pulse(t, 5, 1.6, 2)))
a.R("flL", 0, 0, (0.25 * pulse(t, 6.2, 0.4)))
a.T("body", 0, (0.01 * wave(t, 0.42)), 0)
end
self.move = function(t, a)
local f = 2.8
a.blink(t)
a.R("body", 0, (0.24 * wave(t, f)), (0.05 * wave(t, f)))
a.R("head", 0, ((-0.3) * wave(t, f, 0.06)), 0)
forEach({{"flL", 1, 0}, {"blR", (-1), 0.04}, {"flR", (-1), 0.5}, {"blL", 1, 0.54}}, function(q)
return L.sideStep(a, q[1], q[2], ((t * f) + q[3]), 0.7, 0.35, 0.3)
end)
a.chain("t", 6, t, f, 0, 0.26, 0, 0.15, 0.15)
for i = 1, 3 do
a.S(("sp" .. i), (1 + (0.15 * wave(t, (f * 2), (i * 0.2)))))
end
end
self.react = function(u, a)
local e = bump(u, 0, 1)
local j = sin((u * 90))
a.T("root", 0, (0.5 * bump(u, 0.08, 0.6)), 0)
a.R("body", ((-0.5) * bump(u, 0.08, 0.5)), 0, ((0.04 * e) * j))
for i = 1, 3 do
a.S(("sp" .. i), (1 + (0.9 * e)))
end
a.R("tip", 0, ((0.5 * e) * j), 0)
forEach({"flL", "blL"}, function(n)
return a.R(n, 0, 0, (0.6 * e))
end)
forEach({"flR", "blR"}, function(n)
return a.R(n, 0, 0, ((-0.6) * e))
end)
a.chain("t", 6, (u * 5), 1, (0.2 * e), 0, 0, 0.15, 0.1)
a.brows((0.04 * e))
a.S("eyeL", (1 + (0.15 * e)))
a.S("eyeR", (1 + (0.15 * e)))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.3, 0.24, 0.42, 0.34, 0.5, 0.44, 0.05, 1, 0), kf(u, 0, 0.5, 0.24, 0.56, 0.36, 1.04, 0.46, 1, 1, 1))
local pk = bump(u, 0, 0.28)
a.R("head", ((-0.3) * pk), ((0.6 * pk) * wave(u, 7)), 0)
local run = bump(u, 0.3, 0.8)
a.T("root", ((1.0 * sin((TAU * ss(0.3, 0.78, u)))) * 1), 0, ((0.9 * (cos((TAU * ss(0.3, 0.78, u))) - 1)) * 0.5))
a.R("root", 0, ((TAU * ss(0.3, 0.78, u)) + (((PI / 2) * bump(u, 0.3, 0.78)) * 0.0)), 0)
a.R("body", 0, ((0.3 * run) * wave(u, 16)), 0)
a.R("head", 0, (((-0.3) * run) * wave(u, 16, 0.06)), 0)
forEach({{"flL", 1, 0}, {"blR", (-1), 0.04}, {"flR", (-1), 0.5}, {"blL", 1, 0.54}}, function(q)
return L.sideStep(a, q[1], q[2], ((u * 16) + q[3]), (0.7 * run), 0.35, 0.3)
end)
a.chain("t", 6, (u * 16), 1, 0, (0.3 * run), 0, 0.15, 0.15)
local sk = bump(u, 0.78, 0.92)
a.R("body", 0, (0.4 * sk), 0)
a.S("root", (1 + (0.1 * sk)), (1 - (0.1 * sk)), (1 + (0.1 * sk)))
for i = 1, 3 do
a.S(("sp" .. i), (1 + (0.8 * bump(u, (0.84 + (i * 0.02)), 1))))
end
a.R("tip", 0, ((0.6 * bump(u, 0.84, 1)) * sin((u * 200))), 0)
end
register("spark_salamander", {
	name = "Ð˜ÑÐºÑ€Ð¾Ð²Ð°Ñ ÑÐ°Ð»Ð°Ð¼Ð°Ð½Ð´Ñ€Ð°", hd = 2.8, rd = 1.1, mv = { sp = 2, rad = 1.3, side = false },
	joints = { "root", "body", "sp1", "sp2", "sp3", "flL", "flL2", "blL", "blL2", "flR", "flR2", "blR", "blR2", "t1", "t2", "t3", "t4", "t5", "t6", "tip", "head", "eyeL", "browL", "eyeR", "browR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.36, 0, 0, 0, 0 },
		sp1 = { 0, 0.22, 0.36, 0, 0, 0 },
		sp2 = { 0, 0.22, 0.02, 0, 0, 0 },
		sp3 = { 0, 0.22, -0.3, 0, 0, 0 },
		flL = { 0.3, -0.04, 0.4, 0, 0, 0 },
		flL2 = { 0.3, -0.03, 0, 0, 0, 0 },
		blL = { 0.3, -0.04, -0.42, 0, 0, 0 },
		blL2 = { 0.3, -0.03, 0, 0, 0, 0 },
		flR = { -0.3, -0.04, 0.4, 0, 0, 0 },
		flR2 = { -0.3, -0.03, 0, 0, 0, 0 },
		blR = { -0.3, -0.04, -0.42, 0, 0, 0 },
		blR2 = { -0.3, -0.03, 0, 0, 0, 0 },
		t1 = { 0, 0, -0.62, 0.05, 0, 0 },
		t2 = { 0, 0, -0.26, 0.1, 0, 0 },
		t3 = { 0, 0, -0.26, 0.2, 0, 0 },
		t4 = { 0, 0, -0.26, 0.3, 0, 0 },
		t5 = { 0, 0, -0.24, 0.35, 0, 0 },
		t6 = { 0, 0, -0.22, 0.4, 0, 0 },
		tip = { 0, 0, -0.2, 0, 0, 0 },
		head = { 0, 0.08, 0.7, 0, 0, 0 },
		eyeL = { 0.25, 0.15, 0.29, 0, 0.5, 0 },
		browL = { 0.25, 0.35, 0.26, -0.25, 0.5, -0.2 },
		eyeR = { -0.25, 0.15, 0.29, 0, -0.5, 0 },
		browR = { -0.25, 0.35, 0.26, -0.25, -0.5, 0.2 }
	},
}, self)
end

-- ============ cloud_lamb — ÐžÐ±Ð»Ð°Ñ‡Ð½Ñ‹Ð¹ Ð±Ð°Ñ€Ð°ÑˆÐµÐº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.6})
a.T("root", 0, (0.05 + (0.04 * wave(t, 0.3))), 0)
for i = 1, 8 do
a.S(("p" .. i), (1 + (0.05 * wave(t, 0.42, (i * 0.13)))))
end
a.R("earL", 0, 0, ((0.25 * pulse(t, 3.4, 0.3)) + (0.05 * wave(t, 0.3))))
a.R("earR", 0, 0, (((-0.25) * pulse(t, 4.6, 0.3, 1)) - (0.05 * wave(t, 0.3))))
a.R("tail", 0, ((0.6 * pulse(t, 2.9, 0.6)) * wave(t, 6)), 0)
forEach({"flL", "flR", "blL", "blR"}, function(n, i)
return a.R(n, (0.06 * wave(t, 0.3, (i * 0.25))))
end)
a.R("head", 0, 0, (0.14 * pulse(t, 6, 2.2, 2)))
end
self.move = function(t, a)
local p = ((t * 1.5) % 1)
a.blink(t)
a.T("root", 0, kf(p, 0, 0.02, 0.14, (-0.04), 0.5, 0.62, 0.86, 0.02, 1, 0.02), 0)
a.R("body", kf(p, 0, 0, 0.25, (-0.12), 0.7, 0.12, 1, 0))
local lg = kf(p, 0, 0, 0.14, 0.25, 0.4, (-0.5), 0.7, 0.3, 0.9, (-0.1), 1, 0)
a.R("flL", lg)
a.R("flR", lg)
a.R("blL", (-lg))
a.R("blR", (-lg))
forEach({"flL", "flR", "blL", "blR"}, function(n)
return a.R((n .. "2"), (0.6 * bump(p, 0.3, 0.8)))
end)
for i = 1, 8 do
local q = kf(p, 0, 0, 0.16, 0.1, 0.4, (-0.08), 0.86, 0.12, 1, 0)
a.S(("p" .. i), (1 + (q * 0.5)), (1 - q), (1 + (q * 0.5)))
a.T(("p" .. i), 0, (((-0.05) * bump(p, 0.2, 0.7)) + (0.04 * bump(p, 0.82, 1))), 0)
end
a.R("earL", 0, 0, (0.5 * bump(p, 0.5, 0.95)))
a.R("earR", 0, 0, ((-0.5) * bump(p, 0.5, 0.95)))
a.R("head", ((-0.15) * bump(p, 0.2, 0.7)), 0, 0)
a.R("tail", (0.5 * bump(p, 0.3, 0.8)))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
for i = 1, 8 do
a.S(("p" .. i), (1 + (0.3 * e)))
a.T(("p" .. i), 0, ((0.03 * e) * sin(((u * 30) + i))), 0)
end
a.T("root", 0, (0.3 * e), 0)
a.R("root", 0, (TAU * ss(0.15, 0.85, u)), 0)
a.R("earL", 0, 0, (0.6 * e))
a.R("earR", 0, 0, ((-0.6) * e))
a.brows((0.03 * e))
forEach({"flL", "flR"}, function(n)
return a.R(n, ((-0.4) * e))
end)
forEach({"blL", "blR"}, function(n)
return a.R(n, (0.4 * e))
end)
a.S("hornL", (1 + (0.3 * e)))
a.S("hornR", (1 + (0.3 * e)))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.1, 0.3, 0.5, 0.56, 1.35, 0.72, 1.25, 0.88, (-0.02), 0.94, 0.06, 1, 0), kf(u, 0, 0.4, 0.3, 0.5, 0.52, 1.02, 0.66, 1, 1, 1))
for i = 1, 8 do
a.S(("p" .. i), kf(u, 0, 0.5, (0.2 + (i * 0.03)), 0.5, (0.34 + (i * 0.03)), 1.3, (0.5 + (i * 0.03)), 1, 0.86, 1, 0.92, 1.18, 1, 1))
end
a.R("root", 0, (((-0.6) * bump(u, 0.2, 0.8)) * wave(u, 1.2)), ((0.1 * bump(u, 0.3, 0.8)) * wave(u, 2.5)))
local dg = bump(u, 0.24, 0.86)
forEach({"flL", "flR", "blL", "blR"}, function(n, i)
a.R(n, ((0.25 * dg) * wave(u, 5, (i * 0.25))))
a.R((n .. "2"), (0.3 * dg))
end)
a.R("earL", 0, 0, (((0.4 * dg) * (1 + wave(u, 5))) * 0.5))
a.R("earR", 0, 0, ((((-0.4) * dg) * (1 + wave(u, 5))) * 0.5))
a.R("head", (0.15 * dg), 0, 0)
L.squash(a, u, 0.86, 0.96, 0.12)
a.R("tail", 0, ((0.6 * bump(u, 0.88, 1)) * wave(u, 16)), 0)
end
register("cloud_lamb", {
	name = "ÐžÐ±Ð»Ð°Ñ‡Ð½Ñ‹Ð¹ Ð±Ð°Ñ€Ð°ÑˆÐµÐº", hd = 3.2, rd = 1.3, mv = { sp = 1.5, rad = 1.3, side = false },
	joints = { "root", "body", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "flL", "flL2", "blL", "blL2", "flR", "flR2", "blR", "blR2", "tail", "head", "eyeL", "browL", "eyeR", "browR", "nose", "tuft", "earL", "hornL", "earR", "hornR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.8, -0.05, 0, 0, 0 },
		p1 = { 0, 0.3, 0.12, 0, 0, 0 },
		p2 = { 0.3, 0.14, 0.28, 0, 0, 0 },
		p3 = { -0.3, 0.14, 0.28, 0, 0, 0 },
		p4 = { 0.34, 0.16, -0.2, 0, 0, 0 },
		p5 = { -0.34, 0.16, -0.2, 0, 0, 0 },
		p6 = { 0, 0.32, -0.3, 0, 0, 0 },
		p7 = { 0, 0.06, -0.56, 0, 0, 0 },
		p8 = { 0, -0.06, 0.5, 0, 0, 0 },
		flL = { 0.24, -0.3, 0.3, 0, 0, 0 },
		flL2 = { 0, -0.24, 0, 0, 0, 0 },
		blL = { 0.26, -0.3, -0.34, 0, 0, 0 },
		blL2 = { 0, -0.24, 0, 0, 0, 0 },
		flR = { -0.24, -0.3, 0.3, 0, 0, 0 },
		flR2 = { 0, -0.24, 0, 0, 0, 0 },
		blR = { -0.26, -0.3, -0.34, 0, 0, 0 },
		blR2 = { 0, -0.24, 0, 0, 0, 0 },
		tail = { 0, 0.12, -0.76, 0, 0, 0 },
		head = { 0, 0.2, 0.66, 0, 0, 0 },
		eyeL = { 0.1692, 0.034, 0.3492, 0, 0.4, 0 },
		browL = { 0.1692, 0.2628, 0.2892, -0.25, 0.4, -0.22 },
		eyeR = { -0.1692, 0.034, 0.3492, 0, -0.4, 0 },
		browR = { -0.1692, 0.2628, 0.2892, -0.25, -0.4, 0.22 },
		nose = { 0, -0.1, 0.33, 0, 0, 0 },
		tuft = { 0, 0.32, 0.06, 0, 0, 0 },
		earL = { 0.33, 0.06, -0.04, 0, 0, -1.9 },
		hornL = { 0.38, 0.24, -0.1, 0, 0, 0 },
		earR = { -0.33, 0.06, -0.04, 0, 0, 1.9 },
		hornR = { -0.38, 0.24, -0.1, 0, 0, 0 }
	},
}, self)
end

-- ============ storm_falcon — Ð“Ñ€Ð¾Ð·Ð¾Ð²Ð¾Ð¹ ÑÐ¾ÐºÐ¾Ð»Ñ‘Ð½Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 1.2, head = 0})
local k = math.floor((t / 1.5))
local e = ss(0, 0.1, ((t / 1.5) % 1))
local h = function(n)
return (sin((n * 78.233)) * 0.5)
end
a.R("head", (0.08 * h((k + 3))), (0.7 * (h(k) + ((h((k + 1)) - h(k)) * e))), (0.3 * (h((k + 7)) + ((h((k + 8)) - h((k + 7))) * e))))
local ru = pulse(t, 4.6, 0.9)
L.flap(a, (((-0.3) * ru) - ((0.05 * ru) * wave(t, 9))))
a.R("crest", ((0.2 * ru) + (0.04 * wave(t, 0.5))))
a.R("tail", (0.1 * wave(t, 0.4)), 0, ((0.15 * pulse(t, 3.1, 0.5)) * wave(t, 5)))
a.T("root", 0, (0.05 * pulse(t, 3.9, 0.3, 1)), 0)
end
self.move = function(t, a)
local f = 3.6
a.blink(t)
a.T("root", 0, (0.75 + (0.06 * wave(t, f, 0.3))), 0)
a.R("body", (0.75 + (0.05 * wave(t, f, 0.1))))
a.R("head", (-0.7), 0, (0.06 * wave(t, (f / 2))))
L.flap(a, ((-1.3) + (0.85 * wave(t, f))))
a.R("wingL", (0.25 * wave(t, f, 0.25)))
a.R("wingR", (0.25 * wave(t, f, 0.25)))
a.R("legL", 0.9)
a.R("legR", 0.9)
a.R("tail", (0.4 + (0.12 * wave(t, f, 0.4))), (0.1 * wave(t, (f / 2))), 0)
a.R("crest", 0.3)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
L.flap(a, (((-1.5) * e) - ((0.08 * e) * sin((u * 60)))))
a.R("head", ((-0.5) * e), 0, 0)
a.R("nose", (((0.3 * e) * (1 + sin((u * 50)))) * 0.5))
a.R("crest", ((-0.3) * e))
a.T("root", 0, (0.2 * e), 0)
a.R("tail", ((-0.4) * e))
a.brows(((-0.03) * e), (0.3 * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.2, 0.26, 0.36, 0.36, 0.26, 0.52, 1.7, 0.7, 1.5, 0.84, 0, 1, 0), kf(u, 0, 0.42, 0.36, 0.5, 0.5, 1.03, 0.64, 1, 1, 1))
local fl = (ss(0.34, 0.44, u) * (1 - ss(0.8, 0.9, u)))
L.flap(a, ((fl * ((-1.3) + (0.9 * sin((u * 150))))) - (0.4 * bump(u, 0.88, 1))))
a.R("root", ((fl * 0.25) * sin((u * 40))), 0, ((fl * 0.12) * sin((u * 33))))
a.R("body", (0.3 * fl))
a.R("head", (((-0.3) * fl) - (0.3 * bump(u, 0.05, 0.34))), ((0.5 * bump(u, 0.05, 0.34)) * wave(u, 6)), 0)
a.R("legL", ((0.6 * fl) + ((0.3 * fl) * sin((u * 60)))))
a.R("legR", ((0.6 * fl) - ((0.3 * fl) * sin((u * 60)))))
a.R("tail", (0.4 * fl))
L.squash(a, u, 0.82, 0.94, 0.18)
a.R("crest", (0.4 * bump(u, 0.86, 1)))
end
register("storm_falcon", {
	name = "Ð“Ñ€Ð¾Ð·Ð¾Ð²Ð¾Ð¹ ÑÐ¾ÐºÐ¾Ð»Ñ‘Ð½Ð¾Ðº", hd = 3.2, rd = 1.2, mv = { sp = 2, rad = 1.35, side = false },
	joints = { "root", "body", "wingL", "legL", "wingR", "legR", "tail", "head", "eyeL", "browL", "eyeR", "browR", "nose", "crest" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.66, 0, 0, 0, 0 },
		wingL = { 0.36, 0.14, -0.02, 0, 0, -2.75 },
		legL = { 0.18, -0.42, 0.04, 0, 0, 0 },
		wingR = { -0.36, 0.14, -0.02, 0, 0, 2.75 },
		legR = { -0.18, -0.42, 0.04, 0, 0, 0 },
		tail = { 0, -0.2, -0.38, -0.5, 0, 0 },
		head = { 0, 0.62, 0.08, 0, 0, 0 },
		eyeL = { 0.19, 0.05, 0.31, 0, 0.55, 0 },
		browL = { 0.19, 0.24, 0.29, -0.25, 0.55, 0.4 },
		eyeR = { -0.19, 0.05, 0.31, 0, -0.55, 0 },
		browR = { -0.19, 0.24, 0.29, -0.25, -0.55, -0.4 },
		nose = { 0, -0.06, 0.34, 0, 0, 0 },
		crest = { 0, 0.28, -0.06, 0, 0, 0 }
	},
}, self)
end

-- ============ storm_dragon — Ð¨Ñ‚Ð¾Ñ€Ð¼Ð¾Ð²Ð¾Ð¹ Ð´Ñ€Ð°ÐºÐ¾Ð½Ñ‡Ð¸Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.8, hn = "neck", look = 0.6})
a.R("head", 0, (0.2 * wave(t, 0.09)), (0.1 * pulse(t, 6, 2, 1)))
L.flap(a, ((0.08 * wave(t, 0.42)) + (0.3 * pulse(t, 5.2, 1.1))))
a.R("wingL2", ((-0.15) * pulse(t, 5.2, 1.1)))
a.R("wingR2", ((-0.15) * pulse(t, 5.2, 1.1)))
a.chain("t", 5, t, 0.33, 0.03, 0.13, 0, 0.15, 0.25)
a.R("tip", 0, ((0.5 * pulse(t, 3, 0.3)) * sin((t * 50))), 0)
a.R("earL", 0, (0.3 * pulse(t, 3.7, 0.3)), 0)
a.R("earR", 0, ((-0.3) * pulse(t, 4.9, 0.3, 1)), 0)
a.S("nose", (1 + (0.05 * pulse(t, 4.4, 0.4))))
end
self.move = function(t, a)
local f = 1.5
local w = wave(t, f)
a.blink(t)
a.T("root", 0, (0.8 + (0.12 * wave(t, f, 0.3))), 0)
a.R("body", (0.3 + (0.06 * wave(t, f, 0.15))))
a.R("neck", (0.1 - (0.06 * w)))
a.R("head", (-0.35), 0, 0)
L.flap(a, (0.6 - (0.75 * w)))
a.R("wingL2", (0.6 + (0.5 * wave(t, f, (-0.2)))))
a.R("wingR2", (0.6 + (0.5 * wave(t, f, (-0.2)))))
forEach({"flL", "flR"}, function(n)
a.R(n, 0.5)
a.R((n .. "2"), 0.9)
end)
forEach({"blL", "blR"}, function(n)
a.R(n, 0.9)
a.R((n .. "2"), (-0.5))
end)
a.chain("t", 5, t, f, 0.12, 0.06, 0, 0.17, 0.2)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("body", ((-0.4) * e))
a.T("body", 0, (0.16 * e), 0)
L.flap(a, (0.95 * e))
a.R("wingL2", (0.85 * e))
a.R("wingR2", (0.85 * e))
a.R("neck", ((-0.2) * e))
a.R("head", ((-0.3) * e), 0, 0)
a.R("nose", (0.3 * e))
a.brows(((-0.03) * e), (0.3 * e))
a.R("flL", ((-0.7) * e))
a.R("flR", ((-0.5) * e))
a.R("blL", (0.35 * e))
a.R("blR", (0.35 * e))
a.R("tip", 0, ((0.5 * e) * sin((u * 70))), 0)
a.S("hornL", (1 + (0.2 * e)))
a.S("hornR", (1 + (0.2 * e)))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.05, 0.3, 0.2, 0.44, 0.14, 0.6, 1.5, 0.72, 1.3, 0.84, 0, 1, 0), kf(u, 0, 0.42, 0.3, 0.5, 0.46, 1.03, 0.6, 1, 1, 1))
local cr = (1 - ss(0.3, 0.48, u))
forEach({"flL", "flR"}, function(n)
a.R(n, ((-0.9) * cr))
a.R((n .. "2"), (1.7 * cr))
end)
forEach({"blL", "blR"}, function(n)
a.R(n, (0.9 * cr))
a.R((n .. "2"), ((-1.6) * cr))
end)
a.T("body", 0, ((-0.36) * cr), 0)
a.R("neck", (0.5 * cr))
a.R("head", ((-0.1) * cr), ((0.4 * bump(u, 0.05, 0.3)) * wave(u, 5)), 0)
local w = kf(u, 0, (-0.45), 0.26, (-0.45), 0.46, 1.1, 0.54, (-0.2), 0.62, 1.0, 0.7, (-0.1), 0.78, 0.9, 0.86, 0.3, 1, 0)
L.flap(a, w)
local w2 = kf(u, 0, (-0.6), 0.26, (-0.6), 0.46, 0.9, 0.86, 0.6, 1, 0)
a.R("wingL2", w2)
a.R("wingR2", w2)
a.R("root", ((-0.3) * bump(u, 0.46, 0.62)), (TAU * ss(0.5, 0.8, u)), 0)
L.squash(a, u, 0.82, 0.94, 0.16)
local ro = bump(u, 0.86, 1)
a.R("head", ((-0.3) * ro), 0, 0)
a.R("nose", (0.3 * ro))
a.chain("t", 5, (u * 6), 1, (0.15 * bump(u, 0.4, 1)), 0.1, 0, 0.17, 0.2)
end
register("storm_dragon", {
	name = "Ð¨Ñ‚Ð¾Ñ€Ð¼Ð¾Ð²Ð¾Ð¹ Ð´Ñ€Ð°ÐºÐ¾Ð½Ñ‡Ð¸Ðº", hd = 4, rd = 1.5, mv = { sp = 1.7, rad = 1.4, side = false },
	joints = { "root", "body", "flL", "flL2", "blL", "blL2", "wingL", "wingL2", "flR", "flR2", "blR", "blR2", "wingR", "wingR2", "t1", "t2", "t3", "t4", "t5", "tip", "neck", "head", "eyeL", "browL", "eyeR", "browR", "nose", "hornL", "earL", "hornR", "earR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.72, -0.05, 0, 0, 0 },
		flL = { 0.3, -0.14, 0.36, 0, 0, 0 },
		flL2 = { 0, -0.26, 0, 0, 0, 0 },
		blL = { 0.32, -0.12, -0.36, 0, 0, 0 },
		blL2 = { 0, -0.28, 0, 0, 0, 0 },
		wingL = { 0.26, 0.3, -0.02, 0, -0.6, -0.5 },
		wingL2 = { 0, 0.58, 0, -0.9, 0, 0 },
		flR = { -0.3, -0.14, 0.36, 0, 0, 0 },
		flR2 = { 0, -0.26, 0, 0, 0, 0 },
		blR = { -0.32, -0.12, -0.36, 0, 0, 0 },
		blR2 = { 0, -0.28, 0, 0, 0, 0 },
		wingR = { -0.26, 0.3, -0.02, 0, 0.6, 0.5 },
		wingR2 = { 0, 0.58, 0, -0.9, 0, 0 },
		t1 = { 0, 0, -0.56, 0.1, 0, 0 },
		t2 = { 0, 0, -0.28, 0.1, 0, 0 },
		t3 = { 0, 0, -0.28, 0.12, 0, 0 },
		t4 = { 0, 0, -0.26, 0.15, 0, 0 },
		t5 = { 0, 0, -0.26, 0.2, 0, 0 },
		tip = { 0, 0, -0.22, 0, 0, 0 },
		neck = { 0, 0.2, 0.46, 0.5, 0, 0 },
		head = { 0, 0.5, 0.04, -0.5, 0, 0 },
		eyeL = { 0.23, 0.07, 0.35, 0, 0.52, 0 },
		browL = { 0.23, 0.28, 0.3, -0.25, 0.52, -0.3 },
		eyeR = { -0.23, 0.07, 0.35, 0, -0.52, 0 },
		browR = { -0.23, 0.28, 0.3, -0.25, -0.52, 0.3 },
		nose = { 0, -0.1, 0.36, 0, 0, 0 },
		hornL = { 0.2, 0.3, -0.1, -0.8, 0, -0.3 },
		earL = { 0.4, 0.02, -0.08, 0, 0.5, -1.2 },
		hornR = { -0.2, 0.3, -0.1, -0.8, 0, 0.3 },
		earR = { -0.4, 0.02, -0.08, 0, -0.5, 1.2 }
	},
}, self)
end

-- ============ sky_kitsune — ÐÐµÐ±ÐµÑÐ½Ñ‹Ð¹ ÐºÐ¸Ñ†ÑƒÐ½Ñ ============
do
local self = {}
self.tails = function(a, f)
forEach({"a", "b", "c", "d", "e"}, function(k, i)
return f(("k" .. k), i)
end)
end
self.idle = function(t, a)
L.base(a, t, {seed = 0.1})
a.R("body", (-0.5))
a.T("body", 0, (-0.2), 0)
forEach({"blL", "blR"}, function(n)
a.R(n, 1.45)
a.R((n .. "2"), (-1.9))
end)
forEach({"flL", "flR"}, function(n)
return a.R(n, 0.5)
end)
a.R("head", 0.45)
self.tails(a, function(p)
return a.R((p .. "1"), 0.35, 0, 0)
end)
self.tails(a, function(p, i)
a.R((p .. "1"), (0.1 * wave(t, 0.3, (i * 0.12))), (0.16 * wave(t, 0.24, (i * 0.2))), 0)
a.R((p .. "2"), (0.14 * wave(t, 0.3, ((i * 0.12) - 0.15))), (0.14 * wave(t, 0.24, ((i * 0.2) - 0.15))), 0)
a.R((p .. "3"), (0.2 * wave(t, 0.3, ((i * 0.12) - 0.3))), (0.14 * wave(t, 0.24, ((i * 0.2) - 0.3))), 0)
end)
a.R("earL", 0, 0, (0.3 * pulse(t, 3.8, 0.25)))
a.R("earR", 0, 0, ((-0.3) * pulse(t, 5.4, 0.25, 1.5)))
a.R("head", 0, 0, (0.16 * pulse(t, 7, 2.6, 2)))
a.T("root", 0, (0.01 * wave(t, 0.3)), 0)
end
self.move = function(t, a)
local f = 1.6
a.blink(t)
a.T("root", 0, (0.1 + (0.05 * wave(t, (f * 2), 0.1))), 0)
a.R("body", (0.03 * wave(t, (f * 2))), 0, (0.02 * wave(t, f)))
a.R("head", (0.04 * wave(t, (f * 2), 0.3)), 0, 0)
L.step(a, "flL", (t * f), 0.55, 0.06, 0.7)
L.step(a, "blR", ((t * f) + 0.06), 0.5, 0.05, (-0.6))
L.step(a, "flR", ((t * f) + 0.5), 0.55, 0.06, 0.7)
L.step(a, "blL", ((t * f) + 0.56), 0.5, 0.05, (-0.6))
self.tails(a, function(p, i)
a.R((p .. "1"), ((-0.45) + (0.12 * wave(t, f, (i * 0.1)))), ((0.1 * wave(t, (f / 2), (i * 0.2))) - ((i - 2) * 0.14)), 0)
a.R((p .. "2"), ((-0.1) + (0.16 * wave(t, f, ((i * 0.1) - 0.15)))), (0.1 * wave(t, (f / 2), ((i * 0.2) - 0.15))), 0)
a.R((p .. "3"), (0.2 * wave(t, f, ((i * 0.1) - 0.3))), 0, 0)
end)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
self.tails(a, function(p, i)
a.R((p .. "1"), (0.25 * e), (((i - 2) * 0.22) * e), 0)
a.R((p .. "2"), ((-0.2) * e), 0, 0)
a.R((p .. "3"), (((-0.3) * e) + ((0.1 * e) * sin(((u * 30) + i)))), 0, 0)
a.S((p .. "3"), (1 + (0.15 * e)))
end)
a.R("body", (0.22 * e))
a.R("flL", ((-0.4) * e))
a.R("flR", ((-0.4) * e))
a.R("flL2", (0.3 * e))
a.R("flR2", (0.3 * e))
a.R("head", (0.3 * e), 0, 0)
a.S("eyeL", 1, (1 - (0.7 * bump(u, 0.2, 0.8))), 1)
a.S("eyeR", 1, (1 - (0.7 * bump(u, 0.2, 0.8))), 1)
a.R("earL", (0.2 * e))
a.R("earR", (0.2 * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.25, 0.4, 0.4, 0.6, 1.35, 0.76, 1.2, 0.9, 0, 1, 0), kf(u, 0, 0.42, 0.3, 0.5, 0.5, 1.02, 0.64, 1, 1, 1))
local cu = (1 - ss(0.5, 0.72, u))
forEach({"flL", "flR"}, function(n)
a.R(n, ((-1.0) * cu))
a.R((n .. "2"), (1.9 * cu))
end)
forEach({"blL", "blR"}, function(n)
a.R(n, (1.0 * cu))
a.R((n .. "2"), ((-1.8) * cu))
end)
a.T("body", 0, ((-0.42) * cu), 0)
a.R("head", (0.5 * cu), 0, 0)
a.S("eyeL", 1, (1 - (0.9 * (1 - ss(0.52, 0.66, u)))), 1)
a.S("eyeR", 1, (1 - (0.9 * (1 - ss(0.52, 0.66, u)))), 1)
self.tails(a, function(p, i)
local o = ss((0.08 + (i * 0.07)), (0.3 + (i * 0.07)), u)
local wr = (1 - o)
a.R((p .. "1"), (0.6 * wr), ((((-(i - 2)) * 0.42) + 1.2) * wr), 0)
a.R((p .. "2"), 0, (1.3 * wr), 0)
a.R((p .. "3"), 0, (1.3 * wr), 0)
a.S((p .. "3"), (1 + (0.3 * bump(u, (0.08 + (i * 0.07)), (0.4 + (i * 0.07))))))
local fl = bump(u, 0.6, 0.95)
a.R((p .. "1"), (0.2 * fl), (((i - 2) * 0.2) * fl), 0)
a.R((p .. "3"), ((0.15 * fl) * sin(((u * 24) - i))), 0, 0)
end)
a.R("root", 0, (TAU * ss(0.56, 0.86, u)), 0)
L.squash(a, u, 0.88, 0.97, 0.1)
a.R("earL", 0, 0, (0.3 * bump(u, 0.9, 1)))
a.R("earR", 0, 0, ((-0.3) * bump(u, 0.9, 1)))
end
register("sky_kitsune", {
	name = "ÐÐµÐ±ÐµÑÐ½Ñ‹Ð¹ ÐºÐ¸Ñ†ÑƒÐ½Ñ", hd = 4.6, rd = 1.6, mv = { sp = 1.6, rad = 1.4, side = false },
	joints = { "root", "body", "flL", "flL2", "blL", "blL2", "flR", "flR2", "blR", "blR2", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR", "ka1", "ka2", "ka3", "kb1", "kb2", "kb3", "kc1", "kc2", "kc3", "kd1", "kd2", "kd3", "ke1", "ke2", "ke3" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.8, -0.05, 0, 0, 0 },
		flL = { 0.2, -0.2, 0.36, 0, 0, 0 },
		flL2 = { 0, -0.32, 0, 0, 0, 0 },
		blL = { 0.22, -0.16, -0.38, 0, 0, 0 },
		blL2 = { 0, -0.34, 0, 0, 0, 0 },
		flR = { -0.2, -0.2, 0.36, 0, 0, 0 },
		flR2 = { 0, -0.32, 0, 0, 0, 0 },
		blR = { -0.22, -0.16, -0.38, 0, 0, 0 },
		blR2 = { 0, -0.34, 0, 0, 0, 0 },
		head = { 0, 0.52, 0.52, 0, 0, 0 },
		eyeL = { 0.1974, 0.038, 0.4074, 0, 0.5, 0 },
		browL = { 0.1974, 0.246, 0.3474, -0.25, 0.5, -0.22 },
		eyeR = { -0.1974, 0.038, 0.4074, 0, -0.5, 0 },
		browR = { -0.1974, 0.246, 0.3474, -0.25, -0.5, 0.22 },
		nose = { 0, -0.095, 0.441, 0, 0, 0 },
		earL = { 0.26, 0.28, -0.04, -0.05, 0, -0.3 },
		earR = { -0.26, 0.28, -0.04, -0.05, 0, 0.3 },
		ka1 = { 0, 0.1, -0.5, 0.75, -0.84, 0 },
		ka2 = { 0, 0, -0.34, 0.3, 0, 0 },
		ka3 = { 0, 0, -0.36, 0.3, 0, 0 },
		kb1 = { 0, 0.1, -0.5, 0.75, -0.42, 0 },
		kb2 = { 0, 0, -0.34, 0.3, 0, 0 },
		kb3 = { 0, 0, -0.36, 0.3, 0, 0 },
		kc1 = { 0, 0.1, -0.5, 0.75, 0, 0 },
		kc2 = { 0, 0, -0.34, 0.3, 0, 0 },
		kc3 = { 0, 0, -0.36, 0.3, 0, 0 },
		kd1 = { 0, 0.1, -0.5, 0.75, 0.42, 0 },
		kd2 = { 0, 0, -0.34, 0.3, 0, 0 },
		kd3 = { 0, 0, -0.36, 0.3, 0, 0 },
		ke1 = { 0, 0.1, -0.5, 0.75, 0.84, 0 },
		ke2 = { 0, 0, -0.34, 0.3, 0, 0 },
		ke3 = { 0, 0, -0.36, 0.3, 0, 0 }
	},
}, self)
end

-- ============ comet_kitten — ÐšÐ¾Ð¼ÐµÑ‚Ð½Ñ‹Ð¹ ÐºÐ¾Ñ‚Ñ‘Ð½Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.4})
a.chain("t", 4, t, 0.4, 0.06, 0.2, 0, 0.18, 0.3)
a.R("star", 0, 0, (t * 0.8))
local lk = pulse(t, 6.2, 2)
a.R("flL", ((-1.1) * lk))
a.R("flL2", (1.5 * lk))
a.R("head", (0.25 * lk), (0.2 * lk), ((0.15 * lk) + ((0.06 * lk) * wave(t, 3))))
a.R("earL", 0, 0, (0.3 * pulse(t, 3.3, 0.22)))
a.R("earR", 0, 0, ((-0.3) * pulse(t, 4.9, 0.22, 1)))
a.S("eyeL", 1, (1 - (0.5 * lk)), 1)
a.S("eyeR", 1, (1 - (0.5 * lk)), 1)
end
self.move = function(t, a)
local f = 2.0
local p = ((t * f) % 1)
a.blink(t)
a.T("root", 0, kf(p, 0, 0, 0.5, 0.28, 1, 0), 0)
a.R("body", kf(p, 0, 0.12, 0.3, (-0.2), 0.7, 0.2, 1, 0.12))
a.R("head", (-kf(p, 0, 0.1, 0.3, (-0.15), 0.7, 0.15, 1, 0.1)), 0, 0)
local fr = kf(p, 0, 0.3, 0.3, (-0.9), 0.7, 0.5, 1, 0.3)
local bk = kf(p, 0, (-0.5), 0.25, 0.8, 0.7, (-0.6), 1, (-0.5))
a.R("flL", fr)
a.R("flR", (fr + 0.15))
a.R("blL", bk)
a.R("blR", (bk - 0.1))
forEach({"flL", "flR"}, function(n)
return a.R((n .. "2"), (0.7 * bump(p, 0.1, 0.6)))
end)
a.R("t1", ((-0.8) + (0.2 * wave(t, f, 0.2))))
a.R("t2", ((-0.2) + (0.2 * wave(t, f, 0.05))))
a.R("t3", (0.2 * wave(t, f, (-0.1))))
a.R("t4", (0.2 * wave(t, f, (-0.25))))
a.R("star", 0, 0, (t * 5))
a.R("earL", (0.3 * bump(p, 0.3, 0.8)))
a.R("earR", (0.3 * bump(p, 0.3, 0.8)))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.T("root", 0, (0.7 * bump(u, 0.12, 0.82)), 0)
a.R("root", ((-TAU) * ss(0.15, 0.8, u)), 0, 0)
a.R("flL", ((-0.8) * e))
a.R("flR", ((-0.8) * e))
a.R("blL", (0.8 * e))
a.R("blR", (0.8 * e))
a.R("star", 0, 0, (u * 14))
a.S("star", (1 + (0.4 * e)))
a.chain("t", 4, (u * 3), 1, (0.3 * e), 0, 0, 0.2, 0.2)
a.brows((0.03 * e))
L.squash(a, u, 0.82, 1, 0.14)
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.15, 0.28, 0.28, 0.4, 0.2, 0.56, 1.7, 0.74, 0, 1, 0), kf(u, 0, 0.42, 0.4, 0.5, 0.54, 1.03, 0.68, 1, 1, 1))
local pk = bump(u, 0, 0.4)
a.R("t1", (0.5 * pk))
a.R("t2", (((-0.5) * pk) + ((0.4 * pk) * wave(u, 7))))
a.R("t3", ((0.4 * pk) * wave(u, 7, (-0.2))))
a.S("star", (1 + (0.4 * pk)))
a.R("star", 0, 0, (u * 16))
local j = bump(u, 0.4, 0.76)
a.R("body", (((-0.5) * bump(u, 0.4, 0.56)) + (0.4 * bump(u, 0.58, 0.76))))
a.R("flL", ((-1.1) * j))
a.R("flR", ((-1.1) * j))
a.R("blL", (1.0 * j))
a.R("blR", (1.0 * j))
L.squash(a, u, 0.72, 0.84, 0.2)
local st = bump(u, 0.8, 1)
a.R("body", (0.35 * st))
a.T("body", 0, ((-0.06) * st), 0)
a.R("flL", ((-0.7) * st))
a.R("flR", ((-0.7) * st))
a.R("flL2", (0.3 * st))
a.R("flR2", (0.3 * st))
a.R("head", ((-0.3) * st), 0, 0)
a.R("t1", (0.4 * st))
a.S("eyeL", 1, (1 - (0.8 * st)), 1)
a.S("eyeR", 1, (1 - (0.8 * st)), 1)
end
register("comet_kitten", {
	name = "ÐšÐ¾Ð¼ÐµÑ‚Ð½Ñ‹Ð¹ ÐºÐ¾Ñ‚Ñ‘Ð½Ð¾Ðº", hd = 3.2, rd = 1.3, mv = { sp = 1.8, rad = 1.35, side = false },
	joints = { "root", "body", "flL", "flL2", "blL", "blL2", "flR", "flR2", "blR", "blR2", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR", "t1", "t2", "t3", "t4", "star" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.6, -0.05, 0, 0, 0 },
		flL = { 0.2, -0.16, 0.32, 0, 0, 0 },
		flL2 = { 0, -0.22, 0, 0, 0, 0 },
		blL = { 0.22, -0.14, -0.32, 0, 0, 0 },
		blL2 = { 0, -0.22, 0, 0, 0, 0 },
		flR = { -0.2, -0.16, 0.32, 0, 0, 0 },
		flR2 = { 0, -0.22, 0, 0, 0, 0 },
		blR = { -0.22, -0.14, -0.32, 0, 0, 0 },
		blR2 = { 0, -0.22, 0, 0, 0, 0 },
		head = { 0, 0.46, 0.48, 0, 0, 0 },
		eyeL = { 0.2162, 0.041, 0.4074, 0, 0.44, 0 },
		browL = { 0.2162, 0.275, 0.3474, -0.25, 0.44, -0.22 },
		eyeR = { -0.2162, 0.041, 0.4074, 0, -0.44, 0 },
		browR = { -0.2162, 0.275, 0.3474, -0.25, -0.44, 0.22 },
		nose = { 0, -0.1025, 0.441, 0, 0, 0 },
		earL = { 0.3, 0.3, -0.02, 0, 0, -0.25 },
		earR = { -0.3, 0.3, -0.02, 0, 0, 0.25 },
		t1 = { 0, 0.04, -0.5, 0.9, 0, 0 },
		t2 = { 0, 0, -0.24, 0.35, 0, 0 },
		t3 = { 0, 0, -0.24, 0.3, 0, 0 },
		t4 = { 0, 0, -0.24, 0.25, 0, 0 },
		star = { 0, 0, -0.3, 0, 0, 0 }
	},
}, self)
end

-- ============ moon_owlet — Ð›ÑƒÐ½Ð½Ñ‹Ð¹ ÑÐ¾Ð²Ñ‘Ð½Ð¾Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.7, head = 0, k = 1.6})
local k = math.floor((t / 2.4))
local e = ss(0, 0.09, ((t / 2.4) % 1))
local h = function(n)
return sin((n * 45.164))
end
a.R("head", 0, ((1.25 * (h(k) + ((h((k + 1)) - h(k)) * e))) * 0.8), ((0.35 * (h((k + 4)) + ((h((k + 5)) - h((k + 4))) * e))) * 0.6))
local w = pulse(t, 7.3, 1.4, 3)
a.S("eyeR", 1, (1 - (0.92 * w)), 1)
a.R("earL", 0, 0, (0.3 * pulse(t, 3.1, 0.3)))
a.R("earR", 0, 0, ((-0.3) * pulse(t, 4.3, 0.3, 1)))
local pf = pulse(t, 5.6, 1.6)
a.S("body", (1 + (0.06 * pf)), (1 - (0.03 * pf)), (1 + (0.06 * pf)))
L.flap(a, ((-0.12) * pf))
a.R("tail", (0.1 * wave(t, 0.4)))
end
self.move = function(t, a)
local f = 1.25
local w = wave(t, f)
a.blink(t)
a.T("root", 0, (0.8 + (0.14 * wave(t, f, 0.28))), 0)
a.R("body", (0.35 + (0.05 * wave(t, f, 0.1))))
a.R("head", (-0.3), 0, (0.05 * wave(t, (f / 2))))
L.flap(a, ((-1.35) + (1.0 * w)))
a.R("wingL", (0.3 * wave(t, f, 0.25)))
a.R("wingR", (0.3 * wave(t, f, 0.25)))
a.R("legL", 0.7)
a.R("legR", 0.7)
a.R("tail", (0.3 + (0.15 * wave(t, f, 0.4))))
a.R("earL", 0.3)
a.R("earR", 0.3)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("head", 0, (TAU * ss(0.1, 0.75, u)), 0)
a.S("body", (1 + (0.12 * e)), (1 - (0.04 * e)), (1 + (0.12 * e)))
L.flap(a, ((-0.5) * e))
a.T("root", 0, (0.12 * bump(u, 0.7, 1)), 0)
a.S("eyeL", (1 + (0.12 * e)))
a.S("eyeR", (1 + (0.12 * e)))
a.brows((0.03 * e))
a.R("earL", 0, 0, (0.4 * e))
a.R("earR", 0, 0, ((-0.4) * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.1, 0.3, 0.34, 0.42, 0.28, 0.56, 1.3, 0.7, 1.1, 0.84, 0, 1, 0), kf(u, 0, 0.42, 0.4, 0.5, 0.54, 1.03, 0.68, 1, 1, 1))
a.R("head", 0, kf(u, 0, 0, 0.08, (-1.3), 0.2, 1.3, 0.32, 0, 0.86, 0, 0.94, 0.5, 1, 0), ((0.3 * bump(u, 0.05, 0.36)) * wave(u, 4)))
local fl = (ss(0.4, 0.5, u) * (1 - ss(0.78, 0.88, u)))
L.flap(a, (fl * ((-1.25) + (0.9 * sin((u * 110))))))
a.R("body", (0.25 * fl))
a.R("legL", (0.5 * fl))
a.R("legR", (0.5 * fl))
a.R("root", 0, 0, ((0.1 * fl) * sin((u * 30))))
L.squash(a, u, 0.82, 0.94, 0.2)
local pf = bump(u, 0.88, 1)
a.S("body", (1 + (0.1 * pf)), 1, (1 + (0.1 * pf)))
a.R("earL", 0, 0, (0.4 * pf))
a.R("earR", 0, 0, ((-0.4) * pf))
end
register("moon_owlet", {
	name = "Ð›ÑƒÐ½Ð½Ñ‹Ð¹ ÑÐ¾Ð²Ñ‘Ð½Ð¾Ðº", hd = 3.2, rd = 1.5, mv = { sp = 1.3, rad = 1.35, side = false },
	joints = { "root", "body", "wingL", "legL", "wingR", "legR", "tail", "head", "eyeL", "browL", "eyeR", "browR", "nose", "earL", "earR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.6, 0, 0, 0, 0 },
		wingL = { 0.44, 0.16, -0.02, 0, 0, -2.8 },
		legL = { 0.2, -0.48, 0.1, 0, 0, 0 },
		wingR = { -0.44, 0.16, -0.02, 0, 0, 2.8 },
		legR = { -0.2, -0.48, 0.1, 0, 0, 0 },
		tail = { 0, -0.3, -0.38, -0.6, 0, 0 },
		head = { 0, 0.58, 0.04, 0, 0, 0 },
		eyeL = { 0.23, 0, 0.44, 0, 0.35, 0 },
		browL = { 0.23, 0.2, 0.42, -0.25, 0.35, -0.2 },
		eyeR = { -0.23, 0, 0.44, 0, -0.35, 0 },
		browR = { -0.23, 0.2, 0.42, -0.25, -0.35, 0.2 },
		nose = { 0, -0.1, 0.47, 0, 0, 0 },
		earL = { 0.34, 0.3, -0.04, -0.2, 0, -0.7 },
		earR = { -0.34, 0.3, -0.04, -0.2, 0, 0.7 }
	},
}, self)
end

-- ============ nebula_moth — Ð¢ÑƒÐ¼Ð°Ð½Ð½Ð¾ÑÑ‚Ð½Ñ‹Ð¹ Ð¼Ð¾Ñ‚Ñ‹Ð»Ñ‘Ðº ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.2, look = 0.5})
a.T("root", 0, (0.06 * wave(t, 0.35)), 0)
local w = ((-0.3) + (0.22 * wave(t, 0.35, 0.1)))
a.R("wingL", 0, 0, w)
a.R("wingR", 0, 0, (-w))
a.R("hwL", 0, 0, ((w * 0.8) - 0.1))
a.R("hwR", 0, 0, (((-w) * 0.8) + 0.1))
a.R("antL", (0.15 * wave(t, 0.5)), 0, (0.1 * wave(t, 0.37)))
a.R("antR", (0.15 * wave(t, 0.5, 0.3)), 0, ((-0.1) * wave(t, 0.37, 0.2)))
a.chain("t", 3, t, 0.35, 0.1, 0, 0, 0.2, 0.2)
for i = 1, 3 do
a.R((("l" .. i) .. "L"), (0.1 * wave(t, 0.4, (i * 0.2))))
a.R((("l" .. i) .. "R"), (0.1 * wave(t, 0.4, ((i * 0.2) + 0.5))))
end
end
self.move = function(t, a)
local f = 4.2
local j = ((sin((t * 7.3)) * 0.5) + (sin((t * 11.1)) * 0.5))
a.blink(t)
a.T("root", (0.08 * sin((t * 5.3))), ((0.12 * j) + (0.1 * wave(t, (f / 2)))), 0)
a.R("body", ((-0.35) + (0.06 * wave(t, f))), 0, (0.1 * sin((t * 5.3))))
a.R("head", 0.3, 0, 0)
local w = (0.05 + (0.5 * wave(t, f)))
a.R("wingL", 0, 0, w)
a.R("wingR", 0, 0, (-w))
local h = (0.05 + (0.45 * wave(t, f, (-0.14))))
a.R("hwL", 0, 0, h)
a.R("hwR", 0, 0, (-h))
a.R("antL", (-0.4))
a.R("antR", (-0.4))
a.chain("t", 3, t, f, 0.12, 0, 0, 0.15, 0.2)
for i = 1, 3 do
a.R((("l" .. i) .. "L"), 0.5)
a.R((("l" .. i) .. "R"), 0.5)
end
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.R("wingL", 0, 0, (((-0.25) * e) + ((0.03 * e) * sin((u * 120)))))
a.R("wingR", 0, 0, ((0.25 * e) - ((0.03 * e) * sin((u * 120)))))
a.R("hwL", 0, 0, ((-0.2) * e))
a.R("hwR", 0, 0, (0.2 * e))
a.S("wingL", (1 + (0.12 * e)))
a.S("wingR", (1 + (0.12 * e)))
a.R("root", 0, (TAU * ss(0.15, 0.85, u)), 0)
a.T("root", 0, (0.2 * e), 0)
a.R("body", ((-0.5) * e))
a.R("antL", 0, 0, (0.4 * e))
a.R("antR", 0, 0, ((-0.4) * e))
a.brows((0.03 * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, (-0.75), 0.26, (-0.5), 0.52, (-0.35), 0.7, 0.35, 0.84, 0.2, 1, 0), kf(u, 0, 0.5, 0.26, 0.6, 0.46, 1.0, 1, 1))
local k = ss(0.26, 0.6, u)
local cr = (1 - k)
a.S("wingL", (0.2 + (0.8 * k)), (0.25 + (0.75 * k)), 1)
a.S("wingR", (0.2 + (0.8 * k)), (0.25 + (0.75 * k)), 1)
a.S("hwL", (0.2 + (0.8 * ss(0.34, 0.66, u))))
a.S("hwR", (0.2 + (0.8 * ss(0.34, 0.66, u))))
local up = ((0.55 * cr) + ((0.25 * bump(u, 0.26, 0.6)) * sin((u * 40))))
local fl = (ss(0.62, 0.7, u) * (1 - ss(0.88, 1, u)))
local w = ((up + (fl * (0.05 + (0.5 * sin((u * 120)))))) - (0.3 * ss(0.9, 1, u)))
a.R("wingL", 0, 0, w)
a.R("wingR", 0, 0, (-w))
a.R("hwL", 0, 0, (w * 0.8))
a.R("hwR", 0, 0, ((-w) * 0.8))
a.R("body", (((-0.8) * cr) - (0.3 * fl)))
a.R("head", (0.6 * cr), ((0.4 * bump(u, 0.05, 0.3)) * wave(u, 5)), 0)
a.R("antL", ((0.6 * cr) + ((0.3 * bump(u, 0.5, 0.8)) * wave(u, 9))))
a.R("antR", ((0.6 * cr) + ((0.3 * bump(u, 0.5, 0.8)) * wave(u, 9, 0.3))))
for i = 1, 3 do
a.R((("l" .. i) .. "L"), ((0.4 * cr) * wave(u, 8, (i * 0.3))))
a.R((("l" .. i) .. "R"), ((0.4 * cr) * wave(u, 8, ((i * 0.3) + 0.5))))
end
end
register("nebula_moth", {
	name = "Ð¢ÑƒÐ¼Ð°Ð½Ð½Ð¾ÑÑ‚Ð½Ñ‹Ð¹ Ð¼Ð¾Ñ‚Ñ‹Ð»Ñ‘Ðº", hd = 4.2, rd = 1.5, mv = { sp = 1.5, rad = 1.35, side = false },
	joints = { "root", "body", "t1", "t2", "t3", "l1L", "l2L", "l3L", "wingL", "hwL", "l1R", "l2R", "l3R", "wingR", "hwR", "head", "eyeL", "browL", "eyeR", "browR", "nose", "antL", "antR" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 1, 0, 0, 0, 0 },
		t1 = { 0, -0.04, -0.26, -0.25, 0, 0 },
		t2 = { 0, 0, -0.22, -0.15, 0, 0 },
		t3 = { 0, 0, -0.2, -0.1, 0, 0 },
		l1L = { 0.18, -0.2, 0.2, 0, 0, 0.5 },
		l2L = { 0.18, -0.2, 0.04, 0, 0, 0.5 },
		l3L = { 0.18, -0.2, -0.12, 0, 0, 0.5 },
		wingL = { 0.22, 0.12, 0.04, 0, -1.15, -0.6 },
		hwL = { 0.22, 0.06, -0.02, 0, -1.15, -1.25 },
		l1R = { -0.18, -0.2, 0.2, 0, 0, -0.5 },
		l2R = { -0.18, -0.2, 0.04, 0, 0, -0.5 },
		l3R = { -0.18, -0.2, -0.12, 0, 0, -0.5 },
		wingR = { -0.22, 0.12, 0.04, 0, 1.15, 0.6 },
		hwR = { -0.22, 0.06, -0.02, 0, 1.15, 1.25 },
		head = { 0, 0.14, 0.36, 0, 0, 0 },
		eyeL = { 0.17, 0.02, 0.3, 0, 0.45, 0 },
		browL = { 0.17, 0.22, 0.28, -0.25, 0.45, -0.2 },
		eyeR = { -0.17, 0.02, 0.3, 0, -0.45, 0 },
		browR = { -0.17, 0.22, 0.28, -0.25, -0.45, 0.2 },
		nose = { 0, -0.1, 0.32, 0, 0, 0 },
		antL = { 0.12, 0.28, 0.02, -0.2, 0, -0.45 },
		antR = { -0.12, 0.28, 0.02, -0.2, 0, 0.45 }
	},
}, self)
end

-- ============ eclipse_dragon — Ð”Ñ€Ð°ÐºÐ¾Ð½Ñ‡Ð¸Ðº Ð·Ð°Ñ‚Ð¼ÐµÐ½Ð¸Ñ ============
do
local self = {}
self.idle = function(t, a)
L.base(a, t, {seed = 0.9, hn = "neck", look = 0.5})
a.S("halo", (1 + (0.06 * wave(t, 0.3))))
a.R("head", 0, (0.18 * wave(t, 0.08)), 0)
L.flap(a, ((0.06 * wave(t, 0.42)) + (0.25 * pulse(t, 5.8, 1.2))))
a.chain("t", 5, t, 0.3, 0.03, 0.13, 0, 0.15, 0.25)
a.R("tip", 0, 0, (0.3 * wave(t, 0.4)))
a.S("nose", (1 + (0.05 * pulse(t, 4.8, 0.4))))
end
self.move = function(t, a)
local f = 1.2
local w = wave(t, f)
a.blink(t)
a.T("root", 0, (0.8 + (0.14 * wave(t, f, 0.3))), 0)
a.R("body", (0.25 + (0.07 * wave(t, f, 0.15))))
a.R("neck", (0.1 - (0.07 * w)))
a.R("head", (-0.3), 0, 0)
L.flap(a, (0.65 - (0.8 * w)))
a.R("wingL2", (0.5 + (0.45 * wave(t, f, (-0.2)))))
a.R("wingR2", (0.5 + (0.45 * wave(t, f, (-0.2)))))
forEach({"flL", "flR"}, function(n)
a.R(n, 0.5)
a.R((n .. "2"), 0.9)
end)
forEach({"blL", "blR"}, function(n)
a.R(n, 0.9)
a.R((n .. "2"), (-0.5))
end)
a.chain("t", 5, t, f, 0.13, 0.05, 0, 0.17, 0.2)
end
self.react = function(u, a)
local e = bump(u, 0, 1)
a.S("halo", (1 + (0.6 * e)))
L.flap(a, (0.5 * e))
a.R("wingL", (0.7 * e))
a.R("wingR", (0.7 * e))
a.R("wingL2", (0.6 * e))
a.R("wingR2", (0.6 * e))
a.R("neck", ((-0.15) * e))
a.R("head", (0.15 * e), 0, 0)
a.R("nose", (0.2 * e))
a.brows(((-0.03) * e), (0.3 * e))
a.R("body", ((-0.15) * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, 0.0, 0.34, 0.15, 0.5, 0.1, 0.64, 1.3, 0.76, 1.1, 0.88, 0, 1, 0), kf(u, 0, 0.46, 0.34, 0.52, 0.5, 1.03, 0.64, 1, 1, 1))
a.S("halo", kf(u, 0, 1.6, 0.3, 1.9, 0.56, 1, 0.9, 1, 0.95, 1.5, 1, 1))
local cr = (1 - ss(0.34, 0.52, u))
forEach({"flL", "flR"}, function(n)
a.R(n, ((-0.9) * cr))
a.R((n .. "2"), (1.7 * cr))
end)
forEach({"blL", "blR"}, function(n)
a.R(n, (0.9 * cr))
a.R((n .. "2"), ((-1.6) * cr))
end)
a.T("body", 0, ((-0.36) * cr), 0)
a.R("neck", (0.6 * cr))
a.R("head", (0.2 * cr), 0, 0)
a.S("eyeL", 1, (1 - (0.9 * (1 - ss(0.3, 0.44, u)))), 1)
a.S("eyeR", 1, (1 - (0.9 * (1 - ss(0.3, 0.44, u)))), 1)
local w = kf(u, 0, (-0.4), 0.34, (-0.4), 0.52, 1.1, 0.6, (-0.1), 0.68, 1.0, 0.76, 0, 0.84, 0.8, 1, 0)
L.flap(a, w)
local w2 = kf(u, 0, (-0.5), 0.34, (-0.5), 0.52, 0.8, 0.88, 0.5, 1, 0)
a.R("wingL2", w2)
a.R("wingR2", w2)
L.squash(a, u, 0.86, 0.96, 0.16)
local ro = bump(u, 0.88, 1)
a.R("head", ((-0.3) * ro), 0, 0)
a.R("nose", (0.3 * ro))
a.chain("t", 5, (u * 6), 1, (0.14 * bump(u, 0.4, 1)), 0.1, 0, 0.17, 0.2)
end
register("eclipse_dragon", {
	name = "Ð”Ñ€Ð°ÐºÐ¾Ð½Ñ‡Ð¸Ðº Ð·Ð°Ñ‚Ð¼ÐµÐ½Ð¸Ñ", hd = 4.4, rd = 1.6, mv = { sp = 1.5, rad = 1.4, side = false },
	joints = { "root", "body", "flL", "flL2", "blL", "blL2", "wingL", "wingL2", "flR", "flR2", "blR", "blR2", "wingR", "wingR2", "t1", "t2", "t3", "t4", "t5", "tip", "neck", "head", "eyeL", "browL", "eyeR", "browR", "nose", "hornL", "hornR", "crest", "halo" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 0.74, -0.05, 0, 0, 0 },
		flL = { 0.32, -0.16, 0.36, 0, 0, 0 },
		flL2 = { 0, -0.26, 0, 0, 0, 0 },
		blL = { 0.34, -0.14, -0.36, 0, 0, 0 },
		blL2 = { 0, -0.28, 0, 0, 0, 0 },
		wingL = { 0.28, 0.32, -0.02, 0, -0.75, -0.45 },
		wingL2 = { 0, 0.58, 0, -0.9, 0, 0 },
		flR = { -0.32, -0.16, 0.36, 0, 0, 0 },
		flR2 = { 0, -0.26, 0, 0, 0, 0 },
		blR = { -0.34, -0.14, -0.36, 0, 0, 0 },
		blR2 = { 0, -0.28, 0, 0, 0, 0 },
		wingR = { -0.28, 0.32, -0.02, 0, 0.75, 0.45 },
		wingR2 = { 0, 0.58, 0, -0.9, 0, 0 },
		t1 = { 0, 0, -0.56, 0.1, 0, 0 },
		t2 = { 0, 0, -0.28, 0.15, 0, 0 },
		t3 = { 0, 0, -0.28, 0.25, 0, 0 },
		t4 = { 0, 0, -0.26, 0.35, 0, 0 },
		t5 = { 0, 0, -0.26, 0.4, 0, 0 },
		tip = { 0, 0, -0.22, 0, 0, 0 },
		neck = { 0, 0.22, 0.46, 0.5, 0, 0 },
		head = { 0, 0.5, 0.04, -0.5, 0, 0 },
		eyeL = { 0.24, 0.07, 0.37, 0, 0.52, 0 },
		browL = { 0.24, 0.28, 0.32, -0.25, 0.52, -0.2 },
		eyeR = { -0.24, 0.07, 0.37, 0, -0.52, 0 },
		browR = { -0.24, 0.28, 0.32, -0.25, -0.52, 0.2 },
		nose = { 0, -0.1, 0.38, 0, 0, 0 },
		hornL = { 0.26, 0.26, -0.12, -0.9, 0, -0.5 },
		hornR = { -0.26, 0.26, -0.12, -0.9, 0, 0.5 },
		crest = { 0, 0.3, -0.12, -0.3, 0, 0 },
		halo = { 0, 0.3, 0.3, -0.5, 0, 0 }
	},
}, self)
end

-- ============ astral_phoenix — ÐÑÑ‚Ñ€Ð°Ð»ÑŒÐ½Ñ‹Ð¹ Ñ„ÐµÐ½Ð¸ÐºÑ ============
do
local self = {}
self.tl = function(a, f)
forEach({"a", "b", "c", "d", "e"}, function(k, i)
return f(("p" .. k), i)
end)
end
self.idle = function(t, a)
L.base(a, t, {seed = 0.5, hn = "neck", look = 0.5})
local f = 0.55
local w = wave(t, f)
a.T("root", 0, (0.1 * wave(t, f, 0.28)), 0)
L.flap(a, (0.25 - (0.5 * w)))
a.R("wingL", (0.12 * wave(t, f, 0.25)))
a.R("wingR", (0.12 * wave(t, f, 0.25)))
a.R("body", (0.04 * wave(t, f, 0.1)))
self.tl(a, function(p, i)
return a.chain(p, 4, t, 0.4, 0.12, 0.08, 0, (0.14 + (i * 0.02)), 0.15)
end)
a.R("crest", (0.1 * wave(t, f, 0.3)))
a.R("aura", 0, 0, (t * 0.25))
a.S("aura", (1 + (0.03 * wave(t, 0.3))))
a.R("legL", (0.1 * wave(t, f)))
a.R("legR", (0.1 * wave(t, f, 0.2)))
end
self.move = function(t, a)
local f = 0.95
local w = wave(t, f)
a.blink(t)
a.T("root", 0, (0.2 * wave(t, f, 0.28)), 0)
a.R("body", (0.55 + (0.08 * wave(t, f, 0.1))))
a.R("neck", (-0.3))
a.R("head", (-0.25), 0, 0)
L.flap(a, (0.3 - (0.9 * w)))
a.R("wingL", (0.3 * wave(t, f, 0.25)))
a.R("wingR", (0.3 * wave(t, f, 0.25)))
self.tl(a, function(p, i)
a.R((p .. "1"), 0.5, 0, 0)
a.chain(p, 4, t, f, 0.16, 0.1, 0, (0.16 + (i * 0.02)), 0.2)
end)
a.R("crest", 0.35)
a.R("legL", 0.6)
a.R("legR", 0.6)
a.R("aura", 0, 0, (t * 0.8))
end
self.react = function(u, a)
local e = bump(u, 0, 1)
L.flap(a, (((-0.2) * e) - ((0.04 * e) * sin((u * 50)))))
a.T("root", 0, (0.35 * e), 0)
a.R("root", 0, (TAU * ss(0.2, 0.9, u)), 0)
a.R("body", ((-0.3) * e))
a.R("head", ((-0.3) * e), 0, 0)
a.R("nose", (0.25 * e))
a.S("aura", (1 + (0.5 * e)))
a.R("aura", 0, 0, (u * 6))
self.tl(a, function(p, i)
a.R((p .. "1"), (0.3 * e), (((i - 2) * 0.3) * e), 0)
for j = 2, 4 do
a.R((p .. j), (0.12 * e), 0, 0)
end
end)
a.R("crest", ((-0.3) * e))
a.brows(((-0.02) * e), (0.25 * e))
end
self.hatch = function(u, a)
L.rise(a, u, kf(u, 0, (-0.9), 0.3, (-0.4), 0.46, (-0.15), 0.6, 0.5, 0.76, 0.25, 1, 0), kf(u, 0, 0.6, 0.3, 0.72, 0.46, 0.95, 0.52, 1.06, 0.62, 1, 1, 1))
local wr = (1 - ss(0.44, 0.52, u))
local w = kf(u, 0, (-1.1), 0.44, (-1.1), 0.52, 0.55, 0.6, 0.2, 0.68, (-0.7), 0.76, 0.5, 0.84, (-0.5), 0.92, 0.4, 1, 0)
L.flap(a, w)
a.R("wingL", 0, (1.25 * wr), 0)
a.R("wingR", 0, ((-1.25) * wr), 0)
a.R("neck", ((0.7 * wr) - (0.3 * bump(u, 0.5, 0.7))))
a.R("head", ((0.5 * wr) - (0.3 * bump(u, 0.5, 0.7))), 0, 0)
a.S("eyeL", 1, (1 - (0.9 * (1 - ss(0.42, 0.5, u)))), 1)
a.S("eyeR", 1, (1 - (0.9 * (1 - ss(0.42, 0.5, u)))), 1)
a.R("root", 0, (TAU * ss(0.02, 0.44, u)), 0)
a.R("body", ((-0.3) * bump(u, 0.46, 0.66)))
self.tl(a, function(p, i)
a.R((p .. "1"), ((0.9 * wr) + (0.4 * bump(u, 0.5, 0.8))), (((i - 2) * 0.35) * bump(u, 0.5, 0.9)), 0)
a.chain(p, 4, (u * 6), 1, (0.2 * (1 - wr)), 0.1, 0, 0.16, 0.2)
end)
a.S("aura", kf(u, 0, 0.05, 0.44, 0.05, 0.56, 1.7, 0.8, 1, 1, 1))
a.R("aura", 0, 0, (u * 5))
a.R("crest", ((0.6 * wr) - (0.4 * bump(u, 0.5, 0.7))))
a.R("nose", (0.25 * bump(u, 0.5, 0.64)))
end
register("astral_phoenix", {
	name = "ÐÑÑ‚Ñ€Ð°Ð»ÑŒÐ½Ñ‹Ð¹ Ñ„ÐµÐ½Ð¸ÐºÑ", hd = 5, rd = 1.7, mv = { sp = 1.6, rad = 1.45, side = false },
	joints = { "root", "body", "wingL", "legL", "wingR", "legR", "pa1", "pa2", "pa3", "pa4", "pb1", "pb2", "pb3", "pb4", "pc1", "pc2", "pc3", "pc4", "pd1", "pd2", "pd3", "pd4", "pe1", "pe2", "pe3", "pe4", "neck", "head", "eyeL", "browL", "eyeR", "browR", "nose", "crest", "aura" },
	rest = {
		root = { 0, 0, 0, 0, 0, 0 },
		body = { 0, 1.2, 0, 0.2, 0, 0 },
		wingL = { 0.3, 0.2, -0.04, 0, 0, -1.2 },
		legL = { 0.14, -0.4, 0.1, 0.5, 0, 0 },
		wingR = { -0.3, 0.2, -0.04, 0, 0, 1.2 },
		legR = { -0.14, -0.4, 0.1, 0.5, 0, 0 },
		pa1 = { -0.14, -0.34, -0.2, -1.15, -0.56, 0 },
		pa2 = { 0, 0, -0.36, 0.1, 0, 0 },
		pa3 = { 0, 0, -0.36, 0.1, 0, 0 },
		pa4 = { 0, 0, -0.36, 0.1, 0, 0 },
		pb1 = { -0.07, -0.34, -0.2, -1.15, -0.28, 0 },
		pb2 = { 0, 0, -0.36, 0.1, 0, 0 },
		pb3 = { 0, 0, -0.36, 0.1, 0, 0 },
		pb4 = { 0, 0, -0.36, 0.1, 0, 0 },
		pc1 = { 0, -0.34, -0.2, -1.15, 0, 0 },
		pc2 = { 0, 0, -0.36, 0.1, 0, 0 },
		pc3 = { 0, 0, -0.36, 0.1, 0, 0 },
		pc4 = { 0, 0, -0.36, 0.1, 0, 0 },
		pd1 = { 0.07, -0.34, -0.2, -1.15, 0.28, 0 },
		pd2 = { 0, 0, -0.36, 0.1, 0, 0 },
		pd3 = { 0, 0, -0.36, 0.1, 0, 0 },
		pd4 = { 0, 0, -0.36, 0.1, 0, 0 },
		pe1 = { 0.14, -0.34, -0.2, -1.15, 0.56, 0 },
		pe2 = { 0, 0, -0.36, 0.1, 0, 0 },
		pe3 = { 0, 0, -0.36, 0.1, 0, 0 },
		pe4 = { 0, 0, -0.36, 0.1, 0, 0 },
		neck = { 0, 0.36, 0.14, 0.1, 0, 0 },
		head = { 0, 0.4, 0.06, -0.3, 0, 0 },
		eyeL = { 0.17, 0.05, 0.3, 0, 0.55, 0 },
		browL = { 0.17, 0.24, 0.26, -0.25, 0.55, -0.2 },
		eyeR = { -0.17, 0.05, 0.3, 0, -0.55, 0 },
		browR = { -0.17, 0.24, 0.26, -0.25, -0.55, 0.2 },
		nose = { 0, -0.06, 0.33, 0, 0, 0 },
		crest = { 0, 0.26, -0.04, 0, 0, 0 },
		aura = { 0, 0.1, -0.3, 0, 0, 0 }
	},
}, self)
end

return PetAnimations
