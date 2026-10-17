# I033 follow-up v4: avoid copying the combat cohort

The previous `budget-v3` candidate was **not demonstrated stronger than supplied raw v59**: 65–63 over 128 games and 35–1 in the matched sparring panel, where raw v59 scored 36–0. Reviewing its remaining loss exposed avoidable copying of the cached allied-handle vector. The isolated v4 changes that ownership mechanism; it does not retune the draft or combat tactics.

**Final v4 results: 96–96 against raw v59 over 192 games, and 36–0 in the matched sparring panel. Competitive superiority over raw v59 is not demonstrated.** The source was frozen before a new 96-map validation; those contents are disjoint from the earlier 64-map set. V3 and v4 rates are kept separate. This is a draft review candidate, not an activation or upload recommendation. No online activation, online A/B or complete repository promotion gate is claimed.

## Exact source and inherited scope

The selected follow-up is `v60-cohort-view-v4`, 16 source files, release WASM `47d988a6219fce3d5fe4008e0d2becb2c5600f6c487d786c7e173f8438bb80da`. Against frozen v3 it changes only `combat_cohort.h` and an explicit `<memory>` include in `main.cpp`. All eight allied-list callers, four entry invalidators, protocol parameters and other production files remain unchanged.

The base retains Cassi & Issac as the no-Prism replacement, six-body semantic alerts, the alert memo, immutable identity cache and bounded defensive fallback. The earlier lethal-approach experiment is absent: it passed a narrow Ren counterexample fixture but scored 4–6 against budget-v2, so that tactical guard was not retained. This v4 does not claim to fix Ren's earlier R47 combat advance or redesign channeling/twin escort.

The separately supplied `mybot_v53_simw_all (2).zip` has SHA256 `e1d3c62d431b2dc15c9473cf2497f11ec6712868929b086959b29709f9687e05`, identical to the earlier `mybot_v53_simw_all.zip`. It is not an independent newer improvement that was transplanted. Supplied raw v59 remains the exact external reference from `battlecode_mate_all_wards_alerts_v2.zip`, SHA256 `9b8482af47f275a99d3e4d505495fdcc504b54957ca6db8b53ddcd16fe6bf081`.

## 1. The diagnosed v3 loss and what was actually established

V3 lost 882–1020 on `fresh-compact-open`, side B, against spar12. Saved controls won 1020–832 (fuel+alerts),1028–794 (budget-v2), and1006–758 (raw v59). Its first 764 global action records match budget-v2. At R31, input 785, Issac at `(23,6)` moves to `(24,7)` instead of `(24,6)`, before v3's first native fuel exhaustion at R44. The release replay does not reveal the private decision fuel/target/mode, so the exact movement gate remains unresolved. There is no stale-vision witness or proven chain from that first tile to the final defeat.

At a still-matching R25 state, v3 Cassi and Issac each have 1,562 less fuel than budget-v2. The cached vector is copied into the cache and again on return, even when the pipeline uses that list only once. This is real redundant work. In the resulting v3 game, three deaths lose 124 gems, including a low-HP Ren submission and Issac's coupled death with Cassi; those are inherited policy weaknesses, not all attributed to the cache.

## 2. Immutable ownership removes the copies

V4 moves the first successful SDK vector into an immutable shared owner. A move-only read-only `View` retains that owner and exposes const iteration; an uncached fallback owns its fresh vector directly. Cache hits copy only shared ownership, with no champion-handle/vector-element copies.

The same freshness rules remain: successful queries only, same world round, scope ends on return/exception, and entry to `basic_attack`, `cast_offense`, `step_towards` or `support_spells` invalidates the entire active scope chain. Dirty scopes query fresh lists and never re-cache. Live HP, position, items and cooldowns are still queried through the SDK.

Independent read-only reviews found no dangling range, mutable alias or nested invalidation gap. A temporary `View` lives through its range-for loop, and an outstanding view keeps its immutable list alive after invalidation or scope destruction. Already acquired lists are not refreshed magically after actions; all eight selected loops still finish before acting.

### Controlled actual-SDK cost

A guest-instruction benchmark uses the actual SDK champion objects with deterministic official host stubs, not mock tiny handles. The ordered output hashes agree.

| Reads in one scope | V3 copying cache | V4 immutable view | Saving |
|---|---:|---:|---:|
|First use only |6,357.870 |5,271.870 |1,086 |
|Five repeated reads |16,973.641 |9,655.641 |7,318 |

These are amortized guest-instruction fuel units in that controlled benchmark, **not official native match fuel**. V4 still costs approximately516 more than disabling the cache for a first-use-only scope; it is not advertised as zero overhead. The change removes a measured copying cost while retaining the repeated-read benefit.

### Saved native probe

The saved compact-map side B probe and v3 share the first 1,097 global actions. At R44, input 1118, v4 issues a normal end-turn for Ren while v3 records a fuel-exhaustion command in the same actor state. At the identical R25 world state, v4 restores 1,109/1,087 fuel for Cassi/Issac relative to v3. Five bodies have more reserve; Ren has 1,033 less, so this is not a claim that every full turn becomes cheaper. The probe wins against spar12 on both sides. These two targeted recoveries are mechanism checks, not a broad playing-strength estimate and not proof that one saved reserve value caused the win.

## 3. Inherited protocol and budget protections

The six-body protocol preserves six claims: up to 31 camp groups it uses five-bit claims and the full 16-bit scouting word;32–63 groups retain complete six-bit claims with a 12-bit coarse packet; above 63 groups the original nonpacked five-claim fallback has no new semantic six-body alerts. Lifecycle bytes 5/6 stay separate. Failed/suspended reads, low reserve and changed rounds abort publication; short timestamps need observed packet chronology, so unchanged stale packets do not revive on wrap. Compact reports have explicit coordinate uncertainty and are not promoted into the long-lived precise danger cache.

The earlier native ten-group trace demonstrates full-layout sharing: Tavi publishes in R24 and the other five bodies receive it in R25 while the sixth claim remains intact. Compact-layout support is established by actual-source fixtures, not by that ten-group trace. Shared scouting can convey only directly observed context; it cannot report the unseen Tavi that killed our Stellar during a saved R56 recall.

Alert classification memoization remains scoped to a read-only observation. The final six-body fixture matrix preserves semantic hash `6670136114993335834` across eight flag combinations, reducing stat queries 6,228→1,134 and spawn queries 2,940→756. The older pre-six-body matrix's 756 stat-query count is historical. Immutable identity caching and the bounded already-selected `back_off`/`pv_out` execution remain unchanged. The latter deliberately omits optional spells, resets and expensive reconstruction at low reserve, so it is a behavior change with explicit limits.

Caught SDK errors remain separate from native faults. Error 42 means an invalid attack target (`cambc.h:375` in SDK 2.2.5). Raw v59 and the candidate retain spell-then-basic flow with `P_U34_ATTACK_LIVE=0`; a target disappearing after the spell is a plausible inherited explanation, but captured markers do not identify each attempted target. No general error-free claim is made.

## 4. Final v4 validation

The table contains only frozen v4 source/build results. The 192 raw-v59 games use96 historical developer maps locked before this prototype's outcomes, each played on both physical sides. Their content hashes are disjoint from the earlier 64-map v3 set; these are not globally unseen tournament maps. The matched 36 sparring slots are a separate comparison. Neither v3's 65–63 outcome nor targeted diagnostic games are added to the v4 win rate.

The [228-game ledger](I033-budget-alerts-v4-evidence/final-games.csv) binds the exact source, WASM, CLI/SDK 2.2.5 and engine 0.0.3, map, actual seed, statistics/archive/raw-replay/stdout hashes and separate faults/fuel/error counts. [Paired map outcomes](I033-budget-alerts-v4-evidence/paired-map-outcomes.csv) retain both physical sides.

| Final v4 comparison | Maps / games | Wins–losses | Fuel candidate / opponent | Captured SDK-error markers candidate / opponent |
|---|---|---:|---:|---:|
|vs supplied raw v59 |96 maps /192 games |96–96 |80 /177 |2,606 /2,603 |
|vs spar11 |6 maps /12 games |12–0 |92 /44 |288 /346 |
|vs spar12 |Same 6 maps /12 games |12–0 |112 /58 |256 /320 |
|vs spar16 |Same 6 maps /12 games |12–0 |98 /44 |278 /349 |
|Matched sparring total |36 games |36–0 |302 /146 |822 /1,015 |

Native faults are **0 for both teams in all 228 final slots**. Caught SDK-error markers remain in every final game and are not native faults; stdout is selectively printed or truncatable, so captured counts are not complete SDK-error totals. The [error ledger](I033-budget-alerts-v4-evidence/caught-errors.json) retains the exact captured messages and maximum reported counters. The candidate is not advertised as error-free.

Against raw v59, 17 maps are won on both sides, 17 lost on both, and 62 split. The one-sided map-sign probability is 0.5679168798. Candidate/opponent potential completed body-rounds are 591,405/578,166, corresponding to 1.353/3.061 fuel events per 10,000 potential body-rounds. Those are coarse counts, not normalized by alive actions. Lower fuel exhaustion is a measured operational improvement in this sample, not a demonstrated win-rate gain.

### Historical matched controls — separate sources

| Source on the same 36 sparring slots | Wins–losses | Its own fuel events |
|---|---:|---:|
|Previous Cassi v2 |34–2 |624 |
|Fuel+alerts intermediate |36–0 |650 |
|Budget-v3 copying cohort |35–1 |427 |
|Supplied raw v59 |36–0 |343 |
|Current v4 immutable view |36–0 |302 |

These are 144 historical control slots, separate from the 228 final v4 games. Their own fuel totals must not be confused with the opponents' 146 fuel events in the final sparring panel. The [matched flip ledger](I033-budget-alerts-v4-evidence/matched-outcome-flips.csv) shows the former v3 compact-map side B spar12 loss changing to a win; all 35 formerly won slots remain wins. The two previous Cassi-v2 compact-map side A losses also become wins, but they share one native stream. These are descriptive matching-map/side comparisons with actual seed equality recorded.

The raw-v59 head-to-head panel contains 182 distinct native replay streams across 192 scheduled slots; the sparring panel contains 28 across 36. Across all 228 v4 slots there are 210 distinct native streams. Duplicates remain documented scheduled outcomes, not independent tactical discoveries.

### Source and mechanism verification

The [source manifest](I033-budget-alerts-v4-evidence/source-manifest.json) binds all 16 unchanged tested files and release WASM. The [v4 source-delta audit](I033-budget-alerts-v4-evidence/mechanisms/view-final-binding.json) confirms that only the cohort header and explicit memory include differ from v3, while all eight callers remain unchanged. [Actual-SDK cost evidence](I033-budget-alerts-v4-evidence/mechanisms/view-sdk-benchmark.json), [native same-state excerpts](I033-budget-alerts-v4-evidence/mechanisms/view-native-first-use.json) and the [lifetime review](I033-budget-alerts-v4-evidence/mechanisms/view-lifetime-review.json) retain their scope limits.

[Portable tests](I033-budget-alerts-v4-evidence/portable-tests.zip) compile the complete supplied translation unit against the real SDK and extract the actual current production snippets and cache headers. The [fresh v4 validation](I033-budget-alerts-v4-evidence/mechanisms/portable-v4-final-source-validation.json) covers all protocol, memo, identity/defense and cohort configurations, preserving source hashes. Historical v3/intermediate results are labeled separately. The [evidence ZIP](I033-budget-alerts-v4-evidence.zip) contains the portable ledger, exact source, 102 frozen maps, test package and focused mechanism reports; large native replay archives and executable binaries are omitted.

The newly received post-kill team archive is under separate inspection and is **not included in this frozen v4 source or validation**. A later transplant needs its own source binding and tests.

The implementation evidence supports the specific no-copy/freshness repair, and the matched sparring regression is recovered. **96–96 against raw v59 does not establish a stronger bot.** This is a user-authorized draft for team review, not an upload or activation recommendation. The complete repository promotion gate and online A/B have not been run.
