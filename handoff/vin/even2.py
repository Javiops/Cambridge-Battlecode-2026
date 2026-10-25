# even.py LIST: r30-300 champion-rounds in an even fight (foe <=4, allies<=4 +1 == foes<=4) not even last round = episode start.
# 5 rounds later: we dead / a foe within 4 at start dead / still fighting at edge >=+1 / still even or worse / out of fight (no foe <=4). Also hp% at start.
import json,sys,collections
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
L=json.load(open(sys.argv[1])); E=collections.Counter(); H=[]
def edge(c,M,F):
    p=(c['x'],c['y']); f=[x for x in F if ch(p,(x['x'],x['y']))<=4]
    if not f: return None,f
    return 1+sum(1 for x in M if x is not c and ch(p,(x['x'],x['y']))<=4)-len(f),f
for fn,us in L:
    R={}
    for l in open(fn):
        try: d=json.loads(l)
        except: continue
        R[d['round']]=d
    prev={}
    for r in range(30,296):
        if r not in R or r+5 not in R: continue
        C=[c for c in R[r]['champions'] if c['alive'] and c['x']>=0]
        M=[c for c in C if c['team']==us and c['typeName']!='Issac']; F=[c for c in C if c['team']!=us]
        C5=R[r+5]['champions']
        M5=[c for c in C5 if c['alive'] and c['x']>=0 and c['team']==us and c['typeName']!='Issac']; F5=[c for c in C5 if c['alive'] and c['x']>=0 and c['team']!=us]
        for c in M:
            e,f=edge(c,M,F)
            was=prev.get(c['index']); prev[c['index']]=e
            if e!=0 or was==0: continue
            E['n']+=1; H.append(c['health']/c['maxHealth'])
            me5=[x for x in C5 if x['team']==us and x['index']==c['index']][0]
            fid={x['index'] for x in f}
            F5d={x['index']:x for x in C5 if x['team']!=us}
            for x in f:
                y=F5d.get(x['index'])
                E['foe_hp']+=((x['health']-(y['health'] if y and y['alive'] else 0))/x['maxHealth'])/len(f)
                E['foe_hp0']+=x['health']/x['maxHealth']/len(f)
            fdead=any(not x['alive'] for x in C5 if x['team']!=us and x['index'] in fid)
            if not me5['alive']: k='we_die'
            elif fdead: k='foe_dies'
            else:
                e5,_=edge(me5,M5,F5)
                k='out' if e5 is None else ('up' if e5>=1 else 'still_even_or_worse')
            E[k]+=1
            E['hp_lost']+= (c['health']-me5['health'])/c['maxHealth'] if me5['alive'] else c['health']/c['maxHealth']
n=E['n']
print(f"{sys.argv[1]:16s} even starts/game {n/len(L):.0f} hp@start {sum(H)/n:.0%} 5r later: "+' '.join(f"{k} {E[k]/n:.0%}" for k in ('foe_dies','we_die','up','still_even_or_worse','out'))+f" hp lost {E['hp_lost']/n:.0%} foe hp@start {E['foe_hp0']/n:.0%} foe hp lost {E['foe_hp']/n:.0%}")
