# Crawl the public match-group list back to a date; one group per line in data/groups.jsonl.
import json, urllib.request, time, sys
stop = sys.argv[1] if len(sys.argv) > 1 else '2026-10-15T20:00'
base = 'https://2026a.battlecode.co.uk/api/v1/match-groups?scope=all'
before = None; out = open('../data/groups.jsonl', 'w'); n = 0; last = None
while True:
    url = base + (f'&before={before}' if before else '')
    d = None
    for a in range(5):
        try: d = json.load(urllib.request.urlopen(url, timeout=30)); break
        except Exception: time.sleep(2 * (a + 1))
    if not d or not d.get('groups'): break
    for g in d['groups']: out.write(json.dumps(g) + '\n'); n += 1
    g = d['groups'][-1]; before = f"{g['createdAt']}_{g['id']}"; last = g['createdAt']
    if n % 500 == 0: print(n, last, flush=True)
    if last < stop: break
    time.sleep(0.05)
print('done', n, last)
