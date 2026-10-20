# Stage 6 C++ PPO runtime

`ppo-runtime-v1` integrates the final Stage 5 PPO actor into C++/WASM. It passes
full-game native action parity, release fuel checks and an exact source-bundle
rebuild. Competitive promotion remains a separate Stage 7 decision.

## Frozen model and behavior

The actor is the unchanged 305-parameter checkpoint
`models/ppo-v1/checkpoints/012/weights.f32`, SHA256
`94c1399f470e7c64f65a203a46d4bd14dff4527057d6eb12fc26fffb79b5402f`.
The accepted C++ weight header is copied byte for byte. The deployed bundle contains
no critic, training labels or privileged world queries.

The actor preserves categorical softmax sampling at temperature 1. A 32-bit LCG
advances once per policy decision, including single-candidate decisions, and never
for controller decisions. Allies share its state through the first eight shared
memory bytes. FNV-1a over map dimensions and packed public wall, hole and altar masks
supplies a deterministic seed; team B XORs it with `0x9e3779b9`. WASI randomness is
unused. This deployment seed rule does not repeat the experiment seeds from training.

The farming/banking controller, two-decision limit and draft are unchanged: Ryth,
Prism, Heart of Ruin, Tavi, Cassi and Issac, truncated to the map's pick count.
The controller preserves channels, returns with at least 40 gems or any gems after
round 1600, submits at an adjacent altar, and navigates toward camps or the original
exploration waypoints. Move selection minimizes distance, then y, then x.
Unsuccessful movement remains an accepted attempt, as in the native training worker.

## Release verification

The pinned experiment uses CAMBC CLI 3.0.1, official engine 1.0.0 and the October 20
rules module from Stage 1. All games use `--release` and default fuel budgets.

| Check | Result |
|---|---:|
| Complete matches against frozen current-patch starter | 16, both seats on eight maps |
| Audited deployed champion turns | 160,000 |
| Exact native controller and sampled-policy decisions | 262,936 |
| Independent actor feature and logit probes | 3,041 |
| Bit-identical float32 logit values | 48,656 |
| Feature error at probes | 0 |
| Physical champion types exercised | All six drafted types |
| Bot faults and fuel-exhausted turns, both teams | 0 |
| Ordinary total fuel maximum | 84,574 / 100,000 |
| First-turn total fuel maximum | 97,603 / 200,000 |
| Regression tests | 116 passed |

The cohort covers three-, four- and five-pick maps, including official 71×71 and
80×80 maps. All four submissions match the independent native controller; banking
and channel preservation occur in real release play. The official fuel attachments
account for the entire turn, including trace encoding, stdout writes and `end_turn`.

Every replay is reconstructed with the pinned official engine. The verifier obtains
each actor's authenticated observation, independently encodes features, runs the
frozen JS float32 reference, advances the team RNG, and compares the actual SDK
command with the expected controller or sampled action. It checks both decisions
through round 2000, explicit draft choices, trailing waits, and terminal banks and
outcome against release statistics. Neural probes cover first decisions through
round 80 and every 25 rounds afterwards when the policy acts.

This certificate covers the diagnostic cohort, not every possible map or game state.
The actor lost all 16 games to starter and banked 20 gems total. Stage 5 established
improvement over its BC control, not competitive strength against starter. Stage 7
must address the remaining economy/combat weaknesses before promotion or submission.

## Fuel and trace implementation

The official distance-field search stops once relevant legal moves are reached,
preserving decisions while avoiding unnecessary full-map expansion. Packed terrain
hashing avoids sorting thousands of tiles during initialization. Identical padded
candidate rows share one exact logit evaluation. Model weights and strategy stay fixed.

Development parity checks caught an incorrect exploration waypoint order before
freezing. The incorrect port and experimental guest-side searches were discarded.
The 80×80 stress test also caught first-turn fuel losses, resolved by bounded native
pathfinding and packed terrain seeding. Only the final frozen bytes enter acceptance.

Runtime records use hex text because official stdout attachments insert NUL timeline
separators, which can split a binary record. The parser removes framing NULs,
decodes exact-length records, and rejects truncation, duplicates or incomplete
coverage. Validation raises the log cap to retain full proofs. The exact audited
WASM includes all diagnostic overhead.

## Reproduction and artifacts

Restore the prior Stage 1–5 packages for frozen parents and datasets. Use the pinned
runtime/environment from STAGE1.md, then run from `next/`:

```bash
python -m pytest -q tests
python -m lab stage6 prepare
python -m lab stage6 release
python -m lab stage6 ready
```

`release` freezes source/WASM in `archive/ppo-runtime-v1`, verifies the full schedule,
and rebuilds the source ZIP in a separate directory. Existing frozen versions must
match exactly. `ready` requires the current Stage 5 gate, source-bound release
proof, complete champion/banking coverage, zero faults, fuel headroom, and the
verified source bundle. Lab changes require refreshed Stage 1/3 certificates before
the prerequisite gates can pass.

The 172,172-byte release WASM SHA256 is
`3a8b7f4aba82f3c0ca681ed559167a8913e6341a013d4334b5b50ae7237c607d`.
The exact-rebuild source ZIP SHA256 is
`00ad25648805b8313b45c1337b1cdaab8267a3654058b3347e5a0edb0c4ed238`.
Evidence is in `results/stage6-release.json` and `results/stage6-ready.json`.
Delivery includes source, WASM and hash-manifested validation replays, statistics,
maps and certificates. Final confirmation maps remain sealed; the league champion
and live account are unchanged.
