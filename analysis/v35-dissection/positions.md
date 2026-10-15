# Positions and map control: Live Love Larp v35 vs the top 30 (150 games, 2026-10-15 11:33 UTC)

Sample: 150 online games of v35 (we are team A / side a in 145, side b in 5 — the loader uses `rec['side']`), 59 wins / 91 losses; 50 games vs rank 1-10 (10-40), 100 vs rank 11-30 (49-51). Per map: packs 21 (7-14), collision 19 (12-7), rows 18 (4-14), lanes 18 (3-15), corners 17 (5-12), expanse 17 (11-6), elkring 14 (5-9), interlock 13 (7-6), monolith 13 (5-8). Every number below is counted over the full 150 games unless a smaller sample is stated.

Scripts: `$S/ws2/scripts_positions/` (`common.py` loader; `q1_territory.py` … `q12_rowsgroups.py`, `trace.py <match-prefix> [step] [r0 r1]`; raw outputs `q*.out`, example traces in `traces/`). Definitions:
- **Territory** of a tile = BFS walking distance (8-dir, walls and holes block) to own spawn vs enemy spawn: `own` if closer to us by >3 steps, `enemy` if closer to them by >3, `mid` otherwise (same as the Mite/Univardisty study). Camp groups are classified by their tile. "At spawn" = within 2 of a spawn tile; "near altar/camp" = within 2 of an altar / a living camp monster.
- **Action label per champion-round** (priority order): tribute (k12 start, channel rounds, k18 done), recall (k11 start + the rounds until the jump), cast@champ (spell that damaged an enemy champion), attack champ, dash, cast@camp, attack camp, ability(no effect), move, buy, nothing (alive, no action step at all). k3 at phase 13 is end-turn hp regen, not an action.
- **Classes**: melee = Varg Ryth Issac Vendetta Marcella Ren; caster = Stellar Prism Cassi Tavi; ranged = Vesper/Willow (only opponents draft them).

## 0. Headline findings

1. **We are a home-half farm bot with a fixed opening.** Our champion-rounds are 85-90% in our own half for the first 350 rounds and still 75% after r450; the enemy half is 0-2% in every bin. The opponents (18-30 different bots) are 80% / 13% / 6-8% (own/mid/enemy) by r50-100 and 64/25/11 late. We cross into the enemy half 2.9 times per game (episodes of one champion, median 6 rounds, 78% with an enemy already within 8 = chases); they cross 11.9 times (median 8 rounds, 19% hit a camp there, 10% capture there).
2. **Our positions do not change between wins and losses.** Per-map own/mid/enemy, pairwise distance, alone share, idle share, camp-attacking share are the same in our wins and our losses (e.g. lanes own 92/94%, pd 13.3/12.7, idle 14/14; packs 75/81, pd 8.7/8.0). What changes is (a) our deaths (corners 6.6 vs 16.4 per game, packs 3.6 vs 8.7, elkring 2.2 vs 8.9, collision 7.6 vs 17.7) and (b) the opponent's enemy-half share (corners opp 3.8% in our wins vs 16.5% in our losses; interlock 3.3 vs 12.0; packs 6.9 vs 9.4). The winners come to us; we never go to them.
3. **The opening is deterministic.** On lanes, monolith and rows our 5-6 champions are on exactly the same tiles at r10/20/30/40 in all 18/13/18 games; elkring/expanse/interlock 2 patterns (side mirror). The opponents show 13-21 distinct patterns (one per opponent). Anyone with replays can pre-plan against our first 40 rounds.
4. **Contact numbers.** With an enemy within 8 we are outnumbered 14% of the time (them 15%), but 31% of our deaths happen outnumbered and on corners 56% (opp 24%). Our deaths are in our own half 76% of the time (theirs 39%), next to a living camp 24%, with an ally within 6 in 67% of the cases: we die in groups, at home, in the centre fight of corners/collision/packs. Deaths before r100 decide games: when we lose more champions than the opponent before r100 we win 26% (n=38), when fewer 56% (n=23); on lanes 0% (n=6), on packs 16% (n=6), on corners 22% (n=9).
5. **Formation.** Mean pairwise distance 10.6 (opp 11.5); largest cluster within 3 tiles = 2.0 champions = 48% of the team (opp 2.1 / 47%); 29% of champion-rounds with no ally within 6 (opp 32%). Our casters are NOT behind: with casters and melee both engaged, the melee is strictly nearer the enemy only 44% of rounds, the caster is in front 38% (opp 50% / 32%); the caster-melee gap is +0.23 tiles (opp +0.54; Mite +1.35 in the top-2 study). Casters stand at 5.4 tiles (median 5) from the nearest enemy, melee at 5.3: everybody at the same distance.
6. **What we do per round** (308,639 alive champion-rounds): move 50%, attack camp 19%, cast@camp 3%, tribute 6%, recall 6%, nothing 9%, attack/cast at champions 2%, dash 3%. Opponents: move 49, camp 21, tribute 7, recall 8, nothing 10, fight 2. We are dead 13% of champion-rounds (opp 9%); 17% in losses.
7. **Idle.** 9% of our alive rounds are "nothing"; 54% of those are in our own half away from spawn/altar/camp, 18% next to a living camp, 13% at an altar, 7% at spawn, and 40% with an enemy within 8 (opp 24%). On farm maps we stand idle for 5+ rounds within 6 tiles of a living own-half camp 6.1 times per game on rows (opp 1.3), 35 on lanes (opp 32), 5.6 on elkring (opp 9.4); on rows those streaks last 10.7 rounds and end with the champion attacking that camp only 64% of the time.
8. **Camps.** Captures by group territory (own/mid/enemy): us 3002/622/52, opp 3221/616/166. The opponent captured a group in our half in 64 games (42%; lanes 77%, elkring 78%, monolith 84%, packs 61%), first at median r214; we did it in fewer and later (52 captures total). Mid-camp balance decides: (us mid caps − opp mid caps) ≤ −6 → 0% wins (n=18); −5..−1 → 19% (n=26); 0 → 38% (n=63); 1..5 → 59% (n=27); ≥ 6 → 87% (n=16).
9. **Rows is lost on cycle speed, not on fights** (0-2 deaths a game): our nearest wolf pack (18,3) is recaptured 32 rounds after respawn (median; opp 23 on its mirror), the far pack (42,3) 31 (mean 69, max 244: `604a6cf6` alive and untouched r181-r425). Our 3-champion clearing is as fast as theirs (21 vs 20 rounds) and our capture→tribute delay is shorter (21 vs 23); we simply leave packs standing. 14 of 14 losses end 1056 for the opponent (16 captures) vs 726-957 for us with 66-198 gems still carried.


## 1. Where our champions stand over the game (Q1)

### 1a. Own / middle / enemy share of alive champion-rounds, 50-round bins (150 games; opp = the opponent in the same games)

| split | who | games | 0-49 | 50-99 | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 | 400-449 | 450+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 150 | 90/10/0 | 85/14/1 | 87/12/1 | 86/13/1 | 88/11/1 | 86/12/1 | 86/13/1 | 83/16/1 | 80/18/2 | 75/23/2 |
| ALL | opp | 150 | 94/5/1 | 80/13/6 | 79/13/8 | 78/14/8 | 79/13/8 | 79/14/7 | 78/14/8 | 72/17/11 | 69/20/11 | 64/25/11 |
| map:collision | us | 19 | 58/42/0 | 79/20/1 | 67/33/0 | 62/38/0 | 73/26/1 | 67/31/1 | 66/33/0 | 65/35/0 | 65/34/1 | 68/32/0 |
| map:collision | opp | 19 | 93/6/1 | 73/23/5 | 73/23/4 | 76/21/3 | 66/27/7 | 69/26/5 | 68/25/6 | 64/24/13 | 70/22/8 | 66/29/5 |
| map:corners | us | 17 | 79/20/1 | 81/15/4 | 76/22/3 | 80/19/1 | 84/15/1 | 81/17/2 | 77/20/3 | 79/19/3 | 78/20/2 | 85/13/2 |
| map:corners | opp | 17 | 82/14/4 | 72/20/8 | 64/24/12 | 61/26/12 | 62/25/13 | 61/25/14 | 66/24/11 | 58/23/19 | 59/26/15 | 54/26/19 |
| map:elkring | us | 14 | 97/3/0 | 79/20/1 | 88/12/1 | 82/15/2 | 81/16/3 | 76/19/5 | 77/20/4 | 77/21/2 | 75/21/4 | 77/19/4 |
| map:elkring | opp | 14 | 95/4/0 | 79/12/9 | 77/18/5 | 79/13/8 | 74/19/8 | 76/15/8 | 76/17/7 | 71/17/12 | 72/19/8 | 69/19/12 |
| map:expanse | us | 17 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | - | - |
| map:expanse | opp | 17 | 100/0/0 | 99/0/1 | 99/0/1 | 99/0/1 | 99/0/1 | 99/0/1 | 99/1/0 | 98/2/0 | - | - |
| map:interlock | us | 13 | 97/2/1 | 90/10/1 | 89/10/1 | 88/11/1 | 95/5/0 | 94/5/0 | 91/9/0 | 86/13/1 | 86/13/1 | 79/16/5 |
| map:interlock | opp | 13 | 90/6/3 | 76/14/10 | 80/13/7 | 80/11/9 | 84/10/6 | 81/15/5 | 79/12/8 | 79/14/8 | 80/10/10 | 77/12/11 |
| map:lanes | us | 18 | 100/0/0 | 85/14/0 | 94/5/1 | 93/6/1 | 94/5/2 | 95/5/0 | 92/6/1 | 95/4/0 | 94/4/2 | 96/4/0 |
| map:lanes | opp | 18 | 99/1/0 | 73/14/12 | 75/8/17 | 67/12/20 | 77/8/15 | 81/11/9 | 78/10/12 | 74/12/14 | 72/12/17 | 76/14/10 |
| map:monolith | us | 13 | 100/0/0 | 65/33/2 | 87/10/2 | 83/17/0 | 80/19/1 | 74/23/3 | 82/17/1 | 75/21/3 | 86/13/2 | 76/18/6 |
| map:monolith | opp | 13 | 99/1/0 | 87/10/3 | 84/10/6 | 83/12/5 | 78/12/10 | 79/13/8 | 71/15/14 | 70/19/11 | 69/14/16 | 62/19/19 |
| map:packs | us | 21 | 73/27/0 | 82/18/0 | 78/22/0 | 79/19/2 | 79/20/1 | 79/20/1 | 79/20/1 | 79/20/1 | 79/20/1 | 79/21/1 |
| map:packs | opp | 21 | 85/11/5 | 67/25/8 | 66/25/9 | 60/29/11 | 66/25/9 | 69/22/9 | 66/27/8 | 64/25/12 | 58/32/10 | 65/24/11 |
| map:rows | us | 18 | 100/0/0 | 100/0/0 | 100/0/0 | 99/0/1 | 98/0/2 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 | 100/0/0 |
| map:rows | opp | 18 | 100/0/0 | 99/0/0 | 98/0/2 | 100/0/0 | 99/0/0 | 96/0/4 | 98/0/2 | 99/0/1 | 98/0/2 | 80/0/20 |
| opp:r11-30 | us | 100 | 90/9/0 | 84/14/1 | 88/11/1 | 86/13/1 | 87/11/1 | 86/13/1 | 87/12/1 | 83/16/1 | 79/19/2 | 75/23/2 |
| opp:r11-30 | opp | 100 | 94/4/2 | 81/12/7 | 79/12/8 | 78/13/8 | 80/12/8 | 81/12/7 | 78/14/8 | 74/15/11 | 72/17/11 | 64/24/11 |
| opp:top10 | us | 50 | 88/12/0 | 86/14/0 | 86/13/1 | 86/13/0 | 88/11/1 | 88/11/1 | 85/14/1 | 82/17/1 | 83/16/1 | 76/22/1 |
| opp:top10 | opp | 50 | 93/6/1 | 79/16/5 | 79/15/6 | 77/15/8 | 76/17/7 | 76/16/8 | 78/15/7 | 69/19/12 | 63/26/11 | 62/27/11 |
| res:loss | us | 91 | 91/9/0 | 85/14/1 | 88/10/1 | 88/11/1 | 89/10/1 | 89/10/1 | 88/11/1 | 86/12/1 | 84/15/1 | 82/17/2 |
| res:loss | opp | 91 | 93/5/2 | 77/14/8 | 78/13/10 | 75/14/10 | 75/14/10 | 77/14/9 | 76/15/9 | 70/17/12 | 63/23/14 | 57/27/16 |
| res:win | us | 59 | 87/13/0 | 85/14/1 | 85/14/1 | 83/15/1 | 86/13/1 | 82/16/1 | 83/16/2 | 77/21/1 | 76/22/2 | 69/29/2 |
| res:win | opp | 59 | 95/4/1 | 86/11/3 | 82/14/4 | 83/13/4 | 84/12/4 | 83/13/4 | 83/13/5 | 76/15/9 | 80/14/6 | 72/23/5 |

Reading: the "us" row barely moves (90/10/0 → 75/23/2); the "opp" row leaves home by r50 (80/13/6) and keeps 8-11% in our half. Per map: on corners the opponent is 14-26% in our half from r100 on while we are 1-4% in theirs; on lanes the opponent is 12-20% in our half from r50 (their raids of our top-lane gem clusters, see §5.1) while we are ≤2% in theirs; on monolith they reach 13-19% late; on collision/packs both sides contest the middle (we 26-38% mid, they 21-30%) but they also take 5-13% in our half; expanse/rows: 100/0/0 both. Top-10 vs 11-30 opponents are the same picture for us (the top-10 are slightly deeper in our half late: 11-12% vs 11%). In our losses the opponent is in our half 8-16% from r50 to the end; in our wins 3-9%.

### 1b. Other locations (% of alive champion-rounds): at spawn / idle at spawn / near altar / near a living camp / doing nothing

| split | who | 0-49 | 50-99 | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 | 400-449 | 450+ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 18/2/10/31/8 | 10/1/14/28/8 | 11/1/16/24/10 | 11/1/16/26/9 | 12/1/15/24/10 | 11/1/17/21/9 | 11/1/17/24/9 | 12/1/17/22/10 | 14/2/17/21/10 | 16/2/17/29/11 |
| ALL | opp | 19/1/11/26/8 | 9/1/15/25/10 | 10/1/17/25/10 | 10/1/17/24/11 | 9/1/19/23/10 | 9/1/18/22/12 | 9/1/19/22/12 | 10/1/19/20/11 | 11/1/21/19/10 | 13/1/22/28/10 |
| map:collision | us | 12/0/10/61/9 | 16/1/10/68/10 | 12/1/17/62/11 | 12/1/21/64/12 | 16/1/15/59/10 | 14/2/19/60/12 | 13/1/21/63/12 | 13/2/21/60/13 | 14/1/18/56/13 | 15/2/19/54/13 |
| map:collision | opp | 23/0/2/57/8 | 16/1/11/44/10 | 15/1/11/51/8 | 15/1/9/45/8 | 16/1/16/46/9 | 13/1/14/45/10 | 13/1/16/49/10 | 15/1/12/50/10 | 14/1/13/46/11 | 14/2/18/47/10 |
| map:corners | us | 16/4/31/19/16 | 16/1/19/10/8 | 10/1/29/16/11 | 12/1/29/16/9 | 14/1/24/13/8 | 11/1/24/14/9 | 11/1/31/15/10 | 14/1/23/10/8 | 11/1/26/15/10 | 15/1/19/11/8 |
| map:corners | opp | 15/1/17/20/9 | 9/1/25/14/10 | 8/1/28/19/10 | 8/1/35/19/11 | 7/1/33/17/11 | 8/1/35/19/11 | 8/1/28/18/10 | 9/1/30/15/11 | 7/1/33/15/10 | 8/1/34/17/10 |
| map:elkring | us | 45/2/0/25/3 | 15/1/12/15/6 | 29/2/6/20/7 | 21/2/10/10/9 | 23/3/6/13/6 | 24/4/10/15/10 | 21/2/12/10/7 | 19/3/10/10/10 | 22/4/11/9/10 | 19/2/9/9/9 |
| map:elkring | opp | 38/3/4/30/8 | 18/2/9/20/9 | 19/2/13/20/8 | 22/4/9/21/11 | 16/2/13/21/8 | 17/2/10/19/10 | 19/3/12/15/11 | 15/2/8/17/9 | 15/2/13/15/9 | 16/2/12/16/10 |
| map:expanse | us | 20/5/6/33/11 | 8/1/20/36/4 | 7/1/17/17/10 | 17/2/17/29/3 | 8/0/18/29/8 | 9/0/18/9/3 | 9/1/17/26/9 | 1/0/42/12/6 | - | - |
| map:expanse | opp | 19/1/6/26/9 | 7/1/18/23/12 | 7/0/13/25/13 | 8/1/15/24/11 | 6/0/20/20/11 | 6/0/14/24/14 | 8/1/21/19/16 | 13/2/17/13/20 | - | - |
| map:interlock | us | 19/1/4/24/6 | 7/1/16/10/8 | 8/1/15/7/10 | 8/1/15/14/9 | 12/1/14/10/7 | 10/1/16/11/8 | 11/1/14/12/10 | 8/1/14/11/9 | 10/1/16/11/9 | 12/2/18/12/9 |
| map:interlock | opp | 17/1/10/20/11 | 6/1/22/16/11 | 10/1/20/16/10 | 6/0/17/13/14 | 9/1/25/11/11 | 9/1/23/13/15 | 8/1/22/18/12 | 9/1/21/12/12 | 9/1/24/10/12 | 8/1/26/8/12 |
| map:lanes | us | 13/4/18/22/12 | 1/0/13/51/15 | 7/1/21/35/11 | 5/1/19/36/14 | 5/1/21/36/15 | 6/1/22/28/15 | 4/0/19/35/15 | 7/1/20/32/15 | 7/1/23/24/15 | 8/1/23/27/15 |
| map:lanes | opp | 8/1/30/19/9 | 2/0/15/43/10 | 2/0/23/34/13 | 2/0/19/39/14 | 3/1/22/33/12 | 3/0/19/34/13 | 2/0/22/34/14 | 3/1/22/30/14 | 3/0/24/27/11 | 1/0/22/47/12 |
| map:monolith | us | 13/3/0/34/5 | 5/1/19/13/4 | 7/1/7/18/9 | 6/1/13/23/4 | 6/1/13/18/5 | 5/1/18/20/4 | 6/1/12/18/5 | 7/1/17/18/5 | 8/1/11/17/6 | 11/1/21/17/7 |
| map:monolith | opp | 12/1/1/26/9 | 7/1/10/20/8 | 5/1/10/21/10 | 6/1/12/21/9 | 5/1/11/21/9 | 6/1/13/17/9 | 5/1/15/18/10 | 4/1/17/18/9 | 6/1/15/16/10 | 3/1/19/21/7 |
| map:packs | us | 12/0/13/30/9 | 16/1/13/19/9 | 16/2/15/19/10 | 19/2/16/19/7 | 18/2/17/17/11 | 18/1/16/19/9 | 17/2/18/18/9 | 19/2/20/17/10 | 23/2/22/12/9 | 18/2/19/16/10 |
| map:packs | opp | 27/1/19/18/6 | 15/1/20/21/10 | 18/2/21/16/9 | 20/2/20/17/10 | 21/1/19/16/8 | 19/1/21/14/10 | 19/2/20/17/10 | 17/1/24/13/9 | 20/1/25/13/10 | 20/1/24/12/10 |
| map:rows | us | 15/0/1/36/3 | 10/0/8/21/5 | 8/1/10/18/13 | 8/0/8/21/9 | 7/0/7/22/18 | 8/0/8/18/11 | 11/1/12/17/7 | 6/1/9/20/7 | 8/0/8/12/6 | 20/20/20/0/80 |
| map:rows | opp | 13/1/2/27/3 | 7/1/5/22/10 | 8/1/9/20/9 | 7/1/10/20/10 | 6/1/10/19/12 | 7/1/11/15/13 | 7/1/12/14/13 | 7/1/13/11/13 | 5/0/15/11/12 | 20/20/20/20/80 |
| opp:r11-30 | us | 18/2/10/31/8 | 10/1/15/28/8 | 11/1/16/23/10 | 11/1/16/26/8 | 11/1/15/25/10 | 11/1/18/22/9 | 10/1/17/23/10 | 12/1/17/22/9 | 13/1/19/20/10 | 15/2/18/28/11 |
| opp:r11-30 | opp | 19/1/11/26/9 | 9/1/14/25/10 | 10/1/16/24/10 | 10/1/16/24/12 | 10/1/17/23/10 | 9/1/16/22/12 | 9/1/18/22/13 | 10/1/17/20/12 | 11/1/19/20/11 | 13/2/22/26/10 |
| opp:top10 | us | 17/2/9/32/8 | 10/1/12/28/9 | 12/1/15/26/11 | 12/1/16/27/10 | 12/1/14/23/10 | 13/1/14/21/9 | 12/1/17/25/9 | 11/1/16/23/10 | 18/2/13/23/11 | 18/2/14/33/11 |
| opp:top10 | opp | 19/1/12/28/6 | 9/1/17/26/9 | 10/1/19/26/9 | 10/1/18/25/10 | 9/1/22/21/10 | 9/1/22/23/12 | 10/1/20/22/10 | 9/1/22/20/9 | 11/1/24/17/9 | 13/1/22/32/10 |
| res:loss | us | 17/2/10/30/8 | 10/1/14/27/9 | 12/1/15/23/10 | 11/1/15/24/9 | 12/1/14/23/11 | 12/1/15/20/10 | 11/1/15/23/10 | 12/1/15/20/10 | 16/2/15/18/10 | 19/2/13/22/10 |
| res:loss | opp | 18/1/13/25/8 | 9/1/16/25/9 | 9/1/17/25/10 | 9/1/18/24/11 | 9/1/20/23/10 | 9/1/19/22/12 | 9/1/20/22/11 | 10/1/21/19/11 | 10/1/23/18/10 | 12/1/25/24/10 |
| res:win | us | 18/2/9/34/8 | 10/1/15/30/7 | 10/1/16/25/10 | 12/1/17/28/8 | 11/1/16/27/9 | 11/1/19/23/8 | 10/1/20/25/9 | 11/1/20/25/9 | 12/1/19/23/9 | 13/2/20/36/11 |
| res:win | opp | 19/1/9/29/8 | 10/1/13/26/11 | 10/1/17/24/10 | 12/1/14/25/11 | 10/1/16/23/10 | 10/1/16/23/12 | 10/1/16/23/14 | 10/1/15/22/11 | 13/1/17/21/11 | 13/2/17/32/11 |

Reading: we spend 10-18% of champion-rounds within 2 tiles of our spawn (recalls, shopping, respawns), but idle-at-spawn is only 1-2% (we leave spawn immediately). We stand next to a living camp 21-31% of the time (opp 19-28%) and near an altar 10-17% (opp 11-22%). Per map the big numbers: collision 54-68% next to a camp (the central wolves), corners 17-30% at the centre altar (opp 27-40%), elkring 19-45% at spawn (opp 15-38%). "Nothing" is 8-11% for both sides in every bin.

### 1c. Enemy-half episodes (one champion crossing into enemy territory until it leaves or dies)

| split | who | games | episodes | per game | median len | median start r | hits camp there | hits enemy there | gets hit there | captures there | tributes there | ends dead | median score diff at entry | nearest enemy <=8 at entry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 150 | 437 | 2.9 | 6 | 283 | 13% | 44% | 34% | 16% | 3% | 5% | +22 | 78% |
| ALL | opp | 150 | 1788 | 11.9 | 8 | 297 | 19% | 53% | 51% | 10% | 7% | 8% | +23 | 85% |
| map:collision | us | 19 | 33 | 1.7 | 5 | 286 | 0% | 69% | 51% | 3% | 0% | 15% | +22 | 100% |
| map:collision | opp | 19 | 217 | 11.4 | 7 | 356 | 17% | 58% | 58% | 6% | 0% | 7% | +22 | 92% |
| map:corners | us | 17 | 121 | 7.1 | 4 | 271 | 14% | 48% | 37% | 13% | 11% | 4% | +150 | 88% |
| map:corners | opp | 17 | 580 | 34.1 | 8 | 304 | 19% | 59% | 59% | 4% | 5% | 5% | +48 | 90% |
| map:elkring | us | 14 | 108 | 7.7 | 10 | 323 | 18% | 43% | 27% | 15% | 0% | 2% | -36 | 76% |
| map:elkring | opp | 14 | 242 | 17.3 | 10 | 354 | 30% | 45% | 49% | 15% | 5% | 16% | +54 | 72% |
| map:expanse | us | 17 | 0 |
| map:expanse | opp | 17 | 1 | 0.1 | 227 | 47 | 100% | 100% | 100% | 100% | 100% | 100% | -48 | 0% |
| map:interlock | us | 13 | 35 | 2.7 | 5 | 209 | 2% | 77% | 54% | 2% | 0% | 5% | +88 | 94% |
| map:interlock | opp | 13 | 175 | 13.5 | 7 | 245 | 10% | 46% | 43% | 3% | 9% | 7% | -22 | 91% |
| map:lanes | us | 18 | 36 | 2.0 | 6 | 202 | 19% | 19% | 27% | 38% | 0% | 8% | -14 | 58% |
| map:lanes | opp | 18 | 238 | 13.2 | 6 | 220 | 21% | 40% | 33% | 23% | 13% | 5% | +0 | 88% |
| map:monolith | us | 13 | 61 | 4.7 | 7 | 283 | 6% | 22% | 22% | 26% | 4% | 4% | +38 | 57% |
| map:monolith | opp | 13 | 101 | 7.8 | 18 | 321 | 23% | 51% | 39% | 20% | 8% | 12% | -30 | 63% |
| map:packs | us | 21 | 40 | 1.9 | 4 | 344 | 17% | 40% | 37% | 17% | 0% | 2% | +0 | 75% |
| map:packs | opp | 21 | 229 | 10.9 | 11 | 284 | 14% | 55% | 55% | 10% | 15% | 13% | +40 | 85% |
| map:rows | us | 18 | 3 | 0.2 | 33 | 190 | 0% | 0% | 0% | 0% | 0% | 0% | -66 | 0% |
| map:rows | opp | 18 | 5 | 0.3 | 69 | 241 | 0% | 100% | 100% | 0% | 40% | 80% | +66 | 20% |
| opp:r11-30 | us | 100 | 325 | 3.2 | 6 | 281 | 13% | 45% | 34% | 17% | 3% | 4% | +60 | 78% |
| opp:r11-30 | opp | 100 | 1206 | 12.1 | 8 | 313 | 18% | 49% | 50% | 11% | 8% | 9% | +0 | 83% |
| opp:top10 | us | 50 | 112 | 2.2 | 5 | 290 | 10% | 40% | 34% | 14% | 5% | 5% | -36 | 78% |
| opp:top10 | opp | 50 | 582 | 11.6 | 8 | 263 | 20% | 60% | 53% | 7% | 7% | 7% | +138 | 89% |
| res:loss | us | 91 | 240 | 2.6 | 5 | 284 | 12% | 40% | 35% | 15% | 5% | 7% | -22 | 80% |
| res:loss | opp | 91 | 1289 | 14.2 | 9 | 292 | 23% | 55% | 52% | 11% | 9% | 6% | +72 | 84% |
| res:win | us | 59 | 197 | 3.3 | 6 | 276 | 13% | 48% | 33% | 18% | 2% | 2% | +96 | 75% |
| res:win | opp | 59 | 499 | 8.5 | 6 | 318 | 10% | 46% | 47% | 8% | 4% | 14% | -106 | 88% |

Reading: **we do not invade**: 2.9 episodes/game (lanes 2.0, rows 0.2, expanse 0), median 6 rounds, 78% begin with an enemy within 8 (a chase or a fight that crossed the line), 13% touch a camp, 16% capture there (lanes 38%, monolith 29%: these are the few raids, typically Varg/Ryth on an enemy elk or gem cluster while the lane is empty). The opponents cross 11.9 times/game (corners 32.7, elkring 17.3, lanes 13.2, interlock 13.2, collision 11.4, packs 10.1), 19% hit a camp there, 10% capture, 7% even tribute there; 8% end dead. In our losses they cross 14.2 times/game at a median score lead of +72; in our wins 8.5 times at −106 (desperation raids that end dead 14%).

### 1d. When they invade, what are we doing? (rounds with at least one enemy champion standing in our half)

| split | rounds with invader | our champ-rounds | near invader (<=8) | own/mid/enemy where we are | actions (all) | actions when near |
|---|---|---|---|---|---|---|---|
| ALL | 17064 | 64366 | 44% | 88/10/1 | move 53%, attack camp 14%, nothing 10%, recall 7%, tribute 5%, cast@champ 3%, attack champ 2%, dash 2%, cast@camp 2%, buy 1%, ability(no eff) 0%, arrive 0%, attack(miss) 0% | move 52%, nothing 12%, attack camp 9%, recall 7%, cast@champ 5%, attack champ 5%, tribute 4%, dash 3%, cast@camp 2%, ability(no eff) 1%, attack(miss) 0%, buy 0%, arrive 0% |
| map:collision | 1786 | 4140 | 63% | 90/9/0 | move 52%, nothing 13%, attack camp 10%, recall 9%, cast@champ 4%, dash 4%, attack champ 3%, cast@camp 2%, tribute 1%, ability(no eff) 1%, buy 1%, arrive 1%, attack(miss) 0% | move 51%, nothing 15%, recall 8%, attack camp 7%, cast@champ 7%, attack champ 5%, dash 4%, cast@camp 1%, ability(no eff) 1%, tribute 0%, attack(miss) 0% |
| map:corners | 3849 | 12228 | 52% | 91/8/0 | move 62%, nothing 8%, recall 7%, cast@champ 6%, attack camp 5%, attack champ 4%, tribute 4%, dash 2%, cast@camp 2%, arrive 1%, buy 0%, attack(miss) 0%, ability(no eff) 0% | move 53%, nothing 11%, cast@champ 11%, recall 10%, attack champ 6%, tribute 4%, attack camp 2%, dash 2%, cast@camp 1%, attack(miss) 0%, ability(no eff) 0%, buy 0% |
| map:elkring | 2253 | 9160 | 36% | 82/15/2 | move 52%, attack camp 14%, recall 9%, nothing 9%, cast@camp 5%, tribute 4%, cast@champ 3%, dash 2%, attack champ 2%, buy 1%, arrive 1%, attack(miss) 0%, ability(no eff) 0% | move 55%, nothing 11%, recall 9%, attack camp 8%, cast@champ 7%, attack champ 4%, cast@camp 3%, dash 2%, tribute 1%, attack(miss) 0%, ability(no eff) 0%, buy 0% |
| map:expanse | 227 | 908 | 32% | 100/0/0 | move 54%, attack camp 21%, tribute 7%, nothing 7%, recall 6%, dash 3%, ability(no eff) 1%, arrive 1%, cast@camp 1%, buy 1%, attack champ 1% | move 69%, attack camp 8%, nothing 8%, tribute 4%, recall 3%, ability(no eff) 3%, dash 2%, attack champ 2% |
| map:interlock | 1366 | 5455 | 53% | 88/11/0 | move 47%, attack camp 16%, nothing 11%, recall 9%, tribute 5%, cast@camp 4%, dash 3%, cast@champ 3%, attack champ 2%, buy 1%, arrive 0%, ability(no eff) 0%, attack(miss) 0% | move 44%, attack camp 13%, nothing 13%, recall 10%, tribute 6%, attack champ 4%, cast@champ 4%, cast@camp 3%, dash 2%, ability(no eff) 1%, attack(miss) 0% |
| map:lanes | 2780 | 13785 | 39% | 94/4/0 | move 54%, attack camp 16%, nothing 12%, tribute 6%, recall 3%, dash 2%, attack champ 2%, cast@camp 2%, ability(no eff) 1%, cast@champ 0%, buy 0%, arrive 0%, attack(miss) 0% | move 53%, nothing 15%, attack camp 13%, attack champ 5%, tribute 4%, recall 3%, dash 2%, cast@camp 2%, ability(no eff) 2%, cast@champ 1%, attack(miss) 0% |
| map:monolith | 1785 | 9254 | 28% | 82/15/2 | move 58%, attack camp 16%, nothing 6%, recall 6%, tribute 5%, dash 2%, cast@camp 2%, attack champ 2%, buy 1%, ability(no eff) 1%, cast@champ 0%, arrive 0%, attack(miss) 0% | move 67%, attack camp 10%, nothing 8%, attack champ 5%, recall 2%, dash 2%, ability(no eff) 2%, cast@champ 1%, cast@camp 1%, tribute 1%, attack(miss) 0%, buy 0% |
| map:packs | 2558 | 7206 | 55% | 85/13/1 | move 40%, attack camp 18%, nothing 9%, recall 9%, tribute 7%, cast@camp 4%, dash 4%, attack champ 3%, cast@champ 3%, ability(no eff) 1%, buy 1%, arrive 1%, attack(miss) 0% | move 43%, attack camp 12%, nothing 10%, recall 9%, attack champ 6%, tribute 6%, cast@champ 5%, dash 4%, cast@camp 3%, ability(no eff) 1%, attack(miss) 1%, buy 0%, arrive 0% |
| map:rows | 460 | 2230 | 37% | 100/0/0 | move 48%, attack camp 20%, nothing 11%, tribute 10%, recall 5%, dash 2%, cast@camp 2%, attack champ 1%, buy 0%, arrive 0%, ability(no eff) 0%, cast@champ 0%, attack(miss) 0% | move 54%, tribute 22%, attack camp 9%, nothing 7%, attack champ 4%, dash 2%, recall 1%, cast@camp 1%, cast@champ 0%, ability(no eff) 0%, attack(miss) 0% |
| opp:r11-30 | 11807 | 45423 | 44% | 88/10/1 | move 54%, attack camp 14%, nothing 10%, recall 6%, tribute 5%, cast@camp 2%, cast@champ 2%, dash 2%, attack champ 2%, buy 1%, ability(no eff) 1%, arrive 0%, attack(miss) 0% | move 52%, nothing 12%, attack camp 10%, recall 6%, attack champ 5%, cast@champ 5%, tribute 4%, dash 3%, cast@camp 2%, ability(no eff) 1%, attack(miss) 0%, buy 0%, arrive 0% |
| opp:top10 | 5257 | 18943 | 45% | 89/9/0 | move 52%, attack camp 13%, nothing 10%, recall 8%, tribute 5%, cast@champ 3%, attack champ 3%, dash 2%, cast@camp 2%, arrive 1%, buy 1%, ability(no eff) 0%, attack(miss) 0% | move 53%, nothing 12%, recall 9%, attack camp 7%, cast@champ 6%, attack champ 6%, tribute 3%, dash 3%, cast@camp 1%, ability(no eff) 1%, attack(miss) 0%, buy 0%, arrive 0% |
| res:loss | 13110 | 47742 | 45% | 89/9/0 | move 54%, attack camp 13%, nothing 10%, recall 7%, tribute 5%, cast@champ 3%, dash 2%, attack champ 2%, cast@camp 2%, buy 1%, arrive 1%, ability(no eff) 0%, attack(miss) 0% | move 52%, nothing 12%, attack camp 9%, recall 7%, cast@champ 5%, attack champ 5%, tribute 4%, dash 3%, cast@camp 2%, ability(no eff) 1%, attack(miss) 0%, buy 0%, arrive 0% |
| res:win | 3954 | 16624 | 42% | 87/11/1 | move 52%, attack camp 15%, nothing 10%, recall 6%, tribute 5%, attack champ 3%, cast@camp 3%, dash 3%, cast@champ 2%, buy 1%, ability(no eff) 1%, arrive 0%, attack(miss) 0% | move 54%, nothing 11%, attack camp 9%, attack champ 6%, recall 6%, cast@champ 5%, tribute 3%, dash 3%, cast@camp 2%, ability(no eff) 1%, attack(miss) 0%, buy 0% |

Reading: in 17,064 rounds (of ~67,000) an enemy stands in our half. In those rounds 56% of our champion-rounds are more than 8 tiles from any invader; near an invader (44%) we are moving 52%, doing nothing 12%, attacking a camp 9%, recalling 7%, hitting the invader with spells 5% and attacks 5%. So the modal answer to an invader is "walk" (mostly our normal farm path) and the second is "stand". The share of fighting actions near an invader (10%) is the same on every map and against top-10 and 11-30 opponents. On lanes, where the invaders sit on our gem clusters for 100+ rounds, it is 6% (attack 5%, cast 1%); on rows 4%.

Longest enemy stays in our half (from the episode list): Stellar r51-r327 (276 rounds, 65-68 tiles deep, camps + captures, ended dead), Stellar r47-r274, Stellar r80-r292, Issac r78-r283, Cassi r58-r246, Tavi r52-r228 — all lanes/monolith squatters on our clusters. Our longest: Varg r195-249 (54 rounds, enemy elk, captured), Cassi r149-201, Prism r114-149 (died).


## 2. Spread and formation (Q2)

### 2a. Spread (every 2nd round, ≥2 champions alive)

| split | who | rounds | mean pd | median pd | max pd (mean) | largest cluster (mean) | share of team in largest cluster | all together | all apart | alone | alone: melee/caster/ranged | alone & enemy<=8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 35586 | 10.56 | 9.9 | 17.68 | 2.01 | 48% | 7% | 31% | 29% | 33/25/0% | 21% |
| ALL | opp | 36620 | 11.54 | 11.0 | 19.75 | 2.11 | 47% | 6% | 32% | 32% | 36/28/18% | 25% |
| map:collision | us | 6113 | 7.14 | 7.0 | 10.86 | 2.05 | 59% | 16% | 27% | 19% | 21/17/0% | 10% |
| map:collision | opp | 6465 | 9.05 | 8.7 | 13.36 | 1.86 | 55% | 11% | 37% | 29% | 31/27/0% | 23% |
| map:corners | us | 4552 | 8.93 | 8.7 | 13.89 | 2.17 | 57% | 15% | 31% | 28% | 28/27/0% | 13% |
| map:corners | opp | 4698 | 10.52 | 10.3 | 19.64 | 2.72 | 53% | 9% | 15% | 24% | 26/22/19% | 8% |
| map:elkring | us | 4094 | 9.88 | 10.2 | 16.54 | 1.99 | 45% | 3% | 31% | 25% | 28/23/0% | 34% |
| map:elkring | opp | 4115 | 10.47 | 10.8 | 17.97 | 2.38 | 48% | 5% | 22% | 25% | 29/18/20% | 31% |
| map:expanse | us | 2959 | 16.53 | 16.7 | 26.80 | 1.44 | 36% | 4% | 68% | 66% | 66/65/0% | 42% |
| map:expanse | opp | 2959 | 18.19 | 17.3 | 29.89 | 1.35 | 33% | 1% | 72% | 65% | 67/62/0% | 100% |
| map:interlock | us | 3074 | 8.53 | 8.6 | 14.69 | 2.21 | 48% | 4% | 22% | 21% | 25/18/0% | 17% |
| map:interlock | opp | 3090 | 9.36 | 9.2 | 15.40 | 2.03 | 47% | 5% | 32% | 27% | 31/24/0% | 23% |
| map:lanes | us | 3578 | 12.85 | 12.9 | 23.77 | 2.20 | 40% | 4% | 23% | 26% | 31/16/0% | 17% |
| map:lanes | opp | 3578 | 12.50 | 12.2 | 25.01 | 2.49 | 43% | 4% | 20% | 26% | 29/23/17% | 29% |
| map:monolith | us | 2907 | 16.53 | 16.0 | 29.28 | 1.76 | 32% | 0% | 37% | 45% | 46/45/0% | 48% |
| map:monolith | opp | 2907 | 17.33 | 17.7 | 30.54 | 1.81 | 32% | 0% | 41% | 49% | 50/48/57% | 60% |
| map:packs | us | 4698 | 8.26 | 8.2 | 12.26 | 1.74 | 49% | 3% | 40% | 29% | 33/25/0% | 29% |
| map:packs | opp | 5197 | 9.71 | 9.7 | 14.49 | 1.72 | 48% | 5% | 46% | 37% | 42/32/0% | 37% |
| map:rows | us | 3611 | 11.89 | 11.4 | 22.08 | 2.41 | 48% | 2% | 11% | 20% | 21/15/0% | 27% |
| map:rows | opp | 3611 | 11.97 | 12.3 | 22.47 | 2.59 | 52% | 6% | 10% | 24% | 29/16/10% | 87% |
| opp:r11-30 | us | 24478 | 10.77 | 10.1 | 18.11 | 2.01 | 47% | 6% | 31% | 30% | 33/25/0% | 21% |
| opp:r11-30 | opp | 25007 | 11.68 | 11.2 | 20.06 | 2.08 | 47% | 5% | 33% | 33% | 37/29/20% | 26% |
| opp:top10 | us | 11108 | 10.09 | 9.3 | 16.74 | 2.00 | 49% | 7% | 32% | 29% | 32/25/0% | 21% |
| opp:top10 | opp | 11613 | 11.23 | 10.4 | 19.09 | 2.18 | 49% | 7% | 30% | 30% | 34/26/9% | 23% |
| res:loss | us | 20653 | 10.58 | 10.0 | 17.71 | 2.01 | 48% | 7% | 32% | 29% | 31/25/0% | 22% |
| res:loss | opp | 22050 | 11.56 | 11.0 | 20.32 | 2.23 | 48% | 6% | 28% | 30% | 34/26/17% | 24% |
| res:win | us | 14933 | 10.52 | 9.8 | 17.64 | 2.01 | 47% | 7% | 31% | 30% | 35/24/0% | 19% |
| res:win | opp | 14570 | 11.51 | 10.8 | 18.90 | 1.94 | 47% | 6% | 38% | 36% | 39/31/38% | 28% |

Reading: mean pairwise distance 10.6 vs 11.5, largest cluster 2.0 vs 2.1 champions (48% / 47% of the team); 7% of rounds all together (opp 6%), 31% all apart (opp 32%); 29% of champion-rounds with no ally within 6 (opp 32%), melee 33% / casters 25% (opp 36/28). Per map we are slightly tighter than the opponent on the fight maps (collision 7.1 vs 9.1, corners 8.9 vs 10.5, packs 8.3 vs 9.7, interlock 8.5 vs 9.4) and the same on farm maps (lanes 12.9 vs 12.5, rows 11.9 vs 12.0, monolith 16.5 vs 17.3, expanse 16.5 vs 18.2: 1 champion per camp). "Alone with an enemy within 8" is 21% of our near-enemy champion-rounds (opp 25%); monolith 48%, expanse 42%, elkring 34%. Win/loss: identical for us (10.5/10.6, alone 30/29%).

### 2b. Formation when an enemy is within 8: distance to nearest enemy by class; melee in front of casters?

| split | who | melee d | caster d | ranged d | rounds caster+melee | melee front | level | caster front | gap | ranged vs melee: melee front/level/ranged front | engaged/alive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 5.26/5 | 5.41/5 | - | 10319 | 44% | 16% | 38% | +0.23 | 0%/0%/0% | 50% |
| ALL | opp | 5.06/5 | 5.51/5 | 5.57/6 | 8272 | 50% | 16% | 32% | +0.54 | 57%/15%/27% | 45% |
| map:collision | us | 5.44/6 | 5.58/6 | - | 2592 | 43% | 16% | 39% | +0.23 | 0%/0%/0% | 58% |
| map:collision | opp | 5.14/5 | 5.69/6 | - | 1713 | 51% | 17% | 31% | +0.62 | 0%/0%/0% | 52% |
| map:corners | us | 4.68/5 | 4.94/5 | - | 2336 | 42% | 19% | 38% | +0.15 | 0%/0%/0% | 63% |
| map:corners | opp | 4.82/5 | 5.28/5 | 5.59/6 | 2488 | 51% | 16% | 32% | +0.54 | 63%/13%/23% | 56% |
| map:elkring | us | 5.43/6 | 5.70/6 | - | 962 | 44% | 15% | 40% | +0.08 | 0%/0%/0% | 42% |
| map:elkring | opp | 5.36/6 | 5.82/6 | 6.25/7 | 857 | 53% | 18% | 28% | +0.75 | 47%/17%/34% | 41% |
| map:expanse | us | 5.68/6 | 5.62/6 | - | 21 | 47% | 9% | 42% | +0.10 | 0%/0%/0% | 39% |
| map:interlock | us | 5.37/6 | 5.68/6 | - | 1039 | 43% | 18% | 38% | +0.26 | 0%/0%/0% | 44% |
| map:interlock | opp | 5.25/5 | 5.57/6 | - | 693 | 43% | 16% | 40% | +0.20 | 0%/0%/0% | 43% |
| map:lanes | us | 5.58/6 | 5.67/6 | - | 1167 | 51% | 14% | 33% | +0.60 | 0%/0%/0% | 43% |
| map:lanes | opp | 5.36/6 | 5.48/6 | 5.21/5 | 803 | 48% | 18% | 33% | +0.43 | 38%/22%/39% | 34% |
| map:monolith | us | 5.16/5 | 5.34/6 | - | 550 | 48% | 18% | 33% | +0.48 | 0%/0%/0% | 33% |
| map:monolith | opp | 4.84/5 | 5.46/5 | 4.95/4 | 387 | 50% | 14% | 34% | +0.63 | 0%/25%/75% | 29% |
| map:packs | us | 5.27/5 | 5.36/5 | - | 1593 | 44% | 14% | 40% | +0.02 | 0%/0%/0% | 55% |
| map:packs | opp | 4.82/5 | 5.55/5 | - | 1316 | 50% | 15% | 33% | +0.55 | 0%/0%/0% | 48% |
| map:rows | us | 4.96/5 | 5.94/6 | - | 59 | 55% | 18% | 25% | +1.27 | 0%/0%/0% | 42% |
| map:rows | opp | 4.57/4 | 3.63/3 | - | 15 | 53% | 6% | 40% | +0.27 | 0%/0%/0% | 22% |
| opp:r11-30 | us | 5.28/5 | 5.44/5 | - | 7253 | 44% | 17% | 38% | +0.22 | 0%/0%/0% | 50% |
| opp:r11-30 | opp | 5.07/5 | 5.49/5 | 5.49/6 | 5753 | 50% | 16% | 33% | +0.56 | 58%/15%/26% | 44% |
| opp:top10 | us | 5.20/5 | 5.32/5 | - | 3066 | 46% | 16% | 37% | +0.26 | 0%/0%/0% | 50% |
| opp:top10 | opp | 5.04/5 | 5.54/5 | 6.14/6 | 2519 | 49% | 17% | 32% | +0.51 | 53%/16%/30% | 46% |
| res:loss | us | 5.21/5 | 5.33/5 | - | 6088 | 45% | 16% | 38% | +0.23 | 0%/0%/0% | 51% |
| res:loss | opp | 5.01/5 | 5.47/5 | 5.61/6 | 5230 | 49% | 16% | 33% | +0.46 | 56%/15%/27% | 45% |
| res:win | us | 5.32/5 | 5.51/6 | - | 4231 | 44% | 17% | 38% | +0.23 | 0%/0%/0% | 48% |
| res:win | opp | 5.13/5 | 5.58/6 | 5.20/5 | 3042 | 51% | 17% | 31% | +0.68 | 64%/10%/24% | 45% |
| who | Cassi | Issac | Marcella | Prism | Ren | Ryth | Stellar | Tavi | Varg | Vendetta | VesperVale | Willow |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| us | 5.57/6 (n=5734) | 5.48/6 (n=5201) | - | 5.06/5 (n=2377) | 5.18/5 (n=8399) | 5.08/5 (n=4546) | 5.42/6 (n=8140) | 5.34/5 (n=4973) | 5.31/5 (n=1623) | 5.36/6 (n=1422) | - | - |
| opp | 5.56/6 (n=6027) | 5.17/5 (n=6210) | 5.09/5 (n=299) | 5.47/5 (n=1354) | 5.16/5 (n=5289) | 4.84/5 (n=3779) | 5.50/5 (n=7314) | 5.45/5 (n=4401) | 4.92/5 (n=3918) | 5.14/5 (n=2191) | 5.02/5 (n=138) | 5.67/6 (n=816) |

Reading: **casters are not behind the melee.** With both classes engaged (10,319 rounds), the melee is strictly nearer the enemy in 44%, level 16%, the caster is nearer in 38%; mean gap +0.23 tiles (opp 50/16/32, +0.54; the Mite study measured 66% melee-first, +1.35). On packs the gap is +0.02 and corners +0.15 — Stellar/Prism/Tavi/Cassi stand where Ryth/Ren/Issac stand. Every type of ours sits at median 5-6 tiles from the nearest enemy (Ryth 5.08, Prism 5.06 … Cassi 5.57); the opponents' melee (Ryth 4.84, Varg 4.92) are a tile closer than their casters (Stellar 5.50, Cassi 5.56). Half of our alive champions are within 8 of an enemy when any is (50%; opp 45%): we bring the same numbers they do, we just arrange them flat.


## 3. What each champion type does per round (Q3)

### 3a. Action share (% of alive champion-rounds), all games

| split | who | type | n rounds | move | attack camp | cast@camp | attack champ | cast@champ | dash | ability(no eff) | tribute | recall | buy | nothing | arrive | attack(miss) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | ALL | 308639 | 50 | 19 | 3 | 1 | 1 | 3 | 0 | 6 | 6 | 1 | 9 | 0 | 0 |
| ALL | us | Cassi | 48095 | 52 | 20 | 5 | 1 | 1 | 0 | 1 | 5 | 4 | 0 | 11 | 0 | 0 |
| ALL | us | Issac | 48125 | 40 | 26 | 0 | 1 | 0 | 7 | 0 | 8 | 7 | 1 | 10 | 0 | 0 |
| ALL | us | Prism | 13340 | 56 | 12 | 6 | 1 | 4 | 0 | 0 | 4 | 6 | 0 | 10 | 1 | 0 |
| ALL | us | Ren | 42782 | 42 | 17 | 3 | 2 | 2 | 7 | 0 | 7 | 9 | 1 | 8 | 1 | 0 |
| ALL | us | Ryth | 34419 | 57 | 17 | 3 | 1 | 1 | 0 | 0 | 5 | 6 | 1 | 7 | 0 | 0 |
| ALL | us | Stellar | 39512 | 54 | 11 | 7 | 1 | 4 | 0 | 0 | 5 | 6 | 1 | 11 | 0 | 0 |
| ALL | us | Tavi | 31433 | 54 | 20 | 4 | 1 | 1 | 0 | 0 | 4 | 4 | 0 | 11 | 0 | 0 |
| ALL | us | Varg | 25684 | 55 | 23 | 0 | 1 | 0 | 0 | 1 | 8 | 6 | 1 | 6 | 0 | 0 |
| ALL | us | Vendetta | 25249 | 47 | 22 | 0 | 1 | 0 | 6 | 0 | 8 | 7 | 1 | 8 | 0 | 0 |
| ALL | opp | ALL | 329013 | 49 | 18 | 3 | 1 | 1 | 2 | 0 | 7 | 8 | 1 | 10 | 0 | 0 |
| ALL | opp | Cassi | 54492 | 51 | 20 | 5 | 1 | 1 | 0 | 1 | 4 | 7 | 0 | 10 | 0 | 0 |
| ALL | opp | Issac | 54508 | 42 | 23 | 0 | 1 | 0 | 6 | 0 | 7 | 9 | 1 | 11 | 0 | 0 |
| ALL | opp | Marcella | 2243 | 55 | 16 | 3 | 2 | 2 | 0 | 0 | 5 | 5 | 1 | 11 | 0 | 0 |
| ALL | opp | Prism | 8152 | 48 | 11 | 6 | 1 | 3 | 0 | 0 | 6 | 14 | 0 | 10 | 0 | 0 |
| ALL | opp | Ren | 36038 | 41 | 16 | 3 | 2 | 1 | 6 | 0 | 9 | 10 | 1 | 11 | 0 | 0 |
| ALL | opp | Ryth | 26908 | 50 | 15 | 3 | 1 | 1 | 0 | 0 | 7 | 11 | 1 | 9 | 0 | 0 |
| ALL | opp | Stellar | 49584 | 54 | 10 | 6 | 1 | 2 | 0 | 0 | 7 | 9 | 1 | 10 | 0 | 0 |
| ALL | opp | Tavi | 30044 | 56 | 16 | 4 | 2 | 1 | 0 | 0 | 5 | 4 | 0 | 11 | 1 | 0 |
| ALL | opp | Varg | 34844 | 53 | 19 | 0 | 2 | 0 | 0 | 2 | 9 | 5 | 1 | 9 | 0 | 0 |
| ALL | opp | Vendetta | 25330 | 44 | 22 | 0 | 1 | 0 | 6 | 0 | 8 | 7 | 1 | 10 | 0 | 0 |
| ALL | opp | VesperVale | 1225 | 46 | 25 | 0 | 3 | 0 | 6 | 0 | 5 | 6 | 0 | 8 | 0 | 0 |
| ALL | opp | Willow | 5645 | 52 | 23 | 0 | 2 | 0 | 0 | 3 | 3 | 5 | 0 | 12 | 0 | 0 |

Win/loss and top-10 splits (same table, selected):

| split | who | type | n rounds | move | attack camp | cast@camp | attack champ | cast@champ | dash | ability(no eff) | tribute | recall | buy | nothing | arrive | attack(miss) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| res:win | us | ALL | 129082 | 49 | 19 | 3 | 1 | 1 | 3 | 0 | 7 | 6 | 1 | 9 | 0 | 0 |
| res:win | opp | ALL | 123133 | 51 | 18 | 3 | 1 | 1 | 2 | 0 | 6 | 6 | 0 | 11 | 0 | 0 |
| res:loss | us | ALL | 179557 | 51 | 19 | 3 | 1 | 1 | 2 | 0 | 5 | 6 | 1 | 10 | 0 | 0 |
| res:loss | opp | ALL | 205880 | 47 | 17 | 3 | 1 | 1 | 2 | 1 | 7 | 9 | 1 | 10 | 0 | 0 |
| opp:top10 | us | ALL | 94282 | 49 | 19 | 3 | 1 | 1 | 3 | 0 | 6 | 7 | 1 | 10 | 0 | 0 |
| opp:top10 | opp | ALL | 103744 | 44 | 17 | 3 | 1 | 1 | 2 | 0 | 7 | 14 | 1 | 9 | 0 | 0 |
| opp:r11-30 | us | ALL | 214357 | 50 | 19 | 3 | 1 | 1 | 2 | 0 | 6 | 6 | 1 | 9 | 0 | 0 |
| opp:r11-30 | opp | ALL | 225269 | 51 | 18 | 3 | 1 | 1 | 2 | 1 | 6 | 5 | 1 | 11 | 0 | 0 |

Reading: per type we and the opponents (same types) do the same things: Issac/Vendetta/Varg are the camp hitters (22-26% attack camp), Stellar/Prism cast at camps 6-7% and move 54-56%, everybody fights champions 1-4% of rounds. Differences: our Ren/Issac dash 7% (opp 6%); we recall 6% vs their 8% (vs top-10 opponents they recall 14% — Prism 35%, Ryth 22%: the top-10 use recall as a teleport home after every bag, we do not); we buy 1%; "nothing" 9% vs 10%. In losses our Cassi idles 13%, Prism 10%; the opponent in our losses recalls 9% and tributes 7% (we 5%). Dead share of champion-rounds: us 13% (wins 8, losses 17; corners 27%, collision 22%, packs 18%), opp 9%.

### 3b. Where the "nothing" rounds happen (% of idle champion-rounds)

| split | who | idle rounds | spawn | altar | camp | own | mid | enemy | enemy<=8 | enemy<=3 | hp<50% | carrying gems | camp awake next to it |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 29135 | 7% | 13% | 18% | 54% | 7% | 1% | 40% | 5% | 6% | 10% | 9% |
| ALL | opp | 34077 | 5% | 12% | 13% | 58% | 6% | 5% | 24% | 4% | 10% | 17% | 5% |
| res:win | us | 11718 | 5% | 17% | 19% | 49% | 9% | 1% | 41% | 4% | 5% | 11% | 8% |
| res:win | opp | 13214 | 6% | 8% | 12% | 65% | 7% | 2% | 22% | 4% | 10% | 18% | 4% |
| res:loss | us | 17417 | 9% | 10% | 17% | 58% | 6% | 1% | 39% | 6% | 7% | 9% | 9% |
| res:loss | opp | 20863 | 4% | 15% | 14% | 54% | 6% | 7% | 26% | 5% | 10% | 16% | 7% |
| opp:top10 | us | 9063 | 8% | 11% | 18% | 54% | 8% | 1% | 39% | 5% | 6% | 11% | 9% |
| opp:top10 | opp | 9668 | 4% | 16% | 13% | 55% | 8% | 4% | 27% | 4% | 10% | 19% | 6% |
| opp:r11-30 | us | 20072 | 7% | 13% | 17% | 54% | 7% | 1% | 40% | 5% | 6% | 10% | 9% |
| opp:r11-30 | opp | 24409 | 5% | 11% | 13% | 59% | 6% | 6% | 23% | 4% | 10% | 16% | 5% |
| map:collision | us | 5270 | 4% | 28% | 48% | 9% | 11% | 0% | 64% | 5% | 8% | 21% | 16% |
| map:collision | opp | 4240 | 5% | 16% | 46% | 25% | 4% | 3% | 31% | 5% | 11% | 30% | 6% |
| map:corners | us | 3428 | 11% | 46% | 2% | 39% | 1% | 1% | 74% | 14% | 8% | 6% | 13% |
| map:corners | opp | 4939 | 5% | 61% | 2% | 23% | 3% | 7% | 58% | 11% | 16% | 10% | 13% |
| map:elkring | us | 2797 | 24% | 6% | 4% | 59% | 4% | 4% | 30% | 5% | 5% | 7% | 3% |
| map:elkring | opp | 3748 | 19% | 2% | 5% | 62% | 4% | 9% | 23% | 5% | 11% | 13% | 2% |
| map:expanse | us | 1604 | 9% | 2% | 0% | 89% | 0% | 0% | 1% | 0% | 5% | 0% | 0% |
| map:expanse | opp | 2880 | 2% | 1% | 1% | 96% | 0% | 1% | 0% | 0% | 7% | 21% | 0% |
| map:interlock | us | 2402 | 4% | 12% | 2% | 79% | 2% | 1% | 32% | 5% | 3% | 13% | 2% |
| map:interlock | opp | 3181 | 2% | 5% | 2% | 82% | 4% | 5% | 17% | 3% | 13% | 17% | 1% |
| map:lanes | us | 5424 | 5% | 1% | 40% | 50% | 3% | 0% | 38% | 4% | 7% | 17% | 18% |
| map:lanes | opp | 4967 | 1% | 1% | 38% | 48% | 2% | 9% | 23% | 2% | 6% | 23% | 12% |
| map:monolith | us | 1754 | 8% | 2% | 2% | 79% | 5% | 3% | 18% | 5% | 10% | 8% | 1% |
| map:monolith | opp | 2985 | 3% | 1% | 2% | 85% | 3% | 6% | 8% | 2% | 10% | 28% | 1% |
| map:packs | us | 3172 | 9% | 0% | 4% | 54% | 32% | 1% | 50% | 6% | 3% | 0% | 4% |
| map:packs | opp | 3425 | 7% | 1% | 3% | 45% | 40% | 5% | 35% | 6% | 9% | 3% | 3% |
| map:rows | us | 3284 | 0% | 2% | 1% | 97% | 0% | 0% | 2% | 0% | 3% | 2% | 1% |
| map:rows | opp | 3712 | 1% | 3% | 3% | 92% | 0% | 1% | 4% | 3% | 6% | 7% | 3% |

Reading: 29,135 idle champion-rounds (9%). 54% are in our own half away from spawn/altar/camp (typical: a champion that arrived at an assigned tile and waits), 18% next to a living camp (collision 48%, lanes 40%: waiting at a camp without hitting it), 13% at an altar (corners 46%: standing on the centre altar), 7% at spawn. 40% of our idle rounds have an enemy within 8 (opp 24%); corners 74%, collision 64%, packs 50%: we stand still in sight of the enemy far more than they do. Idle with hp<50% 6% (opp 10%), idle while carrying gems 10% (opp 17%).

Longest idle streaks of ours (len, match, map, start round, type, tile): 35 `7b5737d6` elkring r408 Prism (16,4); 30 rounds: `f7c0393d` monolith r197 Cassi (23,42); `bb03df0f` elkring r548 Tavi (7,6) and r254 (7,15); `604ff2a6`/`43cfdda9` monolith r115-122 Issac (5,21); and **in at least 15 of 18 rows games Cassi stands at (36,8) from r203 for exactly 30 rounds** (the top-25 list is truncated) (script: she waits between wolf packs (31,3) and (42,3) for a respawn while the other three clear (18,3)). 177 streaks ≥8 rounds = 1.2 per game.

### 3c. Idle next to a living own-half camp (farm maps): streaks of ≥5 rounds within 6 tiles of a living own camp group

| map | who | streaks | per game | mean len | no ally within 6 | enemy within 8 | camp awake | an ally is already hitting that camp | hp<50% | ends by attacking that camp (within 3r) |
|---|---|---|---|---|---|---|---|---|---|---|
| elkring | opp | 131 | 9.4 | 6.9 | 22% | 9% | 48% | 33% | 9% | 18% |
| elkring | us | 79 | 5.6 | 8.8 | 39% | 22% | 32% | 8% | 5% | 18% |
| expanse | opp | 55 | 3.2 | 5.3 | 60% | 0% | 43% | 34% | 5% | 16% |
| expanse | us | 45 | 2.6 | 5.4 | 40% | 0% | 37% | 37% | 0% | 0% |
| interlock | opp | 151 | 11.6 | 5.6 | 31% | 4% | 52% | 28% | 13% | 22% |
| interlock | us | 38 | 2.9 | 5.3 | 13% | 39% | 84% | 36% | 2% | 21% |
| lanes | opp | 567 | 31.5 | 5.4 | 20% | 10% | 22% | 16% | 5% | 24% |
| lanes | us | 638 | 35.4 | 5.1 | 20% | 28% | 19% | 13% | 2% | 24% |
| monolith | opp | 44 | 3.4 | 10.2 | 61% | 11% | 25% | 15% | 9% | 54% |
| monolith | us | 13 | 1.0 | 13.5 | 84% | 7% | 0% | 0% | 0% | 53% |
| rows | opp | 24 | 1.3 | 8.8 | 25% | 0% | 41% | 16% | 4% | 37% |
| rows | us | 110 | 6.1 | 10.7 | 32% | 1% | 18% | 18% | 0% | 64% |

Reading: on rows we stand next to a living wolf pack for 5+ rounds 6.1 times a game (opp 1.3), 10.7 rounds each, with 1-2 allies nearby (no ally within 4 in 32%); allies do not arrive during the wait (allies within 4 at start 0.54 → end 0.53) and in 36% the champion walks away without hitting the pack. On lanes both sides do it (35 vs 32 streaks/game, 5 rounds): standing at a cluster with the camp asleep. Interlock: our 38 streaks are 84% next to an awake camp with an enemy within 8 in 39% — we freeze when an enemy is near a contested camp.


## 4. Territory over time: captures by group territory, own-half losses, relation to the result (Q4)

### 4a. Captures by territory of the group (own/mid/enemy from the capturer's side), 50-round bins

| split | who | 0-49 | 50-99 | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 | 400-449 | 450+ | total own/mid/enemy | gems own/mid/enemy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 260/96/0 | 305/30/1 | 336/61/10 | 331/41/4 | 296/52/7 | 337/52/8 | 382/57/9 | 231/57/1 | 187/45/7 | 337/131/5 | 3002/622/52 | 105018/22104/1784 |
| ALL | opp | 344/15/0 | 287/46/8 | 356/64/24 | 350/66/27 | 354/61/16 | 373/58/14 | 359/62/18 | 270/55/19 | 173/45/14 | 355/144/26 | 3221/616/166 | 113152/23438/5526 |
| map:collision | us | 0/32/0 | 38/1/0 | 18/13/0 | 21/15/0 | 21/15/1 | 30/11/0 | 28/14/0 | 33/16/0 | 32/15/0 | 179/86/0 | 400/218/1 | 9026/4796/22 |
| map:collision | opp | 45/1/0 | 25/6/0 | 33/5/0 | 27/3/1 | 25/7/1 | 30/4/0 | 28/9/2 | 33/6/3 | 31/6/1 | 177/49/7 | 454/96/15 | 12314/2112/588 |
| map:corners | us | 0/34/0 | 16/16/0 | 7/24/0 | 7/15/0 | 7/16/0 | 2/15/0 | 4/22/0 | 2/14/0 | 5/12/0 | 11/26/0 | 61/194/0 | 1564/9192/0 |
| map:corners | opp | 15/8/0 | 14/12/0 | 13/21/0 | 12/23/2 | 16/21/0 | 5/17/1 | 15/20/0 | 13/21/0 | 6/19/0 | 30/75/3 | 139/237/6 | 3678/10944/146 |
| map:elkring | us | 28/0/0 | 23/0/0 | 28/0/1 | 25/0/0 | 27/0/1 | 27/0/4 | 23/0/3 | 31/0/0 | 25/0/3 | 79/0/5 | 316/0/17 | 11376/0/612 |
| map:elkring | opp | 34/0/0 | 24/0/1 | 37/0/4 | 29/0/3 | 32/0/3 | 24/0/4 | 33/0/1 | 30/0/3 | 28/0/2 | 79/0/9 | 350/0/30 | 12204/0/1080 |
| map:expanse | us | 51/0/0 | 50/0/0 | 67/0/0 | 65/0/0 | 63/0/0 | 52/0/0 | 73/0/0 | 3/0/0 | - | - | 424/0/0 | 17128/0/0 |
| map:expanse | opp | 48/0/0 | 52/0/1 | 63/0/0 | 60/0/2 | 62/0/0 | 65/1/0 | 53/2/0 | 9/1/0 | - | - | 412/4/3 | 16116/432/144 |
| map:interlock | us | 39/0/0 | 32/0/0 | 40/0/0 | 35/0/1 | 34/0/0 | 42/0/0 | 37/1/0 | 36/2/0 | 33/1/0 | 23/1/0 | 351/5/1 | 11784/180/72 |
| map:interlock | opp | 41/0/0 | 20/1/1 | 34/1/2 | 34/1/0 | 29/2/1 | 32/1/0 | 36/1/0 | 32/1/0 | 27/0/1 | 20/1/2 | 305/9/7 | 10858/324/382 |
| map:lanes | us | 72/0/0 | 79/12/0 | 59/7/5 | 82/5/2 | 65/7/5 | 83/14/0 | 82/10/4 | 45/9/1 | 22/4/0 | 8/0/0 | 597/68/17 | 14290/1496/374 |
| map:lanes | opp | 69/0/0 | 50/15/5 | 82/16/15 | 72/21/17 | 79/15/7 | 95/16/6 | 80/16/10 | 43/8/4 | 15/1/0 | 5/3/0 | 590/111/64 | 14574/2442/1514 |
| map:monolith | us | 52/0/0 | 15/0/1 | 48/0/4 | 37/0/1 | 39/0/0 | 35/0/4 | 37/0/2 | 30/0/0 | 31/0/4 | 4/0/0 | 328/0/16 | 11458/0/704 |
| map:monolith | opp | 42/0/0 | 40/0/0 | 35/0/3 | 53/0/1 | 46/0/4 | 47/0/1 | 37/0/3 | 43/0/6 | 33/0/3 | 5/0/1 | 381/0/22 | 12082/0/836 |
| map:packs | us | 0/30/0 | 34/1/0 | 15/17/0 | 25/6/0 | 22/14/0 | 30/12/0 | 32/10/0 | 22/16/0 | 27/13/0 | 33/18/0 | 240/137/0 | 10572/6440/0 |
| map:packs | opp | 31/6/0 | 24/12/0 | 21/21/0 | 25/18/1 | 25/16/0 | 30/19/2 | 33/14/2 | 29/18/3 | 23/19/7 | 39/16/4 | 280/159/19 | 11856/7184/836 |
| map:rows | us | 18/0/0 | 18/0/0 | 54/0/0 | 34/0/0 | 18/0/0 | 36/0/0 | 66/0/0 | 29/0/0 | 12/0/0 | - | 285/0/0 | 17820/0/0 |
| map:rows | opp | 19/0/0 | 38/0/0 | 38/0/0 | 38/0/0 | 40/0/0 | 45/0/0 | 44/0/0 | 38/0/0 | 10/0/0 | - | 310/0/0 | 19470/0/0 |
| opp:r11-30 | us | 183/62/0 | 204/21/1 | 234/41/8 | 221/27/4 | 210/42/6 | 235/40/7 | 269/33/7 | 162/43/0 | 134/38/6 | 254/105/3 | 2106/452/42 | 73526/16434/1406 |
| opp:r11-30 | opp | 235/7/0 | 181/25/6 | 244/32/20 | 228/40/17 | 239/28/14 | 250/25/12 | 249/35/14 | 184/29/12 | 126/20/11 | 258/104/19 | 2194/345/125 | 76588/12876/4030 |
| opp:top10 | us | 77/34/0 | 101/9/0 | 102/20/2 | 110/14/0 | 86/10/1 | 102/12/1 | 113/24/2 | 69/14/1 | 53/7/1 | 83/26/2 | 896/170/10 | 31492/5670/378 |
| opp:top10 | opp | 109/8/0 | 106/21/2 | 112/32/4 | 122/26/10 | 115/33/2 | 123/33/2 | 110/27/4 | 86/26/7 | 47/25/3 | 97/40/7 | 1027/271/41 | 36564/10562/1496 |
| res:loss | us | 160/51/0 | 179/24/1 | 188/29/7 | 193/16/0 | 161/25/1 | 199/23/4 | 221/31/3 | 134/22/1 | 83/17/1 | 136/46/4 | 1654/284/22 | 58494/10808/756 |
| res:loss | opp | 202/11/0 | 169/39/7 | 216/48/21 | 220/52/25 | 218/52/14 | 243/49/9 | 219/51/13 | 176/45/11 | 99/36/11 | 180/106/23 | 1942/489/134 | 69250/18558/4452 |
| res:win | us | 100/45/0 | 126/6/0 | 148/32/3 | 138/25/4 | 135/27/6 | 138/29/4 | 161/26/6 | 97/35/0 | 104/28/6 | 201/85/1 | 1348/338/30 | 46524/11296/1028 |
| res:win | opp | 142/4/0 | 118/7/1 | 140/16/3 | 130/14/2 | 136/9/2 | 130/9/5 | 140/11/5 | 94/10/8 | 74/9/3 | 175/38/3 | 1279/127/32 | 43902/4880/1074 |

### 4b. Own-half groups captured by the enemy

| split | games | games with own-half group lost | first loss round median / min / p25 |
|---|---|---|---|
| ALL | 150 | 64 (42%) | 214 / 50 / 143 |
| map:collision | 19 | 7 (36%) | 369 / 172 / 223 |
| map:corners | 17 | 3 (17%) | 163 / 157 / 157 |
| map:elkring | 14 | 11 (78%) | 160 / 99 / 102 |
| map:expanse | 17 | 1 (5%) | 97 / 97 / 97 |
| map:interlock | 13 | 4 (30%) | 341 / 70 / 217 |
| map:lanes | 18 | 14 (77%) | 130 / 50 / 103 |
| map:monolith | 13 | 11 (84%) | 248 / 126 / 143 |
| map:packs | 21 | 13 (61%) | 426 / 199 / 336 |
| opp:r11-30 | 100 | 41 (41%) | 212 / 70 / 126 |
| opp:top10 | 50 | 23 (46%) | 217 / 50 / 160 |
| res:loss | 91 | 45 (49%) | 196 / 50 / 140 |
| res:win | 59 | 19 (32%) | 333 / 99 / 157 |

### 4c. Per-game means by map and result

| split | games | us mid caps | opp mid caps | us enemy-half caps | opp enemy-half caps (=our camps lost) | us own | opp own | us mid gems | opp mid gems | opp gems from our half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 150 | 4.1 | 4.1 | 0.3 | 1.1 | 20.0 | 21.5 | 147 | 156 | 37 |
| res:win | 59 | 5.7 | 2.2 | 0.5 | 0.5 | 22.8 | 21.7 | 191 | 83 | 18 |
| res:loss | 91 | 3.1 | 5.4 | 0.2 | 1.5 | 18.2 | 21.3 | 119 | 204 | 49 |
| map:collision win | 12 | 14.2 | 3.0 | 0.1 | 0.3 | 24.2 | 22.2 | 314 | 66 | 14 |
| map:collision loss | 7 | 6.7 | 8.6 | 0.0 | 1.6 | 15.6 | 26.7 | 148 | 189 | 59 |
| map:corners win | 5 | 17.6 | 7.0 | 0.0 | 0.2 | 5.2 | 7.4 | 840 | 317 | 4 |
| map:corners loss | 12 | 8.8 | 16.8 | 0.0 | 0.4 | 2.9 | 8.5 | 416 | 780 | 10 |
| map:elkring win | 5 | 0.0 | 0.0 | 1.4 | 1.2 | 25.6 | 27.2 | 0 | 0 | 43 |
| map:elkring loss | 9 | 0.0 | 0.0 | 1.1 | 2.7 | 20.9 | 23.8 | 0 | 0 | 96 |
| map:expanse win | 11 | 0.0 | 0.3 | 0.0 | 0.0 | 25.8 | 24.5 | 0 | 29 | 0 |
| map:expanse loss | 6 | 0.0 | 0.2 | 0.0 | 0.5 | 23.3 | 23.8 | 0 | 18 | 24 |
| map:interlock win | 7 | 0.6 | 0.7 | 0.1 | 0.0 | 29.4 | 24.4 | 21 | 26 | 0 |
| map:interlock loss | 6 | 0.2 | 0.7 | 0.0 | 1.2 | 24.2 | 22.3 | 6 | 24 | 64 |
| map:lanes win | 3 | 4.3 | 3.3 | 3.7 | 3.3 | 37.7 | 33.0 | 95 | 73 | 74 |
| map:lanes loss | 15 | 3.7 | 6.7 | 0.4 | 3.6 | 32.3 | 32.7 | 81 | 148 | 86 |
| map:monolith win | 5 | 0.0 | 0.0 | 2.0 | 1.4 | 27.2 | 27.2 | 0 | 0 | 53 |
| map:monolith loss | 8 | 0.0 | 0.0 | 0.8 | 1.9 | 24.0 | 30.6 | 0 | 0 | 72 |
| map:packs win | 7 | 8.9 | 5.4 | 0.0 | 0.6 | 13.6 | 13.6 | 415 | 254 | 25 |
| map:packs loss | 14 | 5.4 | 8.6 | 0.0 | 1.1 | 10.4 | 13.2 | 253 | 386 | 47 |
| map:rows win | 4 | 0.0 | 0.0 | 0.0 | 0.0 | 17.2 | 17.2 | 0 | 0 | 0 |
| map:rows loss | 14 | 0.0 | 0.0 | 0.0 | 0.0 | 15.4 | 17.2 | 0 | 0 | 0 |

### 4d. Mid-camp balance vs result

| diff -99..-6 | 18 games | win 0% |
| diff -5..-1 | 26 games | win 19% |
| diff 0..0 | 63 games | win 38% |
| diff 1..5 | 27 games | win 59% |
| diff 6..99 | 16 games | win 87% |

Reading:
- **Middle camps are the game on collision/corners/packs** and we win them only when we win: collision wins 14.2 mid captures vs opp 3.0, losses 6.7 vs 8.6; corners wins 17.6 vs 7.0, losses 8.8 vs 16.8; packs wins 8.9 vs 5.4, losses 5.4 vs 8.6. The same holds in gems (corners wins 840 vs 317 mid gems, losses 416 vs 780). The mid balance by bins shows the swing happens early: on corners our mid captures per bin are 34/16/24/15/16/15/22/14/12/26 vs the opponent's 8/12/21/23/21/17/20/21/19/75 — we win the first clearing (r0-49: 34 vs 8, nobody has died yet) and lose the centre from r100 on (dead champions). On collision r0-49 we take 32 mid captures to their 1 (we walk straight to the central wolves), then 13-16 vs 3-9 per bin.
- **We farm the enemy half almost never** (52 captures in 150 games = 0.35/game; lanes 17, elkring 17, monolith 16, 0 on corners/packs/rows/expanse). The opponents took 166 groups in our half (1.1/game; lanes 64, elkring 30, monolith 22, packs 19, collision 15), 1.5/game in our losses, median 49 gems/game (lanes losses 86, elkring losses 96, interlock losses 64).
- **From what round**: the opponent's first capture in our half comes at median r214 (lanes r130, elkring r160, corners r163, monolith r248, collision r369, packs r426) and happens in 49% of our losses vs 32% of our wins. On lanes (14 of 18 games) and elkring (11 of 14) it is routine from r100 on.
- Games where they took most from our half: `dd220d28` lanes vs WHIM (13 captures, 324 gems, first r79), `22a727e6` collision vs Conley (5, 282 gems, we scored 22), `920d31ac` lanes vs ひななー (11, 264), `690fca52` lanes vs Conley (10, 240), `0969a47f` packs vs BottleBots (5, 220), `6e9d3b94`/`710e2ba1` elkring (5 each, 180).


## 5. The maps we lose most: what is positionally different in wins vs losses, with examples (Q5)

Per-game means (`q5_maps.out`; metrics are % of alive champion-rounds unless stated: own/mid/en territory, depth = mean BFS distance to own spawn, pd = mean pairwise distance, alone = no ally within 6, idle = nothing, spawn = within 2 of spawn, camp = attacking a camp, fight = attacking/casting at champions, trib = tributing; deaths/caps per game; gpr = tributed gems per 100 rounds).


### 5.1 lanes
| metric | us (wins) | us (losses) | opp (our wins) | opp (our losses) |
|---|---|---|---|---|
| own | 92.3 | 93.5 | 79.3 | 78.0 |
| mid | 5.7 | 6.0 | 10.3 | 9.5 |
| en | 2.3 | 0.3 | 10.0 | 12.7 |
| depth | 25.3 | 25.1 | 28.3 | 28.8 |
| pd | 13.3 | 12.7 | 14.2 | 12.1 |
| alone | 29.3 | 25.8 | 34.3 | 24.6 |
| idle | 14.0 | 13.9 | 11.3 | 12.5 |
| spawn | 6.0 | 6.1 | 3.3 | 3.0 |
| camp | 20.0 | 21.7 | 15.0 | 17.9 |
| fight | 1.3 | 1.2 | 2.0 | 1.9 |
| trib | 6.3 | 5.9 | 6.0 | 6.7 |
| deaths | 2.7 | 4.0 | 2.0 | 1.3 |
| caps | 45.7 | 36.3 | 39.7 | 43.1 |
| cap_own | 37.7 | 32.3 | 33.0 | 32.7 |
| cap_mid | 4.3 | 3.7 | 3.3 | 6.7 |
| cap_en | 3.7 | 0.4 | 3.3 | 3.6 |
| gpr | 224.6 | 209.3 | 206.0 | 264.2 |


### 5.2 rows
| metric | us (wins) | us (losses) | opp (our wins) | opp (our losses) |
|---|---|---|---|---|
| own | 100.0 | 99.6 | 97.5 | 98.9 |
| mid | 0.0 | 0.1 | 0.2 | 0.0 |
| en | 0.0 | 0.3 | 2.2 | 1.1 |
| depth | 16.1 | 16.0 | 16.0 | 17.1 |
| pd | 11.9 | 11.8 | 11.0 | 12.2 |
| alone | 20.0 | 20.6 | 24.8 | 23.9 |
| idle | 8.8 | 9.2 | 10.5 | 10.2 |
| spawn | 9.0 | 9.1 | 7.5 | 7.9 |
| camp | 25.8 | 25.6 | 24.8 | 26.9 |
| fight | 0.2 | 0.1 | 0.2 | 0.1 |
| trib | 6.0 | 5.6 | 5.5 | 6.5 |
| deaths | 0.5 | 0.0 | 0.8 | 0.2 |
| caps | 17.2 | 15.4 | 17.2 | 17.2 |
| cap_own | 17.2 | 15.4 | 17.2 | 17.2 |
| cap_mid | 0.0 | 0.0 | 0.0 | 0.0 |
| cap_en | 0.0 | 0.0 | 0.0 | 0.0 |
| gpr | 240.9 | 216.2 | 223.8 | 268.9 |


### 5.3 corners
| metric | us (wins) | us (losses) | opp (our wins) | opp (our losses) |
|---|---|---|---|---|
| own | 72.6 | 85.4 | 80.8 | 56.5 |
| mid | 24.6 | 13.0 | 15.4 | 26.9 |
| en | 2.6 | 1.5 | 3.8 | 16.5 |
| depth | 12.2 | 10.7 | 12.7 | 14.2 |
| pd | 9.0 | 8.8 | 11.8 | 10.1 |
| alone | 25.4 | 30.3 | 32.6 | 22.2 |
| idle | 10.4 | 9.6 | 9.6 | 11.2 |
| spawn | 10.0 | 15.2 | 8.8 | 8.8 |
| camp | 15.6 | 8.2 | 12.0 | 11.5 |
| fight | 6.4 | 7.3 | 4.4 | 5.0 |
| trib | 8.8 | 4.2 | 4.8 | 7.2 |
| deaths | 6.6 | 16.4 | 10.8 | 5.6 |
| caps | 22.8 | 11.8 | 14.6 | 25.8 |
| cap_own | 5.2 | 2.9 | 7.4 | 8.5 |
| cap_mid | 17.6 | 8.8 | 7.0 | 16.8 |
| cap_en | 0.0 | 0.0 | 0.2 | 0.4 |
| gpr | 220.9 | 65.9 | 79.5 | 183.3 |


### 5.4 packs
| metric | us (wins) | us (losses) | opp (our wins) | opp (our losses) |
|---|---|---|---|---|
| own | 75.1 | 80.6 | 68.6 | 66.1 |
| mid | 23.7 | 18.6 | 24.7 | 24.4 |
| en | 1.0 | 0.6 | 6.9 | 9.4 |
| depth | 8.6 | 7.9 | 9.1 | 9.7 |
| pd | 8.7 | 8.0 | 9.3 | 9.8 |
| alone | 31.9 | 31.9 | 39.4 | 38.0 |
| idle | 8.7 | 9.7 | 11.9 | 7.9 |
| spawn | 16.6 | 18.1 | 20.0 | 19.6 |
| camp | 28.3 | 28.0 | 20.7 | 21.6 |
| fight | 3.0 | 3.6 | 2.4 | 2.9 |
| trib | 7.6 | 5.7 | 6.4 | 8.1 |
| deaths | 3.6 | 8.7 | 6.4 | 2.4 |
| caps | 22.4 | 15.7 | 19.6 | 22.9 |
| cap_own | 13.6 | 10.4 | 13.6 | 13.2 |
| cap_mid | 8.9 | 5.4 | 5.4 | 8.6 |
| cap_en | 0.0 | 0.0 | 0.6 | 1.1 |
| gpr | 198.5 | 132.5 | 152.0 | 207.1 |


### 5.5 elkring
| metric | us (wins) | us (losses) | opp (our wins) | opp (our losses) |
|---|---|---|---|---|
| own | 79.6 | 81.7 | 82.2 | 72.6 |
| mid | 17.2 | 16.1 | 13.4 | 17.3 |
| en | 3.2 | 2.4 | 4.4 | 10.2 |
| depth | 9.2 | 8.2 | 9.6 | 10.3 |
| pd | 10.2 | 9.7 | 10.5 | 10.5 |
| alone | 23.8 | 26.4 | 24.4 | 26.0 |
| idle | 7.0 | 7.9 | 9.8 | 9.2 |
| spawn | 21.6 | 25.2 | 19.4 | 19.7 |
| camp | 23.4 | 23.6 | 24.0 | 22.9 |
| fight | 1.8 | 2.6 | 1.0 | 2.4 |
| trib | 5.0 | 3.7 | 4.6 | 5.9 |
| deaths | 2.2 | 8.9 | 10.2 | 6.9 |
| caps | 27.0 | 22.0 | 28.4 | 26.4 |
| cap_own | 25.6 | 20.9 | 27.2 | 23.8 |
| cap_mid | 0.0 | 0.0 | 0.0 | 0.0 |
| cap_en | 1.4 | 1.1 | 1.2 | 2.7 |
| gpr | 176.7 | 102.6 | 131.6 | 172.7 |


Per-game detail lines (every game, us vs opp) are in `q5_maps.out`.

#### 5.1 lanes (18 games, 3-15; draft vend/varg/cassi+issac/ryth/tavi in all 18)
Our positions are identical in wins and losses (own 92-94%, enemy 0.3-2.3%, pd 13, idle 14%). Lane allocation (rounds 1-350, `q8_lanes.out`): we keep 20-30% of champion-rounds in the top lane on our side, 45-51% in the middle lane, 18-33% bottom, 0-2% on their side. The opponents put 39-46% top (5-12% of all their rounds in OUR top lane), 34-38% middle, 5-6% bottom. When enemy champions stand in one of our lanes (2,473 lane-rounds): with 1 invader we have 1.36 champions in that lane (28% none), with 2 invaders 1.33 (57% outnumbered), with 3 invaders 1.22 (78% outnumbered, 40% nobody), with 4 invaders 0.85 (100% outnumbered). In losses 45% of invasion rounds have us outnumbered in the lane (wins 20%) and invaders ≥3 occur in 14% of them (wins 0%). We never reinforce a lane; our 2 bottom-lane champions (Varg, Ryth) stay bottom while 4 enemies sit on our top gem clusters.
- `dd220d28` vs WHIM (rank 30, loss 630-1018, 418 rounds). r20 our six on the standard path (26,18),(21,21),(22,22),(24,17),(21,29),(22,21); r40 Vendetta captures top cluster (36,15)→(33,10) area, Cassi/Ryth hit camps; WHIM's six all in the top/middle of their half. r60: three of WHIM (Vendetta8 at (36,7) hp39%, Stellar9 (37,3), Varg10 (36,3)) are already on our top clusters (36,2-6) while our Vendetta (34,4) and Cassi (33,4) are at 53-60% hp; r65 our Vendetta dies there. r80-r180: WHIM's Cassi6 stands at (33,8) in our half for 100 rounds doing nothing but holding the cluster, Tavi11/Var10 rotate through (34,2)-(40,0); our Tavi dies r123 at (32,13), Cassi+Issac die r156 together at the top cluster; meanwhile Varg and Ryth farm the bottom lane (46,28),(43,24) alone and tribute 22-44 at (11,14)/(30,24). r200-r300: we are 3-4 alive, score 230-454 vs 456-696; r335 Cassi+Issac die again at the top; WHIM finishes 1018 at r418 having taken 13 of our own-half groups (324 gems). At no point do more than two of ours stand within 8 of the squatters.
- `690fca52` vs Conley (rank 20, loss 536-1008, 388 rounds). Same opening. r60 Conley's Cassi7 (40,2), Stellar9 (39,5), Tavi11 (38,2) are on our top clusters; r80 Issac recalls at 22% hp, Tavi dies r84 at (37,7); r100-r160 four of Conley's (Cas7, Iss8, Ste9, Tav11) sit between (14,2) and (36,6) — deep in our half, 25-30 tiles from their spawn — while our Vendetta walks (30,9)→(9,7)→(19,21), Varg farms (46,28) bottom, Ryth tributes 44 at (11,14); Cassi+Issac die r162, Tavi r183, Varg r202 (at (33,9) 1v4). Score r220: 228-552. Conley captured 10 of our groups (240 gems). Our champions never once stood 3+ together against the 4 invaders.
- `4cce0949` vs test (rank 17, win 1022-984, 532 rounds): the only difference is the opponent: test splits 1-2 per lane, its Ryth dies r59 at the middle wolves 1v3, Stellar dies r376; its raiders come one at a time (Ryth6 at (42,9), Tavi10 (42,8) r180) and we trade evenly (our Tavi dies r180, Cassi+Issac r187, Ryth r487). We lead 144-48 by r80 because our r40-r62 cycle of the top+bottom clusters (captures r40-r65 of groups 0,10,7,3,5,9,2) is faster than theirs, and we survive because nobody squats on our clusters. Note we still lost 5 champions and tributed 1022 only at r520.
- `d4fbbc81` vs Full Damage (rank 11, win 1012-926): the opponent's champions are on our side only 62 lane-rounds, never 3 together; our 45 captures vs 40.

#### 5.2 rows (18 games, 4-14; draft vend/varg/cassi+issac/ryth in all 18; 0.1 deaths/game, 0 fights)
Pure farming race: three 3-wolf packs per side (66 gems, respawn 40), the 448-gem monolith group in the centre is never attacked by anyone (0 hits in 18 games), the gold cluster neither. All 14 losses end 1056 (16 captures) for the opponent at r351-449; we end 726-957 with 66-198 gems still carried (`q10_determinism.out`). Our per-game means are identical in wins and losses (own 100%, pd 11.9/11.8, idle 8.8/9.2, camp 25.8/25.6, caps 17.2/15.4); the opponent's pace differs (gpr 224 in our wins, 269 in our losses). Numbers (`q6_cycle.out`, `q11_rows.out`, `q12_rowsgroups.out`):
- Respawn→capture latency: us median 27 / mean 40.9 / p75 41; opp 26 / 35.0 / 42. By pack: nearest (18,3) us median 32 (106 captures) vs opp 23 on its mirror (161 captures); middle (31,3) 24 vs 25 (102 vs 94); far (42,3) 31, mean 69, max 244 (77 captures) vs opp 46, mean 70 (55). We lose 9 rounds per cycle on the nearest pack and leave the far pack standing for 60-244 rounds.
- Clearing itself is fine: first hit→capture 21 rounds median (opp 20), 2.7 hitters (opp 2.9), 70% of packs cleared by 3+ hitters; capture→tribute 21 rounds median (opp 23), only 5% over 40 rounds (opp 15%).
- Where the time goes: idle streaks ≥5 next to a living pack 110 (6.1/game) vs 24; champion-rounds idle next to a dead pack 92/game vs 180 (they wait at the spawn tile for the respawn, we wander and come back late). The scripted Cassi wait at (36,8) r203-r233 (15 games).
- `604a6cf6` vs Still Testing (rank 19, loss 726-1056, 449 rounds), per-pack timeline: (18,3) captured r36, r103, r176, r276 (60 rounds after its r216 respawn), r341, r397; (31,3) r63, r125, then **r305 — 140 rounds after its r165 respawn**; (42,3) r141 then **r425 — 244 rounds after its r181 respawn**. r176-r252: Vendetta, Varg and Ryth each carry 66 gems and walk loops through (33,21)→(23,22)→(19,31)→(29,37)→(19,29)→(23,27)→(33,21) in the enemy half with no enemy within 8 (the enemy is farming at y=40-45), Ryth passes (16,16) next to our altar (15,16) at r192 without tributing and continues to (32,20),(22,34),(26,37); Vendetta tributes at r240, Varg r252, Ryth after r256. Meanwhile Cassi stands at (23,4)/(22,2) doing nothing r195-r245 and Issac at (26,9)/(13,9), with packs (31,3) and (42,3) alive (3 wolves each, asleep) the whole time. 60 rounds, 3 live packs, 5 champions, 0 hits.
- `c3eed638` vs SSSA (rank 29, loss 792-1056, 391 rounds): normal game. (42,3): captured r141, then r279 = 98 rounds after respawn, r341; (18,3) every 18-41 rounds; SSSA's mirror packs: (31,44) recaptured 9-15 rounds after respawn from r168 on (they camp the spawn tile), (18,44) 18-44. Final: we 12 tributes + 198 carried (= 990 earned), they 16 tributes, 0 carried.
- `8ac3e855` vs AlphaSlop (rank 22, win 1023-924, 421): we run the same script (Cassi idle (37,9) r205-235, same captures r36/r63/r141…); AlphaSlop is slower (14 tributes), so the script wins. Rows wins are the opponent's slowness, not anything we do differently.

#### 5.3 corners (17 games, 5-12; draft ryth/stellar/prism/ren/tavi in all 17)
The centre (4 gem-cluster pairs at (34-36,31-37) around the altar) is 90% of the gems and our whole team walks there at r0-20 in every game (r20: Ryth (31,34), Stellar (32,40), Prism (31,36-37), Ren (33-34,38-39), Tavi (31,35), all 17 games) and meets the whole enemy team (the opponents also send 4-6 champions to (35-40,28-36) by r20). The first 5v5 at r20-60 decides the game: deaths before r100: our wins 1.2 ours / 1.8 theirs, our losses 2.1 / 0.8; when we lose more before r100 we win 22% (n=9). After losing the first fight we trickle back one or two at a time (own 85%, alone 30%, 56% of our deaths with ≥3 enemies within 6 and only 17% outnumbering; opp deaths 24% outnumbered) and score nothing: in losses we capture 2.9 own-half groups and 8.8 mid per game (wins 5.2 / 17.6), tribute 66 gems per 100 rounds (opp 183). We do not fall back to the 6 own-half camps (groups (24,60), (10,41), (21,9), (28,13), (16,7), (9,5)): `5b4a4b49` and `bc8b7079` end 0 and 0 tributed.
- `5b4a4b49` vs VeryGood (rank 5, loss 0-1026, 398 rounds). r20 our five at the centre (31-34,34-40) with VeryGood's six (Ste/Tav/Cas/Iss/Wil/Pri) at (37-39,30-35) hitting the clusters. r41-54 they capture both east clusters; r60 Ryth recalling at 18% hp from (26,28), Ren recalling 77% at (10,41), Stellar casting at our own camp (28,13) alone, Prism walking (17,42), Tavi (22,32): the team has scattered to five places. r100 Prism dead, Ren recalling again at 40%, Stellar carrying 22 (our only capture, r86, group 1); VeryGood's Ste5/Cas7/Iss8/Wil9 stand on the centre at (32-36,33-36). r128 Ryth dies, r174 Prism, r220 Stellar+Prism dead, r283 Tavi, r340-380 Ryth+Stellar again: every return is 1-2 champions into 4-6. Score 0-882 at r340. Our last captures: none after r86; 7 deaths, 0 tributes.
- `bc8b7079` vs hello (rank 6, loss 0-1030, 526 rounds; mirror draft). r20 both teams at the centre; r47 Ryth dies, r60 Ryth/Stellar/Prism dead (three deaths in the first fight), r81 Ren, r98 Tavi; r100 hello's five stand at (34-36,27-36) and never leave (opp mid share 27%, own 56%); r140-r500 we come back as singles (Ryth r140 at (28,36) 6% hp; Tavi r180 casting at a camp at (34,39) alone next to five enemies, dead r161-r258-r407…), 14 deaths total, 0 captures after r100, score 0.
- `2d33ba62` vs AlphaSlop (rank 22, win 1020-730, 628 rounds). Same opening; this time the r20-r60 fight is even (Ryth dies r42, Prism r54, AlphaSlop's Ren r42), r100 AlphaSlop holds the centre (five at (34-37,33-35)) and leads 96-284 by r140 — then at r207-r220 Stellar/Prism/Tavi (three together at (32-36,35-37)) kill Cassi+Issac and Ren, at r294 Ryth, AlphaSlop collapses to 2 alive and we farm the centre uncontested r260-r380 (captures r282-285, r362-373: 428→642). We lost 9 champions in this win. The difference from the losses: the opponent sent its champions back into the centre as singles too, and lost the trades.

#### 5.4 packs (21 games, 7-14; draft cassi+issac/ren/stellar in all 21)
Opening in all 21 games: r20 Cassi (9,14)+Stellar (9,15) on mid group (11-12,17-18), Issac (18,12)+Ren (17,12) on mid group (18-19,12-13) — two pairs on the two central packs, own-half packs (8,2),(16,2),(24,2) left for later. The opponent's reply decides: PTN Hyperion (`f1d0f333`, loss 44-1012) keeps its four together and recalls home after every bag (its champions show "recall" in every snapshot), kills our pairs one pair at a time (r60 three of ours dead, r126 Cassi+Issac together, r208-213 all four, r328 Cassi+Issac, r412-420 three) — 14 deaths, 1 capture, score 44. Shawn (`7650c0e0`, loss 544-1040): r94 Cassi+Issac die at the (18,12) pack 2v3 (Ryth6 casting, Ste7, Cas4/Iss5 arriving from (17-20,23-25)), r296 again, r442 Ren; Shawn farms our mid packs (captures of groups 2/3 at r330-418) and its own, 8 deaths vs 1. Nyxius (`cb249ef4`, win 1008-760): Nyxius splits (Varg alone bottom, Stellar alone), its Cassi+Issac walk into our Issac+Ren+Cassi at r43 and die, again r167, r257 — 3 deaths of ours vs 7 of theirs, and we out-capture 22 vs 20. Deaths on packs: 82% in our own half, 47% with exactly one enemy within 6 (duels we lose), 39% alone, 48% alone five rounds earlier, 9 tiles from spawn.

#### 5.5 elkring (14 games, 5-9; draft ryth/stellar/prism/ren/tavi in all 14)
Fixed opening in all 14: r20 Ryth (3,7) 55% hp and Ren (4,0) 33% hp (both already hurt by the (3,6) and (9,2) camps), Stellar (6,5) and Tavi (7,5) hitting (3,6-7), Prism (5,6); r60 Ryth alone at (24,5-6) (the enemy-side elk (26,9)), Stellar (11,12)/(23,6), Prism (3,12), Ren (0,7), Tavi (6,16). We farm 1-2 per camp around our corner (own 80%), 24% of our rounds alone, 48% of our deaths alone (opp 42%), 31% hit by a camp in the 5 rounds before death (we fight at 50% hp next to awake camps). Losses: the opponent walks 2-3 champions through our half from r100 (Mite `2f3472aa`: Ren10 at (23,6) r140, Var5 (23,6) r260, captures of our (9,2)/(19,2) packs at r122/r132; score 108-216 at r140 after Ryth died r~90 alone), elkring losses have opp enemy-half share 10.2% vs 4.4% in wins and 2.7 own-half captures vs 1.2. `c2825ed0` vs geese geese go (loss 396-1008): Stellar+Prism die r90 at (17,10) chasing Tavi9 into the middle 2v3, Ren dies r172 alone at (9,2), Tavi r299, Ryth+Prism r412-417 at (0-6,3-10) against Var5/Ste6/Tav9 who then camp our corner; geese captured 5 of our groups. `7b5737d6` vs Still Testing (win 1044-936): the opponent plays the same raid game (Ren10 at (0,21) r180, Ryt9 (10,19) r220, Var5 (4,25) r300) but loses its raiders one by one (Ren10 r220, Ryt9 r295, Var5 r329, three at r407-411) to our 2-3 at home; our positions are the same as in the losses (own 80%, alone 24%).


## 6. Where and how we die (Q7) and numbers at contact (Q9)

### 6a. Deaths

| split | who | n | per game | own/mid/enemy | at camp | allies 0/1/2+ | enemies 1/2/3+ | alone 5r before | farming before | camp-hit before | gems lost (med/mean) | attackers med | spawn dist med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 858 | 5.7 | 76/21/3 | 24% | 33/37/30 | 31/29/28 | 34% | 7% | 17% | 0/10 | 1 | 13 |
| ALL | opp | 581 | 3.9 | 39/34/28 | 28% | 37/31/31 | 30/31/23 | 36% | 6% | 15% | 0/15 | 1 | 17 |
| res:win | us | 195 | 3.3 | 67/30/3 | 30% | 23/42/35 | 34/30/19 | 30% | 6% | 23% | 0/13 | 1 | 13 |
| res:win | opp | 353 | 6.0 | 42/37/20 | 26% | 37/33/29 | 25/31/27 | 36% | 5% | 13% | 0/18 | 1 | 16 |
| res:loss | us | 663 | 7.3 | 79/19/3 | 22% | 36/35/29 | 30/29/31 | 35% | 7% | 16% | 0/9 | 1 | 12 |
| res:loss | opp | 228 | 2.5 | 33/28/39 | 31% | 36/29/35 | 37/32/17 | 35% | 7% | 17% | 0/10 | 1 | 19 |
| opp:top10 | us | 317 | 6.3 | 78/20/2 | 20% | 37/36/27 | 29/27/31 | 36% | 8% | 17% | 0/10 | 1 | 12 |
| opp:top10 | opp | 151 | 3.0 | 34/36/29 | 31% | 38/29/32 | 27/32/23 | 36% | 5% | 22% | 0/13 | 1 | 17 |
| opp:r11-30 | us | 541 | 5.4 | 75/22/3 | 26% | 31/38/31 | 32/30/27 | 32% | 6% | 17% | 0/10 | 1 | 13 |
| opp:r11-30 | opp | 430 | 4.3 | 40/33/27 | 26% | 37/32/31 | 31/31/23 | 36% | 6% | 12% | 0/15 | 1 | 17 |
| map:collision | us | 215 | 11.3 | 65/33/2 | 53% | 22/45/33 | 33/32/16 | 28% | 6% | 33% | 0/11 | 1 | 12 |
| map:collision | opp | 161 | 8.5 | 38/52/11 | 43% | 34/37/29 | 29/30/23 | 37% | 7% | 18% | 22/24 | 1 | 16 |
| map:corners | us | 230 | 13.5 | 80/17/2 | 12% | 33/37/30 | 17/27/56 | 30% | 0% | 0% | 0/8 | 2 | 13 |
| map:corners | opp | 121 | 7.1 | 38/37/25 | 29% | 17/22/61 | 14/40/40 | 13% | 0% | 0% | 0/13 | 2 | 17 |
| map:elkring | us | 91 | 6.5 | 78/19/3 | 14% | 48/35/16 | 34/36/19 | 37% | 9% | 31% | 0/15 | 1 | 11 |
| map:elkring | opp | 113 | 8.1 | 42/24/35 | 17% | 42/35/23 | 42/27/12 | 39% | 9% | 29% | 0/9 | 1 | 17 |
| map:expanse | opp | 1 | 0.1 | 0/0/100 | 0% | 100/0/0 | 0/100/0 | 100% | 0% | 0% | 0/0 | 2 | 61 |
| map:interlock | us | 56 | 4.3 | 75/21/4 | 8% | 29/27/45 | 29/38/21 | 30% | 8% | 10% | 22/27 | 1 | 14 |
| map:interlock | opp | 42 | 3.2 | 50/19/31 | 7% | 50/29/21 | 19/26/36 | 52% | 7% | 7% | 0/22 | 1 | 16 |
| map:lanes | us | 68 | 3.8 | 84/12/4 | 39% | 22/28/50 | 24/34/32 | 20% | 16% | 27% | 0/4 | 2 | 30 |
| map:lanes | opp | 26 | 1.4 | 38/12/50 | 57% | 46/42/12 | 12/50/19 | 53% | 3% | 30% | 0/8 | 1 | 41 |
| map:monolith | us | 49 | 3.8 | 73/20/6 | 10% | 55/41/4 | 47/22/8 | 51% | 14% | 22% | 0/13 | 1 | 20 |
| map:monolith | opp | 32 | 2.5 | 38/22/41 | 12% | 66/22/12 | 44/28/16 | 59% | 3% | 9% | 0/16 | 1 | 28 |
| map:packs | us | 147 | 7.0 | 82/18/1 | 8% | 39/34/27 | 47/20/17 | 48% | 9% | 9% | 0/3 | 1 | 9 |
| map:packs | opp | 79 | 3.8 | 33/29/38 | 17% | 42/33/25 | 47/25/13 | 36% | 8% | 11% | 0/5 | 1 | 13 |
| map:rows | us | 2 | 0.1 | 100/0/0 | 0% | 50/0/50 | 50/0/0 | 50% | 0% | 0% | 33/33 | 1 | 14 |
| map:rows | opp | 6 | 0.3 | 33/0/67 | 33% | 67/33/0 | 17/33/17 | 66% | 16% | 33% | 0/0 | 1 | 59 |

By type: ours Stellar 164, Cassi 158, Issac 158, Ren 106, Tavi 103, Prism 79, Ryth 65, Vendetta 16, Varg 9; theirs Cassi 129, Issac 129, Stellar 88, Ren 55, Ryth 50, Tavi 35, Varg 30, Vendetta 27, Prism 16, Willow 13, Marcella 8. Our deaths per 50-round bin: 27, 64, 51, 96, 50, 80, 82, 75, 90, 243 (r450+); theirs 19, 36, 37, 47, 51, 52, 50, 52, 72, 165.

### 6b. Opening deaths vs result, and local numbers when an enemy is within 8

| map | games | our deaths <r100 (W / L) | their deaths <r100 (W / L) | win% when we lose more champions before r100 | win% when we lose fewer | win% when equal |
|---|---|---|---|---|---|---|
| ALL | 150 | 0.3 / 0.8 | 0.5 / 0.3 | 26% (n=38) | 56% (n=23) | 40% (n=89) |
| collision | 19 | 0.6 / 0.9 | 0.6 / 0.0 | 57% (n=7) | 100% (n=3) | 55% (n=9) |
| corners | 17 | 1.2 / 2.1 | 1.8 / 0.8 | 22% (n=9) | 50% (n=4) | 25% (n=4) |
| elkring | 14 | 0.2 / 0.8 | 0.6 / 0.6 | 20% (n=5) | 40% (n=5) | 50% (n=4) |
| expanse | 17 | 0.0 / 0.0 | 0.0 / 0.0 | - | - | 64% (n=17) |
| interlock | 13 | 0.3 / 0.8 | 0.4 / 0.3 | 33% (n=3) | 66% (n=3) | 57% (n=7) |
| lanes | 18 | 0.3 / 0.9 | 0.7 / 0.1 | 0% (n=6) | 50% (n=2) | 20% (n=10) |
| monolith | 13 | 0.4 / 0.4 | 0.0 / 0.5 | 50% (n=2) | 0% (n=2) | 44% (n=9) |
| packs | 21 | 0.1 / 0.9 | 0.9 / 0.1 | 16% (n=6) | 75% (n=4) | 27% (n=11) |
| rows | 18 | 0.0 / 0.0 | 0.0 / 0.0 | - | - | 22% (n=18) |
| split | who | champ-rounds | outnumbered | even | outnumbering | deaths n | deaths while outnumbered | even | outnumbering |
|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 42415 | 14% | 22% | 62% | 858 | 31% | 26% | 42% |
| ALL | opp | 41736 | 15% | 23% | 60% | 581 | 29% | 24% | 45% |
| res:win | us | 17106 | 10% | 21% | 68% | 195 | 20% | 31% | 48% |
| res:win | opp | 15476 | 18% | 27% | 54% | 353 | 33% | 23% | 42% |
| res:loss | us | 25309 | 17% | 23% | 58% | 663 | 34% | 24% | 40% |
| res:loss | opp | 26260 | 13% | 21% | 64% | 228 | 23% | 26% | 50% |
| opp:top10 | us | 12639 | 17% | 22% | 59% | 317 | 34% | 22% | 42% |
| opp:top10 | opp | 13322 | 13% | 20% | 65% | 151 | 28% | 21% | 49% |
| opp:r11-30 | us | 29776 | 13% | 22% | 63% | 541 | 29% | 28% | 41% |
| opp:r11-30 | opp | 28414 | 16% | 24% | 58% | 430 | 30% | 25% | 44% |
| map:collision | us | 9246 | 10% | 20% | 69% | 215 | 16% | 29% | 53% |
| map:collision | opp | 8327 | 17% | 25% | 56% | 161 | 31% | 23% | 44% |
| map:corners | us | 9358 | 28% | 23% | 48% | 230 | 56% | 26% | 17% |
| map:corners | opp | 11303 | 9% | 15% | 75% | 121 | 24% | 23% | 51% |
| map:elkring | us | 4580 | 17% | 23% | 58% | 91 | 37% | 20% | 41% |
| map:elkring | opp | 4917 | 13% | 22% | 64% | 113 | 27% | 23% | 49% |
| map:expanse | us | 148 | 0% | 22% | 77% | 0 | 0% | 0% | 0% |
| map:interlock | us | 4227 | 10% | 15% | 74% | 56 | 25% | 19% | 55% |
| map:interlock | opp | 3864 | 17% | 21% | 61% | 42 | 40% | 21% | 38% |
| map:lanes | us | 5248 | 8% | 20% | 71% | 68 | 29% | 30% | 39% |
| map:lanes | opp | 4545 | 20% | 23% | 55% | 26 | 42% | 11% | 46% |
| map:monolith | us | 2832 | 11% | 33% | 55% | 49 | 18% | 34% | 46% |
| map:monolith | opp | 2606 | 19% | 42% | 37% | 32 | 40% | 31% | 28% |
| map:packs | us | 6332 | 10% | 26% | 62% | 147 | 19% | 21% | 59% |
| map:packs | opp | 5848 | 17% | 28% | 53% | 79 | 18% | 36% | 44% |
| map:rows | us | 444 | 3% | 14% | 82% | 2 | 0% | 50% | 50% |
| map:rows | opp | 233 | 57% | 31% | 11% | 6 | 50% | 0% | 50% |

Reading: 858 deaths (5.7/game) vs 581 (3.9). 76% of ours are in our own half (theirs 39%: they die on our side and in the middle), median 13 tiles from our spawn; 24% next to a living camp; 67% with an ally within 6 (theirs 63%), 28% with 3+ enemies within 6 (corners 56%). Only 7% were farming a camp in the 5 rounds before (theirs 6%) and 17% were hit by a camp monster in those rounds (collision 33%, elkring 31%). We die with a median of 0 gems (mean 10; interlock 27, elkring 15). With an enemy within 8 we are outnumbered (allies within 8 incl. self < enemies within 8) 14% of the time overall but 28% on corners (opp 9%), and 56% of our corners deaths are outnumbered. In our wins we are outnumbered 10% and outnumbering 68%; in losses 17% / 58%.


## 7. Is it a script? (Q10)


| map | games | us r10 | us r20 | us r30 | us r40 | opp r10 | opp r20 | opp r30 | opp r40 |
|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 2 | 4 | 11 | 17 | 19 | 19 | 19 | 19 |
| corners | 17 | 2 | 8 | 14 | 16 | 17 | 17 | 17 | 17 |
| elkring | 14 | 2 | 2 | 2 | 2 | 14 | 14 | 14 | 14 |
| expanse | 17 | 2 | 2 | 2 | 2 | 17 | 17 | 17 | 17 |
| interlock | 13 | 2 | 2 | 2 | 11 | 13 | 13 | 13 | 13 |
| lanes | 18 | 1 | 1 | 1 | 1 | 18 | 18 | 18 | 18 |
| monolith | 13 | 1 | 1 | 1 | 1 | 13 | 13 | 13 | 13 |
| packs | 21 | 1 | 7 | 12 | 14 | 21 | 21 | 21 | 21 |
| rows | 18 | 1 | 1 | 1 | 1 | 18 | 18 | 18 | 18 |

Reading: number of distinct (type, tile) sets at r10/20/30/40 across the games of a map, positions mirrored into the team-A frame. Ours: 1-2 patterns through r40 on lanes/monolith/rows/elkring/expanse (the 2 = the side-b mirror not being exact), 2 at r10-20 on interlock/collision/corners, diverging only once the enemy is in vision (corners 8 at r20, packs 7). The opponents: as many patterns as games (every opponent is a different bot, and several of them randomise). Our first 20-40 rounds are predictable to the tile.

## 8. What this says about our behaviour (rules a replay reader would infer) and the differences from the opponents

Inferred rules of v35:
1. **Fixed opening per map**, same tiles every game (lanes: all six down the middle to (21-26,17-29) by r20 then Vendetta/Issac/Cassi/Tavi to the top clusters (33-36,2-15) and Varg/Ryth to the bottom (40-43,25-29); corners: all five to the centre altar by r20; packs: 2+2 on the two central packs; elkring/rows/expanse: nearest pack first with 2-3 hitters, then spread 1 per camp). Not reactive to the draft or position of the enemy before contact.
2. **Territory rule: stay home.** Champions have an assigned set of own-half (and, on collision/packs/corners, central) camps and cycle them; the enemy half is entered only when chasing an enemy that was already within 8 (78% of our 437 crossings) — an enemy elk/cluster is taken only when the chase ends on it (lanes 38%, monolith 29% of crossings capture). No raid logic, no "steal their cluster while they are away".
3. **No defence rule.** An enemy in our half triggers nothing collective: the champions near it keep walking their path (52%) or stand (12%); 10% fight. There is no "regroup to the invader", no reinforcement of a lane (lanes: 1.2-1.4 of ours in a lane whatever the number of invaders, 100% outnumbered against 4), no return to the centre as a group on corners (returns are 1-2 champions into 4-6, 56% of our corners deaths outnumbered).
4. **No formation rule.** Casters and melee advance to the same 5-tile distance (gap +0.23); 38% of engaged rounds a caster is the front body. Clump size ~2 (pairs), 29% alone; the pair is the unit (Cassi+Issac die in the same round 5 times in the two packs examples `f1d0f333`/`7650c0e0`).
5. **Camp-cycling rule with gaps.** Nearest-alive-camp with a planned waiting tile: champions wait at a fixed tile between camps for a respawn (Cassi (36,8) r203 on rows every game), stand 5+ rounds next to a living pack 6/game on rows without hitting it (64% eventually do), and leave the far pack unvisited for 60-244 rounds; carriers tribute 21 rounds after capture (fine) except when something sends them wandering (`604a6cf6`: 60-76 rounds with 66 gems each, loops in the enemy half with nobody around).
6. **Recall rule = retreat at half hp.** 3,851 recall starts (25.7/game) at median 50% hp (48% below 50%), 28% with an enemy within 8, only 3% while being hit in that or the previous round, 16% while carrying gems, median 12 tiles from spawn. The opponents issue 83 starts/game at median 89% hp (23% below 50%), 21% carrying gems: for them recall is the teleport home with the bag (and it shows as 14% of their rounds vs the top-10), for us it is the hp trigger. 6% of our rounds are spent recalling (7% in losses).
7. **Idle in sight of the enemy**: 40% of our idle rounds have an enemy within 8 (opp 24%); corners 74%, collision 64%. A champion with nothing assigned stands still even with enemies next to it.

Differences from the opponents (same games):
- They come to us: 11.9 crossings/game (us 2.9), 8-11% of their rounds in our half from r50, 166 captures in our half (us 52 in theirs), squatting on our lanes clusters for 100-276 rounds; in our losses they are in our half 14.2 times/game at +72 score.
- They die less (3.9 vs 5.7/game, 9% vs 13% dead rounds), away from home (39% own half vs our 76%), less often outnumbered on the fight maps (corners 24% vs 56% of deaths), and their melee are a tile ahead of their casters (gap +0.54 vs +0.23; Mite +1.35).
- Their farm cycle on rows is faster on the nearest pack (23 vs 32 rounds after respawn) and they wait at the dead pack's tile (180 vs 92 champion-rounds/game) instead of elsewhere; 15% of their tributes are >40 rounds after capture (us 5%), i.e. they carry bigger loads but still outscore us by 1-3 packs.
- Their openings vary (13-21 patterns per map vs our 1-2).
- What is NOT different: spread (10.6 vs 11.5), cluster size (2.0 vs 2.1), alone share (29 vs 32%), idle share (9 vs 10%), action mix per type, time next to camps and altars. We are not slower or sloppier at the micro level of "what each champion does per round"; we are a home-only bot with no answer to being visited.

Appendix: full raw tables are in `$S/ws2/scripts_positions/q1_territory.out` (also the per-map rows of every table above), `q2_spread.out`, `q3_actions.out` (per type × win/loss × top-10), `q4_camps.out`, `q5_maps.out` (per-game lines), `q6_cycle.out`, `q7_deaths.out`, `q8_lanes.out`, `q9_opening.out`, `q10_determinism.out`, `q11_rows.out`, `q12_rowsgroups.out`; traces of the 21 example games in `traces/<match>.txt` (20-round steps, one line per round with every champion's tile, territory letter o/m/e, hp, gems and action).
