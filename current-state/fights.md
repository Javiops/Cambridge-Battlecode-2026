# How our bot (v35, "Live Love Larp") fights: 150 games vs the top 30, 2026-10-15 11:33 UTC

Data: `$S/ws2/selected.json` (150 games, 59-91, 50 vs ranks 1-10, 100 vs ranks 11-30; 5 of the games are vs MicroStella, rank 249, which slipped into the set),
per-step decoded replays in `$S/ws2/steps`. Scripts: `$S/ws2/scripts_fights/` (`common.py` loader, `fights_build.py` -> `fights.json`, `analyze.py`, `chase.py`, `extra.py`,
`timeline.py <match-prefix> <r0> <r1>`); raw outputs `out_analyze.txt`, `out_chase.txt`, `out_extra.txt`. Every side-dependent metric is computed symmetrically, so "them" = the
opponents in the same 150 games. Reference numbers for Mite (#1) and Univardisty (#2) come from `/mnt/project-files/analysis/top2-dissection-2026-10-15/fights.md` (same definitions).

**Definitions** (identical to the top-2 dissection): a *fight* is a cluster of champion-on-champion hits merged when within 5 rounds and 8 tiles (union-find). *Real* fight = >= 1000
total damage or a death. *n6* = champions of a side alive within 6 tiles of the first victim at the end of the round before the first hit (the attacker at range 4 counts).
*Contact* = an enemy within 8 tiles (true vision through walls/bushes is not modelled). Distances are Chebyshev. "dist 5" for a spell = a radius-1 ground spell placed at 4.
2158 fights in 118 of the 150 games (32 games, mostly expanse/rows, had no champion-on-champion damage at all); 1096 real.

## 0. Headline numbers

| | us (v35) | opponents (same games) | Mite | Univardisty |
|---|---|---|---|---|
| fights / real fights per game | 14.4 / 7.3 | same games | 13.0 / 7.2 | 17.7 / 9.7 |
| hit first (real fights) | 52% | 48% | 54% | 55% |
| kills / deaths per real fight | 0.52 / 0.77 | 0.77 / 0.52 | 0.67 / 0.68 | 0.66 / 0.61 |
| damage dealt / taken per real fight | 1104 / 993 | 993 / 1104 | 1260 / 1300 | 1413 / 1178 |
| share of fight damage | 53% | 47% | 49% | 55% |
| opener is a spell | 89% | 81% | 87% | 91% |
| opener distance 4-5 / exactly 3 / 1-2 | 65% / 20% / 15% | 68% / 14% / 17% | 78% at 4-5 | 79% at 4-5 |
| first victim isolated (no ally within 4) vs baseline | 56% (38%) | 56% (36%) | 60% (35%) | 48% (26%) |
| first victim < 50% hp vs baseline | 14% (24%) | 8% (15%) | 8% (22%) | 12% (23%) |
| first victim recalling / tributing / farming | 10 / 6 / 13% | 5 / 6 / 19% | 2% / - / 13% | 13% / - / 17% |
| our openers while outnumbered within 6 | 42% | 26% | 29% (within 8) | 54% (within 8) |
| real fights in own half / middle / enemy half (own openers) | 37 / 37 / 26% | 54 / 32 / 13% (= our half when they open) | 42 / 27 / 31% | 29 / 25 / 46% |
| spell share of champion damage | 79% | 65% | 62% | 76% |
| spell cast when enemy <= 4 and both slots up | 55% | 38% | 0.6-0.9 per slot | 0.4-0.9 per slot |
| focus: same victim when 2+ hit in a round | 66% | 74% | 66% | 63% |
| retreat under fire: hp% median | 49% | 47% | 38% | 47% |
| retreating champion dies anyway | 19% (casters 30%) | 11% | 16% | 20% |
| recall under threat completed | 85% | 88% | 87% | 76% |
| chase a retreating enemy >= 3 steps | 11% | 14% | 12% | 13% |
| fight length median / single pokes | 4 rounds / 27% | same | 5 / 20% | 5 / 22% |
| gems lost by deaths in fights (150 games) | 8502 | 8432 | - | - |

We fight about as often as Mite and we open fights at a top-2 rate, but we lose the exchanges: 0.52 kills / 0.77 deaths per real fight (Mite 0.67/0.68), and the
asymmetry is entirely in what happens *after* the first hit. The same first-hit profile (spell at 4, isolated target, no hp/numbers check) that works for Mite/Uni does not
work for us because (a) we open outnumbered far more often (42% vs their 26% on us), (b) our ranged units then drift to distance 1-3, (c) our focus is looser and (d) our casters die
after stepping away at 30% vs 13% for theirs.

## 1. Fights per game, who starts, outcome by who started

| split | games (W-L) | fights | per game | real | real/game | we hit first (all / real) | our kills | our deaths | K/D per real fight | dmg dealt / taken | our dmg share | gems lost / won |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 150 (59-91) | 2158 | 14.4 | 1096 | 7.3 | 54% / 52% | 565 | 840 | 0.52 / 0.77 | 1104 / 993 | 53% | 8502 / 8432 |
| collision | 19 (12-7) | 554 | 29.2 | 293 | 15.4 | 60% / 56% | 161 | 212 | 0.55 / 0.72 | 1080 / 949 | 55% | 2402 / 3882 |
| corners | 17 (5-12) | 356 | 20.9 | 234 | 13.8 | 61% / 58% | 121 | 231 | 0.52 / 0.99 | 1648 / 1326 | 56% | 1902 / 1536 |
| elkring | 14 (5-9) | 325 | 23.2 | 169 | 12.1 | 64% / 57% | 102 | 80 | 0.60 / 0.47 | 1099 / 730 | 62% | 1368 / 954 |
| expanse | 17 (11-6) | 13 | 0.8 | 1 | 0.1 | 0% | 1 | 0 | - | - | - | 0 / 0 |
| interlock | 13 (7-6) | 208 | 16.0 | 86 | 6.6 | 50% / 51% | 42 | 56 | 0.49 / 0.65 | 1001 / 931 | 54% | 1486 / 918 |
| lanes | 18 (3-15) | 176 | 9.8 | 71 | 3.9 | 27% / 27% | 26 | 67 | 0.37 / 0.94 | 536 / 998 | 35% | 280 / 208 |
| monolith | 13 (5-8) | 155 | 11.9 | 67 | 5.2 | 28% / 37% | 31 | 48 | 0.46 / 0.72 | 652 / 792 | 43% | 630 / 528 |
| packs | 21 (7-14) | 363 | 17.3 | 170 | 8.1 | 55% / 52% | 75 | 144 | 0.44 / 0.85 | 869 / 985 | 49% | 368 / 406 |
| rows | 18 (4-14) | 8 | 0.4 | 5 | 0.3 | 38% / 40% | 6 | 2 | - | - | - | 66 / 0 |
| win | 59 | 911 | 15.4 | 431 | 7.3 | 61% / 62% | 353 | 191 | 0.82 / 0.44 | 1222 / 714 | 64% | 2524 / 6238 |
| loss | 91 | 1247 | 13.7 | 665 | 7.3 | 48% / 46% | 212 | 649 | 0.32 / 0.98 | 1028 / 1173 | 47% | 5978 / 2194 |
| top-10 opponents | 50 (10-40) | 677 | 13.5 | 338 | 6.8 | 45% / 44% | 148 | 312 | 0.44 / 0.92 | 1115 / 1157 | 50% | 2982 / 1890 |
| ranks 11-30 | 100 (49-51) | 1481 | 14.8 | 758 | 7.6 | 57% / 56% | 417 | 528 | 0.55 / 0.70 | 1099 / 920 | 55% | 5520 / 6542 |

- Fight volume is a map property: collision 29 fights/game, elkring 23, corners 21 (and corners fights are long: 51% last >= 10 rounds, 1648 dmg each); expanse/rows essentially
  none (21 fights in 35 games). On lanes and monolith the opponents come to us: we open only 27-28% of the fights there and lose lanes 3-15.
- Who hits first predicts the game: in wins we open 62% of real fights (K/D 0.82/0.44), in losses 46% (0.32/0.98). Against the top 10 we open only 44% and go 148-312.
- Elkring is the only map where we win the trades (102-80, 62% of damage); corners (121-231) and packs (75-144) are where we bleed.

### 1b. The first hit

| opener | n | spell | basic | dist 1 / 2 / 3 / 4 / 5+ | round p25 / med / p75 | our n6 (mean) | their n6 | victim hp% med | victim < 50% | victim walking / farming / idle / recalling / tributing |
|---|---|---|---|---|---|---|---|---|---|---|
| us | 1156 | 89% | 11% | 7 / 8 / 20 / 62 / 3% | 181 / 313 / 450 | 1.60 | 1.91 | 88 | 14% | 58 / 13 / 13 / 10 / 6% |
| them | 1002 | 81% | 19% | 13 / 4 / 14 / 54 / 14% | 164 / 290 / 415 | 1.88 | 1.58 | 95 | 8% | 58 / 19 / 12 / 5 / 6% |

- Our opener: Stellar spell at 4 (231), Ren stun at 4 (193), Cassi at 4 (106), Ryth at 4 (71), Tavi at 4 (68), Ren at 3 (66), Prism at 4 (49), Stellar at 3 (41); the only
  basic-attack opener of note is Issac at 1 (33). The opener is at 100% hp (median; only 2% of our openers come from a champion below 50%, 8% for the opponents).
- We open at exactly 4 (62%) and almost never at 5 (3%): our AoE casters do not place the ground spell at 4 to reach a target at 5, whereas the opponents do it 14% of the
  time (Stellar at 5: 93 openers, Ryth at 5: 28). Mite/Uni: 78-79% at 4-5.
- Our opener was walking in 75% of cases, farming 12%, standing 12%; theirs: walking 72%, standing 13%, farming 10%.
- Victim type when we open: Issac 264, Ren 171, Stellar 167, Varg 156 (the enemy melee that walk in front). When they open the first victim is our Ren (236), Issac (172),
  Cassi (131), Stellar (125): Ren because he dashes ahead, Cassi because she stands still (see 3b).
- Victim hp: we do hit low victims a bit more than they do (14% vs 8%) but still below what is available (24% of enemy champion-rounds in our contact are < 50%).
- Victim activity: they catch us farming in 19% of their openers (191) vs 13% for us (146); recalling: we catch them 10% (118, our best fights: 1.34 kills / 0.56 deaths),
  they catch us 5% (54). Tributing 6% both.

### 1c. Outcome by who started (real fights)

| split | who started | n | our kills | our deaths | K/D per fight | gems we lost / won | our dmg / their dmg | we won (kills > deaths) | lost | even |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL | us | 575 | 398 | 335 | 0.69 / 0.58 | 3200 / 6482 | 1305 / 852 | 39% | 30% | 31% |
| ALL | them | 521 | 167 | 505 | 0.32 / 0.97 | 5302 / 1950 | 882 / 1149 | 16% | 57% | 27% |
| collision | us / them | 164 / 129 | 123 / 38 | 89 / 123 | 0.75/0.54 ; 0.29/0.95 | 902/3066 ; 1500/816 | | 45% / 14% | 26% / 52% | |
| corners | us / them | 135 / 99 | 80 / 41 | 121 / 110 | 0.59/0.90 ; 0.41/1.11 | 1046/1246 ; 856/290 | | 23% / 11% | 44% / 64% | |
| elkring | us / them | 97 / 72 | 76 / 26 | 32 / 48 | 0.78/0.33 ; 0.36/0.67 | 648/648 ; 720/306 | | 52% / 22% | 20% / 47% | |
| interlock | us / them | 44 / 42 | 30 / 12 | 19 / 37 | 0.68/0.43 ; 0.29/0.88 | 442/802 ; 1044/116 | | 45% / 14% | 23% / 45% | |
| lanes | us / them | 19 / 52 | 12 / 14 | 4 / 63 | 0.63/0.21 ; 0.27/1.21 | 0/116 ; 280/92 | | 42% / 17% | 16% / 69% | |
| monolith | us / them | 25 / 42 | 17 / 14 | 7 / 41 | 0.68/0.28 ; 0.33/0.98 | 22/198 ; 608/330 | | 60% / 17% | 20% / 67% | |
| packs | us / them | 89 / 81 | 56 / 19 | 63 / 81 | 0.63/0.71 ; 0.23/1.00 | 140/406 ; 228/0 | | 31% / 14% | 36% / 60% | |
| win | us / them | 267 / 164 | 252 / 101 | 80 / 111 | 0.94/0.30 ; 0.62/0.68 | 1042/4936 ; 1482/1302 | | 56% / 34% | 15% / 38% | |
| loss | us / them | 308 / 357 | 146 / 66 | 255 / 394 | 0.47/0.83 ; 0.18/1.10 | 2158/1546 ; 3820/648 | | 25% / 7% | 43% / 66% | |
| top-10 | us / them | 149 / 189 | 101 / 47 | 128 / 184 | 0.68/0.86 ; 0.25/0.97 | 1318/1498 ; 1664/392 | | 33% / 12% | 38% / 59% | |
| 11-30 | us / them | 426 / 332 | 297 / 120 | 207 / 321 | 0.70/0.49 ; 0.36/0.97 | 1882/4984 ; 3638/1558 | | 42% / 17% | 27% / 56% | |

- The opener wins, for both sides, but the opponents convert much better: when **they** open they take 0.97 kills and lose 0.32 per fight (we win only 16% of those fights);
  when **we** open we take 0.69 and lose 0.58 (we win 39%). Mite/Uni as openers: 0.74 / 0.46-0.52.
- Against the top 10, opening does not even give us a positive trade (0.68 / 0.86); on corners our own openers go 80-121.
- Gems: 5302 of our 8502 gems lost in fights are lost in fights the opponent opened. The biggest single losses: collision `15195780` r296 vs BottleBots (-262, 4 deaths after a
  Varg basic-attack opener on our Issac), collision `69757c8e` r741 vs Shawn (-154), collision `ae2470ab` r797 vs Full Damage (-146: a lone Prism kills our Cassi standing still
  with 146 gems, timeline in section 7), interlock `feb23cc4` r431 vs test (-144), corners `62365ad4` r221 vs PTN Hyperion (-144, a 78-round 6-4 brawl).

### 1d. Outcome by what the victim was doing (real fights, opener side's kills / deaths per fight)

| opener | victim activity | n | kills | deaths |
|---|---|---|---|---|
| us | walking | 341 | 0.57 | 0.64 |
| us | idle | 74 | 0.61 | 0.65 |
| us | farming | 69 | 0.81 | 0.42 |
| us | recalling | 59 | 1.34 | 0.56 |
| us | tributing | 32 | 0.75 | 0.22 |
| them | walking | 308 | 0.96 | 0.32 |
| them | farming | 101 | 0.95 | 0.22 |
| them | idle | 63 | 0.94 | 0.54 |
| them | recalling | 27 | 1.22 | 0.22 |
| them | tributing | 22 | 0.95 | 0.32 |

Our openers on a walking enemy (59% of our real openers) are a losing trade (0.57 / 0.64); openers on a busy enemy (farming, recalling, tributing: 160 fights) are the only
ones that pay (0.8-1.3 kills, 0.2-0.6 deaths). The opponents make every category pay, including the walking one (0.96 / 0.32): their opener is followed by a group that
finishes the target.

## 2. When WE start: deliberate engagement or collision?

Categories from the 4 rounds before the hit: *deliberate* = our opener moved toward the victim in >= 3 consecutive rounds; *they came to us* = the victim closed more distance
than our opener; *we were farming* = our opener was hitting / being hit by a camp in >= 2 of those rounds; *other* = short approach (1-2 steps) or both static.

| split | n | deliberate | they came to us | we were farming | other | opener stood still all 4 rounds | victim stepped toward us |
|---|---|---|---|---|---|---|---|
| ALL | 1156 | 38% | 29% | 13% | 21% | 11% | 67% |
| collision | 333 | 34% | 30% | 17% | 19% | 14% | 70% |
| corners | 217 | 40% | 35% | 7% | 18% | 16% | 69% |
| elkring | 207 | 56% | 22% | 8% | 14% | 7% | 66% |
| interlock | 105 | 30% | 27% | 5% | 39% | 8% | 55% |
| lanes | 47 | 15% | 30% | 30% | 26% | 13% | 77% |
| monolith | 43 | 51% | 30% | 9% | 9% | 2% | 56% |
| packs | 201 | 29% | 27% | 19% | 24% | 10% | 66% |
| win / loss | 555 / 601 | 35 / 40% | 30 / 27% | 14 / 12% | 21 / 21% | 14 / 9% | 66 / 67% |
| top-10 / 11-30 | 308 / 848 | 38 / 37% | 26 / 30% | 13 / 13% | 22 / 20% | 9 / 12% | 64 / 68% |
| opponents' openers on us (ALL) | 1002 | 36% | 32% | 8% | 23% | 13% | - |

Consecutive closing rounds of our opener: 0: 426, 1: 192, 2: 104, 3: 69, 4: 41, 5: 34, 6: 34, 7+: 256. So 22% of our openers come at the end of a long walk (7+ rounds
straight at the target) and 37% with no closing step at all: the target walked into range (the victim stepped toward us in the previous round in 67% of our openers).
The opponents' profile is the same (36 / 32 / 8 / 23%): both sides mostly fire the first spell when two groups drift into range 4; neither "sets up" an engagement.

**With how many, against how many, at what hp** (real fights we opened; n6 = within 6 of the victim):

| category | n | our n6 vs theirs | we outnumber / equal / outnumbered | our hp% / their hp% | we healthier (+5) | our K/D | gems lost / won |
|---|---|---|---|---|---|---|---|
| all our openers | 575 | 1.70 vs 2.07 | 23 / 35 / 42% | 94 / 86 | 49% | 0.69 / 0.58 | 3200 / 6482 |
| deliberate | 206 | 1.61 vs 2.12 | 22 / 30 / 48% | 95 / 86 | 50% | 0.83 / 0.51 | 1160 / 2926 |
| they came to us | 162 | 1.66 vs 2.03 | 22 / 38 / 41% | 94 / 87 | 45% | 0.56 / 0.65 | 898 / 1354 |
| other | 114 | 1.69 vs 2.03 | 21 / 43 / 36% | 94 / 79 | 66% | 0.70 / 0.53 | 622 / 1534 |
| we were farming | 93 | 2.00 vs 2.06 | 32 / 32 / 35% | 86 / 89 | 29% | 0.60 / 0.69 | 520 / 668 |
| their openers on us (all) | 521 | 1.97 vs 1.74 (us vs them) | we 43 / 32 / 26% | 89 / 88 | 40% | 0.32 / 0.97 | 5302 / 1950 |

- **We open outnumbered**: in 42% of the real fights we start we have fewer bodies within 6 than the enemy (23% more). Our opener has no ally within 6 in 54% of all our
  openers (626 of 1156; 2 allies 33%, 3+ 13%), while the victim has 2+ allies within 6 in 56%. The opponents open on us with the numbers reversed (they outnumber us 43%,
  outnumbered 26%). Mite opens with a local edge 43% of the time; Uni opens outnumbered 54% but with a 5-body caster line in the enemy half and wins those trades anyway.
- The share of fights **we** open rises when we are behind: ahead 38%, even 56%, behind 67% (collision: 39 / 66 / 82%; elkring 38 / 66 / 79%). I.e. our lone caster pokes
  the enemy group as soon as one enemy walks into 4, and the group answers. Exception: lanes/monolith (we open 25-30% whatever the numbers: there the enemy stack arrives first).
- Hp is not a criterion: our side at 94% vs their 86% is just because our opener is the unhurt one; "we healthier" is a coin flip (49%).
- The deliberate approach is our best category (0.83 / 0.51, +1766 gems) and is still outnumbered 48% of the time: the walk-in is a single champion's decision, the rest
  of the team is elsewhere (our champions within 8 of the fight: 1.9 of 3.9 alive, "split" in 85% of our openers).
- Examples. Deliberate and won: collision `79bed885` r194 (our Stellar walks 7 rounds, spells the tributing enemy Stellar at 100% with 44 gems, Cassi/Issac follow: 1-0, +44);
  corners `2f4101a4` r109 (Tavi spell at 4 on a Varg at 58% with 4 of ours vs 2: 1-0, +48). Deliberate and lost: corners `64d3af95` r532 vs Quantom (Ren stuns a Cassi at 100%
  with 4 of ours vs 5 of theirs: 2-3, -118 gems); packs `5889b79f` r345 vs Univardisty (Stellar pokes a farming Ren at 80%, alone, Cassi 6 tiles back: 0-1).
  Outnumbered opener that still worked: elkring `310b4af7` r304 (lone Stellar spells Issac farming at 88% while Cassi/Issac/Varg are at 50%: 2-0, +36).

## 3. When THEY start: where we were, together or split, gems, what we saw and what we did

| split | n | our dist to own spawn (med) | theirs | fight in our half / middle / their half | we within 3 of an altar | ours within 8 / alive | we are split (ally alive > 8 away) | we carry gems | gems (mean, carriers) | contact rounds before the hit: 1 / 2-3 / 4-7 / 8+ (median) |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 1002 | 15 | 19 | 54 / 32 / 13% | 33% | 2.24 / 4.22 | 83% | 50% | 48 | 0 / 9 / 23 / 68% (13) |
| collision | 221 | 14 | 17 | 48 / 36 / 16% | 38% | 2.36 / 3.33 | 62% | 62% | 42 | 0 / 10 / 24 / 67% (15) |
| corners | 139 | 13 | 17 | 50 / 37 / 14% | 34% | 2.13 / 3.53 | 76% | 35% | 47 | 0 / 6 / 23 / 71% (17) |
| elkring | 118 | 13 | 17 | 53 / 28 / 19% | 23% | 2.19 / 4.52 | 96% | 69% | 50 | 0 / 13 / 19 / 69% (12) |
| interlock | 103 | 15 | 18 | 46 / 46 / 9% | 50% | 2.70 / 4.68 | 86% | 86% | 56 | 1 / 12 / 26 / 61% (10) |
| lanes | 129 | 29 | 42 | 81 / 12 / 7% | 33% | 2.67 / 5.46 | 98% | 43% | 39 | 0 / 6 / 20 / 74% (16) |
| monolith | 112 | 23 | 32 | 53 / 37 / 11% | 31% | 1.62 / 5.71 | 100% | 51% | 56 | 0 / 9 / 33 / 58% (9) |
| packs | 162 | 12 | 15 | 49 / 34 / 17% | 20% | 2.01 / 3.50 | 81% | 14% | 49 | 0 / 6 / 21 / 73% (15) |
| win / loss | 356 / 646 | 15 / 14 | 18 / 19 | 49 / 58% in our half | 37 / 30% | 2.30 / 2.20 | 84 / 83% | 58 / 45% | 48 | 71 / 66% at 8+ |
| top-10 / 11-30 | 369 / 633 | 14 / 15 | 18 / 19 | 53 / 55% | 30 / 34% | 2.17 / 2.28 | 82 / 84% | 45 / 52% | 49 | 64 / 70% at 8+ |

- **They hit us in our half** (54%; their half only 13%) at 15 tiles from our spawn, 33% of the time within 3 of an altar (the altar camps and tribute spot), while they are
  19 tiles from theirs: the opponents come over, we do not. When we open it is 37 / 37 / 26% (Mite 42 / 27 / 31%, Uni 29 / 25 / 46%).
- **We are split in 83% of the fights they start**: 2.2 of our 4.2 living champions are within 8 of the fight; on elkring / lanes / monolith 96-100%. Our n6 at their opener
  is 1 in 41% of cases, 2 in 36%.
- **Gems**: we carry gems in 50% of the fights they open (mean 48 on the carriers; interlock 86%, elkring 69%, collision 62%); 5302 gems were lost in those fights.
- **Vision**: the first hit almost never comes out of nowhere. In 68% of the fights they open, some champion of ours had an enemy within 8 for >= 8 consecutive rounds before
  the hit (median 13 rounds; the count is capped at 39); only 9% of their openers follow a 2-3 round contact. Caveat: "within 8" ignores walls and bushes, so part of this
  is contact without real sight, but on elkring/monolith/lanes (open maps) the shares are the same.

### 3b. What we did in those contact rounds (champion-rounds of the victim side with an enemy within 8, before the first hit)

| victim side | champion-rounds | farming | idle | moved closer | moved away | sideways | recalling |
|---|---|---|---|---|---|---|---|
| us (they open on us) | 44033 | 23% | 16% | 29% | 10% | 18% | 5% |
| opponents (we open on them) | 51238 | 14% | 18% | 33% | 11% | 18% | 7% |

Dominant reaction per fight (>= 2 contact rounds): us: moved closer 49%, kept farming 29%, sideways 12%, idle 8%, recall 1%, moved away 0%; opponents: closer 54%, idle 17%,
farming 14%, sideways 11%, recall 4%, away 0%. So with an enemy in contact we keep farming twice as often as they do (23% vs 14% of champion-rounds, 29% vs 14% of fights),
and "move away" is as rare for us as for them (10-11%): nobody backs off before the first hit, but we are the side that is farming, split and carrying when it lands.
Examples: elkring `d97caaff` r194 vs Univardisty: our Stellar farms the corner camp at (2,3) at 100% hp while Ryth+Tavi walk in from 5 tiles for 18 rounds of contact; Ryth
stuns at 3, our Stellar trades at distance 1 with Ryth for 6 rounds and dies at r202 (0-2); our own Ryth walked the other way (d10) during the approach. interlock
`83a66318` r35 vs lETHal: 8 rounds of contact at the start of the game, 16 of 40 champion-rounds farming, 5v5 at the altar: 0-4, -116 gems. lanes `920d31ac` r75 vs
hinana: 7 rounds of contact, we farm 11 of 28 champion-rounds, their 5 arrive one by one: 0-4.

## 4. Target selection, focus, chasing, spells, ranged distance

| side | rounds with 2+ hitters | same victim | decisions with 2+ enemies in reach | nearest | lowest hp | caster (when available) | gem carrier (when available) | basic attacks | target out of range next round | we then stepped after it |
|---|---|---|---|---|---|---|---|---|---|---|
| us | 852 | 66% | 1946 | 72% | 63% | 63% (n=1291) | 66% (n=946) | 4754 | 44% | 71% |
| them | 896 | 74% | 920 | 77% | 69% | 66% (n=699) | 72% (n=406) | 5025 | 44% | 69% |

- **Focus**: when two or more of our champions hit champions in the same round, they hit the same enemy 66% of the time (Mite 66%, Uni 63%); the opponents in these games
  74%. Our worst focus is on corners (55%, the 5-body brawls) and in losses (62% vs 72% in wins).
- **Target choice** with a choice: nearest 72%, lowest hp 63%; we pick the caster when one is in reach 63% and the carrier 66%; the opponents are a few points higher on every
  criterion (77 / 69 / 66 / 72%) because their decisions are mostly "finish the same target". We make twice as many multi-candidate decisions (1946 vs 920) because our
  champions stand inside the enemy group (section on ranged distance below).
- **Chasing**: 44% of our basic attacks are on a target that is out of range at the end of the next round (same for them), and in 71% of those we step after it. With the
  reference definition (consecutive follow rounds by a champion that hit the victim in the 3 rounds before its first step away): we follow >= 3 steps in 11% of 1916 episodes
  (Mite 12%, Uni 13%; opponents here 14%), 0 steps in 65%; casters 10%, melee 12%; when the victim is below 35% hp 9% (them 11%). Our chases rarely finish anything: the
  victim dies in 18% of the >= 3-step chases vs 33% for theirs, and 11% of our retreat episodes end with the victim dead vs 21% of theirs: they let go as often as we do but
  their last hits land. Long chases are casters walking after a target without casting (elkring `2f3472aa` r160 Stellar follows Issac at 47% for 8 steps, 0 hits; corners `64d3af95`
  r22 Prism follows Varg 5 steps, 0 hits); the opponents' long chases are the same (monolith `40eab0a2` r73 Varg follows Ryth 12 steps, 0 hits).

**Spells**

| side | real fights | cast within 2 rounds of first hit, side that did not open | casts per real fight | champion-rounds with enemy <= 4 and no cast in the previous 8 rounds | cast | walked instead | spell share of champion damage |
|---|---|---|---|---|---|---|---|
| us | 1096 | 79% (of 521 fights they opened) | 5.9 | 2453 | 55% | 19% | 79% |
| them | 1096 | 70% (of 575 we opened) | 5.5 | 3500 | 38% | 32% | 65% |

Per champion (same opportunity definition, both slots surely up, enemy within 4):

| champion | us: n | cast | walked | them: n | cast | walked |
|---|---|---|---|---|---|---|
| Stellar | 562 | 69% | 10% | 645 | 44% | 29% |
| Tavi | 458 | 43% | 36% | 445 | 47% | 26% |
| Ryth | 435 | 58% | 17% | 573 | 31% | 44% |
| Cassi | 283 | 64% | 17% | 357 | 53% | 17% |
| Prism | 216 | 59% | 15% | 106 | 42% | 34% |
| Issac | 205 | 39% | 26% | 568 | 24% | 40% |
| Ren | 177 | 49% | 4% | 265 | 48% | 14% |
| Varg | 72 | 43% | 31% | 308 | 32% | 36% |

- We are the spell-heavier side: 79% of our champion damage is spells (Uni 76%, Mite 62%, opponents here 65%); we fire on cooldown (Stellar 69% of chances, Cassi 64%,
  Prism 59%, Ryth 58%) and the opponents more often walk instead (32% vs 19%; Ryth 44%, Issac 40%, Stellar 29%). Reply speed is fine: in 79% of the fights they open we
  cast within 2 rounds (Mite/Uni's victims: 70%). Note the usage proxy counts only rounds after 8 cast-free rounds, so it under-counts both sides equally; the Mite/Uni
  per-slot numbers (0.6-0.9) are not directly comparable.
- Casting on cooldown without repositioning is the flip side of the next table: our ranged champions stand where they cast.

**Ranged champions: how far from the enemy**

| side | basic attacks at d1 / d2 / d3 | spells at d1 / d2 / d3 / d4 / d5+ | ranged champion fight-rounds | rounds at distance <= 2 |
|---|---|---|---|---|
| us | 16 / 19 / 65% (n=2742) | 5 / 8 / 23 / 56 / 8% (n=3627) | 18497 | 12% |
| them | 7 / 17 / 75% (n=2268) | 1 / 4 / 17 / 61 / 17% (n=2700) | 18014 | 6% |

Our Stellar/Cassi/Tavi/Prism make 35% of their basic attacks at distance 1-2 (953) against 24% (550) for the opponents, cast 36% of their spells from 1-3 (Mite's casters cast
from 3 by choice, but at 3, not 1-2) and only 8% at 5+ (Uni 36-49% of Stellar casts at 5); they spend 12% of their fight rounds within 2 tiles of an enemy (twice the
opponents' 6%). Concretely: a ranged unit that attacks cannot move that turn, so once it is at 2 it stays at 2 (elkring `d97caaff` r199-202: our Stellar trades at distance 1
with Ryth for four rounds and dies; interlock `cabfadde` r399-402 vs VeryGood: our Cassi, 72 gems, steps *toward* an approaching Stellar to distance 2, takes 338+248, starts
a recall at 8% at distance 2 and dies: 0-2, -116 gems).

## 5. Fight length, separation, how fights end, who leaves first

| split | fights | real | length first-last hit med / p75 | single poke | >= 10 rounds | rounds to separation (no enemy within 8) med | ends: kill | wipe | recall | walk away | we leave first | they leave first | same round |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 2158 | 1096 | 4 / 10 | 27% | 28% | 15 | 16% | 14% | 13% | 56% | 26% | 26% | 29% |
| collision | 554 | 293 | 3 / 9 | 29% | 24% | 15 | 14% | 15% | 18% | 53% | 25% | 29% | 28% |
| corners | 356 | 234 | 10 / 21 | 13% | 51% | 22.5 | 22% | 13% | 13% | 50% | 26% | 21% | 34% |
| elkring | 325 | 169 | 3 / 8 | 34% | 20% | 11 | 18% | 16% | 9% | 56% | 27% | 24% | 27% |
| interlock | 208 | 86 | 4 / 10 | 24% | 31% | 16 | 11% | 8% | 12% | 69% | 24% | 31% | 34% |
| lanes | 176 | 71 | 4 / 10 | 28% | 28% | 16 | 19% | 7% | 10% | 63% | 34% | 24% | 28% |
| monolith | 155 | 67 | 3 / 7 | 27% | 13% | 10 | 12% | 21% | 11% | 54% | 19% | 25% | 28% |
| packs | 363 | 170 | 4 / 9 | 31% | 23% | 14 | 13% | 15% | 12% | 57% | 26% | 28% | 25% |
| win / loss | 911 / 1247 | 431 / 665 | 3 / 4 | 31 / 24% | 24 / 30% | 14 / 15 | 14 / 17% | 14 / 14% | 14 / 12% | 57 / 55% | 24 / 27% | 29 / 24% | 28 / 29% |
| top-10 / 11-30 | 677 / 1481 | 338 / 758 | 4 / 4 | 25 / 28% | 28 / 28% | 14 / 15 | 14 / 16% | 15 / 14% | 14 / 12% | 55 / 56% | 27 / 26% | 26 / 26% | 27 / 29% |

("ends" = classification of the last hit: a death in the last 2 rounds = kill; every present champion of a side dead = wipe; otherwise the first side whose champion steps away
after the last hit, with a recall within 6 rounds = recall, without = walk away.)

- Fights are short (median 4 rounds, 27% single pokes; Mite/Uni 5 rounds, 20-22% pokes) and contact ends after a median 15 rounds. Corners is the exception: median 10
  rounds, 51% >= 10, running brawls of 60-78 rounds around the altar (`62365ad4` r221-298 vs PTN Hyperion, 6-4; `5b4a4b49` r65-139 vs VeryGood, 0-2; `f159c312` r576-637
  vs geese, 1-4).
- 30% of all fights end with a death (kill 16% + wipe 14%; real fights: 58%); 56% end with one side walking off and 13% with a recall. Who leaves first is symmetric
  (26% / 26% / same round 29%) and does not depend on who opened (we leave first in 15-17% of real fights, they in 21-22%, same round 25-27%). When we leave it is a walk
  77% / recall 23%; theirs 66% / 34%: the opponents recall out of fights more, we walk and come back.
- **Wipes**: in the real fights they open we get wiped 103 times and wipe them 37; in the ones we open 69 vs 94. A recall was started by one of our participants between the
  last hit and separation in 869 fights, by theirs in 974.

**Retreat under fire** (first step away with an enemy within 4 and damage taken in the previous 3 rounds; `chase.py`):

| side | n | hp% at the step med (p25-p75) | < 30% | < 50% | >= 70% | kite (hits again within 8 rounds) | outnumbered | recall within 10 | recall completed | recall distance to nearest enemy | died within 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| us | 1046 | 49 (31-71) | 22% | 51% | 26% | 21% | 31% | 50% | 85% | 6 | 19% |
| them | 1334 | 47 (31-66) | 23% | 53% | 22% | 14% | 34% | 52% | 88% | 7 | 11% |
| Mite / Uni | 274 / 318 | 38 / 47 | 33 / 22% | 69 / 53% | 15 / 25% | 17 / 33% | 35 / 52% | 56 / 28% | 87 / 76% | 7 / 8 | 16 / 20% |

By hp band, us (n, died, recalled, kite): 0-30%: 230, 28%, 76%, 5%; 30-50%: 300, 20%, 74%, 10%; 50-70%: 239, 17%, 39%, 21%; 70%+: 277, 13%, 13%, 45%.
Them: 0-30%: 310, 19%, 78%, 3%; 30-50%: 392, 8%, 69%, 8%; 50-70%: 335, 11%, 40%, 19%; 70%+: 297, 5%, 18%, 29%.
By class: our melee step away at 49% and die 13% (n=656), our casters at 50% and die **30%** (n=390); their melee 49% / 10%, casters 44% / 13%.

- We step out at the same hp as the opponents (49 vs 47, Uni 47) and recall from 6 tiles with the same completion (85 vs 88%), but we die after the step twice as often
  (19% vs 11%), and the whole gap is the casters (30% vs 13%): a Stellar/Cassi that is already at distance 1-2 when it decides to leave cannot get out (section 4). In the
  30-50% band we die 20% vs 8%.
- We kite more (hit again within 8 rounds: 21% vs 14%; at >= 70% hp 45%): the bot steps back one tile after a spell and comes back for the next one.

## 6. Per opponent (real fights)

| opponent (rank) | W-L | real fights | we hit first | our kills | our deaths | gems lost / won |
|---|---|---|---|---|---|---|
| Intercontinental Fish (1) | 0-5 | 30 | 50% | 6 | 52 | 202 / 80 |
| Mite (2) | 2-3 | 35 | 46% | 20 | 24 | 284 / 176 |
| Shawn (3) | 1-4 | 37 | 54% | 15 | 36 | 402 / 374 |
| Univardisty (4) | 1-4 | 36 | 39% | 6 | 35 | 300 / 44 |
| VeryGood (5) | 0-5 | 37 | 22% | 1 | 31 | 500 / 0 |
| hello (6) | 1-4 | 42 | 31% | 17 | 37 | 412 / 108 |
| PTN Hyperion (7) | 1-4 | 35 | 54% | 44 | 46 | 274 / 494 |
| Nyxius (8) | 1-4 | 12 | 67% | 9 | 4 | 0 / 66 |
| procless (9) | 1-4 | 31 | 29% | 10 | 17 | 162 / 66 |
| Quantom (10) | 2-3 | 43 | 63% | 20 | 30 | 446 / 482 |
| Full Damage (11) | 1-4 | 33 | 36% | 11 | 17 | 336 / 248 |
| (hieroglyphs) (12) | 4-1 | 47 | 64% | 39 | 23 | 226 / 674 |
| geese geese go (13) | 1-4 | 67 | 63% | 36 | 63 | 516 / 532 |
| KratosMessi (14) | 3-2 | 29 | 69% | 13 | 17 | 154 / 388 |
| Boost (15) | 1-4 | 25 | 28% | 8 | 22 | 386 / 22 |
| lETHal (16) | 0-5 | 32 | 44% | 11 | 33 | 482 / 88 |
| test (17) | 5-0 | 31 | 42% | 15 | 27 | 540 / 350 |
| getramramd#euw (18) | 3-2 | 29 | 69% | 21 | 13 | 88 / 380 |
| Still Testing (19) | 3-2 | 44 | 61% | 37 | 11 | 66 / 718 |
| Conley (20) | 2-3 | 34 | 29% | 7 | 41 | 134 / 0 |
| hinana (21) | 1-4 | 44 | 61% | 17 | 46 | 656 / 138 |
| AlphaSlop (22) | 4-1 | 37 | 65% | 29 | 14 | 96 / 314 |
| octo's odyssey (23) | 3-2 | 30 | 57% | 36 | 8 | 48 / 334 |
| Nyx (25) | 3-2 | 43 | 74% | 29 | 23 | 140 / 176 |
| umamusume (26) | 3-2 | 49 | 57% | 14 | 35 | 468 / 338 |
| BottleBots (27) | 1-4 | 44 | 52% | 25 | 46 | 504 / 486 |
| Ely2sh (28) | 2-3 | 54 | 48% | 16 | 50 | 434 / 190 |
| SSSA (29) | 2-3 | 27 | 67% | 14 | 15 | 154 / 326 |
| WHIM (30) | 2-3 | 45 | 58% | 26 | 22 | 48 / 472 |
| MicroStella (249) | 5-0 | 14 | 71% | 13 | 2 | 44 / 368 |

VeryGood (1-31, we open 22%), Intercontinental Fish (6-52), Univardisty (6-35) and Conley (7-41) do not let us open and kill us when they do; against VeryGood we won
0 gems in fights. The teams we beat in fights are the ones we out-open (Still Testing 61%, octo 57%, AlphaSlop 65%, hieroglyphs 64%). PTN Hyperion is the only top-10 team
we trade evenly with (44-46), in 60-78-round corners brawls.

## 7. Worked examples (round-by-round from `timeline.py`)

**A. elkring `d97caaff` r180-202 vs Univardisty (rank 4), they open, 0-2.** Our Stellar1 farms the camp at (2,3) at 42% -> 100% hp (spawn heal at r190) while enemy Ryth7
(81%) and Tavi9 walk in from 5 tiles over 18 rounds; our Tavi4 at 72% -> 34% walks west past them; our Ryth0 walks away east to distance 10 and never comes back. r194:
Ryth7 area-stun at 3 hits Stellar1 and Tavi4 (220). r195-198: Stellar1 answers (319 spell + attack) but stays at distance 3 then walks to distance 1 of Ryth7; r199-202:
trades basics at distance 1 against Ryth + Tavi at 3, takes 205+120+230 and dies at r202 at (0,3), having never stepped away.

**B. collision `ae2470ab` r792-808 vs Full Damage (rank 11), they open, 0-2, -146 gems.** Our Cassi0 stands at (26,21) with 146 gems at 100% hp for 5 rounds while
Prism5 walks from distance 8 to 4; Issac1 dashes away at r795. r797-798: Prism spells 544 + 362 (Cassi at 14%). r799: Cassi *starts a tribute* at 14% hp with the Prism at 4.
r800-804: Prism steps to 3 and finishes her with four basic attacks of 31 while she does nothing; Issac dies with her (paired champion). Ren2 arrives at r805 and
trades 596 for 389 at distance 4. Nothing in the 12 rounds of contact made the Cassi move.

**C. interlock `cabfadde` r394-402 vs VeryGood (rank 5), they open, 0-2, -116 gems.** Cassi0 (91%, 72 gems) idles at (10,18) while Stellar5 walks from 8 to 3; at r399-400
Cassi steps *toward* it to distance 2, takes 338 + 248, starts a recall at 8% at distance 2 (r401) and dies at r402. Tavi4 keeps farming 9 tiles away for the whole episode.

**D. corners `62365ad4` r221-298 vs PTN Hyperion (rank 7), we open, 6-4.** Stellar spell at 4 on a recalling Issac at 62%; 5v6 brawl around the altar for 78 rounds,
each side casts on cooldown, 5164 vs 3766 damage; the fight ends when the last of their participants is dead. The one time the whole team is present the trade is positive.

**E. collision `79bed885` r194 vs MicroStella (rank 249), we open, 1-0, +44.** The textbook opener: Stellar walks 7 rounds, spells a tributing Stellar at 100% with 44 gems
at range 4, Cassi + Issac are within 6 (3 v 1), the target dies in 4 rounds, nobody chases.

## 8. Observed rules of our bot in fights (what a reader would infer from the numbers)

Measured = read directly from a table above; inferred = consistent with the numbers but not isolated as a condition.

1. (measured) **Open with a damage/stun spell at exactly range 4 on the first enemy that enters range**: 89% spell openers, 62% at distance 4, 3% at 5 (no "place the AoE
   at 4 to reach 5"); opener champion: Stellar 322, Ren 307, Cassi 158, Ryth 126, Tavi 122, Prism 66, Issac 33 (of 1156). The opener is at full hp (median 100%, 2% below 50%).
2. (measured) **No numbers check and no hp check**: 42% of our real openers are outnumbered within 6 (23% outnumbering), our opener has no ally within 6 in 54% of
   openers, our hit-first share is highest when behind (67%) and lowest when ahead (38%); "we healthier" 49%.
3. (measured) **Target = nearest enemy in reach (72%), isolated preferred (56% vs 38% baseline)**, low hp not sought (14% vs 24% available); recalling enemies are hit
   when seen (10% of openers) and those are our best fights (1.34 / 0.56).
4. (measured) **Keep doing the current job while enemies are in contact**: in the 13-round median contact before they hit us, 23% of our champion-rounds are farming,
   16% idle, 10% moving away; the dominant per-fight reaction is "move closer" (49%) or "keep farming" (29%); tributes and recalls are started with an enemy at 4
   (example B).
5. (measured) **Cast every spell as soon as it is up**: 55% of both-slots-up opportunities with an enemy within 4 (Stellar 69%, Cassi 64%), reply within 2 rounds in
   79% of the fights they open, 79% of our champion damage is spells.
6. (measured) **Ranged units do not hold range**: 35% of ranged basic attacks at distance 1-2 (953 of 2752), 36% of spells from 1-3 (1324 of 3627), 12% of ranged fight-rounds within 2 of an enemy
   (opponents 6%); they walk toward the current target until it is in basic-attack range and then cannot move on attack turns.
7. (measured) **Loose focus**: 66% same victim when 2+ of ours hit in a round (55% on corners, 62% in losses); the opponents 74%.
8. (measured) **Step away at ~50% hp, recall from 6 tiles** (85% completion), kite back in at >= 70% (45%); no hp-based difference between melee (49%) and casters (50%).
9. (measured) **Do not chase**: 11% of hitter-retreat episodes have >= 3 follow steps, 65% none; the follow steps that do happen are casters walking without casting.
10. (inferred) **Arrive one at a time**: 85% of our openers and 83% of theirs find our team split (ally alive > 8 away); 1.9 of 3.9 living champions near the fight. The bot
    converges on a target rather than regrouping first (Mite/Uni do the same, 6 tiles apart at the hit, but with 3 bodies vs our 1.6-1.7 within 6).

## 9. The five biggest differences from the opponents in the same games (each with counts)

1. **The opener's conversion.** Opener-side kills / deaths per real fight: opponents opening on us 0.97 / 0.32 (505 of our deaths in 521 fights, they win 57% of them), us
   opening 0.69 / 0.58 (335 deaths in 575 fights, we win 39%). Mite/Uni as openers: 0.74 / 0.46-0.52. Our openers on a *walking* enemy (341 fights, 59% of our real openers)
   are a net loss (0.57 / 0.64); theirs on ours (308) are 0.96 / 0.32.
2. **Numbers at the first hit.** We open outnumbered within 6 in 42% of our real openers (239 of 575) and outnumbering in 23% (135); they open on us outnumbering 43%
   (222 of 521), outnumbered 26% (134). Our opener is alone within 6 in 626 of 1156 openers (54%); theirs in 595 of 1002 (59%) but with our n6 lower (1.74 vs their 2.07 when we open).
   Put differently: our hit-first share is 67% when behind and 38% when ahead; the opponents' is the mirror image.
3. **Where ranged units stand.** 953 of our 2752 ranged basic attacks (35%) are at distance 1-2 vs 550 of 2272 (24%) for theirs; 1324 of 3627 of our spells (36%) from 1-3 vs
   599 of 2700 (22%); 2196 of 18497 ranged fight-rounds (12%) within 2 of an enemy vs 1113 of 18014 (6%). Only 8% of our spells reach 5+ (279) vs 17% (458) for theirs.
4. **Dying after deciding to leave.** 19% of our 1046 under-fire retreats end in death within 12 rounds vs 11% of their 1334; casters 30% (n=390) vs 13% (n=409);
   30-50% hp band 20% (n=300) vs 8% (n=392). Same hp at the step (49 vs 47), same recall distance (6 vs 7) and completion (85 vs 88%): the difference is where
   the champion is standing when it decides (point 3).
5. **What the victim side was doing before the hit.** When they open on us, 23% of our contact champion-rounds (9,969 of 44,033) are farming and 16% idle; when we open on
   them 14% (6,988 of 51,238) and 18%. Per fight, "kept farming" is our dominant reaction in 29% (293 of 1001) vs 14% (163 of 1150) for them, and they catch us farming in
   191 openers (19%) vs 146 (13%) the other way, with the richer outcome (0.95 / 0.22 for them, 0.81 / 0.42 for us). Added to that, focus: 74% same-victim rounds for
   them (667 of 896) vs 66% for us (564 of 852).

Everything else is close to symmetric: chase (11 vs 14%), retreat hp (49 vs 47%), recall completion (85 vs 88%), who leaves first (26 / 26 / 29% same round), fight length,
spell timing (we are even faster: 79 vs 70% cast within 2 rounds). The opponents do not out-micro us in the moment of the exchange; they arrive with one more body, keep
their casters at 4-5, and finish what they start.
