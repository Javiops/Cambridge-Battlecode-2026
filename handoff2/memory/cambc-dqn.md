---
name: cambc-dqn
description: 2026-10-16 deep Q-learning + learned fight value (death risk) on the micro net hook: pipeline (tools/ga/dqn.py, fightval.py, PR #27), results (noise, I040/I041 rejected), death-rate gap vs top 2 (1.75x; ally within 4 halves theirs) handed to GA farm as pair genes; PPO (I042) also rejected 14:09, RL track closed; gems/turn PPO also noise, camp-value proposal pending
metadata:
  type: project
  modified: 2026-10-16T15:30:42.517Z
---

2026-10-16 thread "Deep Q-learning" (user: "try a deep-q-learning approach"). Branch claude/dqn-micro-suual7, draft PR #27,
ideas I040 (DQN) and I041 (learned death value), both rejected. Report /mnt/project-files/analysis/dqn-2026-10-16/README.md.
- Pipeline: dqn.h/dqn.patch put a 25-32-7 Q-net on the structure GA's NEAT hook ([[cambc-ga-structure]]), weights in
  `dq_g` (magic DQN1) byte-patched; bot logs `[dq]`/`[dt]` lines to team stdout (must fflush each line, every champion
  shares one stdout, NUL padding). 1,500 games = 373k decisions in 10 min; train ~20 s numpy; eval on v100 vs control.
- Results: free DQN = coward, 24-198; only when +3 gems over rules 51-39 p=0.25; round 2 48-45; death-risk threshold
  (top-2 model, p>30%) 50-38 p=0.24; cloned top-2 steps 37-40. Not gated, no migrant.
- Finding: same situations, we die 7.0% vs 4.0% (top 2) within 10 rounds; with an ally within 4 they halve it, we do not.
**How to apply:** do not rerun DQN rounds vs local rivals before 3 Nov; the hook/logging is reusable for online logs
(`fightval.py compare`); grouping (pairs) is the lead, as GA genes. Related: [[cambc-rl-assessment]] [[cambc-ga-farm]]

**Key finding:** in identical situations (same hp, same numbers) we die 1.75x as often as the top two within 10 rounds (7.0% vs 4.0%). With an ally within 4 tiles their death rate halves; ours does not change. "Stay in pairs" is the likely gap.

**Coordinator action 2026-10-16 12:55 UTC:** the ally-proximity death gap (we die 1.75x more than the top 2 in like situations; an ally within 4 tiles halves their deaths, not ours) was handed to the GA farm thread as proposed genes: pair-stick weight and distance, retreat toward nearest ally, do-not-engage-alone gate. Related: [[cambc-ga-farm]] [[cambc-ga-farm-threads]].

**PPO (I042, rejected, 2026-10-16 14:09; user "y si probamos un PPO"):** tools/ga/ppo.py, same net and decision point as the DQN (dqn.h mode 4 sampling, critic+GAE), stochastic policy starting at 81% rules; 15 rounds x 600 fresh games (9,000 games, ~65 min), reward adds 0.1 x team score margin. Learned more kite (4%->11%), more retreat (4%->9%), no engages, deaths 4.15->3.21 per game. On 100 unseen maps: sampled policy 58-95, greedy 51-67 (p=0.17), fewer deaths (1596 vs 1830) but fewer maps: same coward drift as DQN. ~10x the games of DQN; would need hundreds of rounds with an unvalidated reward. Not recommended before 3 Nov. Code in PR #27, README section at the end. RL track closed.
**PPO gems/turn reward 15:40 UTC (user: "goal should be gem efficiency"):** --reward gems (team gems per round, whole game): no learning (credit too diffuse), v100 sampled 38-175, greedy 51-47. Gems/turn fits farming decisions (camp choice, tribute/recall timing), not the fight step; proposed a learned camp-value. Policy worsened in training (rules 81%->45% of fight turns, win 45%->40%); greedy follows rules 99%. Camp-value proposal awaiting the user's yes/no, coordinator recommends yes.
