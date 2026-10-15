# Reactions and deaths — how our bot (v35, "Live Love Larp") behaves when attacked and how it dies

Data: 150 online games of 2026-10-15 11:33 UTC against the top-30 (59 wins, 91 losses; 145 games as team 0, 5 as team 1; drafts: cassi/ren/stellar 40, ryth/stellar/prism/ren/tavi 31, vendetta/varg/cassi/ryth/tavi 31, vendetta/varg/cassi/ryth 18, vendetta/varg/cassi 17, cassi/ren/stellar/tavi 13). Every-step decoded replays `$S/ws2/steps/<match>.c.jsonl`, maps `$S/ws2/mapsj`. Scripts: `$S/ws2/scripts_reactions/` (`common.py` loader + per-round action classifier, `extract.py` -> `rows.json` (hit episodes, retreats, recall attempts, help pairs, deaths), `report1.py` Q1-Q2, `report2.py` Q3-Q5, `report3.py` Q6, `extra.py`). Opponent tiers: top10 = rank 1-10 (50 games), 11-20 (50), 21-30 (45), other (5 games vs rank 31-249). "Opponents" below = the 150 opposing bots pooled; Mite / Univardisty reference numbers come from `/mnt/project-files/analysis/top2-dissection-2026-10-15/recall_survival.md` and `fights.md` (101 games of 07:00 today).

Definitions used everywhere: **hit round** = a champion-round in which the champion took damage from an enemy champion; **episode** = hit rounds of one champion with gaps <= 5 rounds; **action class** of a champion in a round: fight (attack / damage spell on an enemy champion; a melee that also moved gets fight+away / fight+closer), away / closer / lateral (moved; distance to the nearest enemy of the previous round end grew / shrank / unchanged), camp (hit a camp), recall / tribute (started or continued the channel), nothing (no action with an effect: idle, stunned, failed order, a no-damage ability), dead. Distances are Chebyshev; spawn/altar distances are BFS on the map grid. Pair deaths (Cassi/Issac: when one dies the other dies too) are counted in deaths-per-game and gems lost but excluded from the "how did it die" context (the partner was often 20 tiles away).

## Summary (the numbers behind every claim are in the sections below)

1. **Reaction to a hit (Q1).** In the hit round we fight back 32% of the time (fight 22 + fight+away 6 + fight+closer 4), move away 15%, move closer 13%, do nothing 20%, keep hitting the camp 2%, keep channelling 3%, and are already dead 9%. One round later the picture is 31% fight / 23% away / 4% closer / 19% nothing / 15% dead. The opponents' profile is almost the same (t0: 32% fight, 13% away, 20% closer, 22% nothing, 5% dead) — the big difference is not the action mix but the outcome: **25% of our hit episodes end in death (717/2866) vs 13.7% of theirs (474/3450)**. Per type: casters fight back more (Stellar 34%, Prism 31%) and Issac/Ryth/Vendetta step *closer* on the first hit (30-51%); Tavi does nothing in 43% of first hits. By hp band at t+1: above 70% we fight (34%) or stand (29%); at 40-70% we move away (28%) or fight (35%); below 40% we move away 26% and are dead 48% (opponents 37%). Retreat starts a median 2 rounds after the first hit (62% of episodes contain a retreat step; opponents 58%, also median 2); we retreat alone (no ally within 6) 31% of the time and with the allies staying put 45% — the group retreats together in only 14%.
2. **Retreat quality (Q2).** We start a retreat at median 54% hp with the enemy at 3 tiles; the enemy follows in 76% of retreats (>= 3 follow steps in 39%, chase lasting a median 8 rounds). After 5 rounds the distance to that enemy has grown by a median 3 tiles: we outrun it (+3 or more) in 46% of cases, are caught (no gain) in 9%. We run toward spawn in 53% of retreats and toward an ally in 29%. Outcome within 15 rounds: **death 26%, recall arrived 37%, escape 27%, still fighting 10%**. Opponents: outrun 60%, toward spawn 63%, death 13%, recall 47%. Our retreats below 40% hp die 40% of the time (opponents 17%); casters' retreats die 35% (melee 20%). Worst maps: corners (35% of retreats die), packs 29%, elkring 28%; best: interlock 16%, lanes 19%.
3. **Recalls (Q3).** 25.7 attempts per game, 91% arrive, 5% hit by a foe, 2% die in the channel, 0.2% hit by a camp. hp at start: median 51% (p10 20, p90 88), bimodal at 30-40% and 80-90%; there is **no hp threshold** (full-hp teleports with no gems and no gold happen for every type) and no "escape" pattern: only 15% of starts come within 3 rounds of being hit by a foe. Nearest foe at start: median 14, 71% of attempts with nobody within 9 tiles (99% arrive), 16% with a foe within 5 (49-66% arrive). The channel is interrupted mainly when started with a foe at 4-5 (573 attempts, 33% interrupted) or on corners (72% arrival, 83 foe interruptions + 34 deaths in 17 games). After an interruption we retry in only 32% of cases (30% within 2 rounds), fight in 50%, die in 15%. Mite: 25 starts/game, 9.7% interrupted, retries 59%, strict hp<50% heal rule, starts at 7-8 tiles from a foe in 35% of cases; we recall from farther away (dfoe med 14 vs Mite ~8-13 by map) and are interrupted less (7% vs 9.7%) but do not retry.
4. **Help (Q4).** When one of ours is hit with an ally within 8 (4326 victim-ally pairs), the ally fights within 5 rounds in 29%, moves toward the victim in 20%, keeps farming in 12%, moves away in 15%, does something else in 24%. Median time to help = 1 round. An ally that was hitting a camp when the victim was hit keeps farming in 46% of cases (opponents 40%) and helps in 36%; an ally that was recalling never helps (7%). Opponents: 30% fight / 19% come / 7% keep farming / 15% move away — the same, except that they are less likely to be farming beside a fight. Help rate is lower when the victim dies (32%) than when it survives (54%) for both teams: the victim dies when it is alone or the ally is itself low (ally hp < 40 helps in 19%).
5. **Deaths (Q5).** 858 deaths = 5.72 per game (149 of them pair deaths), 8586 gems lost = 57 per game = 7.1% of what we tribute (opponents: 581 deaths = 3.87 per game, 124 of them pair deaths, 8540 gems lost = 57 per game = 6.3% of their tribute; Mite 4.9 deaths, 52.5 gems, 5.7%; Univardisty 6.1, 109, 12.6%). 73% of our deaths happen in our own half (521/709), median 14 tiles from our spawn; 62 within 2 tiles of an altar. Before the final episode the victim was walking toward the enemy ("approaching") in 270 cases (38%), fleeing 141, idle 82, farming 64, fighting 56, recalling 34, tributing 24. hp at the first hit of the final episode: median 90% (501/709 above 70%) — we are killed from full health, mostly over 4-8 rounds (292) or longer (196), not in one burst (82 one-round deaths). Killer: Stellar 211 (30%), Tavi 80, Ren 75; spells deal a median 68% of the episode damage; 1 enemy did all the damage in 289 deaths, 2 in 255, 3+ in 146. 258 deaths with no ally within 6 (227 while an ally was alive), 276 while outnumbered at the first hit. A recall was in progress in 107 deaths (15%); 351 victims never made a retreat move, 431 fought back at least once. Casters die most: Stellar 164 (1.95 per game drafted), Prism 79 (2.55), Tavi 103 (1.37); Varg 9 and Vendetta 16 almost never die. The opponents die differently: 34% in our half / 38% middle / 29% enemy half, hp at first hit median 72% (107 below 40%), 1-round deaths 100/457 (22%), spells 86% of the damage (our Stellar 36% of all their final-episode damage and 164 killing blows), 43 were recalling and 35 tributing before the fatal episode, 207 (45%) walking toward us.
6. **Worst games (Q6).** The ten worst games lost 232-376 gems each to deaths (3 wins among them). The deciding deaths are of three kinds: a caster tributing or standing at an altar/camp in the open while 1-3 enemies walk into range 4 and kill it from 90-100% hp (feb23cc4 Cassi r81 with 72 gems during an 8-tick tribute; ae2470ab Cassi r805 with 146 gems, hit by Prism at tick 9 of a 15-tick tribute, never cancelled); a melee walking *into* a group (15195780 Issac r301, c2825ed0 Ryth r220/r409, 69757c8e Issac r748 dashing onto an enemy Stellar at full hp and dying in 2 rounds); and the "standing still while poked from range 3-4" pattern (59ac9626 Issac r182-186, cabfadde Issac r251-255: 5 rounds of `nothing` while a Tavi/Stellar at distance 3 takes 60-240 hp per round, then a recall started at distance 3 that is interrupted).

# Detailed tables

## Q1. Reaction to being hit

Unit = champion-round in which the champion took damage from an enemy champion ("hit round"). Action classes: **fight** = basic attack or damage spell on an enemy champion (fight+away / fight+closer = a melee that also moved); **away / closer / lateral** = moved and the Chebyshev distance to the nearest enemy (enemy positions of the previous round end) grew / shrank / stayed; **camp** = attacked a camp monster; **recall / tribute** = started or continued that channel; **nothing** = no action with an effect (idle, failed action, stunned); **dead**.

Counts: hit rounds us 7606 (2866 episodes), opponents 8094 (3450 episodes). Episode = hit rounds of one champion with gaps <= 5 rounds.

### US: action in the hit round (t0) and the next 3 rounds (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t+0 | 7606 | 22% | 6% | 4% | 15% | 13% | 5% | 2% | 0% | 3% | 20% | 9% |
| t+1 | 7606 | 21% | 7% | 3% | 23% | 4% | 5% | 1% | 2% | 2% | 19% | 15% |
| t+2 | 7606 | 17% | 5% | 2% | 27% | 6% | 5% | 1% | 5% | 1% | 11% | 20% |
| t+3 | 7606 | 12% | 4% | 2% | 27% | 7% | 4% | 1% | 9% | 1% | 9% | 24% |

### US: by champion type, action in the hit round / at t+1 (first hit of each episode only)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi t0 | 327 | 21% | 0% | 0% | 12% | 28% | 5% | 3% | 0% | 3% | 22% | 6% |
| Cassi t+1 | 327 | 13% | 0% | 0% | 26% | 3% | 4% | 1% | 0% | 2% | 42% | 8% |
| Issac t0 | 352 | 7% | 5% | 10% | 12% | 30% | 3% | 3% | 0% | 5% | 21% | 4% |
| Issac t+1 | 352 | 10% | 6% | 7% | 22% | 7% | 2% | 1% | 1% | 4% | 32% | 7% |
| Prism t0 | 197 | 31% | 0% | 0% | 7% | 16% | 6% | 1% | 1% | 3% | 32% | 3% |
| Prism t+1 | 197 | 37% | 0% | 0% | 15% | 3% | 5% | 0% | 2% | 2% | 30% | 6% |
| Ren t0 | 674 | 15% | 3% | 6% | 11% | 23% | 3% | 4% | 0% | 4% | 29% | 2% |
| Ren t+1 | 674 | 21% | 6% | 3% | 22% | 8% | 4% | 2% | 2% | 3% | 24% | 4% |
| Ryth t0 | 308 | 9% | 1% | 8% | 13% | 35% | 9% | 2% | 0% | 5% | 17% | 1% |
| Ryth t+1 | 308 | 19% | 3% | 3% | 14% | 4% | 6% | 2% | 1% | 5% | 40% | 3% |
| Stellar t0 | 531 | 34% | 0% | 0% | 13% | 14% | 2% | 1% | 0% | 3% | 30% | 3% |
| Stellar t+1 | 531 | 33% | 0% | 0% | 17% | 5% | 3% | 1% | 2% | 2% | 31% | 7% |
| Tavi t0 | 310 | 17% | 0% | 0% | 17% | 10% | 3% | 2% | 0% | 4% | 43% | 4% |
| Tavi t+1 | 310 | 22% | 0% | 0% | 27% | 7% | 7% | 3% | 5% | 3% | 20% | 8% |
| Varg t0 | 73 | 5% | 4% | 8% | 16% | 36% | 1% | 4% | 1% | 7% | 14% | 3% |
| Varg t+1 | 73 | 10% | 5% | 7% | 18% | 11% | 4% | 1% | 0% | 7% | 34% | 3% |
| Vendetta t0 | 94 | 3% | 3% | 10% | 6% | 51% | 6% | 4% | 0% | 1% | 15% | 0% |
| Vendetta t+1 | 94 | 5% | 9% | 5% | 24% | 4% | 4% | 2% | 0% | 2% | 39% | 4% |

### US: by hp band before the hit (all hit rounds), action at t0 / t+1

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hp >70 t0 | 3426 | 24% | 4% | 5% | 11% | 20% | 4% | 2% | 0% | 4% | 25% | 1% |
| hp >70 t+1 | 3426 | 25% | 5% | 4% | 19% | 7% | 5% | 2% | 1% | 3% | 29% | 3% |
| hp 40-70 t0 | 2430 | 27% | 8% | 5% | 16% | 10% | 6% | 1% | 0% | 2% | 21% | 3% |
| hp 40-70 t+1 | 2430 | 23% | 9% | 3% | 28% | 4% | 5% | 1% | 3% | 1% | 15% | 8% |
| hp <40 t0 | 1750 | 13% | 10% | 1% | 23% | 3% | 5% | 0% | 1% | 1% | 11% | 32% |
| hp <40 t+1 | 1750 | 8% | 7% | 0% | 26% | 1% | 3% | 0% | 2% | 0% | 3% | 48% |

### US: by champion class x hp band, action at t+1 (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| melee hp >70 | 1943 | 21% | 8% | 7% | 17% | 8% | 4% | 2% | 1% | 3% | 28% | 2% |
| melee hp 40-70 | 1454 | 20% | 15% | 5% | 26% | 5% | 4% | 1% | 2% | 2% | 16% | 5% |
| melee hp <40 | 818 | 9% | 15% | 1% | 26% | 1% | 2% | 0% | 2% | 0% | 4% | 40% |
| caster hp >70 | 1483 | 32% | 0% | 0% | 21% | 5% | 5% | 1% | 1% | 2% | 29% | 3% |
| caster hp 40-70 | 976 | 28% | 0% | 0% | 31% | 3% | 7% | 0% | 3% | 1% | 15% | 12% |
| caster hp <40 | 932 | 8% | 0% | 0% | 27% | 1% | 4% | 0% | 2% | 0% | 2% | 55% |

### OPPONENTS: action in the hit round (t0) and the next 3 rounds (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t+0 | 8094 | 19% | 5% | 8% | 13% | 20% | 4% | 1% | 1% | 4% | 22% | 5% |
| t+1 | 8094 | 18% | 5% | 5% | 24% | 10% | 4% | 1% | 1% | 3% | 19% | 9% |
| t+2 | 8094 | 15% | 4% | 5% | 31% | 14% | 5% | 1% | 3% | 2% | 9% | 11% |
| t+3 | 8094 | 12% | 3% | 4% | 32% | 14% | 5% | 2% | 6% | 2% | 7% | 13% |

### OPPONENTS: by champion type, action in the hit round / at t+1 (first hit of each episode only)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi t0 | 381 | 20% | 0% | 0% | 10% | 29% | 4% | 3% | 0% | 5% | 23% | 5% |
| Cassi t+1 | 381 | 15% | 0% | 0% | 25% | 9% | 4% | 3% | 0% | 3% | 31% | 8% |
| Issac t0 | 604 | 7% | 3% | 9% | 9% | 38% | 4% | 1% | 0% | 4% | 21% | 3% |
| Issac t+1 | 604 | 8% | 4% | 6% | 24% | 14% | 5% | 1% | 1% | 4% | 27% | 5% |
| Marcella t0 | 28 | 36% | 4% | 0% | 21% | 25% | 0% | 0% | 0% | 7% | 0% | 7% |
| Marcella t+1 | 28 | 21% | 0% | 4% | 29% | 21% | 4% | 0% | 0% | 4% | 0% | 18% |
| Prism t0 | 112 | 20% | 0% | 0% | 8% | 24% | 4% | 5% | 1% | 4% | 32% | 3% |
| Prism t+1 | 112 | 25% | 0% | 0% | 19% | 12% | 6% | 4% | 0% | 2% | 25% | 7% |
| Ren t0 | 516 | 11% | 1% | 8% | 12% | 31% | 4% | 2% | 0% | 7% | 22% | 2% |
| Ren t+1 | 516 | 15% | 1% | 4% | 18% | 14% | 4% | 2% | 1% | 6% | 29% | 5% |
| Ryth t0 | 335 | 6% | 3% | 7% | 8% | 38% | 5% | 0% | 1% | 6% | 25% | 1% |
| Ryth t+1 | 335 | 15% | 3% | 4% | 19% | 18% | 5% | 1% | 0% | 4% | 28% | 3% |
| Stellar t0 | 574 | 27% | 0% | 0% | 6% | 25% | 3% | 1% | 0% | 7% | 27% | 4% |
| Stellar t+1 | 574 | 23% | 0% | 0% | 17% | 12% | 5% | 2% | 1% | 5% | 28% | 6% |
| Tavi t0 | 317 | 16% | 0% | 3% | 8% | 25% | 3% | 2% | 0% | 5% | 37% | 2% |
| Tavi t+1 | 317 | 24% | 0% | 1% | 21% | 11% | 7% | 3% | 0% | 5% | 23% | 5% |
| Varg t0 | 307 | 8% | 4% | 11% | 9% | 35% | 3% | 1% | 0% | 8% | 20% | 2% |
| Varg t+1 | 307 | 7% | 3% | 7% | 17% | 15% | 4% | 1% | 0% | 7% | 35% | 3% |
| Vendetta t0 | 198 | 6% | 2% | 18% | 7% | 37% | 2% | 2% | 0% | 6% | 19% | 2% |
| Vendetta t+1 | 198 | 12% | 6% | 7% | 20% | 14% | 6% | 1% | 1% | 4% | 28% | 4% |
| VesperVale t0 | 9 | 56% | 0% | 0% | 22% | 22% | 0% | 0% | 0% | 0% | 0% | 0% |
| VesperVale t+1 | 9 | 33% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 56% | 11% |
| Willow t0 | 69 | 9% | 0% | 0% | 12% | 35% | 1% | 6% | 0% | 1% | 32% | 4% |
| Willow t+1 | 69 | 12% | 1% | 0% | 25% | 14% | 7% | 0% | 0% | 0% | 32% | 9% |

### OPPONENTS: by hp band before the hit (all hit rounds), action at t0 / t+1

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hp >70 t0 | 3875 | 19% | 3% | 8% | 7% | 29% | 4% | 2% | 0% | 5% | 23% | 0% |
| hp >70 t+1 | 3875 | 21% | 3% | 6% | 17% | 15% | 4% | 2% | 0% | 4% | 26% | 1% |
| hp 40-70 t0 | 2858 | 22% | 5% | 9% | 16% | 14% | 4% | 1% | 0% | 4% | 22% | 2% |
| hp 40-70 t+1 | 2858 | 20% | 6% | 6% | 31% | 8% | 5% | 1% | 1% | 3% | 16% | 4% |
| hp <40 t0 | 1361 | 11% | 8% | 3% | 21% | 4% | 4% | 0% | 2% | 2% | 19% | 27% |
| hp <40 t+1 | 1361 | 8% | 6% | 1% | 32% | 2% | 2% | 0% | 2% | 1% | 9% | 37% |

### OPPONENTS: by champion class x hp band, action at t+1 (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| melee hp >70 | 2462 | 17% | 5% | 9% | 17% | 17% | 4% | 1% | 0% | 4% | 25% | 1% |
| melee hp 40-70 | 1932 | 18% | 9% | 9% | 28% | 9% | 5% | 1% | 1% | 2% | 16% | 3% |
| melee hp <40 | 946 | 9% | 9% | 2% | 32% | 2% | 2% | 0% | 1% | 1% | 10% | 31% |
| caster hp >70 | 1338 | 29% | 0% | 0% | 17% | 13% | 5% | 3% | 0% | 4% | 27% | 2% |
| caster hp 40-70 | 862 | 23% | 0% | 0% | 37% | 5% | 6% | 2% | 2% | 3% | 16% | 7% |
| caster hp <40 | 392 | 6% | 0% | 0% | 30% | 1% | 2% | 0% | 3% | 1% | 7% | 51% |

### Rounds from the first hit of an episode to the first retreat step

Retreat step = a move that increases the distance to the nearest enemy and after which that distance is >= 2 larger 3 rounds later (or >= 1 with no attack). Only episodes in which the champion was hit by an enemy champion; "none" = no retreat step within the episode + 3 rounds.

| team | episodes | retreat within episode | delay 0 | 1 | 2 | 3 | 4-5 | 6-10 | >10 | median delay | episode died | died with no retreat step | died after a retreat step |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| us | 2866 | 62% | 252 | 377 | 365 | 283 | 262 | 219 | 17 | 2 | 717 | 349 | 368 |
| opp | 3450 | 58% | 264 | 459 | 468 | 261 | 244 | 244 | 47 | 2 | 474 | 308 | 166 |

By champion type and hp band at the first hit (us): share of episodes with a retreat step and median delay

| type | episodes | retreat | med delay | hp>70: n / retreat / delay | 40-70 | <40 |
|---|---|---|---|---|---|---|
| us Cassi | 327 | 61% | 2 | 250 / 61% / 2 | 64 / 66% / 2.0 | 13 / 46% / 0.5 |
| us Issac | 352 | 70% | 2.0 | 296 / 70% / 2.0 | 44 / 75% / 1 | 12 / 58% / 1 |
| us Prism | 197 | 46% | 3.0 | 154 / 45% / 3 | 36 / 50% / 3.0 | 7 / 43% / 2 |
| us Ren | 674 | 71% | 2 | 531 / 71% / 2 | 122 / 75% / 2.0 | 21 / 48% / 1.0 |
| us Ryth | 308 | 67% | 3 | 238 / 66% / 4.0 | 52 / 71% / 2 | 18 / 67% / 1.5 |
| us Stellar | 531 | 48% | 2 | 439 / 49% / 2 | 72 / 50% / 1.5 | 20 / 20% / 0.0 |
| us Tavi | 310 | 60% | 2.0 | 231 / 64% / 2 | 59 / 54% / 1.0 | 20 / 35% / 1 |
| us Varg | 73 | 66% | 2.0 | 57 / 67% / 3.0 | 13 / 77% / 2.0 | 3 / 0% / None |
| us Vendetta | 94 | 71% | 2 | 61 / 67% / 2 | 29 / 83% / 1.0 | 4 / 50% / 1.0 |
| opp Cassi | 381 | 55% | 2 | 285 / 53% / 2.0 | 76 / 67% / 1 | 20 / 30% / 1.0 |
| opp Issac | 604 | 64% | 2.0 | 456 / 61% / 2 | 120 / 79% / 2 | 28 / 43% / 1.0 |
| opp Marcella | 28 | 46% | 2 | 15 / 53% / 3.0 | 11 / 45% / 0 | 2 / 0% / None |
| opp Prism | 112 | 54% | 2.0 | 83 / 53% / 2.0 | 23 / 52% / 1.5 | 6 / 67% / 1.5 |
| opp Ren | 516 | 59% | 2 | 355 / 57% / 3.0 | 120 / 73% / 2.0 | 41 / 41% / 1 |
| opp Ryth | 335 | 61% | 3 | 231 / 59% / 3 | 79 / 70% / 2 | 25 / 52% / 1 |
| opp Stellar | 574 | 47% | 2 | 403 / 45% / 2.0 | 130 / 57% / 1.5 | 41 / 32% / 1 |
| opp Tavi | 317 | 52% | 2.0 | 231 / 48% / 3.0 | 73 / 64% / 1 | 13 / 54% / 1 |
| opp Varg | 307 | 64% | 2.0 | 228 / 61% / 3 | 67 / 78% / 2.0 | 12 / 42% / 1 |
| opp Vendetta | 198 | 67% | 2 | 145 / 64% / 3 | 46 / 80% / 1 | 7 / 43% / 1 |
| opp VesperVale | 9 | 56% | 2 | 4 / 25% / 4 | 5 / 80% / 1.0 | 0 / - / None |
| opp Willow | 69 | 58% | 2.0 | 48 / 56% / 2 | 20 / 65% / 1 | 1 / 0% / None |

Retreat alone or with the group (allies within 6 at the retreat step; an ally "also retreats" if its distance to the same enemy grows by >= 2 over the next 2 rounds)

| team | retreat steps | no ally within 6 | allies stay/fight | some allies retreat | all allies retreat |
|---|---|---|---|---|---|
| us | 1775 | 31% | 45% | 11% | 14% |
| opp | 1987 | 31% | 43% | 14% | 12% |

## Q2. Retreat quality

Unit = retreat step (as defined above), n us 1775, opponents 1987. "Foe follows" = in the next 12 rounds the nearest enemy (at the retreat step) made a move that reduced its distance to the retreating champion; chase length = last such round. Outcome within 15 rounds: death, recall arrived, escape (nearest enemy >= 8 and not hit in rounds 8-15), escape_near (not hit in rounds 8-15 but an enemy still within 8), still_fighting (hit again in rounds 8-15).

| team | n | hp% med | foe dist at step med | foe follows >=1 | >=3 steps | chase len med (if followed) | dist to foe +5r: med change | outrun (>= +3) | caught (<= 0) | toward spawn (dspawn -2 or more) | away from spawn (+2) | toward ally (-2) | away from ally (+2) | death | recall | escape | escape_near | still_fighting | recall started within 15r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| us all | 1775 | 54 | 3 | 76% | 39% | 8.0 | 3 | 46% | 9% | 53% | 6% | 29% | 18% | 26% | 37% | 14% | 13% | 10% | 52% |
| us melee | 1043 | 54 | 3 | 76% | 42% | 8 | 3 | 53% | 9% | 61% | 7% | 33% | 19% | 20% | 40% | 17% | 12% | 11% | 55% |
| us caster | 732 | 52.0 | 3.0 | 77% | 35% | 7 | 2.0 | 36% | 9% | 41% | 5% | 22% | 17% | 35% | 33% | 11% | 13% | 8% | 48% |
| us hp >70 | 559 | 84 | 3 | 77% | 44% | 9 | 2.0 | 38% | 18% | 45% | 14% | 34% | 16% | 19% | 14% | 22% | 21% | 23% | 29% |
| us hp 40-70 | 643 | 54 | 3 | 75% | 41% | 8 | 3 | 52% | 8% | 58% | 4% | 34% | 19% | 21% | 44% | 16% | 13% | 7% | 61% |
| us hp <40 | 573 | 27 | 2 | 77% | 32% | 5.0 | 4.0 | 47% | 2% | 54% | 1% | 17% | 20% | 40% | 52% | 4% | 3% | 1% | 65% |
| us vs melee foe | 1012 | 52.0 | 2.0 | 78% | 41% | 7.0 | 3 | 48% | 7% | 52% | 6% | 28% | 17% | 29% | 34% | 14% | 12% | 11% | 46% |
| us vs caster foe | 741 | 55 | 3 | 74% | 37% | 8 | 2 | 43% | 12% | 54% | 6% | 30% | 19% | 23% | 40% | 14% | 14% | 9% | 60% |
| opp all | 1987 | 49 | 3 | 72% | 38% | 9 | 4.0 | 60% | 7% | 63% | 9% | 29% | 23% | 13% | 47% | 15% | 13% | 12% | 61% |
| opp melee | 1240 | 50.0 | 3.0 | 72% | 37% | 9 | 4 | 62% | 7% | 64% | 10% | 33% | 22% | 13% | 45% | 15% | 12% | 14% | 60% |
| opp caster | 702 | 45.0 | 4.0 | 71% | 41% | 9.0 | 3 | 56% | 7% | 61% | 7% | 24% | 23% | 13% | 49% | 15% | 13% | 10% | 62% |
| opp hp >70 | 456 | 82.0 | 3.0 | 71% | 39% | 9 | 2.0 | 48% | 12% | 49% | 15% | 28% | 22% | 8% | 19% | 24% | 21% | 28% | 34% |
| opp hp 40-70 | 808 | 53.0 | 3.0 | 72% | 39% | 9 | 4 | 61% | 8% | 63% | 9% | 34% | 20% | 12% | 44% | 17% | 14% | 13% | 59% |
| opp hp <40 | 723 | 27 | 3 | 71% | 37% | 8 | 4 | 67% | 3% | 72% | 4% | 24% | 27% | 17% | 69% | 7% | 6% | 2% | 80% |
| opp vs melee foe | 971 | 49 | 2 | 75% | 40% | 9 | 4 | 60% | 6% | 61% | 10% | 29% | 22% | 15% | 44% | 14% | 13% | 14% | 59% |
| opp vs caster foe | 1016 | 49.0 | 3.0 | 68% | 37% | 9.0 | 3 | 61% | 7% | 65% | 8% | 29% | 24% | 11% | 50% | 16% | 12% | 11% | 63% |

Us: retreat outcome by map / result / opponent tier / champion type

| split | n | hp% med | foe follows | death | recall | escape(+near) | still fighting | recall started |
|---|---|---|---|---|---|---|---|---|
| map collision | 421 | 51 | 82% | 22% | 42% | 27% | 9% | 56% |
| map corners | 490 | 50.5 | 72% | 35% | 37% | 16% | 12% | 55% |
| map elkring | 155 | 50 | 72% | 28% | 42% | 25% | 5% | 54% |
| map expanse | 11 | 71 | 73% | 0% | 45% | 55% | 0% | 45% |
| map interlock | 159 | 67 | 77% | 16% | 31% | 38% | 14% | 49% |
| map lanes | 176 | 50.0 | 74% | 19% | 31% | 40% | 10% | 41% |
| map monolith | 108 | 57.0 | 83% | 23% | 24% | 40% | 13% | 36% |
| map packs | 249 | 57 | 76% | 29% | 39% | 25% | 7% | 55% |
| map rows | 6 | 71.0 | 67% | 17% | 0% | 83% | 0% | 17% |
| result win | 595 | 56 | 74% | 19% | 39% | 32% | 10% | 52% |
| result loss | 1180 | 53.0 | 77% | 30% | 36% | 24% | 10% | 52% |
| opp top10 | 668 | 56.0 | 79% | 27% | 37% | 25% | 12% | 54% |
| opp 11-20 | 593 | 51 | 76% | 24% | 38% | 27% | 10% | 51% |
| opp 21-30 | 507 | 52 | 73% | 29% | 35% | 29% | 7% | 50% |
| opp other | 7 | 48 | 71% | 0% | 43% | 57% | 0% | 57% |
| Cassi | 201 | 49 | 82% | 32% | 34% | 28% | 6% | 48% |
| Issac | 246 | 56.5 | 82% | 22% | 40% | 28% | 10% | 54% |
| Prism | 90 | 46.0 | 71% | 47% | 30% | 18% | 6% | 44% |
| Ren | 477 | 56 | 75% | 18% | 43% | 27% | 12% | 57% |
| Ryth | 205 | 48 | 67% | 26% | 36% | 27% | 12% | 58% |
| Stellar | 255 | 54 | 82% | 33% | 37% | 24% | 6% | 49% |
| Tavi | 186 | 57.0 | 68% | 36% | 28% | 23% | 13% | 46% |
| Varg | 48 | 59.5 | 79% | 8% | 29% | 52% | 10% | 33% |
| Vendetta | 67 | 50 | 79% | 16% | 37% | 36% | 10% | 52% |

Examples (us): retreats that ended in death: 64d3af95 corners Ryth r498 hp62% foe Ryth at 2; 64d3af95 corners Ryth r598 hp58% foe Ren at 1; 64d3af95 corners Prism r540 hp66% foe Issac at 3; 64d3af95 corners Ren r365 hp58% foe Varg at 2; 64d3af95 corners Tavi r335 hp53% foe Cassi at 1; 64d3af95 corners Tavi r559 hp52% foe Varg at 1; 7ba9fe5c packs Cassi r415 hp100% foe Vendetta at 3; ca10ce5a elkring Stellar r537 hp92% foe Ryth at 2; ca10ce5a elkring Ren r517 hp50% foe Vendetta at 1; 14ebd970 rows Issac r111 hp58% foe Vendetta at 2; d97caaff elkring Tavi r67 hp51% foe Ren at 4; 40eab0a2 monolith Vendetta r419 hp90% foe Varg at 1; 5889b79f packs Cassi r186 hp60% foe Ren at 1; 5889b79f packs Issac r178 hp58% foe Stellar at 2; 95784669 collision Issac r34 hp52% foe Stellar at 1; 95784669 collision Issac r361 hp60% foe Ren at 1; 7650c0e0 packs Ren r134 hp70% foe Stellar at 4; 7650c0e0 packs Ren r429 hp63% foe Ryth at 2; 69757c8e collision Cassi r862 hp76% foe Issac at 2; 69757c8e collision Issac r272 hp49% foe Cassi at 3; 69757c8e collision Issac r555 hp81% foe Ren at 4; 69757c8e collision Ren r132 hp93% foe Stellar at 4; 69757c8e collision Ren r868 hp100% foe Stellar at 4; 69757c8e collision Stellar r745 hp73% foe Issac at 1; 697

Examples (us): retreats saved by recall: 79bed885 collision Cassi r258 hp21% recall after 6 rounds; 79bed885 collision Issac r213 hp48% recall after 7 rounds; 79bed885 collision Stellar r468 hp76% recall after 9 rounds; 64d3af95 corners Ryth r208 hp48% recall after 6 rounds; 64d3af95 corners Ryth r261 hp32% recall after 3 rounds; 64d3af95 corners Ryth r314 hp27% recall after 8 rounds; 64d3af95 corners Stellar r271 hp64% recall after 6 rounds; 64d3af95 corners Stellar r316 hp52% recall after 6 rounds; 64d3af95 corners Stellar r450 hp32% recall after 4 rounds; 64d3af95 corners Stellar r507 hp35% recall after 4 rounds; 64d3af95 corners 

## Q3. Recall use

Unit = recall attempt. Outcome: arrived (spawn jump 5 rounds later), hit_foe / hit_camp (first damage before arrival), died, moved / attacked (voluntary cancel), restart. "retry" = a new attempt within 10 rounds after an interrupted one. Reference (Mite, 101 games of 07:00 today): heal trigger hp < 50% strict, starts with the nearest foe at 7-8 tiles in 35% of cases, 9.7% interrupted, retries 59% of interruptions.

| team | starts | per game | arrived | hit by foe | hit by camp | died | moved (cancel) | attacked (cancel) | restart | hp% med / p10 / p90 | share hp<50 | gems med / share >0 | dfoe med / p10 | dfoe <= 5 | dfoe 6-8 | dfoe >= 9 | hit by a foe in prev 3 rounds | retries | spawn dist med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| us all | 3860 | 25.7 | 91% | 5% | 0% | 2% | 0% | 0% | 0% | 51.0 / 20 / 88 | 48% | 0.0 / 16% | 14.0 / 5 | 16% | 13% | 71% | 15% | 3% | 13.0 |
| us Cassi | 377 | - | 89% | 6% | 0% | 4% | 0% | 0% | 0% | 46 / 18 / 89 | 55% | 0 / 17% | 13 / 5 | 20% | 11% | 70% | 15% | 4% | 12 |
| us Issac | 702 | - | 94% | 3% | 0% | 2% | 0% | 0% | 0% | 53.0 / 22 / 89 | 47% | 0.0 / 15% | 15.0 / 5 | 10% | 12% | 78% | 9% | 2% | 13.0 |
| us Prism | 171 | - | 85% | 10% | 0% | 4% | 0% | 0% | 0% | 46 / 18 / 91 | 55% | 0 / 11% | 12 / 4 | 30% | 8% | 61% | 23% | 6% | 9 |
| us Ren | 784 | - | 90% | 7% | 0% | 2% | 0% | 0% | 0% | 46.5 / 20 / 87 | 55% | 0.0 / 18% | 11.0 / 5 | 19% | 20% | 61% | 22% | 5% | 11.0 |
| us Ryth | 443 | - | 88% | 7% | 0% | 2% | 0% | 0% | 0% | 52 / 16 / 89 | 46% | 0 / 23% | 13 / 5 | 18% | 15% | 67% | 14% | 5% | 16 |
| us Stellar | 454 | - | 91% | 5% | 0% | 3% | 0% | 0% | 0% | 51.0 / 19 / 90 | 48% | 0.0 / 20% | 10.0 / 4 | 26% | 19% | 55% | 22% | 3% | 11.0 |
| us Tavi | 271 | - | 83% | 10% | 0% | 5% | 0% | 0% | 0% | 48 / 16 / 83 | 53% | 0 / 13% | 11 / 4 | 32% | 9% | 59% | 27% | 7% | 12 |
| us Varg | 303 | - | 99% | 0% | 0% | 0% | 0% | 0% | 0% | 74 / 31 / 94 | 22% | 0 / 12% | 31 / 9 | 1% | 5% | 94% | 0% | 0% | 25 |
| us Vendetta | 355 | - | 99% | 0% | 0% | 0% | 0% | 0% | 0% | 51 / 22 / 82 | 41% | 0 / 11% | 33 / 10 | 1% | 4% | 95% | 1% | 0% | 21 |
| opp all | 5114 | 34.1 | 62% | 11% | 20% | 2% | 3% | 0% | 0% | 56.0 / 20 / 98 | 45% | 0.0 / 30% | 12.0 / 4 | 14% | 21% | 64% | 14% | 32% | 17.0 |
| opp Cassi | 692 | - | 56% | 9% | 27% | 3% | 3% | 0% | 0% | 49.0 / 21 / 100 | 52% | 0.0 / 17% | 13.0 / 5 | 13% | 21% | 66% | 11% | 35% | 16.0 |
| opp Issac | 1114 | - | 56% | 11% | 27% | 3% | 2% | 0% | 0% | 61.0 / 22 / 98 | 40% | 0.0 / 29% | 14.0 / 4 | 14% | 17% | 69% | 13% | 38% | 16.0 |
| opp Marcella | 25 | - | 96% | 0% | 0% | 4% | 0% | 0% | 0% | 57 / 20 / 100 | 48% | 0 / 40% | 9 / 6 | 4% | 40% | 56% | 16% | 0% | 15 |
| opp Prism | 155 | - | 46% | 23% | 23% | 3% | 2% | 0% | 0% | 50 / 15 / 100 | 48% | 0 / 26% | 7 / 4 | 31% | 33% | 36% | 20% | 48% | 19 |
| opp Ren | 699 | - | 61% | 13% | 19% | 1% | 4% | 0% | 0% | 60 / 20 / 98 | 43% | 0 / 36% | 12 / 4 | 14% | 23% | 63% | 17% | 35% | 18 |
| opp Ryth | 602 | - | 40% | 21% | 31% | 1% | 5% | 0% | 0% | 73.0 / 20 / 100 | 34% | 0.0 / 31% | 11.0 / 3 | 24% | 17% | 59% | 20% | 55% | 17.0 |
| opp Stellar | 765 | - | 59% | 13% | 21% | 3% | 3% | 0% | 0% | 56 / 21 / 100 | 44% | 0 / 30% | 11 / 4 | 17% | 21% | 62% | 15% | 36% | 16 |
| opp Tavi | 247 | - | 85% | 4% | 5% | 1% | 3% | 0% | 0% | 33 / 13 / 63 | 82% | 0 / 28% | 9 / 5 | 12% | 38% | 50% | 13% | 7% | 15 |
| opp Varg | 388 | - | 95% | 3% | 1% | 0% | 1% | 0% | 0% | 70.0 / 22 / 96 | 34% | 0.0 / 39% | 14.0 / 6 | 5% | 21% | 74% | 8% | 2% | 18.5 |
| opp Vendetta | 359 | - | 90% | 3% | 5% | 1% | 0% | 0% | 0% | 44 / 18 / 91 | 54% | 0 / 37% | 15 / 6 | 4% | 21% | 75% | 7% | 4% | 18 |
| opp VesperVale | 16 | - | 62% | 0% | 0% | 0% | 38% | 0% | 0% | 13.5 / 9 / 78 | 81% | 0.0 / 12% | 6.0 / 3 | 50% | 6% | 44% | 12% | 38% | 32.0 |
| opp Willow | 52 | - | 88% | 0% | 0% | 2% | 10% | 0% | 0% | 31.5 / 14 / 100 | 77% | 0.0 / 10% | 8.0 / 7 | 6% | 46% | 48% | 8% | 0% | 16.0 |

Us: recall starts by hp band / foe distance (interruption = hit_foe + hit_camp + died)

| split | starts | arrived | interrupted | hit_foe | hit_camp | died | voluntary cancel | retries |
|---|---|---|---|---|---|---|---|---|
| us hp >70 | 1161 | 97% | 2% | 12 | 1 | 5 | 0 | 0% |
| us hp 40-70 | 1322 | 91% | 8% | 96 | 1 | 6 | 0 | 1% |
| us hp <40 | 1377 | 87% | 13% | 84 | 7 | 82 | 1 | 8% |
| us dfoe 1-3 | 63 | 49% | 51% | 22 | 0 | 10 | 0 | 10% |
| us dfoe 4 | 174 | 64% | 34% | 34 | 1 | 24 | 0 | 14% |
| us dfoe 5 | 399 | 66% | 33% | 97 | 1 | 33 | 0 | 13% |
| us dfoe 6 | 222 | 80% | 19% | 25 | 3 | 14 | 1 | 11% |
| us dfoe 7-8 | 277 | 93% | 6% | 14 | 1 | 2 | 0 | 3% |
| us dfoe 9+ | 2725 | 99% | 0% | 0 | 3 | 10 | 0 | 0% |
| us hit in prev 3 rounds | 571 | 67% | 32% | 115 | 3 | 63 | 0 | 16% |
| us not hit recently | 3289 | 96% | 3% | 77 | 6 | 30 | 1 | 1% |
| opp hp >70 | 1979 | 45% | 50% | 238 | 736 | 11 | 79 | 48% |
| opp hp 40-70 | 1360 | 67% | 30% | 203 | 193 | 15 | 27 | 29% |
| opp hp <40 | 1775 | 78% | 18% | 133 | 110 | 80 | 53 | 17% |
| opp dfoe 1-3 | 339 | 11% | 84% | 233 | 21 | 32 | 16 | 85% |
| opp dfoe 4 | 209 | 30% | 66% | 115 | 13 | 9 | 7 | 74% |
| opp dfoe 5 | 188 | 44% | 48% | 66 | 15 | 10 | 14 | 47% |
| opp dfoe 6 | 308 | 69% | 26% | 48 | 11 | 22 | 14 | 15% |
| opp dfoe 7-8 | 791 | 85% | 13% | 40 | 44 | 19 | 13 | 9% |
| opp dfoe 9+ | 3279 | 65% | 31% | 72 | 935 | 14 | 95 | 30% |
| opp hit in prev 3 rounds | 709 | 46% | 51% | 291 | 17 | 51 | 18 | 54% |
| opp not hit recently | 4405 | 65% | 31% | 283 | 1022 | 55 | 141 | 28% |

Us: recall starts per map and per result (starts per game, arrival rate, hp med, dfoe med)

| split | games | starts/game | arrived | hp med | dfoe med | hit_foe | hit_camp | died |
|---|---|---|---|---|---|---|---|---|
| map collision | 19 | 32.8 | 91% | 45.0 | 10.0 | 28 | 7 | 18 |
| map corners | 17 | 24.8 | 72% | 37.0 | 5.0 | 83 | 0 | 34 |
| map elkring | 14 | 45.9 | 94% | 50.5 | 15.0 | 26 | 0 | 7 |
| map expanse | 17 | 15.1 | 99% | 53.0 | 47.5 | 0 | 0 | 0 |
| map interlock | 13 | 30.2 | 89% | 63 | 12 | 26 | 1 | 10 |
| map lanes | 18 | 11.4 | 97% | 38 | 11 | 2 | 0 | 1 |
| map monolith | 13 | 31.5 | 98% | 64.0 | 18.0 | 3 | 0 | 0 |
| map packs | 21 | 24.2 | 90% | 58.0 | 11.0 | 24 | 1 | 23 |
| map rows | 18 | 22.2 | 99% | 67.0 | 34.0 | 0 | 0 | 0 |
| res win | 59 | 27.8 | 94% | 54 | 15 | 53 | 5 | 24 |
| res loss | 91 | 24.4 | 89% | 49 | 13 | 139 | 4 | 69 |
| tier top10 | 50 | 25.5 | 89% | 50 | 13 | 82 | 5 | 40 |
| tier 11-20 | 50 | 26.5 | 93% | 51.0 | 14.0 | 54 | 3 | 21 |
| tier 21-30 | 45 | 25.5 | 92% | 51.0 | 14.0 | 56 | 0 | 32 |
| tier other | 5 | 22.6 | 99% | 63 | 18 | 0 | 1 | 0 |

After an interruption (hit_foe / hit_camp / voluntary cancel), what the champion does in the next 10 rounds:

| team | interrupted attempts | retry | retry within 2 rounds of the interruption | died | fought | walked | none |
|---|---|---|---|---|---|---|---|
| us | 202 | 32% | 30% | 15% | 50% | 2% | 0% |
| opp | 1772 | 82% | 82% | 3% | 9% | 6% | 0% |

Examples (us): recall started with a foe within 3 and interrupted: 40eab0a2 monolith Varg r355 hp52% dfoe 1 gems 44 -> hit_foe; 3a260573 interlock Issac r85 hp40% dfoe 2 gems 0 -> hit_foe; f2e5fff6 packs Cassi r183 hp11% dfoe 2 gems 0 -> died; 2f3472aa elkring Tavi r278 hp46% dfoe 2 gems 36 -> hit_foe; 0969a47f packs Issac r462 hp15% dfoe 3 gems 0 -> died; 84203fcb elkring Ren r550 hp48% dfoe 2 gems 36 -> hit_foe; 49e46ec2 packs Cassi r311 hp15% dfoe 3 gems 0 -> died; c64c25a3 elkring Prism r372 hp21% dfoe 3 gems 36 -> hit_foe; feb23cc4 interlock Tavi r562 hp22% dfoe 3 gems 22 -> hit_foe; e3bc608b corners Ryth r183 hp19% dfoe 2 gems 0 -> died; 3a387edd packs Stellar r473 hp51% dfoe 3 gems 0 -> hit_foe; 6784822d elkring Stellar r223 hp52% dfoe 2 gems 36 -> h

Examples (us): recall interrupted by a camp: 73c3155e interlock Stellar r126 hp52%; cce8926b collision Cassi r240 hp18%; cce8926b collision Issac r488 hp78%; 95784669 collision Issac r436 hp23%; 95784669 collision Ren r438 hp36%; e599d53c collision Issac r428 hp29%; 4ced717d packs Stellar r236 hp17%; 9ff21528 collision Ren r222 hp29%; ae2470ab collision Ren r387 hp37%

## Q4. Help

Unit = (first hit of an episode, ally alive within 8 tiles of the victim at the previous round end). Over the next 5 rounds the ally: **fought** (attacked/cast on an enemy champion), **came** (its distance to the victim shrank by >= 2 without fighting), **kept farming** (hit a camp in >= 2 of the rounds), **moved away** (>= 2 "away" moves), **other**. Time to help = first round (0 = the hit round) at which the ally came or fought.

| team | victim-ally pairs | fought | came | kept farming | moved away | other | time to help med | help at t0 | t1 | t2 | t3+ | victim died: help rate | victim survived: help rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| us all | 4326 | 29% | 20% | 12% | 15% | 24% | 1 | 12% | 14% | 9% | 14% | 32% | 54% |
| us ally was farming a camp | 631 | 12% | 24% | 46% | 6% | 12% | 2.5 | 3% | 8% | 7% | 18% | 26% | 39% |
| us ally was recalling | 298 | 4% | 3% | 1% | 1% | 91% | 1.0 | 1% | 3% | 2% | 2% | 8% | 7% |
| us ally within 3 | 1822 | 43% | 5% | 10% | 16% | 27% | 1 | 14% | 11% | 9% | 13% | 35% | 50% |
| us ally 4-8 | 2504 | 19% | 31% | 13% | 14% | 22% | 1.0 | 11% | 16% | 10% | 14% | 30% | 56% |
| us ally hp < 40 | 452 | 10% | 9% | 1% | 22% | 58% | 1.0 | 6% | 5% | 3% | 5% | 10% | 22% |
| us ally melee | 1929 | 25% | 20% | 12% | 17% | 27% | 1.0 | 11% | 13% | 9% | 12% | 28% | 49% |
| us ally caster | 2397 | 33% | 20% | 12% | 14% | 22% | 1 | 13% | 14% | 10% | 15% | 35% | 57% |
| us ally Cassi | 610 | 24% | 24% | 10% | 18% | 24% | 2.0 | 11% | 12% | 10% | 16% | 27% | 53% |
| us ally Issac | 542 | 12% | 26% | 14% | 20% | 28% | 1.0 | 9% | 12% | 7% | 10% | 23% | 42% |
| us ally Prism | 334 | 43% | 14% | 7% | 13% | 23% | 1.0 | 15% | 15% | 12% | 15% | 47% | 60% |
| us ally Ren | 795 | 31% | 17% | 11% | 13% | 27% | 1 | 13% | 13% | 11% | 11% | 31% | 54% |
| us ally Ryth | 413 | 34% | 14% | 10% | 16% | 26% | 1 | 11% | 14% | 9% | 14% | 28% | 54% |
| us ally Stellar | 851 | 38% | 17% | 11% | 13% | 21% | 1 | 15% | 15% | 10% | 16% | 37% | 60% |
| us ally Tavi | 602 | 29% | 22% | 15% | 12% | 21% | 1.0 | 11% | 16% | 9% | 15% | 34% | 56% |
| us ally Varg | 85 | 14% | 20% | 12% | 27% | 27% | 1 | 9% | 9% | 6% | 9% | 28% | 36% |
| us ally Vendetta | 94 | 10% | 30% | 15% | 20% | 26% | 1 | 10% | 12% | 3% | 15% | 24% | 43% |
| opp all | 6037 | 30% | 19% | 7% | 15% | 29% | 1.0 | 12% | 14% | 9% | 13% | 31% | 51% |
| opp ally was farming a camp | 549 | 20% | 20% | 40% | 6% | 13% | 2 | 5% | 8% | 12% | 15% | 23% | 42% |
| opp ally was recalling | 742 | 19% | 11% | 3% | 4% | 63% | 1.5 | 6% | 9% | 8% | 7% | 21% | 31% |
| opp ally within 3 | 3116 | 41% | 5% | 7% | 19% | 28% | 1.0 | 14% | 12% | 7% | 13% | 31% | 47% |
| opp ally 4-8 | 2921 | 19% | 34% | 8% | 11% | 29% | 1.0 | 10% | 17% | 12% | 14% | 31% | 56% |
| opp ally hp < 40 | 869 | 10% | 11% | 1% | 22% | 56% | 1 | 8% | 5% | 4% | 5% | 16% | 22% |
| opp ally melee | 2807 | 25% | 20% | 7% | 17% | 31% | 1.0 | 11% | 13% | 9% | 12% | 29% | 47% |
| opp ally caster | 3006 | 36% | 18% | 8% | 13% | 25% | 1.0 | 15% | 15% | 10% | 14% | 33% | 56% |
| opp ally Cassi | 995 | 27% | 20% | 10% | 16% | 27% | 2 | 11% | 12% | 10% | 13% | 28% | 49% |
| opp ally Issac | 881 | 17% | 23% | 7% | 20% | 34% | 1 | 10% | 11% | 7% | 11% | 30% | 40% |
| opp ally Marcella | 34 | 32% | 9% | 3% | 18% | 38% | 1.0 | 18% | 18% | 0% | 6% | 40% | 41% |
| opp ally Prism | 273 | 47% | 12% | 9% | 10% | 22% | 1.0 | 17% | 19% | 8% | 16% | 29% | 61% |
| opp ally Ren | 668 | 33% | 18% | 6% | 12% | 30% | 1.0 | 13% | 15% | 10% | 14% | 29% | 53% |
| opp ally Ryth | 615 | 35% | 17% | 6% | 16% | 27% | 1.0 | 11% | 16% | 12% | 13% | 32% | 55% |
| opp ally Stellar | 1059 | 42% | 17% | 6% | 10% | 25% | 1.0 | 17% | 16% | 10% | 16% | 38% | 62% |
| opp ally Tavi | 679 | 36% | 18% | 7% | 15% | 24% | 1 | 14% | 17% | 9% | 13% | 32% | 56% |
| opp ally Varg | 394 | 18% | 20% | 7% | 20% | 35% | 2 | 6% | 11% | 9% | 11% | 19% | 41% |
| opp ally Vendetta | 215 | 21% | 23% | 7% | 18% | 32% | 1.0 | 13% | 13% | 8% | 10% | 35% | 45% |
| opp ally VesperVale | 6 | 33% | 0% | 17% | 17% | 33% | 0.5 | 17% | 17% | 0% | 0% | 50% | 25% |
| opp ally Willow | 218 | 15% | 23% | 15% | 11% | 35% | 2.0 | 4% | 13% | 9% | 13% | 29% | 40% |

Us: help rate (fought or came) by map / result / tier

| split | pairs | fought+came | kept farming |
|---|---|---|---|
| map collision | 1051 | 47% | 10% |
| map corners | 1398 | 59% | 8% |
| map elkring | 319 | 41% | 13% |
| map expanse | 11 | 55% | 9% |
| map interlock | 481 | 41% | 19% |
| map lanes | 475 | 43% | 17% |
| map monolith | 118 | 44% | 8% |
| map packs | 457 | 45% | 14% |
| map rows | 16 | 38% | 12% |
| tier top10 | 1548 | 50% | 10% |
| tier 11-20 | 1431 | 46% | 13% |
| tier 21-30 | 1331 | 51% | 12% |
| tier other | 16 | 19% | 31% |

Examples (us): ally kept farming while the victim died: 7ba9fe5c packs victim Cassi r415 (ally Ren at 7); d97caaff elkring victim Stellar r65 (ally Ryth at 7); 5889b79f packs victim Cassi r183 (ally Ren at 6); 95784669 collision victim Issac r30 (ally Stellar at 2); 95784669 collision victim Issac r359 (ally Cassi at 3); 170d7411 interlock victim Cassi r183 (ally Tavi at 7); 7650c0e0 packs victim Cassi r91 (ally Ren at 5); 7650c0e0 packs victim Cassi r91 (ally Stellar at 5); 244f6a8b corners victim Ryth r24 (ally Stellar at 6); 244f6a8b corners victim Ryth r24 (ally Ren at 4); 3a260573 interlock victim Issac r248 (ally Cassi at 7); 3a260573 interlo

## Q5. Deaths

### US: 858 deaths (5.72 per game), 149 of them pair deaths (Cassi/Issac partner died with the other), 709 direct

Direct deaths only below. Final episode = the run of enemy-champion hits (gaps <= 5) that ends in the death (camp-only deaths: from the first camp hit in the last 30 rounds). "Before" = dominant action in the 5 rounds before the first hit of the final episode; "last 5" = dominant action in the 5 rounds before death.

| | count |
|---|---|
| killing blow: champion spell / champion attack / camp | 367 / 317 / 25 |
| killer type | Stellar 211, Tavi 80, Ren 75, Ryth 55, Cassi 54, Varg 54, Issac 52, Vendetta 42 |
| zone at death: own half / middle / enemy half | 521 / 166 / 22 |
| distance to own spawn at death: med / p25 / p75; <= 6 | 14 / 11 / 18; 64 |
| distance to nearest altar at death: med; <= 2 | 7; 62 |
| doing before the final episode | approaching 270, fleeing 141, idle 82, farming 64, fighting 56, walking 38, recalling 34, tributing 24 |
| doing in the last 5 rounds | fleeing 208, fighting 178, approaching 103, idle 77, recalling 67, walking 41, farming 21, tributing 14 |
| hp% at the first hit of the final episode: med / p25 / p75; >= 70: ; < 40: | 90 / 64 / 100; 501; 71 |
| length of the final episode (rounds): med; 1 round; 2-3; 4-8; > 8 | 5; 82; 139; 292; 196 |
| enemy champions dealing damage in the episode: 1 / 2 / 3+ | 289 / 255 / 146 |
| share of episode damage from spells: med; >= 80%: ; camp-damage share > 50%: | 68; 287; 20 |
| allies within 6 at death: 0 / 1 / 2+ ; all allies dead | 258 / 256 / 195 ; 31 |
| allies within 8 at the first hit: 0 / 1 / 2+ | 183 / 240 / 286 |
| enemies within 8 at the first hit: 1 / 2 / 3+ (outnumbered: foes8 > allies8+1) | 176 / 209 / 324 (276) |
| gems carried at death: deaths with gems / total gems lost / per game / med bag when > 0 / max | 227 / 8586 / 57.2 / 36 / 174 |
| recall in progress at death / recall attempted in the episode | 107 / 111 |
| retreat moves in the episode: 0 / 1-2 / 3+ ; fought back >= 1 round | 351 / 214 / 144 ; 431 |

Per champion type (direct deaths): 

| type | deaths | per game drafted | hp first hit med | ep len med | fled 0 | recall tried | allies6 = 0 | spells >= 80% | gems lost | top killer |
|---|---|---|---|---|---|---|---|---|---|---|
| Cassi | 88 | 0.74 | 84.0 | 5.0 | 45% | 19% | 30% | 48% | 1446 | Stellar |
| Issac | 79 | 0.66 | 98 | 4 | 59% | 16% | 20% | 41% | 1632 | Stellar |
| Prism | 79 | 2.55 | 97 | 6 | 47% | 14% | 29% | 37% | 742 | Stellar |
| Ren | 106 | 1.26 | 80.5 | 5.0 | 53% | 25% | 43% | 55% | 1052 | Stellar |
| Ryth | 65 | 0.81 | 94 | 9 | 43% | 23% | 42% | 29% | 588 | Stellar |
| Stellar | 164 | 1.95 | 92.0 | 5.0 | 52% | 7% | 44% | 38% | 2120 | Stellar |
| Tavi | 103 | 1.37 | 84 | 6 | 40% | 17% | 35% | 36% | 782 | Stellar |
| Varg | 9 | 0.14 | 74 | 4 | 89% | 0% | 56% | 56% | 114 | Tavi |
| Vendetta | 16 | 0.24 | 73.0 | 4.0 | 56% | 0% | 44% | 19% | 110 | Stellar |

Per map / result / tier (all deaths incl. pair): deaths per game, gems lost per game

| split | games | deaths | per game | gems lost | per game | zone own/mid/enemy | before: farming / tributing / recalling / fighting / walking / fleeing |
|---|---|---|---|---|---|---|---|
| map collision | 19 | 215 | 11.3 | 2402 | 126 | 139/71/5 | 5 / 11 / 9 / 8 / 10 / 25 |
| map corners | 17 | 230 | 13.5 | 1902 | 112 | 185/40/5 | 10 / 9 / 16 / 22 / 7 / 50 |
| map elkring | 14 | 91 | 6.5 | 1404 | 100 | 71/17/3 | 12 / 1 / 4 / 7 / 11 / 19 |
| map expanse | 17 | 0 | 0.0 | 0 | 0 | 0/0/0 | 0 / 0 / 0 / 0 / 0 / 0 |
| map interlock | 13 | 56 | 4.3 | 1486 | 114 | 42/12/2 | 4 / 1 / 0 / 5 / 3 / 5 |
| map lanes | 18 | 68 | 3.8 | 280 | 16 | 57/8/3 | 7 / 2 / 0 / 4 / 1 / 5 |
| map monolith | 13 | 49 | 3.8 | 630 | 48 | 36/10/3 | 6 / 0 / 0 / 0 / 0 / 13 |
| map packs | 21 | 147 | 7.0 | 416 | 20 | 120/26/1 | 20 / 0 / 5 / 10 / 6 / 23 |
| map rows | 18 | 2 | 0.1 | 66 | 4 | 2/0/0 | 0 / 0 / 0 / 0 / 0 / 1 |
| res win | 59 | 195 | 3.3 | 2524 | 43 | 131/59/5 | 10 / 13 / 7 / 9 / 7 / 33 |
| res loss | 91 | 663 | 7.3 | 6062 | 67 | 521/125/17 | 54 / 11 / 27 / 47 / 31 / 108 |
| tier top10 | 50 | 317 | 6.3 | 3030 | 61 | 248/63/6 | 25 / 7 / 21 / 22 / 9 / 53 |
| tier 11-20 | 50 | 273 | 5.5 | 2928 | 59 | 196/68/9 | 16 / 8 / 2 / 15 / 13 / 49 |
| tier 21-30 | 45 | 266 | 5.9 | 2584 | 57 | 208/51/7 | 23 / 8 / 11 / 19 / 16 / 39 |
| tier other | 5 | 2 | 0.4 | 44 | 9 | 0/2/0 | 0 / 1 / 0 / 0 / 0 / 0 |

Deaths per game distribution: 0: 44 games, 1: 11 games, 2: 7 games, 3: 6 games, 4: 9 games, 5: 11 games, 6: 6 games, 7: 15 games, 8: 3 games, 9: 4 games, 10: 7 games, 11: 3 games, 12: 4 games, 13: 2 games, 14: 1 games, 15: 3 games, 16: 3 games, 18: 2 games, 19: 1 games, 20: 1 games, 21: 2 games, 22: 1 games, 23: 1 games, 24: 1 games, 25: 1 games, 28: 1 games

Examples: 79bed885 collision Issac r441 tributing hp100% ep 3 rounds 2 foes spells 93% allies6 2 gems 0 killer Stellar; 64d3af95 corners Ryth r398 approaching hp90% ep 19 rounds 2 foes spells 32% allies6 0 gems 0 killer Ren; 64d3af95 corners Ryth r509 approaching hp82% ep 17 rounds 3 foes spells 35% allies6 3 gems 0 killer Vendetta; 64d3af95 corners Ryth r601 approaching hp98% ep 10 rounds 2 foes spells 11% allies6 0 gems 0 killer Vendetta; 64d3af95 corners Stellar r172 fighting hp87% ep 13 rounds 2 foes spells 44% allies6 0 gems 0 killer Ryth; 64d3af95 corners Stellar r359 approaching hp97% ep 8 rounds 4 foes spells 33% allies6 0 gems 0 killer Vendetta; d97caaff elkring Tavi r73 fleeing hp43% ep 2 rounds 2 foes spells 100% allies6 1 gems 0 killer Stellar RECALLING; 95784669 collision Issac r38 farming hp76% ep 9 rounds 2 foes spells 85% allies6 2 gems 0 killer Stellar RECALLING; 95784669 collision Stellar r232 recalling hp11% ep 1 rounds 1 foes spells 100% allies6 0 gems 22 killer Stellar RECALLING; 7650c0e0 packs Cassi r393 fleeing hp100% ep 5 rounds 1 foes spells 100% allies6 0 gems 0 killer Stellar RECALLING; 79bed885 collision Issac r441 tributing hp100% ep 3 rounds 2 foes spells 93% allies6 2 gems 0 killer Stellar; 69757c8e collision Issac r866 tributing hp100% ep 2 rounds 2 foes spells 79% allies6 1 gems 0 killer Cassi; 524c5b58 collision Cassi r110 tributing hp80% ep 5 rounds 2 foes spells 83% allies6 1 gems 0 killer Stellar

### OPPONENTS: 581 deaths (3.87 per game), 124 of them pair deaths (Cassi/Issac partner died with the other), 457 direct

Direct deaths only below. Final episode = the run of enemy-champion hits (gaps <= 5) that ends in the death (camp-only deaths: from the first camp hit in the last 30 rounds). "Before" = dominant action in the 5 rounds before the first hit of the final episode; "last 5" = dominant action in the 5 rounds before death.

| | count |
|---|---|
| killing blow: champion spell / champion attack / camp | 295 / 140 / 22 |
| killer type | Stellar 164, Ren 71, Cassi 37, Issac 36, Ryth 35, Tavi 33, Prism 27, camp 22 |
| zone at death: own half / middle / enemy half | 135 / 173 / 149 |
| distance to own spawn at death: med / p25 / p75; <= 6 | 19 / 16 / 22; 11 |
| distance to nearest altar at death: med; <= 2 | 5; 100 |
| doing before the final episode | approaching 207, fleeing 63, recalling 43, idle 35, tributing 35, fighting 29, farming 26, walking 19 |
| doing in the last 5 rounds | approaching 117, fighting 109, fleeing 87, recalling 46, idle 35, tributing 29, walking 22, farming 12 |
| hp% at the first hit of the final episode: med / p25 / p75; >= 70: ; < 40: | 72 / 42 / 100; 234; 107 |
| length of the final episode (rounds): med; 1 round; 2-3; 4-8; > 8 | 4; 100; 125; 114; 118 |
| enemy champions dealing damage in the episode: 1 / 2 / 3+ | 209 / 156 / 81 |
| share of episode damage from spells: med; >= 80%: ; camp-damage share > 50%: | 86; 270; 13 |
| allies within 6 at death: 0 / 1 / 2+ ; all allies dead | 181 / 140 / 136 ; 9 |
| allies within 8 at the first hit: 0 / 1 / 2+ | 133 / 141 / 183 |
| enemies within 8 at the first hit: 1 / 2 / 3+ (outnumbered: foes8 > allies8+1) | 122 / 157 / 178 (147) |
| gems carried at death: deaths with gems / total gems lost / per game / med bag when > 0 / max | 204 / 8540 / 56.9 / 36.0 / 152 |
| recall in progress at death / recall attempted in the episode | 96 / 72 |
| retreat moves in the episode: 0 / 1-2 / 3+ ; fought back >= 1 round | 312 / 92 / 53 ; 199 |

Per champion type (direct deaths): 

| type | deaths | per game drafted | hp first hit med | ep len med | fled 0 | recall tried | allies6 = 0 | spells >= 80% | gems lost | top killer |
|---|---|---|---|---|---|---|---|---|---|---|
| Cassi | 58 | 0.45 | 66.0 | 2.0 | 67% | 14% | 19% | 62% | 1116 | Stellar |
| Issac | 76 | 0.59 | 77.0 | 4.0 | 68% | 24% | 32% | 58% | 1610 | Stellar |
| Marcella | 8 | 1.60 | 63.5 | 2.0 | 88% | 0% | 38% | 88% | 154 | Stellar |
| Prism | 16 | 1.00 | 87.5 | 2.5 | 69% | 31% | 44% | 69% | 120 | Stellar |
| Ren | 55 | 0.74 | 63 | 3 | 80% | 7% | 35% | 65% | 1316 | Stellar |
| Ryth | 50 | 0.86 | 72.5 | 6.0 | 58% | 26% | 54% | 36% | 592 | Stellar |
| Stellar | 88 | 0.82 | 67.5 | 3.5 | 62% | 20% | 45% | 59% | 1762 | Stellar |
| Tavi | 35 | 0.56 | 72 | 3 | 74% | 6% | 26% | 66% | 480 | Stellar |
| Varg | 30 | 0.38 | 71.0 | 5.5 | 67% | 7% | 73% | 50% | 510 | Stellar |
| Vendetta | 27 | 0.46 | 75 | 4 | 70% | 7% | 48% | 63% | 796 | Stellar |
| VesperVale | 1 | 0.00 | 42 | 2 | 0% | 0% | 100% | 100% | 0 | Cassi |
| Willow | 13 | 1.00 | 100 | 3 | 77% | 0% | 38% | 77% | 84 | Prism |

Per map / result / tier (all deaths incl. pair): deaths per game, gems lost per game

| split | games | deaths | per game | gems lost | per game | zone own/mid/enemy | before: farming / tributing / recalling / fighting / walking / fleeing |
|---|---|---|---|---|---|---|---|
| map collision | 19 | 161 | 8.5 | 3882 | 204 | 61/83/17 | 2 / 13 / 17 / 2 / 3 / 15 |
| map corners | 17 | 121 | 7.1 | 1536 | 90 | 46/45/30 | 4 / 5 / 8 / 12 / 2 / 9 |
| map elkring | 14 | 113 | 8.1 | 1062 | 76 | 47/27/39 | 10 / 4 / 7 / 5 / 10 / 11 |
| map expanse | 17 | 1 | 0.1 | 0 | 0 | 0/0/1 | 0 / 0 / 0 / 1 / 0 / 0 |
| map interlock | 13 | 42 | 3.2 | 918 | 71 | 21/8/13 | 0 / 9 / 4 / 3 / 2 / 7 |
| map lanes | 18 | 26 | 1.4 | 208 | 12 | 10/3/13 | 1 / 1 / 0 / 2 / 0 / 4 |
| map monolith | 13 | 32 | 2.5 | 528 | 41 | 12/7/13 | 1 / 3 / 3 / 0 / 1 / 4 |
| map packs | 21 | 79 | 3.8 | 406 | 19 | 26/23/30 | 8 / 0 / 4 / 4 / 1 / 11 |
| map rows | 18 | 6 | 0.3 | 0 | 0 | 2/0/4 | 0 / 0 / 0 / 0 / 0 / 2 |
| res win | 59 | 353 | 6.0 | 6238 | 106 | 150/132/71 | 7 / 26 / 23 / 12 / 10 / 41 |
| res loss | 91 | 228 | 2.5 | 2302 | 25 | 75/64/89 | 19 / 9 / 20 / 17 / 9 / 22 |
| tier top10 | 50 | 151 | 3.0 | 1890 | 38 | 52/55/44 | 12 / 7 / 14 / 10 / 7 / 18 |
| tier 11-20 | 50 | 204 | 4.1 | 3472 | 69 | 83/66/55 | 8 / 15 / 22 / 7 / 7 / 26 |
| tier 21-30 | 45 | 213 | 4.7 | 2810 | 62 | 83/69/61 | 6 / 12 / 7 / 11 / 4 / 19 |
| tier other | 5 | 13 | 2.6 | 368 | 74 | 7/6/0 | 0 / 1 / 0 / 1 / 1 / 0 |

Deaths per game distribution: 0: 52 games, 1: 15 games, 2: 10 games, 3: 19 games, 4: 4 games, 5: 10 games, 6: 7 games, 7: 7 games, 8: 1 games, 9: 4 games, 10: 2 games, 11: 4 games, 12: 4 games, 14: 4 games, 15: 1 games, 16: 1 games, 17: 2 games, 18: 2 games, 19: 1 games

Examples: 79bed885 collision Vendetta r362 approaching hp100% ep 9 rounds 2 foes spells 86% allies6 1 gems 44 killer Ren; 79bed885 collision Cassi r306 approaching hp100% ep 5 rounds 2 foes spells 100% allies6 1 gems 22 killer Cassi; 79bed885 collision Issac r519 idle hp59% ep 3 rounds 2 foes spells 63% allies6 0 gems 44 killer Ren; 79bed885 collision Stellar r200 approaching hp100% ep 7 rounds 3 foes spells 96% allies6 0 gems 44 killer Issac; 2f4101a4 corners Varg r113 idle hp58% ep 5 rounds 3 foes spells 82% allies6 0 gems 48 killer Stellar; 2f4101a4 corners Ryth r102 fighting hp67% ep 11 rounds 2 foes spells 41% allies6 1 gems 0 killer Ren RECALLING; 2f4101a4 corners Ryth r102 fighting hp67% ep 11 rounds 2 foes spells 41% allies6 1 gems 0 killer Ren RECALLING; 7ba9fe5c packs Ren r243 recalling hp6% ep 1 rounds 1 foes spells 100% allies6 0 gems 0 killer Cassi RECALLING; ca10ce5a elkring Marcella r533 recalling hp4% ep 1 rounds 1 foes spells 100% allies6 1 gems 0 killer Stellar RECALLING; cce8926b collision Ren r562 recalling hp27% ep 1 rounds 1 foes spells 100% allies6 0 gems 108 killer Cassi RECALLING; 73c3155e interlock Vendetta r391 tributing hp76% ep 10 rounds 1 foes spells 72% allies6 0 gems 72 killer Ren; cce8926b collision Varg r542 tributing hp76% ep 9 rounds 2 foes spells 39% allies6 2 gems 0 killer Cassi; 3a260573 interlock Ren r176 tributing hp63% ep 8 rounds 1 foes spells 0% allies6 3 gems 0 killer Issac

### How the opponents die (what we did): our damage sources in their final episodes

Damage share by our champion type: Stellar 36%, Ren 18%, Cassi 9%, Tavi 9%, Ryth 8%, Prism 6%, Issac 6%, camp 4%, Varg 2%, Vendetta 2%
Killing blow by our type: Stellar 164, Ren 71, Cassi 37, Issac 36, Ryth 35, Tavi 33, Prism 27, camp 22, self 12, Vendetta 11, Varg 9

Our deaths: damage share by enemy type: Stellar 32%, Tavi 13%, Ren 11%, Cassi 8%, Issac 7%, Ryth 7%, Varg 7%, Vendetta 6%, camp 4%, Prism 3%, Marcella 1%, Willow 1%, VesperVale 0%

## Q6. The 10 worst games by gems lost to our deaths

| # | match | map | opponent (rank) | result | score us-opp | our deaths | gems lost | opp deaths / gems lost | biggest losses (type r round gems) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | feb23cc4 | interlock | test (17) | win | 1016-812 | 9 | 376 | 5 / 260 | Cassi r81 72g, Cassi r465 72g, Stellar r337 72g, Tavi r438 72g |
| 2 | f2cb3e65 | corners | ひななー (21) | loss | 978-1010 | 23 | 372 | 12 / 92 | Stellar r307 48g, Stellar r665 48g, Prism r354 48g, Prism r657 48g |
| 3 | 15195780 | collision | BottleBots (27) | win | 1002-800 | 10 | 328 | 10 / 450 | Stellar r314 174g, Issac r301 44g, Cassi r301 22g (pair), Cassi r536 22g (pair) |
| 4 | ae2470ab | collision | Full Damage (11) | loss | 850-1004 | 13 | 300 | 4 / 248 | Cassi r805 146g, Issac r469 44g, Ren r439 44g, Stellar r829 44g |
| 5 | c2825ed0 | elkring | geese geese go (13) | loss | 396-1008 | 12 | 288 | 10 / 36 | Ryth r228 36g, Ryth r417 36g, Stellar r65 36g, Prism r90 36g |
| 6 | 69757c8e | collision | Shawn (3) | win | 1012-616 | 21 | 286 | 14 / 374 | Stellar r748 110g, Issac r749 44g, Cassi r866 22g (pair), Issac r462 22g (pair) |
| 7 | 83a66318 | interlock | lETHal (16) | loss | 298-1064 | 13 | 276 | 1 / 0 | Cassi r52 72g, Stellar r237 72g, Stellar r427 44g, Cassi r423 22g |
| 8 | 59ac9626 | interlock | Boost (15) | loss | 524-1030 | 8 | 276 | 0 / 0 | Cassi r298 72g, Issac r193 72g, Issac r441 44g (pair), Cassi r193 22g (pair) |
| 9 | ad957980 | elkring | ひななー (21) | loss | 468-1008 | 15 | 252 | 6 / 36 | Ryth r626 36g, Stellar r231 36g, Stellar r497 36g, Prism r269 36g |
| 10 | cabfadde | interlock | VeryGood (5) | loss | 596-1060 | 5 | 232 | 0 / 0 | Cassi r403 72g, Issac r258 72g, Issac r403 44g (pair), Cassi r258 22g (pair) |

### What decided each of the ten games (reading the round-by-round tables below)

1. **feb23cc4 interlock vs test (#17), won 1016-812, 376 gems lost.** Cassi r75 starts an 8-tick tribute of 72 gems at (18,17) with three enemies within 6 (Stellar at 6, Prism, Tavi). Prism pokes at r76 (87%), Stellar at r79 (59%), and at r81 Stellar+Tavi+Prism spells kill her at tick 7 of the channel, 1 tile from the altar; Issac had walked from 1 to 6 tiles away during the channel instead of standing in front of her. Never cancelled, never moved. The second 72-gem loss (Cassi r465) is a different pattern: four rounds of `nothing` at (20,27) with Ren at 4 tiles and no ally within 6, then Stellar's spell (340) from range, one step away, one step back *closer*, a last-ditch attack at 9% and death.
2. **f2cb3e65 corners vs ひななー (#21), lost 978-1010, 372 gems lost (23 deaths).** Stellar r296-299 is already at 46% carrying 48 gems, wandering (away, away, closer, away) with Tavi and Prism adjacent and 3-4 enemies within 8; it never recalls (foe at 4-6). Ren's spell at r300 (29%), two rounds of fighting back at 24% and 11%, then four "away" steps at 1 tile per round with Ren adjacent the whole way (Ren follows every step) — dies at r307 with 48 gems, the two allies 2-3 tiles behind doing nothing to stop Ren. Stellar r665: stands at (34,31) and trades basic attacks with Tavi (range 2) and Willow for 7 rounds from 97% to 28% without ever stepping back, then eats Tavi's 180 spell.
3. **15195780 collision vs BottleBots (#27), won 1002-800, 328 gems lost.** Stellar r306-314 walks toward Vendetta/Varg with Ren next to it, is hit for 288 by Vendetta at r310 (84% -> 58%), fights back twice at 39% and 20% with the melee adjacent, dies at r314 carrying 174 gems (152 of them picked up at r313 from a kill). Issac r292-301 dashes into Vendetta+Varg at 93% with Ren at 1; the first Varg hits take him to 76%, he stays adjacent for 4 rounds (one of them a failed attack), 13% after a 400-damage round, dead the next round. Both deaths at 10-17 tiles from our spawn.
4. **ae2470ab collision vs Full Damage (#11), lost 850-1004, 300 gems lost.** Cassi r788 starts a 15-tick tribute of 146 gems at (26,21); Prism walks in from 8 to 4 tiles over r793-797 (Issac wanders off from 1 to 6 tiles), hits her for 544 at r797 and 362 at r798 (14%), then finishes her with basic attacks over 7 more rounds. The tribute was restarted at r799 (!) at 14% hp with Prism at 4: 146 gems lost in a single death. Issac r466 is a one-spell death: a 700-damage Stellar cast at 100% hp with nobody within 6, three steps away, dead.
5. **c2825ed0 elkring vs geese geese go (#13), lost 396-1008, 288 gems lost.** Ryth r216-220 walks alone (no ally within 6) toward a group of 3-4 enemies with 36 gems at 69%, gets Ren spell + Varg attacks (45%), stands still one round (33%), then alternates attack+step for 6 rounds while Varg and Ren stay adjacent — dies at r228 to retaliation damage at the map edge (20,0). Ryth r405-417 repeats it: at 94% it steps toward Tavi/Ren with Stellar and Prism next to it, takes Tavi 316 + Stellar 126 (68%), keeps walking laterally/closer for 4 rounds while the allies leave, 41% after Varg's double hit, one step away, dead to Tavi+Stellar spells.
6. **69757c8e collision vs Shawn (#3), won 1012-616, 286 gems lost.** Stellar r740-748 holds 110 gems and chooses to fight Issac approaching from 5 tiles instead of recalling (nobody within 6); Issac reaches melee at r744 (72%), Stellar retreats one tile per round with Issac adjacent (61, 50, 39%) and the enemy Stellar's 316 spell ends it at r748. One round later our Issac, dashing in at 100% to help, takes 406 + 459 from the enemy Stellar and dies at r749 (44 gems).
7. **83a66318 interlock vs lETHal (#16), lost 298-1064, 276 gems lost.** Cassi r44-52: at 47% with 72 gems and four enemies within 8 it starts a recall at r46 with the enemy Cassi at 5 tiles; hit at r48 (27%), then `nothing`, a lateral step, `nothing`, one step away, dead at r52 — no second recall attempt, no run toward Issac/Tavi who are 3-6 tiles away. Stellar r237: walks closer to the enemy Stellar at 100% with 72 gems and nobody within 6, casts once, takes 444 then 306 and dies in 2 rounds.
8. **59ac9626 interlock vs Boost (#15), lost 524-1030, 276 gems lost.** Issac r177-193 farms a camp at (11,18) with Tavi/Stellar beside him while the enemy Tavi walks in from 9 to 3 tiles; after Tavi's 242 spell he stands still for **five rounds** (r182-186, `nothing`) taking 60 per round from range 3 (73% -> 39%), dashes away at r187, starts a recall at r188 with Tavi still at 3 (interrupted at once by a 242 spell, 6%), a second recall at r191 at distance 5, killed at r193 at tick 3. Four allies passed within 6 tiles during the episode; one of them attacked anyone. Cassi r298: same shape, 91% at (16,22), Issac 1 tile away, pokes from Prism, a few steps, then a 605 Stellar spell kills her from 86%.
9. **ad957980 elkring vs ひななー (#21), lost 468-1008, 252 gems lost.** Ryth r621-626 at 11% with 36 gems, two enemies at 4-5: step away, cast a spell (!), step away, recall at r624 with Stellar at 5 — Prism's spell at r625 interrupts and kills. Stellar r218-231: walks toward the enemy Ren alone, trades basic attacks with Ren *adjacent* for 7 rounds from 75% to 27% without moving (a ranged champion that attacks cannot move, so it chose to stand), and dies to Ren's second spell.
10. **cabfadde interlock vs VeryGood (#5), lost 596-1060, 232 gems lost.** Issac r246-258 farms (11,17) with Ren at 2 while Stellar closes from 6 to 4; after the 210 spell he stands still for five rounds (r251-255) taking 38 per round, dashes *laterally*, steps *closer* to the enemy Stellar at 55% and dies to a 497 spell with 72 gems just captured. Cassi r396-403 idles three rounds while Stellar walks from 7 to 4, steps closer, loses 338 + 248 in two rounds, starts a recall at 7% with Stellar at 2 (interrupted immediately), steps closer again, dead.

Common thread of the ten: none of the deciding deaths was a 1-round burst from full hp with no warning. In every case the enemy was visible for 3-5 rounds before the first hit (dfoe 4-8 in the tables), the victim either walked toward it, stood still, or continued a channel, and the first retreat step came after losing 40-60% hp. An ally passed within 6 tiles during the final episode in 12 of the 20 deaths; in only 6 of those did any ally attack an enemy champion during the episode. Over all 709 direct deaths: 178 with no ally within 6 during the episode, 325 with an ally within 6 that never attacked an enemy, 206 with an ally that did (opponents: 150 / 187 / 120).

### Round-by-round tables of the two biggest gem losses in each of the ten games

### 1. feb23cc4 interlock vs test (win 1016-812): 376 gems lost

**Cassi (idx 0) dies r81 with 72 gems, killer Prism; doing before: walking; first hit at r76 with hp 100%; zone own, 16 from own spawn, 1 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 72 | 15,19 | 100 | 72 | lateral (move) |  | Stellar 6 | 2 | Issac@2 Stellar@2 Tavi@4 |  |
| 73 | 16,18 | 100 | 72 | closer (move) |  | Prism 6 | 3 | Issac@1 Stellar@3 Tavi@3 |  |
| 74 | 17,18 | 100 | 72 | closer (move) |  | Stellar 6 | 3 | Issac@1 Stellar@2 Tavi@4 |  |
| 75 | 18,17 | 100 | 72 | lateral (move,tribute) |  | Stellar 6 | 3 | Issac@1 Tavi@4 | TRIBUTE START |
| 76 | 18,17 | 87 | 72 | tribute  | 84 Prism/sp | Tavi 5 | 3 | Issac@1 Tavi@4 | tribute(r75) |
| 77 | 18,17 | 87 | 72 | tribute  |  | Tavi 4 | 3 | Issac@3 Tavi@4 | tribute(r75) |
| 78 | 18,17 | 87 | 72 | tribute  |  | Tavi 4 | 3 | Tavi@3 Issac@4 | tribute(r75) |
| 79 | 18,17 | 59 | 72 | tribute  | 200 Stellar/sp | Stellar 4 | 3 | Tavi@4 Issac@5 | tribute(r75) |
| 80 | 18,17 | 59 | 72 | tribute  |  | Stellar 4 | 3 | Tavi@5 Issac@6 | tribute(r75) |
| 81 | 18,17 | 0 | 72 | DEAD  | 140 Stellar/sp, 220 Tavi/sp, 55 Prism/sp | Tavi 4 | 3 | Tavi@4 Issac@6 | tribute(r75) |

**Cassi (idx 0) dies r465 with 72 gems, killer Stellar; doing before: idle; first hit at r460 with hp 91%; zone enemy, 22 from own spawn, 2 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 456 | 20,27 | 91 | 0 | nothing (abil) |  | Ren 4 | 3 |  |  |
| 457 | 20,27 | 91 | 0 | nothing  |  | Ren 4 | 3 |  |  |
| 458 | 20,27 | 91 | 0 | nothing  |  | Ren 4 | 3 |  |  |
| 459 | 20,27 | 91 | 0 | nothing  |  | Ren 4 | 3 |  |  |
| 460 | 21,26 | 47 | 0 | closer (move) | 340 Stellar/sp | Ren 5 | 3 |  |  |
| 461 | 20,27 | 16 | 0 | away (move) | 238 Stellar/sp | Ren 4 | 3 |  |  |
| 462 | 19,26 | 16 | 0 | closer (move) |  | Ren 5 | 3 |  |  |
| 463 | 19,26 | 9 | 0 | fight (atk,spell) | 35 Stellar/atk | Stellar 3 | 3 |  |  |
| 464 | 20,25 | 0 | 72 | closer (abil,move) | 35 Tavi/atk, 35 Tavi/atk | Stellar 3 | 2 |  |  |
| 465 | 20,25 | 0 | 72 | DEAD (move) | 0 Stellar/atk | Stellar 2 | 2 |  |  |

### 2. f2cb3e65 corners vs ひななー (loss 978-1010): 372 gems lost

**Stellar (idx 1) dies r307 with 48 gems, killer Ren; doing before: fleeing; first hit at r300 with hp 46%; zone own, 13 from own spawn, 6 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 296 | 32,32 | 46 | 48 | away (move) |  | Tavi 5 | 4 | Prism@1 Tavi@1 |  |
| 297 | 31,31 | 46 | 48 | away (move) |  | Willow 6 | 4 | Tavi@1 Prism@2 |  |
| 298 | 32,32 | 46 | 48 | closer (move) |  | Tavi 6 | 3 | Tavi@1 Prism@2 |  |
| 299 | 33,33 | 46 | 48 | away (move) |  | Tavi 4 | 3 | Tavi@1 Prism@2 |  |
| 300 | 33,33 | 29 | 48 | nothing  | 125 Ren/sp | Ren 3 | 4 | Tavi@1 Prism@3 |  |
| 301 | 33,33 | 24 | 48 | fight (atk,spell) |  | Ren 3 | 4 | Tavi@2 Prism@3 |  |
| 302 | 33,33 | 11 | 48 | fight (atk,spell) | 48 Willow/atk, 48 Willow/atk | Ren 2 | 4 | Tavi@2 Prism@4 |  |
| 303 | 32,32 | 11 | 48 | away (move) |  | Ren 2 | 5 | Tavi@3 Prism@5 |  |
| 304 | 31,31 | 5 | 48 | away (move) | 40 Ren/atk | Ren 2 | 5 | Prism@3 Tavi@3 |  |
| 305 | 30,30 | 5 | 48 | away (move) |  | Ren 2 | 4 | Prism@2 Tavi@3 |  |
| 306 | 29,29 | 0 | 48 | away (move) | 40 Ren/atk | Ren 2 | 4 | Prism@1 Tavi@3 |  |
| 307 | 29,29 | 0 | 48 | DEAD (move) | 4 Ren/atk | Ren 2 | 2 | Prism@2 Tavi@3 |  |

**Stellar (idx 1) dies r665 with 48 gems, killer Tavi; doing before: walking; first hit at r658 with hp 97%; zone middle, 18 from own spawn, 3 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 654 | 33,30 | 97 | 0 | lateral (move) |  | Ryth 2 | 3 | Prism@2 Ryth@5 |  |
| 655 | 33,30 | 97 | 0 | fight (atk,spell) |  | Willow 3 | 3 | Prism@1 Ryth@5 |  |
| 656 | 33,30 | 97 | 0 | fight (spell) |  | Willow 3 | 3 | Prism@1 Ryth@6 |  |
| 657 | 34,31 | 97 | 0 | closer (move) |  | Willow 3 | 3 | Prism@2 |  |
| 658 | 34,31 | 88 | 0 | fight (atk) | 35 Tavi/atk, 35 Tavi/atk | Tavi 2 | 3 |  |  |
| 659 | 34,31 | 84 | 0 | fight (atk) | 35 Tavi/atk | Tavi 2 | 3 |  |  |
| 660 | 34,31 | 73 | 0 | fight (atk) | 54 Willow/atk, 35 Tavi/atk | Tavi 2 | 3 |  |  |
| 661 | 34,31 | 63 | 0 | fight (atk) | 54 Willow/atk, 35 Tavi/atk | Tavi 2 | 3 |  |  |
| 662 | 34,31 | 52 | 0 | fight (atk) | 54 Willow/atk, 35 Tavi/atk | Tavi 2 | 3 |  |  |
| 663 | 34,31 | 41 | 0 | fight (atk,spell) | 54 Willow/atk, 35 Tavi/atk | Tavi 2 | 3 |  |  |
| 664 | 34,31 | 28 | 48 | fight (atk,spell) | 54 Willow/atk, 54 Willow/atk | Tavi 2 | 3 |  |  |
| 665 | 34,31 | 0 | 48 | DEAD (move) | 54 Willow/atk, 180 Tavi/sp | Willow 3 | 3 |  |  |

### 3. 15195780 collision vs BottleBots (win 1002-800): 328 gems lost

**Stellar (idx 3) dies r314 with 174 gems, killer Vendetta; doing before: approaching; first hit at r310 with hp 84%; zone own, 10 from own spawn, 12 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 306 | 18,12 | 84 | 22 | closer (move) |  | Vendetta 6 | 2 | Ren@5 |  |
| 307 | 19,11 | 84 | 22 | closer (move) |  | Vendetta 5 | 2 | Ren@3 |  |
| 308 | 18,10 | 84 | 22 | away (move) |  | Varg 3 | 2 | Ren@2 |  |
| 309 | 17,9 | 84 | 22 | away (move) |  | Varg 3 | 2 | Ren@1 |  |
| 310 | 17,9 | 58 | 22 | fight (atk,spell) | 144 Vendetta/atk, 144 Vendetta/atk | Vendetta 2 | 2 |  |  |
| 311 | 17,9 | 39 | 22 | fight (atk) | 144 Vendetta/atk, 72 Varg/atk | Vendetta 1 | 2 |  |  |
| 312 | 16,8 | 20 | 22 | away (move) | 72 Varg/atk, 144 Vendetta/atk | Vendetta 1 | 2 |  |  |
| 313 | 16,8 | 0 | 22 | fight (atk,spell) | 144 Vendetta/atk, 72 Varg/atk | Vendetta 2 | 2 |  |  |
| 314 | 16,8 | 0 | 174 | DEAD (buy) | 9 Vendetta/atk | Vendetta 1 | 1 |  |  |

**Issac (idx 1) dies r301 with 44 gems, killer Vendetta; doing before: approaching; first hit at r296 with hp 94%; zone middle, 17 from own spawn, 4 from altar; allies within 6 at death: 1.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 292 | 22,15 | 93 | 44 | closer (move) |  | Vendetta 7 | 1 | Cassi@3 Ren@3 |  |
| 293 | 23,15 | 93 | 44 | lateral (move) |  | Vendetta 6 | 2 | Ren@1 Cassi@5 |  |
| 294 | 23,18 | 93 | 44 | closer (dash,move) |  | Vendetta 6 | 2 | Ren@2 |  |
| 295 | 24,19 | 93 | 44 | closer (move) |  | Vendetta 3 | 2 | Ren@1 |  |
| 296 | 23,18 | 76 | 44 | fight+away (abil,atk,move) | 80 Varg/atk, 80 Varg/atk | Vendetta 2 | 2 | Ren@1 |  |
| 297 | 24,19 | 76 | 44 | fight+closer (atk,move) |  | Varg 2 | 2 | Ren@1 |  |
| 298 | 24,19 | 67 | 44 | nothing (atkother) | 80 Varg/atk | Varg 1 | 2 | Ren@1 |  |
| 299 | 24,19 | 58 | 44 | fight (atk) | 80 Varg/atk | Varg 1 | 2 | Ren@1 |  |
| 300 | 23,18 | 13 | 44 | fight+away (atk,move) | 80 Varg/atk, 160 Vendetta/atk, 160 Vendetta/atk | Varg 1 | 2 | Ren@1 |  |
| 301 | 23,18 | 0 | 44 | DEAD  | 124 Vendetta/atk | Vendetta 2 | 2 | Ren@3 |  |

### 4. ae2470ab collision vs Full Damage (loss 850-1004): 300 gems lost

**Cassi (idx 0) dies r805 with 146 gems, killer Prism; doing before: tributing; first hit at r797 with hp 100%; zone middle, 20 from own spawn, 1 from altar; allies within 6 at death: 1.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 793 | 26,21 | 100 | 146 | tribute  |  | Prism 8 | 1 | Issac@1 | tribute(r788) |
| 794 | 26,21 | 100 | 146 | tribute  |  | Prism 7 | 1 | Issac@1 | tribute(r788) |
| 795 | 26,21 | 100 | 146 | tribute  |  | Prism 6 | 1 | Issac@1 | tribute(r788) |
| 796 | 26,21 | 100 | 146 | tribute  |  | Prism 5 | 1 | Issac@4 | tribute(r788) |
| 797 | 26,21 | 48 | 146 | tribute  | 544 Prism/sp | Prism 4 | 1 | Issac@5 | tribute(r788) |
| 798 | 26,21 | 14 | 146 | tribute  | 362 Prism/sp | Prism 4 | 1 | Issac@6 | tribute(r788) |
| 799 | 26,21 | 14 | 146 | tribute (abil,tribute) |  | Prism 4 | 1 |  | TRIBUTE START |
| 800 | 26,21 | 14 | 146 | tribute  |  | Prism 4 | 1 |  | tribute(r788) |
| 801 | 26,21 | 11 | 146 | tribute  | 31 Prism/atk | Prism 3 | 1 |  | tribute(r788) |
| 802 | 26,21 | 8 | 146 | tribute  | 31 Prism/atk | Prism 3 | 1 |  | tribute(r788) |
| 803 | 26,21 | 5 | 146 | tribute  | 31 Prism/atk | Prism 3 | 1 |  | tribute(r788) |
| 804 | 26,21 | 2 | 146 | tribute  | 31 Prism/atk | Prism 3 | 1 |  | tribute(r788) |
| 805 | 26,21 | 0 | 146 | DEAD  | 23 Prism/sp | Prism 3 | 1 | Ren@6 | tribute(r788) |

**Issac (idx 1) dies r469 with 44 gems, killer Stellar; doing before: approaching; first hit at r466 with hp 100%; zone own, 15 from own spawn, 6 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 462 | 22,14 | 100 | 44 | lateral (move) |  | Stellar 6 | 1 |  |  |
| 463 | 22,15 | 100 | 44 | closer (move) |  | Stellar 5 | 1 |  |  |
| 464 | 21,14 | 100 | 44 | away (move) |  | Stellar 5 | 1 |  |  |
| 465 | 24,17 | 100 | 44 | closer (dash,move) |  | Stellar 5 | 1 |  |  |
| 466 | 23,16 | 18 | 44 | away (move) | 700 Stellar/sp, 35 Stellar/atk | Stellar 3 | 1 |  |  |
| 467 | 22,15 | 18 | 44 | away (move) |  | Stellar 4 | 1 |  |  |
| 468 | 21,14 | 18 | 44 | away (move) |  | Stellar 4 | 1 |  |  |
| 469 | 21,14 | 0 | 44 | DEAD  | 165 Stellar/sp | Stellar 4 | 1 |  |  |

### 5. c2825ed0 elkring vs geese geese go (loss 396-1008): 288 gems lost

**Ryth (idx 0) dies r228 with 36 gems, killer self; doing before: approaching; first hit at r220 with hp 70%; zone own, 16 from own spawn, 7 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 216 | 20,7 | 69 | 36 | lateral (move) |  | Ren 4 | 4 |  |  |
| 217 | 21,7 | 69 | 36 | closer (move) |  | Varg 5 | 4 |  |  |
| 218 | 22,6 | 69 | 36 | closer (move) |  | Varg 4 | 4 |  |  |
| 219 | 23,5 | 69 | 36 | closer (move) |  | Varg 3 | 3 |  |  |
| 220 | 24,4 | 45 | 36 | closer (move) | 258 Ren/sp, 36 Ren/atk, 72 Varg/atk | Varg 2 | 3 |  |  |
| 221 | 24,4 | 33 | 36 | nothing  | 36 Ren/atk, 72 Varg/atk, 71 Varg/atk | Varg 1 | 3 |  |  |
| 222 | 23,3 | 26 | 36 | fight+away (abil,atk,atkother,move) | 36 Ren/atk, 72 Varg/atk | Varg 1 | 3 |  |  |
| 223 | 23,3 | 23 | 36 | fight (atk,spell) |  | Varg 1 | 3 |  |  |
| 224 | 22,2 | 16 | 36 | fight+away (atk,move) | 36 Ren/atk, 71 Varg/atk | Varg 1 | 3 |  |  |
| 225 | 21,1 | 9 | 36 | fight+away (atk,move) | 36 Ren/atk, 72 Varg/atk | Varg 1 | 3 |  |  |
| 226 | 20,0 | 6 | 36 | fight+away (atk,move) | 36 Ren/atk | Varg 1 | 3 |  |  |
| 227 | 19,0 | 1 | 36 | fight+away (atk,move) | 36 Ren/atk | Ren 1 | 3 |  |  |
| 228 | 19,0 | 0 | 36 | DEAD (atk) |  | Ren 1 | 3 |  |  |

**Ryth (idx 0) dies r417 with 36 gems, killer Varg; doing before: approaching; first hit at r409 with hp 94%; zone own, 14 from own spawn, 9 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 405 | 14,10 | 100 | 36 | closer (move) |  | Ren 6 | 2 | Stellar@1 Prism@2 Tavi@6 |  |
| 406 | 14,10 | 94 | 36 | fight (spell) |  | Ren 4 | 2 | Stellar@1 Prism@2 Tavi@6 |  |
| 407 | 14,10 | 94 | 36 | nothing  |  | Ren 4 | 3 | Prism@1 Stellar@1 Tavi@6 |  |
| 408 | 15,11 | 94 | 36 | closer (move) |  | Tavi 5 | 4 | Prism@1 Stellar@1 Tavi@6 |  |
| 409 | 16,11 | 75 | 36 | lateral (move) | 316 Tavi/sp | Tavi 4 | 4 | Prism@1 Stellar@1 |  |
| 410 | 16,11 | 68 | 36 | nothing  | 126 Stellar/sp | Tavi 4 | 4 | Prism@1 Stellar@2 |  |
| 411 | 17,11 | 68 | 36 | lateral (move) |  | Tavi 4 | 4 | Prism@1 |  |
| 412 | 18,11 | 68 | 36 | lateral (move) |  | Ren 3 | 4 | Prism@1 |  |
| 413 | 19,10 | 66 | 36 | closer (move) | 31 Tavi/atk | Stellar 3 | 4 |  |  |
| 414 | 19,10 | 56 | 36 | fight (spell) | 31 Tavi/atk, 31 Stellar/atk | Varg 3 | 4 |  |  |
| 415 | 18,9 | 41 | 36 | closer (move) | 130 Varg/atk, 130 Varg/atk | Varg 2 | 4 |  |  |
| 416 | 17,8 | 31 | 36 | away (move) | 31 Stellar/atk, 130 Varg/atk | Varg 1 | 4 |  |  |
| 417 | 17,8 | 0 | 36 | DEAD (abil,atk,atkother,move) | 316 Tavi/sp, 180 Stellar/sp, 41 Varg/atk | Varg 1 | 4 |  |  |

### 6. 69757c8e collision vs Shawn (win 1012-616): 286 gems lost

**Stellar (idx 3) dies r748 with 110 gems, killer Stellar; doing before: fighting; first hit at r744 with hp 95%; zone own, 9 from own spawn, 12 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 740 | 18,11 | 95 | 110 | away (move) |  | Issac 5 | 2 |  |  |
| 741 | 18,11 | 95 | 110 | fight (spell) |  | Issac 5 | 2 |  |  |
| 742 | 18,11 | 95 | 110 | fight (atk,spell) |  | Issac 4 | 3 |  |  |
| 743 | 18,11 | 95 | 110 | fight (atk) |  | Issac 3 | 3 |  |  |
| 744 | 18,11 | 72 | 110 | fight (atk) | 125 Issac/atk, 125 Issac/atk | Issac 2 | 3 |  |  |
| 745 | 17,10 | 61 | 110 | away (move) | 125 Issac/atk | Issac 1 | 3 |  |  |
| 746 | 16,9 | 50 | 110 | away (move) | 125 Issac/atk | Issac 2 | 3 | Issac@5 |  |
| 747 | 15,8 | 39 | 110 | away (move) | 125 Issac/atk | Issac 2 | 3 | Issac@3 Cassi@5 |  |
| 748 | 15,8 | 0 | 110 | DEAD (buy) | 125 Issac/atk, 316 Stellar/sp | Issac 2 | 3 | Cassi@3 Issac@3 |  |

**Issac (idx 1) dies r749 with 44 gems, killer Stellar; doing before: approaching; first hit at r748 with hp 100%; zone own, 11 from own spawn, 10 from altar; allies within 6 at death: 1.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 744 | 11,9 | 100 | 0 | closer (move) |  | Issac 10 | 0 | Cassi@2 |  |
| 745 | 12,10 | 100 | 0 | closer (move) |  | Issac 8 | 1 | Cassi@2 |  |
| 746 | 13,11 | 100 | 0 | closer (move) |  | Issac 7 | 1 | Cassi@2 Stellar@5 |  |
| 747 | 16,11 | 100 | 0 | closer (dash,move) |  | Issac 5 | 2 | Cassi@2 Stellar@3 |  |
| 748 | 17,10 | 51 | 0 | fight+closer (abil,atk,move) | 406 Stellar/sp, 35 Stellar/atk | Issac 1 | 3 | Stellar@3 Cassi@4 |  |
| 749 | 17,10 | 0 | 44 | DEAD (move) | 459 Stellar/sp | Stellar 3 | 1 | Cassi@4 |  |

### 7. 83a66318 interlock vs lETHal (loss 298-1064): 276 gems lost

**Cassi (idx 0) dies r52 with 72 gems, killer Tavi; doing before: fighting; first hit at r48 with hp 47%; zone own, 11 from own spawn, 12 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 44 | 9,17 | 47 | 72 | fight (atk) |  | Prism 3 | 4 | Issac@3 Tavi@3 Stellar@6 |  |
| 45 | 8,16 | 47 | 72 | away (move) |  | Cassi 3 | 4 | Issac@3 Tavi@3 Stellar@5 |  |
| 46 | 8,16 | 47 | 72 | recall (recall) |  | Cassi 5 | 4 | Tavi@3 Issac@4 Stellar@6 | RECALL START |
| 47 | 8,16 | 47 | 72 | recall  |  | Cassi 4 | 4 | Tavi@4 Issac@5 | recall(r46) |
| 48 | 8,16 | 27 | 72 | nothing  | 140 Cassi/sp | Cassi 4 | 5 | Tavi@4 Issac@5 |  |
| 49 | 8,15 | 27 | 72 | lateral (move) |  | Cassi 4 | 4 | Tavi@3 Issac@5 |  |
| 50 | 8,15 | 15 | 72 | nothing  | 80 Prism/sp | Cassi 4 | 4 | Tavi@4 Issac@6 |  |
| 51 | 7,14 | 15 | 72 | away (abil,move) |  | Cassi 3 | 4 | Tavi@3 Issac@6 |  |
| 52 | 7,14 | 0 | 72 | DEAD (spell) | 110 Tavi/sp | Tavi 4 | 4 | Tavi@3 Issac@6 |  |

**Stellar (idx 3) dies r237 with 72 gems, killer Stellar; doing before: approaching; first hit at r236 with hp 100%; zone own, 15 from own spawn, 3 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 232 | 15,20 | 100 | 72 | lateral (move) |  | Cassi 5 | 1 |  |  |
| 233 | 15,19 | 100 | 72 | lateral (move) |  | Stellar 8 | 2 |  |  |
| 234 | 16,18 | 100 | 72 | closer (move) |  | Stellar 7 | 2 |  |  |
| 235 | 16,18 | 100 | 72 | fight (spell) |  | Stellar 5 | 2 |  |  |
| 236 | 16,18 | 40 | 72 | nothing  | 220 Tavi/sp, 224 Stellar/sp | Stellar 4 | 3 |  |  |
| 237 | 16,18 | 0 | 72 | DEAD  | 306 Stellar/sp | Stellar 4 | 3 |  |  |

### 8. 59ac9626 interlock vs Boost (loss 524-1030): 276 gems lost

**Cassi (idx 0) dies r298 with 72 gems, killer Stellar; doing before: idle; first hit at r293 with hp 91%; zone own, 17 from own spawn, 5 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 289 | 16,21 | 91 | 72 | nothing (abil) |  | Ren 4 | 3 | Issac@3 Tavi@5 |  |
| 290 | 17,21 | 91 | 72 | closer (move) |  | Ren 4 | 3 | Issac@2 Tavi@6 |  |
| 291 | 17,21 | 91 | 72 | nothing  |  | Ren 4 | 3 | Issac@1 |  |
| 292 | 17,21 | 91 | 72 | nothing  |  | Prism 4 | 3 | Issac@1 |  |
| 293 | 16,22 | 86 | 72 | lateral (move) | 35 Prism/atk | Prism 3 | 3 | Issac@1 |  |
| 294 | 16,22 | 86 | 72 | fight (atk) |  | Prism 3 | 3 | Issac@4 |  |
| 295 | 15,21 | 86 | 72 | away (move) |  | Prism 4 | 3 | Issac@4 |  |
| 296 | 15,21 | 86 | 72 | nothing  |  | Stellar 5 | 3 | Issac@3 Tavi@5 |  |
| 297 | 14,20 | 86 | 72 | away (abil,move) |  | Stellar 4 | 3 | Issac@3 Tavi@4 |  |
| 298 | 14,20 | 0 | 72 | DEAD (move) | 605 Stellar/sp | Stellar 5 | 2 | Issac@2 Tavi@3 |  |

**Issac (idx 1) dies r193 with 72 gems, killer Tavi; doing before: farming; first hit at r181 with hp 100%; zone own, 13 from own spawn, 4 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 177 | 10,17 | 100 | 0 | camp (atkcamp) |  | Tavi 9 | 0 | Tavi@1 Stellar@2 |  |
| 178 | 10,17 | 100 | 0 | camp (atkcamp) |  | Tavi 8 | 1 | Tavi@1 Stellar@2 |  |
| 179 | 11,18 | 100 | 0 | closer (atkcamp,move) |  | Tavi 7 | 1 | Stellar@2 Tavi@2 |  |
| 180 | 11,18 | 100 | 0 | camp (abil,atkcamp) |  | Tavi 5 | 1 | Stellar@2 Tavi@3 Ren@5 |  |
| 181 | 11,18 | 73 | 0 | camp (atkcamp) | 242 Tavi/sp | Tavi 4 | 1 | Stellar@2 Tavi@3 Ren@4 |  |
| 182 | 11,18 | 73 | 0 | nothing  |  | Tavi 4 | 1 | Stellar@2 Ren@3 Tavi@3 |  |
| 183 | 11,18 | 59 | 0 | nothing  | 60 Tavi/atk, 60 Tavi/atk | Tavi 3 | 1 | Stellar@3 Tavi@3 Ren@4 |  |
| 184 | 11,18 | 53 | 0 | nothing  | 60 Tavi/atk | Tavi 3 | 1 | Tavi@3 Stellar@4 Ren@5 |  |
| 185 | 11,18 | 46 | 0 | nothing  | 60 Tavi/atk | Tavi 3 | 1 | Tavi@3 Stellar@4 Ren@6 |  |
| 186 | 11,18 | 39 | 0 | nothing  | 60 Tavi/atk | Tavi 3 | 1 | Tavi@3 Stellar@4 Ren@5 |  |
| 187 | 14,17 | 39 | 0 | away (dash,move) |  | Tavi 3 | 1 | Tavi@3 Ren@4 Stellar@4 |  |
| 188 | 14,17 | 33 | 72 | recall (recall) | 60 Tavi/atk | Tavi 3 | 3 | Ren@5 Tavi@6 | RECALL START |
| 189 | 15,16 | 6 | 72 | away (move) | 242 Tavi/sp | Tavi 3 | 2 | Ren@5 Tavi@6 |  |
| 190 | 15,16 | 6 | 72 | nothing  |  | Tavi 4 | 2 | Ren@5 Cassi@6 |  |
| 191 | 15,16 | 6 | 72 | recall (recall) |  | Tavi 5 | 2 | Ren@5 Cassi@6 | RECALL START |
| 192 | 15,16 | 6 | 72 | recall  |  | Tavi 4 | 3 | Cassi@5 Ren@5 | recall(r191) |
| 193 | 15,16 | 0 | 72 | DEAD  | 56 Tavi/atk | Tavi 3 | 2 | Cassi@4 Ren@4 |  |

### 9. ad957980 elkring vs ひななー (loss 468-1008): 252 gems lost

**Ryth (idx 0) dies r626 with 36 gems, killer Prism; doing before: fleeing; first hit at r625 with hp 11%; zone own, 10 from own spawn, 13 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 621 | 0,14 | 11 | 36 | away (move) |  | Stellar 4 | 2 |  |  |
| 622 | 0,14 | 11 | 36 | fight (spell) |  | Stellar 4 | 2 |  |  |
| 623 | 0,13 | 11 | 36 | away (move) |  | Stellar 4 | 2 |  |  |
| 624 | 0,13 | 11 | 36 | recall (recall) |  | Stellar 5 | 2 |  | RECALL START |
| 625 | 0,13 | 0 | 36 | nothing  | 189 Prism/sp | Prism 4 | 2 |  |  |
| 626 | 0,13 | 0 | 36 | DEAD  | 2 Prism/sp | Prism 4 | 2 |  |  |

**Stellar (idx 1) dies r231 with 36 gems, killer Ren; doing before: approaching; first hit at r222 with hp 97%; zone middle, 15 from own spawn, 8 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 218 | 16,11 | 100 | 36 | closer (move) |  | Ren 7 | 1 | Ren@4 |  |
| 219 | 17,11 | 100 | 36 | closer (move) |  | Ren 6 | 1 | Ren@4 |  |
| 220 | 18,11 | 100 | 36 | lateral (move) |  | Ren 4 | 1 | Ren@4 |  |
| 221 | 18,11 | 96 | 36 | fight (spell) |  | Ren 5 | 1 | Ren@4 |  |
| 222 | 18,11 | 75 | 36 | nothing  | 236 Ren/sp | Ren 4 | 1 | Ren@4 |  |
| 223 | 18,11 | 68 | 36 | fight (atk,spell) |  | Ren 4 | 1 | Ren@5 |  |
| 224 | 18,11 | 65 | 36 | fight (atk) |  | Ren 3 | 1 | Ren@6 |  |
| 225 | 18,11 | 58 | 36 | fight (atk) | 40 Ren/atk | Ren 2 | 1 |  |  |
| 226 | 18,11 | 51 | 36 | fight (atk) | 40 Ren/atk | Ren 1 | 1 |  |  |
| 227 | 18,11 | 44 | 36 | fight (atk) | 40 Ren/atk | Ren 1 | 1 |  |  |
| 228 | 18,11 | 37 | 36 | fight (atk) | 40 Ren/atk | Ren 1 | 1 |  |  |
| 229 | 18,11 | 27 | 36 | fight (atk,spell) | 40 Ren/atk | Ren 1 | 1 |  |  |
| 230 | 18,11 | 2 | 36 | nothing  | 236 Ren/sp, 40 Ren/atk | Ren 1 | 1 |  |  |
| 231 | 18,11 | 0 | 36 | DEAD  | 31 Ren/atk | Ren 1 | 1 |  |  |

### 10. cabfadde interlock vs VeryGood (loss 596-1060): 232 gems lost

**Cassi (idx 0) dies r403 with 72 gems, killer Stellar; doing before: idle; first hit at r400 with hp 91%; zone own, 16 from own spawn, 6 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 396 | 10,18 | 91 | 0 | nothing  |  | Stellar 7 | 1 |  |  |
| 397 | 10,18 | 91 | 0 | nothing  |  | Stellar 6 | 1 |  |  |
| 398 | 10,18 | 91 | 0 | nothing  |  | Stellar 5 | 1 |  |  |
| 399 | 11,19 | 91 | 0 | closer (move) |  | Stellar 4 | 1 |  |  |
| 400 | 12,20 | 43 | 72 | closer (move) | 38 Stellar/atk, 300 Stellar/sp | Stellar 3 | 1 |  |  |
| 401 | 12,20 | 7 | 72 | recall (recall) | 38 Stellar/atk, 210 Stellar/sp | Stellar 2 | 1 |  | RECALL START |
| 402 | 13,19 | 2 | 72 | closer (move) | 38 Stellar/atk | Stellar 2 | 1 |  |  |
| 403 | 13,19 | 0 | 72 | DEAD (recall) | 14 Stellar/atk | Stellar 1 | 1 |  | RECALL START |

**Issac (idx 1) dies r258 with 72 gems, killer Stellar; doing before: farming; first hit at r250 with hp 100%; zone own, 15 from own spawn, 4 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 246 | 11,17 | 100 | 0 | camp (atkcamp) |  | Stellar 6 | 1 | Ren@2 Cassi@5 Tavi@6 |  |
| 247 | 11,17 | 100 | 0 | camp (atkcamp) |  | Stellar 5 | 1 | Ren@2 Cassi@4 Tavi@6 |  |
| 248 | 11,17 | 100 | 0 | camp (atkcamp) |  | Stellar 5 | 1 | Ren@2 Cassi@3 Tavi@6 |  |
| 249 | 11,17 | 100 | 0 | camp (atkcamp) |  | Stellar 4 | 1 | Ren@2 Cassi@3 Tavi@6 |  |
| 250 | 11,18 | 76 | 0 | lateral (move) | 210 Stellar/sp | Stellar 4 | 1 | Ren@2 Cassi@4 Tavi@6 |  |
| 251 | 11,18 | 76 | 0 | nothing  |  | Stellar 4 | 1 | Ren@1 Cassi@5 |  |
| 252 | 11,18 | 72 | 0 | nothing  | 38 Stellar/atk | Stellar 3 | 1 | Ren@2 Cassi@4 |  |
| 253 | 11,18 | 68 | 0 | nothing  | 38 Stellar/atk | Stellar 3 | 1 | Ren@3 Cassi@4 Stellar@6 |  |
| 254 | 11,18 | 63 | 0 | nothing  | 38 Stellar/atk | Stellar 3 | 1 | Cassi@3 Ren@4 Stellar@5 |  |
| 255 | 11,18 | 59 | 0 | nothing  | 38 Stellar/atk | Stellar 3 | 1 | Cassi@4 Stellar@4 Ren@5 |  |
| 256 | 14,17 | 55 | 0 | lateral (dash,move) | 38 Stellar/atk | Stellar 3 | 1 | Cassi@3 Stellar@3 Ren@6 |  |
| 257 | 15,18 | 55 | 72 | closer (move) |  | Stellar 3 | 2 | Cassi@1 Stellar@1 Tavi@6 |  |
| 258 | 15,18 | 0 | 72 | DEAD  | 497 Stellar/sp | Stellar 2 | 2 | Cassi@1 Stellar@2 |  |


## Observed rules of our bot when attacked (what a reader infers from the 150 games)

1. **There is no "I am being hit" reflex.** The action mix in the hit round (32% fight, 28% move, 20% nothing, 5% channel) is the same as the opponents' and the first retreat step comes a median 2 rounds after the first hit for both teams (us 62% of episodes retreat, opponents 58%). What differs is what happens before and after: we are hit at median 90% hp and still die in 25% of episodes (717/2866) vs 13.7% for the opponents.
2. **Melee walk in, casters stand and trade.** On the first hit Issac/Ryth/Varg/Vendetta step *closer* in 30-51% of cases (opponents' melee 35-38%, so similar), while Stellar/Prism fight back (34%/31%) and Tavi does nothing 43% of the time. Standing still while hit happens in 20% of all hit rounds; 689 of 3954 melee hit rounds (17%) are a melee standing still with the attacker 2+ tiles away (out of reach, not approaching, not leaving). 5-round idle streaks under fire exist (59ac9626 r182-186, cabfadde r251-255).
3. **Retreat threshold is ~50% hp, and the retreat is a 1-tile-per-round walk with the enemy adjacent.** Median hp at the retreat step 54%; the enemy follows in 76% of retreats and we outrun it in only 46% (opponents 60%). Retreats below 40% hp die 40% of the time (opponents 17%), casters' retreats 35%.
4. **Retreat alone.** 31% of retreat steps have no ally within 6, and in 45% the allies stay where they are; the group moves back together in 14%. We run toward spawn in 53% of retreats (opponents 63%), toward an ally in 29%.
5. **Recall is a teleport-home used from far away, not an escape.** 71% of the 3860 attempts start with no enemy within 9 tiles (99% arrive); only 15% follow a hit in the previous 3 rounds, and those arrive 67% of the time. hp at start is bimodal (30-40% heals, 80-90% repositions); there is no hp threshold (full-hp starts with no gems and no gold for every type). An interrupted recall is retried in 32% of cases and turned into a fight in 50%; Mite retries 59%.
6. **Channels are never cancelled.** 0 voluntary cancels of recalls (1 move-cancel in 3860 attempts); tributes continue with enemies walking into range 4 (17 deaths during a tribute channel, 724 gems; feb23cc4 r81, ae2470ab r805 where the tribute was even restarted at 14% hp).
7. **Allies help by shooting, not by moving, and only if they were not busy.** 29% of allies within 8 attack an enemy within 5 rounds, 20% move toward the victim; an ally that was hitting a camp keeps hitting it 46% of the time; a recalling ally never comes (7%). In 325 of our 709 direct deaths an ally was within 6 during the final episode and attacked nobody.
8. **We die at home, from full hp, to spells, over 4-8 rounds.** 73% of deaths in our own half, median 14 tiles from spawn; hp at the first hit median 90%; Stellar deals the killing blow in 30% of deaths and spells 68% of the episode damage; the final episode lasts a median 5 rounds, i.e. there were 4+ rounds in which a retreat or a recall at distance >= 6 was possible. 38% of victims were walking toward the enemy before the first hit.
9. **The 3-champion draft (cassi/ren/stellar) and corners are the worst.** 257 deaths in 57 three-champion games (4.5/game) vs 411 in 62 five-champion games (6.6/game, but 2 more champions); corners 13.5 deaths/game (230 in 17 games, 72% recall arrival), collision 7.9, elkring 6.5; expanse 0 and rows 0.1 (no fights there).

## Biggest differences from the opponents (pooled top-30) and from Mite

| behaviour | us | opponents (150 games) | Mite (reference) |
|---|---|---|---|
| deaths per game / gems lost per game / share of tributed | 5.72 / 57 / 7.1% | 3.87 / 57 / 6.3% | 4.9 / 52.5 / 5.7% (Univardisty 6.1 / 109 / 12.6%) |
| hit episodes ending in death | 25% (717/2866) | 13.7% (474/3450) | - |
| hp at first hit of the fatal episode (median) | 90% (501/709 >= 70%) | 72% (234/457 >= 70%) | 68% at r-5 (107/265 bursted) |
| deaths in own half / enemy half | 73% / 3% | 30% / 33% | median 15 tiles from spawn |
| victim walking toward the enemy before the fatal episode | 38% (270/709) | 45% (207/457) | - |
| retreat step hp (median) / retreats that die | 54% / 26% | 49% / 13% | 38% under fire / 16% |
| outrun the follower after 5 rounds (>= +3 tiles) | 46% | 60% | - |
| retreat toward own spawn | 53% | 63% | "walk away toward spawn" |
| retreat ends in a completed recall | 37% | 47% | 65-74% (hp < 50%) |
| recall attempts per game / arrival | 25.7 / 91% | 24-34 (spam merged) / 62-88% | 25 / 90% |
| recall started with a foe within 5 | 16% (49-66% arrive) | 14% | dfoe 7-8 in 35%, 1-5 rare |
| recall hp threshold | none (bimodal 30-40 / 80-90) | Tavi/Willow/Vendetta bots < 50% | strict heal < 50% |
| retry after an interrupted recall | 32% | 82% (incl. spam) | 59% |
| voluntary recall cancel | 0% | 2-3% | 0% (Univardisty 68 cancels) |
| ally within 8 helps (fights or comes) within 5 rounds | 49% | 49% | - |
| ally that was farming keeps farming | 46% | 40% | - |
| deaths with an ally within 6 that never attacked | 325/709 (46%) | 187/457 (41%) | - |
| deaths while a recall was in progress | 107 (15%) | 96 (21%) | 41 (15%) attempted in last 10 r |
| deaths during a tribute channel | 17 (724 gems) | 17 (930 gems) | - |
| killing blow by spell / top killer | 52% / Stellar 30% | 65% / our Stellar 36% | 62% / Stellar 34% |

The two numbers that explain the death gap: we take the first hit at 90% hp and still lose the champion in a quarter of the episodes, because the retreat starts 2 rounds later at ~50% hp, walks one tile per round with the attacker adjacent (outrun in 46%), goes to spawn only half the time and ends in a recall only 37% of the time; the opponents start their fatal episodes already damaged (median 72%), retreat toward spawn (63%), outrun (60%) and recall (47%). Against Mite the gap is in the recall discipline: Mite recalls at hp < 50% as soon as the nearest enemy is 7 tiles away and retries after every interruption (59%); we recall from 14 tiles away when nothing is around (71% of attempts) and, when hit at 4-5 tiles, we fight (50%) instead of retrying (32%).
