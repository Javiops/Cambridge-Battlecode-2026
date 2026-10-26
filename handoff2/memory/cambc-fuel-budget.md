---
name: cambc-fuel-budget
description: Fuel overrun (turns cut off, bot suspended and resumed next round): v3td lean fix 2026-10-13; study27-economy P_FUELGUARD (I033, PR #23) 2026-10-16; how to measure
metadata:
  type: project
---

Found 2026-10-13 ~17:00 UTC during the top-5 study ([[cambc-top5-study]]). A champion turn has 100k
fuel; a turn that runs over ends with replay step kind 26 (fuel exhausted) and the debt spills into the
next rounds, so the champion then acts only every 2nd-4th round. v3td: 500-1240 such turns per game on
lanes, corners, collision and expanse (35-130 on interlock/monolith/packs/rows, ~0 on elkring); the top
teams have 0. Main cost was `bc::vision::camps()` (5-10k fuel per visible camp, 39k mean / 90k p90 per
turn on lanes).

Fix = "lean" (`bot/main_lean.cpp`, `bot/mybot_lean.zip`, 17:38 UTC): `near_camps()` replaces the scan
with per-group lookups: groups within 12 tiles whose camp spawn tile is in `bc::vision::visible_tiles()`
(the engine's effective vision, which `camp_group::state()` checks; the champion's own
`me.visible_tiles()` differs and caused about one exception per turn), camps filtered by
`is_visible()`. Same decisions as v3td. Arena: 14-4 vs v3td, 162 vs 120 gems per 100 rounds, 18-0 vs
hunter2 with 73 deaths, 0-6 fuel-exhausted turns per game. It loses both elkring games (no fuel issue
there, just a different game).

Measure with `arena/tools/ghost/k26.py REPLAY...` (kind-26 steps per team; ~20 s per replay) and the
`errs=` field of the status lines in team-x.stdout.

**Why:** the afternoon fight-rule tests ([[cambc-fight-engine]]) ran on a bot that skipped turns, so
their verdicts may not hold on lean.
**How to apply:** build every new variant on lean, check k26 stays near 0 and exceptions stay low,
and never add per-turn scans of all camps or champions.

**Per-language fuel (measured 2026-10-14, probe bots ws/bots/{cppfuel,rsfuel,mlfuel,pyfuel}):** budget per
turn C++ 100k, Rust 100k, OCaml 500k (5x), Python ~2.5M (25x). Cost of one empty `vision::camps()`: C++ 536,
Rust 969, OCaml 10.4k (19x), Python ~914k (1700x); a 200-step Python loop ~308k vs ~2.4k in C++. The boost is
smaller than the overhead, so C++/Rust give the most work per turn; the user was advised to stay on C++.

**2026-10-16 P_FUELGUARD (I033, PR #23 draft, zip /mnt/project-files/bot/mybot_study27_economy_fuelguard.zip = main incl. P_MONO + guard, not uploaded):**
the online bot lost ~10 turns/game to fuel (lanes 63). Causes: init 120-185k of the 200k first turn (camp_groups() 20-26k,
one BFS per altar); while capturing, other_captures let position() throw for unseen allies (27-35k; C++ throws are dear)
and the evac check scanned vision::camps() + re-ran choose_target. Guard: cheaper same-result code + defer optional work
(init in 3 parts, camp re-choice, logs, greedy fallback step). Site maps 11.5 -> 1.1, hold60 5.9 -> 0.1; unlimited fuel
identical 154/154. Measure with tools/fuelscan.py (replays or --play, --release). Probe costs: BFS 5-8k, df.get 56,
is_set 43, export whole field 6-12k (dearer than reads). `cambc build --release` needs one debug build first.
**11:25 UTC:** on the user's ask the guard was put on the GA bot: /mnt/project-files/bot/mybot_ga65a6_fuelguard.zip = ga65a6 + P_MONO + P_FUELGUARD (not uploaded). Unlimited fuel identical to ga65a6 152/154 (contest only); cut-off turns 13.0 -> 0.8 (site), 6.7 -> 0.1 (hold60); gate --kind fight vs ga65a6 PASS (fresh 71-56, panel 26-15).
**11:40 UTC official 17 maps, ga65a6+guard vs ga65a6:** 23-11 games; won both sides contest (P_MONO), elkring, expanse, fragment, lanes, monolith, swirl; lost both corners; 9 split. Recommended uploading the guard zip.
- 2026-10-16 20:20 on v52: P_ROSTER + P_OCMEMO cut fuel-exhausted turns 106 -> 12 on the site maps with identical decisions, see [[cambc-micro-tracking]].
