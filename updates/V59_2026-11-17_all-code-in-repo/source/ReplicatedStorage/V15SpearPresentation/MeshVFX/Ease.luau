--!strict
--[[
	Ease
	Pure easing curves + phase helpers used by every effect.

	All curves map t in [0, 1] -> [0, 1] (back/elastic overshoot outside that range
	on purpose). Pure Luau: no Roblox services, unit-tested under Lune.

	Usage:
		local k = Ease.outExpo(Ease.phase(t, 0, 0.15)) -- 0..1 during the first 15% of life
		local fade = 1 - Ease.inQuad(Ease.phase(t, 0.3, 1))
]]

export type EaseFn = (t: number) -> number

local Ease = {}

local PI = math.pi
local HALF_PI = math.pi / 2

-- Maps t from the sub-range [a, b] to [0, 1] and clamps. The core tool for
-- multi-phase effects (spawn / hold / dissipate) driven by one normalized time.
function Ease.phase(t: number, a: number, b: number): number
	if b <= a then
		return if t >= b then 1 else 0
	end
	return math.clamp((t - a) / (b - a), 0, 1)
end

function Ease.lerp(a: number, b: number, t: number): number
	return a + (b - a) * t
end

function Ease.linear(t: number): number
	return t
end

function Ease.inQuad(t: number): number
	return t * t
end

function Ease.outQuad(t: number): number
	return 1 - (1 - t) * (1 - t)
end

function Ease.inOutQuad(t: number): number
	return if t < 0.5 then 2 * t * t else 1 - (-2 * t + 2) ^ 2 / 2
end

function Ease.inCubic(t: number): number
	return t * t * t
end

function Ease.outCubic(t: number): number
	return 1 - (1 - t) ^ 3
end

function Ease.outQuart(t: number): number
	return 1 - (1 - t) ^ 4
end

function Ease.outQuint(t: number): number
	return 1 - (1 - t) ^ 5
end

function Ease.inExpo(t: number): number
	return if t <= 0 then 0 else 2 ^ (10 * t - 10)
end

function Ease.outExpo(t: number): number
	return if t >= 1 then 1 else 1 - 2 ^ (-10 * t)
end

function Ease.inOutSine(t: number): number
	return -(math.cos(PI * t) - 1) / 2
end

function Ease.outSine(t: number): number
	return math.sin(t * HALF_PI)
end

-- Overshoots then settles: rocks popping out of the ground, UI punches.
function Ease.outBack(t: number): number
	local c1 = 1.70158
	local c3 = c1 + 1
	return 1 + c3 * (t - 1) ^ 3 + c1 * (t - 1) ^ 2
end

function Ease.outElastic(t: number): number
	if t <= 0 then
		return 0
	elseif t >= 1 then
		return 1
	end
	return 2 ^ (-10 * t) * math.sin((t * 10 - 0.75) * (2 * PI / 3)) + 1
end

-- 0 -> 1 -> 0 bell, peak at `peak` (0..1). Handy for flashes and thickness pulses.
function Ease.pulse(t: number, peak: number): number
	if t <= 0 or t >= 1 then
		return 0
	end
	if t < peak then
		return Ease.outQuad(t / peak)
	end
	return 1 - Ease.inQuad((t - peak) / (1 - peak))
end

--[[
	CSS-style cubic-bezier(x1, y1, x2, y2) easing, so curves can be copied from
	After Effects / cubic-bezier.com. Solves x(u) = t with Newton + bisection fallback.
]]
function Ease.cubicBezier(x1: number, y1: number, x2: number, y2: number): EaseFn
	local cx = 3 * x1
	local bx = 3 * (x2 - x1) - cx
	local ax = 1 - cx - bx
	local cy = 3 * y1
	local by = 3 * (y2 - y1) - cy
	local ay = 1 - cy - by

	local function sampleX(u: number): number
		return ((ax * u + bx) * u + cx) * u
	end
	local function sampleY(u: number): number
		return ((ay * u + by) * u + cy) * u
	end
	local function slopeX(u: number): number
		return (3 * ax * u + 2 * bx) * u + cx
	end

	return function(t: number): number
		if t <= 0 then
			return 0
		elseif t >= 1 then
			return 1
		end
		local u = t
		for _ = 1, 8 do
			local err = sampleX(u) - t
			if math.abs(err) < 1e-6 then
				return sampleY(u)
			end
			local d = slopeX(u)
			if math.abs(d) < 1e-6 then
				break
			end
			u -= err / d
		end
		-- Bisection fallback for flat regions.
		local lo, hi = 0, 1
		u = t
		for _ = 1, 30 do
			local x = sampleX(u)
			if math.abs(x - t) < 1e-6 then
				break
			end
			if x < t then
				lo = u
			else
				hi = u
			end
			u = (lo + hi) / 2
		end
		return sampleY(u)
	end
end

-- Frame-rate independent exponential smoothing factor: x += (target - x) * Ease.expAlpha(k, dt).
-- Never overshoots, unlike `x += (target - x) * k * dt` which explodes when k * dt > 1.
function Ease.expAlpha(sharpness: number, dt: number): number
	return 1 - math.exp(-sharpness * dt)
end

return Ease
