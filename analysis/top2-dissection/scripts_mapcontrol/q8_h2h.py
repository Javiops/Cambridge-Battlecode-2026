import sys, json, collections, statistics
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
print('## per-game map-control metrics (team, map, opp): enemy-half share, mid+enemy captures, dmg dealt/received per champ-round, first enemy contact round, first death round')
print('| team | map | opp | rank | res | score | %own/mid/enemy champ-rounds | captures own/mid/enemy | dmg dealt/100cr | dmg taken/100cr | first contact (<=8) | first own death | first enemy death | tributes (median bag) |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for rec in sorted(SEL,key=lambda r:(r['team'],r['map'],r['orank'])):
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    occ=collections.Counter(); caps=collections.Counter(); dmg=0; taken=0; cr=0; fc=None; fd=None; fe=None; bags=[]
    prev=None
    for r in g.order:
        sn=g.rounds[r]
        for c in sn.values():
            if c['team']==t and c['alive']:
                cr+=1; occ[terr(mp,c['x'],c['y'],t)]+=1
                if fc is None and any(e['team']!=t and e['alive'] and cheb((c['x'],c['y']),(e['x'],e['y']))<=8 for e in sn.values()): fc=r
            if prev and prev[c['i']]['alive'] and not c['alive']:
                if c['team']==t and fd is None: fd=r
                if c['team']!=t and fe is None: fe=r
        prev=sn
        for e in g.evs.get(r,[]):
            if e['ak']==1:
                for x in e['eff']:
                    if x.get('hp',0)<0:
                        if g.teamof[e['a']]==t and g.teamof[x['i']]!=t: dmg+=-x['hp']
                        if g.teamof[e['a']]!=t and g.teamof[x['i']]==t: taken+=-x['hp']
                if e['k']==18 and g.teamof[e['a']]==t:
                    for x in e['eff']:
                        if x.get('gems',0)<0: bags.append(-x['gems'])
            if e['ak']==0 and e['ph']==7:
                for x in e['eff']:
                    if x.get('gems',0)>0 and g.teamof[x['i']]==t:
                        c=sn.get(x['i']); caps[terr(mp,c['x'],c['y'],t)]+=1; break
    print('| %s | %s | %s | %d | %s | %d-%d | %d/%d/%d | %d/%d/%d | %.0f | %.0f | %s | %s | %s | %d (%d) |'%(rec['team'],rec['map'],rec['opp'][:14],rec['orank'],rec['res'],rec['score'],rec['oscore'],100*occ['own']/cr,100*occ['mid']/cr,100*occ['enemy']/cr,caps['own'],caps['mid'],caps['enemy'],100*dmg/cr,100*taken/cr,fc,fd,fe,len(bags),statistics.median(bags) if bags else 0))
