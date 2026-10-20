# Patch 1.0.1 rollout: ppo-league-v12

The unchanged qualified source compiles under official CLI 3.0.2 and produces the
same WASM bytes as the Stage 7 artifact. It was uploaded to Live Love Larp as
Battlecode version 83; downloading that server-stored source ZIP reproduces the
qualified source ZIP hash exactly.

## Official hotfix

[Patch 1.0.1 notes](https://2026a.battlecode.co.uk/game/patch-notes/7a4caf45-afc3-49d0-838a-9eb9657bafc6)
reduce Heart of Ruin's per-shard strength bonus from 5 to 4 and focus bonus from
15 to 12. A patch-invalidated submission now has a 24-hour grace period before
ranked automatic losses. 

The official 3.0.2 C++ SDK files match the pinned 3.0.1 C++ SDK byte for byte.
The controller reads current champion statistics through the SDK. No source,
draft, PPO weights or critic were changed for this check. The release runner
reports engine version 1.0.1 and build `c3e9ffc8d98c106f86660c58344dc26ced9459a504e2f0d90d88b4c8594c7765`.
Earlier Stage 1–7 certificates remain records of their pinned 1.0.0 experiment;
this separate compatibility result does not relabel those old games as 1.0.1.

## Local compatibility results

| Cohort | Wins | Bot faults | Fuel-exhausted turns |
|---|---:|---:|---:|
| All 35 current site maps, both seats | 68/70 | 0 | 17 |
| Repeat of v12's locked 70-map schedule, both seats | 140/140 | 0 | 0 |

The existing numeric criterion (at least 90% versus starter, zero faults and at
most one fuel-exhausted turn per game) passes on each cohort. The previously used
locked maps are a compatibility repeat, not another independent strength test.
No model or strategy was tuned on these results.

Both losses are on `01big-world`: 119 and 101 banked gems, with seven and eight
fuel-exhausted turns. Two additional fuel-exhausted turns occur in a win on
`00ambush`. The largest-map planning cost remains a known weakness.

## Upload and live-test identity

- Team: Live Love Larp (`292625c5-0f3a-49f0-a08a-9757b8f58658`).
- Platform version: **83** (`db9366e1-f5a9-4398-a5a9-87739cd660aa`).
- Note: `ppo-league-v12 | expert/PPO | checkpoint 012 | Patch 1.0.1 checked`.
- Uploaded source ZIP SHA256: `04abd46d87905fff8223555961b88bc20facdba8ea265b5861879a530f6d7af1`.
- Qualified/current-patch WASM SHA256: `7cdeca594e68bc9e5aeaa2a19116fd7eb990ffdafa9c911a7dbd69bcd5866bcc`.
- Current recorded status: **v83 selection cancelled; the live bot changed to v81 and then v82**.
- Server compilation verified: **False**.
- Completed valid v12 sparring games: **0**.

The first requested unranked group
[against Intercontinental Fish](https://2026a.battlecode.co.uk/game/match-groups/005481ca-51a0-4e36-8542-cce33160738c)
ran platform **v81**, after v83's selection was cancelled and the live bot reverted.
Its 0/5 result is excluded from PPO results. The source upload succeeded, but
upload success alone does not establish that a match ran the requested bot.

Only two unranked groups remained when setup began; one was used by that excluded
group. The remaining group is held pending coordination of the live selection.
No further selection changes are made while another team member may be changing it.

## Evidence and reproduction

The accompanying validation ZIP includes every local release statistic/replay,
all map bytes used, the current-patch build logs, exact uploaded source, upload
and version-mismatch observations, and a SHA256 manifest. The official CLI wheel
is identified by hash, rather than copied into the evidence package.

In a separate project, install `cambc==3.0.2`, run `cambc init --yes .`, restore
the qualified source ZIP under `bots/ppo-league-v12`, and run
`cambc build --release bots/ppo-league-v12`. The compatibility runner is included
for the recorded workspace layout and imports the original unchanged statistics
validator. Source and model artifacts from Stage 7 remain unchanged.
