# fight4b.py INDEX.json BOT OUT.json: even contact episodes r21-200, both sides: per-slot ability use (cd rises), hp at use, distance to nearest foe at use
import sys,os,json,collections
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
IDX,BOT,OUT=sys.argv[1:4]; D=os.path.dirname(IDX)
def P(c): return (c['x'],c['y'])
def one(e):
    try: R=dump(os.path.join(D,e['file']),camps=False,timeout=2400)
    except Exception: return None
    if not R: return None
    ours=0 if e['side']=='a' else 1
    byr={}
    for r in R: byr.setdefault(r['round'],r)
    typ={c['index']:c['typeName'] for c in R[0]['champions']}
    T=collections.Counter(); state={}; prevcd={}
    def add(s,t,m,v=1): T[f"{s}|{t}|{m}"]+=v
    for r in range(21,201):
        if r not in byr: continue
        C={c['index']:c for c in byr[r]['champions']}
        for i,c in C.items():
            s='us' if c['team']==ours else 'them'; t=typ[i]
            if not c['alive']: state.pop(i,None); prevcd.pop(i,None); continue
            used=[k for k in (0,1) if i in prevcd and c['cd'][k]>prevcd[i][k]]; prevcd[i]=c['cd']
            al=[o for o in C.values() if o['team']==c['team'] and o['alive']]; en=[o for o in C.values() if o['team']!=c['team'] and o['alive']]
            dn=min([cheb(P(c),P(o)) for o in en] or [99])
            ep=state.get(i)
            if ep is None:
                if dn>3: continue
                na=sum(cheb(P(c),P(o))<=4 for o in al); nf=sum(cheb(P(c),P(o))<=4 for o in en)
                ep={'cls':'even' if na==nf else 'x','start':r,'quiet':0}; state[i]=ep
                if ep['cls']=='even': add(s,t,'ep')
            if ep['cls']=='even':
                add(s,t,'rounds')
                for k in used:
                    add(s,t,f's{k}'); add(s,t,f's{k}_hp',c['health']/c['maxHealth']); add(s,t,f's{k}_dn',min(dn,8))
                    if r-ep['start']<=1: add(s,t,f's{k}_first2')
            ep['quiet']=0 if dn<=3 else ep['quiet']+1
            if ep['quiet']>=3: state.pop(i,None)
    return dict(T)
I=[e for e in json.load(open(IDX)) if e['bot']==BOT]
T=collections.Counter(); g=0
with ProcessPoolExecutor(4) as ex:
    for o in ex.map(one,I):
        if o: T.update(o); g+=1
json.dump({'games':g,'T':T},open(OUT,'w')); print('games',g)
