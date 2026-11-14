const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.setContent('<html><body></body></html>');
await p.addScriptTag({path:'node_modules/three/build/three.min.js'});await p.addScriptTag({path:'icons.js'});
const raw=JSON.parse(fs.readFileSync('../geo2.json'));
const geo={spear:raw['ReplicatedStorage/Assets/Spears/bronze']};
for(const a of ['moonrabbit','rabbit','squirrel','hedgehog','fox','dodo'])geo[a]=raw['ReplicatedStorage/Animals/'+a];
const jobs=[['flyspear',480,480,{geo:'spear',yaw:0,rz:90}]];
for(const a of ['moonrabbit','rabbit','squirrel','hedgehog','fox','dodo']){
  jobs.push([a+'_R',300,260,{geo:a,yaw:90}]);jobs.push([a+'_L',300,260,{geo:a,yaw:-90}]);jobs.push([a+'_F',300,260,{geo:a,yaw:-18}]);}
for(const [n,w,h,o] of jobs){const d=await p.evaluate(([n,w,h,geo,o])=>window.renderItem(n,w,h,geo,o),[n,w,h,geo,o]);fs.writeFileSync('a_'+n+'.png',Buffer.from(d.split(',')[1],'base64'));}
await b.close()})();
