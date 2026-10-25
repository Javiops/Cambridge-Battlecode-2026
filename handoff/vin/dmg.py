# dmg.py REPLAY OUT.json : every-step decode to r300; champion->enemy champion damage per actor and round, fight rounds (foe <=4 at round end)
import sys,json,subprocess,os,collections
os.environ['CAMBC_VIS_WASM']='/mnt/project-files/analysis/local-filter-1021/scripts/v1_0_3-DRqNt1t2.wasm'
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
p=subprocess.Popen(['node','/mnt/project-files/online/tools/replaydump.js',sys.argv[1],'--every-step'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
prev=None; info={}; D=collections.defaultdict(lambda: collections.defaultdict(int)); FR=collections.defaultdict(list); last=None; cr=None
for l in p.stdout:
    d=json.loads(l); r=d['round']
    if r>300: break
    if cr is not None and r!=cr and last:
        C=[c for c in last['champions'] if c['alive'] and c['x']>=0]
        for c in C:
            e=[f for f in C if f['team']!=c['team'] and ch((c['x'],c['y']),(f['x'],f['y']))<=4]
            if e: FR[cr].append(c['index'])
    cr=r; last=d
    H={c['index']:(c['health'],c['team']) for c in d['champions']}
    for c in d['champions']: info[c['index']]=(c['team'],c['typeName'])
    st=d.get('step',{})
    if prev and st.get('actorKind')==1:
        a=st['actorIndex']; at=info.get(a,(None,))[0]
        for k,(h,t) in H.items():
            if k in prev and h<prev[k][0] and t!=at: D[r][f'{a}>{k}']+=prev[k][0]-h
    prev=H
p.kill()
json.dump({'info':info,'dmg':{r:dict(v) for r,v in D.items()},'fight':FR},open(sys.argv[2],'w'))
