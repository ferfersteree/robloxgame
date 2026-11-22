-- ReplicatedStorage/Shared/Config.luau
-- v2: весь баланс, тексты и визуальные настройки. Меняй цифры здесь.
local Config = {}

-- Округление до 3 значащих цифр (цены и награды выглядят чисто).
local function round3(x: number): number
	if x <= 0 then
		return 0
	end
	local p = 10 ^ (math.floor(math.log10(x)) - 2)
	return math.floor(x / p + 0.5) * p
end
Config.round3 = round3

Config.GAME_NAME = "Spear Hunt"
Config.VERSION = "4.0-market"
-- "Demo"   — всё работает на клиенте (фейковый бэкенд, сохранение не нужно)
-- "Remote" — клиент шлёт действия на сервер через Remotes.Request (см. docs/BACKEND.md)
Config.BACKEND = "Demo"
Config.DEMO_LATENCY = 0.08 -- имитация задержки сервера в демо, сек
Config.MAX_PLAYERS = 6
Config.WALK_SPEED = 20
Config.GROUND_Y = 0.1
Config.FOREST_ORIGIN_Z = -3
Config.MAX_THROW_DISTANCE = 12700
-- Caps keep the new long-range progression from guaranteeing rare catches.
Config.RARITY_CHANCE_CAPS = { [2] = 0.35, [3] = 0.22, [4] = 0.12, [5] = 0.025, [6] = 0.002 }

Config.START = {
	coins = 50,
	power = 10,
	bagCap = 12,
	dumbbell = 1,
	spear = "stick",
}

---------------------------------------------------------------------
-- Натяжение: держишь — множитель растёт m(t) = e^(r·t), в скрытый момент «СРЫВ»
---------------------------------------------------------------------
Config.TENSION = {
	rate = 0.6, -- r: ×100 примерно за 7.7 с (V68: было 1.0 и 4.6 с; срывов столько же: точка срыва задаётся множителем, не временем)
	cap = 100, -- на капе бросок происходит сам
	tellTime = 0.6, -- за сколько секунд до срыва копьё начинает сильно дрожать (V65: было 0.42, больше времени отпустить)
	slipEase = 0.55, -- V65: множитель «хрупкости» alpha всех копий: меньше — реже срыв (1 — как до V65)
	crashLuck = 0.25, -- остаётся четверть удачи, накопленной прямо перед срывом
	crashDist = 1, -- срыв сохраняет дальность заряженного броска
	minHold = 0.12, -- короче — это «клик», бросок ×1
	cooldown = 0.9,
}
-- Ступени множителя: свой бросок, след, звук, камера, надпись
Config.TIERS = {
	{ m = 1, name = "THROW", color = Color3.fromRGB(235, 235, 235), color2 = Color3.fromRGB(170, 180, 190), clip = "Throw1", slowmo = 0, orbit = 0, shake = 0 },
	{ m = 2, name = "STRONG", color = Color3.fromRGB(110, 230, 120), color2 = Color3.fromRGB(40, 170, 70), clip = "Throw2", slowmo = 0, orbit = 0, shake = 0.1 },
	{ m = 5, name = "POWERFUL", color = Color3.fromRGB(80, 170, 255), color2 = Color3.fromRGB(30, 90, 220), clip = "Throw5", slowmo = 0.25, orbit = 0.25, shake = 0.2 },
	{ m = 10, name = "HURRICANE", color = Color3.fromRGB(190, 100, 255), color2 = Color3.fromRGB(110, 40, 220), clip = "Throw10", slowmo = 0.45, orbit = 0.5, shake = 0.35 },
	{ m = 25, name = "THUNDER", color = Color3.fromRGB(255, 190, 40), color2 = Color3.fromRGB(255, 110, 20), clip = "Throw25", slowmo = 0.7, orbit = 0.8, shake = 0.55 },
	{ m = 100, name = "LEGEND", color = Color3.fromRGB(255, 70, 110), color2 = Color3.fromRGB(255, 220, 90), clip = "Throw100", slowmo = 1.0, orbit = 1.0, shake = 0.9 },
}

Config.THROW = {
	rangeK = 8, -- V86: не используется для дальности (см. Config.range); 8·√Сила осталась только как мерка удачи в powerLuck
	maxRange = 12700,
	maxFlightTime = 6.5,
	flightSlow = 0.97, -- V86: множитель длительности полёта; было 1.45, игрок попросил в 1.5 раза быстрее (1.45 / 1.5); 1 — как в V85
	minFrac = 0.3, -- при ×1 летит на 30% дальности, при ×100 — на 100%
	flightBase = 0.7,
	flightPerStud = 1 / 75,
	arcFrac = 0.18,
	distLuckDiv = 40,
}

---------------------------------------------------------------------
-- Редкости, мутации, зоны
---------------------------------------------------------------------
Config.RARITIES = {
	{ id = "common", name = "Common", odds = 1, color = Color3.fromRGB(205, 210, 218), dark = Color3.fromRGB(120, 128, 140) },
	{ id = "uncommon", name = "Uncommon", odds = 10, color = Color3.fromRGB(88, 214, 108), dark = Color3.fromRGB(30, 130, 56) },
	{ id = "rare", name = "Rare", odds = 60, color = Color3.fromRGB(64, 160, 255), dark = Color3.fromRGB(20, 80, 190) },
	{ id = "epic", name = "Epic", odds = 400, color = Color3.fromRGB(180, 86, 255), dark = Color3.fromRGB(96, 30, 170) },
	{ id = "legendary", name = "Legendary", odds = 4000, color = Color3.fromRGB(255, 180, 30), dark = Color3.fromRGB(200, 96, 10) },
	{ id = "secret", name = "Secret", odds = 80000, color = Color3.fromRGB(255, 56, 96), dark = Color3.fromRGB(150, 10, 50) },
}

Config.MUTATIONS = {
	gold = { name = "Golden", mult = 5, base = 60, cap = 0.3, color = Color3.fromRGB(255, 200, 50) },
	rainbow = { name = "Rainbow", mult = 15, base = 600, cap = 0.1, color = Color3.fromRGB(255, 120, 220) },
}

-- Зоны леса по дистанции от засады (студы = «метры»). look — свет/туман, когда камера в зоне
Config.ZONES = {
	{ id = 1, name = "Forest Edge", from = 0, to = 35, color = Color3.fromHex("#78c85a"), icon = "🌼", desc = "A sunny meadow, a stream and butterflies.", mechanic = "Watch for rustling grass before an animal leaves its cover.", activeCap = 12, rareLargeCap = 1, look = { ClockTime = 14.2, Brightness = 2.6, Ambient = Color3.fromHex("#78a679"), OutdoorAmbient = Color3.fromHex("#b3c0d5"), FogColor = Color3.fromHex("#c8e1ff"), Density = 0.26, Haze = 1.1, AtmoColor = Color3.fromHex("#d1e0f2"), Decay = Color3.fromHex("#94acce"), Tint = Color3.fromHex("#f0f9ec"), Saturation = 0.2, Contrast = 0.08, Bloom = 0.5 } },
	{ id = 2, name = "Deep Woods", from = 35, to = 80, color = Color3.fromHex("#46a0ff"), icon = "🌲", desc = "Shaded pines, mist, fireflies and cobwebs.", mechanic = "Fireflies outline narrow passages through the shaded forest.", activeCap = 11, rareLargeCap = 1, look = { ClockTime = 17.4, Brightness = 1.4, Ambient = Color3.fromHex("#45666a"), OutdoorAmbient = Color3.fromHex("#9badc0"), FogColor = Color3.fromHex("#7896aa"), Density = 0.42, Haze = 2.4, AtmoColor = Color3.fromHex("#96afbe"), Decay = Color3.fromHex("#6883a0"), Tint = Color3.fromHex("#e5eae8"), Saturation = 0.05, Contrast = 0.12, Bloom = 0.8 } },
	{ id = 3, name = "Wild Marsh", from = 80, to = 140, color = Color3.fromHex("#b456ff"), icon = "🍄", desc = "Swamps, fallen branches, glowing mushrooms and mossy ruins.", mechanic = "Reeds and ripples reveal movement near the marsh pools.", activeCap = 10, rareLargeCap = 1, look = { ClockTime = 19.2, Brightness = 0.8, Ambient = Color3.fromHex("#4c6a70"), OutdoorAmbient = Color3.fromHex("#8fab9c"), FogColor = Color3.fromHex("#6ea05a"), Density = 0.5, Haze = 3.2, AtmoColor = Color3.fromHex("#78aa64"), Decay = Color3.fromHex("#638874"), Tint = Color3.fromHex("#e7ebea"), Saturation = 0.1, Contrast = 0.15, Bloom = 1 } },
	{ id = 4, name = "Ancient Forest", from = 140, to = 230, color = Color3.fromHex("#ffb41e"), icon = "❄️", desc = "Giant trees, crystals, spirit lights and snow.", mechanic = "Spirit lights trace a path between the giant roots.", activeCap = 9, rareLargeCap = 1, look = { ClockTime = 0.4, Brightness = 1.6, Ambient = Color3.fromHex("#94aec5"), OutdoorAmbient = Color3.fromHex("#a7b5da"), FogColor = Color3.fromHex("#aabeff"), Density = 0.38, Haze = 1.6, AtmoColor = Color3.fromHex("#b4c4ff"), Decay = Color3.fromHex("#8499ce"), Tint = Color3.fromHex("#f6fafc"), Saturation = 0.12, Contrast = 0.1, Bloom = 1.1 } },
	{ id = 5, name = "Amber Savanna", from = 230, to = 340, color = Color3.fromHex("#f8bf37"), icon = "☀️", desc = "Golden grass, acacia trees and warm weathered stones.", mechanic = "Tall grass bends before a herd crosses the clearing.", activeCap = 10, rareLargeCap = 1, look = { ClockTime = 15.5, Brightness = 2.5, Ambient = Color3.fromHex("#a49465"), OutdoorAmbient = Color3.fromHex("#bdb7a4"), FogColor = Color3.fromHex("#e9c979"), Density = 0.18, Haze = 0.8, AtmoColor = Color3.fromHex("#e9c979"), Decay = Color3.fromHex("#a69f85"), Tint = Color3.fromHex("#faf5e7"), Saturation = 0.15, Contrast = 0.09, Bloom = 0.35 } },
	{ id = 6, name = "Red Canyons", from = 340, to = 470, color = Color3.fromHex("#ee7442"), icon = "🏜️", desc = "Red sandstone cliffs, narrow trails and natural stone arches.", mechanic = "Echoes and drifting feathers reveal movement near the canyon arches.", activeCap = 9, rareLargeCap = 1, look = { ClockTime = 16.3, Brightness = 2.2, Ambient = Color3.fromHex("#946361"), OutdoorAmbient = Color3.fromHex("#b7a7aa"), FogColor = Color3.fromHex("#dca287"), Density = 0.2, Haze = 1.1, AtmoColor = Color3.fromHex("#dca287"), Decay = Color3.fromHex("#9f898c"), Tint = Color3.fromHex("#f6eae6"), Saturation = 0.13, Contrast = 0.12, Bloom = 0.4 } },
	{ id = 7, name = "Mirage Dunes", from = 470, to = 620, color = Color3.fromHex("#f2d470"), icon = "🐪", desc = "Rolling dunes, hidden oases and ruins beneath the sand.", mechanic = "A shimmer above the dunes may conceal a creature near the oasis.", activeCap = 9, rareLargeCap = 1, look = { ClockTime = 14.8, Brightness = 2.6, Ambient = Color3.fromHex("#a79f7f"), OutdoorAmbient = Color3.fromHex("#bdbcb2"), FogColor = Color3.fromHex("#ebd59c"), Density = 0.19, Haze = 1.3, AtmoColor = Color3.fromHex("#ebd59c"), Decay = Color3.fromHex("#a8a598"), Tint = Color3.fromHex("#fbf7ed"), Saturation = 0.12, Contrast = 0.08, Bloom = 0.38 } },
	{ id = 8, name = "Emerald Jungle", from = 620, to = 800, color = Color3.fromHex("#37c667"), icon = "🌴", desc = "Broad leaves, trailing vines and overgrown jungle temples.", mechanic = "Shaking leaves and loose vines reveal hidden jungle paths.", activeCap = 10, rareLargeCap = 1, look = { ClockTime = 13.7, Brightness = 2, Ambient = Color3.fromHex("#42746d"), OutdoorAmbient = Color3.fromHex("#8fb2ac"), FogColor = Color3.fromHex("#77bc8d"), Density = 0.24, Haze = 1.5, AtmoColor = Color3.fromHex("#77bc8d"), Decay = Color3.fromHex("#689890"), Tint = Color3.fromHex("#e5eee9"), Saturation = 0.16, Contrast = 0.1, Bloom = 0.55 } },
	{ id = 9, name = "Mangrove Marshes", from = 800, to = 1010, color = Color3.fromHex("#62ab64"), icon = "🐊", desc = "Warm channels, tangled mangrove roots and quiet green pools.", mechanic = "Watch the waterline for bubbles and moving roots.", activeCap = 9, rareLargeCap = 1, look = { ClockTime = 17.5, Brightness = 1.7, Ambient = Color3.fromHex("#547572"), OutdoorAmbient = Color3.fromHex("#96aaaa"), FogColor = Color3.fromHex("#88a888"), Density = 0.28, Haze = 1.8, AtmoColor = Color3.fromHex("#88a888"), Decay = Color3.fromHex("#718d8d"), Tint = Color3.fromHex("#e9eeea"), Saturation = 0.08, Contrast = 0.1, Bloom = 0.55 } },
	{ id = 10, name = "Storm Highlands", from = 1010, to = 1250, color = Color3.fromHex("#8cb1fa"), icon = "⚡", desc = "Rocky ledges, thunderclouds and lightning-struck obelisks.", mechanic = "Charged stones flash before flying creatures cross the ridge.", activeCap = 8, rareLargeCap = 1, look = { ClockTime = 18.2, Brightness = 1.8, Ambient = Color3.fromHex("#7084a0"), OutdoorAmbient = Color3.fromHex("#9dabc5"), FogColor = Color3.fromHex("#9aabcc"), Density = 0.25, Haze = 1.9, AtmoColor = Color3.fromHex("#9aabcc"), Decay = Color3.fromHex("#7b8eb2"), Tint = Color3.fromHex("#eff1f4"), Saturation = 0.05, Contrast = 0.14, Bloom = 0.8 } },
	{ id = 11, name = "Azure Coast", from = 1250, to = 1530, color = Color3.fromHex("#36cfe2"), icon = "🏝️", desc = "White beaches, tidal caves and bright coral lagoons.", mechanic = "Tides uncover temporary resting places on the coastal rocks.", activeCap = 9, rareLargeCap = 1, look = { ClockTime = 13.3, Brightness = 2.5, Ambient = Color3.fromHex("#b3b4aa"), OutdoorAmbient = Color3.fromHex("#9ec1d3"), FogColor = Color3.fromHex("#9de1ed"), Density = 0.16, Haze = 0.65, AtmoColor = Color3.fromHex("#9de1ed"), Decay = Color3.fromHex("#7dacc5"), Tint = Color3.fromHex("#fdfcf6"), Saturation = 0.16, Contrast = 0.08, Bloom = 0.55 } },
	{ id = 12, name = "Coral Depths", from = 1530, to = 1850, color = Color3.fromHex("#46a8eb"), icon = "🪸", desc = "An underwater world of coral, sunken gates and glowing kelp.", mechanic = "Bubbles and glowing kelp mark the paths of swimming creatures.", activeCap = 8, rareLargeCap = 1, look = { ClockTime = 12.5, Brightness = 1.7, Ambient = Color3.fromHex("#487fa5"), OutdoorAmbient = Color3.fromHex("#85a4c3"), FogColor = Color3.fromHex("#5d9ac5"), Density = 0.23, Haze = 1.2, AtmoColor = Color3.fromHex("#5d9ac5"), Decay = Color3.fromHex("#5985ae"), Tint = Color3.fromHex("#e6f0f5"), Saturation = 0.1, Contrast = 0.08, Bloom = 0.75 } },
	{ id = 13, name = "Ash Plateau", from = 1850, to = 2220, color = Color3.fromHex("#bf806d"), icon = "🌋", desc = "Cooled lava flows, dark sand and drifting embers.", mechanic = "Drifting embers reveal movement across the dark plateau.", activeCap = 8, rareLargeCap = 1, look = { ClockTime = 17.8, Brightness = 1.8, Ambient = Color3.fromHex("#636a7d"), OutdoorAmbient = Color3.fromHex("#9d9fa9"), FogColor = Color3.fromHex("#9b8c86"), Density = 0.22, Haze = 1.4, AtmoColor = Color3.fromHex("#9b8c86"), Decay = Color3.fromHex("#7c7d8c"), Tint = Color3.fromHex("#ecebec"), Saturation = -0.02, Contrast = 0.12, Bloom = 0.8 } },
	{ id = 14, name = "Volcano Heart", from = 2220, to = 2640, color = Color3.fromHex("#ff6f35"), icon = "🔥", desc = "Magma bridges, obsidian arches and glowing volcanic vents.", mechanic = "Lava pulses light the routes between the cooled platforms.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 20, Brightness = 1.6, Ambient = Color3.fromHex("#4a5167"), OutdoorAmbient = Color3.fromHex("#af9a9d"), FogColor = Color3.fromHex("#c88168"), Density = 0.24, Haze = 1.6, AtmoColor = Color3.fromHex("#c88168"), Decay = Color3.fromHex("#94777b"), Tint = Color3.fromHex("#e6e6e8"), Saturation = 0.08, Contrast = 0.15, Bloom = 1 } },
	{ id = 15, name = "Crystal Caverns", from = 2640, to = 3120, color = Color3.fromHex("#b979ff"), icon = "💎", desc = "Amethyst clusters, crystal bridges and reflective underground pools.", mechanic = "Crystal reflections briefly reveal creatures behind the formations.", activeCap = 8, rareLargeCap = 1, look = { ClockTime = 0.7, Brightness = 1.7, Ambient = Color3.fromHex("#676f93"), OutdoorAmbient = Color3.fromHex("#a5a7ca"), FogColor = Color3.fromHex("#afa0d8"), Density = 0.22, Haze = 1.1, AtmoColor = Color3.fromHex("#afa0d8"), Decay = Color3.fromHex("#8688b9"), Tint = Color3.fromHex("#ededf1"), Saturation = 0.1, Contrast = 0.14, Bloom = 1 } },
	{ id = 16, name = "Lunar Tundra", from = 3120, to = 3670, color = Color3.fromHex("#b4d8ff"), icon = "🌙", desc = "Snowy plains, luminous ice and a great silver moon.", mechanic = "Moonlit tracks and drifting snow show the safest route.", activeCap = 8, rareLargeCap = 1, look = { ClockTime = 0.2, Brightness = 1.8, Ambient = Color3.fromHex("#9bb1c6"), OutdoorAmbient = Color3.fromHex("#a9b8d3"), FogColor = Color3.fromHex("#b8cced"), Density = 0.2, Haze = 0.9, AtmoColor = Color3.fromHex("#b8cced"), Decay = Color3.fromHex("#8ba0c5"), Tint = Color3.fromHex("#f8fbfc"), Saturation = 0.05, Contrast = 0.1, Bloom = 0.9 } },
	{ id = 17, name = "Sky Islands", from = 3670, to = 4290, color = Color3.fromHex("#91e5ee"), icon = "☁️", desc = "Floating cliffs, cloud bridges and ancient wind runes.", mechanic = "Wind trails reveal the direction of creatures between the islands.", activeCap = 8, rareLargeCap = 1, look = { ClockTime = 14, Brightness = 2.3, Ambient = Color3.fromHex("#8aa6bf"), OutdoorAmbient = Color3.fromHex("#aec4d3"), FogColor = Color3.fromHex("#c5e9ef"), Density = 0.16, Haze = 0.7, AtmoColor = Color3.fromHex("#c5e9ef"), Decay = Color3.fromHex("#93b0c6"), Tint = Color3.fromHex("#f4f9fb"), Saturation = 0.12, Contrast = 0.08, Bloom = 0.65 } },
	{ id = 18, name = "Twilight Rift", from = 4290, to = 5000, color = Color3.fromHex("#9b70d5"), icon = "🌀", desc = "Shadowy rifts, glowing spores and impossible rock ledges.", mechanic = "Glowing spores trace the edges of the shadow paths.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 1.5, Brightness = 1.5, Ambient = Color3.fromHex("#495171"), OutdoorAmbient = Color3.fromHex("#989bb9"), FogColor = Color3.fromHex("#8e83ad"), Density = 0.22, Haze = 1.3, AtmoColor = Color3.fromHex("#8e83ad"), Decay = Color3.fromHex("#7478a1"), Tint = Color3.fromHex("#e6e6ea"), Saturation = 0.05, Contrast = 0.15, Bloom = 0.95 } },
	{ id = 19, name = "Starbound Frontier", from = 5000, to = 5800, color = Color3.fromHex("#756aff"), icon = "🌌", desc = "Cosmic islands, stardust and the rings of an ancient portal.", mechanic = "The portal rings light up in the order a creature approaches.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 0.3, Brightness = 1.7, Ambient = Color3.fromHex("#565b8a"), OutdoorAmbient = Color3.fromHex("#9ba1c5"), FogColor = Color3.fromHex("#9691cb"), Density = 0.2, Haze = 1.1, AtmoColor = Color3.fromHex("#9691cb"), Decay = Color3.fromHex("#7980b2"), Tint = Color3.fromHex("#e9e8ef"), Saturation = 0.1, Contrast = 0.12, Bloom = 1.05 } },
	{ id = 20, name = "Rust Gardens", from = 5800, to = 6700, color = Color3.fromHex("#c9803a"), icon = "⚙️", desc = "Overgrown gear gardens, copper pipes and slow clockwork blooms.", mechanic = "Ticking gears reveal where a clockwork creature is hiding.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 16.5, Brightness = 1.9, Ambient = Color3.fromHex("#7a6a55"), OutdoorAmbient = Color3.fromHex("#b0a08a"), FogColor = Color3.fromHex("#c4a070"), Density = 0.24, Haze = 1.5, AtmoColor = Color3.fromHex("#c4a070"), Decay = Color3.fromHex("#8a7a62"), Tint = Color3.fromHex("#f3ead8"), Saturation = 0.1, Contrast = 0.12, Bloom = 0.5 } },
	{ id = 21, name = "Fungal Bogs", from = 6700, to = 7700, color = Color3.fromHex("#7bd6b0"), icon = "🍄", desc = "Giant caps, glowing spores and damp peat.", mechanic = "Drifting spores glow brighter near a hidden creature.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 19.5, Brightness = 1.0, Ambient = Color3.fromHex("#3f6a60"), OutdoorAmbient = Color3.fromHex("#86aa9c"), FogColor = Color3.fromHex("#6fb89a"), Density = 0.45, Haze = 3.0, AtmoColor = Color3.fromHex("#7cc4a4"), Decay = Color3.fromHex("#5f8a78"), Tint = Color3.fromHex("#e6f0ea"), Saturation = 0.12, Contrast = 0.14, Bloom = 1.0 } },
	{ id = 22, name = "Bone Dunes", from = 7700, to = 8800, color = Color3.fromHex("#e8dcc0"), icon = "🦴", desc = "Fossil ribs, bleached dunes and buried skeleton arches.", mechanic = "Rattling bones in the sand give away what is moving below.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 15.0, Brightness = 2.4, Ambient = Color3.fromHex("#a39a82"), OutdoorAmbient = Color3.fromHex("#c4bca6"), FogColor = Color3.fromHex("#e6dcc0"), Density = 0.18, Haze = 0.8, AtmoColor = Color3.fromHex("#e6dcc0"), Decay = Color3.fromHex("#a8a08a"), Tint = Color3.fromHex("#faf6ea"), Saturation = 0.1, Contrast = 0.09, Bloom = 0.35 } },
	{ id = 23, name = "Sunken Citadel", from = 8800, to = 10000, color = Color3.fromHex("#3aa0c8"), icon = "🏰", desc = "A drowned fortress of pearl walls, glowing vents and slow currents.", mechanic = "Bubbles rise along the walls where something big is swimming.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 12.0, Brightness = 1.2, Ambient = Color3.fromHex("#3f7098"), OutdoorAmbient = Color3.fromHex("#7fa2c0"), FogColor = Color3.fromHex("#4f8fba"), Density = 0.3, Haze = 1.6, AtmoColor = Color3.fromHex("#5a9ac4"), Decay = Color3.fromHex("#4f7ea6"), Tint = Color3.fromHex("#e2eef6"), Saturation = 0.1, Contrast = 0.1, Bloom = 0.8 } },
	{ id = 24, name = "Storm Rift", from = 10000, to = 11300, color = Color3.fromHex("#8a7cff"), icon = "🌩️", desc = "A torn sky of lightning, floating shards and humming fulgurite.", mechanic = "Lightning strikes the ground just before a creature crosses the rift.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 21.0, Brightness = 1.3, Ambient = Color3.fromHex("#5a5a8c"), OutdoorAmbient = Color3.fromHex("#9a9ac4"), FogColor = Color3.fromHex("#8a80c8"), Density = 0.26, Haze = 1.7, AtmoColor = Color3.fromHex("#8e84cc"), Decay = Color3.fromHex("#6c68a8"), Tint = Color3.fromHex("#e8e8f4"), Saturation = 0.08, Contrast = 0.15, Bloom = 1.1 } },
	{ id = 25, name = "Primordial Caldera", from = 11300, to = 12700, color = Color3.fromHex("#ff7a3d"), icon = "🌋", desc = "The first volcano: molten lakes, ancient ash and giant fossils.", mechanic = "The ground glows hotter along the route of the biggest creature.", activeCap = 7, rareLargeCap = 1, look = { ClockTime = 18.0, Brightness = 1.7, Ambient = Color3.fromHex("#6a4a44"), OutdoorAmbient = Color3.fromHex("#b09890"), FogColor = Color3.fromHex("#d87850"), Density = 0.26, Haze = 1.8, AtmoColor = Color3.fromHex("#d88056"), Decay = Color3.fromHex("#8e6a62"), Tint = Color3.fromHex("#f0e4de"), Saturation = 0.08, Contrast = 0.15, Bloom = 1.1 } },
}
-- Свет деревни/витрины
-- Separate camp profile: warm local lights should not wash out the plaza.
-- Biome lighting remains independent and retains its authored profiles.
Config.VILLAGE_LOOK = {
 ClockTime = 14.2, Brightness = 1.8,
 Ambient = Color3.fromHex("#6b7279"), OutdoorAmbient = Color3.fromHex("#9ba5b1"),
 FogColor = Color3.fromHex("#c8e1ff"), Density = 0.20, Haze = 0.8,
 AtmoColor = Color3.fromHex("#d1e0f2"), Decay = Color3.fromHex("#94acce"),
 Tint = Color3.fromHex("#fffdf6"), Saturation = 0.12, Contrast = 0.06, Bloom = 0.12,
}

---------------------------------------------------------------------
-- Виды. rarity 1..6; sharp/weight — требования к копью; price — цена при среднем весе
---------------------------------------------------------------------
Config.SPECIES = {
	{ id = "rabbit", icon = "🐇", zone = 1, rarity = 1, wMin = 1, wMax = 3, price = 3, sharp = 1, weight = 1, name = "Rabbit", fact = "Radar ears: it can hear rustling from 30 meters away.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 35, habitatDescription = "A sunny meadow, a stream and butterflies." },
	{ id = "squirrel", icon = "🐿️", zone = 1, rarity = 1, wMin = 0.3, wMax = 0.9, price = 2, sharp = 1, weight = 1, name = "Squirrel", fact = "Forgets where it hid half of its nuts.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 28, habitatDescription = "A sunny meadow, a stream and butterflies." },
	{ id = "hedgehog", icon = "🦔", zone = 1, rarity = 2, wMin = 0.6, wMax = 1.6, price = 7, sharp = 1, weight = 1, name = "Hedgehog", fact = "Five thousand spines and not a mean thought.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 18, habitatDescription = "A sunny meadow, a stream and butterflies." },
	{ id = "fox", icon = "🦊", zone = 1, rarity = 3, wMin = 4, wMax = 9, price = 25, sharp = 1, weight = 1, name = "Fox", fact = "Dives headfirst into snow to catch mice.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 11, habitatDescription = "A sunny meadow, a stream and butterflies." },
	{ id = "dodo", icon = "🦤", zone = 1, rarity = 4, wMin = 10, wMax = 20, price = 90, sharp = 1, weight = 1, name = "Dodo", fact = "Thought to be extinct. Apparently not.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 6, habitatDescription = "A sunny meadow, a stream and butterflies." },
	{ id = "moonrabbit", icon = "🐰", zone = 1, rarity = 5, wMin = 3, wMax = 6, price = 700, sharp = 2, weight = 1, name = "Moon Rabbit", fact = "Appears when moonlight reaches the meadow.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 2, habitatDescription = "A sunny meadow, a stream and butterflies." },
	{ id = "roe", icon = "🦌", zone = 2, rarity = 1, wMin = 15, wMax = 35, price = 9, sharp = 1, weight = 1, name = "Roe Deer", fact = "Can leap six meters from a standstill.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 35, habitatDescription = "Shaded pines, mist, fireflies and cobwebs." },
	{ id = "boar", icon = "🐗", zone = 2, rarity = 1, wMin = 40, wMax = 100, price = 12, sharp = 1, weight = 1, name = "Boar", fact = "Its snout can smell a truffle a meter underground.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 28, habitatDescription = "Shaded pines, mist, fireflies and cobwebs." },
	{ id = "badger", icon = "🦡", zone = 2, rarity = 2, wMin = 7, wMax = 16, price = 22, sharp = 2, weight = 1, name = "Badger", fact = "Builds burrows with a dozen exits.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 18, habitatDescription = "Shaded pines, mist, fireflies and cobwebs." },
	{ id = "wolf", icon = "🐺", zone = 2, rarity = 3, wMin = 30, wMax = 70, price = 60, sharp = 2, weight = 2, name = "Wolf", fact = "Its howl can be heard ten kilometers away.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 11, habitatDescription = "Shaded pines, mist, fireflies and cobwebs." },
	{ id = "lynx", icon = "🐈", zone = 2, rarity = 4, wMin = 15, wMax = 35, price = 200, sharp = 2, weight = 2, name = "Lynx", fact = "Those ear tufts look like little antennas.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 6, habitatDescription = "Shaded pines, mist, fireflies and cobwebs." },
	{ id = "sabertooth", icon = "🐅", zone = 2, rarity = 5, wMin = 150, wMax = 300, price = 1800, sharp = 3, weight = 3, name = "Saber-toothed Cat", fact = "Its fangs are as long as your arm.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 2, habitatDescription = "Shaded pines, mist, fireflies and cobwebs." },
	{ id = "deer", icon = "🦌", zone = 3, rarity = 1, wMin = 80, wMax = 200, price = 45, sharp = 2, weight = 2, name = "Deer", fact = "Grows a new set of antlers every year.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 32, habitatDescription = "Swamps, fallen branches, glowing mushrooms and mossy ruins." },
	{ id = "moose", icon = "🦌", zone = 3, rarity = 2, wMin = 300, wMax = 600, price = 110, sharp = 2, weight = 3, name = "Moose", fact = "A strong swimmer that dives for plants.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 25, habitatDescription = "Swamps, fallen branches, glowing mushrooms and mossy ruins." },
	{ id = "bear", icon = "🐻", zone = 3, rarity = 3, wMin = 150, wMax = 400, price = 320, sharp = 3, weight = 3, name = "Bear", fact = "Loves honey. And berries. And fish. And sleep.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 18, habitatDescription = "Swamps, fallen branches, glowing mushrooms and mossy ruins." },
	{ id = "bison", icon = "🦬", zone = 3, rarity = 4, wMin = 500, wMax = 900, price = 1000, sharp = 3, weight = 4, name = "Bison", fact = "The heaviest animal in the marsh.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 13, habitatDescription = "Swamps, fallen branches, glowing mushrooms and mossy ruins." },
	{ id = "cavebear", icon = "🐻", zone = 3, rarity = 5, wMin = 400, wMax = 1000, price = 7000, sharp = 4, weight = 4, name = "Cave Bear", fact = "Has slept among the ruins for a thousand years.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 9, habitatDescription = "Swamps, fallen branches, glowing mushrooms and mossy ruins." },
	{ id = "spiritdeer", icon = "👻", zone = 3, rarity = 6, wMin = 100, wMax = 220, price = 40000, sharp = 4, weight = 3, name = "Spirit Deer", fact = "Only three people have seen it. Two did not believe their eyes.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 3, habitatDescription = "Swamps, fallen branches, glowing mushrooms and mossy ruins." },
	{ id = "megadeer", icon = "🦌", zone = 4, rarity = 1, wMin = 400, wMax = 700, price = 180, sharp = 3, weight = 3, name = "Giant Deer", fact = "Its antlers are as wide as a cabin.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 32, habitatDescription = "Giant trees, crystals, spirit lights and snow." },
	{ id = "rhino", icon = "🦏", zone = 4, rarity = 2, wMin = 1500, wMax = 3000, price = 450, sharp = 4, weight = 4, name = "Woolly Rhino", fact = "Its fur is warmer than any winter coat.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 25, habitatDescription = "Giant trees, crystals, spirit lights and snow." },
	{ id = "mammoth", icon = "🦣", zone = 4, rarity = 3, wMin = 4000, wMax = 8000, price = 1400, sharp = 4, weight = 5, name = "Mammoth", fact = "Its tusks keep growing throughout its life.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 18, habitatDescription = "Giant trees, crystals, spirit lights and snow." },
	{ id = "cavelion", icon = "🦁", zone = 4, rarity = 4, wMin = 200, wMax = 400, price = 4000, sharp = 5, weight = 4, name = "Cave Lion", fact = "Its roar shakes snow from the trees.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 13, habitatDescription = "Giant trees, crystals, spirit lights and snow." },
	{ id = "icemammoth", icon = "🦣", zone = 4, rarity = 5, wMin = 6000, wMax = 10000, price = 25000, sharp = 5, weight = 5, name = "Ice Mammoth", fact = "Made of ice, but warm at heart.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 9, habitatDescription = "Giant trees, crystals, spirit lights and snow." },
	{ id = "yeti", icon = "❄️", zone = 4, rarity = 6, wMin = 200, wMax = 500, price = 200000, sharp = 6, weight = 5, name = "Yeti", fact = "A legend of the Ancient Forest. Loves hugs.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 3, habitatDescription = "Giant trees, crystals, spirit lights and snow." },
	{ id = "gazelle", icon = "🦌", zone = 5, rarity = 2, wMin = 25, wMax = 65, price = 5000000, sharp = 6, weight = 4, name = "Gazelle", fact = "A sharp turn is often its best escape from a hunter.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 62, habitatDescription = "Golden grass, acacia trees and warm weathered stones." },
	{ id = "hyena", icon = "🐺", zone = 5, rarity = 4, wMin = 25, wMax = 85, price = 20000000, sharp = 7, weight = 5, name = "Hyena", fact = "Its calls travel a long way across the warm savanna.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 30, habitatDescription = "Golden grass, acacia trees and warm weathered stones." },
	{ id = "sunlion", icon = "🦁", zone = 5, rarity = 5, wMin = 180, wMax = 340, price = 60000000, sharp = 8, weight = 6, name = "Sun Lion", fact = "Its golden mane catches the last light of sunset.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Golden grass, acacia trees and warm weathered stones." },
	{ id = "mountain_goat", icon = "🐐", zone = 6, rarity = 2, wMin = 40, wMax = 110, price = 9250000, sharp = 7, weight = 5, name = "Mountain Goat", fact = "Split hooves help it balance on narrow canyon ledges.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 64, habitatDescription = "Red sandstone cliffs, narrow trails and natural stone arches." },
	{ id = "armadillo", icon = "🦔", zone = 6, rarity = 4, wMin = 15, wMax = 45, price = 37000000, sharp = 8, weight = 6, name = "Armadillo", fact = "Protective plates cover its back like a tiny suit of armor.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Red sandstone cliffs, narrow trails and natural stone arches." },
	{ id = "canyon_condor", icon = "🦅", zone = 6, rarity = 5, wMin = 4, wMax = 18, price = 111000000, sharp = 9, weight = 7, name = "Canyon Condor", fact = "It rides rising air between the red stone arches.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 7, habitatDescription = "Red sandstone cliffs, narrow trails and natural stone arches.", spawnHeights = { 8, 38 } },
	{ id = "fennec", icon = "🦊", zone = 7, rarity = 2, wMin = 4, wMax = 16, price = 17112500, sharp = 8, weight = 6, name = "Fennec Fox", fact = "Oversized ears help it release heat in the desert.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 62, habitatDescription = "Rolling dunes, hidden oases and ruins beneath the sand." },
	{ id = "dune_scorpion", icon = "🦂", zone = 7, rarity = 4, wMin = 12, wMax = 45, price = 68450000, sharp = 9, weight = 7, name = "Dune Scorpion", fact = "It waits beneath the cool edge of a sunlit dune.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 30, habitatDescription = "Rolling dunes, hidden oases and ruins beneath the sand." },
	{ id = "sand_wyrm", icon = "🐍", zone = 7, rarity = 5, wMin = 700, wMax = 1800, price = 205350000, sharp = 10, weight = 8, name = "Sand Wyrm", fact = "A moving ridge of sand is the first sign it is near.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Rolling dunes, hidden oases and ruins beneath the sand." },
	{ id = "toucan", icon = "🦅", zone = 8, rarity = 2, wMin = 4, wMax = 18, price = 31658125, sharp = 9, weight = 7, name = "Toucan", fact = "Its bright bill stands out among the giant leaves.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 64, habitatDescription = "Broad leaves, trailing vines and overgrown jungle temples.", spawnHeights = { 8, 38 } },
	{ id = "jaguar", icon = "🐆", zone = 8, rarity = 4, wMin = 55, wMax = 130, price = 126632500, sharp = 10, weight = 8, name = "Jaguar", fact = "A quiet swimmer and a patient jungle hunter.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Broad leaves, trailing vines and overgrown jungle temples." },
	{ id = "jungle_gorilla", icon = "🦍", zone = 8, rarity = 5, wMin = 150, wMax = 350, price = 379897500, sharp = 11, weight = 9, name = "Jungle Gorilla", fact = "It rests in a nest of broad leaves near the old temple.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 7, habitatDescription = "Broad leaves, trailing vines and overgrown jungle temples." },
	{ id = "otter", icon = "🦦", zone = 9, rarity = 2, wMin = 8, wMax = 22, price = 58567531, sharp = 10, weight = 8, name = "Otter", fact = "It slips between the roots and warm mangrove channels.", habitat = "shore", movementMode = "amphibious", spawnKind = "shore_and_water", populationWeight = 62, habitatDescription = "Warm channels, tangled mangrove roots and quiet green pools.", spawnDepths = { 1, 10 } },
	{ id = "crocodile", icon = "🐊", zone = 9, rarity = 4, wMin = 300, wMax = 800, price = 234270125, sharp = 11, weight = 9, name = "Crocodile", fact = "Only its eyes may show above the still water.", habitat = "shore", movementMode = "amphibious", spawnKind = "shore_and_water", populationWeight = 30, habitatDescription = "Warm channels, tangled mangrove roots and quiet green pools.", spawnDepths = { 1, 10 } },
	{ id = "marsh_hydra", icon = "🐉", zone = 9, rarity = 5, wMin = 800, wMax = 2200, price = 702810375, sharp = 12, weight = 10, name = "Marsh Hydra", fact = "Several watchful heads guard the shallow green pools.", habitat = "ground", movementMode = "ground", spawnKind = "shallow_water_ground", populationWeight = 8, habitatDescription = "Warm channels, tangled mangrove roots and quiet green pools." },
	{ id = "storm_ram", icon = "🐏", zone = 10, rarity = 2, wMin = 65, wMax = 160, price = 108349933, sharp = 11, weight = 9, name = "Storm Ram", fact = "Its heavy horns seem to draw sparks from the mountain air.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 64, habitatDescription = "Rocky ledges, thunderclouds and lightning-struck obelisks." },
	{ id = "thunder_eagle", icon = "🦅", zone = 10, rarity = 4, wMin = 15, wMax = 45, price = 433399731, sharp = 12, weight = 10, name = "Thunder Eagle", fact = "It circles the tallest lightning-struck obelisks.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 29, habitatDescription = "Rocky ledges, thunderclouds and lightning-struck obelisks.", spawnHeights = { 8, 38 } },
	{ id = "storm_griffin", icon = "🦅", zone = 10, rarity = 5, wMin = 300, wMax = 750, price = 1300199194, sharp = 13, weight = 11, name = "Storm Griffin", fact = "A guardian of the open sky above the storm ridges.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 7, habitatDescription = "Rocky ledges, thunderclouds and lightning-struck obelisks.", spawnHeights = { 8, 38 } },
	{ id = "sea_turtle", icon = "🐢", zone = 11, rarity = 2, wMin = 90, wMax = 250, price = 200447376, sharp = 12, weight = 10, name = "Sea Turtle", fact = "It follows familiar routes between the beach and the lagoon.", habitat = "shore", movementMode = "amphibious", spawnKind = "shore_and_water", populationWeight = 62, habitatDescription = "White beaches, tidal caves and bright coral lagoons.", spawnDepths = { 1, 10 } },
	{ id = "sea_lion", icon = "🦭", zone = 11, rarity = 4, wMin = 180, wMax = 500, price = 801789503, sharp = 13, weight = 11, name = "Sea Lion", fact = "It rests on warm rocks just above the tide.", habitat = "shore", movementMode = "amphibious", spawnKind = "shore_and_water", populationWeight = 30, habitatDescription = "White beaches, tidal caves and bright coral lagoons.", spawnDepths = { 1, 10 } },
	{ id = "coral_wyvern", icon = "🐉", zone = 11, rarity = 5, wMin = 450, wMax = 1200, price = 2405368508, sharp = 14, weight = 12, name = "Coral Wyvern", fact = "Its coral-colored fins disappear among the reefs.", habitat = "water", movementMode = "swim", spawnKind = "water", populationWeight = 8, habitatDescription = "White beaches, tidal caves and bright coral lagoons.", spawnDepths = { 2, 12 } },
	{ id = "reef_ray", icon = "🐟", zone = 12, rarity = 2, wMin = 80, wMax = 240, price = 370827645, sharp = 13, weight = 11, name = "Reef Ray", fact = "Broad fins carry it smoothly over the sea floor.", habitat = "water", movementMode = "swim", spawnKind = "water", populationWeight = 64, habitatDescription = "An underwater world of coral, sunken gates and glowing kelp.", spawnDepths = { 3, 18 } },
	{ id = "hammer_shark", icon = "🦈", zone = 12, rarity = 4, wMin = 400, wMax = 1000, price = 1483310580, sharp = 14, weight = 12, name = "Hammerhead Shark", fact = "Its wide head helps it sense movement near the sand.", habitat = "water", movementMode = "swim", spawnKind = "water", populationWeight = 29, habitatDescription = "An underwater world of coral, sunken gates and glowing kelp.", spawnDepths = { 3, 18 } },
	{ id = "abyss_leviathan", icon = "🐋", zone = 12, rarity = 5, wMin = 2500, wMax = 7000, price = 4449931741, sharp = 15, weight = 13, name = "Abyssal Leviathan", fact = "A vast silhouette waits beyond the sunken gate.", habitat = "water", movementMode = "swim", spawnKind = "water", populationWeight = 7, habitatDescription = "An underwater world of coral, sunken gates and glowing kelp.", spawnDepths = { 3, 40 } },
	{ id = "ash_lizard", icon = "🦎", zone = 13, rarity = 2, wMin = 12, wMax = 45, price = 686031143, sharp = 14, weight = 12, name = "Ash Lizard", fact = "Dark scales blend into the cooled volcanic stone.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 62, habitatDescription = "Cooled lava flows, dark sand and drifting embers." },
	{ id = "ember_boar", icon = "🐗", zone = 13, rarity = 4, wMin = 150, wMax = 450, price = 2744124573, sharp = 15, weight = 13, name = "Ember Boar", fact = "Small sparks escape its bristles when it charges.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 30, habitatDescription = "Cooled lava flows, dark sand and drifting embers." },
	{ id = "lava_golem", icon = "🗿", zone = 13, rarity = 5, wMin = 1500, wMax = 4000, price = 8232373720, sharp = 16, weight = 14, name = "Lava Golem", fact = "Glowing seams reveal the heat beneath its stone armor.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Cooled lava flows, dark sand and drifting embers." },
	{ id = "obsidian_crab", icon = "🦀", zone = 14, rarity = 2, wMin = 40, wMax = 150, price = 1269157615, sharp = 15, weight = 13, name = "Obsidian Crab", fact = "Its black shell shines like fresh volcanic glass.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 64, habitatDescription = "Magma bridges, obsidian arches and glowing volcanic vents." },
	{ id = "magma_rhino", icon = "🦏", zone = 14, rarity = 4, wMin = 1800, wMax = 4500, price = 5076630461, sharp = 16, weight = 14, name = "Magma Rhino", fact = "It follows the solid paths between the lava vents.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Magma bridges, obsidian arches and glowing volcanic vents." },
	{ id = "phoenix", icon = "🔥", zone = 14, rarity = 5, wMin = 80, wMax = 220, price = 15229891382, sharp = 17, weight = 15, name = "Phoenix", fact = "A trail of embers marks its flight above the crater.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 7, habitatDescription = "Magma bridges, obsidian arches and glowing volcanic vents.", spawnHeights = { 8, 38 } },
	{ id = "crystal_bat", icon = "🦇", zone = 15, rarity = 2, wMin = 3, wMax = 12, price = 2347941588, sharp = 16, weight = 14, name = "Crystal Bat", fact = "Its wings catch light from the cavern crystals.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 65, habitatDescription = "Amethyst clusters, crystal bridges and reflective underground pools.", spawnHeights = { 8, 38 } },
	{ id = "amethyst_fox", icon = "🦊", zone = 15, rarity = 4, wMin = 4, wMax = 16, price = 9391766352, sharp = 17, weight = 15, name = "Amethyst Fox", fact = "Violet reflections conceal it among the crystal clusters.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Amethyst clusters, crystal bridges and reflective underground pools." },
	{ id = "quartz_dragon", icon = "🐲", zone = 15, rarity = 6, wMin = 1500, wMax = 5500, price = 28175299057, sharp = 18, weight = 16, name = "Quartz Dragon", fact = "It guards a quiet chamber beyond the crystal bridge.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 6, habitatDescription = "Amethyst clusters, crystal bridges and reflective underground pools." },
	{ id = "arctic_hare", icon = "🐇", zone = 16, rarity = 2, wMin = 3, wMax = 10, price = 4343691938, sharp = 17, weight = 15, name = "Arctic Hare", fact = "Its winter coat hides it against the moonlit snow.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 65, habitatDescription = "Snowy plains, luminous ice and a great silver moon." },
	{ id = "lunar_wolf", icon = "🐺", zone = 16, rarity = 4, wMin = 25, wMax = 85, price = 17374767752, sharp = 18, weight = 16, name = "Lunar Wolf", fact = "It follows pale tracks beneath the great silver moon.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Snowy plains, luminous ice and a great silver moon." },
	{ id = "aurora_bear", icon = "🐻", zone = 16, rarity = 6, wMin = 450, wMax = 1200, price = 52124303256, sharp = 19, weight = 17, name = "Aurora Bear", fact = "Northern lights seem to ripple across its thick fur.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 6, habitatDescription = "Snowy plains, luminous ice and a great silver moon." },
	{ id = "cloud_sheep", icon = "🐑", zone = 17, rarity = 2, wMin = 45, wMax = 120, price = 8035830085, sharp = 18, weight = 16, name = "Cloud Sheep", fact = "It grazes on the soft grass of the floating islands.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 65, habitatDescription = "Floating cliffs, cloud bridges and ancient wind runes." },
	{ id = "sky_stag", icon = "🦌", zone = 17, rarity = 4, wMin = 200, wMax = 650, price = 32143320341, sharp = 19, weight = 17, name = "Sky Stag", fact = "Wide antlers frame the drifting clouds behind it.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Floating cliffs, cloud bridges and ancient wind runes." },
	{ id = "sky_drake", icon = "🐲", zone = 17, rarity = 6, wMin = 1500, wMax = 5500, price = 96429961023, sharp = 20, weight = 18, name = "Sky Drake", fact = "It rests on high platforms before a long flight.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 6, habitatDescription = "Floating cliffs, cloud bridges and ancient wind runes.", spawnHeights = { 8, 70 } },
	{ id = "dusk_panther", icon = "🐆", zone = 18, rarity = 2, wMin = 55, wMax = 130, price = 14866285658, sharp = 19, weight = 17, name = "Dusk Panther", fact = "Its silhouette blends into the edges of the rift.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 65, habitatDescription = "Shadowy rifts, glowing spores and impossible rock ledges." },
	{ id = "shadow_mantis", icon = "🦗", zone = 18, rarity = 4, wMin = 25, wMax = 90, price = 59465142631, sharp = 20, weight = 18, name = "Shadow Mantis", fact = "It stays perfectly still among the glowing spores.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Shadowy rifts, glowing spores and impossible rock ledges." },
	{ id = "void_behemoth", icon = "🦬", zone = 18, rarity = 6, wMin = 3500, wMax = 9000, price = 178395427893, sharp = 21, weight = 19, name = "Void Behemoth", fact = "The shadow beneath it seems deeper than the rift itself.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 6, habitatDescription = "Shadowy rifts, glowing spores and impossible rock ledges." },
	{ id = "comet_fox", icon = "🦊", zone = 19, rarity = 2, wMin = 4, wMax = 16, price = 27502628467, sharp = 20, weight = 18, name = "Comet Fox", fact = "Its bright tail traces a short arc through the stardust.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 65, habitatDescription = "Cosmic islands, stardust and the rings of an ancient portal." },
	{ id = "stellar_stag", icon = "🦌", zone = 19, rarity = 4, wMin = 200, wMax = 650, price = 110010513867, sharp = 21, weight = 19, name = "Stellar Stag", fact = "It rests beside the runes before the final portal ring.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Cosmic islands, stardust and the rings of an ancient portal." },
	{ id = "astral_dragon", icon = "🐲", zone = 19, rarity = 6, wMin = 1500, wMax = 5500, price = 330031541601, sharp = 22, weight = 20, name = "Astral Dragon", fact = "It circles the last star gate at the edge of the world.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 6, habitatDescription = "Cosmic islands, stardust and the rings of an ancient portal.", spawnHeights = { 8, 70 } },
	{ id = "watchful_meerkat", icon = "🐿️", zone = 5, rarity = 1, wMin = 0.6, wMax = 1, price = 2500000, sharp = 6, weight = 4, name = "Watchful Meerkat", fact = "One always stands guard while the rest dig.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Golden grass, acacia trees and warm weathered stones." },
	{ id = "savanna_ostrich", icon = "🦤", zone = 5, rarity = 3, wMin = 90, wMax = 150, price = 10000000, sharp = 7, weight = 5, name = "Savanna Ostrich", fact = "Runs faster than any hunter on the open golden plain.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Golden grass, acacia trees and warm weathered stones." },
	{ id = "amber_giraffe", icon = "🦒", zone = 5, rarity = 6, wMin = 800, wMax = 1400, price = 180000000, sharp = 8, weight = 6, name = "Amber Giraffe", fact = "It nibbles the tallest acacia leaves nobody else can reach.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Golden grass, acacia trees and warm weathered stones." },
	{ id = "rock_hyrax", icon = "🐹", zone = 6, rarity = 1, wMin = 3, wMax = 5, price = 4625000, sharp = 7, weight = 5, name = "Rock Hyrax", fact = "Sunbathes on warm ledges and whistles when you get close.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Red sandstone cliffs, narrow trails and natural stone arches." },
	{ id = "canyon_roadrunner", icon = "🐦", zone = 6, rarity = 3, wMin = 0.3, wMax = 0.5, price = 18500000, sharp = 8, weight = 6, name = "Canyon Roadrunner", fact = "Races along canyon trails in a cloud of red dust.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Red sandstone cliffs, narrow trails and natural stone arches." },
	{ id = "redthorn_lizard", icon = "🦎", zone = 6, rarity = 6, wMin = 0.1, wMax = 0.3, price = 333000000, sharp = 9, weight = 7, name = "Redthorn Lizard", fact = "Its red spines match the canyon walls exactly.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Red sandstone cliffs, narrow trails and natural stone arches." },
	{ id = "oasis_scarab", icon = "🪲", zone = 7, rarity = 1, wMin = 0.02, wMax = 0.06, price = 8556250, sharp = 8, weight = 6, name = "Oasis Scarab", fact = "Rolls a ball of sun-warmed clay between the palms.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Rolling dunes, hidden oases and ruins beneath the sand." },
	{ id = "dune_jerboa", icon = "🐭", zone = 7, rarity = 3, wMin = 0.05, wMax = 0.15, price = 34225000, sharp = 9, weight = 7, name = "Dune Jerboa", fact = "Leaps three meters across the sand on tiny legs.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Rolling dunes, hidden oases and ruins beneath the sand." },
	{ id = "mirage_camel", icon = "🐪", zone = 7, rarity = 6, wMin = 450, wMax = 700, price = 616050000, sharp = 10, weight = 8, name = "Mirage Camel", fact = "Seems to shimmer in the heat long before it arrives.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Rolling dunes, hidden oases and ruins beneath the sand." },
	{ id = "jade_tapir", icon = "🐗", zone = 8, rarity = 1, wMin = 150, wMax = 300, price = 15829063, sharp = 9, weight = 7, name = "Jade Tapir", fact = "Its green hide vanishes among broad jungle leaves.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Broad leaves, trailing vines and overgrown jungle temples." },
	{ id = "leafcutter_ant", icon = "🐜", zone = 8, rarity = 3, wMin = 0.001, wMax = 0.004, price = 63316250, sharp = 10, weight = 8, name = "Leafcutter Ant", fact = "Carries a leaf ten times its own size.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Broad leaves, trailing vines and overgrown jungle temples." },
	{ id = "emerald_treefrog", icon = "🐸", zone = 8, rarity = 6, wMin = 0.01, wMax = 0.03, price = 1139692500, sharp = 11, weight = 9, name = "Emerald Treefrog", fact = "Sings after rain from the very top of the canopy.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Broad leaves, trailing vines and overgrown jungle temples." },
	{ id = "mudskipper", icon = "🐟", zone = 9, rarity = 1, wMin = 0.05, wMax = 0.2, price = 29283766, sharp = 10, weight = 8, name = "Mudskipper", fact = "A fish that walks out of the water to hunt on the mud.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Warm channels, tangled mangrove roots and quiet green pools." },
	{ id = "mangrove_fiddler", icon = "🦀", zone = 9, rarity = 3, wMin = 0.02, wMax = 0.08, price = 117135063, sharp = 11, weight = 9, name = "Mangrove Fiddler", fact = "Waves one giant claw to win its mate.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Warm channels, tangled mangrove roots and quiet green pools." },
	{ id = "mangrove_flamingo", icon = "🦩", zone = 9, rarity = 6, wMin = 2, wMax = 4, price = 2108431125, sharp = 12, weight = 10, name = "Mangrove Flamingo", fact = "Stands on one leg for hours in the shallows.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Warm channels, tangled mangrove roots and quiet green pools." },
	{ id = "storm_stone_spider", icon = "🕷️", zone = 10, rarity = 1, wMin = 8, wMax = 20, price = 54174966, sharp = 11, weight = 9, name = "Storm Stone Spider", fact = "Weaves webs between lightning-struck stones.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Rocky ledges, thunderclouds and lightning-struck obelisks." },
	{ id = "highland_yak", icon = "🐂", zone = 10, rarity = 3, wMin = 350, wMax = 800, price = 216699866, sharp = 12, weight = 10, name = "Highland Yak", fact = "Shaggy and unbothered by the fiercest mountain storm.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Rocky ledges, thunderclouds and lightning-struck obelisks." },
	{ id = "tempest_pterosaur", icon = "🦅", zone = 10, rarity = 6, wMin = 25, wMax = 60, price = 3900597581, sharp = 13, weight = 11, name = "Tempest Pterosaur", fact = "Rides the storm front with wings like leather sails.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 5, habitatDescription = "Rocky ledges, thunderclouds and lightning-struck obelisks.", spawnHeights = { 8, 38 } },
	{ id = "spiral_hermit_crab", icon = "🦀", zone = 11, rarity = 1, wMin = 1, wMax = 4, price = 100223688, sharp = 12, weight = 10, name = "Spiral Hermit Crab", fact = "Hauls a spiral shell as big as a house.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "White beaches, tidal caves and bright coral lagoons." },
	{ id = "lagoon_pelican", icon = "🐦", zone = 11, rarity = 3, wMin = 8, wMax = 15, price = 400894751, sharp = 13, weight = 11, name = "Lagoon Pelican", fact = "Scoops up a whole lagoon of fish in one bill.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 45, habitatDescription = "White beaches, tidal caves and bright coral lagoons.", spawnHeights = { 8, 38 } },
	{ id = "azure_horseshoe_crab", icon = "🦀", zone = 11, rarity = 6, wMin = 2, wMax = 5, price = 7216105525, sharp = 14, weight = 12, name = "Azure Horseshoe Crab", fact = "An ancient survivor of the shallow blue tides.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "White beaches, tidal caves and bright coral lagoons." },
	{ id = "pearl_nautilus", icon = "🐚", zone = 12, rarity = 1, wMin = 20, wMax = 60, price = 185413823, sharp = 13, weight = 11, name = "Pearl Nautilus", fact = "Its shell grows one pearly chamber at a time.", habitat = "water", movementMode = "swim", spawnKind = "water", populationWeight = 80, habitatDescription = "An underwater world of coral, sunken gates and glowing kelp.", spawnDepths = { 3, 18 } },
	{ id = "coral_seahorse", icon = "🐴", zone = 12, rarity = 3, wMin = 40, wMax = 120, price = 741655290, sharp = 14, weight = 12, name = "Coral Seahorse", fact = "Coils its tail around coral and drifts with the current.", habitat = "water", movementMode = "swim", spawnKind = "water", populationWeight = 45, habitatDescription = "An underwater world of coral, sunken gates and glowing kelp.", spawnDepths = { 3, 18 } },
	{ id = "reef_lobster", icon = "🦞", zone = 12, rarity = 6, wMin = 5, wMax = 15, price = 13349795222, sharp = 15, weight = 13, name = "Reef Lobster", fact = "Rules the reef cracks with enormous claws.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "An underwater world of coral, sunken gates and glowing kelp." },
	{ id = "cinder_porcupine", icon = "🦔", zone = 13, rarity = 1, wMin = 15, wMax = 30, price = 343015572, sharp = 14, weight = 12, name = "Cinder Porcupine", fact = "Its quills glow like embers at dusk.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Cooled lava flows, dark sand and drifting embers." },
	{ id = "ash_anteater", icon = "🐻", zone = 13, rarity = 3, wMin = 30, wMax = 60, price = 1372062287, sharp = 15, weight = 13, name = "Ash Anteater", fact = "Sniffs out insects hiding under warm ash.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Cooled lava flows, dark sand and drifting embers." },
	{ id = "ember_mandrill", icon = "🐒", zone = 13, rarity = 6, wMin = 40, wMax = 90, price = 24697121160, sharp = 16, weight = 14, name = "Ember Mandrill", fact = "Bright face, brighter temper.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Cooled lava flows, dark sand and drifting embers." },
	{ id = "furnace_stag_beetle", icon = "🪲", zone = 14, rarity = 1, wMin = 0.3, wMax = 0.9, price = 634578808, sharp = 15, weight = 13, name = "Furnace Stag Beetle", fact = "Its horns glow orange in the heat of the vents.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Magma bridges, obsidian arches and glowing volcanic vents." },
	{ id = "caldera_toad", icon = "🐸", zone = 14, rarity = 3, wMin = 3, wMax = 9, price = 2538315230, sharp = 16, weight = 14, name = "Caldera Toad", fact = "Soaks in hot springs that would boil anyone else.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Magma bridges, obsidian arches and glowing volcanic vents." },
	{ id = "obsidian_pangolin", icon = "🦔", zone = 14, rarity = 6, wMin = 25, wMax = 60, price = 45689674147, sharp = 17, weight = 15, name = "Obsidian Pangolin", fact = "Rolls into a ball of black volcanic glass.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Magma bridges, obsidian arches and glowing volcanic vents." },
	{ id = "prism_moth", icon = "🦋", zone = 15, rarity = 1, wMin = 0.01, wMax = 0.03, price = 1173970794, sharp = 16, weight = 14, name = "Prism Moth", fact = "Splits moonlight into rainbows with every wingbeat.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 80, habitatDescription = "Amethyst clusters, crystal bridges and reflective underground pools.", spawnHeights = { 8, 38 } },
	{ id = "geode_mole", icon = "🐹", zone = 15, rarity = 3, wMin = 1, wMax = 3, price = 4695883176, sharp = 17, weight = 15, name = "Geode Mole", fact = "Tunnels through crystal and leaves tiny geodes behind.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Amethyst clusters, crystal bridges and reflective underground pools." },
	{ id = "crystal_anemone", icon = "🪸", zone = 15, rarity = 5, wMin = 5, wMax = 15, price = 16435591117, sharp = 18, weight = 16, name = "Crystal Anemone", fact = "Never moves, yet the cave glitters around it.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Amethyst clusters, crystal bridges and reflective underground pools." },
	{ id = "aurora_weasel", icon = "🦦", zone = 16, rarity = 1, wMin = 0.5, wMax = 1.5, price = 2171845969, sharp = 17, weight = 15, name = "Aurora Weasel", fact = "Its fur ripples with colors like the northern lights.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Snowy plains, luminous ice and a great silver moon." },
	{ id = "moon_owl", icon = "🦉", zone = 16, rarity = 3, wMin = 2, wMax = 5, price = 8687383876, sharp = 18, weight = 16, name = "Moon Owl", fact = "Silent wings glow pale under the silver moon.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 45, habitatDescription = "Snowy plains, luminous ice and a great silver moon.", spawnHeights = { 8, 38 } },
	{ id = "tundra_muskox", icon = "🐃", zone = 16, rarity = 5, wMin = 250, wMax = 500, price = 30405843566, sharp = 19, weight = 17, name = "Tundra Muskox", fact = "Herds form a ring around the calves in a blizzard.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Snowy plains, luminous ice and a great silver moon." },
	{ id = "aether_ribbonfish", icon = "🐠", zone = 17, rarity = 1, wMin = 10, wMax = 40, price = 4017915043, sharp = 18, weight = 16, name = "Aether Ribbonfish", fact = "A ribbon of silver that swims through thin air.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 80, habitatDescription = "Floating cliffs, cloud bridges and ancient wind runes.", spawnHeights = { 8, 38 } },
	{ id = "island_chameleon", icon = "🦎", zone = 17, rarity = 3, wMin = 1, wMax = 4, price = 16071660171, sharp = 19, weight = 17, name = "Island Chameleon", fact = "Changes color to match the sky island it clings to.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Floating cliffs, cloud bridges and ancient wind runes." },
	{ id = "cloud_glider", icon = "🐿️", zone = 17, rarity = 5, wMin = 0.8, wMax = 2, price = 56250810597, sharp = 20, weight = 18, name = "Cloud Glider", fact = "Glides between floating islands on soft cloud-fur.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 8, habitatDescription = "Floating cliffs, cloud bridges and ancient wind runes.", spawnHeights = { 8, 38 } },
	{ id = "void_lamprey", icon = "🐍", zone = 18, rarity = 1, wMin = 3, wMax = 10, price = 7433142829, sharp = 19, weight = 17, name = "Void Lamprey", fact = "Drifts through the dark with a ring of tiny teeth.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 80, habitatDescription = "Shadowy rifts, glowing spores and impossible rock ledges.", spawnHeights = { 3, 12 } },
	{ id = "gloom_sloth", icon = "🦥", zone = 18, rarity = 3, wMin = 8, wMax = 20, price = 29732571315, sharp = 20, weight = 18, name = "Gloom Sloth", fact = "Moves so slowly that moss grows on its coat.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Shadowy rifts, glowing spores and impossible rock ledges." },
	{ id = "rift_axolotl", icon = "🦎", zone = 18, rarity = 5, wMin = 0.3, wMax = 0.9, price = 104063999604, sharp = 21, weight = 19, name = "Rift Axolotl", fact = "Smiles calmly at the edge of a shadow rift.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 8, habitatDescription = "Shadowy rifts, glowing spores and impossible rock ledges.", spawnHeights = { 3, 12 } },
	{ id = "nebula_tardigrade", icon = "🐻", zone = 19, rarity = 1, wMin = 0.1, wMax = 0.4, price = 13751314233, sharp = 20, weight = 18, name = "Nebula Tardigrade", fact = "Survives anywhere, even among the stars.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Cosmic islands, stardust and the rings of an ancient portal." },
	{ id = "astral_starfish", icon = "⭐", zone = 19, rarity = 3, wMin = 2, wMax = 6, price = 55005256934, sharp = 21, weight = 19, name = "Astral Starfish", fact = "Each arm points to a different distant star.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Cosmic islands, stardust and the rings of an ancient portal." },
	{ id = "orbital_jellyfish", icon = "🪼", zone = 19, rarity = 5, wMin = 5, wMax = 20, price = 192518399267, sharp = 22, weight = 20, name = "Orbital Jellyfish", fact = "Floats in slow orbits around a glowing core.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 8, habitatDescription = "Cosmic islands, stardust and the rings of an ancient portal.", spawnHeights = { 8, 38 } },
	{ id = "spring_strider", icon = "🦗", zone = 20, rarity = 1, wMin = 10, wMax = 30, price = 25439931332, sharp = 21, weight = 19, name = "Spring Strider", fact = "Bounces over the gardens on coiled legs.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Overgrown gear gardens, copper pipes and slow clockwork blooms." },
	{ id = "copper_weevil", icon = "🪲", zone = 20, rarity = 2, wMin = 0.5, wMax = 1.5, price = 50879862664, sharp = 21, weight = 19, name = "Copper Weevil", fact = "Chews rust off the old pipes and turns green.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 63, habitatDescription = "Overgrown gear gardens, copper pipes and slow clockwork blooms." },
	{ id = "gear_sentinel", icon = "🤖", zone = 20, rarity = 3, wMin = 500, wMax = 900, price = 101759725327, sharp = 22, weight = 20, name = "Gear Sentinel", fact = "Stands guard while its gears tick slowly.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Overgrown gear gardens, copper pipes and slow clockwork blooms." },
	{ id = "magnet_tripod", icon = "🔩", zone = 20, rarity = 4, wMin = 60, wMax = 150, price = 203519450654, sharp = 22, weight = 20, name = "Magnet Tripod", fact = "Three legs, one strong magnet, no patience.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Overgrown gear gardens, copper pipes and slow clockwork blooms." },
	{ id = "iron_hound", icon = "🐕", zone = 20, rarity = 5, wMin = 120, wMax = 260, price = 508798626635, sharp = 23, weight = 21, name = "Iron Hound", fact = "Bolted together from old plates, still loyal.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Overgrown gear gardens, copper pipes and slow clockwork blooms." },
	{ id = "clockwork_basilisk", icon = "🐍", zone = 20, rarity = 6, wMin = 300, wMax = 800, price = 1526395879906, sharp = 23, weight = 21, name = "Clockwork Basilisk", fact = "Its stare winds every spring in the garden.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Overgrown gear gardens, copper pipes and slow clockwork blooms." },
	{ id = "shelf_millipede", icon = "🐛", zone = 21, rarity = 1, wMin = 3, wMax = 8, price = 47063872964, sharp = 22, weight = 20, name = "Shelf Millipede", fact = "A hundred tiny legs and a shelf-fungus back.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Giant caps, glowing spores and damp peat." },
	{ id = "peat_leech", icon = "🪱", zone = 21, rarity = 2, wMin = 1, wMax = 3, price = 94127745928, sharp = 22, weight = 20, name = "Peat Leech", fact = "Waits quietly under the dark peat.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 63, habitatDescription = "Giant caps, glowing spores and damp peat." },
	{ id = "lantern_slug", icon = "🐌", zone = 21, rarity = 3, wMin = 2, wMax = 6, price = 188255491855, sharp = 23, weight = 21, name = "Lantern Slug", fact = "Carries a soft glowing lantern on its back.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Giant caps, glowing spores and damp peat." },
	{ id = "mycelium_bloomstalker", icon = "🌸", zone = 21, rarity = 4, wMin = 80, wMax = 200, price = 376510983710, sharp = 23, weight = 21, name = "Mycelium Bloomstalker", fact = "Walks on threads of living mycelium.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Giant caps, glowing spores and damp peat." },
	{ id = "spore_marauder", icon = "🍄", zone = 21, rarity = 5, wMin = 150, wMax = 400, price = 941277459276, sharp = 24, weight = 22, name = "Spore Marauder", fact = "Leaves a trail of drifting spores behind it.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Giant caps, glowing spores and damp peat." },
	{ id = "cap_mantis", icon = "🦗", zone = 21, rarity = 6, wMin = 20, wMax = 60, price = 2823832377827, sharp = 24, weight = 22, name = "Cap Mantis", fact = "Hides under a mushroom cap, waiting for lunch.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "Giant caps, glowing spores and damp peat." },
	{ id = "fossil_trilobite", icon = "🪲", zone = 22, rarity = 1, wMin = 0.1, wMax = 0.4, price = 87068164983, sharp = 23, weight = 21, name = "Fossil Trilobite", fact = "Older than the sand it hides in.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "Fossil ribs, bleached dunes and buried skeleton arches." },
	{ id = "dune_ankylosaur", icon = "🦖", zone = 22, rarity = 2, wMin = 900, wMax = 2200, price = 174136329966, sharp = 23, weight = 21, name = "Dune Ankylosaur", fact = "Armored like a boulder and just as hard to move.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 63, habitatDescription = "Fossil ribs, bleached dunes and buried skeleton arches." },
	{ id = "fossil_ceratopsian", icon = "🦖", zone = 22, rarity = 3, wMin = 700, wMax = 1800, price = 348272659932, sharp = 24, weight = 22, name = "Fossil Ceratopsian", fact = "A horned giant that never quite finished fossilizing.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "Fossil ribs, bleached dunes and buried skeleton arches." },
	{ id = "skeletal_colossus", icon = "💀", zone = 22, rarity = 4, wMin = 2000, wMax = 5000, price = 696545319864, sharp = 24, weight = 22, name = "Skeletal Colossus", fact = "Its ribs are a whole canyon of white arches.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 29, habitatDescription = "Fossil ribs, bleached dunes and buried skeleton arches." },
	{ id = "sand_reaper", icon = "🦂", zone = 22, rarity = 5, wMin = 200, wMax = 450, price = 1741363299660, sharp = 25, weight = 23, name = "Sand Reaper", fact = "Cuts through the dunes with a scythe-shaped tail.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "Fossil ribs, bleached dunes and buried skeleton arches." },
	{ id = "bone_vulture", icon = "🦅", zone = 22, rarity = 6, wMin = 40, wMax = 90, price = 5224089898980, sharp = 25, weight = 23, name = "Bone Vulture", fact = "Circles over the dunes in a cloak of old bones.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 5, habitatDescription = "Fossil ribs, bleached dunes and buried skeleton arches.", spawnHeights = { 8, 38 } },
	{ id = "abyss_sea_urchin", icon = "🦔", zone = 23, rarity = 1, wMin = 20, wMax = 50, price = 161076105219, sharp = 24, weight = 22, name = "Abyss Sea Urchin", fact = "Spines taller than a knight in armor.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "A drowned fortress of pearl walls, glowing vents and slow currents." },
	{ id = "citadel_cuttlefish", icon = "🦑", zone = 23, rarity = 2, wMin = 10, wMax = 30, price = 322152210437, sharp = 24, weight = 22, name = "Citadel Cuttlefish", fact = "Flashes warning colors across the citadel walls.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 63, habitatDescription = "A drowned fortress of pearl walls, glowing vents and slow currents.", spawnHeights = { 3, 12 } },
	{ id = "cathedral_clam", icon = "🐚", zone = 23, rarity = 3, wMin = 400, wMax = 900, price = 644304420874, sharp = 25, weight = 23, name = "Cathedral Clam", fact = "Its shell rings like a bell in the current.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "A drowned fortress of pearl walls, glowing vents and slow currents." },
	{ id = "trench_angler", icon = "🐟", zone = 23, rarity = 4, wMin = 150, wMax = 400, price = 1288608841748, sharp = 25, weight = 23, name = "Trench Angler", fact = "Lures prey with a lantern in the deepest trench.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 29, habitatDescription = "A drowned fortress of pearl walls, glowing vents and slow currents.", spawnHeights = { 3, 12 } },
	{ id = "pressure_colossus", icon = "🗿", zone = 23, rarity = 5, wMin = 3000, wMax = 7000, price = 3221522104371, sharp = 26, weight = 24, name = "Pressure Colossus", fact = "Built to stand where the sea presses hardest.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "A drowned fortress of pearl walls, glowing vents and slow currents." },
	{ id = "abyss_octopus", icon = "🐙", zone = 23, rarity = 6, wMin = 200, wMax = 600, price = 9664566313112, sharp = 26, weight = 24, name = "Abyss Octopus", fact = "Eight arms, each one holding a different secret.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 5, habitatDescription = "A drowned fortress of pearl walls, glowing vents and slow currents.", spawnHeights = { 3, 12 } },
	{ id = "fulgurite_cricket", icon = "🦗", zone = 24, rarity = 1, wMin = 0.5, wMax = 1.5, price = 297990794654, sharp = 25, weight = 23, name = "Fulgurite Cricket", fact = "Chirps in sparks inside fused lightning glass.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "A torn sky of lightning, floating shards and humming fulgurite." },
	{ id = "rift_kangaroo", icon = "🦘", zone = 24, rarity = 2, wMin = 60, wMax = 140, price = 595981589309, sharp = 25, weight = 23, name = "Rift Kangaroo", fact = "Bounds between rift ledges in single leaps.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 63, habitatDescription = "A torn sky of lightning, floating shards and humming fulgurite." },
	{ id = "thunder_centaur", icon = "🐴", zone = 24, rarity = 3, wMin = 400, wMax = 800, price = 1191963178617, sharp = 26, weight = 24, name = "Thunder Centaur", fact = "Gallops with a crack of thunder at every stride.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "A torn sky of lightning, floating shards and humming fulgurite." },
	{ id = "prism_revenant", icon = "👻", zone = 24, rarity = 4, wMin = 5, wMax = 15, price = 2383926357234, sharp = 26, weight = 24, name = "Prism Revenant", fact = "A restless shimmer that bends light around itself.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 29, habitatDescription = "A torn sky of lightning, floating shards and humming fulgurite.", spawnHeights = { 8, 38 } },
	{ id = "storm_harrier", icon = "🦅", zone = 24, rarity = 5, wMin = 15, wMax = 35, price = 5959815893086, sharp = 27, weight = 25, name = "Storm Harrier", fact = "Hunts along the lightning ridges at dusk.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 8, habitatDescription = "A torn sky of lightning, floating shards and humming fulgurite.", spawnHeights = { 8, 38 } },
	{ id = "rift_serpent", icon = "🐉", zone = 24, rarity = 6, wMin = 400, wMax = 1000, price = 17879447679258, sharp = 27, weight = 25, name = "Rift Serpent", fact = "Slides between storm clouds and the torn ground.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "A torn sky of lightning, floating shards and humming fulgurite." },
	{ id = "caldera_tarsier", icon = "🐒", zone = 25, rarity = 1, wMin = 1, wMax = 3, price = 551282970110, sharp = 26, weight = 24, name = "Caldera Tarsier", fact = "Huge eyes that glow in the red light of the crater.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 80, habitatDescription = "The first volcano: molten lakes, ancient ash and giant fossils." },
	{ id = "ember_salamander", icon = "🦎", zone = 25, rarity = 2, wMin = 6, wMax = 15, price = 1102565940221, sharp = 26, weight = 24, name = "Ember Salamander", fact = "Basks in lava pools like a cat on a windowsill.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 63, habitatDescription = "The first volcano: molten lakes, ancient ash and giant fossils." },
	{ id = "magma_hippo", icon = "🦛", zone = 25, rarity = 3, wMin = 1200, wMax = 2500, price = 2205131880442, sharp = 27, weight = 25, name = "Magma Hippo", fact = "Wallows in lava that is nearly cool enough to be mud.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 45, habitatDescription = "The first volcano: molten lakes, ancient ash and giant fossils." },
	{ id = "lava_dragonfly", icon = "🪰", zone = 25, rarity = 4, wMin = 0.5, wMax = 2, price = 4410263760884, sharp = 27, weight = 25, name = "Lava Dragonfly", fact = "Wings like sheets of glowing glass.", habitat = "air", movementMode = "fly", spawnKind = "air", populationWeight = 29, habitatDescription = "The first volcano: molten lakes, ancient ash and giant fossils.", spawnHeights = { 8, 38 } },
	{ id = "volcanic_wyrm", icon = "🐲", zone = 25, rarity = 5, wMin = 1500, wMax = 4000, price = 11025659402209, sharp = 28, weight = 26, name = "Volcanic Wyrm", fact = "Wakes only when the caldera needs to breathe.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 8, habitatDescription = "The first volcano: molten lakes, ancient ash and giant fossils." },
	{ id = "primordial_titan", icon = "🗿", zone = 25, rarity = 6, wMin = 20000, wMax = 60000, price = 33076978206627, sharp = 28, weight = 26, name = "Primordial Titan", fact = "The first creature, still walking after the first fire.", habitat = "ground", movementMode = "ground", spawnKind = "ground", populationWeight = 5, habitatDescription = "The first volcano: molten lakes, ancient ash and giant fossils." },
}

---------------------------------------------------------------------
-- Копья (магазин в Оружейной). sharp/heavy — кого пробивает, luck/range — множители,
-- alpha — «хрупкость» натяжения: P(дойти до ×m) = m^(-alpha). Меньше alpha — дальше тянешь.
---------------------------------------------------------------------
Config.SPEARS = {
	{ id = "stick", price = 0, sharp = 1, heavy = 1, luck = 1, range = 1, alpha = 0.85, impact = "dust", zone = 1, tier = 1, name = "Stone-tipped Spear", desc = "Every hunter starts somewhere.", trail = { Color3.fromHex("#e6dcc8"), Color3.fromHex("#a08c6e") } },
	{ id = "bone", price = 201, sharp = 2, heavy = 1, luck = 1.2, range = 1.05, alpha = 0.8, impact = "dust", zone = 1, tier = 2, name = "Bone Spear", desc = "Pierces tougher hides.", trail = { Color3.fromHex("#fffaeb"), Color3.fromHex("#c8bea0") } },
	{ id = "bronze", price = 294, sharp = 2, heavy = 2, luck = 1.4, range = 1.1, alpha = 0.76, impact = "sparks", zone = 2, tier = 3, name = "Bronze Spear", desc = "Heavy and dependable.", trail = { Color3.fromHex("#ffbe6e"), Color3.fromHex("#cd7f32") } },
	{ id = "feather", price = 1200, sharp = 3, heavy = 2, luck = 1.7, range = 1.25, alpha = 0.72, impact = "feathers", zone = 2, tier = 4, name = "Feathered Spear", desc = "Flies farther than other early spears.", trail = { Color3.fromHex("#ff7878"), Color3.fromHex("#50a0ff") } },
	{ id = "iron", price = 1480, sharp = 3, heavy = 3, luck = 2, range = 1.3, alpha = 0.68, impact = "sparks", zone = 2, tier = 5, name = "Iron Spear", desc = "Built for bigger game.", trail = { Color3.fromHex("#dce2f0"), Color3.fromHex("#787c88") } },
	{ id = "obsidian", price = 5030, sharp = 4, heavy = 3, luck = 2.6, range = 1.38, alpha = 0.63, impact = "shards", zone = 3, tier = 6, name = "Obsidian Spear", desc = "Forged from black volcanic glass.", trail = { Color3.fromHex("#c86eff"), Color3.fromHex("#3c145a") } },
	{ id = "crystal", price = 11400, sharp = 5, heavy = 4, luck = 3.4, range = 1.45, alpha = 0.58, impact = "crystal", zone = 3, tier = 7, name = "Crystal Spear", desc = "Chimes as it flies.", trail = { Color3.fromHex("#8cffff"), Color3.fromHex("#ffc846") } },
	{ id = "fire", price = 61600, sharp = 5, heavy = 4, luck = 4.5, range = 1.55, alpha = 0.54, impact = "fire", zone = 4, tier = 8, name = "Fire Spear", desc = "Leaves a blazing trail.", trail = { Color3.fromHex("#ffdc50"), Color3.fromHex("#ff4614") } },
	{ id = "ice", price = 75100, sharp = 6, heavy = 5, luck = 6, range = 1.65, alpha = 0.5, impact = "ice", zone = 4, tier = 9, name = "Ice Spear", desc = "Freezes the air around it.", trail = { Color3.fromHex("#ebfaff"), Color3.fromHex("#78c8ff") } },
	{ id = "star", price = 280000, sharp = 6, heavy = 5, luck = 9, range = 1.8, alpha = 0.45, impact = "stars", zone = 4, tier = 10, name = "Star Spear", desc = "Fell from the sky. Almost aims itself.", trail = { Color3.fromHex("#ffe678"), Color3.fromHex("#785aff") } },
	{ id = "amber_sting", price = 345000, sharp = 7, heavy = 6, luck = 10.0, range = 1.9, alpha = 0.44, impact = "sparks", zone = 5, tier = 11, name = "Amber Sting", desc = "A honey-colored edge set in layered amber.", trail = { Color3.fromHex("#fff17b"), Color3.fromHex("#f5a817") } },
	{ id = "solar_trident", price = 593000, sharp = 8, heavy = 6, luck = 11.2, range = 1.945, alpha = 0.434, impact = "fire", zone = 5, tier = 12, name = "Solar Trident", desc = "Three golden prongs catch the light of the savanna.", trail = { Color3.fromHex("#ff692d"), Color3.fromHex("#ffd029") } },
	{ id = "canyon_hook", price = 1370000, sharp = 8, heavy = 7, luck = 12.54, range = 1.99, alpha = 0.428, impact = "shards", zone = 6, tier = 13, name = "Canyon Hook", desc = "A hooked stone blade shaped for the red canyons.", trail = { Color3.fromHex("#73c6e8"), Color3.fromHex("#d77435") } },
	{ id = "condor_quill", price = 1570000, sharp = 9, heavy = 7, luck = 14.05, range = 2.035, alpha = 0.422, impact = "feathers", zone = 6, tier = 14, name = "Condor Quill", desc = "A broad feathered edge built to cut through rising air.", trail = { Color3.fromHex("#d78e36"), Color3.fromHex("#e4dfca") } },
	{ id = "mirage_lance", price = 3410000, sharp = 9, heavy = 8, luck = 15.74, range = 2.08, alpha = 0.416, impact = "crystal", zone = 7, tier = 15, name = "Mirage Lance", desc = "A pale desert lance with a shimmering point.", trail = { Color3.fromHex("#6ee1e9"), Color3.fromHex("#f1cf6c") } },
	{ id = "scorpion_sting", price = 3790000, sharp = 10, heavy = 8, luck = 17.62, range = 2.125, alpha = 0.41, impact = "shards", zone = 7, tier = 16, name = "Scorpion Sting", desc = "A hooked tip and layered grip inspired by desert armor.", trail = { Color3.fromHex("#9aff7e"), Color3.fromHex("#be8240") } },
	{ id = "emerald_vine", price = 7860000, sharp = 10, heavy = 9, luck = 19.74, range = 2.17, alpha = 0.404, impact = "crystal", zone = 8, tier = 17, name = "Emerald Vine", desc = "A green blade held by tightly wrapped jungle vines.", trail = { Color3.fromHex("#c2f757"), Color3.fromHex("#19bd67") } },
	{ id = "temple_guard", price = 8640000, sharp = 11, heavy = 9, luck = 22.11, range = 2.215, alpha = 0.398, impact = "sparks", zone = 8, tier = 18, name = "Temple Guard", desc = "A carved guardian spear from the overgrown temple.", trail = { Color3.fromHex("#ffd24d"), Color3.fromHex("#1b8e78") } },
	{ id = "mangrove_root", price = 17700000, sharp = 11, heavy = 10, luck = 24.76, range = 2.26, alpha = 0.392, impact = "dust", zone = 9, tier = 19, name = "Mangrove Root", desc = "A twisted root shaft fitted with a broad hunting edge.", trail = { Color3.fromHex("#a7e96a"), Color3.fromHex("#5b8c3e") } },
	{ id = "hydra_fangs", price = 19300000, sharp = 12, heavy = 10, luck = 27.73, range = 2.305, alpha = 0.386, impact = "shards", zone = 9, tier = 20, name = "Hydra Fangs", desc = "Twin fang-shaped blades rise from a reinforced socket.", trail = { Color3.fromHex("#9eff78"), Color3.fromHex("#358957") } },
	{ id = "storm_trident", price = 39100000, sharp = 12, heavy = 11, luck = 31.06, range = 2.35, alpha = 0.38, impact = "sparks", zone = 10, tier = 21, name = "Storm Trident", desc = "A forked point that gathers the colors of a storm.", trail = { Color3.fromHex("#fff16c"), Color3.fromHex("#83a9e6") } },
	{ id = "thunder_split", price = 42400000, sharp = 13, heavy = 11, luck = 34.79, range = 2.395, alpha = 0.374, impact = "sparks", zone = 10, tier = 22, name = "Thunder Splitter", desc = "An open lightning-shaped blade built for the high ridges.", trail = { Color3.fromHex("#f7ee56"), Color3.fromHex("#5e88cb") } },
	{ id = "coral_branch", price = 85300000, sharp = 13, heavy = 12, luck = 38.96, range = 2.44, alpha = 0.368, impact = "crystal", zone = 11, tier = 23, name = "Coral Branch", desc = "A branching coral point with a sturdy wrapped grip.", trail = { Color3.fromHex("#8cf5ee"), Color3.fromHex("#f17c8a") } },
	{ id = "tide_crest", price = 91800000, sharp = 14, heavy = 12, luck = 43.63, range = 2.485, alpha = 0.362, impact = "ice", zone = 11, tier = 24, name = "Tide Crest", desc = "A sweeping edge shaped like a breaking wave.", trail = { Color3.fromHex("#b6ffff"), Color3.fromHex("#25c2dd") } },
	{ id = "abyss_anchor", price = 184000000, sharp = 14, heavy = 13, luck = 48.87, range = 2.53, alpha = 0.356, impact = "shards", zone = 12, tier = 25, name = "Abyssal Anchor", desc = "A heavy anchor blade recovered from the deep.", trail = { Color3.fromHex("#64f2e8"), Color3.fromHex("#315c87") } },
	{ id = "leviathan_fang", price = 196000000, sharp = 15, heavy = 13, luck = 54.74, range = 2.575, alpha = 0.35, impact = "ice", zone = 12, tier = 26, name = "Leviathan Fang", desc = "A great sea fang secured inside a reinforced frame.", trail = { Color3.fromHex("#78dce9"), Color3.fromHex("#283c66") } },
	{ id = "ash_saw", price = 391000000, sharp = 15, heavy = 14, luck = 61.3, range = 2.62, alpha = 0.344, impact = "shards", zone = 13, tier = 27, name = "Ash Saw", desc = "A dark serrated blade forged for the volcanic plateau.", trail = { Color3.fromHex("#f0a460"), Color3.fromHex("#5d5a67") } },
	{ id = "golem_heart", price = 416000000, sharp = 16, heavy = 14, luck = 68.66, range = 2.665, alpha = 0.338, impact = "sparks", zone = 13, tier = 28, name = "Golem Heart", desc = "A warm stone core powers its layered metal point.", trail = { Color3.fromHex("#ffbb3c"), Color3.fromHex("#566270") } },
	{ id = "magma_tongue", price = 823000000, sharp = 16, heavy = 15, luck = 76.9, range = 2.71, alpha = 0.332, impact = "fire", zone = 14, tier = 29, name = "Magma Tongue", desc = "A bright molten edge held within a black stone frame.", trail = { Color3.fromHex("#ffd439"), Color3.fromHex("#f25b22") } },
	{ id = "phoenix_wing", price = 873000000, sharp = 17, heavy = 15, luck = 86.13, range = 2.755, alpha = 0.326, impact = "fire", zone = 14, tier = 30, name = "Phoenix Wing", desc = "A fiery wing-shaped blade with a feathered grip.", trail = { Color3.fromHex("#ffdf66"), Color3.fromHex("#f57b20") } },
	{ id = "amethyst_geode", price = 1720000000, sharp = 17, heavy = 16, luck = 96.46, range = 2.8, alpha = 0.32, impact = "crystal", zone = 15, tier = 31, name = "Amethyst Geode", desc = "A hollow crystal crown opens around an amethyst core.", trail = { Color3.fromHex("#e9a2ff"), Color3.fromHex("#9637d8") } },
	{ id = "quartz_needle", price = 1820000000, sharp = 18, heavy = 16, luck = 108.04, range = 2.845, alpha = 0.314, impact = "crystal", zone = 15, tier = 32, name = "Quartz Needle", desc = "A long clear point mounted in a delicate crystal socket.", trail = { Color3.fromHex("#d7ffff"), Color3.fromHex("#9e74d6") } },
	{ id = "lunar_crescent", price = 3570000000, sharp = 18, heavy = 17, luck = 121.0, range = 2.89, alpha = 0.308, impact = "ice", zone = 16, tier = 33, name = "Lunar Crescent", desc = "A silver moon-shaped edge for the frozen plains.", trail = { Color3.fromHex("#ebfaff"), Color3.fromHex("#b5c7ef") } },
	{ id = "aurora_weave", price = 3760000000, sharp = 19, heavy = 17, luck = 135.52, range = 2.935, alpha = 0.302, impact = "ice", zone = 16, tier = 34, name = "Aurora Weave", desc = "Colored bands wrap around its luminous northern blade.", trail = { Color3.fromHex("#bc90ff"), Color3.fromHex("#72e4c2") } },
	{ id = "cloud_feather", price = 7360000000, sharp = 19, heavy = 18, luck = 151.79, range = 2.98, alpha = 0.296, impact = "feathers", zone = 17, tier = 35, name = "Cloud Feather", desc = "A light feathered point built for the floating islands.", trail = { Color3.fromHex("#effbff"), Color3.fromHex("#91d6ec") } },
	{ id = "sky_harpoon", price = 7740000000, sharp = 20, heavy = 18, luck = 170.0, range = 3.025, alpha = 0.29, impact = "feathers", zone = 17, tier = 36, name = "Sky Harpoon", desc = "A long hooked harpoon made to reach across the clouds.", trail = { Color3.fromHex("#f7e696"), Color3.fromHex("#65b6d7") } },
	{ id = "rift_shards", price = 15100000000, sharp = 20, heavy = 19, luck = 190.4, range = 3.07, alpha = 0.284, impact = "shards", zone = 18, tier = 37, name = "Rift Shards", desc = "A floating cluster of dark fragments surrounds its point.", trail = { Color3.fromHex("#dc9bff"), Color3.fromHex("#7139b8") } },
	{ id = "void_scissors", price = 15800000000, sharp = 21, heavy = 19, luck = 213.25, range = 3.115, alpha = 0.278, impact = "crystal", zone = 18, tier = 38, name = "Void Shears", desc = "Two open blades frame the darkness between them.", trail = { Color3.fromHex("#b278ff"), Color3.fromHex("#3b285d") } },
	{ id = "astral_armillary", price = 30800000000, sharp = 21, heavy = 20, luck = 238.84, range = 3.16, alpha = 0.272, impact = "stars", zone = 19, tier = 39, name = "Astral Armillary", desc = "Orbital rings hold a golden point at their center.", trail = { Color3.fromHex("#ffe48b"), Color3.fromHex("#6863df") } },
	{ id = "singularity_spire", price = 32200000000, sharp = 22, heavy = 20, luck = 267.5, range = 3.205, alpha = 0.266, impact = "stars", zone = 19, tier = 40, name = "Singularity Spire", desc = "A stepped black spire held within an open event-horizon frame.", trail = { Color3.fromHex("#f5db77"), Color3.fromHex("#7864e5") } },
	{ id = "gear_pike", price = 62500000000, sharp = 23, heavy = 21, luck = 299.6, range = 3.25, alpha = 0.26, impact = "sparks", zone = 20, tier = 41, name = "Gearwork Pike", desc = "A copper-banded pike that ticks like a clock.", trail = { Color3.fromHex("#ffd07a"), Color3.fromHex("#c9803a") } },
	{ id = "spore_halberd", price = 121000000000, sharp = 24, heavy = 22, luck = 335.6, range = 3.295, alpha = 0.254, impact = "dust", zone = 21, tier = 42, name = "Sporebloom Halberd", desc = "A glowing cap blooms behind its pale blade.", trail = { Color3.fromHex("#9dffd6"), Color3.fromHex("#3f8f78") } },
	{ id = "bone_glaive", price = 235000000000, sharp = 25, heavy = 23, luck = 375.8, range = 3.34, alpha = 0.248, impact = "shards", zone = 22, tier = 43, name = "Boneforged Glaive", desc = "Carved from a fossil rib, edged like a crescent.", trail = { Color3.fromHex("#f4ead0"), Color3.fromHex("#a89a74") } },
	{ id = "pearl_lance", price = 454000000000, sharp = 26, heavy = 24, luck = 420.9, range = 3.385, alpha = 0.242, impact = "ice", zone = 23, tier = 44, name = "Citadel Pearl Lance", desc = "A drowned-fortress spear with a pearl in its socket.", trail = { Color3.fromHex("#bff3ff"), Color3.fromHex("#3aa0c8") } },
	{ id = "rift_conductor", price = 877000000000, sharp = 27, heavy = 25, luck = 471.4, range = 3.43, alpha = 0.236, impact = "sparks", zone = 24, tier = 45, name = "Rift Conductor", desc = "Draws the lightning of the torn sky into its tip.", trail = { Color3.fromHex("#d6ccff"), Color3.fromHex("#8a7cff") } },
	{ id = "primal_fang", price = 1690000000000, sharp = 28, heavy = 26, luck = 528.0, range = 3.475, alpha = 0.23, impact = "fire", zone = 25, tier = 46, name = "Primordial Fang", desc = "A caldera-forged fang, still glowing from the first fire.", trail = { Color3.fromHex("#ffd08a"), Color3.fromHex("#ff7a3d") } },
}
-- Кузница: улучшение купленного копья (уровни 0..5)
Config.FORGE = {
	maxLevel = 7, -- абсолютный потолок; бесплатно доступно freeMax, остальное даёт пасс Master Smith
	freeMax = 5,
	luckPer = 0.12, -- +12% удачи за уровень
	rangePer = 0.04, -- +4% дальности за уровень
	alphaPer = 0.012, -- копьё «держит» натяжение дольше
	costMul = 0.3, -- цена уровня = max(40, price·costMul)·(lvl+1)^1.7
}

-- V86: Сила растёт уровнями. Шкала тренировки — это шкала уровня Силы, она не зависит от гантелей:
-- каждый уровень даёт одинаково +STRENGTH.perLevel Силы, опыта до следующего уровня нужно strengthXp(L).
-- Гантели дают gain опыта за подъём: лучше гантели — быстрее растут уровни. Цены гантелей идут вдоль лестницы копий,
-- поэтому сила и копья растут вместе (таблица: docs/balance_v86.md, генератор tools/balance_v86.py).
Config.STRENGTH = {
	start = 10, -- Сила на 1-м уровне
	perLevel = 5, -- +Сила за каждый уровень
	xpBase = 18, -- опыта с 1-го на 2-й уровень (больше — дольше качать Силу; все гантели масштабируются вместе)
	xpGrowth = 1.042, -- каждый следующий уровень требует на 4.2% больше опыта
	levelsPerZone = 10, -- ~10 уровней Силы на зону леса
	maxLevel = 251, -- потолок: на 251-м уровне (Сила 1260) дальность уже максимальная, дальше уровни ничего не дают
}
Config.DUMBBELL = {
	{ cost = 0, gain = 1, name = "Wooden" },
	{ cost = 420, gain = 2, name = "Stone" },
	{ cost = 4000, gain = 3, name = "Bronze" },
	{ cost = 120000, gain = 5, name = "Iron" },
	{ cost = 550000, gain = 8, name = "Granite" },
	{ cost = 2800000, gain = 18, name = "Golden" },
	{ cost = 6800000, gain = 26, name = "Mammoth" },
	{ cost = 32000000, gain = 60, name = "Crystal" },
	{ cost = 140000000, gain = 140, name = "Obsidian" },
	{ cost = 310000000, gain = 210, name = "Frost" },
	{ cost = 1200000000, gain = 470, name = "Magma" },
	{ cost = 2700000000, gain = 710, name = "Storm" },
	{ cost = 11000000000, gain = 1600, name = "Jade" },
	{ cost = 82000000000, gain = 5600, name = "Celestial" },
	{ cost = 590000000000, gain = 19000, name = "Primal" },
}
-- Сила на уровне L
function Config.strengthOf(level: number): number
	local S = Config.STRENGTH
	return S.start + S.perLevel * (math.clamp(math.floor(level), 1, S.maxLevel) - 1)
end
-- Опыт, нужный чтобы с уровня L перейти на L+1
function Config.strengthXp(level: number): number
	local S = Config.STRENGTH
	return math.max(1, math.floor(S.xpBase * S.xpGrowth ^ (math.clamp(math.floor(level), 1, S.maxLevel) - 1) + 0.5))
end
-- V82: 15 гантелей и 15 стадий стойки. Данные дизайнера (Opus): docs/concepts_v82/dumbbells_v82.lua, превью там же
-- (dumbbells_sheet.png, stands_sheet.png). Формат и правила: docs/concepts_v82/training_contract.md.
do
	local D = {
		NAMES = { "Wooden", "Stone", "Bronze", "Iron", "Granite", "Golden", "Mammoth", "Crystal", "Obsidian", "Frost", "Magma", "Storm", "Jade", "Celestial", "Primal" },
		DUMBBELL_LOOK = {
			-- 1 Wooden: oak blocks held by two brass straps
			{ color = Color3.fromRGB(150, 98, 56), material = Enum.Material.Wood, size = 0.9, parts = {
				{ name = "Bar", shape = "Cylinder", size = {1.68, 0.26, 0.26}, offset = {0, 0, 0}, material = "Wood", rgb = {99, 61, 37}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {0.52, 0.68, 0.68}, offset = {1.04, 0, 0}, material = "Wood", rgb = {158, 98, 52}, weight = true, mirror = true },
				{ name = "Strap", shape = "Block", size = {0.1, 0.72, 0.72}, offset = {1.17, 0, 0}, material = "Metal", rgb = {219, 165, 83}, weight = false, mirror = true },
				{ name = "Strap2", shape = "Block", size = {0.1, 0.72, 0.72}, offset = {0.91, 0, 0}, material = "Metal", rgb = {219, 165, 83}, weight = false, mirror = true },
			} },
			-- 2 Stone: slate blocks lashed with rope, a cobble chip on top
			{ color = Color3.fromRGB(128, 128, 132), material = Enum.Material.Slate, size = 1, parts = {
				{ name = "Bar", shape = "Cylinder", size = {1.8, 0.26, 0.26}, offset = {0, 0, 0}, material = "Wood", rgb = {109, 71, 47}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {0.6, 0.78, 0.78}, offset = {1.1, 0, 0}, material = "Slate", rgb = {128, 137, 145}, weight = true, mirror = true },
				{ name = "Lash", shape = "Block", size = {0.1, 0.82, 0.82}, offset = {0.95, 0, 0}, material = "Fabric", rgb = {196, 160, 104}, weight = false, mirror = true },
				{ name = "Chip", shape = "Block", size = {0.34, 0.1, 0.5}, offset = {1.16, 0.44, 0.05}, material = "Cobblestone", rgb = {150, 156, 160}, weight = false, mirror = true },
			} },
			-- 3 Bronze: round bronze plates with a pale bronze cap and collar
			{ color = Color3.fromRGB(205, 127, 50), material = Enum.Material.Metal, size = 1.1, parts = {
				{ name = "Bar", shape = "Cylinder", size = {1.9, 0.24, 0.24}, offset = {0, 0, 0}, material = "Metal", rgb = {100, 65, 48}, weight = false, mirror = false },
				{ name = "Head", shape = "Cylinder", size = {0.56, 0.88, 0.88}, offset = {1.15, 0, 0}, material = "Metal", rgb = {184, 104, 55}, weight = true, mirror = true },
				{ name = "Plate", shape = "Cylinder", size = {0.12, 0.96, 0.96}, offset = {0.83, 0, 0}, material = "Metal", rgb = {236, 158, 82}, weight = false, mirror = true },
				{ name = "Cap", shape = "Cylinder", size = {0.08, 0.56, 0.56}, offset = {1.46, 0, 0}, material = "Metal", rgb = {236, 158, 82}, weight = false, mirror = true },
				{ name = "Collar", shape = "Cylinder", size = {0.1, 0.36, 0.36}, offset = {0.66, 0, 0}, material = "Metal", rgb = {140, 90, 60}, weight = false, mirror = true },
			} },
			-- 4 Iron: dark iron plates with the blue stripe and steel collars
			{ color = Color3.fromRGB(81, 157, 204), material = Enum.Material.Metal, size = 1.2, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2, 0.26, 0.26}, offset = {0, 0, 0}, material = "Metal", rgb = {125, 139, 147}, weight = false, mirror = false },
				{ name = "Head", shape = "Cylinder", size = {0.66, 0.96, 0.96}, offset = {1.2, 0, 0}, material = "Metal", rgb = {66, 77, 92}, weight = true, mirror = true },
				{ name = "Stripe", shape = "Cylinder", size = {0.1, 1, 1}, offset = {1.2, 0, 0}, material = "SmoothPlastic", rgb = {81, 157, 204}, weight = false, mirror = true },
				{ name = "Collar", shape = "Cylinder", size = {0.14, 0.44, 0.44}, offset = {0.78, 0, 0}, material = "Metal", rgb = {150, 160, 168}, weight = false, mirror = true },
				{ name = "Bolt", shape = "Cylinder", size = {0.07, 0.4, 0.4}, offset = {1.565, 0, 0}, material = "Metal", rgb = {125, 139, 147}, weight = false, mirror = true },
			} },
			-- 5 Granite: speckled granite cubes with emerald gem insets
			{ color = Color3.fromRGB(176, 160, 150), material = Enum.Material.Granite, size = 1.3, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.1, 0.26, 0.26}, offset = {0, 0, 0}, material = "Metal", rgb = {67, 70, 76}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {0.78, 1.06, 1.06}, offset = {1.27, 0, 0}, material = "Granite", rgb = {112, 103, 111}, weight = true, mirror = true },
				{ name = "Band", shape = "Block", size = {0.1, 1.1, 1.1}, offset = {0.95, 0, 0}, material = "SmoothPlastic", rgb = {117, 213, 181}, weight = false, mirror = true },
				{ name = "Gem", shape = "Block", size = {0.06, 0.38, 0.38}, offset = {1.69, 0, 0}, material = "Glass", rgb = {80, 220, 150}, weight = false, mirror = true },
				{ name = "GemFront", shape = "Block", size = {0.34, 0.34, 0.06}, offset = {1.27, 0, 0.55}, material = "Glass", rgb = {80, 220, 150}, weight = false, mirror = true },
			} },
			-- 6 Golden: gold discs with twin foil rims and a glowing sun core
			{ color = Color3.fromRGB(255, 196, 48), material = Enum.Material.Metal, size = 1.4, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.2, 0.26, 0.26}, offset = {0, 0, 0}, material = "Metal", rgb = {146, 97, 32}, weight = false, mirror = false },
				{ name = "Head", shape = "Cylinder", size = {0.84, 1.16, 1.16}, offset = {1.38, 0, 0}, material = "Metal", rgb = {245, 179, 42}, weight = true, mirror = true },
				{ name = "Rim", shape = "Cylinder", size = {0.1, 1.24, 1.24}, offset = {1, 0, 0}, material = "Foil", rgb = {255, 214, 90}, weight = false, mirror = true },
				{ name = "Rim2", shape = "Cylinder", size = {0.1, 1.24, 1.24}, offset = {1.72, 0, 0}, material = "Foil", rgb = {255, 214, 90}, weight = false, mirror = true },
				{ name = "Core", shape = "Cylinder", size = {0.06, 0.66, 0.66}, offset = {1.82, 0, 0}, material = "Neon", rgb = {255, 221, 91}, weight = false, mirror = true, neon = true },
			} },
			-- 7 Mammoth: ivory marble blocks with stacked tusks curling up
			{ color = Color3.fromRGB(240, 232, 214), material = Enum.Material.Marble, size = 1.55, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.3, 0.28, 0.28}, offset = {0, 0, 0}, material = "Wood", rgb = {99, 74, 61}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {0.9, 1.22, 1.22}, offset = {1.45, 0, 0}, material = "Marble", rgb = {243, 232, 201}, weight = true, mirror = true },
				{ name = "Band", shape = "Block", size = {0.12, 1.26, 1.26}, offset = {1.12, 0, 0}, material = "Wood", rgb = {169, 126, 80}, weight = false, mirror = true },
				{ name = "Cap", shape = "Block", size = {0.06, 0.8, 0.8}, offset = {1.93, 0, 0}, material = "Wood", rgb = {169, 126, 80}, weight = false, mirror = true },
				{ name = "TuskRoot", shape = "Block", size = {0.3, 0.26, 0.32}, offset = {1.62, 0.72, 0.2}, material = "SmoothPlastic", rgb = {255, 246, 221}, weight = false, mirror = true },
				{ name = "TuskMid", shape = "Block", size = {0.24, 0.24, 0.24}, offset = {1.74, 0.94, 0.28}, material = "SmoothPlastic", rgb = {255, 248, 228}, weight = false, mirror = true },
				{ name = "TuskTip", shape = "Block", size = {0.16, 0.22, 0.18}, offset = {1.84, 1.14, 0.33}, material = "SmoothPlastic", rgb = {255, 250, 233}, weight = false, mirror = true },
			} },
			-- 8 Crystal: violet rock with glass crystal shards sprouting on top
			{ color = Color3.fromRGB(180, 110, 255), material = Enum.Material.Slate, size = 1.65, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.4, 0.28, 0.28}, offset = {0, 0, 0}, material = "Metal", rgb = {200, 205, 215}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {0.92, 1.26, 1.26}, offset = {1.54, 0, 0}, material = "Slate", rgb = {88, 70, 110}, weight = true, mirror = true },
				{ name = "Collar", shape = "Cylinder", size = {0.12, 0.5, 0.5}, offset = {1, 0, 0}, material = "Metal", rgb = {200, 205, 215}, weight = false, mirror = true },
				{ name = "Shard", shape = "Block", size = {0.28, 0.62, 0.28}, offset = {1.54, 0.9, 0}, material = "Glass", rgb = {190, 120, 255}, weight = false, mirror = true },
				{ name = "Shard2", shape = "Block", size = {0.2, 0.42, 0.2}, offset = {1.34, 0.8, 0.26}, material = "Glass", rgb = {220, 165, 255}, weight = false, mirror = true },
				{ name = "Shard3", shape = "Block", size = {0.2, 0.36, 0.2}, offset = {1.74, 0.77, -0.24}, material = "Glass", rgb = {165, 95, 240}, weight = false, mirror = true },
				{ name = "Core", shape = "Cylinder", size = {0.06, 0.62, 0.62}, offset = {2.02, 0, 0}, material = "Neon", rgb = {200, 130, 255}, weight = false, mirror = true, neon = true },
			} },
			-- 9 Obsidian: black basalt discs with a crown of 3 glass spikes, teal glow seam and core
			{ color = Color3.fromRGB(40, 220, 200), material = Enum.Material.Basalt, size = 1.75, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.5, 0.28, 0.28}, offset = {0, 0, 0}, material = "Metal", rgb = {40, 36, 48}, weight = false, mirror = false },
				{ name = "Head", shape = "Cylinder", size = {0.96, 1.3, 1.3}, offset = {1.58, 0, 0}, material = "Basalt", rgb = {34, 30, 42}, weight = true, mirror = true },
				{ name = "SpikeUp", shape = "Block", size = {0.26, 0.5, 0.26}, offset = {1.58, 0.86, 0}, material = "Glass", rgb = {55, 48, 72}, weight = false, mirror = true },
				{ name = "SpikeFront", shape = "Block", size = {0.22, 0.38, 0.22}, offset = {1.58, 0.68, 0.42}, material = "Glass", rgb = {55, 48, 72}, weight = false, mirror = true },
				{ name = "SpikeBack", shape = "Block", size = {0.22, 0.38, 0.22}, offset = {1.58, 0.68, -0.42}, material = "Glass", rgb = {55, 48, 72}, weight = false, mirror = true },
				{ name = "Seam", shape = "Cylinder", size = {0.06, 1.34, 1.34}, offset = {1.3, 0, 0}, material = "Neon", rgb = {40, 230, 210}, weight = false, mirror = true, neon = true },
				{ name = "Core", shape = "Cylinder", size = {0.06, 0.66, 0.66}, offset = {2.09, 0, 0}, material = "Neon", rgb = {40, 230, 210}, weight = false, mirror = true, neon = true },
			} },
			-- 10 Frost: ice blocks with an icicle crown and a frost core
			{ color = Color3.fromRGB(150, 220, 255), material = Enum.Material.Ice, size = 1.85, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.6, 0.28, 0.28}, offset = {0, 0, 0}, material = "Metal", rgb = {170, 200, 225}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {1, 1.4, 1.34}, offset = {1.64, 0, 0}, material = "Ice", rgb = {150, 215, 255}, weight = true, mirror = true },
				{ name = "Band", shape = "Block", size = {0.1, 1.46, 1.4}, offset = {1.24, 0, 0}, material = "Glacier", rgb = {230, 248, 255}, weight = false, mirror = true },
				{ name = "Icicle", shape = "Block", size = {0.22, 0.56, 0.22}, offset = {1.5, 0.96, 0.3}, material = "Ice", rgb = {210, 240, 255}, weight = false, mirror = true },
				{ name = "Icicle2", shape = "Block", size = {0.2, 0.74, 0.2}, offset = {1.76, 1.05, -0.2}, material = "Ice", rgb = {225, 245, 255}, weight = false, mirror = true },
				{ name = "Icicle3", shape = "Block", size = {0.18, 0.4, 0.18}, offset = {1.98, 0.88, 0.32}, material = "Ice", rgb = {200, 235, 255}, weight = false, mirror = true },
				{ name = "Core", shape = "Block", size = {0.06, 0.7, 0.7}, offset = {2.17, 0, 0}, material = "Neon", rgb = {140, 230, 255}, weight = false, mirror = true, neon = true },
			} },
			-- 11 Magma: cracked lava discs in basalt shells, flame tongues on top
			{ color = Color3.fromRGB(255, 110, 40), material = Enum.Material.CrackedLava, size = 1.95, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.7, 0.3, 0.3}, offset = {0, 0, 0}, material = "Metal", rgb = {50, 40, 38}, weight = false, mirror = false },
				{ name = "Head", shape = "Cylinder", size = {1, 1.4, 1.4}, offset = {1.7, 0, 0}, material = "CrackedLava", rgb = {255, 110, 40}, weight = true, mirror = true },
				{ name = "Shell", shape = "Cylinder", size = {0.14, 1.44, 1.44}, offset = {1.28, 0, 0}, material = "Basalt", rgb = {60, 45, 40}, weight = false, mirror = true },
				{ name = "Shell2", shape = "Cylinder", size = {0.14, 1.44, 1.44}, offset = {2.12, 0, 0}, material = "Basalt", rgb = {60, 45, 40}, weight = false, mirror = true },
				{ name = "Core", shape = "Cylinder", size = {0.07, 0.8, 0.8}, offset = {2.235, 0, 0}, material = "Neon", rgb = {255, 140, 40}, weight = false, mirror = true, neon = true },
				{ name = "Flame", shape = "Block", size = {0.26, 0.42, 0.26}, offset = {1.7, 0.88, 0}, material = "Neon", rgb = {255, 170, 50}, weight = false, mirror = true, neon = true },
				{ name = "Ember", shape = "Block", size = {0.16, 0.26, 0.16}, offset = {1.48, 0.8, 0.24}, material = "Neon", rgb = {255, 90, 30}, weight = false, mirror = true, neon = true },
			} },
			-- 12 Storm: storm-slate blocks ringed by blue neon, zigzag lightning bolts on top
			{ color = Color3.fromRGB(90, 150, 255), material = Enum.Material.Slate, size = 2.05, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.8, 0.3, 0.3}, offset = {0, 0, 0}, material = "Metal", rgb = {80, 90, 110}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {1.06, 1.56, 1.36}, offset = {1.76, 0, 0}, material = "Slate", rgb = {70, 80, 112}, weight = true, mirror = true },
				{ name = "Ring", shape = "Block", size = {0.1, 1.64, 1.42}, offset = {1.76, 0, 0}, material = "Neon", rgb = {110, 190, 255}, weight = false, mirror = true, neon = true },
				{ name = "Bolt", shape = "Block", size = {0.14, 0.36, 0.14}, offset = {1.66, 0.96, 0}, material = "Neon", rgb = {255, 232, 90}, weight = false, mirror = true, neon = true },
				{ name = "Bolt2", shape = "Block", size = {0.14, 0.32, 0.14}, offset = {1.82, 1.26, 0}, material = "Neon", rgb = {255, 232, 90}, weight = false, mirror = true, neon = true },
				{ name = "Bolt3", shape = "Block", size = {0.14, 0.28, 0.14}, offset = {1.7, 1.52, 0}, material = "Neon", rgb = {255, 232, 90}, weight = false, mirror = true, neon = true },
				{ name = "Cap", shape = "Block", size = {0.06, 0.8, 0.8}, offset = {2.32, 0, 0}, material = "Metal", rgb = {200, 210, 230}, weight = false, mirror = true },
			} },
			-- 13 Jade: jade marble blocks, gold trims, glowing green runes
			{ color = Color3.fromRGB(80, 210, 130), material = Enum.Material.Marble, size = 2.15, parts = {
				{ name = "Bar", shape = "Cylinder", size = {2.9, 0.3, 0.3}, offset = {0, 0, 0}, material = "Metal", rgb = {210, 170, 70}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {1.1, 1.66, 1.36}, offset = {1.82, 0, 0}, material = "Marble", rgb = {60, 170, 110}, weight = true, mirror = true },
				{ name = "Trim", shape = "Block", size = {0.1, 1.72, 1.42}, offset = {1.34, 0, 0}, material = "Foil", rgb = {240, 200, 90}, weight = false, mirror = true },
				{ name = "Trim2", shape = "Block", size = {0.1, 1.72, 1.42}, offset = {2.3, 0, 0}, material = "Foil", rgb = {240, 200, 90}, weight = false, mirror = true },
				{ name = "RuneFront", shape = "Block", size = {0.36, 0.36, 0.04}, offset = {1.82, 0, 0.69}, material = "Neon", rgb = {140, 255, 180}, weight = false, mirror = true, neon = true },
				{ name = "RuneTop", shape = "Block", size = {0.36, 0.06, 0.36}, offset = {1.82, 0.85, 0}, material = "Neon", rgb = {140, 255, 180}, weight = false, mirror = true, neon = true },
				{ name = "Cap", shape = "Block", size = {0.06, 0.6, 0.6}, offset = {2.4, 0, 0}, material = "Neon", rgb = {140, 255, 180}, weight = false, mirror = true, neon = true },
			} },
			-- 14 Celestial: navy glass blocks with a gold halo band, a star and a floating moon orb
			{ color = Color3.fromRGB(200, 175, 255), material = Enum.Material.Glass, size = 2.25, parts = {
				{ name = "Bar", shape = "Cylinder", size = {3, 0.3, 0.3}, offset = {0, 0, 0}, material = "Metal", rgb = {230, 225, 255}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {1.14, 1.76, 1.38}, offset = {1.86, 0, 0}, material = "Glass", rgb = {44, 40, 120}, weight = true, mirror = true },
				{ name = "Halo", shape = "Block", size = {0.08, 1.84, 1.44}, offset = {1.86, 0, 0}, material = "Neon", rgb = {255, 215, 120}, weight = false, mirror = true, neon = true },
				{ name = "Rim", shape = "Block", size = {0.12, 1.82, 1.42}, offset = {1.33, 0, 0}, material = "Foil", rgb = {255, 210, 110}, weight = false, mirror = true },
				{ name = "Star", shape = "Block", size = {0.14, 0.14, 0.04}, offset = {1.58, 0.46, 0.7}, material = "Neon", rgb = {255, 250, 225}, weight = false, mirror = true, neon = true },
				{ name = "Moon", shape = "Ball", size = {0.46, 0.46, 0.46}, offset = {1.86, 1.27, 0}, material = "Neon", rgb = {255, 240, 190}, weight = false, mirror = true, neon = true },
				{ name = "Cap", shape = "Block", size = {0.06, 0.9, 0.9}, offset = {2.46, 0, 0}, material = "Neon", rgb = {190, 170, 255}, weight = false, mirror = true, neon = true },
			} },
			-- 15 Primal: dark stone blocks in a ForceField fire aura, bone horns, wrapped grip
			{ color = Color3.fromRGB(255, 80, 50), material = Enum.Material.Slate, size = 2.4, parts = {
				{ name = "Bar", shape = "Cylinder", size = {3.1, 0.34, 0.34}, offset = {0, 0, 0}, material = "Wood", rgb = {70, 40, 30}, weight = false, mirror = false },
				{ name = "GripWrap", shape = "Cylinder", size = {0.9, 0.4, 0.4}, offset = {0, 0, 0}, material = "Fabric", rgb = {130, 40, 30}, weight = false, mirror = false },
				{ name = "Head", shape = "Block", size = {1.14, 1.86, 1.3}, offset = {1.96, 0, 0}, material = "Slate", rgb = {45, 40, 55}, weight = true, mirror = true },
				{ name = "Aura", shape = "Block", size = {1.24, 2, 1.42}, offset = {1.96, 0, 0}, material = "ForceField", rgb = {255, 110, 50}, weight = false, mirror = true },
				{ name = "Band", shape = "Block", size = {0.12, 2.04, 1.44}, offset = {1.46, 0, 0}, material = "Foil", rgb = {255, 190, 70}, weight = false, mirror = true },
				{ name = "Core", shape = "Block", size = {0.06, 1, 0.8}, offset = {2.57, 0, 0}, material = "Neon", rgb = {255, 80, 40}, weight = false, mirror = true, neon = true },
				{ name = "HornRoot", shape = "Block", size = {0.34, 0.46, 0.34}, offset = {2.1, 1.18, 0.3}, material = "Marble", rgb = {240, 226, 196}, weight = false, mirror = true },
				{ name = "HornTip", shape = "Block", size = {0.22, 0.42, 0.22}, offset = {2.28, 1.6, 0.42}, material = "Marble", rgb = {255, 240, 215}, weight = false, mirror = true },
			} },
		},
		GYM_STAND = {
			-- 1 Wooden: classic CAMP GYM: oak decks, rope lashings on the front posts, wooden post caps
			{
				palette = { wood = Color3.fromRGB(181, 122, 71), trim = Color3.fromRGB(125, 80, 46), stone = Color3.fromRGB(84, 98, 101), sign = Color3.fromRGB(44, 117, 108), signText = Color3.fromRGB(255, 255, 255) },
				materials = { wood = "Wood", trim = "Wood", stone = "Slate" },
				extras = {
					{ name = "Lashing", shape = "Block", size = {0.36, 0.14, 0.38}, offset = {4.72, 1.2, 1.23}, material = "Fabric", rgb = {204, 170, 112}, weight = false, mirror = true },
					{ name = "Lashing", shape = "Block", size = {0.36, 0.14, 0.38}, offset = {4.72, 2.8, 1.23}, material = "Fabric", rgb = {204, 170, 112}, weight = false, mirror = true },
					{ name = "UprightCap", shape = "Block", size = {0.42, 0.16, 0.44}, offset = {4.72, 3.72, 1.23}, material = "Wood", rgb = {125, 80, 46}, weight = false, mirror = true },
				},
			},
			-- 2 Stone: cobblestone footings, slate post caps, stone piles on the bottom deck ends, rope lashings
			{
				palette = { wood = Color3.fromRGB(168, 114, 70), trim = Color3.fromRGB(110, 72, 44), stone = Color3.fromRGB(124, 128, 132), sign = Color3.fromRGB(70, 84, 92), signText = Color3.fromRGB(255, 255, 255) },
				materials = { wood = "Wood", trim = "Wood", stone = "Cobblestone" },
				extras = {
					{ name = "Lashing", shape = "Block", size = {0.36, 0.14, 0.38}, offset = {4.72, 1.2, 1.23}, material = "Fabric", rgb = {204, 170, 112}, weight = false, mirror = true },
					{ name = "Lashing", shape = "Block", size = {0.36, 0.14, 0.38}, offset = {4.72, 2.8, 1.23}, material = "Fabric", rgb = {204, 170, 112}, weight = false, mirror = true },
					{ name = "UprightCap", shape = "Block", size = {0.46, 0.2, 0.48}, offset = {4.72, 3.74, 1.23}, material = "Slate", rgb = {140, 146, 150}, weight = false, mirror = true },
					{ name = "StoneStack", shape = "Block", size = {0.5, 0.4, 0.6}, offset = {4.58, 0.68, 0.3}, material = "Cobblestone", rgb = {130, 136, 140}, weight = false, mirror = true },
					{ name = "Pebble", shape = "Block", size = {0.3, 0.24, 0.34}, offset = {4.6, 0.6, -0.45}, material = "Slate", rgb = {150, 156, 160}, weight = false, mirror = true },
				},
			},
			-- 3 Bronze: bronze frame, bronze corner brackets and caps, fire braziers on the top deck ends
			{
				palette = { wood = Color3.fromRGB(176, 116, 66), trim = Color3.fromRGB(184, 104, 55), stone = Color3.fromRGB(110, 104, 98), sign = Color3.fromRGB(120, 62, 30), signText = Color3.fromRGB(255, 226, 170) },
				materials = { wood = "Wood", trim = "Metal", stone = "Slate" },
				extras = {
					{ name = "Bracket", shape = "Block", size = {0.34, 0.34, 0.06}, offset = {4.72, 0.42, 1.4}, material = "Metal", rgb = {205, 127, 50}, weight = false, mirror = true },
					{ name = "Bracket", shape = "Block", size = {0.34, 0.34, 0.06}, offset = {4.72, 2, 1.4}, material = "Metal", rgb = {205, 127, 50}, weight = false, mirror = true },
					{ name = "Bracket", shape = "Block", size = {0.34, 0.34, 0.06}, offset = {4.72, 3.58, 1.4}, material = "Metal", rgb = {205, 127, 50}, weight = false, mirror = true },
					{ name = "UprightCap", shape = "Block", size = {0.42, 0.16, 0.44}, offset = {4.72, 3.72, 1.23}, material = "Metal", rgb = {184, 104, 55}, weight = false, mirror = true },
					{ name = "Brazier", shape = "Block", size = {0.42, 0.2, 0.42}, offset = {4.6, 3.74, 0}, material = "Metal", rgb = {184, 104, 55}, weight = false, mirror = true },
					{ name = "BrazierFire", shape = "Block", size = {0.24, 0.28, 0.24}, offset = {4.6, 3.98, 0}, material = "Neon", rgb = {255, 170, 60}, weight = false, mirror = true, neon = true },
				},
			},
			-- 4 Iron: iron frame, bands and caps, blue side banners, blue lanterns on the top deck ends
			{
				palette = { wood = Color3.fromRGB(150, 102, 64), trim = Color3.fromRGB(70, 80, 94), stone = Color3.fromRGB(90, 96, 104), sign = Color3.fromRGB(40, 62, 92), signText = Color3.fromRGB(170, 220, 255) },
				materials = { wood = "Wood", trim = "Metal", stone = "Slate" },
				extras = {
					{ name = "Lashing", shape = "Block", size = {0.36, 0.14, 0.38}, offset = {4.72, 1.2, 1.23}, material = "Metal", rgb = {66, 77, 92}, weight = false, mirror = true },
					{ name = "Lashing", shape = "Block", size = {0.36, 0.14, 0.38}, offset = {4.72, 2.8, 1.23}, material = "Metal", rgb = {66, 77, 92}, weight = false, mirror = true },
					{ name = "UprightCap", shape = "Block", size = {0.44, 0.18, 0.46}, offset = {4.72, 3.73, 1.23}, material = "Metal", rgb = {90, 100, 115}, weight = false, mirror = true },
					{ name = "Banner", shape = "Block", size = {0.06, 1.5, 0.9}, offset = {4.9, 2.8, 0}, material = "Fabric", rgb = {81, 157, 204}, weight = false, mirror = true },
					{ name = "BannerBar", shape = "Block", size = {0.07, 0.14, 0.94}, offset = {4.9, 3.4, 0}, material = "Metal", rgb = {66, 77, 92}, weight = false, mirror = true },
					{ name = "Lantern", shape = "Block", size = {0.26, 0.3, 0.26}, offset = {4.6, 3.84, 0}, material = "Neon", rgb = {120, 190, 255}, weight = false, mirror = true, neon = true },
					{ name = "LanternTop", shape = "Block", size = {0.34, 0.08, 0.34}, offset = {4.6, 4.03, 0}, material = "Metal", rgb = {66, 77, 92}, weight = false, mirror = true },
				},
			},
			-- 5 Granite: granite frame and footings, granite caps with emerald gems, mint banners, green lanterns
			{
				palette = { wood = Color3.fromRGB(160, 112, 74), trim = Color3.fromRGB(112, 103, 111), stone = Color3.fromRGB(150, 140, 140), sign = Color3.fromRGB(50, 70, 64), signText = Color3.fromRGB(150, 240, 200) },
				materials = { wood = "Wood", trim = "Granite", stone = "Granite" },
				extras = {
					{ name = "UprightCap", shape = "Block", size = {0.5, 0.24, 0.52}, offset = {4.72, 3.76, 1.23}, material = "Granite", rgb = {176, 160, 150}, weight = false, mirror = true },
					{ name = "CapGem", shape = "Block", size = {0.2, 0.2, 0.06}, offset = {4.72, 3.76, 1.5}, material = "Glass", rgb = {80, 220, 150}, weight = false, mirror = true },
					{ name = "Banner", shape = "Block", size = {0.06, 1.5, 0.9}, offset = {4.9, 2.8, 0}, material = "Fabric", rgb = {117, 213, 181}, weight = false, mirror = true },
					{ name = "BannerGem", shape = "Block", size = {0.07, 0.26, 0.26}, offset = {4.91, 2.6, 0}, material = "Glass", rgb = {60, 190, 120}, weight = false, mirror = true },
					{ name = "Lantern", shape = "Block", size = {0.26, 0.3, 0.26}, offset = {4.6, 3.84, 0}, material = "Neon", rgb = {140, 255, 190}, weight = false, mirror = true, neon = true },
					{ name = "LanternTop", shape = "Block", size = {0.36, 0.1, 0.36}, offset = {4.6, 4.04, 0}, material = "Granite", rgb = {112, 103, 111}, weight = false, mirror = true },
				},
			},
			-- 6 Golden: gold foil trims on every deck edge, glowing gold orbs, red-and-gold banners, coin stacks
			{
				palette = { wood = Color3.fromRGB(190, 128, 70), trim = Color3.fromRGB(245, 179, 42), stone = Color3.fromRGB(205, 180, 130), sign = Color3.fromRGB(150, 30, 40), signText = Color3.fromRGB(255, 215, 90) },
				materials = { wood = "Wood", trim = "Foil", stone = "Sandstone" },
				extras = {
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.08, 0.04}, offset = {0, 0.4, 1.5}, material = "Foil", rgb = {245, 179, 42}, weight = false, mirror = false },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.08, 0.04}, offset = {0, 1.98, 1.5}, material = "Foil", rgb = {245, 179, 42}, weight = false, mirror = false },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.08, 0.04}, offset = {0, 3.56, 1.5}, material = "Foil", rgb = {245, 179, 42}, weight = false, mirror = false },
					{ name = "UprightCap", shape = "Block", size = {0.42, 0.16, 0.44}, offset = {4.72, 3.72, 1.23}, material = "Foil", rgb = {245, 179, 42}, weight = false, mirror = true },
					{ name = "Orb", shape = "Ball", size = {0.3, 0.3, 0.3}, offset = {4.72, 3.95, 1.23}, material = "Neon", rgb = {255, 215, 90}, weight = false, mirror = true, neon = true },
					{ name = "Banner", shape = "Block", size = {0.06, 1.5, 0.9}, offset = {4.9, 2.8, 0}, material = "Fabric", rgb = {170, 35, 45}, weight = false, mirror = true },
					{ name = "BannerTrim", shape = "Block", size = {0.07, 0.12, 0.94}, offset = {4.9, 2.1, 0}, material = "Foil", rgb = {245, 179, 42}, weight = false, mirror = true },
					{ name = "CoinStack", shape = "Block", size = {0.36, 0.24, 0.36}, offset = {4.6, 3.76, 0}, material = "Foil", rgb = {245, 179, 42}, weight = false, mirror = true },
				},
				light = Color3.fromRGB(255, 210, 80),
			},
			-- 7 Mammoth: bone-white frame, curved mammoth tusks over the front posts, fur pelts on the top deck ends, hide banners
			{
				palette = { wood = Color3.fromRGB(150, 100, 66), trim = Color3.fromRGB(240, 228, 200), stone = Color3.fromRGB(120, 110, 100), sign = Color3.fromRGB(92, 60, 40), signText = Color3.fromRGB(255, 240, 210) },
				materials = { wood = "Wood", trim = "Marble", stone = "Slate" },
				extras = {
					{ name = "Tusk", shape = "Block", size = {0.26, 0.5, 0.26}, offset = {4.72, 3.89, 1.23}, material = "Marble", rgb = {250, 242, 222}, weight = false, mirror = true },
					{ name = "Tusk2", shape = "Block", size = {0.22, 0.4, 0.22}, offset = {4.6, 4.3, 1.23}, material = "Marble", rgb = {252, 246, 230}, weight = false, mirror = true },
					{ name = "Tusk3", shape = "Block", size = {0.18, 0.3, 0.18}, offset = {4.45, 4.62, 1.23}, material = "Marble", rgb = {255, 250, 238}, weight = false, mirror = true },
					{ name = "Pelt", shape = "Block", size = {0.5, 0.12, 1.9}, offset = {4.6, 3.7, 0}, material = "Fabric", rgb = {130, 92, 60}, weight = false, mirror = true },
					{ name = "Banner", shape = "Block", size = {0.06, 1.4, 0.9}, offset = {4.9, 2.8, 0}, material = "Fabric", rgb = {196, 160, 110}, weight = false, mirror = true },
					{ name = "BannerBone", shape = "Block", size = {0.07, 0.12, 0.94}, offset = {4.9, 2.25, 0}, material = "Marble", rgb = {240, 228, 200}, weight = false, mirror = true },
					{ name = "BoneCap", shape = "Block", size = {0.42, 0.16, 0.44}, offset = {4.72, 3.72, -1.23}, material = "Marble", rgb = {240, 228, 200}, weight = false, mirror = true },
				},
			},
			-- 8 Crystal: violet slate frame, glass crystals on every post, glowing crystal clusters, neon violet deck edges
			{
				palette = { wood = Color3.fromRGB(160, 140, 175), trim = Color3.fromRGB(110, 80, 150), stone = Color3.fromRGB(90, 80, 110), sign = Color3.fromRGB(70, 40, 110), signText = Color3.fromRGB(230, 190, 255) },
				materials = { wood = "Wood", trim = "Slate", stone = "Slate" },
				extras = {
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.05, 0.04}, offset = {0, 0.4, 1.5}, material = "Neon", rgb = {180, 110, 255}, weight = false, mirror = false, neon = true },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.05, 0.04}, offset = {0, 1.98, 1.5}, material = "Neon", rgb = {180, 110, 255}, weight = false, mirror = false, neon = true },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.05, 0.04}, offset = {0, 3.56, 1.5}, material = "Neon", rgb = {180, 110, 255}, weight = false, mirror = false, neon = true },
					{ name = "Crystal", shape = "Block", size = {0.24, 0.7, 0.24}, offset = {4.72, 4, 1.23}, material = "Glass", rgb = {190, 120, 255}, weight = false, mirror = true },
					{ name = "Crystal2", shape = "Block", size = {0.18, 0.45, 0.18}, offset = {4.55, 3.87, 1.05}, material = "Glass", rgb = {220, 170, 255}, weight = false, mirror = true },
					{ name = "BackCrystal", shape = "Block", size = {0.22, 0.55, 0.22}, offset = {4.72, 3.92, -1.23}, material = "Glass", rgb = {165, 95, 240}, weight = false, mirror = true },
					{ name = "GlowCrystal", shape = "Block", size = {0.3, 0.6, 0.3}, offset = {4.6, 0.78, 0.3}, material = "Neon", rgb = {200, 130, 255}, weight = false, mirror = true, neon = true },
					{ name = "GlowCrystal2", shape = "Block", size = {0.2, 0.36, 0.2}, offset = {4.5, 0.66, -0.15}, material = "Glass", rgb = {210, 150, 255}, weight = false, mirror = true },
				},
				light = Color3.fromRGB(190, 120, 255),
			},
			-- 9 Obsidian: charcoal planks, black glass frame and spikes with teal tips, obsidian shards, teal neon deck edges and runes
			{
				palette = { wood = Color3.fromRGB(58, 52, 66), trim = Color3.fromRGB(30, 28, 38), stone = Color3.fromRGB(45, 42, 50), sign = Color3.fromRGB(20, 20, 28), signText = Color3.fromRGB(90, 255, 230) },
				materials = { wood = "WoodPlanks", trim = "Glass", stone = "Basalt" },
				extras = {
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.05, 0.04}, offset = {0, 0.4, 1.5}, material = "Neon", rgb = {40, 230, 210}, weight = false, mirror = false, neon = true },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.05, 0.04}, offset = {0, 1.98, 1.5}, material = "Neon", rgb = {40, 230, 210}, weight = false, mirror = false, neon = true },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.05, 0.04}, offset = {0, 3.56, 1.5}, material = "Neon", rgb = {40, 230, 210}, weight = false, mirror = false, neon = true },
					{ name = "Spike", shape = "Block", size = {0.26, 0.7, 0.26}, offset = {4.72, 3.99, 1.23}, material = "Glass", rgb = {40, 36, 52}, weight = false, mirror = true },
					{ name = "SpikeTip", shape = "Block", size = {0.14, 0.3, 0.14}, offset = {4.72, 4.49, 1.23}, material = "Neon", rgb = {60, 240, 220}, weight = false, mirror = true, neon = true },
					{ name = "BackSpike", shape = "Block", size = {0.22, 0.5, 0.22}, offset = {4.72, 3.89, -1.23}, material = "Glass", rgb = {40, 36, 52}, weight = false, mirror = true },
					{ name = "Shard", shape = "Block", size = {0.34, 0.56, 0.3}, offset = {4.6, 0.76, 0.2}, material = "Glass", rgb = {35, 32, 45}, weight = false, mirror = true },
					{ name = "Shard2", shape = "Block", size = {0.22, 0.36, 0.22}, offset = {4.5, 0.66, -0.35}, material = "Glass", rgb = {35, 32, 45}, weight = false, mirror = true },
					{ name = "Rune", shape = "Block", size = {0.2, 0.2, 0.04}, offset = {4.72, 1.2, 1.4}, material = "Neon", rgb = {60, 240, 220}, weight = false, mirror = true, neon = true },
				},
				light = Color3.fromRGB(40, 230, 210),
			},
			-- 10 Frost: frosted planks, ice frame and glacier footings, snow caps with ice spikes, icicles, snow drifts
			{
				palette = { wood = Color3.fromRGB(205, 225, 240), trim = Color3.fromRGB(150, 210, 250), stone = Color3.fromRGB(200, 225, 240), sign = Color3.fromRGB(60, 120, 180), signText = Color3.fromRGB(255, 255, 255) },
				materials = { wood = "WoodPlanks", trim = "Ice", stone = "Glacier" },
				extras = {
					{ name = "SnowCap", shape = "Block", size = {0.5, 0.16, 0.52}, offset = {4.72, 3.72, 1.23}, material = "Snow", rgb = {245, 250, 255}, weight = false, mirror = true },
					{ name = "IceSpike", shape = "Block", size = {0.24, 0.6, 0.24}, offset = {4.72, 4.02, 1.23}, material = "Ice", rgb = {180, 230, 255}, weight = false, mirror = true },
					{ name = "IceSpike2", shape = "Block", size = {0.16, 0.36, 0.16}, offset = {4.56, 3.9, 1.08}, material = "Ice", rgb = {205, 240, 255}, weight = false, mirror = true },
					{ name = "Icicle", shape = "Block", size = {0.12, 0.36, 0.12}, offset = {4.4, 3.3, 1.4}, material = "Ice", rgb = {200, 235, 255}, weight = false, mirror = true },
					{ name = "Icicle2", shape = "Block", size = {0.1, 0.24, 0.1}, offset = {4.4, 1.78, 1.4}, material = "Ice", rgb = {200, 235, 255}, weight = false, mirror = true },
					{ name = "Icicle3", shape = "Block", size = {0.12, 0.3, 0.12}, offset = {4.4, 0.2, 1.4}, material = "Ice", rgb = {200, 235, 255}, weight = false, mirror = true },
					{ name = "SnowMound", shape = "Block", size = {0.5, 0.2, 1.2}, offset = {4.6, 0.58, 0}, material = "Snow", rgb = {245, 250, 255}, weight = false, mirror = true },
				},
				light = Color3.fromRGB(150, 225, 255),
			},
			-- 11 Magma: charred decks, cracked-lava frame, basalt footings with glowing cracks, fire bowls, lava pools
			{
				palette = { wood = Color3.fromRGB(70, 46, 38), trim = Color3.fromRGB(255, 100, 30), stone = Color3.fromRGB(50, 44, 44), sign = Color3.fromRGB(40, 28, 26), signText = Color3.fromRGB(255, 150, 50) },
				materials = { wood = "Wood", trim = "CrackedLava", stone = "Basalt" },
				extras = {
					{ name = "Crack", shape = "Block", size = {0.5, 0.05, 0.04}, offset = {4.72, 0.18, 1.49}, material = "Neon", rgb = {255, 110, 30}, weight = false, mirror = true, neon = true },
					{ name = "PostCrack", shape = "Block", size = {0.05, 1, 0.04}, offset = {4.7, 1.1, 1.39}, material = "Neon", rgb = {255, 110, 30}, weight = false, mirror = true, neon = true },
					{ name = "FireBowl", shape = "Block", size = {0.42, 0.2, 0.44}, offset = {4.72, 3.74, 1.23}, material = "Basalt", rgb = {50, 44, 44}, weight = false, mirror = true },
					{ name = "Flame", shape = "Block", size = {0.26, 0.4, 0.26}, offset = {4.72, 4.04, 1.23}, material = "Neon", rgb = {255, 140, 40}, weight = false, mirror = true, neon = true },
					{ name = "FlameTip", shape = "Block", size = {0.14, 0.22, 0.14}, offset = {4.72, 4.34, 1.23}, material = "Neon", rgb = {255, 210, 90}, weight = false, mirror = true, neon = true },
					{ name = "LavaPool", shape = "Block", size = {0.5, 0.04, 1.6}, offset = {4.6, 0.5, 0}, material = "Neon", rgb = {255, 90, 20}, weight = false, mirror = true, neon = true },
					{ name = "MagmaRock", shape = "Block", size = {0.36, 0.3, 0.36}, offset = {4.6, 0.63, 0.55}, material = "CrackedLava", rgb = {255, 110, 40}, weight = false, mirror = true },
				},
				light = Color3.fromRGB(255, 120, 40),
			},
			-- 12 Storm: storm-blue planks, steel frame, lightning rods with sparking orbs, floating clouds, bolt banners
			{
				palette = { wood = Color3.fromRGB(90, 105, 135), trim = Color3.fromRGB(185, 195, 215), stone = Color3.fromRGB(60, 66, 80), sign = Color3.fromRGB(28, 36, 64), signText = Color3.fromRGB(255, 230, 80) },
				materials = { wood = "WoodPlanks", trim = "Metal", stone = "Slate" },
				extras = {
					{ name = "Rod", shape = "Block", size = {0.1, 0.9, 0.1}, offset = {4.72, 4.09, 1.23}, material = "Metal", rgb = {190, 200, 215}, weight = false, mirror = true },
					{ name = "RodOrb", shape = "Ball", size = {0.26, 0.26, 0.26}, offset = {4.72, 4.6, 1.23}, material = "Neon", rgb = {150, 215, 255}, weight = false, mirror = true, neon = true },
					{ name = "Cloud", shape = "Block", size = {0.6, 0.3, 0.5}, offset = {4.6, 4.6, -1.05}, material = "SmoothPlastic", rgb = {215, 222, 240}, weight = false, mirror = true },
					{ name = "Cloud2", shape = "Block", size = {0.4, 0.24, 0.4}, offset = {4.54, 4.82, -0.75}, material = "SmoothPlastic", rgb = {235, 240, 250}, weight = false, mirror = true },
					{ name = "Banner", shape = "Block", size = {0.06, 1.4, 0.9}, offset = {4.9, 2.8, 0}, material = "Fabric", rgb = {40, 50, 90}, weight = false, mirror = true },
					{ name = "Bolt", shape = "Block", size = {0.07, 0.4, 0.14}, offset = {4.91, 3, 0.08}, material = "Neon", rgb = {255, 230, 80}, weight = false, mirror = true, neon = true },
					{ name = "Bolt2", shape = "Block", size = {0.07, 0.4, 0.14}, offset = {4.91, 2.66, -0.08}, material = "Neon", rgb = {255, 230, 80}, weight = false, mirror = true, neon = true },
				},
				light = Color3.fromRGB(120, 200, 255),
			},
			-- 13 Jade: red temple wood, gold foil frame, jade footings, jade lanterns, gold spires, glowing runes
			{
				palette = { wood = Color3.fromRGB(160, 64, 48), trim = Color3.fromRGB(240, 200, 90), stone = Color3.fromRGB(80, 170, 120), sign = Color3.fromRGB(40, 130, 90), signText = Color3.fromRGB(255, 225, 120) },
				materials = { wood = "Wood", trim = "Foil", stone = "Marble" },
				extras = {
					{ name = "Lantern", shape = "Block", size = {0.34, 0.42, 0.34}, offset = {4.6, 3.86, 0}, material = "Neon", rgb = {120, 240, 160}, weight = false, mirror = true, neon = true },
					{ name = "LanternRoof", shape = "Block", size = {0.5, 0.1, 0.5}, offset = {4.6, 4.12, 0}, material = "Foil", rgb = {240, 200, 90}, weight = false, mirror = true },
					{ name = "RoofCap", shape = "Block", size = {0.5, 0.1, 0.52}, offset = {4.72, 3.69, 1.23}, material = "Foil", rgb = {240, 200, 90}, weight = false, mirror = true },
					{ name = "JadeSpire", shape = "Block", size = {0.16, 0.36, 0.16}, offset = {4.72, 3.92, 1.23}, material = "Marble", rgb = {80, 170, 120}, weight = false, mirror = true },
					{ name = "SpireBall", shape = "Ball", size = {0.2, 0.2, 0.2}, offset = {4.72, 4.2, 1.23}, material = "Foil", rgb = {240, 200, 90}, weight = false, mirror = true },
					{ name = "Rune", shape = "Block", size = {0.2, 0.26, 0.04}, offset = {4.72, 1.2, 1.4}, material = "Neon", rgb = {140, 255, 180}, weight = false, mirror = true, neon = true },
					{ name = "Rune2", shape = "Block", size = {0.2, 0.26, 0.04}, offset = {4.72, 2.8, 1.4}, material = "Neon", rgb = {140, 255, 180}, weight = false, mirror = true, neon = true },
				},
				light = Color3.fromRGB(120, 255, 170),
			},
			-- 14 Celestial: white marble rack with gold trims, sun orbs, floating violet runes and stars
			{
				palette = { wood = Color3.fromRGB(235, 232, 250), trim = Color3.fromRGB(255, 210, 110), stone = Color3.fromRGB(190, 190, 225), sign = Color3.fromRGB(34, 32, 90), signText = Color3.fromRGB(255, 225, 140) },
				materials = { wood = "Marble", trim = "Foil", stone = "Marble" },
				extras = {
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.08, 0.04}, offset = {0, 0.4, 1.5}, material = "Foil", rgb = {255, 210, 110}, weight = false, mirror = false },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.08, 0.04}, offset = {0, 1.98, 1.5}, material = "Foil", rgb = {255, 210, 110}, weight = false, mirror = false },
					{ name = "DeckTrim", shape = "Block", size = {9.72, 0.08, 0.04}, offset = {0, 3.56, 1.5}, material = "Foil", rgb = {255, 210, 110}, weight = false, mirror = false },
					{ name = "GoldCap", shape = "Block", size = {0.44, 0.12, 0.46}, offset = {4.72, 3.7, 1.23}, material = "Foil", rgb = {255, 210, 110}, weight = false, mirror = true },
					{ name = "SunOrb", shape = "Ball", size = {0.36, 0.36, 0.36}, offset = {4.72, 3.95, 1.23}, material = "Neon", rgb = {255, 220, 130}, weight = false, mirror = true, neon = true },
					{ name = "FloatRune", shape = "Block", size = {0.26, 0.26, 0.06}, offset = {4.72, 4.45, 1.23}, material = "Neon", rgb = {190, 170, 255}, weight = false, mirror = true, neon = true },
					{ name = "FloatRune2", shape = "Block", size = {0.22, 0.22, 0.06}, offset = {4.5, 4.85, 0.6}, material = "Neon", rgb = {190, 170, 255}, weight = false, mirror = true, neon = true },
					{ name = "StarA", shape = "Ball", size = {0.18, 0.18, 0.18}, offset = {4.6, 5.15, 0}, material = "Neon", rgb = {255, 250, 220}, weight = false, mirror = true, neon = true },
					{ name = "StarB", shape = "Ball", size = {0.16, 0.16, 0.16}, offset = {4.85, 4.1, -0.6}, material = "Neon", rgb = {255, 250, 220}, weight = false, mirror = true, neon = true },
				},
				light = Color3.fromRGB(200, 180, 255),
			},
			-- 15 Primal: dark ancient wood, fire-gold trims, granite footings, giant bone horns, aura fires, crimson fang banners
			{
				palette = { wood = Color3.fromRGB(82, 52, 40), trim = Color3.fromRGB(230, 120, 40), stone = Color3.fromRGB(60, 56, 62), sign = Color3.fromRGB(90, 20, 20), signText = Color3.fromRGB(255, 190, 80) },
				materials = { wood = "Wood", trim = "Foil", stone = "Granite" },
				extras = {
					{ name = "Horn", shape = "Block", size = {0.36, 0.5, 0.36}, offset = {4.72, 3.89, 1.23}, material = "Marble", rgb = {240, 226, 196}, weight = false, mirror = true },
					{ name = "Horn2", shape = "Block", size = {0.3, 0.44, 0.3}, offset = {4.62, 4.35, 1.18}, material = "Marble", rgb = {246, 234, 206}, weight = false, mirror = true },
					{ name = "Horn3", shape = "Block", size = {0.22, 0.38, 0.22}, offset = {4.48, 4.74, 1.1}, material = "Marble", rgb = {250, 240, 215}, weight = false, mirror = true },
					{ name = "HornTip", shape = "Block", size = {0.14, 0.3, 0.14}, offset = {4.37, 5.06, 1}, material = "Marble", rgb = {255, 246, 225}, weight = false, mirror = true },
					{ name = "Fire", shape = "Block", size = {0.28, 0.4, 0.28}, offset = {4.6, 3.84, 0}, material = "Neon", rgb = {255, 120, 40}, weight = false, mirror = true, neon = true },
					{ name = "FireAura", shape = "Block", size = {0.5, 0.7, 0.5}, offset = {4.6, 3.99, 0}, material = "ForceField", rgb = {255, 90, 40}, weight = false, mirror = true },
					{ name = "Banner", shape = "Block", size = {0.06, 1.5, 0.9}, offset = {4.9, 2.75, 0}, material = "Fabric", rgb = {150, 25, 25}, weight = false, mirror = true },
					{ name = "Fang", shape = "Block", size = {0.07, 0.3, 0.3}, offset = {4.91, 2.3, 0}, material = "Neon", rgb = {255, 170, 60}, weight = false, mirror = true, neon = true },
				},
				light = Color3.fromRGB(255, 110, 50),
			},
		},
	}
	Config.DUMBBELL_LOOK = D.DUMBBELL_LOOK
	Config.GYM_STAND = D.GYM_STAND
	for i, nm in D.NAMES do
		if Config.DUMBBELL[i] then
			Config.DUMBBELL[i].name = nm
		end
	end
end
Config.REP_COOLDOWN = 0.55

-- Сумка: вместимость по уровням
Config.BAG = {
	{ cap = 12, cost = 0 },
	{ cap = 20, cost = 300 },
	{ cap = 30, cost = 2500 },
	{ cap = 45, cost = 20000 },
	{ cap = 70, cost = 150000 },
	{ cap = 100, cost = 1000000 },
}
Config.WRAP_MULT = 2 -- упакованная добыча продаётся ×2
Config.WRAP_MIN_TIME = 2.5

---------------------------------------------------------------------
-- Уровень и опыт
---------------------------------------------------------------------
Config.XP = {
	perRarity = { 5, 12, 30, 80, 250, 1000 },
	tierBonus = 0.15, -- +15% опыта за каждую ступень множителя
}
function Config.xpForLevel(lvl: number): number
	return math.floor(40 * lvl ^ 1.55)
end
function Config.levelReward(lvl: number): number
	return math.floor(25 * lvl ^ 1.8)
end

---------------------------------------------------------------------
-- Бусты (правая панель)
---------------------------------------------------------------------
Config.BOOSTS = {
	luck = { name = "Luck ×2", icon = "🍀", color = Color3.fromRGB(90, 220, 110), mult = 2 },
	coins = { name = "Coins ×2", icon = "💰", color = Color3.fromRGB(255, 200, 50), mult = 2 },
	range = { name = "Range +25%", icon = "🏹", color = Color3.fromRGB(80, 170, 255), mult = 1.25 },
	tension = { name = "Steady Grip", icon = "💪", color = Color3.fromRGB(255, 120, 90), mult = 0.85 }, -- alpha × 0.85
}
-- Зелья Травницы
Config.POTIONS = {
	{ boost = "luck", dur = 300, cost = 120, k = 0.10 },
	{ boost = "coins", dur = 300, cost = 200, k = 0.35 },
	{ boost = "range", dur = 300, cost = 150, k = 0.10 },
	{ boost = "tension", dur = 240, cost = 260, k = 0.10 },
}
-- Цена зелья = доля k от дохода за время действия при лучшем купленном копье (бросок ≈ THROW_SECONDS).
-- Раньше зелья стоили 120-260 монет всегда и в поздней игре были бесплатными.
Config.THROW_SECONDS = 12
function Config.potionCost(p: any, d: any): number
	-- по лучшему из купленных копий: смена копья перед покупкой цену не снижает
	local best = 1
	for id in (d and d.spears or {}) do
		local sp = Config.SPEAR_BY_ID[id]
		if sp and sp.index > best then
			best = sp.index
		end
	end
	local ev = Config.EV_BY_SPEAR[best] or 0
	local worth = ev * p.dur / Config.THROW_SECONDS
	-- Зелье монет умножает всю продажу, поэтому полная сумка тоже считается: иначе его можно купить
	-- за копейки и продать сразу всю сумку.
	if p.boost == "coins" and d and d.items then
		local bag = 0
		for _, it in d.items do
			bag += it.price * (it.wrapped and Config.WRAP_MULT or 1)
		end
		worth = math.max(worth, bag)
	end
	return math.max(p.cost, round3(worth * p.k))
end

---------------------------------------------------------------------
-- Задания NPC (kind: catch, rarity, zone, tier, sell, range, course, collect, wrap, train)
---------------------------------------------------------------------
Config.QUESTS = {
	{ id = "q1", npc = "hunter", title = "First Catch", text = "Catch 3 animals", kind = "catch", goal = 3, reward = { coins = 60, xp = 30 } },
	{ id = "q2", npc = "hunter", title = "Strong Arm", text = "Make a throw at ×5 or higher", kind = "tier", arg = 5, goal = 1, reward = { coins = 120, boost = "luck", dur = 180 } },
	{ id = "q3", npc = "tracker", title = "Into the Woods", text = "Catch an animal in the Deep Woods", kind = "zone", arg = 2, goal = 1, reward = { coins = 200, xp = 60 } },
	{ id = "q4", npc = "herbalist", title = "Fireflies", text = "Collect 5 fireflies", kind = "collect", arg = "ff", goal = 5, reward = { coins = 150, boost = "coins", dur = 240 } },
	{ id = "q5", npc = "hunter", title = "Sharp Eye", text = "Score 60 points at the target range", kind = "range", goal = 60, reward = { coins = 250, xp = 80 } },
	{ id = "q6", npc = "tracker", title = "A Rare Trail", text = "Catch a rare animal", kind = "rarity", arg = 3, goal = 1, reward = { coins = 400, boost = "range", dur = 300 } },
	{ id = "q7", npc = "herbalist", title = "Camp Workout", text = "Do 25 dumbbell reps", kind = "train", goal = 25, reward = { coins = 300, xp = 100 } }, -- V78: полосы препятствий больше нет, задание про неё заменено
	{ id = "q8", npc = "hunter", title = "Forest Champion", text = "Make a throw at ×25 or higher", kind = "tier", arg = 25, goal = 1, reward = { coins = 1500, boost = "tension", dur = 240 } },
	{ id = "q9", npc = "tracker", title = "Ancient Trails", text = "Catch an animal in the Ancient Forest", kind = "zone", arg = 4, goal = 1, reward = { coins = 5000, xp = 400 } },
	{ id = "q10", npc = "herbalist", title = "Egg Hunt", text = "Find 5 hidden eggs", kind = "collect", arg = "egg", goal = 5, reward = { coins = 2500, boost = "luck", dur = 600 } },
	{ id = "q11", npc = "hunter", title = "Trader", text = "Sell catches worth 1K coins", kind = "sell", goal = 1000, reward = { coins = 800, xp = 150 } },
	{ id = "q12", npc = "tracker", title = "Legend", text = "Make a throw at ×100", kind = "tier", arg = 100, goal = 1, reward = { coins = 20000, boost = "luck", dur = 900 } },
}

-- Реплики NPC (Dialog). V84: role — подпись под именем; greet — приветствия (одно при первом разговоре за сессию);
-- lines — советы по кругу. Задание этого NPC и подсказку по прогрессу игрока Dialog добавляет сам.
Config.NPC = {
	hunter = { name = "Quest Board", role = "Hunter's Lodge", color = Color3.fromRGB(110, 200, 90), greet = {
		"Welcome to the lodge, hunter! Every job posted here pays in coins, XP or a free boost.",
		"Back again? Good. The forest never runs out of work.",
	}, lines = {
		"Step onto the red floor of the Throwing Grounds. It takes you straight to the throwing spot.",
		"Hold to charge your throw. The longer you hold, the bigger the multiplier: ×2, ×5, ×10, ×25 and ×100.",
		"When the spear starts shaking, let go. If your grip slips, the spear still flies just as far, but most of the luck you built up is lost.",
		"Longer throws land in deeper zones, where bigger and rarer animals live.",
		"Strength decides how far you can throw. Train at the dumbbell stand beside your cabin.",
		"The Hunter Pass has its own missions. Open Pass on the left to see today's.",
	} },
	herbalist = { name = "Herbalist", role = "Potions & Remedies", color = Color3.fromRGB(220, 120, 220), greet = {
		"Come in, come in! Mind the cauldron, it bites.",
		"Oh, it's you! I just finished a fresh batch.",
	}, lines = {
		"My luck potions smell like chamomile and coins.",
		"A potion works for a few minutes. Drink it right before a long hunt, not after.",
		"Fireflies gather in the shade near the village. Walk into them to catch them.",
		"There are eggs hidden around the village. Look behind the cabins and in the grass!",
		"Pets hatch from eggs in the Shop. A good pet brings luck, coins or a longer throw.",
	} },
	tracker = { name = "Tracker", role = "Knows Every Trail", color = Color3.fromRGB(240, 180, 80), greet = {
		"Quiet... hear that? No? Good. Means it hasn't smelled us yet.",
		"You again. Your boots are loud, but your aim is getting better.",
	}, lines = {
		"Every zone is a world of its own. Glowing mushrooms light the Wild Marsh.",
		"A Spirit Deer was spotted in the Wild Marsh. Rare as a quiet goose.",
		"Something big and furry lives in the Ancient Forest. Bring a sharp spear.",
		"The Collection shows every animal you have caught, and the shadows of those you haven't.",
		"Climb the lookout tower to see the whole forest at once.",
		"They say there is a volcano at the edge of the world. No spear has ever reached it.",
	} },
	armorer = { name = "Armorer", role = "Spears for Every Hunt", color = Color3.fromRGB(120, 180, 255), greet = {
		"Looking for something sharper? You came to the right rack.",
	}, lines = {
		"A better spear means new animals. That old stick will not catch a Yeti.",
		"Sharp spears pierce tougher hides. Some animals shrug off anything less.",
		"Every spear has its own luck and range. Read the card before you buy.",
		"Spears you own stay yours. Switch between them any time, for free.",
	} },
	merchant = { name = "Merchant", role = "Buys Every Catch", color = Color3.fromRGB(255, 200, 60), greet = {
		"Fresh catch? Put it on the counter, let me have a look!",
	}, lines = {
		"Wrapped catches sell for twice as much!",
		"Prices change through the day. Check the tags in my window before you sell.",
		"A bigger bag means fewer trips back to camp. I sell those too.",
		"Rare animals are worth keeping an eye on. One good catch can pay for a new spear.",
	} },
	smith = { name = "Blacksmith", role = "Forge & Upgrades", color = Color3.fromRGB(255, 130, 60), greet = {
		"Hot day for hammering. What are we improving?",
	}, lines = {
		"Bring me your spear and I will improve its luck and range.",
		"Each forge level costs more than the last, but a tuned spear outlasts three new ones.",
		"I work on the spear in your hands. Pick your favourite before you pay.",
	} },
}

---------------------------------------------------------------------
-- Активности (заглушки наград — в демо выдаются сразу)
---------------------------------------------------------------------
Config.ACTIVITY = {
	range = { shots = 6, coinPerPoint = 1, xpPerPoint = 0.5 },
	course = { coins = 120, xp = 60, coinPerCoin = 5, parTime = 150 }, -- V74: полоса втрое длиннее, время на бонус 150 с (совпадает с COURSE_PAR в Client/Activities)
	firefly = { coins = 15, xp = 5 },
	egg = { coins = 250, xp = 50 },
	lookout = { coins = 25, xp = 10, once = true },
	campfire = { coinsPerMin = 2 },
}

-- Обучение: шаги подсказок (стрелка ведёт к цели)
Config.TUTORIAL = {
	{ text = "Go to the Throwing Grounds at the forest edge", target = "ambush" },
	{ text = "Hold to charge your throw! Release before your grip slips", target = "throw" },
	{ text = "Sell your catch to the Merchant in the plaza", target = "market" },
	{ text = "Buy a new spear at the Armory", target = "armory" },
	{ text = "Train with dumbbells beside your cabin", target = "gym" },
}

---------------------------------------------------------------------
-- Формат чисел
---------------------------------------------------------------------
Config.SUFFIXES = { "", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "De" }

---------------------------------------------------------------------
-- Производные таблицы и формулы
---------------------------------------------------------------------
-- V25: цены видов зон 5-25 пересчитаны (x PRICE_PHI). В V24 доход скакал в 3800 раз между зонами 4 и 5,
-- а копья 6-10 стоили до 100 000 бросков. Теперь рост плавный (см. SHOP.md, раздел "Экономика").
Config.PRICE_PHI = 4.4e-4
for _, sp in Config.SPECIES do
	if sp.zone >= 5 then
		sp.price = math.max(1, round3(sp.price * Config.PRICE_PHI))
	end
end

Config.SPECIES_BY_ID = {} :: { [string]: any }
for i, sp in Config.SPECIES do
	sp.index = i
	Config.SPECIES_BY_ID[sp.id] = sp
end
Config.SPEAR_BY_ID = {} :: { [string]: any }
for i, s in Config.SPEARS do
	s.index = i
	Config.SPEAR_BY_ID[s.id] = s
end
Config.QUEST_BY_ID = {} :: { [string]: any }
for i, q in Config.QUESTS do
	q.index = i
	Config.QUEST_BY_ID[q.id] = q
end

-- V86: дальность по Силе — таблица точек (Сила -> дальность без копья), между точками геометрическая интерполяция.
-- Точка зоны z: Сила входа в зону (start + perLevel*levelsPerZone*(z-1)); первое копьё этой зоны при полном заряде
-- долетает до середины зоны. Сила дальше своего копья не уводит: см. Config.spearReach.
local rangePts: { { number } }? = nil
local function buildRangePts(): { { number } }
	local S = Config.STRENGTH
	local step = S.perLevel * S.levelsPerZone
	local firstRange: { [number]: number } = {}
	for _, sp in Config.SPEARS do
		if firstRange[sp.zone] == nil then
			firstRange[sp.zone] = sp.range
		end
	end
	local pts = { { S.start, 25 } }
	for z = 2, #Config.ZONES do
		local zn = Config.ZONES[z]
		table.insert(pts, { S.start + step * (z - 1), (zn.from + zn.to) * 0.5 / (firstRange[z] or 1) })
	end
	local last = Config.ZONES[#Config.ZONES]
	local best = Config.SPEARS[#Config.SPEARS].range
	table.insert(pts, { S.start + step * #Config.ZONES, last.to / best })
	return pts
end

function Config.range(power: number): number
	local pts = rangePts
	if not pts then
		pts = buildRangePts()
		rangePts = pts
	end
	local p = math.max(tonumber(power) or 0, 1)
	if p <= pts[1][1] then
		return pts[1][2] * math.sqrt(p / pts[1][1])
	end
	for i = 2, #pts do
		local a, b = pts[i - 1], pts[i]
		if p <= b[1] then
			local t = (p - a[1]) / (b[1] - a[1])
			return a[2] * (b[2] / a[2]) ^ t
		end
	end
	return math.min(pts[#pts][2], Config.THROW.maxRange)
end

-- V86: потолок копья — самая дальняя зона, где оно ещё берёт обычного (Common) зверя: обычно на 1-2 зоны дальше
-- своей зоны (Config.SPEARS[i].zone). Сила ведёт бросок до этого края; дальше нужен лучший наконечник, иначе бросок
-- уходил туда, где не взять никого. Кузница и зелье дальности помогают долететь до края с меньшей Силой, но не дальше.
local maxZoneCache: { [string]: number } = {}
function Config.spearMaxZone(spearId: string): number
	local s = Config.SPEAR_BY_ID[spearId] or Config.SPEARS[1]
	local cached = maxZoneCache[s.id]
	if cached then
		return cached
	end
	local best = math.clamp(s.zone or 1, 1, #Config.ZONES)
	for _, sp in Config.SPECIES do
		if sp.rarity == 1 and sp.zone > best and sp.zone <= #Config.ZONES and sp.sharp <= s.sharp and sp.weight <= s.heavy then
			best = sp.zone
		end
	end
	maxZoneCache[s.id] = best
	return best
end

function Config.spearReach(spearId: string): number
	local z = Config.ZONES[Config.spearMaxZone(spearId)]
	return math.min(z.to - 0.01, Config.MAX_THROW_DISTANCE or Config.THROW.maxRange)
end

-- V86: одна формула дальности броска для сервера, окна охоты и диалогов. Потолок копья ограничивает полный бросок,
-- а заряд (distFrac) действует уже после него: даже с лишней Силой бросок ×1 короче, чем ×100, и не все в одну точку
function Config.throwDist(power: number, st: any, rangeBoost: number, m: number): number
	local full = math.min(Config.range(power) * st.range * (rangeBoost or 1), Config.spearReach(st.id))
	return math.min(full * Config.distFrac(m), Config.MAX_THROW_DISTANCE or Config.THROW.maxRange)
end

-- m(t) = e^(r·t), не больше капа
function Config.tensionAt(t: number): number
	return math.min(Config.TENSION.cap, math.exp(Config.TENSION.rate * math.max(t, 0)))
end
-- время, за которое множитель дорастёт до m
function Config.timeFor(m: number): number
	return math.log(math.max(m, 1)) / Config.TENSION.rate
end

-- Ступень по множителю (1..6)
function Config.tierIndex(m: number): number
	local idx = 1
	for i, t in Config.TIERS do
		if m >= t.m - 1e-6 then
			idx = i
		end
	end
	return idx
end

-- Доля дальности по множителю: 0.3 + 0.7·ln m / ln 100
function Config.distFrac(m: number): number
	local f = Config.THROW.minFrac + (1 - Config.THROW.minFrac) * math.log(math.max(m, 1)) / math.log(Config.TENSION.cap)
	return math.clamp(f, 0, 1)
end

function Config.distLuck(d: number): number
	return 1 + d / Config.THROW.distLuckDiv
end

-- V86: удача от Силы считается от дальности, как раньше при 8·√Сила: та же дальность — та же удача
function Config.powerLuck(power: number): number
	local eq = (Config.range(power) / 8) ^ 2
	return 1 + 0.5 * math.log10(math.max(eq, 10) / 10)
end

function Config.flightTime(d: number): number
	local distance = math.max(0, d)
	local familiar = math.min(distance, 230)
	local travel = Config.THROW.flightBase + familiar * Config.THROW.flightPerStud
	if distance > 230 then travel += math.log(1 + (distance - 230) / 230) * 0.85 end
	return math.min(Config.THROW.maxFlightTime, travel) * (Config.THROW.flightSlow or 1)
end

function Config.zoneFor(d: number): number
	-- Зоны 20-25 откроются, когда поднимут MAX_THROW_DISTANCE (и появятся копья нужных ступеней и местность)
	if Config.MAX_THROW_DISTANCE and d >= Config.MAX_THROW_DISTANCE then
		d = Config.MAX_THROW_DISTANCE - 0.001
	end
	for i = #Config.ZONES, 1, -1 do
		if d >= Config.ZONES[i].from then
			return i
		end
	end
	return 1
end

-- Характеристики копья с учётом уровня кузницы
function Config.spearStats(id: string, lvl: number?): any
	local s = Config.SPEAR_BY_ID[id] or Config.SPEARS[1]
	local l = math.clamp(lvl or 0, 0, Config.FORGE.maxLevel)
	return {
		id = s.id,
		name = s.name,
		zone = s.zone,
		sharp = s.sharp,
		heavy = s.heavy,
		luck = s.luck * (1 + Config.FORGE.luckPer * l),
		range = s.range * (1 + Config.FORGE.rangePer * l),
		alpha = math.max(0.08, s.alpha - Config.FORGE.alphaPer * l),
		level = l,
	}
end

function Config.forgeCost(id: string, lvl: number): number
	local s = Config.SPEAR_BY_ID[id] or Config.SPEARS[1]
	return math.floor(math.max(40, s.price * Config.FORGE.costMul) * (lvl + 1) ^ 1.7)
end

---------------------------------------------------------------------
-- Robux-магазин (Client/Shop, Client/Perks, Server/Shop).
-- id — номер Game Pass / Developer Product из Creator Dashboard.
-- id = 0: товар ещё не создан. В Studio покупка имитируется (тест без Robux),
-- в живой игре кнопка показывает SOON и ничего не продаёт.
-- price — запасная цифра для кнопки; настоящая цена читается из MarketplaceService.
---------------------------------------------------------------------
Config.BOOSTS.server = { name = "Server Luck ×2", icon = "🎉", color = Color3.fromRGB(110, 190, 255), mult = 1 }
-- Только за Robux: бесплатного эквивалента в игре нет.
Config.BOOSTS.fortune = { name = "Golden Hour", icon = "✨", color = Color3.fromRGB(255, 200, 50), mult = 1 }
Config.BOOSTS.jackpot = { name = "Jackpot Hour", icon = "🎰", color = Color3.fromRGB(255, 90, 140), mult = 1 }
Config.BOOSTS.fair = { name = "Trade Fair", icon = "🎪", color = Color3.fromRGB(90, 220, 200), mult = 1 }

Config.SHOP = {
	DATASTORE = "SpearHunt_v1",
	STARTER_MAX_LEVEL = 10,
	COIN_REF_MIN = 5000,
	-- Правило каталога: у каждого товара нет бесплатного эквивалента в игре.
	--   charm   - потолки редкости +50% (бесплатные зелья дают +25% и ненадолго)
	--   insight - прогноз рынка на 6 часов (бесплатно виден только текущий час)
	--   broker  - цена почти не падает, когда продаёшь много одного вида
	--   smith   - уровни кузницы 6-7 и скидка 25% (бесплатно максимум 5)
	--   wrap    - завернуть всю сумку одним бантом (бесплатно по одной штуке)
	--   vip     - продажа из любого места, золотая метка, +15% опыта
	PASSES = {
		{ key = "charm", id = 0, price = 399, name = "Lucky Charm", desc = "Rare animal chances +50% forever. Luck x2." },
		{ key = "insight", id = 0, price = 299, name = "Market Insight", desc = "See which rarity is in hot demand for the next 6 hours." },
		{ key = "broker", id = 0, price = 349, name = "Silver Broker", desc = "Selling many of one animal barely lowers its price." },
		{ key = "smith", id = 0, price = 399, name = "Master Smith", desc = "Forge levels 6 and 7. Forging costs 25% less." },
		{ key = "wrap", id = 0, price = 249, name = "Master Wrapper", desc = "Tie one bow and your whole bag is wrapped." },
		{ key = "vip", id = 0, price = 449, name = "VIP Hunter", desc = "Sell from anywhere. Gold VIP tag. +15% XP." },
		-- Лимитированный Founder показывается баннером (в сетке пассов его нет).
		{ key = "founder", id = 0, price = 799, name = "Founder's Edition", desc = "Purple FOUNDER tag, Starlight aura and a bigger daily gift. Limited edition." },
	},
	PRODUCTS = {
		{ key = "starter", id = 0, price = 79, kind = "starter", name = "Starter Pack" },
		{ key = "fortune20", id = 0, price = 79, kind = "boost", boosts = { "fortune" }, dur = 1200, name = "Golden Hour", desc = "Gold and Rainbow mutations come up much more often for 20 min of play." },
		{ key = "jackpot20", id = 0, price = 99, kind = "boost", boosts = { "jackpot" }, dur = 1200, name = "Jackpot Hour", desc = "Rare animal chances +100% for 20 min of play." },
		{ key = "fair30", id = 0, price = 59, kind = "boost", boosts = { "fair" }, dur = 1800, name = "Trade Fair", desc = "No price drops from selling and no weak-demand hours for 30 min." },
		-- Набор: 3 буста на 30 минут. По частям то же стоит 79 x1.5 + 99 x1.5 + 59 = 326 R$.
		{ key = "hour_bundle", id = 0, price = 199, kind = "boost", boosts = { "fortune", "jackpot", "fair" }, dur = 1800, name = "Hunter's Bundle", desc = "Golden Hour, Jackpot Hour and Trade Fair together for 30 min of play." },
		-- V28: яйца (бросок на сервере, шансы в Config.EGGS). id = 0: в Studio покупка имитируется.
		{ key = "egg_forest", id = 0, price = 59, kind = "egg", name = "Forest Talisman Egg", desc = "Common to Epic pets." },
		{ key = "egg_amber", id = 0, price = 149, kind = "egg", name = "Amber Heart Egg", desc = "Uncommon to Legendary pets." },
		{ key = "egg_tide", id = 0, price = 299, kind = "egg", name = "Tide Pearl Egg", desc = "Rare to Mythic pets." },
		{ key = "egg_storm", id = 0, price = 599, kind = "egg", name = "Storm Heart Egg", desc = "Epic to Divine pets." },
		{ key = "egg_astral", id = 0, price = 999, kind = "egg", name = "Astral Core Egg", desc = "Legendary to Divine pets." },
		{ key = "server15", id = 0, price = 149, kind = "server", dur = 900, name = "Server Luck", desc = "Luck x2 and rare chances +25% for everyone on the server for 15 min." },
		{ key = "coins1", id = 0, price = 49, kind = "coins", k = 0.3, name = "Coin Pouch" },
		{ key = "coins2", id = 0, price = 99, kind = "coins", k = 0.8, name = "Coin Sack" },
		{ key = "coins3", id = 0, price = 199, kind = "coins", k = 2, name = "Coin Chest" },
		{ key = "coins4", id = 0, price = 399, kind = "coins", k = 5, name = "Hunter's Hoard", best = true },
		-- V71: Hunter Pass. kind "hpass": в каталог магазина не попадает, продаётся окном пропуска.
		{ key = "pass_premium", id = 0, price = 299, kind = "hpass", name = "Hunter Pass Premium", desc = "Unlocks the gold reward row of the Hunter Pass for the whole season." },
		{ key = "pass_bundle", id = 0, price = 499, kind = "hpass", xp = 3000, name = "Hunter Pass + 10 Tiers", desc = "Premium and 10 tiers (3000 Pass XP) right away." },
	},
	STARTER = { spear = "iron", coins = 4000, bagLvl = 3, boost = "fortune", dur = 1800 },
	-- V26: ранг поддержки по сумме потраченных Robux (пассы считаются по владению, товары по чекам).
	-- Плюшки без бесплатного пути: слоты сумки сверх бесплатных 100, быстрое восстановление цен на рынке,
	-- ежедневный подарок (доля цены следующего копья) и бесплатный Market Insight у Diamond.
	GIFT_BASE = 0.02, -- подарок без ранга
	GIFT_HOURS = 20,
	RANKS = {
		{ name = "Bronze", at = 50, color = Color3.fromRGB(214, 140, 70), bag = 0, gift = 0.04, recover = 1.25 },
		{ name = "Silver", at = 200, color = Color3.fromRGB(214, 224, 238), bag = 20, gift = 0.08, recover = 1.5 },
		{ name = "Gold", at = 500, color = Color3.fromRGB(255, 204, 64), bag = 40, gift = 0.15, recover = 2 },
		{ name = "Diamond", at = 1000, color = Color3.fromRGB(120, 224, 255), bag = 60, gift = 0.25, recover = 3, insight = true },
	},
	-- Бонусы одной характеристики складываются, а не перемножаются.
	PERK = {
		charmLuck = 1, charmCaps = 0.5,
		boostCaps = 0.25, -- зелье удачи за монеты
		jackpotCaps = 1.0,
		serverLuck = 1, serverCaps = 0.25,
		vipXp = 0.15,
		smithLevels = 2, smithDiscount = 0.25,
		fortuneMutMul = 3,
		forecastHours = 6,
	},
}
Config.SHOP_BY_KEY = {} :: { [string]: any }
for _, it in Config.SHOP.PASSES do
	it.pass = true
	Config.SHOP_BY_KEY[it.key] = it
end
for _, it in Config.SHOP.PRODUCTS do
	Config.SHOP_BY_KEY[it.key] = it
end

---------------------------------------------------------------------
-- V71: Hunter Pass (боевой пропуск). Имена hpass/pass* без путаницы с Game Pass: Config.pass* - только про этот пропуск.
-- Награда R: client-сторона (coins, power) или server-сторона (egg, boost, tag, aura); ряд бывает только одной стороны.
---------------------------------------------------------------------
do
	local function C(k: number): any
		return { type = "coins", k = k }
	end
	local function S(n: number): any
		return { type = "power", n = n }
	end
	local function E(key: string): any
		return { type = "egg", key = key }
	end
	local function B(key: string): any
		return { type = "boost", key = key }
	end
	local function T(text: string, color: Color3): any
		return { type = "tag", text = text, color = color }
	end
	local function A(name: string, color: Color3): any
		return { type = "aura", name = name, color = color }
	end
	-- V74: зелье Травницы на dur секунд (luck, coins, range, tension из Config.BOOSTS): выдаёт клиентская экономика
	local function P(boost: string, dur: number): any
		return { type = "potion", boost = boost, dur = dur }
	end
	-- V74: осколки питомцев (улучшение питомцев): выдаёт сервер
	local function H(n: number): any
		return { type = "shards", n = n }
	end
	local function R(free: { any }, premium: { any }): any
		return { free = free, premium = premium }
	end
	Config.PASS = {
		name = "Hunter Pass",
		season = "Pinewatch",
		START = 1794873600, -- 2026-11-17 00:00:00 UTC
		DAYS = 28,
		TIERS = 30,
		XP_PER_TIER = 300,
		BUNDLE_XP = 3000,
		BUNDLE_MAX_XP = 6000,
		DAILY = {
			{
				{ id = "dA1", text = "Catch 8 animals", kind = "catch", goal = 8, xp = 100 },
				{ id = "dA2", text = "Complete 30 dumbbell reps", kind = "train", goal = 30, xp = 100 },
				{ id = "dA3", text = "Wrap 5 catches", kind = "wrap", goal = 5, xp = 100 },
			},
			{
				{ id = "dB1", text = "Catch 5 animals in zone 1", kind = "zone", arg = 1, goal = 5, xp = 100 },
				{ id = "dB2", text = "Throw at x2 or more 4 times", kind = "tier", arg = 2, goal = 4, xp = 100 },
				{ id = "dB3", text = "Complete 20 dumbbell reps", kind = "train", goal = 20, xp = 100 }, -- светлячки собираются один раз за аккаунт: задание бы застревало
			},
			{
				{ id = "dC1", text = "Catch 2 animals of rarity 2+", kind = "rarity", arg = 2, goal = 2, xp = 100 },
				{ id = "dC2", text = "Sell catches worth 100 coins", kind = "sell", goal = 100, xp = 100 },
				{ id = "dC3", text = "Score 30 points at the target range", kind = "range", goal = 30, xp = 100 },
			},
			{
				{ id = "dD1", text = "Throw at x5 or more twice", kind = "tier", arg = 5, goal = 2, xp = 100 },
				{ id = "dD2", text = "Score 40 points at the target range", kind = "range", goal = 40, xp = 100 }, -- V78: вместо полосы препятствий
				{ id = "dD3", text = "Wrap 3 catches", kind = "wrap", goal = 3, xp = 100 }, -- яйца в поле тоже разовые
			},
		},
		WEEKLY = {
			{ id = "w1", text = "Catch 50 animals", kind = "catch", goal = 50, xp = 240 },
			{ id = "w2", text = "Catch 6 animals of rarity 2+", kind = "rarity", arg = 2, goal = 6, xp = 240 },
			{ id = "w3", text = "Make 12 throws at x5 or more", kind = "tier", arg = 5, goal = 12, xp = 240 },
			{ id = "w4", text = "Complete 100 dumbbell reps", kind = "train", goal = 100, xp = 240 },
			{ id = "w5", text = "Wrap 18 catches", kind = "wrap", goal = 18, xp = 240 },
		},
		REWARDS = {
			[1] = R({ C(0.25) }, { E("egg_forest") }),
			[2] = R({ S(10) }, { P("luck", 900) }), -- V74: в премиум-ряду нет обычных монет и Силы: зелья, осколки питомцев, метки, ауры, яйца, бусты
			[3] = R({ C(0.5) }, { B("fortune20") }),
			[4] = R({ E("egg_forest") }, { H(15) }),
			[5] = R({ C(0.75) }, { E("egg_amber") }),
			[6] = R({ S(15) }, { P("coins", 900) }),
			[7] = R({ C(0.5) }, { T("Pine Scout", Color3.fromRGB(110, 220, 140)) }),
			[8] = R({ T("Trail Scout", Color3.fromRGB(120, 210, 120)) }, { B("fair30") }),
			[9] = R({ S(20) }, { P("range", 1200) }),
			[10] = R({ E("egg_forest") }, { E("egg_tide") }),
			[11] = R({ C(0.75) }, { H(25) }),
			[12] = R({ S(25) }, { P("tension", 1200) }),
			[13] = R({ C(0.75) }, { T("Fern Tracker", Color3.fromRGB(90, 230, 150)) }),
			[14] = R({ S(30) }, { B("jackpot20") }),
			[15] = R({ B("fair30") }, { B("jackpot20") }),
			[16] = R({ C(1) }, { P("luck", 1800) }),
			[17] = R({ S(35) }, { H(40) }),
			[18] = R({ E("egg_forest") }, { E("egg_forest") }),
			[19] = R({ C(1) }, { P("coins", 1800) }),
			[20] = R({ T("Campfire", Color3.fromRGB(255, 160, 70)) }, { B("fortune20") }),
			[21] = R({ S(40) }, { A("Fern Glow", Color3.fromRGB(120, 255, 150)) }),
			[22] = R({ C(1) }, { E("egg_forest") }),
			[23] = R({ S(45) }, { A("Ember Trail", Color3.fromRGB(255, 110, 40)) }),
			[24] = R({ C(1) }, { H(60) }),
			[25] = R({ E("egg_amber") }, { E("egg_amber") }),
			[26] = R({ S(50) }, { P("range", 1800), P("tension", 1800) }),
			[27] = R({ C(1.25) }, { T("Elk Rider", Color3.fromRGB(255, 200, 90)) }),
			[28] = R({ S(55) }, { B("fair30") }),
			[29] = R({ C(1.5) }, { H(100) }),
			[30] = R({ T("Pinewatch Ranger", Color3.fromRGB(120, 200, 255)) }, { E("egg_storm"), A("Pinewatch Aurora", Color3.fromRGB(110, 255, 210)) }),
		},
	}
end

local PASS_MISSION_BY_ID: { [string]: any } = {}
for _, set in Config.PASS.DAILY do
	for _, m in set do
		PASS_MISSION_BY_ID[m.id] = m
	end
end
for _, m in Config.PASS.WEEKLY do
	PASS_MISSION_BY_ID[m.id] = m
end

function Config.passMission(id: string): any
	return PASS_MISSION_BY_ID[id]
end

-- Номер сезона n (>= 0), начало и конец (unix). До START считается сезон 0.
function Config.passSeason(now: number?): (number, number, number)
	local P = Config.PASS
	local t = tonumber(now) or Config.marketNow()
	if t ~= t then
		t = P.START
	end
	local len = P.DAYS * 86400
	local n = math.max(0, math.floor((t - P.START) / len))
	local s = P.START + n * len
	return n, s, s + len
end

function Config.passDay(now: number?): number
	local t = tonumber(now) or Config.marketNow()
	if t ~= t then
		t = Config.PASS.START
	end
	local _, s = Config.passSeason(t)
	return math.clamp(math.floor((t - s) / 86400), 0, Config.PASS.DAYS - 1)
end

function Config.passWeek(now: number?): number
	return math.clamp(math.floor(Config.passDay(now) / 7), 0, 3)
end

function Config.passTier(xp: number): number
	local v = tonumber(xp) or 0
	if v ~= v then
		return 0
	end
	return math.clamp(math.floor(v / Config.PASS.XP_PER_TIER), 0, Config.PASS.TIERS)
end

function Config.passDaily(now: number?): { any }
	return Config.PASS.DAILY[(Config.passDay(now) % 4) + 1]
end

function Config.passWeekly(): { any }
	return Config.PASS.WEEKLY
end

-- Сторона ряда наград: coins/power считает клиент, остальное сервер.
function Config.passSide(r: { any }): string
	for _, it in r do
		if it.type ~= "coins" and it.type ~= "power" and it.type ~= "potion" then
			return "server"
		end
	end
	return "client"
end

-- Монеты в паке: доля k от цены копья, следующего за самым дорогим купленным.
-- Так пак стоит одинаково много на любом этапе игры.
function Config.shopCoins(d: any, k: number): number
	local hi = 1
	for i, s in Config.SPEARS do
		if d and d.spears and d.spears[s.id] ~= nil then
			hi = i
		end
	end
	local nxt = Config.SPEARS[hi + 1]
	local ref = nxt and nxt.price or Config.SPEARS[#Config.SPEARS].price * 1.38
	ref = math.max(Config.SHOP.COIN_REF_MIN, ref)
	local n = math.max(1, ref * math.max(k, 0))
	local p = 10 ^ (math.floor(math.log10(n)) - 1)
	return math.floor(n / p + 0.5) * p
end

---------------------------------------------------------------------
-- V25: рынок.
-- Спрос - чистая функция серверного времени и номера вида: у всех игроков одинаковый,
-- сервер для этого не нужен. Насыщение (много одного вида подряд) хранится у игрока в d.market.
-- Средний множитель для того, кто просто продаёт всё, около 1: рынок награждает умение, а не наказывает.
---------------------------------------------------------------------
Config.MARKET = {
	HOUR = 3600,
	NOISE = 0.24, -- разброс спроса (ln-пространство)
	HOT_RARITY = 1.3, -- "горячая" редкость часа
	COLD_RARITY = 0.85,
	HOT_HABITAT = 1.2, -- наземные / летающие / водные
	CRAZE = 1.8, -- ажиотаж на вид (3 часа)
	GLUT = 0.6, -- затоваривание вида (3 часа)
	BLOCK_HOURS = 3,
	NORM = 0.92, -- приводит средний спрос к ~1.0 (события дают в среднем +10%)
	MIN = 0.5,
	MAX = 2.2,
	BROKER_FLOOR = 0.9, -- Silver Broker: спрос в плохие часы не ниже
	SAT = { per = 0.97, floor = 0.5, recover = 20 }, -- каждая продажа вида: x0.97; одна "единица" проходит за 20 с
	SAT_BROKER = { per = 0.99, floor = 0.8, recover = 8 },
}

-- Бонус к потолкам редкости от удачи копья. Без него удача выше ~160 ни на что не влияла:
-- все потолки RARITY_CHANCE_CAPS упирались уже на копье №6.
function Config.capLuckMul(luck: number): number
	return math.clamp(1 + 0.25 * math.log10(math.max(luck or 0, 100) / 100), 1, 2.5)
end

-- Доход за бросок у лучшей зоны для копья по номеру (расчёт V25, бросок x10, без рынка).
Config.EV_BY_SPEAR = { 13.4, 18, 62.6, 64.4, 182, 345, 1570, 1640, 5260, 5650, 8510, 17400, 17800, 34800, 34900, 65700, 66000, 124000, 125000, 234000, 235000, 439000, 441000, 826000, 829000, 1550000, 1560000, 2910000, 2920000, 5460000, 5480000, 10200000, 10300000, 19200000, 19200000, 35900000, 36000000, 67200000, 67400000, 126000000, 234000000, 436000000, 813000000, 1510000000, 2820000000, 3800000000 }

local function hash01(a: number, b: number): number
	local x = (a * 374761 + b * 668265) % 4294967296
	x = bit32.bxor(x, bit32.rshift(x, 13))
	x = (x * 1664525 + 1013904223) % 4294967296
	x = bit32.bxor(x, bit32.rshift(x, 16))
	x = (x * 69069 + 1) % 4294967296
	return (x % 1000003) / 1000003
end

function Config.marketNow(): number
	local ok, t = pcall(function()
		return workspace:GetServerTimeNow()
	end)
	return (ok and type(t) == "number") and t or os.time()
end

local eventCache: { [number]: any } = {}
local HABITATS = { "ground", "air", "water" }

-- События часа: горячая и холодная редкость, горячая среда обитания, ажиотаж и затоваривание вида.
function Config.marketEventsAtHour(h: number): any
	local c = eventCache[h]
	if c then
		return c
	end
	local nR = #Config.RARITIES
	local hot = 1 + math.floor(hash01(h, 11) * nR)
	local cold = ((hot - 1 + 1 + math.floor(hash01(h, 12) * (nR - 1))) % nR) + 1
	local block = math.floor(h / Config.MARKET.BLOCK_HOURS)
	local nS = #Config.SPECIES
	local ci = 1 + math.floor(hash01(block, 21) * nS)
	local gi = 1 + math.floor(hash01(block, 22) * nS)
	if gi == ci then
		gi = gi % nS + 1
	end
	local ev = {
		hotRarity = hot,
		coldRarity = cold,
		hotHabitat = HABITATS[1 + math.floor(hash01(h, 13) * #HABITATS)],
		craze = Config.SPECIES[ci],
		glut = Config.SPECIES[gi],
	}
	eventCache[h] = ev
	return ev
end

function Config.marketEvents(now: number): any
	return Config.marketEventsAtHour(math.floor(now / Config.MARKET.HOUR))
end

local function demandAtHour(sp: any, h: number): number
	local M = Config.MARKET
	local idx = sp.index or 1
	local r = hash01(idx, h) + hash01(idx + 7919, h * 3 + 1) - 1 -- [-1, 1], ближе к 0
	local d = math.exp(M.NOISE * r * 1.8) * M.NORM
	local ev = Config.marketEventsAtHour(h)
	if sp.rarity == ev.hotRarity then
		d *= M.HOT_RARITY
	elseif sp.rarity == ev.coldRarity then
		d *= M.COLD_RARITY
	end
	local kind = sp.spawnKind
	if kind == "shore_and_water" or kind == "shallow_water_ground" then
		kind = "water"
	end
	if kind == ev.hotHabitat then
		d *= M.HOT_HABITAT
	end
	if ev.craze and sp.id == ev.craze.id then
		d *= M.CRAZE
	end
	if ev.glut and sp.id == ev.glut.id then
		d *= M.GLUT
	end
	return math.clamp(d, M.MIN, M.MAX)
end

-- Спрос на вид в момент now (плавный переход между часами).
function Config.marketDemand(sp: any, now: number): number
	local H = Config.MARKET.HOUR
	local h = math.floor(now / H)
	local f = now / H - h
	local s = f * f * (3 - 2 * f)
	local a = demandAtHour(sp, h)
	local b = demandAtHour(sp, h + 1)
	return a + (b - a) * s
end

-- Прогноз спроса на n часов вперёд (пасс Market Insight).
function Config.marketForecast(sp: any, now: number, n: number): { number }
	local out = {}
	for k = 0, n do
		table.insert(out, Config.marketDemand(sp, now + k * Config.MARKET.HOUR))
	end
	return out
end

-- Насыщение: сколько "единиц" этого вида игрок продал недавно.
function Config.marketSaturation(rec: any, now: number, S: any): number
	if type(rec) ~= "table" or type(rec.n) ~= "number" or type(rec.t) ~= "number" then
		return 0
	end
	return math.max(0, rec.n - math.max(0, now - rec.t) / S.recover)
end

-- Котировка продажи. items - предметы к продаже (без изменения состояния).
-- flags: broker (мягкое насыщение), fair (ярмарка: спрос не ниже 1, без насыщения).
-- Возвращает сумму (без бустов монет), количество, строки по предметам, новые счётчики насыщения.
function Config.marketQuote(items: { any }, d: any, now: number, flags: any?): (number, number, { [number]: any }, { [string]: number })
	flags = flags or {}
	local M = Config.MARKET
	local S = flags.broker and M.SAT_BROKER or M.SAT
	if flags.recover and flags.recover ~= 1 then
		S = { per = S.per, floor = S.floor, recover = S.recover / flags.recover } -- ранг поддержки: цена восстанавливается быстрее
	end
	local sold = d and d.market and d.market.sold or {}
	local order = table.clone(items)
	table.sort(order, function(a, b)
		local av = a.price * (a.wrapped and Config.WRAP_MULT or 1)
		local bv = b.price * (b.wrapped and Config.WRAP_MULT or 1)
		if av ~= bv then
			return av > bv
		end
		return a.id < b.id
	end)
	local counts: { [string]: number } = {}
	local rows: { [number]: any } = {}
	local total = 0
	for _, it in order do
		local sp = Config.SPECIES_BY_ID[it.sp]
		local base = it.price * (it.wrapped and Config.WRAP_MULT or 1)
		local dem = sp and Config.marketDemand(sp, now) or 1
		local n = counts[it.sp]
		if n == nil then
			n = Config.marketSaturation(sold[it.sp], now, S)
		end
		local sat = 1
		if flags.fair then
			dem = math.max(1, dem)
		else
			if flags.broker then
				dem = math.max(M.BROKER_FLOOR, dem)
			end
			sat = math.max(S.floor, S.per ^ n)
			counts[it.sp] = n + 1
		end
		local v = base * dem * sat
		rows[it.id] = { dem = dem, sat = sat, value = v }
		total += v
	end
	return math.floor(total), #order, rows, counts
end

---------------------------------------------------------------------
-- V28: ЭКЗОТИКА и ЯЙЦА (только за Robux).
-- Экзотические животные лежат в Config.EXOTICS, а НЕ в Config.SPECIES: поэтому они не попадают ни в Roll,
-- ни в Population, ни в Ambient, ни в Showroom, ни в коллекцию (все они читают Config.SPECIES).
-- Модель берётся у обычного вида base (Fauna150) и перекрашивается/увеличивается по style и scale.
-- fx - бонусы (доля, например 0.06 = +6%; bag - слоты). Минус - компромисс. Всё правится здесь.
---------------------------------------------------------------------
Config.EXOTIC = {
	EQUIP_MAX = 3, -- сколько можно надеть одновременно
	MAX_LEVEL = 5,
	LEVEL_BONUS = 0.10, -- +10% к бонусам вида за уровень
	-- Потолок по характеристике на СУММУ ВСЕХ надетых экзотик (с уровнями). Пассы и бусты складываются с итогом СВЕРХУ
	-- (Perks.luckMult и др.), то есть экзотика может дать не больше CAP независимо от них. Минус не ниже FLOOR (bag: FLOOR_BAG слотов).
	CAP = { luck = 1.0, caps = 0.6, coins = 0.6, xp = 1.0, range = 0.3, grip = 0.3, bag = 40, train = 1.0, forge = 0.4 },
	FLOOR = -0.4,
	FLOOR_BAG = -40,
	STATS = { luck = "Luck", caps = "Rare chance", coins = "Sale coins", xp = "XP", range = "Throw range", grip = "Steady grip", bag = "Bag slots", train = "Training power", forge = "Forge discount" },
	RARITIES = {
		-- V34: 7 ступеней как у питомцев из пака (цвета из прототипа Claude Design)
		{ id = "common", name = "Common", color = Color3.fromRGB(195, 202, 214) },
		{ id = "uncommon", name = "Uncommon", color = Color3.fromRGB(134, 223, 114) },
		{ id = "rare", name = "Rare", color = Color3.fromRGB(108, 188, 255) },
		{ id = "epic", name = "Epic", color = Color3.fromRGB(204, 152, 255) },
		{ id = "legendary", name = "Legendary", color = Color3.fromRGB(255, 198, 80) },
		{ id = "mythic", name = "Mythic", color = Color3.fromRGB(255, 141, 156) },
		{ id = "divine", name = "Divine", color = Color3.fromRGB(255, 240, 168) },
	},
	SHARDS = { 5, 8, 14, 30, 80, 200, 500 }, -- осколки за повтор, по редкости
	UPGRADE = { 10, 16, 28, 60, 160, 400, 1000 }, -- цена уровня N = UPGRADE[редкость] * N осколков
}
Config.EXOTICS = {
	{ id = "candy_hopper", name = "Candy Hopper", base = "rabbit", rarity = 1, scale = 1.5, style = "rainbow", desc = "A bunny made of sprinkles. Hops out of nowhere.", fx = { luck = 0.06 } },
	{ id = "neon_fox", name = "Neon Fox", base = "fox", rarity = 1, scale = 1.4, style = "neon_pink", desc = "Glows brighter when coins are near.", fx = { coins = 0.08 } },
	{ id = "bubble_boar", name = "Bubble Boar", base = "boar", rarity = 1, scale = 1.5, style = "neon_cyan", desc = "Squeaks in bubbles. Learns fast.", fx = { xp = 0.10 } },
	{ id = "glow_wolf", name = "Glowstripe Wolf", base = "wolf", rarity = 2, scale = 1.4, style = "neon_green", desc = "Runs so fast it leaves light behind.", fx = { range = 0.12, coins = -0.06 } },
	{ id = "frost_bear", name = "Frostfur Bear", base = "bear", rarity = 2, scale = 1.5, style = "ice", desc = "Carries a whole glacier in its fur.", fx = { bag = 20, luck = -0.05 } },
	{ id = "ruby_stag", name = "Ruby Antlerlord", base = "megadeer", rarity = 2, scale = 1.4, style = "neon_red", desc = "Antlers cut from living rubies.", fx = { caps = 0.10 } },
	{ id = "prism_otter", name = "Prism Otter", base = "otter", rarity = 2, scale = 1.6, style = "rainbow", desc = "Splashes rainbows. Loves a workout.", fx = { train = 0.15 } },
	{ id = "storm_kitsune", name = "Storm Kitsune", base = "comet_fox", rarity = 3, scale = 1.5, style = "galaxy", desc = "Nine tails of crackling starlight.", fx = { luck = 0.20, grip = -0.10 } },
	{ id = "magma_titan", name = "Magma Titan", base = "lava_golem", rarity = 3, scale = 1.35, style = "magma", desc = "A walking volcano that pays well and throws badly.", fx = { coins = 0.20, range = -0.10 } },
	{ id = "ghost_lynx", name = "Ghost Lynx", base = "lynx", rarity = 3, scale = 1.5, style = "ghost", desc = "You only see it when it wants you to.", fx = { caps = 0.14, xp = 0.10 } },
	{ id = "solar_lion", name = "Solar Maned Lion", base = "sunlion", rarity = 4, scale = 1.5, style = "gold_neon", desc = "A mane of pure noon sunlight.", fx = { luck = 0.30, grip = -0.12 } },
	{ id = "void_mammoth", name = "Void Mammoth", base = "mammoth", rarity = 4, scale = 1.6, style = "void", desc = "Eats light. Stores everything.", fx = { bag = 35, forge = 0.15, range = -0.08 } },
	{ id = "aurora_phoenix", name = "Aurora Phoenix", base = "phoenix", rarity = 4, scale = 1.5, style = "rainbow", desc = "Burns in every color at once.", fx = { caps = 0.20, xp = 0.20 } },
	{ id = "astral_wyrm", name = "Astral Wyrm", base = "astral_dragon", rarity = 5, scale = 1.7, style = "galaxy", desc = "A dragon that swallowed a galaxy.", fx = { luck = 0.45, caps = 0.25, coins = -0.15 } },
	{ id = "leviathan_prime", name = "Leviathan Prime", base = "abyss_leviathan", rarity = 5, scale = 1.5, style = "neon_cyan", desc = "The deep, but glowing.", fx = { range = 0.25, grip = 0.15, luck = -0.10 } },
	{ id = "prismatic_overlord", name = "Prismatic Overlord", base = "void_behemoth", rarity = 6, scale = 1.9, style = "rainbow_neon", desc = "The wildest creature in the game. Everything bends around it.", fx = { luck = 0.55, caps = 0.30, coins = 0.25, xp = 0.25, range = 0.15, bag = -20 } },
}
-- V34: питомцы из пака блочных моделей (ReplicatedStorage/PetModels/<id>). Редкость 1..7: Common, Uncommon, Rare, Epic, Legendary, Mythic, Divine.
-- Старые 16 в яйцах больше не выпадают, но остаются у тех, у кого уже есть (legacy = true); их шкала пересчитана по OLD_RARITY.
local OLD_RARITY = { 1, 3, 4, 5, 6, 7 }
for _, ex in Config.EXOTICS do
	ex.rarity = OLD_RARITY[ex.rarity]
	ex.legacy = true
end
-- { id, имя, семейство (яйцо), редкость, бонусы, описание }. Минус = компромисс.
local NEW_PETS: { { any } } = {
	{ "clover_beetle", "Clover Beetle", "forest", 1, { luck = 0.06 }, "Finds four-leaf clovers without even looking." },
	{ "moss_bunny", "Mossy Bunny", "forest", 1, { xp = 0.10 }, "Hops on mossy rocks and learns from every jump." },
	{ "hazelnut_squirrel", "Hazelnut Squirrel", "forest", 2, { bag = 12 }, "Hides spare nuts and spare animals in its fluffy tail." },
	{ "flower_hedgehog", "Flower Hedgehog", "forest", 3, { caps = 0.12, range = -0.05 }, "Sniffs out rare animals. Slow to curl up for a throw." },
	{ "guardian_fawn", "Guardian Fawn", "forest", 4, { luck = 0.18, xp = 0.08, range = -0.08 }, "The forest sends it to watch over lucky hunters." },
	{ "sand_jerboa", "Sand Jerboa", "amber", 2, { range = 0.10 }, "Jumps three dunes at a time." },
	{ "amber_armadillo", "Amber Armadillo", "amber", 2, { grip = 0.12 }, "Its amber shell never rattles. Neither do your hands." },
	{ "sun_lion_cub", "Sun Lion Cub", "amber", 3, { coins = 0.14, luck = -0.05 }, "Shines on every sale. Naps through the lucky moments." },
	{ "honey_griffin", "Honey Griffin", "amber", 4, { coins = 0.16, xp = 0.10, grip = -0.08 }, "Sweet deals, sticky wings." },
	{ "amber_basilisk", "Amber Basilisk", "amber", 5, { caps = 0.25, coins = 0.15, range = -0.10 }, "One glance from it turns a rare find into gold." },
	{ "bubble_crab", "Bubble Crab", "tide", 3, { train = 0.15, luck = -0.05 }, "Pops bubbles to a training rhythm." },
	{ "coral_turtle", "Coral Turtle", "tide", 3, { bag = 20, range = -0.06 }, "Carries a whole reef on its back. Heavy, but roomy." },
	{ "pearl_axolotl", "Pearl Axolotl", "tide", 4, { luck = 0.18, caps = 0.10, coins = -0.10 }, "Collects pearls instead of coins." },
	{ "tide_ray", "Tide Ray", "tide", 5, { range = 0.22, xp = 0.15, grip = -0.12 }, "Rides the current farther than any spear flies." },
	{ "little_leviathan", "Little Leviathan", "tide", 6, { range = 0.28, grip = 0.15, luck = -0.10 }, "Small for a leviathan. Big for everything else." },
	{ "spark_salamander", "Spark Salamander", "storm", 4, { train = 0.20, grip = -0.10 }, "Every workout leaves it crackling." },
	{ "cloud_lamb", "Cloud Lamb", "storm", 4, { bag = 25, forge = 0.10, range = -0.08 }, "Soft as a cloud, stores as much as one." },
	{ "storm_falcon", "Storm Falcon", "storm", 5, { range = 0.20, grip = 0.10, coins = -0.12 }, "Dives straight through the thunder." },
	{ "storm_dragon", "Storm Dragonling", "storm", 6, { luck = 0.40, range = 0.15, coins = -0.15 }, "Calls lightning to land where it likes." },
	{ "heavenly_kitsune", "Heavenly Kitsune", "storm", 7, { luck = 0.55, caps = 0.30, xp = 0.25, grip = -0.15 }, "A sky spirit. Fortune follows wherever it walks." },
	{ "comet_kitten", "Comet Kitten", "astral", 5, { luck = 0.28, grip = -0.12 }, "Leaves a trail of stardust and happy accidents." },
	{ "moon_owlet", "Moon Owlet", "astral", 5, { caps = 0.18, train = 0.20, coins = -0.10 }, "Studies at night, spots rare animals by day." },
	{ "nebula_moth", "Nebula Moth", "astral", 6, { luck = 0.40, caps = 0.22, coins = -0.15 }, "Wings full of unborn stars." },
	{ "eclipse_dragon", "Eclipse Dragonling", "astral", 6, { coins = 0.35, xp = 0.20, range = -0.15 }, "Swallows the sun and pays in gold." },
	{ "astral_phoenix", "Astral Phoenix", "astral", 7, { coins = 0.45, caps = 0.25, xp = 0.20, range = 0.10, bag = -20 }, "Reborn every night. Everything bends toward its light." },
}
for _, p in NEW_PETS do
	table.insert(Config.EXOTICS, { id = p[1], name = p[2], family = p[3], rarity = p[4], fx = p[5], desc = p[6], model = p[1] })
end
Config.EXOTIC_BY_ID = {} :: { [string]: any }
for i, ex in Config.EXOTICS do
	ex.index = i
	Config.EXOTIC_BY_ID[ex.id] = ex
end

-- Яйца. weights - ОДНА таблица и для сервера (бросок), и для интерфейса (Config.eggOdds). Шансы = вес / сумма весов.
-- ВАЖНО: изменение весов автоматически меняет и бросок, и проценты в окне яйца: ничего дублировать не нужно.
-- Правила Roblox для платных случайных предметов требуют показывать шансы до покупки: окно яйца это делает.
-- V34: 5 яиц из пака (веса = проценты из прототипа, сумма каждого = 100). model = модель яйца в ReplicatedStorage/PetModels.
Config.EGGS = {
	egg_forest = { name = "Forest Talisman Egg", family = "forest", model = "forest_talisman_egg", color = Color3.fromRGB(111, 208, 74), weights = { { "clover_beetle", 40 }, { "moss_bunny", 28 }, { "hazelnut_squirrel", 20 }, { "flower_hedgehog", 10 }, { "guardian_fawn", 2 } } },
	egg_amber = { name = "Amber Heart Egg", family = "amber", model = "amber_heart_egg", color = Color3.fromRGB(255, 176, 46), weights = { { "sand_jerboa", 35 }, { "amber_armadillo", 30 }, { "sun_lion_cub", 22 }, { "honey_griffin", 11 }, { "amber_basilisk", 2 } } },
	egg_tide = { name = "Tide Pearl Egg", family = "tide", model = "tide_pearl_egg", color = Color3.fromRGB(63, 214, 196), weights = { { "bubble_crab", 36 }, { "coral_turtle", 29 }, { "pearl_axolotl", 22 }, { "tide_ray", 11 }, { "little_leviathan", 2 } } },
	egg_storm = { name = "Storm Heart Egg", family = "storm", model = "storm_heart_egg", color = Color3.fromRGB(63, 169, 255), weights = { { "spark_salamander", 35 }, { "cloud_lamb", 30 }, { "storm_falcon", 23 }, { "storm_dragon", 10 }, { "heavenly_kitsune", 2 } } },
	egg_astral = { name = "Astral Core Egg", family = "astral", model = "astral_core_egg", color = Color3.fromRGB(169, 139, 255), weights = { { "comet_kitten", 35 }, { "moon_owlet", 30 }, { "nebula_moth", 18 }, { "eclipse_dragon", 12 }, { "astral_phoenix", 5 } } },
}

-- Шансы яйца в процентах (список в порядке weights). Из этой же таблицы бросает сервер.
function Config.eggOdds(key: string): { { id: string, pct: number } }
	local egg = Config.EGGS[key]
	local out = {}
	if not egg then
		return out
	end
	local total = 0
	for _, w in egg.weights do
		total += w[2]
	end
	for _, w in egg.weights do
		table.insert(out, { id = w[1], pct = w[2] / total * 100 })
	end
	return out
end

-- Бросок яйца (на сервере). rng: Random.
function Config.eggRoll(key: string, rng: Random): string?
	local egg = Config.EGGS[key]
	if not egg then
		return nil
	end
	local total = 0
	for _, w in egg.weights do
		total += w[2]
	end
	local draw = rng:NextNumber() * total
	local acc = 0
	for _, w in egg.weights do
		acc += w[2]
		if draw < acc then
			return w[1]
		end
	end
	return egg.weights[#egg.weights][1]
end

-- Сумма бонусов надетой экзотики по характеристикам (с уровнями и потолками). Считает и сервер, и клиент.
function Config.exoticTotals(owned: any, equipped: any, levels: any): { [string]: number }
	local E = Config.EXOTIC
	local total: { [string]: number } = {}
	local used = 0
	for _, id in equipped or {} do
		local ex = Config.EXOTIC_BY_ID[id]
		if ex and (owned and (tonumber(owned[id]) or 0) > 0) and used < E.EQUIP_MAX then
			used += 1
			local k = 1 + E.LEVEL_BONUS * math.clamp(tonumber(levels and levels[id]) or 0, 0, E.MAX_LEVEL)
			for stat, v in ex.fx do
				total[stat] = (total[stat] or 0) + v * k
			end
		end
	end
	for stat, v in total do
		local lo = stat == "bag" and E.FLOOR_BAG or E.FLOOR
		total[stat] = math.clamp(v, lo, E.CAP[stat] or 1)
	end
	return total
end

function Config.exoticUpgradeCost(ex: any, level: number): number
	return Config.EXOTIC.UPGRADE[ex.rarity] * (level + 1)
end

return Config
