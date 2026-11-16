import json,collections
def rgb(c): return ((c>>16)&255,(c>>8)&255,c&255)
def quant(c,step):
    r,g,b=rgb(c)
    f=lambda v:min(255,int(round(v/step))*step)
    return (f(r),f(g),f(b))
def merge(cells,step):
    """cells: list of [ix,iy,iz,color,flag] -> list of boxes (x0,y0,z0,x1,y1,z1,(r,g,b)) in cell units (inclusive)"""
    bycol=collections.defaultdict(list)
    for ix,iy,iz,c,*_ in cells: bycol[quant(c,step)].append((ix,iy,iz))
    boxes=[]
    for col,lst in bycol.items():
        rows=collections.defaultdict(list)
        for ix,iy,iz in lst: rows[(iy,iz)].append(ix)
        runs=collections.defaultdict(list)   # iy -> list of (x0,x1,z)
        for (iy,iz),xs in rows.items():
            xs.sort(); i=0
            while i<len(xs):
                j=i
                while j+1<len(xs) and xs[j+1]==xs[j]+1: j+=1
                runs[iy].append((xs[i],xs[j],iz)); i=j+1
        rects=collections.defaultdict(list)  # iy -> (x0,x1,z0,z1)
        for iy,rr in runs.items():
            rr.sort(key=lambda t:(t[0],t[1],t[2]))
            openr={}
            for x0,x1,z in rr:
                k=(x0,x1); o=openr.get(k)
                if o and o[3]==z-1: o[3]=z
                else:
                    o=[x0,x1,z,z]; openr[k]=o; rects[iy].append(o)
        openb={}
        for iy in sorted(rects):
            nxt={}
            for x0,x1,z0,z1 in rects[iy]:
                k=(x0,x1,z0,z1); o=openb.get(k)
                if o and o[5]==iy-1: o[5]=iy
                else:
                    o=[x0,iy,z0,x1,iy,z1,col]; boxes.append(o)
                nxt[k]=o
            openb=nxt
    return boxes
if __name__=='__main__':
    d=json.load(open('world_data.bin',encoding='utf-8'))
    em=d['ENVIRONMENT_MODELS']['models']
    for step in (32,64):
        tot=0; per=[]
        for m in em:
            n=len(merge(m['voxels'],step)); tot+=n; per.append((m['id'],len(m['voxels']),n))
        print('step',step,'total boxes',tot)
        print('  hero-size sample:',per[:3],per[25:28],per[50:53])
