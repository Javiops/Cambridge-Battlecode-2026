import json,sys
# deaths.py FILE... : per game, our deaths/kills by round (<=R) and team gold/gems timeline
R=int(sys.argv[1]); files=sys.argv[2:]
for f in files:
    d=json.load(open(f)); us='teamA' if '/A_' in f else 'teamB'
    deaths={'us':[], 'them':[]}
    for e in d['events']:
        if e.get('kind')!='death': continue
        team=e['owner']['team']; nm=e['owner']['name'][:4]
        for en in e['entries']:
            r=en['timestamp']['round']
            if r<=R: deaths['us' if team==us else 'them'].append((r,nm))
    tl={}
    for t in d['teamTimelines']:
        if str(t['owner'])==us or (isinstance(t['owner'],dict) and t['owner'].get('team')==us): tl[t['metric']]=t
    out=d['match']['outcome']
    print(f.split('res/')[-1], 'WIN' if out==us else 'loss', 'rounds',d['match']['roundsCompleted'])
    print('  us   ',sorted(deaths['us']))
    print('  them ',sorted(deaths['them']))
    if files.index(f)==0: print('  metrics',list(tl.keys())[:20]); print('  runs sample',json.dumps(list(tl.values())[0])[:300] if tl else '')
