import sys, json, glob, collections
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
sel=json.load(open(S+'/ws/selected.json'))
bymatch=collections.defaultdict(dict)
for d in sel:
    bymatch[d['match']][d['side']]=('mite' if d['team']=='mite' else 'uni')
    bymatch[d['match']]['other' if d['side']=='a' else 'othera']=d['opp']
teamname={}
for d in sel:
    m=d['match']; me='Mite' if d['team']=='mite' else 'Univardisty'
    teamname[(m,0 if d['side']=='a' else 1)]=me
    teamname[(m,1 if d['side']=='a' else 0)]=d['opp']
cnt=collections.defaultdict(collections.Counter); games=collections.Counter()
near=collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(S+'/ws/steps/*.jsonl')):
    mid=f.split('/')[-1].split('.')[0]
    if (mid,0) not in teamname: continue
    rounds={}; evs=[]
    for line in open(f):
        d=json.loads(line)
        if d['t']=='round': rounds[d['r']]={c[0]:c for c in d['champs']}
        elif d['t']=='ev' and d['ak']==1: evs.append(d)
    teamof={i:c[1] for i,c in rounds[0].items()}
    for t in (0,1): games[teamname[(mid,t)]]+=1
    for e in evs:
        k=e['k']
        if k not in (14,23,20,26): continue
        t=teamof[e['a']]; nm=teamname[(mid,t)]
        cnt[nm][k]+=1
        sn=rounds.get(e['r']-1) or rounds.get(e['r'])
        p=e['apos']
        if sn and p:
            en=any(c[9] and c[1]!=t and max(abs(c[3]-p[0]),abs(c[4]-p[1]))<=8 for c in sn.values())
            near[nm][(k,en)]+=1
for nm in sorted(cnt, key=lambda n:-games[n]):
    g=games[nm]; print(nm, g, {k:round(v/g,1) for k,v in sorted(cnt[nm].items())}, {k:'%d/%d'%(near[nm][(k,True)],near[nm][(k,True)]+near[nm][(k,False)]) for k in (14,23,20,26)})
