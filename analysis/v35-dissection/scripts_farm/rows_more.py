import sys,os; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
B=[json.load(open(f)) for f in sorted(glob.glob(sys.argv[1]+'/*.json'))]
print('### End condition check (all maps, 27): games where max final score >=1000 vs rounds; rounds when neither reached 1000')
c=collections.Counter()
for g in G:
    mx=max(g['score'],g['oscore']); c[(g['map'],'>=1000' if mx>=1000 else '<1000')]+=1
print(sorted(c.items()))
print('rounds of games with max score <1000:',sorted(collections.Counter(g['rounds'] for g in G if max(g['score'],g['oscore'])<1000).items())[:12])
print('rounds of games with max score >=1000 by map (min/med/max):',{m:(min(x),med(x),max(x)) for m in MAPS for x in [[g['rounds'] for g in G if g['map']==m and max(g['score'],g['oscore'])>=1000]] if x})
print()
for lab,gs in (('27',[g for g in G if g['map']=='rows']),('26',[g for g in B if g['map']=='rows'])):
    print(f'### rows {lab}: banking timeline (median round of the k-th completed tribute, cumulative banked), us vs opp; and capture gem values')
    rows=[]
    for k in range(10,18):
        ru=[];ro=[]
        for g in gs:
            for team,lst in (('us',ru),('opp',ro)):
                dn=sorted(tb['done'] for ch in champs(g,team) for tb in ch['tributes'] if tb.get('done'))
                if len(dn)>=k: lst.append(dn[k-1])
        rows.append([k,len(ru),f(med(ru),0),len(ro),f(med(ro),0)])
    tbl(['k-th tribute','us games reaching it','us round med','opp games','opp round med'],rows)
    for team in ('us','opp'):
        cv=collections.Counter(cp['gems'] for g in gs for ch in champs(g,team) for cp in ch['captures'])
        bags=collections.Counter(tb['bag'] for g in gs for ch in champs(g,team) for tb in ch['tributes'] if tb.get('done'))
        # round when the team first reaches 1000 banked
        fin=[]
        for g in gs:
            t=g['t'] if team=='us' else 1-g['t']
            r=next((r for r,s in enumerate(g['sub']) if s[t]>=1000),None); fin.append(r)
        held=[]
        for g in gs:
            for ch in champs(g,team):
                for tb in ch['tributes']:
                    if tb.get('oldest') is not None: held.append(tb['oldest'])
        print(f'- {lab} {team}: capture gem values {dict(cv.most_common(5))}; bag values {dict(bags.most_common(6))}; round reaching 1000: {sorted(x for x in fin if x)} (never: {sum(1 for x in fin if x is None)}); oldest gems age at tribute start med {med(held):.0f} p90 {p(held,0.9):.0f}')
    # shares: captures where 2 champions were paid (split) per game
    split=0; tot=0
    for g in gs:
        k=collections.Counter((cp['g'],cp['r']) for ch in champs(g,'us') for cp in ch['captures'])
        split+=sum(1 for v in k.values() if v>=2); tot+=len(k)
    print(f'- {lab} us: group kills {tot}, paid to 2+ champions (split 33/33) {split}')
    # recalls right after the final-phase: per game, our champion-rounds in recall/shop after r300
    print()
print('### lanes per game (27 then 26): opp rank, result, captures us/opp, deaths us/opp, our captured gems/100cr vs opp')
for lab,gs in (('27',[g for g in G if g['map']=='lanes']),('26',[g for g in B if g['map']=='lanes'])):
    out=[]
    for g in sorted(gs,key=lambda g:g['orank']):
        cu=sum(len(c['captures']) for c in champs(g,'us')); co=sum(len(c['captures']) for c in champs(g,'opp'))
        du=sum(len(c['deaths']) for c in champs(g,'us')); do=sum(len(c['deaths']) for c in champs(g,'opp'))
        out.append(f"{g['opp'][:10]}#{g['orank']} {g['res'][0]} {cu}/{co} d{du}/{do} r{g['rounds']}")
    print(f'- {lab}: '+'; '.join(out))
