---
name: cambc-mite-offscreen
description: 2026-10-15 what #1 Mite does off-screen: scripted per-map play (identical vs every opponent for 100-370 rounds), ~1200 unranked groups a day online, 2 attackers per camp; walking/idle are not the gap
metadata:
  type: project
  modified: 2026-10-15T11:04:36.224Z
---

2026-10-15 10:54 UTC the user asked what Mite does in preparation/behind the scenes to be so far ahead.
Report `/mnt/project-files/analysis/mite-behind-the-scenes-2026-10-15/README.md` (scripts + data; also repo branch
claude/project-thread-ztmd0i under analysis/mite-behind-the-scenes).

**Measured:** (1) Mite plays identically vs #2..#8 on the same map/side until contact: rows 103-369 rounds, monolith
92-120, expanse 80-289, corners 18, elkring 4-65; draft fixed per map. = hand-scripted plan per known map; nothing shows
how it reads a new map. (2) Public match list 10-14 21:32 to 10-15 10:57: Mite in 1244 unranked groups (360 started by
Mite, ~27/h, every hour of the night, vs Univardisty/hello/VeryGood/procless), 5103-1116 map games; we played 96 groups.
Versions are not public. (3) Squad size: Mite 2.0-2.4 attackers per camp under 3000 hp, 3.5 above, 3.2 in the first 50
rounds; kills in 12-21 rounds vs study25 1.2-1.9 attackers and 14-24 rounds; damage per attacker-round equal (42-57).
(4) Walking efficiency study25 0.80 > Mite 0.75 > Uni 0.59; idle champion-rounds 18% both. Pathing is not the gap.
**Takeaway:** the edge is preparation (per-map scripts + online volume) and dying less; copy only the squad rule (sent to
the "Read the map" thread via the coordinator). Related: [[cambc-top2-dissection]] [[cambc-mite-bots]] [[cambc-site-access]]
