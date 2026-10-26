---
name: cambc-top10-after-patch-1020
description: 2026-10-20 top-10 vs top-10 study on engine 3.0 (draft, how they die, fight shape, economy) and where its data/scripts live
metadata:
  type: project
  modified: 2026-10-20T19:35:36.793Z
---
Thread "Top 10 games after the patch" (cmsg_017gbamt2g1g8hMHRHQBc6qbCgNCZqVxjQkziAtEnjY63o), asked by Javier 10-20 18:34 UTC; shares running notes with the API thread in analysis/claude-api-2026-10-18/shared_notes_1020.md (user wants both threads to share memory).
DATA: analysis/top10-patch-1020/: games_top10.json (805 top-10 games since 03:00 UTC, public), match_ids_sample.txt (240 sent to the loop; summaries/ 230 done), t10_stats.py + t10_report.py (also read our v80/v81 summaries), report top10_after_patch_report.md. Loop runs online/fetch_summaries_ids.py (id list -> summaries, cookie stays in loop).
FINDINGS (230 summaries, final; same as the 64-game cut): top draft HoR 87% (we 0% until v82), Stellar/Ren/Ryth core; top deaths 48% with 3-4 attackers vs ours 27%, ours 0-1 attacker 49% (caught alone, fresh, burst); top fights longer and take +50% dmg yet die less (shields, allies); in 1v1 we already leave earlier but die 2x; top farm +40% monster dmg per champion, carry 2-4x bigger bags; teleport crystal 2.8/game (team-specific), we 0.
How to apply: micro fixes should target "don't be the lone target / commit when allies engaged", not leave-earlier hp thresholds. See [[cambc-engine-3-1020]].
CAVEAT: v81 summaries label deaths differently (champion 16.3->7.6/game, camp 4.6->12.8, same total), both sides; compare totals/shares only.
