# usage: python up.py ids.json file1.glb file2.glb ...   (paths relative to C:\SpearHuntAssets)
import subprocess, json, os, sys, threading, queue, time
bat=os.path.join(os.environ['LOCALAPPDATA'],'Roblox','mcp.bat')
p=subprocess.Popen(['cmd','/c',bat],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
q=queue.Queue(); threading.Thread(target=lambda:[q.put(l) for l in p.stdout],daemon=True).start()
nid=[10]
def call(name,args,t=180):
    nid[0]+=1; i=nid[0]
    p.stdin.write((json.dumps({"jsonrpc":"2.0","id":i,"method":"tools/call","params":{"name":name,"arguments":args}})+'\n').encode()); p.stdin.flush()
    end=time.time()+t
    while time.time()<end:
        try: line=q.get(timeout=1)
        except queue.Empty: continue
        try: o=json.loads(line)
        except Exception: continue
        if o.get('id')==i:
            r=o.get('result',{}); return ''.join(c.get('text','') for c in r.get('content',[]))
    return 'TIMEOUT'
p.stdin.write((json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"uploader","version":"1"}}})+'\n').encode()); p.stdin.flush()
time.sleep(3); p.stdin.write((json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})+'\n').encode()); p.stdin.flush()
time.sleep(4)
def sid():
    for _ in range(30):
        st=call('list_roblox_studios',{})
        try:
            for s in json.loads(st)['studios']:
                if '.rbxl' not in (s.get('file') or s.get('name') or ''):
                    return s['id']
        except Exception: pass
        time.sleep(2)
idsf=sys.argv[1]; files=[l.strip() for l in open(sys.argv[2]) if l.strip()]
out=json.load(open(idsf)) if os.path.exists(idsf) else {}
todo=[f for f in files if os.path.basename(f)[:-4] not in out]
print("todo",len(todo)); sys.stdout.flush()
CH=20
for c0 in range(0,len(todo),CH):
    ops={}
    for f in todo[c0:c0+CH]:
        k=os.path.basename(f)[:-4]
        body=json.dumps({"request":{"assetType":"Model","displayName":"SH "+k,"description":"SpearHunt model "+k,"creationContext":{"creator":{"userId":"3410115474"}}}})
        for attempt in range(20):
            r=call('open_cloud_invoke',{"studio_id":sid(),"method":"POST","endpoint":"/assets/v1/assets","body":body,"files":[{"name":"fileContent","path":os.path.join(r"C:\SpearHuntAssets",*f.split("/"))}],"scopes":["asset:read","asset:write"]})
            try:
                j=json.loads(r[r.index('{'):]); ops[k]=j['operationId']; break
            except Exception:
                print('retry',k,r[:140]); sys.stdout.flush(); time.sleep(5 if '429' not in r and 'ate' not in r else 30)
    for rnd in range(120):
        if not ops: break
        time.sleep(4)
        for k,op in list(ops.items()):
            r=call('open_cloud_invoke',{"studio_id":sid(),"method":"GET","endpoint":"/assets/v1/operations/"+op,"scopes":["asset:read"]})
            try:
                j=json.loads(r[r.index('{'):])
                if j.get('done'):
                    resp=j.get('response',{}); out[k]=resp.get('assetId')
                    st=resp.get('moderationResult',{}).get('moderationState')
                    if st!='Approved': print('MOD',k,st)
                    del ops[k]
            except Exception: pass
    json.dump(out,open(idsf,'w'),indent=1)
    print('chunk',c0//CH,'total',len(out),'pending',list(ops)); sys.stdout.flush()
print('DONE total',len(out))
p.kill()
