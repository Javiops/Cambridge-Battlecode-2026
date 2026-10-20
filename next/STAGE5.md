# Stage 5: first PPO self-play run

`ppo-v1` completed its 12 planned PPO iterations. The pipeline checks pass.
Overall Stage 5 gate: **PASSED**. Stage 5 clears its native training and held-out strength milestone; Stage 6 production integration has not started.
The learned actor is exported; it has not been integrated into production WASM or uploaded.

## Held-out result

The final iteration was chosen before training. After freezing it, 64 native
matches ran on 16 new family-3 maps: both seats and two seed pairings per map.
Every opponent is the unchanged BC model with exactly the same deterministic controller,
draft, temperature and two-decision limit. Final confirmation maps were not used.

| Native comparison | PPO result |
|---|---:|
| Wins / games | 39 / 64 |
| Paired win fraction | 60.94% |
| Whole-map 90% bootstrap interval | [53.12%, 68.75%] |
| Mean final banked gems, PPO | 1.47 |
| Mean final banked gems, unchanged BC | 0.81 |

The predeclared strength gate requires the whole-map bootstrap lower bound to exceed
50%. Five thousand resamples retain every seat/seed pairing within each map. The many
sampled states are correlated and are not independent outcome trials. No fresh-evaluation
result selected a checkpoint or hyperparameter. This tests the stochastic native policy,
not the eventual production implementation or strength against the competition's top bots.

## Starting models and action coverage

The actor starts **exactly** from `bc-v1`, with the same 24 global features, 12 candidate
features, eight hidden units, 16 proposals and 305 float32 parameters. Checkpoint 000 is
byte-identical to its parent. There are no new neural inputs or action dimensions.
Parent actor SHA256: `76ec1dcaf4d37f1cccaccd483885e241a7f14cf929630332ece35e72e5988d3e`.

The critic starts from accepted `outcome-v5`, SHA256
`b9380867c31e9b31bb6993b0d38bdedabb1836ac3fedf567f028c87b49985dec`. Its fixed baseline, normalization and frozen BC
encoder are retained. The 41-coefficient head is copied and extended by one zero
intercept, preserving the accepted initial probabilities. Only this separate 42-parameter
head is subsequently refitted on on-policy completed-game outcomes. The five baseline
coefficients stay fixed. The actor's later updates do not change the critic's frozen
feature encoder. Hidden team inventories enter only the critic; local actor inputs and
the strategic controller receive authenticated observations and public terrain.

The original local actor cannot scout deliberately or submit gems. Both the learning
actor and every comparison/opponent therefore use the **same fixed controller**:

- Preserve active channels and wait while dead.
- Route carried gems to an altar at 40 gems, or any positive bag after round 1600;
  submit when adjacent and preserve the submission channel.
- Approach visible camps while outside attack range. When no camp is visible, scout
  deterministic public-map waypoints, varying by champion and round.
- Defer local combat choices to the policy when an enemy is within six tiles or a camp
  is in attack range. Use only legal movement proposals and visible dynamic obstructions.

These controller rules are not PPO learning and are not credited as a PPO strength gain.
The fresh comparison includes them on both sides. The native fixture verifies a complete
80-gem submission, channel preservation, and that hidden enemy gold cannot alter actor
features. Production pathfinding cost and the full controller's fuel remain uncertified.

## PPO and on-policy critic fitting

The implementation uses the [clipped PPO objective](https://arxiv.org/abs/1707.06347)
with masked categorical action probabilities and analytic NumPy gradients. Each actor
batch is collected from its frozen old policy against a frozen opponent mixture:
50% current snapshot, 25% BC, 25% earlier PPO snapshots (falling back to BC before
history exists). Opponents stay fixed throughout a game and batch. Learner seats are
paired. Opponent actions and deterministic controller actions receive no actor gradient.

Rewards are terminal team win/loss (+1/-1), with **no** gold/gem shaping.
[Generalized advantage estimation](https://arxiv.org/abs/1506.02438) stays within each
game, team and champion. Gamma=lambda=1 makes it exactly terminal return minus the
frozen old value, so an imperfect critic affects variance rather than adding bootstrapping
bias to these advantages. Gaps between sampled states use rounds, not an extra discount
per API call. Two micro-actions in the same round share zero elapsed time.

Sampling records both teams every fifth seeded round, including forced/controller states
for critic fitting. Every intervening turn still plays normally until the real terminal
state; no idle-tail shortcut supplies training outcomes. The old logits, selected log
probability and pre-update critic value are saved and audited. Only current learner
policy decisions enter PPO. The optimizer uses four minibatch epochs, size 512, Adam
learning rate 0.00015, clipping epsilon 0.2, entropy coefficient 0.002, a BC-reference KL
penalty of 0.02, gradient norm cap 0.5, target KL 0.015 and maximum KL 0.03. An epoch
exceeding the maximum restores both weights and Adam state.

The critic has a separate regularized binary log-loss fit to complete on-policy outcomes,
not a clipped value-MSE objective. Its prior is the preceding critic checkpoint, L2=0.1.
A warmup refit precedes actor learning. Whole training families, maps and both seats are
grouped in warmup cross-validation:

| Warmup critic | Brier | Log loss |
|---|---:|---:|
| Accepted offline starting critic | 0.236150 | 0.665112 |
| On-policy refit, held-out training folds | 0.206408 | 0.601384 |

Each later batch computes GAE using its saved old values **before** refitting the critic.
There are 156 training/warmup seat captures (115 distinct native
replay traces) over 24 training maps. Identical-policy self-play seat captures can repeat
the same physical trajectory: they select opposite learner teams, supply no independent
extra outcome evidence, and stay together in map/family splits. This is useful actor
self-play data but avoidable duplicate simulation work for a later collector version.
The fresh evaluation contains 64 distinct native replays.

| PPO iteration | Learner policy samples | Final batch KL | Entropy | Distance from BC |
|---|---:|---:|---:|---:|
| 1 | 6,887 | 0.001716 | 1.0431 | 0.03054 |
| 2 | 11,558 | 0.002085 | 1.0961 | 0.04904 |
| 3 | 8,486 | 0.001671 | 1.0624 | 0.06561 |
| 4 | 7,956 | 0.003270 | 1.0730 | 0.07740 |
| 5 | 6,727 | 0.001458 | 1.0022 | 0.08173 |
| 6 | 11,578 | 0.001286 | 1.0972 | 0.08407 |
| 7 | 8,828 | 0.001739 | 1.0688 | 0.08555 |
| 8 | 7,932 | 0.001986 | 1.0433 | 0.08356 |
| 9 | 6,951 | 0.000460 | 0.9787 | 0.08810 |
| 10 | 11,766 | 0.002333 | 1.0680 | 0.08767 |
| 11 | 8,469 | 0.001186 | 1.0912 | 0.09105 |
| 12 | 7,863 | 0.003099 | 1.0817 | 0.09546 |

Total learner policy samples: 105,001; maximum final-batch KL: 0.003270.
Training win fractions against the changing pool are diagnostics, not a strength gate.
Final actor SHA256: `94c1399f470e7c64f65a203a46d4bd14dff4527057d6eb12fc26fffb79b5402f`.

## Checks and limitations

All 111 tests pass, including analytic PPO gradients with masking/entropy/BC anchor,
both clipping branches, KL rollback including optimizer state, per-champion GAE,
round gaps, binary outcome refits, and bit-preserving cached audit reads.
The audit covers 220 completed captures (179 distinct native replay traces),
1,297,015 sampled states and 14,058 native feature probes.
Every old policy probability and value is recomputed; every terminal label is checked
against the saved native replay. Maximum old-log-probability error:
8.95e-16; maximum native critic-feature error:
0. No native action was rejected. The auditor loads
identical compressed arrays/configuration once per read-only pass to avoid repeated
parsing; its driver rechecks frozen bytes and records its own source digest.

Stage 1-4 certificates are refreshed for current lab source hashes; the original actor
and accepted critic remain unchanged. The PPO actor remains small and its spell coverage
is limited to the existing local proposals. There is no learned draft, full spell policy,
shopping/economy planner or competitive-bot qualification. Stage 6 must port the controller
and sampling/inference behavior to production C++, verify release action/logit parity,
and measure the complete fuel cost before any upload. The final strong-opponent and
promotion gates remain separate.

## Artifacts and reproduction

`models/ppo-v1/checkpoints/000..012` contains immutable float32 weights, exact hexadecimal
C++ headers, JSON weights, on-policy critic/Adam state and checkpoint metadata.
`training.json` and `evaluation.json` bind the fixed final checkpoint and result.
`parent-stage4-ready.json` preserves the exact historical parent gate bound by the plan.
Large trajectories and native replays live in the separate Stage 5 data package, with
raw captures, source/probability hashes and whole-map split plans. The model and data
packages have verified per-file SHA256 manifests.

Restore the prior Stage 1-4 packages and this model/data package at repository root.
Use the pinned CLI/SDK and official engine described in STAGE1.md. Set
`OPENBLAS_NUM_THREADS=1` for reproducible small-matrix numerical accumulation.

```bash
cd next
python -m pytest -q tests
python -m lab stage5 check
python -m lab stage5 plan
python -m lab stage5 train       # validates/reuses frozen completion; resumes incomplete runs
python -m lab stage5 evaluate    # cached final evaluation; no model selection/refit
python tools/verify_ppo_captures.py  # same frozen auditor, efficient immutable array I/O
python -m lab stage5 ready       # pipeline and independent strength outcomes reported separately
```

`python -m lab stage5 audit` also runs the same checks directly, with slower repeated
compressed-array reads. The efficient driver supports `--watch` to verify completed
captures while collection continues. To change training settings/source, choose a new
model and dataset and a fresh outer evaluation cohort; frozen checkpoints are never
silently overwritten. `stage5 ready` exits nonzero when the strength gate is not cleared.
No live upload, champion change, promotion or final confirmation games occurred.
