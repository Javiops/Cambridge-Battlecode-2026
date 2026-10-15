import sys,os; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
from common import Game, SEL, cheb
byid={g['match']:g for g in G}
want=sys.argv[1:]
for rec in SEL:
    if rec['map']!='rows' or (want and rec['opp'] not in want): continue
    g=byid[rec['match']]; Gm=Game(rec); R=Gm.R; mp=Gm.map; t=Gm.t
    print(f"\n#### {rec['opp']} (#{rec['orank']}) {rec['res']} rounds {g['rounds']} final {g['score']}/{g['oscore']}")
    own=[c for c in g['champs'] if c['team']=='us']
    acted=collections.defaultdict(dict)
    for r,evs in Gm.ev.items():
        for e in evs:
            if e['ak']==1: acted[r].setdefault(e['a'],[]).append(e['k'])
    r_end=g['rounds']
    for r in range(r_end-45,r_end+1):
        if r not in R: continue
        snap=R[r]; parts=[]
        for cc in snap['champs']:
            if cc[1]!=t: continue
            dalt=mp['dAlt'][cc[4]][cc[3]]; ks=acted[r].get(cc[0],[])
            parts.append(f"{cc[2][:4]} g{cc[7]} hp{cc[5]} dA{dalt} k{ks}")
        print(f"r{r} sub {snap['sub'][t]}/{snap['sub'][1-t]} | "+' | '.join(parts))
    # tribute starts per champion in the last 60 rounds
    for c in own:
        print(' ',c['ty'],'tributes:',[(tb.get('r0'),tb.get('done'),tb['bag'],tb.get('gems')) for tb in c['tributes'] if (tb.get('r0') or tb.get('done') or 0)>=r_end-80],'captures:',[(cp['r'],cp['gems']) for cp in c['captures'] if cp['r']>=r_end-80])
