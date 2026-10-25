# offcamp.py LIST: r30-150 split champion-rounds by state: at camp (<=2 of live camp), at spawn/home(<=3 of own r1 position), walking; pairing (<=3) per state; foes within 6
import json,sys,collections
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
L=json.load(open(sys.argv[1])); N=collections.Counter(); P=collections.Counter(); H=collections.Counter()
for fn,us in L:
    home={}
    for l in open(fn):
        try: d=json.loads(l)
        except: continue
        r=d['round']
        if r<=2:
            for c in d['champions']:
                if c['team']==us and c['x']>=0: home[c['index']]=(c['x'],c['y'])
        if not 30<=r<150: continue
        M=[c for c in d['champions'] if c['alive'] and c['x']>=0 and c['team']==us and c['typeName']!='Issac']
        K=[k for k in d['camps'] if k['alive']]
        for c in M:
            p=(c['x'],c['y'])
            st='camp' if any(ch(p,(k['x'],k['y']))<=2 for k in K) else ('home' if any(ch(p,h)<=3 for h in home.values()) else 'walk')
            if st=='walk' and c['health']<0.5*c['maxHealth']: st='walk_low'
            N[st]+=1; o=[ch(p,(x['x'],x['y'])) for x in M if x is not c]
            P[st]+=bool(o) and min(o)<=3
print(sys.argv[1],' '.join(f'{s} {N[s]/sum(N.values()):.0%} paired {P[s]/N[s]:.0%} |' for s in ('camp','home','walk','walk_low')))
