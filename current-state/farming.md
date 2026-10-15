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

## Q1 Economy

games 150, W-L 59-91; by map: {'collision': '12-7', 'corners': '5-12', 'elkring': '5-9', 'expanse': '11-6', 'interlock': '7-6', 'lanes': '3-15', 'monolith': '5-8', 'packs': '7-14', 'rows': '4-14'}
by opp tier: {'top10': '10-40', '11-20': '23-27', '21-30': '21-24', 'other': '5-0'}

### Tributed gems at round marks (mean over games of the map; us / opp); games still running at that mark in brackets

| map | n | mean rounds | r50 | r100 | r150 | r200 | r250 | r300 | r400 | r500 | r700 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 742 | 17/5 [19] | 49/37 [19] | 93/71 [19] | 149/92 [19] | 193/147 [19] | 245/184 [19] | 371/280 [19] | 480/382 [19] | 657/567 [9] |
| corners | 17 | 565 | 59/6 [17] | 118/69 [17] | 194/126 [17] | 248/210 [17] | 313/287 [17] | 371/365 [17] | 482/498 [15] | 541/613 [11] | 591/787 [4] |
| elkring | 14 | 591 | 0/33 [14] | 98/89 [14] | 141/194 [14] | 217/258 [14] | 271/356 [14] | 336/431 [14] | 482/597 [14] | 634/766 [13] | 762/924 [0] |
| expanse | 17 | 349 | 48/29 [17] | 207/176 [17] | 292/302 [17] | 488/427 [17] | 598/600 [17] | 758/734 [17] | 942/931 [0] | 942/931 [0] | 942/931 [0] |
| interlock | 13 | 479 | 14/34 [13] | 118/123 [13] | 228/211 [13] | 320/285 [13] | 410/397 [13] | 496/507 [13] | 684/712 [13] | 796/858 [4] | 824/878 [0] |
| lanes | 18 | 398 | 24/16 [18] | 140/146 [18] | 281/274 [18] | 370/409 [18] | 487/566 [18] | 626/705 [18] | 803/955 [8] | 830/991 [1] | 839/998 [0] |
| monolith | 13 | 448 | 0/7 [13] | 151/92 [13] | 222/204 [13] | 323/316 [13] | 434/423 [13] | 566/525 [13] | 780/816 [12] | 880/954 [1] | 884/957 [0] |
| packs | 21 | 506 | 34/41 [21] | 133/131 [21] | 197/212 [21] | 261/298 [21] | 335/391 [21] | 418/492 [21] | 590/698 [21] | 736/888 [10] | 781/943 [0] |
| rows | 18 | 402 | 0/16 [18] | 132/106 [18] | 253/238 [18] | 378/374 [18] | 506/534 [18] | 583/675 [18] | 869/975 [10] | 891/1034 [0] | 891/1034 [0] |

### Round the game is decided (last round at which the eventual winner was not ahead, +1) and lead changes

| split | n | decided round med | mean | med % of game | lead changes/game | decided by r100 | decided in last 20% |
|---|---|---|---|---|---|---|---|
| all | 150 | 250 | 278 | 61% | 4.67 | 30 | 48 |
| map collision | 19 | 142 | 301 | 27% | 1.84 | 9 | 3 |
| map corners | 17 | 123 | 253 | 30% | 0.88 | 8 | 3 |
| map elkring | 14 | 239 | 306 | 36% | 3.07 | 2 | 4 |
| map expanse | 17 | 324 | 299 | 92% | 10.29 | 0 | 12 |
| map interlock | 13 | 221 | 229 | 44% | 4.62 | 3 | 2 |
| map lanes | 18 | 242 | 264 | 69% | 6.39 | 3 | 7 |
| map monolith | 13 | 304 | 308 | 68% | 6.69 | 1 | 5 |
| map packs | 21 | 190 | 222 | 41% | 4.52 | 4 | 1 |
| map rows | 18 | 342 | 326 | 86% | 4.17 | 0 | 11 |
| win | 59 | 289 | 292 | 65% | 5.47 | 11 | 23 |
| loss | 91 | 236 | 268 | 61% | 4.14 | 19 | 25 |
| opp top10 | 50 | 230 | 236 | 55% | 4.22 | 11 | 13 |
| opp 11-20 | 50 | 308 | 317 | 69% | 5.08 | 8 | 19 |
| opp 21-30 | 45 | 269 | 293 | 56% | 4.91 | 9 | 16 |
| opp other | 5 | 142 | 159 | 27% | 2.80 | 2 | 0 |

### Farm rates per team (us vs opponent in the same games)

| split | team | n | captures/game | captures/100 champ-rounds alive | gems/capture | captured gems/100cr | tributed gems/100cr | tributed/game | % tributed | % lost at death | % carried at end | % of gems from kills | deaths/game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 150 | 24.5 | 1.19 | 35.1 | 41.7 | 39.2 | 808 | 88% | 6% | 5% | 6% | 5.7 |
| all | opp | 150 | 26.7 | 1.21 | 35.5 | 43.1 | 41.3 | 907 | 90% | 6% | 4% | 6% | 3.9 |
| map collision | us | 19 | 32.6 | 1.41 | 22.4 | 31.5 | 33.5 | 774 | 83% | 14% | 3% | 22% | 11.3 |
| map collision | opp | 19 | 29.7 | 1.27 | 26.6 | 33.8 | 28.8 | 674 | 74% | 22% | 4% | 14% | 8.5 |
| map corners | us | 17 | 15.0 | 0.73 | 42.2 | 30.7 | 28.9 | 595 | 82% | 15% | 2% | 12% | 13.5 |
| map corners | opp | 17 | 22.5 | 0.80 | 38.7 | 30.8 | 29.6 | 837 | 85% | 9% | 5% | 11% | 7.1 |
| map elkring | us | 14 | 23.8 | 0.92 | 36.0 | 33.1 | 29.5 | 762 | 83% | 11% | 6% | 7% | 6.5 |
| map elkring | opp | 14 | 27.1 | 0.95 | 35.0 | 33.1 | 32.3 | 924 | 88% | 7% | 4% | 9% | 8.1 |
| map expanse | us | 17 | 24.9 | 1.78 | 40.4 | 72.0 | 67.3 | 942 | 93% | 0% | 7% | 0% | 0.0 |
| map expanse | opp | 17 | 24.6 | 1.77 | 39.8 | 70.3 | 66.7 | 931 | 95% | 0% | 5% | 0% | 0.1 |
| map interlock | us | 13 | 27.5 | 1.26 | 33.7 | 42.5 | 37.9 | 824 | 83% | 11% | 6% | 7% | 4.3 |
| map interlock | opp | 13 | 24.7 | 1.20 | 36.0 | 43.2 | 42.6 | 878 | 88% | 7% | 5% | 11% | 3.2 |
| map lanes | us | 18 | 37.9 | 1.75 | 23.7 | 41.4 | 38.7 | 839 | 92% | 2% | 6% | 1% | 3.8 |
| map lanes | opp | 18 | 42.5 | 1.87 | 24.2 | 45.4 | 44.0 | 998 | 95% | 1% | 3% | 2% | 1.4 |
| map monolith | us | 13 | 26.5 | 1.06 | 35.4 | 37.6 | 35.5 | 884 | 91% | 5% | 4% | 4% | 3.8 |
| map monolith | opp | 13 | 31.0 | 1.23 | 32.1 | 39.4 | 37.9 | 957 | 92% | 4% | 4% | 5% | 2.5 |
| map packs | us | 21 | 18.0 | 1.09 | 45.1 | 49.3 | 47.5 | 781 | 94% | 3% | 2% | 2% | 7.0 |
| map packs | opp | 21 | 21.8 | 1.23 | 43.4 | 53.5 | 53.3 | 943 | 97% | 2% | 1% | 3% | 3.8 |
| map rows | us | 18 | 15.8 | 0.79 | 62.5 | 49.3 | 44.4 | 891 | 90% | 0% | 10% | 0% | 0.1 |
| map rows | opp | 18 | 17.2 | 0.86 | 62.8 | 54.2 | 51.9 | 1034 | 95% | 0% | 5% | 0% | 0.3 |
| win | us | 59 | 29.1 | 1.33 | 34.3 | 45.5 | 46.4 | 1018 | 92% | 4% | 4% | 9% | 3.3 |
| win | opp | 59 | 24.4 | 1.17 | 34.7 | 40.4 | 34.8 | 727 | 82% | 12% | 6% | 5% | 6.0 |
| loss | us | 91 | 21.5 | 1.09 | 35.7 | 38.9 | 34.0 | 673 | 85% | 9% | 7% | 3% | 7.3 |
| loss | opp | 91 | 28.2 | 1.24 | 36.0 | 44.7 | 45.1 | 1024 | 95% | 2% | 3% | 6% | 2.5 |
| opp top10 | us | 50 | 21.5 | 1.14 | 34.9 | 39.7 | 35.8 | 676 | 86% | 8% | 6% | 5% | 6.3 |
| opp top10 | opp | 50 | 26.8 | 1.29 | 36.3 | 46.8 | 46.4 | 964 | 93% | 4% | 3% | 6% | 3.0 |
| opp 11-20 | us | 50 | 26.4 | 1.25 | 34.4 | 42.8 | 40.8 | 865 | 89% | 6% | 5% | 7% | 5.5 |
| opp 11-20 | opp | 50 | 27.2 | 1.25 | 35.4 | 44.2 | 41.9 | 913 | 89% | 7% | 4% | 6% | 4.1 |
| opp 21-30 | us | 45 | 25.3 | 1.15 | 36.1 | 41.4 | 39.4 | 869 | 89% | 6% | 5% | 6% | 5.9 |
| opp 21-30 | opp | 45 | 26.9 | 1.13 | 35.0 | 39.6 | 37.2 | 884 | 89% | 6% | 5% | 6% | 4.7 |
| opp other | us | 5 | 28.4 | 1.47 | 34.4 | 50.6 | 53.2 | 1026 | 98% | 1% | 2% | 7% | 0.4 |
| opp other | opp | 5 | 18.8 | 0.94 | 32.1 | 30.3 | 24.4 | 487 | 79% | 12% | 9% | 1% | 2.6 |

### Who farms: share of our captured gems by champion type (all games)

| type | champion-games | captured gems | share | gems/champion-game |
|---|---|---|---|---|
| Issac | 119 | 27381 | 21% | 230 |
| Ren | 84 | 19006 | 15% | 226 |
| Cassi | 119 | 16134 | 13% | 136 |
| Varg | 66 | 15390 | 12% | 233 |
| Vendetta | 66 | 14273 | 11% | 216 |
| Ryth | 80 | 13092 | 10% | 164 |
| Stellar | 84 | 12480 | 10% | 149 |
| Tavi | 75 | 7638 | 6% | 102 |
| Prism | 31 | 3512 | 3% | 113 |


## Q2 Draft and shop

### Our draft per map (pick order) and record; opponent drafts seen against us

**collision** (19 games, nch 4):
- us: cassi_issac > ren > stellar x19 (12-7)
- opp: cassi_issac > stellar > ren x3 (opp won 1)
- opp: stellar > ren > tavi x2 (opp won 2)
- opp: vendetta > varg > cassi_issac x1 (opp won 0)
- opp: stellar > cassi_issac > ren x1 (opp won 0)
- opp: cassi_issac > ren > stellar x1 (opp won 1)
- opp: cassi_issac > ryth > ren x1 (opp won 0)

**corners** (17 games, nch 5):
- us: ryth > stellar > prism > ren > tavi x17 (5-12)
- opp: ryth > stellar > prism > ren > tavi x2 (opp won 2)
- opp: ren > stellar > cassi_issac > ryth > varg x1 (opp won 1)
- opp: varg > ryth > willow > stellar > tavi x1 (opp won 0)
- opp: stellar > cassi_issac > ren > marcella > ryth x1 (opp won 0)
- opp: vendetta > cassi_issac > varg > ryth > tavi x1 (opp won 0)
- opp: cassi_issac > vendetta > ryth > stellar > tavi x1 (opp won 0)

**elkring** (14 games, nch 5):
- us: ryth > stellar > prism > ren > tavi x14 (5-9)
- opp: stellar > prism > willow > ren > tavi x2 (opp won 2)
- opp: varg > stellar > cassi_issac > tavi > ren x2 (opp won 1)
- opp: varg > stellar > cassi_issac > ryth > ren x1 (opp won 1)
- opp: vendetta > cassi_issac > varg > ryth > tavi x1 (opp won 0)
- opp: ryth > stellar > prism > ren > tavi x1 (opp won 1)
- opp: vendetta > varg > cassi_issac > ryth > ren x1 (opp won 1)

**expanse** (17 games, nch 4):
- us: vendetta > varg > cassi_issac x17 (11-6)
- opp: varg > cassi_issac > vendetta x4 (opp won 3)
- opp: varg > vendetta > cassi_issac x3 (opp won 2)
- opp: vendetta > cassi_issac > stellar x2 (opp won 0)
- opp: cassi_issac > vendetta > stellar x2 (opp won 0)
- opp: cassi_issac > ren > stellar x1 (opp won 0)
- opp: ren > stellar > cassi_issac x1 (opp won 0)

**interlock** (13 games, nch 5):
- us: cassi_issac > ren > stellar > tavi x13 (7-6)
- opp: ren > stellar > cassi_issac > ryth x2 (opp won 2)
- opp: varg > stellar > cassi_issac > tavi x1 (opp won 0)
- opp: ryth > stellar > prism > ren x1 (opp won 1)
- opp: cassi_issac > ryth > stellar > tavi x1 (opp won 0)
- opp: varg > tavi > stellar > cassi_issac x1 (opp won 0)
- opp: varg > vendetta > ryth > ren x1 (opp won 0)

**lanes** (18 games, nch 6):
- us: vendetta > varg > cassi_issac > ryth > tavi x18 (3-15)
- opp: varg > stellar > cassi_issac > tavi > ren x2 (opp won 1)
- opp: cassi_issac > stellar > ryth > ren > prism x1 (opp won 1)
- opp: cassi_issac > vendetta > ryth > stellar > tavi x1 (opp won 1)
- opp: varg > cassi_issac > stellar > tavi > ren x1 (opp won 1)
- opp: cassi_issac > vendetta > stellar > vesper > tavi x1 (opp won 1)
- opp: varg > vendetta > cassi_issac > ryth > ren x1 (opp won 1)

**monolith** (13 games, nch 6):
- us: vendetta > varg > cassi_issac > ryth > tavi x13 (5-8)
- opp: vendetta > varg > cassi_issac > ryth > ren x1 (opp won 1)
- opp: cassi_issac > ren > stellar > tavi > varg x1 (opp won 0)
- opp: cassi_issac > stellar > ren > varg > tavi x1 (opp won 1)
- opp: cassi_issac > ren > ryth > varg > vendetta x1 (opp won 0)
- opp: varg > cassi_issac > stellar > tavi > ren x1 (opp won 1)
- opp: cassi_issac > stellar > tavi > varg > ryth x1 (opp won 1)

**packs** (21 games, nch 4):
- us: cassi_issac > ren > stellar x21 (7-14)
- opp: varg > stellar > cassi_issac x3 (opp won 2)
- opp: ren > stellar > cassi_issac x2 (opp won 2)
- opp: varg > cassi_issac > stellar x2 (opp won 0)
- opp: stellar > tavi > cassi_issac x2 (opp won 2)
- opp: vendetta > varg > cassi_issac x1 (opp won 1)
- opp: cassi_issac > vendetta > stellar x1 (opp won 0)

**rows** (18 games, nch 5):
- us: vendetta > varg > cassi_issac > ryth x18 (4-14)
- opp: varg > vendetta > cassi_issac > ryth x2 (opp won 2)
- opp: varg > vendetta > cassi_issac > willow x2 (opp won 2)
- opp: ren > varg > vendetta > cassi_issac x1 (opp won 0)
- opp: vendetta > varg > cassi_issac > willow x1 (opp won 1)
- opp: stellar > cassi_issac > ren > vendetta x1 (opp won 1)
- opp: cassi_issac > stellar > ryth > ren x1 (opp won 1)

us pool (champion-games): {'cassi_issac': 119, 'ren': 84, 'stellar': 84, 'ryth': 80, 'tavi': 75, 'vendetta': 66, 'varg': 66, 'prism': 31}; first pick: {'vendetta': 66, 'cassi_issac': 53, 'ryth': 31}

opp pool (champion-games): {'cassi_issac': 128, 'stellar': 107, 'varg': 79, 'ren': 74, 'tavi': 63, 'vendetta': 59, 'ryth': 58, 'prism': 16, 'willow': 13, 'marcella': 5, 'vesper': 3}; first pick: {'cassi_issac': 45, 'varg': 44, 'stellar': 22, 'vendetta': 16, 'ren': 14, 'ryth': 8, 'willow': 1}

### Shop per champion type (per champion-game; trips = rounds with a purchase)

**Us**

| type | n | shards bought (family_stat: total) | emblems/g | 1st buy r (med) | buys/g | trips/g | gap med | % dead | % spawn | % field | earned | spent | gold end | unspent % | trips ending at 0 gold | consumables/g |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi | 119 | power_focus:698, durability_health:281 | 1.17 | 178 | 8.6 | 2.5 | 93 | 12% | 88% | 0% | 265 | 250 | 15 | 6% | 74% | 0.36 |
| Issac | 119 | power_strength:2138, jungle_strength:373 | 3.83 | 84 | 21.7 | 5.0 | 68 | 5% | 95% | 0% | 657 | 639 | 18 | 3% | 77% | 0.62 |
| Ren | 84 | power_focus:1832, durability_health:333 | 4.75 | 68 | 27.1 | 6.3 | 63 | 3% | 97% | 0% | 814 | 786 | 27 | 3% | 58% | 1.31 |
| Stellar | 84 | power_focus:1151, durability_health:269 | 2.99 | 120 | 18.1 | 4.5 | 80 | 9% | 91% | 0% | 547 | 519 | 28 | 5% | 45% | 1.23 |
| Ryth | 80 | power_strength:784, durability_strength:325, jungle_strength:284, bruiser_health:203 | 3.59 | 99 | 20.9 | 3.7 | 89 | 2% | 98% | 0% | 631 | 608 | 23 | 4% | 53% | 0.93 |
| Tavi | 75 | power_focus:388, bruiser_focus:150 | 1.12 | 130 | 7.6 | 3.2 | 84 | 0% | 67% | 33% | 224 | 220 | 4 | 2% | 59% | 0.44 |
| Vendetta | 66 | power_strength:538, durability_strength:271, jungle_strength:249, bruiser_health:231 | 3.53 | 122 | 20.2 | 3.9 | 67 | 1% | 99% | 0% | 611 | 593 | 18 | 3% | 86% | 0.67 |
| Varg | 66 | power_strength:1020, durability_strength:295, jungle_strength:245, bruiser_health:173 | 4.86 | 42 | 26.8 | 4.2 | 64 | 1% | 99% | 0% | 809 | 793 | 16 | 2% | 90% | 0.52 |
| Prism | 31 | power_focus:292, durability_health:87 | 2.10 | 66 | 13.4 | 3.8 | 108 | 6% | 94% | 0% | 392 | 379 | 13 | 3% | 20% | 1.19 |

**Opponents**

| type | n | shards bought (family_stat: total) | emblems/g | 1st buy r (med) | buys/g | trips/g | gap med | % dead | % spawn | % field | earned | spent | gold end | unspent % | trips ending at 0 gold | consumables/g |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi | 128 | power_focus:364, monster_focus:180, jungle_focus:98, durability_health:76, jungle_health:69 | 1.33 | 144 | 4.7 | 2.7 | 108 | 9% | 91% | 0% | 284 | 251 | 32 | 11% | 37% | 0.43 |
| Issac | 128 | power_strength:1415, monster_strength:255, durability_health:217, jungle_strength:179, bruiser_health:174 | 3.70 | 68 | 10.9 | 4.4 | 74 | 5% | 95% | 0% | 655 | 611 | 44 | 7% | 44% | 0.65 |
| Stellar | 107 | power_focus:982, durability_health:176, monster_focus:156, bruiser_focus:128, jungle_focus:123 | 2.99 | 118 | 9.7 | 4.0 | 82 | 10% | 90% | 0% | 555 | 505 | 50 | 9% | 33% | 0.64 |
| Varg | 79 | power_strength:1388, monster_strength:187, jungle_strength:152, durability_health:140, durability_strength:94 | 5.27 | 78 | 14.6 | 4.7 | 68 | 2% | 98% | 0% | 956 | 858 | 98 | 10% | 43% | 0.95 |
| Ren | 74 | power_focus:526, power_strength:419, bruiser_health:156, durability_health:155, monster_strength:110 | 4.28 | 86 | 12.8 | 5.3 | 69 | 6% | 94% | 0% | 800 | 705 | 95 | 12% | 41% | 0.78 |
| Tavi | 63 | power_focus:293, power_strength:167, bruiser_focus:134, durability_health:92, monster_strength:78 | 2.73 | 102 | 9.7 | 5.1 | 50 | 1% | 17% | 82% | 501 | 485 | 16 | 3% | 38% | 0.46 |
| Vendetta | 59 | power_strength:667, monster_strength:222, durability_health:109, jungle_health:86, jungle_strength:78 | 4.24 | 83 | 11.7 | 4.2 | 66 | 4% | 96% | 0% | 834 | 707 | 127 | 15% | 35% | 0.88 |
| Ryth | 58 | power_strength:416, bruiser_health:143, monster_strength:115, durability_health:105, power_health:93 | 3.53 | 103 | 8.3 | 4.0 | 81 | 8% | 92% | 0% | 644 | 589 | 56 | 9% | 32% | 0.69 |
| Prism | 16 | power_focus:80, durability_health:38, jungle_focus:10, jungle_health:10, bruiser_focus:8 | 1.62 | 152 | 7.8 | 3.6 | 109 | 14% | 86% | 0% | 342 | 288 | 54 | 16% | 33% | 0.31 |
| Willow | 13 | power_strength:66, monster_strength:15, durability_health:7, jungle_strength:5, home_strength:5 | 1.31 | 134 | 6.3 | 2.1 | 144 | 4% | 96% | 0% | 253 | 248 | 5 | 2% | 47% | 0.15 |
| Marcella | 5 | power_strength:79, monster_strength:20, jungle_strength:15, durability_health:5 | 4.20 | 79 | 12.4 | 4.0 | 119 | 19% | 81% | 0% | 733 | 724 | 9 | 1% | 20% | 1.00 |
| VesperVale | 3 | monster_strength:22, jungle_strength:6, power_strength:5, home_strength:5 | 2.33 | 212 | 3.3 | 2.0 | 114 | 20% | 80% | 0% | 412 | 380 | 32 | 8% | 33% | 0.00 |

### Our purchase sequences (first 3 trips per champion-game: round:gold spent, H = health shards, [d]=dead, [f]=field)

- Vendetta: r84:90 | r115:160 | r179:180 x15; r127:270 | r235:270HHH | r343:130HH x15; (no purchase) x2; r20:90 | r50:90 | r168:180 x2
- Varg: r36:270 | r143:270HHH | r204:270HH x16; r42:90 | r185:90 | r240:160 x15; r49:180 | r113:180 | r176:180HHH x2; r49:180 | r113:180 | r177:180HHH x2
- Cassi: r184:90 x15; r315:270HHHH x15; (no purchase) x13; r109:90 | r204:90H | r388:90H[d]H[d]H[d] x1
- Issac: r84:90 | r183:90 | r268:90 x15; (no purchase) x15; r123:270 | r177:270 | r342:130 x15; r58:180 | r171:180 | r235:180 x1
- Ryth: r65:270 | r284:270HHH x9; r65:270 | r284:270HHH | r402:270HH x6; (no purchase) x5; r99:180 | r187:180 x2
- Tavi: (no purchase) x16; r88:90 x2; r40:90 | r119:180 | r383:90H x1; r336:90 | r417:90 x1
- Ren: (no purchase) x6; r21:90 | r78:90H | r174:90HHH x1; r91:240HHH | r123:60HH | r164:190 x1; r42:90 | r94:90H | r203:180HHHH x1
- Stellar: (no purchase) x5; r106:130 | r174:100HH | r263:180HHH x1; r309:60[d][d] | r369:10 | r529:120[d][d][d]H[d] x1; r153:180H | r176:90HHH | r271:90H x1
- Prism: (no purchase) x7; r163:40 | r257:90 | r394:90[d]H[d]H[d] x1; r407:90 | r430:90H x1; r66:190H | r123:180HHHH | r330:210 x1

### Family presence per type (share of champion-games with >=5 shards of the family), us vs opp

| team | type | n | families with a full emblem (share of games) |
|---|---|---|---|
| us | Cassi | 119 | power_focus 62%, durability_health 25% |
| us | Issac | 119 | power_strength 84%, jungle_strength 61% |
| us | Ren | 84 | power_focus 82%, durability_health 75% |
| us | Stellar | 84 | power_focus 72%, durability_health 58% |
| us | Ryth | 80 | power_strength 85%, durability_strength 77%, jungle_strength 66%, bruiser_health 36% |
| us | Tavi | 75 | power_focus 54%, bruiser_focus 30% |
| us | Vendetta | 66 | power_strength 87%, durability_strength 77%, jungle_strength 74%, bruiser_health 68% |
| us | Varg | 66 | power_strength 95%, durability_strength 81%, jungle_strength 69%, bruiser_health 46% |
| us | Prism | 31 | power_focus 64%, durability_health 45% |

| team | type | n | families with a full emblem (share of games) |
|---|---|---|---|
| opp | Cassi | 128 | monster_focus 25%, power_focus 22%, jungle_focus 11%, durability_health 10%, jungle_health 8%, durability_focus 6% |
| opp | Issac | 128 | power_strength 60%, monster_strength 36%, durability_health 28%, jungle_strength 26%, jungle_health 15%, bruiser_health 15% |
| opp | Stellar | 107 | power_focus 51%, durability_health 32%, monster_focus 22%, jungle_focus 21%, jungle_health 10%, bruiser_focus 8% |
| opp | Varg | 79 | power_strength 78%, monster_strength 41%, jungle_strength 35%, durability_health 32%, durability_strength 22%, bruiser_health 17% |
| opp | Ren | 74 | durability_health 40%, power_strength 36%, bruiser_health 31%, monster_strength 28%, power_focus 27%, jungle_strength 20% |
| opp | Tavi | 63 | power_strength 28%, power_focus 26%, durability_health 23%, jungle_strength 19%, monster_strength 15%, bruiser_focus 15% |
| opp | Vendetta | 59 | monster_strength 64%, power_strength 57%, durability_health 33%, jungle_health 27%, jungle_strength 25%, power_health 11% |
| opp | Ryth | 58 | power_strength 44%, monster_strength 37%, durability_health 34%, jungle_health 27%, bruiser_health 22%, jungle_strength 18% |
| opp | Prism | 16 | power_focus 37%, durability_health 31%, jungle_focus 12%, jungle_health 12%, monster_focus 6%, bruiser_focus 6% |
| opp | Willow | 13 | power_strength 30%, monster_strength 23%, jungle_strength 7%, home_strength 7%, durability_health 7% |
| opp | Marcella | 5 | monster_strength 80%, power_strength 80%, jungle_strength 60%, durability_health 20% |
| opp | VesperVale | 3 | monster_strength 66%, power_strength 33%, jungle_strength 33%, home_strength 33% |

### Gold per game per map (team totals), us vs opp

| map | n | us earned | us spent | us gold end | us emblems | opp earned | opp spent | opp gold end | opp emblems |
|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 3282 | 3109 | 173 | 18.6 | 3393 | 3198 | 195 | 19.4 |
| corners | 17 | 662 | 626 | 36 | 2.2 | 1670 | 1518 | 152 | 7.7 |
| elkring | 14 | 4935 | 4805 | 130 | 29.5 | 5475 | 5006 | 469 | 31.0 |
| expanse | 17 | 1475 | 1448 | 27 | 7.5 | 1235 | 968 | 267 | 5.2 |
| interlock | 13 | 2118 | 2062 | 57 | 11.6 | 1852 | 1627 | 225 | 8.9 |
| lanes | 18 | 1192 | 1067 | 126 | 5.2 | 1321 | 1113 | 208 | 5.7 |
| monolith | 13 | 3936 | 3848 | 88 | 23.0 | 4251 | 3713 | 538 | 22.2 |
| packs | 21 | 2670 | 2576 | 94 | 15.4 | 3458 | 3206 | 251 | 19.6 |
| rows | 18 | 4061 | 4006 | 56 | 24.2 | 4442 | 4086 | 356 | 25.3 |

| split | team | champion-games | gold at end med | mean | >=90 (3 shards) | >=150 (an emblem) |
|---|---|---|---|---|---|---|
| all | us | 724 | 0 | 18 | 10% | 4% |
| all | opp | 733 | 10 | 58 | 25% | 14% |
| win | us | 273 | 5 | 25 | 14% | 4% |
| win | opp | 277 | 10 | 56 | 29% | 15% |
| loss | us | 451 | 0 | 15 | 7% | 4% |
| loss | opp | 456 | 13 | 60 | 23% | 14% |
| opp top10 | us | 238 | 0 | 18 | 10% | 3% |
| opp top10 | opp | 239 | 10 | 70 | 31% | 18% |
| opp 11-20 | us | 240 | 0 | 20 | 10% | 4% |
| opp 11-20 | opp | 238 | 10 | 42 | 21% | 10% |
| opp 21-30 | us | 223 | 0 | 17 | 8% | 4% |
| opp 21-30 | opp | 231 | 10 | 58 | 22% | 13% |
| opp other | us | 23 | 5 | 20 | 13% | 4% |
| opp other | opp | 25 | 20 | 98 | 48% | 36% |


## Q3 Camp choice

### Per map: camp groups (json group id + side relative to the team), captures per game by us and by the opponent (opponent side is its own view)

**collision** (19 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | wolf | 1350 | 22 | 90 | 40 | 3 | 15 | 6.95 | 100% | 8.37 | 100% |
| 4 | own | gold_cluster | 500 | 0 | 35 | 50 | 5 | 13 | 0.00 | 0% | 0.00 | 0% |
| 1 | own | wolf | 1350 | 22 | 90 | 40 | 8 | 10 | 6.47 | 100% | 7.11 | 100% |
| 5 | own | gold_cluster | 500 | 0 | 35 | 50 | 10 | 8 | 0.00 | 0% | 0.00 | 0% |
| 2 | own | wolf | 1350 | 22 | 90 | 40 | 12 | 6 | 6.89 | 100% | 5.63 | 100% |
| 7 | own | elk | 2400 | 36 | 160 | 60 | 14 | 15 | 0.53 | 47% | 1.32 | 68% |
| 6 | own | gold_cluster | 500 | 0 | 35 | 50 | 15 | 3 | 0.00 | 0% | 0.00 | 0% |
| 8 | own | elk | 2400 | 36 | 160 | 60 | 22 | 18 | 0.00 | 0% | 0.32 | 32% |
| 9 | own | elk+gem_cluster | 3900 | 108 | 160 | 60 | 30 | 26 | 0.05 | 5% | 1.16 | 53% |
| 3 | mid | wolf | 1350 | 22 | 90 | 40 | 17 | 1 | 11.63 | 100% | 5.05 | 74% |
| 6 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 15 | 3 | 0.00 | 0% | 0.00 | 0% |
| 2 | enemy | wolf | 1350 | 22 | 90 | 40 | 12 | 6 | 0.05 | 5% | 0.47 | 26% |
| 5 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 10 | 8 | 0.00 | 0% | 0.00 | 0% |
| 1 | enemy | wolf | 1350 | 22 | 90 | 40 | 8 | 10 | 0.00 | 0% | 0.11 | 11% |
| 4 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 5 | 13 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | wolf | 1350 | 22 | 90 | 40 | 3 | 15 | 0.00 | 0% | 0.05 | 5% |
| 7 | enemy | elk | 2400 | 36 | 160 | 60 | 14 | 15 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | elk | 2400 | 36 | 160 | 60 | 22 | 18 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | elk+gem_cluster | 3900 | 108 | 160 | 60 | 30 | 26 | 0.00 | 0% | 0.16 | 11% |

**corners** (17 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | own | wolf | 1350 | 22 | 90 | 40 | 4 | 23 | 2.18 | 88% | 3.24 | 71% |
| 9 | own | elk | 2400 | 36 | 160 | 60 | 10 | 15 | 0.53 | 47% | 1.06 | 47% |
| 12 | own | elk | 2400 | 36 | 160 | 60 | 12 | 16 | 0.18 | 12% | 0.71 | 41% |
| 8 | own | elk | 2400 | 36 | 160 | 60 | 16 | 13 | 0.00 | 0% | 0.35 | 24% |
| 11 | own | elk | 2400 | 36 | 160 | 60 | 16 | 14 | 0.00 | 0% | 0.12 | 12% |
| 5 | own | wolf | 1350 | 22 | 90 | 40 | 19 | 19 | 0.53 | 35% | 1.29 | 53% |
| 2 | own | elk+gem_cluster | 5300 | 96 | 320 | 60 | 22 | 21 | 0.00 | 0% | 0.06 | 6% |
| 4 | own | gold_cluster | 1000 | 0 | 70 | 50 | 24 | 18 | 0.00 | 0% | 0.00 | 0% |
| 6 | own | wolf | 1350 | 22 | 90 | 40 | 25 | 13 | 0.00 | 0% | 0.65 | 41% |
| 7 | own | wolf | 1350 | 22 | 90 | 40 | 27 | 6 | 0.00 | 0% | 0.53 | 35% |
| 13 | own | elk | 4800 | 72 | 320 | 60 | 29 | 8 | 0.00 | 0% | 0.00 | 0% |
| 0 | mid | gem_cluster | 1000 | 48 | 0 | 50 | 19 | 0 | 4.82 | 94% | 7.94 | 94% |
| 1 | mid | gem_cluster | 1000 | 48 | 0 | 50 | 19 | 0 | 6.76 | 94% | 6.00 | 100% |
| 14 | mid | gold_cluster | 1000 | 0 | 70 | 50 | 19 | 16 | 0.00 | 0% | 0.00 | 0% |
| 10 | mid | gold_cluster | 1000 | 0 | 70 | 50 | 31 | 31 | 0.00 | 0% | 0.00 | 0% |
| 5 | enemy | wolf | 1350 | 22 | 90 | 40 | 19 | 19 | 0.00 | 0% | 0.35 | 24% |
| 2 | enemy | elk+gem_cluster | 5300 | 96 | 320 | 60 | 22 | 21 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | elk | 2400 | 36 | 160 | 60 | 10 | 15 | 0.00 | 0% | 0.12 | 12% |
| 12 | enemy | elk | 2400 | 36 | 160 | 60 | 12 | 16 | 0.00 | 0% | 0.00 | 0% |
| 4 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 24 | 18 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | elk | 2400 | 36 | 160 | 60 | 16 | 13 | 0.00 | 0% | 0.00 | 0% |
| 13 | enemy | elk | 4800 | 72 | 320 | 60 | 29 | 8 | 0.00 | 0% | 0.00 | 0% |
| 6 | enemy | wolf | 1350 | 22 | 90 | 40 | 25 | 13 | 0.00 | 0% | 0.00 | 0% |
| 3 | enemy | wolf | 1350 | 22 | 90 | 40 | 4 | 23 | 0.00 | 0% | 0.06 | 6% |
| 11 | enemy | elk | 2400 | 36 | 160 | 60 | 16 | 14 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | wolf | 1350 | 22 | 90 | 40 | 27 | 6 | 0.00 | 0% | 0.00 | 0% |

**elkring** (14 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 2 | 17 | 6.36 | 100% | 6.93 | 100% |
| 1 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 5 | 14 | 5.50 | 100% | 5.64 | 100% |
| 2 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 8 | 11 | 5.14 | 100% | 5.50 | 100% |
| 3 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 2.57 | 86% | 3.21 | 100% |
| 4 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 3.00 | 93% | 3.21 | 100% |
| 2 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 8 | 11 | 0.00 | 0% | 0.21 | 21% |
| 4 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 0.93 | 57% | 0.86 | 50% |
| 1 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 5 | 14 | 0.00 | 0% | 0.07 | 7% |
| 3 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 0.29 | 29% | 1.43 | 71% |
| 0 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 2 | 17 | 0.00 | 0% | 0.07 | 7% |

**expanse** (17 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11 | own | wolf | 1350 | 22 | 90 | 40 | 5 | 8 | 3.06 | 100% | 4.06 | 100% |
| 1 | own | gem_cluster | 1000 | 48 | 0 | 50 | 11 | 6 | 4.53 | 100% | 4.71 | 100% |
| 12 | own | wolf | 1350 | 22 | 90 | 40 | 15 | 6 | 2.94 | 100% | 3.06 | 94% |
| 2 | own | gem_cluster | 1000 | 48 | 0 | 50 | 17 | 9 | 4.00 | 100% | 4.06 | 100% |
| 14 | own | elk | 2400 | 36 | 160 | 60 | 17 | 9 | 2.82 | 100% | 0.71 | 41% |
| 7 | own | gold_cluster | 1000 | 0 | 70 | 50 | 24 | 8 | 0.00 | 0% | 0.00 | 0% |
| 10 | own | wolf | 1350 | 22 | 90 | 40 | 27 | 6 | 1.88 | 94% | 2.06 | 82% |
| 0 | own | gem_cluster | 1000 | 48 | 0 | 50 | 28 | 7 | 3.88 | 100% | 4.12 | 100% |
| 8 | own | gold_cluster | 1000 | 0 | 70 | 50 | 31 | 8 | 0.00 | 0% | 0.00 | 0% |
| 6 | own | gold_cluster | 1000 | 0 | 70 | 50 | 33 | 1 | 0.00 | 0% | 0.00 | 0% |
| 13 | own | wolf | 2700 | 44 | 180 | 40 | 38 | 8 | 0.94 | 94% | 0.88 | 53% |
| 3 | own | elk+gem_cluster | 3900 | 108 | 160 | 60 | 51 | 9 | 0.88 | 82% | 0.59 | 41% |
| 4 | own | elk+gem_cluster | 3900 | 108 | 160 | 60 | 58 | 16 | 0.00 | 0% | 0.24 | 24% |
| 5 | own | gold_cluster | 1000 | 0 | 70 | 50 | 64 | 26 | 0.00 | 0% | 0.00 | 0% |
| 9 | mid | elk+gem_cluster | 3900 | 108 | 160 | 60 | 63 | 24 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 31 | 8 | 0.00 | 0% | 0.00 | 0% |
| 10 | enemy | wolf | 1350 | 22 | 90 | 40 | 27 | 6 | 0.00 | 0% | 0.00 | 0% |
| 6 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 33 | 1 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 24 | 8 | 0.00 | 0% | 0.00 | 0% |
| 3 | enemy | elk+gem_cluster | 3900 | 108 | 160 | 60 | 51 | 9 | 0.00 | 0% | 0.00 | 0% |
| 4 | enemy | elk+gem_cluster | 3900 | 108 | 160 | 60 | 58 | 16 | 0.00 | 0% | 0.00 | 0% |
| 14 | enemy | elk | 2400 | 36 | 160 | 60 | 17 | 9 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | gem_cluster | 1000 | 48 | 0 | 50 | 28 | 7 | 0.00 | 0% | 0.06 | 6% |
| 12 | enemy | wolf | 1350 | 22 | 90 | 40 | 15 | 6 | 0.00 | 0% | 0.00 | 0% |
| 13 | enemy | wolf | 2700 | 44 | 180 | 40 | 38 | 8 | 0.00 | 0% | 0.00 | 0% |
| 5 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 64 | 26 | 0.00 | 0% | 0.00 | 0% |
| 1 | enemy | gem_cluster | 1000 | 48 | 0 | 50 | 11 | 6 | 0.00 | 0% | 0.12 | 6% |
| 2 | enemy | gem_cluster | 1000 | 48 | 0 | 50 | 17 | 9 | 0.00 | 0% | 0.00 | 0% |
| 11 | enemy | wolf | 1350 | 22 | 90 | 40 | 5 | 8 | 0.00 | 0% | 0.00 | 0% |

**interlock** (13 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | own | wolf | 1350 | 22 | 90 | 40 | 4 | 12 | 7.31 | 100% | 6.38 | 100% |
| 4 | own | wolf | 1350 | 22 | 90 | 40 | 10 | 12 | 7.00 | 100% | 5.77 | 100% |
| 0 | own | gem_cluster | 1500 | 72 | 0 | 50 | 14 | 5 | 6.08 | 100% | 6.54 | 100% |
| 1 | own | gold_cluster | 1000 | 0 | 70 | 50 | 15 | 11 | 0.00 | 0% | 0.00 | 0% |
| 5 | own | wolf | 1350 | 22 | 90 | 40 | 17 | 12 | 6.00 | 100% | 4.54 | 100% |
| 7 | own | elk | 2400 | 36 | 160 | 60 | 24 | 11 | 0.62 | 54% | 0.23 | 15% |
| 6 | mid | elk | 2400 | 36 | 160 | 60 | 27 | 3 | 0.38 | 31% | 0.69 | 54% |
| 2 | mid | gold_cluster | 1000 | 0 | 70 | 50 | 33 | 7 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | gem_cluster | 1500 | 72 | 0 | 50 | 14 | 5 | 0.08 | 8% | 0.46 | 31% |
| 4 | enemy | wolf | 1350 | 22 | 90 | 40 | 10 | 12 | 0.00 | 0% | 0.00 | 0% |
| 5 | enemy | wolf | 1350 | 22 | 90 | 40 | 17 | 12 | 0.00 | 0% | 0.08 | 8% |
| 1 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 15 | 11 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | elk | 2400 | 36 | 160 | 60 | 24 | 11 | 0.00 | 0% | 0.00 | 0% |
| 3 | enemy | wolf | 1350 | 22 | 90 | 40 | 4 | 12 | 0.00 | 0% | 0.00 | 0% |

**lanes** (18 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 4.78 | 100% | 4.28 | 100% |
| 5 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 4.83 | 100% | 4.67 | 100% |
| 6 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 4.61 | 100% | 5.00 | 100% |
| 7 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 8 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 9 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 18 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 4.11 | 100% | 5.06 | 100% |
| 19 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 3.78 | 94% | 5.00 | 100% |
| 20 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 3.78 | 100% | 4.72 | 100% |
| 3 | own | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.61 | 50% | 1.06 | 56% |
| 10 | own | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.22 | 22% | 0.22 | 17% |
| 17 | own | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.06 | 6% | 0.94 | 50% |
| 11 | own | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 2.78 | 94% | 0.50 | 39% |
| 12 | own | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 2.11 | 94% | 0.50 | 33% |
| 13 | own | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 1.50 | 94% | 0.39 | 22% |
| 0 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 1.61 | 83% | 1.56 | 72% |
| 1 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 1.17 | 78% | 1.56 | 61% |
| 2 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.61 | 50% | 0.89 | 56% |
| 14 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.28 | 28% | 1.11 | 61% |
| 15 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.06 | 6% | 1.06 | 56% |
| 16 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.11 | 11% | 0.67 | 33% |
| 11 | enemy | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 0.56 | 50% | 0.17 | 17% |
| 12 | enemy | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 0.17 | 11% | 0.39 | 22% |
| 13 | enemy | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 0.17 | 6% | 0.17 | 17% |
| 3 | enemy | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.00 | 0% | 0.00 | 0% |
| 10 | enemy | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.00 | 0% | 0.00 | 0% |
| 17 | enemy | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.00 | 0% | 0.06 | 6% |
| 4 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.17 | 11% |
| 5 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.28 | 22% |
| 6 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.17 | 17% |
| 7 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 18 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.67 | 28% |
| 19 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.72 | 28% |
| 20 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.56 | 33% |

**monolith** (13 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | own | wolf | 1350 | 22 | 90 | 40 | 5 | 18 | 3.85 | 100% | 6.08 | 100% |
| 2 | own | wolf | 1350 | 22 | 90 | 40 | 9 | 14 | 3.62 | 100% | 4.23 | 100% |
| 5 | own | elk | 2400 | 36 | 160 | 60 | 12 | 15 | 1.31 | 85% | 2.08 | 85% |
| 4 | own | wolf | 1350 | 22 | 90 | 40 | 13 | 17 | 2.46 | 100% | 4.38 | 100% |
| 9 | own | wolf | 2700 | 44 | 180 | 40 | 20 | 11 | 5.00 | 100% | 5.77 | 100% |
| 6 | own | gold_cluster | 500 | 0 | 35 | 50 | 21 | 2 | 0.00 | 0% | 0.00 | 0% |
| 1 | own | wolf | 2700 | 44 | 180 | 40 | 23 | 6 | 5.15 | 100% | 3.85 | 100% |
| 7 | own | gold_cluster | 500 | 0 | 35 | 50 | 25 | 4 | 0.00 | 0% | 0.00 | 0% |
| 8 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 1 | 0.00 | 0% | 0.00 | 0% |
| 10 | own | wolf | 2700 | 44 | 180 | 40 | 35 | 6 | 3.85 | 100% | 2.85 | 100% |
| 0 | own | gem_cluster+monolith | 24000 | 392 | 300 | 150 | 41 | 0 | 0.00 | 0% | 0.00 | 0% |
| 6 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 21 | 2 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 25 | 4 | 0.00 | 0% | 0.00 | 0% |
| 5 | enemy | elk | 2400 | 36 | 160 | 60 | 12 | 15 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | wolf | 2700 | 44 | 180 | 40 | 20 | 11 | 0.00 | 0% | 0.08 | 8% |
| 8 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 1 | 0.00 | 0% | 0.00 | 0% |
| 10 | enemy | wolf | 2700 | 44 | 180 | 40 | 35 | 6 | 1.23 | 77% | 0.77 | 46% |
| 1 | enemy | wolf | 2700 | 44 | 180 | 40 | 23 | 6 | 0.00 | 0% | 0.46 | 38% |
| 2 | enemy | wolf | 1350 | 22 | 90 | 40 | 9 | 14 | 0.00 | 0% | 0.31 | 31% |
| 4 | enemy | wolf | 1350 | 22 | 90 | 40 | 13 | 17 | 0.00 | 0% | 0.15 | 15% |
| 3 | enemy | wolf | 1350 | 22 | 90 | 40 | 5 | 18 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | gem_cluster+monolith | 24000 | 392 | 300 | 150 | 41 | 0 | 0.00 | 0% | 0.00 | 0% |

**packs** (21 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | wolf | 2700 | 44 | 180 | 40 | 4 | 4 | 5.90 | 100% | 7.24 | 100% |
| 2 | own | wolf | 2700 | 44 | 180 | 40 | 12 | 10 | 4.24 | 95% | 4.90 | 100% |
| 1 | mid | gem_cluster+gold_cluster | 2000 | 48 | 70 | 50 | 14 | 7 | 6.19 | 100% | 5.95 | 100% |
| 3 | mid | wolf | 2700 | 44 | 180 | 40 | 23 | 2 | 1.57 | 81% | 3.38 | 100% |
| 0 | enemy | wolf | 2700 | 44 | 180 | 40 | 4 | 4 | 0.00 | 0% | 0.05 | 5% |
| 2 | enemy | wolf | 2700 | 44 | 180 | 40 | 12 | 10 | 0.05 | 5% | 0.29 | 19% |

**rows** (18 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | wolf | 4050 | 66 | 270 | 40 | 11 | 10 | 5.89 | 100% | 7.11 | 100% |
| 1 | own | wolf | 4050 | 66 | 270 | 40 | 24 | 23 | 5.67 | 100% | 6.33 | 100% |
| 2 | own | wolf | 4050 | 66 | 270 | 40 | 35 | 34 | 4.28 | 100% | 3.78 | 100% |
| 4 | own | gold_cluster | 1500 | 0 | 105 | 50 | 41 | 31 | 0.00 | 0% | 0.00 | 0% |
| 3 | mid | gem_cluster+monolith | 41000 | 448 | 600 | 150 | 34 | 24 | 0.00 | 0% | 0.00 | 0% |
| 4 | enemy | gold_cluster | 1500 | 0 | 105 | 50 | 41 | 31 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | wolf | 4050 | 66 | 270 | 40 | 11 | 10 | 0.00 | 0% | 0.00 | 0% |
| 1 | enemy | wolf | 4050 | 66 | 270 | 40 | 24 | 23 | 0.00 | 0% | 0.00 | 0% |
| 2 | enemy | wolf | 4050 | 66 | 270 | 40 | 35 | 34 | 0.00 | 0% | 0.00 | 0% |

### Captures per game by territory (own / mid / enemy), us vs opp

| split | n | us own/mid/enemy | opp own/mid/enemy |
|---|---|---|---|
| all | 150 | 19.8 / 4.4 / 0.3 | 21.2 / 4.4 / 1.1 |
| map collision | 19 | 20.9 / 11.6 / 0.1 | 23.9 / 5.1 / 0.8 |
| map corners | 17 | 3.4 / 11.6 / 0.0 | 8.0 / 13.9 / 0.5 |
| map elkring | 14 | 22.6 / 0.0 / 1.2 | 24.5 / 0.0 / 2.6 |
| map expanse | 17 | 24.9 / 0.0 / 0.0 | 24.5 / 0.0 / 0.2 |
| map interlock | 13 | 27.0 / 0.4 / 0.1 | 23.5 / 0.7 / 0.5 |
| map lanes | 18 | 33.2 / 3.8 / 0.9 | 32.3 / 6.8 / 3.3 |
| map monolith | 13 | 25.2 / 0.0 / 1.2 | 29.2 / 0.0 / 1.8 |
| map packs | 21 | 10.1 / 7.8 / 0.0 | 12.1 / 9.3 / 0.3 |
| map rows | 18 | 15.8 / 0.0 / 0.0 | 17.2 / 0.0 / 0.0 |
| win | 59 | 22.6 / 6.0 / 0.5 | 21.5 / 2.4 / 0.5 |
| loss | 91 | 18.0 / 3.3 / 0.3 | 21.0 / 5.7 / 1.4 |
| opp top10 | 50 | 17.7 / 3.6 / 0.2 | 20.3 / 5.7 / 0.7 |
| opp 11-20 | 50 | 22.1 / 4.0 / 0.4 | 23.0 / 3.4 / 0.9 |
| opp 21-30 | 45 | 19.4 / 5.4 / 0.5 | 20.6 / 4.5 / 1.8 |
| opp other | 5 | 21.4 / 6.4 / 0.6 | 18.0 / 0.8 / 0.0 |

### Opening order: the first 5 groups our team captures (jg/side), most common sequences per map

- collision: first capture round med 33; 3m-3m-2o-1o-0o x4; 3m-3m-2o-0o-1o x3; 3m-3m-1o-2o-0o x2
- corners: first capture round med 41; 0m-1m-0m-1m-3o x4; 1m-1m-0m x1; 0m-1m-1m-0m-5o x1
- elkring: first capture round med 25; 0o-1o-2o-4o-0o x6; 0o-1o-2o-0o-3o x2; 0o-1o-2o-0o-1o x2
- expanse: first capture round med 30; 1o-11o-0o-2o-10o x16; 1o-11o-0o-2o-12o x1
- interlock: first capture round med 20; 3o-4o-0o-5o-3o x11; 3o-4o-0o-5o-4o x1; 3o-4o-0o-3o-4o x1
- lanes: first capture round med 40; 5o-18o-4o-6o-19o x16; 5o-18o-4o-6o-11o x2
- monolith: first capture round med 19; 3o-2o-9o-4o-1o x13
- packs: first capture round med 33; 1m-1m-0o-2o-1m x6; 1m-1m-0o-2o-0o x4; 1m-0o-2o-1m-0o x2
- rows: first capture round med 36; 0o-1o-0o-1o-2o x18

### Camp set per map: groups taken in >=80% / >=50% of games, mean distinct groups per game, Jaccard between games (us vs opp)

| map | n | us core(>=80%) | us >=50% | us distinct/g | us jaccard | opp core | opp >=50% | opp distinct/g | opp jaccard |
|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 4 | 4 | 4.6 | 0.86 | 3 | 6 | 5.8 | 0.63 |
| corners | 17 | 3 | 3 | 3.7 | 0.63 | 2 | 4 | 5.6 | 0.45 |
| elkring | 14 | 5 | 6 | 5.6 | 0.79 | 5 | 7 | 6.6 | 0.79 |
| expanse | 17 | 9 | 9 | 8.7 | 0.94 | 6 | 7 | 7.5 | 0.72 |
| interlock | 13 | 4 | 5 | 4.9 | 0.80 | 4 | 5 | 5.1 | 0.77 |
| lanes | 18 | 10 | 14 | 12.8 | 0.72 | 6 | 13 | 13.6 | 0.52 |
| monolith | 13 | 7 | 8 | 7.6 | 0.92 | 7 | 7 | 8.2 | 0.77 |
| packs | 21 | 4 | 4 | 3.8 | 0.88 | 4 | 4 | 4.2 | 0.92 |
| rows | 18 | 3 | 3 | 3.0 | 1.00 | 3 | 3 | 3.0 | 1.00 |

### Revisits: rounds between a group respawn and our next capture of it (non-first captures); nearest-up rule

| split | n | us revisits | gap med | mean | us captures | nearest-up chosen | 1st or 2nd nearest | extra dist med | mean | opp revisits | gap med | mean | opp captures | nearest | 1st/2nd | extra med | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 150 | 2774 | 33 | 44 | 3676 | 44% | 68% | 0 | 4.5 | 3113 | 32 | 46 | 4003 | 52% | 72% | 0 | 3.9 |
| map collision | 19 | 521 | 39 | 50 | 619 | 52% | 72% | 0 | 3.8 | 470 | 47 | 66 | 565 | 60% | 79% | 0 | 3.6 |
| map corners | 17 | 177 | 33 | 51 | 255 | 38% | 43% | 8 | 7.4 | 300 | 37 | 59 | 382 | 39% | 48% | 5 | 6.9 |
| map elkring | 14 | 270 | 40 | 48 | 333 | 57% | 86% | 0 | 3.0 | 301 | 38 | 49 | 380 | 56% | 81% | 0 | 3.2 |
| map expanse | 17 | 276 | 39 | 43 | 424 | 29% | 55% | 3 | 7.9 | 294 | 32 | 37 | 419 | 44% | 68% | 1 | 5.7 |
| map interlock | 13 | 295 | 23 | 29 | 357 | 52% | 80% | 0 | 3.4 | 259 | 27 | 37 | 321 | 60% | 82% | 0 | 2.7 |
| map lanes | 18 | 465 | 29 | 42 | 682 | 34% | 55% | 0 | 2.1 | 540 | 25 | 39 | 765 | 43% | 57% | 0 | 2.2 |
| map monolith | 13 | 250 | 46 | 54 | 344 | 34% | 53% | 3 | 6.0 | 317 | 36 | 47 | 403 | 48% | 68% | 0 | 4.7 |
| map packs | 21 | 289 | 34 | 45 | 377 | 57% | 80% | 0 | 3.1 | 379 | 33 | 43 | 458 | 57% | 83% | 0 | 3.1 |
| map rows | 18 | 231 | 22 | 32 | 285 | 48% | 97% | 11 | 7.4 | 253 | 23 | 26 | 310 | 68% | 96% | 0 | 4.8 |
| win | 59 | 1341 | 31 | 42 | 1716 | 45% | 68% | 0 | 4.7 | 1104 | 36 | 51 | 1438 | 52% | 73% | 0 | 4.2 |
| loss | 91 | 1433 | 34 | 46 | 1960 | 43% | 68% | 0 | 4.3 | 2009 | 30 | 43 | 2565 | 52% | 71% | 0 | 3.8 |
| opp top10 | 50 | 802 | 33 | 44 | 1076 | 47% | 71% | 0 | 4.2 | 1046 | 31 | 44 | 1339 | 53% | 75% | 0 | 3.6 |
| opp 11-20 | 50 | 1000 | 34 | 45 | 1321 | 44% | 68% | 0 | 4.4 | 1059 | 30 | 46 | 1361 | 53% | 71% | 0 | 3.7 |
| opp 21-30 | 45 | 861 | 33 | 45 | 1137 | 41% | 64% | 1 | 4.9 | 944 | 35 | 47 | 1209 | 50% | 69% | 0 | 4.4 |
| opp other | 5 | 111 | 25 | 32 | 142 | 52% | 69% | 0 | 4.5 | 64 | 50 | 57 | 94 | 39% | 63% | 3 | 5.1 |

### Groups (jg/side in each team's own view) with captures/g by us <0.2 but by opp >=0.5, and the reverse

- collision: opp farms, we do not: ['9o(108g,3900hp,d30: us 0.05 opp 1.16)']; we farm, opp does not: -
- corners: opp farms, we do not: ['6o(22g,1350hp,d25: us 0.00 opp 0.65)', '7o(22g,1350hp,d27: us 0.00 opp 0.53)', '12o(36g,2400hp,d12: us 0.18 opp 0.71)']; we farm, opp does not: -
- elkring: opp farms, we do not: -; we farm, opp does not: -
- expanse: opp farms, we do not: -; we farm, opp does not: -
- interlock: opp farms, we do not: -; we farm, opp does not: -
- lanes: opp farms, we do not: ['15m(22g,1350hp,d40: us 0.06 opp 1.06)', '16m(22g,1350hp,d40: us 0.11 opp 0.67)', '17o(36g,2400hp,d33: us 0.06 opp 0.94)', '18e(24g,500hp,d30: us 0.00 opp 0.67)', '19e(24g,500hp,d30: us 0.00 opp 0.72)', '20e(24g,500hp,d30: us 0.00 opp 0.56)']; we farm, opp does not: ['11e(22g: us 0.56 opp 0.17)']
- monolith: opp farms, we do not: -; we farm, opp does not: -
- packs: opp farms, we do not: -; we farm, opp does not: -
- rows: opp farms, we do not: -; we farm, opp does not: -


## Q4 Squad size and kill speed

### By group hp (Mite reference: 2.0/2.05/2.4/3.5 attackers, 12/17/21/23 rounds)

| split | team | bucket | captures | attackers mean | within 4 at capture | hit->capture med | mean | group hp/attacker/round med | measured dmg/attacker/round med |
|---|---|---|---|---|---|---|---|---|---|
| all | us | <1500 | 1789 | 1.51 | 1.64 | 22 | 29.4 | 44 | 42 |
| all | us | <3000 | 1120 | 2.03 | 1.37 | 24 | 32.0 | 50 | 48 |
| all | us | <800 | 466 | 1.16 | 1.98 | 16 | 17.7 | 29 | 29 |
| all | us | >=3000 | 301 | 2.57 | 1.32 | 21 | 25.4 | 79 | 79 |
| all | opp | <1500 | 1804 | 1.82 | 1.62 | 22 | 30.9 | 38 | 37 |
| all | opp | <3000 | 1286 | 2.27 | 1.34 | 23 | 30.8 | 50 | 48 |
| all | opp | <800 | 563 | 1.44 | 1.98 | 15 | 16.1 | 29 | 29 |
| all | opp | >=3000 | 350 | 2.69 | 1.26 | 22 | 27.1 | 68 | 68 |

### By round (first 50 rounds vs later)

| split | team | bucket | captures | attackers mean | within 4 at capture | hit->capture med | mean | group hp/attacker/round med | measured dmg/attacker/round med |
|---|---|---|---|---|---|---|---|---|---|
| all | us | <150 | 743 | 1.87 | 1.54 | 26 | 29.9 | 36 | 35 |
| all | us | <300 | 1128 | 1.69 | 1.45 | 22 | 28.8 | 45 | 44 |
| all | us | <50 | 356 | 1.85 | 2.01 | 19 | 20.7 | 38 | 35 |
| all | us | >=300 | 1449 | 1.61 | 1.58 | 20 | 29.2 | 56 | 52 |
| all | opp | <150 | 785 | 2.20 | 1.57 | 24 | 28.5 | 34 | 33 |
| all | opp | <300 | 1319 | 1.88 | 1.46 | 21 | 29.5 | 42 | 41 |
| all | opp | <50 | 359 | 2.73 | 2.04 | 17 | 19.3 | 33 | 33 |
| all | opp | >=300 | 1540 | 1.79 | 1.51 | 19 | 29.6 | 54 | 52 |

### By map, all hp buckets pooled

| map | team | captures | attackers mean | hit->capture med | mean group hp | hp/attacker/round med |
|---|---|---|---|---|---|---|
| collision | us | 619 | 1.55 | 20 | 1371 | 48 |
| collision | opp | 565 | 1.78 | 21 | 1520 | 44 |
| corners | us | 255 | 2.02 | 25 | 1129 | 29 |
| corners | opp | 382 | 2.39 | 25 | 1253 | 24 |
| elkring | us | 333 | 2.41 | 26 | 2900 | 48 |
| elkring | opp | 380 | 2.71 | 22 | 2900 | 48 |
| expanse | us | 424 | 1.10 | 24 | 1436 | 53 |
| expanse | opp | 419 | 1.27 | 22 | 1328 | 45 |
| interlock | us | 357 | 1.80 | 19 | 1422 | 40 |
| interlock | opp | 321 | 1.93 | 20 | 1432 | 42 |
| lanes | us | 682 | 1.21 | 18 | 794 | 31 |
| lanes | opp | 765 | 1.65 | 16 | 781 | 29 |
| monolith | us | 344 | 1.51 | 24 | 2179 | 59 |
| monolith | opp | 403 | 1.73 | 22 | 2020 | 54 |
| packs | us | 377 | 2.10 | 23 | 2459 | 48 |
| packs | opp | 458 | 2.16 | 22 | 2509 | 53 |
| rows | us | 285 | 2.66 | 21 | 4050 | 75 |
| rows | opp | 310 | 2.88 | 21 | 4050 | 68 |

### By win/loss and opponent tier, hp >= 800 groups

| split | team | captures (hp>=800) | attackers mean | hit->capture med | hp/attacker/round med |
|---|---|---|---|---|---|
| win | us | 1620 | 1.68 | 22 | 48 |
| win | opp | 1351 | 1.92 | 22 | 45 |
| loss | us | 1590 | 1.89 | 24 | 48 |
| loss | opp | 2089 | 2.18 | 23 | 44 |
| opp top10 | us | 944 | 1.81 | 23 | 48 |
| opp top10 | opp | 1203 | 2.17 | 21 | 45 |
| opp 11-20 | us | 1127 | 1.73 | 23 | 50 |
| opp 11-20 | opp | 1135 | 1.96 | 22 | 48 |
| opp 21-30 | us | 997 | 1.83 | 23 | 48 |
| opp 21-30 | opp | 1008 | 2.12 | 23 | 44 |
| opp other | us | 142 | 1.77 | 20 | 45 |
| opp other | opp | 94 | 1.74 | 28 | 37 |

### Attackers distribution per hp bucket (count of captures by number of attackers), us vs opp

| team | hp bucket | captures | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|---|---|
| us | <1500 | 1789 | 1067 | 576 | 117 | 21 | 8 |
| us | <3000 | 1120 | 285 | 548 | 263 | 19 | 5 |
| us | <800 | 466 | 393 | 70 | 3 | 0 | 0 |
| us | >=3000 | 301 | 34 | 78 | 171 | 18 | 0 |
| opp | <1500 | 1804 | 891 | 550 | 211 | 116 | 36 |
| opp | <3000 | 1286 | 362 | 442 | 314 | 118 | 50 |
| opp | <800 | 563 | 365 | 157 | 35 | 6 | 0 |
| opp | >=3000 | 350 | 67 | 73 | 128 | 66 | 16 |

### Who tanks: champion type taking most monster damage during the capture, by capturing team (count); and monster damage taken per type

- us tank per capture: {'Issac': 558, 'Ren': 495, 'Vendetta': 326, 'Varg': 275, 'Cassi': 274, 'Ryth': 267, 'Stellar': 238, 'Tavi': 111, 'Prism': 43, 'VesperVale': 1, 'Willow': 1}
- us monster damage taken per champion-game: Cassi 808 (40 hits), Issac 1744 (92 hits), Ren 2371 (85 hits), Stellar 1105 (37 hits), Ryth 1964 (64 hits), Tavi 866 (28 hits), Vendetta 1918 (99 hits), Varg 1453 (60 hits), Prism 1500 (29 hits)
- opp tank per capture: {'Issac': 618, 'Ren': 396, 'Varg': 362, 'Stellar': 319, 'Vendetta': 309, 'Cassi': 261, 'Ryth': 236, 'Tavi': 164, 'Prism': 46, 'Marcella': 17, 'Willow': 9, 'VesperVale': 7}
- opp monster damage taken per champion-game: Cassi 969 (42 hits), Issac 1962 (87 hits), Stellar 1008 (41 hits), Varg 1127 (44 hits), Ren 1906 (73 hits), Tavi 990 (37 hits), Vendetta 2249 (89 hits), Ryth 1852 (65 hits), Prism 1472 (41 hits), Willow 400 (14 hits), Marcella 1682 (54 hits), VesperVale 1333 (57 hits)

### Basic-attack distance to the camp monster (share of basic attacks on camps at Chebyshev distance 1 / 2 / 3+), by type

| team | type | camp basic attacks | d0 | d1 | d2 | d3+ |
|---|---|---|---|---|---|---|
| us | Issac | 14552 | 0% | 100% | 0% | 0% |
| us | Cassi | 11586 | 0% | 0% | 4% | 96% |
| us | Varg | 8982 | 0% | 86% | 14% | 0% |
| us | Tavi | 8436 | 0% | 1% | 6% | 93% |
| us | Ren | 7908 | 0% | 100% | 0% | 0% |
| us | Ryth | 7365 | 0% | 100% | 0% | 0% |
| us | Vendetta | 6534 | 0% | 100% | 0% | 0% |
| us | Stellar | 6505 | 0% | 1% | 10% | 89% |
| us | Prism | 2247 | 0% | 0% | 9% | 91% |
| opp | Issac | 14866 | 0% | 100% | 0% | 0% |
| opp | Cassi | 13314 | 0% | 5% | 9% | 86% |
| opp | Varg | 11938 | 0% | 74% | 26% | 0% |
| opp | Stellar | 7528 | 0% | 6% | 10% | 84% |
| opp | Ren | 6794 | 0% | 100% | 0% | 0% |
| opp | Vendetta | 6735 | 0% | 100% | 0% | 0% |
| opp | Tavi | 6470 | 0% | 3% | 8% | 88% |
| opp | Ryth | 5739 | 0% | 100% | 0% | 0% |
| opp | Willow | 1520 | 0% | 5% | 11% | 84% |
| opp | Prism | 1494 | 0% | 4% | 16% | 79% |
| opp | Marcella | 495 | 0% | 100% | 0% | 0% |
| opp | VesperVale | 354 | 0% | 14% | 16% | 70% |

### Team-level: attackers by map in the first capture of the game (whole team on the first camp?)

| map | nch | us attackers 1st camp | 1st capture round | hit->cap | opp attackers | 1st capture round | hit->cap |
|---|---|---|---|---|---|---|---|
| collision | 4 | 2.00 | 33 | 18 | 3.11 | 18 | 14 |
| corners | 5 | 2.53 | 41 | 22 | 3.59 | 31 | 24 |
| elkring | 5 | 3.00 | 25 | 20 | 5.00 | 18 | 16 |
| expanse | 4 | 2.00 | 30 | 17 | 1.76 | 29 | 19 |
| interlock | 5 | 2.00 | 20 | 15 | 3.23 | 19 | 15 |
| lanes | 6 | 1.00 | 40 | 13 | 1.67 | 40 | 14 |
| monolith | 6 | 3.00 | 19 | 15 | 3.00 | 19 | 15 |
| packs | 4 | 2.14 | 33 | 19 | 3.14 | 26 | 22 |
| rows | 5 | 3.00 | 36 | 25 | 4.72 | 31 | 21 |


## Q5 Bags and tributes

| split | team | n | tribute starts | completed | completed/game | per 100 champ-rounds | bag med | mean | p90 | bags<=10 | bags>=100 | captures per bag | oldest gems age med | newest age med | not completed | ..died | ..cancelled | ..other | altar passes with >=10 gems | passes/game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 150 | 3256 | 3057 | 20.4 | 0.99 | 44 | 40 | 66 | 0% | 1% | 1.09 | 11 | 10 | 199 (6%) | 24 | 0 | 175 | 117 | 0.78 |
| all | opp | 150 | 3306 | 3056 | 20.4 | 0.93 | 44 | 45 | 70 | 0% | 2% | 1.22 | 12 | 10 | 250 (8%) | 26 | 0 | 224 | 284 | 1.89 |
| map collision | us | 19 | 485 | 456 | 24.0 | 1.04 | 22 | 32 | 44 | 0% | 4% | 1.22 | 16 | 10 | 29 (6%) | 7 | 0 | 22 | 24 | 1.26 |
| map collision | opp | 19 | 376 | 330 | 17.4 | 0.74 | 22 | 39 | 66 | 0% | 6% | 1.32 | 20 | 16 | 46 (12%) | 11 | 0 | 35 | 75 | 3.95 |
| map corners | us | 17 | 269 | 222 | 13.1 | 0.63 | 48 | 46 | 48 | 0% | 0% | 1.02 | 1 | 1 | 47 (17%) | 8 | 0 | 39 | 25 | 1.47 |
| map corners | opp | 17 | 403 | 315 | 18.5 | 0.66 | 48 | 45 | 48 | 0% | 1% | 1.12 | 6 | 6 | 88 (22%) | 4 | 0 | 84 | 129 | 7.59 |
| map elkring | us | 14 | 291 | 281 | 20.1 | 0.78 | 36 | 38 | 36 | 0% | 1% | 1.00 | 27 | 27 | 10 (3%) | 0 | 0 | 10 | 1 | 0.07 |
| map elkring | opp | 14 | 337 | 313 | 22.4 | 0.78 | 36 | 41 | 72 | 0% | 2% | 1.14 | 19 | 18 | 24 (7%) | 3 | 0 | 21 | 17 | 1.21 |
| map expanse | us | 17 | 415 | 403 | 23.7 | 1.69 | 48 | 40 | 48 | 0% | 3% | 1.00 | 9 | 9 | 12 (3%) | 0 | 0 | 12 | 0 | 0.00 |
| map expanse | opp | 17 | 325 | 324 | 19.1 | 1.37 | 48 | 49 | 70 | 0% | 4% | 1.23 | 9 | 7 | 1 (0%) | 0 | 0 | 1 | 1 | 0.06 |
| map interlock | us | 13 | 331 | 299 | 23.0 | 1.06 | 22 | 36 | 72 | 0% | 0% | 1.03 | 20 | 20 | 32 (10%) | 2 | 0 | 30 | 16 | 1.23 |
| map interlock | opp | 13 | 300 | 244 | 18.8 | 0.91 | 40 | 47 | 72 | 0% | 2% | 1.27 | 20 | 13 | 56 (19%) | 7 | 0 | 49 | 37 | 2.85 |
| map lanes | us | 18 | 525 | 512 | 28.4 | 1.31 | 24 | 29 | 48 | 0% | 0% | 1.24 | 5 | 5 | 13 (2%) | 1 | 0 | 12 | 7 | 0.39 |
| map lanes | opp | 18 | 560 | 554 | 30.8 | 1.36 | 24 | 32 | 48 | 0% | 0% | 1.33 | 8 | 6 | 6 (1%) | 1 | 0 | 5 | 15 | 0.83 |
| map monolith | us | 13 | 305 | 283 | 21.8 | 0.88 | 44 | 41 | 44 | 0% | 0% | 1.12 | 27 | 26 | 22 (7%) | 2 | 0 | 20 | 37 | 2.85 |
| map monolith | opp | 13 | 293 | 274 | 21.1 | 0.84 | 44 | 45 | 66 | 0% | 1% | 1.39 | 28 | 18 | 19 (6%) | 0 | 0 | 19 | 4 | 0.31 |
| map packs | us | 21 | 373 | 362 | 17.2 | 1.05 | 44 | 45 | 48 | 0% | 0% | 1.00 | 5 | 5 | 11 (3%) | 4 | 0 | 7 | 2 | 0.10 |
| map packs | opp | 21 | 448 | 439 | 20.9 | 1.18 | 44 | 45 | 48 | 0% | 0% | 1.04 | 7 | 7 | 9 (2%) | 0 | 0 | 9 | 5 | 0.24 |
| map rows | us | 18 | 262 | 239 | 13.3 | 0.66 | 66 | 67 | 66 | 0% | 0% | 1.03 | 14 | 13 | 23 (9%) | 0 | 0 | 23 | 5 | 0.28 |
| map rows | opp | 18 | 264 | 263 | 14.6 | 0.73 | 66 | 71 | 66 | 0% | 8% | 1.13 | 16 | 16 | 1 (0%) | 0 | 0 | 1 | 1 | 0.06 |
| win | us | 59 | 1602 | 1519 | 25.7 | 1.17 | 36 | 40 | 66 | 0% | 2% | 1.09 | 11 | 10 | 83 (5%) | 7 | 0 | 76 | 55 | 0.93 |
| win | opp | 59 | 1090 | 993 | 16.8 | 0.80 | 44 | 43 | 70 | 0% | 2% | 1.21 | 13 | 11 | 97 (9%) | 20 | 0 | 77 | 114 | 1.93 |
| loss | us | 91 | 1654 | 1538 | 16.9 | 0.85 | 44 | 40 | 66 | 0% | 0% | 1.10 | 11 | 10 | 116 (7%) | 17 | 0 | 99 | 62 | 0.68 |
| loss | opp | 91 | 2216 | 2063 | 22.7 | 1.00 | 44 | 45 | 70 | 0% | 3% | 1.22 | 12 | 10 | 153 (7%) | 6 | 0 | 147 | 170 | 1.87 |
| opp top10 | us | 50 | 914 | 856 | 17.1 | 0.91 | 44 | 39 | 66 | 0% | 1% | 1.11 | 11 | 10 | 58 (6%) | 7 | 0 | 51 | 16 | 0.32 |
| opp top10 | opp | 50 | 1093 | 1021 | 20.4 | 0.98 | 44 | 47 | 72 | 0% | 3% | 1.26 | 12 | 10 | 72 (7%) | 2 | 0 | 70 | 102 | 2.04 |
| opp 11-20 | us | 50 | 1178 | 1103 | 22.1 | 1.04 | 36 | 39 | 66 | 0% | 2% | 1.09 | 11 | 10 | 75 (6%) | 11 | 0 | 64 | 44 | 0.88 |
| opp 11-20 | opp | 50 | 1145 | 1063 | 21.3 | 0.98 | 44 | 43 | 70 | 0% | 2% | 1.18 | 11 | 9 | 82 (7%) | 9 | 0 | 73 | 78 | 1.56 |
| opp 21-30 | us | 45 | 1027 | 964 | 21.4 | 0.97 | 44 | 41 | 66 | 0% | 1% | 1.09 | 11 | 10 | 63 (6%) | 5 | 0 | 58 | 55 | 1.22 |
| opp 21-30 | opp | 45 | 995 | 906 | 20.1 | 0.85 | 44 | 44 | 66 | 0% | 1% | 1.23 | 13 | 10 | 89 (9%) | 12 | 0 | 77 | 100 | 2.22 |
| opp other | us | 5 | 137 | 134 | 26.8 | 1.39 | 36 | 38 | 58 | 0% | 1% | 1.05 | 16 | 13 | 3 (2%) | 1 | 0 | 2 | 2 | 0.40 |
| opp other | opp | 5 | 73 | 66 | 13.2 | 0.66 | 36 | 37 | 48 | 0% | 0% | 1.09 | 19 | 16 | 7 (10%) | 3 | 0 | 4 | 4 | 0.80 |

### Bag distribution at tribute completion (count), us vs opp

| team | tributes | <=10 | 11-22 | 23-44 | 45-66 | 67-100 | >100 |
|---|---|---|---|---|---|---|---|
| us | 3057 | 0 | 802 | 1303 | 811 | 107 | 34 |
| opp | 3056 | 0 | 568 | 1290 | 864 | 263 | 71 |

### Recall as a teleport: captures followed by a recall start within [-5,+3] rounds; cost comparison walk-to-altar vs 5+spawn-to-altar

| split | team | captures | followed by recall | % | walk camp->altar med | 5+spawn->altar med | captures where recall is shorter | ..of which recalled | captures where walking is shorter | ..of which recalled | gems carried on recalled captures med |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 3676 | 1837 | 50% | 9 | 20 | 685 | 378 (55%) | 2991 | 1459 (49%) | 36 |
| all | opp | 4003 | 1029 | 26% | 9 | 20 | 694 | 329 (47%) | 3309 | 700 (21%) | 44 |
| map collision | us | 619 | 215 | 35% | 7 | 24 | 1 | 1 (100%) | 618 | 214 (35%) | 22 |
| map collision | opp | 565 | 137 | 24% | 11 | 24 | 25 | 20 (80%) | 540 | 117 (22%) | 44 |
| map corners | us | 255 | 60 | 24% | 2 | 22 | 37 | 31 (84%) | 218 | 29 (13%) | 22 |
| map corners | opp | 382 | 74 | 19% | 2 | 22 | 56 | 16 (29%) | 326 | 58 (18%) | 36 |
| map elkring | us | 333 | 285 | 86% | 13 | 26 | 0 | 0 (0%) | 333 | 285 (86%) | 36 |
| map elkring | opp | 380 | 101 | 27% | 13 | 26 | 0 | 0 (0%) | 380 | 101 (27%) | 36 |
| map expanse | us | 424 | 225 | 53% | 8 | 10 | 48 | 14 (29%) | 376 | 211 (56%) | 22 |
| map expanse | opp | 419 | 64 | 15% | 8 | 10 | 36 | 5 (14%) | 383 | 59 (15%) | 36 |
| map interlock | us | 357 | 222 | 62% | 13 | 20 | 0 | 0 (0%) | 357 | 222 (62%) | 22 |
| map interlock | opp | 321 | 38 | 12% | 13 | 20 | 0 | 0 (0%) | 321 | 38 (12%) | 22 |
| map lanes | us | 682 | 53 | 8% | 6 | 10 | 200 | 42 (21%) | 482 | 11 (2%) | 44 |
| map lanes | opp | 765 | 54 | 7% | 6 | 10 | 161 | 27 (17%) | 604 | 27 (4%) | 36 |
| map monolith | us | 344 | 287 | 83% | 12 | 28 | 0 | 0 (0%) | 344 | 287 (83%) | 44 |
| map monolith | opp | 403 | 125 | 31% | 15 | 28 | 0 | 0 (0%) | 403 | 125 (31%) | 44 |
| map packs | us | 377 | 229 | 61% | 8 | 6 | 220 | 112 (51%) | 157 | 117 (75%) | 44 |
| map packs | opp | 458 | 213 | 47% | 8 | 6 | 234 | 106 (45%) | 224 | 107 (48%) | 44 |
| map rows | us | 285 | 261 | 92% | 24 | 13 | 179 | 178 (99%) | 106 | 83 (78%) | 66 |
| map rows | opp | 310 | 223 | 72% | 24 | 13 | 182 | 155 (85%) | 128 | 68 (53%) | 66 |
| win | us | 1716 | 879 | 51% | 9 | 21 | 223 | 120 (54%) | 1493 | 759 (51%) | 36 |
| win | opp | 1438 | 292 | 20% | 11 | 20 | 182 | 84 (46%) | 1256 | 208 (17%) | 44 |
| loss | us | 1960 | 958 | 49% | 9 | 13 | 462 | 258 (56%) | 1498 | 700 (47%) | 44 |
| loss | opp | 2565 | 737 | 29% | 9 | 13 | 512 | 245 (48%) | 2053 | 492 (24%) | 44 |
| opp top10 | us | 1076 | 568 | 53% | 9 | 20 | 211 | 120 (57%) | 865 | 448 (52%) | 36 |
| opp top10 | opp | 1339 | 365 | 27% | 9 | 20 | 254 | 113 (44%) | 1085 | 252 (23%) | 44 |
| opp 11-20 | us | 1321 | 647 | 49% | 9 | 13 | 241 | 124 (51%) | 1080 | 523 (48%) | 36 |
| opp 11-20 | opp | 1361 | 311 | 23% | 9 | 13 | 232 | 114 (49%) | 1129 | 197 (17%) | 44 |
| opp 21-30 | us | 1137 | 554 | 49% | 9 | 20 | 228 | 130 (57%) | 909 | 424 (47%) | 36 |
| opp 21-30 | opp | 1209 | 348 | 29% | 9 | 20 | 207 | 102 (49%) | 1002 | 246 (25%) | 44 |
| opp other | us | 142 | 68 | 48% | 9 | 22 | 5 | 4 (80%) | 137 | 64 (47%) | 22 |
| opp other | opp | 94 | 5 | 5% | 12 | 22 | 1 | 0 (0%) | 93 | 5 (5%) | 22 |

### Recalls: per game, hp at start, gems carried, interrupted/died, and what happened after arrival (purchase within 2 rounds)

| split | team | recall starts | per game | arrived | interrupted/died | arrivals with hp>=70% | hp frac med | gems carried med | % carrying gems | gold carried med | arrival followed by purchase |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 3714 | 24.8 | 3528 | 186 | 33% | 0.51 | 0 | 16% | 0 | 67% |
| all | opp | 3472 | 23.1 | 3274 | 198 | 28% | 0.43 | 0 | 36% | 50 | 64% |
| map collision | us | 609 | 32.1 | 567 | 42 | 32% | 0.45 | 0 | 23% | 10 | 72% |
| map collision | opp | 647 | 34.1 | 580 | 67 | 22% | 0.38 | 22 | 53% | 90 | 68% |
| map corners | us | 366 | 21.5 | 302 | 64 | 6% | 0.35 | 0 | 16% | 0 | 34% |
| map corners | opp | 600 | 35.3 | 558 | 42 | 7% | 0.31 | 0 | 27% | 10 | 41% |
| map elkring | us | 627 | 44.8 | 604 | 23 | 31% | 0.51 | 0 | 19% | 10 | 61% |
| map elkring | opp | 491 | 35.1 | 466 | 25 | 29% | 0.47 | 0 | 24% | 55 | 62% |
| map expanse | us | 254 | 14.9 | 254 | 0 | 32% | 0.53 | 0 | 0% | 0 | 84% |
| map expanse | opp | 144 | 8.5 | 144 | 0 | 27% | 0.55 | 0 | 29% | 90 | 79% |
| map interlock | us | 366 | 28.2 | 351 | 15 | 45% | 0.65 | 0 | 18% | 0 | 68% |
| map interlock | opp | 211 | 16.2 | 202 | 9 | 15% | 0.34 | 0 | 36% | 90 | 63% |
| map lanes | us | 200 | 11.1 | 198 | 2 | 12% | 0.38 | 0 | 24% | 90 | 60% |
| map lanes | opp | 212 | 11.8 | 202 | 10 | 19% | 0.40 | 0 | 42% | 20 | 57% |
| map monolith | us | 404 | 31.1 | 402 | 2 | 38% | 0.64 | 0 | 10% | 0 | 81% |
| map monolith | opp | 313 | 24.1 | 305 | 8 | 32% | 0.53 | 0 | 35% | 90 | 77% |
| map packs | us | 493 | 23.5 | 455 | 38 | 38% | 0.58 | 0 | 8% | 10 | 70% |
| map packs | opp | 517 | 24.6 | 481 | 36 | 42% | 0.56 | 0 | 27% | 50 | 70% |
| map rows | us | 395 | 21.9 | 395 | 0 | 44% | 0.67 | 0 | 16% | 0 | 72% |
| map rows | opp | 337 | 18.7 | 336 | 1 | 59% | 0.79 | 0 | 50% | 270 | 80% |
| win | us | 1603 | 27.2 | 1551 | 52 | 36% | 0.55 | 0 | 15% | 0 | 74% |
| win | opp | 1266 | 21.5 | 1157 | 109 | 23% | 0.39 | 0 | 36% | 35 | 62% |
| loss | us | 2111 | 23.2 | 1977 | 134 | 30% | 0.49 | 0 | 17% | 0 | 62% |
| loss | opp | 2206 | 24.2 | 2117 | 89 | 30% | 0.47 | 0 | 36% | 50 | 66% |
| opp top10 | us | 1218 | 24.4 | 1136 | 82 | 32% | 0.51 | 0 | 17% | 0 | 65% |
| opp top10 | opp | 1127 | 22.5 | 1045 | 82 | 29% | 0.48 | 0 | 40% | 60 | 67% |
| opp 11-20 | us | 1278 | 25.6 | 1231 | 47 | 34% | 0.51 | 0 | 16% | 0 | 69% |
| opp 11-20 | opp | 1136 | 22.7 | 1065 | 71 | 30% | 0.42 | 0 | 34% | 90 | 68% |
| opp 21-30 | us | 1106 | 24.6 | 1049 | 57 | 31% | 0.51 | 0 | 15% | 0 | 68% |
| opp 21-30 | opp | 1126 | 25.0 | 1082 | 44 | 27% | 0.41 | 0 | 33% | 20 | 59% |
| opp other | us | 112 | 22.4 | 112 | 0 | 39% | 0.63 | 0 | 4% | 5 | 77% |
| opp other | opp | 83 | 16.6 | 82 | 1 | 0% | 0.33 | 0 | 30% | 35 | 52% |


## Q6 Lost time

### Share of champion-rounds by state (all rounds incl. dead), us vs opp

| split | team | champ-rounds | walk | camp | fight | tribute | recall | shop | idle | cast_other | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 357905 | 46.4% | 19.3% | 2.1% | 4.2% | 5.3% | 0.7% | 8.4% | 0.2% | 13.6% |
| all | opp | 362535 | 47.6% | 18.8% | 2.0% | 4.7% | 7.3% | 0.7% | 9.6% | 0.3% | 9.0% |
| map collision | us | 56480 | 41.5% | 13.9% | 2.9% | 3.4% | 5.5% | 0.8% | 9.5% | 0.3% | 22.3% |
| map collision | opp | 53436 | 45.2% | 14.9% | 2.4% | 3.4% | 7.9% | 0.8% | 8.1% | 0.4% | 16.8% |
| map corners | us | 48085 | 44.8% | 8.1% | 5.2% | 2.8% | 4.1% | 0.3% | 7.4% | 0.2% | 27.1% |
| map corners | opp | 55015 | 49.0% | 10.1% | 4.2% | 3.8% | 10.2% | 0.5% | 9.2% | 0.3% | 12.7% |
| map elkring | us | 41410 | 46.3% | 20.5% | 2.0% | 3.0% | 7.7% | 0.9% | 6.9% | 0.2% | 12.5% |
| map elkring | opp | 46597 | 45.9% | 20.1% | 1.6% | 3.4% | 5.5% | 0.7% | 8.3% | 0.5% | 13.9% |
| map expanse | us | 23796 | 47.0% | 32.0% | 0.0% | 7.7% | 5.4% | 0.9% | 7.0% | 0.0% | 0.0% |
| map expanse | opp | 23796 | 45.5% | 30.9% | 0.1% | 7.2% | 3.1% | 0.5% | 12.4% | 0.1% | 0.3% |
| map interlock | us | 31225 | 48.9% | 20.0% | 1.9% | 4.8% | 6.1% | 0.8% | 8.0% | 0.1% | 9.4% |
| map interlock | opp | 29169 | 48.8% | 19.1% | 2.2% | 6.0% | 3.7% | 0.6% | 11.2% | 0.2% | 8.2% |
| map lanes | us | 43068 | 50.0% | 19.7% | 1.0% | 4.3% | 2.4% | 0.3% | 12.8% | 0.2% | 9.3% |
| map lanes | opp | 42122 | 53.0% | 16.7% | 1.8% | 5.1% | 7.7% | 0.4% | 12.0% | 0.2% | 3.1% |
| map monolith | us | 35022 | 54.3% | 21.0% | 0.9% | 4.1% | 5.8% | 1.0% | 5.2% | 0.1% | 7.7% |
| map monolith | opp | 34566 | 51.9% | 22.6% | 1.3% | 4.4% | 4.7% | 0.8% | 8.9% | 0.2% | 5.1% |
| map packs | us | 42564 | 36.7% | 23.0% | 2.6% | 4.4% | 5.8% | 0.8% | 7.7% | 0.2% | 18.8% |
| map packs | opp | 41579 | 43.2% | 19.0% | 2.4% | 5.5% | 9.8% | 1.0% | 8.4% | 0.1% | 10.6% |
| map rows | us | 36255 | 53.2% | 25.6% | 0.1% | 5.2% | 5.5% | 0.8% | 9.3% | 0.0% | 0.3% |
| map rows | opp | 36255 | 46.6% | 26.1% | 0.1% | 5.5% | 9.3% | 0.8% | 10.5% | 0.1% | 1.0% |
| win | us | 140703 | 48.3% | 20.9% | 2.2% | 5.2% | 5.8% | 0.9% | 8.5% | 0.2% | 8.1% |
| win | opp | 143046 | 47.0% | 18.4% | 1.6% | 3.8% | 5.1% | 0.6% | 9.5% | 0.3% | 13.7% |
| loss | us | 217202 | 45.2% | 18.2% | 2.0% | 3.5% | 5.0% | 0.6% | 8.2% | 0.1% | 17.1% |
| loss | opp | 219489 | 48.0% | 19.0% | 2.3% | 5.2% | 8.8% | 0.7% | 9.7% | 0.2% | 6.0% |
| opp top10 | us | 112335 | 44.8% | 18.9% | 2.1% | 3.7% | 5.5% | 0.7% | 8.3% | 0.1% | 15.9% |
| opp top10 | opp | 112607 | 43.4% | 18.9% | 2.1% | 5.2% | 13.0% | 0.7% | 8.8% | 0.2% | 7.7% |
| opp 11-20 | us | 121433 | 46.4% | 19.8% | 1.8% | 4.4% | 5.4% | 0.7% | 8.5% | 0.2% | 12.7% |
| opp 11-20 | opp | 120313 | 48.4% | 19.2% | 2.0% | 4.8% | 4.8% | 0.7% | 10.3% | 0.3% | 9.5% |
| opp 21-30 | us | 114369 | 47.6% | 18.5% | 2.5% | 4.2% | 4.9% | 0.7% | 8.2% | 0.2% | 13.2% |
| opp 21-30 | opp | 119008 | 50.2% | 17.8% | 2.0% | 4.2% | 4.8% | 0.7% | 9.9% | 0.2% | 10.2% |
| opp other | us | 9768 | 50.2% | 25.5% | 1.1% | 6.2% | 5.8% | 0.9% | 9.0% | 0.0% | 1.2% |
| opp other | opp | 10607 | 54.9% | 22.9% | 0.3% | 2.9% | 4.0% | 0.4% | 8.1% | 0.5% | 6.0% |

### Walking efficiency (moves between purpose points vs shortest path; Mite 0.75, 4.0 extra/leg; study25 0.80)

| split | team | legs | moves | shortest path | efficiency | extra moves/leg |
|---|---|---|---|---|---|---|
| all | us | 6727 | 109635 | 97047 | 0.89 | 1.9 |
| all | opp | 7058 | 111027 | 92772 | 0.84 | 2.6 |
| map collision | us | 1072 | 14039 | 12327 | 0.88 | 1.6 |
| map collision | opp | 895 | 12777 | 10805 | 0.85 | 2.2 |
| map corners | us | 476 | 8317 | 5820 | 0.70 | 5.2 |
| map corners | opp | 697 | 11823 | 8635 | 0.73 | 4.6 |
| map elkring | us | 612 | 11600 | 10092 | 0.87 | 2.5 |
| map elkring | opp | 693 | 12190 | 9809 | 0.80 | 3.4 |
| map expanse | us | 827 | 10545 | 11277 | 1.07 | -0.9 |
| map expanse | opp | 743 | 9906 | 9529 | 0.96 | 0.5 |
| map interlock | us | 656 | 11760 | 10235 | 0.87 | 2.3 |
| map interlock | opp | 565 | 9635 | 7091 | 0.74 | 4.5 |
| map lanes | us | 1194 | 16852 | 16559 | 0.98 | 0.2 |
| map lanes | opp | 1319 | 18581 | 16692 | 0.90 | 1.4 |
| map monolith | us | 627 | 14692 | 12861 | 0.88 | 2.9 |
| map monolith | opp | 676 | 12570 | 10837 | 0.86 | 2.6 |
| map packs | us | 739 | 7952 | 7667 | 0.96 | 0.4 |
| map packs | opp | 897 | 10911 | 8749 | 0.80 | 2.4 |
| map rows | us | 524 | 13878 | 10209 | 0.74 | 7.0 |
| map rows | opp | 573 | 12634 | 10625 | 0.84 | 3.5 |
| win | us | 3231 | 51149 | 44929 | 0.88 | 1.9 |
| win | opp | 2431 | 39024 | 31819 | 0.82 | 3.0 |
| loss | us | 3496 | 58486 | 52118 | 0.89 | 1.8 |
| loss | opp | 4627 | 72003 | 60953 | 0.85 | 2.4 |
| opp top10 | us | 1932 | 30325 | 27322 | 0.90 | 1.6 |
| opp top10 | opp | 2360 | 35736 | 29983 | 0.84 | 2.4 |
| opp 11-20 | us | 2421 | 38122 | 34675 | 0.91 | 1.4 |
| opp 11-20 | opp | 2423 | 37759 | 32053 | 0.85 | 2.4 |
| opp 21-30 | us | 2098 | 36880 | 31409 | 0.85 | 2.6 |
| opp 21-30 | opp | 2115 | 34489 | 28448 | 0.82 | 2.9 |
| opp other | us | 276 | 4308 | 3641 | 0.85 | 2.4 |
| opp other | opp | 160 | 3043 | 2288 | 0.75 | 4.7 |

### Deaths and respawn cost per map (death = 60 rounds dead)

| split | team | n | deaths | deaths/game | rounds dead | % of champ-rounds | gems not farmed while dead (dead rounds x gems/alive round) | gems dropped at death | per game |
|---|---|---|---|---|---|---|---|---|---|
| all | us | 150 | 858 | 5.7 | 48542 | 13.6% | 20227 | 8750 | 58 |
| all | opp | 150 | 581 | 3.9 | 32789 | 9.0% | 14132 | 8470 | 56 |
| map collision | us | 19 | 215 | 11.3 | 12579 | 22.3% | 3967 | 2402 | 126 |
| map collision | opp | 19 | 161 | 8.5 | 8995 | 16.8% | 3039 | 3838 | 202 |
| map corners | us | 17 | 230 | 13.5 | 13029 | 27.1% | 3998 | 1902 | 112 |
| map corners | opp | 17 | 121 | 7.1 | 7013 | 12.7% | 2158 | 1536 | 90 |
| map elkring | us | 14 | 91 | 6.5 | 5167 | 12.5% | 1709 | 1404 | 100 |
| map elkring | opp | 14 | 113 | 8.1 | 6488 | 13.9% | 2149 | 1062 | 76 |
| map expanse | us | 17 | 0 | 0.0 | 0 | 0.0% | 0 | 0 | 0 |
| map expanse | opp | 17 | 1 | 0.1 | 61 | 0.3% | 43 | 0 | 0 |
| map interlock | us | 13 | 56 | 4.3 | 2930 | 9.4% | 1246 | 1486 | 114 |
| map interlock | opp | 13 | 42 | 3.2 | 2386 | 8.2% | 1030 | 918 | 71 |
| map lanes | us | 18 | 68 | 3.8 | 4004 | 9.3% | 1656 | 304 | 17 |
| map lanes | opp | 18 | 26 | 1.4 | 1287 | 3.1% | 584 | 230 | 13 |
| map monolith | us | 13 | 49 | 3.8 | 2690 | 7.7% | 1012 | 630 | 48 |
| map monolith | opp | 13 | 32 | 2.5 | 1768 | 5.1% | 696 | 528 | 41 |
| map packs | us | 21 | 147 | 7.0 | 8022 | 18.8% | 3951 | 556 | 26 |
| map packs | opp | 21 | 79 | 3.8 | 4426 | 10.6% | 2368 | 358 | 17 |
| map rows | us | 18 | 2 | 0.1 | 121 | 0.3% | 60 | 66 | 4 |
| map rows | opp | 18 | 6 | 0.3 | 365 | 1.0% | 198 | 0 | 0 |
| win | us | 59 | 195 | 3.3 | 11348 | 8.1% | 5163 | 2502 | 42 |
| win | opp | 59 | 353 | 6.0 | 19636 | 13.7% | 7933 | 6146 | 104 |
| loss | us | 91 | 663 | 7.3 | 37194 | 17.1% | 14476 | 6248 | 69 |
| loss | opp | 91 | 228 | 2.5 | 13153 | 6.0% | 5881 | 2324 | 26 |
| opp top10 | us | 50 | 317 | 6.3 | 17815 | 15.9% | 7075 | 3122 | 62 |
| opp top10 | opp | 50 | 151 | 3.0 | 8624 | 7.7% | 4033 | 1912 | 38 |
| opp 11-20 | us | 50 | 273 | 5.5 | 15467 | 12.7% | 6625 | 2976 | 60 |
| opp 11-20 | opp | 50 | 204 | 4.1 | 11447 | 9.5% | 5060 | 3428 | 69 |
| opp 21-30 | us | 45 | 266 | 5.9 | 15138 | 13.2% | 6269 | 2608 | 58 |
| opp 21-30 | opp | 45 | 213 | 4.7 | 12082 | 10.2% | 4786 | 2762 | 61 |
| opp other | us | 5 | 2 | 0.4 | 122 | 1.2% | 62 | 44 | 9 |
| opp other | opp | 5 | 13 | 2.6 | 636 | 6.0% | 193 | 368 | 74 |

### Idle rounds: by type (share of alive rounds with no action), us

| team | type | alive rounds | walk | camp | fight | tribute | recall | shop | idle | cast_other |
|---|---|---|---|---|---|---|---|---|---|---|
| us | Cassi | 48214 | 53.6% | 25.0% | 1.6% | 3.7% | 3.8% | 0.5% | 11.6% | 0.2% |
| us | Issac | 48244 | 48.1% | 26.0% | 1.1% | 6.3% | 7.2% | 1.0% | 10.2% | 0.2% |
| us | Ren | 42866 | 50.7% | 20.5% | 4.2% | 5.6% | 9.0% | 1.1% | 8.6% | 0.3% |
| us | Stellar | 39596 | 54.6% | 18.4% | 4.8% | 4.1% | 5.7% | 0.8% | 11.3% | 0.3% |
| us | Ryth | 34499 | 58.7% | 20.2% | 2.3% | 4.1% | 6.2% | 0.8% | 7.5% | 0.1% |
| us | Tavi | 31508 | 55.0% | 23.9% | 2.3% | 2.9% | 4.1% | 0.6% | 11.1% | 0.1% |
| us | Vendetta | 25315 | 54.6% | 22.0% | 0.5% | 6.3% | 7.0% | 1.0% | 8.6% | 0.0% |
| us | Varg | 25750 | 57.0% | 22.6% | 0.5% | 6.7% | 5.9% | 1.0% | 6.1% | 0.2% |
| us | Prism | 13371 | 56.8% | 17.9% | 5.3% | 2.7% | 6.2% | 0.6% | 10.3% | 0.2% |
| opp | Cassi | 54620 | 52.4% | 24.8% | 1.5% | 3.1% | 7.3% | 0.4% | 10.1% | 0.4% |
| opp | Issac | 54636 | 48.4% | 22.6% | 1.5% | 5.9% | 9.2% | 0.8% | 11.4% | 0.2% |
| opp | Stellar | 49691 | 54.9% | 17.1% | 2.9% | 5.0% | 8.8% | 0.7% | 10.4% | 0.2% |
| opp | Ren | 36112 | 48.7% | 19.1% | 3.1% | 6.3% | 9.9% | 0.9% | 11.6% | 0.3% |
| opp | Varg | 34923 | 56.1% | 19.0% | 1.7% | 6.8% | 5.4% | 1.0% | 9.7% | 0.4% |
| opp | Tavi | 30107 | 56.9% | 20.0% | 2.9% | 4.0% | 4.0% | 1.0% | 11.1% | 0.2% |
| opp | Ryth | 26966 | 52.0% | 18.0% | 2.8% | 5.2% | 11.6% | 0.7% | 9.6% | 0.1% |
| opp | Vendetta | 25389 | 51.2% | 22.4% | 1.5% | 6.4% | 6.9% | 0.9% | 10.6% | 0.2% |
| opp | Prism | 8168 | 48.9% | 18.1% | 3.7% | 4.3% | 14.5% | 0.5% | 9.8% | 0.2% |
| opp | Willow | 5658 | 55.3% | 22.7% | 1.6% | 2.4% | 4.7% | 0.3% | 12.2% | 0.8% |
| opp | Marcella | 2248 | 55.3% | 19.8% | 3.4% | 4.0% | 5.5% | 0.7% | 11.0% | 0.1% |
| opp | VesperVale | 1228 | 53.2% | 24.8% | 3.2% | 4.2% | 6.0% | 0.4% | 8.1% | 0.1% |


## Q7 follow-ups

### Recall classification (arrived recalls), us vs opp

- us: heal(hp<50%) 1625 (46%), teleport(carries gems, tributes after) 1098 (31%), shop small (<90 gold) 670 (19%), other (no buy, no gems, hp>=50%) 135 (4%); gold at arrival med 0 (share >=90: 0%, >=150: 0%); hp at start med 0.53
- opp: heal(hp<50%) 1870 (57%), shop small (<90 gold) 691 (21%), teleport(carries gems, tributes after) 591 (18%), other (no buy, no gems, hp>=50%) 118 (4%), shop(hp>=50%, buys) 4 (0%); gold at arrival med 5 (share >=90: 1%, >=150: 0%); hp at start med 0.44

### Rounds lost on recalls after a capture where walking to the altar was shorter than 5 + spawn->altar

- us: 1396 such recalls, 13872 champion-rounds lost in total = 92 per game (9.9 per recall)
- opp: 689 such recalls, 6079 champion-rounds lost in total = 41 per game (8.8 per recall)

### Why tribute starts do not complete

- us: {'died': 24, 'no hit, no move (?)': 82, 'hit during channel': 89, 'moved away': 4}
- opp: {'died': 26, 'hit during channel': 174, 'moved away': 14, 'no hit, no move (?)': 36}

### Rows: largest detour legs for us (extra moves, match, type, moves, shortest): [(138, 'f5686c33', 'Cassi', 152, 14), (138, 'e6728afb', 'Cassi', 152, 14), (138, 'df0f60f1', 'Cassi', 152, 14), (138, 'cc910d4f', 'Cassi', 152, 14), (138, 'c3eed638', 'Cassi', 152, 14), (138, 'a17455eb', 'Cassi', 152, 14), (138, '9d948244', 'Cassi', 152, 14), (138, '8ac3e855', 'Cassi', 152, 14), (138, '78b0bef5', 'Cassi', 152, 14), (138, '78034945', 'Cassi', 152, 14), (138, '6d2039e7', 'Cassi', 152, 14), (138, '67768aef', 'Cassi', 152, 14)]
legs with >=12 extra moves: 66

## Q8 Recall classes (corrected gold at arrival = snapshot gold + purchases that round)

- us: shop (>=90 gold, buys) 1692 (48%), heal (hp<50% at start) 1625 (46%), no reason visible 144 (4%), teleport (gems, tribute after) 43 (1%), shop small (<90 gold) 24 (1%); gold at arrival med 90, >=90: 61%, >=150: 39%
- opp: heal (hp<50% at start) 1870 (57%), shop (>=90 gold, buys) 1218 (37%), no reason visible 120 (4%), teleport (gems, tribute after) 37 (1%), shop small (<90 gold) 29 (1%); gold at arrival med 90, >=90: 57%, >=150: 40%

### Per map recall classes (us / opp counts)

| map | heal (hp<50% at start) | shop (>=90 gold, buys) | teleport (gems, tribute after) | shop small (<90 gold) | no reason visible |
|---|---|---|---|---|---|
| collision | 310 / 383 | 243 / 164 | 0 / 0 | 3 / 7 | 11 / 26 |
| corners | 221 / 461 | 46 / 60 | 4 / 3 | 6 / 9 | 25 / 25 |
| elkring | 291 / 245 | 287 / 185 | 1 / 5 | 4 / 3 | 21 / 28 |
| expanse | 95 / 65 | 143 / 70 | 15 / 6 | 0 / 0 | 1 / 3 |
| interlock | 108 / 144 | 201 / 49 | 7 / 0 | 2 / 0 | 33 / 9 |
| lanes | 134 / 133 | 57 / 60 | 1 / 6 | 0 / 0 | 6 / 3 |
| monolith | 154 / 145 | 239 / 157 | 0 / 0 | 1 / 1 | 8 / 2 |
| packs | 182 / 209 | 229 / 233 | 15 / 16 | 8 / 8 | 21 / 15 |
| rows | 130 / 85 | 247 / 240 | 0 / 1 | 0 / 1 | 18 / 9 |

### Rounds lost on recalls after a capture where walking was shorter, by recall class (champion-rounds, total over 150 games; per game)

| team | recall class | recalls | rounds lost | per game |
|---|---|---|---|---|
| us | heal (hp<50% at start) | 202 | 2070 | 13.8 |
| us | shop (>=90 gold, buys) | 1143 | 11231 | 74.9 |
| us | teleport (gems, tribute after) | 24 | 172 | 1.1 |
| us | shop small (<90 gold) | 4 | 82 | 0.5 |
| us | no reason visible | 19 | 252 | 1.7 |
| opp | heal (hp<50% at start) | 123 | 1134 | 7.6 |
| opp | shop (>=90 gold, buys) | 542 | 4683 | 31.2 |
| opp | teleport (gems, tribute after) | 12 | 111 | 0.7 |
| opp | shop small (<90 gold) | 0 | 0 | 0.0 |
| opp | no reason visible | 2 | 40 | 0.3 |


## Q9 Capture credit, shop trips, rows per type

### Attackers that helped kill a group but were not on the capture tiles (no gems/gold), per type; and credited captures per champion-game

| team | type | champion-games | credited captures/g | group kills helped | ..not credited | % not credited | gold earned/g |
|---|---|---|---|---|---|---|---|
| us | Cassi | 119 | 4.1 | 989 | 523 | 53% | 265 |
| us | Issac | 119 | 6.7 | 1036 | 256 | 25% | 657 |
| us | Ren | 84 | 6.8 | 754 | 216 | 29% | 814 |
| us | Stellar | 84 | 4.6 | 918 | 547 | 60% | 547 |
| us | Ryth | 80 | 4.4 | 551 | 212 | 38% | 631 |
| us | Tavi | 75 | 3.4 | 720 | 475 | 66% | 224 |
| us | Vendetta | 66 | 6.1 | 505 | 109 | 22% | 611 |
| us | Varg | 66 | 5.1 | 426 | 99 | 23% | 809 |
| us | Prism | 31 | 2.9 | 241 | 159 | 66% | 392 |
| opp | Cassi | 128 | 3.4 | 1332 | 942 | 71% | 284 |
| opp | Issac | 128 | 6.3 | 1198 | 441 | 37% | 655 |
| opp | Stellar | 107 | 5.1 | 1300 | 799 | 61% | 555 |
| opp | Varg | 79 | 6.1 | 644 | 181 | 28% | 956 |
| opp | Ren | 74 | 7.5 | 852 | 350 | 41% | 800 |
| opp | Tavi | 63 | 5.1 | 745 | 464 | 62% | 501 |
| opp | Vendetta | 59 | 6.6 | 528 | 158 | 30% | 834 |
| opp | Ryth | 58 | 5.6 | 596 | 295 | 49% | 644 |
| opp | Prism | 16 | 5.0 | 244 | 169 | 69% | 342 |
| opp | Willow | 13 | 1.9 | 124 | 104 | 84% | 253 |
| opp | Marcella | 5 | 4.8 | 41 | 18 | 44% | 733 |
| opp | VesperVale | 3 | 4.7 | 29 | 16 | 55% | 412 |

### Cassi per map: credited captures/g, gold earned/g, buys/g (us vs opp)

| map | n | us Cassi captures/g | gold/g | buys/g | opp Cassi captures/g | gold/g | buys/g |
|---|---|---|---|---|---|---|---|
| collision | 19 | 5.2 | 513 | 16.9 | 4.7 | 501 | 10.0 |
| corners | 17 | - | - | - | 2.9 | 167 | 2.9 |
| elkring | 14 | - | - | - | 2.2 | 412 | 6.3 |
| expanse | 17 | 5.0 | 95 | 3.2 | 4.5 | 79 | 1.2 |
| interlock | 13 | 5.2 | 298 | 9.9 | 2.6 | 261 | 3.9 |
| lanes | 18 | 6.5 | 63 | 1.3 | 6.0 | 108 | 1.3 |
| monolith | 13 | 3.2 | 318 | 10.2 | 3.1 | 341 | 3.2 |
| packs | 21 | 2.8 | 321 | 10.4 | 2.5 | 333 | 5.6 |
| rows | 18 | 0.9 | 240 | 8.0 | 1.6 | 393 | 7.2 |

### Shopping trips (recall at hp>=50% followed by a purchase within 3 rounds of arrival): count per game and rounds from recall start to the next capture or tribute

| split | team | shop trips | per game | rounds to next capture/tribute med | mean | champion-rounds per game |
|---|---|---|---|---|---|---|
| all | us | 1734 | 11.6 | 29 | 37.9 | 403 |
| all | opp | 1259 | 8.4 | 31 | 41.5 | 327 |
| map collision | us | 246 | 12.9 | 33 | 46.4 | 566 |
| map collision | opp | 171 | 9.0 | 35 | 54.9 | 468 |
| map corners | us | 53 | 3.1 | 47 | 67.4 | 178 |
| map corners | opp | 69 | 4.1 | 49 | 65.7 | 259 |
| map elkring | us | 291 | 20.8 | 35 | 51.0 | 944 |
| map elkring | opp | 188 | 13.4 | 38 | 57.6 | 704 |
| map expanse | us | 143 | 8.4 | 17 | 18.0 | 147 |
| map expanse | opp | 70 | 4.1 | 28 | 37.0 | 139 |
| map interlock | us | 204 | 15.7 | 29 | 39.2 | 570 |
| map interlock | opp | 49 | 3.8 | 35 | 43.5 | 157 |
| map lanes | us | 58 | 3.2 | 19 | 41.0 | 114 |
| map lanes | opp | 61 | 3.4 | 20 | 32.8 | 98 |
| map monolith | us | 240 | 18.5 | 35 | 40.2 | 661 |
| map monolith | opp | 158 | 12.2 | 36 | 42.2 | 477 |
| map packs | us | 252 | 12.0 | 13 | 25.3 | 288 |
| map packs | opp | 252 | 12.0 | 15 | 24.8 | 283 |
| map rows | us | 247 | 13.7 | 25 | 29.8 | 383 |
| map rows | opp | 241 | 13.4 | 25 | 32.8 | 417 |
| win | us | 836 | 14.2 | 29 | 36.1 | 489 |
| win | opp | 368 | 6.2 | 33 | 50.5 | 294 |
| loss | us | 898 | 9.9 | 28 | 39.7 | 348 |
| loss | opp | 891 | 9.8 | 30 | 37.8 | 348 |
| opp top10 | us | 539 | 10.8 | 28 | 38.7 | 380 |
| opp top10 | opp | 431 | 8.6 | 28 | 37.5 | 303 |
| opp 11-20 | us | 599 | 12.0 | 28 | 38.2 | 424 |
| opp 11-20 | opp | 429 | 8.6 | 31 | 42.7 | 342 |
| opp 21-30 | us | 526 | 11.7 | 29 | 37.4 | 404 |
| opp 21-30 | opp | 398 | 8.8 | 32 | 44.4 | 372 |
| opp other | us | 70 | 14.0 | 28 | 32.1 | 423 |
| opp other | opp | 1 | 0.2 | nan | nan | 0 |

### Gold at the start of a shopping trip is not observable (recall starts before the capture pays); gold spent on the trip instead

| team | shop trips | gold spent med | <90 | 90-149 | 150-239 | 240-329 | >=330 |
|---|---|---|---|---|---|---|---|
| us | 1734 | 180 | 2% | 32% | 48% | 17% | 0% |
| opp | 1259 | 180 | 5% | 17% | 51% | 24% | 3% |

### Rows: per champion type, states and credited captures (us vs opp)

| team | type | n | captures/g | gems/g | tributes/g | recalls/g | walk | camp | tribute | recall | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|
| us | Vendetta | 18 | 3.2 | 182 | 2.6 | 6.1 | 56% | 23% | 5% | 8% | 8% |
| us | Varg | 18 | 5.6 | 367 | 5.9 | 5.6 | 57% | 20% | 10% | 7% | 5% |
| us | Cassi | 18 | 0.9 | 59 | 1.0 | 0.9 | 52% | 26% | 2% | 1% | 18% |
| us | Issac | 18 | 3.7 | 214 | 2.7 | 5.8 | 44% | 32% | 5% | 7% | 10% |
| us | Ryth | 18 | 2.6 | 169 | 2.4 | 3.6 | 58% | 27% | 4% | 5% | 6% |
| opp | Cassi | 18 | 1.6 | 95 | 1.3 | 2.3 | 48% | 29% | 2% | 8% | 11% |
| opp | Issac | 18 | 4.2 | 262 | 3.5 | 4.9 | 44% | 27% | 7% | 10% | 10% |
| opp | Varg | 15 | 5.1 | 328 | 4.6 | 4.7 | 52% | 21% | 8% | 6% | 11% |
| opp | Vendetta | 11 | 4.8 | 300 | 3.8 | 4.9 | 47% | 25% | 8% | 6% | 12% |
| opp | Stellar | 8 | 1.8 | 107 | 1.6 | 2.2 | 44% | 27% | 3% | 14% | 12% |
| opp | Ryth | 6 | 3.5 | 220 | 2.7 | 4.0 | 43% | 23% | 6% | 18% | 9% |
| opp | Ren | 5 | 4.8 | 310 | 4.4 | 5.4 | 38% | 22% | 7% | 22% | 10% |
| opp | Willow | 5 | 1.6 | 106 | 1.4 | 1.6 | 53% | 36% | 3% | 2% | 5% |
| opp | Tavi | 4 | 2.8 | 146 | 2.0 | 1.2 | 50% | 32% | 3% | 2% | 13% |

### Rows: team captures by round bins (per game), us vs opp; and gems in hand at game end

| team | r0-49 | r50-99 | r100-149 | r150-199 | r200-249 | r250-299 | r300-349 | r350-399 | r400+ | gems in hand at end |
|---|---|---|---|---|---|---|---|---|---|---|
| us | 1.00 | 1.00 | 3.00 | 1.89 | 1.00 | 2.00 | 3.67 | 1.61 | 0.67 | 95 |
| opp | 1.06 | 2.11 | 2.11 | 2.11 | 2.22 | 2.50 | 2.44 | 2.11 | 0.56 | 51 |


## Q10 Camp utilization: for the own-side gem groups each team farms (>=50% of games), share of rounds the group is respawning / up and untouched / under attack

| map | us farmed own groups | respawning | up & untouched | under attack | opp farmed own groups | respawning | up & untouched | under attack |
|---|---|---|---|---|---|---|---|---|
| collision | 3 | 47% | 43% | 10% | 5 | 32% | 61% | 7% |
| corners | 1 | 19% | 74% | 6% | 2 | 19% | 75% | 6% |
| elkring | 5 | 58% | 29% | 13% | 5 | 55% | 33% | 13% |
| expanse | 9 | 40% | 47% | 13% | 7 | 47% | 39% | 14% |
| interlock | 5 | 58% | 28% | 14% | 4 | 59% | 26% | 15% |
| lanes | 10 | 51% | 41% | 8% | 8 | 53% | 40% | 6% |
| monolith | 7 | 43% | 43% | 14% | 7 | 46% | 39% | 15% |
| packs | 2 | 50% | 34% | 16% | 2 | 52% | 31% | 16% |
| rows | 3 | 55% | 25% | 20% | 3 | 60% | 19% | 21% |

