--!strict
local profiles={}
for biome=1,25 do
 for id,profile in require(script.Parent:FindFirstChild(string.format('Biome%02d',biome))) do profiles[id]=profile end
end
return profiles