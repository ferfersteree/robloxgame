--!nonstrict
-- StarterPlayerScripts/Client/PetAnim (V36)
-- Animations of the pet models from the pack (custom Motor6D rigs, front = -Z, bones are world aligned at rest).
-- The pack has no animation clips, so everything is driven by writing Motor6D.Transform every frame.
--
--   idle   breathing, a look around, ear flicks, tail sway          (loops)
--   move   walk / flap / paddle cycle, the stage moves the pet      (loops); anim:setSpeed(v) scales rate and stride
--   sit    haunches down, front legs straight, tail sways, breathing (loops, поверх idle)
--   react  jump with a spin, ears and limbs wave                    (Claude Design prototype, ~1.1-1.6 s)
--   hatch  pecking from inside, jump out of the egg, landing        (Claude Design prototype, 2.7-5 s)
--
-- Whole-body motion of hatch/react (height, spin, scale) is the real root curve of each pet baked from the prototype
-- (PetAnimData, 30 Hz). Limbs are chosen by the joint NAME (Ear, Tail, Wing, Fore, Hind, Leg, Antenna ...), because the
-- joints of the pack differ from the prototype's, and are clamped to the limits stored in the model (SourceDefinition).
local HttpService = game:GetService("HttpService")

local Data = require(script.Parent.PetAnimData)

local PI, TAU = math.pi, math.pi * 2
local sin, cos, abs, max, min, clamp = math.sin, math.cos, math.abs, math.max, math.min, math.clamp

local PetAnim = {}
PetAnim.__index = PetAnim
PetAnim.data = Data

---------------------------------------------------------------------
-- curve helpers (same shape functions as the prototype)
---------------------------------------------------------------------
local function ss(a: number, b: number, x: number): number
	local t = clamp((x - a) / (b - a), 0, 1)
	return t * t * (3 - 2 * t)
end
local function wave(t: number, f: number, ph: number?): number
	return sin(TAU * (t * f + (ph or 0)))
end
local function pulse(t: number, period: number, dur: number, off: number?): number
	local x = (((t + (off or 0)) % period) + period) % period
	return x < dur and sin(PI * x / dur) or 0
end
local function bump(u: number, a: number, b: number): number
	if u <= a or u >= b then
		return 0
	end
	return sin(PI * (u - a) / (b - a))
end
-- smoothed keys: kf(u, u0, v0, u1, v1, ...)
local function kf(u: number, ...: number): number
	local k = { ... }
	if u <= k[1] then
		return k[2]
	end
	for i = 3, #k, 2 do
		if u <= k[i] then
			local t = (u - k[i - 2]) / math.max(1e-6, k[i] - k[i - 2])
			t = t * t * (3 - 2 * t)
			return k[i - 1] + (k[i + 1] - k[i - 1]) * t
		end
	end
	return k[#k]
end

local function sample(arr: { number }?, u: number, dur: number, default: number): number
	if not arr then
		return default
	end
	local n = #arr
	if n == 0 then
		return default
	end
	local f = clamp(u / dur, 0, 1) * (n - 1)
	local i = math.floor(f)
	local a = arr[i + 1]
	local b = arr[min(i + 2, n)]
	return a + (b - a) * (f - i)
end

---------------------------------------------------------------------
-- joint roles
---------------------------------------------------------------------
local function sideOf(n: string): number
	if n:find("Left") or n:find("_L_") or n:find("[a-z]L[A-Z0-9_]") or n:find("[a-z]L$") then
		return -1
	end
	if n:find("Right") or n:find("_R_") or n:find("[a-z]R[A-Z0-9_]") or n:find("[a-z]R$") then
		return 1
	end
	return 0
end

local function roleOf(name: string): string
	local l = name:lower()
	if l:find("^body") then
		return "body"
	elseif l:find("^abdomen") then
		return "abdomen"
	elseif l:find("^neck") or l:find("^spine") then
		return "neck"
	elseif l:find("^head") then
		return "head"
	elseif l:find("ear") and not l:find("wear") then
		return "ear"
	elseif l:find("antenna") then
		return "ant"
	elseif l:find("^eye") then
		return "eye"
	elseif l:find("tail") or l:find("fluke") then
		return "tail"
	elseif l:find("wing") or l:find("^shell") then
		return "wing"
	elseif l:find("flipper") or l:find("pectoral") then
		return "flipper"
	elseif l:find("^leg") and name:find("%d") then
		return "sleg" -- insect / crab legs: swing sideways
	elseif l:find("^fore") or l:find("^arm") or l:find("^hand") or l:find("^tinyarm") or l:find("^tinypaw") or l:find("claw") or l:find("^front") then
		return "fore"
	elseif l:find("^hind") or l:find("^haunch") or l:find("^leg") or l:find("^foot") or l:find("^long") or l:find("^rear") or l:find("thigh") then
		return "hind"
	elseif l:find("gill") or l:find("cephalic") or l:find("antler") or l:find("crest") or l:find("frill") or l:find("flower") or l:find("sprout") or l:find("crown") or l:find("acorn") or l:find("sun") or l:find("moon") or l:find("orbit") then
		return "deco"
	end
	return "deco"
end

local function distal(name: string): boolean
	return name:find("Lower") ~= nil or name:find("Paw") ~= nil or name:find("Foot") ~= nil or name:find("Talons") ~= nil
		or name:find("Hoof") ~= nil or name:find("Finger") ~= nil or name:find("Tip") ~= nil or name:find("Mid") ~= nil
		or name:find("Shin") ~= nil
end

---------------------------------------------------------------------
-- construction
---------------------------------------------------------------------
-- model: a pet model of the pack (Rig folder with Motor6D joints). id: key in PetAnimData (default model.Name / PetId)
function PetAnim.new(model: Model, id: string?)
	local self = setmetatable({}, PetAnim)
	self.model = model
	self.id = id or model:GetAttribute("PetId") or model.Name:gsub("_Building$", "")
	self.d = Data[self.id]
	self.joints = {}
	self.mode = "idle"
	self.wm = 0 -- weight of the move cycle
	self.t = math.random() * 5
	self.mt = 0
	self.ru = -1 -- react progress 0..1
	self.hu = -1 -- hatch progress 0..1
	self.ts = 1
	self.ws = 0 -- вес позы sit
	self.spd = nil -- скорость питомца, студ/с (nil: старое поведение, фиксированный темп)
	self.sp = 0 -- сглаженная скорость
	self.amp = 1
	self.cph = 0 -- фаза шага (циклы)
	self.fph = math.random() -- фаза взмаха крыльев (циклы)
	self.hover = false -- летает / парит: ноги подобраны, крылья машут и на месте

	local limits = {}
	for _, c in model:GetChildren() do
		if c:IsA("StringValue") and c.Value:sub(1, 1) == "{" then
			local ok, def = pcall(HttpService.JSONDecode, HttpService, c.Value)
			if ok and type(def) == "table" and type(def.groups) == "table" then
				for _, g in def.groups do
					limits[g.name] = g.limits
				end
			end
		end
	end

	local byName = {}
	for _, m in model:GetDescendants() do
		if m:IsA("Motor6D") then
			local nm = m.Name:gsub("_Joint$", "")
			local j = { m = m, name = nm, role = roleOf(nm), side = sideOf(nm), dist = distal(nm), depth = 0, limits = limits[nm] }
			j.idx = tonumber(nm:match("(%d+)$")) or 0
			j.acc = { 0, 0, 0, 0, 0, 0 }
			table.insert(self.joints, j)
			byName[m.Part1 and m.Part1.Name or nm] = j
			j.p1 = m.Part1
		end
	end
	-- chain depth (tail segments lag behind each other, distal limb parts follow their parent)
	for _, j in self.joints do
		local d = 0
		local p = j.m.Part0
		while p and byName[p.Name] and d < 8 do
			if byName[p.Name].role == j.role then
				d += 1
			end
			p = byName[p.Name].m.Part0
		end
		j.depth = d
		-- hip index among the same-role joints (alternates the leg phase)
	end
	local sleg = 0
	for _, j in self.joints do
		if j.role == "sleg" then
			sleg += 1
			j.k = sleg
		end
	end
	self.flyer = false
	for _, j in self.joints do
		if j.name:find("Wing") then
			self.flyer = true
		end
	end
	self.h = 3
	local okB, _, size = pcall(function()
		return model:GetBoundingBox()
	end)
	if okB and size then
		self.h = size.Y
	end
	self.baseScale = model:GetScale()
	self.root = { x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0, s = 1 }
	return self
end

function PetAnim:setMode(m: string)
	self.mode = m
end

-- v: скорость питомца в студах/с (nil: сбросить на фиксированный темп)
function PetAnim:setSpeed(v: number?)
	self.spd = v
end

-- парит или летит: ноги не шагают, крылья машут и на месте
function PetAnim:setHover(on: boolean)
	self.hover = on == true
end

function PetAnim:react()
	if self.hu < 0 and self.ru < 0 then
		self.ru = 0
	end
end

function PetAnim:hatch()
	self.hu = 0
	self.ru = -1
	self.wm = 0
	self.mode = "idle"
end

function PetAnim:hatching(): boolean
	return self.hu >= 0
end

function PetAnim:duration(): number
	return self.d and self.d.hd or 2.7
end

---------------------------------------------------------------------
-- layers: every function ADDS into j.acc = {rx, ry, rz, px, py, pz}
---------------------------------------------------------------------
local function addR(j, x: number, y: number, z: number, w: number)
	local a = j.acc
	a[1] += x * w
	a[2] += y * w
	a[3] += z * w
end
local function addP(j, x: number, y: number, z: number, w: number)
	local a = j.acc
	a[4] += x * w
	a[5] += y * w
	a[6] += z * w
end

-- outward tilt of a side part around Z: right side (+X) leans away with negative... see note in the file header
local function out(j, v: number): number
	return -j.side * v
end

function PetAnim:_idle(t: number, w: number)
	local h = self.h / 3
	for _, j in self.joints do
		local r, s = j.role, j.side
		local ph = j.idx * 0.37 + (s > 0 and 0.2 or 0)
		if r == "body" then
			addP(j, 0, 0.03 * h * wave(t, 0.42), 0, w)
			addR(j, 0.012 * wave(t, 0.42, 0.25), 0, 0, w)
		elseif r == "head" or r == "neck" then
			local k = r == "neck" and 0.5 or 1
			addR(j, 0.035 * wave(t, 0.23), 0.16 * k * wave(t, 0.097, 0.3) + 0.07 * k * wave(t, 0.31), 0.035 * wave(t, 0.17, 0.6), w)
		elseif r == "ear" then
			local p = pulse(t, 4.3 + 1.6 * (s > 0 and 1 or 0), 0.34, s > 0 and 1 or 0)
			addR(j, 0, 0, out(j, 0.34 * p) + 0.04 * wave(t, 0.4, ph), w)
		elseif r == "tail" then
			local lag = 0.1 * (j.depth + 1)
			addR(j, 0, 0.1 * wave(t, 0.8, -lag) + 0.35 * pulse(t, 3.3, 0.5, 2) * wave(t, 6, -lag), 0, w)
		elseif r == "wing" then
			if self.hover and self.flyer then
				addR(j, 0, 0, s * (0.12 + 0.38 * sin(TAU * self.fph - j.depth * 0.3)), w) -- висит в воздухе: ровные взмахи
			else
				addR(j, 0, 0, s * 0.05 * wave(t, 0.5, ph), w)
			end
		elseif r == "ant" then
			addR(j, 0.08 * wave(t, 1.3, ph), 0, 0.14 * wave(t, 0.9, ph + 0.3), w)
		elseif r == "flipper" then
			addR(j, 0, 0, s * 0.1 * wave(t, 0.6, ph), w)
		elseif r == "fore" or r == "hind" or r == "sleg" then
			addR(j, 0.02 * wave(t, 0.42, ph), 0, 0, w)
		elseif r == "deco" then
			addR(j, 0.03 * wave(t, 0.5, ph), 0, 0.06 * wave(t, 0.6, ph + 0.2), w)
		end
	end
end

function PetAnim:_move(t: number, w: number)
	local h = self.h / 3
	local ph = self.cph -- фаза шага: темп зависит от скорости (setSpeed)
	local amp = self.amp -- размах шага: бег шире шага
	local lg = self.hover and 0.25 or 1 -- летящий / парящий: ноги почти не шагают
	for _, j in self.joints do
		local r, s = j.role, j.side
		local pj = ph + j.idx * 0.33
		if r == "body" then
			addP(j, 0, 0.07 * h * amp * max(0, sin(TAU * ph)), 0, w)
			addR(j, 0.06 * sin(TAU * ph + 1), 0, 0.04 * sin(TAU * ph), w)
		elseif r == "head" or r == "neck" then
			addR(j, 0.14 * sin(TAU * ph * 2 + 0.6), 0.05 * sin(TAU * ph), 0, w)
		elseif r == "fore" or r == "hind" then
			-- diagonal pairs: fore-left with hind-right
			local half = (r == "hind" and 0.5 or 0) + (s > 0 and 0.5 or 0)
			local a = (j.dist and 0.35 or 0.6) * amp * lg
			local lag = j.dist and 0.12 or 0
			addR(j, -a * sin(TAU * (ph + half - lag)), 0, 0, w)
			addP(j, 0, 0.05 * h * amp * lg * max(0, cos(TAU * (ph + half))), 0, w)
		elseif r == "sleg" then
			local half = (j.k % 2 == 0 and 0.5 or 0) + (s > 0 and 0.5 or 0)
			addR(j, 0, -s * 0.45 * amp * lg * sin(TAU * (ph + half)), s * 0.3 * amp * lg * max(0, cos(TAU * (ph + half))), w)
		elseif r == "wing" then
			-- flyers flap, shell cases barely move
			if self.flyer then
				addR(j, 0, 0, s * 0.75 * sin(TAU * self.fph - j.depth * 0.3), w) -- темп взмахов от скорости
			else
				addR(j, 0, 0, s * 0.18 * sin(TAU * (ph * 2) - j.depth * 0.3), w)
			end
		elseif r == "flipper" then
			addR(j, 0, 0, s * 0.5 * (0.6 + 0.4 * amp) * sin(TAU * ph + (j.dist and 0.5 or 0)), w)
		elseif r == "tail" then
			local lag = 0.12 * (j.depth + 1)
			addR(j, 0, 0.3 * wave(t, 1.6, -lag), 0, w)
		elseif r == "ear" then
			addR(j, 0.1 * sin(TAU * ph * 2), 0, out(j, 0.2 + 0.1 * sin(TAU * ph * 2)), w)
		elseif r == "ant" then
			addR(j, 0.2 * wave(t, 2.1, pj), 0, 0.2 * wave(t, 1.7, pj), w)
		elseif r == "deco" then
			addR(j, 0.08 * sin(TAU * ph * 2 + pj), 0, 0.1 * wave(t, 1.4, pj), w)
		end
	end
end

-- сидит: зад опущен, передние лапы прямые, хвост виляет, дыхание, иногда ухо дёрнется и взгляд в сторону
function PetAnim:_sit(t: number, w: number)
	local h = self.h / 3
	for _, j in self.joints do
		local r, s = j.role, j.side
		local ph = j.idx * 0.37 + (s > 0 and 0.2 or 0)
		if r == "body" then
			addP(j, 0, -0.16 * h + 0.014 * h * wave(t, 0.8), 0, w)
			addR(j, 0.26 + 0.012 * wave(t, 0.8, 0.25), 0, 0, w)
		elseif r == "hind" then
			addR(j, (j.dist and 0.45 or 0.75), 0, 0, w) -- лапы подобраны вперёд под корпус
		elseif r == "fore" then
			addR(j, j.dist and -0.16 or -0.3, 0, 0, w) -- прямые: гасим наклон корпуса
		elseif r == "sleg" then
			addR(j, 0, 0, -s * 0.25, w)
		elseif r == "head" then
			addR(j, -0.22, 0.2 * wave(t, 0.13, 0.4) * ss(0.3, 0.7, wave(t, 0.07) * 0.5 + 0.5), 0, w) -- голова ровно, взгляд по сторонам
		elseif r == "neck" then
			addR(j, -0.06, 0, 0, w)
		elseif r == "tail" then
			addR(j, 0.15, 0.32 * wave(t, 0.9, -0.12 * (j.depth + 1)), 0, w)
		elseif r == "ear" then
			local p = pulse(t, 3.2 + 1.3 * (s > 0 and 1 or 0), 0.3, s > 0 and 1.4 or 0)
			addR(j, 0, 0, out(j, 0.4 * p), w)
		elseif r == "wing" then
			addR(j, 0, 0, s * 0.04, w)
		end
	end
end

-- u: 0..1 over the reaction (prototype react): spin and jump are in the baked root curve
function PetAnim:_react(u: number, w: number)
	local e = bump(u, 0, 1)
	for _, j in self.joints do
		local r, s = j.role, j.side
		if r == "ear" then
			addR(j, 0, 0, out(j, 0.5 * e * wave(u, 3)), w)
		elseif r == "hind" or r == "fore" then
			local k = r == "hind" and 0.7 * bump(u, 0.1, 0.5) or -0.6 * e
			addR(j, k * (j.dist and 0.6 or 1), 0, 0, w)
		elseif r == "sleg" then
			addR(j, 0, 0, -s * 0.5 * bump(u, 0.1, 0.5), w)
		elseif r == "wing" then
			addR(j, 0, 0, s * (0.2 + 0.7 * e * wave(u, 4)), w)
		elseif r == "flipper" then
			addR(j, 0, 0, s * 0.6 * e * wave(u, 3), w)
		elseif r == "tail" then
			addR(j, 0, 0.5 * e * wave(u, 6, -0.1 * j.depth), 0, w)
		elseif r == "head" or r == "neck" then
			addR(j, -0.12 * e, 0.25 * e * wave(u, 2), 0, w)
		elseif r == "ant" or r == "deco" then
			addR(j, 0.2 * e * wave(u, 4, j.idx * 0.2), 0, 0.2 * e * wave(u, 3, j.idx * 0.3), w)
		end
	end
end

-- u: 0..1 over the whole hatch (prototype timing: 0.03-0.44 pecking, 0.46-0.8 jump, 0.78-0.92 landing, 0.84-1 wag)
function PetAnim:_hatch(u: number, w: number)
	local pk = bump(u, 0.03, 0.44)
	local jp = bump(u, 0.46, 0.8)
	local fl = kf(u, 0, 0, 0.46, 0, 0.6, 0.6, 0.78, 0.2, 0.84, -0.7, 0.92, 0.25, 1, 0)
	local wag = bump(u, 0.84, 1)
	for _, j in self.joints do
		local r, s = j.role, j.side
		local k = j.dist and 0.6 or 1
		if r == "ear" then
			addR(j, -0.2 * pk + 0.9 * fl * 0.5, 0, out(j, 0.45 * pk * wave(u, 7, s > 0 and 0.3 or 0)), w)
		elseif r == "head" or r == "neck" then
			addR(j, -0.2 * pk, 0.35 * pk * wave(u, 3.2), 0, w)
		elseif r == "hind" then
			addR(j, 0.9 * jp * k, 0, 0, w)
		elseif r == "fore" then
			addR(j, -0.5 * jp * k, 0, 0, w)
		elseif r == "sleg" then
			addR(j, 0, 0, -s * 0.7 * jp, w)
		elseif r == "wing" then
			addR(j, 0, 0, s * (0.15 + 0.5 * pk * wave(u, 9) + 0.9 * jp), w)
		elseif r == "flipper" then
			addR(j, 0, 0, s * (0.5 * pk * wave(u, 8) + 0.7 * jp), w)
		elseif r == "tail" then
			addR(j, 0, 0.5 * wag * wave(u, 14, -0.1 * j.depth), 0, w)
			addR(j, -0.3 * jp, 0, 0, w)
		elseif r == "body" then
			addR(j, -0.3 * bump(u, 0.46, 0.62) + 0.22 * bump(u, 0.64, 0.8), 0, 0, w)
		elseif r == "ant" or r == "deco" then
			addR(j, 0.3 * pk * wave(u, 6, j.idx * 0.2), 0, 0.3 * (pk + jp) * wave(u, 5, j.idx * 0.25), w)
		end
	end
end

---------------------------------------------------------------------
-- frame update; returns the root offset {x,y,z,rx,ry,rz,s} of the hatch / react curves (already converted to Roblox axes)
---------------------------------------------------------------------
local function ss01(a, b, x)
	return ss(a, b, x)
end

function PetAnim:update(dt: number)
	dt *= self.ts
	local d = self.d
	self.t += dt
	local target = self.mode == "move" and 1 or 0
	self.wm += (target - self.wm) * min(1, dt * 3.2)
	if self.wm < 0.002 then
		self.wm = 0
	end
	local wk = 0.35 + 0.65 * self.wm
	self.mt += dt * wk
	-- скорость: темп шага, размах и частота взмахов
	if self.spd then
		self.sp += (self.spd - self.sp) * min(1, dt * 8)
		self.amp = clamp(0.5 + 0.035 * self.sp, 0.5, 1.4)
		self.cph += dt * min(3.6, 0.9 + 0.12 * self.sp) * wk
		self.fph += dt * min(8, 2.4 + 0.22 * self.sp)
	else
		self.amp = 1
		self.cph += dt * 1.55 * wk
		self.fph += dt * 3.1 * wk
	end
	local tsit = self.mode == "sit" and 1 or 0
	self.ws += (tsit - self.ws) * min(1, dt * 4.5)
	if self.ws < 0.002 then
		self.ws = 0
	end
	if self.ru >= 0 then
		self.ru += dt / (d and d.rd or 1.2)
		if self.ru >= 1 then
			self.ru = -1
		end
	end
	local hatching = false
	if self.hu >= 0 then
		self.hu += dt / (d and d.hd or 2.7)
		if self.hu >= 1 then
			self.hu = -1
		else
			hatching = true
		end
	end

	for _, j in self.joints do
		local a = j.acc
		a[1], a[2], a[3], a[4], a[5], a[6] = 0, 0, 0, 0, 0, 0
	end
	local wi = (1 - self.wm) * (hatching and ss01(0.82, 1, self.hu) or 1)
	if wi > 0 then
		self:_idle(self.t, wi)
	end
	if self.wm > 0 and not hatching then
		self:_move(self.mt, self.wm)
	end
	if self.ws > 0 and not hatching then
		self:_sit(self.t, self.ws)
	end
	local root = self.root
	root.x, root.y, root.z, root.rx, root.ry, root.rz, root.s = 0, 0, 0, 0, 0, 0, 1
	if self.ru >= 0 then
		local u = self.ru
		self:_react(u, min(1, u / 0.1, (1 - u) / 0.16))
		local c = d and d.react
		if c then
			local dur = d.rd
			local t = u * dur
			root.x = -sample(c.x, t, dur, 0)
			root.y = sample(c.y, t, dur, 0)
			root.z = -sample(c.z, t, dur, 0)
			root.rx = -sample(c.rx, t, dur, 0)
			root.ry = sample(c.ry, t, dur, 0)
			root.rz = -sample(c.rz, t, dur, 0)
			root.s = sample(c.s, t, dur, 1)
		end
	end
	if hatching then
		self:_hatch(self.hu, 1)
		local c = d and d.hatch
		if c then
			local dur = d.hd
			local t = self.hu * dur
			root.x = -sample(c.x, t, dur, 0)
			root.y = sample(c.y, t, dur, 0)
			root.z = -sample(c.z, t, dur, 0)
			root.rx = -sample(c.rx, t, dur, 0)
			root.ry = sample(c.ry, t, dur, 0)
			root.rz = -sample(c.rz, t, dur, 0)
			root.s = sample(c.s, t, dur, 1)
		end
	end

	for _, j in self.joints do
		local a = j.acc
		local rx, ry, rz = a[1], a[2], a[3]
		local lim = j.limits
		if lim then
			-- limits are the pack's rotation budget per axis (degrees); allow a little more than that for big gestures
			local function cl(v: number, l: { number }?, mul: number): number
				if not l then
					return v
				end
				return clamp(v, math.rad(l[1]) * mul, math.rad(l[2]) * mul)
			end
			rx, ry, rz = cl(rx, lim.X, 2.2), cl(ry, lim.Y, 2.2), cl(rz, lim.Z, 2.2)
		end
		j.m.Transform = CFrame.new(a[4], a[5], a[6]) * CFrame.Angles(rx, ry, rz)
	end
	return root, hatching
end

-- restore every joint to rest
function PetAnim:reset()
	for _, j in self.joints do
		j.m.Transform = CFrame.identity
	end
	self.hu, self.ru, self.wm, self.ws = -1, -1, 0, 0
end

return PetAnim
