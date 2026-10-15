import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
print('## Q3 Camp choice\n')
print('### Per map: camp groups (json group id + side relative to the team), captures per game by us and by the opponent (opponent side is its own view)\n')
for m in MAPS:
    gs=[g for g in G if g['map']==m]; n=len(gs)
    info={}; cu=collections.Counter(); co=collections.Counter(); gu=collections.Counter(); first_u=collections.Counter(); gamesu=collections.Counter(); gameso=collections.Counter()
    for g in gs:
        for gi,inf in g['groups'].items():
            # key from our view: (jg,terr). for opp view flip terr
            info[(inf['jg'],inf['terr'])]=inf
        seen_u=set(); seen_o=set()
        for c in g['champs']:
            for cp in c['captures']:
                terr=cp['terr'] if c['team']=='us' else {'own':'enemy','enemy':'own','mid':'mid'}[cp['terr']]
                key=(cp['jg'],terr)
                if c['team']=='us': cu[key]+=1; gu[key]+=cp['gems']; seen_u.add(key)
                else: co[key]+=1; seen_o.add(key)
        for k in seen_u: gamesu[k]+=1
        for k in seen_o: gameso[k]+=1
    rows=[]
    for key in sorted(info,key=lambda k:(k[1]!='own',k[1]!='mid',info[k]['dOwn'])):
        inf=info[key]
        if key[1]=='enemy': d=inf['dEnemy']
        else: d=inf['dOwn']
        rows.append([key[0],key[1],'+'.join(inf['types']),inf['hp'],inf['gems'],inf['gold'],inf['respawn'],inf['dOwn'] if key[1]!='enemy' else inf['dEnemy'],inf['dAlt'],f(cu[key]/n,2),f(100*gamesu[key]/n,0)+'%',f(co[key]/n,2),f(100*gameso[key]/n,0)+'%'])
    print(f'**{m}** ({n} games)\n'); tbl(['jg','side','types','hp','gems','gold','respawn','dist from spawn','dist to altar','us captures/g','us % games','opp captures/g','opp % games'],rows)
# territory split
print('### Captures per game by territory (own / mid / enemy), us vs opp\n')
rows=[]
for name,gs in splits():
    r=[name,len(gs)]
    for team in ('us','opp'):
        c=collections.Counter()
        for g in gs:
            for ch in champs(g,team):
                for cp in ch['captures']:
                    terr=cp['terr'] if team=='us' else {'own':'enemy','enemy':'own','mid':'mid'}[cp['terr']]; c[terr]+=1
        n=len(gs); r+=[f'{c["own"]/n:.1f} / {c["mid"]/n:.1f} / {c["enemy"]/n:.1f}']
    rows.append(r)
tbl(['split','n','us own/mid/enemy','opp own/mid/enemy'],rows)
# order: first 5 team captures
print('### Opening order: the first 5 groups our team captures (jg/side), most common sequences per map\n')
for m in MAPS:
    gs=[g for g in G if g['map']==m]; c=collections.Counter(); first=collections.Counter(); fr=[]
    for g in gs:
        caps=sorted([cp for ch in champs(g,'us') for cp in ch['captures']],key=lambda x:x['r'])
        seq=tuple(f"{cp['jg']}{cp['terr'][0]}" for cp in caps[:5]); c[seq]+=1
        if caps: first[f"{caps[0]['jg']}{caps[0]['terr'][0]}@r{caps[0]['r']}"]+=1; fr.append(caps[0]['r'])
    print(f'- {m}: first capture round med {med(fr):.0f}; '+'; '.join(f'{"-".join(k)} x{v}' for k,v in c.most_common(3)))
print()
# camp set stability: per map, groups captured in >=80% games vs set sizes
print('### Camp set per map: groups taken in >=80% / >=50% of games, mean distinct groups per game, Jaccard between games (us vs opp)\n')
rows=[]
for m in MAPS:
    gs=[g for g in G if g['map']==m]; r=[m,len(gs)]
    for team in ('us','opp'):
        sets=[]
        for g in gs:
            s=set()
            for ch in champs(g,team):
                for cp in ch['captures']:
                    terr=cp['terr'] if team=='us' else {'own':'enemy','enemy':'own','mid':'mid'}[cp['terr']]; s.add((cp['jg'],terr))
            sets.append(s)
        cnt=collections.Counter(k for s in sets for k in s); n=len(gs)
        core=[k for k,v in cnt.items() if v>=0.8*n]; half=[k for k,v in cnt.items() if v>=0.5*n]
        jac=[len(a&b)/max(1,len(a|b)) for i,a in enumerate(sets) for b in sets[i+1:]]
        r+=[len(core),len(half),f(mean([len(s) for s in sets]),1),f(mean(jac),2)]
    rows.append(r)
tbl(['map','n','us core(>=80%)','us >=50%','us distinct/g','us jaccard','opp core','opp >=50%','opp distinct/g','opp jaccard'],rows)
# revisit gap and nearest-camp test
print('### Revisits: rounds between a group respawn and our next capture of it (non-first captures); nearest-up rule\n')
rows=[]
for name,gs in splits():
    r=[name,len(gs)]
    for team in ('us','opp'):
        gaps=[cp['since_up'] for g in gs for ch in champs(g,team) for cp in ch['captures'] if cp['since_up']<cp['r']]
        ranks=[cp for g in gs for ch in champs(g,team) for cp in ch['captures'] if cp['rank'] is not None]
        r0=sum(1 for cp in ranks if cp['rank']==0); r1=sum(1 for cp in ranks if cp['rank']<=1); extra=[cp['dsel']-cp['dnear'] for cp in ranks]
        r+=[len(gaps),f(med(gaps),0),f(mean(gaps),0),len(ranks),f(100*r0/max(1,len(ranks)),0)+'%',f(100*r1/max(1,len(ranks)),0)+'%',f(med(extra),0),f(mean(extra),1)]
    rows.append(r)
tbl(['split','n','us revisits','gap med','mean','us captures','nearest-up chosen','1st or 2nd nearest','extra dist med','mean','opp revisits','gap med','mean','opp captures','nearest','1st/2nd','extra med','mean'],rows)
# never touched by us but farmed by opp (in own-view terms) per map
print('### Groups (jg/side in each team\'s own view) with captures/g by us <0.2 but by opp >=0.5, and the reverse\n')
for m in MAPS:
    gs=[g for g in G if g['map']==m]; n=len(gs); cu=collections.Counter(); co=collections.Counter(); info={}
    for g in gs:
        for gi,inf in g['groups'].items(): info[(inf['jg'],inf['terr'])]=inf
        for ch in g['champs']:
            for cp in ch['captures']:
                terr=cp['terr'] if ch['team']=='us' else {'own':'enemy','enemy':'own','mid':'mid'}[cp['terr']]
                (cu if ch['team']=='us' else co)[(cp['jg'],terr)]+=1
    a=[f"{k[0]}{k[1][0]}({info[k]['gems']}g,{info[k]['hp']}hp,d{info[k]['dOwn'] if k[1]!='enemy' else info[k]['dEnemy']}: us {cu[k]/n:.2f} opp {co[k]/n:.2f})" for k in info if cu[k]/n<0.2 and co[k]/n>=0.5]
    b=[f"{k[0]}{k[1][0]}({info[k]['gems']}g: us {cu[k]/n:.2f} opp {co[k]/n:.2f})" for k in info if co[k]/n<0.2 and cu[k]/n>=0.5]
    print(f'- {m}: opp farms, we do not: {a or "-"}; we farm, opp does not: {b or "-"}')
print()
