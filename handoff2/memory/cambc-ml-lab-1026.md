---
name: cambc-ml-lab-1026
description: "10-26 ML session (lab\\ml): CMA-ES phase 1, top-5 behaviour cloning (rT5), ES fight net; dec2/replay facts learned while matching bot features to replays"
metadata:
  node_type: memory
  type: project
  originSessionId: 0b6ed838-649a-4d45-b861-23354f86921a
  modified: 2026-10-26T16:29:26.076Z
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
Related: [[cambc-plan-c97-1025]] [[cambc-vesper-step-reset-1026]] [[cambc-patch-2-0-0-1026]]
