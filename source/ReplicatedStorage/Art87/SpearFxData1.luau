-- V87: эффекты копий 1-23 по docs/concepts_v86/fx_table.md (данные для Art87/SpearFx87)
-- Схема: docs/concepts_v87/roblox/SPEAR_FX_SCHEMA.md. Время в секундах от касания, размеры в studs.

-- вспышка-сфера r 0.5 -> r (диаметр = 2r)
local function flash(color, r, a0, t1, y)
	return {
		mesh = "ball", color = color, neon = true, t0 = 0, t1 = t1 or 0.33,
		size0 = { 1, 1, 1 }, size1 = { r * 2, r * 2, r * 2 }, a0 = a0 or 0.3, a1 = 1,
		y0 = y or 0.5, y1 = y or 0.5, easing = "Quad",
	}
end

-- плоское ударное кольцо по земле от r 0.15 до r
local function ring(mesh, color, r, t1, a0, t0)
	return {
		mesh = mesh, color = color, neon = true, t0 = t0 or 0, t1 = t1 or 0.4,
		size0 = { 0.3, 0.1, 0.3 }, size1 = { r * 2, 0.1, r * 2 }, a0 = a0 or 0, a1 = 1, easing = "Quad",
	}
end

-- веер тёмных трещин по земле (узкие Part)
local function cracks(color, n, len, t1, r)
	return {
		mesh = "part", color = color, count = n, r = r or 0.5, t0 = 0, t1 = t1 or 0.13,
		size0 = { 0.08, 0.04, 0.05 }, size1 = { 0.08, 0.04, len }, a0 = 0, a1 = 0,
		hold = 1.0, easing = "Quad",
	}
end

-- рост из земли (Back Out) и удержание
local function grow(mesh, color, count, r, t0, t1, w, h, hold, neon, spin)
	return {
		mesh = mesh, color = color, neon = neon or false, count = count, r = r, t0 = t0, t1 = t1,
		size0 = { 0.05, 0.05, 0.05 }, size1 = { w, h, w }, a0 = 0, a1 = 0, hold = hold or 0.8,
		spin = spin, easing = "Back",
	}
end

-- клубы пыли / дыма: кольцом расходятся и растут
local function puffs(count, c0, c1, s1, delay, life)
	return {
		at = "ground", texture = "dust", c0 = c0, c1 = c1, s0 = 0.4, s1 = s1 or 2.4, t0 = 0.1, t1 = 1,
		count = count, delay = delay or 0, life = { life or 1.3, life or 1.3 }, speed = { 3, 3 }, spread = 180,
		dir = "out", drag = 3,
	}
end

-- вылет по дуге (камни, осколки, капли)
local function arc(texture, count, c0, c1, size, speed, life, accel, spread, light)
	return {
		at = "ground", texture = texture, c0 = c0, c1 = c1, s0 = size, s1 = size * 0.6, t0 = 0, t1 = 1,
		count = count, life = { life or 1.1, life or 1.1 }, speed = speed or { 6, 10 }, spread = spread or 25,
		dir = "up", accel = { 0, accel or -25, 0 }, rot = 360, light = light,
	}
end

local function delayed(b, d)
	b.delay = d
	return b
end

local function glint(color, rate)
	return {
		at = "tip", texture = "star", c0 = color, c1 = color, s0 = 0.15, s1 = 0.15, t0 = 0, t1 = 1, rate = rate,
		life = { 0.4, 0.4 }, speed = { 0, 0.2 }, spread = 180, dir = "out", light = 1,
	}
end

local function airRing(mesh, color, s1, a0)
	return { mesh = mesh, color = color, every = 0.33, s0 = 0.6, s1 = s1 or 2.0, travel = 6.5, life = 1, a0 = a0 or 0.2 }
end

return {

	-- 01 ----------------------------------------------------------------
	stick = {
		idle = {
			emitters = {
				{ at = "tip", texture = "dust", c0 = "#F1DFB8", c1 = "#C99F6C", s0 = 0.1, s1 = 0.12, t0 = 0.3, t1 = 1,
					rate = 4, life = { 1.2, 1.8 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.3, 0 } },
				glint("#FFF6D8", 1.5),
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "dust", c0 = "#F1DFB8", c1 = "#C99F6C", s0 = 0.3, smid = 1.2, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 12, life = { 0.9, 0.9 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
				{ at = "trail", texture = "rock", c0 = "#9A9184", c1 = "#8A5530", s0 = 0.15, s1 = 0.15, t0 = 0, t1 = 1,
					rate = 7, life = { 0.8, 0.8 }, speed = { 3, 5 }, spread = 25, dir = "back", rot = 360 },
			},
			rings = { airRing("air_ring", "#FFF2D2", 2.0) },
		},
		impact = {
			duration = 1.5,
			bursts = {
				puffs(14, "#F1DFB8", "#C99F6C", 2.5),
				arc("rock", 12, "#9A9184", "#8A5530", 0.3, { 6, 10 }),
			},
			meshes = {
				{ mesh = "crater", color = "#8A5530", t0 = 0, t1 = 0.2, size0 = { 1.1, 0.3, 1.1 }, size1 = { 2.0, 0.3, 2.0 },
					a0 = 0, a1 = 0, hold = 1.0, easing = "Back" },
				cracks("#5A321C", 6, 1.5),
				ring("shock_ring", "#FFF0CC", 2.5, 0.4),
			},
		},
	},

	-- 02 ----------------------------------------------------------------
	bone = {
		idle = {
			emitters = {
				{ at = "tip", texture = "dust", c0 = "#F4ECD6", c1 = "#CFC09A", s0 = 0.1, s1 = 0.12, t0 = 0.3, t1 = 1,
					rate = 4, life = { 1.2, 1.8 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.3, 0 } },
				glint("#FFFBE6", 1.5),
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "dust", c0 = "#F4ECD6", c1 = "#CFC09A", s0 = 0.3, smid = 1.2, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 10, life = { 0.9, 0.9 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
				{ at = "trail", texture = "shard", c0 = "#F1E6C8", c1 = "#CDB68A", s0 = 0.3, s1 = 0.3, t0 = 0, t1 = 1,
					rate = 8, life = { 1, 1 }, speed = { 4, 6 }, spread = 20, dir = "back", rot = 360 },
				{ at = "trail", texture = "sparkle", c0 = "#FFFBE6", c1 = "#FFFBE6", s0 = 0.1, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 4, life = { 0.8, 0.8 }, speed = { 1, 2 }, spread = 30, dir = "back", light = 1 },
			},
			rings = { airRing("dust_ring", "#FFF6DC", 2.0) },
		},
		impact = {
			duration = 1.5,
			bursts = {
				{ at = "ground", texture = "dust", c0 = "#F4ECD6", c1 = "#CFC09A", s0 = 0.4, s1 = 2.2, t0 = 0.1, t1 = 1,
					count = 14, life = { 1.3, 1.3 }, speed = { 3, 3 }, spread = 15, dir = "out", drag = 3 },
				arc("rock", 20, "#A59C8C", "#CDB68A", 0.3, { 6, 10 }),
			},
			meshes = {
				{ mesh = "crater", color = "#CDB68A", t0 = 0, t1 = 0.2, size0 = { 1.0, 0.3, 1.0 }, size1 = { 1.8, 0.3, 1.8 },
					a0 = 0, a1 = 0, hold = 1.0, easing = "Back" },
				cracks("#4A3A36", 5, 1.3),
				ring("dust_ring", "#FFF6DC", 2.3, 0.4),
				-- 5 костяных заноз веером за копьём (по кругу r 1.6)
				grow("bone_splinter", "#F1E6C8", 5, 1.6, 0, 0.47, 0.18, 0.9, 0.5),
				grow("pebble", "#A59C8C", 4, 1.3, 0, 0.3, 0.3, 0.3, 0.7),
				grow("chip", "#CDB68A", 3, 1.1, 0, 0.3, 0.3, 0.3, 0.7),
			},
		},
	},

	-- 03 ----------------------------------------------------------------
	bronze = {
		idle = {
			emitters = {
				glint("#FFF1C0", 2),
				{ at = "tip", texture = "spark", c0 = "#FFD27A", c1 = "#FFD27A", s0 = 0.1, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 4, life = { 1, 1 }, speed = { 0.3, 0.3 }, spread = 180, dir = "out", light = 1 },
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "spark", c0 = "#FFD27A", c1 = "#FFF1C0", s0 = 0.25, smid = 0.35, s1 = 0, t0 = 0,
					t1 = 1, rate = 14, life = { 1, 1 }, speed = { 11, 12 }, spread = 8, dir = "back", light = 1 },
				{ at = "trail", texture = "shard", c0 = "#E8B35A", c1 = "#C98A3A", s0 = 0.25, s1 = 0.2, t0 = 0, t1 = 1,
					rate = 6, life = { 1, 1 }, speed = { 12, 13 }, spread = 6, dir = "back", rot = 720 },
				{ at = "trail", texture = "dust", c0 = "#D9C9A0", c1 = "#D9C9A0", s0 = 0.3, s1 = 1.2, t0 = 0.2, t1 = 1,
					rate = 4, life = { 1, 1 }, speed = { 1, 2 }, spread = 25, dir = "back" },
			},
			rings = { airRing("shock_ring", "#FFB347", 2.1) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFB347", range = 8, brightness = 3, t1 = 0.4 },
			bursts = {
				{ at = "ground", texture = "spark", c0 = "#FFD27A", c1 = "#FFF1C0", s0 = 0.3, s1 = 0.1, t0 = 0, t1 = 1,
					count = 18, life = { 0.87, 0.87 }, speed = { 7, 10 }, spread = 42, dir = "forward",
					accel = { 0, -27, 0 }, light = 1 },
				{ at = "ground", texture = "spark", c0 = "#FFD27A", c1 = "#FFF1C0", s0 = 0.25, s1 = 0.1, t0 = 0, t1 = 1,
					count = 6, life = { 0.87, 0.87 }, speed = { 3, 5 }, spread = 40, dir = "back",
					accel = { 0, -27, 0 }, light = 1 },
				arc("shard", 6, "#E8B35A", "#9A5F26", 0.3, { 3, 5 }),
				puffs(6, "#D9C9A0", "#D9C9A0", 1.8, 0.1, 1.2),
			},
			meshes = {
				flash("#FFE2A0", 1.4, 0.2),
				ring("shock_ring", "#FFB347", 2.6, 0.43, 0, 0),
				ring("shock_ring", "#FFB347", 2.1, 0.6, 0, 0.17),
				-- три вертикальных гонга на высоте 1.0
				{ mesh = "gong_ring", color = "#FFB347", neon = true, t0 = 0, t1 = 0.6, size0 = { 0.3, 0.3, 0.3 },
					size1 = { 2.4, 2.4, 0.3 }, a0 = 0, a1 = 1, y0 = 1, y1 = 1, easing = "Quad" },
				{ mesh = "gong_ring", color = "#FFB347", neon = true, t0 = 0.13, t1 = 0.73, size0 = { 0.3, 0.3, 0.3 },
					size1 = { 3.0, 3.0, 0.3 }, a0 = 0, a1 = 1, y0 = 1, y1 = 1, easing = "Quad" },
				{ mesh = "gong_ring", color = "#FFB347", neon = true, t0 = 0.27, t1 = 0.87, size0 = { 0.3, 0.3, 0.3 },
					size1 = { 3.4, 3.4, 0.3 }, a0 = 0, a1 = 1, y0 = 1, y1 = 1, easing = "Quad" },
				{ mesh = "cyl", color = "#FFC566", neon = true, t0 = 0, t1 = 0.4, size0 = { 1.0, 0.1, 1.0 },
					size1 = { 2.6, 0.1, 2.6 }, a0 = 0.3, a1 = 1, y0 = 1, y1 = 1, easing = "Quad" },
				{ mesh = "dent", color = "#6B4A30", t0 = 0, t1 = 0.2, size0 = { 1.0, 0.2, 1.0 }, size1 = { 1.12, 0.2, 1.12 },
					a0 = 0, a1 = 0, hold = 0.9, easing = "Back" },
			},
		},
	},

	-- 04 ----------------------------------------------------------------
	feather = {
		idle = {
			emitters = {
				{ at = "tip", texture = "feather", c0 = "#E0483A", c1 = "#3D7FD9", s0 = 0.25, s1 = 0.2, t0 = 0.1, t1 = 1,
					rate = 2, life = { 2, 2 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, -0.3, 0 },
					rot = 60 },
				glint("#FFFBE0", 1.5),
			},
		},
		flight = {
			emitters = {
				-- летящие перья (разноцветные)
				{ at = "trail", texture = "feather", c0 = "#E0483A", c1 = "#3D7FD9", s0 = 0.4, smid = 0.6, s1 = 0, t0 = 0,
					t1 = 1, rate = 10, life = { 1, 1 }, speed = { 11, 12 }, spread = 8, dir = "back", rot = 360 },
				{ at = "trail", texture = "feather", c0 = "#F4C542", c1 = "#F08A30", s0 = 0.4, smid = 0.6, s1 = 0, t0 = 0,
					t1 = 1, rate = 6, life = { 1, 1 }, speed = { 11, 12 }, spread = 8, dir = "back", rot = 360 },
				{ at = "trail", texture = "smoke", c0 = "#FFFAF0", c1 = "#FFFAF0", s0 = 0.2, smid = 0.9, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 2, 3 }, spread = 30, dir = "back" },
				{ at = "trail", texture = "leaf", c0 = "#5FBF4A", c1 = "#3C9A3A", s0 = 0.3, s1 = 0.3, t0 = 0, t1 = 1,
					rate = 6, life = { 1, 1 }, speed = { 3, 5 }, spread = 30, dir = "back", rot = 300 },
			},
			rings = {},
		},
		impact = {
			duration = 1.5,
			light = { color = "#D8FFA8", range = 6, brightness = 1.5, t1 = 0.4 },
			bursts = {
				{ at = "ground", texture = "smoke", c0 = "#FFFAF0", c1 = "#FFFAF0", s0 = 0.3, s1 = 1.2, t0 = 0.2, t1 = 1,
					count = 6, life = { 1.2, 1.2 }, speed = { 1, 2 }, spread = 60, dir = "up", accel = { 0, 1, 0 } },
			},
			meshes = {
				flash("#F4FFD0", 1.4, 0.4),
				ring("leaf_ring", "#D8FFA8", 2.5, 0.43),
				-- 18 перьев спиралью вверх, по цветам
				{ mesh = "feather", color = "#E0483A", count = 6, r = 1.0, t0 = 0, t1 = 1.2, size0 = { 0.2, 0.2, 0.2 },
					size1 = { 0.3, 0.9, 0.3 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 2.4, spin = 360, easing = "Sine" },
				{ mesh = "feather", color = "#2BB5A8", count = 6, r = 1.2, t0 = 0, t1 = 1.2, size0 = { 0.2, 0.2, 0.2 },
					size1 = { 0.3, 0.9, 0.3 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 3.0, spin = -360, easing = "Sine" },
				{ mesh = "feather", color = "#F4C542", count = 6, r = 0.8, t0 = 0, t1 = 1.2, size0 = { 0.2, 0.2, 0.2 },
					size1 = { 0.3, 0.9, 0.3 }, a0 = 0, a1 = 1, y0 = 0.15, y1 = 1.8, spin = 360, easing = "Sine" },
				{ mesh = "grass_blade", color = "#5FBF4A", count = 8, r = 1.5, t0 = 0.03, t1 = 0.4,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.14, 0.65, 0.14 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
			},
		},
	},

	-- 05 ----------------------------------------------------------------
	iron = {
		idle = {
			emitters = {
				glint("#FFD27A", 1.5),
				{ at = "tip", texture = "spark", c0 = "#FF9A3A", c1 = "#FF9A3A", s0 = 0.08, s1 = 0.06, t0 = 0, t1 = 1,
					rate = 4, life = { 1, 1 }, speed = { 0.3, 0.3 }, spread = 180, dir = "out", light = 1 },
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "spark", c0 = "#FF9A3A", c1 = "#FFD27A", s0 = 0.25, smid = 0.35, s1 = 0, t0 = 0,
					t1 = 1, rate = 12, life = { 1, 1 }, speed = { 11, 12 }, spread = 8, dir = "back", light = 1 },
				{ at = "trail", texture = "rock", c0 = "#6A7480", c1 = "#C4602A", s0 = 0.18, s1 = 0.18, t0 = 0, t1 = 1,
					rate = 6, life = { 0.9, 0.9 }, speed = { 4, 6 }, spread = 25, dir = "back", rot = 360 },
				{ at = "trail", texture = "dust", c0 = "#DCC592", c1 = "#B69A68", s0 = 0.3, smid = 1.4, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back" },
			},
			rings = { airRing("iron_ring", "#FFC27A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF9A3A", range = 8, brightness = 2, t1 = 0.4 },
			bursts = {
				puffs(10, "#DCC592", "#B69A68", 2.4),
				arc("rock", 10, "#A89C84", "#4A5360", 0.3, { 6, 10 }),
				{ at = "ground", texture = "spark", c0 = "#FF9A3A", c1 = "#FFD27A", s0 = 0.3, s1 = 0.1, t0 = 0, t1 = 1,
					count = 14, life = { 0.5, 0.6 }, speed = { 4, 8 }, spread = 12, dir = "forward",
					accel = { 0, -15, 0 }, light = 1 },
			},
			meshes = {
				flash("#FFB15A", 1.4, 0.4),
				-- 4 каменные плиты вокруг копья (r 1.35)
				{ mesh = "slab", color = "#A89C84", count = 4, r = 1.35, t0 = 0, t1 = 0.3, size0 = { 0.3, 0.1, 0.2 },
					size1 = { 1.15, 0.3, 0.85 }, a0 = 0, a1 = 0, y0 = 0, y1 = 0.3, hold = 1.0, easing = "Back" },
				cracks("#4A5360", 4, 1.5),
				{ mesh = "groove", color = "#4A5360", t0 = 0, t1 = 0.33, size0 = { 0.01, 0.2, 0.05 },
					size1 = { 4.0, 0.2, 0.05 }, a0 = 0, a1 = 0, hold = 0.9, easing = "Quad" },
				{ mesh = "spark", color = "#FF9A3A", neon = true, count = 5, r = 0.5, t0 = 0, t1 = 0.6,
					size0 = { 0.2, 0.05, 0.05 }, size1 = { 0.5, 0.05, 0.05 }, a0 = 0, a1 = 1, easing = "Quad" },
				{ mesh = "pebble", color = "#A89C84", count = 5, r = 1.2, t0 = 0, t1 = 0.3, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.3, 0.3, 0.3 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
			},
		},
	},

	-- 06 ----------------------------------------------------------------
	obsidian = {
		idle = {
			emitters = {
				glint("#E8D2FF", 1.5),
				{ at = "tip", texture = "shard", c0 = "#2A2236", c1 = "#2A2236", s0 = 0.1, s1 = 0.16, t0 = 0, t1 = 1,
					rate = 3, life = { 1.5, 1.5 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", rot = 120 },
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "shard", c0 = "#2A2236", c1 = "#5A3F8A", s0 = 0.4, smid = 0.5, s1 = 0, t0 = 0,
					t1 = 1, rate = 12, life = { 1, 1 }, speed = { 11, 12 }, spread = 12, dir = "back", rot = 540 },
				{ at = "trail", texture = "spark", c0 = "#FF6A4A", c1 = "#FFC7A0", s0 = 0.12, s1 = 0.12, t0 = 0, t1 = 1,
					rate = 8, life = { 0.9, 0.9 }, speed = { 4, 4 }, spread = 40, dir = "back", light = 1 },
				{ at = "trail", texture = "smoke", c0 = "#4A3858", c1 = "#4A3858", s0 = 0.3, s1 = 1.2, t0 = 0.2, t1 = 1,
					rate = 4, life = { 1, 1 }, speed = { 1, 2 }, spread = 25, dir = "back" },
			},
			rings = { airRing("ember_ring", "#FF5A3A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF5A3A", range = 8, brightness = 2.5, t1 = 0.5 },
			bursts = {
				delayed(arc("shard", 24, "#2A2236", "#5A3F8A", 0.3, { 3, 6 }, 0.7, -27, 60), 0.5),
				{ at = "ground", texture = "star", c0 = "#E8D2FF", c1 = "#E8D2FF", s0 = 0.3, s1 = 0.3, t0 = 0, t1 = 1,
					count = 6, delay = 0.5, life = { 0.5, 0.5 }, speed = { 1, 2 }, spread = 90, dir = "up", light = 1 },
			},
			meshes = {
				flash("#9A6AF0", 1.4, 0.4),
				ring("ember_ring", "#FF5A3A", 2.5, 0.43),
				-- 6 светящихся трещин, гаснут к 1.0 с
				{ mesh = "part", color = "#FF5A3A", neon = true, count = 6, r = 0.9, t0 = 0.03, t1 = 0.27,
					size0 = { 0.12, 0.04, 0.05 }, size1 = { 0.12, 0.04, 1.8 }, a0 = 0, a1 = 0.2, hold = 0.7, easing = "Quad" },
				-- внутренние фиолетовые шипы r 0.8 и внешние чёрные r 1.55; раскалываются на 0.5
				{ mesh = "glass_spike", color = "#5A3F8A", count = 6, r = 0.8, t0 = 0.03, t1 = 0.27,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.4, 1.0, 0.4 }, a0 = 0, a1 = 0, hold = 0.2, easing = "Back" },
				{ mesh = "glass_spike", color = "#2A2236", count = 6, r = 1.55, t0 = 0.1, t1 = 0.27,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.5, 1.7, 0.5 }, a0 = 0, a1 = 0, hold = 0.15, easing = "Back" },
				{ mesh = "glass_shard", color = "#2A2236", count = 8, r = 1.6, t0 = 0.5, t1 = 1.0,
					size0 = { 0.3, 0.3, 0.3 }, size1 = { 0.3, 0.3, 0.3 }, a0 = 0, a1 = 1, spin = 600, easing = "Quad" },
			},
		},
	},

	-- 07 ----------------------------------------------------------------
	crystal = {
		idle = {
			emitters = {
				glint("#F0FCFF", 2),
				{ at = "tip", texture = "crystal", c0 = "#6FC8FF", c1 = "#6FC8FF", s0 = 0.08, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 3, life = { 1.5, 1.5 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", light = 0.8 },
			},
			light = { color = "#7FE6FF", range = 5, brightness = 0.6 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "crystal", c0 = "#6FC8FF", c1 = "#9A8AFF", s0 = 0.36, smid = 0.4, s1 = 0, t0 = 0,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 11, 12 }, spread = 8, dir = "back", rot = 540, light = 1 },
				{ at = "trail", texture = "star", c0 = "#F0FCFF", c1 = "#5FF0FF", s0 = 0.3, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 8, life = { 1, 1 }, speed = { 3, 5 }, spread = 25, dir = "back", light = 1 },
				{ at = "trail", texture = "sparkle", c0 = "#F0FCFF", c1 = "#F0FCFF", s0 = 0.1, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 4, life = { 0.9, 0.9 }, speed = { 1, 3 }, spread = 30, dir = "back", light = 1 },
			},
			rings = { { mesh = "chime_ring", color = "#7FE6FF", every = 0.25, s0 = 0.5, s1 = 2.1, travel = 7, life = 1, a0 = 0.2 } },
		},
		impact = {
			duration = 1.5,
			light = { color = "#7FE6FF", range = 9, brightness = 3, t1 = 0.7 },
			bursts = {
				{ at = "ground", texture = "star", c0 = "#F0FCFF", c1 = "#5FF0FF", s0 = 0.3, s1 = 0.1, t0 = 0, t1 = 1,
					count = 22, life = { 0.7, 0.9 }, speed = { 1, 3 }, spread = 60, dir = "up", accel = { 0, 3, 0 }, light = 1 },
			},
			meshes = {
				flash("#C8F8FF", 1.4, 0.4),
				ring("chime_ring", "#7FE6FF", 2.2, 0.4),
				-- 3 больших вертикально поднимающихся кольца (по очереди 0 / 0.17 / 0.33), r 0.6 -> ~1.4
				{ mesh = "chime_ring", color = "#7FE6FF", neon = true, t0 = 0, t1 = 0.73, size0 = { 0.5, 0.1, 0.5 },
					size1 = { 2.8, 0.1, 2.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 3.4, easing = "Quad" },
				{ mesh = "chime_ring", color = "#7FE6FF", neon = true, t0 = 0.17, t1 = 0.9, size0 = { 0.5, 0.1, 0.5 },
					size1 = { 2.8, 0.1, 2.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 3.4, easing = "Quad" },
				{ mesh = "chime_ring", color = "#7FE6FF", neon = true, t0 = 0.33, t1 = 1.06, size0 = { 0.4, 0.1, 0.4 },
					size1 = { 1.8, 0.1, 1.8 }, a0 = 0, a1 = 1, y0 = 0.4, y1 = 3.6, easing = "Quad" },
				{ mesh = "chime_ring", color = "#7FE6FF", neon = true, t0 = 0, t1 = 0.73, size0 = { 0.3, 0.1, 0.3 },
					size1 = { 1.8, 0.1, 1.8 }, a0 = 0, a1 = 1, y0 = 0.4, y1 = 3.7, easing = "Quad" },
				{ mesh = "hex_ring", color = "#7FE6FF", neon = true, t0 = 0.07, t1 = 0.4, size0 = { 0.3, 0.1, 0.3 },
					size1 = { 3.0, 0.1, 3.0 }, a0 = 0, a1 = 0.1, hold = 0.6, easing = "Quad" },
				{ mesh = "hex_crystal", color = "#6FC8FF", neon = true, count = 6, r = 1.5, t0 = 0.07, t1 = 0.4,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.4, 1.15, 0.4 }, a0 = 0, a1 = 0, hold = 0.6, easing = "Back" },
				{ mesh = "hex_crystal", color = "#9A8AFF", neon = true, count = 6, r = 1.2, t0 = 0.17, t1 = 0.5,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.18, 0.5, 0.18 }, a0 = 0, a1 = 0, hold = 0.5, easing = "Back" },
				{ mesh = "sparkle", color = "#F0FCFF", neon = true, count = 8, r = 1.2, t0 = 0, t1 = 1.3,
					size0 = { 0.4, 0.4, 0.4 }, size1 = { 0.1, 0.1, 0.1 }, a0 = 0, a1 = 1, y0 = 0.5, y1 = 3.0, easing = "Sine" },
			},
		},
	},

	-- 08 ----------------------------------------------------------------
	fire = {
		idle = {
			emitters = {
				{ at = "tip", texture = "fire", c0 = "#FF5A14", c1 = "#FFC23A", s0 = 0.2, s1 = 0.05, t0 = 0, t1 = 1,
					rate = 6, life = { 1, 1 }, speed = { 0.5, 1 }, spread = 30, dir = "up", accel = { 0, 1.5, 0 }, light = 1 },
				{ at = "tip", texture = "spark", c0 = "#FFD25A", c1 = "#FFD25A", s0 = 0.08, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 3, life = { 1.2, 1.2 }, speed = { 0.3, 0.3 }, spread = 180, dir = "out", light = 1 },
			},
			light = { color = "#FF7A2A", range = 6, brightness = 1 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "fire", c0 = "#FF5A14", c1 = "#E0302A", s0 = 0.6, smid = 0.9, s1 = 0.2, t0 = 0,
					t1 = 1, rate = 12, life = { 1, 1 }, speed = { 10, 11 }, spread = 10, dir = "back", light = 1 },
				{ at = "trail", texture = "spark", c0 = "#FFC23A", c1 = "#FFC23A", s0 = 0.12, s1 = 0.12, t0 = 0, t1 = 1,
					rate = 10, life = { 0.9, 0.9 }, speed = { 4, 4 }, spread = 45, dir = "back", light = 1 },
				{ at = "trail", texture = "smoke", c0 = "#4A3A3A", c1 = "#4A3A3A", s0 = 0.4, s1 = 1.6, t0 = 0.2, t1 = 1,
					rate = 4, life = { 1, 1 }, speed = { 1, 2 }, spread = 25, dir = "back" },
			},
			rings = { { mesh = "fire_ring", color = "#FF5A14", every = 0.33, s0 = 0.5, s1 = 2.0, travel = 6, life = 1, a0 = 0.2 } },
			light = { color = "#FF7A2A", range = 9, brightness = 2 },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FF7A2A", range = 10, brightness = 4, t1 = 0.8 },
			bursts = {
				{ at = "ground", texture = "spark", c0 = "#FFD25A", c1 = "#FF6A1A", s0 = 0.12, s1 = 0.05, t0 = 0, t1 = 1,
					count = 12, life = { 0.9, 0.9 }, speed = { 5, 9 }, spread = 30, dir = "up", accel = { 0, -27, 0 }, light = 1 },
				{ at = "ground", texture = "smoke", c0 = "#4A3A3A", c1 = "#4A3A3A", s0 = 0.5, s1 = 2.2, t0 = 0.2, t1 = 1,
					count = 8, delay = 0.17, life = { 1.2, 1.2 }, speed = { 2, 3 }, spread = 40, dir = "up" },
			},
			meshes = {
				-- огненная сфера r 0.6 -> ~2.2, и внутреннее ядро
				{ mesh = "ball", color = "#FF7A22", neon = true, t0 = 0, t1 = 0.47, size0 = { 1.2, 1.2, 1.2 },
					size1 = { 4.3, 4.3, 4.3 }, a0 = 0, a1 = 1, y0 = 0.6, y1 = 0.6, easing = "Quad" },
				{ mesh = "ball", color = "#FFD25A", neon = true, t0 = 0, t1 = 0.27, size0 = { 1.0, 1.0, 1.0 },
					size1 = { 2.4, 2.4, 2.4 }, a0 = 0, a1 = 1, y0 = 0.5, y1 = 0.5, easing = "Quad" },
				{ mesh = "scorch", color = "#2C201C", t0 = 0.07, t1 = 0.27, size0 = { 0.4, 0.05, 0.4 },
					size1 = { 3.8, 0.05, 3.8 }, a0 = 0, a1 = 0, hold = 0.95, easing = "Quad" },
				{ mesh = "fire_ring", color = "#FF6A1A", neon = true, t0 = 0.07, t1 = 0.3, size0 = { 0.5, 0.15, 0.5 },
					size1 = { 3.2, 0.15, 3.2 }, a0 = 0, a1 = 1, hold = 0.3, easing = "Quad" },
				-- огоньки кольцом r 1.6 и внутреннее r 0.95
				{ mesh = "flame", color = "#FF5A14", neon = true, count = 14, r = 1.6, t0 = 0.17, t1 = 0.6,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.4, 0.85, 0.4 }, a0 = 0, a1 = 0.2, hold = 0.9, easing = "Sine" },
				{ mesh = "flame", color = "#FFC23A", neon = true, count = 6, r = 0.95, t0 = 0.2, t1 = 0.6,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.35, 0.6, 0.35 }, a0 = 0, a1 = 0.2, hold = 0.9, easing = "Sine" },
				{ mesh = "ember", color = "#FFD25A", neon = true, count = 6, r = 1.4, t0 = 0, t1 = 1.0,
					size0 = { 0.12, 0.12, 0.12 }, size1 = { 0.12, 0.12, 0.12 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 0.3, easing = "Quad" },
			},
		},
	},

	-- 09 ----------------------------------------------------------------
	ice = {
		idle = {
			emitters = {
				{ at = "tip", texture = "snow", c0 = "#F4FBFF", c1 = "#F4FBFF", s0 = 0.09, s1 = 0.06, t0 = 0.2, t1 = 1,
					rate = 4, life = { 1.5, 1.5 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, -0.3, 0 } },
				glint("#F4FCFF", 2),
			},
			light = { color = "#9AE8FF", range = 5, brightness = 0.5 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "shard", c0 = "#BFE9FF", c1 = "#6AB4F0", s0 = 0.4, smid = 0.5, s1 = 0, t0 = 0,
					t1 = 1, rate = 10, life = { 1, 1 }, speed = { 11, 12 }, spread = 12, dir = "back", rot = 540 },
				{ at = "trail", texture = "smoke", c0 = "#F4FBFF", c1 = "#F4FBFF", s0 = 0.3, smid = 1.4, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 2, 4 }, spread = 30, dir = "back" },
				{ at = "trail", texture = "snow", c0 = "#F4FCFF", c1 = "#F4FCFF", s0 = 0.4, s1 = 0.3, t0 = 0, t1 = 1,
					rate = 5, life = { 1, 1 }, speed = { 3, 5 }, spread = 25, dir = "back", rot = 360, light = 0.6 },
			},
			rings = { airRing("frost_ring", "#9AE8FF", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#9AE8FF", range = 9, brightness = 3, t1 = 0.6 },
			bursts = {
				arc("shard", 10, "#BFE9FF", "#6AB4F0", 0.3, { 6, 10 }),
				{ at = "ground", texture = "smoke", c0 = "#F4FBFF", c1 = "#F4FBFF", s0 = 0.4, s1 = 1.8, t0 = 0.2, t1 = 1,
					count = 8, life = { 1.2, 1.2 }, speed = { 1, 2 }, spread = 60, dir = "up" },
			},
			meshes = {
				flash("#D0F6FF", 1.4, 0.4),
				ring("frost_ring", "#9AE8FF", 2.5, 0.4),
				{ mesh = "frost_disc", color = "#EEF8FF", t0 = 0, t1 = 0.4, size0 = { 0.5, 0.05, 0.5 },
					size1 = { 5.4, 0.05, 5.4 }, a0 = 0, a1 = 0, hold = 0.73, easing = "Quad" },
				{ mesh = "frost_disc", color = "#BFEEFF", neon = true, t0 = 0, t1 = 0.4, size0 = { 0.5, 0.05, 0.5 },
					size1 = { 5.0, 0.05, 5.0 }, a0 = 0.1, a1 = 0.7, hold = 0.3, easing = "Quad" },
				-- 6 + 10 + 12 шипов тремя кольцами (r 0.9 / 1.65 / 2.35)
				{ mesh = "ice_spike", color = "#BFE9FF", neon = false, count = 6, r = 0.9, t0 = 0.03, t1 = 0.3,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.45, 1.35, 0.45 }, a0 = 0, a1 = 0, hold = 0.8, easing = "Back" },
				{ mesh = "ice_spike", color = "#6AB4F0", count = 10, r = 1.65, t0 = 0.1, t1 = 0.37,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.35, 1.0, 0.35 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
				{ mesh = "ice_spike", color = "#BFE9FF", count = 12, r = 2.35, t0 = 0.17, t1 = 0.43,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.3, 0.7, 0.3 }, a0 = 0, a1 = 0, hold = 0.6, easing = "Back" },
				{ mesh = "ice_shard", color = "#BFE9FF", count = 5, r = 1.8, t0 = 0, t1 = 0.3,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.3, 0.3, 0.3 }, a0 = 0, a1 = 0, hold = 0.8, easing = "Back" },
			},
		},
	},

	-- 10 ----------------------------------------------------------------
	star = {
		idle = {
			emitters = {
				{ at = "tip", texture = "star", c0 = "#FFE27A", c1 = "#FFF6C8", s0 = 0.3, s1 = 0.15, t0 = 0, t1 = 1,
					rate = 3, life = { 1.5, 1.5 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", rot = 60, light = 1 },
				{ at = "tip", texture = "spark", c0 = "#4AD8E8", c1 = "#4AD8E8", s0 = 0.08, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 3, life = { 1.2, 1.2 }, speed = { 0.3, 0.3 }, spread = 180, dir = "out", accel = { 0, 0.5, 0 }, light = 1 },
			},
			light = { color = "#FFD24A", range = 5, brightness = 0.7 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "star", c0 = "#FFE27A", c1 = "#FFF6C8", s0 = 0.4, smid = 0.5, s1 = 0, t0 = 0,
					t1 = 1, rate = 10, life = { 1, 1 }, speed = { 11, 12 }, spread = 12, dir = "back", rot = 540, light = 1 },
				{ at = "trail", texture = "spark", c0 = "#4AD8E8", c1 = "#4AD8E8", s0 = 0.1, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 8, life = { 0.9, 0.9 }, speed = { 4, 4 }, spread = 40, dir = "back", light = 1 },
				{ at = "trail", texture = "smoke", c0 = "#7A5AD8", c1 = "#7A5AD8", s0 = 0.3, s1 = 1.4, t0 = 0.3, t1 = 1,
					rate = 5, life = { 1, 1 }, speed = { 1, 2 }, spread = 25, dir = "back" },
			},
			rings = { airRing("flash_ring", "#FFD24A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFD24A", range = 10, brightness = 3, t1 = 0.6 },
			bursts = {
				{ at = "ground", texture = "star", c0 = "#FFE27A", c1 = "#4AD8E8", s0 = 0.12, s1 = 0.05, t0 = 0, t1 = 1,
					count = 18, life = { 0.8, 0.8 }, speed = { 2, 4 }, spread = 40, dir = "up", accel = { 0, 3, 0 }, light = 1 },
				arc("rock", 6, "#4E4A58", "#7A7688", 0.3, { 6, 10 }),
				{ at = "ground", texture = "smoke", c0 = "#7A5AD8", c1 = "#7A5AD8", s0 = 0.5, s1 = 2.0, t0 = 0.3, t1 = 1,
					count = 4, delay = 0.1, life = { 1.2, 1.2 }, speed = { 1, 2 }, spread = 60, dir = "up" },
			},
			meshes = {
				flash("#FFE9A8", 1.6, 0.35, 0.37),
				ring("flash_ring", "#FFD24A", 2.5, 0.43),
				{ mesh = "ground_star", color = "#FFD24A", neon = true, t0 = 0.07, t1 = 0.33, size0 = { 0.4, 0.04, 0.4 },
					size1 = { 4.0, 0.04, 4.0 }, a0 = 0, a1 = 0.3, hold = 0.6, spin = 40, easing = "Quad" },
				{ mesh = "ground_star", color = "#FFF6C8", neon = true, t0 = 0.07, t1 = 0.33, size0 = { 0.2, 0.04, 0.2 },
					size1 = { 2.0, 0.04, 2.0 }, a0 = 0, a1 = 0.3, hold = 0.6, spin = -40, easing = "Quad" },
				{ mesh = "flying_star", color = "#FFE27A", neon = true, count = 5, r = 1.2, t0 = 0, t1 = 0.8,
					size0 = { 0.8, 0.1, 0.8 }, size1 = { 0.8, 0.1, 0.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 2.5, spin = 720, easing = "Sine" },
				{ mesh = "flying_star", color = "#4AD8E8", neon = true, count = 10, r = 2.7, t0 = 0.1, t1 = 0.8,
					size0 = { 0.3, 0.05, 0.3 }, size1 = { 0.3, 0.05, 0.3 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 1.2, spin = 720, easing = "Sine" },
			},
		},
	},

	-- 11 ----------------------------------------------------------------
	amber_sting = {
		idle = {
			emitters = {
				{ at = "tip", texture = "bubble", c0 = "#FFE6A0", c1 = "#FFE6A0", s0 = 0.15, s1 = 0.1, t0 = 0.2, t1 = 1,
					rate = 3, life = { 1.5, 1.5 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.6, 0 } },
				glint("#FFE27A", 2),
				{ at = "tip", texture = "spark", c0 = "#FFC83A", c1 = "#FFC83A", s0 = 0.08, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 2, life = { 1.2, 1.2 }, speed = { 0.3, 0.3 }, spread = 180, dir = "out", light = 1 },
			},
			light = { color = "#FFC83A", range = 5, brightness = 0.6 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "drop", c0 = "#F5A623", c1 = "#FFD45A", s0 = 0.5, smid = 0.7, s1 = 0, t0 = 0,
					t1 = 1, rate = 10, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back" },
				{ at = "trail", texture = "spark", c0 = "#FFE27A", c1 = "#FFC83A", s0 = 0.12, s1 = 0.12, t0 = 0, t1 = 1,
					rate = 10, life = { 0.9, 0.9 }, speed = { 4, 4 }, spread = 45, dir = "back", light = 1 },
				{ at = "trail", texture = "feather", c0 = "#E8F2FF", c1 = "#E8F2FF", s0 = 0.35, s1 = 0.3, t0 = 0.2, t1 = 1,
					rate = 4, life = { 1, 1 }, speed = { 4, 6 }, spread = 25, dir = "back", rot = 300 },
			},
			rings = { airRing("hex_ring", "#FFC83A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFC83A", range = 9, brightness = 3, t1 = 0.6 },
			bursts = {
				arc("drop", 14, "#F5A623", "#FFD45A", 0.3, { 6, 10 }),
				arc("spark", 14, "#FFE27A", "#FFC83A", 0.12, { 4, 8 }, 0.87, -27, 40, 1),
			},
			meshes = {
				flash("#FFD86A", 1.4, 0.4),
				ring("hex_ring", "#FFC83A", 2.3, 0.43),
				{ mesh = "honey_puddle", color = "#F5A623", t0 = 0.03, t1 = 0.47, size0 = { 0.4, 0.05, 0.4 },
					size1 = { 4.0, 0.05, 4.0 }, a0 = 0, a1 = 0, hold = 0.66, easing = "Quad" },
				{ mesh = "honey_puddle", color = "#F5A623", count = 5, r = 1.95, t0 = 0.2, t1 = 0.4,
					size0 = { 0.96, 0.04, 0.96 }, size1 = { 0.8, 0.04, 0.8 }, a0 = 0, a1 = 0, hold = 0.73, easing = "Quad" },
				-- соты впереди копья: центр в 1.7 по +X; центральная и 6 вокруг (шаг 0.77)
				{ mesh = "honey_comb", color = "#FFD45A", count = 6, r = 0.77, t0 = 0.13, t1 = 0.4,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.8, 0.95, 0.8 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
				{ mesh = "honey_comb", color = "#F5A623", count = 1, r = 0, t0 = 0.1, t1 = 0.4,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.8, 1.5, 0.8 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
			},
		},
	},

	-- 12 ----------------------------------------------------------------
	solar_trident = {
		idle = {
			emitters = {
				glint("#FFF0A8", 2),
				{ at = "tip", texture = "fire", c0 = "#FF6A1A", c1 = "#FFC23A", s0 = 0.2, s1 = 0.05, t0 = 0, t1 = 1,
					rate = 5, life = { 1, 1 }, speed = { 0.5, 1 }, spread = 40, dir = "up", accel = { 0, 1.5, 0 }, light = 1 },
			},
			light = { color = "#FFC23A", range = 6, brightness = 1 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "fire", c0 = "#FF6A1A", c1 = "#FFC23A", s0 = 0.6, smid = 0.9, s1 = 0.2, t0 = 0,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 10, 11 }, spread = 12, dir = "back", light = 1 },
				{ at = "trail", texture = "spark", c0 = "#FFD24A", c1 = "#FFF0A8", s0 = 0.12, s1 = 0.12, t0 = 0, t1 = 1,
					rate = 8, life = { 0.9, 0.9 }, speed = { 4, 4 }, spread = 45, dir = "back", light = 1 },
				{ at = "trail", texture = "spark", c0 = "#FFD24A", c1 = "#FFD24A", s0 = 0.4, smid = 0.5, s1 = 0, t0 = 0,
					t1 = 1, rate = 6, life = { 1, 1 }, speed = { 11, 12 }, spread = 8, dir = "back", light = 1 },
			},
			rings = { { mesh = "sun_ring", color = "#FFB52A", every = 0.33, s0 = 0.5, s1 = 2.0, travel = 6, life = 1, a0 = 0.2 } },
			light = { color = "#FFC23A", range = 9, brightness = 2 },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFC23A", range = 11, brightness = 4, t1 = 0.8 },
			bursts = {
				arc("spark", 10, "#FFD24A", "#FFF0A8", 0.12, { 5, 9 }, 0.87, -27, 40, 1),
			},
			meshes = {
				flash("#FFD868", 1.6, 0.5, 0.37),
				ring("sun_ring", "#FFB52A", 2.5, 0.43),
				-- 18 лучей горизонтально: длинные 3.6 и короткие 2.4
				{ mesh = "sun_ray", color = "#FFD24A", neon = true, count = 9, r = 0.3, t0 = 0.03, t1 = 0.13,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.14, 0.14, 3.6 }, a0 = 0, a1 = 0.6, y0 = 0.3, y1 = 0.3,
					hold = 0.6, easing = "Back" },
				{ mesh = "sun_ray", color = "#FFF0A8", neon = true, count = 9, r = 0.3, t0 = 0.03, t1 = 0.13,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.12, 0.12, 2.4 }, a0 = 0, a1 = 0.6, y0 = 0.3, y1 = 0.3,
					hold = 0.6, easing = "Back" },
				-- солнечный диск поднимается за копьём 0.3 -> 3.4 + гало
				{ mesh = "sun_disc", color = "#FFD24A", neon = true, t0 = 0, t1 = 1.2, size0 = { 2.0, 0.1, 2.0 },
					size1 = { 3.0, 0.1, 3.0 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 3.4, easing = "Quad" },
				{ mesh = "ball", color = "#FFD868", neon = true, t0 = 0, t1 = 1.2, size0 = { 3.0, 3.0, 3.0 },
					size1 = { 4.5, 4.5, 4.5 }, a0 = 0.5, a1 = 1, y0 = 0.3, y1 = 3.4, easing = "Quad" },
				{ mesh = "sun_ray", color = "#FFF0A8", neon = true, count = 8, r = 0.8, t0 = 0.03, t1 = 1.0,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.1, 0.1, 0.6 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 3.4, easing = "Quad" },
				{ mesh = "fire_ring_flame", color = "#FF6A1A", neon = true, count = 12, r = 1.55, t0 = 0.17, t1 = 0.6,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.4, 0.95, 0.4 }, a0 = 0, a1 = 0.3, hold = 0.9, easing = "Sine" },
			},
		},
	},

	-- 13 ----------------------------------------------------------------
	canyon_hook = {
		idle = {
			emitters = {
				{ at = "tip", texture = "dust", c0 = "#E8956A", c1 = "#B04A34", s0 = 0.07, s1 = 0.05, t0 = 0.3, t1 = 1,
					rate = 5, life = { 1.4, 1.4 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.25, 0 } },
				glint("#FFE2A8", 1.5),
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "dust", c0 = "#E8956A", c1 = "#B04A34", s0 = 0.4, smid = 1.5, s1 = 0, t0 = 0.15,
					t1 = 1, rate = 10, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
				{ at = "trail", texture = "rock", c0 = "#C4492F", c1 = "#E6B87A", s0 = 0.2, s1 = 0.2, t0 = 0, t1 = 1,
					rate = 10, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 30, dir = "back", rot = 360 },
				{ at = "trail", texture = "shard", c0 = "#C4492F", c1 = "#7A2E24", s0 = 0.3, s1 = 0.2, t0 = 0, t1 = 1,
					rate = 6, life = { 1, 1 }, speed = { 11, 12 }, spread = 8, dir = "back", rot = 540 },
			},
			rings = { airRing("dust_ring", "#FFC88A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFB877", range = 7, brightness = 2, t1 = 0.4 },
			bursts = {
				puffs(12, "#E8956A", "#B04A34", 2.5),
				arc("rock", 14, "#C4492F", "#E6B87A", 0.22, { 6, 10 }),
				arc("rock", 4, "#C4492F", "#E08A3C", 0.45, { 6, 10 }),
			},
			meshes = {
				flash("#FFD8A0", 1.5, 0.3),
				ring("shock_ring", "#FFB877", 2.6, 0.4),
				{ mesh = "cyl", color = "#7A2E24", t0 = 0, t1 = 0.13, size0 = { 1.0, 0.1, 1.0 }, size1 = { 2.0, 0.25, 2.0 },
					a0 = 0, a1 = 0, hold = 1.0, easing = "Back" },
				-- 6 ступенчатых столбов-мез кольцом r 1.6 / 1.95 (за копьём пусто)
				{ mesh = "mesa", color = "#C4492F", count = 6, r = 1.75, t0 = 0, t1 = 0.33, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.8, 1.4, 0.8 }, a0 = 0, a1 = 0, hold = 0.8, easing = "Back" },
				{ mesh = "mesa_cap", color = "#E6B87A", count = 6, r = 1.75, t0 = 0, t1 = 0.33, size0 = { 0.05, 0.02, 0.05 },
					size1 = { 1.0, 0.18, 1.0 }, a0 = 0, a1 = 0, y0 = 0, y1 = 1.4, hold = 0.8, easing = "Back" },
				{ mesh = "mesa", color = "#E6B87A", count = 5, r = 2.6, t0 = 0.1, t1 = 0.4, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.52, 0.6, 0.52 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
				cracks("#7A2E24", 6, 1.5),
			},
		},
	},

	-- 14 ----------------------------------------------------------------
	condor_quill = {
		idle = {
			emitters = {
				{ at = "tip", texture = "feather", c0 = "#FFFFFF", c1 = "#2C2A36", s0 = 0.25, s1 = 0.15, t0 = 0.1, t1 = 1,
					rate = 3, life = { 2, 2 }, speed = { 0.1, 0.1 }, spread = 180, dir = "out", accel = { 0, -0.15, 0 }, rot = 60 },
				glint("#FFF2C8", 1.5),
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "feather", c0 = "#2C2A36", c1 = "#FFFFFF", s0 = 0.55, smid = 0.6, s1 = 0, t0 = 0,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 360 },
				{ at = "trail", texture = "feather", c0 = "#C9602F", c1 = "#FFFFFF", s0 = 0.55, smid = 0.6, s1 = 0, t0 = 0,
					t1 = 1, rate = 6, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 200 },
				{ at = "trail", texture = "smoke", c0 = "#FFF4E4", c1 = "#D6A77A", s0 = 0.35, smid = 1.5, s1 = 0, t0 = 0.15,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
			},
			rings = { airRing("wind_ring", "#BFEAFF", 2.1) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#BFEAFF", range = 7, brightness = 1.5, t1 = 0.5 },
			bursts = {
				puffs(10, "#FFF4E4", "#D6A77A", 2.0),
				{ at = "ground", texture = "sparkle", c0 = "#FFF2C8", c1 = "#FFF2C8", s0 = 0.14, s1 = 0.1, t0 = 0, t1 = 1,
					count = 10, life = { 1.2, 1.2 }, speed = { 1, 3 }, spread = 30, dir = "up", accel = { 0, 2, 0 }, light = 1 },
				{ at = "ground", texture = "feather", c0 = "#2C2A36", c1 = "#FFFFFF", s0 = 0.6, s1 = 0, t0 = 0, t1 = 1,
					count = 18, life = { 1.2, 1.2 }, speed = { 3, 3 }, spread = 20, dir = "up", accel = { 0, 1, 0 }, rot = 300 },
			},
			meshes = {
				flash("#FFF0D0", 1.5, 0.3),
				ring("shock_ring", "#BFEAFF", 2.5, 0.4),
				-- столб воздуха r 0.8 x 3.2
				{ mesh = "cyl", color = "#DFF4FF", neon = true, t0 = 0.07, t1 = 1.33, size0 = { 1.6, 0.3, 1.6 },
					size1 = { 1.6, 3.2, 1.6 }, a0 = 0.88, a1 = 1, easing = "Quad" },
				-- 5 колец ветра стопкой (0 / 0.1 / 0.2 / 0.3 / 0.4)
				{ mesh = "wind_ring", color = "#BFEAFF", neon = true, t0 = 0, t1 = 0.87, size0 = { 0.9, 0.1, 0.9 },
					size1 = { 2.8, 0.1, 2.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 2.0, easing = "Quad" },
				{ mesh = "wind_ring", color = "#BFEAFF", neon = true, t0 = 0.1, t1 = 0.97, size0 = { 0.9, 0.1, 0.9 },
					size1 = { 2.8, 0.1, 2.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 2.3, easing = "Quad" },
				{ mesh = "wind_ring", color = "#BFEAFF", neon = true, t0 = 0.2, t1 = 1.07, size0 = { 0.9, 0.1, 0.9 },
					size1 = { 2.8, 0.1, 2.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 2.6, easing = "Quad" },
				{ mesh = "wind_ring", color = "#BFEAFF", neon = true, t0 = 0.3, t1 = 1.17, size0 = { 0.9, 0.1, 0.9 },
					size1 = { 2.8, 0.1, 2.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 2.8, easing = "Quad" },
				{ mesh = "wind_ring", color = "#BFEAFF", neon = true, t0 = 0.4, t1 = 1.27, size0 = { 0.9, 0.1, 0.9 },
					size1 = { 2.8, 0.1, 2.8 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 3.0, easing = "Quad" },
				{ mesh = "puff", color = "#FFF4E4", count = 4, r = 1.5, t0 = 0, t1 = 1.0, size0 = { 0.3, 0.3, 0.3 },
					size1 = { 1.2, 1.2, 1.2 }, a0 = 0.3, a1 = 1, y0 = 0.3, y1 = 1.0, easing = "Quad" },
			},
		},
	},

	-- 15 ----------------------------------------------------------------
	mirage_lance = {
		idle = {
			emitters = {
				{ at = "tip", texture = "star", c0 = "#FFFBE0", c1 = "#FFFBE0", s0 = 0.18, s1 = 0.12, t0 = 0, t1 = 1,
					rate = 3, life = { 0.5, 0.5 }, speed = { 0, 0.2 }, spread = 180, dir = "out", light = 1 },
				{ at = "tip", texture = "dust", c0 = "#F6E2B4", c1 = "#D8AB6A", s0 = 0.07, s1 = 0.05, t0 = 0.3, t1 = 1,
					rate = 4, life = { 1.5, 1.5 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.2, 0 } },
			},
			light = { color = "#A8F0FF", range = 4, brightness = 0.6 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "crystal", c0 = "#A8ECFF", c1 = "#5E7FD0", s0 = 0.34, smid = 0.4, s1 = 0, t0 = 0,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 540, light = 1 },
				{ at = "trail", texture = "dust", c0 = "#F6E2B4", c1 = "#D8AB6A", s0 = 0.35, smid = 1.5, s1 = 0, t0 = 0.15,
					t1 = 1, rate = 10, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
				{ at = "trail", texture = "sparkle", c0 = "#FFFBE0", c1 = "#FFFBE0", s0 = 0.14, s1 = 0.14, t0 = 0, t1 = 1,
					rate = 6, life = { 0.5, 0.5 }, speed = { 1, 3 }, spread = 30, dir = "back", light = 1 },
			},
			rings = { airRing("heat_ring", "#FFD9A0", 2.1, 0.5) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#B8F2FF", range = 8, brightness = 2.5, t1 = 0.6 },
			bursts = {
				{ at = "ground", texture = "sparkle", c0 = "#FFFBE0", c1 = "#FFFBE0", s0 = 0.28, s1 = 0.14, t0 = 0, t1 = 1,
					count = 22, life = { 1, 1 }, speed = { 5, 8 }, spread = 40, dir = "up", accel = { 0, -22, 0 }, light = 1 },
				puffs(10, "#F6E2B4", "#D8AB6A", 2.2),
			},
			meshes = {
				flash("#FFFBE8", 1.5, 0.3),
				ring("heat_ring", "#A8F0FF", 2.5, 0.4),
				{ mesh = "cyl", color = "#F2DFB4", t0 = 0, t1 = 0.13, size0 = { 1.0, 0.1, 1.0 }, size1 = { 1.6, 0.16, 1.6 },
					a0 = 0, a1 = 0, hold = 1.0, easing = "Back" },
				-- 3 прозрачные копии кристалла (h 2.0), r 1.4 / 1.7 / 1.4, мигают и гаснут к 1.33
				{ mesh = "mirror", color = "#B8F2FF", neon = true, count = 3, r = 1.5, t0 = 0, t1 = 1.33,
					size0 = { 0.5, 0.5, 0.5 }, size1 = { 0.8, 2.0, 0.8 }, a0 = 0.1, a1 = 1, easing = "Linear" },
				{ mesh = "shard", color = "#A8ECFF", neon = true, count = 5, r = 1.2, t0 = 0.07, t1 = 0.33,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.3, 0.5, 0.3 }, a0 = 0, a1 = 0, hold = 0.9, easing = "Back" },
				-- 4 кольца марева расходятся до r 2.9 / 2.7 / 2.4 / 2.1
				{ mesh = "heat_ring", color = "#FFD9A0", neon = true, t0 = 0, t1 = 0.67, size0 = { 0.5, 0.1, 0.5 },
					size1 = { 5.8, 0.1, 5.8 }, a0 = 0.5, a1 = 1, easing = "Quad" },
				{ mesh = "heat_ring", color = "#FFD9A0", neon = true, t0 = 0.13, t1 = 0.8, size0 = { 0.5, 0.1, 0.5 },
					size1 = { 5.4, 0.1, 5.4 }, a0 = 0.5, a1 = 1, easing = "Quad" },
				{ mesh = "heat_ring", color = "#FFD9A0", neon = true, t0 = 0.27, t1 = 0.94, size0 = { 0.5, 0.1, 0.5 },
					size1 = { 4.8, 0.1, 4.8 }, a0 = 0.5, a1 = 1, easing = "Quad" },
				{ mesh = "heat_ring", color = "#FFD9A0", neon = true, t0 = 0.4, t1 = 1.07, size0 = { 0.5, 0.1, 0.5 },
					size1 = { 4.2, 0.1, 4.2 }, a0 = 0.5, a1 = 1, easing = "Quad" },
				{ mesh = "glitter", color = "#FFFBE0", neon = true, count = 6, r = 1.4, t0 = 0, t1 = 0.9,
					size0 = { 0.28, 0.28, 0.28 }, size1 = { 0.14, 0.14, 0.14 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 1.5, spin = 180, easing = "Sine" },
			},
		},
	},

	-- 16 ----------------------------------------------------------------
	scorpion_sting = {
		idle = {
			emitters = {
				{ at = "tip", texture = "drop", c0 = "#9BE848", c1 = "#9BE848", s0 = 0.16, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 4, life = { 1.2, 1.2 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, -0.4, 0 }, light = 1 },
				glint("#D8FF9A", 1.5),
			},
			light = { color = "#9BE848", range = 4, brightness = 0.5 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "dust", c0 = "#F2DBA8", c1 = "#C9A068", s0 = 0.35, smid = 1.5, s1 = 0, t0 = 0.15,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
				{ at = "trail", texture = "shard", c0 = "#3B2A24", c1 = "#B07A48", s0 = 0.36, s1 = 0.25, t0 = 0, t1 = 1,
					rate = 8, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 540 },
				{ at = "trail", texture = "drop", c0 = "#9BE848", c1 = "#9BE848", s0 = 0.16, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 10, life = { 0.9, 0.9 }, speed = { 3, 3 }, spread = 25, dir = "back", light = 1 },
			},
			rings = { airRing("shock_ring", "#C2F07A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#9BE848", range = 7, brightness = 2, t1 = 0.5 },
			bursts = {
				puffs(10, "#F2DBA8", "#C9A068", 2.2),
				arc("drop", 14, "#9BE848", "#9BE848", 0.16, { 6, 11 }, 1.1, -25, 25, 1),
				arc("rock", 6, "#3B2A24", "#B07A48", 0.22, { 6, 9 }),
			},
			meshes = {
				flash("#F2FFB8", 1.4, 0.3),
				ring("shock_ring", "#E8FFB0", 2.5, 0.4),
				-- 5 трещин веером + светящаяся жила
				{ mesh = "crack", color = "#3B2A24", count = 5, r = 0.4, t0 = 0, t1 = 0.17, size0 = { 0.1, 0.05, 0.1 },
					size1 = { 0.3, 0.05, 1.8 }, a0 = 0, a1 = 0, hold = 1.1, easing = "Quad" },
				{ mesh = "crack", color = "#9BE848", neon = true, count = 5, r = 0.4, t0 = 0.13, t1 = 0.33,
					size0 = { 0.05, 0.05, 0.1 }, size1 = { 0.1, 0.05, 1.8 }, a0 = 0, a1 = 0.3, hold = 1.0, easing = "Quad" },
				{ mesh = "cyl", color = "#B07A48", t0 = 0, t1 = 0.13, size0 = { 0.8, 0.1, 0.8 }, size1 = { 1.5, 0.15, 1.5 },
					a0 = 0, a1 = 0, hold = 1.0, easing = "Back" },
				-- 2 когтя по бокам, затем смыкаются над точкой удара
				{ mesh = "claw", color = "#3B2A24", count = 2, r = 0.95, t0 = 0.03, t1 = 0.47, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.5, 2.0, 0.5 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
				{ mesh = "ball", color = "#9BE848", neon = true, count = 2, r = 0.1, t0 = 0.37, t1 = 0.57,
					size0 = { 0.18, 0.18, 0.18 }, size1 = { 0.18, 0.18, 0.18 }, a0 = 0, a1 = 0, y0 = 1.8, y1 = 1.8, hold = 0.6,
					easing = "Linear" },
			},
		},
	},

	-- 17 ----------------------------------------------------------------
	emerald_vine = {
		idle = {
			emitters = {
				{ at = "tip", texture = "spore", c0 = "#B8FF9A", c1 = "#B8FF9A", s0 = 0.18, s1 = 0.1, t0 = 0.2, t1 = 1,
					rate = 5, life = { 1.6, 1.6 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.3, 0 }, light = 1 },
				glint("#F4FFD0", 1.5),
			},
			light = { color = "#7FFFB0", range = 4, brightness = 0.5 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "leaf", c0 = "#7BD05A", c1 = "#4C9A3A", s0 = 0.4, s1 = 0.3, t0 = 0, t1 = 1,
					rate = 12, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 360 },
				{ at = "trail", texture = "crystal", c0 = "#2FD68A", c1 = "#1A9A6A", s0 = 0.34, s1 = 0.2, t0 = 0, t1 = 1,
					rate = 8, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 540, light = 1 },
				{ at = "trail", texture = "smoke", c0 = "#D2F8BC", c1 = "#7EC06A", s0 = 0.35, smid = 1.5, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 6, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
			},
			rings = { airRing("shock_ring", "#A8F08A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#7FFFB0", range = 7, brightness = 2, t1 = 0.5 },
			bursts = {
				arc("leaf", 10, "#7BD05A", "#4C9A3A", 0.25, { 5, 9 }, 1.1, -17, 25),
				{ at = "ground", texture = "spore", c0 = "#B8FF9A", c1 = "#B8FF9A", s0 = 0.14, s1 = 0.1, t0 = 0, t1 = 1,
					count = 10, life = { 1.2, 1.2 }, speed = { 1, 3 }, spread = 30, dir = "up", accel = { 0, 1.5, 0 }, light = 1 },
				puffs(10, "#D2F8BC", "#7EC06A", 2.2),
			},
			meshes = {
				flash("#E4FFC8", 1.4, 0.3),
				ring("shock_ring", "#C8FF9A", 2.5, 0.4),
				{ mesh = "vine", color = "#4C9A3A", count = 6, r = 1.5, t0 = 0, t1 = 0.4, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.5, 1.35, 0.5 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
				{ mesh = "leaf", color = "#7BD05A", count = 12, r = 1.5, t0 = 0.2, t1 = 0.57, size0 = { 0.05, 0.02, 0.05 },
					size1 = { 0.5, 0.22, 0.5 }, a0 = 0, a1 = 0, y0 = 0.5, y1 = 0.9, hold = 0.6, easing = "Back" },
				{ mesh = "bud", color = "#2FD68A", neon = true, count = 6, r = 1.5, t0 = 0.27, t1 = 0.63,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.4, 0.4, 0.4 }, a0 = 0, a1 = 0, y0 = 1.3, y1 = 1.3, hold = 0.6, easing = "Back" },
			},
		},
	},

	-- 18 ----------------------------------------------------------------
	temple_guard = {
		idle = {
			emitters = {
				{ at = "tip", texture = "spark", c0 = "#FFD24A", c1 = "#FFD24A", s0 = 0.15, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 5, life = { 1.3, 1.3 }, speed = { 0.3, 0.3 }, spread = 180, dir = "out", accel = { 0, 0.3, 0 }, light = 1 },
				glint("#FFF2B0", 1.5),
			},
			light = { color = "#FFD24A", range = 3, brightness = 0.5 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "spark", c0 = "#FFD24A", c1 = "#FFD24A", s0 = 0.12, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 12, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 30, dir = "back", light = 1 },
				{ at = "trail", texture = "rock", c0 = "#B9AD8E", c1 = "#7D7360", s0 = 0.18, s1 = 0.18, t0 = 0, t1 = 1,
					rate = 8, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 30, dir = "back", rot = 360 },
				{ at = "trail", texture = "star", c0 = "#FFD24A", c1 = "#FFD24A", s0 = 0.3, s1 = 0.2, t0 = 0, t1 = 1,
					rate = 6, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 360, light = 1 },
			},
			rings = { airRing("shock_ring", "#FFD24A", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFD24A", range = 8, brightness = 2.5, t1 = 0.7 },
			bursts = {
				{ at = "ground", texture = "spark", c0 = "#FFD24A", c1 = "#FFD24A", s0 = 0.18, s1 = 0.1, t0 = 0, t1 = 1,
					count = 24, life = { 1, 1 }, speed = { 9, 14 }, spread = 8, dir = "up", accel = { 0, -25, 0 }, light = 1 },
				puffs(8, "#E6DCC0", "#B0A48A", 2.0),
				arc("rock", 6, "#B9AD8E", "#7D7360", 0.22, { 6, 9 }),
			},
			meshes = {
				flash("#FFF0B0", 1.4, 0.3),
				ring("shock_ring", "#FFD24A", 2.5, 0.4),
				{ mesh = "cyl", color = "#7D7360", t0 = 0, t1 = 0.17, size0 = { 0.5, 0.05, 0.5 }, size1 = { 3.6, 0.1, 3.6 },
					a0 = 0, a1 = 0, hold = 1.16, easing = "Quad" },
				{ mesh = "cyl", color = "#FFD24A", neon = true, t0 = 0.07, t1 = 0.27, size0 = { 2.3, 0.1, 2.3 },
					size1 = { 2.3, 0.1, 2.3 }, a0 = 1, a1 = 0.2, hold = 1.0, easing = "Sine" },
				{ mesh = "glyph", color = "#FFD24A", neon = true, count = 8, r = 1.48, t0 = 0.1, t1 = 0.47,
					size0 = { 0.05, 0.02, 0.05 }, size1 = { 0.36, 0.12, 0.36 }, a0 = 0, a1 = 0.2, y0 = 0.1, y1 = 0.1, hold = 0.9, easing = "Back" },
				{ mesh = "pillar", color = "#B9AD8E", count = 4, r = 1.8, t0 = 0.13, t1 = 0.53, size0 = { 0.1, 0.05, 0.1 },
					size1 = { 0.5, 1.3, 0.5 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
				{ mesh = "glyph", color = "#FFD24A", neon = true, count = 4, r = 1.8, t0 = 0.13, t1 = 1.33,
					size0 = { 0.2, 0.05, 0.2 }, size1 = { 0.4, 0.05, 0.4 }, a0 = 0, a1 = 1, y0 = 1.3, y1 = 1.9, easing = "Sine" },
				{ mesh = "spark", color = "#FFD24A", neon = true, count = 4, r = 1.8, t0 = 0.2, t1 = 0.8,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.2, 0.2, 0.2 }, a0 = 0, a1 = 1, y0 = 1.3, y1 = 1.8, easing = "Sine" },
			},
		},
	},

	-- 19 ----------------------------------------------------------------
	mangrove_root = {
		idle = {
			emitters = {
				{ at = "tip", texture = "spore", c0 = "#9AFFC8", c1 = "#9AFFC8", s0 = 0.18, s1 = 0.1, t0 = 0.2, t1 = 1,
					rate = 5, life = { 1.6, 1.6 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.25, 0 }, light = 1 },
				glint("#E8FFD0", 1.5),
			},
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "leaf", c0 = "#62A03C", c1 = "#9AD260", s0 = 0.25, s1 = 0.25, t0 = 0, t1 = 1,
					rate = 10, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 30, dir = "back", rot = 300 },
				{ at = "trail", texture = "shard", c0 = "#7C502E", c1 = "#4A301F", s0 = 0.18, s1 = 0.18, t0 = 0, t1 = 1,
					rate = 8, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 30, dir = "back", rot = 360 },
				{ at = "trail", texture = "dust", c0 = "#B49A74", c1 = "#6E5638", s0 = 0.35, smid = 1.5, s1 = 0, t0 = 0.15,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
			},
			rings = {}, -- нет меша-кольца у этого копья (fx_moss не кольцо)
		},
		impact = {
			duration = 1.5,
			bursts = {
				arc("rock", 16, "#5B4632", "#4A301F", 0.3, { 6, 10 }),
				arc("drop", 10, "#5B4632", "#5B4632", 0.14, { 7, 11 }, 1.0),
				puffs(10, "#B49A74", "#6E5638", 2.2),
			},
			meshes = {
				flash("#E8D4A8", 1.4, 0.35),
				{ mesh = "cyl", color = "#5B4632", t0 = 0, t1 = 0.2, size0 = { 1.2, 0.1, 1.2 }, size1 = { 4.0, 0.15, 4.0 },
					a0 = 0, a1 = 0, hold = 0.87, easing = "Quad" },
				{ mesh = "root_arch", color = "#7C502E", count = 6, r = 1.7, t0 = 0, t1 = 0.23, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 1.5, 1.4, 0.3 }, a0 = 0, a1 = 0, hold = 0.9, easing = "Back" },
				{ mesh = "root_spike", color = "#C0955E", count = 6, r = 0.9, t0 = 0.03, t1 = 0.37,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.3, 1.6, 0.3 }, a0 = 0, a1 = 0, hold = 0.8, easing = "Back" },
				{ mesh = "moss", color = "#62A03C", count = 6, r = 2.3, t0 = 0.13, t1 = 0.43, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.6, 0.3, 0.6 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
				{ mesh = "mud_clump", color = "#5B4632", count = 4, r = 1.3, t0 = 0, t1 = 0.3, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.35, 0.35, 0.35 }, a0 = 0, a1 = 0, hold = 0.8, easing = "Back" },
			},
		},
	},

	-- 20 ----------------------------------------------------------------
	hydra_fangs = {
		idle = {
			emitters = {
				{ at = "tip", texture = "drop", c0 = "#A8FF4A", c1 = "#A8FF4A", s0 = 0.16, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 4, life = { 1.2, 1.2 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, -0.4, 0 }, light = 1 },
				glint("#E4FFB8", 1.5),
			},
			light = { color = "#FF5A3A", range = 3, brightness = 0.4 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "shard", c0 = "#F4F0D8", c1 = "#2F9A5A", s0 = 0.36, s1 = 0.2, t0 = 0, t1 = 1,
					rate = 10, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 540 },
				{ at = "trail", texture = "drop", c0 = "#A8FF4A", c1 = "#A8FF4A", s0 = 0.16, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 10, life = { 0.9, 0.9 }, speed = { 3, 3 }, spread = 25, dir = "back", light = 1 },
				{ at = "trail", texture = "smoke", c0 = "#C8F0C0", c1 = "#5A8A5A", s0 = 0.35, smid = 1.5, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 6, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
			},
			rings = { airRing("shock_ring", "#C2FF80", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#A8FF4A", range = 7, brightness = 2, t1 = 0.5 },
			bursts = {
				arc("shard", 24, "#2F9A5A", "#F4F0D8", 0.17, { 6, 10 }, 1.0, -25, 70),
				arc("drop", 10, "#A8FF4A", "#A8FF4A", 0.14, { 7, 11 }, 1.0, -25, 25, 1),
				puffs(8, "#C8F0C0", "#5A8A5A", 2.2),
			},
			meshes = {
				flash("#E0FFB0", 1.4, 0.3),
				ring("shock_ring", "#C8FF80", 2.5, 0.4),
				-- 2 клыка крестом: впереди копья и дальше (X на высоте ~1)
				{ mesh = "fang", color = "#F4F0D8", count = 1, r = 0.8, t0 = 0, t1 = 0.33, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.5, 2.0, 0.5 }, a0 = 0, a1 = 0, y0 = 0, y1 = 0, hold = 0.9, easing = "Back" },
				{ mesh = "fang", color = "#F4F0D8", count = 1, r = 0.8, t0 = 0.07, t1 = 0.4, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.5, 2.0, 0.5 }, a0 = 0, a1 = 0, hold = 0.9, easing = "Back" },
				{ mesh = "ball", color = "#1C6A40", count = 2, r = 0.8, t0 = 0, t1 = 0.17, size0 = { 0.1, 0.02, 0.1 },
					size1 = { 0.68, 0.08, 0.68 }, a0 = 0, a1 = 0, hold = 1.0, easing = "Quad" },
				{ mesh = "part", color = "#A8FF4A", neon = true, count = 2, r = 0.8, t0 = 0.13, t1 = 0.33,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.08, 1.6, 0.08 }, a0 = 0, a1 = 0.3, hold = 1.0, easing = "Quad" },
				cracks("#1C6A40", 5, 2.2, 0.2),
				{ mesh = "fang", color = "#F4F0D8", count = 6, r = 2.2, t0 = 0.1, t1 = 0.4, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.25, 0.55, 0.25 }, a0 = 0, a1 = 0, hold = 0.7, easing = "Back" },
			},
		},
	},

	-- 21 ----------------------------------------------------------------
	storm_trident = {
		idle = {
			emitters = {
				{ at = "tip", texture = "spark", c0 = "#FFE45A", c1 = "#9A6CFF", s0 = 0.15, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 6, life = { 0.6, 0.6 }, speed = { 0.4, 0.4 }, spread = 180, dir = "out", light = 1 },
				{ at = "tip", texture = "star", c0 = "#FFE45A", c1 = "#FFE45A", s0 = 0.14, s1 = 0.14, t0 = 0, t1 = 1,
					rate = 2, life = { 0.3, 0.3 }, speed = { 0, 0.2 }, spread = 180, dir = "out", light = 1 },
			},
			light = { color = "#9A6CFF", range = 4, brightness = 0.6 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "smoke", c0 = "#D2D2EC", c1 = "#6A6884", s0 = 0.35, smid = 1.5, s1 = 0, t0 = 0.15,
					t1 = 1, rate = 8, life = { 1, 1 }, speed = { 2, 4 }, spread = 25, dir = "back", drag = 2 },
				{ at = "trail", texture = "spark", c0 = "#FFE45A", c1 = "#9A6CFF", s0 = 0.12, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 12, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 30, dir = "back", light = 1 },
				{ at = "trail", texture = "bolt", c0 = "#FFE45A", c1 = "#9A6CFF", s0 = 0.55, s1 = 0.3, t0 = 0, t1 = 1,
					rate = 6, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 360, light = 1 },
			},
			rings = { airRing("elec_ring", "#FFE45A", 2.0) },
		},
		impact = {
			duration = 1.5,
			-- три молнии: свет вспыхивает на каждой; одна запись, спад за 0.4
			light = { color = "#FFE45A", range = 9, brightness = 4, t1 = 0.4 },
			bursts = {
				arc("spark", 20, "#FFE45A", "#9A6CFF", 0.13, { 5, 10 }, 1.0, -25, 30, 1),
				{ at = "ground", texture = "smoke", c0 = "#6A6884", c1 = "#D2D2EC", s0 = 0.4, s1 = 2.2, t0 = 0.2, t1 = 1,
					count = 6, delay = 0.1, life = { 1.2, 1.2 }, speed = { 2, 2 }, spread = 60, dir = "up" },
			},
			meshes = {
				flash("#FFF6C0", 1.5, 0.3),
				-- 3 молнии с высоты 6 вокруг копья (r 1.4 / 1.7 / 1.4); ядро + ореол
				{ mesh = "bolt", color = "#FFE45A", neon = true, count = 3, r = 1.5, t0 = 0, t1 = 0.43,
					size0 = { 0.09, 6, 0.09 }, size1 = { 0.09, 6, 0.09 }, a0 = 0, a1 = 1, easing = "Linear" },
				{ mesh = "bolt_halo", color = "#9A6CFF", neon = true, count = 3, r = 1.5, t0 = 0, t1 = 0.43,
					size0 = { 0.34, 6, 0.34 }, size1 = { 0.34, 6, 0.34 }, a0 = 0.2, a1 = 1, easing = "Linear" },
				{ mesh = "elec_ring", color = "#FFE45A", neon = true, t0 = 0, t1 = 0.47, size0 = { 0.36, 0.1, 0.36 },
					size1 = { 5.6, 0.1, 5.6 }, a0 = 0, a1 = 1, easing = "Quad" },
				{ mesh = "elec_ring", color = "#9A6CFF", neon = true, t0 = 0.13, t1 = 0.6, size0 = { 0.36, 0.1, 0.36 },
					size1 = { 4.8, 0.1, 4.8 }, a0 = 0, a1 = 1, easing = "Quad" },
				{ mesh = "ball", color = "#FFF2A0", neon = true, count = 3, r = 1.5, t0 = 0, t1 = 0.3,
					size0 = { 1.0, 1.0, 1.0 }, size1 = { 1.4, 1.4, 1.4 }, a0 = 0.2, a1 = 1, y0 = 0.3, y1 = 0.3, easing = "Quad" },
				{ mesh = "cyl", color = "#3D3B58", count = 3, r = 1.5, t0 = 0, t1 = 0.1, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.9, 0.05, 0.9 }, a0 = 0, a1 = 0, hold = 1.2, easing = "Quad" },
				{ mesh = "zig", color = "#FFE45A", neon = true, count = 6, r = 1.3, t0 = 0.1, t1 = 0.33,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.5, 0.1, 0.5 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 0.3, spin = 180, easing = "Linear" },
			},
		},
	},

	-- 22 ----------------------------------------------------------------
	thunder_split = {
		idle = {
			emitters = {
				{ at = "tip", texture = "spark", c0 = "#FFF27A", c1 = "#7A9CFF", s0 = 0.15, s1 = 0.08, t0 = 0, t1 = 1,
					rate = 6, life = { 0.6, 0.6 }, speed = { 0.4, 0.4 }, spread = 180, dir = "out", light = 1 },
				{ at = "tip", texture = "star", c0 = "#FFF27A", c1 = "#FFF27A", s0 = 0.14, s1 = 0.14, t0 = 0, t1 = 1,
					rate = 2, life = { 0.3, 0.3 }, speed = { 0, 0.2 }, spread = 180, dir = "out", light = 1 },
			},
			light = { color = "#FFD93A", range = 4, brightness = 0.6 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "bolt", c0 = "#FFF27A", c1 = "#7A9CFF", s0 = 0.6, s1 = 0.3, t0 = 0, t1 = 1,
					rate = 10, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 360, light = 1 },
				{ at = "trail", texture = "spark", c0 = "#FFF27A", c1 = "#7A9CFF", s0 = 0.12, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 12, life = { 0.9, 0.9 }, speed = { 3, 5 }, spread = 30, dir = "back", light = 1 },
				{ at = "trail", texture = "star", c0 = "#FFF27A", c1 = "#FFF27A", s0 = 0.14, s1 = 0.1, t0 = 0, t1 = 1,
					rate = 5, life = { 0.5, 0.5 }, speed = { 1, 3 }, spread = 30, dir = "back", light = 1 },
			},
			rings = { airRing("shock_ring", "#7A9CFF", 2.0) },
		},
		impact = {
			duration = 1.5,
			light = { color = "#FFD93A", range = 9, brightness = 3, t1 = 0.5 },
			bursts = {
				arc("spark", 18, "#FFF27A", "#7A9CFF", 0.13, { 4, 9 }, 1.0, -25, 30, 1),
				arc("rock", 8, "#27306E", "#4452A8", 0.22, { 6, 10 }),
				{ at = "ground", texture = "smoke", c0 = "#68709A", c1 = "#68709A", s0 = 0.4, s1 = 2.2, t0 = 0.2, t1 = 1,
					count = 5, delay = 0.1, life = { 1.2, 1.2 }, speed = { 2, 2 }, spread = 60, dir = "up" },
			},
			meshes = {
				flash("#FFF8C8", 1.5, 0.3),
				ring("shock_ring", "#FFF27A", 2.5, 0.4),
				-- главная трещина 3.1 вперёд (+X) и корка; жила светится
				{ mesh = "crack", color = "#27306E", t0 = 0, t1 = 0.27, size0 = { 0.4, 0.1, 0.1 }, size1 = { 3.1, 0.1, 0.4 },
					a0 = 0, a1 = 0, hold = 1.0, easing = "Quad" },
				{ mesh = "crack_core", color = "#FFF27A", neon = true, t0 = 0, t1 = 0.27, size0 = { 0.4, 0.1, 0.1 },
					size1 = { 3.1, 0.1, 0.2 }, a0 = 0, a1 = 0.2, hold = 1.0, easing = "Quad" },
				{ mesh = "crack", color = "#27306E", count = 2, r = 0.3, t0 = 0.07, t1 = 0.4, size0 = { 0.4, 0.1, 0.1 },
					size1 = { 2.0, 0.1, 0.3 }, a0 = 0, a1 = 0, hold = 0.9, easing = "Quad" },
				{ mesh = "ball", color = "#FFF8C8", neon = true, t0 = 0, t1 = 0.43, size0 = { 0.36, 0.36, 0.36 },
					size1 = { 0.36, 0.36, 0.36 }, a0 = 0, a1 = 1, y0 = 0.2, y1 = 0.2, easing = "Quad" },
				{ mesh = "arc", color = "#FFF27A", neon = true, count = 6, r = 1.5, t0 = 0.07, t1 = 0.44,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.7, 0.55, 0.1 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 0.3, easing = "Linear" },
				{ mesh = "arc", color = "#7A9CFF", neon = true, count = 3, r = 1.0, t0 = 0.13, t1 = 0.5,
					size0 = { 0.1, 0.1, 0.1 }, size1 = { 0.7, 0.55, 0.1 }, a0 = 0, a1 = 1, y0 = 0.3, y1 = 0.3, easing = "Linear" },
				{ mesh = "part", color = "#4452A8", count = 6, r = 1.2, t0 = 0.1, t1 = 0.3, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.2, 0.45, 0.2 }, a0 = 0, a1 = 0, hold = 0.9, easing = "Back" },
			},
		},
	},

	-- 23 ----------------------------------------------------------------
	coral_branch = {
		idle = {
			emitters = {
				{ at = "tip", texture = "bubble", c0 = "#DFFBFF", c1 = "#DFFBFF", s0 = 0.2, s1 = 0.1, t0 = 0.2, t1 = 1,
					rate = 5, life = { 1.5, 1.5 }, speed = { 0.2, 0.2 }, spread = 180, dir = "out", accel = { 0, 0.8, 0 } },
				{ at = "tip", texture = "star", c0 = "#FF9FB6", c1 = "#FF9FB6", s0 = 0.15, s1 = 0.15, t0 = 0, t1 = 1,
					rate = 2, life = { 0.4, 0.4 }, speed = { 0, 0.2 }, spread = 180, dir = "out", light = 1 },
			},
			light = { color = "#7FF6FF", range = 4, brightness = 0.6 },
		},
		flight = {
			emitters = {
				{ at = "trail", texture = "bubble", c0 = "#DFFBFF", c1 = "#7FF6FF", s0 = 0.15, smid = 0.45, s1 = 0, t0 = 0.2,
					t1 = 1, rate = 16, life = { 0.9, 0.9 }, speed = { 3, 3 }, spread = 30, dir = "back", rot = 120 },
				{ at = "trail", texture = "crystal", c0 = "#FF8FB0", c1 = "#6FE9E0", s0 = 0.3, s1 = 0.2, t0 = 0, t1 = 1,
					rate = 8, life = { 1, 1 }, speed = { 11, 12 }, spread = 10, dir = "back", rot = 540, light = 0.6 },
			},
			rings = { { mesh = "ripple_ring", color = "#7FF6FF", every = 0.33, s0 = 0.5, s1 = 2.1, travel = 7, life = 1, a0 = 0.2 } },
		},
		impact = {
			duration = 1.5,
			light = { color = "#7FF6FF", range = 8, brightness = 3, t1 = 0.6 },
			bursts = {
				{ at = "ground", texture = "bubble", c0 = "#DFFBFF", c1 = "#7FF6FF", s0 = 0.25, s1 = 0.1, t0 = 0.1, t1 = 1,
					count = 18, life = { 0.8, 0.8 }, speed = { 2, 4 }, spread = 40, dir = "up", accel = { 0, 4, 0 } },
			},
			meshes = {
				flash("#C8FFFF", 1.3, 0.4, 0.4),
				{ mesh = "sand_mound", color = "#F4DFB6", t0 = 0, t1 = 0.23, size0 = { 1.0, 0.2, 1.0 }, size1 = { 1.7, 0.34, 1.7 },
					a0 = 0, a1 = 0, hold = 1.0, easing = "Back" },
				ring("ripple_ring", "#7FF6FF", 2.5, 0.53, 0, 0),
				ring("ripple_ring", "#7FF6FF", 2.2, 0.7, 0, 0.17),
				ring("ripple_ring", "#7FF6FF", 1.9, 0.86, 0, 0.33),
				-- 16 кристаллов по спирали r 0.7 -> 3.1
				{ mesh = "coral_crystal", color = "#FF8FB0", count = 11, r = 1.9, t0 = 0.07, t1 = 0.8,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.3, 0.7, 0.3 }, a0 = 0, a1 = 0, hold = 0.45, easing = "Back" },
				{ mesh = "coral_crystal", color = "#6FE9E0", count = 5, r = 2.6, t0 = 0.15, t1 = 0.8,
					size0 = { 0.05, 0.05, 0.05 }, size1 = { 0.3, 0.7, 0.3 }, a0 = 0, a1 = 0, hold = 0.45, easing = "Back" },
				{ mesh = "shard", color = "#FF6F5E", count = 4, r = 0.8, t0 = 0.03, t1 = 0.4, size0 = { 0.05, 0.05, 0.05 },
					size1 = { 0.25, 1.0, 0.25 }, a0 = 0, a1 = 0, hold = 0.8, easing = "Back" },
			},
		},
	},
}
