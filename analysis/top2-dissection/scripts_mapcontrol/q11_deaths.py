import sys, json, collections, statistics
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
FIGHT={'corners','interlock','elkring','packs','collision'}
D=collections.defaultdict(list)
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    prev=None
    for r in g.order:
        sn=g.rounds[r]
        if prev:
            for c in sn.values():
                p=prev[c['i']]
                if c['team']==t and p['alive'] and not c['alive']:
                    al=[a for a in prev.values() if a['team']==t and a['alive'] and a['i']!=c['i'] and cheb((a['x'],a['y']),(p['x'],p['y']))<=8]
                    en=[a for a in prev.values() if a['team']!=t and a['alive'] and cheb((a['x'],a['y']),(p['x'],p['y']))<=8]
                    D[(rec['team'],rec['map'],rec['opp'][:12])].append(dict(r=r,ty=p['ty'],terr=terr(mp,p['x'],p['y'],t),al=len(al),en=len(en),gems=p['gems'],diff=g.sub[r][t]-g.sub[r][1-t]))
        prev=sn
print('## deaths: where and in what numbers (per team, fight maps aggregated, plus the Mite-Univardisty games)')
print('| team | games | deaths | in own/mid/enemy half | mean allies within 8 | mean enemies within 8 | outnumbered (allies+1 < enemies) | gems lost per death | deaths while behind |')
print('|---|---|---|---|---|---|---|---|---|')
def row(label,L,ng):
    n=len(L)
    if not n: print('| %s | %d | 0 | | | | | | |'%(label,ng)); return
    c=collections.Counter(d['terr'] for d in L)
    print('| %s | %d | %d | %d/%d/%d%% | %.1f | %.1f | %d%% | %.0f | %d%% |'%(label,ng,n,100*c['own']/n,100*c['mid']/n,100*c['enemy']/n,statistics.mean(d['al'] for d in L),statistics.mean(d['en'] for d in L),100*sum(d['al']+1<d['en'] for d in L)/n,statistics.mean(d['gems'] for d in L),100*sum(d['diff']<=-50 for d in L)/n))
for team in ('mite','uni'):
    L=[d for k,v in D.items() if k[0]==team and k[1] in FIGHT for d in v]; row(team+' fight maps',L,30)
    L=[d for k,v in D.items() if k[0]==team and k[1] not in FIGHT for d in v]; row(team+' farm maps',L,24)
for k,v in sorted(D.items()):
    if k[2].startswith('Univardisty') or k[2]=='Mite': row('%s on %s vs %s'%k,v,1)
