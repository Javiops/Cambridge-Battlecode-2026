# Shopping and resource investment

**Chapter 11 of 12** · [Tactics index](README.md)

How gold becomes useful power for each champion.

## Contents

1. [Purchase timing](#1-purchase-timing)
2. [Stat selection](#2-stat-selection)
3. [Emblem family selection](#3-emblem-family-selection)
4. [Purchase order](#4-purchase-order)
5. [Completion and stacking rules](#5-completion-and-stacking-rules)
6. [Consumable budgeting](#6-consumable-budgeting)
7. [Adaptive builds](#7-adaptive-builds)
8. [Shopping exceptions](#8-shopping-exceptions)

**Evidence and status.** These are **planned tactics**. The [shopping research](shopping-research-2026-10-16.md) separates official mechanics, confirmed elite transactions, our source audit and original proposals. An observed strong team's build is a candidate to test, not proof of an optimal order or a causal win-rate improvement. No bot code is changed by this chapter.

## 1. Purchase timing

Decide when spending accumulated gold improves performance enough to justify the interruption.

**Status:** Planned

**Tactic**

Separate **buying at an available shop** from **leaving a useful task to reach one**. Each body's gold is private, including Cassi and Issac. Current starting gold and passive gold income are zero; waiting alone will not fund the next shard. Spending does not reduce lifetime-earned-gold tiebreak credit.

| Trigger | Chosen action | Stop, exception or fallback |
|---|---|---|
| On own spawn (including after a needed return), or dead on an actionable owner turn | Buy affordable shards that improve the next mission, respecting a specifically justified consumable reserve. Component shards already grant stats; do not wait for all 150 gold if the components are useful now. | Re-read gold/inventory after each successful buy. Stop at the selected useful bundle, insufficient funds, a restriction, an action deadline or the fuel limit. Being dead permits shopping; it does not make the preceding death desirable. |
| Healthy in the field with spendable gold | First identify the affordable upgrade and its expected benefit before the next normal return. Compare it with recall time, walk back, missed capture/tribute and team absence. | Do not recall solely because a fixed gold amount or interval has been reached. Retain the current mission if the upgrade's benefit is unresolved or arrives too late. |
| Tavi can use an equipment purchase before the next action | Buy the relevant legal shard in the field, then recompute the action if its threshold changes. | Field Health raises maximum HP without healing current HP. Consumables and living equipment sales still require spawn. |
| A camp capture or deciding tribute is about to finish | Preserve its completion unless the survival/objective policy requires leaving. Include exact remaining capture phases in any recall plan. | Home-shortened recall can depart before capture completes; use the actual timers and phase order, not the old five-tick overlap assumption. |
| Little useful play remains before a deciding bank/end | Buy only an upgrade that can affect the remaining fight, escape, capture or tribute. | Skip elective trips and economy purchases whose benefit cannot be earned, spent and used in time. Do not impose one fixed round cutoff across maps. |

An elective trip uses **incremental cost**: required recall/spawn time plus travel to the next useful action and missed team opportunities, minus recovery/repositioning time already needed anyway. A purchase during a necessary heal can be cheap incrementally; a healthy remote farmer returning to the same region can pay heavily. Use walkable routes and actual movement abilities.

**Current behavior:** The audited cleaned study27 combat derivative at [`e72cec8`](https://github.com/Javiops/Cambridge-Battlecode-2026/commit/e72cec84391cf0623d15c2eb3f2f864e2b0bddea) uses fixed build overrides and healthy-shopping gates including 180 gold and 40-round spacing. It does not estimate a mission-specific upgrade/trip payoff. The [source audit](shopping-research-2026-10-16.md#our-existing-bot) describes the active branches; these planned rules require implementation.

**Related decisions:** [Recall](10-recall-and-recovery.md), [Farming and capture](08-farming-and-capture.md), [Gems and objectives](09-gems-and-objectives.md).

## 2. Stat selection

Choose Strength, Focus, or Health according to the champion's kit and current needs.

**Status:** Planned

**Tactic**

Choose the stat that changes the body's **next useful actions**, using current HP, actual attacks/casts, champion growth and kit coefficients. One stat point is champion-specific. Focus does not generally reduce cooldowns, increase stun duration or strengthen a dash/reset with no Focus coefficient.

| Body or role | Candidates to compare | Important qualification |
|---|---|---|
| Vendetta, Vesper Vale, Issac; basic-attack farming | Strength, with Health/mitigation when it permits another useful action or avoids a recall/death | Their reset/dash abilities have no direct Focus scaling. More theoretical Strength is wasted if no legal attack is reached. |
| Ryth | Strength versus Health plus its survival and bonus-Strength contribution | Ryth gains Strength equal to 1% of item bonus Health: his +100 Health growth also supplies +1 Strength. Count both effects. |
| Varg | Strength for basic/splash damage; Focus for a shield that will actually absorb useful damage; survival alternatives | Do not value the entire theoretical shield if it is not cast or absorbed. |
| Cassi, Stellar, Tavi | Focus for useful damaging casts; Health/mitigation for surviving to cast or disengage | Remaining cooldown, spell walking restrictions, range, target access and fight length constrain realized damage. |
| Prism | Focus versus survival under the relevant carried-gem state | Carried gems already add Focus; banking or losing them changes that bonus. Evaluate the next mission after the bag changes too. |
| Willow | Focus for effective healing, with survival and actual ally access | Exclude overheal and casts that cannot reach a wounded ally. |
| Ren | Strength for attack-heavy clear; Focus for spells and qualifying retaliation; survival | The best mix depends on hits taken, targets, cooldown and route. Do not infer one stat from his name alone. |
| Marcella | Strength versus damaging-spell Focus and survival | Focus increases the damaging effect, not the duration of the separate stun/reset. |

Prefer a credible survival/clear breakpoint over an unmeasured generic DPS ratio. A simple first comparator can ask whether an upgrade avoids a lethal sequence, removes one required attack/cast or prevents an incoming monster volley. A gain that does not cross such a threshold can still help; retain the established fallback when a small comparator cannot resolve the tradeoff.

**Validation required:** Actual stat deltas, Ryth's cross-stat bonus, Prism before/after banking, effective heal/shield use, and damage sequences rather than raw equipment points alone.

## 3. Emblem family selection

Compare farming damage, protection, income, recall speed, and raw-stat benefits.

**Status:** Planned

**Tactic**

Select a family for a specific remaining job. All shards cost 30 gold; five identical shards combine for 150 total with no extra fee. Check whether that family passive is already owned **in any stat variant**.

| Family | What completion provides | When it belongs in the comparison |
|---|---|---|
| Monster | Five chosen-stat growth points; ×1.1 damage to camps from attacks and damaging spells | A body will deal meaningful future camp damage. Count whether faster clearing saves actions, incoming damage or a contested window. |
| Jungle | Five chosen points; camp-source incoming damage ×0.7 | The body will actually tank damaging camps. Harmless gold/gem clusters and damage avoided entirely do not receive a sustain benefit. |
| Durability | Five chosen points; incoming damage ×0.9 | Relevant PvP/camp damage threatens a useful action or survival. It does not prevent stuns or protect an impossible position. |
| Power | Six chosen points, no passive | Repeated primary-stat scaling or a decisive completion threshold. The fifth shard adds two chosen points relative to four shards. |
| Bruiser | Five chosen points plus one of each other stat | Useful off-stat contributions outweigh the foregone extra primary point. Give unused stats zero value; one useful off-stat can still justify the comparison. |
| Treasure | Five chosen points; +20 percentage points to eligible personal base gold income | Sufficient future capture/kill income can produce useful extra purchases before the decisive period. Compare the foregone alternative passive/Power point, not a universal payback timer. Vesper's bonus adds: 1.2× base becomes 1.4×, not 1.44×. |
| Home | Five chosen points; normal five-end-turn recall becomes three | Future safe recalls save useful time after including walking and capture timing. Do not count two saved channel ticks if leaving early forfeits the camp. |

The first useful passive is a completion event; its loose shards have only their ordinary stats. A duplicate passive family provides no second multiplier, even with a different stat. After obtaining it, compare repeat stats with Power/Bruiser and other still-useful missing families. Do not enforce buying every family once.

Treasure's +20% creates about 150 extra gold from 750 future **base personal** earned gold, but this is a cash-generation horizon, not its actual break-even against another emblem: Treasure already bought five stat points. An alternative can accelerate income indirectly by clearing faster or surviving. Bonus fractions accumulate across awards; refunds are not earned income.

**Related decisions:** [Purchase order](#4-purchase-order), [Completion and stacking](#5-completion-and-stacking-rules), [Adaptive builds](#7-adaptive-builds).

## 4. Purchase order

Decide which early shards and completed emblems deliver the most useful immediate improvement.

**Status:** Planned

**Tactic**

Track the selected bundle, loose shards, first-copy family effects, remaining completion cost and intended next mission. Re-evaluate after a successful purchase or explicit completion, rather than buying an arbitrary long queue without reading the result.

For a first bounded prototype, compare at most three paths: the current role-build fallback, a useful partial-emblem completion, and one mission-relevant survival/farm alternative. Use this **untested starting priority**:

1. An affordable purchase changes a credible next survival/clear test from failing to passing.
2. Otherwise, a purchase removes a required action or incoming camp volley before the next normal return.
3. Otherwise, compare the next useful first-passive or Power/Bruiser completion with the fallback. Retain the fallback if the gain is unresolved.

A body holding four Jungle shards needs only 30 more gold to activate the passive. That is a different immediate option from spending 30 on the first shard of another family. Still allow switching if the next job changes: existing shards are useful stats, not a reason to finish an irrelevant passive at any cost.

Buy useful components at existing legal opportunities; there is no need to hoard 150 purely because completion occurs at five. Conversely, affordable does not mean relevant. Do not split an early budget among many passive families without accounting for the completions delayed. Keep the selected goal stable while the mission is unchanged, with explicit reasons for a switch.

**Stop/fallback:** Stop on a failed/restricted purchase, insufficient gold, named reserve, action deadline or fuel bound. A batch with insufficient gold fails as a whole; never assume it partly succeeded. Re-query the catalogue/state and use the legal fallback action instead of retrying indefinitely.

## 5. Completion and stacking rules

Account for five-shard completion thresholds, stacking stats, and non-stacking emblem passives.

**Status:** Planned

**Tactic**

Maintain two distinct summaries: total item-derived stat points and the set of active unique passive families. Include stats contained in duplicate emblems. Do not use LoL's six-slot inventory model; multiple emblems remain legal in the audited rules.

- Only five **identical family/stat shards** combine. Three Monster Strength plus two Monster Focus do not make one emblem.
- A completed Power item counts as six selected points; Bruiser as five selected plus one of both others. Re-read after automatic combination.
- Monster, Durability, Treasure, Jungle and Home effects apply once per family across all copies/stat variants.
- Durability and Jungle multiply: 100 raw camp damage becomes 90, 70, or **63** with both. Duplicate copies do not reduce it again.
- Ordinary shard prices and absolute growth do not deteriorate with more purchases. **Relative** growth falls as stats rise, duplicate passives saturate, and action-count thresholds create practical diminishing return. These are different effects.

For example, Ryth's ordinary +5 Strength is +10% from 50 and +5% from 100, at the same 30-gold cost. Evaluate whether another offensive point, Health, a useful unique passive or a completion affects the next real action more. There is no justified universal “stop after N Power emblems” rule.

**Validation required:** Inventory/stat accounting through combinations, duplicate families across stats, batch purchases, failed batches, and Tavi sales that remove an active passive.

## 6. Consumable budgeting

Decide when locks and teleport crystals are more valuable than permanent equipment.

**Status:** Planned

**Tactic**

Reserve or spend 10 gold only for a named plausible use before the next resupply. Each body can carry one TP crystal and one altar lock. Check the relevant inventory and purchase permission separately from equipment permission.

- **TP crystal:** consider a necessary terrain crossing or route shortcut whose value exceeds its three-turn-end channel and landing/interruption risk. The destination is within three Chebyshev tiles; this is not an instantaneous escape or map-wide teleport. Recheck the destination and survival before use. Stop holding a reserve once the crossing is no longer part of the mission.
- **Altar lock:** consider blocking/canceling an opposing tribute at a relevant altar, buying time for a fight/rotation, or protecting a deciding bank. Placement is within two tiles, and opponents can remove it with three successful basic attacks. A purchased but unused lock has not created that advantage.
- Do not automatically buy both on every visit. A 10-gold purchase can delay a 30-gold shard or a fifth-shard passive; account for that timing.
- Tavi can buy equipment remotely, **not consumables**. Dead/on-spawn opportunities may replenish a justified consumable. Ordinary wards are free and do not need a shop budget; legacy consumable slots are not valid substitutes.

**Current behavior:** There is no general strategic gold reserve. The enabled helper buys a missing lock for a living, non-channeling body on own spawn with 10–29 gold, purchase permission, no consumable restriction and sufficient fuel. It buys before checking for a useful nearby altar and makes no shopping detour. This convenience rule is different from the use-based budget above. [Current plans and limits](shopping-research-2026-10-16.md#our-existing-bot).

## 7. Adaptive builds

Change purchases when enemy damage, map conditions, or the champion's role demands it.

**Status:** Planned

**Tactic**

Use features of the **selected reachable route and mission**, not a map-name lookup. A large map with harmless clusters is different from a long route of damaging monsters. An apparent map-specific elite build may merely reflect a different draft; inspect the same body within the same team before proposing a map rule.

| Feature/change | Candidate adjustment | What must be checked |
|---|---|---|
| Repeated damaging camps, body acting as tank | First Jungle/Monster, Health or mitigation versus primary damage | Hits actually taken, ally participation, clear actions saved, recalls avoided |
| Harmless resource route / low pressure | Throughput and return/bank timing; reduced value of unused defense | Whether a future contested crossing changes the next job |
| Short enemy reinforcement paths or contested altar | Delivered burst, useful cast window and credible survival | Turn order, target access, cooldown, attack/cast legality and carried-gem stakes |
| Long spawn-to-mission travel | Larger justification for an elective trip; combine buys with necessary recovery | Actual path/abilities, team absence, next useful bundle; Home does not shorten walking |
| New role, new enemy pressure, bag banked | Re-score the bounded candidates and next completion | Existing first-copy passives and Prism's changed gem Focus; avoid oscillating between unrelated partial families |
| Approaching deciding bank/end | Immediate fight/escape/bank value | Whether any new income or faster future recall can still be used |

**Fallback:** If the information/model cannot distinguish candidates, keep the established role build and decline an unproven elective detour. Keep urgency in the mission state so a purchase policy cannot quietly override capture, survival or tribute deadlines.

**Validation required:** Several opponents, unseen generated maps, within-champion comparisons, useful action thresholds, and timing/choice experiments both separately and together. More spending or resemblance to the leader is not a success metric.

## 8. Shopping exceptions

Handle Tavi's field purchases and selling, spawn purchase healing, and each champion's separate budget.

**Status:** Planned

**Tactic**

- Read each body's own gold, inventory and restrictions. There is no pooled carry budget or direct item transfer between Cassi and Issac. Changing who collects capture income is a separate coordination policy, not a shop operation.
- On spawn, buying Health heals the exact added maximum HP, including completion gains. In the field, Tavi's Health purchase does not heal. Dead purchases do not resurrect the body; they equip its return. Consider the separate spawn end-of-turn full heal when valuing immediate purchased healing.
- Only Tavi can sell equipment for full face value, on spawn and also while dead in the pinned engine. The live article abbreviates this as “on spawn”; preserve this executable/source qualification. Sales remove the sold stats/passive immediately and refunds do not count as income. Other champions cannot respec.
- **Tavi's bounded same-turn spawn heal:** buying a loose Health shard on spawn adds maximum and current HP; selling that shard refunds its full price and caps current HP at the restored maximum without undoing all gained healing. A real Mite sequence heals 210/750 to 750/750 at zero net gold/inventory cost, independently reproduced in the engine. Consider this only when healing changes a useful action before the normal spawn end-of-turn heal. Require living Tavi on own spawn, legal buy/sell, at least 30 gold and missing HP; select a Health shard with at most three loose copies so the buy will not auto-combine. Bound cycles by the missing HP/growth, verify the refund/inventory after each pair, and stop on full HP, restrictions, failure or fuel bound. It cannot heal Tavi in the field or while dead. Do not equate zero net gold with zero computation cost. [Exact sequence and qualification](shopping-research-2026-10-16.md#tavis-same-turn-spawn-healing).
- Shopping is blocked by relevant stun/channel restrictions. It does not consume the ordinary move/basic attack/spell allowance. Buy before a useful action when stats change its outcome, then re-read and re-plan; do not apply a blind end-of-turn shopping pass.
- Home is an inventory-dependent timing exception. Use the actual capture phase and remaining recall timer before relying on capture-and-recall overlap. A teammate handoff must be real, not assumed.
- Bound catalogue queries and purchases, reserve fuel for the mission action, and handle failures once. Repeated invalid batches, direct emblem purchases and unavailable legacy consumables must not create loops.

**Current behavior and validation:** The [audited source and research](shopping-research-2026-10-16.md#our-existing-bot) describe its enabled fixed plans, disabled alternatives, 12-iteration purchase bound and missing mission telemetry. Planned validation records gold/inventory before and after, reason/threshold, alternatives, reserve purpose, successful use, recall absence and missed bank/capture opportunities. Keep status **Planned** until code and evidence match these decisions.

---

[Shopping research, elite transactions and mechanics](shopping-research-2026-10-16.md) · [← Recall and recovery](10-recall-and-recovery.md) · [Tactics index](README.md) · [Bot execution and validation →](12-execution-and-validation.md)
