-- ReplicatedStorage/Shared/Net.luau
local RS = game:GetService("ReplicatedStorage")

local Net = {}
local folder = RS:WaitForChild("Remotes")

function Net.ev(name: string): RemoteEvent
	return folder:WaitForChild(name) :: RemoteEvent
end

function Net.fn(name: string): RemoteFunction
	return folder:WaitForChild(name) :: RemoteFunction
end

return Net
