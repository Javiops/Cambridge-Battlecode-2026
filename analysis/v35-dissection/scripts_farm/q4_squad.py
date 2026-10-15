import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
print('## Q4 Squad size and kill speed\n')
def bucket(v,edges): return next((f'<{e}' for e in edges if v<e),f'>={edges[-1]}')
def rowsfor(gs,team,keyf,edges,label):
    rows=[]; b=collections.defaultdict(list)
    for g in gs:
        for ch in champs(g,team):
            for cp in ch['captures']:
                if cp['dur'] is None or cp['natt']==0: continue
                b[bucket(keyf(cp),edges)].append(cp)
    for k in sorted(b,key=lambda s:(s[0]!='<',s)):
        xs=b[k]; rows.append([label,team,k,len(xs),f(mean([x['natt'] for x in xs]),2),f(mean([x['near'] for x in xs]),2),f(med([x['dur'] for x in xs]),0),f(mean([x['dur'] for x in xs]),1),f(med([x['hp']/x['natt']/max(1,x['dur']) for x in xs]),0),f(med([x['dmg']/x['natt']/max(1,x['dur']) for x in xs]),0)])
    return rows
hdr=['split','team','bucket','captures','attackers mean','within 4 at capture','hit->capture med','mean','group hp/attacker/round med','measured dmg/attacker/round med']
print('### By group hp (Mite reference: 2.0/2.05/2.4/3.5 attackers, 12/17/21/23 rounds)\n')
rows=[]
for team in ('us','opp'): rows+=rowsfor(G,team,lambda c:c['hp'],[800,1500,3000],'all')
tbl(hdr,rows)
print('### By round (first 50 rounds vs later)\n'); rows=[]
for team in ('us','opp'): rows+=rowsfor(G,team,lambda c:c['r'],[50,150,300],'all')
tbl(hdr,rows)
print('### By map, all hp buckets pooled\n'); rows=[]
for m in MAPS:
    gs=[g for g in G if g['map']==m]
    for team in ('us','opp'):
        xs=[cp for g in gs for ch in champs(g,team) for cp in ch['captures'] if cp['dur'] is not None and cp['natt']>0]
        rows.append([m,team,len(xs),f(mean([x['natt'] for x in xs]),2),f(med([x['dur'] for x in xs]),0),f(mean([x['hp'] for x in xs]),0),f(med([x['hp']/x['natt']/max(1,x['dur']) for x in xs]),0)])
tbl(['map','team','captures','attackers mean','hit->capture med','mean group hp','hp/attacker/round med'],rows)
print('### By win/loss and opponent tier, hp >= 800 groups\n'); rows=[]
for name,gs in splits():
    if name.startswith('map') or name=='all': continue
    for team in ('us','opp'):
        xs=[cp for g in gs for ch in champs(g,team) for cp in ch['captures'] if cp['dur'] is not None and cp['natt']>0 and cp['hp']>=800]
        rows.append([name,team,len(xs),f(mean([x['natt'] for x in xs]),2),f(med([x['dur'] for x in xs]),0),f(med([x['hp']/x['natt']/max(1,x['dur']) for x in xs]),0)])
tbl(['split','team','captures (hp>=800)','attackers mean','hit->capture med','hp/attacker/round med'],rows)
print('### Attackers distribution per hp bucket (count of captures by number of attackers), us vs opp\n'); rows=[]
for team in ('us','opp'):
    b=collections.defaultdict(collections.Counter)
    for g in G:
        for ch in champs(g,team):
            for cp in ch['captures']:
                if cp['dur'] is None or cp['natt']==0: continue
                b[bucket(cp['hp'],[800,1500,3000])][min(cp['natt'],5)]+=1
    for k in sorted(b,key=lambda s:(s[0]!='<',s)): rows.append([team,k,sum(b[k].values())]+[b[k][n] for n in (1,2,3,4,5)])
tbl(['team','hp bucket','captures','1','2','3','4','5+'],rows)
print('### Who tanks: champion type taking most monster damage during the capture, by capturing team (count); and monster damage taken per type\n')
for team in ('us','opp'):
    tk=collections.Counter(); td=collections.Counter(); hits=collections.Counter(); n=collections.Counter(); dmg=collections.Counter()
    for g in G:
        for ch in champs(g,team):
            n[ch['ty']]+=1; hits[ch['ty']]+=ch['tanked_hits']; dmg[ch['ty']]+=ch['tanked_dmg']
            for cp in ch['captures']:
                if cp['tank']: tk[cp['tank']]+=1
    print(f'- {team} tank per capture: {dict(tk.most_common())}')
    print(f'- {team} monster damage taken per champion-game: '+', '.join(f'{t} {dmg[t]/n[t]:.0f} ({hits[t]/n[t]:.0f} hits)' for t,_ in n.most_common()))
print()
print('### Basic-attack distance to the camp monster (share of basic attacks on camps at Chebyshev distance 1 / 2 / 3+), by type\n'); rows=[]
for team in ('us','opp'):
    d=collections.defaultdict(collections.Counter)
    for g in G:
        for ch in champs(g,team):
            for k,v in ch['ranged_d'].items(): d[ch['ty']][min(int(k),3)]+=v
    for ty,c in sorted(d.items(),key=lambda x:-sum(x[1].values())):
        tot=sum(c.values()); rows.append([team,ty,tot]+[f'{100*c[k]/tot:.0f}%' for k in (0,1,2,3)])
tbl(['team','type','camp basic attacks','d0','d1','d2','d3+'],rows)
print('### Team-level: attackers by map in the first capture of the game (whole team on the first camp?)\n'); rows=[]
for m in MAPS:
    gs=[g for g in G if g['map']==m]; r=[m,gs[0]['nch']]
    for team in ('us','opp'):
        fs=[]
        for g in gs:
            caps=sorted([cp for ch in champs(g,team) for cp in ch['captures'] if cp['dur'] is not None],key=lambda x:x['r'])
            if caps: fs.append(caps[0])
        r+=[f(mean([x['natt'] for x in fs]),2),f(med([x['r'] for x in fs]),0),f(med([x['dur'] for x in fs]),0)]
    rows.append(r)
tbl(['map','nch','us attackers 1st camp','1st capture round','hit->cap','opp attackers','1st capture round','hit->cap'],rows)
