import sys, json, collections, statistics
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
# Q2: per clearing episode of every group: damage share by team, last hit team, capturing team, fight nearby, round
clear=[]   # dicts
trib=collections.defaultdict(list)  # (team,map)-> (phase, altarclass, bag)
buys=collections.defaultdict(collections.Counter)
done=set()
for rec in SEL:
    mid=rec['match']
    mp=load_map(rec['map']); g=Game(mid)
    t=0 if rec['side']=='a' else 1
    names={t:rec['team'], 1-t:'opp:'+rec['opp'][:10]}
    key=(rec['team'],rec['map'])
    # tributes (k18 ph14 gems<0)
    for r in g.order:
        for e in g.evs.get(r,[]):
            if e['ak']==1 and e['k']==18:
                for x in e['eff']:
                    if x.get('gems',0)<0 and g.teamof[x['i']]==t:
                        p=e['apos']; al=min(mp['altars'],key=lambda a:cheb(a,p))
                        trib[key].append((phase(r),terr(mp,al[0],al[1],t),-x['gems'],r))
            if e['ak']==1 and e['k']==13 and g.teamof[e['a']]==t:
                for x in e['eff']:
                    if x.get('gold',0)<0: buys[rec['team']][x['gold']]+=1
    if mid in done: continue
    done.add(mid)
    # clearing episodes per group (both teams)
    dmg=collections.defaultdict(lambda: collections.Counter()); first=collections.defaultdict(lambda: None); lasthit={}
    for r in g.order:
        for e in g.evs.get(r,[]):
            if e['ak']==1 and e['keff']:
                a=e['a']; ta=g.teamof[a]
                for x in e['keff']:
                    if x.get('hp',0)<0:
                        gi=g.camps[0][x['i']]['g']
                        dmg[gi][ta]+=-x['hp']
                        if first[gi] is None: first[gi]=r
                    if x.get('alive')==1 and False: pass
                    if 'alive' in x and x['alive']==0:
                        gi=g.camps[0][x['i']]['g']
                        lasthit[gi]=(ta,r,a)
            if e['ak']==0 and e['ph']==7:
                # capture: gems to champion(s); identify group by champion position
                got=[x for x in e['eff'] if x.get('gems',0)>0]
                if not got: continue
                sn=g.snap(r); ci=got[0]['i']; c=sn.get(ci); tc=g.teamof[ci]
                if not c or c['x']<0: c=g.snap(r-1).get(ci)
                # nearest group tiles
                gi=min(g.gtiles,key=lambda k: min(cheb((c['x'],c['y']),tt) for tt in g.gtiles[k]))
                d=dmg.get(gi,collections.Counter()); lh=lasthit.get(gi)
                tot=sum(d.values()) or 1
                # fight near camp between first damage and capture
                fr=first[gi] or r
                fight=0
                for rr in range(fr,r+1):
                    for e2 in g.evs.get(rr,[]):
                        if e2['ak']==1 and e2['apos'] and min(cheb(e2['apos'],tt) for tt in g.gtiles[gi])<=8:
                            if any(x.get('hp',0)<0 and g.teamof[x['i']]!=g.teamof[e2['a']] for x in e2['eff']): fight+=1
                clear.append(dict(mid=mid[:8],map=rec['map'],r=r,gi=gi,terrA=group_terr(mp,gi,0,g.gtiles),cap=tc,capname=names[tc],
                                  share=d[tc]/tot,lh=lh[0] if lh else None,lhname=names[lh[0]] if lh else None,fight=fight,n=len(got),
                                  gems=sum(x['gems'] for x in got),dur=r-fr))
                dmg[gi]=collections.Counter(); first[gi]=None; lasthit.pop(gi,None)
# summaries
print('## Q2 middle-group captures (group equidistant: |dA-dB|<=3)')
print('| team | map | mid captures by team | by opponent | steals by team (last hit opp) | steals by opp | contested (both dmg) | fights near camp (captures with champ dmg within 8) | median capture round team/opp |')
print('|---|---|---|---|---|---|---|---|---|')
for team in ('mite','uni'):
    for m in sorted(set(r['map'] for r in SEL)):
        L=[c for c in clear if c['map']==m and c['terrA']=='mid' and (c['capname']==team or c['lhname']==team or True)]
        # only games of this team
        mids={r['match'][:8] for r in SEL if r['team']==team and r['map']==m}
        L=[c for c in L if c['mid'] in mids]
        if not L: print('| %s | %s | 0 | | | | | | |'%(team,m)); continue
        byt=[c for c in L if c['capname']==team]; byo=[c for c in L if c['capname']!=team]
        st=[c for c in byt if c['lh'] is not None and c['lhname']!=team]; so=[c for c in byo if c['lh'] is not None and c['lhname']==team]
        cont=[c for c in L if 0<c['share']<1]
        fg=[c for c in L if c['fight']>0]
        print('| %s | %s | %d | %d | %d | %d | %d | %d | %s / %s |'%(team,m,len(byt),len(byo),len(st),len(so),len(cont),len(fg),
              statistics.median([c['r'] for c in byt]) if byt else '-',statistics.median([c['r'] for c in byo]) if byo else '-'))
print()
print('## all steals (capturing team != last-hit team), any territory, games of mite/uni')
print('| map | match | round | group | terr(A) | last hit by | captured by | dmg share of capturer | gems | n on tiles | fight hits near |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for c in clear:
    if c['lh'] is not None and c['lh']!=c['cap']:
        print('| %s | %s | %d | %d | %s | %s | %s | %.2f | %d | %d | %d |'%(c['map'],c['mid'],c['r'],c['gi'],c['terrA'],c['lhname'],c['capname'],c['share'],c['gems'],c['n'],c['fight']))
print()
print('## partial-share captures (capturer did <80% of the damage) per team')
for team in ('mite','uni'):
    mids={r['match'][:8] for r in SEL if r['team']==team}
    L=[c for c in clear if c['mid'] in mids]
    byt=[c for c in L if c['capname']==team]
    print(team,'captures',len(byt),'with share<0.8:',sum(c['share']<0.8 for c in byt),'with share<0.5:',sum(c['share']<0.5 for c in byt),'| opp captures',len(L)-len(byt),'opp share<0.8:',sum(c['share']<0.8 for c in L if c['capname']!=team),'opp share<0.5:',sum(c['share']<0.5 for c in L if c['capname']!=team))
print()
print('## Q3 tributes: altar class by phase, bag sizes')
print('| team | map | n | phase 0-100 own/mid/enemy | 100-300 | 300-end | median bag | p90 bag | max bag | bags<=10 |')
print('|---|---|---|---|---|---|---|---|---|---|')
for team in ('mite','uni'):
    allL=[]
    for m in sorted(set(r['map'] for r in SEL)):
        L=trib[(team,m)]; allL+=L
        if not L: continue
        def cls(ph):
            c=collections.Counter(x[1] for x in L if x[0]==ph); n=sum(c.values()) or 1
            return '%d/%d/%d'%(c['own'],c['mid'],c['enemy'])
        bags=sorted(x[2] for x in L)
        print('| %s | %s | %d | %s | %s | %s | %d | %d | %d | %d%% |'%(team,m,len(L),cls(0),cls(1),cls(2),statistics.median(bags),bags[int(0.9*len(bags))],bags[-1],100*sum(b<=10 for b in bags)/len(bags)))
    bags=sorted(x[2] for x in allL)
    print('| %s | ALL | %d | | | | %d | %d | %d | %d%% |'%(team,len(allL),statistics.median(bags),bags[int(0.9*len(bags))],bags[-1],100*sum(b<=10 for b in bags)/len(bags)))
print()
print('## purchases: gold deltas (consumables would be non-30 multiples)')
for team in ('mite','uni'): print(team, sorted(buys[team].items()))
