---
name: cambc-courier-waste-1018
description: 2026-10-18 replay read of our Ryth (gem carrier, v65 likely) on rows: wasted recalls and gems lost at game end; small candidate idea, not tested
metadata:
  type: project
  modified: 2026-10-18T20:35:06.904Z
---
Match 9b59e1c9 (ranked, rows, lost 924-1056 vs "The something", 0 kills both sides, pure farm race). Replay in /mnt/project-files/analysis/replays-adhoc/. Our Ryth carries gems to altar (35,34): recalls to base with 0 gems right after depositing (r311, ~20 rounds wasted); recall with gems from (18,45) is no faster than walking; picks gems at r380 in far corner and the game ends with 66 undelivered; idle rounds at altar after deposit. Idea for a candidate: recall only if it shortens the trip to the altar with gems; stop fetching gems that cannot be delivered before game end. Wouldn't have flipped this game (990 < 1056). Judge per [[cambc-online-decides-rule-1018]].
CAUSES (v65 src next/archive/bank-v1b-clean/src/main.cpp): recall with gems = P_CAPRECALL 2 cr_capture_extra (hp<~0.85 or gold>=90+3*walk, ignores carried gems / altar distance); empty recall after deposit = shop_trip (gold>=180) after 'bank the bag first'; end-of-game loss = bot assumes 2000 rounds (P_LATE_ROUND 1850), never reads the 1000-gem win race.
OPENING WALK (r0-75): Ryth goes alone to far camp (7,45), waits in rally ring, P_NEEDHEAL 8 wait-drop at r45 (+bad_until 30) exactly as Varg/Cassi arrive 4-6 tiles away; then drops (18,45) at once (needed>coming) and waits for (31,45) respawn. Idea: keep rally while claimers approach. main.cpp ~2395-2425.
WHY ALONE: choose_target cap P_MAX_SHARE 4 (claimers>=cap -> skip), so the 5th champion never joins the opening camp; camps needing more than 1+claimers only get score*0.7, so it picks one it cannot solo. Any fix block goes after help-v1 on chain v65 -> fuel-v1 -> help-v1 (kill-v2 rejected).
