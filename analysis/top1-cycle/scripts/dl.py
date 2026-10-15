import json, time, urllib.request, os
B='https://2026a.battlecode.co.uk'
sel=json.load(open('selected.json')); done=0
for m in {r['match'] for r in sel}:
    f=f'replays/{m}.zip'
    if os.path.exists(f): continue
    for i in range(4):
        try:
            with urllib.request.urlopen(f'{B}/api/v1/matches/{m}/bundle', timeout=60) as r: open(f,'wb').write(r.read()); break
        except Exception as e: print('retry',m,e); time.sleep(2**(i+1))
    done+=1; time.sleep(1)
print('downloaded',done)
