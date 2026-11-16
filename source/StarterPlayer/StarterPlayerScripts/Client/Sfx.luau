-- StarterPlayerScripts/Client/Sfx.luau
-- Только встроенные звуки движка (rbxasset://) + питч-вариации. Мелодии собираются из нот.
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local Sfx = {}
Sfx.enabled = true
Sfx.skipOnce = nil :: string? -- V47: имя события, которое надо один раз не играть (окно магазина играет свой shop_open вместо общего open)
Sfx.music = true

---------------------------------------------------------------------
-- Свои звуки. Файлы лежат в audio/ репозитория; после загрузки в Roblox номера вписываются в Client/AudioIds.
-- Пока номера не вписаны, каждое событие играет встроенный звук движка (как раньше), ничего не ломается.
---------------------------------------------------------------------
local AUDIO: { [string]: any } = {}
do
	local mod = script.Parent:FindFirstChild("AudioIds")
	if mod and mod:IsA("ModuleScript") then
		local ok, ids = pcall(require, mod)
		if ok and type(ids) == "table" then
			AUDIO = ids
		end
	end
end

-- V41: настоящие записи из Creator Store (audio/tools/lib_bank.py): номер, поправка громкости и скорости на ключ файла.
-- Отключить: SoundService:SetAttribute("SpearNoLibrary", true) до запуска клиента. Свои номера из AudioIds ниже по приоритету.
local LIB_IDS: { [string]: string } = {}
local LIB_GAIN: { [string]: number } = {}
local LIB_SPEED: { [string]: number } = {}
local LIB_REUSE: { [string]: string } = {} -- ключ без своего номера берёт номер другого ключа AudioIds (например, музыка яйца берёт загруженную музыку мира)
Sfx.library = SoundService:GetAttribute("SpearNoLibrary") ~= true

local function libGain(key: string): number
	if Sfx.library and LIB_IDS[key] then
		return LIB_GAIN[key] or 1
	end
	return 1
end

local function libSpeed(key: string): number
	if Sfx.library and LIB_IDS[key] then
		return LIB_SPEED[key] or 1
	end
	return 1
end

local function audioId(file: string): string?
	if Sfx.library then
		local lib = LIB_IDS[file]
		if lib then
			return lib
		end
	end
	local id = AUDIO[file]
	if type(id) == "string" and id ~= "" and id ~= "rbxassetid://0" then
		return id
	end
	local re = LIB_REUSE[file]
	if re then
		local rid = AUDIO[re]
		if type(rid) == "string" and rid ~= "" and rid ~= "rbxassetid://0" then
			return rid
		end
	end
	return nil
end

-- событие -> несколько вариантов файла (по кругу, без повтора подряд)
local BANKS: { [string]: { string } } = {
	hover = { "ui_hover_1", "ui_hover_2", "ui_hover_3" },
	press = { "ui_press_1", "ui_press_2", "ui_press_3" },
	click = { "ui_press_1", "ui_press_2", "ui_press_3" },
	open = { "ui_open" }, close = { "ui_close" }, back = { "ui_back" }, error = { "ui_error" },
	select = { "ui_select_1", "ui_select_2" },
	toggle_on = { "ui_toggle_on" }, toggle_off = { "ui_toggle_off" },
	pop = { "pop" }, tick = { "tick" }, rep = { "train_rep_1", "train_rep_2", "train_rep_3" },
	coin = { "coin", "coin_2" }, coin_burst = { "coin_burst" }, buy = { "buy" }, pickup = { "pickup" },
	level = { "level" }, win = { "win" }, sparkle = { "sparkle" }, ping = { "note_marimba" },
	whoosh = { "whoosh" }, swoosh = { "whoosh" }, stamp = { "stamp" }, heart = { "heart" },
	thunder = { "thunder" }, boom = { "boom" }, crash = { "crash" },
	rustle = { "rustle_1", "rustle_2", "rustle_3" },
	creak = { "spear_charge" }, throw = { "spear_throw" }, miss = { "spear_miss" }, fly = { "spear_fly" },
	hit = { "spear_hit_soft_1", "spear_hit_soft_2", "spear_hit_soft_3" },
	hit_ground = { "spear_hit_ground_1", "spear_hit_ground_2", "spear_hit_ground_3" },
	hit_wood = { "spear_hit_wood_1", "spear_hit_wood_2", "spear_hit_wood_3" },
	blip = { "dialog_blip_1", "dialog_blip_2", "dialog_blip_3", "dialog_blip_4" },
	jump = { "jump" }, land = { "land" }, bounce = { "jump" },
	step_grass = { "step_grass_1", "step_grass_2", "step_grass_3", "step_grass_4" },
	step_stone = { "step_stone_1", "step_stone_2", "step_stone_3", "step_stone_4" },
	step_wood = { "step_wood_1", "step_wood_2", "step_wood_3", "step_wood_4" },
	-- V38: звуки магазина (кубики): файлы audio/shop_*.wav
	shop_open = { "shop_open" }, shop_close = { "shop_close" },
	shop_hover = { "shop_hover_1", "shop_hover_2", "shop_hover_3" },
	shop_press = { "shop_press_1", "shop_press_2" },
	shop_pop = { "shop_pop_1", "shop_pop_2" },
	shop_buy = { "shop_buy" }, shop_deny = { "shop_deny" }, shop_odds = { "shop_odds" },
	shop_equip = { "shop_equip" }, shop_unequip = { "shop_unequip" },
	shop_upgrade = { "shop_upgrade" }, shop_claim = { "shop_claim" },
}
-- Пока свой файл события не загружен, играет уже загруженный звук похожего события (а если нет и его: встроенный)
local ALIAS: { [string]: string } = {
	shop_open = "open", shop_close = "close", shop_hover = "hover", shop_press = "press", shop_pop = "pop",
	shop_buy = "buy", shop_deny = "error", shop_odds = "select", shop_equip = "toggle_on", shop_unequip = "toggle_off",
	shop_upgrade = "level", shop_claim = "coin_burst",
}
-- громкость по умолчанию (файлы нормализованы одинаково, громкость задаёт характер события)
local BANK_VOL: { [string]: number } = {
	hover = 0.22, press = 0.4, click = 0.4, open = 0.35, close = 0.33, back = 0.33, error = 0.45, select = 0.4,
	toggle_on = 0.35, toggle_off = 0.35, pop = 0.4, tick = 0.25, rep = 0.45, coin = 0.35, coin_burst = 0.3,
	buy = 0.45, pickup = 0.4, level = 0.5, win = 0.45, sparkle = 0.3, ping = 0.3, whoosh = 0.45, swoosh = 0.45,
	stamp = 0.55, heart = 0.5, thunder = 0.55, boom = 0.6, crash = 0.6, rustle = 0.45, creak = 0.25,
	throw = 0.55, miss = 0.4, fly = 0.25, hit = 0.55, hit_ground = 0.55, hit_wood = 0.55, blip = 0.18,
	jump = 0.35, land = 0.4, bounce = 0.35, step_grass = 0.3, step_stone = 0.3, step_wood = 0.3,
	shop_open = 0.4, shop_close = 0.36, shop_hover = 0.2, shop_press = 0.42, shop_pop = 0.26, shop_buy = 0.5,
	shop_deny = 0.42, shop_odds = 0.4, shop_equip = 0.4, shop_unequip = 0.36, shop_upgrade = 0.48, shop_claim = 0.45,
}
local bankCache: { [string]: Sound } = {}
local lastPick: { [string]: string } = {}

-- Есть ли свой звук для события (тогда встроенный не нужен)
function Sfx.has(name: string): boolean
	local files = BANKS[name]
	if not files then
		return false
	end
	for _, f in files do
		if audioId(f) then
			return true
		end
	end
	return false
end

local IDS = {
	click = "rbxasset://sounds/button.wav",
	swoosh = "rbxasset://sounds/swordslash.wav", -- swoosh.wav: "Asset is not approved for the requester"
	throw = "rbxasset://sounds/swordlunge.wav",
	slash = "rbxasset://sounds/swordslash.wav",
	equip = "rbxasset://sounds/unsheath.wav",
	hit = "rbxasset://sounds/collide.wav",
	collide = "rbxasset://sounds/collide.wav",
	tick = "rbxasset://sounds/clickfast.wav",
	ping = "rbxasset://sounds/electronicpingshort.wav",
	win = "rbxasset://sounds/victory.wav",
	snap = "rbxasset://sounds/snap.wav",
	splat = "rbxasset://sounds/splat.wav",
	jump = "rbxasset://sounds/action_jump.mp3",
	land = "rbxasset://sounds/action_jump_land.mp3",
	fall = "rbxasset://sounds/action_falling.mp3",
	getup = "rbxasset://sounds/action_get_up.mp3",
	swim = "rbxasset://sounds/action_swim.mp3",
	step = "rbxasset://sounds/action_footsteps_plastic.mp3",
	water = "rbxasset://sounds/impact_water.mp3",
}
-- Составные «пресеты»: звук, питч, громкость, разброс питча
local PRESETS: { [string]: { any } } = {
	hover = { "ping", 2.05, 0.11, 0.035 },
	press = { "click", 1.08, 0.34, 0.04 },
	open = { "swoosh", 1.25, 0.32, 0.04 },
	close = { "swoosh", 0.85, 0.35, 0.05 },
	coin = { "ping", 2.2, 0.35, 0.12 },
	buy = { "win", 1.6, 0.4, 0 },
	error = { "hit", 0.6, 0.6, 0 },
	pop = { "click", 1.8, 0.5, 0.1 },
	stamp = { "hit", 0.75, 0.9, 0 },
	rustle = { "step", 0.7, 0.8, 0.15 },
	heart = { "hit", 0.35, 0.9, 0 },
	boom = { "hit", 0.45, 1, 0.05 },
	sparkle = { "ping", 2.8, 0.25, 0.2 },
	creak = { "snap", 0.55, 0.35, 0.1 },
	crash = { "snap", 0.4, 1, 0 },
	level = { "win", 1.2, 0.6, 0 },
	bounce = { "jump", 0.75, 0.8, 0.08 },
	whoosh = { "swoosh", 0.7, 0.8, 0.05 },
	thunder = { "hit", 0.25, 1, 0.03 },
	-- запасные звуки для новых событий (пока не загружены свои)
	select = { "click", 1.25, 0.34, 0.05 },
	back = { "swoosh", 0.9, 0.3, 0.05 },
	blip = { "ping", 1.5, 0.12, 0.05 },
	rep = { "click", 1.8, 0.5, 0.1 }, -- как "pop"
	throw = { "swoosh", 0.7, 0.8, 0.05 }, -- как "whoosh" (бросок копья)
	miss = { "swoosh", 1.1, 0.4, 0.05 },
	hit_ground = { "hit", 0.7, 0.7, 0 }, -- копьё врезалось в землю (как раньше)
	hit_wood = { "hit", 1.3, 0.6, 0.05 },
	pickup = { "ping", 2.0, 0.35, 0.08 },
	coin_burst = { "ping", 2.2, 0.3, 0.15 },
	-- V38: запасные встроенные звуки магазина
	shop_open = { "swoosh", 1.25, 0.3, 0.04 },
	shop_close = { "swoosh", 0.85, 0.33, 0.05 },
	shop_hover = { "ping", 2.05, 0.1, 0.035 },
	shop_press = { "click", 1.08, 0.34, 0.04 },
	shop_pop = { "click", 1.8, 0.3, 0.1 },
	shop_buy = { "win", 1.6, 0.4, 0 },
	shop_deny = { "hit", 0.6, 0.5, 0 },
	shop_odds = { "click", 1.25, 0.34, 0.05 },
	shop_equip = { "click", 1.4, 0.35, 0.03 },
	shop_unequip = { "click", 0.9, 0.35, 0.03 },
	shop_upgrade = { "win", 1.2, 0.5, 0 },
	shop_claim = { "ping", 2.2, 0.3, 0.15 },
}

local folder = Instance.new("Folder")
folder.Name = "SpearSfx"
folder.Parent = SoundService
local cache: { [string]: Sound } = {}
local lastHover = 0
for name, id in IDS do
	local s = Instance.new("Sound")
	s.Name = name
	s.SoundId = id
	s.Volume = 0.6
	s.Parent = folder
	cache[name] = s
end

-- Следующий вариант звука события (шаблон Sound) или nil, если своих файлов нет
local function bankSound(name: string): Sound?
	local files = BANKS[name]
	if not files then
		return nil
	end
	local avail = {}
	for _, f in files do
		if audioId(f) then
			table.insert(avail, f)
		end
	end
	if #avail == 0 then
		local alt = ALIAS[name]
		if alt then
			return bankSound(alt)
		end
		return nil
	end
	local pick = avail[math.random(1, #avail)]
	if #avail > 1 and pick == lastPick[name] then
		pick = avail[(table.find(avail, pick) :: number) % #avail + 1]
	end
	lastPick[name] = pick
	local base = bankCache[pick]
	if not base then
		base = Instance.new("Sound")
		base.Name = pick
		base.SoundId = audioId(pick) :: string
		base.Volume = 0.5
		base.Parent = folder
		bankCache[pick] = base
	end
	return base
end

-- Высоту, подобранную вызывающим кодом под старый встроенный звук, пересчитываем относительно его «нормы»:
-- свои файлы уже сыграны в нужной тональности, поэтому норма = 1
-- События, у которых «старой нормы» нет (встроенный звук лишь запасной): высота передаётся как написана
local ASWRITTEN: { [string]: boolean } = {
	select = true, back = true, blip = true, rep = true, throw = true, miss = true,
	hit_ground = true, hit_wood = true, pickup = true, coin_burst = true,
	shop_open = true, shop_close = true, shop_hover = true, shop_press = true, shop_pop = true, shop_buy = true,
	shop_deny = true, shop_odds = true, shop_equip = true, shop_unequip = true, shop_upgrade = true, shop_claim = true,
}

-- BEGIN GENERATED egg audio (audio/tools/egg_cues.py). Do not edit by hand: change the script and run egg_build.py.
local EGG_BANKS = {
	egg_appear = { "egg_appear" },
	egg_knock = { "egg_knock_1", "egg_knock_2" },
	egg_riser_forest = { "egg_riser_forest" },
	egg_riser_amber = { "egg_riser_amber" },
	egg_riser_tide = { "egg_riser_tide" },
	egg_riser_storm = { "egg_riser_storm" },
	egg_riser_astral = { "egg_riser_astral" },
	egg_crack = { "egg_crack_1", "egg_crack_2" },
	egg_boom_s = { "egg_boom_s" },
	egg_boom_m = { "egg_boom_m" },
	egg_boom_l = { "egg_boom_l" },
	egg_burst_s = { "egg_burst_s" },
	egg_burst_m = { "egg_burst_m" },
	egg_burst_l = { "egg_burst_l" },
	egg_thunder = { "egg_thunder" },
	egg_divine = { "egg_divine" },
	forest_snap = { "forest_snap_1", "forest_snap_2" },
	forest_leaves = { "forest_leaves" },
	forest_shimmer = { "forest_shimmer" },
	amber_note = { "amber_note" },
	amber_inflow = { "amber_inflow" },
	amber_sun = { "amber_sun" },
	amber_shard = { "amber_shard_1", "amber_shard_2" },
	tide_bubbles = { "tide_bubbles" },
	tide_splash = { "tide_splash" },
	tide_pop = { "tide_pop_1", "tide_pop_2" },
	tide_ring = { "tide_ring" },
	storm_crackle = { "storm_crackle" },
	storm_zap = { "storm_zap_1", "storm_zap_2" },
	storm_clamp = { "storm_clamp" },
	storm_thunder = { "storm_thunder" },
	storm_arcs = { "storm_arcs" },
	astral_twinkle = { "astral_twinkle" },
	astral_ring = { "astral_ring" },
	astral_burst = { "astral_burst" },
	astral_split = { "astral_split" },
	egg_flash = { "egg_flash" },
	egg_ring_s = { "egg_ring_s" },
	egg_ring_l = { "egg_ring_l" },
	pet_emerge = { "pet_emerge" },
	pet_trail = { "pet_trail" },
	pet_land_s = { "pet_land_s" },
	pet_land_m = { "pet_land_m" },
	pet_land_l = { "pet_land_l" },
	pet_slowmo = { "pet_slowmo" },
	egg_shafts = { "egg_shafts" },
	egg_halo = { "egg_halo" },
	egg_orbit = { "egg_orbit" },
	pet_tap = { "pet_tap_1", "pet_tap_2" },
	egg_skip = { "egg_skip" },
	egg_reveal_0 = { "egg_reveal_0" },
	egg_reveal_1 = { "egg_reveal_1" },
	egg_reveal_2 = { "egg_reveal_2" },
	egg_reveal_3 = { "egg_reveal_3" },
	egg_reveal_4 = { "egg_reveal_4" },
	egg_reveal_5 = { "egg_reveal_5" },
	egg_reveal_6 = { "egg_reveal_6" },
	egg_card = { "egg_card" },
	egg_new = { "egg_new" },
	egg_dupe = { "egg_dupe" },
	egg_music_a = { "egg_music_a" },
	egg_music_b = { "egg_music_b" },
	egg_surge = { "egg_surge" },
}
-- until a file is uploaded the game plays this existing sound instead (a missing entry means silence)
local EGG_ALIAS = {
	egg_appear = "sparkle",
	egg_knock = "tick",
	egg_riser_forest = "whoosh",
	egg_riser_amber = "whoosh",
	egg_riser_tide = "whoosh",
	egg_riser_storm = "whoosh",
	egg_riser_astral = "whoosh",
	egg_crack = "hit_wood",
	egg_boom_s = "pop",
	egg_boom_m = "boom",
	egg_boom_l = "boom",
	egg_burst_s = "sparkle",
	egg_burst_m = "sparkle",
	egg_burst_l = "sparkle",
	egg_thunder = "thunder",
	egg_divine = "thunder",
	forest_snap = "hit_wood",
	forest_leaves = "rustle",
	amber_note = "ping",
	amber_sun = "level",
	amber_shard = "pickup",
	tide_splash = "whoosh",
	tide_pop = "pop",
	tide_ring = "pop",
	storm_zap = "sparkle",
	storm_clamp = "hit_wood",
	storm_thunder = "thunder",
	astral_ring = "level",
	astral_burst = "win",
	astral_split = "whoosh",
	egg_flash = "sparkle",
	egg_ring_s = "pop",
	egg_ring_l = "whoosh",
	pet_emerge = "whoosh",
	pet_land_s = "land",
	pet_land_m = "land",
	pet_land_l = "land",
	pet_slowmo = "whoosh",
	egg_shafts = "whoosh",
	egg_halo = "level",
	egg_orbit = "whoosh",
	pet_tap = "pop",
	egg_skip = "swoosh",
	egg_reveal_0 = "win",
	egg_reveal_1 = "win",
	egg_reveal_2 = "win",
	egg_reveal_3 = "win",
	egg_reveal_4 = "level",
	egg_reveal_5 = "level",
	egg_reveal_6 = "level",
	egg_card = "stamp",
	egg_new = "coin",
	egg_dupe = "tick",
}
local EGG_VOL = {
	egg_appear = 0.5,
	egg_knock = 0.5,
	egg_riser_forest = 0.5,
	egg_riser_amber = 0.5,
	egg_riser_tide = 0.5,
	egg_riser_storm = 0.5,
	egg_riser_astral = 0.5,
	egg_crack = 0.75,
	egg_boom_s = 0.7,
	egg_boom_m = 0.8,
	egg_boom_l = 0.9,
	egg_burst_s = 0.5,
	egg_burst_m = 0.55,
	egg_burst_l = 0.6,
	egg_thunder = 0.7,
	egg_divine = 0.8,
	forest_snap = 0.55,
	forest_leaves = 0.6,
	forest_shimmer = 0.28,
	amber_note = 0.55,
	amber_inflow = 0.26,
	amber_sun = 0.5,
	amber_shard = 0.5,
	tide_bubbles = 0.3,
	tide_splash = 0.7,
	tide_pop = 0.5,
	tide_ring = 0.5,
	storm_crackle = 0.5,
	storm_zap = 0.6,
	storm_clamp = 0.6,
	storm_thunder = 0.8,
	storm_arcs = 0.3,
	astral_twinkle = 0.3,
	astral_ring = 0.55,
	astral_burst = 0.6,
	astral_split = 0.6,
	egg_flash = 0.5,
	egg_ring_s = 0.3,
	egg_ring_l = 0.4,
	pet_emerge = 0.7,
	pet_trail = 0.22,
	pet_land_s = 0.6,
	pet_land_m = 0.7,
	pet_land_l = 0.75,
	pet_slowmo = 0.6,
	egg_shafts = 0.5,
	egg_halo = 0.55,
	egg_orbit = 0.5,
	pet_tap = 0.5,
	egg_skip = 0.5,
	egg_reveal_0 = 0.62,
	egg_reveal_1 = 0.62,
	egg_reveal_2 = 0.62,
	egg_reveal_3 = 0.62,
	egg_reveal_4 = 0.62,
	egg_reveal_5 = 0.62,
	egg_reveal_6 = 0.62,
	egg_card = 0.5,
	egg_new = 0.6,
	egg_dupe = 0.55,
	egg_music_a = 0.2,
	egg_music_b = 0.2,
	egg_surge = 0.34,
}
for name, files in EGG_BANKS do
	BANKS[name] = files
	ASWRITTEN[name] = true
	BANK_VOL[name] = EGG_VOL[name]
end
for name, alt in EGG_ALIAS do
	ALIAS[name] = alt
end
-- END GENERATED egg audio

-- BEGIN GENERATED library sounds (audio/tools/lib_bank.py). Do not edit by hand.
local EGG_LIB = {
	egg_crack_1 = "rbxassetid://9113959343",
	egg_crack_2 = "rbxassetid://9113959332",
	egg_boom_s = "rbxassetid://1837830050",
	egg_boom_m = "rbxassetid://103410515538241",
	egg_boom_l = "rbxassetid://9125484511",
	egg_thunder = "rbxassetid://95410087861011",
	storm_thunder = "rbxassetid://72113341430811",
	storm_zap_1 = "rbxassetid://9116277954",
	storm_zap_2 = "rbxassetid://9116279560",
	egg_burst_s = "rbxassetid://135968996204345",
	egg_burst_m = "rbxassetid://117011707307950",
	egg_burst_l = "rbxassetid://132381858621446",
	egg_flash = "rbxassetid://135968996204345",
	tide_splash = "rbxassetid://9125702987",
	egg_riser_forest = "rbxassetid://9040288138",
	egg_riser_amber = "rbxassetid://9040281199",
	egg_riser_tide = "rbxassetid://9043343295",
	egg_riser_storm = "rbxassetid://9040281199",
	egg_riser_astral = "rbxassetid://1837834284",
	storm_crackle = "rbxassetid://9116279560",
	storm_arcs = "rbxassetid://9116277954",
	pet_trail = "rbxassetid://131722051883127",
	amber_inflow = "rbxassetid://131722051883127",
	tide_bubbles = "rbxassetid://131722051883127",
	forest_shimmer = "rbxassetid://132381858621446",
	astral_twinkle = "rbxassetid://117011707307950",
	egg_surge = "rbxassetid://9040281199",
	egg_reveal_0 = "rbxassetid://1841173394",
	egg_reveal_1 = "rbxassetid://1841209502",
	egg_reveal_2 = "rbxassetid://1841173434",
	egg_reveal_3 = "rbxassetid://9043144476",
	egg_reveal_4 = "rbxassetid://9041792228",
	egg_reveal_5 = "rbxassetid://1836860398",
	egg_reveal_6 = "rbxassetid://1841180330",
}
local EGG_GAIN = {
	egg_crack_1 = 2.94,
	egg_crack_2 = 3.16,
	egg_boom_s = 1.28,
	egg_boom_m = 0.91,
	egg_boom_l = 0.82,
	egg_thunder = 1.57,
	storm_thunder = 2.57,
	storm_zap_1 = 0.94,
	storm_zap_2 = 1.23,
	egg_burst_s = 0.84,
	egg_burst_m = 0.72,
	egg_burst_l = 3.02,
	egg_flash = 0.84,
	tide_splash = 1.84,
	egg_riser_forest = 0.81,
	egg_riser_amber = 0.88,
	egg_riser_tide = 1.46,
	egg_riser_storm = 0.88,
	egg_riser_astral = 1.16,
	storm_crackle = 1.23,
	storm_arcs = 0.94,
	pet_trail = 2.43,
	amber_inflow = 2.43,
	tide_bubbles = 2.43,
	forest_shimmer = 3.02,
	astral_twinkle = 0.63,
	egg_surge = 0.88,
	egg_reveal_0 = 1.47,
	egg_reveal_1 = 1.26,
	egg_reveal_2 = 1.23,
	egg_reveal_3 = 0.96,
	egg_reveal_4 = 0.79,
	egg_reveal_5 = 0.58,
	egg_reveal_6 = 0.84,
}
local EGG_SPEED = {
	egg_riser_forest = 0.85,
	egg_riser_amber = 1.7,
	egg_riser_tide = 1.5,
	egg_riser_storm = 1.7,
	egg_riser_astral = 1.4,
	amber_inflow = 0.9,
	tide_bubbles = 1.35,
}
local EGG_REUSE = {
	egg_music_a = "music_meadow",
	egg_music_b = "music_cozy",
}
for k, id in EGG_LIB do LIB_IDS[k] = id end
for k, v in EGG_REUSE do LIB_REUSE[k] = v end
for k, g in EGG_GAIN do LIB_GAIN[k] = g end
for k, s in EGG_SPEED do LIB_SPEED[k] = s end
-- END GENERATED library sounds

local function customPitch(name: string, pitch: number?): number?
	if not pitch then
		return nil
	end
	if ASWRITTEN[name] then
		return math.clamp(pitch, 0.5, 1.8)
	end
	local pr = PRESETS[name]
	return math.clamp(pitch / ((pr and pr[2]) or 1), 0.6, 1.7)
end

local function playBank(base: Sound, name: string, pitch: number?, volume: number?, parent: Instance?): Sound
	local s = base:Clone()
	s.PlaybackSpeed = (customPitch(name, pitch) or (1 + (math.random() * 2 - 1) * (if name:sub(1, 4) == "step" then 0.06 else 0.03))) * libSpeed(base.Name)
	s.Volume = (volume or BANK_VOL[name] or 0.4) * libGain(base.Name)
	s.Parent = parent or folder
	s:Play()
	s.Ended:Once(function()
		s:Destroy()
	end)
	task.delay(10, function()
		if s.Parent then
			s:Destroy()
		end
	end)
	return s
end

function Sfx.play(name: string, pitch: number?, volume: number?): Sound?
	if not Sfx.enabled then
		return nil
	end
	if Sfx.skipOnce == name then
		Sfx.skipOnce = nil
		return nil
	end
	if name == "hover" then
		local now = os.clock()
		if now - lastHover < 0.055 then
			return nil
		end
		lastHover = now
	end
	local custom = bankSound(name)
	if custom then
		-- щелчок заряда играет зацикленный звук натяжения, второй раз поверх него не нужен
		if name == "creak" then
			return nil
		end
		return playBank(custom, name, pitch, volume)
	end
	local pr = PRESETS[name]
	local base = cache[pr and pr[1] or name]
	if not base then
		return nil
	end
	local s = base:Clone()
	local p = pitch or (pr and pr[2]) or 1
	if pr and not pitch and pr[4] > 0 then
		p *= 1 + (math.random() * 2 - 1) * pr[4]
	end
	s.PlaybackSpeed = p
	s.Volume = volume or (pr and pr[3]) or 0.6
	s.Parent = folder
	s:Play()
	s.Ended:Once(function()
		s:Destroy()
	end)
	task.delay(8, function()
		if s.Parent then
			s:Destroy()
		end
	end)
	return s
end

-- Второй тихий слой делает нажатия округлыми, а не резкими «кликами».
function Sfx.ui(kind: string)
	if Sfx.has("press") then
		Sfx.play(if kind == "hover" then "hover" elseif kind == "open" then "open" else "press")
		return
	end
	if kind == "press" then
		Sfx.play("press")
		Sfx.play("ping", 1.72 + math.random() * 0.08, 0.075)
	elseif kind == "open" then
		Sfx.play("open")
		Sfx.play("ping", 1.42, 0.065)
	else
		Sfx.play("hover")
	end
end

-- Звук в мире (3D)
function Sfx.at(pos: Vector3, name: string, pitch: number?, volume: number?)
	if not Sfx.enabled then
		return
	end
	local custom = bankSound(name)
	local pr = PRESETS[name]
	local base = custom or cache[pr and pr[1] or name]
	if not base then
		return
	end
	local a = Instance.new("Attachment")
	a.WorldPosition = pos
	a.Parent = workspace.Terrain
	local s = base:Clone()
	if custom then
		s.PlaybackSpeed = customPitch(name, pitch) or (1 + (math.random() * 2 - 1) * 0.03)
		s.Volume = volume or BANK_VOL[name] or 0.7
	else
		s.PlaybackSpeed = pitch or (pr and pr[2]) or 1
		s.Volume = volume or (pr and pr[3]) or 0.7
	end
	s.RollOffMinDistance = 12
	s.RollOffMaxDistance = 160
	s.Parent = a
	s:Play()
	task.delay(6, function()
		a:Destroy()
	end)
end

-- Нота: полутоны от «ля», инструмент — ping/click/tick
function Sfx.note(semi: number, vol: number?, inst: string?)
	if not Sfx.music then
		return
	end
	local custom = if inst == nil or inst == "ping" then bankSound("ping") else nil
	local base = custom or cache[inst or "ping"]
	if not base then
		return
	end
	local s = base:Clone()
	s.PlaybackSpeed = 2 ^ (semi / 12)
	s.Volume = vol or 0.25
	s.Parent = folder
	s:Play()
	task.delay(3, function()
		s:Destroy()
	end)
end

-- Восходящая гамма (для раскрытий и счётчиков)
function Sfx.rise(step: number, vol: number?)
	Sfx.note(step * 2 - 2, vol or 0.35, "ping")
end

-- Зацикленный звук (натяжение, сердцебиение): вернуть Sound, остановить :Destroy()
function Sfx.loop(name: string, pitch: number?, volume: number?): Sound?
	if not Sfx.enabled then
		return nil
	end
	local custom = bankSound(name)
	local pr = PRESETS[name]
	local base = custom or cache[pr and pr[1] or name]
	if not base then
		return nil
	end
	local s = base:Clone()
	s.Looped = true
	s.PlaybackSpeed = (if custom then customPitch(name, pitch) else pitch) or (if custom then 1 else (pr and pr[2])) or 1
	s.Volume = volume or (if custom then BANK_VOL[name] else (pr and pr[3])) or 0.4
	s.Parent = folder
	s:Play()
	return s
end

-- Зацикленный звук, привязанный к предмету (копьё в полёте): умирает вместе с деталью
function Sfx.attachLoop(target: Instance, name: string, volume: number?): Sound?
	if not Sfx.enabled then
		return nil
	end
	local part = if target:IsA("BasePart") then target else target:FindFirstChildWhichIsA("BasePart", true)
	local base = bankSound(name)
	if not part or not base then
		return nil
	end
	local s = base:Clone()
	s.Looped = true
	s.Volume = volume or BANK_VOL[name] or 0.3
	s.RollOffMinDistance = 10
	s.RollOffMaxDistance = 140
	s.Parent = part
	s:Play()
	return s
end

-- V39: слой (музыка, петля) с плавным входом и выходом. Возвращает { stop = function(fadeOut) } или nil, если звука нет.
-- looped = false: проиграть один раз (например, нарастание перед раскрытием яйца)
function Sfx.layer(name: string, volume: number?, fadeIn: number?, pitch: number?, looped: boolean?): any
	if not Sfx.enabled then
		return nil
	end
	local base = bankSound(name)
	if not base then
		return nil
	end
	local s = base:Clone()
	s.Looped = looped ~= false
	s.PlaybackSpeed = (pitch or 1) * libSpeed(base.Name)
	s.Volume = 0
	s.Parent = folder
	s:Play()
	TweenService:Create(s, TweenInfo.new(fadeIn or 0.3), { Volume = (volume or BANK_VOL[name] or 0.3) * libGain(base.Name) }):Play()
	local dead = false
	local handle = {}
	function handle.stop(fadeOut: number?)
		if dead then
			return
		end
		dead = true
		local f = fadeOut or 0.4
		TweenService:Create(s, TweenInfo.new(f), { Volume = 0 }):Play()
		task.delay(f + 0.05, function()
			s:Destroy()
		end)
	end
	if looped == false then
		s.Ended:Once(function()
			dead = true
			s:Destroy()
		end)
	end
	-- страховка: слой не живёт дольше двух минут, даже если сцену не закрыли
	task.delay(120, function()
		handle.stop(0.2)
	end)
	return handle
end

-- Шаг по поверхности: kind = "grass" | "stone" | "wood"
function Sfx.step(kind: string, volume: number?, pitch: number?)
	Sfx.play("step_" .. kind, pitch, volume)
end

---------------------------------------------------------------------
-- Тихая фоновая музыка: треки из публичной библиотеки Roblox.
-- Переключаемся по окончании, при неудачной загрузке пробуем следующий.
---------------------------------------------------------------------
local MUSIC = {
	"rbxassetid://1837879082", -- Paradise Falls
	"rbxassetid://9043887091", -- Lo-fi Chill A
	"rbxassetid://1848354536", -- Relaxed Scene
	"rbxassetid://1837429944", -- Soft Music
}
local musicSound: Sound? = nil
local musicGeneration = 0
local musicRunning = false
local musicMood = "normal"
local musicSkip = false
local musicGroupNow = "normal"
local ambienceSound: Sound? = nil
-- свои треки по настроению: спокойные для обычной игры, живее для охоты
local TRACKS: { [string]: { string } } = {
	normal = { "music_meadow", "music_cozy" },
	hunt = { "music_hunt" },
}

-- Только "hunt" и "normal" меняют музыку; "cinematic"/"busy" (показ добычи, окна) оставляют текущую,
-- иначе каждый бросок переключал бы трек туда и обратно
local function musicGroup(): string
	if musicMood == "hunt" then
		return "hunt"
	elseif musicMood == "normal" then
		return "normal"
	end
	return musicGroupNow
end
local badTracks: { [string]: boolean } = {}

local function customTrackIds(group: string): { string }
	local ids = {}
	for _, f in TRACKS[group] do
		local id = audioId(f)
		if id and not badTracks[id] then
			table.insert(ids, id)
		end
	end
	return ids
end

-- V39: пока идёт открытие яйца, фоновая музыка почти молчит (Sfx.duck), чтобы было слышно музыку и звуки сцены
local duckFactor = 1

local function musicVolume(): number
	local base = 0.115
	if musicMood == "cinematic" then
		base = 0.05
	elseif musicMood == "hunt" then
		base = 0.075
	elseif musicMood == "busy" then
		base = 0.065
	end
	return base * duckFactor
end

function Sfx.setMood(mode: string)
	musicMood = mode
	-- своя музыка: при смене группы (обычная <-> охота) плавно переходим на другой трек
	if musicRunning and musicGroup() ~= musicGroupNow and #customTrackIds(musicGroup()) > 0 then
		musicSkip = true
	end
	local s = musicSound
	if s then
		TweenService:Create(s, TweenInfo.new(0.65, Enum.EasingStyle.Sine), { Volume = musicVolume() }):Play()
	end
end

-- V39: приглушить фоновую музыку (factor 0..1); Sfx.duck(1) возвращает обычную громкость
function Sfx.duck(factor: number, fade: number?)
	duckFactor = math.clamp(factor, 0, 1)
	local info = TweenInfo.new(fade or 0.5, Enum.EasingStyle.Sine)
	local m = musicSound
	if m then
		TweenService:Create(m, info, { Volume = musicVolume() }):Play()
	end
	local a = ambienceSound
	if a then
		TweenService:Create(a, info, { Volume = 0.09 * duckFactor }):Play()
	end
end

function Sfx.setMusic(on: boolean)
	if Sfx.music == on and (not on or musicRunning) then
		return
	end
	Sfx.music = on
	musicGeneration += 1
	musicRunning = false
	local amb = ambienceSound
	ambienceSound = nil
	if amb then
		amb:Destroy()
	end
	local s = musicSound
	musicSound = nil
	if s then
		TweenService:Create(s, TweenInfo.new(0.3), { Volume = 0 }):Play()
		task.delay(0.32, function()
			s:Destroy()
		end)
	end
	if on then
		task.defer(Sfx.startMusic)
	end
end

function Sfx.startMusic()
	if musicRunning or not Sfx.music then
		return
	end
	musicRunning = true
	musicGeneration += 1
	local generation = musicGeneration
	-- тихая атмосфера леса под музыкой (если загружена)
	local ambId = audioId("amb_forest")
	if ambId and not ambienceSound then
		local a = Instance.new("Sound")
		a.Name = "SpearHuntAmbience"
		a.SoundId = ambId
		a.Looped = true
		a.Volume = 0.09 * duckFactor
		a.Parent = SoundService
		a:Play()
		ambienceSound = a
	end
	task.spawn(function()
		local index = math.random(1, #MUSIC)
		local customIndex = 0
		while Sfx.music and generation == musicGeneration do
			musicSkip = false
			musicGroupNow = musicGroup()
			local custom = customTrackIds(musicGroupNow)
			local trackId = MUSIC[index]
			if #custom > 0 then
				customIndex = customIndex % #custom + 1
				trackId = custom[customIndex]
			end
			local s = Instance.new("Sound")
			s.Name = "SpearHuntMusic"
			s.SoundId = trackId
			s.Looped = false
			s.Volume = 0
			s.Parent = SoundService
			musicSound = s
			s:Play()
			TweenService:Create(s, TweenInfo.new(1.2, Enum.EasingStyle.Sine), { Volume = musicVolume() }):Play()
			local ended = false
			s.Ended:Once(function()
				ended = true
			end)
			local elapsed = 0
			local failed = false
			while Sfx.music and generation == musicGeneration and not ended and not musicSkip do
				task.wait(0.5)
				elapsed += 0.5
				-- Ассет недоступен/не загрузился: пробуем следующий трек.
				if elapsed >= 8 and s.TimeLength == 0 then
					failed = true
					break
				end
			end
			if failed and #custom > 0 then
				badTracks[trackId] = true -- этот свой трек не загрузился: дальше играем остальные или библиотеку
			end
			if musicSound == s then
				musicSound = nil
			end
			if musicSkip and generation == musicGeneration then
				-- плавный уход старого трека при смене настроения
				TweenService:Create(s, TweenInfo.new(1.1, Enum.EasingStyle.Sine), { Volume = 0 }):Play()
				task.delay(1.2, function()
					s:Destroy()
				end)
			else
				s:Destroy()
			end
			index = index % #MUSIC + 1
			task.wait(0.3)
		end
		if generation == musicGeneration then
			musicRunning = false
		end
	end)
end

return Sfx
