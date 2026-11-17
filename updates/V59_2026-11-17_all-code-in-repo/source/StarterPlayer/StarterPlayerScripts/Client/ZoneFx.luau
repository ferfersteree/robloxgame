-- StarterPlayerScripts/Client/ZoneFx.luau
-- Camera-local lighting across all biomes, with a smooth 1.4 second transition.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")

local Config = require(RS.Shared.Config)

local ZoneFx = {}
ZoneFx.zone = -1
ZoneFx.Changed = Instance.new("BindableEvent")

local camera = workspace.CurrentCamera
local atmo = Lighting:FindFirstChildOfClass("Atmosphere")
local color = Lighting:FindFirstChild("Color") :: ColorCorrectionEffect?
local bloom = Lighting:FindFirstChildOfClass("BloomEffect")
local AMBUSH_Z = Config.FOREST_ORIGIN_Z or -3

-- Native beam attachments may be imported separately from their references.
local auroras: { { beam: Beam, zone: number } } = {}
local map = workspace:WaitForChild("Map")
task.spawn(function()
	local forest = map:WaitForChild("Forest", 10)
	if not forest then return end
	for _, item in forest:GetDescendants() do
		if not item:IsA("Beam") then continue end
		local holder = item.Parent
		local a0 = holder and holder:FindFirstChild("A0")
		local a1 = holder and holder:FindFirstChild("A1")
		if a0 and a0:IsA("Attachment") and a1 and a1:IsA("Attachment") then
			item.Attachment0 = a0
			item.Attachment1 = a1
		end
		local ancestor: Instance? = holder
		local zone: number? = nil
		local isAurora = false
		while ancestor and ancestor ~= forest do
			isAurora = isAurora or string.find(string.lower(ancestor.Name), "aurora", 1, true) ~= nil
			local id = ancestor:GetAttribute("Zone") or ancestor:GetAttribute("BiomeId")
			if typeof(id) == "number" and Config.ZONES[id] then zone = id end
			ancestor = ancestor.Parent
		end
		if isAurora and item.Attachment0 then
			zone = zone or Config.zoneFor(AMBUSH_Z - item.Attachment0.WorldPosition.Z)
			item.Enabled = ZoneFx.zone == zone
			table.insert(auroras, { beam = item, zone = zone })
		end
	end
end)

type Snap = { [string]: any }
local function snapshot(): Snap
	return {
		ClockTime = Lighting.ClockTime,
		Brightness = Lighting.Brightness,
		Ambient = Lighting.Ambient,
		OutdoorAmbient = Lighting.OutdoorAmbient,
		FogColor = Lighting.FogColor,
		Density = atmo and atmo.Density or 0,
		Haze = atmo and atmo.Haze or 0,
		AtmoColor = atmo and atmo.Color or Color3.new(1, 1, 1),
		Decay = atmo and atmo.Decay or Color3.new(1, 1, 1),
		Tint = color and color.TintColor or Color3.new(1, 1, 1),
		Saturation = color and color.Saturation or 0,
		Contrast = color and color.Contrast or 0,
		Bloom = bloom and bloom.Intensity or 0,
	}
end

local from: Snap = snapshot()
local to: any = nil
local k = 1
local DUR = 1.4

local function lerpN(a: number, b: number, t: number): number
	return a + (b - a) * t
end

local function apply(t: number)
	if not to then
		return
	end
	local e = t * t * (3 - 2 * t)
	-- время суток по кратчайшей дуге (вечер → полночь вперёд, а не через полдень)
	local d = ((to.ClockTime - from.ClockTime + 12) % 24) - 12
	Lighting.ClockTime = (from.ClockTime + d * e) % 24
	Lighting.Brightness = lerpN(from.Brightness, to.Brightness, e)
	Lighting.Ambient = from.Ambient:Lerp(to.Ambient, e)
	Lighting.OutdoorAmbient = from.OutdoorAmbient:Lerp(to.OutdoorAmbient, e)
	Lighting.FogColor = from.FogColor:Lerp(to.FogColor or to.AtmoColor, e)
	if atmo then
		atmo.Density = lerpN(from.Density, to.Density, e)
		atmo.Haze = lerpN(from.Haze, to.Haze, e)
		atmo.Color = from.AtmoColor:Lerp(to.AtmoColor, e)
		atmo.Decay = from.Decay:Lerp(to.Decay, e)
	end
	if color then
		color.TintColor = from.Tint:Lerp(to.Tint, e)
		color.Saturation = lerpN(from.Saturation, to.Saturation, e)
		color.Contrast = lerpN(from.Contrast, to.Contrast, e)
	end
	if bloom then
		bloom.Intensity = lerpN(from.Bloom, to.Bloom, e)
	end
end

function ZoneFx.set(z: number, instant: boolean?)
	if z ~= 0 and not Config.ZONES[z] then z = 0 end
	if z == ZoneFx.zone then
		return
	end
	ZoneFx.zone = z
	local look = z == 0 and Config.VILLAGE_LOOK or Config.ZONES[z].look
	from = snapshot()
	to = look
	k = instant and 1 or 0
	apply(k)
	for _, entry in auroras do
		entry.beam.Enabled = z == entry.zone
	end
	ZoneFx.Changed:Fire(z)
end

-- Зона по положению: лес — к −Z от линии засад
function ZoneFx.zoneAt(p: Vector3): number
	if p.Z > AMBUSH_Z - 4 or math.abs(p.X) > 170 then
		return 0
	end
	return Config.zoneFor(AMBUSH_Z - p.Z)
end

local acc = 0
RunService.RenderStepped:Connect(function(dt)
	if k < 1 then
		k = math.min(1, k + dt / DUR)
		apply(k)
	end
	acc += dt
	if acc > 0.2 then
		acc = 0
		ZoneFx.set(ZoneFx.zoneAt(camera.CFrame.Position))
	end
end)

ZoneFx.set(0, true)

return ZoneFx
