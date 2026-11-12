-- StarterPlayerScripts/Client/Footsteps
-- Мягкие шаги по поверхности (трава / камень / дерево), прыжок и приземление.
-- Работает только когда загружены свои звуки шагов (Client/AudioIds); иначе остаются стандартные шаги Roblox.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Sfx = require(script.Parent.Sfx)

local Footsteps = {}

-- по имени материала; всё остальное звучит как камень
local KIND: { [string]: string } = {
	Grass = "grass", LeafyGrass = "grass", Ground = "grass", Mud = "grass", Sand = "grass", Snow = "grass",
	Sandstone = "grass", Fabric = "grass", Wood = "wood", WoodPlanks = "wood",
}

local function kindOf(material: Enum.Material): string
	return KIND[material.Name] or "stone"
end

function Footsteps.init()
	if not (Sfx.has("step_grass") and Sfx.has("step_stone")) then
		return
	end
	local player = Players.LocalPlayer
	local humanoid: Humanoid? = nil
	local root: BasePart? = nil
	local acc = 0
	local fall = 0

	-- стандартные звуки шагов Roblox убираем, чтобы не звучали вдвое
	local function dropDefault(d: Instance)
		if d:IsA("Sound") and (d.Name == "Running" or d.Name == "Jumping" or d.Name == "Landing") then
			d:Destroy()
		end
	end

	local function bind(char: Model)
		local h = char:WaitForChild("Humanoid", 10) :: Humanoid?
		local r = char:WaitForChild("HumanoidRootPart", 10) :: BasePart?
		if not h or not r then
			return
		end
		humanoid, root = h, r
		acc, fall = 0, 0
		for _, d in r:GetChildren() do
			dropDefault(d)
		end
		r.ChildAdded:Connect(dropDefault)
		h.StateChanged:Connect(function(_, new)
			if new == Enum.HumanoidStateType.Jumping then
				Sfx.play("jump")
			end
		end)
	end

	if player.Character then
		task.spawn(bind, player.Character)
	end
	player.CharacterAdded:Connect(function(char)
		task.spawn(bind, char)
	end)

	RunService.Heartbeat:Connect(function(dt)
		local h, r = humanoid, root
		if not h or not r or not r.Parent or h.Health <= 0 then
			return
		end
		local vel = r.AssemblyLinearVelocity
		local flat = Vector3.new(vel.X, 0, vel.Z).Magnitude
		local grounded = h.FloorMaterial ~= Enum.Material.Air
		if grounded and h.MoveDirection.Magnitude > 0.1 and flat > 2 then
			acc += flat * dt
			local stride = math.clamp(flat * 0.19, 2.4, 4.4)
			if acc >= stride then
				acc -= stride
				Sfx.step(kindOf(h.FloorMaterial), math.clamp(0.16 + flat * 0.012, 0.2, 0.38))
			end
		else
			acc = math.min(acc, 1)
		end
		if not grounded then
			fall = math.min(fall, vel.Y)
		else
			if fall < -22 then
				Sfx.play("land", nil, math.clamp(-fall / 120, 0.25, 0.6))
			end
			fall = 0
		end
	end)
end

return Footsteps
