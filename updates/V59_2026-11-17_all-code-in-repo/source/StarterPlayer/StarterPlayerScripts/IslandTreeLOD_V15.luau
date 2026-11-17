--!strict
-- Only cosmetic, root-owned island trees. One scheduler; no gameplay changes.
local RunService=game:GetService("RunService")
local Input=game:GetService("UserInputService")
local map=workspace:WaitForChild("Map")
local art=map:WaitForChild("StartIslandV15")
local folder=art:WaitForChild("NativeTreesLOD")
local entries={}
local old={}
for _,model in ipairs(folder:GetChildren())do
 local detail=model:FindFirstChild("Detail")
 local proxy=model:FindFirstChild("Proxy")
 local position=model:GetAttribute("RootPosition")
 if detail and proxy and typeof(position)=="Vector3" then
  local full,low={},{}
  for _,p in ipairs(detail:GetChildren())do if p:IsA("BasePart")then old[p]={p.Transparency,p.LocalTransparencyModifier};p.Transparency=0;p.LocalTransparencyModifier=1;table.insert(full,p)end end
  for _,p in ipairs(proxy:GetChildren())do if p:IsA("BasePart")then old[p]={p.Transparency,p.LocalTransparencyModifier};p.LocalTransparencyModifier=0;table.insert(low,p)end end
  table.insert(entries,{model=model,position=position,detail=full,proxy=low,near=false})
 end
end
local elapsed=0
local connection:RBXScriptConnection?=nil
connection=RunService.Heartbeat:Connect(function(dt)
 elapsed+=dt;if elapsed<.3 then return end;elapsed=0
 local camera=workspace.CurrentCamera;if not camera then return end
 local touch=Input.PreferredInput==Enum.PreferredInput.Touch
 local cap=if touch then 12 else 20
 local radius=if touch then 105 else 135
 local ranked={}
 for _,entry in ipairs(entries)do table.insert(ranked,{entry=entry,distance=(entry.position-camera.CFrame.Position).Magnitude})end
 table.sort(ranked,function(a,b)return a.distance<b.distance end)
 local count=0
 for index,item in ipairs(ranked)do
  local entry=item.entry;local near=index<=cap and item.distance<radius
  if near then count+=1 end
  if near~=entry.near then
   entry.near=near
   for _,part in ipairs(entry.detail)do part.LocalTransparencyModifier=if near then 0 else 1 end
   for _,part in ipairs(entry.proxy)do part.LocalTransparencyModifier=if near then 1 else 0 end
   entry.model:SetAttribute("V15_LOD_Mode",if near then "detail"else "proxy")
  end
 end
 folder:SetAttribute("DetailedTrees",count);folder:SetAttribute("ProxyTrees",#entries-count);folder:SetAttribute("DetailCap",cap)
end)
script.Destroying:Connect(function()
 if connection then connection:Disconnect();connection=nil end
 for part,values in pairs(old)do if part.Parent then part.Transparency=values[1];part.LocalTransparencyModifier=values[2]end end
end)

