#!/usr/bin/env python3
"""Judge bots against the specialist panel instead of against each other (2026-10-16, analysis/local-judge).

usage (repo root, after `cambc init --yes` and tools/panel/build_panel.sh):
  python3 tools/panel/panel.py bots/A bots/B [...] [--opps sp_castera,sp_casterh,...] [--maps 'maps/*.map26a,maps_hold60/*.map26a']

Every bot plays every specialist on every map from both sides (results cached in out/ab-cache, shared with ab.py and
gate.py). Prints each bot's record per specialist, and for each pair of bots the games that flip (won by one, lost by
the other in the same opponent+map+side), which is what the online paired comparison (online/lfl.py) measures.
"""
import argparse, glob, hashlib, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ab  # noqa: E402

DEFAULT_OPPS = 'sp_castera,sp_casterh,sp_hunt,sp_centre,sp_farm'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('bots', nargs='+')
    p.add_argument('--opps', default=DEFAULT_OPPS)
    p.add_argument('--maps', default='maps/*.map26a,maps_hold60/*.map26a')
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    p.add_argument('--json', default='')
    A = p.parse_args()
    bots = [b.rstrip('/') for b in A.bots]
    opps = ['bots/' + o if '/' not in o else o for o in A.opps.split(',')]
    missing = [o for o in opps + bots if not os.path.isdir(o)]
    if missing:
        sys.exit(f'missing bot folders: {missing} (tools/panel/build_panel.sh builds the specialists)')
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(ab.build, bots + opps))
    ver = subprocess.run([ab.CLI, '--version'], capture_output=True, text=True, env=ab.ENV).stdout.strip()
    maps = sorted(m for pat in A.maps.split(',') for m in glob.glob(pat))
    h = {b: ab.sha(ab.wasm_of(b)) for b in bots + opps}
    cache = os.path.join('out', 'ab-cache'); os.makedirs(cache, exist_ok=True)
    jobs, idx = [], []
    for b in bots:
        for o in opps:
            for m in maps:
                hm = hashlib.sha256((ab.sha(m) + ver).encode()).hexdigest()[:8]
                for side in 'AB':
                    x, y = (b, o) if side == 'A' else (o, b)
                    jobs.append((x, y, m, f'{h[x]}_{h[y]}_{hm}', cache, os.path.join('out', 'panel', f'{os.path.basename(x)}_{os.path.basename(y)}_{os.path.basename(m)}'), False))
                    idx.append((b, o, m, side))
    with ThreadPoolExecutor(A.jobs) as ex:
        res = list(ex.map(ab.play, jobs))
    won = {}; broken = 0; deaths = {}
    for (b, o, m, side), r in zip(idx, res):
        if not r.get('ok'):
            broken += 1; continue
        me = 0 if side == 'A' else 1
        won[(b, o, m, side)] = r['outcome'] == ('teamA' if me == 0 else 'teamB')
        deaths.setdefault((b, o), []).append(r['deaths'][me])
    print(f'{len(maps)} maps x 2 sides x {len(opps)} specialists; {broken} games did not finish')
    print(f"\n{'bot':28s} " + ' '.join(f'{os.path.basename(o):>12s}' for o in opps) + f" {'all':>8s}")
    for b in bots:
        tot = [0, 0]; cells = []
        for o in opps:
            ks = [k for k in won if k[0] == b and k[1] == o]
            w = sum(won[k] for k in ks); tot[0] += w; tot[1] += len(ks)
            cells.append(f'{100 * w / max(1, len(ks)):5.0f}% d{sum(deaths.get((b, o), [0])) / max(1, len(deaths.get((b, o), [1]))):4.1f}')
        print(f'{b:28s} ' + ' '.join(f'{c:>12s}' for c in cells) + f' {100 * tot[0] / max(1, tot[1]):7.1f}%')
    out = {'maps': len(maps), 'opps': opps, 'pairs': []}
    for i, a in enumerate(bots):
        for b in bots[i + 1:]:
            fa = fb = 0; per = {}
            for (x, o, m, side), w in won.items():
                if x != a or (b, o, m, side) not in won: continue
                wb = won[(b, o, m, side)]
                if w and not wb: fa += 1; per[os.path.basename(o)] = per.get(os.path.basename(o), [0, 0]); per[os.path.basename(o)][0] += 1
                if wb and not w: fb += 1; per[os.path.basename(o)] = per.get(os.path.basename(o), [0, 0]); per[os.path.basename(o)][1] += 1
            pv = ab.sign_p(fa, fa + fb)
            print(f'\n{a} vs {b}: games that flip {fa}-{fb} ({100 * fa / max(1, fa + fb):.0f}% for {os.path.basename(a)}), p={pv:.3f}; '
                  + ', '.join(f'{k} {v[0]}-{v[1]}' for k, v in per.items()))
            out['pairs'].append({'a': a, 'b': b, 'flips': [fa, fb], 'p': pv, 'by_opp': per})
    if A.json:
        json.dump(out, open(A.json, 'w'), indent=1)


if __name__ == '__main__':
    main()
