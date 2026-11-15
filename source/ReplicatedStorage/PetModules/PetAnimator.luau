--!nonstrict
-- PetAnimator: проигрывает анимации питомца так же, как Actor в прототипе
-- (смешивание покой/движение, реакция, появление, движение корня).
local RunService = game:GetService("RunService")
local PetAnimations = require(script.Parent.PetAnimations)

local PetAnimator = {}
PetAnimator.__index = PetAnimator

local function ss(a, b, x) x = math.clamp((x - a) / (b - a), 0, 1) return x * x * (3 - 2 * x) end

-- model: модель питомца из ReplicatedStorage.PetModels (клон), petId: например "moss_bunny"
function PetAnimator.new(model, petId)
	local entry = PetAnimations[petId]
	assert(entry, "Нет анимаций для " .. tostring(petId))
	local self = setmetatable({}, PetAnimator)
	self.model, self.entry = model, entry
	self.root = model.PrimaryPart
	self.base = self.root.CFrame
	self.baseScale = model:GetScale()
	self.motors = {}
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Motor6D") and string.sub(d.Name, -6) == "_Joint" then self.motors[string.sub(d.Name, 1, -7)] = d end
	end
	for _, j in ipairs(entry.joints) do
		if j ~= "root" then assert(self.motors[j], petId .. ": в модели нет сустава " .. j) end
	end
	self.t, self.mt, self.wm = 0, 0, 0
	self.mode = "idle"
	self.ru, self.hu = -1, -1
	self.ang, self.yaw = 0, 0
	self.Orbit = false      -- true: в режиме move питомец ходит по кругу, как в галерее прототипа
	self.ApplyScale = true  -- масштаб корня при появлении (Model:ScaleTo)
	self.scale = 1
	self._set = function(name, cf) local m = self.motors[name] if m then m.Transform = cf end end
	return self
end

function PetAnimator:SetBase(cf) self.base = cf end
function PetAnimator:SetMode(mode) self.mode = mode end            -- "idle" | "move"
function PetAnimator:React() if self.hu < 0 then self.ru = 0 end end -- короткая реакция на нажатие
function PetAnimator:Hatch()                                        -- появление из яйца
	self.hu, self.ru, self.wm, self.mode, self.ang, self.yaw = 0, -1, 0, "idle", 0, 0
end
function PetAnimator:IsHatching() return self.hu >= 0 end

function PetAnimator:Update(dt)
	local e, mv = self.entry, self.entry.mv or {}
	self.t += dt
	self.wm += ((self.mode == "move" and 1 or 0) - self.wm) * math.min(1, dt * 3.2)
	if self.wm < 0.002 then self.wm = 0 end
	self.mt += dt * (0.35 + 0.65 * self.wm)
	if self.ru >= 0 then self.ru += dt / e.rd if self.ru >= 1 then self.ru = -1 end end
	local hw = false
	if self.hu >= 0 then self.hu += dt / e.hd if self.hu >= 1 then self.hu = -1 else hw = true end end

	e.begin()
	local wi = (1 - self.wm) * (hw and ss(0.82, 1, self.hu) or 1)
	if wi > 0 then e.add("idle", self.t, wi) end
	if self.wm > 0 and not hw then e.add("move", self.mt, self.wm) end
	if self.ru >= 0 then local u = self.ru e.add("react", u, math.min(1, u / 0.1, (1 - u) / 0.16)) end
	if hw then e.add("hatch", self.hu, 1) end
	local rootCF, rootScale = e.flush(self._set, self.scale)

	if self.ApplyScale and math.abs(rootScale - self.scale) > 0.03 then
		self.scale = rootScale
		self.model:ScaleTo(self.baseScale * rootScale)
	end
	-- ходьба по кругу (радиус и скорость из прототипа; 1 ед. = 1.5 стада)
	local orbit = CFrame.new()
	if self.Orbit then
		local rad = mv.rad or 1.25
		local w = self.wm
		self.ang += dt * (mv.sp or 1) / math.max(0.3, rad) * w
		local tgt = (w > 0.25) and (self.ang + (mv.side and 0 or math.pi / 2)) or (math.round(self.yaw / (2 * math.pi)) * 2 * math.pi)
		local dy = tgt - self.yaw
		dy = math.atan2(math.sin(dy), math.cos(dy))
		self.yaw += dy * math.min(1, dt * (w > 0.25 and 6 or 3.5))
		orbit = CFrame.new(-math.sin(self.ang) * rad * w * 1.5, 0, -math.cos(self.ang) * rad * w * 1.5) * CFrame.Angles(0, self.yaw, 0)
	end
	self.root.CFrame = self.base * orbit * rootCF
end

function PetAnimator:Start()
	if self.conn then return self end
	self.conn = RunService.Heartbeat:Connect(function(dt) self:Update(math.min(dt, 0.05)) end)
	return self
end
function PetAnimator:Stop() if self.conn then self.conn:Disconnect() self.conn = nil end end
function PetAnimator:Destroy() self:Stop() end

return PetAnimator
