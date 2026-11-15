-- Read-only edit-time acceptance check; run after the complete exhibition layout.
local HttpService=game:GetService('HttpService')
local root=assert(workspace:FindFirstChild('SpearHunt_PetsCollection'),'Collection missing')
local expected={
 forest={'forest_talisman_egg','clover_beetle','moss_bunny','hazelnut_squirrel','flower_hedgehog','guardian_fawn'},
 amber={'amber_heart_egg','sand_jerboa','amber_armadillo','sun_lion_cub','honey_griffin','amber_basilisk'},
 tide={'tide_pearl_egg','bubble_crab','coral_turtle','pearl_axolotl','tide_ray','little_leviathan'},
 storm={'storm_heart_egg','spark_salamander','cloud_lamb','storm_falcon','storm_dragon','heavenly_kitsune'},
 astral={'astral_core_egg','comet_kitten','moon_owlet','nebula_moth','eclipse_dragon','astral_phoenix'},
}
local issues={};local rows={};local seen={};local totals={models=0,eggs=0,pets=0,renderParts=0,nativeUnions=0,motors=0,welds=0,sourcePrimitives=0}
local function check(ok,id,reason)if not ok then table.insert(issues,{id=id,reason=reason})end end
local function frameError(a,b)
 local delta=a:ToObjectSpace(b);local _,angle=delta:ToAxisAngle();return delta.Position.Magnitude,math.abs(angle)
end
local function bounds(m)
 local lo=Vector3.new(math.huge,math.huge,math.huge);local hi=-lo
 for _,p in m.Geometry:GetDescendants()do if p:IsA('BasePart')then for _,x in {-1,1}do for _,y in {-1,1}do for _,z in {-1,1}do
  -- CSG can retain an offset reference frame; measure its actual geometry box.
  local cf,size=p.ExtentsCFrame,p.ExtentsSize
  local v=cf*Vector3.new(x*size.X/2,y*size.Y/2,z*size.Z/2)
  lo=Vector3.new(math.min(lo.X,v.X),math.min(lo.Y,v.Y),math.min(lo.Z,v.Z));hi=Vector3.new(math.max(hi.X,v.X),math.max(hi.Y,v.Y),math.max(hi.Z,v.Z))
 end end end end end;return lo,hi
end
check(#root:GetChildren()==5,'collection','Expected exactly five family folders')
for family,ids in expected do
 local folder=root:FindFirstChild(family)
 check(folder~=nil,family,'Family missing')
 if folder then
  check(#folder:GetChildren()==6,family,'Expected one egg and five pets')
  for index,id in ids do
   local m=folder:FindFirstChild(id)
   check(m~=nil,id,'Expected Model missing')
   if m and m:IsA('Model')then
    totals.models+=1;local kind=if index==1 then'Egg'else'Pet'
    if kind=='Egg'then totals.eggs+=1 else totals.pets+=1 end
    local aid=m:GetAttribute('AssetId');check(aid==id,id,'AssetId differs from stable catalogue ID');check(not seen[aid],id,'Duplicate stable ID');if aid then seen[aid]=true end
    check(m:GetAttribute('AssetKind')==kind,id,'Wrong AssetKind');check(m:GetAttribute('FamilyId')==family,id,'Wrong FamilyId')
    local name=m:GetAttribute('DisplayName');check(typeof(name)=='string'and #name>0,id,'DisplayName missing')
    if kind=='Pet'then check(typeof(m:GetAttribute('Rarity'))=='string'and #m:GetAttribute('Rarity')>0,id,'Rarity missing');check(m:GetAttribute('PetId')==id,id,'PetId mismatch')end
    check(m:GetAttribute('AnimationReady')==true,id,'AnimationReady missing');check(m:GetAttribute('RigType')=='CustomMotor6D',id,'Custom rig identity missing')
    local rig=m:FindFirstChild('Rig');local geo=m:FindFirstChild('Geometry');local r=rig and rig:FindFirstChild('Root')
    check(r~=nil and r:IsA('BasePart'),id,'Rig.Root missing');check(geo~=nil,id,'Geometry missing')
    local count,unions,motors,welds=0,0,0,0;local maxPositionError,maxAngleError=0,0
    if r then check(m.PrimaryPart==r,id,'PrimaryPart is not Rig.Root');check(r.Anchored,id,'Display root must be anchored');check(r.Transparency==1,id,'Root visible')end
    local ac=m:FindFirstChildOfClass('AnimationController');check(ac~=nil and ac:FindFirstChildOfClass('Animator')~=nil,id,'AnimationController/Animator missing')
    for _,v in m:GetDescendants()do
     check(not v:IsA('Humanoid'),id,'Humanoid found in custom animal rig')
     check(not v:IsA('Script')and not v:IsA('LocalScript'),id,'Unexpected runtime script in asset')
     check(not v:IsA('MeshPart'),id,'Nonportable MeshPart backend found')
     if v:IsA('BasePart')then
      check(not v.CanCollide and not v.CanTouch and not v.CanQuery,id,'Decorative/rig part has collision/query cost')
      if v~=r then check(not v.Anchored and v.Massless,id,'Only root may be anchored; attached parts must be massless')end
      if geo and v:IsDescendantOf(geo)then count+=1;if v:IsA('UnionOperation')then unions+=1 end;check(v:FindFirstChild('RigidMount')~=nil,id,'Geometry missing rigid mount')end
     end
     if v:IsA('Motor6D')or v:IsA('Weld')then
      if v:IsA('Motor6D')then motors+=1;check(typeof(v:GetAttribute('RestC0'))=='CFrame',id,'Joint RestC0 missing')else welds+=1 end
      local a,b=v.Part0,v.Part1;local valid=a~=nil and b~=nil and a:IsDescendantOf(m)and b:IsDescendantOf(m)
      check(valid,id,'Broken/external joint reference')
      if valid then
       local transform=if v:IsA('Motor6D')then v.Transform else CFrame.identity
       local pe,ae=frameError(a.CFrame*v.C0*transform,b.CFrame*v.C1);maxPositionError=math.max(maxPositionError,pe);maxAngleError=math.max(maxAngleError,ae)
       check(pe<.004 and ae<.002,id,'Rest joint/weld equation inconsistent: '..v.Name)
      end
     end
    end
    check(count==m:GetAttribute('RenderPartCount'),id,'RenderPartCount mismatch');check(unions==m:GetAttribute('NativeUnionCount'),id,'NativeUnionCount mismatch')
    check(motors==m:GetAttribute('MotionGroupCount'),id,'MotionGroupCount mismatch');check(welds==count,id,'Geometry mounts not one per render part')
    local source=m:FindFirstChild('SourceDefinition');check(source~=nil,id,'SourceDefinition missing')
    local sourceCount=0;if source then local ok,d=pcall(function()return HttpService:JSONDecode(source.Value)end);check(ok,id,'SourceDefinition invalid JSON');if ok then sourceCount=#d.parts;check(d.id==id,id,'SourceDefinition ID mismatch');check(sourceCount==m:GetAttribute('SourcePrimitiveCount'),id,'SourcePrimitiveCount mismatch')end end
    local floorGap=nil;if geo and count>0 then local lo,hi=bounds(m);local exhibition=workspace:FindFirstChild('PetsExhibition');local section=exhibition and exhibition:FindFirstChild(family);local plinth=section and section:FindFirstChild('Plinth_'..id)
     if plinth then floorGap=lo.Y-(plinth.Position.Y+plinth.Size.Y/2);check(math.abs(floorGap)<.005,id,'Model not resting at plinth height')end
     check(hi.Y>lo.Y,id,'Empty visible bounds')
    end
    totals.renderParts+=count;totals.nativeUnions+=unions;totals.motors+=motors;totals.welds+=welds;totals.sourcePrimitives+=sourceCount
    table.insert(rows,{id=id,kind=kind,family=family,renderParts=count,nativeUnions=unions,motors=motors,welds=welds,sourcePrimitives=sourceCount,maxPositionError=maxPositionError,maxAngleError=maxAngleError,floorGap=floorGap})
   elseif m then check(false,id,'Asset is not a Model')end
  end
 end
end
check(totals.models==30 and totals.eggs==5 and totals.pets==25,'collection','30 model/5 egg/25 pet totals failed')
return HttpService:JSONEncode({passed=#issues==0,totals=totals,models=rows,issues=issues,scope='Read-only native edit model, rig and exhibition checks; visual QA separate'})
