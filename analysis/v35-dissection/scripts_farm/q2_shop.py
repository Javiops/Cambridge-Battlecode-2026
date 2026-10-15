import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
print('## Q2 Draft and shop\n')
print('### Our draft per map (pick order) and record; opponent drafts seen against us\n')
for m in MAPS:
    gs=[g for g in G if g['map']==m]
    d=collections.Counter(tuple(g['draft']) for g in gs); od=collections.Counter(tuple(g['odraft']) for g in gs)
    print(f'**{m}** ({len(gs)} games, nch {gs[0]["nch"]}):')
    for k,v in d.most_common():
        w=sum(1 for g in gs if tuple(g['draft'])==k and g['res']=='win'); print(f'- us: {" > ".join(k)} x{v} ({w}-{v-w})')
    for k,v in od.most_common(6):
        w=sum(1 for g in gs if tuple(g['odraft'])==k and g['res']=='loss'); print(f'- opp: {" > ".join(k)} x{v} (opp won {w})')
    print()
# pool
for team,key in (('us','draft'),('opp','odraft')):
    c=collections.Counter(x for g in G for x in g[key]); fp=collections.Counter(g[key][0] for g in G)
    print(f'{team} pool (champion-games): {dict(c.most_common())}; first pick: {dict(fp.most_common())}\n')
# shop per type
print('### Shop per champion type (per champion-game; trips = rounds with a purchase)\n')
def shoprows(team):
    by=collections.defaultdict(list)
    for g in G:
        for c in champs(g,team): by[c['ty']].append((g,c))
    rows=[]
    for ty,lst in sorted(by.items(),key=lambda x:-len(x[1])):
        n=len(lst); first=[]; nb=[]; trips=[]; gaps=[]; dead=spawn=field=0; earned=spent=end=0; fam=collections.Counter(); emb=0; cons=0; after=[]
        for g,c in lst:
            if c['buys']:
                first.append(c['buys'][0]['r']); rs=sorted(set(b['r'] for b in c['buys'])); trips.append(len(rs)); gaps+=[b-a for a,b in zip(rs,rs[1:])]
                lastb={}
                for b in c['buys']: lastb[b['r']]=b
                after+=[b['before']-b['gold'] for b in lastb.values()]
            nb.append(len(c['buys']))
            for b in c['buys']:
                if b['dead']: dead+=1
                elif b['onspawn']: spawn+=1
                else: field+=1
            earned+=c.get('earnedGold',c['earned']); spent+=c.get('spentGold',0); end+=c['gold_end']
            for k,v in c.get('items',{}).items():
                f_,kind,_,stat=k.split('_')
                if kind=='shard': fam[f'{f_}_{stat}']+=v
                else: emb+=v
            cons+=sum(c.get('consumables',[]))
        tot=dead+spawn+field or 1
        rows.append([ty,n,', '.join(f'{k}:{v}' for k,v in fam.most_common(5)),f(emb/n,2),f(med(first),0),f(mean(nb),1),f(mean(trips),1),f(med(gaps),0),f(100*dead/tot,0)+'%',f(100*spawn/tot,0)+'%',f(100*field/tot,0)+'%',f(earned/n,0),f(spent/n,0),f(end/n,0),f(100*end/max(earned,1),0)+'%',f(100*sum(a==0 for a in after)/max(len(after),1),0)+'%',f(cons/n,2)])
    return rows
hdr=['type','n','shards bought (family_stat: total)','emblems/g','1st buy r (med)','buys/g','trips/g','gap med','% dead','% spawn','% field','earned','spent','gold end','unspent %','trips ending at 0 gold','consumables/g']
print('**Us**\n'); tbl(hdr,shoprows('us')); print('**Opponents**\n'); tbl(hdr,shoprows('opp'))
# build order per type for us: sequence of shard families? infer from trip composition: use maxhp flag for health, and emblem count progression
print('### Our purchase sequences (first 3 trips per champion-game: round:gold spent, H = health shards, [d]=dead, [f]=field)\n')
by=collections.defaultdict(collections.Counter)
for g in G:
    for c in champs(g,'us'):
        trips=collections.OrderedDict()
        for b in c['buys']: trips.setdefault(b['r'],[]).append(b)
        seq=[]
        for r,bs in list(trips.items())[:3]:
            tag=''.join(('H' if b['maxhp']>0 else '')+('[d]' if b['dead'] else '')+('[f]' if not b['dead'] and not b['onspawn'] else '') for b in bs)
            seq.append(f"r{r}:{sum(b['gold'] for b in bs)}{tag}")
        by[c['ty']][' | '.join(seq) if seq else '(no purchase)']+=1
for ty,cnt in by.items():
    print(f'- {ty}: '+'; '.join(f'{k} x{v}' for k,v in cnt.most_common(4)))
print()
# per-family emblem order using items: which family is complete when total shards<=5? count games by first emblem family inferred from the 5-shard point: use buys cumulative gold vs items... approximate: report fraction of games with each family present
print('### Family presence per type (share of champion-games with >=5 shards of the family), us vs opp\n')
for team in ('us','opp'):
    by=collections.defaultdict(list)
    for g in G:
        for c in champs(g,team): by[c['ty']].append(c)
    rows=[]
    for ty,lst in sorted(by.items(),key=lambda x:-len(x[1])):
        fam=collections.Counter()
        for c in lst:
            for k,v in c.get('items',{}).items():
                f_,kind,_,stat=k.split('_')
                if kind=='shard' and v>=5: fam[f'{f_}_{stat}']+=1
        rows.append([team,ty,len(lst),', '.join(f'{k} {100*v//len(lst)}%' for k,v in fam.most_common(6))])
    tbl(['team','type','n','families with a full emblem (share of games)'],rows)
# per map economy
print('### Gold per game per map (team totals), us vs opp\n')
rows=[]
for m in MAPS:
    gs=[g for g in G if g['map']==m]; r=[m,len(gs)]
    for team in ('us','opp'):
        e=mean([sum(c.get('earnedGold',0) for c in champs(g,team)) for g in gs]); s=mean([sum(c.get('spentGold',0) for c in champs(g,team)) for g in gs]); en=mean([sum(c['gold_end'] for c in champs(g,team)) for g in gs])
        emb=mean([sum(v for c in champs(g,team) for k,v in c.get('items',{}).items() if 'emblem' in k) for g in gs])
        r+= [f(e,0),f(s,0),f(en,0),f(emb,1)]
    rows.append(r)
tbl(['map','n','us earned','us spent','us gold end','us emblems','opp earned','opp spent','opp gold end','opp emblems'],rows)
# gold unspent at end by win/loss
rows=[]
for name,gs in splits():
    if name.startswith('map'): continue
    for team in ('us','opp'):
        ends=[c['gold_end'] for g in gs for c in champs(g,team)]
        rows.append([name,team,len(ends),f(med(ends),0),f(mean(ends),0),f(100*sum(e>=90 for e in ends)/len(ends),0)+'%',f(100*sum(e>=150 for e in ends)/len(ends),0)+'%'])
tbl(['split','team','champion-games','gold at end med','mean','>=90 (3 shards)','>=150 (an emblem)'],rows)
