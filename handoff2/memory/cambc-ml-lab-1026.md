---
name: cambc-ml-lab-1026
description: "10-26 ML session (lab\\ml): CMA-ES phase 1, top-5 behaviour cloning (rT5), ES fight net; dec2/replay facts learned while matching bot features to replays"
metadata:
  node_type: memory
  type: project
  originSessionId: 0b6ed838-649a-4d45-b861-23354f86921a
  modified: 2026-10-27T09:06:12.045Z
---

USER 2026-10-26 ~15:45 Madrid: "manda un hilo de un bot con un plan detallado, no voy a iterar sobre el plan... tiene que gamblear a que ML funcione". ML session lives in `C:\Users\Javier\Cambc2026\lab\ml\` (INFORME.md = log; PITCH_UPV.md = compute request for the UPV professor). UPV specs unknown (user: "asume un buen escenario con cómputo decente"); everything portable to Linux (setup_linux.sh, env ML_CLI/ML_MAPS/ML_JOBS/ML_SLOTS).

**Infra:** runner.py (sqlite db\games.sqlite, key = bot hash, rival hash, map, side; deterministic so each game once), build.py (params.h rewrite + ml_gen.h; slots work\slot_<ML_SLOTS>_k; each concurrent process needs its own ML_SLOTS), space.py (105 continuous + 87 categorical incl. per-champion shop plans and draft scores), es.py (sep-CMA + categorical ASNG), es_net.py (OpenAI-ES on policy weights), mkpol.py/cpp\pol.h (base mlpol: learned fight policy when a rival is visible within 8). Default vector = co_v7 exactly with unlimited fuel (P_CHASE_GEMS is 144, not 60: P_E1C=0).

**Replay / engine facts found 10-26 (dec2 format):**
- Bot round N starts from record R[N-1]; step kinds and cc of round N are keyed N; R[N] = after round N.
- Within a round champions act in index order: allies with a lower index have already moved (their R[N] tile) when one plays.
- Step kind 11 = recall start, but Mite and willow best girl send it in ~90% of fight turns and cancel; a real recall = kind 11 + home jump within 7 rounds (top 5 ~2% of fight turns, ours 0.5%).
- A bot cannot read allies outside its vision (vis_champions(ally) and sdk_champion on far allies fail); features use allies within 8 only.
- Fuel: a C++ dot product loop is ~10 fuel/iteration; the 140->64->48 MLP cost ~130k scalar, 24k with simd128 + folded embeddings; features with raw sdk_champion + sdk_champion_cooldown ~8k.

**Phase 1 result gen 0 (p1, 16:10-17:15):** median candidate 0.41 vs default 0.57 (420 games each): shop/draft mutations too disruptive → restarted as p1b with pdef 0.95 and draft std x0.4.
**p1c gen 0 (20:17) + validation 20:48 (poolval.py, 840 pool games paired with co_v7):** mean vector +0.055 ± 0.023 (wins 62.5% vs 57.6%; vs kvvl 0.65 vs 0.53, vs co_v7 0.49); on the half not used for selection ≈ +0.045. First real local gain of the ML line; online unknown (local pool is our code family). NOT packed: only export\ml_q1d10.zip exists (Q model, 71/140 vs E1, not worth sending); pack with `mkzip.py NAME WASM_HASH TAG`.
**USER 26-10 ~20:45 "stop the jobs":** coordinator killed p1c, n2, the loop queue/fetcher and the ml_t5vs download; loop and ML relaunched thinking it was a crash, then stopped again on the user's order (confirmed ~21:00). State resumable (runs\p1c\state.pkl, gen_000.json). Do not relaunch without the user. Top 5 at 20:52: Intercontinental Fish, Mite, Trzy Kwaterki, willow best girl, Claudus Maximus (prism best girl out).
**USER 27-10: compute granted:** a "CMTS" cluster with A100 GPUs plus another of 10 machines with V100 GPUs (core counts, scheduler, access method unknown at the time). Our workload is CPU-bound (each game = one cambc/wasm process; PC 16 cores, 14 procs ≈ 2.3 games/s ≈ 0.16 games/s per core), so the value is the nodes' CPU cores; GPU only speeds model training (imitation/Q, which did not transfer). No SSH connection saved in the app on 27-10; `setup_linux.sh` + `PITCH_UPV.md` are the port.
**27-10 proposals awaiting the user's yes (HANDOFF section 11):** (1) cluster plan: CMA-ES runs per V100 machine + net ES on A100, best to t5b every 2-3 h via the loop; (2) big-network test: much more top-10 data, 10-100x net on A100, play it locally with UNLIMITED fuel vs E1; wins → distil + int8 to fit fuel (MLP 140→64→48 = 24k of ~100k/turn); loses → size was not the problem (hidden info + compounding error), imitation only as a start. USER asked "why not just put the weights in and mega-optimize": answer = weights already in (cpp/pol.h), fuel caps size 2-4x, accuracy rose 37→46% from new inputs, not size.
Related: [[cambc-plan-c97-1025]] [[cambc-vesper-step-reset-1026]] [[cambc-patch-2-0-0-1026]]
