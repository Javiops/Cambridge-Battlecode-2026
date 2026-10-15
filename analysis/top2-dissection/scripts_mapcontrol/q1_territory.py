import sys, json, collections
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
occ=collections.defaultdict(collections.Counter)   # (team,map,phase) -> terr counter
occ_all=collections.defaultdict(collections.Counter)
entries=collections.defaultdict(list)   # (team,map) -> list of entry dicts
caps=collections.defaultdict(collections.Counter) # (team,map)-> terr of captures
ecaps=[]  # enemy-side captures with conditions
gcache={}
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); t=0 if rec['side']=='a' else 1
    g=gcache.get(mid) or Game(mid); gcache[mid]=g
    key=(rec['team'],rec['map'])
    prev_t={}; in_enemy={}  # champ -> entry round
    for r in g.order:
        sn=g.rounds[r]
        mine=[c for c in sn.values() if c['team']==t and c['alive']]
        ens=[c for c in sn.values() if c['team']!=t and c['alive']]
        for c in mine:
            tr=terr(mp,c['x'],c['y'],t)
            occ[(key[0],key[1],phase(r))][tr]+=1; occ_all[(key[0],phase(r))][tr]+=1
            if tr=='enemy' and c['i'] not in in_enemy:
                # cause analysis at entry
                nearest=min([cheb((c['x'],c['y']),(e['x'],e['y'])) for e in ens],default=99)
                # was an enemy within 8 in the previous 5 rounds?
                seen=False
                for rr in range(max(0,r-5),r+1):
                    s2=g.rounds.get(rr)
                    if not s2: continue
                    me=s2.get(c['i'])
                    if me and me['alive'] and any(e['alive'] and e['team']!=t and cheb((me['x'],me['y']),(e['x'],e['y']))<=8 for e in s2.values()): seen=True
                in_enemy[c['i']]=dict(r=r,i=c['i'],ty=c['ty'],enemy_alive=len(ens),nearest=nearest,seen=seen,diff=g.sub[r][t]-g.sub[r][1-t],camp=False,atk=False,dead=False,maxdepth=0)
            if tr=='enemy':
                d=in_enemy[c['i']]
                do=spawn_dist(mp,c['x'],c['y'],t); de=spawn_dist(mp,c['x'],c['y'],1-t)
                d['maxdepth']=max(d['maxdepth'],do-de)
        # events in this round for champs in enemy
        for e in g.evs.get(r,[]):
            if e['ak']==1 and e['a'] in in_enemy:
                if e['keff'] and any(x.get('hp',0)<0 for x in e['keff']): in_enemy[e['a']]['camp']=True
                if any(x.get('hp',0)<0 and g.teamof[x['i']]!=t for x in e['eff']): in_enemy[e['a']]['atk']=True
        # exits
        for i,d in list(in_enemy.items()):
            c=sn.get(i)
            if not c or not c['alive'] or terr(mp,c['x'],c['y'],t)!='enemy':
                d['end']=r; d['dead']= (not c) or (not c['alive'])
                entries[key].append(d); del in_enemy[i]
        # captures
        for e in g.evs.get(r,[]):
            if e['ak']==0 and e['ph']==7:
                for x in e['eff']:
                    if x.get('gems',0)>0 and g.teamof[x['i']]==t:
                        c=sn.get(x['i']) or g.snap(r-1).get(x['i'])
                        tr=terr(mp,c['x'],c['y'],t)
                        caps[key][tr]+=1
                        if tr=='enemy':
                            nearest=min([cheb((c['x'],c['y']),(e2['x'],e2['y'])) for e2 in ens],default=99)
                            ecaps.append((rec['team'],rec['map'],mid[:8],r,c['ty'],len(ens),nearest,g.sub[r][t]-g.sub[r][1-t],rec['opp'][:12]))
                        break
def pct(cn):
    n=sum(cn.values()) or 1
    return ' / '.join('%2d%%'%(100*cn[k]/n) for k in ('own','mid','enemy'))
print('## champion-rounds own/mid/enemy by phase (T=%d)'%TERR_T)
print('| team | map | 0-100 | 100-300 | 300-end | captures own/mid/enemy |')
print('|---|---|---|---|---|---|')
for team in ('mite','uni'):
    for m in sorted(set(r['map'] for r in SEL)):
        print('| %s | %s | %s | %s | %s | %s |'%(team,m,pct(occ[(team,m,0)]),pct(occ[(team,m,1)]),pct(occ[(team,m,2)]),' / '.join(str(caps[(team,m)][k]) for k in ('own','mid','enemy'))))
    print('| %s | ALL | %s | %s | %s | |'%(team,pct(occ_all[(team,0)]),pct(occ_all[(team,1)]),pct(occ_all[(team,2)])))
print()
print('## enemy-half entries (episodes of one champion), per team/map')
print('| team | map | episodes | per game | median len | enemy seen <=8 in prev 5r (chase) | hits camp there | hits enemy there | ends dead | all enemies dead at entry | enemies alive<=1 | median score diff |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
import statistics
for team in ('mite','uni'):
    tot=[]
    for m in sorted(set(r['map'] for r in SEL)):
        L=entries[(team,m)]; tot+=L
        if not L: print('| %s | %s | 0 | | | | | | | | | |'%(team,m)); continue
        n=len(L)
        print('| %s | %s | %d | %.1f | %d | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% | %+d |'%(team,m,n,n/6,statistics.median([d['end']-d['r'] for d in L]),100*sum(d['seen'] for d in L)/n,100*sum(d['camp'] for d in L)/n,100*sum(d['atk'] for d in L)/n,100*sum(d['dead'] for d in L)/n,100*sum(d['enemy_alive']==0 for d in L)/n,100*sum(d['enemy_alive']<=1 for d in L)/n,statistics.median([d['diff'] for d in L])))
    n=len(tot)
    print('| %s | ALL | %d | %.1f | %d | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% | %+d |'%(team,n,n/54,statistics.median([d['end']-d['r'] for d in tot]),100*sum(d['seen'] for d in tot)/n,100*sum(d['camp'] for d in tot)/n,100*sum(d['atk'] for d in tot)/n,100*sum(d['dead'] for d in tot)/n,100*sum(d['enemy_alive']==0 for d in tot)/n,100*sum(d['enemy_alive']<=1 for d in tot)/n,statistics.median([d['diff'] for d in tot])))
print()
print('## captures on enemy side (team,map,match,round,champ,enemies alive,nearest enemy,score diff,opp)')
for x in ecaps: print(x)
# long deep entries examples
print()
print('## longest enemy-half episodes')
for team in ('mite','uni'):
    L=sorted([(d['end']-d['r'],m,d) for m in set(r['map'] for r in SEL) for d in entries[(team,m)]],key=lambda z:-z[0])[:6]
    for ln,m,d in L: print(team,m,'len',ln,{k:d[k] for k in ('r','end','ty','enemy_alive','nearest','seen','camp','atk','dead','diff','maxdepth')})
