# Decode replays (tools/replaydump.js --camps) into small per-game files data/compact/<match>.json.gz:
# meta (champions, statistics), per-round champion state, camp-group state changes, submitted gems per round.
import json, gzip, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
RD = '/home/user/cambridge-battlecode-2026/tools/replaydump.js'
V1 = '/root/.cache/cambc/assets/e24cd97081ad9eebe5ab4c64a08cc932350019d2126ddcd586ccea803f345c98/visualiser/assets/v0_0_1-ctH8uuEb.wasm'  # older engine replays
OUT = '../data/compact'; os.makedirs(OUT, exist_ok=True)
def one(zp, wasm=None):
    mid = os.path.basename(zp)[:-4]; op = f'{OUT}/{mid}.json.gz'
    if os.path.exists(op): return 'skip'
    p = subprocess.Popen(['node', RD, zp, '--camps'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                         env=dict(os.environ, **({'CAMBC_VIS_WASM': wasm} if wasm else {})))
    meta = None; R = []; G = []; gstate = {}; champs = None
    for line in p.stdout:
        d = json.loads(line)
        if d.get('summary'): meta = d; continue
        if 'champions' not in d: continue
        if champs is None: champs = [[c['index'], c['team'], c['typeName']] for c in d['champions']]
        R.append([d['round'], d['submittedGems'][0], d['submittedGems'][1],
                  [[c['x'], c['y'], c['health'], c['maxHealth'], c['gems'], c['gold'], int(c['alive'])] for c in d['champions']]])
        for k in d.get('camps', []):
            key = k['index']
            st = (k['groupStateName'], k['captureTeam'], int(k['alive']))
            if gstate.get(key) != st:
                gstate[key] = st
                G.append([d['round'], key, k['group'], k['typeName'], k['spawnX'], k['spawnY'], st[0], st[1], st[2], k['rewardGems'], k['rewardGold']])
    p.wait()
    if not meta and not wasm: return one(zp, V1)
    if not meta: return 'fail'
    with gzip.open(op, 'wt') as f: json.dump(dict(meta=meta, champs=champs, R=R, G=G), f)
    return 'ok'
zs = sorted(os.path.join('../data/replays', f) for f in os.listdir('../data/replays') if f.endswith('.zip'))
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, zs))
print({r: res.count(r) for r in set(res)})
