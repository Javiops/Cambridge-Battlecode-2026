---
name: cambc-caprecall-1018
description: 2026-10-18 23:55 Madrid finding: where the top 10's extra captures come from (capture + recall on the reward tiles 14.4 vs our 8.0 per game; lanes 15 vs 1.8) and the caprecall-v1 candidate block
metadata:
  type: project
  modified: 2026-10-18T21:44:13.193Z
---
Measured (audit scratchpad judge/capture.py, captypes.py, lootsrc.py, caprecall.py; copies in analysis/judge-and-deaths-2026-10-18/scripts; v65 online vs top 10, 67 games, us/them per game):
- captures 26.8/34.5; small camps (22 gems, 90 gold) 20.9/23.3; rewards >30 gems 5.9/10.6 (mostly elk); 100-gem rewards 0/0.3. Gold per capture 112/128.
- kill + capture on the spot (camp died within 6 tiles, 8 rounds): 18.1/18.0 = SAME. Capture of a camp the rival damaged: 0.5/1.6.
- capture + recall combo (recall started <= 7 rounds before the capture by the same champion): 8.0/14.4; lanes 1.8/15.0, corners 6.4/15.4, collision 5.8/13.7, elkring 12.2/14.6, interlock 13.5/13.4; cancelled 0.1/0.2. Their recall usually starts 5 rounds before (lands same round, credited on their spawn); ours 4.
- Our limits (bank-v1b-clean main.cpp ~3284): lanes forces P_CAPRECALL 1 (map rule), cr_capture_extra skips when the walk back looks long (cr_optional_value), and `safe`.
caprecall-v1 (STRATEGY.md "Capture and recall together", block given 21:55 UTC as a writing card, not pasted yet as far as I know): one rule on all maps: on our reward tiles with the capture running and no rival able to hit within the 5-round recall, recall when hp < 90% or gold >= 90 or carrying gems; removes the lanes exception and the walk estimate. Expected combos ~14/game (lanes 2 -> 10+), cancelled < 0.5, captures not down, deaths not up, gems r500 up; parent bank-v1b-clean (or fuel1c if identical).
Also 21:35 UTC tempo-v1 failed the local filter; I recommended parking it ([[cambc-help-v1-1018]]).
Related: [[cambc-kill-v2-online-1018]] [[cambc-courier-waste-1018]] [[cambc-macro-diagnosis-1018]].
~22:30 UTC caprecall-v1 LOCAL (archive\caprecall-v1, parent fuel-v1-clean, 142 maps): combos 13.0->17.1 (lanes 5.5->22.5), captures flat 26.2, cancelled 0.69->0.62 (limit 0.5 fails, parent already above), deaths 3.96->4.31, gems 797->788, fuel 0.66->0.26, 0 faults; h2h vs bank-v1b-clean 125 gen 48.0% (42-54). Site 17: 61.8% vs parent, deaths 11.4->9.8, collision gems 297->451, corners 309->273. Safety = rsafe OR capture_before_recall. No zip; card posted: zip (rec) / park.
21:55 UTC user: 50 groups soon, 25 for v65 (BASELINE V2 = approved base); asked what the other 25 should test -> audit recommended caprecall-v1 replaying v65's fresh 31-55 draw (zip via the bot-thread card; upload only after v65's 25 groups finish); audit judges pair by pair vs v65.
22:05 UTC caprecall-v1.zip READY in results\bundles (user asked 'dame el zip' despite filter miss; noted in versions.md as outside filter). Not uploaded.
22:04 UTC user: v65 (BASELINE V2) active again; audit asked the loop thread directly for a NEW draw on ranks 31-55 (25 groups) now, then caprecall-v1 replays it after the user uploads (once v65's 25 finished). Judge pair by pair with judge/judge_site.py + judge_fresh.py (reference = this v65 batch, not the 19:00 one).
22:11 UTC v65 (BASELINE V2) fresh draw data/draws/2026-10-18T220950Z.json (ranks 31-55, 25 rivals x 5 random maps) SENT 22:09:52-22:11:01 UTC, 25 groups. caprecall-v1 uploads only after all 25 finish, then replays that draw; audit poller judge/wait_groups.py.
22:16 UTC v65 reference on that draw DONE: 37/125 (30%), all 125 verified v65 in games.jsonl. User uploaded caprecall-v1 = site v70 (22:14, compiling); loop replays the draw once v70 is active. Judge: audit judge/judge_pair.py 2026-10-18T220950Z.json 65 70 [-v] (pairs per rival+map, versions from games.jsonl).
22:20 UTC caprecall-v1 = site v70 ONLINE REJECTED: v70 sent 22:16-22:17, all 125 verified v70; paired vs v65 on draw 220950Z: 37 vs 37 wins, changed 16-16 (needed +11.3), score 47/47; interlock +3, packs +2, lanes +1, six maps -1. Loop judge.py agrees. Same rival, maps, side a, no coinflip in both batches. Inferred: more combos alone do not give wins. v70 online replays need the cookie (loop) and were not decoded. By rule v65 goes back on the site (user).
