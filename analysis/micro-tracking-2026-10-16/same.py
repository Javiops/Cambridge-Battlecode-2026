import sys, os, glob, json, subprocess
sys.path.insert(0, 'tools'); import ab
from concurrent.futures import ThreadPoolExecutor
a, b, opp = sys.argv[1:4]; fuel = sys.argv[4] if len(sys.argv) > 4 else None
maps = sorted(glob.glob('maps/*.map26a')); ENV = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'}
def one(t):
    bot, m, side = t
    od = f'fuel/same/{os.path.basename(bot)}_{fuel}_{os.path.basename(m)[:-7]}_{side}'
    os.makedirs(od, exist_ok=True); st = od + '/stats.json'
    if not os.path.exists(st):
        x, y = (bot, opp) if side == 'A' else (opp, bot)
        subprocess.run(['cambc', 'run', x, y, '--map', m, '-o', od, '--statistics', st, '--json'] + (['--fuel', fuel] if fuel else []), capture_output=True, env=ENV)
        for f in glob.glob(od + '/*.repl26a'): os.remove(f)
    d = ab.load_stats(st)
    return (d['outcome'], d['round'], [t['submittedGems'] for t in d['teams']], [c.get('deaths') for c in d['champions']])
jobs = [(bot, m, s) for m in maps for s in 'AB' for bot in (a, b)]
with ThreadPoolExecutor(4) as ex: res = list(ex.map(one, jobs))
same = diff = 0
for i in range(0, len(res), 2):
    if res[i] == res[i+1]: same += 1
    else: diff += 1; print('DIFF', jobs[i][1], jobs[i][2], res[i], res[i+1])
print(f'identical {same} / {same+diff}')
