--!strict
-- Adapter for the existing SpearFx clock/path. Does not decide any endpoint or reward.
local HttpService=game:GetService("HttpService")
local Factory=require(script.Parent.SpearFactoryV15)
local Presentation=require(script.Parent.SpearPresentationV15)
local profiles=Presentation.Profiles
local Adapter={}
local Handle={};Handle.__index=Handle
local TEXTURES={"rbxasset://textures/particles/sparkles_main.dds","rbxasset://textures/particles/fire_sparks_main.dds","rbxasset://textures/particles/SquareParticle.png","rbxasset://textures/sparkle.png"}
local function color(hex: string): Color3
	local n=tonumber(hex:gsub("#",""),16)or 0xffffff
	return Color3.fromRGB(bit32.band(bit32.rshift(n,16),255),bit32.band(bit32.rshift(n,8),255),bit32.band(n,255))
end
function Adapter.Attach(model: Model,id: string,tier: number): any
	local profile=profiles[id]
	if not profile or not model.PrimaryPart then return nil end
	local primary=model.PrimaryPart
	local c1,c2=color(profile.colors[1]),color(profile.colors[2])
	local tip=primary:FindFirstChild("TipAtt")::Attachment
	local tail=primary:FindFirstChild("TrailRoot")::Attachment
	local trails={};local anchors={}
	for i=1,profile.ribbonCount do
		local a=Instance.new("Attachment");a.Position=tail.Position+Vector3.xAxis*(i-2)*.08;a.Parent=primary
		local b=Instance.new("Attachment");b.Position=a.Position+Vector3.zAxis*profile.ribbonWidth*2;b.Parent=primary
		local tr=Instance.new("Trail");tr.Attachment0=a;tr.Attachment1=b;tr.FaceCamera=true;tr.MinLength=.04;tr.Lifetime=profile.trailLife;tr.Color=ColorSequence.new(c1,c2);tr.LightEmission=.8;tr.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.35),NumberSequenceKeypoint.new(.2,.1),NumberSequenceKeypoint.new(1,1)});tr.WidthScale=NumberSequence.new(1,0);tr.Parent=primary
		table.insert(trails,tr);table.insert(anchors,{A=a,B=b,Phase=i*math.pi*2/math.max(1,profile.ribbonCount)})
	end
	local emitter=nil
	if not profile.ordinary then
		emitter=Instance.new("ParticleEmitter");emitter.Texture=TEXTURES[profile.particleMode%4+1];emitter.Color=ColorSequence.new(c1,c2);emitter.Rate=12+profile.index%14;emitter.Lifetime=NumberRange.new(.18,profile.trailLife);emitter.Speed=NumberRange.new(.1,.4+profile.waveAmplitude);emitter.Drag=.8+profile.index%5*.3;emitter.SpreadAngle=Vector2.new(14+profile.index%7*4,14+profile.index%9*3);emitter.Size=NumberSequence.new(.1+profile.index%5*.015,0);emitter.Transparency=NumberSequence.new(.15,1);emitter.LightEmission=.8;emitter.Rotation=NumberRange.new(0,360);emitter.Parent=tail
	end
	local initial=model:GetPivot()
	local self:any=setmetatable({Model=model,Profile=profile,Trails=trails,Anchors=anchors,Emitter=emitter,Tail=tail,Tip=tip,InitialFrame=initial,InitialTip=initial:PointToWorldSpace(tip.Position),Power=math.clamp(.25+(tier-1)*.15,.25,1),Stopped=false},Handle)
	return self
end
function Handle:Frame(position: Vector3,direction: Vector3,u: number,seconds: number): CFrame
	local p=self.Profile
	local envelope=math.sin(math.pi*math.clamp(u,0,1))
	local side=direction:Cross(Vector3.yAxis)
	if side.Magnitude<.0001 then side=Vector3.xAxis end
	side=side.Unit
	local wave=math.sin(u*math.pi*2*p.waveFrequency+p.phaseOffset)
	if p.pathStyle=="zigzag"or p.pathStyle=="storm"or p.pathStyle=="rift"then wave=math.asin(wave)*.8 end
	local visualPosition=position+side*wave*p.waveAmplitude*envelope
	if p.pathStyle=="helix"or p.pathStyle=="armillary"then visualPosition+=Vector3.yAxis*math.cos(u*math.pi*2*p.waveFrequency)*p.waveAmplitude*envelope end
	for _,entry in ipairs(self.Anchors)do
		local angle=entry.Phase+seconds*p.spin
		local offset=Vector3.new(math.cos(angle),0,math.sin(angle))*(.03+p.waveAmplitude*.25)
		entry.A.Position=self.Tail.Position+offset
		entry.B.Position=entry.A.Position+Vector3.zAxis*p.ribbonWidth*2
	end
	local rotation=Factory.Frame(Vector3.zero,direction)*CFrame.Angles(0,seconds*p.spin,0)
	local tipTarget=visualPosition+direction*(1-u)*(self.Tip.Position.Y+1.5)-Vector3.yAxis*.35*u
	if u<.13 then
		local blend=u/.13;blend=blend*blend*(3-2*blend)
		rotation=(self.InitialFrame-self.InitialFrame.Position):Lerp(rotation,blend)
		tipTarget=self.InitialTip:Lerp(tipTarget,blend)
	end
	return rotation+tipTarget-rotation:VectorToWorldSpace(self.Tip.Position)
end
function Handle:Land(position: Vector3,direction: Vector3)
	if self.Stopped then return end
	self.Stopped=true
	for _,trail in ipairs(self.Trails)do trail.Enabled=false end
	if self.Emitter then self.Emitter.Enabled=false;self.Emitter:Clear()end
	local tipFrame=Factory.Frame(position,direction)
	-- V46: Reduced Effects (player attribute LowFx, set by Main): fewer rays and spokes on landing (Quality .3 vmesto 1)
	local lp=game:GetService("Players").LocalPlayer
	local quality=if lp and lp:GetAttribute("LowFx")==true then .3 else 1
	Presentation.Create({Id=self.Profile.id,Model=self.Model,Start=tipFrame,Finish=position,Power=self.Power,FlightTime=.001,ImpactOnly=true,Quality=quality}):Play()
end
function Handle:Stop()
	self.Stopped=true
	for _,trail in ipairs(self.Trails)do if trail.Parent then trail.Enabled=false end end
	if self.Emitter and self.Emitter.Parent then self.Emitter.Enabled=false end
end
return Adapter
