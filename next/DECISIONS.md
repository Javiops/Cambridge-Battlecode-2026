# Decisions and evidence

Conclusions that should outlive one experiment, each with the numbers behind it (after Carson's
screeps-rl DECISIONS.md). Open questions go to ROADMAP.md.

## 2026-10-20 · Scout leaders; develop the current draft with a measured curriculum

Use Fish's observed Stellar, Heart of Ruin, Ren, Cassi & Issac, Ryth priority in
a separate `ppo-topdraft` fork. Both observed leaders picked Heart and Ren in
10/10 post-hotfix drafts. V1 wins 67/70 against starter but 124/270 against v12;
keep it as a development reference, without claiming a strength gain.

The first single-objective rally (v2) staged around a large camp perimeter while
counting allies near its centre: zero assault releases in four full-log canaries.
Reject that implementation. V3 uses one reachable home-side point and latches the
assault after the quorum arrives. Four canaries record 96 per-champion releases
with five/six healthy allied bodies assembled. It wins both elk-arena seats,
banking 288/648 against v1's 72/72, but loses both Stampede seats. It wins 67/70
versus starter and 136/270 versus v1 overall, with zero faults and 33 fuel losses
across 340 release games. Retain for research; it is not a promoted replacement.
See TOPDRAFT.md and results/topdraft-v*.json.

All 24 remaining hourly challenges were used: 120 v83 games across all 35 maps,
both seats, and the top ten teams. Result 4/120, zero faults, 29 fuel losses (all
big-world). Every replay and champion statistic matches the official 1.0.1 WASM.
Such saturated losses are scouting, not the sole progress signal. Hourly testing
now targets approximately 60% nearby/moderately stronger teams, 30% stretch,
10% leaders, using economy/objective/fight/runtime measurements as well as wins.
Fran authorizes automatic tested uploads with short notes; require a fresh
promotion check before stable live replacement. No additional model was trained.

## 2026-10-20 · Hotfix compatibility and actual v83 deployment verified

The unchanged v12 source builds with CLI 3.0.2 to identical WASM under engine
1.0.1. Compatibility repeats are 68/70 on current site maps, zero faults and
17 fuel losses; 140/140 on its locked-map repeat, zero faults/fuel losses.
These are compatibility checks, not fresh independent confirmation.

Fran authorized reselecting v83 and keeping it live for the PPO test. Server
compilation succeeded. The initial Nyx group wins 1/5 and automatic ranked TTS
wins 2/5, both with zero faults/fuel losses. The earlier 0/5 Fish group ran v81
and stays excluded from PPO evaluation. The source ZIP is hash-verified and all
130 audited v83 replays reconstruct exactly. See HOTFIX-1.0.1.md.

## 2026-10-20 · Stage 7 hybrid clears the unchanged promotion gate

Keep `ppo-league-v12` as the qualified candidate: 140/140 wins
(100.00%) on 70 fresh generated confirmation maps, both seats,
zero bot faults and 0 fuel-exhausted turns
(0.0000/game against a 1.0 limit). The source ZIP reproduces
the frozen WASM exactly. Screening wins are 200/200; site stress wins are 12/12;
the full fixed-panel candidate record is 1,000/1,000. See STAGE7.md.

The original actor alone loses 200/200 screening games. The expert/PPO hybrid's
matched actor-disabled control also wins 200/200, so attribute this competitive
improvement to the strategic controller. Six native canaries record
215 PPO calls and 104 changed targets; the
unchanged actor is active, but its independent strength gain is unproven.

Bound optional planning cooperatively and provide a cheap camp fallback when
full planning cannot fit. Keep the checkpoint throw out of line: v11 passed its
game gate but failed an independent byte-exact source rebuild. V12 fixes packaging;
it was verified before consuming a fresh outcome-independent confirmation pool.
The earlier 137/140 result remains historical. Both cohort locks must be retained;
neither cohort may guide another tuned candidate. No upload or champion change.

## 2026-10-20 · PPO C++ runtime passes Stage 6

Keep `ppo-runtime-v1` as the exact runtime port of final PPO checkpoint 012.
Sixteen complete release games cover 160,000 turns and 262,936 native-equivalent
decisions, with all six physical champion types, both seats and maps up to 80×80.
Official total fuel peaks at 84,574/100,000 on ordinary turns and 97,603/200,000 on
first turns; no faults or fuel losses occur. The source ZIP rebuilds to the frozen
WASM. See STAGE6.md and the executable `stage6 ready` gate.

Preserve softmax sampling, team-shared RNG and the training controller. Packed
terrain seeding, early-terminating native pathfinding and shared padded-row logits
reduce fuel without changing the policy. Use hex traces: stdout NUL framing can
split binary records. Both the native parity checker and official total-fuel stream
are required; a neural-kernel measurement alone is insufficient.

The actor loses 0–16 against starter in this diagnostic cohort and banks 20 gems
total. Runtime acceptance does not qualify it competitively. Stage 7 needs stronger
economy/combat behavior and a separate promotion gate. No confirmation or live play.

## 2026-10-20 · First PPO self-play run and native strength gate

Freeze the BC actor and accepted outcome critic as parents, then warm up/refit the critic
on current native behavior and train 12 PPO iterations against frozen self-play snapshots.
A shared deterministic scout/camp/banking controller supplies missing strategic action
coverage on both learner and BC control; it is not attributed as a PPO learning gain.
The 305-parameter actor receives only its original authenticated feature tensors.

The on-policy critic's held-out training-fold Brier improves from
0.236150 to 0.206408.
PPO's final checkpoint scores 60.94% on 64 fresh paired native games,
with whole-map 90% interval [53.12%, 68.75%].
Native pipeline checks pass; strength gate: **PASSED**. Stage 5 clears its native training and held-out strength milestone; Stage 6 production integration has not started.

Audit 220 captures/179 distinct replay traces and 1,297,015 states;
111 tests pass. Equal-policy self-play seat captures can repeat a physical trajectory;
map splits retain these together and the final test contains 64 distinct replays.
No production WASM strength/fuel claim, upload, promotion or confirmation play follows.
See STAGE5.md, results/stage5-ready.json and models/ppo-v1 for frozen evidence.

## 2026-10-20 · Stage 4 inventory critic passes the unchanged acceptance gate

The local-only v2 critic failed; v3's centralized residual and v4's monotone residual
also failed fresh tests. V5 addresses wallet-gold confounding with current equipment
value plus cash, queried causally from native replay state. Nonnegative advantages,
regularization and calibration are selected only on training families. The selected
head uses team/economy features, not BC hidden activations; the frozen actor is unchanged.

V5 uses 51 clean games/40 training maps (74,491 states); 24 new release games/eight unseen
maps and a held-out SDK lineage supply its one outer test. Brier is
0.125076 versus baseline 0.130671;
log loss is 0.386293 versus 0.400749.
Both beat constant prediction too. Paired whole-map Brier difference has 90% bootstrap
interval [-0.009628, -0.001345]. The frozen v5 critic is accepted for the Stage 5
starting point under the existing offline criterion; this is not a bot promotion.

The full audit reconstructs 120,946 states from 75 completed games, export/API
parity passes, all 103 tests pass, and foundation certificates are refreshed. Previous
failures, weights, map cohorts and the v4 trainer remain preserved. Sequential trials
informed later hypotheses; scores from different cohorts are not directly comparable.
See STAGE4.md and results/stage4-trial-ledger.json. PPO has not started. It must gather
on-policy data and refit/recalibrate; the local actor still lacks submission coverage.

## 2026-10-20 · Stage 4: retain the outcome critic experiment; reject the readiness gate

The binary outcome critic reuses `bc-v1` as a frozen feature encoder and trains a
45-parameter readout, with the actor byte-identical. The corrected trial fits 81,953
states from 28 games on 17 training maps, selecting regularization on whole internal
development maps, then refitting all train games before loading outer evaluation.
Both actor teams contribute, weighted equally per game and team; long trajectories
do not count as more independent outcome evidence. A new v76 fuel-limited mirror is
quarantined along with the original Stage 2 rejection.

On 12 fresh SDK-lineage games across four new family-3 screening maps: critic Brier
0.1391, log loss 0.4156, accuracy 78.1%, ECE 0.0313. Constant Brier is 0.2500; the
score/time/seat baseline has Brier 0.1340, log loss 0.3993, accuracy 77.7%, ECE 0.0630.
Better accuracy/calibration-bin error does not override the predeclared proper-score
gate: both Brier and log loss must improve over the simple predictor. They do not.
The paired map Brier-difference 90% interval is [-0.0058, 0.0185], overlapping zero.

The first trial's log loss and model selection were invalid because negating a uint8
label wrapped before multiplication. A reproducing regression test fixes the scorer
by converting labels to float64. That trial remains recorded as invalid, and revised
evaluation uses different maps. No validation-directed checkpoint changes follow the
corrected trial. Stage 4 remains uncleared; keep this as a provisional offline seed,
not a verified on-policy PPO critic. No actor update, PPO, live upload, promotion or
confirmation play. See STAGE4.md for the data, phase metrics and artifacts.

## 2026-10-20 · Stage 3: keep the cloned checkpoint, reject promotion

`bc-v1` trains the certified 305-parameter actor on 44,221 admitted examples. An internal
whole-map development split selects epoch 115/120; a fresh refit uses all training data
before validation is loaded. Held-out exact candidate accuracy is 63.39% against constant
wait's 56.91%, but below the untrained model's 73.28%. Macro action recall improves from
64.85% to 72.98%; movement-type recall improves from 0.73% to 73.51%. Exact movement
accuracy remains 41.15%. Training/validation teacher-lineage shift produces 2,637 cast
predictions against zero validation cast labels. No validation-based checkpoint change.

The exact float32 export passes 1,440-turn official release parity (23,040 bit-identical
logits, all four supported action kinds) and 24 paired screening diagnostics, with zero
faults/fuel exhaustion. Max measured ordinary-turn fuel is 55,081 before the tiny footer.
The trained actor banks zero gems and scores 0/6 against starter; it lacks submission
and macro actions. Keep the model as an offline learning warm start, reject it as a
competitive replacement. No strength gain is established, no confirmation map is opened,
the live v76 submission is unchanged, and Stage 4 has not started. See STAGE3.md.

## 2026-10-20 · Stage 2 baseline: exact replay reconstruction and disjoint lineages

The copied active v76 source builds on the pinned SDK and is frozen as
`online-v76-week2-v1` (origin archive/submission in `bots/baseline-online-v76/ORIGIN.json`).
The 24-slot plan reserves g1 families 0/1/2 for its demonstrations and family 3 for
independent SDK-starter validation. Idle opponents provide context, not teacher labels.
23 clean games yielded 104,133 sampled frames and 59,291 eligible BC rows; one v76 mirror
lost one turn to fuel and is quarantined. Neither that game nor any confirm game trains a model.

The importer reconstructs scoped observations before native inputs. Its 2,560-frame
SDK-log differential test passes, including decoded action sequences. The official replay
omits guest-memory writes and boolean action returns; those remain null. The v1 features
do not use them. Unsupported teacher actions retain null candidate labels.

Four authorized unranked groups (20 games, both seats) against Nyx and Sneaky Bush Campers
all ended in v76 losses. Replay terminals agree with website outcomes. Missing exact
server-build/opponent-WASM identity and overlap with the v76 lineage keep these files in
external diagnostics. Local train/validation maps, families and lineages remain disjoint.

The admitted rows have 44,221 train and 15,070 validation examples; constant wait already
scores 56.9% on validation. Seven training body types, missing Willow/Heart and only 203
supported training casts limit the baseline. Stage 3 must use per-class metrics and live
release evaluation. Details and actual data layout: STAGE2.md. Training has not started.

## 2026-10-20 · Stage 1 complete: use the official rules module for training

The fast environment wraps the exact pinned official WASM module. We avoid maintaining
a separate implementation of the rules. Its authenticated actor observations and action
results match 2,560 release frames across four maps with 3/4/5 picks, including linked
Cassi/Issac bodies. All four matches agree through the final 2,000-round outcome and banks,
with zero faults or fuel exhaustion. Hidden-health mutation leaves the actor observation
unchanged; hidden champion data and enemy inventory queries are denied.

The certified micro-policy envelope is 24 global features, 16 candidates of 12 features,
eight hidden units, 305 float32 weights and at most two decisions per turn. Two full
encode/inference passes stay below the 65,000-fuel admission limit. The earlier larger
three-pass probes exhausted fuel and were rejected before freezing. Retain release fuel
checks for future architecture/feature changes and the eventual trained export.

The g1 pool contains 100 screening maps and 60 sealed generated holdouts; the ten `01*`
site maps are also sealed. Every generated map passed official structural checks and exact
regeneration. The 2,500-game five-control league has zero faults or fuel exhaustion. Ratings:
starter 1,828; seed 1,812; skip10 1,790; skip2 1,384; dummy 687. The 16-point seed gap is
smaller than both handicap gaps (38 and 444). Seed vs starter is exactly 50% over 200 games.
The skip10 interval overlaps starter's, so its rank is a calibration sanity check rather
than evidence that similarly small future improvements are significant.

Saved proofs in `results/stage1-*.json` bind source, configuration, runtime and map/bot
hashes. `python -m lab stage1 ready` is the acceptance check. See STAGE1.md for the actor
contract and reproduction. Stage 2 data collection has not started; no confirmation games
were inspected and no bot was promoted.

## 2026-10-20 · Recalibrate after the week 2 patch

CLI/SDK 3.0.1 changes the rules and design ABI. The lab now pins the observed release engine build,
records an SDK fingerprint for each frozen version and rejects incompatible versions/results.
Pre-patch calibration is historical evidence, not a rating for a current bot.

The fresh three-reference league completed 99 release games on 11 screening maps, both seats plus
mirrors, with zero faults and fuel exhaustion. Total league/report time was 23.679 seconds using
four workers (4.181 games/second on this machine). All 40 unit tests pass; the starter source bundle
rebuilds to exactly its frozen WASM bytes. See `results/calibration-2026-10-20.md` and
`results/patch-validation-2026-10-20.json`.

The seed control rates 1813 (90% interval 1749–1902), starter 1719 (1631–1780), dummy 968 (935–972).
The control's 94-point gap and 64% head-to-head score over 22 games reinforce the need for more maps
before judging small changes. The intervals overlap. The starter remains the reference champion;
no confirm maps were played and no promotion was made.

This was the initial patch-only milestone. The subsequent Stage 1 completion above adds
the fast training environment and neural inference fuel certificate.

## 2026-10-17 · The judge is a pool rating over all versions, not one variant against one base

Every frozen version plays every other on every screen map from both sides. Ratings are fitted
on the whole batch (Bradley-Terry on the Elo scale, `lab/rating.py`) with a 90% bootstrap over
maps. Carson used TrueSkill for the same job; Bradley-Terry needs no package and does not depend
on the order games were played in. Unit tests check that it recovers known ratings within 25 points.

## 2026-10-17 · Calibration: 12 maps x 2 sides can see a large handicap, not a 10% one

Five bots of known strength, 300 games on the 12 screen maps
(`results/calibration-2026-10-17.md`):

| version | what it is | rating | 90% range | final gems |
|---|---|---|---|---|
| calib-seed-v1 | starter with another random seed (same strength) | 1838 | 1770–1923 | 853 |
| calib-skip10-v1 | starter that skips every 10th round | 1830 | 1770–1918 | 840 |
| starter-v1 | the SDK starter | 1777 | 1719–1857 | 824 |
| calib-skip2-v1 | starter that acts every other round | 1384 | 1292–1436 | 510 |
| dummy-v1 | never acts | 672 | 601–704 | 0 |

- The large handicap (half the turns) is clear: 17% against starter, about 400 points below.
- The 10% handicap is invisible: skip10 scores 58% against starter and sits above it.
- Two bots of equal strength (seed vs starter) differ by about 60 points and their ranges overlap
  almost fully. **That is the noise floor of this map set: a gap under ~100 points, or under ~60% head to
  head on 24 games, is not a result.**
- **Consequence:** the loop needs many more maps before it can judge small changes. A map generator is the
  first item in ROADMAP.md. This is the same problem that made our old A/B tests inconclusive, now measured.

## 2026-10-17 · Side B is favoured on the site maps

Every version scores 10–29 points better as side B (seat split in the calibration report). Mirror
games of the starter go to side B 10 times out of 12. A complete tie also goes to B by the rules.
So every comparison plays both sides, and a result from one side is never reported alone.

## 2026-10-17 · Map roles

Only 17 site maps exist locally. 12 are `screen` and 5 are `confirm` (`lab.toml`). The qualifying
maps will be new, so the long-term confirm set is generated maps no one has tuned on.

## 2026-10-20 · Nearby curriculum and failed development candidates

Used all 50 available challenge groups for 250 v83 games, both seats and all 35 maps. Keep live strength separated by opponent cohort. Rejected Heart-focus v4 (95/270 versus v3) and global-area-reserve v5 (initialization starvation). V6 reduces fuel losses versus its parent (14 versus 23) but wins 151/302; against qualified v12 it wins 149/302. No promotion or upload, no confirmation outcomes consumed. Preserve v6 as a runtime hypothesis, not a proven strength improvement. See MAP-LEARNING.md and compact results.

## 2026-10-20 · V84 live field test

V84 compiled on the platform and stays live for iterative learning. Used all eight available challenge groups: 16/40 wins and zero faults/fuel losses, versus 14/40 and 12 fuel losses in the corresponding historical v83 blocks. Do not claim overall strength improvement from this small, partly historical comparison. Stampede wins both seats; elk-arena deposits increase but both seats lose. Big-world B carriers repeatedly hold gems at unchanged positions in tribute mode, so the next isolated hypothesis is obstacle-aware banking progress under low fuel. No promotion, rollback or model retraining. Full evidence: V84-SPARRING.md.

## 2026-10-20 · V7 banking priority and teammate handoff

Continue safe existing banking trips before optional group planning. The local big-world starter reproduction rises from 121/0 to 316/105 banked gems in both seats, with zero faults/fuel losses. Broad screening: 67/70 starter and 148/302 v6; 14 fuel losses across 372 games, zero faults. No proven strength gain or lab promotion. V7 uploaded as v85 and compiled; then Fran requested a teammate handoff, so v82 was restored as selected and live actions were held until 23:10:20 UTC unless released earlier. Zero v85 unranked requests were initiated. Small late-game cargo can still stall; next isolate continuation of positive-cargo trips without changing their start policy. See BANKING-V7.md and LIVE-HOLD.json.

## 2026-10-20 · V8 positive-cargo continuation, offline only

Complete already-started healthy/quiet banking trips even below 12 gems. Big-world starter deposits improve from v7 316/105 to 692/800 with zero faults/fuel losses. V8 wins 152/302 against v7 and 146/302 against fixed v6; starter 69/70. Fuel totals 106 versus v7 and 14 versus fixed v6 are matchup-dependent: the reverse-seat v7 also exhausts 94 times on the same generated B-seat fixture. Do not label that difference a new regression without the fixed-opponent control. No promotion or online upload during the teammate hold. Next isolate the optional spell-scan budget guard. See BANKING-V8.md.

## 2026-10-20 · V9 optional spell guard rejected

Raising only optional spell-scan entry headroom from 22k to 41k does not fix the reproduced Stellar failure: 94 B-seat fuel losses persist. Ten targeted canaries have zero faults. Do not broaden or upload a failed target hypothesis. Frozen v9 and its reproducible source remain intact; working source returns to v8. No global initialization reserve or model change. See BANKING-V9-REJECTED.md.

## 2026-10-20 · V10/V11 runtime hypotheses rejected

Native PPO tile lookups and failed-planner cost learning each leave the 94-loss B-seat case unchanged. Both have ten canaries, zero faults and exact independent rebuilds; neither receives a broad screen or upload. V11 also weakens stress-map banking. Working source returns to v8. Actor-disabled and phase-only diagnostics change the trajectory, so they narrow investigation without proving cost attribution. See RUNTIME-PROBES.md.

## 2026-10-20 · V12 contact-first combat work retained offline

Move the unchanged contact test before ally metadata gathering. Frozen v8 mirror B loses 94 turns; v12 B versus the same v8 opponent loses zero and banks 245 versus 105. Big-world starter banks remain 692/800. Broad 69/70 starter, 157/302 v8 with six total schedule fuel losses; 150/302 fixed v6 with five. Zero faults and exact independent rebuild. This supports a usable targeted runtime fix, not a proven overall strength gain or lab promotion. Keep the teammate hold; stage v85, v8 and v12 field pairs afterward. See CONTACT-V12.md.

## 2026-10-21 · V86 and V87 live, matched benchmark complete

Honored the teammate hold, then collected/native-verified both seats for v85, uploaded/tested v86, then uploaded/tested v87. Each wins 5/10 with zero faults/fuel losses. Big-world banks rise from 202/90 to 381/336; elk B collection/deposits regress. Retain v87 for broader learning, without a strength/promotion claim. Server source deliveries and live compilation are verified. Use the remaining actual quota purposefully; BANKING-FIELD.md preserves the tradeoffs.

## 2026-10-21 · V87 broad field evidence

All 44 groups / 220 games collected and native-verified on 35 maps: 75 wins, zero faults, one fuel loss. Historical same-label v83 subset: 87 wins, 70 fuel losses; this is descriptive, without certified old opponent-B/seed equivalence. Runtime improves while overall results regress. Keep v87 as a usable experiment under Fran's policy; diagnose contest acquisition/delivery and objective fight exposure rather than undo banking automatically. Final actual allowance zero; retain the existing 15-minute check. See V87-CURRICULUM.md.
