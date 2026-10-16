# Bot execution and validation

**Chapter 12 of 12** · [Tactics index](README.md)

How decisions run reliably and how we establish what the bot does.

## Contents

1. [Decision priorities](#1-decision-priorities)
2. [Fuel management](#2-fuel-management)
3. [Turn order and timing](#3-turn-order-and-timing)
4. [Memory and coordination limits](#4-memory-and-coordination-limits)
5. [Action validation and fallbacks](#5-action-validation-and-fallbacks)
6. [Behavior diagnostics](#6-behavior-diagnostics)
7. [Representative testing](#7-representative-testing)
8. [Interactions between changes](#8-interactions-between-changes)

This chapter uses the [16 October reference snapshot](reference-snapshot-2026-10-16.md). The pinned repository source is not a confirmed byte-for-byte match to the screenshot's live v43. Implemented describes reachable source behavior; Planned identifies a material missing condition. This documentation audit ran no bot builds, matches or competitive experiments.

## 1. Decision priorities

Define which behavior wins when farming, fighting, escaping, shopping, and scoring recommend different actions.

**Status:** Planned

**Tactic:** Use the [resource-cycle decision contract](cycle-decision-contract.md) as the single owner of each body's movement/basic/cast budget. Observe lifecycle and actual channel state, handle a deciding delivery/interruption using 09.8, check the next credible response under 07, preserve a still-useful finite commitment under 06, then compare bounded clear/collect/deliver/recover/re-enter cycles. Insert only compatible ward and purchase proposals under 04/11, refresh after each accepted action, and classify movement/start/completion/rejection separately. A rejected fight never falls back to a camp expenditure already rejected for survival.

The contract adds local state and bounded initial test settings, not shared bytes or a hidden team controller. Hard safety/legality/missed-deadline invalidations override an ordinary lease; minor score changes do not. Continue valuable active channels unless a typed permitted cancellation improves the outcome. This planned order is different from the source order below and has no competitive validation yet.

**Current behavior:** Follow the actual active branch order. A spell pre-sweep runs before the normal turn when sweep mode is at least 3; it skips uninitialized, dead and channeling actors. The normal function initializes once, handles dead-actor shopping, records position/resources, resumes purchase-plan construction if needed, shops, then returns for existing channels or insufficient planning fuel. It next updates observations, runs support spells, unstick handling, spawn healing, emergency escape, near-threat recall, ordinary combat, recovery/recall, bag conversion and farming; an enemy attack is a final option.

This order resolves conflicts by earlier returns, not a single team utility score. Active caster kite/front routines can act before the generic engage/avoid tests; shopping occurs after a possible pre-sweep. After the normal function, the enabled lock helper runs, while the ward helper is disabled. Do not move a proposed survival, escort or bank rule earlier merely in prose: that remains a code change requiring validation. [setup and early branches](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2740-L2915); [normal priority ladder](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2917-L3249); [pre-sweep guards](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3381-L3388); [outer action order](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3594-L3698); [fallback/post-action switches](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/params.h#L60-L68).

## 2. Fuel management

Budget computation and handle suspended execution so expensive planning does not produce delayed, outdated actions.

**Status:** Planned

**Tactic:** Budget expensive work before acting, preserve enough fuel for fresh legality checks and turn completion, and restart or revalidate any computation that resumes with changed world state. Separate immutable map caches from current threats, occupancy and action readiness. Stop planning before the reserve is consumed and choose a bounded safe fallback; do not execute a stale target merely because it was good before suspension.

**Current behavior:** The helper requires remaining fuel strictly greater than requested work plus a 6,000 reserve. Ordinary planning asks for 15,000, so needs more than 21,000 remaining; the pre-sweep asks for 6,000, so needs more than 12,000. Shopping is bounded to 12 iterations; item-list construction can resume on later turns. Native altar planning has its own guards and falls back to a legacy selector. Initialization marks itself ready before the whole initialization body, so an interrupted/failed initialization is not a complete retry protocol. These guards do not demonstrate safe continuation after every suspension or a measured per-map budget. No fuel benchmark was run for this audit. [reserve and exception wrapper](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L463-L498); [resumable catalog work](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L997-L1027); [bounded shop](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L1297-L1338); [route fallback](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2020-L2087); [initialization and normal fuel guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2740-L2788); [sweep fuel guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3381-L3388).

## 3. Turn order and timing

Account for alternating teams, champion priority, capture phases, and exact channel completion timing.

**Status:** Planned

**Tactic:** Schedule a joint sequence from the actual owner-turn order: who can move, damage, protect or interrupt before the next enemy action, and which capture/channel phase follows. Change priorities only when the resulting next-round order enables a concrete sequence, and revalidate after death, channel state or enemy interference. Do not count geometric proximity as an action-ready ally or assume both allies act before the enemy.

**Current behavior:** The source uses owner-turn action checks and world-round ages, but does not call the priority setter to coordinate a new team order. Existing channels bypass normal decisions; capture-aware recall overlaps two distinct mechanics and must retain their exact completion rules. The [coordination chapter and its source-bound mechanics evidence](06-team-coordination.md) document alternating team turns, persistent next-round priority changes, same-round later-ally memory visibility and capture/channel timing in its stated engine scope. Those mechanics do not establish that the reference chooses a good combat order. A complete order-aware mission scheduler and follow-up contract remain Planned under [06](06-team-coordination.md). [channel guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2784-L2788); [capture/recall branch](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3092-L3124); [game-loop entry](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3700-L3706).

## 4. Memory and coordination limits

Fit plans into draft memory and shared match memory, including drafts with six champion bodies.

**Status:** Planned

**Tactic:** Fit each communication field to a named decision, owner, age, acceptance rule and expiry. Preserve existing uses of all eight shared bytes before adding a mission or readiness protocol. A six-body draft needs a valid layout for all six actors or an explicit degraded assignment; missing remote data must not silently mean safe, alive or ready. Re-read shared state before a dependent action and use personal observations for legality.

**Current behavior:** Claim storage uses bytes 0–4. With packed claims enabled, exactly six roster bodies and at most 63 camp groups allow six 6-bit group-plus-one claims in those five bytes; otherwise only five ordinary byte claims are available. The write reads those five bytes, changes its field and writes them back, preserving bytes 5–7, but does not prove arbitrary multi-call atomicity or claim freshness. Bytes 5–6 carry camp lifecycle/availability broadcasts, while byte 7 carries the active coarse danger message because help mode is off. Danger uses one of the first seven altar indices and an 8-round, modulo-32 time bucket. Its reader rejects an estimated age above 40 rounds, but an unchanged byte can alias after the 256-round wrap: this is not an absolute expiry guarantee. The lifecycle writer encodes min(250, ready_round // 8 + 1) and the reader multiplies that byte by 8; it is a quantized camp-ready estimate, not an ally readiness acknowledgement. The two lifecycle bytes are written separately. Claims have no time field, and neither message is an enemy list. A 32-byte CMB1 draft record carries roster/config data inside the separate draft buffer. The richer acknowledged commitments in [06](06-team-coordination.md) remain absent. [draft encoding](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L529-L547); [draft decoding](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L1268-L1284); [claim and lifecycle layout](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L1594-L1717); [danger encoding and expiry](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L1790-L1820); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/params.h#L57-L68).

## 5. Action validation and fallbacks

Check preconditions, handle failed actions, and provide a useful fallback when a plan cannot execute.

**Status:** Planned

**Tactic:** Validate current target identity, personal visibility, range, cooldown, occupancy, channel state and resources immediately before a dependent action. Distinguish an attempted command, an accepted action, movement, channel start and eventual reward. On failure, refresh the observation and choose a bounded legal alternative; stop the plan when its required target, route or timing disappears. Avoid a failure loop that consumes repeated turns without making progress.

**Current behavior:** Action wrappers catch standard and unknown exceptions and record failures. Some helpers check action availability, and movement/altar planning has fallbacks, but the active failed-channel and engage-fallback switches are both 0. Several failed recall, tribute or engage branches can therefore return without an alternative. The tribute helper may report handled movement even if the subsequent channel did not begin. This is partial resilience, not full semantic action verification. A complete failure classification and useful fallback policy require implementation and scenarios that test the actual failure, not just the existence of a catch block. [error and attempt handling](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L480-L498); [movement versus tribute start](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2138-L2162); [emergency/recall exits](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2917-L2949); [engage and recovery exits](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3070-L3140); [disabled continuation switches](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/params.h#L60-L68).

## 6. Behavior diagnostics

Measure deaths, lost gems, idle time, travel, capture delays, failed channels, and whether intended behaviors activate.

**Status:** Planned

**Tactic:** Emit bounded decision evidence that explains a lost bag, death, idle turn, travel detour, capture concession or failed channel: actor, round/order, observation age, chosen branch, attempted/accepted action and the reason a fallback did or did not run. Aggregate by map, side, champion and relevant opportunity denominator. Retain adverse examples as well as successful activations; stop excessive logging before it dominates fuel or storage.

**Current behavior:** Error logs print the first eight and then every 500th failure. Initialization logs include memory size, and ordinary status lines record position, health, bag, gold, mode, farm target, errors and fuel every 25 rounds with early/debug exceptions. Routing and capture-recall add bounded economic counters. Optional debug macros being present does not mean they are enabled. The existing replay dissection tool can produce a metric scorecard and proposals, but the audit did not run it or establish complete coverage of the diagnostics listed in this topic. [error throttling](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L480-L485); [bank-route diagnostics](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2120-L2135); [capture-recall counters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L2698-L2705); [initialization log](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3264-L3268); [status output](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/bots/study27-economy/src/main.cpp#L3331-L3348); [existing replay scorecard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/online/dissect.py#L87-L232).

## 7. Representative testing

Evaluate different map geometries, both sides, varied opponent styles, and fresh maps.

**Status:** Implemented

**Tactic:** Use the existing pipeline as a validation procedure, while recording exactly what ran. The gate builds and hashes candidate/base artifacts, rejects identical compiled bots, checks official maps on both sides for faults/broken games, compares shuffled held/development maps, writes counterexamples, and can apply a caster-opponent panel veto. The implemented CLI accepts only farm or fight kinds, despite the README also describing macro and bug. A farm change must favor the candidate with sign-test p below 0.05; a fight change must avoid significant worsening. These are current gate rules, not a proof of general competitive improvement.

Inspect the result's omissions. Fuel measurement covers selected maps on side A, can be unavailable, and can be bypassed; the panel can also be disabled. A generic PASS against a non-online or unknown base explicitly does not clear an upload. Source-hash registration binds the tested baseline only when the actual upload is available and recorded. Online pairing by opponent/map/side is useful observational follow-up, but unknown opponent versions and temporal changes limit causal interpretation. No pipeline stage, build, replay dissection, upload or match was executed for this handbook completion. [CLI/build/safety boundaries](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/tools/gate.py#L167-L229); [fresh maps, counterexamples and panel](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/tools/gate.py#L234-L306); [registered source-hash check](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/tools/online_base.py#L22-L91); [online comparison](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/online/lfl.py#L76-L150).

## 8. Interactions between changes

Test connected improvements together as well as individually, because their value can depend on one another.

**Status:** Planned

**Tactic:** For connected changes A and B, evaluate baseline, A, B and A+B on the same declared mechanics, source identities, maps, sides and opponents where possible. Include a combination when the hypothesized dependency is credible even if an isolated part is weak: a safer farming rule may need a better collector or exit rule before its value appears. Require direct activation evidence and inspect adverse cases. Stop tuning on held-out evaluation maps; use new development cases for the next revision.

**Current behavior:** The harness documents combinations only after their parts have a result, and asks the combination to beat the best part. The gate itself compares one candidate with one base; it does not automatically construct or summarize a full four-arm interaction experiment. Keep that existing conservative promotion rule distinct from the planned interaction study. A local pass, especially with unavailable/bypassed checks or uncertain live identity, is not sufficient to label a tactic Verified or accepted online. No combination experiment was run in this documentation audit. [idea/combination policy](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/harness/README.md#L40-L49); [held-out maps, best-part gate and scope](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/harness/README.md#L85-L104); [two-artifact gate](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/dee0fe7bf464d9f7b281af81f9650135fc541321/tools/gate.py#L167-L203).

---

[← Shopping and resource investment](11-shopping-and-investment.md) · [Tactics index](README.md)
