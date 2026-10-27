# t10plan.py SEL.json DIR OUT.json: per champion type, winner vs loser, per 50-round bucket r1-400: activity, allies within 4, home distance, own half, gems carried, deaths
import sys,os,json,collections
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
SEL,DIR,OUT=sys.argv[1:4]
def P(c): return (c['x'],c['y'])
def one(e):
    try: R=dump(os.path.join(DIR,e['file']),camps=True,timeout=2400)
    except Exception: return None
    if not R: return None
    win=0 if e['a_result']=='win' else 1
    byr={}
    for r in R: byr.setdefault(r['round'],r)
    r0=byr[min(byr)]
    home={t:(lambda L:(sum(x for x,y in L)//len(L),sum(y for x,y in L)//len(L)))([P(c) for c in r0['champions'] if c['team']==t]) for t in (0,1)}
    T=collections.Counter(); prev={}
    for r in range(1,401):
        if r not in byr: continue
        C=byr[r]['champions']; camps=[(k['x'],k['y']) for k in byr[r].get('camps',[]) if k.get('alive')]
        b=(r-1)//50
        for c in C:
            lab='W' if c['team']==win else 'L'; t=c['typeName']; key=f"{lab}|{t}|{b}"
            T[key+'|n']+=1
            pv=prev.get(c['index'])
            if pv and pv['alive'] and not c['alive']: T[key+'|death']+=1
            prev[c['index']]=c
            if not c['alive']: T[key+'|dead']+=1; continue
            p=P(c); en=[o for o in C if o['team']!=c['team'] and o['alive']]; al=[o for o in C if o['team']==c['team'] and o['alive'] and o['index']!=c['index']]
            dh=cheb(p,home[c['team']]); de=cheb(p,home[1-c['team']])
            T[key+'|alive']+=1; T[key+'|dhome']+=dh; T[key+'|ownhalf']+=int(dh<de); T[key+'|athome']+=int(dh<=5)
            T[key+'|al4']+=sum(cheb(p,P(o))<=4 for o in al); T[key+'|gems']+=c['gems']
            if any(cheb(p,P(o))<=3 for o in en): T[key+'|fight']+=1
            elif camps and min(cheb(p,q) for q in camps)<=2: T[key+'|camp']+=1
            elif pv and pv['alive'] and P(pv)!=p: T[key+'|walk']+=1
            else: T[key+'|idle']+=1
    return dict(T)
S=json.load(open(SEL)); T=collections.Counter(); g=0
with ProcessPoolExecutor(4) as ex:
    for o in ex.map(one,S):
        if o: T.update(o); g+=1
json.dump({'games':g,'T':T},open(OUT,'w')); print('games',g)
