# Farm cycle and economy, study27 vs study26 (155 + 150 games vs the top 30, 2026-10-15 12:37 and 11:33 UTC)

Data: study27 = study26 + stacking (`P_STACK_HP 3000`, `P_SHAREEXP 75`, `P_MAX_SHARE 4`: on a camp group of 3000+ hp a joiner values it at
gems / team^0.75 instead of an even split, up to 4 champions; smaller camps keep the even split). 155 unranked games from `$S/ws3/selected.json`
(150 side a, 5 side b), decoded every step into `$S/ws3/steps/*.c.jsonl`; study26 = the 150 games of `$S/ws2/` dissected in `farming.md`.
Same scripts, now parameterised by `FARM_WS` (data dir) and `FARM_OUT` (extract dir): `$S/ws2/scripts_farm/extract.py` -> `out27/<match>.json`,
`q1..q11` -> `out27/q*.md`, `cmp.py` (side by side) -> `out27/cmp.md`, `finish.py`, `rows_more.py`, `rows_end.py`, `rows_tail.py` -> `out27/*.md`.
New this time: `q11_stack.py` (champions within 3 tiles of the group during the attack window, stack lag, deaths by cause, idle near camps), run on
both batches (`out27/q11.md`, `out27/q11_study26.md`). All tables below are "us27 / us26 / opp27 / opp26" unless stated; "cr" = champion-round.
The opponents are the same 30 teams minus SSSA, MicroStella, WHIM plus Palestine (#54), Mate in One (#28), EMPEROR Tung (#30), Cabbage (#16),
but the per-map pairings are different, so per-map records on 9-22 games move by +-3 wins from pairing alone (binomial sd ~2.2 on 19 games).

One engine fact that frames everything: **every game ends when a team banks 1000 gems** (all 155 games; rows 351-442 rounds, expanse 325-398,
lanes 311-485, collision 518-1086). The farm race is a race to 1000, and "gems in hand when the opponent finishes" is the cost of unbanked gems.

## Short answer

1. **The stacking happened online exactly where the rule applies.** On 3000+ hp groups: 3.18 attackers per capture vs 2.72 in study26 (opponents 2.57),
   4 attackers in 143 of 316 captures (45%) vs 18 of 301 (6%), solo captures 7 vs 34; 4+ champions physically on the camp in 47% of the attack windows
   vs 0%. Rows (4050-hp wolf camps, 295 captures): 3.26 vs 2.66 attackers, hit-to-capture **19.6 vs 25.2 rounds mean** (median 19 vs 21), the whole
   team on the first camp (3.94, r33 vs 3.00, r36), second hitter within 2 rounds 66% vs 53%, third hitter 4 vs 6 rounds after the first.
   Expanse's 3900-hp elk+cluster: 2.11 vs 1.00 attackers, 21 vs 24 rounds, 1.12 vs 0.88 captures/game. Collision's 108-gem 3900-hp group: still
   not farmed (2 captures in 19 games, 1.5 attackers; opponents 1.68/game). The rule also fired on elkring's 2900-hp elk+gold_cluster groups
   (opening 4 attackers in 9/9 games vs 3 in 14/14; 33 four-stacks of 230 captures vs 15 of 333) although the replay's group hp is 2900 < 3000.
2. **It sped the kills on rows and the stack decays after r200.** Rows hit-to-capture by phase 24 / 19 / 17 / 17 rounds (r0-99 / 100-199 / 200-299 /
   300+) vs 32 / 24 / 17 / 21; four-stacks 48 of 50, 63 of 69, 31 of 82, **0 of 94** captures. After r300 we farm the 4050 wolves in pairs (42 of 94) as before
   (26: 18 solo + 60 pairs of 107). Net: rows captures 17.4 vs 15.8 per game (opponents 17.0), tributed 961 vs 891 (opp 1037), our 14th tribute at r380 vs r397,
   our 1000 at r403 vs r421 in the wins. Rows went 3-14 (26: 4-14): 11 of the 14 losses end 957-1056 (one bag short, 99-165 gems in hand) where study26
   lost 792-1056 (four bags short) in 8 of 14.
3. **It cost nothing measurable elsewhere**: deaths 5.8 vs 5.7 per game (opponents 4.0 vs 3.9), deaths to monsters 22 vs 25, deaths to champions within 4
   tiles of a live camp 45 vs 49; small camps 17 / 23 / 24 rounds hit-to-capture (< 800 / 800-1500 / 1500-3000) vs 16 / 22 / 24, single-attacker shares
   87 / 61 / 27% vs 84 / 60 / 25% (same); idle 8.0% of cr vs 8.4%, idle within 3 tiles of a live camp 92 vs 100 cr per game; walking efficiency 0.89 both.
   The economy as a whole is unchanged: captures per 100 cr alive 1.15 vs 1.19, captured gems per 100 cr 41.1 vs 41.7 (opponents 43.4 / 43.1),
   tributed 800 vs 808 per game, 13.5% vs 13.6% of cr dead. 58-97 vs 59-91 is the same bot with different pairings on 8 maps and a better rows.
4. **Why rows is still 3-14**: the opponents bank 1000 between r351 and r401 (14 of 17 games, median r392, the same as against study26) and we bank it at r403.
   We gained 18 rounds and need ~15 more. The 18 rounds came from the first 200 rounds (10th tribute r297 vs r303, banked gems equal at r300: 685 vs 688);
   the last 100 rounds are where the game is lost (r400: 940 vs 1021), because (a) the stack dissolves and the late wolves are killed in pairs,
   (b) the last bags detour through the shop: 2.0 shop recalls per game start in the final 30 rounds (26: 1.33), e.g. vs Mite three champions recall to buy
   9 shards each at r380, r385 and r391 of a 398-round game, (c) 33-gem split shares (32 captures) are carried 60 rounds (median) to the next camp and
   banked as 99-gem bags whose channel takes 10 rounds, (d) every rows camp is 24-36 tiles from the altar, so a bag captured after ~r375 cannot land before
   r400 either way. When the opponent's 16th bag lands we hold 165 gems (median; 26: 99): 2.5 camps captured and not banked.

## 1. Economy curve and finish line (27 ; 26)

Tributed gems at round marks, us/opp (`cmp.md` C1):

| map | n 27/26 | r100 | r200 | r300 | r400 | decided round med | mean rounds |
|---|---|---|---|---|---|---|---|
| collision | 19/19 | 46/47 ; 49/37 | 131/127 ; 149/92 | 197/236 ; 245/184 | 313/306 ; 371/280 | 139 ; 142 | 753 ; 742 |
| corners | 19/17 | 122/42 ; 118/69 | 242/201 ; 248/210 | 341/337 ; 371/365 | 469/462 ; 482/498 | 62 ; 123 | 558 ; 565 |
| elkring | 9/14 | 96/118 ; 98/89 | 240/232 ; 217/258 | 370/410 ; 336/431 | 518/570 ; 482/597 | 444 ; 239 | 627 ; 591 |
| expanse | 17/17 | 207/189 ; 207/176 | 488/425 ; 488/427 | 755/725 ; 758/734 | 937/960 ; 942/931 | 324 ; 324 | 366 ; 349 |
| interlock | 19/13 | 118/132 ; 118/123 | 290/302 ; 320/285 | 472/469 ; 496/507 | 648/624 ; 684/712 | 191 ; 221 | 499 ; 479 |
| lanes | 17/18 | 134/128 ; 140/146 | 343/437 ; 370/409 | 556/729 ; 626/705 | 697/965 ; 803/955 | 168 ; 242 | 378 ; 398 |
| monolith | 16/13 | 155/89 ; 151/92 | 342/287 ; 323/316 | 547/535 ; 566/525 | 781/823 ; 780/816 | 339 ; 304 | 448 ; 448 |
| packs | 22/21 | 123/139 ; 133/131 | 259/320 ; 261/298 | 402/508 ; 418/492 | 574/736 ; 590/698 | 216 ; 190 | 494 ; 506 |
| rows | 17/18 | 132/107 ; 132/106 | 396/383 ; 378/374 | **685/688 ; 583/675** | **940/1021 ; 869/975** | 385 ; 342 | 392 ; 402 |

Finish line (`finish.md`): round at which we bank 1000 in our wins ; round at which the opponent banks 1000 in our losses ; gems we are short in
losses (and in hand):

| map | study27 | study26 |
|---|---|---|
| collision | 8 wins r675 ; 11 losses r737 ; short 648 (22) | 12: r704 ; 7: r696 ; short 722 (22) |
| corners | 8: r556 ; 11: r550 ; short 738 (0) | 5: r448 ; 12: r542 ; short 544 (0) |
| elkring | 5: r644 ; 4: r588 ; short 262 (72) | 5: r590 ; 9: r589 ; short 388 (72) |
| expanse | 10: r375 ; 7: r343 ; short 180 (108) | 11: r355 ; 6: r332 ; short 180 (96) |
| interlock | 10: r502 ; 9: r487 ; short 260 (22) | 7: r468 ; 6: r470 ; short 389 (33) |
| lanes | 3: r396 ; 14: r372 ; short 321 (44) | 3: r422 ; 15: r378 ; short 198 (48) |
| monolith | 5: r462 ; 11: r433 ; short 114 (88) | 5: r455 ; 8: r445 ; short 212 (51) |
| packs | 6: r496 ; 16: r488 ; short 228 (0) | 7: r514 ; 14: r486 ; short 278 (0) |
| rows | **3: r403 ; 14: r392 ; short 43 (165)** | 4: r421 ; 14: r392 ; short 208 (99) |

- Rows is the only map where the curve moved: equal with the opponent through r300 (685 vs 688; study26 583 vs 675), then 940 vs 1021 at r400.
  The lost rows games are decided late (median r385 of 392) and by one bag.
- Every other map is within pairing noise: the biggest swings are collision 12-7 -> 8-11 (we are ahead at r100-r200 in both batches; 12.6 vs 11.3 deaths/game)
  and lanes r300 556 vs 626 (five games with 8-10 deaths: Univardisty 16 captures, umamusume 16, Conley 23, Cabbage 26, Boost 29; lanes has no 3000-hp group).
- Opponent tiers: top-10 15-35 (26: 10-40), 11-20 15-35 (23-27), 21-30 23-27 (21-24).

## 2. Rates (us27 / opp27 / us26 / opp26)

| split | n | captures/game | captures/100cr | gems/capture | captured gems/100cr | tributed/game | deaths/game | % lost at death | % in hand at end |
|---|---|---|---|---|---|---|---|---|---|
| all | 155/150 | 23.8 / 26.7 / 24.5 / 26.7 | 1.15 / 1.22 / 1.19 / 1.21 | 35.6 / 35.6 / 35.1 / 35.5 | 41.1 / 43.4 / 41.7 / 43.1 | 800 / 899 / 808 / 907 | 5.8 / 4.0 / 5.7 / 3.9 | 7 / 7 / 6 / 6 | 6 / 4 / 5 / 4 |
| rows | 17/18 | **17.4 / 17.0 / 15.8 / 17.2** | 0.88 / 0.86 / 0.79 / 0.86 | 62.4 / 64.4 / 62.5 / 62.8 | **55.2 / 55.7 / 49.3 / 54.2** | 961 / 1037 / 891 / 1034 | 0.1 / 0.0 / 0.1 / 0.3 | 0 / 0 / 0 / 0 | **11 / 6 / 10 / 5** |
| expanse | 17/17 | 23.9 / 26.2 / 24.9 / 24.6 | 1.63 / 1.79 / 1.78 / 1.77 | 41.1 / 38.5 / 40.4 / 39.8 | 66.9 / 68.9 / 72.0 / 70.3 | 937 / 960 / 942 / 931 | 0.0 / 0.1 / 0.0 / 0.1 | 0 / 0 / 0 / 0 | 5 / 5 / 7 / 5 |
| lanes | 17/18 | 32.8 / 42.5 / 37.9 / 42.5 | 1.59 / 1.93 / 1.75 / 1.87 | 23.5 / 23.9 / 23.7 / 24.2 | 37.3 / 46.3 / 41.4 / 45.4 | 720 / 985 / 839 / 998 | 3.8 / 0.8 / 3.8 / 1.4 | 3 / 1 / 2 / 1 | 6 / 4 / 6 / 3 |
| packs | 22/21 | 17.4 / 22.9 / 18.0 / 21.8 | 1.09 / 1.29 / 1.09 / 1.23 | 44.9 / 43.0 / 45.1 / 43.4 | 49.0 / 55.5 / 49.3 / 53.5 | 752 / 968 / 781 / 943 | 7.1 / 2.4 / 7.0 / 3.8 | 3 / 2 / 3 / 2 | 3 / 2 / 2 / 1 |
| collision | 19/19 | 31.4 / 30.8 / 32.6 / 29.7 | 1.36 / 1.30 / 1.41 / 1.27 | 22.5 / 27.1 / 22.4 / 26.6 | 30.6 / 35.2 / 31.5 / 33.8 | 699 / 752 / 774 / 674 | 12.6 / 8.8 / 11.3 / 8.5 | 19 / 21 / 14 / 22 | 4 / 5 / 3 / 4 |
| win | 58/59 | 28.2 / 23.3 / 29.1 / 24.4 | 1.24 / 1.10 / 1.33 / 1.17 | | 43.9 / 38.7 / 45.5 / 40.4 | 1023 / 685 / 1018 / 727 | 3.1 / 6.7 / 3.3 / 6.0 | 4 / 14 / 4 / 12 | |
| loss | 97/91 | 21.2 / 28.6 / 21.5 / 28.2 | 1.09 / 1.29 / 1.09 / 1.24 | | 39.2 / 46.1 / 38.9 / 44.7 | 667 / 1027 / 673 / 1024 | 7.4 / 2.5 / 7.3 / 2.5 | 10 / 3 / 9 / 2 | |

The full per-map / per-tier table is in the appendix (C2). Rows is the one map where our per-alive-round economy changed: 55.2 vs 49.3 gems per 100 cr,
now equal to the opponents' 55.7. Expanse 66.9 vs 72.0 and lanes 37.3 vs 41.4 are the two moves against us; expanse's opponents also moved (68.9 vs 70.3),
lanes is the five death-heavy games above.

## 3. Squad size and kill speed by group hp (the stacking check)

| group hp | captures | attackers mean | hit->capture med | mean | single attacker | >= 3 attackers | >= 4 attackers | max champions on the camp (q11) | >= 4 on camp |
|---|---|---|---|---|---|---|---|---|---|
| < 800 | 356 / 536 / 466 / 563 | 1.14 / 1.36 / 1.16 / 1.44 | 17 / 15 / 16 / 15 | 18.8 / 16.7 / 17.7 / 16.1 | 87% / 68% / 84% / 65% | 1% / 4% / 1% / 7% | 0% / 0% / 0% / 1% | 2.31 / 2.22 / 2.34 / 2.37 | 3% / 7% / 6% / 12% |
| 800-1500 | 1923 / 2004 / 1789 / 1804 | 1.51 / 1.83 / 1.51 / 1.82 | 23 / 21 / 22 / 22 | 30.6 / 28.8 / 29.4 / 30.9 | 61% / 47% / 60% / 49% | 9% / 21% / 8% / 20% | 2% / 7% / 2% / 8% | 2.18 / 2.25 / 2.19 / 2.23 | 13% / 14% / 12% / 16% |
| 1500-3000 | 1099 / 1255 / 1120 / 1286 | 2.01 / 2.31 / 2.03 / 2.27 | 24 / 23 / 24 / 23 | 29.9 / 29.1 / 32.0 / 30.8 | 27% / 25% / 25% / 28% | 22% / 38% / 26% / 37% | 6% / 14% / 2% / 13% | 2.17 / 2.36 / 2.15 / 2.32 | 9% / 14% / 8% / 15% |
| **>= 3000** | 316 / 336 / 301 / 350 | **3.18** / 2.72 / 2.57 / 2.69 | 20 / 22 / 21 / 22 | **19.9** / 28.5 / 25.4 / 27.1 | **2%** / 20% / 11% / 19% | **75%** / 63% / 63% / 60% | **45%** / 24% / 6% / 23% | **3.28** / 2.76 / 2.54 / 2.77 | **47%** / 25% / 0% / 26% |

Attackers on >= 3000-hp groups, count by 1 / 2 / 3 / 4 / 5+: us27 7 / 73 / 93 / 143 / 0; us26 34 / 78 / 171 / 18 / 0; opp27 67 / 58 / 131 / 62 / 18.
By map (q11): rows us27 295 captures, 3.26 attackers (4 / 58 / 91 / 142), hit->capture 19 med 19.6 mean, vs us26 285, 2.66 (18 / 78 / 171 / 18), 21 / 25.2,
opponents 2.96 (31 / 48 / 130 / 62 / 18), 21 / 23.6; expanse 3900-hp group us27 19 captures, 2.11 attackers (2 / 14 / 2 / 1), 21 rounds, vs 15 captures
all solo at 24 rounds; collision 9o 2 captures (1 solo, 1 pair, 52 rounds) vs 1 solo at 85, opponents 32 captures (1.31 attackers, 30 med).
Stack lag on >= 3000 hp (first hit to the 2nd / 3rd attacker's first hit): 2 / 4 rounds median (means 2.6 / 5.3) vs 2 / 6 (2.9 / 13.7); 2nd hitter within 2
rounds 66% vs 53% (opponents 65%). The pair / triple arrive together now; before, the third came 14 rounds later on average.
Damage per attacker-round on the big camps dropped from 79 to 64 (opponents 68): four champions around a 3-tile camp hit less often each; the kill
is still 5.5 rounds faster.

The rule spilled to 1500-3000 hp groups: >= 4 attackers in 57 captures (6%) vs 19 (2%): elkring 33 of 230 (26: 15 of 333) and packs 24 of 382 (8 of 377),
both maps whose groups are 2700-2900 hp (elkring elk + gold cluster 2900, packs wolves 2700). Elkring's opening is deterministic: r21x4, r37x4, r67x3 in
9/9 games vs r25x3, r36x3, r61x3 in 14/14. The bot's group hp for these groups is apparently not the replay's 2900 (worth a check in `squad` code);
the effect on elkring is a 4-round earlier first capture and hit->capture 30.1 vs 32.7 mean (5-4 vs 5-9, 9 games).

First camp per map (attackers / first capture round / hit->capture; us27, us26, opp27): rows 3.94 / r33 / 23, 3.00 / r36 / 25, 4.88 / r31 / 20;
elkring 4.00 / r21 / 18, 3.00 / r25 / 20, 4.78 / r19 / 17; corners 2.16 / r37 / 18, 2.53 / r41 / 22, 2.95 / r28 / 18; collision 2.00 / r33 / 18 both, opp 2.68 / r18;
packs 2.18 / r33 / 19, 2.14 / r33 / 19, 3.23 / r24; interlock, expanse, lanes, monolith unchanged (2.00 / 2.00 / 1.00 / 3.00). Our first capture is still
5-15 rounds after the opponents' on collision, corners, packs and expanse (r30 vs r25).

## 4. Rows cycle (us27 / us26 / opp27 / opp26)

Captures per 50-round bin per game, then totals:

| team | r0-49 | r50-99 | r100-149 | r150-199 | r200-249 | r250-299 | r300-349 | r350-399 | captures/game | gems in hand at end | tributed/game |
|---|---|---|---|---|---|---|---|---|---|---|---|
| us27 | 1.00 | **1.94** | 2.06 | 2.00 | **2.82** | 2.00 | 3.00 | 2.41 | 17.4 | **118** | 961 |
| us26 | 1.00 | 1.00 | 3.00 | 1.89 | 1.00 | 2.00 | 3.67 | 1.61 | 15.8 | 95 | 891 |
| opp27 | 1.06 | 2.12 | 2.00 | 2.47 | 2.06 | 2.53 | 2.35 | 2.29 | 17.0 | 62 | 1037 |
| opp26 | 1.06 | 2.11 | 2.11 | 2.11 | 2.22 | 2.50 | 2.44 | 2.11 | 17.2 | 51 | 1034 |

- The burst pattern of study26 (1 / 1 / 3 / 1.9 / 1 / 2 / 3.7) became the opponents' steady 2 per 50 rounds; the opening is now r33x4, r58x4, r88x4, r116x4
  in 15 of 17 games (26: r36x3, r63x3, r103x3, r125x3 in 18/18).
- By phase (attackers 1/2/3/4, hit->capture med / mean): r0-99 0/0/2/48, 24 / 24.1 (26: 0/0/36/0, 32 / 32.0); r100-199 0/0/6/63, 19 / 20.4 (0/0/70/18, 24 / 32.4);
  r200-299 0/16/35/31, 17 / 18.4 (0/18/36/0, 17 / 17.6); **r300+ 4/42/48/0, 17 / 17.8** (18/60/29/0, 21 / 20.9). Opponents r300+: 12/21/37/11, 17 / 20.0.
  The stack is intact while the champions are synchronised; after r200 the 180-gold shop recalls (5.8 per game in r200-299, 5.1 in r300+) and the 40-round
  camp respawns spread the five champions over the three camps and the last 94 captures are pairs and triples with nobody at four.
- Banking timeline (median round of the k-th completed tribute, us vs opp): 10th r297 vs r279 (26: r303 vs r293), 12th r329 vs r325 (r340 vs r337),
  13th r349 vs r340 (r395 vs r356), **14th r380 vs r360 (r397 vs r377)**, 15th r403 (3 games) vs r385, 16th r404 (1) vs r398. Our 13th and 14th bags
  moved 46 and 17 rounds earlier; the opponents' schedule did not move.
- Revisit after a respawn: rows 29 rounds median vs 22 (opponents 22 / 23); all maps 33 / 33. Camp utilisation on our three rows groups: 60% respawning /
  21% up and untouched / 19% under attack (26: 55 / 25 / 20; opponents 62 / 17 / 21). Nearest-up camp chosen 46% vs 44% (opp 51%).
- Bags: 66 in 219 of 238 tributes, 99 in 19 (26: 231 and 8); captures per bag 1.10 vs 1.09 (opp 1.21, with 19 bags of 132); 33-gem split captures 32 vs 30,
  carried 60 rounds median (mean 101) before they are banked vs 54 (50). Oldest gems at a tribute start 10 rounds median vs 14 (opp 14).
- Shop recalls on rows: 19.3 recall starts per game (26: 21.9), of which 2.0 per game start in the last 30 rounds of the game, all of them shop trips (26: 1.33).
- Time (rows): walk 51.7% / at a camp 29.2% / idle 7.7% / tribute 5.3% / recall 4.9% vs 53.2 / 25.6 / 9.3 / 5.2 / 5.5; opponents 48.5 / 25.8 / 9.2 / 5.7 / 10.0.

The Mite game (`rows_tail_mite.md`, lost 957-1056 at r398): Varg keeps a 33-gem share from r353, solos the far 4050 wolf at 300-600 hp (34-36 tiles from the
altar) for 27 rounds, captures at r379 (99 gems), recalls r375-380, buys 9 shards, walks 13 tiles, starts a 10-round tribute at r393; Ryth captures at r386,
recalls to shop (9 shards at r391) and is 7 tiles from the altar when Mite's 16th bag lands; Vendetta banks our 14th bag at r380 and immediately recalls
to shop. 165 gems in hand at the end, 43 short.

## 5. Time, deaths, shop recalls, tributes, camps left (us27 / us26 / opp27 / opp26)

| | walk | camp | fight | tribute | recall | shop | idle | dead |
|---|---|---|---|---|---|---|---|---|
| us27 (369,988 cr) | 47.1% | 18.9% | 2.2% | 4.2% | 5.3% | 0.7% | 8.0% | 13.5% |
| us26 (357,905) | 46.4% | 19.3% | 2.1% | 4.2% | 5.3% | 0.7% | 8.4% | 13.6% |
| opp27 (373,651) | 47.3% | 18.4% | 2.2% | 4.8% | 7.4% | 0.7% | 9.6% | 9.4% |
| opp26 (362,535) | 47.6% | 18.8% | 2.0% | 4.7% | 7.3% | 0.7% | 9.6% | 9.0% |

- Dead per map (us27 / us26 / opp27): collision 23.7% / 22.3% / 17.0%, corners 25.0 / 27.1 / 13.7, packs 19.6 / 18.8 / 7.2, interlock 11.5 / 9.4 / 13.5,
  elkring 10.9 / 12.5 / 17.6, lanes 8.9 / 9.3 / 1.9, monolith 5.4 / 7.7 / 4.9, expanse and rows 0. Deaths by cause (q11): monsters 22 (2%) vs 25 (3%),
  champions within 4 tiles of a live camp 45 (5%) vs 49 (6%), champions elsewhere 832 vs 784. Stacking did not add deaths at camps.
- Idle: 345 cr per game vs 356 (opp 402), of which near a live camp 92 vs 100 (opp 91). Walking efficiency 0.89 / 1.7 extra moves per leg vs 0.89 / 1.9.
- Shop recalls before tributing (C7): captures followed by a recall 51% vs 50% (opp 26%), of which 1477 of 2999 where walking to the altar was shorter vs 1459 of 2991;
  recall starts 24.7 vs 24.8 per game; shop trips 11.4 vs 11.6 per game, 403 cr per game both (opp 324 / 327). Recall classes (q8): shop 47% / heal 47% vs 48 / 46.
  Unchanged: this is still cost #2 of `farming.md`.
- Tributes (C9): completed 19.6 per game vs 20.4 (0.95 vs 0.99 per 100 cr; opp 20.4 / 20.4), bag median 44 both, bags over 66 gems 6% vs 5% (opp 11%),
  captures per bag 1.10 vs 1.09 (opp 1.21), not completed 225 (7%) vs 199 (6%), altar passes with >= 10 gems 0.97 vs 0.78 per game (opp 1.98).
- Camps left to the opponent (own-view, us < 0.2 and opp >= 0.5 captures/game): collision 9o 108 gems 0.11 vs 1.63 (26: 0.05 vs 1.16) and now also the enemy
  wolf 2e 0.05 vs 0.63; lanes nine groups (26: six): the middle wolves 14m / 15m / 16m 0.18 / 0.06 / 0.00 vs 1.41 / 1.18 / 0.59, the own elk 17o 0.06 vs 0.59,
  the enemy clusters 18e / 19e / 20e 0 vs 1.18 / 1.12 / 1.00 and 5e / 6e 0 vs 0.59 / 0.53; interlock 0e (72 gems) 0 vs 0.58; corners' far wolves dropped off the
  list only because this batch's opponents took them less (0.00 vs 0.65 / 0.53 before). Territory: 19.5 own / 4.1 mid / 0.3 enemy captures per game vs
  19.8 / 4.4 / 0.3 (opp 20.8 / 4.7 / 1.2). Draft: identical, one list per map, 155/155.

## 6. Answers

**Did stacking happen online?** Yes, on the groups the rule names. 3000+ hp groups: 3.18 attackers vs 2.72 (143 four-stacks of 316 vs 18 of 301, 7 solos vs 34);
4+ champions on the camp during 47% of the attack windows vs 0%. On rows 142 of 295 captures had four attackers (26: 18 of 285) and all of the first four
captures of 15 of 17 games. It did not happen on collision's 108-gem elk+cluster (2 captures, 1.5 attackers): the group is 30 tiles out and is not chosen,
so the share exponent never gets a chance; opponents take it 1.63 times per game. It also fired on elkring's 2900-hp groups (4 on the opening elk 9/9 games).

**Did it speed the kills?** Yes on the big camps: hit-to-capture 19.9 rounds mean vs 25.4 (median 20 vs 21; opponents 28.5 / 25.4), rows 19.6 vs 25.2,
rows opening 24 vs 32, r100-199 20 vs 32; expanse's 3900 group 21 vs 24. Rows captures 17.4 vs 15.8 per game and 55.2 vs 49.3 gems per 100 cr, the
opponents' level; our 14th rows tribute lands at r380 instead of r397 and our 1000 at r403 instead of r421. Damage per attacker-round on those camps fell
79 -> 64 (crowding), so four champions kill 5.5 rounds faster, not twice as fast.

**Did it cost anything?** Nothing measurable. Deaths 5.8 vs 5.7 per game, deaths to monsters 22 vs 25, deaths to champions near a camp 45 vs 49; small camps
+1 round hit-to-capture (17 / 23 / 24 vs 16 / 22 / 24, within noise on 356-1923 captures) with the same single-attacker shares; idle 8.0% vs 8.4%, idle near a camp
92 vs 100 cr per game; walking 0.89 both; tributes 19.6 vs 20.4 per game (the rows bags are 66 either way). Elkring and packs picked up 4-stacks on 2700-2900 hp
groups (33 + 24 captures) with no visible harm (elkring hit-to-capture 30.1 vs 32.7). The whole-batch record 58-97 vs 59-91 is pairing: tiers 15-35 / 15-35 / 23-27
vs 10-40 / 23-27 / 21-24, collision 8-11 vs 12-7 with the same curve.

**Why is rows still 3-14?** Because the opponents' finishing round did not move (1000 banked at r392 median, r351-401 in 14 of 17 games, identical to the
study26 batch) and ours moved from r421 to r403: 18 rounds gained, ~15 short. The deficit is now entirely in the last 100 rounds (685 vs 688 at r300, 940 vs 1021
at r400; 11 of 14 losses 957-1056 with 99-165 gems in hand): the four-stack dissolves after r200 (0 four-stacks in the last 94 captures, 42 pairs), the last bags
go to the shop first (2.0 shop recalls per game in the final 30 rounds; vs Mite three champions buy 9 shards each at r380-391 of 398), 33-gem shares ride along
for 60 rounds and land as 99-gem bags with a 10-round channel, and the camps are 24-36 tiles from the altar so any capture after ~r375 cannot be banked before
r400. The opponents carry 62 gems at the end, we carry 118. A rows-specific end-game (no shop recall once either team is within ~150 of 1000, bank any share
at once, keep the four together on the wolf nearest the altar) is worth about one bag, which is the whole margin in 11 of the 14 losses.

## What changed with study27 and what did not

1. Changed: 3000+ hp camps are killed by 3-4 champions (3.18 attackers, 45% four-stacks) instead of 2-3 (2.72, 6%); the pair and the third arrive within 2-4 rounds.
2. Changed: big-camp kills are 5.5 rounds faster (19.9 vs 25.4 mean), rows 19.6 vs 25.2, the rows opening 24 vs 32.
3. Changed: rows captures 17.4 vs 15.8 per game, gems per alive round 55.2 vs 49.3 (= the opponents), 14th bag at r380 vs r397, our 1000 at r403 vs r421.
4. Changed: rows losses are one bag short (957, 11 of 14) instead of four (792, 8 of 14); the game is equal at r300 and lost between r300 and r400.
5. Changed (unintended): elkring and packs 2700-2900 hp groups also get four-stacks (33 + 24 captures); elkring opens r21x4 instead of r25x3.
6. Not changed: economy per alive round (41.1 vs 41.7 gems per 100 cr), deaths (5.8 vs 5.7), time dead (13.5% vs 13.6%), idle, walking, tributes, bags, draft.
7. Not changed: shop recalls from the capture tile (51% of captures, 11.4 trips, 403 cr per game) and the opponents' 26% / 8.6 / 324.
8. Not changed: camps left to the opponent (collision 9o 0.11 vs 1.63, lanes middle and enemy groups 0-0.18 vs 0.6-1.4), first capture 5-15 rounds late on 4 maps.
9. Not changed: the rows stack after r200 (0 four-stacks in the last 94 captures) and the end-game banking (118 gems in hand at the end vs 62).
10. Not changed: the record (58-97 vs 59-91); the 9 other maps moved only with the pairings, rows 3-14 because the opponents still bank 1000 at r392 and we at r403.

---
# Appendix A: side-by-side tables (`out27/cmp.md`)

## C0 Record

| split | 27 n | 27 W-L | 26 n | 26 W-L |
|---|---|---|---|---|
| all | 155 | 58-97 | 150 | 59-91 |
| collision | 19 | 8-11 | 19 | 12-7 |
| corners | 19 | 8-11 | 17 | 5-12 |
| elkring | 9 | 5-4 | 14 | 5-9 |
| expanse | 17 | 10-7 | 17 | 11-6 |
| interlock | 19 | 10-9 | 13 | 7-6 |
| lanes | 17 | 3-14 | 18 | 3-15 |
| monolith | 16 | 5-11 | 13 | 5-8 |
| packs | 22 | 6-16 | 21 | 7-14 |
| rows | 17 | 3-14 | 18 | 4-14 |
| opp top10 | 50 | 15-35 | 50 | 10-40 |
| opp 11-20 | 50 | 15-35 | 50 | 23-27 |
| opp 21-30 | 50 | 23-27 | 45 | 21-24 |
| opp other | 5 | 5-0 | 5 | 5-0 |
| side a / b | 150 / 5 |  | 145 / 5 |  |

opponents 27 (games, rank): geese geese go(5,#11), VeryGood(5,#4), Nyx(5,#21), getramramd#euw(5,#18), AlphaSlop(5,#27), Univardisty of Shingtonwash(5,#6), Intercontinental Fish(5,#2), procless(5,#7), PTN Hyperion(5,#8), KratosMessi(5,#13), Boost(5,#15), Mite(5,#1), octo's odyssey(5,#26), Palestine 🇵🇸(5,#54), BottleBots(5,#29), Conley(5,#20), umamusume(5,#25), 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿(5,#17), ❤️Quantom❤️(5,#10), hello(5,#5), Shawn(5,#3), Mate in One(5,#28), Still Testing(5,#19), Full Damage(5,#9), EMPEROR Tung(5,#30), test(5,#14), ひななー(5,#23), Nyxius(5,#12), Ely2sh(5,#24), lETHal(5,#22), Cabbage(5,#16)
opponents 26: BottleBots(5), Ely2sh(5), KratosMessi(5), PTN Hyperion(5), Conley(5), ❤️Quantom❤️(5), Shawn(5), 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿(5), SSSA(5), MicroStella(5), Intercontinental Fish(5), getramramd#euw(5), Boost(5), Full Damage(5), Still Testing(5), octo's odyssey(5), procless(5), AlphaSlop(5), hello(5), Mite(5), geese geese go(5), Nyxius(5), WHIM(5), Univardisty of Shingtonwash(5), umamusume(5), test(5), lETHal(5), VeryGood(5), Nyx(5), ひななー(5) 

## C1 Economy curve: tributed gems at round marks, us/opp (27) vs us/opp (26); mean over the games of the map

| map | n 27/26 | r100 27 ; 26 | r200 27 ; 26 | r300 27 ; 26 | r400 27 ; 26 | decided round med 27 ; 26 | mean rounds 27 ; 26 |
|---|---|---|---|---|---|---|---|
| collision | 19/19 | 46/47 ; 49/37 | 131/127 ; 149/92 | 197/236 ; 245/184 | 313/306 ; 371/280 | 139 ; 142 | 753 ; 742 |
| corners | 19/17 | 122/42 ; 118/69 | 242/201 ; 248/210 | 341/337 ; 371/365 | 469/462 ; 482/498 | 62 ; 123 | 558 ; 565 |
| elkring | 9/14 | 96/118 ; 98/89 | 240/232 ; 217/258 | 370/410 ; 336/431 | 518/570 ; 482/597 | 444 ; 239 | 627 ; 591 |
| expanse | 17/17 | 207/189 ; 207/176 | 488/425 ; 488/427 | 755/725 ; 758/734 | 937/960 ; 942/931 | 324 ; 324 | 366 ; 349 |
| interlock | 19/13 | 118/132 ; 118/123 | 290/302 ; 320/285 | 472/469 ; 496/507 | 648/624 ; 684/712 | 191 ; 221 | 499 ; 479 |
| lanes | 17/18 | 134/128 ; 140/146 | 343/437 ; 370/409 | 556/729 ; 626/705 | 697/965 ; 803/955 | 168 ; 242 | 378 ; 398 |
| monolith | 16/13 | 155/89 ; 151/92 | 342/287 ; 323/316 | 547/535 ; 566/525 | 781/823 ; 780/816 | 339 ; 304 | 448 ; 448 |
| packs | 22/21 | 123/139 ; 133/131 | 259/320 ; 261/298 | 402/508 ; 418/492 | 574/736 ; 590/698 | 216 ; 190 | 494 ; 506 |
| rows | 17/18 | 132/107 ; 132/106 | 396/383 ; 378/374 | 685/688 ; 583/675 | 940/1021 ; 869/975 | 385 ; 342 | 392 ; 402 |

## C2 Farm rates (per split: us27 / opp27 / us26 / opp26)

| split | n 27/26 | captures/game | captures/100cr | gems/capture | captured gems/100cr | tributed/game | deaths/game | % lost at death | % carried at end |
|---|---|---|---|---|---|---|---|---|---|
| all | 155/150 | 23.8 / 26.7 / 24.5 / 26.7 | 1.15 / 1.22 / 1.19 / 1.21 | 35.6 / 35.6 / 35.1 / 35.5 | 41.1 / 43.4 / 41.7 / 43.1 | 800 / 899 / 808 / 907 | 5.8 / 4.0 / 5.7 / 3.9 | 7 / 7 / 6 / 6 | 6 / 4 / 5 / 4 |
| map collision | 19/19 | 31.4 / 30.8 / 32.6 / 29.7 | 1.36 / 1.30 / 1.41 / 1.27 | 22.5 / 27.1 / 22.4 / 26.6 | 30.6 / 35.2 / 31.5 / 33.8 | 699 / 752 / 774 / 674 | 12.6 / 8.8 / 11.3 / 8.5 | 19 / 21 / 14 / 22 | 4 / 5 / 3 / 4 |
| map corners | 19/17 | 14.2 / 19.9 / 15.0 / 22.5 | 0.68 / 0.72 / 0.73 / 0.80 | 42.7 / 38.6 / 42.2 / 38.7 | 28.9 / 27.9 / 30.7 / 30.8 | 585 / 738 / 595 / 837 | 12.4 / 7.6 / 13.5 / 7.1 | 12 / 9 / 15 / 9 | 2 / 4 / 2 / 5 |
| map elkring | 9/14 | 25.6 / 28.9 / 23.8 / 27.1 | 0.91 / 0.97 / 0.92 / 0.95 | 36.0 / 34.3 / 36.0 / 35.0 | 32.9 / 33.4 / 33.1 / 33.1 | 896 / 900 / 762 / 924 | 6.1 / 11.1 / 6.5 / 8.1 | 11 / 14 / 11 / 7 | 6 / 4 / 6 / 4 |
| map expanse | 17/17 | 23.9 / 26.2 / 24.9 / 24.6 | 1.63 / 1.79 / 1.78 / 1.77 | 41.1 / 38.5 / 40.4 / 39.8 | 66.9 / 68.9 / 72.0 / 70.3 | 937 / 960 / 942 / 931 | 0.0 / 0.1 / 0.0 / 0.1 | 0 / 0 / 0 / 0 | 5 / 5 / 7 / 5 |
| map interlock | 19/13 | 27.3 / 23.0 / 27.5 / 24.7 | 1.23 / 1.11 / 1.26 / 1.20 | 33.5 / 37.7 / 33.7 / 36.0 | 41.3 / 41.9 / 42.5 / 43.2 | 847 / 821 / 824 / 878 | 5.3 / 5.7 / 4.3 / 3.2 | 13 / 15 / 11 / 7 | 7 / 4 / 6 / 5 |
| map lanes | 17/18 | 32.8 / 42.5 / 37.9 / 42.5 | 1.59 / 1.93 / 1.75 / 1.87 | 23.5 / 23.9 / 23.7 / 24.2 | 37.3 / 46.3 / 41.4 / 45.4 | 720 / 985 / 839 / 998 | 3.8 / 0.8 / 3.8 / 1.4 | 3 / 1 / 2 / 1 | 6 / 4 / 6 / 3 |
| map monolith | 16/13 | 27.4 / 31.8 / 26.5 / 31.0 | 1.08 / 1.27 / 1.06 / 1.23 | 35.7 / 31.9 / 35.4 / 32.1 | 38.4 / 40.5 / 37.6 / 39.4 | 903 / 957 / 884 / 957 | 2.8 / 2.4 / 3.8 / 2.5 | 3 / 3 / 5 / 4 | 8 / 6 / 4 / 4 |
| map packs | 22/21 | 17.4 / 22.9 / 18.0 / 21.8 | 1.09 / 1.29 / 1.09 / 1.23 | 44.9 / 43.0 / 45.1 / 43.4 | 49.0 / 55.5 / 49.3 / 53.5 | 752 / 968 / 781 / 943 | 7.1 / 2.4 / 7.0 / 3.8 | 3 / 2 / 3 / 2 | 3 / 2 / 2 / 1 |
| map rows | 17/18 | 17.4 / 17.0 / 15.8 / 17.2 | 0.88 / 0.86 / 0.79 / 0.86 | 62.4 / 64.4 / 62.5 / 62.8 | 55.2 / 55.7 / 49.3 / 54.2 | 961 / 1037 / 891 / 1034 | 0.1 / 0.0 / 0.1 / 0.3 | 0 / 0 / 0 / 0 | 11 / 6 / 10 / 5 |
| win | 58/59 | 28.2 / 23.3 / 29.1 / 24.4 | 1.24 / 1.10 / 1.33 / 1.17 | 35.3 / 35.3 / 34.3 / 34.7 | 43.9 / 38.7 / 45.5 / 40.4 | 1023 / 685 / 1018 / 727 | 3.1 / 6.7 / 3.3 / 6.0 | 4 / 14 / 4 / 12 | 5 / 7 / 4 / 6 |
| loss | 97/91 | 21.2 / 28.6 / 21.5 / 28.2 | 1.09 / 1.29 / 1.09 / 1.24 | 35.9 / 35.7 / 35.7 / 36.0 | 39.2 / 46.1 / 38.9 / 44.7 | 667 / 1027 / 673 / 1024 | 7.4 / 2.5 / 7.3 / 2.5 | 10 / 3 / 9 / 2 | 7 / 3 / 7 / 3 |
| opp top10 | 50/50 | 21.3 / 26.7 / 21.5 / 26.8 | 1.13 / 1.28 / 1.14 / 1.29 | 36.3 / 36.5 / 34.9 / 36.3 | 40.9 / 46.9 / 39.7 / 46.8 | 718 / 946 / 676 / 964 | 5.9 / 2.1 / 6.3 / 3.0 | 6 / 4 / 8 / 4 | 5 / 4 / 6 / 3 |
| opp 11-20 | 50/50 | 24.9 / 28.9 / 26.4 / 27.2 | 1.18 / 1.28 / 1.25 / 1.25 | 34.1 / 33.8 / 34.4 / 35.4 | 40.1 / 43.4 / 42.8 / 44.2 | 791 / 931 / 865 / 913 | 6.6 / 4.3 / 5.5 / 4.1 | 8 / 7 / 6 / 7 | 6 / 5 / 5 / 4 |
| opp 21-30 | 50/45 | 24.9 / 24.8 / 25.3 / 26.9 | 1.14 / 1.10 / 1.15 / 1.13 | 36.1 / 36.4 / 36.1 / 35.0 | 41.1 / 40.2 / 41.4 / 39.6 | 871 / 829 / 869 / 884 | 5.4 / 6.0 / 5.9 / 4.7 | 7 / 10 / 6 / 6 | 6 / 4 / 5 / 5 |

## C3 Squad size by group hp (us27 / us26 / opp27 / opp26)

| hp bucket | captures | attackers mean | hit->capture med | mean | single attacker | >=3 attackers | >=4 attackers | dmg/attacker/round med |
|---|---|---|---|---|---|---|---|---|
| <800 | 356 / 536 / 466 / 563 | 1.14 / 1.36 / 1.16 / 1.44 | 17 / 15 / 16 / 15 | 18.8 / 16.7 / 17.7 / 16.1 | 87% / 68% / 84% / 65% | 1% / 4% / 1% / 7% | 0% / 0% / 0% / 1% | 28 / 29 / 29 / 29 |
| 800-1500 | 1923 / 2004 / 1789 / 1804 | 1.51 / 1.83 / 1.51 / 1.82 | 23 / 21 / 22 / 22 | 30.6 / 28.8 / 29.4 / 30.9 | 61% / 47% / 60% / 49% | 9% / 21% / 8% / 20% | 2% / 7% / 2% / 8% | 40 / 38 / 42 / 37 |
| 1500-3000 | 1099 / 1255 / 1120 / 1286 | 2.01 / 2.31 / 2.03 / 2.27 | 24 / 23 / 24 / 23 | 29.9 / 29.1 / 32.0 / 30.8 | 27% / 25% / 25% / 28% | 22% / 38% / 26% / 37% | 6% / 14% / 2% / 13% | 48 / 47 / 48 / 48 |
| >=3000 | 316 / 336 / 301 / 350 | 3.18 / 2.72 / 2.57 / 2.69 | 20 / 22 / 21 / 22 | 19.9 / 28.5 / 25.4 / 27.1 | 2% / 20% / 11% / 19% | 75% / 63% / 63% / 60% | 45% / 24% / 6% / 23% | 64 / 68 / 79 / 68 |

### Attackers distribution on >=3000 hp groups (count by 1/2/3/4/5+)

| team | captures | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|---|
| us27 | 316 | 7 | 73 | 93 | 143 | 0 |
| opp27 | 336 | 67 | 58 | 131 | 62 | 18 |
| us26 | 301 | 34 | 78 | 171 | 18 | 0 |
| opp26 | 350 | 67 | 73 | 128 | 66 | 16 |

## C4 First camp per map (attackers on the first capture, first capture round, hit->capture): us27 / us26 / opp27

| map | us27 attackers / 1st capture / hit->cap | us26 | opp27 |
|---|---|---|---|
| collision | 2.00 / r33 / 18 | 2.00 / r33 / 18 | 2.68 / r18 / 16 |
| corners | 2.16 / r37 / 18 | 2.53 / r41 / 22 | 2.95 / r28 / 18 |
| elkring | 4.00 / r21 / 18 | 3.00 / r25 / 20 | 4.78 / r19 / 17 |
| expanse | 2.00 / r30 / 17 | 2.00 / r30 / 17 | 2.47 / r25 / 16 |
| interlock | 2.00 / r20 / 15 | 2.00 / r20 / 15 | 3.00 / r24 / 15 |
| lanes | 1.00 / r41 / 14 | 1.00 / r40 / 13 | 1.41 / r41 / 14 |
| monolith | 3.00 / r19 / 15 | 3.00 / r19 / 15 | 3.06 / r18 / 14 |
| packs | 2.18 / r33 / 19 | 2.14 / r33 / 19 | 3.23 / r24 / 20 |
| rows | 3.94 / r33 / 23 | 3.00 / r36 / 25 | 4.88 / r31 / 20 |

## C5 Rows cycle (us27 / us26 / opp27 / opp26)

| team | n | r0-49 | r50-99 | r100-149 | r150-199 | r200-249 | r250-299 | r300-349 | r350-399 | r400+ | captures/game | gems in hand at end | tributed/game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| us27 | 17 | 1.00 | 1.94 | 2.06 | 2.00 | 2.82 | 2.00 | 3.00 | 2.41 | 0.12 | 17.4 | 118 | 961 |
| us26 | 18 | 1.00 | 1.00 | 3.00 | 1.89 | 1.00 | 2.00 | 3.67 | 1.61 | 0.67 | 15.8 | 95 | 891 |
| opp27 | 17 | 1.06 | 2.12 | 2.00 | 2.47 | 2.06 | 2.53 | 2.35 | 2.29 | 0.12 | 17.0 | 62 | 1037 |
| opp26 | 18 | 1.06 | 2.11 | 2.11 | 2.11 | 2.22 | 2.50 | 2.44 | 2.11 | 0.56 | 17.2 | 51 | 1034 |

| team | revisits (all maps) | gap after respawn med | mean | revisits rows | gap med | mean | nearest-up chosen (all) | extra tiles mean |
|---|---|---|---|---|---|---|---|---|
| us27 | 2787 | 33 | 45 | 244 | 29 | 28 | 46% | 4.8 |
| us26 | 2774 | 33 | 44 | 231 | 22 | 32 | 44% | 4.5 |
| opp27 | 3221 | 33 | 46 | 237 | 22 | 26 | 51% | 4.0 |
| opp26 | 3113 | 32 | 46 | 253 | 23 | 26 | 52% | 3.9 |

### Rows: first-capture round and attackers per game (27 vs 26), from the first 4 team captures

- 27: r33x4 r58x4 r88x4 r116x4 x15; r36x3 r63x3 r103x3 r125x3 x1; r34x4 r64x4 r92x4 r122x3 x1
- 26: r36x3 r63x3 r103x3 r125x3 x18

## C6 Time: share of champion-rounds by state (us27 / us26 / opp27 / opp26)

| team | champ-rounds | walk | camp | fight | tribute | recall | shop | idle | dead |
|---|---|---|---|---|---|---|---|---|---|
| us27 | 369988 | 47.1% | 18.9% | 2.2% | 4.2% | 5.3% | 0.7% | 8.0% | 13.5% |
| us26 | 357905 | 46.4% | 19.3% | 2.1% | 4.2% | 5.3% | 0.7% | 8.4% | 13.6% |
| opp27 | 373651 | 47.3% | 18.4% | 2.2% | 4.8% | 7.4% | 0.7% | 9.6% | 9.4% |
| opp26 | 362535 | 47.6% | 18.8% | 2.0% | 4.7% | 7.3% | 0.7% | 9.6% | 9.0% |

### Dead share per map (us27 / us26 / opp27)

| map | us27 dead (deaths/game) | us26 | opp27 |
|---|---|---|---|
| collision | 23.7% (12.6/g) | 22.3% (11.3/g) | 17.0% (8.8/g) |
| corners | 25.0% (12.4/g) | 27.1% (13.5/g) | 13.7% (7.6/g) |
| elkring | 10.9% (6.1/g) | 12.5% (6.5/g) | 17.6% (11.1/g) |
| expanse | 0.0% (0.0/g) | 0.0% (0.0/g) | 0.2% (0.1/g) |
| interlock | 11.5% (5.3/g) | 9.4% (4.3/g) | 13.5% (5.7/g) |
| lanes | 8.9% (3.8/g) | 9.3% (3.8/g) | 1.9% (0.8/g) |
| monolith | 5.4% (2.8/g) | 7.7% (3.8/g) | 4.9% (2.4/g) |
| packs | 19.6% (7.1/g) | 18.8% (7.0/g) | 7.2% (2.4/g) |
| rows | 0.3% (0.1/g) | 0.3% (0.1/g) | 0.0% (0.0/g) |

## C7 Shop recalls before tributing (us27 / us26 / opp27 / opp26)

| team | captures | followed by recall | recall where walking to the altar is shorter | recall starts/game | hp<50% at start | shop trips/game | rounds to next capture/tribute med | shop-trip champion-rounds/game |
|---|---|---|---|---|---|---|---|---|
| us27 | 3694 | 1882 (51%) | 1477 of 2999 (49%) | 24.7 | 48% | 11.4 | 29 | 403 |
| us26 | 3676 | 1837 (50%) | 1459 of 2991 (49%) | 24.8 | 48% | 11.6 | 29 | 403 |
| opp27 | 4131 | 1060 (26%) | 692 of 3399 (20%) | 23.1 | 57% | 8.6 | 30 | 324 |
| opp26 | 4003 | 1029 (26%) | 700 of 3309 (21%) | 23.1 | 58% | 8.4 | 31 | 327 |

## C8 Camps left to the opponent (own-view jg/side; captures/game us vs opp): groups with us <0.2 and opp >=0.5, 27 vs 26

- collision: 27: 2e(22g,1350hp: 0.05 vs 0.63), 9o(108g,3900hp: 0.11 vs 1.63)  ;;  26: 9o(108g,3900hp: 0.05 vs 1.16)
- corners: 27: -  ;;  26: 6o(22g,1350hp: 0.00 vs 0.65), 7o(22g,1350hp: 0.00 vs 0.53), 12o(36g,2400hp: 0.18 vs 0.71)
- elkring: 27: -  ;;  26: -
- expanse: 27: -  ;;  26: -
- interlock: 27: 0e(72g,1500hp: 0.00 vs 0.58)  ;;  26: -
- lanes: 27: 5e(24g,500hp: 0.00 vs 0.59), 6e(24g,500hp: 0.00 vs 0.53), 14m(22g,1350hp: 0.18 vs 1.41), 15m(22g,1350hp: 0.06 vs 1.18), 16m(22g,1350hp: 0.00 vs 0.59), 17o(36g,2400hp: 0.06 vs 0.59), 18e(24g,500hp: 0.00 vs 1.18), 19e(24g,500hp: 0.00 vs 1.12), 20e(24g,500hp: 0.00 vs 1.00)  ;;  26: 15m(22g,1350hp: 0.06 vs 1.06), 16m(22g,1350hp: 0.11 vs 0.67), 17o(36g,2400hp: 0.06 vs 0.94), 18e(24g,500hp: 0.00 vs 0.67), 19e(24g,500hp: 0.00 vs 0.72), 20e(24g,500hp: 0.00 vs 0.56)
- monolith: 27: -  ;;  26: -
- packs: 27: -  ;;  26: -
- rows: 27: -  ;;  26: -

### Captures per game by territory own/mid/enemy (us27 / us26 / opp27)

| map | us27 | us26 | opp27 |
|---|---|---|---|
| all | 19.5 / 4.1 / 0.3 | 19.8 / 4.4 / 0.3 | 20.8 / 4.7 / 1.2 |
| collision | 20.8 / 10.5 / 0.1 | 20.9 / 11.6 / 0.1 | 23.5 / 6.4 / 0.8 |
| corners | 2.9 / 11.3 / 0.0 | 3.4 / 11.6 / 0.0 | 7.4 / 12.1 / 0.5 |
| elkring | 24.7 / 0.0 / 0.9 | 22.6 / 0.0 / 1.2 | 26.0 / 0.0 / 2.9 |
| expanse | 23.9 / 0.0 / 0.0 | 24.9 / 0.0 / 0.0 | 26.1 / 0.0 / 0.2 |
| interlock | 27.1 / 0.2 / 0.0 | 27.0 / 0.4 / 0.1 | 21.8 / 0.5 / 0.7 |
| lanes | 28.7 / 3.4 / 0.7 | 33.2 / 3.8 / 0.9 | 29.0 / 8.1 / 5.4 |
| monolith | 25.8 / 0.0 / 1.6 | 25.2 / 0.0 / 1.2 | 30.9 / 0.0 / 0.9 |
| packs | 10.4 / 7.0 / 0.0 | 10.1 / 7.8 / 0.0 | 12.1 / 10.4 / 0.4 |
| rows | 17.4 / 0.0 / 0.0 | 15.8 / 0.0 / 0.0 | 17.0 / 0.0 / 0.0 |

## C9 Bags and tributes (us27 / us26 / opp27 / opp26)

| team | tribute starts | completed | per game | per 100cr | bag med | mean | bags >66 | captures per bag | not completed | altar passes/game |
|---|---|---|---|---|---|---|---|---|---|---|
| us27 | 3265 | 3040 | 19.6 | 0.95 | 44 | 41 | 6% | 1.10 | 225 (7%) | 0.97 |
| us26 | 3256 | 3057 | 20.4 | 0.99 | 44 | 40 | 5% | 1.09 | 199 (6%) | 0.78 |
| opp27 | 3509 | 3168 | 20.4 | 0.94 | 44 | 44 | 11% | 1.21 | 341 (10%) | 1.98 |
| opp26 | 3306 | 3056 | 20.4 | 0.93 | 44 | 45 | 11% | 1.22 | 250 (8%) | 1.89 |

## C10 Draft per map 27 vs 26

- collision: 27 {'cassi_issac > ren > stellar': 19} | 26 {'cassi_issac > ren > stellar': 19}
- corners: 27 {'ryth > stellar > prism > ren > tavi': 19} | 26 {'ryth > stellar > prism > ren > tavi': 17}
- elkring: 27 {'ryth > stellar > prism > ren > tavi': 9} | 26 {'ryth > stellar > prism > ren > tavi': 14}
- expanse: 27 {'vendetta > varg > cassi_issac': 17} | 26 {'vendetta > varg > cassi_issac': 17}
- interlock: 27 {'cassi_issac > ren > stellar > tavi': 19} | 26 {'cassi_issac > ren > stellar > tavi': 13}
- lanes: 27 {'vendetta > varg > cassi_issac > ryth > tavi': 17} | 26 {'vendetta > varg > cassi_issac > ryth > tavi': 18}
- monolith: 27 {'vendetta > varg > cassi_issac > ryth > tavi': 16} | 26 {'vendetta > varg > cassi_issac > ryth > tavi': 13}
- packs: 27 {'cassi_issac > ren > stellar': 22} | 26 {'cassi_issac > ren > stellar': 21}
- rows: 27 {'vendetta > varg > cassi_issac > ryth': 17} | 26 {'vendetta > varg > cassi_issac > ryth': 18}

---
# Appendix B: stacking (q11), study27 then study26

## Q11 Stacking (squad on the camp during the attack window)

### Champions on the camp (within 3 tiles of the group) during the attack window, by group hp; attackers = dealt damage

| team | hp bucket | captures | attackers mean | max on camp mean | mean on camp over window | hit->capture med | mean | attackers 1/2/3/4/5+ | max on camp 1/2/3/4/5+ | >=3 on camp | >=4 on camp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| us | <800 | 356 | 1.14 | 2.31 | 1.59 | 17 | 18.8 | 308 / 45 / 3 / 0 / 0 | 56 / 146 / 143 / 10 / 1 | 43% | 3% |
| us | 800-1500 | 1923 | 1.51 | 2.18 | 1.45 | 23 | 30.6 | 1170 / 572 / 139 / 36 / 6 | 596 / 648 / 436 / 214 / 29 | 35% | 13% |
| us | 1500-3000 | 1099 | 2.01 | 2.17 | 1.46 | 24 | 29.9 | 295 / 564 / 179 / 57 / 4 | 284 / 467 / 250 / 76 / 22 | 32% | 9% |
| us | >=3000 | 316 | 3.18 | 3.28 | 2.49 | 20 | 19.9 | 7 / 73 / 93 / 143 / 0 | 5 / 65 / 99 / 132 / 15 | 78% | 47% |
| opp | <800 | 536 | 1.36 | 2.22 | 1.60 | 15 | 16.7 | 367 / 146 / 21 / 2 / 0 | 112 / 237 / 152 / 27 / 8 | 35% | 7% |
| opp | 800-1500 | 2004 | 1.83 | 2.25 | 1.46 | 21 | 28.8 | 941 / 650 / 274 / 98 / 41 | 608 / 681 / 432 / 196 / 87 | 36% | 14% |
| opp | 1500-3000 | 1255 | 2.31 | 2.36 | 1.52 | 23 | 29.1 | 319 / 455 / 309 / 124 / 48 | 298 / 446 / 335 / 126 / 50 | 41% | 14% |
| opp | >=3000 | 336 | 2.72 | 2.76 | 1.97 | 22 | 28.5 | 67 / 58 / 131 / 62 / 18 | 64 / 57 / 132 / 61 / 22 | 64% | 25% |

### >= 3000 hp groups per map (us vs opp): captures, attackers, max on camp, hit->capture

| map | team | captures | per game | attackers mean | attackers 1/2/3/4/5+ | max on camp mean | hit->capture med | mean | mean hp |
|---|---|---|---|---|---|---|---|---|---|
| collision | us | 2 | 0.11 | 1.50 | 1 / 1 / 0 / 0 / 0 | 1.50 | 52 | 52.5 | 3900 |
| collision | opp | 32 | 1.68 | 1.31 | 23 / 8 / 1 / 0 / 0 | 1.31 | 30 | 47.8 | 3900 |
| corners | opp | 3 | 0.16 | 1.00 | 3 / 0 / 0 / 0 / 0 | 1.00 | 104 | 106.7 | 5300 |
| expanse | us | 19 | 1.12 | 2.11 | 2 / 14 / 2 / 1 / 0 | 2.11 | 21 | 21.3 | 3900 |
| expanse | opp | 10 | 0.59 | 1.00 | 10 / 0 / 0 / 0 / 0 | 1.00 | 31 | 43.0 | 3900 |
| monolith | opp | 2 | 0.12 | 2.00 | 0 / 2 / 0 / 0 / 0 | 2.00 | 238 | 238.0 | 24000 |
| rows | us | 295 | 17.35 | 3.26 | 4 / 58 / 91 / 142 / 0 | 3.36 | 19 | 19.6 | 4050 |
| rows | opp | 289 | 17.00 | 2.96 | 31 / 48 / 130 / 62 / 18 | 3.01 | 21 | 23.6 | 4050 |

### Stack lag: rounds from the first hit on the group to the 2nd / 3rd attacker's first hit (captures with >=2 attackers)

| team | hp bucket | captures (>=2 hitters) | 2nd hitter lag med | mean | 2nd within 2 rounds | with 3rd | 3rd lag med | mean |
|---|---|---|---|---|---|---|---|---|
| us | <800 | 30 | 4 | 5.0 | 40% | 0 | nan | nan |
| us | 800-1500 | 648 | 5 | 12.5 | 27% | 86 | 6 | 16.3 |
| us | 1500-3000 | 751 | 4 | 9.6 | 35% | 170 | 8 | 11.9 |
| us | >=3000 | 309 | 2 | 2.6 | 66% | 236 | 4 | 5.3 |
| opp | <800 | 161 | 3 | 5.1 | 39% | 18 | 4 | 5.5 |
| opp | 800-1500 | 937 | 4 | 10.7 | 38% | 316 | 5 | 13.0 |
| opp | 1500-3000 | 853 | 3 | 9.0 | 42% | 405 | 7 | 12.5 |
| opp | >=3000 | 269 | 1 | 4.3 | 65% | 211 | 4 | 8.2 |

### Deaths by cause (last damage source within 3 rounds; champion kills split by distance to the nearest live camp <=4)

| team | deaths | per game | by monsters | by champions near a camp | by champions away | unknown |
|---|---|---|---|---|---|---|
| us | 899 | 5.80 | 22 (2%) | 45 (5%) | 832 (93%) | 0 (0%) |
| opp | 626 | 4.04 | 15 (2%) | 36 (6%) | 575 (92%) | 0 (0%) |

### Idle rounds (alive, no action) and idle within 3 tiles of a live camp

| team | idle rounds | per game | idle near a camp | per game | share of idle |
|---|---|---|---|---|---|
| us | 53536 | 345.4 | 14238 | 91.9 | 27% |
| opp | 62299 | 401.9 | 14111 | 91.0 | 23% |


### study26

## Q11 Stacking (squad on the camp during the attack window)

### Champions on the camp (within 3 tiles of the group) during the attack window, by group hp; attackers = dealt damage

| team | hp bucket | captures | attackers mean | max on camp mean | mean on camp over window | hit->capture med | mean | attackers 1/2/3/4/5+ | max on camp 1/2/3/4/5+ | >=3 on camp | >=4 on camp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| us | <800 | 466 | 1.16 | 2.34 | 1.65 | 16 | 17.7 | 393 / 70 / 3 / 0 / 0 | 74 / 190 / 176 / 23 / 3 | 43% | 6% |
| us | 800-1500 | 1789 | 1.51 | 2.19 | 1.47 | 22 | 29.4 | 1067 / 576 / 117 / 21 / 8 | 536 / 626 / 414 / 177 / 36 | 35% | 12% |
| us | 1500-3000 | 1120 | 2.03 | 2.15 | 1.46 | 24 | 32.0 | 285 / 548 / 263 / 19 / 5 | 277 / 488 / 271 / 79 / 5 | 32% | 8% |
| us | >=3000 | 301 | 2.57 | 2.54 | 1.93 | 21 | 25.4 | 34 / 78 / 171 / 18 / 0 | 34 / 70 / 197 / 0 / 0 | 65% | 0% |
| opp | <800 | 563 | 1.44 | 2.37 | 1.68 | 15 | 16.1 | 365 / 157 / 35 / 6 / 0 | 117 / 218 / 162 / 44 / 22 | 40% | 12% |
| opp | 800-1500 | 1804 | 1.82 | 2.23 | 1.45 | 22 | 30.9 | 891 / 550 / 211 / 116 / 36 | 603 / 592 / 324 / 183 / 102 | 34% | 16% |
| opp | 1500-3000 | 1286 | 2.27 | 2.32 | 1.51 | 23 | 30.8 | 362 / 442 / 314 / 118 / 50 | 352 / 441 / 299 / 128 / 66 | 38% | 15% |
| opp | >=3000 | 350 | 2.69 | 2.77 | 2.01 | 22 | 27.1 | 67 / 73 / 128 / 66 / 16 | 61 / 69 / 129 / 70 / 21 | 63% | 26% |

### >= 3000 hp groups per map (us vs opp): captures, attackers, max on camp, hit->capture

| map | team | captures | per game | attackers mean | attackers 1/2/3/4/5+ | max on camp mean | hit->capture med | mean | mean hp |
|---|---|---|---|---|---|---|---|---|---|
| collision | us | 1 | 0.05 | 1.00 | 1 / 0 / 0 / 0 / 0 | 1.00 | 85 | 85.0 | 3900 |
| collision | opp | 25 | 1.32 | 1.24 | 20 / 4 / 1 / 0 / 0 | 1.24 | 35 | 46.6 | 3900 |
| corners | opp | 1 | 0.06 | 3.00 | 0 / 0 / 1 / 0 / 0 | 2.00 | 156 | 156.0 | 5300 |
| expanse | us | 15 | 0.88 | 1.00 | 15 / 0 / 0 / 0 / 0 | 1.00 | 24 | 24.5 | 3900 |
| expanse | opp | 14 | 0.82 | 1.07 | 13 / 1 / 0 / 0 / 0 | 1.07 | 30 | 34.1 | 3900 |
| rows | us | 285 | 15.83 | 2.66 | 18 / 78 / 171 / 18 / 0 | 2.63 | 21 | 25.2 | 4050 |
| rows | opp | 310 | 17.22 | 2.88 | 34 / 68 / 126 / 66 / 16 | 2.98 | 21 | 24.8 | 4050 |

### Stack lag: rounds from the first hit on the group to the 2nd / 3rd attacker's first hit (captures with >=2 attackers)

| team | hp bucket | captures (>=2 hitters) | 2nd hitter lag med | mean | 2nd within 2 rounds | with 3rd | 3rd lag med | mean |
|---|---|---|---|---|---|---|---|---|
| us | <800 | 59 | 4 | 7.7 | 37% | 0 | nan | nan |
| us | 800-1500 | 617 | 4 | 12.7 | 31% | 80 | 6 | 13.2 |
| us | 1500-3000 | 782 | 4 | 8.8 | 38% | 205 | 11 | 14.0 |
| us | >=3000 | 267 | 2 | 2.9 | 53% | 189 | 6 | 13.7 |
| opp | <800 | 190 | 3 | 5.5 | 47% | 39 | 3 | 5.4 |
| opp | 800-1500 | 799 | 4 | 11.5 | 42% | 274 | 4 | 12.6 |
| opp | 1500-3000 | 835 | 3 | 9.8 | 46% | 418 | 6 | 15.7 |
| opp | >=3000 | 283 | 1 | 5.7 | 71% | 210 | 3 | 7.8 |

### Deaths by cause (last damage source within 3 rounds; champion kills split by distance to the nearest live camp <=4)

| team | deaths | per game | by monsters | by champions near a camp | by champions away | unknown |
|---|---|---|---|---|---|---|
| us | 858 | 5.72 | 25 (3%) | 49 (6%) | 784 (91%) | 0 (0%) |
| opp | 581 | 3.87 | 22 (4%) | 31 (5%) | 528 (91%) | 0 (0%) |

### Idle rounds (alive, no action) and idle within 3 tiles of a live camp

| team | idle rounds | per game | idle near a camp | per game | share of idle |
|---|---|---|---|---|---|
| us | 53356 | 355.7 | 14993 | 100.0 | 28% |
| opp | 60394 | 402.6 | 13530 | 90.2 | 22% |


---
# Appendix C: finish line, rows per game, rows banking timeline, Mite rows tail

### Finish line: round at which a team banks 1000 (median over games where it happened); our finishing round in wins vs the opponents' in losses, 27 vs 26; and our banked gems when the opponent finished (losses)

| map | 27 wins: our 1000 round ; losses: opp 1000 round ; gems short in losses (ours in hand) | 26 same |
|---|---|---|
| collision | 8: 675 ; 11: 737 ; short 648 (in hand 22) | 12: 704 ; 7: 696 ; short 722 (in hand 22) |
| corners | 8: 556 ; 11: 550 ; short 738 (in hand 0) | 5: 448 ; 12: 542 ; short 544 (in hand 0) |
| elkring | 5: 644 ; 4: 588 ; short 262 (in hand 72) | 5: 590 ; 9: 589 ; short 388 (in hand 72) |
| expanse | 10: 375 ; 7: 343 ; short 180 (in hand 108) | 11: 355 ; 6: 332 ; short 180 (in hand 96) |
| interlock | 10: 502 ; 9: 487 ; short 260 (in hand 22) | 7: 468 ; 6: 470 ; short 389 (in hand 33) |
| lanes | 3: 396 ; 14: 372 ; short 321 (in hand 44) | 3: 422 ; 15: 378 ; short 198 (in hand 48) |
| monolith | 5: 462 ; 11: 433 ; short 114 (in hand 88) | 5: 455 ; 8: 445 ; short 212 (in hand 51) |
| packs | 6: 496 ; 16: 488 ; short 228 (in hand 0) | 7: 514 ; 14: 486 ; short 278 (in hand 0) |
| rows | 3: 403 ; 14: 392 ; short 43 (in hand 165) | 4: 421 ; 14: 392 ; short 208 (in hand 99) |

### rows 27: per game (opp rank, result, rounds, final us/opp, lead at r100/200/300/350, max lead, min lead, our gems in hand at end, last tribute round us/opp, captures us/opp)
| opp | rank | res | rounds | final | lead r100/200/300/350 | max lead | min lead | gems in hand end us/opp | last tribute us/opp | captures us/opp |
|---|---|---|---|---|---|---|---|---|---|---|
| Mite | 1 | loss | 398 | 957/1056 | -66 / 0 / -33 / 33 | 66 | -132 | 165/0 | 380/398 | 18/16 |
| Intercontinent | 2 | loss | 401 | 957/1056 | 0 / 0 / 33 / 33 | 66 | -99 | 165/0 | 380/401 | 18/16 |
| Shawn | 3 | loss | 351 | 891/1056 | 132 / 0 / 33 / -99 | 198 | -231 | 33/66 | 349/351 | 15/17 |
| VeryGood | 4 | loss | 374 | 891/1056 | 132 / 0 / -99 / -99 | 198 | -165 | 99/0 | 349/374 | 16/16 |
| Univardisty of | 6 | loss | 401 | 957/1056 | 99 / 154 / 154 / 121 | 253 | -99 | 165/66 | 380/401 | 18/24 |
| PTN Hyperion | 8 | loss | 400 | 957/1056 | 0 / 0 / -33 / -33 | 66 | -132 | 165/66 | 380/400 | 18/17 |
| Full Damage | 9 | loss | 368 | 891/1056 | 66 / 0 / -33 / -33 | 66 | -165 | 99/66 | 349/368 | 16/17 |
| geese geese go | 11 | loss | 390 | 957/1056 | 0 / -66 / -99 / -99 | 66 | -198 | 165/132 | 380/390 | 18/18 |
| Nyxius | 12 | loss | 385 | 957/1056 | 0 / 0 / -33 / 33 | 66 | -132 | 99/66 | 380/385 | 17/17 |
| test | 14 | loss | 387 | 957/1056 | 0 / 0 / 33 / 33 | 99 | -165 | 165/0 | 380/387 | 18/16 |
| Cabbage | 16 | win | 403 | 1056/990 | 0 / 0 / 33 / 33 | 66 | -132 | 66/66 | 403/384 | 18/16 |
| Conley | 20 | win | 403 | 1056/924 | 0 / 66 / 99 / 165 | 165 | -66 | 66/66 | 403/395 | 18/15 |
| Nyx | 21 | loss | 442 | 990/1056 | 0 / 66 / -66 / 0 | 132 | -132 | 132/66 | 402/442 | 19/16 |
| lETHal | 22 | loss | 400 | 957/1056 | 0 / 66 / 33 / 33 | 99 | -99 | 165/66 | 380/400 | 18/17 |
| octo's odyssey | 26 | loss | 368 | 891/1056 | 66 / -66 / -99 / -99 | 66 | -297 | 99/132 | 349/368 | 16/18 |
| Mate in One | 28 | loss | 393 | 957/1056 | 0 / -66 / -33 / -33 | 66 | -132 | 165/66 | 380/393 | 18/17 |
| Palestine 🇵🇸 | 54 | win | 404 | 1056/924 | 0 / 66 / 66 / 66 | 132 | -66 | 0/132 | 404/399 | 16/16 |

- 27 us states: walk 51.7%, camp 29.2%, idle 7.7%, tribute 5.3%, recall 4.9%, shop 0.9%, dead 0.3%, fight 0.0%, cast_other 0.0%
- 27 opp states: walk 48.5%, camp 25.8%, recall 10.0%, idle 9.2%, tribute 5.7%, shop 0.8%, cast_other 0.1%, fight 0.0%

### rows 26: per game (opp rank, result, rounds, final us/opp, lead at r100/200/300/350, max lead, min lead, our gems in hand at end, last tribute round us/opp, captures us/opp)
| opp | rank | res | rounds | final | lead r100/200/300/350 | max lead | min lead | gems in hand end us/opp | last tribute us/opp | captures us/opp |
|---|---|---|---|---|---|---|---|---|---|---|
| Shawn | 3 | loss | 351 | 792/1056 | 132 / 0 / -66 / -198 | 198 | -264 | 66/66 | 340/351 | 14/17 |
| VeryGood | 5 | loss | 374 | 792/1056 | 132 / 0 / -198 / -198 | 198 | -264 | 132/0 | 340/374 | 15/16 |
| PTN Hyperion | 7 | loss | 400 | 957/1056 | 0 / 0 / -132 / -132 | 0 | -198 | 33/66 | 397/400 | 16/17 |
| Nyxius | 8 | loss | 385 | 792/1056 | 0 / 0 / -132 / -66 | 66 | -264 | 198/66 | 340/385 | 16/17 |
| procless | 9 | loss | 392 | 792/1056 | 0 / 0 / -132 / -132 | 66 | -264 | 198/0 | 340/392 | 16/16 |
| ❤️Quantom❤️ | 10 | win | 450 | 1056/924 | 0 / -66 / 0 / 0 | 198 | -132 | 66/66 | 450/441 | 18/14 |
| Full Damage | 11 | loss | 368 | 792/1056 | 66 / 0 / -132 / -132 | 66 | -264 | 66/66 | 340/368 | 14/17 |
| 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | 12 | loss | 401 | 957/1056 | 0 / 0 / -66 / -66 | 66 | -198 | 99/0 | 397/401 | 17/16 |
| Boost | 15 | loss | 391 | 858/1056 | 0 / 0 / -198 / -132 | 0 | -264 | 66/0 | 384/391 | 14/17 |
| lETHal | 16 | loss | 415 | 957/1056 | 0 / 66 / -66 / 0 | 66 | -132 | 99/66 | 397/415 | 17/17 |
| Still Testing | 19 | loss | 449 | 726/1056 | 66 / -66 / 66 / -132 | 66 | -330 | 132/0 | 418/449 | 13/16 |
| Conley | 20 | win | 421 | 1023/990 | 0 / 66 / 0 / 66 | 66 | -66 | 33/66 | 421/419 | 17/16 |
| ひななー | 21 | loss | 420 | 957/1056 | 0 / 0 / -66 / 0 | 66 | -132 | 99/0 | 397/420 | 17/16 |
| AlphaSlop | 22 | win | 421 | 1023/924 | 0 / 66 / 0 / 132 | 132 | -66 | 33/132 | 421/408 | 17/19 |
| octo's odyssey | 23 | loss | 368 | 792/1056 | 66 / -66 / -198 / -198 | 66 | -330 | 66/132 | 340/368 | 14/18 |
| umamusume | 26 | win | 421 | 1023/990 | 0 / 66 / -44 / 99 | 132 | -66 | 33/66 | 421/406 | 17/20 |
| SSSA | 29 | loss | 391 | 792/1056 | 0 / 66 / -99 / -66 | 66 | -264 | 198/0 | 340/391 | 16/17 |
| WHIM | 30 | loss | 415 | 957/1056 | 0 / -66 / -198 / -66 | 66 | -198 | 99/132 | 397/415 | 17/24 |

- 26 us states: walk 53.2%, camp 25.6%, idle 9.3%, recall 5.5%, tribute 5.2%, shop 0.8%, dead 0.3%, fight 0.1%, cast_other 0.0%
- 26 opp states: walk 46.6%, camp 26.1%, idle 10.5%, recall 9.3%, tribute 5.5%, dead 1.0%, shop 0.8%, fight 0.1%, cast_other 0.1%

### End condition check (all maps, 27): games where max final score >=1000 vs rounds; rounds when neither reached 1000
[(('collision', '>=1000'), 19), (('corners', '>=1000'), 19), (('elkring', '>=1000'), 9), (('expanse', '>=1000'), 17), (('interlock', '>=1000'), 19), (('lanes', '>=1000'), 17), (('monolith', '>=1000'), 16), (('packs', '>=1000'), 22), (('rows', '>=1000'), 17)]
rounds of games with max score <1000: []
rounds of games with max score >=1000 by map (min/med/max): {'collision': (518, 732, 1086), 'corners': (380, 550, 787), 'elkring': (541, 633, 844), 'expanse': (325, 375, 398), 'interlock': (319, 501, 613), 'lanes': (311, 381, 485), 'monolith': (387, 444.5, 539), 'packs': (386, 488.0, 596), 'rows': (351, 398, 442)}

### rows 27: banking timeline (median round of the k-th completed tribute, cumulative banked), us vs opp; and capture gem values
| k-th tribute | us games reaching it | us round med | opp games | opp round med |
|---|---|---|---|---|
| 10 | 17 | 297 | 16 | 279 |
| 11 | 17 | 328 | 16 | 305 |
| 12 | 17 | 329 | 16 | 325 |
| 13 | 17 | 349 | 14 | 340 |
| 14 | 13 | 380 | 13 | 360 |
| 15 | 3 | 403 | 11 | 385 |
| 16 | 1 | 404 | 9 | 398 |
| 17 | 0 | nan | 0 | nan |

- 27 us: capture gem values {66: 263, 33: 32}; bag values {66: 219, 99: 19}; round reaching 1000: [403, 403, 404] (never: 14); oldest gems age at tribute start med 10 p90 19
- 27 opp: capture gem values {66: 276, 33: 10, 22: 3}; bag values {66: 222, 132: 19, 33: 3, 55: 1, 88: 1, 121: 1}; round reaching 1000: [351, 368, 368, 374, 385, 387, 390, 393, 398, 400, 400, 401, 401, 442] (never: 3); oldest gems age at tribute start med 14 p90 36
- 27 us: group kills 279, paid to 2+ champions (split 33/33) 16

### rows 26: banking timeline (median round of the k-th completed tribute, cumulative banked), us vs opp; and capture gem values
| k-th tribute | us games reaching it | us round med | opp games | opp round med |
|---|---|---|---|---|
| 10 | 18 | 303 | 17 | 293 |
| 11 | 18 | 334 | 17 | 311 |
| 12 | 17 | 340 | 17 | 337 |
| 13 | 10 | 395 | 14 | 356 |
| 14 | 9 | 397 | 14 | 377 |
| 15 | 4 | 421 | 13 | 391 |
| 16 | 1 | 450 | 8 | 400 |
| 17 | 0 | nan | 1 | 391 |

- 26 us: capture gem values {66: 255, 33: 30}; bag values {66: 231, 99: 8}; round reaching 1000: [421, 421, 421, 450] (never: 14); oldest gems age at tribute start med 14 p90 21
- 26 opp: capture gem values {66: 281, 33: 26, 22: 3}; bag values {66: 228, 132: 21, 33: 7, 99: 4, 55: 3}; round reaching 1000: [351, 368, 368, 374, 385, 391, 391, 392, 400, 401, 415, 415, 420, 449] (never: 4); oldest gems age at tribute start med 16 p90 49
- 26 us: group kills 270, paid to 2+ champions (split 33/33) 15

### lanes per game (27 then 26): opp rank, result, captures us/opp, deaths us/opp, our captured gems/100cr vs opp
- 27: Interconti#2 l 37/43 d2/0 r352; Shawn#3 w 43/40 d0/3 r430; VeryGood#4 w 42/44 d1/2 r396; Univardist#6 l 16/44 d8/0 r311; ❤️Quantom❤#10 l 41/42 d1/0 r357; geese gees#11 l 36/48 d2/0 r368; Nyxius#12 l 32/42 d2/0 r351; KratosMess#13 l 29/43 d1/0 r315; Boost#15 l 29/42 d8/0 r388; Cabbage#16 l 26/41 d10/0 r384; getramramd#18 l 37/45 d0/2 r414; Still Test#19 l 27/48 d3/2 r413; Conley#20 l 23/40 d9/1 r386; ひななー#23 l 37/45 d5/3 r485; umamusume#25 l 16/38 d9/0 r312; BottleBots#29 l 42/46 d2/0 r377; Palestine #54 w 45/32 d1/0 r381
- 26: Interconti#1 l 32/43 d4/0 r376; Mite#2 l 41/41 d0/0 r339; PTN Hyperi#7 l 43/41 d4/5 r428; Nyxius#8 l 32/46 d1/0 r329; procless#9 l 40/46 d3/3 r394; Full Damag#11 w 45/40 d0/2 r422; KratosMess#14 l 40/44 d2/0 r370; Boost#15 l 44/42 d7/3 r454; lETHal#16 l 45/41 d3/0 r378; test#17 w 45/40 d7/3 r532; getramramd#18 l 38/43 d1/0 r364; Conley#20 l 24/41 d6/3 r388; ひななー#21 l 35/43 d8/1 r412; octo's ody#23 l 35/44 d3/0 r355; Nyx#25 w 47/39 d1/1 r416; BottleBots#27 l 34/43 d5/0 r352; SSSA#29 l 36/41 d6/3 r433; WHIM#30 l 26/47 d7/2 r418

#### Mite (#1) loss rounds 398 final 957/1056
r353 sub 891/858 | Vend g0 hp1300 dA5 k[4] | Varg g33 hp610 dA34 k[5] | Cass g0 hp620 dA32 k[5] | Issa g0 hp900 dA13 k[4] | Ryth g0 hp1700 dA16 k[4]
r354 sub 891/858 | Vend g0 hp1300 dA8 k[6, 4] | Varg g33 hp610 dA34 k[5] | Cass g0 hp620 dA32 k[5] | Issa g0 hp900 dA12 k[4, 5, 6, 5] | Ryth g0 hp1700 dA15 k[4]
r355 sub 891/858 | Vend g0 hp1300 dA9 k[4] | Varg g33 hp580 dA34 k[5] | Cass g0 hp620 dA32 k[5] | Issa g0 hp858 dA12 k[5] | Ryth g0 hp1700 dA14 k[4]
r356 sub 891/858 | Vend g0 hp1300 dA10 k[4, 5, 6, 5] | Varg g33 hp520 dA34 k[5] | Cass g0 hp620 dA32 k[5] | Issa g0 hp816 dA12 k[4, 5] | Ryth g0 hp1700 dA13 k[4]
r357 sub 891/858 | Vend g0 hp1300 dA11 k[4, 5, 6, 5] | Varg g33 hp460 dA34 k[5, 6, 5] | Cass g0 hp620 dA32 k[5] | Issa g0 hp788 dA12 k[5] | Ryth g0 hp1700 dA13 k[6]
r358 sub 891/858 | Vend g0 hp1300 dA11 k[5] | Varg g33 hp400 dA34 k[6, 5] | Cass g0 hp620 dA32 k[5] | Issa g0 hp788 dA12 k[4, 5] | Ryth g0 hp1700 dA13 k[4, 5, 6, 5]
r359 sub 891/858 | Vend g0 hp1300 dA11 k[4, 5, 6, 5] | Varg g33 hp400 dA34 k[5] | Cass g0 hp620 dA32 k[6] | Issa g0 hp774 dA12 k[] | Ryth g0 hp1700 dA13 k[]
r360 sub 891/924 | Vend g0 hp1300 dA11 k[] | Varg g33 hp400 dA35 k[4, 5] | Cass g0 hp620 dA33 k[4] | Issa g0 hp774 dA13 k[4] | Ryth g0 hp1700 dA13 k[4]
r361 sub 891/924 | Vend g0 hp1300 dA11 k[] | Varg g33 hp400 dA35 k[5] | Cass g0 hp620 dA33 k[6, 5] | Issa g0 hp774 dA14 k[4] | Ryth g0 hp1700 dA14 k[4]
r362 sub 891/924 | Vend g0 hp1300 dA11 k[] | Varg g33 hp400 dA35 k[5] | Cass g0 hp620 dA33 k[5] | Issa g0 hp774 dA15 k[4] | Ryth g0 hp1700 dA15 k[4]
r363 sub 891/924 | Vend g0 hp1300 dA11 k[] | Varg g33 hp400 dA35 k[5] | Cass g0 hp620 dA33 k[5] | Issa g0 hp774 dA16 k[4] | Ryth g0 hp1700 dA16 k[4]
r364 sub 891/924 | Vend g0 hp1300 dA11 k[] | Varg g33 hp360 dA35 k[5] | Cass g0 hp620 dA34 k[4] | Issa g0 hp774 dA17 k[4] | Ryth g0 hp1700 dA17 k[4]
r365 sub 891/924 | Vend g66 hp1300 dA8 k[6, 4] | Varg g33 hp340 dA36 k[4, 5, 6, 5] | Cass g0 hp620 dA34 k[5] | Issa g0 hp774 dA18 k[4] | Ryth g0 hp1700 dA18 k[4]
r366 sub 891/924 | Vend g66 hp1300 dA7 k[4] | Varg g33 hp320 dA36 k[6, 5] | Cass g0 hp620 dA34 k[5] | Issa g0 hp774 dA19 k[4] | Ryth g0 hp1700 dA19 k[4]
r367 sub 891/924 | Vend g66 hp1300 dA6 k[4] | Varg g33 hp320 dA36 k[5] | Cass g0 hp620 dA34 k[6, 5] | Issa g0 hp774 dA20 k[4] | Ryth g0 hp1700 dA20 k[4]
r368 sub 891/924 | Vend g66 hp1300 dA5 k[4] | Varg g33 hp320 dA36 k[5] | Cass g0 hp620 dA34 k[5] | Issa g0 hp774 dA21 k[4] | Ryth g0 hp1700 dA21 k[4]
r369 sub 891/924 | Vend g66 hp1300 dA4 k[4] | Varg g33 hp320 dA36 k[5] | Cass g0 hp620 dA34 k[6, 5] | Issa g0 hp774 dA21 k[] | Ryth g0 hp1700 dA21 k[]
r370 sub 891/924 | Vend g66 hp1300 dA3 k[4] | Varg g33 hp320 dA36 k[5] | Cass g0 hp620 dA34 k[5] | Issa g0 hp774 dA21 k[] | Ryth g0 hp1700 dA21 k[]
r371 sub 891/924 | Vend g66 hp1300 dA2 k[4] | Varg g33 hp320 dA36 k[5] | Cass g0 hp620 dA34 k[5] | Issa g0 hp774 dA21 k[] | Ryth g0 hp1700 dA21 k[]
r372 sub 891/924 | Vend g66 hp1300 dA1 k[4] | Varg g33 hp300 dA36 k[5] | Cass g0 hp620 dA34 k[5] | Issa g0 hp774 dA22 k[4] | Ryth g0 hp1700 dA22 k[4]
r373 sub 891/924 | Vend g66 hp1300 dA0 k[4, 12] | Varg g33 hp300 dA35 k[4] | Cass g0 hp620 dA34 k[] | Issa g0 hp774 dA23 k[4, 5, 6, 5] | Ryth g0 hp1700 dA22 k[6]
r374 sub 891/924 | Vend g66 hp1300 dA0 k[] | Varg g33 hp300 dA35 k[] | Cass g0 hp620 dA33 k[4] | Issa g0 hp760 dA23 k[5] | Ryth g0 hp1700 dA23 k[4, 5, 6, 5]
r375 sub 891/924 | Vend g66 hp1300 dA0 k[] | Varg g33 hp300 dA35 k[11] | Cass g0 hp620 dA32 k[4] | Issa g0 hp760 dA24 k[4, 5] | Ryth g0 hp1674.8 dA23 k[5]
r376 sub 891/924 | Vend g66 hp1300 dA0 k[] | Varg g33 hp300 dA35 k[] | Cass g0 hp620 dA31 k[4] | Issa g0 hp732 dA24 k[5] | Ryth g0 hp1674.8 dA23 k[5]
r377 sub 891/924 | Vend g66 hp1300 dA0 k[] | Varg g33 hp300 dA35 k[] | Cass g0 hp620 dA30 k[4] | Issa g0 hp704 dA24 k[5] | Ryth g0 hp1674.8 dA24 k[4, 5]
r378 sub 891/924 | Vend g66 hp1300 dA0 k[] | Varg g33 hp300 dA35 k[] | Cass g0 hp620 dA29 k[4] | Issa g0 hp704 dA25 k[4, 5] | Ryth g0 hp1662.2 dA24 k[5]
r379 sub 891/924 | Vend g66 hp1300 dA0 k[] | Varg g99 hp300 dA35 k[] | Cass g0 hp620 dA28 k[4] | Issa g0 hp690 dA25 k[5] | Ryth g0 hp1662.2 dA24 k[5]
r380 sub 957/924 | Vend g0 hp1300 dA0 k[18, 11] | Varg g99 hp1000 dA13 k[4, 13, 13, 13, 13, 13, 13, 13, 13, 13, 3] | Cass g0 hp620 dA27 k[4] | Issa g0 hp676 dA25 k[5] | Ryth g0 hp1662.2 dA24 k[]
r381 sub 957/924 | Vend g0 hp1300 dA0 k[] | Varg g99 hp1000 dA12 k[4] | Cass g0 hp620 dA27 k[] | Issa g0 hp676 dA25 k[] | Ryth g0 hp1662.2 dA24 k[]
r382 sub 957/924 | Vend g0 hp1300 dA0 k[] | Varg g99 hp1000 dA11 k[4] | Cass g0 hp620 dA26 k[4] | Issa g0 hp676 dA22 k[6, 4] | Ryth g0 hp1662.2 dA24 k[]
r383 sub 957/924 | Vend g0 hp1300 dA0 k[] | Varg g99 hp1000 dA10 k[4] | Cass g0 hp620 dA25 k[4] | Issa g0 hp676 dA21 k[4] | Ryth g0 hp1662.2 dA24 k[]
r384 sub 957/924 | Vend g0 hp1300 dA0 k[] | Varg g99 hp1000 dA9 k[4] | Cass g0 hp620 dA24 k[4] | Issa g0 hp676 dA20 k[4] | Ryth g0 hp1662.2 dA24 k[]
r385 sub 957/924 | Vend g0 hp1300 dA14 k[4, 13, 13, 13, 13, 13, 13, 13, 13, 13, 4] | Varg g99 hp1000 dA8 k[4] | Cass g0 hp620 dA23 k[4] | Issa g0 hp676 dA19 k[4] | Ryth g0 hp1662.2 dA24 k[]
r386 sub 957/924 | Vend g0 hp1300 dA14 k[6, 4] | Varg g99 hp1000 dA7 k[4] | Cass g0 hp620 dA22 k[4] | Issa g0 hp676 dA18 k[4] | Ryth g66 hp1662.2 dA24 k[11]
r387 sub 957/924 | Vend g0 hp1300 dA13 k[4] | Varg g99 hp1000 dA6 k[4] | Cass g0 hp620 dA21 k[4] | Issa g0 hp676 dA17 k[4] | Ryth g66 hp1662.2 dA24 k[]
r388 sub 957/990 | Vend g0 hp1300 dA12 k[4] | Varg g99 hp1000 dA5 k[4] | Cass g0 hp620 dA20 k[4] | Issa g0 hp676 dA16 k[4] | Ryth g66 hp1662.2 dA24 k[]
r389 sub 957/990 | Vend g0 hp1300 dA11 k[4] | Varg g99 hp1000 dA4 k[4] | Cass g0 hp620 dA19 k[4] | Issa g0 hp676 dA15 k[4] | Ryth g66 hp1662.2 dA24 k[]
r390 sub 957/990 | Vend g0 hp1300 dA10 k[4] | Varg g99 hp1000 dA3 k[4] | Cass g0 hp620 dA18 k[4] | Issa g0 hp676 dA12 k[6, 4] | Ryth g66 hp1662.2 dA24 k[]
r391 sub 957/990 | Vend g0 hp1300 dA9 k[4] | Varg g99 hp1000 dA2 k[4] | Cass g0 hp620 dA17 k[4] | Issa g0 hp676 dA11 k[4] | Ryth g66 hp1700 dA12 k[4, 13, 13, 13, 13, 13, 13, 13, 13, 13, 4, 3]
r392 sub 957/990 | Vend g0 hp1300 dA8 k[4] | Varg g99 hp1000 dA1 k[4] | Cass g0 hp620 dA16 k[4] | Issa g0 hp676 dA10 k[4] | Ryth g66 hp1700 dA11 k[4]
r393 sub 957/990 | Vend g0 hp1300 dA7 k[4] | Varg g99 hp1000 dA0 k[4, 12] | Cass g0 hp620 dA15 k[4] | Issa g0 hp676 dA9 k[4] | Ryth g66 hp1700 dA10 k[4]
r394 sub 957/990 | Vend g0 hp1300 dA7 k[4] | Varg g99 hp1000 dA0 k[] | Cass g0 hp620 dA14 k[4] | Issa g0 hp676 dA10 k[4] | Ryth g66 hp1700 dA9 k[4]
r395 sub 957/990 | Vend g0 hp1300 dA8 k[4] | Varg g99 hp1000 dA0 k[] | Cass g0 hp620 dA13 k[4] | Issa g0 hp676 dA11 k[4] | Ryth g66 hp1700 dA8 k[4]
r396 sub 957/990 | Vend g0 hp1300 dA9 k[4] | Varg g99 hp1000 dA0 k[] | Cass g0 hp620 dA12 k[4] | Issa g0 hp676 dA12 k[4] | Ryth g66 hp1700 dA8 k[4]
r397 sub 957/990 | Vend g0 hp1300 dA10 k[4] | Varg g99 hp1000 dA0 k[] | Cass g0 hp620 dA11 k[4] | Issa g0 hp676 dA13 k[4] | Ryth g66 hp1700 dA7 k[4]
r398 sub 957/1056 | Vend g0 hp1300 dA11 k[4] | Varg g99 hp1000 dA0 k[] | Cass g0 hp620 dA11 k[] | Issa g0 hp676 dA13 k[] | Ryth g66 hp1700 dA7 k[]
  Vendetta tributes: [(342, 349, 66, 66), (373, 380, 66, 66)] captures: [(332, 66), (365, 66)]
  Varg tributes: [(393, None, 0, 99)] captures: [(379, 66)]
  Cassi tributes: [] captures: []
  Issac tributes: [(321, 328, 66, 66)] captures: []
  Ryth tributes: [(322, 329, 66, 66)] captures: [(386, 66)]

---
# Appendix D: full study27 tables (q1-q10)

## Q1 Economy

games 155, W-L 58-97; by map: {'collision': '8-11', 'corners': '8-11', 'elkring': '5-4', 'expanse': '10-7', 'interlock': '10-9', 'lanes': '3-14', 'monolith': '5-11', 'packs': '6-16', 'rows': '3-14'}
by opp tier: {'top10': '15-35', '11-20': '15-35', '21-30': '23-27', 'other': '5-0'}

### Tributed gems at round marks (mean over games of the map; us / opp); games still running at that mark in brackets

| map | n | mean rounds | r50 | r100 | r150 | r200 | r250 | r300 | r400 | r500 | r700 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 753 | 23/3 [19] | 46/47 [19] | 96/105 [19] | 131/127 [19] | 160/180 [19] | 197/236 [19] | 313/306 [19] | 422/428 [19] | 594/625 [11] |
| corners | 19 | 558 | 61/4 [19] | 122/42 [19] | 197/121 [19] | 242/201 [19] | 301/257 [19] | 341/337 [19] | 469/462 [18] | 505/620 [13] | 572/730 [3] |
| elkring | 9 | 627 | 0/24 [9] | 96/118 [9] | 164/192 [9] | 240/232 [9] | 292/350 [9] | 370/410 [9] | 518/570 [9] | 666/714 [9] | 864/900 [1] |
| expanse | 17 | 366 | 48/47 [17] | 207/189 [17] | 292/319 [17] | 488/425 [17] | 604/617 [17] | 755/725 [17] | 937/960 [0] | 937/960 [0] | 937/960 [0] |
| interlock | 19 | 499 | 10/45 [19] | 118/132 [19] | 195/226 [19] | 290/302 [19] | 388/391 [19] | 472/469 [19] | 648/624 [17] | 798/776 [10] | 847/821 [0] |
| lanes | 17 | 378 | 24/17 [17] | 134/128 [17] | 260/291 [17] | 343/437 [17] | 453/592 [17] | 556/729 [17] | 697/965 [4] | 720/985 [0] | 720/985 [0] |
| monolith | 16 | 448 | 0/14 [16] | 155/89 [16] | 214/184 [16] | 342/287 [16] | 440/426 [16] | 547/535 [16] | 781/823 [14] | 900/949 [1] | 903/957 [0] |
| packs | 22 | 494 | 33/47 [22] | 123/139 [22] | 187/218 [22] | 259/320 [22] | 333/407 [22] | 402/508 [22] | 574/736 [21] | 715/929 [9] | 752/968 [0] |
| rows | 17 | 392 | 4/23 [17] | 132/107 [17] | 264/232 [17] | 396/383 [17] | 528/548 [17] | 685/688 [17] | 940/1021 [8] | 961/1037 [0] | 961/1037 [0] |

### Round the game is decided (last round at which the eventual winner was not ahead, +1) and lead changes

| split | n | decided round med | mean | med % of game | lead changes/game | decided by r100 | decided in last 20% |
|---|---|---|---|---|---|---|---|
| all | 155 | 247 | 257 | 52% | 4.54 | 35 | 50 |
| map collision | 19 | 139 | 264 | 24% | 1.79 | 7 | 2 |
| map corners | 19 | 62 | 117 | 11% | 0.58 | 11 | 1 |
| map elkring | 9 | 444 | 421 | 69% | 3.67 | 1 | 3 |
| map expanse | 17 | 324 | 309 | 93% | 11.18 | 0 | 13 |
| map interlock | 19 | 191 | 245 | 37% | 2.84 | 5 | 4 |
| map lanes | 17 | 168 | 179 | 48% | 4.59 | 2 | 1 |
| map monolith | 16 | 339 | 320 | 82% | 6.38 | 1 | 9 |
| map packs | 22 | 216 | 222 | 43% | 5.09 | 8 | 4 |
| map rows | 17 | 385 | 344 | 97% | 5.29 | 0 | 13 |
| win | 58 | 268 | 260 | 54% | 4.81 | 17 | 17 |
| loss | 97 | 235 | 255 | 52% | 4.38 | 18 | 33 |
| opp top10 | 50 | 212 | 219 | 46% | 4.60 | 12 | 14 |
| opp 11-20 | 50 | 266 | 301 | 55% | 4.72 | 7 | 17 |
| opp 21-30 | 50 | 252 | 249 | 51% | 4.22 | 15 | 17 |
| opp other | 5 | 364 | 273 | 77% | 5.40 | 1 | 2 |

### Farm rates per team (us vs opponent in the same games)

| split | team | n | captures/game | captures/100 champ-rounds alive | gems/capture | captured gems/100cr | tributed gems/100cr | tributed/game | % tributed | % lost at death | % carried at end | % of gems from kills | deaths/game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 155 | 23.8 | 1.15 | 35.6 | 41.1 | 38.7 | 800 | 87% | 7% | 6% | 7% | 5.8 |
| all | opp | 155 | 26.7 | 1.22 | 35.6 | 43.4 | 41.2 | 899 | 89% | 7% | 4% | 6% | 4.0 |
| map collision | us | 19 | 31.4 | 1.36 | 22.5 | 30.6 | 30.3 | 699 | 77% | 19% | 4% | 23% | 12.6 |
| map collision | opp | 19 | 30.8 | 1.30 | 27.1 | 35.2 | 31.7 | 752 | 75% | 21% | 5% | 17% | 8.8 |
| map corners | us | 19 | 14.2 | 0.68 | 42.7 | 28.9 | 27.9 | 585 | 86% | 12% | 2% | 11% | 12.4 |
| map corners | opp | 19 | 19.9 | 0.72 | 38.6 | 27.9 | 26.8 | 738 | 87% | 9% | 4% | 10% | 7.6 |
| map elkring | us | 9 | 25.6 | 0.91 | 36.0 | 32.9 | 32.0 | 896 | 84% | 11% | 6% | 14% | 6.1 |
| map elkring | opp | 9 | 28.9 | 0.97 | 34.3 | 33.4 | 30.3 | 900 | 82% | 14% | 4% | 10% | 11.1 |
| map expanse | us | 17 | 23.9 | 1.63 | 41.1 | 66.9 | 63.8 | 937 | 95% | 0% | 5% | 0% | 0.0 |
| map expanse | opp | 17 | 26.2 | 1.79 | 38.5 | 68.9 | 65.5 | 960 | 95% | 0% | 5% | 0% | 0.1 |
| map interlock | us | 19 | 27.3 | 1.23 | 33.5 | 41.3 | 38.3 | 847 | 80% | 13% | 7% | 14% | 5.3 |
| map interlock | opp | 19 | 23.0 | 1.11 | 37.7 | 41.9 | 39.6 | 821 | 81% | 15% | 4% | 14% | 5.7 |
| map lanes | us | 17 | 32.8 | 1.59 | 23.5 | 37.3 | 34.8 | 720 | 91% | 3% | 6% | 2% | 3.8 |
| map lanes | opp | 17 | 42.5 | 1.93 | 23.9 | 46.3 | 44.8 | 985 | 95% | 1% | 4% | 2% | 0.8 |
| map monolith | us | 16 | 27.4 | 1.08 | 35.7 | 38.4 | 35.4 | 903 | 90% | 3% | 8% | 3% | 2.8 |
| map monolith | opp | 16 | 31.8 | 1.27 | 31.9 | 40.5 | 38.2 | 957 | 92% | 3% | 6% | 3% | 2.4 |
| map packs | us | 22 | 17.4 | 1.09 | 44.9 | 49.0 | 47.2 | 752 | 94% | 3% | 3% | 3% | 7.1 |
| map packs | opp | 22 | 22.9 | 1.29 | 43.0 | 55.5 | 54.6 | 968 | 96% | 2% | 2% | 3% | 2.4 |
| map rows | us | 17 | 17.4 | 0.88 | 62.4 | 55.2 | 49.0 | 961 | 89% | 0% | 11% | 0% | 0.1 |
| map rows | opp | 17 | 17.0 | 0.86 | 64.4 | 55.7 | 52.7 | 1037 | 94% | 0% | 6% | 0% | 0.0 |
| win | us | 58 | 28.2 | 1.24 | 35.3 | 43.9 | 45.0 | 1023 | 91% | 4% | 5% | 11% | 3.1 |
| win | opp | 58 | 23.3 | 1.10 | 35.3 | 38.7 | 32.2 | 685 | 79% | 14% | 7% | 5% | 6.7 |
| loss | us | 97 | 21.2 | 1.09 | 35.9 | 39.2 | 34.4 | 667 | 84% | 10% | 7% | 5% | 7.4 |
| loss | opp | 97 | 28.6 | 1.29 | 35.7 | 46.1 | 46.3 | 1027 | 93% | 3% | 3% | 7% | 2.5 |
| opp top10 | us | 50 | 21.3 | 1.13 | 36.3 | 40.9 | 37.9 | 718 | 89% | 6% | 5% | 5% | 5.9 |
| opp top10 | opp | 50 | 26.7 | 1.28 | 36.5 | 46.9 | 45.6 | 946 | 93% | 4% | 4% | 5% | 2.1 |
| opp 11-20 | us | 50 | 24.9 | 1.18 | 34.1 | 40.1 | 37.3 | 791 | 85% | 8% | 6% | 8% | 6.6 |
| opp 11-20 | opp | 50 | 28.9 | 1.28 | 33.8 | 43.4 | 41.3 | 931 | 88% | 7% | 5% | 7% | 4.3 |
| opp 21-30 | us | 50 | 24.9 | 1.14 | 36.1 | 41.1 | 39.7 | 871 | 87% | 7% | 6% | 10% | 5.4 |
| opp 21-30 | opp | 50 | 24.8 | 1.10 | 36.4 | 40.2 | 37.0 | 829 | 85% | 10% | 4% | 7% | 6.0 |
| opp other | us | 5 | 27.0 | 1.36 | 39.8 | 54.3 | 51.4 | 1019 | 93% | 1% | 7% | 2% | 1.2 |
| opp other | opp | 5 | 22.6 | 1.14 | 37.6 | 43.0 | 40.2 | 794 | 92% | 3% | 5% | 1% | 1.4 |

### Who farms: share of our captured gems by champion type (all games)

| type | champion-games | captured gems | share | gems/champion-game |
|---|---|---|---|---|
| Issac | 127 | 28596 | 22% | 225 |
| Ren | 88 | 20190 | 15% | 229 |
| Vendetta | 67 | 16997 | 13% | 254 |
| Cassi | 127 | 16100 | 12% | 127 |
| Ryth | 78 | 14106 | 11% | 181 |
| Stellar | 88 | 12322 | 9% | 140 |
| Varg | 67 | 11387 | 9% | 170 |
| Tavi | 80 | 8952 | 7% | 112 |
| Prism | 28 | 2988 | 2% | 107 |


## Q2 Draft and shop

### Our draft per map (pick order) and record; opponent drafts seen against us

**collision** (19 games, nch 4):
- us: cassi_issac > ren > stellar x19 (8-11)
- opp: cassi_issac > stellar > ren x4 (opp won 3)
- opp: varg > stellar > cassi_issac x2 (opp won 1)
- opp: stellar > ren > tavi x2 (opp won 2)
- opp: cassi_issac > stellar > tavi x2 (opp won 1)
- opp: vendetta > varg > cassi_issac x2 (opp won 1)
- opp: ren > cassi_issac > stellar x1 (opp won 1)

**corners** (19 games, nch 5):
- us: ryth > stellar > prism > ren > tavi x19 (8-11)
- opp: willow > tavi > ryth > stellar > ren x2 (opp won 1)
- opp: ryth > stellar > prism > ren > tavi x2 (opp won 2)
- opp: varg > stellar > cassi_issac > ryth > ren x2 (opp won 1)
- opp: varg > ryth > stellar > ren > tavi x1 (opp won 0)
- opp: vendetta > cassi_issac > stellar > ryth > tavi x1 (opp won 0)
- opp: cassi_issac > stellar > willow > ren > tavi x1 (opp won 1)

**elkring** (9 games, nch 5):
- us: ryth > stellar > prism > ren > tavi x9 (5-4)
- opp: varg > stellar > cassi_issac > tavi > ren x3 (opp won 2)
- opp: stellar > cassi_issac > ren > marcella > ryth x1 (opp won 0)
- opp: vendetta > varg > cassi_issac > ryth > ren x1 (opp won 0)
- opp: cassi_issac > prism > ren > ryth > stellar x1 (opp won 1)
- opp: varg > marcella > stellar > tavi > willow x1 (opp won 0)
- opp: varg > cassi_issac > vendetta > ryth > tavi x1 (opp won 0)

**expanse** (17 games, nch 4):
- us: vendetta > varg > cassi_issac x17 (10-7)
- opp: varg > vendetta > cassi_issac x3 (opp won 2)
- opp: cassi_issac > varg > vendetta x2 (opp won 0)
- opp: varg > cassi_issac > vendetta x2 (opp won 2)
- opp: cassi_issac > vendetta > varg x2 (opp won 1)
- opp: cassi_issac > ren > stellar x1 (opp won 0)
- opp: cassi_issac > stellar > ryth x1 (opp won 0)

**interlock** (19 games, nch 5):
- us: cassi_issac > ren > stellar > tavi x19 (10-9)
- opp: vendetta > varg > cassi_issac > ryth x3 (opp won 1)
- opp: varg > tavi > stellar > cassi_issac x1 (opp won 0)
- opp: stellar > cassi_issac > ren > ryth x1 (opp won 1)
- opp: stellar > tavi > cassi_issac > willow x1 (opp won 0)
- opp: varg > vendetta > ryth > ren x1 (opp won 0)
- opp: ren > varg > vendetta > ryth x1 (opp won 0)

**lanes** (17 games, nch 6):
- us: vendetta > varg > cassi_issac > ryth > tavi x17 (3-14)
- opp: ryth > cassi_issac > stellar > ren > tavi x2 (opp won 2)
- opp: varg > stellar > cassi_issac > tavi > ren x1 (opp won 1)
- opp: stellar > tavi > cassi_issac > willow > prism x1 (opp won 0)
- opp: varg > cassi_issac > stellar > tavi > ren x1 (opp won 1)
- opp: cassi_issac > vendetta > stellar > vesper > tavi x1 (opp won 1)
- opp: vendetta > varg > cassi_issac > ryth > ren x1 (opp won 1)

**monolith** (16 games, nch 6):
- us: vendetta > varg > cassi_issac > ryth > tavi x16 (5-11)
- opp: vendetta > varg > cassi_issac > ryth > ren x2 (opp won 2)
- opp: varg > stellar > cassi_issac > tavi > ren x2 (opp won 1)
- opp: varg > vendetta > cassi_issac > ryth > ren x2 (opp won 1)
- opp: varg > tavi > stellar > vendetta > cassi_issac x1 (opp won 1)
- opp: varg > ryth > vendetta > ren > marcella x1 (opp won 0)
- opp: varg > stellar > cassi_issac > ryth > ren x1 (opp won 1)

**packs** (22 games, nch 4):
- us: cassi_issac > ren > stellar x22 (6-16)
- opp: varg > stellar > cassi_issac x5 (opp won 4)
- opp: cassi_issac > stellar > varg x3 (opp won 1)
- opp: ren > stellar > cassi_issac x2 (opp won 2)
- opp: stellar > tavi > cassi_issac x2 (opp won 1)
- opp: cassi_issac > stellar > ren x1 (opp won 1)
- opp: ren > varg > vendetta x1 (opp won 1)

**rows** (17 games, nch 5):
- us: vendetta > varg > cassi_issac > ryth x17 (3-14)
- opp: vendetta > cassi_issac > stellar > ryth x1 (opp won 1)
- opp: cassi_issac > stellar > varg > ren x1 (opp won 1)
- opp: cassi_issac > stellar > ryth > ren x1 (opp won 1)
- opp: varg > ryth > cassi_issac > ren x1 (opp won 1)
- opp: cassi_issac > stellar > varg > tavi x1 (opp won 0)
- opp: vendetta > varg > cassi_issac > willow x1 (opp won 1)

us pool (champion-games): {'cassi_issac': 127, 'ren': 88, 'stellar': 88, 'tavi': 80, 'ryth': 78, 'vendetta': 67, 'varg': 67, 'prism': 28}; first pick: {'vendetta': 67, 'cassi_issac': 60, 'ryth': 28}

opp pool (champion-games): {'cassi_issac': 133, 'stellar': 114, 'varg': 89, 'ren': 88, 'tavi': 60, 'ryth': 55, 'vendetta': 48, 'prism': 16, 'willow': 14, 'marcella': 4, 'vesper': 2}; first pick: {'varg': 47, 'cassi_issac': 46, 'stellar': 21, 'vendetta': 17, 'ren': 14, 'ryth': 8, 'willow': 2}

### Shop per champion type (per champion-game; trips = rounds with a purchase)

**Us**

| type | n | shards bought (family_stat: total) | emblems/g | 1st buy r (med) | buys/g | trips/g | gap med | % dead | % spawn | % field | earned | spent | gold end | unspent % | trips ending at 0 gold | consumables/g |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi | 127 | power_focus:626, durability_health:262 | 1.07 | 147 | 7.3 | 2.8 | 92 | 10% | 90% | 0% | 224 | 213 | 10 | 5% | 74% | 0.35 |
| Issac | 127 | power_strength:2336, jungle_strength:407 | 3.93 | 71 | 22.1 | 4.9 | 73 | 6% | 94% | 0% | 669 | 653 | 16 | 2% | 75% | 0.54 |
| Ren | 88 | power_focus:1893, durability_health:347 | 4.72 | 74 | 26.7 | 6.4 | 62 | 4% | 96% | 0% | 806 | 776 | 30 | 4% | 62% | 1.27 |
| Stellar | 88 | power_focus:1110, durability_health:265 | 2.76 | 117 | 16.8 | 4.7 | 77 | 13% | 87% | 0% | 507 | 481 | 26 | 5% | 46% | 1.19 |
| Tavi | 80 | power_focus:567, bruiser_focus:181 | 1.50 | 74 | 10.0 | 4.1 | 67 | 0% | 63% | 37% | 291 | 287 | 3 | 1% | 51% | 0.69 |
| Ryth | 78 | power_strength:900, durability_strength:289, jungle_strength:240, bruiser_health:186 | 3.82 | 100 | 21.4 | 3.7 | 83 | 2% | 98% | 0% | 655 | 629 | 26 | 4% | 68% | 0.74 |
| Vendetta | 67 | power_strength:1018, durability_strength:280, jungle_strength:261, bruiser_health:196 | 4.81 | 84 | 26.7 | 4.6 | 61 | 1% | 99% | 0% | 821 | 791 | 30 | 4% | 93% | 0.55 |
| Varg | 67 | power_strength:574, durability_strength:292, jungle_strength:223, bruiser_health:112 | 3.19 | 49 | 18.5 | 3.4 | 86 | 2% | 98% | 0% | 568 | 544 | 24 | 4% | 76% | 0.61 |
| Prism | 28 | power_focus:138, durability_health:49 | 1.00 | 151 | 7.8 | 2.8 | 138 | 4% | 96% | 0% | 227 | 211 | 16 | 7% | 29% | 1.07 |

**Opponents**

| type | n | shards bought (family_stat: total) | emblems/g | 1st buy r (med) | buys/g | trips/g | gap med | % dead | % spawn | % field | earned | spent | gold end | unspent % | trips ending at 0 gold | consumables/g |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cassi | 133 | power_focus:455, monster_focus:171, jungle_focus:113, durability_health:102, durability_focus:72 | 1.47 | 145 | 5.1 | 2.8 | 100 | 11% | 89% | 0% | 308 | 266 | 41 | 13% | 39% | 0.43 |
| Issac | 133 | power_strength:1331, durability_health:317, monster_strength:244, jungle_strength:183, bruiser_health:163 | 3.47 | 73 | 10.6 | 4.3 | 73 | 9% | 91% | 0% | 630 | 583 | 47 | 7% | 53% | 0.70 |
| Stellar | 114 | power_focus:942, durability_health:226, bruiser_focus:162, monster_focus:162, jungle_focus:131 | 2.84 | 114 | 8.9 | 4.0 | 88 | 12% | 88% | 0% | 537 | 490 | 47 | 9% | 36% | 0.61 |
| Varg | 89 | power_strength:1364, monster_strength:225, durability_health:217, jungle_strength:145, jungle_health:119 | 4.87 | 71 | 15.9 | 4.6 | 70 | 3% | 97% | 0% | 890 | 802 | 88 | 10% | 47% | 0.75 |
| Ren | 88 | power_focus:542, power_strength:305, bruiser_health:222, durability_health:195, monster_strength:133 | 3.65 | 81 | 10.7 | 4.6 | 75 | 5% | 95% | 0% | 685 | 612 | 73 | 11% | 42% | 0.92 |
| Tavi | 60 | power_focus:239, durability_health:132, power_strength:99, monster_focus:53, bruiser_strength:53 | 2.43 | 99 | 9.1 | 5.1 | 62 | 1% | 18% | 81% | 426 | 416 | 9 | 2% | 47% | 0.35 |
| Ryth | 55 | power_strength:372, bruiser_health:133, monster_strength:119, durability_health:104, jungle_health:81 | 3.27 | 97 | 9.5 | 3.6 | 88 | 5% | 95% | 0% | 618 | 553 | 65 | 11% | 43% | 0.60 |
| Vendetta | 48 | power_strength:661, monster_strength:155, durability_health:129, jungle_health:95, jungle_strength:55 | 4.67 | 64 | 15.0 | 4.9 | 65 | 6% | 94% | 0% | 868 | 769 | 99 | 11% | 39% | 0.88 |
| Prism | 16 | power_focus:80, durability_health:49, bruiser_focus:38, monster_focus:12, jungle_focus:10 | 2.06 | 124 | 5.1 | 3.9 | 84 | 10% | 90% | 0% | 402 | 367 | 35 | 9% | 43% | 0.31 |
| Willow | 14 | power_strength:61, bruiser_strength:27, durability_health:9, monster_strength:5, jungle_strength:3 | 1.14 | 156 | 5.1 | 2.2 | 116 | 8% | 92% | 0% | 262 | 226 | 36 | 14% | 55% | 0.07 |
| Marcella | 4 | power_strength:53, monster_strength:15, jungle_health:10, durability_health:8, jungle_strength:5 | 4.75 | 57 | 8.5 | 6.0 | 93 | 29% | 71% | 0% | 790 | 762 | 28 | 4% | 11% | 0.50 |
| VesperVale | 2 | power_strength:38, monster_strength:9, jungle_health:5 | 4.50 | 146 | 5.5 | 4.5 | 61 | 27% | 73% | 0% | 1018 | 780 | 238 | 23% | 22% | 0.00 |

### Our purchase sequences (first 3 trips per champion-game: round:gold spent, H = health shards, [d]=dead, [f]=field)

- Vendetta: r35:270 | r170:270HHH | r218:270HH x15; r84:90 | r115:160 | r179:180 x15; r20:90 | r50:90 | r169:180 x4; r20:90 | r50:90 | r168:180 x3
- Varg: r42:90 | r185:90 | r240:160 x15; r241:130 | r380:270 x11; r241:130 x4; r49:180 | r113:180 | r177:180HHH x3
- Cassi: (no purchase) x34; r184:90 x16; r315:270HHHH x1; r322:90 x1
- Issac: r59:270 | r117:270 | r239:130 x15; r84:90 | r183:90 | r268:90 x15; (no purchase) x11; r169:40 x1
- Ryth: r93:270 | r153:270HHH | r219:270HH x15; (no purchase) x6; r99:180 | r187:180 x2; r99:180 x1
- Tavi: (no purchase) x17; r88:90 x2; r246:90[f][f][f] x1; r209:90[f][f][f] x1
- Ren: (no purchase) x6; r65:90 | r172:180HHHH | r220:130H x1; r36:90 | r138:90H | r230:90HHH x1; r130:180H | r253:180HHHH | r283:180 x1
- Stellar: (no purchase) x8; r169:30[d] | r229:10 | r366:60[d][d] x1; r67:90 | r257:90H x1; r161:180H | r367:60H[d]H[d] | r427:10 x1
- Prism: (no purchase) x7; r213:190H | r323:180HHHH | r521:210 x1; r135:190H | r280:180HHHH | r475:210 x1; r390:190H | r528:180HHHH x1

### Family presence per type (share of champion-games with >=5 shards of the family), us vs opp

| team | type | n | families with a full emblem (share of games) |
|---|---|---|---|
| us | Cassi | 127 | power_focus 51%, durability_health 33% |
| us | Issac | 127 | power_strength 87%, jungle_strength 59% |
| us | Ren | 88 | power_focus 82%, durability_health 75% |
| us | Stellar | 88 | power_focus 72%, durability_health 52% |
| us | Tavi | 80 | power_focus 53%, bruiser_focus 40% |
| us | Ryth | 78 | power_strength 83%, durability_strength 67%, jungle_strength 57%, bruiser_health 37% |
| us | Vendetta | 67 | power_strength 89%, durability_strength 80%, jungle_strength 76%, bruiser_health 47% |
| us | Varg | 67 | power_strength 91%, durability_strength 80%, jungle_strength 53%, bruiser_health 28% |
| us | Prism | 28 | power_focus 53%, durability_health 21% |

| team | type | n | families with a full emblem (share of games) |
|---|---|---|---|
| opp | Cassi | 133 | power_focus 25%, monster_focus 21%, jungle_focus 15%, durability_health 12%, jungle_health 9%, durability_focus 8% |
| opp | Issac | 133 | power_strength 53%, durability_health 33%, monster_strength 33%, jungle_strength 25%, jungle_health 14%, bruiser_health 14% |
| opp | Stellar | 114 | power_focus 55%, durability_health 36%, monster_focus 23%, jungle_focus 21%, bruiser_focus 11%, jungle_health 9% |
| opp | Varg | 89 | power_strength 73%, monster_strength 50%, durability_health 44%, jungle_strength 30%, jungle_health 24%, durability_strength 20% |
| opp | Ren | 88 | durability_health 37%, bruiser_health 30%, power_focus 27%, monster_strength 26%, power_strength 21%, jungle_health 14% |
| opp | Tavi | 60 | durability_health 40%, power_focus 31%, power_strength 20%, monster_focus 16%, bruiser_focus 15%, jungle_strength 13% |
| opp | Ryth | 55 | power_strength 43%, monster_strength 41%, durability_health 34%, jungle_health 27%, bruiser_health 21%, jungle_strength 16% |
| opp | Vendetta | 48 | power_strength 75%, monster_strength 64%, durability_health 45%, jungle_health 39%, jungle_strength 22%, durability_strength 14% |
| opp | Prism | 16 | power_focus 50%, durability_health 43%, bruiser_focus 18%, jungle_focus 12%, monster_focus 6%, jungle_health 6% |
| opp | Willow | 14 | power_strength 35%, bruiser_strength 14%, monster_strength 7%, durability_health 7% |
| opp | Marcella | 4 | monster_strength 75%, power_strength 75%, jungle_health 50%, jungle_strength 25%, power_health 25%, durability_health 25% |
| opp | VesperVale | 2 | monster_strength 50%, power_strength 50%, jungle_health 50% |

### Gold per game per map (team totals), us vs opp

| map | n | us earned | us spent | us gold end | us emblems | opp earned | opp spent | opp gold end | opp emblems |
|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 3173 | 3040 | 133 | 18.5 | 3508 | 3277 | 230 | 19.8 |
| corners | 19 | 588 | 550 | 38 | 1.8 | 1531 | 1416 | 115 | 7.2 |
| elkring | 9 | 5439 | 5294 | 144 | 32.4 | 5703 | 5332 | 371 | 33.1 |
| expanse | 17 | 1361 | 1351 | 9 | 6.9 | 1229 | 1004 | 225 | 5.6 |
| interlock | 19 | 2183 | 2095 | 87 | 11.7 | 1649 | 1483 | 166 | 7.8 |
| lanes | 17 | 1149 | 999 | 149 | 4.8 | 1236 | 952 | 284 | 4.5 |
| monolith | 16 | 4128 | 4039 | 89 | 24.4 | 4244 | 3832 | 413 | 22.8 |
| packs | 22 | 2580 | 2467 | 113 | 14.5 | 3497 | 3165 | 332 | 19.3 |
| rows | 17 | 4431 | 4326 | 105 | 27.3 | 4511 | 4139 | 372 | 25.8 |

| split | team | champion-games | gold at end med | mean | >=90 (3 shards) | >=150 (an emblem) |
|---|---|---|---|---|---|---|
| all | us | 750 | 0 | 19 | 9% | 5% |
| all | opp | 756 | 10 | 55 | 26% | 14% |
| win | us | 274 | 0 | 21 | 10% | 4% |
| win | opp | 278 | 10 | 41 | 22% | 10% |
| loss | us | 476 | 0 | 19 | 9% | 6% |
| loss | opp | 478 | 12 | 64 | 28% | 16% |
| opp top10 | us | 241 | 0 | 18 | 9% | 5% |
| opp top10 | opp | 239 | 10 | 60 | 29% | 14% |
| opp 11-20 | us | 246 | 0 | 20 | 9% | 5% |
| opp 11-20 | opp | 247 | 10 | 59 | 28% | 15% |
| opp 21-30 | us | 239 | 0 | 20 | 9% | 4% |
| opp 21-30 | opp | 246 | 10 | 47 | 21% | 11% |
| opp other | us | 24 | 0 | 24 | 17% | 4% |
| opp other | opp | 24 | 10 | 59 | 29% | 17% |


## Q3 Camp choice

### Per map: camp groups (json group id + side relative to the team), captures per game by us and by the opponent (opponent side is its own view)

**collision** (19 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | wolf | 1350 | 22 | 90 | 40 | 3 | 15 | 7.63 | 100% | 7.74 | 100% |
| 4 | own | gold_cluster | 500 | 0 | 35 | 50 | 5 | 13 | 0.00 | 0% | 0.00 | 0% |
| 1 | own | wolf | 1350 | 22 | 90 | 40 | 8 | 10 | 6.74 | 100% | 6.95 | 100% |
| 5 | own | gold_cluster | 500 | 0 | 35 | 50 | 10 | 8 | 0.00 | 0% | 0.00 | 0% |
| 2 | own | wolf | 1350 | 22 | 90 | 40 | 12 | 6 | 5.95 | 100% | 6.26 | 100% |
| 7 | own | elk | 2400 | 36 | 160 | 60 | 14 | 15 | 0.37 | 37% | 0.79 | 47% |
| 6 | own | gold_cluster | 500 | 0 | 35 | 50 | 15 | 3 | 0.00 | 0% | 0.00 | 0% |
| 8 | own | elk | 2400 | 36 | 160 | 60 | 22 | 18 | 0.00 | 0% | 0.16 | 11% |
| 9 | own | elk+gem_cluster | 3900 | 108 | 160 | 60 | 30 | 26 | 0.11 | 11% | 1.63 | 68% |
| 3 | mid | wolf | 1350 | 22 | 90 | 40 | 17 | 1 | 10.53 | 100% | 6.42 | 79% |
| 6 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 15 | 3 | 0.00 | 0% | 0.00 | 0% |
| 2 | enemy | wolf | 1350 | 22 | 90 | 40 | 12 | 6 | 0.05 | 5% | 0.63 | 42% |
| 5 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 10 | 8 | 0.00 | 0% | 0.00 | 0% |
| 1 | enemy | wolf | 1350 | 22 | 90 | 40 | 8 | 10 | 0.00 | 0% | 0.16 | 16% |
| 4 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 5 | 13 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | wolf | 1350 | 22 | 90 | 40 | 3 | 15 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | elk | 2400 | 36 | 160 | 60 | 14 | 15 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | elk | 2400 | 36 | 160 | 60 | 22 | 18 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | elk+gem_cluster | 3900 | 108 | 160 | 60 | 30 | 26 | 0.00 | 0% | 0.05 | 5% |

**corners** (19 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | own | wolf | 1350 | 22 | 90 | 40 | 4 | 23 | 2.11 | 84% | 3.21 | 84% |
| 9 | own | elk | 2400 | 36 | 160 | 60 | 10 | 15 | 0.32 | 32% | 0.95 | 53% |
| 12 | own | elk | 2400 | 36 | 160 | 60 | 12 | 16 | 0.16 | 11% | 0.47 | 32% |
| 8 | own | elk | 2400 | 36 | 160 | 60 | 16 | 13 | 0.00 | 0% | 0.32 | 16% |
| 11 | own | elk | 2400 | 36 | 160 | 60 | 16 | 14 | 0.00 | 0% | 0.11 | 11% |
| 5 | own | wolf | 1350 | 22 | 90 | 40 | 19 | 19 | 0.37 | 21% | 1.26 | 58% |
| 2 | own | elk+gem_cluster | 5300 | 96 | 320 | 60 | 22 | 21 | 0.00 | 0% | 0.16 | 11% |
| 4 | own | gold_cluster | 1000 | 0 | 70 | 50 | 24 | 18 | 0.00 | 0% | 0.00 | 0% |
| 6 | own | wolf | 1350 | 22 | 90 | 40 | 25 | 13 | 0.00 | 0% | 0.47 | 37% |
| 7 | own | wolf | 1350 | 22 | 90 | 40 | 27 | 6 | 0.00 | 0% | 0.42 | 32% |
| 13 | own | elk | 4800 | 72 | 320 | 60 | 29 | 8 | 0.00 | 0% | 0.00 | 0% |
| 0 | mid | gem_cluster | 1000 | 48 | 0 | 50 | 19 | 0 | 4.32 | 79% | 7.11 | 95% |
| 1 | mid | gem_cluster | 1000 | 48 | 0 | 50 | 19 | 0 | 6.95 | 95% | 4.95 | 89% |
| 14 | mid | gold_cluster | 1000 | 0 | 70 | 50 | 19 | 16 | 0.00 | 0% | 0.00 | 0% |
| 10 | mid | gold_cluster | 1000 | 0 | 70 | 50 | 31 | 31 | 0.00 | 0% | 0.00 | 0% |
| 5 | enemy | wolf | 1350 | 22 | 90 | 40 | 19 | 19 | 0.00 | 0% | 0.37 | 26% |
| 2 | enemy | elk+gem_cluster | 5300 | 96 | 320 | 60 | 22 | 21 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | elk | 2400 | 36 | 160 | 60 | 10 | 15 | 0.00 | 0% | 0.11 | 11% |
| 12 | enemy | elk | 2400 | 36 | 160 | 60 | 12 | 16 | 0.00 | 0% | 0.00 | 0% |
| 4 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 24 | 18 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | elk | 2400 | 36 | 160 | 60 | 16 | 13 | 0.00 | 0% | 0.00 | 0% |
| 13 | enemy | elk | 4800 | 72 | 320 | 60 | 29 | 8 | 0.00 | 0% | 0.00 | 0% |
| 6 | enemy | wolf | 1350 | 22 | 90 | 40 | 25 | 13 | 0.00 | 0% | 0.00 | 0% |
| 3 | enemy | wolf | 1350 | 22 | 90 | 40 | 4 | 23 | 0.00 | 0% | 0.00 | 0% |
| 11 | enemy | elk | 2400 | 36 | 160 | 60 | 16 | 14 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | wolf | 1350 | 22 | 90 | 40 | 27 | 6 | 0.00 | 0% | 0.00 | 0% |

**elkring** (9 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 2 | 17 | 6.67 | 100% | 6.89 | 100% |
| 1 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 5 | 14 | 6.00 | 100% | 6.00 | 100% |
| 2 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 8 | 11 | 5.89 | 100% | 5.78 | 100% |
| 3 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 3.44 | 100% | 3.44 | 89% |
| 4 | own | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 2.67 | 78% | 3.89 | 100% |
| 2 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 8 | 11 | 0.00 | 0% | 0.22 | 11% |
| 4 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 0.56 | 56% | 1.00 | 44% |
| 1 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 5 | 14 | 0.00 | 0% | 0.11 | 11% |
| 3 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 15 | 4 | 0.33 | 33% | 1.44 | 67% |
| 0 | enemy | elk+gold_cluster | 2900 | 36 | 195 | 60 | 2 | 17 | 0.00 | 0% | 0.11 | 11% |

**expanse** (17 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11 | own | wolf | 1350 | 22 | 90 | 40 | 5 | 8 | 3.00 | 100% | 4.59 | 100% |
| 1 | own | gem_cluster | 1000 | 48 | 0 | 50 | 11 | 6 | 4.53 | 100% | 5.24 | 100% |
| 12 | own | wolf | 1350 | 22 | 90 | 40 | 15 | 6 | 2.94 | 100% | 3.24 | 94% |
| 2 | own | gem_cluster | 1000 | 48 | 0 | 50 | 17 | 9 | 3.88 | 100% | 4.24 | 100% |
| 14 | own | elk | 2400 | 36 | 160 | 60 | 17 | 9 | 1.94 | 100% | 0.59 | 41% |
| 7 | own | gold_cluster | 1000 | 0 | 70 | 50 | 24 | 8 | 0.00 | 0% | 0.00 | 0% |
| 10 | own | wolf | 1350 | 22 | 90 | 40 | 27 | 6 | 1.94 | 94% | 2.59 | 82% |
| 0 | own | gem_cluster | 1000 | 48 | 0 | 50 | 28 | 7 | 3.65 | 100% | 4.47 | 100% |
| 8 | own | gold_cluster | 1000 | 0 | 70 | 50 | 31 | 8 | 0.00 | 0% | 0.00 | 0% |
| 6 | own | gold_cluster | 1000 | 0 | 70 | 50 | 33 | 1 | 0.00 | 0% | 0.00 | 0% |
| 13 | own | wolf | 2700 | 44 | 180 | 40 | 38 | 8 | 0.88 | 88% | 0.53 | 41% |
| 3 | own | elk+gem_cluster | 3900 | 108 | 160 | 60 | 51 | 9 | 1.06 | 94% | 0.47 | 29% |
| 4 | own | elk+gem_cluster | 3900 | 108 | 160 | 60 | 58 | 16 | 0.06 | 6% | 0.12 | 12% |
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

**interlock** (19 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | own | wolf | 1350 | 22 | 90 | 40 | 4 | 12 | 7.42 | 100% | 6.26 | 100% |
| 4 | own | wolf | 1350 | 22 | 90 | 40 | 10 | 12 | 7.00 | 100% | 5.11 | 100% |
| 0 | own | gem_cluster | 1500 | 72 | 0 | 50 | 14 | 5 | 6.16 | 100% | 6.74 | 100% |
| 1 | own | gold_cluster | 1000 | 0 | 70 | 50 | 15 | 11 | 0.00 | 0% | 0.00 | 0% |
| 5 | own | wolf | 1350 | 22 | 90 | 40 | 17 | 12 | 5.95 | 100% | 3.68 | 100% |
| 7 | own | elk | 2400 | 36 | 160 | 60 | 24 | 11 | 0.53 | 42% | 0.05 | 5% |
| 6 | mid | elk | 2400 | 36 | 160 | 60 | 27 | 3 | 0.21 | 21% | 0.47 | 32% |
| 2 | mid | gold_cluster | 1000 | 0 | 70 | 50 | 33 | 7 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | gem_cluster | 1500 | 72 | 0 | 50 | 14 | 5 | 0.00 | 0% | 0.58 | 37% |
| 4 | enemy | wolf | 1350 | 22 | 90 | 40 | 10 | 12 | 0.00 | 0% | 0.05 | 5% |
| 5 | enemy | wolf | 1350 | 22 | 90 | 40 | 17 | 12 | 0.00 | 0% | 0.00 | 0% |
| 1 | enemy | gold_cluster | 1000 | 0 | 70 | 50 | 15 | 11 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | elk | 2400 | 36 | 160 | 60 | 24 | 11 | 0.00 | 0% | 0.00 | 0% |
| 3 | enemy | wolf | 1350 | 22 | 90 | 40 | 4 | 12 | 0.00 | 0% | 0.05 | 5% |

**lanes** (17 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 3.82 | 100% | 4.41 | 100% |
| 5 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 4.12 | 100% | 4.41 | 100% |
| 6 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 4.00 | 100% | 4.65 | 100% |
| 7 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 8 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 9 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 18 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 3.35 | 94% | 4.41 | 100% |
| 19 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 3.00 | 94% | 4.53 | 100% |
| 20 | own | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 2.65 | 88% | 4.24 | 100% |
| 3 | own | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.35 | 35% | 0.65 | 35% |
| 10 | own | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.18 | 18% | 0.12 | 12% |
| 17 | own | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.06 | 6% | 0.59 | 35% |
| 11 | own | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 3.12 | 100% | 0.47 | 29% |
| 12 | own | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 2.65 | 100% | 0.35 | 24% |
| 13 | own | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 1.41 | 94% | 0.18 | 12% |
| 0 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 1.47 | 71% | 1.76 | 82% |
| 1 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 1.41 | 88% | 1.65 | 82% |
| 2 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.29 | 29% | 1.53 | 71% |
| 14 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.18 | 18% | 1.41 | 71% |
| 15 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.06 | 6% | 1.18 | 59% |
| 16 | mid | wolf | 1350 | 22 | 90 | 40 | 40 | 12 | 0.00 | 0% | 0.59 | 47% |
| 11 | enemy | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 0.65 | 53% | 0.18 | 18% |
| 12 | enemy | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 0.06 | 6% | 0.18 | 12% |
| 13 | enemy | wolf | 1350 | 22 | 90 | 40 | 36 | 11 | 0.00 | 0% | 0.12 | 12% |
| 3 | enemy | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.00 | 0% | 0.06 | 6% |
| 10 | enemy | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.00 | 0% | 0.00 | 0% |
| 17 | enemy | elk | 2400 | 36 | 160 | 60 | 33 | 8 | 0.00 | 0% | 0.00 | 0% |
| 4 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.47 | 29% |
| 5 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.59 | 41% |
| 6 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 0.53 | 35% |
| 7 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 5 | 0.00 | 0% | 0.00 | 0% |
| 18 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 1.18 | 53% |
| 19 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 1.12 | 41% |
| 20 | enemy | gem_cluster | 500 | 24 | 0 | 50 | 30 | 5 | 0.00 | 0% | 1.00 | 47% |

**monolith** (16 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | own | wolf | 1350 | 22 | 90 | 40 | 5 | 18 | 3.75 | 100% | 6.50 | 100% |
| 2 | own | wolf | 1350 | 22 | 90 | 40 | 9 | 14 | 3.50 | 100% | 4.38 | 100% |
| 5 | own | elk | 2400 | 36 | 160 | 60 | 12 | 15 | 1.38 | 88% | 3.19 | 100% |
| 4 | own | wolf | 1350 | 22 | 90 | 40 | 13 | 17 | 2.56 | 100% | 5.38 | 100% |
| 9 | own | wolf | 2700 | 44 | 180 | 40 | 20 | 11 | 5.00 | 100% | 5.81 | 100% |
| 6 | own | gold_cluster | 500 | 0 | 35 | 50 | 21 | 2 | 0.00 | 0% | 0.00 | 0% |
| 1 | own | wolf | 2700 | 44 | 180 | 40 | 23 | 6 | 5.19 | 100% | 3.38 | 100% |
| 7 | own | gold_cluster | 500 | 0 | 35 | 50 | 25 | 4 | 0.00 | 0% | 0.00 | 0% |
| 8 | own | gold_cluster | 500 | 0 | 35 | 50 | 30 | 1 | 0.00 | 0% | 0.00 | 0% |
| 10 | own | wolf | 2700 | 44 | 180 | 40 | 35 | 6 | 4.44 | 100% | 2.19 | 94% |
| 0 | own | gem_cluster+monolith | 24000 | 392 | 300 | 150 | 41 | 0 | 0.00 | 0% | 0.12 | 6% |
| 6 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 21 | 2 | 0.00 | 0% | 0.00 | 0% |
| 7 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 25 | 4 | 0.00 | 0% | 0.00 | 0% |
| 5 | enemy | elk | 2400 | 36 | 160 | 60 | 12 | 15 | 0.00 | 0% | 0.00 | 0% |
| 9 | enemy | wolf | 2700 | 44 | 180 | 40 | 20 | 11 | 0.00 | 0% | 0.00 | 0% |
| 8 | enemy | gold_cluster | 500 | 0 | 35 | 50 | 30 | 1 | 0.00 | 0% | 0.00 | 0% |
| 10 | enemy | wolf | 2700 | 44 | 180 | 40 | 35 | 6 | 1.62 | 75% | 0.38 | 31% |
| 1 | enemy | wolf | 2700 | 44 | 180 | 40 | 23 | 6 | 0.00 | 0% | 0.31 | 19% |
| 2 | enemy | wolf | 1350 | 22 | 90 | 40 | 9 | 14 | 0.00 | 0% | 0.12 | 12% |
| 4 | enemy | wolf | 1350 | 22 | 90 | 40 | 13 | 17 | 0.00 | 0% | 0.06 | 6% |
| 3 | enemy | wolf | 1350 | 22 | 90 | 40 | 5 | 18 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | gem_cluster+monolith | 24000 | 392 | 300 | 150 | 41 | 0 | 0.00 | 0% | 0.00 | 0% |

**packs** (22 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | wolf | 2700 | 44 | 180 | 40 | 4 | 4 | 6.09 | 100% | 7.05 | 100% |
| 2 | own | wolf | 2700 | 44 | 180 | 40 | 12 | 10 | 4.27 | 95% | 5.05 | 100% |
| 1 | mid | gem_cluster+gold_cluster | 2000 | 48 | 70 | 50 | 14 | 7 | 5.55 | 100% | 6.68 | 100% |
| 3 | mid | wolf | 2700 | 44 | 180 | 40 | 23 | 2 | 1.45 | 73% | 3.73 | 100% |
| 0 | enemy | wolf | 2700 | 44 | 180 | 40 | 4 | 4 | 0.00 | 0% | 0.09 | 9% |
| 2 | enemy | wolf | 2700 | 44 | 180 | 40 | 12 | 10 | 0.00 | 0% | 0.32 | 23% |

**rows** (17 games)

| jg | side | types | hp | gems | gold | respawn | dist from spawn | dist to altar | us captures/g | us % games | opp captures/g | opp % games |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | own | wolf | 4050 | 66 | 270 | 40 | 11 | 10 | 6.00 | 100% | 6.82 | 100% |
| 1 | own | wolf | 4050 | 66 | 270 | 40 | 24 | 23 | 5.71 | 100% | 5.88 | 100% |
| 2 | own | wolf | 4050 | 66 | 270 | 40 | 35 | 34 | 5.65 | 100% | 4.29 | 100% |
| 4 | own | gold_cluster | 1500 | 0 | 105 | 50 | 41 | 31 | 0.00 | 0% | 0.00 | 0% |
| 3 | mid | gem_cluster+monolith | 41000 | 448 | 600 | 150 | 34 | 24 | 0.00 | 0% | 0.00 | 0% |
| 4 | enemy | gold_cluster | 1500 | 0 | 105 | 50 | 41 | 31 | 0.00 | 0% | 0.00 | 0% |
| 0 | enemy | wolf | 4050 | 66 | 270 | 40 | 11 | 10 | 0.00 | 0% | 0.00 | 0% |
| 1 | enemy | wolf | 4050 | 66 | 270 | 40 | 24 | 23 | 0.00 | 0% | 0.00 | 0% |
| 2 | enemy | wolf | 4050 | 66 | 270 | 40 | 35 | 34 | 0.00 | 0% | 0.00 | 0% |

### Captures per game by territory (own / mid / enemy), us vs opp

| split | n | us own/mid/enemy | opp own/mid/enemy |
|---|---|---|---|
| all | 155 | 19.5 / 4.1 / 0.3 | 20.8 / 4.7 / 1.2 |
| map collision | 19 | 20.8 / 10.5 / 0.1 | 23.5 / 6.4 / 0.8 |
| map corners | 19 | 2.9 / 11.3 / 0.0 | 7.4 / 12.1 / 0.5 |
| map elkring | 9 | 24.7 / 0.0 / 0.9 | 26.0 / 0.0 / 2.9 |
| map expanse | 17 | 23.9 / 0.0 / 0.0 | 26.1 / 0.0 / 0.2 |
| map interlock | 19 | 27.1 / 0.2 / 0.0 | 21.8 / 0.5 / 0.7 |
| map lanes | 17 | 28.7 / 3.4 / 0.7 | 29.0 / 8.1 / 5.4 |
| map monolith | 16 | 25.8 / 0.0 / 1.6 | 30.9 / 0.0 / 0.9 |
| map packs | 22 | 10.4 / 7.0 / 0.0 | 12.1 / 10.4 / 0.4 |
| map rows | 17 | 17.4 / 0.0 / 0.0 | 17.0 / 0.0 / 0.0 |
| win | 58 | 22.0 / 5.9 / 0.3 | 20.5 / 2.4 / 0.4 |
| loss | 97 | 17.9 / 2.9 / 0.3 | 20.9 / 6.1 / 1.6 |
| opp top10 | 50 | 18.1 / 3.0 / 0.3 | 20.1 / 5.8 / 0.8 |
| opp 11-20 | 50 | 20.5 / 4.1 / 0.4 | 22.6 / 4.7 / 1.6 |
| opp 21-30 | 50 | 19.8 / 4.8 / 0.3 | 19.7 / 3.7 / 1.3 |
| opp other | 5 | 19.6 / 7.2 / 0.2 | 19.4 / 3.2 / 0.0 |

### Opening order: the first 5 groups our team captures (jg/side), most common sequences per map

- collision: first capture round med 33; 3m-3m-2o-1o-0o x5; 3m-3m-2o-0o-1o x3; 3m-3m-1o-0o-2o x2
- corners: first capture round med 37; 0m-1m-0m-1m-3o x4; 1m-3o-3o-1m x1; 0m-1m-0m-1m-9o x1
- elkring: first capture round med 21; 0o-1o-2o-3o-0o x4; 0o-1o-2o-4o-0o x1; 0o-1o-2o-0o-1o x1
- expanse: first capture round med 30; 1o-11o-0o-2o-10o x16; 1o-11o-0o-2o-12o x1
- interlock: first capture round med 20; 3o-4o-0o-5o-3o x15; 3o-4o-0o-5o-4o x2; 3o-4o-5o-0o-3o x1
- lanes: first capture round med 41; 5o-18o-4o-6o-19o x13; 5o-18o-4o-6o-11o x2; 5o-18o-4o-6o-20o x1
- monolith: first capture round med 19; 3o-2o-9o-4o-1o x16
- packs: first capture round med 33; 1m-1m-0o-2o-1m x9; 1m-0o-2o-1m-0o x3; 0o-1m-0o-2o-0o x2
- rows: first capture round med 33; 0o-1o-2o-0o-1o x16; 0o-1o-0o-1o-2o x1

### Camp set per map: groups taken in >=80% / >=50% of games, mean distinct groups per game, Jaccard between games (us vs opp)

| map | n | us core(>=80%) | us >=50% | us distinct/g | us jaccard | opp core | opp >=50% | opp distinct/g | opp jaccard |
|---|---|---|---|---|---|---|---|---|---|
| collision | 19 | 4 | 4 | 4.5 | 0.86 | 3 | 5 | 5.7 | 0.66 |
| corners | 19 | 2 | 3 | 3.2 | 0.58 | 3 | 5 | 5.5 | 0.46 |
| elkring | 9 | 4 | 6 | 5.7 | 0.78 | 5 | 6 | 6.3 | 0.77 |
| expanse | 17 | 9 | 9 | 8.8 | 0.94 | 6 | 6 | 7.1 | 0.73 |
| interlock | 19 | 4 | 4 | 4.6 | 0.84 | 4 | 4 | 4.8 | 0.79 |
| lanes | 17 | 10 | 12 | 12.0 | 0.74 | 8 | 12 | 14.5 | 0.56 |
| monolith | 16 | 7 | 8 | 7.6 | 0.92 | 7 | 7 | 7.7 | 0.85 |
| packs | 22 | 3 | 4 | 3.7 | 0.87 | 4 | 4 | 4.3 | 0.89 |
| rows | 17 | 3 | 3 | 3.0 | 1.00 | 3 | 3 | 3.0 | 1.00 |

### Revisits: rounds between a group respawn and our next capture of it (non-first captures); nearest-up rule

| split | n | us revisits | gap med | mean | us captures | nearest-up chosen | 1st or 2nd nearest | extra dist med | mean | opp revisits | gap med | mean | opp captures | nearest | 1st/2nd | extra med | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 155 | 2787 | 33 | 45 | 3694 | 46% | 66% | 0 | 4.8 | 3221 | 33 | 46 | 4129 | 51% | 71% | 0 | 4.0 |
| map collision | 19 | 499 | 41 | 55 | 596 | 55% | 73% | 0 | 3.7 | 496 | 48 | 62 | 585 | 57% | 78% | 0 | 3.9 |
| map corners | 19 | 187 | 38 | 57 | 270 | 30% | 36% | 12 | 8.6 | 288 | 44 | 63 | 378 | 39% | 46% | 5 | 6.9 |
| map elkring | 9 | 188 | 40 | 48 | 230 | 55% | 81% | 0 | 3.8 | 211 | 35 | 50 | 260 | 59% | 79% | 0 | 3.5 |
| map expanse | 17 | 256 | 43 | 47 | 406 | 29% | 54% | 6 | 8.5 | 326 | 29 | 35 | 446 | 48% | 70% | 0 | 5.3 |
| map interlock | 19 | 430 | 24 | 31 | 518 | 53% | 76% | 0 | 3.6 | 353 | 32 | 44 | 437 | 56% | 78% | 0 | 3.3 |
| map lanes | 17 | 368 | 28 | 43 | 558 | 35% | 52% | 0 | 2.1 | 496 | 25 | 38 | 723 | 40% | 55% | 0 | 2.2 |
| map monolith | 16 | 317 | 44 | 56 | 439 | 37% | 54% | 3 | 6.3 | 405 | 33 | 44 | 507 | 47% | 68% | 1 | 4.4 |
| map packs | 22 | 298 | 32 | 41 | 382 | 60% | 83% | 0 | 2.6 | 409 | 34 | 45 | 504 | 58% | 82% | 0 | 3.2 |
| map rows | 17 | 244 | 29 | 28 | 295 | 56% | 95% | 0 | 7.1 | 237 | 22 | 26 | 289 | 69% | 94% | 0 | 5.0 |
| win | 58 | 1271 | 32 | 43 | 1638 | 44% | 64% | 1 | 5.1 | 1035 | 35 | 51 | 1352 | 50% | 72% | 0 | 4.4 |
| loss | 97 | 1516 | 35 | 46 | 2056 | 47% | 68% | 0 | 4.5 | 2186 | 32 | 43 | 2777 | 52% | 70% | 0 | 3.8 |
| opp top10 | 50 | 781 | 30 | 44 | 1066 | 46% | 67% | 0 | 4.5 | 1049 | 30 | 42 | 1333 | 52% | 72% | 0 | 3.7 |
| opp 11-20 | 50 | 940 | 35 | 45 | 1246 | 45% | 66% | 0 | 4.7 | 1131 | 33 | 46 | 1447 | 51% | 69% | 0 | 3.9 |
| opp 21-30 | 50 | 968 | 34 | 46 | 1247 | 46% | 66% | 0 | 5.1 | 965 | 35 | 48 | 1236 | 51% | 72% | 0 | 4.4 |
| opp other | 5 | 98 | 31 | 46 | 135 | 41% | 59% | 2 | 5.2 | 76 | 40 | 55 | 113 | 46% | 71% | 0 | 3.8 |

### Groups (jg/side in each team's own view) with captures/g by us <0.2 but by opp >=0.5, and the reverse

- collision: opp farms, we do not: ['2e(22g,1350hp,d12: us 0.05 opp 0.63)', '9o(108g,3900hp,d30: us 0.11 opp 1.63)']; we farm, opp does not: -
- corners: opp farms, we do not: -; we farm, opp does not: -
- elkring: opp farms, we do not: -; we farm, opp does not: -
- expanse: opp farms, we do not: -; we farm, opp does not: -
- interlock: opp farms, we do not: ['0e(72g,1500hp,d14: us 0.00 opp 0.58)']; we farm, opp does not: ['7o(36g: us 0.53 opp 0.05)']
- lanes: opp farms, we do not: ['5e(24g,500hp,d30: us 0.00 opp 0.59)', '6e(24g,500hp,d30: us 0.00 opp 0.53)', '14m(22g,1350hp,d40: us 0.18 opp 1.41)', '15m(22g,1350hp,d40: us 0.06 opp 1.18)', '16m(22g,1350hp,d40: us 0.00 opp 0.59)', '17o(36g,2400hp,d33: us 0.06 opp 0.59)', '18e(24g,500hp,d30: us 0.00 opp 1.18)', '19e(24g,500hp,d30: us 0.00 opp 1.12)', '20e(24g,500hp,d30: us 0.00 opp 1.00)']; we farm, opp does not: ['11e(22g: us 0.65 opp 0.18)', '13o(22g: us 1.41 opp 0.18)']
- monolith: opp farms, we do not: -; we farm, opp does not: -
- packs: opp farms, we do not: -; we farm, opp does not: -
- rows: opp farms, we do not: -; we farm, opp does not: -


## Q4 Squad size and kill speed

### By group hp (Mite reference: 2.0/2.05/2.4/3.5 attackers, 12/17/21/23 rounds)

| split | team | bucket | captures | attackers mean | within 4 at capture | hit->capture med | mean | group hp/attacker/round med | measured dmg/attacker/round med |
|---|---|---|---|---|---|---|---|---|---|
| all | us | <1500 | 1923 | 1.51 | 1.63 | 23 | 30.6 | 42 | 40 |
| all | us | <3000 | 1099 | 2.01 | 1.37 | 24 | 29.9 | 50 | 48 |
| all | us | <800 | 356 | 1.14 | 1.97 | 17 | 18.8 | 28 | 28 |
| all | us | >=3000 | 316 | 3.18 | 1.34 | 20 | 19.9 | 64 | 64 |
| all | opp | <1500 | 2004 | 1.83 | 1.57 | 21 | 28.8 | 38 | 38 |
| all | opp | <3000 | 1255 | 2.31 | 1.35 | 23 | 29.1 | 47 | 47 |
| all | opp | <800 | 536 | 1.36 | 1.90 | 15 | 16.7 | 29 | 29 |
| all | opp | >=3000 | 336 | 2.72 | 1.15 | 22 | 28.5 | 68 | 68 |

### By round (first 50 rounds vs later)

| split | team | bucket | captures | attackers mean | within 4 at capture | hit->capture med | mean | group hp/attacker/round med | measured dmg/attacker/round med |
|---|---|---|---|---|---|---|---|---|---|
| all | us | <150 | 762 | 1.93 | 1.61 | 24 | 28.6 | 36 | 34 |
| all | us | <300 | 1140 | 1.77 | 1.44 | 21 | 29.2 | 48 | 45 |
| all | us | <50 | 358 | 1.94 | 2.01 | 19 | 20.8 | 38 | 36 |
| all | us | >=300 | 1434 | 1.63 | 1.51 | 20 | 29.3 | 58 | 53 |
| all | opp | <150 | 836 | 2.13 | 1.48 | 23 | 27.0 | 34 | 34 |
| all | opp | <300 | 1345 | 1.93 | 1.47 | 21 | 28.3 | 39 | 38 |
| all | opp | <50 | 382 | 2.56 | 1.87 | 18 | 19.5 | 33 | 33 |
| all | opp | >=300 | 1568 | 1.82 | 1.49 | 19 | 28.5 | 54 | 52 |

### By map, all hp buckets pooled

| map | team | captures | attackers mean | hit->capture med | mean group hp | hp/attacker/round med |
|---|---|---|---|---|---|---|
| collision | us | 596 | 1.56 | 20 | 1371 | 45 |
| collision | opp | 585 | 1.72 | 21 | 1522 | 45 |
| corners | us | 270 | 2.02 | 26 | 1108 | 27 |
| corners | opp | 378 | 2.42 | 26 | 1272 | 24 |
| elkring | us | 230 | 2.47 | 26 | 2900 | 45 |
| elkring | opp | 260 | 3.02 | 22 | 2900 | 43 |
| expanse | us | 406 | 1.14 | 24 | 1428 | 53 |
| expanse | opp | 446 | 1.43 | 20 | 1270 | 40 |
| interlock | us | 518 | 1.80 | 19 | 1412 | 40 |
| interlock | opp | 437 | 1.88 | 21 | 1422 | 40 |
| lanes | us | 558 | 1.20 | 18 | 827 | 31 |
| lanes | opp | 723 | 1.53 | 16 | 755 | 29 |
| monolith | us | 439 | 1.48 | 25 | 2202 | 54 |
| monolith | opp | 509 | 1.85 | 21 | 2056 | 54 |
| packs | us | 382 | 2.13 | 23 | 2476 | 50 |
| packs | opp | 504 | 2.26 | 23 | 2496 | 50 |
| rows | us | 295 | 3.26 | 19 | 4050 | 63 |
| rows | opp | 289 | 2.96 | 21 | 4050 | 64 |

### By win/loss and opponent tier, hp >= 800 groups

| split | team | captures (hp>=800) | attackers mean | hit->capture med | hp/attacker/round med |
|---|---|---|---|---|---|
| win | us | 1548 | 1.76 | 22 | 45 |
| win | opp | 1268 | 2.06 | 21 | 42 |
| loss | us | 1790 | 1.90 | 23 | 50 |
| loss | opp | 2327 | 2.09 | 22 | 45 |
| opp top10 | us | 946 | 1.89 | 22 | 47 |
| opp top10 | opp | 1173 | 2.18 | 21 | 44 |
| opp 11-20 | us | 1093 | 1.82 | 23 | 48 |
| opp 11-20 | opp | 1196 | 1.99 | 21 | 45 |
| opp 21-30 | us | 1194 | 1.80 | 23 | 45 |
| opp 21-30 | opp | 1130 | 2.10 | 23 | 41 |
| opp other | us | 105 | 1.74 | 23 | 48 |
| opp other | opp | 96 | 1.86 | 24 | 48 |

### Attackers distribution per hp bucket (count of captures by number of attackers), us vs opp

| team | hp bucket | captures | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|---|---|
| us | <1500 | 1923 | 1170 | 572 | 139 | 36 | 6 |
| us | <3000 | 1099 | 295 | 564 | 179 | 57 | 4 |
| us | <800 | 356 | 308 | 45 | 3 | 0 | 0 |
| us | >=3000 | 316 | 7 | 73 | 93 | 143 | 0 |
| opp | <1500 | 2004 | 941 | 650 | 274 | 98 | 41 |
| opp | <3000 | 1255 | 319 | 455 | 309 | 124 | 48 |
| opp | <800 | 536 | 367 | 146 | 21 | 2 | 0 |
| opp | >=3000 | 336 | 67 | 58 | 131 | 62 | 18 |

### Who tanks: champion type taking most monster damage during the capture, by capturing team (count); and monster damage taken per type

- us tank per capture: {'Issac': 577, 'Ren': 518, 'Varg': 328, 'Vendetta': 325, 'Cassi': 285, 'Stellar': 240, 'Ryth': 231, 'Tavi': 131, 'Prism': 43, 'Marcella': 1, 'VesperVale': 1}
- us monster damage taken per champion-game: Cassi 815 (40 hits), Issac 1610 (84 hits), Ren 2032 (82 hits), Stellar 952 (37 hits), Tavi 769 (28 hits), Ryth 1574 (54 hits), Vendetta 1866 (92 hits), Varg 1549 (63 hits), Prism 1393 (26 hits)
- opp tank per capture: {'Issac': 653, 'Ren': 433, 'Varg': 393, 'Stellar': 350, 'Cassi': 281, 'Vendetta': 271, 'Ryth': 211, 'Tavi': 143, 'Prism': 36, 'Willow': 18, 'Marcella': 17, 'VesperVale': 5}
- opp monster damage taken per champion-game: Cassi 822 (37 hits), Issac 1859 (86 hits), Stellar 965 (43 hits), Varg 1079 (44 hits), Ren 1558 (67 hits), Tavi 859 (34 hits), Ryth 1558 (59 hits), Vendetta 1876 (87 hits), Prism 1142 (36 hits), Willow 576 (21 hits), Marcella 2063 (60 hits), VesperVale 1213 (34 hits)

### Basic-attack distance to the camp monster (share of basic attacks on camps at Chebyshev distance 1 / 2 / 3+), by type

| team | type | camp basic attacks | d0 | d1 | d2 | d3+ |
|---|---|---|---|---|---|---|
| us | Issac | 14841 | 0% | 100% | 0% | 0% |
| us | Cassi | 12682 | 0% | 0% | 3% | 97% |
| us | Varg | 11203 | 0% | 82% | 18% | 0% |
| us | Ren | 7853 | 0% | 100% | 0% | 0% |
| us | Tavi | 7746 | 0% | 1% | 6% | 93% |
| us | Vendetta | 6793 | 0% | 100% | 0% | 0% |
| us | Stellar | 6690 | 0% | 1% | 7% | 92% |
| us | Ryth | 6362 | 0% | 100% | 0% | 0% |
| us | Prism | 2002 | 0% | 1% | 10% | 89% |
| opp | Issac | 15408 | 0% | 100% | 0% | 0% |
| opp | Cassi | 13408 | 0% | 5% | 8% | 87% |
| opp | Varg | 12853 | 0% | 73% | 27% | 0% |
| opp | Stellar | 8878 | 0% | 6% | 10% | 83% |
| opp | Ren | 7573 | 0% | 100% | 0% | 0% |
| opp | Vendetta | 5506 | 0% | 100% | 0% | 0% |
| opp | Tavi | 5449 | 0% | 6% | 7% | 87% |
| opp | Ryth | 4972 | 0% | 100% | 0% | 0% |
| opp | Willow | 1509 | 0% | 3% | 6% | 91% |
| opp | Prism | 1494 | 0% | 4% | 12% | 85% |
| opp | Marcella | 417 | 0% | 100% | 0% | 0% |
| opp | VesperVale | 159 | 0% | 28% | 7% | 65% |

### Team-level: attackers by map in the first capture of the game (whole team on the first camp?)

| map | nch | us attackers 1st camp | 1st capture round | hit->cap | opp attackers | 1st capture round | hit->cap |
|---|---|---|---|---|---|---|---|
| collision | 4 | 2.00 | 33 | 18 | 2.68 | 18 | 16 |
| corners | 5 | 2.16 | 37 | 18 | 2.95 | 28 | 18 |
| elkring | 5 | 4.00 | 21 | 18 | 4.78 | 19 | 17 |
| expanse | 4 | 2.00 | 30 | 17 | 2.47 | 25 | 16 |
| interlock | 5 | 2.00 | 20 | 15 | 3.00 | 24 | 15 |
| lanes | 6 | 1.00 | 41 | 14 | 1.41 | 41 | 14 |
| monolith | 6 | 3.00 | 19 | 15 | 3.06 | 18 | 14 |
| packs | 4 | 2.18 | 33 | 19 | 3.23 | 24 | 20 |
| rows | 5 | 3.94 | 33 | 23 | 4.88 | 31 | 20 |


## Q5 Bags and tributes

| split | team | n | tribute starts | completed | completed/game | per 100 champ-rounds | bag med | mean | p90 | bags<=10 | bags>=100 | captures per bag | oldest gems age med | newest age med | not completed | ..died | ..cancelled | ..other | altar passes with >=10 gems | passes/game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 155 | 3265 | 3040 | 19.6 | 0.95 | 44 | 41 | 66 | 0% | 1% | 1.10 | 11 | 10 | 225 (7%) | 39 | 2 | 184 | 150 | 0.97 |
| all | opp | 155 | 3509 | 3168 | 20.4 | 0.94 | 44 | 44 | 70 | 0% | 2% | 1.21 | 12 | 10 | 341 (10%) | 45 | 1 | 295 | 307 | 1.98 |
| map collision | us | 19 | 461 | 405 | 21.3 | 0.93 | 22 | 33 | 44 | 0% | 2% | 1.25 | 17 | 10 | 56 (12%) | 15 | 1 | 40 | 25 | 1.32 |
| map collision | opp | 19 | 432 | 371 | 19.5 | 0.82 | 22 | 39 | 66 | 0% | 6% | 1.33 | 24 | 14 | 61 (14%) | 9 | 0 | 52 | 69 | 3.63 |
| map corners | us | 19 | 300 | 247 | 13.0 | 0.62 | 48 | 45 | 48 | 0% | 1% | 1.03 | 2 | 2 | 53 (18%) | 8 | 1 | 44 | 40 | 2.11 |
| map corners | opp | 19 | 410 | 323 | 17.0 | 0.62 | 48 | 43 | 48 | 0% | 1% | 1.09 | 7 | 7 | 87 (21%) | 4 | 0 | 83 | 98 | 5.16 |
| map elkring | us | 9 | 216 | 207 | 23.0 | 0.82 | 36 | 39 | 36 | 0% | 0% | 1.00 | 26 | 26 | 9 (4%) | 0 | 0 | 9 | 3 | 0.33 |
| map elkring | opp | 9 | 213 | 192 | 21.3 | 0.72 | 36 | 42 | 72 | 0% | 2% | 1.19 | 19 | 16 | 21 (10%) | 6 | 0 | 15 | 10 | 1.11 |
| map expanse | us | 17 | 401 | 395 | 23.2 | 1.58 | 48 | 40 | 48 | 0% | 3% | 1.01 | 9 | 9 | 6 (1%) | 0 | 0 | 6 | 0 | 0.00 |
| map expanse | opp | 17 | 360 | 353 | 20.8 | 1.42 | 48 | 46 | 70 | 0% | 3% | 1.21 | 8 | 7 | 7 (2%) | 0 | 0 | 7 | 0 | 0.00 |
| map interlock | us | 19 | 469 | 414 | 21.8 | 0.98 | 22 | 39 | 72 | 0% | 2% | 1.05 | 21 | 21 | 55 (12%) | 7 | 0 | 48 | 38 | 2.00 |
| map interlock | opp | 19 | 442 | 332 | 17.5 | 0.84 | 44 | 47 | 72 | 0% | 1% | 1.22 | 19 | 14 | 110 (25%) | 22 | 0 | 88 | 95 | 5.00 |
| map lanes | us | 17 | 420 | 412 | 24.2 | 1.17 | 24 | 30 | 48 | 0% | 0% | 1.26 | 9 | 5 | 8 (2%) | 0 | 0 | 8 | 1 | 0.06 |
| map lanes | opp | 17 | 551 | 530 | 31.2 | 1.42 | 24 | 32 | 48 | 0% | 0% | 1.31 | 6 | 6 | 21 (4%) | 1 | 0 | 20 | 9 | 0.53 |
| map monolith | us | 16 | 375 | 355 | 22.2 | 0.87 | 44 | 41 | 44 | 0% | 1% | 1.13 | 27 | 26 | 20 (5%) | 3 | 0 | 17 | 43 | 2.69 |
| map monolith | opp | 16 | 376 | 347 | 21.7 | 0.86 | 44 | 44 | 66 | 0% | 2% | 1.37 | 24 | 18 | 29 (8%) | 3 | 1 | 25 | 25 | 1.56 |
| map packs | us | 22 | 378 | 367 | 16.7 | 1.05 | 44 | 45 | 48 | 0% | 0% | 1.00 | 5 | 5 | 11 (3%) | 5 | 0 | 6 | 0 | 0.00 |
| map packs | opp | 22 | 476 | 472 | 21.5 | 1.21 | 44 | 45 | 48 | 0% | 0% | 1.05 | 7 | 7 | 4 (1%) | 0 | 0 | 4 | 1 | 0.05 |
| map rows | us | 17 | 245 | 238 | 14.0 | 0.71 | 66 | 69 | 66 | 0% | 0% | 1.08 | 10 | 10 | 7 (3%) | 1 | 0 | 6 | 0 | 0.00 |
| map rows | opp | 17 | 249 | 248 | 14.6 | 0.74 | 66 | 71 | 66 | 0% | 8% | 1.11 | 14 | 14 | 1 (0%) | 0 | 0 | 1 | 0 | 0.00 |
| win | us | 58 | 1595 | 1477 | 25.5 | 1.12 | 44 | 40 | 66 | 0% | 2% | 1.08 | 11 | 11 | 118 (7%) | 10 | 1 | 107 | 83 | 1.43 |
| win | opp | 58 | 1066 | 932 | 16.1 | 0.76 | 44 | 43 | 70 | 0% | 2% | 1.19 | 13 | 11 | 134 (13%) | 25 | 1 | 108 | 178 | 3.07 |
| loss | us | 97 | 1670 | 1563 | 16.1 | 0.83 | 44 | 41 | 66 | 0% | 1% | 1.12 | 11 | 10 | 107 (6%) | 29 | 1 | 77 | 67 | 0.69 |
| loss | opp | 97 | 2443 | 2236 | 23.1 | 1.04 | 44 | 45 | 70 | 0% | 3% | 1.22 | 11 | 9 | 207 (8%) | 20 | 0 | 187 | 129 | 1.33 |
| opp top10 | us | 50 | 918 | 870 | 17.4 | 0.92 | 44 | 41 | 66 | 0% | 1% | 1.11 | 10 | 10 | 48 (5%) | 7 | 0 | 41 | 22 | 0.44 |
| opp top10 | opp | 50 | 1143 | 1055 | 21.1 | 1.02 | 44 | 45 | 72 | 0% | 4% | 1.20 | 11 | 10 | 88 (8%) | 4 | 0 | 84 | 75 | 1.50 |
| opp 11-20 | us | 50 | 1068 | 996 | 19.9 | 0.94 | 44 | 40 | 66 | 0% | 1% | 1.11 | 11 | 10 | 72 (7%) | 17 | 0 | 55 | 65 | 1.30 |
| opp 11-20 | opp | 50 | 1203 | 1076 | 21.5 | 0.96 | 44 | 43 | 72 | 0% | 2% | 1.25 | 13 | 10 | 127 (11%) | 22 | 1 | 104 | 90 | 1.80 |
| opp 21-30 | us | 50 | 1156 | 1057 | 21.1 | 0.96 | 44 | 41 | 66 | 0% | 1% | 1.09 | 15 | 12 | 99 (9%) | 15 | 2 | 82 | 61 | 1.22 |
| opp 21-30 | opp | 50 | 1067 | 942 | 18.8 | 0.84 | 44 | 44 | 70 | 0% | 2% | 1.19 | 11 | 9 | 125 (12%) | 19 | 0 | 106 | 136 | 2.72 |
| opp other | us | 5 | 123 | 117 | 23.4 | 1.18 | 46 | 44 | 66 | 0% | 2% | 1.09 | 7 | 5 | 6 (5%) | 0 | 0 | 6 | 2 | 0.40 |
| opp other | opp | 5 | 96 | 95 | 19.0 | 0.96 | 44 | 42 | 66 | 0% | 0% | 1.11 | 7 | 7 | 1 (1%) | 0 | 0 | 1 | 6 | 1.20 |

### Bag distribution at tribute completion (count), us vs opp

| team | tributes | <=10 | 11-22 | 23-44 | 45-66 | 67-100 | >100 |
|---|---|---|---|---|---|---|---|
| us | 3040 | 0 | 836 | 1215 | 799 | 153 | 37 |
| opp | 3168 | 0 | 704 | 1217 | 902 | 272 | 73 |

### Recall as a teleport: captures followed by a recall start within [-5,+3] rounds; cost comparison walk-to-altar vs 5+spawn-to-altar

| split | team | captures | followed by recall | % | walk camp->altar med | 5+spawn->altar med | captures where recall is shorter | ..of which recalled | captures where walking is shorter | ..of which recalled | gems carried on recalled captures med |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 3694 | 1882 | 51% | 10 | 20 | 695 | 405 (58%) | 2999 | 1477 (49%) | 36 |
| all | opp | 4131 | 1060 | 26% | 9 | 20 | 732 | 368 (50%) | 3399 | 692 (20%) | 44 |
| map collision | us | 596 | 191 | 32% | 7 | 24 | 2 | 2 (100%) | 594 | 189 (32%) | 22 |
| map collision | opp | 585 | 118 | 20% | 11 | 24 | 32 | 21 (66%) | 553 | 97 (18%) | 44 |
| map corners | us | 270 | 68 | 25% | 2 | 22 | 40 | 38 (95%) | 230 | 30 (13%) | 22 |
| map corners | opp | 378 | 85 | 22% | 2 | 22 | 63 | 22 (35%) | 315 | 63 (20%) | 36 |
| map elkring | us | 230 | 188 | 82% | 13 | 26 | 0 | 0 (0%) | 230 | 188 (82%) | 36 |
| map elkring | opp | 260 | 41 | 16% | 13 | 26 | 0 | 0 (0%) | 260 | 41 (16%) | 36 |
| map expanse | us | 406 | 214 | 53% | 8 | 10 | 52 | 18 (35%) | 354 | 196 (55%) | 22 |
| map expanse | opp | 446 | 58 | 13% | 8 | 10 | 36 | 3 (8%) | 410 | 55 (13%) | 22 |
| map interlock | us | 518 | 321 | 62% | 13 | 20 | 0 | 0 (0%) | 518 | 321 (62%) | 22 |
| map interlock | opp | 437 | 78 | 18% | 13 | 20 | 0 | 0 (0%) | 437 | 78 (18%) | 22 |
| map lanes | us | 558 | 50 | 9% | 6 | 10 | 192 | 44 (23%) | 366 | 6 (2%) | 44 |
| map lanes | opp | 723 | 51 | 7% | 6 | 10 | 163 | 29 (18%) | 560 | 22 (4%) | 44 |
| map monolith | us | 439 | 369 | 84% | 12 | 28 | 0 | 0 (0%) | 439 | 369 (84%) | 44 |
| map monolith | opp | 509 | 184 | 36% | 15 | 28 | 0 | 0 (0%) | 509 | 184 (36%) | 44 |
| map packs | us | 382 | 235 | 62% | 8 | 6 | 216 | 112 (52%) | 166 | 123 (74%) | 44 |
| map packs | opp | 504 | 222 | 44% | 8 | 6 | 265 | 135 (51%) | 239 | 87 (36%) | 44 |
| map rows | us | 295 | 246 | 83% | 24 | 13 | 193 | 191 (99%) | 102 | 55 (54%) | 66 |
| map rows | opp | 289 | 223 | 77% | 24 | 13 | 173 | 158 (91%) | 116 | 65 (56%) | 66 |
| win | us | 1638 | 835 | 51% | 9 | 20 | 199 | 112 (56%) | 1439 | 723 (50%) | 36 |
| win | opp | 1352 | 317 | 23% | 11 | 20 | 168 | 65 (39%) | 1184 | 252 (21%) | 44 |
| loss | us | 2056 | 1047 | 51% | 11 | 13 | 496 | 293 (59%) | 1560 | 754 (48%) | 44 |
| loss | opp | 2779 | 743 | 27% | 9 | 13 | 564 | 303 (54%) | 2215 | 440 (20%) | 44 |
| opp top10 | us | 1066 | 559 | 52% | 11 | 16 | 233 | 145 (62%) | 833 | 414 (50%) | 44 |
| opp top10 | opp | 1333 | 345 | 26% | 9 | 20 | 258 | 138 (53%) | 1075 | 207 (19%) | 44 |
| opp 11-20 | us | 1246 | 598 | 48% | 10 | 20 | 226 | 118 (52%) | 1020 | 480 (47%) | 36 |
| opp 11-20 | opp | 1447 | 297 | 21% | 9 | 20 | 239 | 104 (44%) | 1208 | 193 (16%) | 44 |
| opp 21-30 | us | 1247 | 670 | 54% | 10 | 20 | 191 | 115 (60%) | 1056 | 555 (53%) | 36 |
| opp 21-30 | opp | 1238 | 377 | 30% | 10 | 20 | 202 | 109 (54%) | 1036 | 268 (26%) | 44 |
| opp other | us | 135 | 55 | 41% | 7 | 10 | 45 | 27 (60%) | 90 | 28 (31%) | 44 |
| opp other | opp | 113 | 41 | 36% | 9 | 10 | 33 | 17 (52%) | 80 | 24 (30%) | 44 |

### Recalls: per game, hp at start, gems carried, interrupted/died, and what happened after arrival (purchase within 2 rounds)

| split | team | recall starts | per game | arrived | interrupted/died | arrivals with hp>=70% | hp frac med | gems carried med | % carrying gems | gold carried med | arrival followed by purchase |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 3831 | 24.7 | 3647 | 184 | 34% | 0.51 | 0 | 16% | 0 | 66% |
| all | opp | 3575 | 23.1 | 3365 | 210 | 28% | 0.45 | 0 | 34% | 20 | 64% |
| map collision | us | 601 | 31.6 | 556 | 45 | 31% | 0.44 | 0 | 26% | 10 | 69% |
| map collision | opp | 600 | 31.6 | 556 | 44 | 16% | 0.38 | 0 | 46% | 70 | 66% |
| map corners | us | 430 | 22.6 | 378 | 52 | 5% | 0.35 | 0 | 13% | 0 | 30% |
| map corners | opp | 706 | 37.2 | 649 | 57 | 6% | 0.32 | 0 | 24% | 10 | 36% |
| map elkring | us | 432 | 48.0 | 421 | 11 | 29% | 0.50 | 0 | 17% | 10 | 58% |
| map elkring | opp | 290 | 32.2 | 274 | 16 | 25% | 0.44 | 0 | 28% | 113 | 60% |
| map expanse | us | 250 | 14.7 | 250 | 0 | 34% | 0.60 | 0 | 1% | 0 | 80% |
| map expanse | opp | 135 | 7.9 | 135 | 0 | 37% | 0.62 | 0 | 33% | 90 | 86% |
| map interlock | us | 535 | 28.2 | 511 | 24 | 48% | 0.67 | 0 | 21% | 0 | 70% |
| map interlock | opp | 380 | 20.0 | 347 | 33 | 17% | 0.39 | 0 | 29% | 20 | 58% |
| map lanes | us | 196 | 11.5 | 194 | 2 | 12% | 0.36 | 0 | 22% | 55 | 58% |
| map lanes | opp | 159 | 9.4 | 153 | 6 | 16% | 0.38 | 0 | 43% | 50 | 65% |
| map monolith | us | 535 | 33.4 | 526 | 9 | 40% | 0.64 | 0 | 10% | 0 | 78% |
| map monolith | opp | 434 | 27.1 | 410 | 24 | 45% | 0.65 | 0 | 36% | 90 | 83% |
| map packs | us | 524 | 23.8 | 483 | 41 | 39% | 0.56 | 0 | 7% | 0 | 64% |
| map packs | opp | 546 | 24.8 | 517 | 29 | 45% | 0.63 | 0 | 29% | 70 | 70% |
| map rows | us | 328 | 19.3 | 328 | 0 | 58% | 0.80 | 0 | 27% | 0 | 88% |
| map rows | opp | 325 | 19.1 | 324 | 1 | 60% | 0.79 | 0 | 42% | 20 | 79% |
| win | us | 1620 | 27.9 | 1574 | 46 | 35% | 0.54 | 0 | 17% | 0 | 69% |
| win | opp | 1342 | 23.1 | 1227 | 115 | 24% | 0.41 | 0 | 35% | 20 | 57% |
| loss | us | 2211 | 22.8 | 2073 | 138 | 34% | 0.49 | 0 | 16% | 0 | 65% |
| loss | opp | 2233 | 23.0 | 2138 | 95 | 30% | 0.47 | 0 | 33% | 50 | 68% |
| opp top10 | us | 1131 | 22.6 | 1066 | 65 | 35% | 0.51 | 0 | 15% | 0 | 66% |
| opp top10 | opp | 1097 | 21.9 | 1042 | 55 | 29% | 0.49 | 0 | 36% | 70 | 67% |
| opp 11-20 | us | 1255 | 25.1 | 1190 | 65 | 33% | 0.50 | 0 | 17% | 0 | 67% |
| opp 11-20 | opp | 1105 | 22.1 | 1033 | 72 | 28% | 0.42 | 0 | 37% | 70 | 67% |
| opp 21-30 | us | 1352 | 27.0 | 1300 | 52 | 35% | 0.53 | 0 | 16% | 0 | 66% |
| opp 21-30 | opp | 1262 | 25.2 | 1185 | 77 | 27% | 0.44 | 0 | 30% | 20 | 59% |
| opp other | us | 93 | 18.6 | 91 | 2 | 32% | 0.54 | 0 | 20% | 0 | 69% |
| opp other | opp | 111 | 22.2 | 105 | 6 | 29% | 0.40 | 0 | 22% | 10 | 50% |


## Q6 Lost time

### Share of champion-rounds by state (all rounds incl. dead), us vs opp

| split | team | champ-rounds | walk | camp | fight | tribute | recall | shop | idle | cast_other | dead |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | us | 369988 | 47.1% | 18.9% | 2.2% | 4.2% | 5.3% | 0.7% | 8.0% | 0.2% | 13.5% |
| all | opp | 373651 | 47.3% | 18.4% | 2.2% | 4.8% | 7.4% | 0.7% | 9.6% | 0.3% | 9.4% |
| map collision | us | 57316 | 40.9% | 13.4% | 3.1% | 3.5% | 5.3% | 0.7% | 9.2% | 0.4% | 23.7% |
| map collision | opp | 54323 | 45.4% | 15.2% | 2.8% | 4.0% | 5.7% | 0.8% | 8.7% | 0.5% | 17.0% |
| map corners | us | 53135 | 46.6% | 7.9% | 5.2% | 2.8% | 4.3% | 0.3% | 7.6% | 0.2% | 25.0% |
| map corners | opp | 60625 | 50.4% | 8.8% | 4.3% | 3.4% | 9.8% | 0.5% | 8.9% | 0.3% | 13.7% |
| map elkring | us | 28280 | 48.4% | 19.8% | 2.0% | 3.4% | 7.8% | 1.0% | 6.5% | 0.2% | 10.9% |
| map elkring | opp | 32457 | 43.5% | 19.2% | 1.6% | 3.1% | 4.4% | 0.6% | 9.4% | 0.5% | 17.6% |
| map expanse | us | 24960 | 49.7% | 30.7% | 0.0% | 7.3% | 5.0% | 0.8% | 6.5% | 0.0% | 0.0% |
| map expanse | opp | 24960 | 43.0% | 29.0% | 0.1% | 7.2% | 8.3% | 0.5% | 11.6% | 0.0% | 0.2% |
| map interlock | us | 47520 | 48.5% | 18.4% | 2.6% | 4.8% | 5.8% | 0.8% | 7.5% | 0.2% | 11.5% |
| map interlock | opp | 45462 | 46.6% | 16.7% | 2.6% | 5.8% | 4.4% | 0.5% | 9.6% | 0.2% | 13.5% |
| map lanes | us | 38622 | 51.8% | 18.7% | 1.0% | 3.9% | 2.6% | 0.3% | 12.6% | 0.2% | 8.9% |
| map lanes | opp | 38136 | 54.5% | 19.9% | 2.1% | 5.5% | 2.2% | 0.3% | 13.4% | 0.2% | 1.9% |
| map monolith | us | 43146 | 55.1% | 21.5% | 0.8% | 4.1% | 6.2% | 1.0% | 5.8% | 0.1% | 5.4% |
| map monolith | opp | 42188 | 47.1% | 21.7% | 1.0% | 4.6% | 10.9% | 0.9% | 8.8% | 0.2% | 4.9% |
| map packs | us | 43584 | 36.5% | 22.5% | 2.3% | 4.3% | 6.1% | 0.7% | 7.8% | 0.2% | 19.6% |
| map packs | opp | 42075 | 44.6% | 20.7% | 2.3% | 5.7% | 10.2% | 1.0% | 8.1% | 0.2% | 7.2% |
| map rows | us | 33425 | 51.7% | 29.2% | 0.0% | 5.3% | 4.9% | 0.9% | 7.7% | 0.0% | 0.3% |
| map rows | opp | 33425 | 48.5% | 25.8% | 0.0% | 5.7% | 10.0% | 0.8% | 9.2% | 0.1% | 0.0% |
| win | us | 142104 | 49.7% | 19.9% | 2.6% | 5.3% | 5.8% | 0.8% | 8.4% | 0.2% | 7.2% |
| win | opp | 145014 | 45.8% | 16.6% | 1.9% | 3.7% | 7.4% | 0.5% | 8.9% | 0.3% | 14.9% |
| loss | us | 227884 | 45.4% | 18.3% | 1.9% | 3.5% | 4.9% | 0.6% | 7.8% | 0.1% | 17.4% |
| loss | opp | 228637 | 48.3% | 19.5% | 2.3% | 5.5% | 7.4% | 0.7% | 10.0% | 0.2% | 6.0% |
| opp top10 | us | 110821 | 46.4% | 19.2% | 1.9% | 3.9% | 5.2% | 0.7% | 7.9% | 0.1% | 14.6% |
| opp top10 | opp | 109657 | 44.9% | 19.4% | 2.0% | 5.4% | 13.6% | 0.7% | 8.5% | 0.2% | 5.3% |
| opp 11-20 | us | 124462 | 46.7% | 18.4% | 1.9% | 4.0% | 5.1% | 0.7% | 8.2% | 0.2% | 14.8% |
| opp 11-20 | opp | 124771 | 48.7% | 18.4% | 2.2% | 4.9% | 4.5% | 0.7% | 10.6% | 0.3% | 9.7% |
| opp 21-30 | us | 124490 | 47.8% | 18.7% | 2.7% | 4.5% | 5.6% | 0.8% | 7.8% | 0.2% | 11.9% |
| opp 21-30 | opp | 129008 | 47.5% | 17.3% | 2.3% | 4.3% | 5.1% | 0.6% | 9.5% | 0.3% | 13.1% |
| opp other | us | 10215 | 50.0% | 24.3% | 1.9% | 5.9% | 4.6% | 0.6% | 9.4% | 0.1% | 3.1% |
| opp other | opp | 10215 | 54.0% | 21.5% | 1.3% | 4.6% | 5.8% | 0.6% | 8.8% | 0.1% | 3.3% |

### Walking efficiency (moves between purpose points vs shortest path; Mite 0.75, 4.0 extra/leg; study25 0.80)

| split | team | legs | moves | shortest path | efficiency | extra moves/leg |
|---|---|---|---|---|---|---|
| all | us | 6732 | 111250 | 99555 | 0.89 | 1.7 |
| all | opp | 7296 | 115171 | 94869 | 0.82 | 2.8 |
| map collision | us | 1000 | 12885 | 11263 | 0.87 | 1.6 |
| map collision | opp | 954 | 13173 | 11153 | 0.85 | 2.1 |
| map corners | us | 517 | 9797 | 7090 | 0.72 | 5.2 |
| map corners | opp | 701 | 11919 | 8990 | 0.75 | 4.2 |
| map elkring | us | 436 | 8185 | 7174 | 0.88 | 2.3 |
| map elkring | opp | 452 | 7807 | 5981 | 0.77 | 4.0 |
| map expanse | us | 801 | 10970 | 11096 | 1.01 | -0.2 |
| map expanse | opp | 799 | 10970 | 9903 | 0.90 | 1.3 |
| map interlock | us | 932 | 16955 | 14688 | 0.87 | 2.4 |
| map interlock | opp | 769 | 12634 | 10044 | 0.79 | 3.4 |
| map lanes | us | 970 | 14519 | 14038 | 0.97 | 0.5 |
| map lanes | opp | 1252 | 17385 | 15414 | 0.89 | 1.6 |
| map monolith | us | 794 | 17725 | 16211 | 0.91 | 1.9 |
| map monolith | opp | 856 | 16175 | 13644 | 0.84 | 3.0 |
| map packs | us | 749 | 7761 | 7550 | 0.97 | 0.3 |
| map packs | opp | 976 | 12305 | 9647 | 0.78 | 2.7 |
| map rows | us | 533 | 12453 | 10445 | 0.84 | 3.8 |
| map rows | opp | 537 | 12803 | 10093 | 0.79 | 5.0 |
| win | us | 3114 | 50542 | 44087 | 0.87 | 2.1 |
| win | opp | 2284 | 37836 | 30478 | 0.81 | 3.2 |
| loss | us | 3618 | 60708 | 55468 | 0.91 | 1.4 |
| loss | opp | 5012 | 77335 | 64391 | 0.83 | 2.6 |
| opp top10 | us | 1936 | 31648 | 28482 | 0.90 | 1.6 |
| opp top10 | opp | 2388 | 37771 | 30178 | 0.80 | 3.2 |
| opp 11-20 | us | 2241 | 37138 | 33409 | 0.90 | 1.7 |
| opp 11-20 | opp | 2520 | 39376 | 32750 | 0.83 | 2.6 |
| opp 21-30 | us | 2303 | 38496 | 34403 | 0.89 | 1.8 |
| opp 21-30 | opp | 2180 | 34567 | 28938 | 0.84 | 2.6 |
| opp other | us | 252 | 3968 | 3261 | 0.82 | 2.8 |
| opp other | opp | 208 | 3457 | 3003 | 0.87 | 2.2 |

### Deaths and respawn cost per map (death = 60 rounds dead)

| split | team | n | deaths | deaths/game | rounds dead | % of champ-rounds | gems not farmed while dead (dead rounds x gems/alive round) | gems dropped at death | per game |
|---|---|---|---|---|---|---|---|---|---|
| all | us | 155 | 899 | 5.8 | 49808 | 13.5% | 20478 | 10056 | 65 |
| all | opp | 155 | 626 | 4.0 | 35273 | 9.4% | 15309 | 10726 | 69 |
| map collision | us | 19 | 240 | 12.6 | 13568 | 23.7% | 4150 | 3306 | 174 |
| map collision | opp | 19 | 167 | 8.8 | 9262 | 17.0% | 3263 | 3938 | 207 |
| map corners | us | 19 | 235 | 12.4 | 13285 | 25.0% | 3845 | 1534 | 81 |
| map corners | opp | 19 | 145 | 7.6 | 8287 | 13.7% | 2308 | 1382 | 73 |
| map elkring | us | 9 | 55 | 6.1 | 3077 | 10.9% | 1011 | 1080 | 120 |
| map elkring | opp | 9 | 100 | 11.1 | 5717 | 17.6% | 1909 | 1404 | 156 |
| map expanse | us | 17 | 0 | 0.0 | 0 | 0.0% | 0 | 0 | 0 |
| map expanse | opp | 17 | 1 | 0.1 | 61 | 0.2% | 42 | 0 | 0 |
| map interlock | us | 19 | 101 | 5.3 | 5464 | 11.5% | 2257 | 2648 | 139 |
| map interlock | opp | 19 | 109 | 5.7 | 6123 | 13.5% | 2566 | 2842 | 150 |
| map lanes | us | 17 | 64 | 3.8 | 3454 | 8.9% | 1289 | 380 | 22 |
| map lanes | opp | 17 | 13 | 0.8 | 736 | 1.9% | 341 | 256 | 15 |
| map monolith | us | 16 | 45 | 2.8 | 2332 | 5.4% | 896 | 462 | 29 |
| map monolith | opp | 16 | 38 | 2.4 | 2055 | 4.9% | 832 | 440 | 28 |
| map packs | us | 22 | 157 | 7.1 | 8543 | 19.6% | 4183 | 580 | 26 |
| map packs | opp | 22 | 53 | 2.4 | 3032 | 7.2% | 1683 | 464 | 21 |
| map rows | us | 17 | 2 | 0.1 | 85 | 0.3% | 47 | 66 | 4 |
| map rows | opp | 17 | 0 | 0.0 | 0 | 0.0% | 0 | 0 | 0 |
| win | us | 58 | 182 | 3.1 | 10172 | 7.2% | 4462 | 2526 | 44 |
| win | opp | 58 | 387 | 6.7 | 21580 | 14.9% | 8346 | 7016 | 121 |
| loss | us | 97 | 717 | 7.4 | 39636 | 17.4% | 15532 | 7530 | 78 |
| loss | opp | 97 | 239 | 2.5 | 13693 | 6.0% | 6315 | 3710 | 38 |
| opp top10 | us | 50 | 295 | 5.9 | 16234 | 14.6% | 6639 | 2468 | 49 |
| opp top10 | opp | 50 | 105 | 2.1 | 5864 | 5.3% | 2750 | 1852 | 37 |
| opp 11-20 | us | 50 | 329 | 6.6 | 18442 | 14.8% | 7400 | 3860 | 77 |
| opp 11-20 | opp | 50 | 216 | 4.3 | 12113 | 9.7% | 5255 | 3740 | 75 |
| opp 21-30 | us | 50 | 269 | 5.4 | 14818 | 11.9% | 6085 | 3684 | 74 |
| opp 21-30 | opp | 50 | 298 | 6.0 | 16957 | 13.1% | 6820 | 5010 | 100 |
| opp other | us | 5 | 6 | 1.2 | 314 | 3.1% | 171 | 44 | 9 |
| opp other | opp | 5 | 7 | 1.4 | 339 | 3.3% | 146 | 124 | 25 |

### Idle rounds: by type (share of alive rounds with no action), us

| team | type | alive rounds | walk | camp | fight | tribute | recall | shop | idle | cast_other |
|---|---|---|---|---|---|---|---|---|---|---|
| us | Cassi | 51479 | 54.2% | 25.6% | 1.8% | 3.5% | 4.1% | 0.4% | 10.1% | 0.3% |
| us | Issac | 51514 | 49.7% | 24.7% | 1.2% | 6.3% | 7.0% | 1.0% | 10.0% | 0.1% |
| us | Ren | 44984 | 50.9% | 19.6% | 4.3% | 6.2% | 8.9% | 1.1% | 8.6% | 0.3% |
| us | Stellar | 40719 | 55.3% | 18.3% | 4.6% | 4.2% | 5.3% | 0.8% | 11.3% | 0.2% |
| us | Tavi | 34100 | 57.8% | 20.6% | 2.6% | 3.3% | 4.6% | 0.7% | 10.3% | 0.1% |
| us | Ryth | 32993 | 59.1% | 18.4% | 2.6% | 4.4% | 6.0% | 0.8% | 8.5% | 0.1% |
| us | Vendetta | 25947 | 54.8% | 22.0% | 0.4% | 7.2% | 7.4% | 1.1% | 7.0% | 0.1% |
| us | Varg | 26067 | 56.8% | 26.3% | 0.6% | 4.5% | 5.2% | 0.8% | 5.7% | 0.2% |
| us | Prism | 12377 | 57.4% | 17.4% | 5.7% | 2.6% | 6.0% | 0.4% | 10.1% | 0.4% |
| opp | Cassi | 57172 | 53.1% | 24.0% | 1.5% | 3.3% | 7.1% | 0.4% | 10.2% | 0.4% |
| opp | Issac | 57186 | 48.6% | 22.4% | 1.4% | 5.9% | 9.3% | 0.8% | 11.4% | 0.2% |
| opp | Stellar | 54018 | 53.4% | 18.5% | 3.2% | 5.0% | 8.5% | 0.7% | 10.7% | 0.2% |
| opp | Ren | 41072 | 49.4% | 18.8% | 3.8% | 6.0% | 9.1% | 0.9% | 11.8% | 0.4% |
| opp | Varg | 39293 | 56.2% | 18.5% | 1.5% | 7.1% | 6.1% | 1.0% | 9.2% | 0.3% |
| opp | Tavi | 27470 | 57.3% | 18.6% | 3.2% | 4.1% | 4.1% | 1.0% | 11.5% | 0.2% |
| opp | Ryth | 25054 | 52.3% | 16.4% | 2.7% | 5.6% | 12.9% | 0.7% | 9.2% | 0.2% |
| opp | Vendetta | 20163 | 48.5% | 23.0% | 1.9% | 8.1% | 7.5% | 1.1% | 9.7% | 0.2% |
| opp | Prism | 8462 | 49.1% | 18.3% | 4.5% | 4.3% | 14.6% | 0.6% | 8.4% | 0.2% |
| opp | Willow | 5863 | 55.9% | 22.1% | 1.7% | 2.9% | 4.4% | 0.3% | 12.5% | 0.4% |
| opp | Marcella | 1784 | 54.0% | 20.3% | 4.7% | 4.7% | 4.2% | 0.7% | 11.3% | 0.1% |
| opp | VesperVale | 841 | 57.3% | 15.9% | 4.8% | 6.8% | 4.3% | 0.7% | 8.4% | 1.8% |


## Q7 follow-ups

   sample unexplained: 23fc6b7e corners opp Tavi r0=711 gems=36 pos=[36, 33] gems_end? next events: [(711, 12, 10)]
   sample unexplained: 8cbb4b72 packs us Ren r0=506 gems=44 pos=[3, 5] gems_end? next events: [(506, 4, 10), (506, 12, 10)]
   sample unexplained: 298b3a16 interlock us Cassi r0=502 gems=138 pos=[20, 16] gems_end? next events: [(502, 4, 10), (502, 12, 10), (503, 2, 7)]
   sample unexplained: 298b3a16 interlock us Ren r0=497 gems=66 pos=[20, 15] gems_end? next events: [(497, 12, 10), (498, 12, 10)]
   sample unexplained: 81ff614b lanes opp Varg r0=172 gems=72 pos=[30, 3] gems_end? next events: [(172, 12, 10), (175, 6, 10), (175, 12, 10)]
   sample unexplained: 81ff614b lanes opp Issac r0=113 gems=72 pos=[30, 12] gems_end? next events: [(113, 12, 10), (115, 12, 10)]
### Recall classification (arrived recalls), us vs opp

- us: heal(hp<50%) 1701 (47%), teleport(carries gems, tributes after) 1061 (29%), shop small (<90 gold) 735 (20%), other (no buy, no gems, hp>=50%) 150 (4%); gold at arrival med 0 (share >=90: 0%, >=150: 0%); hp at start med 0.53
- opp: heal(hp<50%) 1881 (56%), shop small (<90 gold) 757 (22%), teleport(carries gems, tributes after) 582 (17%), other (no buy, no gems, hp>=50%) 141 (4%), shop(hp>=50%, buys) 4 (0%); gold at arrival med 0 (share >=90: 0%, >=150: 0%); hp at start med 0.46

### Rounds lost on recalls after a capture where walking to the altar was shorter than 5 + spawn->altar

- us: 1429 such recalls, 14216 champion-rounds lost in total = 92 per game (9.9 per recall)
- opp: 686 such recalls, 6031 champion-rounds lost in total = 39 per game (8.8 per recall)

### Why tribute starts do not complete

- us: {'died': 39, 'hit during channel': 116, 'no hit, no move (?)': 61, 'moved away': 9}
- opp: {'hit during channel': 220, 'no hit, no move (?)': 59, 'died': 45, 'moved away': 17}

### Rows: largest detour legs for us (extra moves, match, type, moves, shortest): [(138, '0413ec21', 'Cassi', 152, 14), (87, '2bc7a917', 'Ryth', 111, 24), (60, '2bc7a917', 'Varg', 100, 40), (54, 'ff9f5886', 'Varg', 94, 40), (54, 'ddcf57ff', 'Varg', 94, 40), (54, 'c3a7077e', 'Varg', 94, 40), (54, 'c21d3221', 'Varg', 94, 40), (54, 'a1b65574', 'Varg', 94, 40), (54, '88b53bab', 'Varg', 94, 40), (54, '8637d0d0', 'Varg', 94, 40), (54, '8401ebce', 'Varg', 94, 40), (54, '78e0bf2c', 'Varg', 94, 40)]
legs with >=12 extra moves: 105

## Q8 Recall classes (corrected gold at arrival = snapshot gold + purchases that round)

- us: shop (>=90 gold, buys) 1708 (47%), heal (hp<50% at start) 1701 (47%), no reason visible 155 (4%), teleport (gems, tribute after) 47 (1%), shop small (<90 gold) 36 (1%); gold at arrival med 90, >=90: 60%, >=150: 36%
- opp: heal (hp<50% at start) 1881 (56%), shop (>=90 gold, buys) 1286 (38%), no reason visible 142 (4%), teleport (gems, tribute after) 35 (1%), shop small (<90 gold) 21 (1%); gold at arrival med 90, >=90: 56%, >=150: 38%

### Per map recall classes (us / opp counts)

| map | heal (hp<50% at start) | shop (>=90 gold, buys) | teleport (gems, tribute after) | shop small (<90 gold) | no reason visible |
|---|---|---|---|---|---|
| collision | 314 / 373 | 230 / 148 | 0 / 1 | 3 / 6 | 9 / 28 |
| corners | 282 / 551 | 43 / 62 | 5 / 2 | 12 / 5 | 36 / 29 |
| elkring | 209 / 154 | 195 / 106 | 3 / 0 | 2 / 1 | 12 / 13 |
| expanse | 101 / 46 | 134 / 89 | 15 / 0 | 0 / 0 | 0 / 0 |
| interlock | 163 / 225 | 277 / 91 | 10 / 0 | 9 / 2 | 52 / 29 |
| lanes | 138 / 114 | 53 / 36 | 0 / 3 | 0 / 0 | 3 / 0 |
| monolith | 194 / 133 | 316 / 266 | 0 / 1 | 5 / 1 | 11 / 9 |
| packs | 188 / 199 | 247 / 257 | 14 / 28 | 5 / 6 | 29 / 27 |
| rows | 112 / 86 | 213 / 231 | 0 / 0 | 0 / 0 | 3 / 7 |

### Rounds lost on recalls after a capture where walking was shorter, by recall class (champion-rounds, total over 150 games; per game)

| team | recall class | recalls | rounds lost | per game |
|---|---|---|---|---|
| us | heal (hp<50% at start) | 184 | 1969 | 12.7 |
| us | shop (>=90 gold, buys) | 1170 | 11319 | 73.0 |
| us | teleport (gems, tribute after) | 27 | 239 | 1.5 |
| us | shop small (<90 gold) | 7 | 120 | 0.8 |
| us | no reason visible | 36 | 496 | 3.2 |
| opp | heal (hp<50% at start) | 133 | 1356 | 8.7 |
| opp | shop (>=90 gold, buys) | 536 | 4487 | 28.9 |
| opp | teleport (gems, tribute after) | 5 | 26 | 0.2 |
| opp | shop small (<90 gold) | 0 | 0 | 0.0 |
| opp | no reason visible | 1 | 21 | 0.1 |


## Q9 Capture credit, shop trips, rows per type

### Attackers that helped kill a group but were not on the capture tiles (no gems/gold), per type; and credited captures per champion-game

| team | type | champion-games | credited captures/g | group kills helped | ..not credited | % not credited | gold earned/g |
|---|---|---|---|---|---|---|---|
| us | Cassi | 127 | 3.7 | 1107 | 647 | 58% | 224 |
| us | Issac | 127 | 6.5 | 1100 | 291 | 26% | 669 |
| us | Ren | 88 | 6.8 | 805 | 238 | 30% | 806 |
| us | Stellar | 88 | 4.4 | 904 | 534 | 59% | 507 |
| us | Tavi | 80 | 3.6 | 684 | 415 | 61% | 291 |
| us | Ryth | 78 | 4.5 | 503 | 175 | 35% | 655 |
| us | Vendetta | 67 | 6.3 | 514 | 96 | 19% | 821 |
| us | Varg | 67 | 4.1 | 519 | 246 | 47% | 568 |
| us | Prism | 28 | 2.6 | 228 | 161 | 71% | 227 |
| opp | Cassi | 133 | 3.7 | 1465 | 1009 | 69% | 308 |
| opp | Issac | 133 | 6.2 | 1255 | 488 | 39% | 630 |
| opp | Stellar | 114 | 4.8 | 1433 | 928 | 65% | 537 |
| opp | Varg | 89 | 6.2 | 719 | 195 | 27% | 890 |
| opp | Ren | 88 | 6.8 | 940 | 387 | 41% | 685 |
| opp | Tavi | 60 | 4.6 | 633 | 383 | 61% | 426 |
| opp | Ryth | 55 | 6.0 | 560 | 248 | 44% | 618 |
| opp | Vendetta | 48 | 7.5 | 451 | 103 | 23% | 868 |
| opp | Prism | 16 | 4.9 | 235 | 166 | 71% | 402 |
| opp | Willow | 14 | 2.9 | 129 | 102 | 79% | 262 |
| opp | Marcella | 4 | 6.0 | 34 | 10 | 29% | 790 |
| opp | VesperVale | 2 | 6.0 | 14 | 3 | 21% | 1018 |

### Cassi per map: credited captures/g, gold earned/g, buys/g (us vs opp)

| map | n | us Cassi captures/g | gold/g | buys/g | opp Cassi captures/g | gold/g | buys/g |
|---|---|---|---|---|---|---|---|
| collision | 19 | 4.3 | 423 | 13.7 | 5.6 | 593 | 10.0 |
| corners | 19 | - | - | - | 1.8 | 97 | 2.2 |
| elkring | 9 | - | - | - | 3.0 | 551 | 7.6 |
| expanse | 17 | 5.5 | 85 | 2.8 | 4.6 | 68 | 0.9 |
| interlock | 19 | 4.7 | 292 | 9.7 | 2.5 | 141 | 2.3 |
| lanes | 17 | 5.4 | 14 | 0.5 | 6.4 | 127 | 1.6 |
| monolith | 16 | 3.3 | 341 | 11.3 | 3.6 | 395 | 6.1 |
| packs | 22 | 3.0 | 338 | 11.0 | 3.4 | 437 | 7.7 |
| rows | 17 | 0.1 | 16 | 0.5 | 1.8 | 458 | 8.0 |

### Shopping trips (recall at hp>=50% followed by a purchase within 3 rounds of arrival): count per game and rounds from recall start to the next capture or tribute

| split | team | shop trips | per game | rounds to next capture/tribute med | mean | champion-rounds per game |
|---|---|---|---|---|---|---|
| all | us | 1767 | 11.4 | 29 | 38.7 | 403 |
| all | opp | 1330 | 8.6 | 30 | 40.6 | 324 |
| map collision | us | 233 | 12.3 | 32 | 51.2 | 585 |
| map collision | opp | 154 | 8.1 | 36 | 55.7 | 410 |
| map corners | us | 57 | 3.0 | 48 | 60.0 | 167 |
| map corners | opp | 67 | 3.5 | 56 | 74.3 | 215 |
| map elkring | us | 199 | 22.1 | 34 | 52.7 | 1078 |
| map elkring | opp | 107 | 11.9 | 39 | 59.9 | 652 |
| map expanse | us | 134 | 7.9 | 17 | 17.8 | 133 |
| map expanse | opp | 89 | 5.2 | 29 | 35.4 | 173 |
| map interlock | us | 291 | 15.3 | 33 | 44.4 | 621 |
| map interlock | opp | 93 | 4.9 | 36 | 43.1 | 200 |
| map lanes | us | 53 | 3.1 | 19 | 35.9 | 97 |
| map lanes | opp | 36 | 2.1 | 19 | 22.7 | 47 |
| map monolith | us | 321 | 20.1 | 35 | 41.4 | 756 |
| map monolith | opp | 267 | 16.7 | 36 | 45.0 | 701 |
| map packs | us | 266 | 12.1 | 13 | 22.1 | 250 |
| map packs | opp | 286 | 13.0 | 15 | 24.8 | 307 |
| map rows | us | 213 | 12.5 | 24 | 28.7 | 299 |
| map rows | opp | 231 | 13.6 | 25 | 32.3 | 410 |
| win | us | 795 | 13.7 | 29 | 37.4 | 482 |
| win | opp | 425 | 7.3 | 34 | 47.5 | 318 |
| loss | us | 972 | 10.0 | 29 | 39.9 | 355 |
| loss | opp | 905 | 9.3 | 27 | 37.5 | 328 |
| opp top10 | us | 505 | 10.1 | 29 | 37.1 | 341 |
| opp top10 | opp | 435 | 8.7 | 28 | 39.3 | 319 |
| opp 11-20 | us | 573 | 11.5 | 32 | 43.6 | 449 |
| opp 11-20 | opp | 399 | 8.0 | 31 | 43.3 | 326 |
| opp 21-30 | us | 639 | 12.8 | 29 | 36.6 | 432 |
| opp 21-30 | opp | 460 | 9.2 | 31 | 39.8 | 334 |
| opp other | us | 50 | 10.0 | 20 | 27.7 | 260 |
| opp other | opp | 36 | 7.2 | 25 | 36.6 | 256 |

### Gold at the start of a shopping trip is not observable (recall starts before the capture pays); gold spent on the trip instead

| team | shop trips | gold spent med | <90 | 90-149 | 150-239 | 240-329 | >=330 |
|---|---|---|---|---|---|---|---|
| us | 1767 | 180 | 3% | 35% | 46% | 16% | 0% |
| opp | 1330 | 180 | 5% | 22% | 47% | 23% | 3% |

### Rows: per champion type, states and credited captures (us vs opp)

| team | type | n | captures/g | gems/g | tributes/g | recalls/g | walk | camp | tribute | recall | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|
| us | Vendetta | 17 | 5.9 | 386 | 5.6 | 6.8 | 52% | 23% | 10% | 9% | 4% |
| us | Varg | 17 | 2.0 | 103 | 0.9 | 2.9 | 52% | 37% | 2% | 4% | 4% |
| us | Cassi | 17 | 0.1 | 4 | 0.1 | 0.1 | 54% | 37% | 0% | 0% | 9% |
| us | Issac | 17 | 5.0 | 299 | 4.0 | 5.2 | 47% | 27% | 8% | 7% | 10% |
| us | Ryth | 17 | 4.4 | 291 | 3.8 | 4.4 | 54% | 21% | 7% | 6% | 10% |
| opp | Cassi | 17 | 1.8 | 112 | 1.6 | 2.3 | 52% | 27% | 3% | 8% | 9% |
| opp | Issac | 17 | 4.1 | 259 | 3.2 | 5.4 | 45% | 27% | 6% | 12% | 9% |
| opp | Varg | 14 | 5.2 | 332 | 4.5 | 4.6 | 53% | 20% | 8% | 6% | 12% |
| opp | Stellar | 11 | 1.7 | 114 | 1.5 | 2.5 | 46% | 30% | 3% | 12% | 9% |
| opp | Vendetta | 8 | 5.4 | 355 | 4.8 | 5.5 | 50% | 23% | 10% | 7% | 9% |
| opp | Ryth | 5 | 4.6 | 304 | 4.2 | 5.0 | 44% | 20% | 8% | 23% | 4% |
| opp | Ren | 5 | 3.2 | 211 | 2.8 | 4.4 | 42% | 26% | 5% | 22% | 4% |
| opp | Willow | 4 | 1.5 | 99 | 1.2 | 1.2 | 48% | 34% | 3% | 2% | 13% |
| opp | Tavi | 3 | 2.0 | 132 | 2.0 | 0.7 | 50% | 33% | 4% | 1% | 12% |
| opp | Prism | 1 | 3.0 | 198 | 2.0 | 3.0 | 52% | 32% | 5% | 4% | 7% |

### Rows: team captures by round bins (per game), us vs opp; and gems in hand at game end

| team | r0-49 | r50-99 | r100-149 | r150-199 | r200-249 | r250-299 | r300-349 | r350-399 | r400+ | gems in hand at end |
|---|---|---|---|---|---|---|---|---|---|---|
| us | 1.00 | 1.94 | 2.06 | 2.00 | 2.82 | 2.00 | 3.00 | 2.41 | 0.12 | 118 |
| opp | 1.06 | 2.12 | 2.00 | 2.47 | 2.06 | 2.53 | 2.35 | 2.29 | 0.12 | 62 |


## Q10 Camp utilization: for the own-side gem groups each team farms (>=50% of games), share of rounds the group is respawning / up and untouched / under attack

| map | us farmed own groups | respawning | up & untouched | under attack | opp farmed own groups | respawning | up & untouched | under attack |
|---|---|---|---|---|---|---|---|---|
| collision | 3 | 46% | 44% | 10% | 4 | 38% | 54% | 9% |
| corners | 1 | 18% | 76% | 6% | 3 | 16% | 78% | 5% |
| elkring | 5 | 59% | 27% | 13% | 5 | 54% | 35% | 11% |
| expanse | 9 | 37% | 50% | 12% | 6 | 55% | 30% | 15% |
| interlock | 4 | 68% | 16% | 16% | 4 | 54% | 33% | 14% |
| lanes | 9 | 55% | 36% | 9% | 6 | 64% | 29% | 8% |
| monolith | 7 | 41% | 45% | 14% | 7 | 49% | 37% | 15% |
| packs | 2 | 50% | 34% | 16% | 2 | 53% | 31% | 17% |
| rows | 3 | 60% | 21% | 19% | 3 | 62% | 17% | 21% |


