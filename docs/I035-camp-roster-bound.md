# I035: distinguish a feasible six-body camp squad from an infeasible sentinel

**The narrow roster-bound correctness fix is selected for draft review only. It is not demonstrated stronger than v4 or raw v59 and is not ready for upload.** It scores 37–37 against v4 on 37 locked maps, 19–21 against v4 on the separate 20-map diagnostic set, and 36–0 in matched sparring. Against raw v59 it scores 31–43 on the same 37 maps where the unchanged-v4 matched control also scores 31–43. No complete promotion gate, online A/B or activation is claimed.

This is a six-body feasibility/sentinel repair, **not a complete camp-damage or tanking fix**. The inherited optimistic damage equation remains unchanged. A separate current-engine replay audit establishes the mechanics that a future per-body tanking model must address.

## 1. The exact bug and correction

The old `squad_needed` tests squad sizes one through five and returns six when none is feasible. That six originally means “not feasible with the tested squad sizes.” Cassi & Issac can produce six physical bodies from five draft picks. A caller comparing that old sentinel with a physical roster of six can therefore treat “not feasible” as “a feasible full squad” without ever evaluating six.

For example, the actual-function fixture uses camp HP 9,600, strength 240, individual DPS 40 and affordable incoming damage 1,120. Under the inherited formula, a six-body squad still estimates 1,600 incoming damage, above the budget. The old function returns six; the new function evaluates six and returns seven, an unambiguous infeasible sentinel. With DPS 80, the estimate is 800 and the genuinely feasible six-body squad remains accepted. These are controlled arithmetic counterexamples, not claims that those exact inputs occurred in a saved match.

The patch adds `physical_roster` to the function and passes `s.roster` at four calls across three functions. `s.roster` comes from the physical champion list, not the draft-pick count. The existing one-to-five hot path stays unchanged. Only a physical six-body roster evaluates the sixth body and uses seven for infeasible. The disabled flag and every roster of five or fewer preserve the old return values.

The explicit monolith/attrition overrides remain intact. The patch does not change damage focus, DPS estimates, reserves, rally thresholds, target scoring, engagement logic or draft policy. Restoring the function and four arguments reconstructs the exact original `main.cpp`; the other 14 files are byte-identical to frozen v4. Only `main.cpp` and `params.h` change.

The candidate is `v60-camp-roster-bound`, release WASM `c638944c600f35f203c6eb8da70545031a598a46af4ee5f7ec1d9473a3ccf922`. Its base is the exact 16-file `v60-cohort-view-v4` from I033. The source manifest (`I035-camp-roster-evidence/source-manifest.json`, inside the evidence ZIP) and minimal patch (`I035-camp-roster-evidence/roster-bound.patch`, inside the evidence ZIP) bind both sources. I034's optional postkill move remains excluded.

## 2. Actual-function and integration verification

The portable tests (`I035-camp-roster-evidence/portable-roster-tests.zip`, inside the evidence ZIP) extract the actual old and new `squad_needed` definitions and assert all four production callsites. They verify physical-roster initialization, exact restoration of all unrelated main code, unchanged headers, and full production translation-unit compilation against the official SDK with the feature enabled and disabled.

Six deterministic configurations cover the bound flag off/on and the existing/future focus and far-only modes. Across 10,000 generated inputs per configuration they check all legacy one-to-five-body outputs, disabled-flag identity, genuine six-body feasibility, the new infeasible sentinel, equality boundaries, harmless camps and the retained monolith override. The fresh portable run passes **720,086 assertions**, preserving both source directories. These are deterministic arithmetic assertions, not 720,086 games or independent tactical findings. The recorded source-bound results (`I035-camp-roster-evidence/mechanisms/portable-fixture-validation.json`, inside the evidence ZIP) retain their exact scope.

## 3. What engine 0.0.3 actually does to camp damage

The separate current-engine contract audit (`I035-camp-roster-evidence/mechanisms/current-engine-contract.json`, inside the evidence ZIP) reads two existing distinct replay streams through round 300. It pins native engine 0.0.3/build `d7e29ae3546357b011419c764204b7b9e2232bdb1b07868250c6b35d4c18d2a5`, editor-engine bytes, replay identities and decoder ABI. Camp HP, strength and design range are cross-checked against direct engine APIs. No new games or source changes were made for this mechanics audit.

Of 770 damaging camp steps, 557 have multiple alive on-field bodies geometrically in design range. All 297 strict-nearest cases hit that nearest body alone; 264 demonstrate the full unmitigated raw hit. Thirteen strict-nearest observations include both teams in range, with eleven full-strength hits. The per-volley damage is concentrated, rather than evenly divided among the surrounding champions.

| Exact replay witness | Relevant bodies | Observed damage |
|---|---|---|
|Elkring R4, elk 1 at `(26,23)`, input 94, native sequence 427 |Issac distance 1; Tavi 2; Cassi and Ren 3 |Issac 900→840 alone; the other three are unchanged |
|Elkring R6, elk 0 at `(3,6)`, input 147, native sequence 699 |Four bodies in range; Tavi uniquely nearest at distance 2 |Tavi 750→690 alone |
|Compact R166, wolf 2 at `(8,9)` |Our Tavi distance 3; opposing Issac distance 2 |Opposing Issac 880→860 alone |

The first example directly contradicts charging 60/4=15 damage to each of four bodies. It does not prove a universal fog/tie rule: camp-side vision/bush eligibility was not independently reconstructed, 260 geometric-nearest ties remain unresolved, and shield/mitigation/linked-life effects can change HP loss. A future model must account for those uncertainties without inventing a physical-ID tie order.

Health history is also an unreliable awake-state proxy. The retained observations contain 82 attacks from camps still at full health, and 289 wounded positive-strength round samples that are explicitly asleep. A concrete sleeping elk is group 6/camp 12 at `(19,2)` in R71: 2,065/2,400 HP, strength 60, engine state 2.

The Elkring group 1 opening shows why replacing `health < max` with only current awake state is insufficient. Both members are asleep at the start of R3. Issac attacks the zero-strength resource at `(26,22)`, reducing it from 500 to 460. Both the resource and its untouched 2,400/2,400-HP elk sibling then become awake; that elk hits Issac for 60 during R4's phase 9, before champion inputs. Forecasting a proposed attack must include the damaging siblings it will wake. A damaged zero-strength resource contributes no incoming hit itself.

The compressed observations (`I035-camp-roster-evidence/mechanisms/current-engine-observations.json.gz`, inside the evidence ZIP) retain all 770 damaging steps and sampled engine states. The input binding records the original observation-file hash and the portable serialization hash separately; only workspace paths and JSON serialization are normalized.

### What remains deliberately unresolved

The selected roster repair retains the `n²` denominator in `squad_needed` with the current focus setting, and the independent target scorer still divides its incoming estimate by team size. Those models conflict with the observed concentrated volley. Current HP-based engagement/awake proxies also remain. This report does not describe those defects as fixed.

A complete replacement must assign each living monster's possible hit to individual bodies using positions, actual range and both teams; handle ties and uncertain visibility conservatively; include newly awakened siblings; and keep clear-time gains from additional available DPS separate from the tank's incoming volley. Heterogeneous ready damage, arrival timing, mitigation, movement and kill order matter as well. Simply removing one denominator or refusing every expensive camp is not a validated tanking policy. No global damage-model change is enabled here.

## 4. Native results and matched controls

The 37-map set was locked before the roster-bound outcomes and contains remaining historical generator-pool content. A separate 20-map diagnostic set uses all 17 current official maps plus three pre-existing contrasts. Both physical sides are played. These sets are developer/official samples, not globally unseen tournament maps; the matched six-map sparring panel is separate.

| Source / comparison | Games | Wins–losses | Fuel candidate / opponent | Captured SDK-error markers candidate / opponent |
|---|---:|---:|---:|---:|
|Roster bound / v4, locked 37-map set |74 |37–37 |27 /27 |823 /823 |
|Roster bound / raw v59, same 37 maps |74 |31–43 |28 /68 |819 /841 |
|Unchanged v4 / raw v59, matched 37-map control |74 separate controls |31–43 |28 /67 |812 /834 |
|Roster bound / v4, 20-map diagnostic set |40 |19–21 |232 /235 |794 /793 |
|Roster bound / spar11 |12 |12–0 |92 /44 |288 /346 |
|Roster bound / spar12 |12 |12–0 |112 /58 |259 /328 |
|Roster bound / spar16 |12 |12–0 |98 /44 |278 /349 |
|Roster-bound sparring total |36 |36–0 |302 /146 |825 /1,023 |
|Unchanged v4 sparring control |36 historical controls |36–0 |302 /146 |822 /1,015 |

The roster prototype has **224 scheduled study slots**. Its 74 matched raw-v59 control slots and 36 historical sparring controls are separate. Native faults are zero for both teams throughout; caught SDK-error markers remain in every recorded game and are distinct from native faults. Selective/truncated stdout is not a complete SDK-error census.

The 37-map direct-v4 panel splits every map, with no map won or lost on both sides; its 74 slots contain only 37 distinct native replay streams. The 20-map direct-v4 diagnostic has one map lost on both sides and no map won on both, producing 19–21. This is a diagnostic weakness, not evidence of a playing-strength improvement. Against raw v59, three maps are won on both sides and nine lost on both, matching the unchanged-v4 control's pattern and all 74 individual outcome labels. The 36 sparring outcomes also match unchanged v4 exactly. Matching outcomes do not mean every command or late state is identical.

The raw-v59 result must be compared with the matched control on these same 37 maps, not substituted for I033's 96-map, 192-game v4 result. That earlier result remains preserved in immutable `view-validation.json` and the historical I033 ledger. The separate new summary is explicitly named `control37`; the evidence package keeps those identities and samples separate.

## 5. Evidence and review decision

The study ledger (`I035-camp-roster-evidence/study-games.csv`, inside the evidence ZIP) binds exact source/WASM/runtime/map/seed and statistics, replay-archive, raw-replay and stdout hashes. It retains separate fuel, native-fault and captured-marker counts. Matched controls (`I035-camp-roster-evidence/matched-v4-control-games.csv`, inside the evidence ZIP), outcome comparisons (`I035-camp-roster-evidence/matched-v4-outcome-flips.csv`, inside the evidence ZIP) and paired map outcomes (`I035-camp-roster-evidence/paired-map-outcomes.csv`, inside the evidence ZIP) support the stated comparisons without pooling different opponents or map sets. There are 146 distinct native streams across 224 roster study slots; repeated streams are not independent tactical discoveries.

The [evidence ZIP](I035-camp-roster-evidence.zip) includes both frozen source archives, the minimal patch, map bytes, portable tests, current-engine camp observations, caught-marker ledger and input/integrity bindings. Large raw replays and executable binaries are omitted. Source hashes, native record bindings and ZIP CRCs are verified.

The six-body sentinel is a confirmed correctness defect, so its narrow repair is retained for draft review despite the absence of a demonstrated strength gain. The broader camp-damage/tanking work remains open, with concrete current-engine counterexamples now documented. Neither this patch nor the combined bot is presented as an upload recommendation or a completed promotion gate.
