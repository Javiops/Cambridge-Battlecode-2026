# Recall, healing, tribute and death avoidance — Mite (#1) vs Univardisty of Shingtonwash (#2)

Data: 101 decoded replays of 2026-10-15 (54 Mite games, 54 Univardisty games, 9 maps x 6). Scripts: `$S/reports/scripts_recall/` (`recalls.py` start/outcome tracking, `reasons.py` classification, `tribute.py`, `deaths.py`, `respawn.py`, `refine.py`, `locks.py`, `misc.py`; `loader.py` reuses the loader pattern of `tools/micro/disengage.py`). Raw rows: `recall_rows.json`, `tribute_rows.json`, `death_rows.json` in the same folder.

## 0. How recalls were detected (and what the step kinds mean)

The compact format carries an explicit recall-start step: **`k 11` at ph 10, no effect**. Every completed recall is a `k 11` followed exactly 5 rounds later by a `ph 14 k 4` position jump to the spawn area (1278/1278 Mite arrivals and 1011/1011 Univardisty arrivals have duration 5; nobody owns a Home emblem). So interrupted recalls are not inferred from "standing still": they are `k 11` starts with no arrival, classified by the first thing that happened to that champion afterwards:

| outcome of a `k 11` start | detection |
|---|---|
| arrived | `ph 14 k 4` jump of >1 tile to spawn, r+5 |
| hit_foe / hit_camp | first negative `hp` eff on the champion, source = acting champion of the other team / camp (`ak 2`) |
| died | `alive 0` eff before arrival |
| moved (voluntary cancel) | the champion itself does a `ph 10 k 4` move before r+5 |
| attacked (cancel to fight) | the champion itself attacks/casts with an effect before r+5 |

Other kinds used: `k 12` tribute start, `ph 14 k 18` tribute completion (gems -> 0), `k 13` purchase, `ph 13 k 3` spawn regen, `ph 14 k 1` respawn, `k 20` = altar lock placement (inferred: always within 2 tiles of an altar, and in 1c547a16 the opponent's `k 20` at r988 is the round after Univardisty's last tribute start; afterwards Univardisty never tributed again). All `k 13` purchases happen on spawn or while dead except Tavi's (Tavi buys anywhere, 300+ cases; kit).

## 1. Completed recalls by reason

Reason = first matching flag (state at the start round): **escape** (foe within 5 and hit by a foe in the last 3 rounds) > **heal** (hp < 50%) > **bank** (gems > 0 and the next thing after leaving spawn is a tribute) > **shop** (gold >= 30 and bought on spawn) > **reposition** (none of the above).

| | Mite (1278 arrivals) | Univardisty (1011 arrivals) |
|---|---|---|
| heal | 716 (56%) | 575 (57%) |
| shop | 321 (25%) | 132 (13%) |
| reposition | 178 (14%) | 171 (17%) |
| bank | 45 (3.5%) | 82 (8%) |
| escape | 18 (1.4%) | 51 (5%) |

Flags overlap: Mite heal+shop 278, Univardisty heal+shop 166, heal+bank 51/46 (Uni). 

Thresholds at recall start (median / p10 / p90):

| reason | team | hp% | gems | gold | dist nearest foe | dist spawn (BFS) | dist altar | spawn stay | bought on spawn | next action |
|---|---|---|---|---|---|---|---|---|---|---|
| heal | Mite | 24 / 8 / 44 | 0 / p90 36 | 17 | 8 / p10 7 | 14 | 8 | 2 | 52% | camp 52%, fight 24%, tribute 13% |
| heal | Uni | 26 / 11 / 39 | 0 / p90 66 | 20 | 10 / p10 7 | 14 | 10 | 4 | 50% | camp 49%, tribute 21%, fight 22% |
| shop | Mite | 77 / 53 / 98 | 22 | 180 | 13 / p10 7 | 22 | 1 | 2 | 100% | camp 80% |
| shop | Uni | 76 / 57 / 99 | 22 | 190 | 16 / p10 9 | 20 | 8 | 4 | 100% | camp 69% |
| bank | Mite | 88 / 55 / 100 | 58 / p90 99 | 5 | 25 | 25 | 14 | 3 | 80% | tribute 100% |
| bank | Uni | 78 / 60 / 96 | 44 / p90 66 | 58 | 23 | 13 | 13 | 3 | 98% | tribute 100% |
| escape | Mite | 43 / 19 / 83 | 0 | 55 | 5 / p10 2 | 22 | 8 | 2 | 72% | camp 78% |
| escape | Uni | 33 / 16 / 51 | 0 | 0 | 5 / p10 3 | 18 | 6 | 1 | 37% | camp 41%, fight 41% |
| reposition | Mite | 93 / 66 / 100 | 0 (25/178 carry gems) | 0 | 16 / p10 7 | 15 | 10 | 3 | 54% | camp 57%, tribute 29% |
| reposition | Uni | 76 / 53 / 98 | 0 (20/171) | 10 | 20 / p10 11 | 15 | 14 | 3 | 88% | camp 40%, tribute 32%, fight 22% |

Hard thresholds found:
- **hp < 50% is a strict heal trigger for both teams**: among heal-only recalls the maximum hp% is 49 for every champion type on both teams (Mite: Cassi 49, Issac 49, Ren 49, Ryth 48, Stellar 48, Varg 48, Tavi 33; Uni: all 46-49). hp% histogram of all arrivals: Mite 0-49% = 728 (57%), 50-100% = 550; Uni 619 (61%) vs 392. Mite's heal recalls happen lower (p10 8%) because Mite starts them with foes at 7-8 tiles and retries after hits (see 2).
- **Shop trigger**: shop-only recalls have gold >= 50 (Mite) / >= 70 (Uni), with peaks at 90 and 180 gold (3 or 6 shards): Mite shop-only gold hist 30:8, 60:25, 90:65, 120:17, 150:29, 180:93, 210:29, 240+:55; Uni 90:44, 180:50, 210+:29. Shop recalls are concentrated on elkring (104/35), monolith (65/27), collision (50/25), packs (30/22) — maps where the farm loop passes far from spawn.
- **Bank recalls only exist where the spawn-side altar is close** (rows: altar 10 tiles from spawn, lanes 7-8, packs 3, expanse 7): Mite bank on rows 18, lanes 17; Uni rows 30, collision 8, monolith 14. Everywhere else gems are tributed on the farm route (see 5). Bank recalls carry a bigger bag (Mite med 58, Uni 44).
- **Reposition** (full hp, no gems, nothing to buy) is a real behaviour on rows and packs for both teams (Mite rows 46, packs 46; Uni rows 49, monolith 40, elkring 30, packs 26): the champion is 15 tiles from spawn, teleports home and walks to the next camp (next action: attack camp after a median 14/17 rounds). This is the "recall as teleport" already in the top1-cycle README; the new numbers: 14% / 17% of all arrivals.

Per map (arrivals per game, median hp% at start, median foe distance, spawn stay):

| map | Mite arr/game | Mite hp% | Mite dfoe | Mite stay | Uni arr/game | Uni hp% | Uni dfoe | Uni stay |
|---|---|---|---|---|---|---|---|---|
| collision | 25.5 | 42 | 8 | 4 | 20.7 | 36 | 12 | 4 |
| corners | 36.7 | 27 | 7 | 1 | 24.8 | 28 | 9 | 1 |
| elkring | 33.0 | 63 | 12.5 | 3 | 25.2 | 44 | 12 | 4 |
| expanse | 10.8 | 57 | 43 | 3 | 9.0 | 35.5 | 46 | 4 |
| interlock | 22.7 | 34 | 7 | 4 | 19.3 | 28.5 | 10 | 4 |
| lanes | 18.3 | 38 | 11 | 2 | 12.2 | 21 | 11 | 4 |
| monolith | 24.3 | 44.5 | 13 | 1 | 23.5 | 57 | 18 | 1 |
| packs | 23.2 | 61 | 12 | 2 | 14.8 | 70 | 12 | 4 |
| rows | 18.5 | 82 | 33 | 4 | 19.0 | 73 | 33 | 5 |

Per champion type (Mite): Issac 301 arrivals (heal 185), Ren 247, Cassi 213 (reposition 64 — Cassi recalls at full hp to re-join Issac), Varg 197, Ryth 173, Stellar 136, Tavi 11. Univardisty: Ren 204, Stellar 150, Varg 134 (reposition 49, bank 26: Varg is the courier), Issac 128, Ryth 91, Tavi 83 (heal 71, med 23%), Cassi 78.

Examples: heal — Mite Issac e9c3f66b collision r168 at (17,26) hp 11%, foe at 8, back at camp 9 rounds after arrival. shop — Uni Stellar e9c3f66b r76 hp 57%, 190 gold, stay 1, camp 15 rounds later. bank — Uni Ren e9c3f66b r160, 22 gems, 9 tiles from spawn, tribute 20 rounds later. reposition — Mite Cassi 30b9ea2d collision r197, 100% hp, 0 gems, 0 gold, 3 tiles from spawn (!), attacks a camp 7 rounds after arriving. escape — Uni Ren 1c547a16 collision r811 hp 34%, foe at 4, arrived.

## 2. Recall safety

Distance to the nearest foe at the start (all starts incl. interrupted) and interruption rate (hit/died) by that distance:

| dfoe | Mite starts | Mite interrupted | Uni starts | Uni interrupted |
|---|---|---|---|---|
| 1-3 | 24 | 20 (83%) | 31 | 20 (65%) |
| 4 | 14 | 7 | 36 | 19 (53%) |
| 5 | 27 | 5 | 74 | 23 (31%) |
| 6 | 84 | 10 (12%) | 38 | 3 |
| 7 | 333 | 35 (10%) | 45 | 5 |
| 8 | 161 | 16 (10%) | 74 | 3 |
| 9+ | 773 | 37 (5%) | 863 | 3 (0.3%) |

- **Mite starts recalls with the nearest enemy at 7-8 tiles in 35% of cases** (right at the edge of vision 8; the champion is usually hit by Stellar/Tavi spells from range: 41 of the 61 foe interruptions are Stellar (20) or Tavi (21)). Univardisty recalls with nobody in vision 74% of the time (dfoe >= 9) and only goes under 6 when it is an escape attempt (31+36+74 starts with dfoe <= 5, 62 interrupted).
- Interruptions: Mite 138/1416 starts (9.7%): hit by foe 61, **hit by a camp 44**, died 25, game end 8. Univardisty 150/1161 (12.9%): **voluntary cancel by moving 68**, hit by foe 42, died 21, cancelled to attack 11, game end 6, restart 2.
- Mite's camp interruptions are a bug: it starts recalling while a camp monster (range 3, never chases) is still hitting it and retries every turn: Issac d1a5da76 collision r478-505 made **27 consecutive recall attempts**, each cancelled by the wolf (hp 45% -> 1 tile from death); Ren 4ffb04fa packs r90 8 attempts; 61 champion-rounds wasted in streaks of >= 3. Against foes it does the same: Ryth e9c3f66b collision r126-132 7 attempts at dfoe 3 then died; Issac 314ba251 interlock r76 7 attempts then died; Stellar d85cb577 monolith r384 6 then died.
- What they do after an interruption: Mite retry 82 (59%, 53 of them the very next round), die 32 (23%), fight 14, walk 2. Univardisty retry 85 (57%; 33 next round, 26 two rounds later), die 39 (26%), fight 17, walk 3. Univardisty's 68 self-cancels happen 1-2 rounds into the channel (hp med 26%, foe at 8 at the start, i.e. a foe stepped into vision): 56 of them walk one or two tiles and restart, 9 turn to fight (e.g. Stellar e9c3f66b r218 cancelled r223 -> retry; Ren 1c547a16 r62 cancel r65, retry r66, cancel r67). Mite never cancels voluntarily (0 moved-cancels).

## 3. Time at spawn and what comes next

- Spawn stay after arrival (rounds on a spawn tile, arrival round included): Mite 0:21, 1:372, 2:278, 3:117, **4:397**, 5:79, 6+:14. Univardisty 0:10, 1:242, 2:149, 3:96, **4:386**, 5:107, 6+:21. Both are bimodal (1 vs 4). The 4-round stays are not shopping (121 Mite / 155 Uni stays of 4 with no purchase), not waiting for allies (an ally is on spawn when they leave in only 14% / 11% of them) and not idle (median 0 idle turns; the champion keeps issuing no-effect actions `k 14`/`k 23`). Inferred: a fixed "wait until the next target is worth walking to" timer. 
- Heal: every arrival that was not at full hp gets the end-of-turn full heal on the arrival round (Mite 1162/1278 regen events, Uni 972/1011; the rest arrived already full). Nobody leaves below 100% (Mite 0 cases, Uni 8).
- Shopping on arrival: Mite buys in 65% of stays (0 items 442, 1: 299, 2: 382, 3: 131, 4-5: 24; median 160 gold spent); Univardisty 66% (1: 299, 2: 293, 3: 75; median 180).
- Next action after leaving: Mite attack camp 58% / tribute 17% / fight a foe 16% / recall again 3% / died within 60 rounds 1%, median 14 rounds after arrival. Univardisty camp 46% / tribute 27% / fight 20% / capture 3%, median 17 rounds.
- Cost per game (median): Mite 25 starts, 22.5 arrivals, **169 champion-rounds in recall channels + spawn = 9.4% of all champion-rounds** (1.19 arrivals per champion per 100 rounds); Univardisty 20 starts, 17.5 arrivals, 145 champion-rounds = 6.9% (0.82 per champion per 100 rounds). Corners is the recall-heaviest map (36.7 / 24.8 arrivals per game, stay 1: both teams treat corners as a fight map and use spawn as a heal station).

## 4. Healing without recall

There is none. Every positive-hp regen event (`ph 13 k 3`) in the 101 games is on a spawn tile (Mite 1198/1198, Uni 1115/1115) and heals to full at the end of that turn. The only other positive hp effects are health shard purchases (+hp = +maxhp, Mite 262, Uni 293, on spawn) and respawns. No consumable heal was used by either team. Idle champion-turns in the field at < 60% hp (Mite 6038 = 29% of low-hp field turns, Uni 5465 = 22%) are channel waits (tribute, recall, capture timers), not regen idling. Rule: **below 50% the only heal is the recall; above 50% they keep farming/fighting at that hp**.

## 5. Tribute decisions

| | Mite | Univardisty |
|---|---|---|
| tributes | 1214 | 884 |
| bag at tribute (med / p90 / max) | 36 / 70 / 228 | 44 / 96 / 218 |
| bag histogram | 20s: 511, 30s: 225, 40s: 291, 60-79: 86, 90+: 74 | 20s: 167, 30s: 118, 40s: 338, 60-79: 96, 90+: 121 |
| channel ticks (med) | 4 (3: 511, 4: 225, 5: 291, 6-10: 134, 11+: 48) | 5 (3: 167, 4: 118, 5: 338, 6-10: 185, 11+: 73) |
| hp% at tribute start (med) | 92 | 100 |
| nearest foe at completion (med); foe <= 3 | 12; 27 | 15; 4 |
| passes within 1 of an altar with gems | 1289, tributed 1231 (95%) | 1974, tributed 989; excluding the locked-altar game 1c547a16 (collision, 953 untributed passes) 989/1021 = 97% |
| delay from entering altar zone to tribute start | 0 rounds 1105, 1: 99, 2+: 27 | 0 rounds 974, 1+: 15 |
| bag carried (sampled every 10 rounds, alive) mean / >= 50 / >= 100 | 12.6 / 6.9% / 1.1% | 20.5 / 12.7% / 4.0% |
| deaths carrying gems / gems lost on death | 82 of 265 / 2834 (52.5 per game, **5.7% of tributed**) | 110 of 328 / 5882 (109 per game, **12.6% of tributed**) |

- Both teams tribute **the moment they stand next to an altar** (no waiting for allies, no waiting at the altar beyond the channel; "rounds in altar zone" median 4-5 = the channel itself). They do not detour to tribute: the bag is tributed when the farm route passes an altar, which is why the typical bag is one or two captures (22/44 on most maps, 36 = one wolf pack on elkring). Big bags happen on rows (Mite med 132, Uni 99: a single far altar, 62 tiles from spawn) and in Univardisty's deep farm loops on collision/monolith/expanse (p90 108-110).
- Mite's 58 untributed passes are on interlock (24), corners (17), monolith (12): a champion crossing an altar during a fight or chase; bag at those passes med 22.
- Univardisty carries more (mean bag 20.5 vs 12.6, >= 100 gems 4% of the time vs 1.1%) and loses more: 5882 gems in deaths vs 2834. Biggest losses: Uni Stellar 476 gems (1c547a16 collision r1860: the altar (27,20) was locked by the opponent at r988 and Univardisty's three champions walked around it for 1000 rounds with 100-476 gems each, never breaking the lock), Varg 198 (6da723a4 rows r481), Tavi 168 (1c547a16 r1911), Stellar 144 (bb593284 elkring r647), Ren 132 (6da723a4 rows r389). Mite: Issac 144 (a3d60396 elkring r323), Issac 94 (61d896ac interlock r289), three 72s on interlock.
- Altar locks (`k 20`): Univardisty places 248, Mite 167 (own tribute protection; placed within 2 tiles of the altar with a bag). Against an opponent lock Mite breaks it (3 no-effect basic attacks on the altar then tribute: e9c3f66b collision r65, 3e165d6b elkring r135/r180); Univardisty was never seen attacking a lock (7 tributes after a lock happened without lock attacks, i.e. the lock had gone; 4 "visited, no action", all in 1c547a16).

## 6. Deaths

| | Mite | Univardisty |
|---|---|---|
| deaths (per game) | 265 (4.9) | 328 (6.1) |
| killing blow | spell 164 (62%), attack 97 (37%), camp 4 | spell 197 (60%), attack 117 (36%), camp 14 |
| damage in last 10 rounds | spells 64%, attacks 32%, camps 4% | spells 69%, attacks 27%, camps 4% |
| top killers | Stellar spell 81, Ren atk 28 + spell 28, Tavi spell 26 + atk 14, Issac atk 17, Ryth atk 17 | Stellar spell 117, Ren atk 38 + spell 33, Issac atk 22, Cassi spell 16, Tavi atk 16 |
| hp% 5 rounds before death (med) | 68 | 53 |
| hp% at r-2 >= 50 ("bursted") | 107 (40%) | 83 (25%) |
| hp at r-2 histogram (0/20/40/60/80/100) | 78/57/41/31/25/33 | 131/77/58/25/9/28 |
| nearest foe within 3 at r-5 | 117 (44%) | 122 (37%) |
| no ally within 8 at r-5 | 45 (17%) | 93 (28%) |
| outnumbered (foes within 8 > allies+1) | 78 (29%) | 140 (43%) |
| distance to spawn at death (med) | 15 | 16 |
| recall attempted in last 10 rounds | 41 (15%), hp at r-5 med 46 | 41 (13%), hp med 38 |
| distance to foe grew over last 5 rounds (fled) | 64 (24%) | 59 (18%) |
| attacked in last 10 rounds | 230 (87%) | 292 (89%) |
| hp < 50% and no foe within 3 at r-5 (clear window to walk/recall) | 43 (16%) | 82 (25%) |
| avoidable (killed by a camp, or hp >= 50% at r-5, or hp >= 35% with no foe within 3 at r-5) | 201 (76%) | 222 (68%) |
| camp deaths (foe within 8 at the time) | 4 (4) | 14 (11; 9 on elkring, 4 lanes) |
| gems lost to camps | 44 | 346 |

- Both teams almost always fight back (87-89% attacked in the last 10 rounds) and almost never recall out (13-15%); the recall attempts that exist are usually too late (hp 38-46% with a foe adjacent, hence the interruption counts in 2). 
- Mite dies "fast": 40% of its deaths go from >= 50% hp to dead in two rounds (Stellar/Ren/Tavi spell bursts in group fights: e.g. Cassi e9c3f66b collision r54 100% -> dead to a Stellar 700-damage hit; Varg r176 69% -> 26% -> dead). Univardisty dies "slow": 40% of its deaths are at < 20% hp two rounds before death and 25% had a clear window at r-5 (hp < 50%, no foe within 3) that it spent fighting (Stellar 37e16f73 collision r535: 81% at r-5, foe at 7, 0 allies within 8, 4 foes, died with 44 gems; Tavi 1c547a16 r653: 64% for 8 rounds, 4 foes vs 2 allies, died with 66 gems).
- Camp deaths are rare and nearly always a foe-plus-camp sandwich (Mite 4/4, Uni 11/14), e.g. Mite Ryth 30b9ea2d collision r64 (hp 67 -> 2 under Stellar+Cassi+Issac, finished by the camp), Uni Tavi 3e165d6b elkring r81. Univardisty on elkring loses 9 champions to camps (contested wolf packs).
- By map, deaths per game (Mite / Uni): corners 16.0 / 16.5, collision 7.5 / 5.5, elkring 7.3 / 9.8, interlock 5.5 / 10.3, packs 4.8 / 4.8, lanes 1.3 / 4.5, monolith 1.7 / 2.2, rows 0 / 1.0, expanse 0 / 0. Univardisty's extra deaths are interlock (+4.8/game, 62 deaths, 44 "avoidable") and elkring (+2.5). 
- By type: Mite Cassi 63 + Issac 63 (they die together), Varg 37, Ren 35, Stellar 35, Ryth 30, Tavi 2. Univardisty Stellar 69, Tavi 64, Ren 40, Cassi 37, Issac 37, Ryth 26, Willow 18, Prism 15, Varg 11.

## 7. Respawn

- Shopping: Mite never buys while dead (0/230 respawns) and buys on spawn right after respawning in 35% of respawns (1: 36, 2: 38, 3: 6); Univardisty buys while dead in 34% (1: 52, 2: 44, 3: 1) and never on spawn after respawn. Gold at respawn median 5 for both (the kill reward goes to the opponent, nothing to spend).
- Stay on spawn after respawn: Mite 1 round 38%, 2-3 17%, 4 44%; Univardisty 1 round 24%, 2-3 14%, 4 50%, 5+ 13%. Median idle turn in the stay is 1.
- Where next: Mite attack camp 60%, fight a foe 31% (corners: 53 of 84 respawns go straight back into the fight), capture 3%, recall 2%; median 13 rounds to the first action. Univardisty camp 65%, fight 25%, none 6%; median 17 rounds.

## 8. Rules per team (M = measured, I = inferred)

Mite
1. (M) Recall when hp < 50% (max 49% over 716 heal recalls, every champion type) unless a foe is within ~6 tiles; a foe at 7-8 does not stop it (35% of starts). Does not fight back below 50%: recall is attempted even with a foe adjacent (24 starts at dfoe <= 3, 83% interrupted) and retried every round until it lands or the champion dies (streaks of 6-27).
2. (M) Also recalls while a camp monster is still hitting it (44 camp interruptions) — retries each round instead of stepping out of range 3.
3. (M) Recall to shop when gold >= 50 (min seen; peaks at 90/180 gold = 3/6 shards), typically at 77% hp, after a capture far from spawn (elkring/monolith/collision/packs). Buys 1-3 items on arrival (65% of arrivals).
4. (M) Recall as a teleport at full hp when the next target is far and spawn is closer (rows/packs, 14% of arrivals; even from 3 tiles away from spawn). Bank recalls only on rows/lanes where an altar is 7-10 tiles from spawn.
5. (M) Stays 1 round (heal only) or 4 rounds on spawn, then goes to a camp (58%) or an altar (17%); median 14 rounds from arrival to the next action.
6. (M) Tributes instantly on every altar pass (95%), bag med 36, carries >= 50 gems only 7% of the time; loses 5.7% of its tributed gems to deaths.
7. (M) Breaks enemy altar locks with 3 basic attacks, then tributes. Places its own locks (167).
8. (M) No voluntary recall cancel; no field healing; no potions.
9. (I) Deaths are group-fight bursts (40% from >= 50% to dead in 2 rounds), 76% "avoidable" by the hp/foe-distance criteria; the bot has no "leave the fight at X% hp" rule, only the recall at < 50% that fails under fire.

Univardisty
1. (M) Recall when hp < 50% (max 49%), but only when no enemy is in vision (74% of starts at dfoe >= 9); if an enemy appears during the channel it cancels by moving 1-2 tiles and restarts (68 cancels, 56 retried) or turns to fight (11). Escape recalls at dfoe 3-5 exist (51 arrived, ~45% interrupted).
2. (M) Shop recall at gold >= ~90 (peaks 90/180), 13% of arrivals; buys while dead (34% of respawns) rather than after respawn.
3. (M) Bank recall with 44+ gems where an altar sits near spawn (rows 30, monolith 14, collision 8); reposition recalls at 76% hp with no gems on rows/monolith/elkring/packs.
4. (M) Stays 4 rounds on spawn in half of the arrivals, then camp (46%) or altar (27%); 17 rounds to the next action. 6.9% of champion-rounds spent recalling vs Mite's 9.4%.
5. (M) Tributes instantly on every altar pass (97% outside the locked-altar game) with bigger bags (med 44, p90 96) and carries >= 50 gems 13% of the time; loses 12.6% of its tributed gems to deaths (109 per game).
6. (M) Does not break altar locks: in 1c547a16 (collision, 2000 rounds) it never tributed after the opponent locked the altar at r988 and died with 476 + 168 gems.
7. (M) Dies more (6.1 vs 4.9 per game), mostly slowly and outnumbered (43% outnumbered, 28% alone, 40% below 20% hp two rounds before death) — it keeps fighting below 50% once a foe is in vision because the recall rule is gated on "no enemy visible".
8. (M) Camp deaths 14 (9 on elkring), always with foes around: contests wolf packs at low hp.
9. (I) The gap between the two: Mite's recall is "hp-first" (recall at < 50% regardless of foes, accept interruptions), Univardisty's is "safety-first" (recall only when unseen) — Univardisty wastes fewer rounds (145 vs 169 per game) but dies 25% more and loses twice the gems.
