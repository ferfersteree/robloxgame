--!strict
-- Presentation geometry only: the authoritative catch/result is untouched.
-- V61: куст подстраивается под размер зверя (CoverScale), а у каждого вида своё появление (Emerge):
--   манера выхода (13 вариантов: walk leap burst rise drop swoop surge pounce roll skitter stomp pop flash)
--   + фирменный жест после выхода (16 вариантов). Пара (манера, жест) у 150 видов не повторяется, числа у каждого свои.
--   Таблица REVEAL ниже пишется инструментом tools/creature_data.py, руками её не править.
local RunService=game:GetService("RunService")
local Stage={}
local TAU=math.pi*2

local function ease(u: number): number u=math.clamp(u,0,1);return u*u*(3-2*u) end
local function outc(u: number): number u=math.clamp(u,0,1);return 1-(1-u)^3 end

-- BEGIN V61 REVEAL (tools/creature_data.py)
local REVEAL: { [string]: any } = {
	rabbit = { fam = "leap", flo = "hop2", dur = 0.98, amp = 1.18, hold = 0.41, scare = 0.69, open = 0.38, lead = 0.22 },
	squirrel = { fam = "pop", flo = "twirl", dur = 1.27, amp = 0.84, hold = 0.52, scare = 1.21, open = 0.3, lead = 0.05 },
	hedgehog = { fam = "roll", flo = "wiggle", dur = 1.53, amp = 0.85, hold = 0.48, scare = 0.68, open = 0.6, lead = 0.3 },
	fox = { fam = "pounce", flo = "bow", dur = 1.55, amp = 0.97, hold = 0.45, scare = 0.75, open = 0.56, lead = 0.34 },
	dodo = { fam = "walk", flo = "shake", dur = 1.16, amp = 0.89, hold = 0.38, scare = 1.14, open = 0.81, lead = 0.46 },
	moonrabbit = { fam = "flash", flo = "bounce", dur = 1.16, amp = 1.11, hold = 0.56, scare = 1.13, open = 0.54, lead = 0.1 },
	roe = { fam = "leap", flo = "lookaround", dur = 0.85, amp = 0.85, hold = 0.26, scare = 0.89, open = 0.42, lead = 0.25 },
	boar = { fam = "burst", flo = "shake", dur = 0.96, amp = 1.2, hold = 0.53, scare = 0.76, open = 0.26, lead = 0.1 },
	badger = { fam = "rise", flo = "sniff", dur = 1.57, amp = 1.08, hold = 0.4, scare = 0.72, open = 0.67, lead = 0.19 },
	wolf = { fam = "burst", flo = "roar", dur = 0.94, amp = 0.87, hold = 0.48, scare = 1.24, open = 0.29, lead = 0.1 },
	lynx = { fam = "pounce", flo = "stretch", dur = 1.56, amp = 0.85, hold = 0.4, scare = 0.97, open = 0.57, lead = 0.29 },
	sabertooth = { fam = "pounce", flo = "roar", dur = 1.41, amp = 0.82, hold = 0.39, scare = 1.13, open = 0.6, lead = 0.28 },
	deer = { fam = "walk", flo = "bow", dur = 1.4, amp = 1.05, hold = 0.31, scare = 1.19, open = 0.81, lead = 0.45 },
	moose = { fam = "stomp", flo = "lookaround", dur = 1.67, amp = 1.14, hold = 0.58, scare = 0.82, open = 1.06, lead = 0.48 },
	bear = { fam = "rise", flo = "rear", dur = 1.52, amp = 1.05, hold = 0.23, scare = 0.83, open = 0.69, lead = 0.19 },
	bison = { fam = "stomp", flo = "shake", dur = 1.63, amp = 1.06, hold = 0.32, scare = 1.2, open = 0.97, lead = 0.52 },
	cavebear = { fam = "rise", flo = "stretch", dur = 1.37, amp = 1.08, hold = 0.33, scare = 0.92, open = 0.61, lead = 0.2 },
	spiritdeer = { fam = "flash", flo = "stretch", dur = 1.44, amp = 1.09, hold = 0.48, scare = 0.68, open = 0.47, lead = 0.1 },
	megadeer = { fam = "walk", flo = "flare", dur = 1.39, amp = 1.22, hold = 0.38, scare = 1.06, open = 0.93, lead = 0.46 },
	rhino = { fam = "burst", flo = "stomp3", dur = 0.99, amp = 1.19, hold = 0.6, scare = 1.11, open = 0.3, lead = 0.09 },
	mammoth = { fam = "stomp", flo = "sway", dur = 1.91, amp = 1.01, hold = 0.48, scare = 0.83, open = 0.97, lead = 0.55 },
	cavelion = { fam = "pounce", flo = "rear", dur = 1.31, amp = 1.21, hold = 0.32, scare = 0.76, open = 0.54, lead = 0.27 },
	icemammoth = { fam = "stomp", flo = "roar", dur = 1.76, amp = 1.02, hold = 0.42, scare = 1.14, open = 1.1, lead = 0.56 },
	yeti = { fam = "drop", flo = "rear", dur = 1.16, amp = 1.15, hold = 0.33, scare = 0.75, open = 0.65, lead = 0.11 },
	gazelle = { fam = "leap", flo = "stretch", dur = 1.02, amp = 0.95, hold = 0.6, scare = 1.07, open = 0.4, lead = 0.2 },
	hyena = { fam = "pounce", flo = "wiggle", dur = 1.4, amp = 1.25, hold = 0.26, scare = 0.74, open = 0.57, lead = 0.32 },
	sunlion = { fam = "walk", flo = "roar", dur = 1.42, amp = 0.89, hold = 0.59, scare = 0.81, open = 0.92, lead = 0.48 },
	mountain_goat = { fam = "leap", flo = "stomp3", dur = 0.84, amp = 0.84, hold = 0.31, scare = 1.0, open = 0.39, lead = 0.24 },
	armadillo = { fam = "roll", flo = "stretch", dur = 1.26, amp = 0.96, hold = 0.25, scare = 0.79, open = 0.59, lead = 0.28 },
	canyon_condor = { fam = "swoop", flo = "flare", dur = 1.42, amp = 1.1, hold = 0.55, scare = 1.2, open = 0.53, lead = 0.21 },
	fennec = { fam = "pop", flo = "sniff", dur = 1.38, amp = 0.89, hold = 0.53, scare = 0.87, open = 0.31, lead = 0.05 },
	dune_scorpion = { fam = "skitter", flo = "shake", dur = 1.42, amp = 1.13, hold = 0.62, scare = 0.75, open = 0.58, lead = 0.3 },
	sand_wyrm = { fam = "rise", flo = "coil", dur = 1.64, amp = 1.21, hold = 0.62, scare = 1.13, open = 0.66, lead = 0.22 },
	toucan = { fam = "swoop", flo = "bow", dur = 1.27, amp = 1.2, hold = 0.57, scare = 1.08, open = 0.54, lead = 0.2 },
	jaguar = { fam = "pounce", flo = "coil", dur = 1.27, amp = 1.24, hold = 0.28, scare = 1.19, open = 0.54, lead = 0.3 },
	jungle_gorilla = { fam = "drop", flo = "roar", dur = 1.15, amp = 0.86, hold = 0.48, scare = 0.88, open = 0.65, lead = 0.09 },
	otter = { fam = "surge", flo = "twirl", dur = 1.22, amp = 1.16, hold = 0.42, scare = 0.71, open = 0.41, lead = 0.17 },
	crocodile = { fam = "surge", flo = "shake", dur = 1.17, amp = 1.15, hold = 0.27, scare = 0.7, open = 0.43, lead = 0.16 },
	marsh_hydra = { fam = "rise", flo = "wiggle", dur = 1.49, amp = 0.89, hold = 0.26, scare = 1.06, open = 0.6, lead = 0.22 },
	storm_ram = { fam = "burst", flo = "bow", dur = 0.85, amp = 1.16, hold = 0.32, scare = 0.91, open = 0.29, lead = 0.09 },
	thunder_eagle = { fam = "swoop", flo = "rear", dur = 1.43, amp = 1.0, hold = 0.51, scare = 0.82, open = 0.53, lead = 0.21 },
	storm_griffin = { fam = "swoop", flo = "roar", dur = 1.34, amp = 0.83, hold = 0.6, scare = 0.67, open = 0.48, lead = 0.22 },
	sea_turtle = { fam = "surge", flo = "sway", dur = 1.0, amp = 1.11, hold = 0.59, scare = 1.07, open = 0.42, lead = 0.15 },
	sea_lion = { fam = "surge", flo = "bounce", dur = 0.95, amp = 1.07, hold = 0.43, scare = 1.12, open = 0.43, lead = 0.15 },
	coral_wyvern = { fam = "surge", flo = "coil", dur = 1.17, amp = 1.03, hold = 0.27, scare = 0.58, open = 0.4, lead = 0.17 },
	reef_ray = { fam = "swoop", flo = "sway", dur = 1.49, amp = 1.03, hold = 0.29, scare = 0.74, open = 0.51, lead = 0.21 },
	hammer_shark = { fam = "surge", flo = "spin", dur = 1.08, amp = 1.2, hold = 0.44, scare = 0.86, open = 0.38, lead = 0.14 },
	abyss_leviathan = { fam = "surge", flo = "roar", dur = 0.99, amp = 1.22, hold = 0.33, scare = 0.98, open = 0.43, lead = 0.15 },
	ash_lizard = { fam = "skitter", flo = "twirl", dur = 1.57, amp = 1.19, hold = 0.27, scare = 1.09, open = 0.65, lead = 0.28 },
	ember_boar = { fam = "burst", flo = "sniff", dur = 0.84, amp = 1.24, hold = 0.24, scare = 0.88, open = 0.31, lead = 0.1 },
	lava_golem = { fam = "rise", flo = "stomp3", dur = 1.5, amp = 0.84, hold = 0.48, scare = 0.82, open = 0.64, lead = 0.19 },
	obsidian_crab = { fam = "skitter", flo = "bow", dur = 1.64, amp = 0.87, hold = 0.55, scare = 1.14, open = 0.58, lead = 0.33 },
	magma_rhino = { fam = "burst", flo = "lookaround", dur = 0.98, amp = 1.21, hold = 0.44, scare = 1.14, open = 0.28, lead = 0.11 },
	phoenix = { fam = "flash", flo = "flare", dur = 1.38, amp = 0.93, hold = 0.57, scare = 0.79, open = 0.48, lead = 0.1 },
	crystal_bat = { fam = "swoop", flo = "wiggle", dur = 1.2, amp = 0.91, hold = 0.44, scare = 1.01, open = 0.51, lead = 0.2 },
	amethyst_fox = { fam = "flash", flo = "bow", dur = 1.32, amp = 1.0, hold = 0.61, scare = 0.64, open = 0.5, lead = 0.09 },
	quartz_dragon = { fam = "rise", flo = "spin", dur = 1.28, amp = 0.92, hold = 0.61, scare = 0.93, open = 0.68, lead = 0.23 },
	arctic_hare = { fam = "leap", flo = "spin", dur = 1.09, amp = 0.85, hold = 0.4, scare = 1.15, open = 0.43, lead = 0.24 },
	lunar_wolf = { fam = "flash", flo = "roar", dur = 1.46, amp = 0.8, hold = 0.46, scare = 0.93, open = 0.46, lead = 0.1 },
	aurora_bear = { fam = "walk", flo = "rear", dur = 1.32, amp = 1.13, hold = 0.59, scare = 0.76, open = 0.83, lead = 0.45 },
	cloud_sheep = { fam = "leap", flo = "sniff", dur = 0.93, amp = 0.98, hold = 0.36, scare = 0.89, open = 0.38, lead = 0.2 },
	sky_stag = { fam = "leap", flo = "rear", dur = 0.91, amp = 0.9, hold = 0.47, scare = 0.8, open = 0.4, lead = 0.25 },
	sky_drake = { fam = "swoop", flo = "stomp3", dur = 1.18, amp = 1.02, hold = 0.6, scare = 1.15, open = 0.54, lead = 0.23 },
	dusk_panther = { fam = "pounce", flo = "sniff", dur = 1.61, amp = 1.01, hold = 0.47, scare = 1.1, open = 0.56, lead = 0.34 },
	shadow_mantis = { fam = "drop", flo = "twirl", dur = 1.23, amp = 0.86, hold = 0.43, scare = 0.75, open = 0.61, lead = 0.1 },
	void_behemoth = { fam = "rise", flo = "lookaround", dur = 1.32, amp = 1.11, hold = 0.34, scare = 0.76, open = 0.71, lead = 0.19 },
	comet_fox = { fam = "burst", flo = "spin", dur = 0.93, amp = 1.05, hold = 0.44, scare = 1.13, open = 0.29, lead = 0.09 },
	stellar_stag = { fam = "leap", flo = "bow", dur = 1.06, amp = 1.09, hold = 0.28, scare = 0.75, open = 0.42, lead = 0.21 },
	astral_dragon = { fam = "swoop", flo = "spin", dur = 1.48, amp = 1.06, hold = 0.31, scare = 0.67, open = 0.48, lead = 0.23 },
	watchful_meerkat = { fam = "pop", flo = "lookaround", dur = 1.27, amp = 0.86, hold = 0.27, scare = 0.87, open = 0.31, lead = 0.05 },
	savanna_ostrich = { fam = "burst", flo = "flare", dur = 0.77, amp = 0.96, hold = 0.41, scare = 0.8, open = 0.28, lead = 0.11 },
	amber_giraffe = { fam = "walk", flo = "stretch", dur = 1.42, amp = 1.14, hold = 0.31, scare = 0.71, open = 0.87, lead = 0.48 },
	rock_hyrax = { fam = "pop", flo = "stretch", dur = 1.13, amp = 0.92, hold = 0.57, scare = 0.6, open = 0.33, lead = 0.06 },
	canyon_roadrunner = { fam = "burst", flo = "bounce", dur = 0.98, amp = 0.97, hold = 0.55, scare = 0.58, open = 0.29, lead = 0.11 },
	redthorn_lizard = { fam = "skitter", flo = "sway", dur = 1.34, amp = 0.98, hold = 0.49, scare = 1.13, open = 0.6, lead = 0.34 },
	oasis_scarab = { fam = "rise", flo = "shake", dur = 1.28, amp = 0.99, hold = 0.23, scare = 0.61, open = 0.63, lead = 0.22 },
	dune_jerboa = { fam = "leap", flo = "twirl", dur = 1.08, amp = 0.98, hold = 0.43, scare = 1.25, open = 0.39, lead = 0.2 },
	mirage_camel = { fam = "walk", flo = "stomp3", dur = 1.39, amp = 1.01, hold = 0.49, scare = 0.58, open = 0.8, lead = 0.44 },
	jade_tapir = { fam = "walk", flo = "sniff", dur = 1.24, amp = 1.11, hold = 0.5, scare = 0.9, open = 0.9, lead = 0.5 },
	leafcutter_ant = { fam = "skitter", flo = "sniff", dur = 1.45, amp = 1.21, hold = 0.43, scare = 0.92, open = 0.62, lead = 0.3 },
	emerald_treefrog = { fam = "leap", flo = "bounce", dur = 0.92, amp = 1.12, hold = 0.46, scare = 0.58, open = 0.41, lead = 0.21 },
	mudskipper = { fam = "leap", flo = "wiggle", dur = 0.94, amp = 1.25, hold = 0.37, scare = 0.55, open = 0.37, lead = 0.25 },
	mangrove_fiddler = { fam = "skitter", flo = "wiggle", dur = 1.62, amp = 0.93, hold = 0.52, scare = 0.98, open = 0.57, lead = 0.32 },
	mangrove_flamingo = { fam = "walk", flo = "twirl", dur = 1.34, amp = 1.12, hold = 0.28, scare = 1.09, open = 0.85, lead = 0.48 },
	storm_stone_spider = { fam = "drop", flo = "shake", dur = 1.35, amp = 1.15, hold = 0.52, scare = 0.55, open = 0.61, lead = 0.1 },
	highland_yak = { fam = "stomp", flo = "bow", dur = 1.71, amp = 0.94, hold = 0.38, scare = 0.91, open = 0.99, lead = 0.48 },
	tempest_pterosaur = { fam = "swoop", flo = "sniff", dur = 1.52, amp = 0.95, hold = 0.37, scare = 0.93, open = 0.47, lead = 0.2 },
	spiral_hermit_crab = { fam = "skitter", flo = "lookaround", dur = 1.4, amp = 0.98, hold = 0.34, scare = 1.06, open = 0.65, lead = 0.28 },
	lagoon_pelican = { fam = "swoop", flo = "bounce", dur = 1.52, amp = 0.81, hold = 0.39, scare = 0.68, open = 0.55, lead = 0.23 },
	azure_horseshoe_crab = { fam = "skitter", flo = "hop2", dur = 1.29, amp = 1.04, hold = 0.23, scare = 1.11, open = 0.57, lead = 0.32 },
	pearl_nautilus = { fam = "flash", flo = "spin", dur = 1.29, amp = 0.97, hold = 0.4, scare = 0.84, open = 0.51, lead = 0.09 },
	coral_seahorse = { fam = "surge", flo = "stretch", dur = 0.94, amp = 1.2, hold = 0.39, scare = 0.58, open = 0.4, lead = 0.15 },
	reef_lobster = { fam = "skitter", flo = "stomp3", dur = 1.33, amp = 0.83, hold = 0.61, scare = 1.06, open = 0.61, lead = 0.34 },
	cinder_porcupine = { fam = "roll", flo = "shake", dur = 1.19, amp = 0.81, hold = 0.42, scare = 0.59, open = 0.57, lead = 0.34 },
	ash_anteater = { fam = "walk", flo = "coil", dur = 1.18, amp = 1.06, hold = 0.61, scare = 1.05, open = 0.8, lead = 0.49 },
	ember_mandrill = { fam = "drop", flo = "flare", dur = 1.1, amp = 1.23, hold = 0.29, scare = 0.61, open = 0.58, lead = 0.1 },
	furnace_stag_beetle = { fam = "skitter", flo = "flare", dur = 1.41, amp = 1.17, hold = 0.62, scare = 0.71, open = 0.6, lead = 0.27 },
	caldera_toad = { fam = "leap", flo = "flare", dur = 0.9, amp = 0.99, hold = 0.31, scare = 1.03, open = 0.43, lead = 0.21 },
	obsidian_pangolin = { fam = "roll", flo = "rear", dur = 1.46, amp = 1.01, hold = 0.59, scare = 0.79, open = 0.56, lead = 0.33 },
	prism_moth = { fam = "swoop", flo = "twirl", dur = 1.36, amp = 1.23, hold = 0.24, scare = 1.11, open = 0.53, lead = 0.2 },
	geode_mole = { fam = "pop", flo = "shake", dur = 1.15, amp = 0.84, hold = 0.4, scare = 1.09, open = 0.28, lead = 0.05 },
	crystal_anemone = { fam = "rise", flo = "flare", dur = 1.61, amp = 0.86, hold = 0.32, scare = 0.92, open = 0.63, lead = 0.22 },
	aurora_weasel = { fam = "pounce", flo = "twirl", dur = 1.53, amp = 1.09, hold = 0.55, scare = 0.95, open = 0.59, lead = 0.32 },
	moon_owl = { fam = "swoop", flo = "lookaround", dur = 1.47, amp = 0.93, hold = 0.53, scare = 0.63, open = 0.5, lead = 0.2 },
	tundra_muskox = { fam = "burst", flo = "sway", dur = 0.88, amp = 1.04, hold = 0.43, scare = 1.24, open = 0.27, lead = 0.09 },
	aether_ribbonfish = { fam = "swoop", flo = "coil", dur = 1.47, amp = 1.17, hold = 0.22, scare = 0.76, open = 0.52, lead = 0.21 },
	island_chameleon = { fam = "walk", flo = "lookaround", dur = 1.42, amp = 0.85, hold = 0.39, scare = 0.92, open = 0.91, lead = 0.43 },
	cloud_glider = { fam = "swoop", flo = "stretch", dur = 1.48, amp = 1.24, hold = 0.53, scare = 1.21, open = 0.48, lead = 0.18 },
	void_lamprey = { fam = "surge", flo = "sniff", dur = 1.08, amp = 0.92, hold = 0.35, scare = 0.62, open = 0.42, lead = 0.14 },
	gloom_sloth = { fam = "walk", flo = "sway", dur = 1.33, amp = 0.97, hold = 0.28, scare = 0.83, open = 0.92, lead = 0.51 },
	rift_axolotl = { fam = "surge", flo = "wiggle", dur = 1.2, amp = 1.13, hold = 0.29, scare = 1.09, open = 0.41, lead = 0.14 },
	nebula_tardigrade = { fam = "walk", flo = "wiggle", dur = 1.2, amp = 1.24, hold = 0.3, scare = 1.05, open = 0.9, lead = 0.46 },
	astral_starfish = { fam = "flash", flo = "twirl", dur = 1.26, amp = 1.13, hold = 0.44, scare = 0.63, open = 0.52, lead = 0.11 },
	orbital_jellyfish = { fam = "flash", flo = "sway", dur = 1.35, amp = 1.14, hold = 0.55, scare = 0.97, open = 0.53, lead = 0.1 },
	spring_strider = { fam = "leap", flo = "coil", dur = 0.93, amp = 0.82, hold = 0.51, scare = 0.63, open = 0.43, lead = 0.23 },
	copper_weevil = { fam = "skitter", flo = "stretch", dur = 1.7, amp = 0.99, hold = 0.24, scare = 1.05, open = 0.62, lead = 0.31 },
	gear_sentinel = { fam = "stomp", flo = "spin", dur = 1.61, amp = 1.04, hold = 0.53, scare = 0.75, open = 1.06, lead = 0.53 },
	magnet_tripod = { fam = "stomp", flo = "flare", dur = 2.03, amp = 1.21, hold = 0.23, scare = 0.99, open = 1.04, lead = 0.55 },
	iron_hound = { fam = "burst", flo = "stretch", dur = 0.87, amp = 0.94, hold = 0.61, scare = 1.21, open = 0.31, lead = 0.11 },
	clockwork_basilisk = { fam = "walk", flo = "spin", dur = 1.33, amp = 1.07, hold = 0.55, scare = 1.08, open = 0.81, lead = 0.5 },
	shelf_millipede = { fam = "skitter", flo = "bounce", dur = 1.57, amp = 1.2, hold = 0.26, scare = 0.61, open = 0.56, lead = 0.32 },
	peat_leech = { fam = "skitter", flo = "coil", dur = 1.36, amp = 0.96, hold = 0.5, scare = 1.07, open = 0.56, lead = 0.29 },
	lantern_slug = { fam = "walk", flo = "bounce", dur = 1.29, amp = 1.09, hold = 0.32, scare = 1.24, open = 0.81, lead = 0.48 },
	mycelium_bloomstalker = { fam = "rise", flo = "bounce", dur = 1.64, amp = 1.04, hold = 0.37, scare = 1.2, open = 0.61, lead = 0.19 },
	spore_marauder = { fam = "burst", flo = "hop2", dur = 0.82, amp = 1.03, hold = 0.47, scare = 1.22, open = 0.28, lead = 0.1 },
	cap_mantis = { fam = "drop", flo = "bow", dur = 1.35, amp = 1.09, hold = 0.39, scare = 0.96, open = 0.56, lead = 0.09 },
	fossil_trilobite = { fam = "skitter", flo = "spin", dur = 1.38, amp = 1.02, hold = 0.49, scare = 0.6, open = 0.56, lead = 0.34 },
	dune_ankylosaur = { fam = "stomp", flo = "wiggle", dur = 2.05, amp = 1.01, hold = 0.46, scare = 1.04, open = 1.02, lead = 0.47 },
	fossil_ceratopsian = { fam = "burst", flo = "wiggle", dur = 0.96, amp = 1.14, hold = 0.44, scare = 1.2, open = 0.29, lead = 0.1 },
	skeletal_colossus = { fam = "rise", flo = "roar", dur = 1.28, amp = 0.95, hold = 0.32, scare = 1.06, open = 0.63, lead = 0.2 },
	sand_reaper = { fam = "drop", flo = "stretch", dur = 1.11, amp = 0.9, hold = 0.27, scare = 0.7, open = 0.58, lead = 0.1 },
	bone_vulture = { fam = "swoop", flo = "shake", dur = 1.3, amp = 1.15, hold = 0.46, scare = 0.89, open = 0.53, lead = 0.22 },
	abyss_sea_urchin = { fam = "roll", flo = "twirl", dur = 1.29, amp = 1.0, hold = 0.46, scare = 0.56, open = 0.51, lead = 0.31 },
	citadel_cuttlefish = { fam = "surge", flo = "lookaround", dur = 0.94, amp = 1.13, hold = 0.29, scare = 0.86, open = 0.39, lead = 0.16 },
	cathedral_clam = { fam = "rise", flo = "bow", dur = 1.36, amp = 1.2, hold = 0.62, scare = 1.11, open = 0.67, lead = 0.19 },
	trench_angler = { fam = "flash", flo = "lookaround", dur = 1.23, amp = 1.16, hold = 0.26, scare = 0.84, open = 0.49, lead = 0.11 },
	pressure_colossus = { fam = "stomp", flo = "rear", dur = 1.59, amp = 0.99, hold = 0.42, scare = 0.96, open = 1.07, lead = 0.55 },
	abyss_octopus = { fam = "surge", flo = "flare", dur = 0.93, amp = 0.86, hold = 0.49, scare = 1.24, open = 0.4, lead = 0.17 },
	fulgurite_cricket = { fam = "leap", flo = "shake", dur = 0.85, amp = 1.12, hold = 0.56, scare = 0.88, open = 0.42, lead = 0.25 },
	rift_kangaroo = { fam = "leap", flo = "sway", dur = 1.03, amp = 1.17, hold = 0.4, scare = 0.56, open = 0.42, lead = 0.2 },
	thunder_centaur = { fam = "burst", flo = "rear", dur = 0.77, amp = 0.91, hold = 0.36, scare = 0.7, open = 0.29, lead = 0.11 },
	prism_revenant = { fam = "flash", flo = "rear", dur = 1.19, amp = 1.15, hold = 0.24, scare = 1.18, open = 0.49, lead = 0.11 },
	storm_harrier = { fam = "swoop", flo = "hop2", dur = 1.34, amp = 0.87, hold = 0.31, scare = 1.05, open = 0.55, lead = 0.18 },
	rift_serpent = { fam = "rise", flo = "twirl", dur = 1.43, amp = 1.13, hold = 0.34, scare = 0.72, open = 0.62, lead = 0.2 },
	caldera_tarsier = { fam = "pop", flo = "bow", dur = 1.17, amp = 1.02, hold = 0.41, scare = 1.19, open = 0.3, lead = 0.05 },
	ember_salamander = { fam = "skitter", flo = "rear", dur = 1.45, amp = 0.96, hold = 0.27, scare = 0.94, open = 0.59, lead = 0.32 },
	magma_hippo = { fam = "stomp", flo = "stretch", dur = 1.95, amp = 0.99, hold = 0.24, scare = 1.14, open = 1.05, lead = 0.5 },
	lava_dragonfly = { fam = "flash", flo = "wiggle", dur = 1.45, amp = 1.16, hold = 0.32, scare = 0.72, open = 0.47, lead = 0.1 },
	volcanic_wyrm = { fam = "rise", flo = "sway", dur = 1.28, amp = 0.84, hold = 0.41, scare = 1.21, open = 0.7, lead = 0.19 },
	primordial_titan = { fam = "drop", flo = "stomp3", dur = 1.42, amp = 1.2, hold = 0.49, scare = 0.61, open = 0.62, lead = 0.1 },
}
-- END V61 REVEAL

local DEFAULT_SPEC={fam="walk",flo="shake",dur=1.3,amp=1,hold=.4,scare=.8,open=.7,lead=.45}

function Stage.Spec(id: string): any
 return REVEAL[id] or DEFAULT_SPEC
end

-- Размеры зверя в мире: bounds/w/h/len умножаются на s (модель в сцене тоже увеличена или уменьшена на s)
function Stage.ScaleAnimal(animal: any,s: number): any
 if not animal then return nil end
 local b=animal.bounds
 return {bounds={{b[1][1]*s,b[1][2]*s,b[1][3]*s},{b[2][1]*s,b[2][2]*s,b[2][3]*s}},w=animal.w*s,h=animal.h*s,len=(animal.len or 0)*s}
end

-- Во сколько раз увеличить куст, чтобы в нём мог спрятаться этот зверь (от 1 до 4,5; кубики куста растут вместе)
function Stage.CoverScale(cover: any,animal: any?): number
 if not animal then return 1 end
 local size=cover.bounds.size
 local byH=animal.h*.7/size[2]
 local byW=(animal.w*1.1+2)/size[1]
 local byL=(animal.len or 0)*.4/size[3]
 return math.clamp(math.max(1,byH,byW,byL),1,4.5)
end

function Stage.Plan(pos: Vector3,viewer: Vector3,cover: any,animal: any?,coverScale: number?): any
 local cs=coverScale or 1
 local toward=Vector3.new(viewer.X-pos.X,0,viewer.Z-pos.Z)
 local direction=if toward.Magnitude>.001 then toward.Unit else Vector3.zAxis
 local depth=cover.bounds.size[3]*cs
 local front=if animal then math.max(.2,-animal.bounds[1][3])else 1
 local rear=if animal then math.max(.2,animal.bounds[2][3])else 1
 local width=if animal then animal.w else 2
 -- The end pose remains exactly at the original catch point. The curtain is
 -- behind it, so even a long tail clears the opening instead of clipping it.
 local center=pos-direction*(depth*.5+rear+.65)
 local start=center-direction*(depth*.5+front+.55)
 return {Direction=direction,Center=center,Start=start,Finish=pos,Focus=center:Lerp(pos,.5),Frame=CFrame.lookAt(center,center+direction),Spread=math.max(cover.bounds.size[1]*.48*cs,width*.62+1.4),Height=math.max(if animal then animal.h else 2,cover.bounds.size[2]*cs*.55),Duration=1.1,CoverScale=cs}
end

-- Старый выход «просто пройти» (запасной путь, если у вида нет сценария)
function Stage.Walk(rig: any,plan: any)
 local t0=os.clock();local duration=plan.Duration
 rig.model:SetAttribute("V15_Emerging",true);rig.model:SetAttribute("V15_EmergenceScale",rig.model:GetScale())
 rig:play("walk",1)
 local old=rig.onUpdate
 rig.onUpdate=function(self: any,_dt: number)
  local u=math.clamp((os.clock()-t0)/duration,0,1)
  local position=plan.Start:Lerp(plan.Finish,u)
  self.cf=CFrame.lookAt(position,position+plan.Direction)
 end
 while rig.alive and rig.model.Parent and os.clock()-t0<duration do RunService.RenderStepped:Wait()end
 if rig.alive and rig.model.Parent then
  rig.onUpdate=old
  rig.cf=CFrame.lookAt(plan.Finish,plan.Finish+plan.Direction);rig.root.CFrame=rig.cf
  rig:play("stand",1);rig.model:SetAttribute("V15_Emerging",false)
 end
end

---------------------------------------------------------------------
-- Манеры выхода. Каждая получает долю времени u (0..1) и контекст c и возвращает
-- положение корня, наклон (+ нос вверх), крен, поворот и состояние движения.
-- c: S старт за кустом, C центр куста, F точка поимки, D к игроку, SD вбок, H рост, len длина, wid ширина, hs = min(H,10), amp размах вида
---------------------------------------------------------------------
type Pose=(number,any)->(Vector3,number,number,number,string)

local function lerpPos(c: any,e: number): Vector3
 return c.S:Lerp(c.F,e)
end

local FAMILIES: {[string]: Pose}={}

-- осторожно выглядывает за краем куста, замирает и выходит
FAMILIES.walk=function(u: number,c: any): (Vector3,number,number,number,string)
 local e:number
 if u<.40 then e=.35*ease(u/.40) elseif u<.58 then e=.35 else e=.35+.65*ease((u-.58)/.42) end
 local peek=u>=.40 and u<.58
 local yaw=if peek then .22*math.sin((u-.40)/.18*TAU) else 0
 return lerpPos(c,e),0,0,yaw,if peek then "stand" else "walk"
end

-- выпрыгивает дугой через раскрывшийся куст
FAMILIES.leap=function(u: number,c: any): (Vector3,number,number,number,string)
 local apex=c.hs*(.55+.45*c.amp)+1.2
 return lerpPos(c,ease(u))+Vector3.new(0,math.sin(math.pi*u)*apex,0),.5*math.cos(math.pi*u)*c.amp*.8*(1-ease((u-.8)/.2)),0,0,"hop"
end

-- вылетает рывком с перелётом и тормозит юзом
FAMILIES.burst=function(u: number,c: any): (Vector3,number,number,number,string)
 local over=(c.len*.35+c.H*.2)*c.amp
 local split=.62
 if u<split then
  return c.S:Lerp(c.F+c.D*over,outc(u/split)),0,0,0,"run"
 end
 local k=ease((u-split)/(1-split))
 return (c.F+c.D*over):Lerp(c.F,k),.22*math.sin(k*math.pi),0,0,if k<.7 then "walk" else "stand"
end

-- выбирается из-под земли, отряхивается и выходит
FAMILIES.rise=function(u: number,c: any): (Vector3,number,number,number,string)
 if u<.5 then
  local k=u/.5
  local depth=c.H*1.05+.4
  local shake=(1-k)*.06*c.H*math.sin(u*90)
  return c.C+Vector3.new(0,-depth*(1-outc(k)),0)+c.SD*shake,.15*(1-k),.08*math.sin(u*70)*(1-k),0,"stand"
 end
 return c.C:Lerp(c.F,ease((u-.5)/.5)),0,0,0,"walk"
end

-- падает сверху и приземляется с отскоком
FAMILIES.drop=function(u: number,c: any): (Vector3,number,number,number,string)
 local land=.5
 if u<land then
  local k=u/land
  return c.F+Vector3.new(0,(c.H*1.6+9)*(1-k*k),0),-.35*k,0,(1-k)*2.2*c.amp,"stand"
 end
 local k=(u-land)/(1-land)
 return c.F+Vector3.new(0,math.sin(k*math.pi)*c.hs*.12*(1-k),0),-.35*(1-k),0,0,"stand"
end

-- влетает из-за куста по дуге сверху и садится
FAMILIES.swoop=function(u: number,c: any): (Vector3,number,number,number,string)
 local p0=c.C-c.D*(c.len*.9+3)+Vector3.new(0,c.H*1.8+3,0)
 local p1=c.C+Vector3.new(0,c.H*1.4+1.5,0)
 local p2=c.F
 local t=u
 local a=(1-t)*(1-t);local b=2*(1-t)*t;local d=t*t
 local pos=p0*a+p1*b+p2*d+c.SD*(math.sin(u*math.pi*2)*c.wid*.6*(1-u))
 local vel=(p1-p0)*(2*(1-t))+(p2-p1)*(2*t)
 local pitch=math.atan2(vel.Y,math.max(.1,vel:Dot(c.D)))*(1-ease((u-.75)/.25))
 return pos,pitch,0,0,if u<.85 then "fly" else "stand"
end

-- выныривает: высокая дуга с поворотом и брызгами
FAMILIES.surge=function(u: number,c: any): (Vector3,number,number,number,string)
 local apex=c.hs*(.9+.6*c.amp)+2
 local roll=if c.amp>1.02 then TAU*ease(u) else 0
 return lerpPos(c,ease(u))+Vector3.new(0,math.sin(math.pi*u)*apex,0),.7*math.cos(math.pi*u)*.8*(1-ease((u-.8)/.2)),roll,0,"swim"
end

-- крадётся сбоку, замирает и бросается
FAMILIES.pounce=function(u: number,c: any): (Vector3,number,number,number,string)
 local sgn=if c.amp>1.02 then 1 else -1
 local p0=c.C+c.SD*((c.wid*.8+.8)*sgn)
 local reach=p0+c.D*(.8*c.wid)
 if u<.45 then
  local k=u/.45
  return p0+c.D*(k*.8*c.wid),-.18,0,0,if k<.8 then "walk" else "stand"
 elseif u<.72 then
  local k=(u-.45)/.27
  local pitch=-.18*(1-k)+.30*math.sin(math.pi*k)-.25*k*k
  return reach:Lerp(c.F,ease(k))+Vector3.new(0,math.sin(math.pi*k)*c.hs*.6,0),pitch,0,0,"run"
 end
 local k=ease((u-.72)/.28)
 return c.F,-.25*(1-k),0,0,"stand"
end

-- выкатывается шаром и раскручивается
FAMILIES.roll=function(u: number,c: any): (Vector3,number,number,number,string)
 local split=.74
 local dist=(c.S-c.F).Magnitude
 local turns=math.max(1,math.floor(dist/(math.pi*math.max(c.H,.6))+.5))
 local lift=math.max(0,(c.len-c.H)*.5)
 if u<split then
  local k=u/split
  return c.S:Lerp(c.F,k)+Vector3.new(0,lift,0),-turns*TAU*k,0,0,"stand"
 end
 local k=ease((u-split)/(1-split))
 return c.F+Vector3.new(0,lift*(1-k)+math.sin(k*math.pi)*c.hs*.25,0),-turns*TAU,0,0,"stand"
end

-- перебежками: рывок, остановка, рывок, с зигзагом
FAMILIES.skitter=function(u: number,c: any): (Vector3,number,number,number,string)
 local k=u*5
 local i=math.min(math.floor(k),4)
 local f=k-math.floor(k)
 local mv=ease(math.clamp(f/.6,0,1))
 local e=if u>=1 then 1 else (i+mv)/5
 local zig=math.sin((i+mv)*math.pi)*(1-e)*c.wid*.7*c.amp
 local yaw=.35*math.cos((i+mv)*math.pi)*(1-u)
 return lerpPos(c,e)+c.SD*zig,0,0,yaw,if f<.6 then "walk" else "stand"
end

-- тяжёлыми шагами: на каждом шаге земля вздрагивает
FAMILIES.stomp=function(u: number,c: any): (Vector3,number,number,number,string)
 local bob=math.abs(math.sin(u*math.pi*3))*c.H*.03
 return lerpPos(c,ease(u)*.6+u*.4)+Vector3.new(0,bob,0),.02*math.sin(u*math.pi*6),0,0,"walk"
end

-- выскакивает из куста пружиной и оседает
FAMILIES.pop=function(u: number,c: any): (Vector3,number,number,number,string)
 local h=math.min(c.H,10)
 if u<.35 then
  local k=outc(u/.35)
  return c.C+Vector3.new(0,-h*1.05+h*1.75*k,0),.25*k,0,0,"stand"
 elseif u<.6 then
  local k=ease((u-.35)/.25)
  return c.C+Vector3.new(0,h*.7*(1-k),0),.25*(1-k),0,0,"stand"
 elseif u<.75 then
  local k=(u-.6)/.15
  return c.C+Vector3.new(0,math.sin(k*math.pi)*h*.15,0),0,0,0,"stand"
 end
 return c.C:Lerp(c.F,ease((u-.75)/.25)),0,0,0,"walk"
end

-- возникает со вспышкой и плывёт вперёд, чуть паря
FAMILIES.flash=function(u: number,c: any): (Vector3,number,number,number,string)
 return c.C:Lerp(c.F,ease(u))+Vector3.new(0,math.sin(math.pi*u)*c.hs*.35,0),.1*math.sin(u*TAU),0,.5*math.sin(u*TAU)*(1-u),if u<.8 then "walk" else "stand"
end

-- События для эффектов (доля времени, вид, где): вызывают hooks.fx(вид, точка, сила)
local FAMILY_EVENTS: {[string]: {{any}}}={
 walk={},
 leap={{.02,"dust","S"},{.98,"land","F"}},
 burst={{.02,"dust","C"},{.62,"skid","F"}},
 rise={{0,"dig","C"},{.5,"dust","C"}},
 drop={{.5,"land","F"}},
 swoop={{.05,"flare","C"},{.9,"dust","F"}},
 surge={{.02,"splash","C"},{.97,"splash","F"}},
 pounce={{.45,"dust","P"},{.72,"land","F"}},
 roll={{.02,"dust","C"},{.74,"dust","F"}},
 skitter={{0,"dust","C"}},
 stomp={{.33,"step","P"},{.66,"step","P"},{.98,"step","F"}},
 pop={{0,"pop","C"},{.35,"pop","C"}},
 flash={{0,"flash","C"}},
}

---------------------------------------------------------------------
-- Фирменные жесты после выхода: (y, наклон, крен, поворот); в начале и в конце всё равно ноль
---------------------------------------------------------------------
local function env(u: number): number return math.sin(math.pi*u) end
local FLO_DUR: {[string]: number}={rear=1.3,shake=1.1,bow=1.2,spin=1.1,hop2=1.0,stomp3=1.3,lookaround=1.6,flare=1.4,wiggle=1.0,roar=1.5,sniff=1.4,stretch=1.5,coil=1.6,bounce=1.2,sway=1.8,twirl=1.3}
local FLO: {[string]: (number,any)->(number,number,number,number)}={}
FLO.rear=function(u: number,c: any): (number,number,number,number) local e=env(u)^.6 return c.hs*.10*e,.55*c.amp*e,0,0 end
FLO.shake=function(u: number,c: any): (number,number,number,number) local e=env(u) return 0,0,.09*c.amp*math.sin(u*TAU*7)*e,.05*math.sin(u*TAU*5+1)*e end
FLO.bow=function(u: number,c: any): (number,number,number,number) local e=env(u) return -c.hs*.02*e,-.30*c.amp*e,0,0 end
FLO.spin=function(u: number,c: any): (number,number,number,number) return math.sin(math.pi*u)*c.hs*.12,0,0,TAU*ease(u) end
FLO.hop2=function(u: number,c: any): (number,number,number,number) return math.abs(math.sin(u*math.pi*2))*c.hs*.22*c.amp,0,0,0 end
FLO.stomp3=function(u: number,c: any): (number,number,number,number) return math.abs(math.sin(u*math.pi*3))*c.hs*.10*c.amp,0,0,0 end
FLO.lookaround=function(u: number,c: any): (number,number,number,number) local e=env(u)^.5 return 0,0,0,.7*c.amp*math.sin(u*TAU)*e end
FLO.flare=function(u: number,c: any): (number,number,number,number) local e=env(u) return c.hs*.20*e,.30*c.amp*e,.12*math.sin(u*TAU*3)*e,0 end
FLO.wiggle=function(u: number,c: any): (number,number,number,number) local e=env(u) return 0,0,.06*math.sin(u*TAU*8+1)*e,.16*c.amp*math.sin(u*TAU*8)*e end
FLO.roar=function(u: number,c: any): (number,number,number,number) local a=ease(u*4) local b=ease((u-.6)/.4) return 0,.42*c.amp*a*(1-b),0,0 end
FLO.sniff=function(u: number,c: any): (number,number,number,number) local e=env(u) return 0,-.14*c.amp*math.abs(math.sin(u*math.pi*3))*e,0,.2*math.sin(u*TAU*2)*e end
FLO.stretch=function(u: number,c: any): (number,number,number,number) local e=env(u) return 0,.22*c.amp*math.sin(u*TAU)*e,0,0 end
FLO.coil=function(u: number,c: any): (number,number,number,number) local e=env(u) return c.hs*.05*math.sin(u*TAU*3)*e,0,.10*math.sin(u*TAU*1.5+.5)*e,.5*c.amp*math.sin(u*TAU*1.5)*e end
FLO.bounce=function(u: number,c: any): (number,number,number,number) return c.hs*.35*c.amp*math.abs(math.sin(u*math.pi*3))*(1-u),0,0,0 end
FLO.sway=function(u: number,c: any): (number,number,number,number) local e=env(u) return 0,0,.14*c.amp*math.sin(u*TAU*1.5)*e,.06*math.sin(u*TAU)*e end
FLO.twirl=function(u: number,c: any): (number,number,number,number) return 0,0,0,.9*math.pi*c.amp*math.sin(math.pi*u) end

local FLO_EVENTS: {[string]: {{any}}}={
 roar={{.2,"roar","F"}},
 flare={{.45,"flare","F"}},
 stomp3={{.33,"step","F"},{.66,"step","F"},{.99,"step","F"}},
 hop2={{.5,"dust","F"},{.99,"dust","F"}},
 spin={{.5,"dust","F"}},
 bounce={{.33,"dust","F"},{.66,"dust","F"}},
}

local function runEvents(list: {{any}}?,fired: {[number]: boolean},u: number,hooks: any,c: any,pos: Vector3,strength: number)
 if not list or not hooks or not hooks.fx then return end
 for i,e in ipairs(list) do
  if not fired[i] and u>=(e[1] :: number) then
   fired[i]=true
   local where=e[3]
   local at=if where=="S" then c.S elseif where=="C" then c.C elseif where=="F" then c.F else pos
   hooks.fx(e[2],at,strength)
  end
 end
end

-- Выход зверя из куста по сценарию его вида. Блокирует до конца выхода (звери остаётся в точке поимки);
-- затем в отдельной нити играет фирменный жест и сам возвращает зверя в исходную стойку.
-- hooks (необязательно): fx(kind,pos,strength) для пыли, брызг, толчков; fast = true сокращает выход и пропускает жест.
function Stage.Emerge(rig: any,plan: any,spec: any,hooks: any?)
 local fam=FAMILIES[spec.fam] or FAMILIES.walk
 local H=math.max(.5,rig.h)
 local sc=rig.model:GetScale()
 local D=plan.Direction
 local c={S=plan.Start,F=plan.Finish,C=plan.Center,D=D,SD=Vector3.new(-D.Z,0,D.X),H=H,hs=math.min(H,10),
  len=((rig.model:GetAttribute("Len") or H) :: number)*sc,wid=((rig.model:GetAttribute("Width") or H*.5) :: number)*sc,amp=spec.amp}
 local py=math.min(H,12)*.5
 local strength=spec.scare*math.clamp(H/4,.5,2)
 local fast=hooks~=nil and hooks.fast==true
 local dur=if fast then spec.dur*.55 else spec.dur
 -- вращение вокруг центра тела, а не ступней
 local function assemble(pos: Vector3,pitch: number,roll: number,yaw: number): CFrame
  return CFrame.lookAt(pos,pos+D)*CFrame.new(0,py,0)*CFrame.Angles(pitch,yaw,roll)*CFrame.new(0,-py,0)
 end
 rig.model:SetAttribute("V15_Emerging",true);rig.model:SetAttribute("V15_EmergenceScale",sc)
 local old=rig.onUpdate
 local state=""
 local fired: {[number]: boolean}={}
 local t0=os.clock()
 local events=FAMILY_EVENTS[spec.fam]
 local function frame(): number
  local u=math.clamp((os.clock()-t0)/dur,0,1)
  local pos,pitch,roll,yaw,st=fam(u,c)
  rig.cf=assemble(pos,pitch,roll,yaw)
  if st~=state then state=st;rig:play(st,1) end
  runEvents(events,fired,u,hooks,c,pos,strength)
  return u
 end
 frame()
 rig.root.CFrame=rig.cf
 rig.onUpdate=function(_self: any,_dt: number) frame() end
 while rig.alive and rig.model.Parent and os.clock()-t0<dur do RunService.RenderStepped:Wait()end
 if not (rig.alive and rig.model.Parent) then return end
 frame() -- последний кадр с u = 1: события в конце выхода (приземление, всплеск, последний шаг) обязательно срабатывают
 local rest=CFrame.lookAt(plan.Finish,plan.Finish+D)
 rig.onUpdate=old
 rig.cf=rest;rig.root.CFrame=rest
 rig:play("stand",1)
 local flourish=not (fast or (hooks~=nil and hooks.noFlourish==true))
 -- пока зверь выходит и играет жест, он обновляется каждый кадр (иначе у далёких великанов было бы 8-15 кадров/с)
 if not flourish then rig.model:SetAttribute("V15_Emerging",false) return end
 -- фирменный жест
 local flo=FLO[spec.flo]
 if not flo then return end
 task.spawn(function()
  local fd=(FLO_DUR[spec.flo] or 1.2)*(.9+.2*math.clamp(spec.dur,.7,1.6)/1.3)
  local t1=os.clock()
  local firedF: {[number]: boolean}={}
  local floEvents=FLO_EVENTS[spec.flo]
  local mine=function(self: any,_dt: number)
   local u=math.clamp((os.clock()-t1)/fd,0,1)
   local y,pitch,roll,yaw=flo(u,c)
   self.cf=assemble(plan.Finish+Vector3.new(0,y,0),pitch,roll,yaw)
   runEvents(floEvents,firedF,u,hooks,c,plan.Finish,strength)
  end
  rig.onUpdate=mine
  while rig.alive and rig.model.Parent and rig.onUpdate==mine and os.clock()-t1<fd do RunService.RenderStepped:Wait()end
  -- если сцена уже взяла зверя себе (побег), его движение не трогаем
  if rig.alive and rig.model.Parent then rig.model:SetAttribute("V15_Emerging",false) end
  if rig.alive and rig.model.Parent and rig.onUpdate==mine then
   runEvents(floEvents,firedF,1,hooks,c,plan.Finish,strength)
   rig.onUpdate=nil
   rig.cf=rest;rig.root.CFrame=rest
  end
 end)
end

return Stage
