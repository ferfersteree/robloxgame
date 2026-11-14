// Port of Shop.luau buildIcon + UI.viewport framing, plus real game models from geometry JSON.
THREE.ColorManagement.enabled=false;
const MAT = { 256:{}, 272:{r:.35}, 288:{neon:1}, 1088:{m:.08,r:.35}, 512:{r:.8}, 1568:{glass:1}, 1312:{r:.95} };
const PLASTIC=256, SMOOTH=272, NEON=288, METAL=1088, WOOD=512, GLASS=1568, FABRIC=1312;
function rgb(r,g,b){return new THREE.Color(r/255,g/255,b/255)}
function mk(shape,size,mat4,col,material){
  let g;
  if(shape==='ball'){g=new THREE.SphereGeometry(.5,28,20);g.scale(size[0],size[1],size[2])}
  else if(shape==='cyl'){g=new THREE.CylinderGeometry(.5,.5,1,32);g.rotateZ(Math.PI/2);g.scale(size[0],size[1],size[2])}
  else g=new THREE.BoxGeometry(size[0],size[1],size[2]);
  const o=MAT[material]||{};
  const c=col.clone();
  const m=new THREE.MeshStandardMaterial({color:c,roughness:o.r??.55,metalness:o.m??0,
    emissive:o.neon?c:0x000000,emissiveIntensity:o.neon?.9:0,transparent:!!o.glass,opacity:o.glass?.45:1});
  const mesh=new THREE.Mesh(g,m);mesh.applyMatrix4(mat4);return mesh;
}
function cf(x,y,z,rx=0,ry=0,rz=0){const m=new THREE.Matrix4();m.makeRotationFromEuler(new THREE.Euler(rx,ry,rz,'XYZ'));m.setPosition(x,y,z);return m}
const D=Math.PI/180;
function buildIcon(kind){
  const parts=[];
  const part=(shape,size,m,col,mat)=>parts.push(mk(shape,[size[0],size[1],size[2]],m,col,mat||SMOOTH));
  const disc=(d,h,pos,col,mat)=>part('cyl',[h,d,d],cf(pos[0],pos[1],pos[2],0,0,90*D),col,mat);
  const GOLD=rgb(255,200,50),GOLD2=rgb(236,160,24);
  const coinStack=(n,x,z)=>{for(let i=1;i<=n;i++)disc(1,.17,[x+((i%2==0)?.04:-.03),(i-.5)*.19,z],(i%2==0)?GOLD:GOLD2,METAL)};
  const flask=(col,pos,s)=>{
    part('ball',[1.3*s,1.3*s,1.3*s],cf(pos[0],pos[1]+.65*s,pos[2]),col,NEON);
    part('ball',[.3*s,.3*s,.3*s],cf(pos[0]-.3*s,pos[1]+.95*s,pos[2]-.42*s),rgb(255,255,255),NEON);
    disc(.46*s,.55*s,[pos[0],pos[1]+1.45*s,pos[2]],rgb(214,236,244),GLASS);
    disc(.62*s,.14*s,[pos[0],pos[1]+1.74*s,pos[2]],rgb(214,236,244),GLASS);
    disc(.4*s,.3*s,[pos[0],pos[1]+1.92*s,pos[2]],rgb(150,98,56),SMOOTH)};
  const chest=()=>{const wood=rgb(150,92,48),dark=rgb(104,60,30);
    part('block',[2.4,1.1,1.5],cf(0,.55,0),wood,WOOD);
    part('block',[2.5,.22,1.6],cf(0,1.12,0),dark,WOOD);
    part('block',[2.4,.2,1.5],cf(0,1.9,.72,-62*D,0,0),dark,WOOD);
    for(const x of[-.85,.85])part('block',[.2,1.14,1.54],cf(x,.55,0),GOLD2,METAL);
    part('block',[.34,.4,.12],cf(0,.82,-.78),GOLD,METAL);
    for(let i=1;i<=9;i++){const a=i*2.4;disc(.62,.14,[Math.cos(a)*.75,1.3+(i%3)*.12,Math.sin(a)*.4],(i%2==0)?GOLD:GOLD2,METAL)}};
  if(kind=='coins1'){coinStack(4,0,0);disc(1,.17,[1.05,.09,-.2],GOLD,METAL);part('cyl',[.17,1,1],cf(-.95,.5,.3,0,70*D,0),GOLD2,METAL)}
  else if(kind=='coins2'){coinStack(5,-.6,.3);coinStack(8,.55,.35);coinStack(3,0,-.75)}
  else if(kind=='coins3')chest();
  else if(kind=='coins4'){chest();coinStack(7,-1.9,-.5);coinStack(4,1.9,-.6);coinStack(5,-1.2,-1.3);coinStack(3,1.1,-1.4)}
  else if(kind=='purse'){const l=rgb(170,96,44);
    part('ball',[1.9,1.7,1.7],cf(0,.85,0),l);disc(.75,.5,[0,1.75,0],l);
    disc(.95,.14,[0,1.62,0],GOLD,METAL);disc(.9,.16,[0,2.05,0],GOLD2,METAL);
    part('cyl',[.14,.8,.8],cf(0,.85,-.86,0,90*D,0),GOLD,METAL);coinStack(3,1.35,-.3)}
  else if(kind=='wrap'){const paper=rgb(214,164,104),rope=rgb(224,44,50);
    part('block',[1.7,1.4,1.7],cf(0,.7,0),paper);part('block',[1.76,1.46,.22],cf(0,.7,0),rope);part('block',[.22,1.46,1.76],cf(0,.7,0),rope);
    part('ball',[.7,.42,.42],cf(-.36,1.58,0,0,0,-22*D),rope);part('ball',[.7,.42,.42],cf(.36,1.58,0,0,0,22*D),rope);part('ball',[.34,.34,.34],cf(0,1.5,0),GOLD)}
  else if(kind=='bag'){const canvas=rgb(96,140,78),leather=rgb(132,78,38);
    part('block',[1.6,1.8,.95],cf(0,.9,0),canvas,FABRIC);part('ball',[1.6,.8,.95],cf(0,1.8,0),canvas,FABRIC);
    part('block',[1.66,.75,.2],cf(0,1.62,-.44),leather);part('block',[1.05,.7,.26],cf(0,.55,-.56),leather);
    part('block',[.24,.24,.1],cf(0,1.3,-.56),GOLD,METAL);part('block',[.24,.2,.1],cf(0,.82,-.7),GOLD,METAL);
    for(const x of[-.55,.55])part('block',[.22,1.7,.14],cf(x,.95,.52),leather);
    disc(1.5,.26,[0,2.28,.05],rgb(214,164,104),FABRIC)}
  else if(kind=='titan'){const plate=rgb(240,232,214),steel=rgb(96,100,112);
    part('cyl',[2.6,.26,.26],cf(0,.8,0),steel,METAL);
    for(const s of[-1,1]){part('cyl',[.5,1.6,1.6],cf(s*1.2,.8,0),plate);part('cyl',[.3,1.15,1.15],cf(s*.82,.8,0),GOLD,METAL);part('cyl',[.14,.5,.5],cf(s*1.5,.8,0),steel,METAL)}}
  else if(kind=='vip'){
    disc(1.9,.5,[0,.25,0],GOLD,METAL);disc(1.98,.14,[0,.06,0],GOLD2,METAL);
    for(let i=1;i<=6;i++){const a=(i-1)*Math.PI/3,x=Math.cos(a)*.82,z=Math.sin(a)*.82,tall=(i%2==1)?.95:.6;
      part('block',[.3,tall,.3],cf(x,.5+tall/2,z,0,-a,0),GOLD,METAL);
      part('ball',[.36,.36,.36],cf(x,.56+tall,z),(i%2==1)?rgb(232,50,56):rgb(78,181,255),NEON)}
    part('ball',[.34,.34,.34],cf(0,.26,-.95),rgb(120,255,150),NEON)}
  else if(kind=='luck30')flask(rgb(90,220,110),[0,0,0],1);
  else if(kind=='coins30')flask(rgb(255,200,50),[0,0,0],1);
  else if(kind=='brew30'){flask(rgb(90,220,110),[-1.05,0,.2],.85);flask(rgb(255,200,50),[0,0,-.35],1);flask(rgb(80,170,255),[1.05,0,.2],.85)}
  else if(kind=='server15'){flask(rgb(110,190,255),[0,0,0],1.15);
    for(let i=1;i<=5;i++){const a=i*Math.PI*2/5;part('ball',[.3,.3,.3],cf(Math.cos(a)*1.35,.5+(i%2)*.9,Math.sin(a)*1.35),rgb(255,240,120),NEON)}}
  const g=new THREE.Group();parts.forEach(p=>g.add(p));return g;
}
function fromGeo(list,rainbow){
  const g=new THREE.Group();let i=0;
  for(const p of list){
    if(p.tr>=1)continue;
    let col=new THREE.Color(p.col[0],p.col[1],p.col[2]);
    if(rainbow){i++;const hsl={};col.getHSL(hsl);
      // Roblox HSV recolor: h=(i*.07)%1, s=max(.55,s), v=max(.8,v)
      const c=new THREE.Color();const hh=(i*.07)%1;
      const mx=Math.max(p.col[0],p.col[1],p.col[2]),mn=Math.min(p.col[0],p.col[1],p.col[2]);
      const s=Math.max(.55,mx?(mx-mn)/mx:0),v=Math.max(.8,mx);
      c.setHSL(0,0,0);
      const k=(n)=>{const a=(n+hh*6)%6;return v-v*s*Math.max(0,Math.min(a,4-a,1))};
      col=new THREE.Color(k(5),k(3),k(1));}
    const r=p.rot,m=new THREE.Matrix4().set(r[0],r[1],r[2],p.pos[0], r[3],r[4],r[5],p.pos[1], r[6],r[7],r[8],p.pos[2], 0,0,0,1);
    const shape=p.shape===0?'ball':p.shape===2?'cyl':'block';
    g.add(mk(shape,p.size,m,col,p.mat));
  }
  return g;
}
// UI.viewport: centre the model's bounding box, yaw it, camera FOV 30 at (0,.35r,-dist) looking at origin
function frame(group,yawDeg,w,h,pre){
  if(pre)group.applyMatrix4(pre);
  group.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(group),c=new THREE.Vector3(),ext=new THREE.Vector3();
  box.getCenter(c);box.getSize(ext);
  const root=new THREE.Group();group.position.sub(c);root.add(group);root.rotation.y=yawDeg*D;
  const r=Math.max(ext.x,ext.y,ext.z)*.5,dist=r/Math.tan(15*D)*1.32;
  const scene=new THREE.Scene();scene.add(root);
  scene.add(new THREE.AmbientLight(new THREE.Color(170/255,170/255,180/255),2.7));
  const dl=new THREE.DirectionalLight(new THREE.Color(1,.98,.94),2.3);dl.position.set(.5,1,.6).multiplyScalar(10);scene.add(dl);
  const cam=new THREE.PerspectiveCamera(30,w/h,.1,1000);cam.position.set(0,r*.35,-dist);cam.lookAt(0,0,0);
  return {scene,cam};
}
window.renderItem=function(name,w,h,geo,opt){
  opt=opt||{};let g,yaw=-28,pre=null;
  if(opt.geo){g=fromGeo(geo[opt.geo],opt.rainbow);yaw=opt.yaw;if(opt.rz!==undefined)pre=new THREE.Matrix4().makeRotationZ(opt.rz*D);
  } else
  if(name==='spear'){g=fromGeo(geo.spear);pre=new THREE.Matrix4().makeRotationZ(-42*D);yaw=20}
  else if(name==='charm'){g=fromGeo(geo.rabbit,true)}
  else g=buildIcon(name);
  const rd=window.__rd||(window.__rd=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true}));
  rd.outputColorSpace=THREE.LinearSRGBColorSpace;rd.setPixelRatio(1);rd.setSize(w,h);rd.setClearColor(0x000000,0);
  const {scene,cam}=frame(g,yaw,w,h,pre);
  rd.render(scene,cam);return rd.domElement.toDataURL('image/png');
};
