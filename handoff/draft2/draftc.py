import json,subprocess,os,sys,collections
from concurrent.futures import ThreadPoolExecutor
R,IDX=sys.argv[1],sys.argv[2]; D=os.path.dirname(IDX); I=json.load(open(IDX))
def one(e):
    p=subprocess.Popen(['node',R+'/replaydump_pc.js',os.path.join(D,e['file'])],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,env=dict(os.environ,CAMBC_VIS_WASM=R+'/v2_0_0-hWOQ1R8f.wasm'))
    out=None
    for l in p.stdout:
        if l.startswith('{'):
            d=json.loads(l)
            if 'champions' in d and not d.get('draft'): out=d; break
    p.kill(); p.wait()
    if not out: return None
    ours=0 if e['side']=='a' else 1
    return e['bot'],e['result'],[(c['team']==ours,c.get('typeName',c['type'])) for c in out['champions']]
C=collections.defaultdict(collections.Counter); W=collections.defaultdict(collections.Counter); N=collections.Counter()
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(one,I):
        if not r: continue
        b,res,cs=r; N[b]+=1
        for us,t in cs:
            C[(b,'us' if us else 'them')][t]+=1
            if us and res=='win': W[b][t]+=1
for k in sorted(C): print(k,N[k[0]],dict(C[k].most_common()))
for b in W: print(b,'our type in wins',dict(W[b]))
