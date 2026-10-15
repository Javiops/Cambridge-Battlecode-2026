"""Q5: on the maps we lose most: positional differences win vs loss (per game metrics), and candidates for examples."""
import sys, collections, statistics as st, json
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
ROWS = []
for rec, g in games():
    mp = g.mp; t = g.us
    d = dict(m=rec['match'][:8], map=rec['map'], res=rec['res'], oppname=rec['opp'][:14], orank=rec['orank'], rounds=rec['rounds'], score=rec['score'], oscore=rec['oscore'], draft=','.join(x[:4] for x in rec['draft']))
    for who, tt in (('us', g.us), ('opp', g.them)):
        n = 0; own = mid = en = 0; pd = []; alone = 0; nchamp = 0; idle = 0; spawn = 0; deaths = 0; camp = 0; trib = 0
        fights = 0; gems_carried = []; depth = []
        for r in g.order[1:]:
            sn = g.rounds[r]; mine = [c for c in sn.values() if c['team'] == tt and c['alive']]
            pts = [(c['x'], c['y']) for c in mine]
            if len(pts) >= 2: pd.append(st.mean([cheb(a, b) for i, a in enumerate(pts) for b in pts[i+1:]]))
            for c in mine:
                nchamp += 1; tr = terr(mp, c['x'], c['y'], tt)
                own += tr == 'own'; mid += tr == 'mid'; en += tr == 'enemy'
                if all(cheb((c['x'], c['y']), (o['x'], o['y'])) > 6 for o in mine if o is not c): alone += 1
                lab = primary(g.acts[c['i']][r]); idle += lab == 'nothing'; camp += lab in ('attack camp', 'cast@camp'); trib += lab == 'tribute'
                fights += lab in ('attack champ', 'cast@champ')
                spawn += spawn_dist(mp, c['x'], c['y'], tt) <= 2
                depth.append(spawn_dist(mp, c['x'], c['y'], tt))
        deaths = sum(1 for r, i in g.deaths if g.types[i][0] == tt)
        caps = [(r, i, gm) for r, i, gm in g.caps if g.types[i][0] == tt]
        capterr = collections.Counter()
        for r, i, gm in caps:
            c = g.rounds[r].get(i)
            if c['x'] < 0: c = g.rounds[g.order[g.ridx[r]-1]][i]
            gi = g.camptiles.get((c['x'], c['y']))
            if gi is None: gi = min(g.gtiles, key=lambda gg: min(cheb((c['x'], c['y']), q) for q in g.gtiles[gg]))
            capterr[g.gterr[gi][tt]] += 1
        n = nchamp or 1
        d[who] = dict(own=round(100*own/n), mid=round(100*mid/n), en=round(100*en/n), pd=round(st.mean(pd), 1) if pd else 0, alone=round(100*alone/n), idle=round(100*idle/n), camp=round(100*camp/n), trib=round(100*trib/n), fight=round(100*fights/n), spawn=round(100*spawn/n), deaths=deaths, caps=len(caps), cap_own=capterr['own'], cap_mid=capterr['mid'], cap_en=capterr['enemy'], depth=round(st.mean(depth), 1), gpr=round((rec['score'] if who == 'us' else rec['oscore'])/rec['rounds']*100, 1))
    # first fight round & first death
    d['first_death_us'] = min([r for r, i in g.deaths if g.types[i][0] == t], default=None)
    d['first_death_opp'] = min([r for r, i in g.deaths if g.types[i][0] != t], default=None)
    ROWS.append(d)
json.dump(ROWS, open('q5_rows.json', 'w'))
M = ['own', 'mid', 'en', 'depth', 'pd', 'alone', 'idle', 'spawn', 'camp', 'fight', 'trib', 'deaths', 'caps', 'cap_own', 'cap_mid', 'cap_en', 'gpr']
def mean(L, who, k): return st.mean([d[who][k] for d in L]) if L else 0
for mapn in ['lanes', 'rows', 'corners', 'packs', 'elkring', 'collision', 'interlock', 'monolith', 'expanse']:
    L = [d for d in ROWS if d['map'] == mapn]
    print('\n## %s: %d games, %d wins. Means per game (us W / us L / opp in our W / opp in our L)' % (mapn, len(L), sum(d['res'] == 'win' for d in L)))
    W = [d for d in L if d['res'] == 'win']; Lo = [d for d in L if d['res'] == 'loss']
    print('| metric | us (wins) | us (losses) | opp (our wins) | opp (our losses) |'); print('|---|---|---|---|---|')
    for k in M:
        print('| %s | %.1f | %.1f | %.1f | %.1f |' % (k, mean(W, 'us', k), mean(Lo, 'us', k), mean(W, 'opp', k), mean(Lo, 'opp', k)))
    print('drafts W:', collections.Counter(d['draft'] for d in W), 'L:', collections.Counter(d['draft'] for d in Lo))
    print('games:')
    for d in sorted(L, key=lambda d: (d['res'], d['orank'])):
        print('  ', d['m'], d['res'], d['oppname'], d['orank'], '%d-%d r%d' % (d['score'], d['oscore'], d['rounds']), d['draft'], 'us own/mid/en %d/%d/%d pd %.1f alone %d idle %d deaths %d caps own/mid/en %d/%d/%d' % (d['us']['own'], d['us']['mid'], d['us']['en'], d['us']['pd'], d['us']['alone'], d['us']['idle'], d['us']['deaths'], d['us']['cap_own'], d['us']['cap_mid'], d['us']['cap_en']),
              '| opp own/mid/en %d/%d/%d pd %.1f deaths %d caps %d/%d/%d' % (d['opp']['own'], d['opp']['mid'], d['opp']['en'], d['opp']['pd'], d['opp']['deaths'], d['opp']['cap_own'], d['opp']['cap_mid'], d['opp']['cap_en']), 'first death us/opp', d['first_death_us'], d['first_death_opp'])
