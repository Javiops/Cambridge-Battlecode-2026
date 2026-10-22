"""Candidate-side kills/g, champion damage per kill, deaths/g, gems/g, clears/g over panel dirs; optional stdout tag count (e.g. '[rpunish] start') from the replay bundle."""
import json, glob, os, sys, zipfile, collections
PAN=os.environ.get('PAN','pA,pB,pC,pInv,pD,pF,pE,pG,pM').split(',')
tags=sys.argv[2:]
for bot in sys.argv[1].split(','):
    C=collections.Counter(); n=0
    for p in PAN:
        for f in glob.glob(f'res/cal_{bot}_{p}/[AB]_*.json'):
            b=os.path.basename(f); cand='teamA' if b.startswith('A_') else 'teamB'; d=json.load(open(f)); n+=1
            for c in d['champions']:
                if c['team']!=cand: continue
                m=c['metrics']; C['kills']+=int(m['kills']); C['dmg']+=float(m['championDamageDone']); C['gems']+=int(m['submittedGems'])
                if c['name']!='Issac': C['deaths']+=int(m['deaths'])
            C['clears']+=sum(len(e['entries']) for e in d['events'] if e['kind']=='campClear' and isinstance(e.get('owner'),dict) and e['owner'].get('team')==cand)
            if tags:
                try:
                    z=zipfile.ZipFile(f[:-5]+'.repl26a'); out=z.read('team-a.stdout' if cand=='teamA' else 'team-b.stdout').decode(errors='ignore')
                    for t in tags: C[t]+=out.count(t)
                except Exception as ex: C['logerr']+=1
    s=f"{bot:16s} games {n} kills/g {C['kills']/n:.2f} dmg/kill {C['dmg']/max(1,C['kills']):.0f} deaths/g {C['deaths']/n:.2f} gems/g {C['gems']/n:.0f} clears/g {C['clears']/n:.1f}"
    for t in tags: s+=f"  '{t}'/g {C[t]/n:.2f}"
    print(s)
