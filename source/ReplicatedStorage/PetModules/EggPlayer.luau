--!nonstrict
-- EggPlayer: проигрывает открытие яйца по EggOpenings (движение групп, свет, события).
local RunService = game:GetService("RunService")
local EggOpenings = require(script.Parent.EggOpenings)

local EggPlayer = {}

local function collect(model)
	local motors, parts = {}, {}
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Motor6D") and string.sub(d.Name, -6) == "_Joint" then
			local n = string.sub(d.Name, 1, -7)
			motors[n] = d
			local list = {}
			for _, p in ipairs(d.Part1:GetChildren()) do
				if p:IsA("BasePart") then table.insert(list, { part = p, size = p.Size, tr = p.Transparency }) end
			end
			local neon = #list > 0
			for _, it in ipairs(list) do if it.part.Material ~= Enum.Material.Neon then neon = false end end
			list.neon = neon
			parts[n] = list
		end
	end
	return motors, parts
end

-- k — масштаб группы из прототипа. Одиночная деталь (свечение) меняет размер,
-- группа из многих деталей при k < 1 растворяется (замена масштабу), при k < 0.02 скрыта.
local function applyK(list, k, last)
	if last and math.abs(last - k) < 0.01 then return last end
	if #list == 1 then
		list[1].part.Size = list[1].size * math.max(k, 0.01)
	elseif list.neon then
		for _, it in ipairs(list) do it.part.Size = it.size * math.max(k, 0.01) end -- светящиеся группы: только размер, прозрачность задаёт play()
	else
		local fade = k >= 1 and 0 or 1 - math.clamp(k, 0, 1)
		for _, it in ipairs(list) do it.part.Transparency = it.tr + (1 - it.tr) * fade end
	end
	return k
end

-- Покой на витрине: вернёт соединение, которое можно :Disconnect()
function EggPlayer.idle(model, eggId)
	local egg = EggOpenings[eggId]
	local motors, parts = collect(model)
	local t, lastK = 0, {}
	local function set(name, cf, k)
		local m = motors[name]
		if m then m.Transform = cf lastK[name] = applyK(parts[name], k, lastK[name]) end
	end
	local function fade(list, a) if list then for _, it in ipairs(list) do it.part.Transparency = 1 - math.clamp(a, 0, 1) end end end
	return RunService.Heartbeat:Connect(function(dt)
		t += dt
		local _, _, extra = egg.idle(t, set)
		fade(parts.sun, extra.sun) fade(parts.crack, extra.crack)
	end)
end

-- opts.hd       — длительность появления питомца в секундах (PetAnimations[petId].hd)
-- opts.onEmerge — вызывается один раз в момент появления питомца (тут запускайте PetAnimator:Hatch())
-- opts.onEvent  — function(event) для частиц/колец/вспышек из EggOpenings[eggId].events
-- opts.onDone   — вызывается, когда скорлупа полностью исчезла
function EggPlayer.play(model, eggId, opts)
	opts = opts or {}
	local egg = EggOpenings[eggId]
	assert(egg, "Нет открытия для " .. tostring(eggId))
	local motors, parts = collect(model)
	local glowPart = parts.glow and parts.glow[1] and parts.glow[1].part
	local base = model.PrimaryPart.CFrame
	local function fade(list, a) if list then for _, it in ipairs(list) do it.part.Transparency = 1 - math.clamp(a, 0, 1) end end end
	local light = Instance.new("PointLight")
	light.Color = egg.glowColor light.Range = 14 light.Brightness = 0 light.Parent = model.PrimaryPart
	local hd = opts.hd or 2.8
	local t, lastK, fired, emerged = 0, {}, {}, false
	local function set(name, cf, k)
		local m = motors[name]
		if m then m.Transform = cf lastK[name] = applyK(parts[name], k, lastK[name]) end
	end
	local conn
	local finished = false
	local function step(dt)
		if finished then return end
		t += opts.manual and dt or math.min(dt, 0.05)
		local L, glow, extra = egg.update(t, set, hd)
		light.Brightness = L * 0.8
		if glowPart then glowPart.Transparency = 1 - math.clamp(glow, 0, 1) end
		fade(parts.sun, extra.sun)     -- солнечный рисунок янтарного яйца
		fade(parts.crack, extra.crack) -- трещина-молния грозового яйца
		model.PrimaryPart.CFrame = base * CFrame.Angles(0, 0, extra.sway) -- покачивание морского яйца
		for i, ev in ipairs(egg.events) do
			if not fired[i] and t >= ev.t then fired[i] = true if opts.onEvent then opts.onEvent(ev) end end
		end
		if not emerged and t >= egg.emergeTime() then emerged = true if opts.onEmerge then opts.onEmerge() end end
		if t >= egg.duration(hd) then
			finished = true
			if conn then conn:Disconnect() end
			light:Destroy()
			if opts.onDone then opts.onDone() end
		end
	end
	-- opts.manual: the caller calls handle.step(dt) itself (own clock, skip, slow motion)
	if opts.manual then
		return { step = step, light = light, destroy = function() finished = true pcall(function() light:Destroy() end) end }
	end
	conn = RunService.Heartbeat:Connect(step)
	return conn
end

return EggPlayer
