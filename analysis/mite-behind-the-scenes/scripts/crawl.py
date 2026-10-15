import json, urllib.request, time, sys
base='https://2026a.battlecode.co.uk/api/v1/match-groups?scope=all'
before=None; out=open('groups.jsonl','w'); n=0; last=None
while True:
    url=base+(f'&before={before}' if before else '')
    for a in range(5):
        try: d=json.load(urllib.request.urlopen(url,timeout=30)); break
        except Exception as e: time.sleep(2*(a+1)); d=None
    if not d or not d.get('groups'): break
    for g in d['groups']: out.write(json.dumps(g)+'\n'); n+=1
    g=d['groups'][-1]; before=f"{g['createdAt']}_{g['id']}"; last=g['createdAt']
    if n%500==0: print(n,last,flush=True)
    if last < '2026-10-11': break
    time.sleep(0.05)
print('done',n,last)
