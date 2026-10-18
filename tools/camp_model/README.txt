CAMP FORECAST V2 — REAL-BOT SHADOW INTEGRATION

Baseline: battlecode_mate_no_prism.zip (Mate + all-champion wards + Alerts V2 + No Prism).
Changes: new src/camp_forecast.h, main.cpp snapshots/forecast/event logs, params.h toggles only.
No farming decisions are changed. Do not submit as a stronger bot.

WHAT IS ALREADY GROUNDED
- Per-person current HP, current Strength, basic range and current position
- Monster current health, position and damage; Varg full splash only to nearby secondary monsters
- Completed Monster, Jungle and Durability emblems from the actual item count and shop type list
- Camp strikes before champion turns, nearest-in-range target, 3-tile camp range
- Movement / ranged shoot tradeoff, but only with an OPEN-TERRAIN approximation

WHAT IS STILL UNMODELED
- Spells, resets, shields in effect, buffs and health regeneration
- Exact ally action ordering, movement mask/walls/occupied cells, fog of war
- Enemy interventions, and five-turn capture interruption
These MUST be added/calibrated before using forecasts for a hard safety gate.
A confident=1 diagnostic only means all monsters were visible and no simulated moves were needed,
NOT that omitted spells or rival arrivals were safely predicted.

HOW TO TEST (PowerShell from Battlecode repository root)
  New-Item -ItemType Directory -Force bots\exp_camp_model_shadow | Out-Null
  Expand-Archive "$env:USERPROFILE\Downloads\battlecode_mate_camp_model_shadow.zip" -DestinationPath bots\exp_camp_model_shadow -Force
  & $env:CAMBC_CLI build bots/exp_camp_model_shadow
  python3 tools/ab.py bots/exp_camp_model_shadow bots/exp_mate_no_prism --sets official --jobs 1 --keep
  python3 tools/camp_model_report.py "out/ab/exp_camp_model_shadow_vs_exp_mate_no_prism/official"

NOTE: Logging and queries cost fuel, so the A/B wins of this shadow build are NOT a strategy verdict.
The four-round report is the success criterion: enough matched observations and small errors,
plus no meaningful increase in fuel faults. If it cannot predict clear time/HP accurately,
we must fix its mechanics rather than allowing it to reject camps.

PARAMETERS in params.h
 P_CP_MODE 0 = off, 1 = shadow
 P_CP_TRACE 1 logs [camp-model] and [camp-observed] event lines
 P_CP_RADIUS 5 limits snapshots to champions already near a camp
 P_CP_MINFUEL 48000 attempts not to starve current-turn combat actions

VALIDATION LIMITATIONS
Compiled and tested the model-only C++ code with 7 synthetic cases here, without SDK.
Complete bot source archive checked; full SDK compilation and game simulations
can only run in an installed cambc environment.
