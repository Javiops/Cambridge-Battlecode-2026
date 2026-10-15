import sys, json, glob, collections
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
sel={d['match']:d for d in json.load(open(S+'/ws/selected.json'))}
maps={m.split('/')[-1][:-5]:json.load(open(m)) for m in glob.glob(S+'/ws/mapsj/*.json')}
stat=collections.defaultdict(lambda: collections.Counter())
for f in sorted(glob.glob(S+'/ws/steps/*.jsonl'))[:40]:
    mid=f.split('/')[-1].split('.')[0]
    if mid not in sel: continue
    mp=maps[sel[mid]['map']]; grid=mp['grid']
    altars=[(x,y) for y,row in enumerate(grid) for x,c in enumerate(row) if c=='A']
    sa=mp['spawnA']
    rounds=[]; evs=[]
    for line in open(f):
        d=json.loads(line)
        if d['t']=='round': rounds.append(d)
        elif d['t']=='ev': evs.append(d)
    snap={r['r']:{c[0]:c for c in r['champs']} for r in rounds}
    # recall jumps: pos eff with ph14, k4, jump >2
    jumps=collections.defaultdict(list); tribdone=collections.defaultdict(list)
    for e in evs:
        if e['ak']==1 and e['k']==4 and e['ph']==14:
            for x in e['eff']:
                if x['i']==e['a'] and 'pos' in x and max(abs(x['pos'][0]-x['pos'][2]),abs(x['pos'][1]-x['pos'][3]))>2: jumps[e['a']].append(e['r'])
        if e['ak']==1 and e['ph'] in (13,14):
            for x in e['eff']:
                if x.get('gems',0)<0: tribdone[x['i']].append(e['r'])
    for e in evs:
        if e['ak']!=1 or e['k'] not in (11,12,14,18,20,23,26): continue
        k=e['k']; a=e['a']; p=e['apos']; r=e['r']
        c=snap.get(r,{}).get(a) or snap.get(r-1,{}).get(a)
        st=stat[k]; st['n']+=1
        if p is None: continue
        if any(max(abs(p[0]-ax),abs(p[1]-ay))<=1 for ax,ay in altars): st['at_altar']+=1
        if grid[p[1]][p[0]]=='"': st['in_bush']+=1
        if any(r<j<=r+7 for j in jumps[a]): st['jump_7']+=1
        if any(r<=j<=r+6 for j in tribdone[a]): st['trib_6']+=1
        if c and c[7]>0: st['gems>0']+=1
        if c and c[5]<0.4*c[6]: st['hp<40']+=1
        # also what the effs are
        if e['eff']: st['has_eff']+=1
for k,st in sorted(stat.items()): print(k, dict(st))
