--!strict
-- Local procedural animation on a copy of the existing art. Rest-space is +Y up,
-- -Z forward. Facial cells and studs are rigidly welded to their anatomical group.
local Motion = {}
local TAU = math.pi * 2
local function smooth(x: number): number
 x=math.clamp(x,0,1); return x*x*(3-2*x)
end
local function pulse(t: number, center: number, width: number): number
 return math.exp(-((t-center)/width)^2)
end
local function angles(x: number,y: number,z: number): CFrame
 return CFrame.Angles(x,y,z)
end
function Motion.Rig(model: Model, profile: any): any
 local base=model:GetPivot();local geometry=assert(model:FindFirstChild('Geometry'))
 local cells={};local anchors={};local sourceGroups={}
 for _,part in geometry:GetDescendants() do
  if part:IsA('BasePart') and not part:GetAttribute('SurfaceRelief') then
   local index=part:GetAttribute('SourcePartIndex');local group=part:GetAttribute('RigidBone')
   if index then sourceGroups[index]=group end
  end
 end
 for _,part in geometry:GetDescendants() do
  if part:IsA('BasePart') then
   local group=part:GetAttribute('RigidBone') or sourceGroups[part:GetAttribute('SourcePartIndex')]
   if not group then
    local container=part.Parent
    while container and container~=geometry do
     local index=container:GetAttribute('AnatomyGroup');if index then group=index+1;break end
     container=container.Parent
    end
   end
   assert(type(group)=='number' and profile.groups[group], 'Unmapped art cell '..part:GetFullName())
   table.insert(cells,{part=part,group=group,rest=base:ToObjectSpace(part.CFrame)})
   part.Anchored=true;part.CanCollide=false;part.CanTouch=false;part.Massless=true
  end
 end
 -- Mutate display copies only. The complete original model and baked clips stay intact.
 for _,v in model:GetDescendants() do if v:IsA('JointInstance') or v:IsA('WeldConstraint') then v:Destroy() end end
 local prior=model:FindFirstChild('Rig');if prior then prior:Destroy() end
 local folder=Instance.new('Folder');folder.Name='Rig';folder.Parent=model
 local function bone(name: string, cf: CFrame): Part
  local p=Instance.new('Part');p.Name=name;p.Size=Vector3.one*.025;p.Transparency=1
  p.Anchored=false;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Massless=true;p.CFrame=cf;p.Parent=folder;return p
 end
 local root=bone('Root',base);root.Anchored=true;model.PrimaryPart=root
 local actor=bone('Actor',base)
 local actorJoint=Instance.new('Motor6D');actorJoint.Name='ActorMotion';actorJoint.Part0=root;actorJoint.Part1=actor;actorJoint.Parent=actor
 local joints={};local rests={};local bind={}
 for i,g in profile.groups do
  local cf=CFrame.new(table.unpack(g.j));bind[i]=cf;anchors[i]=bone(g.n,base*cf)
 end
 for i,g in profile.groups do
  local parent=if g.p>=0 then anchors[g.p+1] else actor
  local rest=(if g.p>=0 then bind[g.p+1] else CFrame.identity):ToObjectSpace(bind[i]);rests[i]=rest
  local motor=Instance.new('Motor6D');motor.Name='Joint';motor.Part0=parent;motor.Part1=anchors[i];motor.C0=rest;motor.Parent=anchors[i];joints[i]=motor
 end
 for i,cell in cells do
  local part=cell.part;local anchor=anchors[cell.group]
  local weld=Instance.new('Weld');weld.Name='RigidArt';weld.Part0=anchor;weld.Part1=part
  weld.C0=bind[cell.group]:ToObjectSpace(cell.rest);weld.Parent=part;part.Anchored=false
  if i%350==0 then task.wait() end
 end
 local controller=model:FindFirstChildOfClass('AnimationController') or Instance.new('AnimationController')
 controller.Name='AnimationController';controller.Parent=model
 if not controller:FindFirstChildOfClass('Animator') then Instance.new('Animator',controller) end
 model:SetAttribute('AnimationSystem','SpearHuntAnatomical150');model:SetAttribute('PreparedAnatomicalGroups',#joints)
 local chains={};local minLength=math.huge
 for i,g in profile.groups do
  if g.role=='leg' then
   local knee=nil;local foot=nil
   for k,c in profile.groups do if c.p==i-1 and c.role=='lower' then knee=k;break end end
   if knee then for k,c in profile.groups do if c.p==knee-1 and c.role=='foot' then foot=k;break end end end
   if knee and foot then
    local hip=bind[i].Position;local kn=bind[knee].Position;local ankle=bind[foot].Position
    local l1=(kn-hip).Magnitude;local l2=(ankle-kn).Magnitude
    if l1>.01 and l2>.01 then table.insert(chains,{upper=i,lower=knee,foot=foot,l1=l1,l2=l2,hip=hip,knee=kn,ankle=ankle});minLength=math.min(minLength,l1+l2) end
   end
  end
 end
 local drop=if minLength<math.huge then minLength*.09 else 0
 local calibratedStride=profile.stride
 for _,chain in chains do
  local reach=math.sqrt(math.max(.001,((chain.l1+chain.l2)*.97)^2-(chain.hip.Y-drop-chain.ankle.Y)^2))
  calibratedStride=math.min(calibratedStride,reach*1.6)
 end
 return {model=model,profile=profile,base=base,root=root,actor=actorJoint,joints=joints,rests=rests,bind=bind,cells=cells,chains=chains,drop=drop,stride=calibratedStride}
end

-- Head actions have separate timing and axes; the collection does not share a
-- single global body rocking curve. Every gesture returns to the rest pose.
local function gesture(p: any,t: number): CFrame
 local period=8+p.cycle*2;local u=t%period;local a=pulse(u,period*.37,.6+p.cycle*.15)
 local b=pulse(u,period*.55,.5);local kind=p.gesture
 if kind=='sniff' then return angles(.10*a+math.sin(u*17)*.018*a,.035*b,0)
 elseif kind=='listen' then return angles(-.035*a,.16*a-.12*b,.045*a)
 elseif kind=='groom' then return angles(.15*a,.12*a,-.05*b)
 elseif kind=='root' then return angles(.16*a,-.10*b,0)
 elseif kind=='yawn' then return angles(-.13*a,0,.025*b)
 elseif kind=='sky' then return angles(-.15*a,.08*b,0)
 elseif kind=='browse' then return angles(.12*a,.14*a-.08*b,0)
 elseif kind=='peck' then return angles(.16*pulse(u,period*.4,.22),-.06*b,0)
 elseif kind=='throat' then return angles(-.045*a,0,.012*math.sin(u*3))
 elseif kind=='hydra' then return angles(.045*math.sin(u*1.3),.12*a-.10*b,0)
 else return angles(.025*a,.13*a-.11*b,.018*b) end
end

function Motion.Pose(p: any,state: string,time: number): (CFrame,{CFrame},CFrame)
 local gs=p.groups;local pose=table.create(#gs,CFrame.identity)
 local moving=state=='Move' or state=='FastMove';local fast=state=='FastMove'
 local cycle=p.cycle*(if fast then .70 else 1);local q=time/cycle
 local phase=q%1;local w=q*TAU
 local stride=p.stride*(if fast then 1.60 else 1)
 local actor=CFrame.identity;local root=CFrame.identity
 local head=gesture(p,time)
 local lift=math.min(p.height*.10,p.length*.09)*(if fast then 1.7 else 1)
 local bodyTilt=if fast then -.065 else 0
 local gait=p.gait
 if moving then
  if p.mode=='hop' or gait=='bound' then
   -- Clear compression, push-off, flight and landing phases, rather than a sine bounce.
   local flight=math.clamp((phase-.20)/.60,0,1)
   local y=if phase<.20 then -.035*p.height*math.sin(phase/.20*math.pi) elseif phase<.80 then lift*3.0*math.sin(flight*math.pi) else -.025*p.height*math.sin((phase-.80)/.20*math.pi)
   actor=CFrame.new(0,math.max(0,y),0)*angles(bodyTilt+.12*math.sin(w),0,0)
  elseif p.mode=='air' then
   actor=CFrame.new(0,lift*.45*math.sin(w),0)*angles(bodyTilt,0,.025*math.sin(w*.5))
  elseif p.mode=='water' then
   actor=CFrame.new(0,lift*.25*math.sin(w),0)*angles(bodyTilt*.7,.025*math.sin(w),.025*math.sin(w))
  elseif gait=='serpent' or gait=='slug' or gait=='leech' then
   actor=CFrame.new(.025*p.length*math.sin(w),.008*p.height*(1-math.cos(w*2)),0)*angles(0,.035*math.sin(w),0)
  else
   actor=CFrame.new(0,lift*.20*(1-math.cos(w*2)),0)*angles(bodyTilt+.012*math.sin(w*2),0,.012*math.sin(w))
  end
  local distance=time*stride/cycle
  root=if gait=='side' then CFrame.new(distance,0,0) else CFrame.new(0,0,-distance)
 end
 local tailIndex=0;local armIndex=0
 for i,g in gs do
  local role=g.role;local side=g.side or 0;local offset=CFrame.identity
  if role=='head' or role=='neck' then
   offset=if role=='neck' then CFrame.identity:Lerp(head,.35) else head
   if moving then offset=offset*angles(-bodyTilt*.65,.015*math.sin(w+g.j[2]),0) end
   if p.gesture=='hydra' then offset=offset*angles(.03*math.sin(time+i),.07*math.sin(time*.7+i*2),0) end
  elseif role=='body' then
   -- Breathing stays subtle and local, with no scaling of the assembled artwork.
   offset=if moving then CFrame.identity else CFrame.new(0,.003*p.height*math.sin(time*TAU/(3+p.cycle)),0)
  elseif role=='leg' then
   local ph=(phase+(g.phase or 0))%1
   if fast then
    if gait=='diagonal' or gait=='amble' then ph=(phase+(if (g.order or 0)==0 then .48 else 0)+side*.06)%1 end
    if gait=='lateral' then ph=(phase+(g.phase or 0)*.82)%1 end
   end
   if moving then
    if p.mode=='air' then offset=angles(.28,0,-side*.06)
    elseif p.mode=='water' then offset=angles(.18*math.sin(w+(g.phase or 0)*TAU),side*.10*math.cos(w),side*.16)
    elseif p.mode=='hop' or gait=='bound' then offset=angles(.30*math.sin(w+(if (g.order or 0)==0 then .8 else -.2)),0,side*.018)
    else
     local duty=if fast then .48 else .68
     local swing=if ph<duty then 1-2*ph/duty else -math.cos((ph-duty)/(1-duty)*math.pi)
     local span=math.min(.42,stride/math.max(.5,g.j[2]^2+g.j[1]*3)*.38)
     offset=angles(span*swing,0,side*.015*math.sin(ph*TAU))
    end
   end
  elseif role=='lower' then
   local parent=gs[g.p+1];local ph=(phase+(parent and parent.phase or 0))%1
   if moving and p.mode~='water' and p.mode~='air' then
    local s=math.max(0,math.sin((ph-.65)/.35*math.pi))
    if ph<.65 then s=0 end
    offset=angles(-.45*s*(if fast then 1.35 else 1),0,0)
   end
  elseif role=='foot' then
   if moving and p.mode=='ground' then offset=angles(-.055*math.sin(w),0,0) end
  elseif role=='wing' then
   if p.mode=='air' then
    local amplitude=if gait=='soar' or gait=='glide' then .10 else .39
    if fast then amplitude*=.72 end
    local flap=math.sin(w+(if g.n:lower():find('hind') then .6 else 0))
    offset=angles(.05*(if fast then -1 else 1),side*.03,side*(amplitude*flap+(if fast then .12 else .02)))
   elseif p.mode=='water' then offset=angles(.04*math.cos(w),0,side*.16*math.sin(w+g.j[2]*.4))
   elseif not moving then offset=angles(0,0,side*.025*pulse(time%(9+p.cycle),4,.7)) end
  elseif role=='tail' then
   tailIndex+=1
   local amplitude=if gait=='fish' or gait=='serpent' or gait=='ribbon' or gait=='undulate' then .12 else .035
   local wave=(if moving then w else time*.65)-tailIndex*.48
   if fast then amplitude*=1.6 end
   offset=angles(if gait=='leech' then .035*math.sin(w-tailIndex*.4) else .012*math.sin(wave),amplitude*math.sin(wave),0)
   if gait=='paddle' then offset=angles(.10*math.sin(wave),.025*math.sin(wave),0) end
  elseif role=='arm' then
   armIndex+=1
   if moving and p.mode=='ground' then offset=angles(-.14*math.sin(w+(if side<0 then 0 else math.pi)),0,side*.025)
   elseif p.mode=='water' then offset=angles(.06*math.sin(w-i*.5),.06*math.cos(w-i*.5),side*.05)
   else offset=angles(-.06*pulse(time%(8+p.cycle),3+armIndex*.2,.6),side*.035,side*.03) end
  elseif role=='tentacle' then
   offset=angles(.05*math.sin((if moving then w else time*.7)-i*.5),.035*math.cos(time-i*.4),side*.035*math.sin(time*.8-i*.4))
  elseif role=='valve' then
   offset=angles(0,0,side*(.025+.035*(1+math.sin(time*.7))))
  elseif role=='accent' then
   local n=g.n:lower()
   if n:find('ear') or n:find('antenna') then offset=angles(.025*math.sin(time*2+i),side*.07*pulse(time%7,3+i*.07,.2),0)
   elseif n:find('quill') then offset=angles(.015*math.sin(time*.7+i*.4),0,side*.012)
   elseif n:find('lure') then offset=angles(.055*math.sin(time*1.3),.04*math.cos(time),0)
   elseif n:find('gill') then offset=angles(0,0,side*.055*math.sin(time*1.7+i))
   else offset=angles(.06*math.sin(time*.8),.035*math.sin(time*.5),0) end
  end
  pose[i]=offset
 end
 if state=='Spawn' then
  local u=math.clamp(time/p.revealDuration,0,1)
  local enter=smooth(u/.65);local settle=1-smooth((u-.65)/.35)
  -- Species choreography is encoded as separate trajectories, body poses and accents.
  local reveal=p.reveal;local y=0;local yaw=0;local pitch=0;local roll=0;local z=0;local x=0
  local hops=reveal:find('three') and 3 or reveal:find('two') and 2 or 1
  if p.mode=='hop' then
   local h=math.max(0,math.sin(math.min(u/.70,1)*math.pi*hops));y=h*p.height*.35*(1-u*.7);z=p.length*.55*(1-enter);pitch=.12*math.sin(u*math.pi*2)*settle
  elseif p.mode=='air' then
   y=(1-enter)*p.height*1.4;z=(1-enter)*p.length*1.7;x=math.sin(u*math.pi)*p.length*.28
   roll=.18*math.sin(u*TAU)*settle;pitch=-.12*math.sin(u*math.pi)*settle
  elseif p.mode=='water' then
   y=.20*p.height*math.sin(u*math.pi);z=(1-enter)*p.length*1.2;yaw=.22*math.sin(u*TAU)*settle
  elseif p.mode=='rooted' then pitch=.10*(1-enter)
  else z=p.length*.45*(1-enter);pitch=.06*math.sin(u*TAU)*settle end
  if reveal:find('coil') or reveal:find('spiral') or reveal:find('orbit') then yaw+=.42*math.sin(u*math.pi)*settle;x+=.20*p.length*math.sin(u*TAU)*settle end
  if reveal:find('bow') or reveal:find('snout') or reveal:find('root') then pitch+=.13*pulse(u,.45,.18)*settle end
  if reveal:find('shake') or reveal:find('shiver') then roll+=.055*math.sin(u*TAU*4)*pulse(u,.52,.20) end
  if reveal:find('rise') or reveal:find('wake') or reveal:find('stand') or reveal:find('unfold') or reveal:find('unroll') then pitch+=.14*(1-enter) end
  if reveal:find('peek') or reveal:find('search') or reveal:find('inspect') then yaw+=.18*(pulse(u,.32,.09)-pulse(u,.52,.09)) end
  if reveal:find('brake') or reveal:find('stop') or reveal:find('skid') then pitch-=.09*pulse(u,.47,.16);z+=.16*p.length*pulse(u,.32,.17) end
  actor=CFrame.new(x,y,z)*angles(pitch,yaw,roll)
  for i,g in gs do
   local accent=CFrame.identity;local name=g.n:lower()
   if g.role=='wing' then accent=angles(-.05*pulse(u,.45,.19),0,g.side*.40*pulse(u,.35,.22)*settle)
   elseif g.role=='arm' then accent=angles(-.23*pulse(u,.45,.22)*settle,g.side*.08*settle,g.side*.10*settle)
   elseif g.role=='head' then accent=angles(-.10*pulse(u,.62,.18)*settle,.12*math.sin(u*TAU)*settle,0)
   elseif g.role=='tail' then accent=angles(.08*math.sin(u*math.pi)*settle,.12*math.sin(u*TAU-i*.3)*settle,0)
   elseif g.role=='valve' then accent=angles(0,0,-g.side*.18*(1-enter))
   elseif g.role=='tentacle' then accent=angles(.20*(1-enter)*math.sin(i),0,g.side*.10*(1-enter))
   elseif g.role=='leg' then accent=angles(.14*math.sin(u*TAU*2+(g.phase or 0)*TAU)*settle,0,0)
   elseif name:find('quill') then accent=angles(.07*pulse(u,.5,.2)*settle,0,0) end
   -- The endpoint is exactly Idle at t=0, ensuring a defined handoff.
   pose[i]=pose[i]:Lerp(CFrame.identity,smooth((u-.82)/.18))*accent
  end
  if u>=1 then local idleActor,idlePose=Motion.Pose(p,'Idle',0);return idleActor,idlePose,CFrame.identity end
 end
 return actor,pose,root
end

function Motion.Bind(model: Model,profile: any): any
 local rig=Motion.Rig(model,profile)
 local self={rig=rig,state='Idle',time=0,rate=1,paused=false,travel=false,distance=0,speed=0,blend=1,from={},fromActor=CFrame.identity,current={},currentActor=CFrame.identity}
 for i in profile.groups do self.current[i]=CFrame.identity end
 function self:Play(state: string): ()
  assert(state=='Idle' or state=='Move' or state=='FastMove' or state=='Spawn','Invalid state')
  if state=='FastMove' and not profile.fast then return end
  self.from=table.clone(self.current);self.fromActor=self.currentActor;self.blend=0;self.time=0;self.state=state
 end
 function self:Step(dt: number): ()
  if self.paused then return end
  local elapsed=math.clamp(dt,0,.1)*self.rate;self.time+=elapsed;self.blend=math.min(1,self.blend+elapsed/.30)
  if self.state=='Spawn' and self.time>=profile.revealDuration then self:Play('Idle') end
  local actor,pose,root=Motion.Pose(profile,self.state,self.time)
  -- Analytic two-link support for existing anatomical knee/ankle chains.
  -- Sole orientation remains level during stance. No humanoid rig is imposed.
  if (self.state=='Move' or self.state=='FastMove') and profile.mode=='ground' and #rig.chains>0 then
   actor=CFrame.new(0,-rig.drop,0)*actor
   local frames={};local function rebuild(): ()
    for i,g in profile.groups do frames[i]=(if g.p>=0 then frames[g.p+1] else actor)*rig.rests[i]*pose[i] end
   end
   local function rotationBetween(a: Vector3,b: Vector3): CFrame
    local av=a.Unit;local bv=b.Unit;local cross=av:Cross(bv);local dot=math.clamp(av:Dot(bv),-1,1)
    if cross.Magnitude<1e-6 then return CFrame.identity end
    return CFrame.fromAxisAngle(cross.Unit,math.acos(dot))
   end
   rebuild()
   local fast=self.state=='FastMove';local cycle=profile.cycle*(if fast then .70 else 1)
   local duty=if fast then .48 else .68
   local step=rig.stride
   for _,chain in rig.chains do
    local g=profile.groups[chain.upper];local ph=(self.time/cycle+(g.phase or 0))%1
    local hip=frames[chain.upper].Position
    local z=if ph<duty then -.5+ph/duty else .5-(smooth((ph-duty)/(1-duty)))
    local lift=if ph<duty then 0 else math.sin((ph-duty)/(1-duty)*math.pi)*math.min(chain.l1,chain.l2)*.28
    local reach=math.sqrt(math.max(0,((chain.l1+chain.l2)*.985)^2-(hip.Y-chain.ankle.Y)^2))
    local stride=math.min(step,reach*1.8)
    local target=chain.ankle+Vector3.new(0,lift,z*stride*duty)
    local delta=target-hip;local d=math.clamp(delta.Magnitude,math.abs(chain.l1-chain.l2)+.001,chain.l1+chain.l2-.001)
    local direction=delta.Unit;target=hip+direction*d
    local along=(chain.l1^2-chain.l2^2+d*d)/(2*d)
    local perpendicular=Vector3.new(0,0,1)-direction*direction:Dot(Vector3.new(0,0,1))
    if perpendicular.Magnitude<1e-5 then perpendicular=Vector3.new(0,1,0):Cross(direction) end
    perpendicular=perpendicular.Unit
    local restBend=chain.knee-(chain.hip+chain.ankle)*.5
    if restBend:Dot(perpendicular)<0 then perpendicular=-perpendicular end
    local knee=hip+direction*along+perpendicular*math.sqrt(math.max(0,chain.l1^2-along^2))
    local upperRot=rotationBetween(chain.knee-chain.hip,knee-hip)
    local lowerRot=rotationBetween(chain.ankle-chain.knee,target-knee)
    local parent=if g.p>=0 then frames[g.p+1] else actor
    local upperWorld=CFrame.new(hip)*upperRot
    local lowerWorld=CFrame.new(knee)*lowerRot
    local footWorld=CFrame.new(target)
    pose[chain.upper]=rig.rests[chain.upper]:Inverse()*parent:ToObjectSpace(upperWorld)
    pose[chain.lower]=rig.rests[chain.lower]:Inverse()*upperWorld:ToObjectSpace(lowerWorld)
    pose[chain.foot]=rig.rests[chain.foot]:Inverse()*lowerWorld:ToObjectSpace(footWorld)
    rebuild()
   end
  end
  local weight=smooth(self.blend)
  self.currentActor=self.fromActor:Lerp(actor,weight);rig.actor.C0=self.currentActor
  for i,joint in rig.joints do local value=(self.from[i] or CFrame.identity):Lerp(pose[i],weight);self.current[i]=value;joint.C0=rig.rests[i]*value end
  -- Continuous world distance survives state changes; the circular track has
  -- neither teleporting loop resets nor an accumulating second root offset.
  local moving=self.state=='Move' or self.state=='FastMove'
  local cycle=profile.cycle*(if self.state=='FastMove' then .70 else 1)
  local targetSpeed=if moving then rig.stride/cycle else 0
  self.speed+=(targetSpeed-self.speed)*math.min(1,elapsed*12)
  if self.travel then
   self.distance+=self.speed*elapsed
   local radius=if profile.mode=='water' then 6 else 18
   local theta=self.distance/radius
   rig.root.CFrame=rig.base*CFrame.new(radius*(1-math.cos(theta)),0,-radius*math.sin(theta))*angles(0,-theta,0)
  end
 end
 function self:SetTravel(enabled: boolean): ()
  rig.base=rig.root.CFrame;self.distance=0;self.travel=enabled
 end
 function self:Destroy(): () self.rig.model:Destroy();table.clear(self.current);table.clear(self.from) end
 return self
end
return Motion