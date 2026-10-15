"""Q14 (re-creation of the study26 table 3c): on farm maps, streaks of >=5 consecutive idle ('nothing') rounds while within 6 tiles of a living own-half camp group.
Per streak: no ally within 6 (at start), enemy within 8 (any round), camp awake (any round), an ally already hitting that camp (any round), hp<50% at start, ends by attacking that camp within 3 rounds."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
ST = collections.defaultdict(list); NG = collections.Counter(); PG = collections.Counter()
for rec, g in games():
    if rec['map'] not in ('rows', 'expanse', 'lanes', 'monolith', 'elkring', 'interlock'): continue
    NG[rec['map']] += 1
    campgrp = {k['i']: k['grp'] for k in g.camps[0].values()}
    for who, t in (('us', g.us), ('opp', g.them)):
        cur = {}   # champ -> streak dict
        for idx, r in enumerate(g.order[1:], 1):
            sn = g.rounds[r]; camps = g.camps[r]
            alive_grp = collections.defaultdict(list)
            for k in camps.values():
                if k['alive']: alive_grp[k['grp']].append(k)
            hitting = collections.defaultdict(set)
            for e in g.events[r]:
                if e['ak'] == 1 and e['keff']:
                    for x in e['keff']:
                        if x.get('hp', 0) < 0 and x['i'] in campgrp: hitting[campgrp[x['i']]].add(e['a'])
            mine = [c for c in sn.values() if c['team'] == t and c['alive']]
            ens = [c for c in sn.values() if c['team'] != t and c['alive']]
            for c in mine:
                i = c['i']; lab = primary(g.acts[i][r])
                near = [gi for gi, ks in alive_grp.items() if g.gterr[gi][t] == 'own' and min(cheb((c['x'], c['y']), (k['x'], k['y'])) for k in ks) <= 6]
                if lab == 'nothing' and near:
                    if i not in cur:
                        cur[i] = dict(start=r, len=0, grp=set(), alone=all(cheb((c['x'], c['y']), (o['x'], o['y'])) > 6 for o in mine if o is not c), enemy=False, awake=False, allyhit=False, lowhp=c['hp'] < 0.5*c['mhp'])
                    d = cur[i]; d['len'] += 1; d['grp'] |= set(near)
                    if any(cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8 for e in ens): d['enemy'] = True
                    if any(k['awake'] for gi in near for k in alive_grp[gi]): d['awake'] = True
                    if any(hitting[gi] - {i} for gi in near): d['allyhit'] = True
                else:
                    if i in cur:
                        d = cur.pop(i)
                        if d['len'] >= 5:
                            # ends by attacking one of those camps within 3 rounds
                            d['endatk'] = False
                            for rr in g.order[idx:idx+3]:
                                for e in g.events[rr]:
                                    if e['ak'] == 1 and e['a'] == i and e['keff'] and any(x.get('hp', 0) < 0 and campgrp.get(x['i']) in d['grp'] for x in e['keff']): d['endatk'] = True
                            ST[(rec['map'], who)].append(d); PG[(rec['match'][:8], who)] += 1
print('## idle streaks >=5 rounds within 6 of a living own-half camp group (farm maps)')
print('| map | who | streaks | per game | mean len | no ally within 6 | enemy within 8 | camp awake | an ally is already hitting that camp | hp<50% | ends by attacking that camp (within 3r) |'); print('|---'*11 + '|')
for m in sorted(NG):
    for who in ('us', 'opp'):
        L = ST[(m, who)]; n = len(L) or 1
        print('| %s | %s | %d | %.1f | %.1f | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% |' % (m, who, len(L), len(L)/NG[m], st.mean([d['len'] for d in L]) if L else 0, 100*sum(d['alone'] for d in L)/n, 100*sum(d['enemy'] for d in L)/n, 100*sum(d['awake'] for d in L)/n, 100*sum(d['allyhit'] for d in L)/n, 100*sum(d['lowhp'] for d in L)/n, 100*sum(d['endatk'] for d in L)/n))
