--!strict
-- One client scheduler for rigid .5-stud emergence curtains. No scale writes.
local RunService=game:GetService("RunService")
local Motion: any={}
Motion.__index=Motion
local active: {[any]: boolean}={}
local scheduler: RBXScriptConnection?=nil
local function ease(t: number): number t=math.clamp(t,0,1);return t*t*(3-2*t) end
local function idleScheduler()
 if scheduler and next(active)==nil then scheduler:Disconnect();scheduler=nil end
end
local function schedule()
 if scheduler or not RunService:IsClient() then return end
 scheduler=RunService.RenderStepped:Connect(function(dt)
  for controller in pairs(active)do
   if controller.Destroyed or not controller.Root.Parent then active[controller]=nil else controller:Update(dt) end
  end
  idleScheduler()
 end)
end

function Motion.new(root: Model,options: any?): any
 local opts=options or {}
 local self=setmetatable({Root=root,Options=opts,ZoneId=opts.ZoneId or root:GetAttribute("BiomeId")or 1,Style=(root:GetAttribute("OpenStyle")or "curtain"),CoverHeight=(root:GetAttribute("CoverHeight")or 5),Groups={},Parts={},Frames={},State="ready",OpenFraction=0,Elapsed=0,Running=false,Destroyed=false,CurrentLeft=CFrame.identity,CurrentRight=CFrame.identity},Motion)
 local frame=root:GetPivot()
 for id,name in ipairs({"LeftLobe","RightLobe"})do
  local folder=root:FindFirstChild(name)
  local point=root:GetAttribute("GroupPivot"..id)
  local hinge=if typeof(point)=="Vector3"then CFrame.new(point)else CFrame.new(if id==1 then -2.5 else 2.5,.25,0)
  local node={Id=id,Hinge=hinge,Parts={}}
  if folder then for _,p in ipairs(folder:GetDescendants())do if p:IsA("BasePart")then table.insert(node.Parts,{Part=p,Relative=(frame*hinge):ToObjectSpace(p.CFrame),Size=p.Size})end end end
  table.insert(self.Groups,node)
 end
 self.Connection=root.Destroying:Connect(function()
  self.Destroyed=true;self.Running=false;active[self]=nil
  if self.Connection then self.Connection:Disconnect();self.Connection=nil end
  idleScheduler()
 end)
 return self
end

function Motion:_apply(left: CFrame,right: CFrame)
 if self.Destroyed then return end
 self.CurrentLeft=left;self.CurrentRight=right
 table.clear(self.Parts);table.clear(self.Frames)
 local frame=self.Root:GetPivot()
 for _,g in ipairs(self.Groups)do
  local transform=if g.Id==1 then left else right
  for _,saved in ipairs(g.Parts)do if saved.Part.Parent then table.insert(self.Parts,saved.Part);table.insert(self.Frames,frame*g.Hinge*transform*saved.Relative)end end
 end
 if #self.Parts>0 then workspace:BulkMoveTo(self.Parts,self.Frames,Enum.BulkMoveMode.FireCFrameChanged)end
end

function Motion:Rustle(amplitude: number,elapsed: number?)
 if self.Destroyed or self.State=="opening"or self.State=="open"then return end
 self.State="anticipation"
 local t=elapsed or os.clock();local amp=math.clamp(amplitude,0,3)
 local stone=self.ZoneId==6 or self.ZoneId==14 or self.ZoneId==15 or self.ZoneId==16 or self.ZoneId==19 or self.ZoneId==22 or self.ZoneId==24 or self.ZoneId==25
 local style=self.Style
 -- V61: дрожь зависит от того, как куст раскроется: камень и кости дрожат мелко, облака и звёзды парят, створки качаются
 local intensity=if style=="burst" or style=="sink" then .012 elseif style=="swing" then .02 elseif style=="rise" then .05 elseif stone then .012 else .035
 local a=math.sin(t*27)*intensity*amp;local b=math.sin(t*31+.6)*intensity*amp
 self:_apply(CFrame.Angles(0,a*.35,a),CFrame.Angles(0,-b*.35,b))
end

function Motion:Open(duration: number?,spread: number?)
 if self.Destroyed then return end
 self.State="opening";self.Elapsed=0;self.Duration=math.clamp(duration or .7,.2,2)
 self.Spread=math.max(.5,spread or self.Options.Spread or 4.8)
 self.FromLeft=self.CurrentLeft;self.FromRight=self.CurrentRight
 local angle=if self.ZoneId==16 or self.ZoneId==12 or self.ZoneId==15 then .065 else .14
 local style,spread,height=self.Style,self.Spread,self.CoverHeight
 -- V61: пять манер раскрытия. Створки твёрдые и двигаются целиком (кубики не масштабируются):
 --  curtain: разъезжаются в стороны; swing: распахиваются, как двери, вокруг внешнего края (шарнир задан в рисунке);
 --  burst: разлетаются в стороны и назад; sink: уходят под землю; rise: всплывают вверх и расходятся.
 if style=="swing" then
  -- сначала створка отъезжает наружу на долю Spread (широкому зверю нужен проход), затем поворачивается вокруг шарнира
  self.TargetLeft=CFrame.new(-spread*.6,0,0)*CFrame.Angles(0,-1.45,0)
  self.TargetRight=CFrame.new(spread*.6,0,0)*CFrame.Angles(0,1.45,0)
 elseif style=="burst" then
  self.TargetLeft=CFrame.new(-spread*1.5,.6,1.2)*CFrame.Angles(.25,-.7,.55)
  self.TargetRight=CFrame.new(spread*1.5,.6,1.2)*CFrame.Angles(.25,.7,-.55)
 elseif style=="sink" then
  self.TargetLeft=CFrame.new(-spread*.5,-(height+.5),.3)*CFrame.Angles(0,0,.12)
  self.TargetRight=CFrame.new(spread*.5,-(height+.5),.3)*CFrame.Angles(0,0,-.12)
 elseif style=="rise" then
  self.TargetLeft=CFrame.new(-spread*.9,height*1.2+2,-.5)*CFrame.Angles(0,.3,.4)
  self.TargetRight=CFrame.new(spread*.9,height*1.2+2,-.5)*CFrame.Angles(0,-.3,-.4)
 else
  self.TargetLeft=CFrame.new(-self.Spread,0,0)*CFrame.Angles(0,.045,angle)
  self.TargetRight=CFrame.new(self.Spread,0,0)*CFrame.Angles(0,-.045,-angle)
 end
 self.Running=true
 if self.Options.Auto~=false and RunService:IsClient()then active[self]=true;schedule()end
end

function Motion:Update(dt: number)
 if not self.Running or self.Destroyed then return end
 self.Elapsed=math.min(self.Duration,self.Elapsed+math.max(0,math.min(dt,.25)))
 self.OpenFraction=ease(self.Elapsed/self.Duration)
 self:_apply(self.FromLeft:Lerp(self.TargetLeft,self.OpenFraction),self.FromRight:Lerp(self.TargetRight,self.OpenFraction))
 if self.Elapsed>=self.Duration then self.State="open";self.Running=false;active[self]=nil;idleScheduler()end
end

function Motion:Stop()
 if self.Destroyed then return end
 active[self]=nil;self.Running=false;self.State="ready";self.OpenFraction=0;self.Elapsed=0
 self:_apply(CFrame.identity,CFrame.identity);idleScheduler()
end
function Motion:Destroy()
 if self.Destroyed then return end
 self:Stop();self.Destroyed=true
 if self.Connection then self.Connection:Disconnect();self.Connection=nil end
end
return Motion
