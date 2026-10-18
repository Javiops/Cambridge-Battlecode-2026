# Camp forecast v3 — Shadow-only, ability-aware calibration

**Use case:** Test whether observed ready offensive spells and basic attack resets improve four-round camp damage forecasts. This is NOT yet a better farming strategy. It does not veto camps, rotate champions, or change any farming/combat actions.

Base source: `battlecode_mate_no_prism.zip` (Mate + all-champion wards + Alerts V2 + No Prism). Builds on the previous shadow diagnostic in `battlecode_mate_camp_model_shadow.zip`; other bot code remains the same.

## Changes

- Logs **two** predictions for the same live camp/champion snapshot: existing basic-only (`hp4`, `rem4`) and new ability-aware (`hp4skills`, `rem4skills`).
- Reads each visible ally's real Focus, champion type, and readiness of its corresponding damage/reset abilities.
- Models supported Focus multipliers from current game rules; direct damage, some area damage, and one ready basic-reset. One spell cast per owner turn, and no repeated casts within four rounds.
- Keeps enemy proximity marker (`foe8`) to distinguish contested samples.
- Uses a four-turn forecast horizon instead of 36 to reduce simulation work while evaluating exact +4 observations.
- Does NOT model cooldown refresh from kills, shield skills, precise walls/pathfinding, CC duration, competing enemy damage, exact teammate turn order, or all ability/ground cast combinations. Vision may be incomplete.

## Setup (PowerShell from repo root)

```
New-Item -ItemType Directory -Force bots\exp_camp_model_shadow_v3 | Out-Null
Expand-Archive "$env:USERPROFILE\Downloads\battlecode_mate_camp_model_shadow_v3.zip" -DestinationPath bots\exp_camp_model_shadow_v3 -Force
& $env:CAMBC_CLI build bots/exp_camp_model_shadow_v3
python3 tools/ab.py bots/exp_camp_model_shadow_v3 bots/exp_mate_no_prism --sets official --jobs 1 --keep
```

Install the analyzer separately:

```
New-Item -ItemType Directory -Force tools\camp_model | Out-Null
Expand-Archive "$env:USERPROFILE\Downloads\camp_model_compare_tool.zip" -DestinationPath tools\camp_model -Force
python3 tools/camp_model/camp_model_compare.py "out/ab/exp_camp_model_shadow_v3_vs_exp_mate_no_prism/official"
```

## Criterion for progressing

The *ability-aware* forecast should outperform the basic-only forecast on exact four-round comparisons, **especially for complete-visibility, no-invented-movement cases**. Look for lower MAE/bias in remaining monster HP without worsening champion HP. The ability-aware forecast is still biased by the selection of fights that lasted at least four rounds; the results cannot prove full-camp survival or capture yet.

Don't compare A/B win rates of logging-enabled bots as strategy performance. The diagnostic adds calculations, SDK calls, and logs, which may cost fuel and change execution.

Only when these forecasts are calibrated should a *separate* decision-making bot use them to choose a tank, decide when to start camps, or rotate frontliners. Never make a hard rejection based solely on this unfinished model.
