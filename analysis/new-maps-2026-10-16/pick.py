# Choose replays: per new map, distinct top-vs-top games won by the best teams there, plus our recent games.
import json, collections, random
rows = json.load(open('../data/top_matches.json'))
NEW = ['stampede', 'pilgrimage', 'ambush', 'eight', 'contest', 'fragment', 'swirl', 'rushbait_v2']
random.seed(1); pick = []
for mp in NEW:
    rs = [r for r in rows if r['map'] == mp]
    seen = set(); d = []
    for r in sorted(rs, key=lambda r: r['at'], reverse=True):
        k = (r['a'], r['b'], r['rounds'], r['win'])
        if k in seen: continue
        seen.add(k); d.append(r)
    w = collections.Counter(r['win'] for r in d); n = collections.Counter([r['a'] for r in d] + [r['b'] for r in d])
    best = sorted(n, key=lambda t: -(w[t] + 1) / (n[t] + 2))[:3]
    chosen = []
    for t in best:
        chosen += [r for r in d if r['win'] == t][:5]
    for r in chosen: pick.append(dict(r, who='top', best=best))
    print(mp, 'distinct', len(d), 'best', best, 'chosen', len(chosen))
ours = [json.loads(l) for l in open('/mnt/project-files/online/data/games.jsonl')]
for mp in NEW:
    o = [g for g in ours if g['map'] == mp and g['at'] >= '2026-10-16T04:30' and g.get('opp_rank') and g['opp_rank'] <= 30]
    o = sorted(o, key=lambda g: g['at'], reverse=True)[:6]
    for g in o: pick.append(dict(match=g['match'], map=mp, who='us', a='us' if g['side'] == 'a' else g['opp'], b=g['opp'] if g['side'] == 'a' else 'us', win='us' if g['result'] == 'win' else g['opp'], rounds=g['rounds']))
    print(mp, 'ours', len(o))
json.dump(pick, open('../data/pick.json', 'w'), indent=0)
print(len(pick))
