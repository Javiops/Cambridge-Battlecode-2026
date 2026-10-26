---
name: cambc-buddy-1025
description: 10-25 formation cause on deterministic base b27 - we split while WALKING between camps (top10 walk paired 55-57%, us 37-39%); buddy-v1 pieces sent to PC
metadata:
  type: project
  modified: 2026-10-25T09:33:06.731Z
---
Measured 10-25 ~09:30 UTC (real positions from replay decodes r30-150, near maps; scripts form.py/offcamp.py/walk3.py/clus.py/buddy.py in handoff/buddy/ on branch claude/project-thread-dxkoko, commit 3c9299b).
- Top 10 decodes: /mnt/project-files/analysis/top10-micro-1023/dec300/ (40 games top10 vs ranks 30-60, index.json, side a = team 0).
- AT CAMP paired (<=3) equal: top10 61%, band 73%, us 59-62%. WALKING paired: top10 55%, band 57%, us 37-39% (empty-handed walks 56-62% vs 37-41%). Clusters 2.6 (top10) vs 3.0 (us). Fight rounds at +2: top10 25%, band 27%, us 16%.
- Band 30-60 pairs as much as top 10, so pairing is necessary, not what separates top 10.
- Bot sees only ~half its living allies (vis_champions); g_pe estimates are poor. Shared memory 8 bytes all used (claims 0-4, BC cache 5-6, danger 7). pairfarm pf_on only on 11/26 near maps (spawn path < 35).
- buddy-v1: follower slots 1,3,4 value leader's (0,2,3) claimed group xW. bd2c W150, bd4c W250 + resync. Local 52 g vs b27: +2 15.8->19.5% (bd2c), walking paired 39->42-44%, result -1/9 and -1/13 (noise). Sent to PC via coordinator for pad/J2/reserve. bw (walk toward visible buddy) did nothing.
- ad2/ad3 (prefer claims of allies seen within 3-4) and bw: same ceiling (walking paired ~44%). Per-pair stay-together and join rates ~equal to top10; gap is spread, no single lever.
- BIGGER GAP (10-25 ~10:00 UTC, even.py): in EVEN fights (edge 0 start) top10 deal 12% foe hp in 5 rounds and kill 11%; us online 8% and 2% (18 games); we have 64 even rounds/game vs 44. Next lever proposed to user: fight damage (focus, burst, shop build), not formation.
Related: [[cambc-pairs-loneliness-1024]] [[cambc-pelea-v1-1024]] [[cambc-top10-plan-1024]]
