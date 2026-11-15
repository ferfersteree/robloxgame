--!strict
-- StarterPlayerScripts/SpearHuntEggAmbience. Starts all five eggs during normal Play.
local ReplicatedStorage=game:GetService('ReplicatedStorage')
local Workspace=game:GetService('Workspace')
local tools=ReplicatedStorage:WaitForChild('PetsTools',15)
if not tools then warn('EggEffects: ReplicatedStorage.PetsTools is missing');return end
local source=tools:WaitForChild('EggEffects',15)
if not source or not source:IsA('ModuleScript') then warn('EggEffects: shared module is missing');return end
local EggEffects=require(source)
local alive=true
local collection: Instance?=nil
local globalConnections: {RBXScriptConnection}={}
local collectionConnections: {RBXScriptConnection}={}
local waiting: {[Model]: {RBXScriptConnection}}={}
local handles: {[Model]: any}={}
local pending: {[Model]: boolean}={}

local function unwatch(model: Model)
 local list=waiting[model];waiting[model]=nil
 if list then for _,connection in list do connection:Disconnect() end end
 pending[model]=nil
end
local function remove(model: Model)
 unwatch(model)
 local handle=handles[model];handles[model]=nil
 if handle then handle:Destroy() end
end
local function directAsset(model: Model): boolean
 local parent=model.Parent
 return collection~=nil and parent~=nil and parent.Parent==collection
end
local consider: (Model)->()
local function queue(model: Model)
 if pending[model] or not alive then return end
 pending[model]=true
 task.defer(function()
  pending[model]=nil
  if alive then consider(model) end
 end)
end
consider=function(model: Model)
 if not alive or not directAsset(model) then remove(model);return end
 if handles[model] then return end
 local kind=model:GetAttribute('AssetKind')
 if kind and kind~='Egg' then unwatch(model);return end
 local rig=model:FindFirstChild('Rig');local root=if rig then rig:FindFirstChild('Root') else model.PrimaryPart
 local ready=kind=='Egg' and type(model:GetAttribute('FamilyId'))=='string' and root and root:IsA('BasePart')
  and model:FindFirstChild('SourceDefinition') and not string.find(model.Name,'_Building',1,true)
 if ready then
  unwatch(model)
  local ok,result=pcall(EggEffects.new,model)
  if not ok then warn('EggEffects '..model.Name..': '..tostring(result));return end
  handles[model]=result;result:Start();return
 end
 -- During replication/build, wait on actual object/attribute changes; no polling loop.
 if not waiting[model] then
  waiting[model]={
   model.DescendantAdded:Connect(function() queue(model) end),
   model.AttributeChanged:Connect(function() queue(model) end),
   model:GetPropertyChangedSignal('PrimaryPart'):Connect(function() queue(model) end),
   model:GetPropertyChangedSignal('Name'):Connect(function() queue(model) end),
   model.Destroying:Connect(function() remove(model) end),
  }
 end
end
local function clearCollection()
 for _,connection in collectionConnections do connection:Disconnect() end;table.clear(collectionConnections)
 for model in handles do remove(model) end
 for model in waiting do unwatch(model) end
 collection=nil
end
local function attach(root: Instance)
 if root.Name~='SpearHunt_PetsCollection' or root.Parent~=Workspace or collection==root then return end
 clearCollection();collection=root
 collectionConnections[1]=root.DescendantAdded:Connect(function(instance: Instance)
  if instance:IsA('Model') and directAsset(instance) then queue(instance) end
 end)
 collectionConnections[2]=root.DescendantRemoving:Connect(function(instance: Instance)
  if instance:IsA('Model') and (handles[instance] or waiting[instance]) then remove(instance) end
 end)
 for _,family in root:GetChildren() do for _,model in family:GetChildren() do if model:IsA('Model') then queue(model) end end end
end
globalConnections[1]=Workspace.ChildAdded:Connect(attach)
globalConnections[2]=Workspace.ChildRemoved:Connect(function(instance: Instance) if instance==collection then clearCollection() end end)
local initial=Workspace:FindFirstChild('SpearHunt_PetsCollection');if initial then attach(initial) end
-- Manual graphics settings select a smaller pool budget; Automatic keeps normal distance LOD.
local settingsOK,userSettings=pcall(function() return UserSettings():GetService('UserGameSettings') end)
if settingsOK and userSettings then
 local function applyQuality()
  local value=userSettings.SavedQualityLevel.Value
  EggEffects.SetQualityScale(if value>0 and value<=3 then .5 elseif value>0 and value<=5 then .75 else 1)
 end
 applyQuality();globalConnections[#globalConnections+1]=userSettings:GetPropertyChangedSignal('SavedQualityLevel'):Connect(applyQuality)
end
task.spawn(function()
 local ok,reason=EggEffects.Preload()
 if alive and not ok then warn('EggEffects local texture preload: '..tostring(reason)) end
end)
globalConnections[#globalConnections+1]=script.Destroying:Connect(function()
 alive=false;clearCollection()
 for _,connection in globalConnections do connection:Disconnect() end;table.clear(globalConnections)
end)
