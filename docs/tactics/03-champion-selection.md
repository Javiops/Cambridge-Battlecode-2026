# Champion selection and draft

**Chapter 03 of 12** · [Tactics index](README.md)

Who we select, in which order, and how the team fits together.

## Contents

1. [Champion selection](#1-champion-selection)
2. [Pick order](#2-pick-order)
3. [Draft adaptation](#3-draft-adaptation)
4. [Team composition](#4-team-composition)
5. [Team size](#5-team-size)
6. [Champion and map fit](#6-champion-and-map-fit)
7. [Scaling and investment needs](#7-scaling-and-investment-needs)
8. [Champion-specific rules](#8-champion-specific-rules)

**Source scope:** The [reference snapshot](reference-snapshot-2026-10-16.md) pins the inspected bot at `a0c0fa2`, including its checked-in `params.h`, and explains the unconfirmed live-upload identity. **Implemented** means the stated reachable source behavior; **Planned** retains material policy work. This completion adds no build, simulation or performance validation.

## 1. Champion selection

Choose champions according to the jobs the team needs to perform on the current map.

**Status:** Implemented

**Tactic**

Discover draft choices by enumerating raw values 0–47, accepting nonempty normalized SDK names and removing duplicates/invalid sentinel names. Use the first legal, not-yet-tried choice in the active preference list. The baseline order is Vendetta, Varg, Cassi & Issac, Ryth, Tavi, Vesper Vale, Marcella, Ren, Stellar, Prism, Willow; other discovered valid choices are appended as fallbacks. This is a deterministic recipe policy, not a computed job-value optimizer.

**Conditions**

- Run only in draft mode. With `P_DRAFTUNI=2`, replace the leading preferences when a valid native spawn-region walking distance is at most `P_UNI_PATH=45`.
- After a successful pick, record it and yield the draft turn. Stop trying a particular choice after its first accepted or rejected attempt.

**Exceptions and fallback**

If the spawn path is unavailable, unreachable or longer than 45, retain the baseline list. Continue to other discovered choices when the SDK rejects a pick. No choice is treated as legal solely because it appears in the list; the draft API is authoritative.

**Implementation:** [Baseline preferences](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L526-L527), [Choice discovery](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L550-L574), [Active path-conditioned recipe, ordering and pick loop](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L651-L715), [Active draft/path flags](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L38-L43), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L39-L43).

## 2. Pick order

Decide which champions to reveal first and which choices benefit from additional information.

**Status:** Implemented

**Tactic**

Keep the ordered preference list fixed for this draft. Before every attempt, write the candidate roster and current policy fields into the 32-byte draft-memory buffer; this includes the prospective last pick, because control may not return after the final accepted selection. On success append the raw choice to accepted history. Mark the attempted list entry tried whether accepted or rejected, then continue from the next untried entry on later opportunities.

**Conditions**

- Attempt picks only while `fuel_ok(3000)` holds; this helper also preserves the 6,000-fuel reserve.
- One accepted choice ends the current pass; `end_turn()` yields. If no choice succeeds or fuel is insufficient, yield without inventing a selection.

**Exceptions and fallback**

An invalid/disallowed choice falls through to the remaining list and finally other discovered SDK choices. There is no deliberate hidden-counterpick delay or enemy-pick-driven reorder in this loop. The prospective memory write is not proof the pick was accepted; actual gameplay reads its physical roster from the SDK.

**Implementation:** [Fuel reserve](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L463-L471), [Prospective plan serialization](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L529-L548), [One-success pick loop and rejected-choice handling](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L683-L715), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L39-L43).

## 3. Draft adaptation

Respond to previously revealed enemy picks while accounting for simultaneous selection and shared champion availability.

**Status:** Planned

**Tactic**

Use only draft information the engine has actually revealed. Re-evaluate remaining legal choices against the accepted allied composition, visible enemy picks, available shared choices and the map’s reachable tasks. A simultaneous or not-yet-revealed enemy choice remains unknown. Preserve already accepted choices; after a rejection, choose the next legal alternative rather than claiming the intended composition still exists.

**Conditions**

- Apply when the draft supplies new revealed selections or an attempted choice becomes unavailable.
- Stop adaptation when no new legal information changes the task coverage, the draft is complete, or the remaining fuel requires the deterministic fallback.

**Exceptions and fallback**

Begin with the current fixed recipe as fallback. Counterpick weights and matchup thresholds remain unvalidated policy work; do not invent numerical matchup advantages. A map-only branch is not enemy adaptation.

**Current behavior:** The current routine reads public map geometry and team size but does not read revealed opponent selections or compute matchup scores. Rejected picks advance the fixed list. That is legal-choice fallback, not an implemented counterdraft.

**Implementation:** [Complete current draft information and selection path](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L550-L715).

## 4. Team composition

Balance damage, durability, crowd control, mobility, healing, and farming efficiency.

**Status:** Planned

**Tactic**

Cover the tasks the reachable map actually requires: productive camp clearing, sustainable damage, a useful control/peel action, safe banking and recovery. Identify who can do those tasks before committing several fragile or equipment-dependent bodies to the same job. A body can change task later; composition labels are not permanent assignments. Account for overlapping ability exclusions, private income and the Cassi/Issac linked pick rather than adding nominal damage numbers as if every body can act together.

**Conditions**

- Evaluate the whole accepted-plus-proposed composition before each planned pick, using the actual pick cap and legal alternatives.
- Reject a proposed replacement if it leaves an essential reachable task uncovered; fall back to the best legal recipe member when the richer coverage model is unresolved.

**Exceptions and fallback**

Use the existing size-specific recipe as the explicit baseline, not a claim of optimal balance. Delegate ready-group behavior to [Chapter 06](06-team-coordination.md) and combat action order to [Chapter 07](07-combat-and-survival.md).

**Current behavior:** On a qualifying short path the list starts Cassi/Ren/Stellar for at most three picks; adds Tavi for four; for five starts Ryth/Stellar/Prism/Ren/Tavi. Rejections and SDK limits can change the realized roster. Gameplay calls a roster “casters” when Stellar is present under `P_DRAFTUNI`; it does not calculate all these task-coverage conditions.

**Implementation:** [Current short-path composition recipes](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L651-L673), [Post-draft caster gate](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1194-L1228), [Actual physical roster](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1260-L1266), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L39-L51).

## 5. Team size

Adapt plans to three, four, or five picks and the actual number of controllable bodies.

**Status:** Implemented

**Tactic**

Read the draft pick cap from `bc::draft::team_size()` when selecting the active recipe. Keep that number distinct from controllable body count: selecting Cassi & Issac adds one draft choice and two separate bodies. After initialization, set `s.roster` and the current body index from `bc::champions(my_team)` rather than assuming that the draft list length is the army size. Use that physical count in existing camp affordability/sharing decisions.

**Conditions**

- Select the three-, four- or five-pick recipe only when the active short-path condition holds; otherwise use normal ordered fallback.
- After draft, follow the actual roster even if rejected picks changed the intended recipe. A dead body is not an extra ready worker merely because it remains in roster size.

**Exceptions and fallback**

The SDK still enforces the legal pick cap. If a metadata read fails, the attempt wrapper records failure and the fixed-order pick loop remains the fallback; no extra pick/body is fabricated. Physical roster size is a capacity bound, not proof that every body is nearby, alive or available.

**Implementation:** [Team-size draft branches and SDK picks](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L651-L715), [Physical roster and body index](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1260-L1266), [Roster-bound camp capacity](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1878-L1892), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L39-L43).

## 6. Champion and map fit

Evaluate which kits benefit from camp layouts, narrow corridors, open spaces, and travel distances.

**Status:** Planned

**Tactic**

Choose a kit for a concrete reachable job: walking and legal dash routes, useful basic/spell positions, camp layout, sustainable clear/return cycle and likely fighting space. Use real ability landing/range restrictions and useful personal sight. A short spawn path may justify evaluating a combat-oriented roster, but it does not by itself prove that a caster, diver or farming composition is best.

**Conditions**

- Reconsider map fit when a new map signature, route length or task layout changes the draft’s assumptions.
- Do not persist with a named-family recipe after its required tasks or legal choices are unavailable; use the general fallback.

**Exceptions and fallback**

Retain the existing 45-step spawn-path split until a richer criterion is implemented and tested. Unknown maps use measured geometry rather than being forced into the nearest known map name.

**Current behavior:** `P_DRAFTUNI=2` uses one walking-distance threshold and team size. `P_D34_FAMILY=1` can identify nine known signatures, but every family draft recipe is currently disabled by its zero default. No active per-kit topology score or learned map win model is present.

**Implementation:** [Implemented coarse spawn-path split](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L654-L673), [Optional recipe precedence](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L675-L682), [Public family classifier and disabled recipe options](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/de_rules.h#L46-L113), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L39-L43).

## 7. Scaling and investment needs

Consider starting strength, shard growth, and how much equipment each champion needs.

**Status:** Planned

**Tactic**

Estimate each candidate’s useful first actions with its starting kit, then the private gold and specific item points needed for later tasks. Compare the value of reaching an actual damage/survival breakpoint against the time, reward opportunities and banking/return cost required to fund it. Do not draft several bodies on the assumption that they share one wallet or automatically receive equal camp income. This game has equipment points rather than XP levels.

**Conditions**

- Use before taking an equipment-dependent candidate or assigning several candidates to one early income route.
- Abandon a scaling assumption when its income source is unavailable, its required breakpoint cannot arrive in time, or immediate survival/task coverage is missing.

**Exceptions and fallback**

Use the documented fixed builds as a baseline, not a demonstrated economic optimum. Detailed shopping timing and opportunity-cost rules remain authoritative in [Chapter 11](11-shopping-and-investment.md); do not duplicate or weaken that planned policy here.

**Current behavior:** Draft choice does not calculate candidate growth, per-body future income or build completion time. Gameplay assigns fixed per-champion item plans, then applies `P_SHOP_PLAN=3`, `P_SHOPUNI=1` and the active melee Power opening override. Those implemented build lists do not make the planned draft-investment comparison implemented.

**Implementation:** [Current fixed build and override sequence](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L997-L1073), [Actual shop attempts](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1297-L1343), [Farm value and cycle heuristic](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1825-L1918), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L28-L54).

## 8. Champion-specific rules

Explicitly handle linked deaths, gem-dependent Focus, kill resets, retaliation, splash attacks, stun immunity, and field shopping.

**Status:** Planned

**Tactic**

Apply kit-specific exceptions from current SDK/passive information, then re-read readiness and target state after successful actions. Protect Cassi without treating Issac as a disposable independent pick; retain separate body position, action and income state. Recompute Prism’s effective Focus when held gems change. Recheck Vendetta after a kill before using refreshed cooldowns. Include Ren retaliation and Varg splash in the next exchange rather than treating them as ordinary single-target damage. Do not spend a control action on a stun-immune target as if it supplied a normal stun. Use Tavi’s legal field equipment shopping without assuming field consumables or arbitrary health restoration are available.

**Conditions**

- Apply whenever the chosen body or visible target has one of these relevant kit properties; consult actual target legality, effective stats and cooldowns.
- Stop a reset or follow-up if its target is no longer visible/alive, its ability is unavailable, or survival/objective protection now takes priority.

**Exceptions and fallback**

If metadata is unreadable, retain a conservative legal basic/positioning action and avoid assuming a passive proc, stun, reset or shared budget. Movement-exclusive casts must yield or preserve movement deliberately; the other combat/ability chapters own those action-order rules.

**Current behavior:** The source discovers dash/reset/targeted/ground slots and has `P_U34_RESET_LIVE=2`, which requires a living visible target before an explicit attack-reset follow-up on every map. It also has champion-specific build overrides and runtime effective-stat reads. It does not implement a complete explicit passive-aware draft/combat rule set for all exceptions named above. Kit mechanics are not a claim that the corresponding policy is implemented.

**Implementation:** [Current ability metadata and ready-threat cache](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L774-L862), [Ability slot discovery](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1250-L1258), [Live-target reset guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1527-L1547), [Dead/field shop attempts](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2749-L2777), [Dash reach exceptions](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L83-L102), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L75-L82).

---

[← Map understanding and adaptation](02-map-understanding.md) · [Tactics index](README.md) · [Vision and information →](04-vision-and-information.md)
