# Combat and micro research — 16 October 2026

[Tactics index](README.md) · [The resulting combat policy](07-combat-and-survival.md)

This research asks what strong opponents actually do in combat, which legal sequences our reference bot misses, and how to turn those observations into a coherent policy. Replay observations describe behavior; the proposed policy is our design. Neither establishes a private opponent algorithm or a measured improvement to our bot.

## Scope and source identity

The refreshed ladder was acquired on 16 October 2026 at 11:39 UTC, with match-history cutoff **11:41:43.755965 UTC**. Its first four teams were **Intercontinental Fish, Sneaky Bush Campers, Univardisty of Shingtonwash and procless**. The rest of this frozen top ten were Mite, hello, Shawn, Very Good, ❤️Quantom❤️ and geese geese go. These are acquisition-time ranks, not historical ranks at the time each game was played.

All ten public histories were paged to completion. Selection includes every available finished game between the current first four, plus the latest two game IDs in each other current-top-ten unordered pair/map/match-kind stratum. Selection does not depend on wins or a visually attractive fight. There are 3,422 selected game IDs, **2,498 distinct raw replay streams**, 17 maps and 893 distinct top-four head-to-head streams. Repeated IDs pointing to the exact same raw trajectory are one observational unit, not extra independent games. Results below distinguish chronology, patch, map, roster and champion kit.

The compatible official engine is selected from the replay header's three version bytes, independently checked against the API patch when supplied: **1,768 streams use 0.0.1 and 730 use 0.0.2**. The 893 current-ranked top-four head-to-head streams split into **801 older-patch and 92 current-patch** streams. Both engines came from the official PyPI `cambc 2.2.2` embedded visualiser. Their SHA-256 identifiers are in the evidence manifest. A changed patch is not silently pooled into a current-mechanics claim.

The source comparison uses [`dee0fe7bf464d9f7b281af81f9650135fc541321`](https://github.com/Javiops/Cambridge-Battlecode-2026/commit/dee0fe7bf464d9f7b281af81f9650135fc541321), `bots/study27-economy/src`. All six source files match the earlier `a0c0fa2` reference byte for byte. The uploaded live-v43 source identity remains unconfirmed; public opponent version fields do not establish a version match either. Source omissions are therefore reported as omissions in this reference, not as proven causes of a particular recent loss.

### What can and cannot be measured

Native replays are reconstructed sequentially, retaining owner starts, commands, positions, HP changes, deaths, capture transitions and submitted score. Full-statistics API responses are checked against final champion counters when present; newer public summaries supply round, score and draft checks where populated. Native roster/death-counter reconciliation remains available when full API counters are absent. Missing public counters stay missing.

A **contact start** means a living body outside its own spawn with a living field enemy within Chebyshev six at that body's owner-turn start. It is geometric exposure, not proof of visibility, range, a ready cast, a legal path, or an opportunity deliberately declined. Command-frame enemy HP loss can contain splash, returned effects or linked death. It is an effect association, not the private chosen primary target.

Recipient persistence asks whether the same actor has overlapping opposing HP-loss recipients in consecutive world rounds in which it has such recipients. Shared-recipient pressure asks whether multiple same-team actors affect at least one common opposing recipient in a world round. The strict sensitivity excludes both terminal Cassi/Issac recipients when the pair dies in the same frame, because these compact traces cannot identify which partner was directly struck. Neither metric proves communication, good focus or causation.

Action-order fractions condition on field owner-turns that actually contain both listed actions. Compare champion/ability classes before generalizing: a dash followed by movement is different from movement followed by an offensive cast; a ranged attack reset creates a particular movement/attack exception. Control-class casts are not all control effects: Marcella's enhanced reset basic is a separate example. HP-only totals miss shield absorption and healing.

## Measured opponent behavior

### Current patch: the first four against each other

This primary comparison uses **92 unique 0.0.2 trajectories**. Each stream contributes two team observations; the per-team stream counts below overlap accordingly. Long games and repeated body turns are not independent samples. Fractions describe their stated exposure, not a causal ranking of micro quality.

| Team | Streams | Ordinary move / contact starts | Cast / contact starts | Strict recipient persistence | Strict shared recipient / multi-actor rounds |
| --- | --- | --- | --- | --- | --- |
| Intercontinental Fish | 41 | 19,537/29,481 (66.27%) | 4,445/29,481 (15.08%) | 1,588/1,699 (93.47%) | 589/700 (84.14%) |
| Sneaky Bush Campers | 47 | 18,964/30,925 (61.32%) | 4,126/30,925 (13.34%) | 1,445/1,562 (92.51%) | 330/467 (70.66%) |
| Univardisty of Shingtonwash | 45 | 22,320/29,544 (75.55%) | 3,936/29,544 (13.32%) | 1,109/1,154 (96.10%) | 358/433 (82.68%) |
| procless | 51 | 13,555/22,501 (60.24%) | 3,355/22,501 (14.91%) | 1,355/1,420 (95.42%) | 213/295 (72.20%) |

**Interpretation:** Repeated recipient pressure is common in all four, even after removing ambiguous paired terminal deaths. This is compatible with maintaining a feasible focus, but can also arise from proximity, target availability and persistent fights. It does not prove shared intent or establish why a team wins. The rest of the top ten also show high persistence; this is a common pattern, not a unique first-place technique.

- **Fish:** Recorded movement at contact occurs on 66.27% of starts and casts on 15.08%. Its strict shared-recipient fraction is 589/700. This is observable overlap, not evidence that it always sends the whole team to one target.
- **Sneaky:** It has fewer recorded ordinary-move/contact starts than Fish or Univardisty, while 671 contact starts contain a reset-class cast and 61 contain a heal. Its ranged offensive-cast ordering differs sharply from Univardisty; draft, legal slot behavior and target availability matter.
- **Univardisty:** It records ordinary movement on 75.55% of contact starts, the largest of these four in this slice, and strict recipient overlap 1109/1154. This does not by itself establish successful kiting: the movement can approach, rotate, retreat or make a legal action possible.
- **procless:** It records ordinary movement on 60.24% of contact starts and dash-class casts on711/22501 starts. The current Varg episode demonstrates a move/reset/basic trade with splash, but also an allied death afterward. A valid burst mechanism is not proof that the whole exchange was safe.

### Cast competition and kit-specific sequencing

Contact class counts below retain the same geometric denominator as above. They describe a recorded ability class during contact, not the intended recipient or a completed save. A cast can still affect a camp. A zero count can reflect the draft; it is not proof that a team neglected a useful heal or shield.

| Team | Damage/CC cast turns | Reset cast turns | Dash cast turns | Heal cast turns | Shield cast turns |
| --- | --- | --- | --- | --- | --- |
| Intercontinental Fish | 3,070/29,481 (10.41%) | 519 | 681 | 0 | 175 |
| Sneaky Bush Campers | 2,639/30,925 (8.53%) | 671 | 536 | 61 | 219 |
| Univardisty of Shingtonwash | 2,505/29,544 (8.48%) | 531 | 516 | 0 | 384 |
| procless | 1,844/22,501 (8.20%) | 499 | 711 | 0 | 301 |

The next table shows eight selected champions, pooling the four teams only after conditioning on the champion. Prism (13 body appearances) and Vendetta (5) remain in the full CSVs. **Field turns include farming**; these are sequence-coverage observations, not counts of PvP opportunities or successful combat trades. Body appearances count one champion body on one team side in one stream, not independent games.

| Champion | Body appearances | Move+basic turns; move before basic | Multiple-basic turns with a reset cast | Move before damage/CC cast / turns containing both |
| --- | --- | --- | --- | --- |
| Cassi | 174 | 0; 0 | 0/0 | 960/1,737 (55.27%) |
| Issac | 174 | 4,696; 3,412 | 3,364/3,364 | 0/0 (unavailable) |
| Stellar | 181 | 0; 0 | 0/0 | 0/0 (unavailable) |
| Ren | 135 | 4,211; 3,131 | 0/0 | 0/0 (unavailable) |
| Tavi | 84 | 634; 634 | 1,343/1,343 | 0/0 (unavailable) |
| Ryth | 75 | 1,641; 1,145 | 1,265/1,265 | 0/0 (unavailable) |
| Varg | 125 | 3,219; 2,176 | 2,094/2,094 | 0/0 (unavailable) |
| Willow | 8 | 0; 0 | 140/140 | 0/0 (unavailable) |

The **634 Tavi move+basic turns are all move-first**, whereas ordinary movement followed by an unassisted ranged basic is illegal in the current controlled Tavi fixture. Slot 0 reset restores the attack, but does not restore movement. This is a concrete sequence our generic post-first-hit reset helper does not deliberately construct. The separate exact episodes establish real PvP uses; the aggregate count alone does not.

Cassi has both movement/offensive-cast orders in the pooled data; Stellar has no field turn containing both an ordinary move and a damage/CC cast in this slice. These observations, the kit metadata and controlled action checks argue against a single order for all ranged champions. They do not establish that every absence was a missed opportunity.

### All ten: current-patch context

The 730 current-patch trajectories include the broader top-ten panel. Their opponent/map mixes differ from the leader-only slice. High recipient persistence appears throughout this panel; raw rates cannot isolate a superior focus algorithm.

| Team | Streams | Move / contact starts | Strict recipient persistence | Strict shared recipient / multi-actor rounds |
| --- | --- | --- | --- | --- |
| Intercontinental Fish | 135 | 56,364/84,365 (66.81%) | 4,896/5,324 (91.96%) | 1,874/2,224 (84.26%) |
| Sneaky Bush Campers | 151 | 55,506/88,982 (62.38%) | 4,606/4,937 (93.30%) | 1,225/1,615 (75.85%) |
| Univardisty of Shingtonwash | 138 | 66,828/90,882 (73.53%) | 3,772/3,962 (95.20%) | 1,222/1,498 (81.58%) |
| procless | 131 | 37,360/63,561 (58.78%) | 4,583/4,785 (95.78%) | 730/988 (73.89%) |
| Mite | 163 | 59,244/93,041 (63.68%) | 4,330/4,647 (93.18%) | 1,358/1,638 (82.91%) |
| hello | 118 | 64,632/96,970 (66.65%) | 8,691/9,466 (91.81%) | 2,790/3,331 (83.76%) |
| Shawn | 173 | 81,255/128,196 (63.38%) | 7,313/7,895 (92.63%) | 2,754/3,308 (83.25%) |
| VeryGood | 222 | 94,945/157,417 (60.31%) | 6,304/6,699 (94.10%) | 2,468/2,842 (86.84%) |
| ❤️Quantom❤️ | 106 | 33,996/52,686 (64.53%) | 4,566/4,801 (95.11%) | 823/1,089 (75.57%) |
| geese geese go | 123 | 45,139/69,267 (65.17%) | 5,887/6,250 (94.19%) | 1,702/2,131 (79.87%) |

### Chronology, early encounters and map sensitivity

Latest-two-per-pair/map/kind and available R25–150 windows are reported separately. The latest current-patch slice contains 91 of these 92 streams, so it is a highly overlapping sensitivity, not independent temporal replication. The early window reduces the influence of very long late-game repetitions, but it is a different conditional sample and may end at game completion. A bot version change is not known merely from chronology.

| Team | Full-game strict persistence | Latest-two strict persistence | R25–150 strict persistence |
| --- | --- | --- | --- |
| Intercontinental Fish | 1,588/1,699 (93.47%) | 1,485/1,589 (93.46%) | 324/346 (93.64%) |
| Sneaky Bush Campers | 1,445/1,562 (92.51%) | 1,362/1,472 (92.53%) | 271/311 (87.14%) |
| Univardisty of Shingtonwash | 1,109/1,154 (96.10%) | 1,109/1,154 (96.10%) | 208/222 (93.69%) |
| procless | 1,355/1,420 (95.42%) | 1,355/1,420 (95.42%) | 257/274 (93.80%) |

Per-map counts are often small even though the action logs are large. Selected coverage examples below are **not a map ranking or recommended aggression setting**. A contact-free game does not validate combat performance. Full 17-map tables and per-champion/per-map slices are retained in the evidence package.

| Map | Unique leader H2H streams | Summed geometric contact starts | Why the denominator matters |
| --- | --- | --- | --- |
| contest | 6 | 31,963 | Long repeated exposures can dominate full-game counts. |
| corners | 7 | 12,615 | Separate approach and casting choices by kit and route. |
| expanse | 4 | 0 | These sampled leader games have no contact-six starts. |
| fragment | 6 | 8,663 | The exact current example contains separated fronts. |
| swirl | 4 | 6,657 | The exact current reset/splash exchange has adverse follow-through. |

The older-patch component is a historical sensitivity using the same current-ranked team identities, not evidence of current 0.0.2 mechanics. The full-cohort report preserves separate patch/engine columns and all-patch, current-patch, latest and early-window slices. No comparison here supplies a causal map-feature coefficient or an optimal distance threshold.

## Exact exchanges: useful mechanics and adverse continuations

These are deliberately mechanism-selected windows, not a success-rate sample. Round numbers, ordered native input IDs, raw/bundle hashes and selected frames are retained in the [evidence package](combat-evidence-2026-10-16.zip). The first ten examples are historical 0.0.1 context from the earlier frozen cohort; the final two bring the current fourth team and 0.0.2 into the exact comparison. An observed action establishes neither optimality nor private intent.

| Episode / patch | Map / source window | Exact observation and limit |
| --- | --- | --- |
|01 · 0.0.1 historical|[packs · R130–136](https://2026a.battlecode.co.uk/api/v1/matches/d44a2517-49ab-42f3-bb62-c791cf1d46a3/bundle)|Ren consumes a shield before HP falls; a legal area centre reaches a farther recipient. The pursued body survives the window.|
|02 · 0.0.1 historical|[interlock · R272–279](https://2026a.battlecode.co.uk/api/v1/matches/8bc79c59-04bf-4e79-bd5b-75314eade848/bundle)|Shared pressure is followed by a Cassi/Issac linked loss, then a later allied kill. A final kill alone hides the earlier cost.|
|03 · 0.0.1 historical|[corners · R24–30](https://2026a.battlecode.co.uk/api/v1/matches/f9f576b4-c0a0-42d0-b864-c160bf7e48ea/bundle)|Spell/basic sequences against Ren include returned HP loss; an initially low target survives until a later input.|
|04 · 0.0.1 historical|[corners · R18–24](https://2026a.battlecode.co.uk/api/v1/matches/c58b2e34-29f8-47ef-8e18-a0edc1dd6317/bundle)|Ranged move→reset→basic; exact stun refresh spans a victim owner start, and Willow heals 315 HP.|
|05 · 0.0.1 historical|[corners · R37–43](https://2026a.battlecode.co.uk/api/v1/matches/9c830c09-e7bf-4032-ad35-4cadfac6c49f/bundle)|Basic→reset→basic is observed; later Cassi/Issac linked deaths do not identify a private targeting algorithm.|
|06 · 0.0.1 historical|[lanes · R60–66](https://2026a.battlecode.co.uk/api/v1/matches/9f57b5a5-2065-4bb5-b134-70eceb78aee6/bundle)|A ranged body moves closer, resets and shoots; the later state remains a trade, not automatically successful kiting.|
|07 · 0.0.1 historical|[corners · R378–384](https://2026a.battlecode.co.uk/api/v1/matches/8dfb72d3-26f3-422a-ba5a-5311b4f3aa71/bundle)|Two bodies increase enemy separation while one subsequently collects 48 gems and begins recall.|
|08 · 0.0.1 historical|[corners · R39–47](https://2026a.battlecode.co.uk/api/v1/matches/fb3e09a7-5bd4-4f27-8a67-1bff71093f7c/bundle)|A 48-gem tribute completes before the same actor's following basic kills an enemy.|
|09 · 0.0.1 historical|[elkring · R50–57](https://2026a.battlecode.co.uk/api/v1/matches/42ad5cc9-154f-4630-90c6-d94c5638597b/bundle)|Four sequential basics share an HP-loss recipient, interleaved with other owner turns and a later linked death.|
|10 · 0.0.1 historical|[collision · R975–983](https://2026a.battlecode.co.uk/api/v1/matches/066ab413-964f-4546-b8e6-3a7f0ed667a9/bundle)|One area-command frame has two local deaths and a remote linked death; three deaths are not three direct hits.|
|11 · 0.0.2 current|[fragment · R282–290](https://2026a.battlecode.co.uk/api/v1/matches/cf45b81d-98a4-4e5b-a467-e5cca4222fb4/bundle)|Ren applies control on one front while an ally dies on another; local effect is not team-wide protection.|
|12 · 0.0.2 current|[swirl · R69–76](https://2026a.battlecode.co.uk/api/v1/matches/3b104605-4d6e-4082-9904-da5d2a699cd9/bundle)|Varg move→basic→reset→basic produces splash recipients without Ren return; a later allied death remains part of the exchange.|

### Controlled mechanics, checked on both patches

The same **27 controlled cases / 85 assertions** pass on the pinned 0.0.1 and official 0.0.2 engines. All retained bounded records and checks match exactly, excluding engine identity. These establish the listed possibilities, not equivalence of every mechanic, map or strategy.

| Mechanic | Bounded result | Micro consequence |
| --- | --- | --- |
| Ren return | Each eligible trigger returns 0.2 × Ren's effective Focus, not a fraction of the incoming hit. It still occurs when the triggering hit is fully shielded or kills Ren. | Price each additional eligible direct trigger, including lethal ones; use attacker mitigation/shields and the resulting survival state. |
| Ranged attack reset | Move→reset→basic succeeds; the reset restores attack rather than movement. | A useful reposition can still yield a shot, but a first basic does not promise a later walking escape. |
| Vendetta kill refresh | A kill refreshes cooldowns without refunding an already-used cast. A no-cast basic kill can leave a legal reset/follow-up on another target. | Distinguish cooldown readiness from remaining per-turn permission. Requery both. |
| Secondary effects | Varg splash, Ren return and a Cassi/Issac linked death can share the triggering command frame. | Separate directly affected footprint, self-cost and linked survival; do not count every recipient as an independently selected hit. |
| Shields/control/heals | Rich replay frames confirm shield consumption with zero HP loss, actual stun restrictions and a 315-HP heal. | Evaluate the effect and victim turn timing; damage totals or cast counts alone do not establish value. |

Two additional controlled 0.0.2 cases resolve an important boundary: Varg's basic aimed at Ren splashes Stellar and consumes 20 of Varg's shield through Ren's return; aiming at Stellar splashes Ren for the same 50 HP at each recipient but consumes no Varg shield. **Ren being a secondary splash recipient does not imply the direct-hit return trigger.** The two cases pass separately from the common 27-case suite. A forecast needs the actual effect/target semantics, not one return event for every HP-loss recipient.

### Why effect timing changes the decision

In historical packs episode 01, Ren's first two command frames consume Varg's shield **250→205→42.5** with no HP loss. The next basic removes the last 42.5 shield and only 2.5 HP; Stellar's following area spell then removes 140 HP. The recipient is five tiles from Stellar but the cast centre is four tiles away. A health-only metric misses the earlier contribution, while a unit-distance-only spell filter misses the legal footprint.

In historical corners episode 04, Cassi applies a stun at input 676; the victim's owner start occurs at 677. Tavi's later input 704 refreshes an existing duration-zero restriction to duration one and deals 220 HP; Willow's input 707 restores **315 HP**. Two control casts within one world round need not cover the same remaining victim action. A burst prediction that ignores the next heal, actual restriction expiry or owner order is incomplete.

Historical interlock episode 02 contains an adverse continuation: shared pressure leaves the opposing Ren alive, Issac and remote linked Cassi then die, and an allied Ryth only kills Ren afterward. The later kill does not erase the earlier linked loss or prove that the initial engage was wrong. Track the entire bounded exchange and resource continuation.

Historical corners episode 08 also shows that combat is not always the first valuable event: Stellar completes a **48-gem tribute** immediately before its following basic kills Willow. Preserve a useful channel whose timing is safe rather than treating every enemy sighting as a reason to cancel conversion.

## Comparison with our reference bot

| Decision | What the evidence supports | Reference source gap | Intended correction |
| --- | --- | --- | --- |
| First irreversible action | Movement, casts, support and resets compete for specific allowances; exact ordering matters. | Mode-three pre-sweep can cast before the emergency decision; `P_CASTSAFE=0`. | Decide escape/protection versus a stationary exchange before spending movement or the cast. |
| Strength | Observable actions, timing, shields, return damage and linked survival change a trade. | Nearby HP/count gates are not timely contribution; one threat sum can combine a reset double basic with another spell. | Compare a small set of genuinely legal sequences and credible replies. Do not count incompatible actions twice. |
| Focus | Several actors can repeatedly affect the same recipient; selected cases show actual sequential pressure. | Sweep, kite, front and fallback use different scores; `P_KITEFRONT=0` leaves the common-focus alternative inactive. | Keep a feasible short local focus with deterministic ties, requery after every accepted action, and allow required protection to override it. |
| Ranged reset | Move→reset→basic and basic→reset→basic are observed legal sequences in the relevant kits. | Generic reset is attempted only after a successful first basic leaves the original target alive. | Compare a reset that unlocks a useful first post-move basic; after a kill, consider another living target only if the cast/attack budget remains. |
| Cast allocation | Applied control, shield consumption and healing require effect/timing evidence, not just cast counts or HP damage. | Sweep likes two-target AoE; support takes an early low-HP shield or first sufficient heal; `P_SAVECC=0`. | Spend the cast on the action or life it preserves, the secured useful kill, or the useful damage window. Price the competing slot/reset. |
| Failed action | A rejected command achieves no intended outcome. | Disabled engage-fallback/failed-channel continuation can return after an attempted action. | Refresh the cause and continue with a bounded legal useful alternative. |
| Exit and pursuit | Distance increases can accompany recovery or collection; a late kill can coexist with earlier linked loss and resource transfer. | HP thresholds, approximate reach and NOCHASE are separate heuristics; no complete useful-action/exit budget. | Reassess the next useful action, incoming reply, bag, route and foregone objective; name the next task when leaving. |

The detailed source audit and immutable line links are included in the evidence package and beside each topic in [chapter 07](07-combat-and-survival.md). Disabled branches are not credited as implemented features. The team's supplied reports about hitting contested camps while spending health/cooldowns motivate the priority ordering; they are not an independently measured frequency of our current bot's failures.

## Our policy: mission, legal sequence, reply, refresh

1. **Name the useful result.** Survive, secure a valuable removal, interrupt, protect, collect or complete delivery. A nearby enemy does not automatically make a five-body fight the best task.
2. **Build a small kit-legal choice set.** Hold/cast/basic; basic/reset/basic; ranged move/reset/basic; melee move/basic; dash/basic; required protection; escape/control. Include actual remaining allowances and state. This is bounded local reasoning, not an unbounded multi-agent optimizer.
3. **Price the credible response.** Next actor order, ready control/burst, mitigation, shields, Ren return, Cassi/Issac linked survival, awake camps and a usable exit. Keep missing information explicit. A teammate only contributes if a useful action can arrive before the deadline.
4. **Choose the sequence with the useful result.** Compare survival and conversion, then damage/control. A protector can peel rather than adding unnecessary focus damage. A reset or two-target spell must earn the cast it consumes.
5. **Refresh after each accepted action.** Requery position, target, health/max health, relevant buffs, cooldowns and permissions available to this actor. A kill can refresh cooldowns without refunding a spent cast. A failed command triggers a remaining legal fallback, not the assumption that the result occurred.
6. **Stop at the result or hard abort.** Reconsider when the target dies, sight/route changes, support is late, or the reply becomes losing. Release the old focus and select actual productive work. Do not oscillate on small score changes while the commitment remains useful.

### Adapt by geometry and kit, not a map-name script

| Encounter feature | Tactical consequence |
| --- | --- |
| Narrow approach, walls or holes | Count legal landing/action tiles and arrival order. Stacked bodies can invite area damage and blocked exits; a radius headcount does not establish a firing line. |
| Open pursuit with ranged bodies | Compare stationary exclusive damage, cast-only reposition and the particular reset-shot exception. An approach-and-shot can be a trade rather than a successful kite. |
| Several entry routes or separated fronts | Keep a local contribution deadline. An ally fighting elsewhere is not present help; reserve protection for the actual threatened actor. |
| Valuable carrier or nearly complete altar/capture | Evaluate the deadline and converted score. Intercept, protect or finish the safe conversion instead of maximizing fight duration. |
| Farm pressure with enemies approaching | Do not spend the essential escape/control or health on another monster hit before resolving the credible champion threat. After declining the fight, do not resume the same unsafe farm. |
| Reset/dash-heavy versus stationary burst roster | Use separate legal sequence models. Aggregate move/cast percentages are draft-confounded and cannot select one universal order. |

These are conditional policies for unseen maps. The replay comparisons do not establish an optimal threshold, a fixed best composition, or a causal advantage of one map feature. The existing [vision](04-vision-and-information.md), [coordination](06-team-coordination.md) and [investment](11-shopping-and-investment.md) specifications remain the foundation.

## Implementation order and later validation

First add legal short-sequence coverage, fresh state and useful rejected-action fallback without changing shared memory. Then add survival/return-damage accounting before irreversible expenditure. Then unify local focus and role-aware protection. These changes interact: test the parts and their credible combinations later, rather than rejecting a whole design because one isolated part loses to an older bot.

Later implementation should record activation opportunities, chosen/failed sequences, actual contribution, cast competition, shield/control effects, deaths, bags and completed conversion. Use side-swapped diverse maps, suitable sparring styles and an untouched final set; stratify patch, roster and kit. Do not tune on private holdout maps or equate wins against our ancestor with an improved online strategy. No bot code, new competitive games or submission accompanies this research update.

## Evidence and reproduction

Download the [evidence package](combat-evidence-2026-10-16.zip) and [external provenance manifest](combat-evidence-manifest-2026-10-16.json). The archive contains all aggregate CSV slices, compact publication tables, full-cohort compressed body/team ledgers, canonical and source-ID manifests, decoder/analyzer scripts, selected raw replays, twelve exact episode extracts and native mechanics reports. Its member manifest binds sizes and hashes; the external manifest binds the completed ZIP without a recursive self-hash.

The complete native decode and independent aggregate reconciliation report zero errors. Validation coverage is **2,498/2,498 external round checks; 2,126/4,996 available side-score checks; 2,126/4,996 available side-draft checks; 3,296 external champion-counter bodies; and 25,443 native final-body death-counter checks**. The draft count includes legacy full-statistics draft-pick comparisons performed by the quant audit. Missing fields are not counted as validated. The 92 current-patch leader trajectories have populated public summary scores/drafts but no external champion damage counters.

A separate publication review independently checks 232 displayed numeric/regrouping/source facts, plus 74 bounded episode facts. These reviews do not independently reconstruct every native state or establish policy strength. The 27-case/85-assertion common engine suite and its small supplements retain separate denominators. Use the artifact hashes rather than a changing live page when reproducing the reported slice.

Public sources are the [official ladder](https://2026a.battlecode.co.uk/game/ladder), match pages/bundles linked per episode, [game rules](https://2026a.battlecode.co.uk/game/docs/agents), [Bot API](https://2026a.battlecode.co.uk/game/api) and [official CLI distribution](https://pypi.org/project/cambc/2.2.2/). Quantitative claims refer to the frozen acquisition rather than a changing live ranking. The raw replay streams remain downloadable from their original public bundle URLs.
