const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.setContent('<html><body></body></html>');
await p.addScriptTag({path:'node_modules/three/build/three.min.js'});await p.addScriptTag({path:'icons_toon.js'});
const raw=JSON.parse(fs.readFileSync('../geo2.json'));
const geo={spear:raw['ReplicatedStorage/Assets/Spears/bronze']};
const A=['moonrabbit','rabbit','squirrel','hedgehog','fox','dodo'];for(const a of A)geo[a]=raw['ReplicatedStorage/Animals/'+a];
const jobs=[];
// spear for starter pack (diagonal like Menus.spearView) and flying
jobs.push(['spear',640,640,{geo:'spear',yaw:20,rz:-42}]);jobs.push(['flyspear',900,360,{geo:'spear',yaw:0,rz:90}]);
jobs.push(['charm',640,600,{geo:'moonrabbit',yaw:-22,rainbow:true}]);
for(const n of ['purse','wrap','bag','titan','vip','luck30','coins30','brew30','server15','coins1','coins2','coins3','coins4'])jobs.push([n,640,600,{}]);
for(const a of A){jobs.push([a+'_R',560,460,{geo:a,yaw:90}]);}
jobs.push(['squirrel_F',500,500,{geo:'squirrel',yaw:-18}]);jobs.push(['moonrabbit_F',500,500,{geo:'moonrabbit',yaw:-18}]);
for(const [n,w,h,o] of jobs){const d=await p.evaluate(([n,w,h,geo,o])=>window.renderItem(n,w,h,geo,o),[n,w,h,geo,o]);fs.writeFileSync('t_'+n+'.png',Buffer.from(d.split(',')[1],'base64'));}
console.log('rendered',jobs.length);await b.close()})();
