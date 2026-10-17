# I033: replay-backed repairs and a v59 draft candidate

Review: [draft PR #35](https://github.com/Javiops/Cambridge-Battlecode-2026/pull/35), following up the earlier I032 combination.

The previous combined `mate_bwf` candidate scored **92–102 against its supplied original** over 97 maps, despite passing its individual mechanism tests. Reviewing the actual replay commands exposed two concrete implementation failures: draft-cache validation consumed opening action fuel, and ward-revealed distant camps could become unreachable pathfinding destinations. These explain specific lost decisions. They do not establish that every loss had the same cause.

The submission candidate in this follow-up uses the team's newer **v59 wards-and-alerts bot**, with those narrow repairs, a supported allied-ward query, and a separately tested no-Prism draft policy. It is an **experimental candidate for review**, with mixed offline results: **25–23 against supplied v59 on the separate map set, but 34–2 against sparring bots where raw v59 scores 36–0**. A reliable upgrade is not established. The repository's full promotion gate and online A/B remain pending.

## Exact bases and scope

| Reference | Identity | Role |
|---|---|---|
| Original I032 input | `mate_bwf_upload.zip`, SHA-256 `f5650a73ffaf0af182ff527605bd8337dc67ecd32507703995bbe019f9b0e7af` | Diagnose the earlier combined regression against the exact original |
| Previous combination | `light-all`, the original I032 draft PR candidate | Reconstruct the decisions that regressed |
| New team base | `battlecode_mate_all_wards_alerts_v2.zip`, SHA-256 `9b8482af47f275a99d3e4d505495fdcc504b54957ca6db8b53ddcd16fe6bf081` | Base of the new candidate, called v59 below |
| Selected candidate | `v59-swap-cassi-v2` in the frozen build ledger; published under [`bots/team_baseline/src`](../bots/team_baseline/src) | v59 + narrow repairs + Cassi replacement policy |

The old-combination repair and the new v59 candidate are distinct experiments. Their results must not be added together as if they tested one bot. Source, WASM, map, replay and statistics hashes are recorded in the [final summaries](I032-diagnosis-evidence/final-v2-summary.json), [per-game ledger](I032-diagnosis-evidence/final-v2-games.csv) and [frozen builds](I032-diagnosis-evidence/final-v2-builds.json). Both physical sides are tested per panel map. CLI/SDK **2.2.5** and engine **0.0.3** are pinned; actual seeds are recorded because this CLI exposes no seed override.

## 1. Strict memory validation changed the first movement decision

On `gen20261015_47`, side A, the previous combination and memory-only variant omit Issac's and Ren's intended opening dashes. The anchor-only and channel-only variants issue the dashes. Draft order, starting tiles and initial camp targets agree.

| Actor, round 1 | Original-style opening | Memory-only / previous combination |
|---|---|---|
| Issac | Dash `(4,3) → (6,3)`, then move to `(7,4)` | Move only, `(4,3) → (5,2)` |
| Ren | Dash `(5,3) → (7,5)`, then move to `(8,6)` | Move only, `(5,3) → (6,3)` |

An isolated diagnostic captures fuel before the branch and prints only after the actions. Full cache validation costs **3,579 fuel**, versus **701** for the legacy load. At `step_towards`' unchanged threshold of **31,000** including its reserve:

| Actor | Memory off | Memory on |
|---|---:|---:|
| Issac | 31,449: normal path and dash | 28,682: low-fuel fallback |
| Ren | 31,617: normal path and dash | 28,758: low-fuel fallback |

The fallback returns before dash selection. **Neither side records a fuel-exhaustion event.** The regression is therefore visible in action selection before a hard budget failure. The raw, uninstrumented replays independently show the same command divergence; instrumentation has a small separately acknowledged cost.

The repair keeps independent legacy settings at initialization, copies only the supported **256-byte packet** into owning storage, and finishes the **same full validation** after useful turn actions, before ward placement when reserve permits. Runtime planner state remains invalid until validation completes. Short/malformed packets are rejected; pending validation prevents committing a permanent ward from an unvalidated plan. Movement and combat fuel thresholds are unchanged.

The isolated repair restores the exact selected Issac/Ren opening commands. Its selected verification game changes from the previous combination's **978–1058 loss** to **1006–832 win**, with no native fuel exhaustion. This is a causal mechanism check on a diagnosed case, not an independent playing-strength estimate. The full combined repairs are tested separately below.

Integration exposed a second counterexample: the first combination of the deferred-memory repair with the camp-approach repair again omitted the opening dashes on this map. Its additional pre-step destination check spent action fuel before the original movement guard. The v2 callsite therefore executes the **original `step_towards` first**; only when it returns false, movement remains available and reserve permits does it perform the costly visible-camp check and try neighbouring goals. Normal successful approaches do not pay for that new check before acting.

The integrated old-combination repair, `old-all-repaired-v2`, now passes a native replay assertion for **all four original Issac/Ren dash-and-move commands**, including exact coordinates, on the diagnosed map. It also restores the selected **1006–832** result. This v2 proof is separately bound to its frozen build and raw replay; the isolated success is not retroactively attributed to v1. Failed v1 integration results are retained as historical evidence below.

An early diagnostic attempt copied the entire SDK snapshot and failed to restore the opening. The retained repair copies only the bounded packet; the failed attempt is not the published implementation.

## 2. More ward vision exposed an unreachable camp approach

On `monolith`, side B, the previous combined bot places a ward at `(8,8)` in round **261**. By round **322**, Varg at `(23,0)` sees wolves at `(3,9)` and `(4,9)` through that ward. Those occupied tiles enter the blocker mask. The lean camp scan omits this group because it is more than 12 tiles away, leaving no local monster to attack. The approach tries to path to the occupied camp tiles themselves: its effective destination becomes empty, and Varg yields in rounds **322–325**.

The repair approaches **free neighbouring tiles** when remote, ward-visible camp occupancy blocks the ordinary destination. It preserves local attacks and the existing safe movement machinery. In the selected replay, all four missing movements return. That game changes from a **944–1032 loss at round 411** to a **1032–988 win at round 410**. The v2 integration retains this recovery while also retaining the opening dashes on `gen47`; both mechanisms must pass together. The other physical side of the isolated Monolith check keeps its previous loss, which is included in the evidence.

The lesson from this case is a dependency between scouting and navigation: additional vision changes which tiles are known occupied. Fixing ward placement alone does not repair a destination rule that cannot handle the revealed occupancy. This is not evidence that additional vision is inherently harmful.

## 3. v59's teammate-ward queries could never populate spacing data

The supplied v59 loops through teammate champions and calls `ally.ward_positions()` inside a swallowed exception handler. SDK 2.2.5 explicitly requires a **self handle** for that method. Every non-self call therefore throws; the allied-ward list remains empty, so the existing overlap penalties never apply. Those calls also waste fuel.

The repair uses the supported `bc::vision::wards(*s.my)` API and retains v59's existing scoring and placement policy. This supplies **currently visible allied wards**, not omniscient information about every ward on the map. No alert/claim bytes are reused. Dedicated actual-source tests cover the SDK contract and the effect of visible nearby wards on placement scoring.

The static cache also retains the two-pass anchor-spacing correction. v59's enabled all-champion passing-ward policy uses its own local placement scoring; the static anchors must not be presented as a guarantee of global six-tile separation between every actual ward.

## 4. Channel safety has a measurable conservative cost, not a demonstrated classification bug

On `interlock`, side A, round **53**, Cassi carries **22 gems** at **680/700 HP**. She moves from `(17,18)` to `(18,17)`, next to altar `(19,16)`. The earlier combination's guard sees a possible ready pure stun and omits submission. The matched no-guard control starts in round 53 and completes in round 56; the combination starts in round 54 and completes in round 57. Both observed channels finish unharmed. The next camp attack is also later.

The diagnostic reproduces the original combined command stream and records `ctrl=1`, `unknown=0`, damage estimate `70`, nearest distance `5`. This is an observed conservative-policy timing cost. The enemy electing to move away in this replay does not prove that ignoring the available stun was always safe, or that this one delay caused the eventual loss.

The suspected blanket classification of damaging spells as crowd control was checked and rejected: the relevant `Threat::sr` field is assigned to the pure, movement-compatible control-spell class. No patch is justified by that disproven hypothesis. **The new v59 candidate preserves v59's channel policy; it does not import the old channel model.**

Exact replay excerpts and perspective checks for these cases are in the [native evidence bundle](I032-diagnosis-evidence/native-cases.zip), which contains the README, replay manifest, mechanism evidence and eight raw replay streams. Saved replay streams are examples, not additional strength samples.

## 5. A no-Prism candidate, with its communication tradeoff recorded

The teammate's no-Prism suggestion was treated as a draft hypothesis and compared explicitly. Current primary evidence from the [rendered ladder](https://2026a.battlecode.co.uk/game/ladder), observed **17 October 2026, 16:23 UTC**, shows Cassi & Issac as a common core among the current top four:

| Team | Cassi & Issac | Other displayed leaders | Window |
|---|---:|---|---|
| Intercontinental Fish | 50 | Stellar 50, Ren 48 | Last 50 completed games |
| Sneaky Bush Campers | 34 | Stellar 50, Ren 37 | Last 50 completed games |
| Mite | 50 | Stellar 43, Ryth 37 | Last 50 completed games |
| Nyxius | 50 | Stellar 47, Ren 45 | Last 50 completed games |

These are the ladder's displayed pick frequencies, transcribed from its rendered accessibility image labels at the stated observation time, not complete drafts or proof of champion causality. Saved earlier head-to-head examples also include Prism, so “strong teams never pick Prism” is not supported.

Two narrow variants replace Prism with **Cassi & Issac** or **Willow**, after geometry recipes have chosen preferences. The final discovered-choice fallback also excludes Prism, so an unavailable replacement cannot silently reintroduce it. Other preferences retain their order and duplicate choices are removed normally. For the default five-pick short-path recipe, the Cassi variant becomes **Ryth → Stellar → Cassi & Issac → Ren → Tavi**. Existing non-Prism geometry recipes remain intact.

**Cassi & Issac create two physical bodies.** A five-pick composition containing the pair has six bodies. v59 reserves byte 4 for the sixth packed claim and deliberately disables semantic alerts for six-body teams. The selected variant preserves that fallback; it does **not** claim to preserve active semantic alerts on six-body rosters. This comparison changes both team capability and communication availability. The eight-byte protocol is not redesigned in this change.

## Final v2 validation

The retained candidate is `v59-swap-cassi-v2`. Results for v1 below cannot be claimed for this distinct final source. The native mechanism checks pass for the integrated v2 repair on both diagnosed episodes: `gen47` side A **1006–832**, and `monolith` side B **1032–988**. Final side-swapped panels against the exact references and matched sparring bots are recorded in the [frozen panel summary](I032-diagnosis-evidence/final-v2-summary.json).

| Final comparison | Map set | Wins–losses |
|---|---|---:|
| Previous combination vs exact original | 12 targeted maps, both sides | 6–18 |
| Repaired old combination v2 vs exact original | Same 12 maps, both sides | 11–13 |
| Validated-cache v2 retaining Prism vs supplied v59 | Same 12 maps, both sides | 13–11 |
| Selected v59 Cassi v2 vs supplied v59 | Same 12 maps, both sides | 14–10 |
| Validated-cache v2 retaining Prism vs supplied v59 | 24 separate developer maps, both sides | 24–24 |
| Selected v59 Cassi v2 vs supplied v59 | Same separate 24 maps, both sides | 25–23 |
| Willow v2 vs supplied v59 | Same separate 24 maps, both sides | 22–26 |
| Cassi v2 vs Willow v2 | 14 Prism-relevant maps, both sides | 17–11 |
| Cassi v2 vs validated-cache v2 retaining Prism | Same 14 maps, both sides | 16–12 |
| Selected v59 Cassi v2 vs three matched sparring bots | Preselected six-map set, both sides per opponent | 34–2 |
| Raw v59 control vs the same three sparring bots | Same maps, sides and opponents | 36–0 |

**The final result is mixed and does not establish an upgrade.** The selected candidate has only a small lead against raw v59 on the separate set, the modest draft comparisons remain inconclusive, and it loses two sparring games that raw v59 wins. Across those matched 36-game sparring panels the candidate records **624 fuel-exhaustion events versus 343 for raw v59**. These are raw team-event counts, not body-turn-normalized rates: Cassi can add a body and match duration differs. The increased budget burden remains a material regression to investigate, not a passed performance check.

The [integrity audit](I032-diagnosis-evidence/integrity.json) accepts 428 unique physical games in the final ledger, including explicitly labelled reference comparators and mechanism checks; reused panel slots are counted separately from unique streams. The completed listed panels have **zero native bot faults**. Fuel exhaustion is nonzero, and selectively printed caught SDK errors remain present, including in the supplied references. None of those categories is silently treated as equivalent to a clean runtime or as proof of playing strength.

### Historical exploratory v1 comparisons

| Comparison | Map set | Wins–losses |
|---|---|---:|
| Previous combination vs exact original | 12 targeted maps, both sides | 6–18 |
| First integrated repair (v1) of old combination vs exact original | Same 12 maps, both sides | 11–13 |
| v59 scouting repairs vs supplied v59 | Same 12 maps, both sides | 14–10 |
| v59 + validated deferred cache vs supplied v59 | Same 12 maps, both sides | 14–10 |
| v59 + validated deferred cache vs supplied v59 | 24 separate developer maps, both sides | 25–23 |
| Cassi candidate vs supplied v59 | Same separate 24 maps, both sides | 26–22 |
| Willow candidate vs supplied v59 | Same separate 24 maps, both sides | 22–26 |
| Cassi candidate vs Willow candidate | 14 Prism-relevant maps, both sides | 20–8 |
| Cassi candidate vs validated v59 retaining Prism | Same 14 maps, both sides | 15–13 |

The targeted set consists of eight diagnosed/losing cases and four geometry controls. It is deliberately useful for regression diagnosis and is not an unseen strength gate. The separate 24-map set was selected by SHA-256 order before candidate results and is content-disjoint from the earlier 97-map evaluation. It comes from a historical developer pool and must not be called globally unseen. The 14-map draft panel was selected for relevance to Prism recipes. Panels and variants are correlated.

The exploratory Cassi variant had the more encouraging bounded comparison, particularly against Willow, but **26–22 and 15–13 do not establish a reliable general advantage**. They helped select which draft hypothesis to retain for v2 validation; they are not v2 results. The [exploratory v1 summary](I032-diagnosis-evidence/exploratory-v1-summary.json) remains separate from the final ledger. Native bot faults, inherited fuel exhaustion and selectively printed caught SDK errors are separate measures. Passing mechanism tests does not mean every match has no fuel or SDK error events.

## Verification and maintenance boundaries

- Port verification compiled full production translation units against SDK 2.2.5 for all four memory/anchor combinations. Actual-header fixtures cover malformed/short caches, transactional publication, bounded snapshot ownership, low-reserve deferral, exactly-once completion and anchor spacing. The final exact 13-file source additionally passes a full SDK translation-unit compile and nine portable mechanism fixtures, recorded in [test-results.json](I032-diagnosis-evidence/test-results.json).
- Actual production claim/alert code is exercised with narrow shared-memory mocks: alerts write only bytes 4/7, preserve claims and lifecycle bytes 5/6, claim updates preserve active alerts on up-to-five-body rosters, and six-body teams keep the sixth claim while disabling alerts. Pending cache validation cannot publish partial planner geometry.
- Independent legacy tribute/recall/flee/late/family settings still apply immediately. During memory-port verification, selecting the original branches of its three integration blocks reproduced the entire corresponding scouting-repaired v59 `main.cpp`; no old channel state or policy is imported.
- Actual-source ward tests cover the supported visible-ward query and overlap scoring. Draft tests exercise the final preference/filter/order logic, unavailable replacements, duplicate prevention and all three swap settings, with full production compilation.
- Native replay checks bind actor, round, command kind, coordinates, archive hashes and the selected before/after opening commands. The argument-driven [portable runner and fixtures](I032-diagnosis-evidence/tests.zip) accompany their JSON results; mock mechanisms establish implementation behavior, not native cost or competitive strength. The [candidate source archive](I032-diagnosis-evidence/candidate-source.zip) and [source manifest](I032-diagnosis-evidence/source-manifest.json) pin the reviewed source, with files directly under `src/`.

The working priority remains **our own reachable game-winning delivery before enemy-denial activity**. The inherited finish helper already precedes combat decisions, but it sees exact globally submitted score plus self and **currently visible** allied bags. It cannot prove the contents of hidden allied inventories. No new global own-FINISH signal, denial policy or broad finish rewrite is implemented here; that coordination work remains separate while the teammate develops it. Quantized scouting alerts are not treated as exact inventories or proof of an enemy's live ability state.

No map-name-specific movement or draft patch, broad camp-damage rewrite, live activation, automatic merge or claimed full promotion-gate pass is included in this follow-up.
