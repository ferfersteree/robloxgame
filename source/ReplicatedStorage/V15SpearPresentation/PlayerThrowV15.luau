--!strict
-- R15 cosmetic throwing layer. No animation IDs, input, remotes, damage or rewards.
-- Call Play only after the existing throwing controller accepts the action.
local RunService = game:GetService("RunService")

local PlayerThrow = {}
PlayerThrow.__index = PlayerThrow
local active: {[any]: boolean} = {}
local beforeAnimation: RBXScriptConnection? = nil
local beforePhysics: RBXScriptConnection? = nil

local function smooth(t: number): number
	t = math.clamp(t, 0, 1)
	return t*t*(3-2*t)
end
local function phase(t: number, a: number, b: number): number
	return smooth((t-a)/(b-a))
end
local function blend(a: number, b: number, t: number): number
	return a+(b-a)*t
end
local function validPower(value: number): number
	return if value == value and math.abs(value) < math.huge then math.clamp(value, .1, 1) else .65
end

function PlayerThrow.Timing(power: number): any
	local p = validPower(power)
	local release = .44+.66*p
	return {Release=release, Windup=release*.67, Duration=release+.8+.3*p}
end

function PlayerThrow.Sample(seconds: number, power: number): any
	local p = validPower(power)
	local t = PlayerThrow.Timing(p)
	local wind = phase(seconds, 0, t.Windup)
	local snap = phase(seconds, t.Windup, t.Release)
	local follow = phase(seconds, t.Release, t.Release+.3)
	local recovery = phase(seconds, t.Release+.35, t.Duration)
	local weight = 1-recovery
	return {
		RightShoulder=CFrame.Angles(blend(blend(.95,.2-1.1*p,wind),1.36+.08*p,snap)*weight,0,-.12*wind*(1-follow)*weight),
		RightElbow=CFrame.Angles(blend(blend(1,1.35+1.05*p,wind),.12,snap)*weight,0,0),
		RightWrist=CFrame.Angles(.03*wind*weight,0,0),
		LeftShoulder=CFrame.Angles((-.45*wind+.8*snap)*weight,0,(.12+.15*p)*wind*(1-follow)*weight),
		LeftElbow=CFrame.Angles((.32*wind+.16*snap)*weight,0,0),
		Waist=CFrame.Angles((-.06*wind+.13*follow)*weight,(-.12-.28*p)*wind*(1-snap)+(.1+.15*p)*snap*weight,0),
		Neck=CFrame.Angles((.03*wind-.05*follow)*weight,0,0),
		LeftHip=CFrame.new(0,0,-.17*p*wind*weight)*CFrame.Angles(-.2*p*wind*weight,0,0),
		LeftKnee=CFrame.Angles(.23*p*wind*weight,0,0),
		RightHip=CFrame.new(0,0,.12*p*wind*weight)*CFrame.Angles(.12*p*wind*weight,0,0),
		RightKnee=CFrame.Angles(.18*p*wind*(1-snap)*weight,0,0),
	}
end

-- Direct Euler targets for the project's existing procedural Animator. Returning
-- the intended hinge angles avoids Euler decomposition flipping at 90 degrees.
function PlayerThrow.SampleAngles(seconds: number,power: number): any
	local p=validPower(power);local t=PlayerThrow.Timing(p)
	local wind=phase(seconds,0,t.Windup);local snap=phase(seconds,t.Windup,t.Release)
	local follow=phase(seconds,t.Release,t.Release+.3);local recover=phase(seconds,t.Release+.35,t.Duration);local weight=1-recover
	return {
		RightShoulder={blend(blend(.95,.2-1.1*p,wind),1.36+.08*p,snap)*weight,0,-.12*wind*(1-follow)*weight},
		RightElbow={blend(blend(1,1.35+1.05*p,wind),.12,snap)*weight,0,0},RightWrist={.03*wind*weight,0,0},
		LeftShoulder={(-.45*wind+.8*snap)*weight,0,(.12+.15*p)*wind*(1-follow)*weight},LeftElbow={(.32*wind+.16*snap)*weight,0,0},
		Waist={(-.06*wind+.13*follow)*weight,(-.12-.28*p)*wind*(1-snap)+(.1+.15*p)*snap*weight,0},Neck={(.03*wind-.05*follow)*weight,0,0},
		LeftHip={-.2*p*wind*weight,0,0},LeftKnee={.23*p*wind*weight,0,0},RightHip={.12*p*wind*weight,0,0},RightKnee={.18*p*wind*(1-snap)*weight,0,0},
		root={0,-math.sin(wind*math.pi*.5)*(1-snap)*(.08+.16*p),0},
	}
end

local function releaseLoopIfIdle()
	if next(active) ~= nil then return end
	if beforeAnimation then beforeAnimation:Disconnect();beforeAnimation=nil end
	if beforePhysics then beforePhysics:Disconnect();beforePhysics=nil end
end

function PlayerThrow:_removeLayer()
	for _,entry in pairs(self.Joints) do
		if entry.Motor.Parent and entry.Applied and entry.Motor.Transform == entry.Applied then
			entry.Motor.Transform = entry.Base
		end
		entry.Applied = nil
	end
end

function PlayerThrow:StepAt(seconds: number)
	if self.Destroyed then return end
	self:_removeLayer()
	self.Time = math.clamp(seconds,0,self.Timing.Duration)
	local pose = PlayerThrow.Sample(self.Time,self.Power)
	local blendIn = smooth(self.Time/.12)
	for name,entry in pairs(self.Joints) do
		if entry.Motor.Parent then
			entry.Base = entry.Motor.Transform
			entry.Applied = entry.Base*CFrame.identity:Lerp(pose[name] or CFrame.identity,blendIn)
			entry.Motor.Transform = entry.Applied
		end
	end
	if self.Time >= self.Timing.Release and not self.Released then
		self.Released = true
		if self.OnRelease then self.OnRelease(self:GetGripFrame(),self.Power) end
	end
end

local function startLoop()
	if beforePhysics or not RunService:IsClient() then return end
	-- Remove our previous offsets before Animator computes the next base pose.
	beforeAnimation = RunService.PreAnimation:Connect(function()
		for controller in pairs(active) do controller:_removeLayer() end
	end)
	beforePhysics = RunService.PreSimulation:Connect(function(dt)
		for controller in pairs(active) do
			controller:StepAt(controller.Time+math.min(dt,.1))
			if controller.Time >= controller.Timing.Duration then controller:Stop() end
		end
	end)
end

function PlayerThrow.new(character: Model, options: any?): any
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	assert(humanoid and humanoid.RigType == Enum.HumanoidRigType.R15,"PlayerThrowV15 requires the existing R15 character")
	local joints = {}
	local wanted = {RightShoulder=true,RightElbow=true,RightWrist=true,LeftShoulder=true,LeftElbow=true,Waist=true,Neck=true,LeftHip=true,LeftKnee=true,RightHip=true,RightKnee=true}
	for _,object in ipairs(character:GetDescendants()) do
		if object:IsA("Motor6D") and wanted[object.Name] then
			joints[object.Name] = {Motor=object,Base=object.Transform,Applied=nil}
		end
	end
	local self:any = setmetatable({Character=character,Joints=joints,Time=0,Power=.65,Timing=PlayerThrow.Timing(.65),Released=false,Destroyed=false,OnRelease=nil},PlayerThrow)
	self.GripOffset = if options and options.GripOffset then options.GripOffset else CFrame.new(.02,-.1,-.07)*CFrame.Angles(math.pi,0,0)
	self.DestroyConnection = character.Destroying:Connect(function() self:Destroy() end)
	return self
end

function PlayerThrow:GetGripFrame(): CFrame
	local hand = self.Character:FindFirstChild("RightHand")
	return if hand and hand:IsA("BasePart") then hand.CFrame*self.GripOffset else self.Character:GetPivot()
end

function PlayerThrow:Play(power: number, onRelease: ((CFrame,number)->())?): number
	self:Stop()
	self.Power = validPower(power)
	self.Timing = PlayerThrow.Timing(self.Power)
	self.Time = 0;self.Released=false;self.OnRelease=onRelease
	active[self]=true
	startLoop()
	return self.Timing.Release
end

function PlayerThrow:Stop()
	active[self]=nil
	self:_removeLayer()
	self.OnRelease=nil
	releaseLoopIfIdle()
end

function PlayerThrow:Destroy()
	if self.Destroyed then return end
	self:Stop();self.Destroyed=true
	if self.DestroyConnection then self.DestroyConnection:Disconnect();self.DestroyConnection=nil end
	table.clear(self.Joints)
end

return PlayerThrow
