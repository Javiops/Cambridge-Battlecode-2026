#!/usr/bin/env python3
"""Per-team fight and farm statistics from decoded games (compact steps format, see
analysis/top2-dissection-2026-10-15/data/DATA.md). Same definitions for online games and local panel games,
so a sparring opponent can be checked against the real teams it imitates.

usage:
  gamestats.py GAMES.json MAPS_DIR STEPS_DIR [--out rows.jsonl]
GAMES.json: list of {"match", "map", "tags": [tag of team 0, tag of team 1], "result0": "win"|"loss"}.
Steps file: STEPS_DIR/<match>.c.jsonl.

Per team and game it writes: rounds, gems banked, deaths, deaths before round 500, kills, gems carried at death,
deaths within 6 of an altar with 10+ gems, centre share (champion-rounds within 8 of the map centre, rounds 100-700),
and contact rows for the curves: per contact turn (enemy alive within 8), hp band, retreat (distance to the nearest
enemy grows next round, only with an enemy within 5), died within 10 rounds.
`summary` (gamestats.py --summary rows.jsonl [--by tag|tag,map]) prints the table.
"""
import argparse, collections, json, os, sys

HB = [0, .2, .3, .4, .5, .6, .7, .8, .9, 1.01]


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def band(f):
    for i in range(len(HB) - 1):
        if HB[i] < f <= HB[i + 1]:
            return i
    return 0


def load(path):
    rounds = []
    for line in open(path):
        d = json.loads(line)
        if d.get('t') == 'round':
            rounds.append(d)
    rounds.sort(key=lambda d: d['r'])
    return rounds


def game_rows(g, maps_dir, steps_dir):
    mname = g['map'].replace('_', '-')
    m = json.load(open(os.path.join(maps_dir, mname + '.json')))
    altars = [(x, y) for y, row in enumerate(m['grid']) for x, c in enumerate(row) if c == 'A']
    centre = ((m['w'] - 1) / 2, (m['h'] - 1) / 2)
    R = load(os.path.join(steps_dir, g['match'] + '.c.jsonl'))
    if len(R) < 50:
        return []
    out = []
    by_r = {d['r']: d for d in R}
    last = R[-1]
    teams = {0: {}, 1: {}}
    for t in (0, 1):
        teams[t] = dict(match=g['match'], map=g['map'], team=t, tag=g['tags'][t], rounds=last['r'],
                        gems=last['sub'][t], win=(g['result0'] == 'win') == (t == 0), deaths=0, deaths500=0, kills=0,
                        gems_at_death=0, altar_carry_deaths=0, centre=0, crounds=0,
                        curve=[[0, 0, 0, 0] for _ in range(len(HB) - 1)])  # per band: retreat-eligible, retreats, contact, died10
    prev = None
    death_rounds = collections.defaultdict(list)  # champion idx -> rounds it died
    for d in R:
        if prev is not None:
            pc = {c[0]: c for c in prev['champs']}
            for c in d['champs']:
                p = pc.get(c[0])
                if p and p[9] == 1 and c[9] == 0:
                    t = c[1]
                    T = teams[t]
                    T['deaths'] += 1
                    T['deaths500'] += d['r'] < 500
                    T['gems_at_death'] += p[7]
                    if p[7] >= 10 and altars and min(cheb((p[3], p[4]), a) for a in altars) <= 6:
                        T['altar_carry_deaths'] += 1
                    teams[1 - t]['kills'] += 1
                    death_rounds[c[0]].append(d['r'])
        prev = d
    # contact turns and centre share
    for d in R:
        r = d['r']
        alive = [c for c in d['champs'] if c[9] == 1 and c[3] >= 0]
        if 100 <= r <= 700:
            for c in alive:
                teams[c[1]]['crounds'] += 1
                teams[c[1]]['centre'] += cheb((c[3], c[4]), centre) <= 8
        nxt = by_r.get(r + 1)
        if not nxt:
            continue
        npos = {c[0]: c for c in nxt['champs']}
        for c in alive:
            foes = [e for e in alive if e[1] != c[1]]
            if not foes:
                continue
            dmin = min(cheb((c[3], c[4]), (e[3], e[4])) for e in foes)
            if dmin > 8:
                continue
            b = band(c[5] / max(1, c[6]))
            cu = teams[c[1]]['curve'][b]
            cu[2] += 1
            cu[3] += any(r < dr <= r + 10 for dr in death_rounds[c[0]])
            n = npos.get(c[0])
            if dmin <= 5 and n and n[9] == 1 and n[3] >= 0 and cheb((n[3], n[4]), (c[3], c[4])) <= 1:
                nf = [npos.get(e[0]) for e in foes]
                nf = [e for e in nf if e and e[9] == 1 and e[3] >= 0]
                if nf:
                    cu[0] += 1
                    # retreat: our own step increased the distance to the foes' current positions
                    d_after = min(cheb((n[3], n[4]), (e[3], e[4])) for e in foes)
                    cu[1] += d_after > dmin
    for t in (0, 1):
        out.append(teams[t])
    return out


def summary(rows, by):
    keys = by.split(',')
    agg = collections.OrderedDict()
    for x in rows:
        k = tuple(x[k] for k in keys)
        a = agg.setdefault(k, dict(n=0, win=0, deaths=0, deaths500=0, kills=0, gems=0, rounds=0, gad=0, acd=0, centre=0,
                                   crounds=0, curve=[[0, 0, 0, 0] for _ in range(len(HB) - 1)]))
        a['n'] += 1; a['win'] += x['win']; a['deaths'] += x['deaths']; a['deaths500'] += x['deaths500']
        a['kills'] += x['kills']; a['gems'] += x['gems']; a['rounds'] += x['rounds']; a['gad'] += x['gems_at_death']
        a['acd'] += x['altar_carry_deaths']; a['centre'] += x['centre']; a['crounds'] += x['crounds']
        for i in range(len(HB) - 1):
            for j in range(4):
                a['curve'][i][j] += x['curve'][i][j]
    print(f"{'group':28s} {'n':>4s} {'win%':>5s} {'deaths':>6s} {'d<500':>6s} {'kills':>6s} {'gems/100r':>9s} {'gem@death':>9s} "
          f"{'altar-carry':>11s} {'centre%':>7s} {'died10':>6s} | retreat share by hp 30-40 40-50 50-60 60-70 90-100")
    for k, a in sorted(agg.items()):
        n = a['n']
        cont = sum(c[2] for c in a['curve']); d10 = sum(c[3] for c in a['curve'])
        rs = ' '.join(f"{a['curve'][i][1] / a['curve'][i][0]:.2f}" if a['curve'][i][0] else '  - ' for i in (2, 3, 4, 5, 8))
        print(f"{'/'.join(map(str, k)):28s} {n:4d} {100 * a['win'] / n:5.0f} {a['deaths'] / n:6.1f} {a['deaths500'] / n:6.1f} "
              f"{a['kills'] / n:6.1f} {100 * a['gems'] / max(1, a['rounds']):9.1f} {a['gad'] / n:9.0f} {a['acd'] / n:11.1f} "
              f"{100 * a['centre'] / max(1, a['crounds']):7.0f} {100 * d10 / max(1, cont):5.1f}% | {rs}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('games', nargs='?'); p.add_argument('maps', nargs='?'); p.add_argument('steps', nargs='?')
    p.add_argument('--out', default='rows.jsonl'); p.add_argument('--summary', default='')
    p.add_argument('--by', default='tag')
    A = p.parse_args()
    if A.summary:
        rows = [json.loads(l) for f in A.summary.split(',') for l in open(f) if l.strip()]
        summary(rows, A.by)
        return
    G = json.load(open(A.games))
    with open(A.out, 'w') as f:
        for g in G:
            if not os.path.exists(os.path.join(A.steps, g['match'] + '.c.jsonl')):
                continue
            try:
                for row in game_rows(g, A.maps, A.steps):
                    f.write(json.dumps(row) + '\n')
            except Exception as e:  # a broken decode should not stop the batch
                print('skip', g['match'], e, file=sys.stderr)


if __name__ == '__main__':
    main()
