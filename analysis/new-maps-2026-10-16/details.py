# Fetch match-group details (per-game statistics) for groups between two top-N teams; data/details/<group>.json
import json, os, sys, time, urllib.request
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
lad = json.load(open('../data/ladder.json'))['teams']
top = {t['teamId']: (i + 1, t['name']) for i, t in enumerate(lad[:N])}
os.makedirs('../data/details', exist_ok=True)
gs = [json.loads(l) for l in open('../data/groups.jsonl')]
sel = [g for g in gs if g['status'] == 'finished' and all(s['teamId'] in top for s in g['sides'])]
print('groups', len(gs), 'top-vs-top finished', len(sel), flush=True)
for i, g in enumerate(sel):
    p = f"../data/details/{g['id']}.json"
    if os.path.exists(p): continue
    for a in range(4):
        try:
            d = json.load(urllib.request.urlopen(f"https://2026a.battlecode.co.uk/api/v1/match-groups/{g['id']}", timeout=30)); break
        except Exception as e:
            d = None; time.sleep(3 * (a + 1))
    if d: json.dump(d, open(p, 'w'))
    if i % 50 == 0: print(i, flush=True)
    time.sleep(0.1)
