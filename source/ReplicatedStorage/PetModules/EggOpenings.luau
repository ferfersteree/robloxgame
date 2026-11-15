--!nonstrict
-- EggOpenings: открытия яиц SpearHunt, перенесённые из веб-прототипа формула в формулу.
-- Сгенерировано автоматически из кода прототипа. Не править вручную.
--
-- EggOpenings[eggId] = { prep, open, clear, emerge, update(t, set [, hd]), idle(t, set), events = {...}, groups = {...} }
--   set(имяГруппы, CFrame, k): CFrame — для Motor6D "<имяГруппы>_Joint".Transform; k — масштаб группы из прототипа
local EggOpenings = {}

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

-- ===== состояние яйца: те же вызовы mv / hinge / rot / sc, что в прототипе =====
-- info.groups[name] = { ax, ay, az } — ось петли группы в осях прототипа
local function register(id, info, self)
	local names, groups = info.order, info.groups
	-- parts[n] повторяет объект группы прототипа: p0 — исходное место, g.position / g.rotation — текущие
	local parts, quat, ks = {}, {}, {}
	for _, n in ipairs(names) do
		local g = groups[n]
		local p = { p0 = { x = g[4], y = g[5], z = g[6] }, axis = { g[1], g[2], g[3] }, g = { position = { x = g[4], y = g[5], z = g[6] }, rotation = { x = 0, y = 0, z = 0, order = "XYZ" } } }
		local r = p.g.rotation
		r.set = function(x, y, z, order) r.x, r.y, r.z = x, y, z if order then r.order = order end quat[n] = nil end
		parts[n] = p
		ks[n] = 1
	end
	local e = { x = info.x, parts = parts, L = 0, sw = 0, Lc = { set = function() end } }
	e.x.gm = { material = { opacity = 0 } } -- свечение внутри яйца
	e.x.sg = { opacity = 0 }                 -- солнечный рисунок (янтарное)
	e.x.cm = { opacity = 1 }                 -- трещина-молния (грозовое)
	function e.mv(n, x, y, z) local p = parts[n] if p then local q = p.g.position q.x, q.y, q.z = p.p0.x + x, p.p0.y + y, p.p0.z + z end end
	function e.hinge(n, a, ax)
		local p = parts[n] if not p then return end
		local vx, vy, vz = p.axis[1], p.axis[2], p.axis[3]
		if ax then vx, vy, vz = ax.x, ax.y, ax.z end
		quat[n] = CFrame.fromAxisAngle(Vector3.new(-vx, vy, -vz), a)
	end
	function e.rot(n, x, y, z) local p = parts[n] if p then p.g.rotation.set(x, y, z) end end
	function e.orbit(n, ang, out, dy)
		local p = parts[n]
		local c, s = cos(ang), sin(ang)
		local x, z = p.p0.x * (1 + out), p.p0.z * (1 + out)
		local q = p.g.position
		q.x, q.y, q.z = x * c + z * s, p.p0.y + dy, -x * s + z * c
		p.g.rotation.y = ang
		quat[n] = nil
	end
	-- МАСШТАБ группы: Motor6D его не умеет, поэтому k уходит третьим аргументом в set(name, cf, k).
	-- Неравномерный масштаб (sc с тремя числами) сведён к первому числу.
	function e.sc(n, s1) if parts[n] then ks[n] = max(0.0001, s1) end end
	function e.ev() return false end -- события вынесены в таблицу events
	local fx = { emit = function() end, burst = function() end, ring = function() end, bolt = function() end, rnd = function() return 1 end }
	self.prep, self.open, self.clear, self.emerge, self.glow = info.prep, info.open, info.clear, info.emerge, info.glow

	local function reset()
		for _, n in ipairs(names) do
			local p = parts[n]
			local q, r = p.g.position, p.g.rotation
			q.x, q.y, q.z = p.p0.x, p.p0.y, p.p0.z
			r.x, r.y, r.z = 0, 0, 0
			quat[n] = nil
			ks[n] = 1
		end
		e.L, e.sw = 0, 0
	end
	local extra = {}
	local function flush(set)
		for i = 1, #names do
			local n = names[i]
			local p = parts[n]
			local q, r = p.g.position, p.g.rotation
			local cf = CFrame.new(-(q.x - p.p0.x) * SCALE, (q.y - p.p0.y) * SCALE, -(q.z - p.p0.z) * SCALE)
			if quat[n] then
				cf = cf * quat[n]
			elseif r.x ~= 0 or r.y ~= 0 or r.z ~= 0 then
				if r.order == "YXZ" then cf = cf * CFrame.fromEulerAnglesYXZ(-r.x, r.y, -r.z) else cf = cf * CFrame.fromEulerAnglesXYZ(-r.x, r.y, -r.z) end
			end
			set(n, cf, ks[n])
		end
		-- sway: наклон всего яйца вокруг оси Z (радианы, уже в осях Roblox); sun / crack: непрозрачность 0..1
		extra.sway, extra.sun, extra.crack = -e.sw, e.x.sg.opacity, e.x.cm.opacity
		return e.L, e.x.gm.material.opacity, extra
	end
	local entry = { id = id, name = info.name, price = info.price, pets = info.pets, groups = names,
		prep = info.prep, open = info.open, clear = info.clear, emerge = info.emerge,
		glowColor = info.glowColor, themeColor = info.themeColor, events = info.events }
	-- update(t, set [, hd]): t — секунды от начала открытия; hd — длительность появления питомца (сек).
	-- set(имяГруппы, CFrame для Motor6D.Transform, k) — k это масштаб группы из прототипа (1 = норма, →0 = исчезла).
	-- Возвращает: яркость внутреннего света (0..3), непрозрачность свечения (0..1) и таблицу { sway, sun, crack }.
	function entry.update(t, set, hd)
		hd = hd or 2.8
		local tC = info.prep + info.open * info.emerge + hd * 0.42
		reset()
		self.seq(e, t, t - tC, fx, 0)
		return flush(set)
	end
	-- покой на витрине (как в магазине прототипа)
	function entry.idle(t, set)
		reset()
		self.seq(e, 0, -1, fx, 0)
		self.idle(e, t)
		e.sw = 0
		return flush(set)
	end
	-- момент появления питомца и полная длительность
	function entry.emergeTime() return info.prep + info.open * info.emerge end
	function entry.duration(hd) hd = hd or 2.8 return info.prep + info.open * info.emerge + hd * 0.42 + info.clear end
	EggOpenings[id] = entry
end


-- ============ forest — Ð›ÐµÑÐ½Ð¾Ð¹ Ñ‚Ð°Ð»Ð¸ÑÐ¼Ð°Ð½ ============
do
local self = {}
self.idle = function(e, t)
e.hinge("spA", (0.08 * wave(t, 0.5)))
e.hinge("spB", ((-0.08) * wave(t, 0.5, 0.2)))
for k = 0, (5) - 1 do
e.hinge(("lf" .. k), (0.03 + (0.03 * wave(t, 0.4, (k * 0.2)))))
end
e.sc("glow", 0.01)
end
self.seq = function(e, t, c, fx, x0)
local P = self.prep
local O = self.open
local o = (t - P)
local alive = (ss(0.1, 0.8, t) * (1 - ss((P + 0.2), (P + 0.9), t)))
for k = 0, (5) - 1 do
e.hinge(("lf" .. k), (0.05 + (alive * (0.22 + (0.2 * sin(((t * 8.5) + (k * 1.7))))))))
end
local gr = ss(0.4, 1.9, t)
e.sc("sprout", (1 + (0.55 * gr)))
e.hinge("spA", (((-0.35) * gr) + ((0.12 * alive) * sin((t * 6)))))
e.hinge("spB", ((0.35 * gr) - ((0.12 * alive) * sin(((t * 6) + 1)))))
local gl = (ss(0.8, P, t) * (1 - ss(0, 0.9, c)))
e.sc("glow", max(0.01, ((0.55 + (0.42 * gl)) + (0.03 * sin((t * 7))))))
e.x.gm.material.opacity = (0.85 * gl)
e.L = ((1.6 * gl) + (1.4 * bump(o, 0, 0.8)))
e.Lc.set(self.glow)
if (((t < P) and (t > 0.5)) and (fx.rnd() < (0.25 * alive))) then
local a = (fx.rnd() * TAU)
fx.emit({tex = "dot", p = {(x0 + (sin(a) * 1.0)), (0.6 + (fx.rnd() * 1.4)), (cos(a) * 1.0)}, v = {0, 0.35, 0}, life = 1.3, s = 0.07, s1 = 0.02, col = "#e9ff9a", sway = 0.4})
end
for k = 0, (8) - 1 do
local u = ss((1.55 + (k * 0.1)), (2.05 + (k * 0.1)), t)
local n = e.x[("bn" .. k)]
e.mv(("belt" .. k), ((n.x * 0.55) * u), ((((-1.0) * u) * u) + (0.25 * sin((u * PI)))), ((n.z * 0.55) * u))
e.hinge(("belt" .. k), (2.2 * u))
e.sc(("belt" .. k), (1 - ss(0.75, 1, u)))
if truthy(e.ev(("b" .. k), t, (1.55 + (k * 0.1)))) then
fx.burst(3, function(i, r)
return {tex = "chip", p = {(x0 + (n.x * 1.1)), 1.05, (n.z * 1.1)}, v = {((n.x * 1.2) + (r() - 0.5)), (1.2 + r()), ((n.z * 1.2) + (r() - 0.5))}, g = 5, life = 0.7, s = 0.08, col = "#b9773f", add = false, spin = 6}
end)
end
end
local tr = (ss(1.6, P, t) * (1 - ss(0, 0.3, o)))
e.mv("cap", 0, kf(o, 0, 0, 0.25, 0.25, 1.1, 1.9), 0)
e.rot("cap", 0, (max(0, o) * 3.2), (0.2 * bump(o, 0.1, 1.2)))
e.sc("cap", (1 - ss(0.7, 1.3, o)))
for k = 0, (5) - 1 do
local u = (((o - 0.12) - (k * 0.07)) / 0.95)
local a = (((0.05 * tr) * (1 + sin(((t * 30) + k)))) + iff((u > 0), (1.35 * outBack(min(1, u))), 0))
local w = ss(0, 1, (c - (k * 0.05)))
e.hinge(("pet" .. k), (a + (0.5 * w)))
e.sc(("pet" .. k), (1 - ss(0.2, 1, (c - (k * 0.05)))))
end
if truthy(e.ev("open", t, (P + 0.15))) then
fx.ring({x0, 0.08, 0}, "#c9ff8a", 0.6, 2.6, 0.9, 0.7)
fx.burst(22, function(i, r)
local a = (r() * TAU)
local s = (1.2 + (r() * 1.8))
return {tex = "leaf", p = {(x0 + (sin(a) * 0.6)), (1.5 + (r() * 0.5)), (cos(a) * 0.6)}, v = {(sin(a) * s), (1.6 + (r() * 2)), (cos(a) * s)}, g = 2.6, drag = 0.8, life = (1.6 + r()), s = (0.2 + (r() * 0.14)), col = iff((r() > 0.5), "#8fd82e", "#3fa53c"), add = false, rot = (r() * 6), spin = ((r() - 0.5) * 8), sway = 0.6}
end)
fx.burst(26, function(i, r)
local a = (r() * TAU)
return {tex = "dot", p = {(x0 + ((sin(a) * 0.5) * r())), 1.2, ((cos(a) * 0.5) * r())}, v = {(sin(a) * 0.5), (0.8 + (r() * 1.6)), (cos(a) * 0.5)}, life = (1.4 + r()), s = 0.1, s1 = 0.02, col = "#f1ffb0", sway = 0.5, drag = 0.6}
end)
end
e.mv("cup", 0, ((-0.5) * ss(0.1, 1.2, c)), 0)
e.sc("cup", (1 - ss(0.25, 1.25, c)))
end
register("forest", {
	name = "Ð›ÐµÑÐ½Ð¾Ð¹ Ñ‚Ð°Ð»Ð¸ÑÐ¼Ð°Ð½", price = 59, prep = 2.5, open = 1.5, clear = 1.3, emerge = 0.55, glow = "#f4ffb0",
	glowColor = Color3.fromRGB(244, 255, 176), themeColor = Color3.fromRGB(111, 208, 74),
	pets = { "clover_beetle", "moss_bunny", "hazel_squirrel", "flower_hedgehog", "guardian_fawn" },
	order = { "cup", "belt0", "belt1", "belt2", "belt3", "belt4", "belt5", "belt6", "belt7", "pet0", "lf0", "pet1", "lf1", "pet2", "lf2", "pet3", "lf3", "pet4", "lf4", "cap", "sprout", "spA", "spB", "glow" },
	groups = {
		cup = { 1, 0, 0, 0, 0, 0 },
		belt0 = { 0.923879533, 0, -0.382683432, 0.399285794, 1.051048103, 0.963961178 },
		belt1 = { 0.382683432, 0, -0.923879533, 0.963961178, 1.051048103, 0.399285794 },
		belt2 = { -0.382683432, 0, -0.923879533, 0.963961178, 1.051048103, -0.399285794 },
		belt3 = { -0.923879533, 0, -0.382683432, 0.399285794, 1.051048103, -0.963961178 },
		belt4 = { -0.923879533, 0, 0.382683432, -0.399285794, 1.051048103, -0.963961178 },
		belt5 = { -0.382683432, 0, 0.923879533, -0.963961178, 1.051048103, -0.399285794 },
		belt6 = { 0.382683432, 0, 0.923879533, -0.963961178, 1.051048103, 0.399285794 },
		belt7 = { 0.923879533, 0, 0.382683432, -0.399285794, 1.051048103, 0.963961178 },
		pet0 = { 1, 0, 0, 0, 1.154454838, 0.938616413 },
		lf0 = { 1, 0, 0, 0, 0.773543258, -0.225992523 },
		pet1 = { 0.309016994, 0, -0.951056516, 0.892677256, 1.154454838, 0.290048423 },
		lf1 = { 0.309016994, 0, -0.951056516, -0.214931662, 0.773543258, -0.06983553 },
		pet2 = { -0.809016994, 0, -0.587785252, 0.551704885, 1.154454838, -0.75935663 },
		lf2 = { -0.809016994, 0, -0.587785252, -0.132835072, 0.773543258, 0.182831792 },
		pet3 = { -0.809016994, 0, 0.587785252, -0.551704885, 1.154454838, -0.75935663 },
		lf3 = { -0.809016994, 0, 0.587785252, 0.132835072, 0.773543258, 0.182831792 },
		pet4 = { 0.309016994, 0, 0.951056516, -0.892677256, 1.154454838, 0.290048423 },
		lf4 = { 0.309016994, 0, 0.951056516, 0.214931662, 0.773543258, -0.06983553 },
		cap = { 1, 0, 0, 0, 2.001, 0 },
		sprout = { 1, 0, 0, 0, 0.299, 0 },
		spA = { 0, 0, 1, 0, 0.24, 0 },
		spB = { 0, 0, 1, 0, 0.24, 0 },
		glow = { 1, 0, 0, 0, 1.15, 0 }
	},
	x = { bn0 = { x = 0.381096964, y = 0.090962065, z = 0.920049459 }, bn1 = { x = 0.920049459, y = 0.090962065, z = 0.381096964 }, bn2 = { x = 0.920049459, y = 0.090962065, z = -0.381096964 }, bn3 = { x = 0.381096964, y = 0.090962065, z = -0.920049459 }, bn4 = { x = -0.381096964, y = 0.090962065, z = -0.920049459 }, bn5 = { x = -0.920049459, y = 0.090962065, z = -0.381096964 }, bn6 = { x = -0.920049459, y = 0.090962065, z = 0.381096964 }, bn7 = { x = -0.381096964, y = 0.090962065, z = 0.920049459 } },
	events = {
		{ t = 0.5, type = "stream", color = Color3.fromRGB(233, 255, 154), count = 15, untilT = 2.5, note = "искры вокруг яйца, ~15 в секунду, поднимаются вверх" },
		{ t = 1.55, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt0", note = "щепки от сегмента пояса" },
		{ t = 1.65, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt1", note = "щепки от сегмента пояса" },
		{ t = 1.75, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt2", note = "щепки от сегмента пояса" },
		{ t = 1.85, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt3", note = "щепки от сегмента пояса" },
		{ t = 1.95, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt4", note = "щепки от сегмента пояса" },
		{ t = 2.05, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt5", note = "щепки от сегмента пояса" },
		{ t = 2.15, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt6", note = "щепки от сегмента пояса" },
		{ t = 2.25, type = "burst", color = Color3.fromRGB(185, 119, 63), count = 3, group = "belt7", note = "щепки от сегмента пояса" },
		{ t = 2.5, type = "flash", color = Color3.fromRGB(244, 255, 176), count = 1, life = 0.8, note = "вспышка света изнутри" },
		{ t = 2.65, type = "ring", color = Color3.fromRGB(201, 255, 138), count = 1, r0 = 0.9, r1 = 3.9, life = 0.9, note = "кольцо по полу" },
		{ t = 2.65, type = "burst", color = Color3.fromRGB(143, 216, 46), count = 22, color2 = Color3.fromRGB(63, 165, 60), note = "листья-кубики вверх и в стороны" },
		{ t = 2.65, type = "burst", color = Color3.fromRGB(241, 255, 176), count = 26, note = "мягкие искры вверх" },
	},
}, self)
end

-- ============ amber — Ð¯Ð½Ñ‚Ð°Ñ€Ð½Ð¾Ðµ ÑÐµÑ€Ð´Ñ†Ðµ ============
do
local self = {}
self.idle = function(e, t)
e.sc("glow", 0.01)
e.sc("sun", 0.01)
end
self.seq = function(e, t, c, fx, x0)
local P = self.prep
local o = (t - P)
for k = 0, (6) - 1 do
local u = ((t - 0.25) - (k * 0.2))
e.sc(("inc" .. k), ((1 + (0.5 * bump(u, 0, 0.5))) + iff((u > 0), (0.12 + (0.1 * sin(((t * 9) + k)))), 0)))
if truthy(e.ev(("i" .. k), t, (0.25 + (k * 0.2)))) then
local n = e.x[("n" .. k)]
fx.burst(5, function(i, r)
return {tex = "star", p = {(x0 + (n.x * 0.95)), (0.7 + (r() * 0.9)), (n.z * 0.95)}, v = {(n.x * 0.4), (0.3 + (r() * 0.4)), (n.z * 0.4)}, life = (0.7 + (r() * 0.4)), s = 0.16, s1 = 0.02, col = "#ffe08a"}
end)
end
end
local gl = (ss(0.2, 1.6, t) * (1 - ss(0, 0.9, c)))
e.sc("glow", max(0.01, ((0.7 + (0.3 * gl)) + (0.03 * sin((t * 8))))))
e.x.gm.material.opacity = (0.6 * gl)
e.L = ((1.4 * gl) + (1.6 * bump(o, 0, 0.7)))
e.Lc.set(self.glow)
local sn = (ss(1.2, 2.2, t) * (1 - ss(0.1, 0.6, o)))
e.sc("sun", max(0.01, ((outBack(ss(1.2, 2.1, t)) * (1 + (0.06 * sin((t * 10))))) * iff((sn > 0), 1, 0))))
e.x.sg.opacity = (0.9 * sn)
e.parts.sun.g.rotation.z = (t * 0.5)
if truthy(e.ev("sr", t, 1.5)) then
fx.ring({x0, 0.04, 0}, "#ffcf5a", 0.3, 2.4, 1.1, 0.8)
end
if truthy(e.ev("sr2", t, 2.0)) then
fx.ring({x0, 0.05, 0}, "#fff0b0", 0.3, 3.0, 1.1, 0.6)
end
if (((t > 1.3) and (t < (P + 0.4))) and (fx.rnd() < 0.3)) then
local a = (fx.rnd() * TAU)
fx.emit({tex = "dot", p = {(x0 + (sin(a) * 1.6)), 0.1, (cos(a) * 1.6)}, v = {((-sin(a)) * 0.9), 0.8, ((-cos(a)) * 0.9)}, life = 0.9, s = 0.09, s1 = 0.02, col = "#ffd86a"})
end
e.mv("cap", 0, kf(o, 0, 0, 0.3, 0.35, 1.2, 1.5), 0)
e.rot("cap", 0, (max(0, o) * 2.4), 0)
e.sc("cap", (1 - ss(0.8, 1.4, o)))
for j = 0, (6) - 1 do
local k = ({0, 3, 1, 4, 2, 5})[(j) + 1]
local u = (((o - 0.12) - (j * 0.14)) / 0.8)
e.hinge(("seg" .. k), iff((u > 0), (1.2 * outBack(min(1, u))), ((0.03 * ss(2.2, P, t)) * (1 + sin(((t * 26) + k))))))
if truthy(e.ev(("s" .. k), t, ((P + 0.12) + (j * 0.14)))) then
local n = e.x[("n" .. k)]
fx.burst(6, function(i, r)
return {tex = "chip", p = {(x0 + (n.x * 0.9)), (1.3 + (r() * 0.6)), (n.z * 0.9)}, v = {(n.x * (1 + (r() * 1.4))), (1 + (r() * 2)), (n.z * (1 + (r() * 1.4)))}, g = 5, life = 0.9, s = 0.11, col = iff((r() > 0.5), "#ffb23a", "#ffd97a"), spin = 8, floor = 0.03}
end)
fx.ring({(x0 + (n.x * 0.7)), 0.04, (n.z * 0.7)}, "#ffcf5a", 0.1, 0.9, 0.5, 0.5)
end
local w = ss(0, 1, (c - (j * 0.06)))
e.sc(("seg" .. k), (1 - w))
if (w > 0) then
e.hinge(("seg" .. k), (1.2 + (0.5 * w)))
end
end
e.mv("base", 0, ((-0.4) * ss(0.3, 1.2, c)), 0)
e.sc("base", (1 - ss(0.4, 1.25, c)))
end
register("amber", {
	name = "Ð¯Ð½Ñ‚Ð°Ñ€Ð½Ð¾Ðµ ÑÐµÑ€Ð´Ñ†Ðµ", price = 149, prep = 2.7, open = 1.7, clear = 1.3, emerge = 0.6, glow = "#ffd27a",
	glowColor = Color3.fromRGB(255, 210, 122), themeColor = Color3.fromRGB(255, 176, 46),
	pets = { "sand_jerboa", "amber_armadillo", "sun_lion_cub", "honey_griffin", "amber_basilisk" },
	order = { "base", "seg0", "inc0", "seg1", "inc1", "seg2", "inc2", "seg3", "inc3", "seg4", "inc4", "seg5", "inc5", "sun", "cap", "glow" },
	groups = {
		base = { 1, 0, 0, 0, 0, 0 },
		seg0 = { 1, 0, 0, 0, 0.18642678, 0.570182295 },
		inc0 = { 1, 0, 0, 0, 1.01357322, -0.570182295 },
		seg1 = { 0.5, 0, -0.866025404, 0.493792352, 0.18642678, 0.285091147 },
		inc1 = { 1, 0, 0, -0.493792352, 1.01357322, -0.285091147 },
		seg2 = { -0.5, 0, -0.866025404, 0.493792352, 0.18642678, -0.285091147 },
		inc2 = { 1, 0, 0, -0.493792352, 1.01357322, 0.285091147 },
		seg3 = { -1, 0, 0, 0, 0.18642678, -0.570182295 },
		inc3 = { 1, 0, 0, 0, 1.01357322, 0.570182295 },
		seg4 = { -0.5, 0, 0.866025404, -0.493792352, 0.18642678, -0.285091147 },
		inc4 = { 1, 0, 0, 0.493792352, 1.01357322, 0.285091147 },
		seg5 = { 0.5, 0, 0.866025404, -0.493792352, 0.18642678, 0.285091147 },
		inc5 = { 1, 0, 0, 0.493792352, 1.01357322, -0.285091147 },
		sun = { 1, 0, 0, 0, 0.872807909, 0.622828658 },
		cap = { 1, 0, 0, 0, 2.07, 0 },
		glow = { 1, 0, 0, 0, 1.15, 0 }
	},
	x = { n0 = { x = 0, y = -0.84755933, z = 0.530700652 }, n1 = { x = 0.459600247, y = -0.84755933, z = 0.265350326 }, n2 = { x = 0.459600247, y = -0.84755933, z = -0.265350326 }, n3 = { x = 0, y = -0.84755933, z = -0.530700652 }, n4 = { x = -0.459600247, y = -0.84755933, z = -0.265350326 }, n5 = { x = -0.459600247, y = -0.84755933, z = 0.265350326 } },
	events = {
		{ t = 0.25, type = "burst", color = Color3.fromRGB(255, 224, 138), count = 5, group = "seg0", note = "включение загорается: звёздочки у сегмента" },
		{ t = 0.45, type = "burst", color = Color3.fromRGB(255, 224, 138), count = 5, group = "seg1", note = "включение загорается: звёздочки у сегмента" },
		{ t = 0.65, type = "burst", color = Color3.fromRGB(255, 224, 138), count = 5, group = "seg2", note = "включение загорается: звёздочки у сегмента" },
		{ t = 0.85, type = "burst", color = Color3.fromRGB(255, 224, 138), count = 5, group = "seg3", note = "включение загорается: звёздочки у сегмента" },
		{ t = 1.05, type = "burst", color = Color3.fromRGB(255, 224, 138), count = 5, group = "seg4", note = "включение загорается: звёздочки у сегмента" },
		{ t = 1.25, type = "burst", color = Color3.fromRGB(255, 224, 138), count = 5, group = "seg5", note = "включение загорается: звёздочки у сегмента" },
		{ t = 1.3, type = "stream", color = Color3.fromRGB(255, 216, 106), count = 18, untilT = 3.1, note = "искры слетаются к яйцу, ~18 в секунду" },
		{ t = 1.5, type = "ring", color = Color3.fromRGB(255, 207, 90), count = 1, r0 = 0.45, r1 = 3.6, life = 1.1, note = "солнечное кольцо по полу" },
		{ t = 2, type = "ring", color = Color3.fromRGB(255, 240, 176), count = 1, r0 = 0.45, r1 = 4.5, life = 1.1, note = "второе солнечное кольцо" },
		{ t = 2.7, type = "flash", color = Color3.fromRGB(255, 210, 122), count = 1, life = 0.7, note = "вспышка света изнутри" },
		{ t = 2.82, type = "burst", color = Color3.fromRGB(255, 178, 58), count = 6, color2 = Color3.fromRGB(255, 217, 122), group = "seg0", note = "осколки янтаря от сегмента" },
		{ t = 2.82, type = "ring", color = Color3.fromRGB(255, 207, 90), count = 1, r0 = 0.15, r1 = 1.35, life = 0.5, group = "seg0", note = "малое кольцо под сегментом" },
		{ t = 2.96, type = "burst", color = Color3.fromRGB(255, 178, 58), count = 6, color2 = Color3.fromRGB(255, 217, 122), group = "seg3", note = "осколки янтаря от сегмента" },
		{ t = 2.96, type = "ring", color = Color3.fromRGB(255, 207, 90), count = 1, r0 = 0.15, r1 = 1.35, life = 0.5, group = "seg3", note = "малое кольцо под сегментом" },
		{ t = 3.1, type = "burst", color = Color3.fromRGB(255, 178, 58), count = 6, color2 = Color3.fromRGB(255, 217, 122), group = "seg1", note = "осколки янтаря от сегмента" },
		{ t = 3.1, type = "ring", color = Color3.fromRGB(255, 207, 90), count = 1, r0 = 0.15, r1 = 1.35, life = 0.5, group = "seg1", note = "малое кольцо под сегментом" },
		{ t = 3.24, type = "burst", color = Color3.fromRGB(255, 178, 58), count = 6, color2 = Color3.fromRGB(255, 217, 122), group = "seg4", note = "осколки янтаря от сегмента" },
		{ t = 3.24, type = "ring", color = Color3.fromRGB(255, 207, 90), count = 1, r0 = 0.15, r1 = 1.35, life = 0.5, group = "seg4", note = "малое кольцо под сегментом" },
		{ t = 3.38, type = "burst", color = Color3.fromRGB(255, 178, 58), count = 6, color2 = Color3.fromRGB(255, 217, 122), group = "seg2", note = "осколки янтаря от сегмента" },
		{ t = 3.38, type = "ring", color = Color3.fromRGB(255, 207, 90), count = 1, r0 = 0.15, r1 = 1.35, life = 0.5, group = "seg2", note = "малое кольцо под сегментом" },
		{ t = 3.52, type = "burst", color = Color3.fromRGB(255, 178, 58), count = 6, color2 = Color3.fromRGB(255, 217, 122), group = "seg5", note = "осколки янтаря от сегмента" },
		{ t = 3.52, type = "ring", color = Color3.fromRGB(255, 207, 90), count = 1, r0 = 0.15, r1 = 1.35, life = 0.5, group = "seg5", note = "малое кольцо под сегментом" },
	},
}, self)
end

-- ============ tide — Ð–ÐµÐ¼Ñ‡ÑƒÐ¶Ð¸Ð½Ð° Ð¿Ñ€Ð¸Ð»Ð¸Ð²Ð° ============
do
local self = {}
self.idle = function(e, t)
e.sc("glow", 0.01)
end
self.seq = function(e, t, c, fx, x0)
local P = self.prep
local o = (t - P)
local rnd = fx.rnd
local bub = (ss(0.1, 0.6, t) * (1 - ss(0.2, 1.2, o)))
if ((bub > 0) and (rnd() < ((0.4 * bub) + (0.3 * ss(1.6, P, t))))) then
local a = (rnd() * TAU)
local rr = (0.5 + (rnd() * 0.7))
fx.emit({tex = "bubble", p = {(x0 + (sin(a) * rr)), (0.1 + (rnd() * 0.5)), (cos(a) * rr)}, v = {0, (0.7 + (rnd() * 0.8)), 0}, life = (1.4 + rnd()), s = (0.08 + (rnd() * 0.14)), s1 = (0.2 + (rnd() * 0.1)), col = "#eaffff", sway = 0.5, a = 0.9})
end
e.sw = ((((0.1 * ss(0.3, 1.2, t)) + (0.08 * ss(1.6, P, t))) * sin(((t * 4.2) + (0.4 * sin((t * 1.7)))))) * (1 - ss(0, 0.25, o)))
local gl = (ss(0.8, P, t) * (1 - ss(0, 0.9, c)))
e.sc("glow", max(0.01, (0.7 + (0.3 * gl))))
e.x.gm.material.opacity = (0.55 * gl)
e.L = ((1.2 * gl) + (1.5 * bump(o, 0, 0.7)))
e.Lc.set(self.glow)
for k = 0, (8) - 1 do
local d = min(k, (8 - k))
local u = ((o - (d * 0.07)) / 0.7)
e.hinge(("cup" .. k), iff((u > 0), (1.25 * outBack(min(1, u))), ((0.05 * ss(1.8, P, t)) * (1 + sin(((t * 5) + (k * 0.8)))))))
local w = ss(0, 1, (c - (d * 0.05)))
e.sc(("cup" .. k), (1 - w))
end
if truthy(e.ev("spl", t, (P + 0.1))) then
fx.ring({x0, 0.05, 0}, "#bff7ee", 0.5, 2.6, 0.9, 0.8)
fx.ring({x0, 0.06, 0}, "#ffffff", 0.3, 1.8, 0.6, 0.7)
fx.burst(34, function(i, r)
local a = (r() * TAU)
local s = (1 + (r() * 1.6))
return {tex = "drop", p = {(x0 + (sin(a) * 0.8)), 0.4, (cos(a) * 0.8)}, v = {(sin(a) * s), (2.2 + (r() * 2.4)), (cos(a) * s)}, g = 7, life = (0.9 + (r() * 0.4)), s = (0.08 + (r() * 0.08)), col = iff((r() > 0.4), "#c8fff4", "#ffffff"), add = false, a = 0.9, floor = 0.03}
end)
end
for i = 3, 0, -1 do
local st = (0.15 + ((3 - i) * 0.2))
local u = ss(st, (st + 0.7), o)
e.mv(("r" .. i), 0, (u * (1.1 + (0.2 * i))), 0)
e.rot(("r" .. i), 0, (u * iff(truthy((i % 2)), 0.9, (-0.9))), 0)
e.sc(("r" .. i), (1 - ss(0.45, 1, u)))
if truthy(e.ev(("r" .. i), t, ((P + st) + 0.4))) then
fx.burst(10, function(j, r)
local a = (r() * TAU)
local rr = K.prof((0.45 + (i * 0.14))).r
return {tex = "bubble", p = {(x0 + (sin(a) * rr)), ((EH * (0.45 + (i * 0.14))) + 0.9), (cos(a) * rr)}, v = {(sin(a) * 0.4), (0.6 + (r() * 0.8)), (cos(a) * 0.4)}, life = (1 + (r() * 0.8)), s = (0.12 + (r() * 0.14)), s1 = 0.3, col = "#f4ffff", sway = 0.5}
end)
end
end
e.mv("low", 0, ((-0.45) * ss(0.2, 1.2, c)), 0)
e.sc("low", (1 - ss(0.3, 1.25, c)))
end
register("tide", {
	name = "Ð–ÐµÐ¼Ñ‡ÑƒÐ¶Ð¸Ð½Ð° Ð¿Ñ€Ð¸Ð»Ð¸Ð²Ð°", price = 299, prep = 2.7, open = 1.6, clear = 1.3, emerge = 0.6, glow = "#c8fff4",
	glowColor = Color3.fromRGB(200, 255, 244), themeColor = Color3.fromRGB(63, 214, 196),
	pets = { "bubble_crab", "coral_turtle", "pearl_axolotl", "tide_ray", "little_leviathan" },
	order = { "low", "cup0", "cup1", "cup2", "cup3", "cup4", "cup5", "cup6", "cup7", "r0", "r1", "r2", "r3", "glow" },
	groups = {
		low = { 1, 0, 0, 0, 0, 0 },
		cup0 = { 1, 0, 0, 0, 0.069, 0.397208933 },
		cup1 = { 0.707106781, 0, -0.707106781, 0.28086913, 0.069, 0.28086913 },
		cup2 = { 0, 0, -1, 0.397208933, 0.069, 0 },
		cup3 = { -0.707106781, 0, -0.707106781, 0.28086913, 0.069, -0.28086913 },
		cup4 = { -1, 0, 0, 0, 0.069, -0.397208933 },
		cup5 = { -0.707106781, 0, 0.707106781, -0.28086913, 0.069, -0.28086913 },
		cup6 = { 0, 0, 1, -0.397208933, 0.069, 0 },
		cup7 = { 0.707106781, 0, 0.707106781, -0.28086913, 0.069, 0.28086913 },
		r0 = { 1, 0, 0, 0, 0.851, 0 },
		r1 = { 1, 0, 0, 0, 1.219, 0 },
		r2 = { 1, 0, 0, 0, 1.587, 0 },
		r3 = { 1, 0, 0, 0, 1.909, 0 },
		glow = { 1, 0, 0, 0, 1.1, 0 }
	},
	x = { n0 = { x = 0, y = -0.939309056, z = 0.343072146 }, n1 = { x = 0.242588641, y = -0.939309056, z = 0.242588641 }, n2 = { x = 0.343072146, y = -0.939309056, z = 0 }, n3 = { x = 0.242588641, y = -0.939309056, z = -0.242588641 }, n4 = { x = 0, y = -0.939309056, z = -0.343072146 }, n5 = { x = -0.242588641, y = -0.939309056, z = -0.242588641 }, n6 = { x = -0.343072146, y = -0.939309056, z = 0 }, n7 = { x = -0.242588641, y = -0.939309056, z = 0.242588641 } },
	events = {
		{ t = 0.1, type = "stream", color = Color3.fromRGB(234, 255, 255), count = 24, untilT = 3.9, note = "пузырьки поднимаются вокруг яйца, ~24 в секунду" },
		{ t = 2.7, type = "flash", color = Color3.fromRGB(200, 255, 244), count = 1, life = 0.7, note = "вспышка света изнутри" },
		{ t = 2.8, type = "ring", color = Color3.fromRGB(191, 247, 238), count = 1, r0 = 0.75, r1 = 3.9, life = 0.9, note = "всплеск: кольцо по полу" },
		{ t = 2.8, type = "ring", color = Color3.fromRGB(255, 255, 255), count = 1, r0 = 0.45, r1 = 2.7, life = 0.6, note = "всплеск: второе кольцо" },
		{ t = 2.8, type = "burst", color = Color3.fromRGB(200, 255, 244), count = 34, color2 = Color3.fromRGB(255, 255, 255), note = "брызги вверх, падают на пол" },
		{ t = 3.25, type = "burst", color = Color3.fromRGB(244, 255, 255), count = 10, group = "r3", note = "жемчужный ряд лопается пузырями" },
		{ t = 3.45, type = "burst", color = Color3.fromRGB(244, 255, 255), count = 10, group = "r2", note = "жемчужный ряд лопается пузырями" },
		{ t = 3.65, type = "burst", color = Color3.fromRGB(244, 255, 255), count = 10, group = "r1", note = "жемчужный ряд лопается пузырями" },
		{ t = 3.85, type = "burst", color = Color3.fromRGB(244, 255, 255), count = 10, group = "r0", note = "жемчужный ряд лопается пузырями" },
	},
}, self)
end

-- ============ storm — Ð¡ÐµÑ€Ð´Ñ†Ðµ Ð³Ñ€Ð¾Ð·Ñ‹ ============
do
local self = {}
self.idle = function(e, t)
e.sc("glow", 0.01)
e.x.cm.opacity = (0.75 + (0.25 * sin((t * 3))))
end
self.seq = function(e, t, c, fx, x0)
local P = self.prep
local o = (t - P)
local rnd = fx.rnd
local cp = e.x.cp
local pt = function(i)
return {(x0 + cp[(i) + 1].x), cp[(i) + 1].y, cp[(i) + 1].z}
end
local rate = (0.04 + (0.3 * ss(0.2, P, t)))
e.x.cm.opacity = iff((t <= 0), 1, (0.6 + ((0.4 * sin((t * 30))) * ss(0, 1, t))))
e.sc("crack", (1 - ss(0.1, 0.5, o)), 1, (1 - ss(0.1, 0.5, o)))
if (((t > 0.15) and (o < 0.3)) and (rnd() < rate)) then
local i = math.floor((rnd() * (#cp - 2)))
local j = min((#cp - 1), ((i + 1) + math.floor((rnd() * 3))))
fx.bolt(pt(i), pt(j), "#bfeaff", 0.1, 0.022, 0.3)
if (rnd() < 0.5) then
local p = pt(j)
fx.emit({tex = "star", p = p, v = {((rnd() - 0.5) * 1.5), (rnd() * 1.5), (0.6 + rnd())}, g = 3, life = 0.4, s = 0.14, s1 = 0.02, col = "#d8f2ff"})
end
end
if truthy(orv(e.ev("run", t, 0.5), e.ev("run2", t, 1.1))) then
for i = 0, ((#cp - 1)) - 1 do
fx.bolt(pt(i), pt((i + 1)), "#ffffff", 0.22, 0.035, 0.25)
end
end
local gl = (ss(0.6, P, t) * (1 - ss(0, 0.9, c)))
e.sc("glow", max(0.01, ((0.7 + (0.3 * gl)) + (0.05 * sin((t * 23))))))
e.x.gm.material.opacity = (0.5 * gl)
e.L = ((gl * (1 + (0.5 * sin((t * 31))))) + (3 * bump(o, 0, 0.35)))
e.Lc.set(self.glow)
for j = 0, (6) - 1 do
local k = ({0, 5, 1, 4, 2, 3})[(j) + 1]
local t0 = (1.35 + (j * 0.2))
local u = ss(t0, (t0 + 0.5), t)
local n = e.x[("nc" .. k)]
e.mv(("cl" .. k), (n.x * (0.9 * u)), ((((-1.3) * u) * u) + (0.3 * sin((u * PI)))), (n.z * (0.9 * u)))
e.hinge(("cl" .. k), ((-2.5) * u))
e.sc(("cl" .. k), (1 - ss(0.7, 1, u)))
if truthy(e.ev(("c" .. k), t, t0)) then
local p = {(x0 + (n.x * 1.0)), 1.15, (n.z * 1.0)}
fx.bolt(p, {(p[1] + (n.x * 0.6)), 1.5, (p[3] + (n.z * 0.6))}, "#e6f6ff", 0.14, 0.03, 0.4)
fx.burst(7, function(i, r)
return {tex = "star", p = p, v = {((n.x * (1 + (r() * 2))) + (r() - 0.5)), (r() * 2.4), ((n.z * (1 + (r() * 2))) + (r() - 0.5))}, g = 6, life = (0.5 + (r() * 0.3)), s = 0.13, s1 = 0.02, col = "#cfeeff"}
end)
end
end
local cv = ss(1.3, 2.4, t)
e.mv("chev", 0, ((-0.2) * cv), (0.5 * cv))
e.sc("chev", (1 - ss(0.5, 1, cv)))
if truthy(e.ev("thun", t, P)) then
fx.ring({x0, 0.05, 0}, "#9fd8ff", 0.4, 3.0, 0.7, 0.9)
for k = 0, (6) - 1 do
local n = e.x[("nu" .. k)]
fx.bolt({x0, 1.2, 0}, {(x0 + (n.x * 2.2)), ((1.2 + (n.y * 2)) + iff(truthy((k % 2)), 0.8, (-0.5))), (n.z * 2.2)}, "#ffffff", 0.2, 0.04, 0.2)
end
end
e.mv("top", 0, kf(o, 0, 0, 0.4, 0.6, 1.4, 1.9), 0)
e.rot("top", 0, (max(0, o) * 1.5), 0)
e.sc("top", (1 - ss(0.8, 1.5, o)))
for k = 0, (6) - 1 do
local u = outBack(ss((0.05 + (k * 0.05)), (0.75 + (k * 0.05)), o))
local hv = ((0.03 * sin(((t * 3) + k))) * u)
local w = ss(0, 1, (c - (k * 0.05)))
local n = e.x[("nu" .. k)]
e.mv(("up" .. k), (n.x * ((0.5 * u) + (0.6 * w))), (((0.34 * u) + hv) + (0.5 * w)), (n.z * ((0.5 * u) + (0.6 * w))))
e.sc(("up" .. k), (1 - w))
n = e.x[("nl" .. k)]
e.mv(("lo" .. k), (n.x * ((0.45 * u) + (0.6 * w))), ((((-0.06) * u) - (hv * 0.5)) - (0.2 * w)), (n.z * ((0.45 * u) + (0.6 * w))))
e.sc(("lo" .. k), (1 - w))
if (((o > 0.3) and (c < 0.4)) and (rnd() < 0.06)) then
local a = e.x[("nu" .. k)]
local b = e.x[("nl" .. ((k + 1) % 6))]
fx.bolt({(x0 + (a.x * 1.5)), 1.9, (a.z * 1.5)}, {(x0 + (b.x * 1.5)), 0.7, (b.z * 1.5)}, "#bfeaff", 0.1, 0.02, 0.25)
end
end
e.mv("base", 0, ((-0.4) * ss(0.3, 1.2, c)), 0)
e.sc("base", (1 - ss(0.4, 1.25, c)))
end
register("storm", {
	name = "Ð¡ÐµÑ€Ð´Ñ†Ðµ Ð³Ñ€Ð¾Ð·Ñ‹", price = 599, prep = 2.8, open = 1.6, clear = 1.3, emerge = 0.6, glow = "#9fd8ff",
	glowColor = Color3.fromRGB(159, 216, 255), themeColor = Color3.fromRGB(63, 169, 255),
	pets = { "spark_salamander", "cloud_lamb", "storm_falcon", "storm_dragon", "sky_kitsune" },
	order = { "base", "lo0", "up0", "cl0", "lo1", "up1", "cl1", "lo2", "up2", "cl2", "lo3", "up3", "cl3", "lo4", "up4", "cl4", "lo5", "up5", "cl5", "chev", "top", "cryst", "crack", "glow" },
	groups = {
		base = { 1, 0, 0, 0, 0, 0 },
		lo0 = { 1, 0, 0, 0.485019812, 0.69, 0.840078956 },
		up0 = { 1, 0, 0, 0.424232071, 1.564, 0.734791502 },
		cl0 = { 0.866025404, 0, -0.5, 0.519573575, 1.160080409, 0.89992783 },
		lo1 = { 1, 0, 0, 0.970039623, 0.69, 0 },
		up1 = { 1, 0, 0, 0.848464143, 1.564, 0 },
		cl1 = { 0, 0, -1, 1.03914715, 1.160080409, 0 },
		lo2 = { 1, 0, 0, 0.485019812, 0.69, -0.840078956 },
		up2 = { 1, 0, 0, 0.424232071, 1.564, -0.734791502 },
		cl2 = { -0.866025404, 0, -0.5, 0.519573575, 1.160080409, -0.89992783 },
		lo3 = { 1, 0, 0, -0.485019812, 0.69, -0.840078956 },
		up3 = { 1, 0, 0, -0.424232071, 1.564, -0.734791502 },
		cl3 = { -0.866025404, 0, 0.5, -0.519573575, 1.160080409, -0.89992783 },
		lo4 = { 1, 0, 0, -0.970039623, 0.69, 0 },
		up4 = { 1, 0, 0, -0.848464143, 1.564, 0 },
		cl4 = { 0, 0, 1, -1.03914715, 1.160080409, 0 },
		lo5 = { 1, 0, 0, -0.485019812, 0.69, 0.840078956 },
		up5 = { 1, 0, 0, -0.424232071, 1.564, 0.734791502 },
		cl5 = { 0.866025404, 0, 0.5, -0.519573575, 1.160080409, 0.89992783 },
		chev = { 1, 0, 0, 0, 0.268703159, 0.837689301 },
		top = { 1, 0, 0, 0, 2.047, 0 },
		cryst = { 1, 0, 0, 0, 0.253, 0 },
		crack = { 1, 0, 0, 0, 1.15, 0 },
		glow = { 1, 0, 0, 0, 1.15, 0 }
	},
	x = { nl0 = { x = 0.485581938, y = -0.238412929, z = 0.841052588 }, nu0 = { x = 0.4535249, y = 0.421023347, z = 0.78552817 }, nc0 = { x = 0.492892917, y = 0.168006818, z = 0.853715574 }, nl1 = { x = 0.971163877, y = -0.238412929, z = 0 }, nu1 = { x = 0.907049801, y = 0.421023347, z = 0 }, nc1 = { x = 0.985785833, y = 0.168006818, z = 0 }, nl2 = { x = 0.485581938, y = -0.238412929, z = -0.841052588 }, nu2 = { x = 0.4535249, y = 0.421023347, z = -0.78552817 }, nc2 = { x = 0.492892917, y = 0.168006818, z = -0.853715574 }, nl3 = { x = -0.485581938, y = -0.238412929, z = -0.841052588 }, nu3 = { x = -0.4535249, y = 0.421023347, z = -0.78552817 }, nc3 = { x = -0.492892917, y = 0.168006818, z = -0.853715574 }, nl4 = { x = -0.971163877, y = -0.238412929, z = 0 }, nu4 = { x = -0.907049801, y = 0.421023347, z = 0 }, nc4 = { x = -0.985785833, y = 0.168006818, z = 0 }, nl5 = { x = -0.485581938, y = -0.238412929, z = 0.841052588 }, nu5 = { x = -0.4535249, y = 0.421023347, z = 0.78552817 }, nc5 = { x = -0.492892917, y = 0.168006818, z = 0.853715574 }, cp = { { x = 0, y = 2.244333986, z = 0.65886745 }, { x = 0.064484747, y = 1.925181704, z = 0.919705538 }, { x = -0.031229262, y = 1.717052815, z = 1.0406631 }, { x = 0.103309244, y = 1.45602767, z = 1.144779536 }, { x = -0.06030149, y = 1.244002528, z = 1.205024609 }, { x = 0.074250525, y = 0.972161458, z = 1.236023376 }, { x = -0.072143833, y = 0.632780897, z = 1.200953989 }, { x = 0.032566969, y = 0.339658387, z = 1.08523995 }, { x = -0.016689139, y = 0.044623858, z = 0.834345666 } } },
	events = {
		{ t = 0.15, type = "stream", color = Color3.fromRGB(191, 234, 255), count = 12, untilT = 3.1, group = "crack", note = "короткие разряды по шву, частота растёт от ~2 до ~20 в секунду" },
		{ t = 0.5, type = "bolt", color = Color3.fromRGB(255, 255, 255), count = 8, group = "crack", life = 0.22, note = "разряд пробегает по всему шву" },
		{ t = 1.1, type = "bolt", color = Color3.fromRGB(255, 255, 255), count = 8, group = "crack", life = 0.22, note = "второй разряд по всему шву" },
		{ t = 1.35, type = "bolt", color = Color3.fromRGB(230, 246, 255), count = 1, group = "cl0", life = 0.14, note = "разряд от скобы" },
		{ t = 1.35, type = "burst", color = Color3.fromRGB(207, 238, 255), count = 7, group = "cl0", note = "искры от освободившейся скобы" },
		{ t = 1.55, type = "bolt", color = Color3.fromRGB(230, 246, 255), count = 1, group = "cl5", life = 0.14, note = "разряд от скобы" },
		{ t = 1.55, type = "burst", color = Color3.fromRGB(207, 238, 255), count = 7, group = "cl5", note = "искры от освободившейся скобы" },
		{ t = 1.75, type = "bolt", color = Color3.fromRGB(230, 246, 255), count = 1, group = "cl1", life = 0.14, note = "разряд от скобы" },
		{ t = 1.75, type = "burst", color = Color3.fromRGB(207, 238, 255), count = 7, group = "cl1", note = "искры от освободившейся скобы" },
		{ t = 1.95, type = "bolt", color = Color3.fromRGB(230, 246, 255), count = 1, group = "cl4", life = 0.14, note = "разряд от скобы" },
		{ t = 1.95, type = "burst", color = Color3.fromRGB(207, 238, 255), count = 7, group = "cl4", note = "искры от освободившейся скобы" },
		{ t = 2.15, type = "bolt", color = Color3.fromRGB(230, 246, 255), count = 1, group = "cl2", life = 0.14, note = "разряд от скобы" },
		{ t = 2.15, type = "burst", color = Color3.fromRGB(207, 238, 255), count = 7, group = "cl2", note = "искры от освободившейся скобы" },
		{ t = 2.35, type = "bolt", color = Color3.fromRGB(230, 246, 255), count = 1, group = "cl3", life = 0.14, note = "разряд от скобы" },
		{ t = 2.35, type = "burst", color = Color3.fromRGB(207, 238, 255), count = 7, group = "cl3", note = "искры от освободившейся скобы" },
		{ t = 2.8, type = "flash", color = Color3.fromRGB(159, 216, 255), count = 1, life = 0.35, note = "вспышка грома, яркость ×3" },
		{ t = 2.8, type = "ring", color = Color3.fromRGB(159, 216, 255), count = 1, r0 = 0.6, r1 = 4.5, life = 0.7, note = "ударное кольцо по полу" },
		{ t = 2.8, type = "bolt", color = Color3.fromRGB(255, 255, 255), count = 6, life = 0.2, note = "шесть разрядов из центра к сегментам брони" },
		{ t = 3.1, type = "stream", color = Color3.fromRGB(191, 234, 255), count = 20, untilT = 5.336, note = "разряды между раздвинутыми сегментами, ~20 в секунду" },
	},
}, self)
end

-- ============ astral — ÐÑÑ‚Ñ€Ð°Ð»ÑŒÐ½Ð¾Ðµ ÑÐ´Ñ€Ð¾ ============
do
local self = {}
self.rings = function(e, t, al, sp, sc)
local p = e.parts
p.ringA.g.rotation.set(((0.2 * (1 - al)) + 0.0), (sp * 1.0), (0.28 * (1 - al)), "YXZ")
p.ringB.g.rotation.set(((-0.08) * (1 - al)), ((-sp) * 0.7), ((-0.1) * (1 - al)), "YXZ")
p.ringA.g.position.y = (p.ringA.p0.y - (0.37 * al))
p.ringB.g.position.y = (p.ringB.p0.y + (0.23 * al))
e.sc("ringA", (sc * (1 + (0.16 * al))))
e.sc("ringB", sc)
end
self.idle = function(e, t)
self.rings(e, t, 0, (t * 0.25), 1)
e.sc("glow", 0.01)
e.sc("core", 0.6)
end
self.seq = function(e, t, c, fx, x0)
local P = self.prep
local o = (t - P)
local rnd = fx.rnd
local al = ss(0.3, 1.8, t)
local sp = (((t * 0.25) + ((1.4 * ss(0.8, P, t)) * t)) + (max(0, o) * 3))
local rs = ((1 + (0.25 * outBack(ss(0, 0.8, o)))) + (1.6 * ss(0, 1.1, c)))
self.rings(e, t, al, sp, (rs * (1 - ss(0.5, 1.3, c))))
if truthy(e.ev("al", t, 1.8)) then
fx.ring({x0, 1.15, 0}, "#e9dcff", 1.0, 2.2, 0.8, 0.6)
fx.burst(16, function(i, r)
local a = ((i / 16) * TAU)
return {tex = "star", p = {(x0 + (sin(a) * 1.2)), 1.15, (cos(a) * 1.2)}, v = {(sin(a) * 0.5), ((r() - 0.5) * 0.3), (cos(a) * 0.5)}, life = 1, s = 0.16, s1 = 0.02, col = "#fff1c8"}
end)
end
if (((t > 0.4) and (c < 0.6)) and (rnd() < 0.22)) then
local a = (rnd() * TAU)
local rr = (1.3 + (rnd() * 0.9))
fx.emit({tex = "star", p = {(x0 + (sin(a) * rr)), (0.3 + (rnd() * 1.9)), (cos(a) * rr)}, v = {((-sin(a)) * 0.25), 0, ((-cos(a)) * 0.25)}, life = 1.3, s = (0.05 + (rnd() * 0.12)), s1 = 0.01, col = iff((rnd() > 0.5), "#ffffff", "#c9b6ff")})
end
local gl = (ss(0.8, P, t) * (1 - ss(0.1, 1, c)))
e.sc("glow", max(0.01, ((0.8 + (0.35 * gl)) + (0.04 * sin((t * 6))))))
e.x.gm.material.opacity = (0.5 * gl)
e.L = ((1.3 * gl) + (2 * bump(o, 0, 0.8)))
e.Lc.set(self.glow)
e.mv("cap", 0, (kf(o, 0, 0, 0.5, 0.5, 1.6, 1.3) + (0.04 * sin((t * 2)))), 0)
e.rot("cap", (0.3 * ss(0, 1.5, o)), (max(0, o) * 0.8), 0)
e.sc("cap", (1 - ss(0.2, 1, c)))
local pre = ss(2.0, P, t)
forEach(e.x.f, function(f, i)
local u = outBack(ss(((0.05 + (f.ti * 0.16)) + (f.k * 0.03)), ((0.95 + (f.ti * 0.16)) + (f.k * 0.03)), o))
local d = (((0.05 * pre) * (1 + (0.3 * sin(((t * 5) + i))))) + (u * (0.5 + (0.1 * f.ti))))
local hv = ((u * 0.06) * sin(((t * 1.7) + (i * 1.3))))
local w = ss(0, 1, (c - (0.03 * i)))
local ang = (((u * 0.25) * iff(truthy((f.ti % 2)), 1, (-1))) + ((w * w) * 2.6))
e.orbit(f.n, ang, ((d + (w * 0.5)) / max(0.35, hypot(e.parts[f.n].p0.x, e.parts[f.n].p0.z))), ((((f.ny * d) * 1.1) + hv) + (w * 0.5)))
local g = e.parts[f.n].g
g.rotation.x = (((u * 0.3) * sin((i * 2.1))) + (hv * 2))
g.rotation.z = ((u * 0.3) * cos((i * 1.7)))
e.sc(f.n, (1 - w))
end)
if truthy(e.ev("split", t, (P + 0.1))) then
fx.ring({x0, 1.15, 0}, "#ffffff", 0.4, 2.8, 1.0, 0.7)
fx.burst(30, function(i, r)
local a = (r() * TAU)
local b = ((r() - 0.5) * 2)
return {tex = "star", p = {x0, 1.15, 0}, v = {(sin(a) * (1 + (r() * 1.6))), (b * 1.4), (cos(a) * (1 + (r() * 1.6)))}, drag = 1.2, life = (1.2 + r()), s = (0.1 + (r() * 0.12)), s1 = 0.01, col = iff((r() > 0.5), "#fff1c8", "#c9b6ff")}
end)
end
local cs = (((0.6 + (0.25 * ss(1.5, P, t))) + (0.5 * outBack(ss(0.1, 0.9, o)))) * (1 + (0.05 * sin((t * 7)))))
e.sc("core", (cs * (1 - ss(((self.open * self.emerge) + 0.05), ((self.open * self.emerge) + 0.8), o))))
e.parts.core.g.rotation.set((t * 0.7), (t * 1.1), 0)
end
register("astral", {
	name = "ÐÑÑ‚Ñ€Ð°Ð»ÑŒÐ½Ð¾Ðµ ÑÐ´Ñ€Ð¾", price = 999, prep = 3, open = 1.8, clear = 1.4, emerge = 0.62, glow = "#e9dcff",
	glowColor = Color3.fromRGB(233, 220, 255), themeColor = Color3.fromRGB(169, 139, 255),
	pets = { "comet_kitten", "moon_owlet", "nebula_moth", "eclipse_dragon", "astral_phoenix" },
	order = { "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "f13", "cap", "ringA", "ringB", "core", "glow" },
	groups = {
		f0 = { 1, 0, 0, 0, 0.4485, 0.871292898 },
		f1 = { 1, 0, 0, 0.828648788, 0.4485, 0.269244313 },
		f2 = { 1, 0, 0, 0.512133116, 0.4485, -0.704890762 },
		f3 = { 1, 0, 0, -0.512133116, 0.4485, -0.704890762 },
		f4 = { 1, 0, 0, -0.828648788, 0.4485, 0.269244313 },
		f5 = { 1, 0, 0, 0.551025987, 1.173, 0.805432452 },
		f6 = { 1, 0, 0, 0.936288176, 1.173, -0.27516454 },
		f7 = { 1, 0, 0, 0.027631929, 1.173, -0.975493491 },
		f8 = { 1, 0, 0, -0.919210705, 1.173, -0.327723593 },
		f9 = { 1, 0, 0, -0.595735388, 1.173, 0.772949171 },
		f10 = { 1, 0, 0, 0.206239731, 1.8285, 0.666716982 },
		f11 = { 1, 0, 0, 0.666716982, 1.8285, -0.206239731 },
		f12 = { 1, 0, 0, -0.206239731, 1.8285, -0.666716982 },
		f13 = { 1, 0, 0, -0.666716982, 1.8285, 0.206239731 },
		cap = { 1, 0, 0, 0, 2.139, 0 },
		ringA = { 1, 0, 0, 0, 1.52, 0 },
		ringB = { 1, 0, 0, 0, 0.92, 0 },
		core = { 1, 0, 0, 0, 1.15, 0 },
		glow = { 1, 0, 0, 0, 1.15, 0 }
	},
	x = { f = { { n = "f0", nx = 0, ny = -0.515166893, nz = 0.857089886, ti = 0, k = 0 }, { n = "f1", nx = 0.815140921, ny = -0.515166893, nz = 0.26485534, ti = 0, k = 1 }, { n = "f2", nx = 0.503784795, ny = -0.515166893, nz = -0.693400283, ti = 0, k = 2 }, { n = "f3", nx = -0.503784795, ny = -0.515166893, nz = -0.693400283, ti = 0, k = 3 }, { n = "f4", nx = -0.815140921, ny = -0.515166893, nz = 0.26485534, ti = 0, k = 4 }, { n = "f5", nx = 0.554983997, ny = 0.18416935, nz = 0.811217859, ti = 1, k = 0 }, { n = "f6", nx = 0.943013517, ny = 0.18416935, nz = -0.277141042, ti = 1, k = 1 }, { n = "f7", nx = 0.027830409, ny = 0.18416935, nz = -0.982500442, ti = 1, k = 2 }, { n = "f8", nx = -0.925813379, ny = 0.18416935, nz = -0.330077625, ti = 1, k = 3 }, { n = "f9", nx = -0.600014544, ny = 0.18416935, nz = 0.778501251, ti = 1, k = 4 }, { n = "f10", nx = 0.243592005, ny = 0.566179375, nz = 0.78746673, ti = 2, k = 0 }, { n = "f11", nx = 0.78746673, ny = 0.566179375, nz = -0.243592005, ti = 2, k = 1 }, { n = "f12", nx = -0.243592005, ny = 0.566179375, nz = -0.78746673, ti = 2, k = 2 }, { n = "f13", nx = -0.78746673, ny = 0.566179375, nz = 0.243592005, ti = 2, k = 3 } } },
	events = {
		{ t = 0.4, type = "stream", color = Color3.fromRGB(255, 255, 255), count = 13, color2 = Color3.fromRGB(201, 182, 255), untilT = 5.892, note = "звёздочки вокруг яйца, ~13 в секунду" },
		{ t = 1.8, type = "ring", color = Color3.fromRGB(233, 220, 255), count = 1, r0 = 1.5, r1 = 3.3, life = 0.8, height = 1.725, note = "кольца выровнялись: кольцо на высоте ядра" },
		{ t = 1.8, type = "burst", color = Color3.fromRGB(255, 241, 200), count = 16, height = 1.725, note = "звёзды по кругу" },
		{ t = 3, type = "flash", color = Color3.fromRGB(233, 220, 255), count = 1, life = 0.8, note = "вспышка света, яркость ×2" },
		{ t = 3.1, type = "ring", color = Color3.fromRGB(255, 255, 255), count = 1, r0 = 0.6, r1 = 4.2, life = 1, height = 1.725, note = "скорлупа разделилась: кольцо от ядра" },
		{ t = 3.1, type = "burst", color = Color3.fromRGB(255, 241, 200), count = 30, color2 = Color3.fromRGB(201, 182, 255), height = 1.725, note = "звёзды во все стороны от ядра" },
	},
}, self)
end

return EggOpenings
