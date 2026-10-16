# Tactics reference snapshot — 16 October 2026

[Tactics index](README.md)

This handbook completion documents the latest retrieved repository bot and supplies concrete intended behavior where its implementation is incomplete. It changes documentation only. No bot build, simulation, new elite replay study or competitive experiment was run for this completion.

## Which bot is described

| Identity | Evidence and limit |
| --- | --- |
| Repository | [`Javiops/Cambridge-Battlecode-2026`](https://github.com/Javiops/Cambridge-Battlecode-2026) |
| Audited revision | [`a0c0fa2f222557483d665a9f7fce6f64a30b94ba`](https://github.com/Javiops/Cambridge-Battlecode-2026/commit/a0c0fa2f222557483d665a9f7fce6f64a30b94ba), main retrieved on 16 October 2026 |
| Reference source | [`bots/study27-economy/src`](https://github.com/Javiops/Cambridge-Battlecode-2026/tree/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src), including `params.h` and all five other source files |
| Source identity | `06e02e5342a8bac48a216b7407a3551d30190385fdd501d1195a74704392f22a`, using the repository's `tools/online_base.py` sorted-path/file-hash convention; [individual hashes and procedure](reference-source-2026-10-16.manifest.json) |
| Claimed live upload | The supplied screenshot shows **v43**, note **“same as v42 just without trolling mono”**, uploaded by GustavoIsMe, Live/Active. The screenshot does not include source bytes or a source hash. |
| Live/source match | **Unconfirmed.** The signed-in upload could not be retrieved. An upload number, note, ZIP size, newest filename or stale README is insufficient to prove identity. Do not relabel this reference as confirmed v43. |

The repository's older top-level README still calls v30 current. The newer [online-sync merge #17](https://github.com/Javiops/Cambridge-Battlecode-2026/pull/17) identifies `study27-economy` as the then-online source; the subsequent [monolith merge #21](https://github.com/Javiops/Cambridge-Battlecode-2026/pull/21) is included in the audited revision. Those records support the reference choice, not an exact match to screenshot v43. No `online/data/versions.jsonl` upload/hash record is present in the retrieved archive.

To close the identity gap later, download the actual v43 source, compare all relative `src/` filenames and bytes, and record its ZIP hash and upload number. If it differs, review the changed active branches and update only affected Current behavior paragraphs. Keep the existing intended policies unless evidence supports a better policy.

## Current implementation facts that matter

The optional `params.h` is included **before** the `#ifndef` defaults in `main.cpp`. An old header comment saying the uploaded bot has no parameters is not evidence that these parameters are absent. Follow the final configuration and reachable call order.

| Area | Active reference behavior | Consequence for the handbook |
| --- | --- | --- |
| Draft | `P_DRAFTUNI=2`, spawn walking-path gate `P_UNI_PATH=45`; family classification enabled but all family-specific draft recipe overrides default to 0 | Record the actual ordered draft and its fallback. Do not infer a unique recipe for every classified family. See [03](03-champion-selection.md). |
| Monolith-only economy | `P_MONO=1` by default, but runtime `mono_only` requires a gem-bearing monolith and no non-monolith gem group | Gold-only groups become eligible and monolith staffing can expand to the whole roster only under that feature gate. This is **not** a global monolith disable or a rule for every map named Monolith. See [02](02-map-understanding.md) and [08](08-farming-and-capture.md). |
| Wards | `P_R5_WARD=0`; dormant bush helper called only if enabled | Preserve the researched mission-aware ward specification as Planned. See [04](04-vision-and-information.md). |
| Coordination | Claims and danger/lifecycle bytes remain active; explicit group/help/twin routines disabled | Current cooperation is not a full mission/readiness protocol. Preserve [06](06-team-coordination.md). |
| Capture release | New `cf_evac_reward` requires an actual visible eligible holder and a productive legal exit; the separate `other_captures` selector still considers claims within four tiles | Describe the partial improvement without claiming complete handoff correctness. See [08.6](08-farming-and-capture.md#6-capture-ownership-and-continuity) and [06.8](06-team-coordination.md#8-shared-commitments). |
| Combat | `P_CASTSAFE=0`, `P_KITEFRONT=0`; active cast pre-sweep/kite/front routines have distinct priorities | Do not describe a universal shared focus or guaranteed survival-first action order as implemented. See [07](07-combat-and-survival.md). |
| Contested farming | No active enemy-aware camp health/cooldown reserve gate; ordinary farming still invokes `engage(..., false, true)` with `P_RESERVE_PCT=-60` | Discord's secure-farming requirement remains Planned, despite diagnostic counter names. See [08.5](08-farming-and-capture.md#5-camp-commitment-and-abandonment). |
| Extra capture recall | Return-path-priced optional healing/gold thresholds, with Tavi gold-only exclusion and unavailable-path fallback | Update the partial Current behavior in [10](10-recall-and-recovery.md) and [11.1](11-shopping-and-investment.md#1-purchase-timing); keep the richer mission-payoff policy. |
| Banking | `br_policy=1`; threat-aware policy 2 is dormant, failed-channel continuation flag remains 0 | Walking-route heuristics do not imply a fully safe altar-selection model. See [09](09-gems-and-objectives.md). |
| Purchases | `P_SHOP_PLAN=3`, later `P_SHOPUNI=1` caster overrides, then `P_NE_POWER_OPEN=1` melee opening; loop bounded to 12 buys | Preserve the researched shopping policy and explicitly document the current fixed baseline. See [11](11-shopping-and-investment.md). |

Exact thresholds and higher-priority exceptions live in their chapters. A source-based heuristic is not a measured optimum. Descriptive comments, dormant code and telemetry names are not proof a behavior executes.

## How the supplied team feedback was used

The user supplied Discord text as evidence of team priorities. It is not an instruction from the team to execute actions, and no Discord messages were sent or private Discord history consulted for this completion.

| Reported observation or wish | Where it becomes a concrete planned rule |
| --- | --- |
| Micro is the biggest priority | [07 Combat and survival](07-combat-and-survival.md): survival/interrupt/focus decisions, legal action sequencing and commit/exit conditions |
| We damage camps while enemies punish us, losing HP and cooldowns | [08 Farming and capture](08-farming-and-capture.md): compare the credible enemy response before committing camp damage; wait, reposition, contest or leave when unsafe |
| Camps are killed but conceded or not collected | [08](08-farming-and-capture.md) and [06.8](06-team-coordination.md#8-shared-commitments): designate a real holder, confirm presence/overlap and reward receipt; release excess clearers |
| Choose an appropriate collector rather than everyone doing everything | [06.1](06-team-coordination.md#1-role-assignment) and [08](08-farming-and-capture.md): assignment by timely legal contribution, safety, income use and alternatives, not a fixed weakest/strongest label |
| Use wards and the eight bytes more efficiently | Preserve [04](04-vision-and-information.md) and [06.8](06-team-coordination.md#8-shared-commitments); do not overwrite the existing claims/lifecycle/danger allocation |

The pasted statement about qualification on 4 November is a dated team statement, not an independently verified event date. It does not define mechanics or change the tactics here.

## Status and review boundary

All 96 numbered topics have a concrete baseline or explicit intended policy: 19 are source-Implemented and 77 are Planned, including composites with useful implemented subparts. **Implemented** means the stated reachable behavior is present in the pinned source; it does not mean it is optimal or currently live. **Planned** means an important condition is absent, different or still to be implemented. Partial implementation is identified under Current behavior. Existing research verifies particular mechanics or observations, not the competitive strength of every proposed rule.

The detailed intended policies in chapters **04, 06 and 11** were retained. Only their reference/current-behavior notes were refreshed where the newly audited code justifies it. Their historical replay/mechanics research keeps its original revision and limitations.

Checks for this update cover topic coverage, preserved headings/anchors, relative links, source-reference line bounds, manifest hashes and the protected-chapter policy boundary. The [documentation check record](reference-validation-2026-10-16.json) contains the coverage and checked-link counts. These are documentation checks. Future implementation, scenario validation and comparative play remain separate work under [12](12-execution-and-validation.md).
