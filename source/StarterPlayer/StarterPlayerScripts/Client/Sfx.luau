-- StarterPlayerScripts/Client/Sfx.luau
-- Только встроенные звуки движка (rbxasset://) + питч-вариации. Мелодии собираются из нот.
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local Sfx = {}
Sfx.enabled = true
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

local function audioId(file: string): string?
	local id = AUDIO[file]
	if type(id) == "string" and id ~= "" and id ~= "rbxassetid://0" then
		return id
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
}
-- громкость по умолчанию (файлы нормализованы одинаково, громкость задаёт характер события)
local BANK_VOL: { [string]: number } = {
	hover = 0.22, press = 0.4, click = 0.4, open = 0.35, close = 0.33, back = 0.33, error = 0.45, select = 0.4,
	toggle_on = 0.35, toggle_off = 0.35, pop = 0.4, tick = 0.25, rep = 0.45, coin = 0.35, coin_burst = 0.3,
	buy = 0.45, pickup = 0.4, level = 0.5, win = 0.45, sparkle = 0.3, ping = 0.3, whoosh = 0.45, swoosh = 0.45,
	stamp = 0.55, heart = 0.5, thunder = 0.55, boom = 0.6, crash = 0.6, rustle = 0.45, creak = 0.25,
	throw = 0.55, miss = 0.4, fly = 0.25, hit = 0.55, hit_ground = 0.55, hit_wood = 0.55, blip = 0.18,
	jump = 0.35, land = 0.4, bounce = 0.35, step_grass = 0.3, step_stone = 0.3, step_wood = 0.3,
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
	swoosh = "rbxasset://sounds/swoosh.wav",
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
}

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
	s.PlaybackSpeed = customPitch(name, pitch) or (1 + (math.random() * 2 - 1) * (if name:sub(1, 4) == "step" then 0.06 else 0.03))
	s.Volume = volume or BANK_VOL[name] or 0.4
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

local function musicVolume(): number
	if musicMood == "cinematic" then
		return 0.05
	elseif musicMood == "hunt" then
		return 0.075
	elseif musicMood == "busy" then
		return 0.065
	end
	return 0.115
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
		a.Volume = 0.09
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
