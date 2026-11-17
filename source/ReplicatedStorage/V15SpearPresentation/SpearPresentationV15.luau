--!strict
-- Client-only spear presentation. The existing server remains authoritative.
-- Model is a visual clone; this module never moves a damage/hitbox object.
local RunService = game:GetService("RunService")
local HttpService = game:GetService("HttpService")
local BeamArc = require(script.Parent.MeshVFX.BeamArc)
local Ease = require(script.Parent.MeshVFX.Ease)
local VFXMath = require(script.Parent.MeshVFX.VFXMath)
local Profiles = HttpService:JSONDecode(require(script.Parent.SpearProfilesV15)).profiles

local Presentation = {}
local Handle = {}
Handle.__index = Handle
local profilesById = {}
for _,profile in ipairs(Profiles) do profilesById[profile.id]=profile end
local active: {[any]: boolean} = {}
local scheduler: RBXScriptConnection? = nil

-- These engine texture paths are already used by this project's WorldFx module.
local TEXTURES = {
	"rbxasset://textures/particles/sparkles_main.dds",
	"rbxasset://textures/particles/fire_sparks_main.dds",
	"rbxasset://textures/particles/SquareParticle.png",
	"rbxasset://textures/sparkle.png",
}

local function color(hex: string): Color3
	local n = tonumber(hex:gsub("#",""),16) or 0xffffff
	return Color3.fromRGB(bit32.band(bit32.rshift(n,16),255),bit32.band(bit32.rshift(n,8),255),bit32.band(n,255))
end
local function visual(part: BasePart)
	part.Anchored=true;part.CanCollide=false;part.CanTouch=false;part.CanQuery=false;part.CastShadow=false
end
local function stopScheduler()
	if next(active)==nil and scheduler then scheduler:Disconnect();scheduler=nil end
end
local function safeNumber(value: number?, fallback: number): number
	return if type(value)=="number" and value==value and math.abs(value)<math.huge then value else fallback
end

function Handle:_path(u: number): Vector3
	u=math.clamp(u,0,1)
	local envelope=math.sin(math.pi*u)
	local p=self.Start.Position:Lerp(self.Finish,u)+Vector3.yAxis*envelope*self.ArcHeight
	local amplitude=self.Profile.waveAmplitude
	local wave=math.sin(u*math.pi*2*self.Profile.waveFrequency+self.Profile.phaseOffset)
	local right=self.HorizontalRight
	if self.Profile.pathStyle=="zigzag" or self.Profile.pathStyle=="rift" or self.Profile.pathStyle=="storm" then wave=math.asin(wave)*.8 end
	p+=right*wave*amplitude*envelope
	if self.Profile.pathStyle=="helix" or self.Profile.pathStyle=="armillary" then p+=Vector3.yAxis*math.cos(u*math.pi*2*self.Profile.waveFrequency)*amplitude*envelope end
	return p
end

function Handle:_impact()
	if self.Impacted then return end
	self.Impacted=true
	for _,trail in ipairs(self.Trails) do trail.Enabled=false end
	for _,emitter in ipairs(self.FlightEmitters) do emitter.Enabled=false;emitter:Clear() end
	for _,emitter in ipairs(self.ImpactEmitters) do emitter:Emit(if self.Profile.ordinary then 8 else math.floor((18+self.Profile.index%20)*self.Quality)) end
	if self.OnImpact then self.OnImpact(self.Finish,self.Power) end
end

function Handle:StepAt(seconds: number)
	if self.Destroyed then return end
	self.Time=math.clamp(seconds,0,self.Duration)
	local u=math.clamp(self.Time/self.FlightTime,0,1)
	local p=self:_path(u)
	local velocity=self:_path(math.min(1,u+.001))-self:_path(math.max(0,u-.001))
	local pointing=if velocity.Magnitude>.0001 then VFXMath.lookAlong(p,velocity) else CFrame.new(p)
	-- Local +Y is the model's tip direction; lookAlong uses local -Z.
	local frame=pointing*CFrame.Angles(-math.pi/2,0,0)*CFrame.Angles(0,self.Profile.spin*u*math.pi*2,0)
	if u<.13 then frame=self.Start:Lerp(frame,Ease.inOutSine(u/.13)) end
	local modelFrame=frame*CFrame.new(-self.TipLocal)
	self.Model:PivotTo(modelFrame)
	self.ImpactAnchor.CFrame=CFrame.new(self.Finish)
	if self.Time>=self.FlightTime then self:_impact() end
	local elapsed=self.Time-self.FlightTime
	for index,ray in ipairs(self.Rays) do
		local localTime=elapsed-(index%3)*self.Profile.impactDelay
		local life=.45+self.Profile.impactHeight*.16
		local show=localTime>=0 and localTime<life
		ray.Beam.Enabled=show
		if show then
			local progress=localTime/life
			local angle=index/#self.Rays*math.pi*2+self.Profile.impactTwist*progress
			local radius=(.8+self.Power*3.6)*Ease.outExpo(progress)
			local height=math.sin(math.pi*progress)*self.Profile.impactHeight*(.35+(index%3)*.24)
			ray.A0.Position=Vector3.new(math.cos(angle)*.15,.04,math.sin(angle)*.15)
			ray.A1.Position=Vector3.new(math.cos(angle)*radius,height,math.sin(angle)*radius)
			ray.Beam.Width0=(.03+.045*self.Power)*(1-progress)
			ray.Beam.Width1=.01
			ray.Beam.Transparency=NumberSequence.new(progress)
		end
	end
	for index,ring in ipairs(self.Rings) do
		local localTime=elapsed-(index-1)*(.06+self.Profile.index%4*.013)
		local life=.6+(index-1)*.06
		local show=localTime>=0 and localTime<life
		ring:setEnabled(show)
		if show then
			local progress=localTime/life
			ring:setFrame(CFrame.new(self.Finish+Vector3.yAxis*.06)*CFrame.Angles(0,self.Profile.impactTwist*progress,0))
			ring:set((.5+self.Power*3.1)*Ease.outExpo(progress)*(1+(index-1)*.2),0,math.pi*2,function()return .035+.03*self.Power end,1-(1-progress)^1.4)
		end
	end
	for index,entry in ipairs(self.Ground) do
		local age=elapsed-entry.Delay
		local k=math.clamp(age/.7,0,1)
		local wave=if self.Power>=.5 and age>=0 and age<.7 then math.sin(math.pi*k)*(.09+self.Power*.28)*math.sin(age*26) else 0
		entry.Part.Transparency=if elapsed>=0 and elapsed<1.6 and self.Power>=.5 then 0 else 1
		entry.Part.CFrame=entry.Frame*CFrame.new(0,math.max(-.02,wave),0)*CFrame.Angles(math.cos(index)*wave*.6,0,math.sin(index)*wave*.6)
	end
end

function Presentation.Create(options: any): any
	local profile=assert(profilesById[options.Id],"Unknown V15 spear profile")
	assert(options.Model and options.Model:IsA("Model"),"Pass the visual spear model")
	local power=math.clamp(safeNumber(options.Power,.65),.1,1)
	local start=options.Start :: CFrame
	local finish=options.Finish :: Vector3
	assert(typeof(start)=="CFrame" and typeof(finish)=="Vector3","Presentation requires validated visual start/finish")
	local root=Instance.new("Folder");root.Name="V15_Spear_"..profile.id;root.Parent=options.Parent or workspace
	local model=if options.ImpactOnly then Instance.new("Model") else options.Model:Clone();model.Name="VisualSpear"
	if options.ImpactOnly then
		local marker=Instance.new("Part");visual(marker);marker.Size=Vector3.one*.02;marker.Transparency=1;marker.Name="Pivot";marker.Parent=model;model.PrimaryPart=marker
	end
	for _,part in ipairs(model:GetDescendants()) do if part:IsA("BasePart") then visual(part) end end
	model.Parent=root
	local primary=assert(model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart",true),"Model has no root")
	model.PrimaryPart=primary
	local tipAttachment=if options.ImpactOnly and options.Model.PrimaryPart then options.Model.PrimaryPart:FindFirstChild("Tip") else primary:FindFirstChild("Tip")
	local tipLocal=if tipAttachment and tipAttachment:IsA("Attachment") then tipAttachment.Position else Vector3.new(0,model:GetExtentsSize().Y,0)
	local tip=Instance.new("Attachment");tip.Name="FXTip";tip.Position=tipLocal;tip.Parent=primary
	local tail=Instance.new("Attachment");tail.Name="FXTail";tail.Position=tipLocal-Vector3.yAxis*.35;tail.Parent=primary
	local c1,c2=color(profile.colors[1]),color(profile.colors[2])
	local trails={}
	for i=1,if options.ImpactOnly then 0 else profile.ribbonCount do
		local a=Instance.new("Attachment");a.Position=tail.Position+Vector3.xAxis*(i-2)*.07;a.Parent=primary
		local b=Instance.new("Attachment");b.Position=a.Position+Vector3.zAxis*(profile.ribbonWidth*2);b.Parent=primary
		local trail=Instance.new("Trail");trail.Attachment0=a;trail.Attachment1=b;trail.FaceCamera=true;trail.Lifetime=profile.trailLife;trail.LightEmission=.85;trail.Color=ColorSequence.new(c1,c2);trail.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.45),NumberSequenceKeypoint.new(.2,.1),NumberSequenceKeypoint.new(1,1)});trail.WidthScale=NumberSequence.new(1,0);trail.Enabled=not profile.ordinary;trail.Parent=primary;table.insert(trails,trail)
	end
	local quality=math.clamp(safeNumber(options.Quality,1),.25,1)
	local flightEmitters={}
	if not profile.ordinary and not options.ImpactOnly then
		local emitter=Instance.new("ParticleEmitter");emitter.Texture=TEXTURES[profile.particleMode%#TEXTURES+1];emitter.Color=ColorSequence.new(c1,c2);emitter.Rate=(12+profile.index%13)*quality;emitter.Lifetime=NumberRange.new(.18,profile.trailLife);emitter.Speed=NumberRange.new(.15,.45+profile.waveAmplitude);emitter.Drag=1+profile.index%5*.4;emitter.SpreadAngle=Vector2.new(15+profile.index%8*4,18+profile.index%5*5);emitter.Size=NumberSequence.new(.11+.01*(profile.index%5),0);emitter.Transparency=NumberSequence.new(.15,1);emitter.Rotation=NumberRange.new(0,360);emitter.LightEmission=.75;emitter.Parent=tail;table.insert(flightEmitters,emitter)
	end
	local impactAnchor=Instance.new("Part");visual(impactAnchor);impactAnchor.Size=Vector3.one*.05;impactAnchor.Transparency=1;impactAnchor.CFrame=CFrame.new(finish);impactAnchor.Parent=root
	local anchor=Instance.new("Attachment");anchor.Parent=impactAnchor
	local impact=Instance.new("ParticleEmitter");impact.Rate=0;impact.Texture=TEXTURES[(profile.index+1)%#TEXTURES+1];impact.Color=ColorSequence.new(c1,c2);impact.Lifetime=NumberRange.new(.35,.85);impact.Speed=NumberRange.new(2,4+power*5);impact.SpreadAngle=Vector2.new(65,65);impact.Drag=2;impact.Acceleration=Vector3.new(0,-profile.particleGravity*4,0);impact.Size=NumberSequence.new(.2+power*.15,0);impact.Transparency=NumberSequence.new(.1,1);impact.LightEmission=if profile.ordinary then 0 else .8;impact.Parent=anchor
	local rings={};for i=1,profile.rings do table.insert(rings,BeamArc.new(root,4,{color=if i%2==0 then c2 else c1,segmentsPerPiece=10})) end
	local rays={}
	if not profile.ordinary then
		for i=1,math.max(3,math.floor(profile.spokes*quality)) do
			local a=Instance.new("Attachment");a.Parent=impactAnchor
			local b=Instance.new("Attachment");b.Parent=impactAnchor
			local beam=Instance.new("Beam");beam.Attachment0=a;beam.Attachment1=b;beam.FaceCamera=true;beam.Enabled=false;beam.LightEmission=.8;beam.LightInfluence=0;beam.Segments=8;beam.Color=ColorSequence.new(c1,c2);beam.Parent=impactAnchor
			table.insert(rays,{A0=a,A1=b,Beam=beam})
		end
	end
	local ground={};local rayParams=RaycastParams.new();rayParams.FilterType=Enum.RaycastFilterType.Exclude;rayParams.FilterDescendantsInstances={root};rayParams.IgnoreWater=true
	for i=1,math.floor(24*quality) do
		local angle=i/(24*quality)*math.pi*2;local radius=1.6+i%3*.55;local candidate=finish+Vector3.new(math.cos(angle)*radius,5,math.sin(angle)*radius)
		local hit=workspace:Raycast(candidate,Vector3.new(0,-14,0),rayParams)
		if hit then
			local cube=Instance.new("Part");visual(cube);cube.Name="GroundRippleCell";cube.Size=Vector3.one*.48;cube.Material=hit.Material;cube.Color=if hit.Instance:IsA("BasePart") then hit.Instance.Color else workspace.Terrain:GetMaterialColor(hit.Material)
			cube.TopSurface=Enum.SurfaceType.Studs;cube.BottomSurface=Enum.SurfaceType.Studs;cube.LeftSurface=Enum.SurfaceType.Studs;cube.RightSurface=Enum.SurfaceType.Studs;cube.FrontSurface=Enum.SurfaceType.Studs;cube.BackSurface=Enum.SurfaceType.Studs;cube.Transparency=1
			local frame=VFXMath.alignToNormal(hit.Position-hit.Normal*.23,hit.Normal);cube.CFrame=frame;cube.Parent=root;table.insert(ground,{Part=cube,Frame=frame,Delay=radius/(4+power*5)})
		end
	end
	local horizontal=finish-start.Position;horizontal=Vector3.new(horizontal.X,0,horizontal.Z)
	local right=if horizontal.Magnitude>.01 then horizontal.Unit:Cross(Vector3.yAxis) else Vector3.xAxis
	local flightTime=if options.ImpactOnly then .001 else math.clamp(safeNumber(options.FlightTime,1.85-power*.58+(profile.index%4)*.018),.25,20)
	local self:any=setmetatable({Root=root,Model=model,Profile=profile,Start=start,Finish=finish,TipLocal=tipLocal,Power=power,FlightTime=flightTime,Duration=flightTime+1.85,ArcHeight=safeNumber(options.ArcHeight,2.1+power*4.7),HorizontalRight=right,Time=0,Trails=trails,FlightEmitters=flightEmitters,ImpactEmitters={impact},ImpactAnchor=impactAnchor,Rings=rings,Rays=rays,Ground=ground,Quality=quality,Impacted=false,Destroyed=false,OnImpact=options.OnImpact},Handle)
	self:StepAt(if options.ImpactOnly then flightTime else 0)
	return self
end

function Handle:Play()
	active[self]=true
	if not scheduler and RunService:IsClient() then
		scheduler=RunService.RenderStepped:Connect(function(dt)
			for handle in pairs(active) do
				handle:StepAt(handle.Time+math.min(dt,.1))
				if handle.Time>=handle.Duration then handle:Destroy() end
			end
		end)
	end
	return self
end

function Handle:Destroy()
	if self.Destroyed then return end
	self.Destroyed=true;active[self]=nil;self.Root:Destroy();stopScheduler()
end

Presentation.Profiles=profilesById

-- Convert the hand's grip frame into the visual tip frame expected by Create.
function Presentation.TipFrameAtGrip(model: Model, gripFrame: CFrame): CFrame
	local primary=model.PrimaryPart
	assert(primary,"Set the model PrimaryPart to its exported Pivot")
	local grip=primary:FindFirstChild("Grip")
	local tip=primary:FindFirstChild("Tip")
	assert(grip and grip:IsA("Attachment") and tip and tip:IsA("Attachment"),"Exported Grip/Tip Attachments are required")
	return gripFrame*CFrame.new(tip.Position-grip.Position)
end

return Presentation
