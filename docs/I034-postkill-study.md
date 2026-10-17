# I034: optional immediate postkill capture study

**Keep the selected v4 source unchanged.** The adapted capture block scores 24–16 against v4 in a 40-game diagnostic comparison, but 20–20 against supplied raw v59 and 33–3 on the matched sparring panel where unchanged v4 scores 36–0. This is an interesting local mechanism, not a demonstrated stronger bot. It remains an optional review patch and is absent from the selected source; no upload, activation, online A/B or promotion-gate pass is claimed.

## Exact sources and what the experiment isolates

The new teammate archive has SHA256 `b91c6d08a668ede1d911bfbf8c6d664ed7cf187225ddc082c0e00c05c303b39f`. Its 12-file source differs from supplied raw v59 only in `main.cpp` and `params.h`: a final no-Prism draft filter and an optional immediate capture move after a camp kill. It contains no new camp-damage or tanking mathematics. Testing that complete archive against our v4 measures the combined effect of its own older base, draft filter and capture change; its 17–23 result is not an isolated estimate of the capture block.

The separately frozen `v60-postkill-combined` prototype transplants only adapted postkill capture onto `v60-cohort-view-v4`. It changes `main.cpp` and `params.h`; the other 14 files are byte-identical. It retains our existing Cassi & Issac draft policy, six-body alerts, memory layout and budget/cohort mechanisms. The teammate's separate final draft filter is not imported.

The selected v4 release WASM is `47d988a6219fce3d5fe4008e0d2becb2c5600f6c487d786c7e173f8438bb80da`. The unselected combined prototype's WASM is `959e51b47f5e55542a116b81c610cdbcb2f92afd3611d565846d3959a88b7324`. The source manifest (`source-manifest.json` in the evidence ZIP) binds all three sources, their exact files, release builds and runtime. The minimal optional patch (`optional-postkill.patch` in the evidence ZIP) is against frozen v4, not a replacement submission.

## The proposed behavior

After the existing camp-engagement call, a finisher may use remaining movement to enter an adjacent reward tile immediately. The block first requires authoritative `camp_group_reward_available` state for the whole group; the pre-attack visible-monster list alone cannot prove that every monster was killed. The camp-engagement choice itself is unchanged.

It retains the teammate's narrow conditions: movement available, a current nearest-enemy snapshot with no enemy within six tiles, and the existing `fuel_ok(12000)` check. With the unchanged 6,000 reserve this requires more than 18,000 fuel. The candidate tile must be adjacent, clear of static terrain and current champion occupancy, with snapshot danger below 30% of current health. If another living ally already occupies the reward footprint, the finisher keeps its original position.

The pre-kill blocked mask can still contain the monster that just died. Consequently the optional move queries current champion occupancy instead of rejecting that newly vacated tile using the stale monster blocker mask. This allows the intended capture without weakening static-terrain checks.

The adaptation also addresses four concrete SDK/control-flow issues in the exact teammate block:

1. Skip the allied roster scan if the finisher already stands on the reward footprint.
2. Require a successful complete ally-occupancy scan; a failed or partial query is not evidence that nobody is capturing.
3. Abort the optional move if an SDK read advances the world round, because the nearest-enemy/threat snapshot then belongs to an older round.
4. After a successful move, record the actual current engine round as `cap_start`; the move call itself can span a round.

These checks do not make an SDK check-and-move sequence atomic. A failed move does not publish a successful capture, and the code does not infer a completed reward from merely entering its footprint. It also does not solve full capturer-role assignment, holding an objective through its capture duration, or later contest/rotation decisions.

## Actual-source mechanism tests

The portable fixture package (`portable-postkill-tests.zip` in the evidence ZIP) extracts the actual optional block and four production helpers, verifies the exact post-engagement callsite, and compiles the full production translation unit against the real SDK with the feature enabled and disabled. It then runs the block under narrow deterministic SDK mocks.

The fresh portable run passes **33 adapted enabled cases**, one disabled case proving no extra queries or actions, and 33 exact-teammate comparison cases. The original comparison intentionally reproduces the four control-flow counterexamples above; passing those comparison assertions does not endorse the original behavior. The recorded results (`mechanisms/portable-fixture-validation.json` in the evidence ZIP) bind the exact frozen source and prove it remained unchanged.

Coverage includes authoritative whole-group clearance, missing handles, stale blockers, fresh occupancy, an ally already capturing, a dead ally, already being on the footprint, no movement, strict fuel and threat boundaries, failed/partial SDK reads, eight round-advancing read phases, failed moves, and a move that itself crosses a round. This establishes the implementation's specified local behavior, not competitive superiority or perfect information about unseen enemies.

## Native comparisons

The 20-map diagnostic set contains all 17 current official maps plus three pre-existing contrasting developer maps, played on both physical sides. Its content was frozen before the postkill outcomes. These are known developer/official maps, not sealed unseen tournament validation. The same six-map, three-opponent sparring panel supplies the separate 36 slots.

| Frozen source / opponent | Games | Wins–losses | Fuel candidate / opponent | Captured SDK-error markers candidate / opponent |
|---|---:|---:|---:|---:|
|Exact teammate / unchanged v4 |40 |17–23 |293 /201 |741 /802 |
|Adapted capture + v4 / unchanged v4 |40 |24–16 |241 /214 |818 /822 |
|Adapted capture + v4 / supplied raw v59 |40 |20–20 |152 /261 |799 /764 |
|Adapted capture + v4 / spar11 |12 |10–2 |82 /42 |269 /331 |
|Adapted capture + v4 / spar12 |12 |12–0 |119 /50 |275 /329 |
|Adapted capture + v4 / spar16 |12 |11–1 |105 /42 |253 /343 |
|Adapted capture matched sparring total |36 |33–3 |306 /134 |797 /1,003 |
|Unchanged v4 matched sparring control |36 historical controls |36–0 |302 /146 |822 /1,015 |

The table contains **156 study slots** and 36 separate historical control slots. It does not pool the exact teammate and adapted prototypes into a single candidate win rate. Native faults are zero for both teams in every slot. Captured SDK-error markers remain present, with selective/truncatable stdout; they are not complete error totals and are not native faults.

Against unchanged v4, the adapted prototype wins both sides on seven maps and loses both on three; ten split. The one-sided paired map-sign probability is 0.171875, which does not establish improvement. Against raw v59 it wins both sides on five maps, loses both on five, and splits ten; the corresponding probability is 0.623046875. The modest direct-base result is insufficient to outweigh the observed sparring regressions or claim a stronger general bot.

The three sparring loss slots are Elkring side B against spar11 and spar16, and `fresh-compact-open` side A against spar11. Unchanged v4 wins their matched controls. The flip ledger (`matched-v4-outcome-flips.csv` in the evidence ZIP) records their exact map hashes, sides, seeds, record keys and outcomes. Candidate sparring fuel rises only from 302 to 306; that aggregate difference alone cannot explain individual losses or establish that extra movement is intrinsically harmful.

## What the three actual loss replays show

A bounded replay audit (`mechanisms/loss-audit.json` in the evidence ZIP) reconstructs those three losses and their three matched v4 controls. All six reconstruction/final-death checks pass; each pair has the same actual seed, roster and geometry. Both Elkring opponent labels produce identical full timelines in each version, so they represent two recorded slots but one distinct pattern.

| Matched slot | Combined score | Unchanged v4 score | Gems lost combined / v4 | First actual change |
|---|---:|---:|---:|---|
|spar11 / Elkring B |576–1008 |1008–900 |216 /72 |Ryth R15: `(27,22)` → `(26,22)` |
|spar16 / Elkring B |576–1008 |1008–900 |216 /72 |Same Elkring timeline |
|spar11 / compact A |716–1012 |1014–372 |168 /44 |Ryth R17: `(11,8)` → `(12,8)` |

The first 381 Elkring global action records match. Ryth then lands the final camp hit and uses the new move onto group 1; unchanged v4 yields and steps on next turn. The combined version receives 36 gems in R21 instead of R22. In compact, the first 427 actions match before the analogous final-hit move onto group 4; it receives 36 gems in R23 instead of R24. No enemy is within eight tiles at either initial move. Both Elkring variants have zero fuel exhaustion; compact has 14 versus 15. These first moves work as specified and are not witnesses of a failed occupancy, stale-round or fuel-exhaustion bug.

Later gem losses are higher, but those occur after state divergence. There is no proven complete causal chain from the initial one-turn capture gain to the eventual defeats, and no harmful capturer-rank, altar-lock, shared-memory or cohort conflict was established in these initial witnesses.

There is a concrete later capture-persistence interaction in compact: Ryth clears group 0 and steps onto it in R457, waits through R460, then leaves in R461 as a foe approaches within six tiles. By R462 the capture timer resets; he casts toward the foe in R463 and finally receives the 44-gem reward in R483. An instantaneous entry check does not decide whether the team can hold an objective through its six-round capture horizon. That is a specific remaining policy problem, not proof that this sequence caused the defeat or justification for guessing a larger distance threshold.

The optional move also bypasses the full existing capturer election until the next turn. Its special tank/priority exclusions are inactive in this profile (`dpsfarm=capprio=0`), and no harmful role-assignment witness was found. The evidence supports investigating persistence, contest and later rotation together while preserving the successful local capture mechanism as an optional patch.

## Evidence and selection

The 156-slot ledger (`study-games.csv` in the evidence ZIP) records source/WASM/runtime identities, exact map content and actual seed, statistics/replay-archive/raw-replay/stdout hashes, outcomes, and separate fuel/native-fault/caught-marker counts. The paired outcomes (`paired-map-outcomes.csv` in the evidence ZIP) retain both physical sides. There are 146 distinct native replay streams across the 156 study slots; repeated streams remain documented scheduled outcomes rather than independent tactical discoveries. The unchanged-v4 control's 36 slots contain 28 distinct streams.

The [evidence ZIP](I034-postkill-evidence.zip) includes the exact source archives, minimal optional patch, frozen maps, portable fixtures, raw captured error messages and result/binding manifests. Large native replay archives and executable binaries are omitted; their hashes are retained. ZIP CRCs, saved-record bindings and unchanged production source are verified by the exporter.

The selected source remains v4. Postkill capture is kept as reviewable experimental evidence because its local acceleration works, while the full capture/contest/rotation interaction is not sufficiently understood or validated to enable it. V4 itself remains the review-only candidate described in I033, with no demonstrated superiority over raw v59.
