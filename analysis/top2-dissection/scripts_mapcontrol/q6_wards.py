import sys, json, collections, statistics
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
FIGHT={'corners','interlock','elkring','packs','collision'}
st=collections.defaultdict(collections.Counter)
bushcr=collections.defaultdict(collections.Counter)
scout=collections.defaultdict(list)
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    team=rec['team']; mt='fight' if rec['map'] in FIGHT else 'farm'
    # per-round bush occupancy and lone-forward champions without camp hits
    camphit=collections.defaultdict(set)  # champ -> rounds hitting camps
    for r in g.order:
        for e in g.evs.get(r,[]):
            if e['ak']==1 and e['keff'] and any(x.get('hp',0)<0 for x in e['keff']): camphit[e['a']].add(r)
            if e['ak']==1 and e['k'] in (14,23) and g.teamof[e['a']]==t:
                p=e['apos']; sn=g.snap(r); k=e['k']
                S_=st[(team,k)]; S_['n']+=1
                if tuple(p) in mp['bush']: S_['bush']+=1
                S_[terr(mp,p[0],p[1],t)]+=1
                ne=min([cheb(p,(c['x'],c['y'])) for c in sn.values() if c['team']!=t and c['alive']],default=99)
                if ne<=8: S_['enemy<=8']+=1
                # nearest camp group tiles
                dc=min(min(cheb(p,tt) for tt in tiles) for tiles in g.gtiles.values())
                if dc<=3: S_['camp<=3']+=1
                if cheb(p,(sn[e['a']]['x'],sn[e['a']]['y']))>0: S_['moved_same_round']+=1
                if any(x['i']==e['a'] for x in e['eff']): S_['selfeff']+=1
    for r in g.order:
        sn=g.rounds[r]
        for c in sn.values():
            if c['team']!=t or not c['alive']: continue
            bushcr[(team,mt)]['cr']+=1
            if (c['x'],c['y']) in mp['bush']: bushcr[(team,mt)]['bush']+=1
            # lone forward: in mid/enemy, no ally within 8, no camp hit in r-4..r
            tr=terr(mp,c['x'],c['y'],t)
            if tr in ('mid','enemy') and not any(a['team']==t and a['alive'] and a['i']!=c['i'] and cheb((a['x'],a['y']),(c['x'],c['y']))<=8 for a in sn.values()) and not any(rr in camphit[c['i']] for rr in range(r-4,r+1)):
                bushcr[(team,mt)]['lone_fwd_nocamp']+=1
print('## Q6 effect-less action kinds 14 and 23 (candidate ward placements): where they happen')
print('| team | kind | n | in bush | own/mid/enemy | enemy within 8 | within 3 of a camp |')
print('|---|---|---|---|---|---|---|')
for team in ('mite','uni'):
    for k in (14,23):
        S_=st[(team,k)]; n=S_['n'] or 1
        print('| %s | k%d | %d | %d%% | %d/%d/%d%% | %d%% | %d%% |'%(team,k,S_['n'],100*S_['bush']/n,100*S_['own']/n,100*S_['mid']/n,100*S_['enemy']/n,100*S_['enemy<=8']/n,100*S_['camp<=3']/n))
print()
print('## champion-rounds standing in a bush, and lone forward champion-rounds (mid/enemy half, no ally within 8, no camp hit in 5 rounds)')
for k,v in sorted(bushcr.items()): print(k, 'bush %.1f%%'%(100*v['bush']/v['cr']), 'lone-forward-no-camp %.1f%%'%(100*v['lone_fwd_nocamp']/v['cr']), 'of',v['cr'])
