import struct, lz4.block, zstandard, sys
def chunks(data):
    assert data[:8]==b'<roblox!'
    nclass,ninst=struct.unpack('<ii',data[16:24]); p=32; out=[]
    while p<len(data):
        name=data[p:p+4]; cl,ul,_=struct.unpack('<iii',data[p+4:p+16]); p+=16
        if cl==0: body=data[p:p+ul]; p+=ul
        else:
            raw=data[p:p+cl]; p+=cl
            body=zstandard.ZstdDecompressor().decompress(raw,max_output_size=ul) if raw[:4]==b'\x28\xb5\x2f\xfd' else lz4.block.decompress(raw,uncompressed_size=ul)
        out.append((name.rstrip(b'\0').decode(),body))
        if name.startswith(b'END'): break
    return nclass,ninst,out
def unzig(v): return (v>>1) ^ -(v&1)
def read_ints(b,n):
    # interleaved big-endian zigzag int32
    arr=[0]*n
    for i in range(n):
        v=(b[i]<<24)|(b[n+i]<<16)|(b[2*n+i]<<8)|b[3*n+i]; arr[i]=unzig(v)
    return arr
def accum(a):
    o=[];s=0
    for x in a: s+=x;o.append(s)
    return o
def parse(path):
    data=open(path,'rb').read()
    nc,ni,ch=chunks(data)
    classes={};inst={};parent={};props={}
    for name,b in ch:
        if name=='INST':
            cid,=struct.unpack('<i',b[:4]);l,=struct.unpack('<i',b[4:8]);cn=b[8:8+l].decode();p=8+l
            hasserv=b[p];p+=1;n,=struct.unpack('<i',b[p:p+4]);p+=4
            ids=accum(read_ints(b[p:p+4*n],n))
            classes[cid]=(cn,ids)
            for i in ids: inst[i]=cn
        elif name=='PRNT':
            n,=struct.unpack('<i',b[1:5]);p=5
            ch_=accum(read_ints(b[p:p+4*n],n));p+=4*n
            pa=accum(read_ints(b[p:p+4*n],n))
            for c,q in zip(ch_,pa): parent[c]=q
        elif name=='PROP':
            cid,=struct.unpack('<i',b[:4]);l,=struct.unpack('<i',b[4:8]);pn=b[8:8+l].decode();t=b[8+l];p=9+l
            if t==1:
                ids=classes[cid][1];vals=[]
                for i in ids:
                    sl,=struct.unpack('<i',b[p:p+4]);vals.append(b[p+4:p+4+sl]);p+=4+sl
                for i,v in zip(ids,vals): props.setdefault(i,{})[pn]=v
    return inst,parent,props
