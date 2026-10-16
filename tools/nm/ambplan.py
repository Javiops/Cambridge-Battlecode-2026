#!/usr/bin/env python3
"""Farm plan of a team on one map, turn by turn (2026-10-16, new-maps thread, the user's "lost on ambush" ask).

usage (repo root):
  python3 tools/nm/ambplan.py bots/US [--opps sp_farm,...] [--map ambush]     our local games (replays under out/lz/)
  python3 tools/nm/ambplan.py --top [--map ambush]                            the top-10 replays of the morning study

Per game: capture order (round, gems or gold, camp position seen from our side), banks (round, gems), 1000-gem round,
and per champion the share of its rounds walking / at a camp (within 3 tiles) / at home (within 6 of our spawn) /
standing elsewhere (idle) / dead, plus the round it first reached a camp.
"""
import argparse, gzip, json, os, statistics as st, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import localzones as lz  # noqa: E402
import ab  # noqa: E402

def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def camps_of(m):
    d = json.loads(subprocess.run(['node', 'tools/mapjson.js', m], capture_output=True, text=True).stdout)
    return [(c['x'], c['y']) for c in d['camps']], d['w'], d['h']

def plan(d, t, camps, W, H):
    R = d['R']; CH = d['champs']
    me = [i for i, c in enumerate(CH) if c[1] == t]
    ps = [R[1][3][i][:2] for i in me]; home = (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
    own = (lambda p: p) if t == 0 else (lambda p: (W - 1 - p[0], H - 1 - p[1]))
    last = {}; caps = []; seen = set()
    for g in d['G']:
        r, ci, grp, typ, x, y, state, team, alive, rg, rgold = g
        if state == 'reward_available' and team in (0, 1): last[grp] = (team, r)
        if state == 'respawning' and grp in last and (r, grp) not in seen:
            seen.add((r, grp)); tm = last.pop(grp)[0]
            if tm == t: caps.append((r, rg, rgold, own((x, y))))
    banks = []
    sub = [x[1 + t] for x in R]
    for k in range(1, len(R)):
        if sub[k] > sub[k - 1]: banks.append((R[k][0], sub[k] - sub[k - 1]))
    reach = next((R[k][0] for k in range(len(R)) if sub[k] >= 1000), None)
    act = {i: [0, 0, 0, 0, 0] for i in me}; first = {i: None for i in me}
    for k in range(1, len(R)):
        a = R[k - 1][3]; b = R[k][3]
        for i in me:
            if not b[i][6]: act[i][4] += 1; continue
            p = tuple(b[i][:2]); near = min(cheb(p, c) for c in camps) <= 3
            if near and first[i] is None: first[i] = R[k][0]
            if tuple(a[i][:2]) != p and a[i][6]: act[i][0] += 1
            elif near: act[i][1] += 1
            elif cheb(p, home) <= 6: act[i][2] += 1
            else: act[i][3] += 1
    return caps, banks, reach, {CH[i][2]: (act[i], first[i]) for i in me}

def show(tag, caps, banks, reach, act, n=10):
    print(f'== {tag}  reach1000={reach}  banks={len(banks)} avg bag={st.mean(b for _, b in banks) if banks else 0:.0f}')
    print('   caps: ' + ' '.join(f'r{r}:{"G%d" % g if g else "o%d" % gold}{p}' for r, g, gold, p in caps[:n]))
    print('   banks: ' + ' '.join(f'r{r}:{b}' for r, b in banks[:n]))
    for name, (a, f) in act.items():
        tot = max(1, sum(a))
        print(f'   {name:12s} walk {100*a[0]/tot:3.0f}%  camp {100*a[1]/tot:3.0f}%  home {100*a[2]/tot:3.0f}%  idle {100*a[3]/tot:3.0f}%  dead {100*a[4]/tot:3.0f}%  first camp r{f}')

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('bots', nargs='*'); p.add_argument('--opps', default='sp_castera,sp_casterh,sp_hunt,sp_centre,sp_farm')
    p.add_argument('--map', default='ambush'); p.add_argument('--top', action='store_true'); p.add_argument('--n', type=int, default=10); A = p.parse_args()
    m = f'maps/{A.map}.map26a'; camps, W, H = camps_of(m)
    if A.top:
        D = '/mnt/project-files/analysis/new-maps-2026-10-16/data/'
        for g in json.load(open(D + 'games.json')):
            if g['map'] != A.map or g['who'] != 'top' or not g['win']: continue
            try: d = json.load(gzip.open(D + 'compact/' + g['match'] + '.json.gz', 'rt'))
            except FileNotFoundError: continue
            show(f"{g['team']} vs {g['opp']}", *plan(d, 'ab'.index(g['side']), camps, W, H), n=A.n)
        sys.exit()
    for b in A.bots:
        b = b.rstrip('/'); ab.build(b)
        for o in A.opps.split(','):
            o = 'bots/' + o
            for side in 'AB':
                x, y = (b, o) if side == 'A' else (o, b)
                d = lz.run((x, y, m, f'out/lz/{A.map}_{ab.sha(ab.wasm_of(x))}{ab.sha(ab.wasm_of(y))}'))
                if d: show(f'{os.path.basename(b)} vs {os.path.basename(o)} side {side}', *plan(d, 0 if side == 'A' else 1, camps, W, H), n=A.n)
