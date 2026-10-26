---
name: cambc-det-fuel-1024
description: kvvl-det (det-fuel): fuel_ok reads a deterministic meter so code changes stop reshuffling games; versions, calibration, results
metadata:
  type: project
  modified: 2026-10-24T21:15:34.000Z
---
10-24 20:22 coordinator asked: a kvvl version whose decisions don't depend on fuel left; test kvdet vs kvdet+probe = 0 changed games; check no fuel run-out and no strength loss vs kvvl (J2 on PC); it becomes the base to judge everything else.
- Cause of online "noise": any recompile shifts real fuel use from turn 1, so fuel_ok() branches flip from r2-3 (chain 16 pairs diverge median r3). kvvl + 20-instruction probe changes 248/312 local games, 43 results.
- det-fuel: g_dm meter charged per FP section (dm_cost(sec), depends on foes within 10 = g_dm_nf and a 70k shop visit on spawn), DM_CALL 400 per check, fuel_okc(need, charge) charges heavy passes (path search 15k, choose_target 28k, status line 21k, engage 19k, chase 17k, altar roots 17k, HoR loops 9k...). Quota DM_Q 88000 (2x first turn), real fuel only vetoes below DM_EMERG 9000 (counter dm=meter/emerg in status line).
- Results 52-game subset vs +probe: v1 flat means 225/312 changed; v2 30/52; v3 (foe-driven) 6/52, emerg 140->11/game; v4 1/52, emerg 3.4/game.
- Bench: scratch vend/ws (cambc 3.0.5 venv, 26 non-far maps x 6 rivals x 2 sides = 312 g, runall.sh/sub.sh/divloc.py/pair.py/vstat.py/emerg.py). Debug builds kvd2dbg/kvd3dbg print [dme]/[dmg] rows (heavy-turn gaps per call site).
Related: [[cambc-stall-root-cause-1024]] [[cambc-pelea-v1-1024]]
- 10-24 22:00 USER: det8 NOT online ("no deberiamos estar satisfechos"); replan: make the worst turn fit the real fuel so no decision reads fuel. Method: `cambc run-batch --fuel-quantum 2000000` = unlimited fuel; an exact optimization gives byte-identical replay.repl26a (ws/same.py). kvvl ungated: median 44k/turn, 3.2% >90k, 0.1% >190k (shop turns 170-215k: 12 buys x 7.4k plan walk).
- fuelfit opts (scratch vend/opts/o0*.py applied by applyopts.sh on kvvl/src; all exact 52/52): o01-03 vis_champions cache keyed (round, my pos, wards, attack/use count); o04 shop plan->shard resolved once + static bushes; o05 lshop cache, ward lazy positions, pow table. Profile build: mkprof.sh (ungate.py + autoprof.py + profhdr.py), pragg.py/secagg.py. PC (J2 800 g): det8 +9.2 vs kvvl +10.4; pad.py +20: det8 389/61 changed vs kvvl 337/67 (not less sensitive).
