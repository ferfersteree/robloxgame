--!strict
-- Thin, joined cell models for cosmetic hand/flight copies. Six-entry bounded cache.
local HttpService=game:GetService("HttpService")
local Factory={}
local cache={}
local age={}
local tick=0
local PIVOT=Vector3.new(0,4,0)
local data=script.Parent:WaitForChild("ModelsData")

local function build(id: string): Model?
	-- V25: у копий 41-46 пока нет своей модели, они берут вид Пика сингулярности
	local module=data:FindFirstChild(id) or data:FindFirstChild("singularity_spire")
	if not module or not module:IsA("ModuleScript") then return nil end
	local spec=HttpService:JSONDecode(require(module))
	local m=Instance.new("Model");m.Name=id;m:SetAttribute("V15Spear",true);m:SetAttribute("SpearId",id);m:SetAttribute("CubeUnit",.1)
	local pivot=Instance.new("Part");pivot.Name="RuntimePivot";pivot.Size=Vector3.one*.02;pivot.CFrame=CFrame.new(PIVOT);pivot.Transparency=1;pivot.Anchored=true;pivot.CanCollide=false;pivot.CanTouch=false;pivot.CanQuery=false;pivot.CastShadow=false;pivot.Parent=m;m.PrimaryPart=pivot
	for index=1,#spec.parts,11 do
		local p=spec.parts
		local cell=Instance.new("Part");cell.Name="Cell_"..math.floor(index/11+1);cell.Size=Vector3.new(p[index+1],p[index+2],p[index+3]);cell.CFrame=CFrame.new(p[index+4],p[index+5],p[index+6]);cell.Material=Enum.Material.Plastic
		local c=p[index+7];cell.Color=Color3.fromRGB(bit32.band(bit32.rshift(c,16),255),bit32.band(bit32.rshift(c,8),255),bit32.band(c,255))
		cell.Anchored=true;cell.CanCollide=false;cell.CanTouch=false;cell.CanQuery=false;cell.CastShadow=false
		cell.TopSurface=Enum.SurfaceType.Studs;cell.BottomSurface=Enum.SurfaceType.Studs;cell.LeftSurface=Enum.SurfaceType.Studs;cell.RightSurface=Enum.SurfaceType.Studs;cell.FrontSurface=Enum.SurfaceType.Studs;cell.BackSurface=Enum.SurfaceType.Studs;cell.Parent=m
	end
	local function attachment(name: string,point: {number})
		local a=Instance.new("Attachment");a.Name=name;a.Position=Vector3.new(table.unpack(point))-PIVOT;a.Parent=pivot
	end
	attachment("Grip",spec.grip);attachment("Tip",spec.tip);attachment("TipAtt",spec.tip);attachment("GlowAtt",spec.tip);attachment("TrailRoot",spec.attachments.TrailRoot);attachment("TailAtt",{0,.1,0})
	m:SetAttribute("CellCount",#spec.parts/11)
	return m
end

function Factory.Create(id: string): Model?
	tick+=1
	if not cache[id] then
		local model=build(id)
		if not model then return nil end
		cache[id]=model
		local count=0;for _ in pairs(cache)do count+=1 end
		if count>6 then
			local oldest=nil;local stamp=math.huge
			for key,value in pairs(age)do if key~=id and value<stamp then oldest=key;stamp=value end end
			if oldest then cache[oldest]:Destroy();cache[oldest]=nil;age[oldest]=nil end
		end
	end
	age[id]=tick
	return cache[id]:Clone()
end

function Factory.Frame(position: Vector3,direction: Vector3): CFrame
	local up=if direction.Magnitude>.0001 then direction.Unit else Vector3.yAxis
	local right=up:Cross(Vector3.yAxis)
	if right.Magnitude<.0001 then right=Vector3.xAxis end
	right=right.Unit
	return CFrame.fromMatrix(position,right,up,right:Cross(up))
end

function Factory.AtTip(model: Model,tipPosition: Vector3,direction: Vector3): CFrame
	local tip=model.PrimaryPart and model.PrimaryPart:FindFirstChild("TipAtt")
	local localTip=if tip and tip:IsA("Attachment") then tip.Position else Vector3.new(0,3.5,0)
	local rotation=Factory.Frame(Vector3.zero,direction)
	return rotation+tipPosition-rotation:VectorToWorldSpace(localTip)
end

function Factory.AtGrip(model: Model,gripFrame: CFrame): CFrame
	local grip=model.PrimaryPart and model.PrimaryPart:FindFirstChild("Grip")
	local point=if grip and grip:IsA("Attachment") then grip.Position else Vector3.new(0,-1.5,0)
	return gripFrame*CFrame.new(-point)
end

function Factory.Clear()
	for _,model in pairs(cache)do model:Destroy()end
	table.clear(cache);table.clear(age)
end
return Factory
