# Stage 7 competitive qualification

This page records the qualification milestone before the hotfix and upload.
See [HOTFIX-1.0.1.md](HOTFIX-1.0.1.md) for later release status.

`ppo-league-v12` passes the unchanged promotion gate against `starter-week2-v1`:
140/140 wins (100.00%) on 70 fresh generated maps,
both seats. The source ZIP independently rebuilds to the qualified WASM.
The bot is eligible for promotion and review; no live upload or champion change was made.

## What improved

The original Stage 6 C++ PPO actor wins 0/200 screening games and banks 3.67 gems
per game. Incremental fixes to its compact controller improve economy but remain
too weak. The accepted version combines the team's existing v76 expert strategic
controller with the unchanged trained PPO actor for bounded attack-target choices.
It adds cooperative fuel budgeting and a cheap camp-planning fallback.

This is an expert/PPO hybrid. Farming, purchases, healing, spell use, draft,
banking and team camp claims come from the expert controller. The 305 float32
PPO weights and certified inference kernel are unchanged. No additional PPO
training or critic inference is performed in Stage 7.

The adapter samples at temperature 1 among safe eligible attack targets, at most
once per champion round when sufficient fuel remains. Neutral choices preserve
the original camp kind or select harmless gem/gold clusters; enemy choices preserve
a guaranteed finishing target. Movement candidates are omitted from this attack-only
inference call. The adapter uses a private map/unit-seeded RNG per champion, avoiding
the expert controller's shared camp-claim memory. This deliberately changes the full
Stage 6 controller and sampling stream; Stage 6's full-controller parity claim is
not extended to the hybrid.

Six full release canaries record 215 actual multi-target PPO calls
and 104 targets changed from the expert proposal. The actor is active.
However, the matched `ppo-disabled-v3` controller also wins all 200 screening games.
The measured win-rate difference is zero, with whole-map bootstrap interval [0, 0]
on this saturated sample. That provides no evidence of an independent PPO strength
gain. The competitive improvement is attributed to the strategic controller.

## Acceptance evidence

All matches use the pinned October 20 CAMBC 3.0.1 SDK and official release engine,
with default fuel limits. Every comparison includes both seats.

| Check | Result |
|---|---:|
| Starter screening: 100 generated maps | 200/200 wins |
| Known site stress maps: six maps | 12/12 wins |
| Candidate against the full five-bot screening panel | 1,000/1,000 wins |
| Full-panel candidate faults / fuel-exhausted turns | 0 / 2 across 1,000 games |
| Fresh confirmation: 70 generated maps | 140/140 wins (100.00%) |
| Confirmation side A / side B | 100.00% / 100.00% |
| Required starter score | at least 90% |
| Candidate / opponent faults in confirmation | 0 / 0 |
| Confirmation fuel-exhausted turns | 0 total; 0.0000/game |
| Allowed fuel-exhausted turns | at most 1.0/game |
| Archived promotion matches | 140 |
| Official ordinary / initial fuel maxima | 92,815 / 183,945 |
| Judge regression tests | 122 passed |
| Source ZIP rebuild | identical WASM bytes |

The gate's champion and weak opponent are both starter. The unchanged judge counts
that opponent once at the stricter 90% threshold. Screening/stress results contain
zero candidate faults or fuel-exhausted turns. The broader league reports its own
runtime metrics in `results/STAGE7-LEAGUE-QUALIFIED.md`; the seed-control noise gap
is 16 rating points and 50% head-to-head over 200 games. Use win counts and the
promotion verdict as the acceptance evidence, rather than extrapolating the
regularized Elo estimate beyond this weak reference panel.

Official fuel attachments cover entire turns, including logging and `end_turn`.
The table reports observed stream maxima, not a claim that every possible turn
has headroom. Handled SDK action rejections are distinct from official bot faults.
Every captured confirmation replay reproduces the gated outcome, round count
and both teams' statistics exactly.

## Development and fuel fixes

The first twelve maps of the screening pool supply the paired development schedule.
The table preserves unsuccessful trials as well as the accepted source lineage.

| Version | Development wins | Bot faults | Fuel-exhausted turns | Mean banked gems |
|---|---:|---:|---:|---:|
| v1 | 3/24 | 22 | 126 | 162.7 |
| v2 | 2/24 | 0 | 0 | 112.9 |
| v3 | 0/24 | 0 | 0 | 114.7 |
| v4 | 4/24 | 0 | 0 | 177.5 |
| v5 | 5/24 | 0 | 1 | 169.6 |
| v6 | 24/24 | 0 | 3 | 997.1 |
| v7 | 24/24 | 0 | 5 | 1004.5 |
| v8 | 24/24 | 0 | 0 | 994.4 |
| v9 | 24/24 | 0 | 0 | 989.6 |
| v10 | 24/24 | 0 | 0 | 979.2 |
| v11 | 24/24 | 0 | 0 | 991.1 |
| v12 | 24/24 | 0 | 0 | 992.4 |

V1-v5 improve the original compact controller: camp lifecycle, bounded planning,
available attacks, shopping/survival and persistent farm intent. V6 imports the
stronger expert strategic controller. V7 lowers the adapter's fuel threshold;
its intended wider mask did not land until v8. V8 broadens safe neutral targets.
V9 rejects single-target inference cheaply and raises the reserve. V10 adds
cooperative planning-budget checkpoints. V11 adds a cheap safe camp choice when
full planning cannot fit. V12 keeps the budget exception out of line so fresh
source builds are reproducible. Archived source and `params.h` define each trial;
older JSON config snapshots can retain unused settings or the then-current
default candidate name and are not a substitute for those frozen sources.

The large-map stress failures exposed two separate problems: expensive loops lost
turns to fuel, and requiring the full planning cost could leave heroes waiting
indefinitely. Checkpoints defer optional planning before the engine fuel trap;
budget exceptions propagate through the controller's catches. The bounded fallback
selects a reachable, unclaimed resource group using partial available information.

## Confirmation integrity and source packaging

V11 passed the original 70-map promotion cohort, 137/140 wins, zero faults and
17 fuel-exhausted turns. Its independent source build differed by 186 code-section
bytes in compiler-generated exception wrappers, so it failed packaging acceptance.
That result remains in `results/stage7-v11-*`; it is not the qualified artifact.

V12 adds only `noinline` to the cooperative budget checkpoint. Its source bundle
was verified before confirmation. The consumed original cohort was retired,
with its attempt lock retained. A predeclared, outcome-independent g1 replacement
pool uses seed 2026103001 and the same map generator. All 70 maps were generated
and hashed before any v12 confirmation game. Their bytes are disjoint from the
retired and screening pools. Gate thresholds were not changed.

The r2 attempt lock binds candidate WASM, map hashes, opponent, gate settings and
runtime. It permits an identical resumed run and rejects another candidate or
renamed consumed map bytes. The final candidate was frozen before this cohort
was used. Both confirmation cohorts are now consumed: further strategic tuning
requires a new independent pool.

| Artifact | SHA256 |
|---|---|
| Qualified `ppo-league-v12` WASM | `7cdeca594e68bc9e5aeaa2a19116fd7eb990ffdafa9c911a7dbd69bcd5866bcc` |
| Unchanged checkpoint 012 weights | `94c1399f470e7c64f65a203a46d4bd14dff4527057d6eb12fc26fffb79b5402f` |
| Verified submission source ZIP | `04abd46d87905fff8223555961b88bc20facdba8ea265b5861879a530f6d7af1` |

## Reproduction and handoff

Restore the prior stages' frozen versions/models and the Stage 7 validation
package, including the replay directories and maps. Follow STAGE1.md for the
pinned CLI, SDK and official rules WASM. From `next/`, run:

```bash
python -m pytest -q tests
python -m lab stage7 maps
python -m lab stage7 bundle
python -m lab stage7 screen
python -m lab stage7 canary
python -m lab stage7 gate
python -m lab stage7 ready
```

These commands verify the same frozen bytes and cached schedule. They do not
authorize choosing another candidate on the consumed confirmation maps. The
validation package includes the frozen source lineage, matched actor-disabled
control, model checkpoint, per-game records, all confirmation replays/statistics,
and file hashes. `stage7 ready` verifies current sources, complete proof hashes
and a new exact source-bundle rebuild. Earlier source-bound stage certificates
are refreshed without retraining their frozen models.

The bundle is `results/bundles/ppo-league-v12.zip`. Upload and activation remain the
next explicit team decision. Beating starter does not establish strength against
the live ladder's stronger teams; the present evidence supports the stated gate.
