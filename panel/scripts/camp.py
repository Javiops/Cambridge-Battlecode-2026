"""Candidate-side camp deaths (death context 'camp'), Stellar camp deaths, champion deaths, captures (campClear), gold earned, per game over the panel dirs."""
import json, glob, os, sys, collections
PAN=sys.argv[2].split(',') if len(sys.argv)>2 else ['pA','pB','pC','pInv','pD','pF']
for bot in sys.argv[1].split(','):
    C=collections.Counter(); n=0
    for p in PAN:
        for f in glob.glob(f'res/cal_{bot}_{p}/[AB]_*.json'):
            cand='teamA' if os.path.basename(f).startswith('A_') else 'teamB'; d=json.load(open(f)); n+=1
            for e in d['events']:
                o=e.get('owner')
                if not isinstance(o,dict) or o.get('team')!=cand: continue
                for x in e['entries']:
                    if e['kind']=='death' and o.get('name')!='Issac':
                        k='camp' if x.get('context')=='camp' else 'champ'
                        C[k]+=1
                        if k=='camp' and o.get('name')=='Stellar': C['stellar_camp']+=1
                    elif e['kind']=='campClear': C['clears']+=1
            for c in d['champions']:
                if c['team']==cand:
                    m=c['metrics']; C['gold']+=float(m.get('earnedGold',0) or 0)
    print(f"{bot:14s} games {n} camp deaths/g {C['camp']/n:.2f} (Stellar {C['stellar_camp']/n:.2f})  champion-caused deaths/g {C['champ']/n:.2f}  clears/g {C['clears']/n:.1f}  gold/g {C['gold']/n:.0f}")
