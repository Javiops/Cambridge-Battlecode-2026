# Download replay bundles of data/pick.json (public; S3 redirect), politely.
import json, os, time, urllib.request
os.makedirs('../data/replays', exist_ok=True)
for i, r in enumerate(json.load(open('../data/pick.json'))):
    p = f"../data/replays/{r['match']}.zip"
    if os.path.exists(p): continue
    for a in range(4):
        try:
            urllib.request.urlretrieve(f"https://2026a.battlecode.co.uk/api/v1/matches/{r['match']}/bundle", p); break
        except Exception as e:
            print('retry', r['match'], e, flush=True); time.sleep(15 * (a + 1))
    if i % 20 == 0: print(i, flush=True)
    time.sleep(4)
print('done')
