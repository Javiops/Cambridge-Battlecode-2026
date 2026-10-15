"""Retreat-under-fire thresholds (enemy within 4, damage taken in previous 3 rounds), fight durations, examples."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_fights')
from common import *
P=json.load(open(S+'/reports/scripts_fights/positioning_out.json')); F=json.load(open(S+'/reports/scripts_fights/fights.json'))
def pct(a,b): return '%d%%'%round(100*a/b) if b else '-'
def med(x): return st.median(x) if x else None
print('# retreat under fire = first step away while an enemy is within 4 and we took damage in the previous 3 rounds')
for tk in ('mite','uni','opp'):
    L=[r for r in P['leave'][tk] if r['d']<=4 and r['taken_prev']>0]
    h=sorted(r['hpp'] for r in L); q=lambda p: h[int(p*(len(h)-1))]
    print(tk,'n',len(L),'hp% med',q(.5),'p25-p75',q(.25),q(.75),'<30',pct(sum(1 for x in h if x<30),len(h)),'<40',pct(sum(1 for x in h if x<40),len(h)),'<50',pct(sum(1 for x in h if x<50),len(h)),'>=70',pct(sum(1 for x in h if x>=70),len(h)),
          '| leave',pct(sum(1 for r in L if r['kind']=='leave'),len(L)),'kite',pct(sum(1 for r in L if r['kind']=='kite'),len(L)),'| died',pct(sum(1 for r in L if r['died']),len(L)),'recalled',pct(sum(1 for r in L if r['recalled']),len(L)),'arrived',pct(sum(1 for r in L if r['arrived']),len(L)),
          '| outnumbered',pct(sum(1 for r in L if r['enemies']>r['allies']+1),len(L)),'allies dead',pct(sum(1 for r in L if r['allies_dead']>0),len(L)))
    for lo,hi in ((0,30),(30,50),(50,70),(70,101)):
        x=[r for r in L if lo<=r['hpp']<hi]
        if x: print('   hp %d-%d: n %d leave %s kite %s died %s recalled %s outnumbered %s'%(lo,hi,len(x),pct(sum(1 for r in x if r['kind']=='leave'),len(x)),pct(sum(1 for r in x if r['kind']=='kite'),len(x)),pct(sum(1 for r in x if r['died']),len(x)),pct(sum(1 for r in x if r['recalled']),len(x)),pct(sum(1 for r in x if r['enemies']>r['allies']+1),len(x))))
    byc=collections.defaultdict(list)
    for r in L: byc[cls(r['ty'])].append(r)
    for c,x in byc.items(): print('   class',c,'n',len(x),'hp% med',med([r['hpp'] for r in x]),'leave',pct(sum(1 for r in x if r['kind']=='leave'),len(x)),'died',pct(sum(1 for r in x if r['died']),len(x)))
print('\n# fights duration')
for t in ('mite','uni'):
    fs=[f for f in F if f['team']==t]; d=[f['r1']-f['r0']+1 for f in fs]
    print(t,'duration med',med(d),'>30 rounds',pct(sum(1 for x in d if x>30),len(d)),'n',len(d),'1-hit pokes',pct(sum(1 for f in fs if f['nhits']==1),len(fs)))
print('\n# example retreats (from fights.json): saved by recall (hp<30) / died anyway')
for t in ('mite','uni'):
    n1=n2=0
    for f in F:
        if f['team']!=t: continue
        for r in f['retreats']:
            if r['team']!=f['us'] or r['d']>4 or r['taken_prev']==0: continue
            if r['hpp']<30 and r['recalled'] and r['arrived'] and not r['died'] and n1<3:
                n1+=1; print(t,'saved',f['map'],f['match'][:8],'r%d'%r['r'],r['ty'],'hp%d%%'%r['hpp'],'enemy at',r['d'],'allies',r['allies'],'enemies',r['enemies'],'recall started at dist',r['rec_d'])
            if r['died'] and n2<3:
                n2+=1; print(t,'died ',f['map'],f['match'][:8],'r%d'%r['r'],r['ty'],'hp%d%%'%r['hpp'],'enemy at',r['d'],'allies',r['allies'],'enemies',r['enemies'])
