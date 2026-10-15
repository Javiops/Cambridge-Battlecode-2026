#!/usr/bin/env python3
"""pace.py BOT OPP 'MAPGLOB' OUTDIR [--compact]: run BOT (side a) vs OPP on each map, report final round and gems; optional compact dumps for analysis"""
import sys, glob, os, subprocess, json, concurrent.futures as cf
bot, opp, mg, out = sys.argv[1:5]; comp = '--compact' in sys.argv
os.makedirs(out, exist_ok=True)
env = dict(os.environ, CAMBC_NO_UPDATE_CHECK='1')
def one(m):
    name = os.path.basename(m)[:-7]; od = f'{out}/{name}'
    if not glob.glob(f'{od}/*.repl26a'):
        subprocess.run(['cambc', 'run', bot, opp, '--map', m, '-o', od], cwd='/home/user/ws', env=env, capture_output=True)
    rep = glob.glob(f'{od}/*.repl26a')[0]
    js = f'{od}/dump.jsonl'
    if not os.path.exists(f'{od}/summary.json'):
        p = subprocess.run(['node', '/home/user/ws/tools/replaydump.js', rep] + (['--camps'] if comp else []), capture_output=True, text=True)
        lines = p.stdout.strip().split('\n'); summ = json.loads(lines[-1])
        json.dump({'round': summ['finalRound'], 'gems': summ['submittedGems'], 'outcome': summ['outcomeName']}, open(f'{od}/summary.json', 'w'))
        if comp: open(js, 'w').write(p.stdout)
    return name, json.load(open(f'{od}/summary.json'))
maps = sorted(glob.glob(mg))
with cf.ThreadPoolExecutor(8) as ex:
    res = dict(ex.map(one, maps))
tot = 0
for n in sorted(res):
    r = res[n]; tot += r['round']; print(f"{n:14} round {r['round']:5} gems {r['gems']}")
print('TOTAL rounds', tot, 'maps', len(res))
