local T={}
local root=workspace.SpearHunt_PetsCollection
local stage=game.ServerStorage:FindFirstChild('PetsQAStaging') or Instance.new('Folder');stage.Name='PetsQAStaging';stage.Parent=game.ServerStorage
local active=nil
local function bounds(m)
 local lo=Vector3.new(math.huge,math.huge,math.huge);local hi=-lo
 for _,p in m.Geometry:GetDescendants()do if p:IsA('BasePart')then
  local cf,sz=p.ExtentsCFrame,p.ExtentsSize
  for _,x in {-1,1}do for _,y in {-1,1}do for _,z in {-1,1}do local v=cf*Vector3.new(x*sz.X/2,y*sz.Y/2,z*sz.Z/2);lo=lo:Min(v);hi=hi:Max(v)end end end
 end end;return (lo+hi)/2,hi-lo
end
local function arr(v)return{v.X,v.Y,v.Z}end
function T.Stage()
 for _,f in root:GetChildren()do for _,m in f:GetChildren()do
  m:SetAttribute('QAOriginalPivot',m:GetPivot());m.Parent=stage
 end end
end
function T.Show(id)
 if active then active.Parent=stage end
 local m=assert(stage:FindFirstChild(id));m:PivotTo(CFrame.identity);m.Parent=root[m:GetAttribute('FamilyId')];active=m
 local center,size=bounds(m);local d=math.max(size.X,size.Y,size.Z)*1.95
 local views={};local function add(name,dir,dist,target)views[#views+1]={name=name,position=arr(target+dir.Unit*dist),target=arr(target)}end
 add('front',Vector3.new(0,.035,-1),d,center)
 add('threeq',Vector3.new(.7,.4,-1),d,center)
 add('side',Vector3.new(1,.06,0),d,center)
 add('rear',Vector3.new(.22,.15,1),d,center)
 add('top',Vector3.new(0,1,.001),d,center)
 local def=game.HttpService:JSONDecode(m.SourceDefinition.Value);local eyes={}
 for _,p in def.parts do if p.name=='FriendlyEye'then table.insert(eyes,Vector3.new(p.cf[1],p.cf[2],p.cf[3]))end end
 if #eyes>0 then local e=Vector3.zero;for _,v in eyes do e+=v end;e/=#eyes
  local w=(eyes[#eyes]-eyes[1]).Magnitude+.8;add('face',Vector3.new(.12,.06,-1),math.max(1.75,w*2),e)
 else add('detail',Vector3.new(.1,.12,-1),d*.62,center+Vector3.new(0,size.Y*.13,-size.Z*.28))end
 return {id=id,center=arr(center),size=arr(size),views=views}
end
function T.Restore()
 if active then active.Parent=stage;active=nil end
 for _,m in stage:GetChildren()do m:PivotTo(m:GetAttribute('QAOriginalPivot'));m:SetAttribute('QAOriginalPivot',nil);m.Parent=root[m:GetAttribute('FamilyId')]end
end
return T
