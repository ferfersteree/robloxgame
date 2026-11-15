--!strict
-- Run ONCE via Studio MCP Client execute_luau after the shared module is installed.
-- Uses temporary client-only clones outside the exhibition; existing owners are untouched.
local Workspace=game:GetService('Workspace')
local HttpService=game:GetService('HttpService')
local M=require(game.ReplicatedStorage.PetsTools.EggEffects)
local source=Workspace.SpearHunt_PetsCollection
local fixtures=Instance.new('Folder');fixtures.Name='EggEffects_QA_Fixtures';fixtures.Parent=Workspace
local handles: {any}={};local rows={};local failures={};local motorsChecked=0
local ok,reason=xpcall(function()
 for _,family in source:GetChildren() do
  for _,model in family:GetChildren() do if model:IsA('Model') and model:GetAttribute('AssetKind')=='Egg' then
   local clone=model:Clone();clone.Name=model.Name..'_QA'
   local copiedCosmetics=clone:FindFirstChild('_EggAmbient_Client');if copiedCosmetics then copiedCosmetics:Destroy() end
   clone:PivotTo(CFrame.new(#rows*12,200,0));clone.Parent=fixtures
   local snapshots={};for _,node in clone:GetDescendants() do if node:IsA('Motor6D') then snapshots[node]={c0=node.C0,c1=node.C1,transform=node.Transform};motorsChecked+=1 end end
   local options={Manual=true,ForceLOD=1,Seed=420}
   local h=M.new(clone,options);handles[#handles+1]=h;h:Start()
   local before=h:GetDiagnostics();assert(before.running and before.lod==1)
   local duplicateOK=pcall(M.new,clone,options);assert(not duplicateOK,'Duplicate ownership was accepted')
   for i=1,180 do h:Step(i/30,1/30) end
   local after=h:GetDiagnostics();assert(after.allocatedInstances==before.allocatedInstances,'Pool grew during playback')
   assert(after.updates>30 and after.particlesEmitted>0,'No actual effect updates/emissions')
   for motor,rest in snapshots do assert(motor.C0==rest.c0 and motor.C1==rest.c1,'Ambient changed rig rest C0/C1') end
   local pointCount=0;for _,node in clone._EggAmbient_Client:GetDescendants() do
    if node:IsA('PointLight') then assert(not node.Shadows and node.Range<=3.201);pointCount+=1 end
    if node:IsA('BasePart') then assert(node.Anchored and not node.CanCollide and not node.CanTouch and not node.CanQuery and not node.CastShadow) end
   end
   local foreignMotor=nil;local foreignPose=nil
   for motor,rest in snapshots do
    if motor.Part1 and table.find({'Sprout','CrownCap','SunLock','CoralCrown','CrystalCap','OrbitGold','OrbitPearl'},motor.Part1.Name) then
     foreignMotor=motor;foreignPose=rest.transform*CFrame.Angles(.13,.07,-.09);motor.Transform=foreignPose;break
    end
   end
   clone:SetAttribute('EggOpening',true);h:Step(6.1,.1)
   assert(h:GetDiagnostics().suspended,'EggOpening did not suspend ambient')
   if foreignMotor then
    local offset=foreignPose:ToObjectSpace(foreignMotor.Transform);local _,angle=offset:ToAxisAngle()
    assert(offset.Position.Magnitude<1e-5 and math.abs(angle)<1e-4,'Ambient overwrote a foreign opening pose')
   end
   for _,node in clone._EggAmbient_Client:GetDescendants() do
    if node:IsA('BasePart') then assert(node.Transparency==1,'Opening left pooled decor visible')
    elseif node:IsA('Beam') or node:IsA('Trail') or node:IsA('PointLight') or node:IsA('ParticleEmitter') then assert(not node.Enabled,'Opening left a render layer enabled') end
   end
   for motor,rest in snapshots do motor.Transform=rest.transform end
   clone:SetAttribute('EggOpening',false);h:Step(6.4,.3);assert(not h:GetDiagnostics().suspended)
   options.ForceLOD=3;h:Step(6.8,.4);local far=h:GetDiagnostics();assert(far.lod==3)
   local emittedAtFar=far.particlesEmitted;h:Step(7.2,.4);assert(h:GetDiagnostics().particlesEmitted==emittedAtFar,'Far LOD still emitted particles')
   options.ForceLOD=1;h:Step(7.6,.4);h:Stop();h:Stop()
   for motor,rest in snapshots do
    local offset=rest.transform:ToObjectSpace(motor.Transform);local _,angle=offset:ToAxisAngle()
    assert(offset.Position.Magnitude<1e-5 and math.abs(angle)<1e-4,'Stop did not restore authored motor Transform')
   end
   h:Start();h:Start();h:Step(.5,.5);assert(h:GetDiagnostics().starts==2,'Start was not idempotent')
   local final=h:GetDiagnostics();assert(final.allocatedInstances==before.allocatedInstances)
   h:Destroy();h:Destroy();assert(h:GetDiagnostics().destroyed and h:GetDiagnostics().ownedConnections==0)
   assert(not clone:FindFirstChild('_EggAmbient_Client') and M.GetForModel(clone)==nil)
   local again=M.new(clone,options);handles[#handles+1]=again;again:Start();again:Step(.5,.5);again:Destroy()
   rows[#rows+1]={id=model.Name,family=model:GetAttribute('FamilyId'),allocated=before.allocatedInstances,classes=before.classes,
    steadyUpdates=after.updates,particlesEmitted=after.particlesEmitted,poolStable=true,openingResume=true,farLODCulled=true,restartAndDestroyPassed=true,pointLights=pointCount}
   clone:Destroy()
  end end
 end
 assert(#rows==5,'Expected five thematic eggs')
 -- All automatic handles must share one scheduler and release it after Stop.
 local auto={}
 for i=1,2 do
  local original=source.forest.forest_talisman_egg;local clone=original:Clone()
  local copied=clone:FindFirstChild('_EggAmbient_Client');if copied then copied:Destroy() end
  clone.Name='SchedulerFixture'..i;clone.Parent=fixtures
  local h=M.new(clone,{ForceLOD=1});handles[#handles+1]=h;h:Start();auto[#auto+1]=h
 end
 assert(auto[1]:GetDiagnostics().schedulerConnections==1 and auto[2]:GetDiagnostics().schedulerConnections==1)
 local priorActive=auto[1]:GetDiagnostics().automaticEffectsActive-2
 for _,h in auto do h:Destroy() end
 assert(auto[1]:GetDiagnostics().automaticEffectsActive==priorActive,'Automatic owner leaked from scheduler')
end,debug.traceback)
for _,h in handles do h:Destroy() end
fixtures:Destroy()
if not ok then failures[#failures+1]=tostring(reason) end
return HttpService:JSONEncode({passed=ok and #rows==5,models=rows,issues=failures,motorsChecked=motorsChecked,
 scope='Actual Studio client lifecycle/pool/LOD/rig checks; separate visual motion review required',serverOrExhibitionModelsChanged=false})
