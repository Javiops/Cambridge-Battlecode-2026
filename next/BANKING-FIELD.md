# Paired banking field benchmark, 21 October

**Platform v87 / ppo-topdraft-v12 is compiled and live.** V86 / topdraft v8 and
v85 / topdraft v7 remain available. V83 / qualified league v12 is preserved.
The temporary teammate hold was honored through 23:10:20 UTC. Read-only checks
showed their batch complete, and v85 had already been selected by another session.
This agent initiated only unranked games after the hold, with short upload notes.

All three versions play the same pinned Preyas submission and five maps in both
seats. Preyas was observed at #118 / 1,696 Elo, our team #128 / 1,683. Every queued
and completed version is verified. All 30 official replays/statistics independently
match terminal winner/round/banks and champion gold, collection, deposits, kills
and deaths through official rules 1.0.1 and the pinned build.

| Platform / source | Wins | Faults / fuel losses | Big-world bank A/B | Elk-arena bank A/B |
|---|---:|---:|---:|---:|
| v85 / topdraft v7 | 5/10 | 0 / 0 | 202 / 90 | 0 / 432 |
| v86 / topdraft v8 | 5/10 | 0 / 0 | 381 / 336 | 0 / 72 |
| v87 / topdraft v12 | 5/10 | 0 / 0 | 381 / 336 | 72 / 72 |

Completing small existing banking trips improves the targeted big-world economy,
but does not improve this benchmark's win count. Collection rises from 237/114
to 385/396 between v85 and v86; deaths rise from 10/0 to 13/13. Movement permits
more acquisition and also more exposure. Elk-arena B regresses from 612 collected
and 432 banked to 108 collected and 72 banked, with deaths 16 to 17. Diagnose that
acquisition/control tradeoff; it is not solely a deposit-conversion problem.
V87 eliminates zero-bank games in this small pair but still loses both elk seats.

Mean banks are 663.2, 674.6 and 668.8 across the three versions; v87's opponent
mean bank is 742.8 versus 812.1/824.4 in the previous pairs. One frozen opponent,
five maps and deterministic games are limited evidence. No overall strength
improvement, independent PPO gain or lab promotion is claimed. The weights and
historical Stage 1–7 certificates stay unchanged, and no new holdouts were used.

The v86 and v87 source ZIPs downloaded from the server exactly match their frozen
uploads. Independent local release rebuilds match the frozen WASM. Live status
and completed official games verify server compilation; no server binary hash is
claimed. See the deployment JSONs and CONTACT-V12.md for offline checks.

Next use the remaining actual allowance with v87 across broader maps and several
nearby/stretch opponents, with at most 10% leader scouting. Keep the benchmarking
tradeoffs visible, especially acquisition and deaths at the sole objective. An
unranked Crimson Pathfinders group and automatic ranked matches were observed
separately and are excluded; they were not initiated by this agent.
