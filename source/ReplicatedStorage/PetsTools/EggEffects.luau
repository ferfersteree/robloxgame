--!strict
-- Persistent, client-owned egg ambience. No remotes, uploads, opening logic or gameplay.
-- Pool lifecycle and <=90 degree Beam arcs follow the installed roblox-mesh-vfx helpers.
-- Install as ReplicatedStorage.PetsTools.EggEffects. Bootstrap belongs in StarterPlayerScripts.
local RunService = game:GetService('RunService')
local Workspace = game:GetService('Workspace')
local ContentProvider = game:GetService('ContentProvider')

export type Options = { Manual: boolean?, AllowEditPreview: boolean?, ForceLOD: number?, Seed: number? }
export type Handle = {
 Start: (self: Handle) -> Handle,
 Stop: (self: Handle) -> (),
 Destroy: (self: Handle) -> (),
 Step: (self: Handle, time: number, deltaTime: number) -> (),
 GetDiagnostics: (self: Handle) -> {[string]: any},
}
local EggEffects = {} :: any
EggEffects.__index = EggEffects
local active: {[any]: boolean} = {}
local owners: {[Model]: any} = setmetatable({}, {__mode='k'}) :: any
local scheduler: RBXScriptConnection? = nil
local globalQuality = 1
local TAU = math.pi * 2
local PARK = CFrame.new(0,-50000,0)
local TEX = {
 glow='rbxasset://textures/particles/explosion01_implosion_main.dds',
 star='rbxasset://textures/particles/sparkles_main.dds',
 ring='rbxasset://textures/particles/explosion01_shockwave_main.dds',
 spark='rbxasset://textures/particles/fire_sparks_main.dds',
}
local COLORS = {
 forest={Color3.fromRGB(142,217,70),Color3.fromRGB(246,213,102),Color3.fromRGB(70,132,43)},
 amber={Color3.fromRGB(255,167,54),Color3.fromRGB(255,220,123),Color3.fromRGB(185,88,24)},
 tide={Color3.fromRGB(83,215,218),Color3.fromRGB(224,249,244),Color3.fromRGB(65,147,192)},
 storm={Color3.fromRGB(113,202,255),Color3.fromRGB(224,245,255),Color3.fromRGB(77,105,211)},
 astral={Color3.fromRGB(143,111,235),Color3.fromRGB(230,233,255),Color3.fromRGB(245,204,111)},
}
local ALPHA: {NumberSequence} = {}
for i=0,50 do ALPHA[i+1]=NumberSequence.new(i/50) end
local function alphaSequence(value: number): NumberSequence
 return ALPHA[math.clamp(math.floor(value*50+.5),0,50)+1]
end
local function finite(n: number): boolean return n==n and math.abs(n)<1e9 end
local function pulse(t: number, speed: number, phase: number): number return .5+.5*math.sin(t*speed+phase) end
local function sameFrame(a: CFrame,b: CFrame): boolean
 local p=(a.Position-b.Position).Magnitude;local _,angle=a:ToObjectSpace(b):ToAxisAngle()
 return p<1e-5 and math.abs(angle)<1e-4
end
local function colorNear(a: Color3,b: Color3): boolean return math.abs(a.R-b.R)+math.abs(a.G-b.G)+math.abs(a.B-b.B)<.009 end

function EggEffects:_new(className: string, name: string, parent: Instance?): any
 local instance=Instance.new(className);instance.Name=name
 if parent then instance.Parent=parent end
 self.allocated+=1;self.classCounts[className]=(self.classCounts[className] or 0)+1
 return instance
end
function EggEffects:_part(name: string,size: Vector3,color: Color3,shape: string?): BasePart
 local p=self:_new(if shape=='wedge' then 'WedgePart' else 'Part',name,self.folder) :: BasePart
 p.Size=size;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false
 p.Material=Enum.Material.SmoothPlastic;p.Color=color;p.Transparency=1;p.CFrame=PARK
 p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth
 self.visuals[#self.visuals+1]=p
 return p
end
function EggEffects:_attachment(name: string,parent: BasePart,position: Vector3?): Attachment
 local a=self:_new('Attachment',name,parent) :: Attachment
 a.Position=position or Vector3.zero;return a
end
function EggEffects:_node(name: string,position: Vector3?): Attachment return self:_attachment(name,self.holder,position) end
function EggEffects:_emitter(name: string,parent: Instance,texture: string,color: Color3,life: NumberRange,size: number): ParticleEmitter
 local p=self:_new('ParticleEmitter',name,parent) :: ParticleEmitter
 p.Texture=texture;p.Color=ColorSequence.new(color);p.Rate=0;p.Enabled=false
 p.Lifetime=life;p.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,size*.45),NumberSequenceKeypoint.new(.2,size),NumberSequenceKeypoint.new(1,size*.12)})
 p.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.85),NumberSequenceKeypoint.new(.18,.2),NumberSequenceKeypoint.new(.7,.32),NumberSequenceKeypoint.new(1,1)})
 p.Speed=NumberRange.new(0);p.EmissionDirection=Enum.NormalId.Top;p.SpreadAngle=Vector2.new(14,14)
 p.LightEmission=.55;p.LightInfluence=.15;p.Brightness=1.2;p.Orientation=Enum.ParticleOrientation.FacingCamera
 p.Rotation=NumberRange.new(0,360);p.ZOffset=0;p.VelocityInheritance=0
 p:SetAttribute('EmitCount',1);self.emitters[#self.emitters+1]=p;return p
end
function EggEffects:_light(name: string,parent: Instance,color: Color3,range: number): PointLight
 local p=self:_new('PointLight',name,parent) :: PointLight
 p.Color=color;p.Range=math.min(range,3.2);p.Brightness=0;p.Enabled=false;p.Shadows=false
 self.lights[#self.lights+1]=p;return p
end
function EggEffects:_beam(name: string,a: Attachment,b: Attachment,color: Color3,width: number): Beam
 local beam=self:_new('Beam',name,self.holder) :: Beam
 beam.Attachment0=a;beam.Attachment1=b;beam.Color=ColorSequence.new(color);beam.Width0=width;beam.Width1=width*.55
 beam.FaceCamera=true;beam.LightEmission=.65;beam.LightInfluence=.1;beam.Segments=8
 beam.Transparency=alphaSequence(.3);beam.Enabled=false
 self.beams[#self.beams+1]=beam;return beam
end
function EggEffects:_trail(name: string,p: BasePart,color: Color3): Trail
 local a=self:_attachment(name..'_A',p,Vector3.new(-.035,0,0));local b=self:_attachment(name..'_B',p,Vector3.new(.035,0,0))
 local trail=self:_new('Trail',name,p) :: Trail
 trail.Attachment0=a;trail.Attachment1=b;trail.Color=ColorSequence.new(color);trail.Lifetime=.22
 trail.FaceCamera=true;trail.LightEmission=.55;trail.LightInfluence=.15;trail.MinLength=.015
 trail.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.35),NumberSequenceKeypoint.new(1,1)})
 trail.WidthScale=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(1,0)})
 trail.Enabled=false;self.trails[#self.trails+1]=trail;return trail
end
function EggEffects:_arc(name: string,radius: number,width: number,color: Color3): any
 local arc={points={},beams={},radius=radius}
 for i=1,3 do arc.points[i]=self:_node(name..'_P'..i) end
 for i=1,2 do arc.beams[i]=self:_beam(name..'_Beam'..i,arc.points[i],arc.points[i+1],color,width) end
 return arc
end
function EggEffects:_drawArc(arc: any,plane: CFrame,start: number,sweep: number,transparency: number,visible: boolean)
 local step=sweep/2;local curve=(4/3)*math.tan(math.abs(step)/4)*arc.radius
 for i=1,3 do
  local angle=start+step*(i-1)
  local pos=Vector3.new(-arc.radius*math.sin(angle),0,-arc.radius*math.cos(angle))
  local tangent=Vector3.new(-math.cos(angle),0,math.sin(angle))
  arc.points[i].CFrame=plane*CFrame.fromMatrix(pos,tangent,Vector3.yAxis)
 end
 for _,beam in arc.beams do
  beam.CurveSize0=curve;beam.CurveSize1=curve;beam.Transparency=alphaSequence(transparency);beam.Enabled=visible
 end
end
function EggEffects:_place(p: BasePart,frame: CFrame,transparency: number?)
 local tr=transparency or 0;if p.Transparency~=tr then p.Transparency=tr end
 self.moveParts[#self.moveParts+1]=p;self.moveFrames[#self.moveFrames+1]=frame
end
function EggEffects:_emit(key: string,emitter: ParticleEmitter,time: number,period: number,count: number)
 local cycle=math.floor(time/period)
 if self.beats[key]~=cycle then
  self.beats[key]=cycle
  local amount=math.clamp(math.floor(count*self.quality+.5),1,3)
  emitter:Emit(amount);self.emitted+=amount
 end
end
function EggEffects:_anchorLocal(name: string,fallback: Vector3,base: CFrame): Vector3
 local anchor=self.anchors[name]
 if anchor and anchor.Parent then return base:PointToObjectSpace(anchor.WorldPosition) end
 return fallback
end
function EggEffects:_coreBrightness(value: number)
 self.coreLight.Enabled=true;self.coreLight.Brightness=value*self.quality
 if self.rimLight then self.rimLight.Enabled=true;self.rimLight.Brightness=value*.4*self.quality end
end
function EggEffects:_pose(name: string,offset: CFrame)
 local slot=self.motors[name]
 if slot and slot.motor.Parent then
  local frame=slot.base*offset;slot.motor.Transform=frame;slot.last=frame
 end
end
function EggEffects:_releaseMotion()
 for _,slot in self.motors do
  if slot.last and slot.motor.Parent and sameFrame(slot.motor.Transform,slot.last) then slot.motor.Transform=slot.base end
  slot.last=nil
 end
 for _,slot in self.glowParts do
  if slot.part.Parent and slot.last and colorNear(slot.part.Color,slot.last) then slot.part.Color=slot.base end
  slot.last=nil
 end
end
function EggEffects:_hide()
 for _,p in self.visuals do if p.Parent then p.Transparency=1 end end
 for _,p in self.emitters do if p.Parent then p.Enabled=false;p:Clear() end end
 for _,p in self.beams do if p.Parent then p.Enabled=false end end
 for _,p in self.trails do if p.Parent then p.Enabled=false;p:Clear() end end
 for _,p in self.lights do if p.Parent then p.Enabled=false;p.Brightness=0 end end
 self:_releaseMotion()
end

function EggEffects:_buildForest()
 local palette=COLORS.forest;self.fireflies={};self.leaves={}
 for i=1,6 do
  local node=self:_node('UnevenFirefly_'..i)
  local emitter=self:_emitter('FireflyGlint_'..i,node,TEX.glow,if i%3==0 then palette[1] else palette[2],NumberRange.new(.24,.38),.15)
  emitter.LockedToPart=true;emitter.LightEmission=.7;emitter.Brightness=1.4
  self.fireflies[i]={node=node,emitter=emitter,phase=self.rng:NextNumber(0,TAU),speed=self.rng:NextNumber(.38,.73)}
 end
 for i=1,4 do
  local a=self:_part('LooseLeaf_'..i..'_Left',Vector3.new(.14,.035,.30),palette[1],'wedge')
  local b=self:_part('LooseLeaf_'..i..'_Right',Vector3.new(.14,.035,.30),palette[3],'wedge')
  self.leaves[i]={a=a,b=b,phase=self.rng:NextNumber(0,TAU),speed=.19+i*.025}
 end
 self.dust=self:_emitter('QuietRisingPollen',self:_node('PollenBase',Vector3.new(0,-self.height*.42,0)),TEX.glow,palette[2],NumberRange.new(2.2,3.1),.055)
 self.dust.Speed=NumberRange.new(.3,.65);self.dust.SpreadAngle=Vector2.new(45,45);self.dust.Acceleration=Vector3.new(.035,.08,.025);self.dust.LightEmission=.25
end
function EggEffects:_stepForest(t: number,base: CFrame)
 self:_coreBrightness(.25+.16*pulse(t,1.1,.4))
 for i,item in self.fireflies do
  if i<=self.budgetCount(6) then
   local a=item.phase+t*item.speed;local r=self.radius*(1.22+.13*math.sin(a*1.63))
   item.node.Position=Vector3.new(math.cos(a)*r,.25+math.sin(a*1.3+item.phase)*self.height*.33,math.sin(a*.83)*r)
   self:_emit('fly'..i,item.emitter,t+item.phase,.14,1)
  end
 end
 for i,item in self.leaves do
  if i<=self.budgetCount(4) then
   local a=item.phase+t*item.speed;local v=Vector3.new(math.cos(a)*self.radius*1.38,math.sin(a*1.7)*self.height*.34,math.sin(a*.91)*self.radius*1.28)
   local f=base*CFrame.new(v)*CFrame.Angles(math.sin(a)*.38,a*.8,math.sin(a*1.4)*.3)
   self:_place(item.a,f*CFrame.new(-.065,0,0));self:_place(item.b,f*CFrame.new(.065,0,0)*CFrame.Angles(0,math.pi,0))
  end
 end
 self:_emit('pollen',self.dust,t+.43,.8,2)
 self:_pose('Sprout',CFrame.Angles(math.rad(4)*math.sin(t*1.2),math.rad(1.2)*math.sin(t*.65),math.rad(2.6)*math.sin(t*.88)))
end
function EggEffects:_buildAmber()
 self.fragments={};local palette=COLORS.amber
 for i=1,5 do
  local shard=self:_part('FloatingAmber_'..i,Vector3.new(.14+.025*i,.18+.025*i,.13),if i%2==0 then palette[1] else palette[3],'wedge')
  local cap=self:_part('AmberCutFace_'..i,Vector3.new(.10,.025,.10),palette[2])
  self.fragments[i]={part=shard,cap=cap,phase=self.rng:NextNumber(0,TAU),speed=.13+i*.018}
 end
 self.sparks=self:_emitter('RareGoldenSparks',self:_node('WarmInclusions',Vector3.new(0,0,-self.radius*.85)),TEX.star,palette[2],NumberRange.new(.55,1.05),.09)
 self.sparks.Speed=NumberRange.new(.22,.62);self.sparks.SpreadAngle=Vector2.new(105,105);self.sparks.Acceleration=Vector3.new(0,.12,0);self.sparks.Drag=.8
 self.heat=self:_emitter('InnerAmberMotes',self:_node('InnerWarmth',Vector3.new(0,.15,-self.radius*.95)),TEX.glow,palette[1],NumberRange.new(.8,1.4),.06)
 self.heat.Speed=NumberRange.new(.08,.2);self.heat.LightEmission=.35
end
function EggEffects:_stepAmber(t: number,base: CFrame)
 self:_coreBrightness(.34+.18*pulse(t,.82,1.6))
 for i,item in self.fragments do
  if i<=self.budgetCount(5) then
   local a=item.phase+t*item.speed;local r=self.radius*(1.28+.06*math.sin(a*2))
   local pos=Vector3.new(math.cos(a)*r,math.sin(item.phase+t*.24)*self.height*.29,math.sin(a)*r*.88)
   local frame=base*CFrame.new(pos)*CFrame.Angles(t*.17+item.phase,t*.11,math.sin(a)*.35)
   self:_place(item.part,frame);self:_place(item.cap,frame*CFrame.new(0,item.part.Size.Y*.4,-.025),.08)
  end
 end
 self:_emit('gold',self.sparks,t+.25,.72,2);self:_emit('heat',self.heat,t+.56,.94,1)
 self:_pose('CrownCap',CFrame.Angles(0,math.rad(2.4)*math.sin(t*.47),math.rad(.9)*math.sin(t*.63)))
 self:_pose('SunLock',CFrame.Angles(0,0,math.rad(1.6)*math.sin(t*.7)))
end
function EggEffects:_buildTide()
 self.bubbles={};local palette=COLORS.tide
 for i=1,4 do
  local angle=(i-.4)*TAU/4
  local node=self:_node('BubbleLane_'..i,Vector3.new(math.cos(angle)*self.radius*1.15,-self.height*.41,math.sin(angle)*self.radius*1.15))
  local emitter=self:_emitter('PearlBubble_'..i,node,TEX.ring,palette[2],NumberRange.new(2.1+i*.18,2.8+i*.2),.12+i*.026)
  emitter.Speed=NumberRange.new(.38+i*.14,.62+i*.17);emitter.Acceleration=Vector3.new(.025*math.sin(i),.055,.03*math.cos(i))
  emitter.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.06+i*.02),NumberSequenceKeypoint.new(.3,.12+i*.026),NumberSequenceKeypoint.new(1,.20+i*.03)})
  emitter.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.9),NumberSequenceKeypoint.new(.16,.28),NumberSequenceKeypoint.new(.78,.38),NumberSequenceKeypoint.new(1,1)})
  emitter.LightEmission=.25;emitter.Brightness=1.05;emitter.SpreadAngle=Vector2.new(6,6);emitter.Rotation=NumberRange.new(0)
  self.bubbles[i]=emitter
 end
 self.waterArcs={self:_arc('WaterSwishA',self.radius*1.25,.045,palette[1]),self:_arc('WaterSwishB',self.radius*1.32,.035,palette[2])}
end
function EggEffects:_stepTide(t: number,_base: CFrame)
 self:_coreBrightness(.22+.12*pulse(t,.9,.1))
 for i,emitter in self.bubbles do if i<=self.budgetCount(4) then self:_emit('bubble'..i,emitter,t+i*.41,.43+i*.075,1) end end
 for i,arc in self.waterArcs do
  local phase=(t*.34+(i-1)*.5)%1;local visible=phase<.47 and (self.tier==1 or i==1)
  local opacity=if visible then math.sin(phase/.47*math.pi)*.5 else 0
  local plane=CFrame.new(0,-.35+(i-1)*.7,0)*CFrame.Angles(math.rad(12*i),0,math.rad(10*(-1)^i))
  self:_drawArc(arc,plane,-t*.42+i*2,math.rad(115),1-opacity,visible)
 end
 self:_pose('CoralCrown',CFrame.Angles(math.rad(2)*math.sin(t*.63),math.rad(2.3)*math.sin(t*.44),math.rad(1.3)*math.sin(t*.8)))
end
function EggEffects:_buildStorm()
 local palette=COLORS.storm;self.crystalNodes={};self.crystalLights={};self.lightningPoints={};self.lightning={}
 for i=1,4 do
  local p=self:_node('CrystalLight_'..i)
  self.crystalNodes[i]=p;self.crystalLights[i]=self:_light('CrystalPulse_'..i,p,palette[1],1.8)
 end
 for i=1,8 do self.lightningPoints[i]=self:_node('ArcPoint_'..i) end
 for i=1,5 do self.lightning[i]=self:_beam('LightningTrunk_'..i,self.lightningPoints[i],self.lightningPoints[i+1],palette[2],.032) end
 self.lightning[6]=self:_beam('LightningBranchA',self.lightningPoints[3],self.lightningPoints[7],palette[1],.018)
 self.lightning[7]=self:_beam('LightningBranchB',self.lightningPoints[4],self.lightningPoints[8],palette[1],.014)
 self.impulseNode=self:_node('SparkImpulseSource')
 self.impulses=self:_emitter('SharpElectricSparks',self.impulseNode,TEX.spark,palette[2],NumberRange.new(.12,.25),.13)
 self.impulses.Speed=NumberRange.new(2.4,4.5);self.impulses.Drag=5;self.impulses.SpreadAngle=Vector2.new(100,100)
 self.impulses.Orientation=Enum.ParticleOrientation.VelocityParallel;self.impulses.Rotation=NumberRange.new(-90);self.impulses.LightEmission=.8
end
function EggEffects:_stepStorm(t: number,base: CFrame)
 local cycle=math.floor(t/2.25);local phase=t%2.25
 self:_coreBrightness(.14+.08*pulse(t,.9,0))
 for i,node in self.crystalNodes do
  local angle=(i-1)*TAU/4+.35
  local fallback=Vector3.new(math.cos(angle)*self.radius*.72,self.height*(.39+.065*(i%2)),math.sin(angle)*self.radius*.72)
  node.Position=self:_anchorLocal('FX_Crystal_0'..i,fallback,base)
  local k=math.max(0,1-math.abs(phase-(.13+(i-1)*.16))/.105)
  local light=self.crystalLights[i];light.Enabled=true;light.Brightness=(.035+k*.7)*self.quality
 end
 local flash=(phase>.11 and phase<.21) or (phase>.30 and phase<.36)
 local a=self.crystalNodes[cycle%4+1].Position;local b=self.crystalNodes[(cycle+2)%4+1].Position
 for i=1,6 do
  local u=(i-1)/5
  local wobble=if i==1 or i==6 then Vector3.zero else Vector3.new(math.sin(cycle*7+i*13)*.11,math.cos(cycle*5+i*11)*.15,math.sin(cycle*3+i*7)*.1)
  self.lightningPoints[i].Position=a:Lerp(b,u)+wobble+Vector3.new(0,math.sin(u*math.pi)*.35,0)
 end
 self.lightningPoints[7].Position=self.lightningPoints[3].Position+Vector3.new(.26,.35,-.12)
 self.lightningPoints[8].Position=self.lightningPoints[4].Position+Vector3.new(-.24,.21,.15)
 self.impulseNode.Position=self.lightningPoints[3].Position
 for i,beam in self.lightning do beam.Enabled=flash and (self.tier==1 or i<6);beam.Transparency=alphaSequence(if i<6 then .15 else .36) end
 if flash then self:_emit('electric',self.impulses,t,.16,3) end
 self:_pose('CrystalCap',CFrame.Angles(math.rad(.6)*math.sin(t*17)*(if flash then 1 else .1),0,math.rad(.5)*math.sin(t*13)*(if flash then 1 else .1)))
end
function EggEffects:_buildAstral()
 local palette=COLORS.astral;self.orbits={}
 local planes={CFrame.Angles(math.rad(26),0,math.rad(18)),CFrame.Angles(math.rad(-39),math.rad(47),math.rad(-24)),CFrame.Angles(math.rad(71),math.rad(-18),math.rad(21))}
 for i=1,3 do
  local color=if i==3 then palette[3] elseif i==2 then palette[2] else palette[1]
  local starA=self:_part('OrbitStar_'..i..'_Vertical',Vector3.new(.065,.26,.055),color)
  local starB=self:_part('OrbitStar_'..i..'_Cross',Vector3.new(.20,.065,.055),color)
  starA.Material=Enum.Material.Neon;starB.Material=Enum.Material.Neon
  local trail=self:_trail('ShortCometTail_'..i,starA,color)
  local node=self:_node('StarGlints_'..i)
  local emitter=self:_emitter('AstralTwinkle_'..i,node,TEX.star,color,NumberRange.new(.25,.48),.12)
  emitter.LockedToPart=false;emitter.Speed=NumberRange.new(.025,.1);emitter.LightEmission=.65
  self.orbits[i]={a=starA,b=starB,trail=trail,node=node,emitter=emitter,plane=planes[i],radius=self.radius*(1.28+i*.07),phase=i*1.94,speed=if i%2==0 then -.24 else .17+i*.025,
   arc=self:_arc('OrbitWake_'..i,self.radius*(1.28+i*.07),.023,color)}
 end
 self.starDust=self:_emitter('SlowNebulaMotes',self:_node('NebulaBase',Vector3.new(0,-self.height*.28,0)),TEX.glow,palette[1],NumberRange.new(1.4,2.1),.065)
 self.starDust.Speed=NumberRange.new(.12,.25);self.starDust.SpreadAngle=Vector2.new(50,50);self.starDust.LightEmission=.4
end
function EggEffects:_stepAstral(t: number,base: CFrame)
 self:_coreBrightness(.23+.13*pulse(t,.71,2.2))
 for i,item in self.orbits do
  local angle=t*item.speed+item.phase;local pos=item.plane:PointToWorldSpace(Vector3.new(-item.radius*math.sin(angle),0,-item.radius*math.cos(angle)))
  local visible=self.tier==1 or i<3
  if visible then
   local f=base*CFrame.new(pos)*CFrame.Angles(.1*math.sin(t+i),t*.3,item.phase)
   local alpha=.06+.2*pulse(t,1.8+i*.15,item.phase)
   self:_place(item.a,f,alpha);self:_place(item.b,f,alpha)
   item.node.Position=pos;self:_emit('twinkle'..i,item.emitter,t+i*.21,.34+i*.09,1)
  end
  item.trail.Enabled=visible and self.tier==1
  self:_drawArc(item.arc,item.plane,angle-.8,math.rad(42),.72,visible)
 end
 self:_emit('nebula',self.starDust,t+.32,1.0,2)
 self:_pose('OrbitGold',CFrame.Angles(math.rad(3)*math.sin(t*.43),t*.105,math.rad(2)*math.sin(t*.57)))
 self:_pose('OrbitPearl',CFrame.Angles(math.rad(4)*math.sin(t*.36),-t*.084,math.rad(2.5)*math.sin(t*.48)))
 self:_pose('CrownCap',CFrame.Angles(0,math.rad(2.5)*math.sin(t*.51),math.rad(1.1)*math.sin(t*.68)))
end

local BUILDERS={forest=EggEffects._buildForest,amber=EggEffects._buildAmber,tide=EggEffects._buildTide,storm=EggEffects._buildStorm,astral=EggEffects._buildAstral}
local STEPPERS={forest=EggEffects._stepForest,amber=EggEffects._stepAmber,tide=EggEffects._stepTide,storm=EggEffects._stepStorm,astral=EggEffects._stepAstral}
local function stopSchedulerIfIdle()
 if next(active)==nil and scheduler then scheduler:Disconnect();scheduler=nil end
end
local function runScheduler()
 if scheduler then return end
 scheduler=RunService.PreSimulation:Connect(function(dt: number)
  debug.profilebegin('SpearHunt.EggAmbient')
  for effect in active do
   local ok,reason=pcall(EggEffects.Step,effect,effect.age+dt,dt)
   if not ok then effect.lastError=tostring(reason);effect:Stop();warn('EggEffects '..effect.model.Name..': '..tostring(reason)) end
  end
  debug.profileend()
 end)
end
function EggEffects.new(model: Model,options: Options?): Handle
 local opts=options or {}
 assert(RunService:IsClient() or (opts.AllowEditPreview==true and RunService:IsStudio() and not RunService:IsRunning()),'Egg ambience must run on the client')
 assert(model:IsA('Model') and model:GetAttribute('AssetKind')=='Egg','Expected an Egg Model')
 assert(not owners[model],'This model already has an EggEffects owner; destroy it before replacing')
 assert(not model:FindFirstChild('_EggAmbient_Client'),'An old ambient folder exists; destroy its old controller before hot-reloading')
 local family=model:GetAttribute('FamilyId');assert(type(family)=='string' and BUILDERS[family],'Unsupported egg FamilyId')
 local rig=model:FindFirstChild('Rig');local root=if rig then rig:FindFirstChild('Root') else model.PrimaryPart
 assert(root and root:IsA('BasePart'),'Egg requires its existing Rig.Root or PrimaryPart')
 local seed=opts.Seed or ({forest=137,amber=293,tide=421,storm=557,astral=719})[family]
 local height=model:GetAttribute('EggFXHeight');local radius=model:GetAttribute('EggFXRadius');local centerY=model:GetAttribute('EggFXCenterY')
 height=if type(height)=='number' then math.clamp(height,1,12) else 4.8
 radius=if type(radius)=='number' then math.clamp(radius,.35,5) else 1.55
 centerY=if type(centerY)=='number' then math.clamp(centerY,-5,12) else height*.48
 local self=setmetatable({model=model,root=root,options=opts,family=family,height=height,radius=radius,centerY=centerY,
  rng=Random.new(seed),allocated=0,classCounts={},visuals={},emitters={},lights={},beams={},trails={},motors={},anchors={},glowParts={},connections={},
  moveParts={},moveFrames={},beats={},age=0,emitted=0,updates=0,starts=0,running=false,destroyed=false,suspended=false,tier=0,quality=1,
  timeAccumulator=0,lodAccumulator=.3,lastError=nil,glowTick=-1},EggEffects)
 self.folder=self:_new('Folder','_EggAmbient_Client',nil);self.folder:SetAttribute('ClientCosmeticOwner','EggEffects_R2')
 self.folder.Archivable=opts.AllowEditPreview~=true
 local buildOK,buildReason=xpcall(function()
 self.holder=self:_part('AmbientFrame',Vector3.new(.05,.05,.05),Color3.new(1,1,1));self.holder.Transparency=1
 for _,node in model:GetDescendants() do
  if node:IsA('Attachment') and string.sub(node.Name,1,3)=='FX_' then self.anchors[node.Name]=node
  elseif node:IsA('Motor6D') and node.Part1 then self.motors[node.Part1.Name]={motor=node,base=node.Transform,last=nil}
  elseif node:IsA('BasePart') and node:GetAttribute('EggFXGlow')==true then
   if not node:IsA('PartOperation') or node.UsePartColor then
    local sequence=node:GetAttribute('EggFXSequence')
    self.glowParts[#self.glowParts+1]={part=node,base=node.Color,last=nil,sequence=if type(sequence)=='number' then math.clamp(sequence,1,4) else 1}
   end
  end
 end
 local palette=COLORS[family]
 self.coreNode=self:_node('CoreLight',Vector3.new(0,.1,-radius*.72));self.coreLight=self:_light('LocalCoreLight',self.coreNode,palette[1],3.2)
 self.rimNode=self:_node('RimLight',Vector3.new(radius*.7,.35,.15));self.rimLight=self:_light('LocalRimLight',self.rimNode,palette[2],2.2)
 BUILDERS[family](self)
 self.stepFamily=STEPPERS[family]
 self.budgetCount=function(count: number): number return math.max(1,math.floor(count*self.quality+.5)) end
 self:_hide()
 end,debug.traceback)
 if not buildOK then self.folder:Destroy();error(buildReason,0) end
 self.folder.Parent=model;owners[model]=self
 self.connections[1]=model.Destroying:Connect(function() self:Destroy() end)
 self.connections[2]=model.AncestryChanged:Connect(function() if self.running and not model:IsDescendantOf(Workspace) then self:Stop() end end)
 self.connections[3]=model:GetAttributeChangedSignal('EggOpening'):Connect(function()
  if model:GetAttribute('EggOpening')==true then self.suspended=true;self:_hide() end
 end)
 self.connections[4]=self.folder.Destroying:Connect(function() if not self.destroyed then self:Destroy() end end)
 return (self :: any) :: Handle
end
function EggEffects:Start(): Handle
 assert(not self.destroyed,'Cannot start a destroyed effect')
 if self.running then return self end
 assert(self.model:IsDescendantOf(Workspace),'Parent the egg in Workspace before Start')
 self.running=true;self.age=0;self.timeAccumulator=0;self.lodAccumulator=.3;self.tier=0;self.starts+=1
 self.suspended=self.model:GetAttribute('EggOpening')==true;table.clear(self.beats)
 for _,slot in self.motors do slot.base=slot.motor.Transform;slot.last=nil end
 if not self.options.Manual then active[self]=true;runScheduler() end
 self:Step(0,0);return self
end
function EggEffects:Stop()
 if self.destroyed then return end
 self.running=false;active[self]=nil;self:_hide();self.tier=0;stopSchedulerIfIdle()
end
function EggEffects:Step(time: number,dt: number)
 if self.destroyed or not self.running then return end
 assert(finite(time) and finite(dt) and dt>=0,'Step needs finite time and nonnegative dt')
 if not self.model:IsDescendantOf(Workspace) or not self.root.Parent then self:Stop();return end
 self.age=time
 if self.model:GetAttribute('EggOpening')==true then
  if not self.suspended then self.suspended=true;self:_hide() end
  return
 elseif self.suspended then
  self.suspended=false;table.clear(self.beats);self.tier=0;self.lodAccumulator=.3
  for _,slot in self.motors do if slot.motor.Parent then slot.base=slot.motor.Transform end end
 end
 self.lodAccumulator+=dt;self.timeAccumulator+=dt
 if self.lodAccumulator>=.25 or self.tier==0 then
  self.lodAccumulator=0
  local tier=self.options.ForceLOD
  if not tier then
   local camera=Workspace.CurrentCamera;local distance=if camera then (camera.CFrame.Position-self.root.Position).Magnitude else 0
   tier=if distance>190 then 3 elseif distance>62 then 2 else 1
  end
  tier=math.clamp(math.floor(tier),1,3)
  local quality=(if tier==1 then 1 elseif tier==2 then .5 else 0)*globalQuality
  if tier~=self.tier or quality~=self.quality then self:_hide();self.tier=tier;table.clear(self.beats) end
  self.quality=quality
 end
 if self.tier==3 then return end
 local interval=if self.tier==1 and globalQuality>.6 then 1/30 else 1/15
 if dt>0 and self.timeAccumulator<interval then return end
 self.timeAccumulator=0;table.clear(self.moveParts);table.clear(self.moveFrames)
 local center=self.anchors.FX_Center
 local base=if center and center.Parent then center.WorldCFrame else self.root.CFrame*CFrame.new(0,self.centerY,0)
 self.holder.CFrame=base
 local core=self.anchors.FX_Core
 if core and core.Parent then self.coreNode.Position=base:PointToObjectSpace(core.WorldPosition) end
 self.stepFamily(self,time,base)
 local tick=math.floor(time*10)
 if tick~=self.glowTick then
  self.glowTick=tick
  for _,slot in self.glowParts do if slot.part.Parent then
   local strength=if self.family=='storm' then math.max(0,1-math.abs((time%2.25)-(.13+(slot.sequence-1)*.16))/.105)*.2 else .03+.07*pulse(time,.8,slot.sequence)
   local c=slot.base:Lerp(COLORS[self.family][2],strength*self.quality);slot.part.Color=c;slot.last=c
  end end
 end
 if #self.moveParts>0 then Workspace:BulkMoveTo(self.moveParts,self.moveFrames,Enum.BulkMoveMode.FireCFrameChanged) end
 self.updates+=1
end
function EggEffects:Destroy()
 if self.destroyed then return end
 self:Stop();self.destroyed=true
 for _,connection in self.connections do connection:Disconnect() end;table.clear(self.connections)
 if owners[self.model]==self then owners[self.model]=nil end
 self.folder:Destroy()
 table.clear(self.visuals);table.clear(self.emitters);table.clear(self.lights);table.clear(self.beams);table.clear(self.trails)
 table.clear(self.motors);table.clear(self.anchors);table.clear(self.glowParts);table.clear(self.moveParts);table.clear(self.moveFrames)
 self.fireflies=nil;self.leaves=nil;self.fragments=nil;self.bubbles=nil;self.waterArcs=nil;self.crystalNodes=nil;self.crystalLights=nil;self.lightningPoints=nil;self.lightning=nil;self.orbits=nil
 self.dust=nil;self.sparks=nil;self.heat=nil;self.impulses=nil;self.impulseNode=nil;self.starDust=nil
 self.budgetCount=nil;self.stepFamily=nil
end
function EggEffects:GetDiagnostics(): {[string]:any}
 local totalActive=0;for _ in active do totalActive+=1 end
 return {family=self.family,running=self.running,destroyed=self.destroyed,suspended=self.suspended,lod=self.tier,quality=self.quality,time=self.age,
  allocatedInstances=self.allocated,classes=table.clone(self.classCounts),pooledVisualParts=#self.visuals,emitters=#self.emitters,beams=#self.beams,trails=#self.trails,lights=#self.lights,
  starts=self.starts,updates=self.updates,particlesEmitted=self.emitted,ownedConnections=#self.connections,schedulerConnections=if scheduler then 1 else 0,
  automaticEffectsActive=totalActive,lastError=self.lastError}
end
function EggEffects.GetForModel(model: Model): Handle? return owners[model] end
function EggEffects.SetQualityScale(value: number) globalQuality=math.clamp(value,.35,1) end
function EggEffects.Preload(): (boolean,string?)
 local ok,reason=pcall(ContentProvider.PreloadAsync,ContentProvider,{TEX.glow,TEX.star,TEX.ring,TEX.spark})
 return ok,if ok then nil else tostring(reason)
end
return EggEffects
