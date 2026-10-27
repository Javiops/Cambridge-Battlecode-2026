# bench_jack.py RESDIR... : on maps with a jackpot group (>= 50% of the map's gems), first capture round of it by us / by the rival, and how often each side takes it first
import sys,json,glob,os,collections,statistics as st
T=json.load(open('/tmp/claude-0/ff/gem/cache/mapgroups.json'))
J={}
for m,gs in T.items():
    tot=sum(g['gems'] for g in gs.values()); big=[g for g in gs.values() if g['gems']>=0.5*tot and tot>0]
    if big: J[m]=big[0]
for d in sys.argv[1:]:
    files=glob.glob(f'/tmp/claude-0/ff/ws4/res/{d}/**/*.json',recursive=True); n=0; first=collections.Counter(); R={'us':[],'riv':[]}; caps={'us':0,'riv':0}
    for f in files:
        b=os.path.basename(f); side='teamA' if b.startswith('A_') else 'teamB'; m=b[2:-5]
        if m not in J: continue
        try: j=json.load(open(f))
        except Exception: continue
        n+=1; jg=J[m]; ev=[]
        for e in j['events']:
            if e['kind']!='campClear': continue
            for en in e['entries']:
                if max(abs(jg['cx']-en['x']),abs(jg['cy']-en['y']))<=5: ev.append((en['timestamp']['round'],'us' if e['owner'].get('team')==side else 'riv'))
        ev.sort()
        if ev: first[ev[0][1]]+=1; R[ev[0][1]].append(ev[0][0])
        else: first['none']+=1
        for r,w in ev:
            if r<=600: caps[w]+=1
    if not n: print(d,'no jackpot games'); continue
    print(f"{d:18s} jackpot games {n:3d} | first taken by us {first['us']} (median r{st.median(R['us']) if R['us'] else '-'}), by rival {first['riv']} (median r{st.median(R['riv']) if R['riv'] else '-'}), nobody {first['none']} | jackpot captures <=r600 per game us {caps['us']/n:.2f} riv {caps['riv']/n:.2f}")
print('jackpot maps in table:', sorted(J))
