# How study27 fights, next to study26: 155 games vs the top 30, 2026-10-15 12:37 UTC

study27 = study26 + "stack up to 4 champions on camp groups of 3000+ hp, one on smaller camps". 155 unranked games, 58-97 (study26: 150 games, 59-91).

Data: `$S/ws3/selected.json` + `$S/ws3/steps/` (the decode pipeline `dl.sh` died at 136/155 at 12:57; the last 19 were decoded with `$S/ws3/resume.sh`, same steps; all 155 present).
Scripts are the study26 ones in `$S/ws2/scripts_fights/`, now parameterised: `WS=$S/ws3 FIGHTS=$S/ws2/scripts_fights/fights_27.json python3 -I fights_build.py | analyze.py | chase.py | extra.py | timeline.py`
(defaults = study26 paths; `DUMP=file.json` makes `chase.py` / `extra.py` write their raw episodes). Outputs: `fights_27.json`, `out_analyze_27.txt`, `out_chase_27.txt`, `out_extra_27.txt`,
and `compare.py -> out_compare.txt`, which produced every side-by-side table below. Definitions are unchanged from `fights.md` (fight = cluster of champion-on-champion hits within 5 rounds / 8 tiles;
real = >= 1000 damage or a death; n6 = bodies within 6 of the first victim; contact = enemy within 8). Columns: **s27 us** = study27, **s26 us** = study26, **s27 opp** / **s26 opp** = the opponents
in those same games. Counts are in brackets; with ~600 real fights per opener side, a kills-per-fight rate moves by about +-0.04 from sampling alone, a share of 1000-2000 events by +-2-3 points.

**Sample caveats before reading differences.** (1) The map mix is not the same: elkring 9 games (14 in s26), interlock 19 (13), monolith 16 (13), collision 19 (19), corners 19 (17), packs 22 (21).
(2) Four opponents are new (Cabbage 16, Mate in One 28, EMPEROR Tung 30, Palestine 54) replacing SSSA, WHIM, MicroStella (249) and one slot; ranks of the rest shifted. (3) PTN Hyperion starts a
recall on every champion every round (403 recall-start events per 100 rounds vs 5-8 for everyone else), so every opener we land on them is labelled "victim recalling": 18 of our 123 recalling-victim
openers in s27 and 31 of 111 in s26 are that artefact. The "recalling" rows below are read with that in mind.

## 0. Headline table

| | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| games (W-L) | 155 (58-97) | 150 (59-91) | | |
| fights / real fights per game | 15.0 / 7.7 (2324 / 1199) | 14.4 / 7.3 (2158 / 1096) | same games | same games |
| hit first (real fights) | 51% (610/1199) | 52% (575/1096) | 49% | 48% |
| kills / deaths per real fight | 0.51 / 0.74 (612-884) | 0.52 / 0.77 (565-840) | 0.74 / 0.51 | 0.77 / 0.52 |
| damage dealt / taken per real fight | 1077 / 991 | 1104 / 993 | 991 / 1077 | 993 / 1104 |
| opener conversion (kills / deaths in fights this side opened) | 0.68 / 0.59 (n=610) | 0.69 / 0.58 (n=575) | 0.89 / 0.33 (n=589) | 0.97 / 0.32 (n=521) |
| fights won / lost as the opener | 39% / 30% | 39% / 29% | 52% / 18% | 57% / 15% |
| opener is a spell; at distance 4 / 5+ | 90%; 63 / 3% | 89%; 62 / 3% | 81%; 52 / 18% | 81%; 54 / 14% |
| outnumbered within 6 when opening (real) | 41% (251/610) | 42% (239/575) | 35% (209/589) | 43% (222/521) |
| own n6 vs enemy n6 when opening | 1.74 vs 2.06 | 1.70 vs 2.07 | 1.81 vs 1.94 | 1.74 vs 1.97 |
| contact rounds before being hit (median; 8+) | 14; 67% | 13; 68% | 14; 69% | 13; 66% |
| contact champion-rounds farming / idle / closer | 20 / 16 / 30% | 23 / 16 / 29% | 13 / 18 / 32% | 14 / 18 / 33% |
| focus: same victim when 2+ hit | 67% (651/977) | 66% (564/852) | 72% (719/997) | 74% (667/896) |
| chase >= 3 steps; victim dies when chased | 11% (232/2109); 16% | 11% (209/1916); 18% | 13%; 31% | 14%; 33% |
| cast within 2 rounds of being opened on | 75% (441/589) | 79% (409/521) | 70% (429/610) | 70% (401/575) |
| cast when enemy <= 4 and both slots up / walked instead | 49% (1531/3123) / 23% | 55% (1357/2453) / 19% | 38% / 33% | 38% / 32% |
| spell share of champion damage | 80% | 79% | 66% | 65% |
| ranged basic attacks at distance 1-2 | 38% (1110/2889) | 35% (953/2752) | 22% (525/2387) | 24% (550/2272) |
| ranged fight-rounds within 2 of an enemy | 12% (2496/21082) | 12% (2196/18497) | 5% | 6% |
| retreat under fire: hp% at the step (median) | 48 | 49 | 49 | 47 |
| retreating champion dies within 12 rounds | 19% (228/1192) | 19% (201/1046) | 10% (138/1451) | 11% (145/1334) |
| ... casters | 27% (124/465) | 30% (118/390) | 10% (45/445) | 13% (52/409) |
| recall under threat completed | 85% (507/599) | 85% (447/527) | 87% | 88% |
| fight length median / single pokes | 4 / 26% | 4 / 27% | | |
| gems lost / won by deaths in fights | 9806 / 10364 | 8502 / 8432 | 10364 / 9806 | 8432 / 8502 |
| gems tributed (game totals) | 124045 (800/game) | 121260 (808/game) | 139292 | 136052 |

The fight profile of study27 is the study26 profile within sampling noise on almost every line. The two places where the numbers moved more than noise are both on the spell side
(we cast less on cooldown: 49% vs 55% of 2453-3123 opportunities, and reply within 2 rounds in 75% vs 79%) and in the opponents' conversion, which fell from 0.97 to 0.89 kills per
fight they open (0.33 deaths each time): we die a little less in the fights they start (523 deaths in 589 fights vs 505 in 521) but still lose them 52% / win 18%.

## 1. Fights per game, who opens, opener conversion

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| games with any fight | 123 of 155 | 118 of 150 | | |
| fights per game / real per game | 15.0 / 7.7 | 14.4 / 7.3 | | |
| hit first (all fights) | 52% (1204/2324) | 54% (1156/2158) | 48% | 46% |
| hit first (real fights) | 51% (610/1199) | 52% (575/1096) | 49% | 48% |
| kills / deaths per real fight | 0.51 / 0.74 | 0.52 / 0.77 | 0.74 / 0.51 | 0.77 / 0.52 |
| share of fight damage | 53% | 53% | 47% | 47% |
| fights this side opened: kills / deaths; won / lost | 0.68 / 0.59 (416-361 in 610); 39 / 30% | 0.69 / 0.58 (398-335 in 575); 39 / 29% | 0.89 / 0.33 (523-196 in 589); 52 / 18% | 0.97 / 0.32 (505-167 in 521); 57 / 15% |
| fights the other side opened: kills / deaths; won / lost | 0.33 / 0.89 (196-523); 18 / 52% | 0.32 / 0.97 (167-505); 15 / 57% | 0.59 / 0.68; 30 / 39% | 0.58 / 0.69; 29 / 39% |
| gems lost / won in fights this side opened | 3646 / 7816 | 3200 / 6482 | 2548 / 6160 | 1950 / 5302 |
| gems lost / won in fights the other side opened | 6160 / 2548 | 5302 / 1950 | 7816 / 3646 | 6482 / 3200 |
| dmg dealt / taken per fight this side opened | 1279 / 884 | 1305 / 852 | 1102 / 867 | 1149 / 882 |

- Same volume (+0.4 real fights per game, mostly interlock: 8.5 vs 6.6 per game on 19 vs 13 games), same hit-first share, same K/D (0.51 / 0.74 vs 0.52 / 0.77).
- The opener still wins for both sides and we still convert worse: 0.68 / 0.59 vs their 0.89 / 0.33. Their conversion is the one number that moved (0.97 -> 0.89 kills per fight they
  open, won 57% -> 52%); it is a 2-sigma move on ~550 fights, and 10 of the 18 fewer kills-per-100-fights come from one category, "they catch us farming" (below).
- More gems change hands in fights in both directions (+15% lost, +23% won) with only +8% fights: both sides carried more (we carry gems in 50% of the fights they open, 51 mean vs 48;
  they carry in 61%, 69 mean vs 64).

### 1b. The first hit (all fights, by opener side)

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| openers (n) | 1204 | 1156 | 1120 | 1002 |
| spell | 90% | 89% | 81% | 81% |
| distance 1 / 2 / 3 / 4 / 5+ | 6 / 7 / 21 / 63 / 3% | 7 / 8 / 20 / 62 / 3% | 13 / 4 / 13 / 52 / 18% | 13 / 4 / 14 / 54 / 14% |
| round p25 / med / p75 | 182 / 311 / 436 | 181 / 313 / 450 | 156 / 274 / 407 | 164 / 290 / 415 |
| opener hp% med / < 50% | 97 / 3% (34) | 100 / 2% (24) | 91 / 8% (87) | 89 / 8% (77) |
| victim hp% med / < 50% | 87 / 14% (173) | 89 / 14% (157) | 96 / 7% (81) | 95 / 8% (78) |
| victim isolated (no ally within 4) / baseline | 55% / 36% | 56% / 38% | 56% / 34% | 56% / 36% |
| victim walking / farming / idle / recalling / tributing | 56 / 12 / 13 / 10 / 8% | 58 / 13 / 13 / 10 / 6% | 57 / 18 / 14 / 4 / 7% | 58 / 19 / 12 / 5 / 6% |
| opener champion | Stellar 321, Ren 320, Cassi 184, Tavi 140, Ryth 113 | Stellar 322, Ren 307, Cassi 158, Ryth 126, Tavi 122 | Stellar 338, Ren 219, Cassi 125, Ryth 120, Tavi 114 | Stellar 301, Ren 166, Tavi 130, Cassi 127, Ryth 108 |
| first victim | Issac 272, Varg 184, Ren 176, Stellar 168, Cassi 116 | Issac 264, Ren 171, Stellar 167, Varg 156, Cassi 98 | Ren 231, Issac 196, Cassi 165, Stellar 150, Tavi 124 | Ren 236, Issac 172, Cassi 131, Stellar 125, Tavi 101 |

Identical: spell at exactly 4 (63%, 3% at 5+ against the opponents' 18%), isolated victim preferred (55% vs 36% baseline), low victims not sought (14% vs 24% available), opener at full hp.
Opponents open on us earlier in the game than we do on them (median round 274 vs 311, p25 156 vs 182), in both batches.

### 1c/1d. Opener-side outcome by what the victim was doing (real fights; kills / deaths per fight, n)

| victim was | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| walking | 0.61 / 0.66 (337) | 0.57 / 0.64 (341) | 0.92 / 0.36 (331) | 0.96 / 0.32 (308) |
| idle | 0.65 / 0.55 (85) | 0.61 / 0.65 (74) | 1.02 / 0.25 (81) | 0.94 / 0.54 (63) |
| farming | 0.59 / 0.53 (64) | 0.81 / 0.42 (69) | 0.78 / 0.32 (95) | 0.95 / 0.22 (101) |
| recalling (see PTN caveat) | 1.09 / 0.44 (68) | 1.34 / 0.56 (59) | 0.88 / 0.15 (33) | 1.22 / 0.22 (27) |
| tributing | 0.75 / 0.46 (56) | 0.75 / 0.22 (32) | 0.69 / 0.43 (49) | 0.95 / 0.32 (22) |

- Our openers on a walking enemy (55% of our real openers) are still a losing trade (0.61 / 0.66); theirs on ours 0.92 / 0.36.
- **They catch us farming with a worse result than before**: 95 real fights, 74 of our deaths and 30 kills (s26: 101 fights, 96 deaths, 22 kills), i.e. 0.78 / 0.32 against 0.95 / 0.22. The
  number of times they catch us farming did not change (200 of 1120 openers = 18%, s26 191 of 1002 = 19%), and the number of our champions busy with a camp when it happens is the same
  distribution (1: 102, 2: 68, 3: 22, 4+: 8; s26 97 / 63 / 22 / 9): the stacking rule did not make the farming group bigger at the moment of the hit, nor more often present (>= 2 of ours
  hitting a camp at the first hit in 11% of fights, both batches). Our n6 in those fights is 2.17 vs 2.04. So the gain is 22 deaths on ~100 fights: real but at the edge of what the sample can show.
- Our own openers on a farming enemy got worse (0.59 / 0.53 on 64 vs 0.81 / 0.42 on 69): same order of magnitude, opposite sign, n < 70 each; noise.
- We get caught tributing more often (49 real fights vs 22) and our tributing openers on them also doubled (56 vs 32); neither category pays the way it did (0.75 / 0.46; 0.69 / 0.43 for them).

## 2. Numbers, hp and approach at the first hit (openers of this side, real fights)

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| real fights opened (n) | 610 | 575 | 589 | 521 |
| own n6 vs enemy n6 (mean) | 1.74 vs 2.06 | 1.70 vs 2.07 | 1.81 vs 1.94 | 1.74 vs 1.97 |
| outnumber / equal / outnumbered within 6 | 24% (148) / 35% / 41% (251) | 23% (135) / 35% / 42% (239) | 28% (163) / 37% / 35% (209) | 26% (134) / 32% / 43% (222) |
| K/D when outnumbering | 0.85 / 0.53 (148) | 0.74 / 0.49 (135) | 1.02 / 0.23 (163) | 1.02 / 0.31 (134) |
| K/D when outnumbered | 0.57 / 0.60 (251) | 0.68 / 0.69 (239) | 0.89 / 0.35 (209) | 0.91 / 0.36 (222) |
| opener alone within 6 (all openers) | 55% (662/1204) | 55% (631/1156) | 54% | 60% |
| hit-first share when ahead / even / behind (all fights) | 39 / 52 / 64% | 38 / 56 / 67% | 36 / 48 / 61% | 33 / 44 / 62% |
| own hp% / enemy hp% at the hit (med) | 91 / 85 | 94 / 86 | 88 / 90 | 88 / 89 |
| approach: deliberate / they came / farming / other | 37 / 28 / 12 / 23% | 38 / 29 / 13 / 21% | 34 / 32 / 10 / 24% | 36 / 32 / 8 / 23% |
| deliberate openers: K/D | 0.73 / 0.59 (230) | 0.83 / 0.51 (206) | 0.88 / 0.24 (218) | 0.99 / 0.29 (208) |
| own champions within 8 / alive | 2.16 / 3.93 | 2.09 / 3.90 | 2.20 / 4.39 | 2.13 / 4.45 |
| team split (ally alive > 8 away) | 82% | 83% | 88% | 91% |
| fight in own half / middle / enemy half | 40 / 32 / 29% | 41 / 33 / 26% | 17 / 30 / 52% | 18 / 30 / 53% |

No numbers check, no hp check, same as before: we open outnumbered in 41% of our real openers (they: 35%, down from 43%; the opponents' set changed, so this is not a change in us), our
opener is alone within 6 in 55% of openers, our hit-first share is highest when behind (64%) and lowest when ahead (39%). The only thing that reads as a shift is that our outnumbered openers
got worse (0.57 / 0.60 on 251 vs 0.68 / 0.69 on 239) and our outnumbering ones better (0.85 / 0.53 on 148 vs 0.74 / 0.49 on 135): both within ~1.5 sigma.

## 3. Before the first hit, side that gets hit

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| fights where this side was hit first (n) | 1120 | 1002 | 1204 | 1156 |
| contact rounds before the hit: 1 / 2-3 / 4-7 / 8+ (median) | 0 / 9 / 24 / 67% (14) | 0 / 9 / 23 / 68% (13) | 0 / 8 / 23 / 69% (14) | 1 / 8 / 26 / 66% (13) |
| victim side champions within 8 / alive | 2.24 / 4.21 | 2.24 / 4.22 | 2.23 / 4.26 | 2.19 / 4.28 |
| victim side split | 82% | 83% | 88% | 88% |
| victim side carries gems / mean on carriers | 50% / 51 | 50% / 48 | 61% / 69 | 60% / 64 |
| hit in own half / middle / enemy half | 53 / 33 / 14% | 54 / 32 / 13% | 25 / 36 / 39% | 26 / 37 / 37% |
| contact champion-rounds (n) | 49799 | 44033 | 55578 | 51238 |
| farming / idle / closer / away / sideways / recalling | 20 / 16 / 30 / 9 / 19 / 5% | 23 / 16 / 29 / 10 / 18 / 5% | 13 / 18 / 32 / 11 / 19 / 6% | 14 / 18 / 33 / 11 / 18 / 7% |
| dominant reaction per fight: closer / farming / idle / sideways / recall | 52 / 25 / 9 / 12 / 1% (1119) | 49 / 29 / 8 / 12 / 1% (1001) | 55 / 14 / 17 / 11 / 3% | 54 / 14 / 17 / 11 / 4% |

Same picture: they hit us in our half (53%), after a median 14 rounds of contact, with our team split (82%) and 2.2 of 4.2 champions near. The farming share of our contact champion-rounds
went from 23% to 20% (9,969 of 44,033 -> 10,162 of 49,799) and "kept farming" as the dominant reaction from 29% to 25% of fights (293 of 1001 -> 285 of 1119): 3-4 points on tens of thousands of
champion-rounds is a real but small shift, and still 1.5x the opponents' 13-14%. The extra contact rounds went to "moved closer" (29 -> 30%) and "sideways" (18 -> 19%), not to "moved away" (10 -> 9%).

## 4. Focus, target choice, chase, spells, ranged distance

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| focus: same victim when 2+ hit in a round | 67% (651/977) | 66% (564/852) | 72% (719/997) | 74% (667/896) |
| focus in wins / losses | 62% (297/480) / 71% (354/497) | 72% (253/352) / 62% (311/500) | 73% / 72% | 78% / 73% |
| target (2+ in reach): nearest / lowest hp (n) | 70 / 62% (2047) | 72 / 63% (1946) | 78 / 69% (1000) | 77 / 69% (920) |
| caster when available / carrier when available | 62% (783/1256) / 63% (556/887) | 63% / 66% | 70% / 72% | 66% / 72% |
| basic attacks; target out of range next round; stepped after it | 5105; 44%; 72% | 4754; 44%; 71% | 5450; 46%; 68% | 5025; 44%; 69% |
| hitter-retreat episodes; 0 / 1-2 / >= 3 / >= 5 follow steps | 2109; 67 / 22 / 11 / 3% | 1916; 65 / 24 / 11 / 3% | 1650; 59 / 27 / 13 / 5% | 1453; 55 / 30 / 14 / 4% |
| >= 3 steps when victim < 35% hp | 8% (51/607) | 9% (54/574) | 9% (45/507) | 11% (48/439) |
| victim died (all) / when chased >= 3 | 10% (215) / 16% (38/232) | 11% (209) / 18% (37/209) | 21% (339) / 31% (68/222) | 21% / 33% |
| hit again after the step | 10% | 11% | 14% | 15% |

- Focus and target choice unchanged (67% same victim; nearest 70%, lowest 62%; twice as many multi-candidate decisions as the opponents because we stand inside their group).
  The study26 note "our focus is worse in losses (62 vs 72%)" is reversed in study27 (71% in losses, 62% in wins) on 350-500 rounds each: it was noise, focus does not predict the result.
- Chase unchanged: 11% of 2109 episodes followed >= 3 steps, and the victim dies in 16% of those vs 31% for the opponents' chases; 10% of the enemies that step away from us die, 21% of ours
  that step away from them.

**Spells**

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| cast within 2 rounds of the first hit (fights the other side opened) | 75% (441/589) | 79% (409/521) | 70% (429/610) | 70% (401/575) |
| casts per real fight | 5.90 | 5.88 | 5.51 | 5.53 |
| champion-rounds with enemy <= 4 and both slots up: cast / walked | 49% (1531/3123) / 23% | 55% (1357/2453) / 19% | 38% (1410/3747) / 33% | 38% (1343/3500) / 32% |
| spell share of champion damage | 80% | 79% | 66% | 65% |
| per champion cast rate (n) | Stellar 62% (627), Cassi 56% (412), Tavi 37% (690), Prism 60% (210), Ryth 52% (497), Ren 53% (242), Issac 32% (290) | Stellar 69% (562), Cassi 64% (283), Tavi 43% (458), Prism 59% (216), Ryth 58% (435), Ren 49% (177), Issac 39% (205) | Stellar 46%, Cassi 54%, Tavi 41%, Prism 45%, Ryth 38%, Ren 44%, Issac 25% | Stellar 44%, Cassi 53%, Tavi 47%, Prism 42%, Ryth 31%, Ren 48%, Issac 24% |

This is the one systematic shift: with an enemy within 4 and both slots up we cast in 49% of champion-rounds instead of 55% (6 points on 2453-3123 rounds, 3 sigma) and walked instead in
23% instead of 19%; every caster except Prism and Ren dropped (Stellar 69 -> 62, Cassi 64 -> 56, Tavi 43 -> 37, Ryth 58 -> 52, Issac 39 -> 32). The reply within 2 rounds of being opened on
also dropped (79% -> 75%, 409/521 -> 441/589). Casts per real fight and spell share of damage did not move (5.9; 80%), so the spells are still fired, just a round or two later: the
opportunity rows grew (3123 vs 2453 champion-rounds, +27%, with only +9% real fights), i.e. more rounds spent with an enemy at <= 4 and slots up. That is consistent with champions
arriving at the fight from a camp a few tiles further away than before (the stacking rule moves champions to the big camps), but nothing in the fight data isolates the cause.

**Ranged champions: distance**

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| ranged basic attacks at d1 / d2 / d3 (n) | 19 / 19 / 61% (2889) | 16 / 19 / 65% (2752) | 6 / 16 / 77% (2387) | 7 / 17 / 75% (2272) |
| at d1-2 | 38% (1110) | 35% (953) | 22% (525) | 24% (550) |
| spells at d1 / d2 / d3 / d4 / d5+ (n) | 5 / 7 / 21 / 58 / 8% (3942) | 5 / 8 / 23 / 56 / 8% (3627) | 2 / 3 / 15 / 59 / 21% (3062) | 1 / 4 / 17 / 61 / 17% (2700) |
| spells from 1-3 | 34% (1332) | 37% (1324) | 20% (621) | 22% (599) |
| ranged fight-rounds within 2 of an enemy | 12% (2496/21082) | 12% (2196/18497) | 5% (1033/19638) | 6% (1113/18014) |

Unchanged, if anything slightly worse at the basic-attack end (38% of ranged basic attacks at distance 1-2, 19% at distance 1 vs 16%: +3 points on ~2800, borderline). Still 8% of spells
at 5+ against 21% for the opponents; still 12% of ranged fight-rounds within 2 (opponents 5%).

## 5. Retreat under fire, fight ends

| metric | s27 us | s26 us | s27 opp | s26 opp |
|---|---|---|---|---|
| retreats under fire (n) | 1192 | 1046 | 1451 | 1334 |
| hp% at the step med (p25-p75) | 48 (31-68) | 49 (31-71) | 49 (32-68) | 47 (31-66) |
| < 30% / < 50% / >= 70% | 22 / 51 / 23% | 22 / 51 / 26% | 21 / 51 / 23% | 23 / 53 / 22% |
| died within 12 rounds | 19% (228) | 19% (201) | 10% (138) | 11% (145) |
| died: melee / casters | 14% (104/727) / 27% (124/465) | 13% (83/656) / 30% (118/390) | 9% / 10% | 10% / 13% |
| died by hp band 0-30 / 30-50 / 50-70 / 70+ | 30 / 20 / 16 / 12% | 28 / 20 / 17 / 13% | 16 / 11 / 7 / 4% | 19 / 8 / 11 / 5% |
| recall within 10 / completed / distance to nearest enemy | 50% / 85% (507/599) / 6 | 50% / 85% (447/527) / 6 | 55% / 87% / 7 | 52% / 88% / 7 |
| kite (hits again within 8 rounds) | 18% | 21% | 14% | 14% |
| outnumbered at the step | 31% | 31% | 36% | 34% |
| fight length med / p75; single pokes; >= 10 rounds | 4 / 10; 26%; 28% | 4 / 10; 27%; 28% | | |
| ends: kill / wipe / recall / walk | 16 / 14 / 13 / 56% | 16 / 14 / 13 / 56% | | |
| leaves first / other first / same round | 26 / 26 / 29% | 26 / 26 / 29% | 26 / 26 / 29% | |
| wiped / wiped the other (real fights) | 182 / 138 | 172 / 131 | 138 / 182 | 131 / 172 |
| leave kind: walk / recall | 77 / 23% | 77 / 23% | 64 / 36% | 66 / 34% |

Line for line the same: we step away at 48% hp, recall from 6 tiles and complete 85%, and die anyway in 19% (casters 27%, n=465; opponents' casters 10%). Fight length, how fights end
and who leaves first are the same to the percentage point.

## 6. Per map (real fights; study27 | study26)

| map | W-L s27 | s26 | real fights / game s27 | s26 | we hit first s27 | s26 | kills-deaths s27 | s26 | K/D per real fight s27 | s26 | gems lost / won s27 | s26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| collision | 8-11 | 12-7 | 17.3 | 15.4 | 56% | 56% | 161-235 | 161-212 | 0.49 / 0.71 | 0.55 / 0.72 | 3174 / 3656 | 2402 / 3882 |
| corners | 8-11 | 5-12 | 14.5 | 13.8 | 55% | 58% | 145-235 | 121-231 | 0.53 / 0.85 | 0.52 / 0.99 | 1534 / 1358 | 1902 / 1536 |
| elkring | 5-4 | 5-9 | 12.7 | 12.1 | 60% | 57% | 95-48 | 102-80 | 0.83 / 0.42 | 0.60 / 0.47 | 1080 / 1368 | 1368 / 954 |
| expanse | 10-7 | 11-6 | 0.1 | 0.1 | - | - | 1-0 | 1-0 | - | - | 0 / 0 | 0 / 0 |
| interlock | 10-9 | 7-6 | 8.5 | 6.6 | 56% | 51% | 107-101 | 42-56 | 0.66 / 0.62 | 0.49 / 0.65 | 2554 / 2914 | 1486 / 918 |
| lanes | 3-14 | 3-15 | 4.1 | 3.9 | 13% | 27% | 13-64 | 26-67 | 0.19 / 0.93 | 0.37 / 0.94 | 356 / 256 | 280 / 208 |
| monolith | 5-11 | 5-8 | 5.0 | 5.2 | 34% | 37% | 38-45 | 31-48 | 0.47 / 0.56 | 0.46 / 0.72 | 418 / 440 | 630 / 528 |
| packs | 6-16 | 7-14 | 7.5 | 8.1 | 49% | 52% | 52-154 | 75-144 | 0.31 / 0.93 | 0.44 / 0.85 | 624 / 372 | 368 / 406 |
| rows | 3-14 | 4-14 | 0.1 | 0.3 | - | - | 0-2 | 6-2 | - | - | 66 / 0 | 66 / 0 |
| ALL | 58-97 | 59-91 | 7.7 | 7.3 | 51% | 52% | 612-884 | 565-840 | 0.51 / 0.74 | 0.52 / 0.77 | 9806 / 10364 | 8502 / 8432 |

- The per-map fight numbers are stable where the sample is: corners 145-235 vs 121-231, elkring 95-48 vs 102-80 (still the only map we win the trades on), lanes 13-64 vs 26-67 (we open only
  13% of lanes fights, 9 of 70, vs 27%), monolith 38-45 vs 31-48.
- Collision flipped from 12-7 to 8-11 with the same fight profile (161 kills both times, 235 vs 212 deaths, 56% hit first): the collision result moved by 4 games on 19, the fights did not.
- Packs is where the trades got worse: 52-154 (0.31 / 0.93) vs 75-144 (0.44 / 0.85) on 22 vs 21 games; 6-16. Interlock went the other way: 107-101 on 19 games (0.66 / 0.62) vs 42-56 on 13
  (0.49 / 0.65), with twice the gems moving (2554 / 2914).
- Expanse and rows are still fight-free (2 real fights in 34 games) and still decide 7 of the 97 losses on rows alone (3-14): nothing in this report applies there.
- Top 10: 15-35 (s26 10-40), real fights 334, we hit first 42% (44%), kills-deaths 105-289 (148-312). Ranks 11-30: 38-62 (44-51), 849 fights, 54% (56%), 500-589 (404-526).

## 7. Per opponent (real fights), study27 with the study26 numbers for the same team

| opponent (rank s27 / s26) | W-L s27 | s26 | real fights | we hit first | our kills | our deaths | gems lost / won | s26: fights, hit first, kills, deaths |
|---|---|---|---|---|---|---|---|---|
| Mite (1 / 2) | 1-4 | 2-3 | 26 | 23% | 4 | 23 | 44 / 0 | 35, 46%, 20, 24 |
| Intercontinental Fish (2 / 1) | 1-4 | 0-5 | 19 | 37% | 4 | 17 | 258 / 22 | 30, 50%, 6, 52 |
| Shawn (3 / 3) | 4-1 | 1-4 | 46 | 46% | 26 | 26 | 436 / 562 | 37, 54%, 15, 36 |
| VeryGood (4 / 5) | 1-4 | 0-5 | 31 | 35% | 6 | 26 | 264 / 46 | 37, 22%, 1, 31 |
| hello (5 / 6) | 0-5 | 1-4 | 51 | 27% | 8 | 56 | 368 / 124 | 42, 31%, 17, 37 |
| Univardisty (6 / 4) | 0-5 | 1-4 | 36 | 39% | 1 | 44 | 250 / 0 | 36, 39%, 6, 35 |
| procless (7 / 9) | 1-4 | 1-4 | 42 | 45% | 10 | 31 | 180 / 80 | 31, 29%, 10, 17 |
| PTN Hyperion (8 / 7) | 2-3 | 1-4 | 30 | 40% | 19 | 44 | 210 / 162 | 35, 54%, 44, 46 |
| Full Damage (9 / 11) | 2-3 | 1-4 | 14 | 71% | 8 | 6 | 44 / 232 | 33, 36%, 11, 17 |
| Quantom (10 / 10) | 3-2 | 2-3 | 39 | 69% | 19 | 16 | 208 / 580 | 43, 63%, 20, 30 |
| geese geese go (11 / 13) | 0-5 | 1-4 | 60 | 53% | 24 | 44 | 442 / 398 | 67, 63%, 36, 63 |
| Nyxius (12 / 8) | 1-4 | 1-4 | 23 | 65% | 18 | 13 | 198 / 372 | 12, 67%, 9, 4 |
| KratosMessi (13 / 14) | 2-3 | 3-2 | 28 | 50% | 13 | 14 | 200 / 298 | 29, 69%, 13, 17 |
| test (14 / 17) | 1-4 | 5-0 | 54 | 35% | 20 | 42 | 610 / 574 | 31, 42%, 15, 27 |
| Boost (15 / 15) | 0-5 | 1-4 | 55 | 29% | 15 | 67 | 710 / 216 | 25, 28%, 8, 22 |
| Cabbage (16 / -) | 2-3 | - | 42 | 48% | 10 | 54 | 514 / 110 | new |
| (hieroglyphs) (17 / 12) | 1-4 | 4-1 | 39 | 46% | 32 | 33 | 636 / 252 | 47, 64%, 39, 23 |
| getramramd#euw (18 / 18) | 2-3 | 3-2 | 36 | 64% | 29 | 10 | 154 / 586 | 29, 69%, 21, 13 |
| Still Testing (19 / 19) | 3-2 | 3-2 | 56 | 52% | 34 | 17 | 88 / 644 | 44, 61%, 37, 11 |
| Conley (20 / 20) | 3-2 | 2-3 | 23 | 43% | 15 | 30 | 286 / 138 | 34, 29%, 7, 41 |
| Nyx (21 / 25) | 1-4 | 3-2 | 56 | 71% | 25 | 33 | 222 / 140 | 43, 74%, 29, 23 |
| lETHal (22 / 16) | 2-3 | 0-5 | 33 | 61% | 9 | 31 | 666 / 258 | 32, 44%, 11, 33 |
| hinana (23 / 21) | 3-2 | 1-4 | 32 | 56% | 13 | 20 | 210 / 210 | 44, 61%, 17, 46 |
| Ely2sh (24 / 28) | 3-2 | 2-3 | 52 | 44% | 29 | 28 | 234 / 300 | 54, 48%, 16, 50 |
| umamusume (25 / 26) | 2-3 | 3-2 | 26 | 54% | 9 | 31 | 224 / 164 | 49, 57%, 14, 35 |
| octo's odyssey (26 / 23) | 3-2 | 3-2 | 48 | 60% | 61 | 20 | 310 / 502 | 30, 57%, 36, 8 |
| AlphaSlop (27 / 22) | 3-2 | 4-1 | 56 | 70% | 41 | 33 | 466 / 890 | 37, 65%, 29, 14 |
| Mate in One (28 / -) | 2-3 | - | 34 | 59% | 33 | 19 | 96 / 534 | new |
| BottleBots (29 / 27) | 2-3 | 1-4 | 36 | 58% | 24 | 26 | 574 / 936 | 44, 52%, 25, 46 |
| EMPEROR Tung (30 / -) | 2-3 | - | 60 | 65% | 46 | 24 | 660 / 910 | new |
| Palestine (54 / -) | 5-0 | - | 16 | 62% | 7 | 6 | 44 / 124 | new |

At 5 games per opponent the W-L swings are mostly noise (Shawn 1-4 -> 4-1 with the fights going 15-36 -> 26-26; test 5-0 -> 1-4 with 15-27 -> 20-42; hieroglyphs 4-1 -> 1-4), but the pattern
that persists is the one from study26: the teams that do not let us open (Mite 23%, hello 27%, Boost 29%, VeryGood 35%, test 35%) kill us 3-7 to 1 (Mite 4-23, hello 8-56, Boost 15-67,
Univardisty 1-44, VeryGood 6-26), and the teams we out-open are the ones we beat in fights (octo 61-20 at 60%, Still Testing 34-17, getramramd 29-10, EMPEROR Tung 46-24, Mate in One 33-19).
Mite is the clearest regression in the sample: 20-24 at 46% hit-first in s26, 4-23 at 23% in s27 (26 fights, 0 gems won).

## 8. Three worked timelines from study27 (worst losses by score margin; `timeline.py` with `WS=$S/ws3`)

**A. collision `3316543c` vs Univardisty (rank 6), 66-1078, fights 0-18.** First real fight r30-50, they open, we lose 3 and kill 0. r26-29: our Cassi0, Issac1 (76%), Stellar3 all hit
the camp at (21,20) while enemy Stellar4 + Tavi6 walk in from distance 8 to 5 over 4 rounds (Ren2 stands at (24,18)); nobody reacts. r30: Stellar4 spells Issac1 at 5 (140). r31-33: Cassi0 and
Stellar3 walk *north*, away from Issac; Issac1 walks *into* Stellar4 to distance 1 and trades basics (takes 70 + 235), dashes back at 26% (r34), stands still two rounds at distance 4, starts a
recall at r36 and is finished by a Tavi spell at r37 (2% -> dead at r38, and the paired Cassi0 dies with him although she is 10 tiles away). While that happens Ren2 starts a tribute at r34 six tiles away. r41-49: Stellar3 and Ren2 vs Stellar4 + Tavi6, 2v2, both at
range 4-5; Stellar3 stands on (20,15) for nine rounds casting on cooldown and never steps (100% -> 29%); Ren2 dashes out at 56% (r48) and leaves Stellar3 alone at 33%, who dies at r50.
Everything from study26 in one fight: farming through 4 contact rounds, an Issac walking to distance 1, a tribute started next to a fight, a caster that does not move, allies that leave one at a time.

**B. interlock `258821b2` vs hieroglyphs (rank 17), 160-1044, fights 3-14, -270 gems; fight r35-66, they open, 0-5, -138 gems.** r30-35: our Ren2 dashes ahead alone from (12,13) to (16,17)
toward enemy Cassi6 while Cassi0/Issac1/Tavi4 farm at (6-11,18-20) and Stellar3 idles at (5,14); Cassi6 opens on Ren at 4 (140), Ren answers (162). r37-44: their Issac7, Ren8, Stellar5 arrive
together from the east (4 bodies within 6 by r45); ours arrive one at a time. r45-49: Stellar3 walks in a straight line from (5,14) to (15,26), ending at distance 2 of Ren8 and 4 of Stellar5,
takes 325 (r46), casts twice at distance 1 and dies at r50 (100% -> 0 in four rounds, no step away until 9%). r50-57: Tavi4 follows the same path to distance 2 of Ryth9 and Stellar5 (r55),
takes 360 + 275, dies at r58. r57-63: Cassi0 (back from a recall) walks to distance 1 of Ryth9 and is killed by basics (the paired Issac1, farming 10 tiles away, dies with her) while Ren2 walks beside her without attacking. r63-66: Ren2, now
alone at distance 1 of three enemies, takes 175 + 280 and dies. Four separate arrivals, each walking to distance 1-2 of a group of 4, plus the paired death: 0-5.

**C. packs `e339a02d` vs PTN Hyperion (rank 8), 44-1012, fights 3-19; fight r23-39, they open, 0-3, -48 gems.** r18-21: Issac1 and Ren2 farm the camp at (18,12) while Cassi4, Stellar6,
Ryth7 walk toward it as a group of 3 (PTN's "recall every round" shows as RECALL on each line; they never arrive anywhere). r22: Ren2 dashes from the camp to distance 3 of all three and takes
410 in one round (Cassi attack + spell, Stellar spell, Ryth spell), 100% -> 54%. r25: Issac1 dashes in after him. r26-32: Ren (48% -> 21%) and Issac (78% -> 36%) trade spells at 3-4 with the
trio; our Stellar3 arrives at r29 from 9 tiles. r33: Ren starts a recall at 21% at distance 4, stands still for 4 rounds and gets away (the one retreat that works here). r34-35: Issac dies at 9%
at distance 2, and the paired Cassi0 with him. r34-39: Stellar3 walks to distance 2 then 1 of Ryth7 and trades basics with him for five rounds (100% -> 24%), dies r40. 2 bodies into 3, then 1 into 3, each at distance 1-3: 0-3.

## 9. What changed with study27 and what did not

1. The fight profile is the study26 profile: 15.0 fights / 7.7 real per game (14.4 / 7.3), hit first 51% (52%), 0.51 / 0.74 kills / deaths per real fight (0.52 / 0.77), 53% of fight damage, 4-round fights, 26% pokes.
2. Our opener conversion did not move (0.68 / 0.59 on 610 fights vs 0.69 / 0.58 on 575); opening outnumbered 41% (42%), opener alone 55% (55%), hit-first share 64% when behind / 39% when ahead (67 / 38%).
3. The opponents convert slightly less on us: 0.89 / 0.33 on 589 fights vs 0.97 / 0.32 on 521, and the drop sits in "they caught us farming": 30-74 in 95 fights vs 22-96 in 101. It is 2 sigma on ~100 fights.
4. Stacking is invisible at the moment of the hit: the number of our champions on a camp when they open on us farming is the same distribution (1: 102, 2: 68, 3: 22, 4+: 8 vs 97 / 63 / 22 / 9), >= 2 busy in 11% of fights both times.
5. We farm a little less under contact: 20% of contact champion-rounds (23%), "kept farming" the dominant reaction in 25% of fights (29%); still 1.5x the opponents' 13-14%, and "moved away" is still 9-10%.
6. We cast less on cooldown: 49% of both-slots-up opportunities (55%, 3 sigma on ~3000 rounds), reply within 2 rounds 75% (79%); casts per fight and spell share unchanged (5.9; 80%), so the spells come later, not fewer.
7. Ranged positioning unchanged or a touch worse: 38% of ranged basics at distance 1-2 (35%), 12% of ranged fight-rounds within 2 (12%), 8% of spells at 5+ (8%; opponents 21%).
8. Retreat, chase, focus, fight ends: identical to the point (step away at 48%, die after it 19% / casters 27%, recall completed 85%, chase >= 3 steps 11%, same victim 67%, leave first 26 / 26 / 29%). The s26 "worse focus in losses" reversed (71% in losses, 62% in wins): noise.
9. Per map the trades are stable (corners 145-235, elkring 95-48, lanes 13-64, monolith 38-45); collision went 12-7 -> 8-11 with the same fights (161-235 vs 161-212), packs got worse (52-154 vs 75-144), interlock better (107-101 vs 42-56, on 19 vs 13 games); expanse/rows still fight-free.
10. Against the top 10 the same five teams still deny the opener and kill 3-7 to 1 (Mite 4-23 at 23% hit-first, hello 8-56, Boost 15-67, Univardisty 1-44); the 58-97 vs 59-91 result is within what 5-game opponent series and the map mix can move, and nothing in the fights explains a gain or a loss from the camp-stacking rule.
