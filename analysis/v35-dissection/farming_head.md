# Our farm cycle and economy (v35, 150 games vs the top 30, 2026-10-15 11:33 UTC)

Data: 150 games of v35 ("Live Love Larp") from `$S/ws2/selected.json`, decoded every step (`$S/ws2/steps/*.c.jsonl`); 145 on side a, 5 on side b
(handled by the recorded side, not by assuming team 0). Opponent tiers: top-10 (50 games), 11-20 (50), 21-30 (45), other (5, rank 249).
Record: **59-91** (collision 12-7, expanse 11-6, interlock 7-6, monolith 5-8, elkring 5-9, corners 5-12, packs 7-14, rows 4-14, lanes 3-15;
vs top-10 10-40, 11-20 23-27, 21-30 21-24, other 5-0). Everything below compares us with the opponent **in the same games**, and with
the Mite reference numbers from `/mnt/project-files/analysis/mite-behind-the-scenes-2026-10-15` and `top2-dissection-2026-10-15`.
Scripts: `$S/ws2/scripts_farm/` (`common.py` loader, `extract.py` -> `out/<match>.json` with per-champion timelines for both teams,
`q1_econ.py` ... `q10_util.py`); the full tables each script printed are in the appendix (per map, win/loss, opponent tier).
"Champion-round" (cr) = one champion for one round; "nch" counts champions (Cassi and Issac are two champions).

Where a measured number matches a parameter of `bots/study25/src/params.h` the parameter is named: the v35 farm rules are those of study25
(`P_SHOP_RECALL 180`, `P_RECALL_PCT 55`, `P_CAPRECALL 2`, `P_NOGOLD 1`, `P_NE_POWER_OPEN 1`, `P_PAIR 2`), all confirmed by the replays.

## Short answer

1. **The farm engine itself keeps pace while alive**: captures per 100 champion-rounds alive 1.19 (us) vs 1.21 (opp), gems per capture 35.1 vs 35.5,
   damage per attacker-round equal or better, walking straighter (0.89 vs 0.84), fewer idle rounds (8.4% vs 9.6%), gold spent more completely
   (18 vs 58 gold left at the end). On expanse (0 deaths for both) the economy is a tie: 72.0 vs 70.3 captured gems/100cr, 11-6.
2. **We lose gems in four places, in this order of size** (per game, all 150 games; details in section 8):
   (a) time dead: 13.6% of champion-rounds vs 9.0% (5.7 vs 3.9 deaths/game) = 135 vs 94 gems not farmed per game, and in our 91 losses 9% of
   captured gems are dropped at death vs 2%; (b) shopping trips: 11.6 vs 8.4 recall-to-shop trips per game, 403 vs 327 champion-rounds per game,
   1143 of them started on the capture tile when walking to the altar was shorter (75 champion-rounds/game vs 31); (c) squad size: 1.16/1.51/2.03/2.57
   attackers by hp bucket vs Mite 2.0/2.05/2.4/3.5, hit-to-capture 16/22/24/21 rounds vs 12/17/21/23, and 2-3 champions on the first camp vs the
   opponents' 3-5, so our first capture comes 5-15 rounds later on 5 of 9 maps; (d) camps we leave to the opponent: the 108-gem elk+cluster on
   collision (opp 1.16 captures/game, us 0.05), the elk and the enemy-side clusters on lanes (opp +2.9 captures/game), the far wolves on corners.
3. **Not a problem**: walking efficiency, idle time, unspent gold, tribute interruptions (89 hit during the channel vs 174), bag size (median 44 both),
   altar passes (0.78/game vs 1.89), gems carried at the end (5% vs 4%).
4. **Our cycle is a fixed script** like Mite's: one draft per map (150/150), the same opening camp order in almost every game of a map (rows 18/18,
   monolith 13/13, expanse 16/17, lanes 16/18), a fixed own-side camp set (Jaccard between games 0.86-1.00 on 5 maps), no enemy-side farming
   (0.3 captures/game), no gold clusters, no monoliths.

## 1. Economy curve

Tributed gems at round marks (mean per map, us/opp, from the appendix Q1 table; games still running in brackets):

| map | n | r50 | r100 | r200 | r300 | r400 | r500 |
|---|---|---|---|---|---|---|---|
| collision | 19 | 17/5 | 49/37 | 149/92 | 245/184 | 371/280 | 480/382 |
| corners | 17 | 59/6 | 118/69 | 248/210 | 371/365 | 482/498 [15] | 541/613 [11] |
| elkring | 14 | 0/33 | 98/89 | 217/258 | 336/431 | 482/597 | 634/766 [13] |
| expanse | 17 | 48/29 | 207/176 | 488/427 | 758/734 | 942/931 [0] | - |
| interlock | 13 | 14/34 | 118/123 | 320/285 | 496/507 | 684/712 | 796/858 [4] |
| lanes | 18 | 24/16 | 140/146 | 370/409 | 626/705 | 803/955 [8] | 830/991 [1] |
| monolith | 13 | 0/7 | 151/92 | 323/316 | 566/525 | 780/816 [12] | 880/954 [1] |
| packs | 21 | 34/41 | 133/131 | 261/298 | 418/492 | 590/698 | 736/888 [10] |
| rows | 18 | 0/16 | 132/106 | 378/374 | 583/675 | 869/975 [10] | 891/1034 [0] |

- We are **ahead at r100 on collision, corners, expanse, monolith and rows** and behind from r150-250 on corners, elkring, lanes, packs and rows.
  On elkring the opponent leads from r50 (we bank our first gems after r50: first capture r25 but the altar is 14-17 tiles from the camps).
- **Round the game is decided** (last round at which the eventual winner was not ahead, +1): median 250 = 61% of the game; 30 games decided by r100
  (collision 9, corners 8, packs 4), 48 decided in the last 20% of the game. Expanse (92% of the game, 10.3 lead changes) and rows (86%, 4.2) are
  banking races to the end; collision (27%) and corners (30%) are decided by the first fights. Decided round is later in our wins (289) than in our
  losses (236): when we lose we lose early.
- **Rates** (us vs opp): captures/game 24.5 vs 26.7; captures per 100cr alive 1.19 vs 1.21; gems/capture 35.1 vs 35.5; captured gems/100cr 41.7 vs 43.1;
  tributed gems/100cr 39.2 vs 41.3; tributed per game 808 vs 907. Of all gems we obtain (captures + kills), **88% are tributed, 6% dropped at death,
  5% still carried at the end** (opp 90 / 6 / 4); 6% of both teams' gems come from kills.
- Wins vs losses: in wins we capture 45.5/100cr vs their 40.4 and lose 4% to deaths vs their 12%; in losses 38.9 vs 44.7 and we drop 9% vs their 2%.
  Against the top 10: 39.7 vs 46.8 per 100cr, 21.5 vs 26.8 captures/game, 6.3 vs 3.0 deaths/game.
- Per map the economy per alive round is equal on corners (30.7 vs 30.8), elkring (33.1 vs 33.1), interlock (42.5 vs 43.2), monolith (37.6 vs 39.4) and
  better for us on expanse (72.0 vs 70.3); it is worse on **rows (49.3 vs 54.2, 0 deaths on both sides)**, packs (49.3 vs 53.5) and lanes (41.4 vs 45.4).
  The rows gap is the cleanest farm-engine gap (section 8).
- Who farms: Issac 21% of our captured gems (230/champion-game), Ren 15% (226), Cassi 13% (136), Varg 12% (233), Vendetta 11% (216), Ryth 10% (164),
  Stellar 10% (149), Tavi 6% (102), Prism 3% (113).

## 2. Draft and shop

**Draft is fixed per map (150/150, one draft per map)**: collision and packs C&I > Ren > Stellar (12-7, 7-14); corners and elkring
Ryth > Stellar > Prism > Ren > Tavi (5-12, 5-9: yesterday's Univardisty caster table, `P_DRAFTUNI 2`); expanse Vendetta > Varg > C&I (11-6);
interlock C&I > Ren > Stellar > Tavi (7-6); lanes and monolith Vendetta > Varg > C&I > Ryth > Tavi (3-15, 5-8); rows Vendetta > Varg > C&I > Ryth (4-14).
Pool: C&I 119 champion-games, Ren 84, Stellar 84, Ryth 80, Tavi 75, Vendetta 66, Varg 66, Prism 31; first pick Vendetta 66, C&I 53, Ryth 31.
Opponents drafted against us: C&I 128, Stellar 107, Varg 79, Ren 74, Tavi 63, Vendetta 59, Ryth 58, Prism 16, Willow 13; first pick C&I 45, Varg 44,
Stellar 22. On rows every opponent plays the same melee core as us (Varg/Vendetta/C&I); on packs Varg > Stellar > C&I beat us 2 of 3 and
Stellar > Tavi > C&I 2 of 2; on corners the mirror of our own draft beat us 2 of 2.

**Shop** (purchases = `k13` steps, items from the engine summary; we buy one shard per step, so "buys" counts shards):

| type | n | shard families bought (total shards) | emblems/g | 1st buy r | trips/g | gap | % dead | % spawn | % field | earned | spent | gold end | trips ending at 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Varg | 66 | power_str 1020, durability_str 295, jungle_str 245, bruiser_hp 173 | 4.86 | 42 | 4.2 | 64 | 1% | 99% | 0% | 809 | 793 | 16 | 90% |
| Ren | 84 | power_focus 1832, durability_hp 333 | 4.75 | 68 | 6.3 | 63 | 3% | 97% | 0% | 814 | 786 | 27 | 58% |
| Issac | 119 | power_str 2138, jungle_str 373 | 3.83 | 84 | 5.0 | 68 | 5% | 95% | 0% | 657 | 639 | 18 | 77% |
| Ryth | 80 | power_str 784, durability_str 325, jungle_str 284, bruiser_hp 203 | 3.59 | 99 | 3.7 | 89 | 2% | 98% | 0% | 631 | 608 | 23 | 53% |
| Vendetta | 66 | power_str 538, durability_str 271, jungle_str 249, bruiser_hp 231 | 3.53 | 122 | 3.9 | 67 | 1% | 99% | 0% | 611 | 593 | 18 | 86% |
| Stellar | 84 | power_focus 1151, durability_hp 269 | 2.99 | 120 | 4.5 | 80 | 9% | 91% | 0% | 547 | 519 | 28 | 45% |
| Prism | 31 | power_focus 292, durability_hp 87 | 2.10 | 66 | 3.8 | 108 | 6% | 94% | 0% | 392 | 379 | 13 | 20% |
| Cassi | 119 | power_focus 698, durability_hp 281 | 1.17 | 178 | 2.5 | 93 | 12% | 88% | 0% | 265 | 250 | 15 | 74% |
| Tavi | 75 | power_focus 388, bruiser_focus 150 | 1.12 | 130 | 3.2 | 84 | 0% | 67% | 33% | 224 | 220 | 4 | 59% |

- Build order (source `P_NE_POWER_OPEN 1`, confirmed by the family shares: Varg has a full power emblem in 95% of games, durability 81%, jungle 69%,
  bruiser 46%): melee = **power(str) x5 -> durability(str) x5 -> jungle(str) x5 -> bruiser health x5 -> power forever**; Issac = power x10 -> jungle -> power;
  Cassi/Stellar/Prism/Ren = power(focus) x5 -> durability health x5 -> power forever; Tavi = power focus -> bruiser focus. We never buy monster, treasure or home.
  Mite's order is jungle -> durability -> bruiser -> power (safety first); 25-64% of the opponents' melee champions buy a **monster** emblem (Vendetta 64%,
  Varg 41%, Issac 36%) which we never do.
- Sequences are the same in every game of a map (deterministic): Varg `r36:270 | r143:270HHH | r204:270HH` x16, Issac `r84:90 | r183:90 | r268:90` x15,
  Ryth `r65:270 | r284:270HHH` x15, Cassi `r184:90` x15 or `r315:270HHHH` x15, Tavi no purchase at all in 16 of 75 games, Ren none in 6 of 84.
- Timing: first purchase at r42 (Varg) to r178 (Cassi); trips every 63-108 rounds; 88-99% bought alive on spawn, 1-12% while dead (Cassi 12%, Stellar 9%),
  Tavi 33% in the field (opponents' Tavi 82% in the field and 501 gold/game vs our 224). Gold left at the end: median 0, mean 18 per champion, 10% of
  champion-games end with >= 90 gold and 4% with >= 150 (an unbought emblem); opponents 58 mean, 25% and 14%. **We out-spend every opponent tier**.
- Team gold per game (us vs opp): collision 3282/3393, corners 662/1670, elkring 4935/5475, expanse 1475/1235, interlock 2118/1852, lanes 1192/1321,
  monolith 3936/4251, packs 2670/3458, rows 4061/4442. Corners is gold starvation (27% of champion-rounds dead), packs and rows are fewer captures.

## 3. Camp choice

- **Territory**: 19.8 own / 4.4 mid / 0.3 enemy captures per game (opp 21.2 / 4.4 / 1.1). Enemy-side captures only on elkring (1.2/game: the two
  enemy elks nearest the middle), monolith (1.2: the enemy 2700-hp wolf nearest our altar) and lanes (0.9). No gold-only cluster is ever taken by anyone
  (0 in 150 games, `P_NOGOLD 1`), no monolith.
- **Set stability** (groups taken in >= 80% of games / mean distinct groups per game / Jaccard between games): collision 4 / 4.6 / 0.86, corners 3 / 3.7 / 0.63,
  elkring 5 / 5.6 / 0.79, expanse 9 / 8.7 / 0.94, interlock 4 / 4.9 / 0.80, lanes 10 / 12.8 / 0.72, monolith 7 / 7.6 / 0.92, packs 4 / 3.8 / 0.88, rows 3 / 3.0 / 1.00.
  Opponents (30 different teams pooled) 0.45-1.00. Our set is as fixed as Mite's (Mite: 3 of 9 on rows, 7 of 30 on expanse, 12 of 42 on lanes; ours 3, 9, 10-14).
- **Opening order is a script**: rows `0o-1o-0o-1o-2o` in 18/18 games, monolith `3o-2o-9o-4o-1o` 13/13, expanse `1o-11o-0o-2o-10o` 16/17, lanes `5o-18o-4o-6o-19o`
  16/18, interlock `3o-4o-0o-5o-3o` 11/13, elkring `0o-1o-2o-4o-0o` 6/14, collision `3m-3m-...` (the centre wolf first, twice) 19/19. First capture at r19-41
  (monolith 19, interlock 20, elkring 25, expanse 30, collision 33, packs 33, rows 36, lanes 40, corners 41), 5-15 rounds later than the opponent on collision
  (33 vs 18), corners (41 vs 31), elkring (25 vs 18), packs (33 vs 26), rows (36 vs 31).
- **Nearest camp that is up** (from the champion's last capture/tribute/arrival point, among gem groups up at that moment): chosen in 44% of our 3676 captures,
  1st or 2nd nearest in 68%, mean extra distance 4.5 tiles (opp 52%, 72%, 3.9; Mite 38%, Univardisty 41% in the earlier study). The choice is a score
  (`gems / rounds` with squad, bank-trip and hysteresis terms, `P_STICK 125`), not "nearest up", and it matches the opponents' choices as often as it differs.
  Lowest on expanse (29%: the bank-trip term pulls to the altar-side clusters) and lanes (34%).
- **Revisits**: median 33 rounds after a group respawns (mean 44) vs 32 (46) for the opponents and 25-45 for Mite; interlock 23, rows 22, monolith 46.
  Camp utilization on our farmed own-side groups (appendix Q10): rows 55% respawning / 25% up-and-untouched / 20% under attack vs opp 60 / 19 / 21,
  collision 47 / 43 / 10 (3 groups) vs 32 / 61 / 7 (5 groups). We do not leave camps standing more than the opponents do; we clear fewer of them.
- **Camps the opponents farm and we never touch** (own-view sides; captures/game us vs opp): collision elk+cluster `9o` (108 gems, 3900 hp, 30 tiles from spawn)
  0.05 vs 1.16, elks `7o`/`8o` 0.53/0.00 vs 1.32/0.32; corners wolves `6o`/`7o` (22 gems, 25-27 tiles) 0 vs 0.65/0.53 and elk `12o` 0.18 vs 0.71; lanes own elk `17o`
  0.06 vs 0.94, middle wolves `15m`/`16m` 0.06/0.11 vs 1.06/0.67, enemy clusters `18e`/`19e`/`20e` 0 vs 0.67/0.72/0.56. The reverse (we farm, they do not):
  lanes enemy wolf `11e` 0.56 vs 0.17, collision centre wolf `3m` 11.6 vs 5.1 (we hold the centre camp on collision, 12-7).

## 4. Squad size and kill speed (stack2 logic, both teams, 3676 + 4003 captures)

| group hp | us attackers | us hit->capture (med) | us dmg/attacker/round | opp attackers | opp hit->capture | opp dmg/att/round | Mite attackers | Mite hit->capture |
|---|---|---|---|---|---|---|---|---|
| < 800 | 1.16 | 16 | 29 | 1.44 | 15 | 29 | 2.0 | 12 |
| 800-1500 | 1.51 | 22 | 44 | 1.82 | 22 | 38 | 2.05 | 17 |
| 1500-3000 | 2.03 | 24 | 50 | 2.27 | 23 | 50 | 2.4 | 21 |
| >= 3000 | 2.57 | 21 | 79 | 2.69 | 22 | 68 | 3.5 | 23 |
| first 50 rounds | 1.85 | 19 | 38 | 2.73 | 17 | 33 | 3.2 | 15 |

- Attackers by count on 800-1500 hp groups: 1 attacker in 1067 of 1789 captures (60%), 2 in 576, 3+ in 146; opponents 891 / 550 / 363 (49% single).
  On >= 3000 hp: 3 attackers in 171 of 301, 4 in 18, never 5; opponents 128 / 66 / 16. `P_PAIR 2` gives a pair on gem groups, but the pair is often not formed.
- Damage per attacker-round is the same or higher than the opponents' (and than Mite's 23/42/48/51 of the earlier study): the micro is not the gap, the number of
  champions on the camp is. At the capture tick only 1.3-2.0 of ours are within 4 tiles (same as the opponents): the helpers leave for the next camp.
- Whole team on the first camp: opponents 3.1 (collision), 3.6 (corners), 5.0 (elkring), 4.7 (rows), 3.2 (interlock); us 2.0, 2.5, 3.0, 3.0, 2.0. Our first
  capture is 5-15 rounds later on those maps (section 3).
- By result: in losses we use 1.89 attackers on >= 800 hp groups vs the opponents' 2.18; in wins 1.68 vs 1.92. Against the top 10: 1.81 vs 2.17.
- **Aggro**: the champion taking most monster damage in a capture is Issac (558 captures), Ren (495), Vendetta (326), Varg (275), Cassi (274), Ryth (267), Stellar (238).
  Monster damage taken per champion-game: Ren 2371, Ryth 1964, Vendetta 1918, Issac 1744, Varg 1453, Stellar 1105, Tavi 866, Cassi 808 (opp Varg takes 1127: their
  Varg buys monster/jungle emblems; ours takes 1453).
- **Ranged attack from 3+**: Cassi 96% of camp basic attacks at distance >= 3, Tavi 93%, Prism 91%, Stellar 89%; Varg 86% at 1 and 14% at 2; melee 100% at 1.
  Because only champions on the group's tiles are paid, **our ranged helpers get no gems and no gold in 53% (Cassi), 60% (Stellar), 66% (Tavi), 66% (Prism) of the
  group kills they help with** (opponents 71 / 61 / 62 / 69%: same engine rule, same habit). On rows our Cassi walks 225 rounds with 0 gems and 0 gold in every game
  (0.9 credited captures/game, 18% idle; opp Cassi 1.6).

## 5. Bags and tributes

| | us | opp | Mite (ref) |
|---|---|---|---|
| tribute starts / completed (150 games) | 3256 / 3057 (20.4 per game, 0.99 per 100cr) | 3306 / 3056 (20.4, 0.93) | 22 per game |
| bag at completion: median / mean / p90 | 44 / 40 / 66 | 44 / 45 / 70 | 36 / - / 70 |
| bags <= 10 / >= 100 | 0% / 1% | 0% / 2% | 0% |
| bag distribution 11-22 / 23-44 / 45-66 / 67-100 / >100 | 802 / 1303 / 811 / 107 / 34 | 568 / 1290 / 864 / 263 / 71 | |
| captures per bag | 1.09 | 1.22 | 1 trip per 2 camps on rows (ref) |
| age of the oldest / newest gems at the start (median rounds) | 11 / 10 | 12 / 10 | |
| starts not completed | 199 (6%): died 24, hit during the channel 89, moved 4, restart after a move 82 | 250 (8%): 26 / 174 / 14 / 36 | 3% |
| altar passes with >= 10 gems and no tribute | 117 (0.78 per game) | 284 (1.89) | |
| captures followed by a recall start within [-5,+3] rounds | 1837 (50%) | 1029 (26%) | |
| ... where 5 + spawn->altar < walk to altar | 378 of 685 (55%) | 329 of 694 (47%) | 53/53 on rows |
| ... where walking is shorter | 1459 of 2991 (49%) | 700 of 3309 (21%) | |

- **One camp, one tribute**: the bag is the camp's gem value (22 / 44 / 66 modes; captures per bag 1.09) and it is banked within ~11 rounds (`P_TRIBUTE_GEMS 12`).
  Opponents chain two camps more often (bags over 66 gems: 334 vs 141 of ~3057). Per map: rows bag 66 = one 4050-hp wolf camp, both teams; collision 22 both;
  corners 48 both.
- The 82 "restart" cases are a tribute started in the same round as a move, ignored by the engine and restarted 1-3 rounds later (1-3 rounds lost each, not an
  interruption). Real interruptions (hit while channelling, 89) are half the opponents' (174) and concentrated on corners (47 uncompleted of 269 starts, 17%).
- **Recall as a teleport**: on rows we recall right after a capture in 92% of captures, and in 178 of the 179 captures where "5 + spawn->altar" beats walking (99%,
  the Mite rule, which they do 85%); on packs 112 of 220 (51% vs 45%). But on the maps where walking is always shorter we recall after the capture anyway:
  elkring 285 of 333 captures (86% vs 27%), monolith 287 of 344 (83% vs 31%), interlock 222 of 357 (62% vs 12%), expanse 211 of 376 (56% vs 15%). These are
  not teleports: classifying every arrived recall by hp at start, gold at arrival (snapshot + purchases that round) and what happens next gives
  **shop trips 1692 (48%), heals (hp < 50%) 1625 (46%)**, gems-home-then-altar 43 (1%), no visible reason 144 (4%); opponents heal 57%, shop 37%.
  Gold spent per shop trip: median 180 both (`P_SHOP_RECALL 180`); 150-239 in 48% of our trips, 90-149 in 32% (opp 17%). Median hp at a recall start 0.53 (`P_RECALL_PCT 55`).
- Recall starts: 24.8 per game vs 23.1; 186 interrupted or died (5%) vs 198; 67% of arrivals are followed by a purchase within 2 rounds (opp 64%).

## 6. Lost time

Share of champion-rounds (all 150 games; 357,905 champion-rounds for us, 362,535 for the opponents):

| | walk | at a camp (hitting) | fighting | tributing | recalling | shopping | idle (alive, no action) | dead |
|---|---|---|---|---|---|---|---|---|
| us | 46.4% | 19.3% | 2.1% | 4.2% | 5.3% | 0.7% | 8.4% | **13.6%** |
| opp | 47.6% | 18.8% | 2.0% | 4.7% | 7.3% | 0.7% | 9.6% | 9.0% |

- Dead: corners 27.1% vs 12.7% (13.5 vs 7.1 deaths/game), collision 22.3% vs 16.8% (11.3 vs 8.5), packs 18.8% vs 10.6% (7.0 vs 3.8), lanes 9.3% vs 3.1%
  (3.8 vs 1.4), elkring 12.5% vs 13.9% (6.5 vs 8.1, the one fight map where we die less), expanse and rows 0. In losses 17.1% vs 6.0%; vs the top 10 15.9% vs 7.7%.
  Respawn cost at 60 rounds per death: 48,542 rounds dead (324 per game) = 135 gems per game not farmed at our own rate of 0.42 gems per alive round,
  vs 94 for the opponents; gems dropped at death 58 vs 56 per game (equal: we take back as much as we lose).
- Walking efficiency (moves between purpose points vs shortest path): **0.89, 1.9 extra moves per leg** (opp 0.84 / 2.6; Mite 0.75 / 4.0; study25 0.80 / 3.5).
  Per map 0.87-1.07 except corners 0.70 (fights) and rows 0.74 (7.0 extra per leg): the rows figure is Cassi's 152-move "legs" with no purpose point because she is
  never credited, not detours; dashes make expanse > 1. We do not walk in circles.
- Idle 8.4% vs 9.6%; per type Cassi 11.6%, Stellar 11.3%, Tavi 11.1%, Issac 10.2% (ranged champions waiting at range), Varg 6.1%. Not a gap.
- Recall channel 5.3% vs 7.3% but our shop trips are more numerous (11.6 vs 8.4 per game) and start before the tribute: rounds from recall start to the next capture
  or tribute, median 29 vs 31, total **403 vs 327 champion-rounds per game** (elkring 944 vs 704, interlock 570 vs 157, monolith 661 vs 477, collision 566 vs 468;
  packs and rows equal).

## 7. Observed rules of our farm cycle (each measured over 150 games)

1. Draft: one fixed list per map (150/150); caster table on the 4 short-path maps, Vendetta > Varg > C&I melee core on the farm maps.
2. Camp set: own-side gem groups only (19.8 own / 4.4 mid / 0.3 enemy captures per game), no gold clusters (0), no monoliths (0); the same set every game
   (Jaccard 0.86-1.00 on collision, expanse, monolith, packs, rows) and the same opening sequence (rows 18/18, monolith 13/13, expanse 16/17, lanes 16/18).
3. Next camp: a score, not nearest-up (nearest chosen 44%, 1st/2nd nearest 68%, mean 4.5 extra tiles); hysteresis keeps the target; revisit 33 rounds after respawn.
4. Squad: 1 attacker under 800 hp (84% single), 1-2 on 800-1500 (60% single), 2 on 1500-3000 (49% pairs), 3 on >= 3000 (57% triples); 2-3 on the first camp.
   Ranged champions hit from 3+ (89-96%) and stand off the capture tiles (53-66% of their kills unpaid).
5. Capture -> tribute: bank each camp's gems at once (1.09 captures per bag, bag = camp value, oldest gems 11 rounds old), at the nearest altar, never walk past one
   with gems (0.78 passes/game), never bank <= 10.
6. Capture -> recall: start the recall on the capture tiles (`P_CAPRECALL 2`) when hp < 55% (46% of recalls) or when the camp's gold brings the purse to >= 180
   (48%; median 180 spent); on rows also when recall + home->altar is shorter (99%). Result: a recall after 50% of all captures, 86% on elkring, 83% on monolith.
7. Shop: on spawn, alive (88-99%), buy down to 0 gold (74-90% of trips end at 0; 18 gold left at the end); melee power x5 -> durability -> jungle -> bruiser health -> power,
   casters power focus -> durability health -> power; never monster, treasure or home; Tavi mostly never buys (16/75 games with no purchase).

## 8. Differences from the opponents and from Mite that cost the most gems

Ranked by the estimated gems per game, each with its count (our rate of 0.42 gems per alive champion-round is used to convert time):

| # | difference | count | estimated cost |
|---|---|---|---|
| 1 | **Time dead**: 5.7 vs 3.9 deaths/game, 13.6% vs 9.0% of champion-rounds dead (corners 27%, collision 22%, packs 19%, lanes 9%) | 858 deaths vs 581; 48,542 rounds dead vs 32,789 | 135 vs 94 gems/game not farmed (**+41 gems/game** over all games); in the 91 losses also 69 vs 26 gems/game dropped at death (+43), so ~85 gems/game in losses; corners 27% dead = 230 deaths in 17 games |
| 2 | **Shop recalls from the capture tile**: recall to shop at 180 gold before tributing, 11.6 vs 8.4 trips/game; 1143 of them where walking to the altar was shorter (opp 542) | 1692 shop recalls vs 1218; 403 vs 327 champion-rounds/game in shop trips | +76 champion-rounds/game = **32 gems/game**; elkring +240 cr (100 gems), interlock +413 cr (170), monolith +184 cr (77), collision +98 cr |
| 3 | **Squad size / first camp**: 1.16/1.51/2.03/2.57 attackers vs Mite 2.0/2.05/2.4/3.5, hit-to-capture 16/22/24 vs 12/17/21 on < 3000 hp; 2-3 on the first camp vs 3-5 | 1067 single-attacker captures on 800-1500 hp (60% vs 49%); first capture 5-15 rounds later on 5 maps | fewer captures where no one dies: packs 18.0 vs 21.8 (-3.8 x 45 = **170 gems/game**), rows 15.8 vs 17.2 (-92), lanes 37.9 vs 42.5 (-110); first capture delay ~10 rounds x nch x 0.42 = 20 gems/game |
| 4 | **Camps left to the opponent**: collision elk+cluster 9o (108 gems), lanes elk 17o + middle 15m/16m + enemy clusters 18e-20e, corners far wolves 6o/7o and elk 12o | opp captures/game on those groups: collision 1.16 + 1.32 + 0.32, lanes 0.94 + 1.06 + 0.67 + 0.67 + 0.72 + 0.56, corners 0.65 + 0.53 + 0.71; ours 0.05-0.18 | collision ~125 gems/game of 9o alone (we still win collision 12-7 by holding the centre wolf), lanes ~100, corners ~50 |
| 5 | **Ranged helpers unpaid**: Cassi/Stellar/Tavi/Prism off the capture tiles | 523 / 547 / 475 / 159 unpaid kills (53-66%); Tavi 224 gold/game vs opp Tavi 501, 1.1 vs 2.7 emblems | no direct gem loss (the tile champion is paid) but our casters stay under-itemized: Cassi 1.2 emblems/game, Tavi 1.1; opponents' Tavi shops in the field (82% of buys) |
| 6 | One camp per tribute (1.09 vs 1.22 captures per bag; bags over 66 gems 141 vs 334) | ~1.3 extra tribute trips per game | ~1.3 trips x ~13 rounds = 17 cr/game = **7 gems/game**; on rows Mite banks 1 trip per 2 camps (ref), we never do (0 bags >= 100 in 239) |
| 7 | Tribute restarts after a move in the same round | 82 wasted starts, 1-3 rounds each | < 1 gem/game |
| 8 | Build order: power before jungle/durability (Mite jungle -> durability first; opponents buy monster emblems in 25-64% of melee games) | monster damage taken per game: our Varg 1453 vs opp Varg 1127, our Ren 2371 vs 1906 | more heal recalls (1625, 46% of recalls); not quantified in gems |

Not costs (we are equal or better): walking efficiency 0.89 vs 0.84; idle 8.4% vs 9.6%; unspent gold 18 vs 58; tribute interruptions 89 vs 174; altar passes 0.78 vs 1.89
per game; gems carried at the end 5% vs 4%; gems per capture 35.1 vs 35.5; damage per attacker-round equal or higher in every hp bucket; camp utilization equal.

**Rows, the pure farm race we lose 4-14 with 0 deaths**: same 3-camp set, same bag (66), same hit-to-capture (21), same walking share; the opponent gets
4.7 champions on the first camp (r31 vs r36), 2.88 vs 2.66 attackers afterwards, chains two camps in 8% of bags (0% for us), recalls to shop after the
tribute instead of before it, and keeps a steady 2.1-2.5 captures per 50 rounds while ours come in bursts (1.0 / 1.0 / 3.0 / 1.9 / 1.0 / 2.0 / 3.7 per
50-round bin, identical in all 18 games): captures 15.8 vs 17.2, tributed 891 vs 1034, 95 vs 51 gems still in hand when the game ends. The fix that
touches all of this is the squad rule (2 per camp, everyone on the first camp) plus "tribute, then recall to shop".

---
# Appendix: full tables (script output)
