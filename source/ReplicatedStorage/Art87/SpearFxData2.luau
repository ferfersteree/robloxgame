-- V87: эффекты копий 24-46 по docs/concepts_v86/fx_table.md (данные для Art87/SpearFx87)
-- Схема: docs/concepts_v87/roblox/SPEAR_FX_SCHEMA.md. Локальные функции ниже только собирают обычные таблицы.

local G = { 0, -27, 0 }

local function merge(t, o)
	if o then
		for k, v in pairs(o) do
			t[k] = v
		end
	end
	return t
end

-- эмиттер в руке
local function I(tex, c0, c1, s0, rate, o)
	return merge({
		at = "tip", texture = tex, c0 = c0, c1 = c1, s0 = s0, s1 = s0, t0 = 0.2, t1 = 1,
		rate = rate, life = { 1.4, 1.6 }, speed = { 0.2, 0.3 }, spread = 180, dir = "out",
	}, o)
end

-- блик-звёздочка в руке
local function glint(c, rate, s, o)
	return I("sparkle", c, c, s or 0.15, rate, merge({ t0 = 0, t1 = 1, life = { 0.5, 0.5 }, light = 1 }, o))
end

-- эмиттер на летящем копье
local function F(tex, c0, c1, s0, s1, rate, o)
	return merge({
		at = "trail", texture = tex, c0 = c0, c1 = c1, s0 = s0, s1 = s1, t0 = 0.2, t1 = 1,
		rate = rate, life = { 0.9, 1 }, speed = { 3, 5 }, spread = 30, dir = "back",
	}, o)
end

-- кольцо полёта
-- s0/s1 - множители размера (как в таблице x0.5 -> x2.1), k - поправка на родной размер меша
local function fring(mesh, color, every, travel, s1, k, s0)
	k = k or 1
	return { mesh = mesh, color = color, every = every or 0.33, s0 = (s0 or 0.5) * k, s1 = (s1 or 2.1) * k, travel = travel or 6.5, life = 1, a0 = 0.2 }
end

-- всплеск частиц при ударе
local function B(tex, c0, c1, n, s0, s1, speed, life, o)
	return merge({
		at = "ground", texture = tex, c0 = c0, c1 = c1, s0 = s0, s1 = s1, t0 = 0.1, t1 = 1,
		count = n, life = life, speed = speed, spread = 45, dir = "up",
	}, o)
end

-- меш/шар при ударе
local function M(mesh, color, o)
	return merge({
		mesh = mesh, color = color, neon = true, count = 1, r = 0, t0 = 0, t1 = 0.4,
		size0 = { 0.3, 0.3, 0.3 }, size1 = { 1, 1, 1 }, a0 = 0, a1 = 1, easing = "Quad",
	}, o)
end

-- вспышка-сфера (r в студах)
local function flash(color, r0, r1, a0, t1)
	return M("ball", color, {
		t1 = t1 or 0.4, size0 = { r0 * 2, r0 * 2, r0 * 2 }, size1 = { r1 * 2, r1 * 2, r1 * 2 },
		a0 = a0 or 0.3, a1 = 1, y0 = 0.8, y1 = 0.8,
	})
end

-- плоское кольцо-меш по земле (d - диаметр)
local function ring(mesh, color, d0, d1, t0, t1, o)
	return merge(M(mesh, color, { t0 = t0, t1 = t1, size0 = { d0, 0.1, d0 }, size1 = { d1, 0.1, d1 }, y0 = 0.1, y1 = 0.1 }), o)
end

-- плоский светящийся диск/пятно по земле
local function disc(color, d0, d1, a0, t0, t1, o)
	return merge(M("ball", color, {
		t0 = t0, t1 = t1, size0 = { d0, 0.05, d0 }, size1 = { d1, 0.05, d1 }, a0 = a0, a1 = 1, y0 = 0.05, y1 = 0.05,
	}), o)
end

-- трещины по земле (Neon-Part)
local function cracks(color, n, len, t0, t1, o)
	return merge(M("part", color, {
		count = n, r = 0.4, t0 = t0, t1 = t1, size0 = { 0.1, 0.1, 0.2 }, size1 = { len, 0.1, 0.1 },
		a0 = 0, a1 = 1, y0 = 0.05, y1 = 0.05, easing = "Quad",
	}), o)
end

-- клубы дыма/пыли/брызг вверх
local function puff(color, n, delay, s1, life, o)
	return B("smoke", color, color, n, 0.5, s1, { 1.5, 3 }, { life * 0.8, life }, merge({
		delay = delay, t0 = 0.2, t1 = 1, spread = 40, drag = 1,
	}, o))
end

-- звёздочки-вспышки
local function stars(color, n, delay, life, o)
	return B("star", color, color, n, 0.35, 0.35, { 2, 5 }, { life * 0.8, life }, merge({
		delay = delay, t0 = 0, t1 = 1, spread = 180, dir = "out", light = 1,
	}, o))
end

return {
	-- 24 ---------------------------------------------------------------------
	tide_crest = {
		idle = {
			emitters = {
				I("bubble", "#E2FBFF", "#E2FBFF", 0.16, 5, { life = { 1.5, 1.5 }, dir = "up", accel = { 0, 0.8, 0 } }),
				glint("#C8FBFF", 2),
			},
			light = { color = "#6FF0FF", range = 4, brightness = 0.6 },
		},
		flight = {
			emitters = {
				F("smoke", "#F2FDFF", "#F2FDFF", 0.3, 0, 12, { smid = 1.4, t0 = 0.3, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 25 }),
				F("crystal", "#BFEEFF", "#BFEEFF", 0.34, 0.34, 8, { speed = { 10, 13 }, spread = 8, rot = 540, t0 = 0, light = 1 }),
				F("drop", "#6FF0FF", "#6FF0FF", 0.14, 0.14, 6, { speed = { 4, 4 }, t0 = 0, light = 1 }),
			},
			rings = { fring("water_ring", "#6FF0FF", 0.33, 7) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#6FF0FF", range = 8, brightness = 3, t1 = 0.7 },
			bursts = {
				B("drop", "#6FF0FF", "#F4FCFF", 16, 0.2, 0.2, { 7, 12 }, { 0.8, 1.2 }, { t0 = 0, spread = 60, accel = G, delay = 0 }),
				B("crystal", "#BFEEFF", "#BFEEFF", 10, 0.3, 0.3, { 6, 12 }, { 0.8, 1.2 }, { t0 = 0, spread = 70, accel = G, rot = 300, light = 1 }),
				puff("#F2FDFF", 6, 0.1, 1.8, 1.2, { t0 = 0.3, speed = { 1.5, 2.5 }, dir = "up" }),
			},
			meshes = {
				flash("#D8FFFF", 0.5, 1.2, 0.4, 0.4),
				-- 9 завитков-волн дугой перед копьём; обрушиваются к 1.0 с
				M("wave_slab", "#1F7FD6", { count = 9, r = 1.25, neon = false, t0 = 0, t1 = 0.2, size0 = { 0.87, 0.1, 0.64 }, size1 = { 0.87, 1.78, 0.64 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.8 }),
				-- пенные шапки ныряют к центру
				M("ball", "#F4FCFF", { count = 9, r = 1.25, t0 = 0, t1 = 1.0, size0 = { 0.4, 0.4, 0.4 }, size1 = { 0.05, 0.05, 0.05 }, a0 = 0, a1 = 0.6, y0 = 1.5, y1 = 0.3, easing = "Quad" }),
				ring("foam_ring", "#F0FFFF", 1.2, 5.2, 0, 1.2, { a0 = 0, a1 = 1 }),
				ring("water_ring", "#6FF0FF", 1.2, 4.6, 0, 0.53),
				ring("water_ring", "#6FF0FF", 1.2, 3.8, 0.2, 0.73),
			},
		},
	},

	-- 25 ---------------------------------------------------------------------
	abyss_anchor = {
		idle = {
			emitters = {
				I("bubble", "#D8FBFF", "#D8FBFF", 0.16, 5, { life = { 1.6, 1.6 }, dir = "up", accel = { 0, 0.8, 0 } }),
				glint("#C8FFF4", 2),
			},
			light = { color = "#58FFE0", range = 5, brightness = 0.8 },
		},
		flight = {
			emitters = {
				F("bubble", "#D8FBFF", "#D8FBFF", 0.15, 0, 12, { smid = 0.4, speed = { 3, 3 }, spread = 30, t0 = 0.2 }),
				F("shard", "#3FAE9C", "#3FAE9C", 0.3, 0.3, 8, { speed = { 10, 13 }, spread = 8, rot = 360, t0 = 0 }),
				-- звенья цепи (эмиттер-приближение)
				F("shard", "#53647A", "#53647A", 0.3, 0, 5, { smid = 0.4, speed = { 10, 13 }, spread = 8, rot = 360, t0 = 0 }),
			},
			rings = { fring("water_ring", "#58FFE0", 0.33, 7) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#58FFE0", range = 9, brightness = 4, t1 = 0.7 },
			bursts = {
				B("drop", "#6FC8EE", "#6FC8EE", 12, 0.2, 0.2, { 7, 12 }, { 0.8, 1.2 }, { t0 = 0, spread = 60, accel = G }),
				B("bubble", "#D8FBFF", "#D8FBFF", 8, 0.3, 0.3, { 2, 4 }, { 0.8, 0.8 }, { delay = 0.03, spread = 30, t0 = 0.2 }),
				puff("#EAFFFF", 5, 0.1, 1.8, 1.4, { t0 = 0.3 }),
			},
			meshes = {
				flash("#C8FFF4", 0.5, 1.4, 0.3, 0.4),
				ring("shock_ring", "#58FFE0", 1.13, 6.0, 0, 0.47),
				ring("shock_ring", "#58FFE0", 1.13, 4.8, 0.1, 0.57),
				ring("shock_ring", "#58FFE0", 1.13, 3.6, 0.2, 0.67),
				-- корона из 12 водяных шипов
				M("crown_spike", "#6FC8EE", { count = 12, r = 0.78, t0 = 0, t1 = 0.33, size0 = { 0.2, 0.1, 0.1 }, size1 = { 0.6, 1.6, 0.26 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.62 }),
				-- падающие звенья цепи
				M("chain_link", "#53647A", { count = 4, r = 1.4, neon = false, t0 = 0.03, t1 = 0.5, size0 = { 0.3, 0.3, 0.07 }, size1 = { 0.5, 0.54, 0.12 }, a0 = 0, a1 = 0, y0 = 3.4, y1 = 0.2, easing = "Bounce", hold = 0.8 }),
				M("chain_link", "#2E3A4E", { count = 4, r = 2.0, neon = false, t0 = 0.1, t1 = 0.55, size0 = { 0.3, 0.3, 0.07 }, size1 = { 0.5, 0.54, 0.12 }, a0 = 0, a1 = 0, y0 = 3.0, y1 = 0.2, easing = "Bounce", hold = 0.7 }),
			},
		},
	},

	-- 26 ---------------------------------------------------------------------
	leviathan_fang = {
		idle = {
			emitters = {
				I("snow", "#D8F6FF", "#D8F6FF", 0.14, 5, { life = { 1.6, 1.6 }, accel = { 0, -0.3, 0 } }),
				glint("#E6FCFF", 2),
			},
			light = { color = "#6FF0FF", range = 5, brightness = 0.8 },
		},
		flight = {
			emitters = {
				F("shard", "#CDF1FF", "#CDF1FF", 0.4, 0.4, 10, { speed = { 10, 13 }, spread = 8, rot = 540, t0 = 0, light = 1 }),
				F("smoke", "#D8F6FF", "#D8F6FF", 0.3, 0, 8, { smid = 1.5, t0 = 0.3, speed = { 3, 4 }, spread = 25 }),
				F("snow", "#E6FCFF", "#E6FCFF", 0.28, 0.28, 6, { t0 = 0, rot = 300, light = 1, life = { 0.9, 0.9 } }),
			},
			rings = { fring("air_ring", "#8FF2FF", 0.33, 7) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#6FF0FF", range = 9, brightness = 4, t1 = 0.9 },
			bursts = {
				B("shard", "#CDF1FF", "#5FA9D8", 14, 0.4, 0.4, { 7, 12 }, { 0.8, 1.2 }, { t0 = 0, spread = 70, accel = G, rot = 300, light = 1 }),
				B("rock", "#5FA9D8", "#5FA9D8", 6, 0.28, 0.28, { 5, 9 }, { 0.8, 1.2 }, { t0 = 0, spread = 60, accel = G }),
				puff("#D8F6FF", 6, 0.1, 2.0, 1.4, { t0 = 0.2, speed = { 2, 3 } }),
				stars("#E6FCFF", 6, 0.13, 0.4),
			},
			meshes = {
				flash("#DCFBFF", 0.5, 1.4, 0.3, 0.4),
				-- гигантский клык позади копья, оседает и уходит под землю
				M("ice_fang", "#CDF1FF", { t0 = 0.07, t1 = 0.3, size0 = { 0.3, 0.3, 0.3 }, size1 = { 1.4, 3.46, 1.33 }, a0 = 0, a1 = 0.3, y0 = -1, y1 = 0, easing = "Back", hold = 0.63 }),
				-- 3 малых клыка рядом
				M("ice_fang", "#5FA9D8", { count = 3, r = 1.3, t0 = 0.07, t1 = 0.3, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.63, 1.56, 0.6 }, a0 = 0, a1 = 0.3, y0 = -0.5, y1 = 0, easing = "Back", hold = 0.6 }),
				ring("frost_ring", "#CDF1FF", 1.8, 2.7, 0, 0.27, { a0 = 0, a1 = 0.3, hold = 0.86 }),
				ring("frost_glow", "#8FF2FF", 1.2, 4.8, 0, 0.47),
				cracks("#8FF2FF", 5, 1.8, 0.03, 1.2, {}),
			},
		},
	},

	-- 27 ---------------------------------------------------------------------
	ash_saw = {
		idle = {
			emitters = {
				I("fire", "#FFC23A", "#FF5A14", 0.17, 7, { life = { 1, 1 }, speed = { 0.2, 0.5 }, dir = "up", accel = { 0, 1.2, 0 }, light = 1 }),
			},
			light = { color = "#FF7A2A", range = 5, brightness = 1 },
		},
		flight = {
			emitters = {
				F("spark", "#FFC23A", "#FF5A14", 0.12, 0.12, 12, { t0 = 0, speed = { 4, 4 }, spread = 45, light = 1 }),
				F("smoke", "#4A4248", "#4A4248", 0.5, 2.0, 8, { t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
				-- пильные диски
				F("gear", "#8D8F9C", "#33303A", 0.6, 0.6, 5, { speed = { 10, 13 }, spread = 8, rot = 720, t0 = 0 }),
				-- языки пламени
				F("fire", "#FF5A14", "#FFC23A", 0.4, 0.3, 7, { speed = { 9, 11 }, spread = 6, t0 = 0, light = 1 }),
			},
			rings = { fring("ash_ring", "#FF6A1A", 0.33, 6.5) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF7A2A", range = 9, brightness = 4, t1 = 0.8 },
			bursts = {
				puff("#4A4248", 10, 0.07, 2.4, 1.2, { t0 = 0.2, speed = { 1.5, 3 } }),
				B("fire", "#FFC23A", "#FF5A14", 14, 0.25, 0.1, { 2, 4 }, { 1, 1.3 }, { t0 = 0, accel = { 0, 2, 0 }, spread = 60, light = 1, delay = 0 }),
				B("spark", "#FF7A2A", "#FF7A2A", 12, 0.16, 0.0, { 3, 6 }, { 0.4, 0.6 }, { delay = 0.1, t0 = 0, light = 1, dir = "out", spread = 80 }),
			},
			meshes = {
				flash("#FFD08A", 0.5, 1.4, 0.35, 0.33),
				disc("#18121A", 0.8, 4.2, 0.2, 0, 0.4, { a1 = 0.7, hold = 0.77 }),
				ring("ash_ring", "#FF6A1A", 1.1, 5.0, 0, 0.4),
				-- 6 пильных дисков едут веером (приближение: на среднем радиусе крутятся и гаснут)
				M("saw_disc", "#8D8F9C", { count = 3, r = 1.9, neon = false, t0 = 0.03, t1 = 0.6, size0 = { 0.2, 0.03, 0.2 }, size1 = { 0.68, 0.07, 0.68 }, a0 = 0, a1 = 0, spin = 1080, y0 = 0.1, y1 = 0.1, hold = 0.2 }),
				M("saw_disc", "#33303A", { count = 3, r = 2.4, neon = false, t0 = 0.1, t1 = 0.7, size0 = { 0.2, 0.03, 0.2 }, size1 = { 0.68, 0.07, 0.68 }, a0 = 0, a1 = 0, spin = -1080, y0 = 0.1, y1 = 0.1, hold = 0.1 }),
				cracks("#FF6A1A", 5, 1.8, 0.03, 1.2),
			},
		},
	},

	-- 28 ---------------------------------------------------------------------
	golem_heart = {
		idle = {
			emitters = {
				I("spark", "#FFC24A", "#FFC24A", 0.11, 5, { at = "grip", life = { 1.2, 1.2 }, light = 1, t0 = 0.2 }),
			},
			light = { color = "#FF8A2A", range = 6, brightness = 1.2 },
		},
		flight = {
			emitters = {
				F("rock", "#8F8678", "#5F574F", 0.2, 0.2, 8, { speed = { 10, 13 }, spread = 8, rot = 720, t0 = 0 }),
				F("spark", "#FFC24A", "#FFC24A", 0.12, 0.12, 10, { t0 = 0, speed = { 4, 4 }, spread = 45, light = 1 }),
				F("dust", "#D8C8A8", "#D8C8A8", 0.5, 2.0, 7, { t0 = 0.3, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
			},
			rings = { fring("air_ring", "#FF8A2A", 0.33, 6.5, 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF8A2A", range = 10, brightness = 4, t1 = 1.3 },
			bursts = {
				B("spark", "#FFC24A", "#FFC24A", 12, 0.16, 0.16, { 7, 12 }, { 0.8, 1.2 }, { delay = 0.53, t0 = 0, accel = G, light = 1, spread = 70 }),
				B("rock", "#8F8678", "#5F574F", 8, 0.28, 0.28, { 6, 10 }, { 0.8, 1.2 }, { delay = 0.53, t0 = 0, accel = G, spread = 70, rot = 300 }),
				puff("#D8C8A8", 8, 0.03, 2.2, 1.4, { t0 = 0.2 }),
			},
			meshes = {
				flash("#FFD08A", 0.5, 1.2, 0.3, 0.33),
				-- два кулака поднимаются, замахиваются, хлопают (приближение: одно движение вверх-к центру)
				M("golem_fist", "#8F8678", { count = 2, r = 1.1, neon = false, t0 = 0.03, t1 = 0.53, size0 = { 0.2, 0.2, 0.2 }, size1 = { 1.22, 1.06, 1.21 }, a0 = 0, a1 = 0, y0 = -0.8, y1 = 1.2, easing = "Back", hold = 0.8 }),
				-- руки-столбы
				M("part", "#5F574F", { count = 2, r = 1.1, neon = false, t0 = 0.03, t1 = 0.4, size0 = { 0.4, 0.1, 0.4 }, size1 = { 0.4, 1.5, 0.4 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.9 }),
				-- светящиеся ладони
				M("ball", "#FFB03A", { count = 2, r = 1.1, t0 = 0.63, t1 = 1.0, size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.4, 0.4, 0.4 }, a0 = 0, a1 = 0.3, y0 = 1.2, y1 = 1.2, easing = "Sine" }),
				ring("core_ring", "#FF8A2A", 1.0, 5.0, 0.53, 1.0),
				ring("core_ring", "#FFD25A", 1.1, 4.0, 0, 0.47),
				ring("core_ring", "#FFD25A", 1.1, 3.0, 0.27, 0.74),
			},
		},
	},

	-- 29 ---------------------------------------------------------------------
	magma_tongue = {
		idle = {
			emitters = {
				I("fire", "#FFC040", "#FF5A1A", 0.17, 7, { life = { 1, 1 }, speed = { 0.2, 0.5 }, dir = "up", accel = { 0, 1.3, 0 }, light = 1 }),
				I("drop", "#FFC040", "#FFC040", 0.12, 2, { at = "grip", life = { 0.8, 0.8 }, dir = "up", speed = { 0.1, 0.3 }, accel = { 0, -6, 0 } }),
			},
			light = { color = "#FF6A1A", range = 6, brightness = 1.3 },
		},
		flight = {
			emitters = {
				F("drop", "#FF5A1A", "#FFC040", 0.28, 0, 8, { smid = 0.5, t0 = 0, speed = { 3, 3 }, spread = 25, light = 1 }),
				F("fire", "#FF5A1A", "#FFC040", 0.8, 0.4, 8, { t0 = 0, speed = { 9, 11 }, spread = 6, light = 1 }),
				F("smoke", "#4A3A40", "#4A3A40", 0.5, 1.8, 6, { t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
				F("spark", "#FFC040", "#FFC040", 0.12, 0.12, 6, { t0 = 0, speed = { 4, 4 }, spread = 45 }),
			},
			rings = { fring("fire_ring", "#FF5A1A", 0.33, 6.5, 2.0) },
			light = { color = "#FF6A1A", range = 9, brightness = 1.8 },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF6A1A", range = 14, brightness = 6, t1 = 1.3 },
			bursts = {
				-- 12 капель лавы дугой
				B("drop", "#FF5A1A", "#FFC040", 12, 0.22, 0.22, { 8, 13 }, { 0.9, 1.2 }, { delay = 0.1, t0 = 0, accel = G, light = 1, spread = 60 }),
				B("rock", "#2A2226", "#2A2226", 8, 0.32, 0.32, { 6, 10 }, { 0.9, 1.2 }, { delay = 0.03, t0 = 0, accel = G, spread = 70, rot = 300 }),
				B("fire", "#FFC040", "#FF5A1A", 6, 0.3, 0.1, { 3, 5 }, { 0.9, 0.9 }, { delay = 0.07, t0 = 0, light = 1, spread = 20 }),
				puff("#4A3A40", 8, 0.13, 2.4, 1.2, { t0 = 0.1, speed = { 2, 3 } }),
			},
			meshes = {
				flash("#FFC878", 0.5, 1.4, 0.35, 0.33),
				disc("#FF5A1A", 0.8, 3.2, 0.05, 0, 0.4, { a1 = 0.6, hold = 0.9 }),
				-- главная трещина вперёд по +X и боковые ветки
				M("lava_crack", "#FF5A1A", { t0 = 0, t1 = 0.2, size0 = { 0.4, 0.05, 0.1 }, size1 = { 3.21, 0.24, 0.32 }, a0 = 0, a1 = 0.3, y0 = 0.05, y1 = 0.05, hold = 0.8 }),
				M("part", "#E0301A", { count = 2, r = 0.6, t0 = 0, t1 = 0.25, size0 = { 0.2, 0.1, 0.1 }, size1 = { 1.2, 0.1, 0.1 }, a0 = 0, a1 = 0.3, y0 = 0.05, y1 = 0.05, hold = 0.8 }),
				-- три гейзера по трещине
				M("lava_geyser", "#FF5A1A", { count = 3, r = 1.7, t0 = 0.1, t1 = 0.23, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.9, 2.4, 0.9 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.6 }),
				M("lava_geyser", "#FFC040", { count = 3, r = 1.7, t0 = 0.1, t1 = 0.23, size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.54, 1.5, 0.54 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.6 }),
			},
		},
	},

	-- 30 ---------------------------------------------------------------------
	phoenix_wing = {
		idle = {
			emitters = {
				I("fire", "#FFD24A", "#FF6A1A", 0.17, 6, { life = { 1, 1 }, speed = { 0.2, 0.5 }, dir = "up", accel = { 0, 1.3, 0 }, light = 1 }),
				glint("#FFF2C0", 2),
			},
			light = { color = "#FF8A2A", range = 6, brightness = 1.2 },
		},
		flight = {
			emitters = {
				F("fire", "#FF6A1A", "#E0302A", 0.9, 0.5, 10, { t0 = 0, speed = { 9, 12 }, spread = 8, light = 1 }),
				F("feather", "#FFD24A", "#FF6A1A", 0.5, 0.5, 8, { t0 = 0, speed = { 3, 4 }, spread = 30, rot = 200, light = 1, life = { 0.9, 0.9 } }),
				F("spark", "#FFD24A", "#FFD24A", 0.12, 0.12, 8, { t0 = 0, speed = { 4, 4 }, spread = 45 }),
			},
			rings = { fring("fire_ring", "#FF6A1A", 0.33, 6, 2.0) },
			light = { color = "#FF8A2A", range = 10, brightness = 2 },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF8A2A", range = 14, brightness = 5, t1 = 1.3 },
			bursts = {
				stars("#FFF2C0", 6, 0.2, 0.4),
			},
			meshes = {
				flash("#FFE0A0", 0.5, 1.5, 0.3, 0.33),
				ring("fire_ring", "#FFD24A", 1.3, 5.2, 0, 0.47),
				ring("fire_ring", "#FF6A1A", 1.3, 4.2, 0.17, 0.64),
				-- центральный столб огня
				M("wing_feather", "#FFD24A", { t0 = 0, t1 = 0.17, size0 = { 0.3, 0.3, 0.3 }, size1 = { 0.8, 2.2, 0.8 }, a0 = 0, a1 = 0.3, hold = 0.43 }),
				-- два крыла: 12 огненных перьев веером
				M("wing_feather", "#FF6A1A", { count = 4, r = 1.0, t0 = 0, t1 = 0.37, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.55, 1.9, 0.55 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.8 }),
				M("wing_feather", "#FFD24A", { count = 4, r = 1.4, t0 = 0.03, t1 = 0.4, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.6, 2.3, 0.6 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.75 }),
				M("wing_feather", "#E0302A", { count = 4, r = 1.8, t0 = 0.06, t1 = 0.43, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.65, 2.7, 0.65 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.7 }),
				-- угли поднимаются из крыльев
				M("ember_flame", "#FFD24A", { count = 7, r = 1.0, t0 = 0.47, t1 = 1.1, size0 = { 0.13, 0.18, 0.12 }, size1 = { 0.01, 0.01, 0.01 }, a0 = 0, a1 = 1, y0 = 0.5, y1 = 1.8, easing = "Sine" }),
				M("ember_flame", "#FF6A1A", { count = 7, r = 1.5, t0 = 0.5, t1 = 1.1, size0 = { 0.13, 0.18, 0.12 }, size1 = { 0.01, 0.01, 0.01 }, a0 = 0, a1 = 1, y0 = 0.5, y1 = 1.6, easing = "Sine" }),
				-- падающие перья-листья
				M("fall_feather", "#FFD24A", { count = 4, r = 1.4, t0 = 0.27, t1 = 1.2, size0 = { 0.5, 0.06, 0.17 }, size1 = { 0.5, 0.06, 0.17 }, a0 = 0, a1 = 1, y0 = 3.2, y1 = 0.2, spin = 160, easing = "Sine" }),
				M("fall_feather", "#FF6A1A", { count = 4, r = 2.0, t0 = 0.3, t1 = 1.2, size0 = { 0.5, 0.06, 0.17 }, size1 = { 0.5, 0.06, 0.17 }, a0 = 0, a1 = 1, y0 = 2.8, y1 = 0.2, spin = -160, easing = "Sine" }),
			},
		},
	},

	-- 31 ---------------------------------------------------------------------
	amethyst_geode = {
		idle = {
			emitters = {
				I("spark", "#E8B0FF", "#E8B0FF", 0.11, 5, { at = "grip", life = { 1.3, 1.3 }, light = 1, t0 = 0.2 }),
				glint("#F6E0FF", 2, 0.15, { texture = "star", at = "grip" }),
			},
			light = { color = "#C46AFF", range = 6, brightness = 1 },
		},
		flight = {
			emitters = {
				F("crystal", "#9A4EE0", "#C996FF", 0.4, 0.4, 10, { speed = { 10, 13 }, spread = 8, rot = 540, t0 = 0, light = 1 }),
				F("star", "#F6E0FF", "#F6E0FF", 0.3, 0.3, 8, { t0 = 0, rot = 300, light = 1, life = { 0.9, 0.9 } }),
				F("smoke", "#E0B8FF", "#E0B8FF", 0.3, 0, 6, { smid = 1.5, t0 = 0.3, speed = { 1, 2 }, spread = 25 }),
			},
			rings = { fring("geode_ring", "#C46AFF", 0.33, 7) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#C46AFF", range = 11, brightness = 5, t1 = 1.3 },
			bursts = {
				B("crystal", "#9A4EE0", "#C996FF", 12, 0.4, 0.4, { 6, 12 }, { 0.8, 1.2 }, { delay = 0.67, t0 = 0, spread = 70, accel = G, rot = 300, light = 1 }),
				stars("#F6E0FF", 6, 0.6, 0.4),
				puff("#E0B8FF", 6, 0.6, 1.8, 1.0, { t0 = 0.3, speed = { 1, 2 }, dir = "up" }),
			},
			meshes = {
				flash("#F0D0FF", 0.5, 1.4, 0.3, 0.33),
				-- купол из кристаллов остриями внутрь, раскрывается наружу (приближение: растёт и гаснет на 1.1 с)
				M("dome_crystal", "#9A4EE0", { count = 9, r = 1.7, neon = false, t0 = 0.03, t1 = 0.4, size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.39, 1.1, 0.33 }, a0 = 0, a1 = 0, y0 = 0.2, y1 = 0.7, easing = "Back", hold = 0.67 }),
				M("dome_crystal", "#C996FF", { count = 9, r = 1.4, neon = false, t0 = 0.06, t1 = 0.43, size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.34, 0.95, 0.29 }, a0 = 0, a1 = 0, y0 = 0.5, y1 = 1.1, easing = "Back", hold = 0.64 }),
				-- ядро внутри купола, набухает и гаснет
				M("ball", "#D89AFF", { t0 = 0.1, t1 = 1.0, size0 = { 1.8, 1.8, 1.8 }, size1 = { 4.3, 4.3, 4.3 }, a0 = 0.65, a1 = 1, y0 = 0.9, y1 = 0.9, easing = "Sine" }),
				disc("#C46AFF", 2.4, 3.8, 0.6, 0, 1.2),
				ring("geode_ring", "#C46AFF", 1.2, 6.0, 0.67, 1.14),
				ring("geode_ring", "#C46AFF", 1.2, 4.8, 0.83, 1.3),
			},
		},
	},

	-- 32 ---------------------------------------------------------------------
	quartz_needle = {
		idle = {
			emitters = {
				I("spark", "#F4FEFF", "#F4FEFF", 0.11, 4, { life = { 1.2, 1.2 }, light = 1, t0 = 0.2 }),
				glint("#F4FEFF", 3, 0.2, { texture = "star", life = { 0.4, 0.4 } }),
			},
			light = { color = "#8CE6FF", range = 5, brightness = 0.8 },
		},
		flight = {
			emitters = {
				-- иглы-штрихи вдоль оси
				F("shard", "#E8F4FF", "#A8C4E8", 0.9, 1.6, 14, { speed = { 10, 13 }, spread = 6, t0 = 0, light = 1 }),
				F("star", "#F4FEFF", "#F4FEFF", 0.3, 0.3, 8, { t0 = 0, rot = 300, light = 1, life = { 0.9, 0.9 } }),
				F("smoke", "#F0FCFF", "#F0FCFF", 0.3, 1.2, 5, { t0 = 0.3, speed = { 1, 2 }, spread = 25, life = { 0.9, 0.9 } }),
			},
			rings = { fring("glow_ring", "#8CE6FF", 0.33, 7.5, 2.3) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#8CE6FF", range = 9, brightness = 3, t1 = 1.0 },
			bursts = {
				stars("#F4FEFF", 8, 0.13, 0.4, { speed = { 1, 3 } }),
				B("shard", "#E8F4FF", "#A8C4E8", 8, 0.3, 0.3, { 6, 10 }, { 0.8, 1.2 }, { delay = 0, t0 = 0, spread = 70, accel = G, rot = 300 }),
			},
			meshes = {
				flash("#E8FCFF", 0.5, 1.4, 0.3, 0.33),
				disc("#A8E8FF", 2.4, 4.8, 0.6, 0, 1.0),
				ring("glow_ring", "#8CE6FF", 1.2, 5.2, 0.4, 0.9),
				-- лес из ~44 игл тремя кольцами радиусов
				M("needle", "#E8F4FF", { count = 14, r = 0.9, neon = false, t0 = 0, t1 = 0.2, size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.12, 1.2, 0.12 }, a0 = 0, a1 = 0, easing = "Back", hold = 1.0 }),
				M("needle", "#E8F4FF", { count = 18, r = 1.7, neon = false, t0 = 0.03, t1 = 0.23, size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.14, 1.55, 0.15 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.97 }),
				M("needle", "#A8C4E8", { count = 12, r = 2.3, neon = false, t0 = 0.06, t1 = 0.26, size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.15, 2.0, 0.16 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.9 }),
			},
		},
	},

	-- 33 ---------------------------------------------------------------------
	lunar_crescent = {
		idle = {
			emitters = {
				I("snow", "#F0F8FF", "#F0F8FF", 0.12, 5, { life = { 1.6, 1.6 }, accel = { 0, -0.3, 0 } }),
				glint("#F4FCFF", 2),
			},
			light = { color = "#BFE6FF", range = 6, brightness = 0.9 },
		},
		flight = {
			emitters = {
				-- маленькие серебряные полумесяцы (приближение осколками)
				F("shard", "#E4EAF6", "#E4EAF6", 0.6, 0.6, 8, { speed = { 10, 13 }, spread = 8, rot = 360, t0 = 0 }),
				F("smoke", "#F0F8FF", "#F0F8FF", 0.3, 0, 8, { smid = 1.5, t0 = 0.3, speed = { 3, 4 }, spread = 25 }),
				F("star", "#F4FCFF", "#F4FCFF", 0.3, 0.3, 6, { t0 = 0, rot = 300, light = 1, life = { 0.9, 0.9 } }),
			},
			rings = { fring("halo", "#BFE6FF", 0.33, 7, 2.1, 0.55) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#BFE6FF", range = 10, brightness = 4, t1 = 1.0 },
			bursts = {
				B("crystal", "#BFEAFF", "#BFEAFF", 10, 0.24, 0.24, { 6, 10 }, { 0.8, 1.2 }, { t0 = 0, spread = 70, accel = G, rot = 300 }),
				puff("#F0F8FF", 6, 0.1, 2.0, 1.4, { t0 = 0.3, speed = { 2, 3 } }),
				stars("#F4FCFF", 6, 0.13, 0.4),
			},
			meshes = {
				flash("#EAF6FF", 0.5, 1.4, 0.3, 0.4),
				disc("#D8F0FF", 0.24, 5.2, 0.5, 0.13, 0.53, { a1 = 0.7, hold = 0.65 }),
				-- кольцо halo: родные оси {d, d, 0.07}, плашмя его должен положить плеер
				M("halo", "#BFE6FF", { t0 = 0, t1 = 0.47, size0 = { 1.2, 1.2, 0.07 }, size1 = { 6.0, 6.0, 0.07 }, y0 = 0.1, y1 = 0.1 }),
				-- 6 ледяных полумесяцев веером (приближение: на радиусе ~2, крутятся и гаснут)
				M("moon_blade", "#BFEAFF", { count = 6, r = 2.0, t0 = 0, t1 = 0.97, size0 = { 0.3, 0.17, 0.6 }, size1 = { 0.68, 0.38, 1.41 }, a0 = 0, a1 = 1, spin = 900, y0 = 0.15, y1 = 0.15 }),
				M("frost_crystal", "#BFEAFF", { count = 12, r = 2.1, neon = false, t0 = 0.17, t1 = 0.4, size0 = { 0.05, 0.1, 0.05 }, size1 = { 0.13, 0.5, 0.13 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.9 }),
				-- луна и ореол поднимаются
				M("moon_disc", "#E6F4FF", { t0 = 0.13, t1 = 1.33, size0 = { 1.58, 1.6, 1.58 }, size1 = { 1.58, 1.6, 1.58 }, a0 = 0, a1 = 1, y0 = 2.2, y1 = 3.8, easing = "Sine" }),
				M("halo", "#BFE6FF", { t0 = 0.13, t1 = 1.33, size0 = { 2.3, 2.3, 0.07 }, size1 = { 3.3, 3.3, 0.07 }, a0 = 0, a1 = 1, y0 = 2.2, y1 = 3.8, easing = "Sine" }),
			},
		},
	},

	-- 34 ---------------------------------------------------------------------
	aurora_weave = {
		idle = {
			emitters = {
				I("spark", "#5DFFB0", "#B070FF", 0.11, 5, { life = { 1.4, 1.4 }, light = 1, t0 = 0.2 }),
				glint("#F4FFFC", 2, 0.15, { texture = "star" }),
			},
			light = { color = "#5DFFB0", range = 6, brightness = 0.9 },
		},
		flight = {
			emitters = {
				F("crystal", "#BFEEFF", "#BFEEFF", 0.38, 0.38, 8, { speed = { 10, 13 }, spread = 8, rot = 540, t0 = 0, light = 1 }),
				F("star", "#F4FFFC", "#F4FFFC", 0.3, 0.3, 8, { t0 = 0, rot = 300, light = 1, life = { 0.9, 0.9 } }),
				F("smoke", "#5DFFB0", "#B070FF", 0.3, 1.6, 6, { t0 = 0.4, speed = { 1, 2 }, spread = 25, life = { 0.9, 0.9 } }),
			},
			rings = {
				fring("fl_ring", "#5DFFB0", 0.5, 7.5, 2.3),
				fring("fl_ring", "#3BE8FF", 0.5, 7.5, 2.3),
				fring("fl_ring", "#B070FF", 0.5, 7.5, 2.3),
			},
		},
		impact = {
			duration = 1.5,
			light = { color = "#5DFFB0", range = 10, brightness = 4, t1 = 1.0 },
			bursts = {
				B("crystal", "#BFEEFF", "#BFEEFF", 8, 0.3, 0.3, { 6, 10 }, { 0.8, 1.2 }, { t0 = 0, spread = 70, accel = G, rot = 300 }),
				puff("#C8FFF0", 4, 0.1, 2.0, 1.4, { t0 = 0.3, speed = { 2, 3 } }),
			},
			meshes = {
				flash("#E8FFFA", 0.5, 1.4, 0.3, 0.33),
				disc("#7AFFD0", 2.4, 4.8, 0.6, 0.13, 1.0),
				-- 9 цветных колец поднимаются по очереди (3 цвета по 3 уровня высоты)
				M("aurora_ring", "#5DFFB0", { count = 1, t0 = 0, t1 = 0.9, size0 = { 1.8, 0.1, 1.8 }, size1 = { 2.9, 0.1, 2.9 }, a0 = 0.1, a1 = 1, y0 = 0.1, y1 = 1.0, easing = "Sine" }),
				M("aurora_ring", "#3BE8FF", { count = 1, t0 = 0.05, t1 = 0.95, size0 = { 1.8, 0.1, 1.8 }, size1 = { 2.9, 0.1, 2.9 }, a0 = 0.1, a1 = 1, y0 = 0.1, y1 = 1.9, easing = "Sine" }),
				M("aurora_ring", "#B070FF", { count = 1, t0 = 0.1, t1 = 1.0, size0 = { 1.8, 0.1, 1.8 }, size1 = { 2.9, 0.1, 2.9 }, a0 = 0.1, a1 = 1, y0 = 0.1, y1 = 2.8, easing = "Sine" }),
				-- 3 кольца по 8 световых лучей вокруг копья
				M("light_shaft", "#5DFFB0", { count = 8, r = 0.85, t0 = 0.07, t1 = 0.6, size0 = { 0.13, 0.24, 0.09 }, size1 = { 0.13, 2.4, 0.09 }, a0 = 0, a1 = 1, easing = "Sine" }),
				M("light_shaft", "#3BE8FF", { count = 8, r = 1.05, t0 = 0.17, t1 = 0.7, size0 = { 0.13, 0.24, 0.09 }, size1 = { 0.13, 2.4, 0.09 }, a0 = 0, a1 = 1, easing = "Sine" }),
				M("light_shaft", "#B070FF", { count = 8, r = 1.25, t0 = 0.27, t1 = 0.8, size0 = { 0.13, 0.24, 0.09 }, size1 = { 0.13, 2.4, 0.09 }, a0 = 0, a1 = 1, easing = "Sine" }),
				M("ice_crystal", "#BFEEFF", { count = 14, r = 1.7, neon = false, t0 = 0.13, t1 = 0.4, size0 = { 0.05, 0.1, 0.05 }, size1 = { 0.13, 0.56, 0.13 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.6 }),
				M("star", "#F4FFFC", { count = 8, r = 1.5, t0 = 0.2, t1 = 0.9, size0 = { 0.1, 0.01, 0.1 }, size1 = { 0.6, 0.05, 0.6 }, a0 = 0, a1 = 1, y0 = 0.5, y1 = 1.6, easing = "Sine" }),
			},
		},
	},

	-- 35 ---------------------------------------------------------------------
	cloud_feather = {
		idle = {
			emitters = {
				I("smoke", "#FFFFFF", "#CFE8FF", 0.09, 5, { life = { 1.5, 1.5 }, dir = "up", accel = { 0, 0.3, 0 } }),
				glint("#FFFBE0", 1.5),
			},
			light = { color = "#CFEEFF", range = 8, brightness = 0.8 },
		},
		flight = {
			emitters = {
				F("smoke", "#FFFFFF", "#CFE8FF", 0.6, 0, 10, { smid = 1.8, t0 = 0.1, speed = { 2, 4 }, spread = 25, life = { 1, 1 } }),
				F("feather", "#FFFFFF", "#58B7FF", 0.7, 0.7, 6, { t0 = 0, rot = 300, life = { 1, 1 } }),
				F("feather", "#FF9EC4", "#FFD35A", 0.7, 0.7, 4, { t0 = 0, rot = 300, life = { 1, 1 } }),
				F("sparkle", "#FFFBE0", "#FFFBE0", 0.15, 0.15, 6, { t0 = 0, light = 1, life = { 0.8, 0.8 }, spread = 60 }),
			},
			rings = {
				fring("rainbow_ring", "#FF4A5A", 0.99, 6.5),
				fring("rainbow_ring", "#FFE14A", 0.99, 6.5),
				fring("rainbow_ring", "#3AD8FF", 0.99, 6.5),
			},
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFFFFF", range = 12, brightness = 2, t1 = 0.4 },
			bursts = {
				B("smoke", "#FFFFFF", "#CFE8FF", 18, 0.9, 2.5, { 3, 5 }, { 1.1, 1.3 }, { t0 = 0.1, delay = 0, spread = 80, dir = "out", drag = 2 }),
				B("feather", "#FFFFFF", "#FF9EC4", 5, 0.8, 0.8, { 5, 7 }, { 1.2, 1.3 }, { t0 = 0, delay = 0, spread = 40, rot = 250, accel = { 0, -4, 0 } }),
				B("feather", "#58B7FF", "#FFD35A", 5, 0.8, 0.8, { 5, 7 }, { 1.2, 1.3 }, { t0 = 0, delay = 0, spread = 40, rot = 250, accel = { 0, -4, 0 } }),
				B("sparkle", "#FFFBE0", "#FFFBE0", 8, 0.2, 0.2, { 2, 4 }, { 1.1, 1.2 }, { t0 = 0, delay = 0.07, spread = 40, light = 1 }),
			},
			meshes = {
				M("ball", "#FFFFFF", { t0 = 0, t1 = 0.4, size0 = { 0.8, 0.8, 0.8 }, size1 = { 3.4, 3.4, 3.4 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				-- облачная подушка по земле
				M("cloud_puff", "#CFE8FF", { neon = false, t0 = 0, t1 = 1.3, size0 = { 1.0, 0.3, 1.0 }, size1 = { 5.2, 0.9, 5.2 }, a0 = 0.2, a1 = 1, y0 = 0.2, y1 = 0.2 }),
				-- 7 радужных колец с шагом 0.03 с
				M("rainbow_ring", "#FF4A5A", { t0 = 0.03, t1 = 0.8, size0 = { 1.1, 0.1, 1.1 }, size1 = { 2.9, 0.1, 2.9 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 0.15 }),
				M("rainbow_ring", "#FF9A3A", { t0 = 0.06, t1 = 0.8, size0 = { 1.35, 0.1, 1.35 }, size1 = { 3.5, 0.1, 3.5 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 0.2 }),
				M("rainbow_ring", "#FFE14A", { t0 = 0.09, t1 = 0.8, size0 = { 1.6, 0.1, 1.6 }, size1 = { 4.2, 0.1, 4.2 }, a0 = 0, a1 = 1, y0 = 0.25, y1 = 0.25 }),
				M("rainbow_ring", "#5AE06A", { t0 = 0.12, t1 = 0.8, size0 = { 1.85, 0.1, 1.85 }, size1 = { 4.8, 0.1, 4.8 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 0.3 }),
				M("rainbow_ring", "#3AD8FF", { t0 = 0.15, t1 = 0.8, size0 = { 2.1, 0.1, 2.1 }, size1 = { 5.5, 0.1, 5.5 }, a0 = 0, a1 = 1, y0 = 0.35, y1 = 0.35 }),
				M("rainbow_ring", "#4A7AFF", { t0 = 0.18, t1 = 0.8, size0 = { 2.35, 0.1, 2.35 }, size1 = { 6.1, 0.1, 6.1 }, a0 = 0, a1 = 1, y0 = 0.4, y1 = 0.4 }),
				M("rainbow_ring", "#B05AFF", { t0 = 0.21, t1 = 0.8, size0 = { 2.6, 0.1, 2.6 }, size1 = { 6.8, 0.1, 6.8 }, a0 = 0, a1 = 1, y0 = 0.45, y1 = 0.45 }),
			},
		},
	},

	-- 36 ---------------------------------------------------------------------
	sky_harpoon = {
		idle = {
			emitters = {
				I("smoke", "#FFFFFF", "#CFE6FF", 0.09, 5, { life = { 1.5, 1.5 } }),
				glint("#FFF0A0", 1.5),
			},
			light = { color = "#BFEAFF", range = 8, brightness = 0.7 },
		},
		flight = {
			emitters = {
				F("smoke", "#FFFFFF", "#CFE6FF", 0.6, 0, 10, { smid = 1.8, t0 = 0.1, speed = { 2, 4 }, spread = 25, life = { 1, 1 } }),
				F("feather", "#FFFFFF", "#4FB4FF", 0.65, 0.65, 5, { t0 = 0, rot = 300, life = { 1, 1 } }),
				F("feather", "#E8B43E", "#FFFFFF", 0.65, 0.65, 4, { t0 = 0, rot = 300, life = { 1, 1 } }),
				F("sparkle", "#FFF0A0", "#FFF0A0", 0.15, 0.15, 5, { t0 = 0, light = 1, life = { 0.8, 0.8 }, spread = 60 }),
			},
			rings = { fring("wind_ring", "#E8FBFF", 0.25, 7) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFFFFF", range = 12, brightness = 2, t1 = 0.4 },
			bursts = {
				B("smoke", "#FFFFFF", "#CFE6FF", 12, 0.9, 2.4, { 3, 5 }, { 1.1, 1.3 }, { t0 = 0.1, delay = 0, spread = 80, dir = "out", drag = 2 }),
				B("feather", "#FFFFFF", "#4FB4FF", 8, 0.8, 0.8, { 5, 7 }, { 1.2, 1.3 }, { t0 = 0, delay = 0, spread = 40, rot = 250, accel = { 0, -4, 0 } }),
				B("sparkle", "#FFF0A0", "#FFF0A0", 8, 0.2, 0.2, { 3, 6 }, { 1.0, 1.2 }, { t0 = 0, delay = 0.07, spread = 120, light = 1 }),
			},
			meshes = {
				M("ball", "#FFFFFF", { t0 = 0, t1 = 0.4, size0 = { 0.8, 0.8, 0.8 }, size1 = { 3.2, 3.2, 3.2 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				-- 3 латунных зубца-гарпуна по кругу r 1.7
				M("barb", "#E8B43E", { count = 3, r = 1.7, neon = false, t0 = 0.07, t1 = 0.4, size0 = { 0.2, 0.2, 0.1 }, size1 = { 1.11, 1.7, 0.32 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.87 }),
				M("ball", "#FFF0A0", { count = 3, r = 1.5, t0 = 0.07, t1 = 0.4, size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.25, 0.25, 0.25 }, a0 = 0, a1 = 0.2, y0 = 1.5, y1 = 1.6, hold = 0.8 }),
				-- кольца-якоря у основания зубцов
				M("wind_ring", "#FFF0A0", { count = 3, r = 1.7, t0 = 0.13, t1 = 0.9, size0 = { 0.6, 0.1, 0.6 }, size1 = { 1.3, 0.1, 1.3 }, a0 = 0, a1 = 1, y0 = 0.1, y1 = 0.1 }),
				-- 6 колец ветра спиралью вверх
				M("wind_ring", "#E8FBFF", { count = 6, r = 0.5, t0 = 0.07, t1 = 1.33, size0 = { 1.3, 0.1, 1.3 }, size1 = { 3.1, 0.1, 3.1 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 4.2, spin = 720, easing = "Sine" }),
			},
		},
	},

	-- 37 ---------------------------------------------------------------------
	rift_shards = {
		idle = {
			emitters = {
				I("spark", "#F0D0FF", "#B45CFF", 0.08, 7, { life = { 1.5, 1.5 } }),
				glint("#F0D0FF", 1, 0.15, { texture = "star" }),
			},
			light = { color = "#B06CFF", range = 9, brightness = 1 },
		},
		flight = {
			emitters = {
				F("shard", "#2A2038", "#7A2FB0", 0.5, 0.5, 12, { t0 = 0, rot = 500, life = { 1, 1 } }),
				F("smoke", "#5A2A8A", "#5A2A8A", 0.6, 0, 8, { smid = 1.8, t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
				F("spark", "#F0D0FF", "#F0D0FF", 0.12, 0.12, 8, { t0 = 0, speed = { 4, 6 }, spread = 45, life = { 0.8, 0.8 } }),
			},
			rings = { fring("rift_rim", "#B45CFF", 0.5, 6.5, 2.1, 0.6), fring("rift_rim", "#FF7AE8", 1.0, 6.5, 2.1, 0.6) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#B06CFF", range = 10, brightness = 4, t1 = 1.1 },
			bursts = {
				-- светлые искры вихрем (приближение: поднимаются у центра) и взрыв искр при имплозии
				B("spark", "#F0D0FF", "#B45CFF", 16, 0.14, 0.0, { 1, 2 }, { 0.7, 0.9 }, { delay = 0.07, t0 = 0, light = 1, dir = "out", spread = 120 }),
				B("spark", "#F0D0FF", "#F0D0FF", 8, 0.16, 0.0, { 3, 6 }, { 0.4, 0.4 }, { delay = 1.1, t0 = 0, light = 1, dir = "out", spread = 180 }),
			},
			meshes = {
				-- диск разлома раскрывается, держится до ~1.1 с
				M("rift_disc", "#0E0618", { neon = false, t0 = 0, t1 = 0.27, size0 = { 1.8, 0.05, 1.8 }, size1 = { 6.0, 0.05, 6.0 }, a0 = 0.1, a1 = 0.1, y0 = 0.05, y1 = 0.05, hold = 0.85 }),
				M("rift_rim", "#B45CFF", { t0 = 0, t1 = 0.27, size0 = { 2.0, 0.1, 2.0 }, size1 = { 6.4, 0.1, 6.4 }, a0 = 0, a1 = 0.1, y0 = 0.1, y1 = 0.1, hold = 0.85 }),
				M("rift_rim", "#FF7AE8", { t0 = 0, t1 = 0.27, size0 = { 1.6, 0.06, 1.6 }, size1 = { 4.8, 0.06, 4.8 }, a0 = 0, a1 = 0.1, y0 = 0.12, y1 = 0.12, hold = 0.85 }),
				M("crack", "#B45CFF", { count = 6, r = 1.2, t0 = 0.07, t1 = 0.6, size0 = { 0.3, 0.05, 0.1 }, size1 = { 2.0, 0.1, 0.5 }, a0 = 0, a1 = 0.3, y0 = 0.05, y1 = 0.05, hold = 0.4 }),
				-- тёмные осколки втягиваются в центр
				M("shard", "#2A2038", { count = 5, r = 2.8, neon = false, t0 = 0.07, t1 = 0.97, size0 = { 0.18, 0.55, 0.19 }, size1 = { 0.02, 0.05, 0.02 }, a0 = 0, a1 = 0, y0 = 1.5, y1 = 0.3, spin = 400, easing = "Quad" }),
				M("shard", "#7A2FB0", { count = 5, r = 3.1, neon = false, t0 = 0.1, t1 = 0.97, size0 = { 0.18, 0.55, 0.19 }, size1 = { 0.02, 0.05, 0.02 }, a0 = 0, a1 = 0, y0 = 2.0, y1 = 0.3, spin = -400, easing = "Quad" }),
				-- имплозия и кольцо-вспышка
				M("ball", "#E6B8FF", { t0 = 1.0, t1 = 1.1, size0 = { 1.0, 1.0, 1.0 }, size1 = { 6.0, 6.0, 6.0 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				M("rift_rim", "#FF7AE8", { t0 = 1.1, t1 = 1.33, size0 = { 0.8, 0.1, 0.8 }, size1 = { 10, 0.1, 10 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 0.15 }),
			},
		},
	},

	-- 38 ---------------------------------------------------------------------
	void_scissors = {
		idle = {
			emitters = {
				I("spark", "#F0D0FF", "#B45CFF", 0.08, 7, { life = { 1.5, 1.5 } }),
				glint("#F0D0FF", 1, 0.15, { texture = "star" }),
			},
			light = { color = "#A050F0", range = 8, brightness = 0.9 },
		},
		flight = {
			emitters = {
				-- полумесяцы-разрезы (приближение осколками)
				F("shard", "#B45CFF", "#FF6AF0", 0.5, 0.5, 8, { speed = { 10, 13 }, spread = 10, rot = 400, t0 = 0, light = 1 }),
				F("shard", "#1C1626", "#6A2AA8", 0.45, 0.45, 8, { rot = 500, life = { 1, 1 }, t0 = 0 }),
				F("smoke", "#4A1F78", "#4A1F78", 0.6, 0, 7, { smid = 1.8, t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
			},
			rings = {}, -- у void_scissors нет меша кольца, кольца полёта опущены
		},
		impact = {
			duration = 1.5,
			light = { color = "#B45CFF", range = 10, brightness = 4, t1 = 1.0 },
			bursts = {
				B("shard", "#1C1626", "#6A2AA8", 12, 0.5, 0.5, { 2, 4 }, { 0.6, 0.9 }, { delay = 0.7, t0 = 0, dir = "out", spread = 120, rot = 400, accel = { 0, -4, 0 } }),
				puff("#4A1F78", 6, 0.7, 2.5, 0.8, { s0 = 0.8, t0 = 0.2, speed = { 2, 3 } }),
				B("spark", "#F0D0FF", "#F0D0FF", 10, 0.16, 0.16, { 3, 6 }, { 1.0, 1.0 }, { delay = 0.07, t0 = 0, dir = "out", spread = 150, light = 1 }),
			},
			meshes = {
				-- два светящихся разреза крестом
				M("slash", "#B45CFF", { count = 2, r = 0.5, t0 = 0.07, t1 = 0.2, size0 = { 0.4, 0.05, 0.2 }, size1 = { 3.6, 0.05, 0.2 }, a0 = 0, a1 = 0.3, y0 = 0.8, y1 = 0.8, spin = 76, hold = 0.57 }),
				M("slash", "#F2D8FF", { count = 2, r = 0.5, t0 = 0.07, t1 = 0.2, size0 = { 0.4, 0.05, 0.08 }, size1 = { 3.4, 0.05, 0.08 }, a0 = 0, a1 = 0.3, y0 = 0.82, y1 = 0.82, spin = 76, hold = 0.57 }),
				-- пузырь пустоты: обод и тёмное ядро, лопается к 0.8 с
				M("void_bubble", "#C070FF", { t0 = 0.07, t1 = 0.67, size0 = { 0.7, 0.7, 0.7 }, size1 = { 2.6, 2.6, 2.6 }, a0 = 0.3, a1 = 0.5, y0 = 1, y1 = 1, easing = "Sine" }),
				M("void_bubble", "#0A0412", { neon = false, t0 = 0.07, t1 = 0.67, size0 = { 0.5, 0.5, 0.5 }, size1 = { 2.2, 2.2, 2.2 }, a0 = 0, a1 = 0, y0 = 1, y1 = 1, easing = "Sine" }),
				M("ball", "#C070FF", { t0 = 0.67, t1 = 0.8, size0 = { 2.6, 2.6, 2.6 }, size1 = { 8.6, 8.6, 8.6 }, a0 = 0.5, a1 = 1, y0 = 1, y1 = 1 }),
				M("ball", "#FF6AF0", { t0 = 0.7, t1 = 1.13, size0 = { 0.6, 0.1, 0.6 }, size1 = { 10, 0.1, 10 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 0.15 }),
				-- 6 полумесяцев-разрезов уносит ветром
				M("crescent", "#B45CFF", { count = 3, r = 1.0, t0 = 0.1, t1 = 1.33, size0 = { 0.2, 0.07, 0.4 }, size1 = { 0.49, 0.17, 0.98 }, a0 = 0, a1 = 1, y0 = 0.5, y1 = 2.0, spin = 400 }),
				M("crescent", "#FF6AF0", { count = 3, r = 2.0, t0 = 0.12, t1 = 1.33, size0 = { 0.2, 0.07, 0.4 }, size1 = { 0.49, 0.17, 0.98 }, a0 = 0, a1 = 1, y0 = 0.5, y1 = 2.4, spin = -400 }),
			},
		},
	},

	-- 39 ---------------------------------------------------------------------
	astral_armillary = {
		idle = {
			emitters = {
				I("sparkle", "#FFFBE0", "#FFFBE0", 0.17, 4, { life = { 0.6, 0.6 }, light = 1, t0 = 0 }),
				I("dust", "#FFFBE0", "#FFFBE0", 0.06, 6, { life = { 1.5, 1.5 } }),
			},
			light = { color = "#FFE8A0", range = 9, brightness = 1 },
		},
		flight = {
			emitters = {
				F("star", "#FFE680", "#7AE8FF", 0.4, 0.4, 10, { t0 = 0, rot = 540, life = { 1, 1 }, light = 1 }),
				F("spark", "#FFFBE0", "#FFFBE0", 0.12, 0.12, 10, { t0 = 0, life = { 0.8, 0.8 }, speed = { 3, 5 }, spread = 60 }),
				F("smoke", "#FFD870", "#FFD870", 0.6, 0, 5, { smid = 1.6, t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
			},
			rings = {
				fring("armillary_ring", "#FFE680", 1.0, 6.5),
				fring("armillary_ring", "#7AE8FF", 1.0, 6.5),
				fring("armillary_ring", "#FF8AD8", 1.0, 6.5),
			},
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFE8A0", range = 12, brightness = 2, t1 = 0.5 },
			bursts = {
				B("star", "#FFE680", "#FFFBE0", 14, 0.4, 0.4, { 2, 5 }, { 1.1, 1.3 }, { delay = 0.03, t0 = 0, rot = 300, light = 1, spread = 80 }),
				B("sparkle", "#FFFBE0", "#FFFBE0", 14, 0.18, 0.18, { 2, 5 }, { 0.9, 1.1 }, { delay = 0.1, t0 = 0, light = 1, spread = 80 }),
			},
			meshes = {
				M("ball", "#FFF0B0", { t0 = 0, t1 = 0.4, size0 = { 0.8, 0.8, 0.8 }, size1 = { 3.8, 3.8, 3.8 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				-- плоская 8-лучевая звезда на земле
				M("ground_star", "#FFE680", { t0 = 0.07, t1 = 1.33, size0 = { 1.2, 0.05, 1.2 }, size1 = { 4.5, 0.05, 4.5 }, a0 = 0, a1 = 1, y0 = 0.1, y1 = 0.1, spin = 120 }),
				-- 6 колец-орбит на высоте 1.3 (разные цвета, вращение)
				M("armillary_ring", "#FFE680", { count = 2, r = 0.1, t0 = 0.03, t1 = 1.33, size0 = { 0.6, 0.09, 0.6 }, size1 = { 3.3, 0.2, 3.3 }, a0 = 0, a1 = 1, y0 = 1.3, y1 = 1.3, spin = 360 }),
				M("armillary_ring", "#7AE8FF", { count = 2, r = 0.1, t0 = 0.05, t1 = 1.33, size0 = { 0.6, 0.09, 0.6 }, size1 = { 4.0, 0.2, 4.0 }, a0 = 0, a1 = 1, y0 = 1.3, y1 = 1.3, spin = -420 }),
				M("armillary_ring", "#FF8AD8", { count = 2, r = 0.1, t0 = 0.07, t1 = 1.33, size0 = { 0.6, 0.09, 0.6 }, size1 = { 5.2, 0.2, 5.2 }, a0 = 0, a1 = 1, y0 = 1.3, y1 = 1.3, spin = 560 }),
				-- 6 планет-шариков на орбите
				M("ball", "#7AE8FF", { count = 3, r = 2.0, t0 = 0.07, t1 = 1.2, size0 = { 0.28, 0.28, 0.28 }, size1 = { 0.05, 0.05, 0.05 }, a0 = 0, a1 = 0.3, y0 = 1.3, y1 = 1.3, spin = 360, easing = "Sine" }),
				M("ball", "#FF8AD8", { count = 3, r = 2.1, t0 = 0.1, t1 = 1.2, size0 = { 0.28, 0.28, 0.28 }, size1 = { 0.05, 0.05, 0.05 }, a0 = 0, a1 = 0.3, y0 = 1.3, y1 = 1.3, spin = -360, easing = "Sine" }),
			},
		},
	},

	-- 40 ---------------------------------------------------------------------
	singularity_spire = {
		idle = {
			emitters = {
				I("spark", "#FFF2D0", "#FF9A2A", 0.08, 7, { life = { 1.5, 1.5 } }),
				glint("#FFF2D0", 1, 0.15, { texture = "star" }),
			},
			light = { color = "#8A50E0", range = 9, brightness = 0.9 },
		},
		flight = {
			emitters = {
				-- частицы вихрем (приближение: частицы уходят назад)
				F("spark", "#FFF2D0", "#FF9A2A", 0.14, 0.14, 12, { t0 = 0.2, speed = { 2, 4 }, spread = 40, life = { 1, 1 } }),
				F("shard", "#2C2238", "#2C2238", 0.3, 0.3, 6, { rot = 500, life = { 1, 1 }, t0 = 0 }),
				F("smoke", "#3A1A5A", "#3A1A5A", 0.6, 0, 8, { smid = 1.8, t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
			},
			rings = { fring("horizon_ring", "#FF9A2A", 0.5, 6.8, 0.2, 1, 1.2), fring("horizon_ring", "#A45AFF", 1.0, 6.8, 0.2, 1, 1.2) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF9A2A", range = 12, brightness = 5, t1 = 0.9 },
			bursts = {
				-- вспышка частиц после имплозии
				B("spark", "#FFF2D0", "#FF9A2A", 26, 0.18, 0.0, { 3, 6 }, { 0.5, 0.8 }, { delay = 0.5, t0 = 0, light = 1, dir = "out", spread = 150 }),
			},
			meshes = {
				-- тёмное ядро имплозии растёт и сжимается
				M("dark_disc", "#06030A", { neon = false, t0 = 0.07, t1 = 0.4, size0 = { 0.6, 0.6, 0.6 }, size1 = { 2.4, 2.4, 2.4 }, a0 = 0.1, a1 = 0.1, y0 = 0.9, y1 = 0.9, hold = 0.17 }),
				-- частицы втягиваются к точке над касанием
				M("particle", "#FFF2D0", { count = 13, r = 3.0, t0 = 0.03, t1 = 0.57, size0 = { 0.18, 0.18, 0.16 }, size1 = { 0.02, 0.02, 0.02 }, a0 = 0, a1 = 1, y0 = 1.5, y1 = 0.9, easing = "Quad" }),
				M("particle", "#FF9A2A", { count = 13, r = 3.4, t0 = 0.03, t1 = 0.57, size0 = { 0.18, 0.18, 0.16 }, size1 = { 0.02, 0.02, 0.02 }, a0 = 0, a1 = 1, y0 = 2.0, y1 = 0.9, easing = "Quad" }),
				M("ball", "#FFE8C0", { t0 = 0.5, t1 = 0.87, size0 = { 0.6, 0.6, 0.6 }, size1 = { 3.6, 3.6, 3.6 }, a0 = 0, a1 = 1, y0 = 0.9, y1 = 0.9 }),
				M("horizon_ring", "#FF9A2A", { t0 = 0.53, t1 = 1.33, size0 = { 0.8, 0.14, 0.8 }, size1 = { 12, 0.14, 12 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 0.15 }),
				M("horizon_ring", "#FFF2D0", { t0 = 0.6, t1 = 1.33, size0 = { 0.8, 0.14, 0.8 }, size1 = { 10, 0.14, 10 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 0.2 }),
				-- 7 ступенчатых чёрных столбов по кругу
				M("pillar", "#18121F", { count = 4, r = 1.8, neon = false, t0 = 0.53, t1 = 0.8, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.84, 2.1, 0.73 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.6 }),
				M("pillar", "#2C2238", { count = 3, r = 2.0, neon = false, t0 = 0.6, t1 = 0.85, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.84, 2.1, 0.73 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.5 }),
				M("horizon_ring", "#FF9A2A", { count = 7, r = 1.9, t0 = 0.53, t1 = 0.8, size0 = { 0.3, 0.1, 0.3 }, size1 = { 0.6, 0.1, 0.6 }, a0 = 0, a1 = 0, y0 = 0.5, y1 = 2.1, hold = 0.45 }),
			},
		},
	},

	-- 41 ---------------------------------------------------------------------
	gear_pike = {
		idle = {
			emitters = {
				I("smoke", "#FFFFFF", "#FFFFFF", 0.12, 3, { t0 = 0.3, life = { 1.5, 1.5 }, speed = { 0.4, 0.4 }, spread = 20, dir = "up" }),
				I("spark", "#FFB030", "#FFB030", 0.05, 3, { life = { 0.8, 0.8 }, t0 = 0, light = 1 }),
				glint("#FFF0B0", 2, 0.14),
			},
			light = { color = "#FFC060", range = 8, brightness = 0.8 },
		},
		flight = {
			emitters = {
				F("gear", "#F0C040", "#2A9A9A", 0.5, 0.5, 8, { rot = 540, life = { 1, 1 }, t0 = 0 }),
				F("smoke", "#FFFFFF", "#F3DCB8", 0.6, 0, 8, { smid = 1.8, t0 = 0.1, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
				F("spark", "#FFF0B0", "#FFF0B0", 0.12, 0.12, 8, { t0 = 0, speed = { 4, 6 }, spread = 45, life = { 0.8, 0.8 } }),
			},
			rings = { fring("gear_mark", "#FFB030", 0.33, 6.5, 2.1, 0.4) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFE2A0", range = 10, brightness = 2, t1 = 0.4 },
			bursts = {
				-- 8 болтов по дуге (шестерёни - меши ниже)
				B("shard", "#5A5260", "#5A5260", 8, 0.14, 0.14, { 5, 9 }, { 1.0, 1.1 }, { delay = 0, t0 = 0, accel = { 0, -25, 0 }, spread = 70, rot = 300 }),
				B("smoke", "#FFFFFF", "#F3DCB8", 10, 0.8, 2.5, { 2, 4 }, { 1.1, 1.3 }, { delay = 0.07, t0 = 0.1, spread = 30, drag = 1 }),
				B("spark", "#FFF0B0", "#FFF0B0", 10, 0.14, 0.14, { 3, 7 }, { 0.9, 1.0 }, { delay = 0, t0 = 0, light = 1, spread = 80 }),
			},
			meshes = {
				M("ball", "#FFE2A0", { t0 = 0, t1 = 0.4, size0 = { 0.8, 0.8, 0.8 }, size1 = { 3.6, 3.6, 3.6 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				-- шестерня-метка на земле, медленно крутится
				M("gear_mark", "#FFB030", { t0 = 0.07, t1 = 1.33, size0 = { 1.5, 0.04, 1.5 }, size1 = { 2.8, 0.04, 2.8 }, a0 = 0, a1 = 1, y0 = 0.1, y1 = 0.1, spin = 100 }),
				-- шестерни: катятся по земле (приближение: вращаются на месте, гаснут к 1.2 с)
				M("gear", "#F0C040", { count = 3, r = 1.8, neon = false, t0 = 0, t1 = 1.2, size0 = { 0.9, 0.1, 0.87 }, size1 = { 0.1, 0.02, 0.1 }, a0 = 0, a1 = 0, y0 = 0.3, y1 = 0.1, spin = 360, easing = "Bounce" }),
				M("gear", "#D8743A", { count = 2, r = 2.4, neon = false, t0 = 0, t1 = 1.2, size0 = { 0.7, 0.08, 0.7 }, size1 = { 0.1, 0.02, 0.1 }, a0 = 0, a1 = 0, y0 = 0.3, y1 = 0.1, spin = -360, easing = "Bounce" }),
				M("gear", "#2A9A9A", { count = 2, r = 2.0, neon = false, t0 = 0, t1 = 1.2, size0 = { 0.8, 0.09, 0.8 }, size1 = { 0.1, 0.02, 0.1 }, a0 = 0, a1 = 0, y0 = 0.3, y1 = 0.1, spin = 300, easing = "Bounce" }),
				-- 3 пружины пружинят
				M("spring", "#5A5260", { count = 3, r = 1.3, neon = false, t0 = 0.07, t1 = 1.27, size0 = { 0.4, 0.1, 0.4 }, size1 = { 0.4, 0.77, 0.4 }, a0 = 0, a1 = 0, easing = "Bounce" }),
			},
		},
	},

	-- 42 ---------------------------------------------------------------------
	spore_halberd = {
		idle = {
			emitters = {
				I("spore", "#9AFFB0", "#FF9AE0", 0.08, 9, { life = { 1.8, 1.8 }, accel = { 0, 0.3, 0 }, light = 1 }),
				glint("#9AFFB0", 1, 0.14, { texture = "star" }),
			},
			light = { color = "#9AFFC0", range = 9, brightness = 0.9 },
		},
		flight = {
			emitters = {
				F("spore", "#8AFFB8", "#FF9EE0", 0.6, 0, 9, { smid = 1.8, t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
				F("spore", "#E86AB8", "#4AD8C0", 0.35, 0.35, 6, { rot = 300, life = { 1, 1 }, t0 = 0 }),
				F("spore", "#9AFFB0", "#FF9AE0", 0.14, 0.14, 12, { life = { 0.8, 0.8 }, t0 = 0, light = 1 }),
			},
			rings = { fring("ground_ring", "#9AFFB0", 0.5, 6.5), fring("ground_ring", "#5CF0E0", 1.0, 6.5) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#9AFFC0", range = 11, brightness = 1.5, t1 = 1.2 },
			bursts = {
				B("spore", "#8AFFB8", "#FF9EE0", 16, 0.9, 2.4, { 2, 3 }, { 1.1, 1.3 }, { delay = 0, t0 = 0.2, spread = 80, dir = "out", drag = 2 }),
				B("spore", "#9AFFB0", "#FF9AE0", 20, 0.16, 0.12, { 2, 4 }, { 1.1, 1.3 }, { delay = 0.03, t0 = 0, light = 1, accel = { 0, 1, 0 }, spread = 60 }),
			},
			meshes = {
				M("ball", "#D8FFE8", { t0 = 0, t1 = 0.4, size0 = { 0.8, 0.8, 0.8 }, size1 = { 3.6, 3.6, 3.6 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				ring("ground_ring", "#9AFFB0", 1.2, 5.0, 0, 0.6),
				-- 7 грибов вырастают по кругу с пружинкой
				M("mushroom", "#E86AB8", { count = 4, r = 1.6, neon = false, t0 = 0.1, t1 = 0.43, size0 = { 0.2, 0.2, 0.2 }, size1 = { 1.24, 1.12, 1.18 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.7 }),
				M("mushroom", "#4AD8C0", { count = 3, r = 2.3, neon = false, t0 = 0.13, t1 = 0.46, size0 = { 0.2, 0.2, 0.2 }, size1 = { 1.1, 1.0, 1.05 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.65 }),
				-- светящиеся точки на шляпках
				M("ball", "#9AFFB0", { count = 4, r = 1.6, t0 = 0.2, t1 = 0.5, size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.25, 0.25, 0.25 }, a0 = 0, a1 = 0.3, y0 = 1.0, y1 = 1.1, hold = 0.65 }),
			},
		},
	},

	-- 43 ---------------------------------------------------------------------
	bone_glaive = {
		idle = {
			emitters = {
				I("dust", "#F2E8CC", "#CDB890", 0.08, 6, { t0 = 0.3, life = { 1.5, 1.5 } }),
				glint("#FFE090", 1.5, 0.14, { texture = "star" }),
			},
			light = { color = "#FFD890", range = 8, brightness = 0.7 },
		},
		flight = {
			emitters = {
				F("shard", "#F4EAD0", "#D8C4A0", 0.5, 0.5, 10, { rot = 500, life = { 1, 1 }, t0 = 0 }),
				F("dust", "#F2E8CC", "#CDB890", 0.6, 0, 9, { smid = 1.8, t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
				F("shard", "#D8C4A0", "#D8C4A0", 0.4, 0.4, 4, { rot = 400, life = { 1, 1 }, t0 = 0 }),
				F("spark", "#FFE090", "#FFE090", 0.12, 0.12, 6, { t0 = 0, life = { 0.8, 0.8 }, speed = { 3, 5 }, spread = 60 }),
			},
			rings = { fring("bone_ring", "#FFA028", 0.33, 6.5, 2.1, 0.6) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFD890", range = 10, brightness = 1.5, t1 = 0.4 },
			bursts = {
				B("shard", "#F4EAD0", "#8A7A6A", 10, 0.25, 0.25, { 6, 10 }, { 1.0, 1.1 }, { delay = 0, t0 = 0, accel = { 0, -25, 0 }, spread = 60, rot = 300 }),
				B("dust", "#F2E8CC", "#CDB890", 14, 0.8, 2.3, { 3, 3 }, { 1.2, 1.3 }, { delay = 0, t0 = 0.1, spread = 80, dir = "out", drag = 3 }),
				B("spark", "#FFE090", "#FFE090", 8, 0.14, 0.14, { 3, 6 }, { 1.0, 1.0 }, { delay = 0, t0 = 0, light = 1, spread = 90 }),
			},
			meshes = {
				M("ball", "#FFF0C8", { t0 = 0, t1 = 0.4, size0 = { 0.8, 0.8, 0.8 }, size1 = { 3.6, 3.6, 3.6 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				-- костяной вал по земле
				M("bone_ring", "#F4EAD0", { neon = false, t0 = 0.07, t1 = 0.4, size0 = { 1.8, 0.09, 1.8 }, size1 = { 4.0, 0.09, 4.0 }, a0 = 0, a1 = 0, y0 = 0.1, y1 = 0.1, easing = "Back", hold = 0.8 }),
				-- 10 рёбер вырастают кругом (грудная клетка)
				M("rib", "#F4EAD0", { count = 5, r = 2.1, neon = false, t0 = 0.07, t1 = 0.5, size0 = { 0.4, 0.1, 0.07 }, size1 = { 1.89, 2.47, 0.33 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.7 }),
				M("rib", "#D8C4A0", { count = 5, r = 2.1, neon = false, t0 = 0.13, t1 = 0.56, size0 = { 0.4, 0.1, 0.07 }, size1 = { 1.89, 2.47, 0.33 }, a0 = 0, a1 = 0, easing = "Back", hold = 0.65 }),
				-- 5 позвонков
				M("vertebra", "#F4EAD0", { count = 5, r = 1.6, neon = false, t0 = 0, t1 = 1.2, size0 = { 0.36, 0.24, 0.34 }, size1 = { 0.04, 0.03, 0.04 }, a0 = 0, a1 = 0, y0 = 1.5, y1 = 0.1, spin = 300, easing = "Bounce" }),
			},
		},
	},

	-- 44 ---------------------------------------------------------------------
	pearl_lance = {
		idle = {
			emitters = {
				I("bubble", "#DFFBFF", "#DFFBFF", 0.15, 7, { life = { 1.8, 1.8 }, dir = "up", speed = { 0.4, 0.4 }, spread = 30 }),
				glint("#FFF0B0", 1.5, 0.14),
			},
			light = { color = "#C8F8FF", range = 8, brightness = 0.8 },
		},
		flight = {
			emitters = {
				F("bubble", "#DFFBFF", "#DFFBFF", 0.2, 0, 14, { smid = 0.6, t0 = 0.1, speed = { 2, 4 }, spread = 25, life = { 1, 1 } }),
				F("bubble", "#F6F0FF", "#F6F0FF", 0.2, 0.2, 8, { t0 = 0, life = { 1, 1 } }),
				F("crystal", "#FFB0C8", "#FF7A68", 0.5, 0.5, 6, { rot = 300, life = { 1, 1 }, t0 = 0 }),
			},
			rings = {}, -- у pearl_lance нет меша кольца, кольца полёта опущены
		},
		impact = {
			duration = 1.5,
			light = { color = "#C8F8FF", range = 11, brightness = 1.5, t1 = 1.0 },
			bursts = {
				B("bubble", "#DFFBFF", "#DFFBFF", 10, 0.3, 0.3, { 3, 6 }, { 1.1, 1.3 }, { delay = 0.07, t0 = 0.2, spread = 30 }),
				B("star", "#FFF0B0", "#FFF0B0", 8, 0.2, 0.2, { 3, 6 }, { 0.9, 1.0 }, { delay = 0.1, t0 = 0, light = 1, dir = "out", spread = 150 }),
			},
			meshes = {
				M("ball", "#FFFFFF", { t0 = 0, t1 = 0.4, size0 = { 0.8, 0.8, 0.8 }, size1 = { 3.6, 3.6, 3.6 }, a0 = 0, a1 = 1, y0 = 0.8, y1 = 0.8 }),
				-- пузырь-купол вырастает и лопается
				M("bubble_dome", "#D8FCFF", { neon = false, t0 = 0.13, t1 = 1.3, size0 = { 2, 2, 2 }, size1 = { 5.4, 5.4, 4.2 }, a0 = 0.4, a1 = 1, easing = "Quad" }),
				-- 7 створок-ракушек веером
				M("shell_rib", "#FF7A68", { count = 4, r = 1.3, neon = false, t0 = 0.1, t1 = 0.7, size0 = { 0.3, 0.02, 0.14 }, size1 = { 2.25, 0.15, 1.08 }, a0 = 0, a1 = 0, y0 = 0.1, y1 = 0.1, easing = "Back", hold = 0.5 }),
				M("shell_rib", "#FFB0C8", { count = 3, r = 1.9, neon = false, t0 = 0.2, t1 = 0.8, size0 = { 0.3, 0.02, 0.14 }, size1 = { 2.25, 0.15, 1.08 }, a0 = 0, a1 = 0, y0 = 0.1, y1 = 0.1, easing = "Back", hold = 0.4 }),
				-- 11 ледяных шипов веером-раковиной
				M("ice_spike", "#C8F6FF", { count = 6, r = 1.4, t0 = 0.07, t1 = 0.45, size0 = { 0.1, 0.2, 0.1 }, size1 = { 0.32, 1.3, 0.28 }, a0 = 0.2, a1 = 0.2, easing = "Back", hold = 0.7 }),
				M("ice_spike", "#C8F6FF", { count = 5, r = 2.0, t0 = 0.1, t1 = 0.5, size0 = { 0.1, 0.2, 0.1 }, size1 = { 0.4, 1.9, 0.35 }, a0 = 0.2, a1 = 0.2, easing = "Back", hold = 0.65 }),
				-- 9 жемчужин
				M("pearl", "#F6F0FF", { count = 9, r = 2.0, neon = false, t0 = 0, t1 = 1.2, size0 = { 0.28, 0.28, 0.26 }, size1 = { 0.03, 0.03, 0.03 }, a0 = 0, a1 = 0, y0 = 1.0, y1 = 0.15, easing = "Bounce" }),
			},
		},
	},

	-- 45 ---------------------------------------------------------------------
	rift_conductor = {
		idle = {
			emitters = {
				I("spark", "#F4EAFF", "#7AF0FF", 0.06, 7, { life = { 1.2, 1.2 }, speed = { 0.5, 0.5 } }),
				glint("#F4EAFF", 1.5, 0.15, { texture = "star", life = { 0.4, 0.4 } }),
			},
			light = { color = "#B070FF", range = 9, brightness = 1 },
		},
		flight = {
			emitters = {
				F("bolt", "#F4EAFF", "#7AF0FF", 0.9, 0.9, 9, { rot = 300, life = { 1, 1 }, t0 = 0, light = 1 }),
				F("spark", "#F4EAFF", "#F4EAFF", 0.12, 0.12, 10, { t0 = 0, speed = { 4, 6 }, spread = 45, life = { 0.8, 0.8 }, light = 1 }),
				F("smoke", "#5A2A90", "#5A2A90", 0.6, 0, 6, { smid = 1.6, t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
			},
			rings = { fring("electric_ring", "#B45CFF", 0.5, 6.8), fring("electric_ring", "#7AF0FF", 1.0, 6.8) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#B070FF", range = 13, brightness = 3, t1 = 1.0 },
			bursts = {
				B("spark", "#F4EAFF", "#7AF0FF", 12, 0.14, 0.14, { 2, 6 }, { 0.9, 1.0 }, { delay = 0.2, t0 = 0, light = 1, accel = { 0, 1, 0 }, spread = 90, dir = "out" }),
				B("bolt", "#B45CFF", "#7AF0FF", 6, 0.9, 0.9, { 0.5, 1 }, { 0.15, 0.3 }, { delay = 0.1, t0 = 0, light = 1, dir = "out", spread = 180 }),
			},
			meshes = {
				-- 8 узлов-шаров по кругу r 3.1 на высоте ~2.5 зажигаются по очереди
				M("node", "#F4EAFF", { count = 4, r = 3.1, t0 = 0.03, t1 = 0.13, size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.39, 0.42, 0.39 }, a0 = 0, a1 = 0, y0 = 2.5, y1 = 2.5, hold = 0.6 }),
				M("node", "#7AF0FF", { count = 4, r = 3.1, t0 = 0.1, t1 = 0.2, size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.39, 0.42, 0.39 }, a0 = 0, a1 = 0, y0 = 2.6, y1 = 2.6, hold = 0.5 }),
				-- молнии от узлов в копьё (приближение: 2 слоя меша bolt вспыхивают)
				M("bolt", "#B45CFF", { count = 8, r = 1.6, t0 = 0.1, t1 = 0.2, size0 = { 0.3, 0.2, 0.1 }, size1 = { 3.35, 1.75, 0.66 }, a0 = 0, a1 = 0.3, y0 = 1.4, y1 = 1.4, easing = "Linear", hold = 0.4 }),
				M("bolt", "#F4EAFF", { count = 8, r = 1.6, t0 = 0.13, t1 = 0.23, size0 = { 0.3, 0.2, 0.1 }, size1 = { 2.5, 1.3, 0.3 }, a0 = 0, a1 = 0.3, y0 = 1.4, y1 = 1.4, easing = "Linear", hold = 0.35 }),
				-- электрическое ядро у острия
				M("ball", "#E8C8FF", { t0 = 0.07, t1 = 0.87, size0 = { 1.0, 1.0, 1.0 }, size1 = { 4.3, 4.3, 4.3 }, a0 = 0, a1 = 1, y0 = 1.2, y1 = 1.2, easing = "Sine" }),
				-- три кольца электричества, тоньше с каждым
				M("electric_ring", "#B45CFF", { t0 = 0.17, t1 = 1.2, size0 = { 1.2, 0.14, 1.2 }, size1 = { 6.2, 0.14, 6.2 }, a0 = 0, a1 = 1, y0 = 0.1, y1 = 0.1 }),
				M("electric_ring", "#F4EAFF", { t0 = 0.27, t1 = 1.2, size0 = { 1.2, 0.1, 1.2 }, size1 = { 5.5, 0.1, 5.5 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 0.15 }),
				M("electric_ring", "#7AF0FF", { t0 = 0.37, t1 = 1.2, size0 = { 1.2, 0.06, 1.2 }, size1 = { 4.8, 0.06, 4.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 0.2 }),
				M("ground_crack", "#B45CFF", { count = 6, r = 1.2, t0 = 0.3, t1 = 0.9, size0 = { 0.3, 0.05, 0.1 }, size1 = { 1.31, 0.22, 0.61 }, a0 = 0, a1 = 0.3, y0 = 0.05, y1 = 0.05, hold = 0.27 }),
			},
		},
	},

	-- 46 ---------------------------------------------------------------------
	primal_fang = {
		idle = {
			emitters = {
				I("fire", "#FFC23A", "#FF5A14", 0.2, 8, { life = { 1, 1 }, speed = { 0.2, 0.5 }, dir = "up", accel = { 0, 1.5, 0 }, light = 1 }),
			},
			light = { color = "#FF7A2A", range = 6, brightness = 1.2 },
		},
		flight = {
			emitters = {
				-- языки пламени кометы
				F("fire", "#FF5A14", "#E0302A", 0.9, 0.5, 14, { t0 = 0, speed = { 9, 12 }, spread = 8, light = 1 }),
				F("spark", "#FFC23A", "#FFC23A", 0.12, 0.12, 12, { t0 = 0, speed = { 4, 4 }, spread = 45, light = 1 }),
				F("smoke", "#4A3440", "#4A3440", 0.4, 1.8, 8, { t0 = 0.2, speed = { 1, 2 }, spread = 25, life = { 1, 1 } }),
			},
			rings = { fring("fire_ring", "#FF5A14", 0.33, 6, 2.0) },
			light = { color = "#FF7A2A", range = 10, brightness = 2 },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF7A2A", range = 14, brightness = 6, t1 = 1.3 },
			bursts = {
				puff("#4A3440", 10, 0.13, 2.4, 1.2, { t0 = 0.1, speed = { 2, 3 } }),
			},
			meshes = {
				flash("#FFD08A", 0.5, 1.6, 0, 0.33),
				-- центральный столб огня
				M("flame", "#FFC23A", { t0 = 0, t1 = 0.17, size0 = { 0.3, 0.3, 0.3 }, size1 = { 1.39, 2.6, 1.39 }, a0 = 0, a1 = 0.3, hold = 0.43 }),
				-- 9 светящихся трещин лучами
				cracks("#FF6A1A", 9, 2.1, 0, 0.23, { a1 = 0.2, hold = 0.8 }),
				ring("lava_ring", "#FF6A1A", 1.8, 3.1, 0.07, 0.37, { a0 = 0, a1 = 0.3, hold = 0.9 }),
				-- 7 огненных столбов по кругу r 1.45
				M("flame", "#FF5A14", { count = 3, r = 1.45, t0 = 0.1, t1 = 0.4, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.85, 2.0, 0.85 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.5 }),
				M("flame", "#FFC23A", { count = 2, r = 1.45, t0 = 0.13, t1 = 0.43, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.85, 2.0, 0.85 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.5 }),
				M("flame", "#E0302A", { count = 2, r = 1.45, t0 = 0.16, t1 = 0.46, size0 = { 0.2, 0.2, 0.2 }, size1 = { 0.85, 2.0, 0.85 }, a0 = 0, a1 = 0.3, easing = "Back", hold = 0.5 }),
				-- 10 расплавленных камней падают вокруг
				M("molten_rock", "#3A2F45", { count = 5, r = 2.2, neon = false, t0 = 0, t1 = 1.1, size0 = { 0.21, 0.3, 0.2 }, size1 = { 0.04, 0.06, 0.04 }, a0 = 0, a1 = 0, y0 = 2.0, y1 = 0.1, spin = 200, easing = "Bounce" }),
				M("molten_rock", "#FF6A1A", { count = 5, r = 2.8, t0 = 0, t1 = 1.1, size0 = { 0.21, 0.3, 0.2 }, size1 = { 0.04, 0.06, 0.04 }, a0 = 0, a1 = 0, y0 = 2.4, y1 = 0.1, spin = -200, easing = "Bounce" }),
			},
		},
	},
}
