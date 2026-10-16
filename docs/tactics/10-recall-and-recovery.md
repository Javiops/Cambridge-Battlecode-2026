# Recall and recovery

**Chapter 10 of 12** · [Tactics index](README.md)

How we recall, teleport, recover, and rejoin productive play.

**Reference:** Current behavior uses the [pinned reference snapshot](reference-snapshot-2026-10-16.md) at [`a0c0fa2`](https://github.com/Javiops/Cambridge-Battlecode-2026/commit/a0c0fa2f222557483d665a9f7fce6f64a30b94ba), `bots/study27-economy/src`, with its [active parameters][c10-flags]. Its identity with the live v43 upload remains unverified. The planned decisions below have not been implemented or competitively validated by this documentation work. Use personal observations and actual channel/action state; do not assume a teammate's hidden position, HP, or intent.

## Contents

1. [Recall timing](#1-recall-timing)
2. [Recall safety](#2-recall-safety)
3. [Capture and recall overlap](#3-capture-and-recall-overlap)
4. [Recall interruption response](#4-recall-interruption-response)
5. [Spawn recovery](#5-spawn-recovery)
6. [Teleport crystal usage](#6-teleport-crystal-usage)
7. [Channel-specific behavior](#7-channel-specific-behavior)
8. [Death and re-entry](#8-death-and-re-entry)

## 1. Recall timing

Compare the benefit of healing, shopping, or repositioning with channel time and the journey back.

**Status:** Planned

**Tactic:** Separate necessary survival recovery from an elective shopping/reposition trip. For the elective trip, identify the HP or affordable upgrade that changes the next useful action, and compare it with channel time, spawn recovery, a walkable return route, missed capture/bank work, and team absence. Use the [shopping decision](11-shopping-and-investment.md#1-purchase-timing) as the authority for upgrade payoff. Gold or elapsed rounds alone does not establish that leaving is worthwhile; Tavi's ordinary field-shopping permission further reduces the reason to return just to spend.

Preserve a nearly completed useful capture/tribute unless safety forces an abort. Bank first when a genuinely reachable safe altar secures the bag at acceptable delay. Begin a necessary recall once the [full-channel safety check](#2-recall-safety) passes. End the trip when the required heal/purchase is installed and a productive re-entry route is available; do not remain on spawn simply because more health would be possible.

**Current behavior:** Below 55% HP requests ordinary recovery; the additional `gold >= 240 && HP < 50%` condition is already covered by that HP request. A recent `need_heal` request also qualifies below 80%. Non-Tavi elective shop recall requires at least 180 gold, more than 40 rounds since the recorded shop recall, more than 150 since a shop failure when `P_SHOPFIX=1`, and no active capture start. Ordinary recall requires `rsafe` and distance from spawn centre greater than six; with at least ten gems, a chosen altar within `min(home distance,12)` walking-distance units is tried first.

The newer **extra capture-trip** gate estimates return walking distance. Its HP cutoff is `clamp(0.90 − 0.006 × walk, 0.65, 0.90)`; its non-Tavi gold cutoff is `90 + 3 × min(walk,50)`, with shop-spacing/failure gates. Missing return-path data declines that extra opportunity. Necessary ordinary/emergency recovery is not vetoed by that optional-trip gate. These are current heuristics, not the mission payoff policy above. See [ordinary and capture recalls][c10-recalls] and [optional-trip calculation][c10-optional].

## 2. Recall safety

Estimate whether enemies or monsters can interrupt the channel before it completes.

**Status:** Planned

**Tactic:** Before starting, compare the actual remaining recall duration with visible enemy attack, spell, dash and control opportunities, acting order, and any awake monster that can damage the body. A safe tile now can be reachable before recall finishes. Use a real holder/cover plan if another body is expected to preserve the objective while we leave. Do not treat a ward's remote view as teammate vision or permission to assume an unseen route is clear.

If the channel cannot survive, first take a legal lower-threat move/control/dash action and reassess from the new state. If no safe start exists, continue escape or useful protection rather than repeatedly issuing recall in place. Recheck a pending recall after new information; continue it when finishing remains better than the legal cancellation alternative. Use actual permissions rather than a generic cancel-every-channel action.

**Current behavior:** `safe` means nearest visible enemy farther than eight, no nearby observed damaged camp within four, and no recorded HP loss in the last two rounds. For the source's Stellar-containing team, `rsafe` also permits nearest enemy at least five, at least one round since recorded damage, and no such damaged camp. The near-enemy recovery branch uses this relaxed rule below 55% HP and farther than six from spawn. These distance/proxy checks do not forecast the entire five- or three-tick channel and cannot certify hidden enemies or an untouched member of an awake group. Once channeling, the main decision normally returns without reassessing a cancellation plan. See [safety and emergency branches][c10-safety] and [channel return][c10-entry].

**Fallback:** Unknown threat timing is not proof of safety. Prefer a better observed retreat position or preserve the current productive task when recovery is elective. Exact risk margins remain planned parameters rather than universal “safe radius” guarantees.

## 3. Capture and recall overlap

Decide when recalling during capture saves time without losing rewards or creating an unnecessary return trip.

**Status:** Planned

**Tactic:** Recall on the capture region only when the reward will complete before our departure, or an actual replacement holder preserves all remaining capture phases. Read the real capture state, recall duration, inventory effects and phase order. Extra occupants do not accelerate the capture timer. Preserve the last holder until payout or a real overlapping handoff unless survival explicitly aborts the capture.

Normal recall uses five owner-turn-end ticks; Home uses three. The existing controlled example starts capture timer five in round two: normal recall then completes after the round-seven reward, while identical Home timing leaves at round five and loses the capture. Therefore do not reuse a fixed one-round delay or the five-tick overlap assumption after Home. Delay the shorter recall until reward precedes departure, or hand off to an actually present suitable ally. This is a confirmed timing exception, not evidence that every Home purchase is bad.

**Current behavior:** `P_CAPRECALL=2`, but Lanes explicitly uses mode one, which removes the extra optional capture trip there. Elsewhere, the return-walk gate in [10.1](#1-recall-timing) can add an opportunity. Capture recall requires strict `safe`, a fresh waiting reward at the target, no preferred collector according to `other_captures`, presence on the region and at least one elapsed round since local `cap_start`. Before entry, it can suppress ordinary recall so farming moves onto the region first. The delay is not computed from the owned Home effect or actual remaining capture phase. See [capture-recall branch][c10-recalls] and [verified Home/capture interaction](shopping-research-2026-10-16.md#verified-rules-and-investment-mathematics).

**Stop/fallback:** If timing, capture ownership, or return benefit is unresolved, finish collection before an elective recall. Safety can override collection. Do not call the trip free merely because channel and capture overlap; the return walk and forgone field work remain costs.

## 4. Recall interruption response

Decide whether to retry, retreat farther, fight, or change objectives after interruption.

**Status:** Planned

**Tactic:** Distinguish a rejected start, a channel still in progress, a completed arrival, and an interrupted channel. Requery current position, HP, channel state, threat and available actions before choosing the response. Do not mark a failed start as successful recovery or consume the rest of the decision merely because a recall command was attempted.

After an interruption by a reachable threat, first change the condition that caused it: reposition out of its useful action window, disable it, regroup with a real protector, or fight only if the bounded response supports that choice. Retry from the same tile only when fresh information establishes a meaningful change, such as the threatening ability becoming unavailable. Make at most one start attempt per decision pass, and use a legal remaining action on rejection where available. A finite retry history belongs in local state; a remote retry protocol is unnecessary for the first prototype.

**Current behavior:** Exceptions are caught, but `P_U34_FAILED_CHANNELS=0` disables the broader failed-channel continuation. The emergency branch can return after a failed recall start without trying movement; the capture branch also returns after its attempt. Ordinary recall returns after an attempted start under the disabled continuation setting. The near-recall branch does continue if its attempt fails. No explicit interruption cause/backoff policy is implemented; next nonchanneling turns re-enter normal selection. See [emergency/near recall][c10-safety] and [ordinary/capture attempts][c10-recalls].

**Fallback:** If no legal escape or useful action remains, preserve the current state and reassess next turn; do not spin repeated commands or fabricate a completed recall. Update commitment/collection duties when the interrupted recovery changes arrival timing.

## 5. Spawn recovery

Remain on spawn long enough to receive the required healing before leaving again.

**Status:** Planned

**Tactic:** After shopping, re-read current HP, maximum HP, equipment, restrictions and ready actions. Stay for the healing needed to survive and perform the next mission; use the current 95% threshold as an initial fallback when no mission estimate is available, not a required optimum. Depart when that requirement is met and the chosen route/action is legal. A threatened spawn can require protection or an urgent safe exit instead of a routine wait.

Shopping during an already necessary heal is permitted when legal. Do not infer an immediate field heal from buying Health: the established mechanics distinguish field max-HP growth from the own-spawn current-HP increase. The bounded Tavi Health-shard buy/sell healing exception is a separately verified mechanic and a **planned** capability; the audited bot does not implement it. Follow its inventory/refund/fuel guards in [11.8](11-shopping-and-investment.md#8-shopping-exceptions) before considering same-turn recovery.

**Current behavior:** The main body returns on own spawn when its computed health fraction is below 95%, optionally using a basic attack on an eligible enemy. Shop and support/pre-sweep activity can occur before that return. Importantly, `mhp` is cached **before** the shop call, while HP is read afterward. A Health purchase can therefore make the source's fraction differ from `current HP / current max HP`; it is not an exact post-purchase 95% guarantee. See [entry/shop/HP order][c10-entry] and [spawn wait][c10-spawn].

**Stop/fallback:** If the mission need is unknown, refresh actual post-purchase stats and use the conservative fallback. If purchase or optional healing fails, keep the existing inventory/cash interpretation and receive normal spawn recovery rather than retrying an unbounded loop.

## 6. Teleport crystal usage

Decide when its channel, destination, and purchase cost justify crossing terrain or shortening a route.

**Status:** Planned

**Tactic:** Consider a crystal only for a named useful crossing or relocation. It costs ten gold, carries at most one, and uses a three-turn-end channel to a legal destination within three Chebyshev tiles. Compare that delay, landing/interruption risk and gold opportunity cost with walking or a ready champion movement ability. The crystal can bypass intervening terrain, but the destination must satisfy actual legality; it is not an instantaneous escape or map-wide teleport.

Before buying or using, check the personal inventory and budget, actual action restrictions, legal destination/occupancy, and whether the channel can finish before the relevant threat or objective deadline. Choose the destination for the next useful action and an exit, not solely for shorter straight-line distance. Refresh state after starting and on the next opportunity; treat rejection or interruption as a new route decision.

**Stop/fallback:** Skip use when walking/mobility reaches the same mission sooner or the landing/channel is unsafe. On rejected use, retain the item/balance state shown by the engine, choose another legal landing if it still meets the deadline, or walk/replan. Do not assume a failed attempt moved the body or that any channel can be manually cancelled.

**Current behavior:** The pinned source contains no crystal purchase/use policy. `P_TELE` defaults to zero; its dormant “tele-bank” branch is ordinary recall plus walking from home, not a TP-crystal action. See [inactive recall shortcut][c10-tele] and the [consumable mechanics and purchase policy](11-shopping-and-investment.md#6-consumable-budgeting).

## 7. Channel-specific behavior

Handle recall, tribute, and teleport separately because their interruption and cancellation rules differ.

**Status:** Planned

**Tactic:** Keep explicit channel type, destination/objective, remaining duration, and completion/abort condition. Recall transfers us home and can lose a camp hold on departure; tribute converts carried value and has different damage-interruption behavior; TP crystal reserves a landing and has its own action rules. Read actual state and permitted operations before reacting. A generic “in combat, cancel channel” policy is invalid.

For recall, use [safety](#2-recall-safety) and [interruption response](#4-recall-interruption-response). For tribute, prioritize securing the bag under [chapter 09](09-gems-and-objectives.md) and the confirmed engine rules; do not assume ordinary damage interrupts it like recall. For crystal, use [10.6](#6-teleport-crystal-usage) and recheck the legal landing and channel outcome. Perform a useful free ward placement before beginning a channel when the [ward policy](04-vision-and-information.md) authorizes it; do not assume deployment remains legal during a channel.

Preserve a channel when its completion still meets the mission and no legal alternative improves the outcome. Yield only through an actual permitted operation justified by a fresh safety/objective decision. On completion or interruption, release stale collection/arrival assumptions and replan from the resulting position/resources.

**Current behavior:** The source returns for recall, tribute or teleport after its shop/reward bookkeeping and does not maintain a channel-specific cancellation policy. Pre-sweep also declines all three channel states; altar-lock and dormant ward helpers reject them. This avoids many illegal actions but does not implement the planned outcome comparison. See [channel early return][c10-entry], [sweep exclusion][c10-sweep] and [utility restrictions][c10-utility].

## 8. Death and re-entry

Account for lost gems, respawn downtime, shopping while dead, and safe routes back into play.

**Status:** Planned

**Tactic:** On death, clear the body's active farm/collector contribution and stop promising imminent support. Retain the actual personal gold, equipment and consumable inventory; carried-gem loss and respawn absence still make death costly. Cassi and Issac are separate resource owners with linked death risk, so update both availability and each body's real inventory rather than treating them as one wallet.

Buy while dead only through legal permissions and the [current investment priority](11-shopping-and-investment.md), using the next mission rather than an assumed old route. On respawn, refresh HP/max HP, ready abilities, objective availability and personally visible threats. Reassign from the current position: return to a still-useful job only when it survives the new travel deadline; otherwise take safe productive work or the minimum useful regroup. Do not automatically walk back into the fight that killed the body.

**Current behavior:** The dead branch calls the fixed shop policy, drops the camp target/claim and returns. The source retains its other local state across ordinary owner turns; re-entry has no dedicated mission assignment or explicit reset of every previous threat/plan field. Normal spawn recovery and later target selection handle the living body. Existing gold/items retention is a verified mechanic, not a reason to choose death as a routine recall substitute. See [dead branch][c10-entry] and [personal resource mechanics](shopping-research-2026-10-16.md#verified-rules-and-investment-mathematics).

**Stop/fallback:** A body contributes again only when it can legally act within the selected mission window. If remote information is stale, choose a reachable job from confirmed state and preserve the source's safe fallback rather than claiming a complete team re-entry contract.

---

[← Gems and altar control](09-gems-and-objectives.md) · [Tactics index](README.md) · [Shopping and resource investment →](11-shopping-and-investment.md)

[c10-flags]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L1-L82
[c10-optional]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2686-L2737
[c10-recalls]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3092-L3140
[c10-safety]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2862-L2948
[c10-entry]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2740-L2787
[c10-spawn]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2910-L2915
[c10-tele]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3185-L3198
[c10-sweep]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3381-L3388
[c10-utility]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/utility.h#L11-L102
