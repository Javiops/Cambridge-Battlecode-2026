import json, sys, time, urllib.request, os
B='https://2026a.battlecode.co.uk/api/v1'
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(u, timeout=60) as r: return r.read()
        except Exception as e:
            print('retry', u, e, file=sys.stderr); time.sleep(2**(i+1))
    raise SystemExit('fail '+u)
team, name, pages = sys.argv[1], sys.argv[2], int(sys.argv[3])
out = open(f'groups_{name}.jsonl','w'); before=None
for p in range(pages):
    u = f'{B}/match-groups?scope=all&team={team}' + (f'&before={before}' if before else '')
    d = json.loads(get(u)); gs=d['groups']
    for g in gs: out.write(json.dumps(g)+'\n')
    print(p, len(gs), gs[-1]['createdAt'] if gs else None, file=sys.stderr)
    if not d.get('more') or not gs: break
    before = f"{gs[-1]['createdAt']}_{gs[-1]['id']}"; time.sleep(1)
