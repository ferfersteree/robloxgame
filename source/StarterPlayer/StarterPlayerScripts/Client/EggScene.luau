-- StarterPlayerScripts/Client/EggScene.luau
-- Egg opening cinematic (V31). 2D scene made of UI objects, nothing uploaded to Roblox.
--   intro   : the egg drops in with a bounce and a shockwave
--   charge  : the egg shakes harder and harder, glows in the colour of its rarity, cracks grow from an impact
--             point (tap the egg to crack it faster), sparks are pulled into it, ticks speed up
--   burst   : white flash, the shell breaks into real pieces that fly out with physics, rays, rings, confetti
--   reveal  : the animal pops out on a glowing stage with its rarity banner, bonuses and a CONTINUE button
-- The shell pieces and the cracks come from the egg sprite itself: at the start the sprite is cut into 13 pieces along
-- irregular lines (a warped Voronoi), and the crack overlay is drawn along those same lines, so the egg really
-- breaks where the cracks are. The egg only visualises the result: the animal was already rolled by the server.
-- If the sprite or EditableImage is not available the caller falls back to the simple 2D hatch.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local AssetService = game:GetService("AssetService")
local RS = game:GetService("ReplicatedStorage")

local UI = require(script.Parent.UIKit)
local Sfx = require(script.Parent.Sfx)
local EggArt = require(script.Parent.EggArt)

local EggScene = {}

local WHITE = Color3.new(1, 1, 1)
local BLACK = Color3.new(0, 0, 0)

local function easeOutBack(t: number): number
	local c1 = 1.70158
	local c3 = c1 + 1
	return 1 + c3 * (t - 1) ^ 3 + c1 * (t - 1) ^ 2
end

local function easeOutCubic(t: number): number
	return 1 - (1 - t) ^ 3
end

local function newI(class: string, props: { [string]: any }, parent: Instance?): any
	local i = Instance.new(class)
	for k, v in props do
		(i :: any)[k] = v
	end
	if parent then
		i.Parent = parent
	end
	return i
end

local function rgba(r: number, g: number, b: number, a: number): number
	return r + g * 256 + b * 65536 + a * 16777216
end

-- A soft white ring texture (generated once); the scene tints it and stretches it into circles and floor ellipses
local ringImage: any = nil
local function getRingImage(): any
	if ringImage then
		return ringImage
	end
	local S = 160
	local img = AssetService:CreateEditableImage({ Size = Vector2.new(S, S) })
	local buf = buffer.create(S * S * 4)
	local c = (S - 1) / 2
	for y = 0, S - 1 do
		for x = 0, S - 1 do
			local d = math.sqrt((x - c) ^ 2 + (y - c) ^ 2) / c
			local a = d > 1 and 0 or math.exp(-((d - 0.88) / 0.06) ^ 2)
			buffer.writeu32(buf, (y * S + x) * 4, 16777215 + math.floor(math.clamp(a, 0, 1) * 255) * 16777216)
		end
	end
	img:WritePixelsBuffer(Vector2.zero, Vector2.new(S, S), buf)
	ringImage = img
	return img
end

---------------------------------------------------------------------
-- Cutting the egg: pieces + crack buckets (runs in a coroutine, yields often)
---------------------------------------------------------------------
local function prepare(info: any, seed: number, low: boolean): any
	local raw, w, h = info.raw, info.w, info.h
	local rng = Random.new(seed)
	local N = low and 9 or 13
	local sx, sy = {}, {}
	local tries = 0
	local minD = w * 0.22
	while #sx < N and tries < 900 do
		tries += 1
		local x, y = rng:NextInteger(4, w - 5), rng:NextInteger(4, h - 5)
		if buffer.readu8(raw, (y * w + x) * 4 + 3) > 200 then
			local ok = true
			for i = 1, #sx do
				local dx, dy = sx[i] - x, sy[i] - y
				if dx * dx + dy * dy < minD * minD then
					ok = false
					break
				end
			end
			if ok then
				table.insert(sx, x)
				table.insert(sy, y)
			end
		end
		if tries == 450 then
			minD *= 0.7
		end
	end
	local n = #sx
	local lab = buffer.create(w * h)
	local minx, maxx, miny, maxy = {}, {}, {}, {}
	for i = 1, n do
		minx[i], maxx[i], miny[i], maxy[i] = w, -1, h, -1
	end
	for y = 0, h - 1 do
		for x = 0, w - 1 do
			if buffer.readu8(raw, (y * w + x) * 4 + 3) > 40 then
				-- warped coordinates make the borders between cells irregular like real cracks
				local wx = x + 9 * math.sin(y * 0.085 + 1.3) + 5 * math.sin(y * 0.21 + x * 0.05)
				local wy = y + 9 * math.sin(x * 0.09 + 0.7) + 5 * math.sin(x * 0.19 - y * 0.04)
				local best, bi = math.huge, 1
				for i = 1, n do
					local dx, dy = wx - sx[i], wy - sy[i]
					local d = dx * dx + dy * dy
					if d < best then
						best, bi = d, i
					end
				end
				buffer.writeu8(lab, y * w + x, bi)
				if x < minx[bi] then
					minx[bi] = x
				end
				if x > maxx[bi] then
					maxx[bi] = x
				end
				if y < miny[bi] then
					miny[bi] = y
				end
				if y > maxy[bi] then
					maxy[bi] = y
				end
			end
		end
		if y % 12 == 11 then
			task.wait()
		end
	end
	-- cracks: pixels where two cells meet, grouped by how soon the crack reaches them (it spreads from an impact point)
	local NB = 24
	local buckets = {}
	for b = 1, NB do
		buckets[b] = {}
	end
	local ox, oy = w * (0.3 + 0.4 * rng:NextNumber()), h * (0.25 + 0.35 * rng:NextNumber())
	local diag = math.sqrt(w * w + h * h)
	for y = 0, h - 2 do
		for x = 0, w - 2 do
			local l = buffer.readu8(lab, y * w + x)
			if l > 0 then
				local r = buffer.readu8(lab, y * w + x + 1)
				local d = buffer.readu8(lab, (y + 1) * w + x)
				if (r > 0 and r ~= l) or (d > 0 and d ~= l) then
					local dist = math.sqrt((x - ox) ^ 2 + (y - oy) ^ 2) / diag
					local ct = math.clamp(dist * 1.5 + rng:NextNumber() * 0.12, 0, 1)
					local bk = buckets[math.min(NB, math.floor(ct * NB) + 1)]
					bk[#bk + 1] = x
					bk[#bk + 1] = y
				end
			end
		end
		if y % 24 == 23 then
			task.wait()
		end
	end
	-- the pieces (with a lit rim so they read as chunks of shell)
	local pieces = {}
	for i = 1, n do
		local bw, bh = maxx[i] - minx[i] + 1, maxy[i] - miny[i] + 1
		if bw >= 3 and bh >= 3 then
			local buf = buffer.create(bw * bh * 4)
			for y = miny[i], maxy[i] do
				for x = minx[i], maxx[i] do
					if buffer.readu8(lab, y * w + x) == i then
						local si = (y * w + x) * 4
						local di = ((y - miny[i]) * bw + (x - minx[i])) * 4
						local r, g, b, a = buffer.readu8(raw, si), buffer.readu8(raw, si + 1), buffer.readu8(raw, si + 2), buffer.readu8(raw, si + 3)
						local rim = x == 0 or y == 0 or x == w - 1 or y == h - 1
							or buffer.readu8(lab, y * w + x - 1) ~= i or buffer.readu8(lab, y * w + x + 1) ~= i
							or buffer.readu8(lab, (y - 1) * w + x) ~= i or buffer.readu8(lab, (y + 1) * w + x) ~= i
						if rim then
							r, g, b = math.min(255, r + 75), math.min(255, g + 75), math.min(255, b + 75)
						end
						buffer.writeu8(buf, di, r)
						buffer.writeu8(buf, di + 1, g)
						buffer.writeu8(buf, di + 2, b)
						buffer.writeu8(buf, di + 3, a)
					end
				end
			end
			local img = AssetService:CreateEditableImage({ Size = Vector2.new(bw, bh) })
			img:WritePixelsBuffer(Vector2.zero, Vector2.new(bw, bh), buf)
			table.insert(pieces, { img = img, x = minx[i], y = miny[i], w = bw, h = bh })
			task.wait()
		end
	end
	return { pieces = pieces, buckets = buckets, NB = NB }
end

---------------------------------------------------------------------
-- The scene
---------------------------------------------------------------------
local function start(ctx: any, info: any)
	local rar = ctx.rar
	local ex = ctx.ex
	local low = ctx.low == true
	local rank: number = ex.rarity
	local col: Color3 = rar.color
	local function accent(t: number): Color3
		if rank >= 6 then
			return Color3.fromHSV((t * 0.35) % 1, 0.55, 1)
		end
		return col
	end
	local cam = workspace.CurrentCamera
	local vw, vh = cam.ViewportSize.X, cam.ViewportSize.Y

	local sg = newI("ScreenGui", { Name = "EggHatch", DisplayOrder = 60, ResetOnSpawn = false, IgnoreGuiInset = true }, UI.top.Parent)
	local bg = newI("Frame", { BackgroundColor3 = Color3.fromRGB(8, 5, 24), BackgroundTransparency = 1, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1) }, sg)
	local hit = newI("TextButton", { Text = "", AutoButtonColor = false, BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = 2 }, sg)
	local stage = newI("Frame", { BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), ZIndex = 3 }, sg)
	local zoom = newI("UIScale", { Scale = 1 }, stage)

	local dispH = math.floor(vh * 0.5)
	local sc = dispH / info.h
	local dispW = math.floor(info.w * sc)
	local cx, cy = vw * 0.5, vh * 0.47

	-- background light: soft glows, rotating rays, a lit pedestal
	local glowA = UI.glow(stage, col, math.floor(vh * 1.5), 0.78)
	glowA.AnchorPoint = Vector2.new(0.5, 0.5)
	glowA.Position = UDim2.fromOffset(cx, cy)
	glowA.ZIndex = 1
	local rays1: any = nil
	pcall(function()
		rays1 = UI.rays(stage, col:Lerp(WHITE, 0.3), 14, math.floor(vh * 1.7), 18)
		rays1.AnchorPoint = Vector2.new(0.5, 0.5)
		rays1.Position = UDim2.fromOffset(cx, cy)
		rays1.ZIndex = 2
		newI("UIScale", { Name = "S", Scale = 0.25 }, rays1)
	end)
	local floorY = cy + dispH * 0.5
	local pedGlow = UI.glow(stage, col, math.floor(dispW * 2.6), 0.5)
	pedGlow.AnchorPoint = Vector2.new(0.5, 0.5)
	pedGlow.Size = UDim2.fromOffset(dispW * 2.8, dispH * 0.34)
	pedGlow.Position = UDim2.fromOffset(cx, floorY)
	pedGlow.ZIndex = 3
	local floorRing = newI("ImageLabel", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Size = UDim2.fromOffset(dispW * 1.9, dispW * 1.9 * 0.3), Position = UDim2.fromOffset(cx, floorY), ImageColor3 = col, ImageTransparency = 0.2, ZIndex = 3 }, stage)
	pcall(function()
		floorRing.ImageContent = Content.fromObject(getRingImage())
	end)
	local aura = UI.glow(stage, col, math.floor(dispH * 1.45), 0.8)
	aura.AnchorPoint = Vector2.new(0.5, 0.5)
	aura.Position = UDim2.fromOffset(cx, cy)
	aura.ZIndex = 4

	-- the egg: sprite + crack overlay (a second EditableImage the cracks are drawn into)
	local eggFrame = newI("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Size = UDim2.fromOffset(dispW, dispH), Position = UDim2.fromOffset(cx, cy - dispH * 0.9), ZIndex = 5 }, stage)
	local eggScale = newI("UIScale", { Scale = 0.2 }, eggFrame)
	local eggImg = newI("ImageLabel", { BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = 5 }, eggFrame)
	pcall(function()
		eggImg.ImageContent = Content.fromObject(EggArt.imageOf("hatch_" .. ctx.eggKey))
	end)
	local crackImage: any = nil
	local cbuf = buffer.create(info.w * info.h * 4)
	local crackLabel = newI("ImageLabel", { BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = 6 }, eggFrame)
	pcall(function()
		crackImage = AssetService:CreateEditableImage({ Size = Vector2.new(info.w, info.h) })
		crackLabel.ImageContent = Content.fromObject(crackImage)
	end)

	-- particles: one pool, reused for everything (sparks, dust pulled into the egg, confetti)
	local nP = low and 46 or 100
	local pool = {}
	for i = 1, nP do
		pool[i] = { on = false, f = newI("Frame", { BorderSizePixel = 0, AnchorPoint = Vector2.new(0.5, 0.5), Visible = false, ZIndex = 9 }, stage) }
	end
	local poolIdx = 0
	local function emit(kind: string, x: number, y: number, vx: number, vy: number, life: number, size: number, color: Color3, spin: number?, grav: number?): any
		for _ = 1, nP do
			poolIdx = poolIdx % nP + 1
			local q = pool[poolIdx]
			if not q.on then
				q.on, q.kind, q.x, q.y, q.vx, q.vy, q.t, q.life, q.size = true, kind, x, y, vx, vy, 0, life, size
				q.spin, q.grav, q.rot = spin or 0, grav or 0, math.random() * 360
				q.f.BackgroundColor3 = color
				q.f.Visible = true
				q.f.Rotation = q.rot
				if kind == "pull" then
					q.ang = math.atan2(y - cy, x - cx)
					q.r0 = math.sqrt((x - cx) ^ 2 + (y - cy) ^ 2)
				end
				return q
			end
		end
		return nil
	end

	-- shockwave rings (a ring texture stretched into a circle, or flat to look like a ripple on the floor)
	local rings = {}
	for i = 1, 6 do
		local f = newI("ImageLabel", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Visible = false, ZIndex = 7 }, stage)
		pcall(function()
			f.ImageContent = Content.fromObject(getRingImage())
		end)
		rings[i] = { on = false, f = f }
	end
	local ringIdx = 0
	local function ring(x: number, y: number, r0: number, r1: number, dur: number, color: Color3, delay: number?, flat: number?)
		ringIdx = ringIdx % #rings + 1
		local r = rings[ringIdx]
		r.on, r.x, r.y, r.r0, r.r1, r.dur, r.t, r.flat = true, x, y, r0, r1, dur, -(delay or 0), flat or 1
		r.f.ImageColor3 = color
	end

	-- screen hud: hint, progress bar, skip
	local hint = UI.label({ Text = "TAP THE EGG!", TextSize = 34, Color = WHITE, StrokeColor = col:Lerp(BLACK, 0.6), Stroke = 5, Size = UDim2.fromOffset(520, 44), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(cx, vh * 0.8), ZIndex = 14, Parent = stage })
	hint.Visible = false
	local hintScale = newI("UIScale", { Scale = 1 }, hint)
	local barBg = newI("Frame", { BackgroundColor3 = Color3.fromRGB(14, 8, 34), BorderSizePixel = 0, AnchorPoint = Vector2.new(0.5, 0), Size = UDim2.fromOffset(300, 12), Position = UDim2.fromOffset(cx, vh * 0.8 + 52), Visible = false, ZIndex = 14 }, stage)
	newI("UICorner", { CornerRadius = UDim.new(0.5, 0) }, barBg)
	newI("UIStroke", { Color = col:Lerp(BLACK, 0.5), Thickness = 2 }, barBg)
	local barFill = newI("Frame", { BackgroundColor3 = col, BorderSizePixel = 0, Size = UDim2.fromScale(0, 1), ZIndex = 15 }, barBg)
	newI("UICorner", { CornerRadius = UDim.new(0.5, 0) }, barFill)

	local flash = newI("Frame", { BackgroundColor3 = WHITE, BackgroundTransparency = 1, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1), ZIndex = 50, Active = false }, sg)

	-- reveal group (built now, shown after the burst)
	local side = math.floor(vh * 0.36)
	local pcy = vh * 0.34
	local revRays: any = nil
	pcall(function()
		revRays = UI.rays(stage, col:Lerp(WHITE, 0.25), 16, math.floor(vh * 1.9), 12)
		revRays.AnchorPoint = Vector2.new(0.5, 0.5)
		revRays.Position = UDim2.fromOffset(cx, pcy)
		revRays.ZIndex = 10
		revRays.Visible = false
		newI("UIScale", { Name = "S", Scale = 0.2 }, revRays)
	end)
	local holder = newI("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Size = UDim2.fromOffset(side * 1.3, side), Position = UDim2.fromOffset(cx, pcy), Visible = false, ZIndex = 12 }, stage)
	local holderScale = newI("UIScale", { Scale = 0 }, holder)
	local holderGlow = UI.glow(holder, col, math.floor(side * 1.5), 0.45)
	holderGlow.AnchorPoint = Vector2.new(0.5, 0.5)
	holderGlow.Position = UDim2.fromScale(0.5, 0.5)
	holderGlow.ZIndex = 11
	if ctx.portrait then
		pcall(ctx.portrait, holder)
	end
	local ry = pcy + side * 0.5 + 8
	local info2 = newI("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Size = UDim2.fromOffset(560, 300), Position = UDim2.fromOffset(cx, ry + 40), Visible = false, ZIndex = 12 }, stage)
	local infoScale = newI("UIScale", { Scale = 0.8 }, info2)
	local panel = newI("Frame", { BackgroundColor3 = Color3.fromRGB(14, 8, 34), BackgroundTransparency = 0.4, BorderSizePixel = 0, Size = UDim2.new(1, 0, 0, 280), Position = UDim2.fromOffset(0, 0), ZIndex = 11 }, info2)
	newI("UICorner", { CornerRadius = UDim.new(0, 18) }, panel)
	newI("UIStroke", { Color = col, Thickness = 2, Transparency = 0.35 }, panel)
	local ribbon = newI("Frame", { BackgroundColor3 = col:Lerp(BLACK, 0.45), BackgroundTransparency = 0.1, BorderSizePixel = 0, Size = UDim2.new(1, 0, 0, 34), ZIndex = 12 }, info2)
	newI("UIGradient", { Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, 0), NumberSequenceKeypoint.new(0.8, 0), NumberSequenceKeypoint.new(1, 1) }) }, ribbon)
	UI.label({ Text = string.upper(rar.name), TextSize = 24, Color = col:Lerp(WHITE, 0.35), StrokeColor = BLACK, Stroke = 4, Size = UDim2.fromScale(1, 1), ZIndex = 13, Parent = ribbon })
	UI.label({ Text = ex.name, TextSize = 50, Color = WHITE, StrokeColor = col:Lerp(BLACK, 0.6), Stroke = 6, Scaled = true, MaxSize = 50, Size = UDim2.new(1, 0, 0, 58), Position = UDim2.fromOffset(0, 38), ZIndex = 13, Parent = info2 })
	UI.label({ Text = ex.desc, TextSize = 17, Color = WHITE, StrokeColor = BLACK, Stroke = 3, Wrap = true, Size = UDim2.new(1, -40, 0, 44), Position = UDim2.fromOffset(20, 98), ZIndex = 13, Parent = info2 })
	local ly = 146
	for _, l in ctx.lines or {} do
		UI.label({ Text = l[1], TextSize = 22, Color = l[2], StrokeColor = BLACK, Stroke = 3, Size = UDim2.new(1, 0, 0, 26), Position = UDim2.fromOffset(0, ly), ZIndex = 13, Parent = info2 })
		ly += 26
	end
	local tagText = ctx.dupe and string.format("DUPLICATE  +%d shards", ctx.shards or 0) or "NEW EXOTIC!"
	local tag = UI.label({ Text = tagText, TextSize = 28, Color = ctx.dupe and Color3.fromRGB(160, 220, 255) or Color3.fromRGB(255, 216, 74), StrokeColor = BLACK, Stroke = 5, Size = UDim2.new(1, 0, 0, 36), Position = UDim2.fromOffset(0, ly + 6), ZIndex = 13, Parent = info2 })
	local tagScale = newI("UIScale", { Scale = 0 }, tag)
	panel.Size = UDim2.new(1, 0, 0, ly + 52)

	local finished = false
	local conn: RBXScriptConnection? = nil
	local prep: any = nil
	local prepFailed = false
	local function cleanup()
		if prep then
			for _, p in prep.pieces do
				pcall(function()
					p.img:Destroy()
				end)
			end
		end
		pcall(function()
			if crackImage then
				crackImage:Destroy()
			end
		end)
	end
	local finish: () -> () = function() end
	local cont = UI.button({ Text = "CONTINUE", TextSize = 24, Color = Color3.fromRGB(84, 214, 52), Size = UDim2.fromOffset(220, 50), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromOffset(cx, vh - 76), ZIndex = 40, Sound = "press" }, function()
		finish()
	end)
	cont.Visible = false
	cont.Parent = sg
	local onSkip: () -> () = function() end
	local skip = UI.button({ Text = "SKIP", TextSize = 18, Color = Color3.fromRGB(90, 70, 150), Size = UDim2.fromOffset(96, 36), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -20, 1, -20), ZIndex = 40, Sound = "press" }, function()
		onSkip()
	end)
	skip.Visible = false
	skip.Parent = sg

	-- cut the egg in the background while the intro plays
	task.spawn(function()
		local ok, res = pcall(prepare, info, math.floor(os.clock() * 1000) % 100000 + 7, low)
		if ok and res then
			prep = res
		else
			prepFailed = true
			warn("[EggScene] prepare failed: " .. tostring(res))
		end
	end)

	-- state
	local phase = "intro"
	local pt = 0
	local clock = 0
	local p = 0
	local tapKick = 0
	local shake = 0
	local lastTick = 0
	local stageHits = { false, false, false, false, false }
	local pullAcc = 0
	local drawn = 0
	local ps: { any } = {}
	local revealed = false
	local canFinish = false
	local second = false

	local function drawCracks(prog: number)
		if not prep or not crackImage then
			return
		end
		local upto = math.min(prep.NB, math.floor(prog * prep.NB * 1.04))
		if upto <= drawn then
			return
		end
		local w, h = info.w, info.h
		local coreC = rgba(255, 248, 232, 255)
		local hc = col:Lerp(WHITE, 0.45)
		local haloC = rgba(math.floor(hc.R * 255), math.floor(hc.G * 255), math.floor(hc.B * 255), 200)
		for b = drawn + 1, upto do
			local bk = prep.buckets[b]
			for i = 1, #bk, 2 do
				local x, y = bk[i], bk[i + 1]
				for dy = -1, 1 do
					for dx = -1, 1 do
						local xx, yy = x + dx, y + dy
						if xx >= 0 and yy >= 0 and xx < w and yy < h then
							local idx = (yy * w + xx) * 4
							if dx == 0 and dy == 0 or (dy == 0 and dx == 1) then
								buffer.writeu32(cbuf, idx, coreC)
							elseif buffer.readu8(cbuf, idx + 3) < 200 then
								buffer.writeu32(cbuf, idx, haloC)
							end
						end
					end
				end
			end
		end
		drawn = upto
		crackImage:WritePixelsBuffer(Vector2.zero, Vector2.new(w, h), cbuf)
	end

	local function burstSparks(n: number, speed: number)
		for _ = 1, math.floor(n * (low and 0.5 or 1)) do
			local a = math.random() * math.pi * 2
			local s = speed * (0.4 + math.random() * 0.8)
			emit("spark", cx, cy, math.cos(a) * s, math.sin(a) * s - speed * 0.2, 0.7 + math.random() * 0.6, 8 + math.random() * 12, math.random() < 0.4 and WHITE or accent(clock + math.random()), 0, 700)
		end
	end

	local function stageHit(k: number)
		stageHits[k] = true
		ring(cx, floorY, dispW * 0.5, dispW * (1.3 + k * 0.2), 0.7, accent(clock), 0, 0.3)
		ring(cx, cy, dispH * 0.2, dispH * (0.7 + k * 0.1), 0.6, accent(clock))
		burstSparks(5 + k * 2, 300 + k * 60)
		shake = math.max(shake, 4 + k * 2.5)
		Sfx.play("boom", 0.7 + k * 0.12, 0.35 + k * 0.05)
		hintScale.Scale = 1.3
		tapKick = 1
	end

	local function startBurst()
		phase = "burst"
		pt = 0
		eggImg.Visible = false
		crackLabel.Visible = false
		eggFrame.Rotation = 0
		hint.Visible = false
		barBg.Visible = false
		skip.Visible = false
		floorRing.Visible = false
		pedGlow.Visible = false
		-- shell pieces fly out of the egg
		if prep then
			for _, pc in prep.pieces do
				local lbl = newI("ImageLabel", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Size = UDim2.fromOffset(pc.w * sc, pc.h * sc), ZIndex = 8 }, eggFrame)
				lbl.ImageContent = Content.fromObject(pc.img)
				local px, py = (pc.x + pc.w * 0.5) * sc, (pc.y + pc.h * 0.5) * sc
				lbl.Position = UDim2.fromOffset(px, py)
				local dx, dy = px - dispW * 0.5, py - dispH * 0.5
				local len = math.max(math.sqrt(dx * dx + dy * dy), 1)
				local spd = (430 + math.random() * 480) * (vh / 800)
				table.insert(ps, { lbl = lbl, x = px, y = py, vx = dx / len * spd + (math.random() - 0.5) * 120, vy = dy / len * spd - 330 * (vh / 800), rot = 0, spin = (math.random() - 0.5) * 900 })
			end
		end
		flash.BackgroundColor3 = WHITE
		flash.BackgroundTransparency = 0
		UI.tween(flash, 0.75, { BackgroundTransparency = 1 })
		ring(cx, floorY, dispW * 0.6, dispW * 3.2, 0.9, WHITE, 0, 0.3)
		ring(cx, cy, dispH * 0.15, vh * 0.95, 0.9, WHITE)
		ring(cx, cy, dispH * 0.1, vh * 0.75, 0.8, accent(clock), 0.08)
		ring(cx, cy, dispH * 0.1, vh * 0.55, 0.7, col:Lerp(WHITE, 0.4), 0.16)
		burstSparks(46, 900)
		for _ = 1, low and 18 or 46 do
			local a = math.random() * math.pi * 2
			local s = 250 + math.random() * 650
			local cc = rank >= 6 and Color3.fromHSV(math.random(), 0.6, 1) or (math.random() < 0.5 and col or col:Lerp(WHITE, 0.6))
			emit("conf", cx, cy, math.cos(a) * s, math.sin(a) * s - 500, 1.6 + math.random() * 1.2, 10 + math.random() * 8, cc, (math.random() - 0.5) * 720, 900)
		end
		shake = low and 10 or 22
		task.spawn(function()
			UI.tween(zoom, 0.1, { Scale = 1.09 })
			task.wait(0.12)
			UI.tween(zoom, 0.55, { Scale = 1 }, Enum.EasingStyle.Back)
		end)
		Sfx.play("boom", 1, 1)
		Sfx.play(rank >= 5 and "thunder" or "pop", 1, 0.9)
		if rays1 then
			local s = rays1:FindFirstChild("S")
			if s then
				s.Scale = 1.6
			end
		end
	end

	local function startReveal()
		revealed = true
		holder.Visible = true
		info2.Visible = true
		if revRays then
			revRays.Visible = true
		end
		UI.tween(holderScale, 0.7, { Scale = 1 }, Enum.EasingStyle.Back)
		UI.tween(infoScale, 0.55, { Scale = 1 }, Enum.EasingStyle.Back)
		UI.tween(info2, 0.5, { Position = UDim2.fromOffset(cx, ry) }, Enum.EasingStyle.Quad)
		Sfx.play("sparkle", 1 + rank * 0.04, 0.9)
		task.delay(0.6, function()
			if not finished then
				UI.tween(tagScale, 0.5, { Scale = 1 }, Enum.EasingStyle.Back)
				Sfx.play("pop", 1.2, 0.6)
			end
		end)
		if rank >= 4 then
			task.delay(0.35, function()
				if not finished then
					Sfx.play("level", 1, 0.8)
					flash.BackgroundColor3 = col:Lerp(WHITE, 0.4)
					flash.BackgroundTransparency = 0.35
					UI.tween(flash, 0.8, { BackgroundTransparency = 1 })
					ring(cx, pcy, side * 0.2, vh * 0.8, 0.9, col:Lerp(WHITE, 0.3))
					shake = math.max(shake, 8)
				end
			end)
		end
	end

	finish = function()
		if finished then
			return
		end
		finished = true
		if conn then
			conn:Disconnect()
		end
		cleanup()
		sg:Destroy()
		if ctx.onDone then
			ctx.onDone()
		end
	end

	hit.MouseButton1Click:Connect(function()
		if phase == "charge" then
			p = math.min(1, p + 0.07)
			tapKick = 1
			shake = math.max(shake, 3)
			Sfx.play("tick", 1.2 + p * 0.8, 0.5)
			local a = math.random() * math.pi * 2
			for _ = 1, low and 1 or 3 do
				emit("spark", cx, cy, math.cos(a) * 240, math.sin(a) * 240 - 100, 0.5, 8, WHITE, 0, 500)
			end
		elseif phase == "burst" and canFinish then
			finish()
		end
	end)
	onSkip = function()
		if phase == "intro" or phase == "charge" then
			p = 1
			if phase == "intro" then
				phase = "charge"
				pt = 0
				eggFrame.Position = UDim2.fromOffset(cx, cy)
				eggScale.Scale = 1
				eggFrame.Rotation = 0
			end
		end
	end

	conn = RunService.RenderStepped:Connect(function(dt0)
		local dt = math.min(dt0, 0.05) * (tonumber(Players.LocalPlayer.PlayerGui:GetAttribute("EggSceneSpeed")) or 1) -- debug: slow motion for checking frames
		clock += dt
		pt += dt
		-- screen shake
		if shake > 0.2 then
			stage.Position = UDim2.new(0.5, (math.random() - 0.5) * 2 * shake, 0.5, (math.random() - 0.5) * 2 * shake)
			shake = math.max(0, shake - dt * (low and 30 or 38))
		else
			stage.Position = UDim2.fromScale(0.5, 0.5)
		end
		-- rays rotate by themselves; scale/aura per phase below
		if phase == "intro" then
			local u = math.clamp(pt / 0.75, 0, 1)
			bg.BackgroundTransparency = 1 - 0.965 * math.clamp(pt / 0.5, 0, 1)
			eggScale.Scale = 0.2 + 0.8 * easeOutBack(u)
			local drop = easeOutCubic(math.clamp(pt / 0.55, 0, 1))
			eggFrame.Position = UDim2.fromOffset(cx, cy - dispH * 0.9 * (1 - drop))
			eggFrame.Rotation = (1 - u) * -14
			aura.ImageTransparency = 0.8 - 0.25 * u
			if pt >= 0.55 and not second then
				second = true
				ring(cx, floorY, dispW * 0.3, dispW * 2.0, 0.7, accent(clock), 0, 0.3)
				burstSparks(10, 340)
				Sfx.play("pop", 0.9, 0.8)
				shake = 6
			end
			if pt >= 1.05 then
				phase = "charge"
				pt = 0
				hint.Visible = true
				barBg.Visible = true
				skip.Visible = true
			end
		elseif phase == "charge" then
			local D = low and 3.2 or 5.0
			p = math.min(1, p + dt / D * (0.55 + 0.9 * p))
			tapKick = math.max(0, tapKick - dt * 5)
			local fq = 7 + 22 * p
			local amp = 1.2 + 13 * p ^ 1.6
			eggFrame.Rotation = math.sin(clock * fq) * amp + tapKick * 5 * math.sin(clock * 40)
			eggFrame.Position = UDim2.fromOffset(cx + math.sin(clock * 53) * 5 * p ^ 2, cy + math.sin(clock * 47) * 3 * p ^ 2 - tapKick * 6)
			eggScale.Scale = 1 + 0.12 * p + 0.025 * math.sin(clock * 9) + tapKick * 0.05
			local ac = accent(clock)
			aura.ImageColor3 = ac
			aura.ImageTransparency = 0.7 - 0.5 * p + 0.06 * math.sin(clock * (5 + 12 * p))
			pedGlow.ImageColor3 = ac
			floorRing.ImageColor3 = ac
			floorRing.ImageTransparency = 0.25 - 0.2 * p + 0.08 * math.sin(clock * 6)
			glowA.ImageColor3 = ac
			glowA.ImageTransparency = 0.82 - 0.3 * p
			if rays1 then
				local s = rays1:FindFirstChild("S")
				if s then
					s.Scale = 0.25 + 0.75 * p
				end
			end
			-- cracks grow with progress
			drawCracks(p)
			for k, th in { 0.18, 0.4, 0.62, 0.8, 0.93 } do
				if p >= th and not stageHits[k] then
					stageHit(k)
				end
			end
			-- sparks pulled into the egg
			pullAcc += dt * (6 + 44 * p) * (low and 0.5 or 1)
			while pullAcc >= 1 do
				pullAcc -= 1
				local a = math.random() * math.pi * 2
				local r = dispH * (0.7 + math.random() * 0.6)
				emit("pull", cx + math.cos(a) * r, cy + math.sin(a) * r * 0.8, 0, 0, 0.55 + math.random() * 0.4, 6 + math.random() * 8, math.random() < 0.35 and WHITE or accent(clock + math.random()), (math.random() < 0.5 and 1 or -1) * (2 + math.random() * 2))
			end
			-- ticking gets faster and higher
			if clock - lastTick > 0.55 - 0.43 * p then
				lastTick = clock
				Sfx.play("tick", 0.8 + p * 1.0, 0.45)
			end
			hintScale.Scale += (1 + 0.08 * math.sin(clock * 8) - hintScale.Scale) * math.min(1, dt * 10)
			hint.Text = p < 0.4 and "TAP THE EGG!" or (p < 0.8 and "KEEP TAPPING!" or "ALMOST THERE!")
			barFill.Size = UDim2.fromScale(p, 1)
			barFill.BackgroundColor3 = ac
			if pt > 1.0 then
				skip.Visible = true
			end
			if p >= 1 and (prep or prepFailed) then
				startBurst()
			end
		elseif phase == "burst" then
			-- shell pieces: gravity, spin, fade
			for _, q in ps do
				q.vy += 1500 * (vh / 800) * dt
				q.x += q.vx * dt
				q.y += q.vy * dt
				q.rot += q.spin * dt
				q.lbl.Position = UDim2.fromOffset(q.x, q.y)
				q.lbl.Rotation = q.rot
				q.lbl.ImageTransparency = math.clamp((pt - 0.45) / 0.9, 0, 1)
			end
			aura.ImageTransparency = 0.35 + 0.2 * math.sin(clock * 6)
			aura.ImageColor3 = accent(clock)
			if rays1 then
				local s = rays1:FindFirstChild("S")
				if s then
					s.Scale = math.max(1, s.Scale - dt * 1.2)
				end
			end
			if pt > 0.45 and not revealed then
				startReveal()
			end
			if revealed then
				if revRays then
					local s = revRays:FindFirstChild("S")
					if s then
						s.Scale = math.min(1, s.Scale + dt * 1.6)
					end
				end
				-- confetti rain keeps falling for a while
				if pt < 3.2 then
					pullAcc += dt * (low and 7 or 18)
					while pullAcc >= 1 do
						pullAcc -= 1
						emit("conf", math.random() * vw, -20, (math.random() - 0.5) * 80, 120 + math.random() * 120, 2.4 + math.random(), 9 + math.random() * 8, rank >= 6 and Color3.fromHSV(math.random(), 0.6, 1) or (math.random() < 0.5 and col or col:Lerp(WHITE, 0.6)), (math.random() - 0.5) * 540, 120)
					end
				end
			end
			if pt > 1.4 and not canFinish then
				canFinish = true
				cont.Visible = true
			end
		end
		-- particles
		for i = 1, nP do
			local q = pool[i]
			if q.on then
				q.t += dt
				local u = q.t / q.life
				if u >= 1 then
					q.on = false
					q.f.Visible = false
				else
					if q.kind == "pull" then
						q.ang += q.spin * dt
						local r = q.r0 * (1 - u) ^ 1.4
						q.x = cx + math.cos(q.ang) * r
						q.y = cy + math.sin(q.ang) * r * 0.85
						q.f.BackgroundTransparency = (u < 0.2) and (1 - u / 0.2) or ((u > 0.75) and ((u - 0.75) / 0.25) or 0)
						q.f.Size = UDim2.fromOffset(q.size * (1 - 0.5 * u), q.size * (1 - 0.5 * u))
					else
						q.vy += q.grav * dt
						q.vx *= (1 - 0.8 * dt)
						q.x += q.vx * dt
						q.y += q.vy * dt
						q.rot += q.spin * dt
						q.f.Rotation = q.rot
						q.f.BackgroundTransparency = u < 0.6 and 0 or (u - 0.6) / 0.4
						if q.kind == "conf" then
							q.f.Size = UDim2.fromOffset(q.size, math.max(2, q.size * 0.55 * math.abs(math.cos(q.t * 7 + q.rot))))
						else
							local s = q.size * (1 - 0.7 * u)
							q.f.Size = UDim2.fromOffset(s, s)
						end
					end
					q.f.Position = UDim2.fromOffset(q.x, q.y)
				end
			end
		end
		-- rings
		for _, r in rings do
			if r.on then
				r.t += dt
				if r.t >= r.dur then
					r.on = false
					r.f.Visible = false
				elseif r.t >= 0 then
					local u = r.t / r.dur
					local d = (r.r0 + (r.r1 - r.r0) * easeOutCubic(u)) * 2
					r.f.Visible = true
					r.f.Size = UDim2.fromOffset(d, d * r.flat)
					r.f.Position = UDim2.fromOffset(r.x, r.y)
					r.f.ImageTransparency = 0.1 + 0.9 * u
				end
			end
		end
	end)
end

function EggScene.available(eggKey: string): boolean
	return EggArt.has("hatch_" .. eggKey)
end

-- ctx: eggKey, ex (exotic species), rar (rarity table with .color/.name), low, dupe, shards, lines, portrait(parent), onDone, onFail
function EggScene.play(ctx: any)
	EggArt.whenRaw("hatch_" .. ctx.eggKey, function(info)
		if not info then
			if ctx.onFail then
				ctx.onFail()
			end
			return
		end
		local ok, err = pcall(start, ctx, info)
		if not ok then
			warn("[EggScene] " .. tostring(err))
			if ctx.onFail then
				ctx.onFail()
			end
		end
	end)
end

return EggScene
