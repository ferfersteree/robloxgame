-- Local gestures for the supplied v11 vendor rigs. Gameplay and prompts stay
-- with the existing server/client controllers; this module only poses joints.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local NativeVendors = {}
local player = Players.LocalPlayer
local bindings = {}
local metadataCache = {}
local pending = setmetatable({}, { __mode = "k" })
local connections = {}
local initialized = false
local lengths = { hello = 2.7, farewell = 2, talk = 5.4, yes = 1.7, no = 1.8, inspect = 3 }

local function action(actor, state)
	if not lengths[state] then return end
	actor.state = state
	actor.elapsed = 0
end

local function reset(binding)
	for index, joint in pairs(binding.motors) do
		if joint.Parent then joint.C0 = binding.rest[index] end
	end
	for lid, transparency in pairs(binding.lidRest) do
		if lid.Parent then lid.Transparency = transparency end
	end
end

local function bind(source)
	if pending[source] then return end
	pending[source] = true
	task.spawn(function()
		local model = source.Parent
		if not model or not model:IsA("Model") or bindings[model] then return end
		local rig = model:FindFirstChild("Rig") or model:WaitForChild("Rig", 5)
		if not rig or not model:IsDescendantOf(workspace) then pending[source] = nil; return end
		local assetId = model:GetAttribute("AssetId")
		local key = if assetId then tostring(model:GetAttribute("AssetKind")) .. ":" .. tostring(assetId) else source
		local metadata = metadataCache[key]
		if not metadata then
			local ok, result = pcall(require, source)
			if not ok or type(result) ~= "table" then return end
			metadata = result
			metadataCache[key] = metadata
		end
		local binding = { model = model, motors = {}, rest = {}, actors = {}, lidRest = {}, visible = false, reaction = "" }
		local parts = {}
		for _, bone in ipairs(rig:GetChildren()) do
			if not bone:IsA("BasePart") then continue end
			local index = bone:GetAttribute("BoneIndex")
			local joint = bone:FindFirstChild("Joint")
			if typeof(index) == "number" then
				parts[index] = bone
				if joint and joint:IsA("Motor6D") then binding.motors[index] = joint; binding.rest[index] = joint.C0 end
			end
		end
		local geometry = model:FindFirstChild("Geometry")
		for index, data in ipairs(metadata) do
			local head = rig:FindFirstChild(data.headPart) or parts[data.head]
			if not head or not head:IsA("BasePart") then continue end
			local actor = { data = data, head = head, state = "idle", elapsed = 0, near = false, phase = data.role * .71 + index * .34, lids = {} }
			for _, name in ipairs(data.lids or {}) do
				local lid = geometry and geometry:FindFirstChild(name)
				if lid and lid:IsA("BasePart") then actor.lids[#actor.lids + 1] = lid; binding.lidRest[lid] = lid.Transparency end
			end
			binding.actors[#binding.actors + 1] = actor
		end
		if #binding.actors > 0 then bindings[model] = binding end
	end)
end

local function rotate(binding, index, x, y, z, dy)
	local joint = binding.motors[index]
	if joint and joint.Parent then joint.C0 = binding.rest[index] * CFrame.new(0, dy or 0, 0) * CFrame.Angles(x or 0, y or 0, z or 0) end
end

local function stepActor(binding, actor, dt, t, observer)
	local data, p = actor.data, actor.phase
	actor.elapsed += dt
	local distance = (observer - actor.head.Position).Magnitude
	local near = distance < (if actor.near then 15 else 11)
	if near and not actor.near then action(actor, "hello") elseif not near and actor.near then action(actor, "farewell") end
	actor.near = near
	local duration = lengths[actor.state]
	if duration and actor.elapsed >= duration then actor.state = "idle"; actor.elapsed = 0; duration = nil end
	local u = actor.elapsed
	local env = if duration then math.clamp(u / .22, 0, 1) * math.clamp((duration - u) / .28, 0, 1) else 0
	local chest = { math.sin(t * 1.55 + p) * .008, math.sin(t * .55 + p) * .008, math.sin(t * .75 + p) * .005 }
	local head = { math.sin(t * 1.4 + p) * .012, math.sin(t * .65 + p) * .045, 0 }
	local arms = {
		{ { math.sin(t * 1.1 + p) * .016, 0, -.012 }, { -.035, 0, 0 }, { 0, 0, 0 } },
		{ { math.sin(t * 1.1 + p + 1) * .016, 0, .012 }, { -.035, 0, 0 }, { 0, 0, 0 } },
	}
	if actor.state == "hello" or actor.state == "farewell" then
		local i = math.clamp((data.wave or 0) + 1, 1, 2)
		local side, gain = if i == 2 then 1 else -1, if actor.state == "hello" then 1 else .77
		arms[i] = { { -.16 * env, side * .08 * env, side * 1.85 * env * gain }, { -.45 * env, side * .09 * env, side * (.22 + math.sin(u * 10 + p) * .17) * env }, { math.sin(u * 10 + p) * .09 * env, math.sin(u * 10 + p) * .19 * env, side * math.sin(u * 10 + p) * .27 * env } }
		head[3] = side * .035 * env; head[1] += math.sin(u * 6) * .045 * env; chest[1] -= .015 * env
	elseif actor.state == "talk" or actor.state == "inspect" then
		local speech, beat = math.sin(u * 5.2 + p), math.sin(u * 3.1 + p)
		local gain = if data.role == 5 then .72 else if data.role == 3 then 1.12 else 1
		for i = 1, 2 do
			local side = if i == 2 then 1 else -1
			arms[i] = { { -(.25 + speech * .07) * env, side * .10 * env, side * (.42 + beat * .10) * env * gain }, { -(.61 + math.sin(u * 4.5 + i - 1 + p) * .15) * env, side * .12 * env, side * .08 * env }, { math.sin(u * 4.2 + i - 1) * .05 * env, side * .12 * env, side * (.1 + math.sin(u * 3.2 + i - 1) * .07) * env } }
		end
		head[1] += (.015 + math.sin(u * 5.3 + p) * .038) * env; head[2] += math.sin(u * 2.2 + p) * .065 * env; chest[1] -= .014 * env
	elseif actor.state == "yes" then head[1] += (.04 + math.sin(u * 10) * .16) * env
	elseif actor.state == "no" then head[2] += math.sin(u * 10.5) * .22 * env
	end
	if data.heldHand then
		local i = math.clamp(data.heldHand, 1, 2)
		local side = if i == 2 then 1 else -1
		local talk = if actor.state == "talk" then env else 0
		arms[i] = { { math.sin(t * 1.1 + p) * .008 - .055 * talk, side * .018 * talk, side * .055 * talk }, { -.045 - .045 * talk, 0, side * .015 * talk }, { .012 * talk, 0, -side * .018 * talk } }
		-- Tools are welded to the supplied hand bone, so hammer and spear grips
		-- remain intact throughout these small working gestures.
		if data.role == 0 and actor.state == "idle" then
			local work = (t + p) % 4.2
			if work < 1.8 then
				local pulse = math.sin(math.clamp(work / 1.8, 0, 1) * math.pi) ^ 2
				arms[i][1][1] -= .43 * pulse; arms[i][2][1] -= .52 * pulse; chest[1] += .025 * pulse
			end
		end
	end
	if data.role == 1 and actor.state == "idle" and near then
		local lift = (.5 + .5 * math.sin(t * 2.1 + p)) * .22
		for i = 1, 2 do arms[i][2][1] -= lift end
	end
	-- Use the unposed joint frame, avoiding feedback from last frame's look.
	local joint = binding.motors[data.head]
	if distance < 30 and joint and joint.Part0 then
		local localPoint = (joint.Part0.CFrame * binding.rest[data.head]):PointToObjectSpace(observer)
		local horizontal = math.sqrt(localPoint.X ^ 2 + localPoint.Z ^ 2)
		local weight = math.clamp((30 - distance) / 14, 0, 1)
		head[2] += math.clamp(math.atan2(localPoint.X, localPoint.Z), -.38, .38) * weight
		head[1] -= math.clamp(math.atan2(localPoint.Y, horizontal), -.16, .16) * weight
	end
	rotate(binding, data.chest, chest[1], chest[2], chest[3], math.sin(t * 1.6 + p) * .012)
	rotate(binding, data.head, head[1], head[2], head[3])
	for i, indices in ipairs(data.arms or {}) do
		for j, index in ipairs(indices) do local angles = arms[i] and arms[i][j]; if angles then rotate(binding, index, angles[1], angles[2], angles[3]) end end
	end
	local blink = (t + p) % (4.1 + data.role * .13)
	for _, lid in ipairs(actor.lids) do if lid.Parent then lid.Transparency = if blink > .08 and blink < .22 then 0 else binding.lidRest[lid] end end
end

-- Optional visual reactions for the existing menu controller.
function NativeVendors.react(target, state)
	if not target then return end
	for model, binding in pairs(bindings) do
		if model == target or model:IsDescendantOf(target) then for _, actor in ipairs(binding.actors) do action(actor, state) end end
	end
end

function NativeVendors.init(map)
	if initialized then return end
	initialized = true
	map = map or workspace:WaitForChild("Map")
	local function added(item)
		if item:IsA("ModuleScript") and item.Name == "NativeVendorActors" then bind(item)
		elseif item.Name == "Rig" and item.Parent and item.Parent:IsA("Model") then
			local metadata = item.Parent:FindFirstChild("NativeVendorActors")
			if metadata and metadata:IsA("ModuleScript") then bind(metadata) end
		end
	end
	for _, item in ipairs(map:GetDescendants()) do added(item) end
	connections[#connections + 1] = map.DescendantAdded:Connect(added)
	connections[#connections + 1] = RunService.RenderStepped:Connect(function(dt)
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		local camera = workspace.CurrentCamera
		local observer = if root then root.Position else if camera then camera.CFrame.Position else Vector3.zero
		local t = os.clock()
		for model, binding in pairs(bindings) do
			if not model:IsDescendantOf(workspace) then reset(binding); bindings[model] = nil; continue end
			local head = binding.actors[1].head
			local visible = head.Parent ~= nil and (head.Position - observer).Magnitude <= 150
			if not visible then if binding.visible then reset(binding) end; binding.visible = false; continue end
			binding.visible = true
			local reaction = model:GetAttribute("VendorReaction") or ""
			if reaction ~= binding.reaction then for _, actor in ipairs(binding.actors) do action(actor, reaction) end; binding.reaction = reaction end
			for _, actor in ipairs(binding.actors) do if actor.head.Parent then stepActor(binding, actor, math.min(dt, .1), t, observer) end end
		end
	end)
end

function NativeVendors.destroy()
	for _, connection in ipairs(connections) do connection:Disconnect() end
	for _, binding in pairs(bindings) do reset(binding) end
	table.clear(connections); table.clear(bindings); table.clear(pending); initialized = false
end

return NativeVendors
