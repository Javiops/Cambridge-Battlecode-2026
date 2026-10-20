# Stage 4: outcome critic acceptance passed

`outcome-v5` passes `python -m lab stage4 ready` against the pinned October 20
CAMBC 3.0.1 release runtime. Both predictive and pipeline checks pass.
Stage 5 is eligible to begin; PPO has not started.

## Result and unchanged gate

The criterion remains strict improvement in **both Brier score and log loss** over
**both** constant P(win)=0.5 and an independently selected score/time/seat baseline.
The critic was frozen before 24 release games on eight new family-3 maps were played.
SDK starter/seed pairings run both seats, plus starter mirrors on every map. These maps
and SDK policy lineage are absent from critic fitting. All 24 completed with zero faults
and fuel exhaustion. Evaluation contains 46,455 sampled states, weighted equally per
game, then per team, then per state; these states are not independent outcome trials.

| Predictor | Brier (lower better) | Log loss (lower better) | Accuracy |
|---|---:|---:|---:|
| Constant P(win)=0.5 | 0.250000 | 0.693147 | 50.00% |
| Score/time/seat baseline | 0.130671 | 0.400749 | 86.89% |
| Inventory-aware critic | 0.125076 | 0.386293 | 87.04% |

| Phase | Baseline Brier | Critic Brier |
|---|---:|---:|
| early | 0.202871 | 0.198138 |
| middle | 0.109372 | 0.102051 |
| late | 0.072381 | 0.068208 |

Early/middle/late mean rounds 1-666, 667-1333 and 1334-2000. Full calibration and
phase metrics are in `models/outcome-v5/evaluation.json`.
The paired whole-map Brier difference (critic minus baseline) is
-0.005595; its 90% bootstrap interval is
[-0.009628, -0.001345] over 2,000 map resamples retaining every seat/pairing.
The interval supports improvement on this cohort. Eight independent maps remain a small sample.

## What changed

The actor's certified 305 float32 weights remain byte-identical, SHA256
`76ec1dcaf4d37f1cccaccd483885e241a7f14cf929630332ece35e72e5988d3e`. Its local encoder and hidden activations remain frozen.
The training-only critic adds **current** whole-team state and equipment inventories,
queried from the official native engine using each champion's authenticated viewpoint.
Privileged enemy information is never added to actor observations or its runtime.

The 74-feature state retains the original 44 local features, adds 24 perspective-signed
team features (carried gems, wallet gold, alive/health fractions, strength/focus and
altar/channel proximity, plus time and signed-log transforms), and six inventory features.
The latter are team differences in paid equipment value and wallet-plus-equipment,
with time and signed-log transforms. Shards cost 30 and fused emblems represent 150;
42 inventory counters cover every family/stat. Native tests verify five-shard fusion,
conservation of wallet-plus-equipment under buying, and actor privacy. Net worth is an
income proxy, **not** the exact lifetime-gold tiebreak: consumables and other spending
can break the equality.

The selected `team_banks_wealth` head has 46 trained parameters
including the five-parameter score/time baseline and temperature. It uses monotone
nonnegative team/economy advantages and banking curves, with signed economic features
attenuated when bank margins are large. Its selected inputs do not use the frozen BC
hidden activations; they remain available in the state representation. This result
therefore supports the centralized critic features, not a claimed benefit from BC embeddings.
The separate actor remains the Stage 3 starting policy. No critic cost enters C++ turns.

The target is binary completed-game outcome: P(win), with V=2*P(win)-1 and no
micro-action discount. A nonterminal value of zero means uncertainty. Completed ties
resolve under the game's team-B rule; unfinished/faulted games never become draw labels.

## Training and frozen evaluation

Training contains 51 clean games on 40 maps from families 0/1/2,
with 74,491 first-decision states sampled every ten rounds, both teams included.
It extends the Stage 2/v2 training sources with v76 mirrors; six whole fuel-limited
training games across these collections are quarantined. External online sparring
replays remain excluded. Label balance follows equal game/team weighting.

Leave-one-training-family-out cross-validation selects the independent baseline L2
(0.001) and critic mode, L2 (1.0) and shrinkage (1.0).
Each fold fits scaling only on its training portion. The internal requirement is at
least 0.002 Brier improvement plus lower log loss before opening a fresh test.
Training CV Brier: baseline 0.129438, critic 0.125709.
The full model is then fitted once and frozen before evaluation. No checkpoint or
hyperparameter is selected using the v5 outer results. `plan.json` binds the datasets,
map bytes, policy lineages, release runtime and fixed criterion.

Critic export SHA256: `b9380867c31e9b31bb6993b0d38bdedabb1836ac3fedf567f028c87b49985dec`.
`stage4 audit` rechecks hashed replay bytes, release stats, terminal labels and every
stored native state, reconstructing 120,946 states from 75 games.
`stage4 ready` independently recomputes metrics and float64 export accumulation;
maximum probability error is 3.96e-08.
The snapshot API matches 64 native records with maximum
error 0; values stay within [-1,1].
All 103 tests pass. Stage 1 parity, throughput and calibration certificates and Stage 3
actor release/fuel certificates are refreshed against current source hashes.

## Earlier experiments, preserved

| Model | Status | Own-cohort baseline Brier | Own-cohort critic Brier |
|---|---|---:|---:|
| outcome-v1 | invalid | invalid | invalid |
| outcome-v2 | rejected | 0.13402090117443738 | 0.13906797388302033 |
| outcome-v3 | rejected | 0.1253462445673012 | 0.127066577858856 |
| outcome-v4 | rejected | 0.16226743955915793 | 0.16741421569550186 |
| outcome-v5 | passed | 0.13067074600401501 | 0.12507579582082076 |

These cohorts differ: compare predictors **within** a row, not absolute scores across rows.
V1 was invalidated by an unsigned uint8 log-loss bug, now covered by a regression test.
V2's local head, v3's unconstrained centralized residual and v4's monotone state residual
all failed fresh evaluation; their weights/reports remain immutable. V3 expanded the
training games; v5 re-extracts the same 51 clean games with current inventories.
Prior failures informed later hypotheses, followed by new map cohorts and newly frozen
models. Sequential experimentation is disclosed rather than treating the final cohort
as independent of the entire research process. The original v2 report is preserved in
`results/critic-history/outcome-v2.md`; v4's trainer is preserved beside it. V3's trainer
remains `lab/central_critic.py`. `results/stage4-trial-ledger.json` indexes all outcomes.

## Reproduce and use

Check out this PR, restore the previous Stage 1-3 artifact/data packages and the new
Stage 4 v5 data package at the repository root. Follow STAGE1.md for the pinned CLI,
Node and official WASM module. Large replays and native states stay outside Git.
The v5 model package contains the frozen actor/critic exports and evidence; the data
package contains raw sources, current-state shards, map bytes and the v3 source manifest
needed by the inventory extraction. Per-file SHA256 manifests cover both packages.

```bash
cd next
python -m pytest -q tests
python -m lab stage4 collect       # existing shards verified; no new training games
python -m lab stage4 plan
python -m lab stage4 evaluate      # cached native release captures; no refit
python -m lab stage4 audit
python -m lab stage3 verify
python -m lab stage3 release
python -m lab stage1 verify
python -m lab stage1 benchmark
python -m lab stage1 calibrate
python -m lab stage4 ready         # passed=true, next_stage=5
```

The frozen model cannot be overwritten. To refit, choose a new model/dataset, predeclare
new acceptance maps and run `stage4 train` before `evaluate`; preserve inspected cohorts.
The current inference API is
`lab.monotone_critic.evaluate_snapshot(observation, units, terrain)`, returning probability
and value. It requires current native unit inventories, never terminal statistics.

This is an offline critic under the training behavior mixture, not an established value
function for the BC actor or a future PPO policy. Stage 5 must collect on-policy rollouts
and refit/recalibrate it. The actor still banks no gems under its local proposal contract;
submission/macro-action coverage remains future work. No actor-strength improvement,
production integration, live upload or promotion is claimed. Confirmation maps remain sealed.
