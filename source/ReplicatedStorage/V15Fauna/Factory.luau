--!strict
-- Client-side editable cube fauna. Old ReplicatedStorage.Animals is preserved.
local HttpService=game:GetService("HttpService")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local Factory={}
local decoded: {[string]: any}={}
local library=script.Parent:WaitForChild("ModelsData")

function Factory.Get(id: string): any?
 if decoded[id] then return decoded[id] end
 local source=library:FindFirstChild(id)
 if not source or not source:IsA("ModuleScript") then return nil end
 local data=HttpService:JSONDecode(require(source))
 decoded[id]=data
 return data
end

local function part(name: string,size: Vector3,cf: CFrame,visible: boolean): Part
 local result=Instance.new("Part")
 result.Name=name;result.Size=size;result.CFrame=cf
 result.Anchored=false;result.CanCollide=false;result.CanTouch=false;result.CanQuery=false;result.Massless=true;result.CastShadow=visible
 if not visible then result.Transparency=1 end
 return result
end

function Factory.Create(id: string): Model?
 local data=Factory.Get(id)
 if not data then return nil end
 local model=Instance.new("Model");model.Name=id
 local oldLibrary=ReplicatedStorage:FindFirstChild("Animals")
 local oldTemplate=oldLibrary and oldLibrary:FindFirstChild(id)
 if oldTemplate then for name,value in pairs(oldTemplate:GetAttributes()) do model:SetAttribute(name,value) end end
 model:SetAttribute("NativeV11",true);model:SetAttribute("NativeV15",true);model:SetAttribute("SpeciesId",id);model:SetAttribute("AssetId",id);model:SetAttribute("Rig",data.rig)
 model:SetAttribute("Height",data.h);model:SetAttribute("BoundsX",data.w);model:SetAttribute("BoundsY",data.h);model:SetAttribute("BoundsZ",data.bounds[2][3]-data.bounds[1][3]);model:SetAttribute("BiomeId",data.zone)
 model:SetAttribute("AnimationState","idle");model:SetAttribute("LocomotionProfile",data.animation.profile);model:SetAttribute("GroundOffsetY",0);model:SetAttribute("VoxelCubeCount",#data.parts/11)
 local rig=Instance.new("Folder");rig.Name="Rig";rig.Parent=model
 local root=part("B001_Root",Vector3.one*.02,CFrame.identity,false);root.Anchored=true;root:SetAttribute("BoneIndex",1);root.Parent=rig;model.PrimaryPart=root
 local actor=part("B002_ActorBody",Vector3.one*.02,CFrame.identity,false);actor:SetAttribute("BoneIndex",2);actor.Parent=rig
 local function joint(child: BasePart,parent: BasePart)
  local motor=Instance.new("Motor6D");motor.Name="Joint";motor.Part0=parent;motor.Part1=child;motor.C0=parent.CFrame:ToObjectSpace(child.CFrame);motor.C1=CFrame.identity;motor.Parent=child
 end
 joint(actor,root)
 local bones={}
 for index,g in ipairs(data.groups) do
  local bone=part(string.format("B%03d_%s",index+2,g.n),Vector3.one*.02,CFrame.new(table.unpack(g.j)),false);bone:SetAttribute("BoneIndex",index+2);bone:SetAttribute("AnatomicalKind",g.kind);bone.Parent=rig;bones[index]=bone
 end
 for index,g in ipairs(data.groups) do joint(bones[index],if g.p>=0 then bones[g.p+1] else actor) end
 local geometry=Instance.new("Model");geometry.Name="Geometry";geometry.Parent=model
 for offset=1,#data.parts,11 do
  local p=data.parts;local group=p[offset]+1;local size=Vector3.new(p[offset+1],p[offset+2],p[offset+3]);local cf=CFrame.new(p[offset+4],p[offset+5],p[offset+6])
  local cell=part("Cell_"..tostring((offset-1)/11+1),size,cf,true);cell.Material=Enum.Material.Plastic
  local color=p[offset+7];cell.Color=Color3.fromRGB(bit32.band(bit32.rshift(color,16),255),bit32.band(bit32.rshift(color,8),255),bit32.band(color,255))
  cell.TopSurface=Enum.SurfaceType.Studs;cell.BottomSurface=Enum.SurfaceType.Studs;cell.LeftSurface=Enum.SurfaceType.Studs;cell.RightSurface=Enum.SurfaceType.Studs;cell.FrontSurface=Enum.SurfaceType.Studs;cell.BackSurface=Enum.SurfaceType.Studs
  cell:SetAttribute("RigidBone",group);cell.Parent=geometry
  local bone=bones[group];local weld=Instance.new("Weld");weld.Name="RigidCube";weld.Part0=bone;weld.Part1=cell;weld.C0=bone.CFrame:ToObjectSpace(cell.CFrame);weld.C1=CFrame.identity;weld.Parent=cell
  if (offset-1)/11%240==239 then task.wait() end
 end
 return model
end
return Factory
