import json,sys
# champ.py R FILE... : per our champion collectedGems/submittedGems/earnedGold/spentGold/gold/monsterDamageDone at round R
R=int(sys.argv[1])
def at(runs,r):
    t=0;v=0
    for x in runs:
        if t+x['duration']>r: return x['value']
        t+=x['duration']; v=x['value']
    return v
for f in sys.argv[2:]:
    d=json.load(open(f)); us='teamA' if '/A_' in f else 'teamB'
    ch={c['id']:c for c in d['champions']}
    ct={}
    for t in d['championTimelines']:
        o=t['owner']; cid=o['id'] if isinstance(o,dict) else o
        ct.setdefault(cid,{})[t['metric']]=t['runs']
    print(f.split('res/')[-1], 'WIN' if d['match']['outcome']==us else 'loss', f'@r{R}')
    for cid,m in sorted(ct.items()):
        c=ch.get(cid,{}); team=c.get('team'); 
        if team!=us: continue
        print('  ',str(c.get('name',''))[:8].ljust(8),' '.join(f"{k[:9]}={at(m[k],R)}" for k in ('collectedGems','submittedGems','gems','earnedGold','spentGold','gold','monsterDamageDone','championDamageDone') if k in m))
