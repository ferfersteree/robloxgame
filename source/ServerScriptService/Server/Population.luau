-- One shared, lightweight population. Clients draw only nearby optimized rigs.
local Run=game:GetService("RunService")
local RS=game:GetService("ReplicatedStorage")
local Config=require(RS.Shared.Config)
local Fauna=require(RS:WaitForChild("Fauna150"))
local Population={}
local function large(sp)
 return sp.rarity>=4 and math.max(Fauna.Attr(sp.id,"BoundsX") or 0,Fauna.Attr(sp.id,"BoundsY") or 0,Fauna.Attr(sp.id,"BoundsZ") or 0)>11
end
local function habitatHome(sp,slot,count,zone,pockets,duplicate)
 local marker=pockets and pockets:FindFirstChild("Spawn_"..sp.id)
 local point=if marker then marker.Position else Vector3.new(35,.15,(Config.FOREST_ORIGIN_Z or -3)-(zone.from+zone.to)*.5)
 local z=point.Z
 if duplicate and zone.id<=16 then
  local margin=math.min(8,(zone.to-zone.from)/3)
  local distance=math.clamp(zone.from+(zone.to-zone.from)*(slot-.5)/count,zone.from+margin,zone.to-margin)
  z=(Config.FOREST_ORIGIN_Z or -3)-distance
 end
 local y=point.Y
 if sp.habitat=="ground" or sp.habitat=="shore" then
  y=Config.GROUND_Y+.03-(Fauna.Attr(sp.id,"MinY") or 0)
 end
 return Vector3.new(point.X,y,z)
end
function Population.start()
 if Population.started then return end;Population.started=true
 local map=workspace:WaitForChild("Map")
 local forest=map:WaitForChild("Forest")
 -- Static previews are for map editing; gameplay uses animated streamed fauna.
 for _,zone in ipairs(forest:GetChildren()) do
  local preview=zone:FindFirstChild("EditorWildlife")
  if preview then preview:Destroy() end
 end
 local folder=Instance.new("Folder");folder.Name="WorldPopulation";folder.Parent=map
 local residents={}
 local now=workspace:GetServerTimeNow()
 for zoneId,zone in ipairs(Config.ZONES) do
  local pool,regular,giants,common={},{},{},{}
  local baseline=math.huge
  for _,sp in ipairs(Config.SPECIES) do
   if sp.zone==zoneId then table.insert(pool,sp);baseline=math.min(baseline,sp.rarity) end
  end
  for _,sp in ipairs(pool) do
   if sp.rarity==baseline then table.insert(common,sp) end
   table.insert(if large(sp) then giants else regular,sp)
  end
  local biome=forest:FindFirstChild("Biome"..zoneId)
  local pockets=biome and biome:FindFirstChild("SpawnPockets")
  local count=math.min(zone.activeCap or 8,10)
  for slot=1,count do
   local isGiant=slot==#regular+1 and #giants>0
   local duplicate=slot>#regular and not isGiant
   local sp=if slot<=#regular then regular[slot] elseif isGiant then giants[1] else common[(slot-1)%#common+1]
   local home=habitatHome(sp,slot,count,zone,pockets,duplicate)
   local anchor=Instance.new("Part");anchor.Name="Resident_"..zoneId.."_"..slot
   anchor.Size=Vector3.new(.1,.1,.1);anchor.Transparency=1;anchor.Anchored=true
   anchor.CanCollide=false;anchor.CanTouch=false;anchor.CanQuery=false;anchor.CastShadow=false
   anchor:SetAttribute("SpeciesId",sp.id);anchor:SetAttribute("Zone",zoneId)
   anchor:SetAttribute("AnimationState","idle");anchor:SetAttribute("AnimationSpeed",1)
   anchor.CFrame=CFrame.new(home);anchor.Parent=folder
   table.insert(residents,{part=anchor,home=home,sp=sp,seed=zoneId*17+slot*3,phase=zoneId*17+slot*3,lastTime=now,t0=now,
    rare=if isGiant then giants else nil,pockets=pockets,slot=slot,count=count,zone=zone,duplicate=duplicate,cycle=-1})
  end
 end
 Population.residents=residents
 local elapsed=0
 Run.Heartbeat:Connect(function(dt)
  elapsed+=dt;if elapsed<.2 then return end;elapsed=0
  local stamp=workspace:GetServerTimeNow()
  for _,r in ipairs(residents) do
   local t=stamp-r.t0+r.seed
   if r.rare and #r.rare>1 then
    local cycle=math.floor(t/60)
    if cycle~=r.cycle then
     r.cycle=cycle;r.sp=r.rare[cycle%#r.rare+1]
     r.home=habitatHome(r.sp,r.slot,r.count,r.zone,r.pockets,false)
     r.part:SetAttribute("SpeciesId",r.sp.id)
    end
   end
   local active=t%24<14
   local scared=(r.part:GetAttribute("FleeUntil") or 0)>stamp
   if active or scared or r.sp.habitat=="air" or r.sp.habitat=="water" then r.phase+=(stamp-r.lastTime)*(if scared then .5 else .12) end
   r.lastTime=stamp
   local a=r.phase
   local radius=math.min(if r.sp.habitat=="air" then 8 elseif r.sp.habitat=="water" then 4 else 3.5,(r.zone.to-r.zone.from)/8)
   local bob=if r.sp.habitat=="air" or r.sp.habitat=="water" then math.sin(a*.7)*.4 else 0
   local p=r.home+Vector3.new(math.sin(a)*radius,bob,math.cos(a)*radius*.7)
   local direction=Vector3.new(math.cos(a),0,-math.sin(a)*.7)
   r.part.CFrame=CFrame.lookAt(p,p+direction)
   local state=if scared then "run" elseif active or r.sp.habitat=="air" or r.sp.habitat=="water" then "walk" else "idle"
   local speed=if scared then 1.6 else 1
   if r.part:GetAttribute("AnimationState")~=state then r.part:SetAttribute("AnimationState",state) end
   if r.part:GetAttribute("AnimationSpeed")~=speed then r.part:SetAttribute("AnimationSpeed",speed) end
  end
 end)
 local fx=RS:WaitForChild("Remotes"):WaitForChild("Fx")
 local rate={}
 fx.OnServerEvent:Connect(function(player,payload)
  if type(payload)~="table" or payload.k~="reveal" or typeof(payload.pos)~="Vector3" then return end
  local p=payload.pos
  if p.X~=p.X or p.Y~=p.Y or p.Z~=p.Z or math.abs(p.X)>150 or math.abs(p.Z)>Config.MAX_THROW_DISTANCE+30 then return end
  local stamp=workspace:GetServerTimeNow()
  if stamp-(rate[player] or 0)<1 then return end;rate[player]=stamp
  for _,r in ipairs(residents) do if (r.part.Position-p).Magnitude<28 then r.part:SetAttribute("FleeUntil",stamp+2.5) end end
 end)
 game.Players.PlayerRemoving:Connect(function(player)rate[player]=nil end)
end
return Population
