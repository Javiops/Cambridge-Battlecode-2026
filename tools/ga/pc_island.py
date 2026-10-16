#!/usr/bin/env python3
"""Run the weights GA (tools/ga/ga.py) as a standing island on a home PC and publish it to a git branch.

One generation per `ga.py run --gens 1` call (it resumes from WORK/state.json, so a kill loses at most the
generation in progress; finished games are cached in WORK/games.jsonl). After every generation the state, the log
and the top genomes are copied to islands/pc/ and committed and pushed to the current branch (pc-island).

usage (repo root, after `ga.py --work out/ga-pc prepare --base bots/study27-economy --center ga65a6`):
  py tools/ga/pc_island.py --jobs 12
Stop: create the file out/ga-pc/STOP (stops after the current generation), or kill the python processes.
"""
import argparse, json, os, shutil, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genome as G  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def git(*args, check=False):
    r = subprocess.run(['git', *args], capture_output=True, text=True)
    if check and r.returncode:
        print('git', *args, 'failed:', r.stderr[-500:], flush=True)
    return r


def publish(work, dest, top):
    st = json.load(open(os.path.join(work, 'state.json')))
    meta = json.load(open(os.path.join(work, 'meta.json')))
    if meta.get('center'):
        G.set_center(meta['center'])
    os.makedirs(dest, exist_ok=True)
    for f in ('state.json', 'log.md', 'meta.json', 'validate.txt'):
        if os.path.exists(os.path.join(work, f)):
            shutil.copy(os.path.join(work, f), os.path.join(dest, f))
    inds = st['inds']
    evald = [i for i, d in inds.items() if d['deltas'] and i != st['base']]
    shr = lambda i: sum(inds[i]['deltas']) / (len(inds[i]['deltas']) + 1.0)
    best = sorted(evald, key=shr, reverse=True)[:top]
    out = {'gen': st['gen'], 'center': 'ga65a6', 'updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'best': [{'id': i, 'shrunk': round(shr(i), 4), 'n': len(inds[i]['deltas']), 'genome': inds[i]['g'],
                     'diff_vs_center': G.diff(inds[i]['g'])} for i in best]}
    json.dump(out, open(os.path.join(dest, 'best.json'), 'w'), indent=1)
    return st['gen'], best[:1]


def push(branch, msg):
    git('add', '-A', 'islands/pc')
    if not git('diff', '--cached', '--quiet').returncode:
        return
    git('commit', '-q', '-m', msg, check=True)
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        if git('push', '-q', '-u', 'origin', branch, check=True).returncode == 0:
            return


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--work', default='out/ga-pc')
    p.add_argument('--jobs', type=int, default=12)
    p.add_argument('--pop', type=int, default=16)
    p.add_argument('--maps', type=int, default=12)
    p.add_argument('--opps', default='bots/ga65a6,bots/spar11,bots/spar12,bots/spar16')
    p.add_argument('--seed', type=int, default=44)
    p.add_argument('--dest', default='islands/pc')
    p.add_argument('--top', type=int, default=8)
    A = p.parse_args()
    branch = git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip()
    if branch in ('main', 'master', 'HEAD'):
        sys.exit(f'refusing to publish to {branch}; check out pc-island')
    stop = os.path.join(A.work, 'STOP')
    while not os.path.exists(stop):
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.join(HERE, 'ga.py'), '--work', A.work, '--jobs', str(A.jobs),
                            'run', '--gens', '1', '--pop', str(A.pop), '--maps', str(A.maps), '--opps', A.opps,
                            '--seed', str(A.seed)])
        if r.returncode:
            print(f'ga.py exited {r.returncode}; retrying in 60 s', flush=True)
            time.sleep(60)
            continue
        gen, top = publish(A.work, A.dest, A.top)
        push(branch, f'pc island: generation {gen - 1} done ({(time.time() - t0) / 60:.1f} min), top {top}')
        if git('fetch', '-q', 'origin').returncode == 0 and git('ls-tree', '-r', '--name-only', 'origin/main',
                                                               'tools/ga/island.py').stdout.strip():
            print('NOTE: tools/ga/island.py is on origin/main: switch this PC to the island protocol', flush=True)
    print('STOP file found, exiting', flush=True)


if __name__ == '__main__':
    main()
