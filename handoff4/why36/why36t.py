# why36t.py: one line per loss (c34+c36, v4o2 and e1foco): gems, deaths, outnumbered deaths, big captures, dead champion-rounds
import json,gzip,os,collections
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
print('chain bot map rival | final gems us/riv | deaths r1-150 us/riv | deaths r151-600 us/riv | of which 3+ foes within 6 us/riv | big caps (>=40) r<=600 us/riv | dead champion-rounds r1-600 us/riv')
for x in sorted(T,key=lambda x:(x['chain'],x['bot'],x['map'])):
    if x['result']!='loss': continue
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1
    gv={}
    for k in D['camps']: gv[k[2]]=max(gv.get(k[2],0),k[5] or 0)
    S=[collections.Counter(),collections.Counter()]
    for g,t,r in D['caps']:
        if t in (0,1) and r<=600 and gv.get(g,0)>=40: S[0 if t==us else 1]['big']+=1
    prev={}
    for row in D['rounds']:
        r=row['r']
        if r>600: break
        for c in row['c']:
            i=0 if c[1]==us else 1
            if r>=1 and not c[9]: S[i]['dead']+=1
            p=prev.get(c[0])
            if p and p[9] and not c[9]:
                S[i]['d1' if r<=150 else 'd2']+=1
                if r>150 and sum(1 for a in prev.values() if a[1]!=c[1] and a[9] and ch(a,p)<=6)>=3: S[i]['d3']+=1
        prev={c[0]:c for c in row['c']}
    g=D['meta']['gems']
    print(f"{x['chain']} {x['bot']} {x['map']} {x['rival']} | {g[us]}/{g[1-us]} | {S[0]['d1']}/{S[1]['d1']} | {S[0]['d2']}/{S[1]['d2']} | {S[0]['d3']}/{S[1]['d3']} | {S[0]['big']}/{S[1]['big']} | {S[0]['dead']}/{S[1]['dead']}")
