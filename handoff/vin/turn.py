# turn.py REPLAY TEAM OUT : per champion turn r30-300 of TEAM: nearest foe at turn start, hit (champion dmg), moved, used ability (kind 6 any)
import sys,json,subprocess,os,collections
os.environ['CAMBC_VIS_WASM']='/mnt/project-files/analysis/local-filter-1021/scripts/v1_0_3-DRqNt1t2.wasm'
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
team=int(sys.argv[2])
p=subprocess.Popen(['node','/mnt/project-files/online/tools/replaydump.js',sys.argv[1],'--every-step'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
prev=None; cur=None; out=[]
def flush():
    if cur: out.append(cur)
for l in p.stdout:
    d=json.loads(l); r=d['round']
    if r>300: break
    st=d['step']; C={c['index']:c for c in d['champions']}
    if st['actorKind']==1 and prev and r>=30:
        a=st['actorIndex']
        if C[a]['team']==team:
            if not cur or cur['a']!=a or cur['r']!=r:
                flush()
                pa=prev[a]
                F=[c for c in prev.values() if c['team']!=team and c['alive'] and c['x']>=0]
                fd=min([ch((pa['x'],pa['y']),(c['x'],c['y'])) for c in F] or [99])
                cur={'a':a,'r':r,'t':pa['typeName'],'fd':fd,'hp':pa['health']/pa['maxHealth'],'x0':(pa['x'],pa['y']),'hit':0,'ab':0,'kinds':[]}
            cur['kinds'].append(st['kind'])
            for k,c in C.items():
                if c['team']!=team and k in prev and c['health']<prev[k]['health']: cur['hit']=1
            cur['x1']=(C[a]['x'],C[a]['y'])
    prev=C
flush(); p.kill()
for c in out: c['moved']=int(c['x0']!=c.get('x1',c['x0'])); del c['x0']; c.pop('x1',None)
json.dump(out,open(sys.argv[3],'w'))
