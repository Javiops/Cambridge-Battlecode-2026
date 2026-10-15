#!/usr/bin/env python3
"""pacecmp.py BOT1 BOT2 ... : solo pace (rounds to finish vs idle, side a) on official + gen + gen4 maps; compares each to the first"""
import sys, subprocess, json, glob, os, concurrent.futures as cf
bots = sys.argv[1:]
maps = sorted(glob.glob('maps/*.map26a')) + sorted(glob.glob('maps_gen/*.map26a')) + sorted(glob.glob('maps_gen4/*.map26a'))
env = dict(os.environ, CAMBC_NO_UPDATE_CHECK='1')
def run(job):
    bot, m = job; od = f'out/pace/{bot}/{os.path.basename(m)[:-7]}'; st = od + '/stats.json'
    if not os.path.exists(st):
        os.makedirs(od, exist_ok=True)
        subprocess.run(['cambc', 'run', f'bots/{bot}', 'bots/idle', '--map', m, '-o', od, '--statistics', st], env=env, capture_output=True)
        for f in glob.glob(od + '/*.repl26a'): os.remove(f)
    d = json.load(open(st)); g = d['teams'][0]['submittedGems']
    return bot, m, d['round'] if g >= 1000 else 2000 - g
with cf.ThreadPoolExecutor(4) as ex: res = list(ex.map(run, [(b, m) for b in bots for m in maps]))
R = {(b, m): r for b, m, r in res}
def grp(m): return 'official' if m.startswith('maps/') else 'gen' if 'maps_gen/' in m else 'gen4'
for b in bots:
    line = f'{b:12}'
    for gname in ('official', 'gen', 'gen4'):
        ms = [m for m in maps if grp(m) == gname]
        tot = sum(R[(b, m)] for m in ms)
        if b != bots[0]:
            fa = sum(R[(b, m)] < R[(bots[0], m)] - 5 for m in ms); sl = sum(R[(b, m)] > R[(bots[0], m)] + 5 for m in ms)
            line += f' | {gname} {tot:6} ({tot - sum(R[(bots[0], m)] for m in ms):+5}) faster {fa:2} slower {sl:2}'
        else: line += f' | {gname} {tot:6}'
    print(line)
json.dump({f'{b}|{m}': r for (b, m), r in R.items()}, open('out/pace/last.json', 'w'))
