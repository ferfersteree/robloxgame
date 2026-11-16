--!nonstrict
-- StarterPlayerScripts/Client/ShopVoxels (V36)
-- Кубические (воксельные) 3D-иконки товаров магазина в том же кубическом стиле, что яйца и питомцы.
-- Модель собирается из кубиков в сетке и склеивается в минимум деталей (по X, потом по Z, потом по Y).
-- ShopVoxels.build(kind) -> Model | nil. Вид: передом к камере -Z, низ на y = 0. Ничего не загружается в Roblox.
-- Ключи kind те же, что у плоских иконок: coins1..4, charm, insight, broker, smith, wrap, vip, founder,
-- fortune20, jackpot20, fair30, hour_bundle, server15, bag, luck30.
local ShopVoxels = {}

local function C(r, g, b)
	return Color3.fromRGB(r, g, b)
end

-- палитра: имя -> { цвет, материал? }
local NEON = Enum.Material.Neon
local PAL = {
	gold = { C(255, 196, 36) }, gold2 = { C(214, 146, 24) }, goldHi = { C(255, 236, 130) },
	glowGold = { C(255, 226, 110), NEON },
	brown = { C(150, 96, 52) }, brownD = { C(104, 64, 34) }, brownL = { C(192, 132, 78) },
	burlap = { C(208, 172, 110) }, burlapD = { C(168, 130, 78) },
	cork = { C(196, 150, 96) }, cream = { C(250, 242, 214) },
	red = { C(228, 62, 70) }, redD = { C(170, 38, 50) },
	pink = { C(255, 110, 160) }, pinkD = { C(214, 66, 118) }, pinkL = { C(255, 168, 200) },
	glowPink = { C(255, 120, 180), NEON },
	green = { C(84, 190, 90) }, greenD = { C(46, 134, 62) }, greenL = { C(150, 232, 120) },
	blue = { C(80, 150, 255) }, blueD = { C(46, 96, 196) }, blueL = { C(160, 206, 255) },
	glowBlue = { C(110, 190, 255), NEON },
	cyan = { C(70, 210, 210) }, cyanD = { C(36, 150, 160) }, cyanL = { C(150, 244, 240) },
	glowCyan = { C(120, 255, 240), NEON },
	purple = { C(160, 100, 230) }, purpleD = { C(104, 56, 176) }, purpleL = { C(206, 164, 255) },
	glowPurple = { C(190, 130, 255), NEON },
	yellow = { C(255, 214, 60) }, yellowD = { C(222, 160, 24) }, yellowL = { C(255, 240, 150) },
	white = { C(250, 250, 250) }, glass = { C(214, 236, 252) },
	grey = { C(170, 176, 190) }, greyD = { C(110, 116, 130) }, iron = { C(66, 70, 84) }, ironL = { C(122, 128, 142) },
	orangeGlow = { C(255, 150, 40), NEON },
	soil = { C(110, 76, 48) },
}

---------------------------------------------------------------------
-- сетка кубиков
---------------------------------------------------------------------
local Vox = {}
Vox.__index = Vox

function Vox.new()
	return setmetatable({ cells = {} }, Vox)
end

local function key(x, y, z)
	return x .. "," .. y .. "," .. z
end

-- c == nil стирает кубик (так вырезаются полости)
function Vox:set(x, y, z, c)
	x, y, z = math.floor(x + 0.5), math.floor(y + 0.5), math.floor(z + 0.5)
	if c == nil then
		self.cells[key(x, y, z)] = nil
		return
	end
	self.cells[key(x, y, z)] = { x, y, z, c }
end

function Vox:clear(x, y, z)
	self.cells[key(math.floor(x + 0.5), math.floor(y + 0.5), math.floor(z + 0.5))] = nil
end

function Vox:box(x0, y0, z0, x1, y1, z1, c)
	for x = x0, x1 do
		for y = y0, y1 do
			for z = z0, z1 do
				self:set(x, y, z, c)
			end
		end
	end
end

function Vox:ellipsoid(cx, cy, cz, rx, ry, rz, c)
	for x = math.floor(cx - rx), math.ceil(cx + rx) do
		for y = math.floor(cy - ry), math.ceil(cy + ry) do
			for z = math.floor(cz - rz), math.ceil(cz + rz) do
				local dx, dy, dz = (x - cx) / rx, (y - cy) / ry, (z - cz) / rz
				if dx * dx + dy * dy + dz * dz <= 1.0 then
					self:set(x, y, z, c)
				end
			end
		end
	end
end

function Vox:ball(cx, cy, cz, r, c)
	self:ellipsoid(cx, cy, cz, r, r, r, c)
end

-- цилиндр вдоль Y (радиус r, от y0 до y1 включительно)
function Vox:cylY(cx, cz, r, y0, y1, c)
	for x = math.floor(cx - r), math.ceil(cx + r) do
		for z = math.floor(cz - r), math.ceil(cz + r) do
			if (x - cx) ^ 2 + (z - cz) ^ 2 <= r * r then
				for y = y0, y1 do
					self:set(x, y, z, c)
				end
			end
		end
	end
end

-- цилиндр вдоль Z (монета лицом к камере)
function Vox:cylZ(cx, cy, r, z0, z1, c)
	for x = math.floor(cx - r), math.ceil(cx + r) do
		for y = math.floor(cy - r), math.ceil(cy + r) do
			if (x - cx) ^ 2 + (y - cy) ^ 2 <= r * r then
				for z = z0, z1 do
					self:set(x, y, z, c)
				end
			end
		end
	end
end

-- цилиндр вдоль X
function Vox:cylX(cy, cz, r, x0, x1, c)
	for y = math.floor(cy - r), math.ceil(cy + r) do
		for z = math.floor(cz - r), math.ceil(cz + r) do
			if (y - cy) ^ 2 + (z - cz) ^ 2 <= r * r then
				for x = x0, x1 do
					self:set(x, y, z, c)
				end
			end
		end
	end
end

-- перекрасить уже существующие кубики по условию
function Vox:recolor(pred, c)
	for _, cell in self.cells do
		if pred(cell[1], cell[2], cell[3]) then
			cell[4] = c
		end
	end
end

-- рисунок из строк (вид спереди, x вправо, верхняя строка сверху) на плоскости z
function Vox:glyph(rows, x0, y0, z, map)
	local h = #rows
	for r, line in rows do
		for i = 1, #line do
			local ch = line:sub(i, i)
			local c = map[ch]
			if c then
				self:set(x0 + i - 1, y0 + (h - r), z, c)
			end
		end
	end
end

-- склейка: по X, затем по Z, затем по Y (одноцветные коробки)
function Vox:build(name: string, unit: number): Model
	local byColor = {}
	for _, cell in self.cells do
		local list = byColor[cell[4]]
		if not list then
			list = {}
			byColor[cell[4]] = list
		end
		list[#list + 1] = cell
	end
	local model = Instance.new("Model")
	model.Name = name
	local minX, minY, minZ = math.huge, math.huge, math.huge
	for _, cell in self.cells do
		minX, minY, minZ = math.min(minX, cell[1]), math.min(minY, cell[2]), math.min(minZ, cell[3])
	end
	for cname, list in byColor do
		-- индекс по (y, z) -> отсортированные x
		local rows = {}
		for _, cell in list do
			local rk = cell[2] .. "," .. cell[3]
			local r = rows[rk]
			if not r then
				r = { y = cell[2], z = cell[3], xs = {} }
				rows[rk] = r
			end
			r.xs[#r.xs + 1] = cell[1]
		end
		-- прогоны по X
		local runsByY = {}
		for _, r in rows do
			table.sort(r.xs)
			local i = 1
			while i <= #r.xs do
				local j = i
				while j < #r.xs and r.xs[j + 1] == r.xs[j] + 1 do
					j += 1
				end
				local ly = runsByY[r.y]
				if not ly then
					ly = {}
					runsByY[r.y] = ly
				end
				ly[#ly + 1] = { x0 = r.xs[i], x1 = r.xs[j], z = r.z }
				i = j + 1
			end
		end
		-- склейка по Z внутри каждого y
		local rectsByY = {}
		for y, runs in runsByY do
			table.sort(runs, function(a, b)
				if a.x0 ~= b.x0 then
					return a.x0 < b.x0
				end
				if a.x1 ~= b.x1 then
					return a.x1 < b.x1
				end
				return a.z < b.z
			end)
			local rects = {}
			local open = {}
			for _, run in runs do
				local rk = run.x0 .. "," .. run.x1
				local o = open[rk]
				if o and o.z1 == run.z - 1 then
					o.z1 = run.z
				else
					o = { x0 = run.x0, x1 = run.x1, z0 = run.z, z1 = run.z }
					open[rk] = o
					rects[#rects + 1] = o
				end
			end
			rectsByY[y] = rects
		end
		-- склейка по Y
		local ys = {}
		for y in rectsByY do
			ys[#ys + 1] = y
		end
		table.sort(ys)
		local openBoxes = {}
		local boxes = {}
		for _, y in ys do
			local nextOpen = {}
			for _, r in rectsByY[y] do
				local bk = r.x0 .. "," .. r.x1 .. "," .. r.z0 .. "," .. r.z1
				local o = openBoxes[bk]
				if o and o.y1 == y - 1 then
					o.y1 = y
				else
					o = { x0 = r.x0, x1 = r.x1, z0 = r.z0, z1 = r.z1, y0 = y, y1 = y }
					boxes[#boxes + 1] = o
				end
				nextOpen[bk] = o
			end
			openBoxes = nextOpen
		end
		local pal = PAL[cname]
		for _, b in boxes do
			local p = Instance.new("Part")
			p.Anchored = true
			p.CanCollide = false
			p.CanQuery = false
			p.CanTouch = false
			p.CastShadow = false
			p.TopSurface = Enum.SurfaceType.Smooth
			p.BottomSurface = Enum.SurfaceType.Smooth
			p.Material = pal[2] or Enum.Material.SmoothPlastic
			p.Color = pal[1]
			p.Size = Vector3.new(b.x1 - b.x0 + 1, b.y1 - b.y0 + 1, b.z1 - b.z0 + 1) * unit
			p.Position = Vector3.new((b.x0 + b.x1 + 1) / 2 - minX, (b.y0 + b.y1 + 1) / 2 - minY, (b.z0 + b.z1 + 1) / 2 - minZ) * unit
			p.Name = cname
			p.Parent = model
		end
	end
	model.PrimaryPart = model:FindFirstChildWhichIsA("BasePart")
	return model
end

---------------------------------------------------------------------
-- общие кирпичики
---------------------------------------------------------------------
local function sparkle(v, x, y, z, c)
	c = c or "glowGold"
	v:set(x, y, z, c)
	v:set(x - 1, y, z, c)
	v:set(x + 1, y, z, c)
	v:set(x, y - 1, z, c)
	v:set(x, y + 1, z, c)
end

-- стопка монет: n штук, чередуются два оттенка
local function coinStack(v, cx, cz, n, r, y0)
	y0 = y0 or 0
	for i = 0, n - 1 do
		v:cylY(cx, cz, r or 1.8, y0 + i, y0 + i, (i % 2 == 0) and "gold" or "gold2")
	end
	v:cylY(cx, cz, (r or 1.8) - 0.9, y0 + n - 1, y0 + n - 1, "goldHi")
end

-- монета лицом к камере
local function coinFront(v, cx, cy, z, r)
	v:cylZ(cx, cy, r, z, z + 1, "gold2")
	v:cylZ(cx, cy, r - 0.9, z - 1, z, "gold")
	v:cylZ(cx, cy, r - 2.0, z - 1, z - 1, "goldHi")
end

local GLYPH = {
	star = { ".X.", "XXX", ".X." },
	heart = { "X.X", "XXX", ".X." },
	coin = { ".X.", "XXX", ".X." },
	clover = { "X.X", ".X.", "X.X" },
}

-- зелье: ox, oz - центр, r - радиус, liquid - цвет, glyph - ключ рисунка, gcol - цвет рисунка
local function potion(v, ox, oz, r, liquid, liquidHi, glyph, gcol)
	local cy = math.floor(r * 0.92 + 0.5)
	v:ellipsoid(ox, cy, oz, r, r * 0.92, r, liquid)
	-- блик и тёмный низ
	v:ellipsoid(ox - r * 0.45, cy + r * 0.35, oz - r * 0.55, r * 0.34, r * 0.3, r * 0.3, liquidHi)
	local neckR = math.max(1.2, r * 0.36)
	local top = math.floor(cy + r * 0.85)
	v:cylY(ox, oz, neckR + 0.4, top, top + 2, "glass")
	v:cylY(ox, oz, neckR + 0.9, top + 3, top + 3, "glass")
	v:cylY(ox, oz, neckR + 0.2, top + 4, top + 5, "cork")
	-- этикетка спереди
	if r >= 3 then
		local zf = math.floor(oz - r) - 1
		v:box(math.floor(ox) - 1, math.floor(cy) - 1, zf, math.floor(ox) + 1, math.floor(cy) + 1, zf, "cream")
		if glyph and GLYPH[glyph] then
			v:glyph(GLYPH[glyph], math.floor(ox) - 1, math.floor(cy) - 1, zf - 1, { X = gcol })
		end
	end
end

---------------------------------------------------------------------
-- модели
---------------------------------------------------------------------
local B = {}

-- кожаный кошелёк с монетой
B.coins1 = function(v)
	v:ellipsoid(0, 4, 0, 5, 3.9, 4.6, "brown")
	v:ellipsoid(-2.4, 5.2, -3.4, 1.7, 1.4, 1.2, "brownL")
	v:cylY(0, 0, 2.6, 7, 8, "brownD")
	v:cylY(0, 0, 3.0, 7, 7, "gold2") -- завязка
	v:cylY(0, 0, 3.6, 9, 9, "brown")
	v:cylY(0, 0, 3.0, 10, 10, "brown")
	v:cylY(0, 0, 1.9, 10, 10, "brownD")
	v:cylY(0, 0, 1.5, 10, 11, "gold") -- монеты в горловине
	coinFront(v, 5, 3, -6, 2.6)
	coinStack(v, -6, -2, 3, 1.6)
	sparkle(v, 6, 9, -2)
	sparkle(v, -7, 8, 0)
end

-- мешок с монетами
B.coins2 = function(v)
	v:ellipsoid(0, 5, 0, 6, 5, 5.4, "burlap")
	v:ellipsoid(-2.8, 6.5, -4.6, 2, 1.8, 1.2, "cream")
	v:cylY(0, 0, 3.2, 10, 11, "burlapD")
	v:cylY(0, 0, 3.8, 10, 10, "red") -- верёвка
	v:ellipsoid(-3, 13, 0, 2.2, 1.6, 1.4, "burlapD")
	v:ellipsoid(3, 12.6, 0, 2.2, 1.4, 1.4, "burlapD")
	coinFront(v, 0, 5, -6, 3)
	coinStack(v, 8, -2, 6, 1.9)
	coinStack(v, -8, -3, 4, 1.9)
	sparkle(v, 6, 13, -3)
end

-- сундук, крышка откинута, внутри монеты
local function chest(v, rich)
	v:box(-6, 0, -4, 5, 5, 3, "brown")
	v:box(-6, 0, -4, 5, 0, 3, "brownD")
	for _, x in { -5, 4 } do
		v:box(x, 0, -5, x, 5, -5, "gold2") -- ремни на лицевой стороне
	end
	v:box(-1, 2, -5, 0, 4, -5, "gold") -- замок
	v:box(-1, 3, -6, 0, 3, -6, "goldHi")
	-- откинутая крышка у задней стенки
	v:box(-6, 6, 3, 5, 11, 4, "brown")
	v:box(-6, 6, 4, 5, 11, 4, "brownD")
	v:box(-6, 11, 3, 5, 11, 4, "gold2")
	for _, x in { -5, 4 } do
		v:box(x, 6, 3, x, 11, 4, "gold2")
	end
	-- горка монет
	local h = rich and 4.2 or 3.0
	v:ellipsoid(-0.5, 5, -0.5, 5.6, h, 3.6, "gold")
	v:ellipsoid(-2.5, 7, -1, 2, 1.4, 1.6, "goldHi")
	v:set(2, 8, 0, "gold2")
	v:set(-4, 8, 1, "gold2")
end

B.coins3 = function(v)
	chest(v, false)
	sparkle(v, 8, 9, -2)
	sparkle(v, -9, 11, -1)
end

B.coins4 = function(v)
	chest(v, true)
	coinStack(v, 8.5, -3, 7, 2, 0)
	coinStack(v, -9, -3, 5, 2, 0)
	coinStack(v, 7, -7, 3, 1.8, 0)
	v:box(-3, 8, -2, -2, 9, -1, "red")
	v:box(1, 8, 0, 2, 9, 1, "blue")
	v:box(-1, 9, 1, 0, 10, 2, "green")
	sparkle(v, 0, 13, 0)
	sparkle(v, -9, 10, 0)
	sparkle(v, 9, 11, 0)
end

-- четырёхлистный клевер
B.charm = function(v)
	local lc = { { -3, 8 }, { 3, 8 }, { -3, 3 }, { 3, 3 } }
	for _, p in lc do
		v:ellipsoid(p[1], p[2] + 3, 0, 3.2, 3.2, 1.7, "green")
		v:ellipsoid(p[1] - (p[1] > 0 and -0.8 or 0.8), p[2] + 4, -1.4, 1.5, 1.4, 0.8, "greenL")
	end
	v:ellipsoid(0, 8, 0, 1.6, 1.6, 1.7, "greenD")
	-- стебель с изгибом
	v:box(0, 2, 0, 0, 5, 0, "greenD")
	v:box(0, 0, 0, 1, 1, 0, "greenD")
	v:box(1, 0, 0, 2, 0, 0, "greenD")
	-- золотая монетка-подставка
	v:cylY(0, 0, 3.2, -1, -1, "gold2")
	sparkle(v, 7, 12, 0)
	sparkle(v, -7, 13, 0)
	sparkle(v, 6, 1, -1)
end

-- хрустальный шар
B.insight = function(v)
	v:cylY(0, 0, 4, 0, 0, "brownD")
	v:cylY(0, 0, 3, 1, 2, "brown")
	v:cylY(0, 0, 2.2, 3, 3, "gold2")
	v:ball(0, 9, 0, 5.4, "blueL")
	v:ball(-0.5, 9, -0.5, 4.2, "blue")
	v:ball(1, 9.5, -2, 2.4, "glowPurple")
	v:ball(-2, 10.5, -2.5, 1.3, "glowCyan")
	v:ellipsoid(-3, 12, -3.5, 1.3, 1.6, 0.8, "white") -- блик
	sparkle(v, 8, 14, 0)
	sparkle(v, -8, 12, 1)
end

-- весы с монетами
B.broker = function(v)
	v:box(-4, 0, -3, 4, 0, 3, "greyD")
	v:box(-3, 1, -2, 3, 1, 2, "grey")
	v:box(-1, 2, -1, 0, 12, 0, "grey")
	v:box(-9, 12, -1, 8, 12, 0, "gold")
	v:box(-9, 13, -1, 8, 13, 0, "gold2")
	v:ball(0, 14, 0, 1.6, "gold")
	for _, x in { -8, 7 } do
		v:box(x, 7, 0, x, 11, 0, "greyD")
		v:cylY(x + 0.5, 0, 3.4, 6, 6, "grey")
		v:cylY(x + 0.5, 0, 2.6, 6, 6, "greyD")
		v:cylY(x + 0.5, 0, 3.4, 7, 7, "ironL")
		v:cylY(x + 0.5, 0, 2.5, 7, 7, nil)
	end
	coinStack(v, -7.5, 0, 4, 2, 7)
	v:box(7, 7, -1, 8, 8, 0, "blue")
	v:box(7, 9, -1, 7, 9, -1, "blueL")
	sparkle(v, 11, 13, 0)
end

-- наковальня и молот
B.smith = function(v)
	v:box(-5, 0, -3, 5, 1, 3, "iron")
	v:box(-3, 2, -2, 3, 5, 2, "iron")
	v:box(-7, 6, -3, 7, 8, 3, "ironL")
	v:box(-11, 7, -2, -8, 8, 2, "ironL")
	v:box(-13, 7, -1, -12, 8, 1, "ironL")
	v:box(-7, 9, -3, 7, 9, 3, "greyD")
	-- молот
	for t = 0, 6 do
		v:box(3 + t, 10 + t, -1, 4 + t, 11 + t, 0, "brown")
	end
	v:box(7, 16, -2, 13, 19, 2, "greyD")
	v:box(7, 19, -2, 13, 19, 2, "grey")
	-- искры
	v:set(-4, 11, -1, "orangeGlow")
	v:set(-1, 12, 0, "orangeGlow")
	v:set(1, 11, -2, "glowGold")
	v:set(-6, 10, 1, "glowGold")
end

-- подарок с бантом
B.wrap = function(v)
	v:box(-5, 0, -5, 5, 7, 5, "pink")
	v:box(-5, 7, -5, 5, 8, 5, "pinkD")
	v:box(-6, 8, -6, 6, 9, 6, "pinkD")
	v:box(-1, 0, -6, 1, 9, 6, "yellow") -- лента вдоль
	v:box(-6, 0, -1, 6, 7, 1, "yellow") -- лента поперёк
	v:box(-1, 9, -6, 1, 10, 6, "yellow")
	v:box(-6, 9, -1, 6, 10, 1, "yellow")
	v:ellipsoid(-3, 12, 0, 2.6, 2, 1.8, "yellowD")
	v:ellipsoid(3, 12, 0, 2.6, 2, 1.8, "yellowD")
	v:ellipsoid(-3, 12.4, -1.2, 1.4, 1, 0.8, "yellowL")
	v:ellipsoid(3, 12.4, -1.2, 1.4, 1, 0.8, "yellowL")
	v:box(-1, 11, -1, 1, 13, 1, "yellow")
	sparkle(v, 8, 12, -2)
	sparkle(v, -8, 14, 0)
end

-- корона с самоцветами
local function crown(v, band, bandD, gems, tall)
	v:cylY(0, 0, 5.6, 0, 3, band)
	v:cylY(0, 0, 4.3, 1, 3, nil) -- полость
	v:cylY(0, 0, 4.3, 1, 1, "purpleD") -- бархат внутри
	v:cylY(0, 0, 5.6, 0, 0, bandD) -- нижний ободок
	v:cylY(0, 0, 5.6, 3, 3, bandD) -- верхний ободок
	v:cylY(0, 0, 4.5, 3, 3, nil)
	local n = 5
	for i = 0, n - 1 do
		local a = i * math.pi * 2 / n + math.pi / 2
		local x, z = math.cos(a) * 4.9, math.sin(a) * 4.9
		local h = (i == 0) and tall or (tall - 2)
		v:box(x - 0.5, 4, z - 0.5, x + 0.5, 3 + h, z + 0.5, band)
		v:ball(x, 4 + h + 1, z, 1.3, gems[i % #gems + 1])
	end
	-- крупный камень спереди
	v:box(-1, 1, -6, 1, 3, -6, gems[1])
	v:set(0, 2, -7, "white")
end
B.vip = function(v)
	crown(v, "gold", "gold2", { "red", "blue", "green" }, 6)
	sparkle(v, 8, 10, -3)
	sparkle(v, -8, 9, -3)
end

B.founder = function(v)
	crown(v, "purple", "gold", { "glowCyan", "glowPink", "glowGold" }, 8)
	sparkle(v, 8, 12, -2)
	sparkle(v, -8, 11, -2)
	sparkle(v, 0, 16, 0)
end

B.fortune20 = function(v)
	potion(v, 0, 0, 5, "yellow", "yellowL", "star", "gold2")
	sparkle(v, 7, 9, -2)
	sparkle(v, -7, 12, -1)
	sparkle(v, 6, 15, 0)
end

B.jackpot20 = function(v)
	potion(v, -2, 0, 5, "pink", "pinkL", "heart", "red")
	coinStack(v, 7, -3, 5, 2, 0)
	coinStack(v, 6, 2, 2, 1.8, 0)
	sparkle(v, -8, 13, -1)
	sparkle(v, 8, 10, -4)
end

B.fair30 = function(v)
	potion(v, -2, 0, 5, "cyan", "cyanL", "coin", "gold2")
	coinFront(v, 6, 3, -5, 2.2)
	sparkle(v, -8, 12, -1)
	sparkle(v, 7, 12, 0)
end

B.hour_bundle = function(v)
	potion(v, -7, 1, 3, "yellow", "yellowL", nil, nil)
	potion(v, 7, 1, 3, "cyan", "cyanL", nil, nil)
	potion(v, 0, -2, 5, "pink", "pinkL", "heart", "red")
	sparkle(v, 0, 17, 0)
	sparkle(v, -10, 12, -1)
	sparkle(v, 10, 12, -1)
end

B.luck30 = function(v)
	potion(v, 0, 0, 5, "green", "greenL", "clover", "greenD")
	sparkle(v, 7, 10, -2)
	sparkle(v, -7, 13, -1)
end

-- глобус на подставке со значком x2
B.server15 = function(v)
	v:cylY(0, 0, 4, 0, 0, "brownD")
	v:cylY(0, 0, 2.6, 1, 1, "brown")
	v:box(-1, 2, -1, 0, 3, 0, "gold2")
	local cy = 9
	for x = -6, 6 do
		for y = cy - 6, cy + 6 do
			for z = -6, 6 do
				local d2 = x * x + (y - cy) ^ 2 + z * z
				if d2 <= 5.4 * 5.4 then
					-- материки: пятна зелёного
					local land = ((x + 2) ^ 2 + (y - cy - 2) ^ 2 + (z + 5) ^ 2 < 15) or ((x - 3) ^ 2 + (y - cy + 2) ^ 2 + (z + 4) ^ 2 < 13) or ((x + 1) ^ 2 + (y - cy + 3) ^ 2 + (z - 4) ^ 2 < 14)
					v:set(x, y, z, land and "green" or "blue")
				end
			end
		end
	end
	v:ellipsoid(-2.4, cy + 3, -3.8, 1.3, 1.6, 0.8, "blueL")
	-- значок x2
	v:cylZ(7, 15, 3.2, -6, -5, "gold2")
	v:cylZ(7, 15, 2.5, -7, -6, "gold")
	v:glyph({ "XXX", "..X", "XXX", "X..", "XXX" }, 6, 13, -8, { X = "white" })
	sparkle(v, -8, 14, -2)
	sparkle(v, -7, 5, -2)
end

-- рюкзак: высокий, с клапаном, карманом, лямками и ручкой
B.bag = function(v)
	v:box(-4, 0, -3, 4, 9, 3, "green")
	v:ellipsoid(0, 9, 0, 4.7, 3.4, 3.6, "green") -- скруглённый верх
	v:box(-4, 0, -3, 4, 0, 3, "greenD")
	for _, p in { { -4, 0 }, { 4, 0 } } do
		v:clear(p[1], p[2], -3)
		v:clear(p[1], p[2], 3)
	end
	v:recolor(function(x, y, z)
		return y >= 8 and z <= -1
	end, "greenD") -- клапан
	v:box(-3, 1, -5, 3, 5, -4, "greenD") -- карман
	v:box(-3, 5, -5, 3, 5, -4, "brown")
	v:box(-1, 5, -6, 0, 7, -6, "gold") -- пряжка
	v:box(-1, 5, -6, 0, 5, -6, "goldHi")
	v:box(-5, 1, -2, -5, 8, 2, "brown") -- лямки
	v:box(5, 1, -2, 5, 8, 2, "brown")
	v:box(-2, 12, -1, -2, 13, 1, "brown") -- ручка
	v:box(2, 12, -1, 2, 13, 1, "brown")
	v:box(-2, 13, -1, 2, 13, 1, "brown")
	sparkle(v, 8, 11, -2)
	sparkle(v, -8, 6, -1)
end

---------------------------------------------------------------------
-- публичное API
---------------------------------------------------------------------
local UNIT = 0.2
local cache: { [string]: Model? } = {}

function ShopVoxels.has(kind: string): boolean
	return B[kind] ~= nil
end

-- Готовый шаблон модели (общий, не менять: UI.viewport клонирует сам). nil, если для kind нет иконки.
function ShopVoxels.build(kind: string): Model?
	local fn = B[kind]
	if not fn then
		return nil
	end
	local m = cache[kind]
	if m then
		return m
	end
	local ok, res = pcall(function()
		local v = Vox.new()
		fn(v)
		return v:build(kind, UNIT)
	end)
	if not ok then
		warn("[ShopVoxels] " .. kind .. ": " .. tostring(res))
		return nil
	end
	cache[kind] = res
	return res
end

-- Для проверки: сколько деталей в модели
function ShopVoxels.kinds(): { string }
	local list = {}
	for k in B do
		table.insert(list, k)
	end
	table.sort(list)
	return list
end

return ShopVoxels
