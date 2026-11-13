-- ReplicatedStorage/Shared/Config.luau
-- v2: весь баланс, тексты и визуальные настройки. Меняй цифры здесь.
local Config = {}

Config.GAME_NAME = "Spear Hunt"
Config.VERSION = "3.4-no-trophy-heads"
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
	rate = 1.0, -- r: ×100 примерно за 4.6 с
	cap = 100, -- на капе бросок происходит сам
	tellTime = 0.42, -- за сколько секунд до срыва копьё начинает сильно дрожать
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
	rangeK = 8, -- дальность = rangeK·√Сила (в студах)
	maxRange = 12700,
	maxFlightTime = 6.5,
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
	{ id = "bone", price = 150, sharp = 2, heavy = 1, luck = 1.2, range = 1.05, alpha = 0.8, impact = "dust", zone = 1, tier = 2, name = "Bone Spear", desc = "Pierces tougher hides.", trail = { Color3.fromHex("#fffaeb"), Color3.fromHex("#c8bea0") } },
	{ id = "bronze", price = 1200, sharp = 2, heavy = 2, luck = 1.4, range = 1.1, alpha = 0.76, impact = "sparks", zone = 2, tier = 3, name = "Bronze Spear", desc = "Heavy and dependable.", trail = { Color3.fromHex("#ffbe6e"), Color3.fromHex("#cd7f32") } },
	{ id = "feather", price = 6000, sharp = 3, heavy = 2, luck = 1.7, range = 1.25, alpha = 0.72, impact = "feathers", zone = 2, tier = 4, name = "Feathered Spear", desc = "Flies farther than other early spears.", trail = { Color3.fromHex("#ff7878"), Color3.fromHex("#50a0ff") } },
	{ id = "iron", price = 25000, sharp = 3, heavy = 3, luck = 2, range = 1.3, alpha = 0.68, impact = "sparks", zone = 2, tier = 5, name = "Iron Spear", desc = "Built for bigger game.", trail = { Color3.fromHex("#dce2f0"), Color3.fromHex("#787c88") } },
	{ id = "obsidian", price = 120000, sharp = 4, heavy = 3, luck = 2.6, range = 1.38, alpha = 0.63, impact = "shards", zone = 3, tier = 6, name = "Obsidian Spear", desc = "Forged from black volcanic glass.", trail = { Color3.fromHex("#c86eff"), Color3.fromHex("#3c145a") } },
	{ id = "crystal", price = 600000, sharp = 5, heavy = 4, luck = 3.4, range = 1.45, alpha = 0.58, impact = "crystal", zone = 3, tier = 7, name = "Crystal Spear", desc = "Chimes as it flies.", trail = { Color3.fromHex("#8cffff"), Color3.fromHex("#ffc846") } },
	{ id = "fire", price = 2500000, sharp = 5, heavy = 4, luck = 4.5, range = 1.55, alpha = 0.54, impact = "fire", zone = 4, tier = 8, name = "Fire Spear", desc = "Leaves a blazing trail.", trail = { Color3.fromHex("#ffdc50"), Color3.fromHex("#ff4614") } },
	{ id = "ice", price = 10000000, sharp = 6, heavy = 5, luck = 6, range = 1.65, alpha = 0.5, impact = "ice", zone = 4, tier = 9, name = "Ice Spear", desc = "Freezes the air around it.", trail = { Color3.fromHex("#ebfaff"), Color3.fromHex("#78c8ff") } },
	{ id = "star", price = 50000000, sharp = 6, heavy = 5, luck = 9, range = 1.8, alpha = 0.45, impact = "stars", zone = 4, tier = 10, name = "Star Spear", desc = "Fell from the sky. Almost aims itself.", trail = { Color3.fromHex("#ffe678"), Color3.fromHex("#785aff") } },
	{ id = "amber_sting", price = 75000000, sharp = 7, heavy = 6, luck = 10.0, range = 1.9, alpha = 0.44, impact = "sparks", zone = 5, tier = 11, name = "Amber Sting", desc = "A honey-colored edge set in layered amber.", trail = { Color3.fromHex("#fff17b"), Color3.fromHex("#f5a817") } },
	{ id = "solar_trident", price = 103500000, sharp = 8, heavy = 6, luck = 11.2, range = 1.945, alpha = 0.434, impact = "fire", zone = 5, tier = 12, name = "Solar Trident", desc = "Three golden prongs catch the light of the savanna.", trail = { Color3.fromHex("#ff692d"), Color3.fromHex("#ffd029") } },
	{ id = "canyon_hook", price = 142830000, sharp = 8, heavy = 7, luck = 12.54, range = 1.99, alpha = 0.428, impact = "shards", zone = 6, tier = 13, name = "Canyon Hook", desc = "A hooked stone blade shaped for the red canyons.", trail = { Color3.fromHex("#73c6e8"), Color3.fromHex("#d77435") } },
	{ id = "condor_quill", price = 197110000, sharp = 9, heavy = 7, luck = 14.05, range = 2.035, alpha = 0.422, impact = "feathers", zone = 6, tier = 14, name = "Condor Quill", desc = "A broad feathered edge built to cut through rising air.", trail = { Color3.fromHex("#d78e36"), Color3.fromHex("#e4dfca") } },
	{ id = "mirage_lance", price = 272010000, sharp = 9, heavy = 8, luck = 15.74, range = 2.08, alpha = 0.416, impact = "crystal", zone = 7, tier = 15, name = "Mirage Lance", desc = "A pale desert lance with a shimmering point.", trail = { Color3.fromHex("#6ee1e9"), Color3.fromHex("#f1cf6c") } },
	{ id = "scorpion_sting", price = 375370000, sharp = 10, heavy = 8, luck = 17.62, range = 2.125, alpha = 0.41, impact = "shards", zone = 7, tier = 16, name = "Scorpion Sting", desc = "A hooked tip and layered grip inspired by desert armor.", trail = { Color3.fromHex("#9aff7e"), Color3.fromHex("#be8240") } },
	{ id = "emerald_vine", price = 518010000, sharp = 10, heavy = 9, luck = 19.74, range = 2.17, alpha = 0.404, impact = "crystal", zone = 8, tier = 17, name = "Emerald Vine", desc = "A green blade held by tightly wrapped jungle vines.", trail = { Color3.fromHex("#c2f757"), Color3.fromHex("#19bd67") } },
	{ id = "temple_guard", price = 714850000, sharp = 11, heavy = 9, luck = 22.11, range = 2.215, alpha = 0.398, impact = "sparks", zone = 8, tier = 18, name = "Temple Guard", desc = "A carved guardian spear from the overgrown temple.", trail = { Color3.fromHex("#ffd24d"), Color3.fromHex("#1b8e78") } },
	{ id = "mangrove_root", price = 986490000, sharp = 11, heavy = 10, luck = 24.76, range = 2.26, alpha = 0.392, impact = "dust", zone = 9, tier = 19, name = "Mangrove Root", desc = "A twisted root shaft fitted with a broad hunting edge.", trail = { Color3.fromHex("#a7e96a"), Color3.fromHex("#5b8c3e") } },
	{ id = "hydra_fangs", price = 1361360000, sharp = 12, heavy = 10, luck = 27.73, range = 2.305, alpha = 0.386, impact = "shards", zone = 9, tier = 20, name = "Hydra Fangs", desc = "Twin fang-shaped blades rise from a reinforced socket.", trail = { Color3.fromHex("#9eff78"), Color3.fromHex("#358957") } },
	{ id = "storm_trident", price = 1878680000, sharp = 12, heavy = 11, luck = 31.06, range = 2.35, alpha = 0.38, impact = "sparks", zone = 10, tier = 21, name = "Storm Trident", desc = "A forked point that gathers the colors of a storm.", trail = { Color3.fromHex("#fff16c"), Color3.fromHex("#83a9e6") } },
	{ id = "thunder_split", price = 2592570000, sharp = 13, heavy = 11, luck = 34.79, range = 2.395, alpha = 0.374, impact = "sparks", zone = 10, tier = 22, name = "Thunder Splitter", desc = "An open lightning-shaped blade built for the high ridges.", trail = { Color3.fromHex("#f7ee56"), Color3.fromHex("#5e88cb") } },
	{ id = "coral_branch", price = 3577750000, sharp = 13, heavy = 12, luck = 38.96, range = 2.44, alpha = 0.368, impact = "crystal", zone = 11, tier = 23, name = "Coral Branch", desc = "A branching coral point with a sturdy wrapped grip.", trail = { Color3.fromHex("#8cf5ee"), Color3.fromHex("#f17c8a") } },
	{ id = "tide_crest", price = 4937300000, sharp = 14, heavy = 12, luck = 43.63, range = 2.485, alpha = 0.362, impact = "ice", zone = 11, tier = 24, name = "Tide Crest", desc = "A sweeping edge shaped like a breaking wave.", trail = { Color3.fromHex("#b6ffff"), Color3.fromHex("#25c2dd") } },
	{ id = "abyss_anchor", price = 6813470000, sharp = 14, heavy = 13, luck = 48.87, range = 2.53, alpha = 0.356, impact = "shards", zone = 12, tier = 25, name = "Abyssal Anchor", desc = "A heavy anchor blade recovered from the deep.", trail = { Color3.fromHex("#64f2e8"), Color3.fromHex("#315c87") } },
	{ id = "leviathan_fang", price = 9402590000, sharp = 15, heavy = 13, luck = 54.74, range = 2.575, alpha = 0.35, impact = "ice", zone = 12, tier = 26, name = "Leviathan Fang", desc = "A great sea fang secured inside a reinforced frame.", trail = { Color3.fromHex("#78dce9"), Color3.fromHex("#283c66") } },
	{ id = "ash_saw", price = 12975580000, sharp = 15, heavy = 14, luck = 61.3, range = 2.62, alpha = 0.344, impact = "shards", zone = 13, tier = 27, name = "Ash Saw", desc = "A dark serrated blade forged for the volcanic plateau.", trail = { Color3.fromHex("#f0a460"), Color3.fromHex("#5d5a67") } },
	{ id = "golem_heart", price = 17906290000, sharp = 16, heavy = 14, luck = 68.66, range = 2.665, alpha = 0.338, impact = "sparks", zone = 13, tier = 28, name = "Golem Heart", desc = "A warm stone core powers its layered metal point.", trail = { Color3.fromHex("#ffbb3c"), Color3.fromHex("#566270") } },
	{ id = "magma_tongue", price = 24710690000, sharp = 16, heavy = 15, luck = 76.9, range = 2.71, alpha = 0.332, impact = "fire", zone = 14, tier = 29, name = "Magma Tongue", desc = "A bright molten edge held within a black stone frame.", trail = { Color3.fromHex("#ffd439"), Color3.fromHex("#f25b22") } },
	{ id = "phoenix_wing", price = 34100750000, sharp = 17, heavy = 15, luck = 86.13, range = 2.755, alpha = 0.326, impact = "fire", zone = 14, tier = 30, name = "Phoenix Wing", desc = "A fiery wing-shaped blade with a feathered grip.", trail = { Color3.fromHex("#ffdf66"), Color3.fromHex("#f57b20") } },
	{ id = "amethyst_geode", price = 47059030000, sharp = 17, heavy = 16, luck = 96.46, range = 2.8, alpha = 0.32, impact = "crystal", zone = 15, tier = 31, name = "Amethyst Geode", desc = "A hollow crystal crown opens around an amethyst core.", trail = { Color3.fromHex("#e9a2ff"), Color3.fromHex("#9637d8") } },
	{ id = "quartz_needle", price = 64941460000, sharp = 18, heavy = 16, luck = 108.04, range = 2.845, alpha = 0.314, impact = "crystal", zone = 15, tier = 32, name = "Quartz Needle", desc = "A long clear point mounted in a delicate crystal socket.", trail = { Color3.fromHex("#d7ffff"), Color3.fromHex("#9e74d6") } },
	{ id = "lunar_crescent", price = 89619220000, sharp = 18, heavy = 17, luck = 121.0, range = 2.89, alpha = 0.308, impact = "ice", zone = 16, tier = 33, name = "Lunar Crescent", desc = "A silver moon-shaped edge for the frozen plains.", trail = { Color3.fromHex("#ebfaff"), Color3.fromHex("#b5c7ef") } },
	{ id = "aurora_weave", price = 123674520000, sharp = 19, heavy = 17, luck = 135.52, range = 2.935, alpha = 0.302, impact = "ice", zone = 16, tier = 34, name = "Aurora Weave", desc = "Colored bands wrap around its luminous northern blade.", trail = { Color3.fromHex("#bc90ff"), Color3.fromHex("#72e4c2") } },
	{ id = "cloud_feather", price = 170670840000, sharp = 19, heavy = 18, luck = 151.79, range = 2.98, alpha = 0.296, impact = "feathers", zone = 17, tier = 35, name = "Cloud Feather", desc = "A light feathered point built for the floating islands.", trail = { Color3.fromHex("#effbff"), Color3.fromHex("#91d6ec") } },
	{ id = "sky_harpoon", price = 235525770000, sharp = 20, heavy = 18, luck = 170.0, range = 3.025, alpha = 0.29, impact = "feathers", zone = 17, tier = 36, name = "Sky Harpoon", desc = "A long hooked harpoon made to reach across the clouds.", trail = { Color3.fromHex("#f7e696"), Color3.fromHex("#65b6d7") } },
	{ id = "rift_shards", price = 325025560000, sharp = 20, heavy = 19, luck = 190.4, range = 3.07, alpha = 0.284, impact = "shards", zone = 18, tier = 37, name = "Rift Shards", desc = "A floating cluster of dark fragments surrounds its point.", trail = { Color3.fromHex("#dc9bff"), Color3.fromHex("#7139b8") } },
	{ id = "void_scissors", price = 448535270000, sharp = 21, heavy = 19, luck = 213.25, range = 3.115, alpha = 0.278, impact = "crystal", zone = 18, tier = 38, name = "Void Shears", desc = "Two open blades frame the darkness between them.", trail = { Color3.fromHex("#b278ff"), Color3.fromHex("#3b285d") } },
	{ id = "astral_armillary", price = 618978670000, sharp = 21, heavy = 20, luck = 238.84, range = 3.16, alpha = 0.272, impact = "stars", zone = 19, tier = 39, name = "Astral Armillary", desc = "Orbital rings hold a golden point at their center.", trail = { Color3.fromHex("#ffe48b"), Color3.fromHex("#6863df") } },
	{ id = "singularity_spire", price = 854190560000, sharp = 22, heavy = 20, luck = 267.5, range = 3.205, alpha = 0.266, impact = "stars", zone = 19, tier = 40, name = "Singularity Spire", desc = "A stepped black spire held within an open event-horizon frame.", trail = { Color3.fromHex("#f5db77"), Color3.fromHex("#7864e5") } },
}
-- Кузница: улучшение купленного копья (уровни 0..5)
Config.FORGE = {
	maxLevel = 5,
	luckPer = 0.12, -- +12% удачи за уровень
	rangePer = 0.04, -- +4% дальности за уровень
	alphaPer = 0.012, -- копьё «держит» натяжение дольше
	costMul = 0.3, -- цена уровня = max(40, price·costMul)·(lvl+1)^1.7
}

-- Гантели: прирост Силы за подъём
Config.DUMBBELL = {
	{ cost = 0, gain = 1, name = "Wooden" },
	{ cost = 40, gain = 2, name = "Stone" },
	{ cost = 250, gain = 4, name = "Bronze" },
	{ cost = 1500, gain = 8, name = "Iron" },
	{ cost = 8000, gain = 15, name = "Granite" },
	{ cost = 40000, gain = 30, name = "Golden" },
	{ cost = 150000, gain = 60, name = "Mammoth" },
}
Config.DUMBBELL_LOOK = {
	{ color = Color3.fromRGB(150, 98, 56), material = Enum.Material.Plastic, size = 0.9 },
	{ color = Color3.fromRGB(128, 128, 132), material = Enum.Material.Plastic, size = 1.0 },
	{ color = Color3.fromRGB(205, 127, 50), material = Enum.Material.Plastic, size = 1.1 },
	{ color = Color3.fromRGB(90, 94, 104), material = Enum.Material.Plastic, size = 1.2 },
	{ color = Color3.fromRGB(176, 160, 150), material = Enum.Material.Plastic, size = 1.3 },
	{ color = Color3.fromRGB(255, 196, 48), material = Enum.Material.Plastic, size = 1.4 },
	{ color = Color3.fromRGB(240, 232, 214), material = Enum.Material.Plastic, size = 1.55 },
}
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
	{ boost = "luck", dur = 300, cost = 120 },
	{ boost = "coins", dur = 300, cost = 200 },
	{ boost = "range", dur = 300, cost = 150 },
	{ boost = "tension", dur = 240, cost = 260 },
}

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
	{ id = "q7", npc = "herbalist", title = "Acrobat", text = "Complete the obstacle course", kind = "course", goal = 1, reward = { coins = 300, xp = 100 } },
	{ id = "q8", npc = "hunter", title = "Forest Champion", text = "Make a throw at ×25 or higher", kind = "tier", arg = 25, goal = 1, reward = { coins = 1500, boost = "tension", dur = 240 } },
	{ id = "q9", npc = "tracker", title = "Ancient Trails", text = "Catch an animal in the Ancient Forest", kind = "zone", arg = 4, goal = 1, reward = { coins = 5000, xp = 400 } },
	{ id = "q10", npc = "herbalist", title = "Egg Hunt", text = "Find 5 hidden eggs", kind = "collect", arg = "egg", goal = 5, reward = { coins = 2500, boost = "luck", dur = 600 } },
	{ id = "q11", npc = "hunter", title = "Trader", text = "Sell catches worth 1K coins", kind = "sell", goal = 1000, reward = { coins = 800, xp = 150 } },
	{ id = "q12", npc = "tracker", title = "Legend", text = "Make a throw at ×100", kind = "tier", arg = 100, goal = 1, reward = { coins = 20000, boost = "luck", dur = 900 } },
}

-- Реплики NPC (Dialog). Первая — приветствие, дальше — советы по кругу
Config.NPC = {
	hunter = { name = "Quest Board", color = Color3.fromRGB(110, 200, 90), lines = {
		"A new hunter! The shelter is at the forest edge. Step inside and hold to charge your throw.",
		"Hold longer for a bigger multiplier. If your grip slips, the spear still flies with 25% of your luck.",
		"When the spear starts shaking, release before your grip slips.",
		"Longer throws reach deeper zones, where bigger and rarer animals live.",
	} },
	herbalist = { name = "Herbalist", color = Color3.fromRGB(220, 120, 220), lines = {
		"My luck potions smell like chamomile and coins.",
		"Fireflies love the shade near the village. Collect some and I will reward you.",
		"There are eggs hidden around the village. Search the grass!",
	} },
	tracker = { name = "Tracker", color = Color3.fromRGB(240, 180, 80), lines = {
		"Every zone is a world of its own. Even the air is green in the Wild Marsh.",
		"A Spirit Deer was spotted among the Wild Marsh ruins...",
		"Something big and furry lives in the Ancient Forest. No idea what it is.",
		"Climb the lookout tower for a view of the whole map.",
	} },
	armorer = { name = "Armorer", color = Color3.fromRGB(120, 180, 255), lines = {
		"A better spear means new animals. That old stick will not catch a yeti.",
	} },
	merchant = { name = "Merchant", color = Color3.fromRGB(255, 200, 60), lines = {
		"Wrapped catches sell for twice as much!",
	} },
	smith = { name = "Blacksmith", color = Color3.fromRGB(255, 130, 60), lines = {
		"Bring me your spear and I will improve its luck and range.",
	} },
}

---------------------------------------------------------------------
-- Активности (заглушки наград — в демо выдаются сразу)
---------------------------------------------------------------------
Config.ACTIVITY = {
	range = { shots = 6, coinPerPoint = 1, xpPerPoint = 0.5 },
	course = { coins = 120, xp = 60, coinPerCoin = 5, parTime = 45 },
	firefly = { coins = 15, xp = 5 },
	egg = { coins = 250, xp = 50 },
	lookout = { coins = 25, xp = 10, once = true },
	campfire = { coinsPerMin = 2 },
}

-- Обучение: шаги подсказок (стрелка ведёт к цели)
Config.TUTORIAL = {
	{ text = "Go to the hunting shelter at the forest edge", target = "ambush" },
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

function Config.range(power: number): number
	return math.min(Config.THROW.maxRange, Config.THROW.rangeK * math.sqrt(math.max(power, 1)))
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

function Config.powerLuck(power: number): number
	return 1 + 0.5 * math.log10(math.max(power, 10) / 10)
end

function Config.flightTime(d: number): number
	local distance = math.max(0, d)
	local familiar = math.min(distance, 230)
	local travel = Config.THROW.flightBase + familiar * Config.THROW.flightPerStud
	if distance > 230 then travel += math.log(1 + (distance - 230) / 230) * 0.85 end
	return math.min(Config.THROW.maxFlightTime, travel)
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

Config.SHOP = {
	DATASTORE = "SpearHunt_v1",
	STARTER_MAX_LEVEL = 10,
	COIN_REF_MIN = 5000,
	PASSES = {
		{ key = "charm", id = 0, price = 399, name = "Lucky Charm", desc = "Luck x2 forever. Rare animal limits +50%." },
		{ key = "purse", id = 0, price = 299, name = "Golden Purse", desc = "Every sale pays +100% coins. Forever." },
		{ key = "wrap", id = 0, price = 249, name = "Master Wrapper", desc = "Tie one bow and your whole bag is wrapped." },
		{ key = "bag", id = 0, price = 179, name = "Big Game Bag", desc = "+60 bag slots. Sell from anywhere." },
		{ key = "titan", id = 0, price = 149, name = "Titan Training", desc = "Every dumbbell rep gives x2 Strength." },
		{ key = "vip", id = 0, price = 449, name = "VIP Hunter", desc = "Gold VIP tag. +20% coins and +25% XP." },
	},
	PRODUCTS = {
		{ key = "starter", id = 0, price = 79, kind = "starter", name = "Starter Pack" },
		{ key = "luck30", id = 0, price = 59, kind = "boost", boosts = { "luck" }, dur = 1800, name = "Luck Brew", desc = "Luck x2 and rare limits +25% for 30 min of play." },
		{ key = "coins30", id = 0, price = 49, kind = "boost", boosts = { "coins" }, dur = 1800, name = "Coin Brew", desc = "+100% coins from sales for 30 min of play." },
		{ key = "brew30", id = 0, price = 119, kind = "boost", boosts = { "luck", "coins", "range", "tension" }, dur = 1800, name = "Hunter's Brew", desc = "Luck, Coins, Range and Steady Grip for 30 min." },
		{ key = "server15", id = 0, price = 149, kind = "server", dur = 900, name = "Server Luck", desc = "Luck x2 for everyone on the server for 15 min." },
		{ key = "coins1", id = 0, price = 49, kind = "coins", k = 0.3, name = "Coin Pouch" },
		{ key = "coins2", id = 0, price = 99, kind = "coins", k = 0.8, name = "Coin Sack" },
		{ key = "coins3", id = 0, price = 199, kind = "coins", k = 2, name = "Coin Chest" },
		{ key = "coins4", id = 0, price = 399, kind = "coins", k = 5, name = "Hunter's Hoard", best = true },
	},
	STARTER = { spear = "bronze", coins = 2000, bagLvl = 2, boost = "luck", dur = 1800 },
	-- Бонусы одной характеристики складываются, а не перемножаются.
	PERK = {
		charmLuck = 1, charmCaps = 0.5,
		boostCaps = 0.25,
		serverLuck = 1, serverCaps = 0.25,
		purseCoins = 1, vipCoins = 0.2, vipXp = 0.25,
		bagSlots = 60, repMult = 2,
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

return Config
