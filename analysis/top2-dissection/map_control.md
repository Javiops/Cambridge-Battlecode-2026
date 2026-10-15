# Map control, game phases and reaction to the opponent: Mite (#1) and Univardisty (#2)

Data: 101 decoded replays of 2026-10-15 (54 games per team, 6 per map, each vs a different top-20 rival; 7 games are Mite vs Univardisty).
Scripts: `$S/reports/scripts_mapcontrol/` (`common.py` loader + `q1_territory.py` ... `q12_examples.py`, `trace.py`; raw outputs `q*.out`).

**Definitions used everywhere below**
- Territory of a tile = BFS walking distance to own spawn vs enemy spawn. `own` if closer to us by more than 3 steps, `enemy` if closer to them by more than 3, `mid` otherwise. Camp groups and altars are classified the same way (middle camps = equidistant groups: corners 8, packs 3, collision 2, interlock 4, expanse 3, lanes 12 wolves, rows 1 (monolith+gems), elkring/monolith none).
- Phases: 0-100, 100-300, 300-end. Fight maps = corners, interlock, elkring, packs, collision; farm maps = rows, expanse, monolith, lanes.
- Step kinds decoded empirically (not in the docs): k11 = recall start (jump 5 turn-ends later), k12 = tribute start (always at an altar with gems), k18 = tribute completion (gems -> 0). k14 and k23 are effect-less actions; k20/k26 are rare (see Q6). No ward entity is exported by the replay decoder, so wards are inferred only.
- Steal = a group captured by a team that did not land the last hit on its last monster (and usually did < 20% of the damage).

## 1. Territory over time

Share of alive champion-rounds in own / mid / enemy territory, captures by territory (6 games per cell):

| team | map | 0-100 | 100-300 | 300-end | captures own/mid/enemy |
|---|---|---|---|---|---|
| mite | collision | 70/25/3 | 67/29/3 | 57/31/10 | 139 / 55 / 6 |
| mite | corners | 77/13/8 | 71/18/9 | 69/18/11 | 36 / 66 / 4 |
| mite | elkring | 89/9/0 | 78/19/2 | 73/22/4 | 149 / 3 / 4 |
| mite | interlock | 80/16/2 | 76/18/4 | 69/25/4 | 147 / 25 / 1 |
| mite | packs | 74/21/3 | 66/29/3 | 68/28/3 | 74 / 47 / 1 |
| mite | monolith | 93/6/0 | 79/15/4 | 77/16/5 | 181 / 4 / 2 |
| mite | lanes | 100/0/0 | 96/2/0 | 97/2/0 | 225 / 15 / 0 |
| mite | expanse, rows | 100/0/0 | 100/0/0 | 100/0/0 | 168+93 / 0 / 0 |
| **mite ALL** | | **88/9/2** | **83/13/3** | **73/19/6** | |
| uni | collision | 71/22/6 | 65/26/8 | 50/45/4 | 135 / 49 / 9 |
| uni | corners | 91/8/0 | 68/21/9 | 76/15/7 | 26 / 61 / 1 |
| uni | elkring | 82/13/4 | 68/18/12 | 69/20/10 | 119 / 10 / 14 |
| uni | interlock | 76/10/12 | 77/12/10 | 72/12/14 | 117 / 1 / 6 |
| uni | packs | 78/18/2 | 71/19/9 | 76/14/9 | 82 / 34 / 2 |
| uni | monolith | 97/0/1 | 81/11/7 | 69/16/14 | 172 / 4 / 2 |
| uni | lanes | 75/11/13 | 72/8/18 | 78/6/14 | 212 / 5 / 34 |
| uni | expanse, rows | 100/0/0 | 100/0/0 | 100/0/0 | 141+93 / 0 / 0 |
| **uni ALL** | | **86/8/4** | **79/11/8** | **71/19/9** | |

- Both teams start at home and drift towards the middle over the game (own-half share 88% -> 73% for Mite, 86% -> 71% for Univardisty). The enemy half is marginal for Mite (2-6%) and small but real for Univardisty (4-9%, up to 14-18% on lanes, interlock, monolith late).
- **Why they enter the enemy half** (one episode = one champion crossing into enemy territory; Mite 359 episodes = 6.6/game, Univardisty 658 = 12.2/game, median length 9-10 rounds):

| team | enemy seen (<=8) in the 5 rounds before entry | hits a camp there | hits an enemy there | ends dead | all enemies dead at entry | <=1 enemy alive | median score diff |
|---|---|---|---|---|---|---|---|
| mite | 94% | 23% | 59% | 7% | 0% | 5% | +72 |
| uni | 88% | 25% | 59% | 10% | 0% | 3% | +24 |

  Nearly every crossing is a chase (an enemy was visible just before), not a plan: they follow a fleeing or fighting enemy over the line and come back. Only 23-25% of the episodes touch an enemy camp. "Enemy dead" is never the trigger (0% of entries with all enemies dead).
- **Captures on the enemy side**: Mite 18 in 54 games (0.3/game, 6 of them in one collision game vs Quantom at +366..+668), Univardisty 70 (1.3/game), of which 34 on lanes alone (23 gem clusters, 10 wolves). Conditions: in 83-100% of Mite's enemy-side captures an enemy champion was within 8 tiles (they are captures taken while fighting over the camp, not sneaks); the score is usually ahead (median +150) and enemies alive 2.5-4. Univardisty's lanes raids happen with the enemy 50% of the time within 8, at any score (-114 to +456), mostly in phase 100-300 (22 of 34), e.g. match `0c9cfa11` (vs Full Damage) r269-351: Issac/Ren/Stellar take 7 enemy gem clusters in a row while behind -114 and turn the game (win 1004-944); match `d9fd5de8` (vs geese geese go): 16 enemy-side captures r80-344. Against Mite on lanes (`c8d4cf63`) Univardisty took 6 enemy clusters r88-294 but still lost 970-1006.
- Longest stays: Mite max 60 rounds (corners `265a46b9` r29-89, Cassi chasing with camp+enemy hits); Univardisty 112 rounds (lanes `3d6515e6` Issac r242-354 farming the enemy clusters).

## 2. Contested middle camps and steals

Captures of equidistant groups in the 6 games per map (team / opponent), steals (capturer != last hit), "contested" = both teams damaged the group in that clearing, "fight near" = captures with champion-vs-champion damage within 8 tiles of the group during the clearing:

| team | map | mid captures team / opp | steals by team / by opp | contested | fight near camp | median capture round team / opp |
|---|---|---|---|---|---|---|
| mite | corners | 82 / 81 | 12 / 7 | 46 | 132 | 317 / 353 |
| mite | collision | 54 / 30 | 1 / 1 | 20 | 65 | 357 / 404 |
| mite | packs | 63 / 23 | 4 / 1 | 35 | 62 | 272 / 280 |
| mite | interlock | 25 / 3 | 0 / 0 | 2 | 13 | 334 / 234 |
| mite | lanes | 8 / 30 | 1 / 2 | 4 | 21 | 250 / 243 |
| uni | corners | 45 / 129 | 10 / 8 | 59 | 147 | 329 / 393 |
| uni | collision | 40 / 38 | 4 / 6 | 23 | 61 | 443 / 437 |
| uni | packs | 28 / 44 | 6 / 2 | 31 | 50 | 277 / 294 |
| uni | interlock | 1 / 5 | 0 / 0 | 1 | 2 | 387 / 281 |
| uni | lanes | 17 / 13 | 4 / 0 | 12 | 27 | 155 / 294 |

- Mite wins the middle on collision (54-30), packs (63-23) and interlock (25-3); Univardisty loses it on corners (45-129) and packs (28-44). On corners the 4 central gem-cluster pairs next to the centre altar (34,34) are the whole game: every capture there has a fight attached (132-147 fight-hits per 6 games) and 46-59 of the ~170 clearings are damaged by both teams.
- The middle wolves on lanes are mostly left to the opponent by Mite (8 vs 30) and the middle gold clusters of interlock are taken by nobody (no gems).
- **Steals (all territories, 124 in the 101 games)**: Mite stole 32 (22 with < 20% of the damage) and was stolen 20; Univardisty stole 36 (24 with < 20%) and was stolen 35. By map: corners 37, collision 26, lanes 21, packs 16, elkring 11, interlock 10, monolith 2, rows/expanse 0.
- **Mechanism (traced)**: it is not "wait hidden for the last hit". The steal happens when a fight starts over a cleared group: the clearing team is pushed off or killed, and whoever is left standing on the spawn tile 5 rounds later takes it.
  - corners `265a46b9` r24-31: Univardisty's Prism/Tavi kill the cluster at (39,30) at r24; Mite's Varg/Stellar/Cassi/Ryth arrive, trade spells r27-30, Univardisty backs off, Ryth stands on the tile and captures 48 gems at r31 with 0% of the camp damage.
  - corners `d6b437f2` r28-40: Shawn clears both clusters, Mite kills Ren/Tavi, Shawn's survivors leave, Varg+Stellar capture both (r40) 12 rounds later.
  - corners `8f7d1b55` r84-95 (against Mite): Mite's Stellar at 10 hp is chased off the cleared cluster, hello's Ryth walks on and captures at r95.
  - corners `a1a3769a` r318-329: Univardisty's Willow sits on a cluster hello cleared, tributes 48 at the centre altar at r321 and captures the next cluster at r329 while the hello champions fight 8 tiles away.

## 3. Altar use

Tributes (k18) by altar territory and phase, bag size:

| team | map | n | 0-100 own/mid/enemy | 100-300 | 300-end | median bag | p90 | max | bags <= 10 |
|---|---|---|---|---|---|---|---|---|---|
| mite | collision | 172 | 0/18/0 | 0/60/0 | 0/94/0 | 22 | 36 | 212 | 0% |
| mite | corners | 98 | 0/12/0 | 2/32/0 | 1/51/0 | 48 | 48 | 228 | 0% |
| mite | elkring | 151 | 0/21/0 | 0/54/0 | 0/76/0 | 36 | 36 | 144 | 0% |
| mite | interlock | 159 | 25/0/0 | 47/6/2 | 63/15/1 | 22 | 72 | 116 | 0% |
| mite | packs | 124 | 17/0/0 | 46/0/0 | 61/0/0 | 44 | 48 | 48 | 0% |
| mite | monolith | 183 | 0/31/0 | 0/95/0 | 0/57/0 | 22 | 44 | 66 | 0% |
| mite | lanes | 177 | 24/0/0 | 99/0/0 | 54/0/0 | 24 | 60 | 144 | 0% |
| mite | expanse | 94 | 14/0/0 | 42/0/0 | 38/0/0 | 48 | 96 | 132 | 0% |
| mite | rows | 56 | 1/0/0 | 23/0/0 | 32/0/0 | 132 | 165 | 165 | 0% |
| **mite ALL** | | 1214 | | | | 36 | 70 | 228 | 0% |
| uni | collision | 118 | 0/14/0 | 0/26/0 | 0/78/0 | 44 | 108 | 218 | 0% |
| uni | corners | 68 | 0/1/0 | 0/31/0 | 2/34/0 | 48 | 48 | 96 | 0% |
| uni | elkring | 112 | 0/10/0 | 0/37/0 | 0/65/0 | 36 | 72 | 144 | 0% |
| uni | interlock | 88 | 8/0/1 | 27/0/4 | 39/1/8 | 62 | 94 | 188 | 0% |
| uni | packs | 108 | 14/0/2 | 30/0/4 | 44/0/14 | 44 | 48 | 92 | 0% |
| uni | monolith | 97 | 0/2/0 | 0/40/0 | 0/55/0 | 44 | 110 | 176 | 0% |
| uni | lanes | 140 | 9/0/3 | 56/0/11 | 59/0/2 | 46 | 48 | 144 | 0% |
| uni | expanse | 95 | 22/0/0 | 52/0/0 | 21/0/0 | 48 | 108 | 108 | 0% |
| uni | rows | 58 | 2/0/0 | 31/0/0 | 25/0/0 | 99 | 132 | 132 | 0% |
| **uni ALL** | | 884 | | | | 44 | 96 | 218 | 0% |

- Which altar is simply the nearest one to the farmed camps: on collision, corners, elkring and monolith the only/closest altars are middle ones, so 100% of tributes are "mid"; on packs/lanes/expanse/rows they are the own-side altars. Mite tributes at an enemy-side altar 3 times in 54 games (all interlock), Univardisty 49 times (interlock 13, packs 20, lanes 16) - again the by-product of raiding the enemy side.
- Bag sizes: Mite tributes small bags often (median 36, 1214 tributes = 22/game), Univardisty bigger and fewer (median 44, 884 = 16/game); both on rows carry 100-165 gems per trip. No team ever tributes 10 gems or less, so there is no "panic banking" of tiny bags. Mite's p90 of 70 vs Univardisty's 96 means Univardisty walks around with more stealable gems (mean carried on fight maps 21 vs 8 gems per champion-round, see Q5), and it loses 15 gems per death vs Mite's 11.
- **Altar locks**: none observed. All purchases are shards/emblems (multiples of 30) plus a 10-gold item (Mite 308, Univardisty 420 buys; a consumable, not a lock: no tribute is ever converted into altar attacks and no tribute is cancelled by an enemy). Tributes started without completion within 15 rounds: Mite 44 of 1265 (3%), Univardisty 124 of 1030 (12%) - stuns/deaths while channelling, mostly on corners.
- Tribute timing with the 5-round capture: the champion starts the tribute on the capture tile when an altar is adjacent (corners centre, interlock (19,16)); otherwise it walks. Univardisty cancels and restarts (k20, 248 times) to fold freshly captured gems into one channel.

## 4. Reaction to the opponent

### 4a. A new enemy within 8 tiles (no enemy within 8 in the previous 5 rounds): what the champion does in the next 5 rounds

| team / maps | n | approach | hold | retreat | hits enemy | hits camp | recalls | allies converge (mean ally distance drops >= 2) | moves >= 3 toward own spawn |
|---|---|---|---|---|---|---|---|---|---|
| mite fight | 1381 | 53% | 27% | 15% | 24% | 25% | 4% | 18% | 7% |
| uni fight | 1183 | 48% | 32% | 14% | 26% | 25% | 1% | 23% | 6% |
| mite farm | 313 | 42% | 27% | 25% | 19% | 24% | 7% | 20% | 17% |
| uni farm | 307 | 45% | 24% | 25% | 25% | 19% | 1% | 16% | 11% |

By situation (fight maps):

| situation | Mite n | approach / retreat / recall / camp | Uni n | approach / retreat / recall / camp |
|---|---|---|---|---|
| own hp < 50% | 88 | 29% / 36% / **40%** / 20% | 95 | 35% / 32% / **7%** / 28% |
| own hp >= 50% | 1293 | 55% / 14% / 2% / 25% | 1088 | 49% / 13% / 1% / 25% |
| carrying >= 50 gems | 37 | 59% / 2% / 2% / 0% | 134 | 32% / 18% / 0% / 2% |
| no gems | 902 | 51% / 18% / 3% / 35% | 734 | 50% / 14% / 1% / 34% |
| was hitting a camp | 271 | 45% / 20% / 9% / **57%** | 252 | 46% / 17% / 4% / **58%** |
| equal numbers within 8 | 140 | 47% / 24% / 12% / 25% (allies converge 35%) | 187 | 45% / 20% / 2% / 24% (converge 37%) |
| outnumbered | 15 | 46% / 20% / 0% | 32 | 43% / 9% / 0% |
| enemy hp < 50% | 158 | 38% / 30% / 1% | 137 | 28% / 25% / 0% |
| in enemy half | 23 | 52% / 30% / 4% (30% go home) | 63 | 50% / 17% / 1% (46% keep hitting the camp) |

Reading:
- Default reaction on sight is to **close in** (about half the time) and **keep doing the current job**: a champion that was hitting a camp keeps hitting it in 57-58% of cases. Nobody retreats just because an enemy appeared.
- **Low hp is the one real trigger**: at < 50% hp Mite starts a recall within 5 rounds in 40% of contacts (and in 39% moves >= 3 tiles toward home), Univardisty only 7% recalls and walks away instead (32% retreat, 35% move home). Univardisty's casters prefer to fight from range 4 and keep farming.
- **Gems do not make them cautious**: with >= 50 gems Mite approaches 59% and retreats 2%; Univardisty holds position (44%) more than it retreats (18%).
- Numbers: "outnumbered" contacts are rare (15-32) because they move as a pack; when numbers are equal both teams converge allies in ~35% of cases (vs 16-21% otherwise).
- Example (Mite recall on contact): collision `d1a5da76` r208 Cassi at 34% hp with 36 gems meets Quantom's champion, recalls that turn. Example (Univardisty walking away): collision `1c547a16` r482 Tavi at 50% with 44 gems retreats 5 tiles toward home, no recall.

### 4b. An enemy group (>= 2) enters our half: response in the next 10 rounds

| team / maps | episodes | ours within 10 tiles of the group at entry -> +10 | far champions (> 10) moving >= 4 toward | moving away | still hitting camps | recalling |
|---|---|---|---|---|---|---|
| mite fight | 89 | 2.6 -> 2.1 | 0.75 per episode | 0.01 | 0.8 of 4.0 | 0.65 |
| uni fight | 94 | 2.5 -> 2.0 | 0.48 | 0.05 | 0.6 of 3.5 | 0.44 |
| mite farm | 16 | 2.2 -> 1.5 | 1.75 | 0.50 | 2.4 of 5.8 | 0.56 |
| uni farm | 10 | 1.5 -> 1.3 | 1.30 | 0.50 | 2.0 of 5.4 | 0.50 |

Neither team has a "defend the half" routine: the number of their champions near the invaders does **not** rise in 10 rounds (2.6 -> 2.1), about 0.5-0.75 far champions walk over (and those are the ones heading to the same camps anyway), and 1 champion per episode starts a recall. Examples of real convergence are the exception: collision `d1a5da76` r218 (Mite, 2 far champions arrive, 4 within 10 after 10 rounds); corners `373814ef` r50 (Univardisty, 3 -> 5). Examples of ignoring: elkring `2f0076ab` r269, two enemies in Mite's half, 0 Mite champions within 10 before and after, 2 keep hitting camps; corners `9d113be1` r334 Univardisty keeps farming at -746.

### 4c. After an ally dies within 12 tiles: next 8 rounds of each nearby ally

| team / maps | n | retreats >= 3 toward spawn | recalls | keeps hitting enemies | hits a camp | also dies |
|---|---|---|---|---|---|---|
| mite fight | 485 | 27% | 15% | 41% | 20% | 8% |
| - with >= 2 enemies near | 239 | 38% | 20% | 61% | 12% | 13% |
| - own hp < 50% | 131 | 70% | 41% | 24% | 6% | 8% |
| uni fight | 508 | 26% | 8% | 44% | 18% | 6% |
| - with >= 2 enemies near | 278 | 32% | 7% | 62% | 7% | 11% |
| - own hp < 50% | 100 | 61% | 31% | 28% | 8% | 10% |

A death does not make the rest run: 61-62% of the allies still in a fight keep attacking; the ones that leave are the low-hp ones (70%/61% retreat, 41%/31% recall). Mite again prefers the recall, Univardisty the walk. Only 8-13% die in the following 8 rounds, so the "one by one" pattern is rare for both.

## 5. Score state

Per champion-round, by tributed-gem difference (ahead >= +50, behind <= -50) and by "late" = last 100 rounds of the game (107 of 108 games end at 1000 gems; one Univardisty-hello collision game went to round 2000, 922-462):

| team | maps | state | champ-rounds | % in mid+enemy | dmg to champions /100cr | kills /100cr | deaths /100cr | captures /100cr | tributes /100cr | mean bag | mean gems carried |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mite | fight | behind | 18281 | 23% | 882 | 0.38 | 0.62 | 0.84 | 0.65 | 34 | 10 |
| mite | fight | even | 19214 | 24% | 525 | 0.23 | 0.23 | 1.07 | 0.72 | 34 | 7 |
| mite | fight | ahead | 32500 | 33% | 675 | 0.30 | 0.26 | 1.22 | 1.38 | 39 | 10 |
| mite | fight | late | 12368 | 31% | 841 | 0.39 | 0.36 | 1.22 | 1.30 | 40 | 13 |
| uni | fight | behind | 21309 | 21% | 957 | 0.35 | 0.48 | 0.70 | 0.43 | 44 | 14 |
| uni | fight | even | 18137 | 22% | 700 | 0.29 | 0.36 | 1.02 | 0.58 | 45 | 12 |
| uni | fight | ahead | 30056 | 39% | 1318 | 0.48 | 0.33 | 1.11 | 0.99 | 51 | 30 |
| uni | fight | late | 9981 | 25% | 1159 | 0.38 | 0.53 | 1.05 | 1.00 | 46 | 15 |
| mite | farm | behind | 12776 | 1% | 101 | 0.05 | 0.00 | 1.40 | 0.51 | 68 | 35 |
| mite | farm | ahead | 17540 | 12% | 218 | 0.06 | 0.05 | 1.47 | 1.61 | 39 | 9 |
| uni | farm | behind | 18048 | 9% | 218 | 0.13 | 0.09 | 1.18 | 0.57 | 64 | 30 |
| uni | farm | ahead | 13030 | 22% | 360 | 0.13 | 0.15 | 1.51 | 1.30 | 56 | 16 |

- **No "play safe when ahead"**: both teams are *more* forward and deal *more* damage when ahead (Mite 24% -> 33% mid+enemy, Univardisty 22% -> 39% and 1318 dmg/100cr). Being ahead is the consequence of winning fights, and winners keep hunting. Nobody stops fighting when ahead.
- **Behind** = losing fights: deaths double (Mite 0.62/100cr, worst state), captures fall 20-30%, the tribute rate halves and bags get bigger (34 -> they hold on; farm maps 68 and 64 mean bag when behind vs 39/56 ahead) - they bank less often, not more, when behind, which is what the nearest-camp loop produces when champions are dead or far from an altar.
- **Last 100 rounds**: the tribute rate rises (Mite fight 0.94 -> 1.30/100cr, farm 0.89 -> 1.52; Univardisty 0.66 -> 1.00, 0.59 -> 1.40) with normal bags (median 36-48, 0% bags <= 10 in the last 25 rounds). So the end-game is a banking race, not a fight, but it is "bank what you have" rather than a special rush.
- Tribute bag in the last 25 rounds: Mite farm 40, fight 45; Univardisty 49 / 43 (vs 33-49 earlier). Univardisty's deaths/100cr go up late on fight maps (0.36 -> 0.53): it keeps carrying 15-30 gems into end-game fights.

## 6. Wards, bushes, scouting

- Warding cannot be confirmed from the decoded replays (no ward objects exported; the free trinket is not a purchase). Two effect-less action kinds exist: k14 (Mite 32/game, Univardisty 27/game, also 46-363/game for other bots - Quantom's 363/game looks like a ward spam every round) and k23 (Mite 46/game, Univardisty 7/game). Where they happen for Mite/Univardisty: 1-2% in bushes, 68-81% in own territory, 28-39% with an enemy within 8, and k23 for Mite 65% within 3 tiles of a camp. k14 recurs on consecutive rounds (704 of 3252 intervals = 1 round) and k23 twice in the same round 57 times, so at most one of them is the ward trinket (charge recharges one round after use). Treat warding as **unobserved**; if either team wards, it is at the camp it is clearing, not at chokepoints.
- Bush standing: Mite 11% of champion-rounds on farm maps (the bush rows of lanes/expanse are on the farm routes), 4.5% on fight maps; Univardisty 3%. Neither parks a champion in a bush as a lookout: rounds spent alone in mid/enemy territory without touching a camp are 2-3% (Mite) and 3-5% (Univardisty) of champion-rounds, and these are chases, not scouting trips (see Q1).
- Vision is handled by **moving as a pack**: at first contact on fight maps "outnumbered" happens in only 1-3% of contacts, and at death the victim has 1.4-1.9 allies within 8 (Q11). They see with the group, not with wards.

## 7. Per-opponent adaptation (same team, same map, different opponents)

Games of the same team on the same side with the same draft are compared round by round (positions mirrored to side A). First round where the team's own positions differ:

| team | map | pairs | first-diff rounds | pairs with an enemy within 8 of one of ours in the 3 rounds before |
|---|---|---|---|---|
| mite | corners | 7 | 18 18 18 18 19 19 20 | 7/7 |
| mite | packs | 10 | 26 26 26 26 27 27 27 27 27 33 | 10/10 |
| mite | collision | 10 | 30 30 30 30 36 36 36 38 38 45 | 10/10 |
| mite | interlock | 15 | 6 x8, 31 x4, 37 37 41 | 3/15 |
| mite | elkring | 7 | 4 4 4 4 44 47 65 | 3/7 |
| mite | lanes | 10 | 43 x4, 54 x3, 58 58 80 | 6/10 |
| mite | monolith | 10 | 92 92 92 92 93 93 93 100 100 120 | 10/10 |
| mite | expanse | 10 | 16 x4, 80 x4, 172 289 | 0/10 |
| mite | rows | 10 | 103 x4, 125 x3, 290 290 369 | 4/10 |
| uni | interlock | 10 | 21 x4, 22 x5, 24 | 10/10 |
| uni | collision | 4 | 38 38 40 41 | 4/4 |
| uni | expanse | 6 | 59 59 59 303 303 309 | 3/6 |
| uni | lanes / corners / monolith / packs | 3/1/1/1 | 47 47 58 / 17 / 79 / 37 | all |

- On fight maps the games are **identical until first contact** (corners r18, packs r26-27, collision r30-38, monolith r92-100): the opening is a fixed script and the opponent changes nothing until a champion is seen. The divergence is then driven by where the enemy is (e.g. collision: vs hello the enemy was 1 tile away at r30, vs Univardisty 12).
- Tiny divergences with no contact exist (expanse r16 Issac (5,12) vs (5,11); interlock r6 Cassi (1,6) vs (2,6); elkring r4): one-tile path tie-breaks that are not explained by anything visible, most likely time-budget dependent code (the earlier README noted that a change in first-turn computation flips games). Beyond those, on rows Mite's games vs Univardisty and Intercontinental are identical for 369 rounds.
- **Drafts**: Mite drafts the same team on a map against every opponent (collision Varg/Ryth/Cassi+Issac; corners Varg/Stellar/Cassi+Issac/Ryth/Ren; ...). Univardisty's draft changes with the opponent in 7 of 9 maps (corners: 5 different line-ups in 6 games), i.e. it counter-drafts, Mite does not.
- **Does Mite play Univardisty differently?** No - the opening is the same script, and Mite's map-control numbers vs Univardisty are inside its range vs others (own-half share 75-100%, captures own/mid/enemy 27/1/1 on elkring, 8/14/0 on corners). What differs is the outcome: on collision (`e9c3f66b`) Mite lost 154-1100 with 19 deaths (68% in its own half, 1.1 allies and 1.8 enemies within 8 at death, 78% of deaths while behind): Mite's Ryth/Issac walk to the middle wolf (24,22) at r44-54 while Univardisty's Tavi/Stellar/Ren wait 5 tiles away in their half, and Stellar's 700-damage spell kills Cassi at r54; Mite then keeps sending champions back to the same camps. Head-to-head Mite won 5 of 7 (corners, elkring, lanes, packs, rows), lost collision and monolith.

## 8. Mite vs Univardisty, and the rule list

| aspect | Mite | Univardisty |
|---|---|---|
| enemy half presence | 2-6% of champion-rounds, 6.6 crossings/game, 0.3 enemy-side captures/game | 4-9%, 12.2 crossings/game, 1.3 enemy-side captures/game (34 on lanes) |
| middle camps | wins them on collision/packs/interlock, splits corners | loses corners 45-129 and packs 28-44 |
| steals | 32 made / 20 suffered | 36 made / 35 suffered |
| tributes | 22/game, median bag 36, p90 70 | 16/game, median 44, p90 96; 12% of tribute channels interrupted |
| contact at < 50% hp | recall 40% | recall 7%, walk away |
| gems carried on fight maps | 8/champion-round | 21 |
| deaths on fight maps | 247 in 30 games, 35% outnumbered | 282, 43% outnumbered, 47% on farm maps in the enemy half |
| draft | fixed per map | changes per opponent |
| ahead | 33% forward, 675 dmg/100cr | 39% forward, 1318 dmg/100cr |

**Rules (M = measured in these games, I = inferred interpretation)**

1. (M) Farm your own half; the share of time in own territory falls from ~88% to ~73% over the game as the nearest-up camps move to the middle. The enemy half is entered only while chasing a visible enemy (94%/88% of crossings) and left after ~10 rounds.
2. (M) Enemy-side camps are taken only when the team is already there fighting (an enemy within 8 in 83-100% of Mite's cases); Univardisty additionally raids enemy gem clusters on lanes from round ~80 regardless of score. (I) Mite has no "steal the enemy jungle" rule; Univardisty has one for maps where the enemy clusters are closer than the next own camp.
3. (M) Middle camps are taken by the group that is there first and fought over on corners/packs/collision; steals are the by-product of winning the fight at a cleared group (capturer did < 20% of the damage in 46 of 68 steals), not of hiding and waiting.
4. (M) Tribute at the altar nearest to the camp just cleared; start the channel on the capture tile when an altar is adjacent; never bank bags <= 10; no altar locks are used.
5. (M) On sight of an enemy: keep the current job (57% keep hitting the camp) and close in (~50%); the only retreat triggers are hp < 50% (Mite: recall 40%; Univardisty: walk 32%) and, weakly, a low-hp enemy (chase 38%/28%). Gems carried do not change the reaction.
6. (M) No territorial defence: an enemy group in our half does not pull champions in (2.6 -> 2.1 nearby after 10 rounds). (I) Defence is implicit: the camps are where our champions are anyway.
7. (M) An ally's death does not trigger a group retreat; 61% of the allies in the fight keep attacking, the low-hp ones (70%) leave.
8. (M) Score does not switch modes: ahead = more forward and more damage, behind = fewer captures and half the tribute rate because champions are dead or far. End-game = higher tribute frequency with normal bags.
9. (M) Vision comes from grouping, not wards or bush lookouts (lone forward champions 2-5% of champion-rounds).
10. (M) The opening is a fixed script until first contact; Mite's rival-specific play is zero (same draft, same path), Univardisty's is the draft only.
11. (I) Mite's edge over Univardisty on fight maps comes from rules 5 and 8: small bags (less to lose), recall at low hp, and no raids into the enemy half; Univardisty's edge on lanes/monolith comes from rule 2 (raiding) and bigger bags.

## Files
- Report: `$S/reports/map_control.md`
- Scripts: `$S/reports/scripts_mapcontrol/common.py` (loader, BFS territory), `q1_territory.py`, `q2q3_camps_altars.py`, `q4_react.py`, `q5_score.py`, `q6_wards.py`, `q7_diverge.py`, `q7b_enemycomp.py`, `q8_h2h.py` (per-game table), `q9_lanes.py`, `q10_trib.py`, `q11_deaths.py`, `q12_examples.py`, `trace.py <match-prefix> r0 r1 [radius] [group]` (round-by-round viewer); outputs `q*.out`.
