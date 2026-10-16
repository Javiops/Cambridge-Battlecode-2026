import json,os,sys,time,subprocess
B="https://2026a.battlecode.co.uk"
s=json.load(open('sel.json'))
for x in s:
    m=x['match']; p=f'zips/{m}.zip'
    if os.path.exists(p) and os.path.getsize(p)>1000: continue
    url=B+f"/api/v1/matches/{m}/bundle"
    for k in range(30):
        subprocess.run(['curl','-sSL','-o',p,url])
        if os.path.getsize(p)>1000: break
        try: j=json.load(open(p))
        except Exception: print(m,open(p).read()[:100]); time.sleep(3); continue
        if 'pollUrl' in j: url=B+j['pollUrl']
        time.sleep(max(2,j.get('retryAfter',2)))
    print(m, os.path.getsize(p), flush=True)
