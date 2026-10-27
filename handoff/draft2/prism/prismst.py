# prismst.py INDEX.json OUT.json: per game with Prism on the rival side, Prism's summary stats + per-round behaviour
import json,subprocess,os,sys
from concurrent.futures import ThreadPoolExecutor
R='/home/user/cambridge-battlecode-2026/handoff/replay2'; IDX,OUT=sys.argv[1],sys.argv[2]; D=os.path.dirname(IDX)
I=json.load(open(IDX))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def one(e):
    p=subprocess.run(['node',R+'/replaydump_pc.js',os.path.join(D,e['file'])],capture_output=True,text=True,timeout=3000,env=dict(os.environ,CAMBC_VIS_WASM=R+'/v2_0_0-hWOQ1R8f.wasm'))
    rows=[];summ=None
    for l in p.stdout.splitlines():
        if not l.startswith('{'): continue
        d=json.loads(l)
        if d.get('summary'): summ=d
        elif 'champions' in d and not d.get('draft'): rows.append(d)
    if not rows or not summ: return None
    ours=0 if e['side']=='a' else 1; th=1-ours
    pr=[c['index'] for c in rows[0]['champions'] if c['team']==th and c['typeName']=='Prism']
    if not pr: return None
    pi=pr[0]; out={'file':e['file'],'bot':e['bot'],'result':e['result'],'map':e['map'],'rival':e['rival'],'stats':summ['statistics'],'prism':pi,'th':th}
    per=[]; prevcd=None
    for d in rows:
        C={c['index']:c for c in d['champions']}; c=C[pi]
        if not c['alive']: per.append([d['round'],0]); prevcd=None; continue
        al=[cheb((c['x'],c['y']),(o['x'],o['y'])) for o in C.values() if o['team']==th and o['index']!=pi and o['alive']]
        en=[cheb((c['x'],c['y']),(o['x'],o['y'])) for o in C.values() if o['team']!=th and o['alive']]
        cast=[i for i in (0,1) if prevcd is not None and c['cd'][i]>prevcd[i]]
        per.append([d['round'],1,c['x'],c['y'],c['health'],c['maxHealth'],c['gems'],c['gold'],min(al) if al else 99,sum(1 for x in al if x<=4),min(en) if en else 99,sum(1 for x in en if x<=4),cast,c['cd']])
        prevcd=c['cd']
    out['per']=per; return out
def has(e):
    p=subprocess.Popen(['node',R+'/replaydump_pc.js',os.path.join(D,e['file'])],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,env=dict(os.environ,CAMBC_VIS_WASM=R+'/v2_0_0-hWOQ1R8f.wasm'))
    ok=False; th=1 if e['side']=='a' else 0
    for l in p.stdout:
        if l.startswith('{'):
            d=json.loads(l)
            if 'champions' in d and not d.get('draft'): ok=any(c['team']==th and c['typeName']=='Prism' for c in d['champions']); break
    p.kill(); p.wait(); return ok
with ThreadPoolExecutor(8) as ex: H=list(ex.map(has,I))
G=[e for e,h in zip(I,H) if h]; print('prism games',len(G),flush=True)
res=[]
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(lambda e: (lambda: one(e))() if True else None, G):
        if r: res.append(r)
json.dump(res,open(OUT,'w'))
print('games with rival Prism',len(res))
