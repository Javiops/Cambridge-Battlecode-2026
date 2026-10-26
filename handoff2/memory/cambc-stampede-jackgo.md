---
name: cambc-stampede-jackgo
description: 2026-10-16 15:03 stampede rule I045 (PR #26): from round P_JACKGO=350, P_JACKN=3 champions go to the centre and contest the prize, 2 keep farming gold; zip mybot_online1252_jackgo.zip = 12:52 online bot + rule only; identical games elsewhere; no local rival contests the centre so only online judges it; 15:06 combined zip mybot_online1252_jackgo_imitation.zip ready (rule + im_a retreat), upload advised after the 15:46 batch
metadata:
  type: project
  modified: 2026-10-16T15:18:27.502Z
---

Built by the "Study the 8 new maps" thread (cmsg_017gbamt2g1g8hMHRHQBc6qbMd44pcXaw6qZg9DZcQUmBg) after the online check showed the jackpot rule works but we never show up when the top teams take the centre (r305-650, 2-6 champions) and chain captures (see [[cambc-new-maps-1016]]).

Rule: from round P_JACKGO (350) P_JACKN (3) champions go together to the stampede centre and contest it, no longer leave it for "too strong", wait there through respawn; the other 2 keep farming gold. Params so the macro GA can tune them. Off = identical to the online bot on the 17 maps; on = only stampede changes. Local: 6 variants both sides vs 6 local rivals + online bot; 3 at 350 wins 12/14 (online bot 11/12), 1-1 vs online bot; 5 at 350 worse (10/14, loses both sides). These numbers are noise: no local rival contests the centre like the top 10, even the Mite/Nyx route ghosts lose 1080-0. Zip /mnt/project-files/bot/mybot_online1252_jackgo.zip, not uploaded. PR #26, idea I045.

Coordinator 15:05: asked the thread for mybot_online1252_jackgo_imitation.zip (online bot + this rule + im_a retreat params from [[cambc-replay-imitation]]), verified identical to each parent with the other off, as the single next upload candidate around 16:00; the centre-contesting gap went to the local-judge thread as a specialist opponent ([[cambc-local-judge]]). Related: [[cambc-online-is-economy]] [[cambc-ga-farm]].

**15:06 UTC:** combined candidate ready, /mnt/project-files/bot/mybot_online1252_jackgo_imitation.zip = 12:52 online bot + P_JACKGO 350/P_JACKN 3 + im_a retreat params (P_UNI_FLEE 33, P_LOWHP 40, P_GA_AVOID_HP 45, P_AVOID_DIST 2); verified on 17 maps both sides: stampede off = identical to the imitation zip, retreat at online values = identical to the jackgo zip; differs from the imitation zip only on stampede. Lineage in mybot_online1252_jackgo_imitation.txt; versions.jsonl line is added by the New maps thread only when the user says "uploaded" there (the loop reads the last line as the online bot). Coordinator advised uploading right after the 15:46 batch.

**15:17 UTC:** mybot_online1252_jackgo_imp.zip ready (12:52 bot + stampede rule + im_p paired retreat), verified: rule off = identical to the im_p zip, retreat at online values = identical to the jackgo zip; differs from im_p zip only on stampede. Not uploaded; swap decision card pending (coordinator recommends swap). versions.jsonl untouched until the user says uploaded.
