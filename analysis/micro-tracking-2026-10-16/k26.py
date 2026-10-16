import sys, os, glob, json, subprocess
from concurrent.futures import ThreadPoolExecutor
bots = sys.argv[1].split(','); opp = sys.argv[2]
maps = sorted(glob.glob('maps/*.map26a'))
ENV = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'}
def one(t):
    b, m, side = t
    od = f'fuel/out/{os.path.basename(b)}_{os.path.basename(m)[:-7]}_{side}'
    cf = od + '/k.json'
    if os.path.exists(cf): return t, json.load(open(cf))
    os.makedirs(od, exist_ok=True)
    x, y = (b, opp) if side == 'A' else (opp, b)
    for _ in range(3):
        subprocess.run(['cambc', 'run', x, y, '--map', m, '-o', od], capture_output=True, env=ENV)
        reps = glob.glob(od + '/*.repl26a')
        if reps: break
    if not reps: return t, 0
    p = subprocess.run(['node', 'tools/replaydump.js', reps[0], '--every-step'], capture_output=True, text=True)
    me = 0 if side == 'A' else 1
    k, team = 0, {}
    for line in p.stdout.splitlines():
        try: d = json.loads(line)
        except ValueError: continue
        if 'step' not in d: continue
        if not team: team = {c['index']: c['team'] for c in d.get('champions', [])}
        st = d['step']
        if st.get('kind') == 26 and st.get('actorKind') == 1 and team.get(st.get('actorIndex')) == me: k += 1
    for f in reps: os.remove(f)
    json.dump(k, open(cf, 'w')); return t, k
jobs = [(b, m, s) for b in bots for m in maps for s in 'AB']
with ThreadPoolExecutor(4) as ex: res = list(ex.map(one, jobs))
tab = {}
for (b, m, s), k in res: tab.setdefault(os.path.basename(m)[:-7], {}).setdefault(b, 0); tab[os.path.basename(m)[:-7]][b] += k
print('map'.ljust(14) + ''.join(os.path.basename(b).rjust(10) for b in bots))
for m in sorted(tab): print(m.ljust(14) + ''.join(str(tab[m][b]).rjust(10) for b in bots))
print('TOTAL'.ljust(14) + ''.join(str(sum(tab[m][b] for m in tab)).rjust(10) for b in bots))
