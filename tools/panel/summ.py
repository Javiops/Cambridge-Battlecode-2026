#!/usr/bin/env python3
"""Summarise arena.py --json results from OUR bot's point of view.
usage: summ.py OURBOT RESULTS.json [...]   -> one line per file: W-L, our deaths/kills per game, gems, by map losses"""
import json, sys, collections
our = sys.argv[1]
for f in sys.argv[2:]:
    R = json.load(open(f)); rs = R['results'] if isinstance(R, dict) and 'results' in R else R
    if isinstance(rs, dict): rs = list(rs.values())
    w = l = 0; dd = kk = gg = og = 0; lost = collections.Counter(); n = 0
    for x in rs:
        if not x.get('ok'): continue
        t = 0 if x['a'].rstrip('/').endswith(our) else 1
        n += 1
        win = x['outcome'] == ('teamA' if t == 0 else 'teamB')
        w += win; l += not win
        if not win: lost[x['map'].split('/')[-1].split('.')[0]] += 1
        dd += sum(c['deaths'] for c in x['champs'] if c['team'] in (t, 'AB'[t], 'ab'[t]))
        kk += sum(c['kills'] for c in x['champs'] if c['team'] in (t, 'AB'[t], 'ab'[t]))
        gg += x['gems'][t]; og += x['gems'][1 - t]
    print(f"{f}: {w}-{l}  our deaths/game {dd/n:.1f} kills/game {kk/n:.1f}  gems {gg/n:.0f} vs {og/n:.0f}  losses: {dict(lost)}")
