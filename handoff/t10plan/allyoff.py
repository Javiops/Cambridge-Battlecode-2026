# allyoff.py RESDIR OUT.json: local h2h replays (A_*: our bot team 0, B_*: team 1). Per side (us / opp):
# share of alive champion-rounds off spawn (cheb>3 from own spawn) whose nearest alive ally is within 4 (coordmodel gate >55%).
import sys,os,json,glob,collections
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
D,OUT=sys.argv[1:3]
def P(c): return (c['x'],c['y'])
def one(f):
    try: R=dump(f,camps=False,timeout=2400)
    except Exception: return None
    if not R: return None
    us=0 if os.path.basename(f).startswith('A_') else 1
    byr={}
    for r in R: byr.setdefault(r['round'],r)
    r0=byr[min(byr)]
    home={t:(lambda L:(sum(x for x,y in L)/len(L),sum(y for x,y in L)/len(L)))([P(c) for c in r0['champions'] if c['team']==t]) for t in (0,1)}
    T=collections.Counter()
    for r,row in byr.items():
        C=row['champions']
        for c in C:
            if not c['alive']: continue
            p=P(c)
            if cheb(p,home[c['team']])<=3: continue
            side='us' if c['team']==us else 'op'
            al=[cheb(p,P(o)) for o in C if o['team']==c['team'] and o['alive'] and o['index']!=c['index']]
            near=int(bool(al) and min(al)<=4)
            for w in ('all','r51-400' if 51<=r<=400 else None, 'r151-400' if 151<=r<=400 else None):
                if w: T[f"{side}|{w}|n"]+=1; T[f"{side}|{w}|near"]+=near
    return dict(T)
fs=sorted(glob.glob(os.path.join(D,'*.repl26a'))); T=collections.Counter(); g=0
with ProcessPoolExecutor(4) as ex:
    for o in ex.map(one,fs):
        if o: T.update(o); g+=1
res={'games':g}
for s in ('us','op'):
    for w in ('all','r51-400','r151-400'):
        n=T[f"{s}|{w}|n"]; res[f"{s} {w}"]=round(100*T[f"{s}|{w}|near"]/max(1,n),1)
json.dump(res,open(OUT,'w')); print(res)
