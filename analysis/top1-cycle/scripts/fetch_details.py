import json, sys, time, urllib.request, os
B='https://2026a.battlecode.co.uk/api/v1'
lad=json.load(open('../ladder.json'))['teams']; rank={t['teamId']:t['rank'] for t in lad}
os.makedirs('groups',exist_ok=True)
for n in ['mite','uni']:
    gs=[json.loads(l) for l in open(f'groups_{n}.jsonl')]
    top=[g for g in gs if g['status']=='finished' and all(rank.get(s['teamId'],999)<=20 for s in g['sides'])]
    for g in top:
        f=f"groups/{g['id']}.json"
        if os.path.exists(f): continue
        with urllib.request.urlopen(f"{B}/match-groups/{g['id']}", timeout=60) as r: open(f,'wb').write(r.read())
        time.sleep(0.7)
