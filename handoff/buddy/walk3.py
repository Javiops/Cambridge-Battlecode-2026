# walk3.py LIST: r30-150 walking champion-rounds split by gems carried (0 / 1-9 / 10+) and position vs prev round toward altar; pairing per class; also gem banking events per champion
import json,sys,collections
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
L=json.load(open(sys.argv[1])); N=collections.Counter(); P=collections.Counter(); BK=collections.Counter(); NG=0
for fn,us in L:
    home={}; prevg={}
    NG+=1
    for l in open(fn):
        try: d=json.loads(l)
        except: continue
        r=d['round']
        if r<=2:
            for c in d['champions']:
                if c['team']==us and c['x']>=0: home[c['index']]=(c['x'],c['y'])
        M=[c for c in d['champions'] if c['alive'] and c['x']>=0 and c['team']==us and c['typeName']!='Issac']
        for c in M:
            g=c['gems']
            if prevg.get(c['index'],0)>=5 and g==0 and r<=300:
                BK['bank']+=1; BK['bank_g']+=prevg[c['index']]
                o=[ch((c['x'],c['y']),(x['x'],x['y'])) for x in M if x is not c]
                BK['bank_paired']+=bool(o) and min(o)<=3
            prevg[c['index']]=g
        if not 30<=r<150: continue
        K=[k for k in d['camps'] if k['alive']]
        for c in M:
            p=(c['x'],c['y'])
            if any(ch(p,(k['x'],k['y']))<=2 for k in K) or any(ch(p,h)<=3 for h in home.values()): continue
            g=c['gems']; cl='g0' if g==0 else ('g1-9' if g<10 else 'g10+')
            N[cl]+=1; o=[ch(p,(x['x'],x['y'])) for x in M if x is not c]
            P[cl]+=bool(o) and min(o)<=3
T=sum(N.values())
print(sys.argv[1],' '.join(f'{k} {N[k]/T:.0%} paired {P[k]/N[k]:.0%} |' for k in ('g0','g1-9','g10+')), f"banks/game r<=300 {BK['bank']/NG:.1f} gems/bank {BK['bank_g']/max(1,BK['bank']):.1f} paired at bank {BK['bank_paired']/max(1,BK['bank']):.0%}")
