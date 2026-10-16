#!/usr/bin/env python3
"""Online side of the calibration table: paired (opponent, map, side) comparison of each version change.

usage: python3 calib_online.py [DATA_DIR]   (default /mnt/project-files/online/data)
Prints, per version change, the shared pairings, flips each way, sign-test p, and per-map flips;
then, over every pairing played by 2+ versions, how often each map / rival tier ever flips.
"""
import collections, json, math, os, sys

DATA = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/online/data'
W = {  # version windows (UTC), from data/versions.jsonl and hourly.md
    'study26': [('2026-10-15T11:32', '2026-10-15T12:08')],
    'study27': [('2026-10-15T12:08', '2026-10-15T13:59'), ('2026-10-15T15:36', '2026-10-15T17:09')],
    'study28': [('2026-10-15T13:59', '2026-10-15T15:36')],
    'overnight': [('2026-10-15T17:09', '2026-10-16T07:47')],  # study27+corners fix, then study27-economy (switch time unknown)
    'ga65a6': [('2026-10-16T10:46', '2026-10-16T12:48')],
    'combined': [('2026-10-16T12:53', '2026-10-17')],  # ga65a6 + P_MONO + P_FUELGUARD + P_JACKPOT
}
CHANGES = [('study27', 'study26'), ('study28', 'study27'), ('overnight', 'study27'),
           ('ga65a6', 'overnight'), ('combined', 'ga65a6'), ('combined', 'overnight')]


def sign_p(k, n):
    if n == 0:
        return 1.0
    return min(1.0, sum(math.comb(n, i) for i in range(n + 1) if abs(i - n / 2) >= abs(k - n / 2)) / 2 ** n)


def ver(t):
    for v, ws in W.items():
        for a, b in ws:
            if a <= t < b:
                return v
    return None


games = [json.loads(l) for l in open(os.path.join(DATA, 'games.jsonl')) if l.strip()]
games = [g for g in games if g['result'] in ('win', 'loss') and g['kind'] == 'unranked']
latest = collections.defaultdict(dict)  # version -> pairing -> game (most recent)
for g in sorted(games, key=lambda g: g['at']):
    v = ver(g['at'])
    if v:
        latest[v][(g['opp_id'], g['map'], g['side'])] = g
for v in W:
    G = latest[v].values()
    print(f"{v:10s} {len(G):4d} distinct pairings, win {sum(g['result'] == 'win' for g in G)}")

print('\n## Version changes (A = new, B = old), shared pairings only')
out = []
for a, b in CHANGES:
    keys = set(latest[a]) & set(latest[b])
    fa = fb = 0
    pm = collections.defaultdict(lambda: [0, 0, 0])
    for k in keys:
        wa, wb = latest[a][k]['result'] == 'win', latest[b][k]['result'] == 'win'
        pm[k[1]][0] += 1
        if wa and not wb: fa += 1; pm[k[1]][1] += 1
        if wb and not wa: fb += 1; pm[k[1]][2] += 1
    p = sign_p(fa, fa + fb)
    maps = ', '.join(f'{m} {x[1]}-{x[2]}' for m, x in sorted(pm.items(), key=lambda kv: -(kv[1][1] + kv[1][2])) if x[1] + x[2])
    print(f'{a} vs {b}: {len(keys)} pairings, flips {fa}-{fb}, p={p:.2f}; by map {maps}')
    out.append(dict(a=a, b=b, pairs=len(keys), flips_a=fa, flips_b=fb, p=round(p, 3), by_map={m: x for m, x in pm.items()}))

print('\n## Which pairings can flip at all (pairings played by 2+ versions)')
byk = collections.defaultdict(list)
for v, d in latest.items():
    for k, g in d.items():
        byk[k].append(g)
for name, keyf in (('map', lambda k, gs: k[1]),
                   ('rival rank', lambda k, gs: (lambda r: 'top 10' if r <= 10 else 'top 11-30' if r <= 30 else '31+')(gs[-1]['opp_rank'] or 999)),
                   ('side', lambda k, gs: k[2])):
    t = collections.defaultdict(lambda: [0, 0, 0])  # pairings, ever flipped, wins share
    for k, gs in byk.items():
        if len(gs) < 2:
            continue
        r = {g['result'] for g in gs}
        x = t[keyf(k, gs)]
        x[0] += 1; x[1] += len(r) > 1; x[2] += sum(g['result'] == 'win' for g in gs) / len(gs)
    print(f'\n{name:12s} pairings  flip%  win%')
    for m, (n, f, w) in sorted(t.items(), key=lambda kv: -kv[1][1] / kv[1][0]):
        print(f'{m:12s} {n:8d} {100 * f / n:5.0f}% {100 * w / n:5.0f}%')
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calib_online.json'), 'w'), indent=1)
