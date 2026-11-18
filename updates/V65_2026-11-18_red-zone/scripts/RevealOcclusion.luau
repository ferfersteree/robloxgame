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

function Occlusion.refresh()
	if not active then return end
	local camera = workspace.CurrentCamera
	if not camera then return end
	local ignored: { Instance } = { Fx.folder }
	if player.Character then table.insert(ignored, player.Character) end
	-- Sample the whole presentation, not a single ray to the animal's feet.
	-- This also clears branches over a bush and obstructions beside its silhouette.
	local right = camera.CFrame.RightVector
	local width = math.clamp(height * 0.75, 2.2, 11)
	local top = math.max(5.5, height * 1.3 + 1)
	local targets = {}
	for _, y in { 0.35, top * 0.5, top } do
		for _, x in { -width, 0, width } do
			table.insert(targets, focus + right * x + Vector3.yAxis * y)
		end
	end
	for _, part in camera:GetPartsObscuringTarget(targets, ignored) do
		if part:IsA("BasePart") and part.Transparency < 1 then conceal(part) end
	end
	-- Imported decorative parts often have CanQuery=false and are omitted by the
	-- engine query. A small, once-per-scene candidate set covers those parts and
	-- also handles the camera starting inside a trunk, wall or shelter roof.
	local eye = camera.CFrame.Position
	for _, part in nearby do
		if part.Parent and part.Transparency < 1 and not protected(part) then
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

-- V65: камера переехала к зверю: дальше расчищаем вид на новую точку (без нового обхода всей карты)
function Occlusion.setFocus(position: Vector3, animalHeight: number)
	if not active then
		return
	end
	focus = position
	height = animalHeight
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

function Occlusion.begin(position: Vector3, animalHeight: number)
	Occlusion.finish()
	focus = position
	height = animalHeight
	elapsed = 0
	active = true
	if player.Character then watchCharacter(player.Character) end
	respawnConnection = player.CharacterAdded:Connect(watchCharacter)
	for _, object in workspace:GetDescendants() do rememberNearby(object) end
	worldConnection = workspace.DescendantAdded:Connect(rememberNearby)
	Occlusion.refresh()
	RunService:BindToRenderStep(renderName, Enum.RenderPriority.Camera.Value + 3, function(dt)
		-- Roblox's normal camera transparency controller runs earlier in the frame.
		-- Keep accessories and held tools hidden even on a very short throw.
		for _, part in characterParts do
			if part.Parent then part.LocalTransparencyModifier = 1 end
		end
		elapsed += dt
		if elapsed >= 0.08 then elapsed = 0; Occlusion.refresh() end
	end)
end

return Occlusion
