# t10plan-v13 "the rivals' shop" (2026-10-28 ~22:30 UTC): v4o2 + the top-20 rivals' observed purchase order per champion type

Base: **v4o2** (`zips/e1foco-t10plan-v4o2.zip`, roles only on near maps, 80/140 vs kvvl in its session; 72 in the v9-v12 sessions), NOT the
v9-v12 block code. Zip `zips/e1foco-t10plan-v13.zip` (sha256 in `zips/SHA256SUMS`), diff `src/t10plan-v13_vs_v4o2.diff` (259 lines:
main.cpp shop(), champions.h, vesper.h, marcella.h, vendetta.h, ryth.h, heart_of_ruin.h, params.h). Everything under `P_V13` (params.h).
Nothing new before r30 (`P_V13_R`): init builds the v4o2 plans byte for byte; the first shop() call at r>=30 swaps the plan
(`champ::v13_plan`). No init printf. One stdout line per purchase: `[v13-shop] r= ch= item=<family>-<stat> gold=<after>`.

## 1. Measurement: what the top-20 rivals carry and do, round by round (an/shop13dec.py + an/shop13.py + an/shop13plan.py)

Data: `pcassets/replays_c37/{kvvl,t10plan4o2}` (branch claude/pc-e1-assets), 160 online games vs 16 rivals of ranks 5-20 (print dont int,
Claudus Maximus, hello, Trzy Kwaterki, prism best girl, Sponge, policy wonk, NEETCoders, Supaswag, procless, Univardisty, new team(4), SSSA,
:3, meow, German Empire), 80 with kvvl and 80 with v4o2 on our side (15 wins). Decoded to r600 with a new bounded decoder
(`an/shop13dec.py`, three passes of `pcassets/viewer/replaydump.js`): the engine 2.0.0 snapshot champion struct (624 bytes) **does carry the
item list per round** (u32[84] at byte 240, family x stat x shard/emblem), the strength total (f32 at 148), the focus total (f32 at 132)
and max hp (f32 at 32); purchases are the per-round differences (an emblem = its 5th shard). Camp damage per step comes from `--deltas`
(one entry per attack / ability step), so "hit" = one damaging step, "hitter-round" = a champion-round with at least one damaging step.
`us` = the bot of the batch (kvvl or v4o2, side from index.json), `rival` = the other side. Window r30-150 unless stated.

### 1a. Damage to camps per hit, hits per hitter-round, hitter-rounds per game (r30-150, v4o2 batch; the kvvl batch gives the same numbers +-2)

| champion | rival hits/game | **rival dmg/hit** | rival hits/hitter-round | rival hitter-rounds/game | us hits/game | **us dmg/hit** | us hits/hitter-round | us hitter-rounds/game |
|---|---|---|---|---|---|---|---|---|
| Vesper | 36.0 | **55.3** | 1.13 | 31.8 | 26.6 | **49.8** | 1.17 | 22.7 |
| Marcella | 24.1 | **59.3** | 1.27 | 19.0 | 22.1 | **54.6** | 1.24 | 17.9 |
| Vendetta | 30.3 | **68.6** | 1.25 | 24.2 | 26.0 | **67.9** | 1.28 | 20.2 |
| Ryth | 29.6 | **56.6** | 1.54 | 19.2 | 24.3 | **55.4** | 1.36 | 17.8 |
| HoR | 33.2 | **55.0** | 1.23 | 27.1 | 17.5 | **64.4** | 1.30 | 13.5 |
| Ren (ours, far maps) | - | - | - | - | 22.2 | 43.6 | 1.09 | 20.4 |

Per team: mean hitters per round r30-150 rival 0.90 vs us 0.69 (109 vs 84 hitter-rounds a game, +30%); rounds with 0 hitters 51% vs 55%,
with 3+ hitters 12.0% vs 5.4%. Hitters on the same camp (rounds with a hitter): 1 / 2 / 3 / 4+ = rival 65.5 / 21.9 / 9.2 / 3.4%, us
81.3 / 13.7 / 3.8 / 1.3% (mean 1.51 vs 1.25).

### 1b. Gold-group captures (gold >= 20, capture inside r30-150)

| | rival | us (v4o2) |
|---|---|---|
| captures / game | 4.39 | 4.20 |
| hitter-rounds / capture | **22.1** | **16.5** |
| bodies that hit / capture | 1.97 | 1.45 |
| hitting phase first hit -> group dead, mean / median | 14.7 / 13 | 14.2 / 5 |
| first hit -> capture | 21.9 | 21.6 |
| group hp / gold | 1631 / 75 | 1157 / 64 |

The rival does not clear a gold group with fewer hitter-rounds: it spends more (22 vs 16.5), because it takes bigger groups (1631 hp vs
1157) with two bodies instead of 1.5, and the hitting phase is the same (14.7 vs 14.2 rounds).

### 1c. Hp, max hp, strength, focus, gold by round (alive champions, mean; v4o2 batch)

| champion | r30 rival / us | r60 | r100 | r150 | r300 | r600 |
|---|---|---|---|---|---|---|
| Vesper hp/mhp/str/foc/gold | 892/1002/46/100/20 vs 882/1000/45/100/17 | 890/1018/50/100/45 vs 796/1000/49/100/45 | 879/1034/59/100/45 vs 791/1000/56/100/52 | 969/1126/70/101/51 vs 800/1027/64/100/47 | 1283/1453/99/105/50 vs 929/1131/79/103/21 | 2027/2444/201/139/96 vs 1101/1383/120/117/33 |
| Marcella | 1110/1203/45/61/17 vs 1007/1200/45/61/3 | 953/1229/45/66/37 vs 989/1200/45/65/10 | 1153/1284/46/76/34 vs 993/1202/45/71/16 | 1157/1365/48/84/55 vs 1061/1201/45/83/19 | 1486/1701/56/137/59 vs 1054/1225/47/119/34 | 2427/2758/89/285/82 vs 1440/1669/66/197/41 |
| Vendetta | 818/1000/70/100/4 vs 867/1000/70/100/4 | 788/1033/72/100/16 vs 854/1000/72/100/14 | 851/1066/75/100/20 vs 871/1007/74/100/27 | 885/1116/76/100/32 vs 874/1007/82/100/19 | 1115/1302/96/101/31 vs 900/1064/97/101/27 | 1725/1977/142/110/37 vs 1163/1461/146/114/50 |
| Ryth | 1086/1200/45/100/2 vs 1033/1200/45/100/2 | 1004/1220/45/100/8 vs 988/1222/45/100/11 | 1039/1244/45/100/17 vs 1114/1252/46/100/19 | 1094/1334/47/100/14 vs 1173/1303/47/100/13 | 1285/1560/52/100/34 vs 1246/1412/50/100/15 | 1938/2253/75/109/16 vs 1598/1837/67/104/14 |
| HoR | 906/1000/30/100/4 vs 828/1000/30/100/14 | 807/1017/30/101/13 vs 856/1030/30/100/45 | 865/1051/30/104/25 vs 1067/1162/30/102/14 | 922/1074/30/110/26 vs 953/1207/30/104/23 | 1111/1311/30/136/34 vs 1137/1419/30/114/37 | 1613/1866/33/185/57 vs 1530/1848/32/137/24 |

Up to r150 the stats are the same (strength within 2-6 points, max hp within 100). The rival pulls away from r300: Vesper 99 -> 201 strength
and 1453 -> 2444 max hp at r600 against our 79 -> 120 and 1131 -> 1383, Marcella 137 -> 285 focus against 119 -> 197. That is the number
of shards bought (next table), i.e. gold earned, not the order.

### 1d. Purchases by round (shards per champion-game; an emblem counts as its 5th shard), rival vs us (v4o2 batch)

| champion | r30-60 | r60-100 | r100-150 | r150-300 | r300-600 | total <= r600 | mean gold before a purchase |
|---|---|---|---|---|---|---|---|
| Vesper rival | 1.1 (prospector-s .4, treasure-s .3, jungle-s .2) | 1.8 (treasure-s .8, jungle-s .4) | 2.9 (prospector-s .6, treasure-s .5) | 8.6 (durab-h 1.5, bruiser-s 1.2, bruiser-h 1.1, jungle-s 1.1) | 24.2 (bruiser-s 11.8, bruiser-h 4.2, durab-h 1.7, power-s 1.5) | **38.8** | 221 |
| Vesper us | 0.7 (durab-s .5) | 1.3 (durab-s 1.1) | 1.7 (durab-s 1.0, jungle-s .5) | 3.8 (jungle-s 1.3, bruiser-h 1.0) | 6.8 (bruiser-s 4.7, bruiser-h 1.0) | **14.4** | 176 |
| Marcella rival | 0.8 (treasure-f/h) | 1.5 (treasure-f .5, treasure-h .3) | 1.5 | 8.2 (bruiser-h 1.2, durab-h .8, treasure-f .7, bruiser-f .7, prospector-f .7) | 22.4 (bruiser-f 6.7, bruiser-h 6.0, bruiser-s 3.0) | **34.4** | 208 |
| Marcella us | 0.3 (treasure-f) | 0.4 | 0.8 | 3.4 (treasure-f 1.9, bruiser-f 1.0) | 9.6 (bruiser-h 3.0, bruiser-f 2.7, jungle-s 1.9) | **14.5** | 148 |
| Vendetta rival | 0.5 | 0.8 | 0.7 | 5.5 (jungle-s 1.4, prospector-h .8, treasure-s .7) | 13.2 (bruiser-s 3.0, bruiser-h 2.9, durab-h 1.8) | **20.8** | 138 |
| Vendetta us | 0.3 | 0.4 | 1.3 (treasure-s 1.0) | 2.8 (treasure-s 1.2, jungle-s .7) | 7.2 (bruiser-s 2.3, bruiser-h 2.0, jungle-s 1.6) | **11.9** | 137 |
| Ryth rival | 0.2 | 0.4 | 0.9 (prospector-h .4) | 2.9 (treasure-h .8, jungle-s .5, prospector-h .5) | 9.1 (bruiser-h 2.6, durab-h 1.4) | **13.5** | 119 |
| Ryth us | 0.2 | 0.4 | 0.4 | 1.7 (treasure-h 1.1) | 5.3 (jungle-s 1.4, bruiser-h 1.4, treasure-h 1.2) | **8.0** | 143 |
| HoR rival | 0.3 | 0.6 | 0.8 (treasure-f .4) | 4.6 (jungle-f 1.1, bruiser-h .8, prospector-h .6) | 9.2 (bruiser-h 2.3, durab-h 1.7, bruiser-f 1.4) | **15.5** | 124 |
| HoR us | 0.4 | 1.3 (treasure-h 1.1) | 0.6 | 2.7 (treasure-h 1.5, jungle-f .8) | 4.9 (bruiser-h 1.7, jungle-f 1.5) | **9.8** | 128 |

In r30-150 nobody buys much: the rival 0.4-5.8 shards per champion, we 1.0-3.7. The 2.4x gap in shards is r300-600, paid with gold we do not
have (gold in hand at r600: rival Vesper 96, Marcella 82 vs our 33, 41; gold before a purchase 221 vs 176).

### 1e. The rivals' order (both batches, 160 games; modal item of the k-th purchase event, median round, gold before p25/p50/p75)

| champion | #1 | #2 | #3 | #4 | #5 | #6 | #7-10 | r300-600 fill (shards/game) |
|---|---|---|---|---|---|---|---|---|
| Vesper (118) | treasure-s 40% / prospector-s 29% (r71, 79/133/199) | treasure-s 23% / jungle-s 22% (r132) | prospector-s 22% / jungle-s 20% (r168) | prospector-s 21% / jungle-s 18% / durab-h 17% (r190) | durab-h 27% (r244) | durab-h 26% (r285) | durab-h 30% then bruiser-s 34-39% (r325-390) | bruiser-s 11.2, bruiser-h 4.0, power-s 1.5 |
| Marcella (144) | treasure-f 22% / treasure-h 16% / prospector-h 11% (r83, 80/120/190) | treasure-f 23% (r169) | jungle-s 17% / durab-h 12% (r213) | durab-h 15% / bruiser-h 12% (r263) | bruiser-h 15% (r292) | bruiser-h 18% / bruiser-f 15% (r328) | bruiser-h/f/s (r350-450) | bruiser-f 6.6, bruiser-h 5.9, bruiser-s 3.0 |
| Ryth (88) | treasure-h 32% / prospector-h 29% / jungle-h 20% (r151, 40/100/110) | treasure-h 29% / prospector-h 29% (r226) | jungle-s 26% (r294) | bruiser-h 19% / jungle-s 19% (r364) | bruiser-h 27% (r404) | bruiser-h 40% (r466) | bruiser-h / durab-h | bruiser-h 2.3, durab-h 1.3, jungle-s 0.75 |
| Vendetta (132) | treasure-s 25% / prospector-h 24% / treasure-h 20% (r121, 40/80/100) | treasure-s 22% / jungle-s 20% (r205) | jungle-s 32% (r241) | jungle-s 28% (r295) | jungle-s 29% (r337) | durab-h 24% (r386) | bruiser-h / durab-h / bruiser-s | bruiser-s 2.5, bruiser-h 2.3, durab-h 1.8 |
| HoR (136) | treasure-f 27% / prospector-h 19% / jungle-f 15% (r158, 40/100/120) | jungle-f 21% (r234) | jungle-f 28% (r287) | bruiser-h 21% (r335) | jungle-f 27% / bruiser-h 24% / durab-h 23% (r348) | bruiser-h 25% / durab-h 25% (r390) | durab-h / bruiser-f | bruiser-h 2.5, durab-h 1.5, bruiser-f 1.2 |

The 16 rivals do not share a build (the modal item is 20-40% at every position). The v4o2 plans (t10shop-v1, built from top-10 games
10-22) already were treasure -> jungle -> bruiser-h -> durab-h -> bruiser fill for Marcella, Ryth, Vendetta, HoR; the differences are
Vesper (ours durab-s first, theirs treasure-s / prospector-s then durab-h), Marcella's second emblem (ours bruiser-f, theirs jungle-s /
durab-h), HoR's first (ours treasure-h, theirs treasure-f), Vendetta's durab-h before bruiser-h, the fill mixes, and the "prospector"
family (engine 2.0.0, no SDK description; the visualiser tracks prospectorGold / prospectorGems per champion), which no version of ours
buys and which is the rivals' first or second purchase in 20-30% of the champions.

**Conclusion of the measurement: damage per hit is NOT the gap.** Same damage per hit (within 10%, HoR ours higher), same hits per
hitter-round, same strength / max hp up to r150, same hitting phase per gold group (14-15 rounds) and more hitter-rounds per capture on
the rival's side. What the numbers point to: (1) the rival's champions spend 30% more champion-rounds hitting camps in r30-150 (109 vs
84 a game) and 12% vs 5% of the rounds with 3+ hitters; (2) they take bigger groups (1631 hp, 75 gold) with 2 bodies; (3) from r150 they
earn 2-2.5x the gold and convert it into 2.4x the shards, which is why their Vesper / Marcella are twice as strong at r600. The shop order
is a consequence of (1)-(3), not a cause.

## 2. v13: the rivals' order and thresholds in v4o2's shop (diff `src/t10plan-v13_vs_v4o2.diff`)

| champion | v4o2 plan (init, kept before r30) | **v13 plan from r30** (champ::v13_plan) | v13 fill from r300 (late_mix weights = rival shards r300-600) | gold floor (p25 of the rival's first purchase) |
|---|---|---|---|---|
| Vesper | durab-s, jungle-s, bruiser-h, bruiser-s* (legacy, hp_pick on) | treasure-s, prospector-s, durab-h, bruiser-s* (own plan, hp_pick off) | bruiser-s 11.2 / bruiser-h 4.0 / power-s 1.5 | 79 |
| Marcella | treasure-f, bruiser-f, jungle-s, bruiser-h x2, bruiser-f* | treasure-f, jungle-s, durab-h, bruiser-h, bruiser-f* | bruiser-f 6.6 / bruiser-h 5.9 / bruiser-s 3.0 | 80 |
| Vendetta | treasure-s, jungle-s, bruiser-h, bruiser-s* | treasure-s, jungle-s, durab-h, bruiser-h, bruiser-s* | bruiser-s 2.5 / bruiser-h 2.3 / durab-h 1.8 | 40 |
| Ryth | treasure-h, jungle-s, bruiser-h, durab-h, bruiser-s, bruiser-h* | treasure-h, jungle-s, bruiser-h, durab-h, bruiser-h* | bruiser-h 2.3 / durab-h 1.3 / jungle-s 0.75 | 40 |
| HoR | treasure-h, jungle-f, bruiser-h, durab-h, bruiser-h x2, bruiser-f* | treasure-f, jungle-f, bruiser-h, durab-h, bruiser-f* | bruiser-h 2.5 / durab-h 1.5 / bruiser-f 1.2 | 40 |
| Ren | unchanged (no rival Ren in the 160 games) | unchanged | unchanged | 30 |

`P_LSHOP_R` 400 -> 300 (the rivals' fill window). The floor: at r>=30 the champion buys only with gold >= floor (v4o2: 30). Nothing else
changes (the shop still buys only on spawn / dead, P_SHOP_RECALL 180 as before). The plan swap is the first shop() call at r>=30;
init and the opening are v4o2's: first divergence of our positions vs v4o2 (an/shop13div.py, 140 games): 1 game before r30
(gato_gemcombat5_a at r4, the same fuel-only divergence v7/v10 had), 31 at r30-79, 108 at r80+. Low-fuel / fuel-wait markers: 0.

## 3. Local check (70 maps x 2 sides vs kvvl, cambc 4.0.0; an/shop13.py on dec37/v4o2k and dec37/v13k, an/shop13lines.py)

| | v4o2 | **v13** |
|---|---|---|
| wins vs kvvl | 80/140 | **71/140** (not broken: gate < 40) |
| `[v13-shop]` lines a game (<= r600 / total) | - | 61 / 186 |
| dmg per hit r30-150: Vesper / Marcella / Vendetta / Ryth / HoR | 51.6 / 55.7 / 68.9 / 54.5 / 61.4 | 49.5 / 54.9 / 68.8 / 54.4 / 63.4 |
| hitter-rounds a game r30-150, same five | 24.9 / 20.7 / 22.9 / 22.8 / 17.5 | 25.4 / 20.4 / 23.7 / 23.3 / 16.6 |
| gold captures r30-150 a game / hitter-rounds per capture / bodies | 4.28 / 20.6 / 1.58 | 4.35 / 20.2 / 1.57 |
| hitting phase (first hit -> group dead) mean / median | 17.7 / 15 | 17.7 / 15 |
| hitters on the same camp, mean | 1.33 | 1.32 |
| shards bought <= r600: Vesper / Marcella / Vendetta / Ryth / HoR | 20.6 / 19.1 / 13.8 / 9.5 / 15.6 | 18.3 / 15.2 / 14.0 / 9.5 / 13.8 |
| Vesper r150 hp/mhp/str/gold -> r600 | 882/1048/68/42 -> 1286/1516/140/45 | 839/1006/60/108 -> 1342/1596/119/112 |
| Marcella r150 hp/mhp/str/foc/gold -> r600 | 998/1204/45/92/23 -> 1584/1829/71/211/47 | 979/1201/46/77/52 -> 1477/1768/68/154/117 |
| HoR r150 hp/mhp/foc -> r600 | 951/1208/102 -> 1803/2166/163 | 844/1007/119 -> 1387/1649/190 |
| first purchase round (median) Vesper / Marcella / Vendetta / Ryth / HoR | 93 / 160 / 160 / 184 / 120 (c37 batch) | 117 / 186 / 180 / 191 / 94 |

Mechanism: damage per hit, hitter-rounds, captures and the hitting phase do not move (they were already equal to the rivals' in the
online measurement). The gold floor keeps Vesper / Marcella sitting on 108 / 52 gold at r150 and 112 / 117 at r600 that v4o2 would
have spent (-2.3 / -3.9 shards by r600), HoR's treasure-f instead of treasure-h costs max hp (1649 vs 2166 at r600), and the
rivals' late mix buys fewer strength shards for Vesper (119 vs 140). kvvl (the local judge) punishes that: -9 games, within the
+-7 noise of this bench but with the wrong sign everywhere. v13b was not built: the build is not broken and the measurement says
the shop is not the lever.

## 4. What the numbers point to instead
The rival side in the 160 online games has the same damage per hit and the same stats up to r150; it hits camps 30% more
champion-rounds (109 vs 84 a game in r30-150), takes groups 40% bigger with two bodies, and from r150 converts 2-2.5x our gold
income into 2.4x the shards. The lever is champion-rounds on camps and group size in r30-150 (presence, not kit), which the block
line (v9-v12) tried to buy with synchronization and lost on cohesion; the shop follows the gold and cannot create it.

Tools: `an/shop13dec.py` (bounded 3-pass decoder with per-round items / strength / focus / max hp), `an/shop13.py DIR... [--index]`
(the tables above; without --index the side is the local _a/_b suffix), `an/shop13plan.py` (the rivals' purchase sequence and gold
percentiles per champion type), `an/shop13lines.py TAG` ([v13-shop] stdout lines), `an/shop13div.py TAGA TAGB` (first divergence).
