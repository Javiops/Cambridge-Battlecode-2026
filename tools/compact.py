import sys, json
# usage: compact.py steps.jsonl out.jsonl  -- compress every-step dump to events + round snapshots
src, dst = sys.argv[1], sys.argv[2]
out = open(dst, 'w')
prevC = None; prevK = None; lastRound = None; lastLine = None
ACTION = {4,5,6,11,12,13,14,18,20,23,26,1}
def snap(d):
    return {'t':'round','r':d['round'],'sub':d['submittedGems'],
            'champs':[[c['index'],c['team'],c['typeName'],c['x'],c['y'],c['health'],c['maxHealth'],c['gems'],c['gold'],int(c['alive'])] for c in d['champions']],
            'camps':[[k['index'],k['typeName'],k['x'],k['y'],k['health'],int(k['alive']),int(k['awake']),k['group']] for k in d.get('camps',[])]}
for line in open(src):
    d = json.loads(line)
    if 'round' not in d or 'step' not in d:
        if 'summary' in d: out.write(json.dumps({'t':'summary','stats':d.get('statistics'),'final':d.get('finalRound')})+'\n')
        continue
    r = d['round']
    if lastRound is not None and r != lastRound:
        out.write(json.dumps(snap(lastLine))+'\n')
    lastRound = r; lastLine = d
    s = d['step']
    curC = {c['index']:c for c in d['champions']}
    curK = {k['index']:k for k in d.get('camps',[])}
    eff = []; keff = []
    if prevC:
        for i,c in curC.items():
            p = prevC.get(i)
            if not p: continue
            e = {}
            if (c['x'],c['y']) != (p['x'],p['y']): e['pos'] = [p['x'],p['y'],c['x'],c['y']]
            if c['health'] != p['health']: e['hp'] = c['health']-p['health']
            if c['maxHealth'] != p['maxHealth']: e['maxhp'] = c['maxHealth']-p['maxHealth']
            if c['gems'] != p['gems']: e['gems'] = c['gems']-p['gems']
            if c['gold'] != p['gold']: e['gold'] = c['gold']-p['gold']
            if c['alive'] != p['alive']: e['alive'] = int(c['alive'])
            if e: e['i'] = i; e['hpnow'] = c['health']; eff.append(e)
        for i,k in curK.items():
            p = prevK.get(i)
            if not p: continue
            e = {}
            if k['health'] != p['health']: e['hp'] = k['health']-p['health']
            if k['alive'] != p['alive']: e['alive'] = int(k['alive'])
            if k['awake'] != p['awake']: e['awake'] = int(k['awake'])
            if (k['x'],k['y']) != (p['x'],p['y']): e['pos'] = [p['x'],p['y'],k['x'],k['y']]
            if e: e['i'] = i; e['hpnow'] = k['health']; keff.append(e)
    if eff or keff or (s['actorKind']==1 and s['kind'] in ACTION):
        a = curC.get(s['actorIndex']) if s['actorKind']==1 else None
        out.write(json.dumps({'t':'ev','r':r,'ph':s['phase'],'k':s['kind'],'ak':s['actorKind'],'a':s['actorIndex'],
                              'apos':[a['x'],a['y']] if a else None,'eff':eff,'keff':keff})+'\n')
    prevC = curC; prevK = curK
if lastLine: out.write(json.dumps(snap(lastLine))+'\n')
out.close()
