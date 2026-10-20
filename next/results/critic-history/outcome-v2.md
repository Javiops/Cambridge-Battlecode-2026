# Stage 4: outcome critic from the frozen BC model

`outcome-v2` is trained and exported. Its independent prediction gate **FAILED**.
The critic fails the held-out prediction gate. Keep it as a reproducible rejected experiment; Stage 4 is not cleared for PPO. Do not present the fitted checkpoint as a useful value model.
The original `bc-v1` actor stays byte-identical. PPO, production integration, live upload,
promotion and confirmation-map play have not started.

## What was trained

The actor's certified 305 float32 parameters are loaded directly from `models/bc-v1/weights.f32`,
SHA256 `76ec1dcaf4d37f1cccaccd483885e241a7f14cf929630332ece35e72e5988d3e`. Its feature encoder is frozen and used as a starting
representation. A separate **45-parameter logistic outcome head** is learned; no actor
parameter changes. The critic is a Python training component, not an extra C++ turn cost.

The critic takes 44 current-state features: four score/time/seat baseline features,
the actor's 24 global features, and legal-candidate mean/max pools of its eight hidden
activations. Padding is excluded. The four baseline features are own-minus-enemy bank,
round/2000, known actor seat (-1 for A, +1 for B), and bank margin multiplied by elapsed
time. Seat is critic-only and is available to the actor at decision time. Outcome, future
statistics, teacher action, match/map identifiers and hidden enemy state are not inputs.

The target is completed-game binary win/loss from the acting team's perspective.
`P(win)` maps to `V = 2*P(win)-1`, with no per-micro-action discount. Exact completed
terminal values are +1/-1; incomplete, crashed or fuel-limited captures cannot become
draw labels. A zero nonterminal estimate means uncertainty, not an observed draw.

## Data and model selection

| Partition | Completed admitted games | First-decision states |
|---|---:|---:|
| Training | 28 | 81,953 |
| Historical Stage 2 validation | 6 | 17,947 |
| Fresh Stage 4 evaluation | 12 | 50,800 |

Training spans 17 maps in g1 families 0/1/2. It combines the 17 admitted Stage 2
games with 11 clean games from a predeclared 12-map v76 self-play extension. The extra
game on g1-screen-008 lost one team-B turn to fuel and is quarantined in full, along with
the original Stage 2 quarantined game. The 20 external online sparring replays remain excluded.

Unlike cloning, the critic uses **both teams**, including idle opponents and dead champions,
at the first decision of each sampled turn. A qualified teacher action is unnecessary
for a game-outcome target. Every game gets equal weight, both teams split that weight,
and sampled states split their team's weight. Long games and teams with more actions
cannot dominate; the weighted win prior is exactly 0.5.

Normalization is fitted on the relevant training portion only. Whole maps, with every
episode and both seats grouped, form the internal development split in `lab.toml`.
Four predeclared L2 values (0.001, 0.01, 0.1, 1.0) are compared by development log loss,
then the selected head is refitted on all training games. Critic selected L2
**0.001**; the separately selected score/time baseline uses
**0.001**. Newton optimization converged in
9 iterations. Fitting and evaluation took 8.5 seconds.

The final head is frozen before either outer evaluation partition is loaded. Fresh
evaluation uses maps 039, 041, 044 and 056 (family 3), SDK starter versus its seed twin in
both seats plus starter mirrors: 12 games, with zero faults or fuel exhaustion. Neither
the maps nor either actor/opponent lineage occurs in critic fitting. No model choice
uses these results. Historical validation was already inspected in earlier stages.

## Fresh evaluation

Lower Brier score and log loss are better. ECE is the weighted ten-bin calibration error;
it is not sufficient on its own, since the uninformative constant predictor is globally
calibrated under balanced seat weighting.

| Predictor | Brier | Log loss | Accuracy | ECE |
|---|---:|---:|---:|---:|
| Constant P(win)=0.5 | 0.2500 | 0.6931 | 50.0% | 0.0000 |
| Score, time and seat baseline | 0.1340 | 0.3993 | 77.7% | 0.0630 |
| BC encoder + trained outcome head | 0.1391 | 0.4156 | 78.1% | 0.0313 |

| Phase | Constant Brier | Score/time Brier | Critic Brier |
|---|---:|---:|---:|
| early | 0.2500 | 0.2111 | 0.2131 |
| middle | 0.2500 | 0.1438 | 0.1489 |
| late | 0.2500 | 0.0466 | 0.0547 |

Phases are rounds 1-666, 667-1333, and 1334-2000. Calibration and reliability-bin tables
for every phase and partition are stored in `models/outcome-v2/training.json`.
The acceptance rule, fixed before the final evaluation, requires critic Brier **and**
log loss to beat both constant and score/time baselines on fresh games.

Paired map-level Brier difference (critic minus score/time) has a 90% bootstrap interval
**[-0.0058, 0.0185]**, using 2,000 resamples of four whole maps. Superiority
supported by this interval: **False**. The many replay
frames are correlated; they are not independent outcome trials.

## Invalid first trial and limits

`outcome-v1` is rejected, with its record in `results/stage4-invalid-v1.json`. An unsigned
uint8 label wrapped during unary negation in the log-loss metric, invalidating its
reported log loss and checkpoint selection. A test reproduced the issue; casting labels
to float64 fixes it. The old 013/017/022/028 evaluation maps were marked inspected and
were not reused as this trial's fresh evaluation. The frozen v1 checkpoint was not overwritten.
The revised trial also expands independent training games; all settings and map choices
were recorded before its outcome evaluation.

This is an offline value estimate under the replay behavior mixture. It is **not**
automatically the value of the BC actor or a subsequently changed PPO policy. Stage 5
must collect on-policy trajectories and refit/recalibrate before using value estimates
as trusted advantages. The critic sees local observations and lacks full team inventories
or hidden units; the dataset still has limited independent games and champion coverage.
The actor still lacks submission and macro planning; fitting the critic cannot repair
that action-space limitation. No actor-strength improvement is claimed here.

## Artifacts and reproduction

- `models/outcome-v2/critic.npz`: float32 head, normalization and exact frozen BC backbone.
- `models/outcome-v2/actor.f32`: byte-identical starting actor, for later PPO initialization.
- `models/outcome-v2/score-time.npz`: independently fitted comparison baseline.
- `models/outcome-v2/plan.json`, `training.json`: predeclared selection, provenance and results.
- `datasets/stage4-outcome-v2/`: derived states, fresh raw replays, release stats and source hashes.
- `results/stage4-*.json`: plan, data audit, training, invalid-trial record and readiness gate.

Restore the Stage 2 data package and Stage 4 package at the repository root, and follow
STAGE1.md for the pinned runtime. The data audit reconstructs every state from the hashed
actor-scoped records. The readiness check verifies the parent actor, exports, results and
independent probability accumulation. Large datasets remain outside Git.

```bash
cd next
python -m pytest -q tests
python -m lab stage4 plan
python -m lab stage4 collect      # cached once collected; planned release games only
python -m lab stage4 audit
python -m lab stage3 verify       # refresh foundation certificates after lab changes
python -m lab stage3 release
python -m lab stage1 verify
python -m lab stage1 benchmark
python -m lab stage1 calibrate
python -m lab stage4 ready        # exits nonzero if the predictive gate fails
```

For a new training run, choose new `[stage4].model` and dataset names and a fresh outer
evaluation plan, then run `python -m lab stage4 train` after collecting/auditing data.
Existing model folders are immutable. The inference API is
`lab.critic.evaluate_observations(observations, terrain)`, returning probabilities and
values; call `terminal_value` separately for completed terminal states.

All **89 tests pass**. The exported observation API exactly reproduces predictions on
64 recorded actor observations, and its values stay in [-1,1]. Across the full fresh
evaluation set, probability error against independent float64 accumulation is at most
1.82e-7. Stage 1 and Stage 3 source-bound release/fuel/parity certificates are refreshed;
the unchanged actor still rebuilds to its frozen WASM. `stage4 ready` records pipeline
checks as passed and the predictive gate as failed, and exits with status 1 for that failure.
