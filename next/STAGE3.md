# Stage 3: behavioural cloning baseline

The `bc-v1` model is trained, frozen, exported to exact float32 C++ weights and exercised
in the official release engine. This completes the training/export/runtime milestone.
It does not establish a stronger competitive bot. No promotion or live submission changed,
no confirmation maps were played, and Stage 4 has not started.

## Training and separation

- Dataset: `stage2-baseline-v1`, manifest SHA256
  `271e888f1c473b3559d30802d28fa0168be0a982a657a92c456bb216efcb2426`.
- 44,221 training examples from 17 admitted games; 15,070 validation examples from six
  different games. The quarantined episode and 20 external sparring replays are excluded.
- Candidate actor: 24 global features, 12 candidate features, 8 ReLU hidden units,
  16 masked proposals, 305 parameters. Its certified representation is unchanged.
- Actor inputs are only `features`, `candidates`, and `mask`. Win/outcome, seat, input
  index, future state, and private opponent memory are never model inputs.
- Epoch selection uses whole training maps 001, 004, 007 for development, with all their
  episodes and both seats grouped. The remaining three training maps fit the selection run.
  The criterion is the mean of exact candidate accuracy and macro action recall;
  the earliest epoch wins ties. The selected epoch is **115 of 120**.
- The model is then initialized again and refit on all 44,221 examples for 115 epochs.
  Only after that are validation shards loaded. The validation model-selection count is zero.
  Subsequent read-only error analysis reproduces the same frozen model's metrics.
- NumPy 2.5.4, seed 20261023, batch size 256, Adam learning rate 0.003, L2 coefficient
  0.0001; Adam moments 0.9/0.999 and epsilon 1e-8. Weighted candidate cross entropy uses
  inverse-square-root action-class frequencies from the relevant fit partition, capped at
  6 before normalization to unit mean row weight. Padding has zero probability and gradient.
  Training completed in 53.3 seconds on this machine; no GPU or PyTorch is required.

The pre-training plan is `models/bc-v1/plan.json`; selection history, refit history and
metrics are in `models/bc-v1/training.json`. The recorded trainer source digest is in
`models/bc-v1/provenance.json`. Settings are in `[stage3]` in `lab.toml`.

## Held-out results

Exact accuracy means the exact target, move direction, or ability slot matches the teacher.
Action recall below groups proposals by action type, so it can be higher than exact accuracy.
These are correlated replay frames from only two validation maps, not 15,070 independent games.

| Model | Exact candidate accuracy | Action-type accuracy | Macro action recall |
|---|---:|---:|---:|
| Always wait | 56.91% | 56.91% | 33.33% |
| Certified untrained weights | 73.28% | 74.94% | 64.85% |
| Trained `bc-v1` | **63.39%** | **72.28%** | **72.98%** |

| Teacher action | Examples | Trained type recall | Trained precision | Exact candidate accuracy |
|---|---:|---:|---:|---:|
| Wait | 8,576 | 71.02% | 92.95% | 71.02% |
| Move | 3,405 | 73.51% | 72.59% | 41.15% |
| Attack | 3,089 | 74.39% | 94.49% | 66.72% |
| Cast | 0 | Unmeasured | 0% against these labels | Unmeasured |

The trained model beats constant wait by 6.48 percentage points and improves macro recall
by 8.12 points over the untrained weights. It is **9.89 points below the untrained weights
on exact accuracy**. The untrained actor largely waits and attacks: its movement-type
recall is just 0.73%, and exact movement accuracy is 0.21%.

The trained actor predicts 2,637 casts (17.50%) where the validation teachers never cast.
Training uses the team's v76 lineage, which casts; validation uses the SDK starter lineage,
which does not. These predictions disagree with the held-out teacher; whether a legal cast
is beneficial requires in-engine outcome evaluation. Movement direction is another clear
limitation. We retain the original result without selecting a new checkpoint on validation.

The dataset lacks Willow and Heart. Supported casts are only self shield/attack reset;
targeted spells, recall, shopping, tribute, and strategic planning are outside this actor.
No claim of general champion coverage or strong-opponent imitation follows from these metrics.

## Export and official release checks

`models/bc-v1/weights.f32` contains **1,220 bytes**, little-endian float32, SHA256
`76ec1dcaf4d37f1cccaccd483885e241a7f14cf929630332ece35e72e5988d3e`.
`weights.json` and hexadecimal-literal `weights.h` preserve the same values. Layout:
global weights `[24,8]`, candidate weights `[12,8]`, hidden bias `[8]`, output `[8]`,
output bias `[1]`, all feature-major. Argmax ties choose the lowest legal proposal index.

`bc-actor-v1` release WASM SHA256:
`35bff8023613b7932718947dca1d3672243435c2d7110814e00711e643984f37`.
The source bundle rebuilds to these exact bytes. `bc-untrained-v1` has identical controller,
draft, observation encoder, kernel, and diagnostics; only its weight header differs.
Both are local actor canaries without a macro controller; draft is Ryth, Prism, Heart,
Tavi, Cassi, truncated to the map's pick count. Heart/Cassi bodies here are runtime probes,
not evidence of dataset coverage. Each champion executes at most two model decisions per turn.

- On 00collision and generated screening map 002: **1,440 first-decision observations**,
  **23,040 bit-identical Python/WASM logits**, identical legal argmax, and successful
  SDK actions matching actor-scoped native replay. All four supported action types occur.
  An independent scalar reference also checks 64 sampled rows.
- Max observed ordinary-turn encoder/inference fuel across up to two decisions: **47,401**.
  Max measured before the tiny final diagnostic footer: **55,081 of 100,000**. First-turn
  initialization has a separate 200,000 budget. This is a measured envelope, not a proof
  over every possible game state. Full-game statistics show zero faults or fuel exhaustion.
- **24 paired release matches**: both models against dummy and starter, both seats, on
  generated screening maps 008, 009, 010. Zero faults/fuel exhaustion on either side.
  Two additional complete mirror games provide the parity traces above.

| Actor | Opponent | Wins / games | Mean banked gems | Mean camp clears |
|---|---|---:|---:|---:|
| Trained | Dummy | 4 / 6 | 0 | 5.33 |
| Untrained | Dummy | 3 / 6 | 0 | 0 |
| Trained | Starter | 0 / 6 | 0 | 10.67 |
| Untrained | Starter | 0 / 6 | 0 | 0 |

The complete-tie rule awards team B the win. The untrained actor's 3/6 dummy score is
therefore the seat rule, not useful play. The tiny panel cannot establish a strength gain;
the trained actor's 4/6 score is not a promotion result. Both bank zero because submission
is absent from the candidate action set. This is why the artifact is a learning warm start.

`results/stage3-{training,analysis,parity,release,ready}.json` contains the evidence and hashes.
All **78 tests pass**. The reference champion stays `starter-week2-v1`.

## Reproduce and use

Restore the Stage 2 data package at repository root, install `requirements-data.txt`, and
follow STAGE1.md for the pinned CLI/SDK, official rules module and generated maps. The
small trained weights are committed; the large dataset and frozen WASM remain artifacts.

```bash
cd next
python -m pytest -q tests
python -m lab stage3 prepare       # freeze trained/control versions if absent
python -m lab stage3 verify        # official SDK, logits, action and fuel parity
python -m lab stage3 release       # paired screening diagnostics + exact bundle rebuild
python -m lab stage3 analyze       # read-only frozen-model error analysis
python -m lab stage1 verify        # refresh source-bound foundation certificates
python -m lab stage1 benchmark
python -m lab stage1 calibrate     # reuses the 2,500 pinned calibration games if restored
python -m lab stage3 ready         # checks Stage 1/2, weights and release proofs
```

To retrain, choose a **new** `[stage3].model` name in `lab.toml`, then run
`python -m lab stage3 train`. Training refuses to overwrite an existing model folder.
Use new frozen version names for changed bots. Validation is now inspected; changes
motivated by these errors need fresh evaluation data for a new generalization claim.
Keep `bc-v1` as the Stage 3 checkpoint and initialize subsequent learning from its 305
weights; do not upload this canary as a replacement for v76.
