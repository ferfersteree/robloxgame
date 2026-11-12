const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('C',m.text())});
await p.setContent('<html><body></body></html>');
await p.addScriptTag({path:'node_modules/three/build/three.min.js'});
await p.addScriptTag({path:'icons.js'});
const raw=JSON.parse(fs.readFileSync('../geo.json'));
const geo={spear:raw['ReplicatedStorage/Assets/Spears/bronze'],rabbit:raw['ReplicatedStorage/Animals/moonrabbit']};
const out={};
const items=['spear','charm','purse','wrap','bag','titan','vip','luck30','coins30','brew30','server15','coins1','coins2','coins3','coins4'];
for(const n of items){out[n]=await p.evaluate(([n,geo])=>window.renderItem(n,n==='spear'?360:240,n==='spear'?360:224,geo),[n,geo]);}
fs.writeFileSync('icons.json',JSON.stringify(out));
for(const n of items)fs.writeFileSync('icon_'+n+'.png',Buffer.from(out[n].split(',')[1],'base64'));
console.log('ok',Object.values(out).reduce((a,v)=>a+v.length,0));await b.close()})();
