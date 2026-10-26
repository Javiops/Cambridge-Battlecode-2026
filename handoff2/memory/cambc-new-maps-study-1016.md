---
name: cambc-new-maps-study-1016
description: 2026-10-16 study of the 8 new site maps vs top 10 (report path, findings, I040-I044, P_JACKPOT PR #26, zip ga65a6+mono+jackpot not uploaded); site API no longer returns public statistics
metadata:
  type: project
  modified: 2026-10-16T12:00:09.643Z
---

Report `/mnt/project-files/analysis/new-maps-2026-10-16/README.md` (Spanish), tables report_tables.md, per-game data/games.json,
scripts in scripts/ (also repo analysis/new-maps-2026-10-16, docs/new-maps-2026-10-16.md). 120 top-10 replays on the new maps + 48 ours.
**Site change 2026-10-16:** match-groups/<id> no longer returns `statistics` for public games; replays still public
(bundle may answer {"status":"pending"} first; then re-GET the plain bundle URL, the pollUrl 404s). 503s under load: 1 req / 4-5 s.
Old replays need CAMBC_VIS_WASM = visualiser v0_0_1 (ext.py retries with it).
**Findings:** C&I in every winning draft on 14/14 maps (old ones too), Stellar in most; winners earn ~2x gold on all new maps,
17-22 buys/game vs our 9-12. stampede: winners stay off the central 360-gem group until r350-475, farm ~9000 gold, then take it;
we go at r53 and die 27x. contest same (first gem r1337). eight = fight map with spawn_path 46 (threshold 45). fragment/swirl:
same draft, we lose by dying (micro).
**Gates (base main):** I041 P_NOGOLD 0 FAIL 2-15; I040 caster draft everywhere FAIL 37-57; P_DRAFT5 alone PASS 14-8 ns;
I042 P_JACKPOT 350 PASS (fires only on stampede), now ON in main params via PR #26 (draft). Zip on online bot:
/mnt/project-files/bot/mybot_ga65a6_mono_jackpot.zip (ga65a6 + P_MONO + P_JACKPOT), gate vs ga65a6 PASS fight 29-43 p=0.125,
contest+stampede won both sides; not uploaded. I043 (fight-map reading), I044 (shop cadence) are ideas only.
Related: [[cambc-new-maps-1016]] [[cambc-contest-monolith]] [[cambc-new-maps-rule]] [[cambc-harness]]

**12:05 UTC:** combined upload candidate /mnt/project-files/bot/mybot_ga65a6_mono_fuelguard_jackpot.zip (ga65a6 + P_MONO + P_FUELGUARD + P_JACKPOT 350); with --fuel 100000000 identical to the jackpot zip on 17/17 site maps and to the fuelguard zip on 16/17 (only stampede differs). Not uploaded; user asked to upload this one zip.
**12:52 UTC:** the user uploaded and activated mybot_ga65a6_mono_fuelguard_jackpot.zip; recorded in online/data/versions.jsonl (src 32644eda90). Games from 12:53 belong to it.
**14:55 UTC online check** (online-check/, check.py): build behaves as intended; stampede 0-10 vs top-24: we farm gold (often more than them) and stay off the centre, but they take it r305-650 with 2-6 champs while we have 0-1 there, 3 caps = 1080; we die 5-21 times before r500. Missing rule: commit the whole team to the jackpot from r350. contest 0-7: pure fight loss, ~19 deaths before r500, 64-92/game, 1/3 their gold; monolith is not the issue.
**15:05 UTC I045** P_JACKGO 350 / P_JACKN 3 (PR #26): from r350 3 champs commit to the jackpot (needed capped, wait through respawn, score x P_JACKW 10). Off = identical to online bot on 17 maps (--fuel 1e8); on changes only stampede. Local can't judge (all local rivals lose stampede anyway; ghosts of the online games lose 1080-0). Zip /mnt/project-files/bot/mybot_online1252_jackgo.zip = 12:52 online bot + rule only, not uploaded.
**15:10 UTC** single next upload /mnt/project-files/bot/mybot_online1252_jackgo_imitation.zip = online 12:52 + I045 + im_a retreat params; identity checks pass; lineage + versions.jsonl line to append on upload in the .txt next to it (not appended: versions.jsonl last row = what is online).
**15:09:52 UTC** the user uploaded mybot_online1252_jackgo_imitation.zip (versions.jsonl row added, src 05c752ed3c); I045 stage online.
**15:25 UTC** next candidate /mnt/project-files/bot/mybot_online1252_jackgo_imp.zip = 12:52 + I045 + im_p paired retreat (I062); identity checks pass; .txt alongside has the versions.jsonl row to add only when uploaded.
**15:20:11 UTC** user uploaded mybot_online1252_jackgo_imp.zip (versions.jsonl row added, src 8b6a37dada); the 15:09 im_a version had no clean batch; first clean batch 15:46.
