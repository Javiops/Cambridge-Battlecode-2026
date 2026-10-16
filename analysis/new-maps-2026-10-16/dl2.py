# Re-fetch bundles that came back as {"status":"pending"}: poll the pollUrl until the zip is ready.
import json, os, time, urllib.request
B = 'https://2026a.battlecode.co.uk'
for f in sorted(os.listdir('replays')):
    p = 'replays/' + f
    if os.path.getsize(p) > 1000: continue
    for a in range(12):
        url = B + f'/api/v1/matches/{f[:-4]}/bundle'  # the pollUrl 404s once the job is done; the plain URL then redirects to the zip
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
        except Exception as e:
            time.sleep(10); continue
        open(p, 'wb').write(data)
        if len(data) > 1000: break
        time.sleep(6)
    print(f, os.path.getsize(p), flush=True); time.sleep(3)
