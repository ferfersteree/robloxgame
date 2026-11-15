-- Native CSG assets, custom animal/egg joints, no runtime generators or external assets.
local Geometry=game:GetService('GeometryService')
local Http=game:GetService('HttpService')
local Factory={}
local function color(n)return Color3.fromRGB(math.floor(n/65536)%256,math.floor(n/256)%256,n%256)end
local function frame(a)return CFrame.new(table.unpack(a))end
local function properties(p)
 p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth
end
local function primitive(d,base,parent)
 assert(d.s~='ball','R2 anatomy must use authored brick volumes')
 local p=Instance.new(if d.s=='wedge'then'WedgePart'else'Part');if d.s=='cylinder'then p.Shape=Enum.PartType.Cylinder end
 p.Name=d.name
 p.Size=Vector3.new(table.unpack(d.size));p.CFrame=base*frame(d.cf);p.Color=color(d.color)
 p.Material=if d.material=='neon'then Enum.Material.Neon elseif d.material=='glass'then Enum.Material.Glass elseif d.material=='metal'then Enum.Material.Metal else Enum.Material.SmoothPlastic
 p.Transparency=if d.material=='glass'then .22 else 0;p.Reflectance=if d.material=='neon'then 0 else .035
 properties(p);p.Parent=parent;return p
end
function Factory.Build(d,parent,base)
 base=base or CFrame.identity
 local old=parent:FindFirstChild(d.id)
 if old then local backup=game.ServerStorage:FindFirstChild('SpearHunt_PetsBackups')or Instance.new('Folder');backup.Name='SpearHunt_PetsBackups';backup.Parent=game.ServerStorage;local copy=old:Clone();copy.Name=old.Name..'_before_'..tostring(math.floor(os.clock()));copy.Parent=backup end
 local model=Instance.new('Model');model.Name=d.id..'_Building';model.WorldPivot=base
 model:SetAttribute('AssetId',d.id);model:SetAttribute('DisplayName',d.displayName);model:SetAttribute('AssetKind',d.assetKind);model:SetAttribute('FamilyId',d.familyId)
 if d.assetKind=='Pet'then model:SetAttribute('Rarity',d.rarity);model:SetAttribute('RarityDisplayName',d.rarityDisplayName);model:SetAttribute('PetId',d.id)end
 model:SetAttribute('AnimationReady',true);model:SetAttribute('RigType','CustomMotor6D');model:SetAttribute('FrontDirection','-Z');model:SetAttribute('GeometryVersion',d.geometryVersion or 2);model:SetAttribute('SourcePrimitiveCount',#d.parts)
 local geo=Instance.new('Folder');geo.Name='Geometry';geo.Parent=model
 local rig=Instance.new('Folder');rig.Name='Rig';rig.Parent=model
 local root=Instance.new('Part');root.Name='Root';root.Size=Vector3.new(.05,.05,.05);root.CFrame=base;root.Transparency=1;properties(root);root.Parent=rig;model.PrimaryPart=root
 local bones={};local groups={}
 for _,g in d.groups do
  local bone=Instance.new('Part');bone.Name=g.name;bone.Size=Vector3.new(.04,.04,.04);bone.CFrame=base*frame(g.pivot);bone.Transparency=1;properties(bone);bone.Anchored=false;bone.Massless=true;bone:SetAttribute('MotionGroup',g.name);bone.Parent=rig;bones[g.name]=bone
  local attachment=Instance.new('Attachment');attachment.Name='JointPivot';attachment.Parent=bone
  local gm=Instance.new('Model');gm.Name=g.name;gm.WorldPivot=bone.CFrame;gm:SetAttribute('MotionGroup',g.name);gm.Parent=geo;groups[g.name]=gm
 end
 for _,g in d.groups do
  local bone=bones[g.name];local parentBone=if g.parent then assert(bones[g.parent])else root
  local joint=Instance.new('Motor6D');joint.Name=g.name..'_Joint';joint.Part0=parentBone;joint.Part1=bone;joint.C0=parentBone.CFrame:ToObjectSpace(bone.CFrame);joint.C1=CFrame.identity;joint:SetAttribute('RestC0',joint.C0);joint.Parent=bone
 end
 model.Parent=parent
 local count,unions=0,0
 local ok,reason=xpcall(function()
 for _,g in d.groups do
  local mats={}
  for _,p in d.parts do if p.g==g.name then local k=p.material or'plastic';mats[k]=mats[k]or{};table.insert(mats[k],p)end end
  for material,items in mats do
   for first=1,#items,100 do
    local temporary=Instance.new('Folder');local inputs={}
    for n=first,math.min(first+99,#items)do table.insert(inputs,primitive(items[n],base,temporary))end
    temporary.Name='Building_'..g.name;temporary.Parent=model
    local results
    if #inputs==1 then results={inputs[1]}else
     local rest={};for n=2,#inputs do rest[n-1]=inputs[n]end
     local success,value=pcall(function()return Geometry:UnionAsync(inputs[1],rest,{CollisionFidelity=Enum.CollisionFidelity.Box,RenderFidelity=Enum.RenderFidelity.Precise,SplitApart=false})end)
     assert(success,'CSG group '..g.name..': '..tostring(value));results=value
    end
    assert(#results>0,'CSG produced no geometry for '..g.name)
    for _,p in results do
     assert(p:IsA('BasePart') and not p:IsA('MeshPart'),'Expected portable native geometry for '..g.name)
     p.Name=g.name..'_'..material..'_'..first
     if p:IsA('PartOperation')then p.UsePartColor=false;unions+=1 end
     p.Anchored=false;p.Massless=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false
     p.CastShadow=material~='neon';p:SetAttribute('MotionGroup',g.name);p:SetAttribute('SourcePrimitiveCount',math.min(100,#items-first+1));p.Parent=groups[g.name]
     local weld=Instance.new('Weld');weld.Name='RigidMount';weld.Part0=bones[g.name];weld.Part1=p;weld.C0=bones[g.name].CFrame:ToObjectSpace(p.CFrame);weld.C1=CFrame.identity;weld.Parent=p;count+=1
    end
    for _,p in inputs do if p.Parent==temporary then p:Destroy()end end;temporary:Destroy();task.wait()
   end
  end
 end
 end,debug.traceback)
 if not ok then model:Destroy();error(reason,0)end
 local ac=Instance.new('AnimationController');ac.Name='AnimationController';ac.Parent=model;local anim=Instance.new('Animator');anim.Parent=ac
 local source=Instance.new('StringValue');source.Name='SourceDefinition';source.Value=Http:JSONEncode(d);source.Parent=model
 model:SetAttribute('RenderPartCount',count);model:SetAttribute('NativeUnionCount',unions);model:SetAttribute('MotionGroupCount',#d.groups)
 if old then old:Destroy()end;model.Name=d.id
 return {id=d.id,renderParts=count,unions=unions,groups=#d.groups,sourceParts=#d.parts}
end
return Factory
