---
name: cambc-dev-speed
description: 2026-10-16 measured cost of local games and where development speed can still be gained (online uptime/informative pairings, GA racing, more workers); early stop and --release rejected
metadata:
  type: project
  modified: 2026-10-16T11:31:46.462Z
---

2026-10-16 11:35 UTC thread "mejorar tiempos" (report /mnt/project-files/analysis/dev-speed-2026-10-16/README.md):
- A game costs 0.43 CPU-s (0.73 ms/round, engine-bound: starter-cpp costs the same); 4-core cloud thread = ~9 games/s = ~32k/hour; --jobs 4 is optimal. Gate (1120 games) ~2 min; GA already at the hardware limit.
- Rejected: early stop (leader at round 500 is right only 100/120; lead>=200 rule saves 10%; `--rounds` writes no stats), `--release` (same speed, games identical, now builds), more jobs.
- Online: 50% of repeated (opp,map,side) unranked games never changed result -> pick flippable maps/rivals for ~2x info per hour.
- cambc 2.2.1 has `cambc match-groups create <team> --maps ...`, `quota`, `download`, `ladder`, `matches` with the 7-day CLI login: can replace the browser cookie in the online loop (not yet tried; needs the user's OK for `cambc login`).
**How to apply:** speed ideas go to online uptime, informative pairings, GA racing and extra workers, not engine tricks. Related: [[cambc-ab-tool]] [[cambc-online-loop]] [[cambc-ga-micro]]
**User PC (11:45 UTC):** i5-14400F 10C/16T, 15.8 GB, Windows; same kit = 27 games/s at 12 jobs (15.1@4, 23.2@8, 26.7@16) = 3x a cloud thread. cambc 2.1.6 there (cloud 2.2.1); `python` is the Store alias, use `py`. Kit: C:\Users\Javier\Cambc2026\pc-bench (bench_pc.py).
PC island readiness: Python 3.14 via `py`; cambc toolchain in %LOCALAPPDATA%\cambc (cmake, ninja, wasi-sdk-33); git 2.54 reaches the repo without login; CAMBC_WASMTIME_CACHE works on Windows; 145 GB free. Only gap: upgrade cambc 2.1.6 -> 2.2.1.
2026-10-18 17:35 UTC user tip: testing without replays is much faster. Checked: next\lab (lab/core.py run_game) calls `cambc run ... -o <tempdir> --statistics --json --release --log-limit 0`, replay goes to a temp dir and is discarded, results cached as JSON. cambc 2.2.1 `run` has NO flag to skip writing the replay (-o only picks the dir); `cambc run-batch --jobs N` (manifest: bot-a bot-b map replay [--statistics]) runs many games without one cambc launch per game, untested. Measure on the PC before claiming a gain.
17:40 UTC MEASURED (cloud 4 cores, bank-v1b-clean self-play, 34 games; PC by the rival thread, 50 games): replay bundle 82 KB/game, RAM disk vs disk identical (5.9 games/s cloud), no statistics / binary / JSON stats identical, logs off no gain; no compile cache 3-4x slower; run-batch slower on PC (11-14 vs 16-20 games/s at 16 jobs) and needs project dirs, not frozen wasm. next\lab (per-game run + .cambc/wasmtime-cache) is already the fastest setup; remaining lever = fewer games per test (sequential stop), not faster games. Bench script: audit scratchpad speed/bench.py.
