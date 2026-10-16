#!/usr/bin/env python3
"""Fuel-exhausted turns in CAMBC games: how many, for whom, on which maps and in which situations.

usage (from the repo root):
  python3 tools/fuelscan.py REPLAY_OR_BUNDLE...                    # scan existing replays (local .repl26a or online .zip)
  python3 tools/fuelscan.py --play bots/A bots/B --maps 'maps/*.map26a' [--fuel N] [--jobs 4]
                                                                    # play A vs B on each map, side A only, then scan

A champion turn that runs past its fuel budget ends with timeline step kind 26 instead of the normal end (kind 8);
whatever the bot had not done yet that turn is lost. "blank" = a kind-26 turn with no action before it (the champion
did nothing at all that round). "fight" = an enemy champion within 6 tiles at that moment, "early" = rounds 1-3
(the bot's init).
Plays with `--release` (debug_block skipped, as on the platform). Output: one line per game + totals per map;
--json FILE writes the raw numbers.
"""
import argparse, collections, glob, json, os, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP = os.path.join(ROOT, 'tools', 'replaydump.js')
CLI = os.environ.get('CAMBC_CLI', 'cambc')
ENV = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'}
ENV.setdefault('CAMBC_WASMTIME_CACHE', os.path.join(ROOT, 'out', 'wasmtime-cache'))
ACTIONS = {4, 5, 6, 11, 12, 13, 18, 20, 23}


def engines():
    """Engine wasms to try: the default (newest), then every visualiser wasm in the cambc cache (online replays of
    16 Oct still need v0_0_1 while local games use v0_0_2)."""
    found = sorted(glob.glob(os.path.expanduser('~/.cache/cambc/assets/*/visualiser/assets/*.wasm')))
    return [os.environ.get('CAMBC_VIS_WASM')] + [f for f in found if f != os.environ.get('CAMBC_VIS_WASM')]


def scan(path):
    """Counts per team index (0 = A) from one replay, trying each engine version until one decodes it."""
    for w in engines():
        r = scan_with(path, w)
        if r['rounds'] > 0:
            return r
    return r


def scan_with(path, wasm):
    """Counts per team index (0 = A) from one replay: turns, k26, blank, fight, rounds of k26 per champion."""
    env = dict(os.environ)
    if wasm:
        env['CAMBC_VIS_WASM'] = wasm
    p = subprocess.Popen(['node', DUMP, path, '--every-step'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env)
    team, typ = {}, {}
    out = {t: collections.Counter() for t in (0, 1)}
    per_ch = collections.Counter()
    acted = {}          # champion -> acted in its current turn
    pos = {}
    last_round = 0
    for line in p.stdout:
        if '"step"' not in line:
            continue
        d = json.loads(line)
        st = d['step']
        chs = d.get('champions') or []
        if chs and not team:
            team = {c['index']: c['team'] for c in chs}
            typ = {c['index']: c['typeName'] for c in chs}
        if st.get('actorKind') != 1 or st.get('phase') != 10:
            continue
        a, k = st.get('actorIndex'), st.get('kind')
        last_round = max(last_round, st.get('round', 0))
        if k in ACTIONS:
            acted[a] = True
            continue
        if k not in (8, 26):
            continue
        t = team.get(a, 0)
        out[t]['turns'] += 1
        if k == 26:
            me = next((c for c in chs if c['index'] == a), None)
            near = 99
            if me:
                for c in chs:
                    if c['team'] != t and c.get('alive') and c['x'] >= 0:
                        near = min(near, max(abs(c['x'] - me['x']), abs(c['y'] - me['y'])))
            out[t]['k26'] += 1
            if not acted.get(a):
                out[t]['blank'] += 1
            out[t]['fight' if near <= 6 else 'quiet'] += 1
            per_ch[(t, typ.get(a, str(a)))] += 1
            if st.get('round', 0) <= 3:
                out[t]['early'] += 1
        acted[a] = False
    p.wait()
    return {'rounds': last_round, 'teams': {t: dict(c) for t, c in out.items()},
            'per_champion': {f'{t}:{n}': v for (t, n), v in per_ch.items()}}



def play(job):
    a, b, m, fuel, od = job
    os.makedirs(od, exist_ok=True)
    cmd = [CLI, 'run', a, b, '--map', m, '-o', od, '--release']
    if fuel:
        cmd += ['--fuel', str(fuel)]
    subprocess.run(cmd, capture_output=True, env=ENV)
    reps = glob.glob(os.path.join(od, '*.repl26a'))
    if not reps:
        return m, None
    r = scan(reps[0])
    for f in reps:
        os.remove(f)
    return m, r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('replays', nargs='*')
    ap.add_argument('--play', nargs=2, metavar=('BOT_A', 'BOT_B'))
    ap.add_argument('--maps', default='maps/*.map26a')
    ap.add_argument('--fuel', type=int, default=0)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    ap.add_argument('--json', default='')
    a = ap.parse_args()
    res = []
    if a.play:
        for bot in a.play:
            subprocess.run([CLI, 'build', '--release', bot], capture_output=True, env=ENV)
        tmp = tempfile.mkdtemp(prefix='fuelscan_', dir=os.path.join(ROOT, 'out') if os.path.isdir(os.path.join(ROOT, 'out')) else None)
        jobs = [(a.play[0], a.play[1], m, a.fuel, os.path.join(tmp, os.path.basename(m))) for m in sorted(glob.glob(a.maps))]
        with ThreadPoolExecutor(a.jobs) as ex:
            for m, r in ex.map(play, jobs):
                if r:
                    res.append((os.path.splitext(os.path.basename(m))[0], r))
    else:
        with ThreadPoolExecutor(a.jobs) as ex:
            for path, r in zip(a.replays, ex.map(scan, a.replays)):
                res.append((os.path.basename(path), r))
    tot = {0: collections.Counter(), 1: collections.Counter()}
    print(f'{"game":<28} {"rounds":>6} | {"A k26":>6} {"blank":>5} {"fight":>5} {"early":>5} | {"B k26":>6} {"blank":>5} {"fight":>5}')
    for name, r in res:
        A, B = r['teams'].get(0, {}), r['teams'].get(1, {})
        for t, c in ((0, A), (1, B)):
            tot[t].update(c)
        print(f'{name[:28]:<28} {r["rounds"]:>6} | {A.get("k26", 0):>6} {A.get("blank", 0):>5} {A.get("fight", 0):>5} {A.get("early", 0):>5} |'
              f' {B.get("k26", 0):>6} {B.get("blank", 0):>5} {B.get("fight", 0):>5}')
    n = max(1, len(res))
    for t in (0, 1):
        c = tot[t]
        print(f'team {"AB"[t]}: {c["k26"] / n:.1f} fuel-exhausted turns/game ({c["blank"] / n:.1f} blank, {c["fight"] / n:.1f} near an enemy,'
              f' {c["early"] / n:.1f} in rounds 1-3), {100.0 * c["k26"] / max(1, c["turns"]):.2f}% of {c["turns"] / n:.0f} turns/game')
    if a.json:
        json.dump(res, open(a.json, 'w'), indent=1)


if __name__ == '__main__':
    main()
