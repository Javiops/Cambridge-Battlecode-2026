# Positions and map control: study27 (v35 + stacking) vs study26 (v35) against the top 30

**Samples.** study27 = 155 unranked games of study27 (study26 + "stack up to 4 champions on camp groups of 3000+ hp, one champion on smaller camps"), 12:37 UTC, 58-97 (top-10 opponents 15-35 in 50 games, rank 11-30 43-62 in 105). study26 = the 150 games of the earlier dissection (`positions.md`), 59-91 (10-40 / 49-51). Per map, study27 vs study26 (W-L): collision 8-11 vs 12-7, corners 8-11 vs 5-12, elkring 5-4 vs 9 games (5-9), expanse 10-7 vs 11-6, interlock 10-9 vs 7-6, lanes 3-14 vs 3-15, monolith 5-11 vs 5-8, packs 6-16 vs 7-14, rows 3-14 vs 4-14. Same 30-opponent pool except 4 bots (Palestine, Cabbage, Mate in One, EMPEROR Tung replace MicroStella, WHIM, SSSA, Nyx stays). Side a in 150/155. Drafts per map identical to study26 in every game.

**Camp groups with ≥3000 hp (where the stacking rule can fire):** rows wolf packs (4050 ×3 per side) and the central monolith (41000, untouched by anyone); expanse 4-camp groups (3900: one own, one enemy, two mid) ; collision 4-elk groups (3900, one per side); corners 3-cluster groups (5300) and elk pairs (4800); monolith map: the 24000 monoliths only. **No such group exists on lanes, packs, elkring (2900), interlock** — on those maps the change can only act through "one champion on smaller camps".

**How to read the tables.** Every table of the study26 report is repeated with four rows per split: `us27` / `us26` / `opp27` / `opp26` (the opponents' numbers in the study27 games and in the study26 games). Definitions are unchanged (territory = BFS distance to own vs enemy spawn, own/mid/enemy with a 3-step band; action labels; classes). "Large relative to the sample" below means the difference of per-game means is ≥2 standard errors (`cmp_games.md`), or, for counts, the gap exceeds ~2 × sqrt(count); everything else is reported as "no change" even when the printed digits differ.

**Scripts** (`$S/ws2/scripts_positions/`): the loader `common.py` now takes the batch directory from `WS=<dir>` (default `ws2`; `WS=ws3` for study27; `DATA=/abs/path` also works). `run_all.sh <ws> <outdir>` runs q1-q15 (`q13_stacking.py` and `q14_idlecamp.py` are new: hitters per capture by group-hp class; the idle-next-to-living-camp streak table, whose original script was lost — it reproduces the study26 numbers within 1-2%; `q15_rows_end.py`: rows end-game). `cmp_tables.py <outA> <outB>` merges the markdown tables of two runs; `cmp_games.py` compares per-game metrics with standard errors. study27 outputs: `$S/ws3/pos_out/` (`q*.out`, `cmp_tables.md`, `cmp_games.md`, `traces/<match>.txt`). Re-run: `WS=ws3 python3 -I $S/ws2/scripts_positions/q1_territory.py`, or `$S/ws2/scripts_positions/run_all.sh ws3 $S/ws3/pos_out`.

## 0. Headline

1. **The stacking rule fires exactly where it can, and only there.** Rows: 42% of our pack captures now have 4 concurrent hitters (0% in study26; 293 captures), first-hit→capture 18 rounds (21), respawn→capture of the nearest pack 19 rounds median (32), captures 17.4/game (15.8, z=3.5), gems per 100 rounds 245 (222, z=4.3), idle streaks next to a living pack 67 (3.9/game) vs 110 (6.1), largest cluster 2.9 champions (2.4). Expanse: the 3900-hp groups are now hit by 2 champions (74% of 19 captures; 0 of 15 before) and our mean depth rose 14.6→16.6 (z=6.5). Collision: 2 captures of the 3900 elk group (1 before). Nothing else about where we stand changed: own/mid/enemy 85/13/1 vs 86/13/1, pairwise distance 10.6/10.6, alone 30/29%, idle 9.0/9.4%, caster-melee gap +0.18/+0.23, invasions 3.0/2.9 per game, deaths 5.8/5.7 per game, 73/25/2 vs 76/21/3 by zone.
2. **Rows is still 3-14 because the race is now lost by the last two bags, not by the cycle.** In 15 of 17 games the 16th capture comes at r365 (a fixed script, identical tiles in every game), the last tribute lands at r380 for 957, and 165 gems (10 games) or 99 (5) are still carried when the opponent reaches 1056 at r366-r398: we end 10 games at 957-1056 having earned 1122. The carried gems are half-bags: the r239 double capture gives Varg and Issac 33 each; Varg keeps his 33 until he captures the far pack at r379 (140 rounds), recalls and buys at spawn with 99 at r380. study26 lost the same games at 726-957 with 66-198 carried; the stacking bought ~100 gems per game and left the finish untouched.
3. **Lanes is the same loss with a bigger invasion.** Opponents stood in our half 19% of their rounds (12% in study26) and captured 94 of our groups (64) = 6.6 per loss (3.6); rounds with ≥3 enemies in one of our lanes 568 (296), and we had 0.9-1.3 champions there. Our captures fell to 32.8/game (37.9, z=-1.9), alone share rose from 26.4% to 30.5% (z=2.2), and the opening lost its exact determinism (2-4 patterns at r10-40 instead of 1). Fighting share near invaders 10% in both batches; deaths 3.8/game in both.
4. **Packs, monolith, collision moved by 1-4 games, which is noise, but packs shows one real change: we kill fewer** (opp deaths 2.4/game vs 3.8, z=-2.0) and cross less (19 episodes vs 40), and the opponents now take a camp in our half in 16 of 22 games (13 of 21), first at median r289 (r426). Monolith: we now spend 19% of rounds in the middle (17%, z=2.3) and idle 5.9% (5.3, z=2.1), capture 27.4 vs their 31.8 (26.5 vs 31.0 before): still the same 4-5 captures/game behind. Collision 8-11 after 12-7 with identical positions (pd 7.1/7.1, own 69/68, mid captures 10.4 vs 11.5) — the 7 games in which we lost more champions before r100 went 1-6 (4-3 in study26).
5. **Formation, idle behaviour and reactions to invaders are byte-identical in every table** (melee front 44%/44%, caster front 39/38; idle with an enemy within 8 42/40%; when invaded we move 53/52%, stand 12/12%, fight 10/10%). Mid-camp balance decides as before: diff ≤ -6 → 7% wins (n=26; 0% n=18), -5..-1 → 20% (19%), 0 → 36% (38%), 1..5 → 52% (59%), ≥6 → 89% (87%).


## 1. Where our champions stand (Q1)

### 1a. Own / middle / enemy share of alive champion-rounds, 50-round bins

| split | who | games | 0-49 | 50-99 | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 | 400-449 | 450+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 155 | 89/11/0 | 84/15/1 | 88/11/1 | 86/13/1 | 87/12/1 | 87/12/1 | 85/14/2 | 83/16/1 | 80/19/1 | 75/23/2 |
| ALL | us26 | 150 | 90/10/0 | 85/14/1 | 87/12/1 | 86/13/1 | 88/11/1 | 86/12/1 | 86/13/1 | 83/16/1 | 80/18/2 | 75/23/2 |
| ALL | opp27 | 155 | 94/5/1 | 81/13/7 | 80/12/8 | 79/13/8 | 76/14/10 | 77/14/9 | 77/14/10 | 74/16/10 | 69/22/9 | 65/24/11 |
| ALL | opp26 | 150 | 94/5/1 | 80/13/6 | 79/13/8 | 78/14/8 | 79/13/8 | 79/14/7 | 78/14/8 | 72/17/11 | 69/20/11 | 64/25/11 |
| map:collision | us27 | 19 | 56/43/1 | 82/17/1 | 67/32/0 | 67/33/0 | 73/26/0 | 71/29/1 | 70/29/1 | 66/34/0 | 70/30/0 | 68/31/1 |
| map:collision | us26 | 19 | 58/42/0 | 79/20/1 | 67/33/0 | 62/38/0 | 73/26/1 | 67/31/1 | 66/33/0 | 65/35/0 | 65/34/1 | 68/32/0 |
| map:collision | opp27 | 19 | 93/6/0 | 63/28/9 | 72/23/5 | 69/25/6 | 66/29/5 | 68/28/5 | 68/29/4 | 65/30/5 | 68/27/5 | 64/30/6 |
| map:collision | opp26 | 19 | 93/6/1 | 73/23/5 | 73/23/4 | 76/21/3 | 66/27/7 | 69/26/5 | 68/25/6 | 64/24/13 | 70/22/8 | 66/29/5 |
| map:corners | us27 | 19 | 79/20/1 | 80/15/4 | 77/22/2 | 84/15/2 | 75/19/7 | 75/20/4 | 69/24/7 | 79/17/4 | 84/14/2 | 81/16/3 |
| map:corners | us26 | 17 | 79/20/1 | 81/15/4 | 76/22/3 | 80/19/1 | 84/15/1 | 81/17/2 | 77/20/3 | 79/19/3 | 78/20/2 | 85/13/2 |
| map:corners | opp27 | 19 | 85/12/3 | 80/12/9 | 66/22/12 | 64/25/11 | 63/19/18 | 64/22/14 | 66/15/19 | 59/21/20 | 58/30/12 | 59/25/16 |
| map:corners | opp26 | 17 | 82/14/4 | 72/20/8 | 64/24/12 | 61/26/12 | 62/25/13 | 61/25/14 | 66/24/11 | 58/23/19 | 59/26/15 | 54/26/19 |
| map:elkring | us27 | 9 | 95/5/0 | 83/16/1 | 82/15/3 | 82/15/3 | 81/17/2 | 82/16/2 | 82/17/1 | 74/23/3 | 75/22/4 | 77/20/3 |
| map:elkring | us26 | 14 | 97/3/0 | 79/20/1 | 88/12/1 | 82/15/2 | 81/16/3 | 76/19/5 | 77/20/4 | 77/21/2 | 75/21/4 | 77/19/4 |
| map:elkring | opp27 | 9 | 96/3/0 | 72/18/10 | 79/13/8 | 84/10/6 | 73/19/8 | 81/13/7 | 64/24/12 | 77/13/10 | 77/16/7 | 70/17/13 |
| map:elkring | opp26 | 14 | 95/4/0 | 79/12/9 | 77/18/5 | 79/13/8 | 74/19/8 | 76/15/8 | 76/17/7 | 71/17/12 | 72/19/8 | 69/19/12 |
| map:expanse | us27 | 17 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 99/1/0 | 94/6/0 | - | - |
| map:expanse | us26 | 17 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | - | - |
| map:expanse | opp27 | 17 | 100/0/0 | 99/0/1 | 99/0/1 | 99/0/1 | 99/0/1 | 100/0/0 | 99/1/0 | 97/1/2 | - | - |
| map:expanse | opp26 | 17 | 100/0/0 | 99/0/1 | 99/0/1 | 99/0/1 | 99/0/1 | 99/0/1 | 99/1/0 | 98/2/0 | - | - |
| map:interlock | us27 | 19 | 97/2/0 | 86/13/1 | 96/4/1 | 89/10/0 | 90/9/1 | 90/10/0 | 90/8/1 | 86/12/1 | 87/12/0 | 83/15/2 |
| map:interlock | us26 | 13 | 97/2/1 | 90/10/1 | 89/10/1 | 88/11/1 | 95/5/0 | 94/5/0 | 91/9/0 | 86/13/1 | 86/13/1 | 79/16/5 |
| map:interlock | opp27 | 19 | 88/6/6 | 78/15/7 | 79/11/10 | 80/11/8 | 76/13/11 | 77/11/13 | 78/14/8 | 76/15/9 | 76/12/11 | 68/15/17 |
| map:interlock | opp26 | 13 | 90/6/3 | 76/14/10 | 80/13/7 | 80/11/9 | 84/10/6 | 81/15/5 | 79/12/8 | 79/14/8 | 80/10/10 | 77/12/11 |
| map:lanes | us27 | 17 | 100/0/0 | 86/14/0 | 96/3/1 | 93/6/0 | 95/5/0 | 93/6/1 | 93/6/2 | 94/5/0 | 98/2/0 | 100/0/0 |
| map:lanes | us26 | 18 | 100/0/0 | 85/14/0 | 94/5/1 | 93/6/1 | 94/5/2 | 95/5/0 | 92/6/1 | 95/4/0 | 94/4/2 | 96/4/0 |
| map:lanes | opp27 | 17 | 99/1/1 | 67/15/18 | 69/8/23 | 66/10/24 | 66/10/24 | 67/10/23 | 72/8/20 | 73/8/18 | 58/10/32 | 77/3/20 |
| map:lanes | opp26 | 18 | 99/1/0 | 73/14/12 | 75/8/17 | 67/12/20 | 77/8/15 | 81/11/9 | 78/10/12 | 74/12/14 | 72/12/17 | 76/14/10 |
| map:monolith | us27 | 16 | 100/0/0 | 61/38/1 | 87/10/3 | 80/19/2 | 77/21/2 | 78/20/2 | 76/22/1 | 79/20/2 | 78/21/1 | 72/24/4 |
| map:monolith | us26 | 13 | 100/0/0 | 65/33/2 | 87/10/2 | 83/17/0 | 80/19/1 | 74/23/3 | 82/17/1 | 75/21/3 | 86/13/2 | 76/18/6 |
| map:monolith | opp27 | 16 | 99/1/0 | 92/6/2 | 88/8/5 | 87/10/2 | 84/11/5 | 75/16/9 | 74/15/10 | 74/17/9 | 80/15/5 | 78/19/3 |
| map:monolith | opp26 | 13 | 99/1/0 | 87/10/3 | 84/10/6 | 83/12/5 | 78/12/10 | 79/13/8 | 71/15/14 | 70/19/11 | 69/14/16 | 62/19/19 |
| map:packs | us27 | 22 | 71/29/0 | 85/15/0 | 79/21/0 | 72/27/1 | 84/15/0 | 84/16/0 | 80/19/0 | 78/21/1 | 78/22/0 | 82/18/0 |
| map:packs | us26 | 21 | 73/27/0 | 82/18/0 | 78/22/0 | 79/19/2 | 79/20/1 | 79/20/1 | 79/20/1 | 79/20/1 | 79/20/1 | 79/21/1 |
| map:packs | opp27 | 22 | 88/11/2 | 73/23/4 | 70/25/4 | 71/22/7 | 61/28/11 | 68/24/9 | 66/24/11 | 68/26/6 | 63/28/8 | 67/25/8 |
| map:packs | opp26 | 21 | 85/11/5 | 67/25/8 | 66/25/9 | 60/29/11 | 66/25/9 | 69/22/9 | 66/27/8 | 64/25/12 | 58/32/10 | 65/24/11 |
| map:rows | us27 | 17 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | - |
| map:rows | us26 | 18 | 100/0/0 | 100/0/0 | 100/0/0 | 99/0/1 | 98/0/2 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 |
| map:rows | opp27 | 17 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 99/0/1 | 99/0/1 | 86/0/14 | - |
| map:rows | opp26 | 18 | 100/0/0 | 99/0/0 | 98/0/2 | 100/0/0 | 99/0/0 | 96/0/4 | 98/0/2 | 99/0/1 | 98/0/2 | 80/0/20 |


Differences large relative to the sample: **none for us** — the ALL row is 89/11/0 … 75/23/2 vs 90/10/0 … 75/23/2, and every map row is within the game-to-game spread (per-game means own 85.5±0.9 vs 85.8±0.9, mid 13.5±0.9 vs 13.2±0.9, enemy 1.0±0.2 vs 0.9±0.1). Rows: the one "99/0/1"-"98/0/2" dip of study26 (two carriers wandering into the enemy half in `604a6cf6`) is gone (100/0/0 in every bin). Expanse: 99/1/0 at r300-349 and 94/6/0 at r350-399 — the new visits to the mid 3900-hp groups (per-game mid share 0.6±0.1% vs 0.0, z=5.4, depth 16.6±0.3 vs 14.6±0.1, z=6.5). Monolith mid share 19.2±0.6 vs 17.1±0.7 (z=2.3). **For the opponents**: on lanes they are in our half 18-32% of their rounds from r50 (12-20% in study26; per game 19.3±4.2 vs 12.3±2.8), on interlock 6-17% (3-11%), on monolith 2-10% (3-19%, fewer).

### 1b. Other locations (at spawn / idle at spawn / near altar / near a living camp / nothing)

| split | who | 0-49 | 50-99 | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 | 400-449 | 450+ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 17/2/11/31/9 | 10/1/14/27/9 | 10/1/16/23/10 | 11/1/16/24/9 | 11/1/16/25/8 | 11/1/16/21/8 | 10/1/18/23/8 | 11/1/17/23/10 | 13/1/18/19/9 | 15/2/18/28/10 |
| ALL | us26 | 18/2/10/31/8 | 10/1/14/28/8 | 11/1/16/24/10 | 11/1/16/26/9 | 12/1/15/24/10 | 11/1/17/21/9 | 11/1/17/24/9 | 12/1/17/22/10 | 14/2/17/21/10 | 16/2/17/29/11 |
| ALL | opp27 | 18/1/12/27/8 | 9/1/14/26/10 | 10/1/18/25/10 | 10/1/18/24/10 | 9/1/19/22/11 | 9/1/18/23/11 | 10/1/20/20/10 | 10/1/20/19/10 | 11/1/24/19/11 | 12/2/23/26/12 |
| ALL | opp26 | 19/1/11/26/8 | 9/1/15/25/10 | 10/1/17/25/10 | 10/1/17/24/11 | 9/1/19/23/10 | 9/1/18/22/12 | 9/1/19/22/12 | 10/1/19/20/11 | 11/1/21/19/10 | 13/1/22/28/10 |
| map:expanse | us27 | 20/5/6/33/11 | 8/1/20/36/4 | 7/1/17/17/10 | 17/2/17/28/3 | 8/0/18/29/8 | 8/0/16/10/2 | 6/0/13/23/5 | 8/0/18/18/10 | - | - |
| map:expanse | us26 | 20/5/6/33/11 | 8/1/20/36/4 | 7/1/17/17/10 | 17/2/17/29/3 | 8/0/18/29/8 | 9/0/18/9/3 | 9/1/17/26/9 | 1/0/42/12/6 | - | - |
| map:expanse | opp27 | 18/1/8/25/8 | 5/0/18/25/12 | 6/0/15/26/10 | 7/1/15/22/10 | 7/1/21/20/10 | 6/0/13/24/13 | 6/1/19/18/14 | 8/1/19/18/15 | - | - |
| map:expanse | opp26 | 19/1/6/26/9 | 7/1/18/23/12 | 7/0/13/25/13 | 8/1/15/24/11 | 6/0/20/20/11 | 6/0/14/24/14 | 8/1/21/19/16 | 13/2/17/13/20 | - | - |
| map:lanes | us27 | 13/4/19/22/12 | 1/0/14/52/16 | 8/0/26/28/10 | 6/1/20/35/15 | 4/1/21/33/13 | 6/1/21/30/15 | 6/1/22/33/13 | 6/1/21/32/15 | 7/1/24/23/15 | 5/1/27/30/11 |
| map:lanes | us26 | 13/4/18/22/12 | 1/0/13/51/15 | 7/1/21/35/11 | 5/1/19/36/14 | 5/1/21/36/15 | 6/1/22/28/15 | 4/0/19/35/15 | 7/1/20/32/15 | 7/1/23/24/15 | 8/1/23/27/15 |
| map:lanes | opp27 | 7/1/29/21/10 | 2/0/14/45/11 | 2/0/24/36/15 | 3/0/21/36/14 | 2/0/20/36/15 | 3/1/20/36/15 | 2/0/24/34/14 | 3/1/22/32/15 | 2/0/18/32/16 | 5/1/53/6/5 |
| map:lanes | opp26 | 8/1/30/19/9 | 2/0/15/43/10 | 2/0/23/34/13 | 2/0/19/39/14 | 3/1/22/33/12 | 3/0/19/34/13 | 2/0/22/34/14 | 3/1/22/30/14 | 3/0/24/27/11 | 1/0/22/47/12 |
| map:monolith | us27 | 13/3/0/34/6 | 5/1/18/15/3 | 8/2/6/20/11 | 6/1/14/22/5 | 6/1/15/21/5 | 6/1/14/18/5 | 7/1/17/21/6 | 6/1/16/20/7 | 6/1/15/16/6 | 9/1/18/13/7 |
| map:monolith | us26 | 13/3/0/34/5 | 5/1/19/13/4 | 7/1/7/18/9 | 6/1/13/23/4 | 6/1/13/18/5 | 5/1/18/20/4 | 6/1/12/18/5 | 7/1/17/18/5 | 8/1/11/17/6 | 11/1/21/17/7 |
| map:monolith | opp27 | 12/1/2/28/8 | 6/1/9/22/10 | 6/1/11/20/9 | 5/1/15/22/11 | 5/1/16/20/9 | 5/1/18/21/11 | 7/1/18/19/8 | 5/1/16/17/7 | 6/1/16/12/9 | 6/1/18/15/9 |
| map:monolith | opp26 | 12/1/1/26/9 | 7/1/10/20/8 | 5/1/10/21/10 | 6/1/12/21/9 | 5/1/11/21/9 | 6/1/13/17/9 | 5/1/15/18/10 | 4/1/17/18/9 | 6/1/15/16/10 | 3/1/19/21/7 |
| map:packs | us27 | 11/0/12/31/9 | 17/1/15/17/10 | 16/2/15/19/11 | 18/2/16/18/12 | 19/2/18/20/8 | 20/2/17/21/7 | 20/2/19/17/9 | 19/2/20/16/9 | 22/2/21/15/9 | 24/2/23/13/9 |
| map:packs | us26 | 12/0/13/30/9 | 16/1/13/19/9 | 16/2/15/19/10 | 19/2/16/19/7 | 18/2/17/17/11 | 18/1/16/19/9 | 17/2/18/18/9 | 19/2/20/17/10 | 23/2/22/12/9 | 18/2/19/16/10 |
| map:packs | opp27 | 30/1/20/18/6 | 15/1/17/23/9 | 20/1/20/15/7 | 18/1/20/17/8 | 18/1/20/17/8 | 18/2/20/16/10 | 21/2/22/14/9 | 16/1/22/14/9 | 19/1/23/13/9 | 18/2/26/12/11 |
| map:packs | opp26 | 27/1/19/18/6 | 15/1/20/21/10 | 18/2/21/16/9 | 20/2/20/17/10 | 21/1/19/16/8 | 19/1/21/14/10 | 19/2/20/17/10 | 17/1/24/13/9 | 20/1/25/13/10 | 20/1/24/12/10 |
| map:rows | us27 | 12/0/2/37/5 | 9/0/4/18/12 | 5/0/8/24/8 | 5/0/8/22/6 | 11/1/9/29/5 | 5/1/8/18/7 | 8/1/13/13/7 | 7/1/9/22/11 | 7/1/14/16/15 | - |
| map:rows | us26 | 15/0/1/36/3 | 10/0/8/21/5 | 8/1/10/18/13 | 8/0/8/21/9 | 7/0/7/22/18 | 8/0/8/18/11 | 11/1/12/17/7 | 6/1/9/20/7 | 8/0/8/12/6 | 20/20/20/0/80 |
| map:rows | opp27 | 13/1/2/25/3 | 8/1/5/19/9 | 8/1/8/18/7 | 8/1/10/18/10 | 7/1/10/16/9 | 7/1/10/13/11 | 7/1/12/11/11 | 6/1/12/11/10 | 12/2/14/13/13 | - |
| map:rows | opp26 | 13/1/2/27/3 | 7/1/5/22/10 | 8/1/9/20/9 | 7/1/10/20/10 | 6/1/10/19/12 | 7/1/11/15/13 | 7/1/12/14/13 | 7/1/13/11/13 | 5/0/15/11/12 | 20/20/20/20/80 |

No change (ALL us 17/2/11/31/9 … 15/2/18/28/10 vs 18/2/10/31/8 … 16/2/17/29/11). Rows r50-99: "nothing" 12% vs 5% and next-to-camp 18% vs 21% — the 4-stack waits for the pack respawn together (see 3c, where the streaks are fewer but still there). Full table in `cmp_tables.md`.

### 1c. Enemy-half episodes (one champion crossing into enemy territory)

| split | who | games | episodes | per game | median len | median start r | hits camp there | hits enemy there | gets hit there | captures there | tributes there | ends dead | median score diff at entry | nearest enemy <=8 at entry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 155 | 465 | 3.0 | 5 | 256 | 11% | 49% | 37% | 12% | 4% | 4% | +96 | 84% |
| ALL | us26 | 150 | 437 | 2.9 | 6 | 283 | 13% | 44% | 34% | 16% | 3% | 5% | +22 | 78% |
| ALL | opp27 | 155 | 1702 | 11.0 | 8 | 284 | 20% | 55% | 53% | 9% | 8% | 9% | +44 | 86% |
| ALL | opp26 | 150 | 1788 | 11.9 | 8 | 297 | 19% | 53% | 51% | 10% | 7% | 8% | +23 | 85% |
| map:collision | us27 | 19 | 36 | 1.9 | 3 | 289 | 22% | 69% | 44% | 2% | 0% | 0% | +44 | 100% |
| map:collision | us26 | 19 | 33 | 1.7 | 5 | 286 | 0% | 69% | 51% | 3% | 0% | 15% | +22 | 100% |
| map:collision | opp27 | 19 | 201 | 10.6 | 8 | 354 | 19% | 61% | 65% | 7% | 0% | 10% | +66 | 89% |
| map:collision | opp26 | 19 | 217 | 11.4 | 7 | 356 | 17% | 58% | 58% | 6% | 0% | 7% | +22 | 92% |
| map:corners | us27 | 19 | 177 | 9.3 | 4 | 275 | 11% | 64% | 48% | 6% | 6% | 7% | +236 | 93% |
| map:corners | us26 | 17 | 121 | 7.1 | 4 | 271 | 14% | 48% | 37% | 13% | 11% | 4% | +150 | 88% |
| map:corners | opp27 | 19 | 530 | 27.9 | 8 | 301 | 19% | 62% | 63% | 4% | 4% | 3% | +157 | 93% |
| map:corners | opp26 | 17 | 580 | 34.1 | 8 | 304 | 19% | 59% | 59% | 4% | 5% | 5% | +48 | 90% |
| map:elkring | us27 | 9 | 54 | 6.0 | 10 | 357 | 25% | 51% | 35% | 14% | 0% | 3% | +36 | 66% |
| map:elkring | us26 | 14 | 108 | 7.7 | 10 | 323 | 18% | 43% | 27% | 15% | 0% | 2% | -36 | 76% |
| map:elkring | opp27 | 9 | 140 | 15.6 | 12 | 348 | 42% | 41% | 53% | 17% | 5% | 26% | +36 | 73% |
| map:elkring | opp26 | 14 | 242 | 17.3 | 10 | 354 | 30% | 45% | 49% | 15% | 5% | 16% | +54 | 72% |
| map:expanse | us27 | 17 | 0 |
| map:expanse | us26 | 17 | 0 |
| map:expanse | opp27 | 17 | 1 | 0.1 | 182 | 47 | 100% | 100% | 100% | 100% | 100% | 100% | -48 | 0% |
| map:expanse | opp26 | 17 | 1 | 0.1 | 227 | 47 | 100% | 100% | 100% | 100% | 100% | 100% | -48 | 0% |
| map:interlock | us27 | 19 | 44 | 2.3 | 6 | 263 | 2% | 72% | 45% | 0% | 0% | 4% | +83 | 100% |
| map:interlock | us26 | 13 | 35 | 2.7 | 5 | 209 | 2% | 77% | 54% | 2% | 0% | 5% | +88 | 94% |
| map:interlock | opp27 | 19 | 312 | 16.4 | 6 | 259 | 12% | 56% | 51% | 3% | 11% | 10% | +22 | 85% |
| map:interlock | opp26 | 13 | 175 | 13.5 | 7 | 245 | 10% | 46% | 43% | 3% | 9% | 7% | -22 | 91% |
| map:lanes | us27 | 17 | 24 | 1.4 | 8 | 259 | 20% | 25% | 25% | 45% | 0% | 4% | -41 | 50% |
| map:lanes | us26 | 18 | 36 | 2.0 | 6 | 202 | 19% | 19% | 27% | 38% | 0% | 8% | -14 | 58% |
| map:lanes | opp27 | 17 | 175 | 10.3 | 9 | 234 | 30% | 50% | 36% | 30% | 18% | 5% | +0 | 90% |
| map:lanes | opp26 | 18 | 238 | 13.2 | 6 | 220 | 21% | 40% | 33% | 23% | 13% | 5% | +0 | 88% |
| map:monolith | us27 | 16 | 111 | 6.9 | 2 | 226 | 1% | 12% | 14% | 22% | 6% | 1% | +148 | 73% |
| map:monolith | us26 | 13 | 61 | 4.7 | 7 | 283 | 6% | 22% | 22% | 26% | 4% | 4% | +38 | 57% |
| map:monolith | opp27 | 16 | 104 | 6.5 | 11 | 274 | 24% | 42% | 34% | 12% | 11% | 13% | +2 | 72% |
| map:monolith | opp26 | 13 | 101 | 7.8 | 18 | 321 | 23% | 51% | 39% | 20% | 8% | 12% | -30 | 63% |
| map:packs | us27 | 22 | 19 | 0.9 | 5 | 197 | 15% | 52% | 63% | 15% | 0% | 5% | +0 | 89% |
| map:packs | us26 | 21 | 40 | 1.9 | 4 | 344 | 17% | 40% | 37% | 17% | 0% | 2% | +0 | 75% |
| map:packs | opp27 | 22 | 238 | 10.8 | 8 | 275 | 14% | 52% | 46% | 11% | 11% | 8% | +76 | 83% |
| map:packs | opp26 | 21 | 229 | 10.9 | 11 | 284 | 14% | 55% | 55% | 10% | 15% | 13% | +40 | 85% |
| map:rows | us27 | 17 | 0 |
| map:rows | us26 | 18 | 3 | 0.2 | 33 | 190 | 0% | 0% | 0% | 0% | 0% | 0% | -66 | 0% |
| map:rows | opp27 | 17 | 1 | 0.1 | 53 | 294 | 0% | 100% | 100% | 0% | 0% | 0% | +0 | 0% |
| map:rows | opp26 | 18 | 5 | 0.3 | 69 | 241 | 0% | 100% | 100% | 0% | 40% | 80% | +66 | 20% |

Us: 465 episodes (3.0/game) vs 437 (2.9); 84% begin with an enemy within 8 (78%): still chases, not raids. Per map the only counts that moved beyond noise are **packs 19 vs 40** (0.9 vs 1.9/game; fewer chases because fewer of their champions die near us) and **monolith 111 vs 61** (6.9 vs 4.7/game; median length 2 rounds, 1% hit a camp, 12% hit an enemy, 22% capture there: brief crossings of the band around the (36,40)-(45,41) camps, 24 vs 16 captures of enemy groups in total). Corners 177 vs 121 (9.3 vs 7.1/game) is the same rate per contact. Opponents: 1702 (11.0/game) vs 1788 (11.9); lanes 175 vs 238 episodes but longer and more productive (30% hit a camp, 30% capture, 18% tribute there vs 21/23/13%); interlock 312 vs 175 (16.4 vs 13.5/game, 19 vs 13 games).

### 1d. What we do when an enemy stands in our half

| split | batch | rounds with invader | our champ-rounds | near invader (<=8) | own/mid/enemy where we are | actions (all) | actions when near |
|---|---|---|---|---|---|---|---|
| ALL | 27 | 17140 | 66179 | 43% | 89/9/0 | move 55%, attack camp 13%, nothing 9%, recall 7%, tribute 5%, dash 3%, cast@champ 2%, attack champ 2%, cast@camp 2%, buy 1%, ability(no eff) 1%, arrive 0%, attack(miss) 0% | move 53%, nothing 12%, attack camp 8%, recall 6%, cast@champ 5%, attack champ 5%, tribute 3%, dash 3%, cast@camp 2%, ability(no eff) 1%, attack(miss) 0%, buy 0%, arrive 0% |
| ALL | 26 | 17064 | 64366 | 44% | 88/10/1 | move 53%, attack camp 14%, nothing 10%, recall 7%, tribute 5%, cast@champ 3%, attack champ 2%, dash 2%, cast@camp 2%, buy 1%, ability(no eff) 0%, arrive 0%, attack(miss) 0% | move 52%, nothing 12%, attack camp 9%, recall 7%, cast@champ 5%, attack champ 5%, tribute 4%, dash 3%, cast@camp 2%, ability(no eff) 1%, attack(miss) 0%, buy 0%, arrive 0% |
| map:lanes | 27 | 3274 | 16653 | 39% | 93/5/0 | move 56%, attack camp 16%, nothing 12%, tribute 5%, recall 4%, dash 2%, attack champ 2%, cast@camp 2%, ability(no eff) 1%, buy 0%, arrive 0%, cast@champ 0%, attack(miss) 0% | move 56%, nothing 16%, attack camp 11%, attack champ 4%, tribute 4%, recall 2%, dash 2%, ability(no eff) 2%, cast@camp 1%, cast@champ 1%, attack(miss) 0% |
| map:lanes | 26 | 2780 | 13785 | 39% | 94/4/0 | move 54%, attack camp 16%, nothing 12%, tribute 6%, recall 3%, dash 2%, attack champ 2%, cast@camp 2%, ability(no eff) 1%, cast@champ 0%, buy 0%, arrive 0%, attack(miss) 0% | move 53%, nothing 15%, attack camp 13%, attack champ 5%, tribute 4%, recall 3%, dash 2%, cast@camp 2%, ability(no eff) 2%, cast@champ 1%, attack(miss) 0% |
| map:monolith | 27 | 1733 | 9331 | 23% | 78/19/1 | move 58%, attack camp 15%, tribute 7%, recall 7%, nothing 6%, dash 2%, cast@camp 2%, attack champ 2%, buy 1%, arrive 0%, ability(no eff) 0%, cast@champ 0%, attack(miss) 0% | move 68%, nothing 7%, attack camp 7%, attack champ 5%, tribute 4%, dash 3%, recall 2%, ability(no eff) 1%, cast@champ 1%, cast@camp 1%, buy 0%, attack(miss) 0% |
| map:monolith | 26 | 1785 | 9254 | 28% | 82/15/2 | move 58%, attack camp 16%, nothing 6%, recall 6%, tribute 5%, dash 2%, cast@camp 2%, attack champ 2%, buy 1%, ability(no eff) 1%, cast@champ 0%, arrive 0%, attack(miss) 0% | move 67%, attack camp 10%, nothing 8%, attack champ 5%, recall 2%, dash 2%, ability(no eff) 2%, cast@champ 1%, cast@camp 1%, tribute 1%, attack(miss) 0%, buy 0% |
| map:packs | 27 | 2166 | 5985 | 52% | 90/9/0 | move 40%, attack camp 15%, recall 10%, nothing 9%, tribute 7%, dash 4%, attack champ 4%, cast@champ 3%, cast@camp 3%, ability(no eff) 1%, buy 1%, arrive 1%, attack(miss) 0% | move 45%, recall 12%, attack camp 10%, nothing 10%, attack champ 7%, cast@champ 6%, dash 3%, tribute 3%, cast@camp 2%, ability(no eff) 2%, attack(miss) 1%, arrive 0% |
| map:packs | 26 | 2558 | 7206 | 55% | 85/13/1 | move 40%, attack camp 18%, nothing 9%, recall 9%, tribute 7%, cast@camp 4%, dash 4%, attack champ 3%, cast@champ 3%, ability(no eff) 1%, buy 1%, arrive 1%, attack(miss) 0% | move 43%, attack camp 12%, nothing 10%, recall 9%, attack champ 6%, tribute 6%, cast@champ 5%, dash 4%, cast@camp 3%, ability(no eff) 1%, attack(miss) 1%, buy 0%, arrive 0% |
| map:rows | 27 | 113 | 516 | 30% | 100/0/0 | move 52%, attack camp 21%, tribute 10%, nothing 7%, recall 6%, dash 1%, attack champ 1%, cast@camp 1%, buy 1%, cast@champ 0% | move 61%, tribute 11%, attack camp 9%, nothing 7%, attack champ 4%, recall 3%, dash 3%, cast@camp 2%, cast@champ 1% |
| map:rows | 26 | 460 | 2230 | 37% | 100/0/0 | move 48%, attack camp 20%, nothing 11%, tribute 10%, recall 5%, dash 2%, cast@camp 2%, attack champ 1%, buy 0%, arrive 0%, ability(no eff) 0%, cast@champ 0%, attack(miss) 0% | move 54%, tribute 22%, attack camp 9%, nothing 7%, attack champ 4%, dash 2%, recall 1%, cast@camp 1%, cast@champ 0%, ability(no eff) 0%, attack(miss) 0% |

Identical: near an invader we move 53% (52), stand 12% (12), attack a camp 8% (9), fight 10% (10). Lanes: fight 5% (6). The rule "no collective answer to an invader" is unchanged.


## 2. Spread and formation (Q2)

### 2a. Spread

| split | who | rounds | mean pd | median pd | max pd (mean) | largest cluster (mean) | share of team in largest cluster | all together | all apart | alone | alone: melee/caster/ranged | alone & enemy<=8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 36728 | 10.61 | 9.7 | 17.88 | 2.06 | 49% | 7% | 31% | 30% | 33/25/0% | 19% |
| ALL | us26 | 35586 | 10.56 | 9.9 | 17.68 | 2.01 | 48% | 7% | 31% | 29% | 33/25/0% | 21% |
| ALL | opp27 | 37983 | 11.17 | 10.7 | 19.11 | 2.13 | 49% | 7% | 31% | 31% | 35/27/20% | 23% |
| ALL | opp26 | 36620 | 11.54 | 11.0 | 19.75 | 2.11 | 47% | 6% | 32% | 32% | 36/28/18% | 25% |
| map:collision | us27 | 6166 | 7.14 | 6.8 | 10.61 | 2.02 | 60% | 16% | 30% | 19% | 22/17/0% | 11% |
| map:collision | us26 | 6113 | 7.14 | 7.0 | 10.86 | 2.05 | 59% | 16% | 27% | 19% | 21/17/0% | 10% |
| map:collision | opp27 | 6660 | 8.84 | 8.3 | 13.03 | 1.87 | 57% | 13% | 37% | 29% | 30/27/0% | 22% |
| map:collision | opp26 | 6465 | 9.05 | 8.7 | 13.36 | 1.86 | 55% | 11% | 37% | 29% | 31/27/0% | 23% |
| map:corners | us27 | 5081 | 9.27 | 8.9 | 14.59 | 2.14 | 55% | 13% | 32% | 28% | 28/27/0% | 13% |
| map:corners | us26 | 4552 | 8.93 | 8.7 | 13.89 | 2.17 | 57% | 15% | 31% | 28% | 28/27/0% | 13% |
| map:corners | opp27 | 5290 | 10.34 | 10.0 | 18.85 | 2.65 | 54% | 9% | 17% | 23% | 24/21/23% | 7% |
| map:corners | opp26 | 4698 | 10.52 | 10.3 | 19.64 | 2.72 | 53% | 9% | 15% | 24% | 26/22/19% | 8% |
| map:elkring | us27 | 2795 | 10.05 | 10.2 | 16.99 | 2.05 | 45% | 4% | 29% | 27% | 30/24/0% | 34% |
| map:elkring | us26 | 4094 | 9.88 | 10.2 | 16.54 | 1.99 | 45% | 3% | 31% | 25% | 28/23/0% | 34% |
| map:elkring | opp27 | 2723 | 9.78 | 9.8 | 17.04 | 2.54 | 52% | 6% | 18% | 22% | 25/17/26% | 29% |
| map:elkring | opp26 | 4115 | 10.47 | 10.8 | 17.97 | 2.38 | 48% | 5% | 22% | 25% | 29/18/20% | 31% |
| map:expanse | us27 | 3105 | 17.31 | 17.0 | 28.70 | 1.45 | 36% | 4% | 67% | 65% | 64/68/0% | 40% |
| map:expanse | us26 | 2959 | 16.53 | 16.7 | 26.80 | 1.44 | 36% | 4% | 68% | 66% | 66/65/0% | 42% |
| map:expanse | opp27 | 3105 | 16.83 | 16.2 | 27.61 | 1.47 | 36% | 2% | 65% | 59% | 61/57/0% | 100% |
| map:expanse | opp26 | 2959 | 18.19 | 17.3 | 29.89 | 1.35 | 33% | 1% | 72% | 65% | 67/62/0% | 100% |
| map:interlock | us27 | 4596 | 8.23 | 8.1 | 14.01 | 2.29 | 50% | 5% | 21% | 19% | 21/18/0% | 15% |
| map:interlock | us26 | 3074 | 8.53 | 8.6 | 14.69 | 2.21 | 48% | 4% | 22% | 21% | 25/18/0% | 17% |
| map:interlock | opp27 | 4694 | 9.25 | 9.2 | 15.14 | 2.03 | 48% | 5% | 32% | 26% | 28/24/19% | 25% |
| map:interlock | opp26 | 3090 | 9.36 | 9.2 | 15.40 | 2.03 | 47% | 5% | 32% | 27% | 31/24/0% | 23% |
| map:lanes | us27 | 3181 | 13.35 | 13.3 | 24.72 | 2.21 | 40% | 4% | 24% | 30% | 35/19/0% | 22% |
| map:lanes | us26 | 3578 | 12.85 | 12.9 | 23.77 | 2.20 | 40% | 4% | 23% | 26% | 31/16/0% | 17% |
| map:lanes | opp27 | 3206 | 12.95 | 13.1 | 25.82 | 2.49 | 42% | 4% | 17% | 26% | 30/21/19% | 25% |
| map:lanes | opp26 | 3578 | 12.50 | 12.2 | 25.01 | 2.49 | 43% | 4% | 20% | 26% | 29/23/17% | 29% |
| map:monolith | us27 | 3582 | 16.97 | 16.5 | 30.43 | 1.78 | 31% | 0% | 35% | 45% | 45/45/0% | 44% |
| map:monolith | us26 | 2907 | 16.53 | 16.0 | 29.28 | 1.76 | 32% | 0% | 37% | 45% | 46/45/0% | 48% |
| map:monolith | opp27 | 3582 | 15.93 | 16.5 | 28.57 | 1.99 | 35% | 1% | 33% | 44% | 48/37/0% | 59% |
| map:monolith | opp26 | 2907 | 17.33 | 17.7 | 30.54 | 1.81 | 32% | 0% | 41% | 49% | 50/48/57% | 60% |
| map:packs | us27 | 4892 | 8.07 | 7.8 | 11.71 | 1.75 | 51% | 5% | 39% | 28% | 30/26/0% | 25% |
| map:packs | us26 | 4698 | 8.26 | 8.2 | 12.26 | 1.74 | 49% | 3% | 40% | 29% | 33/25/0% | 29% |
| map:packs | opp27 | 5393 | 9.52 | 9.3 | 14.46 | 1.75 | 49% | 5% | 44% | 36% | 40/31/0% | 35% |
| map:packs | opp26 | 5197 | 9.71 | 9.7 | 14.49 | 1.72 | 48% | 5% | 46% | 37% | 42/32/0% | 37% |
| map:rows | us27 | 3330 | 10.92 | 11.3 | 21.37 | 2.88 | 57% | 3% | 3% | 17% | 21/4/0% | 26% |
| map:rows | us26 | 3611 | 11.89 | 11.4 | 22.08 | 2.41 | 48% | 2% | 11% | 20% | 21/15/0% | 27% |
| map:rows | opp27 | 3330 | 11.54 | 12.0 | 21.98 | 2.68 | 53% | 7% | 7% | 22% | 27/15/9% | 100% |
| map:rows | opp26 | 3611 | 11.97 | 12.3 | 22.47 | 2.59 | 52% | 6% | 10% | 24% | 29/16/10% | 87% |

ALL: mean pairwise distance 10.61 vs 10.56, largest cluster 2.06 vs 2.01, alone 30% vs 29%, alone-with-enemy 19% vs 21%: no change. **Rows is the exception and it is the stacking rule**: largest cluster 2.88 champions = 57% of the team (2.41 / 48%), all-apart rounds 3% (11%), alone 17% (20%) and the casters are alone 4% of their rounds (15%): Cassi now stands in the 4-stack instead of at her waiting tile. Expanse pd 17.3 vs 16.5 (the pairs sent to the 3900 groups walk further). Per-game: rows pd 10.9±0.1 vs 11.9±0.1 (z=-11), alone 18.1±0.3 vs 20.5±0.5 (z=-4.0); every other map within 1 SE.

### 2b. Formation when an enemy is within 8

| split | who | melee d | caster d | ranged d | rounds caster+melee | melee front | level | caster front | gap | ranged vs melee: melee front/level/ranged front | engaged/alive |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 5.20/5 | 5.36/5 | - | 11001 | 44% | 16% | 39% | +0.18 | 0%/0%/0% | 50% |
| ALL | us26 | 5.26/5 | 5.41/5 | - | 10319 | 44% | 16% | 38% | +0.23 | 0%/0%/0% | 50% |
| ALL | opp27 | 5.01/5 | 5.54/5 | 5.18/5 | 9082 | 53% | 16% | 30% | +0.69 | 57%/16%/25% | 46% |
| ALL | opp26 | 5.06/5 | 5.51/5 | 5.57/6 | 8272 | 50% | 16% | 32% | +0.54 | 57%/15%/27% | 45% |
| map:collision | us27 | 5.39/6 | 5.47/6 | - | 2570 | 44% | 16% | 38% | +0.18 | 0%/0%/0% | 59% |
| map:collision | us26 | 5.44/6 | 5.58/6 | - | 2592 | 43% | 16% | 39% | +0.23 | 0%/0%/0% | 58% |
| map:collision | opp27 | 5.08/5 | 5.74/6 | - | 1918 | 52% | 17% | 29% | +0.74 | 0%/0%/0% | 54% |
| map:collision | opp26 | 5.14/5 | 5.69/6 | - | 1713 | 51% | 17% | 31% | +0.62 | 0%/0%/0% | 52% |
| map:corners | us27 | 4.69/5 | 5.01/5 | - | 2751 | 44% | 17% | 37% | +0.22 | 0%/0%/0% | 63% |
| map:corners | us26 | 4.68/5 | 4.94/5 | - | 2336 | 42% | 19% | 38% | +0.15 | 0%/0%/0% | 63% |
| map:corners | opp27 | 4.78/5 | 5.25/5 | 5.18/5 | 2795 | 54% | 16% | 28% | +0.68 | 58%/18%/23% | 57% |
| map:corners | opp26 | 4.82/5 | 5.28/5 | 5.59/6 | 2488 | 51% | 16% | 32% | +0.54 | 63%/13%/23% | 56% |
| map:elkring | us27 | 5.28/5 | 5.71/6 | - | 686 | 46% | 15% | 38% | +0.21 | 0%/0%/0% | 41% |
| map:elkring | us26 | 5.43/6 | 5.70/6 | - | 962 | 44% | 15% | 40% | +0.08 | 0%/0%/0% | 42% |
| map:elkring | opp27 | 5.45/6 | 5.92/6 | 5.53/5 | 593 | 54% | 16% | 29% | +0.87 | 66%/6%/27% | 41% |
| map:elkring | opp26 | 5.36/6 | 5.82/6 | 6.25/7 | 857 | 53% | 18% | 28% | +0.75 | 47%/17%/34% | 41% |
| map:expanse | us27 | 5.84/6 | 5.78/6 | - | 24 | 45% | 12% | 41% | +0.12 | 0%/0%/0% | 39% |
| map:expanse | us26 | 5.68/6 | 5.62/6 | - | 21 | 47% | 9% | 42% | +0.10 | 0%/0%/0% | 39% |
| map:interlock | us27 | 5.32/6 | 5.49/6 | - | 1739 | 39% | 16% | 43% | -0.05 | 0%/0%/0% | 46% |
| map:interlock | us26 | 5.37/6 | 5.68/6 | - | 1039 | 43% | 18% | 38% | +0.26 | 0%/0%/0% | 44% |
| map:interlock | opp27 | 5.04/5 | 5.65/6 | 5.89/6 | 1171 | 54% | 17% | 28% | +0.85 | 0%/0%/0% | 44% |
| map:interlock | opp26 | 5.25/5 | 5.57/6 | - | 693 | 43% | 16% | 40% | +0.20 | 0%/0%/0% | 43% |
| map:lanes | us27 | 5.43/6 | 5.56/6 | - | 1128 | 48% | 15% | 35% | +0.49 | 0%/0%/0% | 43% |
| map:lanes | us26 | 5.58/6 | 5.67/6 | - | 1167 | 51% | 14% | 33% | +0.60 | 0%/0%/0% | 43% |
| map:lanes | opp27 | 5.18/5 | 5.53/6 | 4.71/4 | 927 | 50% | 15% | 33% | +0.41 | 46%/12%/40% | 37% |
| map:lanes | opp26 | 5.36/6 | 5.48/6 | 5.21/5 | 803 | 48% | 18% | 33% | +0.43 | 38%/22%/39% | 34% |
| map:monolith | us27 | 5.18/5 | 5.30/5 | - | 640 | 51% | 16% | 32% | +0.50 | 0%/0%/0% | 31% |
| map:monolith | us26 | 5.16/5 | 5.34/6 | - | 550 | 48% | 18% | 33% | +0.48 | 0%/0%/0% | 33% |
| map:monolith | opp27 | 4.90/5 | 5.66/6 | - | 455 | 56% | 16% | 27% | +0.77 | 0%/0%/0% | 28% |
| map:monolith | opp26 | 4.84/5 | 5.46/5 | 4.95/4 | 387 | 50% | 14% | 34% | +0.63 | 0%/25%/75% | 29% |
| map:packs | us27 | 5.27/5 | 5.44/5 | - | 1456 | 42% | 15% | 42% | +0.00 | 0%/0%/0% | 53% |
| map:packs | us26 | 5.27/5 | 5.36/5 | - | 1593 | 44% | 14% | 40% | +0.02 | 0%/0%/0% | 55% |
| map:packs | opp27 | 4.98/5 | 5.60/5 | - | 1223 | 52% | 13% | 34% | +0.55 | 0%/0%/0% | 46% |
| map:packs | opp26 | 4.82/5 | 5.55/5 | - | 1316 | 50% | 15% | 33% | +0.55 | 0%/0%/0% | 48% |
| map:rows | us27 | 5.19/5 | 7.00/7 | - | 7 | 71% | 0% | 28% | +2.14 | 0%/0%/0% | 41% |
| map:rows | us26 | 4.96/5 | 5.94/6 | - | 59 | 55% | 18% | 25% | +1.27 | 0%/0%/0% | 42% |
| map:rows | opp26 | 4.57/4 | 3.63/3 | - | 15 | 53% | 6% | 40% | +0.27 | 0%/0%/0% | 22% |

Melee strictly in front 44% / level 16% / caster in front 39% (study26 44/16/38), gap +0.18 (+0.23); casters 5.36 tiles from the nearest enemy, melee 5.20 (5.41/5.26). Interlock gap went to -0.05 (caster in front 43%, 1739 rounds vs 1039) — the one map where we are now literally caster-first, but the 19-vs-13-game samples overlap. The opponents' gap widened to +0.69 (+0.54), i.e. the pool's melee lead by two-thirds of a tile; ours by a fifth.


## 3. What each champion does per round (Q3)

### 3a. Action share (type = ALL)

| split | who | type | n rounds | move | attack camp | cast@camp | attack champ | cast@champ | dash | ability(no eff) | tribute | recall | buy | nothing | arrive | attack(miss) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | ALL | 319430 | 50 | 19 | 3 | 1 | 1 | 3 | 0 | 6 | 6 | 1 | 9 | 0 | 0 |
| ALL | us26 | ALL | 308639 | 50 | 19 | 3 | 1 | 1 | 3 | 0 | 6 | 6 | 1 | 9 | 0 | 0 |
| ALL | opp27 | ALL | 337622 | 48 | 17 | 3 | 1 | 1 | 2 | 0 | 7 | 8 | 1 | 10 | 0 | 0 |
| ALL | opp26 | ALL | 329013 | 49 | 18 | 3 | 1 | 1 | 2 | 0 | 7 | 8 | 1 | 10 | 0 | 0 |
| res:win | us27 | ALL | 131658 | 49 | 18 | 3 | 1 | 2 | 2 | 0 | 8 | 6 | 1 | 9 | 0 | 0 |
| res:win | us26 | ALL | 129082 | 49 | 19 | 3 | 1 | 1 | 3 | 0 | 7 | 6 | 1 | 9 | 0 | 0 |
| res:win | opp27 | ALL | 123156 | 50 | 17 | 3 | 1 | 1 | 2 | 1 | 6 | 9 | 0 | 10 | 0 | 0 |
| res:win | opp26 | ALL | 123133 | 51 | 18 | 3 | 1 | 1 | 2 | 0 | 6 | 6 | 0 | 11 | 0 | 0 |
| res:loss | us27 | ALL | 187772 | 51 | 19 | 3 | 1 | 1 | 3 | 0 | 5 | 6 | 1 | 9 | 0 | 0 |
| res:loss | us26 | ALL | 179557 | 51 | 19 | 3 | 1 | 1 | 2 | 0 | 5 | 6 | 1 | 10 | 0 | 0 |
| res:loss | opp27 | ALL | 214466 | 48 | 18 | 3 | 1 | 1 | 2 | 0 | 8 | 8 | 1 | 10 | 0 | 0 |
| res:loss | opp26 | ALL | 205880 | 47 | 17 | 3 | 1 | 1 | 2 | 1 | 7 | 9 | 1 | 10 | 0 | 0 |
| opp:top10 | us27 | ALL | 94346 | 50 | 20 | 3 | 1 | 1 | 3 | 0 | 6 | 6 | 1 | 9 | 0 | 0 |
| opp:top10 | us26 | ALL | 94282 | 49 | 19 | 3 | 1 | 1 | 3 | 0 | 6 | 7 | 1 | 10 | 0 | 0 |
| opp:top10 | opp27 | ALL | 103554 | 44 | 17 | 3 | 1 | 1 | 2 | 0 | 7 | 14 | 1 | 9 | 0 | 0 |
| opp:top10 | opp26 | ALL | 103744 | 44 | 17 | 3 | 1 | 1 | 2 | 0 | 7 | 14 | 1 | 9 | 0 | 0 |
| opp:r11-30 | us27 | ALL | 225084 | 50 | 18 | 3 | 1 | 2 | 3 | 0 | 6 | 6 | 1 | 9 | 0 | 0 |
| opp:r11-30 | us26 | ALL | 214357 | 50 | 19 | 3 | 1 | 1 | 2 | 0 | 6 | 6 | 1 | 9 | 0 | 0 |
| opp:r11-30 | opp27 | ALL | 234068 | 50 | 17 | 3 | 1 | 1 | 2 | 1 | 7 | 5 | 1 | 11 | 0 | 0 |
| opp:r11-30 | opp26 | ALL | 225269 | 51 | 18 | 3 | 1 | 1 | 2 | 1 | 6 | 5 | 1 | 11 | 0 | 0 |

Identical to the percent (move 50, attack camp 19, cast@camp 3, tribute 6, recall 6, nothing 9, fight 2, dash 3). Dead share of champion-rounds: us 13% (13), opp 9% (9); per map us collision 23 (22), corners 25 (27), packs 19 (18), interlock 11 (9), lanes 8 (9), monolith 5 (7). Per type (full table in `q3_actions.out`): Varg attack-camp 23→22%, Issac 26→27%, nothing per type within 1 point.

### 3b. Where the idle rounds happen

| split | who | idle rounds | spawn | altar | camp | own | mid | enemy | enemy<=8 | enemy<=3 | hp<50% | carrying gems | camp awake next to it |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 28811 | 7% | 14% | 17% | 53% | 7% | 1% | 42% | 6% | 6% | 11% | 9% |
| ALL | us26 | 29135 | 7% | 13% | 18% | 54% | 7% | 1% | 40% | 5% | 6% | 10% | 9% |
| ALL | opp27 | 34855 | 5% | 13% | 13% | 56% | 6% | 7% | 26% | 5% | 10% | 17% | 5% |
| ALL | opp26 | 34077 | 5% | 12% | 13% | 58% | 6% | 5% | 24% | 4% | 10% | 17% | 5% |
| map:collision | us27 | 5156 | 4% | 27% | 51% | 7% | 10% | 0% | 66% | 5% | 8% | 22% | 17% |
| map:collision | us26 | 5270 | 4% | 28% | 48% | 9% | 11% | 0% | 64% | 5% | 8% | 21% | 16% |
| map:collision | opp27 | 4613 | 7% | 18% | 48% | 22% | 4% | 2% | 35% | 5% | 13% | 27% | 6% |
| map:collision | opp26 | 4240 | 5% | 16% | 46% | 25% | 4% | 3% | 31% | 5% | 11% | 30% | 6% |
| map:corners | us27 | 3918 | 10% | 51% | 2% | 34% | 2% | 2% | 79% | 16% | 9% | 5% | 14% |
| map:corners | us26 | 3428 | 11% | 46% | 2% | 39% | 1% | 1% | 74% | 14% | 8% | 6% | 13% |
| map:corners | opp27 | 5229 | 6% | 51% | 2% | 27% | 2% | 11% | 61% | 13% | 17% | 8% | 12% |
| map:corners | opp26 | 4939 | 5% | 61% | 2% | 23% | 3% | 7% | 58% | 11% | 16% | 10% | 13% |
| map:elkring | us27 | 1802 | 27% | 7% | 5% | 54% | 5% | 3% | 31% | 4% | 5% | 9% | 5% |
| map:elkring | us26 | 2797 | 24% | 6% | 4% | 59% | 4% | 4% | 30% | 5% | 5% | 7% | 3% |
| map:elkring | opp27 | 3004 | 16% | 3% | 3% | 58% | 3% | 16% | 25% | 4% | 14% | 10% | 1% |
| map:elkring | opp26 | 3748 | 19% | 2% | 5% | 62% | 4% | 9% | 23% | 5% | 11% | 13% | 2% |
| map:expanse | us27 | 1565 | 9% | 3% | 0% | 88% | 0% | 0% | 1% | 0% | 5% | 0% | 0% |
| map:expanse | us26 | 1604 | 9% | 2% | 0% | 89% | 0% | 0% | 1% | 0% | 5% | 0% | 0% |
| map:expanse | opp27 | 2828 | 2% | 0% | 0% | 97% | 0% | 1% | 0% | 0% | 7% | 17% | 0% |
| map:expanse | opp26 | 2880 | 2% | 1% | 1% | 96% | 0% | 1% | 0% | 0% | 7% | 21% | 0% |
| map:interlock | us27 | 3420 | 5% | 10% | 3% | 79% | 3% | 0% | 38% | 6% | 3% | 15% | 2% |
| map:interlock | us26 | 2402 | 4% | 12% | 2% | 79% | 2% | 1% | 32% | 5% | 3% | 13% | 2% |
| map:interlock | opp27 | 4266 | 5% | 7% | 1% | 77% | 3% | 7% | 21% | 4% | 9% | 18% | 1% |
| map:interlock | opp26 | 3181 | 2% | 5% | 2% | 82% | 4% | 5% | 17% | 3% | 13% | 17% | 1% |
| map:lanes | us27 | 4782 | 5% | 2% | 40% | 50% | 3% | 0% | 40% | 5% | 8% | 17% | 15% |
| map:lanes | us26 | 5424 | 5% | 1% | 40% | 50% | 3% | 0% | 38% | 4% | 7% | 17% | 18% |
| map:lanes | opp27 | 5006 | 2% | 1% | 38% | 44% | 4% | 12% | 24% | 2% | 6% | 23% | 12% |
| map:lanes | opp26 | 4967 | 1% | 1% | 38% | 48% | 2% | 9% | 23% | 2% | 6% | 23% | 12% |
| map:monolith | us27 | 2385 | 7% | 3% | 1% | 77% | 8% | 4% | 14% | 3% | 10% | 7% | 1% |
| map:monolith | us26 | 1754 | 8% | 2% | 2% | 79% | 5% | 3% | 18% | 5% | 10% | 8% | 1% |
| map:monolith | opp27 | 3617 | 4% | 12% | 1% | 78% | 2% | 4% | 10% | 2% | 6% | 30% | 1% |
| map:monolith | opp26 | 2985 | 3% | 1% | 2% | 85% | 3% | 6% | 8% | 2% | 10% | 28% | 1% |
| map:packs | us27 | 3296 | 9% | 1% | 5% | 53% | 31% | 0% | 43% | 5% | 3% | 1% | 4% |
| map:packs | us26 | 3172 | 9% | 0% | 4% | 54% | 32% | 1% | 50% | 6% | 3% | 0% | 4% |
| map:packs | opp27 | 3304 | 7% | 2% | 2% | 44% | 40% | 6% | 30% | 6% | 9% | 5% | 2% |
| map:packs | opp26 | 3425 | 7% | 1% | 3% | 45% | 40% | 5% | 35% | 6% | 9% | 3% | 3% |
| map:rows | us27 | 2487 | 0% | 0% | 0% | 99% | 0% | 0% | 0% | 0% | 5% | 7% | 0% |
| map:rows | us26 | 3284 | 0% | 2% | 1% | 97% | 0% | 0% | 2% | 0% | 3% | 2% | 1% |
| map:rows | opp27 | 2988 | 1% | 0% | 2% | 97% | 0% | 0% | 0% | 0% | 9% | 7% | 2% |
| map:rows | opp26 | 3712 | 1% | 3% | 3% | 92% | 0% | 1% | 4% | 3% | 6% | 7% | 3% |

28,811 idle champion-rounds (29,135). Same distribution: 53% own-half away from everything (54), 17% next to a living camp (18), 14% altar (13), 7% spawn (7); 42% with an enemy within 8 (40). Rows: 2,487 idle rounds (3,284), 99% in own half, 0% with an enemy near — the pack wait is shorter but still a wait. Longest streaks ≥8: 116 (0.7/game) vs 177 (1.2/game): the 30-round Cassi wait at (36,8) r203 on rows survives in **1 of 17 games** (`0413ec21`; 15 of 18 before; no shorter (36,8) wait appears in the top-25 list either); the Issac (5,21) r115-r145 wait on monolith is in 3 of 16 games (2 of 13), and in `233c4851` Issac stands there r115-r190.

### 3c. Idle ≥5 rounds within 6 tiles of a living own-half camp group (farm maps; q14 recomputed for both batches)

| map | who | streaks | per game | mean len | no ally within 6 | enemy within 8 | camp awake | an ally is already hitting that camp | hp<50% | ends by attacking that camp (within 3r) |
|---|---|---|---|---|---|---|---|---|---|---|
| elkring | us27 | 48 | 5.3 | 8.9 | 41% | 37% | 41% | 33% | 0% | 22% |
| elkring | us26 | 77 | 5.5 | 9.1 | 38% | 33% | 36% | 33% | 2% | 19% |
| elkring | opp27 | 86 | 9.6 | 5.9 | 9% | 22% | 56% | 55% | 5% | 22% |
| elkring | opp26 | 131 | 9.4 | 6.9 | 17% | 16% | 54% | 51% | 9% | 16% |
| expanse | us27 | 48 | 2.8 | 5.5 | 62% | 0% | 35% | 35% | 0% | 0% |
| expanse | us26 | 45 | 2.6 | 5.4 | 40% | 0% | 37% | 37% | 0% | 0% |
| expanse | opp27 | 54 | 3.2 | 5.2 | 53% | 0% | 53% | 53% | 3% | 7% |
| expanse | opp26 | 55 | 3.2 | 5.3 | 58% | 0% | 45% | 45% | 5% | 9% |
| interlock | us27 | 55 | 2.9 | 5.6 | 16% | 45% | 85% | 72% | 0% | 10% |
| interlock | us26 | 38 | 2.9 | 5.3 | 15% | 47% | 84% | 81% | 0% | 2% |
| interlock | opp27 | 191 | 10.1 | 5.5 | 25% | 4% | 46% | 46% | 7% | 14% |
| interlock | opp26 | 150 | 11.5 | 5.7 | 31% | 6% | 59% | 54% | 14% | 16% |
| lanes | us27 | 519 | 30.5 | 5.1 | 21% | 37% | 27% | 26% | 1% | 18% |
| lanes | us26 | 635 | 35.3 | 5.1 | 16% | 32% | 28% | 27% | 1% | 15% |
| lanes | opp27 | 557 | 32.8 | 5.5 | 20% | 13% | 28% | 27% | 2% | 12% |
| lanes | opp26 | 564 | 31.3 | 5.5 | 19% | 13% | 30% | 27% | 5% | 15% |
| monolith | us27 | 17 | 1.1 | 12.6 | 94% | 23% | 5% | 5% | 0% | 52% |
| monolith | us26 | 13 | 1.0 | 13.5 | 100% | 15% | 0% | 0% | 0% | 23% |
| monolith | opp27 | 83 | 5.2 | 7.1 | 14% | 26% | 79% | 72% | 2% | 79% |
| monolith | opp26 | 44 | 3.4 | 10.2 | 63% | 18% | 65% | 38% | 9% | 45% |
| rows | us27 | 67 | 3.9 | 7.5 | 49% | 0% | 25% | 25% | 0% | 50% |
| rows | us26 | 110 | 6.1 | 10.7 | 48% | 2% | 19% | 18% | 0% | 64% |
| rows | opp27 | 10 | 0.6 | 9.8 | 30% | 0% | 60% | 40% | 20% | 60% |
| rows | opp26 | 24 | 1.3 | 8.8 | 29% | 0% | 62% | 54% | 4% | 37% |

**Rows: 67 streaks (3.9/game, mean 7.5 rounds) vs 110 (6.1/game, 10.7 rounds)** — 43 fewer on 17 vs 18 games, outside Poisson noise (±13); 50% end with the champion attacking that pack (64%): the remaining waits are the 4-stack standing at a pack that is asleep until the respawn, not a champion that forgot the pack. Lanes 519 (30.5/game) vs 635 (35.3): -116 ± 34, i.e. ~5 fewer waits per game, with the opponents at 32.8 (31.3). Monolith 17 vs 13, elkring 48 vs 77 (5.3 vs 5.5/game), expanse 48 vs 45, interlock 55 vs 38 (2.9/game both): no change per game.


## 4. Territory via captures (Q4)

### 4a. Captures by territory of the group (own/mid/enemy from the capturer's side)

| split | who | 0-49 | 50-99 | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 | 400-449 | 450+ | total own/mid/enemy | gems own/mid/enemy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 259/99/0 | 335/21/1 | 320/69/16 | 340/48/3 | 336/47/5 | 315/43/3 | 317/59/8 | 277/49/2 | 174/30/2 | 382/127/7 | 3055/592/47 | 108136/21784/1718 |
| ALL | us26 | 260/96/0 | 305/30/1 | 336/61/10 | 331/41/4 | 296/52/7 | 337/52/8 | 382/57/9 | 231/57/1 | 187/45/7 | 337/131/5 | 3002/622/52 | 105018/22104/1784 |
| ALL | opp27 | 366/15/1 | 300/49/18 | 373/69/27 | 356/56/28 | 368/71/23 | 348/71/24 | 350/71/20 | 278/65/14 | 173/59/13 | 352/141/32 | 3264/667/200 | 115742/24680/6440 |
| ALL | opp26 | 344/15/0 | 287/46/8 | 356/64/24 | 350/66/27 | 354/61/16 | 373/58/14 | 359/62/18 | 270/55/19 | 173/45/14 | 355/144/26 | 3221/616/166 | 113152/23438/5526 |
| map:collision | us27 | 0/33/0 | 38/1/0 | 15/16/0 | 27/10/0 | 25/9/0 | 22/12/0 | 27/13/0 | 28/11/0 | 32/13/0 | 184/79/1 | 398/197/1 | 9026/4334/22 |
| map:collision | us26 | 0/32/0 | 38/1/0 | 18/13/0 | 21/15/0 | 21/15/1 | 30/11/0 | 28/14/0 | 33/16/0 | 32/15/0 | 179/86/0 | 400/218/1 | 9026/4796/22 |
| map:collision | opp27 | 44/0/0 | 22/5/2 | 34/8/0 | 28/6/1 | 28/7/2 | 28/9/1 | 33/9/0 | 27/8/0 | 33/10/1 | 174/57/8 | 451/119/15 | 12840/2618/416 |
| map:collision | opp26 | 45/1/0 | 25/6/0 | 33/5/0 | 27/3/1 | 25/7/1 | 30/4/0 | 28/9/2 | 33/6/3 | 31/6/1 | 177/49/7 | 454/96/15 | 12314/2112/588 |
| map:corners | us27 | 0/38/0 | 17/14/0 | 3/26/0 | 8/19/0 | 4/19/0 | 4/18/0 | 3/25/0 | 4/14/0 | 5/6/0 | 12/31/0 | 60/210/0 | 1526/10008/0 |
| map:corners | us26 | 0/34/0 | 16/16/0 | 7/24/0 | 7/15/0 | 7/16/0 | 2/15/0 | 4/22/0 | 2/14/0 | 5/12/0 | 11/26/0 | 61/194/0 | 1564/9192/0 |
| map:corners | opp27 | 18/7/0 | 22/7/1 | 19/24/0 | 11/17/0 | 20/20/0 | 6/23/0 | 14/19/2 | 9/22/0 | 9/27/0 | 19/59/3 | 147/225/6 | 4064/10368/146 |
| map:corners | opp26 | 15/8/0 | 14/12/0 | 13/21/0 | 12/23/2 | 16/21/0 | 5/17/1 | 15/20/0 | 13/21/0 | 6/19/0 | 30/75/3 | 139/237/6 | 3678/10944/146 |
| map:elkring | us27 | 18/0/0 | 13/0/0 | 20/0/2 | 13/0/1 | 19/0/0 | 19/0/0 | 19/0/0 | 18/0/0 | 18/0/0 | 65/0/5 | 222/0/8 | 7992/0/288 |
| map:elkring | us26 | 28/0/0 | 23/0/0 | 28/0/1 | 25/0/0 | 27/0/1 | 27/0/4 | 23/0/3 | 31/0/0 | 25/0/3 | 79/0/5 | 316/0/17 | 11376/0/612 |
| map:elkring | opp27 | 22/0/0 | 16/0/2 | 22/0/2 | 20/0/2 | 19/0/0 | 23/0/4 | 16/0/1 | 20/0/2 | 18/0/1 | 59/0/11 | 235/0/25 | 8028/0/900 |
| map:elkring | opp26 | 34/0/0 | 24/0/1 | 37/0/4 | 29/0/3 | 32/0/3 | 24/0/4 | 33/0/1 | 30/0/3 | 28/0/2 | 79/0/9 | 350/0/30 | 12204/0/1080 |
| map:expanse | us27 | 51/0/0 | 50/0/0 | 67/0/0 | 65/0/0 | 63/0/0 | 49/0/0 | 34/0/0 | 26/1/0 | - | - | 405/1/0 | 16580/108/0 |
| map:expanse | us26 | 51/0/0 | 50/0/0 | 67/0/0 | 65/0/0 | 63/0/0 | 52/0/0 | 73/0/0 | 3/0/0 | - | - | 424/0/0 | 17128/0/0 |
| map:expanse | opp27 | 49/0/0 | 59/0/1 | 54/0/0 | 63/0/2 | 68/0/0 | 60/0/0 | 59/1/0 | 29/1/0 | - | - | 441/2/3 | 16794/216/144 |
| map:expanse | opp26 | 48/0/0 | 52/0/1 | 63/0/0 | 60/0/2 | 62/0/0 | 65/1/0 | 53/2/0 | 9/1/0 | - | - | 412/4/3 | 16116/432/144 |
| map:interlock | us27 | 56/0/0 | 45/0/0 | 60/0/0 | 49/0/0 | 47/0/0 | 48/0/0 | 51/0/0 | 47/1/0 | 48/1/0 | 63/2/0 | 514/4/0 | 17226/144/0 |
| map:interlock | us26 | 39/0/0 | 32/0/0 | 40/0/0 | 35/0/1 | 34/0/0 | 42/0/0 | 37/1/0 | 36/2/0 | 33/1/0 | 23/1/0 | 351/5/1 | 11784/180/72 |
| map:interlock | opp27 | 56/0/0 | 30/1/0 | 52/1/1 | 47/0/1 | 41/0/1 | 41/1/2 | 38/1/0 | 36/1/2 | 34/0/2 | 42/2/4 | 417/7/13 | 15472/252/764 |
| map:interlock | opp26 | 41/0/0 | 20/1/1 | 34/1/2 | 34/1/0 | 29/2/1 | 32/1/0 | 36/1/0 | 32/1/0 | 27/0/1 | 20/1/2 | 305/9/7 | 10858/324/382 |
| map:lanes | us27 | 52/0/0 | 88/6/1 | 48/3/4 | 72/8/0 | 53/9/1 | 74/6/2 | 56/9/4 | 39/10/0 | 9/0/0 | 4/0/0 | 495/51/12 | 11742/1122/264 |
| map:lanes | us26 | 72/0/0 | 79/12/0 | 59/7/5 | 82/5/2 | 65/7/5 | 83/14/0 | 82/10/4 | 45/9/1 | 22/4/0 | 8/0/0 | 597/68/17 | 14290/1496/374 |
| map:lanes | opp27 | 72/0/1 | 33/21/11 | 83/15/20 | 59/20/20 | 75/20/15 | 66/20/13 | 66/18/8 | 36/11/3 | 10/3/3 | 1/0/0 | 501/128/94 | 12240/2830/2244 |
| map:lanes | opp26 | 69/0/0 | 50/15/5 | 82/16/15 | 72/21/17 | 79/15/7 | 95/16/6 | 80/16/10 | 43/8/4 | 15/1/0 | 5/3/0 | 590/111/64 | 14574/2442/1514 |
| map:monolith | us27 | 64/0/0 | 16/0/0 | 61/0/10 | 46/0/2 | 50/0/4 | 36/0/1 | 48/0/4 | 45/0/2 | 29/0/2 | 18/0/1 | 413/0/26 | 14542/0/1144 |
| map:monolith | us26 | 52/0/0 | 15/0/1 | 48/0/4 | 37/0/1 | 39/0/0 | 35/0/4 | 37/0/2 | 30/0/0 | 31/0/4 | 4/0/0 | 328/0/16 | 11458/0/704 |
| map:monolith | opp27 | 55/0/0 | 53/0/0 | 54/0/4 | 56/0/0 | 59/0/0 | 53/0/1 | 55/0/3 | 50/0/3 | 40/0/2 | 20/0/1 | 495/0/14 | 15692/0/550 |
| map:monolith | opp26 | 42/0/0 | 40/0/0 | 35/0/3 | 53/0/1 | 46/0/4 | 47/0/1 | 37/0/3 | 43/0/6 | 33/0/3 | 5/0/1 | 381/0/22 | 12082/0/836 |
| map:packs | us27 | 1/28/0 | 35/0/0 | 11/24/0 | 26/11/0 | 27/10/0 | 29/7/0 | 28/12/0 | 29/12/0 | 31/10/0 | 36/15/0 | 253/129/0 | 11088/6068/0 |
| map:packs | us26 | 0/30/0 | 34/1/0 | 15/17/0 | 25/6/0 | 22/14/0 | 30/12/0 | 32/10/0 | 22/16/0 | 27/13/0 | 33/18/0 | 240/137/0 | 10572/6440/0 |
| map:packs | opp27 | 32/8/0 | 29/15/1 | 21/21/0 | 30/13/2 | 23/24/5 | 28/18/3 | 29/23/6 | 32/22/4 | 27/19/4 | 37/23/5 | 288/186/30 | 12000/8396/1276 |
| map:packs | opp26 | 31/6/0 | 24/12/0 | 21/21/0 | 25/18/1 | 25/16/0 | 30/19/2 | 33/14/2 | 29/18/3 | 23/19/7 | 39/16/4 | 280/159/19 | 11856/7184/836 |
| map:rows | us27 | 17/0/0 | 33/0/0 | 35/0/0 | 34/0/0 | 48/0/0 | 34/0/0 | 51/0/0 | 41/0/0 | 2/0/0 | - | 295/0/0 | 18414/0/0 |
| map:rows | us26 | 18/0/0 | 18/0/0 | 54/0/0 | 34/0/0 | 18/0/0 | 36/0/0 | 66/0/0 | 29/0/0 | 12/0/0 | - | 285/0/0 | 17820/0/0 |
| map:rows | opp27 | 18/0/0 | 36/0/0 | 34/0/0 | 42/0/0 | 35/0/0 | 43/0/0 | 40/0/0 | 39/0/0 | 2/0/0 | - | 289/0/0 | 18612/0/0 |
| map:rows | opp26 | 19/0/0 | 38/0/0 | 38/0/0 | 38/0/0 | 40/0/0 | 45/0/0 | 44/0/0 | 38/0/0 | 10/0/0 | - | 310/0/0 | 19470/0/0 |

Totals us 3055/592/47 (3002/622/52), opp 3264/667/200 (3221/616/166). **Our enemy-half farming is still 0.3/game** (47 captures; lanes 12 vs 17, monolith 26 vs 16, elkring 8 vs 17 in 9 vs 14 games). **The opponents took 200 groups in our half vs 166**: lanes 94 (64), packs 30 (19), interlock 13 (7), elkring 25 (30), monolith 14 (22). Rows: 295 vs 285 captures for us (17.4 vs 15.8/game), the opponents 289 vs 310 (17.0 vs 17.2/game): the gap of 1.4 captures/game against us became a lead of 0.4 — and the result did not move (see 5.1).

### 4b. Own-half groups captured by the enemy

| split | batch | games | games with own-half group lost | first loss round median / min / p25 |
|---|---|---|---|---|
| ALL | 27 | 155 | 67 (43%) | 234 / 48 / 113 |
| ALL | 26 | 150 | 64 (42%) | 214 / 50 / 143 |
| map:collision | 27 | 19 | 9 (47%) | 233 / 85 / 184 |
| map:collision | 26 | 19 | 7 (36%) | 369 / 172 / 223 |
| map:corners | 27 | 19 | 5 (26%) | 317 / 99 / 312 |
| map:corners | 26 | 17 | 3 (17%) | 163 / 157 / 157 |
| map:elkring | 27 | 9 | 8 (88%) | 140 / 78 / 110 |
| map:elkring | 26 | 14 | 11 (78%) | 160 / 99 / 102 |
| map:expanse | 27 | 17 | 1 (5%) | 97 / 97 / 97 |
| map:expanse | 26 | 17 | 1 (5%) | 97 / 97 / 97 |
| map:interlock | 27 | 19 | 7 (36%) | 356 / 113 / 177 |
| map:interlock | 26 | 13 | 4 (30%) | 341 / 70 / 217 |
| map:lanes | 27 | 17 | 13 (76%) | 111 / 48 / 85 |
| map:lanes | 26 | 18 | 14 (77%) | 130 / 50 / 103 |
| map:monolith | 27 | 16 | 8 (50%) | 198 / 102 / 139 |
| map:monolith | 26 | 13 | 11 (84%) | 248 / 126 / 143 |
| map:packs | 27 | 22 | 16 (72%) | 289 / 99 / 234 |
| map:packs | 26 | 21 | 13 (61%) | 426 / 199 / 336 |

Lanes 13 of 17 games (14 of 18), first at median r111 (r130). **Packs 16 of 22 (13 of 21), first at r289 (r426)**; monolith 8 of 16 (11 of 13), first r198 (r248). Collision 9 of 19 (7 of 19), corners 5 of 19 (3 of 17), interlock 7 of 19 (4 of 13): within noise.

### 4c. Per-game means by map and result

| split | batch | games | us mid caps | opp mid caps | us enemy-half caps | opp enemy-half caps (=our camps lost) | us own | opp own | us mid gems | opp mid gems | opp gems from our half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 27 | 155 | 3.8 | 4.3 | 0.3 | 1.3 | 19.7 | 21.1 | 141 | 159 | 42 |
| ALL | 26 | 150 | 4.1 | 4.1 | 0.3 | 1.1 | 20.0 | 21.5 | 147 | 156 | 37 |
| res:win | 27 | 58 | 5.7 | 2.1 | 0.3 | 0.4 | 22.3 | 20.7 | 212 | 82 | 17 |
| res:win | 26 | 59 | 5.7 | 2.2 | 0.5 | 0.5 | 22.8 | 21.7 | 191 | 83 | 18 |
| res:loss | 27 | 97 | 2.7 | 5.6 | 0.3 | 1.8 | 18.2 | 21.2 | 98 | 205 | 56 |
| res:loss | 26 | 91 | 3.1 | 5.4 | 0.2 | 1.5 | 18.2 | 21.3 | 119 | 204 | 49 |
| map:collision win | 27 | 8 | 14.8 | 2.4 | 0.1 | 0.2 | 24.8 | 19.6 | 324 | 52 | 6 |
| map:collision win | 26 | 12 | 14.2 | 3.0 | 0.1 | 0.3 | 24.2 | 22.2 | 314 | 66 | 14 |
| map:collision loss | 27 | 11 | 7.2 | 9.1 | 0.0 | 1.2 | 18.2 | 26.7 | 158 | 200 | 34 |
| map:collision loss | 26 | 7 | 6.7 | 8.6 | 0.0 | 1.6 | 15.6 | 26.7 | 148 | 189 | 59 |
| map:corners win | 27 | 8 | 17.4 | 5.4 | 0.0 | 0.0 | 4.4 | 8.6 | 831 | 246 | 0 |
| map:corners win | 26 | 5 | 17.6 | 7.0 | 0.0 | 0.2 | 5.2 | 7.4 | 840 | 317 | 4 |
| map:corners loss | 27 | 11 | 6.5 | 16.5 | 0.0 | 0.5 | 2.3 | 7.1 | 305 | 764 | 13 |
| map:corners loss | 26 | 12 | 8.8 | 16.8 | 0.0 | 0.4 | 2.9 | 8.5 | 416 | 780 | 10 |
| map:elkring win | 27 | 5 | 0.0 | 0.0 | 1.0 | 2.6 | 26.4 | 26.6 | 0 | 0 | 94 |
| map:elkring win | 26 | 5 | 0.0 | 0.0 | 1.4 | 1.2 | 25.6 | 27.2 | 0 | 0 | 43 |
| map:elkring loss | 27 | 4 | 0.0 | 0.0 | 0.8 | 3.0 | 22.5 | 25.5 | 0 | 0 | 108 |
| map:elkring loss | 26 | 9 | 0.0 | 0.0 | 1.1 | 2.7 | 20.9 | 23.8 | 0 | 0 | 96 |
| map:expanse win | 27 | 10 | 0.1 | 0.2 | 0.0 | 0.0 | 24.9 | 26.0 | 11 | 22 | 0 |
| map:expanse win | 26 | 11 | 0.0 | 0.3 | 0.0 | 0.0 | 25.8 | 24.5 | 0 | 29 | 0 |
| map:expanse loss | 27 | 7 | 0.0 | 0.0 | 0.0 | 0.4 | 22.3 | 25.9 | 0 | 0 | 21 |
| map:expanse loss | 26 | 6 | 0.0 | 0.2 | 0.0 | 0.5 | 23.3 | 23.8 | 0 | 18 | 24 |
| map:interlock win | 27 | 10 | 0.4 | 0.3 | 0.0 | 0.0 | 29.1 | 21.9 | 14 | 11 | 0 |
| map:interlock win | 26 | 7 | 0.6 | 0.7 | 0.1 | 0.0 | 29.4 | 24.4 | 21 | 26 | 0 |
| map:interlock loss | 27 | 9 | 0.0 | 0.4 | 0.0 | 1.4 | 24.8 | 22.0 | 0 | 16 | 85 |
| map:interlock loss | 26 | 6 | 0.2 | 0.7 | 0.0 | 1.2 | 24.2 | 22.3 | 6 | 24 | 64 |
| map:lanes win | 27 | 3 | 4.0 | 7.7 | 0.7 | 0.3 | 38.7 | 30.7 | 88 | 169 | 8 |
| map:lanes win | 26 | 3 | 4.3 | 3.3 | 3.7 | 3.3 | 37.7 | 33.0 | 95 | 73 | 74 |
| map:lanes loss | 27 | 14 | 2.8 | 7.5 | 0.7 | 6.6 | 27.1 | 29.2 | 61 | 166 | 159 |
| map:lanes loss | 26 | 15 | 3.7 | 6.7 | 0.4 | 3.6 | 32.3 | 32.7 | 81 | 148 | 86 |
| map:monolith win | 27 | 5 | 0.0 | 0.0 | 1.6 | 0.2 | 28.2 | 29.8 | 0 | 0 | 9 |
| map:monolith win | 26 | 5 | 0.0 | 0.0 | 2.0 | 1.4 | 27.2 | 27.2 | 0 | 0 | 53 |
| map:monolith loss | 27 | 11 | 0.0 | 0.0 | 1.6 | 1.2 | 24.7 | 31.5 | 0 | 0 | 46 |
| map:monolith loss | 26 | 8 | 0.0 | 0.0 | 0.8 | 1.9 | 24.0 | 30.6 | 0 | 0 | 72 |
| map:packs win | 27 | 6 | 9.2 | 5.5 | 0.0 | 1.5 | 13.2 | 12.8 | 427 | 258 | 66 |
| map:packs win | 26 | 7 | 8.9 | 5.4 | 0.0 | 0.6 | 13.6 | 13.6 | 415 | 254 | 25 |
| map:packs loss | 27 | 16 | 4.6 | 9.6 | 0.0 | 1.3 | 10.9 | 13.2 | 219 | 428 | 55 |
| map:packs loss | 26 | 14 | 5.4 | 8.6 | 0.0 | 1.1 | 10.4 | 13.2 | 253 | 386 | 47 |
| map:rows win | 27 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 17.3 | 15.7 | 0 | 0 | 0 |
| map:rows win | 26 | 4 | 0.0 | 0.0 | 0.0 | 0.0 | 17.2 | 17.2 | 0 | 0 | 0 |
| map:rows loss | 27 | 14 | 0.0 | 0.0 | 0.0 | 0.0 | 17.4 | 17.3 | 0 | 0 | 0 |
| map:rows loss | 26 | 14 | 0.0 | 0.0 | 0.0 | 0.0 | 15.4 | 17.2 | 0 | 0 | 0 |

### 4d. Mid-camp balance (us mid caps − opp mid caps) vs result

| diff | study27 | study26 |
|---|---|---|
| ≤ -6 | 26 games, win 7% | 18 games, win 0% |
| -5..-1 | 25 games, win 20% | 26 games, win 19% |
| 0 | 68 games, win 36% | 63 games, win 38% |
| 1..5 | 17 games, win 52% | 27 games, win 59% |
| ≥ 6 | 19 games, win 89% | 16 games, win 87% |

Reading: same curve. Lanes losses: the opponent's captures in our half per loss **6.6 vs 3.6**, gems from our half 159 vs 86 per loss, our own-half captures 27.1 vs 32.3 per loss. Packs losses: opp mid captures 9.6 vs 8.6, ours 4.6 vs 5.4. Collision/corners/elkring/expanse/interlock/monolith wins and losses have the same shape as study26 within 1-2 captures.


## 5. The maps we lose most, with examples

Per-game means from `cmp_games.md` (us27 / us26 / opp in the study27 games; ± = standard error; ** = |z| ≥ 2):


### 5.1 rows (17 games, 3-14; study26 18 games, 4-14)

| metric | us27 | us26 | z | opp27 | opp26 |
|---|---|---|---|---|---|
| own | 100.0±0.0 | 99.7±0.3 | +1.0 | 99.7±0.3 | 98.6±0.8 |
| mid | 0.0±0.0 | 0.1±0.1 | -1.0 | 0.0±0.0 | 0.1±0.1 |
| en | 0.0±0.0 | 0.2±0.2 | -1.0 | 0.3±0.3 | 1.3±0.7 |
| depth | 17.7±0.1 | 16.0±0.1 | +11.6 ** | 16.6±0.3 | 16.8±0.4 |
| pd | 10.9±0.1 | 11.9±0.1 | -11.3 ** | 11.5±0.3 | 12.0±0.4 |
| alone | 18.1±0.3 | 20.5±0.5 | -4.0 ** | 22.1±0.9 | 24.1±1.8 |
| idle | 7.4±0.2 | 9.1±0.1 | -6.7 ** | 9.1±1.1 | 10.3±1.0 |
| camp | 29.3±0.3 | 25.7±0.3 | +9.6 ** | 25.9±1.8 | 26.4±1.7 |
| fight | 0.0±0.0 | 0.1±0.1 | -1.5 | 0.1±0.1 | 0.1±0.1 |
| deaths | 0.1±0.1 | 0.1±0.1 | +0.0 | 0.0±0.0 | 0.3±0.2 |
| caps | 17.4±0.3 | 15.8±0.3 | +3.5 ** | 17.0±0.5 | 17.2±0.5 |
| cap_own | 17.4±0.3 | 15.8±0.3 | +3.5 ** | 17.0±0.5 | 17.2±0.5 |
| cap_mid | 0.0±0.0 | 0.0±0.0 | +0.0 | 0.0±0.0 | 0.0±0.0 |
| cap_en | 0.0±0.0 | 0.0±0.0 | +0.0 | 0.0±0.0 | 0.0±0.0 |
| gpr | 245.1±2.4 | 221.7±4.8 | +4.3 ** | 265.1±4.9 | 258.9±5.9 |

Everything our stacking rule was meant to do happened: attack-camp share 29.3% (25.7, z=9.6), captures 17.4 (15.8), gems/100 rounds 245 (222), pd 10.9 (11.9), idle 7.4% (9.1), spawn 7.8% (9.1). Opponents in the same games: 265 gems/100r (259), 17.0 captures. Clearing (q11/q13): first hit→capture 18 rounds median (21), 3.16 distinct hitters (2.70), max concurrent 4 in 42% of captures (0%), 3 in 31% (68%); group-rounds under attack with 4 hitters 17% (0%). Respawn→capture (q12): nearest pack (18,3) median 19 (32), middle (31,3) 29 (24), far (42,3) 36 (31), max 141 (244); opponents 21/23/41. Our 16th capture comes at r365 in 15 of 17 games (study26: r375 in 11 of 18, never in 7):

**Rows end-game (q15), study27:**

| match | opp | rank | res | score | rounds | us caps (r of 16th) | opp caps (r of 16th) | us last tribute r | us gems carried at end | us earned (score+carried) | us caps by 100r | opp caps by 100r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0413ec21 | Nyx | 21 | loss | 990-1056 | 442 | 19 (378) | 16 (442) | 402 | 132 | 1122 | 2/5/3/7/2 | 3/3/4/4/2 |
| 2bc7a917 | Palestine 🇵🇸 | 54 | win | 1056-924 | 404 | 16 (386) | 16 (398) | 404 | 0 | 1056 | 3/4/4/5/0 | 2/4/5/5/0 |
| c3a7077e | Univardisty  | 6 | loss | 957-1056 | 401 | 18 (365) | 24 (261) | 380 | 165 | 1122 | 3/4/5/6/0 | 3/9/6/6/0 |
| ff9f5886 | Shawn | 3 | loss | 891-1056 | 351 | 15 (-) | 17 (325) | 349 | 33 | 924 | 3/4/5/3/0 | 4/4/6/3/0 |
| 09112589 | Intercontine | 2 | loss | 957-1056 | 401 | 18 (365) | 16 (385) | 380 | 165 | 1122 | 3/4/5/6/0 | 3/5/4/4/0 |
| 0da6d890 | Mite | 1 | loss | 957-1056 | 398 | 18 (365) | 16 (381) | 380 | 165 | 1122 | 3/4/5/6/0 | 3/4/4/5/0 |
| ddcf57ff | test | 14 | loss | 957-1056 | 387 | 18 (365) | 16 (366) | 380 | 165 | 1122 | 3/4/5/6/0 | 3/4/5/4/0 |
| 6e1049fe | Conley | 20 | win | 1056-924 | 403 | 18 (365) | 15 (-) | 403 | 66 | 1122 | 3/4/5/6/0 | 3/4/3/5/0 |
| c21d3221 | geese geese  | 11 | loss | 957-1056 | 390 | 18 (365) | 18 (368) | 380 | 165 | 1122 | 3/4/5/6/0 | 3/5/4/6/0 |
| 62ebcae9 | octo's odyss | 26 | loss | 891-1056 | 368 | 16 (365) | 18 (348) | 349 | 99 | 990 | 3/4/5/4/0 | 4/4/5/5/0 |
| 8401ebce | lETHal | 22 | loss | 957-1056 | 400 | 18 (365) | 17 (375) | 380 | 165 | 1122 | 3/4/5/6/0 | 3/3/5/6/0 |
| 2d5e6ef6 | Full Damage | 9 | loss | 891-1056 | 368 | 16 (365) | 17 (343) | 349 | 99 | 990 | 3/4/5/4/0 | 4/4/5/4/0 |
| 8637d0d0 | Nyxius | 12 | loss | 957-1056 | 385 | 17 (365) | 17 (361) | 380 | 99 | 1056 | 3/4/5/5/0 | 3/6/3/5/0 |
| 09d2bdc1 | PTN Hyperion | 8 | loss | 957-1056 | 400 | 18 (365) | 17 (377) | 380 | 165 | 1122 | 3/4/5/6/0 | 4/4/4/5/0 |
| 78e0bf2c | VeryGood | 4 | loss | 891-1056 | 374 | 16 (365) | 16 (351) | 349 | 99 | 990 | 3/4/5/4/0 | 4/4/5/3/0 |
| a1b65574 | Cabbage | 16 | win | 1056-990 | 403 | 18 (365) | 16 (383) | 403 | 66 | 1122 | 3/4/5/6/0 | 2/5/5/4/0 |
| 88b53bab | Mate in One | 28 | loss | 957-1056 | 393 | 18 (365) | 17 (378) | 380 | 165 | 1122 | 3/4/5/6/0 | 3/4/5/5/0 |

**study26:**

| match | opp | rank | res | score | rounds | us caps (r of 16th) | opp caps (r of 16th) | us last tribute r | us gems carried at end | us earned (score+carried) | us caps by 100r | opp caps by 100r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 14ebd970 | ❤️Quantom❤️ | 10 | win | 1056-924 | 450 | 18 (400) | 14 (-) | 450 | 66 | 1122 | 2/4/5/4/3 | 2/4/3/3/2 |
| f5686c33 | Shawn | 3 | loss | 792-1056 | 351 | 14 (-) | 17 (325) | 340 | 66 | 858 | 2/5/3/4/0 | 4/4/6/3/0 |
| 604a6cf6 | Still Testin | 19 | loss | 726-1056 | 449 | 13 (-) | 16 (430) | 418 | 132 | 858 | 2/4/1/4/2 | 3/2/5/4/2 |
| 8ac3e855 | AlphaSlop | 22 | win | 1023-924 | 421 | 17 (375) | 19 (365) | 421 | 33 | 1056 | 2/5/3/6/1 | 4/5/4/4/2 |
| 78034945 | Conley | 20 | win | 1023-990 | 421 | 17 (375) | 16 (417) | 421 | 33 | 1056 | 2/5/3/6/1 | 3/4/3/5/1 |
| 6d2039e7 | WHIM | 30 | loss | 957-1056 | 415 | 17 (375) | 24 (308) | 397 | 99 | 1056 | 2/5/3/6/1 | 3/5/7/8/1 |
| 78b0bef5 | umamusume | 26 | win | 1023-990 | 421 | 17 (375) | 20 (335) | 421 | 33 | 1056 | 2/5/3/6/1 | 3/3/7/6/1 |
| c3eed638 | SSSA | 29 | loss | 792-1056 | 391 | 16 (375) | 17 (366) | 340 | 198 | 990 | 2/5/3/6/0 | 3/5/5/4/0 |
| 61a8e144 | octo's odyss | 23 | loss | 792-1056 | 368 | 14 (-) | 18 (348) | 340 | 66 | 858 | 2/5/3/4/0 | 4/4/5/5/0 |
| cc910d4f | ひななー | 21 | loss | 957-1056 | 420 | 17 (375) | 16 (394) | 397 | 99 | 1056 | 2/5/3/6/1 | 2/4/5/5/0 |
| 5053757b | lETHal | 16 | loss | 957-1056 | 415 | 17 (375) | 17 (394) | 397 | 99 | 1056 | 2/5/3/6/1 | 3/3/5/5/1 |
| 67768aef | Boost | 15 | loss | 858-1056 | 391 | 14 (-) | 17 (370) | 384 | 66 | 924 | 2/5/3/4/0 | 4/5/4/4/0 |
| 9d948244 | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | 12 | loss | 957-1056 | 401 | 17 (375) | 16 (376) | 397 | 99 | 1056 | 2/5/3/6/1 | 2/5/5/4/0 |
| 27dfe5e4 | Full Damage | 11 | loss | 792-1056 | 368 | 14 (-) | 17 (343) | 340 | 66 | 858 | 2/5/3/4/0 | 4/4/5/4/0 |
| a17455eb | procless | 9 | loss | 792-1056 | 392 | 16 (375) | 16 (373) | 340 | 198 | 990 | 2/5/3/6/0 | 2/5/4/5/0 |
| e6728afb | Nyxius | 8 | loss | 792-1056 | 385 | 16 (375) | 17 (361) | 340 | 198 | 990 | 2/5/3/6/0 | 3/6/3/5/0 |
| 57caf3c2 | PTN Hyperion | 7 | loss | 957-1056 | 400 | 16 (375) | 17 (377) | 397 | 33 | 990 | 2/5/3/6/0 | 4/4/4/5/0 |
| df0f60f1 | VeryGood | 5 | loss | 792-1056 | 374 | 15 (-) | 16 (351) | 340 | 132 | 924 | 2/5/3/5/0 | 4/4/5/3/0 |

Reading: the script is fixed to the round — captures at r33, r58, r88, r116, r148, r169, r197, r217, r239 (split 33+33), r254, r276, r303, r313, r332, r365 (16th) in every game; last tribute r380; 165 gems carried at the end in 10 games (Varg 99 + one 66-bag), 99 in 5. We earn 1122 by r380 in 12 of 17 games (study26: 1056 in 4, 858-990 in the rest) and lose because the opponent tributes its 16th bag by r366-r398 while our 15th and 16th bags are still walking. The result is decided by (a) the half-bags: at r239 the pack is split 33/33 between Varg and Issac; Varg carries 33 gems from r239 to r379 and shops at spawn (2,2) with 99 at r380 (`0da6d890`, `ff9f5886`, all 17 games have `Var1 g33` from r240 to r340); (b) the 15-25 round capture→tribute walk at the end (our median delay 17 rounds, opp 21, but their 16th capture is a full bag). Wins (`2bc7a917`, `6e1049fe`, `a1b65574`): the opponent's 16th capture comes after r383 or never; nothing we did differed.

- `0da6d890` vs Mite (rank 1, loss 957-1056, 398 rounds). r20: Ven/Var/Iss/Cas all on (18,3) (four hitters, 52-100% hp), Ryth walking to (22,9); r33 capture, r40 the four at (28-30,5-8) on the middle pack, r58 capture, r80 all four on (41-43,4-6), r88 capture; Mite mirrors it with 4-5 hitters (captures r31, r55, r79). r100-r240 both sides cycle at the same pace (score 132-198 … 528-528); r239 split capture (Var1 33, Iss3 33). r240-r340: Var1 walks with 33 gems ((42,3) r240 recalling at 49% hp, (20,9) r260, (39,8) r280, (41,2) r300, (30,4) r320, (32,8) r340) and never tributes; r320 Iss3 and Ryt4 carry 66 each to the altar (15,16) (score 693→825 at r340); Mite's Ryt6 and Var5 recall home with 66 each ("buy" at (47,47) r320/r340 then tribute at (34,35)). r365 our 16th capture ((18,3), by Vendetta); r371 Mite's Cas7 captures; r379 Varg captures the far pack (42,3), 36 rounds after its respawn, and now holds 99; r380 score 957-924 with Ven0 tributing at (14,15), Var1 recalled to spawn (2,2) with 99 gems buying, Iss3/Ryt4 clearing (31,4) again; Mite captures its 16th at r381 and reaches 1056 at r398 while we hold 165.
- `ff9f5886` vs Shawn (rank 3, loss 891-1056, 351 rounds). Same script to the round (r33, r58, r88, r116, …, r239 split, r254, r276, r303, r313, r332 = 15 captures). Shawn is faster on its side: its (31,44) pack is recaptured 14-27 rounds after respawn from r98 on, (18,44) 14-17, and it tributes double bags (Iss9 132 at r120, Ryt6 132 at r160, Ven7 132 at r180, Ryt6 132 at r300): 16th capture r325, 1056 at r351. At r340 we are at 825 with Ven0 carrying 66 at (10,11) and Var1 still holding his 33 from r239 at (32,8). We never hit the 41000-hp monolith (0 hits in 17 games, both sides), nor our gold cluster.

### 5.2 lanes (17 games, 3-14; study26 18 games, 3-15)

| metric | us27 | us26 | z | opp27 | opp26 |
|---|---|---|---|---|---|
| own | 93.7±0.5 | 93.3±0.5 | +0.5 | 71.9±3.4 | 78.2±3.1 |
| mid | 5.7±0.4 | 5.9±0.4 | -0.4 | 8.8±1.1 | 9.6±1.8 |
| en | 0.5±0.2 | 0.7±0.3 | -0.4 | 19.3±4.2 | 12.3±2.8 |
| depth | 24.6±0.4 | 25.2±0.3 | -1.0 | 30.5±0.9 | 28.8±0.8 |
| pd | 13.3±0.2 | 12.8±0.2 | +1.9 | 12.9±0.5 | 12.4±0.4 |
| alone | 30.5±1.3 | 26.4±1.3 | +2.2 ** | 26.4±1.7 | 26.2±1.6 |
| idle | 13.5±0.5 | 13.9±0.4 | -0.7 | 13.5±0.8 | 12.3±1.2 |
| camp | 20.5±0.7 | 21.4±0.6 | -1.0 | 20.2±1.0 | 17.4±1.5 |
| fight | 1.2±0.1 | 1.2±0.2 | -0.2 | 2.3±0.4 | 1.9±0.3 |
| deaths | 3.8±0.9 | 3.8±0.6 | -0.0 | 0.8±0.3 | 1.4±0.4 |
| caps | 32.8±2.2 | 37.9±1.6 | -1.9 | 42.5±0.9 | 42.5±0.5 |
| cap_own | 29.1±2.0 | 33.2±1.3 | -1.7 | 29.5±1.2 | 32.8±0.6 |
| cap_mid | 3.0±0.4 | 3.8±0.6 | -1.1 | 7.5±1.3 | 6.2±1.0 |
| cap_en | 0.7±0.2 | 0.9±0.4 | -0.6 | 5.5±1.5 | 3.6±1.0 |
| gpr | 189.3±14.1 | 211.8±8.1 | -1.4 | 264.8±9.7 | 254.5±7.6 |

Our positions are unchanged (own 93.7/93.3, mid 5.7/5.9, enemy 0.5/0.7, pd 13.3/12.8, idle 13.5/13.9, deaths 3.8/3.8); alone 30.5 vs 26.4 (z=2.2) is the only flagged metric. What changed is the other side: the opponents stand in our half 19.3% of their rounds (12.3%), hold 71.9% own (78.2%), capture 5.5 groups in our half per game (3.6), 7.5 mid (6.2) and tribute 265 gems/100r (255). Our captures fell to 32.8 (37.9): the 4.1 fewer own-half captures are the clusters they sit on. Lane table (q8): with 2 invaders in one of our lanes we have 1.00 champion there (1.33) and are outnumbered 71% (57%); with 3 invaders 0.93 (1.22), 91% outnumbered; ≥3-invader rounds 568 (296). Idle streaks next to a living camp 30.5/game (35.3). The opening is no longer one pattern: 2 distinct position sets at r10/20/30 and 4 at r40 (1/1/1/1) — the "one champion per small camp" allocation varies with who reaches which cluster first, but all 17 games still send Vendetta/Issac/Cassi/Tavi top-middle and Varg/Ryth bottom.

- `c55dcf06` vs umamusume (rank 25, loss 250-1018, 312 rounds; they took 19 of our groups, 456 gems, first at r48). r20 our six on the usual tiles (26,18),(21,21),(22,22),(24,17),(21,29),(22,21); umamusume's six already at (62-69,0-6) heading for the top lane. r40: Vendetta (36,13) and Cassi (33,14) on our middle clusters, Issac (34,6) top, Varg/Ryth (40,27-29) bottom; umamusume's Ren10 is at (38,5) in our half, Cas6/Ste8/Tav11 at (47-49,0-4). r56 **Cassi and Issac die together at the top cluster** (Ste8 casting, Cas6 (36,2), Tav11 (38,2), Ren10 (31,2): four enemies on our top clusters, 2v4). r60-r160: Cas6, Ste8, Ren10, Tav11 rotate through (30-38,2-13) capturing our clusters every 10-15 rounds (CAP r62,65,66,69,73,84,94,99,101,118,120,121,135,136,147,148,153 …); our respawned Cassi/Issac walk back to (26,15)/(33,18) at r140 and die again at r152 at (36,15); Vendetta dies r157, Tavi r171, Varg r176: at r180 Ryth is our only champion alive, tributing 44 at (11,14). r220-r300 the pattern repeats (Ryth dies r262 at (33,9) casting at 7% hp, Tavi r275); we finish 250. In no snapshot are more than two of ours within 8 of the four squatters; Varg and Ryth farm (41-46,24-28) bottom for 300 rounds.
- `a9f211f4` vs Univardisty (rank 6, loss 344-1020, 311 rounds; 15 of our groups, 358 gems). r40 Univardisty's six stand at (53-55,2-14) — their side of the middle; r47-r50 they capture 8 mid/own clusters in 4 rounds (CAP r47: four groups); r60 Ryt6 (44,8), Ren10 (46,11), Tav11 (45,7) in the middle, Cas7/Iss8/Ste9 behind. r80 Ryt6 at (40,6) in our half attacking Vendetta (37,7, 62%); r92 Tavi dies at (39,12); r100 Ryt6 (27,0), Cas7 (36,3), Tav11 (30,3) are on our top clusters tributing at our altars ((30,3) `trib`), Vendetta/Issac recall at 25%/16% hp r120; r156 Vendetta dies; r193-r199 Tavi, Cassi+Issac die at the middle; r293-298 again. Score 232-566 at r200. Varg stays at (43-47,13-28) alone the whole game.

### 5.3 packs (22 games, 6-16; study26 21 games, 7-14)

| metric | us27 | us26 | z | opp27 | opp26 |
|---|---|---|---|---|---|
| own | 79.5±1.0 | 78.8±0.9 | +0.6 | 69.7±1.9 | 66.9±1.8 |
| mid | 20.1±1.0 | 20.3±0.9 | -0.1 | 23.4±1.4 | 24.5±1.3 |
| en | 0.2±0.1 | 0.7±0.2 | -1.9 | 7.0±1.0 | 8.6±1.3 |
| depth | 7.9±0.1 | 8.1±0.1 | -1.2 | 9.4±0.2 | 9.5±0.2 |
| pd | 8.0±0.2 | 8.2±0.1 | -0.9 | 9.5±0.2 | 9.7±0.3 |
| alone | 30.6±1.2 | 31.9±1.1 | -0.8 | 37.0±2.2 | 38.5±2.4 |
| idle | 9.5±0.5 | 9.4±0.3 | +0.3 | 8.4±0.7 | 9.2±0.7 |
| camp | 27.5±0.7 | 28.1±0.9 | -0.5 | 22.1±1.3 | 21.3±1.4 |
| fight | 3.0±0.3 | 3.4±0.3 | -0.9 | 2.6±0.3 | 2.7±0.3 |
| deaths | 7.1±0.9 | 7.0±1.0 | +0.1 | 2.4±0.4 | 3.8±0.6 |
| caps | 17.4±1.2 | 18.0±1.1 | -0.4 | 22.9±0.9 | 21.8±0.7 |
| cap_own | 11.5±0.7 | 11.4±0.7 | +0.1 | 13.1±0.9 | 13.3±0.8 |
| cap_mid | 5.9±0.7 | 6.5±0.6 | -0.7 | 8.5±0.7 | 7.6±0.7 |
| cap_en | 0.0±0.0 | 0.0±0.0 | +0.0 | 1.4±0.3 | 0.9±0.3 |
| gpr | 152.5±11.6 | 154.5±10.3 | -0.1 | 197.4±5.8 | 188.7±8.0 |

Same positions (own 79.5/78.8, pd 8.0/8.2, alone 30.6/31.9, deaths 7.1/7.0, caps 17.4/18.0). The opponents die less: 2.4/game (3.8, z=-2.0), 53 deaths vs 79, and cross into our half 7.0% (8.6%) but capture there more (1.4 vs 0.9/game; own-half group lost in 16 of 22 games, first r289 vs r426). Our enemy-half episodes 19 (40). Opening deaths: when we lose fewer champions before r100 we won 0 of 3 (3 of 4 before) — small n. The pair-death pattern is intact: Cassi+Issac die in the same round 5 times in `20ecdfaf`, 3 times in `7545df09`.

- `20ecdfaf` vs hello (rank 5, loss 332-1032, 487 rounds, 14 deaths). r20: Cassi (9,14)+Stellar (9,15) on the (11-12,17-18) mid pack, Issac (18,12)+Ren (17,12) on the (18-19,12-13) pack — the fixed opening; hello's four walk (19-22,19-27). r40 Cassi hit at (5,11) 45% hp carrying 48, Cas4/Ste6 of hello at (9-10,12) in our half casting; **r46 Cassi+Issac die**; r60 Ren (7,3) 42%, Stellar (8,2) idle, hello 2 captures ahead. r95 Ren dies; r136 Cassi+Issac again (at (13-15,14-15), 2v3); r208 Stellar, r219 Cassi+Issac, r352 Cassi+Issac, r367 Stellar, r388 Ren, r469 Cassi+Issac. Between deaths our survivors farm (8,2)/(16,2)/(24,2) and the 44-gem mid packs alone (Ren2 `camp` at (7,3) r200/r240/r300); hello farms all four central packs and its own (CAP every 10-20 rounds), 68-228 at r140, 244-756 at r400.
- `7545df09` vs Mate in One (rank 28, loss 488-1012, 470 rounds, 8 deaths). r20 identical opening; Mate in One's Var4 (24,27), Ste5 (14,20) walking to our (11,17) pack. **r33 Cassi+Issac die** at the (18,12) pack (Ste5+Var4+Iss7 from the south, our Ren at (14,9) `..` idle, Stellar (0,4) walking home) — first death of the game at r33, the opponent 44-0 up. r41-r54 they capture both mid packs; r100-r200 we are two champions (Ren (8,3) camp, Stellar (16-21,8-10) `..` idle 21 rounds at (21,9) r141-r162 next to the enemy-held pack) and recover to 136-320; r209 Cassi+Issac die again at the (11,17) pack, r323 Stellar, r406 Cassi+Issac, r447 Stellar. Opp mid captures 9, ours 3.

### 5.4 monolith (16 games, 5-11; study26 13 games, 5-8)

| metric | us27 | us26 | z | opp27 | opp26 |
|---|---|---|---|---|---|
| own | 79.1±0.7 | 81.1±0.9 | -1.7 | 83.6±1.1 | 80.2±1.8 |
| mid | 19.2±0.6 | 17.1±0.7 | +2.3 ** | 11.1±0.7 | 12.0±1.0 |
| en | 1.6±0.3 | 1.7±0.4 | -0.3 | 5.2±0.8 | 7.9±1.9 |
| depth | 17.7±0.2 | 17.4±0.2 | +1.1 | 16.8±0.5 | 17.9±0.5 |
| pd | 16.9±0.2 | 16.5±0.2 | +1.6 | 16.0±0.6 | 17.4±0.7 |
| alone | 45.4±0.7 | 45.7±0.8 | -0.2 | 45.1±2.5 | 49.6±2.5 |
| idle | 5.9±0.2 | 5.3±0.2 | +2.1 ** | 9.0±1.3 | 9.2±1.0 |
| camp | 22.8±0.4 | 22.6±0.5 | +0.3 | 23.1±1.7 | 24.0±0.6 |
| fight | 0.9±0.1 | 0.9±0.1 | +0.1 | 0.9±0.2 | 1.3±0.1 |
| deaths | 2.8±0.4 | 3.8±0.6 | -1.3 | 2.4±0.4 | 2.5±0.5 |
| caps | 27.4±0.7 | 26.5±0.8 | +0.9 | 31.8±0.8 | 31.0±1.2 |
| cap_own | 25.8±0.7 | 25.2±0.8 | +0.6 | 30.9±0.8 | 29.3±1.2 |
| cap_mid | 0.0±0.0 | 0.0±0.0 | +0.0 | 0.0±0.0 | 0.0±0.0 |
| cap_en | 1.6±0.3 | 1.2±0.3 | +0.9 | 0.9±0.3 | 1.7±0.3 |
| gpr | 202.2±6.0 | 196.9±7.8 | +0.5 | 215.1±7.7 | 215.5±8.6 |

A farming race we lose by 4.4 captures/game (27.4 vs 31.8; study26 26.5 vs 31.0): their respawn→capture latency 36 rounds median (ours 49), their clearings 20 rounds with 1.83 hitters (ours 25, 1.43), their 3+-hitter clearings 21% (ours 4%) — the opponents stack on monolith's 2700-hp wolf pairs, we do not (below the 3000 threshold). We now stand in the middle 19.2% (17.1, z=2.3) because the tribute altars (19,19)/(30,30) are in the band, and idle 5.9% (5.3, z=2.1). Deaths 2.8 (3.8), 57% alone. Own-half group lost in 8 of 16 games (11 of 13).

- `233c4851` vs Mite (rank 1, loss 718-1002, 444 rounds, 6 deaths). r20 our fixed opening (Vendetta buying at spawn, Varg (11,26), Cassi (11,34), Issac (14,46), Ryth (22,49), Tavi (12,49)); Mite's six hit (36-39,6-20) with 4 on one camp. r60 110-102, even. r100-r180: **Issac stands at (5,21) doing nothing from r115 to r190** (hp 82%, 0 gems, no enemy within 8 until r120), while Mite's Var6 walks our half ((9,14) r120, (5,10) r240 capturing our (3,9) wolves, (11,11) r260 tributing 44 at our altar (12,10)); r159 Tavi dies at (29,31) (mid altar, 1v2); r222 Vendetta dies at (16,23) to Var6 alone (19% hp, `miss`); r324 Varg at (9,16) 7% hp dies; r350 Cassi+Issac die at (33,34)/(35,48); r418 Vendetta. Mite 33 own-half captures + 2 of ours; we 22 + 2 of theirs (Ryth at (26,14) r280). Score 286-212 at r160 → 440-556 at r280 → 718-1002.
- `d181f483` vs Nyxius (rank 12, loss 688-1010, 387 rounds, 2 deaths). No fight until r201 (Cassi+Issac die at (15,22)/(20,20) while tributing at the mid altar, Ven7+Ryt10). Captures: Nyxius 31 (r17, 19, 28, 38, 39, 43, 48, 49, 57, 64, 72, 87, 95, 96, 111 ×2, 113, 115, 131, 140, 143, 148, 152, 173 ×2, 174 ×2, 175 …), always 2-3 champions per wolf pair and recalling home with 44-88 gems ("Var6 g88 camp" r100, "Ven7 g88" r120); ours 21 with one champion per camp (Var1 (4,10) `camp` alone r100/r280, Cas2 (6,36) alone r60-r200) and the same Issac idle at (5,21) r115-r145. 154-0 at r100 (their first tribute is late), 308-410 at r200, 586-798 at r320.


## 6. Deaths (Q7) and numbers at contact (Q9)

### 6a. Deaths

| split | who | n | per game | own/mid/enemy | at camp | allies 0/1/2+ | enemies 1/2/3+ | alone 5r before | farming before | camp-hit before | gems lost (med/mean) | attackers med | spawn dist med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 899 | 5.8 | 73/25/2 | 24% | 32/39/29 | 27/29/32 | 32% | 5% | 15% | 0/11 | 1 | 13 |
| ALL | us26 | 858 | 5.7 | 76/21/3 | 24% | 33/37/30 | 31/29/28 | 34% | 7% | 17% | 0/10 | 1 | 13 |
| ALL | opp27 | 626 | 4.0 | 41/35/25 | 22% | 34/34/32 | 28/34/23 | 33% | 7% | 13% | 0/17 | 1 | 17 |
| ALL | opp26 | 581 | 3.9 | 39/34/28 | 28% | 37/31/31 | 30/31/23 | 36% | 6% | 15% | 0/15 | 1 | 17 |
| res:win | us27 | 182 | 3.1 | 65/31/4 | 27% | 24/41/35 | 31/31/27 | 28% | 6% | 19% | 0/13 | 1 | 14 |
| res:win | us26 | 195 | 3.3 | 67/30/3 | 30% | 23/42/35 | 34/30/19 | 30% | 6% | 23% | 0/13 | 1 | 13 |
| res:win | opp27 | 387 | 6.7 | 43/34/23 | 21% | 34/33/33 | 25/37/23 | 30% | 7% | 11% | 0/18 | 1 | 16 |
| res:win | opp26 | 353 | 6.0 | 42/37/20 | 26% | 37/33/29 | 25/31/27 | 36% | 5% | 13% | 0/18 | 1 | 16 |
| res:loss | us27 | 717 | 7.4 | 75/24/2 | 23% | 34/38/27 | 26/29/33 | 33% | 5% | 14% | 0/10 | 1 | 13 |
| res:loss | us26 | 663 | 7.3 | 79/19/3 | 22% | 36/35/29 | 30/29/31 | 35% | 7% | 16% | 0/9 | 1 | 12 |
| res:loss | opp27 | 239 | 2.5 | 37/35/28 | 23% | 34/36/30 | 33/29/21 | 38% | 8% | 15% | 0/15 | 1 | 17 |
| res:loss | opp26 | 228 | 2.5 | 33/28/39 | 31% | 36/29/35 | 37/32/17 | 35% | 7% | 17% | 0/10 | 1 | 19 |
| map:collision | us27 | 240 | 12.6 | 59/41/0 | 50% | 25/43/32 | 33/30/20 | 26% | 5% | 34% | 0/13 | 1 | 13 |
| map:collision | us26 | 215 | 11.3 | 65/33/2 | 53% | 22/45/33 | 33/32/16 | 28% | 6% | 33% | 0/11 | 1 | 12 |
| map:collision | opp27 | 167 | 8.8 | 32/55/13 | 43% | 31/43/26 | 31/32/19 | 32% | 10% | 24% | 0/23 | 1 | 16 |
| map:collision | opp26 | 161 | 8.5 | 38/52/11 | 43% | 34/37/29 | 29/30/23 | 37% | 7% | 18% | 22/24 | 1 | 16 |
| map:corners | us27 | 235 | 12.4 | 75/20/6 | 14% | 29/40/32 | 12/31/57 | 27% | 0% | 0% | 0/7 | 2 | 14 |
| map:corners | us26 | 230 | 13.5 | 80/17/2 | 12% | 33/37/30 | 17/27/56 | 30% | 0% | 0% | 0/8 | 2 | 13 |
| map:corners | opp27 | 145 | 7.6 | 57/30/13 | 22% | 19/20/61 | 19/36/34 | 14% | 5% | 0% | 0/9 | 2 | 16 |
| map:corners | opp26 | 121 | 7.1 | 38/37/25 | 29% | 17/22/61 | 14/40/40 | 13% | 0% | 0% | 0/13 | 2 | 17 |
| map:elkring | us27 | 55 | 6.1 | 73/24/4 | 21% | 38/44/18 | 44/25/18 | 30% | 1% | 29% | 0/20 | 1 | 10 |
| map:elkring | us26 | 91 | 6.5 | 78/19/3 | 14% | 48/35/16 | 34/36/19 | 37% | 9% | 31% | 0/15 | 1 | 11 |
| map:elkring | opp27 | 100 | 11.1 | 35/28/37 | 13% | 45/33/22 | 42/32/15 | 43% | 7% | 22% | 0/14 | 1 | 18 |
| map:elkring | opp26 | 113 | 8.1 | 42/24/35 | 17% | 42/35/23 | 42/27/12 | 39% | 9% | 29% | 0/9 | 1 | 17 |
| map:expanse | opp27 | 1 | 0.1 | 0/0/100 | 0% | 100/0/0 | 100/0/0 | 100% | 0% | 0% | 0/0 | 1 | 64 |
| map:expanse | opp26 | 1 | 0.1 | 0/0/100 | 0% | 100/0/0 | 0/100/0 | 100% | 0% | 0% | 0/0 | 2 | 61 |
| map:interlock | us27 | 101 | 5.3 | 86/12/2 | 13% | 35/36/30 | 19/30/36 | 34% | 8% | 11% | 22/25 | 1 | 14 |
| map:interlock | us26 | 56 | 4.3 | 75/21/4 | 8% | 29/27/45 | 29/38/21 | 30% | 8% | 10% | 22/27 | 1 | 14 |
| map:interlock | opp27 | 109 | 5.7 | 46/24/30 | 2% | 31/32/37 | 24/35/26 | 32% | 7% | 7% | 0/27 | 1 | 17 |
| map:interlock | opp26 | 42 | 3.2 | 50/19/31 | 7% | 50/29/21 | 19/26/36 | 52% | 7% | 7% | 0/22 | 1 | 16 |
| map:lanes | us27 | 64 | 3.8 | 94/5/2 | 23% | 23/39/38 | 17/23/52 | 21% | 9% | 17% | 0/6 | 2 | 28 |
| map:lanes | us26 | 68 | 3.8 | 84/12/4 | 39% | 22/28/50 | 24/34/32 | 20% | 16% | 27% | 0/4 | 2 | 30 |
| map:lanes | opp27 | 13 | 0.8 | 15/8/77 | 23% | 46/46/8 | 15/62/23 | 38% | 0% | 23% | 22/20 | 1 | 44 |
| map:lanes | opp26 | 26 | 1.4 | 38/12/50 | 57% | 46/42/12 | 12/50/19 | 53% | 3% | 30% | 0/8 | 1 | 41 |
| map:monolith | us27 | 45 | 2.8 | 60/36/4 | 20% | 58/33/9 | 40/24/13 | 64% | 11% | 15% | 0/9 | 1 | 22 |
| map:monolith | us26 | 49 | 3.8 | 73/20/6 | 10% | 55/41/4 | 47/22/8 | 51% | 14% | 22% | 0/13 | 1 | 20 |
| map:monolith | opp27 | 38 | 2.4 | 34/29/37 | 21% | 82/18/0 | 29/42/13 | 84% | 10% | 13% | 0/12 | 1 | 27 |
| map:monolith | opp26 | 32 | 2.5 | 38/22/41 | 12% | 66/22/12 | 44/28/16 | 59% | 3% | 9% | 0/16 | 1 | 28 |
| map:packs | us27 | 157 | 7.1 | 76/23/1 | 9% | 39/35/25 | 40/31/11 | 41% | 12% | 9% | 0/4 | 1 | 9 |
| map:packs | us26 | 147 | 7.0 | 82/18/1 | 8% | 39/34/27 | 47/20/17 | 48% | 9% | 9% | 0/3 | 1 | 9 |
| map:packs | opp27 | 53 | 2.4 | 34/26/40 | 13% | 28/58/13 | 28/30/17 | 32% | 9% | 7% | 0/7 | 1 | 13 |
| map:packs | opp26 | 79 | 3.8 | 33/29/38 | 17% | 42/33/25 | 47/25/13 | 36% | 8% | 11% | 0/5 | 1 | 13 |
| map:rows | us27 | 2 | 0.1 | 100/0/0 | 0% | 100/0/0 | 100/0/0 | 100% | 0% | 0% | 33/33 | 1 | 11 |
| map:rows | us26 | 2 | 0.1 | 100/0/0 | 0% | 50/0/50 | 50/0/0 | 50% | 0% | 0% | 33/33 | 1 | 14 |
| map:rows | opp26 | 6 | 0.3 | 33/0/67 | 33% | 67/33/0 | 17/33/17 | 66% | 16% | 33% | 0/0 | 1 | 59 |

899 deaths (5.8/game) vs 858 (5.7); opponents 626 (4.0) vs 581 (3.9). By zone: ours 73/25/2 (76/21/3): 225 of ours in the middle vs 180 — the only zone shift above noise, from corners (20% vs 17%, 47 vs 39), collision (41 vs 33%, 98 vs 71 deaths) and monolith (36 vs 20%, 16 vs 10). Lanes: 94% own-half (84%), at a camp 23% (39%: 15 vs 27 deaths next to a living camp — we die on the lane tiles between clusters now), 52% with 3+ enemies within 6 (32%). Interlock 101 deaths (5.3/game) vs 56 (4.3) in 19 vs 13 games; mean gems lost 25. Everything else (allies 0/1/2+ 32/39/29, alone 5 rounds before 32%, camp-hit before 15%, median attackers 1, spawn distance 13) is the study26 picture. By type: Stellar 185, Cassi 176, Issac 176, Ren 106, Tavi 100, Prism 70, Ryth 64, Vendetta 13, Varg 9.

### 6b. Opening deaths vs result, and local numbers

| map | batch | games | our deaths <r100 (W / L) | their deaths <r100 (W / L) | win% when we lose more champions before r100 | win% when we lose fewer | win% when equal |
|---|---|---|---|---|---|---|---|
| ALL | 27 | 155 | 0.2 / 0.8 | 0.6 / 0.2 | 8% (n=37) | 66% (n=21) | 42% (n=97) |
| ALL | 26 | 150 | 0.3 / 0.8 | 0.5 / 0.3 | 26% (n=38) | 56% (n=23) | 40% (n=89) |
| collision | 27 | 19 | 0.2 / 1.1 | 0.9 / 0.0 | 14% (n=7) | 100% (n=4) | 37% (n=8) |
| collision | 26 | 19 | 0.6 / 0.9 | 0.6 / 0.0 | 57% (n=7) | 100% (n=3) | 55% (n=9) |
| corners | 27 | 19 | 0.5 / 1.9 | 2.0 / 0.6 | 0% (n=10) | 100% (n=4) | 80% (n=5) |
| corners | 26 | 17 | 1.2 / 2.1 | 1.8 / 0.8 | 22% (n=9) | 50% (n=4) | 25% (n=4) |
| elkring | 27 | 9 | 0.4 / 0.8 | 0.2 / 0.8 | 50% (n=2) | 50% (n=2) | 60% (n=5) |
| elkring | 26 | 14 | 0.2 / 0.8 | 0.6 / 0.6 | 20% (n=5) | 40% (n=5) | 50% (n=4) |
| expanse | 27 | 17 | 0.0 / 0.0 | 0.0 / 0.0 | - | - | 58% (n=17) |
| expanse | 26 | 17 | 0.0 / 0.0 | 0.0 / 0.0 | - | - | 64% (n=17) |
| interlock | 27 | 19 | 0.0 / 1.6 | 0.5 / 0.6 | 0% (n=4) | 80% (n=5) | 60% (n=10) |
| interlock | 26 | 13 | 0.3 / 0.8 | 0.4 / 0.3 | 33% (n=3) | 66% (n=3) | 57% (n=7) |
| lanes | 27 | 17 | 0.0 / 0.8 | 0.3 / 0.0 | 0% (n=7) | 100% (n=1) | 22% (n=9) |
| lanes | 26 | 18 | 0.3 / 0.9 | 0.7 / 0.1 | 0% (n=6) | 50% (n=2) | 20% (n=10) |
| monolith | 27 | 16 | 0.2 / 0.3 | 0.2 / 0.2 | 0% (n=2) | 0% (n=2) | 41% (n=12) |
| monolith | 26 | 13 | 0.4 / 0.4 | 0.0 / 0.5 | 50% (n=2) | 0% (n=2) | 44% (n=9) |
| packs | 27 | 22 | 0.3 / 0.6 | 0.2 / 0.4 | 20% (n=5) | 0% (n=3) | 35% (n=14) |
| packs | 26 | 21 | 0.1 / 0.9 | 0.9 / 0.1 | 16% (n=6) | 75% (n=4) | 27% (n=11) |
| rows | 27 | 17 | 0.0 / 0.0 | 0.0 / 0.0 | - | - | 17% (n=17) |
| rows | 26 | 18 | 0.0 / 0.0 | 0.0 / 0.0 | - | - | 22% (n=18) |

| split | who | champ-rounds | outnumbered | even | outnumbering | deaths n | deaths while outnumbered | even | outnumbering |
|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | 45371 | 14% | 22% | 63% | 899 | 32% | 27% | 40% |
| ALL | us26 | 42415 | 14% | 22% | 62% | 858 | 31% | 26% | 42% |
| ALL | opp27 | 44845 | 15% | 22% | 61% | 626 | 28% | 25% | 46% |
| ALL | opp26 | 41736 | 15% | 23% | 60% | 581 | 29% | 24% | 45% |
| map:collision | us27 | 9628 | 10% | 20% | 68% | 240 | 20% | 26% | 53% |
| map:collision | us26 | 9246 | 10% | 20% | 69% | 215 | 16% | 29% | 53% |
| map:collision | opp27 | 8947 | 17% | 23% | 58% | 167 | 28% | 17% | 54% |
| map:collision | opp26 | 8327 | 17% | 25% | 56% | 161 | 31% | 23% | 44% |
| map:corners | us27 | 10971 | 26% | 22% | 51% | 235 | 57% | 28% | 14% |
| map:corners | us26 | 9358 | 28% | 23% | 48% | 230 | 56% | 26% | 17% |
| map:corners | opp27 | 12851 | 11% | 15% | 72% | 145 | 21% | 26% | 52% |
| map:corners | opp26 | 11303 | 9% | 15% | 75% | 121 | 24% | 23% | 51% |
| map:elkring | us27 | 3182 | 15% | 22% | 61% | 55 | 30% | 27% | 41% |
| map:elkring | us26 | 4580 | 17% | 23% | 58% | 91 | 37% | 20% | 41% |
| map:elkring | opp27 | 3437 | 13% | 19% | 67% | 100 | 31% | 28% | 41% |
| map:elkring | opp26 | 4917 | 13% | 22% | 64% | 113 | 27% | 23% | 49% |
| map:expanse | us27 | 124 | 0% | 22% | 77% | 0 | 0% | 0% | 0% |
| map:expanse | us26 | 148 | 0% | 22% | 77% | 0 | 0% | 0% | 0% |
| map:interlock | us27 | 7038 | 9% | 14% | 75% | 101 | 29% | 23% | 46% |
| map:interlock | us26 | 4227 | 10% | 15% | 74% | 56 | 25% | 19% | 55% |
| map:interlock | opp27 | 6282 | 19% | 21% | 59% | 109 | 29% | 25% | 44% |
| map:interlock | opp26 | 3864 | 17% | 21% | 61% | 42 | 40% | 21% | 38% |
| map:lanes | us27 | 5200 | 12% | 22% | 64% | 64 | 39% | 32% | 28% |
| map:lanes | us26 | 5248 | 8% | 20% | 71% | 68 | 29% | 30% | 39% |
| map:lanes | opp27 | 4856 | 16% | 22% | 60% | 13 | 30% | 69% | 0% |
| map:lanes | opp26 | 4545 | 20% | 23% | 55% | 26 | 42% | 11% | 46% |
| map:monolith | us27 | 3146 | 9% | 36% | 54% | 45 | 24% | 31% | 44% |
| map:monolith | us26 | 2832 | 11% | 33% | 55% | 49 | 18% | 34% | 46% |
| map:monolith | opp27 | 2832 | 21% | 40% | 38% | 38 | 52% | 28% | 18% |
| map:monolith | opp26 | 2606 | 19% | 42% | 37% | 32 | 40% | 31% | 28% |
| map:packs | us27 | 6002 | 10% | 24% | 65% | 157 | 15% | 29% | 55% |
| map:packs | us26 | 6332 | 10% | 26% | 62% | 147 | 19% | 21% | 59% |
| map:packs | opp27 | 5521 | 18% | 27% | 53% | 53 | 24% | 28% | 47% |
| map:packs | opp26 | 5848 | 17% | 28% | 53% | 79 | 18% | 36% | 44% |
| map:rows | us26 | 444 | 3% | 14% | 82% | 2 | 0% | 50% | 50% |
| map:rows | opp26 | 233 | 57% | 31% | 11% | 6 | 50% | 0% | 50% |

When we lose more champions than the opponent before r100 we win **8% (n=37)** (26%, n=38): collision 1 of 7 (4 of 7), corners 0 of 10 (2 of 9), interlock 0 of 4, lanes 0 of 7. Outnumbered share 14/22/63% (14/22/62); corners deaths outnumbered 57% (56%). No change in how we fight; a worse draw of early fights on collision/corners explains those two maps' swings (collision 12-7 → 8-11, corners 5-12 → 8-11).


## 7. Is the opening a script? (Q10)

| map | batch | games | us r10 | us r20 | us r30 | us r40 | opp r10 | opp r20 | opp r30 | opp r40 |
|---|---|---|---|---|---|---|---|---|---|---|
| collision | 27 | 19 | 1 | 4 | 10 | 19 | 19 | 19 | 19 | 19 |
| collision | 26 | 19 | 2 | 4 | 11 | 17 | 19 | 19 | 19 | 19 |
| corners | 27 | 19 | 3 | 11 | 19 | 19 | 19 | 19 | 19 | 19 |
| corners | 26 | 17 | 2 | 8 | 14 | 16 | 17 | 17 | 17 | 17 |
| elkring | 27 | 9 | 1 | 1 | 1 | 1 | 9 | 9 | 9 | 9 |
| elkring | 26 | 14 | 2 | 2 | 2 | 2 | 14 | 14 | 14 | 14 |
| expanse | 27 | 17 | 2 | 2 | 2 | 2 | 17 | 17 | 17 | 17 |
| expanse | 26 | 17 | 2 | 2 | 2 | 2 | 17 | 17 | 17 | 17 |
| interlock | 27 | 19 | 2 | 1 | 3 | 16 | 19 | 19 | 19 | 19 |
| interlock | 26 | 13 | 2 | 2 | 2 | 11 | 13 | 13 | 13 | 13 |
| lanes | 27 | 17 | 2 | 2 | 2 | 4 | 17 | 17 | 17 | 17 |
| lanes | 26 | 18 | 1 | 1 | 1 | 1 | 18 | 18 | 18 | 18 |
| monolith | 27 | 16 | 1 | 1 | 2 | 2 | 16 | 16 | 16 | 16 |
| monolith | 26 | 13 | 1 | 1 | 1 | 1 | 13 | 13 | 13 | 13 |
| packs | 27 | 22 | 2 | 8 | 15 | 18 | 22 | 22 | 22 | 22 |
| packs | 26 | 21 | 1 | 7 | 12 | 14 | 21 | 21 | 21 | 21 |
| rows | 27 | 17 | 3 | 3 | 3 | 3 | 17 | 17 | 17 | 17 |
| rows | 26 | 18 | 1 | 1 | 1 | 1 | 18 | 18 | 18 | 18 |

Rows 3 patterns (1), lanes 2/2/2/4 (1/1/1/1), monolith 1/1/2/2, interlock 2/1/3/16, corners 3/11/19/19 (2/8/14/16), packs 2/8/15/18 (1/7/12/14): the stacking/one-per-camp allocation introduced a second or third variant of the first 40 rounds on rows and lanes, but the tiles are the same sets (the rows variants differ in which of Vendetta/Varg takes (17,4) vs (17,5)). The opponents are as varied as before (one pattern per game).

## 8. Farm cycle (Q6, Q11, Q13)

| map | who | captures | latency med/mean/p75 | own-half latency med | waiting at dead camp (champ-rounds per game) | idle share | tributes/game | median bag | p90 bag |
|---|---|---|---|---|---|---|---|---|---|
| rows | us27 | 295 | 30 / 32.8 / 41 | 30 | 102 | 7% | 14.0 | 66 | 66 |
| rows | us26 | 285 | 27 / 40.9 / 41 | 27 | 92 | 9% | 13.3 | 66 | 66 |
| rows | opp27 | 289 | 25 / 32.3 / 36 | 25 | 154 | 9% | 14.6 | 66 | 66 |
| rows | opp26 | 310 | 26 / 35.0 / 42 | 26 | 180 | 10% | 14.6 | 66 | 66 |
| expanse | us27 | 406 | 52 / 69.3 / 75 | 52 | 78 | 6% | 23.2 | 48 | 48 |
| expanse | us26 | 424 | 47 / 64.5 / 73 | 47 | 82 | 7% | 23.7 | 48 | 48 |
| expanse | opp27 | 446 | 33 / 47.4 / 54 | 33 | 161 | 11% | 20.8 | 48 | 70 |
| expanse | opp26 | 419 | 37 / 51.7 / 57 | 37 | 162 | 12% | 19.1 | 48 | 70 |
| lanes | us27 | 558 | 48 / 68.2 / 72 | 47 | 239 | 13% | 24.2 | 24 | 48 |
| lanes | us26 | 682 | 47 / 64.7 / 72 | 40 | 267 | 14% | 28.4 | 24 | 48 |
| lanes | opp27 | 723 | 43 / 65.3 / 77 | 37 | 266 | 13% | 31.2 | 24 | 48 |
| lanes | opp26 | 765 | 42 / 64.1 / 76 | 38 | 259 | 12% | 30.8 | 24 | 48 |
| monolith | us27 | 439 | 49 / 65.5 / 81 | 49 | 113 | 6% | 22.2 | 44 | 44 |
| monolith | us26 | 344 | 49 / 62.8 / 74 | 48 | 99 | 5% | 21.8 | 44 | 44 |
| monolith | opp27 | 509 | 36 / 48.6 / 55 | 35 | 172 | 9% | 21.7 | 44 | 66 |
| monolith | opp26 | 403 | 38 / 48.9 / 62 | 36 | 183 | 9% | 21.1 | 44 | 66 |
| elkring | us27 | 230 | 41 / 53.9 / 66 | 40 | 128 | 7% | 23.0 | 36 | 36 |
| elkring | us26 | 333 | 41 / 52.6 / 61 | 40 | 120 | 7% | 20.1 | 36 | 36 |
| elkring | opp27 | 260 | 37 / 53.3 / 63 | 35 | 262 | 11% | 21.3 | 36 | 72 |
| elkring | opp26 | 380 | 41 / 55.7 / 69 | 39 | 205 | 9% | 22.4 | 36 | 72 |
| interlock | us27 | 518 | 26 / 39.7 / 40 | 26 | 138 | 8% | 21.8 | 22 | 72 |
| interlock | us26 | 357 | 25 / 41.4 / 39 | 25 | 145 | 8% | 23.0 | 22 | 72 |
| interlock | opp27 | 437 | 33 / 46.4 / 51 | 32 | 191 | 11% | 17.5 | 44 | 72 |
| interlock | opp26 | 321 | 31 / 44.4 / 51 | 30 | 215 | 12% | 18.8 | 40 | 72 |

| map | who | clearings | first hit->capture med/mean | hitters mean | 1 / 2 / 3+ hitters | tribute delay med/mean (n) |
|---|---|---|---|---|---|---|
| rows | us27 | 293 | 18 / 18.5 | 3.16 | 6% / 19% / 74% | 17 / 22.7 (238) |
| rows | us26 | 270 | 21 / 25.5 | 2.70 | 7% / 23% / 70% | 21 / 23.1 (239) |
| rows | opp27 | 247 | 20 / 25.5 | 3.00 | 12% / 15% / 73% | 21 / 30.3 (247) |
| rows | opp26 | 269 | 20 / 26.6 | 2.90 | 11% / 21% / 68% | 23 / 31.0 (262) |
| expanse | us27 | 406 | 24 / 24.5 | 1.13 | 88% / 12% / 1% | 12 / 12.7 (395) |
| expanse | us26 | 423 | 24 / 24.3 | 1.10 | 90% / 10% / 0% | 12 / 12.7 (403) |
| expanse | opp27 | 417 | 20 / 27.0 | 1.46 | 64% / 28% / 8% | 13 / 19.8 (353) |
| expanse | opp26 | 386 | 23 / 27.8 | 1.30 | 75% / 21% / 4% | 13 / 22.2 (324) |
| monolith | us27 | 435 | 25 / 30.6 | 1.43 | 61% / 35% / 4% | 31 / 36.1 (350) |
| monolith | us26 | 339 | 24 / 30.1 | 1.47 | 57% / 39% / 4% | 31 / 36.3 (277) |
| monolith | opp27 | 458 | 20 / 26.2 | 1.83 | 47% / 33% / 21% | 27 / 44.0 (338) |
| monolith | opp26 | 358 | 21 / 34.1 | 1.72 | 52% / 31% / 16% | 32 / 42.3 (265) |
| lanes | us27 | 481 | 18 / 33.8 | 1.17 | 84% / 14% / 1% | 12 / 17.3 (407) |
| lanes | us26 | 593 | 17 / 35.0 | 1.25 | 78% / 19% / 3% | 8 / 16.2 (507) |
| lanes | opp27 | 574 | 16 / 33.6 | 1.53 | 60% / 28% / 11% | 9 / 20.8 (521) |
| lanes | opp26 | 605 | 16 / 34.6 | 1.64 | 59% / 26% / 16% | 11 / 21.6 (549) |

| map | who | class | captures | per game | first hit->cap med/mean | distinct hitters | max concurrent | conc 1/2/3/4+ | gems/cap |
|---|---|---|---|---|---|---|---|---|---|
| ALL | us27 | big | 314 | 2.0 | 19 / 18.9 | 3.09 | 3.03 | 7/23/30/40% | 66 |
| ALL | us26 | big | 286 | 1.9 | 22 / 25.6 | 2.60 | 2.52 | 12/24/64/0% | 67 |
| ALL | opp27 | big | 281 | 1.8 | 21 / 30.0 | 2.78 | 2.62 | 21/23/35/21% | 71 |
| ALL | opp26 | big | 300 | 2.0 | 21 / 29.0 | 2.73 | 2.61 | 19/26/35/20% | 69 |
| ALL | us27 | small | 3100 | 20.0 | 22 / 34.0 | 1.58 | 1.44 | 63/32/5/1% | 33 |
| ALL | us26 | small | 3085 | 20.6 | 22 / 34.4 | 1.60 | 1.44 | 61/33/6/0% | 33 |
| ALL | opp27 | small | 3195 | 20.6 | 20 / 35.4 | 1.86 | 1.63 | 56/30/10/4% | 33 |
| ALL | opp26 | small | 3023 | 20.2 | 20 / 35.8 | 1.87 | 1.64 | 57/29/9/5% | 33 |
| collision | us27 | big | 2 | 0.1 | 52 / 52.5 | 1.50 | 1.50 | 50/50/0/0% | 108 |
| collision | us26 | big | 1 | 0.1 | 85 / 85.0 | 1.00 | 1.00 | 100/0/0/0% | 108 |
| collision | opp27 | big | 21 | 1.1 | 28 / 51.8 | 1.24 | 1.19 | 81/19/0/0% | 108 |
| collision | opp26 | big | 17 | 0.9 | 32 / 49.1 | 1.18 | 1.12 | 88/12/0/0% | 108 |
| collision | us27 | small | 465 | 24.5 | 23 / 58.2 | 1.61 | 1.31 | 71/27/2/0% | 22 |
| collision | us26 | small | 481 | 25.3 | 21 / 52.1 | 1.64 | 1.33 | 68/30/1/0% | 22 |
| collision | opp27 | small | 402 | 21.2 | 23 / 65.4 | 1.82 | 1.49 | 66/24/6/4% | 24 |
| collision | opp26 | small | 403 | 21.2 | 23 / 58.3 | 1.85 | 1.55 | 60/30/6/4% | 24 |
| expanse | us27 | big | 19 | 1.1 | 21 / 21.3 | 2.11 | 2.11 | 11/74/11/5% | 108 |
| expanse | us26 | big | 15 | 0.9 | 24 / 24.5 | 1.00 | 1.00 | 100/0/0/0% | 108 |
| expanse | opp27 | big | 9 | 0.5 | 31 / 55.9 | 1.00 | 1.00 | 100/0/0/0% | 108 |
| expanse | opp26 | big | 13 | 0.8 | 31 / 42.4 | 1.08 | 1.08 | 92/8/0/0% | 108 |
| expanse | us27 | small | 387 | 22.8 | 24 / 24.6 | 1.09 | 1.05 | 95/5/0/0% | 38 |
| expanse | us26 | small | 408 | 24.0 | 24 / 24.3 | 1.11 | 1.07 | 93/7/0/0% | 38 |
| expanse | opp27 | small | 408 | 24.0 | 19 / 26.3 | 1.47 | 1.41 | 66/28/5/1% | 38 |
| expanse | opp26 | small | 373 | 21.9 | 22 / 27.3 | 1.30 | 1.25 | 78/20/2/1% | 38 |
| lanes | us27 | small | 481 | 28.3 | 18 / 33.8 | 1.17 | 1.07 | 93/7/0/0% | 24 |
| lanes | us26 | small | 593 | 32.9 | 17 / 35.0 | 1.25 | 1.10 | 91/9/1/0% | 24 |
| lanes | opp27 | small | 574 | 33.8 | 16 / 33.6 | 1.53 | 1.29 | 75/22/3/0% | 24 |
| lanes | opp26 | small | 605 | 33.6 | 16 / 34.6 | 1.64 | 1.40 | 71/21/7/2% | 24 |
| monolith | opp27 | big | 1 | 0.1 | 238 / 238.0 | 2.00 | 2.00 | 0/100/0/0% | 196 |
| monolith | us27 | small | 435 | 27.2 | 25 / 30.6 | 1.43 | 1.37 | 67/30/4/0% | 36 |
| monolith | us26 | small | 339 | 26.1 | 24 / 30.1 | 1.47 | 1.42 | 62/34/4/0% | 35 |
| monolith | opp27 | small | 457 | 28.6 | 20 / 25.8 | 1.83 | 1.71 | 52/32/11/5% | 31 |
| monolith | opp26 | small | 358 | 27.5 | 21 / 34.1 | 1.72 | 1.57 | 59/31/6/4% | 32 |
| packs | us27 | small | 364 | 16.5 | 23 / 29.5 | 2.00 | 1.91 | 30/51/15/3% | 45 |
| packs | us26 | small | 363 | 17.3 | 23 / 31.3 | 1.94 | 1.85 | 31/52/17/0% | 45 |
| packs | opp27 | small | 438 | 19.9 | 21 / 28.8 | 1.97 | 1.77 | 44/38/15/3% | 44 |
| packs | opp26 | small | 386 | 18.4 | 20 / 27.5 | 1.92 | 1.72 | 49/33/15/3% | 44 |
| rows | us27 | big | 293 | 17.2 | 18 / 18.5 | 3.16 | 3.10 | 6/20/31/42% | 63 |
| rows | us26 | big | 270 | 15.0 | 21 / 25.5 | 2.70 | 2.61 | 7/25/68/0% | 64 |
| rows | opp27 | big | 247 | 14.5 | 20 / 25.5 | 3.00 | 2.83 | 12/24/40/24% | 65 |
| rows | opp26 | big | 269 | 14.9 | 20 / 26.6 | 2.90 | 2.78 | 12/27/39/22% | 64 |

| map | who | class | group-rounds | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|---|---|
| ALL | us27 | big | 4668 | 28% | 33% | 22% | 15% |
| ALL | us26 | big | 5039 | 30% | 48% | 21% | 0% |
| ALL | opp27 | big | 5752 | 47% | 28% | 17% | 5% |
| ALL | opp26 | big | 5909 | 45% | 30% | 18% | 5% |
| ALL | us27 | small | 50031 | 82% | 15% | 1% | 0% |
| ALL | us26 | small | 49227 | 81% | 16% | 1% | 0% |
| ALL | opp27 | small | 48653 | 81% | 14% | 3% | 0% |
| ALL | opp26 | small | 47505 | 81% | 14% | 3% | 1% |
| collision | us27 | big | 65 | 93% | 6% | 0% | 0% |
| collision | us26 | big | 19 | 100% | 0% | 0% | 0% |
| collision | opp27 | big | 764 | 86% | 13% | 0% | 0% |
| collision | opp26 | big | 596 | 95% | 3% | 0% | 0% |
| collision | us27 | small | 6863 | 89% | 10% | 0% | 0% |
| collision | us26 | small | 7100 | 89% | 9% | 0% | 0% |
| collision | opp27 | small | 6484 | 88% | 8% | 1% | 0% |
| collision | opp26 | small | 6425 | 84% | 12% | 2% | 0% |
| expanse | us27 | big | 550 | 81% | 15% | 3% | 0% |
| expanse | us26 | big | 338 | 100% | 0% | 0% | 0% |
| expanse | opp27 | big | 271 | 100% | 0% | 0% | 0% |
| expanse | opp26 | big | 346 | 99% | 0% | 0% | 0% |
| expanse | us27 | small | 6864 | 98% | 1% | 0% | 0% |
| expanse | us26 | small | 7085 | 97% | 2% | 0% | 0% |
| expanse | opp27 | small | 6465 | 88% | 10% | 0% | 0% |
| expanse | opp26 | small | 6499 | 92% | 6% | 0% | 0% |
| rows | us27 | big | 4053 | 20% | 36% | 25% | 17% |
| rows | us26 | big | 4682 | 25% | 51% | 22% | 0% |
| rows | opp27 | big | 4536 | 36% | 33% | 22% | 7% |
| rows | opp26 | big | 4893 | 34% | 35% | 22% | 6% |
| rows | opp26 | small | 40 | 100% | 0% | 0% | 0% |

Reading: the rule is visible only on rows (4 concurrent hitters in 42% of captures, group-rounds with 4 hitters 17%) and expanse (big groups: 2 hitters in 74% of 19 captures, 1.1 per game; small groups still 95% single-hitter) and twice on collision. On lanes/packs/monolith/interlock/elkring the "one on smaller camps" half left the numbers where they were (lanes 1.17 hitters vs 1.25; packs 2.00 vs 1.94; monolith 1.43 vs 1.47). Rows capture→tribute delay 17 rounds median (21). Expanse: our respawn→capture latency went up (52 vs 47 median; the pair that walks to a 3900 group leaves its 1000-hp cluster for longer) and captures/game down 23.9 vs 24.9, gpr 256 vs 270 (z=-1.4, not significant on 17 games; result 10-7 vs 11-6).

## 9. Lanes allocation (Q8)

| who | phase | top our/mid/their | mid-lane our/mid/their | bottom our/mid/their |
|---|---|---|---|---|
| us27 | 1-99 | 21/0/0 | 45/0/0 | 32/0/2 |
| us26 | 1-99 | 20/0/0 | 45/0/0 | 33/0/2 |
| opp27 | 1-99 | 47/0/9 | 36/0/2 | 5/0/2 |
| opp26 | 1-99 | 46/0/5 | 38/0/4 | 6/0/1 |
| us27 | 100-249 | 22/0/0 | 52/0/0 | 24/0/1 |
| us26 | 100-249 | 23/0/0 | 51/0/0 | 23/0/2 |
| opp27 | 100-249 | 36/0/14 | 33/0/12 | 4/0/1 |
| opp26 | 100-249 | 39/0/12 | 34/0/9 | 6/0/1 |
| us27 | 250-350 | 26/0/0 | 45/0/1 | 26/0/2 |
| us26 | 250-350 | 30/0/0 | 50/0/1 | 18/0/1 |
| opp27 | 250-350 | 41/0/15 | 32/0/11 | 1/0/1 |
| opp26 | 250-350 | 43/0/10 | 36/0/5 | 5/0/1 |

| invaders in lane | batch | rounds | mean ours in lane | ours < invaders | ours = 0 |
|---|---|---|---|---|---|
| 1 | 27 | 1391 | 1.18 | 29% | 29% |
| 1 | 26 | 1597 | 1.36 | 28% | 28% |
| 2 | 27 | 695 | 1.00 | 71% | 44% |
| 2 | 26 | 580 | 1.33 | 57% | 33% |
| 3 | 27 | 362 | 0.93 | 91% | 44% |
| 3 | 26 | 199 | 1.22 | 78% | 40% |
| 4 | 27 | 180 | 1.34 | 91% | 32% |
| 4 | 26 | 92 | 0.85 | 100% | 54% |
| 5 | 27 | 26 | 1.81 | 100% | 0% |
| 5 | 26 | 5 | 3.00 | 100% | 0% |


## 10. What changed with study27 and what did not

1. Changed: on rows we clear with 4 (42% of captures), capture 17.4 packs/game instead of 15.8, idle next to a living pack 3.9 instead of 6.1 times a game, and reach the 16th capture at r365 instead of r375-or-never. Not changed: 3-14, because the opponent tributes 1056 at r366-r398 while we hold 99-165 gems (half-bags from the r239 split carried 126 rounds, shopping at spawn with 99 at r380).
2. Changed: on expanse two champions go to the 3900-hp groups (74% of those captures) and our depth rose 2 tiles; captures/game 23.9 vs 24.9 — slightly slower, not significant (10-7 vs 11-6).
3. Not changed anywhere: territory (85/13/1), invasions (3.0/game, 84% chases), formation (melee front 44%, gap +0.2), action mix, idle share (9%), reaction to invaders (fight 10%), deaths per game (5.8) and the way we die (outnumbered on corners 57%, in pairs on packs).
4. Lanes: nothing of ours moved except alone share (30 vs 26%); the opponents in this batch squatted harder (19% of their rounds in our half, 94 of our groups taken vs 64, ≥3-invader lane-rounds 568 vs 296) and our capture count dropped to 32.8 from 37.9. 3-14 both times.
5. Packs: the opponents die less (2.4 vs 3.8 per game) and take our own-half packs earlier (r289 vs r426 median, 16 of 22 games); our Cassi+Issac pair still dies together (5 times in `20ecdfaf`). 6-16 vs 7-14.
6. Monolith: 4.4 captures/game behind in both batches (their 36-round vs our 49-round respawn→capture; they stack 3+ on 2700-hp wolf pairs 21% of the time, we 4% — below our 3000 threshold); Issac still idles at (5,21) from r115. 5-11 vs 5-8.
7. Collision 8-11 (12-7) and corners 8-11 (5-12) swapped with identical positional numbers; both are decided by the first fight (lose more before r100 → 1 of 7 and 0 of 10 wins) and the draw of those fights.
8. Mid-camp balance still predicts the result (≤-6: 7% wins, ≥6: 89%); the opponents' captures in our half rose from 166 to 200 (lanes 94, packs 30) and ours in theirs stayed at 47.
9. The opening is still a script (rows/lanes/monolith 1-4 patterns at r40 vs 16-19 for the opponents); the stacking added a second variant, not reactivity.
10. Net: study27 changed the clearing speed on the two maps with ≥3000-hp groups and nothing about positions, defence or the end-game; the maps that cost the most games (lanes, packs, corners/collision fights, monolith's one-per-camp latency, rows' last two bags) are exactly where it could not act.

Appendix: full merged tables in `$S/ws3/pos_out/cmp_tables.md` (also 1b/1d per map, 3a per type, 4a per map), per-game comparison `cmp_games.md`, raw study27 outputs `q1_territory.out` … `q15_rows_end.out`, traces of the 8 example games in `traces/`.
