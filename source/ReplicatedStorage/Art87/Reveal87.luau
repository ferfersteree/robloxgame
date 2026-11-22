-- ReplicatedStorage/Art87/Reveal87
-- V87: раскрытие добычи кустом и появлением зверя от Claude Design.
-- Куст биома (Tease_* по редкости, потом Open_*) и зверь (Reveal, потом Idle) собираются заранее (ensureBush/ensureAnimal,
-- пока копьё летит), потом сцена ставится в мир и проигрывается. Модуль не знает про интерфейс и камеру: Reveal.luau
-- зовёт его шаги и сам делает свет, вспышки, карточку.
-- Координаты: зверь смотрит в -Z и стоит в точке поимки лицом к игроку; куст в локальной точке (0, 0, +dist) за ним.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Debris = game:GetService("Debris")
local Lib = require(script.Parent:WaitForChild("Lib"))

local FPS = 30
local SKIP_RATE = 5 -- во сколько раз ускоряются клипы при «Пропустить»
-- Motor6D.Transform не масштабируется Model:ScaleTo (масштабируются только C0/C1), поэтому смещения клипов домножаем
-- на масштаб сами. Если Lib начнёт масштабировать смещения сам, выключить.
local SCALE_TRANSFORM = false -- V87: Lib.pose сам домножает смещения на масштаб модели (rootScaleLoc для корня)

local Reveal87 = {}
local Scene = {}
Scene.__index = Scene

export type Args = { sp: string, zone: number, rarity: number, ws: number, mut: string?, plan: any, parent: Instance }

-- Есть ли у пары биом/зверь новые модели и данные
-- V87: один раз за сессию пробуем собрать зверя и куст: если сборка падает, раскрытие идёт старым путём (иначе
-- ошибка внутри сцены выкидывала игрока из охоты)
local tried: { [string]: boolean } = {}
local function buildsOk(key: string, build: () -> Model?): boolean
	local r = tried[key]
	if r == nil then
		local ok, m = pcall(build)
		r = ok and m ~= nil
		if ok and m then
			m:Destroy()
		elseif not ok then
			warn("[Reveal87] " .. key .. ": " .. tostring(m))
		end
		tried[key] = r
	end
	return r
end

function Reveal87.supports(spId: string, zone: number): boolean
	local ok, res = pcall(function()
		return Lib.hasBush(zone) and Lib.hasAnimal(spId)
	end)
	if not (ok and res == true) then
		return false
	end
	return buildsOk("a:" .. spId, function()
		return (Lib.animal(spId))
	end) and buildsOk("b:" .. zone, function()
		return (Lib.bush(zone))
	end)
end

-- Геометрия сцены от точки поимки pos и места игрока from. ws — WorldScale зверя (куст растёт вместе с ним).
function Reveal87.plan(spId: string, zone: number, pos: Vector3, from: Vector3, ws: number): any
	local ad = Lib.animalData(spId)
	local bd = Lib.bushData(zone)
	local toward = Vector3.new(from.X - pos.X, 0, from.Z - pos.Z)
	local dir = if toward.Magnitude > 0.001 then toward.Unit else Vector3.zAxis
	local finalCF = CFrame.lookAt(pos, pos + dir)
	local bushScale = math.max(ad.cover or 1, 0.5) * ws
	local dist = (ad.dist or 2) * ws
	local bushCF = finalCF * CFrame.new(0, 0, dist)
	local h = (ad.height or 2) * ws
	local w = (ad.width or 1.5) * ws
	local len = (ad.length or 2) * ws
	local bushH = (if bd.size then bd.size[2] else 4) * bushScale
	local center = bushCF.Position
	return {
		Direction = dir, Finish = pos, Start = pos, Center = center, Focus = center:Lerp(pos, 0.5),
		Frame = bushCF, BushCF = bushCF, FinalCF = finalCF, Height = math.max(h, bushH * 0.6), CoverScale = bushScale,
		h = h, w = w, len = len, bounds = { { -w / 2, 0, -len / 2 }, { w / 2, h, len / 2 } },
	}
end

---------------------------------------------------------------------
-- Проигрывание клипов с поправкой на масштаб
---------------------------------------------------------------------
local function fixScale(rig: any, s: number, rootS: number?)
	if not SCALE_TRANSFORM or s == 1 or rig.dead then
		return
	end
	local q = s - 1
	for _, m in rig.motors do
		local p = m.Transform.Position
		if p ~= Vector3.zero then
			m.Transform = CFrame.new(p * q) * m.Transform
		end
	end
	local rm = rig.rootMotor
	if rm then
		-- смещение корня зависит только от общего масштаба, а не от собственного ключа масштаба корня
		local p = rm.Transform.Position
		if p ~= Vector3.zero then
			rm.Transform = CFrame.new(p * ((rootS or s) - 1)) * rm.Transform
		end
	end
end

-- sf: функция текущего масштаба (у зверя он меняется по ключу масштаба корня Reveal)
local function playRig(rig: any, clip: string, loop: boolean, onDone: (() -> ())?, sf: () -> (number, number?))
	if not rig then
		return
	end
	rig:play(clip, loop, onDone)
	if rig.clip == clip then
		fixScale(rig, sf())
	end
end

local function stepRig(rig: any, dt: number, rate: number, sf: () -> (number, number?))
	if not rig or rig.dead or rig.clip == nil then
		return
	end
	rig.rate = rate
	local before = rig.clip
	rig:step(dt)
	-- клип сменился в onDone (Reveal -> Idle): новый клип уже поправлен в playRig, второй раз не домножаем
	if rig.clip ~= nil and rig.clip ~= before then
		return
	end
	fixScale(rig, sf())
end

---------------------------------------------------------------------
-- Сцена
---------------------------------------------------------------------
function Reveal87.new(a: Args): any
	local self = setmetatable({
		a = a, sp = a.sp, zone = a.zone, rarity = a.rarity, ws = a.ws, plan = a.plan, parent = a.parent,
		cf = a.plan.FinalCF, alive = true, dead = false, revealed = false, idle = false,
		folders = {}, isFast = nil,
	}, Scene)
	return self
end

-- Куст: клон, поворот и масштаб (без родителя: дешёвая часть остаётся на момент показа)
function Scene.ensureBush(self: any)
	if self.dead or self.bush then
		return
	end
	local m, rig = Lib.bush(self.zone)
	if not m then
		return
	end
	m:PivotTo(self.plan.BushCF)
	if self.plan.CoverScale ~= 1 then
		m:ScaleTo(self.plan.CoverScale)
	end
	self.bush, self.bushRig = m, rig
	Debris:AddItem(m, 90)
end

-- Зверь: клон, мутация, поворот, масштаб WorldScale
function Scene.ensureAnimal(self: any)
	if self.dead or self.model then
		return
	end
	local m, rig = Lib.animal(self.sp)
	if not m then
		return
	end
	if self.a.mut then
		local ok, err = pcall(function()
			require(RS:WaitForChild("Shared"):WaitForChild("Util")).applyMutation(m, self.a.mut)
		end)
		if not ok then
			warn("[Reveal87] mutation: " .. tostring(err))
		end
	end
	m:PivotTo(self.cf)
	if self.ws ~= 1 then
		m:ScaleTo(self.ws)
	end
	rig.rootScaleLoc = self.ws -- V87: смещение корня (выход из куста) по WorldScale, а не по ключу масштаба корня
	self.model, self.animalRig = m, rig
	Debris:AddItem(m, 90)
end

function Scene.ensureAll(self: any)
	self:ensureBush()
	self:ensureAnimal()
end

-- Свет эпик-интриги: для 5-6 редкости без своей лампы в данных куста
local LIGHT_KEYS = { 1, 0, 60, 0, 80, 2, 95, 3.75, 101, 10, 105, 0 }

local function makeLight(self: any, hex: string?)
	local holder = Instance.new("Part")
	holder.Name = "Bush87Light"
	holder.Transparency = 1
	holder.Size = Vector3.one * 0.1
	holder.Anchored = true
	holder.CanCollide = false
	holder.CanQuery = false
	holder.CanTouch = false
	holder.CastShadow = false
	holder.CFrame = self.plan.BushCF * CFrame.new(0, 2 * self.plan.CoverScale, 0)
	local l = Instance.new("PointLight")
	l.Color = if hex then Color3.fromHex(hex) else Color3.fromRGB(255, 210, 26)
	l.Range = 16 * self.plan.CoverScale
	l.Brightness = 0
	l.Shadows = false
	l.Parent = holder
	holder.Parent = self.parent
	self.light = l
	table.insert(self.folders, holder)
end

-- Текущий масштаб зверя: WorldScale, а во время Reveal ещё и ключ масштаба корня (появление «из нуля»);
-- Motor6D масштаб сегментов не применяет, поэтому весь зверь растёт через ScaleTo
function Scene.animalScale(self: any): (number, number)
	local rig = self.animalRig
	local k = 1
	if not self.idle and rig and rig.clip == "Reveal" then
		local c = rig.data.clips.Reveal
		local rc = c and c.root
		if rc and rc.scale and #rc.scale >= 5 then
			local sx = Lib.sample3(rc.scale, rig.frame)
			k = math.max(sx, 0.02)
		end
	end
	local s = self.ws * k
	local m = self.model
	-- V87: ScaleTo трогает все меши зверя, поэтому только при заметной разнице (3%) или на точном конце
	if m then
		local cur = m:GetScale()
		if math.abs(cur - s) > 0.03 * s or (k == 1 and math.abs(cur - s) > 1e-4) then
			m:ScaleTo(s)
		end
	end
	return s, self.ws
end

function Scene.bushScale(self: any): number
	return self.plan.CoverScale
end

-- Куст Open_Burst: куски разлетаются, масштаб сегментов Motor6D не умеет, поэтому гасим прозрачностью, потом убираем
local function fadeBurst(self: any)
	local br = self.bushRig
	if not br or br.clip ~= "Open_Burst" then
		return
	end
	local t = math.clamp((br.frame - 6) / 8, 0, 1)
	for _, list in br.parts do
		for _, p in list do
			p.Transparency = t
		end
	end
end

function Scene.startDriver(self: any)
	if self.conn then
		return
	end
	local bushSf = function()
		return self.plan.CoverScale
	end
	local animalSf = function()
		return self:animalScale()
	end
	self.conn = RunService.Heartbeat:Connect(function(dt)
		if self.dead then
			return
		end
		-- нечем жить: модель убрал таймер Debris или кто-то снаружи
		if (self.bush and not self.bush.Parent and not self.bushGone) or (self.revealStarted and self.model and not self.model.Parent) then
			self:destroy()
			return
		end
		local rate = if self.isFast and self.isFast() then SKIP_RATE else 1
		if self.bush and self.bush.Parent then
			stepRig(self.bushRig, dt, rate, bushSf)
			fadeBurst(self)
			local l = self.light
			if l then
				local br = self.bushRig
				l.Brightness = if br and br.clip == "Tease_Epic" then math.min(Lib.sample1(LIGHT_KEYS, br.frame), 12) else 0
			end
		end
		if self.model and self.model.Parent then
			stepRig(self.animalRig, dt, if self.idle then (self.idleRate or 1) else rate, animalSf)
			-- побег: зверь убегает прочь от игрока
			local fl = self.flee
			if fl then
				local p = fl.from + fl.dir * ((os.clock() - fl.t0) * 24)
				self.cf = CFrame.lookAt(p, p + fl.dir)
				self.model:PivotTo(self.cf)
			end
		end
	end)
end

-- Побег зверя после раскрытия (поимка не удалась): быстрый Idle и бег в сторону dir
function Scene.runAway(self: any, dir: Vector3)
	self.idleRate = 3
	self.flee = { from = self.cf.Position, dir = dir, t0 = os.clock() }
end

-- Поставить куст в мир (вызывать до Occlusion.begin: Reveal.luau так и делает)
function Scene.place(self: any)
	self:ensureBush()
	if self.dead or not self.bush then
		return
	end
	self.bush.Name = "RevealBush87"
	self.bush.Parent = self.parent
	self:startDriver()
end

local function waitUntil(self: any, cond: () -> boolean, timeout: number)
	local t0 = os.clock()
	while not self.dead and not cond() and os.clock() - t0 < timeout do
		RunService.RenderStepped:Wait()
	end
end

-- Интрига куста по редкости (2.5 / 3 / 3.5 с) с его эффектами. Блокирует до конца клипа.
function Scene.tease(self: any)
	if self.dead or not self.bushRig or not self.bush then
		return
	end
	if self.isFast and self.isFast() then
		return
	end
	local r = self.rarity
	local tier = if r <= 2 then "Common" elseif r <= 4 then "Rare" else "Epic"
	local clip = "Tease_" .. tier
	local bd = Lib.bushData(self.zone)
	local prefix = string.format("Bush_%02d_FX_", self.zone)
	local keep, hasLight = {}, false
	for _, f in (bd and bd.fx) or {} do
		local g = f[2]
		-- группы кусты называются Bush_NN_FX_Common / Rare / Epic и Epic5 / Epic6 (цвет света по редкости)
		if g == prefix .. tier or (r >= 5 and g == prefix .. "Epic" .. tostring(r)) then
			table.insert(keep, f)
			if f[8] == "light" then
				hasLight = true
			end
		end
	end
	local teaseFolder: Folder? = nil
	if #keep > 0 then
		teaseFolder = Lib.playFx(keep, self.plan.BushCF, { parent = self.parent, lib = Lib.fxLib(string.format("fx_bush_%02d", self.zone)), scale = self.plan.CoverScale, max = 240 })
		table.insert(self.folders, teaseFolder)
	end
	if r >= 5 and not hasLight then
		makeLight(self, bd and bd.epicGlow and bd.epicGlow[r])
	end
	local done = false
	playRig(self.bushRig, clip, false, function()
		done = true
	end, function()
		return self.plan.CoverScale
	end)
	waitUntil(self, function()
		return done
	end, self.bushRig:length(clip) / FPS + 2)
	-- «Пропустить» посреди интриги: недоигранные эффекты убираем
	if teaseFolder and teaseFolder.Parent and self.isFast and self.isFast() then
		teaseFolder:Destroy()
	end
end

-- Куст раскрывается (Open_Burst / Open_Part), зверь играет Reveal со своими эффектами и уходит в Idle.
-- Блокирует до конца Reveal; зверь дальше крутит Idle, пока не вызван destroy.
function Scene.reveal(self: any)
	self:ensureAnimal()
	if self.dead or not self.model then
		return nil
	end
	local ad = Lib.animalData(self.sp)
	self.model.Parent = self.parent
	self.revealStarted = true
	self:startDriver()
	if self.bushRig then
		local open = (ad and ad.open) or "Open_Part"
		playRig(self.bushRig, open, false, function()
			-- куски Open_Burst уже невидимы: куст не нужен, Open_Part остаётся раскрытым до конца сцены
			if open == "Open_Burst" and not self.dead and self.bush then
				self.bushGone = true
				self.bush:Destroy()
			end
		end, function()
			return self.plan.CoverScale
		end)
	end
	if ad and ad.fx and #ad.fx > 0 then
		local folder = Lib.playFx(ad.fx, self.cf, { parent = self.parent, group = "AN_" .. self.sp .. "_FX", lib = Lib.fxLib("fx_" .. self.sp), scale = self.ws, max = 240 })
		table.insert(self.folders, folder)
	end
	local done = false
	playRig(self.animalRig, "Reveal", false, function()
		done = true
		if not self.dead then
			self.idle = true
			playRig(self.animalRig, "Idle", true, nil, function()
				return self:animalScale()
			end)
		end
	end, function()
		return self:animalScale()
	end)
	waitUntil(self, function()
		return done
	end, self.animalRig:length("Reveal") / FPS + 2)
	if self.dead then
		return nil
	end
	self.revealed = true
	return self
end

-- Убрать всё: куст, зверя, эффекты, свет; клипы больше не шагают
function Scene.destroy(self: any)
	if self.dead then
		return
	end
	self.dead = true
	self.alive = false
	if self.conn then
		self.conn:Disconnect()
		self.conn = nil
	end
	for _, f in self.folders do
		if f.Parent then
			f:Destroy()
		end
	end
	table.clear(self.folders)
	if self.bushRig then
		self.bushRig:destroy()
	end
	if self.animalRig then
		self.animalRig:destroy()
	end
	if self.bush then
		self.bush:Destroy()
	end
	if self.model then
		self.model:Destroy()
	end
end

return Reveal87
