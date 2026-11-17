-- StarterPlayerScripts/Client/Theme.luau
-- Стиль интерфейса: шрифт FredokaOne, белый текст с чёрной обводкой, сочные градиенты.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Shared.Config)

local Theme = {}

Theme.FONT = Enum.Font.FredokaOne
Theme.STROKE = 3

Theme.C = {
	text = Color3.fromRGB(250, 255, 247),
	dim = Color3.fromRGB(192, 216, 207),
	stroke = Color3.fromRGB(8, 16, 20),
	panel = Color3.fromRGB(30, 48, 55),
	panel2 = Color3.fromRGB(18, 30, 36),
	panelLine = Color3.fromRGB(10, 23, 27),
	card = Color3.fromRGB(45, 70, 73),
	gold = Color3.fromRGB(255, 204, 82),
	green = Color3.fromRGB(105, 224, 138),
	blue = Color3.fromRGB(78, 181, 255),
	purple = Color3.fromRGB(177, 119, 255),
	red = Color3.fromRGB(255, 91, 102),
	orange = Color3.fromRGB(255, 157, 67),
	pink = Color3.fromRGB(255, 126, 190),
	cyan = Color3.fromRGB(80, 224, 213),
	gray = Color3.fromRGB(150, 170, 171),
	dark = Color3.fromRGB(13, 23, 27),
	xp = Color3.fromRGB(120, 230, 255),
}

-- Цвет кнопки → (верх, низ, обводка, тень)
function Theme.shades(c: Color3): (Color3, Color3, Color3, Color3)
	local h, s, v = c:ToHSV()
	local top = Color3.fromHSV(h, math.max(0, s * 0.75), math.min(1, v * 1.12 + 0.06))
	local bottom = Color3.fromHSV(h, math.min(1, s * 1.08), v * 0.78)
	local line = Color3.fromHSV(h, math.min(1, s * 1.1), v * 0.42)
	local shadow = Color3.fromHSV(h, math.min(1, s * 1.1), v * 0.3)
	return top, bottom, line, shadow
end

function Theme.rarity(r: number)
	return Config.RARITIES[math.clamp(r, 1, #Config.RARITIES)]
end

function Theme.tier(i: number)
	return Config.TIERS[math.clamp(i, 1, #Config.TIERS)]
end

function Theme.lerp(a: Color3, b: Color3, t: number): Color3
	return a:Lerp(b, math.clamp(t, 0, 1))
end

-- Радужный цвет по времени
function Theme.rainbow(t: number, s: number?, v: number?): Color3
	return Color3.fromHSV((t * 0.25) % 1, s or 0.7, v or 1)
end

return Theme
