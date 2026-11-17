--!strict
-- Presentation geometry only: the authoritative catch/result is untouched.
local RunService=game:GetService("RunService")
local Stage={}
function Stage.Plan(pos: Vector3,viewer: Vector3,cover: any,animal: any?): any
 local toward=Vector3.new(viewer.X-pos.X,0,viewer.Z-pos.Z)
 local direction=if toward.Magnitude>.001 then toward.Unit else Vector3.zAxis
 local depth=cover.bounds.size[3]
 local front=if animal then math.max(.2,-animal.bounds[1][3])else 1
 local rear=if animal then math.max(.2,animal.bounds[2][3])else 1
 local width=if animal then animal.w else 2
 -- The end pose remains exactly at the original catch point. The curtain is
 -- behind it, so even a long tail clears the opening instead of clipping it.
 local center=pos-direction*(depth*.5+rear+.65)
 local start=center-direction*(depth*.5+front+.55)
 return {Direction=direction,Center=center,Start=start,Finish=pos,Frame=CFrame.lookAt(center,center+direction),Focus=center:Lerp(pos,.5),Spread=math.max(cover.bounds.size[1]*.48,width*.62+1.4),Height=math.max(if animal then animal.h else 2,cover.bounds.size[1]*.55),Duration=1.1}
end
function Stage.Walk(rig: any,plan: any)
 local t0=os.clock();local duration=plan.Duration
 rig.model:SetAttribute("V15_Emerging",true);rig.model:SetAttribute("V15_EmergenceScale",rig.model:GetScale())
 rig:play("walk",1)
 local old=rig.onUpdate
 rig.onUpdate=function(self: any,_dt: number)
  local u=math.clamp((os.clock()-t0)/duration,0,1)
  local position=plan.Start:Lerp(plan.Finish,u)
  self.cf=CFrame.lookAt(position,position+plan.Direction)
 end
 while rig.alive and rig.model.Parent and os.clock()-t0<duration do RunService.RenderStepped:Wait()end
 if rig.alive and rig.model.Parent then
  rig.onUpdate=old
  rig.cf=CFrame.lookAt(plan.Finish,plan.Finish+plan.Direction);rig.root.CFrame=rig.cf
  rig:play("stand",1);rig.model:SetAttribute("V15_Emerging",false)
 end
end
return Stage
