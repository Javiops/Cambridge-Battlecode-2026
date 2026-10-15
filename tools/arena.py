#!/usr/bin/env python3
"""Run many cambc matches in parallel and summarise them.
usage (from a cambc workspace dir):
  python3 arena.py BOT_A BOT_B [--maps 'maps/**/*.map26a'] [--jobs 4] [--sides both|a|b] [--rounds N] [--out out/arena] [--keep]
Prints one line per match and a summary (win rate for BOT_A, mean gems, gems per 100 rounds)."""
import argparse, glob, json, os, shutil, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor
CLI = os.environ.get('CAMBC_CLI', 'cambc')
# compile each bot once and reuse it: without this every game spends ~1.5 s of CPU compiling both wasm bots
os.environ.setdefault('CAMBC_WASMTIME_CACHE', os.path.abspath(os.path.join('out', 'wasmtime-cache')))
def build(bot):
    r = subprocess.run([CLI, 'build', bot], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:], file=sys.stderr); sys.exit(f'build failed: {bot}')
def one(job):
    a, b, m, outdir, rounds, keep = job
    os.makedirs(outdir, exist_ok=True)
    stats = os.path.join(outdir, 'stats.json')
    cmd = [CLI, 'run', a, b, '--map', m, '-o', outdir, '--statistics', stats]
    if rounds: cmd += ['--rounds', str(rounds)]
    r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'})
    res = {'a': a, 'b': b, 'map': m, 'ok': os.path.exists(stats), 'log': r.stdout[-1500:] + r.stderr[-800:]}
    if res['ok']:
        d = json.load(open(stats))
        res.update(outcome=d['outcome'], round=d['round'], gems=[t['submittedGems'] for t in d['teams']],
                   faults=d['botFaults'],
                   champs=[{k: c[k] for k in ('team', 'type', 'collectedGems', 'submittedGems', 'earnedGold', 'spentGold', 'kills', 'deaths', 'monsterDamageDone', 'championDamageDone')} for c in d['champions']])
        # pull the stdout logs out of the bundle for later analysis
        for f in glob.glob(os.path.join(outdir, '*.repl26a')):
            try:
                with zipfile.ZipFile(f) as z:
                    for n in ('team-a.stdout', 'team-b.stdout'):
                        if n in z.namelist(): z.extract(n, outdir)
            except zipfile.BadZipFile: pass
            if not keep: os.remove(f)
    return res
def main():
    p = argparse.ArgumentParser(); p.add_argument('bot_a'); p.add_argument('bot_b')
    p.add_argument('--maps', default='maps/**/*.map26a'); p.add_argument('--jobs', type=int, default=4)
    p.add_argument('--sides', default='both'); p.add_argument('--rounds', type=int, default=0)
    p.add_argument('--out', default='out/arena'); p.add_argument('--keep', action='store_true'); p.add_argument('--json', default='')
    p.add_argument('--no-build', action='store_true')
    A = p.parse_args()
    maps = sorted(glob.glob(A.maps, recursive=True))
    if not maps: sys.exit('no maps')
    if not A.no_build:
        build(A.bot_a); build(A.bot_b)
    jobs = []
    for i, m in enumerate(maps):
        name = os.path.splitext(os.path.basename(m))[0]
        if A.sides in ('both', 'a'): jobs.append((A.bot_a, A.bot_b, m, os.path.join(A.out, f'{name}_A'), A.rounds, A.keep))
        if A.sides in ('both', 'b'): jobs.append((A.bot_b, A.bot_a, m, os.path.join(A.out, f'{name}_B'), A.rounds, A.keep))
    with ThreadPoolExecutor(A.jobs) as ex: results = list(ex.map(one, jobs))
    wins = losses = draws = 0; gdiff = []; rate = []; fails = 0
    for r in results:
        if not r['ok']:
            fails += 1; print('FAIL', r['map'], r['log'].strip().splitlines()[-1:] ); continue
        me = 0 if r['a'] == A.bot_a else 1
        g_me, g_op = r['gems'][me], r['gems'][1 - me]
        won = (r['outcome'] == ('teamA' if me == 0 else 'teamB'))
        lost = (r['outcome'] in ('teamA', 'teamB')) and not won
        wins += won; losses += lost; draws += (not won and not lost)
        gdiff.append(g_me - g_op); rate.append(100.0 * g_me / max(1, r['round']))
        mine = [c for c in r['champs'] if c['team'] == me]
        print(f"{os.path.basename(r['map']):22s} side={'A' if me==0 else 'B'} {'WIN ' if won else 'LOSS' if lost else 'DRAW'} r={r['round']:4d} gems {g_me:4d}-{g_op:4d}  deaths={sum(c['deaths'] for c in mine)} kills={sum(c['kills'] for c in mine)} faults={r['faults']}")
    n = max(1, len(gdiff))
    print(f"\n{A.bot_a} vs {A.bot_b}: {wins}W {losses}L {draws}D of {len(results)} ({fails} failed) | winrate {100.0*wins/max(1,wins+losses+draws):.0f}% | mean gem diff {sum(gdiff)/n:+.0f} | gems/100 rounds {sum(rate)/n:.1f}")
    if A.json:
        json.dump({'bot_a': A.bot_a, 'bot_b': A.bot_b, 'wins': wins, 'losses': losses, 'draws': draws, 'results': results}, open(A.json, 'w'))
if __name__ == '__main__': main()
