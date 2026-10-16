# Gems and altar control

**Chapter 09 of 12** · [Tactics index](README.md)

How we protect resources and convert them into a winning score.

## Contents

1. [Tribute timing](#1-tribute-timing)
2. [Bag size and exposure](#2-bag-size-and-exposure)
3. [Altar selection](#3-altar-selection)
4. [Tribute positioning and protection](#4-tribute-positioning-and-protection)
5. [Channel continuation or cancellation](#5-channel-continuation-or-cancellation)
6. [Altar locks](#6-altar-locks)
7. [Territory and resource denial](#7-territory-and-resource-denial)
8. [Finishing and deadlines](#8-finishing-and-deadlines)

This chapter uses the [16 October reference snapshot](reference-snapshot-2026-10-16.md). The pinned repository source is not a confirmed byte-for-byte match to the screenshot's live v43. Implemented describes reachable source behavior; Planned identifies a material missing condition. This documentation audit ran no bot builds, matches or competitive experiments.

## 1. Tribute timing

Decide when to bank carried gems rather than continue farming or fighting.

**Status:** Implemented

**Tactic:** After higher-priority escape, combat and recall handling, bank a positive bag when no eligible chain-farm diversion is selected and one of these tests holds: bag at least 12; round at least 1,850; bag at least 10 with selected-altar distance at most 8 (4 on Rows); or bag at least 5 with distance at most 2. On Rows only, more than 40 rounds without a seen foe raises the ordinary bag threshold to 48. These reference values come from active parameters and map overrides, not an optimality claim.

Before late banking, a bag below 36 (60 on Rows) with altar distance above 2 may continue to the nearest ready non-monolith gem group within Chebyshev distance 8, closer than the altar, unclaimed except for our own existing target, and estimated solo-clearable with current HP minus 30% of maximum HP. A selected diversion postpones this bank branch. Ordinary recall can bank first with at least 10 gems when the altar is no farther than min(home distance, 12). Failed banking still ends these branches because the failed-channel continuation flag is 0. [bank before recall](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3092-L3140); [bank and chain rules](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3152-L3199); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L1-L20).

## 2. Bag size and exposure

Balance fewer delivery trips against longer tribute channels and greater losses on death.

**Status:** Planned

**Tactic:** Choose a bag by expected safe conversion rate, not just fewer trips. Include the extra channel length, route exposure, interception risk, death transfer, and the opportunity to collect another imminent reward during a channel. Reduce the target when a small delivery wins, a lock or threat changes the route, or the deadline is close. Stop accumulating when the next reward is less valuable than protecting and converting the current bag.

**Current behavior:** The reference uses the fixed thresholds in [09.1](#1-tribute-timing); the dedicated own-bag combat modifier is disabled. The saved official rules specify tribute duration max(1, ceil(starting bag / 10)) owner-turn-end ticks, followed by completion at the next owner turn start. Completion banks the then-current bag, including later capture rewards. Carried gems are not banked score and can transfer on champion death; linked Cassi/Issac deaths have special combined-bag handling. Prism's gem-based Focus also makes conversion a current-stat tradeoff. These mechanics inform the planned calculation; no such complete bag optimizer is present. [Official rules, checked against the saved 16 October snapshot](https://2026a.battlecode.co.uk/game/docs); [disabled carry mode](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L108-L110); [fixed bag policy](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3152-L3199).

## 3. Altar selection

Choose an altar using actual travel distance, safety, locks, and the next productive destination.

**Status:** Planned

**Tactic:** Choose among reachable adjacent channel positions by time to legal tribute, credible safety through completion, locks, and the productive action after delivery. Prefer a feasible safe conversion over a shorter route that cannot finish. Recompute after a lock, threat or route change; if no delivery is feasible, preserve the bag through a safer productive route rather than repeatedly attempting an impossible channel.

**Current behavior:** Active policy 1 computes a walking field and the shortest reachable passable tile in an altar's adjacent ring, plus one to retain the center-distance threshold convention. Cost adds 40 for a remembered enemy lock, 20 for a sufficiently enemy-side altar, and 60 for a fresh nearby danger alert, with held-area exceptions. Ties use home distance then altar index. Visible locks refresh a 40-round memory. The threat-aware policy 2 and the generic altar-safety flag are disabled; the next productive destination is absent. Planning requires remaining fuel above 56,000 and at most 64 altars, caches only the same round and position, and falls back to the legacy penalized Chebyshev selector if unavailable. Thus only the walking/penalty subparts are implemented. [selector, ring distances, cache and fallback](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1921-L2087); [safety default](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L138-L140); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L16-L17).

## 4. Tribute positioning and protection

Choose where to channel and whether the carrier needs vision, an escort, or nearby defenders.

**Status:** Planned

**Tactic:** Select an adjacent legal tile with a viable escape or continuation and the best actionable warning of approaching enemies. Request a specific protector only when that actor can arrive and contribute before the vulnerable delivery window; otherwise choose a safer altar, delay with a purpose, or convert a smaller available bag. Release the protector when the channel completes, is canceled, or ceases to be the best team commitment. Use personal observations and explicit compact messages rather than assuming shared vision or remote ally positions.

**Current behavior:** The bank helper selects an altar, steps toward its ring and attempts tribute immediately when adjacent. It does not assign or acknowledge an escort, calculate a protection window, or reserve a particular safe channel tile with teammates. A helper return can mean movement occurred even when no tribute began. Preserve the intended ward and commitment policies in [04](04-vision-and-information.md) and [06](06-team-coordination.md); they are not supplied by the current route heuristic. [move and tribute helper](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2138-L2162); [existing claim/broadcast layout](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1594-L1675).

## 5. Channel continuation or cancellation

Reassess whether completing a tribute is worth the risk as threats change.

**Status:** Planned

**Tactic:** At each owner turn, compare remaining channel time and expected converted value with the credible actions that could stop or kill the carrier. Continue when completion is still the best feasible outcome; cancel for a concrete legal escape or defensive action when continuing loses more. Reassess after an enemy arrives, a lock appears, a teammate fails to arrive, or the match deadline changes the value. Do not cancel merely because ordinary damage occurred: the saved rules say damage alone does not interrupt tribute, while stun, death and an enemy altar lock can.

**Current behavior:** Once submitting, recalling or teleporting, the normal decision function returns before ordinary threat processing; the spell pre-sweep also avoids active channels. There is no active manual tribute-cancellation policy. Failed channel attempts are caught, but the active failed-channel flag is 0, so several calling branches return even if nothing started. Starting a channel, decrementing its end ticks and completing it at the following owner start are different events; a recorded submit attempt is not banked score. [Official rules, saved snapshot checked 16 October](https://2026a.battlecode.co.uk/game/docs); [channel guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2780-L2788); [failed recall/bank handling](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3130-L3140); [pre-sweep channel guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3381-L3388); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L60-L68).

## 6. Altar locks

Decide when to buy, place, remove, or route around locks.

**Status:** Planned

**Tactic:** Buy or place a lock when its expected prevention or delay of enemy conversion beats the personal gold, travel and action alternatives. Place it where an enemy can credibly deliver, without blocking a more valuable allied plan. If an enemy lock blocks our delivery, compare removal time and exposure with rerouting; stop hitting it when a better legal delivery or survival action appears. Treat a blocked tribute converted into a lock attack as removal progress, not a successful tribute.

**Current behavior:** The post-turn helper is enabled. It buys a missing lock only in own spawn, when affordable and personal gold is below 30, subject to alive, non-channeling, consumable-use and fuel guards. With a lock owned, it considers altars within distance 2, avoids allied locks, requires enemy-home distance no more than own-home distance plus 4, and chooses the nearest to enemy home. It has no general value model or planned removal sequence; altar choice merely penalizes remembered enemy locks. The saved rules price a lock at 10 gold, allow one carried, and require three basic hits to remove an enemy lock. [Official rules](https://2026a.battlecode.co.uk/game/docs); [active lock helper](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/utility.h#L73-L104); [post-turn call](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3685-L3686); [routing penalty](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1921-L1945); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L54-L55).

## 7. Territory and resource denial

Decide when to defend home resources, contest the middle, invade, or obstruct enemy scoring.

**Status:** Planned

**Tactic:** Allocate defenders, clearers and collectors to protect a reliable scoring cycle. Contest or invade when arrival, local legal contribution, capture ownership and eventual delivery justify the risk; otherwise defend reachable income or trade for another resource. Denial counts only when it changes the opponent's feasible conversion or income enough to beat our alternative. Stop an invasion when its support, vision, capture continuity or return route fails. Avoid leaving every actor at the same cleared camp.

**Current behavior:** Camp choice discounts groups within eight tiles of enemy home by 0.6 and sufficiently farther from our home by 0.3. A qualifying caster composition can select a roughly equidistant altar area containing at least two nearby gem groups; those held groups receive a 2x camp value multiplier and bypass some danger/altar penalties. These geographic preferences are partial territory heuristics, not a shared defense, invasion or denial plan. Claims and partial capture-release behavior must be interpreted under [08](08-farming-and-capture.md) and [06](06-team-coordination.md), without assuming claim equals actual holder. [hold-area construction](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1227-L1244); [camp geography and danger exceptions](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1865-L1912); [altar held-area exceptions](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1964-L1974).

## 8. Finishing and deadlines

Calculate whether deliveries can secure victory or complete before the match ends, including tiebreak priorities.

**Status:** Planned

**Tactic:** Estimate the earliest legal completion of each candidate delivery from walking, occupancy, lock removal, channel ticks and owner-turn timing. Select a delivery that reaches 1,000 before the opponent when feasible; otherwise maximize completed tribute by the limit and then respect lifetime-gold and kill tiebreaks. Reduce bag targets or abandon an unfinishable capture when that improves the result. Treat an unknown enemy route or cooldown as uncertainty, not proof of a safe win.

**Current behavior:** Round 1,850 disables chain farming and makes any positive bag eligible for the ordinary bank branch, but it does not prove arrival or completion before round 2,000. Survival, combat and some recall decisions retain higher priority. The source has no team-score comparison, opponent finish-time model or tiebreak controller; its monolith-only gold exception merely makes tiebreak income eligible in that economy. The official 2,000-round rule and a test runner's shortened horizon must be recorded separately. [Official rules, checked against the saved 16 October snapshot](https://2026a.battlecode.co.uk/game/docs); [late-bank behavior](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3152-L3199); [gold-only exception](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1873-L1875); [higher priorities](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2910-L3140).

---

[← Farming and camp capture](08-farming-and-capture.md) · [Tactics index](README.md) · [Recall and recovery →](10-recall-and-recovery.md)
