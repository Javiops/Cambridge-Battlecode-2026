# Farming, capture, delivery and return — evidence and policy

**16 October 2026. Documentation and replay research; all new decision policies are Planned.** The outcome to optimize is a completed productive cycle: useful clear → preserved capture → actual personal receipt → safe conversion → useful next field action. A camp kill, recall command or arrival at home is only an intermediate event.

Start with the [single decision contract](cycle-decision-contract.md), then [08 farming/capture](08-farming-and-capture.md), [09 delivery/objectives](09-gems-and-objectives.md), [10 recall/return](10-recall-and-recovery.md), the [source comparison](cycle-source-audit.md), and [controlled timing checks](cycle-timing-current-002.md). Information, team commitments, legal combat and purchases retain the authorities already defined in 04/06/07/11.

## What changes in the intended tactic

| Decision | Evidence-backed problem/opportunity | Planned rule |
|---|---|---|
| Start or continue a camp | A damaged camp and nearby bodies do not establish a safe next response or ready help | Check actual legal contributions, monster/enemy reply, escape/control reserve and a viable collector before expenditure; recheck after each action |
| Kill versus collect | Clearers and recipients can differ; excess bodies dilute personal income or lose useful time | Keep an actual eligible holder through payout, release redundant bodies toward useful work, and make local handoff acyclic |
| Capture plus recall | Successful overlap exists, but Home changes departure and an enemy can reset another capture tile | Use verified phase/duration and supported continuity guards; actual replacement or payout-first when those guards are unavailable |
| Bank versus another camp | Another reward can delay or prevent conversion; current bag is not new income | Compare bank-now with one additional feasible reward followed by bank; keep the current bag exactly once and stop indefinite chaining |
| Recall and shop | Full HP recall can reposition productively; a long return can also consume the apparent benefit | Require a named survival/purchase/next-work benefit and include actual channel, heal, shop and return route cost |
| Use all tactics together | Current independent early branches can consume actions before the delivery/farm decision | One action-budget owner selects a mission, executes one compatible legal action, refreshes and continues or releases |
| Unseen tournament maps | A map label does not identify safe routes, capture continuity or delivery expense | Use geometry/resource/arrival features; keep unknowns explicit and test on untouched generated maps |

These rules are our proposed synthesis. Public replays reveal outcomes and actions, not private policy code, personal observations or counterfactual optimal decisions. Their association with top teams does not prove that copying a threshold causes wins.

## Corpus, identities and limits

The public [ladder](https://2026a.battlecode.co.uk/game/ladder) was fetched at **2026-10-16 12:39:47 UTC**; histories use a fixed **12:41:26.627 UTC** cutoff. “Top four” means the identities at that snapshot: **Sneaky Bush Campers, Intercontinental Fish, Univardisty of Shingtonwash and procless**. It is not a claim about their rank when an older game was played. All ten current identities, including new number ten Full Damage, were refreshed.

Complete histories with hashed prior-cache overlap identified **4,319 finished internal top-ten series**, including 310 between the current top four. Selection was made without reading outcomes: all top-four head-to-head game IDs plus the latest two game IDs per other unordered-pair/map/match-kind stratum. **3,580 selected source IDs** produced **2,588 distinct raw replay streams and unambiguous ordered external team pairs**, across 17 map labels. Repeated replay IDs with identical bytes are aliases, not extra independent games. No raw hash crossed conflicting external identities in this selection.

Replay headers and matching native engines separate **952 streams on patch 0.0.2** from **1,636 on 0.0.1**. There are **951 unique top-four H2H streams overall: 150 current-patch primary and 801 historical**. Never pool the patches to estimate a current timing or strategy. Existing traces were reused only when raw SHA and ordered external identities matched; all 530 missing traces were decoded successfully. Bundle CRC/raw/source binding checks report no acquisition errors.

The current-patch primary analysis additionally scans every native frame: **13,587,626 frames**, 12,331 personal-gem changes and 28,621 group-pair changes across the 150 H2H streams. This catches capture control lost during actor actions that phase-7-only sampling misses. The complete gem ledger supports a strictly defined clean receipt-to-bank subset rather than assuming fungible banked gems came from a particular camp.

Native reconstruction/resource conservation are checked per stream; API rounds/scores and champion counters are compared where available. The denominator audit records 2,188 public-summary source traces, 291 full-statistics and 109 legacy traces with the old API scope unrecorded; the refreshed canonical API has full statistics for 378 streams. Exact available-API-score conservation applies to 2,660 of 5,176 team-game rows, while native score-ledger conservation covers all 5,176. Missing public counters remain unavailable; final-summary agreement does not establish an unavailable damage/stat check. Personal visibility, exact guest fuel, private enemy actions/cooldowns and the causal effect of a tactic are outside these replay measures. Maps, sides, matchup, draft/roster size, duration and evolving opponent versions confound comparisons. Bodies and events within a game are correlated. There are no confidence claims based on treating every event as an independent trial.

The code reference is **`bots/study27-economy/src`**, freshly retrieved at main **`ba93427c94c344b0fade0757208c5e0eeeb88c41`**. All six bot files match the earlier immutable source pin; [line-bounded audit links](cycle-source-audit.md) therefore retain that existing pin. This does not confirm identity with screenshot live-v43 or a later upload. No bot source, ladder submission or competitive challenge was changed by this update.

## Current top-four head-to-head measurements

Primary current-top4 H2H: 150 distinct raw trajectories, 8640 exact capture payouts and 9057 recipient observations. 365/8640 (4.2%) payouts had multiple recipients. 627/8640 (7.3%) payouts included a recipient with no source-mapped camp damage since the previous payout; this is a role observation, not evidence of deliberate delegation.

Exact reward-available→payout lag is available for 8640/8640 payouts: median 7, IQR 6–9, p90 10 world rounds. Fixed-stage sampled lag is separately retained (n=8640); the two definitions must not be pooled.

The complete native group ledger contains 8787 waiting episodes, of which 8640 end in payout and 147 remain right-censored. It records 1251 control-to-neutral transitions and 0 direct side switches. These transitions do not establish intentional abandonment or its cause.

There are 5199 tribute start commands and 4723 exact score/bag-drop completions, banking 242024 gems in total. Start bag median 44; actual completed bank median 44. Start outcomes: {'completed_exact_score': 4723, 'death_before_completion': 110, 'superseded_by_next_start': 301, 'no_completion_before_trace_end': 65}. Uncompleted commands are not automatically failures.

Collection followups cover 9057 recipient observations, stopping at the next personal death or trace end. A next exact bank exists for 6399; its latency median is 30 rounds. This is an ordered event relation, not attribution of those banked gems to the receipt.

The complete personal-gem ledger identifies 3382 clean receipt→bank sequences: pre-receipt bag zero, no intervening personal gem delta or death, and an exact equal terminal bank with a linked tribute start. Their bank latency median is 17 rounds (IQR 11–31). This selected subset is not a general conversion-rate estimate.

Strict sampled recall→alive-spawn boundaries number 8038 (distinct streams 150). Of these, 7367 have a subsequent trace-confirmed field productive event before death, next recall or trace end: median spawn→event 21 rounds. Camp HP loss and enemy HP loss followups are separately reported (n=6461 and n=3472). Delayed spell damage is outside this narrow command-confirmed return measure.

| Current rank / team | H2H streams | Payouts / shared | Exact wait median / p90 | Tribute bag median | Banked completions / gems | Strict recall boundaries / return median |
|---|---:|---:|---:|---:|---:|---:|
| 1. Sneaky Bush Campers | 82 | 2053 / 279 | 7 / 10 | 44 | 1386 / 64557 | 2186 / 24 |
| 2. Intercontinental Fish | 71 | 2372 / 42 | 7 / 12 | 48 | 1039 / 60896 | 1948 / 18 |
| 3. Univardisty of Shingtonwash | 73 | 1992 / 17 | 7 / 13 | 44 | 1008 / 56790 | 1805 / 20 |
| 4. procless | 74 | 2223 / 27 | 6 / 10 | 36 | 1290 / 59781 | 2099 / 20 |

Each team table row is an observed event distribution within its own H2H appearances. Opponent, side, map, duration, roster size and policy version differ; these are not matched or causal performance estimates. Current rank belongs to the timestamped supplied ladder and is not rank at play.

Corpus: {'raw_streams': 2588, 'patch_0.0.2': 952, 'cohort_top4_vs_other_current_top10': 996, 'cohort_other_current_top10': 641, 'cohort_top4_h2h': 951, 'patch_0.0.1': 1636}; exact raw SHA deduplication; source/audit errors 0; independent ledger validation errors 0. Event tables keep patch 0.0.1 separate as historical sensitivity and preserve missing native/API counters.

The stage-join audit directly links **3,320 distinct exact bank events** with a prior collection receipt, a strict sampled recall→spawn boundary and a later actual field productive event. These banks share **2,810 distinct reset/return events**, so they are bank-level joins, not 3,320 independent complete cycles. Of the banks, 2,371 satisfy the clean single-receipt attribution, and 3,171 have mapped recipient camp HP loss on a linked group. There are 1,871 bank-before-recall and 1,449 recall-before-bank orders. Both orderings therefore occur in observed completed sequences; no universal ordering or optimality follows.

Historical sensitivity remains separate: the 801 patch-0.0.1 H2H streams and 150 primary streams both have sampled wait median 6 and tribute-start bag median 44; observed productive return medians are 19 versus 21 rounds. This is descriptive sensitivity with different opponents/versions/maps/exposure, not an estimated patch effect. Exact all-frame wait timing is available only for the 150 primary streams.

## Wider current-patch top-ten coverage

The following uses the selected current-top-ten internal sample, not just H2H among ranks 1–4. “Shared” is a payout with more than one actual recipient. A recipient who did no mapped camp damage is a role observation; it does not establish deliberate delegation. Actual cleared/captured/banked outcomes must be kept distinct.

| Snapshot rank / team | Current-patch streams | Payouts / shared | Tribute start bag median | Exact bank completions / gems |
|---|---:|---:|---:|---:|
| 1. Sneaky Bush Campers | 258 | 7037 / 975 | 44 | 4683 / 219272 |
| 2. Intercontinental Fish | 172 | 5881 / 99 | 48 | 2570 / 153034 |
| 3. Univardisty of Shingtonwash | 174 | 5429 / 66 | 44 | 2596 / 148080 |
| 4. procless | 182 | 5808 / 64 | 44 | 3286 / 155776 |
| 5. Mite | 240 | 9328 / 330 | 36 | 4744 / 193055 |
| 6. ❤️Quantom❤️ | 136 | 3939 / 68 | 48 | 1764 / 97283 |
| 7. Shawn | 201 | 5191 / 177 | 48 | 2379 / 146247 |
| 8. VeryGood | 251 | 5945 / 20 | 22 | 4413 / 189500 |
| 9. hello | 201 | 6095 / 38 | 44 | 2963 / 145478 |
| 10. Full Damage | 89 | 2267 / 56 | 36 | 1537 / 65180 |

These event counts are exposure and outcome descriptions, not an economy-strength ranking. High bank volume can reflect a long game or a particular roster/map. Choose per-stream/pair/side/geometry comparisons for later policy evaluation, and keep missing followup rather than silently excluding unfinished cycles.

### Champion work and income can differ

| Team / body | Body appearances / distinct streams | Share of that team's source-mapped camp HP loss | Share of that team's captured gems |
|---|---:|---:|---:|
| Intercontinental Fish / Ren | 66 / 66 | 12.2% | 25.9% |
| Intercontinental Fish / Stellar | 68 / 68 | 30.6% | 14.8% |
| Univardisty of Shingtonwash / Issac | 73 / 73 | 17.9% | 29.4% |

The shares use the team's whole primary-H2H exposure, including drafts where a listed body is absent; they do not normalize a matched composition or imply that work and income should be equal. Cassi and Issac are separate physical bodies. These resource/work differences support considering different local jobs, but do not recover a private assignment algorithm or prove one champion should always collect.

## What the completed cycles show

**Collection is a separate job.** In primary H2H, 8,275/8,640 payouts (95.8%) have a single actual recipient, while 5,085/8,640 (58.9%) include at least one mapped clear contributor who does not receive that payout. This is compatible with clearers leaving collection to another body, but the contribution window can include earlier failed clears, so it does not prove an assigned handoff. Sneaky shares 279/2,053 payouts (13.6%), whereas the other three share only 17–42 each; there is no single copying rule that fits every top team. Useful parallel work is possible: one body holds a finished group, another clears or protects, and different carriers bank separately. More bodies are justified when they change clear feasibility, contest outcome or a concrete purchase breakpoint; “everyone helps and everyone waits” is not automatically best. A lone unsupported collector can instead lose the bag. The specification names a collector before expenditure where evidence supports it, keeps the last real holder, and prices each helper's alternative.

**Overlap is valuable when it actually completes.** Several top-four sequences receive the camp reward immediately before recall relocation, then bank and resume work. This saves overlapping occupied time; it does not make the subsequent walking/shop/re-entry free. The adverse examples show interruption or loss after receipt. A successful command, an active recall and a capture reward are three different facts.

**Delivery precedes the scoreboard.** Bank-now can be correct before healing, or a protected recall can precede delivery; the viable ordering depends on route, HP, threats, channel timing and next useful action. Larger observed bags do not define an optimal threshold. A next tribute may contain multiple receipts or another gem source, so it cannot automatically be attributed back to the immediately preceding camp. Only the explicit clean ledger subset supports exact one-receipt conversion.

**Recovery should end at productive re-entry.** A return trip can enable survival, an installed upgrade or a better route. The first move outside spawn is not proof of return value: we separately measure actual camp HP loss, enemy HP loss and new collection. Long examples make the route cost visible even when the bank succeeds. Declining a fight may be correct; declining it while continuing to spend HP/casts on an unsafe camp can still be wrong.

## Eleven exact current-patch episodes

These deliberately selected examples came from the earlier 92-stream current-patch top-four subset; all their raw hashes are present with unambiguous identities in the refreshed 150-stream primary cohort. They illustrate successful and adverse outcomes, not their population frequency. Map names below locate evidence and never select the new policy. Native sequence/phase, body IDs, roster, group IDs, bags, score changes and source hashes are retained in the evidence archive. **57 recorded capture/submission event checks** agree with the independent trace/native reconstruction.

### 1. sneaky-packs-overlap — packs

[Public series](https://2026a.battlecode.co.uk/game/match-groups/26398c86-d35d-4038-b9f4-66de3e49be61), game `c55af396-08ca-4128-a37c-968ebd6e451d`, inspected rounds 50–110.

Sneaky Issac1 cleared group2 on r80, stood through capture start r81, and began a five-tick recall that same round at 670/995 HP with no gems.

At r86 capture phase7, the holder received 70 gold and 48 gems while recall timer was already zero. Recall relocation happened later in the same world round at phase14, followed by full 1185/1185 HP at phase13 after purchases increased maximum HP.

The 48-gem tribute started r90 and actually completed r95; bag48→0 and side0 score+48 agree. At r106 Issac directly dealt 68.5 camp HP loss, establishing productive return rather than arrival alone.

This body also dealt direct enemy damage during r54–57 in the bounded lead-in; this observed fighting precedes the capture/recall sequence and does not prove a priority rule.

### 2. uni-fragment-return — fragment

[Public series](https://2026a.battlecode.co.uk/game/match-groups/2cf8c837-254b-4f52-9c44-6c933e00eeb5), game `9702e344-a397-4e37-a9ab-3310c000264a`, inspected rounds 308–353.

Univardisty Issac6 killed the last camp in group1 r325; capture started r326 phase7 and recall started r326 phase10 at 295.4499816894531/1375 HP with an empty bag.

On r331, payout58 at phase7 preceded recall relocation at phase14 and full spawn recovery at phase13. The sampled next-round spawn arrival r332 is a one-round-late observation; exact native arrival is r331.

Tribute began r341 for six owner turn ends and completed r347: bag58→0, side1 score+58. Direct basic attack r349 input6309 dealt121.5 to enemy Ren1, from Issac position14,19 outside its spawn.

### 3. procless-fragment-recovery — fragment

[Public series](https://2026a.battlecode.co.uk/game/match-groups/2cf8c837-254b-4f52-9c44-6c933e00eeb5), game `9702e344-a397-4e37-a9ab-3310c000264a`, inspected rounds 762–820.

Procless had already made group1 reward available r771. Allied Issac1 left its capture region r776 with timer1, resetting to neutral; Stellar3 later became holder and capture restarted r784.

Stellar3 dealt518 direct enemy HP loss r778. At r784 it recalled on the capture region at83.70001220703125/1125 HP with zero gems.

At r789 phase7 it received250 gold and58 gems; later phase14 it relocated to spawn, and phase13 healed to1125. No death or inferred rescue is needed to establish this completed recovery.

Tribute801 completed807 with score+58; at816 direct cast input13581 caused1116 HP loss to opposing Issac6. The immediately adjacent prior tribute775 belongs to an earlier bag and must not be attributed to payout789.

### 4. fish-swirl-bank-first — swirl

[Public series](https://2026a.battlecode.co.uk/game/match-groups/9f3b7948-3e1f-491e-b884-a86b0cd096d6), game `24d776a8-2b1b-4703-b01b-5cdff42fb40f`, inspected rounds 72–133.

Fish Ren0 received360 gold and88 gems at group18 payout106, after ally Stellar1 made the camp reward available100.

Ren started tribute113 and completed122: bag88→0, side0 score+88. On the very next native action in the same round it began recall with430 gold, zero gems, and1000/1000 HP.

Recall completed127, purchases changed HP/maxHP, and Ren dealt212.5 camp HP loss by cast129. Full-HP recall here is observable; shopping/repositioning intent is not directly observed.

A Ren-owned spell step r98 caused two enemy HP losses while Ren was approaching the camp sequence; remote spell ownership is not proof of its personal vision of either recipient.

### 5. sneaky-swirl-split — swirl

[Public series](https://2026a.battlecode.co.uk/game/match-groups/26398c86-d35d-4038-b9f4-66de3e49be61), game `ce6d20c1-3694-402c-b2e9-70a0aeb71f03`, inspected rounds 338–408.

Sneaky Stellar1 made group18 reward available353; capture began359. Cassi2 began recall359 at359/700 HP, Stellar1 began recall362 at1074.60009765625/1125 HP.

Payout364 divided the camp into two actual personal receipts:180 gold+44 gems each. Cassi recall timer0 and Stellar timer3 were visible at payout; the two bodies did not accelerate the capture countdown.

Cassi relocated home later364 and healed700; Stellar relocated367 and healed1125. Separate tribute starts368/371 completed373/376 with two independent bag44→0 and side0 score+44 events.

Both bodies later caused camp HP loss, Cassi392 and Stellar404. This establishes two delivered shares and two returns, not a causal claim that sharing beat a single carrier.

### 6. procless-rows-cycle — rows

[Public series](https://2026a.battlecode.co.uk/game/match-groups/9c919cb3-8341-45a1-8bf1-6c5280b0d5cd), game `d2f8eca2-f754-48f1-9615-068507e064f9`, inspected rounds 1–90.

On rows, procless Varg8 recalled25 after group1 capture had started24. Payout29 supplied270 gold+66 gems with one recall tick still remaining.

Recall relocated30 and full recovery followed at turn end. Tribute started43 at35,34 targeting altar34,33 and completed50, with bag66→0 and side1 score+66.

Actual next work was r69 direct basic-attack HP loss95 to each of three group1 camps after their respawn; the next clear80 is also in the bounded trace. Body8 is procless, not Univardisty.

### 7. fish-pilgrimage-long-return — pilgrimage

[Public series](https://2026a.battlecode.co.uk/game/match-groups/3759dcd0-4c43-427a-b94d-b5fd9d499212), game `839b0f80-95e0-472b-9cd9-db592ebe09a2`, inspected rounds 633–765.

Fish Varg11 cleared group12 r662, collected780 gold+144 gems r668 at770/1200 HP, and began recall later668.

Recall arrived673 at48,1; purchases changed maxHP to1500, followed by full recovery at turn end. The first next-round spawn sample674 is later than native arrival.

Tribute did not start until730, and its15-countdown channel completed745 with side1 score+144. At762 direct basic attack dealt220 enemy HP loss from26,49.

This successful path still occupies94 world rounds from receipt668 to recorded productive return762. It is an example of travel/channel cost to measure, not proof that recall was the fastest route.

### 8. uni-fragment-adverse — fragment

[Public series](https://2026a.battlecode.co.uk/game/match-groups/2cf8c837-254b-4f52-9c44-6c933e00eeb5), game `9702e344-a397-4e37-a9ab-3310c000264a`, inspected rounds 49–92.

Univardisty Stellar4 left group1 capture at75 with timer3; it restarted79 and began recall at510/750 HP.

An enemy cast r83 input1676 interrupted recall at timer1; native channel1→0 and HP loss are visible. This recall command did not reach spawn.

Stellar nevertheless collected250 gold+58 gems r84 at220/750 HP. It died r89 carrying58 before any tribute completion. Payout and recall command do not establish secured score or recovery.

### 9. sneaky-eight-adverse — eight

[Public series](https://2026a.battlecode.co.uk/game/match-groups/1aebe41f-d873-4ac4-b6d6-2d8f30fcc23b), game `00971df3-7cb0-46de-9f7d-d4cb383b4613`, inspected rounds 115–153.

On eight, an opposing Tavi11 cast made camp3 reward available141. Sneaky Varg5 held the capture begun142 and collected180 gold+44 gems147 at542.5/1000 HP.

Varg basic attacks continued147,149,150, each causing65 enemy HP loss. It died in its own r150 basic-attack frame carrying44, with no tribute completion.

The step actor is Varg5 even though Varg dies in that step. Secondary/retaliation loss means actor identity must not be called the killer. This bounds an economic capture followed by adverse combat continuation without asserting why either bot chose it.

### 10. sneaky-lanes-parallel — lanes

[Public series](https://2026a.battlecode.co.uk/game/match-groups/37d0e240-9a4c-4c19-9fe7-d84dc6a5a963), game `a9e180f9-905b-46b4-b3be-0b6b6e845bc9`, inspected rounds 20–85.

Sneaky distributed five bodies across distinct lanes camps. Issac1/Stellar2/Tavi5/Cassi0/Willow3 each individually received24 gems from groups10/12/38/8/36 at rounds43/45/46/49/50 respectively.

All five actually completed their own24-gem tributes at rounds50/54/55/58/60. These are five separate score+24 and personal bag24→0 events, totaling120 permanent score, rather than five queued tribute commands.

Issac and Stellar were already doing actual camp HP loss again at56; Issac got a second24-gem camp receipt65 and banked it72; Tavi caused camp HP loss75. No recall was issued by these five in this bounded20–85 window.

Parallel participation is observed. The trace alone does not establish a central assignment algorithm or that each bot had full teammate position/vision information.

### 11. sneaky-corners-concession — corners

[Public series](https://2026a.battlecode.co.uk/game/match-groups/f77360d0-c17d-4175-93dc-99883a0a5a92), game `953c804b-a2eb-49a0-bc9e-5b792eddce9a`, inspected rounds 260–315.

Sneaky Cassi6 made group2 reward available266. Side1 capture starts270,272,277,284 repeatedly reset when that same holder moves off the region at270,273,280,287; later two resets occurred with capture timer2.

The r287 move34,37→35,38 reset team1,timer2 to neutral,timer0. This is a direct same-step capture state transition, not an inference from another body recalling.

Univardisty Tavi3 began side0 capture294 and received48 gems299. Tavi died carrying48 at301 before delivering, so enemy receipt was not permanent enemy score.

Sneaky Willow/Issac recalls277/285 occurred at37,33 and35,28 and are not the capture-holder departures. They must not be described as causing group2 loss merely because they co-occurred.

The corners concession is especially easy to overinterpret: the body physically leaving the capture region reset its progress; two nearby-in-time recalls belonged to remote bodies and did not cause that reset. The enemy recipient then died before banking. Do not equate conceded capture with permanent enemy score, or the actor executing a frame with the killer when retaliation/secondary effects also occur.

## Mechanics that the policy must respect

The separate [current-engine timing report](cycle-timing-current-002.md) contains **12 controlled cases / 97 passing assertions**, including real enemy movement, occupied-tile rejection and a real basic attack. This is a mechanics probe, not new bot matches or a comparison of policy strength.

Normal recall uses five owner-end ticks; Home uses three. Capture first establishes its progress, then decrements; in the uncontested fixture normal recall needs one prior hold interval, Home three. A multi-tile region can be contested through its unoccupied second tile while recall continues. The actual public camp-group state stays `reward_available` before setup, during progress and after reset, and has no audited capture owner/countdown query. The host replay timer is not a bot input. Damage can interrupt recall without removing the holder. An actual remaining channel time of zero can still mean pending completion at the next owner start.

The narrow Planned overlap exception uses a sole spawn tile, uninterrupted living presence, verified duration/hold, credible survival and a worthwhile return mission. Ordinary enemy movement into that occupied tile rejects. The Home-plus-single-tile combination is a mechanics-based inference requiring implementation coverage. Broader regions need supported contest/continuity bounds or a real replacement; payout-first is the uncertain-continuity fallback and can cost five/three owner intervals relative to successful overlap. It is explicitly not universally superior.

Tribute starts with duration `max(1, ceil(start_bag/10))`. In controlled cases, 22 newly captured gems join an already active tribute: 31→53 banks at its original four-tick completion, and 5→27 banks after its original one tick. No new duration is added. This is a geometry/timing opportunity, conditional on legal altar approach, holding continuity and the distinct tribute interruption rules. It does not justify starting an unsafe channel near every camp.

## Generalizing across geometry

Do not add one tactic per map. The static feature pass uses the official 0.0.2 engine's managed distance field on walls, holes, altars and the opposing spawn mask, with legal altar approach roots and original capture tiles. Four small distance/connectivity checks pass. Dynamic champions/camps, movement locks, spell readiness, forced displacement, personal visibility and enemy decisions are excluded: these are **static route lower bounds, not full action ETAs or combat reach**.

All 150 primary raw trajectories pass exact terrain SHA, dimensions and spawn-rectangle comparison against the corresponding static-field exemplar. Initial camp membership differs in 34 streams. Distances were therefore queried from the validated dense fields at each stream's actual initial camp-group tiles; the join does not assume a map label or group index fixes a camp layout. No primary receipt or strict recall was excluded for a missing field after this correction. Per-stream variant hashes, source trace paths and checks are in `current/geometry-bins.json`.

The fields exclude dynamic camps/champions, locks, move permissions and readiness. They describe a lower-bound static walk, not complete action ETA. Bin cuts are reference quartiles of unique map/side/group slots in the 17 supplied exemplars. Samples are correlated and selected; no map-policy coefficient or causal distance effect is estimated.

| Original group tiles → nearest legal altar approach, static walk | Clean exact receipt→bank events | Distinct streams | Median receipt→bank rounds |
|---|---:|---:|---:|
| ≤8 | 1,509 | 102 | 11 |
| (8,13] | 1,160 | 107 | 19 |
| (13,20] | 338 | 68 | 30 |
| >20 | 375 | 54 | 40 |

All 3,382 rows above have a complete native personal-gem ledger: bag zero before receipt, no intervening personal gem delta/death, and an exact equal terminal bank with a linked tribute. This is a selected clean subset, not a general conversion-rate estimate. The feature describes original group tiles, not the exact recipient tile or an attack firing position. In the broader mixed-bag followup panel, next banks are observed for 2,237/3,124, 2,180/2,603, 1,086/1,610 and 896/1,720 recipient observations respectively; their medians are 14, 28, 52 and 54 rounds. Those broader banks cannot be attributed to the individual camp receipt.

| Recall command position → own spawn, static walk | Strict sampled recall→spawn boundaries | Distinct streams | Available productive returns | Median spawn→productive-event rounds |
|---|---:|---:|---:|---:|
| ≤22 | 5,014 | 128 | 4,617 | 17 |
| (22,33] | 1,446 | 126 | 1,336 | 25 |
| (33,46] | 805 | 76 | 731 | 42 |
| >46 | 773 | 45 | 683 | 50 |

The second feature describes the location left at recall start, not the next field objective. It is descriptive context for observed reset/return sequences. The productive-event measure is an actual field attack/cast with same-frame camp/enemy HP loss or a capture receipt, observed before the next death, recall or trace end. Missing followups are retained in the boundary denominator. Return to camp HP loss and enemy HP loss are separately available in `current/geometry-bins.csv`.

Exact source hashes, valid-match counts, camp variants, thresholds, all 48 table rows and missingness are in `current/geometry-bins.json`. The 87 initially uncovered `corners` recipient observations were resolved by actual per-stream camp-tile queries; no camp layout was guessed.

| Feature | How it changes the candidate decision |
|---|---|
| Route cost from useful camp/capture tiles to a legal altar ring | Compare direct bank, one more reward then bank, and recall-assisted bank with actual channel ticks |
| Route from spawn to the next viable job | Charge re-entry; a saved recall tick can be small relative to a long return |
| Our and enemy arrival to this objective and its exits | Determine whether a clear/hold window needs help, protection, warning vision or abandonment |
| Capture-region tile count and actual continuous occupancy | One tile supports a narrower continuity proof; several tiles allow contest without removing us |
| Damaging versus harmless resources, reward mix, monolith-only gems | Change squad size, damage reserve, gold investment and where score can actually be produced |
| Chokes, alternative exits, obstacles and warning sight | Change legal action tiles, escape feasibility and whether a carrier can finish tribute |

For example, pilgrimage's 122-tile static opposing approach versus fragment's 22 and packs'25 distinguishes route scale, but does not by itself justify aggression or a bag target. Expanse has ten altars and lanes eighteen versus eight's one; candidate-specific altar access still matters more than total count. Rushbait_v2's opposing-spawn approach lower bound is zero because the spawn rectangles touch: treating that global number as immediate field combat would be misleading. Use objective-specific arrival and actionable reach instead. A square map can contain long disconnected routes; width/aspect alone is insufficient.

Geometry bins are descriptive sensitivity, not fitted policy coefficients. No “if map==…” rule is added. Later implementation must reserve unseen generated maps, keep the same feature definitions, and promote only after matched tests across opponent styles and both sides.

## Comparison with our source and implementation order

The [source audit](cycle-source-audit.md) links every material claim to immutable code and active flags. Existing strengths include walking-distance camp selection, local in-range monster targeting, reset mode2, a present-holder evacuation check, recall path pricing and walking-ring altar routing. These should be retained where compatible.

Material gaps are: claims/headcounts standing in for timely contribution; permissive camp-HP affordability rather than an enemy-aware reserve; the damaged-camp rally bypass; capture nomination before physical arrival; capture timeout/gain proxies; no public-score-driven finish; fixed bank/recall and named-map exceptions; same-turn pre-shop maximum HP; independent pre-sweep/support/kite/front branches before common arbitration; no typed accepted-versus-moved/rejected channel result; and no explicit priced useful return mission. This is a source comparison, not evidence every gap caused a particular loss.

Implement fresh state and action outcome semantics first, then common arbitration, local readiness/secure expenditure, collector continuity, one-reward delivery and priced recovery/re-entry. Preserve 04's personal-vision contract, 06's real commitments, 07's action legality and 11's purchase breakpoints. The first version adds no shared bytes: the existing eight are occupied and claims lack freshness; a richer team role/ETA protocol needs its own encoding/ownership/migration design.

Compare arbitration-only, cycle-only, guarded-overlap/fallback variants and useful combinations. Evaluate actual activations, completed banks, lost bags, capture resets, wasted clear damage/cooldowns, assembly/idle time, productive return, fuel and endgame completion. Use the same pinned engine/source on both sides, several sparring styles and development geometries, then untouched generated maps. The native viewer is unmetered and cannot prove guest-fuel safety. None of these Planned policies is a measured improvement yet.

## Evidence and reproduction

The [evidence archive](resource-cycle-evidence-2026-10-16.zip) and [external checksum manifest](resource-cycle-evidence-manifest-2026-10-16.json) contain cohort/source projections, raw/engine/source hashes, full-population aggregates and audits, primary event ledgers, all 150 thin native gem/group ledgers, eleven exact episode extracts and selected raw replays, geometry fields/fixtures, timing probes and scripts. The archive member manifest verifies each included byte; omitted full-population trace/event caches remain explicitly omitted to keep the publication bounded. Public replay bundles can be reacquired by the IDs/URLs in the source manifests.

The full population is reproducible from the acquisition scripts and public bundle references; exact raw-byte/header/ordered-team verification is required before reuse. Replay engines are the official CLI 2.2.2 embedded viewer binaries pinned by SHA, not assumed interchangeable patches. The current engine is `e123b59d9dea198762ab7a04db9b3cb6d06dfa991088e41c24750fc4cb88b947`; historical0.0.1 is `ce302dc6666ae43592f6936e572bc4baca92a345bff13ef7f986609ac666a0dc`. The research stores engine hashes rather than redistributing the binaries. See archive `REPRODUCTION.md` for environment variables, stages and metric definitions.

The archive contains no authentication material, private opponent source or new ladder challenges. [Official rules](https://2026a.battlecode.co.uk/game/docs) and [Bot API](https://2026a.battlecode.co.uk/game/api) govern legality; controlled observations and the cached-SDK audit make their scope explicit. This update changes the specification and evidence only.
