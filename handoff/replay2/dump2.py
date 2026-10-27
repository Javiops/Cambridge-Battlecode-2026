#!/usr/bin/env python3 -I
"""dump2.py: per-round replay rows for engine 2.0.0 replays (site since 2026-10-26, cambc 4.0.0).
Use it as a drop-in for capkind_light.dump:  sys.path.insert(0, DIR); from dump2 import dump, cheb
dump(path) accepts a raw .repl26a or a bundle zip (local run-batch bundle or site download). It returns a list of round
dicts (round, champions[], camps[], submittedGems...) or None. CLI: dump2.py REPLAY [--every-step] prints JSON lines."""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
JS = os.path.join(HERE, 'replaydump2.js'); WASM = os.path.join(HERE, 'v2_0_0-hWOQ1R8f.wasm')
def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
def dump(path, camps=True, every_step=False, timeout=300):
    args = ['node', JS, path] + (['--camps'] if camps else []) + (['--every-step'] if every_step else [])
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=dict(os.environ, CAMBC_VIS_WASM=WASM))
    rows = [json.loads(l) for l in p.stdout.splitlines() if l.startswith('{')]
    rows = [r for r in rows if 'champions' in r and not r.get('draft')]
    return rows or None
if __name__ == '__main__':
    for r in dump(sys.argv[1], every_step='--every-step' in sys.argv) or []: print(json.dumps(r))
