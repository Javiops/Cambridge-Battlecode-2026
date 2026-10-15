# The opening (rounds 0-60): how Mite (#1) and Univardisty of Shingtonwash (#2) start a game

Data: 101 replays of 2026-10-15 (108 team-games: 6 per team per map). Everything below is measured from the decoded events (`$S/ws/steps`), scripts in `$S/reports/scripts_opening/` (`openlib.py` loader, `summarize.py` -> `summaries.json`, `tables.py` -> `tables.md`, `determinism.py`, `timelines.py` / `timelines_short.py`). Distances are BFS steps from the team's spawn to the tile next to the camp. "d11" = 11 steps. Round numbers are engine rounds; a capture lands exactly 6 rounds after the last monster of the group dies when a champion stays on the group's spawn tiles (kill r10 -> reward r16, seen in every game).

## 1. Summary

- **Mite opens the same way on every map: the whole team (or all but one) stacks the nearest camp, kills it in 4-11 rounds, leaves exactly one champion on the capture tiles and fans out "nearest camp that is up" with 1-3 champions per camp.** Then it banks early and small: first tribute at r25-32 on 6 of 9 maps (bag 22-44), the capturer carries and tributes.
- **Univardisty pre-assigns a split from round 1** (3 champions on the nearest camp, 1-2 champions walk straight to a second/third camp or to the centre), opens with ranged units firing from range 3-5 at r1-3, kills slower (9-15 rounds with 2-3 champions), recall-shops after the first capture (r21-30, items for 150-190 gold) and **banks late**: first tribute r50-67 on 6 of 9 maps, carrying 100-150 gems at r60.
- On the fight maps Mite farms 2-3 camps before going to the middle (collision: Issac at the centre altar r25 with 22 gems; interlock: contact r37-43 after 3 captures) except corners, where 4 champions walk straight to the centre altar (arrive r17-25) while Issac+Ren take the wolf. Univardisty sends 3 casters straight to the corners centre (r15-17) and loses every corners game (0-6), and on interlock sends Issac alone to the centre at r17.
- Both teams are deterministic in their opening: same camp order and timing in all 6 games of a map until an enemy is within about 10 tiles. Mite's draft is fixed per map; Univardisty's draft changes with the opponent (32 distinct map-draft combinations in 54 games, 2-5 per map, against Mite's 9) and its opening changes with the draft.
- Mite's one visible opening leak: a single champion attacking an elk alone for 10-30 rounds without killing it (elkring Varg r20-49, corners Issac r22-30, interlock Issac r41-52) and then recalling with nothing.

## 2. Rounds 1-10: who goes where (Q1)

Table A (per map, team; 6 games each). "first-choosers" = champions whose first camp hit was this group; "all hitters" = everybody who hit it before it died. "attack range" = Chebyshev distance attacker-camp at each hit (0 = standing on the camp tile after a dash/positioning; 1 = melee; 3-5 = ranged). "side" = where the attackers stand relative to the camp: between the camp and own spawn ("spawn"), to the side ("flank") or beyond it ("far_s"). No team ever attacks from a bush (bush fraction 0.00 everywhere); on 7 of 9 maps there is no bush within 3 tiles of the first camp, and on rows/lanes where there is one, nobody uses it.

| map | team | first group (type, dist) | first hit r | champs on it (first-choosers / all hitters) | kill r | capture r | capturers (n, gems each) | spread r10 | distinct first targets | attack range (tiles:count) | side |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rows | mite | wolf d11 (6) | 10 | 5 / 5 | 25 | 31 | 1 x 66 (6) | 5 | 1 | 0:72 1:338 3:89 | spawn:349 flank:102 far_s:48 |
| rows | uni | wolf d11 (6) | 9-12 | 5 / 5 | 24-25 | 30 | 1 x 66 (3, credited on spawn after a recall from the tile), 2 x 33/33 (3) | 3-4 | 1 | 0:65 1:183 2:55 3:100 4:20 5:13 | spawn:327 flank:83 far_s:26 |
| expanse | mite | wolf d5 (6) | 8 | 3-4 / 3-4 | 12-16 | 19-23 | 1 x 22 (6) | 2-4 | 1-2 | 1:107 3:56 | spawn:163 |
| expanse | uni | wolf d5 (6) | 9-10 | 2-3 / 2-3 | 18-22 | 24-28 | 1 x 22 (6) | 3-11 | 2-3 | 1:164 4:1 | spawn:137 flank:28 |
| lanes | mite | gem_cluster d30 (6) | 25 | 2 / 2 | 30 | 36 | 1 x 24 (6) | 6 | 4 | 1:66 | spawn:66 |
| lanes | uni | gem_cluster d30 (6) | 29-30 | 0-2 / 1-2 | 35-39 | 42-46 | 1 x 24 (6) | 2 | 3-6 | 1:2 3:48 4:4 5:1 | spawn:55 |
| monolith | mite | wolf d5 (6) | 4 | 6 / 6 | 7 | 13 | 1 x 22 (6) | 6-7 | 1 | 1:168 3:89 | spawn:245 flank:12 |
| monolith | uni | wolf d5 (6) | 3 | 3 / 3-4 | 11-12 | 17-19 | 1 x 22 (6) | 9-14 | 3 | 1:133 3:109 4:13 | spawn:185 far_s:70 |
| packs | mite | wolf d4 (6) | 4 | 4 / 4 | 14 | 20 | 1 x 44 (6) | 2-3 | 1 | 0:30 1:125 3:159 | spawn:271 flank:30 far_s:13 |
| packs | uni | wolf d4 (6) | 2-6 | 3-4 / 3-4 | 14-16 | 20-22 | 2 x 22/22 (2), 1 x 44 (4) | 2-9 | 1-2 | 0:5 1:182 3:66 4:9 5:13 | spawn:243 flank:20 far_s:12 |
| collision | mite | wolf d3 (6) | 3 | 4 / 4 | 10 | 16 | 1 x 22 (6) | 2-4 | 1 | 1:146 3:62 | spawn:208 |
| collision | uni | wolf d3 (6) | 2-3 | 3 / 3 | 10 | 16 | 1 x 22 (6) | 3-4 | 1 | 1:27 3:77 4:17 5:8 | spawn:129 |
| corners | mite | wolf d4 (6) | 4 | 2 / 2-4 | 16 | 22 | 1 x 22 (6) | 13 | 2-4 | 1:202 | spawn:202 |
| corners | uni | wolf d4 (6) | 4-5 | 2 / 2 | 16-18 | 22-24 | 1 x 22 (6) | 14-17 | 3-4 | 1:102 3:41 4:5 5:1 | spawn:123 flank:26 |
| elkring | mite | elk+gold_cluster d2 (6) | 2 | 5 / 5 | 12 | 18 | 1 x 36 (6) | 6 | 2 | 0:6 1:216 2:6 3:102 | spawn:306 far_s:18 flank:6 |
| elkring | uni | elk+gold_cluster d2 (6) | 1-2 | 5-6 / 5-6 | 10-11 | 17-18 | 1 x 36 (6) | 2-4 | 1 | 0:1 1:83 3:154 4:23 5:13 | spawn:262 flank:3 far_s:9 |
| interlock | mite | wolf d4 (6) | 4 | 4-5 / 4-5 | 10-11 | 16-17 | 1 x 22 (6) | 4-5 | 1-2 | 1:181 3:27 | spawn:158 flank:50 |
| interlock | uni | wolf d4 (6) | 3-4 | 1-2 / 1-2 | 18-21 | 24 | 1 x 22 (5); 6cb958d0: killed r21 by Stellar alone, reward only r30 (tiles left empty) | 13 | 2-3 | 1:122 2:1 3:19 4:6 5:6 | spawn:146 far_s:8 |

Reading per map (round numbers identical in all 6 games unless a range is given):

| map | Mite (fixed draft) | Univardisty |
|---|---|---|
| rows | All 5 walk 9-15 rounds to the 3-wolf group g0 (66 gems, d11): Issac first hit r10, Ren/Cassi r12, Ryth r14, Varg r16; dead r25; one capturer (Ryth, or Cassi on side b) gets 66 at r31. The other 4 leave on r25-26 for the next group (d24), dead r49-51. | Same group, all 5, ranged first hit r9-12 (Prism/Stellar from range 3-5), dead r24-25. Capture r30 by 1 (66) or 2 (33/33) champions. Two champions recall from the tiles at r25 with 0 gems, buy at r30-31 (10+150+90 gold). |
| expanse | 3 units (Ren, Cassi, Issac) on wolf d5, hit r8, dead r12-16; Stellar walks alone to gem cluster d11 (hit r15, dead r21-23). Capture r19-23 by Issac or Ren (22). | Issac+Vendetta+Varg on wolf d5 (hit r10, dead r18, cap r24 Vendetta); Cassi walks alone to gem cluster d11 (hit r14, dead r27). Spread at r10 is 4 tiles, like Mite. |
| lanes | 30-step walk; the 6 units split 4 ways at r25-38 over the gem clusters (24 gems each): Ren+Issac g36 (r25, dead r30, cap r36 Issac), Stellar/Cassi/Ren g38 (r30-33), Tavi g40, Cassi g12; Varg walks 37 rounds to elk g20 and hits it alone r38-60+ (never dead by r60). | Same split, later: Tavi/Prism first hit r29-30, one champion per cluster (6 clusters, 1-2 hitters each), dead r35-41, captures r42-50 (six captures by r50, 144 gems carried). |
| monolith | All 6 on wolf d5: Issac hits r4, dead r7 (4 rounds), cap r13 Ren. Then 6-way fan-out: Varg+Cassi+Issac elk d12 (r13-31), Stellar wolf d9 alone (r13-29), Ryth wolf d13 alone (r15-32), Ren walks to the middle altar with 22 gems. | Cassi+Issac+Ren on wolf d5 (hit r3, dead r12, cap r19 Issac); Stellar alone on wolf d9 (hit r7); Prism/Varg (or Varg+Vendetta) walk to wolf d13 from r1 (hit r14-18). Spread at r10 = 9-14 tiles. |
| packs | All 4 on the 2-wolf group d4: Cassi r4 (from spawn), dead r14, cap r20 Stellar (44). Then Ren alone to wolf d12 (r21), Cassi+Issac to the middle gem+gold cluster (r21-26). | 3-4 on wolf d4 (Tavi/Stellar hit r2-6), dead r14-16, cap r20-22 (1x44 or 2x22). Cassi (4-unit drafts) walks to the middle cluster alone at r14. |
| collision | All 4 on wolf d3: Cassi hits r3, dead r10, cap r16 Issac (22). Issac stays, the other 3 go to wolf d8 at r11 (dead r22, cap r28 Ryth), then Varg+Cassi wolf d12 (r26-38, cap r44 Varg). | All 3 on wolf d3: Stellar/Prism fire from spawn at r2 (range 4-5), dead r10, cap r16 Ren; wolf d8 r14-22 (cap r23 Ren, who recalls from the tile); wolf d12 r25-36 (cap r44 Stellar). |
| corners | Split 2/4 from r1: Issac+Ren wolf d4 (r4-16, cap r22 Ren); Varg, Stellar, Cassi, Ryth walk 17-25 rounds straight to the centre altar. Issac then hits elk d12 alone r22-30 and recalls at r32 with nothing. | Split 2/3 from r1: Ryth+Ren (or Will+Varg) wolf d4 (r4-18, cap r22-24); Stellar/Prism/Tavi walk to the centre gem clusters (arrive r15-18, hit r16-19). |
| elkring | 5 on elk+gold d2 (Issac/Ren hit r2, dead r12, cap r18 Issac 36); Varg walks 19 rounds to elk d15 and hits it alone r20-49 (never dead). Then 4 on elk d5 (r14-25, cap r30-31 Ren), 3 on elk d8 (r32-43, cap r49 Stellar). | All 5-6 on elk d2 (ranged hit r1-2, dead r10-11, cap r17-18 Ren/Ryth), then all on elk d5 (r12-25, cap r30-32), 4-5 on elk d8 (r25-41). Tightest grouping of any opening (spread 2-4 tiles at r10). |
| interlock | 4-5 on wolf d4 (Issac r4, dead r10-11, cap r16-17 Issac); Cassi goes alone to wolf d10 at r13 (joined r14-19, dead r20, cap r26 Varg); gem cluster g1 (3 clusters, 72 gems) r22-32 (cap r37-38 Ryth/Ren). | Ryth+Ren on wolf d4 (dead r18 - 15 rounds with 2), cap r24 Ryth; Cassi+Stellar gem cluster g1 d14 (hit r13-15, dead r23, cap r31 Stellar 72); Issac walks alone to the centre (20,21), arrives r17-20. |

Measured facts about the attack itself:
- Kill speed depends on the number of hitters: Mite 4 rounds with 6 on a wolf (monolith), 7-8 with 4-5 (collision, interlock), 11 with 4 on 2 wolves (packs), 11 with 5 on elk+gold (elkring), 16 with 5 on 3 wolves (rows); Univardisty 9-10 with 3 on a wolf, 15 with 2 (interlock), 19 with 1 (interlock 6cb958d0, Stellar alone r3-21).
- Mite hits at range 1 in 69% of its first-camp hits (Varg, Ryth, Ren, Issac melee) and at range 3 in 26% (Cassi's and Stellar's spells, Ryth's slot 0). Univardisty's casters hit at range 3-5 (Stellar, Prism, Tavi; 41% of its first-camp hits are at range 3-5) and step one tile closer every 2-4 rounds (the "walk r14 / camp r15-17 / walk r18" pattern in the timelines).
- Both teams stand between the camp and their own spawn (Mite 88% of hits from the "spawn side", Univardisty 85%); never beyond it. The wolf focuses one champion (20 dmg x 2-3 per round) and the focused champion keeps hitting; nobody kites.
- Mite stacks; Univardisty splits. Distinct first targets per game: Mite 1 on rows/monolith/packs/collision/interlock(5 of 6), 2 on expanse/elkring/corners, 4 on lanes. Univardisty 3-4 on monolith, corners, interlock, lanes; 2 on expanse; 1 on rows/packs/collision/elkring. Mite's spread at r10 is 2-7 tiles on 7 maps; Univardisty's is 9-17 tiles on monolith, corners, interlock.

## 3. The first capture (Q2)

- At most one champion stands on the capture tiles during the whole capture window in 97 of 108 first captures (Mite 48/54, the exceptions being packs x5 and rows x1 where a second champion stands on the second monster's tile for a round or two; Univardisty 49/54, with 2 occupants sharing the reward on rows x3 (33/33) and packs x2 (22/22)). More allies do not speed a capture, and both teams know it.
- Who stays: the champion standing on (or next to) the camp tile at the kill, which is almost always a melee unit. Mite: Issac on collision (5/6), interlock (4/6), elkring (6/6), lanes (6/6); Ren on monolith (5/6), corners (6/6); Stellar on packs (5/6, it dashes onto the tile); Ryth on rows. Univardisty: Ren (collision 6/6, elkring 3/6, corners), Issac (expanse, monolith 6/6, rows), Vendetta (expanse), Ryth (interlock 5/6).
- Who moves on: everybody else, the same round the camp dies. Of the hitters that did not capture, 199/206 Mite and 142/156 Univardisty champion-cases went to the next camp (the rest were corners/packs fights). On rows r25-26 Mite's 4 non-capturers leave for the d24 group while Ryth sits 6 rounds alone.
- Who carries: the capturer. Mite's capturer either walks to the altar (collision Issac 22 gems r17-26 -> mid altar; monolith Ren r14-26 -> mid altar; elkring Issac -> mid altar r19-31; interlock Issac -> own altar r18-24) or starts a recall on the capture tile the round the reward lands (packs Stellar r20, 44 gems -> home r25 -> own altar r29; rows Ryth starts the recall at r28, gets 66 at r31, arrives r33, buys two items (150+120) and walks back out with the gems; lanes Ren r51). Univardisty's capturer recalls from the tile at r23-26 on collision/rows/monolith/elkring (collision: Ren recall r24, reward 22 lands at r29 on spawn, buys 150+10, walks back 10 rounds), and otherwise keeps farming with the gems on it.
- Univardisty loses a round on several captures by stepping off the tiles (empty tile = timer reset): lanes 6/6 games have a window with 0 occupants (kill r39 -> reward r46 instead of r45), monolith 4/6, elkring 5/6.

## 4. First tribute (Q3)

| map | team | first tribute r | altar | bag | who | tributes by r60 (n games with >=1) | recalls by r60 per game | captures by r60 per game | gems carried+tributed r60 |
|---|---|---|---|---|---|---|---|---|---|
| rows | mite | none by r70 | none(6) | - | none(6) | 0/6 | 2 | 2 | 132 |
| rows | uni | 65-66 | none(4), own(2) | 33-99 | none(4), Varg(2) | 0/6 | 2-4 | 1-3 | 66-132 |
| expanse | mite | 44-60 | own(6) | 70-96 | Ren4(1), Issa(5) | 6/6 | 0-1 | 4 | 140 |
| expanse | uni | 35-37 | own(6) | 24-48 | Issa(5), Varg(1) | 6/6 | 0-1 | 3-5 | 92-140 |
| lanes | mite | 48-51 | own(6) | 24 | Issa(6) | 6/6 | 1 | 5 | 132 |
| lanes | uni | 51 | none(5), own(1) | 24 | none(5), Ren4(1) | 1/6 | 0 | 6 | 144 |
| monolith | mite | 27 | mid(6) | 22 | Ren1(5), Issa(1) | 6/6 | 2-4 | 4 | 102 |
| monolith | uni | 62 | none(5), enemy(1) | 22 | none(5), Varg(1) | 0/6 | 1-3 | 4-5 | 110-154 |
| packs | mite | 28-29 | own(6) | 44 | Stel(5), Ren3(1) | 6/6 | 1-4 | 1-3 | 44-140 |
| packs | uni | 29-67 | own(5), enemy(1) | 22-88 | Issa(1), Varg(3), Ren5(2) | 4/6 | 1-4 | 2-5 | 88-136 |
| collision | mite | 27-31 | mid(6) | 22 | Issa(5), Ryth(1) | 6/6 | 0-3 | 2-4 | 44-110 |
| collision | uni | 57-65 | mid(4), none(2) | 22-88 | Ren2(1), Stel(2), none(2), Ren5(1) | 2/6 | 1-2 | 3 | 66-110 |
| corners | mite | 32-43 | mid(3), none(3) | 22-48 | Ryth(1), none(3), Ren1(2) | 3/6 | 1-7 | 1-4 | 22-166 |
| corners | uni | 41 | none(5), mid(1) | 22 | none(5), Ren9(1) | 1/6 | 0-3 | 1-2 | 0-70 |
| elkring | mite | 32 | mid(6) | 36 | Issa(6) | 6/6 | 3 | 3-4 | 108 |
| elkring | uni | 50-67 | mid(4), none(2) | 36-72 | Tavi(1), Ren9(1), Ryth(1), Ren3(1), none(2) | 3/6 | 0-4 | 3-4 | 108-144 |
| interlock | mite | 25-28 | own(6) | 22 | Issa(4), Ryth(2) | 6/6 | 0-4 | 4 | 66-138 |
| interlock | uni | 33-53 | none(2), own(3), enemy(1) | 72 | none(2), Stel(3), Ren7(1) | 4/6 | 0-3 | 2-4 | 94-138 |

- Mite tributes early and small. On the fight maps it uses the **middle altar** (collision (27,20) at r27-31, bag 22; monolith (30,30)/(19,19) at r27, bag 22; elkring (3,26)/(26,3) at r32, bag 36; corners (35,34) at r32-43 when it is not fighting) and the **own-side altar** on farm maps (packs (2,6) r28-29 bag 44; interlock (20,23) r25-28 bag 22; lanes (29,4) r48-51 bag 24; expanse (66,53) r44-60 bag 70-96). On rows it does not tribute before r60: it carries 132 gems and uses the recall to shop (r28/r54), not to bank. First tributor: Issac in 27 of 54 games, Ren 9, Stellar 5, Ryth 4, none by r70 in 9.
- Univardisty tributes late or not at all by r60: never on rows (first r65-66), lanes (5/6 none), monolith (5/6 none), corners (5/6 none), 2/6 games on collision (r57-65, mid altar), 3/6 on elkring (r50-67). Only on expanse (r35-37, own altar, 24-48), packs (r29-31, own altar, 44) and interlock (Stellar 72 at r33-53) does it bank in the opening. At r60 it carries 108-154 gems on 5 maps.
- Tribute durations are as the rules say: 22 gems = 3 ticks (start r27 -> done r30), 36 = 4, 44 = 5, 72 = 8, 96 = 10 (Mite Ren on expanse r60).

## 5. Timelines to r60 (Q4)

Condensed per-champion timelines (coordinates dropped; camp label = group id, type, side, distance from own spawn). The first game of each map is the Mite-vs-Univardisty game when one exists, so both teams are seen on the same map in the same game. Full versions with coordinates: `$S/reports/scripts_opening/timelines.md`.

#### rows
**mite** (side a) vs uni, match `e862af8e`, win:
- Varg0: walk r1-15 > camp g0 wolf(own,d11) r16-25 > walk r26-36 > camp g2 wolf(own,d24) r37-51 > capture r52 > walk r53-60
- Ryth1: walk r1-13 > camp g0 wolf(own,d11) r14-25 > capture r26-27 > recall r28 > cap+recall r29-32 > walk r33-60
- Cass2: walk r1-11 > camp g0 wolf(own,d11) r12-24 > walk r25-37 > camp g2 wolf(own,d24) r38-50 > walk r51-60
- Issa3: walk r1-9 > camp g0 wolf(own,d11) r10-25 > walk r26-32 > camp g2 wolf(own,d24) r33-51 > capture r52-53 > recall r54 > cap+recall r55-58 > walk r59-60
- Ren4: walk r1-11 > camp g0 wolf(own,d11) r12-24 > capture r25 > walk r26-34 > camp g2 wolf(own,d24) r35-50 > walk r51-58 > camp g4 wolf(own,d35) r59-60
- key events: r28 recall Ryth1 0; r31 capture Ryth1 66; r54 recall Issa3 0; r57 capture Issa3 66
**uni** (side b) vs mite, match `e862af8e`, loss:
- Cass5: walk r1-12 > camp g1 wolf(own,d11) r13-24 > walk r25-35 > camp g3 wolf(own,d24) r36-48 > recall r50-55 > walk r56-60
- Issa6: walk r1-11 > camp g1 wolf(own,d11) r12-24 > recall r25-30 > walk r31-55 > camp g3 wolf(own,d24) r56 > walk r57-60
- Stel7: walk r1-9 > camp g1 wolf(own,d11) r10-24 > walk r25-32 > camp g3 wolf(own,d24) r33-55 > capture r56 > recall r57 > cap+recall r58-60
- Tavi8: walk r1-9 > camp g1 wolf(own,d11) r10-24 > walk r25-34 > camp g3 wolf(own,d24) r35-55 > walk r56-60
- Varg9: walk r1-15 > camp g1 wolf(own,d11) r16-24 > recall r25 > cap+recall r26-29 > capture r30 > walk r31-60
- key events: r25 recall Issa6 0; r25 recall Varg9 0; r30 capture Varg9 66; r50 recall Cass5 0; r57 recall Stel7 0
**mite** (side a) vs Intercontinental Fish, match `dafdce22`, loss:
- Varg0: walk r1-15 > camp g0 wolf(own,d11) r16-25 > walk r26-36 > camp g2 wolf(own,d24) r37-51 > capture r52 > walk r53-60
- Ryth1: walk r1-13 > camp g0 wolf(own,d11) r14-25 > capture r26-27 > recall r28 > cap+recall r29-32 > walk r33-60
- Cass2: walk r1-11 > camp g0 wolf(own,d11) r12-24 > walk r25-37 > camp g2 wolf(own,d24) r38-50 > walk r51-60
- Issa3: walk r1-9 > camp g0 wolf(own,d11) r10-25 > walk r26-32 > camp g2 wolf(own,d24) r33-51 > capture r52-53 > recall r54 > cap+recall r55-58 > walk r59-60
- Ren4: walk r1-11 > camp g0 wolf(own,d11) r12-24 > capture r25 > walk r26-34 > camp g2 wolf(own,d24) r35-50 > walk r51-58 > camp g4 wolf(own,d35) r59-60
- key events: r28 recall Ryth1 0; r31 capture Ryth1 66; r54 recall Issa3 0; r57 capture Issa3 66
**uni** (side b) vs Intercontinental Fish, match `8e028e85`, loss:
- Cass5: walk r1-12 > camp g1 wolf(own,d11) r13-25 > walk r26-35 > camp g3 wolf(own,d24) r36-48 > walk r49-57 > camp g5 wolf(own,d35) r58-60
- Issa6: walk r1-15 > camp g1 wolf(own,d11) r16-24 > capture r25 > recall r26 > cap+recall r27-30 > capture r31 > walk r32-60
- Varg7: walk r1-12 > camp g1 wolf(own,d11) r13-24 > walk r25-34 > camp g3 wolf(own,d24) r35-47 > capture r48 > recall r49 > cap+recall r50-53 > capture r54 > walk r55-60
- Pris8: walk r1-8 > camp g1 wolf(own,d11) r9-24 > walk r25-32 > camp g3 wolf(own,d24) r33-48 > walk r49-55 > camp g5 wolf(own,d35) r56-60
- Stel9: walk r1-13 > camp g1 wolf(own,d11) r14-24 > walk r25-34 > camp g3 wolf(own,d24) r35-48 > walk r49-57 > camp g5 wolf(own,d35) r58-60
- key events: r26 recall Issa6 0; r31 capture Issa6 66; r49 recall Varg7 0; r54 capture Varg7 66

#### expanse
**mite** (side b) vs Intercontinental Fish, match `8c9f4333`, win:
- Ren4: walk r1-7 > camp g21 wolf(own,d5) r8-16 > walk r17-19 > camp g3 gem_(own,d11) r20-23 > capture r24-29 > camp g23 wolf(own,d15) r31-35 > walk r36-44 > camp g1 gem_(own,d28) r45-48 > capture r49-55 > walk r56-59 > tribute r60
- Stel5: walk r1-14 > camp g3 gem_(own,d11) r15-22 > walk r23-26 > camp g23 wolf(own,d15) r27-34 > walk r35-47 > camp g1 gem_(own,d28) r48 > walk r49-59 > camp g29 wolf(own,d27) r60
- Cass6: walk r1-7 > camp g21 wolf(own,d5) r8-15 > walk r16-39 > camp g1 gem_(own,d28) r40-48 > walk r49-59 > camp g29 wolf(own,d27) r60
- Issa7: walk r1-8 > camp g21 wolf(own,d5) r9-16 > capture r17-22 > walk r23-27 > camp g23 wolf(own,d15) r28-35 > capture r36 > recall r37 > cap+recall r38-41 > walk r42-58 > camp g5 gem_(own,d17) r59-60
- key events: r22 capture Issa7 22; r29 capture Ren4 48; r37 recall Issa7 22; r41 capture Issa7 22; r55 capture Ren4 48; r60 tribute Ren4 96
**uni** (side b) vs Intercontinental Fish, match `14e939e8`, win:
- Cass4: walk r1-13 > camp g3 gem_(own,d11) r14-27 > walk r28-43 > camp g5 gem_(own,d17) r44-60
- Issa5: walk r1-9 > camp g21 wolf(own,d5) r10-17 > walk r18-24 > camp g3 gem_(own,d11) r25-26 > capture r27-33 > walk r34-36 > tribute r37-42 > walk r43-49 > camp g1 gem_(own,d28) r50-60
- Vend6: walk r1-9 > camp g21 wolf(own,d5) r10-18 > capture r19-24 > walk r25-31 > camp g23 wolf(own,d15) r32-40 > walk r41-49 > tribute r50-53 > walk r54-57 > camp g1 gem_(own,d28) r58-60
- Varg7: walk r1-11 > camp g21 wolf(own,d5) r12-17 > walk r18-21 > camp g3 gem_(own,d11) r22-26 > walk r27-30 > camp g23 wolf(own,d15) r31-40 > capture r41-46 > walk r47-51 > tribute r52-55 > walk r56-60
- key events: r24 capture Vend6 22; r33 capture Issa5 48; r37 tribute Issa5 48; r46 capture Varg7 22; r50 tribute Vend6 22; r52 tribute Varg7 22

#### lanes
**mite** (side a) vs uni, match `c8d4cf63`, win:
- Varg0: walk r1-37 > camp g20 elk(own,d33) r38-60
- Stel1: walk r1-31 > camp g38 gem_(own,d30) r32 > camp g40 gem_(own,d30) r34 > camp g34 elk(own,d33) r37-48 > capture r49 > walk r50-56 > camp g6 elk(own,d33) r57 > capture r58 > camp g6 elk(own,d33) r59-60
- Cass2: walk r1-29 > camp g38 gem_(own,d30) r30-32 > camp g12 gem_(own,d30) r34-45 > capture r48 > camp g10 gem_(own,d30) r49-51 > capture r52-55 > camp g6 elk(own,d33) r56 > capture r58 > camp g6 elk(own,d33) r59-60
- Issa3: walk r1-26 > camp g36 gem_(own,d30) r27-30 > capture r31-36 > camp g34 elk(own,d33) r37-45 > walk r46-50 > tribute r51-54 > walk r55-60
- Tavi4: walk r1-32 > camp g40 gem_(own,d30) r33 > capture r36 > camp g34 elk(own,d33) r37-47 > walk r48-50 > capture r51 > walk r52-55 > camp g10 gem_(own,d30) r56-57 > walk r58-60
- Ren5: walk r1-24 > camp g36 gem_(own,d30) r25-29 > camp g38 gem_(own,d30) r31-33 > capture r34-39 > camp g34 elk(own,d33) r40-48 > capture r49-50 > recall r51 > cap+recall r52-55 > walk r56-60
- key events: r36 capture Issa3 24; r39 capture Ren5 24; r42 capture Tavi4 24; r51 tribute Issa3 24; r51 recall Ren5 24; r54 capture Cass2 24; r55 capture Ren5 36
**uni** (side b) vs mite, match `c8d4cf63`, loss:
- Ryth6: walk r1-32 > camp g11 gem_(own,d30) r33 > walk r34-36 > camp g11 gem_(own,d30) r37-41 > capture r42-48 > walk r49-60
- Stel7: walk r1-30 > camp g13 gem_(own,d30) r31-35 > capture r38-44 > walk r45-49 > camp g41 gem_(own,d30) r50 > walk r51-60
- Pris8: walk r1-28 > camp g37 gem_(own,d30) r29-39 > capture r42-48 > walk r49-60
- Ren9: walk r1-31 > camp g39 gem_(own,d30) r32-40 > capture r41-45 > camp g41 gem_(own,d30) r46-52 > capture r53-58 > walk r59-60
- Tavi10: walk r1-32 > camp g9 gem_(own,d30) r33-41 > capture r44-50 > walk r51-60
- key events: r44 capture Stel7 24; r46 capture Ren9 24; r48 capture Ryth6 24; r48 capture Pris8 24; r50 capture Tavi10 24; r58 capture Ren9 24
**mite** (side a) vs Intercontinental Fish, match `8bf100be`, win:
- Varg0: walk r1-37 > camp g20 elk(own,d33) r38-60
- Stel1: walk r1-31 > camp g38 gem_(own,d30) r32 > camp g40 gem_(own,d30) r34 > camp g34 elk(own,d33) r37-48 > walk r49-59 > camp g6 elk(own,d33) r60
- Cass2: walk r1-29 > camp g38 gem_(own,d30) r30-32 > camp g12 gem_(own,d30) r34-45 > capture r48 > camp g10 gem_(own,d30) r49-51 > capture r52-55 > walk r56-59 > camp g6 elk(own,d33) r60
- Issa3: walk r1-26 > camp g36 gem_(own,d30) r27-30 > capture r31-36 > camp g34 elk(own,d33) r37-42 > walk r43-47 > tribute r48-51 > walk r52-54 > camp g10 gem_(own,d30) r55-56 > capture r57-60
- Tavi4: walk r1-32 > camp g40 gem_(own,d30) r33 > capture r36 > camp g34 elk(own,d33) r37-47 > capture r49 > capture r51 > walk r52-55 > camp g10 gem_(own,d30) r56 > capture r57-59 > camp g6 elk(own,d33) r60
- Ren5: walk r1-24 > camp g36 gem_(own,d30) r25-29 > camp g38 gem_(own,d30) r31-33 > capture r34-39 > camp g34 elk(own,d33) r40-48 > capture r49-50 > recall r51 > cap+recall r52-55 > walk r56-60
- key events: r36 capture Issa3 24; r39 capture Ren5 24; r42 capture Tavi4 24; r48 tribute Issa3 24; r51 recall Ren5 24; r54 capture Cass2 24; r55 capture Ren5 36
**uni** (side a) vs PTN Hyperion, match `3e800856`, loss:
- Cass0: walk r1-33 > camp g12 gem_(own,d30) r34 > camp g8 gem_(own,d30) r35-43 > walk r44-54 > capture r55 > walk r56-60
- Issa1: walk r1-32 > camp g10 gem_(own,d30) r33-40 > capture r41-47 > walk r48-51 > tribute r52-55 > walk r56-60
- Ryth2: walk r1-30 > camp g12 gem_(own,d30) r31 > camp g10 gem_(own,d30) r32 > camp g12 gem_(own,d30) r33-34 > capture r35-40 > camp g10 gem_(own,d30) r41 > camp g8 gem_(own,d30) r43-44 > capture r45-51 > walk r52-55 > tribute r56-60
- Marc3: walk r1-34 > camp g40 gem_(own,d30) r35 > capture r36-42 > camp g36 gem_(own,d30) r44-46 > capture r47-53 > walk r54-58 > camp g28 wolf(own,d37) r59-60
- Ren4: walk r1-31 > camp g38 gem_(own,d30) r32-38 > capture r39-44 > camp g36 gem_(own,d30) r45 > walk r46-50 > tribute r51-54 > walk r55-60
- Tavi5: walk r1-29 > camp g40 gem_(own,d30) r30-34 > camp g38 gem_(own,d30) r37-38 > camp g36 gem_(own,d30) r41-45 > walk r46-58 > camp g28 wolf(own,d37) r59-60
- key events: r41 capture Ryth2 24; r42 capture Marc3 24; r45 capture Ren4 24; r47 capture Issa1 24; r51 capture Ryth2 24; r51 tribute Ren4 24; r52 capture Marc3 24; r52 tribute Issa1 24; r56 tribute Ryth2 48

#### monolith
**uni** (side a) vs mite, match `ced08a2f`, win:
- Cass0: walk r1-2 > camp g7 wolf(own,d5) r3-12 > walk r13-20 > camp g9 wolf(own,d13) r21-25 > walk r26-32 > camp g19 wolf(own,d20) r33-36 > walk r37-47 > capture r48 > recall r49 > cap+recall r50-53 > capture r54 > walk r55-60
- Issa1: walk r1-4 > camp g7 wolf(own,d5) r5-12 > capture r13-19 > walk r20-31 > camp g19 wolf(own,d20) r32-37 > walk r38-60
- Stel2: walk r1-6 > camp g5 wolf(own,d9) r7-25 > capture r28-34 > walk r35-60
- Pris3: walk r1-17 > camp g9 wolf(own,d13) r18-24 > camp g19 wolf(own,d20) r27-37 > walk r38-58 > camp g7 wolf(own,d5) r59-60
- Ren4: walk r1-3 > camp g7 wolf(own,d5) r4-12 > walk r13-19 > camp g9 wolf(own,d13) r20-24 > capture r25-31 > camp g19 wolf(own,d20) r34 > walk r35-60
- Varg5: walk r1-13 > camp g9 wolf(own,d13) r14-17 > walk r18-23 > camp g19 wolf(own,d20) r24-36 > recall r37 > cap+recall r38-41 > walk r42-60
- key events: r19 capture Issa1 22; r31 capture Ren4 22; r34 capture Stel2 22; r37 recall Varg5 0; r49 recall Cass0 0; r54 capture Cass0 44
**mite** (side b) vs uni, match `ced08a2f`, loss:
- Varg6: walk r1-4 > camp g6 wolf(own,d5) r5-7 > walk r8-16 > camp g10 elk(own,d12) r17-31 > capture r32-37 > walk r38-51 > tribute r52-56 > recall r57-60
- Stel7: walk r1-3 > camp g6 wolf(own,d5) r4-6 > walk r7-12 > camp g4 wolf(own,d9) r13-29 > capture r32-38 > walk r39-52 > tribute r53-55 > recall r56-60
- Cass8: walk r1-4 > camp g6 wolf(own,d5) r5-6 > walk r7-15 > camp g10 elk(own,d12) r16-30 > walk r31-42 > camp g18 wolf(own,d20) r43-57 > recall r59-60
- Issa9: walk r1-3 > camp g6 wolf(own,d5) r4-7 > walk r8-12 > camp g10 elk(own,d12) r13-30 > walk r31-41 > camp g2 wolf(own,d23) r42-53 > recall r55-60
- Ryth10: walk r1-5 > camp g6 wolf(own,d5) r6-7 > walk r8-14 > camp g8 wolf(own,d13) r15-32 > capture r33-39 > walk r40-55 > tribute r56-59 > walk r60
- Ren11: walk r1-5 > camp g6 wolf(own,d5) r6-7 > capture r8-13 > walk r14-26 > tribute r27-30 > walk r31-39 > camp g21 wolf(own,d35) r40-60
- key events: r13 capture Ren11 22; r27 tribute Ren11 22; r37 capture Varg6 36; r38 capture Stel7 22; r39 capture Ryth10 22; r52 tribute Varg6 36; r53 tribute Stel7 22; r55 recall Issa9 0; r56 tribute Ryth10 22; r56 recall Stel7 0; r57 recall Varg6 0; r59 recall Cass8 0
**mite** (side b) vs Intercontinental Fish, match `be5f79ae`, win:
- Varg6: walk r1-4 > camp g6 wolf(own,d5) r5-7 > walk r8-16 > camp g10 elk(own,d12) r17-31 > capture r32-37 > walk r38-51 > tribute r52-56 > recall r57-60
- Stel7: walk r1-3 > camp g6 wolf(own,d5) r4-6 > walk r7-12 > camp g4 wolf(own,d9) r13-29 > capture r32-38 > walk r39-52 > tribute r53-55 > recall r56-60
- Cass8: walk r1-4 > camp g6 wolf(own,d5) r5-6 > walk r7-15 > camp g10 elk(own,d12) r16-30 > walk r31-42 > camp g18 wolf(own,d20) r43-57 > recall r59-60
- Issa9: walk r1-3 > camp g6 wolf(own,d5) r4-7 > walk r8-12 > camp g10 elk(own,d12) r13-30 > walk r31-41 > camp g2 wolf(own,d23) r42-53 > recall r55-60
- Ryth10: walk r1-5 > camp g6 wolf(own,d5) r6-7 > walk r8-14 > camp g8 wolf(own,d13) r15-32 > capture r33-39 > walk r40-55 > tribute r56-59 > walk r60
- Ren11: walk r1-5 > camp g6 wolf(own,d5) r6-7 > capture r8-13 > walk r14-26 > tribute r27-30 > walk r31-39 > camp g21 wolf(own,d35) r40-60
- key events: r13 capture Ren11 22; r27 tribute Ren11 22; r37 capture Varg6 36; r38 capture Stel7 22; r39 capture Ryth10 22; r52 tribute Varg6 36; r53 tribute Stel7 22; r55 recall Issa9 0; r56 tribute Ryth10 22; r56 recall Stel7 0; r57 recall Varg6 0; r59 recall Cass8 0
**uni** (side b) vs Intercontinental Fish, match `ed8c5da9`, win:
- Cass6: walk r1-2 > camp g6 wolf(own,d5) r3-12 > walk r13-26 > camp g18 wolf(own,d20) r27-43 > walk r44-59 > camp g21 wolf(own,d35) r60
- Issa7: walk r1-4 > camp g6 wolf(own,d5) r5-12 > capture r13-19 > walk r20-22 > camp g8 wolf(own,d13) r23-33 > recall r34 > cap+recall r35-38 > capture r39 > walk r40-60
- Stel8: walk r1-6 > camp g4 wolf(own,d9) r7-16 > capture r19-25 > walk r26-50 > capture r51 > walk r52-60
- Ren9: walk r1-3 > camp g6 wolf(own,d5) r4-12 > walk r13-24 > camp g18 wolf(own,d20) r25-43 > capture r44-50 > walk r51-60
- Varg10: walk r1-17 > camp g8 wolf(own,d13) r18-32 > walk r33-38 > camp g18 wolf(own,d20) r39-43 > capture r44-50 > walk r51-60
- Tavi11: walk r1-7 > camp g4 wolf(own,d9) r8-16 > walk r17-42 > camp g18 wolf(own,d20) r43 > walk r44-60
- key events: r19 capture Issa7 22; r25 capture Stel8 22; r34 recall Issa7 22; r39 capture Issa7 22; r50 capture Ren9 22; r50 capture Varg10 22

#### packs
**mite** (side a) vs uni, match `e2e84b09`, win:
- Ren0: walk r1-4 > camp g0 wolf(own,d4) r5-14 > capture r15-16 > walk r17-20 > camp g4 wolf(own,d12) r21-35 > recall r37-42 > walk r43-60
- Stel1: walk r1-4 > camp g0 wolf(own,d4) r5-13 > capture r16-19 > recall r20 > cap+recall r21-24 > walk r25-28 > tribute r29-34 > walk r35-42 > camp g2 gem_+gold(mid,d13) r43-51 > capture r54-60
- Cass2: walk r1-3 > camp g0 wolf(own,d4) r4-13 > walk r14-25 > camp g3 gem_+gold(mid,d14) r26-30 > walk r31-33 > fight r34 > walk r35-42 > recall r43-48 > walk r49-60
- Issa3: walk r1-4 > camp g0 wolf(own,d4) r5-13 > walk r14-20 > camp g3 gem_+gold(mid,d14) r21-32 > fight r33-40 > recall r43-48 > walk r49-59 > camp g0 wolf(own,d4) r60
- key events: r20 capture Stel1 44; r20 recall Stel1 44; r29 tribute Stel1 44; r37 recall Ren0 0; r43 recall Issa3 0; r43 recall Cass2 0; r60 capture Stel1 48
**uni** (side b) vs mite, match `e2e84b09`, loss:
- Cass4: walk r1-13 > camp g3 gem_+gold(mid,d13) r14-21 > fight r24 > walk r25-31 > fight r32-37 > fight r39-40 > recall r42-47 > walk r48-60
- Issa5: walk r1-5 > camp g1 wolf(own,d4) r6-16 > capture r17-22 > walk r23-25 > camp g5 wolf(own,d12) r26-36 > recall r38-43 > walk r44-50 > tribute r51-54 > walk r55-60
- Stel6: walk r1-6 > camp g1 wolf(own,d4) r7-16 > capture r17-22 > walk r23-27 > camp g2 gem_+gold(mid,d14) r28-36 > fight r38 > camp g2 gem_+gold(mid,d14) r41-42 > fight r43 > recall r44-49 > walk r50-54 > tribute r55-58 > walk r59-60
- Varg7: walk r1-6 > camp g1 wolf(own,d4) r7-15 > walk r16-22 > camp g5 wolf(own,d12) r23-46 > recall r47 > cap+recall r48-51 > capture r52 > walk r53-56 > tribute r57-60
- key events: r22 capture Issa5 22; r22 capture Stel6 22; r38 recall Issa5 22; r42 recall Cass4 0; r44 recall Stel6 22; r47 recall Varg7 0; r51 tribute Issa5 22; r52 capture Varg7 44; r55 tribute Stel6 22; r57 tribute Varg7 44
**mite** (side a) vs Intercontinental Fish, match `04cf1ea1`, loss:
- Ren0: walk r1-4 > camp g0 wolf(own,d4) r5-14 > capture r15-16 > walk r17-20 > camp g4 wolf(own,d12) r21-35 > recall r37-42 > walk r43-53 > fight r54 > walk r55-59 > capture r60
- Stel1: walk r1-4 > camp g0 wolf(own,d4) r5-13 > capture r16-19 > recall r20 > cap+recall r21-24 > walk r25-28 > tribute r29-34 > walk r35-42 > camp g2 gem_+gold(mid,d13) r43 > fight r45 > walk r46-50 > fight r51 > camp g2 gem_+gold(mid,d13) r52 > fight r54 > walk r55-58 > camp g3 gem_+gold(mid,d14) r59 > walk r60
- Cass2: walk r1-3 > camp g0 wolf(own,d4) r4-13 > walk r14-25 > camp g3 gem_+gold(mid,d14) r26-44 > walk r45-50 > fight r51 > camp g2 gem_+gold(mid,d13) r52 > walk r53-55 > recall r56-60
- Issa3: walk r1-4 > camp g0 wolf(own,d4) r5-13 > walk r14-20 > camp g3 gem_+gold(mid,d14) r21-44 > fight r47 > fight r49-50 > camp g2 gem_+gold(mid,d13) r51-52 > capture r53 > fight r54 > capture r55 > recall r56 > cap+recall r57-60
- key events: r20 capture Stel1 44; r20 recall Stel1 44; r29 tribute Stel1 44; r37 recall Ren0 0; r56 recall Issa3 0; r56 recall Cass2 0; r59 capture Issa3 48
**uni** (side b) vs Intercontinental Fish, match `eab84102`, win:
- Stel4: walk r1-3 > camp g1 wolf(own,d4) r4-14 > walk r15-21 > camp g3 gem_+gold(mid,d13) r22-44 > capture r46-52 > walk r53-60
- Varg5: walk r1-5 > camp g1 wolf(own,d4) r6-14 > capture r15-20 > recall r22-27 > walk r28-41 > camp g5 wolf(own,d12) r42-56 > recall r57 > cap+recall r58-60
- Tavi6: walk r1-2 > camp g1 wolf(own,d4) r3-13 > walk r14-20 > camp g5 wolf(own,d12) r21 > camp g2 gem_+gold(mid,d14) r24-53 > capture r55-60
- key events: r20 capture Varg5 44; r22 recall Varg5 44; r52 capture Stel4 48; r57 recall Varg5 44

#### collision
**uni** (side a) vs mite, match `e9c3f66b`, win:
- Tavi0: walk r1-3 > camp g0 wolf(own,d3) r4-9 > walk r10-14 > camp g2 wolf(own,d8) r15-21 > walk r22-24 > camp g4 wolf(own,d12) r25-34 > walk r35-42 > fight r43 > fight r46 > fight r48 > fight r51-53 > fight r55 > walk r56-58 > fight r59 > walk r60
- Stel1: walk r1 > camp g0 wolf(own,d3) r2-10 > walk r11-13 > camp g2 wolf(own,d8) r14-22 > walk r23-26 > camp g10 gold(own,d10) r27 > camp g4 wolf(own,d12) r30-34 > camp g10 gold(own,d10) r35 > capture r38-43 > camp g12 gold(own,d15) r44 > camp g6 wolf(mid,d17) r46 > walk r47-50 > fight r51-54 > fight r57-60
- Ren2: walk r1 > camp g0 wolf(own,d3) r2-9 > capture r10-16 > camp g2 wolf(own,d8) r19-22 > capture r23 > recall r24 > cap+recall r25-28 > capture r29 > walk r30-39 > capture r40 > walk r41-49 > fight r50-51 > fight r54-56 > fight r58 > walk r59-60
- key events: r16 capture Ren2 22; r24 recall Ren2 22; r29 capture Ren2 22; r44 capture Stel1 22
**mite** (side b) vs uni, match `e9c3f66b`, loss:
- Varg3: walk r1-5 > camp g1 wolf(own,d3) r6-10 > walk r11-15 > camp g3 wolf(own,d8) r16-22 > walk r23-25 > camp g5 wolf(own,d12) r26-38 > capture r39-44 > walk r45-53 > camp g12 gold(enemy,d19) r54 > fight r55 > camp g12 gold(enemy,d19) r56 > fight r57-60
- Ryth4: walk r1-5 > camp g1 wolf(own,d3) r6-10 > walk r11-13 > camp g3 wolf(own,d8) r14-22 > capture r23-28 > walk r29-38 > tribute r39-41 > camp g7 wolf(mid,d17) r42 > camp g12 gold(enemy,d19) r43 > camp g7 wolf(mid,d17) r44-48 > camp g12 gold(enemy,d19) r51 > fight r52 > walk r53-57 > recall r58-60
- Cass5: walk r1-2 > camp g1 wolf(own,d3) r3-9 > walk r10-15 > camp g3 wolf(own,d8) r16-21 > walk r22-25 > camp g5 wolf(own,d12) r26-37 > walk r38-53 > dead r54-60
- Issa6: walk r1-3 > camp g1 wolf(own,d3) r4-10 > capture r11-16 > walk r17-26 > tribute r27-29 > camp g7 wolf(mid,d17) r30-47 > fight r50-53 > dead r54-60
- key events: r16 capture Issa6 22; r27 tribute Issa6 22; r28 capture Ryth4 22; r39 tribute Ryth4 22; r44 capture Varg3 22; r54 death Cass5; r54 death Issa6; r58 recall Ryth4 0
**mite** (side b) vs Intercontinental Fish, match `bf3fc10f`, win:
- Varg4: walk r1-5 > camp g1 wolf(own,d3) r6-10 > walk r11-15 > camp g3 wolf(own,d8) r16-22 > walk r23-25 > camp g5 wolf(own,d12) r26-38 > capture r39-44 > walk r45-52 > fight r53-57 > fight r59 > walk r60
- Ryth5: walk r1-5 > camp g1 wolf(own,d3) r6-10 > walk r11-13 > camp g3 wolf(own,d8) r14-22 > capture r23-28 > walk r29-37 > fight r38 > tribute r40-42 > camp g7 wolf(mid,d17) r43-45 > camp g12 gold(enemy,d19) r46 > camp g6 wolf(mid,d17) r49-50 > fight r53-54 > fight r56-60
- Cass6: walk r1-2 > camp g1 wolf(own,d3) r3-9 > walk r10-15 > camp g3 wolf(own,d8) r16-21 > walk r22-25 > camp g5 wolf(own,d12) r26-37 > walk r38-54 > fight r55 > fight r58 > fight r60
- Issa7: walk r1-3 > camp g1 wolf(own,d3) r4-10 > capture r11-16 > walk r17-26 > tribute r27-29 > camp g7 wolf(mid,d17) r30-44 > walk r45-47 > camp g7 wolf(mid,d17) r48-50 > fight r51-52 > fight r54-60
- key events: r16 capture Issa7 22; r27 tribute Issa7 22; r28 capture Ryth5 22; r40 tribute Ryth5 22; r44 capture Varg4 22
**uni** (side b) vs Intercontinental Fish, match `37e16f73`, win:
- Stel4: walk r1-2 > camp g1 wolf(own,d3) r3-10 > walk r11-13 > camp g3 wolf(own,d8) r14-23 > walk r24-26 > camp g5 wolf(own,d12) r27-36 > capture r39-44 > camp g13 gold(own,d15) r45 > camp g7 wolf(mid,d17) r47-54 > walk r55-58 > tribute r59-60
- Pris5: walk r1 > camp g1 wolf(own,d3) r2-10 > walk r11-14 > camp g3 wolf(own,d8) r15-22 > walk r23-25 > camp g11 gold(own,d10) r26 > camp g5 wolf(own,d12) r28-36 > walk r37-41 > camp g7 wolf(mid,d17) r42-53 > capture r56-60
- Ren6: walk r1 > camp g1 wolf(own,d3) r2-9 > capture r10-16 > camp g3 wolf(own,d8) r17 > walk r18-20 > camp g3 wolf(own,d8) r21-22 > capture r23 > recall r24 > cap+recall r25-28 > capture r29 > walk r30-43 > fight r44 > fight r46 > fight r48-54 > walk r55-59 > recall r60
- key events: r16 capture Ren6 22; r24 recall Ren6 22; r29 capture Ren6 22; r45 capture Stel4 22; r59 tribute Stel4 22; r60 recall Ren6 44

#### corners
**mite** (side a) vs uni, match `265a46b9`, win:
- Varg0: walk r1-24 > capture r25-26 > fight r27-29 > capture r31 > camp g0 gem_(mid,d17) r32 > capture r33-39 > tribute r41-46 > camp g3 gem_(mid,d19) r47 > fight r50 > walk r51-56 > recall r57-60
- Stel1: walk r1-23 > camp g0 gem_(mid,d17) r24 > fight r27 > walk r28-30 > camp g0 gem_(mid,d17) r31-32 > fight r35-36 > walk r37-39 > fight r40 > walk r41-43 > recall r44-49 > walk r50-60
- Cass2: walk r1-18 > camp g0 gem_(mid,d17) r19 > walk r20-24 > camp g0 gem_(mid,d17) r25 > walk r26-36 > fight r37-45 > dead r46-60
- Issa3: walk r1-3 > camp g6 wolf(own,d4) r4-16 > walk r17-21 > camp g24 elk(own,d12) r22-30 > recall r32-37 > walk r38-45 > dead r46-60
- Ryth4: walk r1-25 > camp g0 gem_(mid,d17) r26 > capture r27-31 > tribute r32-36 > fight r37 > camp g2 gem_(mid,d17) r39-43 > camp g3 gem_(mid,d19) r44-47 > camp g2 gem_(mid,d17) r48-51 > fight r53 > camp g2 gem_(mid,d17) r54 > fight r57-59 > walk r60
- Ren5: walk r1-3 > camp g6 wolf(own,d4) r4-16 > capture r17-22 > walk r23-38 > tribute r39-41 > camp g2 gem_(mid,d17) r42-43 > camp g3 gem_(mid,d19) r44-51 > capture r52-54 > fight r55 > capture r56 > fight r57-58 > tribute r60
- key events: r22 capture Ren5 22; r31 capture Ryth4 48; r32 recall Issa3 0; r32 tribute Ryth4 48; r39 capture Varg0 48; r39 tribute Ren5 22; r41 tribute Varg0 48; r44 recall Stel1 0; r46 death Cass2; r46 death Issa3; r57 capture Ren5 48; r57 recall Varg0 0; r60 tribute Ren5 48
**uni** (side b) vs mite, match `265a46b9`, loss:
- Ryth6: walk r1-4 > camp g7 wolf(own,d4) r5 > walk r6-8 > camp g7 wolf(own,d4) r9-17 > capture r18-23 > walk r24-41 > camp g3 gem_(mid,d17) r42 > fight r45 > walk r46-49 > fight r50 > fight r53 > walk r54-56 > fight r57-59 > walk r60
- Stel7: walk r1-18 > camp g0 gem_(mid,d19) r19-21 > fight r24 > fight r27 > walk r28-30 > fight r31-32 > recall r35-40 > walk r41-56 > fight r57 > fight r59 > walk r60
- Pris8: walk r1-15 > camp g1 gem_(mid,d17) r16-24 > walk r25-28 > fight r29 > fight r32 > walk r33-37 > fight r38 > fight r40 > fight r43-46 > recall r47-52 > walk r53-60
- Ren9: walk r1-4 > camp g7 wolf(own,d4) r5-16 > walk r17-36 > fight r37 > walk r38-46 > fight r47 > walk r48-52 > fight r53 > fight r55 > walk r56-58 > fight r59 > walk r60
- Tavi10: walk r1-17 > camp g1 gem_(mid,d17) r18-22 > walk r23-27 > fight r28 > walk r29-31 > fight r32 > fight r35-37 > fight r39-42 > fight r44 > recall r46-51 > walk r52-60
- key events: r23 capture Ryth6 22; r35 recall Stel7 0; r46 recall Tavi10 0; r47 recall Pris8 0
**mite** (side a) vs Intercontinental Fish, match `a19f0480`, loss:
- Varg0: walk r1-23 > fight r24-29 > walk r30-33 > recall r34-39 > walk r40-59 > camp g2 gem_(mid,d17) r60
- Stel1: walk r1-22 > camp g1 gem_(mid,d19) r23-24 > fight r27-28 > fight r31-33 > walk r34-38 > fight r39-40 > dead r42-60
- Cass2: walk r1-20 > camp g1 gem_(mid,d19) r21 > fight r24 > fight r26-29 > fight r31 > walk r32-36 > camp g3 gem_(mid,d19) r37 > walk r38-42 > fight r43 > fight r45 > walk r46-51 > fight r52 > camp g2 gem_(mid,d17) r53-60
- Issa3: walk r1-3 > camp g6 wolf(own,d4) r4-16 > walk r17-21 > camp g24 elk(own,d12) r22-30 > recall r32-37 > walk r38-57 > fight r58 > camp g2 gem_(mid,d17) r59-60
- Ryth4: walk r1-26 > fight r27-29 > camp g3 gem_(mid,d19) r31 > fight r32-33 > fight r35 > walk r36-38 > fight r39 > camp g2 gem_(mid,d17) r40-41 > fight r42-43 > walk r44-46 > fight r47 > walk r48-51 > recall r52-57 > walk r58-60
- Ren5: walk r1-3 > camp g6 wolf(own,d4) r4-16 > capture r17-22 > walk r23-41 > fight r42-43 > fight r46-48 > fight r50 > recall r52-57 > walk r58-60
- key events: r22 capture Ren5 22; r32 recall Issa3 0; r34 recall Varg0 0; r42 death Stel1; r52 recall Ryth4 0; r52 recall Ren5 22
**uni** (side b) vs Intercontinental Fish, match `373814ef`, loss:
- Will6: walk r1-4 > camp g7 wolf(own,d4) r5-18 > walk r19-35 > fight r36-37 > walk r38-44 > fight r45-46 > walk r47-51 > fight r52-53 > walk r54-57 > recall r58-60
- Ryth7: walk r1-15 > camp g1 gem_(mid,d17) r16 > walk r17-19 > camp g1 gem_(mid,d17) r20 > fight r21-26 > walk r27-31 > fight r32 > walk r33-36 > fight r37-38 > walk r39-42 > camp g1 gem_(mid,d17) r43 > walk r44-49 > fight r50 > camp g1 gem_(mid,d17) r51 > fight r53-55 > walk r56-58 > fight r59 > walk r60
- Ren8: walk r1-15 > camp g3 gem_(mid,d17) r16 > walk r17-20 > fight r21-26 > walk r27-30 > fight r31-34 > walk r35-38 > recall r39-44 > walk r45-57 > fight r58 > fight r60
- Varg9: walk r1-5 > camp g7 wolf(own,d4) r6-17 > capture r18-24 > walk r25-58 > fight r59-60
- Tavi10: walk r1-18 > camp g0 gem_(mid,d19) r19 > fight r21-24 > fight r27 > fight r30-37 > recall r40-45 > walk r46-60
- key events: r24 capture Varg9 22; r39 recall Ren8 0; r40 recall Tavi10 0; r58 recall Will6 0

#### elkring
**mite** (side a) vs uni, match `3e165d6b`, win:
- Varg0: walk r1-19 > camp g6 elk+gold(own,d15) r20-49 > walk r50-52 > recall r53-58 > walk r59-60
- Stel1: walk r1-4 > camp g0 elk+gold(own,d2) r5-12 > walk r13-15 > camp g2 elk+gold(own,d5) r16-25 > walk r26-31 > camp g4 elk+gold(own,d8) r32-41 > walk r42-44 > capture r45-49 > walk r50-59 > tribute r60
- Cass2: walk r1-3 > camp g0 elk+gold(own,d2) r4-10 > walk r11-13 > camp g2 elk+gold(own,d5) r14-23 > walk r24-31 > camp g4 elk+gold(own,d8) r32-41 > walk r42-48 > camp g9 elk+gold(own,d15) r49-60
- Issa3: walk r1 > camp g0 elk+gold(own,d2) r2-12 > capture r13-18 > walk r19-31 > tribute r32-35 > recall r36-41 > walk r42-44 > capture r45-46 > walk r47-54 > camp g9 elk+gold(own,d15) r55-60
- Ryth4: walk r1-3 > camp g0 elk+gold(own,d2) r4-11 > walk r12-15 > camp g2 elk+gold(own,d5) r16-25 > walk r26-32 > camp g4 elk+gold(own,d8) r33-43 > capture r44-45 > capture r47 > walk r48-58 > camp g9 elk+gold(own,d15) r59-60
- Ren5: walk r1 > camp g0 elk+gold(own,d2) r2-12 > camp g2 elk+gold(own,d5) r14-25 > capture r26-31 > walk r32-41 > tribute r42-45 > recall r46-51 > walk r52-58 > capture r59 > walk r60
- key events: r18 capture Issa3 36; r31 capture Ren5 36; r32 tribute Issa3 36; r36 recall Issa3 0; r42 tribute Ren5 36; r46 recall Ren5 0; r49 capture Stel1 36; r53 recall Varg0 0; r60 tribute Stel1 36
**uni** (side b) vs mite, match `3e165d6b`, loss:
- Vesp6: walk r1-3 > camp g1 elk+gold(own,d2) r4-10 > camp g3 elk+gold(own,d5) r13-23 > walk r24-28 > camp g5 elk+gold(own,d8) r29-39 > recall r40-45 > walk r46-60
- Stel7: walk r1 > camp g1 elk+gold(own,d2) r2-10 > camp g3 elk+gold(own,d5) r13-23 > walk r24-28 > camp g5 elk+gold(own,d8) r29-39 > walk r40-45 > camp g8 elk+gold(own,d15) r46 > walk r47-49 > camp g8 elk+gold(own,d15) r50-60
- Pris8: walk r1 > camp g1 elk+gold(own,d2) r2-10 > camp g3 elk+gold(own,d5) r12-23 > walk r24-29 > camp g5 elk+gold(own,d8) r30-39 > walk r40-46 > camp g8 elk+gold(own,d15) r47-59 > walk r60
- Ren9: walk r1 > camp g1 elk+gold(own,d2) r2-10 > capture r11-17 > walk r18-22 > camp g3 elk+gold(own,d5) r23 > walk r24-30 > camp g5 elk+gold(own,d8) r31-39 > capture r40 > recall r41 > cap+recall r42-45 > capture r46 > walk r47-60
- Tavi10: walk r1 > camp g1 elk+gold(own,d2) r2-10 > camp g3 elk+gold(own,d5) r13-22 > capture r24-30 > walk r31-43 > camp g8 elk+gold(own,d15) r44-59 > walk r60
- key events: r17 capture Ren9 36; r30 capture Tavi10 36; r40 recall Vesp6 0; r41 recall Ren9 36; r46 capture Ren9 36
**mite** (side a) vs Intercontinental Fish, match `a8ac14b5`, win:
- Varg0: walk r1-19 > camp g6 elk+gold(own,d15) r20-43 > walk r44-46 > recall r47-52 > walk r53-60
- Stel1: walk r1-4 > camp g0 elk+gold(own,d2) r5-12 > camp g2 elk+gold(own,d5) r15-23 > walk r24-31 > camp g4 elk+gold(own,d8) r32-41 > walk r42-44 > capture r45-49 > walk r50-59 > tribute r60
- Cass2: walk r1-3 > camp g0 elk+gold(own,d2) r4-10 > walk r11-14 > camp g2 elk+gold(own,d5) r15-23 > walk r24-31 > camp g4 elk+gold(own,d8) r32-41 > walk r42-48 > camp g9 elk+gold(own,d15) r49-60
- Issa3: walk r1 > camp g0 elk+gold(own,d2) r2-12 > capture r13-18 > walk r19-31 > tribute r32-35 > recall r36-41 > walk r42-44 > capture r45-46 > walk r47-54 > camp g9 elk+gold(own,d15) r55-60
- Ryth4: walk r1-3 > camp g0 elk+gold(own,d2) r4-11 > walk r12-15 > camp g2 elk+gold(own,d5) r16-24 > walk r25-32 > camp g4 elk+gold(own,d8) r33-43 > capture r44-45 > capture r47 > walk r48-58 > camp g9 elk+gold(own,d15) r59-60
- Ren5: walk r1 > camp g0 elk+gold(own,d2) r2-12 > camp g2 elk+gold(own,d5) r14-24 > capture r25-30 > walk r31-40 > tribute r41-44 > recall r45-49 > fight r50-52 > walk r53-58 > camp g6 elk+gold(own,d15) r59 > walk r60
- key events: r18 capture Issa3 36; r30 capture Ren5 36; r32 tribute Issa3 36; r36 recall Issa3 0; r41 tribute Ren5 36; r45 recall Ren5 0; r47 recall Varg0 0; r49 capture Stel1 36; r60 tribute Stel1 36
**uni** (side b) vs Intercontinental Fish, match `bb593284`, loss:
- Stel6: walk r1-2 > camp g1 elk+gold(own,d2) r3-11 > walk r12-14 > camp g3 elk+gold(own,d5) r15-25 > walk r26-32 > camp g7 elk+gold(own,d15) r33-43 > walk r44-48 > camp g9 elk+gold(enemy,d22) r49 > fight r52-53 > walk r54-56 > fight r57-60
- Pris7: walk r1 > camp g1 elk+gold(own,d2) r2-10 > walk r11-13 > camp g3 elk+gold(own,d5) r14-25 > walk r26-32 > camp g7 elk+gold(own,d15) r33 > walk r34-36 > camp g7 elk+gold(own,d15) r37-42 > walk r43-48 > fight r49-54 > fight r57-59 > walk r60
- Will8: walk r1-2 > camp g1 elk+gold(own,d2) r3-11 > camp g3 elk+gold(own,d5) r13-25 > walk r26-34 > camp g7 elk+gold(own,d15) r35-42 > walk r43-47 > camp g9 elk+gold(enemy,d22) r48 > fight r50-51 > fight r53 > fight r56 > fight r58-59 > walk r60
- Ren9: walk r1 > camp g1 elk+gold(own,d2) r2-11 > capture r12-18 > walk r19-24 > camp g3 elk+gold(own,d5) r25 > walk r26-32 > camp g7 elk+gold(own,d15) r33-42 > capture r43-49 > tribute r52-55 > fight r57 > walk r58-60
- Tavi10: walk r1 > camp g1 elk+gold(own,d2) r2-10 > camp g3 elk+gold(own,d5) r13-24 > capture r26-32 > walk r33-37 > camp g7 elk+gold(own,d15) r38-42 > walk r43-49 > fight r50-53 > walk r54-56 > fight r57-59 > walk r60
- key events: r18 capture Ren9 36; r32 capture Tavi10 36; r49 capture Ren9 36; r52 tribute Ren9 72

#### interlock
**mite** (side b) vs Shawn, match `3425ed50`, win:
- Varg4: walk r1-8 > camp g7 wolf(own,d4) r9-11 > walk r12-15 > camp g9 wolf(own,d10) r16-20 > capture r21-26 > walk r27-31 > capture r32 > walk r33-38 > fight r39 > tribute r40-43 > fight r44-48 > fight r50-52 > walk r53-60
- Ryth5: walk r1-6 > camp g7 wolf(own,d4) r7-11 > walk r12-16 > camp g9 wolf(own,d10) r17-19 > walk r20-23 > camp g1 gem_(own,d14) r24-31 > capture r32-37 > walk r38-43 > fight r44 > fight r47 > tribute r48-56 > fight r59-60
- Cass6: walk r1-12 > camp g9 wolf(own,d10) r13-19 > walk r20-23 > camp g1 gem_(own,d14) r24-30 > camp g11 wolf(own,d17) r33-43 > walk r44-50 > recall r51-56 > walk r57-60
- Issa7: walk r1-3 > camp g7 wolf(own,d4) r4-11 > capture r12-17 > walk r18-24 > tribute r25-28 > walk r29-40 > camp g12 elk(mid,d27) r41-52 > walk r53-55 > recall r56-60
- Ren8: walk r1-3 > camp g7 wolf(own,d4) r4-10 > walk r11-13 > camp g9 wolf(own,d10) r14-19 > camp g1 gem_(own,d14) r22-31 > camp g11 wolf(own,d17) r34-44 > capture r45-50 > walk r51-57 > tribute r58-60
- key events: r17 capture Issa7 22; r25 tribute Issa7 22; r26 capture Varg4 22; r37 capture Ryth5 72; r40 tribute Varg4 22; r48 tribute Ryth5 72; r50 capture Ren8 22; r51 recall Cass6 0; r56 recall Issa7 0; r58 tribute Ren8 22
**uni** (side b) vs hello, match `e7a228c4`, win:
- Ryth5: walk r1-4 > camp g7 wolf(own,d4) r5 > walk r6-9 > camp g7 wolf(own,d4) r10-18 > capture r19-24 > walk r25-27 > camp g9 wolf(own,d10) r28-39 > recall r40 > cap+recall r41-44 > capture r45 > walk r46-60
- Cass6: walk r1-14 > camp g1 gem_(own,d14) r15-23 > walk r24-30 > fight r31-35 > fight r37 > fight r39 > walk r40-42 > recall r43-48 > walk r49-60
- Issa7: walk r1-27 > fight r28-29 > walk r30-32 > fight r33 > walk r34-48 > camp g11 wolf(own,d17) r49-59 > walk r60
- Stel8: walk r1-12 > camp g1 gem_(own,d14) r13-23 > capture r25-32 > fight r35 > fight r38-40 > fight r43 > walk r44-46 > recall r47-52 > walk r53-60
- Ren9: walk r1-3 > camp g7 wolf(own,d4) r4-17 > walk r18-22 > camp g1 gem_(own,d14) r23 > walk r24-26 > camp g9 wolf(own,d10) r27-38 > walk r39-45 > fight r46 > fight r48 > walk r49-59 > fight r60
- key events: r24 capture Ryth5 22; r31 capture Stel8 72; r40 recall Ryth5 22; r43 recall Cass6 0; r45 capture Ryth5 22; r47 recall Stel8 72

## 6. Fight maps: centre, first contact, first fight (Q5)

Table C: "centre arrival" = first round a champion is within 4 BFS steps of the map centre; "captures before contact" = rewards collected before the first champion-vs-champion damage; "fight window" = contiguous damage exchanges (gap <= 5 rounds); deaths counted inside the window plus 2 rounds.

| map | team | game | opp | centre arrival r (who) | captures before contact | first contact r (who, kind) | contact pos dist-to-centre | fight window | my deaths | enemy deaths | deaths by r60 | result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| collision | mite | e9c3f66b | uni | r25 Issa6 | 2 | r43 Ryth4 enemy | 3 | r43-63 | 3 | 0 | 2 | loss |
| collision | mite | bf3fc10f | Intercontine | r25 Issa7 | 2 | r38 Ryth5 enemy | 2 | r38-38 | 0 | 0 | 0 | win |
| collision | mite | 30b9ea2d | hello | r25 Issa7 | 2 | r29 Issa7 by_enemy | 4 | r29-38 | 0 | 0 | 0 | loss |
| collision | mite | d1a5da76 | ❤️Quantom❤️ | r27 Ryth1 | 2 | r41 Ryth1 enemy | 3 | r41-53 | 0 | 1 | 0 | win |
| collision | mite | a340814f | VeryGood | r25 Issa7 | 2 | r36 Ryth5 enemy | 1 | r36-57 | 1 | 0 | 1 | loss |
| collision | mite | 4224353c | procless | r25 Issa7 | 3 | r51 Ryth5 enemy | 2 | r51-51 | 0 | 0 | 0 | win |
| collision | uni | e9c3f66b | mite | r39 Tavi0 | 2 | r43 Tavi0 by_enemy | 0 | r43-63 | 0 | 3 | 0 | win |
| collision | uni | 37e16f73 | Intercontine | r41 Ren6 | 2 | r44 Ren6 enemy | 0 | r44-54 | 0 | 1 | 0 | win |
| collision | uni | 1c547a16 | hello | r38 Tavi6 | 3 | r44 Ren5 enemy | 0 | r44-58 | 0 | 1 | 0 | win |
| collision | uni | f63abb8a | PTN Hyperion | r38 Tavi6 | 2 | r42 Tavi6 enemy | 1 | r42-56 | 0 | 2 | 0 | win |
| collision | uni | 626278d9 | VeryGood | r38 Tavi6 | 2 | r39 Tavi6 by_enemy | 2 | r39-54 | 0 | 2 | 0 | win |
| collision | uni | e5dc1b72 | Full Damage | r42 Ren5 | 2 | r41 Stel3 enemy | 5 | r41-53 | 0 | 1 | 0 | loss |
| corners | mite | 265a46b9 | uni | r17 Cass2 | 1 | r24 Stel1 enemy | 3 | r24-69 | 2 | 0 | 2 | win |
| corners | mite | a19f0480 | Intercontine | r17 Cass2 | 0 | r21 Cass2 enemy | 0 | r21-52 | 1 | 1 | 1 | loss |
| corners | mite | 8f7d1b55 | hello | r17 Cass2 | 0 | r20 Stel1 enemy | 3 | r20-63 | 4 | 1 | 2 | loss |
| corners | mite | d6b437f2 | Shawn | r17 Cass7 | 0 | r19 Cass7 enemy | 2 | r19-62 | 1 | 3 | 1 | win |
| corners | mite | 9c6eefab | ❤️Quantom❤️ | r17 Cass8 | 0 | r22 Stel7 enemy | 1 | r22-24 | 0 | 0 | 0 | win |
| corners | mite | 14b7f542 | VeryGood | r17 Cass2 | 0 | r21 Stel1 enemy | 2 | r21-48 | 0 | 0 | 0 | loss |
| corners | uni | 265a46b9 | mite | r17 Stel7 | 1 | r24 Stel7 by_enemy | 5 | r24-69 | 0 | 2 | 0 | loss |
| corners | uni | 373814ef | Intercontine | r15 Ren8 | 0 | r21 Ryth7 by_enemy | 4 | r21-38 | 0 | 0 | 0 | loss |
| corners | uni | a1a3769a | hello | r16 Ryth7 | 0 | r22 Stel8 by_enemy | 5 | r22-59 | 4 | 0 | 4 | loss |
| corners | uni | 502126ec | Shawn | r15 Cass2 | 0 | r19 Stel5 by_enemy | 3 | r19-37 | 5 | 0 | 5 | loss |
| corners | uni | 940529ee | PTN Hyperion | r16 Ryth2 | 0 | r19 Tavi4 enemy | 6 | r19-55 | 4 | 0 | 4 | loss |
| corners | uni | 9d113be1 | VeryGood | r16 Ryth8 | 1 | r23 Ryth8 enemy | 1 | r23-45 | 3 | 0 | 3 | loss |
| elkring | mite | 3e165d6b | uni | r23 Issa3 | 3 | r66 Ren5 by_enemy | 6 | r66-70 | 0 | 0 | 0 | win |
| elkring | mite | a8ac14b5 | Intercontine | r23 Issa3 | 3 | r50 Ren5 by_enemy | 7 | r50-52 | 0 | 0 | 0 | win |
| elkring | mite | 014dcd6f | hello | r23 Issa3 | 3 | none<r70 | - | - | - | - | 0 | win |
| elkring | mite | a3d60396 | Shawn | r19 Issa8 | 4 | r56 Stel6 enemy | 3 | r56-70 | 3 | 1 | 0 | loss |
| elkring | mite | ff7099ce | ❤️Quantom❤️ | r19 Issa8 | 2 | r50 Ryth9 enemy | 7 | r50-59 | 0 | 0 | 0 | win |
| elkring | mite | 2f0076ab | VeryGood | r23 Issa3 | 3 | r59 Stel1 enemy | 6 | r59-60 | 0 | 0 | 0 | win |
| elkring | uni | 3e165d6b | mite | r27 Vesp6 | 3 | r66 Ren9 enemy | 4 | r66-70 | 0 | 0 | 0 | loss |
| elkring | uni | bb593284 | Intercontine | r31 Will8 | 2 | r49 Pris7 enemy | 3 | r49-70 | 0 | 3 | 0 | loss |
| elkring | uni | ba31bc58 | hello | r24 Tavi9 | 2 | r52 Ryth7 by_enemy | 6 | r52-52 | 0 | 0 | 0 | win |
| elkring | uni | 8534cb83 | Shawn | - | 4 | r53 Stel0 by_enemy | 5 | r53-70 | 4 | 1 | 2 | loss |
| elkring | uni | 1bdbee78 | PTN Hyperion | r24 Pris10 | 4 | r68 Ryth9 by_enemy | 0 | r68-68 | 0 | 0 | 0 | win |
| elkring | uni | 42f6a030 | VeryGood | r28 Tavi7 | 3 | r61 Ren10 by_enemy | 1 | r61-70 | 0 | 1 | 0 | win |
| interlock | mite | 3425ed50 | Shawn | r23 Issa7 | 3 | r39 Varg4 by_enemy | 0 | r39-52 | 0 | 0 | 0 | win |
| interlock | mite | 62298bb6 | ❤️Quantom❤️ | r23 Issa7 | 3 | r43 Ryth5 enemy | 1 | r43-49 | 0 | 0 | 0 | win |
| interlock | mite | 61d896ac | VeryGood | r23 Issa8 | 3 | r38 Varg5 by_enemy | 0 | r38-62 | 0 | 0 | 0 | win |
| interlock | mite | 314ba251 | Boost | r23 Issa7 | 3 | r38 Ryth5 enemy | 6 | r38-69 | 0 | 3 | 0 | win |
| interlock | mite | fa3ab409 | geese geese  | r24 Ryth6 | 3 | r41 Ryth6 enemy | 3 | r41-41 | 0 | 0 | 1 | win |
| interlock | mite | 0534793d | Mate in One | r24 Ryth6 | 2 | r37 Ryth6 enemy | 1 | r37-37 | 0 | 0 | 0 | loss |
| interlock | uni | e7a228c4 | hello | r17 Issa7 | 1 | r28 Issa7 by_enemy | 0 | r28-48 | 0 | 0 | 0 | win |
| interlock | uni | b0776150 | PTN Hyperion | r17 Issa7 | 2 | r33 Cass6 by_enemy | 0 | r33-45 | 2 | 0 | 2 | win |
| interlock | uni | 60b0d7a9 | VeryGood | r17 Issa7 | 1 | r31 Issa7 by_enemy | 0 | r31-31 | 0 | 0 | 0 | loss |
| interlock | uni | 9a14a323 | Boost | r17 Issa6 | 0 | r23 Issa6 by_enemy | 5 | r23-23 | 0 | 0 | 2 | loss |
| interlock | uni | c0a2bf6b | geese geese  | r17 Issa7 | 2 | r39 Cass6 by_enemy | 0 | r39-39 | 0 | 0 | 0 | win |
| interlock | uni | 6cb958d0 | Mate in One | r11 Issa6 | 2 | r41 Ren7 enemy | 0 | r41-52 | 0 | 0 | 0 | loss |
| packs | mite | e2e84b09 | uni | r20 Issa3 | 1 | r24 Issa3 by_enemy | 2 | r24-24 | 0 | 0 | 0 | win |
| packs | mite | 04cf1ea1 | Intercontine | r20 Issa3 | 1 | r43 Stel1 enemy | 1 | r43-56 | 0 | 2 | 0 | loss |
| packs | mite | 87fb83cb | hello | r20 Issa3 | 1 | r35 Issa3 by_enemy | 1 | r35-48 | 2 | 0 | 2 | win |
| packs | mite | 4ffb04fa | ❤️Quantom❤️ | r20 Stel4 | 2 | r44 Stel4 enemy | 0 | r44-48 | 0 | 0 | 0 | win |
| packs | mite | c5ff8931 | VeryGood | r20 Issa3 | 1 | r27 Issa3 enemy | 1 | r27-32 | 0 | 0 | 0 | win |
| packs | mite | 5b29ede0 | procless | r20 Issa3 | 1 | r26 Issa3 enemy | 1 | r26-30 | 0 | 0 | 0 | win |
| packs | uni | e2e84b09 | mite | r23 Cass4 | 2 | r24 Cass4 enemy | 3 | r24-24 | 0 | 0 | 0 | loss |
| packs | uni | eab84102 | Intercontine | r32 Tavi6 | 2 | none<r70 | - | - | - | - | 0 | win |
| packs | uni | 836e6655 | hello | r42 Ren5 | 2 | r41 Ren5 enemy | 4 | r41-64 | 0 | 0 | 0 | loss |
| packs | uni | 424c9ce5 | Shawn | r68 Stel2 | 5 | r61 Stel2 enemy | 5 | r61-69 | 0 | 0 | 0 | loss |
| packs | uni | b469f4c8 | VeryGood | r41 Stel4 | 1 | r38 Stel4 enemy | 5 | r38-61 | 0 | 2 | 0 | win |
| packs | uni | 09882a3a | Full Damage | r47 Stel4 | 1 | r42 Stel4 enemy | 4 | r42-58 | 0 | 2 | 0 | win |
| lanes | mite | c8d4cf63 | uni | - | 5 | r65 Stel1 by_enemy | 8 | r65-70 | 1 | 0 | 0 | win |
| lanes | mite | 8bf100be | Intercontine | r78 Cass2 | 5 | none<r70 | - | - | - | - | 0 | win |
| lanes | mite | e4ac414e | hello | - | 5 | none<r70 | - | - | - | - | 0 | win |
| lanes | mite | 77144bd7 | Shawn | - | 5 | none<r70 | - | - | - | - | 0 | win |
| lanes | mite | 72b54436 | ❤️Quantom❤️ | r80 Cass2 | 5 | none<r70 | - | - | - | - | 0 | loss |
| lanes | mite | cf07481e | VeryGood | - | 5 | none<r70 | - | - | - | - | 0 | win |
| lanes | uni | c8d4cf63 | mite | r53 Tavi10 | 6 | r65 Stel7 enemy | 6 | r65-70 | 0 | 1 | 0 | loss |
| lanes | uni | 3e800856 | PTN Hyperion | r61 Ren4 | 6 | r66 Cass0 by_enemy | 6 | r66-70 | 0 | 0 | 0 | loss |
| lanes | uni | 3d6515e6 | VeryGood | r50 Ryth6 | 6 | r55 Marc10 enemy | 5 | r55-70 | 1 | 2 | 0 | win |
| lanes | uni | 0c9cfa11 | Full Damage | r50 Ryth6 | 6 | r62 Ryth6 by_enemy | 4 | r62-70 | 0 | 0 | 0 | win |
| lanes | uni | a71493d4 | Boost | r50 Ryth6 | 6 | r59 Tavi11 enemy | 5 | r59-69 | 1 | 1 | 0 | win |
| lanes | uni | d9fd5de8 | geese geese  | r50 Ryth6 | 6 | r51 Ren10 enemy | 10 | r51-69 | 1 | 3 | 0 | win |

Per map:
- **collision** (spawn-to-spawn path 41). Mite farms first: 2 camps (22+22), Issac reaches the mid altar at r25 and tributes r27-30; the rest keep farming wolves d8/d12 and the mid wolf g7 (r30-44). First contact r36-51, usually Ryth engaging near the mid altar (26,21). Mite went 3-3 and lost the first fight badly vs Univardisty (e9c3f66b r43-63: Cassi+Issac dead r54, Varg r63, 0 Univardisty deaths), vs VeryGood (Ryth dead r50). Univardisty farms 3 camps (3 captures) and one recall-shop trip before its 3 casters walk to the centre at r38-42; first contact r39-44 at the centre itself (dist 0-2); it won the first fight in all 6 games (0 own deaths, 1-3 enemy deaths) and went 5-1 on the map.
- **corners** (path 26). Both go almost straight. Mite: Cassi arrives at r17 (0 captures before contact in 5 of 6 games), Varg/Stellar/Ryth r17-25, contact r19-24 next to the centre altar; Issac+Ren bring the wolf's 22 gems at r22-39. Results of Mite's first fight: 1/3 (vs Shawn, won), 2/0 (vs Univardisty, won anyway: Univardisty had 0 captures to tribute and its casters recalled at r35-47), 4/1 (vs hello, lost), 1/1, 0/0, 0/0. Univardisty: 3 casters arrive r15-17, contact r19-24 at dist 1-6 from the centre; first-fight deaths 0/2, 0/0, 4/0, 5/0, 4/0, 3/0 - it lost all 6 games, four of them by losing 3-5 champions before r55 and never tributing.
- **elkring** (path 37). Neither team goes to the centre: Mite's "centre arrival" at r19-23 is Issac walking past it to the mid altar with 36 gems. Both farm 3-4 elk+gold groups before any contact; first contact r49-68 (Mite r50-66, Univardisty r49-68), outside the opening. Mite 5-1, Univardisty 3-3.
- **interlock** (path 34). Mite farms 3 captures (22+22+72 by r38), Issac tributes at the own altar (20,23) at r25-28, contact r37-43 near that altar or the mid elk; 0 own deaths in all 6 first fights, 3 enemy deaths vs Boost. Univardisty sends Issac alone to the centre at r17 (b0776150: Issac walks 20 rounds to the enemy gem cluster g0 d24, hits it once at r21, walks back); first contact r23-41 is Issac/Cassi being hit at the centre with 0-2 captures done; Cassi+Issac die at r43 in b0776150 and r52 in 9a14a323.
- **packs** (path 29, farm map by the earlier classification but with middle clusters): Mite sends Cassi+Issac to the middle gem+gold cluster at r20-21 after the first wolf, contact r24-44 at the cluster (dist 0-2 from centre); first-fight deaths 0/0 x4, 0/2 (vs Intercontinental), 2/0 (vs hello: Cassi+Issac dead r46). Univardisty reaches the middle at r23-47 and fights at r24-61.

## 7. Same opening regardless of opponent? (Q6)

Method (`determinism.py`): mirror side-B positions into the side-A frame and find the first round where the set of (champion type, position) differs between two games of the same team, map and draft; record the distance to the nearest enemy at that round.

- **Mite**: identical through r80 in every pair on rows (5 same-side games) and monolith (5 games). Collision: pairs diverge at r30-45 with an enemy 1-12 tiles away. Corners: r18-20, enemy 4-8 tiles away (the centre fight). Lanes: r43-58, enemy 5-15. Interlock: r31-41 (enemy 4-15). Two exceptions where Mite changes with no enemy in sight: expanse at r16 (enemy 55-62 tiles away; Issac deals 25 instead of 40 damage because Cassi skipped one hit, so Issac instead of Ren ends up on the capture tile - a one-champion swap, the camp order and all later rounds are the same), elkring at r4 (Varg/Stellar one tile apart, enemy 20-22 away), interlock at r6 in fa3ab409/0534793d (Cassi joins the wolf instead of walking to wolf d10, kill r10 instead of r11, enemy 30 away). These are tie-breaks, not plan changes; the camp sequence and capture rounds match within one round.
- **Univardisty**: the draft depends on the opponent (collision: Tavi/Stellar/Ren vs Prism/Stellar/Ren; corners 5 different drafts in 6 games; elkring 5; monolith 4), and the split assignment depends on the draft (who goes alone to the second camp). With the same draft the opening is identical until the enemy is 3-14 tiles away: interlock r21-24, collision r38-41, packs r37, lanes r47-58, expanse r59 (when "hello" walked into its jungle), corners r17.
- Side A vs side B are not mirror images for either team: the spawn tile assignment differs (e.g. Mite's Issac spawns at (6,5) on side B vs the mirror of (6,1) on side A), which shifts a few early steps and on expanse changes who joins the wolf (Stellar joins on side A, kill r12 with 4; goes to the gem cluster on side B, kill r16 with 3).

Where the opponent changes the opening:
- Enemy at the centre early (corners always; packs 87fb83cb "hello" at the cluster r21; interlock 9a14a323 Boost's Prism at r18) -> the fight replaces the cluster farming; Mite's casters who were going to hit the cluster hit champions instead, and Mite starts recalling at r32-45.
- Enemy enters the jungle: collision 30b9ea2d "hello"'s Ren at the mid altar r26 -> Issac tributes r28 and fights r29-38, then recalls at r41 and r51 with 22 gems unbanked (Mite lost that game); expanse 0726cfdf "hello" at Univardisty's wolf r56-60 -> Varg fights instead of starting the gem cluster.
- Nobody comes: the opening runs unchanged to r60+ (rows, monolith, lanes for Mite).

## 8. Mite vs Univardisty, and the rules they follow (Q7)

Measured differences in the opening:

| | Mite | Univardisty |
|---|---|---|
| draft | fixed per map (Varg/Ryth/Cassi+Issac/Ren/Stellar; Tavi on lanes) | changes with the opponent, 2-5 drafts per map |
| r1-10 | everybody to the nearest camp (3-6 hitters), 1-2 exceptions walk to a far target (lanes Varg elk, elkring Varg elk, corners 4 to the centre) | 3 on the nearest camp, 1-2 pre-assigned to the next camp or the centre; casters open fire at range 3-5 from r1-3 |
| first kill | r7-16 (4-11 rounds) | r10-25 (9-19 rounds) |
| capture | 1 champion stays, others leave the same round | 1 champion (2 on rows/packs); tiles sometimes left empty for a round |
| after the first capture | capturer walks to the altar, or recalls from the tile when the recall was planned (packs, rows, lanes) | capturer recalls from the tile (r23-26) to shop, walks back with the gems |
| first tribute | r25-32 on 6 maps, bag 22-44; mid altar on fight maps, own altar on farm maps; rows: none, carries 132 | r50-67 on 6 maps or none; carries 108-154 at r60 |
| shopping | after the recall at r25-33 (packs 150+30, rows 150+120, elkring 150+30+10) | r21-31, right after the first capture and the recall home (150+10, or 150+30+10) |
| where it shops | on the spawn tiles, 98 of 98 purchases | 133 of 142 on spawn; 9 purchases next to spawn or in the field (elkring r21-23, corners) |
| centre on fight maps | corners r17 (4 champions), collision r25 (1 champion with gems), interlock r37-43 (3 captures first) | corners r15-17 (3 casters), collision r38-42 (3 camps first), interlock r17 (Issac alone) |
| first fight by deaths (won / even / lost) | collision 1/3/2; corners 1/3/2; interlock 1/5/0 (never loses a champion); packs 1/4/1 | collision 6/0/0; corners 1/1/4 (3-5 champions lost in 4 games); interlock 0/5/1 (plus Cassi+Issac dead r52 in 9a14a323) |

Opening rules Mite follows (measured = seen in all 6 games of the maps named; inferred = the simplest rule that reproduces it):
1. (measured) Every champion walks to the nearest camp of the farm set at r1; the group stays together until that camp dies (rows, monolith, packs, collision, interlock, elkring (5 of 6), expanse (3 of 4)).
2. (measured) Exceptions are pre-planned per map, not reactive: Varg alone to a far elk on lanes/elkring, Stellar alone to the gem cluster on expanse, 4 champions straight to the centre altar on corners.
3. (measured) The champion standing on the camp tile at the kill stays alone; everybody else leaves that round for the nearest camp that is up (nearest-camp-up rule of the earlier report applies from the first fan-out).
4. (measured) Bigger groups get more champions: 3 on the elk (monolith), 2-3 on the 3-cluster group (interlock), 1 on a single wolf once the first camp is down.
5. (measured) Bank the first bag as soon as there is a route: walk to the middle altar on collision/monolith/elkring (r27-32), to the own altar on interlock/packs (r25-29); on rows/lanes keep the gems and recall only to shop.
6. (measured) Recall is started on the capture tile when the champion is going home anyway (packs r20, rows r28/r54, lanes r51, expanse r33-37), so the 5-round recall overlaps the capture timer.
7. (inferred) Fight maps: go to the middle only with gems to bank or after the own-side camps are done, except corners where the centre clusters are the farm set.
8. (measured leak) A lone champion will keep hitting an elk it cannot kill for 10-30 rounds (elkring Varg r20-49, corners Issac r22-30, interlock Issac r41-52) and then recall with nothing.

Opening rules Univardisty follows:
1. (measured) Draft reacts to the opponent; the first-round split is fixed by role: melee (Ren, Ryth, Varg, Vendetta, Willow, Issac) take the nearest camp; a caster or Cassi is sent alone to the second camp (monolith Stellar d9, expanse Cassi d11, packs Cassi to the middle) or to the centre (interlock Issac, corners Stellar/Prism/Tavi).
2. (measured) Casters start hitting from range 3-5 the moment the camp is in range (r1-3) and step in one tile every few rounds; melee units arrive 2-4 rounds later.
3. (measured) One champion captures; it then recalls from the tile to shop (r23-26) and walks back out with the gems. Captured gems are not banked in the opening: first tribute r50-67 or none on 6 of 9 maps.
4. (measured) After the first camp, champions go to the nearest camp that is up individually (1-2 per camp), which makes the second and third kills slower (collision wolf d8: 8 rounds with 3; interlock wolf d10: 12 rounds with 2) but keeps 5-6 captures going in parallel on lanes (6 captures by r50 vs Mite's 5 by r55).
5. (measured) On fight maps it commits the casters to the centre by r15-17 (corners) or r17 (interlock, Issac) regardless of what the enemy has, and on collision only after 3 camps (r38-42). The corners version lost every game.
6. (inferred) Recall below ~30% hp (earlier report) also governs the opening: corners casters recall at r35-47 after the first exchange, which leaves the centre to Mite.

Numbers to reuse: kill+6 = capture round; one occupant is enough; Mite reaches the first middle altar with 22 gems at r25-27 on collision/monolith; a 6-champion stack kills a wolf in 4 rounds, a 3-champion group in 9-10, a 2-champion group in 15.
