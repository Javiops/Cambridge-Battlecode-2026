# Farming and camp capture

**Chapter 08 of 12** · [Tactics index](README.md)

How we turn camps into resources with useful timing and distribution.

**Reference:** Current behavior means the [pinned reference snapshot](reference-snapshot-2026-10-16.md) at [`a0c0fa2`](https://github.com/Javiops/Cambridge-Battlecode-2026/commit/a0c0fa2f222557483d665a9f7fce6f64a30b94ba), `bots/study27-economy/src`, with its [active parameters][c08-flags] and source defaults. Its identity with live v43 is unverified. **Implemented** records source behavior, without new gameplay validation; additions are **Planned**. Distances are Chebyshev tiles unless identified as walking distances.

## Contents

1. [Camp selection](#1-camp-selection)
2. [Opening farming allocation](#2-opening-farming-allocation)
3. [Camp combat positioning](#3-camp-combat-positioning)
4. [Monster targeting](#4-monster-targeting)
5. [Camp commitment and abandonment](#5-camp-commitment-and-abandonment)
6. [Capture ownership and continuity](#6-capture-ownership-and-continuity)
7. [Reward distribution](#7-reward-distribution)
8. [Respawn cycling](#8-respawn-cycling)

## 1. Camp selection

Rank camps by rewards, travel time, clearing time, incoming damage, and competition.

**Status:** Implemented

**Tactic:** Score eligible groups by weighted reward per estimated champion-time cost. Current gold weight is 0.25 before round 600 and 0.24 afterward. Use walking distance when its distance field succeeds, otherwise the explicit geometric fallback. Estimate clear time from our modeled DPS times assumed team size, add six rounds for capture, and charge estimated incoming damage through a recall/heal/return cycle. These terms are heuristics, not exact simulation.

Skip a temporarily rejected group, an unavailable respawn beyond the arrival allowance, and a recent danger area unless it is a designated hold group. Ordinarily skip groups without gems (`P_NOGOLD=1`). With `P_MONO=1`, when all gem-bearing groups are monolith groups, permit gold farming and cap the monolith's nominal required squad at roster size so persistent attrition remains eligible. This permits a contest-map strategy; it does not order every body to the monolith simultaneously. Named-map bank-cost/share adjustments still apply.

Enforce claim-based capacity: damaging camps allow at least the nominal required squad or four; gem clusters can use a pair; a waiting reward allows one. Use even reward division in scoring except non-monolith groups with at least 3000 HP use exponent 0.75. Penalize a group still needing more partners, enemy-side travel, and the enemy doorstep; apply the configured central-hold and current-target bonuses. Keep the best strictly positive score, or use [no-target waiting](#8-respawn-cycling).

**Limits:** Claimed bodies are not verified ready participants; the camp model assumes identical contribution and shared incoming damage. `P_RESERVE_PCT=-60` makes the camp affordability allowance permissive, not a positive health reserve. Stronger readiness and contested-farm rules remain [08.3](#3-camp-combat-positioning) and [08.5](#5-camp-commitment-and-abandonment).

**Implementation:** [Scoring and eligibility][c08-select], [DPS/squad model][c08-dps], [monolith-only detection][c08-mono].

## 2. Opening farming allocation

Assign the first camps and squads to build an effective early economy.

**Status:** Planned

**Tactic:** Use the revealed map's legal routes, camp threats and rewards to assign the smallest timely squad that can safely clear each opening job. An additional helper joins only when faster clear, avoided damage, or securing a contested reward beats its best feasible separate camp. Reserve the first collector and the exit/bank route as part of the job; do not assume every clearer must wait for capture. Follow the mission/readiness rules in [chapter 06](06-team-coordination.md).

Start with deterministic local decisions using the current claim layout: choose a camp, publish the intent, and check actual allies before waking a camp that requires help. Claim order can break ties, but a claim has no arrival guarantee. Do not wait indefinitely for an absent, dead, channeling, or delayed body. If required participants cannot arrive before the useful start window, take a viable smaller camp or stage outside monster reach and re-evaluate. The exact bounded assembly deadline is a planned parameter derived from travel and contest timing, not an optimized universal number.

**Current behavior:** There is no active scripted opening replacement: `P_O36_REPLACE=0`, `P_D34_OPENING=0`, and `P_PACKOPEN=0`. Bodies use the same independent camp scoring, shared claims, and nominal squad gate as later play. Before an untouched damaging group is started, insufficient nearby bodies can cause rejection, a heal request, or waiting on a radius-five ring. The current count within seven does not check action readiness or arrival order. Once a visible member is damaged, that initial rally gate is bypassed.

**Implementation gap:** [Parameters][c08-flags], [inactive defaults][c08-defaults], [rally gate][c08-farm].

## 3. Camp combat positioning

Predict which champion monsters will attack and position the squad accordingly.

**Status:** Planned

**Tactic:** Before waking a damaging group, identify the body actually exposed to its next attacks and the legal tiles from which helpers can contribute. Keep vulnerable ranged damage outside unnecessary monster/enemy reach where its action range permits, and let a healthier or protected participant take exposure only when that body can survive the expected attacks and still fulfill its next job. Do not assume monster damage splits evenly because several allies are nearby.

Use one short readiness check first: forecast the next incoming camp/enemy response from observable attacks, our ready actions, and actual participants. Hold the camp hit or rooting cast when it consumes the health, escape movement, or control needed to survive that response. Recheck after a monster changes position, a helper leaves, an enemy appears, or a shield/heal expires. An explicit tank rotation or aggro prediction needs confirmed targeting mechanics before implementation; do not import an unsupported taunt/body-block model.

**Current behavior:** The source uses total monster Strength and an equal-share squad affordability model. It engages a chosen member through its attack-range ring, with dash allowed; it has no explicit tank assignment or monster-focus rotation. Ordinary movement can avoid a ready enemy volley at 70% of our HP, but that is not a camp tanking model. Camp state/aggro is not exposed as an awake flag; the code uses damaged monsters as a proxy in several checks. See [camp engagement][c08-farm] and [squad assumptions][c08-dps].

**Stop/fallback:** If no safe action slot exists, stage outside the visible damaging monsters' actual ranges or abandon the job. Preserve capture only while survival permits it. Useful farming resumes when the threatening response is no longer immediate or the required combat reserve is restored.

## 4. Monster targeting

Choose attack order using range, remaining health, incoming damage, splash value, and ability resets.

**Status:** Implemented

**Tactic:** Within the assigned group, start from the visible living member with the least current HP. When a basic attack is available, `P_U34_FARM_REACH=1` scans up to eight members within fuel limits and instead selects the lowest-HP living member already in basic range. This avoids walking to another member when a useful attack is available now. If no local candidate exists or the scan cannot run, retain the original choice.

Use the current engage sequence: nearby offense spell, basic attack/reset, close toward the attack-range ring if needed, then basic attack. Only one selected target is pursued by that call. After the first successful basic hit, preserve the reset if that target is no longer alive and visible (`P_U34_RESET_LIVE=2`). Move to capture logic when the group exposes a waiting reward, rather than treating an empty visible camp list as proof of completion.

**Limits:** `P_SAVECC=0` does not reserve control for a nearby enemy, and the generic pre-attack fresh-target switch is off (`P_U34_ATTACK_LIVE=0`). The method is not a damage-per-incoming-hit optimizer, does not plan camp splash centres, and may still attempt a stale target after a preceding spell. The secure-farming veto in [08.5](#5-camp-commitment-and-abandonment) remains Planned.

**Implementation:** [Target choice][c08-farm], [offense/attack/reset sequence][c08-helpers].

## 5. Camp commitment and abandonment

Decide when to start, reinforce, pause, or leave a camp as circumstances change.

**Status:** Planned

**Tactic:** Commit when the minimum timely squad can survive the clear and a body can finish collection. Retain a productive target through small score changes. Immediately reopen the decision for a new enemy threat, a lost participant, an unsafe response, a failed route, or a reward already collected. Damage already dealt is a benefit only if the remaining job can still be secured; it does not justify sacrificing the collector or spending an essential escape cooldown.

For the first contested-farm prototype, inspect the next opponent/monster response before each discretionary hit or movement-exclusive camp cast. Reserve enough health and the specific ready escape/control action needed for that response. Use the existing 25% emergency HP threshold, or the Stellar-team 35% threshold, only as initial fallback floors; forecast lethal damage can require leaving earlier. If a visible enemy cannot affect the next useful action and the clear remains affordable, continue farming. This avoids a blanket visible-enemy veto.

**Current behavior:** A damaged member or an active capture on the region suppresses routine retargeting. Uncommitted travel is reconsidered every six rounds, with a 1.25 current-target scoring bonus. The initial squad gate runs only before observed damage. Below 18% HP, farming marks the group bad for 30 rounds, clears its claim, and flees if an observed damaged monster is in range. Strong-group rejection lasts 60 rounds; hidden probing gives up after more than three failed moves and rejects for 25. Combat/escape branches can already preempt farming, but no dedicated per-camp health/cooldown reserve against a nearby opponent is active. Declared `cf_focus_*` counters are not evidence of an implemented veto.

**Stop/fallback:** Clear the abandoned intent; select safe work or recovery. If the best action is to pause, wait outside the relevant threat range with a finite recheck, not on the damage tile. See [commitment and farming branches][c08-farm], [hidden probing][c08-probe], and [fight priority](07-combat-and-survival.md#1-fight-selection).

## 6. Capture ownership and continuity

Ensure someone completes the uncontested capture, remembering that extra occupants do not accelerate it.

**Status:** Planned

**Tactic:** When the group reports a waiting reward, designate one body that can actually occupy and remain on the region through completion. Preserve the last holder until reward receipt or a replacement already overlaps the required phases. A claim from within four tiles is an approach intention, not a completed handoff. When survival requires leaving, explicitly abandon the capture instead of assuming a remote claimant will save it.

Before departure, check the replacement's observed presence, HP, channel state, next action and the capture/recall phase order. A new remote acknowledgement scheme requires the byte budget and freshness design in [06.8](06-team-coordination.md#8-shared-commitments); it is not added implicitly here. Re-evaluate on death, movement, recall, enemy contest, or failed movement. End the hold only when the reward is confirmed, the replacement is established, or safety forces an abort.

**Current behavior:** `P_ONE_CAP=1` and `P_CAPCLAIM=1` rank a still-claiming ally within four of the region ahead of us by distance, then roster index. The newer evacuation helper improves the on-region case: it leaves only for an actually visible, living ally with at least 35% HP, not recalling/teleporting/submitting, already on the region. It also requires a legal step off the region toward another scored camp, no greater modeled enemy danger, and no visible damaging monster able to reach the destination. Without such a step, the current holder stays. An off-region body may still drop the target for the nearer claimant. This improves continuity but does not guarantee the other holder will remain until payout.

**Implementation gap:** [Claim-based nomination][c08-nominate], [actual-holder evacuation][c08-evac], [capture branch][c08-capture].

## 7. Reward distribution

Decide who should occupy the capture region when rewards arrive and who should leave.

**Status:** Planned

**Tactic:** Choose the collector by the next useful personal purchase, carrying/escape risk, and opportunity cost of waiting. Separate the useful clearers/protectors from bodies that need to remain at payout. More occupants do not accelerate capture and can divide the rewards. Gold and inventory are personal, including Cassi and Issac; do not allocate a teammate's shop budget as if it were pooled.

Consider a Treasure holder's eligible personal gold bonus or a nearby useful purchase threshold, but compare it with the travel/absence and safety cost of transferring the job. Do not divert a strong combat body merely to maximize its gold counter. If no meaningful allocation advantage is established, retain the existing viable holder. Use deterministic roster order only as a tie-break, not a claim that that body is always the best collector.

Confirm collection with the actual lifecycle/reward observation and personal balances where available. The current source infers reward arrival from **any** positive gold/gem change while on its target region; that is a useful proxy, not complete attribution. A contribution to monster damage alone does not secure the reward. See the established [personal economy mechanics](shopping-research-2026-10-16.md#verified-rules-and-investment-mathematics) and [investment policy](11-shopping-and-investment.md).

**Current behavior:** Collector nomination uses claim/distance/index; `P_CAPDPS=0` disables the alternative ranged-first preference. The source does not allocate collection by personal upgrade threshold or Treasure. Existing evacuation may reduce excess holders when a safe purposeful exit exists, but leaves them in place when it cannot establish that exit. Do not label this a complete loot-assignment policy. See [nomination][c08-nominate], [evacuation][c08-evac], and [reward-gain proxy][c08-reward].

## 8. Respawn cycling

Track camp availability, avoid blocking respawns, and choose between waiting and pursuing another resource.

**Status:** Implemented

**Tactic:** Refresh a group's lifecycle when one of its original spawn tiles is in personal effective vision. A visible respawn timer extends `next_ok`; a waiting reward clears that timer and records the observation round. A received lifecycle packet can extend the local cooldown estimate. Keep an unseen group's stored estimate distinct from a fresh engine observation.

With `P_RESPAWN=4`, consider a normal respawning camp when its wait is within estimated travel plus four; monolith waits are excluded by this selection allowance. At an assigned near-ready group with no live visible members, wait in the source's ring two to three tiles from its spawn tiles. If no camp is eligible at all, choose a non-monolith future group minimizing `wait + geometric distance / 2`; only stage when that score is below 120 and HP is at least 60%. That no-target staging ring is five tiles away, outside the union of radius-four areas. Otherwise request recovery when below 90% HP and far from home, or move home.

**Stop/fallback:** Fresh live/reward/respawning state replaces the old interpretation on observation. A group that has no visible living members and no fresh waiting reward is approached/probed; it is not assumed cleared. Failed probing is bounded. Do not stand on an expected spawn tile merely because a cached timer expired. These waiting positions are implemented heuristics, not verified optimal cycling or a universal proof that every respawn is unblocked.

**Implementation:** [Lifecycle refresh and sharing][c08-lifecycle], [eligibility][c08-select], [no-target staging][c08-farm], [near-ready waiting and probing][c08-probe].

---

[← Combat and survival](07-combat-and-survival.md) · [Tactics index](README.md) · [Gems and altar control →](09-gems-and-objectives.md)

[c08-flags]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L1-L82
[c08-select]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1825-L1918
[c08-dps]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1745-L1771
[c08-mono]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1124-L1160
[c08-defaults]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L120-L140
[c08-farm]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2434-L2580
[c08-helpers]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1504-L1566
[c08-probe]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2610-L2640
[c08-nominate]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2299-L2335
[c08-evac]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2360-L2431
[c08-capture]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2583-L2608
[c08-reward]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2762-L2778
[c08-lifecycle]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1671-L1742
