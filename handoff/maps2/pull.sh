#!/bin/bash
# pull.sh DIR : download the site's current map pool (engine 2.0.0) into DIR with curl and check each sha256.
# Needed in cloud containers: `cambc maps pull` rejects the agent proxy CA (UnknownIssuer); curl goes through it.
set -e; D=${1:-maps}; mkdir -p "$D"; B=https://2026a.battlecode.co.uk/api/v1/maps/pool
curl -sS "$B/" > "$D/pool.json"
python3 - "$D" <<'PY'
import json,subprocess,hashlib,sys
d=sys.argv[1]; P=json.load(open(d+'/pool.json'))['maps']; bad=0
for m in P:
    f=f"{d}/{m['name']}.map26a"
    subprocess.run(['curl','-sSL','-o',f,f"https://2026a.battlecode.co.uk/api/v1/maps/pool/{m['id']}/file"],check=True)
    if hashlib.sha256(open(f,'rb').read()).hexdigest()!=m['sha256']: bad+=1; print('sha mismatch',m['name'])
print(len(P),'maps,',bad,'bad')
PY
