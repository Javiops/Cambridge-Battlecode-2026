#!/usr/bin/env python3
"""Where our bot plays on a map, by phase, from local games (2026-10-16, new-maps thread).

usage (repo root): python3 tools/nm/localzones.py bots/US [bots/US2 ...] --opps sp_castera,sp_casterh --maps eight,ambush

Plays US vs each opponent on each map from both sides (replays kept under out/lz/), decodes them with
tools/replaydump.js --camps and prints the same table as analysis/new-maps-strategy-2026-10-16/scripts/zones.py
(time per zone and phase, captures / deaths / banks per zone, spread, gold, kills/deaths, opening route), for our team.
"""
import argparse, collections, glob, json, os, statistics as st, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ab  # noqa: E402

def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
def zone(p, own, en):
    a, b = cheb(p, own), cheb(p, en); t = a / max(a + b, 1)
    return 0 if t < 0.4 else (1 if t <= 0.6 else 2)

def decode(repl):
    p = subprocess.Popen(['node', 'tools/replaydump.js', repl, '--camps'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    meta = None; R = []; G = []; gstate = {}; champs = None
    for line in p.stdout:
        d = json.loads(line)
        if d.get('summary'): meta = d; continue
        if 'champions' not in d: continue
        if champs is None: champs = [[c['index'], c['team'], c['typeName']] for c in d['champions']]
        R.append([d['round'], d['submittedGems'][0], d['submittedGems'][1],
                  [[c['x'], c['y'], c['health'], c['maxHealth'], c['gems'], c['gold'], int(c['alive'])] for c in d['champions']]])
        for k in d.get('camps', []):
            s = (k['groupStateName'], k['captureTeam'], int(k['alive']))
            if gstate.get(k['index']) != s:
                gstate[k['index']] = s
                G.append([d['round'], k['index'], k['group'], k['typeName'], k['spawnX'], k['spawnY'], s[0], s[1], s[2], k['rewardGems'], k['rewardGold']])
    p.wait()
    return dict(meta=meta, champs=champs, R=R, G=G)

def metrics(d, t):
    R = d['R']; CH = d['champs']; S = (d['meta'] or {}).get('statistics') or {}
    me = [i for i, c in enumerate(CH) if c[1] == t]
    sc = {}
    for tt in (0, 1):
        ps = [R[1][3][i][:2] for i, c in enumerate(CH) if c[1] == tt]
        sc[tt] = (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
    own, en = sc[t], sc[1 - t]
    last = {}; caps = []; seen = set()
    for g in d['G']:
        r, ci, grp, typ, x, y, state, team, alive, rg, rgold = g
        if state == 'reward_available' and team in (0, 1): last[grp] = (team, r)
        if state == 'respawning' and grp in last and (r, grp) not in seen:
            seen.add((r, grp)); tm = last.pop(grp)[0]
            if tm == t: caps.append((r, grp, rg, rgold, x, y))
    occ = [[0, 0, 0] for _ in range(3)]; deaths = [0, 0, 0]; banks = [0, 0, 0]; spread = []
    for k in range(1, len(R)):
        r = R[k][0]; a = R[k - 1][3]; b = R[k][3]; ph = 0 if r < 150 else (1 if r < 400 else 2)
        alive = [b[i][:2] for i in me if b[i][6]]
        for i in me:
            if b[i][6]: occ[ph][zone(b[i][:2], own, en)] += 1
            if a[i][6] and not b[i][6]: deaths[zone(a[i][:2], own, en)] += 1
            if a[i][6] and b[i][6] and a[i][4] > 0 and b[i][4] == 0 and cheb(b[i][:2], own) > 4: banks[zone(b[i][:2], own, en)] += 1
        if len(alive) >= 2 and k % 10 == 0:
            cx = sum(p[0] for p in alive) / len(alive); cy = sum(p[1] for p in alive) / len(alive)
            spread.append(st.mean(cheb(p, (cx, cy)) for p in alive))
    cz = [0, 0, 0]
    for c in caps: cz[zone((c[4], c[5]), own, en)] += 1
    stc = [c for c in S.get('champions', []) if c['team'] == t]
    return dict(occ=occ, deaths=deaths, banks=banks, caps=cz, spread=st.mean(spread) if spread else 0,
                gold=sum(c.get('earnedGold', 0) for c in stc), kills=sum(c.get('kills', 0) for c in stc),
                route=''.join('OME'[zone((c[4], c[5]), own, en)] + ('g' if c[2] == 0 else '') for c in caps[:6]),
                gems=(d['meta'] or {}).get('submittedGems', [0, 0])[t], ogems=(d['meta'] or {}).get('submittedGems', [0, 0])[1 - t])

def run(job):
    a, b, m, out = job
    os.makedirs(out, exist_ok=True)
    if not glob.glob(os.path.join(out, '*.repl26a')):
        subprocess.run([ab.CLI, 'run', a, b, '--map', m, '-o', out], capture_output=True, env=ab.ENV)
    f = glob.glob(os.path.join(out, '*.repl26a'))
    if not f: return None
    cj = os.path.join(out, 'compact.json')
    if os.path.exists(cj): return json.load(open(cj))
    inner = os.path.join(out, 'replay.repl26a')
    with zipfile.ZipFile(f[0]) as z: z.extract('replay.repl26a', out)
    d = decode(inner); os.remove(inner); json.dump(d, open(cj, 'w')); return d

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('bots', nargs='+'); p.add_argument('--opps', default='sp_castera,sp_casterh')
    p.add_argument('--maps', default='eight'); p.add_argument('--jobs', type=int, default=4); A = p.parse_args()
    opps = ['bots/' + o for o in A.opps.split(',')]
    jobs, idx = [], []
    for b in A.bots:
        b = b.rstrip('/')
        for o in opps:
            for mn in A.maps.split(','):
                m = f'maps/{mn}.map26a'
                for side in 'AB':
                    x, y = (b, o) if side == 'A' else (o, b)
                    h = ab.sha(ab.wasm_of(x)) + ab.sha(ab.wasm_of(y))
                    jobs.append((x, y, m, f'out/lz/{mn}_{h}')); idx.append((b, o, mn, side))
    with ThreadPoolExecutor(A.jobs) as ex: res = list(ex.map(run, jobs))
    agg = collections.defaultdict(list)
    for (b, o, mn, side), d in zip(idx, res):
        if d: agg[(mn, b)].append(metrics(d, 0 if side == 'A' else 1))
    print('| map | bot | n | time own/mid/enemy r0-150 | r150-400 | r400+ | caps o/m/e | deaths o/m/e | banks o/m/e | spread | gold | kills | gems us-them | openings |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for (mn, b), L in sorted(agg.items()):
        n = len(L)
        def pct(ph):
            s = [sum(x['occ'][ph][z] for x in L) for z in range(3)]; T = max(sum(s), 1)
            return '/'.join(f'{100 * v / T:.0f}' for v in s)
        f = lambda key: '/'.join(f"{sum(x[key][z] for x in L) / n:.1f}" for z in range(3))
        rt = collections.Counter(x['route'] for x in L).most_common(2)
        print(f"| {mn} | {os.path.basename(b)} | {n} | {pct(0)} | {pct(1)} | {pct(2)} | {f('caps')} | {f('deaths')} | {f('banks')} | "
              f"{st.mean(x['spread'] for x in L):.1f} | {st.median(x['gold'] for x in L):.0f} | {st.mean(x['kills'] for x in L):.1f} | "
              f"{st.mean(x['gems'] for x in L):.0f}-{st.mean(x['ogems'] for x in L):.0f} | {', '.join(f'{r} x{c}' for r, c in rt)} |")
