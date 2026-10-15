#!/usr/bin/env python3
"""A/B test: is CANDIDATE better than BASE? One command, fast, honest.

usage (from the repo root, after `cambc init --yes`):
  python3 tools/ab.py bots/CANDIDATE bots/BASE                # official 9 + maps_gen (44) + maps_hold60 (60)
  python3 tools/ab.py bots/CAND bots/BASE --sets official,dev  # pick sets: official, gen, hold, dev (200 maps)
  python3 tools/ab.py bots/CAND bots/BASE --jobs 8 --keep      # keep replays in out/ab/...

What it does
  * builds both bots at the same time (cambc only rebuilds what changed)
  * turns on the wasmtime compile cache (CAMBC_WASMTIME_CACHE): without it every game spends ~1.5 s of CPU
    compiling the two bots before round 1; with it a game costs ~0.5 s of CPU, so 4x more games per minute
  * caches every result by (wasm A, wasm B, map): games are deterministic, so a game already played is never
    played again (re-running a comparison, or the base against the same rival, is free)
  * plays every map from both sides and scores by MAPS, not games: a map counts for you only if you win it
    from both sides. It also finds the maps where the two bots played the exact same game (the candidate
    behaved like the base, the side decided), which are pure noise in a games count.
  * prints a verdict with the sign test and the rough number of maps you would still need.
"""
import argparse, glob, hashlib, json, math, os, subprocess, sys, time, zipfile
from concurrent.futures import ThreadPoolExecutor

CLI = os.environ.get('CAMBC_CLI', 'cambc')
SETS = {'official': 'maps/*.map26a', 'gen': 'maps_gen/*.map26a', 'hold': 'maps_hold60/*.map26a',
        'dev': 'maps_dev200/*.map26a'}
ENV = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'}
ENV.setdefault('CAMBC_WASMTIME_CACHE', os.path.abspath(os.path.join('out', 'wasmtime-cache')))


def wasm_of(bot):
    return os.path.join(bot, '.cambc', 'build', 'bot-injected.wasm')


def build(bot):
    r = subprocess.run([CLI, 'build', bot], capture_output=True, text=True, env=ENV)
    if r.returncode != 0 or not os.path.exists(wasm_of(bot)):
        print(r.stdout[-3000:], r.stderr[-3000:], file=sys.stderr)
        sys.exit(f'build failed: {bot}')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()[:16]


def play(job):
    """One game; returns a small dict. Cached by content hash, so identical games are never replayed."""
    a, b, m, key, cache, outdir, keep = job
    cf = os.path.join(cache, key + '.json')
    if os.path.exists(cf) and not keep:
        try:
            return dict(json.load(open(cf)), cached=True)
        except ValueError:
            pass
    os.makedirs(outdir, exist_ok=True)
    stats = os.path.join(outdir, 'stats.json')
    r = subprocess.run([CLI, 'run', a, b, '--map', m, '-o', outdir, '--statistics', stats],
                       capture_output=True, text=True, env=ENV)
    if not os.path.exists(stats):
        return {'ok': False, 'log': (r.stdout + r.stderr)[-500:]}
    d = json.load(open(stats))
    res = {'ok': True, 'outcome': d['outcome'], 'round': d['round'],
           'gems': [t['submittedGems'] for t in d['teams']],
           'deaths': [sum(c['deaths'] for c in d['champions'] if c['team'] == t) for t in (0, 1)],
           'faults': d.get('botFaults')}
    for f in glob.glob(os.path.join(outdir, '*.repl26a')):
        if keep:
            try:
                with zipfile.ZipFile(f) as z:
                    for n in ('team-a.stdout', 'team-b.stdout'):
                        if n in z.namelist():
                            z.extract(n, outdir)
            except zipfile.BadZipFile:
                pass
        else:
            os.remove(f)
    if not keep:
        os.remove(stats)
        try:
            os.rmdir(outdir)
        except OSError:
            pass
    json.dump(res, open(cf, 'w'))
    return dict(res, cached=False)


def sign_p(k, n):
    """two-sided sign test"""
    if n == 0:
        return 1.0
    return min(1.0, sum(math.comb(n, i) for i in range(n + 1) if abs(i - n / 2) >= abs(k - n / 2)) / 2 ** n)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('cand'); p.add_argument('base')
    p.add_argument('--sets', default='official,gen,hold', help='comma list of: ' + ', '.join(SETS))
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    p.add_argument('--keep', action='store_true', help='keep replays and stdout logs in out/ab/')
    p.add_argument('--no-build', action='store_true')
    p.add_argument('--log', default='', help='also write per-map lines here (format read by sign.py)')
    A = p.parse_args()
    cand, base = A.cand.rstrip('/\\'), A.base.rstrip('/\\')
    t0 = time.time()
    if not A.no_build:
        with ThreadPoolExecutor(2) as ex:
            list(ex.map(build, [cand, base]))
    tb = time.time() - t0
    ver = subprocess.run([CLI, '--version'], capture_output=True, text=True, env=ENV).stdout.strip()
    hc, hb = sha(wasm_of(cand)), sha(wasm_of(base))
    if hc == hb:
        print('NOTE: the two bots compiled to the same wasm; every game will be a mirror.')
    cache = os.path.join('out', 'ab-cache'); os.makedirs(cache, exist_ok=True)
    tag = f"{os.path.basename(cand)}_vs_{os.path.basename(base)}"
    jobs, index = [], []
    for s in A.sets.split(','):
        maps = sorted(glob.glob(SETS.get(s, s)))
        if not maps:
            print(f'(set {s}: no maps found, skipped)'); continue
        for m in maps:
            hm = hashlib.sha256((sha(m) + ver).encode()).hexdigest()[:8]
            name = os.path.splitext(os.path.basename(m))[0]
            for side, (x, y, hx, hy) in (('A', (cand, base, hc, hb)), ('B', (base, cand, hb, hc))):
                jobs.append((x, y, m, f'{hx}_{hy}_{hm}', cache, os.path.join('out', 'ab', tag, s, f'{name}_{side}'), A.keep))
                index.append((s, name, side))
    t1 = time.time()
    with ThreadPoolExecutor(A.jobs) as ex:
        results = list(ex.map(play, jobs))
    tp = time.time() - t1
    played = sum(1 for r in results if r.get('ok') and not r['cached'])

    per = {}  # (set, map) -> {side: result}
    lines = []
    for (s, name, side), r in zip(index, results):
        per.setdefault((s, name), {})[side] = r
        if not r.get('ok'):
            print('FAIL', s, name, side, r.get('log', '').strip().splitlines()[-1:]); continue
        me = 0 if side == 'A' else 1
        won = r['outcome'] == ('teamA' if me == 0 else 'teamB')
        lost = r['outcome'] in ('teamA', 'teamB') and not won
        r['res'] = 'WIN' if won else 'LOSS' if lost else 'DRAW'
        r['me'], r['op'] = r['gems'][me], r['gems'][1 - me]
        lines.append(f"{name:24s} side={side} {r['res']:4s} r={r['round']:4d} gems {r['me']:4d}-{r['op']:4d}"
                     f"  deaths={r['deaths'][me]}  [{s}]")
    if A.log:
        open(A.log, 'w').write('\n'.join(lines) + '\n')

    print(f"\n{cand} (candidate) vs {base} (base)   built in {tb:.0f}s, {len(jobs)} games ({played} played, "
          f"{len(jobs) - played} from cache) in {tp:.0f}s\n")
    print(f"{'set':9s} {'maps':>4s} {'games':>9s} {'won both':>8s} {'lost both':>9s} {'split':>5s} {'same game':>9s}"
          f" {'net':>4s} {'p':>5s}  {'gems/100r cand-base':>19s}")
    tot_w = tot_l = 0; fresh_wl = {}
    for s in dict.fromkeys(k[0] for k in per):
        w = l = sp = same = gw = gl = 0; rate_c = rate_b = 0.0; n = 0
        for (s2, name), d in per.items():
            if s2 != s or len(d) < 2 or not all(x.get('ok') for x in d.values()):
                continue
            ra, rb = d['A'], d['B']
            n += 1
            gw += (ra['res'] == 'WIN') + (rb['res'] == 'WIN'); gl += (ra['res'] == 'LOSS') + (rb['res'] == 'LOSS')
            if ra['res'] == rb['res'] == 'WIN': w += 1
            elif ra['res'] == rb['res'] == 'LOSS': l += 1
            else: sp += 1
            # identical game: candidate played exactly like the base, the side decided
            if ra['round'] == rb['round'] and ra['gems'] == rb['gems'] and ra['outcome'] == rb['outcome']:
                same += 1
            rate_c += 50.0 * (ra['me'] / ra['round'] + rb['me'] / rb['round'])
            rate_b += 50.0 * (ra['op'] / ra['round'] + rb['op'] / rb['round'])
        tot_w += w; tot_l += l; fresh_wl[s] = (w, l)
        print(f"{s:9s} {n:4d} {gw:4d}-{gl:<4d} {w:8d} {l:9d} {sp:5d} {same:9d} {w - l:+4d} {sign_p(w, w + l):5.2f}"
              f"  {rate_c / max(1, n):8.1f} - {rate_b / max(1, n):<8.1f}")
    print(f"{'ALL':9s} {'':4s} {'':9s} {tot_w:8d} {tot_l:9d} {'':5s} {'':9s} {tot_w - tot_l:+4d} {sign_p(tot_w, tot_l + tot_w):5.2f}\n")
    # the verdict uses only fresh maps nobody tuned on (hold, dev) when they were played
    fresh = [s for s in fresh_wl if s in ('hold', 'dev')] or list(fresh_wl)
    tot_w = sum(fresh_wl[s][0] for s in fresh); tot_l = sum(fresh_wl[s][1] for s in fresh)
    n = tot_w + tot_l
    pv = sign_p(tot_w, n)
    print(f"Verdict on {'+'.join(fresh)} ({tot_w} won both sides, {tot_l} lost both):")
    if n == 0:
        print('  no decisive maps (every map split 1-1). The change does nothing measurable.')
    elif pv < 0.05:
        print(f"  {'CANDIDATE' if tot_w > tot_l else 'BASE'} is better (p={pv:.2f}).")
    else:
        # rough number of decisive maps needed to confirm the current rate (80% power, p<0.05)
        q = max(tot_w, tot_l) / n
        need = math.ceil(((1.96 * 0.5 + 0.84 * math.sqrt(q * (1 - q))) / (q - 0.5)) ** 2) if q > 0.5 else None
        if need is None or need > 1000:
            print(f"  no measurable difference (p={pv:.2f}, {tot_w}-{tot_l} on decisive maps). Treat it as a coin flip.")
        else:
            print(f"  not decided (p={pv:.2f}). It is {tot_w}-{tot_l} on decisive maps; if that rate is real you need "
                  f"about {need} decisive maps (you have {n}); add --sets dev or generate more fresh maps.")
    print("Reminder: maps_gen is a training set by now and maps_hold60 is the sealed check; "
          "a win that shows only on the set you tuned on is not a win.")


if __name__ == '__main__':
    main()
