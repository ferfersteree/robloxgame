-- StarterPlayerScripts/Client/HtmlWorld.luau
-- V37: мир из HTML-версии (растения, камни, кристаллы, здания и ориентиры зон 1-16 и 19-25) в виде кубиков.
-- Целиком это сотни тысяч деталей, поэтому детали строятся только вокруг камеры (она летит за копьём) и
-- убираются, когда камера уходит. Данные: ReplicatedStorage/HtmlWorld (Protos, Index, Z01..Z25), их пишет
-- tools/html_world_build.py. Ничего не реплицируется: детали создаются на клиенте, без коллизий и без запросов
-- (копьё, камера и звери их не видят). Выключатель: атрибут Enabled у ReplicatedStorage/HtmlWorld.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UIS = game:GetService("UserInputService")

local HtmlWorld = {}

local GROUND_Y = 0.1 -- верх земли всех зон
local CHUNK = 70 -- длина куска по z (как в HTML)
local EXTRA = 70 -- запас радиуса перед удалением
-- радиусы по классам: 1 дерево, 2 камень/кристалл, 3 трава и кусты, 4 здание зоны, 5 ориентир.
-- Те же числа в tools/html_world_build.py (там по ним считается нагрузка).
local RADIUS = { 260, 200, 100, 420, 600 }
local CAP_DESKTOP, CAP_MOBILE = 16000, 8000 -- V86: было 24000 / 11000 (меньше деталей в кадре — выше FPS) -- сколько деталей держим одновременно (дальние куски не строим сверх этого)
local STEP_TIME = 0.25
local NEAR = 0.55 -- доля радиуса, внутри которой строим всегда, даже сверх лимита
local FAST_SPEED = 35 -- студов/с: пока камера летит быстрее (за копьём), ничего не строим и не убираем (V86: было 500; герой ходит 20 студов/с; в полёте
-- на 3000 студов кадр подвисал на 50-70 мс от стройки и удаления кусков)

local started = false
local root: Instance? = nil
local protos: any = nil
local zoneRows: { { number } } = {}
local zonesLoaded: { [number]: boolean } = {}
local chunkItems: { [number]: { flora: { number }, unique: { any }, parts: number } } = {}
local templates: { [number]: Model } = {}
local live: { [number]: { folder: Folder, parts: number, ready: boolean, dead: boolean } } = {}
local pending: { [number]: number } = {} -- ключ куска -> приоритет (меньше = ближе)
local current: any = nil -- кусок, который строится сейчас
local liveParts = 0
local folderLive: Folder? = nil
local scale = 1
local cap = CAP_DESKTOP
local frameBudget = 0.004 -- сколько секунд кадра уходит на создание деталей
local reapBudget = 0.0015 -- и на удаление ушедших кусков (порциями, иначе кадр подвисает)
local dying: { { folder: Folder, kids: { Instance }, i: number } } = {}
local lastEnabled = true
local maxPumpMs, maxStepMs = 0, 0
local lastCamPos: Vector3? = nil
local lastCamT = 0
local colors: { [number]: Color3 } = {}
local cameraFast = false -- V86: камера летит; pump ждёт

local function colorOf(rgb: number): Color3
	local c = colors[rgb]
	if not c then
		c = Color3.fromRGB(rgb // 65536, (rgb // 256) % 256, rgb % 256)
		colors[rgb] = c
	end
	return c
end

local function newPart(cls: number, cx: number, cy: number, cz: number, sx: number, sy: number, sz: number, rgb: number): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = cls == 1 or cls == 4 or cls == 5
	p.Material = Enum.Material.Plastic
	p.Color = colorOf(rgb)
	p.Size = Vector3.new(sx / 4, sy / 4, sz / 4)
	p.CFrame = CFrame.new(cx / 4, cy / 4, cz / 4)
	return p
end

-- шаблон растения (по номеру прототипа), строится один раз
local function template(idx: number): Model
	local m = templates[idx]
	if m then
		return m
	end
	local pr = protos[idx]
	local cls, boxes = pr[2], pr[3]
	m = Instance.new("Model")
	m.Name = pr[1]
	for i = 1, #boxes, 7 do
		local p = newPart(cls, boxes[i], boxes[i + 1], boxes[i + 2], boxes[i + 3], boxes[i + 4], boxes[i + 5], boxes[i + 6])
		p.Parent = m
	end
	m.WorldPivot = CFrame.new()
	templates[idx] = m
	return m
end

local function zoneModule(zone: number): any
	local mod = root and root:FindFirstChild(string.format("Z%02d", zone))
	if not mod then
		return nil
	end
	local ok, data = pcall(require, mod)
	if not ok then
		warn("[HtmlWorld] " .. mod.Name .. ": " .. tostring(data))
		return nil
	end
	return data
end

local function chunkFor(key: number)
	local c = chunkItems[key]
	if not c then
		c = { flora = {}, unique = {}, parts = 0 }
		chunkItems[key] = c
	end
	return c
end

-- раскладывает растения и здания зоны по кускам (cz * 8 + класс)
local function loadZone(zone: number)
	if zonesLoaded[zone] then
		return
	end
	zonesLoaded[zone] = true
	local data = zoneModule(zone)
	if not data then
		return
	end
	local v = data.v
	for i = 1, #v, 3 do
		local code, z = v[i], v[i + 2] / 10
		local pr = protos[code // 4 + 1]
		if pr then
			local cz = math.max(0, math.floor(-z / CHUNK))
			local c = chunkFor(cz * 8 + pr[2])
			local f = c.flora
			local n = #f
			f[n + 1], f[n + 2], f[n + 3] = code, v[i + 1], v[i + 2]
			c.parts += #pr[3] // 7
		end
	end
	for _, e in data.u do
		local cz = math.max(0, math.floor(-(e[4] / 10) / CHUNK))
		local c = chunkFor(cz * 8 + e[1])
		table.insert(c.unique, e)
		c.parts += #e[5] // 7
	end
end

-- все зоны, которые пересекает кусок, должны быть загружены, иначе кусок построится неполным
local function chunkReady(cz: number): boolean
	local lo, hi = cz * CHUNK - 3, (cz + 1) * CHUNK - 3 -- расстояние от старта; мировая z = -3 - расстояние
	for _, row in zoneRows do
		if row[3] >= lo and row[2] <= hi and not zonesLoaded[row[1]] then
			return false
		end
	end
	return true
end

local function distToChunk(camX: number, camZ: number, cz: number): number
	local zlo, zhi = -(cz + 1) * CHUNK, -cz * CHUNK
	local dz = if camZ < zlo then zlo - camZ elseif camZ > zhi then camZ - zhi else 0
	local dx = math.max(math.abs(camX) - 120, 0)
	return math.sqrt(dx * dx + dz * dz)
end

local function unload(key: number)
	local l = live[key]
	if not l then
		return
	end
	live[key] = nil
	l.dead = true
	liveParts -= l.parts
	-- сам кусок убираем порциями в reap(), чтобы не подвешивать кадр
	table.insert(dying, { folder = l.folder, kids = l.folder:GetChildren(), i = 1 })
end

local function reap(deadline: number)
	while #dying > 0 and os.clock() < deadline do
		local d = dying[#dying]
		local kids = d.kids
		while d.i <= #kids and os.clock() < deadline do
			kids[d.i]:Destroy()
			d.i += 1
		end
		if d.i > #kids then
			d.folder:Destroy()
			table.remove(dying)
		end
	end
end

local function clearAll()
	for key, l in live do
		live[key] = nil
		l.dead = true
		l.folder:Destroy()
	end
	for _, d in dying do
		d.folder:Destroy()
	end
	table.clear(dying)
	table.clear(pending)
	current = nil
	liveParts = 0
end

-- строит часть куска, пока не вышло время кадра; true, когда кусок готов
local function advance(job: any, deadline: number): boolean
	local c = job.items
	local folder = job.folder
	local f = c.flora
	while job.fi <= #f do
		local code, x, z = f[job.fi], f[job.fi + 1] / 10, f[job.fi + 2] / 10
		job.fi += 3
		local pr = protos[code // 4 + 1]
		local m = template(code // 4 + 1):Clone()
		m:PivotTo(CFrame.new(x, GROUND_Y, z) * CFrame.Angles(0, (code % 4) * math.pi / 2, 0))
		m.Parent = folder
		job.live.parts += #pr[3] // 7
		liveParts += #pr[3] // 7
		if os.clock() >= deadline then
			return false
		end
	end
	local u = c.unique
	while job.ui <= #u do
		local e = u[job.ui]
		local boxes = e[5]
		local ox, oz = e[3] / 10, e[4] / 10
		if not job.model then
			local m = Instance.new("Model")
			m.Name = e[2]
			m.Parent = folder
			job.model = m
			job.bi = 1
		end
		local cls = e[1]
		local n = 0
		while job.bi <= #boxes do
			local i = job.bi
			local p = newPart(cls, boxes[i] + ox * 4, boxes[i + 1] + GROUND_Y * 4, boxes[i + 2] + oz * 4, boxes[i + 3], boxes[i + 4], boxes[i + 5], boxes[i + 6])
			p.Parent = job.model
			job.bi += 7
			job.live.parts += 1
			liveParts += 1
			n += 1
			if n % 24 == 0 and os.clock() >= deadline then
				return false
			end
		end
		job.model = nil
		job.ui += 1
	end
	return true
end

local function pump()
	if not lastEnabled then
		return
	end
	if cameraFast then
		return
	end
	local t0 = os.clock()
	reap(t0 + reapBudget)
	local deadline = os.clock() + frameBudget
	while os.clock() < deadline do
		if not current then
			-- ближайший из ожидающих
			local bestKey, bestPrio = nil, math.huge
			for key, prio in pending do
				if prio < bestPrio then
					bestKey, bestPrio = key, prio
				end
			end
			if not bestKey then
				return
			end
			pending[bestKey] = nil
			local items = chunkItems[bestKey]
			if not items or live[bestKey] then
				continue
			end
			if liveParts + items.parts > cap and bestPrio > NEAR then
				-- сверх лимита дальние куски не строим; вернутся в очередь на следующем шаге, если ещё нужны
				continue
			end
			local folder = Instance.new("Folder")
			folder.Name = "K" .. bestKey
			folder.Parent = folderLive
			local l = { folder = folder, parts = 0, ready = false, dead = false }
			live[bestKey] = l
			current = { key = bestKey, items = items, folder = folder, live = l, fi = 1, ui = 1, bi = 1 }
		end
		local done = advance(current, deadline)
		if done then
			current.live.ready = true
			current = nil
		else
			break
		end
	end
	local ms = (os.clock() - t0) * 1000
	if ms > maxPumpMs then
		maxPumpMs = ms
	end
end

local function step()
	local t0 = os.clock()
	local enabled = root ~= nil and root:GetAttribute("Enabled") ~= false
	if enabled ~= lastEnabled then
		lastEnabled = enabled
		if not enabled then
			clearAll()
		end
	end
	if not enabled then
		return
	end
	local cam = workspace.CurrentCamera
	if not cam then
		return
	end
	local pos = cam.CFrame.Position
	local camX, camZ = pos.X, pos.Z
	-- скорость камеры
	local now = os.clock()
	local fast = false
	if lastCamPos and now > lastCamT then
		fast = (Vector3.new(camX - lastCamPos.X, 0, camZ - lastCamPos.Z)).Magnitude / (now - lastCamT) > FAST_SPEED
	end
	lastCamPos, lastCamT = pos, now
	cameraFast = fast
	if pos.Y > 300 then
		fast = true -- камера высоко (комната раскрытия яйца и т. п.): мир внизу не нужен
	end
	-- зоны, которые попадают в самый большой радиус; за шаг грузим одну, ближайшую (require и раскладка стоят миллисекунды)
	local rmax = RADIUS[5] * scale + CHUNK
	local dLo, dHi = -camZ - rmax, -camZ + rmax
	local nextZone, nextD = nil, math.huge
	for _, row in zoneRows do
		-- row: { zone, from, to }; мировая z = -3 - расстояние
		if not zonesLoaded[row[1]] and row[3] + 3 >= dLo and row[2] + 3 <= dHi then
			local d = math.abs(-((row[2] + row[3]) / 2 + 3) - camZ)
			if d < nextD then
				nextZone, nextD = row[1], d
			end
		end
	end
	if nextZone and not fast then
		loadZone(nextZone)
	end
	-- какие куски нужны
	local wanted: { [number]: number } = {}
	local ready: { [number]: boolean } = {}
	for cls = 1, 5 do
		local r = RADIUS[cls] * scale
		local cMin = math.max(0, math.floor(-(camZ + r) / CHUNK))
		local cMax = math.max(0, math.floor(-(camZ - r) / CHUNK))
		for cz = cMin, cMax do
			local key = cz * 8 + cls
			if chunkItems[key] then
				local rd = ready[cz]
				if rd == nil then
					rd = chunkReady(cz)
					ready[cz] = rd
				end
				local d = distToChunk(camX, camZ, cz)
				if rd and d <= r then
					wanted[key] = d / r
				end
			end
		end
	end
	-- убрать ушедшие
	for key, l in live do
		local cls = key % 8
		local r = RADIUS[cls] * scale + EXTRA
		if distToChunk(camX, camZ, key // 8) > r then
			if current and current.key == key then
				current = nil
			end
			unload(key)
		end
	end
	-- ожидающие: оставить только нужные; на быстром пролёте новое не строим
	for key in pending do
		if fast or not wanted[key] then
			pending[key] = nil
		end
	end
	if not fast then
		for key, prio in wanted do
			if not live[key] and not (current and current.key == key) then
				pending[key] = prio
			end
		end
	end
	-- слишком много деталей: убираем самый дальний из дальних кусков
	if liveParts > cap * 1.25 then
		local worstKey, worst = nil, NEAR
		for key, l in live do
			if l.ready then
				local cls = key % 8
				local p = distToChunk(camX, camZ, key // 8) / (RADIUS[cls] * scale)
				if p > worst then
					worstKey, worst = key, p
				end
			end
		end
		if worstKey then
			unload(worstKey)
		end
	end
	local ms = (os.clock() - t0) * 1000
	if ms > maxStepMs then
		maxStepMs = ms
	end
	if folderLive then
		local chunks, waiting = 0, 0
		for _ in live do
			chunks += 1
		end
		for _ in pending do
			waiting += 1
		end
		-- счётчики для отладки (видны в Explorer у папки HtmlWorldLive)
		folderLive:SetAttribute("Parts", liveParts)
		folderLive:SetAttribute("Chunks", chunks)
		folderLive:SetAttribute("Pending", waiting)
		folderLive:SetAttribute("Dying", #dying)
		folderLive:SetAttribute("PumpMaxMs", math.floor(maxPumpMs * 10) / 10)
		folderLive:SetAttribute("StepMaxMs", math.floor(maxStepMs * 10) / 10)
	end
end

function HtmlWorld.init()
	if started then
		return
	end
	started = true
	root = RS:WaitForChild("HtmlWorld", 15)
	if not root then
		warn("[HtmlWorld] ReplicatedStorage.HtmlWorld not found")
		return
	end
	local okP, p = pcall(require, (root :: Instance):WaitForChild("Protos"))
	local okI, index = pcall(require, (root :: Instance):WaitForChild("Index"))
	if not okP or not okI then
		warn("[HtmlWorld] data failed: " .. tostring(okP and index or p))
		return
	end
	protos = p
	for _, r in index do
		table.insert(zoneRows, { r[1], r[2], r[3] })
	end
	local mobile = UIS.TouchEnabled and not UIS.KeyboardEnabled
	scale = mobile and 0.65 or 1
	cap = mobile and CAP_MOBILE or CAP_DESKTOP
	frameBudget = mobile and 0.002 or 0.003 -- V86: было 0.003 / 0.004
	reapBudget = mobile and 0.001 or 0.0015
	folderLive = Instance.new("Folder")
	folderLive.Name = "HtmlWorldLive"
	folderLive.Parent = workspace
	RunService.Heartbeat:Connect(pump)
	task.spawn(function()
		while true do
			local ok, err = pcall(step)
			if not ok then
				warn("[HtmlWorld] step failed: " .. tostring(err))
			end
			task.wait(STEP_TIME)
		end
	end)
end

-- Для проверки: сколько деталей и кусков живёт сейчас
function HtmlWorld.stats()
	local chunks, ready, waiting = 0, 0, 0
	for _, l in live do
		chunks += 1
		if l.ready then
			ready += 1
		end
	end
	for _ in pending do
		waiting += 1
	end
	return { parts = liveParts, chunks = chunks, ready = ready, pending = waiting, cap = cap, scale = scale }
end

-- Для проверки в Studio (режим Edit): строит все куски от расстояния from до to (в студах от старта) сразу,
-- без подгрузки по камере. Возвращает число деталей.
function HtmlWorld.preview(from: number, to: number, parent: Instance): number
	root = root or RS:WaitForChild("HtmlWorld")
	protos = protos or require((root :: Instance):WaitForChild("Protos"))
	if #zoneRows == 0 then
		for _, r in require((root :: Instance):WaitForChild("Index")) do
			table.insert(zoneRows, { r[1], r[2], r[3] })
		end
	end
	for _, row in zoneRows do
		if row[3] + 3 >= from - CHUNK and row[2] + 3 <= to + CHUNK then
			loadZone(row[1])
		end
	end
	local total = 0
	local deadline = math.huge
	for cz = math.floor((from + 3) / CHUNK), math.floor((to + 3) / CHUNK) do
		for cls = 1, 5 do
			local items = chunkItems[cz * 8 + cls]
			if items then
				local folder = Instance.new("Folder")
				folder.Name = "K" .. (cz * 8 + cls)
				folder.Parent = parent
				local l = { folder = folder, parts = 0, ready = false, dead = false }
				local job = { key = cz * 8 + cls, items = items, folder = folder, live = l, fi = 1, ui = 1, bi = 1 }
				advance(job, deadline)
				total += l.parts
			end
		end
	end
	return total
end

return HtmlWorld
