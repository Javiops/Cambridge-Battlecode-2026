#!/usr/bin/env python3
"""Rival panel: play BASE and each CANDIDATE against every panel rival on every map, both sides, then judge
the candidate game by game against the base (same rival, same map, same side), like the online judge.

usage (from the repo root, after `cambc init`):
    python3 panel/run.py bots/v110 bots/my_change                 # 9 rivals x 40 maps x 2 sides = 720 games per bot
    python3 panel/run.py bots/v110 bots/my_change --rivals pA,pInv --maps elk_arena,the_farm --jobs 8
    python3 panel/run.py bots/v110 bots/my_change --gold          # + gold@r400 and deaths (decodes replays, needs node)

Results go to out/panel/res/cal_<bot>_<rival>/{A,B}_<map>.{json,repl26a} (A_ = our bot is team A).
<bot> is the folder name plus a hash of its src/, so an edited bot never reuses stale games and an
unchanged base is played only once. The engine is deterministic: a game that is already there is skipped.
"""
import argparse, glob, hashlib, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out', 'panel')
RIVALS = 'pA,pB,pC,pInv,pD,pF,pE,pG,pM'


def tag(bot):
    h = hashlib.sha256()
    for f in sorted(glob.glob(os.path.join(bot, 'src', '**', '*'), recursive=True)):
        if os.path.isfile(f):
            h.update(os.path.relpath(f, bot).encode()); h.update(open(f, 'rb').read())
    return f"{os.path.basename(os.path.normpath(bot))}-{h.hexdigest()[:8]}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('base'); ap.add_argument('cands', nargs='+')
    ap.add_argument('--rivals', default=RIVALS, help=f'comma list from panel/rivals (default {RIVALS})')
    ap.add_argument('--maps', default='', help='comma list of map names (default: every map in --map-dir)')
    ap.add_argument('--map-dir', default='maps_site40')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    ap.add_argument('--gold', action='store_true', help='also report gold@r400 and deaths (scripts/gold400.py)')
    a = ap.parse_args()

    rivals = a.rivals.split(',')
    maps = sorted(glob.glob(os.path.join(ROOT, a.map_dir, '*.map26a')))
    if a.maps:
        want = set(a.maps.split(',')); maps = [m for m in maps if os.path.basename(m)[:-7] in want]
    if not maps: sys.exit(f'no maps found in {a.map_dir}')
    bots = [os.path.abspath(b) for b in [a.base] + a.cands]
    for b in bots:
        if not os.path.isdir(os.path.join(b, 'src')): sys.exit(f'{b}: no src/ folder')
    tags = [tag(b) for b in bots]

    rows = []
    for bot, t in zip(bots, tags):
        for r in rivals:
            d = os.path.join(OUT, 'res', f'cal_{t}_{r}'); os.makedirs(d, exist_ok=True)
            rv = os.path.join(ROOT, 'panel', 'rivals', r)
            if not os.path.isdir(rv): sys.exit(f'unknown rival {r}')
            for m in maps:
                name = os.path.basename(m)[:-7]
                for side, (x, y) in (('A', (bot, rv)), ('B', (rv, bot))):
                    js = os.path.join(d, f'{side}_{name}.json')
                    if not os.path.exists(js):
                        rows.append(f'{x} {y} {m} {js[:-4]}repl26a --statistics {js} --json')
    print(f'{len(bots)} bots x {len(rivals)} rivals x {len(maps)} maps x 2 sides; {len(rows)} games to play')
    if rows:
        man = os.path.join(OUT, 'manifest.txt'); open(man, 'w').write('\n'.join(rows) + '\n')
        subprocess.run(['cambc', 'run-batch', man, '--jobs', str(a.jobs), '--release', '--json'], cwd=ROOT,
                       stdout=subprocess.DEVNULL, env={**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'})
        missing = sum(1 for row in rows if not os.path.exists(row.split()[5]))
        if missing == len(rows): sys.exit('no game produced statistics: see the cambc error above (did `cambc init` run?)')
        if missing: print(f'WARNING: {missing} games produced no statistics (build error or crash?)')

    env = {**os.environ, 'PAN': ','.join(rivals)}
    if a.maps: env['MAPS'] = a.maps
    scripts = os.path.join(ROOT, 'panel', 'scripts')
    subprocess.run([sys.executable, os.path.join(scripts, 'judge.py'), *tags], cwd=OUT, env=env)
    if a.gold:
        subprocess.run([sys.executable, os.path.join(scripts, 'gold400.py'), *tags], cwd=OUT, env=env)


if __name__ == '__main__':
    main()
