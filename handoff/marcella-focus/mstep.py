#!/usr/bin/env python3
"""mstep.py t10|LOCALRES N OUT.json : every-step decode r30-300; Marcella's damage to enemy champions per step kind:
first attack of the turn, second attack (after an ability = reset), ability with damage (2 x Focus spell)."""
import sys,json,subprocess,os,collections,glob
from concurrent.futures import ProcessPoolExecutor
os.environ['CAMBC_VIS_WASM']='/mnt/project-files/analysis/local-filter-1021/scripts/v1_0_3-DRqNt1t2.wasm'
def one(a):
    z,team=a
    p=subprocess.Popen(['node','/mnt/project-files/online/tools/replaydump.js',z,'--every-step'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
    prev=None; out=collections.Counter(); turn=None
    for l in p.stdout:
        d=json.loads(l); r=d['round']
        if r>300: break
        st=d['step']; C={c['index']:c for c in d['champions']}
        if prev and st['actorKind']==1 and r>=30:
            a=st['actorIndex']
            if C[a]['team']==team and C[a]['typeName']=='Marcella':
                if turn!=(a,r): turn=(a,r); natk=0; ab=False
                dmg=sum(prev[k]['health']-c['health'] for k,c in C.items() if c['team']!=team and k in prev and c['health']<prev[k]['health'])
                ph='r30-150' if r<150 else 'r150-300'
                k=st['kind']
                if k==5:
                    cat='atk2' if natk>=1 else 'atk1'; natk+=1
                    if dmg>0: out[(ph,cat,'n')]+=1; out[(ph,cat,'d')]+=dmg
                elif k==6:
                    if dmg>0: out[(ph,'spell','n')]+=1; out[(ph,'spell','d')]+=dmg
                    else: out[(ph,'ab0','n')]+=1
        prev=C
    p.kill()
    return {'|'.join(k):v for k,v in out.items()}
def jobs(w,n):
    if w=='t10':
        L=json.load(open('/mnt/project-files/online/data/t10_vs_band_1024/index.json'))['games']; R='/mnt/project-files/online/data/replays/'
        J=[(R+g['match']+'.zip',0 if g['side']=='a' else 1) for g in L if not g.get('far') and '6' in g['draft'] and os.path.exists(R+g['match']+'.zip')]
    else: J=[(z,0 if os.path.basename(z).startswith('A_') else 1) for z in sorted(glob.glob(w+'/*/*.repl26a'))]
    return J[:n]
if __name__=='__main__':
    J=jobs(sys.argv[1],int(sys.argv[2])); T=collections.Counter(); g=0
    with ProcessPoolExecutor(4) as ex:
        for o in ex.map(one,J):
            g+=1
            for k,v in o.items(): T[tuple(k.split('|'))]+=v
    json.dump({'games':g,'T':{'|'.join(k):v for k,v in T.items()}},open(sys.argv[3],'w'))
    print(sys.argv[1],'games',g)
    for ph in ('r30-150','r150-300'):
        print(' ',ph,' '.join(f"{c}: {T[(ph,c,'n')]/g:.1f}/g x {T[(ph,c,'d')]/max(1,T[(ph,c,'n')]):.0f}" for c in ('atk1','atk2','spell')), f"reset(no dmg ability) {T[(ph,'ab0','n')]/g:.1f}/g")
