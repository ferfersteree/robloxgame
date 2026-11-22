-- Clear only the local reveal's line of sight; the shared map stays untouched.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Fx = require(script.Parent.WorldFx)

local Occlusion = {}
local player = Players.LocalPlayer
local renderName = "RevealLineOfSight"
local originals: { [BasePart]: number } = {}
local disabled: { [Instance]: boolean } = {}
local characterParts: { BasePart } = {}
local characterConnection: RBXScriptConnection? = nil
local respawnConnection: RBXScriptConnection? = nil
local worldConnection: RBXScriptConnection? = nil
local nearby: { BasePart } = {}
local active = false
local focus = Vector3.zero
local height = 2
local elapsed = 0

local function protected(part: BasePart): boolean
	return part:IsDescendantOf(Fx.folder) or (player.Character ~= nil and part:IsDescendantOf(player.Character))
end

local function rememberNearby(object: Instance)
	if not object:IsA("BasePart") or object.Transparency >= 1 or protected(object) then return end
	local reach = math.max(48, height * 4 + 24)
	if (object.Position - focus).Magnitude <= reach + object.Size.Magnitude * 0.5 then
		table.insert(nearby, object)
	end
end

---------------------------------------------------------------------
-- V74: пространственный индекс деталей мира. Замер в Studio: обход workspace:GetDescendants() (около 150 тысяч деталей)
-- на старте сцены улова занимал 150-165 мс в одном кадре, это и был рывок при приземлении копья. Теперь детали один
-- раз в фоне раскладываются по клеткам 64x64 (по X и Z), новые и удалённые обновляют индекс, а сцена берёт только
-- клетки рядом с точкой. Крупные детали (длиннее клетки) лежат отдельным списком и проверяются всегда.
---------------------------------------------------------------------
local CELL = 64
local cells: { [number]: { [BasePart]: boolean } } = {}
local cellOf: { [BasePart]: number } = setmetatable({}, { __mode = "k" }) :: any
local bigParts: { [BasePart]: boolean } = setmetatable({}, { __mode = "k" }) :: any
local indexReady = false
-- V76: детали, появившиеся за последние секунды (HtmlWorld достраивает деревья и постройки, пока копьё летит)
local recent: { BasePart } = {}
local recentAt: { number } = {}
local recentN = 0

local function cellKey(ix: number, iz: number): number
	return (ix + 8192) * 16384 + (iz + 8192)
end

local function indexAdd(part: BasePart)
	if cellOf[part] ~= nil or bigParts[part] then
		return
	end
	if part.Size.Magnitude > CELL then
		bigParts[part] = true
		return
	end
	local pos = part.Position
	local key = cellKey(math.floor(pos.X / CELL), math.floor(pos.Z / CELL))
	local cell = cells[key]
	if not cell then
		cell = {}
		cells[key] = cell
	end
	cell[part] = true
	cellOf[part] = key
end

local function indexRemove(part: Instance)
	local key = cellOf[part :: any]
	if key then
		local cell = cells[key]
		if cell then
			cell[part :: any] = nil
		end
		cellOf[part :: any] = nil
	end
	bigParts[part :: any] = nil
end

-- кандидаты рядом с точкой: то же условие, что у полного обхода (не дальше reach + половина диагонали детали)
local function indexQuery(position: Vector3, animalHeight: number): { BasePart }
	local reach = math.max(48, animalHeight * 4 + 24)
	local out: { BasePart } = {}
	local span = reach + CELL * 0.5
	for ix = math.floor((position.X - span) / CELL), math.floor((position.X + span) / CELL) do
		for iz = math.floor((position.Z - span) / CELL), math.floor((position.Z + span) / CELL) do
			local cell = cells[cellKey(ix, iz)]
			if cell then
				for part in cell do
					if part.Parent and part.Transparency < 1 and (part.Position - position).Magnitude <= reach + part.Size.Magnitude * 0.5 and not protected(part) then
						table.insert(out, part)
					end
				end
			end
		end
	end
	for part in bigParts do
		if part.Parent and part.Transparency < 1 and (part.Position - position).Magnitude <= reach + part.Size.Magnitude * 0.5 and not protected(part) then
			table.insert(out, part)
		end
	end
	return out
end

-- фоновая раскладка всего мира: 2 мс на кадр, один раз за сеанс; поддерево эффектов не индексируется
task.spawn(function()
	workspace.DescendantAdded:Connect(function(object)
		if object:IsA("BasePart") and not object:IsDescendantOf(Fx.folder) then
			indexAdd(object)
			-- журнал недавно появившихся деталей: begin дополняет ими список, снятый при броске
			recentN += 1
			recent[recentN] = object
			recentAt[recentN] = os.clock()
			if recentN > 60000 then -- старую половину журнала выбрасываем (HtmlWorld за дальний полёт достраивает до ~24 тысяч деталей)
				local keep = 30000
				table.move(recent, recentN - keep + 1, recentN, 1)
				table.move(recentAt, recentN - keep + 1, recentN, 1)
				for i = keep + 1, recentN do
					recent[i] = nil
					recentAt[i] = nil
				end
				recentN = keep
			end
		end
	end)
	workspace.DescendantRemoving:Connect(indexRemove)
	local stack: { Instance } = { workspace }
	local t0 = os.clock()
	while #stack > 0 do
		local node = table.remove(stack) :: Instance
		for _, child in node:GetChildren() do
			if child == Fx.folder then
				continue
			end
			if child:IsA("BasePart") then
				indexAdd(child)
			end
			table.insert(stack, child)
		end
		if os.clock() - t0 > 0.002 then
			RunService.Heartbeat:Wait()
			t0 = os.clock()
		end
	end
	indexReady = true
end)

export type Prepared = { focus: Vector3, height: number, list: { BasePart }, done: boolean, cancelled: boolean, t0: number? }
local SCAN_BUDGET = 0.0015 -- секунд на кадр при заранее подготовленном обходе мира

-- Обход workspace заранее (пока копьё летит), кусками по SCAN_BUDGET за кадр: на старте раскрытия в одном кадре
-- он давал заметный рывок. Список кандидатов тот же, что собирает begin; поддеревья ClientFx и персонажа пропускаются
-- (их детали protected и в список всё равно не попадают).
function Occlusion.prepare(position: Vector3, animalHeight: number): Prepared
	local prep: Prepared = { focus = position, height = animalHeight, list = {}, done = false, cancelled = false }
	if indexReady then
		-- V77: индекс готов. Список собирается в фоне по клеткам (не больше SCAN_BUDGET за кадр: сбор целиком стоил
		-- 30-40 мс и попал бы в кадр броска) и складывается тремя кольцами от точки наружу: первая порция проверки
		-- в начале сцены попадает на куст и то, что рядом с ним
		prep.t0 = os.clock()
		task.spawn(function()
			local reach = math.max(48, animalHeight * 4 + 24)
			local rings: { { BasePart } } = { {}, {}, {} }
			local function consider(part: BasePart)
				if part.Parent and part.Transparency < 1 then
					local d = (part.Position - position).Magnitude
					if d <= reach + part.Size.Magnitude * 0.5 and not protected(part) then
						table.insert(if d < 14 then rings[1] elseif d < 30 then rings[2] else rings[3], part)
					end
				end
			end
			local span = reach + CELL * 0.5
			local t0 = os.clock()
			for ix = math.floor((position.X - span) / CELL), math.floor((position.X + span) / CELL) do
				for iz = math.floor((position.Z - span) / CELL), math.floor((position.Z + span) / CELL) do
					local cell = cells[cellKey(ix, iz)]
					if cell then
						for part in cell do
							consider(part)
						end
					end
					-- пауза только между клетками: внутри клетки таблица не должна меняться под перебором
					if os.clock() - t0 > SCAN_BUDGET then
						RunService.Heartbeat:Wait()
						if prep.cancelled then
							return
						end
						t0 = os.clock()
					end
				end
			end
			for part in bigParts do
				consider(part)
			end
			local list = rings[1]
			table.move(rings[2], 1, #rings[2], #list + 1, list)
			table.move(rings[3], 1, #rings[3], #list + 1, list)
			prep.list = list
			prep.done = not prep.cancelled
		end)
		return prep
	end
	task.spawn(function()
		local reach = math.max(48, animalHeight * 4 + 24)
		local skipChar = player.Character
		local stack: { Instance } = { workspace }
		local t0 = os.clock()
		while #stack > 0 do
			if prep.cancelled then
				return
			end
			local node = table.remove(stack) :: Instance
			for _, child in node:GetChildren() do
				if child == Fx.folder or child == skipChar then
					continue
				end
				if child:IsA("BasePart") and child.Transparency < 1 and not protected(child) then
					if (child.Position - position).Magnitude <= reach + child.Size.Magnitude * 0.5 then
						table.insert(prep.list, child)
					end
				end
				if #child:GetChildren() > 0 then
					table.insert(stack, child)
				end
			end
			if os.clock() - t0 > SCAN_BUDGET then
				RunService.Heartbeat:Wait()
				t0 = os.clock()
			end
		end
		prep.done = not prep.cancelled
	end)
	return prep
end

function Occlusion.discard(prep: Prepared?)
	if prep then
		prep.cancelled = true
		table.clear(prep.list)
	end
end

local function crossesBox(origin: Vector3, direction: Vector3, half: Vector3): boolean
	local low, high = 0, 1
	for axis = 1, 3 do
		local a = if axis == 1 then origin.X elseif axis == 2 then origin.Y else origin.Z
		local d = if axis == 1 then direction.X elseif axis == 2 then direction.Y else direction.Z
		local extent = (if axis == 1 then half.X elseif axis == 2 then half.Y else half.Z) + 0.04
		if math.abs(d) < 0.00001 then
			if math.abs(a) > extent then return false end
		else
			local first, last = (-extent - a) / d, (extent - a) / d
			if first > last then first, last = last, first end
			low, high = math.max(low, first), math.min(high, last)
			if low > high then return false end
		end
	end
	return high >= 0 and low < 0.995
end

local function conceal(part: BasePart)
	if originals[part] == nil then
		originals[part] = part.LocalTransparencyModifier
	end
	part.LocalTransparencyModifier = 1
end

local function addCharacterPart(object: Instance)
	if object:IsA("BasePart") then
		table.insert(characterParts, object)
		conceal(object)
	elseif object:IsA("ParticleEmitter") or object:IsA("Trail") or object:IsA("Beam") then
		disabled[object] = object.Enabled
		object.Enabled = false
	end
end

local function watchCharacter(character: Model)
	if characterConnection then characterConnection:Disconnect() end
	table.clear(characterParts)
	for _, object in character:GetDescendants() do addCharacterPart(object) end
	characterConnection = character.DescendantAdded:Connect(addCharacterPart)
end

-- точки, которые должны быть видны: вся сцена, а не один луч к ногам зверя (ветки над кустом, помехи сбоку)
local function sightTargets(camera: Camera): { Vector3 }
	local right = camera.CFrame.RightVector
	local width = math.clamp(height * 0.75, 2.2, 11)
	local top = math.max(5.5, height * 1.3 + 1)
	local targets = {}
	for _, y in { 0.35, top * 0.5, top } do
		for _, x in { -width, 0, width } do
			table.insert(targets, focus + right * x + Vector3.yAxis * y)
		end
	end
	return targets
end

-- V77: проверка деталей из списка nearby порциями. Замер в Studio: полный проход по списку (тысячи деталей, по 9 лучей
-- на каждую) раз в 0,08 с давал кадры на 10-15 мс длиннее всё время показа. Теперь каждый кадр проверяется небольшая
-- порция по кругу; список отсортирован от точки наружу, поэтому ближние помехи убираются первыми.
local scanIdx = 1
local SCAN_FIRST = 600 -- деталей в кадре старта сцены
local SCAN_STEP = 220 -- деталей за обычный кадр
local function scanSlice(count: number)
	local camera = workspace.CurrentCamera
	local n = #nearby
	if not camera or n == 0 then
		return
	end
	local targets = sightTargets(camera)
	local eye = camera.CFrame.Position
	for _ = 1, math.min(count, n) do
		if scanIdx > n then
			scanIdx = 1
		end
		local part = nearby[scanIdx]
		scanIdx += 1
		-- originals[part] ~= nil: деталь уже скрыта
		if part.Parent and originals[part] == nil and part.Transparency < 1 then
			local cf, half = part.CFrame, part.Size * 0.5
			local origin = cf:PointToObjectSpace(eye)
			for _, target in targets do
				if crossesBox(origin, cf:VectorToObjectSpace(target - eye), half) then
					conceal(part)
					break
				end
			end
		end
	end
end

-- запрос движка: детали с CanQuery, заслоняющие точки сцены
local function engineQuery()
	local camera = workspace.CurrentCamera
	if not camera then
		return
	end
	local ignored: { Instance } = { Fx.folder }
	if player.Character then
		table.insert(ignored, player.Character)
	end
	for _, part in camera:GetPartsObscuringTarget(sightTargets(camera), ignored) do
		if part:IsA("BasePart") and part.Transparency < 1 then
			conceal(part)
		end
	end
end

-- full = true: пройти весь список сразу (старое поведение); иначе запрос движка и первая порция ближних деталей
function Occlusion.refresh(full: boolean?)
	if not active then
		return
	end
	engineQuery()
	if full then
		scanIdx = 1
		scanSlice(#nearby)
	else
		scanSlice(SCAN_FIRST)
	end
end

-- V65: камера переехала к зверю: дальше расчищаем вид на новую точку (без нового обхода всей карты)
function Occlusion.setFocus(position: Vector3, animalHeight: number)
	if not active then
		return
	end
	focus = position
	height = animalHeight
	scanIdx = 1 -- новая точка: снова от ближних деталей
	Occlusion.refresh()
end

function Occlusion.finish()
	active = false
	RunService:UnbindFromRenderStep(renderName)
	if characterConnection then characterConnection:Disconnect(); characterConnection = nil end
	if respawnConnection then respawnConnection:Disconnect(); respawnConnection = nil end
	if worldConnection then worldConnection:Disconnect(); worldConnection = nil end
	for part, old in originals do
		if part.Parent then part.LocalTransparencyModifier = old end
	end
	for object, old in disabled do
		if object.Parent then (object :: any).Enabled = old end
	end
	table.clear(originals)
	table.clear(disabled)
	table.clear(characterParts)
	table.clear(nearby)
end

-- pre: заготовленный Occlusion.prepare; подходит, только если закончен и для той же точки и высоты
function Occlusion.begin(position: Vector3, animalHeight: number, pre: Prepared?)
	Occlusion.finish()
	local usePre = pre ~= nil and pre.done and not pre.cancelled and (pre.focus - position).Magnitude < 0.01 and pre.height == animalHeight
	if pre and not usePre then
		pre.cancelled = true
	end
	focus = position
	height = animalHeight
	elapsed = 0
	active = true
	if player.Character then watchCharacter(player.Character) end
	respawnConnection = player.CharacterAdded:Connect(watchCharacter)
	if usePre then
		nearby = (pre :: Prepared).list
		-- V76: список снят при броске (в кадре старта сцены его сбор стоил 30-40 мс). За время полёта рядом могли
		-- достроиться деревья и постройки: добавляем только детали, появившиеся после снимка, из журнала
		local since = (pre :: Prepared).t0
		if since then
			for i = recentN, 1, -1 do
				if recentAt[i] < since then
					break
				end
				local part = recent[i]
				if part.Parent then
					rememberNearby(part)
				end
			end
		end
	elseif indexReady then
		nearby = indexQuery(position, animalHeight) -- без заготовки: только клетки рядом с точкой
	else
		for _, object in workspace:GetDescendants() do rememberNearby(object) end -- первые секунды сеанса, пока индекс строится
	end
	worldConnection = workspace.DescendantAdded:Connect(rememberNearby)
	scanIdx = 1
	Occlusion.refresh()
	RunService:BindToRenderStep(renderName, Enum.RenderPriority.Camera.Value + 3, function(dt)
		-- Roblox's normal camera transparency controller runs earlier in the frame.
		-- Keep accessories and held tools hidden even on a very short throw.
		for _, part in characterParts do
			if part.Parent then part.LocalTransparencyModifier = 1 end
		end
		elapsed += dt
		if elapsed >= 0.08 then
			elapsed = 0
			engineQuery()
		end
		scanSlice(SCAN_STEP)
	end)
end

return Occlusion
