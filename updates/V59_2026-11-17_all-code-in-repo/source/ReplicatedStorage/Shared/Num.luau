-- ReplicatedStorage/Shared/Num.luau
-- Формат чисел: 999 → "999", 1234 → "1.23K", 1.5e15 → "1.5Qa" … до De (1e33).
local Config = require(script.Parent.Config)

local Num = {}
local SUF = Config.SUFFIXES

local function trim(s: string): string
	if s:find("%.") then
		s = s:gsub("0+$", ""):gsub("%.$", "")
	end
	return s
end

function Num.short(n: number): string
	if n ~= n then
		return "0"
	end
	local neg = n < 0
	n = math.abs(n)
	if n < 1000 then
		local s = n < 10 and n % 1 ~= 0 and trim(string.format("%.1f", n)) or tostring(math.floor(n + 0.5))
		return (neg and "-" or "") .. s
	end
	local i = math.min(math.floor(math.log10(n) / 3), #SUF - 1)
	local v = n / 10 ^ (i * 3)
	local s
	if v >= 100 then
		s = string.format("%.0f", math.floor(v))
	elseif v >= 10 then
		s = trim(string.format("%.1f", math.floor(v * 10) / 10))
	else
		s = trim(string.format("%.2f", math.floor(v * 100) / 100))
	end
	return (neg and "-" or "") .. s .. SUF[i + 1]
end

-- С разделителем тысяч: 1234567 → "1 234 567" (для счётчиков до миллиона)
function Num.full(n: number): string
	n = math.floor(n + 0.5)
	if math.abs(n) >= 1e6 then
		return Num.short(n)
	end
	local s = tostring(math.abs(n))
	local out = s:reverse():gsub("(%d%d%d)", "%1 "):reverse()
	out = out:gsub("^ ", "")
	return (n < 0 and "-" or "") .. out
end

function Num.weight(w: number): string
	if w >= 1000 then
		return trim(string.format("%.2f", w / 1000)) .. " t"
	elseif w >= 10 then
		return trim(string.format("%.1f", w)) .. " kg"
	end
	return trim(string.format("%.2f", w)) .. " kg"
end

function Num.mult(m: number): string
	if m < 1 then
		return "×" .. trim(string.format("%.2f", m))
	end
	if m >= 10 then
		return "×" .. tostring(math.floor(m + 0.5))
	end
	return "×" .. trim(string.format("%.1f", m))
end

function Num.time(sec: number): string
	sec = math.max(0, math.floor(sec + 0.5))
	if sec >= 3600 then
		return string.format("%d:%02d:%02d", sec // 3600, (sec // 60) % 60, sec % 60)
	end
	return string.format("%d:%02d", sec // 60, sec % 60)
end

function Num.odds(p: number): string
	if p <= 0 then
		return "—"
	end
	if p >= 0.995 then
		return "100%"
	end
	if p >= 0.01 then
		return trim(string.format("%.1f", p * 100)) .. "%"
	end
	return "1 in " .. Num.short(1 / p)
end

return Num
