# I032 — mate_bwf cache, ward spacing and channel starts

**Decision: experimental; playing-strength improvement is not established.** The final three-fix build went **92–102 against the supplied original over 97 maps, both sides**. This PR is for review of the correctness changes, not a recommendation to replace the live bot. The full repository promotion gate was not run and is not marked PASS.

## Baseline and review scope

The baseline is Fran's `mate_bwf_upload.zip`, SHA256 `f5650a73ffaf0af182ff527605bd8337dc67ecd32507703995bbe019f9b0e7af`.
Commit `6d7ace0c6e708e61745c1a1afcd9920ea2bd9f0b` imports its twelve files verbatim into the existing working path, `bots/study27-economy/src`. Review the next source commit against that import to isolate these fixes from the older bot previously in this directory.

Relative to the import, only `draft_plan.h`, `utility.h`, `main.cpp`, `params.h` and the new `channel_safety.h` change. In particular, `fight.h` and `verdict.h` are byte-identical to the supplied ZIP. The live eight-byte communication protocol and champion-selection policy are retained.

During the work, main gained `22b279231c9f5506b64a490a5be8f1bc4820fee2`, which adds `bots/team_baseline`. This PR does not edit that directory. Its measurements apply to the explicitly supplied ZIP, not to a silently substituted team baseline or a new ward-alert protocol.

## Three independent changes

| Switch | Default | Change |
|---|---:|---|
| `P_DP_MEMORY_FIX` | 1 | Build and decode the draft plan transactionally; validate the full v2 packet before committing runtime state. |
| `P_DP_ANCHOR_FIX` | 1 | Choose the best anchor first, then the best candidate at least six Chebyshev tiles from it. |
| `P_DP_CHANNEL_FIX` | 1 | Check local eligibility and actual channel acceptance; continue to the existing fallback when a start fails. |

Setting all three switches to zero exercises the original branches. All eight combinations were compiled and tested separately. Defaults represent the requested experimental correctness package; they were not selected as a statistically superior combination.

### Draft memory

The old planner could mark preparation complete and expose a partially built packet after a failed query or interrupted stage. The fixed path commits a completed temporary plan only after all required stages succeed. It checks packet length, magic, version, readiness, dimensions, draft team size, counts, coordinates and flags before replacing runtime state. Unsupported or incomplete layouts use the fallback rather than being clamped into a plausible plan.

The legacy `CMB1` settings prefix is loaded independently of the extended plan. A failed extended decode cannot suppress those settings. If the full write fails, the short fallback also clears the extended magic: short SDK writes can retain the old tail. An invalid plan, or a completed plan with no usable ward anchor, restores the original ward goal/rank/altar behavior consistently.

Preparation guards reserve fuel and can defer or abandon preparation safely. The 60k admission threshold is **not** a bound on total preparation cost. Earlier fixed-cache diagnostic builds, before the equal-score tie refinement, successfully prepared and loaded the cache on ambush, corners and interlock; instrumented preparation used approximately 56k–206k from roughly 884k available draft fuel. These are representative measurements, not a universal resource guarantee for the final build.

### Ward anchors

The old single pass could promote a new best anchor and move the old best into second place without rechecking their separation. Two passes enforce the distance from the *final* first anchor. Equal scores keep the first candidate in the SDK enumeration order, preserving the original tie rule. The fixture contains the adjacent-promotion counterexample, tied first and second choices, and reversed enumeration order.

The score, number of warders and placement policy are retained. This change fixes the anchor-spacing invariant; it does not establish an optimal vision strategy for every map.

### Channel starts

`recall()` and `submit_gems()` return void. Returning true merely because the call did not throw can stop the rest of the turn even when no channel began. The wrappers now verify `is_recalling()` / `is_submitting_gems()`, with immediate-completion checks where appropriate. Failed starts reach the existing movement, combat or banking fallback instead of being reported as a successful action.

The local guard uses the current position and current round, existing observed champion threats, and actual awake state for nearby damaging camps when considering recall. A move can reveal a new enemy, so the post-move check refreshes positions. Optional `P_TRIBSAFE` is checked at the actual tile; its supplied default remains zero. Safe capture-and-recall overlap is retained after the last camp dies. Ordinary camp damage is not assigned to the submitting champion without target evidence, and ordinary damage is not treated as an automatic submission interruption.

This is a **local** safety check, not a guarantee that an entire stationary channel will complete. The inherited threat estimate can miss future cooldowns, hidden arrivals, projectiles and some CC distinctions. No new full-fight simulation, ability/cooldown observer or blanket 26k entry threshold is added to this final path.

## Verification

`tools/mate_bwf_safety/run.py` compiles the complete production translation unit against the supplied official SDK in all eight switch combinations. It also runs combined WASI fixtures using the actual draft/header code and channel functions extracted verbatim from `main.cpp`. Mock inputs deliberately exercise host failures and malformed memory; they are distinct from native match evidence.

Every combination passed. Checks cover partial preparation, short and unsupported packets, failed writes retaining old tails, independent settings fallback, stable spaced anchors, actual accepted/rejected channel starts, failed-start fallback, stale rounds, moved positions, collection failures and cleared-capture overlap. Source hashes are checked before and after the suite.

Native comparisons used official CLI **2.2.5**, SDK **2.2.5**, release builds and engine **0.0.3**, build `d7e29ae3546357b011419c764204b7b9e2232bdb1b07868250c6b35d4c18d2a5`. Both physical sides were run. The all-disabled control matched outcome, round count, scores, rosters, metrics, event counts, gem ledgers and fuel events in all 32 screening-map side swaps; stdout bytes were not identical, so command-stream equivalence is not claimed.

All audited native bot-fault counts are zero. Fuel exhaustion and caught SDK-error prints already occur in the original; these remain separately reported rather than being described as zero or conflated with native faults. A gameplay fuel event is not evidence of a draft failure. Absence of a fuel event also does not imply identical decisions, because the original has fuel-dependent early exits.

The final combination recorded 188 fuel-exhaustion events against the original's 169 in those 194 direct games. Against the sparring panel it recorded 695 events over 1,850,551 potential completed body-rounds (3.756 per 10k), versus 644/1,853,284 (3.475 per 10k) for the matched original controls. These denominators count physical bodies, not draft picks, and are not alive-turn or exact execution-budget denominators. Resource overhead is another reason not to promote the combination from this evidence.

The submission ZIP has exactly thirteen files directly under `src/`. CRC and every extracted file hash were checked, then the extracted source was built with the official CLI. It produced the same WASM as the final candidate. Its eight smoke slots reused the same saved games and are **not** eight new independent games.

## Results

There were 32 screening maps, 21 initially withheld maps and a separate set of 44 remaining repository holdout maps, disjoint by content hash. The latter set was frozen before any final light-variant games. These historical pools are not claimed to be previously unseen by the team. Selection used filenames/content exclusion, not outcomes or preferred geometry. Map names do not select policies in the code.

Individual changes and the final combination against the exact original:

| Final variant | Screen: 64 games | Initial holdout: 42 games | Separate confirmation: 88 games | Total: 194 games |
|---|---:|---:|---:|---:|
| Memory only | 31–33 | 21–21 | 42–46 | 94–100 |
| Spacing only | 33–31 | 20–22 | 46–42 | 99–95 |
| Local channels only | 31–33 | 25–17 | 44–44 | 100–94 |
| All three | 29–35 | 24–18 | 39–49 | 92–102 |

The three pairwise combinations were also tested on all screening maps. The final combination was tested against each of its six constituents, not just against the old bot. Those results do not establish that combining the fixes improves strength.

Against `spar11`, `spar12` and `spar16`, the final combination won **526/582**, while the original won **520/582** in the corresponding map/side/seed controls. This small difference does not establish a general improvement. Each individual fix also received a three-opponent screening panel. Sparring wins alone are insufficient because these opponents are weaker than the supplied original on many maps.

Paired-map results, matched sparring win flips, per-game hashes and resource measurements are provided in the accompanying `I032-evidence` data. Count maps won from both sides separately from split maps. Stages such as official/dev overlap the screening/holdout groups: do not sum all stage rows. Duplicate physical hashes and cached repeats are not independent samples. There is no configurable CLI seed override in these runs; the actual engine seed is recorded.

### Alternative evaluated

An earlier alternative projected a complete stationary channel using visible enemy cooldowns, repeated spells, dash reach and camp damage. It was tested independently and in all combinations, with separate source/build hashes. It is not included in the final source. Its channel-only original comparison was 55–51 over the initial 53 maps, while its three-change combination was 48–58; this is mixed evidence, not proof that every forecast decision is harmful.

The forecast was conservative about dash arrival, AoE duration and camp targeting, and could overprice a submission by assigning all nearby camp damage to the submitting champion. Matched statistics did not show a broad fuel or death collapse. Actual channel denials were not logged, so their frequency and causal contribution cannot be inferred from fewer completed banks. The final local guard is simpler to audit; its superiority is also unproven.

## Reproduction and promotion

Run the portable regression suite using the SDK and WASI SDK paths on your machine, as described in `tools/mate_bwf_safety/README.md`. For native comparisons, initialize with CLI 2.2.5, verify the SDK version, build both inputs with `cambc build BOT --release`, and run both orders with `cambc run A B --map MAP --release --json --statistics STATS -o OUT`. Reconstruct the original from the import commit and override only the three named definitions in scratch copies for the ablations. Preserve the map, actual seed, engine build, source and WASM hashes when comparing results.

**Formal gate: NOT RUN. Online evaluation: NOT RUN. Promotion: NOT RECOMMENDED on current strength evidence.** The ZIP is an experimental submission candidate for review/testing. Retain the supplied original as the competitive benchmark and review each correctness change independently before deciding whether to integrate it into `team_baseline`.
