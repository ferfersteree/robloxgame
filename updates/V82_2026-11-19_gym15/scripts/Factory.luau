--!strict
-- Native editable .5-stud cubes. No asset uploads or stretched cells.
local HttpService = game:GetService("HttpService")
local Factory = {}
Factory.Version=15
local dataFolder = script.Parent:WaitForChild("ModelsData")
local decoded = {}
local exposed = {}
local UNIT = .5

function Factory.Get(id: string): any
 if decoded[id] then return decoded[id] end
 local source = dataFolder:FindFirstChild(id)
 if not source or not source:IsA("ModuleScript") then return nil end
 local spec = HttpService:JSONDecode(require(source))
 decoded[id] = spec
 return spec
end

-- V82: ground-cells strip lying in front of each bush (tools/biome_covers.py: v.box(.., 0,0, -5,-4, ground=True))
local function isGroundStrip(v: any): boolean
 return (v[5] or 0)==0 and v[2]==0 and (v[3]==-5 or v[3]==-4)
end

local function surfaceCells(id: string, spec: any): {any}
 if exposed[id] then return exposed[id] end
 local occupied = {}
 local function key(x,y,z) return x..","..y..","..z end
 for _,v in ipairs(spec.voxels) do occupied[key(v[1],v[2],v[3])] = v[5] or 0 end
 local result = {}
 for _,v in ipairs(spec.voxels) do
  local x,y,z,g=v[1],v[2],v[3],v[5] or 0
  if occupied[key(x+1,y,z)]~=g or occupied[key(x-1,y,z)]~=g or occupied[key(x,y+1,z)]~=g or occupied[key(x,y-1,z)]~=g or occupied[key(x,y,z+1)]~=g or occupied[key(x,y,z-1)]~=g then table.insert(result,v) end
 end
 exposed[id] = result
 return result
end

function Factory.CellCount(id: string): number
 local spec=Factory.Get(id)
 return if spec then #surfaceCells(id,spec) else 0
end

function Factory.Create(id: string, cf: CFrame?, parent: Instance?, options: any?): Model?
 local spec=Factory.Get(id)
 if not spec then return nil end
 local frame=cf or CFrame.identity
 -- V61: options.Scale (1..4,5) увеличивает куст целиком: кубики остаются кубиками, просто крупнее (для крупных зверей)
 local scale=if options and type(options.Scale)=="number" then math.clamp(options.Scale,.25,6) else 1
 local unit=UNIT*scale
 local m=Instance.new("Model")
 m.Name=id
 m:SetAttribute("AssetId",id)
 m:SetAttribute("VoxelSize",unit)
 m:SetAttribute("CoverScale",scale)
 m:SetAttribute("CoverHeight",(spec.bounds and spec.bounds.size and spec.bounds.size[2] or 5)*scale)
 m:SetAttribute("OpenStyle",(spec.appearance and spec.appearance.openStyle) or "curtain")
 m:SetAttribute("LogicalVoxelCount",#spec.voxels)
 m:SetAttribute("VegetationVersion",15)
 m:SetAttribute("FrontDirection","-Z")
 m:SetAttribute("BiomeId",spec.biomeId or spec.biomes[1])
 local pivot=Instance.new("Part")
 pivot.Name="Pivot";pivot.Size=Vector3.new(.02,.02,.02);pivot.CFrame=frame;pivot.Transparency=1;pivot.Anchored=true;pivot.CanCollide=false;pivot.CanQuery=false;pivot.CanTouch=false;pivot.CastShadow=false;pivot.Parent=m;m.PrimaryPart=pivot
 local folders={}
 for i,name in ipairs({"Core","LeftLobe","RightLobe"}) do local f=Instance.new("Folder");f.Name=name;f.Parent=m;folders[i-1]=f end
 for _,g in ipairs(spec.groups or {}) do if g.pivot then m:SetAttribute("GroupPivot"..g.id,Vector3.new(table.unpack(g.pivot))*scale) end end
 for name,position in pairs(spec.attachments or {}) do local a=Instance.new("Attachment");a.Name=name;a.Position=Vector3.new(table.unpack(position))*scale;a.Parent=pivot end
 local origin=spec.origin or {0,.25,0}
 local all=options and options.AllCells==true
 local cells0=if all then spec.voxels else surfaceCells(id,spec)
 -- V82: полоса кубиков-«земли» перед кустом (группа 0, y=0, z -5..-4) убрана: остаётся один куст
 local cells={}
 for _,v in ipairs(cells0) do if not isGroundStrip(v) then table.insert(cells,v) end end
 for i,v in ipairs(cells) do
  local p=Instance.new("Part")
  p.Name="Cell_"..i;p.Size=Vector3.new(unit,unit,unit);p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=options and options.CastShadow==true or false;p.Material=Enum.Material.Plastic
  local color=v[4];p.Color=Color3.fromRGB(bit32.band(bit32.rshift(color,16),255),bit32.band(bit32.rshift(color,8),255),bit32.band(color,255))
  p.TopSurface=Enum.SurfaceType.Studs;p.BottomSurface=Enum.SurfaceType.Studs;p.LeftSurface=Enum.SurfaceType.Studs;p.RightSurface=Enum.SurfaceType.Studs;p.FrontSurface=Enum.SurfaceType.Studs;p.BackSurface=Enum.SurfaceType.Studs
  local g=v[5] or 0;p:SetAttribute("VoxelGroupId",g);p:SetAttribute("VoxelGroup",g)
  p.CFrame=frame*CFrame.new((v[1]*UNIT+origin[1])*scale,(v[2]*UNIT+origin[2])*scale,(v[3]*UNIT+origin[3])*scale);p.Parent=folders[g] or folders[0]
  if options and options.Yield and i%192==0 then task.wait() end
 end
 m:SetAttribute("VisibleCellCount",#cells)
 m.Parent=parent
 return m
end

function Factory.CreateCover(zoneId: number, cf: CFrame?, parent: Instance?, options: any?): Model?
 return Factory.Create(string.format("spawn_cover_%02d",math.clamp(math.floor(zoneId),1,25)),cf,parent,options)
end

function Factory.BiomeColors(zoneId: number): (Color3,Color3)
 local spec=Factory.Get(string.format("spawn_cover_%02d",math.clamp(math.floor(zoneId),1,25)))
 local c1,c2=0x67a24a,0x3d753e
 if spec and spec.particleColors then c1=spec.particleColors[1];c2=spec.particleColors[2] or c1 -- V61: цвета брызг заданы в рисунке куста
 elseif spec then c1=spec.voxels[math.max(1,math.floor(#spec.voxels*.55))][4];c2=spec.voxels[math.max(1,math.floor(#spec.voxels*.8))][4] end
 local function color(c) return Color3.fromRGB(bit32.band(bit32.rshift(c,16),255),bit32.band(bit32.rshift(c,8),255),bit32.band(c,255)) end
 return color(c1),color(c2)
end
return Factory
