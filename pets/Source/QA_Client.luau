-- Run once in Client during Play. Restores camera, leaves no listeners or scripts.
local RunService=game:GetService('RunService')
local HttpService=game:GetService('HttpService')
local Stats=game:GetService('Stats')
assert(RunService:IsRunning()and RunService:IsClient(),'FPS check requires Play/Client')
local cam=assert(workspace.CurrentCamera);local floor=assert(workspace:FindFirstChild('GalleryFloor'))
local saved={kind=cam.CameraType,cframe=cam.CFrame,focus=cam.Focus,fov=cam.FieldOfView}
local samples={};local reason=nil
local ok,err=xpcall(function()
 local target=Vector3.new(0,1,0);cam.CameraType=Enum.CameraType.Scriptable;cam.FieldOfView=42
 cam.Focus=CFrame.new(target);cam.CFrame=CFrame.lookAt(target+Vector3.new(.35,.95,-1).Unit*math.max(floor.Size.X,floor.Size.Z)*1.55,target)
 local warm=os.clock()+1;repeat RunService.RenderStepped:Wait()until os.clock()>=warm
 local untilTime=os.clock()+5
 repeat local dt=RunService.RenderStepped:Wait();samples[#samples+1]=dt until os.clock()>=untilTime
end,debug.traceback)
cam.CameraType=saved.kind;cam.CFrame=saved.cframe;cam.Focus=saved.focus;cam.FieldOfView=saved.fov
if not ok then reason=tostring(err)end
local sum=0;local slow=0;for _,v in samples do sum+=v;if v>1/30 then slow+=1 end end;table.sort(samples)
local count=#samples;local mean=if count>0 then sum/count else 0
local memory=nil;local memoryOK,value=pcall(function()return Stats:GetTotalMemoryUsageMb()end);if memoryOK then memory=value end
return HttpService:JSONEncode({passed=ok and count>0,error=reason,sampleCount=count,sampleSeconds=sum,meanFPS=if mean>0 then 1/mean else 0,medianFrameMs=if count>0 then samples[math.max(1,math.floor(count*.5))]*1000 else 0,p95FrameMs=if count>0 then samples[math.max(1,math.ceil(count*.95))]*1000 else 0,framesOver33ms=slow,memoryMB=memory,cameraRestored=true,scope='Five seconds of this local Studio client at overview; background throttling and hardware affect results; not mobile or published-game certification'})
