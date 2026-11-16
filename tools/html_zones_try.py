"""Zones of the web world (SpearHunt_World_v15.html) -> Roblox parts, a first try (V36).

Usage:  python -I -X utf8 html_zones_try.py 1,2,3 48     (zone ids, colour step)
Needs world_data.bin in the current folder: the 24.8 MB JSON that the HTML keeps gzip+base64 inside its second
<script> (window.WORLD_DATA_READY=...atob("...")). Decode: base64 -> gzip.decompress -> save as world_data.bin.
Writes HtmlZones_try.rbxmx: per zone the three hero models of the HTML (structure, canopy, feature) at 1 stud
resolution (2x2x2 cells merged, colours quantized, boxes merged by vox2boxes.merge) plus the authored landmark boxes.
Heights are the zone levels of the HTML; in Studio the models were dropped onto the game's own ground.
Only landmark parts of geometry 'box' are converted (rock, crystal, canopy, pyramid are skipped).
"""
import json,collections,math,sys
sys.path.insert(0,'.')
from vox2boxes import merge,quant,rgb
d=json.load(open('world_data.bin',encoding='utf-8'))
M=0xFFFFFFFF
def rng(seed):
    s=[seed&M]
    def r():
        x=s[0]
        x^=(x<<13)&M; x^=x>>17; x^=(x<<5)&M
        s[0]=x
        return x/4294967296
    return r
zones={z['id']:z for z in d['WORLD_CATALOG']['zones']}
widths=[190,194,202,220,238,234,240,250,256,246,276,296,260,264,244,268,276,270,284,286,302,290,320,304,320]
levels=[3,5,3.5,10,7,10,10,10,4,25,3,-23,20]
ZONES=[int(a) for a in sys.argv[1].split(',')] if len(sys.argv)>1 else [1,2,3]
STEP=int(sys.argv[2]) if len(sys.argv)>2 else 48
em={m['id']:m for m in d['ENVIRONMENT_MODELS']['models']}

def downsample(m):
    blocks=collections.defaultdict(collections.Counter)
    for ix,iy,iz,c,*_ in m['voxels']:
        blocks[(ix//2,iy//2,iz//2)][quant(c,STEP)]+=1
    cells=[]
    for (bx,by,bz),cnt in blocks.items():
        (r,g,b),_=cnt.most_common(1)[0]
        cells.append([bx,by,bz,(r<<16)|(g<<8)|b,0])
    return cells

def hero_positions(zid):
    z=zones[zid]; w=widths[zid-1]; start,end=z['from'],z['to']; length=end-start
    r=rng(13069+zid*593)
    out=[]
    for kind,sx,u in (('structure',-.33,.24),('canopy',.31,.5),('feature',-.29,.76)):
        x=w*sx+(r()-.5)*10
        zz=-(start+length*max(.1,min(.9,u+(r()-.5)*.32)))
        out.append((kind,x,zz))
    return out

_ref=[0]
def ref():
    _ref[0]+=1
    return 'RBX%032X'%_ref[0]
def part_xml(name,cx,cy,cz,sx,sy,sz,rgb24,rot=None,collide=True,mat=256):
    r00,r01,r02,r10,r11,r12,r20,r21,r22=rot or (1,0,0,0,1,0,0,0,1)
    col=(0xFF<<24)|rgb24
    return ('<Item class="Part" referent="%s"><Properties><token name="shape">1</token><bool name="Anchored">true</bool>'
     '<CoordinateFrame name="CFrame"><X>%.4f</X><Y>%.4f</Y><Z>%.4f</Z><R00>%.6f</R00><R01>%.6f</R01><R02>%.6f</R02><R10>%.6f</R10><R11>%.6f</R11><R12>%.6f</R12><R20>%.6f</R20><R21>%.6f</R21><R22>%.6f</R22></CoordinateFrame>'
     '<bool name="CanCollide">%s</bool><bool name="CanTouch">false</bool><bool name="CastShadow">false</bool><Color3uint8 name="Color3uint8">%d</Color3uint8>'
     '<token name="Material">%d</token><string name="Name">%s</string><Vector3 name="size"><X>%.4f</X><Y>%.4f</Y><Z>%.4f</Z></Vector3></Properties></Item>')%(ref(),cx,cy,cz,r00,r01,r02,r10,r11,r12,r20,r21,r22,'true' if collide else 'false',col,mat,name,sx,sy,sz)
def container(cls,name,children,extra=''):
    return '<Item class="%s" referent="%s"><Properties><string name="Name">%s</string>%s</Properties>%s</Item>'%(cls,ref(),name,extra,''.join(children))

total=0
zone_items=[]
report=[]
for zid in ZONES:
    items=[]
    base_y=levels[zid-1] if zid<=len(levels) else 0
    for kind,x,z in hero_positions(zid):
        mid='env_%02d_%s'%(zid,kind)
        m=em[mid]; cells=downsample(m)
        boxes=merge(cells,1)   # colours are already quantized; step 1 keeps them
        ox,oy,oz=m['origin']
        parts=[]
        for x0,y0,z0,x1,y1,z1,col in boxes:
            sx,sy,sz=(x1-x0+1),(y1-y0+1),(z1-z0+1)
            cx=x+ox+(x0+x1)/2+0.25; cy=base_y+oy+(y0+y1)/2+0.25; cz=z+oz+(z0+z1)/2+0.25
            parts.append(part_xml('p',cx,cy,cz,sx,sy,sz,(col[0]<<16)|(col[1]<<8)|col[2]))
        total+=len(parts)
        items.append(container('Model',mid,parts,'<bool name="NeedsPivotMigration">false</bool>'))
        report.append((mid,len(m['voxels']),len(cells),len(parts),round(x,1),round(z,1)))
    # authored landmark boxes of this zone
    lp=[p for p in d['VOXEL_PLACEMENTS']['landmarkParts'] if p['zone']==zid]
    parts=[]
    for p in lp:
        if p.get('geometry')!='box': continue
        rx,ry,rz=p['rotation']
        # Euler XYZ (three.js) -> matrix
        cx_,sx_=math.cos(rx),math.sin(rx);cy_,sy_=math.cos(ry),math.sin(ry);cz_,sz_=math.cos(rz),math.sin(rz)
        # R = Rx*Ry*Rz? three.js 'XYZ' order = Rx*Ry*Rz
        R=[[cy_*cz_,-cy_*sz_,sy_],[cx_*sz_+sx_*sy_*cz_,cx_*cz_-sx_*sy_*sz_,-sx_*cy_],[sx_*sz_-cx_*sy_*cz_,sx_*cz_+cx_*sy_*sz_,cx_*cy_]]
        px,py,pz=p['position']
        parts.append(part_xml('lm',px,py,pz,p['size'][0],p['size'][1],p['size'][2],p['color'],rot=(R[0][0],R[0][1],R[0][2],R[1][0],R[1][1],R[1][2],R[2][0],R[2][1],R[2][2])))
    total+=len(parts)
    items.append(container('Folder','landmarkParts',parts))
    report.append(('zone%d landmarkParts'%zid,len(lp),0,len(parts),0,0))
    zone_items.append(container('Folder','Zone%d'%zid,items))
root=container('Model','HtmlZonesTry',zone_items,'<bool name="NeedsPivotMigration">false</bool>')
xml="<?xml version='1.0' encoding='utf-8'?><roblox version=\"4\">"+root+"</roblox>"
open('HtmlZones_try.rbxmx','w',encoding='utf-8').write(xml)
print('total parts',total,'bytes',len(xml))
for r in report: print(r)
print('geometries:',collections.Counter(p['geometry'] for p in d['VOXEL_PLACEMENTS']['landmarkParts']))
