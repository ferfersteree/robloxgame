const fs=require('fs'),vm=require('vm');
const A='C:/Users/user/AppData/Local/Temp/claude/ec29f026d20d029c/b319fb1f-ac51-4419-97ca-6a3b1ea960fc/scratchpad/html/assets/';
const ctxObj={console,Math,Date,setTimeout,clearTimeout,Float32Array,Uint8Array,Uint16Array,Uint32Array,Int32Array,Float64Array,ArrayBuffer,Map,Set,Object,Array,Promise,Symbol,performance:{now:()=>0}};
ctxObj.window=ctxObj;ctxObj.globalThis=ctxObj;ctxObj.self=ctxObj;
ctxObj.document={createElement:()=>({getContext:()=>({}),style:{},width:0,height:0}),createElementNS:()=>({style:{}})};
ctxObj.navigator={userAgent:'node'};
vm.createContext(ctxObj);
for(const f of ['b9c1bba8ace106923eb233bf5429e401.js','9790a78911cc87108f515a24dfc2af21.js'])vm.runInContext(fs.readFileSync(A+f,'utf8'),ctxObj,{filename:f});
module.exports={SP:ctxObj.SpearPets,T:ctxObj.THREE};
