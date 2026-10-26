---
name: cambc-ab-tool
description: The standard fast A/B command (tools/ab.py) and the wasmtime compile cache that makes local games 4x cheaper; measured 2026-10-15
metadata:
  type: project
  modified: 2026-10-15T10:50:12.852Z
---

2026-10-15: `python3 tools/ab.py bots/CAND bots/BASE [--sets official,gen,hold,dev]` (team repo PR #2, copy in
/mnt/project-files/arena/tools/ab.py) is the standard way to measure a candidate. Use it instead of ad-hoc scripts.
- `CAMBC_WASMTIME_CACHE=/abs/dir` (an undocumented env var in the cambc binary) caches the compiled bots. Without it, each game spends
  ~1.5 of ~2.2 CPU-s compiling. With it: 226 games (official+gen+hold60) 141 s -> 35 s on 4 cores; 626 games with dev200 ~100 s.
  Stats are byte-identical. arena.py sets it too.
- Results are cached in out/ab-cache by (wasm A hash, wasm B hash, map+cli version). The tool scores maps won/lost on both sides and flags
  identical games (same round+gems both sides). The verdict uses only hold+dev.
- New set maps_dev200 (genmaps seed 4242; /mnt/project-files/arena/maps/dev200). mkmap.js now finds the editor wasm for any cambc version.
- Checks: study25 vs v30 = dev 88-34, hold 19-12 (study25 is better). A tiny change (P_RECALL_PCT 57) = gen 1-8 (p 0.04, false alarm)
  but 18-19 on hold+dev.
- Build ~15 s per bot single-threaded (one big main.cpp, -O3). ab.py builds both bots in parallel.
Related: [[cambc-eval-method]] [[cambc-arena-setup]]
