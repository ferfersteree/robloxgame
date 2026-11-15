--!nonstrict
-- StarterPlayerScripts/Client/EggOpen3D (V35)
-- The 3D egg opening of the Claude Design prototype, played with the real pack models in a private stage that exists only on
-- this client (nothing is replicated, nothing is uploaded). Timeline (seconds from the start, numbers are the prototype's):
--   prep    the egg wakes up: rocking grows, glow and sparks, ambience of the family (EggEffects of the pack)
--   open    the lid (UpperShell) cracks open and is thrown off, flash, burst of the family, shockwave ring
--   emerge  at prep + open*emerge the animal pops out: its real hatch curve (height, spin, scale) + limb animation (PetAnim)
--   clear   the empty shell sinks and fades
--   land    the animal lands: rings and sparks, as many as its rarity
--   reveal  the card (built by the caller), the animal idles, a tap makes it react
-- Higher rarities add: tension tremor before the opening, slow motion at the jump, light shafts, a halo, a camera swing,
-- a full orbit for the top rarity. The animal was already rolled by the server; this only shows the result.
-- If anything goes wrong before the reveal, ctx.onFail() is called and the caller falls back to the plain 2D hatch.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")
local StarterGui = game:GetService("StarterGui")
local RS = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local Mods = RS:WaitForChild("PetModules")
local PetAnimations = require(Mods:WaitForChild("PetAnimations"))
local PetAnimator = require(Mods:WaitForChild("PetAnimator"))
local EggPlayer = require(Mods:WaitForChild("EggPlayer"))
local EggOpenings = require(Mods:WaitForChild("EggOpenings"))

local EggOpen3D = {}

local PI, TAU = math.pi, math.pi * 2
local sin, cos, max, min, clamp = math.sin, math.cos, math.max, math.min, math.clamp

local STAGE = Vector3.new(0, 2600, 0)

local TEX = {
	glow = "rbxasset://textures/particles/explosion01_implosion_main.dds",
	star = "rbxasset://textures/particles/sparkles_main.dds",
	ring = "rbxasset://textures/particles/explosion01_shockwave_main.dds",
	spark = "rbxasset://textures/particles/fire_sparks_main.dds",
}

-- per egg family: prep, open, emerge (fractions are the prototype's), burst colours, how the pieces move
local FAMILY = {
	forest = { prep = 2.5, open = 1.5, emerge = 0.55, a = Color3.fromRGB(142, 217, 70), b = Color3.fromRGB(246, 232, 130), c = Color3.fromRGB(70, 150, 60), grav = -9, tex = "star", up = 14 },
	amber = { prep = 2.7, open = 1.7, emerge = 0.6, a = Color3.fromRGB(255, 167, 54), b = Color3.fromRGB(255, 226, 140), c = Color3.fromRGB(205, 100, 30), grav = -12, tex = "spark", up = 16 },
	tide = { prep = 2.7, open = 1.6, emerge = 0.6, a = Color3.fromRGB(83, 215, 218), b = Color3.fromRGB(224, 249, 244), c = Color3.fromRGB(65, 147, 192), grav = 3, tex = "glow", up = 9 },
	storm = { prep = 2.8, open = 1.6, emerge = 0.6, a = Color3.fromRGB(113, 202, 255), b = Color3.fromRGB(235, 248, 255), c = Color3.fromRGB(110, 120, 235), grav = -6, tex = "spark", up = 18 },
	astral = { prep = 3.0, open = 1.8, emerge = 0.62, a = Color3.fromRGB(143, 111, 235), b = Color3.fromRGB(245, 215, 120), c = Color3.fromRGB(230, 233, 255), grav = 0, tex = "star", up = 11 },
}

local REVEAL_DELAY = { 0.35, 0.45, 0.6, 0.8, 1.0, 1.3, 1.7 }
local RINGS = { 1, 1, 2, 2, 3, 3, 4 }
local SPARKS = { 6, 10, 16, 24, 36, 48, 70 }
local SHAFTS = { 0, 0, 2, 4, 6, 8, 12 }
local DIM = { 0, 0, 0.1, 0.2, 0.32, 0.42, 0.52 }

local function ss(a: number, b: number, x: number): number
	local t = clamp((x - a) / (b - a), 0, 1)
	return t * t * (3 - 2 * t)
end
local function lerp(a: number, b: number, t: number): number
	return a + (b - a) * t
end
local function outBack(t: number): number
	t = clamp(t, 0, 1)
	local c = 1.70158
	return 1 + (c + 1) * (t - 1) ^ 3 + c * (t - 1) ^ 2
end
local function bump(u: number, a: number, b: number): number
	if u <= a or u >= b then
		return 0
	end
	return sin(PI * (u - a) / (b - a))
end

-- ids of the game (pack of the first delivery) -> ids of the Claude Design export
local DESIGN_ID = { hazelnut_squirrel = "hazel_squirrel", heavenly_kitsune = "sky_kitsune" }
local function designId(id: string): string
	return DESIGN_ID[id] or id
end

local function packModel(id: string): Model?
	local folder = RS:FindFirstChild("PetModelsDesign")
	local src = folder and folder:FindFirstChild(id)
	if not (src and src:IsA("Model")) then
		return nil
	end
	local m = src:Clone()
	for _, d in m:GetDescendants() do
		if d:IsA("LuaSourceContainer") or d:IsA("Humanoid") then
			d:Destroy()
		end
	end
	return m
end

-- family: forest/amber/tide/storm/astral, petModel: id of the animal in the game
function EggOpen3D.available(family: string?, petModel: string?): boolean
	local folder = RS:FindFirstChild("PetModelsDesign")
	local mods = RS:FindFirstChild("PetModules")
	return folder ~= nil and mods ~= nil and family ~= nil and petModel ~= nil and folder:FindFirstChild("egg_" .. family) ~= nil and folder:FindFirstChild(designId(petModel)) ~= nil
end

local function setFade(model: Instance, v: number)
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") then
			p.LocalTransparencyModifier = v
		end
	end
end

local function part(parent: Instance, name: string, size: Vector3, color: Color3, mat: Enum.Material, tr: number?): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Material = mat
	p.Transparency = tr or 0
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function seqColor(a: Color3, b: Color3): ColorSequence
	return ColorSequence.new(a, b)
end

---------------------------------------------------------------------
-- play
---------------------------------------------------------------------
-- ctx: eggModel, petModel (ids in ReplicatedStorage/PetModels), family, rank (1..7), color (rarity colour), low,
--      buildReveal(sg, finish) -> builds the card, onDone(), onFail(), sfx(name, pitch, vol)
function EggOpen3D.play(ctx: any)
	local player = Players.LocalPlayer
	local cam = workspace.CurrentCamera
	local fam = FAMILY[ctx.family] or FAMILY.forest
	local rar = clamp((ctx.rank or 1) - 1, 0, 6) -- prototype rarity 0..6
	local low = ctx.low == true
	local sfx = ctx.sfx or function() end

	local petId = designId(ctx.petModel)
	local egg = packModel("egg_" .. tostring(ctx.family))
	local pet = packModel(petId)
	if not egg or not pet or not cam then
		if ctx.onFail then
			ctx.onFail()
		end
		return
	end

	-- state that must be restored
	local saved = {
		camType = cam.CameraType,
		camCF = cam.CFrame,
		fov = cam.FieldOfView,
		focus = cam.Focus,
		ambient = Lighting.Ambient,
		outdoor = Lighting.OutdoorAmbient,
		brightness = Lighting.Brightness,
		exposure = Lighting.ExposureCompensation,
		guis = {},
		core = {},
		fx = {},
		density = nil,
	}
	local folder = Instance.new("Folder")
	folder.Name = "EggOpen3D_Stage"
	local conn: RBXScriptConnection? = nil
	local sg: ScreenGui? = nil
	local ambience: any = nil
	local petAnim: any = nil
	local finished = false
	local revealed = false

	local function cleanup()
		if finished then
			return
		end
		finished = true
		pcall(function()
			RunService:UnbindFromRenderStep("EggOpen3D")
		end)
		if conn then
			conn:Disconnect()
		end
		if ambience then
			pcall(function()
				ambience:Destroy()
			end)
		end
		pcall(function()
			folder:Destroy()
		end)
		if sg then
			pcall(function()
				sg:Destroy()
			end)
		end
		for e, v in saved.fx do
			pcall(function()
				e.Enabled = v
			end)
		end
		pcall(function()
			local at = Lighting:FindFirstChildOfClass("Atmosphere")
			if at and saved.density then
				at.Density = saved.density
			end
		end)
		pcall(function()
			cam.CameraType = saved.camType
			cam.FieldOfView = saved.fov
			cam.CFrame = saved.camCF
			cam.Focus = saved.focus
			Lighting.Ambient = saved.ambient
			Lighting.OutdoorAmbient = saved.outdoor
			Lighting.Brightness = saved.brightness
			Lighting.ExposureCompensation = saved.exposure
		end)
		for g, v in saved.guis do
			pcall(function()
				g.Enabled = v
			end)
		end
		for t, v in saved.core do
			pcall(function()
				StarterGui:SetCoreGuiEnabled(t, v)
			end)
		end
	end

	local function fail(err: any)
		warn("[EggOpen3D] " .. tostring(err))
		cleanup()
		if revealed then
			if ctx.onDone then
				ctx.onDone()
			end
		elseif ctx.onFail then
			ctx.onFail()
		end
	end

	local ok, err = pcall(function()
		---------------------------------------------------------------
		-- sizes
		---------------------------------------------------------------
		local _, eggSize = egg:GetBoundingBox()
		local _, petSize = pet:GetBoundingBox()
		local H = eggSize.Y
		local S = max(petSize.X, petSize.Y, petSize.Z)
		local ws = H / 2.3 -- studs per prototype unit
		local d = PetAnimations[petId]
		local hd = d.hd
		local landAt = d.landAt or 0.78
		local fy = (d.fy or 0) * 1.5

		local EO = EggOpenings[ctx.family]
		local prep, open = EO.prep, EO.open
		local tE = EO.emergeTime()
		local tL = tE + hd * landAt
		local tP = tE + hd
		local tR = tP + REVEAL_DELAY[rar + 1]

		---------------------------------------------------------------
		-- the room: a closed dark room so the world and the sky never show
		---------------------------------------------------------------
		folder.Parent = workspace
		local dark = Color3.fromRGB(28, 14, 66)
		local R = 90
		for _, w in {
			{ Vector3.new(0, -3.5, 0), Vector3.new(R * 2, 3, R * 2) },
			{ Vector3.new(0, R, 0), Vector3.new(R * 2, 3, R * 2) },
			{ Vector3.new(R, R / 2, 0), Vector3.new(3, R + 6, R * 2) },
			{ Vector3.new(-R, R / 2, 0), Vector3.new(3, R + 6, R * 2) },
			{ Vector3.new(0, R / 2, R), Vector3.new(R * 2, R + 6, 3) },
			{ Vector3.new(0, R / 2, -R), Vector3.new(R * 2, R + 6, 3) },
		} do
			local p = part(folder, "Wall", w[2], dark, Enum.Material.SmoothPlastic)
			p.Position = STAGE + w[1]
		end
		-- floor: a lit disc and a thin glowing ring
		local disc = part(folder, "Disc", Vector3.new(0.6, 14 * ws / 2, 14 * ws / 2), Color3.fromRGB(84, 52, 170), Enum.Material.SmoothPlastic)
		disc.Shape = Enum.PartType.Cylinder
		disc.CFrame = CFrame.new(STAGE + Vector3.new(0, -0.3, 0)) * CFrame.Angles(0, 0, PI / 2)
		local rim = part(folder, "Rim", Vector3.new(0.2, 14 * ws / 2 + 0.6, 14 * ws / 2 + 0.6), fam.a, Enum.Material.Neon)
		rim.Shape = Enum.PartType.Cylinder
		rim.CFrame = CFrame.new(STAGE + Vector3.new(0, -0.45, 0)) * CFrame.Angles(0, 0, PI / 2)
		-- crystals around (decoration, the prototype's purple crystals); they fade out while they are in the way of the camera
		local crystals = {}
		local rng = Random.new(7)
		for i = 1, low and 6 or 12 do
			local a = i / 12 * TAU + rng:NextNumber() * 0.4
			local r0 = (10 + rng:NextNumber() * 14) * ws / 2
			local h = (3 + rng:NextNumber() * 6) * ws / 2
			local c = part(folder, "Crystal", Vector3.new(h * 0.22, h, h * 0.22), Color3.fromRGB(226, 160, 255):Lerp(fam.a, 0.25), Enum.Material.Glass, 0.15)
			c.CFrame = CFrame.new(STAGE + Vector3.new(sin(a) * r0, h * 0.5, cos(a) * r0)) * CFrame.Angles(rng:NextNumber() * 0.25, a, rng:NextNumber() * 0.25)
			table.insert(crystals, { p = c, base = 0.15, fade = 0 })
		end
		-- lights
		local keyP = part(folder, "KeyLight", Vector3.new(1, 1, 1), Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, 1)
		keyP.Position = STAGE + Vector3.new(0, H * 3.2, -H * 1.2)
		local key = Instance.new("PointLight")
		key.Color = Color3.fromRGB(235, 220, 255)
		key.Brightness = 2.4
		key.Range = 60
		key.Parent = keyP
		local rimP = part(folder, "RimLight", Vector3.new(1, 1, 1), fam.a, Enum.Material.SmoothPlastic, 1)
		rimP.Position = STAGE + Vector3.new(H * 1.6, H * 1.2, H * 1.4)
		local rimL = Instance.new("PointLight")
		rimL.Color = fam.a
		rimL.Brightness = 1.4
		rimL.Range = 40
		rimL.Parent = rimP
		local coreP = part(folder, "CoreLight", Vector3.new(1, 1, 1), fam.b, Enum.Material.SmoothPlastic, 1)
		coreP.Position = STAGE + Vector3.new(0, H * 0.5, 0)
		local core = Instance.new("PointLight")
		core.Color = fam.b
		core.Brightness = 0
		core.Range = 26
		core.Parent = coreP

		-- the game's post effects (blur of the open window, bloom, colour grading, sun rays) wash out the stage: off until the end
		for _, e in Lighting:GetChildren() do
			if e:IsA("PostEffect") or e:IsA("SunRaysEffect") then
				if e.Enabled then
					saved.fx[e] = true
					e.Enabled = false
				end
			elseif e:IsA("Atmosphere") then
				saved.density = e.Density
				e.Density = 0
			end
		end
		-- no shadows from ~1000 small parts (the main cost of the scene)
		for _, m in { egg, pet } do
			for _, d in m:GetDescendants() do
				if d:IsA("BasePart") then
					d.CastShadow = false
				end
			end
		end
		-- local lighting: only this client sees it, restored in cleanup
		Lighting.Ambient = Color3.fromRGB(96, 78, 150)
		Lighting.OutdoorAmbient = Color3.fromRGB(96, 78, 150)

		---------------------------------------------------------------
		-- the egg and the animal
		---------------------------------------------------------------
		local home = CFrame.new(STAGE + Vector3.new(0, 0.05, 0))
		egg.Parent = folder
		egg:PivotTo(home)
		pet:PivotTo(home) -- parented only at the emerge moment
		local eggDriver: any = nil -- created below, after the particles exist
		local streams = {}
		petAnim = PetAnimator.new(pet, petId)
		petAnim.Orbit = false

		---------------------------------------------------------------
		-- particles
		---------------------------------------------------------------
		local fxP = part(folder, "Fx", Vector3.new(1, 1, 1), Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, 1)
		fxP.Position = STAGE + Vector3.new(0, H * 0.5, 0)
		local fxAtt = Instance.new("Attachment")
		fxAtt.Parent = fxP
		local function emitter(tex: string, c0: Color3, c1: Color3, size: number, life: number, speed: number, accelY: number, spread: number, rotSpd: number): ParticleEmitter
			local e = Instance.new("ParticleEmitter")
			e.Texture = TEX[tex] or TEX.star
			e.Color = seqColor(c0, c1)
			e.LightEmission = 0.8
			e.LightInfluence = 0
			e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, size), NumberSequenceKeypoint.new(1, 0) })
			e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.7, 0.2), NumberSequenceKeypoint.new(1, 1) })
			e.Lifetime = NumberRange.new(life * 0.7, life)
			e.Speed = NumberRange.new(speed * 0.5, speed)
			e.Acceleration = Vector3.new(0, accelY, 0)
			e.SpreadAngle = Vector2.new(spread, spread)
			e.Rotation = NumberRange.new(0, 360)
			e.RotSpeed = NumberRange.new(-rotSpd, rotSpd)
			e.Drag = 1
			e.Rate = 0
			e.Enabled = false
			e.Parent = fxAtt
			return e
		end
		local burstA = emitter(fam.tex, fam.a, fam.c, 0.9 * ws, 1.8, fam.up * ws / 2, fam.grav * ws / 2, 180, 220)
		local burstB = emitter("star", fam.b, Color3.new(1, 1, 1), 0.7 * ws, 1.5, 12 * ws / 2, -4 * ws / 2, 180, 120)
		local sparkIn = emitter("star", fam.b, fam.a, 0.35 * ws, 1.1, 1.5 * ws, 3, 180, 60)
		sparkIn.Speed = NumberRange.new(0.5, 1.5)
		local landFx = emitter("star", Color3.new(1, 1, 1), fam.a, 0.5 * ws, 1.4, 8 * ws / 2, -6, 80, 120)
		local ambient = emitter("star", fam.b, fam.a, 0.3 * ws, 2.2, 1.2, 0.8, 180, 40)
		local nSpark = low and 0.5 or 1

		-- rings: flat neon discs expanding on the floor
		local rings = {}
		for i = 1, 4 do
			local r = part(folder, "Ring", Vector3.new(0.12, 1, 1), Color3.new(1, 1, 1), Enum.Material.Neon, 1)
			r.Shape = Enum.PartType.Cylinder
			rings[i] = { p = r, t = -1, dur = 1, r0 = 1, r1 = 4 }
		end
		local ringIdx = 0
		local function ring(color: Color3, r0: number, r1: number, dur: number)
			ringIdx = ringIdx % #rings + 1
			local q = rings[ringIdx]
			q.t, q.dur, q.r0, q.r1 = 0, dur, r0 * ws, r1 * ws
			q.p.Color = color
		end

		-- light shafts for the higher rarities
		local shafts = {}
		for i = 1, SHAFTS[rar + 1] do
			if low and i > 4 then
				break
			end
			local s = part(folder, "Shaft", Vector3.new(0.5 * ws, 5.2 * ws, 0.5 * ws), Color3.fromRGB(255, 246, 216), Enum.Material.Neon, 1)
			shafts[i] = s
		end
		-- halo (mythic and above)
		local halo = part(folder, "Halo", Vector3.new(0.12, 1, 1), Color3.fromRGB(255, 243, 196), Enum.Material.Neon, 1)
		halo.Shape = Enum.PartType.Cylinder

		---------------------------------------------------------------
		-- gui: hide everything else, own screen gui
		---------------------------------------------------------------
		local pg = player:WaitForChild("PlayerGui")
		for _, g in pg:GetChildren() do
			if g:IsA("ScreenGui") and g.Enabled then
				saved.guis[g] = true
				g.Enabled = false
			end
		end
		for _, t in { Enum.CoreGuiType.Backpack, Enum.CoreGuiType.Chat, Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Health, Enum.CoreGuiType.EmotesMenu } do
			local okC, v = pcall(function()
				return StarterGui:GetCoreGuiEnabled(t)
			end)
			if okC and v then
				saved.core[t] = true
				pcall(function()
					StarterGui:SetCoreGuiEnabled(t, false)
				end)
			end
		end
		sg = Instance.new("ScreenGui")
		sg.Name = "EggOpen3D"
		sg.DisplayOrder = 60
		sg.ResetOnSpawn = false
		sg.IgnoreGuiInset = true
		sg.Parent = pg
		local flash = Instance.new("Frame")
		flash.BackgroundColor3 = Color3.new(1, 1, 1)
		flash.BackgroundTransparency = 1
		flash.BorderSizePixel = 0
		flash.Size = UDim2.fromScale(1, 1)
		flash.ZIndex = 50
		flash.Active = false
		flash.Parent = sg
		local vignette = Instance.new("Frame")
		vignette.BackgroundColor3 = Color3.new(0, 0, 0)
		vignette.BackgroundTransparency = 1
		vignette.BorderSizePixel = 0
		vignette.Size = UDim2.fromScale(1, 1)
		vignette.ZIndex = 1
		vignette.Active = false
		vignette.Parent = sg
		local hit = Instance.new("TextButton")
		hit.Text = ""
		hit.AutoButtonColor = false
		hit.BackgroundTransparency = 1
		hit.Size = UDim2.fromScale(1, 1)
		hit.ZIndex = 2
		hit.Parent = sg
		local fast = false
		local skip = Instance.new("TextButton")
		skip.Text = "SKIP"
		skip.Font = Enum.Font.GothamBlack
		skip.TextSize = 18
		skip.TextColor3 = Color3.new(1, 1, 1)
		skip.BackgroundColor3 = Color3.fromRGB(10, 20, 70)
		skip.BackgroundTransparency = 0.25
		skip.AnchorPoint = Vector2.new(1, 0)
		skip.Position = UDim2.new(1, -16, 0, 16)
		skip.Size = UDim2.fromOffset(86, 38)
		skip.ZIndex = 40
		skip.Parent = sg
		Instance.new("UICorner", skip).CornerRadius = UDim.new(0, 10)
		skip.MouseButton1Click:Connect(function()
			fast = true
			skip.Visible = false
		end)

		local function finish()
			if finished then
				return
			end
			cleanup()
			if ctx.onDone then
				ctx.onDone()
			end
		end

		---------------------------------------------------------------
		-- the egg of the export: events of EggOpenings -> particles, rings, flashes
		---------------------------------------------------------------
		local shake = 0
		local emerged = false
		local function onEvent(e: any)
			local ty = e.type
			fxAtt.WorldPosition = STAGE + Vector3.new(0, H * 0.55, 0)
			if ty == "burst" then
				burstA.Color = seqColor(e.color, e.color2 or fam.c)
				burstA:Emit(max(1, math.floor((e.count or 8) * nSpark)))
			elseif ty == "ring" then
				ring(e.color or Color3.new(1, 1, 1), e.r0 or 0.6, e.r1 or 3, e.life or 0.9)
			elseif ty == "flash" then
				flash.BackgroundColor3 = e.color or Color3.new(1, 1, 1)
				flash.BackgroundTransparency = 0.5
				TweenService:Create(flash, TweenInfo.new(e.life or 0.7), { BackgroundTransparency = 1 }):Play()
				shake = max(shake, 0.25)
			elseif ty == "bolt" then
				burstB.Color = seqColor(e.color or Color3.new(1, 1, 1), Color3.new(1, 1, 1))
				burstB:Emit(max(1, math.floor((e.count or 4) * nSpark)))
				shake = max(shake, 0.12)
			elseif ty == "stream" then
				table.insert(streams, { from = e.t, to = e.untilT or (e.t + 2), rate = e.count or 10, color = e.color or Color3.new(1, 1, 1), acc = 0 })
			end
		end
		eggDriver = EggPlayer.play(egg, ctx.family, {
			manual = true,
			hd = hd,
			onEvent = onEvent,
			onEmerge = function()
				if not emerged then
					emerged = true
					pet.Parent = folder
					petAnim:Hatch()
					petAnim:Update(0)
				end
			end,
		})

		---------------------------------------------------------------
		-- the frame loop
		---------------------------------------------------------------
		cam.CameraType = Enum.CameraType.Scriptable
		cam.FieldOfView = 48
		local ot = 0
		local ev = {}
		local ts = 1
		local view = { x = 0, y = H * 0.5, dist = H * 3.0, yaw = 0, pitch = 0.12 }
		local glow = { x = 0, y = H * 0.5, dist = H * 3.0, yaw = 0, pitch = 0.12 }
		local lastTick = 0
		local petBase = pet
		local petCy = max(0.4, petSize.Y * 0.5)
		local usr = { yaw = 0 }
		local rarityDelay = REVEAL_DELAY[rar + 1]

		local function onStep(dt: number)
			if finished then
				return
			end
			dt = min(dt, 0.05)
			if cam.CameraType ~= Enum.CameraType.Scriptable then
				cam.CameraType = Enum.CameraType.Scriptable
			end
			if fast and not revealed then
				dt *= 3
			end
			-- slow motion at the jump of high rarities (prototype)
			local u = petAnim.hu
			ts = 1
			if rar >= 4 and u > 0.5 and u < 0.68 then
				ts = lerp(1, ({ 1, 1, 1, 1, 0.55, 0.45, 0.35 })[rar + 1], bump(u, 0.5, 0.68))
			end
			dt *= ts
			ot += dt
			local t = ot

			-- egg appears (fade in), then the egg of the Claude Design export runs its own opening (EggPlayer)
			if t < 0.6 then
				setFade(egg, 1 - ss(0, 0.45, t))
			elseif not ev.shown then
				ev.shown = true
				setFade(egg, 0)
			end
			if eggDriver then
				eggDriver.step(dt)
			end
			-- streams of sparks of the opening (events of type "stream")
			for _, sdef in streams do
				if t >= sdef.from and t <= sdef.to then
					sdef.acc += dt * sdef.rate * nSpark
					while sdef.acc >= 1 do
						sdef.acc -= 1
						local a = math.random() * TAU
						fxAtt.WorldPosition = STAGE + Vector3.new(sin(a) * H * 0.55, H * (0.1 + math.random() * 0.8), cos(a) * H * 0.55)
						sparkIn.Color = seqColor(sdef.color, fam.a)
						sparkIn:Emit(1)
					end
				end
			end
			if t < prep and t - lastTick > 0.34 - 0.24 * clamp(t / prep, 0, 1) then
				lastTick = t
				sfx("tick", 0.8 + clamp(t / prep, 0, 1) * 0.9, 0.5)
			end
			if t >= prep and not ev.open then
				ev.open = true
				shake = 0.5 + 0.12 * rar
				sfx(rar >= 5 and "thunder" or (rar >= 3 and "boom" or "pop"), 1, 0.9)
				sfx("sparkle", 1 + rar * 0.04, 0.8)
				if rar >= 4 then
					sfx("level", 1, 0.7)
				end
			end
			local tC = tE
			core.Brightness = 0
			-- land
			if t >= tL and not ev.land then
				ev.land = true
				for i = 1, RINGS[rar + 1] do
					ring(i % 2 == 0 and fam.a or Color3.new(1, 1, 1), 0.3, 1.6 + (i - 1) * 0.55 + rar * 0.12, 0.7 + i * 0.22)
				end
				fxAtt.WorldPosition = STAGE + Vector3.new(0, 0.3, 0)
				landFx:Emit(math.floor(SPARKS[rar + 1] * nSpark))
				shake = max(shake, 0.18 + 0.04 * rar)
			end
			if rar >= 4 and t > tE and t < tR + 2 and math.random() < dt * (4 + rar * 3) * 0.5 * nSpark then
				local a = math.random() * TAU
				local rr = (0.6 + math.random() * 1.2) * ws
				fxAtt.WorldPosition = STAGE + Vector3.new(sin(a) * rr, 0.2, cos(a) * rr)
				ambient:Emit(1)
			end
			if rar == 6 and not ev.pulse and t >= tE + hd * 0.45 then
				ev.pulse = true
				flash.BackgroundTransparency = 0.55
				TweenService:Create(flash, TweenInfo.new(0.9), { BackgroundTransparency = 1 }):Play()
			end

			-- the animal (PetAnimator of the export moves the root and scales the model itself)
			if emerged then
				ev.emerge = true
				petAnim:Update(dt)
			end

			-- reveal
			if t >= tR and not revealed then
				revealed = true
				skip.Visible = false
				sfx("sparkle", 1.2, 0.6)
				if ctx.buildReveal then
					local okR, eR = pcall(ctx.buildReveal, sg, finish)
					if not okR then
						warn("[EggOpen3D] reveal: " .. tostring(eR))
					end
				end
			end

			-- rings
			for _, q in rings do
				if q.t >= 0 then
					q.t += dt
					local k = q.t / q.dur
					if k >= 1 then
						q.t = -1
						q.p.Transparency = 1
					else
						local rr = lerp(q.r0, q.r1, 1 - (1 - k) ^ 2)
						q.p.Size = Vector3.new(0.12, rr * 2, rr * 2)
						q.p.CFrame = CFrame.new(STAGE + Vector3.new(0, 0.08, 0)) * CFrame.Angles(0, 0, PI / 2)
						q.p.Transparency = 0.25 + 0.75 * k
					end
				end
			end

			-- ceremony light: shafts and halo
			local cer = ss(tE + hd * 0.3, tE + hd * 0.62, t)
			local hold = 1 - 0.7 * ss(tR, tR + 2.5, t)
			for i, s in shafts do
				local n = #shafts
				local an = i / n * TAU + t * 0.12
				local rr = (0.5 + 0.35 * sin(i * 2.3)) * ws
				s.CFrame = CFrame.new(STAGE + Vector3.new(sin(an) * rr, s.Size.Y * 0.5, cos(an) * rr - 0.2 * ws)) * CFrame.Angles(0, an, sin(an) * 0.16)
				s.Transparency = 1 - clamp((0.1 + 0.05 * sin(t * 1.7 + i)) * cer * hold * (0.6 + rar * 0.08) * 1.6, 0, 0.5)
			end
			local hk = rar >= 5 and cer * (1 - 0.4 * ss(tR, tR + 3, t)) or 0
			if hk > 0 then
				local hs = max(0.9, S * 0.62) * (0.6 + 0.4 * outBack(cer))
				halo.Size = Vector3.new(0.12, hs * 2, hs * 2)
				halo.CFrame = CFrame.new(STAGE + Vector3.new(0, max(0.7, petCy + fy), 1.0 * ws)) * CFrame.Angles(0, PI / 2, 0) * CFrame.Angles(0, 0.3 * sin(t * 0.8), 0.25 * sin(t * 0.6))
				halo.Transparency = 1 - 0.6 * hk
			end
			local dim = DIM[rar + 1] * cer * (1 - 0.5 * ss(tR, tR + 3, t))
			key.Brightness = 2.4 * (1 - dim * 0.8)
			vignette.BackgroundTransparency = 1 - dim * 0.9

			-- camera (the prototype's path, in the mirrored frame: the front of the models is -Z)
			local s = ss(tE + hd * 0.35, tR, t)
			local asp = cam.ViewportSize.X / max(1, cam.ViewportSize.Y)
			local wide = max(1, 0.92 / asp)
			local eggDist = lerp(H * 3.4, H * 3.1, ss(0, prep + open, t)) * wide
			local petDist = clamp(S * 2.6, H * 1.7, H * 3.6) * wide * (1 + ({ 0.04, 0.06, 0.1, 0.16, 0.22, 0.28, 0.36 })[rar + 1] * (1 - ss(tP - 0.2, tR, t)))
			glow.dist = lerp(eggDist, petDist, s)
			glow.y = lerp(H * 0.5, max(S * 0.28, petCy * 0.95 + fy), s)
			glow.yaw = 0.07 * sin(t * 0.7) * (1 - s) - 0.5 * s * 0 + ({ 0, 0.12, 0.28, 0.5, 0.75, 1.05, 0 })[rar + 1] * sin(PI * s) - (rar == 6 and TAU * ss(tE + hd * 0.5, tR, t) or 0)
			glow.pitch = 0.12 - ({ 0, 0, 0.02, 0.05, 0.09, 0.12, 0.14 })[rar + 1] * sin(PI * s) + 0.02 * s
			local k = min(1, dt * 5.5)
			view.dist += (glow.dist - view.dist) * k
			view.y += (glow.y - view.y) * k
			view.yaw += (glow.yaw + usr.yaw - view.yaw) * k
			view.pitch += (glow.pitch - view.pitch) * k
			local cp = cos(view.pitch)
			local center = STAGE + Vector3.new(0, view.y, 0)
			local pos = center + Vector3.new(-sin(view.yaw) * cp * view.dist, sin(view.pitch) * view.dist, -cos(view.yaw) * cp * view.dist)
			shake = max(0, shake - dt * 1.6)
			local off = Vector3.new((math.random() - 0.5) * shake * 0.5, (math.random() - 0.5) * shake * 0.5, 0)
			-- decoration that stands between the camera and the subject (or around the camera) becomes invisible
			local ray = center - pos
			local len = ray.Magnitude
			local dir = ray / max(len, 0.001)
			for _, c in crystals do
				local cp = c.p.Position
				local rel = cp - pos
				local along = clamp(rel:Dot(dir), 0, len)
				local dist = (rel - dir * along).Magnitude
				local reach = c.p.Size.Y * 0.5 + 3
				local near = (cp - pos).Magnitude < reach + 6
				local want = (dist < reach or near) and 1 or 0
				c.fade += (want - c.fade) * min(1, dt * 8)
				c.p.Transparency = c.base + (1 - c.base) * c.fade
			end
			cam.CFrame = CFrame.lookAt(pos, center) * CFrame.new(off)
		end

		RunService:BindToRenderStep("EggOpen3D", Enum.RenderPriority.Camera.Value + 1, function(dt)
			local okF, eF = pcall(onStep, dt)
			if not okF then
				fail(eF)
			end
		end)

		-- tapping: before the reveal a tap on empty space does nothing; after it, a tap on the animal makes it react
		hit.Activated:Connect(function(input)
			if not revealed or finished then
				return
			end
			local pos2 = input and input.Position or UserInputService:GetMouseLocation()
			local ray = cam:ViewportPointToRay(pos2.X, pos2.Y)
			local c = petBase:GetPivot().Position + Vector3.new(0, petCy * pet:GetScale(), 0)
			local to = c - ray.Origin
			local proj = to:Dot(ray.Direction)
			if proj > 0 then
				local dist = (ray.Origin + ray.Direction * proj - c).Magnitude
				if dist < S * 0.7 * pet:GetScale() then
					petAnim:React()
					sfx("pop", 1.2, 0.6)
				end
			end
		end)
	end)
	if not ok then
		fail(err)
	end
end

return EggOpen3D
