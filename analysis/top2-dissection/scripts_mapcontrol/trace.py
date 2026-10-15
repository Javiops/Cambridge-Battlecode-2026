import sys, json, collections
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
pref=sys.argv[1]; r0=int(sys.argv[2]); r1=int(sys.argv[3]); R=int(sys.argv[4]) if len(sys.argv)>4 else 6
rec=[r for r in SEL if r['match'].startswith(pref)][0]; g=Game(rec['match']); mp=load_map(rec['map'])
print(rec['team'],rec['side'],rec['map'],'vs',rec['opp'],rec['res'],rec['score'],rec['oscore'])
# find focus: tiles near a capture in [r0,r1]: use arg5 group index or auto = group captured
gi=int(sys.argv[5]) if len(sys.argv)>5 else None
for r in range(r0,r1+1):
    sn=g.snap(r); cs=g.camps.get(r) or g.camps[max(k for k in g.camps if k<=r)]
    line=['r%d sub%s'%(r,g.sub.get(r))]
    for e in g.evs.get(r,[]):
        if e['ak']==1 and e['keff'] and any(x.get('hp',0)<0 for x in e['keff']):
            line.append('%s%d(t%d)hits camp%s'%(sn[e['a']]['ty'][:3],e['a'],g.teamof[e['a']],[x['i'] for x in e['keff'] if x.get('hp',0)<0]))
        if e['ak']==1 and any(x.get('hp',0)<0 for x in e['eff']):
            line.append('%s%d(t%d)->%s'%(sn[e['a']]['ty'][:3],e['a'],g.teamof[e['a']],[(x['i'],x['hp']) for x in e['eff'] if x.get('hp',0)<0]))
        if e['ak']==0 and e['ph']==7 and any(x.get('gems',0)>0 for x in e['eff']): line.append('CAPTURE %s'%[(x['i'],x['gems']) for x in e['eff'] if x.get('gems',0)>0])
        if e['ak']==1 and e['k'] in (11,12,18): line.append('%d:k%d'%(e['a'],e['k']))
    if gi is not None:
        tiles=g.gtiles[gi]
        near=['%s%d(t%d)@%d,%d hp%d g%d'%(c['ty'][:3],c['i'],c['team'],c['x'],c['y'],c['hp'],c['gems']) for c in sn.values() if c['alive'] and min(cheb((c['x'],c['y']),t) for t in tiles)<=R]
        camp=['c%d:%d%s'%(k['i'],k['hp'],'' if k['alive'] else 'X') for k in cs.values() if k['g']==gi]
        line.append(' | '.join(camp)); line.append(' '.join(near))
    print(' '.join(line))
