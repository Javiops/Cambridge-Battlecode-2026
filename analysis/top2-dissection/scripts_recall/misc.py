import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
import collections, statistics as st, json
def med(xs): return st.median(xs) if xs else None
rows=json.load(open('recall_rows.json'))
for team in ('mite','uni'):
    A=[x for x in rows if x['team']==team and x['result']=='arrived']
    print('=====',team)
    print(' stay x bought:',sorted(collections.Counter((min(x['stay'],5),min(x['bought'],3)) for x in A).items()))
    S=[x for x in A if x['flags']==['shop']]
    print(' shop-only recalls gold hist:',sorted(collections.Counter(min(x['gold']//30*30,300) for x in S).items()),'gold min',min(x['gold'] for x in S) if S else None)
    print(' shop-only by map:',collections.Counter(x['map'] for x in S))
    # heal recalls: hp% by whether foe within 8 at start
    Hh=[x for x in A if 'heal' in x['flags']]
    print(' heal recalls: foe within 8: %d, none: %d; hpp med w/foe %s, w/o %s ; last_hit<=3: %d'%(sum(x['nfoe8']>0 for x in Hh),sum(x['nfoe8']==0 for x in Hh),med([x['hpp'] for x in Hh if x['nfoe8']>0]),med([x['hpp'] for x in Hh if x['nfoe8']==0]),sum(x['last_hit']<=3 for x in Hh)))
    print(' all starts: last_hit dist:',sorted(collections.Counter(min(x['last_hit'],20) if x['last_hit']>=0 else -1 for x in rows if x['team']==team).items()))
    # recalls with hp>=50 and no shop/bank/escape: what do they look like? dalt, gems, dspawn
    Rp=[x for x in A if x['reason']=='reposition']
    print(' reposition: gems>0 %d/%d, dalt med %s, dspawn med %s, nfoe8>0 %d, next %s'%(sum(x['gems']>0 for x in Rp),len(Rp),med([x['dalt'] for x in Rp]),med([x['dspawn'] for x in Rp]),sum(x['nfoe8']>0 for x in Rp),collections.Counter(x['next'] for x in Rp)))
    # interrupted hit_camp: context
    I=[x for x in rows if x['team']==team and x['result']=='hit_camp']
    print(' hit_camp interrupted: hpp med %s, dfoe med %s, after %s, examples %s'%(med([x['hpp'] for x in I]),med([x['dfoe'] for x in I]),collections.Counter(x['after'] for x in I),[(x['match'][:8],x['map'],x['ty'],x['r'],x['hpp']) for x in I[:4]]))
    # recall start distance-to-foe threshold: fraction of starts with dfoe<=6
    St=[x for x in rows if x['team']==team]
    print(' starts dfoe<=6: %d/%d (%.0f%%); of those arrived %d'%(sum(x['dfoe']<=6 for x in St),len(St),100*sum(x['dfoe']<=6 for x in St)/len(St),sum(1 for x in St if x['dfoe']<=6 and x['result']=='arrived')))
    print(' interruption rate by dfoe:',{d:'%d/%d'%(sum(1 for x in St if min(x['dfoe'],9)==d and x['result'] not in('arrived','game_end','moved')),sum(1 for x in St if min(x['dfoe'],9)==d)) for d in range(1,10)})
    # rounds lost per game: 5 per arrival + stay
    pg=collections.defaultdict(int); 
    for x in St:
        pg[x['match']]+= (5+x.get('stay',0)) if x['result']=='arrived' else max(0,(x['end'] or x['r'])-x['r'])
    print(' champ-rounds in recall+spawn per game: med %s, as %% of champ-rounds: %.1f%%'%(med(list(pg.values())),100*sum(pg.values())/sum(load_map(g['map'])['nch']*g['rounds'] for g in load_sel() if g['team']==team)))
