---
name: cambc-farm-speed
description: 2026-10-14 "Farmeo" task: where our solo farming loses time (rows walls, gold-cluster trips, dropped walks), variants tested and results
metadata:
  type: project
  modified: 2026-10-14T11:30:01.607Z
---

10:59 UTC 2026-10-14 the user chose "Farmeo" (farm speed). Benchmarks: `tools/farmbench.sh TAG BOTS` (9 maps
vs idle, rounds to 1000, study16 = 3534) and `tools/fbgen.sh TAG maps_genall BOTS` (44 generated maps,
study16 = 23560). Summary script with per-map diffs: scratchpad fgsum.py (copy logs fg_fd_study16.log as baseline).

**Rival pace (online losses, round they hit 1000):** rows min 374 / mean 418 vs our solo 486 (worst gap);
expanse 326 vs 372; monolith 362 vs 383; interlock 371 vs 408; other maps we are as fast alone.

**Rows diagnosis (`P_MAPDUMP 1` prints the map; `P_DBGT 1` + `P_DBGT_LEN 1000` prints every target score):**
walls at y10-11 (x13+) and y21 (x0-32) make the walk from the east camps (31,4)/(42,4) to our altar (15,16)
26-37 steps, while recall (5) + spawn->altar is 18. Procless recalls on the capture tile, shops, walks
spawn->altar->camp. Our waste in a solo game: Cassi spends ~100 rounds on the gold-only cluster (1,32) for 105
gold, ~10% of champion-rounds are walks dropped by the 20-round re-choose, the far camp (42,4) gets 3 captures.

**Tested (farmbench / gen):** P_PATHD 1 (walking-distance targets) 3494 / 24030 (rows 426, gen31_14 +420
outlier), P_NOGOLD 1 3502 / 23504, P_STICK 200 (hysteresis, default 125) 3534 / 23590, 300 worse,
P_PATHD+NOGOLD 3494 / 23986, P_CAPRECALL 2 rows 447 but 3608, rs20/gw/ms/sr variants within noise.
New in fbase: **P_TELE N** (bank: recall when walk-to-altar > 5 + spawn->altar + N): no effect, the bot already
recalls to shop after each capture (270 gold). **P_SHOPFIX 1**: on big maps (gen31_14 is 80 wide) init can run
out of fuel before build_shop lists the items (P_PATHD fields made it shards=0): nobody ever buys and the
shop-trip recall fires every 40 rounds forever. Fix: finish the list on later turns, no shop trip for 150 rounds
after a spawn visit that bought nothing. Debug: `[shopfail]` print under P_DBGT. P_RESPAWN 15/40 with PATHD: no gain.
**11:40 UTC: study18 = site version 26** = study16 + P_SHOPFIX 1 + P_PATHD 1 + P_NOGOLD 1 (bot/mybot_study18.zip,
main/params/fight_study18): farmbench 3494 (rows 428), gen 23560 (= v24), vs v24 pool 9-9 (+46 gems), gen 46-42,
vs spar7-10 15-33 (v24 11-37), k26 0-8 a game like v24. Waiting for the user to activate it and play games.
