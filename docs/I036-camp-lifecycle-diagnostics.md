# I036 Camp lifecycle recall and escape diagnostics

**This follow-up remains diagnostic. I035's `v60-camp-roster-bound` stays selected for review; none of these experiments is promoted or recommended for upload.** Correct camp-state classification exposed an inherited unsafe-recall decision. Separately, concrete camp fatalities exposed a gap in global retreat routing. The resulting changes compile and pass their bound mechanism fixtures, but their native panels must be judged separately against the selected source and raw v59.

The triple `state-window-escape-v2` was the sole balanced confirmation candidate: one fixed 37-map panel against each of selected base and raw v59, 148 slots total. Its 20-map selected-base score remains 19–21. Mechanical coverage and the recorded sparring-budget result motivated that confirmation while retaining the benchmark weakness. Both confirmation panels are complete: 36–38 against selected base and 36–38 against raw v59. This confirmation did not demonstrate superiority over selected base. I035 remains selected; no source promotion or upload follows.

The [evidence ZIP](I036-camp-diagnostics-evidence.zip) contains the source archives, patches, frozen flags, actual C++ fixtures, validation reports, causal witnesses and native ledger. Paths named below are archive entries rather than separately published GitHub files.

## Concrete decisions

- **Stellar on Elkring, R106:** in saved postkill stream `fe217e50550de1525e5967e2fb87ae04e7a987d8f93f792103637feb02c9774e`, Stellar has 225/825 HP at `(27,20)`. Awake elk 1 `(26,23)` has 60 strength. Three personally visible native-legal northern tiles at y19 leave range 3, but homeward retreat walks south through y21–25. Camp phases 108–110 deal 60 each and R111 deals the remaining 45. This identifies a missed earlier escape, not a guaranteed rescue on the final lethal turn.
- **Ryth on compact, R185:** at 68.25 HP, actual `(9,7)→(9,8)` remains in overlapping wolf 20/elk 60 envelopes. The next camp phase deals 18+54 after mitigation and kills him. Legal `(8,8)` avoids the elk, retaining only the wolf exposure and equal recorded enemy distance. The R183 AoE also woke that elk; an alternate enemy-covering area excludes it, but no alternate cast was executed. Both own deaths enter global low-HP flee, so changing only combat `pv_out` would miss them.
- **Ren's first lifecycle divergence:** compact's candidate/control share 1,383 commands before Ren R59/input1404 recalls at `(12,12)` instead of yielding. The nearby damaged resource has 0 strength, so removing its false camp warning is correct. Visible Ryth at `(19,15)` can approach and interrupt. Ren loses 100 HP at R63 and arrives home at end R71; the control moves two tiles, recalls at R62 and arrives at R67. The exact pre-command enemy cooldown is3, versus 4 in the round-start snapshot. This local delay does not explain the final 182-gem score gap by itself.
- **Cassi's capture opportunity:** Elkring's first changed command follows 3,518 identical commands. Candidate Cassi recalls at R145 and arrives home R150; the control walks three turns to `(3,12)`, recalls at R149 and receives 36 gems/195 gold at the R153 group4 capture. Candidate recall is earlier and safe but misses that participation. Its final score is nevertheless 72 gems higher, so the local missed reward is not a complete match explanation.
- **Tavi's gratuitous tie:** escape v1 first changes Elkring R66 from `(26,12)` toward `(25,13)` instead of the original `(26,13)`. Both endpoints leave the elk envelope with equal reconstructed champion danger and home distance. Both streams subsequently take no camp damage, recall R68 and arrive R73. The new first step has no demonstrated immediate survival benefit. V2 follows the SDK's N,NE,E,SE,S,SW,W,NW order for residual ties; this corrects the observed tie, not every legacy route.

These exact native/API observations are retained under `causal/`. The recall-window follow-up also changes an earlier Issac decision at R34 after 837 identical commands. A visible moving-away Ryth with cooldown 1 still triggers its conservative window veto; both recalls complete unharmed, two rounds apart, while the window path collects 44 gems/180 gold at R40. Worlds already differ before Ren R59, so that new stream cannot be called a causal replay rescue of old Ren.

The later postkill-plus-escape native audit preserves the exact initial Stellar/Ryth prestates: 2,537 and 3,932 global commands match respectively. The intended escapes occur, but **both focal champions still die after re-entry**. Stellar takes the legal 0-envelope exit at R106, then homeward fallback returns into range R107; death moves R111→R113. Ryth takes the 20-envelope tile at R185, receives only 18 wolf damage at R186 and survives at 50.25 HP, then fallback moves into the 80-envelope tile; death moves R186→R187. The strict-lower selector cannot authorize 0→0 safe continuation or 20→20 equal-exposure continuation. These are concrete limits of the narrow patch. Three slots contain two distinct native patterns, and the cached postkill control also predates the roster-sentinel fix, so neither the improved final scores nor this comparison is presented as a one-flag causal strength ablation.

## Changes remain separate

`camp-state-guard` replaces only the existing nearby-camp HP-history proxy with visible current awake state and positive strength. It retains the original radius 4 and downstream uses. Failed/stale reads keep positive evidence or an exact old warning. Its per-camp round checks add measurable guest/API overhead.

`camp-state-batch` preserves that meaning with one begin/end owner-round guard for the entire nonempty collection. Failed members get the old predicate; an uncertain whole scan retains positive evidence or the complete old loop. Its actual-source off/on fixtures pass 22,951 assertions. Empty lists add no queries. The fixed-state official-SDK import proxy reduces round calls from 2N to 2: 24 nearby camps fall from 6,597 to 4,282 guest instructions/scan; 24 far camps from 4,412 to 2,217. One-camp scans are slightly dearer. These are guest instruction measurements with deterministic host responses, excluding official engine host charges; they do not attribute a native fuel regression.

`recall-window` gates only relaxed near-foe recall admission when original `safe` is false. It reuses already-read spell metadata/cooldowns and basic reach over five future enemy opportunities, conservatively rejecting incomplete/stale coverage. It adds no SDK reads. It is a possible-approach envelope, not pursuit prediction, terrain/dash simulation, capture-value policy or an ongoing-channel repair. Its bound fixtures pass 7,408 assertions.

`camp-escape`/`camp-escape-v2` act only in the low-HP global flee fallback. They preserve dash users and available melee hit ordering, use known visible awake raw camp envelopes, and consider at most 24 inputs/8 hazards/8 adjacent poses. Minimum existing champion danger comes first; lower camp exposure then home distance breaks ties. V2 batches round guards, removes redundant health checks because awake is living, and uses the official residual direction order. SDK/API count records and 58 enabled/2 disabled fixture cases are retained separately. A full-health awake camp can otherwise admit recall before the escape branch, so truthful lifecycle and escape have a verified admission dependency.

`state-window` and `state-window-escape-v2` are exact frozen compositions, with full-SDK off/on compilation, bound state/window/escape fixtures and 28 actual combined branch checks each. `postkill-escape-v2` is a different experiment: selected roster base plus the already validated postkill capture block and exact escape-v2, with **no lifecycle or recall-window feature**. Its four flag combinations pass the capture/escape fixtures. These are distinct sources and hypotheses.

## Native panels

|Candidate|Opponent|Set|Maps|Slots|Wins–losses|Fuel candidate / opponent|Records reused in earlier listed summaries|
|---|---|---|---:|---:|---:|---:|---:|
|camp-state-guard|camp-roster-bound|probe|2|4|2–2|31 / 16|0|
|camp-state-batch|camp-roster-bound|probe|2|4|2–2|33 / 30|0|
|camp-escape|camp-roster-bound|probe|2|4|1–3|24 / 27|0|
|camp-escape-v2|camp-roster-bound|probe|2|4|2–2|23 / 22|0|
|recall-window|diagnosis-v59|screen|20|40|22–18|177 / 265|0|
|recall-window|spar11|screen|6|12|12–0|98 / 41|0|
|recall-window|spar12|screen|6|12|12–0|187 / 70|0|
|recall-window|spar16|screen|6|12|12–0|105 / 48|0|
|recall-window|camp-roster-bound|probe|2|4|3–1|39 / 35|0|
|recall-window|camp-roster-bound|screen|20|40|20–20|237 / 222|4|
|state-window|diagnosis-v59|screen|20|40|26–14|179 / 292|0|
|state-window|spar11|screen|6|12|12–0|87 / 41|0|
|state-window|spar12|screen|6|12|12–0|142 / 72|0|
|state-window|spar16|screen|6|12|12–0|70 / 41|0|
|state-window|camp-roster-bound|screen|20|40|18–22|238 / 225|0|
|state-window-escape-v2|diagnosis-v59|holdout|37|74|36–38|40 / 62|0|
|state-window-escape-v2|diagnosis-v59|screen|20|40|25–15|159 / 247|0|
|state-window-escape-v2|spar11|screen|6|12|12–0|82 / 41|0|
|state-window-escape-v2|spar12|screen|6|12|12–0|132 / 68|0|
|state-window-escape-v2|spar16|screen|6|12|12–0|70 / 41|0|
|state-window-escape-v2|camp-roster-bound|holdout|37|74|36–38|39 / 26|0|
|state-window-escape-v2|camp-roster-bound|screen|20|40|19–21|234 / 217|0|
|postkill-escape-v2|diagnosis-v59|screen|20|40|21–19|162 / 277|0|
|postkill-escape-v2|spar11|screen|6|12|12–0|136 / 43|0|
|postkill-escape-v2|spar12|screen|6|12|12–0|142 / 68|0|
|postkill-escape-v2|spar16|screen|6|12|12–0|109 / 43|0|
|postkill-escape-v2|camp-roster-bound|screen|20|40|15–25|251 / 212|0|
|camp-roster-bound|diagnosis-v59|screen|20|40|15–25|163 / 287|0|
|camp-roster-bound|spar11|screen|6|12|12–0|92 / 44|0|
|camp-roster-bound|spar12|screen|6|12|12–0|112 / 58|0|
|camp-roster-bound|spar16|screen|6|12|12–0|98 / 44|0|
|camp-roster-bound|diagnosis-v59|holdout|37|74|31–43|28 / 68|0|

The ledger contains 632 experimental summary slots, 628 distinct record keys and 529 distinct native replay streams. Reused probe/screen slots are not independent additional games. The 150 selected-source control slots are separate. Each source/opponent/map manifest remains separately labeled; there is no pooled win rate across this table. Twenty-map diagnostics include known official/developer maps rather than sealed tournament-unseen maps; sparring uses its separate six-map panel. The ledger binds map, actual seed, both source/binary identities, statistics/replay/stdout hashes, fuel and caught-error markers.

All verified native faults are 0 for both teams. Caught SDK errors remain, including inherited invalid-target errors, and selective/truncated stdout is not a complete error census. Fuel events are native exhaustion counts, not alive-action-normalized rates or function-level costs. Neither a factual model correction nor a local fixture guarantees a stronger complete policy.

## Review boundary

The concentrated camp-damage model remains open: per-monster nearest victim/ties/visibility, awakened siblings, tank allocation, clear time, mitigation, arrival timing and retreat-before-lethal exposure are not solved by a Boolean lifecycle guard or a conservative escape envelope. The inherited optimistic sharing equations and separate farming engagement proxies remain unless explicitly changed by another source. No fine tuning or source promotion is performed by this export.

The planned snapshot is complete. No further runs, parameter iterations or combinations are planned for this follow-up. The builder reproduces saved evidence without running games or tests. The full final-source gate was not rerun for these unselected experiments; mechanism fixtures and SDK compilation are narrower checks. No online A/B or activation occurred. Only I035's selected source remains current here.
