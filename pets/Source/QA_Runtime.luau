-- Run once in the Server datamodel during Play. Does not create clips or scripts.
local RunService=game:GetService('RunService')
local HttpService=game:GetService('HttpService')
assert(RunService:IsRunning()and RunService:IsServer(),'Runtime rig check requires Play/Server')
local root=assert(workspace:FindFirstChild('SpearHunt_PetsCollection'))
local rows={};local issues={};local saved={};local totalMotors,totalMounts=0,0
local function errorOf(a,b)local d=a:ToObjectSpace(b);local _,angle=d:ToAxisAngle();return d.Position.Magnitude,math.abs(angle)end
local function waitFrames()for _=1,3 do RunService.Heartbeat:Wait()end end
local function restore(list)for _,r in list do if r.joint.Parent then r.joint.C0=r.c0;r.joint.Transform=r.transform end end end
local function checkAll(m)
 local pe,ae,mounts=0,0,0
 for _,j in m:GetDescendants()do if j:IsA('Weld')or j:IsA('Motor6D')then
  if not j.Part0 or not j.Part1 then table.insert(issues,{id=m.Name,reason='Broken runtime joint '..j.Name})else
   local t=if j:IsA('Motor6D')then j.Transform else CFrame.identity
   local p,a=errorOf(j.Part0.CFrame*j.C0*t,j.Part1.CFrame*j.C1);pe=math.max(pe,p);ae=math.max(ae,a)
   if j:IsA('Weld')then mounts+=1 end
  end
 end end;return pe,ae,mounts
end
local ok,reason=xpcall(function()
 for _,family in root:GetChildren()do for _,m in family:GetChildren()do if m:IsA('Model')then
  local localSaved={};local before={};local r=assert(m.Rig:FindFirstChild('Root'));local rootFrame=r.CFrame
  for _,p in m.Geometry:GetDescendants()do if p:IsA('BasePart')then before[p]=p.CFrame end end
  for _,j in m.Rig:GetDescendants()do if j:IsA('Motor6D')then
   local entry={joint=j,c0=j.C0,transform=j.Transform};table.insert(saved,entry);table.insert(localSaved,entry)
   j.Transform=CFrame.identity;j.C0=j.C0*CFrame.Angles(math.rad(7),math.rad(9),math.rad(5))
  end end
  waitFrames()
  local pe,ae,mounts=checkAll(m);local moved=0;local maxMove=0
  for p,cf in before do local distance,angle=errorOf(cf,p.CFrame);maxMove=math.max(maxMove,distance);if distance>.001 or angle>.001 then moved+=1 end end
  local rootError=errorOf(rootFrame,r.CFrame)
  if pe>.006 or ae>.004 then table.insert(issues,{id=m.Name,reason='Joint/face mount shifted during pose',positionError=pe,angleError=ae})end
  if moved==0 then table.insert(issues,{id=m.Name,reason='No geometry followed posed joints'})end
  if rootError>.001 then table.insert(issues,{id=m.Name,reason='Anchored display root moved'})end
  restore(localSaved);waitFrames()
  local restPe,restAe=checkAll(m);local restMax=0
  for p,cf in before do local distance,angle=errorOf(cf,p.CFrame);restMax=math.max(restMax,distance);if distance>.007 or angle>.004 then table.insert(issues,{id=m.Name,reason='Rest pose not restored',part=p.Name,distance=distance,angle=angle})end end
  totalMotors+=#localSaved;totalMounts+=mounts
  table.insert(rows,{id=m.Name,motorsPosed=#localSaved,rigidMounts=mounts,movingGeometry=moved,maxGeometryDisplacement=maxMove,posedPositionError=pe,posedAngleError=ae,restPositionError=restPe,restAngleError=restAe,restoreDistanceError=restMax})
 end end end
end,debug.traceback)
-- Cleanup also runs if any per-model check failed unexpectedly.
restore(saved);waitFrames()
if not ok then table.insert(issues,{id='runtime',reason=tostring(reason)})end
if #rows~=30 then table.insert(issues,{id='runtime',reason='Expected 30 tested models, got '..#rows})end
return HttpService:JSONEncode({passed=#issues==0,models=rows,issues=issues,motorsPosed=totalMotors,rigidMountsChecked=totalMounts,posesRestored=true,scope='Temporary bounded joint poses only; no animation clips authored'})
