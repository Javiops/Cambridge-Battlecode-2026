# divq.py A B: online pairs: games where results differ between bot dirs A and B on near maps; first divergence round and context
import json,gzip,os,sys,collections
W='/tmp/claude-0/w'; A,B=sys.argv[1],sys.argv[2]
near=set(open('/tmp/claude-0/-home-user-cambridge-battlecode-2026/3dc070b2-a00b-5e31-ba97-59618d5276fa/scratchpad/near.txt').read().split())
T=json.load(open(f'{W}/c34index.json')); I={(x['bot'],os.path.basename(x['file'])):x for x in T}
N={1:'Ves',7:'Mar',12:'HoR',0:'Ryt',2:'Ven'}
ch=lambda a,b:max(abs(a[3]-b[3]),abs(a[4]-b[4]))
def ld(d,f): return json.load(gzip.open(f'{W}/dec/{d}/'+f.replace('.repl26a','.json.gz')))
for x in T:
    if x['bot']!=A.replace('on_','') or x['map'] not in near: continue
    b=os.path.basename(x['file']); y=I.get((B.replace('on_',''),b))
    if not y or y['result']==x['result']: continue
    us=0 if x['side']=='a' else 1
    DA,DB=ld(A,b),ld(B,b)
    RA,RB=DA['rounds'],DB['rounds']
    k=next((i for i,(p,q) in enumerate(zip(RA,RB)) if [(c[0],c[3],c[4]) for c in p['c']]!=[(c[0],c[3],c[4]) for c in q['c']]),None)
    print(f"## {x['map']} {x['rival']} side {x['side']}: {A} {x['result']} / {B} {y['result']}; first divergence round {RA[k]['r'] if k is not None else None}")
    if k is None: continue
    for tag,R in ((A,RA),(B,RB)):
        row=R[k]; prev=R[k-1]
        cs={c[2]:c for c in row['c'] if c[1]==us}; pc={c[2]:c for c in prev['c'] if c[1]==us}; en=[c for c in prev['c'] if c[1]!=us and c[9]]
        moved=[t for t in cs if t in pc and (cs[t][3],cs[t][4])!=(RB[k]['c'][0][3],0) ]
        s=[]
        for t,c in cs.items():
            p=pc.get(t)
            nf=sum(1 for e in en if ch(e,p)<=6) if p else 0
            s.append(f"{N.get(t)} ({p[3]},{p[4]})->({c[3]},{c[4]}) hp{int(p[5])}/{int(p[6])} foes<=6:{nf}" if p else '')
        # 20-round outcome
        j=min(k+20,len(R)-1); dd=sum(1 for c in R[j]['c'] if c[1]==us and not c[9]); de=sum(1 for c in R[j]['c'] if c[1]!=us and not c[9])
        caps=sum(1 for g,t,r in (DA if tag==A else DB)['caps'] if t==us and RA[k]['r']<=r<=RA[k]['r']+20)
        print(f"  {tag}: "+'; '.join(s)); print(f"     +20r: ours dead {dd}, theirs dead {de}, our caps {caps}, gems at end {(DA if tag==A else DB)['meta']['gems']}")
