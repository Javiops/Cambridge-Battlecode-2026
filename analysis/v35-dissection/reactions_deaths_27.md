# Reactions and deaths — study27 (stacking on big camps) vs study26 (v35)

Data: 155 unranked games of 2026-10-15 12:31-12:38 UTC against the top-30 with **study27** = study26 + `P_STACK_HP 3000` / `P_SHAREEXP 75` (a champion joining a camp group of 3000+ monster hp values it at gems / team^0.75 instead of an even split, so up to 4 champions stack there; smaller camps keep the even split). Result 58-97 (37.4%); study26 was 59-91 (39.3%) in 150 games at 11:33 UTC. Same game mix: 150 games as team 0 and 5 as team 1, drafts cassi/ren/stellar 41, vendetta/varg/cassi/ryth/tavi 33, ryth/stellar/prism/ren/tavi 28, cassi/ren/stellar/tavi 19, vendetta/varg/cassi/ryth 17, vendetta/varg/cassi 17; opponents top10 50 / 11-20 50 / 21-30 50 / other 5; maps collision 19, corners 19, elkring 9, expanse 17, interlock 19, lanes 17, monolith 16, packs 22, rows 17 (study26: elkring 14, interlock 13, monolith 13, corners 17, rows 18).

Files: replays decoded to `$S/ws3/steps/<match>.c.jsonl`, games `$S/ws3/selected.json`. The study26 scripts in `$S/ws2/scripts_reactions/` now take the data directory from `WS` and the rows file name from `ROWS` (`WS=$S/ws3 ROWS=rows_27.json python3 -I extract.py` -> `rows_27.json`; `stack.py` -> `stack_27.json` / `stack_26.json` for the stacking context; `compare27.py` prints sections 1-6 below from the two rows files; `permap_stack.py` the per-map stacking table; `report3.py` the worst-games tables; `extra.py` the tribute-channel deaths). Definitions (hit round, episode, action classes, retreat step, recall attempt, help pair, direct vs pair death) are those of `$S/ws2/reports/reactions_deaths.md`. In every table the three columns are **study27 us / study26 us / the opponents in the study27 games**; `z` is the two-proportion z-score of study27 us against study26 us, printed when |z| >= 1.8 and bold when >= 2.5 — with 700-900 deaths and 3000 episodes per study, a difference of 3-4 points in a death-related share is inside the noise, and only the flagged rows are called out below.

## Summary

1. **Nothing in the reaction machinery moved.** Action mix in the hit round (23/6/4% fight variants, 15% away, 13% closer, 21% nothing, 8% dead) and one round later is identical to study26 within 1 point; episodes ending in death 24% (756/3164) vs 25% (717/2866), opponents 14%; retreat step in 61% of episodes with a median delay of 2 rounds (same); retreat outcomes death 24% / recall 39% / escape 26% / still fighting 11% (study26 26/37/27/10); recall attempts 25.6 per game, 92% arrive, 7% interrupted, 36% retry (same); help rate 49% (same), an ally that was farming keeps farming 46% (same). The only reaction-side rows that clear the noise: retreats with **no ally within 6 fell from 31% to 27%** (521/1938 vs 545/1775, z=-2.6) and the whole group retreats together in 16% vs 14% (z=2.0); recalls started with a foe within 5 arrive 70% vs 64% (497/708 vs 406/636, z=2.5), and recalls started within 3 rounds of a hit arrive 72% vs 67% (z=2.1). These are consistent with champions being slightly closer together, not with a new behaviour.
2. **Deaths: 5.80 per game (899) vs 5.72 (858); direct deaths 4.72 vs 4.73 per game.** Gems lost 63.5 per game vs 57.2 (7.9% vs 7.1% of what we tribute; the study27 opponents lose 68 per game, 7.6%). The extra 6 gems per game are not more deaths but **bigger bags on the same deaths**: deaths carrying >= 60 gems 34 (2928 gems) vs 21 (1726), >= 100 gems 6 (854) vs 3 (430); deaths during a tribute channel 23 (1436 gems) vs 17 (724). Four of the five biggest single losses of the batch are a Stellar or Ren killed at tick 4-13 of a tribute at the centre altar of collision with 66-216 gems (section 7). Deaths within 2 tiles of an altar: 13% vs 9% (93/731 vs 62/709, z=2.4; corners 45, collision 23). Everything else about how we die is unchanged: 70% in our own half (73%), median 15 tiles from spawn, hp at the first hit of the fatal episode median 91% (90%), 1-round deaths 14% (12%), approaching the enemy before the episode 42% (38%, z=1.4), no retreat move in the episode 52% (50%), no ally within 6 at death 34% (36%), outnumbered at the first hit 42% (39%), recall in progress 14% (15%). Killer: Stellar 35% (30%), spell share of the episode damage median 74% (68%), killing blow by spell 56% (52%); Ryth and Vendetta kill us less (29+27 vs 55+42) — the opponent pool, not us.
3. **Per type and map:** Tavi's episode death rate 26% vs 32% (103/391 vs 99/310, z=-1.8) and Prism 33% vs 39% are the only type-level moves; Cassi 0.88 direct deaths per game drafted (0.74), Stellar 2.10 (1.95) with 3030 gems lost (2120). Per map: collision 12.6 deaths / 169 gems per game (11.3 / 126), corners 12.4 / 81 (13.5 / 112), interlock 5.3 / 134 (4.3 / 114, 19 vs 13 games), monolith 2.8 / 26 (3.8 / 48); expanse and rows 0 deaths in both. Opponent tier 11-20 cost 6.6 deaths per game (5.5), top10 5.9 (6.3).
4. **Stacking changed where we stand, not how we die.** By the engine's camp groups the 3000+ rule bites only on rows (six 3-wolf groups, 4050 hp) and corners (four elk pairs, 4800 hp, barely farmed): on rows the share of our champion-rounds spent with 3+ of ours on one group went from 12.5% to 21.8% and with 4+ from 0% to 11.8% (3924 champion-rounds at stack 4 on a big group vs 0), while rows has 0.1 deaths per game in both studies. On every other map the stack-3+ share is unchanged (collision 8.3% vs 8.7%, elkring 8.7 vs 8.0, interlock 6.4 vs 5.9, packs 4.8 vs 5.1). Accordingly: deaths with 3-4 of ours on the same camp group 23 vs 23 (3% of direct deaths, 1.39 vs 1.36 deaths per 1000 champion-rounds in that state; none on a big group in either study), deaths next to a living camp monster 17% vs 20% (124 vs 145; awake monster 10% vs 13%, z=-1.9), hit by a camp in the previous 5 rounds 13% vs 16% (92 vs 110), killed by a camp 22 vs 25, allies within 6 at death 0/1/2+ = 34/38/28% vs 36/36/28%. Among the 23 stacked deaths, 12 (study26: 7) had taken camp damage in the previous 5 rounds and 13 (15) had 3+ enemies within 8: a 3-stack that gets jumped while the camp is still biting — same count, same shape. Hit episodes starting while stacked 3+ are rarer per champion-round (9.6 per 1000) than solo (13.7) or in pairs (13.6) in both studies; the opponents are hit as often stacked as not (15.6).
5. **Gems lost by stack size at death** is the one stacking-adjacent number that moved: deaths at stack 1 (alone on a camp group) cost 2460 gems (159 deaths) vs 1400 (165 deaths), all of it on collision (1578 vs 878 gems in 75 vs 80 deaths): the centre altar of collision (26,19)-(27,21) is within 3 of a wolf camp, so a tributing Stellar counts as "stack 1 next to a living wolf", and six of those deaths carried 66-216 gems. It is the tribute-at-the-centre-altar pattern of study26's worst games (ae2470ab, feb23cc4) with larger bags, not a stacking effect.

# Tables (study27 us / study26 us / study27 opponents)

## 1. Hit reactions

Unit = hit round (champion took damage from an enemy champion). Flag: z = two-proportion z-score study27 us vs study26 us; bold when |z| >= 2.5.

### action at t+0 (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| study27 us | 8396 | 23% | 6% | 4% | 15% | 13% | 4% | 1% | 0% | 3% | 21% | 8% |
| study26 us | 7606 | 22% | 6% (z=-2.1) | 4% | 15% | 13% | 5% (z=-2.1) | 2% | 0% | 3% (z=2.7) | 20% | 9% |
| study27 opp | 8696 | 20% | 5% | 7% | 13% | 19% | 4% | 1% | 0% | 4% | 22% | 5% |

### action at t+1 (all hit rounds)

| rows | n | fight | fight+away | fight+closer | away | closer | lateral | camp | recall | tribute | nothing | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| study27 us | 8396 | 21% | 6% | 3% | 24% | 5% | 4% | 1% | 2% | 2% | 19% | 14% |
| study26 us | 7606 | 21% | 7% | 3% | 23% | 4% | 5% | 1% (z=-2.1) | 2% | 2% (z=2.7) | 19% | 15% (z=-2.1) |
| study27 opp | 8696 | 19% | 5% | 5% | 24% | 10% | 4% | 1% | 1% | 3% | 20% | 8% |

### action at t+1 by hp band before the hit (fight / away / nothing / dead)

| | study27 us | study26 us | study27 opp |
|---|---|---|---|
| hp >70 | n=3896: 34% / 19% / 28% / 2% | n=3426: 34% / 19% / 29% / 3% | n=4203: 30% / 17% / 27% / 1% |
| hp 40-70 | n=2593: 35% / 29% / 15% / 6% | n=2430: 35% / 28% / 15% / 8% | n=3057: 31% / 31% / 17% / 4% |
| hp <40 | n=1907: 14% / 27% / 5% / 47% | n=1750: 15% / 26% / 3% / 48% | n=1436: 17% / 30% / 8% / 38% |

### hit episodes: death rate, retreat step, group retreat

| | study27 us | study26 us | study27 opp |
|---|---|---|---|
| episodes ending in death (within episode + 6 rounds) | 24% (756/3164) | 25% (717/2866) | 14% (522/3737) |
|   died, first hit at hp >70 | 21% (517/2489) | 22% (496/2257) | 9% (241/2683) |
|   died, first hit at hp 40-70 | 27% (141/519) | 30% (147/491) | 18% (148/845) |
|   died, first hit at hp <40 | 63% (98/156) | 63% (74/118) | 64% (133/209) |
|   died, melee | 17% (282/1613) | 18% (276/1501) | 13% (274/2146) |
|   died, caster | 31% (474/1551) | 32% (441/1365) | 15% (229/1497) |
| episodes with a retreat step | 61% (1938/3164) | 62% (1775/2866) | 59% (2188/3737) |
| retreat delay (rounds after first hit), median | 2.0 (n=1938) | 2 (n=1775) | 2.0 (n=2188) |
| retreat step with no ally within 6 | 27% (521/1938) **(z=-2.6)** | 31% (545/1775) | 28% (612/2188) |
| retreat step, allies stay | 45% (867/1938) | 45% (790/1775) | 43% (947/2188) |
| retreat step, all allies also retreat | 16% (318/1938) (z=2.0) | 14% (250/1775) | 13% (280/2188) |
| first hit with 2+ allies within 8 | 50% (1596/3164) (z=1.8) | 48% (1379/2866) | 56% (2106/3737) |
| first hit with 0 allies within 8 | 17% (547/3164) (z=-1.8) | 19% (548/2866) | 17% (626/3737) |
| episodes hit by 2+ enemy champions | 30% (953/3164) | 29% (818/2866) | 30% (1116/3737) |

### death rate per hit episode by champion type (us)

| type | study27 | study26 | study27 opp |
|---|---|---|---|
| Cassi | 28% (112/393) | 30% (98/327) | 17% (64/385) |
| Issac | 20% (81/400) | 22% (78/352) | 14% (93/643) |
| Marcella | - | - | 38% (8/21) |
| Prism | 33% (67/203) | 39% (76/197) | 11% (15/132) |
| Ren | 16% (113/717) | 16% (108/674) | 12% (73/617) |
| Ryth | 20% (66/323) | 21% (65/308) | 11% (33/302) |
| Stellar | 34% (192/564) | 32% (168/531) | 15% (94/620) |
| Tavi | 26% (103/391) | 32% (99/310) | 16% (56/360) |
| Varg | 10% (9/89) | 12% (9/73) | 10% (39/394) |
| Vendetta | 15% (13/84) | 17% (16/94) | 17% (28/169) |
| VesperVale | - | - | 30% (3/10) |
| Willow | - | - | 19% (16/84) |

## 2. Retreat outcomes

Unit = retreat step (see study26 report for the definition). Outcome within 15 rounds.

| | study27 us | study26 us | study27 opp |
|---|---|---|---|
| retreat steps per game | 12.50 (1938/155) | 11.83 (1775/150) | 14.12 (2188/155) |
| hp% at the retreat step, median | 53.0 (n=1938) | 54 (n=1775) | 50.0 (n=2188) |
| nearest foe distance at the step, median | 3.0 (n=1938) | 3 (n=1775) | 3.0 (n=2188) |
| foe follows (>= 1 closing step) | 76% (1470/1938) | 76% (1352/1775) | 72% (1570/2188) |
| outrun after 5 rounds (distance +3 or more) | 47% (913/1938) | 46% (817/1775) | 63% (1368/2188) |
| caught (no distance gained after 5 rounds) | 8% (158/1938) | 9% (164/1775) | 7% (160/2188) |
| toward own spawn (dspawn -2 or more after 5 rounds) | 56% (1078/1938) (z=1.8) | 53% (935/1775) | 65% (1415/2188) |
| toward an ally (-2 or more) | 26% (502/1938) | 29% (506/1775) | 27% (597/2188) |
| outcome: death | 24% (464/1938) | 26% (466/1775) | 12% (269/2188) |
| outcome: recall | 39% (764/1938) | 37% (656/1775) | 49% (1070/2188) |
| outcome: escape | 14% (271/1938) | 14% (254/1775) | 14% (313/2188) |
| outcome: escape_near | 12% (227/1938) | 13% (222/1775) | 11% (245/2188) |
| outcome: still_fighting | 11% (212/1938) | 10% (177/1775) | 13% (291/2188) |
|   death, retreat started below 40% hp | 36% (233/646) | 40% (228/573) | 17% (123/742) |
|   death, retreat started above 70% hp | 14% (78/556) (z=-2.2) | 19% (106/559) | 7% (36/504) |
|   death, melee | 19% (211/1109) | 20% (209/1043) | 12% (172/1401) |
|   death, caster | 31% (253/829) (z=-1.9) | 35% (257/732) | 13% (93/741) |
| recall started within 15 rounds of the step | 54% (1042/1938) | 52% (922/1775) | 64% (1398/2188) |

## 3. Recalls

Unit = recall attempt (spam restarts merged).

| | study27 us | study26 us | study27 opp |
|---|---|---|---|
| attempts per game | 25.55 (3961/155) | 25.73 (3860/150) | 33.70 (5223/155) |
| outcome: arrived | 92% (3647/3961) | 91% (3528/3860) | 63% (3282/5223) |
| outcome: hit_foe | 5% (186/3961) | 5% (192/3860) | 10% (517/5223) |
| outcome: hit_camp | 0% (10/3961) | 0% (9/3860) | 21% (1100/5223) |
| outcome: died | 2% (96/3961) | 2% (93/3860) | 2% (90/5223) |
| outcome: moved | 0% (2/3961) | 0% (0/3860) | 3% (173/5223) |
| outcome: attacked | 0% (1/3961) | 0% (1/3860) | 0% (5/5223) |
| interrupted (hit_foe + hit_camp + died) | 7% (292/3961) | 8% (294/3860) | 33% (1707/5223) |
| hp% at start, median | 51 (n=3961) | 51.0 (n=3860) | 57 (n=5223) |
| started with hp < 50 | 49% (1928/3961) | 48% (1834/3860) | 44% (2300/5223) |
| started with gems > 0 | 18% (694/3961) | 16% (634/3860) | 27% (1395/5223) |
| nearest foe at start, median | 13 (n=3961) | 14.0 (n=3860) | 13 (n=5223) |
| started with a foe within 5 | 18% (708/3961) | 16% (636/3860) | 13% (690/5223) |
|   of those, arrived | 70% (497/708) (z=2.5) | 64% (406/636) | 32% (219/690) |
| started within 3 rounds of being hit by a foe | 17% (661/3961) (z=2.3) | 15% (571/3860) | 13% (694/5223) |
|   of those, arrived | 72% (478/661) (z=2.1) | 67% (381/571) | 54% (374/694) |
| retry after an interruption/cancel (of interrupted attempts) | 36% (72/199) | 32% (65/202) | 84% (1500/1795) |
| died within 10 rounds of an interruption | 18% (36/199) | 15% (30/202) | 2% (43/1795) |
| fought within 10 rounds of an interruption | 44% (87/199) | 50% (102/202) | 9% (161/1795) |

Recall starts per game by map (us; starts / arrival / interrupted):

| map | study27 (games) | study26 (games) |
|---|---|---|
| collision | 32.4 / 90% / 58 (19) | 32.8 / 91% / 53 (19) |
| corners | 24.7 / 81% / 89 (19) | 24.8 / 72% / 117 (17) |
| elkring | 49.7 / 94% / 23 (9) | 45.9 / 94% / 33 (14) |
| expanse | 14.8 / 100% / 0 (17) | 15.1 / 99% / 0 (17) |
| interlock | 29.4 / 91% / 44 (19) | 30.2 / 89% / 37 (13) |
| lanes | 11.7 / 97% / 3 (17) | 11.4 / 97% / 3 (18) |
| monolith | 33.8 / 97% / 11 (16) | 31.5 / 98% / 3 (13) |
| packs | 25.0 / 88% / 64 (22) | 24.2 / 90% / 48 (21) |
| rows | 19.4 / 99% / 0 (17) | 22.2 / 99% / 0 (18) |

## 4. Help

Unit = (first hit of an episode, ally alive within 8). Help = ally fought or came within 5 rounds.

| | study27 us | study26 us | study27 opp |
|---|---|---|---|
| victim-ally pairs per game | 32.35 (5014/155) | 28.84 (4326/150) | 43.49 (6741/155) |
| ally fought | 29% (1465/5014) | 29% (1265/4326) | 30% (2041/6741) |
| ally came | 20% (979/5014) | 20% (852/4326) | 19% (1253/6741) |
| ally kept_farming | 12% (583/5014) | 12% (504/4326) | 6% (423/6741) |
| ally moved_away | 16% (785/5014) | 15% (654/4326) | 15% (999/6741) |
| ally other | 24% (1202/5014) | 24% (1051/4326) | 30% (2025/6741) |
| help (fought+came) | 49% (2444/5014) | 49% (2117/4326) | 49% (3294/6741) |
|   ally was farming a camp: kept farming | 46% (344/745) | 46% (289/631) | 38% (207/548) |
|   ally was farming a camp: helped | 37% (279/745) | 36% (230/631) | 40% (219/548) |
|   ally within 3: helped | 47% (959/2057) | 47% (859/1822) | 45% (1545/3428) |
|   victim died: helped | 35% (358/1013) | 32% (302/946) | 24% (187/773) |
|   victim survived: helped | 52% (2086/4001) | 54% (1815/3380) | 52% (3107/5968) |
| share of first hits with an ally within 8 (of episodes) | 83% (2617/3164) (z=1.8) | 81% (2318/2866) | 83% (3111/3737) |

## 5. Deaths

| | study27 us | study26 us | study27 opp |
|---|---|---|---|
| deaths per game (incl. pair deaths) | 5.80 (899/155) | 5.72 (858/150) | 4.04 (626/155) |
| direct deaths per game | 4.72 (731/155) | 4.73 (709/150) | 3.21 (497/155) |
| gems lost to deaths per game | 63.55 (9850/155) | 57.24 (8586/150) | 68.08 (10552/155) |
| gems lost as share of gems tributed | 7.9% (9850 / 124045) | 7.1% (8586 / 121260) | 7.6% (10552 / 139292) |
| deaths carrying gems | 28% (248/899) | 26% (227/858) | 35% (216/626) |
| bag when > 0, median | 36.0 (n=248) | 36 (n=227) | 44.0 (n=216) |
| zone: own half (direct deaths) | 70% (511/731) | 73% (521/709) | 32% (160/497) |
| zone: enemy half | 3% (20/731) | 3% (22/709) | 29% (146/497) |
| distance to own spawn, median | 15 (n=731) | 14 (n=709) | 19 (n=497) |
| within 2 of an altar | 13% (93/731) (z=2.4) | 9% (62/709) | 25% (122/497) |
| doing before the final episode: approaching | 42% (305/731) | 38% (270/709) | 38% (188/497) |
| doing before the final episode: fleeing | 18% (128/731) | 20% (141/709) | 13% (64/497) |
| doing before the final episode: idle | 12% (85/731) | 12% (82/709) | 8% (39/497) |
| doing before the final episode: farming | 9% (65/731) | 9% (64/709) | 5% (27/497) |
| doing before the final episode: fighting | 6% (42/731) | 8% (56/709) | 8% (38/497) |
| doing before the final episode: recalling | 6% (47/731) | 5% (34/709) | 11% (57/497) |
| doing before the final episode: tributing | 2% (18/731) | 3% (24/709) | 11% (54/497) |
| doing before the final episode: walking | 6% (41/731) | 5% (38/709) | 6% (30/497) |
| hp% at the first hit of the final episode, median | 91 (n=731) | 90 (n=709) | 63 (n=497) |
|   hp >= 70 at first hit | 70% (513/731) | 71% (501/709) | 46% (231/497) |
|   hp < 40 at first hit | 13% (93/731) | 10% (71/709) | 26% (131/497) |
| 1-round deaths (burst) | 14% (100/731) | 12% (82/709) | 29% (144/497) |
| final episode length (rounds), median | 5 (n=731) | 5 (n=709) | 3 (n=497) |
| enemy champions dealing damage: 1 | 39% (282/731) | 41% (289/709) | 48% (241/497) |
| enemy champions dealing damage: 3+ | 23% (168/731) | 21% (146/709) | 17% (84/497) |
| spell share of episode damage, median | 74 (n=731) | 68 (n=709) | 88 (n=497) |
| killing blow by spell | 56% (408/731) | 52% (367/709) | 68% (336/497) |
| killing blow by camp | 3% (22/731) | 4% (25/709) | 3% (15/497) |
| camp damage > 50% of the episode | 2% (15/731) | 3% (20/709) | 2% (10/497) |
| allies within 6 at death: 0 | 34% (248/731) | 36% (258/709) | 35% (173/497) |
| allies within 6 at death: 2+ | 28% (202/731) | 28% (195/709) | 30% (149/497) |
| allies within 8 at the first hit: 2+ | 41% (302/731) | 40% (286/709) | 45% (222/497) |
| outnumbered at the first hit (foes8 > allies8+1) | 42% (304/731) | 39% (276/709) | 33% (164/497) |
| recall in progress at death | 14% (105/731) | 15% (107/709) | 17% (84/497) |
| recall attempted in the episode | 13% (94/731) | 16% (111/709) | 9% (46/497) |
| no retreat move in the episode | 52% (381/731) | 50% (351/709) | 71% (353/497) |
| fought back >= 1 round | 60% (441/731) | 61% (431/709) | 40% (200/497) |

### killer type (direct deaths)

| killer | study27 us | study26 us | study27 opp |
|---|---|---|---|
| Stellar | 258 (35%) | 211 (30%) | 165 (33%) |
| Ren | 87 (12%) | 75 (11%) | 91 (18%) |
| Tavi | 76 (10%) | 80 (11%) | 63 (13%) |
| Cassi | 60 (8%) | 54 (8%) | 34 (7%) |
| Issac | 58 (8%) | 52 (7%) | 34 (7%) |
| Varg | 57 (8%) | 54 (8%) | 7 (1%) |
| Ryth | 29 (4%) | 55 (8%) | 32 (6%) |
| Vendetta | 27 (4%) | 42 (6%) | 10 (2%) |
| Prism | 25 (3%) | 25 (4%) | 24 (5%) |
| camp | 22 (3%) | 25 (4%) | 15 (3%) |
| self | 16 (2%) | 21 (3%) | 22 (4%) |
| Marcella | 7 (1%) | 6 (1%) | 0 (0%) |

### deaths per champion type (direct deaths; per game in which the type was drafted)

| type | study27: deaths / games drafted / per game / gems lost | study26 | study27 opp |
|---|---|---|---|
| Cassi | 112 / 127 / 0.88 / 1510 | 88 / 119 / 0.74 / 1446 | 56 / 133 / 0.42 / 1112 |
| Issac | 72 / 127 / 0.57 / 1740 | 79 / 119 / 0.66 / 1632 | 89 / 133 / 0.67 / 2100 |
| Marcella | - | - | 8 / 4 / 2.00 / 36 |
| Prism | 70 / 28 / 2.50 / 480 | 79 / 31 / 2.55 / 742 | 15 / 16 / 0.94 / 60 |
| Ren | 106 / 88 / 1.20 / 1390 | 106 / 84 / 1.26 / 1052 | 69 / 88 / 0.78 / 1654 |
| Ryth | 64 / 78 / 0.82 / 598 | 65 / 80 / 0.81 / 588 | 31 / 55 / 0.56 / 572 |
| Stellar | 185 / 88 / 2.10 / 3030 | 164 / 84 / 1.95 / 2120 | 87 / 114 / 0.76 / 1886 |
| Tavi | 100 / 80 / 1.25 / 816 | 103 / 75 / 1.37 / 782 | 55 / 60 / 0.92 / 952 |
| Varg | 9 / 67 / 0.13 / 176 | 9 / 66 / 0.14 / 114 | 39 / 89 / 0.44 / 1334 |
| Vendetta | 13 / 67 / 0.19 / 110 | 16 / 66 / 0.24 / 110 | 28 / 48 / 0.58 / 552 |
| VesperVale | - | - | - |
| Willow | - | - | 17 / 14 / 1.21 / 294 |

### deaths per game by map (all deaths incl. pair; deaths/game, gems lost/game, games)

| map | study27 us | study26 us | study27 opp |
|---|---|---|---|
| collision | 12.6 / 169 (19) | 11.3 / 126 (19) | 8.8 / 200 (19) |
| corners | 12.4 / 81 (19) | 13.5 / 112 (17) | 7.6 / 71 (19) |
| elkring | 6.1 / 120 (9) | 6.5 / 100 (14) | 11.1 / 156 (9) |
| expanse | 0.0 / 0 (17) | 0.0 / 0 (17) | 0.1 / 0 (17) |
| interlock | 5.3 / 134 (19) | 4.3 / 114 (13) | 5.7 / 153 (19) |
| lanes | 3.8 / 21 (17) | 3.8 / 16 (18) | 0.8 / 15 (17) |
| monolith | 2.8 / 26 (16) | 3.8 / 48 (13) | 2.4 / 28 (16) |
| packs | 7.1 / 28 (22) | 7.0 / 20 (21) | 2.4 / 17 (22) |
| rows | 0.1 / 4 (17) | 0.1 / 4 (18) | 0.0 / 0 (17) |

### deaths per game by result / tier / draft size

| split | study27 us | study26 us | study27 opp |
|---|---|---|---|
| res win | 3.1 / 41 (58) | 3.3 / 43 (59) | 6.7 / 121 (58) |
| res loss | 7.4 / 77 (97) | 7.3 / 67 (91) | 2.5 / 37 (97) |
| tier top10 | 5.9 / 46 (50) | 6.3 / 61 (50) | 2.1 / 36 (50) |
| tier 11-20 | 6.6 / 77 (50) | 5.5 / 59 (50) | 4.3 / 72 (50) |
| tier 21-30 | 5.4 / 73 (50) | 5.9 / 57 (45) | 6.0 / 100 (50) |
| tier other | 1.2 / 9 (5) | 0.4 / 9 (5) | 1.4 / 25 (5) |
| nch 3 | 6.8 / 66 (58) | 6.4 / 49 (57) | 3.8 / 72 (58) |
| nch 4 | 2.9 / 73 (36) | 1.9 / 50 (31) | 3.0 / 81 (36) |
| nch 5 | 6.5 / 56 (61) | 7.1 / 68 (62) | 4.9 / 57 (61) |

Deaths per game distribution (us): study27 0:41, 1:11, 2:14, 3:12, 4:5, 5:9, 6:7, 7:7, 8:10, 9:4, 10:3, 11:4, 12:2, 13:2, 14:6, 15:4, 17:1, 18:1, 19:2, 20:5, 21:2, 22:1, 23:1, 24:1; study26 0:44, 1:11, 2:7, 3:6, 4:9, 5:11, 6:6, 7:15, 8:3, 9:4, 10:7, 11:3, 12:4, 13:2, 14:1, 15:3, 16:3, 18:2, 19:1, 20:1, 21:2, 22:1, 23:1, 24:1, 25:1, 28:1


Deaths during a tribute channel (from `extra.py`, direct deaths): study27 23 (1436 gems), study26 17 (724 gems), study27 opponents 33 (2314 gems). Idle-under-fire streaks of 3+ rounds: 28 vs 22 (opponents 19); melee hit rounds standing still with the attacker 2+ tiles away: 17% in both (745/4284 vs 689/3954).

## 6. Stacking and deaths

"On a camp group" = within 3 tiles of a living camp entity of that group (monster or cluster); stack = number of our living champions on the same group as the victim (victim included); big group = the bot P_STACK_HP rule: a non-monolith camp group (replay group id) whose monsters total >= 3000 hp: the 3-wolf groups of rows (4050, 6 per map) and the elk pairs of corners (4800, 4 per map); every other map has only 1350/2400/2700 groups. Exposure = champion-rounds. Direct deaths only.

### exposure: share of champion-rounds by stack size (small groups / big groups)

| stack | study27 us | study26 us | study27 opp |
|---|---|---|---|
| 0 | 60% / 0% (190116 / 0) | 59% / 0% (181076 / 0) | 62% / 0% (208338 / 0) |
| 1 | 21% / 0% (67502 / 766) | 21% / 0% (64352 / 1010) | 20% / 0% (68499 / 1552) |
| 2 | 11% / 1% (36674 / 2902) | 12% / 2% (38384 / 4890) | 10% / 1% (32658 / 2962) |
| 3 | 4% / 1% (11835 / 3318) | 4% / 1% (12456 / 4506) | 4% / 1% (12693 / 3522) |
| 4 | 1% / 1% (2228 / 3924) | 1% / 0% (1780 / 0) | 1% / 0% (4028 / 1260) |
| 5+ | 0% / 0% | 0% / 0% | 0% / 0% |


### where stacking happens: per map, our champion-rounds (study27, then study26)

Big group = non-monolith replay camp group with >= 3000 monster hp (rows: six 3-wolf groups; corners: four elk pairs). Caveat: on lanes the 18 single wolves are 4-8 wolves within 4 tiles of each other by position; the replay's group ids keep them separate and so, presumably, does the bot (stack 3+ share there fell 3.6% -> 2.7%). "Carrying >= 60" = champion-rounds with a bag of 60+ gems.

| map | games | big groups/map | champ-rounds | on a big group | stack 3+ | stack 3+ on big | stack 4+ | mean bag carried | share of champ-rounds carrying >= 60 | max bag per game (mean) |
|---|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 0 | 43672 | 0.0% | 8.3% | 0.0% | 0.8% | 11.6 | 1.9% | 115 |
| corners | 19 | 4 | 39755 | 0.1% | 5.9% | 0.0% | 1.4% | 6.7 | 0.5% | 64 |
| elkring | 9 | 0 | 25158 | 0.0% | 8.7% | 0.0% | 2.4% | 12.8 | 1.8% | 78 |
| expanse | 17 | 0 | 24892 | 0.0% | 1.0% | 0.0% | 0.6% | 8.8 | 1.5% | 104 |
| interlock | 19 | 0 | 41961 | 0.0% | 6.4% | 0.0% | 1.2% | 15.4 | 10.9% | 120 |
| lanes | 17 | 0 | 35066 | 0.0% | 2.7% | 0.0% | 0.0% | 6.1 | 0.1% | 51 |
| monolith | 16 | 0 | 40718 | 0.0% | 1.3% | 0.0% | 0.2% | 12.9 | 0.2% | 60 |
| packs | 22 | 0 | 34953 | 0.0% | 4.8% | 0.0% | 0.5% | 5.3 | 0.0% | 49 |
| rows | 17 | 6 | 33255 | 32.7% | 21.8% | 21.8% | 11.8% | 12.8 | 14.5% | 97 |

| map | games | big groups/map | champ-rounds | on a big group | stack 3+ | stack 3+ on big | stack 4+ | mean bag carried | share of champ-rounds carrying >= 60 | max bag per game (mean) |
|---|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 0 | 43825 | 0.0% | 8.7% | 0.0% | 0.6% | 10.4 | 1.5% | 102 |
| corners | 17 | 4 | 34971 | 0.0% | 6.3% | 0.0% | 1.3% | 6.9 | 0.5% | 70 |
| elkring | 14 | 0 | 36173 | 0.0% | 8.0% | 0.0% | 1.1% | 12.0 | 0.6% | 62 |
| expanse | 17 | 0 | 23728 | 0.0% | 0.8% | 0.0% | 0.5% | 9.2 | 1.2% | 97 |
| interlock | 13 | 0 | 28230 | 0.0% | 5.9% | 0.0% | 1.6% | 13.3 | 9.1% | 88 |
| lanes | 18 | 0 | 38956 | 0.0% | 3.6% | 0.0% | 0.4% | 6.4 | 0.0% | 48 |
| monolith | 13 | 0 | 32254 | 0.0% | 1.5% | 0.0% | 0.2% | 13.1 | 0.6% | 64 |
| packs | 21 | 0 | 34458 | 0.0% | 5.1% | 0.0% | 0.2% | 5.6 | 0.1% | 51 |
| rows | 18 | 6 | 36044 | 28.8% | 12.5% | 12.5% | 0.0% | 11.5 | 15.2% | 88 |

### direct deaths by stack size at death, and deaths per 1000 champion-rounds in that state

| stack at death | study27 us | study26 us | study27 opp |
|---|---|---|---|
| 0 | 483 (66% of deaths; 2.54 per 1000 cr) | 457 (64% of deaths; 2.52 per 1000 cr) | 319 (64% of deaths; 1.53 per 1000 cr) |
| 1 | 159 (22% of deaths; 2.33 per 1000 cr) | 165 (23% of deaths; 2.52 per 1000 cr) | 113 (23% of deaths; 1.61 per 1000 cr) |
| 2 | 66 (9% of deaths; 1.67 per 1000 cr) | 64 (9% of deaths; 1.48 per 1000 cr) | 48 (10% of deaths; 1.35 per 1000 cr) |
| 3 | 21 (3% of deaths; 1.39 per 1000 cr) | 23 (3% of deaths; 1.36 per 1000 cr) | 9 (2% of deaths; 0.56 per 1000 cr) |
| 4+ | 2 (0% of deaths; 0.32 per 1000 cr) | 0 (0% of deaths; 0.00 per 1000 cr) | 8 (2% of deaths; 1.08 per 1000 cr) |

| | study27 us | study26 us | study27 opp |
|---|---|---|---|
| death on a big camp group (stack >= 1, big) | 0% (0/731) | 0% (0/709) | 0% (0/497) |
| death with 3-4 of ours on the same camp group | 3% (23/731) | 3% (23/709) | 3% (17/497) |
|   of those, on a big group | 0% (0/23) | 0% (0/23) | 0% (0/17) |
| 5 rounds before death: 3-4 of ours on one camp group | 4% (26/731) | 3% (21/709) | 5% (27/497) |
| living camp monster within 3 at death | 17% (124/731) | 20% (145/709) | 18% (88/497) |
|   awake monster within 3 | 10% (72/731) (z=-1.9) | 13% (93/709) | 11% (56/497) |
| hit by a camp in the previous 5 rounds | 13% (92/731) | 16% (110/709) | 12% (62/497) |
|   camp dealt >= 300 in the previous 5 rounds | 2% (11/731) | 2% (11/709) | 2% (9/497) |
| killed by a camp | 3% (22/731) | 4% (25/709) | 3% (15/497) |
| allies within 6 at death: 0 | 34% (248/731) | 36% (258/709) | 35% (173/497) |
| allies within 6 at death: 1 | 38% (281/731) | 36% (256/709) | 35% (175/497) |
| allies within 6 at death: 2+ | 28% (202/731) | 28% (195/709) | 30% (149/497) |
|   stack >= 3 deaths: enemies within 8 >= 3 | 57% (13/23) | 65% (15/23) | 76% (13/17) |
|   stack >= 3 deaths: hit by a camp in prev 5 rounds | 52% (12/23) | 30% (7/23) | 18% (3/17) |
|   stack 0 deaths: hit by a camp in prev 5 rounds | 3% (15/483) | 3% (14/457) | 3% (10/319) |

### gems lost by stack size at death (direct deaths)

| stack | study27 us | study26 us | study27 opp |
|---|---|---|---|
| 0 | 5202 gems in 483 deaths (33.6/game) | 5040 gems in 457 deaths (33.6/game) | 6300 gems in 319 deaths (40.6/game) |
| 1 | 2460 gems in 159 deaths (15.9/game) | 1400 gems in 165 deaths (9.3/game) | 2118 gems in 113 deaths (13.7/game) |
| 2 | 732 gems in 66 deaths (4.7/game) | 490 gems in 64 deaths (3.3/game) | 842 gems in 48 deaths (5.4/game) |
| 3+ | 208 gems in 23 deaths (1.3/game) | 364 gems in 23 deaths (2.4/game) | 48 gems in 17 deaths (0.3/game) |

### hit episodes starting while stacked (hit-round starts after a quiet round), and deaths per such start

| stack at hit | study27 us | study26 us | study27 opp |
|---|---|---|---|
| 0 | 2610 (60%; 13.7 per 1000 cr) | 2251 (58%; 12.4 per 1000 cr) | 2915 (59%; 14.0 per 1000 cr) |
| 1 | 1018 (23%; 14.9 per 1000 cr) | 972 (25%; 14.9 per 1000 cr) | 1110 (22%; 15.8 per 1000 cr) |
| 2 | 537 (12%; 13.6 per 1000 cr) | 523 (13%; 12.1 per 1000 cr) | 554 (11%; 15.6 per 1000 cr) |
| 3+ | 207 (5%; 9.6 per 1000 cr) | 167 (4%; 8.8 per 1000 cr) | 369 (7%; 15.6 per 1000 cr) |


## 7. The 5 worst study27 games by gems lost to our deaths



| # | match | map | opponent (rank) | result | score us-opp | our deaths | gems lost | opp deaths / gems lost | biggest losses (type r round gems) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | e3bf65f3 | collision | EMPEROR Tung (30) | loss | 570-1040 | 10 | 434 | 11 / 432 | Stellar r824 216g, Stellar r637 108g, Stellar r520 44g, Issac r44 22g |
| 2 | d1ce27ab | collision | test (14) | loss | 770-1012 | 20 | 396 | 7 / 220 | Ren r1038 110g, Ren r899 66g, Ren r812 44g, Stellar r436 44g |
| 3 | 8f2955db | collision | Cabbage (16) | loss | 264-1178 | 24 | 372 | 9 / 110 | Stellar r769 174g, Issac r716 44g, Stellar r514 44g, Cassi r120 22g |
| 4 | 3ab8a976 | interlock | Boost (15) | loss | 530-1008 | 11 | 348 | 4 / 108 | Stellar r352 130g, Cassi r335 72g, Issac r335 36g (pair), Cassi r188 22g |
| 5 | 951ce686 | corners | lETHal (22) | loss | 476-1036 | 17 | 346 | 1 / 22 | Stellar r170 48g, Stellar r544 48g, Prism r268 48g, Prism r562 48g |


### What decided each of the five (from the round-by-round tables below and the full death lists)

1. **e3bf65f3 collision vs EMPEROR Tung (#30), lost 570-1040, 434 gems lost in 10 deaths (the opponent also lost 432 in 11).** Two tribute-channel deaths at the centre altar decide it. Stellar starts a tribute of **216 gems** at r806 at (26,19), 66% hp, Cassi 2 tiles away; the enemy Vendetta is visible at 8 tiles from r816 and walks in one tile per round (7, 6, 5, 2); at r820 she takes 144+144 and keeps channelling, Cassi walks off at r821, three more rounds of 144 per round with Vendetta adjacent, dead at r824 at tick 18 with the bag intact — never cancelled, never moved, nobody within 6 until Issac arrives at 5-6 tiles in the last two rounds. Earlier, at r628, the same Stellar had started a tribute of 108 gems **at 13% hp** at (27,21), alone, and Varg walked 6 -> 1 over r632-637 and killed her in two hits. The other eight deaths carry 0-44 gems (Issac r44 idle at 76%, Cassi/Issac pair deaths, Stellar r520 fighting Issac at 46% with 44 gems).
2. **d1ce27ab collision vs test (#14), lost 770-1012, 20 deaths, 396 gems.** A long game (r1038) in which we die 20 times, 11 of them while "approaching" at 95-100% hp and 4 while a recall was in progress; the enemy Stellar has 9 killing blows. The two expensive ones: Ren r891 starts a tribute of 66 gems at (26,19) at 100% hp with our Stellar at 2 and two enemies within 8; the enemy Stellar walks 7 -> 4, our Stellar leaves at r894, the enemy Ren's 697 spell lands at tick 5 (50%), Ren answers with one spell, one step away, Prism 273 + Stellar 397, dead at r899 alone. Ren r1038 (110 gems, the game's last round): dashes into the enemy Ren at 68% with nobody within 6, trades two attacks down to 50%, steps away twice and is killed from range 3 by a 705 spell.
3. **8f2955db collision vs Cabbage (#16), lost 264-1178, 24 deaths, 372 gems.** Our worst scoreline. 13 of the 24 deaths are the enemy Stellar's; 8 are pair deaths; 10 victims were "approaching" and 5 "idle" at 70-100% hp when the fatal episode started. Stellar r755 starts a tribute of **174 gems** at (26,21) at 100%, alone (no ally within 6 for the whole channel); the enemy Stellar is visible at 8 from r764 and walks to 4; a 1080-damage spell at r768 leaves 4%, dead at tick 14. Issac r716 (44 gems): walks laterally beside Cassi and Ren, then dashes *closer* toward Tavi/Stellar at 6 tiles and is one-shot by a 760 spell at 84% hp.
4. **3ab8a976 interlock vs Boost (#15), lost 530-1008, 11 deaths, 348 gems.** Seven of the eleven deaths had a recall in progress or attempted in the episode. Stellar r352 (**130 gems**): at 28% hp with the enemy Stellar at 5 it starts a recall at r348 at (16,17); Ren and Tavi are 4-6 tiles away for all four ticks and attack nobody; the enemy Stellar steps 6 -> 4 and the 254 spell at tick 4 kills her, 1 tick from arrival. Cassi r335 (72 gems) is the same shape 17 rounds earlier: 15% hp, one attack+spell at r331, one step away, recall at r333 with Tavi at 6, killed by a 105 spell at tick 2; Issac (36 gems) dies as her pair. Cassi r188 and Tavi r199 (22 gems each) also die with a recall running, at 96-100% hp at the first hit.
5. **951ce686 corners vs lETHal (#22), lost 476-1036, 17 deaths vs 1, 346 gems.** The corners pattern: 48-gem pot bags lost one at a time (Stellar r170, Tavi r202, Prism r268, Ren r410 during a tribute, Stellar r544, Prism r562). Stellar r170: stands idle at (36,32) at 62% while the enemy Issac walks 6 -> 2 over r161-165, trades basic attacks down to 35% with Issac adjacent, then retreats one tile per round for three rounds with Issac following every step; dead with 48 gems and no ally within 6 at any point. Stellar r544: four rounds of `nothing` at 100% hp at (34,37) with Tavi at 5 and 3-4 enemies within 8 (Prism 2 tiles away, also idle), then a step *closer*, Tavi 220 + Cassi 320 in two rounds (28% -> 10%), two attacks at 10% and 2%, dead; Prism and Ryth within 4-6 at the end, neither attacked.

Common thread, as in study26: none of the ten deciding deaths is a no-warning burst. The killer was visible at 5-8 tiles for 4-5 rounds before the first hit in all ten; four victims were in a tribute channel (none cancelled), three were in a recall channel started with the enemy at 4-6 tiles, three stood or walked toward the enemy at 62-100% hp. The new element is the size of the bags: 216, 174, 130, 110, 108 gems in one death each (study26's worst single losses were 174 and 146).

### Round-by-round tables of the two biggest gem losses in each of the five games

### 1. e3bf65f3 collision vs EMPEROR Tung (loss 570-1040): 434 gems lost

**Stellar (idx 3) dies r824 with 216 gems, killer Vendetta; doing before: tributing; first hit at r820 with hp 66%; zone middle, 20 from own spawn, 1 from altar; allies within 6 at death: 1.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 816 | 26,19 | 66 | 216 | tribute  |  | Vendetta 8 | 1 | Cassi@2 | tribute(r806) |
| 817 | 26,19 | 66 | 216 | tribute  |  | Vendetta 7 | 1 | Cassi@2 | tribute(r806) |
| 818 | 26,19 | 66 | 216 | tribute  |  | Vendetta 6 | 1 | Cassi@2 | tribute(r806) |
| 819 | 26,19 | 66 | 216 | tribute  |  | Vendetta 5 | 1 | Cassi@2 | tribute(r806) |
| 820 | 26,19 | 40 | 216 | tribute  | 144 Vendetta/atk, 144 Vendetta/atk | Vendetta 2 | 1 | Cassi@2 | tribute(r806) |
| 821 | 26,19 | 27 | 216 | tribute  | 144 Vendetta/atk | Vendetta 1 | 1 |  | tribute(r806) |
| 822 | 26,19 | 14 | 216 | tribute  | 144 Vendetta/atk | Vendetta 1 | 1 |  | tribute(r806) |
| 823 | 26,19 | 2 | 216 | tribute  | 144 Vendetta/atk | Vendetta 1 | 1 | Issac@6 | tribute(r806) |
| 824 | 26,19 | 0 | 216 | DEAD (buy) | 22 Vendetta/atk | Vendetta 1 | 1 | Issac@5 | tribute(r806) |

**Stellar (idx 3) dies r637 with 108 gems, killer Varg; doing before: tributing; first hit at r636 with hp 14%; zone middle, 21 from own spawn, 1 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 632 | 27,21 | 13 | 108 | tribute  |  | Varg 6 | 1 |  | tribute(r628) |
| 633 | 27,21 | 13 | 108 | tribute  |  | Varg 5 | 1 |  | tribute(r628) |
| 634 | 27,21 | 13 | 108 | tribute  |  | Varg 4 | 1 |  | tribute(r628) |
| 635 | 27,21 | 13 | 108 | tribute  |  | Varg 3 | 2 |  | tribute(r628) |
| 636 | 27,21 | 2 | 108 | tribute  | 121 Varg/atk | Varg 2 | 2 |  | tribute(r628) |
| 637 | 27,21 | 0 | 108 | DEAD (buy) | 31 Varg/atk | Varg 1 | 2 |  | tribute(r628) |

### 2. d1ce27ab collision vs test (loss 770-1012): 396 gems lost

**Ren (idx 2) dies r1038 with 110 gems, killer Ren; doing before: fighting; first hit at r1038 with hp 50%; zone middle, 17 from own spawn, 4 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 1034 | 25,18 | 68 | 110 | fight+closer (atk,dash,move) |  | Ren 4 | 1 |  |  |
| 1035 | 25,18 | 59 | 110 | fight (atk) |  | Ren 1 | 1 |  |  |
| 1036 | 24,17 | 50 | 110 | fight+away (atk,move) |  | Ren 1 | 2 |  |  |
| 1037 | 23,16 | 50 | 110 | away (move) |  | Ren 2 | 2 |  |  |
| 1038 | 23,16 | 0 | 110 | DEAD (buy) | 705 Ren/sp | Ren 3 | 1 |  |  |

**Ren (idx 2) dies r899 with 66 gems, killer Stellar; doing before: tributing; first hit at r896 with hp 100%; zone middle, 19 from own spawn, 2 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 892 | 26,19 | 100 | 66 | tribute  |  | Stellar 7 | 2 | Stellar@2 | tribute(r891) |
| 893 | 26,19 | 100 | 66 | tribute  |  | Stellar 6 | 2 | Stellar@2 | tribute(r891) |
| 894 | 26,19 | 100 | 66 | tribute  |  | Stellar 6 | 2 |  | tribute(r891) |
| 895 | 26,19 | 100 | 66 | tribute  |  | Stellar 5 | 3 |  | tribute(r891) |
| 896 | 26,19 | 50 | 66 | tribute  | 697 Ren/sp | Stellar 4 | 3 |  | tribute(r891) |
| 897 | 26,19 | 47 | 66 | fight (spell) | 31 Stellar/atk | Stellar 3 | 3 |  |  |
| 898 | 25,18 | 28 | 66 | away (move) | 273 Prism/sp | Stellar 3 | 3 |  |  |
| 899 | 25,18 | 0 | 66 | DEAD  | 397 Stellar/sp | Ren 3 | 3 |  |  |

### 3. 8f2955db collision vs Cabbage (loss 264-1178): 372 gems lost

**Stellar (idx 3) dies r769 with 174 gems, killer Stellar; doing before: tributing; first hit at r768 with hp 100%; zone middle, 20 from own spawn, 1 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 764 | 26,21 | 100 | 174 | tribute  |  | Stellar 8 | 1 |  | tribute(r755) |
| 765 | 26,21 | 100 | 174 | tribute  |  | Stellar 7 | 1 |  | tribute(r755) |
| 766 | 26,21 | 100 | 174 | tribute  |  | Stellar 6 | 1 |  | tribute(r755) |
| 767 | 26,21 | 100 | 174 | tribute  |  | Stellar 5 | 1 |  | tribute(r755) |
| 768 | 26,21 | 4 | 174 | tribute  | 1080 Stellar/sp | Stellar 4 | 1 |  | tribute(r755) |
| 769 | 26,21 | 0 | 174 | DEAD (buy) | 45 Stellar/sp | Stellar 4 | 1 |  | tribute(r755) |

**Issac (idx 1) dies r716 with 44 gems, killer Stellar; doing before: walking; first hit at r716 with hp 84%; zone middle, 17 from own spawn, 4 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 712 | 18,14 | 84 | 44 | lateral (move) |  | Cassi 5 | 2 | Cassi@1 Ren@2 |  |
| 713 | 19,14 | 84 | 44 | lateral (move) |  | Cassi 5 | 3 | Ren@1 |  |
| 714 | 22,15 | 84 | 44 | closer (dash,move) |  | Tavi 6 | 3 | Ren@1 |  |
| 715 | 23,16 | 84 | 44 | closer (move) |  | Stellar 6 | 2 | Ren@2 |  |
| 716 | 23,16 | 0 | 44 | DEAD (move) | 760 Stellar/sp | Stellar 5 | 2 |  |  |

### 4. 3ab8a976 interlock vs Boost (loss 530-1008): 348 gems lost

**Stellar (idx 3) dies r352 with 130 gems, killer Stellar; doing before: recalling; first hit at r352 with hp 28%; zone own, 14 from own spawn, 3 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 348 | 16,17 | 28 | 130 | recall (recall) |  | Stellar 5 | 2 | Ren@5 | RECALL START |
| 349 | 16,17 | 28 | 130 | recall  |  | Stellar 6 | 2 | Ren@5 Tavi@6 | recall(r348) |
| 350 | 16,17 | 28 | 130 | recall  |  | Stellar 6 | 2 | Ren@5 Tavi@5 | recall(r348) |
| 351 | 16,17 | 28 | 130 | recall  |  | Stellar 5 | 2 | Tavi@4 Ren@5 | recall(r348) |
| 352 | 16,17 | 0 | 130 | DEAD (buy) | 254 Stellar/sp | Stellar 4 | 2 | Tavi@3 Ren@5 |  |

**Cassi (idx 0) dies r335 with 72 gems, killer Tavi; doing before: fleeing; first hit at r335 with hp 15%; zone own, 14 from own spawn, 4 from altar; allies within 6 at death: 1.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 331 | 16,18 | 15 | 72 | fight (atk,spell) |  | Ren 3 | 2 |  |  |
| 332 | 15,17 | 15 | 72 | away (move) |  | Tavi 4 | 2 |  |  |
| 333 | 15,17 | 15 | 72 | recall (recall) |  | Tavi 6 | 2 |  | RECALL START |
| 334 | 15,17 | 15 | 72 | recall  |  | Tavi 5 | 2 |  | recall(r333) |
| 335 | 15,17 | 0 | 72 | DEAD  | 105 Tavi/sp | Tavi 4 | 2 | Stellar@6 |  |

### 5. 951ce686 corners vs lETHal (loss 476-1036): 346 gems lost

**Stellar (idx 1) dies r170 with 48 gems, killer Issac; doing before: idle; first hit at r165 with hp 63%; zone own, 17 from own spawn, 5 from altar; allies within 6 at death: 0.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 161 | 36,32 | 62 | 0 | nothing  |  | Issac 6 | 1 |  |  |
| 162 | 36,32 | 62 | 0 | nothing  |  | Issac 5 | 1 |  |  |
| 163 | 36,32 | 62 | 0 | fight (spell) |  | Issac 4 | 2 |  |  |
| 164 | 36,32 | 62 | 0 | fight (atk,spell) |  | Issac 3 | 2 |  |  |
| 165 | 36,32 | 44 | 0 | fight (atk) | 68 Issac/atk, 68 Issac/atk | Issac 2 | 2 |  |  |
| 166 | 36,32 | 35 | 48 | fight (atk) | 68 Issac/atk | Issac 1 | 2 |  |  |
| 167 | 35,31 | 26 | 48 | lateral (move) | 68 Issac/atk | Issac 1 | 2 |  |  |
| 168 | 34,30 | 17 | 48 | away (move) | 68 Issac/atk | Issac 1 | 2 |  |  |
| 169 | 33,29 | 7 | 48 | away (move) | 68 Issac/atk | Issac 1 | 2 |  |  |
| 170 | 33,29 | 0 | 48 | DEAD (move) | 59 Issac/atk | Issac 1 | 2 |  |  |

**Stellar (idx 1) dies r544 with 48 gems, killer Tavi; doing before: idle; first hit at r539 with hp 100%; zone middle, 20 from own spawn, 1 from altar; allies within 6 at death: 2.**

| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |
|---|---|---|---|---|---|---|---|---|---|
| 535 | 34,37 | 100 | 0 | nothing  |  | Tavi 5 | 4 | Prism@2 Tavi@5 |  |
| 536 | 34,37 | 100 | 0 | nothing  |  | Tavi 5 | 4 | Prism@2 Tavi@5 |  |
| 537 | 34,37 | 100 | 0 | nothing  |  | Tavi 5 | 3 | Prism@2 Tavi@5 |  |
| 538 | 34,37 | 100 | 0 | nothing  |  | Tavi 5 | 3 | Prism@2 Tavi@5 |  |
| 539 | 35,36 | 70 | 0 | closer (move) | 220 Tavi/sp | Tavi 5 | 3 | Prism@2 |  |
| 540 | 35,36 | 28 | 48 | nothing  | 320 Cassi/sp | Tavi 4 | 3 | Prism@3 |  |
| 541 | 35,36 | 10 | 48 | fight (atk,spell) | 65 Tavi/atk, 65 Tavi/atk | Tavi 3 | 3 | Prism@3 |  |
| 542 | 35,36 | 2 | 48 | fight (atk,spell) | 65 Tavi/atk | Tavi 3 | 3 | Prism@3 |  |
| 543 | 36,35 | 2 | 48 | away (move) |  | Tavi 3 | 3 | Prism@3 Ryth@6 |  |
| 544 | 36,35 | 0 | 48 | DEAD (move) | 15 Tavi/atk | Tavi 3 | 3 | Prism@4 Ryth@6 |  |


## What changed with study27 and what did not

1. Changed: on rows (the only map where the 3000-hp rule finds big camps that we farm), 4-stacks on a camp group went from 0 to 11.8% of our champion-rounds and 3+-stacks from 12.5% to 21.8%; rows still has 0.1 deaths per game, so the change produced no deaths there.
2. Not changed: on all other maps the stacking shares are the same as study26 within a point (collision 8.3 vs 8.7% at 3+), so the deaths analysis is effectively a replication of study26 with a different opponent sample.
3. Not changed: deaths 5.80 vs 5.72 per game, direct 4.72 vs 4.73, episodes ending in death 24 vs 25%, hp at the first hit of the fatal episode 91 vs 90%, 70 vs 73% in our own half, 42 vs 38% walking toward the enemy beforehand.
4. Not changed: deaths next to a living camp (17 vs 20%), hit by a camp in the previous 5 rounds (13 vs 16%), killed by a camp (22 vs 25), deaths with 3-4 of ours on one camp group (23 vs 23, 0 on big groups in both), allies within 6 at death (0 in 34 vs 36%).
5. Not changed: hit-round action mix, retreat delay (median 2), retreat outcomes (death 24 vs 26%), recall volume and arrival (25.6/game, 92%), retry after interruption (36 vs 32%), help rate (49%), farming ally keeps farming (46%).
6. Small, plausible moves toward tighter groups: retreat steps with no ally within 6 27% vs 31% (z=-2.6), whole-group retreats 16% vs 14%, first hits with 2+ allies within 8 50% vs 48%, recalls with a foe within 5 arriving 70% vs 64% (z=2.5).
7. Changed for the worse, but driven by bag size not death count: gems lost 63.5 vs 57.2 per game (7.9% vs 7.1% of tribute), deaths with 60+ gems 34 vs 21, tribute-channel deaths 23 (1436 gems) vs 17 (724); five single deaths cost 108-216 gems, four of them tributes at collision's centre altar with an enemy walking in from 8 tiles.
8. Changed with the opponent pool, not with us: killing blows by Stellar 35 vs 30%, by Ryth/Vendetta 8 vs 14%; spell share of the fatal damage 74 vs 68%; opponents' own losses 68 gems per game (study26 opponents 57).
9. Same worst-game anatomy: a channel (tribute or recall) continued with an enemy at 4-6 tiles, a caster idle for 3-5 rounds while an enemy closes from 6, a melee dashing into a group at full hp; allies within 4-6 that attack nobody.
10. Bottom line: study27 is study26 with the same death profile and 6 more gems per game lost in bigger bags; the stacking rule did not create camp-side deaths, and a change aimed at deaths must target the tribute/recall channels under approach and the pre-hit idling, where the big bags go.
