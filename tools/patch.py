import struct, sys, lz4.block, zstandard
from rbx import parse, unzig, read_ints, accum
src, dst, newfile, target = sys.argv[1:5]   # target = path suffix of the ModuleScript, e.g. StarterPlayer/StarterPlayerScripts/Client/Shop
data = open(src,'rb').read()
inst,parent,props = parse(src)
def path(i):
    r=[]
    while i in parent and i!=-1:
        r.append(props.get(i,{}).get('Name',b'?').decode()); i=parent[i]
    return '/'.join(reversed(r))
hits=[i for i,c in inst.items() if c=='ModuleScript' and path(i)==target]
assert len(hits)==1, hits
ref=hits[0]
# raw chunk walk
p=32; chunks=[]
while p<len(data):
    name=data[p:p+4]; cl,ul,res=struct.unpack('<iii',data[p+4:p+16])
    n=cl if cl else ul
    chunks.append([name,cl,ul,res,data[p+16:p+16+n]]); p+=16+n
    if name.startswith(b'END'): break
assert p==len(data)
def body(c):
    name,cl,ul,res,raw=c
    if cl==0: return raw
    if raw[:4]==b'\x28\xb5\x2f\xfd': return zstandard.ZstdDecompressor().decompress(raw,max_output_size=ul)
    return lz4.block.decompress(raw,uncompressed_size=ul)
# find ModuleScript class id and its referent order
cid=None
for c in chunks:
    if c[0]==b'INST':
        b=body(c); k,=struct.unpack('<i',b[:4]); l,=struct.unpack('<i',b[4:8])
        if b[8:8+l]==b'ModuleScript':
            cid=k; n,=struct.unpack('<i',b[9+l:13+l]); ids=accum(read_ints(b[13+l:13+l+4*n],n))
assert cid is not None and ref in ids
idx=ids.index(ref)
new=open(newfile,'rb').read()
done=False
for c in chunks:
    if c[0]==b'PROP':
        b=body(c); k,=struct.unpack('<i',b[:4]); l,=struct.unpack('<i',b[4:8])
        if k==cid and b[8:8+l]==b'Source':
            q=9+l; out=[b[:q]]; 
            for i in range(len(ids)):
                sl,=struct.unpack('<i',b[q:q+4]); s=b[q+4:q+4+sl]; q+=4+sl
                if i==idx:
                    old=s; s=new
                out.append(struct.pack('<i',len(s))+s)
            assert q==len(b)
            nb=b''.join(out)
            if c[4][:4]==b'\x28\xb5\x2f\xfd':
                comp=zstandard.ZstdCompressor(level=19).compress(nb)
            else:
                comp=lz4.block.compress(nb,store_size=False,mode='high_compression',compression=9)
            c[1],c[2],c[4]=len(comp),len(nb),comp
            done=True
assert done
hdr=data[:32]
outb=hdr+b''.join(c[0]+struct.pack('<iii',c[1],c[2],c[3])+c[4] for c in chunks)
open(dst,'wb').write(outb)
print('patched', target, 'old',len(old),'new',len(new), 'file',len(data),'->',len(outb))
