local root=workspace.SpearHunt_PetsCollection
local order={'forest','amber','tide','storm','astral'}
local data=game.HttpService:JSONDecode(game.ReplicatedStorage.PetsTools.Catalogue.Value)
local exhibits=workspace:FindFirstChild('PetsExhibition')or Instance.new('Folder');exhibits.Name='PetsExhibition';exhibits.Parent=workspace
for _,v in exhibits:GetChildren()do v:Destroy()end
local function bounds(m)
 local low=Vector3.new(math.huge,math.huge,math.huge);local high=-low
 for _,p in m.Geometry:GetDescendants()do if p:IsA('BasePart')then for _,x in {-1,1}do for _,y in {-1,1}do for _,z in {-1,1}do local v=p.ExtentsCFrame*Vector3.new(x*p.ExtentsSize.X/2,y*p.ExtentsSize.Y/2,z*p.ExtentsSize.Z/2);low=Vector3.new(math.min(low.X,v.X),math.min(low.Y,v.Y),math.min(low.Z,v.Z));high=Vector3.new(math.max(high.X,v.X),math.max(high.Y,v.Y),math.max(high.Z,v.Z))end end end end end
 return (low+high)/2,high-low
end
local families={};local widths={0,0,0};local depths={0,0};local placements={}
for n,id in order do local f={id=id,models={},widths={0,0,0},depths={0,0},name=data.families[id]}
 for _,entry in data.assets do if entry.familyId==id then local m=assert(root[id]:FindFirstChild(entry.id));local center,size=bounds(m);table.insert(f.models,{m=m,entry=entry,center=center,size=size})end end
 assert(#f.models==6)
 for j,r in f.models do local c=(j-1)%3+1;local row=math.floor((j-1)/3)+1;f.widths[c]=math.max(f.widths[c],r.size.X+1.6,4.6);f.depths[row]=math.max(f.depths[row],r.size.Z+2.8,5.3)end
 f.width=2;for _,v in f.widths do f.width+=v end;f.depth=3.3;for _,v in f.depths do f.depth+=v end
 widths[(n-1)%3+1]=math.max(widths[(n-1)%3+1],f.width);depths[math.floor((n-1)/3)+1]=math.max(depths[math.floor((n-1)/3)+1],f.depth);families[n]=f
end
local W=8*4;for _,v in widths do W+=v end;local D=8*3;for _,v in depths do D+=v end
local function part(parent,name,size,pos,col,collide)
 local p=Instance.new('Part');p.Name=name;p.Size=size;p.CFrame=CFrame.new(pos);p.Color=col;p.Material=Enum.Material.SmoothPlastic;p.Anchored=true;p.CanCollide=collide;p.CanTouch=false;p.CanQuery=collide;p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth;p.Parent=parent;return p
end
local function label(parent,name,text,pos,w,h)
 local p=part(parent,name,Vector3.new(w,h,.08),pos,Color3.fromRGB(31,47,64),false);local g=Instance.new('SurfaceGui');g.Name='Label';g.Face=Enum.NormalId.Front;g.LightInfluence=0;g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud;g.PixelsPerStud=90;g.Parent=p
 local t=Instance.new('TextLabel');t.BackgroundTransparency=1;t.Size=UDim2.fromScale(.96,.9);t.Position=UDim2.fromScale(.02,.05);t.Font=Enum.Font.GothamSemibold;t.TextColor3=Color3.fromRGB(246,248,251);t.TextScaled=true;t.TextWrapped=true;t.Text=text;t.Parent=g
end
local floor=workspace.GalleryFloor;floor.Size=Vector3.new(W,.3,D);floor.CFrame=CFrame.new(0,-.15,0);floor.CanCollide=true
local y=-D/2+8
for row=1,2 do local x=-W/2+8
 for col=1,3 do local n=(row-1)*3+col;local f=families[n]
 if f then local sec=Instance.new('Model');sec.Name=f.id;sec:SetAttribute('FamilyId',f.id);sec.Parent=exhibits;local cx=x+widths[col]/2
  part(sec,'SectionFloor',Vector3.new(widths[col],.04,depths[row]),Vector3.new(cx,.02,y+depths[row]/2),Color3.fromRGB(207,214,220),false)
  label(sec,'FamilySign',f.name,Vector3.new(cx,.73,y+.8),widths[col]-.4,1.1)
  local z=y+2.4
  for r=1,2 do local xx=cx-f.width/2+1
   for c=1,3 do local item=f.models[(r-1)*3+c];local sw,sd=f.widths[c],f.depths[r];local px=xx+sw/2;local pz=z+1.2+(sd-2.3)/2
    local target=Vector3.new(px,.65+item.size.Y/2,pz);item.m:PivotTo(CFrame.new(target-item.center)*item.m:GetPivot())
    part(sec,'Plinth_'..item.entry.id,Vector3.new(sw-.3,.65,sd-.35),Vector3.new(px,.325,z+sd/2),Color3.fromRGB(231,235,239),true)
    local text=item.entry.displayName;if item.entry.assetKind=='Pet'then text..=' · '..item.entry.rarityDisplayName end
    label(sec,'Name_'..item.entry.id,text,Vector3.new(px,.96,z+.3),sw-.5,.56)
    local bc,bs=bounds(item.m);placements[item.entry.id]={pivot={item.m:GetPivot():GetComponents()},center={bc.X,bc.Y,bc.Z},size={bs.X,bs.Y,bs.Z}};xx+=sw
   end;z+=f.depths[r]
  end
 end;x+=widths[col]+8
 end;y+=depths[row]+8
end
local spawn=workspace:FindFirstChild('VisitorSpawn')or Instance.new('SpawnLocation');spawn.Name='VisitorSpawn';spawn.Size=Vector3.new(4,.2,4);spawn.CFrame=CFrame.lookAt(Vector3.new(0,.1,-D/2+3),Vector3.new(0,.1,0));spawn.Anchored=true;spawn.Transparency=1;spawn.CanCollide=false;spawn.Duration=0;spawn.Neutral=true;spawn.Parent=workspace
local cam=workspace.CurrentCamera;local target=Vector3.new(0,1,0);cam.FieldOfView=42;cam.Focus=CFrame.new(target);cam.CFrame=CFrame.lookAt(target+Vector3.new(.35,.95,-1).Unit*math.max(W,D)*1.55,target)
return game.HttpService:JSONEncode({count=30,floor={W,D},placements=placements,camera={cam.CFrame:GetComponents()}})
