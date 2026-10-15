import sys,os; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
B=[json.load(open(f)) for f in sorted(glob.glob(sys.argv[1]+'/*.json'))]
for lab,gs in (('27',[g for g in G if g['map']=='rows']),('26',[g for g in B if g['map']=='rows'])):
    print(f'### rows {lab}: per game (opp rank, result, rounds, final us/opp, lead at r100/200/300/350, max lead, min lead, our gems in hand at end, last tribute round us/opp, captures us/opp)')
    rows=[]
    for g in sorted(gs,key=lambda g:g['orank']):
        sub=g['sub']; t=g['t']
        leads=[sub[min(r,len(sub)-1)][t]-sub[min(r,len(sub)-1)][1-t] for r in (100,200,300,350)]
        allL=[s[t]-s[1-t] for s in sub]
        endg=sum(c['gems_end'] for c in champs(g,'us')); endo=sum(c['gems_end'] for c in champs(g,'opp'))
        lt=max([tb['done'] for c in champs(g,'us') for tb in c['tributes'] if tb.get('done')]+[0]); lto=max([tb['done'] for c in champs(g,'opp') for tb in c['tributes'] if tb.get('done')]+[0])
        cu=sum(len(c['captures']) for c in champs(g,'us')); co=sum(len(c['captures']) for c in champs(g,'opp'))
        rows.append([g['opp'][:14],g['orank'],g['res'],g['rounds'],f"{g['score']}/{g['oscore']}",' / '.join(str(x) for x in leads),max(allL),min(allL),f'{endg}/{endo}',f'{lt}/{lto}',f'{cu}/{co}'])
    tbl(['opp','rank','res','rounds','final','lead r100/200/300/350','max lead','min lead','gems in hand end us/opp','last tribute us/opp','captures us/opp'],rows)
    # time share and per-type on rows
    for team in ('us','opp'):
        c=collections.Counter(); n=0
        for g in gs:
            for ch in champs(g,team): c.update(ch['states']); n+=1
        tot=sum(c.values()); print(f'- {lab} {team} states: '+', '.join(f'{k} {100*v/tot:.1f}%' for k,v in sorted(c.items(),key=lambda x:-x[1])))
    # gems/attacker-round and camp utilization: how many captures per 4050 group per game, and the group's respawn
    print()
