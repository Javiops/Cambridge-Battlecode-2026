---
name: cambc-top10-plan-1024
description: 10-24 plan-level comparison V20 vs top10 (HoR hunts vs farms, quiet rounds, bags, far numbers, respawn waits); hfarm-v1 closed
metadata:
  type: project
---
Continuation of [[cambc-top10-micro-1023]] (thread "Qué hace mejor el top 10").
10-24 ~00:00 UTC PLAN VIEW (user 23:36 "debe haber algo que estemos obviando"; plan-1023/README.md, plots, plan100.py). V20 (37 v139 decoded, steps in scratchpad) vs t10, r100-700:
(1) our HoR hunts, theirs farms: camp 9.9% vs 20.5% of rounds, contact 34% vs 22%, walks end at a champion 44% vs 23%, kills 3.7 vs 1.7/g;
(2) quiet rounds: camp 19% vs 23%, walk 63% vs 57% (HoR, Vendetta, Vesper);
(3) we hit champions 5.0% vs 3.4% of rounds;
(4) t10 winners carry 60-160 gems on the field vs our 20-70; collected @r600 466 vs 367;
(5) in our losses 3.0-3.2 clusters, 60-66% in own third; t10 losers 2.5.
The k150 gap is CLOSED on V20 (0.62 vs 0.58). Next: hfarm-v1 (heart_of_ruin.h), then bigger bags.
00:25 UTC hfarm-v1 (e69dbc69, R0) and hfarm-v1b (565df9aa, from r150) built on v20c, in bot/hfarm-v1: HoR skips chase/bcf/ally-duty/helping unless a rival is within 2, she was hit, or a hurt ally is under attack. Sent to the local filter for the hard panel.
BAGS (bags.py): tributes/game 16.2 t10 vs 20.3 V20, bag median 22 vs 21, 50+ bags 19% vs 6%, gems lost at death 97 vs 27/game. The bag-policy lever is small (~4 trips/game); the carried stock comes from more farm time. Low priority.
00:35 UTC FAR NUMBERS (summaries; plan-1023/far_numbers.txt, scripts/farnum.py; t10 40 sides vs V20 v139 65 far games), sent to the far thread:
- collected gems @r800 525 vs 398;
- team monster dmg r150-400 23.2k vs 17.5k (-24%), r400-800 48.7k vs 36.6k;
- every champion -27..-41% from r150 (Marcella -41%); r0-150 about equal.
00:09 UTC hfarm HARD PANEL vs V20: v1 -30 (bar 22.1), v1b -20; near/mid negative, far +1/+2. Team kills -0.8, deaths +0.5-0.7. HoR gems unchanged (r800 111->113): skipping fights did NOT make HoR farm, it only removed support. CLOSED as built. Open question: what HoR does with the freed time (walk?) and why it does not take camps.

- 10-24 00:20 respawn-wait check (waits.py, same camp GROUP required): t10 2.9 respawn hits/game (16 rounds) vs V20 1.4 (3). The earlier 7.8 vs 2.5 counted any camp hit, so it was inflated. Long waits (15+ rounds) 0.8 vs 0.1/game. Small lever, not the missing piece.
- 10-24 ~01:00 FARM DECOMPOSITION (scratchpad an/trips.py, dph.py, spl.py, mhp.py, stack.py): camp-hit rounds/team r100-700 EQUAL (t10 259 vs V20 254); stacking same; we leave camps with a rival near 24% vs 15% of sessions. Camp dmg per attack round r150-800 HoR 50 vs 34, Vesper 41 vs 31, others equal. HoR mhp r150/500/700 t10 1000/1500/2000 vs ours 1400/2100/3000; gold all spent both. -> hfarm-v2 (5e99b22d = hfarm-v1b + top-10 HoR emblem order) and hfarm-v2b (94f31c46, build only) sent to local filter for hard panel.
- 10-24 00:57 HARD PANEL vs V20: hfarm-v2 -23 (bar 21.8; far -1 mid -17 near -5; HoR kills 2.52->1.95), hfarm-v2b (build only) -23 (bar 19.5; HoR deaths 1.33->1.64, team deaths +0.77). HoR gold@400 unchanged (408->411-414): the build does not make her farm faster. HoR LINE CLOSED (hfarm v1/v1b/v2/v2b all negative).
- 10-24 ~10:20 NEAR r30-150 FORMATION (top10 vs ranks 30-60 125 games vs V20 500; analysis/top10-micro-1023/early150/PAIRS.md, pairs.py, pairrun2.py, joiner.py): no-pair rounds r60-150 19-23% vs 41-43%; group of 3+ 33-40% vs 19-21%; no fixed couples (runs median 6); farm time equal; reaction to a rival equal; caught solo 4.4 vs 5.6/game, joined within 6 rounds 44% vs 34% (reactive ~27% vs ~18%). Piece "farm in pairs" is BUILT by thread "Copiar las decisiones del top 10" (stall thread assigned it); this thread is only the top-10 reference.
