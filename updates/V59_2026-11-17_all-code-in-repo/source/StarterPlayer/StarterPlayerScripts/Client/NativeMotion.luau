--!strict
-- Plays the shared sampled anatomical poses; V16 and V15 libraries coexist.
local RS=game:GetService("ReplicatedStorage")
local NativeMotion={}
local cache={}
local HttpService=game:GetService("HttpService")
local aliases={sleep="idle",look="stand",hop="walk",flee="run",fly="walk",swim="walk",crawl="walk"}
local function prepared(id,model)
 local version=if model:GetAttribute("NativeV16")==true then 16 elseif model:GetAttribute("NativeV15")==true then 15 else 11
 local v15=version>=15
 local cacheKey=if v15 then id.."@"..tostring(version) else id
 if cache[cacheKey] then return cache[cacheKey] end
 local library=RS:FindFirstChild("Animals")
 local source=library and library:FindFirstChild(id)
 local v15Folder=RS:FindFirstChild("V"..tostring(version).."Fauna")
 local dataModule=if v15 then (v15Folder and v15Folder:FindFirstChild("MotionData") and v15Folder.MotionData:FindFirstChild(id)) else (source and source:FindFirstChild("BakedMotion")) or model:FindFirstChild("BakedMotion")
 if not dataModule then return nil end
 local raw=require(dataModule)
 local data=if type(raw)=="string" then HttpService:JSONDecode(raw) else raw
 if v15 then data.clips.stand=data.clips.idle;data.clips.happy=data.clips.idle end
 local function clip(value)
  return {duration=value.duration,frames={},raw=value.frames}
 end
 local result={clips={},transitions={},users=0,id=cacheKey}
 for key,value in pairs(data.clips) do result.clips[key]=clip(value) end
 for key,value in pairs(data.transitions or {}) do result.transitions[key]=clip(value) end
 cache[cacheKey]=result
 return result
end
local function cachedFrame(clip,index)
 local out=clip.frames[index]
 if out then return out end
 out={}
 for j,p in ipairs(clip.raw[index]) do out[j]=CFrame.new(p[1],p[2],p[3],p[4],p[5],p[6],p[7]) end
 clip.frames[index]=out
 return out
end
local function sample(clip,time,looped,into)
 local t=if looped then time%clip.duration else math.clamp(time,0,clip.duration)
 local f=t/clip.duration*(#clip.raw-1)
 local left=math.min(#clip.raw,math.floor(f)+1)
 local right=math.min(#clip.raw,left+1)
 local alpha=f-math.floor(f)
 local pose=into
 local a,b=cachedFrame(clip,left),cachedFrame(clip,right)
 for index,first in ipairs(a) do pose[index]=first:Lerp(b[index],alpha) end
 return pose
end
local function ease(t)
 t=math.clamp(t,0,1)
 return t*t*t*(t*(t*6-15)+10)
end
function NativeMotion.bind(model)
 local rig=model:FindFirstChild("Rig")
 if not rig then return nil end
 local id=model:GetAttribute("SpeciesId") or model.Name
 local data=prepared(id,model)
 if not data then return nil end
 local joints={}
 for _,bone in ipairs(rig:GetChildren()) do
  if bone:IsA("BasePart") then
   local index=bone:GetAttribute("BoneIndex")
   local joint=bone:FindFirstChild("Joint")
   if type(index)=="number" and index>=2 and joint and joint:IsA("Motor6D") then joints[index-1]=joint end
  end
 end
 data.users+=1
 local self={joints=joints,data=data,state="idle",time=0,blend=0,from={},fromScale=model:GetScale(),pose={},transition=nil,pending=nil,model=model,alive=true}
 for index,joint in pairs(joints) do self.from[index]=joint.C0 end
 if model:GetAttribute("NativeV15") then
  local pose=cachedFrame(data.clips.idle,1)
  for index,joint in pairs(joints) do if pose[index] then joint.C0=CFrame.new(pose[index].Position*model:GetScale())*pose[index].Rotation;self.from[index]=joint.C0 end end
 end
 function self:play(state)
  local target=aliases[state] or state
  if not self.data.clips[target] then target="idle" end
  if target==self.state then return end
  self.from={};for index,joint in pairs(self.joints) do self.from[index]=joint.C0 end
  self.fromScale=self.model:GetScale()
  self.blend=0;self.time=0
  if self.state=="idle" and target~="idle" then self.transition=self.data.transitions.rise;self.pending=target
  elseif target=="idle" then self.transition=self.data.transitions.rest;self.pending=target
  else self.transition=nil;self.pending=nil end
  self.state=target
 end
 function self:step(dt,speed)
  if not self.alive or self.model:GetAttribute("AnimationPaused")==true then return end
  local elapsed=math.min(dt,.25)*math.clamp(speed or 1,0,4)
  self.time+=elapsed;self.blend+=elapsed
  local target
  if self.transition then
   target=sample(self.transition,self.time,false,self.pose)
   if self.time>=self.transition.duration then
    self.transition=nil;self.time=0;self.from={};self.blend=0;self.pending=nil
    for index,joint in pairs(self.joints) do self.from[index]=joint.C0 end
    self.fromScale=self.model:GetScale()
   end
  else target=sample(self.data.clips[self.state],self.time,true,self.pose) end
  local weight=ease(self.blend/(if self.transition then .16 else .85))
  local scale=self.model:GetScale()
  for index,joint in pairs(self.joints) do
   local goal=target[index]
   if goal and joint.Parent then
    -- Poses use authoring units; Model:ScaleTo may change during the reveal.
    if scale~=1 then goal=CFrame.new(goal.Position*scale)*goal.Rotation end
    local first=self.from[index]
    if first and scale~=self.fromScale then first=CFrame.new(first.Position*(scale/self.fromScale))*first.Rotation end
    joint.C0=if first then first:Lerp(goal,weight) else goal
   end
  end
 end
 function self:destroy()
  if not self.alive then return end
  self.alive=false;self.data.users-=1
  if self.data.users==0 then cache[self.data.id]=nil end
  self.joints={};self.pose={};self.from={}
 end
 return self
end
return NativeMotion
