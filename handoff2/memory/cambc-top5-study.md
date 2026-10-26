---
name: cambc-top5-study
description: Top-5 replay study (2026-10-13): where the 45 decoded top games and analyst reports live, the 8 top-team habits coded as switches (patch_study.py) and their arena results; state handed off at 18:00 UTC
metadata:
  type: project
  modified: 2026-10-13T18:05:00.000Z
---

Started 16:15 UTC 2026-10-13 when the user asked to "study the best players' matches rather than
construct our own bot from scratch". Full handoff: `/mnt/project-files/handoff/estado-2026-10-13.md`.

Data under /mnt/project-files/analysis/: `top5_study_bundle/<map>/<id>.txt` (45 top games: profile,
stats, routes) and `ours/` (18 v3td ladder games); `top5_study_compact/` (decoded replays, event
stream); `top5_study_results/` (analyst JSON: 8 maps + cross_farming, cross_shopping, cross_kills;
interlock missing, prompt in `prompts/`). Synthesis `analysis/top5-study.md` not written yet.
Tools: `arena/tools/ghost/` (studyrep.py, bookgen.py, k26.py...), `arena/tools/micro/fights.py`.

First finding: the fuel overrun, see [[cambc-fuel-budget]]. Then `arena/tools/study/patch_study.py`
adds 8 switches to main_lean.cpp (P_ONE_CAP, P_SHOP_PLAN, P_SHOP_RECALL 180, P_SAFE_RECALL,
P_OWN_ALTAR 20, P_RESPAWN 4, P_CHAIN 36, P_HALF 30). All on = `bot/mybot_study.zip`: 16-2 vs v3td,
208 vs 120 gems per 100 rounds, 12-6 vs lean, 34 deaths vs hunter2 (lean 73), 6-0 vs ghosts with
11 deaths. Alone: P_SAFE_RECALL (33 hunter deaths) and P_SHOP_RECALL (16-2) help most; P_SHOP_PLAN
alone hurts (3-15 vs lean). Leave-one-out ablation and the fight rules (engage check, focus, ally
duty, no walking away from melee) are still to do. The opening-book bot (patch_book) was 7-11.

**Why:** copying the winners' recorded play is the user's chosen approach.
**How to apply:** build on main_study/main_lean, test every change with stbatch.sh (vs v3td,
lean, hunter2, ghosts) and k26.py, and get online results before replacing mybot.zip.
