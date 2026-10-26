---
name: cambc-carson-method
description: 2026-10-17 user decision to scrap switch-testing and rebuild following CarsonBurke (top 3); study report link, his method, the 4-phase plan to 4 Nov
metadata:
  type: project
  modified: 2026-10-17T20:04:47.094Z
---

2026-10-17 19:55 UTC the user called the day a failure ("A/B testing and throwing what sticks") and decided to scratch the current approach and learn to build properly from CarsonBurke's public work until 4 Nov (memory said 3 Nov; the plan freezes 2 Nov).
Report: https://claude.ai/artifact/SKkU5fL6fSPxZCaWxMGCje (thread "CarsonBurke study").
His public sources: CarsonBurke/kaggriculture (~10th of 10,246 on Kaggle; screening then finalist gates on unseen seeds, held-out opponents, hardest-opponent league, strategy collapse caught too late), CarsonBurke/cb-bc (spring Cambridge bot: day 1 = rules notes, maps, TrueSkill round robin ablations/elo.py over all versions both sides, stats every 100 rounds, dashboard, LLM ablation overseer; then PPO RL, 5 weeks on an RTX 5090, postmortem PDF), orbit-wars (configs as truth, symmetry tests, frozen validation panel), The International Screeps bot DESIGN.md (Utils/Procs/Services/Data/Tasks), screeps-rl DECISIONS.md. His autumn CAMBC 2026a bot is not public.
**Why:** he also ablates heavily; the difference is a small layered code base, a non-saturating metric plus diagnostic snapshots, a pool rating with a frozen panel, and written decisions.
**How to apply:** no new P_* switches on v53/team_baseline (frozen as opponent and online fallback). New bot bots/next: sense -> plan -> act -> log layers, strategy as data. Phases: 0 instruments (league.py, farmbench vs dummy, snapshots, skeleton) 17-19 Oct; 1 economy 20-23; 2 survival/fights 24-28 with online batch; 3 team play 29 Oct-1 Nov; 4 freeze 2 Nov. No RL. Related: [[cambc-flexible-architecture]] [[cambc-v53]] [[cambc-harness]].
