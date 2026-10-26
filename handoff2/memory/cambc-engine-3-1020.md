---
name: cambc-engine-3-1020
description: 2026-10-20 cambc 3.0 engine on the site: rules/economy facts, bench at /tmp/c3init, and the 3.0 candidates (econ3, fuelfix, sealed boss_battle fix)
metadata:
  type: project
---
Site on cambc 3.0 from 02:53-03:00 UTC 10-20 (heart_of_ruin first drafted 05:58; patch notes 'Patch Notes - Week 2' in analysis/claude-api-2026-10-18/patch_notes_week2_1020.txt). Local bench: /tmp/cambc3/bin/cambc 3.0.1 in /tmp/c3init (CAMBC_NO_UPDATE_CHECK=1); the 2.2.5 arena no longer judges. Details: analysis/claude-api-2026-10-18/engine3_changes_1020.md.
FACTS: new champion heart_of_ruin (draft index 11) and golem camp (on no site map); cluster hp 120; elk range 4, monolith 5; gems per clear wolf 4, cluster 7, elk 15, monolith 200; gold 6.6/round, kill gold 100; altar lock hits 5, ward cooldown 10. Games ~1550 rounds; more deaths only from length. END RULE: 1000 submitted gems, else round 2000; tiebreak submitted > lifetime gold > kills > team B. Tribute range 1 (bc::constants::submit_gems_range).
3.0 DROP (audit, cut at 03:00): 48.9% (485 g) -> 46.9% (855); 00lanes/01big_world/01fracture 24/72 -> 2/115, other 18 maps 51.6% -> 53.9% = FUEL-WAIT: can_choose keeps the cost of the turn-1 (double fuel) choice, so champions idle 70-80%.
CANDIDATES (all vs ranks 71-95, pinned on v76 draw 2026-10-20T145753Z):
- fuelfix-nd (bundles/fuelfix-nd.zip 7f70bfab; cheap choice instead of waiting, no decay): target maps 6/6 locally. Judge pre-registered: target net >= 2*sqrt(changed), others >= -2*sqrt. In the loop, tag fuelfix-on-v76.
- econ3c-ff (bundles/econ3c-ff.zip 3f74dda1 = econ3 E1 gates + E3 camp facts + E4 retarget, chase kept 144, on fuelfix-nd): 84-78 local, deaths +1.0 (audit note). Queued 2nd in the loop, tag econ3c-ff-on-v76. E2 wolf discount hurts (off).
- sealed-v1 (bundles/sealed-v1.zip f0e3acde, was b48d568d; on fuelfix-nd): 01boss_battle's only altar has 7 wall neighbours + 1 monolith tile, so the bot froze in tribute all game. A sealed altar = no altar -> farm kills the monolith -> banks. Local boss 2/2 (1000-gem wins), no-op elsewhere. LESSON: per-call vision checks on every map cost fuel (v1 77-85) -> static-first checks. Sent to the audit 15:20.
Next weak maps: gold_rush 16%, elk_arena 19%. Kill gold 100 = fight-layer lever not yet built.
Audit verdicts and conditions on these candidates: [[cambc-fuelfix-1020]].
- 16:49 USER: v80 = econ3c-ff = NEW BASE (activated by Javier). sealed held, rides in the next general candidate (econ3c-ff-sealed c0bd8472 = v80 + sealed, verified). Next draws: v80 vs 101-125, 25+25/hour (quota 50/rolling hour).
- 18:00 vision-v1 (bundles/vision-v1.zip 63ab1b1f = v80 + sealed + P_WARD ward on unseen bushes within 6): MECHANISM a unit in a bush is unseen beyond ~2 tiles (local probe 0-1%). Rivals ward ~270/game, we 0; our deaths on bush 10% vs 4%, broad across maps/rivals. Local 87-75 (harm check only). Audit OK; loop tag vision-v1-on-v80 on v80 draw 174749Z (101-126). Pre-registered (a) rival deaths on bush share up, (b) our deaths near bush, (c) deaths/kills (cap -1), (d) wards. Summaries: online/data/summaries (cambc summary JSON); my diag script analysis/claude-api-2026-10-18/scripts/summ_diag_1020.py; kill x,y = victim tile.
