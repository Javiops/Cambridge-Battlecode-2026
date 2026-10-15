import sys, json, collections, statistics
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
# enemy-side captures: group type, how many of ours within 3 of tiles, enemies within 8, and what the enemy's nearest champion did
out=collections.defaultdict(collections.Counter)
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    for r in g.order:
        sn=g.rounds[r]
        for e in g.evs.get(r,[]):
            if e['ak']==0 and e['ph']==7:
                got=[x for x in e['eff'] if x.get('gems',0)>0 and g.teamof[x['i']]==t]
                if not got: continue
                c=sn[got[0]['i']]
                if terr(mp,c['x'],c['y'],t)!='enemy': continue
                gi=min(g.gtiles,key=lambda k: min(cheb((c['x'],c['y']),tt) for tt in g.gtiles[k]))
                ty=tuple(sorted(k['ty'] for k in g.camps[0].values() if k['g']==gi))
                key=(rec['team'],rec['map'])
                out[key]['n']+=1; out[key][ty]+=1
                en=[x for x in sn.values() if x['team']!=t and x['alive']]
                out[key]['enemies_alive_sum']+=len(en)
                out[key]['enemy_within_8']+= any(cheb((c['x'],c['y']),(x['x'],x['y']))<=8 for x in en)
                out[key]['phase%d'%phase(r)]+=1
for k,v in sorted(out.items()):
    n=v['n']; print(k, 'n=%d'%n, 'mean enemies alive %.1f'%(v['enemies_alive_sum']/n), 'enemy within 8 at capture %d%%'%(100*v['enemy_within_8']/n), 'phases',v['phase0'],v['phase1'],v['phase2'], {kk:vv for kk,vv in v.items() if isinstance(kk,tuple)})
